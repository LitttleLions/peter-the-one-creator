"""Framework-neutral command builders for the local workbench UI."""

from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path
from typing import Any

import yaml

from lib.name_registry import load_names
from lib.output_paths import (
    book_exports_root,
    book_output_root,
    list_source_scene_paths,
    parse_scene_number,
)
from lib.translation_chunks import scene_chunks, should_chunk
from lib.workbench_state import chapter_rows, load_style_profiles, scene_counts


@dataclass(frozen=True)
class NewBookOptions:
    source: str
    title: str
    author: str
    style: str
    source_lang: str = "ru"
    target_lang: str = "de"
    ruleset_apply: bool = False


@dataclass(frozen=True)
class TranslateRunOptions:
    book_id: str
    chapter: str
    style: str
    provider: str
    model: str | None = None
    ollama_model: str | None = None
    chunk_char_limit: int | None = None
    scene: str | None = None
    overwrite: bool = False
    dry_run: bool = False


@dataclass(frozen=True)
class TranslateBatchOptions:
    book_id: str
    style: str
    provider: str
    scope: str
    chapter: str | None = None
    start_chapter: str | None = None
    end_chapter: str | None = None
    model: str | None = None
    ollama_model: str | None = None
    chunk_char_limit: int | None = None
    overwrite: bool = False
    auto_status: bool = False
    dry_run: bool = False
    assemble_after: bool = False


@dataclass(frozen=True)
class ReviewOptions:
    book_id: str
    style: str
    scope: str
    chapter: str | None = None
    start_chapter: str | None = None
    end_chapter: str | None = None
    llm: str = "none"
    llm_scope: str = "flagged"
    model: str | None = None
    ollama_model: str | None = None
    fail_on_errors: bool = False
    dry_run: bool = False


@dataclass(frozen=True)
class ExportOptions:
    book_id: str
    style: str
    scope: str
    export_format: str
    chapter: str | None = None
    allow_partial: bool = False


@dataclass(frozen=True)
class IllustrationBatchOptions:
    book_id: str
    style: str
    kind: str
    scope: str
    chapter: str | None = None
    start_chapter: str | None = None
    end_chapter: str | None = None
    backend: str | None = None
    model: str | None = None
    moodboard: str | None = None
    aspect_ratio: str | None = None
    quality: str | None = None
    missing: bool = False
    overwrite: bool = False
    dry_run: bool = False
    no_reference: bool = False
    allow_paid_generation: bool = False


@dataclass(frozen=True)
class TranslationContext:
    output_root: Path
    output_root_label: str
    counts: dict[str, Any]
    missing_count: int
    scene_choices: list[str]
    default_scene_index: int
    source_lang: str
    source_lang_label: str
    unit_label: str
    chapter_as_scene: bool


@dataclass(frozen=True)
class ReviewContext:
    output_root: Path
    review_root: Path
    summary_json: Path
    summary_md: Path
    fix_root: Path
    fix_manifest: Path
    fix_plan: Path
    manual_review: Path
    promotion_report: Path


@dataclass(frozen=True)
class ExportContext:
    output_root: Path
    export_meta: dict[str, Any]
    cover_status: str
    illustrations_status: str
    front_enabled: list[str]
    style_rows: list[dict[str, Any]]
    chapter_metrics: dict[str, Any]
    missing_chapters: list[str]
    selected_chapters: list[str]
    illustration_counts: dict[str, int]


SOURCE_EXTENSIONS = (".rtf", ".doc", ".txt", ".md")
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


def build_extract_scenes_command(book_id: str, chapter: str) -> list[str]:
    return ["tools/extract_scenes.py", "--book", book_id, "--chapter", chapter]


def build_init_book_command(options: NewBookOptions) -> list[str]:
    cmd = [
        "tools/init_book.py",
        "--source", options.source,
        "--title", options.title,
        "--author", options.author,
        "--style", options.style,
        "--source-lang", options.source_lang,
        "--target-lang", options.target_lang,
    ]
    cmd.append("--ruleset-apply" if options.ruleset_apply else "--no-ruleset-apply")
    return cmd


def build_assemble_chapter_command(book_id: str, chapter: str, style: str) -> list[str]:
    return [
        "tools/assemble_chapter.py",
        "--book", book_id,
        "--chapter", chapter,
        "--style", style,
    ]


