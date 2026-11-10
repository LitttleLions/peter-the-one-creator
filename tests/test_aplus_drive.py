from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import aplus_drive as drive  # noqa: E402


def _controls() -> list[dict]:
    return [
        {"index": 0, "tag": "input", "type": "text", "label": "Headline", "disabled": False, "options": []},
        {"index": 1, "tag": "input", "type": "text", "label": "Untertitel", "disabled": False, "options": []},
        {"index": 2, "tag": "input", "type": "text", "label": "Passwort", "disabled": False, "options": []},
        {"index": 3, "tag": "input", "type": "file", "label": "Bild", "disabled": False, "options": []},
        {"index": 4, "tag": "button", "type": "submit", "label": "Speichern", "disabled": False, "options": []},
        {"index": 5, "tag": "input", "type": "text", "label": "Gesperrt", "disabled": True, "options": []},
    ]


class UrlTests(unittest.TestCase):
    def test_allows_amazon_hosts(self) -> None:
        drive.assert_allowed_url("https://kdp.amazon.com/en_US/bookshelf")
        drive.assert_allowed_url("https://www.amazon.de/gp/whatever")

    def test_rejects_foreign_and_lookalike_hosts(self) -> None:
        for url in ("https://example.com", "https://kdp.amazon.com.evil.com", "file:///C:/x.html"):
            with self.assertRaises(SystemExit):
                drive.assert_allowed_url(url)


class SensitiveTests(unittest.TestCase):
    def test_sensitive_labels(self) -> None:
        for label in ("Passwort", "Steuer-ID", "IBAN", "E-Mail-Adresse", "Telefonnummer"):
            self.assertTrue(drive.is_sensitive(label), label)

    def test_normal_labels_are_not_sensitive(self) -> None:
        for label in ("Headline", "Beschreibung", "Bild"):
            self.assertFalse(drive.is_sensitive(label), label)

    def test_submit_labels(self) -> None:
        self.assertTrue(drive.requires_submit_confirmation("Speichern"))
        self.assertTrue(drive.requires_submit_confirmation("Veröffentlichen"))
        self.assertFalse(drive.requires_submit_confirmation("Weiter"))


class ResolveTests(unittest.TestCase):
    def test_resolves_case_and_space_insensitive(self) -> None:
        control, problem = drive.resolve_step(_controls(), {"label": "  hEaDlInE "})
        self.assertEqual(problem, "")
        self.assertIsNotNone(control)
        assert control is not None
        self.assertEqual(control["index"], 0)

    def test_ambiguous_label_is_reported(self) -> None:
        controls = [
            {"index": 0, "tag": "input", "type": "text", "label": "Headline", "disabled": False, "options": []},
            {"index": 1, "tag": "input", "type": "text", "label": "headline", "disabled": False, "options": []},
        ]
        control, problem = drive.resolve_step(controls, {"label": "Headline"})
        self.assertIsNone(control)
        self.assertIn("mehrdeutig", problem)

    def test_missing_label_is_reported(self) -> None:
        control, problem = drive.resolve_step(_controls(), {"label": "Gibtsnicht"})
        self.assertIsNone(control)
        self.assertIn("kein Feld", problem)


class ValidateTests(unittest.TestCase):
    def test_blocks_sensitive_and_disabled_fields(self) -> None:
        steps = [
            {"action": "fill", "label": "Passwort", "value": "geheim"},
            {"action": "fill", "label": "Gesperrt", "value": "x"},
        ]
        resolved, problems = drive.validate_steps(_controls(), steps, REPO_ROOT)
        self.assertEqual(resolved, [])
        self.assertTrue(any("sensibles Feld" in item for item in problems))
        self.assertTrue(any("deaktiviert" in item for item in problems))

    def test_upload_records_hash_and_flags_submit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            asset = Path(tmp) / "bild.jpg"
            asset.write_bytes(b"abc123")
            steps = [
                {"action": "upload", "label": "Bild", "path": "bild.jpg"},
                {"action": "click", "label": "Speichern"},
            ]
            resolved, problems = drive.validate_steps(_controls(), steps, Path(tmp))

        self.assertEqual(problems, [])
        self.assertEqual(resolved[0]["size"], 6)
        self.assertEqual(len(resolved[0]["sha256"]), 64)
        self.assertTrue(resolved[1]["needs_confirmation"])

    def test_missing_upload_file_is_a_problem(self) -> None:
        steps = [{"action": "upload", "label": "Bild", "path": "fehlt.jpg"}]
        resolved, problems = drive.validate_steps(_controls(), steps, REPO_ROOT)
        self.assertEqual(resolved, [])
        self.assertTrue(any("Datei fehlt" in item for item in problems))


class JournalTests(unittest.TestCase):
    def test_journal_appends_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.jsonl"
            drive.append_journal(path, {"ts": "2026-11-10T10:00:00", "outcome": "ok"})
            drive.append_journal(path, {"ts": "2026-11-10T10:00:01", "outcome": "blocked"})
            lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([line["outcome"] for line in lines], ["ok", "blocked"])


class BrowserTests(unittest.TestCase):
    """Ein echter Kopflauf gegen eine lokale Seite (uebersprungen ohne Chromium)."""

    def test_snapshot_and_execute_on_local_page(self) -> None:
        try:
            from playwright.sync_api import sync_playwright  # noqa: F401
        except Exception:
            self.skipTest("Playwright fehlt")

        with tempfile.TemporaryDirectory() as tmp:
            html = Path(tmp) / "form.html"
            html.write_text(
                "<html><body><form>"
                "<label for='h'>Headline</label><input id='h' name='h'>"
                "<label for='b'>Bild</label><input id='b' type='file'>"
                "<button type='button'>Speichern</button>"
                "</form></body></html>",
                encoding="utf-8",
            )
            journal = Path(tmp) / "journal.jsonl"
            try:
                with drive.open_browser(Path(tmp) / "state.json", headless=True) as (page, _context):
                    page.goto(html.as_uri())
                    controls = page.evaluate(drive.SNAPSHOT_JS)
                    labels = [control["label"] for control in controls]
                    plan = {
                        "url": html.as_uri(),
                        "steps": [
                            {"position": 1, "action": "fill", "label": "Headline", "value": "Hallo"},
                            {"position": 2, "action": "click", "label": "Speichern"},
                        ],
                    }
                    records = drive.execute_plan(page, plan, journal)
                    value = page.input_value("[data-drive-control='0']")
            except Exception as error:  # Chromium fehlt o. ae.
                self.skipTest(f"Browser nicht verfuegbar: {error}")

        self.assertIn("Headline", labels)
        self.assertIn("Speichern", labels)
        self.assertEqual(value, "Hallo")
        self.assertEqual(records[0]["outcome"], "ok")
        self.assertEqual(records[1]["outcome"], "blocked")


if __name__ == "__main__":
    unittest.main()
