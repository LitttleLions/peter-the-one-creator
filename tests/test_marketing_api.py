from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import yaml
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib.book_project import find_book  # noqa: E402
from lib.workbench_api import (  # noqa: E402
    MarketingOptions,
    build_marketing_export_command,
    marketing_context,
    marketing_settings,
)
from webapp.backend.main import create_app  # noqa: E402


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class MarketingCommandTests(unittest.TestCase):
    def test_command_without_provider_has_no_cost_flags(self) -> None:
        cmd = build_marketing_export_command(MarketingOptions(book_id="sample"))
        self.assertEqual(cmd, ["tools/export_marketing.py", "--book", "sample"])

    def test_command_with_style_provider_and_regenerate(self) -> None:
        cmd = build_marketing_export_command(
            MarketingOptions(
                book_id="sample",
                style="stil-test",
                provider="workspace_ai",
                regenerate=True,
                dry_run=True,
            )
        )
        for flag in ("--style", "--provider", "--regenerate", "--dry-run"):
            self.assertIn(flag, cmd)
        self.assertIn("workspace_ai", cmd)

    def test_command_can_skip_texts(self) -> None:
        cmd = build_marketing_export_command(
            MarketingOptions(book_id="sample", no_texts=True)
        )
        self.assertIn("--no-texts", cmd)


class MarketingApiTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        book_root = root / "books" / "sample"
        write_yaml(
            book_root / "book.yaml",
            {
                "id": "sample",
                "title": "Sample Book",
                "author": "Author",
                "source_lang": "ru",
                "target_lang": "de",
                "style_mode": "stil",
            },
        )
        write_yaml(
            book_root / "export.yaml",
            {
                "book": {
                    "title": "Sample Book",
                    "author": "Author",
                    "description": "Beschreibung.",
                },
                "website": {
                    "enabled": True,
                    "amazon_url": "https://www.amazon.de/dp/B0TEST",
                },
                "marketing": {
                    "enabled": True,
                    "campaign_start": "",
                    "youtube": {"url": "", "public": False},
                    "songs": [],
                },
            },
        )
        write_text(book_root / "styles" / "stil.md", "# Stil\n")
        write_text(
            book_root / "work" / "scenes" / "de" / "stil" / "001" / "scene-01.md",
            "Der erste Satz. Der zweite Satz.\n",
        )
        write_text(book_root / "assets" / "covers" / "cover.jpg", "cover")
        write_text(book_root / "assets" / "chapter" / "chapter-001.jpg", "image")
        self.repo_root = root
        self.client = TestClient(create_app(root))

    def tearDown(self) -> None:
        self.tmp.cleanup()


class MarketingApiTests(MarketingApiTestBase):
    def test_settings_reads_block_and_links(self) -> None:
        book = find_book(self.repo_root, "sample")
        settings = marketing_settings(book, self.repo_root)
        self.assertTrue(settings["enabled"])
        self.assertTrue(settings["has_block"])
        self.assertEqual(settings["amazon"]["url"], "https://www.amazon.de/dp/B0TEST")
        self.assertEqual(settings["amazon"]["assignment"], "user_provided")
        self.assertEqual(settings["songs"], [])
        self.assertFalse(settings["generated_texts"]["exists"])

    def test_context_reports_posts_and_missing_links(self) -> None:
        book = find_book(self.repo_root, "sample")
        context = marketing_context(book, "stil", self.repo_root)
        posts = {post["id"]: post for post in context["posts"]}
        self.assertEqual(posts["x-t0-intro"]["status"], "needs_review")
        self.assertEqual(posts["yt-main"]["status"], "omitted")
        self.assertTrue(context["relative_dates_only"])
        items = {item["item"] for item in context["missing"]}
        self.assertIn("song_data", items)
        self.assertIn("youtube_url", items)

    def test_marketing_endpoint_returns_context(self) -> None:
        response = self.client.get("/api/books/sample/marketing?style=stil")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["book_id"], "sample")
        self.assertEqual(len(body["posts"]), 9)
        self.assertEqual(body["amazon"]["url"], "https://www.amazon.de/dp/B0TEST")

    def test_marketing_endpoint_settings_only(self) -> None:
        response = self.client.get("/api/books/sample/marketing?preview=false")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["settings"]["enabled"])

    def test_action_plan_builds_marketing_command(self) -> None:
        response = self.client.post(
            "/api/actions/plan",
            json={
                "action": "marketing_export",
                "book_id": "sample",
                "style": "stil",
                "dry_run": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        command = response.json()["command"]
        self.assertEqual(command[0], "tools/export_marketing.py")
        self.assertIn("--dry-run", command)

    def test_action_plan_rejects_regenerate_without_provider(self) -> None:
        response = self.client.post(
            "/api/actions/plan",
            json={
                "action": "marketing_export",
                "book_id": "sample",
                "style": "stil",
                "regenerate": True,
            },
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
