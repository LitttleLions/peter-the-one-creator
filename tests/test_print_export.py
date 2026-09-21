from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import export_manuscript as export  # noqa: E402
from lib.print_css import build_paperback_css, write_paperback_css  # noqa: E402
from lib.print_pdf import (  # noqa: E402
    _helvetica_overlay_pdf,
    count_export_words,
    count_frontmatter_sections,
    export_paperback_interior,
)
from lib.print_spec import (  # noqa: E402
    PrintSpec,
    kdp_gutter_band,
    kdp_gutter_mm,
    kdp_max_pages,
    kdp_spine_mm,
    load_print_spec,
    wrap_height_in,
    wrap_width_in,
)


class PrintSpecTests(unittest.TestCase):
    def test_kdp_gutter_table(self) -> None:
        self.assertEqual(kdp_gutter_mm(24), 9.6)
        self.assertEqual(kdp_gutter_mm(150), 9.6)
        self.assertEqual(kdp_gutter_mm(151), 12.7)
        self.assertEqual(kdp_gutter_mm(300), 12.7)
        self.assertEqual(kdp_gutter_mm(301), 15.9)
        self.assertEqual(kdp_gutter_mm(500), 15.9)
        self.assertEqual(kdp_gutter_mm(501), 19.1)
        self.assertEqual(kdp_gutter_mm(700), 19.1)
        self.assertEqual(kdp_gutter_mm(701), 22.3)
        self.assertEqual(kdp_gutter_mm(828), 22.3)
        self.assertEqual(kdp_gutter_band(151), 300)

    def test_kdp_page_limits_by_paper(self) -> None:
        self.assertEqual(kdp_max_pages("cream"), 776)
        self.assertEqual(kdp_max_pages("white"), 828)
        self.assertEqual(kdp_max_pages("groundwood"), 812)
        spec = load_print_spec(REPO_ROOT, {})
        self.assertEqual(spec.paper, "cream")
        self.assertEqual(spec.kdp_max_pages(), 776)

    def test_trim_size_does_not_change_type(self) -> None:
        classic = load_print_spec(REPO_ROOT, {})
        six = load_print_spec(REPO_ROOT, {}, overlay={"trim_size": "6x9"})
        self.assertEqual(classic.trim_size, "5.5x8.5")
        self.assertEqual(six.trim_size, "6x9")
        self.assertEqual(six.trim_width_in, 6.0)
        self.assertEqual(six.trim_height_in, 9.0)
        self.assertEqual(six.font_size_pt, classic.font_size_pt)
        self.assertEqual(six.line_height_pt, classic.line_height_pt)
        self.assertEqual(six.layout_profile, "classic")
        self.assertEqual(classic.filename_slug, "55x85-classic-full")
        self.assertEqual(six.filename_slug, "6x9-classic-full")

    def test_layout_profile_does_not_change_trim(self) -> None:
        spec = load_print_spec(
            REPO_ROOT, {}, overlay={"layout_profile": "long_classic"}
        )
        self.assertEqual(spec.trim_size, "5.5x8.5")
        self.assertEqual(spec.font_size_pt, 10.2)
        self.assertEqual(spec.line_height_pt, 12.5)
        self.assertEqual(spec.chapter_start, "next_page")
        self.assertEqual(spec.filename_slug, "55x85-long_classic-full")

    def test_spine_and_wrap_size_from_page_count(self) -> None:
        self.assertAlmostEqual(kdp_spine_mm(200), 12.7)
        self.assertAlmostEqual(wrap_width_in(200, 5.5), 11.75)
        self.assertAlmostEqual(wrap_height_in(8.5), 8.75)

    def test_side_margin_uses_min_outer(self) -> None:
        spec = PrintSpec.from_dict({}, REPO_ROOT)
        self.assertEqual(spec.side_margin_mm(120), 12.7)
        self.assertEqual(spec.side_margin_mm(200), 12.7)
        self.assertEqual(spec.side_margin_mm(400), 15.9)

    def test_needs_rerender_only_when_side_margin_changes(self) -> None:
        spec = PrintSpec.from_dict({}, REPO_ROOT)
        self.assertFalse(spec.needs_rerender(120, 200))
        self.assertTrue(spec.needs_rerender(200, 400))
        self.assertFalse(spec.needs_rerender(400, 450))

    def test_series_defaults_load_from_config(self) -> None:
        spec = load_print_spec(REPO_ROOT, {})
        self.assertEqual(spec.profile, "classic")
        self.assertEqual(spec.trim_width_in, 5.5)
        self.assertEqual(spec.trim_height_in, 8.5)
        self.assertEqual(spec.font_family, "EB Garamond")
        self.assertTrue(spec.font_regular_path.is_file())
        self.assertTrue(spec.font_italic_path.is_file())

    def test_book_override_merges(self) -> None:
        spec = load_print_spec(REPO_ROOT, {"print": {"font": {"size_pt": 11.0}}})
        self.assertEqual(spec.font_size_pt, 11.0)
        self.assertEqual(spec.profile, "classic")


