"""
Lokales Dashboard fuer die Buch-Werkbank.

Design-Referenz:
    docs/dashboard-design-system.md

Start:
    streamlit run tools/dashboard.py
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import yaml

from lib.name_registry import load_names, write_names
from lib.output_paths import (
    book_exports_root,
    book_output_root,
    de_scene_path,
    list_source_scene_paths,
    parse_scene_number,
    prompt_path,
    source_scene_path,
)
from lib.translation_chunks import (
    chunk_char_limit as resolve_chunk_char_limit,
    scene_chunks,
    should_chunk,
)
from lib.workbench_state import (
    assembly_paths,
    book_by_id,
    chapter_ids,
    chapter_rows,
    load_books,
    load_style_profiles,
    load_models,
    log_path,
    scene_counts,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
DESIGN_REFERENCE = REPO_ROOT / "docs" / "dashboard-design-system.md"
BOOK_METADATA_PROMPT = REPO_ROOT / "docs" / "book-metadata-prompt.md"
BATCH_JOB_FILE = REPO_ROOT / ".dashboard-batch-job.json"
BATCH_LOG_DIR = REPO_ROOT / "var" / "dashboard-jobs"


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def show_result(result: subprocess.CompletedProcess[str]) -> None:
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    if result.returncode == 0:
        st.success("Fertig.")
    else:
        st.error(f"Fehlercode {result.returncode}")
    if stdout.strip() or stderr.strip():
        with st.expander("Technisches Log", expanded=result.returncode != 0):
            if stdout.strip():
                st.code(stdout, language="text")
            if stderr.strip():
                st.code(stderr, language="text")


def _process_running(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
        )
        if f'"{pid}"' in (result.stdout or ""):
            return True
        # Retry once after a short pause — Windows taskkill /F may take
        # a moment to fully unregister the PID from the task list.
        import time
        time.sleep(1.0)
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
        )
        return f'"{pid}"' in (result.stdout or "")
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _job_stale(job: dict) -> bool:
    """Return True if the job file looks outdated (older than 4 hours)."""
    started = job.get("started_at") or ""
    if not started:
        return False
    try:
        started_dt = datetime.fromisoformat(started)
        return (datetime.now() - started_dt).total_seconds() > 4 * 3600
    except Exception:
        return False


def _stop_process_tree(pid: int) -> subprocess.CompletedProcess[str]:
    if os.name == "nt":
        return subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
    return subprocess.run(
        ["kill", "-TERM", str(pid)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def _load_batch_job() -> dict | None:
    if not BATCH_JOB_FILE.exists():
        return None
    try:
        return json.loads(BATCH_JOB_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


def _save_batch_job(job: dict) -> None:
    BATCH_JOB_FILE.write_text(
        json.dumps(job, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _clear_batch_job() -> None:
    if BATCH_JOB_FILE.exists():
        BATCH_JOB_FILE.unlink()


def _write_batch_job(job: dict) -> None:
    _save_batch_job(job)


def _refresh_batch_job(job: dict | None) -> tuple[dict | None, bool]:
    if not job:
        return None, False
    status = str(job.get("status") or "")
    if status in {"completed", "failed", "stopped"}:
        return job, False
    pid = int(job.get("pid") or 0)
    if _job_stale(job):
        job["status"] = "stale"
        job["completed_at"] = datetime.now().isoformat(timespec="seconds")
        _write_batch_job(job)
        return job, False
    if pid and _process_running(pid):
        job["status"] = "running"
        return job, True
    raw_log_path = str(job.get("log_path") or "")
    log_path = REPO_ROOT / raw_log_path if raw_log_path else None
    if log_path is not None and log_path.is_file():
        text = log_path.read_text(encoding="utf-8", errors="replace")
        if "Summary:" in text and job.get("returncode") is None:
            job["returncode"] = 0
        elif "Traceback" in text and job.get("returncode") is None:
            job["returncode"] = 1
    job["status"] = "completed"
    job["completed_at"] = datetime.now().isoformat(timespec="seconds")
    job["status_note"] = "Status nachtraeglich erkannt; Prozess laeuft nicht mehr."
    _write_batch_job(job)
    return job, False


def _job_status_label(job: dict, running: bool) -> str:
    if running:
        return "laeuft"
    status = str(job.get("status") or "")
    returncode = job.get("returncode")
    if status == "completed":
        if returncode is None:
            return "beendet"
        return f"beendet (Code {returncode})"
    if status == "failed":
        return f"fehlgeschlagen (Code {returncode})"
    if status == "stale":
        return "unbekannt/stale"
    if status == "stopped":
        return "gestoppt"
    return "beendet"


def _job_is_running(job: dict | None) -> bool:
    _job, running = _refresh_batch_job(job)
    return running


def _progress_from_log(text: str) -> tuple[int | None, int | None]:
    progress = None
    for match in re.finditer(r"^\[(\d+)/(\d+)\]\s+(?:Kapitel|python\b)", text, re.MULTILINE):
        progress = (int(match.group(1)), int(match.group(2)))
    return progress or (None, None)


def _latest_job_log(kind: str, book_id: str, style: str) -> Path | None:
    if not BATCH_LOG_DIR.exists():
        return None
    pattern = f"*-{kind}-{book_id}-{style}.log"
    logs = sorted(
        BATCH_LOG_DIR.glob(pattern),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return logs[0] if logs else None


def _log_completion_label(text: str) -> str:
    if "Summary:" in text:
        return "beendet"
    if "Traceback" in text or "FEHLER:" in text:
        return "fehlgeschlagen/abgebrochen"
    return "unvollstaendig"


def _show_latest_job_log(kind: str, book_id: str, style: str) -> None:
    log_path = _latest_job_log(kind, book_id, style)
    if not log_path:
        return
    text = log_path.read_text(encoding="utf-8", errors="replace")
    done, total = _progress_from_log(text)
    status = _log_completion_label(text)
    st.markdown("### Letzter Hintergrundlauf")
    st.info(
        f"Status aus Log: {status} | "
        f"{f'Fortschritt: {done}/{total} | ' if done is not None and total else ''}"
        f"Log: {log_path.relative_to(REPO_ROOT)}"
    )
    with st.expander("Letzten Log anzeigen", expanded=status != "beendet"):
        st.code("\n".join(text.splitlines()[-80:]) or "(leer)", language="text")


def _start_batch_job(
    args: list[str],
    book_id: str,
    style: str,
    provider: str,
    kind: str = "batch",
) -> dict:
    BATCH_LOG_DIR.mkdir(parents=True, exist_ok=True)
    _clear_batch_job()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = BATCH_LOG_DIR / f"{stamp}-{kind}-{book_id}-{style}.log"
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    runner_args = [
        sys.executable,
        "-u",
        "tools/dashboard_job_runner.py",
        "--repo-root", str(REPO_ROOT),
        "--job-file", str(BATCH_JOB_FILE),
        "--log-path", str(log_path),
        "--book-id", book_id,
        "--style", style,
        "--provider", provider,
        "--kind", kind,
        "--",
        sys.executable,
        *args,
    ]
    proc = subprocess.Popen(
        runner_args,
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )
    job = {
        "pid": proc.pid,
        "child_pid": None,
        "book_id": book_id,
        "style": style,
        "provider": provider,
        "kind": kind,
        "status": "running",
        "returncode": None,
        "command": [sys.executable, *args],
        "log_path": str(log_path.relative_to(REPO_ROOT)),
        "started_at": datetime.now().isoformat(timespec="seconds"),
    }
    # The runner owns the job file, including completion status. Wait briefly
    # for its initial write so fast jobs cannot be overwritten as "running".
    import time
    for _ in range(20):
        persisted = _load_batch_job()
        if persisted and int(persisted.get("pid") or 0) == proc.pid:
            return persisted
        time.sleep(0.05)
    if proc.poll() is None:
        proc.terminate()
    job["status"] = "failed"
    job["returncode"] = proc.poll()
    job["completed_at"] = datetime.now().isoformat(timespec="seconds")
    job["status_note"] = "Dashboard-Runner konnte die Jobdatei nicht initialisieren."
    _save_batch_job(job)
    return job


def _show_batch_job_panel(
    key_prefix: str = "batch-job",
    current_book_id: str | None = None,
    current_style: str | None = None,
    current_provider: str | None = None,
) -> tuple[dict | None, bool]:
    job, running = _refresh_batch_job(_load_batch_job())
    if not job:
        return None, False
    pid = int(job.get("pid") or 0)
    status = _job_status_label(job, running)
    raw_log_path = str(job.get("log_path") or "")
    log_path = REPO_ROOT / raw_log_path if raw_log_path else None
    kind = str(job.get("kind") or "batch")
    title = {
        "review": "Aktiver Review-Lauf",
        "translate": "Aktiver Uebersetzungslauf",
    }.get(kind, "Aktiver Hintergrund-Batch")
    same_context = True
    if current_book_id is not None:
        same_context = (
            str(job.get("book_id") or "") == current_book_id
            and (current_style is None or str(job.get("style") or "") == current_style)
            and (
                current_provider is None
                or str(job.get("provider") or "") == current_provider
            )
        )
    if running and not same_context:
        title = "Anderer Hintergrundlauf"
    st.markdown(
        f"""
        <div class="job-panel {'muted' if running and not same_context else ''}">
          <div>
            <div class="job-title">{title}</div>
            <div class="job-meta">
              <span>Status: {escape(status)}</span>
              <span>PID: {pid}</span>
              <span>Buch: {escape(str(job.get('book_id') or '-'))}</span>
              <span>Stil: {escape(str(job.get('style') or '-'))}</span>
              <span>Provider: {escape(str(job.get('provider') or '-'))}</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    raw_command = job.get("command") or []
    if raw_command:
        with st.expander("Kommando anzeigen", expanded=False):
            st.code(" ".join(str(part) for part in raw_command), language="text")
    if job.get("child_pid"):
        st.caption(f"Kindprozess: {job.get('child_pid')}")
    if job.get("completed_at"):
        st.caption(f"Beendet: {job.get('completed_at')}")
    if job.get("status_note"):
        st.caption(str(job.get("status_note")))
    show_live_details = same_context or not running
    if log_path is not None and log_path.is_file() and show_live_details:
        text = log_path.read_text(encoding="utf-8", errors="replace")
        done, total = _progress_from_log(text)
        if done is not None and total:
            st.progress(
                min(done / total, 1.0),
                text=f"Fortschritt: {done}/{total} Kapitel",
            )
        tail = "\n".join(text.splitlines()[-80:])
        with st.expander("Batch-Log", expanded=not running):
            st.code(tail or "(noch keine Ausgabe)", language="text")
    elif running and not same_context:
        st.caption(
            "Dieser Lauf gehoert zu einem anderen Buch/Stil. Stoppen ist moeglich; "
            "Details bleiben eingeklappt, damit der aktuelle Arbeitsbereich ruhig bleibt."
        )
    col_stop, col_clear = st.columns([1, 1])
    with col_stop:
        if st.button(
            "Hintergrund-Batch stoppen",
            disabled=not running,
            key=f"{key_prefix}-stop",
        ):
            result = _stop_process_tree(pid)
            if result.returncode == 0:
                job["status"] = "stopped"
                job["returncode"] = None
                job["completed_at"] = datetime.now().isoformat(timespec="seconds")
                _write_batch_job(job)
                st.success("Batch-Prozessbaum gestoppt.")
            else:
                st.error("Stoppen fehlgeschlagen.")
            show_result(result)
            st.rerun()
    with col_clear:
        if st.button(
            "Beendeten Lauf ausblenden",
            disabled=running,
            key=f"{key_prefix}-clear",
        ):
            _clear_batch_job()
            st.rerun()
    return job, running


