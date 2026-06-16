"""
extract_wolnelektury_epub.py
============================

Extrahiert eine Wolne-Lektury-EPUB als Buchpaket-Arbeitsgrundlage.

Das Tool ist bewusst auf die saubere Wolne-Lektury-Struktur zugeschnitten:
TOC/NCX bestimmt die Reihenfolge, Anmerkungsanker werden entfernt, Spenden-,
Navigations- und Redaktionsseiten werden ignoriert.
"""

from __future__ import annotations

import argparse
import io
import re
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime
from html import unescape
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).parent))

from lib.book_project import find_book as find_book_project
from lib.output_paths import book_output_root, chapters_dir, source_scene_path
from lib.status_manager import (
    ChapterState,
    new_book_state,
    save_state,
    STATUS_PENDING,
)
from lib.scene_splitter import count_words


REPO_ROOT = Path(__file__).resolve().parent.parent
XHTML_NS = "{http://www.w3.org/1999/xhtml}"
NCX_NS = "{http://www.daisy.org/z3986/2005/ncx/}"


@dataclass
class WorkUnit:
    chapter_id: str
    source_title: str
    display_title: str
    epub_path: str
    body: str
    words: int


def find_book(book_id: str | None) -> dict:
    return find_book_project(REPO_ROOT, book_id)


def ns_tag(name: str) -> str:
    return f"{XHTML_NS}{name}"


def strip_text(value: str) -> str:
    value = unescape(value)
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def roman_to_int(value: str) -> int:
    numerals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
    total = 0
    prev = 0
    for char in reversed(value.upper()):
        current = numerals.get(char, 0)
        if current < prev:
            total -= current
        else:
            total += current
            prev = current
    return total


def toc_entries(zf: zipfile.ZipFile) -> list[tuple[str, str]]:
    tree = ET.fromstring(zf.read("EPUB/toc.ncx"))
    entries: list[tuple[str, str]] = []
    for nav_point in tree.findall(f".//{NCX_NS}navPoint"):
        text_el = nav_point.find(f"./{NCX_NS}navLabel/{NCX_NS}text")
        content_el = nav_point.find(f"./{NCX_NS}content")
        if text_el is None or content_el is None:
            continue
        src = (content_el.get("src") or "").split("#", 1)[0]
        label = strip_text("".join(text_el.itertext()))
        if src.startswith("part") and label:
            entries.append((label, f"EPUB/{src}"))
    return entries


def remove_annotation_anchors(root: ET.Element) -> None:
    for parent in list(root.iter()):
        children = list(parent)
        for index, child in enumerate(children):
            if child.tag != ns_tag("a"):
                continue
            href = child.get("href") or ""
            css_class = child.get("class") or ""
            if "annotations.xhtml" not in href and "anchor" not in css_class:
                continue
            replacement_text = child.tail or ""
            if index == 0:
                parent.text = (parent.text or "") + replacement_text
            else:
                prev = children[index - 1]
                prev.tail = (prev.tail or "") + replacement_text
            parent.remove(child)


def extract_body(zf: zipfile.ZipFile, epub_path: str) -> tuple[str, str]:
    root = ET.fromstring(zf.read(epub_path))
    remove_annotation_anchors(root)
    book_text = root.find(f".//*[@id='book-text']")
    scope = book_text if book_text is not None else root.find(f".//{ns_tag('body')}")
    if scope is None:
        return "", ""
    headings = []
    for level in range(1, 7):
        headings.extend(scope.findall(f".//{ns_tag(f'h{level}')}"))
    source_title = strip_text(" ".join("".join(h.itertext()) for h in headings[:1]))
    paragraphs: list[str] = []
    for paragraph in scope.findall(f".//{ns_tag('p')}"):
        text = strip_text("".join(paragraph.itertext()))
        if text and text != "WolneLektury.pl":
            paragraphs.append(text)
    return source_title, "\n\n".join(paragraphs).strip()


