#!/usr/bin/env python
"""Build the Motivatier shelf production site under webpage/dist/.

Runs ``npm install`` when node_modules is missing, then ``npm run build``
inside ``webpage/`` (not ``webapp/`` — that is the dashboard frontend).

Usage:
    python tools/build_webpage_dist.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WEBPAGE_ROOT = REPO_ROOT / "webpage"


def resolve_npm() -> str:
    """Find npm executable (Windows needs npm.cmd; bare 'npm' fails in CreateProcess)."""
    candidates = ["npm.cmd", "npm"] if os.name == "nt" else ["npm"]
    for name in candidates:
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit(
        "npm wurde nicht gefunden. Node.js installieren und ein neues Terminal oeffnen, "
        "oder PATH pruefen. Dann erneut: python tools/build_webpage_dist.py"
    )


def run(command: list[str], cwd: Path) -> None:
    print(f"$ {' '.join(command)}  (cwd={cwd})", flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    if not WEBPAGE_ROOT.is_dir():
        raise SystemExit(f"webpage/ fehlt: {WEBPAGE_ROOT}")
    if not (WEBPAGE_ROOT / "package.json").is_file():
        raise SystemExit(f"package.json fehlt in {WEBPAGE_ROOT}")

    npm = resolve_npm()
    node_modules = WEBPAGE_ROOT / "node_modules"
    if not node_modules.is_dir():
        print("node_modules fehlt; fuehre npm install in webpage/ aus.", flush=True)
        run([npm, "install"], WEBPAGE_ROOT)

    run([npm, "run", "build"], WEBPAGE_ROOT)
    dist = WEBPAGE_ROOT / "dist"
    print(f"Fertig: {dist}", flush=True)
    print("Nicht per file:// oeffnen — lokalen Server nutzen:", flush=True)
    print("  python tools/preview_webpage.py", flush=True)
    print("  oder: cd webpage && npm run preview", flush=True)
    print("Deploy: Inhalt von webpage/dist/ auf die Domain kopieren.", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"Build fehlgeschlagen (exit {exc.returncode}).", file=sys.stderr, flush=True)
        raise SystemExit(exc.returncode or 1)
