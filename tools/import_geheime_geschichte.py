"""
Import-Skript für 成吉思汗実録 (Geheime Geschichte der Mongolen)
Extrahiert aus dem Wikisource-EPUB Kapitel (Bände) und Szenen (§N-Marker).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from html.parser import HTMLParser

REPO_ROOT = Path(__file__).resolve().parent.parent
BOOK_ID = "geheime-geschichte-mongolen"
BOOK_DIR = REPO_ROOT / "books" / BOOK_ID
SOURCE_DIR = BOOK_DIR / "source" / "epub_temp" / "OPS"
WORK_DIR = BOOK_DIR / "work"
CHAPTERS_DIR = WORK_DIR / "chapters"
SCENES_DIR = WORK_DIR / "scenes" / "ja"

# Mapping: XHTML-Datei → Kapitelnummer
# c0 = Hauptseite (skip), c1 = 序論 → Kapitel 000 (Prolog)
# c2 = 目録 (skip)
# c3-c12 = 巻の一 bis 巻の十
# c13-c14 = 巻の十一-1, -2
# c15-c16 = 巻の十二-1, -2
XHTML_TO_CHAPTER = {
    "c1_cheng_ji_si_han_shi_lu_xu_lun.xhtml": "000",
    "c3_cheng_ji_si_han_shi_lu_juanno_yi.xhtml": "001",
    "c4_cheng_ji_si_han_shi_lu_juanno_er.xhtml": "002",
    "c5_cheng_ji_si_han_shi_lu_juanno_san.xhtml": "003",
    "c6_cheng_ji_si_han_shi_lu_juanno_si.xhtml": "004",
    "c7_cheng_ji_si_han_shi_lu_juanno_wu.xhtml": "005",
    "c8_cheng_ji_si_han_shi_lu_juanno_liu.xhtml": "006",
    "c9_cheng_ji_si_han_shi_lu_juanno_qi.xhtml": "007",
    "c10_cheng_ji_si_han_shi_lu_juanno_ba.xhtml": "008",
    "c11_cheng_ji_si_han_shi_lu_juanno_jiu.xhtml": "009",
    "c12_cheng_ji_si_han_shi_lu_juanno_shi.xhtml": "010",
    "c13_cheng_ji_si_han_shi_lu_juanno_shi_yi_1.xhtml": "011",
    "c14_cheng_ji_si_han_shi_lu_juanno_shi_yi_2.xhtml": "012",
    "c15_cheng_ji_si_han_shi_lu_juanno_shi_er_1.xhtml": "013",
    "c16_cheng_ji_si_han_shi_lu_juanno_shi_er_2.xhtml": "014",
}

# §N(01:01:02) marker pattern
SCENE_MARKER_RE = re.compile(r"§(\d+)\((\d+:\d+:\d+)\)")


class XHTMLStripper(HTMLParser):
    """Entfernt HTML-Tags und extrahiert Text + Szenenstruktur."""

    def __init__(self):
        super().__init__()
        self.text_parts: list[str] = []
        self.current_scene_title: str | None = None
        self.current_scene_marker: str | None = None
        self.scenes: list[dict] = []  # {marker, title, text}
        self._in_bold = False
        self._bold_text: list[str] = []
        self._skip_nav = False
        self._skip_depth = 0  # für style/script Blöcke
        self._in_style = False

    def handle_starttag(self, tag: str, attrs: list):
        attr_dict = dict(attrs)
        if tag in ("style", "script"):
            self._in_style = True
            return
        if self._in_style:
            return
        if tag == "b":
            self._in_bold = True
            self._bold_text = []
        # Navigation / header divs zum Überspringen
        if tag == "div":
            div_id = attr_dict.get("id", "")
            div_class = attr_dict.get("class", "")
            if div_id.startswith("navigation") or div_class == "mw-inputbox-centered":
                self._skip_nav = True
                self._skip_depth += 1
            return
        if self._skip_nav:
            self._skip_depth += 1
            return
        if tag == "sup":  # Referenz-Links überspringen
            self._skip_depth += 1
            return
        if tag == "hr":
            self.text_parts.append("\n")
        if tag == "br":
            self.text_parts.append("\n")

    def handle_endtag(self, tag: str):
        if tag in ("style", "script"):
            self._in_style = False
            return
        if self._in_style:
            return
        if tag == "b" and self._in_bold:
            self._in_bold = False
            bold_text = "".join(self._bold_text).strip()
            if bold_text and self.current_scene_marker:
                self.current_scene_title = bold_text
            return
        if tag == "div" or tag == "sup":
            if self._skip_depth > 0:
                self._skip_depth -= 1
            if self._skip_depth == 0:
                self._skip_nav = False
            return
        if self._skip_depth > 0:
            self._skip_depth -= 1
            return
        if tag == "p":
            self.text_parts.append("\n\n")

    def handle_data(self, data: str):
        if self._in_style or self._skip_nav or self._skip_depth > 0:
            return
        if self._in_bold:
            self._bold_text.append(data)
            return

        # Prüfe auf §N Marker
        match = SCENE_MARKER_RE.search(data)
        if match:
            if self.current_scene_marker:
                self._flush_scene()
            self.current_scene_marker = match.group(0)
            self.current_scene_title = None
            return

        self.text_parts.append(data)

    def handle_entityref(self, name: str):
        """Behandle HTML-Entitäten."""
        entities = {
            "lt": "<", "gt": ">", "amp": "&", "quot": '"',
            "apos": "'", "nbsp": " ",
        }
        self.text_parts.append(entities.get(name, f"&{name};"))

    def handle_charref(self, name: str):
        """Behandle numerische Zeichenreferenzen."""
        try:
            if name.startswith("x"):
                self.text_parts.append(chr(int(name[1:], 16)))
            else:
                self.text_parts.append(chr(int(name)))
        except (ValueError, OverflowError):
            self.text_parts.append(f"&#{name};")

    def _flush_scene(self):
        """Speichert die aktuelle Szene."""
        if self.current_scene_marker:
            scene_text = "".join(self.text_parts).strip()
            self.scenes.append({
                "marker": self.current_scene_marker,
                "title": self.current_scene_title or "",
                "text": scene_text,
            })
            self.text_parts = []

    def flush_final_scene(self):
        """Speichert die letzte Szene nach dem Parsen."""
        self._flush_scene()
        # Falls noch Text außerhalb von Szenenmarkern übrig ist
        remaining = "".join(self.text_parts).strip()
        if remaining and not self.scenes:
            self.scenes.append({
                "marker": "",
                "title": "",
                "text": remaining,
            })


def strip_html(html_content: str) -> tuple[str, list[dict]]:
    """Entfernt HTML und extrahiert Plaintext + Szenen."""
    parser = XHTMLStripper()
    parser.feed(html_content)
    parser.flush_final_scene()
    # Gesamttext aus allen Szenen
    full_text = "\n\n".join(s["text"] for s in parser.scenes)
    return full_text, parser.scenes


def clean_text(text: str) -> str:
    """Bereinigt den extrahierten Text."""
    # Entferne überflüssige Leerzeilen
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Entferne Wikidata-Ruby-Annotationen
    text = re.sub(r"​[^​]*​", "", text)
    # Entferne Nullbreite-Zeichen
    text = text.replace("\u200b", "")
    return text.strip()


def scene_heading(number: int, title: str = "") -> str:
    title = clean_text(title)
    if title:
        return f"## {number}. {title}"
    return f"## {number}"


def write_pipeline_scenes(chap_num: str, scenes: list[dict]) -> int:
    """Schreibt scene-NN.md und die Kapitelquelle mit ##-Headings."""
    scene_dir = SCENES_DIR / chap_num
    scene_dir.mkdir(parents=True, exist_ok=True)

    # Alte Import-Artefakte und veraltete Monolith-Szenen entfernen
    for stale in scene_dir.glob("*-source.md"):
        stale.unlink()
    for stale in scene_dir.glob("scene-*.md"):
        stale.unlink()

    chapter_parts: list[str] = []
    written = 0
    for i, scene in enumerate(scenes, start=1):
        body = clean_text(scene.get("text") or "")
        if not body:
            continue
        heading = scene_heading(i, scene.get("title") or "")
        block = f"{heading}\n\n{body}"
        scene_path = scene_dir / f"scene-{i:02d}.md"
        scene_path.write_text(block + "\n", encoding="utf-8")
        chapter_parts.append(block)
        written += 1

    chapter_path = CHAPTERS_DIR / f"{chap_num}-source.md"
    chapter_path.write_text("\n\n".join(chapter_parts) + "\n", encoding="utf-8")
    print(f"  -> {chapter_path.name} ({chapter_path.stat().st_size} Bytes)")
    print(f"  -> {written} Szenen als scene-NN.md")
    return written


