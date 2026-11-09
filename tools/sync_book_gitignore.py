#!/usr/bin/env python3
"""Schreibt den Git-Ausschluss fuer grosse Medien in books/<id>/.gitignore.

Muster kommen aus ``config/gitignore-assets.yaml``, der Schalter pro Buch aus
``book.yaml`` -> ``gitignore.large_assets``. Nur der zwischen den Markern
liegende Abschnitt wird angefasst; eigene Zeilen bleiben stehen.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from lib.book_project import find_book as find_book_project  # noqa: E402
from lib.gitignore_assets import (  # noqa: E402
    load_settings,
    write_gitignore,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "assets/master/, Audio, Video und Clips pro Buchpaket aus Git "
            "heraushalten."
        )
    )
    parser.add_argument(
        "--book",
        action="append",
        help="Buch-ID; mehrfach nutzbar. Ohne Angabe: alle Buchpakete.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Nur pruefen, nichts schreiben (Exit 1 bei Abweichung)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Aenderungen anzeigen, nicht schreiben",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    book_ids = args.book or sorted(
        path.parent.name
        for path in (REPO_ROOT / "books").glob("*/book.yaml")
    )
    if not book_ids:
        print("Keine Buchpakete gefunden.")
        return 0

    drifted = 0
    for book_id in book_ids:
        book = find_book_project(REPO_ROOT, book_id)
        settings = load_settings(book, REPO_ROOT)
        state = str(settings["state"])
        if state != "ok":
            drifted += 1
        label = f"{book_id:<26} {len(settings['patterns']):>2} Muster  {state}"
        if args.check or state == "ok":
            print(label)
            continue
        if args.dry_run:
            print(f"{label}  (dry-run, nicht geschrieben)")
            continue
        write_gitignore(book, REPO_ROOT)
        print(f"{label}  -> books/{book_id}/.gitignore")

    if args.check and drifted:
        print(f"\n{drifted} Buchpaket(e) ohne aktuellen Ausschluss.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
