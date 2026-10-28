"""romanforge_client.py - Client fuer die RomanForge-API (Stufe 2).

Liest ROMANFORGE_URL und ROMANFORGE_API_KEY aus der Umgebung und stellt
Methoden zum Abruf von Uebergaben und zum Download von Markdown-Exports bereit.

Die Endpunkte sind als Konstanten am oberen Rand des Moduls gesammelt und
koennen leicht angepasst werden, sobald die genaue API-Struktur von
RomanForge bekannt ist.
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
# Endpunkte (anzupassen an die tatsächliche RomanForge-API)
# ---------------------------------------------------------------------------

#: Pfadrelativ zur Basis-URL, um eine Uebergabe abzufragen.
HANDOFF_GET_PATH = "/api/handoffs/{handoff_id}"

#: Es gibt keinen separaten Export-Endpunkt; der Markdown-Export wird aus den
#: Kapitel-Inhalten der Uebergabe-Antwort aufgebaut (siehe download_export).


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


def get_handoff(config: RomanForgeConfig, handoff_id: str) -> dict[str, Any]:
    """Ruft die Metadaten einer Uebergabe ab.

    Gibt ein dict mit den von der API gelieferten Feldern zurück (z. B.
    titel, autor, kapitel, status). Die genaue Struktur hängt von der
    RomanForge-API ab.
    """
    url = _build_url(config, HANDOFF_GET_PATH, handoff_id=handoff_id)
    raw = _request(config, url)
    import json

    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise RomanForgeError(
            f"Antwort von RomanForge ist kein gültiges JSON ({url}): {exc}"
        ) from exc


def download_export(config: RomanForgeConfig, handoff_id: str) -> str:
    """Lädt den Markdown-Export einer Uebergabe herunter und gibt ihn als Text zurück.

    Schreibt nichts ins Dateisystem; der Aufrufer entscheidet, was mit dem
    Text passiert (z. B. als --source-Ersatz an import_markdown_original.py
    übergeben).
    """
    data = get_handoff_data(config, handoff_id)
    chapters = data.get("chapters", [])
    chapters_sorted = sorted(chapters, key=lambda c: c.get("number", 0))
    lines: list[str] = []
    for ch in chapters_sorted:
        title = ch.get("title") or f"Kapitel {ch.get('number', '?')}"
        content = ch.get("content") or ""
        lines.append("## " + title)
        lines.append("")
        lines.append(content)
        lines.append("")
    return "\n".join(lines)


__all__ = [
    "RomanForgeConfig",
    "RomanForgeError",
    "get_handoff",
    "get_handoff_data",
    "download_export",
]


def get_handoff_data(config: RomanForgeConfig, handoff_id: str) -> dict[str, Any]:
    """Ruft die vollen Uebergabe-Daten ab (Metadaten + Kapitel mit Content).

    Gibt das JSON der RomanForge-API zuruck mit u. a. den Feldern:
    mode, expose, format, handoff, project, chapters, instance, publication.
    """
    url = _build_url(config, HANDOFF_GET_PATH, handoff_id=handoff_id)
    raw = _request(config, url)
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise RomanForgeError(
            "Antwort von RomanForge ist kein gueltiges JSON ({url}): {exc}".format(
                url=url, exc=exc
            )
        ) from exc
