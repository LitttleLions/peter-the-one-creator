"""
translate_batch.py
==================

Fuehrt mehrere Kapiteluebersetzungen hintereinander aus.
Die eigentliche Uebersetzung bleibt in translate_chapter.py.
"""

from __future__ import annotations

import argparse
import io
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.book_project import find_book as find_book_project
from lib.output_paths import (
    book_output_root,
    find_scene_translations,
    list_ru_scene_paths,
    parse_scene_number,
)
from lib.workbench_state import chapter_ids


REPO_ROOT = Path(__file__).resolve().parent.parent


def find_book(book_id: str | None) -> dict:
    return find_book_project(REPO_ROOT, book_id)


def chapter_range(all_ids: list[str], start: str | None, end: str | None) -> list[str]:
    if start is None and end is None:
        return all_ids
    start = start or all_ids[0]
    end = end or all_ids[-1]
    return [cid for cid in all_ids if start <= cid <= end]


def chapter_complete(book: dict, chapter_id: str, style: str) -> bool:
    output_root = book_output_root(REPO_ROOT, book)
    ru_paths = list_ru_scene_paths(output_root, chapter_id)
    if not ru_paths:
        return False
    de_map = find_scene_translations(output_root, chapter_id, style)
    ru_nums = [
        num for path in ru_paths
        if (num := parse_scene_number(path, chapter_id)) is not None
    ]
    return bool(ru_nums) and all(num in de_map for num in ru_nums)


def build_commands(
    book: dict,
    chapters: list[str],
    style: str,
    provider: str,
    model: str | None,
    overwrite: bool,
    auto_status: bool,
    no_review: bool,
) -> list[list[str]]:
    commands: list[list[str]] = []
    output_root = book_output_root(REPO_ROOT, book)
    for cid in chapters:
        if not list_ru_scene_paths(output_root, cid):
            commands.append([
                "tools/extract_scenes.py",
                "--book", book["id"],
                "--chapter", cid,
            ])
        if chapter_complete(book, cid, style) and not overwrite:
            continue
        cmd = [
            "tools/translate_chapter.py",
            "--book", book["id"],
            "--chapter", cid,
            "--style", style,
            "--provider", provider,
        ]
        if provider == "openrouter" and model:
            cmd.extend(["--model", model])
        if overwrite:
            cmd.append("--overwrite")
        if auto_status:
            cmd.append("--auto-status")
        if no_review:
            cmd.append("--no-review")
        commands.append(cmd)
    return commands


def build_assemble_commands(book: dict, chapters: list[str], style: str) -> list[list[str]]:
    return [
        [
            "tools/assemble_chapter.py",
            "--book", book["id"],
            "--chapter", cid,
            "--style", style,
        ]
        for cid in chapters
    ]


def run_command(cmd: list[str]) -> int:
    result = subprocess.run([sys.executable, *cmd], cwd=REPO_ROOT)
    return int(result.returncode)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Mehrere Kapitel uebersetzen.")
    ap.add_argument("--book", default=None)
    ap.add_argument("--style", default=None)
    ap.add_argument("--provider", choices=["openrouter", "prompt_file", "workspace_ai"], default="openrouter")
    ap.add_argument("--model", default=None)
    ap.add_argument("--chapter", default=None, help="Ein einzelnes Kapitel")
    ap.add_argument("--from", dest="from_chapter", default=None, help="Startkapitel")
    ap.add_argument("--to", dest="to_chapter", default=None, help="Endkapitel")
    ap.add_argument("--all", action="store_true", help="Alle Kapitel")
    ap.add_argument("--missing", action="store_true", help="Nur unvollstaendige Kapitel")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument(
        "--assemble-after",
        action="store_true",
        help="Nach dem Batch fuer jedes ausgewaehlte Kapitel assemble_chapter.py starten.",
    )
    ap.add_argument("--auto-status", action="store_true")
    ap.add_argument("--no-review", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    return ap.parse_args()


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    args = parse_args()
    book = find_book(args.book)
    style = args.style or book.get("style_mode", "stil-01-original")
    ids = chapter_ids(book, REPO_ROOT)
    if not ids:
        print("FEHLER: Keine Kapitel gefunden.", file=sys.stderr)
        return 1

    if args.chapter:
        selected = [args.chapter]
    elif args.all:
        selected = ids
    elif args.from_chapter or args.to_chapter:
        selected = chapter_range(ids, args.from_chapter, args.to_chapter)
    elif args.missing:
        selected = ids
    else:
        print("FEHLER: Gib --chapter, --from/--to, --all oder --missing an.", file=sys.stderr)
        return 2

    if args.missing:
        selected = [
            cid for cid in selected
            if not chapter_complete(book, cid, style)
        ]

    translate_commands = build_commands(
        book=book,
        chapters=selected,
        style=style,
        provider=args.provider,
        model=args.model,
        overwrite=args.overwrite,
        auto_status=args.auto_status,
        no_review=args.no_review,
    )
    assemble_commands = build_assemble_commands(book, selected, style) if args.assemble_after else []
    commands = translate_commands + assemble_commands

    print(f"=== Batch: {book['title']} ({book['id']}) ===")
    print(f"Kapitel: {len(selected)} ausgewaehlt")
    print(f"Style: {style}")
    print(f"Provider: {args.provider}")
    print("Ablauf: fehlende RU-Arbeitseinheiten vorbereiten, dann Uebersetzen/Prompt je Kapitel")
    print(f"Kapitel zusammensetzen: {'ja' if args.assemble_after else 'nein'}")
    print(f"Kommandos: {len(commands)}")
    if args.dry_run:
        print("(dry-run: keine Dateien geschrieben, keine API-Calls)")
    print()

    if not commands:
        print("Nichts zu tun.")
        return 0

    for idx, cmd in enumerate(commands, 1):
        text = " ".join(cmd)
        print(f"[{idx}/{len(commands)}] python {text}")
        if args.dry_run:
            continue
        code = run_command(cmd)
        if code != 0:
            print(f"ABBRUCH: Kommando fehlgeschlagen mit Code {code}", file=sys.stderr)
            return code
    return 0


if __name__ == "__main__":
    sys.exit(main())
