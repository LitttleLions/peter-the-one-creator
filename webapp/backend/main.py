"""FastAPI backend entrypoint for the dashboard migration."""

from __future__ import annotations

import asyncio
import base64
import json
import re
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse


REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = REPO_ROOT / "tools"
FRONTEND_DIST = REPO_ROOT / "webapp" / "frontend" / "dist"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from lib import dashboard_jobs  # noqa: E402
from lib.book_project import book_project  # noqa: E402
from lib.name_registry import write_names  # noqa: E402
from lib.output_paths import (  # noqa: E402
    book_output_root,
    de_scene_path,
    list_source_scene_paths,
    parse_scene_number,
    prompt_path,
    source_scene_path,
)
from lib.workbench_api import (  # noqa: E402
    ExportOptions,
    IllustrationBatchOptions,
    NewBookOptions,
    ReviewOptions,
    TranslateBatchOptions,
    TranslateRunOptions,
    build_assemble_chapter_command,
    build_export_command,
    build_extract_scenes_command,
    build_init_book_command,
    build_illustration_batch_command,
    build_review_command,
    build_review_fixes_command,
    build_translate_batch_command,
    build_translate_chapter_command,
    editable_name_rows,
    export_context,
    guess_title_author,
    latest_export_files,
    names_path,
    normalize_name_rows,
    style_options,
    unregistered_sources,
)
from lib.workbench_state import book_by_id, chapter_rows, load_books, load_models  # noqa: E402

from .json_utils import jsonable


class ActionPlanRequest(BaseModel):
    action: str
    book_id: str | None = None
    chapter: str | None = None
    style: str | None = None
    provider: str | None = None
    model: str | None = None
    ollama_model: str | None = None
    chunk_char_limit: int | None = None
    scene: str | None = None
    overwrite: bool = False
    dry_run: bool = False
    scope: str | None = None
    start_chapter: str | None = None
    end_chapter: str | None = None
    auto_status: bool = False
    assemble_after: bool = False
    llm: str = "none"
    llm_scope: str = "flagged"
    fail_on_errors: bool = False
    export_format: str | None = None
    allow_partial: bool = False
    kind: str | None = None
    backend: str | None = None
    moodboard: str | None = None
    aspect_ratio: str | None = None
    quality: str | None = None
    missing: bool = False
    no_reference: bool = False
    allow_paid_generation: bool = False
    fix_action: str | None = None
    source: str | None = None
    title: str | None = None
    author: str = ""
    source_lang: str = "ru"
    target_lang: str = "de"
    ruleset_apply: bool = False


class NamesUpdateRequest(BaseModel):
    names: list[dict[str, Any]]


class BookSettingsUpdateRequest(BaseModel):
    active_style: str
    translate_provider: str
    translate_model: str | None = None
    chunk_char_limit: int | None = None


def _global_style_options(repo_root: Path) -> list[dict[str, str]]:
    styles_root = repo_root / "styles"
    rows: list[dict[str, str]] = []
    if styles_root.exists():
        for path in sorted(styles_root.glob("*.md")):
            if path.stem.lower() == "readme":
                continue
            label = path.stem.replace("-", " ").title()
            rows.append({"id": path.stem, "label": label})
    if rows:
        return rows
    return [
        {"id": "stil-01-original", "label": "Stil 01 Original"},
        {"id": "stil-02-poetisch", "label": "Stil 02 Poetisch"},
        {"id": "stil-03-branderson", "label": "Stil 03 Branderson"},
    ]


def _repo_root(request: Request) -> Path:
    return Path(request.app.state.repo_root)


