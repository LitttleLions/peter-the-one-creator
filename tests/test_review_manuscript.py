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
    build_llm_prompt_for_paths,
    chapter_findings,
    review_chapter_deterministic,
    write_reports,
)


def write_scene(root: Path, lang: str, style: str | None, chapter: str, scene: int, text: str) -> None:
    if lang != "de":
        path = root / "books" / "sample" / "work" / "scenes" / lang / chapter / f"scene-{scene:02d}.md"
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

    def test_llm_json_without_findings_is_warning(self) -> None:
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
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_scene(root, "ru", None, "001", 1, "## 1\n\n" + ("Русский текст. " * 80))
            write_scene(root, "de", "stil-test", "001", 1, "## Szene 1\n\n" + ("Deutscher Text. " * 80))

            add_llm_findings(
                root,
                self.book(),
                "stil-test",
                review,
                chat=lambda _system, _user: '{"anderes_feld":[]}',
                scope="all",
            )

        findings = chapter_findings(review)
        self.assertEqual(findings[0].category, "llm_review_failed")
        self.assertIn("findings", findings[0].message)

    def test_japanese_source_skips_length_ratio(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ja = "## 1\n\n" + ("日本語の原文です。" * 40)
            de = "## Szene 1\n\n" + " ".join(
                f"Deutscher Satz der Uebersetzung Nummer {idx}."
                for idx in range(200)
            )
            write_scene(root, "ja", None, "006", 1, ja)
            write_scene(root, "de", "stil-test", "006", 1, de)
            book = {
                **self.book(),
                "source_lang": "ja",
            }

            review = review_chapter_deterministic(root, book, "006", "stil-test")

        categories = {item.category for item in chapter_findings(review)}
        self.assertNotIn("length_ratio", categories)

    def test_llm_prompt_includes_names_and_source_lang(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_scene(root, "ja", None, "006", 1, "## 1\n\n日本語の原文です。 " * 20)
            write_scene(root, "de", "stil-test", "006", 1, "## Szene 1\n\nTemüdschin ritt weiter. " * 20)
            names_path = root / "books" / "sample" / "names.yaml"
            names_path.parent.mkdir(parents=True, exist_ok=True)
            names_path.write_text(
                "entries:\n"
                "- source: テムヂン\n"
                "  target: Temüdschin\n"
                "  type: person\n"
                "  status: approved\n",
                encoding="utf-8",
            )
            book = {
                **self.book(),
                "source_lang": "ja",
                "names_file": "books/sample/names.yaml",
            }
            scene = SceneReview(
                chapter="006",
                scene=1,
                ru_path="books/sample/work/scenes/ja/006/scene-01.md",
                de_path="books/sample/work/scenes/de/stil-test/006/scene-01.md",
                ru_words=20,
                de_words=40,
            )

            _system, user = build_llm_prompt_for_paths(root, book, "stil-test", scene)

        self.assertIn("Original JA:", user)
        self.assertIn("Temüdschin", user)
        self.assertIn("verbindliche namens-/begriffsliste", user.lower())
        self.assertIn("current_text", user)
        self.assertIn("suggested_text", user)

    def test_canonical_name_criticism_is_dropped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_scene(root, "ja", None, "006", 1, "## 1\n\nテムヂンが来た。" * 20)
            write_scene(root, "de", "stil-test", "006", 1, "## Szene 1\n\nTemüdschin kam. " * 40)
            names_path = root / "books" / "sample" / "names.yaml"
            names_path.parent.mkdir(parents=True, exist_ok=True)
            names_path.write_text(
                "entries:\n- source: テムヂン\n  target: Temüdschin\n",
                encoding="utf-8",
            )
            book = {
                **self.book(),
                "source_lang": "ja",
                "names_file": "books/sample/names.yaml",
            }
            review = ChapterReview(
                chapter="006",
                style="stil-test",
                ru_scenes=1,
                de_scenes=1,
                scenes=[
                    SceneReview(
                        chapter="006",
                        scene=1,
                        ru_path="books/sample/work/scenes/ja/006/scene-01.md",
                        de_path="books/sample/work/scenes/de/stil-test/006/scene-01.md",
                        ru_words=20,
                        de_words=40,
                        findings=[],
                    )
                ],
            )
            payload = json.dumps({
                "findings": [
                    {
                        "severity": "ERROR",
                        "category": "names",
                        "summary": "Falsche Transkription Temüdschin.",
                        "evidence": "DE: Temüdschin",
                        "recommendation": "Temürjin verwenden.",
                        "fixable": True,
                        "current_text": "Temüdschin kam",
                        "suggested_text": "Temürjin kam",
                        "confidence": 0.9,
                    },
                    {
                        "severity": "WARNING",
                        "category": "grammar",
                        "summary": "Satz unklar.",
                        "evidence": "kam.",
                        "recommendation": "Umformulieren.",
                        "fixable": True,
                        "current_text": "",
                        "suggested_text": "",
                        "confidence": 0.5,
                    },
                ]
            }, ensure_ascii=False)

            add_llm_findings(
                root,
                book,
                "stil-test",
                review,
                chat=lambda _system, _user: payload,
                scope="all",
            )

        findings = chapter_findings(review)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].category, "grammar")
        self.assertIs(findings[0].fixable, False)


if __name__ == "__main__":
    unittest.main()
