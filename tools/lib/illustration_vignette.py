"""
illustration_vignette.py
========================

Waehlt fuer die Kapitelillustration *einen* bildtragenden Moment aus dem
Kapitel und legt ihn strukturiert als JSON ab, damit der Prompt
nachvollziehbar, editierbar und ohne erneute KI-Kosten reproduzierbar ist.

Hintergrund: Der bisherige Prompt bestand zur Haelfte aus einem festen
``illustration_setting`` (Ort, Wetter, Figurenkostueme) und nahm als
Szenenanteil die *ersten zwei Absaetze* des Kapitels. Bei Kapitelanfaengen
mit Wetter- und Ortsbeschreibung kam so in jedem Kapitel dieselbe Kulisse
heraus, und Figuren, die im Kapitel nur *erwaehnt* werden, landeten als
anwesend im Bild. Die Vignette dreht das um: zuerst der Moment
(Person + Handlung + Ort), dann Figuren, dann Stil.

Ablauf:
    ``ensure_vignette(...)`` liest oder schreibt
    ``<work>/prompts/higgsfield/vignettes/<kapitel>.json``.

Provider:
- ``auto``       - vorhandene Datei nutzen, sonst Heuristik (keine API-Kosten)
- ``none``       - Heuristik erzwingen
- ``openrouter`` - LLM waehlt Moment und anwesende Figuren
- ``off``        - keine Vignette; der Aufrufer baut den bisherigen Prompt

JSON-Felder (englische Schluessel wie in den uebrigen Metadaten, Inhalte in
der Buchsprache):

- ``moment``      eine Handlung mit Person und Ort, ein Satz
- ``figures``     nur koerperlich anwesende Figuren
                  (``name``, ``action``, ``look``)
- ``props``       konkrete Gegenstaende, die das Bild traegt
- ``composition`` Bildausschnitt (``wide establishing shot``, ``medium shot``,
                  ``close-up``, ``low angle``, ``high angle``,
                  ``over-the-shoulder``, ``two-shot``)
- ``beat``        ein Wort zum dramatischen Kern (Konfrontation, Verlust ...)
- ``evidence``    Absatznummern, auf die sich der Moment stuetzt
- ``source``      ``heuristic``, ``openrouter`` oder ``manual``
- ``text_sha256`` Fingerabdruck des Kapiteltexts; aendert er sich, ist die
                  Vignette veraltet (``is_stale``)
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from lib.name_registry import load_names
from lib.openrouter_client import OpenRouterClient, OpenRouterError
from lib.output_paths import book_output_root


VIGNETTE_VERSION = 1
DEFAULT_MODEL = "google/gemini-2.5-flash-lite"
MAX_MOMENT_CHARS = 220
MAX_LOOK_CHARS = 140

COMPOSITIONS = (
    "wide establishing shot",
    "medium shot",
    "close-up",
    "low angle",
    "high angle",
    "over-the-shoulder",
    "two-shot",
)

PROVIDERS = ("auto", "none", "openrouter", "off")


class VignetteError(RuntimeError):
    """Fehler beim Laden, Pruefen oder Erzeugen einer Vignette."""


# ---------------------------------------------------------------------------
# Datenmodell
# ---------------------------------------------------------------------------


@dataclass
class Figure:
    name: str
    action: str = ""
    look: str = ""


@dataclass
class Vignette:
    chapter: str
    moment: str
    title: str = ""
    figures: list[Figure] = field(default_factory=list)
    props: list[str] = field(default_factory=list)
    composition: str = ""
    beat: str = ""
    evidence: list[int] = field(default_factory=list)
    source: str = "heuristic"
    model: str | None = None
    created: str = ""
    text_sha256: str = ""
    usage: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": VIGNETTE_VERSION,
            "chapter": self.chapter,
            "title": self.title,
            "moment": self.moment,
            "figures": [
                {"name": f.name, "action": f.action, "look": f.look}
                for f in self.figures
            ],
            "props": list(self.props),
            "composition": self.composition,
            "beat": self.beat,
            "evidence": list(self.evidence),
            "source": self.source,
            "model": self.model,
            "created": self.created or _now(),
            "text_sha256": self.text_sha256,
            "usage": dict(self.usage),
        }


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def text_digest(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:16]


def is_stale(vignette: Vignette, text: str) -> bool:
    """True, wenn der Kapiteltext seit dem Vignettenlauf geaendert wurde."""
    if not vignette.text_sha256:
        return False
    return vignette.text_sha256 != text_digest(text)


def normalize_provider(value: str | None) -> str:
    provider = (value or "auto").strip().lower()
    if provider not in PROVIDERS:
        raise VignetteError(
            f"Unbekannter Vignetten-Provider: {value!r}. "
            f"Erlaubt: {', '.join(PROVIDERS)}."
        )
    return provider


# ---------------------------------------------------------------------------
# Ablage
# ---------------------------------------------------------------------------


def vignette_dir(output_root: Path) -> Path:
    return output_root / "prompts" / "higgsfield" / "vignettes"


def vignette_path(output_root: Path, chapter_id: str) -> Path:
    return vignette_dir(output_root) / f"{chapter_id}.json"


def save_vignette(path: Path, vignette: Vignette) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(vignette.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def load_vignette(path: Path) -> Vignette:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise VignetteError(f"Vignette nicht lesbar ({path}): {exc}") from exc
    except json.JSONDecodeError as exc:
        raise VignetteError(f"Vignette ist kein gueltiges JSON ({path}): {exc}") from exc
    return parse_vignette_payload(
        data,
        chapter_id=str(data.get("chapter") or path.stem),
        source=str(data.get("source") or "manual"),
        model=data.get("model"),
        text_sha=str(data.get("text_sha256") or ""),
        title=str(data.get("title") or ""),
    )


# ---------------------------------------------------------------------------
# Pruefen
# ---------------------------------------------------------------------------


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _clean_list(value: Any, *, limit: int = 6) -> list[str]:
    if isinstance(value, str):
        value = [part for part in re.split(r"[,;]", value)]
    if not isinstance(value, (list, tuple)):
        return []
    result: list[str] = []
    for item in value:
        text = _clean(item)
        if text and text not in result:
            result.append(text)
        if len(result) >= limit:
            break
    return result


def _parse_evidence(value: Any) -> list[int]:
    if isinstance(value, (int, float)):
        return [int(value)]
    if not isinstance(value, (list, tuple)):
        return []
    numbers: list[int] = []
    for item in value:
        try:
            numbers.append(int(item))
        except (TypeError, ValueError):
            continue
    return numbers[:8]


def _parse_figures(value: Any) -> list[Figure]:
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, (list, tuple)):
        return []
    figures: list[Figure] = []
    for item in value:
        if isinstance(item, str):
            name = _clean(item)
            if name:
                figures.append(Figure(name=name))
            continue
        if not isinstance(item, dict):
            continue
        name = _clean(item.get("name") or item.get("figur") or item.get("figures"))
        if not name:
            continue
        figures.append(
            Figure(
                name=name,
                action=_clean(item.get("action") or item.get("aktion")),
                look=_clean(item.get("look") or item.get("aussehen"))[:MAX_LOOK_CHARS],
            )
        )
        if len(figures) >= 4:
            break
    return figures


def parse_vignette_payload(
    data: Any,
    *,
    chapter_id: str,
    source: str = "manual",
    model: str | None = None,
    text_sha: str = "",
    title: str = "",
) -> Vignette:
    """Prueft ein Vignetten-Dict und gibt eine ``Vignette`` zurueck."""
    if not isinstance(data, dict):
        raise VignetteError("Vignette muss ein JSON-Objekt sein.")
    moment = _clean(data.get("moment"))
    if not moment:
        raise VignetteError(
            "Vignette ohne 'moment': es muss ein Satz sein, der die Handlung im "
            "Bild beschreibt."
        )
    if len(moment) > MAX_MOMENT_CHARS:
        moment = _clip_sentence(moment, MAX_MOMENT_CHARS)
    composition = _clean(data.get("composition"))
    if composition not in COMPOSITIONS:
        # Unbekannte Ausschnitte sind kein Grund abzubrechen - der Prompt
        # nimmt den Text woertlich.
        composition = composition[:80]
    return Vignette(
        chapter=chapter_id,
        moment=moment,
        title=_clean(title or data.get("title")),
        figures=_parse_figures(data.get("figures")),
        props=_clean_list(data.get("props"), limit=4),
        composition=composition,
        beat=_clean(data.get("beat"))[:40],
        evidence=_parse_evidence(data.get("evidence")),
        source=_clean(source) or "manual",
        model=(str(model) if model else None),
        created=_clean(data.get("created")) or _now(),
        text_sha256=text_sha,
        usage=data.get("usage") if isinstance(data.get("usage"), dict) else {},
    )


# ---------------------------------------------------------------------------
# Textzerlegung
# ---------------------------------------------------------------------------


_META_LINE_RE = re.compile(
    r"^\s*\*?Buch:\s*"
    r"|^\s*<!--\s*status:"
    r"|^\s*(?:Kapitel-ID|Kapitel|Szene|Stil|Erstellt am|Provider|Modell|Tokens?):"
    r"|^\s*-{3,}\s*$"
)


def chapter_title(text: str) -> str:
    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            return stripped[3:].strip()
    return ""


def paragraphs(text: str) -> list[str]:
    """Absaetze des Kapitels, ohne Metazeilen und ohne Ueberschriften.

    Anders als der Auszug fuer den Legacy-Prompt bleiben Dialogabsaetze
    erhalten: der Konflikt eines Kapitels steht oft in der Rede.
    """
    result: list[str] = []
    current: list[str] = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            if current:
                result.append(" ".join(current))
                current = []
            continue
        if line.startswith("#") or _META_LINE_RE.match(line):
            continue
        current.append(line)
    if current:
        result.append(" ".join(current))
    return [re.sub(r"\s+", " ", p).strip() for p in result if p.strip()]


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _clip_sentence(text: str, limit: int) -> str:
    """Kuerzt auf ganze Saetze bis ``limit`` Zeichen."""
    text = _clean(text)
    if len(text) <= limit:
        return text
    selected = ""
    for sentence in _SENTENCE_SPLIT_RE.split(text):
        candidate = f"{selected} {sentence}".strip()
        if len(candidate) > limit:
            break
        selected = candidate
    if selected:
        return selected
    return text[:limit].rsplit(" ", 1)[0].rstrip(".,;:") + "."


def person_entries(entries: Iterable[dict[str, Any]] | None) -> list[dict[str, Any]]:
    return [
        entry
        for entry in (entries or [])
        if str(entry.get("type") or "person").strip().lower() == "person"
    ]


def _candidates(entry: dict[str, Any]) -> list[str]:
    values = [entry.get("source"), entry.get("target"), *(entry.get("aliases") or [])]
    return [str(value).strip() for value in values if str(value or "").strip()]


def entry_label(entry: dict[str, Any]) -> str:
    return str(
        entry.get("visual_label")
        or entry.get("target")
        or entry.get("source")
        or ""
    ).strip()


def count_mentions(text: str, name: str) -> int:
    value = str(name or "").strip()
    if not value:
        return 0
    if len(value) <= 2:
        return text.count(value)
    pattern = (
        rf"(?<![\w-]){re.escape(value)}(?![\w-])"
        if " " in value
        else rf"(?<![\w-]){re.escape(value)}(?:s)?(?![\w-])"
    )
    try:
        return len(re.findall(pattern, text, flags=re.IGNORECASE | re.UNICODE))
    except re.error:
        return 1 if value in text else 0


def figure_looks(entries: Iterable[dict[str, Any]] | None) -> dict[str, str]:
    """Aussehen je Figurenname aus dem Glossar (Schluessel kleingeschrieben)."""
    looks: dict[str, str] = {}
    for entry in person_entries(entries):
        look = _clean(entry.get("visual"))
        if not look:
            continue
        for name in _candidates(entry):
            looks.setdefault(name.lower(), look)
    return looks


def look_for(looks: dict[str, str], name: str) -> str:
    value = _clean(name).lower()
    if not value:
        return ""
    if value in looks:
        return looks[value]
    for key, look in looks.items():
        if key and (key in value or value in key):
            return look
    return ""


# ---------------------------------------------------------------------------
# Heuristik (ohne KI)
# ---------------------------------------------------------------------------


_ACTION_RE = re.compile(
    r"\b(?:packte|griff|riss|trat|stieß|stiess|schlug|zog|hielt|warf|kniete|"
    r"zitterte|wandte|schob|hob|senkte|presste|klemmte|stemmte|schleifte|"
    r"zerrte|bohrte|stach|sprang|stellte|holte|legte|setzte|drehte|beugte|"
    r"streckte|fasste|umklammerte|kippte|stürzte|stuerzte)(?:e|en|t|te|ten)?\b",
    re.IGNORECASE,
)

# Innerlichkeit ist kein Bild: Gedanken, Erinnerungen, Bewertungen. Solche
# Absaetze sind erzaehlerisch wichtig, als Illustration aber leer - sie
# liefern dem Bildmodell keine Handlung und keine Gegenstaende.
_INTROSPECTION_RE = re.compile(
    r"\b(?:dachte|gedanke|gedanken|erinnerte|erinnerung|wusste|spürte|spuerte|"
    r"fühlte|fuehlte|ahnte|begriff|verstand|schloss die augen|schwieg|"
    r"zweifel|hoffte|fürchtete|fuerchtete|überlegte|ueberlegte)\b",
    re.IGNORECASE,
)


def _title_terms(title: str) -> list[str]:
    terms: list[str] = []
    for word in re.findall(r"[A-Za-zÄÖÜäöüß]{5,}", title or ""):
        stem = word.lower()[:5]
        if stem not in terms:
            terms.append(stem)
    return terms


def _present_labels(text: str, entries: list[dict[str, Any]]) -> list[str]:
    present: list[str] = []
    for entry in entries:
        label = entry_label(entry)
        if not label:
            continue
        if any(count_mentions(text, name) for name in _candidates(entry)):
            if label not in present:
                present.append(label)
    return present


def _score_paragraph(
    paragraph: str,
    entries: list[dict[str, Any]],
    terms: list[str],
) -> tuple[float, list[str]]:
    score = 0.0
    present = _present_labels(paragraph, entries)
    score += 3.0 * min(3, len(present))
    score += 2.0 * min(3, len(_ACTION_RE.findall(paragraph)))
    score += 1.0 * min(4, paragraph.count("»"))
    lowered = paragraph.lower()
    title_hits = sum(1 for term in terms if term in lowered)
    score += 4.0 * title_hits
    if title_hits and present:
        # Titelbezug und eine anwesende Figur: das ist der bildtragende Absatz.
        score += 2.0
    score -= 3.5 * min(2, len(_INTROSPECTION_RE.findall(paragraph)))
    if len(paragraph) > 1200:
        score -= 2.0
    if len(paragraph) < 80:
        score -= 2.0
    return score, present


def _label_per_target(
    entries: list[dict[str, Any]],
    full_text: str,
) -> dict[str, str]:
    """Ein Label je Figur, auch wenn zwei Glossareintraege denselben Namen tragen.

    Beispiel ``die-sprache-des-anderen``: "Berto der Knecht" und "Berto der
    Sohn" heissen im Text beide "Berto". Ohne Aufloesung stuenden zwei
    Personen im Prompt, die eine Figur verdraengen. Entschieden wird ueber
    spezifische Belege ("Berto der Knecht", "Sohn Berto") im Kapiteltext.
    """
    chosen: dict[str, tuple[int, str]] = {}
    for entry in entries:
        label = entry_label(entry)
        target = str(entry.get("target") or entry.get("source") or "").strip().lower()
        if not label or not target:
            continue
        specific = [name for name in _candidates(entry) if " " in name]
        score = sum(count_mentions(full_text, name) for name in specific)
        current = chosen.get(target)
        if current is None or score > current[0]:
            chosen[target] = (score, label)
    return {target: label for target, (_score, label) in chosen.items()}


def _allowed_labels(entries: list[dict[str, Any]], full_text: str) -> set[str]:
    return set(_label_per_target(entries, full_text).values())


def build_heuristic_vignette(
    *,
    text: str,
    entries: Iterable[dict[str, Any]] | None,
    chapter_id: str,
) -> Vignette:
    """Kostenfreier Vorschlag: Absatz mit Titelbezug, Figuren und Handlung."""
    people = person_entries(entries)
    title = chapter_title(text)
    terms = _title_terms(title)
    chunks = paragraphs(text)
    if not chunks:
        raise VignetteError(
            f"Kapitel {chapter_id} enthaelt keinen Text fuer eine Vignette."
        )

    best_index = 0
    best_score = float("-inf")
    best_present: list[str] = []
    for index, chunk in enumerate(chunks):
        score, present = _score_paragraph(chunk, people, terms)
        if score > best_score:
            best_index, best_score, best_present = index, score, present

    moment = _clip_sentence(chunks[best_index], MAX_MOMENT_CHARS)
    allowed = _allowed_labels(people, text)
    labels = [label for label in best_present if label in allowed]
    if not labels:
        neighbours: list[str] = []
        for offset in (1, -1, 2, -2):
            idx = best_index + offset
            if 0 <= idx < len(chunks):
                neighbours.extend(_present_labels(chunks[idx], people))
        labels = [
            label
            for label in dict.fromkeys(neighbours)
            if label in allowed
        ]
    figures = [Figure(name=label, action="", look="") for label in labels[:3]]

    return Vignette(
        chapter=chapter_id,
        moment=moment,
        title=title,
        figures=figures,
        props=[],
        composition="medium shot" if figures else "wide establishing shot",
        beat="",
        evidence=[best_index],
        source="heuristic",
        model=None,
        created=_now(),
        text_sha256=text_digest(text),
    )


# ---------------------------------------------------------------------------
# LLM (OpenRouter)
# ---------------------------------------------------------------------------


_SYSTEM_PROMPT = (
    "Du bist Bildredakteur für einen Historienroman. Aus einem Kapitel wählst "
    "du genau den Moment, der sich als ein einziges Bild erzählen lässt, und "
    "beschreibst ihn so, dass ein Illustrator ihn ohne den Text zeichnen "
    "könnte. Antworte ausschließlich mit einem JSON-Objekt."
)


def _llm_user_prompt(
    *,
    chapter_id: str,
    title: str,
    text: str,
    entries: list[dict[str, Any]],
) -> str:
    chunks = paragraphs(text)
    numbered = "\n".join(f"[{index}] {chunk}" for index, chunk in enumerate(chunks))
    glossary: list[str] = []
    for entry in person_entries(entries):
        label = entry_label(entry)
        look = _clean(entry.get("visual"))
        if label and look:
            glossary.append(f"- {label}: {look}")

    return f"""Kapitel {chapter_id}: {title}

