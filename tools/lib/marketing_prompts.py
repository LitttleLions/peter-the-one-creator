"""
marketing_prompts.py
====================

Promptbau, Antwortauswertung und Provenienz fuer die Marketingtexte.

Der Datenbrief kommt aus :mod:`lib.marketing_campaign` und enthaelt Metadaten,
Glossar und eine echte Leseprobe -- bewusst nicht den ganzen Roman. Die Texte
enthalten keine Links; die Adressen setzt der Exporter beim Rendern zusammen,
damit ein spaeter nachgetragener Amazon- oder YouTube-Link keine neue
Textgenerierung ausloest.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

from lib import marketing_campaign as campaign  # noqa: E402
from lib.output_paths import archive_sent_prompt, book_output_root  # noqa: E402

PROMPT_VERSION = campaign.PROMPT_VERSION
URL_PATTERN = campaign.URL_PATTERN

SYSTEM_PROMPT = """Du schreibst Verkaufsbegleittexte fuer eine deutsche \
Buchausgabe der Marke Motivatier Classics.

Harte Regeln:
- Erfasse ausschliesslich Aussagen, die aus dem gelieferten Datenbrief belegt
  sind. Erfinde keine Rezensionen, Zitate, Auszeichnungen, Verkaufszahlen,
  biografischen oder historischen Tatsachen.
- Erfinde keine Textstellen. Wenn du eine Buchpassage zitierst, nutze nur die
  gelieferte Leseprobe und kennzeichne sie als Zitat aus der Ausgabe.
- Schreibe keine werblichen Saetze, die wie ein Zitat des Autors wirken.
- "Jetzt erschienen" nur, wenn der Datenbrief das ausdruecklich belegt. Sonst
  nutze "Unsere Ausgabe", "Heute stellen wir vor" oder einen direkten
  inhaltlichen Einstieg.
- Keine generischen Superlative, keine kuenstliche Dringlichkeit, keine
  erfundenen Leserreaktionen, keine Hashtag-Wolken.
- Variiere Satzbau und Einstieg zwischen den Beitraegen. Wiederhole nicht den
  Klappentext.
- Beschreibe die Ausgabe nur mit belegbaren Eigenschaften.
- Jeder Beitrag hat einen klaren naechsten Schritt, aber KEINE URL im Text:
  die Adressen haengt das Exportprogramm an.
