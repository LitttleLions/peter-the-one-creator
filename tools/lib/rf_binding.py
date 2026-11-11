"""rf_binding.py - feste Bindung eines Buchpakets an ein RomanForge-Projekt.

Die Zuordnung laeuft ueber ``instance`` (Host) und ``project_id`` in
``books/<id>/book.yaml`` (Block ``romanforge:``), nie ueber den Titel:

    romanforge:
      instance: romanforge.example.de
      project_id: 8

Der Schluessel muss unter allen Buechern eindeutig sein. Buecher ohne Block
(z. B. Uebersetzungen fremder Vorlagen) werden von RomanForge-Werkzeugen nicht
angefasst. Reine Funktionen, keine Netzwerkzugriffe.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

BLOCK_KEY = "romanforge"


def normalize_host(url: str | None) -> str:
    """Host (mit Port, klein) einer URL oder eines Hosts; das Schema zaehlt nicht.

    Die Uebergabe nennt die Instanz aus Proxy-Headern (oft ``http://``), die
    .env meist ``https://``; verglichen wird deshalb nur der Host.
    """
    text = (url or "").strip()
    if not text:
        return ""
    if "//" not in text:
        text = "//" + text
    return (urlsplit(text).netloc or "").lower()


def read_binding(book_cfg: dict[str, Any]) -> tuple[str, int] | None:
    """(Host, Projekt-ID) aus der Buchkonfiguration oder None ohne gueltigen Block."""
    block = book_cfg.get(BLOCK_KEY)
    if not isinstance(block, dict):
        return None
    host = normalize_host(str(block.get("instance") or ""))
    try:
        project_id = int(block.get("project_id"))
    except (TypeError, ValueError):
        return None
    return (host, project_id) if host else None


def handoff_key(handoff_data: dict[str, Any]) -> tuple[str, int] | None:
    """(Host, Projekt-ID) aus den Uebergabe-Daten."""
    host = normalize_host(str(handoff_data.get("instance") or ""))
    try:
        project_id = int((handoff_data.get("project") or {}).get("id"))
    except (TypeError, ValueError):
        return None
    return (host, project_id) if host else None


def find_bound(books: list[tuple[str, dict[str, Any]]], key: tuple[str, int]) -> list[str]:
    """Buch-IDs, deren Bindung genau diesem Schluessel entspricht. books: (id, Konfiguration)."""
    return [book_id for book_id, cfg in books if read_binding(cfg) == key]


def check_update(
    *,
    book_id: str,
    book_cfg: dict[str, Any],
    handoff_data: dict[str, Any],
    env_url: str,
    books: list[tuple[str, dict[str, Any]]],
    state_rf_ids: list[str],
    snapshot_ids: list[str],
) -> list[str]:
    """Fehlermeldungen fuer eine Aktualisierung (leer = alles in Ordnung)."""
    errors: list[str] = []
    key = handoff_key(handoff_data)
    if key is None:
        return ["Uebergabe nennt keine Instanz oder Projekt-ID."]
    if normalize_host(env_url) != key[0]:
        errors.append(
            f"Instanz der Uebergabe ({key[0]}) passt nicht zu ROMANFORGE_URL ({normalize_host(env_url) or '-'}). "
            "Falsche Umgebung?"
        )
    binding = read_binding(book_cfg)
    if binding is None:
        errors.append(
            f"Buch '{book_id}' ist nicht an RomanForge gebunden. Erst pruefen und binden: "
            f"--book {book_id} --handoff <id> --bind (Trockenlauf), dann mit --apply."
        )
    elif binding != key:
        errors.append(
            f"Buch '{book_id}' ist an {binding[0]} Projekt {binding[1]} gebunden, "
            f"die Uebergabe gehoert zu {key[0]} Projekt {key[1]}."
        )
    others = [other for other in find_bound(books, key) if other != book_id]
    if others:
        errors.append(
            f"Mehrere Buecher tragen dieselbe Bindung ({key[0]} Projekt {key[1]}): "
            f"{', '.join(sorted([book_id, *others]))}. Doppelablage bereinigen."
        )
    if binding == key and state_rf_ids and not set(state_rf_ids) & set(snapshot_ids):
        errors.append(
            "Keine einzige Kapitel-ID aus state.yaml kommt in der Uebergabe vor; "
            "das Buch passt nicht zu diesem Projekt."
        )
    return errors


def prove_by_chapters(
    *,
    state_chapters: dict[str, Any],
    snapshot_ids: list[str],
    snapshot_hashes: list[str],
) -> tuple[bool, str]:
    """Beweist ueber Inhalte, dass ein Buch zu einer Uebergabe gehoert.

    Erst Kapitel-IDs (rf_id), sonst Textstand (rf_base). Die Mehrheit der
    Kapitel muss uebereinstimmen. Rueckgabe: (bewiesen, Begruendung).
    """
    chapters = [c for c in state_chapters.values() if isinstance(c, dict)]
    if not chapters:
        return False, "state.yaml enthaelt keine Kapitel."
    with_id = [str(c["rf_id"]) for c in chapters if c.get("rf_id")]
    if with_id:
        hits = sum(1 for rid in with_id if rid in set(snapshot_ids))
        ok = hits * 2 >= len(with_id)
        return ok, f"Kapitel-IDs: {hits} von {len(with_id)} passen zur Uebergabe."
    bases = [str(c["rf_base"]) for c in chapters if c.get("rf_base")]
    if not bases:
        return False, "Weder rf_id noch rf_base in state.yaml."
    known = set(snapshot_hashes)
    hits = sum(1 for base in bases if base in known)
    return hits * 2 >= len(bases), f"Textstand: {hits} von {len(bases)} Kapiteln stimmen mit der Uebergabe ueberein."


def binding_block(host: str, project_id: int) -> str:
    return (
        "\n# Feste Zuordnung zum RomanForge-Projekt (nicht ueber den Titel suchen)\n"
        f"{BLOCK_KEY}:\n  instance: {host}\n  project_id: {int(project_id)}\n"
    )


def append_binding(book_yaml: Path, host: str, project_id: int) -> None:
    """Haengt den Block ans Dateiende; die Datei wird nicht neu serialisiert (Kommentare bleiben)."""
    text = book_yaml.read_text(encoding="utf-8")
    if f"\n{BLOCK_KEY}:" in "\n" + text:
        raise ValueError(f"{book_yaml} enthaelt bereits einen '{BLOCK_KEY}:'-Block.")
    if text and not text.endswith("\n"):
        text += "\n"
    book_yaml.write_text(text + binding_block(host, project_id), encoding="utf-8")
