"""Tests fuer die Metadaten-Uebernahme RomanForge -> peter (tools/lib/rf_metadata.py, tools/rf_metadata.py)
und das Herausgeber-Feld in Titelei und KDP (tools/lib/credits.py, kdp_mapping).

Laeuft ohne pytest:
    .\\.venv\\Scripts\\python.exe -m unittest tests.test_rf_metadata -v
"""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import rf_metadata as cli  # noqa: E402
from lib import credits  # noqa: E402
from lib import kdp_mapping  # noqa: E402
from lib import rf_metadata as rfm  # noqa: E402

EXPORT = """# Kopf
defaults:
  cover:
    show: true
book:
  title: Titel
  subtitle: Alter Untertitel   # Kommentar
  author: Alter Autor
  translator: ''
  description: |
    Alter Klappentext.

    Zweiter Absatz.
  title_page_extra:
  - Zeile eins
  - Zeile zwei
  publisher: Alter Verlag
  language: de-DE
amazon:
  marketplace: DE
"""

BOOK = "id: buch\ntitle: Titel\nauthor: Alter Autor\n# Kommentar\nsource_lang: de\n"

# Dieselbe Datei ohne vorhandenen Klappentext (der Langtext-Fall "peter ist leer").
EXPORT_LEER = EXPORT.replace("  description: |\n    Alter Klappentext.\n\n    Zweiter Absatz.\n", "  description: ''\n")


def rf(**over) -> dict:
    values = {f.rf_key: "" for f in rfm.FIELDS}
    values.update(over)
    return values


class PlanTests(unittest.TestCase):
    def kinds(self, actions):
        return {a.rf_key: a.kind for a in actions}

    def test_leerer_romanforge_wert_aendert_nichts(self):
        actions = rfm.plan_metadata(rf(), {"subtitle": "peter"}, {})
        self.assertTrue(all(a.kind == rfm.UNCHANGED for a in actions))
        self.assertEqual(rfm.render_report(actions), "Metadaten unveraendert.")

    def test_identitaetsfelder_ueberschreiben_immer(self):
        actions = rfm.plan_metadata(rf(author_name="Neu", subtitle="Neu2"), {"author_name": "Alt", "subtitle": ""}, {})
        kinds = self.kinds(actions)
        self.assertEqual((kinds["author_name"], kinds["subtitle"]), (rfm.SET, rfm.SET))

    def test_gleicher_wert_wird_nur_einmal_angeglichen(self):
        first = self.kinds(rfm.plan_metadata(rf(publisher="V"), {"publisher": "V"}, {}))
        self.assertEqual(first["publisher"], rfm.ADOPT)
        second = self.kinds(rfm.plan_metadata(rf(publisher="V"), {"publisher": "V"}, {"publisher": rfm.sha("V")}))
        self.assertEqual(second["publisher"], rfm.UNCHANGED)

    def test_titel_wird_nur_gemeldet(self):
        kinds = self.kinds(rfm.plan_metadata(rf(title="Ashkar I"), {"title": "Ashkar I (Das Glasmeer)"}, {}))
        self.assertEqual(kinds["title"], rfm.REPORTED)

    def test_klappentext_folgt_nur_wenn_leer_oder_unberuehrt(self):
        leer = self.kinds(rfm.plan_metadata(rf(blurb="Neu"), {"blurb": ""}, {}))
        self.assertEqual(leer["blurb"], rfm.FOLLOWED)
        unberuehrt = self.kinds(rfm.plan_metadata(rf(blurb="Neu"), {"blurb": "Alt"}, {"blurb": rfm.sha("Alt")}))
        self.assertEqual(unberuehrt["blurb"], rfm.FOLLOWED)
        von_hand = self.kinds(rfm.plan_metadata(rf(blurb="Neu"), {"blurb": "Selbst"}, {"blurb": rfm.sha("Alt")}))
        self.assertEqual(von_hand["blurb"], rfm.DIVERGED)
        ohne_stand = self.kinds(rfm.plan_metadata(rf(blurb="Neu"), {"blurb": "Selbst"}, {}))
        self.assertEqual(ohne_stand["blurb"], rfm.DIVERGED)

    def test_zeilenumbrueche_zaehlen_nicht(self):
        kinds = self.kinds(rfm.plan_metadata(rf(blurb=rfm.norm("A\r\nB")), {"blurb": "A\nB"}, {"blurb": rfm.sha("A\nB")}))
        self.assertEqual(kinds["blurb"], rfm.UNCHANGED)


