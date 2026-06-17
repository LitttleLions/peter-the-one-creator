"""
apply_review_suggestions.py
===========================

Staged Fix-Lauf fuer Review-Befunde.

Plan und Stage schreiben nur unter work/review-fixes/<style>/.
Produktive Szenendateien werden ausschliesslich mit --promote geaendert.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from assemble_chapter import assemble_chapter
from lib.book_project import find_book as find_book_project
from lib.review_fixes import (
    build_fix_plan,
    fix_plan_path,
    fixes_root,
    manifest_path,
    manual_review_path,
    promote_staged_fixes,
    render_plan_text,
    stage_fixes,
    write_plan_artifacts,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plant, staged oder uebernimmt sichere Review-Ersetzungen."
    )
    parser.add_argument("--book", required=True, help="Buch-ID")
    parser.add_argument("--style", required=True, help="Zu reparierender Stil")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true", help="Nur Fix-Plan ausgeben")
    mode.add_argument("--stage", action="store_true", help="Kandidaten erzeugen")
    mode.add_argument("--promote", action="store_true", help="Gepruefte Kandidaten uebernehmen")
    return parser.parse_args()


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    args = parse_args()
    book = find_book_project(REPO_ROOT, args.book)

    print(f"=== Review-Fixes: {book['title']} ({book['id']}) ===")
    print(f"Stil: {args.style}")
    print()

    if args.plan:
        _summary, staged, manual = build_fix_plan(REPO_ROOT, book, args.style)
        write_plan_artifacts(REPO_ROOT, book, args.style, staged, manual)
        print(render_plan_text(staged, manual))
        print(f"Plan: {fix_plan_path(REPO_ROOT, book, args.style).relative_to(REPO_ROOT)}")
        print(f"Manuell: {manual_review_path(REPO_ROOT, book, args.style).relative_to(REPO_ROOT)}")
        return 0

    if args.stage:
        manifest = stage_fixes(REPO_ROOT, book, args.style)
        applied = sum(len(item.applied) for item in manifest.staged)
        print(f"Kandidaten: {len(manifest.staged)} Szene(n)")
        print(f"Ersetzungen: {applied}")
        print(f"Manifest: {manifest_path(REPO_ROOT, book, args.style).relative_to(REPO_ROOT)}")
        print(f"Manuell: {manual_review_path(REPO_ROOT, book, args.style).relative_to(REPO_ROOT)}")
        print(f"Root: {fixes_root(REPO_ROOT, book, args.style).relative_to(REPO_ROOT)}")
        return 0

    if args.promote:
        report = promote_staged_fixes(
            REPO_ROOT,
            book,
            args.style,
            assemble_func=assemble_chapter,
        )
        print(f"Uebernommen: {report.promoted}")
        print(f"Uebersprungen: {report.skipped}")
        if report.assembled_chapters:
            print("Neu zusammengesetzt:")
            for path in report.assembled_chapters:
                print(f"- {path}")
        for item in report.items:
            if item.status != "promoted":
                print(
                    f"SKIP {item.chapter}/{item.scene:02d}: {item.message}",
                    file=sys.stderr,
                )
        return 0 if report.skipped == 0 else 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
