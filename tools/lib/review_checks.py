"""Review checks for translated book packages.

The review layer is report-only: it reads RU/DE scene files, writes review
reports, and never changes translation files.
"""

from __future__ import annotations

import json
import re
import statistics
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import yaml

from lib.degeneration import detect_degeneration
from lib.name_registry import compact_name_lines, load_names
from lib.output_paths import (
    book_output_root,
    find_scene_translations,
    list_source_scene_paths,
    parse_scene_number,
)


SEVERITY_ORDER = {"INFO": 0, "WARNING": 1, "ERROR": 2}
CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
REPLACEMENT_RE = re.compile(r"[\uFFFD\u0000-\u0008\u000B-\u001F]")
# Mojibake: UTF-8, das als Latin-1/CP1252 gelesen wurde (GÃ¼te, Ð"/Ñ).
# Deterministisch erkennbar, release-blockierend. Echte RU-Zitate stehen
# kyrillisch (CYRILLIC_RE), nicht mojibake-codiert.
MOJIBAKE_RE = re.compile(r"[ÃÐÑ]")
# Akzentuierte Transliterationsartefakte: das russische Betonungszeichen landet
# als Akut im deutschen Namen ("Golowín", "Krapotkín", "Dják"). Deterministisch
# pruefbar, weil die akzentfreie Form im Buchglossar (names.yaml) steht:
# akzentuierte Variante da, Glossarform nicht -> release-blockierend.
# Legitime Akzente (Franzoesisch "Molière", Ungarisch "Báthory", Pinyin
# "Shèngwǔ") haben keinen Glossareintrag und werden deshalb nicht geflaggt.
ACCENT_VOWELS = "áàâäÁÀÂÄéèêëÉÈÊËíìîïÍÌÎÏóòôöÓÒÔÖúùûüÚÙÛÜýÿÝŸ"
ACCENT_STRIP_MAP = str.maketrans({
    "á": "a", "à": "a", "â": "a", "ä": "a",
    "é": "e", "è": "e", "ê": "e", "ë": "e",
    "í": "i", "ì": "i", "î": "i", "ï": "i",
    "ó": "o", "ò": "o", "ô": "o", "ö": "o",
    "ú": "u", "ù": "u", "û": "u", "ü": "u",
    "ý": "y", "ÿ": "y",
    "Á": "A", "À": "A", "Â": "A", "Ä": "A",
    "É": "E", "È": "E", "Ê": "E", "Ë": "E",
    "Í": "I", "Ì": "I", "Î": "I", "Ï": "I",
    "Ó": "O", "Ò": "O", "Ô": "O", "Ö": "O",
    "Ú": "U", "Ù": "U", "Û": "U", "Ü": "U",
    "Ý": "Y", "Ÿ": "Y",
})
ACCENT_TOKEN_RE = re.compile(
    r"[A-Za-z" + ACCENT_VOWELS + r"]*(?:[" + ACCENT_VOWELS + r"])[A-Za-z"
    + ACCENT_VOWELS + r"']*"
)
# Optionale Ausnahmeliste: `work/review-allowlist.yaml` darf exakt markierte
# russische Originalzitate vom Kyrillisch-Check ausnehmen. Alles andere bleibt
# release-blockierend.
ORIGINAL_QUOTE_ALLOWLIST_FILE = "review-allowlist.yaml"
SCENE_HEADER_RE = re.compile(r"^##\s+Szene\s+(\d+)\s*$", re.IGNORECASE)
# Modell-Artefakt: die numerische Quell-Ueberschrift der Szene. Sie kommt in
# jeder Heading-Ebene vor ("## 8", "# 8", "### 6").
NUMERIC_HEADER_RE = re.compile(r"^(#{1,4})\s+(\d+)\.?\s*$")
# Kopfbereich fuer die Duplikat-Pruefung: Anzahl nicht-leerer Zeilen nach dem
# Szenenkopf, in denen eine numerische Modell-Ueberschrift stehen darf
# (Auftakt-Blockquote + erste Absaetze).
HEAD_REGION_NON_EMPTY_LINES = 5
SENTENCE_END_RE = re.compile(r"[.!?;:\n]")
# Sprachen ohne zuverlaessige Leerzeichen-Wortgrenzen fuer length_ratio.
CJK_SOURCE_LANGS = {"ja", "zh", "zh-cn", "zh-tw", "ko"}
# Absatz-Raffung: eine Uebersetzung darf Absaetze zusammenziehen, aber nicht
# massenhaft verschwinden lassen. Geprueft wird nur ab genug Quellabsaetzen,
# damit kurze Szenen und Dialogfetzen kein Rauschen erzeugen. Zusaetzlich muss
# die Wortzahl geschrumpft sein: reines Verschmelzen kurzer Absaetze (Dialog)
# laesst die Wortzahl unveraendert und ist kein Raffungssignal (Live-Befund
# Peter 2026-09-17: 5 von 175 Szenen mit Absatzverhaeltnis 0.62-0.81, aber
# Wortverhaeltnis 1.23-1.38 = unauffaellig).
PARAGRAPH_DROP_MIN_SOURCE_PARAS = 20
PARAGRAPH_DROP_WARN_RATIO = 0.85
PARAGRAPH_DROP_ERROR_RATIO = 0.55
PARAGRAPH_DROP_MIN_WORD_RATIO = 0.95
# Laengen-Ausreisser auf Buchebene: der Stil eines Buchs schwankt zwischen
# Szenen nur wenig (Peter der Erste: Median 1.30, Q25/Q75 1.27/1.36). Ein
# fester Korridor erzeugt deshalb entweder Blindflecken oder Fehlalarme;
# gemeldet wird relativ zum Median aller Szenen des Buchs.
LENGTH_OUTLIER_MIN_SCENES = 10
LENGTH_OUTLIER_WARN_FACTOR = 0.72
LENGTH_OUTLIER_ERROR_FACTOR = 0.55
LENGTH_OUTLIER_WARN_FACTOR_HIGH = 1.50
LENGTH_OUTLIER_ERROR_FACTOR_HIGH = 2.00