def build_translate_chapter_command(options: TranslateRunOptions) -> list[str]:
    cmd = [
        "tools/translate_chapter.py",
        "--book", options.book_id,
        "--chapter", options.chapter,
        "--style", options.style,
        "--provider", options.provider,
    ]
    if options.provider == "openrouter" and options.model:
        cmd.extend(["--model", options.model])
    elif options.provider == "ollama" and options.ollama_model:
        cmd.extend(["--model", options.ollama_model])
    if options.chunk_char_limit is not None:
        cmd.extend(["--chunk-char-limit", str(int(options.chunk_char_limit))])
    if options.scene:
        cmd.extend(["--scene", options.scene])
    if options.overwrite:
        cmd.append("--overwrite")
    if options.dry_run:
        cmd.extend(["--dry-run", "--dry-run-first-scene"])
    return cmd


def build_translate_batch_command(options: TranslateBatchOptions) -> list[str]:
    cmd = [
        "tools/translate_batch.py",
        "--book", options.book_id,
        "--style", options.style,
        "--provider", options.provider,
    ]
    if options.provider == "openrouter" and options.model:
        cmd.extend(["--model", options.model])
    elif options.provider == "ollama" and options.ollama_model:
        cmd.extend(["--model", options.ollama_model])
    if options.chunk_char_limit is not None:
        cmd.extend(["--chunk-char-limit", str(int(options.chunk_char_limit))])
    if options.scope == "Aktuelles Kapitel":
        if options.chapter:
            cmd.extend(["--chapter", options.chapter])
    elif options.scope == "Bereich":
        if options.start_chapter and options.end_chapter:
            cmd.extend(["--from", options.start_chapter, "--to", options.end_chapter])
    else:
        cmd.append("--missing")
    if options.overwrite:
        cmd.append("--overwrite")
    if options.assemble_after and options.provider in ("openrouter", "ollama"):
        cmd.append("--assemble-after")
    if options.auto_status:
        cmd.append("--auto-status")
    if options.dry_run:
        cmd.append("--dry-run")
    return cmd


def build_review_command(options: ReviewOptions) -> list[str]:
    cmd = [
        "tools/review_manuscript.py",
        "--book", options.book_id,
        "--style", options.style,
        "--llm", options.llm,
        "--llm-scope", options.llm_scope,
    ]
    if options.scope == "Aktuelles Kapitel":
        if options.chapter:
            cmd.extend(["--chapter", options.chapter])
    elif options.scope == "Bereich":
        if options.start_chapter and options.end_chapter:
            cmd.extend(["--from", options.start_chapter, "--to", options.end_chapter])
    else:
        cmd.append("--all")
    if options.llm == "openrouter" and options.model:
        cmd.extend(["--model", options.model])
    if options.llm == "ollama" and options.ollama_model:
        cmd.extend(["--ollama-model", options.ollama_model])
    if options.fail_on_errors:
        cmd.append("--fail-on-errors")
    if options.dry_run:
        cmd.append("--dry-run")
    return cmd


def build_review_fixes_command(book_id: str, style: str, action: str) -> list[str]:
    if action not in {"plan", "stage", "promote"}:
        raise ValueError(f"Unbekannte Review-Fix-Aktion: {action}")
    return ["tools/apply_review_suggestions.py", "--book", book_id, "--style", style, f"--{action}"]


def build_export_command(options: ExportOptions) -> list[str]:
    cmd = [
        "tools/export_manuscript.py",
        "--book", options.book_id,
        "--style", options.style,
        "--scope", options.scope,
        "--format", options.export_format,
    ]
    if options.scope == "chapter" and options.chapter:
        cmd.extend(["--chapter", options.chapter])
    if options.allow_partial:
        cmd.append("--allow-partial")
    return cmd


