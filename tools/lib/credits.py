"""credits.py - Herausgeber und Uebersetzer in der Titelei.

export.yaml kennt neben ``translator``/``translator_label`` jetzt ein eigenes Herausgeber-Feld
(``editor`` mit dem Vermerk ``editor_note``). Die Titelei zeigt eine Zeile "Vermerk: Name"; die
vorhandenen Stellen lesen dafuer translator/translator_label. Damit sie unveraendert bleiben,
bildet ``apply_editor_credit`` den Herausgeber auf diese Felder ab, aber nur, wenn kein
Uebersetzer gesetzt ist (ein Uebersetzer geht vor).
"""

from __future__ import annotations

from typing import Any

DEFAULT_EDITOR_LABEL = "Herausgabe"


def _clean(value: Any) -> str:
    return str(value or "").strip()


def apply_editor_credit(meta: dict[str, Any]) -> dict[str, Any]:
    """Ergaenzt translator/translator_label aus editor/editor_note, wenn kein Uebersetzer da ist."""
    editor = _clean(meta.get("editor"))
    if editor and not _clean(meta.get("translator")):
        meta["translator"] = editor
        meta["translator_label"] = _clean(meta.get("editor_note")) or DEFAULT_EDITOR_LABEL
    return meta


def publisher_label(meta: dict[str, Any]) -> str:
    """Beschriftung des Verlags im Impressum: 'Herausgeber' war bisher der Verlag; mit eigenem
    Herausgeber-Feld heisst die Zeile 'Verlag'."""
    return "Verlag" if _clean(meta.get("editor")) else "Herausgeber"
