from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()
