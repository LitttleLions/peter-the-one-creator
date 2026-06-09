"""
assemble_chapter.py
===================

Phase 3 der Pipeline: Baut aus einzelnen Szenen-Translationsdateien
eine komplette Kapitel-Sammeldatei.

Neue Struktur:
    books/<book-id>/work/scenes/de/<style>/NNN/scene-01.md
    books/<book-id>/work/assembled/<style>/NNN-translation-v1-<style>.md
"""

from __future__ import annotations

import argparse
import io
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.book_project import find_book as find_book_project
from lib.output_paths import (
    book_output_root,
    find_scene_translations,
    list_chapter_ids_with_ru_scenes,
    next_translation_path,
    source_chapter_path,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def find_book(book_id: str | None) -> dict:
    return find_book_project(REPO_ROOT, book_id)


def count_words(text: str) -> int:
    return len([w for w in text.split() if w])


def get_title_ru(output_root: Path, chapter_id: str) -> str:
    src = source_chapter_path(output_root, chapter_id)
    if not src.exists():
        return f"Kapitel {chapter_id}"
    for line in src.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    return f"Kapitel {chapter_id}"


def render_header(
    chapter_id: str,
    title_ru: str,
    book_title: str,
    mode: str,
    scene_count: int,
) -> str:
    out = [
        f"# Kapitel {chapter_id}: {title_ru}",
        "",
        f"*Buch: {book_title} - Alexei Tolstoi*",
        f"*Stil: **{mode}** (assemble aus {scene_count} Szenen)*",
        f"*Erstellt am: {datetime.now().isoformat(timespec='seconds')}*",
        "",
        "---",
        "",
    ]
    return "\n".join(out)


def assemble_chapter(
    output_root: Path,
    chapter_id: str,
    style: str,
    book_title: str,
    dry_run: bool = False,
) -> tuple[Path | None, int, list[int]]:
    scene_map = find_scene_translations(output_root, chapter_id, style)
    if not scene_map:
        print(f"  FEHLER: Keine Szenen-Translations fuer "
              f"{chapter_id} (style={style}) gefunden",
              file=sys.stderr)
        return None, 0, []

    sorted_nums = sorted(scene_map.keys())
    title_ru = get_title_ru(output_root, chapter_id)
    header = render_header(
        chapter_id, title_ru, book_title, style, len(sorted_nums)
    )

    parts = [header]
    words_total = 0
    for num in sorted_nums:
        path = scene_map[num]
        text = path.read_text(encoding="utf-8").strip()
        words_total += count_words(text)
        parts.append(f"## Szene {num}")
        parts.append("")
        parts.append(text)
        parts.append("")

    out_path = next_translation_path(output_root, chapter_id, style)
    if not dry_run:
        out_path.write_text("\n".join(parts) + "\n", encoding="utf-8")

    return out_path, words_total, []


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                          errors="replace")

    ap = argparse.ArgumentParser(
        description="Szenen-Translations zu Kapitel zusammenbauen."
    )
    ap.add_argument("--book", default=None,
                    help="Buch-ID (default: erstes Buchpaket)")
    ap.add_argument("--chapter", default=None,
                    help="Einzelnes Kapitel (z.B. '001')")
    ap.add_argument("--all", action="store_true",
                    help="Alle Kapitel zusammenbauen")
    ap.add_argument("--style", required=True,
                    help="Style-Profil/Output-Ordner")
    ap.add_argument("--dry-run", action="store_true",
                    help="Nur Struktur anzeigen, keine Dateien schreiben")
    args = ap.parse_args()

    if not args.chapter and not args.all:
        ap.error("Entweder --chapter oder --all angeben")

    book = find_book(args.book)
    output_root = book_output_root(REPO_ROOT, book)
    if not output_root.exists():
        print(f"FEHLER: {output_root} existiert nicht.", file=sys.stderr)
        return 1

    if args.all:
        chapter_ids = list_chapter_ids_with_ru_scenes(output_root)
    else:
        chapter_ids = [args.chapter]

    print(f"=== Buch: {book['title']} ({book['id']}) ===")
    print(f"Kapitel: {len(chapter_ids)}")
    print(f"Stil: {args.style}")
    print(f"Modus: {'dry-run' if args.dry_run else 'zusammenbauen'}")
    print()

    total_words = 0
    written = 0
    for cid in chapter_ids:
        print(f"--- Kapitel {cid} ---")
        out_path, words, _missing = assemble_chapter(
            output_root, cid, args.style, book["title"],
            dry_run=args.dry_run,
        )
        if out_path is None:
            continue
        marker = "  " if args.dry_run else "  OK"
        print(f"{marker} {out_path.relative_to(output_root)} "
              f"({words:,} Woerter)")
        total_words += words
        written += 1
        print()

    print(f"Ergebnis: {written}/{len(chapter_ids)} Kapitel, "
          f"{total_words:,} Woerter")
    if args.dry_run:
        print("(dry-run: keine Dateien geschrieben)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
