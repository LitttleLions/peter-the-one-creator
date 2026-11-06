"""romanforge_client.py - Client fuer die RomanForge-API (Stufe 2).

Liest ROMANFORGE_URL und ROMANFORGE_API_KEY aus der Umgebung und stellt
Methoden zum Abruf von Uebergaben und zum Aufbau von Markdown-Exports bereit.

Der Endpunkt ist als Konstante am oberen Rand des Moduls gesammelt. Jede
Antwort wird auf Format (``romanforge-handoff/1``) und Modus (``new`` oder
``update``) geprueft; eine andere Version wird nicht still falsch gelesen.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DOTENV_PATH = REPO_ROOT / ".env"


class RomanForgeError(RuntimeError):
    """Fehler beim Umgang mit der RomanForge-API."""


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


@dataclass(frozen=True)
class RomanForgeConfig:
    base_url: str
    api_key: str
    timeout_seconds: int = 60

    @classmethod
    def from_env(cls) -> "RomanForgeConfig":
        # .env laden, falls noch nicht geschehen (wie openrouter_client.py)
        load_dotenv(DOTENV_PATH, override=False)
        base_url = _env("ROMANFORGE_URL", "").rstrip("/")
        api_key = _env("ROMANFORGE_API_KEY", "")
        if not base_url:
            raise RomanForgeError(
                "ROMANFORGE_URL ist nicht in der Umgebung gesetzt (.env)."
            )
        if not api_key:
            raise RomanForgeError(
                "ROMANFORGE_API_KEY ist nicht in der Umgebung gesetzt (.env)."
            )
        return cls(base_url=base_url, api_key=api_key)


# ---------------------------------------------------------------------------
# Endpunkt und unterstuetztes Format der RomanForge-API
# ---------------------------------------------------------------------------

#: Pfadrelativ zur Basis-URL, um eine Uebergabe abzufragen.
HANDOFF_GET_PATH = "/api/handoffs/{handoff_id}"

#: Es gibt keinen separaten Export-Endpunkt; der Markdown-Export wird aus den
#: Kapitel-Inhalten der Uebergabe-Antwort aufgebaut (siehe export_text_from_data).

#: Einziges Format, das peter versteht (Feld ``format`` der Antwort).
SUPPORTED_FORMAT = "romanforge-handoff/1"
#: Erlaubte Werte des Felds ``mode``.
SUPPORTED_MODES = ("new", "update")


def check_handoff_data(data: Any, url: str = "") -> dict[str, Any]:
    """Prueft Format und Modus einer Uebergabe-Antwort und gibt sie unveraendert zurueck."""
    if not isinstance(data, dict):
        raise RomanForgeError(f"Antwort von RomanForge ist kein JSON-Objekt ({url}).")
    fmt = data.get("format")
    if fmt != SUPPORTED_FORMAT:
        raise RomanForgeError(
            f"Unbekanntes Uebergabe-Format {fmt!r} ({url}); peter versteht nur "
            f"{SUPPORTED_FORMAT!r}. tools/lib/romanforge_client.py und "
            "tools/import_markdown_original.py muessen fuer das neue Format angepasst werden."
        )
    mode = data.get("mode")
    if mode not in SUPPORTED_MODES:
        raise RomanForgeError(
            f"Unbekannter Uebergabe-Modus {mode!r} ({url}); erlaubt sind {', '.join(SUPPORTED_MODES)}."
        )
    return data


def _build_url(config: RomanForgeConfig, path_template: str, **kwargs: Any) -> str:
    path = path_template.format(**kwargs)
    return f"{config.base_url}{path}"


def _request(config: RomanForgeConfig, url: str) -> bytes:
    """Führt eine GET-Anfrage gegen die RomanForge-API durch und gibt den Rohkörper zurück."""
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Accept": "text/markdown, text/plain, */*",
        "User-Agent": "peter-the-one-creator/romanforge-client/1.0",
    }
    request = Request(url, headers=headers, method="GET")
    try:
        with urlopen(request, timeout=config.timeout_seconds) as response:
            return response.read()
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        raise RomanForgeError(
            f"RomanForge-API Fehler {exc.code} für {url}: {body}"
        ) from exc
    except URLError as exc:
        raise RomanForgeError(f"RomanForge-API nicht erreichbar ({url}): {exc}") from exc


def get_handoff_data(config: RomanForgeConfig, handoff_id: str) -> dict[str, Any]:
    """Ruft die vollen Uebergabe-Daten ab (Metadaten + Kapitel mit Content).

    Gibt das gepruefte JSON der RomanForge-API zurueck mit u. a. den Feldern:
    mode, expose, format, handoff, project, chapters, instance, publication,
    characters.
    """
    url = _build_url(config, HANDOFF_GET_PATH, handoff_id=handoff_id)
    raw = _request(config, url)
    try:
        data = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise RomanForgeError(
            "Antwort von RomanForge ist kein gueltiges JSON ({url}): {exc}".format(
                url=url, exc=exc
            )
        ) from exc
    return check_handoff_data(data, url)


def get_handoff(config: RomanForgeConfig, handoff_id: str) -> dict[str, Any]:
    """Ruft eine Uebergabe ab (gleich wie ``get_handoff_data``)."""
    return get_handoff_data(config, handoff_id)


def _chapters_sorted(data: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(data.get("chapters", []), key=lambda c: c.get("number", 0))


def export_text_from_data(data: dict[str, Any]) -> str:
    """Baut den Markdown-Export (``## Titel`` + Inhalt je Kapitel) aus den Uebergabe-Daten.

    Schreibt nichts ins Dateisystem; der Aufrufer entscheidet, was mit dem
    Text passiert (z. B. als --source-Ersatz an import_markdown_original.py).
    """
    lines: list[str] = []
    for ch in _chapters_sorted(data):
        title = ch.get("title") or f"Kapitel {ch.get('number', '?')}"
        content = ch.get("content") or ""
        lines.append("## " + title)
        lines.append("")
        lines.append(content)
        lines.append("")
    return "\n".join(lines)


def chapter_rf_ids(data: dict[str, Any]) -> list[str | None]:
    """Kapitel-IDs (``chapters.id`` in RomanForge) in der Reihenfolge des Exports."""
    return [str(ch["id"]) if ch.get("id") is not None else None for ch in _chapters_sorted(data)]


def download_export(config: RomanForgeConfig, handoff_id: str) -> str:
    """Laedt eine Uebergabe und gibt den Markdown-Export als Text zurueck (ein Abruf)."""
    return export_text_from_data(get_handoff_data(config, handoff_id))


__all__ = [
    "RomanForgeConfig",
    "RomanForgeError",
    "SUPPORTED_FORMAT",
    "check_handoff_data",
    "chapter_rf_ids",
    "export_text_from_data",
    "get_handoff",
    "get_handoff_data",
    "download_export",
]
