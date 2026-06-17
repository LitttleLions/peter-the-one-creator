from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib.review_fixes import (  # noqa: E402
    apply_replacements,
    build_fix_plan,
    promote_staged_fixes,
    stage_fixes,
)


def book() -> dict:
    return {
        "id": "sample",
        "title": "Sample",
        "author": "Autor",
        "work_dir": "books/sample/work",
    }


def scene_paths(root: Path, style: str = "stil-test") -> tuple[Path, Path]:
    ru_path = root / "books" / "sample" / "work" / "scenes" / "ru" / "001" / "scene-01.md"
    de_path = root / "books" / "sample" / "work" / "scenes" / "de" / style / "001" / "scene-01.md"
    ru_path.parent.mkdir(parents=True, exist_ok=True)
    de_path.parent.mkdir(parents=True, exist_ok=True)
    return ru_path, de_path


def write_review(root: Path, finding: dict, style: str = "stil-test") -> None:
    review_root = root / "books" / "sample" / "work" / "reviews" / style
    chapters = review_root / "chapters"
    chapters.mkdir(parents=True, exist_ok=True)
    summary = {
        "book_id": "sample",
        "title": "Sample",
        "style": style,
        "chapters": ["001"],
        "created_at": "2026-06-15T00:00:00",
        "llm": "none",
        "counts": {"ERROR": 1, "WARNING": 0, "INFO": 0},
        "chapter_reports": [f"books/sample/work/reviews/{style}/chapters/001-review.md"],
        "summary_markdown": f"books/sample/work/reviews/{style}/review-summary.md",
        "summary_json": f"books/sample/work/reviews/{style}/review-summary.json",
    }
    review = {
        "chapter": "001",
        "style": style,
        "ru_scenes": 1,
        "de_scenes": 1,
        "findings": [],
        "scenes": [
            {
                "chapter": "001",
                "scene": 1,
                "ru_path": "books/sample/work/scenes/ru/001/scene-01.md",
                "de_path": f"books/sample/work/scenes/de/{style}/001/scene-01.md",
                "ru_words": 100,
                "de_words": 100,
                "findings": [finding],
            }
        ],
    }
    (review_root / "review-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False),
        encoding="utf-8",
    )
    (chapters / "001-review.json").write_text(
        json.dumps(review, ensure_ascii=False),
        encoding="utf-8",
    )


