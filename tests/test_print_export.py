from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import export_manuscript as export  # noqa: E402
from lib.asset_images import (  # noqa: E402
    DEFAULT_MASTER_PROCESSING,
    MASTER_DIRNAME,
    discover_export_assets,
    is_master_path,
    load_master_processing,
    master_assets_enabled,
)
from lib.gitignore_assets import (  # noqa: E402
    book_switch,
    effective_patterns,
    gitignore_state,
    load_config,
    render_gitignore,
)
from lib.print_css import build_paperback_css, write_paperback_css  # noqa: E402
from lib.print_pdf import (  # noqa: E402
    _helvetica_overlay_pdf,
    count_export_words,
    count_frontmatter_sections,
    export_paperback_interior,
    illustration_tier_summary,
)
from lib.print_wrap import DEFAULT_BACK_COLORS  # noqa: E402
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

    def test_outer_margin_is_fixed_and_gutter_grows(self) -> None:
        """Aussenrand fest, Bundsteg waechst mit der Seitenzahl (2026-11-11).

        Frueher war aussen = innen = Bundsteg; dadurch wurde der Satzspiegel
        bei dicken Buechern unnoetig schmal (KDP-Druckvorschau).
        """
        spec = PrintSpec.from_dict({}, REPO_ROOT)
        self.assertEqual(spec.side_margin_mm(120), 12.7)
        self.assertEqual(spec.side_margin_mm(200), 12.7)
        self.assertEqual(spec.side_margin_mm(400), 12.7)
        self.assertEqual(spec.outer_margin_mm(400), 12.7)
        self.assertEqual(spec.gutter_margin_mm(120), 12.7)
        self.assertEqual(spec.gutter_margin_mm(400), 15.9)
        self.assertEqual(spec.gutter_margin_mm(637), 19.1)

    def test_needs_rerender_only_when_gutter_band_changes(self) -> None:
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
        # Aussenrand fest (12.7 mm), Bundsteg seitenabhaengig innen (15.9 mm
        # im Band bis 500 Seiten).
        self.assertIn("margin: 16mm 12.7mm 18mm 12.7mm", css)
        self.assertIn("@page :right", css)
        self.assertIn("@page :left", css)
        self.assertIn("margin-left: 15.9mm", css)
        self.assertIn("margin-right: 15.9mm", css)
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

    def test_titlepage_min_height_uses_type_area_not_trim(self) -> None:
        """Regression 2026-09-27: min-height auf voller Trim-Hoehe erzeugt
        im A5/Paperback-Satz je eine Leerseite, weil der Block hoeher ist
        als der Satzspiegel."""
        spec = PrintSpec.from_dict({}, REPO_ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            css = build_paperback_css(spec, Path(tmp) / "book-paperback.css", 80)
        self.assertIn("min-height: 180.9mm", css)
        self.assertNotIn("min-height: 8.5in", css)
        self.assertLess(
            spec.fill_height_mm(), spec.trim_height_in * 25.4
        )
        self.assertAlmostEqual(spec.fill_height_mm(), spec.type_height_mm() - 1.0, places=6)

    def test_six_by_nine_titlepage_min_height_follows_margins(self) -> None:
        spec = load_print_spec(REPO_ROOT, {}, overlay={"trim_size": "6x9"})
        with tempfile.TemporaryDirectory() as tmp:
            css = build_paperback_css(spec, Path(tmp) / "book-paperback.css", 80)
        # 9in = 228.6mm - 16 - 18 - 1 Sicherheitszugabe
        self.assertIn("min-height: 193.6mm", css)
        self.assertNotIn("min-height: 9in", css)


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
                    "publisher": "Motivatier Stiftung",
                },
                cover_path=cover,
                html_path=root / "wrap.html",
                spec=spec,
                page_count=200,
            )
        self.assertIn("size: 11.75in 8.75in", html)
        self.assertIn("barcode-reserve", html)
        # Barcode-Platz bleibt frei: nichts wird gemalt (kein Rahmen).
        self.assertNotIn("dashed", html)
        self.assertIn("Motivatier Stiftung", html)
        self.assertIn("class='spine'", html)
        # Ein einzelnes "}}" beendet die Regel und laesst die naechste Regel
        # fallen: der Ruecken verlor dann Breite und die Zentrierung, das
        # Vorderseitenbild wurde gestaucht (Befund 2026-11-10).
        self.assertNotIn("}}", html)
        self.assertIn(".spine span", html)
        self.assertIn("rotate(-90deg)", html)
        self.assertIn("width: 0.5in", html)

    def test_wrap_styled_by_default(self) -> None:
        """Gestaltet ist der Standard: auch ohne `print.back_cover` kommt die
        gestaltete Rueckseite. So bekommt jede KI bei einem neuen Print-Lauf
        automatisch das neue Format (Nutzerentscheidung 2026-11-11)."""
        from lib.print_wrap import render_wrap_html

        spec = PrintSpec.from_dict({}, REPO_ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cover = root / "cover-print.jpg"
            cover.write_bytes(b"img")
            html = render_wrap_html(
                meta={"title": "T", "author": "A", "summary": "S."},
                cover_path=cover,
                html_path=root / "wrap.html",
                spec=spec,
                page_count=200,
            )
        self.assertIn(DEFAULT_BACK_COLORS["background"], html)
        self.assertIn("back-head", html)
        self.assertIn("spine-rule", html)
        self.assertNotIn("background: #ffffff", html)

    def test_wrap_plain_only_when_explicitly_disabled(self) -> None:
        """Schlicht gibt es nur noch bewusst: styled: false."""
        from lib.print_wrap import render_wrap_html

        spec = PrintSpec.from_dict({}, REPO_ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cover = root / "cover-print.jpg"
            cover.write_bytes(b"img")
            html = render_wrap_html(
                meta={
                    "book": {"title": "T", "author": "A", "summary": "S."},
                    "print": {"back_cover": {"styled": False}},
                },
                cover_path=cover,
                html_path=root / "wrap.html",
                spec=spec,
                page_count=200,
            )
        self.assertIn("background: #ffffff", html)
        self.assertNotIn("back-head", html)
        self.assertNotIn("author-bio", html)

    def test_wrap_styled_back_cover_from_export_document(self) -> None:
        """`print.back_cover` gestaltet die Rueckseite (Dokumentform wie in
        export.yaml, Buchdaten unter `book`). Genau diese Form uebergibt
        build_cover.py - vorher kam nur `book` an und die Gestaltung fiel
        stillschweigend auf Weiss zurueck (Befund 2026-11-11)."""
        from lib.print_wrap import back_cover_settings, render_wrap_html

        spec = PrintSpec.from_dict({}, REPO_ROOT)
        meta = {
            "book": {"title": "Der Pharao", "author": "Boleslaw Prus", "summary": "S."},
            "print": {
                "back_cover": {
                    "styled": True,
                    "colors": {"background": "#f4ecdc", "heading": "#8c2b1c"},
                    "tagline": "Macht und Wissen.",
                    "quote": "Aegypten ist ein Geschenk des Nils.",
                    "quote_source": "Herodot",
                    "author_bio": "Boleslaw Prus (1847-1912).",
                }
            },
        }
        self.assertTrue(back_cover_settings(meta)["styled"])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cover = root / "cover-print.jpg"
            cover.write_bytes(b"img")
            html = render_wrap_html(
                meta=meta,
                cover_path=cover,
                html_path=root / "wrap.html",
                spec=spec,
                page_count=640,
            )
        self.assertIn("background: #f4ecdc", html)
        self.assertIn("Der Pharao", html)
        self.assertIn("Boleslaw Prus", html)
        self.assertIn("back-head", html)
        self.assertIn("author-bio", html)
        self.assertIn("Herodot", html)
        self.assertIn("spine-rule", html)
        self.assertNotIn("background: #ffffff", html)
        self.assertNotIn("}}", html)

    def test_back_cover_colors_fall_back(self) -> None:
        from lib.print_wrap import back_cover_settings

        cfg = back_cover_settings(
            {"print": {"back_cover": {"styled": True, "colors": {"heading": ""}}}}
        )
        self.assertEqual(cfg["colors"]["heading"], DEFAULT_BACK_COLORS["heading"])
        self.assertEqual(cfg["colors"]["background"], DEFAULT_BACK_COLORS["background"])

    def test_back_cover_flat_meta_still_works(self) -> None:
        """Flache Metadaten (aeltere Aufrufer) bleiben lesbar."""
        from lib.print_wrap import back_cover_copy

        title, author, _summary = back_cover_copy(
            {"title": "T", "author": "A", "summary": "S."}
        )
        self.assertEqual((title, author), ("T", "A"))

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

    def test_folio_overlay_embeds_the_book_font(self) -> None:
        """Folios frueher als Helvetica (nicht eingebettet) - KDP hat sie ersetzt."""
        from pypdf import PdfReader

        from lib.print_pdf import _folios_overlay_pdf

        spec = PrintSpec.from_dict({}, REPO_ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            path = _folios_overlay_pdf(
                Path(tmp) / "folios.pdf",
                spec,
                Path(tmp),
                [1, 2, 3],
                width_pt=396.0,
                height_pt=612.0,
                margin_pt=45.0,
                folio_y_pt=28.0,
            )
            reader = PdfReader(str(path))
            self.assertGreaterEqual(len(reader.pages), 3)
            fonts = (reader.pages[0].get("/Resources") or {}).get("/Font") or {}
            names = [
                str(ref.get_object().get("/BaseFont")) for ref in fonts.values()
            ]
            self.assertTrue(names, "keine Schrift im Folio-Overlay")
            self.assertFalse(
                any("Helvetica" in name for name in names),
                f"Helvetica im Folio-Overlay: {names}",
            )

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


class BlankPageTests(unittest.TestCase):
    def _pdf_with_blank_and_text_page(self, path: Path) -> None:
        from pypdf import PdfReader, PdfWriter

        writer = PdfWriter()
        writer.add_blank_page(width=200, height=200)
        text_page = PdfReader(
            io.BytesIO(_helvetica_overlay_pdf(200, 200, 20, 100, "Impressum", 9.0))
        ).pages[0]
        writer.add_page(text_page)
        writer.add_blank_page(width=200, height=200)
        with path.open("wb") as handle:
            writer.write(handle)

    def test_find_blank_pages_reports_empty_pages(self) -> None:
        from lib.print_pdf import blank_page_warning, find_blank_pages

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "interior.pdf"
            self._pdf_with_blank_and_text_page(path)
            blanks = find_blank_pages(path)
        self.assertEqual(blanks, [1, 3])

    def test_blank_page_warning_names_the_pages(self) -> None:
        from lib.print_pdf import blank_page_warning

        text = blank_page_warning([1, 3])
        self.assertIn("2 Leerseite(n)", text)
        self.assertIn("1, 3", text)
        self.assertIn("fill_height_mm", text)

    @unittest.skipUnless(
        importlib.util.find_spec("pypdfium2"), "pypdfium2 optional"
    )
    def test_frontmatter_fill_flags_sparse_pages(self) -> None:
        """Eine fast leere Titelei-Seite soll als `sparse` gemeldet werden -
        sie ist die Seite, die sich im Druck einsparen laesst."""
        from lib.print_pdf import frontmatter_fill_report

        spec = load_print_spec(REPO_ROOT, {})
        from pypdf import PdfReader, PdfWriter

        writer = PdfWriter()
        # 5.5x8.5in = 396x612pt; Satzspiegel 16mm..(612-18mm)
        sparse = PdfReader(
            io.BytesIO(_helvetica_overlay_pdf(396, 612, 40, 500, "Wenig Text", 9.0))
        ).pages[0]
        full = PdfReader(
            io.BytesIO(_helvetica_overlay_pdf(396, 612, 40, 100, "Viel Text", 9.0))
        ).pages[0]
        writer.add_page(sparse)
        writer.add_page(full)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "interior.pdf"
            with path.open("wb") as handle:
                writer.write(handle)
            fill = frontmatter_fill_report(path, 2, spec)

        self.assertEqual([item["page"] for item in fill], [1, 2])
        self.assertTrue(fill[0]["sparse"])
        self.assertLess(fill[0]["used_percent"], 20.0)
        self.assertFalse(fill[1]["sparse"])
        self.assertGreater(fill[1]["used_percent"], 80.0)

    def test_sparse_frontmatter_warning_names_the_switches(self) -> None:
        from lib.print_pdf import sparse_frontmatter_warning

        text = sparse_frontmatter_warning(
            [
                {"page": 1, "used_percent": 72.1, "sparse": False},
                {"page": 3, "used_percent": 19.8, "sparse": True},
            ]
        )
        self.assertIn("3 (20%)", text)
        self.assertNotIn("1 (", text)
        self.assertIn("author_bio_page", text)

    def test_paperback_report_lists_blank_pages(self) -> None:
        spec = load_print_spec(REPO_ROOT, {})

        def fake_render(_html_path: Path, pdf_path: Path) -> None:
            self._pdf_with_blank_and_text_page(pdf_path)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = export_paperback_interior(
                spec=spec,
                chapters=[
                    export.ChapterExport(
                        "001", "K", [export.SceneExport(1, "kurz")], [], 1, 1
                    )
                ],
                html_text='<section class="frontmatter-page titlepage"></section>',
                html_path=root / "book.paperback.html",
                css_path=root / "book-paperback.css",
                pdf_path=root / "interior.pdf",
                report_path=root / "print-report.json",
                author="Autor",
                title="Titel",
                render_pdf=fake_render,
                stamp=False,
            )
        self.assertEqual(report["blank_pages"], [1, 3])
        self.assertTrue(any("Leerseite" in w for w in report["warnings"]))
        self.assertEqual(report["status"], "warning")


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


class MasterAssetTests(unittest.TestCase):
    """Zweite Bild-Ebene: assets/master/ fuer den Taschenbuchsatz."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.book = self.root / "books" / "sample"
        self.assets = self.book / "assets"
        self.addCleanup(self.tmp.cleanup)

    def _write(self, rel: str, size: tuple[int, int]) -> Path:
        from PIL import Image

        path = self.assets / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", size, (30, 60, 90)).save(path, format="JPEG", quality=90)
        return path

    def test_output_path_targets_master_folder(self) -> None:
        import generate_illustration as gi

        book = {"book_root": str(self.book)}
        request = gi.IllustrationRequest(
            book_id="sample",
            chapter_id="007",
            scene_number=None,
            style="s",
            kind="chapter",
            model="gpt_image_2",
            moodboard="",
            images=(),
            no_reference=True,
            aspect_ratio="3:4",
            quality="2k",
            overwrite=False,
        )
        reader = gi.output_image_path(book, request, {"format": "JPEG"})
        master = gi.output_image_path(book, request, {"format": "JPEG"}, master=True)
        self.assertEqual(
            reader, self.book / "assets" / "chapter" / "chapter-007.jpg"
        )
        self.assertEqual(
            master,
            self.book / "assets" / MASTER_DIRNAME / "chapter" / "chapter-007.jpg",
        )

    def test_master_processing_defaults_and_override(self) -> None:
        self.assertEqual(load_master_processing({}), DEFAULT_MASTER_PROCESSING)
        book = {
            "higgsfield": {
                "image_processing": {
                    "max_width": 1024,
                    "master": {"jpeg_quality": 88, "max_width": 3000},
                }
            }
        }
        cfg = load_master_processing(book)
        # Nur der master-Block ueberschreibt, der Reader-Block nicht.
        self.assertEqual(cfg["jpeg_quality"], 88)
        self.assertEqual(cfg["max_width"], 3000)
        self.assertEqual(cfg["max_height"], 2048)

    def test_keep_master_switch(self) -> None:
        self.assertTrue(master_assets_enabled({}))
        self.assertTrue(master_assets_enabled({"higgsfield": {}}))
        self.assertFalse(
            master_assets_enabled({"higgsfield": {"keep_master": False}})
        )

    def test_is_master_path(self) -> None:
        self.assertTrue(is_master_path(Path("a/assets/master/chapter/c.jpg")))
        self.assertFalse(is_master_path(Path("a/assets/chapter/c.jpg")))

    def test_export_prefers_master_for_print(self) -> None:
        self._write("chapter/chapter-001.jpg", (768, 1024))
        self._write("master/chapter/chapter-001.jpg", (1536, 2048))
        meta = {
            "_base_dir": str(self.book),
            "illustrations": {"enabled": True, "chapter_images": True},
        }
        reader = export.chapter_illustration(meta, "001")
        printed = export.chapter_illustration(meta, "001", prefer_master=True)
        assert reader is not None and printed is not None
        self.assertNotIn(MASTER_DIRNAME, Path(reader.path).parts)
        self.assertIn(MASTER_DIRNAME, Path(printed.path).parts)

    def test_export_falls_back_to_reader_without_master(self) -> None:
        self._write("chapter/chapter-002.jpg", (768, 1024))
        meta = {
            "_base_dir": str(self.book),
            "illustrations": {"enabled": True, "chapter_images": True},
        }
        printed = export.chapter_illustration(meta, "002", prefer_master=True)
        assert printed is not None
        self.assertNotIn(MASTER_DIRNAME, Path(printed.path).parts)

    def test_scene_master_resolution(self) -> None:
        self._write("scene/003/scene-001.jpg", (768, 1024))
        self._write("master/scene/003/scene-001.jpg", (1536, 2048))
        meta = {
            "_base_dir": str(self.book),
            "illustrations": {"enabled": True, "scene_images": True},
        }
        printed = export.scene_illustration(meta, "003", 1, prefer_master=True)
        assert printed is not None
        self.assertIn(MASTER_DIRNAME, Path(printed.path).parts)

    def test_tier_summary_counts_master(self) -> None:
        class Item:
            def __init__(self, path: str) -> None:
                self.path = path

        items = [
            Item("assets/master/chapter/chapter-001.jpg"),
            Item("assets/chapter/chapter-002.jpg"),
        ]
        summary = illustration_tier_summary(items)
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["master"], 1)
        self.assertEqual(summary["reader"], 1)

    def test_optimizer_reads_master_but_writes_reader(self) -> None:
        self._write("master/chapter/chapter-001.jpg", (1536, 2048))
        found = discover_export_assets(
            self.book,
            include_cover=False,
            include_scene=False,
            from_master=True,
        )
        self.assertEqual(len(found), 1)
        item = found[0]
        self.assertIn(MASTER_DIRNAME, item.source.parts)
        # Ziel bleibt ausserhalb von master/ – Originale werden nie ersetzt.
        self.assertNotIn(MASTER_DIRNAME, item.jpeg_target.parts)
        self.assertEqual(
            item.jpeg_target, self.assets / "chapter" / "chapter-001.jpg"
        )

    def test_optimizer_default_ignores_master_folder(self) -> None:
        self._write("chapter/chapter-001.jpg", (768, 1024))
        self._write("master/chapter/chapter-002.jpg", (1536, 2048))
        found = discover_export_assets(
            self.book,
            include_cover=False,
            include_scene=False,
        )
        stems = {item.jpeg_target.stem for item in found}
        self.assertIn("chapter-001", stems)
        self.assertNotIn("chapter-002", stems)


class GitignoreAssetsTests(unittest.TestCase):
    """Pro-Buch-Schalter gegen grosse, regenerierbare Medien."""

    def setUp(self) -> None:
        self.config = load_config(REPO_ROOT)

    def test_default_config_lists_master_folder(self) -> None:
        self.assertIn("/assets/master/", self.config["patterns"])
        self.assertIn("/assets/video/", self.config["patterns"])

    def test_config_fallback_keeps_markers(self) -> None:
        """Ohne config/gitignore-assets.yaml muss es trotzdem renderbar bleiben."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            config = load_config(Path(tmp))
        self.assertEqual(config["patterns"], ["/assets/master/"])
        self.assertTrue(config["begin_marker"].startswith("# >>>"))
        self.assertTrue(config["end_marker"].startswith("# <<<"))
        text = render_gitignore("", {"gitignore": {"large_assets": True}}, config)
        self.assertIn("/assets/master/", text)

    def test_switch_defaults_to_active(self) -> None:
        self.assertTrue(book_switch({})["large_assets"])
        self.assertIn("/assets/master/", effective_patterns({}, self.config))

    def test_switch_off_yields_no_patterns(self) -> None:
        book = {"gitignore": {"large_assets": False}}
        self.assertEqual(effective_patterns(book, self.config), [])
        self.assertIn("Kein Ausschluss", render_gitignore("", book, self.config))

    def test_extra_and_disabled_patterns(self) -> None:
        book = {
            "gitignore": {
                "extra_patterns": ["/work/gross/"],
                "disabled_patterns": ["/assets/video/"],
            }
        }
        patterns = effective_patterns(book, self.config)
        self.assertIn("/work/gross/", patterns)
        self.assertNotIn("/assets/video/", patterns)
        self.assertIn("/assets/master/", patterns)

    def test_render_is_idempotent(self) -> None:
        book = {"gitignore": {"large_assets": True}}
        once = render_gitignore("", book, self.config)
        self.assertEqual(render_gitignore(once, book, self.config), once)
        self.assertEqual(gitignore_state(once, book, self.config), "ok")
        self.assertEqual(gitignore_state("", book, self.config), "abweichend")

    def test_foreign_lines_are_preserved(self) -> None:
        book = {"gitignore": {"large_assets": True}}
        text = render_gitignore("eigene-regel/\n", book, self.config)
        self.assertTrue(text.startswith("eigene-regel/"))
        self.assertIn("/assets/master/", text)
        self.assertEqual(render_gitignore(text, book, self.config), text)

    def test_changed_patterns_replace_block_in_place(self) -> None:
        first = render_gitignore(
            "kopf/\nfuss/\n", {"gitignore": {"large_assets": True}}, self.config
        )
        book2 = {
            "gitignore": {
                "large_assets": True,
                "disabled_patterns": ["/assets/video/"],
            }
        }
        second = render_gitignore(first, book2, self.config)
        self.assertNotIn("/assets/video/", second)
        self.assertEqual(second.count("/assets/master/"), 1)
        self.assertTrue(second.startswith("kopf/"))
        self.assertEqual(gitignore_state(second, book2, self.config), "ok")

    def test_repo_books_all_have_current_switch(self) -> None:
        """Alle Buchpakete muessen den verwalteten Abschnitt fuehren."""
        import yaml

        books = sorted((REPO_ROOT / "books").glob("*/book.yaml"))
        self.assertTrue(books, "keine Buchpakete gefunden")
        for book_yaml in books:
            data = yaml.safe_load(book_yaml.read_text(encoding="utf-8")) or {}
            path = REPO_ROOT / "books" / str(data["id"]) / ".gitignore"
            with self.subTest(book=data["id"]):
                self.assertTrue(path.is_file(), f"{path} fehlt")
                state = gitignore_state(
                    path.read_text(encoding="utf-8"), data, self.config
                )
                self.assertEqual(state, "ok")


if __name__ == "__main__":
    unittest.main()
