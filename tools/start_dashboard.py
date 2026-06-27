#!/usr/bin/env python
"""Start the FastAPI/React dashboard as a local single-process app."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = REPO_ROOT / "webapp" / "frontend"
FRONTEND_DIST = FRONTEND_ROOT / "dist"


def run(command: list[str], cwd: Path) -> None:
    print(f"$ {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def ensure_frontend_build(force: bool) -> None:
    index_path = FRONTEND_DIST / "index.html"
    if index_path.exists() and not force:
        return
    if not FRONTEND_ROOT.exists():
        raise SystemExit(f"Frontend-Verzeichnis fehlt: {FRONTEND_ROOT}")
    node_modules = FRONTEND_ROOT / "node_modules"
    if not node_modules.exists():
        print("node_modules fehlt; fuehre npm install aus.", flush=True)
        run(["npm", "install"], FRONTEND_ROOT)
    run(["npm", "run", "build"], FRONTEND_ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build and start the local FastAPI/React dashboard."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default="8000")
    parser.add_argument(
        "--build",
        action="store_true",
        help="Frontend-Build immer neu erzeugen.",
    )
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="Frontend-Build nicht pruefen oder erzeugen.",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Uvicorn im Reload-Modus starten.",
    )
    args = parser.parse_args()

    if not args.no_build:
        ensure_frontend_build(force=args.build)

    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "webapp.backend.main:app",
        "--host",
        args.host,
        "--port",
        str(args.port),
    ]
    if args.reload:
        command.append("--reload")

    print(f"Dashboard: http://{args.host}:{args.port}", flush=True)
    subprocess.run(command, cwd=REPO_ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
