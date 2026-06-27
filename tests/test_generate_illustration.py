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
                        "style_id": "11111111-1111-4111-8111-111111111111",
                        "strength": 1.0,
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
            "backend": "auto",
            "moodboard_name": None,
            "moodboard_strength": 1.0,
            "soul_id": None,
            "soul_strength": 1.0,
            "allow_paid_generation": False,
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

    def test_aspect_ratio_normalizes_semicolon_typo(self) -> None:
        self.assertEqual(gi.normalize_aspect_ratio("3;4"), "3:4")
        self.assertEqual(gi.normalize_aspect_ratio("3 : 4"), "3:4")

    def test_aspect_ratio_rejects_invalid_value(self) -> None:
        with self.assertRaises(SystemExit):
            gi.normalize_aspect_ratio("hochformat")

    def test_dry_run_writes_prompt_and_metadata_without_image(self) -> None:
        prompt_path, meta_path, image_path = gi.generate_illustration(
            self.request(),
            dry_run=True,
        )

        self.assertTrue(prompt_path.exists())
        self.assertTrue(meta_path.exists())
        self.assertFalse(image_path.exists())
        prompt = prompt_path.read_text(encoding="utf-8")
        self.assertIn("Sanka steht im Schnee vor der schwarzen Izba", prompt)
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        self.assertTrue(meta["dry_run"])
        self.assertFalse(meta["schema_checked"])
        self.assertEqual(meta["output_path"], str(image_path))

    def test_prompt_filters_book_status_header_but_keeps_setting(self) -> None:
        source = (
            "*Buch: Aëlita* <!-- status: pending --> "
            "Das Schiff flog niedrig ueber den Mars.\n\n"
            "Rote Ebenen lagen unter ihm."
        )
        book = {
            "illustration_setting": (
                "Post-revolutionary Petrograd 1920s and ancient Mars civilisation."
            )
        }

        prompt = gi.build_prompt(book, self.request(), source)

        self.assertNotIn("Buch:", prompt)
        self.assertNotIn("status:", prompt)
        self.assertIn("Das Schiff flog niedrig ueber den Mars", prompt)
        self.assertIn("Post-revolutionary Petrograd", prompt)

    def test_prompt_filters_split_book_status_header(self) -> None:
        source = (
            "*Buch: Aëlita*\n"
            "<!-- status: pending -->\n\n"
            "Das Schiff flog niedrig ueber den Mars."
        )

        excerpt = gi.clean_markdown_excerpt(source)

        self.assertNotIn("Buch:", excerpt)
        self.assertNotIn("status:", excerpt)
        self.assertEqual(excerpt, "Das Schiff flog niedrig ueber den Mars.")

    def test_prompt_adds_visual_descriptions_for_present_characters(self) -> None:
        names_path = self.book_root / "names.yaml"
        names_path.write_text(
            "\n".join([
                "entries:",
                "- source: Санка",
                "  target: Sanka",
                "  aliases: [Sanka]",
                "  type: person",
                "  status: approved",
                "  visual: Schmaler junger Mann, wettergegerbtes Gesicht, dunkler Kaftan.",
                "- source: Пётр",
                "  target: Peter",
                "  aliases: [Peter]",
                "  type: person",
                "  status: approved",
                "  visual: Sehr grosser junger Zar mit wachem Blick.",
            ]),
            encoding="utf-8",
        )
        book = find_book(self.root, "peter-i-buch-01")

        prompt = gi.build_prompt(
            book,
            self.request(),
            "Sanka steht im Schnee vor der schwarzen Izba.",
        )

        self.assertIn("Characters present: Sanka:", prompt)
        self.assertIn("wettergegerbtes Gesicht", prompt)
        self.assertNotIn("Sehr grosser junger Zar", prompt)

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
        self.assertEqual(defaults["backend"], "auto")

    def test_existing_image_is_not_overwritten_without_flag(self) -> None:
        book = find_book(self.root, "peter-i-buch-01")
        image_path = gi.output_image_path(book, self.request())
        image_path.parent.mkdir(parents=True)
        image_path.write_bytes(b"old image")

        with self.assertRaises(SystemExit):
            gi.generate_illustration(self.request(), dry_run=True)

    def test_moodboard_cli_backend_blocks_and_keeps_prompt_files(self) -> None:
        request = self.request(
            moodboard="11111111-1111-4111-8111-111111111111",
            backend="cli",
        )
        with patch.object(gi, "run_json_command") as run_json:
            with self.assertRaises(SystemExit):
                gi.generate_illustration(request, dry_run=False)
        run_json.assert_not_called()

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
        self.assertNotIn("--custom_reference_id", meta["command"])

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

    def test_moodboard_api_backend_without_allow_paid_generation_blocks(self) -> None:
        request = self.request(
            moodboard="11111111-1111-4111-8111-111111111111",
            backend="api",
        )
        with (
            patch.object(gi, "discover_higgsfield_style", return_value={"id": request.moodboard, "name": "Peter"}),
            patch.object(
                gi,
                "run_higgsfield_api_adapter",
                return_value={
                    "ok": True,
                    "request_payload": {
                        "style_id": request.moodboard,
                        "style_strength": 1.0,
                    },
                },
            ) as adapter,
        ):
            with self.assertRaises(SystemExit) as ctx:
                gi.generate_illustration(request, dry_run=False)

        self.assertIn("HIGGSFIELD_API_PAID_GENERATION_NOT_ALLOWED", str(ctx.exception))
        payloads = [call.args[0] for call in adapter.call_args_list]
        self.assertTrue(all(payload.get("dry_run") for payload in payloads))

    def test_moodboard_api_backend_style_not_found_blocks_before_generate(self) -> None:
        request = self.request(
            moodboard="11111111-1111-4111-8111-111111111111",
            backend="api",
        )
        with (
            patch.object(gi, "discover_higgsfield_style", return_value=None),
            patch.object(gi, "run_higgsfield_api_adapter") as adapter,
        ):
            with self.assertRaises(SystemExit) as ctx:
                gi.generate_illustration(request, dry_run=False)

        self.assertIn("HIGGSFIELD_API_STYLE_NOT_FOUND", str(ctx.exception))
        adapter.assert_not_called()

    def test_moodboard_api_backend_dry_run_uses_style_id_only(self) -> None:
        request = self.request(
            moodboard="11111111-1111-4111-8111-111111111111",
            backend="api",
        )
        with patch.object(
            gi,
            "run_higgsfield_api_adapter",
            return_value={
                "ok": True,
                "request_payload": {
                    "style_id": request.moodboard,
                    "style_strength": 1.0,
                },
            },
        ) as adapter:
            _prompt_path, meta_path, _image_path = gi.generate_illustration(
                request,
                dry_run=True,
            )

        payload = adapter.call_args.args[0]
        self.assertEqual(payload["style_id"], request.moodboard)
        self.assertNotIn("custom_reference_id", payload)
        self.assertIsNone(payload["soul_id"])
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        self.assertEqual(meta["api_dry_run_request"]["style_id"], request.moodboard)
        self.assertNotIn("custom_reference_id", meta["api_dry_run_request"])

    def test_moodboard_api_backend_keeps_soul_id_separate(self) -> None:
        request = self.request(
            moodboard="11111111-1111-4111-8111-111111111111",
            backend="api",
            soul_id="22222222-2222-4222-8222-222222222222",
            soul_strength=0.75,
        )
        with patch.object(
            gi,
            "run_higgsfield_api_adapter",
            return_value={
                "ok": True,
                "request_payload": {
                    "style_id": request.moodboard,
                    "custom_reference_id": request.soul_id,
                },
            },
        ) as adapter:
            gi.generate_illustration(request, dry_run=True)

        payload = adapter.call_args.args[0]
        self.assertEqual(payload["style_id"], request.moodboard)
        self.assertEqual(payload["soul_id"], request.soul_id)

    def test_real_cli_generation_flow_uses_mocked_higgsfield_and_download(self) -> None:
        def fake_download(url: str, destination: Path,
                          image_processing=None) -> None:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(f"downloaded from {url}".encode("utf-8"))

        with (
            patch.object(gi, "validate_higgsfield_available"),
            patch.object(gi, "run_json_command", return_value=[{"image_url": "https://example.test/image.jpg"}]) as run_json,
            patch.object(gi, "download_url", side_effect=fake_download),
        ):
            _prompt_path, meta_path, image_path = gi.generate_illustration(
                self.request(no_reference=True, backend="auto"),
                dry_run=False,
            )

        self.assertTrue(image_path.exists())
        self.assertIn(b"https://example.test/image.jpg", image_path.read_bytes())
        command = run_json.call_args.args[0]
        self.assertNotIn("--custom_reference_id", command)
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        self.assertFalse(meta["dry_run"])
        self.assertTrue(meta["schema_checked"])
        self.assertEqual(meta["media_url"], "https://example.test/image.jpg")

    def test_real_generation_flow_accepts_image_references_without_moodboard_schema(self) -> None:
        image_ref = "22222222-2222-4222-8222-222222222222"

        def fake_download(url: str, destination: Path,
                          image_processing=None) -> None:
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
        def fake_download(url: str, destination: Path,
                          image_processing=None) -> None:
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

    def test_moodboard_auto_selects_api_not_cli_custom_reference(self) -> None:
        request = self.request(moodboard="11111111-1111-4111-8111-111111111111")
        self.assertEqual(gi.selected_backend(request), "api")
        with (
            patch.object(gi, "discover_higgsfield_style", return_value={"id": request.moodboard}),
            patch.object(
                gi,
                "run_higgsfield_api_adapter",
                return_value={"ok": True, "request_payload": {"style_id": request.moodboard}},
            ) as adapter,
            patch.object(gi, "run_json_command") as run_json,
        ):
            with self.assertRaises(SystemExit):
                gi.generate_illustration(request, dry_run=False)

        adapter.assert_called()
        run_json.assert_not_called()

    def test_flag_is_soul_reference_detects_custom_reference_id(self) -> None:
        self.assertTrue(gi._flag_is_soul_reference("--custom_reference_id"))
        self.assertTrue(gi._flag_is_soul_reference("--Custom_Reference_Id"))
        self.assertFalse(gi._flag_is_soul_reference("--style_id"))
        self.assertFalse(gi._flag_is_soul_reference("--moodboard_id"))

    def test_diagnose_reports_only_custom_reference_as_not_supported(self) -> None:
        schema = {"params": [{"name": "custom_reference_id"}]}
        with (
            patch.object(gi, "higgsfield_executable", return_value="higgsfield"),
            patch.object(gi, "run_json_command", return_value=schema) as run_json,
        ):
            diagnostic = gi.diagnose_higgsfield_reference(
                "text2image_soul_v2",
                "11111111-1111-4111-8111-111111111111",
            )

        command = run_json.call_args.args[0]
        self.assertEqual(command, ["higgsfield", "model", "get", "text2image_soul_v2", "--json"])
        self.assertFalse(diagnostic["can_use_moodboard"])
        self.assertTrue(diagnostic["only_custom_reference"])
        self.assertTrue(diagnostic["uses_custom_reference_fallback"])
        self.assertEqual(diagnostic["status"], "only_custom_reference_id")
        self.assertNotIn("generate", command)

    def test_diagnose_reports_style_id_as_supported(self) -> None:
        schema = {"params": [{"name": "style_id"}, {"name": "custom_reference_id"}]}
        with (
            patch.object(gi, "higgsfield_executable", return_value="higgsfield"),
            patch.object(gi, "run_json_command", return_value=schema),
        ):
            diagnostic = gi.diagnose_higgsfield_reference(
                "text2image_soul_v2",
                "11111111-1111-4111-8111-111111111111",
            )

        self.assertTrue(diagnostic["can_use_moodboard"])
        self.assertEqual(diagnostic["selected_flag"], "--style_id")
        self.assertEqual(diagnostic["status"], "moodboard_supported")

    def test_diagnose_reports_missing_cli_without_schema_call(self) -> None:
        with (
            patch.object(gi, "higgsfield_executable", return_value=None),
            patch.object(gi, "run_json_command") as run_json,
        ):
            diagnostic = gi.diagnose_higgsfield_reference(
                "text2image_soul_v2",
                "11111111-1111-4111-8111-111111111111",
            )

        run_json.assert_not_called()
        self.assertFalse(diagnostic["schema_checked"])
        self.assertEqual(diagnostic["status"], "cli_missing")


if __name__ == "__main__":
    unittest.main()
