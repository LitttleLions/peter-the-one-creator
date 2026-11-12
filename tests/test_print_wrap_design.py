"""Gestaltung der Umschlag-Rueckseite (Review 2026-11-12)."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib.print_spec import PrintSpec  # noqa: E402
from lib.print_wrap import (  # noqa: E402
    DEFAULT_BACK_COLORS,
    FIT_LEVELS,
    back_cover_settings,
    contrast_ratio,
    derive_palette,
    footer_line,
    header_line,
    render_fitted_wrap_html,
    render_wrap_html,
)


def _meta(**book: object) -> dict:
    base = {
        "title": "Der Pharao",
        "author": "Boleslaw Prus",
        "description": "Wer herrscht, muss wissen.\n\nZweiter Absatz.",
    }
    base.update(book)
    return {"book": base}


class WrapDesignTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.spec = PrintSpec.from_dict({}, REPO_ROOT)
        self.cover = self.root / "cover-print.png"
        from PIL import Image

        Image.new("RGB", (200, 300), (30, 70, 120)).save(self.cover)

    def _html(self, meta: dict, pages: int = 332, cover: Path | None = None, **kw) -> str:
        return render_wrap_html(
            meta=meta,
            cover_path=cover or self.cover,
            html_path=self.root / "wrap.html",
            spec=self.spec,
            page_count=pages,
            **kw,
        )

    def test_palette_from_cover_edge(self) -> None:
        palette = derive_palette(self.cover)
        assert palette is not None
        self.assertNotEqual(palette["background"], DEFAULT_BACK_COLORS["background"])
        self.assertGreaterEqual(
            contrast_ratio(palette["text"], palette["background"]), 7.0
        )
        self.assertGreaterEqual(
            contrast_ratio(palette["spine_text"], palette["spine"]), 7.0
        )

    def test_explicit_colors_win_over_derived(self) -> None:
        meta = _meta()
        meta["print"] = {"back_cover": {"colors": {"background": "#ffeedd"}}}
        cfg = back_cover_settings(meta, self.cover)
        self.assertEqual(cfg["colors"]["background"], "#ffeedd")
        self.assertNotEqual(cfg["colors"]["heading"], DEFAULT_BACK_COLORS["heading"])

    def test_unreadable_cover_falls_back_to_defaults(self) -> None:
        bad = self.root / "bad.png"
        bad.write_bytes(b"kein bild")
        cfg = back_cover_settings(_meta(), bad)
        self.assertEqual(cfg["colors"], DEFAULT_BACK_COLORS)

    def test_header_line_series_then_publisher_then_nothing(self) -> None:
        self.assertEqual(header_line(_meta(series="Reihe", publisher="Verlag")), "Reihe")
        self.assertEqual(header_line(_meta(publisher="Verlag")), "Verlag")
        self.assertEqual(header_line(_meta()), "")
        self.assertNotIn("class='brand'", self._html(_meta()))
        # Verlag steht nicht doppelt, wenn er schon die Kopfzeile ist
        self.assertEqual(footer_line(_meta(publisher="Verlag")), "")
        self.assertEqual(footer_line(_meta(series="Reihe", publisher="Verlag")), "Verlag")

    def test_initial_only_for_letters(self) -> None:
        self.assertIn("class='dropcap'", self._html(_meta()))
        digits = _meta(description="1241 war ein Jahr.")
        self.assertNotIn("class='dropcap'", self._html(digits))

    def test_empty_fields_leave_no_traces(self) -> None:
        html = self._html(_meta(author="", description=""))
        self.assertNotIn("<p class='author'>", html)
        self.assertNotIn("class='blurb'", html)
        self.assertNotIn("class='author-bio'", html)

    def test_subtitle_only_when_short(self) -> None:
        self.assertIn("class='subtitle'", self._html(_meta(subtitle="Ein Roman")))
        self.assertNotIn("class='subtitle'", self._html(_meta(subtitle="x" * 80)))

    def test_html_language_and_hyphenation(self) -> None:
        html = self._html(_meta(language="de-DE"))
        self.assertIn("<html lang='de'>", html)
        self.assertIn("hyphens: auto", html)

    def test_no_barcode_drawing_but_space_reserved(self) -> None:
        html = self._html(_meta())
        self.assertIn("barcode-reserve", html)
        self.assertNotIn("dashed", html)
        self.assertNotIn("border: 0.3pt", html)

    def test_spine_text_depends_on_thickness(self) -> None:
        thin = self._html(_meta(publisher="Verlag"), pages=60)
        self.assertNotIn("<span>", thin)
        self.assertNotIn("class='spine-rule", thin)
        normal = self._html(_meta(publisher="Verlag"), pages=332)
        self.assertIn("<span>Boleslaw Prus", normal)
        self.assertNotIn("spine-pub'>", normal)  # 21 mm: noch kein Verlag
        thick = self._html(_meta(publisher="Verlag"), pages=600)
        self.assertIn("spine-pub'>Verlag", thick)

    def test_spine_font_scales_with_width(self) -> None:
        self.assertIn("font-size: 14.0pt", self._html(_meta(), pages=332))
        small = self._html(_meta(), pages=100)  # 6,35 mm Ruecken
        self.assertNotIn("font-size: 14.0pt", small)

    def test_fit_uses_first_level_that_fits(self) -> None:
        calls: list[int] = []

        def measure(_path: Path) -> float:
            calls.append(1)
            return 0.0 if len(calls) >= 3 else 120.0

        html, notes, fits = render_fitted_wrap_html(
            meta=_meta(),
            cover_path=self.cover,
            html_path=self.root / "fit.html",
            spec=self.spec,
            page_count=332,
            measure=measure,
        )
        self.assertTrue(fits)
        self.assertEqual(len(calls), 3)
        self.assertIn(f"{FIT_LEVELS[2]['blurb_pt']}pt", html)
        self.assertTrue(notes)

    def test_fit_drops_quote_last_and_keeps_bio(self) -> None:
        meta = _meta(author_bio="Kurzbio.")
        meta["print"] = {"back_cover": {"quote": "Ein Zitat.", "quote_source": "Quelle"}}
        seen: list[str] = []

        def measure(path: Path) -> float:
            seen.append(path.read_text(encoding="utf-8"))
            return 50.0

        html, notes, fits = render_fitted_wrap_html(
            meta=meta,
            cover_path=self.cover,
            html_path=self.root / "fit.html",
            spec=self.spec,
            page_count=332,
            measure=measure,
        )
        self.assertFalse(fits)
        self.assertIn("class='quote'", seen[0])
        self.assertNotIn("class='quote'", html)
        self.assertIn("class='author-bio'", html)
        self.assertTrue(any("kuerzen" in n for n in notes))

    def test_fit_without_measure_is_plain_render(self) -> None:
        html, notes, fits = render_fitted_wrap_html(
            meta=_meta(),
            cover_path=self.cover,
            html_path=self.root / "fit.html",
            spec=self.spec,
            page_count=332,
        )
        self.assertTrue(fits)
        self.assertEqual(notes, [])
        self.assertNotIn("}}", html)


if __name__ == "__main__":
    unittest.main()
