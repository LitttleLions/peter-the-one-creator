from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib.kdp_client import KdpClient, KdpClientError  # noqa: E402
from kdp_sync import pull_book  # noqa: E402


class ClientGuardTests(unittest.TestCase):
    def test_phase1_blocks_writes_and_allows_read_plus_single_sync(self) -> None:
        calls: list[tuple[str, str]] = []

        def transport(method: str, path: str, body):
            calls.append((method, path))
            if path == "/api/kdp/metadata/sync/TITLEID1234/kindle":
                return {"book": {"titleId": "TITLEID1234", "format": "kindle", "title": "Der Pharao"}}
            if path == "/api/kdp/status":
                return {"connected": True}
            return {}

        client = KdpClient(transport=transport)
        self.assertTrue(client.status()["connected"])
        book = client.sync_format("TITLEID1234", "kindle")
        self.assertEqual(book["titleId"], "TITLEID1234")
        for blocked in (
            "/api/kdp/metadata/update",
            "/api/kdp/pricing/update",
            "/api/kdp/content/upload",
            "/api/kdp/publish",
            "/api/kdp/categories/update",
            "/api/kdp/titles/delete",
            "/api/kdp/reports/download",
            "/api/kdp/metadata/sync",
        ):
            with self.assertRaises(KdpClientError):
                client.post_json(blocked, {})
        self.assertEqual(
            calls,
            [
                ("GET", "/api/kdp/status"),
                ("POST", "/api/kdp/metadata/sync/TITLEID1234/kindle"),
            ],
        )


class PullTests(unittest.TestCase):
    def test_pull_reads_one_title_and_does_not_bind(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book_root = root / "books" / "pharao"
            book_root.mkdir(parents=True)
            export = book_root / "export.yaml"
            export.write_text(
                "book:\n"
                "  title: Der Pharao\n"
                "  author: Bolesław Prus\n"
                "  language: de-DE\n"
                "  publisher: Motivatier Stiftung\n"
                "  description: Ein Roman.\n"
                "website:\n"
                "  amazon_url: ''\n",
                encoding="utf-8",
            )
            before = export.read_text(encoding="utf-8")
            calls: list[str] = []

            def transport(method: str, path: str, body):
                calls.append(f"{method} {path}")
                if path == "/api/kdp/status":
                    return {"connected": True}
                if path == "/api/kdp/bookshelf":
                    return {"refs": [{"titleId": "TITLEID1234", "format": "kindle"}]}
                if path == "/api/kdp/catalog":
                    return {
                        "books": [
                            {
                                "key": "TITLEID1234",
                                "title": "Der Pharao",
                                "author": "Bolesław Prus",
                                "digitalAsin": "B0EXAMPLE1",
                            }
                        ]
                    }
                if path == "/api/kdp/metadata":
                    return {"books": []}
                if path == "/api/kdp/metadata/sync/TITLEID1234/kindle":
                    return {
                        "book": {
                            "titleId": "TITLEID1234",
                            "format": "kindle",
                            "title": "Der Pharao",
                            "asin": "B0EXAMPLE1",
                            "description": "<p>Ein Roman.</p>",
                            "language": "German",
                            "primaryAuthor": {"firstName": "Bolesław", "lastName": "Prus"},
                        }
                    }
                raise AssertionError(path)

            book = {
                "id": "pharao",
                "book_root": "books/pharao",
                "export_config": "books/pharao/export.yaml",
                "work_dir": "books/pharao/work",
                "style_mode": "stil-02-poetisch",
            }
            result = pull_book(book, root, KdpClient(transport=transport))
            ist = json.loads(Path(result["ist_path"]).read_text(encoding="utf-8"))
            self.assertEqual(export.read_text(encoding="utf-8"), before)

        self.assertEqual(result["title_id"], "TITLEID1234")
        self.assertEqual(ist["book"]["asin"], "B0EXAMPLE1")
        self.assertNotIn("metadata/update", " ".join(calls))
        self.assertNotIn("publish", " ".join(calls))


if __name__ == "__main__":
    unittest.main()
