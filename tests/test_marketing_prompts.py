from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib import marketing_campaign as campaignpkg  # noqa: E402
from lib import marketing_prompts as promptspkg  # noqa: E402

BRIEF_NO_SONG = {
    "book_id": "sample",
    "title": "Beispielroman",
    "author": "Anna Beispiel",
    "translator": "Motivatier Classics",
    "translator_label": "Uebersetzung und editorische Einrichtung",
    "publisher": "Motivatier Hermann Stiftung",
    "language": "de-DE",
    "description": "Kurzbeschreibung.",
    "summary": "Inhaltsbeschreibung.",
    "author_bio": "Zur Autorin.",
    "edition_notes": ["Diese Ausgabe ist eine neue deutsche Uebersetzung."],
    "names": ["- Peter -> Peter"],
    "sample_passage": {
        "chapter": "001",
        "scene": 1,
        "source": "books/sample/work/scenes/de/stil-test/001/scene-01.md",
        "text": "Sanka sprang von der Ofenbank.",
    },
    "brand": {"label": "Motivatier Classics"},
    "limits": {
        "x_weighted_chars": 280,
        "x_target_min": 220,
        "x_target_max": 250,
        "youtube_title_chars": 100,
        "youtube_description_chars": 5000,
    },
    "song": None,
}


def brief_with_song() -> dict:
    brief = json.loads(json.dumps(BRIEF_NO_SONG))
    brief["song"] = {
        "title": "Hohes Feuer",
        "ai_generated": "true",
        "credits": ["Musik: Test"],
    }
    return brief


class ExtractJsonTests(unittest.TestCase):
    def test_extracts_plain_and_fenced_json(self) -> None:
        self.assertEqual(promptspkg.extract_json('{"a": 1}'), {"a": 1})
        fenced = "Hier:\n```json\n{\"texts\": {}}\n```\nEnde"
        self.assertEqual(promptspkg.extract_json(fenced), {"texts": {}})

    def test_invalid_json_raises(self) -> None:
        with self.assertRaises(ValueError):
            promptspkg.extract_json("keine Ausgabe")


class ValidatePayloadTests(unittest.TestCase):
    def test_urls_are_removed_and_unknown_ids_dropped(self) -> None:
        payload = {
            "texts": {
                "x-t0-intro": {"text": "Ein Text mit https://example.org im Satz."},
                "x-unbekannt": {"text": "Weg damit."},
            }
        }
        clean, problems = promptspkg.validate_payload(payload, BRIEF_NO_SONG)
        self.assertNotIn("http", clean["texts"]["x-t0-intro"]["text"])
        self.assertNotIn("x-unbekannt", clean["texts"])
        self.assertTrue(any("unbekannte Beitrags-ID" in item for item in problems))

    def test_song_positions_are_dropped_without_song(self) -> None:
        payload = {
            "texts": {"x-t1-song": {"text": "Songtext"}},
            "youtube": {"title": "Liedtitel", "body": "Zwei Saetze."},
        }
        clean, problems = promptspkg.validate_payload(payload, BRIEF_NO_SONG)
        self.assertEqual(clean["texts"], {})
        self.assertEqual(clean["youtube"], {})
        self.assertEqual(len(problems), 2)

    def test_song_positions_are_kept_with_song(self) -> None:
        payload = {
            "texts": {"x-t1-song": {"text": "Songtext"}},
            "youtube": {
                "title": "Liedtitel",
                "prequel": "Vorschau.",
                "body": "Zwei Saetze.",
                "thumbnail_label": "Label",
                "shorts": {
                    "yt-short-1": {
                        "title": "Short 1",
                        "description": "Beschreibung",
                        "overlays": ["A", "B"],
                    }
                },
            },
        }
        clean, problems = promptspkg.validate_payload(payload, brief_with_song())
        self.assertEqual(problems, [])
        self.assertIn("x-t1-song", clean["texts"])
        self.assertEqual(clean["youtube"]["title"], "Liedtitel")
        self.assertEqual(
            clean["youtube"]["shorts"]["yt-short-1"]["overlays"], ["A", "B"]
        )

    def test_empty_texts_are_reported(self) -> None:
        payload = {"texts": {"x-t5-content": {"text": "   "}}}
        clean, problems = promptspkg.validate_payload(payload, BRIEF_NO_SONG)
        self.assertEqual(clean["texts"], {})
        self.assertTrue(any("leerer Text" in item for item in problems))


