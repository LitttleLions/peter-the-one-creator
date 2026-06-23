from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib.translation_chunks import (  # noqa: E402
    _detect_overlap,
    _strip_tail_overlap,
    chunk_char_limit,
    de_chunk_path,
    render_chunked_translation,
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


class OverlapDetectionTests(unittest.TestCase):
    def test_no_overlap_different_text(self) -> None:
        self.assertEqual(
            _detect_overlap("Ende des ersten Teils.", "Anfang des zweiten Teils."),
            0,
        )

    def test_detect_repeated_sentence_overlap(self) -> None:
        tail = "Sie blickte langsam zum Fenster hinauf."
        head = "Sie blickte langsam zum Fenster hinauf. Der Mond schien hell."
        overlap = _detect_overlap(tail, head)
        self.assertGreater(overlap, 20)

    def test_no_overlap_short_match(self) -> None:
        shared = "der"
        tail = f"Das war {shared}"
        head = f"{shared} Mann ging fort."
        self.assertEqual(_detect_overlap(tail, head), 0)

    def test_strip_tail_overlap_removes_duplicate(self) -> None:
        prev = "Sie blickte zum Fenster."
        current = "Sie blickte zum Fenster. Draußen war es dunkel."
        result = _strip_tail_overlap(prev, current)
        self.assertEqual(result, "Draußen war es dunkel.")

    def test_strip_tail_overlap_no_op(self) -> None:
        prev = "Das Kapitel endet hier."
        current = "Ein neuer Abschnitt beginnt."
        result = _strip_tail_overlap(prev, current)
        self.assertEqual(result, current)


class RenderChunkedTranslationTests(unittest.TestCase):
    def test_no_overlap_between_parts(self) -> None:
        result = render_chunked_translation([
            "Erster Teil des Textes.",
            "Zweiter Teil des Textes.",
        ])
        expected = "Erster Teil des Textes.\n\nZweiter Teil des Textes."
        self.assertEqual(result, expected)

    def test_removes_overlap_between_parts(self) -> None:
        result = render_chunked_translation([
            "Sie trat ein und sah sich um.",
            "Sie trat ein und sah sich um. Der Raum war leer und dunkel.",
        ])
        expected = "Sie trat ein und sah sich um.\n\nDer Raum war leer und dunkel."
        self.assertEqual(result, expected)

    def test_single_part_passes_through(self) -> None:
        result = render_chunked_translation(["Ein einziger Abschnitt."])
        self.assertEqual(result, "Ein einziger Abschnitt.")

    def test_three_parts_with_overlap(self) -> None:
        result = render_chunked_translation([
            "Am Morgen ging er zum Markt.",
            "Am Morgen ging er zum Markt. Dort kaufte er Brot.",
            "Dort kaufte er Brot. Danach kehrte er heim.",
        ])
        expected = (
            "Am Morgen ging er zum Markt.\n\n"
            "Dort kaufte er Brot.\n\n"
            "Danach kehrte er heim."
        )
        self.assertEqual(result, expected)

    def test_empty_parts_are_skipped(self) -> None:
        result = render_chunked_translation(["", "Einziger Inhalt.", ""])
        self.assertEqual(result, "Einziger Inhalt.")


if __name__ == "__main__":
    unittest.main()
