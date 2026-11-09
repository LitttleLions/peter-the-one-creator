"""
import_de_original.py
======================

Zerlegt die Markdown-Quelle eines **deutschen Originals** in Kapitelquellen
und DE-Szenen (chapter_as_scene) fuer den Export. Ohne LLM, ohne Kosten.

Voraussetzungen in book.yaml:
    source_lang: de
    target_lang: de
    structure.mode: chapter_as_scene

Kapitelgrenze ist die `## `-Ueberschrift der Quelle (Ebene 2). Text vor der
ersten `##`-Ueberschrift (Titelblock, Genrezeile) wird nicht als Kapitel
gefuehrt.

Beispiel:
    python tools/import_de_original.py --book die-dritte-chronik
    python tools/import_de_original.py --book der-lotse --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.book_project import find_book as find_book_project
from lib.output_paths import (
    book_output_root,
    de_scene_path,
    source_chapter_path,
    source_scene_path,
)
from lib.status_manager import (
    STATUS_DONE,
    ChapterState,
    add_chapter,
    new_book_state,
    now_iso,
    save_state,
)


REPO_ROOT = Path(__file__).resolve().parent.parent

CHAPTER_SPLIT_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
NUMBERED_PREFIX_RE = re.compile(r"^\d+\.\s+")
KAPITEL_PREFIX_RE = re.compile(
    r"^Kapitel\s+\d+\s*[–—:\-]\s*(.+)$",
    re.IGNORECASE,
)
WORD_RE = re.compile(r"\w+", re.UNICODE)


def literary_title(raw: str) -> str:
    title = raw.strip()
    title = NUMBERED_PREFIX_RE.sub("", title).strip()
    match = KAPITEL_PREFIX_RE.match(title)
    if match:
        return match.group(1).strip()
    return title


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def normalize_body(title: str, body: str) -> str:
    lines = body.replace("\r\n", "\n").split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    # Doppelte Titelzeile direkt nach dem Heading entfernen
    if lines:
        first = lines[0].strip().strip("*").strip()
        if first.casefold() == title.casefold():
            lines.pop(0)
            while lines and not lines[0].strip():
                lines.pop(0)
        elif first.startswith("# ") and literary_title(first[2:]).casefold() == title.casefold():
            lines.pop(0)
            while lines and not lines[0].strip():
                lines.pop(0)

    # Trennlinien am Anfang entfernen
    while lines and lines[0].strip() in {"---", "***", "* * *"}:
        lines.pop(0)
        while lines and not lines[0].strip():
            lines.pop(0)

    text = "\n".join(lines).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def split_chapters(source_text: str) -> list[tuple[str, str]]:
    matches = list(CHAPTER_SPLIT_RE.finditer(source_text))
    if not matches:
        raise SystemExit("Keine ##-Kapitelueberschriften in der Quelle gefunden.")

    chapters: list[tuple[str, str]] = []
    for idx, match in enumerate(matches):
        raw_heading = match.group(1).strip()
        title = literary_title(raw_heading)
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(source_text)
        body = normalize_body(title, source_text[start:end])
        if not body:
            raise SystemExit(f"Leerer Kapitelkoerper nach Heading: {raw_heading}")
        chapters.append((title, body))
    return chapters


def render_chapter_source(chapter_id: str, title: str, body: str, book_title: str) -> str:
    return "\n".join(
        [
            f"# {title}",
            "",
            f"*Buch: {book_title}*",
            f"*Kapitel-ID: {chapter_id}*",
            "",
            "---",
            "",
            body,
            "",
        ]
    )


def render_scene(title: str, body: str) -> str:
    return "\n".join([f"## {title}", "", body, ""])


def check_book(book: dict) -> None:
    if str(book.get("source_lang") or "") != "de" or str(book.get("target_lang") or "") != "de":
        raise SystemExit(
            "Dieses Tool ist nur fuer deutsche Originale "
            f"(source_lang/target_lang: de). Buch {book['id']} ist "
            f"{book.get('source_lang')} -> {book.get('target_lang')}."
        )
    structure = book.get("structure") or {}
    mode = str(structure.get("mode") or "")
    if mode != "chapter_as_scene":
        raise SystemExit(
            f"structure.mode muss 'chapter_as_scene' sein, ist aber '{mode}'."
        )


def import_book(book_id: str, dry_run: bool = False) -> int:
    book = find_book_project(REPO_ROOT, book_id)
    check_book(book)
    source_path = REPO_ROOT / book["source_path"]
    if not source_path.exists():
        print(f"FEHLER: Quelle nicht gefunden: {source_path}", file=sys.stderr)
        return 1

    source_text = source_path.read_text(encoding="utf-8")
    chapters = split_chapters(source_text)
    style = str(book.get("style_mode") or "stil-01-original")
    output_root = book_output_root(REPO_ROOT, book)
    status_path = REPO_ROOT / book["status_file"]

    print(f"=== {book['title']} ({book['id']}) ===")
    print(f"Quelle: {source_path.relative_to(REPO_ROOT)}")
    print(f"Stil:   {style}")
    print(f"Kapitel: {len(chapters)}")
    print("-" * 60)

    total_words = 0
    for idx, (title, body) in enumerate(chapters, 1):
        words = count_words(body)
        total_words += words
        print(f"{idx:03d}  {words:6,}  {title}")
    print("-" * 60)
    print(f"Summe: {total_words:,} Wörter")

    if dry_run:
        print("(dry-run: keine Dateien geschrieben)")
        return 0

    state = new_book_state(book)
    for idx, (title, body) in enumerate(chapters, 1):
        chapter_id = f"{idx:03d}"
        words = count_words(body)

        chapter_path = source_chapter_path(output_root, chapter_id)
        chapter_path.parent.mkdir(parents=True, exist_ok=True)
        chapter_path.write_text(
            render_chapter_source(chapter_id, title, body, book["title"]),
            encoding="utf-8",
        )

        # Quellszene (source_lang=de) und Exportszene (de/<style>)
        src_scene = source_scene_path(output_root, chapter_id, 1, "de")
        src_scene.parent.mkdir(parents=True, exist_ok=True)
        scene_text = render_scene(title, body)
        src_scene.write_text(scene_text, encoding="utf-8")

        de_scene = de_scene_path(output_root, chapter_id, 1, style)
        de_scene.parent.mkdir(parents=True, exist_ok=True)
        de_scene.write_text(scene_text, encoding="utf-8")

        add_chapter(
            state,
            ChapterState(
                id=chapter_id,
                title_ru=title,
                title_de=title,
                status=STATUS_DONE,
                words_source=words,
                words_target=words,
                completed_at=now_iso(),
            ),
        )

    status_path.parent.mkdir(parents=True, exist_ok=True)
    save_state(state, status_path)

    print()
    print(f"Kapitelquellen: {output_root / 'chapters'}")
    print(f"DE-Szenen:      {output_root / 'scenes' / 'de' / style}")
    print(f"Status:         {status_path.relative_to(REPO_ROOT)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Markdown-Quelle eines DE-Originals in Kapitel + DE-Szenen zerlegen.",
    )
    parser.add_argument("--book", required=True, help="Buch-ID, z.B. der-lotse")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    return import_book(args.book, dry_run=args.dry_run)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main())
