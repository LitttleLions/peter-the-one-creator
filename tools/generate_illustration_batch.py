#!/usr/bin/env python3
"""Batch wrapper for Higgsfield book illustrations."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from lib.book_project import find_book as find_book_project  # noqa: E402


def normalize_chapter(value: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError("Kapitel darf nicht leer sein.")
    return text.zfill(3) if text.isdigit() else text


def chapter_range(start: str, end: str | None) -> list[str]:
    first = normalize_chapter(start)
    last = normalize_chapter(end or start)
    if first.isdigit() and last.isdigit():
        first_num = int(first)
        last_num = int(last)
        if last_num < first_num:
            raise ValueError("--to darf nicht vor --from liegen.")
        return [f"{number:03d}" for number in range(first_num, last_num + 1)]
    if end and first != last:
        raise ValueError("Nichtnumerische Kapitelbereiche werden nicht unterstuetzt.")
    return [first]


def scene_numbers(book: dict, style: str, chapter: str) -> list[str]:
    book_root = Path(book["book_root"])
    scene_dir = book_root / "work" / "scenes" / "de" / style / chapter
    if not scene_dir.exists():
        return []
    numbers: list[str] = []
    for path in sorted(scene_dir.glob("scene-*.md")):
        stem = path.stem.removeprefix("scene-")
        if stem:
            numbers.append(stem)
    return numbers


def image_exists(book: dict, chapter: str, kind: str, scene: str | None) -> bool:
    book_root = Path(book["book_root"])
    suffixes = (".jpg", ".jpeg", ".png", ".webp")
    if kind == "chapter":
        base = book_root / "assets" / "chapter" / f"chapter-{chapter}"
    else:
        base = book_root / "assets" / "scene" / chapter / f"scene-{scene}"
    return any(base.with_suffix(suffix).exists() for suffix in suffixes)


def build_command(args: argparse.Namespace, chapter: str, kind: str, scene: str | None) -> list[str]:
    command = [
        sys.executable,
        "tools/generate_illustration.py",
        "--book",
        args.book,
        "--chapter",
        chapter,
        "--kind",
        kind,
    ]
    if scene:
        command.extend(["--scene", scene])
    passthrough = {
        "--style": args.style,
        "--model": args.model,
        "--moodboard": args.moodboard,
        "--aspect-ratio": args.aspect_ratio,
        "--quality": args.quality,
        "--backend": args.backend,
        "--soul-id": args.soul_id,
    }
    for flag, value in passthrough.items():
        if value:
            command.extend([flag, str(value)])
    for image in args.image or []:
        command.extend(["--image", image])
    if args.soul_strength is not None:
        command.extend(["--soul-strength", str(args.soul_strength)])
    if args.no_reference:
        command.append("--no-reference")
    if args.allow_paid_generation:
        command.append("--allow-paid-generation")
    if args.dry_run:
        command.append("--dry-run")
    if args.overwrite:
        command.append("--overwrite")
    return command


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Erzeugt Higgsfield-Illustrationen im Batch.")
    parser.add_argument("--book", required=True, help="Buch-ID")
    parser.add_argument("--chapter", help="Einzelnes Kapitel, z. B. 001")
    parser.add_argument("--from", dest="start_chapter", help="Erstes Kapitel")
    parser.add_argument("--to", dest="end_chapter", help="Letztes Kapitel")
    parser.add_argument("--style", help="Style-Slug; Default aus book.yaml")
    parser.add_argument("--kind", choices=("scene", "chapter", "both"), default="scene")
    parser.add_argument("--missing", action="store_true", help="Vorhandene Zielbilder ueberspringen")
    parser.add_argument("--model")
    parser.add_argument("--moodboard")
    parser.add_argument("--image", action="append", default=[])
    parser.add_argument("--no-reference", action="store_true")
    parser.add_argument("--aspect-ratio")
    parser.add_argument("--quality")
    parser.add_argument("--backend", choices=("cli", "api", "auto"))
    parser.add_argument("--soul-id")
    parser.add_argument("--soul-strength", type=float)
    parser.add_argument("--allow-paid-generation", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.chapter and not args.start_chapter:
        raise SystemExit("Nutze --chapter oder --from/--to.")
    if args.chapter and args.start_chapter:
        raise SystemExit("Nutze entweder --chapter oder --from/--to, nicht beides.")

    book = find_book_project(REPO_ROOT, args.book)
    style = args.style or str(book.get("style_mode") or "stil-01-original")
    chapters = chapter_range(args.chapter or args.start_chapter, args.end_chapter)
    kinds = ["chapter", "scene"] if args.kind == "both" else [args.kind]
    total = 0
    skipped = 0

    for chapter in chapters:
        for kind in kinds:
            scenes = [None] if kind == "chapter" else scene_numbers(book, style, chapter)
            if kind == "scene" and not scenes:
                print(f"[{chapter}] Keine DE-Szenen fuer Stil {style} gefunden; uebersprungen.", flush=True)
                continue
            for scene in scenes:
                label = f"{chapter} {kind}" + (f" {scene}" if scene else "")
                if args.missing and image_exists(book, chapter, kind, scene):
                    skipped += 1
                    print(f"[{label}] Zielbild vorhanden; uebersprungen.", flush=True)
                    continue
                command = build_command(args, chapter, kind, scene)
                print(f"[{label}] Starte: {' '.join(command)}", flush=True)
                result = subprocess.run(command, cwd=REPO_ROOT)
                if result.returncode != 0:
                    return result.returncode
                total += 1

    print(f"Batch fertig: {total} erzeugt/geplant, {skipped} uebersprungen.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