def _book_summary(book: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    style = str(book.get("style_mode") or "stil-01-original")
    ai = book.get("ai") or {}
    rows = chapter_rows(book, style, repo_root)
    missing = sum(int(row.get("Fehlt") or 0) for row in rows)
    return {
        "id": book.get("id"),
        "title": book.get("title"),
        "author": book.get("author"),
        "source_lang": book.get("source_lang"),
        "target_lang": book.get("target_lang"),
        "style_mode": style,
        "ai_provider": ai.get("provider") or "openrouter",
        "ai_model": ai.get("model") or "",
        "chunk_char_limit": ai.get("chunk_char_limit"),
        "chapters": len(rows),
        "missing_scenes": missing,
        "book_root": book.get("book_root"),
    }


def _load_book_or_404(repo_root: Path, book_id: str) -> dict[str, Any]:
    try:
        return book_by_id(book_id, repo_root)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _job_detail(
    job: dict[str, Any],
    repo_root: Path,
    log_lines: int = 80,
) -> dict[str, Any]:
    refreshed, running = dashboard_jobs.refresh_job(job, repo_root)
    if not refreshed:
        raise HTTPException(status_code=404, detail="Job nicht gefunden")
    tail = dashboard_jobs.read_log_tail(refreshed, repo_root, lines=log_lines)
    done, total = dashboard_jobs.progress_from_log(tail)
    item = dict(refreshed)
    item["running"] = running
    item["progress"] = {"done": done, "total": total}
    item["log_tail"] = tail
    return item


def _required(value: str | None, field: str) -> str:
    if value is None or not str(value).strip():
        raise HTTPException(status_code=400, detail=f"Pflichtfeld fehlt: {field}")
    return str(value)


def _encode_log_id(path: Path, repo_root: Path) -> str:
    rel = path.resolve().relative_to(repo_root.resolve()).as_posix()
    return base64.urlsafe_b64encode(rel.encode("utf-8")).decode("ascii").rstrip("=")


def _decode_log_id(log_id: str, repo_root: Path) -> Path:
    try:
        padded = log_id + ("=" * (-len(log_id) % 4))
        rel = base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Ungueltige Log-ID") from exc
    path = (repo_root / rel).resolve()
    root = repo_root.resolve()
    if root not in path.parents and path != root:
        raise HTTPException(status_code=400, detail="Logpfad liegt ausserhalb des Repos")
    return path


def _log_item(path: Path, repo_root: Path, source: str) -> dict[str, Any]:
    stat = path.stat()
    rel = path.resolve().relative_to(repo_root.resolve()).as_posix()
    return {
        "id": _encode_log_id(path, repo_root),
        "path": rel,
        "name": path.name,
        "source": source,
        "size": stat.st_size,
        "modified_at": datetime_from_timestamp(stat.st_mtime),
    }


def datetime_from_timestamp(value: float) -> str:
    from datetime import datetime

    return datetime.fromtimestamp(value).isoformat(timespec="seconds")


def _list_log_paths(repo_root: Path, book_id: str | None = None) -> list[tuple[Path, str]]:
    items: list[tuple[Path, str]] = []
    jobs_root = dashboard_jobs.jobs_dir(repo_root)
    if jobs_root.exists():
        items.extend((path, "dashboard-job") for path in jobs_root.glob("*.log") if path.is_file())
    books_root = repo_root / "books"
    if books_root.exists():
        pattern = f"{book_id}/status/logs/*.log.md" if book_id else "*/status/logs/*.log.md"
        items.extend((path, "book-status") for path in books_root.glob(pattern) if path.is_file())
    return sorted(items, key=lambda item: item[0].stat().st_mtime, reverse=True)


def _book_work_root(book: dict[str, Any], repo_root: Path) -> Path:
    root = Path(str(book["book_root"]))
    if not root.is_absolute():
        root = repo_root / root
    return root / "work"


def _read_text_if_exists(path: Path, limit_chars: int = 120_000) -> str:
    if not path.exists() or not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) > limit_chars:
        return text[-limit_chars:]
    return text


def _read_json_if_exists(path: Path) -> Any | None:
    if not path.exists() or not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


PLAIN_YAML_SCALAR_RE = re.compile(r"^[A-Za-z0-9_./:-]+$")
YAML_BOOLEAN_LIKE = {"true", "false", "yes", "no", "on", "off", "null", "none", "~"}


def _yaml_scalar(value: str | int) -> str:
    if isinstance(value, int):
        return str(value)
    text = str(value)
    if not text:
        return "''"
    if PLAIN_YAML_SCALAR_RE.match(text) and text.lower() not in YAML_BOOLEAN_LIKE:
        return text
    return json.dumps(text, ensure_ascii=False)


def _top_level_key_pattern(key: str) -> re.Pattern[str]:
    return re.compile(rf"^{re.escape(key)}\s*:.*$")


def _replace_top_level_scalar(lines: list[str], key: str, value: str | int) -> None:
    pattern = _top_level_key_pattern(key)
    replacement = f"{key}: {_yaml_scalar(value)}"
    for index, line in enumerate(lines):
        if pattern.match(line):
            lines[index] = replacement
            return
    lines.append(replacement)


def _find_top_level_block(lines: list[str], key: str) -> tuple[int, int] | None:
    pattern = _top_level_key_pattern(key)
    start: int | None = None
    for index, line in enumerate(lines):
        if pattern.match(line):
            start = index
            break
    if start is None:
        return None
    end = len(lines)
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if line and not line[0].isspace() and not line.startswith("#"):
            end = index
            break
    return start, end


