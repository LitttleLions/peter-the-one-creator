from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib.kdp_mapping import (  # noqa: E402
    KdpMatchStop,
    asin_from_store_url,
    load_export_document,
    map_kdp_soll,
    match_kdp_title,
    upsert_amazon_join,
)


def _export() -> dict:
    return {
        "book": {
            "title": "Der Pharao",
            "subtitle": "in neuer deutscher Ausgabe",
            "author": "Bolesław Prus",
            "translator": "Motivatier Classics",
            "translator_label": "Übersetzung und editorische Einrichtung",
            "language": "de-DE",
            "publisher": "Motivatier Stiftung",
            "description": "Erster Absatz.\n\nZweiter Absatz.",
            "summary": "Das ist die Titelei und nicht der Klappentext.",
            "author_bio": "Nur für das EPUB.",
            "cover": {"image_path": "assets/covers/cover.jpg"},
        },
        "website": {"amazon_url": ""},
        "author": "Motivatier",
    }


class MappingTests(unittest.TestCase):
    def test_pharao_fields_come_from_export_book(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cover = root / "assets" / "covers"
            cover.mkdir(parents=True)
            (cover / "cover.jpg").write_bytes(b"jpg")
            (cover / "cover-print.png").write_bytes(b"png")
            epub_dir = root / "exports" / "stil-02-poetisch" / "book" / "epub"
            epub_dir.mkdir(parents=True)
            (epub_dir / "book-der-pharao-20260921-120000.epub").write_bytes(b"old")
            (epub_dir / "book-der-pharao-20260921-163814.epub").write_bytes(b"new")
            print_dir = root / "exports" / "stil-02-poetisch" / "book" / "print"
            print_dir.mkdir(parents=True)
            (print_dir / "book-der-pharao-55x85-classic-head-20260921-170000-paperback-interior.pdf").write_bytes(b"i")
            (print_dir / "book-der-pharao-55x85-classic-head-20260921-170000-paperback-wrap.pdf").write_bytes(b"w")
            soll = map_kdp_soll(_export(), book_root=root, style="stil-02-poetisch")

        self.assertEqual(soll["title"], "Der Pharao")
        self.assertEqual(soll["primaryAuthor"], {"firstName": "Bolesław", "lastName": "Prus"})
        self.assertEqual(soll["language"], "German")
        self.assertEqual(soll["publisherLabel"], "Motivatier Stiftung")
        self.assertEqual(soll["description"], "Erster Absatz.\n\nZweiter Absatz.")
        self.assertNotIn("Titelei", soll["description"])
        self.assertFalse(soll["isPublicDomain"])
        self.assertFalse(soll["isAdultContent"])
        self.assertIsNone(soll["keywords"])
        self.assertIsNone(soll["prices"])
        self.assertEqual(
            soll["contributors"],
            [
                {"role": "Translator", "firstName": "", "lastName": "Motivatier Classics"},
                {"role": "Editor", "firstName": "", "lastName": "Motivatier Classics"},
            ],
        )
        self.assertTrue(soll["formats"]["kindle"]["enabled"])
        self.assertFalse(soll["formats"]["paperback"]["enabled"])
        self.assertTrue(soll["formats"]["kindle"]["interior_path"].endswith("20260921-163814.epub"))
        self.assertEqual(soll["formats"]["kindle"]["cover_path"], "assets/covers/cover.jpg")
        self.assertEqual(soll["formats"]["paperback"]["cover_path"], "assets/covers/cover-print.png")
        self.assertTrue(
            soll["formats"]["paperback"]["wrap_path"].endswith(
                "20260921-170000-paperback-wrap.pdf"
            )
        )

    def test_short_link_has_no_asin_but_dp_url_does(self) -> None:
        self.assertEqual(asin_from_store_url("https://amzn.to/3AbcDef"), "")
        self.assertEqual(
            asin_from_store_url("https://www.amazon.de/dp/B0HK567117/"),
            "B0HK567117",
        )

    def test_de_and_person_translator(self) -> None:
        export = _export()
        export["book"]["language"] = "de"
        export["book"]["translator"] = "Ada Klein"
        soll = map_kdp_soll(export, book_root=Path("."), style="stil")
        self.assertEqual(soll["language"], "German")
        self.assertEqual(soll["contributors"][0]["firstName"], "Ada")
        self.assertEqual(soll["contributors"][0]["lastName"], "Klein")
        self.assertEqual(soll["contributors"][1]["lastName"], "Motivatier Classics")

    def test_original_without_translator_has_editor_only(self) -> None:
        export = _export()
        export["book"]["translator"] = ""
        soll = map_kdp_soll(export, book_root=Path("."), style="stil")
        self.assertEqual([item["role"] for item in soll["contributors"]], ["Editor"])

    def test_repo_pharao_export_maps_without_book_yaml_author(self) -> None:
        path = REPO_ROOT / "books" / "pharao" / "export.yaml"
        if not path.is_file():
            self.skipTest("pharao export.yaml fehlt")
        export = load_export_document(path)
        soll = map_kdp_soll(
            export,
            book_root=path.parent,
            style="stil-02-poetisch",
        )
        self.assertEqual(soll["title"], "Der Pharao")
        self.assertEqual(soll["primaryAuthor"]["lastName"], "Prus")
        self.assertEqual(soll["language"], "German")
        self.assertTrue(soll["description"].startswith("Bolesław Prus"))
        self.assertNotIn("Der Pharao führt in ein Ägypten", soll["description"])
        self.assertEqual(soll["asin"], "")


class MatchTests(unittest.TestCase):
    def _soll(self, **fmt_over) -> dict:
        soll = map_kdp_soll(_export(), book_root=Path("."), style="stil")
        soll["formats"]["kindle"].update(fmt_over)
        return soll

    def test_title_id_wins(self) -> None:
        soll = self._soll(title_id="A1B2C3D4E5F6", asin="B0HK567117")
        matched = match_kdp_title(
            soll,
            fmt="kindle",
            bookshelf={"refs": [{"titleId": "A1B2C3D4E5F6", "format": "kindle"}]},
            catalog={"books": []},
            cache={"books": []},
        )
        self.assertEqual(matched["via"], "title_id")
        self.assertEqual(matched["title_id"], "A1B2C3D4E5F6")

    def test_asin_joins_only_when_catalog_key_is_bookshelf_id(self) -> None:
        soll = self._soll(asin="B0HK567117")
        matched = match_kdp_title(
            soll,
            fmt="kindle",
            bookshelf={"refs": [{"titleId": "TITLEID1234", "format": "kindle"}]},
            catalog={
                "books": [
                    {
                        "key": "TITLEID1234",
                        "title": "Der Pharao",
                        "author": "Bolesław Prus",
                        "digitalAsin": "B0HK567117",
                        "printAsin": None,
                    }
                ]
            },
            cache={"books": []},
        )
        self.assertEqual(matched["title_id"], "TITLEID1234")
        self.assertEqual(matched["via"], "asin")

    def test_exact_title_stops_when_bookshelf_has_no_names(self) -> None:
        soll = self._soll()
        with self.assertRaises(KdpMatchStop) as caught:
            match_kdp_title(
                soll,
                fmt="kindle",
                bookshelf={
                    "refs": [
                        {"titleId": "ONLYONE1234", "format": "kindle"},
                    ]
                },
                catalog={
                    "books": [
                        {
                            "key": "reports-key",
                            "title": "Der Pharao",
                            "author": "Bolesław Prus",
                            "digitalAsin": "B0HK567117",
                        }
                    ]
                },
                cache={"books": []},
            )
        self.assertIn("nichts zugeordnet", str(caught.exception).lower() + "kein eindeutiger")
        self.assertTrue(caught.exception.candidates)

    def test_two_catalog_keys_stop(self) -> None:
        soll = self._soll()
        with self.assertRaises(KdpMatchStop):
            match_kdp_title(
                soll,
                fmt="kindle",
                bookshelf={
                    "refs": [
                        {"titleId": "TITLEID1234", "format": "kindle"},
                        {"titleId": "TITLEID5678", "format": "kindle"},
                    ]
                },
                catalog={
                    "books": [
                        {"key": "TITLEID1234", "title": "Der Pharao", "author": "Prus"},
                        {"key": "TITLEID5678", "title": "Der Pharao", "author": "Bolesław Prus"},
                    ]
                },
                cache={"books": []},
            )

    def test_saved_title_id_missing_on_bookshelf_stops(self) -> None:
        soll = self._soll(title_id="MISSING12345")
        with self.assertRaises(KdpMatchStop):
            match_kdp_title(
                soll,
                fmt="kindle",
                bookshelf={"refs": [{"titleId": "OTHERID12345", "format": "kindle"}]},
                catalog={"books": []},
                cache={"books": []},
            )


class BindTests(unittest.TestCase):
    def test_bind_keeps_the_rest_of_export_yaml(self) -> None:
        original = "book:\n  title: Der Pharao\n  author: Bolesław Prus\nwebsite:\n  amazon_url: ''\n"
        updated = upsert_amazon_join(
            original,
            fmt="kindle",
            title_id="TITLEID1234",
            asin="B0HK567117",
        )
        self.assertIn("title: Der Pharao", updated)
        self.assertIn("author: Bolesław Prus", updated)
        self.assertIn("amazon_url: ''", updated)
        self.assertIn("title_id: 'TITLEID1234'", updated)
        self.assertIn("asin: 'B0HK567117'", updated)
        self.assertIn("enabled: false", updated)

    def test_bind_replaces_existing_title_id_only(self) -> None:
        original = (
            "book:\n  title: Der Pharao\namazon:\n  marketplace: DE\n"
            "  kindle:\n    enabled: true\n    title_id: ''\n    asin: ''\n"
            "  paperback:\n    enabled: false\n"
        )
        updated = upsert_amazon_join(original, fmt="kindle", title_id="TITLEID1234", asin="")
        self.assertIn("marketplace: DE", updated)
        self.assertIn("title_id: 'TITLEID1234'", updated)
        self.assertIn("enabled: false", updated)
        self.assertEqual(updated.count("amazon:"), 1)


if __name__ == "__main__":
    unittest.main()