def build_illustration_batch_command(options: IllustrationBatchOptions) -> list[str]:
    cmd = [
        "tools/generate_illustration_batch.py",
        "--book", options.book_id,
        "--style", options.style,
        "--kind", options.kind,
    ]
    if options.scope == "chapter":
        if not options.chapter:
            raise ValueError("chapter ist fuer Illustration-Scope 'chapter' erforderlich.")
        cmd.extend(["--chapter", options.chapter])
    elif options.scope == "range":
        if not options.start_chapter:
            raise ValueError("start_chapter ist fuer Illustration-Scope 'range' erforderlich.")
        cmd.extend(["--from", options.start_chapter])
        if options.end_chapter:
            cmd.extend(["--to", options.end_chapter])
    else:
        raise ValueError(f"Unbekannter Illustration-Scope: {options.scope}")
    optional_values = {
        "--backend": options.backend,
        "--model": options.model,
        "--moodboard": options.moodboard,
        "--aspect-ratio": options.aspect_ratio,
        "--quality": options.quality,
    }
    for flag, value in optional_values.items():
        if value:
            cmd.extend([flag, str(value)])
    if options.missing:
        cmd.append("--missing")
    if options.overwrite:
        cmd.append("--overwrite")
    if options.dry_run:
        cmd.append("--dry-run")
    if options.no_reference:
        cmd.append("--no-reference")
    if options.allow_paid_generation:
        cmd.append("--allow-paid-generation")
    return cmd


def unregistered_sources(repo_root: Path, books: list[dict[str, Any]]) -> list[Path]:
    registered = {
        (repo_root / str(book.get("source_path", ""))).resolve()
        for book in books
        if book.get("source_path")
    }
    candidates: list[Path] = []
    books_dir = repo_root / "books"
    for suffix in SOURCE_EXTENSIONS:
        candidates.extend(books_dir.glob(f"*{suffix}"))
    return sorted(
        [path for path in candidates if path.resolve() not in registered],
        key=lambda path: path.name.lower(),
    )


def guess_title_author(path: Path) -> tuple[str, str]:
    stem = path.stem.strip()
    if " - " in stem:
        author, title = stem.split(" - ", 1)
        return title.strip(), author.strip()
    return stem, ""


def translation_context(
    book: dict[str, Any],
    chapter: str,
    style: str,
    repo_root: Path,
) -> TranslationContext:
    output_root = book_output_root(repo_root, book)
    counts = scene_counts(book, chapter, style, repo_root)
    source_lang = str(book.get("source_lang") or "ru")
    structure_mode = ((book.get("structure") or {}).get("mode") or "scenes")
    chapter_as_scene = structure_mode == "chapter_as_scene"
    if chapter_as_scene:
        scene_choices = ["aktuelles Kapitel"]
        default_scene_index = 0
    else:
        scene_choices = ["alle fehlenden"]
        scene_choices.extend(f"{num:02d}" for num in counts["missing"])
        next_missing = counts.get("next_missing")
        default_scene_index = (
            scene_choices.index(f"{next_missing:02d}") if next_missing is not None else 0
        )
    return TranslationContext(
        output_root=output_root,
        output_root_label=str(output_root.relative_to(repo_root)).replace("\\", "/"),
        counts=counts,
        missing_count=len(counts["missing"]),
        scene_choices=scene_choices,
        default_scene_index=default_scene_index,
        source_lang=source_lang,
        source_lang_label=source_lang.upper(),
        unit_label="Kapitel" if chapter_as_scene else "Szenen",
        chapter_as_scene=chapter_as_scene,
    )


def review_context(book: dict[str, Any], style: str, repo_root: Path) -> ReviewContext:
    output_root = book_output_root(repo_root, book)
    review_root = output_root / "reviews" / style
    fix_root = output_root / "review-fixes" / style
    return ReviewContext(
        output_root=output_root,
        review_root=review_root,
        summary_json=review_root / "review-summary.json",
        summary_md=review_root / "review-summary.md",
        fix_root=fix_root,
        fix_manifest=fix_root / "fix-manifest.json",
        fix_plan=fix_root / "fix-plan.txt",
        manual_review=fix_root / "manual-review.md",
        promotion_report=fix_root / "promotion-report.json",
    )


