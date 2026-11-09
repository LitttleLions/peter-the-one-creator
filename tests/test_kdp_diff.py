from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib.kdp_diff import diff_listing, render_diff_markdown  # noqa: E402


def _soll() -> dict:
    return {
        "title": "Der Pharao",
        "subtitle": "Untertitel",
        "language": "German",
        "publisherLabel": "Motivatier Stiftung",
        "primaryAuthor": {"firstName": "Bolesław", "lastName": "Prus"},
        "contributors": [
            {"role": "Translator", "firstName": "", "lastName": "Motivatier Classics"},
        ],
        "description": "Erster Absatz.\n\nZweiter Absatz.",
        "isPublicDomain": False,
        "isAdultContent": False,
        "keywords": None,
        "categories": None,
        "prices": None,
        "formats": {
            "kindle": {
                "interior_path": "exports/stil/book/epub/book.epub",
                "cover_path": "assets/covers/cover.jpg",
            }
        },
    }


class DiffTests(unittest.TestCase):
    def test_html_description_can_match_and_prices_stay_local_missing(self) -> None:
        ist = {
            "title": "Der Pharao",
            "subtitle": "Untertitel",
            "language": "German",
            "publisherLabel": "Motivatier Stiftung",
            "primaryAuthor": {"firstName": "Bolesław", "lastName": "Prus"},
            "contributors": [
                {"role": "Translator", "firstName": "", "lastName": "Motivatier Classics"},
            ],
            "description": "<p>Erster Absatz.</p><p>Zweiter Absatz.</p>",
            "isPublicDomain": False,
            "isAdultContent": False,
            "keywords": ["ägypten", "roman"],
            "categories": ["Literature"],
            "prices": {"USD": "9.99"},
            "listPriceUsd": "9.99",
            "isbn": "123",
            "kdpSelect": True,
            "territory": "worldwide",
            "royaltyPlan": "70",
            "interiorFileName": "other.pdf",
            "coverFileName": "cover.jpg",
        }
        rows = {row["field"]: row for row in diff_listing(_soll(), ist, fmt="kindle")}
        self.assertEqual(rows["description"]["status"], "same")
        self.assertEqual(rows["title"]["status"], "same")
        self.assertEqual(rows["keywords"]["status"], "local_missing")
        self.assertEqual(rows["prices"]["status"], "local_missing")
        self.assertEqual(rows["kdpSelect"]["status"], "local_missing")
        self.assertEqual(rows["isbn"]["status"], "local_missing")
        self.assertEqual(rows["interior"]["status"], "different")
        self.assertEqual(rows["cover"]["status"], "same")
        self.assertTrue(all(row["apply"] is False for row in rows.values()))
        self.assertIn("kein lokales Soll", rows["keywords"]["note"])

    def test_changed_title_is_different_not_a_write(self) -> None:
        ist = {"title": "Faraon", "description": ""}
        rows = {row["field"]: row for row in diff_listing(_soll(), ist, fmt="kindle")}
        self.assertEqual(rows["title"]["status"], "different")
        self.assertEqual(rows["subtitle"]["status"], "amazon_missing")
        markdown = render_diff_markdown("pharao", "kindle", list(rows.values()))
        self.assertIn("status: different", markdown)
        self.assertIn("kein Schreiben", markdown)


if __name__ == "__main__":
    unittest.main()
