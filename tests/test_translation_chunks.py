from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib.translation_chunks import (  # noqa: E402
    chunk_char_limit,
    de_chunk_path,
    scene_chunks,
    split_text_chunks,
)


class TranslationChunkTests(unittest.TestCase):
    def test_limit_comes_from_book_before_pipeline(self) -> None:
        book = {"ai": {"chunk_char_limit": 12345}}
        pipeline = {"pipeline": {"ai_defaults": {"chunk_char_limit": 24000}}}

        self.assertEqual(chunk_char_limit(book, pipeline), 12345)

    def test_split_keeps_small_text_single_chunk(self) -> None:
        self.assertEqual(split_text_chunks("kurzer text", 24000), ["kurzer text"])

    def test_split_large_text_on_paragraph_boundaries(self) -> None:
        text = "a" * 9000 + "\n\n" + "b" * 9000 + "\n\n" + "c" * 9000

        chunks = split_text_chunks(text, 18100)

        self.assertEqual(len(chunks), 2)
        self.assertIn("a" * 20, chunks[0])
        self.assertIn("b" * 20, chunks[0])
        self.assertIn("c" * 20, chunks[1])

    def test_scene_chunks_have_part_numbers(self) -> None:
        chunks = scene_chunks(1, "a" * 100 + "\n\n" + "b" * 100, 120)

        self.assertEqual([(c.part, c.total) for c in chunks], [(1, 2), (2, 2)])

    def test_de_chunk_path_keeps_chunks_outside_scene_outputs(self) -> None:
        book = {"work_dir": "books/sample/work"}

        path = de_chunk_path(Path("repo"), book, "stil", "006", 1, 2)

        self.assertEqual(
            path,
            Path("repo/books/sample/work/chunks/de/stil/006/scene-01/part-02.md"),
        )


if __name__ == "__main__":
    unittest.main()