def remember_result(kind: str, message: str) -> None:
    st.session_state["dashboard_last_result"] = {
        "kind": kind,
        "message": message,
    }


def show_remembered_result() -> None:
    data = st.session_state.pop("dashboard_last_result", None)
    if not data:
        return
    if data.get("kind") == "error":
        st.error(data.get("message", "Fehler."))
    else:
        st.success(data.get("message", "Fertig."))


def safe_delete_output_file(path: Path, output_root: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False
    resolved_path = path.resolve()
    resolved_root = output_root.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"Pfad liegt nicht im Output-Ordner: {path}") from exc
    path.unlink()
    return True


def delete_existing_style_outputs(
    scene_path: Path,
    prompt_file_path: Path,
    output_root: Path,
) -> list[Path]:
    deleted = []
    for path in (scene_path, prompt_file_path):
        if safe_delete_output_file(path, output_root):
            deleted.append(path)
    return deleted


def model_groups() -> dict[str, list[dict]]:
    models = load_models(REPO_ROOT)
    groups: dict[str, list[dict]] = {}
    for model in models:
        provider = model.get("provider") or "Andere"
        groups.setdefault(provider, []).append(model)
    return groups


def model_label(model: dict) -> str:
    name = model.get("name") or model.get("id", "")
    model_id = model.get("id", "")
    return f"{name} · {model_id}"


def provider_action(provider: str) -> dict[str, str]:
    actions = {
        "openrouter": {
            "title": "OpenRouter-Uebersetzung",
            "button": "Uebersetzung starten",
            "copy": (
                "Sendet die ausgewaehlten Quell-Szenen an OpenRouter und "
                "schreibt fertige deutsche Szenendateien."
            ),
            "target": "books/<id>/work/scenes/de/<style>/<Kapitel>/scene-XX.md",
        },
        "ollama": {
            "title": "Ollama-Uebersetzung",
            "button": "Uebersetzung starten",
            "copy": (
                "Sendet die ausgewaehlten Quell-Szenen an das lokale "
                "Ollama-Modell und schreibt fertige deutsche Szenendateien."
            ),
            "target": "books/<id>/work/scenes/de/<style>/<Kapitel>/scene-XX.md",
        },
        "prompt_file": {
            "title": "Prompt-Datei bauen",
            "button": "Prompt-Datei bauen",
            "copy": (
                "Baut den vollstaendigen System- und User-Prompt, ohne "
                "einen KI-Call auszufuehren."
            ),
            "target": "books/<id>/work/prompts/<Kapitel>-scene-XX-<style>.md",
        },
        "workspace_ai": {
            "title": "Workspace-Auftrag bauen",
            "button": "Workspace-Auftrag bauen",
            "copy": (
                "Schreibt eine Arbeitsanweisung fuer eine KI, die dieses "
                "Repo direkt im Editor geoeffnet hat."
            ),
            "target": "books/<id>/work/prompts/<Kapitel>-scene-XX-<style>.md",
        },
    }
    return actions.get(provider, actions["openrouter"])


def latest_export_files(book: dict, style: str, repo_root: Path) -> list[Path]:
    export_root = book_exports_root(repo_root, book) / style
    if not export_root.exists():
        return []
    paths = []
    for pattern in (
        "chapter/docx/*.docx",
        "chapter/epub/*.epub",
        "book/docx/*.docx",
        "book/epub/*.epub",
        # Legacy layout from early exporter versions. Keep reading it,
        # but write new exports into the scoped folders above.
        "docx/*.docx",
        "epub/*.epub",
    ):
        paths.extend(export_root.glob(pattern))
    return sorted(paths, key=lambda path: path.stat().st_mtime, reverse=True)


def exportable_style_rows(book: dict, styles: list[dict], chapter: str, repo_root: Path) -> list[dict]:
    rows: list[dict] = []
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


def load_export_meta(book: dict) -> dict:
    path = REPO_ROOT / str(book.get("export_config", ""))
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


def load_pipeline_config() -> dict:
    path = REPO_ROOT / "config" / "pipeline.yaml"
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def oversized_source_scenes(
    book: dict,
    chapter_id: str,
    limit: int,
    repo_root: Path,
) -> list[dict]:
    if not chapter_id or limit <= 0:
        return []
    output_root = book_output_root(repo_root, book)
    source_lang = str(book.get("source_lang") or "ru")
    items = []
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


IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


def find_named_image(directory: Path, stem: str) -> Path | None:
    for ext in IMAGE_EXTENSIONS:
        candidate = directory / f"{stem}{ext}"
        if candidate.is_file():
            return candidate
    return None


