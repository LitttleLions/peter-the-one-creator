"""RomanForge-Figuren als Spiegel im Buchpaket und Abgleich mit names.yaml.

RomanForge fuehrt die Figuren-Stammdaten (Name, Rolle, Aussehen) der
Quellsprache; jede Figur hat dort eine stabile ``uid``. Peter legt den
Abruf unveraendert als ``books/<id>/romanforge/characters.json`` ab
(erzeugt, nie von Hand bearbeiten) und gleicht ihn mit ``names.yaml`` ab.

Eigentum je Feld:
  RomanForge: source, rf_uid, rf_appearance_sha (verknuepfte Eintraege)
  Peter:      target, aliases, type, note, visual, status (nie ueberschrieben)
Eintraege ohne ``rf_uid`` (Orte, Begriffe, Peter-eigene) bleiben unberuehrt,
ausser der einmalige Namensabgleich ordnet sie eindeutig zu.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MIRROR_DIR = "romanforge"
MIRROR_FILE = "characters.json"
MIRROR_FORMAT = "romanforge-characters/1"

NEW = "neu"
LINK = "verknuepfen"
RENAMED = "umbenannt"
APPEARANCE = "aussehen-geaendert"
REMOVED = "in-romanforge-geloescht"
CONFLICT = "konflikt"
UNCHANGED = "unveraendert"


def _clean(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def appearance_sha(appearance: str | None) -> str:
    return hashlib.sha256(_clean(appearance).encode("utf-8")).hexdigest()


def normalize_characters(raw: Any) -> list[dict[str, Any]]:
    """Figurenliste aus einem Handoff-Snapshot, sortiert nach uid. Eintraege ohne uid/Name entfallen."""
    result: list[dict[str, Any]] = []
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict):
            continue
        uid, name = _clean(item.get("uid")), _clean(item.get("name"))
        if not uid or not name:
            continue
        result.append({
            "uid": uid,
            "name": name,
            "role": _clean(item.get("role")) or None,
            "description": _clean(item.get("description")) or None,
            "appearance": _clean(item.get("appearance")) or None,
            "first_appears_chapter": item.get("first_appears_chapter"),
            "updated_at": item.get("updated_at"),
        })
    return sorted(result, key=lambda c: c["uid"])


def mirror_path(book_root: Path | str) -> Path:
    return Path(book_root) / MIRROR_DIR / MIRROR_FILE


def write_mirror(book_root: Path | str, handoff_id: str, characters: list[dict[str, Any]]) -> Path:
    path = mirror_path(book_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "format": MIRROR_FORMAT,
        "generated": "Erzeugt von tools/sync_romanforge_characters.py - nicht von Hand bearbeiten.",
        "handoff_id": handoff_id,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "characters": characters,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def read_mirror(book_root: Path | str) -> dict[str, Any]:
    path = mirror_path(book_root)
    if not path.exists():
        raise FileNotFoundError(f"Kein RomanForge-Spiegel: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass
class Action:
    kind: str
    uid: str
    name: str
    detail: str = ""
    entry_index: int | None = None
    fields: dict[str, Any] = field(default_factory=dict)


def _alias_list(entry: dict[str, Any]) -> list[str]:
    aliases = entry.get("aliases") or []
    if isinstance(aliases, str):
        aliases = [aliases]
    return [_clean(a) for a in aliases if _clean(a)]


def plan_sync(
    entries: list[dict[str, Any]],
    characters: list[dict[str, Any]],
    *,
    same_language: bool,
) -> list[Action]:
    """Berechnet die Abgleich-Aktionen, ohne etwas zu veraendern."""
    actions: list[Action] = []
    by_uid = {
        _clean(e.get("rf_uid")): i for i, e in enumerate(entries) if _clean(e.get("rf_uid"))
    }
    seen_names: dict[str, list[str]] = {}
    for ch in characters:
        seen_names.setdefault(ch["name"].lower(), []).append(ch["uid"])
    duplicate_names = {name for name, uids in seen_names.items() if len(uids) > 1}
    current_uids = {c["uid"] for c in characters}

    for ch in characters:
        uid, name = ch["uid"], ch["name"]
        sha = appearance_sha(ch.get("appearance"))
        if name.lower() in duplicate_names:
            actions.append(Action(CONFLICT, uid, name, "Mehrere Figuren mit gleichem Namen in RomanForge - dort eindeutig machen."))
            continue
        if uid in by_uid:
            idx = by_uid[uid]
            entry = entries[idx]
            fields: dict[str, Any] = {}
            kind, detail = UNCHANGED, ""
            if _clean(entry.get("source")) != name:
                kind = RENAMED
                detail = f"source '{_clean(entry.get('source'))}' -> '{name}'; target und aliases pruefen"
                fields["source"] = name
            if _clean(entry.get("rf_appearance_sha")) != sha:
                if kind == UNCHANGED:
                    kind = APPEARANCE
                    detail = "Aussehen in RomanForge geaendert; Bild-Prompt (visual) pruefen"
                fields["rf_appearance_sha"] = sha
                if entry.get("rf_appearance_sha") is not None:
                    fields["rf_visual_check"] = True
            if entry.get("status") == "removed_in_rf":
                fields["status"] = "draft"
                detail = (detail + "; " if detail else "") + "wieder in RomanForge vorhanden"
                if kind == UNCHANGED:
                    kind = APPEARANCE
            actions.append(Action(kind, uid, name, detail, idx, fields))
            continue
        # Einmaliger Namensabgleich fuer Eintraege ohne rf_uid.
        candidates = [
            i for i, e in enumerate(entries)
            if not _clean(e.get("rf_uid"))
            and name.lower() in {_clean(e.get("source")).lower(), *(a.lower() for a in _alias_list(e))}
        ]
        if len(candidates) == 1:
            actions.append(Action(LINK, uid, name, "ueber Namen/Alias zugeordnet", candidates[0],
                                  {"rf_uid": uid, "rf_appearance_sha": sha}))
        elif len(candidates) > 1:
            actions.append(Action(CONFLICT, uid, name, f"{len(candidates)} Eintraege in names.yaml passen auf den Namen - nicht automatisch zugeordnet."))
        else:
            new_entry: dict[str, Any] = {
                "source": name,
                "target": name if same_language else "",
                "aliases": [],
                "type": "person",
                "status": "draft",
                "rf_uid": uid,
                "rf_appearance_sha": sha,
            }
            if ch.get("role"):
                new_entry["note"] = f"RomanForge-Rolle: {ch['role']}"
            if ch.get("appearance"):
                new_entry["visual"] = ch["appearance"]
            actions.append(Action(NEW, uid, name, "neuer Eintrag (draft)", None, new_entry))

    for uid, idx in by_uid.items():
        if uid not in current_uids and entries[idx].get("status") != "removed_in_rf":
            actions.append(Action(REMOVED, uid, _clean(entries[idx].get("source")),
                                  "in RomanForge nicht mehr vorhanden; Eintrag bleibt, wird markiert", idx,
                                  {"status": "removed_in_rf"}))
    return actions


def apply_sync(entries: list[dict[str, Any]], actions: list[Action]) -> list[dict[str, Any]]:
    """Wendet die Aktionen auf eine Kopie der Eintraege an."""
    result = [dict(e) for e in entries]
    for action in actions:
        if action.kind == NEW:
            result.append(dict(action.fields))
        elif action.entry_index is not None and action.fields:
            result[action.entry_index].update(action.fields)
    return result


def render_plan(actions: list[Action]) -> str:
    if not actions:
        return "Keine Figuren im Spiegel."
    rows = [f"{a.kind:<24} {a.name:<28} {a.uid[:8]}  {a.detail}".rstrip() for a in actions]
    counts: dict[str, int] = {}
    for a in actions:
        counts[a.kind] = counts.get(a.kind, 0) + 1
    summary = ", ".join(f"{k}: {v}" for k, v in sorted(counts.items()))
    return "\n".join(rows) + f"\n\nSumme: {summary}"