def _set_nested_scalar(lines: list[str], block_key: str, key: str, value: str | int) -> None:
    block = _find_top_level_block(lines, block_key)
    if block is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append(f"{block_key}:")
        block = len(lines) - 1, len(lines)
    start, end = block
    child_pattern = re.compile(rf"^(\s+){re.escape(key)}\s*:.*$")
    inferred_indent = "  "
    for index in range(start + 1, end):
        child_match = re.match(r"^(\s+)\S", lines[index])
        if child_match:
            inferred_indent = child_match.group(1)
        match = child_pattern.match(lines[index])
        if match:
            lines[index] = f"{match.group(1)}{key}: {_yaml_scalar(value)}"
            return
    lines.insert(end, f"{inferred_indent}{key}: {_yaml_scalar(value)}")


def _write_book_settings_preserving_yaml(
    path: Path,
    *,
    style: str,
    provider: str,
    model: str | None,
    chunk_char_limit: int | None,
) -> None:
    text = path.read_text(encoding="utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    had_trailing_newline = text.endswith(("\n", "\r\n"))
    lines = text.splitlines()
    _replace_top_level_scalar(lines, "style_mode", style)
    _set_nested_scalar(lines, "ai", "provider", provider)
    if model:
        _set_nested_scalar(lines, "ai", "model", model.strip())
    if chunk_char_limit is not None:
        _set_nested_scalar(lines, "ai", "chunk_char_limit", int(chunk_char_limit))
    path.write_text(newline.join(lines) + (newline if had_trailing_newline else ""), encoding="utf-8")


def _file_info(path: Path, repo_root: Path) -> dict[str, Any] | None:
    if not path.exists() or not path.is_file():
        return None
    stat = path.stat()
    return {
        "path": path.resolve().relative_to(repo_root.resolve()).as_posix(),
        "name": path.name,
        "size": stat.st_size,
        "modified_at": datetime_from_timestamp(stat.st_mtime),
    }


def _review_artifacts(book: dict[str, Any], style: str, repo_root: Path) -> dict[str, Any]:
    work_root = _book_work_root(book, repo_root)
    review_root = work_root / "reviews" / style
    fix_root = work_root / "review-fixes" / style
    summary_json_path = review_root / "review-summary.json"
    summary_md_path = review_root / "review-summary.md"
    summary = _read_json_if_exists(summary_json_path)
    reports: list[dict[str, Any]] = []
    chapters_root = review_root / "chapters"
    if chapters_root.exists():
        for md_path in sorted(chapters_root.glob("*-review.md")):
            chapter = md_path.name.removesuffix("-review.md")
            json_path = chapters_root / f"{chapter}-review.json"
            reports.append(
                {
                    "chapter": chapter,
                    "markdown": _file_info(md_path, repo_root),
                    "json": _file_info(json_path, repo_root),
                    "content": _read_text_if_exists(md_path, limit_chars=80_000),
                    "data": _read_json_if_exists(json_path),
                }
            )
    fix_files = {
        "manifest": fix_root / "fix-manifest.json",
        "plan": fix_root / "fix-plan.txt",
        "manual_review": fix_root / "manual-review.md",
        "promotion_report": fix_root / "promotion-report.json",
    }
    return {
        "book_id": book.get("id"),
        "style": style,
        "exists": review_root.exists(),
        "review_root": jsonable(review_root, repo_root),
        "summary": summary,
        "summary_markdown": _read_text_if_exists(summary_md_path),
        "summary_file": _file_info(summary_md_path, repo_root),
        "summary_json_file": _file_info(summary_json_path, repo_root),
        "reports": reports,
        "fixes": {
            key: {
                "file": _file_info(path, repo_root),
                "content": _read_text_if_exists(path) if path.suffix.lower() in {".md", ".txt"} else "",
                "data": _read_json_if_exists(path) if path.suffix.lower() == ".json" else None,
            }
            for key, path in fix_files.items()
        },
    }


def _style_test_artifacts(
    book: dict[str, Any],
    chapter: str,
    scene: int | None,
    repo_root: Path,
) -> dict[str, Any]:
    output_root = book_output_root(repo_root, book)
    source_lang = str(book.get("source_lang") or "ru")
    scene_numbers = [
        number
        for path in list_source_scene_paths(output_root, chapter, source_lang)
        if (number := parse_scene_number(path, chapter)) is not None
    ]
    selected_scene = scene or (min(scene_numbers) if scene_numbers else None)
    source: dict[str, Any] | None = None
    styles: list[dict[str, Any]] = []
    if selected_scene is not None:
        source_path = source_scene_path(output_root, chapter, selected_scene, source_lang)
        source = {
            "scene": f"{selected_scene:02d}",
            "path": _file_info(source_path, repo_root),
            "content": _read_text_if_exists(source_path),
        }
        for profile in style_options(book, repo_root):
            style_id = str(profile.get("id") or "")
            scene_path = de_scene_path(output_root, chapter, selected_scene, style_id)
            generated_prompt_path = prompt_path(output_root, chapter, style_id, selected_scene)
            styles.append(
                {
                    "id": style_id,
                    "label": profile.get("label") or style_id,
                    "scene": {
                        "path": _file_info(scene_path, repo_root),
                        "content": _read_text_if_exists(scene_path),
                    },
                    "prompt": {
                        "path": _file_info(generated_prompt_path, repo_root),
                        "content": _read_text_if_exists(generated_prompt_path),
                    },
                    "has_output": scene_path.exists() or generated_prompt_path.exists(),
                }
            )
    return {
        "book_id": book.get("id"),
        "chapter": chapter,
        "source_lang": source_lang,
        "scenes": [f"{number:02d}" for number in sorted(set(scene_numbers))],
        "selected_scene": f"{selected_scene:02d}" if selected_scene is not None else None,
        "source": source,
        "styles": styles,
    }


def _build_action_command(plan: ActionPlanRequest, repo_root: Path) -> list[str]:
    action = plan.action.strip()
    allowed = [
        "assemble_chapter",
        "export",
        "extract_chapters",
        "extract_scenes",
        "illustration_batch",
        "init_book",
        "review",
        "review_fixes",
        "translate_batch",
        "translate_chapter",
    ]
    if action not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unbekannte Action: {action}. Erlaubt: {', '.join(allowed)}",
        )
    if action != "init_book":
        _load_book_or_404(repo_root, _required(plan.book_id, "book_id"))
    if action == "extract_chapters":
        return ["tools/extract_chapters.py", "--book", _required(plan.book_id, "book_id")]
    if action == "extract_scenes":
        return build_extract_scenes_command(
            _required(plan.book_id, "book_id"),
            _required(plan.chapter, "chapter"),
        )
    if action == "assemble_chapter":
        return build_assemble_chapter_command(
            _required(plan.book_id, "book_id"),
            _required(plan.chapter, "chapter"),
            _required(plan.style, "style"),
        )
    if action == "translate_chapter":
        return build_translate_chapter_command(
            TranslateRunOptions(
                book_id=_required(plan.book_id, "book_id"),
                chapter=_required(plan.chapter, "chapter"),
                style=_required(plan.style, "style"),
                provider=_required(plan.provider, "provider"),
                model=plan.model,
                ollama_model=plan.ollama_model,
                chunk_char_limit=plan.chunk_char_limit,
                scene=plan.scene,
                overwrite=plan.overwrite,
                dry_run=plan.dry_run,
            )
        )
    if action == "translate_batch":
        return build_translate_batch_command(
            TranslateBatchOptions(
                book_id=_required(plan.book_id, "book_id"),
                style=_required(plan.style, "style"),
                provider=_required(plan.provider, "provider"),
                scope=_required(plan.scope, "scope"),
                chapter=plan.chapter,
                start_chapter=plan.start_chapter,
                end_chapter=plan.end_chapter,
                model=plan.model,
                ollama_model=plan.ollama_model,
                chunk_char_limit=plan.chunk_char_limit,
                overwrite=plan.overwrite,
                auto_status=plan.auto_status,
                dry_run=plan.dry_run,
                assemble_after=plan.assemble_after,
            )
        )
    if action == "review":
        return build_review_command(
            ReviewOptions(
                book_id=_required(plan.book_id, "book_id"),
                style=_required(plan.style, "style"),
                scope=_required(plan.scope, "scope"),
                chapter=plan.chapter,
                start_chapter=plan.start_chapter,
                end_chapter=plan.end_chapter,
                llm=plan.llm,
                llm_scope=plan.llm_scope,
                model=plan.model,
                ollama_model=plan.ollama_model,
                fail_on_errors=plan.fail_on_errors,
                dry_run=plan.dry_run,
            )
        )
    if action == "export":
        return build_export_command(
            ExportOptions(
                book_id=_required(plan.book_id, "book_id"),
                style=_required(plan.style, "style"),
                scope=_required(plan.scope, "scope"),
                export_format=_required(plan.export_format, "export_format"),
                chapter=plan.chapter,
                allow_partial=plan.allow_partial,
            )
        )
    if action == "illustration_batch":
        return build_illustration_batch_command(
            IllustrationBatchOptions(
                book_id=_required(plan.book_id, "book_id"),
                style=_required(plan.style, "style"),
                kind=_required(plan.kind, "kind"),
                scope=_required(plan.scope, "scope"),
                chapter=plan.chapter,
                start_chapter=plan.start_chapter,
                end_chapter=plan.end_chapter,
                backend=plan.backend,
                model=plan.model,
                moodboard=plan.moodboard,
                aspect_ratio=plan.aspect_ratio,
                quality=plan.quality,
                missing=plan.missing,
                overwrite=plan.overwrite,
                dry_run=plan.dry_run,
                no_reference=plan.no_reference,
                allow_paid_generation=plan.allow_paid_generation,
            )
        )
    if action == "review_fixes":
        return build_review_fixes_command(
            _required(plan.book_id, "book_id"),
            _required(plan.style, "style"),
            _required(plan.fix_action, "fix_action"),
        )
    if action == "init_book":
        return build_init_book_command(
            NewBookOptions(
                source=_required(plan.source, "source"),
                title=_required(plan.title, "title"),
                author=plan.author,
                style=_required(plan.style, "style"),
                source_lang=plan.source_lang,
                target_lang=plan.target_lang,
                ruleset_apply=plan.ruleset_apply,
            )
        )
    raise HTTPException(status_code=400, detail=f"Nicht geplante Action: {action}")


