"""
style_prompts.py
================

Laedt bearbeitbare Style-Profile aus styles/*.md und baut daraus die
fertigen System-/User-Messages fuer OpenRouter oder Promptdateien.

Legacy-Fallback: config/style_modes.yaml mit literal/middle/stylized wird
weiterhin gelesen, damit alte Outputs und Kommandos nicht brechen. Neue
Laeufe sollen aber Style-Profile aus styles/ verwenden.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import yaml

from lib.name_registry import compact_name_lines, load_names

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_STYLE_MODES_PATH = REPO_ROOT / "config" / "style_modes.yaml"
DEFAULT_STYLE_PROFILES_DIR = REPO_ROOT / "styles"
LEGACY_MODES = ("literal", "middle", "stylized")


class StylePromptError(RuntimeError):
    """Wird bei Konfigurations- oder Prompt-Fehlern geworfen."""


def style_slug_from_path(path: Path) -> str:
    return path.stem.strip().lower()


def style_label_from_slug(slug: str) -> str:
    label = re.sub(r"^stil-(\d+)-", r"Stil \1 - ", slug)
    return label.replace("-", " ").strip().title()


def default_temperature(slug: str) -> float:
    if "original" in slug or "literal" in slug:
        return 0.2
    if "poetisch" in slug or "middle" in slug:
        return 0.35
    return 0.4


def available_style_profiles(
    profiles_dir: Path | str = DEFAULT_STYLE_PROFILES_DIR,
) -> list[dict]:
    root = Path(profiles_dir)
    if not root.exists():
        return []
    profiles = []
    for path in sorted(root.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        slug = style_slug_from_path(path)
        profiles.append({
            "id": slug,
            "label": style_label_from_slug(slug),
            "path": path,
        })
    return profiles


def available_style_ids(include_legacy: bool = True) -> list[str]:
    ids = [p["id"] for p in available_style_profiles()]
    if include_legacy:
        for legacy in LEGACY_MODES:
            if legacy not in ids:
                ids.append(legacy)
    return ids


class StylePrompts:
    def __init__(
        self,
        path: Path | str = DEFAULT_STYLE_MODES_PATH,
        profiles_dir: Path | str = DEFAULT_STYLE_PROFILES_DIR,
    ):
        self.path = Path(path)
        self.profiles_dir = Path(profiles_dir)
        self.modes: dict[str, dict] = {}
        self._load_profiles()
        self._load_legacy_modes()
        if not self.modes:
            raise StylePromptError(
                "Keine Style-Profile in styles/ und keine Legacy-Modi gefunden"
            )

    def _load_profiles(self) -> None:
        for profile in available_style_profiles(self.profiles_dir):
            path = Path(profile["path"])
            text = path.read_text(encoding="utf-8").strip()
            slug = profile["id"]
            try:
                profile_path = str(path.resolve().relative_to(REPO_ROOT.resolve()))
            except ValueError:
                profile_path = str(path)
            self.modes[slug] = {
                "label": profile["label"],
                "short": f"Style-Profil aus {path.name}",
                "rules_append": False,
                "temperature": default_temperature(slug),
                "profile_text": text,
                "profile_path": profile_path,
                "system_prompt": (
                    "Du bist ein literarischer Uebersetzer. Du uebersetzt "
                    "aus der Ausgangssprache ins Deutsche."
                ),
                "user_prompt_prefix": (
                    "Uebersetze den folgenden Text ins Deutsche."
                ),
            }

    def _load_legacy_modes(self) -> None:
        if not self.path.exists():
            return
        data = yaml.safe_load(self.path.read_text(encoding="utf-8"))
        modes = data.get("modes") if isinstance(data, dict) else None
        if not isinstance(modes, dict):
            return
        for mode in LEGACY_MODES:
            if mode in modes and mode not in self.modes:
                self.modes[mode] = modes[mode]

    def style_ids(self) -> list[str]:
        return list(self.modes.keys())

    def get_mode(self, mode: str) -> dict:
        if mode not in self.modes:
            raise StylePromptError(
                f"Unbekannter Stil: {mode!r}. "
                f"Erlaubt: {', '.join(self.style_ids())}"
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
        Baut die Messages-Liste fuer einen OpenRouter-Call.

        - mode: Style-Profil-Slug aus styles/ oder Legacy-Modus.
        - rules_text: nur fuer Legacy-Modi relevant. Style-Profile bringen
          ihren Regeltext selbst in profile_text mit.
        """
        m = self.get_mode(mode)
        system = self._build_system_prompt(m, mode, book_cfg)

        user_parts: list[str] = []
        user_parts.append(m.get("user_prompt_prefix", "").rstrip())
        user_parts.append("")
        user_parts.append("### Buch")
        user_parts.append(f"- Titel: {book_cfg.get('title', '?')}")
        user_parts.append(f"- Autor: {book_cfg.get('author', '?')}")
        user_parts.append(f"- Stil: {mode}")
        if m.get("profile_path"):
            user_parts.append(f"- Style-Profil: {m['profile_path']}")
            user_parts.append(
                "- Das Style-Profil steht im System-Prompt und ist verbindlich."
            )
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

        names_file = book_cfg.get("names_file")
        if names_file:
            name_lines = compact_name_lines(load_names(REPO_ROOT / names_file))
            if name_lines:
                user_parts.append("### Verbindliche Namen und Begriffe")
                user_parts.append("")
                user_parts.append(
                    "Nutze diese Schreibweisen, wenn die genannten Personen "
                    "oder Begriffe im Quelltext vorkommen. Nicht aufgefuehrte "
                    "russische Namen werden konservativ transliteriert oder "
                    "im Zweifel beibehalten."
                )
                user_parts.extend(name_lines)
                user_parts.append("")

        if m.get("rules_append") and rules_text:
            user_parts.append("### Regelwerk (zur Referenz)")
            user_parts.append("")
            user_parts.append(rules_text.rstrip())
            user_parts.append("")

        user_parts.append("### Zu uebersetzender Text")
        user_parts.append("")
        user_parts.append(source_text.rstrip())
        user_parts.append("")
        user_parts.append("### Ausgabe")
        user_parts.append(
            "Gib ausschliesslich die fertige deutsche Uebersetzung aus. "
            "Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine "
            "Formulierung wie 'Hier ist die Uebersetzung'."
        )
        user = "\n".join(user_parts)

        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

    @staticmethod
    def _build_system_prompt(mode_cfg: dict, mode: str, book_cfg: dict) -> str:
        system = mode_cfg["system_prompt"].rstrip()
        meta_lines = [
            "",
            "---",
            f"Buch: {book_cfg.get('title', '?')} "
            f"({book_cfg.get('author', '?')})",
            f"Sprache: {book_cfg.get('source_lang', '?')} -> "
            f"{book_cfg.get('target_lang', '?')}",
        ]
        parts = [system, "\n".join(meta_lines)]
        if mode_cfg.get("profile_text"):
            parts.extend([
                "",
                "### Verbindliches Style-Profil",
                "",
                (
                    "Dieses Profil ist die hoechstrangige Stilvorgabe fuer "
                    f"diesen Lauf ({mode}). Es hat Vorrang vor allgemeinen "
                    "Uebersetzungsgewohnheiten. Erzeuge eine Ausgabe, deren "
                    "Stil sichtbar und konsequent aus diesem Profil folgt. "
                    "Wenn das Profil ausdruecklich einen Vorabsatz, eine "
                    "Lede, eine Ueberschrift, einen Prolog oder eine andere "
                    "Struktur-Ergaenzung verlangt, setze diese Vorgabe um; "
                    "das gilt dann nicht als unerlaubtes Erfinden."
                ),
                "",
                mode_cfg["profile_text"].rstrip(),
            ])
        parts.extend([
            "",
            "### Harte Ausgabe-Regeln",
            "",
            (
                "Diese Regeln gelten nur, soweit das Style-Profil nichts "
                "ausdruecklich anderes verlangt."
            ),
            "",
            "- Gib nur die Uebersetzung aus.",
            "- Keine Vorbemerkung, keine Zusammenfassung, keine Analyse.",
            "- Keine Saetze wie 'Hier ist die Uebersetzung'.",
            (
                "- Keine Markdown-Ueberschriften erfinden, ausser sie stehen "
                "im Quelltext oder das Style-Profil verlangt sie."
            ),
            (
                "- Inhalt, Reihenfolge und Fakten des Quelltexts bleiben "
                "erhalten; explizit im Style-Profil verlangte Vorabsaetze "
                "oder Lede-Bloecke duerfen ergaenzt werden."
            ),
        ])
        return "\n".join(parts)


def quick_estimate_tokens(text: str) -> int:
    """Sehr grobe Token-Schaetzung: ~4 Zeichen pro Token."""
    return max(1, len(text) // 4)
