"""Tests fuer tools/lib/rf_characters.py (RomanForge-Figuren-Spiegel und names.yaml-Abgleich).

Stil: unittest wie tests/test_book_project.py. Laeuft ohne pytest:
    .\\.venv\\Scripts\\python.exe -m unittest tests.test_rf_characters -v
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib import rf_characters as rfc  # noqa: E402


def ch(uid: str, name: str, appearance: str | None = "Rotes Haar", role: str | None = "Hauptfigur") -> dict:
    return {"uid": uid, "name": name, "role": role, "description": None,
            "appearance": appearance, "first_appears_chapter": 1, "updated_at": None}


def kinds(actions: list[rfc.Action]) -> dict[str, str]:
    return {a.name: a.kind for a in actions}


class NormalizeTests(unittest.TestCase):
    def test_sortiert_nach_uid_und_verwirft_unbrauchbare_eintraege(self):
        raw = [{"uid": "b", "name": "Ben"}, {"uid": "a", "name": " Anna "}, {"uid": "", "name": "X"},
               {"name": "Ohne uid"}, "kaputt", {"uid": "c", "name": ""}]
        result = rfc.normalize_characters(raw)
        self.assertEqual([c["name"] for c in result], ["Anna", "Ben"])
        self.assertEqual(rfc.normalize_characters(None), [])


class PlanTests(unittest.TestCase):
    def test_neue_figur_wird_draft_mit_vorbefuelltem_visual(self):
        actions = rfc.plan_sync([], [ch("u1", "Mara")], same_language=True)
        self.assertEqual(actions[0].kind, rfc.NEW)
        entry = rfc.apply_sync([], actions)[0]
        self.assertEqual(entry["source"], "Mara")
        self.assertEqual(entry["target"], "Mara")
        self.assertEqual(entry["status"], "draft")
        self.assertEqual(entry["rf_uid"], "u1")
        self.assertEqual(entry["visual"], "Rotes Haar")

    def test_target_bleibt_leer_bei_uebersetzung(self):
        entry = rfc.apply_sync([], rfc.plan_sync([], [ch("u1", "Mara")], same_language=False))[0]
        self.assertEqual(entry["target"], "")

    def test_namensabgleich_ordnet_eindeutig_per_alias_zu_und_laesst_peter_felder(self):
        entries = [{"source": "Frederik Holm", "target": "Frederik Holm", "aliases": ["Holm"],
                    "visual": "Dreispitz", "note": "wichtig", "status": "approved"}]
        actions = rfc.plan_sync(entries, [ch("u9", "Holm")], same_language=True)
        self.assertEqual(actions[0].kind, rfc.LINK)
        result = rfc.apply_sync(entries, actions)[0]
        self.assertEqual(result["rf_uid"], "u9")
        for key in ("source", "target", "aliases", "visual", "note", "status"):
            self.assertEqual(result[key], entries[0][key], key)

    def test_mehrdeutiger_namensabgleich_ist_konflikt(self):
        entries = [{"source": "Holm", "target": "Holm"}, {"source": "Kapitaen", "target": "K", "aliases": ["Holm"]}]
        actions = rfc.plan_sync(entries, [ch("u9", "Holm")], same_language=True)
        self.assertEqual(actions[0].kind, rfc.CONFLICT)
        self.assertEqual(rfc.apply_sync(entries, actions), entries)

    def test_doppelter_name_in_romanforge_ist_konflikt(self):
        actions = rfc.plan_sync([], [ch("u1", "Mara"), ch("u2", "mara")], same_language=True)
        self.assertEqual({a.kind for a in actions}, {rfc.CONFLICT})

    def test_umbenennung_bei_gleicher_uid_aendert_nur_source(self):
        entries = [{"source": "Mara", "target": "Mara-Ziel", "aliases": ["M"], "rf_uid": "u1",
                    "rf_appearance_sha": rfc.appearance_sha("Rotes Haar")}]
        actions = rfc.plan_sync(entries, [ch("u1", "Marit")], same_language=True)
        self.assertEqual(actions[0].kind, rfc.RENAMED)
        result = rfc.apply_sync(entries, actions)[0]
        self.assertEqual(result["source"], "Marit")
        self.assertEqual(result["target"], "Mara-Ziel")
        self.assertEqual(result["aliases"], ["M"])

    def test_geaendertes_aussehen_meldet_bildprompt_pruefung_ohne_visual_zu_aendern(self):
        entries = [{"source": "Mara", "target": "Mara", "visual": "alt", "rf_uid": "u1",
                    "rf_appearance_sha": rfc.appearance_sha("Rotes Haar")}]
        actions = rfc.plan_sync(entries, [ch("u1", "Mara", appearance="Schwarzes Haar")], same_language=True)
        self.assertEqual(actions[0].kind, rfc.APPEARANCE)
        result = rfc.apply_sync(entries, actions)[0]
        self.assertEqual(result["visual"], "alt")
        self.assertTrue(result["rf_visual_check"])
        self.assertEqual(result["rf_appearance_sha"], rfc.appearance_sha("Schwarzes Haar"))

    def test_unberuehrtes_visual_folgt_geaendertem_aussehen(self):
        entries = [{"source": "Mara", "target": "Mara", "visual": "Rotes Haar", "rf_uid": "u1",
                    "rf_appearance_sha": rfc.appearance_sha("Rotes Haar"), "rf_visual_check": True}]
        actions = rfc.plan_sync(entries, [ch("u1", "Mara", appearance="Schwarzes Haar")], same_language=True)
        self.assertEqual(actions[0].kind, rfc.FOLLOWED)
        result = rfc.apply_sync(entries, actions)[0]
        self.assertEqual(result["visual"], "Schwarzes Haar")
        self.assertEqual(result["rf_appearance_sha"], rfc.appearance_sha("Schwarzes Haar"))
        self.assertNotIn("rf_visual_check", result)
        again = rfc.plan_sync([result], [ch("u1", "Mara", appearance="Schwarzes Haar")], same_language=True)
        self.assertEqual(again[0].kind, rfc.UNCHANGED)

    def test_leeres_visual_wird_beim_ersten_aussehen_gefuellt(self):
        entries = [{"source": "Berengar", "target": "Berengar", "rf_uid": "u1",
                    "rf_appearance_sha": rfc.appearance_sha(None)}]
        actions = rfc.plan_sync(entries, [ch("u1", "Berengar", appearance="Grauer Bart, breite Schultern")], same_language=True)
        self.assertEqual(actions[0].kind, rfc.FOLLOWED)
        self.assertEqual(rfc.apply_sync(entries, actions)[0]["visual"], "Grauer Bart, breite Schultern")

    def test_von_hand_angepasstes_visual_bleibt_und_wird_nur_markiert(self):
        entries = [{"source": "Mara", "target": "Mara", "visual": "Handtext", "rf_uid": "u1",
                    "rf_appearance_sha": rfc.appearance_sha("Rotes Haar")}]
        actions = rfc.plan_sync(entries, [ch("u1", "Mara", appearance="Schwarzes Haar")], same_language=True)
        self.assertEqual(actions[0].kind, rfc.APPEARANCE)
        result = rfc.apply_sync(entries, actions)[0]
        self.assertEqual(result["visual"], "Handtext")
        self.assertTrue(result["rf_visual_check"])

    def test_aussehen_in_romanforge_geleert_aendert_visual_nicht(self):
        entries = [{"source": "Mara", "target": "Mara", "visual": "Rotes Haar", "rf_uid": "u1",
                    "rf_appearance_sha": rfc.appearance_sha("Rotes Haar")}]
        actions = rfc.plan_sync(entries, [ch("u1", "Mara", appearance=None)], same_language=True)
        self.assertEqual(actions[0].kind, rfc.APPEARANCE)
        self.assertEqual(rfc.apply_sync(entries, actions)[0]["visual"], "Rotes Haar")

    def test_umbenennung_und_nachziehen_zusammen(self):
        entries = [{"source": "Mara", "target": "Mara", "visual": "Rotes Haar", "rf_uid": "u1",
                    "rf_appearance_sha": rfc.appearance_sha("Rotes Haar")}]
        actions = rfc.plan_sync(entries, [ch("u1", "Marit", appearance="Blondes Haar")], same_language=True)
        self.assertEqual(actions[0].kind, rfc.RENAMED)
        result = rfc.apply_sync(entries, actions)[0]
        self.assertEqual((result["source"], result["visual"]), ("Marit", "Blondes Haar"))

    def test_namensabgleich_fuellt_nur_ein_leeres_visual(self):
        entries = [{"source": "Holm", "target": "Holm"}]
        result = rfc.apply_sync(entries, rfc.plan_sync(entries, [ch("u9", "Holm")], same_language=True))[0]
        self.assertEqual(result["visual"], "Rotes Haar")

    def test_unveraendert_wird_nicht_geschrieben(self):
        entries = [{"source": "Mara", "target": "Mara", "rf_uid": "u1",
                    "rf_appearance_sha": rfc.appearance_sha("Rotes Haar")}]
        actions = rfc.plan_sync(entries, [ch("u1", "Mara")], same_language=True)
        self.assertEqual(kinds(actions), {"Mara": rfc.UNCHANGED})
        self.assertEqual(rfc.apply_sync(entries, actions), entries)

    def test_in_romanforge_geloeschte_figur_wird_markiert_nie_entfernt(self):
        entries = [{"source": "Alt", "target": "Alt", "rf_uid": "gone", "visual": "Bild"},
                   {"source": "Ort", "target": "Ort"}]
        actions = rfc.plan_sync(entries, [], same_language=True)
        self.assertEqual([a.kind for a in actions], [rfc.REMOVED])
        result = rfc.apply_sync(entries, actions)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["status"], "removed_in_rf")
        self.assertEqual(result[0]["visual"], "Bild")
        self.assertNotIn("status", result[1])

    def test_eintraege_ohne_rf_uid_bleiben_unberuehrt(self):
        entries = [{"source": "Ostsee", "target": "Baltic", "type": "place"}]
        actions = rfc.plan_sync(entries, [ch("u1", "Mara")], same_language=True)
        result = rfc.apply_sync(entries, actions)
        self.assertEqual(result[0], entries[0])
        self.assertEqual(len(result), 2)

    def test_apply_aendert_die_uebergebene_liste_nicht(self):
        entries = [{"source": "Holm", "target": "Holm"}]
        rfc.apply_sync(entries, rfc.plan_sync(entries, [ch("u9", "Holm")], same_language=True))
        self.assertNotIn("rf_uid", entries[0])

    def test_zweiter_lauf_nach_apply_ist_unveraendert(self):
        first = rfc.apply_sync([], rfc.plan_sync([], [ch("u1", "Mara")], same_language=True))
        again = rfc.plan_sync(first, [ch("u1", "Mara")], same_language=True)
        self.assertEqual(kinds(again), {"Mara": rfc.UNCHANGED})


class AppearanceReportTests(unittest.TestCase):
    def test_tabelle_zeigt_den_stand_je_figur(self):
        sha = rfc.appearance_sha
        entries = [
            {"source": "A", "rf_uid": "u1", "visual": "gleich", "rf_appearance_sha": sha("gleich")},
            {"source": "B", "rf_uid": "u2", "visual": "Handtext", "rf_appearance_sha": sha("alt")},
            {"source": "C", "rf_uid": "u3", "visual": "alt", "rf_appearance_sha": sha("alt")},
            {"source": "D", "rf_uid": "u4"},
            {"source": "E", "rf_uid": "u5", "visual": "nur hier", "rf_appearance_sha": sha(None)},
            {"source": "F", "rf_uid": "u6", "rf_appearance_sha": sha(None)},
        ]
        characters = [ch("u1", "A", "gleich"), ch("u2", "B", "neu"), ch("u3", "C", "neu"), ch("u4", "D", "da"),
                      ch("u5", "E", None), ch("u6", "F", None), ch("u7", "G", "x")]
        rows = {r["name"]: r["status"] for r in rfc.appearance_report(entries, characters)}
        self.assertEqual(rows, {
            "A": "gleich", "B": "weicht ab (von Hand)", "C": "folgt RomanForge", "D": "visual leer",
            "E": "nur in peter", "F": "fehlt in beiden", "G": "nicht verknuepft",
        })
        self.assertIn("weicht ab (von Hand)", rfc.render_appearance_report(rfc.appearance_report(entries, characters)))


class MirrorTests(unittest.TestCase):
    def test_spiegel_schreiben_und_lesen(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = rfc.write_mirror(tmp, "h-1", [ch("u1", "Mara")])
            self.assertTrue(str(path).endswith("romanforge\\characters.json") or str(path).endswith("romanforge/characters.json"))
            data = rfc.read_mirror(tmp)
            self.assertEqual(data["format"], rfc.MIRROR_FORMAT)
            self.assertEqual(data["handoff_id"], "h-1")
            self.assertEqual(data["characters"][0]["name"], "Mara")

    def test_fehlender_spiegel_gibt_klaren_fehler(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                rfc.read_mirror(tmp)


class NewBookFromHandoffTests(unittest.TestCase):
    """--new --handoff legt den Figuren-Spiegel und draft-Eintraege in names.yaml an."""

    def test_neues_buch_bekommt_spiegel_und_names_aus_der_uebergabe(self):
        from unittest import mock

        import yaml
        import import_markdown_original as mod

        handoff = {
            "chapters": [{"id": 5, "number": 1, "title": "Eins", "content": "Mara geht los."}],
            "characters": [ch("u1", "Mara"), ch("u2", "Ben", appearance=None, role=None)],
        }
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch("lib.romanforge_client.RomanForgeConfig.from_env", return_value=object()), \
                mock.patch("lib.romanforge_client.get_handoff_data", return_value=handoff), \
                mock.patch("lib.romanforge_client.download_export", return_value="# Eins\n\nMara geht los.\n"):
            book_root = Path(tmp) / "testbuch"
            code = mod.main(["--new", "--handoff", "h1", "--title", "Testbuch", "--author", "A. Autor",
                             "--id", "testbuch", "--book-root", str(book_root)])
            self.assertEqual(code, 0)
            mirror = rfc.read_mirror(book_root)
            self.assertEqual([c["uid"] for c in mirror["characters"]], ["u1", "u2"])
            names = yaml.safe_load((book_root / "names.yaml").read_text(encoding="utf-8"))["entries"]
            self.assertEqual({e["source"]: e["rf_uid"] for e in names}, {"Mara": "u1", "Ben": "u2"})
            self.assertTrue(all(e["status"] == "draft" and e["target"] == e["source"] for e in names))


if __name__ == "__main__":
    unittest.main()