class SetKeyTests(unittest.TestCase):
    def test_ersetzt_skalar_und_behaelt_den_rest(self):
        out = rfm.set_key(EXPORT, "book", "author", "Neuer Autor")
        data = yaml.safe_load(out)
        self.assertEqual(data["book"]["author"], "Neuer Autor")
        self.assertIn("# Kopf", out)
        self.assertEqual(data["book"]["title_page_extra"], ["Zeile eins", "Zeile zwei"])
        self.assertEqual(data["amazon"]["marketplace"], "DE")

    def test_ersetzt_blocktext_inklusive_leerzeile(self):
        out = rfm.set_key(EXPORT, "book", "description", "Neu eins.\n\nNeu zwei.")
        data = yaml.safe_load(out)
        self.assertEqual(data["book"]["description"].strip(), "Neu eins.\n\nNeu zwei.")
        self.assertEqual(data["book"]["publisher"], "Alter Verlag")

    def test_ersetzt_nicht_die_liste_der_nachbarn(self):
        out = rfm.set_key(EXPORT, "book", "title_page_extra", "x")
        self.assertNotIn("Zeile eins", out)
        self.assertEqual(yaml.safe_load(out)["book"]["publisher"], "Alter Verlag")

    def test_fehlender_schluessel_wird_am_blockende_ergaenzt(self):
        out = rfm.set_key(EXPORT, "book", "editor", "Motivatier Classics")
        data = yaml.safe_load(out)
        self.assertEqual(data["book"]["editor"], "Motivatier Classics")
        self.assertEqual(data["amazon"]["marketplace"], "DE")
        self.assertNotIn("editor", data["amazon"])

    def test_oberste_ebene_und_sonderzeichen(self):
        out = rfm.set_key(BOOK, None, "author", "Timo: \"Verita\" # x")
        self.assertEqual(yaml.safe_load(out)["author"], 'Timo: "Verita" # x')
        self.assertIn("# Kommentar", out)

    def test_zahl_bleibt_zahl(self):
        out = rfm.set_key(EXPORT, "book", "series_volume", "2", number=True)
        self.assertEqual(yaml.safe_load(out)["book"]["series_volume"], 2)

    def test_crlf_bleibt_erhalten(self):
        text = EXPORT.replace("\n", "\r\n")
        out = rfm.set_key(text, "book", "author", "X")
        self.assertNotIn("\r\r", out)
        self.assertEqual(out.count("\r\n"), out.count("\n"))
        self.assertEqual(yaml.safe_load(out)["book"]["author"], "X")

    def test_fehlender_block_ist_ein_fehler(self):
        with self.assertRaises(ValueError):
            rfm.set_key(BOOK, "book", "author", "X")


class ApplyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "export.yaml").write_text(EXPORT_LEER, encoding="utf-8")
        (self.root / "book.yaml").write_text(BOOK, encoding="utf-8")
        self.addCleanup(self.tmp.cleanup)

    def test_vorhandener_klappentext_ohne_uebernahmestand_wird_nicht_ueberschrieben(self):
        (self.root / "export.yaml").write_text(EXPORT, encoding="utf-8")
        actions = rfm.plan_metadata(rf(blurb="RF-Text"), rfm.current_values(self.root), {})
        rfm.apply_actions(self.root, actions, "h1")
        self.assertIn("Alter Klappentext.", self.export()["description"])
        self.assertNotIn("blurb", rfm.read_mirror(self.root)["adopted"])

    def export(self):
        return yaml.safe_load((self.root / "export.yaml").read_text(encoding="utf-8"))["book"]

    def test_apply_schreibt_beide_dateien_und_den_spiegel(self):
        values = rf(author_name="Timo Verita", editor_name="Motivatier Classics", editor_note="Herausgabe",
                    series_number="3", blurb="Neuer Klappentext.", title="Anderer Titel")
        actions = rfm.plan_metadata(values, rfm.current_values(self.root), {})
        notes = rfm.apply_actions(self.root, actions, "h1")
        export = self.export()
        self.assertEqual(export["author"], "Timo Verita")
        self.assertEqual((export["editor"], export["editor_note"], export["series_volume"]),
                         ("Motivatier Classics", "Herausgabe", 3))
        self.assertEqual(export["description"].strip(), "Neuer Klappentext.")
        self.assertEqual(export["title"], "Titel")  # Titel wird nie geschrieben
        self.assertEqual(yaml.safe_load((self.root / "book.yaml").read_text(encoding="utf-8"))["author"], "Timo Verita")
        self.assertEqual(notes, [])
        mirror = rfm.read_mirror(self.root)
        self.assertEqual(mirror["handoff_id"], "h1")
        self.assertEqual(mirror["adopted"]["blurb"], rfm.sha("Neuer Klappentext."))
        self.assertNotIn("title", mirror["adopted"])

    def test_zweiter_lauf_ist_unveraendert(self):
        values = rf(author_name="Timo Verita", blurb="Text.")
        rfm.apply_actions(self.root, rfm.plan_metadata(values, rfm.current_values(self.root), {}), "h1")
        again = rfm.plan_metadata(values, rfm.current_values(self.root), rfm.read_mirror(self.root)["adopted"])
        self.assertEqual(rfm.render_report(again), "Metadaten unveraendert.")

    def test_von_hand_geaenderter_klappentext_bleibt_ausser_mit_force(self):
        first = rfm.plan_metadata(rf(blurb="RF eins"), rfm.current_values(self.root), {})
        rfm.apply_actions(self.root, first, "h1")
        text = (self.root / "export.yaml").read_text(encoding="utf-8").replace("RF eins", "Von Hand")
        (self.root / "export.yaml").write_text(text, encoding="utf-8")
        second = rfm.plan_metadata(rf(blurb="RF zwei"), rfm.current_values(self.root), rfm.read_mirror(self.root)["adopted"])
        self.assertEqual([a.kind for a in second if a.rf_key == "blurb"], [rfm.DIVERGED])
        rfm.apply_actions(self.root, second, "h2")
        self.assertEqual(self.export()["description"].strip(), "Von Hand")
        rfm.apply_actions(self.root, second, "h2", force={"blurb"})
        self.assertEqual(self.export()["description"].strip(), "RF zwei")

    def test_hinweis_bei_herausgeber_und_uebersetzer(self):
        (self.root / "export.yaml").write_text(EXPORT.replace("translator: ''", "translator: Jemand"), encoding="utf-8")
        actions = rfm.plan_metadata(rf(editor_name="Ed"), rfm.current_values(self.root), {})
        notes = rfm.apply_actions(self.root, actions, "h1")
        self.assertTrue(any("translator" in n for n in notes))


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "buch"
        self.root.mkdir()
        (self.root / "export.yaml").write_text(EXPORT_LEER, encoding="utf-8")
        (self.root / "book.yaml").write_text(
            BOOK + "romanforge:\n  instance: rf.example.de\n  project_id: 8\n", encoding="utf-8")
        self.addCleanup(self.tmp.cleanup)
        project = SimpleNamespace(id="buch", root=self.root, config=yaml.safe_load((self.root / "book.yaml").read_text(encoding="utf-8")))
        self.patches = [
            mock.patch.object(cli, "discover_projects", return_value=[project]),
            mock.patch("lib.romanforge_client.RomanForgeConfig.from_env",
                       return_value=SimpleNamespace(base_url="https://rf.example.de")),
        ]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)

    def run_cli(self, args, publication=None):
        data = {"format": "romanforge-handoff/1", "mode": "update", "instance": "http://rf.example.de",
                "project": {"id": 8, "title": "Titel"}, "expose": "Handlung.",
                "publication": publication or {}, "chapters": []}
        out, err = io.StringIO(), io.StringIO()
        with mock.patch("lib.romanforge_client.get_handoff_data", return_value=data), \
                redirect_stdout(out), redirect_stderr(err):
            code = cli.main(args)
        return code, out.getvalue(), err.getvalue()

    def test_trockenlauf_dann_apply_findet_das_buch_ueber_die_bindung(self):
        pub = {"author_name": "Timo Verita", "editor_name": "Motivatier Classics", "blurb": "Klappe."}
        code, out, _ = self.run_cli(["--handoff", "11111111-aaaa"], pub)
        self.assertEqual(code, 0)
        self.assertIn("Trockenlauf", out)
        self.assertIn("Klappentext", out)
        self.assertNotIn("Motivatier", (self.root / "export.yaml").read_text(encoding="utf-8"))
        code, out, _ = self.run_cli(["--handoff", "11111111-aaaa", "--apply"], pub)
        self.assertEqual(code, 0)
        export = yaml.safe_load((self.root / "export.yaml").read_text(encoding="utf-8"))["book"]
        self.assertEqual(export["editor"], "Motivatier Classics")
        self.assertTrue((self.root / "romanforge" / "expose.md").exists())
        code, out, _ = self.run_cli(["--handoff", "11111111-aaaa"], pub)
        self.assertIn("Metadaten unveraendert.", out)

    def test_falsche_projekt_id_bricht_ab(self):
        data_pub = {}
        out, err = io.StringIO(), io.StringIO()
        data = {"format": "romanforge-handoff/1", "mode": "update", "instance": "http://rf.example.de",
                "project": {"id": 99, "title": "X"}, "publication": data_pub, "chapters": []}
        with mock.patch("lib.romanforge_client.get_handoff_data", return_value=data), \
                redirect_stdout(out), redirect_stderr(err):
            code = cli.main(["--book", "buch", "--handoff", "h"])
        self.assertEqual(code, 2)
        self.assertIn("gebunden", err.getvalue())

    def test_unbekanntes_force_feld(self):
        code, _, err = self.run_cli(["--handoff", "h", "--force-meta", "nix"])
        self.assertEqual(code, 2)
        self.assertIn("nix", err)

    def test_tabelle_fuer_romanforge(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = cli.main(["--book", "buch", "--fuer-romanforge"])
        self.assertEqual(code, 0)
        self.assertIn("Alter Autor", out.getvalue())


class CreditsTests(unittest.TestCase):
    def test_herausgeber_wird_zur_titelzeile(self):
        meta = credits.apply_editor_credit({"editor": "Motivatier Classics", "editor_note": "Herausgabe und Einrichtung"})
        self.assertEqual((meta["translator"], meta["translator_label"]),
                         ("Motivatier Classics", "Herausgabe und Einrichtung"))
        plain = credits.apply_editor_credit({"editor": "Ed"})
        self.assertEqual(plain["translator_label"], "Herausgabe")

    def test_uebersetzer_geht_vor(self):
        meta = credits.apply_editor_credit({"editor": "Ed", "translator": "Uebersetzerin", "translator_label": "Uebersetzung"})
        self.assertEqual((meta["translator"], meta["translator_label"]), ("Uebersetzerin", "Uebersetzung"))

    def test_ohne_herausgeber_bleibt_alles_wie_es_war(self):
        meta = {"translator": "X", "translator_label": "Y", "publisher": "V"}
        self.assertEqual(credits.apply_editor_credit(dict(meta)), meta)
        self.assertEqual(credits.publisher_label(meta), "Herausgeber")
        self.assertEqual(credits.publisher_label({"editor": "Ed"}), "Verlag")

    def test_kdp_mitwirkende(self):
        self.assertEqual(
            kdp_mapping.build_contributors({"editor": "Anna Beispiel"}),
            [{"role": "Editor", "firstName": "Anna", "lastName": "Beispiel"}],
        )
        self.assertEqual(
            kdp_mapping.build_contributors({"editor": "Motivatier Classics"}),
            [{"role": "Editor", "firstName": "", "lastName": "Motivatier Classics"}],
        )
        old = kdp_mapping.build_contributors({"translator": "Jo Rest", "translator_label": "Uebersetzung"})
        self.assertEqual([c["role"] for c in old], ["Translator", "Editor"])


if __name__ == "__main__":
    unittest.main()