def export_context(
    book: dict[str, Any],
    styles: list[dict[str, Any]],
    style: str,
    chapter: str,
    chapters: list[str],
    export_scope: str,
    repo_root: Path,
) -> ExportContext:
    output_root = book_output_root(repo_root, book)
    export_meta = load_export_meta(book, repo_root)
    cover_cfg = export_meta.get("cover", {}) or {}
    front_cfg = export_meta.get("front_matter", {}) or {}
    illustrations_cfg = export_meta.get("illustrations", {}) or {}
    cover_mode = cover_cfg.get("mode", "placeholder")
    cover_image = str(cover_cfg.get("image_path") or "").strip()
    cover_status = (
        cover_image if cover_mode == "image" and cover_image else "Automatisches Platzhalter-Cover"
    )
    front_enabled = [
        name for name, enabled in [
            ("Cover im Text", front_cfg.get("cover_in_body", True)),
            ("Beschreibung", front_cfg.get("description_page", True)),
            ("Impressum", front_cfg.get("imprint_page", True)),
            ("Inhalt", front_cfg.get("toc_page", True)),
        ]
        if enabled
    ]
    style_rows = exportable_style_rows(book, styles, chapter, repo_root)
    source_lang = str(book.get("source_lang") or "ru")
    if export_scope == "chapter":
        counts = scene_counts(book, chapter, style, repo_root)
        missing_chapters = [chapter] if counts["missing"] else []
        chapter_metrics = {
            "scope": "chapter",
            "chapter": chapter,
            "chapters": 1 if chapter else 0,
            "source_label": f"{source_lang.upper()}-Szenen",
            "source_scenes": counts["ru"],
            "de_scenes": counts["de"],
            "missing": len(counts["missing"]),
            "missing_scenes": counts["missing"],
        }
    else:
        rows = chapter_rows(book, style, repo_root)
        missing_chapters = [
            row["Kapitel"] for row in rows if int(row.get("Fehlt") or 0) > 0
        ]
        chapter_metrics = {
            "scope": "book",
            "chapter": "",
            "chapters": len(rows),
            "source_label": f"{source_lang.upper()}-Szenen",
            "source_scenes": sum(int(row.get("RU") or 0) for row in rows),
            "de_scenes": sum(int(row.get("DE") or 0) for row in rows),
            "missing": sum(int(row.get("Fehlt") or 0) for row in rows),
            "missing_scenes": [],
        }
    selected_chapters = [chapter] if export_scope == "chapter" and chapter else chapters
    illustration_counts = count_export_illustrations(
        book,
        export_meta,
        selected_chapters,
        repo_root,
    )
    return ExportContext(
        output_root=output_root,
        export_meta=export_meta,
        cover_status=cover_status,
        illustrations_status="aktiv" if illustrations_cfg.get("enabled", False) else "aus",
        front_enabled=front_enabled,
        style_rows=style_rows,
        chapter_metrics=chapter_metrics,
        missing_chapters=missing_chapters,
        selected_chapters=selected_chapters,
        illustration_counts=illustration_counts,
    )


def latest_export_files(book: dict[str, Any], style: str, repo_root: Path) -> list[Path]:
    export_root = book_exports_root(repo_root, book) / style
    if not export_root.exists():
        return []
    paths: list[Path] = []
    for pattern in (
        "chapter/docx/*.docx",
        "chapter/epub/*.epub",
        "chapter/pdf/*.pdf",
        "book/docx/*.docx",
        "book/epub/*.epub",
        "book/pdf/*.pdf",
        "docx/*.docx",
        "epub/*.epub",
        "pdf/*.pdf",
    ):
        paths.extend(export_root.glob(pattern))
    return sorted(paths, key=lambda path: path.stat().st_mtime, reverse=True)