def _background_job_metadata(plan: ActionPlanRequest) -> tuple[str, str, str, str]:
    action = plan.action.strip()
    if action == "review":
        return (
            _required(plan.book_id, "book_id"),
            _required(plan.style, "style"),
            f"review:{plan.llm}",
            "review",
        )
    if action == "translate_batch":
        return (
            _required(plan.book_id, "book_id"),
            _required(plan.style, "style"),
            _required(plan.provider, "provider"),
            "batch",
        )
    if action == "translate_chapter":
        return (
            _required(plan.book_id, "book_id"),
            _required(plan.style, "style"),
            _required(plan.provider, "provider"),
            "translate",
        )
    if action == "export":
        return (
            _required(plan.book_id, "book_id"),
            _required(plan.style, "style"),
            f"export:{_required(plan.export_format, 'export_format')}",
            "export",
        )
    if action == "illustration_batch":
        return (
            _required(plan.book_id, "book_id"),
            _required(plan.style, "style"),
            "higgsfield",
            "illustration_batch",
        )
    if action == "review_fixes":
        return (
            _required(plan.book_id, "book_id"),
            _required(plan.style, "style"),
            f"review-fixes:{_required(plan.fix_action, 'fix_action')}",
            "review_fixes",
        )
    if action == "extract_chapters":
        return (
            _required(plan.book_id, "book_id"),
            "",
            "setup",
            "extract_chapters",
        )
    if action == "init_book":
        return (
            "setup",
            _required(plan.style, "style"),
            "setup",
            "init_book",
        )
    raise HTTPException(
        status_code=400,
        detail=(
            "Als Hintergrundjob sind aktuell nur review, translate_batch, "
            "translate_chapter, export, illustration_batch, review_fixes, "
            "extract_chapters und init_book erlaubt."
        ),
    )


