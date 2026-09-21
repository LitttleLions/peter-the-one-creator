"""Framework-neutral dashboard background job helpers."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
JOB_DIR = REPO_ROOT / "var" / "dashboard-jobs"
TERMINAL_STATUSES = {"completed", "failed", "stopped", "stale"}


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
    return slug.strip("-") or "job"


def make_job_id(kind: str, book_id: str, style: str) -> str:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return "-".join(safe_slug(part) for part in [stamp, kind, book_id, style])


def jobs_dir(repo_root: Path = REPO_ROOT) -> Path:
    return repo_root / "var" / "dashboard-jobs"


def job_file(job_id: str, repo_root: Path = REPO_ROOT) -> Path:
    return jobs_dir(repo_root) / f"{job_id}.json"


def job_log_path(job_id: str, repo_root: Path = REPO_ROOT) -> Path:
    return jobs_dir(repo_root) / f"{job_id}.log"


def write_job(path: Path, job: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def load_job_path(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_job(job_id: str, repo_root: Path = REPO_ROOT) -> dict[str, Any] | None:
    return load_job_path(job_file(job_id, repo_root))


def list_jobs(repo_root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    root = jobs_dir(repo_root)
    if not root.exists():
        return []
    jobs = []
    for path in root.glob("*.json"):
        job = load_job_path(path)
        if job:
            job.setdefault("job_id", path.stem)
            jobs.append(job)
    return sorted(
        jobs,
        key=lambda item: str(item.get("started_at") or item.get("updated_at") or ""),
        reverse=True,
    )


def progress_from_log(text: str) -> tuple[int | None, int | None]:
    progress = None
    for match in re.finditer(r"^\[(\d+)/(\d+)\]\s+(?:Kapitel|python\b)", text, re.MULTILINE):
        progress = (int(match.group(1)), int(match.group(2)))
    return progress or (None, None)


def read_log_tail(job: dict[str, Any], repo_root: Path = REPO_ROOT, lines: int = 80) -> str:
    raw_log_path = str(job.get("log_path") or "")
    if not raw_log_path:
        return ""
    path = Path(raw_log_path)
    if not path.is_absolute():
        path = repo_root / path
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return "\n".join(text.splitlines()[-lines:])


def latest_job_log(kind: str, book_id: str, style: str, repo_root: Path = REPO_ROOT) -> Path | None:
    root = jobs_dir(repo_root)
    if not root.exists():
        return None
    pattern = f"*-{safe_slug(kind)}-{safe_slug(book_id)}-{safe_slug(style)}.log"
    logs = sorted(root.glob(pattern), key=lambda path: path.stat().st_mtime, reverse=True)
    return logs[0] if logs else None


def _run_captured(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    """Windows tasklist/taskkill output is not always cp1252-safe."""
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        **kwargs,
    )


def process_running(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        result = _run_captured(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
        )
        return f'"{pid}"' in (result.stdout or "")
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def job_process_running(job: dict[str, Any]) -> bool:
    for key in ("pid", "child_pid"):
        try:
            pid = int(job.get(key) or 0)
        except (TypeError, ValueError):
            pid = 0
        if pid and process_running(pid):
            return True
    return False


_MANIFEST_LINE_RE = re.compile(r"^Manifest:\s+(.+)$", re.MULTILINE)


def _resolve_repo_path(raw: str, repo_root: Path) -> Path:
    path = Path(raw.strip().strip('"'))
    if not path.is_absolute():
        path = repo_root / path
    return path


def _print_report_complete(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    return bool(data.get("page_count"))


def _manifest_complete(path: Path, repo_root: Path) -> bool:
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    outputs = data.get("outputs") or []
    print_report = data.get("print_report")
    if print_report:
        report_path = _resolve_repo_path(str(print_report), repo_root)
        return _print_report_complete(report_path)
    return bool(outputs)


def export_completion_signal(
    job: dict[str, Any], repo_root: Path, log_text: str = ""
) -> int | None:
    """0 = Erfolg, 1 = Fehler, None = unbekannt.

    Erfolg braucht Geschrieben:/Manifest: plus fertigen Report/Manifest.
    Eine halbfertige PDF allein reicht nicht.
    """
    if not log_text:
        raw_log_path = str(job.get("log_path") or "")
        if raw_log_path:
            path = _resolve_repo_path(raw_log_path, repo_root)
            if path.is_file():
                log_text = path.read_text(encoding="utf-8", errors="replace")
    if not log_text:
        return None
    failed_marker = "Traceback" in log_text or "FEHLER:" in log_text
    has_written = "Geschrieben:" in log_text or "Manifest:" in log_text or "Summary:" in log_text
    if failed_marker and not has_written:
        return 1
    if not has_written:
        return None
    manifest_match = _MANIFEST_LINE_RE.search(log_text)
    if manifest_match:
        manifest_path = _resolve_repo_path(manifest_match.group(1), repo_root)
        if _manifest_complete(manifest_path, repo_root):
            return 0
        if str(job.get("kind") or "") == "export" and "paperback" in str(
            job.get("provider") or job.get("command") or ""
        ):
            return None
    for line in log_text.splitlines():
        if "print-report.json" in line.replace("\\", "/"):
            report_path = _resolve_repo_path(line.split(":", 1)[-1], repo_root)
            if _print_report_complete(report_path):
                return 0
    if "Geschrieben:" in log_text or "Summary:" in log_text:
        return 0
    return None


def stop_process_tree(pid: int, repo_root: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    if pid <= 0:
        return subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="",
            stderr="Keine gueltige Prozess-ID fuer Stop vorhanden.",
        )
    if os.name == "nt":
        return _run_captured(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            cwd=repo_root,
        )
    return _run_captured(
        ["kill", "-TERM", str(pid)],
        cwd=repo_root,
    )


def job_stale(job: dict[str, Any], seconds: int = 4 * 3600) -> bool:
    timestamp = str(job.get("updated_at") or job.get("started_at") or "")
    if not timestamp:
        return False
    try:
        dt = datetime.fromisoformat(timestamp)
    except Exception:
        return False
    return (datetime.now() - dt).total_seconds() > seconds


def refresh_job(job: dict[str, Any] | None, repo_root: Path = REPO_ROOT) -> tuple[dict[str, Any] | None, bool]:
    if not job:
        return None, False
    status = str(job.get("status") or "")
    if status in {"completed", "failed", "stopped"}:
        return job, False

    def _finalize(status_name: str, returncode: int, note: str) -> tuple[dict[str, Any], bool]:
        job["status"] = status_name
        job["returncode"] = returncode
        job["completed_at"] = job.get("completed_at") or now_iso()
        job["status_note"] = note
        write_job(job_file(str(job.get("job_id")), repo_root), job)
        return job, False

    if job_process_running(job):
        if status == "stale":
            job["status"] = "running"
            job.pop("status_note", None)
            write_job(job_file(str(job.get("job_id")), repo_root), job)
        else:
            job["status"] = "running"
        return job, True

    raw_log_path = str(job.get("log_path") or "")
    log_text = ""
    path = repo_root / raw_log_path if raw_log_path else None
    if path is not None and path.is_file():
        log_text = path.read_text(encoding="utf-8", errors="replace")
    signal = export_completion_signal(job, repo_root, log_text)
    if signal == 0:
        return _finalize(
            "completed",
            0,
            "Status nachtraeglich erkannt; Prozess laeuft nicht mehr.",
        )
    if signal == 1:
        return _finalize(
            "failed",
            1,
            "Status nachtraeglich erkannt; Prozess laeuft nicht mehr.",
        )
    if job.get("stop_requested"):
        job["status"] = "stopped"
        job["completed_at"] = job.get("completed_at") or now_iso()
        write_job(job_file(str(job.get("job_id")), repo_root), job)
        return job, False
    if job.get("returncode") is not None:
        return _finalize(
            "completed" if job.get("returncode") == 0 else "failed",
            int(job.get("returncode") or 1),
            "Status nachtraeglich erkannt; Prozess laeuft nicht mehr.",
        )
    if status == "stale":
        return job, False
    job["status"] = "stale"
    job["completed_at"] = job.get("completed_at") or now_iso()
    job["status_note"] = (
        "Prozess laeuft nicht mehr; finaler Returncode fehlt."
        if not job_stale(job)
        else "Job-Heartbeat ist veraltet."
    )
    write_job(job_file(str(job.get("job_id")), repo_root), job)
    return job, False


def active_job(repo_root: Path = REPO_ROOT) -> tuple[dict[str, Any] | None, bool]:
    for job in list_jobs(repo_root):
        refreshed, running = refresh_job(job, repo_root)
        if refreshed and (running or str(refreshed.get("status") or "") not in TERMINAL_STATUSES):
            return refreshed, running
    jobs = list_jobs(repo_root)
    if jobs:
        return refresh_job(jobs[0], repo_root)
    return None, False


def request_stop(job: dict[str, Any], repo_root: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    job_id = str(job.get("job_id") or "")
    if job_id:
        job["stop_requested"] = True
        job["stop_requested_at"] = now_iso()
        write_job(job_file(job_id, repo_root), job)
    pid = int(job.get("pid") or 0)
    return stop_process_tree(pid, repo_root)


def clear_job(job: dict[str, Any], repo_root: Path = REPO_ROOT) -> None:
    job_id = str(job.get("job_id") or "")
    if not job_id:
        return
    path = job_file(job_id, repo_root)
    if path.exists():
        path.unlink()


def start_job(
    args: list[str],
    book_id: str,
    style: str,
    provider: str,
    kind: str = "batch",
    repo_root: Path = REPO_ROOT,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = jobs_dir(repo_root)
    root.mkdir(parents=True, exist_ok=True)
    job_id = make_job_id(kind, book_id, style)
    suffix = 2
    while job_file(job_id, repo_root).exists() or job_log_path(job_id, repo_root).exists():
        base_job_id = make_job_id(kind, book_id, style)
        job_id = f"{base_job_id}-{suffix}"
        suffix += 1
    log_path = job_log_path(job_id, repo_root)
    metadata_path = job_file(job_id, repo_root)
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    seed = {
        "job_id": job_id,
        "pid": None,
        "child_pid": None,
        "book_id": book_id,
        "style": style,
        "provider": provider,
        "kind": kind,
        "status": "starting",
        "returncode": None,
        "command": [sys.executable, *args],
        "log_path": str(log_path.relative_to(repo_root)),
        "started_at": now_iso(),
        "updated_at": now_iso(),
    }
    if extra:
        seed.update(extra)
    write_job(metadata_path, seed)
    runner_args = [
        sys.executable,
        "-u",
        "tools/dashboard_job_runner.py",
        "--repo-root", str(repo_root),
        "--job-id", job_id,
        "--jobs-dir", str(root),
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
        cwd=repo_root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )
    fallback = dict(seed)
    fallback["pid"] = proc.pid
    for _ in range(40):
        persisted = load_job_path(metadata_path)
        if persisted and str(persisted.get("job_id") or "") == job_id:
            return persisted
        if proc.poll() is not None:
            break
        time.sleep(0.05)
    fallback["status"] = "failed"
    fallback["returncode"] = proc.poll()
    fallback["completed_at"] = now_iso()
    fallback["status_note"] = "Dashboard-Runner konnte die Jobdatei nicht initialisieren."
    write_job(metadata_path, fallback)
    return fallback
