from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import aplus_build as aplus  # noqa: E402


def _meta() -> dict:
    return {
        "title": "Die Sprache des Anderen",
        "subtitle": "Ein Straßburger Roman aus dem 9. Jahrhundert",
        "description": (
            "Erster Absatz über Alda und die Schulden.\n\n"
            "Zweiter Absatz über Raginbert und die Urkunde.\n\n"
            "Dritter Absatz über den Jungen, der lesen lernt."
        ),
        "summary": "Zusammenfassung des Romans. " * 40,
        "series": "Zwischen Rhein und Maas",
        "series_volume": 2,
    }


def _book_root(tmp: Path, images: int = 4) -> Path:
    root = tmp / "buch"
    chapter = root / "assets" / "chapter"
    chapter.mkdir(parents=True)
    for index in range(1, images + 1):
        path = chapter / f"chapter-{index:03d}.jpg"
        Image.new("RGB", (600, 800), (30 * index, 40, 60)).save(path, format="JPEG")
    return root


class TrimTests(unittest.TestCase):
    def test_trim_keeps_short_text(self) -> None:
        self.assertEqual(aplus.trim_text("Kurzer Satz.", 300), "Kurzer Satz.")

    def test_trim_cuts_on_word_boundary(self) -> None:
        text = "wort " * 100
        trimmed = aplus.trim_text(text, 40)
        self.assertLessEqual(len(trimmed), 40)
        self.assertTrue(trimmed.endswith("..."))
        self.assertFalse(trimmed[:-3].endswith("wor"))
        self.assertNotIn("  ", trimmed)


class PlanTests(unittest.TestCase):
    def test_plan_uses_title_series_and_description(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _book_root(Path(tmp))
            plan = aplus.build_plan(_meta(), "die-sprache-des-anderen", root)

        by_id = {module.module_id: module for module in plan.modules}
        self.assertEqual(by_id["hero"].headline, "Die Sprache des Anderen")
        self.assertIn("Alda", by_id["hero"].body)
        self.assertIn("Raginbert", by_id["three"].body)
        self.assertNotIn("Erster Absatz", by_id["three"].body)
        self.assertEqual(by_id["text"].headline, "Zwischen Rhein und Maas - Band 2")
        self.assertLessEqual(len(by_id["text"].body), aplus.SUMMARY_LIMIT)

    def test_plan_declares_amazon_image_sizes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _book_root(Path(tmp))
            plan = aplus.build_plan(_meta(), "buch", root)

        by_id = {module.module_id: module for module in plan.modules}
        hero = by_id["hero"].images[0]
        self.assertEqual((hero.width, hero.height), (970, 600))
        thumbs = by_id["three"].images
        self.assertEqual(len(thumbs), 3)
        self.assertTrue(all((item.width, item.height) == (300, 300) for item in thumbs))
        self.assertTrue(all(item.source is not None for item in thumbs))

    def test_plan_without_images_notes_the_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _book_root(Path(tmp), images=0)
            plan = aplus.build_plan(_meta(), "buch", root)

        reasons = " ".join(item["reason"] for item in plan.skipped)
        self.assertIn("Kapitelbilder", reasons)
        hero = [module for module in plan.modules if module.module_id == "hero"][0]
        self.assertIsNone(hero.images[0].source)


class OutputTests(unittest.TestCase):
    def test_render_image_produces_exact_pixels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _book_root(Path(tmp))
            target = aplus.ModuleImage(role="hero", width=970, height=600)
            destination = Path(tmp) / "out.jpg"
            aplus.render_image(root / "assets" / "chapter" / "chapter-001.jpg", target, destination)
            with Image.open(destination) as image:
                self.assertEqual(image.size, (970, 600))
                self.assertEqual(image.mode, "RGB")

    def test_write_outputs_writes_plan_copy_and_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _book_root(Path(tmp))
            out = Path(tmp) / "aplus"
            plan = aplus.build_plan(_meta(), "buch", root)
            written = aplus.write_outputs(plan, out)

            payload = json.loads((out / "modules.json").read_text(encoding="utf-8"))
            copy_text = (out / "copy.md").read_text(encoding="utf-8")
            hero_file = out / "assets" / "hero-hero-970x600.jpg"

            self.assertTrue(hero_file.is_file())
            self.assertEqual(payload["modules"][0]["id"], "hero")
            self.assertEqual(payload["modules"][0]["body_chars"], len(plan.modules[0].body))
            self.assertIn("## Standard-Bild mit Textueberlagerung", copy_text)
            self.assertIn("970x600", copy_text)
            self.assertTrue(any(path.name == "modules.json" for path in written))


if __name__ == "__main__":
    unittest.main()
