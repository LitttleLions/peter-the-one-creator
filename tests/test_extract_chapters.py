from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import extract_chapters as extract  # noqa: E402
from lib.rtf_parser import Block, parse_rtf  # noqa: E402


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

    def test_plain_text_source_splits_english_chapter_markers(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.txt"
            path.write_text(
                "Project Gutenberg header\n\n"
                "CHAPTER I\n\n"
                "First chapter text.\n\n"
                "CHAPTER II\n\n"
                "Second chapter text.\n\n"
                "*** END OF THE PROJECT GUTENBERG EBOOK SAMPLE ***\n\n"
                "License text that must not enter the chapter.\n",
                encoding="utf-8",
            )
            blocks, meta = parse_rtf(path)

        segments = extract.build_chapter_segments(blocks)
        self.assertEqual(meta["source_format"], "plain_text")
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0][0], "CHAPTER I")
        self.assertEqual(segments[0][1][0].text, "First chapter text.")
        self.assertEqual(segments[1][0], "CHAPTER II")
        self.assertEqual(segments[1][1][0].text, "Second chapter text.")


if __name__ == "__main__":
    unittest.main()