def build_units(epub_path: Path) -> list[WorkUnit]:
    with zipfile.ZipFile(epub_path) as zf:
        entries = toc_entries(zf)
        units: list[WorkUnit] = []
        roman_chapter_index = 0
        current_tom = ""
        for label, src in entries:
            if label in {"Początek utworu"} or label.startswith("Faraon, tom"):
                continue
            if label in {"Tom I", "Tom II", "Tom III"}:
                current_tom = label
                continue
            if label == "Wstęp":
                chapter_id = "000"
                display_title = "Einleitung"
            elif label == "Epilog":
                chapter_id = "068"
                display_title = "Epilog"
            elif label.startswith("Rozdział "):
                roman_chapter_index += 1
                chapter_id = f"{roman_chapter_index:03d}"
                display_title = label
            else:
                continue
            source_title, body = extract_body(zf, src)
            title = source_title or label
            if label.startswith("Rozdział ") and current_tom:
                title = f"{current_tom} - {title}"
            if not body:
                continue
            units.append(
                WorkUnit(
                    chapter_id=chapter_id,
                    source_title=title,
                    display_title=display_title,
                    epub_path=src,
                    body=body,
                    words=count_words(body),
                )
            )
        return units


def render_chapter(unit: WorkUnit, book_title: str) -> str:
    return "\n".join([
        f"# Kapitel {unit.chapter_id}: {unit.source_title}",
        "",
        f"*Buch: {book_title}*",
        f"*Quelle: {unit.epub_path}*",
        "",
        "<!-- status: pending -->",
        "",
        unit.body,
        "",
    ])


def write_units(book: dict, units: list[WorkUnit], dry_run: bool) -> None:
    output_root = book_output_root(REPO_ROOT, book)
    source_lang = str(book.get("source_lang") or "pl")
    if dry_run:
        return
    chapters = chapters_dir(output_root)
    chapters.mkdir(parents=True, exist_ok=True)
    for unit in units:
        (chapters / f"{unit.chapter_id}-source.md").write_text(
            render_chapter(unit, book["title"]),
            encoding="utf-8",
        )
        scene_path = source_scene_path(output_root, unit.chapter_id, 1, source_lang)
        scene_path.parent.mkdir(parents=True, exist_ok=True)
        scene_path.write_text(unit.body.rstrip() + "\n", encoding="utf-8")

    state = new_book_state(book)
    state.created_at = datetime.now().isoformat(timespec="seconds")
    state.chapters = [
        ChapterState(
            id=unit.chapter_id,
            title_ru=unit.source_title,
            status=STATUS_PENDING,
            words_source=unit.words,
        )
        for unit in units
    ]
    save_state(state, REPO_ROOT / book["status_file"])


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                          errors="replace")

    parser = argparse.ArgumentParser(
        description="Extrahiert Wolne-Lektury-EPUBs in chapters/ und scenes/<lang>/."
    )
    parser.add_argument("--book", required=True)
    parser.add_argument("--source", default=None, help="EPUB-Pfad relativ zum Buchpaket oder Repo")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    book = find_book(args.book)
    book_root = REPO_ROOT / "books" / book["id"]
    source = args.source or book["source_path"]
    source_path = Path(source)
    if not source_path.is_absolute():
        candidate = book_root / source
        source_path = candidate if candidate.exists() else REPO_ROOT / source
    if not source_path.exists():
        print(f"FEHLER: Quelle nicht gefunden: {source_path}", file=sys.stderr)
        return 1

    units = build_units(source_path)
    print(f"=== Wolne-Lektury-EPUB: {book['title']} ({book['id']}) ===")
    print(f"Quelle: {source_path.relative_to(REPO_ROOT)}")
    print(f"Arbeitseinheiten: {len(units)}")
    print("-" * 72)
    for unit in units:
        print(f"{unit.chapter_id:>3}  {unit.words:>6,} Wörter  {unit.source_title}")
    print("-" * 72)
    print(f"Summe: {sum(unit.words for unit in units):,} Wörter")
    if args.dry_run:
        print("(dry-run: keine Dateien geschrieben)")
        return 0

    write_units(book, units, dry_run=False)
    print("Geschrieben:")
    output_root = book_output_root(REPO_ROOT, book)
    print(f"  {chapters_dir(output_root).relative_to(REPO_ROOT)}")
    print(f"  {(output_root / 'scenes' / str(book.get('source_lang') or 'pl')).relative_to(REPO_ROOT)}")
    print(f"  {(REPO_ROOT / book['status_file']).relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
