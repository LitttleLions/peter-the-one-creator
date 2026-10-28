"""Import William Horatio Bates' *Perfect Sight Without Glasses*.

The Wikisource edition is the clean text source.  The supplied EPUB is kept
untouched and its original JPEG assets are copied into ``assets/figures`` with
an auditable manifest.  Wikisource's ``:Fig. N`` captions are retained as
textual markers; automatic inline placement is deliberately not guessed from
scan filenames.

Examples::

    python tools/import_perfect_sight.py --dry-run
    python tools/import_perfect_sight.py
    python tools/import_perfect_sight.py --refresh
"""

from __future__ import annotations

import argparse
import io
import re
import shutil
import sys
from html import unescape
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))

from lib.book_project import find_book as find_book_project
from lib.output_paths import de_scene_path, source_chapter_path, source_scene_path
from lib.status_manager import ChapterState, add_chapter, new_book_state, save_state


REPO_ROOT = Path(__file__).resolve().parent.parent
BOOK_ID = "perfect.sight"
BOOK_DIR = REPO_ROOT / "books" / BOOK_ID
EPUB_PATH = BOOK_DIR / "source" / "Perfect Sight Without Glasses.epub"
FIGURES_DIR = BOOK_DIR / "assets" / "figures"
MANIFEST_PATH = FIGURES_DIR / "manifest.yaml"
WIKISOURCE_ROOT = "https://en.wikisource.org/w/index.php"

SECTIONS: list[tuple[str, str, str]] = [
    ("000", "The Fundamental Principle", "Perfect_Sight_Without_Glasses/The_Fundamental_Principle"),
    ("001", "Preface", "Perfect_Sight_Without_Glasses/Preface"),
]
CHAPTER_TITLES = {
    1: "Introductory",
    2: "Simultaneous Retinoscopy",
    3: "Evidence for the Accepted Theory of Accommodation",
    4: "The Truth About Accommodation as Demonstrated by Experiments on the Eye Muscles of Fish, Cats, Dogs, Rabbits and Other Animals",
    5: "The Truth About Accommodation as Demonstrated by a Study of Images Reflected from the Lens, Cornea, Iris and Sclera",
    6: "The Truth About Accommodation as Demonstrated by Clinical Observations",
    7: "The Variability of the Refraction of the Eye",
    8: "What Glasses Do to Us",
    9: "The Cause and Cure of Errors of Refraction",
    10: "Strain",
    11: "Central Fixation",
    12: "Palming",
    13: "Memory as an Aid to Vision",
    14: "Imagination as an Aid to Vision",
    15: "Shifting and Swinging",
    16: "The Illusions of Imperfect and of Normal Sight",
    17: "Vision Under Adverse Conditions a Benefit to the Eyes",
    18: "Optimums and Pessimums",
    19: "The Relief of Pain and Other Symptoms by the Aid of the Memory",
    20: "Presbyopia: Its Cause and Cure",
    21: "Squint and Amblyopia: Their Cause",
    22: "Squint and Amblyopia: Their Cure",
    23: "Floating Specks: Their Cause and Cure",
    24: "Home Treatment",
    25: "Correspondence Treatment",
    26: "The Prevention of Myopia in Schools: Methods That Failed",
    27: "The Prevention and Cure of Myopia and Other Errors of Refraction in Schools: A Method That Succeeded",
    28: "The Story of Emily",
    29: "Mind and Vision",
    30: "Normal Sight and the Relief of Pain for Soldiers and Sailors",
    31: "Letters from Patients",
    32: "Reason and Authority",
}
for _number, _title in CHAPTER_TITLES.items():
    SECTIONS.append((f"{_number + 1:03d}", f"Chapter {_number}: {_title}", f"Perfect_Sight_Without_Glasses/Chapter_{_number}"))


