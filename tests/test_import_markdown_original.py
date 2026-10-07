"""Tests fuer tools/import_markdown_original.py (Stufe 1 RomanForge-Uebernahme).

Jede Zeile der Abgleichtabelle aus docs/plan-uebernahme-romanforge.md
Abschnitt 3 ist hier ein Test. Dazu K1 (state.yaml pro Kapitel),
K2 (--keep / --accept auf Konflikt), K3 (Vergleichsaufbereitung wie
import_die_dritte_chronik.py), K4 (kein input()), K5 (Zustand/Bericht-Trennung).

Stil: unittest wie tests/test_book_project.py. Laeuft ohne pytest:
    py -3 -m unittest tests.test_import_markdown_original -v
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))


def _load_module():
    import import_markdown_original as mod  # noqa: E402

    return mod


CHRONIK_ID = "die-dritte-chronik"
CHRONIK_BOOK = REPO_ROOT / "books" / CHRONIK_ID
CHRONIK_STYLE = "stil-01-original"
BASELINE_REV = "150f0c1:books/die-dritte-chronik/source/Die dritte Chronik.md"
CHRONIK_SOURCE = CHRONIK_BOOK / "source" / "Die dritte Chronik.md"


def _baseline_to_file(dest: Path) -> Path:
    """Schreibt den Ursprungs-Export per git show binär nach dest (ohne Lesen)."""
    import subprocess as sp  # noqa: E402

    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as fh:
        proc = sp.run(["git", "show", BASELINE_REV], stdout=fh, cwd=str(REPO_ROOT))
    if proc.returncode != 0:
        raise RuntimeError("Baseline 150f0c1 nicht verfuegbar")
    return dest


def _temp_book_from_chronik(tmp: Path, scene_ids: list[str] | str) -> Path:
    """Tempokopie: echte book.yaml + echte Szenen per Dateisystem kopieren.

    scene_ids == "all" kopiert alle vorhandenen Chronik-Szenen.
    """
    import shutil  # noqa: E402

    book_root = tmp / "books" / CHRONIK_ID
    (book_root / "source").mkdir(parents=True, exist_ok=True)
    (book_root / "work" / "chapters").mkdir(parents=True, exist_ok=True)
    (book_root / "styles").mkdir(parents=True, exist_ok=True)
    (book_root / "status").mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(CHRONIK_BOOK / "book.yaml"), str(book_root / "book.yaml"))
    if scene_ids == "all":
        style_root = CHRONIK_BOOK / "work" / "scenes" / "de" / CHRONIK_STYLE
        ids = sorted(p.name for p in style_root.iterdir() if p.is_dir())
    else:
        ids = list(scene_ids)
    for cid in ids:
        src = CHRONIK_BOOK / "work" / "scenes" / "de" / CHRONIK_STYLE / cid / "scene-01.md"
        dst = book_root / "work" / "scenes" / "de" / CHRONIK_STYLE / cid / "scene-01.md"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dst))
    return book_root


def _state_path(book_root: Path) -> Path:
    return book_root / "work" / "imports" / "romanforge" / "state.yaml"


def _parse_actions(stdout: str) -> dict[str, str]:
    """Liest {Kapitel-ID: Einstufung} aus der Berichtstabelle (nur ASCII-Felder)."""
    out: dict[str, str] = {}
    for line in stdout.splitlines():
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 6 or cells[0] == "Kapitel":
            continue
        out[cells[0]] = cells[4]
    return out


ARCHIVED_EXPORT = (
    CHRONIK_BOOK / "work" / "imports" / "romanforge" / "runs"
    / "20261007-201221" / "export.md"
)


def _real_fresh_export(dest_dir: Path) -> Path:
    """Echten archivierten RomanForge-Export als 'frischen Export' kopieren.

    Quelle: `books/<id>/work/imports/romanforge/runs/<stempel>/export.md`
    (der Schreibzugriff hat den rohen Export byte-identisch archiviert).
    """
    import shutil  # noqa: E402

    if not ARCHIVED_EXPORT.exists():
        raise unittest.SkipTest(f"Archivierter Export fehlt: {ARCHIVED_EXPORT}")
    dest = dest_dir / "fresh-export.md"
    shutil.copy2(str(ARCHIVED_EXPORT), str(dest))
    return dest


def _run_tool(*args: str) -> object:
    import subprocess as sp  # noqa: E402

    return sp.run(
        [sys.executable, str(REPO_ROOT / "tools" / "import_markdown_original.py"), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO_ROOT),
    )


class ParserTests(unittest.TestCase):
    """Parser an echten Chronik-Faellen (kopiert, nur Nummern/Titel)."""

    def test_001_praefix_48_kapitel(self) -> None:
        mod = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            baseline = _baseline_to_file(Path(tmp) / "baseline.md")
            data = baseline.read_bytes().decode("utf-8")
            chapters = mod.split_chapters(data)
        self.assertEqual(len(chapters), 48)
        self.assertEqual(chapters[0][0], "Prolog – Bagdad, Februar 1258")

    def test_006_innere_trenner_selbstvergleich_nichts(self) -> None:
        mod = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            baseline = _baseline_to_file(Path(tmp) / "baseline.md")
            book_root = _temp_book_from_chronik(Path(tmp), ["006"])
            chapters = mod.split_chapters(baseline.read_bytes().decode("utf-8"))
            title, body = chapters[5]
            data = (
                book_root / "work" / "scenes" / "de" / CHRONIK_STYLE
                / "006" / "scene-01.md"
            ).read_bytes().decode("utf-8")
            self.assertEqual(mod.scene_title(data), title)
            self.assertEqual(
                mod.text_hash(mod.canonical_text(body)),
                mod.text_hash(mod.canonical_text(mod.scene_body(data))),
            )

    def test_009_innere_trenner_aber_redigiert(self) -> None:
        mod = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            baseline = _baseline_to_file(Path(tmp) / "baseline.md")
            book_root = _temp_book_from_chronik(Path(tmp), ["009"])
            chapters = mod.split_chapters(baseline.read_bytes().decode("utf-8"))
            _title, body = chapters[8]
            data = (
                book_root / "work" / "scenes" / "de" / CHRONIK_STYLE
                / "009" / "scene-01.md"
            ).read_bytes().decode("utf-8")
            self.assertNotEqual(
                mod.text_hash(mod.canonical_text(body)),
                mod.text_hash(mod.canonical_text(mod.scene_body(data))),
            )

    def test_keine_kapitel_ist_fehler(self) -> None:
        mod = _load_module()
        with self.assertRaises(SystemExit):
            mod.split_chapters("# Titel ohne Kapitel\n\nText.\n")

class TableRowTests(unittest.TestCase):
    """Je eine Zeile der Abgleichtabelle (Abschnitt 3)."""

    def test_unveraendert_unveraendert_nichts(self) -> None:
        mod = _load_module()
        self.assertEqual(mod.classify_chapter(False, False), "nichts")

    def test_rf_geaendert_peter_unveraendert_vorschlag(self) -> None:
        mod = _load_module()
        self.assertEqual(mod.classify_chapter(True, False), "uebernahme-vorgeschlagen")

    def test_rf_unveraendert_peter_geaendert_peter_behalten(self) -> None:
        mod = _load_module()
        self.assertEqual(mod.classify_chapter(False, True), "peter-behalten")

    def test_beide_geaendert_konflikt(self) -> None:
        mod = _load_module()
        self.assertEqual(mod.classify_chapter(True, True), "konflikt")

    def test_neu_entfallen_verschoben_nur_melden_nie_auto(self) -> None:
        mod = _load_module()
        export = [("Neu A", "Text A"), ("Bekannt", "Text B")]
        known = {"001": "Bekannt"}
        rows = mod.match_chapters(export, known)
        by_title = {r["title_export"]: r for r in rows}
        self.assertEqual(by_title["Neu A"]["action"], "neu")
        self.assertEqual(by_title["Bekannt"]["action"], "zugeordnet")

    def test_titel_vor_position_bei_verschiebung(self) -> None:
        mod = _load_module()
        export = [("B", "Text B"), ("A", "Text A")]
        known = {"001": "A", "002": "B"}
        rows = mod.match_chapters(export, known)
        matched = sorted(r["chapter_id"] for r in rows if r["action"] == "zugeordnet")
        self.assertEqual(matched, ["001", "002"])


class PresumedRenameTests(unittest.TestCase):
    """Schritt 3: neu+entfallen an gleicher Position -> 'vermutlich umbenannt'.

    Wie der Rest der Suite an echten Chronik-Kapiteln (nur Titel gelesen).
    Reine Heuristik, nur Hinweis, kein Auto-Merge; Einstufungen bleiben
    neu/entfallen; der Hinweis steht in der detail-Spalte des Berichts.
    """

    SCENES = (
        REPO_ROOT / "books" / CHRONIK_ID
        / "work" / "scenes" / "de" / CHRONIK_STYLE
    )

    def _scene_title(self, mod, chapter_id: str) -> str:
        path = self.SCENES / chapter_id / "scene-01.md"
        if not path.exists():
            self.skipTest(f"Chronik-Szene {chapter_id} nicht vorhanden")
        return mod.scene_title(path.read_text(encoding="utf-8"))

    def test_umbenannt_an_gleicher_position(self) -> None:
        mod = _load_module()
        t1 = self._scene_title(mod, "001")
        t2 = self._scene_title(mod, "002")
        export = [(t1, "Text A"), ("Ganz neuer Titel", "Text B")]
        known = {"001": t1, "002": t2}
        matched = mod.match_chapters(export, known)
        presumed = mod.find_presumed_renames(matched, ["002"])
        self.assertEqual(presumed, {"002": "Ganz neuer Titel"})

    def test_neu_und_entfallen_ohne_positionspartner(self) -> None:
        mod = _load_module()
        t1 = self._scene_title(mod, "001")
        t2 = self._scene_title(mod, "002")
        t3 = self._scene_title(mod, "003")
        export = [(t1, "Text A"), (t3, "Text C"), ("Ganz neuer Titel", "Text B")]
        known = {"001": t1, "002": t2, "003": t3}
        matched = mod.match_chapters(export, known)
        # 002 faellt weg, das neue Kapitel steht aber an Position 3 -> kein Hinweis.
        presumed = mod.find_presumed_renames(matched, ["002"])
        self.assertEqual(presumed, {})

    def test_bericht_zeigt_vermutlich_umbenannt(self) -> None:
        mod = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            book_root = _temp_book_from_chronik(Path(tmp), ["001", "002"])
            title1 = mod.scene_title(
                (book_root / "work" / "scenes" / "de" / CHRONIK_STYLE
                 / "001" / "scene-01.md").read_text(encoding="utf-8"))
            export = Path(tmp) / "export.md"
            export.write_text(
                f"## {title1}\n\nText A.\n\n## Ganz neuer Titel\n\nText B.\n",
                encoding="utf-8")
            baseline = _baseline_to_file(Path(tmp) / "baseline.md")
            proc = _run_tool(
                "--book-root", str(book_root), "--source", str(export),
                "--baseline", str(baseline), "--compare")
            assert hasattr(proc, "returncode") and hasattr(proc, "stdout")
            self.assertEqual(getattr(proc, "returncode"), 2)
            out = str(getattr(proc, "stdout")) + str(getattr(proc, "stderr"))
            self.assertIn("vermutlich umbenannt", out)


class StateTests(unittest.TestCase):
    """K1: state.yaml pro Kapitel fortschreiben."""

    def test_nur_bearbeitete_kapitel_bekommen_neue_werte(self) -> None:
        mod = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.yaml"
            state = {
                "book": "demo",
                "chapters": {
                    "001": {"title": "A", "rf_base": "a1", "peter_base": "a2",
                            "base_export": "run-1"},
                    "002": {"title": "B", "rf_base": "b1", "peter_base": "b2",
                            "base_export": "run-1"},
                },
            }
            mod.write_state(state_path, state)
            mod.update_state_chapter(
                state, "001", title="A", rf_base="a9",
                peter_base="a8", base_export="run-2",
            )
            mod.write_state(state_path, state)
            reloaded = mod.load_state(state_path)
            self.assertEqual(reloaded["chapters"]["001"]["rf_base"], "a9")
            self.assertEqual(reloaded["chapters"]["002"]["rf_base"], "b1")
            self.assertEqual(reloaded["chapters"]["002"]["peter_base"], "b2")

    def test_nicht_uebernommenes_bleibt_stehen_K1(self) -> None:
        mod = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.yaml"
            state = {"book": "demo", "chapters": {
                "001": {"title": "A", "rf_base": "h0",
                        "peter_base": "h0", "base_export": "run-1"}}}
            mod.write_state(state_path, state)
            reloaded = mod.load_state(state_path)
            self.assertEqual(reloaded["chapters"]["001"]["rf_base"], "h0")


class KeepTests(unittest.TestCase):
    """K2: --keep loest Konflikt zugunsten von peter."""

    def test_keep_setzt_rf_base_peter_base_bleibt(self) -> None:
        mod = _load_module()
        state = {"book": "demo", "chapters": {
            "008": {"title": "X", "rf_base": "alt", "peter_base": "v2",
                    "base_export": "run-1"}}}
        mod.apply_keep(state, "008", new_rf_base="neu", base_export="run-2")
        chapter = state["chapters"]["008"]
        self.assertEqual(chapter["rf_base"], "neu")
        self.assertEqual(chapter["peter_base"], "v2")

    def test_accept_auf_konflikt_warnt(self) -> None:
        mod = _load_module()
        warning = mod.accept_warning("008", "konflikt")
        self.assertIn("008", warning)
        self.assertIn("peter", warning.lower())
        self.assertIn("Git", warning)


class NoInputTests(unittest.TestCase):
    def test_kein_input_aufruf_K4(self) -> None:
        import re as _re

        source = (REPO_ROOT / "tools" / "import_markdown_original.py").read_text(encoding="utf-8")
        hits = [line for line in source.splitlines()
                if _re.search(r"(?<![\w.])input\s*\(", line) and "Eingabeprompt" not in line]
        self.assertEqual(hits, [])


class ReportTests(unittest.TestCase):
    """Bericht an echten Faellen 001/025 (nur Nummern/Titel/Einstufung)."""

    def test_001_unveraendert_und_025_titelabgleich(self) -> None:
        mod = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            baseline = _baseline_to_file(Path(tmp) / "baseline.md")
            book_root = _temp_book_from_chronik(Path(tmp), ["001", "025"])
            chapters = mod.split_chapters(baseline.read_bytes().decode("utf-8"))
            rows = []
            for cid, pos in (("001", 0), ("025", 24)):
                title, body = chapters[pos]
                data = (
                    book_root / "work" / "scenes" / "de" / CHRONIK_STYLE
                    / cid / "scene-01.md"
                ).read_bytes().decode("utf-8")
                h = mod.text_hash(mod.canonical_text(body))
                rows.append(mod.build_row(
                    chapter_id=cid, title_export=title,
                    title_peter=mod.scene_title(data),
                    body_export=body, body_peter=mod.scene_body(data),
                    rf_base=h, peter_base=h))
            report = mod.render_report("Die dritte Chronik", rows)
            self.assertIn("001", report)
            self.assertIn("025", report)
            by_id = {r["chapter_id"]: r for r in rows}
            self.assertEqual(by_id["001"]["title_export"], by_id["001"]["title_peter"])


class SceneHeadTests(unittest.TestCase):
    """Kopfformate an echten Szenen (nur Titelabgleich)."""

    def test_008_rauten2_kopf(self) -> None:
        mod = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            book_root = _temp_book_from_chronik(Path(tmp), ["008"])
            baseline = _baseline_to_file(Path(tmp) / "baseline.md")
            chapters = mod.split_chapters(baseline.read_bytes().decode("utf-8"))
            data = (
                book_root / "work" / "scenes" / "de" / CHRONIK_STYLE
                / "008" / "scene-01.md"
            ).read_bytes().decode("utf-8")
            self.assertEqual(mod.scene_title(data), chapters[7][0])

    def test_025_kapitelkopf(self) -> None:
        mod = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            book_root = _temp_book_from_chronik(Path(tmp), ["025"])
            baseline = _baseline_to_file(Path(tmp) / "baseline.md")
            chapters = mod.split_chapters(baseline.read_bytes().decode("utf-8"))
            data = (
                book_root / "work" / "scenes" / "de" / CHRONIK_STYLE
                / "025" / "scene-01.md"
            ).read_bytes().decode("utf-8")
            self.assertEqual(mod.scene_title(data), chapters[24][0])
            self.assertTrue(data.lstrip().startswith("# "))


class CliDryRunTests(unittest.TestCase):
    def test_dry_run_und_compare_schreiben_nichts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            baseline = _baseline_to_file(Path(tmp) / "baseline.md")
            book_root = _temp_book_from_chronik(Path(tmp), ["001"])
            proc = _run_tool(
                "--book-root", str(book_root), "--source", str(baseline),
                "--baseline", str(baseline), "--dry-run")
            assert hasattr(proc, "returncode")
            self.assertEqual(getattr(proc, "returncode"), 0)
            self.assertFalse((book_root / "work" / "imports").exists())
            # Teilkopie: --compare meldet Rest als entfallen -> Exit 2, schreibt nichts.
            proc = _run_tool(
                "--book-root", str(book_root), "--source", str(baseline),
                "--baseline", str(baseline), "--compare")
            assert hasattr(proc, "returncode")
            self.assertEqual(getattr(proc, "returncode"), 2)
            self.assertFalse((book_root / "work" / "imports").exists())

    def test_compare_ohne_state_braucht_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            baseline = _baseline_to_file(Path(tmp) / "baseline.md")
            book_root = _temp_book_from_chronik(Path(tmp), ["001"])
            proc = _run_tool(
                "--book-root", str(book_root), "--source", str(baseline), "--compare")
            assert hasattr(proc, "returncode") and hasattr(proc, "stderr")
            self.assertEqual(getattr(proc, "returncode"), 2)
            err = str(getattr(proc, "stderr")) + str(getattr(proc, "stdout"))
            self.assertIn("--baseline", err)


class CliWriteTests(unittest.TestCase):
    """Schreiben auf Chronik-Tempokopie (nur Nummern/Einstufungen)."""

    def test_accept_008_schreibt_drei_kopien_seed_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            baseline = _baseline_to_file(Path(tmp) / "baseline.md")
            book_root = _temp_book_from_chronik(Path(tmp), ["008", "009"])
            scene_009 = (
                book_root / "work" / "scenes" / "de" / CHRONIK_STYLE
                / "009" / "scene-01.md"
            )
            before_009 = scene_009.read_bytes()
            proc = _run_tool(
                "--book-root", str(book_root), "--source", str(baseline),
                "--baseline", str(baseline), "--accept", "008")
            assert hasattr(proc, "returncode")
            self.assertEqual(getattr(proc, "returncode"), 0)
            mod = _load_module()
            state = mod.load_state(_state_path(book_root))
            self.assertIn("008", state["chapters"])
            # Option B: nicht uebernommenes 009 wird mit Baseline-Ausgangsstand
            # geseedet (nicht leer, kein Konflikt).
            self.assertIn("009", state["chapters"])
            base_hashes = mod.baseline_hashes(baseline)
            self.assertEqual(state["chapters"]["009"]["rf_base"], base_hashes["009"])
            self.assertEqual(state["chapters"]["009"]["peter_base"], base_hashes["009"])
            self.assertEqual(scene_009.read_bytes(), before_009)
            self.assertTrue(
                (book_root / "work" / "chapters" / "008-source.md").exists())
            self.assertTrue(
                (book_root / "work" / "scenes" / "de" / "008" / "scene-01.md").exists())

    def test_keep_025_nur_state_kein_schreiben(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            baseline = _baseline_to_file(Path(tmp) / "baseline.md")
            book_root = _temp_book_from_chronik(Path(tmp), ["025"])
            target = (
                book_root / "work" / "scenes" / "de" / CHRONIK_STYLE
                / "025" / "scene-01.md"
            )
            before = target.read_bytes()
            proc = _run_tool(
                "--book-root", str(book_root), "--source", str(baseline),
                "--baseline", str(baseline), "--keep", "025")
            assert hasattr(proc, "returncode")
            self.assertEqual(getattr(proc, "returncode"), 0)
            self.assertEqual(target.read_bytes(), before)
            mod = _load_module()
            state = mod.load_state(
                book_root / "work" / "imports" / "romanforge" / "state.yaml")
            self.assertIn("025", state["chapters"])

    def test_new_braucht_id_title_author_K4(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            baseline = _baseline_to_file(Path(tmp) / "baseline.md")
            proc = _run_tool("--new", "--source", str(baseline), "--title", "Nur Titel")
            assert hasattr(proc, "returncode") and hasattr(proc, "stderr")
            self.assertNotEqual(getattr(proc, "returncode"), 0)
            err = str(getattr(proc, "stderr")) + str(getattr(proc, "stdout"))
            self.assertIn("--author", err)



class NewCommandTests(unittest.TestCase):
    """--new (Stufe 1b): neutrales Paket, alle Kapitel, state.yaml + status.json.

    Quelle ist die Tempokopie des echt archivierten RomanForge-Exports
    (runs/20261007-201221/export.md). Geschrieben wird ausschliesslich unter
    --book-root (Temporarverzeichnis); das echte books/ bleibt unberuehrt.
    Keine Texte werden gelesen, nur Schluessel/Zahlen geprueft.
    """

    NEW_STYLE = "stil-01-original"

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _export_copy(self) -> Path:
        return _real_fresh_export(self.tmp)

    def _run_new(self, book_root: Path, source: Path, *extra: str):
        return _run_tool(
            "--new", "--book-root", str(book_root), "--source", str(source), *extra)

    def test_new_importiert_alle_kapitel_state_status_export(self) -> None:
        export = self._export_copy()
        book_root = self.tmp / "ashkara"
        proc = self._run_new(
            book_root, export,
            "--id", "ashkara", "--title", "Ashkara", "--author", "Testautor")
        self.assertEqual(
            getattr(proc, "returncode"), 0,
            msg=str(getattr(proc, "stderr")))
        mod = _load_module()
        chapters = mod.split_chapters(export.read_bytes().decode("utf-8"))
        self.assertEqual(len(chapters), 48)

        # drei Textkopien je Kapitel (work/chapters, scenes/de/NNN,
        # scenes/de/<style>/NNN)
        for idx in range(1, 49):
            cid = f"{idx:03d}"
            self.assertTrue(
                (book_root / "work" / "chapters" / f"{cid}-source.md").is_file(),
                msg=f"Kapitelquelle fehlt: {cid}")
            self.assertTrue(
                (book_root / "work" / "scenes" / "de" / cid / "scene-01.md").is_file(),
                msg=f"Quellszene fehlt: {cid}")
            self.assertTrue(
                (book_root / "work" / "scenes" / "de" / self.NEW_STYLE
                 / cid / "scene-01.md").is_file(),
                msg=f"DE-Szene fehlt: {cid}")

        # state.yaml: 48 Eintraege, rf_base == peter_base == Export-Hash
        state = mod.load_state(mod.state_path_for(book_root))
        self.assertEqual(len(state["chapters"]), 48)
        for idx, (_title, body) in enumerate(chapters, 1):
            cid = f"{idx:03d}"
            expected = mod.text_hash(mod.canonical_text(body))
            self.assertEqual(state["chapters"][cid]["rf_base"], expected)
            self.assertEqual(state["chapters"][cid]["peter_base"], expected)

        # status.json: 48 Kapitel, alle done
        status = json.loads(
            (book_root / "status" / "status.json").read_text(encoding="utf-8"))
        self.assertEqual(len(status["chapters"]), 48)
        self.assertTrue(all(c["status"] == "done" for c in status["chapters"]))
        self.assertTrue(all(c["words_target"] > 0 for c in status["chapters"]))

        # export.yaml: neutrale Vorlage, ohne Chronik-Felder, ohne
        # website:/marketing:-Block (nur Schluessel, keine Texte).
        export_cfg = yaml.safe_load(
            (book_root / "export.yaml").read_text(encoding="utf-8"))
        self.assertNotIn("website", export_cfg)
        self.assertNotIn("marketing", export_cfg)
        book = export_cfg.get("book", {})
        for key in ("original_title", "original_author", "summary", "author_bio"):
            self.assertNotIn(key, book)
        self.assertIn(book.get("translator"), ("", None))
        self.assertIn(book.get("translator_label"), ("", None))
        self.assertEqual(book.get("title"), "Ashkara")
        self.assertEqual(book.get("author"), "Testautor")

        # Folge-Compare ohne --baseline: 48 x 'nichts'
        proc2 = _run_tool(
            "--book-root", str(book_root), "--source", str(export), "--compare")
        self.assertEqual(
            getattr(proc2, "returncode"), 0,
            msg=str(getattr(proc2, "stderr")))
        actions = _parse_actions(str(getattr(proc2, "stdout")))
        self.assertEqual(len(actions), 48)
        self.assertTrue(all(v == "nichts" for v in actions.values()))

    def test_new_ohne_title_meldet_vorschlag_nicht_still(self) -> None:
        export = self._export_copy()
        book_root = self.tmp / "no-title"
        proc = self._run_new(book_root, export, "--author", "Testautor")
        self.assertNotEqual(getattr(proc, "returncode"), 0)
        out = str(getattr(proc, "stdout")) + str(getattr(proc, "stderr"))
        self.assertIn("Die dritte Chronik", out)  # Vorschlag aus '#'-Zeile
        self.assertIn("--title", out)
        self.assertFalse(book_root.exists())  # nichts angelegt

    def test_new_bricht_ab_wenn_paket_existiert(self) -> None:
        export = self._export_copy()
        book_root = self.tmp / "existing"
        book_root.mkdir(parents=True)
        (book_root / "book.yaml").write_text("id: existing\n", encoding="utf-8")
        proc = self._run_new(
            book_root, export, "--id", "existing",
            "--title", "Existing", "--author", "Testautor")
        self.assertEqual(getattr(proc, "returncode"), 2)
        out = str(getattr(proc, "stdout")) + str(getattr(proc, "stderr"))
        self.assertIn("existiert", out)


class FullStateSeedTests(unittest.TestCase):
    """Option B: Erstlauf legt state.yaml fuer ALLE Kapitel an; danach kein
    --baseline mehr noetig; Kapitel ohne Eintrag = 'ohne-ausgangsstand'."""

    def test_erster_keep_schreibt_48_eintraege(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            baseline = _baseline_to_file(Path(tmp) / "baseline.md")
            book_root = _temp_book_from_chronik(Path(tmp), "all")
            proc = _run_tool(
                "--book-root", str(book_root), "--source", str(baseline),
                "--baseline", str(baseline), "--keep", "008,031,033,036")
            self.assertEqual(getattr(proc, "returncode"), 0)
            mod = _load_module()
            state = mod.load_state(_state_path(book_root))
            self.assertEqual(len(state["chapters"]), 48)
            # Gekeepte Kapitel tragen den aktuellen Export-Hash, nicht die Baseline.
            self.assertNotEqual(
                state["chapters"]["008"]["rf_base"],
                state["chapters"]["001"]["rf_base"])
            self.assertEqual(
                state["chapters"]["001"]["rf_base"],
                state["chapters"]["001"]["peter_base"])

    def test_folge_compare_ohne_baseline_erwartete_verteilung(self) -> None:
        import collections  # noqa: E402

        with tempfile.TemporaryDirectory() as tmp:
            baseline = _baseline_to_file(Path(tmp) / "baseline.md")
            fresh = _real_fresh_export(Path(tmp))
            book_root = _temp_book_from_chronik(Path(tmp), "all")
            _run_tool(
                "--book-root", str(book_root), "--source", str(fresh),
                "--baseline", str(baseline), "--keep", "008,031,033,036")
            proc = _run_tool(
                "--book-root", str(book_root), "--source", str(fresh),
                "--compare")
            self.assertEqual(getattr(proc, "returncode"), 2)
            actions = _parse_actions(str(getattr(proc, "stdout")))
            counts = collections.Counter(actions.values())
            self.assertEqual(counts["nichts"], 35)
            self.assertEqual(counts["peter-behalten"], 11)
            self.assertEqual(counts["konflikt"], 2)
            self.assertEqual(counts["ohne-ausgangsstand"], 0)
            self.assertEqual(
                sorted(cid for cid, a in actions.items() if a == "konflikt"),
                ["012", "025"])

    def test_kapitel_ohne_state_eintrag_ist_ohne_ausgangsstand(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            baseline = _baseline_to_file(Path(tmp) / "baseline.md")
            book_root = _temp_book_from_chronik(Path(tmp), "all")
            _run_tool(
                "--book-root", str(book_root), "--source", str(baseline),
                "--baseline", str(baseline), "--keep", "036")
            mod = _load_module()
            state = mod.load_state(_state_path(book_root))
            del state["chapters"]["012"]
            mod.write_state(_state_path(book_root), state)
            proc = _run_tool(
                "--book-root", str(book_root), "--source", str(baseline),
                "--compare")
            self.assertEqual(getattr(proc, "returncode"), 2)
            actions = _parse_actions(str(getattr(proc, "stdout")))
            self.assertEqual(actions["012"], "ohne-ausgangsstand")
            self.assertNotEqual(actions["012"], "konflikt")

    def test_baseline_bei_vorhandener_state_wird_ignoriert(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            baseline = _baseline_to_file(Path(tmp) / "baseline.md")
            book_root = _temp_book_from_chronik(Path(tmp), "all")
            _run_tool(
                "--book-root", str(book_root), "--source", str(baseline),
                "--baseline", str(baseline), "--keep", "036")
            proc = _run_tool(
                "--book-root", str(book_root), "--source", str(baseline),
                "--baseline", str(baseline), "--compare")
            out = str(getattr(proc, "stdout")) + str(getattr(proc, "stderr"))
            self.assertIn("ignoriert", out)


class ChronikSelfCompareTests(unittest.TestCase):
    """K3 korrigiert: Ursprungs-Baseline (150f0c1) gegen Szenen.

    Sollwert a): 48 Kapitel, peter-geaendert genau die 13 redigierten.
    """

    EXPECTED_PETER_CHANGED = {
        "008", "009", "012", "018", "025", "026", "031", "033",
        "034", "035", "036", "041", "043",
    }

    def test_baseline_gegen_szenen_nur_redigierte_weichen_ab(self) -> None:
        import subprocess as sp  # noqa: E402

        mod = _load_module()
        scenes_root = (
            REPO_ROOT / "books" / "die-dritte-chronik" / "work"
            / "scenes" / "de" / "stil-01-original"
        )
        if not scenes_root.exists():
            self.skipTest("Chronik-Dateien nicht vorhanden")
        proc = sp.run(
            ["git", "show", "150f0c1:books/die-dritte-chronik/source/Die dritte Chronik.md"],
            capture_output=True, cwd=str(REPO_ROOT), shell=False,
        )
        if proc.returncode != 0 or not proc.stdout:
            self.skipTest("Ursprungs-Baseline 150f0c1 nicht verfuegbar")
        try:
            baseline_text = proc.stdout.decode("utf-8")
        except UnicodeDecodeError:
            self.skipTest("Baseline nicht UTF-8 lesbar")
        chapters = mod.split_chapters(baseline_text)
        self.assertEqual(len(chapters), 48)
        peter_changed: list[str] = []
        for idx, (title, body) in enumerate(chapters, 1):
            chapter_id = f"{idx:03d}"
            baseline = mod.text_hash(mod.canonical_text(body))
            scene_path = scenes_root / chapter_id / "scene-01.md"
            self.assertTrue(scene_path.exists(), msg=f"Szene fehlt: {chapter_id}")
            peter_body = mod.scene_body(scene_path.read_text(encoding="utf-8"))
            if mod.text_hash(mod.canonical_text(peter_body)) != baseline:
                peter_changed.append(chapter_id)
        self.assertEqual(set(peter_changed), self.EXPECTED_PETER_CHANGED)


if __name__ == "__main__":
    unittest.main()

