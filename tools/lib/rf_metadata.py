"""rf_metadata.py - Buchangaben (Metadaten) aus RomanForge nach peter uebernehmen.

RomanForge ist fuer diese Angaben die Quelle. Pro Uebergabe gibt es EINE Pruefung:
ist nichts zu tun, kommt eine Zeile, sonst nur die betroffenen Felder.

Regeln je Feld (Tabelle FIELDS):
  ueberschreiben  kurze Identitaetsfelder (Autor, Untertitel, Reihe, Band, Verlag, Herausgeber,
                  Herausgabevermerk): RomanForge gewinnt immer.
  folgt           Langtexte (Klappentext): folgt RomanForge nur, wenn der peter-Wert leer oder seit der
                  letzten Uebernahme unberuehrt ist (Hash wie bei rf_appearance_sha); sonst Markierung.
  melden          Titel: nur melden, nie schreiben (Arbeitstitel in RomanForge, Buchtitel in peter).
Ein leerer RomanForge-Wert aendert in peter nie etwas.

Geschrieben wird per gezieltem Zeilenersatz in book.yaml / export.yaml (Kommentare und
Blockformen bleiben); das Ergebnis wird vor dem Schreiben gegengeprueft. Reine Funktionen
plus Datei-Zugriff auf das Buchpaket, keine Netzwerkzugriffe.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

OVERWRITE = "ueberschreiben"
FOLLOW = "folgt"
REPORT = "melden"

# Aktionen
UNCHANGED = "unveraendert"
SET = "setzen"
FOLLOWED = "nachziehen"
DIVERGED = "weicht-ab"
ADOPT = "angeglichen"
REPORTED = "abweichender-titel"

MIRROR_NAME = "metadata.json"


@dataclass(frozen=True)
class Field:
    rf_key: str
    label: str
    mode: str
    #: (Datei, Block oder None fuer oberste Ebene, Schluessel); der erste Eintrag gilt als aktueller Wert.
    targets: tuple[tuple[str, str | None, str], ...]


FIELDS: tuple[Field, ...] = (
    Field("title", "Titel", REPORT, (("export.yaml", "book", "title"),)),
    Field("author_name", "Autor", OVERWRITE,
          (("export.yaml", "book", "author"), ("book.yaml", None, "author"))),
    Field("subtitle", "Untertitel", OVERWRITE, (("export.yaml", "book", "subtitle"),)),
    Field("series_name", "Reihe", OVERWRITE, (("export.yaml", "book", "series"),)),
    Field("series_number", "Band", OVERWRITE, (("export.yaml", "book", "series_volume"),)),
    Field("publisher", "Verlag", OVERWRITE, (("export.yaml", "book", "publisher"),)),
    Field("editor_name", "Herausgeber", OVERWRITE, (("export.yaml", "book", "editor"),)),
    Field("editor_note", "Herausgabevermerk", OVERWRITE, (("export.yaml", "book", "editor_note"),)),
    Field("blurb", "Klappentext", FOLLOW, (("export.yaml", "book", "description"),)),
)

FIELD_BY_KEY = {f.rf_key: f for f in FIELDS}


@dataclass
class Action:
    rf_key: str
    label: str
    kind: str
    rf_value: str
    current: str
    note: str = ""


# ---------------------------------------------------------------------------
# Werte
# ---------------------------------------------------------------------------

def norm(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("\r\n", "\n").strip()


def sha(value: Any) -> str:
    return hashlib.sha256(norm(value).encode("utf-8")).hexdigest()


def rf_values(handoff_data: dict[str, Any]) -> dict[str, str]:
    """Alle Felder aus der Uebergabe als normalisierte Texte ('' = leer)."""
    publication = handoff_data.get("publication") or {}
    project = handoff_data.get("project") or {}
    values = {f.rf_key: norm(publication.get(f.rf_key)) for f in FIELDS if f.rf_key != "title"}
    values["title"] = norm(project.get("title"))
    return values


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def read_target(book_root: Path, target: tuple[str, str | None, str]) -> str:
    filename, parent, key = target
    data = _load(book_root / filename)
    node = data.get(parent) if parent else data
    return norm(node.get(key)) if isinstance(node, dict) else ""


def current_values(book_root: Path) -> dict[str, str]:
    return {f.rf_key: read_target(book_root, f.targets[0]) for f in FIELDS}


# ---------------------------------------------------------------------------
# Spiegel (zuletzt uebernommene RomanForge-Werte als Hash)
# ---------------------------------------------------------------------------

def mirror_path(book_root: Path) -> Path:
    return book_root / "romanforge" / MIRROR_NAME


def read_mirror(book_root: Path) -> dict[str, Any]:
    path = mirror_path(book_root)
    if not path.exists():
        return {"handoff_id": "", "adopted": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("adopted", {})
    return data


def write_mirror(book_root: Path, handoff_id: str, adopted: dict[str, str]) -> Path:
    path = mirror_path(book_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"handoff_id": handoff_id, "adopted": adopted}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


# ---------------------------------------------------------------------------
# Plan
# ---------------------------------------------------------------------------

def plan_metadata(rf: dict[str, str], current: dict[str, str], adopted: dict[str, str]) -> list[Action]:
    actions: list[Action] = []
    for f in FIELDS:
        new, now = rf.get(f.rf_key, ""), current.get(f.rf_key, "")
        if not new:
            actions.append(Action(f.rf_key, f.label, UNCHANGED, new, now, "in RomanForge leer"))
            continue
        if new == now:
            kind = UNCHANGED if adopted.get(f.rf_key) == sha(new) or f.mode == REPORT else ADOPT
            actions.append(Action(f.rf_key, f.label, kind, new, now))
            continue
        if f.mode == REPORT:
            actions.append(Action(f.rf_key, f.label, REPORTED, new, now,
                                  "wird nie geschrieben (Arbeitstitel in RomanForge)"))
        elif f.mode == OVERWRITE:
            actions.append(Action(f.rf_key, f.label, SET, new, now,
                                  "RomanForge gewinnt" if now else "war leer"))
        else:  # FOLLOW
            untouched = not now or adopted.get(f.rf_key) == sha(now)
            if untouched:
                actions.append(Action(f.rf_key, f.label, FOLLOWED, new, now))
            else:
                actions.append(Action(f.rf_key, f.label, DIVERGED, new, now,
                                      "in peter von Hand geaendert; mit --force-meta " + f.rf_key + " uebernehmen"))
    return actions


def pending(actions: list[Action]) -> list[Action]:
    return [a for a in actions if a.kind not in (UNCHANGED,)]


def render_report(actions: list[Action]) -> str:
    rows = pending(actions)
    if not rows:
        return "Metadaten unveraendert."

    def short(text: str) -> str:
        flat = " ".join(text.split())
        return flat if len(flat) <= 60 else flat[:57] + "..."

    lines = ["| Feld | Aktion | RomanForge | peter | Hinweis |", "|---|---|---|---|---|"]
    for a in rows:
        lines.append(f"| {a.label} | {a.kind} | {short(a.rf_value)} | {short(a.current) or '-'} | {a.note} |")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Schreiben: gezielter Zeilenersatz
# ---------------------------------------------------------------------------

def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def render_key(key: str, value: str, indent: int, number: bool = False) -> list[str]:
    pad = " " * indent
    if "\n" in value and not value.startswith((" ", "\n")):
        lines = [f"{pad}{key}: |-"]
        lines.extend(f"{pad}  {row}".rstrip() if row else "" for row in value.split("\n"))
        return lines
    data: Any = int(value) if number and value.lstrip("-").isdigit() else value
    dumped = yaml.safe_dump({key: data}, allow_unicode=True, default_flow_style=False, width=10**6)
    return [f"{pad}{row}" for row in dumped.rstrip("\n").split("\n")]


def set_key(text: str, parent: str | None, key: str, value: str, number: bool = False) -> str:
    """Setzt `key` (oberste Ebene oder direkt unter `parent:`) per Zeilenersatz; Rest der Datei bleibt."""
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.replace("\r\n", "\n").split("\n")
    trailing_newline = text.endswith("\n")
    if trailing_newline:
        lines = lines[:-1]
    if parent:
        start = next((i for i, row in enumerate(lines) if re.match(rf"^{re.escape(parent)}:\s*(#.*)?$", row)), None)
        if start is None:
            raise ValueError(f"Block '{parent}:' nicht gefunden.")
        end = len(lines)
        for i in range(start + 1, len(lines)):
            row = lines[i]
            if row.strip() and not row.lstrip().startswith("#") and _indent_of(row) == 0:
                end = i
                break
        lo, hi, indent = start + 1, end, 2
    else:
        lo, hi, indent = 0, len(lines), 0

    key_re = re.compile(rf"^{' ' * indent}{re.escape(key)}:(\s|$)")
    found = next((i for i in range(lo, hi) if key_re.match(lines[i])), None)
    new_rows = render_key(key, value, indent, number)
    if found is None:
        insert_at = hi
        while insert_at > lo and not lines[insert_at - 1].strip():
            insert_at -= 1
        lines[insert_at:insert_at] = new_rows
    else:
        stop = found + 1
        while stop < hi:
            row = lines[stop]
            if (not row.strip()) or _indent_of(row) > indent or (_indent_of(row) == indent and row.lstrip().startswith("- ")):
                stop += 1
                continue
            break
        while stop > found + 1 and not lines[stop - 1].strip():
            stop -= 1
        lines[found:stop] = new_rows
    out = eol.join(lines)
    return out + (eol if trailing_newline else "")


def _verify(text: str, parent: str | None, key: str, expected: str) -> None:
    data = yaml.safe_load(text) or {}
    node = data.get(parent) if parent else data
    got = norm(node.get(key)) if isinstance(node, dict) else None
    if got != norm(expected):
        raise ValueError(f"Gegenpruefung fehlgeschlagen fuer {key}: gelesen {got!r}")


def write_field(book_root: Path, f: Field, value: str) -> None:
    for filename, parent, key in f.targets:
        path = book_root / filename
        if not path.exists():
            continue
        with open(path, encoding="utf-8", newline="") as handle:
            text = handle.read()
        patched = set_key(text, parent, key, value, number=(f.rf_key == "series_number"))
        _verify(patched, parent, key, value)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(patched)


def apply_actions(
    book_root: Path, actions: list[Action], handoff_id: str, force: set[str] | None = None,
    adopted: dict[str, str] | None = None,
) -> list[str]:
    """Schreibt SET/FOLLOWED (und erzwungene DIVERGED) sowie den Spiegel. Gibt Hinweise zurueck."""
    force = force or set()
    adopted = dict(adopted if adopted is not None else read_mirror(book_root)["adopted"])
    notes: list[str] = []
    for a in actions:
        f = FIELD_BY_KEY[a.rf_key]
        write = a.kind in (SET, FOLLOWED) or (a.kind == DIVERGED and a.rf_key in force)
        if write:
            write_field(book_root, f, a.rf_value)
        if write or a.kind == ADOPT:
            adopted[a.rf_key] = sha(a.rf_value)
    write_mirror(book_root, handoff_id, adopted)
    export = _load(book_root / "export.yaml").get("book") or {}
    if norm(export.get("editor")) and norm(export.get("translator")):
        notes.append(
            "Hinweis: export.yaml hat Herausgeber (editor) und Uebersetzer (translator); die Titelei zeigt dann "
            "nur den Uebersetzer. Bei einem Original translator leeren."
        )
    return notes
