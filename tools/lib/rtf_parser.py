"""
Source-Parser für peter-the-one (v4 - pragmatic)
================================================

Strategie (einfach und robust):
1. Rohe Bytes einlesen
2. RTF-Quellen ueber `striprtf` extrahieren; Plaintext-Quellen direkt dekodieren
3. Plain-Text anhand von \n+\n in Paragraphen aufteilen
4. Paragraphen als "heading" markieren, wenn sie einem
   Heading-Pattern entsprechen (Книга/Глава/Часть/...)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from striprtf.striprtf import rtf_to_text


@dataclass
class Block:
    kind: str
    level: int
    text: str
    raw: str = ""


# Patterns, die auf eine Überschrift im russischen Text hinweisen
HEADING_PATTERNS = [
    # Книга первая, Книга вторая, ...
    (re.compile(r"^\s*Книга\s+[а-яА-ЯёЁ]+\s*$", re.UNICODE), 1),
    # Глава первая, Глава 1, Глава вторая, ...
    (re.compile(r"^\s*Глава\s+(первая|вторая|третья|четвёртая|четвертая|"
                r"пятая|шестая|седьмая|восьмая|девятая|десятая|"
                r"\d+)\s*$", re.UNICODE), 3),
    # Часть первая, ...
    (re.compile(r"^\s*Часть\s+[а-яА-ЯёЁ]+\s*$", re.UNICODE), 1),
    # Отдел первый
    (re.compile(r"^\s*Отдел\s+[а-яА-ЯёЁ]+\s*$", re.UNICODE), 2),
    # Spezielle Überschriften am Anfang
    (re.compile(r"^\s*Эпилог\s*$", re.UNICODE), 2),
    (re.compile(r"^\s*Пролог\s*$", re.UNICODE), 2),
    (re.compile(r"^\s*Предисловие\s*$", re.UNICODE), 2),
    (re.compile(r"^\s*Вступление\s*$", re.UNICODE), 2),
    # English Project Gutenberg sources, e.g. Boleslaw Prus, Pharaoh.
    (re.compile(r"^\s*CHAPTER\s+[IVXLCDM]+\.?,?\s*$", re.IGNORECASE), 3),
    (re.compile(r"^\s*CHAPTER\s+\d+\.?,?\s*$", re.IGNORECASE), 3),
    (re.compile(r"^\s*(BOOK|PART|VOLUME)\s+[IVXLCDM]+\.?,?\s*$", re.IGNORECASE), 1),
]


def _classify_paragraph(text: str) -> Tuple[str, int]:
    """Liefert (kind, level) für einen Paragraph-Text."""
    for pat, level in HEADING_PATTERNS:
        if pat.match(text):
            return "heading", level
    return "paragraph", 0


# Regex zum Finden von \'xx-Escape-Sequenzen in RTF
RTF_ESC_RE = re.compile(rb"\\'([0-9a-fA-F]{2})")


def _decode_rtf_escapes(raw_bytes: bytes) -> bytes:
    """
    Ersetzt alle `\\'xx`-Sequenzen im RTF durch das entsprechende
    CP1251-Byte. Danach werden keine Escape-Sequenzen mehr da sein,
    und striprtf kann sie nicht mehr falsch interpretieren.
    """
    def _replace_escape(m: re.Match) -> bytes:
        hex_val = m.group(1).decode("ascii")
        byte_val = bytes.fromhex(hex_val)
        return byte_val

    return RTF_ESC_RE.sub(_replace_escape, raw_bytes)


def _decode_plain_text(raw_bytes: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw_bytes.decode("utf-8", errors="replace")


def _strip_gutenberg_footer(text: str) -> str:
    markers = [
        r"^LITTLE,\s+BROWN,\s+&\s+CO\.'S Popular fiction\s*$",
        r"^By the Same Author\s*$",
        r"^End of Project Gutenberg's\b.*$",
        r"^\*\*\*\s+END OF THE PROJECT GUTENBERG EBOOK\b.*$",
    ]
    positions = []
    for pattern in markers:
        marker = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if marker:
            positions.append(marker.start())
    if positions:
        return text[:min(positions)].rstrip() + "\n"
    return text


def _blocks_from_plain_text(full_plain: str) -> List[Block]:
    raw_paras = re.split(r"\n+", full_plain)
    blocks: List[Block] = []
    for p in raw_paras:
        text = p.strip()
        if not text:
            continue
        kind, level = _classify_paragraph(text)
        blocks.append(Block(kind=kind, level=level, text=text, raw=p[:200]))
    return blocks


def parse_rtf(path: str | Path) -> Tuple[List[Block], dict]:
    raw_bytes = Path(path).read_bytes()
    is_rtf = raw_bytes.lstrip().startswith(b"{\\rtf")

    if is_rtf:
        decoded_bytes = _decode_rtf_escapes(raw_bytes)
        raw_text = decoded_bytes.decode("cp1251", errors="replace")
        full_plain = rtf_to_text(raw_text, errors="ignore")
        source_format = "rtf"
    else:
        full_plain = _strip_gutenberg_footer(_decode_plain_text(raw_bytes))
        source_format = "plain_text"

    blocks = _blocks_from_plain_text(full_plain)

    meta = {
        "file": str(path),
        "source_format": source_format,
        "size_bytes": len(raw_bytes),
        "blocks_total": len(blocks),
        "headings_total": sum(1 for b in blocks if b.kind == "heading"),
        "plain_chars": len(full_plain),
    }
    return blocks, meta


def extract_chapter_titles(blocks: List[Block]) -> List[Tuple[int, int, str]]:
    out = []
    for i, b in enumerate(blocks):
        if b.kind == "heading":
            out.append((i, b.level, b.text))
    return out


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if len(sys.argv) < 2:
        print("usage: rtf_parser.py <rtf-file>")
        sys.exit(1)
    blocks, meta = parse_rtf(sys.argv[1])
    print(f"Datei: {meta.get('file')}")
    print(f"Größe: {meta.get('size_bytes')} bytes")
    print(f"Plain-Text: {meta.get('plain_chars'):,} Zeichen")
    print(f"Blöcke: {meta.get('blocks_total')}")
    print(f"Headings: {meta.get('headings_total')}")
    print("-" * 60)
    for idx, level, title in extract_chapter_titles(blocks):
        print(f"[{idx:6d}] L{level}  {title}")
