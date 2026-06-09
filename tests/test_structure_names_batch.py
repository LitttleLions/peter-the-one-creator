from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import extract_scenes  # noqa: E402
import translate_batch  # noqa: E402
from lib.name_registry import write_names  # noqa: E402
from lib.output_paths import ru_scene_dir  # noqa: E402
from lib.style_prompts import StylePrompts  # noqa: E402
import lib.style_prompts as style_prompts_mod  # noqa: E402


class StructureNamesBatchTests(unittest.TestCase):
    def test_chapter_as_scene_creates_single_scene(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chapters = root / "chapters"
            chapters.mkdir()
            (chapters / "001-source.md").write_text(
                "# Kapitel 1\n\n*Buch: Test*\n\nAbsatz eins.\n\nAbsatz zwei.\n",
                encoding="utf-8",
            )
            result = extract_scenes.extract_scenes_for_chapter(
                root,
                "001",
                structure_mode="chapter_as_scene",
                dry_run=False,
            )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["number"], 1)
        self.assertIn("Absatz eins.", result[0]["text"])

    def test_scenes_mode_keeps_multiple_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chapters = root / "chapters"
            chapters.mkdir()
            (chapters / "001-source.md").write_text(
                "# Kapitel 1\n\n## 1\n\nErste Szene.\n\n## 2\n\nZweite Szene.\n",
                encoding="utf-8",
            )
            result = extract_scenes.extract_scenes_for_chapter(
                root,
                "001",
                structure_mode="scenes",
                dry_run=True,
            )

        self.assertEqual([item["number"] for item in result], [1, 2])

    def test_names_are_injected_into_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            styles = root / "styles"
            styles.mkdir()
            (styles / "stil-test.md").write_text("Bewahre Namen.", encoding="utf-8")
            names_path = root / "books" / "sample" / "names.yaml"
            write_names(
                names_path,
                [{
                    "source": "Анна",
                    "target": "Anna",
                    "aliases": ["Anna Arkadjewna"],
                    "type": "person",
                    "status": "approved",
                    "note": "Hauptfigur",
                }],
            )
            old_root = style_prompts_mod.REPO_ROOT
            style_prompts_mod.REPO_ROOT = root
            try:
                prompts = StylePrompts(path=root / "missing.yaml", profiles_dir=styles)
                messages = prompts.build_messages(
                    mode="stil-test",
                    book_cfg={
                        "title": "Sample",
                        "author": "Autor",
                        "source_lang": "ru",
                        "target_lang": "de",
                        "names_file": "books/sample/names.yaml",
                    },
                    source_text="Анна вошла.",
                )
            finally:
                style_prompts_mod.REPO_ROOT = old_root

        self.assertIn("### Verbindliche Namen und Begriffe", messages[1]["content"])
        self.assertIn("Анна -> Anna", messages[1]["content"])

    def test_batch_builds_extract_and_translate_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = translate_batch.REPO_ROOT
            translate_batch.REPO_ROOT = Path(tmp)
            try:
                book = {
                    "id": "sample",
                    "title": "Sample",
                    "work_dir": "books/sample/work",
                }
                commands = translate_batch.build_commands(
                    book=book,
                    chapters=["001"],
                    style="stil-test",
                    provider="prompt_file",
                    model=None,
                    overwrite=False,
                    auto_status=False,
                    no_review=False,
                )
            finally:
                translate_batch.REPO_ROOT = old_root

        self.assertEqual(commands[0][:4], ["tools/extract_scenes.py", "--book", "sample", "--chapter"])
        self.assertEqual(commands[1][:4], ["tools/translate_chapter.py", "--book", "sample", "--chapter"])


if __name__ == "__main__":
    unittest.main()
