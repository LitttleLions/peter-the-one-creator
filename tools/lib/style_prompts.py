"""
style_prompts.py
================
Lädt config/style_modes.yaml und baut daraus die fertigen
System-/User-Messages für den OpenRouter-Aufruf.

Verwendung:
    from lib.style_prompts import StylePrompts

    sp = StylePrompts()
    messages = sp.build_messages(
        mode="stylized",
        book_cfg=book_dict,
        source_text=chapter_md_text,
        rules_text=rules_file_content,  # optional
    )
    # messages = [{"role": "system", "content": ...},
    #            {"role": "user", "content": ...}]
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_STYLE_MODES_PATH = REPO_ROOT / "config" / "style_modes.yaml"

VALID_MODES = ("literal", "middle", "stylized")


class StylePromptError(RuntimeError):
    """Wird bei Konfigurations- oder Prompt-Fehlern geworfen."""


class StylePrompts:
    def __init__(self, path: Path | str = DEFAULT_STYLE_MODES_PATH):
        self.path = Path(path)
        if not self.path.exists():
            raise StylePromptError(
                f"style_modes-Datei nicht gefunden: {self.path}"
            )
        data = yaml.safe_load(self.path.read_text(encoding="utf-8"))
        modes = data.get("modes") if isinstance(data, dict) else None
        if not isinstance(modes, dict):
            raise StylePromptError(
                f"Ungültige Struktur in {self.path}: 'modes' fehlt"
            )
        for m in VALID_MODES:
            if m not in modes:
                raise StylePromptError(
                    f"Stilmodus '{m}' fehlt in {self.path}"
                )
        self.modes = modes

    def get_mode(self, mode: str) -> dict:
        if mode not in self.modes:
            raise StylePromptError(
                f"Unbekannter Stilmodus: {mode!r}. "
                f"Erlaubt: {', '.join(VALID_MODES)}"
            )
        return self.modes[mode]

    def build_messages(
        self,
        mode: str,
        book_cfg: dict,
        source_text: str,
        rules_text: Optional[str] = None,
    ) -> list[dict]:
        """
        Baut die Messages-Liste für einen OpenRouter-Call.

        - mode       — "literal" | "middle" | "stylized"
        - book_cfg   — Dict aus config/books.yaml (für Titel,
                       Autor, Sprachen, Namenskonvention)
        - source_text — der zu übersetzende Text (Markdown oder plain)
        - rules_text — optionaler Inhalt der Regeln aus logic/.
                       Wird nur angehängt, wenn
                       self.get_mode(mode)["rules_append"] True ist.
        """
        m = self.get_mode(mode)

        # System-Prompt mit Buch-Kontext anreichern
        system = self._enrich_system_prompt(m["system_prompt"], book_cfg)

        # User-Prompt: Prefix + optionale Regeln + Source
        user_parts: list[str] = []
        user_parts.append(m.get("user_prompt_prefix", "").rstrip())
        user_parts.append("")
        user_parts.append(f"### Buch")
        user_parts.append(f"- Titel: {book_cfg.get('title', '?')}")
        user_parts.append(f"- Autor: {book_cfg.get('author', '?')}")
        user_parts.append(f"- Stilmodus: {mode}")
        nconv = book_cfg.get("naming_convention", {})
        if isinstance(nconv, dict) and nconv.get("style"):
            user_parts.append(
                f"- Namensschreibweise: {nconv['style']}"
            )
        if isinstance(nconv, dict) and nconv.get("example"):
            user_parts.append("- Beispiele:")
            for ex in nconv["example"]:
                user_parts.append(f"  - {ex}")
        user_parts.append("")
        if m.get("rules_append") and rules_text:
            user_parts.append("### Regelwerk (zur Referenz)")
            user_parts.append("")
            user_parts.append(rules_text.rstrip())
            user_parts.append("")
        user_parts.append("### Zu übersetzender Text")
        user_parts.append("")
        user_parts.append(source_text.rstrip())
        user = "\n".join(user_parts)

        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

    @staticmethod
    def _enrich_system_prompt(system: str, book_cfg: dict) -> str:
        """Fügt Buch-Metadaten in den System-Prompt ein, ohne
        die Anweisungen zu verdoppeln."""
        meta_lines = [
            "",
            "---",
            f"Buch: {book_cfg.get('title', '?')} "
            f"({book_cfg.get('author', '?')})",
            f"Sprache: {book_cfg.get('source_lang', '?')} → "
            f"{book_cfg.get('target_lang', '?')}",
        ]
        return system.rstrip() + "\n" + "\n".join(meta_lines)


# Kleine Helfer-Funktion für die Kommandozeile / Tests
def quick_estimate_tokens(text: str) -> int:
    """Sehr grobe Token-Schätzung: ~4 Zeichen pro Token
    (gilt für Deutsch und Russisch grob)."""
    return max(1, len(text) // 4)
