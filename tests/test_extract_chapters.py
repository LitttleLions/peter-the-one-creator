from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import extract_chapters as extract  # noqa: E402
from lib.rtf_parser import Block  # noqa: E402


class ExtractChapterTests(unittest.TestCase):
    def test_fallback_splits_roman_chapters_inside_parts(self) -> None:
        blocks = [
            Block(kind="paragraph", level=0, text="Frontmatter"),
            Block(kind="paragraph", level=0, text="ЧАСТЬ ПЕРВАЯ"),
            Block(kind="paragraph", level=0, text="I"),
            Block(kind="paragraph", level=0, text="Erster Text"),
            Block(kind="paragraph", level=0, text="II"),
            Block(kind="paragraph", level=0, text="Zweiter Text"),
        ]
        segments = extract.build_fallback_segments(blocks)
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0][0], "ЧАСТЬ ПЕРВАЯ - I")
        self.assertEqual(segments[0][1][0].text, "Erster Text")
        self.assertEqual(segments[1][0], "ЧАСТЬ ПЕРВАЯ - II")


if __name__ == "__main__":
    unittest.main()