class PrintCssTests(unittest.TestCase):
    def test_paperback_css_is_digest_not_a5(self) -> None:
        spec = PrintSpec.from_dict({}, REPO_ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            css_path = Path(tmp) / "book-paperback.css"
            css = build_paperback_css(spec, css_path, page_count=400)
        self.assertIn("size: 5.5in 8.5in", css)
        self.assertIn("@font-face", css)
        self.assertIn("text-align: justify", css)
        self.assertIn("text-indent: 1.2em", css)
        self.assertIn("margin: 16mm 15.9mm 18mm 15.9mm", css)
        self.assertNotIn("size: A5", css)
        self.assertIn(".scene-text blockquote", css)
        self.assertIn("font-style: italic", css)
        self.assertIn("max-width: 72%", css)
        self.assertIn("1.15pt double", css)
        self.assertIn("max-height: 90mm", css)
        self.assertIn(".series-catalog", css)
        self.assertNotIn("max-width: 100%;\n  max-height: 120mm", css)

    def test_write_paperback_css_roundtrip(self) -> None:
        spec = PrintSpec.from_dict({}, REPO_ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            path = write_paperback_css(Path(tmp) / "book-paperback.css", spec, 80)
            text = path.read_text(encoding="utf-8")
        self.assertIn("size: 5.5in 8.5in", text)
        self.assertIn("12.7mm", text)

    def test_six_by_nine_css_keeps_classic_type(self) -> None:
        spec = load_print_spec(REPO_ROOT, {}, overlay={"trim_size": "6x9"})
        with tempfile.TemporaryDirectory() as tmp:
            css = build_paperback_css(spec, Path(tmp) / "book-paperback.css", 400)
        self.assertIn("size: 6in 9in", css)
        self.assertIn("font-size: 10.8pt", css)
        self.assertIn("line-height: 13.6pt", css)
        self.assertNotIn("size: 5.5in 8.5in", css)

    def test_long_classic_css_keeps_trim(self) -> None:
        spec = load_print_spec(
            REPO_ROOT, {}, overlay={"layout_profile": "long_classic"}
        )
        with tempfile.TemporaryDirectory() as tmp:
            css = build_paperback_css(spec, Path(tmp) / "book-paperback.css", 80)
        self.assertIn("size: 5.5in 8.5in", css)
        self.assertIn("font-size: 10.2pt", css)
        self.assertIn("line-height: 12.5pt", css)

    def test_inline_css_uses_type_height_ratio(self) -> None:
        spec = load_print_spec(
            REPO_ROOT, {}, overlay={"illustration_mode": "inline"}
        )
        with tempfile.TemporaryDirectory() as tmp:
            css = build_paperback_css(spec, Path(tmp) / "book-paperback.css", 80)
        self.assertIn("max-height: 81.8", css)
        self.assertNotIn("max-height: 90mm", css)
        self.assertGreater(spec.illustration_max_height_mm(), 70)
        self.assertLess(spec.illustration_max_height_mm(), 90)

    def test_recto_chapter_start_css(self) -> None:
        spec = load_print_spec(
            REPO_ROOT, {}, overlay={"chapter_start": "recto"}
        )
        with tempfile.TemporaryDirectory() as tmp:
            css = build_paperback_css(spec, Path(tmp) / "book-paperback.css", 80)
        self.assertIn("break-before: right", css)


class PrintHtmlTests(unittest.TestCase):
    def _chapter(self) -> export.ChapterExport:
        return export.ChapterExport(
            chapter_id="001",
            title="Kapitel 1",
            scenes=[
                export.SceneExport(
                    number=1,
                    text="> Ein Vorspann.\n\nDer erste Satz des Kapitels.",
                )
            ],
            missing=[],
            ru_count=1,
            de_count=1,
        )

    def test_paperback_html_omits_cover_and_keeps_blockquote(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cover = root / "cover.png"
            cover.write_bytes(b"image")
            chapter = self._chapter()
            meta = {
                "_base_dir": str(root),
                "title": "Der Pharao",
                "author": "Boleslaw Prus",
                "front_matter": {
                    "cover_in_body": True,
                    "title_page": True,
                    "summary_page": False,
                    "author_bio_page": False,
                    "imprint_page": False,
                    "toc_page": False,
                },
            }
            html_path = root / "book.paperback.html"
            css_path = root / "book-paperback.css"
            text = export.render_pdf_html(
                [chapter],
                meta,
                style="stil-02-poetisch",
                scope="book",
                partial=False,
                cover_path=cover,
                html_path=html_path,
                css_path=css_path,
                include_cover=False,
            )
        self.assertNotIn('class="frontmatter-page coverpage"', text)
        self.assertNotIn("cover-image", text)
        self.assertIn("<blockquote>", text)
        self.assertIn("Ein Vorspann.", text)
        self.assertIn('class="chapter"', text)
        self.assertIn('id="kapitel-001"', text)

    def test_inline_illustration_keeps_lede_without_page_break(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = root / "plate.jpg"
            image.write_bytes(b"image")
            chapter = self._chapter()
            illustration = export.Illustration("chapter", "001", None, image)
            text = export.render_pdf_html(
                [chapter],
                {
                    "_base_dir": str(root),
                    "title": "Der Pharao",
                    "front_matter": {
                        "cover_in_body": False,
                        "title_page": False,
                        "imprint_page": False,
                    },
                    "illustrations": {
                        "enabled": True,
                        "chapter_page_break_after_image": True,
                    },
                },
                style="stil-02-poetisch",
                scope="book",
                partial=False,
                cover_path=image,
                html_path=root / "book.paperback.html",
                css_path=root / "book-paperback.css",
                illustrations=[illustration],
                include_cover=False,
                illustration_mode="inline",
            )
        illustration_at = text.find("chapter-illustration")
        heading_at = text.find("chapter-heading")
        quote_at = text.find("<blockquote>")
        self.assertGreater(illustration_at, 0)
        self.assertGreater(heading_at, illustration_at)
        self.assertGreater(quote_at, heading_at)
        self.assertIn("chapter-illustration inline", text)
        self.assertNotIn("page-break-after", text)
        self.assertIn("Ein Vorspann.", text)

    def test_full_page_illustration_keeps_page_break(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = root / "plate.jpg"
            image.write_bytes(b"image")
            text = export.render_pdf_html(
                [self._chapter()],
                {
                    "_base_dir": str(root),
                    "title": "Der Pharao",
                    "front_matter": {
                        "cover_in_body": False,
                        "title_page": False,
                        "imprint_page": False,
                    },
                },
                style="stil-02-poetisch",
                scope="book",
                partial=False,
                cover_path=image,
                html_path=root / "book.paperback.html",
                css_path=root / "book-paperback.css",
                illustrations=[export.Illustration("chapter", "001", None, image)],
                include_cover=False,
                illustration_mode="full_page",
            )
        self.assertIn("chapter-illustration full-page page-break-after", text)

    def test_find_print_cover_does_not_fallback_to_kindle_cover(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            covers = root / "assets" / "covers"
            covers.mkdir(parents=True)
            (covers / "cover.jpg").write_bytes(b"kindle")
            self.assertIsNone(export.find_print_cover({"_base_dir": str(root)}))
            print_cover = covers / "cover-print.png"
            print_cover.write_bytes(b"print")
            found = export.find_print_cover({"_base_dir": str(root)})
            self.assertEqual(found, print_cover)

    def test_paperback_html_includes_catalog_without_print_cover(self) -> None:
        from lib.series_catalog import CatalogEntry

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cover = root / "cover.png"
            cover.write_bytes(b"image")
            entry = CatalogEntry(
                book_id="aelita",
                title="Aelita",
                author="Alexei Tolstoi",
                summary="Mars.",
                cover_path=None,
                sort_order=10,
            )
            text = export.render_pdf_html(
                [self._chapter()],
                {
                    "_base_dir": str(root),
                    "title": "Der Pharao",
                    "author": "Boleslaw Prus",
                    "front_matter": {
                        "cover_in_body": True,
                        "title_page": True,
                        "summary_page": False,
                        "author_bio_page": False,
                        "imprint_page": False,
                        "toc_page": False,
                    },
                },
                style="stil-02-poetisch",
                scope="book",
                partial=False,
                cover_path=cover,
                html_path=root / "book.paperback.html",
                css_path=root / "book-paperback.css",
                include_cover=False,
                catalog_entries=[entry],
            )
        self.assertNotIn('class="frontmatter-page coverpage"', text)
        self.assertIn('id="series-catalog"', text)
        self.assertIn("Aelita", text)

    def test_wrap_html_uses_spine_formula_and_barcode_box(self) -> None:
        from lib.print_wrap import render_wrap_html

        spec = PrintSpec.from_dict({}, REPO_ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cover = root / "cover-print.jpg"
            cover.write_bytes(b"img")
            html = render_wrap_html(
                meta={
                    "title": "Der Pharao",
                    "author": "Boleslaw Prus",
                    "summary": "Ein Satz.",
                },
                cover_path=cover,
                html_path=root / "wrap.html",
                spec=spec,
                page_count=200,
            )
        self.assertIn("size: 11.75in 8.75in", html)
        self.assertIn("barcode-reserve", html)
        self.assertIn("Motivatier Classics", html)
        self.assertIn("class='spine'", html)

    def test_preview_html_still_includes_cover(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cover = root / "cover.png"
            cover.write_bytes(b"image")
            text = export.render_pdf_html(
                [self._chapter()],
                {
                    "_base_dir": str(root),
                    "title": "Der Pharao",
                    "front_matter": {
                        "cover_in_body": True,
                        "title_page": False,
                        "imprint_page": False,
                    },
                },
                style="stil-test",
                scope="book",
                partial=False,
                cover_path=cover,
                html_path=root / "book.pdf.html",
                css_path=root / "book-print.css",
            )
        self.assertIn('class="frontmatter-page coverpage"', text)


class PrintPdfPipelineTests(unittest.TestCase):
    def test_frontmatter_section_count_and_words(self) -> None:
        html = (
            '<section class="frontmatter-page titlepage"></section>'
            '<section class="frontmatter-page imprintpage"></section>'
            '<section class="chapter"></section>'
        )
        self.assertEqual(count_frontmatter_sections(html), 2)
        chapters = [
            export.ChapterExport(
                "001",
                "K",
                [export.SceneExport(1, "eins zwei drei")],
                [],
                1,
                1,
            )
        ]
        self.assertEqual(count_export_words(chapters), 3)

    def test_helvetica_overlay_is_readable_pdf(self) -> None:
        from pypdf import PdfReader

        blob = _helvetica_overlay_pdf(396, 612, 40, 30, "12")
        reader = PdfReader(__import__("io").BytesIO(blob))
        self.assertEqual(len(reader.pages), 1)

    def test_export_rerenders_when_gutter_band_changes(self) -> None:
        from pypdf import PdfWriter

        spec = PrintSpec.from_dict({}, REPO_ROOT)
        chapter = export.ChapterExport(
            "001",
            "K",
            [export.SceneExport(1, "kurz")],
            [],
            1,
            1,
        )
        html = (
            '<section class="frontmatter-page titlepage"></section>'
            '<section class="chapter" id="kapitel-001"></section>'
        )
        calls: list[int] = []

        def fake_render(_html_path: Path, pdf_path: Path) -> None:
            writer = PdfWriter()
            page_count = 400
            calls.append(page_count)
            for _ in range(page_count):
                writer.add_blank_page(width=5.5 * 72, height=8.5 * 72)
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            with pdf_path.open("wb") as handle:
                writer.write(handle)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = export_paperback_interior(
                spec=spec,
                chapters=[chapter],
                html_text=html,
                html_path=root / "book.paperback.html",
                css_path=root / "book-paperback.css",
                pdf_path=root / "interior.pdf",
                report_path=root / "print-report.json",
                author="Autor",
                title="Titel",
                render_pdf=fake_render,
                stamp=False,
            )
            css = (root / "book-paperback.css").read_text(encoding="utf-8")
            self.assertTrue((root / "print-report.json").is_file())

        self.assertEqual(len(calls), 2)
        self.assertEqual(report["iterations"], 2)
        self.assertTrue(report["gutter_rerendered"])
        self.assertTrue(report["cover_omitted"])
        self.assertEqual(report["page_count"], 400)
        self.assertIn("15.9mm", css)

    def test_export_skips_second_pass_when_band_matches(self) -> None:
        from pypdf import PdfWriter

        spec = PrintSpec.from_dict({}, REPO_ROOT)
        chapter = export.ChapterExport(
            "001",
            "K",
            [export.SceneExport(1, "kurz")],
            [],
            1,
            1,
        )
        calls: list[int] = []

        def fake_render(_html_path: Path, pdf_path: Path) -> None:
            calls.append(1)
            writer = PdfWriter()
            for _ in range(80):
                writer.add_blank_page(width=5.5 * 72, height=8.5 * 72)
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            with pdf_path.open("wb") as handle:
                writer.write(handle)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = export_paperback_interior(
                spec=spec,
                chapters=[chapter],
                html_text='<section class="chapter"></section>',
                html_path=root / "book.paperback.html",
                css_path=root / "book-paperback.css",
                pdf_path=root / "interior.pdf",
                report_path=root / "print-report.json",
                author="Autor",
                title="Titel",
                render_pdf=fake_render,
                stamp=False,
            )

        self.assertEqual(len(calls), 1)
        self.assertEqual(report["iterations"], 1)
        self.assertFalse(report["gutter_rerendered"])
        self.assertEqual(report["kdp_max_pages"], 776)
        self.assertTrue(report["within_kdp_page_limit"])
        self.assertEqual(report["trim_size"], "5.5x8.5")
        self.assertEqual(report["layout_profile"], "classic")
        self.assertEqual(report["illustration_mode"], "full_page")

    def test_third_gutter_pass_when_band_changes_twice(self) -> None:
        from pypdf import PdfWriter

        spec = PrintSpec.from_dict({}, REPO_ROOT)
        counts = [400, 701, 701]
        calls: list[int] = []

        def fake_render(_html_path: Path, pdf_path: Path) -> None:
            page_count = counts[min(len(calls), len(counts) - 1)]
            calls.append(page_count)
            writer = PdfWriter()
            for _ in range(page_count):
                writer.add_blank_page(width=5.5 * 72, height=8.5 * 72)
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            with pdf_path.open("wb") as handle:
                writer.write(handle)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = export_paperback_interior(
                spec=spec,
                chapters=[
                    export.ChapterExport(
                        "001", "K", [export.SceneExport(1, "kurz")], [], 1, 1
                    )
                ],
                html_text='<section class="frontmatter-page titlepage"></section><section class="chapter"></section>',
                html_path=root / "book.paperback.html",
                css_path=root / "book-paperback.css",
                pdf_path=root / "interior.pdf",
                report_path=root / "print-report.json",
                author="Autor",
                title="Titel",
                render_pdf=fake_render,
                stamp=False,
            )
            css = (root / "book-paperback.css").read_text(encoding="utf-8")

        self.assertEqual(len(calls), 3)
        self.assertEqual(report["iterations"], 3)
        self.assertEqual(report["page_count"], 701)
        self.assertEqual(report["gutter_mm"], 22.3)
        self.assertIn("22.3mm", css)

    def test_report_warns_above_cream_limit_without_changing_type(self) -> None:
        from pypdf import PdfWriter

        spec = load_print_spec(REPO_ROOT, {})
        self.assertEqual(spec.font_size_pt, 10.8)

        def fake_render(_html_path: Path, pdf_path: Path) -> None:
            writer = PdfWriter()
            for _ in range(800):
                writer.add_blank_page(width=5.5 * 72, height=8.5 * 72)
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            with pdf_path.open("wb") as handle:
                writer.write(handle)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = export_paperback_interior(
                spec=spec,
                chapters=[
                    export.ChapterExport(
                        "001", "K", [export.SceneExport(1, "kurz")], [], 1, 1
                    )
                ],
                html_text='<section class="chapter"></section>',
                html_path=root / "book.paperback.html",
                css_path=root / "book-paperback.css",
                pdf_path=root / "interior.pdf",
                report_path=root / "print-report.json",
                author="Autor",
                title="Titel",
                render_pdf=fake_render,
                stamp=False,
            )

        self.assertEqual(report["page_count"], 800)
        self.assertEqual(report["kdp_max_pages"], 776)
        self.assertFalse(report["within_kdp_page_limit"])
        self.assertEqual(report["status"], "warning")
        self.assertTrue(any("776" in item for item in report["warnings"]))
        self.assertEqual(spec.font_size_pt, 10.8)

    def test_output_basename_includes_print_slug(self) -> None:
        spec = load_print_spec(
            REPO_ROOT,
            {},
            overlay={"trim_size": "6x9", "layout_profile": "classic", "illustration_mode": "inline"},
        )
        name = export.output_basename(
            {"title": "Der Pharao"},
            "stil-02-poetisch",
            "book",
            None,
            print_spec=spec,
        )
        self.assertEqual(name, "book-der-pharao-stil-02-poetisch-6x9-classic-inline")


class PrintCompareTests(unittest.TestCase):
    def test_markdown_table_from_reports(self) -> None:
        from lib.print_compare import render_print_comparison_markdown

        md = render_print_comparison_markdown(
            [
                {
                    "trim_size": "5.5x8.5",
                    "layout_profile": "classic",
                    "illustration_mode": "full_page",
                    "paper": "cream",
                    "page_count": 922,
                    "kdp_max_pages": 776,
                    "within_kdp_page_limit": False,
                    "output_pdf": "a.pdf",
                },
                {
                    "trim_size": "6x9",
                    "layout_profile": "classic",
                    "illustration_mode": "full_page",
                    "paper": "cream",
                    "page_count": 754,
                    "kdp_max_pages": 776,
                    "within_kdp_page_limit": True,
                    "output_pdf": "b.pdf",
                },
            ],
            title="Der Pharao",
        )
        self.assertIn("5.5x8.5", md)
        self.assertIn("NOT KDP COMPATIBLE", md)
        self.assertIn("KDP COMPATIBLE", md)
        self.assertIn("+146", md)


if __name__ == "__main__":
    unittest.main()
