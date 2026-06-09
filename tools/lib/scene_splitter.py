"""
scene_splitter.py
=================
Zerlegt eine `NNN-source.md`-Quelldatei in Szenen.

Erkennt Szenen anhand von Markdown-Headings der Form
`## N` oder `## N. Titel`. Alles vor der ersten Szene
gilt als "Frontmatter" (Titel-Block, Header).

Verwendung:
    from lib.scene_splitter import split_into_scenes

    frontmatter, scenes = split_into_scenes(
        Path("books/<book-id>/work/chapters/001-source.md")
    )
    # frontmatter: str (Header / Lede)
    # scenes: list[Scene] mit .number, .title, .text
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# Akzeptiert "## 1", "## 1.", "## 1. Titel", "## 1 — Titel"
# Sowie nackte Zahlen auf separaten Zeilen: "1", "2.", etc.
SCENE_HEADING_RE = re.compile(
    r"^(?:##\s+)?(\d+)\.?\s*(.*?)\s*$"
)


@dataclass
class Scene:
    number: int
    title: str
    text: str   # gesamter Szenen-Text inkl. Heading-Zeile

    @property
    def heading_line(self) -> str:
        suffix = f" {self.title}" if self.title else ""
        return f"## {self.number}{('.' if self.title else '')}{suffix}"


def split_into_scenes(
    source_path: Path | str,
) -> tuple[str, list[Scene]]:
    """
    Liest die Markdown-Quelldatei und gibt (Frontmatter, Szenen) zurück.

    - Frontmatter: alles vor dem ersten `## N`-Heading.
      In der Praxis ist das der Header (Titel, Buch, status-Kommentar).
    - Szenen: jeweils ein Block von einer Heading-Zeile bis zur
      nächsten Heading-Zeile (oder Dateiende).
    """
    p = Path(source_path)
    text = p.read_text(encoding="utf-8")
    return split_markdown_into_scenes(text)


def split_markdown_into_scenes(
    text: str,
) -> tuple[str, list[Scene]]:
    """Reine String-Variante — nützlich für Tests."""
    lines = text.splitlines()
    first_scene_idx: Optional[int] = None
    for i, line in enumerate(lines):
        if SCENE_HEADING_RE.match(line):
            first_scene_idx = i
            break
    if first_scene_idx is None:
        # Keine Szene erkannt → alles ist Frontmatter
        return text.strip(), []

    frontmatter = "\n".join(lines[:first_scene_idx]).rstrip()

    # Szenen-Blocks: sammle zusammenhängende Bereiche
    scene_lines_groups: list[list[str]] = []
    current: list[str] = []
    in_scene = False
    for line in lines[first_scene_idx:]:
        if SCENE_HEADING_RE.match(line):
            if in_scene:
                scene_lines_groups.append(current)
            current = [line]
            in_scene = True
        else:
            if in_scene:
                current.append(line)
    if in_scene:
        scene_lines_groups.append(current)

    scenes: list[Scene] = []
    for grp in scene_lines_groups:
        m = SCENE_HEADING_RE.match(grp[0])
        assert m is not None
        num = int(m.group(1))
        title = m.group(2).strip()
        body = "\n".join(grp).rstrip()
        scenes.append(Scene(number=num, title=title, text=body))
    return frontmatter, scenes


def count_words(text: str) -> int:
    return len([w for w in text.split() if w])
