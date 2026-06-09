from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib.book_project import find_book, load_books, write_yaml  # noqa: E402


class BookProjectTests(unittest.TestCase):
    def test_discovers_book_package_and_derives_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book_root = root / "books" / "sample-book"
            write_yaml(
                book_root / "book.yaml",
                {
                    "id": "sample-book",
                    "title": "Sample",
                    "author": "Author",
                    "source_path": "source/sample.rtf",
                    "source_lang": "ru",
                    "target_lang": "de",
                    "style_mode": "stil-01-original",
                },
            )
            books = load_books(root)
            book = find_book(root, "sample-book")

        self.assertEqual([item["id"] for item in books], ["sample-book"])
        self.assertEqual(book["source_path"], "books/sample-book/source/sample.rtf")
        self.assertEqual(book["work_dir"], "books/sample-book/work")
        self.assertEqual(book["exports_dir"], "books/sample-book/exports")
        self.assertEqual(book["status_file"], "books/sample-book/status/status.json")
        self.assertEqual(book["styles_dir"], "books/sample-book/styles")


if __name__ == "__main__":
    unittest.main()
