from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import generate_illustration as gi  # noqa: E402
from lib.book_project import find_book, write_yaml  # noqa: E402


class GenerateIllustrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.old_repo_root = gi.REPO_ROOT
        gi.REPO_ROOT = self.root
        self.addCleanup(self.cleanup)
        self.book_root = self.root / "books" / "peter-i-buch-01"
        write_yaml(
            self.book_root / "book.yaml",
            {
                "id": "peter-i-buch-01",
                "title": "Peter der Erste",
                "author": "Alexei Tolstoi",
                "source_path": "source/peter.rtf",
                "source_lang": "ru",
                "target_lang": "de",
                "style_mode": "stil-02-poetisch",
                "higgsfield": {
                    "model": "text2image_soul_v2",
                    "aspect_ratio": "3:4",
                    "quality": "2k",
                    "moodboard": {
                        "name": "Buch Peter der Erste",
                        "custom_reference_id": "11111111-1111-4111-8111-111111111111",
                    },
                },
            },
        )
        de_scene = (
            self.book_root
            / "work"
            / "scenes"
            / "de"
            / "stil-02-poetisch"
            / "001"
            / "scene-01.md"
        )
        de_scene.parent.mkdir(parents=True, exist_ok=True)
        de_scene.write_text(
            "## Szene 1\n\nSanka steht im Schnee vor der schwarzen Izba.",
            encoding="utf-8",
        )

    def cleanup(self) -> None:
        gi.REPO_ROOT = self.old_repo_root
        self.tmp.cleanup()

    def request(self, **overrides) -> gi.IllustrationRequest:
        data = {
            "book_id": "peter-i-buch-01",
            "chapter_id": "001",
            "scene_number": 1,
            "style": "stil-02-poetisch",
            "kind": "scene",
            "model": gi.DEFAULT_MODEL,
            "moodboard": gi.DEFAULT_MOODBOARD,
            "images": (),
            "no_reference": False,
            "aspect_ratio": gi.DEFAULT_ASPECT_RATIO,
            "quality": gi.DEFAULT_QUALITY,
            "overwrite": False,
        }
        data.update(overrides)
        return gi.IllustrationRequest(**data)

    def test_scene_output_path_uses_export_convention(self) -> None:
        book = find_book(self.root, "peter-i-buch-01")
        path = gi.output_image_path(book, self.request())
        self.assertEqual(
            path,
            self.book_root / "assets" / "scene" / "001" / "scene-001.jpg",
        )

    def test_chapter_output_path_uses_export_convention(self) -> None:
        book = find_book(self.root, "peter-i-buch-01")
        path = gi.output_image_path(
            book,
            self.request(kind="chapter", scene_number=None),
        )
        self.assertEqual(
            path,
            self.book_root / "assets" / "chapter" / "chapter-001.jpg",
        )

    def test_dry_run_writes_prompt_and_metadata_without_image(self) -> None:
        prompt_path, meta_path, image_path = gi.generate_illustration(
            self.request(),
            dry_run=True,
        )

        self.assertTrue(prompt_path.exists())
        self.assertTrue(meta_path.exists())
        self.assertFalse(image_path.exists())
        prompt = prompt_path.read_text(encoding="utf-8")
        self.assertIn("Image for Peter der Erste, chapter 001, scene 01", prompt)
        self.assertIn("No readable text", prompt)
        self.assertNotIn("Cinematic realism", prompt)
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        self.assertTrue(meta["dry_run"])
        self.assertFalse(meta["schema_checked"])
        self.assertEqual(meta["output_path"], str(image_path))

    def test_higgsfield_defaults_are_read_from_book_config(self) -> None:
        book = find_book(self.root, "peter-i-buch-01")
        defaults = gi.higgsfield_defaults(book)

        self.assertEqual(defaults["model"], "text2image_soul_v2")
        self.assertEqual(defaults["aspect_ratio"], "3:4")
        self.assertEqual(defaults["quality"], "2k")
        self.assertEqual(
            defaults["moodboard"],
            "11111111-1111-4111-8111-111111111111",
        )

    def test_existing_image_is_not_overwritten_without_flag(self) -> None:
        book = find_book(self.root, "peter-i-buch-01")
        image_path = gi.output_image_path(book, self.request())
        image_path.parent.mkdir(parents=True)
        image_path.write_bytes(b"old image")

        with self.assertRaises(SystemExit):
            gi.generate_illustration(self.request(), dry_run=True)

    def test_schema_failure_keeps_prompt_files(self) -> None:
        request = self.request(
            moodboard="11111111-1111-4111-8111-111111111111",
        )
        with patch.object(
            gi,
            "validate_moodboard_support",
            side_effect=SystemExit("kein Moodboard-Feld"),
        ):
            with self.assertRaises(SystemExit):
                gi.generate_illustration(request, dry_run=False)

        prompt_path = (
            self.book_root
            / "work"
            / "prompts"
            / "higgsfield"
            / "001-scene-01-stil-02-poetisch.md"
        )
        meta_path = prompt_path.with_suffix(".json")
        self.assertTrue(prompt_path.exists())
        self.assertTrue(meta_path.exists())
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        self.assertFalse(meta["schema_checked"])
        self.assertFalse(meta["dry_run"])

    def test_share_link_without_uuid_or_image_is_rejected_after_prompt_write(self) -> None:
        with self.assertRaises(SystemExit):
            gi.generate_illustration(self.request(), dry_run=False)

        prompt_path = (
            self.book_root
            / "work"
            / "prompts"
            / "higgsfield"
            / "001-scene-01-stil-02-poetisch.md"
        )
        meta_path = prompt_path.with_suffix(".json")
        self.assertTrue(prompt_path.exists())
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        self.assertEqual(meta["moodboard"], gi.DEFAULT_MOODBOARD)
        self.assertFalse(meta["schema_checked"])

    def test_run_json_command_parses_subprocess_stdout(self) -> None:
        completed = SimpleNamespace(
            returncode=0,
            stdout='{"params": [{"name": "moodboard_id"}]}',
            stderr="",
        )
        with patch.object(gi.subprocess, "run", return_value=completed):
            data = gi.run_json_command(["higgsfield", "model", "get", "x", "--json"])

        self.assertEqual(data["params"][0]["name"], "moodboard_id")

    def test_real_generation_flow_uses_mocked_higgsfield_and_download(self) -> None:
        def fake_download(url: str, destination: Path) -> None:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(f"downloaded from {url}".encode("utf-8"))

        with (
            patch.object(gi, "validate_moodboard_support", return_value=("--moodboard_id", {})),
            patch.object(gi, "run_json_command", return_value=[{"image_url": "https://example.test/image.jpg"}]) as run_json,
            patch.object(gi, "download_url", side_effect=fake_download),
        ):
            _prompt_path, meta_path, image_path = gi.generate_illustration(
                self.request(moodboard="11111111-1111-4111-8111-111111111111"),
                dry_run=False,
            )

        self.assertTrue(image_path.exists())
        self.assertIn(b"https://example.test/image.jpg", image_path.read_bytes())
        command = run_json.call_args.args[0]
        self.assertIn("--moodboard_id", command)
        self.assertIn("11111111-1111-4111-8111-111111111111", command)
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        self.assertFalse(meta["dry_run"])
        self.assertTrue(meta["schema_checked"])
        self.assertEqual(meta["media_url"], "https://example.test/image.jpg")

    def test_real_generation_flow_accepts_image_references_without_moodboard_schema(self) -> None:
        image_ref = "22222222-2222-4222-8222-222222222222"

        def fake_download(url: str, destination: Path) -> None:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(b"image")

        with (
            patch.object(gi, "validate_higgsfield_available"),
            patch.object(gi, "validate_moodboard_support") as moodboard_schema,
            patch.object(gi, "run_json_command", return_value={"result_url": "https://example.test/image.jpg"}) as run_json,
            patch.object(gi, "download_url", side_effect=fake_download),
        ):
            _prompt_path, meta_path, image_path = gi.generate_illustration(
                self.request(images=(image_ref,)),
                dry_run=False,
            )

        self.assertTrue(image_path.exists())
        moodboard_schema.assert_not_called()
        command = run_json.call_args.args[0]
        self.assertIn("--image", command)
        self.assertIn(image_ref, command)
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        self.assertEqual(meta["images"], [image_ref])

    def test_no_reference_generation_skips_reference_validation(self) -> None:
        def fake_download(url: str, destination: Path) -> None:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(b"image")

        with (
            patch.object(gi, "validate_higgsfield_available"),
            patch.object(gi, "validate_moodboard_support") as moodboard_schema,
            patch.object(gi, "run_json_command", return_value={"result_url": "https://example.test/image.jpg"}) as run_json,
            patch.object(gi, "download_url", side_effect=fake_download),
        ):
            _prompt_path, meta_path, image_path = gi.generate_illustration(
                self.request(no_reference=True),
                dry_run=False,
            )

        self.assertTrue(image_path.exists())
        moodboard_schema.assert_not_called()
        command = run_json.call_args.args[0]
        self.assertNotIn("--image", command)
        self.assertNotIn("--custom_reference_id", command)
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        self.assertTrue(meta["no_reference"])


if __name__ == "__main__":
    unittest.main()