def exportable_style_rows(
    book: dict[str, Any],
    styles: list[dict[str, Any]],
    chapter: str,
    repo_root: Path,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in styles:
        sid = item.get("id")
        if not sid:
            continue
        current = scene_counts(book, chapter, sid, repo_root) if chapter else {
            "ru": 0,
            "de": 0,
            "missing": [],
        }
        all_rows = chapter_rows(book, sid, repo_root)
        rows.append({
            "Stil": sid,
            "Name": item.get("label") or sid,
            "Aktuelles Kapitel DE": current["de"],
            "Aktuelles Kapitel fehlt": len(current["missing"]),
            "Buch DE": sum(int(row.get("DE") or 0) for row in all_rows),
            "Buch fehlt": sum(int(row.get("Fehlt") or 0) for row in all_rows),
        })
    return rows


def load_export_meta(book: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    path = repo_root / str(book.get("export_config", ""))
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    defaults = data.get("defaults", {}) or {}
    book_cfg = data.get("book", {}) or {}
    meta = {**defaults, **book_cfg}
    for key in ("cover", "front_matter", "output", "illustrations"):
        merged = {
            **(defaults.get(key, {}) or {}),
            **(book_cfg.get(key, {}) or {}),
        }
        if merged:
            meta[key] = merged
    return meta


def oversized_source_scenes(
    book: dict[str, Any],
    chapter_id: str,
    limit: int,
    repo_root: Path,
) -> list[dict[str, Any]]:
    if not chapter_id or limit <= 0:
        return []
    output_root = book_output_root(repo_root, book)
    source_lang = str(book.get("source_lang") or "ru")
    items: list[dict[str, Any]] = []
    for path in list_source_scene_paths(output_root, chapter_id, source_lang):
        scene_num = parse_scene_number(path, chapter_id)
        if scene_num is None:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if should_chunk(text, limit):
            chunks = scene_chunks(scene_num, text, limit)
            items.append({
                "scene": scene_num,
                "chars": len(text),
                "chunks": len(chunks),
                "path": path,
            })
    return items


def find_named_image(directory: Path, stem: str) -> Path | None:
    for ext in IMAGE_EXTENSIONS:
        candidate = directory / f"{stem}{ext}"
        if candidate.is_file():
            return candidate
    return None


def count_export_illustrations(
    book: dict[str, Any],
    export_meta: dict[str, Any],
    selected_chapters: list[str],
    repo_root: Path,
) -> dict[str, int]:
    cfg = export_meta.get("illustrations", {}) or {}
    if not cfg.get("enabled", False):
        return {"chapter": 0, "scene": 0, "total": 0}
    book_root = repo_root / str(book.get("book_root", ""))
    chapter_count = 0
    scene_count = 0
    if cfg.get("chapter_images", True):
        chapter_dir = book_root / "assets" / "chapter"
        chapter_count = sum(
            1
            for chapter_id in selected_chapters
            if find_named_image(chapter_dir, f"chapter-{chapter_id}")
        )
    if cfg.get("scene_images", True):
        for chapter_id in selected_chapters:
            scene_dir = book_root / "assets" / "scene" / chapter_id
            stems: set[str] = set()
            if scene_dir.exists():
                for path in scene_dir.iterdir():
                    if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
                        if re.match(r"^scene-\d{3}$", path.stem):
                            stems.add(path.stem)
            scene_count += len(stems)
    return {
        "chapter": chapter_count,
        "scene": scene_count,
        "total": chapter_count + scene_count,
    }


def style_options(book: dict[str, Any], repo_root: Path) -> list[dict[str, Any]]:
    profiles = load_style_profiles(repo_root, book)
    if profiles:
        return profiles
    return [
        {"id": "stylized", "label": "Stylized"},
        {"id": "middle", "label": "Middle"},
        {"id": "literal", "label": "Literal"},
    ]


def book_path(book: dict[str, Any], key: str, repo_root: Path) -> Path:
    return repo_root / str(book.get(key, ""))


def names_path(book: dict[str, Any], repo_root: Path) -> Path:
    return book_path(book, "names_file", repo_root)


def editable_name_rows(book: dict[str, Any], repo_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in load_names(names_path(book, repo_root)):
        aliases = entry.get("aliases") or []
        if isinstance(aliases, list):
            aliases_text = ", ".join(str(item) for item in aliases)
        else:
            aliases_text = str(aliases)
        rows.append({
            "source": entry.get("source", ""),
            "target": entry.get("target", ""),
            "aliases": aliases_text,
            "type": entry.get("type", "person"),
            "status": entry.get("status", "draft"),
            "note": entry.get("note", ""),
        })
    rows.append({
        "source": "",
        "target": "",
        "aliases": "",
        "type": "person",
        "status": "draft",
        "note": "",
    })
    return rows


def normalize_name_rows(rows: Any) -> list[dict[str, Any]]:
    if hasattr(rows, "to_dict"):
        rows = rows.to_dict("records")
    result: list[dict[str, Any]] = []
    for row in rows:
        source = str(row.get("source") or "").strip()
        target = str(row.get("target") or "").strip()
        if not source and not target:
            continue
        aliases_text = str(row.get("aliases") or "").strip()
        aliases = [item.strip() for item in aliases_text.split(",") if item.strip()]
        result.append({
            "source": source,
            "target": target,
            "aliases": aliases,
            "type": str(row.get("type") or "person").strip(),
            "status": str(row.get("status") or "draft").strip(),
            "note": str(row.get("note") or "").strip(),
        })
    return result
