"""Tests fuer das X-Clip-Rendering (Cover + Song -> MP4)."""

import unittest
from pathlib import Path

import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib import x_clip as xclip
from lib.workbench_api import XClipOptions, build_x_clip_command


class BuildFilterTests(unittest.TestCase):
    def test_filter_uses_blur_cover_shadow_and_yuv420p(self) -> None:
        filtr = xclip.build_filter(1080)
        self.assertIn("gblur=sigma=24", filtr)
        self.assertIn("scale=880:880", filtr)
        self.assertIn("black@0.34", filtr)
        self.assertIn("format=yuv420p[v]", filtr)

    def test_filter_scales_with_size(self) -> None:
        filtr = xclip.build_filter(720)
        self.assertIn("scale=720:720", filtr)
        self.assertIn("scale=586:586", filtr)


class BuildCommandTests(unittest.TestCase):
    def _request(self) -> xclip.XClipRequest:
        return xclip.XClipRequest(
            cover=Path("cover.png"),
            audio=Path("song.mp3"),
            output=Path("clip.mp4"),
            start=0.0,
            duration=45.0,
            title="Titel",
        )

    def test_command_maps_video_and_audio(self) -> None:
        cmd = xclip.build_command(self._request())
        self.assertEqual(cmd[0], "ffmpeg")
        self.assertIn("-filter_complex", cmd)
        self.assertIn("[v]", cmd)
        self.assertIn("1:a:0", cmd)
        self.assertIn("libx264", cmd)
        self.assertIn("aac", cmd)
        self.assertIn("+faststart", cmd)
        self.assertIn("yuv420p", cmd)

    def test_default_clip_name(self) -> None:
        self.assertEqual(xclip.default_clip_name("song-01", 45.0), "song-01-x-45s.mp4")


class WorkbenchCommandTests(unittest.TestCase):
    def test_build_x_clip_command(self) -> None:
        cmd = build_x_clip_command(XClipOptions(book_id="peter-i-buch-01"))
        self.assertEqual(
            cmd,
            [
                "tools/render_x_clip.py", "--book", "peter-i-buch-01",
                "--song", "song-01", "--start", "0", "--duration", "45",
                "--size", "1080",
            ],
        )

    def test_build_x_clip_command_with_overwrite_and_dry_run(self) -> None:
        cmd = build_x_clip_command(
            XClipOptions(book_id="b", song="song-02", start=10.0,
                         duration=30.0, overwrite=True, dry_run=True)
        )
        self.assertIn("--overwrite", cmd)
        self.assertIn("--dry-run", cmd)
        self.assertIn("10", cmd)
        self.assertIn("30", cmd)


if __name__ == "__main__":
    unittest.main()
