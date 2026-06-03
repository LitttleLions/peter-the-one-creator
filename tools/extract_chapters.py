"""
extract_chapters.py
===================

Liest eine RTF-Quelldatei (z. B. .doc mit RTF-Inhalt), zerlegt sie an
den Heading-Markern in Kapitel und schreibt pro Kapitel eine
Markdown-Datei in das Output-Verzeichnis.

Außerdem wird die Status-JSON-Datei initialisiert, falls noch nicht
vorhanden.

Verwendung:
    python tools/extract_chapters.py [--book peter-i-buch-01]

Wenn --book fehlt, wird der erste Eintrag aus config/books.yaml
genommen.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

# Tools-Verzeichnis auf den Pfad setzen
sys.path.insert(0, str(Path(__file__).parent))

import yaml
from lib.rtf_parser import parse_rtf, extract_chapter_titles, Block
from lib.status_manager import (
    BookState, ChapterState, new_book_state, save_state, add_chapter,
    STATUS_PENDING,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def load_books_registry() -> list[dict]:
    p = REPO_ROOT / "config" / "books.yaml"
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    return data.get("books", [])


def find_book(book_id: str | None) -> dict:
    books = load_books_registry()
    if book_id is None:
        if not books:
            raise SystemExit("Keine Bücher in config/books.yaml")
        return books[0]
    for b in books:
        if b["id"] == book_id:
            return b
    raise SystemExit(f"Buch mit id={book_id} nicht gefunden")


def chapter_id(idx: int) -> str:
    return f"{idx:03d}"


def chapter_slug(idx: int, title: str) -> str:
    s = title.lower().strip()
    out = []
    for word in s.split():
        cleaned = "".join(c for c in word if c.isalnum())
        if cleaned:
            out.append(cleaned)
        if len(out) >= 4:
            break
    slug = "-".join(out) or "kapitel"
    return f"{chapter_id(idx)}-{slug}"[:80]


def build_chapter_segments(blocks: list[Block]) -> list[tuple[str, list[Block]]]:
    """
    Zerlegt die Blockliste in Kapitel-Segmente.

    Strategie: Wir wählen das "feinste" Heading-Level, das mehrfach
    vorkommt (= mutmaßliche Kapitelebene, "Глава X"). Alles
    dazwischen gehört zu einem Kapitel.
    """
    headings = extract_chapter_titles(blocks)
    if not headings:
        return []

    levels = sorted({lvl for _, lvl, _ in headings})
    target_level = None
    for lvl in reversed(levels):
        cnt = sum(1 for _, l, _ in headings if l == lvl)
        if cnt >= 2:
            target_level = lvl
            break
    if target_level is None:
        target_level = levels[0]

    segments: list[tuple[str, list[Block]]] = []
    current_title: str | None = None
    current_buf: list[Block] = []

    for b in blocks:
        if b.kind == "heading":
            if b.level == target_level:
                if current_title is not None:
                    segments.append((current_title, current_buf))
                current_title = b.text
                current_buf = []
            else:
                if current_title is None:
                    # Vor dem ersten Kapitel: ignorieren (Frontmatter)
                    continue
                current_buf.append(b)
        else:
            if current_title is None:
                continue
            current_buf.append(b)

    if current_title is not None:
        segments.append((current_title, current_buf))

    return segments


def render_chapter_md(title: str, blocks: list[Block], idx: int,
                      book_title: str) -> str:
    lines = []
    lines.append(f"# Kapitel {idx}: {title}")
    lines.append("")
    lines.append(f"*Buch: {book_title}*")
    lines.append("")
    lines.append("<!-- status: pending -->")
    lines.append("")
    for b in blocks:
        if b.kind == "blank":
            lines.append("")
        elif b.kind == "heading":
            lines.append(f"## {b.text}")
            lines.append("")
        elif b.kind == "paragraph":
            lines.append(b.text)
            lines.append("")
    return "\n".join(lines)


def count_words(s: str) -> int:
    return len([w for w in s.split() if w])


def main() -> int:
    # UTF-8 für stdout (Windows cmd kann sonst keine Kyrillica ausgeben)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                          errors="replace")

    ap = argparse.ArgumentParser()
    ap.add_argument("--book", default=None)
    ap.add_argument("--dry-run", action="store_true",
                    help="Nur Inhaltsübersicht, keine Dateien schreiben")
    args = ap.parse_args()

    book = find_book(args.book)
    print(f"=== Buch: {book['title']} ({book['id']}) ===")
    print(f"Quelle: {book['source_path']}")
    print(f"Stilmodus: {book.get('style_mode', 'stylized')}")
    print(f"Regelwerk: {'AN' if book.get('ruleset_apply', True) else 'AUS'}")
    print()

    src = REPO_ROOT / book["source_path"]
    if not src.exists():
        print(f"FEHLER: Quelldatei nicht gefunden: {src}")
        return 1

    print(f"Lese RTF… ({src.stat().st_size:,} bytes)")
    blocks, meta = parse_rtf(src)
    print(f"Blöcke: {meta['blocks_total']:,}  |  Headings: {meta['headings_total']:,}")
    print()

    segments = build_chapter_segments(blocks)
    print(f"Erkannte Kapitel: {len(segments)}")
    print("-" * 60)
    print(f"{'#':>3}  {'Lvl':>3}  {'Wörter':>7}  Titel")
    print("-" * 60)
    total_words = 0
    for i, (title, blk) in enumerate(segments, 1):
        text = "\n".join(b.text for b in blk if b.kind != "blank")
        wc = count_words(text)
        total_words += wc
        lvl = 0
        for b in blk:
            if b.kind == "heading":
                lvl = b.level
                break
        print(f"{i:>3}  {lvl:>3}  {wc:>7,}  {title[:60]}")
    print("-" * 60)
    print(f"Summe: {total_words:,} Wörter in {len(segments)} Kapiteln")
    print()

    if args.dry_run:
        print("(dry-run: keine Dateien geschrieben)")
        return 0

    # Status-Datei initialisieren
    status_path = REPO_ROOT / book["status_file"]
    if status_path.exists():
        print(f"Status-Datei existiert bereits: {status_path}")
        state = BookState.from_json(status_path.read_text(encoding="utf-8"))
    else:
        state = new_book_state(book)
        print(f"Neue Status-Datei: {status_path}")

    existing_ids = {c.id for c in state.chapters}
    for i, (title, blk) in enumerate(segments, 1):
        cid = chapter_id(i)
        if cid in existing_ids:
            for c in state.chapters:
                if c.id == cid:
                    c.title_ru = title
                    break
        else:
            text = "\n".join(b.text for b in blk if b.kind != "blank")
            ch = ChapterState(
                id=cid,
                title_ru=title,
                status=STATUS_PENDING,
                words_source=count_words(text),
            )
            add_chapter(state, ch)

    save_state(state, status_path)
    print(f"Status aktualisiert: {len(state.chapters)} Kapitel-Einträge")
    print()

    chapters_dir = REPO_ROOT / book["output_dir"] / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)
    for i, (title, blk) in enumerate(segments, 1):
        cid = chapter_id(i)
        md = render_chapter_md(title, blk, i, book["title"])
        path = chapters_dir / f"{cid}-source.md"
        path.write_text(md, encoding="utf-8")
    print(f"Quell-Kapitel geschrieben: {chapters_dir}  ({len(segments)} Dateien)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
