"""
import_die_dritte_chronik.py
============================

Zerlegt die Markdown-Quelle von *Die dritte Chronik* in Kapitelquellen
und DE-Szenen (chapter_as_scene) fuer den Export.

Beispiel:
    python tools/import_die_dritte_chronik.py
    python tools/import_die_dritte_chronik.py --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.book_project import find_book as find_book_project
from lib.output_paths import (
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
BOOK_ID = "die-dritte-chronik"

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
        if first in {title, raw_title_variants(title)} or first.casefold() == title.casefold():
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


def raw_title_variants(title: str) -> str:
    return title


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    book = find_book_project(REPO_ROOT, BOOK_ID)
    source_path = REPO_ROOT / book["source_path"]
    if not source_path.exists():
        print(f"FEHLER: Quelle nicht gefunden: {source_path}", file=sys.stderr)
        return 1

    source_text = source_path.read_text(encoding="utf-8")
    chapters = split_chapters(source_text)
    style = str(book.get("style_mode") or "stil-01-original")
    output_root = REPO_ROOT / book["work_dir"]
    status_path = REPO_ROOT / book["status_file"]

    print(f"=== {book['title']} ({BOOK_ID}) ===")
    print(f"Quelle: {source_path.relative_to(REPO_ROOT)}")
    print(f"Kapitel: {len(chapters)}")
    print("-" * 60)

    total_words = 0
    for idx, (title, body) in enumerate(chapters, 1):
        words = count_words(body)
        total_words += words
        print(f"{idx:03d}  {words:6,}  {title}")
    print("-" * 60)
    print(f"Summe: {total_words:,} Wörter")

    if args.dry_run:
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


if __name__ == "__main__":
    raise SystemExit(main())