class PromptBuildTests(unittest.TestCase):
    def test_system_prompt_forbids_urls_and_invented_facts(self) -> None:
        self.assertIn("KEINE URL", promptspkg.SYSTEM_PROMPT)
        self.assertIn("Erfinde keine Rezensionen", promptspkg.SYSTEM_PROMPT)

    def test_user_prompt_contains_brief_but_not_the_whole_novel(self) -> None:
        system, user = promptspkg.build_prompt(BRIEF_NO_SONG)
        self.assertEqual(system, promptspkg.SYSTEM_PROMPT)
        self.assertIn("Sanka sprang von der Ofenbank.", user)
        self.assertIn("Beispielroman", user)
        self.assertIn("Kapitel 001, Szene 1", user)
        self.assertIn("- Peter -> Peter", user)
        self.assertIn("x-t8-sample", user)
        self.assertLess(len(user), 12000)

    def test_song_section_marks_missing_music(self) -> None:
        _, user = promptspkg.build_prompt(BRIEF_NO_SONG)
        self.assertIn("kein Song vorhanden", user)
        _, user_with_song = promptspkg.build_prompt(brief_with_song())
        self.assertIn("Hohes Feuer", user_with_song)


class PromptPersistenceTests(unittest.TestCase):
    def test_workspace_payload_records_provenance(self) -> None:
        payload = promptspkg.workspace_payload(
            {"id": "sample"}, BRIEF_NO_SONG, "stil-test"
        )
        self.assertEqual(payload["generator"], "workspace_ai")
        self.assertEqual(
            payload["source_hash"], campaignpkg.source_hash(BRIEF_NO_SONG)
        )
        self.assertEqual(payload["prompt_version"], promptspkg.PROMPT_VERSION)
        self.assertEqual(payload["texts"], {})

    def test_prompt_file_and_workspace_order_are_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "books" / "sample").mkdir(parents=True)
            book = {
                "id": "sample",
                "work_dir": "books/sample/work",
                "exports_dir": "books/sample/exports",
                "book_root": "books/sample",
            }
            system, user = promptspkg.build_prompt(BRIEF_NO_SONG)
            prompt_path = promptspkg.write_prompt_file(
                book, root, "stil-test", BRIEF_NO_SONG, system, user
            )
            self.assertTrue(prompt_path.is_file())
            self.assertEqual(
                prompt_path.relative_to(root).as_posix(),
                "books/sample/work/prompts/marketing/sample-marketing-stil-test.md",
            )
            self.assertIn(
                campaignpkg.source_hash(BRIEF_NO_SONG),
                prompt_path.read_text(encoding="utf-8"),
            )

            order_path = promptspkg.write_workspace_order(
                book, root, "stil-test", BRIEF_NO_SONG, system, user
            )
            self.assertEqual(
                order_path.relative_to(root).as_posix(),
                "books/sample/work/marketing/generation-request.md",
            )

            generated = promptspkg.write_generated(
                book,
                root,
                promptspkg.workspace_payload(book, BRIEF_NO_SONG, "stil-test"),
            )
            self.assertEqual(
                generated.relative_to(root).as_posix(),
                "books/sample/work/marketing/generated.json",
            )
            data = json.loads(generated.read_text(encoding="utf-8"))
            self.assertEqual(data["book_id"], "sample")


if __name__ == "__main__":
    unittest.main()
