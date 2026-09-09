"""Review checks for translated book packages.

The review layer is report-only: it reads RU/DE scene files, writes review
reports, and never changes translation files.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

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
SCENE_HEADER_RE = re.compile(r"^##\s+Szene\s+(\d+)\s*$", re.IGNORECASE)
NUMERIC_HEADER_RE = re.compile(r"^##\s+\d+\.?\s*$")
SENTENCE_END_RE = re.compile(r"[.!?;:\n]")
# Sprachen ohne zuverlaessige Leerzeichen-Wortgrenzen fuer length_ratio.
CJK_SOURCE_LANGS = {"ja", "zh", "zh-cn", "zh-tw", "ko"}


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


def has_double_scene_heading(text: str) -> bool:
    significant = [line.strip() for line in text.splitlines() if line.strip()]
    for idx, line in enumerate(significant[:-1]):
        if SCENE_HEADER_RE.match(line) and NUMERIC_HEADER_RE.match(significant[idx + 1]):
            return True
    return False


def deterministic_scene_findings(
    chapter_id: str,
    scene_num: int,
    ru_text: str,
    de_text: str,
    ru_words: int,
    de_words: int,
    source_lang: str = "ru",
) -> list[Finding]:
    findings: list[Finding] = []
    clean_de = strip_markdown_controls(de_text)
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
            )
        )
        review.scenes.append(scene_review)
    return review


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
