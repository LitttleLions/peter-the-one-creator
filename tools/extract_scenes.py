"""
extract_scenes.py
=================

Zerlegt eine oder alle NNN-source.md-Dateien in einzelne russische
Szenen-Dateien.

Neue Struktur:
    books/<book-id>/work/chapters/NNN-source.md
    books/<book-id>/work/scenes/ru/NNN/scene-01.md
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.book_project import find_book as find_book_project
from lib.output_paths import (
    book_output_root,
    chapters_dir,
    ru_scene_path,
)
from lib.scene_splitter import Scene, count_words, split_into_scenes


REPO_ROOT = Path(__file__).resolve().parent.parent


def find_book(book_id: str | None) -> dict:
    return find_book_project(REPO_ROOT, book_id)


def scene_file_path(output_root: Path, chapter_id: str,
                    scene_number: int) -> Path:
    return ru_scene_path(output_root, chapter_id, scene_number)


def source_body_as_single_scene(src_path: Path) -> Scene:
    """Fallback fuer Kapitel ohne explizite Szenenmarker."""
    lines = []
    for line in src_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        if stripped.startswith("# "):
            continue
        if stripped.startswith("*Buch:"):
            continue
        if stripped.startswith("<!-- status:"):
            continue
        lines.append(line.rstrip())
    text = "\n".join(lines).strip()
    text = text if text else src_path.read_text(encoding="utf-8").strip()
    return Scene(number=1, title="", text=text)


def extract_scenes_for_chapter(
    output_root: Path,
    chapter_id: str,
    structure_mode: str = "scenes",
    dry_run: bool = False,
) -> list[dict]:
    source_dir = chapters_dir(output_root)
    src_path = source_dir / f"{chapter_id}-source.md"
    if not src_path.exists():
        print(f"  FEHLER: {src_path} nicht gefunden", file=sys.stderr)
        return []

    if structure_mode == "chapter_as_scene":
        scenes = [source_body_as_single_scene(src_path)]
    else:
        _frontmatter, scenes = split_into_scenes(src_path)

    if not scenes:
        print(f"  WARNUNG: Keine Szenen in {src_path} erkannt",
              file=sys.stderr)
        scenes = [source_body_as_single_scene(src_path)]

    results = []
    for sc in scenes:
        sf = scene_file_path(output_root, chapter_id, sc.number)
        wc = count_words(sc.text)
        results.append({
            "number": sc.number,
            "title": sc.title,
            "words": wc,
            "path": sf,
            "text": sc.text,
        })
        if not dry_run:
            sf.parent.mkdir(parents=True, exist_ok=True)
            sf.write_text(sc.text + "\n", encoding="utf-8")

    return results


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                          errors="replace")

    ap = argparse.ArgumentParser(
        description="Kapitel in russische Szenen-Dateien zerlegen."
    )
    ap.add_argument("--book", default=None,
                    help="Buch-ID (default: erstes Buchpaket)")
    ap.add_argument("--chapter", default=None,
                    help="Einzelnes Kapitel (z.B. '001')")
    ap.add_argument("--all", action="store_true",
                    help="Alle Kapitel zerlegen")
    ap.add_argument("--dry-run", action="store_true",
                    help="Nur Struktur anzeigen, keine Dateien schreiben")
    args = ap.parse_args()

    if not args.chapter and not args.all:
        ap.error("Entweder --chapter oder --all angeben")

    book = find_book(args.book)
    structure = book.get("structure") or {}
    structure_mode = str(structure.get("mode") or "scenes")
    output_root = book_output_root(REPO_ROOT, book)
    source_dir = chapters_dir(output_root)

    if not source_dir.exists():
        print(f"FEHLER: {source_dir} existiert nicht. "
              f"Zuerst extract_chapters.py ausfuehren.", file=sys.stderr)
        return 1

    if args.all:
        source_files = sorted(source_dir.glob("*-source.md"))
        chapter_ids = [p.stem.replace("-source", "") for p in source_files]
    else:
        chapter_ids = [args.chapter]

    print(f"=== Buch: {book['title']} ({book['id']}) ===")
    print(f"Kapitel: {len(chapter_ids)}")
    print(f"Struktur: {structure_mode}")
    print(f"Modus: {'dry-run' if args.dry_run else 'extrahiere'}")
    print()

    total_scenes = 0
    total_words = 0

    for cid in chapter_ids:
        print(f"--- Kapitel {cid} ---")
        results = extract_scenes_for_chapter(
            output_root,
            cid,
            structure_mode=structure_mode,
            dry_run=args.dry_run,
        )
        if not results:
            continue

        for r in results:
            marker = "  " if args.dry_run else "  OK"
            title_part = f" - {r['title']}" if r["title"] else ""
            print(f"{marker} Szene {r['number']:02d}: "
                  f"{r['words']:,} Woerter{title_part}")
            if not args.dry_run:
                print(f"      -> {r['path'].relative_to(output_root)}")

        total_scenes += len(results)
        total_words += sum(r["words"] for r in results)
        print()

    print(f"Ergebnis: {total_scenes} Szenen in {len(chapter_ids)} "
          f"Kapiteln ({total_words:,} Woerter)")
    if args.dry_run:
        print("(dry-run: keine Dateien geschrieben)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
