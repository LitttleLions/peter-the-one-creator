from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib.workbench_api import (  # noqa: E402
    ExportOptions,
    NewBookOptions,
    ReviewOptions,
    TranslateBatchOptions,
    TranslateRunOptions,
    build_export_command,
    build_init_book_command,
    build_review_command,
    build_review_fixes_command,
    build_translate_batch_command,
    build_translate_chapter_command,
    count_export_illustrations,
    editable_name_rows,
    export_context,
    guess_title_author,
    load_export_meta,
    normalize_name_rows,
    review_context,
    translation_context,
    unregistered_sources,
)


class WorkbenchApiTests(unittest.TestCase):
    def test_build_translate_chapter_ollama_scene_command(self) -> None:
        cmd = build_translate_chapter_command(
            TranslateRunOptions(
                book_id="pharao",
                chapter="001",
                scene="01",
                style="stil",
                provider="ollama",
                ollama_model="gemma4:latest",
                chunk_char_limit=10000,
                overwrite=True,
            )
        )

        self.assertEqual(cmd[0], "tools/translate_chapter.py")
        self.assertIn("--book", cmd)
        self.assertIn("pharao", cmd)
        self.assertIn("--chapter", cmd)
        self.assertIn("001", cmd)
        self.assertIn("--style", cmd)
        self.assertIn("stil", cmd)
        self.assertIn("gemma4:latest", cmd)
        self.assertIn("--scene", cmd)
        self.assertIn("--overwrite", cmd)

    def test_build_translate_batch_range_dry_run(self) -> None:
        cmd = build_translate_batch_command(
            TranslateBatchOptions(
                book_id="pharao",
                style="stil",
                provider="openrouter",
                scope="Bereich",
                start_chapter="001",
                end_chapter="005",
                model="model-x",
                chunk_char_limit=9000,
                dry_run=True,
            )
        )

        self.assertIn("--from", cmd)
        self.assertIn("001", cmd)
        self.assertIn("--to", cmd)
        self.assertIn("005", cmd)
        self.assertIn("--dry-run", cmd)

    def test_build_review_ollama_command(self) -> None:
        cmd = build_review_command(
            ReviewOptions(
                book_id="pharao",
                style="stil",
                scope="Aktuelles Kapitel",
                chapter="004",
                llm="ollama",
                llm_scope="all",
                ollama_model="gemma4:latest",
                fail_on_errors=True,
            )
        )

        self.assertEqual(cmd[0], "tools/review_manuscript.py")
        self.assertIn("--book", cmd)
        self.assertIn("pharao", cmd)
        self.assertIn("--style", cmd)
        self.assertIn("stil", cmd)
        self.assertIn("--chapter", cmd)
        self.assertIn("--ollama-model", cmd)
        self.assertIn("--fail-on-errors", cmd)

    def test_build_export_and_review_fix_commands(self) -> None:
        export_cmd = build_export_command(
            ExportOptions(
                book_id="pharao",
                style="stil",
                scope="chapter",
                export_format="pdf",
                chapter="001",
                allow_partial=True,
            )
        )
        fix_cmd = build_review_fixes_command("pharao", "stil", "stage")

        self.assertIn("--chapter", export_cmd)
        self.assertIn("--allow-partial", export_cmd)
        self.assertEqual(fix_cmd[-1], "--stage")

    def test_build_init_book_command(self) -> None:
        cmd = build_init_book_command(
            NewBookOptions(
                source="books/Autor - Titel.rtf",
                title="Titel",
                author="Autor",
                style="stil-01-original",
                source_lang="pl",
                target_lang="de",
                ruleset_apply=True,
            )
        )

        self.assertEqual(cmd[0], "tools/init_book.py")
        self.assertIn("--source", cmd)
        self.assertIn("books/Autor - Titel.rtf", cmd)
        self.assertIn("--source-lang", cmd)
        self.assertIn("pl", cmd)
        self.assertIn("--ruleset-apply", cmd)

    def test_guess_title_author_from_source_filename(self) -> None:
        title, author = guess_title_author(Path("Boleslaw Prus - Pharao.rtf"))

        self.assertEqual(title, "Pharao")
        self.assertEqual(author, "Boleslaw Prus")

    def test_unregistered_sources_excludes_registered_book_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            books_dir = root / "books"
            books_dir.mkdir()
            loose = books_dir / "Loose Source.rtf"
            registered = books_dir / "sample" / "source" / "Registered Source.rtf"
            loose.write_text("loose", encoding="utf-8")
            registered.parent.mkdir(parents=True)
            registered.write_text("registered", encoding="utf-8")

            result = unregistered_sources(
                root,
                [{"source_path": "books/sample/source/Registered Source.rtf"}],
            )

        self.assertEqual([path.name for path in result], ["Loose Source.rtf"])

    def test_load_export_meta_merges_defaults_and_book_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            export_yaml = root / "books" / "sample" / "export.yaml"
            export_yaml.parent.mkdir(parents=True)
            export_yaml.write_text(
                "\n".join([
                    "defaults:",
                    "  front_matter:",
                    "    toc_page: false",
                    "    imprint_page: true",
                    "book:",
                    "  title: Sample",
                    "  front_matter:",
                    "    toc_page: true",
                ]),
                encoding="utf-8",
            )
            meta = load_export_meta(
                {"export_config": "books/sample/export.yaml"},
                root,
            )

        self.assertEqual(meta["title"], "Sample")
        self.assertTrue(meta["front_matter"]["toc_page"])
        self.assertTrue(meta["front_matter"]["imprint_page"])

    def test_editable_and_normalized_name_rows_round_trip_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            names_yaml = root / "books" / "sample" / "names.yaml"
            names_yaml.parent.mkdir(parents=True)
            names_yaml.write_text(
                "\n".join([
                    "entries:",
                    "- source: Анна",
                    "  target: Anna",
                    "  aliases: [Anna Arkadjewna, Anja]",
                    "  type: person",
                    "  status: approved",
                    "  note: Hauptfigur",
                ]),
                encoding="utf-8",
            )
            rows = editable_name_rows({"names_file": "books/sample/names.yaml"}, root)
            normalized = normalize_name_rows(rows)

        self.assertEqual(rows[0]["aliases"], "Anna Arkadjewna, Anja")
        self.assertEqual(normalized[0]["aliases"], ["Anna Arkadjewna", "Anja"])

    def test_count_export_illustrations_counts_matching_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book_root = root / "books" / "sample"
            (book_root / "assets" / "chapter").mkdir(parents=True)
            (book_root / "assets" / "scene" / "001").mkdir(parents=True)
            (book_root / "assets" / "chapter" / "chapter-001.jpg").write_text("x")
            (book_root / "assets" / "scene" / "001" / "scene-001.png").write_text("x")
            (book_root / "assets" / "scene" / "001" / "ignored.txt").write_text("x")

            counts = count_export_illustrations(
                {"book_root": "books/sample"},
                {
                    "illustrations": {
                        "enabled": True,
                        "chapter_images": True,
                        "scene_images": True,
                    }
                },
                ["001"],
                root,
            )

        self.assertEqual(counts, {"chapter": 1, "scene": 1, "total": 2})

    def test_translation_context_for_scene_book(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work = root / "books" / "sample" / "work"
            (work / "scenes" / "pl" / "001").mkdir(parents=True)
            (work / "scenes" / "de" / "stil" / "001").mkdir(parents=True)
            (work / "scenes" / "pl" / "001" / "scene-01.md").write_text("pl1")
            (work / "scenes" / "pl" / "001" / "scene-02.md").write_text("pl2")
            (work / "scenes" / "de" / "stil" / "001" / "scene-01.md").write_text("de1")

            ctx = translation_context(
                {
                    "work_dir": "books/sample/work",
                    "source_lang": "pl",
                    "structure": {"mode": "scenes"},
                },
                "001",
                "stil",
                root,
            )

        self.assertEqual(ctx.counts["ru"], 2)
        self.assertEqual(ctx.counts["de"], 1)
        self.assertEqual(ctx.missing_count, 1)
        self.assertEqual(ctx.scene_choices, ["alle fehlenden", "02"])
        self.assertEqual(ctx.default_scene_index, 1)
        self.assertEqual(ctx.source_lang_label, "PL")
        self.assertEqual(ctx.unit_label, "Szenen")

    def test_review_context_paths(self) -> None:
        ctx = review_context({"work_dir": "books/sample/work"}, "stil", Path("repo"))

        self.assertEqual(ctx.review_root, Path("repo/books/sample/work/reviews/stil"))
        self.assertEqual(ctx.summary_json.name, "review-summary.json")
        self.assertEqual(ctx.fix_manifest.name, "fix-manifest.json")

    def test_export_context_for_book_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book_root = root / "books" / "sample"
            work = book_root / "work"
            (work / "chapters").mkdir(parents=True)
            (work / "scenes" / "ru" / "001").mkdir(parents=True)
            (work / "scenes" / "ru" / "002").mkdir(parents=True)
            (work / "scenes" / "de" / "stil" / "001").mkdir(parents=True)
            (book_root / "assets" / "chapter").mkdir(parents=True)
            (book_root / "export.yaml").write_text(
                "\n".join([
                    "defaults:",
                    "  front_matter:",
                    "    toc_page: true",
                    "  illustrations:",
                    "    enabled: true",
                    "book:",
                    "  cover:",
                    "    mode: placeholder",
                ]),
                encoding="utf-8",
            )
            (work / "chapters" / "001-source.md").write_text("c1")
            (work / "chapters" / "002-source.md").write_text("c2")
            (work / "scenes" / "ru" / "001" / "scene-01.md").write_text("ru1")
            (work / "scenes" / "ru" / "002" / "scene-01.md").write_text("ru2")
            (work / "scenes" / "de" / "stil" / "001" / "scene-01.md").write_text("de1")
            (book_root / "assets" / "chapter" / "chapter-001.jpg").write_text("x")

            ctx = export_context(
                {
                    "book_root": "books/sample",
                    "work_dir": "books/sample/work",
                    "export_config": "books/sample/export.yaml",
                    "status_file": "books/sample/status/status.json",
                    "source_lang": "ru",
                },
                [{"id": "stil", "label": "Stil"}],
                "stil",
                "001",
                ["001", "002"],
                "book",
                root,
            )

        self.assertEqual(ctx.chapter_metrics["chapters"], 2)
        self.assertEqual(ctx.chapter_metrics["source_scenes"], 2)
        self.assertEqual(ctx.chapter_metrics["de_scenes"], 1)
        self.assertEqual(ctx.chapter_metrics["missing"], 1)
        self.assertEqual(ctx.missing_chapters, ["002"])
        self.assertEqual(ctx.illustration_counts["chapter"], 1)
        self.assertIn("Inhalt", ctx.front_enabled)


if __name__ == "__main__":
    unittest.main()
