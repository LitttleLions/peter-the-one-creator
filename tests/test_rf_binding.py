"""Tests fuer die feste Bindung Buch <-> RomanForge-Projekt (tools/lib/rf_binding.py und --bind).

Laeuft ohne pytest:
    .\\.venv\\Scripts\\python.exe -m unittest tests.test_rf_binding -v
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

import import_markdown_original as mod  # noqa: E402
from lib import rf_binding as rfb  # noqa: E402

KEY = ("rf.example.de", 8)


def handoff(**extra) -> dict:
    data = {
        "format": "romanforge-handoff/1", "mode": "update", "instance": "http://rf.example.de",
        "project": {"id": 8, "title": "Testbuch"},
        "chapters": [{"id": 11, "number": 1, "title": "Eins", "content": "Mara geht los."}],
    }
    data.update(extra)
    return data


class HelperTests(unittest.TestCase):
    def test_host_ohne_schema_pfad_und_grossschreibung(self):
        for value in ("https://RF.Example.de/", "http://rf.example.de", "rf.example.de", "rf.example.de/app"):
            self.assertEqual(rfb.normalize_host(value), "rf.example.de")
        self.assertEqual(rfb.normalize_host("http://localhost:3000"), "localhost:3000")
        self.assertEqual(rfb.normalize_host(""), "")
        self.assertEqual(rfb.normalize_host(None), "")

    def test_bindung_lesen(self):
        cfg = {"romanforge": {"instance": "https://RF.example.de", "project_id": "8"}}
        self.assertEqual(rfb.read_binding(cfg), KEY)
        self.assertIsNone(rfb.read_binding({}))
        self.assertIsNone(rfb.read_binding({"romanforge": {"instance": "x"}}))
        self.assertIsNone(rfb.read_binding({"romanforge": "kaputt"}))

    def test_schluessel_der_uebergabe(self):
        self.assertEqual(rfb.handoff_key(handoff()), KEY)
        self.assertIsNone(rfb.handoff_key({"project": {"id": 1}}))

    def test_nachweis_ueber_kapitel_ids_dann_textstand(self):
        chapters = {"001": {"rf_id": "11"}, "002": {"rf_id": "12"}}
        self.assertTrue(rfb.prove_by_chapters(state_chapters=chapters, snapshot_ids=["11", "12"], snapshot_hashes=[])[0])
        self.assertFalse(rfb.prove_by_chapters(state_chapters=chapters, snapshot_ids=["90"], snapshot_hashes=[])[0])
        by_hash = {"001": {"rf_base": "aa"}, "002": {"rf_base": "bb"}}
        self.assertTrue(rfb.prove_by_chapters(state_chapters=by_hash, snapshot_ids=[], snapshot_hashes=["aa", "bb"])[0])
        self.assertFalse(rfb.prove_by_chapters(state_chapters=by_hash, snapshot_ids=[], snapshot_hashes=["zz"])[0])
        self.assertFalse(rfb.prove_by_chapters(state_chapters={}, snapshot_ids=["1"], snapshot_hashes=[])[0])

    def test_block_wird_angehaengt_und_kommentare_bleiben(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "book.yaml"
            path.write_text("id: x\n# wichtiger Kommentar\ntitle: Titel", encoding="utf-8")
            rfb.append_binding(path, "rf.example.de", 8)
            text = path.read_text(encoding="utf-8")
            self.assertIn("# wichtiger Kommentar", text)
            self.assertEqual(yaml.safe_load(text)["romanforge"], {"instance": "rf.example.de", "project_id": 8})
            with self.assertRaises(ValueError):
                rfb.append_binding(path, "rf.example.de", 9)


class CheckUpdateTests(unittest.TestCase):
    def run_check(self, *, cfg=None, data=None, env="https://rf.example.de", others=(), state_ids=("11",), snap=("11",)):
        books = [("buch", cfg or {})] + [(name, {"romanforge": {"instance": "rf.example.de", "project_id": 8}})
                                         for name in others]
        return rfb.check_update(
            book_id="buch", book_cfg=cfg or {}, handoff_data=data or handoff(), env_url=env,
            books=books, state_rf_ids=list(state_ids), snapshot_ids=list(snap))

    bound = {"romanforge": {"instance": "rf.example.de", "project_id": 8}}

    def test_gebundenes_buch_ist_in_ordnung(self):
        self.assertEqual(self.run_check(cfg=self.bound), [])

    def test_ungebundenes_buch_wird_abgelehnt(self):
        errors = self.run_check(cfg={})
        self.assertTrue(any("nicht an RomanForge gebunden" in e for e in errors))

    def test_falsche_instanz_wird_abgelehnt(self):
        errors = self.run_check(cfg=self.bound, env="https://localhost:3000")
        self.assertTrue(any("ROMANFORGE_URL" in e for e in errors))

    def test_andere_projekt_id_wird_abgelehnt(self):
        errors = self.run_check(cfg={"romanforge": {"instance": "rf.example.de", "project_id": 9}})
        self.assertTrue(any("gebunden" in e and "gehoert" in e for e in errors))

    def test_doppelablage_wird_abgelehnt(self):
        errors = self.run_check(cfg=self.bound, others=("kopie",))
        self.assertTrue(any("Doppelablage" in e for e in errors))

    def test_fremde_kapitel_ids_werden_abgelehnt(self):
        errors = self.run_check(cfg=self.bound, state_ids=("90", "91"), snap=("11",))
        self.assertTrue(any("Kapitel-ID" in e for e in errors))

    def test_geloeschtes_kapitel_allein_ist_kein_fehler(self):
        self.assertEqual(self.run_check(cfg=self.bound, state_ids=("11", "90"), snap=("11",)), [])


class BindCommandTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "buch"
        (self.root / "work" / "imports" / "romanforge").mkdir(parents=True)
        (self.root / "book.yaml").write_text("id: buch\ntitle: Buch\n", encoding="utf-8")
        state = {"book": "buch", "chapters": {"001": {"title": "Eins", "rf_id": "11", "rf_base": "x", "peter_base": "x"}}}
        (self.root / "work" / "imports" / "romanforge" / "state.yaml").write_text(
            yaml.safe_dump(state), encoding="utf-8")
        self.addCleanup(self.tmp.cleanup)

    def run_main(self, extra, data=None):
        config = SimpleNamespace(base_url="https://rf.example.de")
        out, err = io.StringIO(), io.StringIO()
        with mock.patch("lib.romanforge_client.RomanForgeConfig.from_env", return_value=config), \
                mock.patch("lib.romanforge_client.get_handoff_data", return_value=data or handoff()), \
                redirect_stdout(out), redirect_stderr(err):
            code = mod.main(["--book-root", str(self.root), "--handoff", "h1", *extra])
        return code, out.getvalue(), err.getvalue()

    def book(self):
        return yaml.safe_load((self.root / "book.yaml").read_text(encoding="utf-8"))

    def test_trockenlauf_schreibt_nichts(self):
        code, out, _ = self.run_main(["--bind"])
        self.assertEqual(code, 0)
        self.assertIn("Trockenlauf", out)
        self.assertNotIn("romanforge", self.book())

    def test_apply_schreibt_die_bindung_und_wiederholung_ist_harmlos(self):
        code, _, _ = self.run_main(["--bind", "--apply"])
        self.assertEqual(code, 0)
        self.assertEqual(self.book()["romanforge"], {"instance": "rf.example.de", "project_id": 8})
        code, out, _ = self.run_main(["--bind", "--apply"])
        self.assertEqual(code, 0)
        self.assertIn("bereits", out)

    def test_ohne_nachweis_nur_mit_bestaetigter_projekt_id(self):
        data = handoff(chapters=[{"id": 90, "number": 1, "title": "Fremd", "content": "Anderer Text."}])
        code, _, err = self.run_main(["--bind", "--apply"], data)
        self.assertEqual(code, 2)
        self.assertIn("--project-id 8", err)
        self.assertNotIn("romanforge", self.book())
        code, _, _ = self.run_main(["--bind", "--apply", "--project-id", "7"], data)
        self.assertEqual(code, 2)
        code, _, _ = self.run_main(["--bind", "--apply", "--project-id", "8"], data)
        self.assertEqual(code, 0)
        self.assertIn("romanforge", self.book())

    def test_aktualisieren_ohne_bindung_bricht_ab(self):
        code, _, err = self.run_main(["--compare"])
        self.assertEqual(code, 2)
        self.assertIn("nicht an RomanForge gebunden", err)

    def test_aktualisieren_mit_bindung_laeuft(self):
        self.run_main(["--bind", "--apply"])
        _, out, err = self.run_main(["--compare"])
        self.assertNotIn("gebunden", err)
        self.assertIn("Uebernahmebericht", out)

    def test_bind_ohne_handoff_wird_abgelehnt(self):
        err = io.StringIO()
        with redirect_stderr(err), redirect_stdout(io.StringIO()):
            code = mod.main(["--book-root", str(self.root), "--bind"])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
