"""
marketing_campaign.py
=====================

Kampagnendaten, Validierung und Rendering fuer den Marketingexport.

Der Export liest ausschliesslich vorhandene Buchdaten:

* ``books/<id>/book.yaml``   -- ID, Titel, Autor, Styles, KI-Defaults
* ``books/<id>/export.yaml`` -- Metadaten, Titelei, Cover, Bilder,
  top-level ``website:`` (Amazon-Link) und optional ``marketing:``
* ``books/<id>/names.yaml``  -- Glossar (optional, nur fuer Prompts)
* ``books/<id>/work/scenes/de/<style>/`` -- fertige DE-Szenen
* ``books/<id>/assets/``    -- Cover, Kapitel- und Szenenbilder

Erzeugt wird ein strukturiertes Paket unter
``books/<id>/exports/marketing/``. Es wird nichts veroeffentlicht und keine
Plattform-API angesprochen.

Wiederholbarkeit: Beitrags-IDs sind aus Buch-ID und Beitragsfunktion
abgeleitet; ``generated_at`` allein erzwingt keine neue Textversion.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, tzinfo
from pathlib import Path
from typing import Any, Iterable

import yaml

_TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import export_manuscript as manuscript  # noqa: E402
from lib.output_paths import (  # noqa: E402
    book_exports_root,
    book_output_root,
    find_scene_translations,
)


SCHEMA_VERSION = 1
PROMPT_VERSION = "marketing-1"
GLOBAL_CONFIG_PATH = "config/marketing.yaml"
DEFAULT_TIMEZONE = "Europe/Berlin"
MARKETING_SCOPE = "marketing"

# Statuskonvention: Textlage und Veroeffentlichungsreife bleiben getrennt.
STATUS_GENERATED = "generated"
STATUS_READY = "ready"
STATUS_NEEDS_REVIEW = "needs_review"
STATUS_NEEDS_AMAZON = "needs_amazon_url"
STATUS_NEEDS_YOUTUBE = "needs_youtube_url"
STATUS_BLOCKED = "blocked"
STATUS_OMITTED = "omitted"

URL_PATTERN = re.compile(r"https?://[^\s<>\"')]+")
AMAZON_HOST_PATTERN = re.compile(r"(^|\.)amazon\.[a-z.]+$", re.IGNORECASE)
SENTENCE_END = ".!?"

DEFAULT_GLOBAL_CONFIG: dict[str, Any] = {
    "brand": {
        "label": "Motivatier Classics",
        "publisher": "Motivatier Hermann Stiftung",
        "shelf_url": "https://stiftung.motivatier.de/classics/index.html",
        "shelf_intro": "Weitere Buecher von Motivatier Classics",
    },
    "schedule": {"timezone": DEFAULT_TIMEZONE, "offsets": {}},
    "limits": {
        "x_weighted_chars": 280,
        "x_target_min": 220,
        "x_target_max": 250,
        "url_weight": 23,
        "youtube_title_chars": 100,
        "youtube_description_chars": 5000,
        "youtube_short_title_chars": 100,
        "youtube_short_description_chars": 5000,
    },
    "sample": {"max_chars": 320, "min_chars": 120},
    "media": {"min_word_length": 6, "keywords_per_post": 12},
}


# ---------------------------------------------------------------------------
# Beitragsfunktionen
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PostSpec:
    """Eine Beitragsfunktion der Kampagne.

    ``needs`` nennt die harten Voraussetzungen (``amazon``, ``song``,
    ``youtube``). Fehlt eine davon, wird der Beitrag dokumentiert, aber nicht
    als veroeffentlichungsbereit ausgewiesen.
    """

    id: str
    platform: str
    kind: str
    label: str
    needs: tuple[str, ...] = ()
    offset_days: int = 0
    x_post: bool = False


POST_SPECS: tuple[PostSpec, ...] = (
    PostSpec("x-t0-intro", "x", "book_intro", "Buchvorstellung", ("amazon",), 0, True),
    PostSpec("x-t1-song", "x", "song_clip", "Song- oder Clipausschnitt", ("amazon", "song"), 1, True),
    PostSpec("x-t2-youtube", "x", "youtube_announce", "Vollstaendiger Song auf YouTube", ("song", "youtube"), 2, True),
    PostSpec("yt-main", "youtube", "song_video", "Vollstaendiges Liedvideo", ("amazon", "song", "youtube"), 2),
    PostSpec("yt-short-1", "youtube", "short_song", "Short: musikalischer Einstieg", ("song",), 3),
    PostSpec("x-t5-content", "x", "content", "Inhaltlicher Beitrag", ("amazon",), 5, True),
    PostSpec("x-t8-sample", "x", "sample", "Leseprobe oder Besonderheit der Ausgabe", ("amazon",), 8, True),
    PostSpec("yt-short-2", "youtube", "short_content", "Short: inhaltlicher Einstieg", (), 10),
    PostSpec("x-t12-second-angle", "x", "second_angle", "Zweiter thematischer Zugang", ("amazon",), 12, True),
)

POST_SPEC_BY_ID: dict[str, PostSpec] = {spec.id: spec for spec in POST_SPECS}


# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or {}


def merge_defaults(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_defaults(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_global_config(repo_root: Path) -> dict[str, Any]:
    """Globale Marketingdefaults aus ``config/marketing.yaml``."""
    raw = load_yaml(repo_root / GLOBAL_CONFIG_PATH)
    return merge_defaults(DEFAULT_GLOBAL_CONFIG, raw)


def marketing_block(export_data: dict[str, Any]) -> dict[str, Any]:
    """Buchlokaler ``marketing:``-Block (top-level, analog zu ``website:``)."""
    return export_data.get("marketing") or {}


def marketing_enabled(export_data: dict[str, Any]) -> bool:
    block = marketing_block(export_data)
    if not block:
        return False
    return bool(block.get("enabled", True))


def schedule_offsets(global_cfg: dict[str, Any]) -> dict[str, int]:
    offsets = dict(global_cfg.get("schedule", {}).get("offsets") or {})
    result: dict[str, int] = {}
    for spec in POST_SPECS:
        value = offsets.get(spec.id)
        result[spec.id] = int(value) if value is not None else spec.offset_days
    return result


def limits_config(global_cfg: dict[str, Any]) -> dict[str, Any]:
    return merge_defaults(DEFAULT_GLOBAL_CONFIG["limits"], global_cfg.get("limits") or {})


def brand_config(global_cfg: dict[str, Any]) -> dict[str, Any]:
    return merge_defaults(DEFAULT_GLOBAL_CONFIG["brand"], global_cfg.get("brand") or {})


# ---------------------------------------------------------------------------
# Zeichengewichtung (konservative Naeherung)
# ---------------------------------------------------------------------------


def weighted_length(text: str, url_weight: int = 23) -> int:
    """Konservative Naeherung der X-Zeichenzaehlung.

    * URLs zaehlen als ``url_weight`` Zeichen (Standard 23, t.co-Umleitung).
    * Breite Zeichen (CJK, Vollbreite) und Emoji zaehlen als 2.
    * Kombinierende Zeichen zaehlen als 1 (bewusst *nicht* 0, damit die
      Naeherung nicht untertreibt).

    Das ist eine Naeherung, keine Plattformvalidierung.
    """
    urls = URL_PATTERN.findall(text)
    remaining = URL_PATTERN.sub("", text)
    total = len(urls) * url_weight
    for char in remaining:
        total += 2 if _is_wide_char(char) else 1
    return total


def _is_wide_char(char: str) -> bool:
    codepoint = ord(char)
    if 0x1F000 <= codepoint <= 0x1FAFF:  # Emoji / Symbole
        return True
    if 0x1100 <= codepoint <= 0x115F:  # Hangul Jamo
        return True
    if 0x2E80 <= codepoint <= 0xA4CF:  # CJK-Radikale bis Yi
        return True
    if 0xAC00 <= codepoint <= 0xD7A3:  # Hangul-Silben
        return True
    if 0xF900 <= codepoint <= 0xFAFF:  # CJK-Kompatibilitaet
        return True
    if 0xFF00 <= codepoint <= 0xFF60:  # Vollbreite Formen
        return True
    return unicodedata.east_asian_width(char) in {"W", "F"}


def truncate_at_sentence(text: str, max_chars: int) -> str:
    """Kuerzt an einer Satzgrenze, niemals mitten im Satz."""
    collapsed = re.sub(r"\s+", " ", text).strip()
    if len(collapsed) <= max_chars:
        return collapsed
    window = collapsed[: max_chars + 1]
    cut = -1
    for match in re.finditer(rf"[{re.escape(SENTENCE_END)}](?=\s|$)", window):
        cut = match.end()
    if cut < 0:
        cut = window.rfind(" ")
        if cut <= 0:
            return ""
    return collapsed[:cut].strip()


# ---------------------------------------------------------------------------
# Zeitzone Europe/Berlin
# ---------------------------------------------------------------------------


class BerlinFallbackTZ(tzinfo):
    """Fallback ohne ``tzdata``: EU-Sommerzeitregel.

    Innerhalb der Umstellungstunde (letzter Sonntag im Maerz/Oktober) ist die
    Einordnung um bis zu einer Stunde unsicher. Der Fallback greift nur, wenn
    ``zoneinfo`` keine Zeitzonendaten findet.
    """

    def utcoffset(self, dt: datetime | None) -> timedelta:
        return timedelta(hours=2) if self._dst_active(dt) else timedelta(hours=1)

    def dst(self, dt: datetime | None) -> timedelta:
        return timedelta(hours=1) if self._dst_active(dt) else timedelta(0)

    def tzname(self, dt: datetime | None) -> str:
        return "CEST" if self._dst_active(dt) else "CET"

    @staticmethod
    def _dst_active(dt: datetime | None) -> bool:
        if dt is None:
            return False
        naive = dt.replace(tzinfo=None)
        start = datetime(naive.year, 3, _last_sunday(naive.year, 3), 2)
        end = datetime(naive.year, 10, _last_sunday(naive.year, 10), 3)
        return start <= naive < end


def _last_sunday(year: int, month: int) -> int:
    if month == 12:
        last = datetime(year, 12, 31)
    else:
        last = datetime(year, month + 1, 1) - timedelta(days=1)
    return last.day - ((last.weekday() + 1) % 7)


def berlin_tzinfo() -> tzinfo:
    """Europe/Berlin ueber zoneinfo, sonst deterministischer Fallback."""
    try:
        from zoneinfo import ZoneInfo

        return ZoneInfo(DEFAULT_TIMEZONE)
    except Exception:  # pragma: no cover - nur ohne tzdata/Systemdaten
        return BerlinFallbackTZ()


def parse_campaign_start(value: Any, tz: tzinfo) -> datetime | None:
    """Liest ``marketing.campaign_start``.

    Mit Offset wird der Zeitpunkt uebernommen, ohne Offset als Berliner
    Ortszeit interpretiert. Ein fehlendes Datum ist ein gueltiger Zustand.
    """
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(
            f"campaign_start ist kein ISO-8601-Datum: {text!r} ({exc})"
        ) from exc
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=tz)
    return parsed.astimezone(tz)


def scheduled_at(
    campaign_start: datetime | None,
    offset_days: int,
    tz: tzinfo,
) -> str | None:
    if campaign_start is None:
        return None
    moment = campaign_start + timedelta(days=offset_days)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=tz)
    return moment.astimezone(tz).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Links
# ---------------------------------------------------------------------------


def amazon_link(export_data: dict[str, Any]) -> dict[str, Any]:
    """Amazon-Adresse der konkreten Ausgabe.

    Quelle ist zuerst ``marketing.amazon_url``, sonst die bereits vorhandene
    Regal-Adresse ``website.amazon_url``. Ein syntaktisch gueltiger Link wird
    als Benutzerangabe uebernommen (``user_provided``); das ist ausdruecklich
    keine Bestaetigung durch Amazon.
    """
    website = export_data.get("website") or {}
    marketing = marketing_block(export_data)
    override = str(marketing.get("amazon_url") or "").strip()
    raw = override or str(website.get("amazon_url") or "").strip()
    source = "marketing.amazon_url" if override else "website.amazon_url"
    if not raw:
        return {
            "url": "",
            "source": source,
            "url_status": "missing",
            "syntax": "not_checked",
            "assignment": "missing",
        }
    syntax = "ok" if _is_syntactic_url(raw) else "invalid"
    host = _url_host(raw)
    return {
        "url": raw,
        "source": source,
        "url_status": "present",
        "syntax": syntax,
        "host": host,
        "is_amazon_host": bool(host and AMAZON_HOST_PATTERN.search(host)),
        "assignment": "user_provided" if syntax == "ok" else "unverified",
        "note": (
            "Aus dem Buchdatensatz uebernommen; keine Pruefung gegen die "
            "konkrete Amazon-Ausgabe."
        ),
    }


def _is_syntactic_url(value: str) -> bool:
    return bool(re.match(r"^https?://[^\s]+$", value))


def _url_host(value: str) -> str:
    match = re.match(r"^https?://([^/?#]+)", value)
    return (match.group(1) or "").lower() if match else ""


def youtube_link(marketing: dict[str, Any]) -> dict[str, Any]:
    """Video-Adresse bzw. Video-ID des spaeteren YouTube-Uploads."""
    block = marketing.get("youtube") or {}
    url = str(block.get("url") or "").strip()
    video_id = str(block.get("video_id") or "").strip()
    derived = False
    if not url and video_id:
        url = f"https://www.youtube.com/watch?v={video_id}"
        derived = True
    if url and not video_id:
        match = re.search(r"[?&]v=([A-Za-z0-9_-]{6,})", url)
        if match:
            video_id = match.group(1)
    return {
        "url": url,
        "video_id": video_id,
        "url_status": "present" if url else "missing",
        "public": bool(block.get("public", False)),
        "derived_from_video_id": derived,
        "syntax": "ok" if not url or _is_syntactic_url(url) else "invalid",
    }


# ---------------------------------------------------------------------------
# Songs
# ---------------------------------------------------------------------------


def song_entries(marketing: dict[str, Any], book_root: Path) -> list[dict[str, Any]]:
    """Songdaten aus ``marketing.songs`` samt Dateipruefung."""
    entries: list[dict[str, Any]] = []
    for index, raw in enumerate(marketing.get("songs") or [], start=1):
        if not isinstance(raw, dict):
            continue
        file_rel = str(raw.get("file") or "").strip()
        lyrics_rel = str(raw.get("lyrics_file") or "").strip()
        file_path = _resolve_repo_path(file_rel, book_root)
        lyrics_path = _resolve_repo_path(lyrics_rel, book_root)
        entries.append(
            {
                "id": str(raw.get("id") or f"song-{index:02d}").strip(),
                "title": str(raw.get("title") or "").strip(),
                "file": file_rel,
                "file_exists": bool(file_path and file_path.is_file()),
                "lyrics_file": lyrics_rel,
                "lyrics_exists": bool(lyrics_path and lyrics_path.is_file()),
                "clip_start_seconds": raw.get("clip_start_seconds"),
                "clip_duration_seconds": raw.get("clip_duration_seconds"),
                "full_video": str(raw.get("full_video") or "").strip(),
                "short_clips": list(raw.get("short_clips") or []),
                "credits": list(raw.get("credits") or []),
                "ai_generated": _normalize_flag(raw.get("ai_generated")),
            }
        )
    return entries


def _resolve_repo_path(value: str, book_root: Path) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else book_root / path


def _normalize_flag(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return "unknown"


def has_usable_song(songs: list[dict[str, Any]]) -> bool:
    return any(song["file"] and song["file_exists"] for song in songs)


# ---------------------------------------------------------------------------
# Pfade und Textquellen
# ---------------------------------------------------------------------------


def book_root(book: dict[str, Any], repo_root: Path) -> Path:
    return repo_root / str(book.get("book_root") or f"books/{book.get('id')}")


def marketing_work_dir(book: dict[str, Any], repo_root: Path) -> Path:
    return book_output_root(repo_root, book) / MARKETING_SCOPE


def marketing_export_dir(book: dict[str, Any], repo_root: Path) -> Path:
    return book_exports_root(repo_root, book) / MARKETING_SCOPE


def rel_path(repo_root: Path, path: Path) -> str:
    """Repo-relativer POSIX-Pfad (keine absoluten Entwicklerpfade)."""
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def stable_id(book_id: str, post_id: str) -> str:
    """Stabile Beitrags-ID aus Buch-ID und Beitragsfunktion."""
    return f"{book_id}:{post_id}"


def source_hash(brief: dict[str, Any]) -> str:
    payload = json.dumps(brief, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def load_generated(book_root_dir: Path) -> dict[str, Any]:
    path = book_root_dir / "work" / MARKETING_SCOPE / "generated.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8")) or {}
    except json.JSONDecodeError as exc:
        raise ValueError(f"generated.json ist kein gueltiges JSON: {exc}") from exc


def generated_path(book_root_dir: Path) -> Path:
    return book_root_dir / "work" / MARKETING_SCOPE / "generated.json"


def overrides_dir(book_root_dir: Path) -> Path:
    return book_root_dir / "work" / MARKETING_SCOPE / "overrides"


def needs_regeneration(
    brief_hash: str,
    generated: dict[str, Any],
    *,
    force: bool,
) -> tuple[bool, str]:
    """Entscheidet, ob Texte neu erzeugt werden muessen.

    ``generated_at`` loest ausdruecklich keine Neuversion aus.
    """
    if force:
        return True, "regenerate_forced"
    if not generated:
        return True, "no_generated_texts"
    if str(generated.get("source_hash") or "") != brief_hash:
        return True, "source_changed"
    if str(generated.get("prompt_version") or "") != PROMPT_VERSION:
        return True, "prompt_version_changed"
    if not (generated.get("texts") or {}):
        return True, "generated_texts_empty"
    return False, "reused"


def load_overrides(book_root_dir: Path) -> dict[str, dict[str, Any]]:
    """Manuell gepflegte Texte; sie haben Vorrang vor generierten Texten."""
    root = overrides_dir(book_root_dir)
    overrides: dict[str, dict[str, Any]] = {}
    if not root.is_dir():
        return overrides
    for path in sorted(root.glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        overrides[path.stem] = {"text": text, "source": "override", "path": path}
    return overrides


def collect_texts(book_root_dir: Path) -> dict[str, dict[str, Any]]:
    """Fasst generierte Texte und manuelle Overrides zusammen.

    Overrides gewinnen. Der Ursprung wird pro Beitrag mitgefuehrt, damit im
    Manifest erkennbar bleibt, was maschinell und was redaktionell ist.
    """
    generated = load_generated(book_root_dir)
    texts: dict[str, dict[str, Any]] = {}
    for post_id, entry in (generated.get("texts") or {}).items():
        if not isinstance(entry, dict):
            continue
        texts[post_id] = {**entry, "source": entry.get("source") or "generated"}
    for post_id, entry in load_overrides(book_root_dir).items():
        texts[post_id] = entry
    youtube = generated.get("youtube") or {}
    if youtube:
        texts["yt-main"] = {**youtube, "source": youtube.get("source") or "generated"}
        for short_id, short in (youtube.get("shorts") or {}).items():
            if isinstance(short, dict):
                texts[short_id] = {**short, "source": short.get("source") or "generated"}
    return texts


# ---------------------------------------------------------------------------
# Leseprobe (echte Passage aus der fertigen Ausgabe)
# ---------------------------------------------------------------------------


def export_meta(book: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    """Exportmetadaten eines Buchpakets, aufgeloest gegen ``repo_root``.

    Gleiche Zusammenfuehrung wie ``export_manuscript.load_export_config``, aber
    ohne den globalen Repo-Root des Exportmoduls -- dadurch sind Buchpakete in
    Tests und in anderen Arbeitsverzeichnissen sauber aufloesbar.
    """
    export_data = load_export_data(book, repo_root)
    defaults = export_data.get("defaults", {}) or {}
    book_cfg = export_data.get("book", {}) or {}
    meta: dict[str, Any] = {**defaults, **book_cfg}
    for key in ("cover", "front_matter", "output", "illustrations"):
        merged = {
            **(defaults.get(key) or {}),
            **(book_cfg.get(key) or {}),
        }
        if merged:
            meta[key] = merged
    meta.setdefault("title", book.get("title", ""))
    meta.setdefault("author", book.get("author", ""))
    meta.setdefault("language", "de-DE")
    meta["_base_dir"] = str(book_root(book, repo_root))
    return meta


def chapter_ids_with_de_scenes(
    book: dict[str, Any], style: str, repo_root: Path
) -> list[str]:
    root = book_output_root(repo_root, book)
    style_root = root / "scenes" / "de" / style
    if not style_root.is_dir():
        return []
    return sorted(
        path.name
        for path in style_root.iterdir()
        if path.is_dir() and any(path.glob("scene-*.md"))
    )


def chapter_text(
    book: dict[str, Any], style: str, chapter_id: str, repo_root: Path
) -> str:
    root = book_output_root(repo_root, book)
    scenes = find_scene_translations(root, chapter_id, style)
    parts = [
        manuscript.clean_scene_markdown(path.read_text(encoding="utf-8"))
        for _, path in sorted(scenes.items())
    ]
    return "\n\n".join(part for part in parts if part)


def select_sample(
    book: dict[str, Any],
    style: str,
    repo_root: Path,
    sample_cfg: dict[str, Any],
) -> dict[str, Any] | None:
    """Erste echte Passage, die lang genug fuer einen Leseproben-Beitrag ist.

    Die Passage stammt ausschliesslich aus ``work/scenes/de/<style>/`` und wird
    an einer Satzgrenze gekuerzt. Editoriale Vorabsaetze (Blockzitate wie die
    Vorspaenne in Peter I) sind keine Autorenstellen und werden uebersprungen.
    """
    max_chars = int(sample_cfg.get("max_chars", 320))
    min_chars = int(sample_cfg.get("min_chars", 120))
    root = book_output_root(repo_root, book)
    for chapter_id in chapter_ids_with_de_scenes(book, style, repo_root):
        scenes = find_scene_translations(root, chapter_id, style)
        for number, path in sorted(scenes.items()):
            raw = manuscript.clean_scene_markdown(path.read_text(encoding="utf-8"))
            body = strip_editorial_lead(raw)
            text = truncate_at_sentence(body, max_chars)
            if len(text) >= min_chars:
                return {
                    "chapter": chapter_id,
                    "scene": number,
                    "source": rel_path(repo_root, path),
                    "text": text,
                    "editorial_lead_skipped": body != raw.strip(),
                }
    return None


def strip_editorial_lead(text: str) -> str:
    """Entfernt editoriale Vorabsaetze am Textanfang.

    Blockzitate (``>``) und Ueberschriften (``#``) am Szenenanfang sind in
    dieser Werkbank redaktionelle Zusaetze (z. B. die Vorspaenne in Peter I)
    und keine Autorenstellen. Fuer Zitate werden sie uebersprungen.
    """
    lines = text.replace("\r\n", "\n").split("\n")
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped or stripped.startswith(">") or stripped.startswith("#"):
            index += 1
            continue
        break
    return "\n".join(lines[index:]).strip()


# ---------------------------------------------------------------------------
# Themenzuordnung fuer Bilder
# ---------------------------------------------------------------------------

STOPWORDS_DE = {
    "dieser", "diese", "dieses", "diesem", "diesen", "darauf", "daran", "davon",
    "bereits", "wieder", "nicht", "nichts", "immer", "etwas", "jemand", "niemand",
    "wurden", "werden", "worden", "hatte", "hatten", "konnte", "konnten", "musste",
    "wollte", "sollte", "würde", "würden", "seiner", "seine", "seinen", "seinem",
    "ihrer", "ihre", "ihren", "ihrem", "einer", "eines", "einem", "einen", "gegen",
    "zwischen", "während", "obwohl", "deshalb", "deswegen", "trotzdem", "danach",
    "vorher", "später", "plötzlich", "vielleicht", "wirklich", "sondern", "sowie",
    "einfach", "endlich", "bereits", "gerade", "kaum", "doch", "aber", "auch",
}


def keywords(text: str, min_word_length: int, limit: int) -> list[str]:
    from collections import Counter

    words = re.findall(rf"[A-Za-zÄÖÜäöüß]{{{int(min_word_length)},}}", text.lower())
    counts = Counter(word for word in words if word not in STOPWORDS_DE)
    return [word for word, _ in counts.most_common(int(limit))]


def match_chapter(
    post_text: str,
    chapter_pool: list[tuple[str, set[str]]],
    used: set[str],
    media_cfg: dict[str, Any],
) -> str | None:
    """Waehlt das thematisch passendste, noch nicht verwendete Kapitel.

    Die Zuordnung vergleicht Inhaltswoerter des Beitrags mit den Inhaltswoertern
    des jeweiligen Kapitels. Das ist deterministisch und bevorzugt nicht
    automatisch das erste Bild des Buches.
    """
    min_len = int(media_cfg.get("min_word_length", 6))
    limit = int(media_cfg.get("keywords_per_post", 12))
    post_words = keywords(post_text, min_len, limit)
    if not post_words:
        return None
    post_set = set(post_words)
    best: tuple[int, str] | None = None
    for chapter_id, chapter_words in chapter_pool:
        if chapter_id in used:
            continue
        score = len(post_set & chapter_words)
        if score <= 0:
            continue
        if best is None or score > best[0]:
            best = (score, chapter_id)
    return best[1] if best else None


# ---------------------------------------------------------------------------
# Medien
# ---------------------------------------------------------------------------


def resolve_cover(meta: dict[str, Any], repo_root: Path) -> dict[str, Any] | None:
    """Cover aus ``export.yaml`` (explizite ``image_path`` oder Auto-Erkennung).

    ``prepare_cover`` erzeugt bei fehlendem Bild ein Platzhalter-Cover. Fuer
    Marketingmaterial wird nur ein echtes Cover zugeordnet -- ein Platzhalter
    waere als Medium irrefuehrend.
    """
    cover_cfg = meta.get("cover", {}) or {}
    mode = str(cover_cfg.get("mode") or "placeholder").strip().lower()
    image_path = str(cover_cfg.get("image_path") or "").strip()
    if mode == "image" or image_path:
        base_dir = Path(str(meta.get("_base_dir") or repo_root))
        path = Path(image_path)
        if not path.is_absolute():
            path = base_dir / path
        if path.is_file():
            return {"kind": "cover", "path": rel_path(repo_root, path)}
        return None
    found = manuscript.find_named_image(
        Path(str(meta.get("_base_dir") or repo_root)) / "assets" / "covers", "cover"
    )
    if found:
        return {"kind": "cover", "path": rel_path(repo_root, found)}
    return None


def chapter_image_map(
    meta: dict[str, Any], repo_root: Path
) -> dict[str, str]:
    """Kapitel-ID -> repo-relativer Pfad des Kapitelbildes."""
    result: dict[str, str] = {}
    base = Path(str(meta.get("_base_dir") or repo_root)) / "assets" / "chapter"
    if not base.is_dir():
        return result
    for path in sorted(base.glob("chapter-*")):
        if not path.is_file() or path.stem.endswith("_alt"):
            continue
        if path.suffix.lower() not in manuscript.IMAGE_EXTENSIONS:
            continue
        match = re.match(r"chapter-(\d{3})$", path.stem)
        if not match:
            continue
        chapter_id = match.group(1)
        current = result.get(chapter_id)
        if current is None or _image_rank(path) < _image_rank(Path(current)):
            result[chapter_id] = rel_path(repo_root, path)
    return result


def _image_rank(path: Path) -> tuple[int, str]:
    order = {".jpg": 0, ".jpeg": 1, ".png": 2, ".webp": 3}
    return (order.get(path.suffix.lower(), 9), path.name)


class MediaAllocator:
    """Deterministische, thematisch begruendete Bildzuordnung."""

    def __init__(
        self,
        repo_root: Path,
        chapter_images: dict[str, str],
        cover: dict[str, Any] | None,
        overrides: dict[str, str],
        meta: dict[str, Any],
    ) -> None:
        self.repo_root = repo_root
        self.chapter_images = chapter_images
        self.cover = cover
        self.overrides = overrides or {}
        self.meta = meta
        self.used: set[str] = set()
        self.usage: dict[str, int] = {}

    def explicit(self, post_id: str) -> dict[str, Any] | None:
        value = str(self.overrides.get(post_id) or "").strip()
        if not value:
            return None
        path = Path(value)
        resolved = path if path.is_absolute() else self.repo_root / path
        if not resolved.is_file():
            return {
                "kind": "image",
                "path": value,
                "exists": False,
                "note": "marketing.media verweist auf eine fehlende Datei",
            }
        self.used.add(value)
        return {"kind": "image", "path": rel_path(self.repo_root, resolved), "exists": True}

    def chapter(self, chapter_id: str) -> dict[str, Any] | None:
        path = self.chapter_images.get(chapter_id)
        if not path:
            return None
        reused = path in self.used
        self.used.add(path)
        self.usage[path] = self.usage.get(path, 0) + 1
        return {
            "kind": "chapter_image",
            "chapter": chapter_id,
            "path": path,
            "exists": True,
            "reused": reused,
        }

    def _unused(self) -> list[str]:
        return [
            chapter_id
            for chapter_id in sorted(self.chapter_images)
            if self.chapter_images[chapter_id] not in self.used
        ]

    def _least_used(self) -> str | None:
        """Bei knappem Bildmaterial: gleichmaessig wiederverwenden statt Luecke."""
        if not self.chapter_images:
            return None
        return min(
            sorted(self.chapter_images),
            key=lambda chapter_id: (
                self.usage.get(self.chapter_images[chapter_id], 0),
                chapter_id,
            ),
        )

    def nearest_chapter(self, chapter_id: str | None) -> dict[str, Any] | None:
        if chapter_id and chapter_id in self.chapter_images:
            return self.chapter(chapter_id)
        unused = self._unused()
        if unused:
            return self.chapter(unused[0])
        fallback = self._least_used()
        return self.chapter(fallback) if fallback else None

    def by_position(self, fraction: float) -> dict[str, Any] | None:
        """Gleichmaessig verteiltes Kapitelbild, bevorzugt noch unbenutzte."""
        ids = self._unused()
        if not ids:
            fallback = self._least_used()
            return self.chapter(fallback) if fallback else None
        index = min(len(ids) - 1, max(0, int(round(fraction * (len(ids) - 1)))))
        return self.chapter(ids[index])


    def scene(
        self, chapter_id: str | None, scene_number: int | None
    ) -> dict[str, Any] | None:
        if not chapter_id or scene_number is None:
            return None
        illustration = manuscript.scene_illustration(
            self.meta, chapter_id, scene_number
        )
        if illustration is None:
            return None
        path = rel_path(self.repo_root, illustration.path)
        self.used.add(path)
        return {
            "kind": "scene_image",
            "chapter": chapter_id,
            "scene": scene_number,
            "path": path,
            "exists": True,
        }

    def cover_ref(self) -> dict[str, Any] | None:
        if not self.cover:
            return None
        self.used.add(self.cover["path"])
        return {**self.cover, "exists": True}


# ---------------------------------------------------------------------------
# Kampagne bauen
# ---------------------------------------------------------------------------

DISCLAIMER_SONG = (
    "Begleitsong zum Roman: eigenstaendige Musik zum Buch, kein Hoerbuch und "
    "kein Originaltext des Autors."
)
AMAZON_MISSING_HINT = (
    "<Amazon-Link fehlt - in books/<id>/export.yaml unter website.amazon_url "
    "eintragen>"
)


class CampaignBuilder:
    """Baut Beitragsobjekte, Validierung und Manifest aus vorhandenen Daten."""

    def __init__(
        self,
        repo_root: Path,
        book: dict[str, Any],
        style: str,
        global_cfg: dict[str, Any],
        export_data: dict[str, Any],
        texts: dict[str, dict[str, Any]],
        generated: dict[str, Any] | None = None,
    ) -> None:
        self.repo_root = repo_root
        self.book = book
        self.book_id = str(book.get("id"))
        self.style = style
        self.global_cfg = global_cfg
        self.export_data = export_data
        self.texts = texts
        self.generated = generated or {}
        self.book_root_dir = book_root(book, repo_root)
        self.meta = export_meta(book, repo_root)
        self.limits = limits_config(global_cfg)
        self.brand = brand_config(global_cfg)
        self.offsets = schedule_offsets(global_cfg)
        self.tz = berlin_tzinfo()
        self.marketing = marketing_block(export_data)
        self.amazon = amazon_link(export_data)
        self.youtube = youtube_link(self.marketing)
        self.songs = song_entries(self.marketing, self.book_root_dir)
        self.lead_song = next(
            (song for song in self.songs if song["file"] and song["file_exists"]),
            None,
        )
        self.campaign_start = parse_campaign_start(
            self.marketing.get("campaign_start"), self.tz
        )
        self.sample = select_sample(
            book, style, repo_root, self.global_cfg.get("sample") or {}
        )
        self.media_cfg = merge_defaults(
            DEFAULT_GLOBAL_CONFIG["media"], global_cfg.get("media") or {}
        )
        self.media_overrides = {
            str(key): str(value)
            for key, value in (self.marketing.get("media") or {}).items()
            if isinstance(value, (str, int))
        }
        self.chapter_images = chapter_image_map(self.meta, self.repo_root)
        self.cover = resolve_cover(self.meta, self.repo_root)
        self.allocator = MediaAllocator(
            self.repo_root,
            self.chapter_images,
            self.cover,
            self.media_overrides,
            self.meta,
        )
        self.chapter_pool = self._chapter_pool()

    # -- Hilfen ------------------------------------------------------------

    def _chapter_pool(self) -> list[tuple[str, set[str]]]:
        min_len = int(self.media_cfg.get("min_word_length", 6))
        limit = int(self.media_cfg.get("keywords_per_post", 12))
        pool: list[tuple[str, set[str]]] = []
        for chapter_id in sorted(self.chapter_images):
            text = chapter_text(self.book, self.style, chapter_id, self.repo_root)
            pool.append((chapter_id, set(keywords(text, min_len, limit * 4))))
        return pool

    def _entry(self, post_id: str) -> dict[str, Any]:
        entry = self.texts.get(post_id) or {}
        return entry if isinstance(entry, dict) else {}

    def _body(self, post_id: str) -> str:
        return str(self._entry(post_id).get("text") or "").strip()

    def _compose_x(self, body: str, url: str) -> str:
        parts = [body] if body else []
        if url:
            parts.append(url)
        return "\n\n".join(parts)

    def _media_for(self, spec: PostSpec, body: str) -> list[dict[str, Any]]:
        explicit = self.allocator.explicit(spec.id)
        if explicit is not None:
            return [explicit]
        if spec.id == "x-t0-intro":
            ref = self.allocator.cover_ref()
            return [ref] if ref else []
        if spec.id in {"x-t1-song", "yt-short-1", "yt-main"}:
            chapter_id = self.sample["chapter"] if self.sample else None
            scene_number = self.sample["scene"] if self.sample else None
            ref = self.allocator.scene(chapter_id, scene_number)
            if ref is None:
                ref = self.allocator.nearest_chapter(chapter_id)
            if ref is None:
                ref = self.allocator.cover_ref()
            return [ref] if ref else []
        if spec.id == "x-t2-youtube":
            ref = self.allocator.cover_ref()
            return [ref] if ref else []
        if spec.id == "x-t8-sample":
            chapter_id = self.sample["chapter"] if self.sample else None
            ref = self.allocator.nearest_chapter(chapter_id)
            return [ref] if ref else []
        used_chapters = {
            chapter_id
            for chapter_id, path in self.chapter_images.items()
            if path in self.allocator.used
        }
        matched = match_chapter(
            body, self.chapter_pool, used_chapters, self.media_cfg
        )
        ref = self.allocator.chapter(matched) if matched else None
        if ref is None:
            fractions = {
                "x-t5-content": 0.35,
                "x-t12-second-angle": 0.7,
                "yt-short-2": 0.55,
            }
            ref = self.allocator.by_position(fractions.get(spec.id, 0.5))
        return [ref] if ref else []

    # -- YouTube-Texte -----------------------------------------------------

    def _edition_note(self) -> str:
        parts: list[str] = []
        translator = str(self.meta.get("translator") or "").strip()
        label = str(self.meta.get("translator_label") or "").strip()
        if translator:
            parts.append(f"{label or 'Uebersetzung'}: {translator}.")
        publisher = str(self.meta.get("publisher") or "").strip()
        if publisher:
            parts.append(f"Herausgegeben von der {publisher}.")
        return " ".join(parts)

    def _credit_lines(self) -> list[str]:
        song = self.lead_song or (self.songs[0] if self.songs else None)
        if not song:
            return []
        return [f"- {str(item).strip()}" for item in song["credits"] if str(item).strip()]

    def _audio_ref(self, clip: bool) -> dict[str, Any] | None:
        if not self.lead_song:
            return None
        ref: dict[str, Any] = {
            "kind": "audio_clip" if clip else "audio_full",
            "path": self.lead_song["file"],
            "exists": True,
            "title": self.lead_song["title"],
            "ai_generated": self.lead_song["ai_generated"],
        }
        if clip:
            ref["clip_start_seconds"] = self.lead_song["clip_start_seconds"]
            ref["clip_duration_seconds"] = self.lead_song["clip_duration_seconds"]
            ref["clip_start_measured"] = False
        return ref

    def _youtube_description(self, entry: dict[str, Any]) -> str:
        prequel = str(entry.get("prequel") or "").strip()
        body = str(entry.get("body") or entry.get("text") or "").strip()
        if not prequel and not body:
            # Kein Inhalt: lieber nichts als ein Gerüst ohne Aussage.
            return ""
        amazon_line = self.amazon["url"] or AMAZON_MISSING_HINT
        lines = [
            f"Das Buch auf Amazon: {amazon_line}",
            f"{self.brand['shelf_intro']}: {self.brand['shelf_url']}",
        ]
        if prequel:
            lines += ["", prequel]
        if body:
            lines += ["", body]
        attribution = " - ".join(
            part
            for part in [
                str(self.meta.get("author") or "").strip(),
                str(self.meta.get("title") or "").strip(),
            ]
            if part
        )
        if attribution:
            lines += ["", attribution]
        edition = self._edition_note()
        if edition:
            lines += ["", edition]
        lines += ["", DISCLAIMER_SONG]
        credits = self._credit_lines()
        if credits:
            lines += ["", "Produktionsangaben:", *credits]
        return "\n".join(lines).strip()

    def _short_description(self, entry: dict[str, Any]) -> str:
        parts: list[str] = []
        description = str(entry.get("description") or "").strip()
        if description:
            parts.append(description)
        overlays = [
            str(item).strip()
            for item in (entry.get("overlays") or [])
            if str(item).strip()
        ]
        if overlays:
            parts.append("Texteinblendungen: " + " | ".join(overlays))
        if not parts:
            return ""
        attribution = " - ".join(
            part
            for part in [
                str(self.meta.get("author") or "").strip(),
                str(self.meta.get("title") or "").strip(),
            ]
            if part
        )
        if attribution:
            parts.append(attribution)
        return "\n\n".join(parts)

    def _shotlist(
        self,
        media: list[dict[str, Any]],
        overlays: list[str],
        book_ref: str,
    ) -> list[dict[str, Any]]:
        audio = self._audio_ref(clip=True)
        shots: list[dict[str, Any]] = []
        for index, ref in enumerate(media):
            missing: list[str] = []
            if not ref.get("exists", True):
                missing.append("image_source")
            if audio is None:
                missing.append("audio_source")
            elif audio.get("clip_start_seconds") is None:
                missing.append("clip_start_seconds")
            shots.append(
                {
                    "order": index + 1,
                    "image_source": ref.get("path"),
                    "image_exists": bool(ref.get("exists", True)),
                    "overlay": overlays[index] if index < len(overlays) else "",
                    "book_ref": book_ref,
                    "audio_source": audio["path"] if audio else None,
                    "audio_start_seconds": (
                        audio.get("clip_start_seconds") if audio else None
                    ),
                    "planned_duration_seconds": (
                        audio.get("clip_duration_seconds") if audio else None
                    ),
                    "duration_measured": False,
                    "missing": missing,
                }
            )
        return shots

    # -- Status und Validierung -------------------------------------------

    def _decide_status(
        self, spec: PostSpec, text: str, over_limit: bool
    ) -> tuple[str, list[str], list[str]]:
        reasons: list[str] = []
        depends: list[str] = []
        needs = set(spec.needs)
        if "amazon" in needs:
            depends.append("amazon_url")
            if self.amazon["url_status"] == "missing":
                reasons.append("amazon_url_missing")
            elif self.amazon["syntax"] != "ok":
                return STATUS_BLOCKED, reasons + ["amazon_url_invalid"], depends
        if "song" in needs:
            depends.append("song_file")
            if self.lead_song is None:
                if any(song["file"] for song in self.songs):
                    return STATUS_BLOCKED, reasons + ["song_file_missing"], depends
                return STATUS_OMITTED, reasons + ["no_song_data"], depends
        if "youtube" in needs:
            depends.append("youtube_url")
            if self.youtube["url_status"] == "missing":
                reasons.append("youtube_url_missing")
            elif self.youtube["syntax"] != "ok":
                return STATUS_BLOCKED, reasons + ["youtube_url_invalid"], depends
            elif not self.youtube["public"]:
                return STATUS_BLOCKED, reasons + ["youtube_video_not_public"], depends
        if not text:
            return STATUS_NEEDS_REVIEW, reasons + ["text_missing"], depends
        if over_limit:
            return STATUS_NEEDS_REVIEW, reasons + ["weighted_chars_over_limit"], depends
        if "amazon_url_missing" in reasons:
            return STATUS_NEEDS_AMAZON, reasons, depends
        if "youtube_url_missing" in reasons:
            return STATUS_NEEDS_YOUTUBE, reasons, depends
        source = str(self._entry(spec.id).get("source") or "generated")
        if source == "override":
            return STATUS_READY, reasons, depends
        return STATUS_GENERATED, reasons, depends

    def _book_ref(self, media: list[dict[str, Any]]) -> str:
        for ref in media:
            chapter = str(ref.get("chapter") or "").strip()
            if chapter:
                return f"Kapitel {chapter}"
        return str(self.meta.get("title") or "").strip()

    def _default_yt_title(self) -> str:
        song_title = str((self.lead_song or {}).get("title") or "").strip()
        return build_youtube_title(
            str(self.meta.get("title") or "").strip(),
            song_title,
            str(self.meta.get("author") or "").strip(),
            str(self.brand.get("label") or "Motivatier Classics"),
            int(self.limits.get("youtube_title_chars", 100)),
        )


def build_youtube_title(
    book_title: str,
    song_title: str,
    author: str,
    brand_label: str,
    limit: int = 100,
) -> str:
    """Titelmuster des Liedvideos, gekuerzt auf die maximale Titellaenge.

    Muster mit Songtitel: ``Buchtitel - Songtitel | Lied zum Roman von Autor``
    Muster ohne Songtitel: ``Buchtitel - Lied zum Roman von Autor | Marke``
    Nicht alle Bestandteile muessen enthalten sein; gekuerzt wird am trennenden
    Sonderzeichen, nie mitten im Wort, wenn ein Bestandteil weglassbar ist.
    """
    book = book_title.strip()
    song = song_title.strip()
    who = author.strip()
    brand = brand_label.strip()
    if song:
        variants = [
            " - ".join(part for part in [book, f"{song} | Lied zum Roman von {who}".strip()] if part),
            " - ".join(part for part in [book, song] if part),
            book,
        ]
    else:
        variants = [
            " - ".join(part for part in [book, f"Lied zum Roman von {who} | {brand}".strip()] if part),
            " - ".join(part for part in [book, f"Lied zum Roman von {who}".strip()] if part),
            book,
        ]
    for candidate in variants:
        text = re.sub(r"\s+", " ", candidate).strip(" -|")
        if len(text) <= limit:
            return text
    return re.sub(r"\s+", " ", variants[-1]).strip()[:limit].strip()


def _text_status(source: str, payload_text: str, over_limit: bool) -> str:
    if not payload_text:
        return "missing"
    if over_limit:
        return "over_limit"
    return "ready" if source == "override" else "generated"


class CampaignRunner(CampaignBuilder):
    """Baut die vollstaendige Kampagne inklusive Manifest."""

    def build(self) -> dict[str, Any]:
        posts = [self._build_post(spec) for spec in POST_SPECS]
        posts.sort(
            key=lambda item: (int(item["offset_days"]), item["platform"], item["id"])
        )
        return self._assemble(posts)

    def _build_post(self, spec: PostSpec) -> dict[str, Any]:
        entry = self._entry(spec.id)
        body_source = str(entry.get("text") or entry.get("body") or "").strip()
        media = self._media_for(spec, body_source)
        overlays = [
            str(item).strip()
            for item in (entry.get("overlays") or [])
            if str(item).strip()
        ]
        title: str | None = None
        text: str | None = None
        description: str | None = None
        shotlist: list[dict[str, Any]] = []
        related_video_ref: dict[str, Any] | None = None
        profile_ref: dict[str, Any] | None = None
        primary_kind = "youtube" if spec.id == "x-t2-youtube" else "amazon"

        if spec.platform == "x":
            body = self._body(spec.id)
            url = (
                self.youtube["url"] if primary_kind == "youtube" else self.amazon["url"]
            )
            # Ein Link allein ist kein Beitrag: ohne Text bleibt die Position offen.
            text = self._compose_x(body, url) if body else ""
            if spec.id == "x-t1-song":
                audio = self._audio_ref(clip=True)
                if audio:
                    media = media + [audio]
        elif spec.id == "yt-main":
            title = str(entry.get("title") or "").strip() or self._default_yt_title()
            description = self._youtube_description(entry)
            audio = self._audio_ref(clip=False)
            if audio:
                media = media + [audio]
            shotlist = self._shotlist(media, overlays, self._book_ref(media))
        else:
            title = str(entry.get("title") or "").strip() or None
            description = self._short_description(entry)
            audio = self._audio_ref(clip=True)
            if audio:
                media = media + [audio]
            shotlist = self._shotlist(media, overlays, self._book_ref(media))
            related_video_ref = {
                "target": "yt-main",
                "resolution": "marketing.youtube.url",
                "available": bool(self.youtube["url"]),
                "instruction": (
                    "In der YouTube-App das verknuepfte Video setzen; normale URLs in "
                    "Shorten-Beschreibungen sind nicht zuverlaessig anklickbar."
                ),
            }
            profile_ref = {
                "resolution": "Kanal-Profil",
                "available": False,
                "instruction": (
                    "Alternativ den Kanal-Profillink in der YouTube-App verknuepfen."
                ),
            }

        payload_text = text or description or ""
        if "song" in spec.needs and self.lead_song is None:
            # Ohne vorhandenen Song entsteht kein vermeintliches Liedvideo und
            # kein Clipbeitrag mit Musikbezug. Die Position bleibt mit Grund
            # dokumentiert (omitted), Medien/Shotlist zeigen den Materialstand.
            title = None
            description = None
            text = None
            overlays = []
            payload_text = ""
        limit_key = {
            "x": "x_weighted_chars",
            "youtube": "youtube_description_chars",
        }[spec.platform]
        char_limit = int(self.limits[limit_key])
        url_weight = int(self.limits["url_weight"])
        weighted = weighted_length(payload_text, url_weight)
        over_limit = bool(payload_text) and weighted > char_limit
        status, reasons, depends = self._decide_status(spec, payload_text, over_limit)

        title_limit: int | None = None
        if title:
            title_limit = int(
                self.limits["youtube_title_chars"]
                if spec.id == "yt-main"
                else self.limits["youtube_short_title_chars"]
            )
        title_over = bool(title and title_limit and len(title) > title_limit)
        if title_over and status not in (STATUS_BLOCKED, STATUS_OMITTED):
            status = STATUS_NEEDS_REVIEW
            reasons = reasons + ["title_over_limit"]

        offset = int(self.offsets.get(spec.id, spec.offset_days))
        source = str(entry.get("source") or ("generated" if payload_text else "missing"))
        link = self.youtube if primary_kind == "youtube" else self.amazon
        return {
            "id": spec.id,
            "campaign_id": stable_id(self.book_id, spec.id),
            "platform": spec.platform,
            "type": spec.kind,
            "label": spec.label,
            "offset_days": offset,
            "offset_label": f"T+{offset}",
            "scheduled_at": scheduled_at(self.campaign_start, offset, self.tz),
            "timezone": str(
                self.global_cfg.get("schedule", {}).get("timezone") or DEFAULT_TIMEZONE
            ),
            "title": title,
            "text": text,
            "description": description,
            "overlays": overlays,
            "shotlist": shotlist,
            "primary_link": {
                "kind": primary_kind,
                "url": str(link.get("url") or ""),
                "url_status": link.get("url_status"),
                "syntax": link.get("syntax"),
                "source": link.get("source"),
            },
            "secondary_links": [
                {
                    "kind": "shelf",
                    "url": str(self.brand.get("shelf_url") or ""),
                    "note": "Programmuebersicht, kein Buch-Deeplink",
                }
            ],
            "media": media,
            "related_video_ref": related_video_ref,
            "profile_ref": profile_ref,
            "reviewed": bool(entry.get("reviewed", False)),
            "notes": str(entry.get("notes") or "").strip(),
            "text_source": source,
            "text_status": _text_status(source, payload_text, over_limit),
            "publish_status": (
                STATUS_READY if status in (STATUS_READY, STATUS_GENERATED) else status
            ),
            "status": status,
            "reasons": reasons,
            "depends_on": depends,
            "placeholders": (
                ["amazon_url"]
                if "amazon_url_missing" in reasons and payload_text
                else []
            ),
            "validation": {
                "weighted_chars": weighted,
                "weighted_chars_limit": char_limit,
                "weighted_chars_status": "over_limit" if over_limit else "ok",
                "weighted_chars_note": (
                    "konservative Naeherung; URLs zaehlen als "
                    f"{url_weight} Zeichen, keine Plattformvalidierung"
                ),
                "target_band": (
                    [int(self.limits["x_target_min"]), int(self.limits["x_target_max"])]
                    if spec.platform == "x"
                    else None
                ),
                "title_chars": len(title) if title else None,
                "title_limit": title_limit,
                "title_status": "over_limit" if title_over else ("ok" if title else None),
                "url_syntax": link.get("syntax") if link.get("url") else "not_checked",
                "media_exists": all(ref.get("exists", True) for ref in media),
            },
        }

    # -- Manifest ----------------------------------------------------------

    def _media_list(self, posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        collected: dict[str, dict[str, Any]] = {}
        for post in posts:
            for ref in post["media"]:
                path = str(ref.get("path") or "")
                if not path:
                    continue
                entry = collected.setdefault(
                    path,
                    {
                        "path": path,
                        "kind": ref.get("kind"),
                        "exists": bool(ref.get("exists", True)),
                        "used_by": [],
                    },
                )
                if post["id"] not in entry["used_by"]:
                    entry["used_by"].append(post["id"])
                for key in (
                    "chapter",
                    "scene",
                    "title",
                    "ai_generated",
                    "clip_start_seconds",
                    "clip_duration_seconds",
                    "clip_start_measured",
                    "note",
                ):
                    if ref.get(key) is not None and entry.get(key) is None:
                        entry[key] = ref[key]
        return [collected[path] for path in sorted(collected)]

    def _affected(self, posts: list[dict[str, Any]], key: str) -> list[str]:
        return [post["id"] for post in posts if key in post["depends_on"]]

    def _disclosure(self) -> dict[str, str]:
        if not self.songs:
            return {
                "requires_synthetic_media_disclosure": "unknown",
                "basis": (
                    "keine Musik-/Videodaten hinterlegt; Kennzeichnungspflicht "
                    "nicht beurteilbar"
                ),
            }
        flags = {song["ai_generated"] for song in self.songs}
        if flags == {"false"}:
            return {
                "requires_synthetic_media_disclosure": "false",
                "basis": "Songdaten sind im Buchdatensatz als nicht KI-generiert gefuehrt",
            }
        if "true" in flags:
            return {
                "requires_synthetic_media_disclosure": "true",
                "basis": "mindestens eine Songdatei ist als KI-generiert gefuehrt",
            }
        return {
            "requires_synthetic_media_disclosure": "unknown",
            "basis": "Songdaten ohne belegte Einordnung (ai_generated: unknown)",
        }

    def _missing_items(
        self, posts: list[dict[str, Any]], media: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        amazon_status = (
            "missing" if self.amazon["url_status"] == "missing" else self.amazon["syntax"]
        )
        if amazon_status != "ok":
            items.append(
                {
                    "item": "amazon_url",
                    "status": amazon_status,
                    "affects": self._affected(posts, "amazon_url"),
                    "resolution": (
                        "books/<id>/export.yaml: website.amazon_url setzen "
                        "(oder marketing.amazon_url fuer eine abweichende Ausgabe)"
                    ),
                }
            )
        if not self.songs or not self.lead_song:
            items.append(
                {
                    "item": "song_data",
                    "status": "missing",
                    "affects": self._affected(posts, "song_file"),
                    "resolution": (
                        "marketing.songs in export.yaml pflegen und die Audiodatei "
                        "repo-relativ unter books/<id>/assets/ ablegen"
                    ),
                }
            )
        if self.youtube["url_status"] == "missing":
            items.append(
                {
                    "item": "youtube_url",
                    "status": "missing",
                    "affects": self._affected(posts, "youtube_url"),
                    "resolution": (
                        "marketing.youtube.url oder marketing.youtube.video_id "
                        "in export.yaml eintragen"
                    ),
                }
            )
        elif not self.youtube["public"]:
            items.append(
                {
                    "item": "youtube_public",
                    "status": "pending",
                    "affects": self._affected(posts, "youtube_url"),
                    "resolution": (
                        "marketing.youtube.public auf true setzen, sobald das "
                        "Video oeffentlich erreichbar ist"
                    ),
                }
            )
        if not self.sample:
            items.append(
                {
                    "item": "sample_passage",
                    "status": "missing",
                    "affects": ["x-t8-sample"],
                    "resolution": "fertige DE-Szenen im gewaehlten Style erzeugen",
                }
            )
        if not self.cover:
            items.append(
                {
                    "item": "cover_image",
                    "status": "missing",
                    "affects": ["x-t0-intro", "x-t2-youtube", "yt-main"],
                    "resolution": (
                        "Cover unter books/<id>/assets/covers/ ablegen oder "
                        "cover.image_path in export.yaml setzen"
                    ),
                }
            )
        if not self.chapter_images:
            items.append(
                {
                    "item": "chapter_images",
                    "status": "missing",
                    "affects": ["x-t5-content", "x-t8-sample", "x-t12-second-angle"],
                    "resolution": (
                        "Kapitelbilder erzeugen (tools/generate_illustration.py) "
                        "oder marketing.media setzen"
                    ),
                }
            )
        for entry in media:
            if not entry.get("exists", True):
                items.append(
                    {
                        "item": f"media_file:{entry['path']}",
                        "status": "missing",
                        "affects": entry["used_by"],
                        "resolution": "Datei anlegen oder marketing.media korrigieren",
                    }
                )
        for post in posts:
            if post["status"] in (STATUS_OMITTED, STATUS_BLOCKED):
                # Materialgrund ist bereits oben dokumentiert.
                continue
            if post["text_status"] == "missing":
                items.append(
                    {
                        "item": f"text:{post['id']}",
                        "status": "missing",
                        "affects": [post["id"]],
                        "resolution": (
                            "work/marketing/generated.json erzeugen oder "
                            f"work/marketing/overrides/{post['id']}.md anlegen"
                        ),
                    }
                )
        return items

    def _data_sources(self) -> list[dict[str, Any]]:
        book_rel = f"books/{self.book_id}"
        sources: list[dict[str, Any]] = [
            {"kind": "book_yaml", "path": f"{book_rel}/book.yaml"},
            {"kind": "export_yaml", "path": f"{book_rel}/export.yaml"},
            {"kind": "global_config", "path": GLOBAL_CONFIG_PATH},
        ]
        if self.cover:
            sources.append({"kind": "cover", "path": self.cover["path"]})
        if self.chapter_images:
            sources.append(
                {
                    "kind": "chapter_images",
                    "path": f"{book_rel}/assets/chapter",
                    "count": len(self.chapter_images),
                }
            )
        if self.sample:
            sources.append(
                {
                    "kind": "sample_passage",
                    "path": self.sample["source"],
                    "chapter": self.sample["chapter"],
                    "scene": self.sample["scene"],
                    "note": "echte Passage aus der fertigen DE-Ausgabe, an Satzgrenze gekuerzt",
                }
            )
        for song in self.songs:
            sources.append(
                {
                    "kind": "song",
                    "id": song["id"],
                    "path": song["file"],
                    "exists": song["file_exists"],
                }
            )
        generated_file = generated_path(self.book_root_dir)
        if generated_file.exists():
            sources.append(
                {
                    "kind": "generated_texts",
                    "path": rel_path(self.repo_root, generated_file),
                    "generator": str(self.generated.get("generator") or ""),
                    "model": str(self.generated.get("model") or ""),
                }
            )
        for override in sorted(overrides_dir(self.book_root_dir).glob("*.md")):
            sources.append(
                {"kind": "text_override", "path": rel_path(self.repo_root, override)}
            )
        return sources

    def _assemble(self, posts: list[dict[str, Any]]) -> dict[str, Any]:
        media = self._media_list(posts)
        missing = self._missing_items(posts, media)
        disclosure = self._disclosure()
        yt_main = next((post for post in posts if post["id"] == "yt-main"), None)
        shorts = [post for post in posts if post["type"].startswith("short_")]
        open_posts = [
            post["id"]
            for post in posts
            if post["status"] not in (STATUS_READY, STATUS_GENERATED)
        ]
        over_limit = [
            post["id"]
            for post in posts
            if post["validation"]["weighted_chars_status"] == "over_limit"
        ]
        offsets = {
            spec.id: int(self.offsets.get(spec.id, spec.offset_days))
            for spec in POST_SPECS
        }
        return {
            "schema_version": SCHEMA_VERSION,
            "campaign_id": f"{self.book_id}-marketing",
            "book": {
                "id": self.book_id,
                "title": str(self.meta.get("title") or "").strip(),
                "subtitle": str(self.meta.get("subtitle") or "").strip(),
                "author": str(self.meta.get("author") or "").strip(),
                "language": str(self.meta.get("language") or "de-DE").strip(),
                "translator": str(self.meta.get("translator") or "").strip(),
                "translator_label": str(self.meta.get("translator_label") or "").strip(),
                "publisher": str(self.meta.get("publisher") or "").strip(),
                "style": self.style,
                "source_lang": str(self.book.get("source_lang") or ""),
                "target_lang": str(self.book.get("target_lang") or ""),
                "structure_mode": str(
                    (self.book.get("structure") or {}).get("mode") or ""
                ),
            },
            "edition": {
                "original_title": str(self.meta.get("original_title") or "").strip(),
                "original_author": str(self.meta.get("original_author") or "").strip(),
                "rights": str(self.meta.get("rights") or "").strip(),
                "is_translation": str(self.book.get("source_lang") or "")
                != str(self.book.get("target_lang") or ""),
                "edition_notes": [
                    str(item).strip()
                    for item in (self.meta.get("title_page_extra") or [])
                    if str(item).strip()
                ],
                "note": (
                    "Nur belegte Angaben aus export.yaml; keine erfundenen "
                    "Zusatzleistungen."
                ),
            },
            "data_sources": self._data_sources(),
            "amazon": self.amazon,
            "youtube": self.youtube,
            "songs": self.songs,
            "campaign": {
                "start": (
                    self.campaign_start.isoformat(timespec="seconds")
                    if self.campaign_start
                    else None
                ),
                "start_source": (
                    "marketing.campaign_start" if self.campaign_start else "unset"
                ),
                "timezone": str(
                    self.global_cfg.get("schedule", {}).get("timezone")
                    or DEFAULT_TIMEZONE
                ),
                "relative_dates_only": self.campaign_start is None,
                "offsets_days": offsets,
                "note": (
                    "Kampagnenstart ist nicht das Erscheinungsdatum. Ohne Startdatum "
                    "bleiben die relativen Termine gueltig."
                ),
            },
            "posts": posts,
            "youtube_materials": {
                "video": yt_main,
                "shorts": shorts,
                "note": (
                    "Liedvideo und Shorts entstehen nur bei vorhandenem Song; "
                    "Short-Verweise auf das vollstaendige Video sind Anweisungen "
                    "fuer eine spaetere Veroeffentlichung, keine fertigen Links."
                ),
            },
            "media": media,
            "missing": missing,
            "validation": {
                "ok": all(post["publish_status"] == STATUS_READY for post in posts),
                "open_posts": open_posts,
                "over_limit_posts": over_limit,
                "url_checks": {
                    "amazon": self.amazon.get("syntax"),
                    "youtube": self.youtube.get("syntax"),
                    "note": (
                        "Syntaktische Pruefung; kein Nachweis, dass die Adresse zur "
                        "Ausgabe gehoert oder veroeffentlicht ist."
                    ),
                },
                "limits": self.limits,
                "notes": (
                    "weighted_chars ist eine konservative Naeherung (URLs = 23 "
                    "Zeichen, breite Zeichen = 2), keine Plattformvalidierung."
                ),
            },
            "delivery": {
                "requires_synthetic_media_disclosure": disclosure[
                    "requires_synthetic_media_disclosure"
                ],
                "requires_synthetic_media_disclosure_basis": disclosure["basis"],
                "made_for_kids": "not_set",
                "made_for_kids_note": (
                    "Unabhaengig von der Kennzeichnung synthetischer Medien; daraus "
                    "nicht ableitbar."
                ),
                "dependencies": missing,
                "instructions": [
                    "Dieses Paket veroeffentlicht nichts und spricht keine Plattform-API an.",
                    "Normale URLs in Shorts-Beschreibungen sind nicht zuverlaessig "
                    "anklickbar; verknuepftes Video bzw. Kanal-Profil setzen.",
                    "T+2 und das Liedvideo erst nach bestaetigter oeffentlicher "
                    "Verfuegbarkeit veroeffentlichen.",
                ],
                "handover": {
                    "target": "Postiz oder gleichwertiger Dienst",
                    "input": "campaign.json",
                },
            },
            "sample": self.sample,
            "text_provenance": {
                "generator": str(self.generated.get("generator") or "unbekannt"),
                "model": str(self.generated.get("model") or ""),
                "generated_at": str(self.generated.get("generated_at") or ""),
                "prompt_version": str(
                    self.generated.get("prompt_version") or PROMPT_VERSION
                ),
                "source_hash": str(self.generated.get("source_hash") or ""),
                "override_texts": sorted(
                    post_id
                    for post_id, entry in self.texts.items()
                    if str(entry.get("source")) == "override"
                ),
                "note": "generated_at erzwingt keine neue Inhaltsversion.",
            },
            "exported_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }


# ---------------------------------------------------------------------------
# Einstiegspunkte
# ---------------------------------------------------------------------------


def load_export_data(book: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    return load_yaml(repo_root / str(book.get("export_config") or ""))


def _name_lines(book: dict[str, Any], repo_root: Path, limit: int = 40) -> list[str]:
    from lib.name_registry import compact_name_lines, load_names

    path = repo_root / str(book.get("names_file") or "")
    if not path.exists():
        return []
    return compact_name_lines(load_names(path), limit=limit, include_meta=False)


def campaign_brief(
    book: dict[str, Any],
    repo_root: Path,
    style: str,
    global_cfg: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Kompakter Datenbrief fuer die Texterzeugung und ihre Quellpruefsumme.

    Enthaelt Metadaten, Glossar und genau eine echte Leseprobe -- bewusst
    nicht den ganzen Roman.
    """
    cfg = global_cfg or load_global_config(repo_root)
    export_data = load_export_data(book, repo_root)
    meta = export_meta(book, repo_root)
    book_root_dir = book_root(book, repo_root)
    marketing = marketing_block(export_data)
    sample = select_sample(book, style, repo_root, cfg.get("sample") or {})
    songs = song_entries(marketing, book_root_dir)
    lead = next((song for song in songs if song["file"] and song["file_exists"]), None)
    return {
        "book_id": str(book.get("id")),
        "title": str(meta.get("title") or "").strip(),
        "subtitle": str(meta.get("subtitle") or "").strip(),
        "author": str(meta.get("author") or "").strip(),
        "translator": str(meta.get("translator") or "").strip(),
        "translator_label": str(meta.get("translator_label") or "").strip(),
        "publisher": str(meta.get("publisher") or "").strip(),
        "language": str(meta.get("language") or "de-DE").strip(),
        "original_title": str(meta.get("original_title") or "").strip(),
        "original_author": str(meta.get("original_author") or "").strip(),
        "description": str(meta.get("description") or "").strip(),
        "summary": str(meta.get("summary") or "").strip(),
        "author_bio": str(meta.get("author_bio") or "").strip(),
        "edition_notes": [
            str(item).strip()
            for item in (meta.get("title_page_extra") or [])
            if str(item).strip()
        ],
        "style": style,
        "source_lang": str(book.get("source_lang") or ""),
        "target_lang": str(book.get("target_lang") or ""),
        "names": _name_lines(book, repo_root),
        "sample_passage": sample,
        "brand": brand_config(cfg),
        "limits": limits_config(cfg),
        "offsets_days": schedule_offsets(cfg),
        "post_ids": [spec.id for spec in POST_SPECS],
        "song": (
            {
                "title": lead["title"],
                "ai_generated": lead["ai_generated"],
                "credits": lead["credits"],
            }
            if lead
            else None
        ),
        "shelf_url": str(brand_config(cfg).get("shelf_url") or ""),
    }


def build_campaign(
    book: dict[str, Any],
    repo_root: Path,
    style: str,
    *,
    global_cfg: dict[str, Any] | None = None,
    texts: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Baut das Kampagnenmanifest aus vorhandenen Buchdaten."""
    cfg = global_cfg or load_global_config(repo_root)
    export_data = load_export_data(book, repo_root)
    book_root_dir = book_root(book, repo_root)
    text_map = texts if texts is not None else collect_texts(book_root_dir)
    generated = load_generated(book_root_dir)
    runner = CampaignRunner(
        repo_root, book, style, cfg, export_data, text_map, generated
    )
    return runner.build()


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _status_line(post: dict[str, Any]) -> str:
    return (
        f"Status `{post['status']}` | Text `{post['text_status']}` | "
        f"Veroeffentlichung `{post['publish_status']}`"
    )


def _media_line(post: dict[str, Any]) -> str:
    if not post["media"]:
        return "keine"
    return ", ".join(f"{ref.get('kind')}: {ref.get('path')}" for ref in post["media"])


def render_posts_md(manifest: dict[str, Any]) -> str:
    book = manifest["book"]
    campaign = manifest["campaign"]
    amazon = manifest["amazon"]
    lines = [
        f"# X-Beitraege - {book['title']} ({book['author']})",
        "",
        f"- Kampagnenstart: {campaign['start'] or 'nicht gesetzt (relative Termine bleiben gueltig)'}",
        f"- Zeitzone: {campaign['timezone']}",
        f"- Amazon-Link: {amazon['url'] or 'fehlt'} (Quelle: {amazon['source']})",
        "- Zeichenangaben sind eine konservative Naeherung (URLs = 23 Zeichen),",
        "  keine Plattformvalidierung.",
        "",
    ]
    for post in manifest["posts"]:
        if post["platform"] != "x":
            continue
        validation = post["validation"]
        lines += [
            f"## {post['offset_label']} - {post['label']} (`{post['id']}`)",
            "",
            f"- {_status_line(post)}",
            f"- Geplant: {post['scheduled_at'] or 'relativ (kein Startdatum gesetzt)'}",
            (
                f"- Zeichen (gewichtet): {validation['weighted_chars']} / "
                f"{validation['weighted_chars_limit']} | Zielband "
                f"{validation['target_band']}"
            ),
            (
                f"- Hauptlink: {post['primary_link']['kind']} "
                f"({post['primary_link']['url_status']}, {post['primary_link']['syntax']})"
            ),
            f"- Medien: {_media_line(post)}",
        ]
        if post["reasons"]:
            lines.append(f"- Offene Gruende: {', '.join(post['reasons'])}")
        if post["placeholders"]:
            lines.append(
                "- Enthaelt offenen Platzhalter: " + ", ".join(post["placeholders"])
            )
        if post["notes"]:
            lines.append(f"- Redaktionsnotiz: {post['notes']}")
        lines += ["", "```text", post["text"] or "<kein Text vorhanden>", "```", ""]
    return "\n".join(lines).rstrip() + "\n"


def _shotlist_md(shotlist: list[dict[str, Any]]) -> list[str]:
    if not shotlist:
        return []
    lines = [
        "Shotlist (Reihenfolge | Bildquelle | Texteinblendung | Buchbezug | Audio | "
        "Start | geplante Dauer | fehlende Angaben):",
        "",
    ]
    for shot in shotlist:
        start = (
            shot["audio_start_seconds"]
            if shot["audio_start_seconds"] is not None
            else "unbekannt"
        )
        duration = (
            shot["planned_duration_seconds"]
            if shot["planned_duration_seconds"] is not None
            else "unbekannt"
        )
        lines.append(
            f"{shot['order']}. {shot['image_source']} | {shot['overlay'] or '-'} | "
            f"{shot['book_ref']} | {shot['audio_source'] or '-'} | {start} | "
            f"{duration} | {', '.join(shot['missing']) or '-'}"
        )
    lines += [
        "",
        "Geplante Dauern sind Vorschlaege; gemessene Timecodes liegen nicht vor.",
    ]
    return lines


def _youtube_block(post: dict[str, Any], lines: list[str]) -> None:
    validation = post["validation"]
    lines += [
        f"## {post['offset_label']} - {post['label']} (`{post['id']}`)",
        "",
        f"- {_status_line(post)}",
        f"- Geplant: {post['scheduled_at'] or 'relativ (kein Startdatum gesetzt)'}",
        (
            f"- Titel: {validation['title_chars']} / {validation['title_limit']} Zeichen"
            if post["title"]
            else "- Titel: keiner"
        ),
        (
            f"- Beschreibung (gewichtet): {validation['weighted_chars']} / "
            f"{validation['weighted_chars_limit']}"
        ),
        f"- Medien: {_media_line(post)}",
    ]
    if post["reasons"]:
        lines.append(f"- Offene Gruende: {', '.join(post['reasons'])}")
    if post["notes"]:
        lines.append(f"- Redaktionsnotiz: {post['notes']}")
    if post.get("related_video_ref"):
        ref = post["related_video_ref"]
        lines.append(
            "- Verknuepftes Video (Anweisung, kein fertiger Link): "
            f"{ref['resolution']} | verfuegbar: {ref['available']}"
        )
    if post.get("profile_ref"):
        lines.append("- Kanal-Profil: siehe profile_ref im Manifest")
    if post["overlays"]:
        lines.append("- Texteinblendungen: " + " | ".join(post["overlays"]))
    lines.append("")
    if post["title"]:
        lines += ["Titel:", "", "```text", post["title"], "```", ""]
    if post["description"]:
        lines += ["Beschreibung:", "", "```text", post["description"], "```", ""]
    elif post["text"]:
        lines += ["Text:", "", "```text", post["text"], "```", ""]
    lines += _shotlist_md(post["shotlist"])
    lines.append("")


def render_youtube_md(manifest: dict[str, Any]) -> str:
    book = manifest["book"]
    materials = manifest["youtube_materials"]
    delivery = manifest["delivery"]
    video = materials["video"]
    video_usable = bool(video) and video["status"] not in (
        STATUS_OMITTED,
        STATUS_BLOCKED,
    )
    lines = [
        f"# YouTube-Materialien - {book['title']} ({book['author']})",
        "",
        f"- Liedvideo vorhanden: {'ja' if video_usable else 'nein'}",
        (
            "- Positionen: "
            + (
                ", ".join(
                    f"{post['id']} ({post['status']})" for post in materials["shorts"]
                )
                or "keine"
            )
        ),
        f"- YouTube-Adresse: {manifest['youtube']['url'] or 'noch nicht bekannt'}",
        (
            "- Kennzeichnung synthetischer Medien: "
            f"{delivery['requires_synthetic_media_disclosure']} "
            f"({delivery['requires_synthetic_media_disclosure_basis']})"
        ),
        (
            "- Made for Kids: nicht gesetzt und unabhaengig von der Kennzeichnung "
            "synthetischer Medien."
        ),
        "",
        "Normale URLs in Shorts-Beschreibungen sind kein verlaesslicher anklickbarer",
        "Weg zum Buch; verknuepftes Video bzw. Kanal-Profil setzen.",
        "",
    ]
    if video_usable:
        _youtube_block(materials["video"], lines)
    else:
        reason = (
            ", ".join(materials["video"]["reasons"])
            if materials["video"]
            else "no_song_data"
        )
        lines += [
            "## Kein Liedvideo",
            "",
            f"- Grund: {reason}",
            "- Ohne Songdaten wird hier kein Liedvideo-Material erzeugt.",
            "",
        ]
    for short in materials["shorts"]:
        if short["status"] in (STATUS_OMITTED, STATUS_BLOCKED):
            lines += [
                f"## {short['offset_label']} - {short['label']} (`{short['id']}`)",
                "",
                f"- Status `{short['status']}` - ausgelassen ({', '.join(short['reasons'])})",
                "",
            ]
            continue
        _youtube_block(short, lines)
    return "\n".join(lines).rstrip() + "\n"


STATUS_LEGEND = [
    ("generated", "Text liegt vor, ist aber noch nicht redaktionell freigegeben"),
    ("ready", "Text und alle Voraussetzungen sind erfuellt (manuell uebernommen)"),
    ("needs_review", "Text fehlt oder ueberschreitet ein Plattformlimit"),
    ("needs_amazon_url", "Text fertig, Amazon-Link fehlt"),
    ("needs_youtube_url", "Text fertig, YouTube-Adresse fehlt"),
    ("blocked", "Medium/Adresse vorhanden, aber unbrauchbar oder nicht oeffentlich"),
    ("omitted", "Position bewusst ausgelassen, weil Material fehlt"),
]


def render_readme_md(manifest: dict[str, Any]) -> str:
    book = manifest["book"]
    campaign = manifest["campaign"]
    amazon = manifest["amazon"]
    youtube = manifest["youtube"]
    limits = manifest["validation"]["limits"]
    lines = [
        f"# Marketingpaket - {book['title']}",
        "",
        "Dieses Paket wurde aus den vorhandenen Buchdaten erzeugt. Es",
        "veroeffentlicht nichts und spricht keine Plattform-API an.",
        "",
        "## Dateien",
        "",
        "- `campaign.json` - maschinenlesbares Kampagnenmanifest (Uebergabe an Postiz o. Ae.)",
        "- `posts.md` - X-Beitraege zum Kopieren",
        "- `youtube.md` - Liedvideo und Shorts (Titel, Beschreibung, Shotlist)",
        "- `media.json` - Medienuebersicht mit repo-relativen Pfaden",
        "- `README.md` - diese Hinweise",
        "",
        "## Offene Angaben in diesem Paket",
        "",
    ]
    missing = manifest["missing"]
    if missing:
        for item in missing:
            lines.append(
                f"- `{item['item']}` ({item['status']}) - betrifft: "
                f"{', '.join(item['affects']) or 'kampagnenweit'} - {item['resolution']}"
            )
    else:
        lines.append("- keine offenen Angaben")
    lines += [
        "",
        "## Angaben pflegen",
        "",
        f"- Amazon-Link: `books/{book['id']}/export.yaml` -> `website.amazon_url` "
        "(oder `marketing.amazon_url` fuer eine abweichende Ausgabe). Der Link wird als "
        "Benutzerangabe uebernommen; es findet keine Pruefung gegen die Amazon-Ausgabe statt.",
        f"- YouTube-Adresse spaeter: `books/{book['id']}/export.yaml` -> "
        "`marketing.youtube.url` (oder `video_id`) und `public: true`, sobald das Video "
        "oeffentlich ist. Ein erneuter Export aktualisiert dann nur Linkfeld, "
        "zusammengesetzte Texte und Validierung.",
        f"- Kampagnenstart: `books/{book['id']}/export.yaml` -> `marketing.campaign_start` "
        "(ISO 8601, Europe/Berlin). Ohne Startdatum bleiben die relativen Termine gueltig.",
        f"- Songdaten: `books/{book['id']}/export.yaml` -> `marketing.songs` mit `file`, "
        "`title`, `lyrics_file`, `clip_start_seconds`, `clip_duration_seconds`, `credits`, "
        "`ai_generated`. Fehlende Songs blockieren nur die Musikbestandteile.",
        f"- Bildzuordnung: `books/{book['id']}/export.yaml` -> `marketing.media` "
        "(`<post-id>: assets/chapter/chapter-012.jpg`).",
        "",
        "## Texte erzeugen und bearbeiten",
        "",
        f"- Generierte Texte: `books/{book['id']}/work/marketing/generated.json`",
        f"- Manuelle Fassung: `books/{book['id']}/work/marketing/overrides/<post-id>.md` "
        "(hat Vorrang und wird als `override` gekennzeichnet)",
        "",
        "```bash",
        f"python tools/export_marketing.py --book {book['id']} --dry-run",
        f"python tools/export_marketing.py --book {book['id']}",
        "```",
        "",
        "Ein erneuter Export erzeugt keine neuen Beitrags-IDs und keine neuen Texte; neu",
        "erzeugt wird nur bei geaenderten Quelldaten, geaenderter Prompt-Version oder",
        "`--regenerate`.",
        "",
        "## Statuswerte",
        "",
    ]
    for name, meaning in STATUS_LEGEND:
        lines.append(f"- `{name}`: {meaning}")
    lines += [
        "",
        "Textlage (`text_status`) und Veroeffentlichungsreife (`publish_status`) sind",
        "getrennt: ein Text kann fertig sein, waehrend ein Video noch nicht oeffentlich ist.",
        "",
        "## Angaben zu diesem Lauf",
        "",
        f"- Kampagnenstart: {campaign['start'] or 'nicht gesetzt'} "
        f"(Quelle: {campaign['start_source']})",
        f"- Zeitzone: {campaign['timezone']}",
        f"- Amazon-Link: {amazon['url'] or 'fehlt'} (Quelle: {amazon['source']}, "
        f"Syntax: {amazon['syntax']})",
        f"- YouTube: {youtube['url'] or 'noch nicht bekannt'} "
        f"(oeffentlich: {youtube['public']})",
        f"- Songs hinterlegt: {len(manifest['songs'])}",
        f"- Textgenerator: {manifest['text_provenance']['generator']} "
        f"(Modell: {manifest['text_provenance']['model'] or 'nicht zutreffend'}, "
        f"Prompt-Version: {manifest['text_provenance']['prompt_version']})",
        "",
        "## Zeichengrenzen",
        "",
        f"- X: {limits['x_weighted_chars']} gewichtete Zeichen, Zielband "
        f"{limits['x_target_min']}-{limits['x_target_max']}",
        f"- YouTube-Titel: {limits['youtube_title_chars']} Zeichen",
        f"- YouTube-Beschreibung: {limits['youtube_description_chars']} Zeichen",
        "",
        "Die gewichtete Laenge ist eine konservative Naeherung (URLs zaehlen als 23",
        "Zeichen, breite Zeichen als 2) und keine Plattformvalidierung.",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def check_no_placeholders_in_ready(manifest: dict[str, Any]) -> None:
    """Ein versandfertiger Beitrag darf keinen offenen Platzhalter enthalten."""
    for post in manifest["posts"]:
        if post["publish_status"] == STATUS_READY and post["placeholders"]:
            raise ValueError(
                f"Beitrag {post['id']} ist als bereit markiert, enthaelt aber "
                f"Platzhalter: {', '.join(post['placeholders'])}"
            )


def write_package(manifest: dict[str, Any], export_dir: Path) -> list[Path]:
    check_no_placeholders_in_ready(manifest)
    export_dir.mkdir(parents=True, exist_ok=True)
    payloads = {
        "campaign.json": json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        "posts.md": render_posts_md(manifest),
        "youtube.md": render_youtube_md(manifest),
        "media.json": json.dumps(
            {
                "book_id": manifest["book"]["id"],
                "media": manifest["media"],
                "note": (
                    "Pfade sind repo-relativ (POSIX), damit das Paket uebertragbar "
                    "bleibt."
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        "README.md": render_readme_md(manifest),
    }
    written: list[Path] = []
    for name, text in payloads.items():
        path = export_dir / name
        path.write_text(text, encoding="utf-8", newline="")
        written.append(path)
    return written


