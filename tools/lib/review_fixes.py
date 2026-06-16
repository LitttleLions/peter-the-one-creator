"""Staged fixes for review findings.

This module never writes productive scene files during planning or staging.
Only ``promote_staged_fixes`` copies staged candidates back into
``work/scenes/de/...`` after hash and deterministic review checks.
"""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

from lib.output_paths import book_output_root
from lib.review_checks import count_words, deterministic_scene_findings


FIX_VERSION = 1

CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
MIXED_TOKEN_RE = re.compile(r"[A-Za-zÀ-ɏ\u0400-\u04FF]+")
TRANSLATION_QUOTE_RE = re.compile(
    r"(?:Uebersetzung|Übersetzung)\s*:\s*[«\"']([^»\"']+)[»\"']"
)
RECOMMENDATION_QUOTE_RE = re.compile(
    r"(?:Verwende|Ersetze|Nutze)[^«\"']*[«\"']([^»\"']+)[»\"']",
    re.IGNORECASE,
)

HOMOGLYPH_MAP = {
    "А": "A",
    "В": "B",
    "Е": "E",
    "К": "K",
    "М": "M",
    "Н": "H",
    "О": "O",
    "Р": "P",
    "С": "C",
    "Т": "T",
    "Х": "X",
    "а": "a",
    "е": "e",
    "о": "o",
    "р": "p",
    "с": "c",
    "у": "y",
    "х": "x",
    "И": "I",
    "Н": "N",
    "и": "i",
    "н": "n",
}


@dataclass
class Replacement:
    current_text: str
    suggested_text: str
    source: str
    confidence: float = 0.75


@dataclass
class ManualFinding:
    chapter: str
    scene: int
    category: str
    message: str
    reason: str
    recommendation: str = ""


@dataclass
class AppliedFix:
    chapter: str
    scene: int
    category: str
    source: str
    current_text: str
    suggested_text: str


@dataclass
class StagedScene:
    chapter: str
    scene: int
    source_path: str
    ru_path: str
    candidate_path: str
    original_sha256: str
    candidate_sha256: str
    applied: list[AppliedFix] = field(default_factory=list)
    manual: list[ManualFinding] = field(default_factory=list)


@dataclass
class FixManifest:
    version: int
    book_id: str
    style: str
    created_at: str
    source_review_summary: str
    staged: list[StagedScene]


@dataclass
class PromotionItem:
    chapter: str
    scene: int
    source_path: str
    candidate_path: str
    status: str
    message: str
    backup_path: str = ""


@dataclass
class PromotionReport:
    book_id: str
    style: str
    created_at: str
    promoted: int
    skipped: int
    assembled_chapters: list[str]
    items: list[PromotionItem]


