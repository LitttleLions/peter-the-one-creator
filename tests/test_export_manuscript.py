from __future__ import annotations

import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import export_manuscript as export  # noqa: E402


class ExportManuscriptTests(unittest.TestCase):
    def write_test_image(self, path: Path) -> None:
        from PIL import Image

        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (12, 12), "#cc3333").save(path)

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
        self.assertEqual(dirs["pdf"], root / "stil-test" / "chapter" / "pdf")
        self.assertEqual(dirs["work"], root / "stil-test" / "chapter" / "work")
        self.assertEqual(
            dirs["manifests"],
            root / "stil-test" / "chapter" / "manifests",
        )

    def test_export_formats_include_pdf_and_keep_all_alias(self) -> None:
        self.assertEqual(export.EXPORT_FORMATS, ("docx", "epub", "pdf", "all"))

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

    def test_chapter_illustration_is_inserted_before_chapter_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = root / "assets" / "chapter" / "chapter-001.jpg"
            image.parent.mkdir(parents=True)
            image.write_bytes(b"image")
            chapter = export.ChapterExport(
                chapter_id="001",
                title="Kapitel 1",
                scenes=[export.SceneExport(number=1, text="Ein Satz.")],
                missing=[],
                ru_count=1,
                de_count=1,
            )
            meta = {
                "_base_dir": str(root),
                "title": "Peter der Erste",
                "front_matter": {"title_page": False, "imprint_page": False},
                "display": {
                    "chapters": {
                        "format": "words_de",
                        "suffix": " Kapitel",
                    }
                },
                "illustrations": {
                    "enabled": True,
                    "chapter_images": True,
                    "scene_images": True,
                    "chapter_page_break_after_image": True,
                },
            }
            illustrations = export.collect_illustrations([chapter], meta)
            md_path = root / "work" / "export.md"
            text = export.render_export_markdown(
                [chapter],
                meta=meta,
                style="stil-test",
                scope="book",
                partial=False,
                cover_ref=None,
                markdown_path=md_path,
                illustrations=illustrations,
            )

        self.assertIn('<div class="chapter-illustration page-break-after">', text)
        self.assertIn('chapter-001.jpg" alt="Kapitel 001"', text)
        self.assertNotIn("![Kapitel 001]", text)
        self.assertLess(
            text.index("chapter-001.jpg"),
            text.index("# Erstes Kapitel"),
        )

    def test_missing_illustration_does_not_change_export_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chapter = export.ChapterExport(
                chapter_id="001",
                title="Kapitel 1",
                scenes=[export.SceneExport(number=1, text="Ein Satz.")],
                missing=[],
                ru_count=1,
                de_count=1,
            )
            meta = {
                "_base_dir": str(root),
                "title": "Peter der Erste",
                "front_matter": {"title_page": False, "imprint_page": False},
                "illustrations": {"enabled": True},
            }
            text = export.render_export_markdown(
                [chapter],
                meta=meta,
                style="stil-test",
                scope="book",
                partial=False,
                cover_ref=None,
                markdown_path=root / "work" / "export.md",
                illustrations=export.collect_illustrations([chapter], meta),
            )

        self.assertNotIn("chapter-001", text)
        self.assertNotIn("scene-01", text)

    def test_scene_illustration_is_inserted_before_scene_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = root / "assets" / "scene" / "001" / "scene-002.png"
            image.parent.mkdir(parents=True)
            image.write_bytes(b"image")
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
            meta = {
                "_base_dir": str(root),
                "title": "Peter der Erste",
                "front_matter": {"title_page": False, "imprint_page": False},
                "display": {
                    "scenes": {
                        "show": True,
                        "format": "number",
                        "align": "center",
                    }
                },
                "illustrations": {
                    "enabled": True,
                    "chapter_images": True,
                    "scene_images": True,
                    "scene_page_break_after_image": False,
                },
            }
            illustrations = export.collect_illustrations([chapter], meta)
            text = export.render_export_markdown(
                [chapter],
                meta=meta,
                style="stil-test",
                scope="book",
                partial=False,
                cover_ref=None,
                markdown_path=root / "work" / "export.md",
                illustrations=illustrations,
            )

        self.assertIn('<div class="scene-illustration">', text)
        self.assertIn('scene-002.png" alt="Kapitel 001, Szene 02"', text)
        self.assertLess(text.index("scene-002.png"), text.index("[2]{.scene-marker"))

    def test_check_epub_reports_invalid_xhtml_image_alt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            epub = Path(tmp) / "bad.epub"
            with zipfile.ZipFile(epub, "w") as zf:
                zf.writestr("mimetype", "application/epub+zip")
                zf.writestr("META-INF/container.xml", "<container/>")
                zf.writestr("EPUB/package.opf", "<package/>")
                zf.writestr("EPUB/nav.xhtml", "<html><body>nav</body></html>")
                zf.writestr(
                    "EPUB/text/ch001.xhtml",
                    '<html><body><img src="image.png" alt /></body></html>',
                )

            result = export.check_epub(epub)

        self.assertTrue(any("XHTML-Parsefehler" in item for item in result))

    def test_disabled_illustrations_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = root / "assets" / "chapter" / "chapter-001.jpg"
            image.parent.mkdir(parents=True)
            image.write_bytes(b"image")
            chapter = export.ChapterExport(
                chapter_id="001",
                title="Kapitel 1",
                scenes=[export.SceneExport(number=1, text="Ein Satz.")],
                missing=[],
                ru_count=1,
                de_count=1,
            )
            meta = {
                "_base_dir": str(root),
                "illustrations": {"enabled": False},
            }

        self.assertEqual(export.collect_illustrations([chapter], meta), [])

    def test_write_docx_accepts_chapter_illustration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = root / "assets" / "chapter" / "chapter-001.png"
            self.write_test_image(image)
            chapter = export.ChapterExport(
                chapter_id="001",
                title="Kapitel 1",
                scenes=[export.SceneExport(number=1, text="Ein Satz.")],
                missing=[],
                ru_count=1,
                de_count=1,
            )
            meta = {
                "_base_dir": str(root),
                "title": "Peter der Erste",
                "front_matter": {
                    "cover_in_body": False,
                    "title_page": False,
                    "summary_page": False,
                    "author_bio_page": False,
                    "description_page": False,
                    "imprint_page": False,
                    "toc_page": False,
                },
                "illustrations": {
                    "enabled": True,
                    "chapter_images": True,
                    "chapter_page_break_after_image": True,
                },
            }
            out = root / "out.docx"
            export.write_docx(
                out,
                [chapter],
                meta,
                style="stil-test",
                scope="book",
                partial=False,
                cover_path=image,
                illustrations=export.collect_illustrations([chapter], meta),
            )
            self.assertTrue(out.exists())

    def test_render_pdf_html_contains_frontmatter_chapter_scene_and_images(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chapter_image = root / "assets" / "chapter" / "chapter-001.png"
            scene_image = root / "assets" / "scene" / "001" / "scene-002.png"
            cover = root / "assets" / "covers" / "cover.png"
            for image in (chapter_image, scene_image, cover):
                image.parent.mkdir(parents=True, exist_ok=True)
                image.write_bytes(b"image")
            chapter = export.ChapterExport(
                chapter_id="001",
                title="Kapitel 1",
                scenes=[
                    export.SceneExport(number=1, text="Ein **Satz**.\n\n> Zitat."),
                    export.SceneExport(number=2, text="*Zweite* Szene."),
                ],
                missing=[],
                ru_count=2,
                de_count=2,
            )
            meta = {
                "_base_dir": str(root),
                "title": "Peter der Erste",
                "author": "Alexei Tolstoi",
                "summary": "Kurze Zusammenfassung.",
                "front_matter": {
                    "cover_in_body": True,
                    "title_page": True,
                    "summary_page": True,
                    "author_bio_page": False,
                    "imprint_page": False,
                    "toc_page": True,
                },
                "display": {
                    "chapters": {
                        "format": "words_de",
                        "suffix": " Kapitel",
                        "align": "center",
                    },
                    "scenes": {
                        "show": True,
                        "format": "number",
                        "align": "center",
                    },
                },
                "illustrations": {
                    "enabled": True,
                    "chapter_images": True,
                    "scene_images": True,
                },
            }
            html_path = root / "work" / "book.pdf.html"
            css_path = root / "work" / "book-print.css"
            text = export.render_pdf_html(
                [chapter],
                meta,
                style="stil-test",
                scope="book",
                partial=False,
                cover_path=cover,
                html_path=html_path,
                css_path=css_path,
                illustrations=export.collect_illustrations([chapter], meta),
            )

        self.assertIn("<title>Peter der Erste</title>", text)
        self.assertIn('class="frontmatter-page titlepage"', text)
        self.assertIn("Kurze Zusammenfassung.", text)
        self.assertIn('id="frontmatter-toc"', text)
        self.assertIn('id="kapitel-001"', text)
        self.assertIn("Erstes Kapitel", text)
        self.assertIn('class="scene-marker">1</div>', text)
        self.assertIn("<strong>Satz</strong>", text)
        self.assertIn("<blockquote>", text)
        self.assertIn("chapter-001.png", text)
        self.assertIn("scene-002.png", text)
        chapter_section = text[text.index('id="kapitel-001"'):]
        self.assertLess(chapter_section.index("chapter-001.png"), chapter_section.index("Erstes Kapitel"))
        self.assertIn('class="chapter-illustration page-break-after"', text)
        self.assertNotIn("<figcaption", text)

    def test_write_pdf_css_contains_a5_page_and_breaks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = export.write_pdf_css(Path(tmp) / "book-print.css")
            css = path.read_text(encoding="utf-8")

        self.assertIn("@page", css)
        self.assertIn("size: A5", css)
        self.assertIn("margin: 18mm 16mm 20mm 16mm", css)
        self.assertIn(".chapter", css)
        self.assertIn("break-before: page", css)
        self.assertIn("page-break-after: always", css)

    def test_epub_postprocess_renames_auto_title_nav_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "book.epub"
            title = "Peter der Erste - Kapitel 001"
            with zipfile.ZipFile(path, "w") as zf:
                zf.writestr("mimetype", b"application/epub+zip")
                zf.writestr("META-INF/container.xml", b"<container />")
                zf.writestr(
                    "EPUB/nav.xhtml",
                    (
                        '<nav epub:type="toc"><ol class="toc">'
                        '<li><a href="text/ch001.xhtml#peter-der-erste---kapitel-001">'
                        f"{title}"
                        "</a></li>"
                        '<li><a href="text/ch002.xhtml#kapitel-001">Erstes Kapitel</a></li>'
                        "</ol></nav>"
                    ).encode("utf-8"),
                )
                zf.writestr(
                    "EPUB/text/ch001.xhtml",
                    (
                        "<body><section>"
                        f"<h1>{title}</h1>"
                        '<div class="frontmatter-page titlepage"></div>'
                        "</section></body>"
                    ).encode("utf-8"),
                )

            export.remove_auto_title_heading_from_epub(path, title, "Titelseite")

            with zipfile.ZipFile(path) as zf:
                nav = zf.read("EPUB/nav.xhtml").decode("utf-8")
                body = zf.read("EPUB/text/ch001.xhtml").decode("utf-8")

        self.assertIn(">Titelseite</a>", nav)
        self.assertIn(">Erstes Kapitel</a>", nav)
        self.assertNotIn(f">{title}</a>", nav)
        self.assertNotIn(f"<h1>{title}</h1>", body)

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

    def test_render_export_markdown_uses_custom_title_and_imprint_text(self) -> None:
        chapter = export.ChapterExport(
            chapter_id="001",
            title="Kapitel 1",
            scenes=[export.SceneExport(number=1, text="Ein Satz.")],
            missing=[],
            ru_count=1,
            de_count=1,
        )
        text = export.render_export_markdown(
            [chapter],
            meta={
                "title": "Peter der Erste",
                "subtitle": "Der große Roman über Zar Peter I.",
                "author": "Alexei Nikolajewitsch Tolstoi",
                "translator": "Motivatier Classics",
                "translator_label": "Übersetzung und editorische Einrichtung",
                "language": "de-DE",
                "title_page_extra": [
                    "Originaltitel: Пётр Первый",
                    "Herausgegeben von der Motivatier Hermann Stiftung",
                ],
                "imprint_text": (
                    "Freies Impressum.\n\n"
                    "Alexei Nikolajewitsch Tolstoi\n\n"
                    "Der große Roman über Zar Peter I.\n\n"
                    "Originaltitel: Пётр Первый\n\n"
                    "Herausgegeben von der Motivatier Hermann Stiftung\n\n"
                    "Alle Rechte vorbehalten."
                ),
                "front_matter": {
                    "title_page": True,
                    "summary_page": False,
                    "author_bio_page": False,
                    "imprint_page": True,
                    "combined_epub_front_matter": False,
                },
            },
            style="stil-test",
            scope="book",
            partial=False,
            cover_ref=None,
        )
        self.assertIn("[Originaltitel: Пётр Первый]{.title-extra}", text)
        self.assertIn(
            "[Übersetzung und editorische Einrichtung: Motivatier Classics]{.translator}",
            text,
        )
        self.assertIn('class="frontmatter-page imprintpage"', text)
        self.assertIn('class="imprint-title"', text)
        self.assertIn('class="imprint-rights"', text)
        self.assertIn("Freies Impressum.", text)
        self.assertIn("Alle Rechte vorbehalten.", text)
        self.assertNotIn("**Titel:**", text)

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
