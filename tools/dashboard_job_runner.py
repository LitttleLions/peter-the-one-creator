"""
dashboard_job_runner.py
=======================

Small wrapper for dashboard background jobs.

It owns the visible job status file while the child command runs and writes a
final status when the child exits. This avoids stale "laeuft" states in
Streamlit when the child process has already completed.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a dashboard background job.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--job-file", required=True)
    parser.add_argument("--log-path", required=True)
    parser.add_argument("--book-id", required=True)
    parser.add_argument("--style", required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--kind", default="batch")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        parser.error("missing child command after --")
    return args


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    job_file = Path(args.job_file)
    log_path = Path(args.log_path)
    if not log_path.is_absolute():
        log_path = repo_root / log_path
    if not job_file.is_absolute():
        job_file = repo_root / job_file

    command = [str(part) for part in args.command]
    job = {
        "pid": os.getpid(),
        "child_pid": None,
        "book_id": args.book_id,
        "style": args.style,
        "provider": args.provider,
        "kind": args.kind,
        "status": "running",
        "returncode": None,
        "command": command,
        "log_path": str(log_path.relative_to(repo_root)),
        "started_at": datetime.now().isoformat(timespec="seconds"),
    }
    write_json(job_file, job)

    log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with log_path.open("w", encoding="utf-8") as log_handle:
            child_env = os.environ.copy()
            child_env["PYTHONUNBUFFERED"] = "1"
            child = subprocess.Popen(
                command,
                cwd=repo_root,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                text=True,
                env=child_env,
            )
            job["child_pid"] = child.pid
            write_json(job_file, job)
            returncode = child.wait()
    except Exception as exc:
        job["status"] = "failed"
        job["returncode"] = 1
        job["completed_at"] = datetime.now().isoformat(timespec="seconds")
        job["error"] = str(exc)
        write_json(job_file, job)
        return 1

    job["status"] = "completed" if returncode == 0 else "failed"
    job["returncode"] = returncode
    job["completed_at"] = datetime.now().isoformat(timespec="seconds")
    write_json(job_file, job)
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
