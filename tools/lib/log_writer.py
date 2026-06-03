"""
Logfile-Generator für peter-the-one
====================================

Erzeugt pro Kapitel eine .log.md-Datei, in der festgehalten wird:
- Welche Regeln angewendet wurden
- Welche Stellen schwierig waren
- Welche Regelanpassungen gemacht wurden
- Wortzahl-Vergleich
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional


def chapter_log_path(log_dir: str | Path, chapter_id: str) -> Path:
    return Path(log_dir) / f"{chapter_id}.log.md"


def write_chapter_log(
    log_dir: str | Path,
    chapter_id: str,
    title_ru: str,
    title_de: str,
    words_source: int,
    words_target: int,
    rules_applied: list[str],
    difficult_spots: list[str],
    rule_adjustments: list[str],
    notes: Optional[str] = None,
) -> Path:
    """
    Schreibt (oder überschreibt) das Logfile für ein Kapitel.
    """
    path = chapter_log_path(log_dir, chapter_id)
    path.parent.mkdir(parents=True, exist_ok=True)

    delta = words_target - words_source
    pct = (words_target / words_source * 100) if words_source else 0

    lines = []
    lines.append(f"# Log – Kapitel {chapter_id}")
    lines.append("")
    lines.append(f"- **Erstellt:** {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"- **Titel (RU):** {title_ru}")
    lines.append(f"- **Titel (DE):** {title_de}")
    lines.append(f"- **Wörter Original:** {words_source}")
    lines.append(f"- **Wörter Übersetzung:** {words_target}")
    lines.append(f"- **Delta:** {delta:+d} ({pct:.0f}%)")
    lines.append("")

    lines.append("## Angewendete Regeln")
    if rules_applied:
        for r in rules_applied:
            lines.append(f"- {r}")
    else:
        lines.append("- (keine explizit vermerkt)")
    lines.append("")

    lines.append("## Schwierige Stellen")
    if difficult_spots:
        for d in difficult_spots:
            lines.append(f"- {d}")
    else:
        lines.append("- (keine)")
    lines.append("")

    lines.append("## Regelanpassungen")
    if rule_adjustments:
        for r in rule_adjustments:
            lines.append(f"- {r}")
    else:
        lines.append("- (keine)")
    lines.append("")

    if notes:
        lines.append("## Notizen")
        lines.append(notes)
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def append_to_log(
    log_dir: str | Path,
    chapter_id: str,
    section: str,
    line: str,
) -> None:
    """Hängt eine Zeile an einen bestehenden Log-Abschnitt an."""
    path = chapter_log_path(log_dir, chapter_id)
    if not path.exists():
        write_chapter_log(log_dir, chapter_id, "", "", 0, 0, [], [], [])
    text = path.read_text(encoding="utf-8")
    new_line = f"- {line}"
    if f"## {section}" in text:
        text = text.replace(f"## {section}\n", f"## {section}\n{new_line}\n", 1)
    else:
        text += f"\n## {section}\n{new_line}\n"
    path.write_text(text, encoding="utf-8")
