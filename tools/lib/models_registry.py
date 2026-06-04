"""
models_registry.py
==================
Laedt `config/models.yaml` und stellt Helfer bereit:

- `load_models_registry(path=...)` -> Registry-Objekt
- `registry.get(id)` -> Model-Dict oder None
- `registry.validate(id)` -> wirft ModelError bei unbekannter ID
- `registry.list_ids()` -> sortierte Liste aller IDs
- `registry.list_by_provider()` -> gruppiert nach Provider
- `registry.default_for(book_id)` -> Default-Modell-ID fuer ein Buch
- `registry.fallback()` -> globale Fallback-ID

Verwendung:
    from lib.models_registry import load_models_registry, ModelError

    reg = load_models_registry()
    reg.validate("anthropic/claude-3.5-sonnet")  # OK
    reg.validate("unknown/model")                  # -> ModelError
    print(reg.list_by_provider())
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Optional

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_PATH = REPO_ROOT / "config" / "models.yaml"


class ModelError(RuntimeError):
    """Wird bei unbekannter Modell-ID oder ungueltiger Registry geworfen."""


class ModelsRegistry:
    def __init__(self, data: dict, path: Path):
        self.path = path
        models = data.get("models")
        if not isinstance(models, list):
            raise ModelError(
                f"Ungueltige Struktur in {path}: 'models' muss eine Liste sein"
            )
        # IDs muessen eindeutig sein
        seen: set[str] = set()
        for m in models:
            if not isinstance(m, dict) or not m.get("id"):
                raise ModelError(
                    f"Ungueltiger Modell-Eintrag in {path}: {m!r}"
                )
            mid = m["id"]
            if mid in seen:
                raise ModelError(
                    f"Doppelte Modell-ID in {path}: {mid!r}"
                )
            seen.add(mid)
        self.models: list[dict] = models
        self.by_id: dict[str, dict] = {m["id"]: m for m in models}
        self.defaults: dict = data.get("defaults") or {}

    def get(self, model_id: str) -> Optional[dict]:
        return self.by_id.get(model_id)

    def validate(self, model_id: str) -> dict:
        m = self.get(model_id)
        if m is None:
            valid = ", ".join(self.list_ids()[:5]) + ", ..."
            raise ModelError(
                f"Unbekannte Modell-ID: {model_id!r}. "
                f"Beispiele: {valid}. "
                f"Verfuegbare Modelle siehe config/models.yaml."
            )
        return m

    def list_ids(self) -> list[str]:
        return sorted(self.by_id.keys())

    def list_by_provider(self) -> dict[str, list[dict]]:
        out: dict[str, list[dict]] = defaultdict(list)
        for m in self.models:
            out[m.get("provider", "?")].append(m)
        return dict(out)

    def default_for(self, book_id: str) -> Optional[str]:
        """Liefert die Default-ID fuer ein bestimmtes Buch, falls
        in `models.yaml: models[i].default_for` eingetragen."""
        for m in self.models:
            defaults = m.get("default_for") or []
            if book_id in defaults:
                return m["id"]
        return None

    def fallback(self) -> str:
        """Globale Fallback-ID aus `models.yaml: defaults.fallback_model`,
        oder `anthropic/claude-3.5-sonnet` als hartcodierter Notnagel."""
        fb = self.defaults.get("fallback_model")
        if isinstance(fb, str) and fb in self.by_id:
            return fb
        if "anthropic/claude-3.5-sonnet" in self.by_id:
            return "anthropic/claude-3.5-sonnet"
        # Letzter Ausweg: irgendein Eintrag
        return self.models[0]["id"] if self.models else ""


def load_models_registry(
    path: Path | str = DEFAULT_PATH,
) -> ModelsRegistry:
    p = Path(path)
    if not p.exists():
        raise ModelError(f"models.yaml nicht gefunden: {p}")
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ModelError(f"Ungueltige Struktur in {p}: Top-Level muss ein Dict sein")
    return ModelsRegistry(data, p)


# Mini-Self-Test
if __name__ == "__main__":
    reg = load_models_registry()
    print(f"Modelle geladen: {len(reg.models)}")
    print(f"Erste 5 IDs: {reg.list_ids()[:5]}")
    print(f"Fallback: {reg.fallback()}")
    for prov, lst in reg.list_by_provider().items():
        print(f"  {prov}: {len(lst)} Modell(e)")
