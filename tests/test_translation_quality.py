from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from translate_chapter import TranslationQualityError, validate_translation_output  # noqa: E402


class TranslationQualityTests(unittest.TestCase):
    def test_prompt_echo_is_rejected(self) -> None:
        messages = [
            {"role": "system", "content": "Du bist ein literarischer Uebersetzer. Du uebersetzt aus der Ausgangssprache ins Deutsche."},
            {"role": "user", "content": "Uebersetze diesen langen Beispieltext ins Deutsche."},
        ]

        with self.assertRaises(TranslationQualityError):
            validate_translation_output(
                "## System\n\nDu bist ein literarischer Uebersetzer.\n\n## User\n\nUebersetze...",
                messages,
                label="test",
            )

    def test_system_prompt_echo_without_markdown_is_rejected(self) -> None:
        messages = [
            {"role": "system", "content": "Du bist ein literarischer Uebersetzer. Du uebersetzt aus der Ausgangssprache ins Deutsche."},
            {"role": "user", "content": "Uebersetze diesen langen Beispieltext ins Deutsche."},
        ]

        with self.assertRaises(TranslationQualityError):
            validate_translation_output(
                "Du bist ein literarischer Uebersetzer. Du uebersetzt aus der Ausgangssprache ins Deutsche.",
                messages,
                label="test",
            )

    def test_normal_translation_is_accepted(self) -> None:
        messages = [
            {"role": "system", "content": "Du bist ein Uebersetzer."},
            {"role": "user", "content": "Uebersetze diesen langen Beispieltext ins Deutsche."},
        ]

        validate_translation_output(
            "Der alte Mann trat in den Hof und blickte schweigend zum Himmel.",
            messages,
            label="test",
        )

    def test_legitimate_du_bist_ein_translation_is_accepted(self) -> None:
        messages = [
            {"role": "system", "content": "Du bist ein literarischer Uebersetzer. Du uebersetzt aus der Ausgangssprache ins Deutsche."},
            {"role": "user", "content": "Uebersetze diesen langen Beispieltext ins Deutsche."},
        ]

        validate_translation_output(
            "Du bist ein kluger Mann, sagte der Priester leise.",
            messages,
            label="test",
        )


if __name__ == "__main__":
    unittest.main()
