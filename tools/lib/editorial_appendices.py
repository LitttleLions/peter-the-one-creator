"""Book-local translated appendices, shared by export and deterministic review."""
from pathlib import Path
from typing import Any

import yaml


def load_appendices(meta: dict[str, Any], style: str) -> list[dict[str, Any]]:
    """Load explicitly configured texts; fail on missing/empty/outside-package files."""
    base = Path(meta.get("_base_dir", ".")).resolve()
    result = []
    for index, entry in enumerate(meta.get("appendices") or [], 1):
        if entry.get("style") != style:
            continue
        path = (base / entry["path"]).resolve()
        if not path.is_relative_to(base):
            raise ValueError(f"Anhang liegt ausserhalb des Buchpakets: {path}")
        text = path.read_text(encoding="utf-8-sig").strip()
        if not text or not str(entry.get("title") or "").strip():
            raise ValueError(f"Anhang ohne Text oder Titel: {path}")
        result.append({**entry, "text": text, "anchor": f"anhang-{index}"})
    return result


def review_appendix_text(
    repo_root: Path, book: dict[str, Any], style: str, chapter: str, scene: int,
) -> str:
    """Include relocated translations in QA, without excluding any source text."""
    config = book.get("export_config")
    if not config:
        return ""
    path = repo_root / config
    if not path.exists():
        return ""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
    except (OSError, ValueError):
        return ""
    meta = {**(data.get("defaults") or {}), **(data.get("book") or {})}
    # `appendices` ist ein top-level Block; nur Szenen-Anhaenge laden, damit
    # andere fehlende Dateien die Pruefung dieses Kapitels nicht blockieren.
    meta["appendices"] = [
        entry for entry in data.get("appendices") or []
        if str(entry.get("source_chapter", "")).zfill(3) == chapter
        and entry.get("source_scene") == scene
    ]
    meta["_base_dir"] = str(path.parent)
    return "\n\n".join(item["text"] for item in load_appendices(meta, style))