async def _job_event_stream(
    job_id: str,
    request: Request,
    repo_root: Path,
    interval_sec: float = 1.0,
    log_lines: int = 80,
):
    while True:
        if await request.is_disconnected():
            break
        job = dashboard_jobs.load_job(job_id, repo_root)
        if not job:
            yield {
                "event": "error",
                "data": json.dumps({"detail": f"Job nicht gefunden: {job_id}"}, ensure_ascii=False),
            }
            break
        detail = _job_detail(job, repo_root, log_lines=log_lines)
        yield {
            "event": "job",
            "data": json.dumps(jsonable(detail, repo_root), ensure_ascii=False),
        }
        if str(detail.get("status") or "") in dashboard_jobs.TERMINAL_STATUSES:
            break
        await asyncio.sleep(interval_sec)


def _mount_frontend(app: FastAPI, repo_root: Path) -> None:
    dist_root = repo_root / "webapp" / "frontend" / "dist"
    index_path = dist_root / "index.html"
    if not index_path.exists():
        return

    assets_root = dist_root / "assets"
    if assets_root.exists():
        app.mount("/assets", StaticFiles(directory=assets_root), name="frontend-assets")

    @app.get("/", include_in_schema=False)
    def frontend_index() -> FileResponse:
        return FileResponse(index_path)

    @app.get("/{full_path:path}", include_in_schema=False)
    def frontend_spa(full_path: str) -> FileResponse:
        if full_path.startswith("api/") or full_path == "health":
            raise HTTPException(status_code=404, detail="Not found")
        requested = (dist_root / full_path).resolve()
        try:
            requested.relative_to(dist_root.resolve())
        except ValueError as exc:
            raise HTTPException(status_code=404, detail="Not found") from exc
        if requested.is_file():
            return FileResponse(requested)
        return FileResponse(index_path)


