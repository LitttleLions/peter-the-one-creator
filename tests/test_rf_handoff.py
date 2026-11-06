"""Tests fuer die Uebergabe-Schnittstelle RomanForge -> peter (Format, Kapitel-ID, Verlagsangaben, Exposé).

Stil: unittest wie tests/test_rf_characters.py. Laeuft ohne pytest:
    .\\.venv\\Scripts\\python.exe -m unittest tests.test_rf_handoff -v
"""

from __future__ import annotations

import argparse
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import import_markdown_original as mod  # noqa: E402
from lib import rf_characters as rfc  # noqa: E402
from lib import romanforge_client as client  # noqa: E402


def snapshot(**extra) -> dict:
    data = {"format": "romanforge-handoff/1", "mode": "new", "chapters": []}
    data.update(extra)
    return data


class FormatTests(unittest.TestCase):
    def test_bekanntes_format_wird_unveraendert_durchgereicht(self):
        data = snapshot(mode="update")
        self.assertIs(client.check_handoff_data(data), data)

    def test_unbekanntes_format_gibt_klaren_fehler(self):
        with self.assertRaisesRegex(client.RomanForgeError, "romanforge-handoff/2"):
            client.check_handoff_data(snapshot(format="romanforge-handoff/2"))

    def test_fehlendes_format_und_unbekannter_modus_werden_abgelehnt(self):
        with self.assertRaises(client.RomanForgeError):
            client.check_handoff_data({"mode": "new"})
        with self.assertRaises(client.RomanForgeError):
            client.check_handoff_data(snapshot(mode="merge"))
        with self.assertRaises(client.RomanForgeError):
            client.check_handoff_data(["kein", "objekt"])

    def test_export_text_und_ids_folgen_der_kapitelnummer(self):
        data = snapshot(chapters=[
            {"id": 9, "number": 2, "title": "Zwei", "content": "B"},
            {"id": 4, "number": 1, "title": "Eins", "content": "A"},
        ])
        self.assertEqual(client.chapter_rf_ids(data), ["4", "9"])
        text = client.export_text_from_data(data)
        self.assertLess(text.index("## Eins"), text.index("## Zwei"))


class MatchByIdTests(unittest.TestCase):
    export = [("Neuer Titel", "x"), ("Zwei", "y")]
    known = {"001": "Alter Titel", "002": "Zwei"}

    def test_id_haelt_ein_umbenanntes_kapitel_zusammen(self):
        rows = mod.match_chapters(self.export, self.known, ["11", "12"], {"001": "11", "002": "12"})
        self.assertEqual([r["chapter_id"] for r in rows], ["001", "002"])

    def test_ohne_ids_gilt_der_titel(self):
        rows = mod.match_chapters(self.export, self.known)
        self.assertEqual([r["chapter_id"] for r in rows], [None, "002"])
        self.assertEqual(rows[0]["action"], mod.ACTION_NEW)

    def test_falsche_laenge_der_id_liste_wird_ignoriert(self):
        rows = mod.match_chapters(self.export, self.known, ["11"], {"001": "11"})
        self.assertEqual([r["chapter_id"] for r in rows], [None, "002"])

    def test_id_ohne_treffer_faellt_auf_den_titel_zurueck(self):
        rows = mod.match_chapters(self.export, self.known, ["99", "98"], {"001": "11", "002": "12"})
        self.assertEqual([r["chapter_id"] for r in rows], [None, "002"])

    def test_uebernehmen_behaelt_die_bekannte_rf_id(self):
        state = {"chapters": {"001": {"title": "Alt", "rf_id": "11"}}}
        mod.update_state_chapter(state, "001", title="Neu", rf_base="a", peter_base="a", base_export="s")
        self.assertEqual(state["chapters"]["001"]["rf_id"], "11")
        mod.update_state_chapter(state, "001", title="Neu", rf_base="a", peter_base="a", base_export="s", rf_id="12")
        self.assertEqual(state["chapters"]["001"]["rf_id"], "12")


class PublicationTests(unittest.TestCase):
    def args(self, **kw) -> argparse.Namespace:
        base = {"author": None, "subtitle": None, "series": None, "publisher": None}
        base.update(kw)
        return argparse.Namespace(**base)

    def test_cli_gewinnt_und_fehlendes_wird_gefuellt(self):
        args = self.args(author="CLI Autor")
        publication = {"author_name": "RF Autor", "subtitle": " Untertitel ", "series_name": None, "publisher": "Verlag"}
        taken = mod.apply_publication_defaults(args, publication)
        self.assertEqual((args.author, args.subtitle, args.series, args.publisher),
                         ("CLI Autor", "Untertitel", None, "Verlag"))
        self.assertEqual(taken, ["subtitle=Untertitel", "publisher=Verlag"])

    def test_ohne_publication_bleibt_alles_leer(self):
        args = self.args()
        self.assertEqual(mod.apply_publication_defaults(args, None), [])
        self.assertIsNone(args.author)


class ExposeTests(unittest.TestCase):
    def test_expose_wird_als_vorlage_abgelegt(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = rfc.write_expose(tmp, "h-1", "  Handlung in drei Saetzen.  ")
            self.assertEqual(path.name, "expose.md")
            self.assertIn("Handlung in drei Saetzen.", path.read_text(encoding="utf-8"))
            self.assertIsNone(rfc.write_expose(tmp, "h-1", None))
            self.assertIsNone(rfc.write_expose(tmp, "h-1", "   "))


class NewFromHandoffTests(unittest.TestCase):
    def test_neues_buch_uebernimmt_verlagsangaben_und_expose(self):
        import yaml

        handoff = snapshot(
            chapters=[{"id": 5, "number": 1, "title": "Eins", "content": "Mara geht los."}],
            publication={"author_name": "A. Autor", "subtitle": "Ein Untertitel", "series_name": "Reihe",
                         "series_number": 2, "publisher": "Verlag X"},
            expose="Kurzer Plot.",
        )
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch("lib.romanforge_client.RomanForgeConfig.from_env", return_value=object()), \
                mock.patch("lib.romanforge_client.get_handoff_data", return_value=handoff):
            book_root = Path(tmp) / "testbuch"
            code = mod.main(["--new", "--handoff", "h1", "--title", "Testbuch",
                             "--id", "testbuch", "--book-root", str(book_root)])
            self.assertEqual(code, 0)
            export = yaml.safe_load((book_root / "export.yaml").read_text(encoding="utf-8"))["book"]
            self.assertEqual(export["author"], "A. Autor")
            self.assertEqual((export["subtitle"], export["publisher"], export["series"]),
                             ("Ein Untertitel", "Verlag X", "Reihe"))
            self.assertIn("Kurzer Plot.", (book_root / "romanforge" / "expose.md").read_text(encoding="utf-8"))
            state = yaml.safe_load((book_root / "work" / "imports" / "romanforge" / "state.yaml").read_text(encoding="utf-8"))
            self.assertEqual(state["chapters"]["001"]["rf_id"], "5")


if __name__ == "__main__":
    unittest.main()