class ReviewFixTests(unittest.TestCase):
    def test_extracts_quoted_translation_replacement(self) -> None:
        text = "Vorher alter Ausdruck nachher."
        findings = [{
            "category": "names",
            "message": "Name pruefen.",
            "evidence": "Original: «x»; Übersetzung: «alter Ausdruck»",
            "recommendation": "Verwende künftig «neuer Ausdruck».",
        }]

        fixed, applied, manual = apply_replacements(text, "001", 1, findings)

        self.assertEqual(fixed, "Vorher neuer Ausdruck nachher.")
        self.assertEqual(len(applied), 1)
        self.assertEqual(manual, [])

    def test_repairs_single_mixed_cyrillic_token(self) -> None:
        text = "Deine Ehefrau Dunkа schlaegt die Stirn."
        findings = [{
            "category": "cyrillic_in_translation",
            "message": "DE-Szene enthaelt kyrillische Zeichen.",
        }]

        fixed, applied, manual = apply_replacements(text, "001", 1, findings)

        self.assertIn("Dunka", fixed)
        self.assertNotIn("Dunkа", fixed)
        self.assertEqual(len(applied), 1)
        self.assertEqual(manual, [])

    def test_repairs_mixed_cyrillic_transliteration_tail(self) -> None:
        text = "Man sah Boborykин in der Menge."
        findings = [{
            "category": "cyrillic_in_translation",
            "message": "DE-Szene enthaelt kyrillische Zeichen.",
        }]

        fixed, applied, manual = apply_replacements(text, "005", 13, findings)

        self.assertIn("Boborykin", fixed)
        self.assertNotIn("Boborykин", fixed)
        self.assertEqual(len(applied), 1)
        self.assertEqual(manual, [])

    def test_does_not_replace_multiple_occurrences(self) -> None:
        text = "Name Name"
        findings = [{
            "category": "names",
            "message": "Name pruefen.",
            "current_text": "Name",
            "suggested_text": "Neuer Name",
            "fixable": True,
        }]

        fixed, applied, manual = apply_replacements(text, "001", 1, findings)

        self.assertEqual(fixed, text)
        self.assertEqual(applied, [])
        self.assertEqual(len(manual), 1)
        self.assertIn("2x", manual[0].reason)

    def test_does_not_replace_missing_text(self) -> None:
        text = "Kein Treffer."
        findings = [{
            "category": "names",
            "message": "Name pruefen.",
            "current_text": "Alter Name",
            "suggested_text": "Neuer Name",
            "fixable": True,
        }]

        fixed, applied, manual = apply_replacements(text, "001", 1, findings)

        self.assertEqual(fixed, text)
        self.assertEqual(applied, [])
        self.assertEqual(len(manual), 1)
        self.assertIn("nicht gefunden", manual[0].reason)

    def test_does_not_replace_whole_sentence_with_single_name(self) -> None:
        text = "Deine Ehefrau Dunka schlaegt die Stirn."
        findings = [{
            "category": "names",
            "message": "Name pruefen.",
            "evidence": "Übersetzung: «Deine Ehefrau Dunka schlaegt die Stirn»",
            "recommendation": "Verwende die uebliche Form «Dunja».",
        }]

        fixed, applied, manual = apply_replacements(text, "001", 1, findings)

        self.assertEqual(fixed, text)
        self.assertEqual(applied, [])
        self.assertEqual(len(manual), 1)

    def test_stage_and_promote_with_hash_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ru_path, de_path = scene_paths(root)
            ru_path.write_text("## 1\n\n" + ("Русский текст. " * 400), encoding="utf-8")
            de_path.write_text(
                "## Szene 1\n\n"
                + " ".join(
                    f"Deutscher Satz der Uebersetzung Nummer {idx} "
                    "mit einem ruhigen Verlauf und klarer Sprache."
                    for idx in range(100)
                )
                + " Dunkа.",
                encoding="utf-8",
            )
            write_review(root, {
                "severity": "ERROR",
                "category": "cyrillic_in_translation",
                "message": "DE-Szene enthaelt kyrillische Zeichen.",
            })

            _summary, staged, manual = build_fix_plan(root, book(), "stil-test")
            manifest = stage_fixes(root, book(), "stil-test")
            de_path.write_text(de_path.read_text(encoding="utf-8") + "\nNachtraeglich.", encoding="utf-8")

            report = promote_staged_fixes(
                root,
                book(),
                "stil-test",
                assemble_func=lambda output_root, chapter, style, title, dry_run=False: (
                    output_root / "assembled" / style / f"{chapter}.md",
                    0,
                    [],
                ),
            )

        self.assertEqual(len(staged), 1)
        self.assertEqual(manual, [])
        self.assertEqual(len(manifest.staged), 1)
        self.assertEqual(report.promoted, 0)
        self.assertEqual(report.skipped, 1)
        self.assertIn("Original-Datei", report.items[0].message)

    def test_stage_and_promote_clean_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ru_path, de_path = scene_paths(root)
            ru_path.write_text("## 1\n\n" + ("Русский текст. " * 400), encoding="utf-8")
            de_path.write_text(
                "## Szene 1\n\n"
                + " ".join(
                    f"Deutscher Satz der Uebersetzung Nummer {idx} "
                    "mit einem ruhigen Verlauf und klarer Sprache."
                    for idx in range(100)
                )
                + " Dunkа.",
                encoding="utf-8",
            )
            write_review(root, {
                "severity": "ERROR",
                "category": "cyrillic_in_translation",
                "message": "DE-Szene enthaelt kyrillische Zeichen.",
            })
            stage_fixes(root, book(), "stil-test")

            report = promote_staged_fixes(
                root,
                book(),
                "stil-test",
                assemble_func=lambda output_root, chapter, style, title, dry_run=False: (
                    output_root / "assembled" / style / f"{chapter}.md",
                    0,
                    [],
                ),
            )
            promoted_text = de_path.read_text(encoding="utf-8")

        self.assertEqual(report.promoted, 1)
        self.assertIn("Dunka", promoted_text)
        self.assertNotIn("Dunkа", promoted_text)


if __name__ == "__main__":
    unittest.main()