def count_export_illustrations(
    book: dict,
    export_meta: dict,
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


def unregistered_sources(repo_root: Path, books: list[dict]) -> list[Path]:
    registered = {
        (repo_root / str(book.get("source_path", ""))).resolve()
        for book in books
        if book.get("source_path")
    }
    candidates: list[Path] = []
    books_dir = repo_root / "books"
    for pattern in ("*.rtf", "*.doc", "*.txt", "*.md"):
        candidates.extend(books_dir.glob(pattern))
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


def style_options(book: dict) -> list[dict]:
    profiles = load_style_profiles(REPO_ROOT, book)
    if profiles:
        return profiles
    return [
        {"id": "stylized", "label": "Stylized"},
        {"id": "middle", "label": "Middle"},
        {"id": "literal", "label": "Literal"},
    ]


def book_path(book: dict, key: str) -> Path:
    return REPO_ROOT / str(book.get(key, ""))


def names_path(book: dict) -> Path:
    return book_path(book, "names_file")


def editable_name_rows(book: dict) -> list[dict]:
    rows = []
    for entry in load_names(names_path(book)):
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


def normalize_name_rows(rows: list[dict]) -> list[dict]:
    if hasattr(rows, "to_dict"):
        rows = rows.to_dict("records")
    result = []
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


def render_soft_table(rows: list[dict], empty_label: str = "Keine Daten vorhanden.") -> None:
    if not rows:
        st.info(empty_label)
        return
    headers = list(rows[0].keys())
    head = "".join(f"<th>{escape(str(header))}</th>" for header in headers)
    body_parts = []
    for row in rows:
        cells = "".join(
            f"<td>{escape(str(row.get(header, '')))}</td>"
            for header in headers
        )
        body_parts.append(f"<tr>{cells}</tr>")
    st.markdown(
        f"""
        <div class="soft-table-wrap">
          <table class="soft-table">
            <thead><tr>{head}</tr></thead>
            <tbody>{"".join(body_parts)}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_design_system_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

        :root {
            --background: hsl(230 25% 97%);
            --foreground: hsl(230 25% 15%);
            --card: hsl(0 0% 100%);
            --primary: hsl(28 95% 55%);
            --primary-foreground: hsl(0 0% 100%);
            --secondary: hsl(28 30% 95%);
            --secondary-foreground: hsl(28 50% 35%);
            --muted: hsl(230 20% 93%);
            --muted-foreground: hsl(230 15% 50%);
            --border: hsl(230 20% 90%);
            --input: hsl(230 20% 90%);
            --ring: hsl(28 95% 55%);
            --shadow-card: 0 2px 12px -2px hsl(230 25% 15% / 0.06);
            --shadow-card-hover: 0 8px 24px -4px hsl(28 95% 55% / 0.2);
            --radius: 16px;
        }

        html, body, [class*="css"], .stApp {
            font-family: "Plus Jakarta Sans", system-ui, -apple-system,
                BlinkMacSystemFont, "Segoe UI", sans-serif;
            -webkit-font-smoothing: antialiased;
        }

        .stApp {
            background: var(--background);
            color: var(--foreground);
        }

        .block-container {
            max-width: none;
            padding-top: 30px;
            padding-left: 32px;
            padding-right: 32px;
            padding-bottom: 48px;
        }

        [data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, hsl(0 0% 100% / 0.84), hsl(230 25% 97% / 0.78));
            border-right: 1px solid hsl(230 20% 90% / 0.72);
            box-shadow: 14px 0 42px -28px hsl(230 25% 15% / 0.32);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            width: 300px !important;
        }

        [data-testid="stSidebar"] > div:first-child {
            padding: 22px 16px 18px;
        }

        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
        [data-testid="stSidebar"] label {
            color: var(--muted-foreground);
            font-size: 12px;
            font-weight: 600;
        }

        .sidebar-brand {
            margin: 0 0 14px;
            padding: 16px 16px 14px;
            border-radius: var(--radius);
            background:
                linear-gradient(135deg, hsl(28 95% 55%), hsl(35 90% 60%));
            color: white;
            box-shadow: 0 8px 24px -4px hsl(28 95% 55% / 0.26);
        }

        .sidebar-brand .eyebrow {
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            opacity: 0.82;
            margin-bottom: 5px;
        }

        .sidebar-brand .title {
            font-size: 21px;
            font-weight: 800;
            line-height: 1.1;
            color: white;
        }

        .sidebar-brand .subtitle {
            margin-top: 8px;
            font-size: 11px;
            font-weight: 500;
            opacity: 0.86;
            color: white;
        }

        .sidebar-section-title {
            margin: 14px 0 7px;
            color: var(--muted-foreground);
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .sidebar-meta {
            display: grid;
            gap: 4px;
            margin: 8px 0 10px;
            padding: 10px 12px;
            border: 1px solid hsl(230 20% 90% / 0.7);
            border-radius: 14px;
            background: hsl(0 0% 100% / 0.58);
        }

        .sidebar-meta div {
            color: var(--muted-foreground);
            font-size: 11px;
            font-weight: 600;
            line-height: 1.35;
            overflow-wrap: anywhere;
        }

        .sidebar-meta b {
            color: var(--foreground);
            font-weight: 800;
        }

        .app-topbar {
            position: sticky;
            top: 12px;
            z-index: 20;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
            margin: 0 0 22px;
            padding: 16px 20px;
            border: 1px solid hsl(230 20% 90% / 0.72);
            border-radius: var(--radius);
            background: hsl(0 0% 100% / 0.88);
            box-shadow: 0 14px 40px -28px hsl(230 25% 15% / 0.38);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
        }

        .app-title {
            color: var(--foreground);
            font-size: 23px;
            font-weight: 800;
            line-height: 1.18;
        }

        .app-subtitle {
            margin-top: 4px;
            color: var(--muted-foreground);
            font-size: 13px;
            font-weight: 500;
        }

        .topbar-meta {
            display: flex;
            flex-wrap: wrap;
            justify-content: flex-end;
            gap: 8px;
        }

        .topbar-chip {
            display: inline-flex;
            align-items: center;
            min-height: 30px;
            padding: 5px 10px;
            border: 1px solid hsl(230 20% 90% / 0.74);
            border-radius: 999px;
            background: hsl(230 25% 98% / 0.86);
            color: var(--muted-foreground);
            font-size: 12px;
            font-weight: 700;
            white-space: nowrap;
        }

        .topbar-chip.accent {
            border-color: hsl(28 95% 55% / 0.22);
            background: hsl(28 30% 95%);
            color: var(--secondary-foreground);
        }

        .hero-strip {
            margin: 0 0 18px;
            padding: 18px 22px;
            border: 1px solid hsl(28 95% 55% / 0.18);
            border-radius: var(--radius);
            background:
                linear-gradient(145deg, hsl(0 0% 100%), hsl(28 30% 97%));
            box-shadow: var(--shadow-card);
        }

        .hero-strip .kicker {
            display: inline-flex;
            align-items: center;
            padding: 3px 10px;
            border-radius: 999px;
            background: var(--secondary);
            color: var(--secondary-foreground);
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .hero-strip .copy {
            color: var(--muted-foreground);
            font-size: 14px;
            margin-top: 4px;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 2px 10px;
            background: var(--secondary);
            color: var(--secondary-foreground);
            font-size: 12px;
            font-weight: 700;
            margin: 0 6px 8px 0;
        }

        .job-panel {
            margin: 12px 0 10px;
            padding: 14px 16px;
            border: 1px solid hsl(28 95% 55% / 0.18);
            border-radius: 16px;
            background: linear-gradient(145deg, hsl(0 0% 100%), hsl(28 30% 98%));
            box-shadow: var(--shadow-card);
        }

        .job-panel.muted {
            border-color: hsl(230 20% 90% / 0.82);
            background: hsl(0 0% 100% / 0.76);
            box-shadow: 0 10px 26px -24px hsl(230 25% 15% / 0.34);
        }

        .job-panel.muted .job-title {
            font-size: 16px;
        }

        .job-title {
            color: var(--foreground);
            font-size: 18px;
            font-weight: 800;
            line-height: 1.25;
        }

        .job-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 7px;
            margin-top: 9px;
        }

        .job-meta span {
            display: inline-flex;
            align-items: center;
            min-height: 26px;
            padding: 4px 9px;
            border-radius: 999px;
            background: hsl(28 30% 95%);
            color: var(--secondary-foreground);
            font-size: 11px;
            font-weight: 700;
        }

        .workflow-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 16px;
            margin: 14px 0 18px;
        }

        .workflow-card {
            min-height: 190px;
            padding: 18px;
            border: 1px solid var(--border);
            border-radius: var(--radius);
            background: linear-gradient(145deg, hsl(0 0% 100%), hsl(230 25% 98%));
            box-shadow: var(--shadow-card);
        }

        .workflow-card:hover {
            border-color: hsl(28 95% 55% / 0.28);
            box-shadow: var(--shadow-card-hover);
            transition: all 300ms ease;
        }

        .workflow-step {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 28px;
            height: 28px;
            border-radius: 999px;
            margin-bottom: 10px;
            background: var(--secondary);
            color: var(--secondary-foreground);
            font-size: 12px;
            font-weight: 800;
        }

        .workflow-title {
            color: var(--foreground);
            font-size: 17px;
            font-weight: 700;
            margin-bottom: 6px;
        }

        .workflow-copy {
            color: var(--muted-foreground);
            font-size: 13px;
            line-height: 1.55;
        }

        .path-pill {
            display: inline-flex;
            max-width: 100%;
            margin-top: 10px;
            padding: 5px 9px;
            border-radius: 999px;
            background: var(--muted);
            color: var(--muted-foreground);
            font-size: 11px;
            font-weight: 600;
            overflow-wrap: anywhere;
        }

        .workflow-card.accent {
            border-color: hsl(28 95% 55% / 0.34);
            background:
                linear-gradient(145deg, hsl(28 30% 97%), hsl(0 0% 100%));
        }

        .tool-panel {
            min-height: 178px;
            padding: 20px;
            border: 1px solid var(--border);
            border-radius: var(--radius);
            background: var(--card);
            box-shadow: var(--shadow-card);
            margin-bottom: 12px;
        }

        .tool-panel strong {
            display: block;
            color: var(--foreground);
            font-size: 17px;
            font-weight: 700;
            margin-bottom: 6px;
        }

        .tool-panel span {
            display: block;
            color: var(--muted-foreground);
            font-size: 13px;
            line-height: 1.55;
        }

        .mini-list {
            display: grid;
            gap: 8px;
            margin: 12px 0 4px;
        }

        .mini-list div {
            padding: 9px 11px;
            border: 1px solid var(--border);
            border-radius: 12px;
            background: hsl(230 20% 98%);
            color: var(--muted-foreground);
            font-size: 13px;
            font-weight: 500;
        }

        .section-heading {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin: 22px 0 10px;
        }

        .section-heading h3 {
            margin: 0;
            font-size: 18px;
            font-weight: 800;
        }

        .section-heading span {
            color: var(--muted-foreground);
            font-size: 12px;
            font-weight: 600;
        }

        .soft-table-wrap {
            max-height: 460px;
            overflow: auto;
            padding: 14px 16px;
            border: 1px solid hsl(230 20% 90% / 0.72);
            border-radius: 16px;
            background: var(--card);
            box-shadow: 0 16px 40px -30px hsl(230 25% 15% / 0.42);
        }

        .soft-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            color: var(--foreground);
            font-size: 13px;
            line-height: 1.5;
        }

        .soft-table,
        .soft-table tr,
        .soft-table th,
        .soft-table td {
            border-left: 0 !important;
            border-right: 0 !important;
            border-bottom: 0 !important;
        }

        .soft-table th {
            position: sticky;
            top: 0;
            z-index: 1;
            padding: 11px 10px;
            background: hsl(0 0% 100% / 0.96);
            color: var(--muted-foreground) !important;
            font-size: 12px;
            font-weight: 700;
            text-align: left;
        }

        .soft-table td {
            padding: 13px 10px;
            border-top: 1px solid hsl(230 20% 90% / 0.58) !important;
            color: var(--foreground) !important;
            font-weight: 500;
            vertical-align: top;
        }

        .soft-table tbody tr:hover td {
            background: hsl(28 30% 97% / 0.56);
        }

        .export-grid {
            display: grid;
            grid-template-columns: minmax(0, 1.1fr) minmax(280px, 0.9fr);
            gap: 18px;
            margin: 14px 0 18px;
        }

        .export-card {
            padding: 24px;
            border: 1px solid hsl(230 20% 90% / 0.72);
            border-radius: 16px;
            background: linear-gradient(145deg, hsl(0 0% 100%), hsl(230 25% 98%));
            box-shadow: 0 16px 40px -30px hsl(230 25% 15% / 0.42);
        }

        .export-card h3 {
            margin-top: 0;
            margin-bottom: 8px;
            font-size: 20px;
            font-weight: 800;
        }

        .export-card p {
            color: var(--muted-foreground);
            font-size: 14px;
            line-height: 1.55;
        }

        .output-list {
            display: grid;
            gap: 10px;
            margin-top: 16px;
        }

        .output-item,
        .config-row {
            display: grid;
            grid-template-columns: 34px minmax(120px, 0.8fr) minmax(0, 1.2fr);
            align-items: center;
            gap: 12px;
            min-height: 48px;
            padding: 9px 0;
            border-bottom: 1px solid hsl(230 20% 90% / 0.62);
        }

        .output-item:last-child,
        .config-row:last-child {
            border-bottom: 0;
        }

        .output-item strong,
        .config-row b {
            color: var(--foreground);
            font-size: 13px;
            font-weight: 800;
        }

        .output-item span:last-child,
        .config-row span:last-child {
            color: var(--muted-foreground);
            font-size: 12px;
            font-weight: 600;
            line-height: 1.45;
            overflow-wrap: anywhere;
        }

        .config-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            border-radius: 12px;
            background: hsl(28 30% 95%);
            color: var(--primary);
        }

        .config-icon svg {
            width: 17px;
            height: 17px;
            stroke: currentColor;
            stroke-width: 2;
            fill: none;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        .config-row {
            color: var(--muted-foreground);
        }

        @media (max-width: 900px) {
            .workflow-grid {
                grid-template-columns: 1fr;
            }

            .export-grid {
                grid-template-columns: 1fr;
            }
        }

        h1, h2, h3 {
            color: var(--foreground);
            letter-spacing: 0;
        }

        h1 {
            font-size: 34px;
            font-weight: 800;
            margin-bottom: 4px;
        }

        h2 {
            font-size: 24px;
            font-weight: 700;
        }

        h3 {
            font-size: 20px;
            font-weight: 600;
        }

        [data-testid="stMetric"],
        [data-testid="stDataFrame"],
        .stTextArea,
        .stCodeBlock,
        [data-testid="stExpander"],
        [data-testid="stAlert"] {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            box-shadow: var(--shadow-card);
            padding: 14px;
        }

        [data-testid="stMetric"]:hover,
        [data-testid="stDataFrame"]:hover {
            border-color: hsl(28 95% 55% / 0.3);
            box-shadow: var(--shadow-card-hover);
            transition: all 300ms ease;
        }

        [data-testid="stMetricLabel"] p {
            color: var(--muted-foreground);
            font-size: 12px;
            font-weight: 600;
        }

        [data-testid="stMetricValue"] {
            color: var(--foreground);
            font-weight: 800;
        }

        .stButton > button {
            min-height: 40px;
            border-radius: 999px;
            border: 1px solid hsl(230 20% 90% / 0.95);
            background: hsl(0 0% 100%);
            color: var(--foreground);
            font-size: 14px;
            font-weight: 600;
            transition: all 200ms ease;
            box-shadow: 0 8px 18px -16px hsl(230 25% 15% / 0.32);
        }

        .stButton > button:hover {
            border-color: hsl(28 95% 55% / 0.36);
            color: var(--primary);
            box-shadow: 0 10px 24px -18px hsl(28 95% 55% / 0.5);
        }

        .stButton > button[kind="primary"],
        [data-testid="baseButton-primary"] {
            border-color: hsl(28 95% 55% / 0.3) !important;
            background: linear-gradient(135deg, hsl(28 95% 55%), hsl(35 90% 60%)) !important;
            color: var(--primary-foreground) !important;
            box-shadow: 0 12px 26px -14px hsl(28 95% 55% / 0.72) !important;
        }

        .stButton > button[kind="primary"]:hover,
        [data-testid="baseButton-primary"]:hover {
            color: var(--primary-foreground) !important;
            filter: brightness(0.98);
        }

        [data-baseweb="select"] > div {
            background: var(--card);
            border-color: var(--input);
            box-shadow: 0 1px 8px -4px hsl(230 25% 15% / 0.2);
        }

        [data-baseweb="select"] > div:focus-within {
            border-color: var(--ring);
            box-shadow: 0 0 0 2px hsl(28 95% 55% / 0.18);
        }

        [data-testid="stRadio"] [role="radiogroup"] {
            gap: 8px;
        }

        [data-testid="stRadio"] label {
            padding: 7px 11px;
            border-radius: 999px;
            background: hsl(0 0% 100% / 0.76);
            border: 1px solid hsl(230 20% 90% / 0.72);
            color: var(--foreground);
            font-weight: 650;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"]:first-of-type [role="radiogroup"] {
            display: grid;
            gap: 3px;
            padding: 6px;
            border: 1px solid hsl(230 20% 90% / 0.72);
            border-radius: 16px;
            background: hsl(0 0% 100% / 0.58);
            box-shadow: 0 10px 28px -26px hsl(230 25% 15% / 0.35);
        }

        [data-testid="stSidebar"] [data-testid="stRadio"]:first-of-type label {
            width: 100%;
            min-height: 36px;
            margin: 0;
            padding: 8px 10px;
            border: 0;
            border-radius: 11px;
            background: transparent;
            color: var(--muted-foreground);
            box-shadow: none;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"]:first-of-type label:hover {
            background: hsl(230 20% 96%);
            color: var(--foreground);
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
            border-color: hsl(28 95% 55% / 0.32);
            background: hsl(28 30% 95%);
            color: var(--primary);
            box-shadow: 0 8px 18px -16px hsl(28 95% 55% / 0.7);
        }

        [data-testid="stSidebar"] [data-testid="stRadio"]:first-of-type label:has(input:checked) {
            border: 0;
            background: hsl(28 95% 55% / 0.1);
            color: var(--primary);
            box-shadow: inset 3px 0 0 hsl(28 95% 55%);
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child {
            display: none;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"]:first-of-type label p {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin: 0;
            font-weight: 700;
            font-size: 12px;
            line-height: 1.2;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"]:first-of-type label p::before {
            content: "";
            width: 16px;
            height: 16px;
            flex: 0 0 16px;
            background: currentColor;
            opacity: 0.86;
            -webkit-mask: var(--nav-icon) center / contain no-repeat;
            mask: var(--nav-icon) center / contain no-repeat;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"]:first-of-type label:nth-of-type(1) p {
            --nav-icon: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='3' width='7' height='7'/%3E%3Crect x='14' y='3' width='7' height='7'/%3E%3Crect x='14' y='14' width='7' height='7'/%3E%3Crect x='3' y='14' width='7' height='7'/%3E%3C/svg%3E");
        }

        [data-testid="stSidebar"] [data-testid="stRadio"]:first-of-type label:nth-of-type(2) p {
            --nav-icon: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 3v18'/%3E%3Cpath d='M3 7h18'/%3E%3Cpath d='M3 17h18'/%3E%3C/svg%3E");
        }

        [data-testid="stSidebar"] [data-testid="stRadio"]:first-of-type label:nth-of-type(3) p {
            --nav-icon: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M16 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V8z'/%3E%3Cpath d='M16 3v5h5'/%3E%3Cpath d='M8 13h8'/%3E%3Cpath d='M8 17h5'/%3E%3C/svg%3E");
        }

        [data-testid="stSidebar"] [data-testid="stRadio"]:first-of-type label:nth-of-type(4) p {
            --nav-icon: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m5 8 6 6'/%3E%3Cpath d='m4 14 6-6 2-3 7 7-3 2-6 6z'/%3E%3C/svg%3E");
        }

        [data-testid="stSidebar"] [data-testid="stRadio"]:first-of-type label:nth-of-type(5) p {
            --nav-icon: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 3v18'/%3E%3Cpath d='m17 8-5-5-5 5'/%3E%3Cpath d='m17 16-5 5-5-5'/%3E%3C/svg%3E");
        }

        [data-testid="stSidebar"] [data-testid="stRadio"]:first-of-type label:nth-of-type(6) p {
            --nav-icon: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 6h18'/%3E%3Cpath d='M7 12h14'/%3E%3Cpath d='M3 18h18'/%3E%3C/svg%3E");
        }

        [data-testid="stSidebar"] [data-testid="stRadio"]:first-of-type label:nth-of-type(7) p {
            --nav-icon: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M9 11 12 14 22 4'/%3E%3Cpath d='M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11'/%3E%3C/svg%3E");
        }

        [data-testid="stSidebar"] [data-testid="stRadio"]:first-of-type label:nth-of-type(8) p {
            --nav-icon: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'/%3E%3Cpath d='M7 10l5 5 5-5'/%3E%3Cpath d='M12 15V3'/%3E%3C/svg%3E");
        }

        [data-testid="stSidebar"] [data-testid="stRadio"]:first-of-type label:nth-of-type(9) p {
            --nav-icon: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/%3E%3Cpath d='M14 2v6h6'/%3E%3Cpath d='M8 13h8'/%3E%3Cpath d='M8 17h8'/%3E%3C/svg%3E");
        }

        [data-testid="stCheckbox"] label {
            line-height: 1.45;
        }

        @media (max-width: 700px) {
            .block-container {
                padding-left: 16px;
                padding-right: 16px;
                padding-top: 52px;
            }

            .app-topbar {
                position: relative;
                top: auto;
                align-items: flex-start;
                flex-direction: column;
            }

            .topbar-meta {
                justify-content: flex-start;
            }

            .output-item,
            .config-row {
                grid-template-columns: 34px minmax(0, 1fr);
            }

            .output-item span:last-child,
            .config-row span:last-child {
                grid-column: 2;
            }
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background: var(--muted);
            border-radius: 8px;
            padding: 4px;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            color: var(--muted-foreground);
            font-weight: 600;
            padding: 8px 14px;
        }

        .stTabs [aria-selected="true"] {
            background: var(--card);
            color: var(--foreground);
            box-shadow: var(--shadow-card);
        }

        [data-baseweb="select"] > div,
        [data-baseweb="radio"] label,
        [data-testid="stCheckbox"] label {
            border-radius: 8px;
        }

        .stCaptionContainer,
        .stMarkdown p {
            color: var(--muted-foreground);
        }

        textarea {
            border-radius: 12px !important;
            border-color: var(--border) !important;
            background: linear-gradient(145deg, hsl(0 0% 100%), hsl(230 25% 98%));
            font-family: "Plus Jakarta Sans", system-ui, sans-serif;
            line-height: 1.6;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="Buch-Werkbank", layout="wide")
apply_design_system_css()

books = load_books(REPO_ROOT)
book_ids = [b["id"] for b in books]
st.sidebar.markdown(
    """
    <div class="sidebar-brand">
      <div class="eyebrow">Produktion</div>
      <div class="title">Buch-Werkbank</div>
      <div class="subtitle">Style-Profile, Szenen, Assemblies und Exporte</div>
    </div>
    """,
    unsafe_allow_html=True,
)
nav_options = [
    "Uebersicht",
    "Buch-Setup",
    "Namen",
    "Uebersetzen",
    "Stiltest",
    "Versionen",
    "Review",
    "Export",
    "Logs",
]
st.sidebar.markdown('<div class="sidebar-section-title">Navigation</div>', unsafe_allow_html=True)
section = st.sidebar.radio(
    "Navigation",
    nav_options,
    label_visibility="collapsed",
)
st.sidebar.markdown('<div class="sidebar-section-title">Projekt</div>', unsafe_allow_html=True)
book_id = st.sidebar.selectbox("Buch", book_ids)
book = book_by_id(book_id, REPO_ROOT)
source_lang = str(book.get("source_lang") or "ru")
source_lang_label = source_lang.upper()
pipeline_cfg = load_pipeline_config()
default_chunk_limit = resolve_chunk_char_limit(book, pipeline_cfg)
structure = book.get("structure") or {}
structure_mode = str(structure.get("mode") or "scenes")
chapter_as_scene = structure_mode == "chapter_as_scene"
unit_label = "Kapitel" if chapter_as_scene else "Szenen"
st.sidebar.markdown(
    f"""
    <div class="sidebar-meta">
      <div><b>Aktiv</b> {book.get('title', book_id)}</div>
      <div><b>Sprache</b> {source_lang_label} -> {str(book.get('target_lang') or 'de').upper()}</div>
      <div><b>Struktur</b> {structure.get('label') or structure_mode}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
style_default = book.get("style_mode", "stylized")
styles = style_options(book)
style_ids = [s["id"] for s in styles]
style_labels = {s["id"]: s.get("label", s["id"]) for s in styles}
style = st.sidebar.selectbox(
    "Stil",
    style_ids,
    index=style_ids.index(style_default) if style_default in style_ids else 0,
    format_func=lambda value: style_labels.get(value, value),
)

chapters = chapter_ids(book, REPO_ROOT)
if chapters:
    chapter = st.sidebar.selectbox("Kapitel", chapters)
    counts = scene_counts(book, chapter, style, REPO_ROOT)
else:
    chapter = ""
    st.sidebar.warning("Noch keine Kapitel. Im Tab Buch-Setup Quellen erzeugen.")
    counts = {
        "ru": 0,
        "de": 0,
        "missing": [],
        "next_missing": None,
        "complete": False,
    }

models_by_provider = model_groups()
default_model = (book.get("ai") or {}).get("model")
provider_names = list(models_by_provider.keys())
default_model_group = provider_names[0] if provider_names else "Andere"
for provider_name, provider_models in models_by_provider.items():
    if any(item.get("id") == default_model for item in provider_models):
        default_model_group = provider_name
        break
with st.sidebar.expander("KI & Provider", expanded=False):
    model_provider_group = st.selectbox(
        "Modellgruppe",
        provider_names,
        index=provider_names.index(default_model_group) if provider_names else 0,
    )
    provider_models = models_by_provider.get(model_provider_group, [])
    model_ids = [item["id"] for item in provider_models]
    model_labels = {item["id"]: model_label(item) for item in provider_models}
    model_index = (
        model_ids.index(default_model)
        if default_model in model_ids
        else 0
    )
    model = st.selectbox(
        "OpenRouter-Modell",
        model_ids,
        index=model_index,
        format_func=lambda value: model_labels.get(value, value),
    )

    provider = st.radio(
        "Provider",
        ["openrouter", "ollama", "prompt_file", "workspace_ai"],
        horizontal=True,
    )
    ollama_model = st.session_state.get("ollama_model", "qwen3:8b")
    if provider == "ollama":
        ollama_model = st.selectbox(
            "Ollama-Modell",
            ["qwen3:8b", "gemma4:latest"],
            index=0 if ollama_model not in ("qwen3:8b", "gemma4:latest") else
                  ["qwen3:8b", "gemma4:latest"].index(ollama_model),
            help="Lokales Ollama-Modell. qwen3:8b wird empfohlen.",
        )
        st.session_state["ollama_model"] = ollama_model
style_label = style_labels.get(style, style)
model_display = model if provider != "ollama" else f"Ollama · {ollama_model}"
provider_display = {"openrouter": "OpenRouter", "ollama": "Ollama lokal", "prompt_file": "Prompt-Datei", "workspace_ai": "Workspace-KI"}.get(provider, provider)
st.sidebar.markdown(
    f"""
    <div class="sidebar-meta">
      <div><b>Stil</b> {style_label}</div>
      <div><b>Provider</b> {provider_display}</div>
      <div><b>Modell</b> {model_display}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="app-topbar">
      <div>
        <div class="app-title">Buch-Werkbank: {book.get("title", book_id)}</div>
        <div class="app-subtitle">
          {section} fuer {source_lang_label} -> {str(book.get("target_lang") or "de").upper()}
        </div>
      </div>
      <div class="topbar-meta">
        <span class="topbar-chip accent">{style_label}</span>
        <span class="topbar-chip">{provider}</span>
        <span class="topbar-chip">{chapter or "kein Kapitel"}</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

chunk_limit_input = default_chunk_limit

if section == "Uebersicht":
    st.subheader(book["title"])
    output_root = book_output_root(REPO_ROOT, book)
    st.caption(str(output_root.relative_to(REPO_ROOT)))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"{source_lang_label}-{unit_label}", counts["ru"])
    c2.metric(f"DE-{unit_label}", counts["de"])
    c3.metric("Fehlend", len(counts["missing"]))
    c4.metric("Naechste Einheit", counts["next_missing"] or "-")

    st.markdown(
        """
        <div class="section-heading">
          <h3>Kapitelstatus</h3>
          <span>Status je Arbeitseinheit</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    rows = chapter_rows(book, style, REPO_ROOT)
    display_rows = []
    for row in rows:
        display_row = dict(row)
        display_row[f"Titel {source_lang_label}"] = display_row.pop("Titel RU", "")
        display_row[f"{source_lang_label}"] = display_row.pop("RU", 0)
        display_rows.append(display_row)
    render_soft_table(display_rows)

if section == "Buch-Setup":
    st.markdown(
        """
        <div class="hero-strip">
          <div class="kicker">Buch-Setup</div>
          <h2>Neues Buch registrieren und Struktur vorbereiten</h2>
          <div class="copy">
            Jedes Buch ist ein eigenes Paket unter books/&lt;id&gt;/. Quelle,
            Config, Cover, Arbeitsdaten, Exporte, Status und Logs liegen dort.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    unregistered = unregistered_sources(REPO_ROOT, books)
    col_new, col_current = st.columns([1, 1])
    with col_new:
        st.markdown(
            """
            <div class="tool-panel">
              <strong>1. Neue Quelle registrieren</strong>
              <span>
                Registriert eine Quelldatei als Buchpaket. Die Datei wird in
                books/&lt;id&gt;/source/ abgelegt und die noetigen Unterordner
                werden vorbereitet.
              </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not unregistered:
            st.info("Keine losen Quelldateien direkt unter books/ gefunden.")
        else:
            source_options = [str(path.relative_to(REPO_ROOT)) for path in unregistered]
            source_choice = st.selectbox("Unregistrierte Quelle", source_options)
            source_path = REPO_ROOT / source_choice
            guessed_title, guessed_author = guess_title_author(source_path)
            new_title = st.text_input("Titel", value=guessed_title)
            new_author = st.text_input("Autor", value=guessed_author)
            new_style = st.selectbox(
                "Start-Stil",
                style_ids,
                index=style_ids.index("stil-01-original")
                if "stil-01-original" in style_ids else 0,
                format_func=lambda value: style_labels.get(value, value),
                key="setup-new-style",
            )
            source_lang = st.text_input("Quellsprache", value="ru")
            target_lang = st.text_input("Zielsprache", value="de")
            use_rules = st.checkbox("Regelwerk fuer dieses Buch aktivieren", value=False)
            if st.button("Buch registrieren"):
                cmd = [
                    "tools/init_book.py",
                    "--source", source_choice,
                    "--title", new_title,
                    "--author", new_author,
                    "--style", new_style,
                    "--source-lang", source_lang,
                    "--target-lang", target_lang,
                ]
                cmd.append("--ruleset-apply" if use_rules else "--no-ruleset-apply")
                show_result(run_command(cmd))
                st.info("Nach dem Registrieren die Seite neu laden, damit das Buch in der Sidebar erscheint.")

        if BOOK_METADATA_PROMPT.exists():
            prompt_text = BOOK_METADATA_PROMPT.read_text(encoding="utf-8")
            st.markdown(
                """
                <div class="tool-panel">
                  <strong>Metadaten-Prompt fuer fremde KI</strong>
                  <span>
                    Diesen Prompt kannst du mit Titel/Quelle in eine andere KI
                    geben. Die Antwort liefert Felder fuer book.yaml,
                    export.yaml und names.yaml.
                  </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.text_area(
                "Prompt-Vorlage",
                prompt_text,
                height=360,
                help="Inhalt aus docs/book-metadata-prompt.md",
            )

    with col_current:
        st.markdown(
            f"""
            <div class="tool-panel">
              <strong>2. Aktuelles Buch vorbereiten</strong>
              <span>
                Zeigt die aktiven Paketpfade und erzeugt bei Bedarf die
                Kapitelquellen aus der Quelle dieses Buchpakets.
              </span>
              <div class="mini-list">
                <div>Buch: {book.get("title", book_id)}</div>
                <div>Quelle: {book.get("source_path", "")}</div>
                <div>Work: {book.get("work_dir", "")}</div>
                <div>Exporte: {book.get("exports_dir", "")}</div>
                <div>Chunk-Grenze: {default_chunk_limit:,} Zeichen</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(
            "Grosse Quell-Szenen werden beim Uebersetzen intern in Chunks "
            "verarbeitet. Die sichtbare Szenenstruktur bleibt unveraendert."
        )
        if st.button("Quell-Kapitel erzeugen"):
            show_result(run_command([
                "tools/extract_chapters.py",
                "--book", book_id,
            ]))
            st.info("Danach ggf. Seite neu laden und im Uebersetzen-Tab Quell-Szenen extrahieren.")

if section == "Namen":
    st.markdown(
        f"""
        <div class="hero-strip">
          <div class="kicker">Namen und Begriffe</div>
          <h2>Namenliste fuer {book.get("title", book_id)}</h2>
          <div class="copy">
            Diese Liste wird kompakt in jeden Prompt eingefuegt. Nicht
            gepflegte russische Namen werden konservativ transliteriert oder
            im Zweifel beibehalten.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    npath = names_path(book)
    st.caption(str(npath.relative_to(REPO_ROOT)))
    rows = editable_name_rows(book)
    edited_rows = st.data_editor(
        rows,
        width="stretch",
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "source": st.column_config.TextColumn("Original"),
            "target": st.column_config.TextColumn("Deutsch"),
            "aliases": st.column_config.TextColumn("Alias/Koseformen"),
            "type": st.column_config.SelectboxColumn(
                "Typ",
                options=["person", "place", "term", "title", "nickname"],
            ),
            "status": st.column_config.SelectboxColumn(
                "Status",
                options=["approved", "draft", "review"],
            ),
            "note": st.column_config.TextColumn("Notiz"),
        },
        key=f"names-editor-{book_id}",
    )
    normalized_names = normalize_name_rows(edited_rows)
    candidates = [
        row for row in normalized_names
        if row.get("status") in ("draft", "review") or not row.get("target")
    ]
    c1, c2, c3 = st.columns(3)
    c1.metric("Eintraege", len(normalized_names))
    c2.metric("Kandidaten", len(candidates))
    c3.metric("Approved", sum(1 for row in normalized_names if row.get("status") == "approved"))
    if candidates:
        st.info(
            "Offen: "
            + ", ".join(str(row.get("source") or row.get("target")) for row in candidates[:12])
            + (" ..." if len(candidates) > 12 else "")
        )
    if st.button("Namenliste speichern"):
        write_names(npath, normalized_names)
        st.success(f"Gespeichert: {npath.relative_to(REPO_ROOT)}")

if section == "Uebersetzen":
    action = provider_action(provider)
    style_label = style_labels.get(style, style)
    output_root = book_output_root(REPO_ROOT, book)
    output_root_label = str(output_root.relative_to(REPO_ROOT)).replace("\\", "/")
    missing_count = len(counts["missing"])

    st.markdown(
        f"""
        <div class="hero-strip">
          <div class="kicker">Kapitel {chapter}</div>
          <h2>Uebersetzen, Prompts bauen, Kapitel zusammensetzen</h2>
          <div class="copy">
            Diese Seite arbeitet in drei Schritten: erst Quell-Arbeitseinheiten
            vorbereiten, dann je nach Provider Uebersetzungen oder Prompts schreiben,
            danach fertige DE-Szenen ohne weiteren KI-Lauf zu einer
            Kapiteldatei zusammensetzen.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"{source_lang_label}-{unit_label}", counts["ru"])
    c2.metric(f"DE-{unit_label}", counts["de"])
    c3.metric("Fehlend", missing_count)
    c4.metric("Naechste Einheit", counts["next_missing"] or "-")

    st.markdown(
        f"""
        <span class="status-badge">Style: {style_label}</span>
        <span class="status-badge">Provider: {provider}</span>
        <span class="status-badge">Modell: {model}</span>
        <span class="status-badge">Chunk-Grenze: {default_chunk_limit:,} Zeichen</span>
        """,
        unsafe_allow_html=True,
    )
    translate_job, translate_job_running = _show_batch_job_panel(
        "translate-job",
        current_book_id=book_id,
        current_style=style,
        current_provider=provider,
    )
    if translate_job is None:
        _show_latest_job_log("translate", book_id, style)

    if chapter_as_scene:
        scene_choices = ["aktuelles Kapitel"]
        default_scene = 0
    else:
        scene_choices = ["alle fehlenden"]
        scene_choices.extend(f"{num:02d}" for num in counts["missing"])
        if counts["next_missing"] is not None:
            default_scene = scene_choices.index(f"{counts['next_missing']:02d}")
        else:
            default_scene = 0
    col_scope, col_flags = st.columns([2, 1])
    with col_scope:
        scene_choice = st.selectbox(
            "Umfang des Laufs",
            scene_choices,
            index=default_scene,
            help=(
                "Bei kapitelbasierten Buechern ist das aktuelle Kapitel die "
                "kleinste Einheit. Bei Szenenbuechern kann eine einzelne "
                "Szene oder alle fehlenden Szenen gestartet werden."
            ),
        )
    with col_flags:
        overwrite = st.checkbox(
            "Vorhandenes Ergebnis ersetzen",
            value=False,
            help=(
                "Nur aktivieren, wenn eine bestehende DE-Szene oder "
                "Prompt-Datei bewusst neu geschrieben werden soll."
            ),
        )
        dry_run = st.checkbox(
            "Nur anzeigen, nicht schreiben",
            value=False,
            help=(
                "Baut den ersten Prompt zur Kontrolle, fuehrt aber keinen "
                "API-Call aus und schreibt keine Ergebnisdatei."
            ),
        )
        chunk_limit_input = st.number_input(
            "Chunk-Grenze",
            min_value=0,
            max_value=200000,
            value=int(default_chunk_limit),
            step=1000,
            help=(
                "Quell-Szenen ueber dieser Zeichenzahl werden intern in Teile "
                "uebersetzt. 0 deaktiviert Chunking. Die finale DE-Datei "
                "bleibt dieselbe scene-XX.md."
            ),
        )

    source_lang = str(book.get("source_lang") or "ru")
    source_lang_label = source_lang.upper()

    oversized_current = oversized_source_scenes(
        book, chapter, int(chunk_limit_input), REPO_ROOT
    )
    if oversized_current:
        st.warning(
            "Interne Chunk-Uebersetzung wird fuer dieses Kapitel greifen: "
            + ", ".join(
                f"Szene {item['scene']:02d}: {item['chars']:,} Zeichen "
                f"-> {item['chunks']} Chunks"
                for item in oversized_current
            )
            + ". Es entstehen keine neuen Buchszenen; die Chunks werden wieder "
            "zur gleichen scene-XX.md zusammengesetzt."
        )

    if chapter_as_scene:
        selection_text = f"Kapitel {chapter}"
    elif scene_choice == "alle fehlenden":
        selection_text = (
            "Alle fehlenden Szenen"
            if missing_count
            else "Keine fehlenden Szenen im aktuellen Style"
        )
    else:
        selection_text = f"Szene {scene_choice}"

    st.markdown(
        f"""
        <div class="workflow-grid">
          <div class="workflow-card">
            <div class="workflow-step">1</div>
            <div class="workflow-title">{source_lang_label}-Szenen vorbereiten</div>
            <div class="workflow-copy">
              Erzeugt die Arbeitseinheiten der Quellsprache fuer dieses Kapitel.
              Bei Anna Karenina ist jedes Kapitel genau eine Einheit.
            </div>
            <div class="path-pill">{output_root_label}/scenes/{source_lang}/{chapter}/scene-XX.md</div>
          </div>
          <div class="workflow-card">
            <div class="workflow-step">2</div>
            <div class="workflow-title">{action["title"]}</div>
            <div class="workflow-copy">
              {action["copy"]}<br>
              Auswahl: {selection_text}
            </div>
            <div class="path-pill">{action["target"]}</div>
          </div>
          <div class="workflow-card">
            <div class="workflow-step">3</div>
            <div class="workflow-title">Kapiteldatei bauen</div>
            <div class="workflow-copy">
              Fuegt vorhandene DE-Szenen per Dateioperation zusammen. Dabei
              wird kein Text erneut an eine KI geschickt.
            </div>
            <div class="path-pill">{output_root_label}/assembled/{style}/</div>
          </div>
          <div class="workflow-card accent">
            <div class="workflow-step">4</div>
            <div class="workflow-title">DOCX / EPUB exportieren</div>
            <div class="workflow-copy">
              Erstellt ein Leser-Dokument mit Cover, Beschreibung,
              Impressum und Inhaltsseite. Die Einstellungen liegen in
              books/{book_id}/export.yaml.
            </div>
            <div class="path-pill">exports/{style}/chapter|book/</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown(
            f"""
            <div class="tool-panel">
              <strong>1. Quellen vorbereiten</strong>
              <span>
                Nutzt die Kapitelquelle und erzeugt die Arbeitseinheiten der
                Quellsprache fuer dieses Kapitel.
              </span>
              <div class="mini-list">
                <div>Quelle: books/&lt;id&gt;/work/chapters/NNN-source.md</div>
                <div>Ziel: books/&lt;id&gt;/work/scenes/{source_lang}/NNN/</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(f"{source_lang_label}-Szenen extrahieren", disabled=not bool(chapter)):
            show_result(run_command([
                "tools/extract_scenes.py",
                "--book", book_id,
                "--chapter", chapter,
            ]))

    with col_b:
        st.markdown(
            f"""
            <div class="tool-panel">
              <strong>2. Lauf starten</strong>
              <span>{action["copy"]}</span>
              <div class="mini-list">
                <div>Auswahl: {selection_text}</div>
                <div>Ziel: {action["target"]}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if provider == "openrouter":
            st.caption(
                "Verbraucht OpenRouter-Tokens und schreibt DE-Szenen. "
                "Token und Antwortmodell landen im Kapitel-Log."
            )
        elif provider == "ollama":
            st.caption(
                "Sendet Szenen an das lokale Ollama-Modell und schreibt "
                "DE-Szenen. Kein Token-Verbrauch, keine Netzwerk-Kosten."
            )
        else:
            st.caption(
                "Schreibt nur Prompt-/Arbeitsdateien. Es wird kein externer "
                "KI-Call ausgefuehrt."
            )
        if st.button(
            action["button"],
            disabled=not bool(chapter) or translate_job_running,
        ):
            cmd = [
                "tools/translate_chapter.py",
                "--book", book_id,
                "--chapter", chapter,
                "--style", style,
                "--provider", provider,
            ]
            if provider == "openrouter":
                cmd.extend(["--model", model])
            elif provider == "ollama":
                cmd.extend(["--model", ollama_model])
            cmd.extend(["--chunk-char-limit", str(int(chunk_limit_input))])
            if not chapter_as_scene and scene_choice != "alle fehlenden":
                cmd.extend(["--scene", scene_choice])
            if overwrite:
                cmd.append("--overwrite")
            if dry_run:
                cmd.extend(["--dry-run", "--dry-run-first-scene"])
            if provider in ("openrouter", "ollama") and not dry_run:
                job = _start_batch_job(
                    cmd,
                    book_id=book_id,
                    style=style,
                    provider=provider,
                    kind="translate",
                )
                st.success(
                    "Uebersetzung im Hintergrund gestartet. "
                    f"PID {job['pid']}, Log: {job['log_path']}"
                )
                st.rerun()
            else:
                show_result(run_command(cmd))

    with col_c:
        st.markdown(
            f"""
            <div class="tool-panel">
              <strong>3. Kapitel zusammensetzen</strong>
              <span>
                Baut aus vorhandenen DE-Szenen eine Kapitelversion. Dieser
                Schritt ist tokenfrei und schickt nichts an eine KI.
              </span>
              <div class="mini-list">
                <div>Style: {style}</div>
                <div>Ziel: books/&lt;id&gt;/work/assembled/{style}/</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Kapitel zusammensetzen", disabled=counts["de"] == 0 or not bool(chapter)):
            show_result(run_command([
                "tools/assemble_chapter.py",
                "--book", book_id,
                "--chapter", chapter,
                "--style", style,
            ]))
        if counts["de"] == 0:
            st.caption("Noch keine DE-Szenen fuer diesen Style vorhanden.")

    st.markdown("### Mehrere Kapitel uebersetzen")
    st.caption(
        "Dieser Batch fuehrt Schritt 1 und Schritt 2 fuer mehrere Kapitel aus: "
        "fehlende Quell-Arbeitseinheiten werden bei Bedarf erzeugt, danach werden "
        "fehlende DE-Ergebnisse oder Prompt-Dateien fuer den gewaehlten Provider "
        "geschrieben. DOCX/EPUB-Export passiert hier nicht."
    )
    st.markdown(
        f"""
        <div class="tool-panel">
          <strong>Was bedeutet "Alle fehlenden"?</strong>
          <span>
            Es werden die Kapitel ausgewaehlt, bei denen fuer den aktuellen
            Stil <strong>{style_label}</strong> noch nicht alle Quell-Arbeitseinheiten
            als DE-Ergebnis vorhanden sind. Vorhandene Ergebnisse bleiben erhalten,
            ausser "Vorhandenes Ergebnis ersetzen" ist oben aktiv.
          </span>
          <div class="mini-list">
            <div>Provider openrouter: schreibt DE-Szenen und verbraucht Tokens.</div>
            <div>Provider prompt_file: schreibt nur Prompt-Dateien, keine DE-Szenen.</div>
            <div>Provider workspace_ai: schreibt Arbeitsanweisungen fuer eine Repo-KI.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    batch_a, batch_b, batch_c, batch_d = st.columns([1.2, 1, 1, 1])
    with batch_a:
        batch_scope = st.selectbox(
            "Batch-Umfang",
            ["Aktuelles Kapitel", "Bereich", "Alle fehlenden"],
            help=(
                "Legt nur fest, welche Kapitel der Batch betrachtet. "
                "Der Batch exportiert kein EPUB/DOCX."
            ),
        )
    with batch_b:
        start_chapter = st.selectbox(
            "Von",
            chapters or [chapter],
            index=chapters.index(chapter) if chapter in chapters else 0,
            disabled=batch_scope != "Bereich",
        )
    with batch_c:
        end_chapter = st.selectbox(
            "Bis",
            chapters or [chapter],
            index=chapters.index(chapter) if chapter in chapters else 0,
            disabled=batch_scope != "Bereich",
        )
    with batch_d:
        batch_auto_status = st.checkbox(
            "Status automatisch",
            value=False,
            help="Setzt Kapitel bei OpenRouter-Laeufen automatisch auf Review.",
        )
        batch_dry_run = st.checkbox("Batch nur planen", value=True)
        batch_assemble_after = st.checkbox(
            "Danach zusammensetzen",
            value=False,
            disabled=provider not in ("openrouter", "ollama"),
            help=(
                "Startet nach erfolgreichen Uebersetzungen "
                "assemble_chapter.py fuer die ausgewaehlten Kapitel. "
                "Bei prompt_file/workspace_ai entstehen keine DE-Szenen."
            ),
        )

    batch_summary = []
    if batch_scope == "Aktuelles Kapitel":
        batch_summary.append(f"Kapitel: {chapter}")
    elif batch_scope == "Bereich":
        batch_summary.append(f"Kapitel: {start_chapter} bis {end_chapter}")
    else:
        batch_summary.append("Kapitel: alle aktuell unvollstaendigen Kapitel")
    batch_summary.append(f"Schritt 1: Quell-Arbeitseinheiten bei Bedarf erzeugen")
    batch_summary.append(f"Schritt 2: {action['title']}")
    batch_summary.append(
        "Schritt 3: Kapitel zusammensetzen"
        if batch_assemble_after and provider in ("openrouter", "ollama")
        else "Schritt 3: nicht automatisch"
    )
    batch_summary.append(f"Chunk-Grenze: {int(chunk_limit_input):,} Zeichen")
    batch_summary.append("Export: nicht in diesem Batch")
    st.info(" | ".join(batch_summary))

    active_job, active_job_running = _refresh_batch_job(_load_batch_job())
    if active_job_running:
        blocker_log = active_job.get("log_path") or "-"
        same_context = (
            active_job.get("book_id") == book_id
            and active_job.get("style") == style
            and active_job.get("provider") == provider
        )
        message = (
            f"{active_job.get('book_id')} | {active_job.get('style')} | "
            f"{active_job.get('provider')} | PID {active_job.get('pid')} | "
            f"Log: {blocker_log}"
        )
        if same_context:
            st.info(
                "Dieser Uebersetzungs-Batch laeuft im Hintergrund. "
                f"{message}. Weitere Batches sind bis zum Abschluss gesperrt."
            )
        else:
            st.warning(
                "Ein anderer Hintergrund-Batch laeuft bereits. "
                f"{message}. Bitte erst stoppen oder abwarten."
            )

    batch_button_label = "Batch planen" if batch_dry_run else "Batch im Hintergrund starten"
    if active_job_running:
        st.caption("Der Startknopf ist deaktiviert, solange ein Hintergrundlauf aktiv ist.")
    if st.button(batch_button_label, disabled=not bool(chapters) or active_job_running):
        cmd = [
            "tools/translate_batch.py",
            "--book", book_id,
            "--style", style,
            "--provider", provider,
        ]
        if provider == "openrouter":
            cmd.extend(["--model", model])
        elif provider == "ollama":
            cmd.extend(["--model", ollama_model])
        cmd.extend(["--chunk-char-limit", str(int(chunk_limit_input))])
        if batch_scope == "Aktuelles Kapitel":
            cmd.extend(["--chapter", chapter])
        elif batch_scope == "Bereich":
            cmd.extend(["--from", start_chapter, "--to", end_chapter])
        else:
            cmd.append("--missing")
        if overwrite:
            cmd.append("--overwrite")
        if batch_assemble_after and provider in ("openrouter", "ollama"):
            cmd.append("--assemble-after")
        if batch_auto_status:
            cmd.append("--auto-status")
        if batch_dry_run:
            cmd.append("--dry-run")
            with st.spinner("Batch wird geplant..."):
                show_result(run_command(cmd))
        else:
            job = _start_batch_job(cmd, book_id=book_id, style=style, provider=provider)
            st.success(
                "Batch im Hintergrund gestartet. "
                f"PID {job['pid']}, Log: {job['log_path']}"
            )
            st.rerun()

if section == "Stiltest":
    show_remembered_result()
    st.subheader(f"Stiltest Kapitel {chapter}")
    output_root = book_output_root(REPO_ROOT, book)
    source_lang = str(book.get("source_lang") or "ru")
    source_lang_label = source_lang.upper()
    source_scene_nums = [
        num for p in list_source_scene_paths(output_root, chapter, source_lang)
        if (num := parse_scene_number(p, chapter)) is not None
    ]
    if not source_scene_nums:
        st.info(f"Keine {source_lang_label}-Szenen fuer dieses Kapitel gefunden.")
    else:
        scene_num = st.selectbox(
            "Vergleichs-Szene",
            [f"{num:02d}" for num in sorted(source_scene_nums)],
        )
        selected_scene = int(scene_num)
        st.caption(
            "Links steht das Original, daneben die Style-Profile "
            "aus dem Buchpaket."
        )
        replace_existing = st.checkbox(
            "Vorhandenes Ergebnis beim Erzeugen ersetzen",
            value=False,
            help=(
                "Loescht die vorhandene Szenen- oder Prompt-Datei fuer "
                "den gewaehlten Stil, bevor neu erzeugt wird."
            ),
        )
        cols = st.columns(min(4, len(styles) + 1))
        source_path = source_scene_path(output_root, chapter, selected_scene, source_lang)
        with cols[0]:
            st.markdown(f"### Original {source_lang_label}")
            if source_path.exists():
                st.caption(str(source_path.relative_to(REPO_ROOT)))
                st.text_area(
                    f"{source_lang}-scene-{scene_num}",
                    source_path.read_text(encoding="utf-8"),
                    height=420,
                    key=f"compare-{source_lang}-{chapter}-{scene_num}",
                )
            else:
                st.info(f"Keine {source_lang_label}-Szene gefunden.")
        for idx, profile in enumerate(styles):
            style_id = profile["id"]
            label = profile.get("label", style_id)
            with cols[(idx + 1) % len(cols)]:
                st.markdown(f"### {label}")
                scene_path = de_scene_path(
                    output_root, chapter, selected_scene, style_id,
                )
                generated_prompt_path = prompt_path(
                    output_root, chapter, style_id, selected_scene,
                )
                if scene_path.exists():
                    st.caption(str(scene_path.relative_to(REPO_ROOT)))
                    st.text_area(
                        f"{style_id}-scene-{scene_num}",
                        scene_path.read_text(encoding="utf-8"),
                        height=420,
                        key=f"compare-{style_id}-{chapter}-{scene_num}",
                    )
                else:
                    st.info("Noch keine Uebersetzung.")
                    if generated_prompt_path.exists():
                        st.caption(str(generated_prompt_path.relative_to(REPO_ROOT)))
                        st.text_area(
                            f"{style_id}-prompt-{scene_num}",
                            generated_prompt_path.read_text(encoding="utf-8"),
                            height=420,
                            key=f"prompt-{style_id}-{chapter}-{scene_num}",
                        )
                if scene_path.exists() or generated_prompt_path.exists():
                    if st.button(
                        "Vorhandenes Ergebnis loeschen",
                        key=f"delete-{style_id}-{chapter}-{scene_num}",
                    ):
                        try:
                            deleted = delete_existing_style_outputs(
                                scene_path, generated_prompt_path, output_root,
                            )
                        except ValueError as exc:
                            remember_result("error", str(exc))
                            st.rerun()
                        if deleted:
                            remember_result(
                                "success",
                                "Geloescht: "
                                + ", ".join(
                                    str(p.relative_to(REPO_ROOT)) for p in deleted
                                ),
                            )
                        else:
                            remember_result("success", "Keine Datei vorhanden.")
                        st.rerun()
                if st.button(
                    f"{label} erzeugen",
                    key=f"run-{style_id}-{chapter}-{scene_num}",
                ):
                    if (
                        provider == "openrouter"
                        and scene_path.exists()
                        and not replace_existing
                    ):
                        remember_result(
                            "error",
                            (
                                "Diese Szene existiert bereits. Aktiviere "
                                "'Vorhandenes Ergebnis beim Erzeugen ersetzen' "
                                "oder loesche das Ergebnis, damit wirklich ein "
                                f"neuer OpenRouter-Lauf mit {model} startet."
                            ),
                        )
                        st.rerun()
                    cmd = [
                        "tools/translate_chapter.py",
                        "--book", book_id,
                        "--chapter", chapter,
                        "--scene", scene_num,
                        "--style", style_id,
                        "--provider", provider,
                    ]
                    if provider == "openrouter":
                        cmd.extend(["--model", model])
                    elif provider == "ollama":
                        cmd.extend(["--model", ollama_model])
                    cmd.extend(["--chunk-char-limit", str(int(chunk_limit_input))])
                    if replace_existing:
                        try:
                            delete_existing_style_outputs(
                                scene_path, generated_prompt_path, output_root,
                            )
                        except ValueError as exc:
                            remember_result("error", str(exc))
                            st.rerun()
                        cmd.append("--overwrite")
                    with st.spinner(f"{label} wird erzeugt..."):
                        result = run_command(cmd)
                    show_result(result)
                    if result.returncode == 0 and scene_path.exists():
                        remember_result(
                            "success",
                            f"{label} erzeugt: "
                            f"{scene_path.relative_to(REPO_ROOT)} "
                            f"(Provider: {provider}, Modell: {model})",
                        )
                        st.rerun()
                    if result.returncode == 0 and generated_prompt_path.exists():
                        remember_result(
                            "success",
                            f"{label} Prompt geschrieben: "
                            f"{generated_prompt_path.relative_to(REPO_ROOT)} "
                            f"(Provider: {provider}, Modell: {model})",
                        )
                        st.rerun()

if section == "Versionen":
    st.subheader(f"Assemblies Kapitel {chapter}")
    paths = assembly_paths(book, chapter, style, REPO_ROOT)
    if not paths:
        st.info("Keine Kapitelversion vorhanden.")
    else:
        labels = [p.name for p in paths]
        selected = st.selectbox("Version", labels, index=len(labels) - 1)
        path = paths[labels.index(selected)]
        st.caption(str(path.relative_to(REPO_ROOT)))
        st.text_area(
            "Inhalt",
            path.read_text(encoding="utf-8"),
            height=500,
        )

if section == "Review":
    output_root = book_output_root(REPO_ROOT, book)
    review_root = output_root / "reviews" / style
    summary_json = review_root / "review-summary.json"
    summary_md = review_root / "review-summary.md"

    st.markdown(
        f"""
        <div class="hero-strip">
          <div class="kicker">Release-Review</div>
          <h2>Editor-Agent fuer fertige Uebersetzungen</h2>
          <div class="copy">
            Der Review-Lauf prueft den explizit ausgewaehlten Stil report-only.
            Er veraendert keine Szenendateien und fuehrt keine Auto-Fixes aus.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info(
        f"Gepruefter Stil: {style_label}. Reports: "
        f"{review_root.relative_to(REPO_ROOT)}"
    )

    review_a, review_b, review_c, review_d = st.columns([1.2, 1, 1, 1])
    with review_a:
        review_scope = st.selectbox(
            "Review-Umfang",
            ["Aktuelles Kapitel", "Bereich", "Ganzes Buch"],
        )
    with review_b:
        review_start = st.selectbox(
            "Review von",
            chapters or [chapter],
            index=chapters.index(chapter) if chapter in chapters else 0,
            disabled=review_scope != "Bereich",
        )
    with review_c:
        review_end = st.selectbox(
            "Review bis",
            chapters or [chapter],
            index=chapters.index(chapter) if chapter in chapters else 0,
            disabled=review_scope != "Bereich",
        )
    with review_d:
        review_llm = st.selectbox(
            "KI-Review",
            ["none", "openrouter", "ollama"],
            format_func={
                "none": "Regelcheck (keine KI)",
                "openrouter": "OpenRouter",
                "ollama": "Ollama lokal",
            }.get,
            help=(
                "Legt fest, ob zusaetzlich zu den regelbasierten Checks ein "
                "LLM als Editor mitliest. 'Regelcheck (keine KI)' laeuft den "
                "gewaehlten Umfang vollstaendig durch, liest RU- und DE-Dateien "
                "lokal und prueft feste Kriterien: fehlende Szenen, kyrillische "
                "Reste, kaputte Zeichen, auffaellige Laengen, doppelte Header "
                "und Degeneration. OpenRouter nutzt das links gewaehlte Modell; "
                "Ollama nutzt ein lokales Modell."
            ),
        )
        review_llm_scope = st.selectbox(
            "KI-Umfang",
            ["flagged", "all"],
            format_func={
                "flagged": "Nur auffaellige Szenen",
                "all": "Alle Szenen",
            }.get,
            help=(
                "Gilt nur, wenn ein KI-Review aktiv ist. 'Nur auffaellige "
                "Szenen' sendet nur Szenen an das Modell, bei denen die "
                "regelbasierten Checks bereits etwas gefunden haben. 'Alle "
                "Szenen' laesst das Modell jede RU/DE-Szene im gewaehlten "
                "Umfang gegenlesen; das ist gruendlicher, aber langsamer und "
                "bei OpenRouter teurer."
            ),
        )
    st.caption(
        "Der Review ist report-only: Die Gesamtuebersicht wird immer unter "
        "work/reviews/ geschrieben. Einzelne Kapitelreports entstehen nur fuer "
        "Kapitel mit Befunden; saubere Kapitel stehen nur in der Summary."
    )

    DEFAULT_OLLAMA_MODELS = ["qwen3:8b", "gemma4:latest"]
    ollama_model = "gemma4:latest"
    if review_llm == "ollama":
        ollama_model = st.selectbox(
            "Ollama-Modell",
            DEFAULT_OLLAMA_MODELS,
            index=0 if ollama_model not in DEFAULT_OLLAMA_MODELS else
                  DEFAULT_OLLAMA_MODELS.index(ollama_model),
            help="Lokales Ollama-Modell. qwen3:8b wird empfohlen.",
        )
    review_fail_on_errors = st.checkbox(
        "Exit-Code bei Fehlern",
        value=True,
        help="Nuetzlich fuer Release-Gates und Skripte.",
    )

    review_cmd = [
        "tools/review_manuscript.py",
        "--book", book_id,
        "--style", style,
        "--llm", review_llm,
        "--llm-scope", review_llm_scope,
    ]
    if review_scope == "Aktuelles Kapitel":
        review_cmd.extend(["--chapter", chapter])
    elif review_scope == "Bereich":
        review_cmd.extend(["--from", review_start, "--to", review_end])
    else:
        review_cmd.append("--all")
    if review_llm == "openrouter":
        review_cmd.extend(["--model", model])
    if review_llm == "ollama":
        review_cmd.extend(["--ollama-model", ollama_model])
    if review_fail_on_errors:
        review_cmd.append("--fail-on-errors")

    active_job, active_job_running = _show_batch_job_panel(
        "review-job",
        current_book_id=book_id,
        current_style=style,
        current_provider=f"review:{review_llm}",
    )
    if active_job is None:
        _show_latest_job_log("review", book_id, style)
    col_plan, col_run = st.columns([1, 1])
    with col_plan:
        if st.button("Review planen", disabled=not bool(chapters)):
            with st.spinner("Review wird geplant..."):
                show_result(run_command([*review_cmd, "--dry-run"]))
    with col_run:
        if st.button(
            "Review im Hintergrund starten",
            disabled=not bool(chapters) or active_job_running,
        ):
            job = _start_batch_job(
                review_cmd,
                book_id=book_id,
                style=style,
                provider=f"review:{review_llm}",
                kind="review",
            )
            st.success(
                "Review im Hintergrund gestartet. "
                f"PID {job['pid']}, Log: {job['log_path']}"
            )
            st.rerun()

    if summary_json.exists():
        try:
            summary = json.loads(summary_json.read_text(encoding="utf-8"))
        except Exception:
            summary = {}
        st.markdown("### Letzter Review")
        counts_summary = summary.get("counts") or {}
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Kapitel", len(summary.get("chapters") or []))
        m2.metric("Fehler", counts_summary.get("ERROR", 0))
        m3.metric("Warnungen", counts_summary.get("WARNING", 0))
        m4.metric("Hinweise", counts_summary.get("INFO", 0))
        st.caption(str(summary_json.relative_to(REPO_ROOT)))
        if summary_md.exists():
            with st.expander("Summary anzeigen", expanded=False):
                st.markdown(summary_md.read_text(encoding="utf-8"))
    else:
        st.info("Noch kein Review-Report fuer diesen Stil vorhanden.")

    st.markdown("### Review-Fixes")
    fix_root = output_root / "review-fixes" / style
    fix_manifest = fix_root / "fix-manifest.json"
    fix_plan = fix_root / "fix-plan.txt"
    manual_review = fix_root / "manual-review.md"
    promotion_report = fix_root / "promotion-report.json"
    fix_cmd = [
        "tools/apply_review_suggestions.py",
        "--book", book_id,
        "--style", style,
    ]
    fix_a, fix_b, fix_c = st.columns([1, 1, 1])
    with fix_a:
        if st.button("Fixes planen", disabled=not summary_json.exists()):
            show_result(run_command([*fix_cmd, "--plan"]))
    with fix_b:
        if st.button("Fix-Kandidaten erzeugen", disabled=not summary_json.exists()):
            show_result(run_command([*fix_cmd, "--stage"]))
    with fix_c:
        if st.button("Gepruefte Kandidaten uebernehmen", disabled=not fix_manifest.exists()):
            show_result(run_command([*fix_cmd, "--promote"]))

    if fix_manifest.exists():
        try:
            manifest = json.loads(fix_manifest.read_text(encoding="utf-8"))
        except Exception:
            manifest = {}
        staged_items = manifest.get("staged") or []
        staged_fixes = sum(len(item.get("applied") or []) for item in staged_items)
        manual_count = 0
        if manual_review.exists():
            manual_count = sum(
                1
                for line in manual_review.read_text(
                    encoding="utf-8", errors="replace"
                ).splitlines()
                if line.startswith("## Kapitel ")
            )
        fm1, fm2, fm3, fm4 = st.columns(4)
        fm1.metric("Staged", len(staged_items))
        fm2.metric("Fixbar", staged_fixes)
        fm3.metric("Nicht eindeutig", manual_count)
        fm4.metric("Manifest", "vorhanden")
        st.caption(str(fix_manifest.relative_to(REPO_ROOT)))
        if manual_review.exists():
            with st.expander("Manuelle Fixliste anzeigen", expanded=False):
                st.markdown(manual_review.read_text(encoding="utf-8"))
    else:
        st.caption("Noch keine Fix-Kandidaten fuer diesen Review gestaged.")

    if fix_plan.exists():
        with st.expander("Fix-Plan anzeigen", expanded=False):
            st.code(fix_plan.read_text(encoding="utf-8", errors="replace"), language="text")

    if promotion_report.exists():
        try:
            report = json.loads(promotion_report.read_text(encoding="utf-8"))
        except Exception:
            report = {}
        pr1, pr2, pr3 = st.columns(3)
        pr1.metric("Uebernommen", report.get("promoted", 0))
        pr2.metric("Uebersprungen", report.get("skipped", 0))
        pr3.metric("Assembled", len(report.get("assembled_chapters") or []))

if section == "Export":
    output_root = book_output_root(REPO_ROOT, book)
    export_meta = load_export_meta(book)
    cover_cfg = export_meta.get("cover", {}) or {}
    front_cfg = export_meta.get("front_matter", {}) or {}
    output_cfg = export_meta.get("output", {}) or {}
    illustrations_cfg = export_meta.get("illustrations", {}) or {}
    cover_mode = cover_cfg.get("mode", "placeholder")
    cover_image = str(cover_cfg.get("image_path") or "").strip()
    cover_status = (
        cover_image if cover_mode == "image" and cover_image else "Automatisches Platzhalter-Cover"
    )
    illustrations_status = "aktiv" if illustrations_cfg.get("enabled", False) else "aus"
    front_enabled = [
        name for name, enabled in [
            ("Cover im Text", front_cfg.get("cover_in_body", True)),
            ("Beschreibung", front_cfg.get("description_page", True)),
            ("Impressum", front_cfg.get("imprint_page", True)),
            ("Inhalt", front_cfg.get("toc_page", True)),
        ]
        if enabled
    ]
    st.markdown(
        f"""
        <div class="hero-strip">
          <div class="kicker">Leser-Export</div>
          <h2>EPUB, DOCX und PDF erstellen</h2>
          <div class="copy">
            Baut aus fertigen DE-Szenen ein Lesedokument. Cover,
            Beschreibung, Impressum und Inhaltsseite werden ueber
            books/{book_id}/export.yaml gesteuert.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="export-grid">
          <div class="export-card">
            <h3>Was entsteht?</h3>
            <p>
              DOCX nutzt python-docx fuer ein bearbeitbares Word-Manuskript.
              EPUB nutzt Pandoc. PDF rendert eine eigene HTML-/CSS-Version
              mit Playwright und Chromium.
            </p>
            <div class="output-list">
              <div class="output-item">
                <span class="config-icon"><svg viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5z"/></svg></span>
                <strong>Dokumente</strong>
                <span>DOCX, EPUB oder PDF als Lesefassung ohne Prompt-, Provider- oder Tokeninformationen.</span>
              </div>
              <div class="output-item">
                <span class="config-icon"><svg viewBox="0 0 24 24"><path d="M3 3h18v18H3z"/><path d="M8 8h8"/><path d="M8 12h8"/><path d="M8 16h5"/></svg></span>
                <strong>Quelle</strong>
                <span>books/{book_id}/work/scenes/de/{style}/</span>
              </div>
              <div class="output-item">
                <span class="config-icon"><svg viewBox="0 0 24 24"><path d="M4 4h6l2 3h8v13H4z"/><path d="M4 10h16"/></svg></span>
                <strong>Ausgabe</strong>
                <span>books/{book_id}/exports/{style}/chapter|book/</span>
              </div>
            </div>
          </div>
          <div class="export-card">
            <h3>Konfiguration</h3>
            <div class="config-row">
              <span class="config-icon"><svg viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5z"/></svg></span>
              <b>Cover</b><span>{cover_status}</span>
            </div>
            <div class="config-row">
              <span class="config-icon"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M8 13h8"/><path d="M8 17h5"/></svg></span>
              <b>Frontmatter</b><span>{", ".join(front_enabled) or "aus"}</span>
            </div>
            <div class="config-row">
              <span class="config-icon"><svg viewBox="0 0 24 24"><path d="M21 19V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14"/><path d="M3 16l5-5 4 4 3-3 6 6"/><circle cx="8.5" cy="8.5" r="1.5"/></svg></span>
              <b>Illustrationen</b><span>{illustrations_status}</span>
            </div>
            <div class="config-row">
              <span class="config-icon"><svg viewBox="0 0 24 24"><path d="M5 12h14"/><path d="M5 6h14"/><path d="M5 18h14"/></svg></span>
              <b>Trenner</b><span>{output_cfg.get("scene_separator", "* * *")}</span>
            </div>
            <div class="config-row">
              <span class="config-icon"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg></span>
              <b>Datei</b><span>books/{book_id}/export.yaml</span>
            </div>
            <div class="config-row">
              <span class="config-icon"><svg viewBox="0 0 24 24"><path d="M4 4h6l2 3h8v13H4z"/><path d="M4 10h16"/></svg></span>
              <b>Cover-Ordner</b><span>books/{book_id}/assets/covers/</span>
            </div>
            <div class="config-row">
              <span class="config-icon"><svg viewBox="0 0 24 24"><path d="M3 3h18v18H3z"/><path d="M7 7h10v10H7z"/></svg></span>
              <b>Kapitelbilder</b><span>books/{book_id}/assets/chapter/chapter-NNN.*</span>
            </div>
            <div class="config-row">
              <span class="config-icon"><svg viewBox="0 0 24 24"><path d="M3 3h18v18H3z"/><path d="M8 8h8v8H8z"/><path d="M12 3v5"/><path d="M12 16v5"/></svg></span>
              <b>Szenenbilder</b><span>books/{book_id}/assets/scene/NNN/scene-NNN.*</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-heading">
          <h3>Export-Einstellungen</h3>
          <span>Umfang, Format und Teil-Export</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    control_a, control_b, control_c = st.columns([1, 1, 1])
    with control_a:
        export_scope_label = st.radio(
            "Umfang",
            ["Aktuelles Kapitel", "Ganzes Buch"],
            horizontal=True,
        )
        export_scope = (
            "chapter" if export_scope_label == "Aktuelles Kapitel" else "book"
        )
    with control_b:
        export_format_label = st.selectbox(
            "Format",
            ["DOCX + EPUB", "DOCX", "EPUB", "PDF"],
        )
        export_format = {
            "DOCX + EPUB": "all",
            "DOCX": "docx",
            "EPUB": "epub",
            "PDF": "pdf",
        }[export_format_label]
    with control_c:
        allow_partial_export = st.checkbox(
            "Teil-Export erlauben",
            value=False,
            help=(
                "Ohne diese Option bricht der Export ab, sobald fuer den "
                "gewaehlten Style Szenen fehlen."
            ),
        )

    st.info(
        f"Exportiert wird immer der links ausgewaehlte Stil: {style_label}. "
        "Wenn gerade uebersetzte Dateien fehlen, pruefe zuerst diese Stiltabelle."
    )
    if export_format == "pdf":
        st.info(
            "PDF benoetigt Playwright und Chromium: "
            "`pip install -r requirements.txt` und "
            "`python -m playwright install chromium`."
        )
    st.markdown(
        """
        <div class="section-heading">
          <h3>Kapitelstatus</h3>
          <span>Bereits vorhandene DE-Szenen je Stil</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_soft_table(exportable_style_rows(book, styles, chapter, REPO_ROOT))

    if export_scope == "chapter":
        export_counts = counts
        export_missing_chapters = [chapter] if export_counts["missing"] else []
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Kapitel", chapter)
        c2.metric(f"{source_lang_label}-Szenen", export_counts["ru"])
        c3.metric("DE-Szenen", export_counts["de"])
        c4.metric("Fehlend", len(export_counts["missing"]))
        if export_counts["missing"]:
            st.warning(
                "Fehlende Szenen: "
                + ", ".join(f"{num:02d}" for num in export_counts["missing"])
            )
    else:
        rows = chapter_rows(book, style, REPO_ROOT)
        export_missing_chapters = [
            row["Kapitel"] for row in rows if int(row.get("Fehlt") or 0) > 0
        ]
        total_ru = sum(int(row.get("RU") or 0) for row in rows)
        total_de = sum(int(row.get("DE") or 0) for row in rows)
        total_missing = sum(int(row.get("Fehlt") or 0) for row in rows)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Kapitel", len(rows))
        c2.metric(f"{source_lang_label}-Szenen", total_ru)
        c3.metric("DE-Szenen", total_de)
        c4.metric("Fehlend", total_missing)
        if export_missing_chapters:
            st.warning(
                "Unvollstaendige Kapitel: "
                + ", ".join(export_missing_chapters[:12])
                + (" ..." if len(export_missing_chapters) > 12 else "")
            )

    selected_export_chapters = [chapter] if export_scope == "chapter" and chapter else chapters
    illustration_counts = count_export_illustrations(
        book,
        export_meta,
        selected_export_chapters,
        REPO_ROOT,
    )
    ic1, ic2, ic3 = st.columns(3)
    ic1.metric("Illustrationen", illustration_counts["total"])
    ic2.metric("Kapitelbilder", illustration_counts["chapter"])
    ic3.metric("Szenenbilder", illustration_counts["scene"])

    st.caption(
        f"Eigenes Cover: Bild nach books/{book_id}/assets/covers/ legen, "
        "dann in export.yaml `cover.mode: image` und `cover.image_path` setzen."
    )
    st.caption(
        f"Optionale Bilder: Kapitelbilder nach books/{book_id}/assets/chapter/"
        " als `chapter-NNN.*`, Szenenbilder nach "
        f"books/{book_id}/assets/scene/NNN/ als `scene-NNN.*` legen."
    )
    export_disabled = export_scope == "chapter" and not bool(chapter)
    if export_disabled:
        st.info("Fuer Kapitel-Export zuerst Quell-Kapitel erzeugen.")
    if st.button("Export erzeugen", disabled=export_disabled, type="primary"):
        cmd = [
            "tools/export_manuscript.py",
            "--book", book_id,
            "--style", style,
            "--scope", export_scope,
            "--format", export_format,
        ]
        if export_scope == "chapter":
            cmd.extend(["--chapter", chapter])
        if allow_partial_export:
            cmd.append("--allow-partial")
        with st.spinner("Export wird erzeugt..."):
            show_result(run_command(cmd))

    latest_exports = latest_export_files(book, style, REPO_ROOT)
    if latest_exports:
        st.markdown("### Letzte Exportdateien")
        for path in latest_exports[:8]:
            st.caption(str(path.relative_to(REPO_ROOT)))
    else:
        st.info("Noch keine Exportdateien fuer diesen Style vorhanden.")

if section == "Logs":
    st.subheader(f"Log Kapitel {chapter}")
    lp = log_path(book, chapter, REPO_ROOT)
    if lp.exists():
        st.caption(str(lp.relative_to(REPO_ROOT)))
        st.text_area("Log", lp.read_text(encoding="utf-8"), height=500)
    else:
        st.info("Kein Logfile vorhanden.")
