"""Review checks for translated book packages.

The review layer is report-only: it reads RU/DE scene files, writes review
reports, and never changes translation files.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from lib.degeneration import detect_degeneration
from lib.output_paths import (
    book_output_root,
    find_scene_translations,
    list_ru_scene_paths,
    parse_scene_number,
)


SEVERITY_ORDER = {"INFO": 0, "WARNING": 1, "ERROR": 2}
CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
REPLACEMENT_RE = re.compile(r"[\uFFFD\u0000-\u0008\u000B-\u001F]")
SCENE_HEADER_RE = re.compile(r"^##\s+Szene\s+(\d+)\s*$", re.IGNORECASE)
NUMERIC_HEADER_RE = re.compile(r"^##\s+\d+\.?\s*$")
SENTENCE_END_RE = re.compile(r"[.!?;:\n]")


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
) -> list[Finding]:
    findings: list[Finding] = []
    clean_de = strip_markdown_controls(de_text)
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
    if ru_words >= 80 and de_words:
        ratio = de_words / ru_words
        if ratio < 0.55 or ratio > 2.60:
            findings.append(finding(
                "ERROR",
                "length_ratio",
                f"DE/RU-Wortverhaeltnis ist stark auffaellig ({ratio:.2f}).",
                chapter_id,
                scene_num,
                evidence=f"RU={ru_words}, DE={de_words}",
                recommendation="Auf Auslassung, Doppelung oder Ausschweifung pruefen.",
            ))
        elif ratio < 0.75 or ratio > 2.10:
            findings.append(finding(
                "WARNING",
                "length_ratio",
                f"DE/RU-Wortverhaeltnis ist auffaellig ({ratio:.2f}).",
                chapter_id,
                scene_num,
                evidence=f"RU={ru_words}, DE={de_words}",
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
    ru_paths = list_ru_scene_paths(output_root, chapter_id)
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
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start:end + 1])
        preview = text.replace("\n", " ")[:220]
        raise ValueError(
            "KI-Antwort enthielt kein JSON-Objekt. "
            f"Antwortbeginn: {preview!r}"
        )


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


def add_llm_findings(
    repo_root: Path,
    book: dict[str, Any],
    style: str,
    review: ChapterReview,
    chat: Callable[[str, str], str],
    scope: str,
    progress: Callable[[SceneReview], None] | None = None,
) -> None:
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
            items = data.get("findings") or []
            if not isinstance(items, list):
                raise ValueError("'findings' ist keine Liste")
        except Exception as exc:
            scene.findings.append(finding(
                "WARNING",
                "llm_review_failed",
                f"KI-Review fehlgeschlagen: {exc}",
                scene.chapter,
                scene.scene,
                evidence=raw[:500],
                recommendation=(
                    "Backend/Modell pruefen, Ollama-Modell wechseln oder "
                    "Lauf ohne KI-Review wiederholen."
                ),
                source="llm",
            ))
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            severity = str(item.get("severity") or "INFO").upper()
            if severity not in SEVERITY_ORDER:
                severity = "INFO"
            scene.findings.append(finding(
                severity,
                str(item.get("category") or "llm"),
                str(item.get("summary") or "KI-Hinweis"),
                scene.chapter,
                scene.scene,
                evidence=str(item.get("evidence") or ""),
                recommendation=str(item.get("recommendation") or ""),
                source="llm",
                current_text=str(item.get("current_text") or ""),
                suggested_text=str(item.get("suggested_text") or ""),
                confidence=optional_float(item.get("confidence")),
                fixable=optional_bool(item.get("fixable")),
            ))


def build_llm_prompt_for_paths(
    repo_root: Path,
    book: dict[str, Any],
    style: str,
    scene: SceneReview,
) -> tuple[str, str]:
    ru_text = (repo_root / scene.ru_path).read_text(encoding="utf-8", errors="replace")
    de_text = (repo_root / scene.de_path).read_text(encoding="utf-8", errors="replace")
    system = (
        "Du bist ein strenger literarischer Schlussredakteur fuer eine "
        "russisch-deutsche Romanuebersetzung. Antworte ausschliesslich als JSON."
    )
    user = (
        "Pruefe RU-Original und DE-Uebersetzung. Melde nur konkrete, belegbare "
        "Probleme. Nutze ERROR nur fuer release-blockierende Probleme wie "
        "Sinnverlust, fehlende Passage, falsche Namen, stehengebliebenes "
        "Russisch oder kaputte Formatierung. Nutze WARNING fuer stilistische "
        "oder kleinere editorische Hinweise.\n\n"
        "Antwort exakt als JSON:\n"
        "{\"findings\":[{\"severity\":\"ERROR|WARNING|INFO\","
        "\"category\":\"meaning|omission|addition|names|register|grammar|formatting\","
        "\"summary\":\"...\",\"evidence\":\"...\",\"recommendation\":\"...\","
        "\"fixable\":true|false,\"current_text\":\"exakt vorhandener DE-Text oder leer\","
        "\"suggested_text\":\"exakter Ersatz oder leer\",\"confidence\":0.0}]}\n\n"
        f"Buch: {book.get('title')} / {book.get('author')}\n"
        f"Style: {style}\n"
        f"Kapitel: {scene.chapter}, Szene: {scene.scene:02d}\n\n"
        "Original RU:\n"
        f"{ru_text}\n\n"
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
