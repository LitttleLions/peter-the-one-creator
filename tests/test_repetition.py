"""Tests fuer tools/lib/repetition.py (Detektor, report-only).

Kalibrierungsziele (freigegeben):
- Beispiel 1 (Er-las-Anapher, 6x): max. INFO.
- Beispiel 2 (Chinqai-Absatz): min. ein WARNING.
- Kurze bewusste Dreier-Anapher: keine Meldung.
- Niemals ERROR (kein Gate-Effekt).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib import repetition as rep  # noqa: E402
from tests.repetition_fixtures import (  # noqa: E402
    EXAMPLE_ANAPHORA,
    EXAMPLE_CHINQAI,
    LITANY_OK,
    scene_path_008,
)


class RepetitionTests(unittest.TestCase):
    def test_anaphora_example_is_info_not_warning(self) -> None:
        out = rep.repetition_scene_findings("008", 1, EXAMPLE_ANAPHORA)

        ana = [f for f in out if f["message"].startswith("Anapher")]
        self.assertTrue(ana, "Er-las-Anapher (6x) muss erkannt werden")
        self.assertTrue(
            all(f["severity"] == "INFO" for f in ana),
            "6er-Anapher bleibt INFO (erst ab 7x WARNING)",
        )

    def test_three_line_anaphora_is_free(self) -> None:
        out = rep.repetition_scene_findings("001", 1, LITANY_OK)

        ana = [f for f in out if f["message"].startswith("Anapher")]
        self.assertEqual(ana, [])

    def test_chinqai_example_reaches_warning(self) -> None:
        out = rep.repetition_scene_findings("008", 1, EXAMPLE_CHINQAI)

        warns = [f for f in out if f["severity"] == "WARNING"]
        self.assertTrue(
            warns, "Chinqai-Absatz muss min. ein WARNING liefern"
        )
        cats = " | ".join(f["message"] for f in out)
        self.assertTrue(
            "Stapelung" in cats or "immer wieder" in cats
            or "Wort-Echo" in cats,
            f"WARNING muss Stapelung/Formel/Echo sein, got: {cats}",
        )

    def test_never_error(self) -> None:
        for text in (EXAMPLE_ANAPHORA, EXAMPLE_CHINQAI, LITANY_OK):
            for found in rep.repetition_scene_findings("008", 1, text):
                self.assertNotEqual(found["severity"], "ERROR")

    def test_short_scene_is_silent(self) -> None:
        out = rep.repetition_scene_findings(
            "001", 1, "## Szene 1\n\nKurzer Satz. Noch einer."
        )
        self.assertEqual(out, [])

    def test_chapter_008_flags_repetition(self) -> None:
        path = scene_path_008()
        if not path.exists():
            self.skipTest("Kapitel 008 fehlt lokal")
        text = path.read_text(encoding="utf-8")
        out = rep.repetition_scene_findings("008", 1, text)

        self.assertTrue(out, "Kap. 008 muss Befunde liefern")
        joined = " | ".join(f["message"] for f in out)
        self.assertTrue(
            "Anapher" in joined or "Stapelung" in joined
            or "Wort-Echo" in joined or "Leitmotiv" in joined,
            f"Kap. 008 muss Wiederholung melden, got: {joined}",
        )


if __name__ == "__main__":
    unittest.main()
