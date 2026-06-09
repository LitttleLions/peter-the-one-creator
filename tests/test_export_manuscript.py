from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import export_manuscript as export  # noqa: E402


class ExportManuscriptTests(unittest.TestCase):
    def test_clean_scene_markdown_removes_control_lines(self) -> None:
        raw = "\n".join([
            "## Szene 7",
            "",
            "### Vier",
            "",
            "*Stil: **stil-02-poetisch** (assemble aus 19 Szenen)*",
            "---",
            "Sanja trat hinaus.",
            "",
            "Noch ein Satz.",
        ])
        cleaned = export.clean_scene_markdown(raw)
        self.assertNotIn("Szene 7", cleaned)
        self.assertNotIn("Vier", cleaned)
        self.assertNotIn("Stil:", cleaned)
        self.assertNotIn("---", cleaned)
        self.assertIn("Sanja trat hinaus.", cleaned)
        self.assertIn("Noch ein Satz.", cleaned)

    def test_collect_export_reports_missing_scenes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chapters").mkdir()
            (root / "chapters" / "001-source.md").write_text(
                "# Kapitel 1: Test\n", encoding="utf-8"
            )
            ru = root / "scenes" / "ru" / "001"
            de = root / "scenes" / "de" / "style-a" / "001"
            ru.mkdir(parents=True)
            de.mkdir(parents=True)
            (ru / "scene-01.md").write_text("## 1\nRU 1", encoding="utf-8")
            (ru / "scene-02.md").write_text("## 2\nRU 2", encoding="utf-8")
            (de / "scene-01.md").write_text("## Szene 1\nDE 1", encoding="utf-8")

            result = export.collect_export(
                output_root=root,
                style="style-a",
                scope="chapter",
                chapter_id="001",
                allow_partial=False,
            )

        self.assertEqual(result.chapters, [])
        self.assertEqual(result.missing_by_chapter, {"001": [2]})

    def test_placeholder_cover_is_png(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = export.make_cover(
                Path(tmp),
                title="Peter der Erste",
                author="Alexei Tolstoi",
                style="stil-test",
                scope_label="Kapitel 001",
                meta={"cover": {"background": "#f59e0b", "foreground": "#ffffff"}},
            )
            data = path.read_bytes()
        self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))

    def test_export_dirs_are_scoped_by_style_and_scope(self) -> None:
        root = Path("books") / "book-a" / "exports"
        dirs = export.export_dirs(root, "stil-test", "chapter")
        self.assertEqual(dirs["docx"], root / "stil-test" / "chapter" / "docx")
        self.assertEqual(dirs["epub"], root / "stil-test" / "chapter" / "epub")
        self.assertEqual(dirs["work"], root / "stil-test" / "chapter" / "work")
        self.assertEqual(
            dirs["manifests"],
            root / "stil-test" / "chapter" / "manifests",
        )

    def test_prepare_cover_uses_external_image(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cover.png"
            path.write_bytes(b"not-a-real-png-but-a-file")
            resolved = export.prepare_cover(
                Path(tmp) / "work",
                title="Peter der Erste",
                author="Alexei Tolstoi",
                style="stil-test",
                scope_label="Kapitel 001",
                meta={"cover": {"mode": "image", "image_path": str(path)}},
            )
        self.assertEqual(resolved, path)

    def test_render_export_markdown_uses_compact_epub_front_matter(self) -> None:
        chapter = export.ChapterExport(
            chapter_id="001",
            title="Kapitel 1: Erstes Kapitel",
            scenes=[export.SceneExport(number=1, text="Ein Satz.")],
            missing=[],
            ru_count=1,
            de_count=1,
        )
        text = export.render_export_markdown(
            [chapter],
            meta={
                "title": "Peter der Erste",
                "author": "Alexei Tolstoi",
                "language": "de-DE",
                "description": "Kurze Beschreibung.",
                "front_matter": {
                    "cover_in_body": False,
                    "description_page": True,
                    "imprint_page": True,
                    "toc_page": False,
                    "combined_epub_front_matter": True,
                },
                "output": {"scene_separator": "* * *"},
            },
            style="stil-test",
            scope="chapter",
            partial=False,
            cover_ref="cover.png",
        )
        self.assertNotIn("![Cover](cover.png)", text)
        self.assertIn("# Titelei", text)
        self.assertIn("## Zu dieser Ausgabe", text)
        self.assertIn("## Impressum", text)
        self.assertNotIn("# Inhalt", text)
        self.assertIn("# Kapitel 001: Erstes Kapitel {#kapitel-001}", text)

    def test_clean_chapter_title_hides_source_mojibake(self) -> None:
        chapter = export.ChapterExport(
            chapter_id="001",
            title="Kapitel 1: \u00d0\u201c\u00d0\u00bb\u00d0\u00b0\u00d0\u00b2\u00d0\u00b0",
            scenes=[],
            missing=[],
            ru_count=0,
            de_count=0,
        )
        self.assertEqual(export.clean_chapter_title(chapter), "Kapitel 001")

    def test_german_ordinal_chapter_titles(self) -> None:
        meta = {
            "display": {
                "chapters": {
                    "format": "words_de",
                    "suffix": " Kapitel",
                    "include_source_title": False,
                }
            }
        }
        cases = {
            "001": "Erstes Kapitel",
            "002": "Zweites Kapitel",
            "021": "Einundzwanzigstes Kapitel",
            "133": "Hundertdreiunddreissigstes Kapitel",
        }
        for chapter_id, expected in cases.items():
            chapter = export.ChapterExport(
                chapter_id=chapter_id,
                title=f"Kapitel {chapter_id}",
                scenes=[],
                missing=[],
                ru_count=0,
                de_count=0,
            )
            self.assertEqual(export.display_chapter_title(chapter, meta), expected)

    def test_anna_display_hides_scene_markers(self) -> None:
        chapters = [
            export.ChapterExport(
                chapter_id="001",
                title="Kapitel 1",
                scenes=[export.SceneExport(number=1, text="Anna Text.")],
                missing=[],
                ru_count=1,
                de_count=1,
            ),
            export.ChapterExport(
                chapter_id="002",
                title="Kapitel 2",
                scenes=[export.SceneExport(number=1, text="Mehr Text.")],
                missing=[],
                ru_count=1,
                de_count=1,
            ),
        ]
        text = export.render_export_markdown(
            chapters,
            meta={
                "title": "Anna Karenina",
                "author": "Lew Tolstoi",
                "language": "de-DE",
                "front_matter": {"title_page": False, "imprint_page": False},
                "display": {
                    "chapters": {
                        "format": "words_de",
                        "suffix": " Kapitel",
                        "align": "center",
                        "include_source_title": False,
                    },
                    "scenes": {"show": False},
                },
            },
            style="stil-02-poetisch",
            scope="book",
            partial=False,
            cover_ref=None,
        )
        self.assertIn("# Erstes Kapitel {#kapitel-001 .chapter-heading .centered}", text)
        self.assertIn("# Zweites Kapitel {#kapitel-002 .chapter-heading .centered}", text)
        self.assertNotIn("Kapitel 001", text)
        self.assertNotIn(".scene-marker", text)

    def test_peter_display_shows_scene_numbers(self) -> None:
        chapter = export.ChapterExport(
            chapter_id="001",
            title="Kapitel 1",
            scenes=[
                export.SceneExport(number=1, text="Szene eins."),
                export.SceneExport(number=2, text="Szene zwei."),
            ],
            missing=[],
            ru_count=2,
            de_count=2,
        )
        text = export.render_export_markdown(
            [chapter],
            meta={
                "title": "Peter der Erste",
                "author": "Alexei Tolstoi",
                "language": "de-DE",
                "front_matter": {"title_page": False, "imprint_page": False},
                "display": {
                    "chapters": {
                        "format": "words_de",
                        "suffix": " Kapitel",
                        "align": "center",
                        "include_source_title": False,
                    },
                    "scenes": {
                        "show": True,
                        "format": "number",
                        "align": "center",
                        "page_break": False,
                        "separator": "",
                    },
                },
                "output": {"scene_separator": "* * *"},
            },
            style="stil-02-poetisch",
            scope="book",
            partial=False,
            cover_ref=None,
        )
        self.assertIn("# Erstes Kapitel {#kapitel-001 .chapter-heading .centered}", text)
        self.assertIn("[1]{.scene-marker .centered}", text)
        self.assertIn("[2]{.scene-marker .centered}", text)
        self.assertNotIn("* * *", text)


if __name__ == "__main__":
    unittest.main()
