"""Typografie-Block fuer Titelbild-Prompts aus den Buchdaten erzeugen.

Marke (Herausgeber, z. B. "Motivatier Classics") steht oben, Titel, Untertitel
und Autor aus den Buchdaten, der Verlag klein unten. Der Block wird in den
handgeschriebenen Cover-Prompt unter "TYPOGRAPHY" eingefuegt; Szene und Stil
bleiben Handarbeit. Es wird nichts geschrieben oder generiert.

Aufruf::

    python tools/cover_text.py --book die-sprache-des-anderen
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.book_project import find_book as find_book_project  # noqa: E402
from lib.kdp_mapping import load_export_document  # noqa: E402
from lib.print_wrap import _book_fields, _text_field, brand_line, footer_line  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]


def cover_text_block(meta: dict) -> str:
    fields = _book_fields(meta)
    brand = brand_line(meta)
    publisher = footer_line(meta) or brand
    title = _text_field(fields, "title")
    subtitle = _text_field(fields, "subtitle")
    author = _text_field(fields, "author")
    lines = [
        "TYPOGRAPHY, integrated into the artwork, clean sharp serif capitals, every word spelled exactly:"
    ]
    if brand:
        lines.append(
            f"- At the very top, centered, small letterspaced capitals (publisher brand): {brand.upper()}"
        )
    if title:
        lines.append(f"- Centered title in very large capitals: {title.upper()}")
    if subtitle:
        lines.append(f"- Below the title, small letterspaced capitals: {subtitle.upper()}")
    if author:
        lines.append(f"- Author name, letterspaced capitals: {author.upper()}")
    if publisher and publisher != brand:
        lines.append(f"- Bottom, very small letterspaced capitals (legal publisher): {publisher.upper()}")
    lines.append(
        "- Keep a clear word space between every word; no other text, no barcode, no price."
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book", required=True)
    args = parser.parse_args()
    book = find_book_project(REPO_ROOT, args.book)
    meta = load_export_document(REPO_ROOT / book["export_config"])
    print(cover_text_block(meta))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