def create_app(repo_root: Path = REPO_ROOT) -> FastAPI:
    app = FastAPI(
        title="Peter the One Workbench API",
        version="0.1.0",
    )
    app.state.repo_root = Path(repo_root)

    @app.get("/health")
    def health(request: Request) -> dict[str, Any]:
        root = _repo_root(request)
        return {"status": "ok", "repo_root": jsonable(root, root)}

    @app.get("/api/books")
    def api_books(request: Request) -> dict[str, Any]:
        root = _repo_root(request)
        books = load_books(root)
        return {
            "books": jsonable([_book_summary(book, root) for book in books], root),
        }

    @app.get("/api/setup")
    def api_setup(request: Request) -> dict[str, Any]:
        root = _repo_root(request)
        books = load_books(root)
        source_rows = []
        for path in unregistered_sources(root, books):
            title, author = guess_title_author(path)
            source_rows.append({
                "path": path.resolve().relative_to(root.resolve()).as_posix(),
                "name": path.name,
                "title": title,
                "author": author,
            })
        prompt_path = root / "docs" / "book-metadata-prompt.md"
        return {
            "unregistered_sources": source_rows,
            "styles": _global_style_options(root),
            "metadata_prompt": _read_text_if_exists(prompt_path),
            "books": jsonable([_book_summary(book, root) for book in books], root),
        }

    @app.get("/api/books/{book_id}")
    def api_book(book_id: str, request: Request) -> dict[str, Any]:
        root = _repo_root(request)
        book = _load_book_or_404(root, book_id)
        return {
            "book": jsonable(book, root),
            "summary": jsonable(_book_summary(book, root), root),
        }

    @app.get("/api/books/{book_id}/chapters")
    def api_book_chapters(
        book_id: str,
        request: Request,
        style: str | None = Query(default=None),
    ) -> dict[str, Any]:
        root = _repo_root(request)
        book = _load_book_or_404(root, book_id)
        selected_style = style or str(book.get("style_mode") or "stil-01-original")
        rows = chapter_rows(book, selected_style, root)
        return {
            "book_id": book_id,
            "style": selected_style,
            "chapters": jsonable(rows, root),
        }

    @app.get("/api/books/{book_id}/styles")
    def api_book_styles(book_id: str, request: Request) -> dict[str, Any]:
        root = _repo_root(request)
        book = _load_book_or_404(root, book_id)
        return {
            "book_id": book_id,
            "default_style": str(book.get("style_mode") or "stil-01-original"),
            "styles": jsonable(style_options(book, root), root),
        }

    @app.get("/api/books/{book_id}/names")
    def api_book_names(book_id: str, request: Request) -> dict[str, Any]:
        root = _repo_root(request)
        book = _load_book_or_404(root, book_id)
        rows = [
            row for row in editable_name_rows(book, root)
            if str(row.get("source") or "").strip() or str(row.get("target") or "").strip()
        ]
        return {
            "book_id": book_id,
            "names": jsonable(rows, root),
        }

    @app.put("/api/books/{book_id}/names")
    def api_book_names_update(book_id: str, payload: NamesUpdateRequest, request: Request) -> dict[str, Any]:
        root = _repo_root(request)
        book = _load_book_or_404(root, book_id)
        normalized = normalize_name_rows(payload.names)
        errors: list[str] = []
        for index, row in enumerate(normalized, start=1):
            if not str(row.get("source") or "").strip():
                errors.append(f"Zeile {index}: source fehlt")
            if not str(row.get("target") or "").strip():
                errors.append(f"Zeile {index}: target fehlt")
        if errors:
            raise HTTPException(status_code=400, detail={"errors": errors})
        write_names(names_path(book, root), normalized)
        rows = [
            row for row in editable_name_rows(book, root)
            if str(row.get("source") or "").strip() or str(row.get("target") or "").strip()
        ]
        return {
            "book_id": book_id,
            "names": jsonable(rows, root),
            "saved": True,
        }

    @app.put("/api/books/{book_id}/settings")
    def api_book_settings_update(book_id: str, payload: BookSettingsUpdateRequest, request: Request) -> dict[str, Any]:
        root = _repo_root(request)
        book = _load_book_or_404(root, book_id)
        available_styles = {str(item.get("id")) for item in style_options(book, root)}
        style = payload.active_style.strip()
        if not style:
            raise HTTPException(status_code=400, detail="active_style fehlt")
        if available_styles and style not in available_styles:
            raise HTTPException(status_code=400, detail=f"Unbekannter Stil: {style}")
        provider = payload.translate_provider.strip()
        if provider not in {"openrouter", "ollama", "prompt_file", "workspace_ai"}:
            raise HTTPException(status_code=400, detail=f"Unbekannter Provider: {provider}")
        chunk_char_limit = payload.chunk_char_limit
        if chunk_char_limit is not None and chunk_char_limit < 1000:
            raise HTTPException(status_code=400, detail="chunk_char_limit muss mindestens 1000 sein")

        project = book_project(root, book_id)
        _write_book_settings_preserving_yaml(
            project.root / "book.yaml",
            style=style,
            provider=provider,
            model=payload.translate_model,
            chunk_char_limit=chunk_char_limit,
        )

        saved_book = _load_book_or_404(root, book_id)
        return {
            "book_id": book_id,
            "saved": True,
            "summary": jsonable(_book_summary(saved_book, root), root),
            "book": jsonable(saved_book, root),
        }

    @app.get("/api/books/{book_id}/reviews/{style}")
    def api_book_review(book_id: str, style: str, request: Request) -> dict[str, Any]:
        root = _repo_root(request)
        book = _load_book_or_404(root, book_id)
        return jsonable(_review_artifacts(book, style, root), root)

    @app.get("/api/books/{book_id}/exports/{style}")
    def api_book_exports(
        book_id: str,
        style: str,
        request: Request,
        scope: str = Query(default="chapter"),
        chapter: str | None = Query(default=None),
    ) -> dict[str, Any]:
        root = _repo_root(request)
        book = _load_book_or_404(root, book_id)
        if scope not in {"chapter", "book"}:
            raise HTTPException(status_code=400, detail="scope muss 'chapter' oder 'book' sein")
        rows = chapter_rows(book, style, root)
        chapters = [
            str(row.get("Kapitel") or "").strip()
            for row in rows
            if str(row.get("Kapitel") or "").strip()
        ]
        selected_chapter = chapter or (chapters[0] if chapters else "")
        context = export_context(
            book,
            style_options(book, root),
            style,
            selected_chapter,
            chapters,
            scope,
            root,
        )
        latest_files = [
            item
            for item in (_file_info(path, root) for path in latest_export_files(book, style, root)[:20])
            if item is not None
        ]
        return jsonable(
            {
                "book_id": book_id,
                "style": style,
                "scope": scope,
                "chapter": selected_chapter,
                "context": context,
                "latest_files": latest_files,
            },
            root,
        )

    @app.get("/api/books/{book_id}/style-test")
    def api_style_test(
        book_id: str,
        request: Request,
        chapter: str = Query(...),
        scene: int | None = Query(default=None, ge=1),
    ) -> dict[str, Any]:
        root = _repo_root(request)
        book = _load_book_or_404(root, book_id)
        return jsonable(_style_test_artifacts(book, chapter, scene, root), root)

    @app.get("/api/models")
    def api_models(request: Request) -> dict[str, Any]:
        root = _repo_root(request)
        return {"models": jsonable(load_models(root), root)}

    @app.get("/api/jobs")
    def api_jobs(
        request: Request,
        limit: int = Query(default=20, ge=1, le=100),
    ) -> dict[str, Any]:
        root = _repo_root(request)
        jobs = []
        for job in dashboard_jobs.list_jobs(root)[:limit]:
            jobs.append(_job_detail(job, root, log_lines=20))
        return {"jobs": jsonable(jobs, root)}

    @app.get("/api/jobs/{job_id}")
    def api_job_detail(
        job_id: str,
        request: Request,
        log_lines: int = Query(default=80, ge=0, le=500),
    ) -> dict[str, Any]:
        root = _repo_root(request)
        job = dashboard_jobs.load_job(job_id, root)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job nicht gefunden: {job_id}")
        return {"job": jsonable(_job_detail(job, root, log_lines=log_lines), root)}

    @app.get("/api/logs")
    def api_logs(
        request: Request,
        book_id: str | None = Query(default=None),
        limit: int = Query(default=50, ge=1, le=200),
    ) -> dict[str, Any]:
        root = _repo_root(request)
        if book_id:
            _load_book_or_404(root, book_id)
        logs = [_log_item(path, root, source) for path, source in _list_log_paths(root, book_id)[:limit]]
        return {"logs": jsonable(logs, root)}

    @app.get("/api/logs/{log_id}")
    def api_log_detail(
        log_id: str,
        request: Request,
        lines: int = Query(default=300, ge=0, le=2000),
    ) -> dict[str, Any]:
        root = _repo_root(request)
        path = _decode_log_id(log_id, root)
        allowed_suffixes = {".log", ".md"}
        if not path.is_file() or path.suffix.lower() not in allowed_suffixes:
            raise HTTPException(status_code=404, detail="Log nicht gefunden")
        rel = path.relative_to(root.resolve()).as_posix()
        if not (rel.startswith("var/dashboard-jobs/") or "/status/logs/" in rel):
            raise HTTPException(status_code=400, detail="Pfad ist kein bekannter Logpfad")
        text = path.read_text(encoding="utf-8", errors="replace")
        content = "\n".join(text.splitlines()[-lines:]) if lines else text
        item = _log_item(path, root, "dashboard-job" if rel.startswith("var/dashboard-jobs/") else "book-status")
        return {
            "log": jsonable(item, root),
            "content": content,
            "truncated": lines > 0 and len(text.splitlines()) > lines,
        }

    @app.post("/api/jobs/{job_id}/stop")
    def api_job_stop(job_id: str, request: Request) -> dict[str, Any]:
        root = _repo_root(request)
        job = dashboard_jobs.load_job(job_id, root)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job nicht gefunden: {job_id}")
        refreshed, running = dashboard_jobs.refresh_job(job, root)
        if not refreshed:
            raise HTTPException(status_code=404, detail=f"Job nicht gefunden: {job_id}")
        if not running:
            return {
                "job": jsonable(_job_detail(refreshed, root), root),
                "stopped": False,
                "message": "Job laeuft nicht.",
            }
        result = dashboard_jobs.request_stop(refreshed, root)
        stopped_job = dashboard_jobs.load_job(job_id, root) or refreshed
        return {
            "job": jsonable(_job_detail(stopped_job, root), root),
            "stopped": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    @app.post("/api/actions/plan")
    def api_action_plan(plan: ActionPlanRequest, request: Request) -> dict[str, Any]:
        root = _repo_root(request)
        command = _build_action_command(plan, root)
        return {
            "action": plan.action,
            "command": command,
            "command_text": " ".join(command),
            "cwd": jsonable(root, root),
        }

    @app.post("/api/jobs")
    def api_job_start(plan: ActionPlanRequest, request: Request) -> dict[str, Any]:
        root = _repo_root(request)
        if plan.dry_run and plan.action.strip() != "illustration_batch":
            raise HTTPException(
                status_code=400,
                detail="Dry-runs werden nicht als Hintergrundjob gestartet. Nutze /api/actions/plan.",
            )
        command = _build_action_command(plan, root)
        book_id, style, provider, kind = _background_job_metadata(plan)
        job = dashboard_jobs.start_job(
            command,
            book_id=book_id,
            style=style,
            provider=provider,
            kind=kind,
            repo_root=root,
        )
        return {
            "job": jsonable(_job_detail(job, root, log_lines=20), root),
            "command": command,
        }

    @app.get("/api/jobs/{job_id}/events")
    async def api_job_events(
        job_id: str,
        request: Request,
        interval_sec: float = Query(default=1.0, ge=0.1, le=10.0),
        log_lines: int = Query(default=80, ge=0, le=500),
    ):
        root = _repo_root(request)
        if dashboard_jobs.load_job(job_id, root) is None:
            raise HTTPException(status_code=404, detail=f"Job nicht gefunden: {job_id}")
        return EventSourceResponse(
            _job_event_stream(
                job_id,
                request,
                root,
                interval_sec=interval_sec,
                log_lines=log_lines,
            )
        )

    _mount_frontend(app, app.state.repo_root)
    return app


app = create_app()