def sha256_text(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def repo_path(repo_root: Path, raw: str) -> Path:
    path = Path(str(raw).replace("\\", "/"))
    if path.is_absolute():
        return path
    return repo_root / path


def review_root(repo_root: Path, book: dict[str, Any], style: str) -> Path:
    return book_output_root(repo_root, book) / "reviews" / style


def fixes_root(repo_root: Path, book: dict[str, Any], style: str) -> Path:
    return book_output_root(repo_root, book) / "review-fixes" / style


def manifest_path(repo_root: Path, book: dict[str, Any], style: str) -> Path:
    return fixes_root(repo_root, book, style) / "fix-manifest.json"


def manual_review_path(repo_root: Path, book: dict[str, Any], style: str) -> Path:
    return fixes_root(repo_root, book, style) / "manual-review.md"


def fix_plan_path(repo_root: Path, book: dict[str, Any], style: str) -> Path:
    return fixes_root(repo_root, book, style) / "fix-plan.txt"


def promotion_report_path(repo_root: Path, book: dict[str, Any], style: str) -> Path:
    return fixes_root(repo_root, book, style) / "promotion-report.json"


def load_review_summary(repo_root: Path, book: dict[str, Any], style: str) -> dict[str, Any]:
    path = review_root(repo_root, book, style) / "review-summary.json"
    if not path.exists():
        raise FileNotFoundError(f"Review-Summary fehlt: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_chapter_reviews(
    repo_root: Path,
    book: dict[str, Any],
    style: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    summary = load_review_summary(repo_root, book, style)
    root = review_root(repo_root, book, style)
    reviews = []
    for chapter in summary.get("chapters") or []:
        path = root / "chapters" / f"{chapter}-review.json"
        if path.exists():
            reviews.append(json.loads(path.read_text(encoding="utf-8")))
    return summary, reviews


def extract_structured_replacement(finding: dict[str, Any]) -> Replacement | None:
    current = str(finding.get("current_text") or "").strip()
    suggested = str(finding.get("suggested_text") or "").strip()
    if not current or not suggested or current == suggested:
        return None
    if finding.get("fixable") is False:
        return None
    confidence_raw = finding.get("confidence")
    try:
        confidence = float(confidence_raw) if confidence_raw is not None else 0.85
    except (TypeError, ValueError):
        confidence = 0.85
    return Replacement(current, suggested, source="structured", confidence=confidence)


def word_count(text: str) -> int:
    return len([part for part in re.split(r"\s+", text.strip()) if part])


def replacement_scope_is_safe(current: str, suggested: str) -> bool:
    current_words = word_count(current)
    suggested_words = word_count(suggested)
    if current_words <= 1:
        return suggested_words <= 4
    if suggested_words == 0:
        return False
    return current_words <= max(4, suggested_words * 3)


def extract_quoted_replacement(finding: dict[str, Any]) -> Replacement | None:
    evidence = str(finding.get("evidence") or "")
    recommendation = str(finding.get("recommendation") or "")
    current_match = TRANSLATION_QUOTE_RE.search(evidence)
    suggested_match = RECOMMENDATION_QUOTE_RE.search(recommendation)
    if not current_match or not suggested_match:
        return None
    current = current_match.group(1).strip()
    suggested = suggested_match.group(1).strip()
    if not current or not suggested or current == suggested:
        return None
    if not replacement_scope_is_safe(current, suggested):
        return None
    return Replacement(current, suggested, source="quoted-recommendation", confidence=0.70)


def extract_mixed_cyrillic_replacements(text: str) -> list[Replacement]:
    replacements: list[Replacement] = []
    seen: set[tuple[str, str]] = set()
    for match in MIXED_TOKEN_RE.finditer(text):
        token = match.group(0)
        has_cyrillic = bool(CYRILLIC_RE.search(token))
        has_latin = any(("A" <= ch <= "Z") or ("a" <= ch <= "z") or ("\u00C0" <= ch <= "\u024F") for ch in token)
        if not has_cyrillic or not has_latin:
            continue
        converted = "".join(HOMOGLYPH_MAP.get(ch, ch) for ch in token)
        if CYRILLIC_RE.search(converted) or converted == token:
            continue
        key = (token, converted)
        if key in seen:
            continue
        seen.add(key)
        replacements.append(Replacement(token, converted, source="mixed-cyrillic", confidence=0.90))
    return replacements


def replacements_for_finding(finding: dict[str, Any], current_text: str) -> list[Replacement]:
    structured = extract_structured_replacement(finding)
    if structured:
        return [structured]
    quoted = extract_quoted_replacement(finding)
    if quoted:
        return [quoted]
    if str(finding.get("category") or "") == "cyrillic_in_translation":
        return extract_mixed_cyrillic_replacements(current_text)
    return []


def apply_replacements(
    text: str,
    chapter: str,
    scene: int,
    findings: list[dict[str, Any]],
) -> tuple[str, list[AppliedFix], list[ManualFinding]]:
    out = text
    applied: list[AppliedFix] = []
    manual: list[ManualFinding] = []
    for finding in findings:
        category = str(finding.get("category") or "review")
        message = str(finding.get("message") or finding.get("summary") or "")
        recommendation = str(finding.get("recommendation") or "")
        replacements = replacements_for_finding(finding, out)
        if not replacements:
            manual.append(ManualFinding(
                chapter=chapter,
                scene=scene,
                category=category,
                message=message,
                reason="kein eindeutiger maschineller Ersatz erkennbar",
                recommendation=recommendation,
            ))
            continue
        for repl in replacements:
            count = out.count(repl.current_text)
            if count == 0:
                manual.append(ManualFinding(
                    chapter=chapter,
                    scene=scene,
                    category=category,
                    message=message,
                    reason=f"Ausgangstext nicht gefunden: {repl.current_text!r}",
                    recommendation=recommendation,
                ))
                continue
            if count > 1:
                manual.append(ManualFinding(
                    chapter=chapter,
                    scene=scene,
                    category=category,
                    message=message,
                    reason=f"Ausgangstext kommt {count}x vor: {repl.current_text!r}",
                    recommendation=recommendation,
                ))
                continue
            out = out.replace(repl.current_text, repl.suggested_text, 1)
            applied.append(AppliedFix(
                chapter=chapter,
                scene=scene,
                category=category,
                source=repl.source,
                current_text=repl.current_text,
                suggested_text=repl.suggested_text,
            ))
    return out, applied, manual


def build_fix_plan(
    repo_root: Path,
    book: dict[str, Any],
    style: str,
) -> tuple[dict[str, Any], list[StagedScene], list[ManualFinding]]:
    summary, reviews = load_chapter_reviews(repo_root, book, style)
    staged: list[StagedScene] = []
    manual_all: list[ManualFinding] = []
    root = fixes_root(repo_root, book, style)
    for review in reviews:
        for scene_data in review.get("scenes") or []:
            findings = scene_data.get("findings") or []
            if not findings:
                continue
            chapter = str(scene_data.get("chapter") or review.get("chapter"))
            scene = int(scene_data.get("scene") or 0)
            source_path = repo_path(repo_root, str(scene_data.get("de_path") or ""))
            ru_path = repo_path(repo_root, str(scene_data.get("ru_path") or ""))
            if not source_path.exists():
                manual_all.append(ManualFinding(
                    chapter=chapter,
                    scene=scene,
                    category="missing_source",
                    message="DE-Szenendatei fehlt.",
                    reason=str(source_path),
                ))
                continue
            text = source_path.read_text(encoding="utf-8", errors="replace")
            candidate, applied, manual = apply_replacements(text, chapter, scene, findings)
            manual_all.extend(manual)
            if not applied:
                continue
            candidate_rel = root / chapter / f"scene-{scene:02d}.md"
            staged.append(StagedScene(
                chapter=chapter,
                scene=scene,
                source_path=str(source_path.relative_to(repo_root)),
                ru_path=str(ru_path.relative_to(repo_root)) if ru_path.exists() else "",
                candidate_path=str(candidate_rel.relative_to(repo_root)),
                original_sha256=sha256_text(text),
                candidate_sha256=sha256_text(candidate),
                applied=applied,
                manual=manual,
            ))
    return summary, staged, manual_all


def render_plan_text(staged: list[StagedScene], manual: list[ManualFinding]) -> str:
    applied_count = sum(len(item.applied) for item in staged)
    lines = [
        f"Fixbare Szenen: {len(staged)}",
        f"Fixbare Ersetzungen: {applied_count}",
        f"Manuell zu pruefen: {len(manual)}",
        "",
    ]
    for item in staged:
        lines.append(f"- Kapitel {item.chapter}, Szene {item.scene:02d}: {len(item.applied)} Ersetzung(en)")
        for fix in item.applied:
            lines.append(f"  * {fix.category}: {fix.current_text!r} -> {fix.suggested_text!r}")
    if manual:
        lines.extend(["", "Manuell:", ""])
        for item in manual[:80]:
            lines.append(f"- Kapitel {item.chapter}, Szene {item.scene:02d}: {item.category} - {item.reason}")
        if len(manual) > 80:
            lines.append(f"- ... {len(manual) - 80} weitere")
    return "\n".join(lines).rstrip() + "\n"


def write_manual_review(path: Path, manual: list[ManualFinding]) -> None:
    lines = ["# Manuelle Review-Fixes", ""]
    if not manual:
        lines.append("Keine manuell offenen Befunde.")
    for item in manual:
        lines.extend([
            f"## Kapitel {item.chapter}, Szene {item.scene:02d}: {item.category}",
            "",
            item.message or "(ohne Meldung)",
            "",
            f"Grund: {item.reason}",
            "",
        ])
        if item.recommendation:
            lines.extend([f"Empfehlung: {item.recommendation}", ""])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_plan_artifacts(
    repo_root: Path,
    book: dict[str, Any],
    style: str,
    staged: list[StagedScene],
    manual: list[ManualFinding],
) -> None:
    root = fixes_root(repo_root, book, style)
    root.mkdir(parents=True, exist_ok=True)
    fix_plan_path(repo_root, book, style).write_text(
        render_plan_text(staged, manual),
        encoding="utf-8",
    )
    write_manual_review(manual_review_path(repo_root, book, style), manual)


def stage_fixes(
    repo_root: Path,
    book: dict[str, Any],
    style: str,
) -> FixManifest:
    summary, staged, manual = build_fix_plan(repo_root, book, style)
    root = fixes_root(repo_root, book, style)
    root.mkdir(parents=True, exist_ok=True)
    write_plan_artifacts(repo_root, book, style, staged, manual)
    for item in staged:
        source = repo_path(repo_root, item.source_path)
        candidate = repo_path(repo_root, item.candidate_path)
        original = source.read_text(encoding="utf-8", errors="replace")
        candidate_text, _applied, _manual = apply_replacements(
            original,
            item.chapter,
            item.scene,
            [
                finding
                for review in load_chapter_reviews(repo_root, book, style)[1]
                if str(review.get("chapter")) == item.chapter
                for scene_data in review.get("scenes") or []
                if int(scene_data.get("scene") or 0) == item.scene
                for finding in scene_data.get("findings") or []
            ],
        )
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_text(candidate_text, encoding="utf-8")
    manifest = FixManifest(
        version=FIX_VERSION,
        book_id=str(book.get("id")),
        style=style,
        created_at=datetime.now().isoformat(timespec="seconds"),
        source_review_summary=str((review_root(repo_root, book, style) / "review-summary.json").relative_to(repo_root)),
        staged=staged,
    )
    manifest_path(repo_root, book, style).write_text(
        json.dumps(asdict(manifest), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest


def load_manifest(repo_root: Path, book: dict[str, Any], style: str) -> FixManifest:
    path = manifest_path(repo_root, book, style)
    if not path.exists():
        raise FileNotFoundError(f"Fix-Manifest fehlt: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    staged = [
        StagedScene(
            chapter=str(item["chapter"]),
            scene=int(item["scene"]),
            source_path=str(item["source_path"]),
            ru_path=str(item.get("ru_path") or ""),
            candidate_path=str(item["candidate_path"]),
            original_sha256=str(item["original_sha256"]),
            candidate_sha256=str(item["candidate_sha256"]),
            applied=[
                AppliedFix(
                    chapter=str(fix["chapter"]),
                    scene=int(fix["scene"]),
                    category=str(fix["category"]),
                    source=str(fix["source"]),
                    current_text=str(fix["current_text"]),
                    suggested_text=str(fix["suggested_text"]),
                )
                for fix in item.get("applied") or []
            ],
            manual=[],
        )
        for item in data.get("staged") or []
    ]
    return FixManifest(
        version=int(data.get("version") or 0),
        book_id=str(data.get("book_id") or ""),
        style=str(data.get("style") or ""),
        created_at=str(data.get("created_at") or ""),
        source_review_summary=str(data.get("source_review_summary") or ""),
        staged=staged,
    )


def candidate_has_errors(repo_root: Path, item: StagedScene) -> list[str]:
    if not item.ru_path:
        return ["RU-Pfad fehlt im Manifest."]
    ru_path = repo_path(repo_root, item.ru_path)
    candidate_path = repo_path(repo_root, item.candidate_path)
    if not ru_path.exists():
        return [f"RU-Datei fehlt: {item.ru_path}"]
    ru_text = ru_path.read_text(encoding="utf-8", errors="replace")
    de_text = candidate_path.read_text(encoding="utf-8", errors="replace")
    findings = deterministic_scene_findings(
        item.chapter,
        item.scene,
        ru_text,
        de_text,
        count_words(ru_text),
        count_words(de_text),
    )
    return [f"{finding.category}: {finding.message}" for finding in findings if finding.severity == "ERROR"]


def promote_staged_fixes(
    repo_root: Path,
    book: dict[str, Any],
    style: str,
    assemble_func,
) -> PromotionReport:
    manifest = load_manifest(repo_root, book, style)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    items: list[PromotionItem] = []
    promoted_chapters: set[str] = set()
    for item in manifest.staged:
        source = repo_path(repo_root, item.source_path)
        candidate = repo_path(repo_root, item.candidate_path)
        if not source.exists() or not candidate.exists():
            items.append(PromotionItem(item.chapter, item.scene, item.source_path, item.candidate_path, "skipped", "Quelle oder Kandidat fehlt."))
            continue
        source_text = source.read_text(encoding="utf-8", errors="replace")
        candidate_text = candidate.read_text(encoding="utf-8", errors="replace")
        if sha256_text(source_text) != item.original_sha256:
            items.append(PromotionItem(item.chapter, item.scene, item.source_path, item.candidate_path, "skipped", "Original-Datei wurde seit Staging geaendert."))
            continue
        if sha256_text(candidate_text) != item.candidate_sha256:
            items.append(PromotionItem(item.chapter, item.scene, item.source_path, item.candidate_path, "skipped", "Kandidat-Datei wurde seit Staging geaendert."))
            continue
        errors = candidate_has_errors(repo_root, item)
        if errors:
            items.append(PromotionItem(item.chapter, item.scene, item.source_path, item.candidate_path, "skipped", "; ".join(errors[:3])))
            continue
        backup = source.with_name(f"{source.name}.bak-{stamp}")
        shutil.copy2(source, backup)
        source.write_text(candidate_text, encoding="utf-8")
        promoted_chapters.add(item.chapter)
        items.append(PromotionItem(
            item.chapter,
            item.scene,
            item.source_path,
            item.candidate_path,
            "promoted",
            "uebernommen",
            backup_path=str(backup.relative_to(repo_root)),
        ))
    output_root = book_output_root(repo_root, book)
    assembled: list[str] = []
    for chapter in sorted(promoted_chapters):
        out_path, _words, _missing = assemble_func(
            output_root,
            chapter,
            style,
            str(book.get("title") or book.get("id")),
            dry_run=False,
        )
        if out_path is not None:
            assembled.append(str(out_path.relative_to(repo_root)))
    report = PromotionReport(
        book_id=str(book.get("id")),
        style=style,
        created_at=datetime.now().isoformat(timespec="seconds"),
        promoted=sum(1 for item in items if item.status == "promoted"),
        skipped=sum(1 for item in items if item.status != "promoted"),
        assembled_chapters=assembled,
        items=items,
    )
    root = fixes_root(repo_root, book, style)
    root.mkdir(parents=True, exist_ok=True)
    promotion_report_path(repo_root, book, style).write_text(
        json.dumps(asdict(report), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report
