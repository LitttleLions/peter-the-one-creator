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
from lib.illustration_vignette import (  # noqa: E402
    Figure,
    Vignette,
    VignetteError,
    build_heuristic_vignette,
    ensure_vignette,
    parse_vignette_payload,
    vignette_path,
)


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
                        "web_ui_moodboard_id": "11111111-1111-4111-8111-111111111111",
                        "availability": "web_ui_only",
                        "strength": 1.0,
                    },
                    "reference_images": [
                        "books/peter-i-buch-01/assets/reference/style-01.jpg"
                    ],
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

    def test_gpt_image_rejects_soul_15k_resolution(self) -> None:
        from lib.higgsfield_models import normalize_size_value, size_cli_args

        self.assertEqual(normalize_size_value("gpt_image_2", "1.5k"), "2k")
        self.assertEqual(
            size_cli_args("gpt_image_2", "1.5k", "medium"),
            ["--resolution", "2k", "--quality", "medium"],
        )

    def test_chapter_prompt_prefers_de_scene_over_source(self) -> None:
        chapter_src = self.book_root / "work" / "chapters" / "001-source.md"
        chapter_src.parent.mkdir(parents=True, exist_ok=True)
        chapter_src.write_text(
            "*Buch: Aëlita*\n\nНа пустыре перед мастерской.\n",
            encoding="utf-8",
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
            "Auf dem Brachland vor Los' Werkstatt versammelte sich Volk.\n",
            encoding="utf-8",
        )
        book = find_book(self.root, "peter-i-buch-01")
        path = gi.preferred_scene_path(
            book,
            self.request(kind="chapter", scene_number=None),
        )
        self.assertEqual(path, de_scene)

    def test_command_for_log_hides_prompt_body(self) -> None:
        logged = gi._command_for_log(
            ["higgsfield", "generate", "create", "x", "--prompt", "ä" * 200, "--json"]
        )
        self.assertIn("<prompt 200 chars>", logged)
        self.assertNotIn("ääää", logged)

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
            "id": "aelita",
            "illustration_setting": (
                "Post-revolutionary Petrograd 1920s and ancient Mars civilisation."
            )
        }

        prompt = gi.build_prompt(book, self.request(), source)

        self.assertNotIn("Buch:", prompt)
        self.assertNotIn("status:", prompt)
        self.assertIn("Das Schiff flog niedrig ueber den Mars", prompt)
        self.assertIn("Post-revolutionary Petrograd", prompt)
        self.assertIn("Chapter 001 Scene 01.", prompt)
        self.assertNotIn("TRACKING", prompt)
        self.assertNotIn("Pure pictorial", prompt)
        self.assertNotIn("title=", prompt)

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

    def test_excerpt_keeps_short_motto_out_but_retains_body(self) -> None:
        source = (
            "## Szene 1\n\n"
            "> „Dinge und Taten, die nicht aufgezeichnet sind…“\n\n"
            "Ich wurde vor einem halben Jahrhundert geboren, im mittleren Russland.\n"
        )
        excerpt = gi.clean_markdown_excerpt(source)
        self.assertNotIn("Dinge und Taten", excerpt)
        self.assertIn("Ich wurde vor einem halben Jahrhundert geboren", excerpt)

    def test_excerpt_keeps_narrative_wrapped_entirely_in_blockquotes(self) -> None:
        source = (
            "## Szene 1\n\n"
            "> Das erste Erinnerungsbild, das ich habe, ist etwas Kleinliches.\n\n"
            "> Meine Kindheit erinnere ich mich mit Trauer. Jede Kindheit ist traurig.\n\n"
            "> Vielleicht war meine Kindheit traurig aus einigen besonderen Umstaenden?\n"
        )
        excerpt = gi.clean_markdown_excerpt(source)
        self.assertIn("Das erste Erinnerungsbild", excerpt)
        self.assertIn("Meine Kindheit erinnere ich mich mit Trauer", excerpt)
        self.assertNotIn(">", excerpt)
        # Only the first two narrative paragraphs – longer dumps become storyboards.
        self.assertNotIn("Vielleicht war meine Kindheit", excerpt)

    def test_excerpt_limits_to_two_paragraphs_to_avoid_storyboards(self) -> None:
        source = "\n\n".join([
            "Erster Moment am Fluss im Abendlicht.",
            "Zweiter Moment im Gutshofgarten.",
            "Dritter Moment mit dem Vater am Tisch.",
            "Vierter Moment bei der Kinderfrau.",
            "Fuenfter Moment auf der Jagd.",
            "Sechster Moment mit der Gitarre.",
        ])
        excerpt = gi.clean_markdown_excerpt(source)
        self.assertIn("Erster Moment", excerpt)
        self.assertIn("Zweiter Moment", excerpt)
        self.assertNotIn("Dritter Moment", excerpt)
        self.assertNotIn("Sechster Moment", excerpt)

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
        self.assertEqual(defaults["moodboard_availability"], "web_ui_only")
        self.assertEqual(
            defaults["reference_images"],
            ("books/peter-i-buch-01/assets/reference/style-01.jpg",),
        )

    def test_existing_image_blocks_real_run_without_flag(self) -> None:
        book = find_book(self.root, "peter-i-buch-01")
        image_path = gi.output_image_path(book, self.request())
        image_path.parent.mkdir(parents=True)
        image_path.write_bytes(b"old image")

        with self.assertRaises(SystemExit):
            gi.generate_illustration(self.request(), dry_run=False)
        self.assertEqual(image_path.read_bytes(), b"old image")

    def test_existing_image_does_not_block_dry_run(self) -> None:
        book = find_book(self.root, "peter-i-buch-01")
        image_path = gi.output_image_path(book, self.request())
        image_path.parent.mkdir(parents=True)
        image_path.write_bytes(b"old image")

        gi.generate_illustration(self.request(), dry_run=True)
        self.assertEqual(image_path.read_bytes(), b"old image")

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

    def test_web_ui_moodboard_api_backend_blocks_before_paid_generation(self) -> None:
        request = self.request(
            moodboard="11111111-1111-4111-8111-111111111111",
            backend="api",
        )
        with (
            patch.object(gi, "discover_higgsfield_style") as discover,
            patch.object(gi, "run_higgsfield_api_adapter") as adapter,
        ):
            with self.assertRaises(SystemExit) as ctx:
                gi.generate_illustration(request, dry_run=False)

        self.assertIn("HIGGSFIELD_WEB_UI_MOODBOARD_NOT_PROGRAMMATIC", str(ctx.exception))
        discover.assert_not_called()
        adapter.assert_not_called()

    def test_api_backend_without_web_ui_moodboard_requires_paid_flag(self) -> None:
        request = self.request(
            backend="api",
            no_reference=True,
            moodboard="",
        )
        with patch.object(
            gi,
            "run_higgsfield_api_adapter",
            return_value={
                "ok": True,
                "request_payload": {"style_id": None, "soul_id": None},
            },
        ) as adapter:
            with self.assertRaises(SystemExit) as ctx:
                gi.generate_illustration(request, dry_run=False)

        self.assertIn("HIGGSFIELD_API_PAID_GENERATION_NOT_ALLOWED", str(ctx.exception))
        payloads = [call.args[0] for call in adapter.call_args_list]
        self.assertTrue(all(payload.get("dry_run") for payload in payloads))

    def test_api_backend_dry_run_omits_web_ui_moodboard_style_id(self) -> None:
        request = self.request(
            backend="api",
            no_reference=True,
            moodboard="11111111-1111-4111-8111-111111111111",
        )
        with patch.object(
            gi,
            "run_higgsfield_api_adapter",
            return_value={
                "ok": True,
                "request_payload": {
                    "style_id": None,
                    "style_strength": None,
                },
            },
        ) as adapter:
            _prompt_path, meta_path, _image_path = gi.generate_illustration(
                request,
                dry_run=True,
            )

        payload = adapter.call_args.args[0]
        self.assertIsNone(payload["style_id"])
        self.assertNotIn("custom_reference_id", payload)
        self.assertIsNone(payload["soul_id"])
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        self.assertIsNone(meta["api_dry_run_request"]["style_id"])
        self.assertNotIn("custom_reference_id", meta["api_dry_run_request"])

    def test_api_backend_keeps_soul_id_separate_from_web_ui_moodboard(self) -> None:
        request = self.request(
            moodboard="11111111-1111-4111-8111-111111111111",
            backend="api",
            no_reference=True,
            soul_id="22222222-2222-4222-8222-222222222222",
            soul_strength=0.75,
        )
        with patch.object(
            gi,
            "run_higgsfield_api_adapter",
            return_value={
                "ok": True,
                "request_payload": {
                    "style_id": None,
                    "custom_reference_id": request.soul_id,
                },
            },
        ) as adapter:
            gi.generate_illustration(request, dry_run=True)

        payload = adapter.call_args.args[0]
        self.assertIsNone(payload["style_id"])
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

    def test_cli_generation_passes_soul_id_as_custom_reference(self) -> None:
        soul_id = "22222222-2222-4222-8222-222222222222"

        def fake_download(url: str, destination: Path,
                          image_processing=None) -> None:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(b"image")

        with (
            patch.object(gi, "validate_higgsfield_available"),
            patch.object(gi, "run_json_command", return_value={"result_url": "https://example.test/image.jpg"}) as run_json,
            patch.object(gi, "download_url", side_effect=fake_download),
        ):
            gi.generate_illustration(
                self.request(no_reference=True, soul_id=soul_id),
                dry_run=False,
            )

        command = run_json.call_args.args[0]
        self.assertIn("--custom_reference_id", command)
        self.assertEqual(command[command.index("--custom_reference_id") + 1], soul_id)

    def test_web_ui_moodboard_auto_does_not_select_api_or_custom_reference(self) -> None:
        request = self.request(moodboard="11111111-1111-4111-8111-111111111111")
        self.assertEqual(gi.selected_backend(request), "cli")
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

        adapter.assert_not_called()
        run_json.assert_not_called()

    def test_flag_is_soul_reference_detects_custom_reference_id(self) -> None:
        self.assertTrue(gi._flag_is_soul_reference("--custom_reference_id"))
        self.assertTrue(gi._flag_is_soul_reference("--Custom_Reference_Id"))
        self.assertFalse(gi._flag_is_soul_reference("--style_id"))
        self.assertFalse(gi._flag_is_soul_reference("--moodboard_id"))

    def test_diagnose_reports_web_ui_moodboard_as_not_programmatic(self) -> None:
        schema = {"params": [{"name": "custom_reference_id"}]}
        with (
            patch.object(gi, "higgsfield_executable", return_value="higgsfield"),
            patch.object(gi, "run_json_command", return_value=schema) as run_json,
        ):
            diagnostic = gi.diagnose_higgsfield_reference(
                "text2image_soul_v2",
                "11111111-1111-4111-8111-111111111111",
            )

        run_json.assert_not_called()
        self.assertFalse(diagnostic["can_use_moodboard"])
        self.assertEqual(diagnostic["programmatic_support"], "no")
        self.assertEqual(diagnostic["status"], "web_ui_moodboard_only")
        self.assertIn("Web-UI-Moodboards", diagnostic["reason"])

    def test_diagnose_reports_non_uuid_schema_style_id_as_supported(self) -> None:
        schema = {"params": [{"name": "style_id"}, {"name": "custom_reference_id"}]}
        with (
            patch.object(gi, "higgsfield_executable", return_value="higgsfield"),
            patch.object(gi, "run_json_command", return_value=schema),
        ):
            diagnostic = gi.diagnose_higgsfield_reference(
                "text2image_soul_v2",
                "",
            )

        self.assertTrue(diagnostic["can_use_moodboard"])
        self.assertEqual(diagnostic["selected_flag"], "--style_id")
        self.assertEqual(diagnostic["status"], "moodboard_supported")

    def test_download_url_retries_after_connection_reset(self) -> None:
        from io import BytesIO

        from PIL import Image

        buffer = BytesIO()
        Image.new("RGB", (8, 8), "white").save(buffer, format="PNG")
        payload = buffer.getvalue()
        calls = {"count": 0}

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *exc_info):
                return False

            def read(self):
                return payload

        def fake_urlopen(*args, **kwargs):
            calls["count"] += 1
            if calls["count"] < 3:
                raise gi.urllib.error.URLError("reset")
            return FakeResponse()

        target = self.book_root / "assets" / "chapter" / "retry.jpg"
        with (
            patch.object(gi.urllib.request, "urlopen", side_effect=fake_urlopen),
            patch.object(gi.time, "sleep"),
        ):
            gi.download_url("https://example.test/image.png", target)

        self.assertEqual(calls["count"], 3)
        self.assertTrue(target.exists())

    def test_diagnose_reports_missing_cli_without_schema_call(self) -> None:
        with (
            patch.object(gi, "higgsfield_executable", return_value=None),
            patch.object(gi, "run_json_command") as run_json,
        ):
            diagnostic = gi.diagnose_higgsfield_reference(
                "text2image_soul_v2",
                "",
            )

        run_json.assert_not_called()
        self.assertFalse(diagnostic["schema_checked"])
        self.assertEqual(diagnostic["status"], "cli_missing")


