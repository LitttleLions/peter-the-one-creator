"""Verwaltet den Git-Ausschluss grosser Medien pro Buchpaket.

Die verwaltete Sektion in ``books/<id>/.gitignore`` wird zwischen zwei Markern
geschrieben; alles ausserhalb bleibt unangetastet. Muster kommen aus
``config/gitignore-assets.yaml``, der Schalter pro Buch aus ``book.yaml``:

    gitignore:
      large_assets: true
      extra_patterns: ["/work/gross/"]
      disabled_patterns: ["/assets/audio/"]
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = "config/gitignore-assets.yaml"
FALLBACK_PATTERNS = ("/assets/master/",)
DEFAULT_BEGIN_MARKER = "# >>> motivatier:large-assets >>>"
DEFAULT_END_MARKER = "# <<< motivatier:large-assets <<<"


def load_config(repo_root: Path) -> dict[str, Any]:
    path = repo_root / DEFAULT_CONFIG_PATH
    if not path.is_file():
        # Ohne Config-Datei bleiben die Kernmuster aktiv; die Marker muessen
        # trotzdem gesetzt sein, sonst bricht render_block().
        return {
            "patterns": list(FALLBACK_PATTERNS),
            "begin_marker": DEFAULT_BEGIN_MARKER,
            "end_marker": DEFAULT_END_MARKER,
        }
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    defaults = data.get("defaults") or {}
    return {
        "patterns": [str(p) for p in (defaults.get("patterns") or FALLBACK_PATTERNS)],
        "begin_marker": str(data.get("begin_marker") or DEFAULT_BEGIN_MARKER),
        "end_marker": str(data.get("end_marker") or DEFAULT_END_MARKER),
    }


def book_switch(book: dict[str, Any]) -> dict[str, Any]:
    """``gitignore:``-Block eines Buchs lesen (Default: aktiv)."""
    block = book.get("gitignore")
    if not isinstance(block, dict):
        return {"large_assets": True, "extra": [], "disabled": []}
    disabled = block.get("disabled_patterns") or []
    extra = block.get("extra_patterns") or []
    return {
        "large_assets": bool(block.get("large_assets", True)),
        "extra": [str(p) for p in extra],
        "disabled": {str(p) for p in disabled},
    }


def effective_patterns(book: dict[str, Any], config: dict[str, Any]) -> list[str]:
    switch = book_switch(book)
    if not switch["large_assets"]:
        return []
    seen: set[str] = set()
    out: list[str] = []
    for pattern in list(config["patterns"]) + switch["extra"]:
        if pattern in switch["disabled"] or pattern in seen:
            continue
        seen.add(pattern)
        out.append(pattern)
    return out


def render_block(book: dict[str, Any], config: dict[str, Any]) -> str:
    patterns = effective_patterns(book, config)
    lines = [config["begin_marker"]]
    if patterns:
        lines.append("# Grosse, regenerierbare Medien (nicht im Repo).")
        lines.append("# Buch-Schalter: book.yaml -> gitignore.large_assets")
        lines.append("# Erzeugt von tools/sync_book_gitignore.py")
        lines.extend(patterns)
    else:
        lines.append("# Kein Ausschluss (gitignore.large_assets: false).")
    lines.append(config["end_marker"])
    return "\n".join(lines)


def split_sections(text: str, config: dict[str, Any]) -> tuple[str, str, str]:
    """(prefix, managed, suffix) – managed enthaelt die Markerzeilen."""
    begin = config["begin_marker"]
    end = config["end_marker"]
    start = text.find(begin)
    stop = text.find(end)
    if start == -1 or stop == -1 or stop < start:
        return text, "", ""
    stop += len(end)
    return text[:start], text[start:stop], text[stop:]


def render_gitignore(existing: str, book: dict[str, Any], config: dict[str, Any]) -> str:
    """Bestehenden .gitignore-Inhalt plus aktualisierte Sektion."""
    block = render_block(book, config)
    text = existing or ""
    if not text.strip():
        return block + "\n"
    prefix, managed, suffix = split_sections(text, config)
    if not managed:
        base = text if text.endswith("\n") else text + "\n"
        return f"{base}\n{block}\n"
    new_suffix = suffix if suffix.startswith("\n") or not suffix else "\n" + suffix
    return f"{prefix}{block}{new_suffix}"


def gitignore_state(existing: str, book: dict[str, Any], config: dict[str, Any]) -> str:
    """``ok`` wenn die Datei bereits dem Soll entspricht, sonst ``abweichend``."""
    wanted = render_gitignore(existing, book, config)
    return "ok" if existing == wanted else "abweichend"


def load_settings(book: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    """Vollstaendiger Schalter-Zustand fuer CLI und Dashboard-API."""
    config = load_config(repo_root)
    switch = book_switch(book)
    target = repo_root / "books" / str(book.get("id") or "") / ".gitignore"
    existing = target.read_text(encoding="utf-8") if target.is_file() else ""
    try:
        shown_path = target.resolve().relative_to(
            repo_root.resolve()
        ).as_posix()
    except ValueError:
        shown_path = target.as_posix()
    return {
        "large_assets": switch["large_assets"],
        "extra_patterns": switch["extra"],
        "disabled_patterns": sorted(switch["disabled"]),
        "patterns": effective_patterns(book, config),
        "gitignore_path": shown_path,
        "state": gitignore_state(existing, book, config),
    }


def write_gitignore(book: dict[str, Any], repo_root: Path) -> str:
    """``books/<id>/.gitignore`` auf den Sollstand bringen. Gibt den State zurueck."""
    config = load_config(repo_root)
    target = repo_root / "books" / str(book.get("id") or "") / ".gitignore"
    existing = target.read_text(encoding="utf-8") if target.is_file() else ""
    target.write_text(render_gitignore(existing, book, config), encoding="utf-8")
    return "ok"


def with_switch(
    book: dict[str, Any], large_assets: bool
) -> dict[str, Any]:
    """Kopie des Buchs mit gesetztem ``gitignore.large_assets``."""
    updated = dict(book)
    block = dict(updated.get("gitignore") or {}) if isinstance(
        updated.get("gitignore"), dict
    ) else {}
    block["large_assets"] = bool(large_assets)
    updated["gitignore"] = block
    return updated