@dataclass
class Finding:
    severity: str
    category: str
    message: str
    chapter: str
    scene: int | None = None
    evidence: str = ""
    recommendation: str = ""
    source: str = "deterministic"
    current_text: str = ""
    suggested_text: str = ""
    confidence: float | None = None
    fixable: bool | None = None
    position: int | None = None


@dataclass
class SceneReview:
    chapter: str
    scene: int
    ru_path: str
    de_path: str
    ru_words: int
    de_words: int
    findings: list[Finding] = field(default_factory=list)


@dataclass
class ChapterReview:
    chapter: str
    style: str
    ru_scenes: int
    de_scenes: int
    findings: list[Finding] = field(default_factory=list)
    scenes: list[SceneReview] = field(default_factory=list)


@dataclass
class ReviewSummary:
    book_id: str
    title: str
    style: str
    chapters: list[str]
    created_at: str
    llm: str
    counts: dict[str, int]
    chapter_reports: list[str]
    summary_markdown: str
    summary_json: str


def count_words(text: str) -> int:
    return len([part for part in re.split(r"\s+", text.strip()) if part])


def count_paragraphs(text: str) -> int:
    """Nicht-leere Absaetze (durch Leerzeilen getrennt) eines Szenentexts."""
    return len([part for part in re.split(r"\n\s*\n", text.strip()) if part.strip()])


