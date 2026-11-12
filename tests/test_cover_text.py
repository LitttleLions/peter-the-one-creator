"""Typografie-Block fuer Cover-Prompts."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from cover_text import cover_text_block  # noqa: E402


class CoverTextTests(unittest.TestCase):
    def test_brand_top_publisher_bottom(self) -> None:
        meta = {"book": {"title": "Der Pharao", "author": "Boleslaw Prus",
                         "editor": "Motivatier Classics", "publisher": "Motivatier Stiftung"}}
        block = cover_text_block(meta)
        self.assertLess(block.index("MOTIVATIER CLASSICS"), block.index("DER PHARAO"))
        self.assertLess(block.index("BOLESLAW PRUS"), block.index("MOTIVATIER STIFTUNG"))

    def test_publisher_only_not_repeated(self) -> None:
        block = cover_text_block({"book": {"title": "X", "publisher": "Verlag"}})
        self.assertEqual(block.count("VERLAG"), 1)


if __name__ == "__main__":
    unittest.main()
