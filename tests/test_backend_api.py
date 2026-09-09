from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from fastapi.testclient import TestClient

from webapp.backend.main import create_app


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


class BackendApiTests(unittest.TestCase):
    def make_repo(self) -> Path:
        root = Path(self.tmp.name)
        book_root = root / "books" / "sample"
        write_yaml(
            book_root / "book.yaml",
            {
                "id": "sample",
                "title": "Sample Book",
                "author": "Author",
                "source_path": "source/sample.rtf",
                "source_lang": "ru",
                "target_lang": "de",
                "style_mode": "stil",
            },
        )
        work = book_root / "work"
        (work / "chapters").mkdir(parents=True)
        (work / "scenes" / "ru" / "001").mkdir(parents=True)
        (work / "scenes" / "ru" / "002").mkdir(parents=True)
        (work / "scenes" / "de" / "stil" / "001").mkdir(parents=True)
        (book_root / "styles").mkdir(parents=True)
        (root / "config").mkdir(parents=True)
        (work / "chapters" / "001-source.md").write_text("source 1", encoding="utf-8")
        (work / "chapters" / "002-source.md").write_text("source 2", encoding="utf-8")
        (work / "scenes" / "ru" / "001" / "scene-01.md").write_text("ru1", encoding="utf-8")
        (work / "scenes" / "ru" / "002" / "scene-01.md").write_text("ru2", encoding="utf-8")
        (work / "scenes" / "de" / "stil" / "001" / "scene-01.md").write_text("de1", encoding="utf-8")
        (book_root / "styles" / "stil.md").write_text("# Stil\n", encoding="utf-8")
        (book_root / "status" / "logs").mkdir(parents=True)
        (book_root / "status" / "logs" / "001.log.md").write_text("status log\nline 2", encoding="utf-8")
        (root / "var" / "dashboard-jobs").mkdir(parents=True)
        (root / "var" / "dashboard-jobs" / "job.log").write_text("job log\nline 2", encoding="utf-8")
        write_yaml(
            book_root / "names.yaml",
            {
                "entries": [
                    {
                        "source": "Пётр",
                        "target": "Peter",
                        "aliases": ["Petr"],
                        "type": "person",
                        "status": "approved",
                        "note": "Zar",
                    }
                ]
            },
        )
        write_yaml(
            root / "config" / "models.yaml",
            {
                "models": [
                    {
                        "id": "anthropic/claude-sonnet-4.6",
                        "name": "Claude Sonnet 4.6",
                        "provider": "Anthropic",
                    }
                ]
            },
        )
        return root

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo_root = self.make_repo()
        self.client = TestClient(create_app(self.repo_root))

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_health(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_books_summary(self) -> None:
        response = self.client.get("/api/books")

        self.assertEqual(response.status_code, 200)
        books = response.json()["books"]
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0]["id"], "sample")
        self.assertEqual(books[0]["chapters"], 2)
        self.assertEqual(books[0]["missing_scenes"], 1)

    def test_book_detail_and_404(self) -> None:
        response = self.client.get("/api/books/sample")
        missing = self.client.get("/api/books/missing")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["book"]["title"], "Sample Book")
        self.assertEqual(missing.status_code, 404)

    def test_chapters_for_selected_style(self) -> None:
        response = self.client.get("/api/books/sample/chapters?style=stil")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["style"], "stil")
        by_id = {row["Kapitel"]: row for row in body["chapters"]}
        self.assertEqual(by_id["001"]["RU"], 1)
        self.assertEqual(by_id["001"]["DE"], 1)
        self.assertEqual(by_id["002"]["Fehlt"], 1)

    def test_styles_and_models(self) -> None:
        styles = self.client.get("/api/books/sample/styles")
        models = self.client.get("/api/models")

        self.assertEqual(styles.status_code, 200)
        self.assertEqual(styles.json()["default_style"], "stil")
        self.assertEqual(styles.json()["styles"][0]["id"], "stil")
        self.assertEqual(models.status_code, 200)
        self.assertEqual(models.json()["models"][0]["id"], "anthropic/claude-sonnet-4.6")

    def test_names(self) -> None:
        response = self.client.get("/api/books/sample/names")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["book_id"], "sample")
        self.assertEqual(body["names"][0]["source"], "Пётр")
        self.assertEqual(body["names"][0]["target"], "Peter")
        self.assertEqual(body["names"][0]["aliases"], "Petr")

    def test_illustration_setting_roundtrip(self) -> None:
        empty = self.client.get("/api/books/sample")
        self.assertEqual(empty.status_code, 200)
        self.assertEqual(empty.json()["summary"].get("illustration_setting") or "", "")

        response = self.client.put(
            "/api/books/sample/illustration-setting",
            json={
                "illustration_setting": (
                    "Imperial Russia, painterly literary illustration, "
                    "atmospheric light, clear central figure."
                )
            },
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["saved"])
        self.assertIn("painterly literary illustration", body["illustration_setting"])
        self.assertIn(
            "painterly literary illustration",
            body["summary"]["illustration_setting"],
        )

        yaml_text = (self.repo_root / "books" / "sample" / "book.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("illustration_setting: >-", yaml_text)
        self.assertIn("painterly literary illustration", yaml_text)

        too_long = self.client.put(
            "/api/books/sample/illustration-setting",
            json={"illustration_setting": "x" * 4001},
        )
        self.assertEqual(too_long.status_code, 400)

    def test_logs_list_and_detail(self) -> None:
        response = self.client.get("/api/logs?book_id=sample")

        self.assertEqual(response.status_code, 200)
        logs = response.json()["logs"]
        sources = {item["source"] for item in logs}
        self.assertIn("dashboard-job", sources)
        self.assertIn("book-status", sources)

        detail = self.client.get(f"/api/logs/{logs[0]['id']}?lines=1")

        self.assertEqual(detail.status_code, 200)
        body = detail.json()
        self.assertIn("line 2", body["content"])
        self.assertTrue(body["truncated"])

    def test_jobs_list(self) -> None:
        jobs_dir = self.repo_root / "var" / "dashboard-jobs"
        jobs_dir.mkdir(parents=True, exist_ok=True)
        (jobs_dir / "job-1.json").write_text(
            json.dumps({
                "job_id": "job-1",
                "status": "completed",
                "book_id": "sample",
                "style": "stil",
                "provider": "openrouter",
                "kind": "review",
                "started_at": "2026-06-23T12:00:00",
                "log_path": "var/dashboard-jobs/job-1.log",
            }),
            encoding="utf-8",
        )

        response = self.client.get("/api/jobs")

        self.assertEqual(response.status_code, 200)
        jobs = response.json()["jobs"]
        self.assertEqual(jobs[0]["job_id"], "job-1")
        self.assertFalse(jobs[0]["running"])
        self.assertEqual(jobs[0]["progress"], {"done": None, "total": None})

    def test_job_detail_includes_log_tail_and_progress(self) -> None:
        jobs_dir = self.repo_root / "var" / "dashboard-jobs"
        jobs_dir.mkdir(parents=True, exist_ok=True)
        (jobs_dir / "job-2.log").write_text(
            "\n".join([
                "start",
                "[1/3] Kapitel 001",
                "[2/3] Kapitel 002",
            ]),
            encoding="utf-8",
        )
        (jobs_dir / "job-2.json").write_text(
            json.dumps({
                "job_id": "job-2",
                "status": "completed",
                "book_id": "sample",
                "style": "stil",
                "provider": "openrouter",
                "kind": "review",
                "started_at": "2026-06-23T12:00:00",
                "log_path": "var/dashboard-jobs/job-2.log",
            }),
            encoding="utf-8",
        )

        response = self.client.get("/api/jobs/job-2?log_lines=2")
        missing = self.client.get("/api/jobs/missing")

        self.assertEqual(response.status_code, 200)
        job = response.json()["job"]
        self.assertEqual(job["job_id"], "job-2")
        self.assertEqual(job["progress"], {"done": 2, "total": 3})
        self.assertNotIn("start", job["log_tail"])
        self.assertIn("[2/3] Kapitel 002", job["log_tail"])
        self.assertEqual(missing.status_code, 404)

    def test_stop_non_running_job_returns_current_detail(self) -> None:
        jobs_dir = self.repo_root / "var" / "dashboard-jobs"
        jobs_dir.mkdir(parents=True, exist_ok=True)
        (jobs_dir / "job-3.json").write_text(
            json.dumps({
                "job_id": "job-3",
                "status": "completed",
                "book_id": "sample",
                "style": "stil",
                "provider": "openrouter",
                "kind": "review",
                "started_at": "2026-06-23T12:00:00",
                "log_path": "var/dashboard-jobs/job-3.log",
            }),
            encoding="utf-8",
        )

        response = self.client.post("/api/jobs/job-3/stop")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["stopped"])
        self.assertEqual(body["job"]["job_id"], "job-3")
        self.assertEqual(body["message"], "Job laeuft nicht.")

    def test_action_plan_translate_batch(self) -> None:
        response = self.client.post(
            "/api/actions/plan",
            json={
                "action": "translate_batch",
                "book_id": "sample",
                "style": "stil",
                "provider": "ollama",
                "ollama_model": "gemma4:latest",
                "scope": "Bereich",
                "start_chapter": "001",
                "end_chapter": "002",
                "chunk_char_limit": 9000,
                "dry_run": True,
                "assemble_after": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["action"], "translate_batch")
        self.assertEqual(body["command"][0], "tools/translate_batch.py")
        self.assertIn("--from", body["command"])
        self.assertIn("--to", body["command"])
        self.assertIn("--dry-run", body["command"])
        self.assertIn("--assemble-after", body["command"])

    def test_action_plan_init_book_does_not_require_existing_book(self) -> None:
        response = self.client.post(
            "/api/actions/plan",
            json={
                "action": "init_book",
                "source": "books/Author - Title.rtf",
                "title": "Title",
                "author": "Author",
                "style": "stil",
                "source_lang": "pl",
                "target_lang": "de",
                "ruleset_apply": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        command = response.json()["command"]
        self.assertEqual(command[0], "tools/init_book.py")
        self.assertIn("--ruleset-apply", command)
        self.assertIn("pl", command)

    def test_action_plan_rejects_unknown_action_and_missing_book(self) -> None:
        unknown = self.client.post(
            "/api/actions/plan",
            json={"action": "unknown", "book_id": "sample"},
        )
        missing_book = self.client.post(
            "/api/actions/plan",
            json={
                "action": "extract_scenes",
                "book_id": "missing",
                "chapter": "001",
            },
        )

        self.assertEqual(unknown.status_code, 400)
        self.assertIn("Unbekannte Action", unknown.json()["detail"])
        self.assertEqual(missing_book.status_code, 404)

    def test_job_start_allows_translate_batch(self) -> None:
        with patch("webapp.backend.main.dashboard_jobs.start_job") as start_job:
            start_job.return_value = {
                "job_id": "job-start",
                "status": "completed",
                "book_id": "sample",
                "style": "stil",
                "provider": "ollama",
                "kind": "batch",
                "started_at": "2026-06-23T12:00:00",
                "log_path": "var/dashboard-jobs/job-start.log",
            }

            response = self.client.post(
                "/api/jobs",
                json={
                    "action": "translate_batch",
                    "book_id": "sample",
                    "style": "stil",
                    "provider": "ollama",
                    "ollama_model": "gemma4:latest",
                    "scope": "Aktuelles Kapitel",
                    "chapter": "001",
                },
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["job"]["job_id"], "job-start")
        self.assertEqual(body["job"]["kind"], "batch")
        self.assertEqual(body["command"][0], "tools/translate_batch.py")
        start_job.assert_called_once()
        self.assertEqual(start_job.call_args.kwargs["kind"], "batch")
        self.assertEqual(start_job.call_args.kwargs["provider"], "ollama")

    def test_job_start_allows_translate_chapter_scene(self) -> None:
        with patch("webapp.backend.main.dashboard_jobs.start_job") as start_job:
            start_job.return_value = {
                "job_id": "job-translate",
                "status": "completed",
                "book_id": "sample",
                "style": "stil",
                "provider": "openrouter",
                "kind": "translate",
                "started_at": "2026-06-23T12:00:00",
                "log_path": "var/dashboard-jobs/job-translate.log",
            }

            response = self.client.post(
                "/api/jobs",
                json={
                    "action": "translate_chapter",
                    "book_id": "sample",
                    "style": "stil",
                    "provider": "openrouter",
                    "model": "anthropic/claude-sonnet-4.6",
                    "chapter": "001",
                    "scene": "01",
                },
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["job"]["job_id"], "job-translate")
        self.assertIn("--scene", body["command"])
        self.assertEqual(start_job.call_args.kwargs["kind"], "translate")

    def test_job_start_allows_review(self) -> None:
        with patch("webapp.backend.main.dashboard_jobs.start_job") as start_job:
            start_job.return_value = {
                "job_id": "job-review",
                "status": "completed",
                "book_id": "sample",
                "style": "stil",
                "provider": "review:none",
                "kind": "review",
                "started_at": "2026-06-23T12:00:00",
                "log_path": "var/dashboard-jobs/job-review.log",
            }

            response = self.client.post(
                "/api/jobs",
                json={
                    "action": "review",
                    "book_id": "sample",
                    "style": "stil",
                    "scope": "Aktuelles Kapitel",
                    "chapter": "001",
                    "llm": "none",
                    "fail_on_errors": True,
                },
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["job"]["job_id"], "job-review")
        self.assertEqual(body["job"]["provider"], "review:none")
        self.assertIn("--fail-on-errors", body["command"])
        self.assertEqual(start_job.call_args.kwargs["kind"], "review")

    def test_job_start_allows_export(self) -> None:
        with patch("webapp.backend.main.dashboard_jobs.start_job") as start_job:
            start_job.return_value = {
                "job_id": "job-export",
                "status": "completed",
                "book_id": "sample",
                "style": "stil",
                "provider": "export:pdf",
                "kind": "export",
                "started_at": "2026-06-23T12:00:00",
                "log_path": "var/dashboard-jobs/job-export.log",
            }

            response = self.client.post(
                "/api/jobs",
                json={
                    "action": "export",
                    "book_id": "sample",
                    "style": "stil",
                    "scope": "chapter",
                    "chapter": "001",
                    "export_format": "pdf",
                    "allow_partial": True,
                },
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["job"]["job_id"], "job-export")
        self.assertEqual(body["job"]["provider"], "export:pdf")
        self.assertIn("--allow-partial", body["command"])
        self.assertEqual(start_job.call_args.kwargs["kind"], "export")

    def test_job_start_allows_build_shelf_website(self) -> None:
        with patch("webapp.backend.main.dashboard_jobs.start_job") as start_job:
            start_job.return_value = {
                "job_id": "job-shelf",
                "status": "completed",
                "book_id": "website",
                "style": "",
                "provider": "build",
                "kind": "build_shelf_website",
                "started_at": "2026-06-23T12:00:00",
                "log_path": "var/dashboard-jobs/job-shelf.log",
            }

            response = self.client.post(
                "/api/jobs",
                json={"action": "build_shelf_website"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["job"]["job_id"], "job-shelf")
        self.assertEqual(body["command"], ["tools/build_shelf_website.py"])
        self.assertEqual(start_job.call_args.kwargs["kind"], "build_shelf_website")
        self.assertEqual(start_job.call_args.kwargs["book_id"], "website")

    def test_website_settings_round_trip(self) -> None:
        export_path = self.repo_root / "books" / "sample" / "export.yaml"
        export_path.write_text(
            "\n".join([
                "book:",
                "  title: Sample Book",
                "  author: Author",
                "website:",
                "  enabled: false",
                "  amazon_url: ''",
                "  sort_order: 5",
                "",
            ]),
            encoding="utf-8",
        )
        covers = self.repo_root / "books" / "sample" / "assets" / "covers"
        covers.mkdir(parents=True)
        (covers / "cover.png").write_bytes(b"png")

        listed = self.client.get("/api/website/books")
        self.assertEqual(listed.status_code, 200)
        listed_body = listed.json()
        self.assertEqual(listed_body["enabled_count"], 0)
        self.assertEqual(listed_body["books"][0]["id"], "sample")
        self.assertFalse(listed_body["books"][0]["enabled"])
        self.assertTrue(listed_body["books"][0]["has_cover"])

        got = self.client.get("/api/books/sample/website")
        self.assertEqual(got.status_code, 200)
        self.assertFalse(got.json()["enabled"])
        self.assertEqual(got.json()["sort_order"], 5)

        saved = self.client.put(
            "/api/books/sample/website",
            json={
                "enabled": True,
                "amazon_url": "https://www.amazon.de/dp/example",
                "sort_order": 12,
            },
        )
        self.assertEqual(saved.status_code, 200)
        self.assertTrue(saved.json()["enabled"])
        self.assertEqual(saved.json()["amazon_url"], "https://www.amazon.de/dp/example")
        self.assertEqual(saved.json()["sort_order"], 12)

        text = export_path.read_text(encoding="utf-8")
        self.assertIn("enabled: true", text)
        self.assertIn("amazon_url: https://www.amazon.de/dp/example", text)
        self.assertIn("sort_order: 12", text)
        self.assertIn("book:", text)

        enabled_only = self.client.get("/api/website/books?enabled_only=true")
        self.assertEqual(enabled_only.status_code, 200)
        self.assertEqual(enabled_only.json()["enabled_count"], 1)
        self.assertTrue(enabled_only.json()["books"][0]["has_amazon"])

    def test_website_rejects_bad_amazon_url(self) -> None:
        response = self.client.put(
            "/api/books/sample/website",
            json={"enabled": True, "amazon_url": "not-a-url", "sort_order": 1},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("amazon_url", response.json()["detail"])

    def test_job_start_rejects_dry_run(self) -> None:
        dry_run = self.client.post(
            "/api/jobs",
            json={
                "action": "translate_batch",
                "book_id": "sample",
                "style": "stil",
                "provider": "ollama",
                "scope": "Aktuelles Kapitel",
                "chapter": "001",
                "dry_run": True,
            },
        )

        self.assertEqual(dry_run.status_code, 400)
        self.assertIn("Dry-runs", dry_run.json()["detail"])

    def test_job_events_stream_terminal_job_snapshot(self) -> None:
        jobs_dir = self.repo_root / "var" / "dashboard-jobs"
        jobs_dir.mkdir(parents=True, exist_ok=True)
        (jobs_dir / "job-events.log").write_text(
            "[1/1] Kapitel 001\nSummary: ok",
            encoding="utf-8",
        )
        (jobs_dir / "job-events.json").write_text(
            json.dumps({
                "job_id": "job-events",
                "status": "completed",
                "book_id": "sample",
                "style": "stil",
                "provider": "openrouter",
                "kind": "review",
                "started_at": "2026-06-23T12:00:00",
                "log_path": "var/dashboard-jobs/job-events.log",
            }),
            encoding="utf-8",
        )

        with self.client.stream("GET", "/api/jobs/job-events/events?interval_sec=0.1") as response:
            body = "".join(response.iter_text())

        self.assertEqual(response.status_code, 200)
        self.assertIn("event: job", body)
        self.assertIn('"job_id": "job-events"', body)
        self.assertIn('"done": 1', body)
        self.assertIn("Summary: ok", body)

    def test_job_events_missing_job_returns_404(self) -> None:
        response = self.client.get("/api/jobs/missing/events")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