def strip_markdown_controls(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("<!--") and stripped.endswith("-->"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def max_words_without_sentence_end(text: str) -> int:
    longest = 0
    for segment in SENTENCE_END_RE.split(text):
        longest = max(longest, count_words(segment))
    return longest


def repetition_style_findings(
    chapter_id: str,
    scene_num: int,
    de_text: str,
) -> list[Finding]:
    """Stil-Wiederholungen (Kategorie repetition_style), INFO/WARNING, nie ERROR.

    Lazy Import aus lib.repetition (kein Zyklus): Detektor liefert Dicts,
    hier werden sie in Findings gewrappt. Schlaegt der Detektor je fehl,
    bleibt der harte Gate-Check unberuehrt (leise None statt Crash).
    """
    try:
        from lib.repetition import (
            CATEGORY as REPETITION_CATEGORY,
            repetition_scene_findings,
        )
    except Exception:
        return []
    try:
        raw = repetition_scene_findings(chapter_id, scene_num, de_text or "")
    except Exception:
        return []
    out: list[Finding] = []
    for item in raw:
        severity = str(item.get("severity") or "INFO").upper()
        if severity == "ERROR":
            severity = "WARNING"
        if severity not in ("INFO", "WARNING"):
            severity = "INFO"
        out.append(finding(
            severity,
            REPETITION_CATEGORY,
            str(item.get("message") or "Stil-Wiederholung."),
            chapter_id,
            scene_num,
            evidence=str(item.get("evidence") or ""),
            recommendation=str(item.get("recommendation") or ""),
        ))
    return out


def paragraph_drop_finding(
    chapter_id: str,
    scene_num: int,
    source_text: str,
    de_text: str,
    source_lang: str = "ru",
    source_words: int = 0,
    de_words: int = 0,
) -> Finding | None:
    """Verdacht auf Raffung: DE-Szene hat deutlich weniger Absaetze und Woerter.

    Absatzbuendelung allein ist noch kein Fehler - kurze Dialogabsaetze
    duerfen zusammengezogen werden. Gemeldet wird deshalb nur, wenn
    zusaetzlich die Wortzahl unter die der Quelle faellt
    (``PARAGRAPH_DROP_MIN_WORD_RATIO``). Genau diese Kombination trennt
    Raffung von reinem Absatz-Styling.
    """
    source_paras = count_paragraphs(source_text)
    de_paras = count_paragraphs(de_text)
    if source_paras < PARAGRAPH_DROP_MIN_SOURCE_PARAS or de_paras < 1:
        return None
    quotient = de_paras / source_paras
    if quotient >= PARAGRAPH_DROP_WARN_RATIO:
        return None
    if source_words <= 0 or de_words <= 0:
        source_words = count_words(source_text)
        de_words = count_words(de_text)
    word_ratio = (de_words / source_words) if source_words else 1.0
    if word_ratio >= PARAGRAPH_DROP_MIN_WORD_RATIO:
        return None
    severity = "ERROR" if quotient < PARAGRAPH_DROP_ERROR_RATIO else "WARNING"
    label = str(source_lang or "ru").upper()
    return finding(
        severity,
        "paragraph_drop",
        (
            f"DE-Szene hat deutlich weniger Absaetze als die {label}-Quelle "
            f"({de_paras} statt {source_paras}) und weniger Woerter "
            f"({word_ratio:.2f} x)."
        ),
        chapter_id,
        scene_num,
        evidence=(
            f"DE-Absaetze={de_paras}, Quell-Absaetze={source_paras}, "
            f"DE/{label}-Woerter={de_words}/{source_words} ({word_ratio:.2f})"
        ),
        recommendation=(
            "Auf Raffung/Auslassung pruefen; betroffene Szene mit Chunking "
            "neu uebersetzen (translate_chapter.py --chunk-char-limit 7000)."
        ),
    )


def finding(
    severity: str,
    category: str,
    message: str,
    chapter: str,
    scene: int | None = None,
    evidence: str = "",
    recommendation: str = "",
    source: str = "deterministic",
    current_text: str = "",
    suggested_text: str = "",
    confidence: float | None = None,
    fixable: bool | None = None,
    position: int | None = None,
) -> Finding:
    return Finding(
        severity=severity,
        category=category,
        message=message,
        chapter=chapter,
        scene=scene,
        evidence=evidence[:500],
        recommendation=recommendation,
        source=source,
        current_text=current_text,
        suggested_text=suggested_text,
        confidence=confidence,
        fixable=fixable,
        position=position,
    )


def duplicate_heading_lines(text: str) -> list[int]:
    """Zeilenindizes (0-basiert) doppelter Szenen-Ueberschriften.

    Das Modell gibt gelegentlich die numerische Quell-Ueberschrift der Szene
    mit aus. Sie steht nicht zwangslaeufig direkt neben ``## Szene N``:
    bei Stilprofilen mit Auftakt-Blockquote lautet die Reihenfolge
    ``## Szene N`` -> ``> Auftakt`` -> ``## N``. Geprueft wird deshalb der
    Kopfbereich (die ersten ``HEAD_REGION_NON_EMPTY_LINES`` nicht-leeren
    Zeilen nach dem Szenenkopf). Gewertet wird nur eine Ueberschrift, deren
    Nummer zur Szenennummer passt (jede Heading-Ebene). Szenen im Altformat
    ohne ``## Szene N`` haben kein Duplikat und bleiben unberuehrt.
    """
    lines = text.splitlines()
    head = next(
        (match for match in (SCENE_HEADER_RE.match(line.strip()) for line in lines) if match),
        None,
    )
    if head is None:
        return []
    head_idx = lines.index(
        next(line for line in lines if SCENE_HEADER_RE.match(line.strip()))
    )
    scene_number = head.group(1)
    hits: list[int] = []
    checked = 0
    for idx in range(head_idx + 1, len(lines)):
        stripped = lines[idx].strip()
        if not stripped:
            continue
        checked += 1
        if checked > HEAD_REGION_NON_EMPTY_LINES:
            break
        numeric = NUMERIC_HEADER_RE.match(stripped)
        if numeric and numeric.group(2) == scene_number:
            hits.append(idx)
    return hits


def has_double_scene_heading(text: str) -> bool:
    return bool(duplicate_heading_lines(text))


def review_allowlist_path(repo_root: Path, book: dict[str, Any]) -> Path:
    """Optionale Ausnahmeliste fuer ausdruecklich markierte RU-Originalzitate."""
    return book_output_root(repo_root, book) / ORIGINAL_QUOTE_ALLOWLIST_FILE


def load_original_quote_allowlist(
    repo_root: Path,
    book: dict[str, Any],
) -> dict[tuple[str, int], list[str]]:
    """Liest `work/review-allowlist.yaml` -> {(chapter, scene): [exakte Zitate]}.

    Ohne Datei bleibt alles wie bisher: Kyrillisch in DE-Szenen ist ein
    release-blockierender ERROR. Nur exakt hier hinterlegte Zitate werden vor
    dem Zeichen-Check entfernt.
    """
    path = review_allowlist_path(repo_root, book)
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        print(f"WARNUNG: {path} ist ungueltig ({exc}); Ausnahmen werden ignoriert.")
        return {}
    entries = data.get("original_quotes")
    if not isinstance(entries, list):
        return {}
    allowlist: dict[tuple[str, int], list[str]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        text = str(entry.get("text") or "").strip()
        if not text:
            continue
        try:
            scene = int(entry.get("scene"))
        except (TypeError, ValueError):
            continue
        chapter = str(entry.get("chapter") or "").strip()
        if not chapter:
            continue
        allowlist.setdefault((chapter, scene), []).append(text)
    return allowlist


def strip_allowed_original_quotes(
    text: str,
    allowed_quotes: list[str] | None,
) -> str:
    if not allowed_quotes:
        return text
    for snippet in allowed_quotes:
        if snippet and snippet in text:
            text = text.replace(snippet, " ")
    return text


def deterministic_scene_findings(
    chapter_id: str,
    scene_num: int,
    ru_text: str,
    de_text: str,
    ru_words: int,
    de_words: int,
    source_lang: str = "ru",
    allowed_quotes: list[str] | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    clean_de = strip_markdown_controls(de_text)
    clean_de = strip_allowed_original_quotes(clean_de, allowed_quotes)
    source_label = str(source_lang or "ru").upper()
    if not clean_de or len(clean_de) < 50 or de_words < 10:
        findings.append(finding(
            "ERROR",
            "empty_or_short",
            "DE-Szene ist leer oder auffaellig kurz.",
            chapter_id,
            scene_num,
            evidence=clean_de[:160],
            recommendation="Szene neu erzeugen oder manuell pruefen.",
        ))
    cyrillic = CYRILLIC_RE.findall(clean_de)
    if cyrillic:
        snippet_match = CYRILLIC_RE.search(clean_de)
        start = max(0, (snippet_match.start() if snippet_match else 0) - 80)
        end = min(len(clean_de), start + 220)
        current_char = snippet_match.group(0) if snippet_match else ""
        findings.append(finding(
            "ERROR",
            "cyrillic_in_translation",
            "DE-Szene enthaelt kyrillische Zeichen.",
            chapter_id,
            scene_num,
            evidence=clean_de[start:end],
            recommendation="Pruefen, ob Originaltext stehen geblieben ist.",
            current_text=current_char,
            confidence=0.80,
            fixable=None,
            position=snippet_match.start() if snippet_match else None,
        ))
    if REPLACEMENT_RE.search(clean_de):
        findings.append(finding(
            "ERROR",
            "encoding_garbage",
            "DE-Szene enthaelt Replacement- oder Steuerzeichen.",
            chapter_id,
            scene_num,
            recommendation="Datei/Generierung auf Encoding-Schaden pruefen.",
        ))
    lang = str(source_lang or "ru").lower()
    if lang not in CJK_SOURCE_LANGS and ru_words >= 80 and de_words:
        ratio = de_words / ru_words
        if ratio < 0.55 or ratio > 2.60:
            findings.append(finding(
                "ERROR",
                "length_ratio",
                f"DE/{source_label}-Wortverhaeltnis ist stark auffaellig ({ratio:.2f}).",
                chapter_id,
                scene_num,
                evidence=f"{source_label}={ru_words}, DE={de_words}",
                recommendation="Auf Auslassung, Doppelung oder Ausschweifung pruefen.",
            ))
        elif ratio < 0.75 or ratio > 2.10:
            findings.append(finding(
                "WARNING",
                "length_ratio",
                f"DE/{source_label}-Wortverhaeltnis ist auffaellig ({ratio:.2f}).",
                chapter_id,
                scene_num,
                evidence=f"{source_label}={ru_words}, DE={de_words}",
                recommendation="Stichprobenartig gegenlesen.",
            ))
    paragraph_finding = paragraph_drop_finding(
        chapter_id,
        scene_num,
        ru_text,
        de_text,
        source_lang=source_lang,
        source_words=ru_words,
        de_words=de_words,
    )
    if paragraph_finding is not None:
        findings.append(paragraph_finding)
    if has_double_scene_heading(clean_de):
        findings.append(finding(
            "WARNING",
            "duplicate_heading",
            "DE-Szene enthaelt doppelte Szenenueberschriften.",
            chapter_id,
            scene_num,
            recommendation="Vor Export bereinigen oder Export-Cleaner pruefen.",
        ))
    long_sentence = max_words_without_sentence_end(clean_de)
    if long_sentence > 300:
        findings.append(finding(
            "ERROR",
            "long_sentence",
            f"Sehr langer Satz/Abschnitt ohne Satzende ({long_sentence} Woerter).",
            chapter_id,
            scene_num,
            recommendation="Auf Degeneration oder fehlende Interpunktion pruefen.",
        ))
    elif long_sentence > 180:
        findings.append(finding(
            "WARNING",
            "long_sentence",
            f"Langer Satz/Abschnitt ohne Satzende ({long_sentence} Woerter).",
            chapter_id,
            scene_num,
            recommendation="Lesbarkeit pruefen.",
        ))
    degeneration = detect_degeneration(clean_de, expected_language="deutsch")
    if not degeneration.get("ok", True):
        findings.append(finding(
            "ERROR",
            "degeneration",
            str(degeneration.get("reason") or "Degeneration erkannt."),
            chapter_id,
            scene_num,
            recommendation="Szene neu erzeugen oder manuell ueberarbeiten.",
        ))
    mojibake_match = MOJIBAKE_RE.search(clean_de)
    if mojibake_match:
        start = max(0, mojibake_match.start() - 100)
        evidence = clean_de[start:mojibake_match.start() + 100].replace("\n", " ")
        findings.append(finding(
            "ERROR",
            "mojibake",
            "DE-Szene enthaelt Mojibake (kaputtes Encoding, z. B. Ã/Ð/Ñ).",
            chapter_id,
            scene_num,
            evidence=f"…{evidence}…",
            recommendation="Datei-Encoding pruefen (UTF-8), ggf. neu schreiben.",
        ))
    findings.extend(repetition_style_findings(chapter_id, scene_num, de_text))
    return findings


def review_chapter_deterministic(
    repo_root: Path,
    book: dict[str, Any],
    chapter_id: str,
    style: str,
) -> ChapterReview:
    output_root = book_output_root(repo_root, book)
    source_lang = str(book.get("source_lang") or "ru")
    ru_paths = list_source_scene_paths(output_root, chapter_id, source_lang)
    ru_by_num = {
        num: path
        for path in ru_paths
        if (num := parse_scene_number(path, chapter_id)) is not None
    }
    de_by_num = find_scene_translations(output_root, chapter_id, style)
    allowlist = load_original_quote_allowlist(repo_root, book)
    targets = glossary_targets(repo_root, book)
    review = ChapterReview(
        chapter=chapter_id,
        style=style,
        ru_scenes=len(ru_by_num),
        de_scenes=len(de_by_num),
    )
    if not ru_by_num:
        review.findings.append(finding(
            "ERROR",
            "missing_ru_scenes",
            "Keine RU-Szenen fuer dieses Kapitel gefunden.",
            chapter_id,
            recommendation="extract_scenes.py fuer das Kapitel ausfuehren.",
        ))
        return review
    missing_de = sorted(set(ru_by_num) - set(de_by_num))
    extra_de = sorted(set(de_by_num) - set(ru_by_num))
    for scene_num in missing_de:
        review.findings.append(finding(
            "ERROR",
            "missing_de_scene",
            f"DE-Szene {scene_num:02d} fehlt.",
            chapter_id,
            scene_num,
            evidence=str(ru_by_num[scene_num]),
            recommendation="Szene uebersetzen oder Zielstil pruefen.",
        ))
    for scene_num in extra_de:
        review.findings.append(finding(
            "WARNING",
            "extra_de_scene",
            f"DE-Szene {scene_num:02d} hat keine passende RU-Szene.",
            chapter_id,
            scene_num,
            evidence=str(de_by_num[scene_num]),
            recommendation="Alte oder falsche Szenendatei pruefen.",
        ))
    for scene_num in sorted(set(ru_by_num) & set(de_by_num)):
        ru_path = ru_by_num[scene_num]
        de_path = de_by_num[scene_num]
        ru_text = ru_path.read_text(encoding="utf-8", errors="replace")
        de_text = de_path.read_text(encoding="utf-8", errors="replace")
        from lib.editorial_appendices import review_appendix_text

        appendix = review_appendix_text(repo_root, book, style, chapter_id, scene_num)
        if appendix:
            # Ausgelagerte editorische Uebersetzungen zaehlen zum Szenentext:
            # Ohne Anrechnung faelscht der Wegzug in den Anhang eine Raffung.
            de_text += "\n\n" + appendix
        ru_words = count_words(ru_text)
        de_words = count_words(de_text)
        scene_review = SceneReview(
            chapter=chapter_id,
            scene=scene_num,
            ru_path=str(ru_path.relative_to(repo_root)),
            de_path=str(de_path.relative_to(repo_root)),
            ru_words=ru_words,
            de_words=de_words,
        )
        scene_review.findings.extend(
            deterministic_scene_findings(
                chapter_id,
                scene_num,
                ru_text,
                de_text,
                ru_words,
                de_words,
                source_lang=source_lang,
                allowed_quotes=allowlist.get((chapter_id, scene_num), []),
            )
        )
        scene_review.findings.extend(
            accented_transliteration_findings(
                chapter_id,
                scene_num,
                de_text,
                targets,
            )
        )
        review.scenes.append(scene_review)
    return review


def glossary_targets(repo_root: Path, book: dict[str, Any]) -> set[str]:
    """Verbindliche Zielformen aus names.yaml (target + aliases)."""
    names_file = str(book.get("names_file") or "").strip()
    if not names_file:
        return set()
    entries = load_names(repo_root / names_file)
    targets: set[str] = set()
    for entry in entries:
        values = [entry.get("target")]
        aliases = entry.get("aliases") or []
        if isinstance(aliases, str):
            aliases = [aliases]
        values.extend(aliases)
        for value in values:
            text = str(value or "").strip()
            if text:
                targets.add(text)
    return targets


def accented_transliteration_findings(
    chapter_id: str,
    scene_num: int,
    de_text: str,
    targets: set[str],
) -> list[Finding]:
    """Akzentuierte Variante einer Glossarform -> release-blockierender ERROR.

    Deterministisch und praezise: geflaggt wird nur, wenn die akzentfreie Form
    im Buchglossar steht und die akzentuierte Form dort nicht. Legitime
    Akzente ohne Glossareintrag (Molière, Báthory, Shèngwǔ) bleiben unberuehrt.
    """
    if not targets:
        return []
    findings: list[Finding] = []
    seen: set[str] = set()
    for match in ACCENT_TOKEN_RE.finditer(strip_markdown_controls(de_text)):
        token = match.group(0)
        plain = token.translate(ACCENT_STRIP_MAP)
        if plain == token or token in seen:
            continue
        if token in targets or plain not in targets:
            continue
        seen.add(token)
        findings.append(finding(
            "ERROR",
            "accented_transliteration",
            f"Name '{token}' traegt ein Transliterations-Akzentzeichen.",
            chapter_id,
            scene_num,
            evidence=token,
            recommendation=(
                f"Ersetze '{token}' durch die Glossarform '{plain}' "
                "(Akzentzeichen aus der Betonung entfernen)."
            ),
            current_text=token,
            suggested_text=plain,
            fixable=True,
        ))
    return findings


def extract_json_object(text: str) -> dict[str, Any]:
    if not text.strip():
        raise ValueError("KI-Antwort war leer; erwartet wurde JSON.")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        candidate = text[start:end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
        # Repair common Ollama JSON errors: unescaped quotes inside strings
        repaired = _repair_json(candidate)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass
    preview = text.replace("\n", " ")[:220]
    raise ValueError(
        "KI-Antwort enthielt kein gueltiges JSON-Objekt. "
        f"Antwortbeginn: {preview!r}"
    )


def _repair_json(text: str) -> str:
    """Simple repair for common Ollama JSON output errors.
    
    Handles unescaped double quotes and control characters inside string values
    by replacing them with their escaped equivalents.
    """
    # Remove control characters except \n, \r, \t
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    # Fix unescaped backslashes followed by non-escape chars
    text = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', text)
    return text


def optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def optional_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "ja", "1"}:
            return True
        if lowered in {"false", "no", "nein", "0"}:
            return False
    return None


def load_book_name_lines(repo_root: Path, book: dict[str, Any], limit: int = 120) -> list[str]:
    names_file = str(book.get("names_file") or "").strip()
    if not names_file:
        return []
    path = Path(names_file)
    if not path.is_absolute():
        path = repo_root / path
    if not path.exists():
        return []
    return compact_name_lines(load_names(path), limit=limit)


def canonical_name_targets(repo_root: Path, book: dict[str, Any]) -> set[str]:
    names_file = str(book.get("names_file") or "").strip()
    if not names_file:
        return set()
    path = Path(names_file)
    if not path.is_absolute():
        path = repo_root / path
    if not path.exists():
        return set()
    targets: set[str] = set()
    for entry in load_names(path):
        target = str(entry.get("target") or "").strip()
        if target:
            targets.add(target)
    return targets


def normalize_llm_finding_fields(
    item: dict[str, Any],
    canonical_targets: set[str],
) -> dict[str, Any] | None:
    """Normalisiert KI-Befunde; verwirft Namenskritik gegen die Namensliste."""
    category = str(item.get("category") or "llm").strip().lower()
    current_text = str(item.get("current_text") or "").strip()
    suggested_text = str(item.get("suggested_text") or "").strip()
    recommendation = str(item.get("recommendation") or "").strip()
    summary = str(item.get("summary") or "KI-Hinweis").strip()

    if category == "names" and canonical_targets and current_text:
        for target in canonical_targets:
            if target and target in current_text:
                # Modell will eine verbindliche Target-Form ersetzen -> ignorieren.
                if suggested_text and target not in suggested_text:
                    return None
                if not suggested_text and any(
                    token in summary.lower() or token in recommendation.lower()
                    for token in ("falsch", "inkorrekt", "nicht korrekt", "erfindung")
                ):
                    return None

    fixable = optional_bool(item.get("fixable"))
    if fixable is True and (not current_text or not suggested_text or current_text == suggested_text):
        fixable = False
        if not recommendation:
            recommendation = (
                "Kein eindeutiger Textersatz; manuell pruefen oder "
                "current_text/suggested_text nachliefern."
            )

    return {
        "severity": str(item.get("severity") or "INFO").upper(),
        "category": category or "llm",
        "summary": summary,
        "evidence": str(item.get("evidence") or ""),
        "recommendation": recommendation,
        "current_text": current_text,
        "suggested_text": suggested_text,
        "confidence": optional_float(item.get("confidence")),
        "fixable": fixable,
    }


def add_llm_findings(
    repo_root: Path,
    book: dict[str, Any],
    style: str,
    review: ChapterReview,
    chat: Callable[[str, str], str],
    scope: str,
    progress: Callable[[SceneReview], None] | None = None,
) -> None:
    name_targets = canonical_name_targets(repo_root, book)
    for scene in review.scenes:
        has_flags = bool(scene.findings)
        if scope != "all" and not has_flags:
            continue
        system, user = build_llm_prompt_for_paths(repo_root, book, style, scene)
        raw = ""
        try:
            if progress is not None:
                progress(scene)
            raw = chat(system, user)
            data = extract_json_object(raw)
            if "findings" not in data:
                raise ValueError("KI-JSON enthaelt kein Feld 'findings'.")
            items = data.get("findings") or []
            if not isinstance(items, list):
                raise ValueError("'findings' ist keine Liste")
        except Exception as exc:
            print(
                f"  [LLM-Review FAIL] Kapitel {scene.chapter}, Szene {scene.scene:02d}: {exc}",
                file=sys.stderr,
                flush=True,
            )
            recommendation = (
                "Backend/Modell pruefen, Ollama-Modell wechseln oder "
                "Lauf ohne KI-Review wiederholen."
            )
            message = f"KI-Review fehlgeschlagen: {exc}"
            if "finish_reason=length" in str(exc) or "abgeschnitten" in str(exc).lower():
                recommendation = (
                    "Antwort wurde abgeschnitten: max_tokens erhoehen "
                    "(Review-Default jetzt 8000) oder kuerzeres Modell ohne langes Thinking waehlen."
                )
            scene.findings.append(finding(
                "WARNING",
                "llm_review_failed",
                message,
                scene.chapter,
                scene.scene,
                evidence=raw[:500],
                recommendation=recommendation,
                source="llm",
            ))
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            normalized = normalize_llm_finding_fields(item, name_targets)
            if normalized is None:
                continue
            severity = normalized["severity"]
            if severity not in SEVERITY_ORDER:
                severity = "INFO"
            scene.findings.append(finding(
                severity,
                normalized["category"],
                normalized["summary"],
                scene.chapter,
                scene.scene,
                evidence=normalized["evidence"],
                recommendation=normalized["recommendation"],
                source="llm",
                current_text=normalized["current_text"],
                suggested_text=normalized["suggested_text"],
                confidence=normalized["confidence"],
                fixable=normalized["fixable"],
            ))


def build_llm_prompt_for_paths(
    repo_root: Path,
    book: dict[str, Any],
    style: str,
    scene: SceneReview,
) -> tuple[str, str]:
    source_lang = str(book.get("source_lang") or "ru").upper()
    source_text = (repo_root / scene.ru_path).read_text(encoding="utf-8", errors="replace")
    de_text = (repo_root / scene.de_path).read_text(encoding="utf-8", errors="replace")
    name_lines = load_book_name_lines(repo_root, book)
    names_block = ""
    if name_lines:
        names_block = (
            "\nVerbindliche Namens-/Begriffsliste des Buchpakets "
            "(Target-Formen sind KANONISCH; wenn DE sie nutzt, ist das KEIN Fehler "
            "und keine alternative Transkription vorschlagen):\n"
            + "\n".join(name_lines)
            + "\n"
        )
    system = (
        "Du bist ein strenger literarischer Schlussredakteur fuer eine "
        "literarische Uebersetzung ins Deutsche. Antworte ausschliesslich als "
        "gueltiges JSON ohne Markdown, Kommentar, Reasoning oder Einleitung. "
        "Kein Fliesstext ausserhalb des JSON-Objekts."
    )
    user = (
        f"Pruefe Original ({source_lang}) und DE-Uebersetzung. Melde nur konkrete, "
        "belegbare Probleme, die eine klare Handlung erlauben. "
        "Lieber wenige praezise Befunde als viele vage Hinweise.\n\n"
        "ERROR nur fuer release-blockierende Probleme: Sinnverlust, fehlende Passage, "
        "stehengebliebenes Original, kaputte Formatierung, klar falsche Eigennamen "
        "gegenueber Original UND gegenueber der Namensliste.\n"
        "WARNING fuer kleinere editorische Hinweise mit konkretem Ersatz.\n\n"
        "Wenn ein Befund auto-korrigierbar sein soll: setze fixable=true UND liefere "
        "current_text als exakten Teilstring aus dem DE-Text sowie suggested_text als "
        "exakten Ersatz. Ohne beide Felder setze fixable=false.\n"
        "Keine Namenskritik, die nur eine andere wissenschaftliche Transkription bevorzugt, "
        "wenn die DE-Form in der Namensliste steht.\n\n"
        "Wenn du keine konkreten Befunde hast, antworte exakt mit: "
        "{\"findings\":[]}\n\n"
        "Antwort exakt als JSON:\n"
        "{\"findings\":[{\"severity\":\"ERROR|WARNING|INFO\","
        "\"category\":\"meaning|omission|addition|names|register|grammar|formatting\","
        "\"summary\":\"kurz und handlungsorientiert\","
        "\"evidence\":\"kurze Belegstelle aus Original und/oder DE\","
        "\"recommendation\":\"konkrete naechste Handlung\","
        "\"fixable\":true|false,"
        "\"current_text\":\"exakt vorhandener DE-Text oder leer\","
        "\"suggested_text\":\"exakter Ersatz oder leer\","
        "\"confidence\":0.0}]}\n\n"
        f"Buch: {book.get('title')} / {book.get('author')}\n"
        f"Style: {style}\n"
        f"Kapitel: {scene.chapter}, Szene: {scene.scene:02d}\n"
        f"{names_block}\n"
        f"Original {source_lang}:\n"
        f"{source_text}\n\n"
        "Uebersetzung DE:\n"
        f"{de_text}\n"
    )
    return system, user


def chapter_findings(review: ChapterReview) -> list[Finding]:
    out = list(review.findings)
    for scene in review.scenes:
        out.extend(scene.findings)
    return out


def count_findings(chapter_reviews: list[ChapterReview]) -> dict[str, int]:
    counts = {"ERROR": 0, "WARNING": 0, "INFO": 0}
    for review in chapter_reviews:
        for item in chapter_findings(review):
            counts[item.severity] = counts.get(item.severity, 0) + 1
    return counts


def apply_length_outliers(
    chapter_reviews: list[ChapterReview],
    source_lang: str = "ru",
) -> int:
    """Meldet Szenen, deren DE/Quelle-Wortverhaeltnis weit vom Buch-Median abweicht.

    Der feste Korridor in ``deterministic_scene_findings`` schuetzt nur vor
    Extremfaellen. Szenen mit 60-90 Prozent des Buch-Medians (gerafft, aber
    nicht kurz genug fuer den Korridor) blieben ungemeldet. Diese buchweite
    Auswertung laeuft nach dem Sammeln aller Kapitel und haengt ihre Befunde
    an die jeweilige Szene. Gibt die Zahl der gemeldeten Szenen zurueck.
    """
    if str(source_lang or "ru").lower() in CJK_SOURCE_LANGS:
        return 0
    label = str(source_lang or "ru").upper()
    ratios = [
        scene.de_words / scene.ru_words
        for review in chapter_reviews
        for scene in review.scenes
        if scene.ru_words >= 80 and scene.de_words
    ]
    if len(ratios) < LENGTH_OUTLIER_MIN_SCENES:
        return 0
    median = statistics.median(ratios)
    if median <= 0:
        return 0
    added = 0
    for review in chapter_reviews:
        for scene in review.scenes:
            if scene.ru_words < 80 or not scene.de_words:
                continue
            ratio = scene.de_words / scene.ru_words
            if (
                ratio < median * LENGTH_OUTLIER_ERROR_FACTOR
                or ratio > median * LENGTH_OUTLIER_ERROR_FACTOR_HIGH
            ):
                severity = "ERROR"
            elif (
                ratio < median * LENGTH_OUTLIER_WARN_FACTOR
                or ratio > median * LENGTH_OUTLIER_WARN_FACTOR_HIGH
            ):
                severity = "WARNING"
            else:
                continue
            scene.findings.append(finding(
                severity,
                "length_outlier",
                f"DE/{label}-Wortverhaeltnis {ratio:.2f} weicht stark vom Buch-Median {median:.2f} ab.",
                review.chapter,
                scene.scene,
                evidence=f"{label}={scene.ru_words}, DE={scene.de_words}, Buch-Median={median:.2f}",
                recommendation=(
                    "Auf Raffung pruefen; betroffene Szene mit Chunking "
                    "neu uebersetzen (translate_chapter.py --chunk-char-limit 7000)."
                ),
            ))
            added += 1
    return added


def review_to_dict(review: ChapterReview) -> dict[str, Any]:
    return asdict(review)


def render_chapter_markdown(book: dict[str, Any], review: ChapterReview) -> str:
    findings = chapter_findings(review)
    counts = {"ERROR": 0, "WARNING": 0, "INFO": 0}
    for item in findings:
        counts[item.severity] = counts.get(item.severity, 0) + 1
    lines = [
        f"# Review Kapitel {review.chapter}",
        "",
        f"- Buch: {book.get('title')} ({book.get('id')})",
        f"- Stil: {review.style}",
        f"- RU-Szenen: {review.ru_scenes}",
        f"- DE-Szenen: {review.de_scenes}",
        f"- Fehler: {counts.get('ERROR', 0)}",
        f"- Warnungen: {counts.get('WARNING', 0)}",
        f"- Hinweise: {counts.get('INFO', 0)}",
        "",
    ]
    if not findings:
        lines.append("Keine Befunde.")
        lines.append("")
        return "\n".join(lines)
    lines.append("## Befunde")
    lines.append("")
    for item in sorted(findings, key=lambda f: -SEVERITY_ORDER.get(f.severity, 0)):
        scene = f", Szene {item.scene:02d}" if item.scene is not None else ""
        lines.append(f"### {item.severity}: {item.category} ({item.chapter}{scene})")
        lines.append("")
        lines.append(item.message)
        if item.evidence:
            lines.append("")
            lines.append(f"> {item.evidence.replace(chr(10), ' ')[:500]}")
        if item.recommendation:
            lines.append("")
            lines.append(f"Empfehlung: {item.recommendation}")
        lines.append("")
    return "\n".join(lines)


def write_reports(
    repo_root: Path,
    book: dict[str, Any],
    style: str,
    reviews: list[ChapterReview],
    llm: str,
) -> ReviewSummary:
    output_root = book_output_root(repo_root, book)
    root = output_root / "reviews" / style
    chapters_dir = root / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)
    chapter_report_paths: list[str] = []
    for review in reviews:
        findings = chapter_findings(review)
        json_path = chapters_dir / f"{review.chapter}-review.json"
        md_path = chapters_dir / f"{review.chapter}-review.md"
        if not findings:
            json_path.unlink(missing_ok=True)
            md_path.unlink(missing_ok=True)
            continue
        json_path.write_text(
            json.dumps(review_to_dict(review), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        md_path.write_text(render_chapter_markdown(book, review), encoding="utf-8")
        chapter_report_paths.append(str(md_path.relative_to(repo_root)))
    counts = count_findings(reviews)
    summary_md = root / "review-summary.md"
    summary_json = root / "review-summary.json"
    summary = ReviewSummary(
        book_id=str(book.get("id")),
        title=str(book.get("title")),
        style=style,
        chapters=[r.chapter for r in reviews],
        created_at=datetime.now().isoformat(timespec="seconds"),
        llm=llm,
        counts=counts,
        chapter_reports=chapter_report_paths,
        summary_markdown=str(summary_md.relative_to(repo_root)),
        summary_json=str(summary_json.relative_to(repo_root)),
    )
    summary_json.write_text(
        json.dumps(asdict(summary), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    summary_md.write_text(render_summary_markdown(summary, reviews), encoding="utf-8")
    return summary


def render_summary_markdown(summary: ReviewSummary, reviews: list[ChapterReview]) -> str:
    lines = [
        f"# Review Summary: {summary.title}",
        "",
        f"- Buch-ID: {summary.book_id}",
        f"- Stil: {summary.style}",
        f"- Erstellt: {summary.created_at}",
        f"- LLM: {summary.llm}",
        f"- Kapitel: {len(summary.chapters)}",
        f"- Kapitel mit Befunden: {len(summary.chapter_reports)}",
        f"- Fehler: {summary.counts.get('ERROR', 0)}",
        f"- Warnungen: {summary.counts.get('WARNING', 0)}",
        f"- Hinweise: {summary.counts.get('INFO', 0)}",
        "",
        "## Kapitel",
        "",
    ]
    for review in reviews:
        counts = {"ERROR": 0, "WARNING": 0, "INFO": 0}
        for item in chapter_findings(review):
            counts[item.severity] = counts.get(item.severity, 0) + 1
        status = "Befund" if sum(counts.values()) else "OK"
        lines.append(
            f"- {review.chapter}: {status} "
            f"(ERROR={counts.get('ERROR', 0)}, "
            f"WARNING={counts.get('WARNING', 0)}, INFO={counts.get('INFO', 0)})"
        )
    total_errors = summary.counts.get("ERROR", 0)
    total_warnings = summary.counts.get("WARNING", 0)
    total_infos = summary.counts.get("INFO", 0)
    if total_errors == 0 and total_warnings == 0 and total_infos == 0:
        lines.extend([
            "",
            "Alle geprueften Kapitel sind regelbasiert unauffaellig — "
            "keine kyrillischen Reste, keine Encoding-Fehler, "
            "keine auffaelligen Laengen, keine Degeneration.",
        ])
    errors = [
        item
        for review in reviews
        for item in chapter_findings(review)
        if item.severity == "ERROR"
    ]
    if errors:
        lines.extend(["", "## Release-blockierende Fehler", ""])
        for item in errors:
            scene = f", Szene {item.scene:02d}" if item.scene is not None else ""
            lines.append(f"- {item.chapter}{scene}: {item.category} - {item.message}")
    return "\n".join(lines) + "\n"
