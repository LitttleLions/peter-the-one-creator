"""Book-local name and term registry helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_names(path: Path | str) -> list[dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return []
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    entries = data.get("entries", [])
    return entries if isinstance(entries, list) else []


def write_names(path: Path | str, entries: list[dict[str, Any]]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {"entries": entries}
    p.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def compact_name_lines(entries: list[dict[str, Any]], limit: int = 80) -> list[str]:
    lines: list[str] = []
    for entry in entries[:limit]:
        source = str(entry.get("source") or "").strip()
        target = str(entry.get("target") or "").strip()
        if not source or not target:
            continue
        aliases = entry.get("aliases") or []
        if isinstance(aliases, str):
            aliases = [aliases]
        aliases_text = ", ".join(str(item).strip() for item in aliases if str(item).strip())
        status = str(entry.get("status") or "draft").strip()
        note = str(entry.get("note") or "").strip()
        line = f"- {source} -> {target}"
        details = []
        if aliases_text:
            details.append(f"Alias: {aliases_text}")
        if status:
            details.append(f"Status: {status}")
        if note:
            details.append(note)
        if details:
            line += " (" + "; ".join(details) + ")"
        lines.append(line)
    return lines
