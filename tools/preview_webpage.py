#!/usr/bin/env python
"""Serve webpage/dist/ locally (Vite preview). Do not open index.html via file://.

Usage:
    python tools/preview_webpage.py
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
    candidates = ["npm.cmd", "npm"] if os.name == "nt" else ["npm"]
    for name in candidates:
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit("npm nicht gefunden. Node.js installieren und neues Terminal oeffnen.")


def main() -> int:
    dist = WEBPAGE_ROOT / "dist" / "index.html"
    if not dist.is_file():
        print("Noch kein Build. Zuerst: python tools/build_webpage_dist.py", flush=True)
        raise SystemExit(1)

    npm = resolve_npm()
    print("Vorschau: http://127.0.0.1:4173", flush=True)
    print("(file:// funktioniert nicht — Browser blockiert ES-Module.)", flush=True)
    subprocess.run([npm, "run", "preview", "--", "--host", "127.0.0.1", "--port", "4173"], cwd=WEBPAGE_ROOT, check=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode or 1)