def fetch_raw(title: str) -> str:
    query = urllib.parse.urlencode({"title": title, "action": "raw", "format": "text"})
    request = urllib.request.Request(
        f"{WIKISOURCE_ROOT}?{query}",
        headers={"User-Agent": "peter-the-one-creator/1.0 (book import; contact repository owner)"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read().decode("utf-8")


def strip_wikimarkup(raw: str) -> str:
    text = raw.replace("\r\n", "\n")
    text = re.sub(r"^\{\{header.*?^\}\}\s*", "", text, flags=re.MULTILINE | re.DOTALL)
    text = re.split(r"^Notes\s*$", text, maxsplit=1, flags=re.MULTILINE)[0]
    text = re.sub(r"\{\{rule\}\}", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"\{\{[^{}]+\}\}", "", text)
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[https?://[^ ]+ ([^\]]+)\]", r"\1", text)
    text = re.sub(r"^\s*={1,6}\s*(.*?)\s*={1,6}\s*$", r"\1", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*:\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+[\w'’-]*\b", text, flags=re.UNICODE))


def render_source(chapter_id: str, title: str, body: str) -> str:
    return f"# {title}\n\n*Buch: Perfect Sight Without Glasses*\n*Kapitel-ID: {chapter_id}*\n\n---\n\n{body.strip()}\n"


def render_scene(title: str, body: str) -> str:
    return f"## {title}\n\n{body.strip()}\n"


def extract_figures() -> list[dict]:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    with zipfile.ZipFile(EPUB_PATH) as archive:
        image_names = sorted(
            name for name in archive.namelist()
            if name.lower().startswith("epub/") and Path(name).suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
        )
        for index, source_name in enumerate(image_names, 1):
            target = FIGURES_DIR / f"figure-{index:03d}{Path(source_name).suffix.lower()}"
            target.write_bytes(archive.read(source_name))
            page_match = re.search(r"image_(\d+)", Path(source_name).stem)
            source_page = int(page_match.group(1)) if page_match else None
            records.append({
                "id": f"figure-{index:03d}",
                "source_file": source_name,
                "source_page": source_page,
                "path": target.relative_to(BOOK_DIR).as_posix(),
                "chapter_id": "",
                "figure_label": "",
                "placement": "review",
                "status": "review",
                "note": "Original scan asset; page/caption/chapter placement requires editorial matching.",
            })
    MANIFEST_PATH.write_text(yaml.safe_dump({"figures": records}, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return records


def roman_to_int(value: str) -> int:
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    previous = 0
    for char in reversed(value.upper()):
        number = values[char]
        total += -number if number < previous else number
        previous = number
    return total


def add_figure_markers(body: str, records: list[dict], chapter_id: str) -> str:
    candidates = [r for r in records if r.get("chapter_id") == chapter_id and r.get("figure_label")]
    for record in candidates:
        label = str(record["figure_label"])
        pattern = re.compile(re.escape(label[: min(len(label), 35)]), flags=re.IGNORECASE)
        marker = f"<!-- figure: {record['id']} -->"
        body = pattern.sub(lambda match: match.group(0) + "\n" + marker, body, count=1)
    return body


def import_book(dry_run: bool, refresh: bool) -> int:
    book = find_book_project(REPO_ROOT, BOOK_ID)
    output_root = REPO_ROOT / book["work_dir"]
    style = book["style_mode"]
    fetched: list[tuple[str, str, str]] = []
    figure_records: list[dict] = []
    if not dry_run:
        figure_records = extract_figures()
    for chapter_id, title, page in SECTIONS:
        chapter_path = source_chapter_path(output_root, chapter_id)
        if chapter_path.exists() and not refresh:
            body = chapter_path.read_text(encoding="utf-8")
            body = body.split("---", 1)[-1].strip()
        else:
            print(f"Lade {title} ...")
            body = strip_wikimarkup(fetch_raw(page))
        if not body:
            raise RuntimeError(f"Leerer Wikisource-Text: {page}")
        fetched.append((chapter_id, title, body))

    print(f"Kapitel/Abschnitte: {len(fetched)}")
    print(f"Wörter: {sum(word_count(body) for _, _, body in fetched):,}")
    if dry_run:
        print("(dry-run: keine Dateien geschrieben)")
        return 0

    state = new_book_state(book)
    for chapter_id, title, body in fetched:
        chapter_path = source_chapter_path(output_root, chapter_id)
        chapter_path.parent.mkdir(parents=True, exist_ok=True)
        chapter_path.write_text(render_source(chapter_id, title, body), encoding="utf-8")

        source_scene = source_scene_path(output_root, chapter_id, 1, "en")
        source_scene.parent.mkdir(parents=True, exist_ok=True)
        source_scene.write_text(render_scene(title, body), encoding="utf-8")

        # Placeholder path only: the source scene is ready for translation.
        # Do not mark it as a completed German translation.
        de_scene = de_scene_path(output_root, chapter_id, 1, style)
        if de_scene.exists() and refresh:
            de_scene.unlink()
        add_chapter(state, ChapterState(
            id=chapter_id,
            title_ru=title,
            words_source=word_count(body),
        ))

    save_state(state, REPO_ROOT / book["status_file"])
    print(f"Quellkapitel geschrieben: {len(fetched)}")
    print(f"Originalabbildungen extrahiert: {len(figure_records)}")
    print(f"Manifest: {MANIFEST_PATH.relative_to(REPO_ROOT)}")
    return 0


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = argparse.ArgumentParser(description="Importiert Perfect Sight Without Glasses aus Wikisource.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--refresh", action="store_true", help="Wikisource-Texte neu laden und vorhandene Arbeitsdateien ersetzen")
    args = parser.parse_args()
    if not EPUB_PATH.exists():
        raise SystemExit(f"EPUB nicht gefunden: {EPUB_PATH}")
    return import_book(args.dry_run, args.refresh)


if __name__ == "__main__":
    raise SystemExit(main())