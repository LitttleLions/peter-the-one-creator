"""Tests fuer rf_status (ein Befehl, nur lesen) und den Schutz von --accept gegen uncommittete Arbeit.

Laeuft ohne pytest:
    .\\.venv\\Scripts\\python.exe -m unittest tests.test_rf_status -v
"""

from __future__ import annotations

import io
import json
import subprocess
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

import import_markdown_original as imp  # noqa: E402
import rf_status as cli  # noqa: E402

CHAPTER = "Mara geht los."


def handoff(project_id: int = 8, **extra) -> dict:
    data = {
        "format": "romanforge-handoff/1", "mode": "update", "instance": "http://rf.example.de",
        "project": {"id": project_id, "uid": "u-1", "title": "Testbuch"},
        "expose": "Plot.", "publication": {"author_name": "Timo Verita"},
        "characters": [{"uid": "c1", "name": "Mara", "role": None, "description": None,
                        "appearance": None, "first_appears_chapter": None, "updated_at": None}],
        "chapters": [{"id": 11, "number": 1, "title": "Eins", "content": CHAPTER}],
    }
    data.update(extra)
    return data


class StatusTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "buch"
        (self.root / "work" / "imports" / "romanforge").mkdir(parents=True)
        (self.root / "book.yaml").write_text(
            "id: buch\ntitle: Testbuch\nauthor: Timo Verita\nsource_lang: de\ntarget_lang: de\n"
            "romanforge:\n  instance: rf.example.de\n  project_id: 8\n", encoding="utf-8")
        (self.root / "export.yaml").write_text("book:\n  title: Testbuch\n  author: Timo Verita\n", encoding="utf-8")
        (self.root / "names.yaml").write_text("entries: []\n", encoding="utf-8")
        state = {"book": "buch", "chapters": {"001": {"title": "Eins", "rf_id": "11", "rf_base": "x", "peter_base": "x"}}}
        (self.root / "work" / "imports" / "romanforge" / "state.yaml").write_text(yaml.safe_dump(state), encoding="utf-8")
        self.addCleanup(self.tmp.cleanup)
        project = SimpleNamespace(id="buch", root=self.root,
                                  config=yaml.safe_load((self.root / "book.yaml").read_text(encoding="utf-8")))
        for patcher in (
            mock.patch.object(cli, "discover_projects", return_value=[project]),
            mock.patch("lib.romanforge_client.RomanForgeConfig.from_env",
                       return_value=SimpleNamespace(base_url="https://rf.example.de")),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    def run_cli(self, args, data=None):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch("lib.romanforge_client.get_handoff_data", return_value=data or handoff()), \
                redirect_stdout(out), redirect_stderr(err):
            code = cli.main(args)
        return code, out.getvalue(), err.getvalue()

    def test_zeigt_alle_drei_bereiche_und_legt_nur_das_archiv_an(self):
        before = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file())
        code, out, err = self.run_cli(["--handoff", "11111111-aaaa"])
        self.assertEqual((code, err), (0, ""))
        for heading in ("## Kapitel", "## Figuren", "## Buchangaben", "## Zusammenfassung"):
            self.assertIn(heading, out)
        self.assertIn("Nichts uebernommen", out)
        after = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file())
        new = [p for p in after if p not in before]
        self.assertEqual(len(new), 1)
        self.assertTrue(new[0].endswith("handoff-meta.json"))
        meta = json.loads((self.root / new[0]).read_text(encoding="utf-8"))
        self.assertNotIn("content", meta["chapters"][0])
        self.assertEqual(meta["chapters"][0]["id"], 11)
        self.assertEqual(meta["publication"]["author_name"], "Timo Verita")

    def test_ohne_archiv_wird_gar_nichts_geschrieben(self):
        before = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file())
        self.run_cli(["--handoff", "h", "--no-archive"])
        after = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file())
        self.assertEqual(before, after)

    def test_falsche_projekt_id_bricht_ab(self):
        code, out, err = self.run_cli(["--handoff", "h", "--book", "buch"], handoff(project_id=99))
        self.assertEqual(code, 2)
        self.assertIn("gebunden", err)
        self.assertNotIn("## Kapitel", out)

    def test_ohne_gebundenes_buch_gibt_hinweis(self):
        code, _, err = self.run_cli(["--handoff", "h"], handoff(project_id=99))
        self.assertEqual(code, 2)
        self.assertIn("kein eindeutiges Buch", err)

    def test_figur_mit_gleichem_namen_ist_konflikt_mit_exit_1(self):
        data = handoff()
        data["characters"].append(dict(data["characters"][0], uid="c2"))
        code, out, _ = self.run_cli(["--handoff", "h"], data)
        self.assertEqual(code, 1)
        self.assertIn("konflikt", out)


class AcceptGuardTests(unittest.TestCase):
    def test_ausserhalb_von_git_ist_nichts_ungesichert(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(imp.uncommitted_book_paths(Path(tmp)), [])

    def test_uncommittete_kapitelfassung_wird_gemeldet(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run = lambda *a: subprocess.run(["git", "-C", tmp, *a], check=True, capture_output=True)  # noqa: E731
            run("init", "-q")
            run("config", "user.email", "t@example.de")
            run("config", "user.name", "T")
            (root / "work" / "chapters").mkdir(parents=True)
            (root / "work" / "chapters" / "001-source.md").write_text("alt", encoding="utf-8")
            run("add", "-A")
            run("commit", "-q", "-m", "x")
            self.assertEqual(imp.uncommitted_book_paths(root), [])
            (root / "work" / "chapters" / "001-source.md").write_text("von Hand geaendert", encoding="utf-8")
            dirty = imp.uncommitted_book_paths(root)
            self.assertEqual(len(dirty), 1)
            self.assertIn("001-source.md", dirty[0])


if __name__ == "__main__":
    unittest.main()
