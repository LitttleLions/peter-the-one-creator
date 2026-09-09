"""Kuratierte Higgsfield-Bildmodelle und CLI-Parametermapping."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = REPO_ROOT / "config" / "higgsfield_models.yaml"


@lru_cache(maxsize=1)
def load_higgsfield_model_catalog() -> dict[str, Any]:
    if not CATALOG_PATH.exists():
        return {"default": "text2image_soul_v2", "models": []}
    data = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8")) or {}
    models = data.get("models") or []
    if not isinstance(models, list):
        models = []
    return {
        "default": str(data.get("default") or "text2image_soul_v2"),
        "models": [m for m in models if isinstance(m, dict) and m.get("id")],
    }


def list_higgsfield_models() -> list[dict[str, Any]]:
    catalog = load_higgsfield_model_catalog()
    return list(catalog["models"])


def higgsfield_model_meta(model_id: str) -> dict[str, Any]:
    model_id = (model_id or "").strip()
    for entry in list_higgsfield_models():
        if str(entry.get("id")) == model_id:
            return entry
    return {
        "id": model_id or "text2image_soul_v2",
        "label": model_id or "text2image_soul_v2",
        "size_param": "quality",
        "size_options": ["1.5k", "2k"],
        "default_size": "2k",
    }


def normalize_size_value(model_id: str, raw: str | None) -> str:
    meta = higgsfield_model_meta(model_id)
    value = str(raw or "").strip()
    options = [str(x) for x in (meta.get("size_options") or [])]
    default = str(meta.get("default_size") or (options[0] if options else "2k"))
    if not value:
        return default
    lowered = value.lower()
    # Alias: "high" als Groesse meint die Default-Aufloesung, nicht GPT-Render-Qualitaet.
    if lowered in {"high", "max", "ultra"} and lowered not in {o.lower() for o in options}:
        return default
    if options and value not in options and lowered in {o.lower() for o in options}:
        for option in options:
            if option.lower() == lowered:
                return option
    # Buch-Default "1.5k" (Soul) darf nicht unveraendert an GPT/Nano Banana
    # als --resolution 1.5k gehen – CLI lehnt das ab.
    if options and value not in options:
        return default
    return value


def normalize_render_quality(model_id: str, raw: str | None) -> str | None:
    meta = higgsfield_model_meta(model_id)
    render_param = str(meta.get("render_quality_param") or "").strip()
    if not render_param:
        return None
    options = [str(x) for x in (meta.get("render_quality_options") or [])]
    default = str(meta.get("default_render_quality") or (options[0] if options else "high"))
    value = str(raw or "").strip().lower()
    if value in options:
        return value
    if value and value in {o.lower() for o in options}:
        for option in options:
            if option.lower() == value:
                return option
    return default


def size_cli_args(
    model_id: str,
    quality: str | None,
    render_quality: str | None = None,
) -> list[str]:
    """Mappt UI-/book.yaml-Groesse und optionale Render-Qualitaet auf CLI-Flags."""
    meta = higgsfield_model_meta(model_id)
    size_param = str(meta.get("size_param") or "quality")
    size_value = normalize_size_value(model_id, quality)
    args = [f"--{size_param}", size_value]

    render_param = str(meta.get("render_quality_param") or "").strip()
    if render_param:
        render_value = normalize_render_quality(model_id, render_quality)
        if render_value:
            args.extend([f"--{render_param}", render_value])
    return args
