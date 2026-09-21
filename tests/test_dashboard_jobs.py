from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib import dashboard_jobs  # noqa: E402


class DashboardJobsTests(unittest.TestCase):
    def test_progress_from_log_uses_last_progress_line(self) -> None:
        text = "\n".join([
            "start",
            "[1/3] Kapitel 001",
            "noise",
            "[3/3] Kapitel 003",
        ])

        self.assertEqual(dashboard_jobs.progress_from_log(text), (3, 3))

    def test_job_files_are_listed_newest_first(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = {
                "job_id": "first",
                "status": "completed",
                "started_at": "2026-01-01T10:00:00",
            }
            second = {
                "job_id": "second",
                "status": "running",
                "started_at": "2026-01-01T11:00:00",
            }
            dashboard_jobs.write_job(dashboard_jobs.job_file("first", root), first)
            dashboard_jobs.write_job(dashboard_jobs.job_file("second", root), second)

            jobs = dashboard_jobs.list_jobs(root)

        self.assertEqual([job["job_id"] for job in jobs], ["second", "first"])

    def test_runner_writes_completed_job_file_and_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            jobs_dir = root / "var" / "dashboard-jobs"
            log_path = jobs_dir / "unit.log"
            runner = REPO_ROOT / "tools" / "dashboard_job_runner.py"
            result = subprocess.run(
                [
                    sys.executable,
                    str(runner),
                    "--repo-root", str(root),
                    "--job-id", "unit",
                    "--jobs-dir", str(jobs_dir),
                    "--log-path", str(log_path),
                    "--book-id", "book",
                    "--style", "style",
                    "--provider", "provider",
                    "--kind", "test",
                    "--",
                    sys.executable,
                    "-c",
                    "print('Summary: ok')",
                ],
                capture_output=True,
                text=True,
            )
            job = json.loads((jobs_dir / "unit.json").read_text(encoding="utf-8"))
            log_text = log_path.read_text(encoding="utf-8")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(job["job_id"], "unit")
        self.assertEqual(job["status"], "completed")
        self.assertEqual(job["returncode"], 0)
        self.assertIn("updated_at", job)
        self.assertIn("Summary: ok", log_text)

    def test_refresh_job_treats_geschrieben_as_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            jobs_dir = dashboard_jobs.jobs_dir(root)
            jobs_dir.mkdir(parents=True)
            log_path = jobs_dir / "export.log"
            log_path.write_text(
                "Taschenbuch: 922 Seiten\nGeschrieben:\n  foo.pdf\n",
                encoding="utf-8",
            )
            job = {
                "job_id": "export",
                "status": "running",
                "pid": 0,
                "log_path": str(log_path.relative_to(root)),
                "started_at": datetime.now().isoformat(timespec="seconds"),
                "updated_at": datetime.now().isoformat(timespec="seconds"),
            }
            dashboard_jobs.write_job(dashboard_jobs.job_file("export", root), job)
            refreshed, _alive = dashboard_jobs.refresh_job(job, root)

        self.assertEqual(refreshed["status"], "completed")
        self.assertEqual(refreshed["returncode"], 0)

    def test_refresh_job_recovers_stale_when_print_report_complete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            jobs_dir = dashboard_jobs.jobs_dir(root)
            jobs_dir.mkdir(parents=True)
            print_dir = root / "books" / "pharao" / "exports" / "print"
            print_dir.mkdir(parents=True)
            report_path = print_dir / "book-print-report.json"
            report_path.write_text(
                '{"page_count": 754, "kdp_max_pages": 776}\n',
                encoding="utf-8",
            )
            manifest_path = print_dir / "book.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "outputs": [str(report_path.relative_to(root))],
                        "print_report": str(report_path.relative_to(root)),
                    }
                ),
                encoding="utf-8",
            )
            log_path = jobs_dir / "export.log"
            log_path.write_text(
                f"Geschrieben:\n  interior.pdf\nManifest: {manifest_path.relative_to(root)}\n",
                encoding="utf-8",
            )
            job = {
                "job_id": "stale-export",
                "status": "stale",
                "pid": 0,
                "kind": "export",
                "provider": "export:paperback",
                "log_path": str(log_path.relative_to(root)),
                "started_at": datetime.now().isoformat(timespec="seconds"),
                "updated_at": datetime.now().isoformat(timespec="seconds"),
            }
            dashboard_jobs.write_job(dashboard_jobs.job_file("stale-export", root), job)
            refreshed, _alive = dashboard_jobs.refresh_job(job, root)

        self.assertEqual(refreshed["status"], "completed")
        self.assertEqual(refreshed["returncode"], 0)

    def test_refresh_job_does_not_succeed_on_pdf_alone(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            jobs_dir = dashboard_jobs.jobs_dir(root)
            jobs_dir.mkdir(parents=True)
            pdf_path = root / "half.pdf"
            pdf_path.write_bytes(b"%PDF")
            log_path = jobs_dir / "export.log"
            log_path.write_text("rendering...\n", encoding="utf-8")
            job = {
                "job_id": "half-export",
                "status": "running",
                "pid": 0,
                "kind": "export",
                "provider": "export:paperback",
                "log_path": str(log_path.relative_to(root)),
                "started_at": datetime.now().isoformat(timespec="seconds"),
                "updated_at": datetime.now().isoformat(timespec="seconds"),
            }
            dashboard_jobs.write_job(dashboard_jobs.job_file("half-export", root), job)
            refreshed, _alive = dashboard_jobs.refresh_job(job, root)

        self.assertEqual(refreshed["status"], "stale")
        self.assertIsNone(refreshed.get("returncode"))


if __name__ == "__main__":
    unittest.main()
