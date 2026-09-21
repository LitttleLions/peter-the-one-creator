from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib.series_catalog import (  # noqa: E402
    CatalogEntry,
    catalog_html,
    catalog_markdown,
    compact_summary,
    load_series_catalog,
)


def _write_book(
    root: Path,
    book_id: str,
    *,
    enabled: bool = True,
    catalog: bool | None = None,
    title: str = "Titel",
    author: str = "Autor",
    sort_order: int = 10,
    with_cover: bool = True,
) -> Path:
    book_root = root / "books" / book_id
    (book_root / "assets" / "covers").mkdir(parents=True)
    website = [
        "website:",
        f"  enabled: {str(enabled).lower()}",
        f"  sort_order: {sort_order}",
    ]
    if catalog is not None:
        website.append(f"  catalog: {str(catalog).lower()}")
    (book_root / "export.yaml").write_text(
        "\n".join(
            [
                "book:",
                f"  title: {title}",
                f"  author: {author}",
                "  summary: |",
                "    Erster Absatz des Kurztextes.",
                "",
                "    Zweiter Absatz bleibt aussen vor.",
                *website,
                "",
            ]
        ),
        encoding="utf-8",
    )
    if with_cover:
        (book_root / "assets" / "covers" / "cover.jpg").write_bytes(b"cover")
    return book_root


class SeriesCatalogTests(unittest.TestCase):
    def test_compact_summary_uses_first_paragraph(self) -> None:
        text = compact_summary("Eins zwei.\n\nDrei vier.")
        self.assertEqual(text, "Eins zwei.")

    def test_load_skips_current_book_and_catalog_false(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_book(root, "alpha", title="Alpha", sort_order=20)
            _write_book(root, "beta", title="Beta", sort_order=10)
            _write_book(root, "parked", title="Parked", catalog=False)
            _write_book(root, "off", title="Off", enabled=False)
            entries = load_series_catalog(root, exclude_book_id="alpha")
        ids = [item.book_id for item in entries]
        self.assertEqual(ids, ["beta"])
        self.assertNotIn("alpha", ids)
        self.assertNotIn("parked", ids)
        self.assertNotIn("off", ids)

    def test_markdown_and_html_share_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cover = Path(tmp) / "cover.jpg"
            cover.write_bytes(b"x")
            entry = CatalogEntry(
                book_id="aelita",
                title="Aelita",
                author="Alexei Tolstoi",
                summary="Ein Marsroman.",
                cover_path=cover,
                sort_order=10,
            )
            md_path = Path(tmp) / "book.md"
            html_path = Path(tmp) / "book.html"
            markdown = "\n".join(catalog_markdown([entry], md_path))
            html = "\n".join(catalog_html([entry], html_path))
        self.assertIn("Weitere Motivatier Classics", markdown)
        self.assertIn("Weitere Motivatier Classics", html)
        self.assertIn("Aelita", markdown)
        self.assertIn("Alexei Tolstoi", html)
        self.assertIn("series-entry", markdown)
        self.assertIn("series-catalog", html)
        self.assertEqual(catalog_markdown([], md_path), [])
        self.assertEqual(catalog_html([], html_path), [])

    def test_repo_catalog_honors_exclusions(self) -> None:
        entries = load_series_catalog(REPO_ROOT, exclude_book_id="pharao")
        ids = {item.book_id for item in entries}
        self.assertNotIn("pharao", ids)
        self.assertNotIn("anna-karenina", ids)
        self.assertNotIn("pissemski-tausend-seelen", ids)
        self.assertNotIn("grin-wellenlaeuferin", ids)
        self.assertTrue(ids)


if __name__ == "__main__":
    unittest.main()