Aufgabe: Wähle den einen Moment dieses Kapitels, der das Bild trägt, und beschreibe ihn als Vignette.

Regeln:
1. Genau ein Moment: eine Handlung, ein Ort, ein Zeitpunkt. Kein Nacheinander, keine Bildfolge.
2. Wähle den Moment mit der stärksten sichtbaren Veränderung oder Konfrontation - nicht den Kapitelanfang, nur weil er der Anfang ist.
3. "figures": höchstens drei Figuren, nur wer in diesem Moment körperlich anwesend ist. Wer nur erwähnt, zitiert oder gedacht wird, gehört nicht dazu.
4. "moment": Deutsch, Gegenwart, maximal 220 Zeichen, eine Handlung mit Person und Ort.
5. "action": nur Haltung oder Blickrichtung, die im "moment" noch nicht steht - keine Wiederholung des Moments; sonst "".
6. "look": nur was der Text in diesem Moment hergibt (Kleidung, Statur, Gegenstand in der Hand), maximal 120 Zeichen; sonst "".
7. "props": höchstens vier konkrete Dinge, die das Bild trägt (z. B. "Eisenkette am Bug").
8. "composition": genau einer von {", ".join(COMPOSITIONS)}. Vermeide die immer gleiche Frontalansicht von Personen, die auf die Kamera zugehen.
9. "beat": ein Wort zum dramatischen Kern (z. B. Konfrontation, Abschied, Verlust, List).
10. "evidence": die Absatznummern aus dem Text, auf die sich der Moment stützt.
11. Keine Verneinungen ("kein", "ohne", "nie"), keine Bildüberschriften, keine Schrift im Bild.