CHAPTER_TEXT = (
    "## Die Ketten an den Kähnen\n\n"
    "Der Schlamm vor dem Wassertor roch nach altem Schnee und Pferdemist.\n\n"
    "Raginbert hatte den Zins auf das Holz gelegt, so sagte man am Kai.\n\n"
    "Ihre drei größten Lastkähne lagen mit fingerdicken Eisenketten am "
    "Bollwerk, und Isenbart stand oben auf dem Dammweg. »Wer hat euch "
    "geheißen, mein Holz an die Mauer zu ketten?«, fragte Alda.\n\n"
    "Der Vogt zuckte die Achseln.\n"
)

NAMES_YAML = """entries:
- source: Alda
  target: Alda
  aliases: []
  type: person
  status: draft
  visual: 40-jährige Frau in gefettetem Wollmantel
- source: Raginbert
  target: Raginbert
  aliases: []
  type: person
  status: draft
  visual: Grundherr im blauen Mantel mit Fuchspelz
- source: Isenbart
  target: Isenbart
  aliases: []
  type: person
  status: draft
  visual: Vogt im dunkelblauen Wollmantel mit Marderfell
"""


class VignettePromptTests(unittest.TestCase):
    """Vignetten-Stufe: Moment zuerst, Stil zuletzt, nur anwesende Figuren."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.old_repo_root = gi.REPO_ROOT
        gi.REPO_ROOT = self.root
        self.addCleanup(self.cleanup)
        self.book_root = self.root / "books" / "die-sprache-des-anderen"
        write_yaml(
            self.book_root / "book.yaml",
            {
                "id": "die-sprache-des-anderen",
                "title": "Die Sprache des Anderen",
                "author": "Timo Verita",
                "source_lang": "de",
                "target_lang": "de",
                "style_mode": "stil-01-original",
                "illustration_setting": (
                    "Cinematic painterly realism, cold winter light."
                ),
                "illustration_world": "Wool, linen, iron chains.",
                "higgsfield": {
                    "model": "gpt_image_2_5",
                    "aspect_ratio": "3:4",
                    "quality": "1k",
                },
            },
        )
        scene = (
            self.book_root
            / "work"
            / "scenes"
            / "de"
            / "stil-01-original"
            / "001"
            / "scene-01.md"
        )
        scene.parent.mkdir(parents=True, exist_ok=True)
        scene.write_text(CHAPTER_TEXT, encoding="utf-8")
        (self.book_root / "names.yaml").write_text(NAMES_YAML, encoding="utf-8")

    def cleanup(self) -> None:
        gi.REPO_ROOT = self.old_repo_root
        self.tmp.cleanup()

    def book(self) -> dict:
        return find_book(self.root, "die-sprache-des-anderen")

    def request(self, **overrides) -> gi.IllustrationRequest:
        data = {
            "book_id": "die-sprache-des-anderen",
            "chapter_id": "001",
            "scene_number": None,
            "style": "stil-01-original",
            "kind": "chapter",
            "model": "gpt_image_2_5",
            "moodboard": gi.DEFAULT_MOODBOARD,
            "images": (),
            "no_reference": True,
            "aspect_ratio": "3:4",
            "quality": "1k",
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

    def vignette(self, **overrides) -> Vignette:
        data = {
            "chapter": "001",
            "moment": "Alda packt die Eisenkette am Bug der Schwalbe.",
            "title": "Die Ketten an den Kähnen",
            "figures": [
                Figure(name="Alda", action="Hand um die Kette"),
                Figure(name="Isenbart", action="hält das gesiegelte Leder"),
            ],
            "props": ["Eisenkette", "Pergament mit Wachssiegel"],
            "composition": "medium shot",
            "beat": "Konfrontation",
            "evidence": [2],
            "source": "manual",
        }
        data.update(overrides)
        return Vignette(**data)

    def test_prompt_puts_moment_first_and_style_last(self) -> None:
        prompt = gi.build_prompt(
            self.book(), self.request(), CHAPTER_TEXT, vignette=self.vignette()
        )

        self.assertTrue(
            prompt.startswith("Alda packt die Eisenkette am Bug der Schwalbe.")
        )
        self.assertIn("Figuren: Alda", prompt)
        self.assertIn("Isenbart", prompt)
        self.assertIn("Gegenstände: Eisenkette", prompt)
        self.assertIn("Bildausschnitt: medium shot", prompt)
        self.assertTrue(prompt.lower().endswith("cold winter light."))
        # Kein Tracking-Header und keine Figurenliste aus dem Glossar.
        self.assertNotIn("Chapter 001", prompt)
        self.assertNotIn("Raginbert", prompt)
        self.assertNotIn("Fuchspelz", prompt)

    def test_prompt_stays_short_with_default_anchors(self) -> None:
        prompt = gi.build_prompt(
            self.book(), self.request(), CHAPTER_TEXT, vignette=self.vignette()
        )

        self.assertLess(len(prompt), 900)

    def test_style_anchor_is_capped_at_budget(self) -> None:
        book = self.book()
        book["illustration_setting"] = "A" * 5000 + " ENDMARKER"
        prompt = gi.build_prompt(
            book, self.request(), CHAPTER_TEXT, vignette=self.vignette()
        )

        self.assertNotIn("ENDMARKER", prompt)
        self.assertLessEqual(
            len(prompt), len(self.vignette().moment) + gi.PROMPT_STYLE_LIMIT + 400
        )

    def test_legacy_prompt_keeps_tracking_header_without_vignette(self) -> None:
        prompt = gi.build_prompt(self.book(), self.request(), CHAPTER_TEXT)

        self.assertIn("Chapter 001.", prompt)
        self.assertIn("Cinematic painterly realism", prompt)

    def test_heuristic_vignette_prefers_paragraph_matching_title(self) -> None:
        vignette = build_heuristic_vignette(
            text=CHAPTER_TEXT,
            entries=[
                {"source": "Alda", "target": "Alda", "type": "person"},
                {"source": "Raginbert", "target": "Raginbert", "type": "person"},
                {"source": "Isenbart", "target": "Isenbart", "type": "person"},
            ],
            chapter_id="001",
        )

        self.assertEqual(vignette.evidence, [2])
        self.assertIn("Eisenketten", vignette.moment)
        names = [figure.name for figure in vignette.figures]
        self.assertIn("Isenbart", names)
        self.assertIn("Alda", names)
        # Raginbert wird im Kapitel nur erwaehnt, nicht gezeigt.
        self.assertNotIn("Raginbert", names)
        self.assertEqual(vignette.source, "heuristic")
        self.assertTrue(vignette.text_sha256)

    def test_vignette_payload_requires_moment_and_clips_long_text(self) -> None:
        with self.assertRaises(VignetteError):
            parse_vignette_payload({"figures": []}, chapter_id="001")

        vignette = parse_vignette_payload(
            {"moment": "Wort " * 200, "composition": "close-up"},
            chapter_id="001",
        )
        self.assertLessEqual(len(vignette.moment), 300)

    def test_ensure_vignette_writes_json_and_reuses_it(self) -> None:
        book = self.book()
        text = CHAPTER_TEXT
        first = ensure_vignette(
            repo_root=self.root, book=book, chapter_id="001", text=text,
            provider="auto",
        )
        path = vignette_path(self.root / book["work_dir"], "001")
        self.assertTrue(path.exists())

        second = ensure_vignette(
            repo_root=self.root, book=book, chapter_id="001", text=text,
            provider="auto",
        )
        self.assertEqual(first.moment, second.moment)
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["moment"], first.moment)
        self.assertEqual(payload["source"], "heuristic")

    def test_dry_run_uses_vignette_and_keeps_real_prompt_file(self) -> None:
        request = self.request(vignette_provider="auto")
        prompt_path, meta_path, image_path = gi.generate_illustration(
            request, dry_run=True
        )

        self.assertTrue(prompt_path.name.endswith("-dryrun.md"))
        self.assertFalse((prompt_path.parent / prompt_path.name.replace("-dryrun", "")).exists())
        self.assertFalse(image_path.exists())
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        self.assertEqual(meta["prompt_builder"], "vignette")
        self.assertTrue(Path(meta["vignette_path"]).exists())

    def test_vignette_off_keeps_legacy_prompt_builder(self) -> None:
        prompt_path, meta_path, _ = gi.generate_illustration(
            self.request(vignette_provider="off"), dry_run=True
        )

        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        self.assertEqual(meta["prompt_builder"], "legacy")
        prompt = prompt_path.read_text(encoding="utf-8")
        self.assertIn("Chapter 001.", prompt)
        self.assertNotIn("Vignette", prompt)


if __name__ == "__main__":
    unittest.main()
