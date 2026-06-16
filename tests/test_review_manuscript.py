from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib.review_checks import (  # noqa: E402
    ChapterReview,
    SceneReview,
    add_llm_findings,
    chapter_findings,
    review_chapter_deterministic,
    write_reports,
)


def write_scene(root: Path, lang: str, style: str | None, chapter: str, scene: int, text: str) -> None:
    if lang == "ru":
        path = root / "books" / "sample" / "work" / "scenes" / "ru" / chapter / f"scene-{scene:02d}.md"
    else:
        assert style is not None
        path = root / "books" / "sample" / "work" / "scenes" / "de" / style / chapter / f"scene-{scene:02d}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ReviewManuscriptTests(unittest.TestCase):
    def book(self) -> dict:
        return {
            "id": "sample",
            "title": "Sample",
            "author": "Autor",
            "work_dir": "books/sample/work",
        }

    def test_complete_scene_has_no_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ru = "## 1\n\n" + " ".join(
                f"Это русский исходный текст номер {idx}." for idx in range(60)
            )
            de = "## Szene 1\n\n" + " ".join(
                f"Deutscher Satz der Uebersetzung Nummer {idx}."
                for idx in range(65)
            )
            write_scene(root, "ru", None, "001", 1, ru)
            write_scene(root, "de", "stil-test", "001", 1, de)

            review = review_chapter_deterministic(root, self.book(), "001", "stil-test")

        self.assertEqual(chapter_findings(review), [])

    def test_missing_de_scene_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_scene(root, "ru", None, "001", 1, "## 1\n\n" + ("Русский текст. " * 80))

            review = review_chapter_deterministic(root, self.book(), "001", "stil-test")

        findings = chapter_findings(review)
        self.assertEqual(findings[0].severity, "ERROR")
        self.assertEqual(findings[0].category, "missing_de_scene")

    def test_cyrillic_and_replacement_chars_are_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_scene(root, "ru", None, "001", 1, "## 1\n\n" + ("Русский текст. " * 80))
            write_scene(
                root,
                "de",
                "stil-test",
                "001",
                1,
                "## Szene 1\n\nDies ist Deutsch, aber hier steht noch Москва und ein \uFFFD Zeichen. "
                * 10,
            )

            review = review_chapter_deterministic(root, self.book(), "001", "stil-test")

        categories = {item.category for item in chapter_findings(review)}
        self.assertIn("cyrillic_in_translation", categories)
        self.assertIn("encoding_garbage", categories)

    def test_write_reports_creates_summary_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_scene(root, "ru", None, "001", 1, "## 1\n\n" + ("Русский текст. " * 80))
            review = review_chapter_deterministic(root, self.book(), "001", "stil-test")

            summary = write_reports(root, self.book(), "stil-test", [review], llm="none")

            summary_path = root / summary.summary_json
            data = json.loads(summary_path.read_text(encoding="utf-8"))

        self.assertEqual(data["counts"]["ERROR"], 1)
        self.assertTrue(summary.summary_markdown.endswith("review-summary.md"))

    def test_clean_chapter_does_not_create_chapter_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ru = "## 1\n\n" + " ".join(
                f"Это русский исходный текст номер {idx}." for idx in range(60)
            )
            de = "## Szene 1\n\n" + " ".join(
                f"Deutscher Satz der Uebersetzung Nummer {idx}."
                for idx in range(65)
            )
            write_scene(root, "ru", None, "001", 1, ru)
            write_scene(root, "de", "stil-test", "001", 1, de)
            review = review_chapter_deterministic(root, self.book(), "001", "stil-test")

            summary = write_reports(root, self.book(), "stil-test", [review], llm="none")

            chapter_md = (
                root
                / "books"
                / "sample"
                / "work"
                / "reviews"
                / "stil-test"
                / "chapters"
                / "001-review.md"
            )

        self.assertEqual(summary.chapter_reports, [])
        self.assertFalse(chapter_md.exists())

    def test_llm_json_failure_is_warning_not_release_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ru = "## 1\n\n" + " ".join(
                f"Это русский исходный текст номер {idx}." for idx in range(60)
            )
            de = "## Szene 1\n\n" + " ".join(
                f"Deutscher Satz der Uebersetzung Nummer {idx}."
                for idx in range(65)
            )
            write_scene(root, "ru", None, "001", 1, ru)
            write_scene(root, "de", "stil-test", "001", 1, de)
            review = ChapterReview(
                chapter="001",
                style="stil-test",
                ru_scenes=1,
                de_scenes=1,
                scenes=[
                    SceneReview(
                        chapter="001",
                        scene=1,
                        ru_path="books/sample/work/scenes/ru/001/scene-01.md",
                        de_path="books/sample/work/scenes/de/stil-test/001/scene-01.md",
                        ru_words=100,
                        de_words=100,
                        findings=[],
                    )
                ],
            )

            add_llm_findings(
                root,
                self.book(),
                "stil-test",
                review,
                chat=lambda _system, _user: "kein json",
                scope="all",
            )

        findings = chapter_findings(review)
        self.assertEqual(findings[0].category, "llm_review_failed")
        self.assertEqual(findings[0].severity, "WARNING")


if __name__ == "__main__":
    unittest.main()