def migrate_existing_section_files() -> int:
    """Wandelt vorhandene NN-source.md in Pipeline-scene-NN.md um."""
    if not SCENES_DIR.exists():
        print("Keine scenes/ja-Dateien gefunden.")
        return 0

    total = 0
    for chap_dir in sorted(p for p in SCENES_DIR.iterdir() if p.is_dir()):
        sources = sorted(chap_dir.glob("[0-9][0-9]-source.md"))
        if not sources:
            continue

        scenes: list[dict] = []
        for src in sources:
            raw = src.read_text(encoding="utf-8")
            lines = raw.splitlines()
            title = ""
            if lines and lines[0].startswith("# "):
                title = lines[0][2:].strip()
                body = "\n".join(lines[1:])
            else:
                body = raw
            scenes.append({"title": title, "text": body})

        print(f"Migriere Kapitel {chap_dir.name} ({len(sources)} Abschnitte)...")
        total += write_pipeline_scenes(chap_dir.name, scenes)

    return total


def import_from_epub() -> int:
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    SCENES_DIR.mkdir(parents=True, exist_ok=True)

    total_scenes = 0
    for xhtml_file, chap_num in sorted(XHTML_TO_CHAPTER.items()):
        src_path = SOURCE_DIR / xhtml_file
        if not src_path.exists():
            print(f"SKIP: {xhtml_file} nicht gefunden")
            continue

        print(f"Verarbeite {xhtml_file} → Kapitel {chap_num}...")
        html_content = src_path.read_text(encoding="utf-8")
        _full_text, scenes = strip_html(html_content)
        total_scenes += write_pipeline_scenes(chap_num, scenes)

    print(f"\nFertig! {len(XHTML_TO_CHAPTER)} Kapitel, {total_scenes} Szenen extrahiert.")
    return total_scenes


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(
        description=(
            "Importiert die Geheime Geschichte der Mongolen aus dem "
            "Wikisource-EPUB in Kapitel- und scene-NN.md-Dateien."
        )
    )
    ap.add_argument(
        "--migrate-existing",
        action="store_true",
        help="Vorhandene NN-source.md nach scene-NN.md migrieren (ohne EPUB).",
    )
    args = ap.parse_args()

    if args.migrate_existing:
        total = migrate_existing_section_files()
        print(f"\nMigration fertig: {total} Szenen.")
        return 0

    import_from_epub()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())