- Rede ueber das Buch, nicht ueber die Kampagne."""


def _bullet_block(lines: list[str], empty: str = "- (keine Angabe)") -> list[str]:
    return lines or [empty]


def render_brief(brief: dict[str, Any]) -> str:
    """Baut den User-Prompt aus dem Datenbrief."""
    parts: list[str] = [
        "Datenbrief zur Ausgabe:",
        "",
        f"- Buch-ID: {brief.get('book_id')}",
        f"- Titel: {brief.get('title')}",
        f"- Untertitel: {brief.get('subtitle')}",
        f"- Autor: {brief.get('author')}",
        f"- Originaltitel: {brief.get('original_title')}",
        f"- Originalautor: {brief.get('original_author')}",
        f"- Uebersetzung/Einrichtung: {brief.get('translator')} "
        f"({brief.get('translator_label')})",
        f"- Herausgeber: {brief.get('publisher')}",
        f"- Sprache: {brief.get('language')}",
        f"- Marke: {(brief.get('brand') or {}).get('label')}",
        "",
        "Kurzbeschreibung:",
        str(brief.get("description") or "(keine)"),
        "",
        "Ausfuehrliche Inhaltsbeschreibung:",
        str(brief.get("summary") or "(keine)"),
        "",
        "Zum Autor:",
        str(brief.get("author_bio") or "(keine)"),
        "",
        "Belegte Editionsangaben:",
    ]
    parts += _bullet_block(
        [f"- {item}" for item in (brief.get("edition_notes") or [])]
    )
    parts += ["", "Namensglossar (Schreibweise verbindlich):"]
    parts += _bullet_block(list(brief.get("names") or []))
    sample = brief.get("sample_passage") or {}
    parts += ["", "Echte Leseprobe aus der fertigen deutschen Ausgabe:"]
    if sample:
        parts += [
            f"(Quelle: Kapitel {sample.get('chapter')}, Szene {sample.get('scene')})",
            "",
            f'"{sample.get("text")}"',
        ]
    else:
        parts.append("(keine verfuegbar)")
    song = brief.get("song")
    parts += ["", "Musikmaterial:"]
    if song:
        parts += [
            f"- Songtitel: {song.get('title') or '(ohne Titel)'}",
            f"- KI-Kennzeichnung der Musik: {song.get('ai_generated')}",
        ]
        parts += _bullet_block(
            [f"- Credit: {item}" for item in (song.get("credits") or [])]
        )
    else:
        parts.append("- kein Song vorhanden; musikalische Beitraege entfallen")
    return "\n".join(parts)


def response_schema(brief: dict[str, Any]) -> str:
    limits = brief.get("limits") or {}
    schema = {
        "texts": {
            "x-t0-intro": {
                "text": "<Buchvorstellung: zentraler Konflikt, Titel und Autor, "
                "belegbare Aussage zur Ausgabe>",
                "notes": "<kurze Begruendung der Motivwahl>",
            },
            "x-t1-song": {"text": "<nur wenn ein Song vorhanden ist, sonst leer>"},
            "x-t2-youtube": {
                "text": "<Ankuendigung des vollstaendigen Songs; ohne 'jetzt online', "
                "solange die Veroeffentlichung nicht belegt ist>"
            },
            "x-t5-content": {"text": "<eigenstaendiger inhaltlicher Gedanke>"},
            "x-t8-sample": {
                "text": "<kurze echte Passage mit Zitatkennzeichnung oder eine "
                "belegbare Besonderheit der Ausgabe>"
            },
            "x-t12-second-angle": {
                "text": "<zweiter Aspekt, andere Perspektive als T+0 und T+5>"
            },
        },
        "youtube": {
            "title": "<Titel nach Muster 'Buchtitel - Songtitel | Lied zum Roman von Autor'>",
            "prequel": "<eine bis zwei Saetze Vorschau>",
            "body": "<zwei bis vier Saetze zu Roman und musikalischer Interpretation>",
            "thumbnail_label": "<kurze Beschriftung fuer das Vorschaubild>",
            "shorts": {
                "yt-short-1": {
                    "title": "<Titel>",
                    "description": "<kurze Beschreibung>",
                    "overlays": ["<Texteinblendung 1>", "<Texteinblendung 2>"],
                },
                "yt-short-2": {
                    "title": "<Titel>",
                    "description": "<kurze Beschreibung>",
                    "overlays": ["<Texteinblendung 1>", "<Texteinblendung 2>"],
                },
            },
        },
    }
    return "\n".join(
        [
            "Laengenvorgaben (gewichtet, URLs zaehlen als 23 Zeichen):",
            f"- X-Beitraege: hoechstens {limits.get('x_weighted_chars')} Zeichen, "
            f"Ziel {limits.get('x_target_min')}-{limits.get('x_target_max')} Zeichen, "
            "eine bis drei kurze Absaetze, kein Link im Text",
            f"- YouTube-Titel: hoechstens {limits.get('youtube_title_chars')} Zeichen",
            f"- YouTube-Beschreibung: hoechstens "
            f"{limits.get('youtube_description_chars')} Zeichen",
            "",
            "Liefere ausschliesslich JSON in genau dieser Struktur:",
            "",
            json.dumps(schema, ensure_ascii=False, indent=2),
            "",
            "Musikalische Bestandteile (x-t1-song, x-t2-youtube, youtube) bleiben leer, "
            "wenn kein Song vorhanden ist. Erfinde keine Instrumentierung, Stimmlage "
            "oder Klangfarbe.",
        ]
    )


def build_prompt(brief: dict[str, Any]) -> tuple[str, str]:
    return SYSTEM_PROMPT, render_brief(brief) + "\n\n" + response_schema(brief)


# ---------------------------------------------------------------------------
# Antwort auswerten
# ---------------------------------------------------------------------------


def extract_json(text: str) -> dict[str, Any]:
    """Liest das erste JSON-Objekt aus einer Modellantwort."""
    cleaned = str(text or "").strip()
    fence = re.search(r"```(?:json)?\s*(.+?)```", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1).strip()
    start = cleaned.find("{")
    if start < 0:
        raise ValueError("Antwort enthaelt kein JSON-Objekt")
    try:
        payload, _ = json.JSONDecoder().raw_decode(cleaned[start:])
    except json.JSONDecodeError as exc:
        raise ValueError(f"Antwort ist kein gueltiges JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Antwort-JSON ist kein Objekt")
    return payload


def validate_payload(
    payload: dict[str, Any], brief: dict[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    """Prueft die Modellantwort gegen die Beitragsfunktionen.

    URLs werden aus den Texten entfernt (der Exporter setzt sie selbst);
    musikalische Beitraege ohne Song werden verworfen.
    """
    problems: list[str] = []
    texts_in = payload.get("texts") or {}
    if not isinstance(texts_in, dict):
        problems.append("texts ist kein Objekt")
        texts_in = {}
    has_song = bool(brief.get("song"))
    clean_texts: dict[str, dict[str, Any]] = {}
    for post_id, entry in texts_in.items():
        if post_id not in campaign.POST_SPEC_BY_ID:
            problems.append(f"unbekannte Beitrags-ID ignoriert: {post_id}")
            continue
        if not isinstance(entry, dict):
            problems.append(f"{post_id}: Eintrag ist kein Objekt")
            continue
        spec = campaign.POST_SPEC_BY_ID[post_id]
        if "song" in spec.needs and not has_song:
            problems.append(f"{post_id}: ohne Song verworfen")
            continue
        value = str(entry.get("text") or "").strip()
        if URL_PATTERN.search(value):
            problems.append(f"{post_id}: URL aus dem Text entfernt")
            value = URL_PATTERN.sub("", value).strip()
        if not value:
            problems.append(f"{post_id}: leerer Text")
            continue
        clean: dict[str, Any] = {"text": value}
        if entry.get("notes"):
            clean["notes"] = str(entry["notes"]).strip()
        clean_texts[post_id] = clean

    youtube_in = payload.get("youtube") or {}
    youtube: dict[str, Any] = {}
    if isinstance(youtube_in, dict) and youtube_in:
        if not has_song:
            problems.append("youtube: ohne Song verworfen")
        else:
            shorts_in = youtube_in.get("shorts") or {}
            shorts: dict[str, Any] = {}
            for short_id in ("yt-short-1", "yt-short-2"):
                entry = shorts_in.get(short_id) if isinstance(shorts_in, dict) else None
                if not isinstance(entry, dict):
                    continue
                shorts[short_id] = {
                    "title": str(entry.get("title") or "").strip(),
                    "description": str(entry.get("description") or "").strip(),
                    "overlays": [
                        str(item).strip()
                        for item in (entry.get("overlays") or [])
                        if str(item).strip()
                    ],
                }
            youtube = {
                key: str(youtube_in.get(key) or "").strip()
                for key in ("title", "prequel", "body", "thumbnail_label")
            }
            if shorts:
                youtube["shorts"] = shorts
    return {"texts": clean_texts, "youtube": youtube}, problems


# ---------------------------------------------------------------------------
# Texte erzeugen und ablegen
# ---------------------------------------------------------------------------


def _payload(
    book: dict[str, Any],
    brief: dict[str, Any],
    style: str,
    *,
    generator: str,
    model: str = "",
    texts: dict[str, Any] | None = None,
    youtube: dict[str, Any] | None = None,
    usage: dict[str, Any] | None = None,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": campaign.SCHEMA_VERSION,
        "book_id": str(book.get("id")),
        "style": style,
        "generator": generator,
        "model": model,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "prompt_version": PROMPT_VERSION,
        "source_hash": campaign.source_hash(brief),
        "usage": usage or {},
        "notes": list(notes or []),
        "texts": texts or {},
        "youtube": youtube or {},
    }


def write_generated(
    book: dict[str, Any], repo_root: Path, payload: dict[str, Any]
) -> Path:
    """Schreibt ``work/marketing/generated.json`` (getrennt von Overrides)."""
    path = campaign.generated_path(campaign.book_root(book, repo_root))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="",
    )
    return path


def prompt_file_path(book: dict[str, Any], repo_root: Path, style: str) -> Path:
    output_root = book_output_root(repo_root, book)
    return (
        output_root / "prompts" / "marketing" / f"{book.get('id')}-marketing-{style}.md"
    )


def write_prompt_file(
    book: dict[str, Any],
    repo_root: Path,
    style: str,
    brief: dict[str, Any],
    system: str,
    user: str,
) -> Path:
    """Schreibt den vollstaendigen Prompt als Datei (Provider ``prompt_file``)."""
    path = prompt_file_path(book, repo_root, style)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Marketingprompt {book.get('id')} ({style})",
        "",
        f"- Prompt-Version: {PROMPT_VERSION}",
        f"- Quellpruefsumme: {campaign.source_hash(brief)}",
        "- Ergebnis: Antwort als JSON in work/marketing/generated.json ablegen "
        "(Felder texts/youtube).",
        "",
        "## System",
        "",
        system,
        "",
        "## User",
        "",
        user,
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8", newline="")
    return path


def write_workspace_order(
    book: dict[str, Any],
    repo_root: Path,
    style: str,
    brief: dict[str, Any],
    system: str,
    user: str,
) -> Path:
    """Arbeitsanweisung fuer eine KI, die direkt im Repo arbeitet.

    Provider ``workspace_ai``: Die KI im Editor fuellt ``generated.json`` nach
    dieser Anweisung; es entstehen keine API-Kosten.
    """
    book_root_dir = campaign.book_root(book, repo_root)
    path = book_root_dir / "work" / "marketing" / "generation-request.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    target = campaign.generated_path(book_root_dir)
    skeleton = {
        "schema_version": campaign.SCHEMA_VERSION,
        "book_id": str(book.get("id")),
        "style": style,
        "generator": "workspace_ai",
        "model": "<Modellname der bearbeitenden KI>",
        "generated_at": "<ISO 8601>",
        "prompt_version": PROMPT_VERSION,
        "source_hash": campaign.source_hash(brief),
        "texts": {},
        "youtube": {},
    }
    lines = [
        f"# Arbeitsanweisung: Marketingtexte fuer {brief.get('title')}",
        "",
        "Ziel: die Datei",
        "",
        "```text",
        campaign.rel_path(repo_root, target),
        "```",
        "",
        "befuellen. Struktur: `texts` (Beitrags-IDs) und `youtube`. Kopfdaten:",
        "",
        "```json",
        json.dumps(skeleton, ensure_ascii=False, indent=2),
        "```",
        "",
        "Die `source_hash` muss exakt uebernommen werden; sie steuert, ob ein",
        "erneuter Export die Texte als aktuell ansieht.",
        "",
        "## System",
        "",
        system,
        "",
        "## Auftrag",
        "",
        user,
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8", newline="")
    return path


def generate_with_openrouter(
    book: dict[str, Any],
    repo_root: Path,
    style: str,
    brief: dict[str, Any],
    system: str,
    user: str,
    *,
    client: Any | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """Erzeugt Texte ueber den bestehenden OpenRouter-Client.

    Modell und Reasoning-Stufe kommen aus ``book.yaml: ai.*``; es wird kein
    neuer Anbieter und kein zusaetzlicher Schluessel benoetigt.
    """
    from lib.openrouter_client import OpenRouterClient

    ai = book.get("ai") or {}
    model = str(ai.get("model") or "")
    reasoning = str(ai.get("reasoning_effort") or "") or None
    max_tokens = min(int(ai.get("max_tokens_per_scene") or 4000), 8000)
    temperature = 0.5

    if client is None:
        client = OpenRouterClient.from_env(model_override=model or None)
        if reasoning:
            client.reasoning_effort = reasoning
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    archive_sent_prompt(
        book_output_root(repo_root, book),
        chapter_id="marketing",
        style=style,
        provider="openrouter",
        model=str(getattr(client, "model", "") or model),
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    raw = client.chat(
        system=system,
        user=user,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    payload, problems = validate_payload(extract_json(raw), brief)
    generated = _payload(
        book,
        brief,
        style,
        generator="openrouter",
        model=str(getattr(client, "last_response_model", "") or model),
        texts=payload.get("texts") or {},
        youtube=payload.get("youtube") or {},
        usage=dict(getattr(client, "last_usage", {}) or {}),
    )
    return generated, problems


def workspace_payload(
    book: dict[str, Any],
    brief: dict[str, Any],
    style: str,
) -> dict[str, Any]:
    """Leerer Textrahmen fuer den Provider ``workspace_ai``.

    Die Texte selbst kommen aus der Arbeit einer KI im Repository.
    """
    return _payload(
        book,
        brief,
        style,
        generator="workspace_ai",
        model="Repository-KI (Editor)",
        notes=["Texte als Repository-KI erstellt; Quellhash stammt aus dem Datenbrief."],
    )

