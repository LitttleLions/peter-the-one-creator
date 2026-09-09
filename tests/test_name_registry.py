from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib.name_registry import compact_name_lines  # noqa: E402


class NameRegistryTests(unittest.TestCase):
    def test_compact_name_lines_prompt_default_is_mapping_only(self) -> None:
        lines = compact_name_lines(
            [{
                "source": "Hö'elün",
                "target": "Höelün",
                "aliases": ["Höelun"],
                "status": "draft",
                "note": "alternativ Hö'elün; noch redaktionell festlegen",
            }]
        )
        self.assertEqual(lines, ["- Hö'elün -> Höelün"])

    def test_compact_name_lines_include_meta(self) -> None:
        lines = compact_name_lines(
            [{
                "source": "Jamuqa",
                "target": "Dschamucha",
                "aliases": ["Jamucha"],
                "status": "draft",
                "note": "gut aussprechbar",
            }],
            include_meta=True,
        )
        self.assertEqual(len(lines), 1)
        self.assertIn("Jamuqa -> Dschamucha", lines[0])
        self.assertIn("Alias: Jamucha", lines[0])
        self.assertIn("Status: draft", lines[0])
        self.assertIn("gut aussprechbar", lines[0])


if __name__ == "__main__":
    unittest.main()