Antworte mit genau diesem JSON:
{{"moment": "...", "figures": [{{"name": "...", "action": "...", "look": "..."}}], "props": ["..."], "composition": "...", "beat": "...", "evidence": [0]}}

Bekannte Figuren (Aussehen aus dem Glossar, nur nutzen wenn anwesend):
{chr(10).join(glossary) or "- (keine)"}

Kapiteltext (Absätze nummeriert):
{numbered}
"""


def _extract_json(raw: str) -> dict[str, Any]:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```[A-Za-z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        raise VignetteError(
            f"LLM-Antwort enthält kein JSON-Objekt: {raw[:300]!r}"
        )
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        raise VignetteError(
            f"LLM-Antwort ist kein gültiges JSON ({exc}): {raw[:300]!r}"
        ) from exc
    if not isinstance(data, dict):
        raise VignetteError("LLM-Antwort ist kein JSON-Objekt.")
    return data


def build_llm_vignette(
    *,
    text: str,
    entries: Iterable[dict[str, Any]] | None,
    chapter_id: str,
    model: str | None = None,
    client: OpenRouterClient | None = None,
) -> Vignette:
    """Laesst ein LLM den bildtragenden Moment waehlen."""
    people = person_entries(entries)
    model_name = model or DEFAULT_MODEL
    if client is None:
        try:
            client = OpenRouterClient.from_env(model_override=model_name)
        except OpenRouterError as exc:
            raise VignetteError(str(exc)) from exc
    try:
        raw = client.chat(
            system=_SYSTEM_PROMPT,
            user=_llm_user_prompt(
                chapter_id=chapter_id,
                title=chapter_title(text),
                text=text,
                entries=people,
            ),
            temperature=0.3,
            max_tokens=1200,
        )
    except OpenRouterError as exc:
        raise VignetteError(
            f"Vignette für Kapitel {chapter_id} konnte nicht erzeugt werden: {exc}"
        ) from exc

    vignette = parse_vignette_payload(
        _extract_json(raw),
        chapter_id=chapter_id,
        source="openrouter",
        model=model_name,
        text_sha=text_digest(text),
        title=chapter_title(text),
    )
    vignette.usage = dict(client.last_usage or {})
    return vignette


# ---------------------------------------------------------------------------
# Einstieg
# ---------------------------------------------------------------------------


def _load_entries(repo_root: Path, book: dict[str, Any]) -> list[dict[str, Any]]:
    names_file = book.get("names_file")
    if not names_file:
        return []
    path = repo_root / str(names_file)
    if not path.exists():
        return []
    return list(load_names(path) or [])


def _source_for_provider(provider: str) -> str | None:
    if provider == "openrouter":
        return "openrouter"
    if provider == "none":
        return "heuristic"
    return None


def ensure_vignette(
    *,
    repo_root: Path,
    book: dict[str, Any],
    chapter_id: str,
    text: str,
    provider: str = "auto",
    model: str | None = None,
    overwrite: bool = False,
) -> Vignette:
    """Liest die Vignette aus dem Buchpaket oder erzeugt sie neu."""
    provider = normalize_provider(provider)
    if provider == "off":
        raise VignetteError("Vignetten sind abgeschaltet (provider=off).")

    output_root = book_output_root(repo_root, book)
    path = vignette_path(output_root, chapter_id)
    requested_source = _source_for_provider(provider)

    if path.exists() and not overwrite:
        cached = load_vignette(path)
        if requested_source is None or cached.source == requested_source:
            return cached

    entries = _load_entries(repo_root, book)
    if provider == "openrouter":
        vignette = build_llm_vignette(
            text=text,
            entries=entries,
            chapter_id=chapter_id,
            model=model,
        )
    else:
        vignette = build_heuristic_vignette(
            text=text,
            entries=entries,
            chapter_id=chapter_id,
        )
    save_vignette(path, vignette)
    return vignette
