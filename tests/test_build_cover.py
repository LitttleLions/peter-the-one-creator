from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import build_cover as cover  # noqa: E402
from lib.print_spec import PrintSpec  # noqa: E402


class GeometryTests(unittest.TestCase):
    def _spec(self, trim: str, paper: str = "cream") -> PrintSpec:
        return PrintSpec.from_dict(
            {"trim_size": trim, "paper": paper}, REPO_ROOT
        )

    def test_6x9_332_pages_matches_kdp_expectation(self) -> None:
        """KDP meldete 13,080 x 9,250 in - genau das muss hier herauskommen."""
        geometry = cover.wrap_geometry(self._spec("6x9"), 332)
        self.assertAlmostEqual(geometry["width_in"], 13.08, places=2)
        self.assertAlmostEqual(geometry["height_in"], 9.25, places=2)
        self.assertAlmostEqual(geometry["spine_mm"], 21.08, places=1)

    def test_5_5x8_5_330_pages(self) -> None:
        geometry = cover.wrap_geometry(self._spec("5.5x8.5"), 330)
        self.assertAlmostEqual(geometry["width_in"], 12.075, places=3)
        self.assertAlmostEqual(geometry["height_in"], 8.75, places=2)

    def test_spine_grows_with_page_count(self) -> None:
        spec = self._spec("6x9")
        small = cover.wrap_geometry(spec, 200)["spine_mm"]
        large = cover.wrap_geometry(spec, 500)["spine_mm"]
        self.assertGreater(large, small)
        self.assertAlmostEqual(large - small, (500 - 200) * 0.0635, places=2)

    def test_paper_changes_spine(self) -> None:
        cream = cover.wrap_geometry(self._spec("6x9", "cream"), 300)["spine_mm"]
        white = cover.wrap_geometry(self._spec("6x9", "white"), 300)["spine_mm"]
        self.assertNotAlmostEqual(cream, white, places=1)


class CoverLookupTests(unittest.TestCase):
    def test_missing_cover_returns_none(self) -> None:
        self.assertIsNone(cover.find_print_cover(Path("C:/gibt/es/nicht")))


if __name__ == "__main__":
    unittest.main()
