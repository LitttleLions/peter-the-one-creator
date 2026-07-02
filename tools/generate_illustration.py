"""
generate_illustration.py
========================

Erzeugt Szenen- oder Kapitelillustrationen via Higgsfield und legt sie in der
bestehenden Export-Konvention des Buchpakets ab.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).parent))

from lib.book_project import find_book as find_book_project
from lib.output_paths import (
    book_output_root,
    de_scene_path,
    source_chapter_path,
    source_scene_path,
)
from lib.name_registry import load_names
from PIL import Image


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = "text2image_soul_v2"
DEFAULT_MOODBOARD = "https://higgsfield.ai/s/R0FemgKUPW4"
DEFAULT_ASPECT_RATIO = "3:4"
DEFAULT_QUALITY = "1.5k"
DEFAULT_IMAGE_PROCESSING: dict[str, Any] = {
    "format": "JPEG",
    "jpeg_quality": 95,
    "max_width": None,
    "max_height": None,
}
DEFAULT_OUTPUT_EXT = ".jpg"
UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
ASPECT_RATIO_RE = re.compile(r"^\d+(?:\.\d+)?:\d+(?:\.\d+)?$")

# NOTE: text2image_soul_v2 hat KEINEN negative_prompt-Parameter.
# Alle Negativ-Formulierungen ("no X") werden als positive Anweisung
# gelesen. Deshalb nur positive Beschreibungen im illustration_setting
# pro Buch (book.yaml).


@dataclass(frozen=True)
class IllustrationRequest:
    book_id: str
    chapter_id: str
    scene_number: int | None
    style: str
    kind: str
    model: str
    moodboard: str
    images: tuple[str, ...]
    no_reference: bool
    aspect_ratio: str
    quality: str
    overwrite: bool
    backend: str = "auto"
    moodboard_name: str | None = None
    moodboard_strength: float = 1.0
    soul_id: str | None = None
    soul_strength: float = 1.0
    allow_paid_generation: bool = False


def normalize_chapter_id(value: str) -> str:
    value = value.strip()
    if not value.isdigit():
        raise SystemExit(f"Kapitel muss numerisch sein: {value!r}")
    return f"{int(value):03d}"


def normalize_scene_number(value: str | None, kind: str) -> int | None:
    if kind == "chapter":
        return None
    if value is None:
        raise SystemExit("--scene ist fuer --kind scene erforderlich")
    value = value.strip()
    if not value.isdigit():
        raise SystemExit(f"Szene muss numerisch sein: {value!r}")
    return int(value)


def normalize_aspect_ratio(value: str) -> str:
    text = str(value or "").strip().replace(";", ":").replace("：", ":")
    text = re.sub(r"\s*:\s*", ":", text)
    if not ASPECT_RATIO_RE.match(text):
        raise SystemExit(
            f"Ungueltiges Seitenverhaeltnis: {value!r}. Erwartet z. B. 3:4 oder 16:9."
        )
    return text


def output_ext_for_format(fmt: str) -> str:
    fmt_upper = fmt.strip().upper()
    if fmt_upper == "PNG":
        return ".png"
    if fmt_upper == "JPEG":
        return ".jpg"
    return DEFAULT_OUTPUT_EXT


def output_image_path(book: dict[str, Any], request: IllustrationRequest,
                      image_processing: dict[str, Any] | None = None) -> Path:
    book_root = REPO_ROOT / str(book["book_root"])
    assets_root = book_root / "assets"
    ext = output_ext_for_format(
        (image_processing or {}).get("format", "JPEG")
    )
    if request.kind == "chapter":
        return assets_root / "chapter" / f"chapter-{request.chapter_id}{ext}"
    if request.scene_number is None:
        raise SystemExit("--scene ist fuer Szenenbilder erforderlich")
    return (
        assets_root
        / "scene"
        / request.chapter_id
        / f"scene-{request.scene_number:03d}{ext}"
    )


def prompt_stem(request: IllustrationRequest) -> str:
    if request.kind == "chapter":
        return f"{request.chapter_id}-chapter-{request.style}"
    scene = request.scene_number or 0
    return f"{request.chapter_id}-scene-{scene:02d}-{request.style}"


def prompt_paths(book: dict[str, Any], request: IllustrationRequest) -> tuple[Path, Path]:
    output_root = book_output_root(REPO_ROOT, book)
    prompt_dir = output_root / "prompts" / "higgsfield"
    stem = prompt_stem(request)
    return prompt_dir / f"{stem}.md", prompt_dir / f"{stem}.json"


def preferred_scene_path(book: dict[str, Any], request: IllustrationRequest) -> Path:
    if request.scene_number is None:
        return source_chapter_path(book_output_root(REPO_ROOT, book), request.chapter_id)
    output_root = book_output_root(REPO_ROOT, book)
    de_path = de_scene_path(
        output_root,
        request.chapter_id,
        request.scene_number,
        request.style,
    )
    if de_path.exists():
        return de_path
    return source_scene_path(
        output_root,
        request.chapter_id,
        request.scene_number,
        str(book.get("source_lang") or "ru"),
    )


def read_scene_text(book: dict[str, Any], request: IllustrationRequest) -> tuple[Path, str]:
    path = preferred_scene_path(book, request)
    if not path.exists():
        raise SystemExit(f"Quelldatei nicht gefunden: {path}")
    return path, path.read_text(encoding="utf-8")


# Zeilen, die wie poetische Motti, Zitate oder Szenen-Metadaten aussehen.
# Sie verleiten Higgsfield dazu, Text im Bild zu rendern.
_MOTTO_PATTERNS = [
    r'^\s*##\s+Szene\s+\d+',        # "## Szene 1"
    r'^\s*»',                         # Mottos im Guillemet-Stil
    r'^\s*«',                         # ...
    r'^\s*[„"][^"]{0,120}[„"]',      # Kurze Zitat-Zeilen (max ~120 Zeichen)
    r'^\s*[*_]*—\s+',                 # "— Aus den Lehren ..."
    r'^\s*>',                         # Markdown-Blockzitate
]
_MOTTO_RE = re.compile("|".join(_MOTTO_PATTERNS))
_BOOK_STATUS_HEADER_RE = re.compile(
    r'^\s*[*_]*Buch:\s+.*?<!--\s*status:[^>]*-->\s*'
)
_BOOK_TITLE_HEADER_RE = re.compile(r'^\s*[*_]*Buch:\s+.*?[*_]*\s*$')
_STATUS_COMMENT_RE = re.compile(r'^\s*<!--\s*status:[^>]*-->\s*$')


_MAX_PARAGRAPHS = 6


def clean_markdown_excerpt(text: str, limit: int = 2000) -> str:
    # Erst alle irrelevanten Zeilen herausfiltern
    filtered_lines: list[str] = []
    in_motto_block = False
    for raw in text.splitlines():
        line = _BOOK_STATUS_HEADER_RE.sub("", raw.strip())
        if _BOOK_TITLE_HEADER_RE.match(line) or _STATUS_COMMENT_RE.match(line):
            in_motto_block = False
            continue
        if not line:
            filtered_lines.append("")
            in_motto_block = False
            continue
        if line.startswith("#"):
            in_motto_block = line.startswith("##")
            continue
        if line.startswith(">"):
            in_motto_block = True
            continue
        if in_motto_block and (line.startswith(">") or line.startswith("—") or
                               re.match(r'^\s*[*_]{1,2}', line)):
            continue
        if _MOTTO_RE.match(line):
            in_motto_block = True
            continue
        in_motto_block = False
        filtered_lines.append(line)
    # Absaetze aus aufeinanderfolgenden Nicht-Leerzeilen bauen
    paragraphs: list[str] = []
    current: list[str] = []
    for line in filtered_lines:
        if line:
            current.append(line)
        else:
            if current:
                paragraphs.append(" ".join(current))
                current = []
    if current:
        paragraphs.append(" ".join(current))
    paragraphs = [re.sub(r"\s+", " ", p).strip() for p in paragraphs if p.strip()]
    selected = paragraphs[:_MAX_PARAGRAPHS]
    compact = " ".join(selected)
    if len(compact) <= limit:
        return compact
    return compact[:limit].rsplit(" ", 1)[0].rstrip(".,;:") + "..."


def load_illustration_setting(book: dict[str, Any]) -> str:
    """Load the user-editable illustration_setting from book.yaml.
    
    Newlines aus YAML-Block-Scalar werden durch Spaces ersetzt,
    damit der Prompt single-line bleibt (Higgsfield-CLI-Limitierung).
    """
    setting = str(book.get("illustration_setting") or "").strip()
    return re.sub(r"\s+", " ", setting)


def _name_match(text: str, name: str) -> bool:
    value = str(name or "").strip()
    if not value:
        return False
    if len(value) <= 2:
        return value in text
    pattern = rf"(?<![\w-]){re.escape(value)}(?![\w-])"
    return re.search(pattern, text, flags=re.IGNORECASE | re.UNICODE) is not None


def character_visual_lines(book: dict[str, Any], source_text: str, limit: int = 3) -> list[str]:
    names_file = book.get("names_file")
    if not names_file:
        return []
    names_path = REPO_ROOT / str(names_file)
    entries = load_names(names_path)
    lines: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        if str(entry.get("type") or "person").strip() != "person":
            continue
        visual = re.sub(r"\s+", " ", str(entry.get("visual") or "").strip())
        if not visual:
            continue
        candidates = [
            entry.get("source"),
            entry.get("target"),
            *(entry.get("aliases") or []),
        ]
        if not any(_name_match(source_text, str(candidate)) for candidate in candidates):
            continue
        label = str(entry.get("target") or entry.get("source") or "").strip()
        if not label or label in seen:
            continue
        seen.add(label)
        lines.append(f"{label}: {visual}")
        if len(lines) >= limit:
            break
    return lines


def build_prompt(book: dict[str, Any], request: IllustrationRequest, source_text: str) -> str:
    """Build a concise Higgsfield prompt with only positive descriptions.

    The model text2image_soul_v2 has NO negative_prompt parameter.
    All "no X" formulations are read as positive instructions and produce
    exactly what we want to avoid. Therefore the prompt consists only of:
    1. illustration_setting from book.yaml (period, location, style)
    2. The cleaned scene excerpt (atmosphere, not literal depiction)

    Single-line only – Higgsfield CLI kann mehrzeilige --prompt-Werte
    nicht korrekt verarbeiten.
    """
    setting = load_illustration_setting(book)
    excerpt = clean_markdown_excerpt(source_text)
    character_lines = character_visual_lines(book, source_text)
    character_text = ""
    if character_lines:
        character_text = "Characters present: " + "; ".join(character_lines) + "."
    parts = [part for part in (setting, character_text, excerpt) if part]
    return re.sub(r"\s+", " ", " ".join(parts))


def run_json_command(cmd: list[str]) -> Any:
    completed = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        raise SystemExit(f"Befehl fehlgeschlagen: {' '.join(cmd)}\n{stderr}")
    text = completed.stdout.strip()
    if not text:
        return None
    # Zunaechst ganz normal als JSON parsen (Objekte oder Arrays).
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Higgsfield CLI gibt manchmal ein JSON-ARRAY mit Statuszeilen (UUID)
    # davor zurueck. raw_decode ab der ersten '['-Position.
    idx = text.find("[")
    if idx >= 0:
        try:
            return json.JSONDecoder().raw_decode(text, idx)[0]
        except json.JSONDecodeError:
            pass
    raise SystemExit(
        f"Keine JSON-Ausgabe von {' '.join(cmd)}: {text[:1000]}"
    )


def is_uuid(value: str) -> bool:
    return bool(UUID_RE.match(value.strip()))


def is_url(value: str) -> bool:
    return value.strip().lower().startswith(("http://", "https://"))


def higgsfield_defaults(book: dict[str, Any]) -> dict[str, Any]:
    cfg = book.get("higgsfield") or {}
    moodboard = cfg.get("moodboard") if isinstance(cfg, dict) else None
    moodboard_name = None
    moodboard_strength = 1.0
    moodboard_availability = "web_ui_only"
    if isinstance(moodboard, dict):
        moodboard_value = (
            moodboard.get("web_ui_moodboard_id")
            or moodboard.get("style_id")
        )
        moodboard_name = moodboard.get("name")
        moodboard_strength = float(moodboard.get("strength", 1.0))
        moodboard_availability = str(
            moodboard.get("availability") or "web_ui_only"
        )
    else:
        moodboard_value = None
    soul = cfg.get("soul") if isinstance(cfg, dict) else None
    soul_enabled = bool(soul.get("enabled")) if isinstance(soul, dict) else False
    soul_id = soul.get("id") if isinstance(soul, dict) and soul_enabled else None
    soul_strength = (
        float(soul.get("strength", 1.0))
        if isinstance(soul, dict) and soul_enabled
        else 1.0
    )
    return {
        "model": (
            str(cfg.get("model") or DEFAULT_MODEL)
            if isinstance(cfg, dict)
            else DEFAULT_MODEL
        ),
        "moodboard": str(moodboard_value or DEFAULT_MOODBOARD),
        "moodboard_name": str(moodboard_name) if moodboard_name else None,
        "moodboard_strength": moodboard_strength,
        "moodboard_availability": moodboard_availability,
        "soul_id": str(soul_id) if soul_id else None,
        "soul_strength": soul_strength,
        "reference_images": tuple(
            str(item)
            for item in (
                cfg.get("reference_images") if isinstance(cfg, dict) else []
            )
            or []
        ),
        "backend": (
            str(cfg.get("backend") or "auto")
            if isinstance(cfg, dict)
            else "auto"
        ),
        "aspect_ratio": (
            str(cfg.get("aspect_ratio") or DEFAULT_ASPECT_RATIO)
            if isinstance(cfg, dict)
            else DEFAULT_ASPECT_RATIO
        ),
        "quality": (
            str(cfg.get("quality") or DEFAULT_QUALITY)
            if isinstance(cfg, dict)
            else DEFAULT_QUALITY
        ),
    }


def iter_param_names(value: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            lowered = str(key).lower()
            if lowered in {"name", "key", "id", "slug"} and isinstance(item, str):
                names.add(item)
            elif any(token in lowered for token in ("moodboard", "preset", "style")):
                names.add(str(key))
            names.update(iter_param_names(item))
    elif isinstance(value, list):
        for item in value:
            names.update(iter_param_names(item))
    return names


# --- Moodboard-/Stil-Parameter-Erkennung ---
#
# Die Higgsfield-CLI exponiert fuer text2image_soul_v2 derzeit kein style_id.
# Korrekte Moodboard-/Style-Laeufe in der Higgsfield-History setzen aber
# params.style_id. custom_reference_id erzeugt dagegen General + Character/
# Soul-Referenz und ist fuer Moodboards der falsche Kanal.
#
# Kandidaten-Liste priorisiert echte Stil-/Moodboard-Parameter vor
# custom_reference_id. Letztere wird nur diagnostisch erkannt und fuer
# Moodboards abgelehnt.

_MOODBOARD_STYLE_CANDIDATES = [
    "style_id",
    "moodboard_id",
    "moodboard",
    "moodboard_url",
    "preset_id",
    "preset",
    "style",
]
_SOUL_REFERENCE_CANDIDATE = "custom_reference_id"


def normalize_param_name(value: str) -> str:
    return value.replace("-", "_").lower()


def moodboard_flag_from_schema(schema: Any) -> str | None:
    """Findet den ersten Moodboard-/Stil-Parameter im CLI-Modellschema.

    Durchsucht das Schema rekursiv nach Parameternamen. Gibt das
    passende CLI-Flag zurueck (z. B. ``--style_id``) oder None.
    ``custom_reference_id`` wird NUR zurueckgegeben, wenn kein
    echter Stil-Parameter gefunden wurde, und wird vom Aufrufer
    (validate_moodboard_support) gesondert behandelt.
    """
    names = {normalize_param_name(name): name for name in iter_param_names(schema)}

    # Zuerst echte Stil-/Moodboard-Parameter suchen
    for candidate in _MOODBOARD_STYLE_CANDIDATES:
        if candidate in names:
            return "--" + names[candidate]

    # Fallback: custom_reference_id (wird vom Aufrufer geprueft)
    if _SOUL_REFERENCE_CANDIDATE in names:
        return "--" + names[_SOUL_REFERENCE_CANDIDATE]

    return None


def _flag_is_soul_reference(flag: str) -> bool:
    """Prueft, ob das Flag auf custom_reference_id verweist."""
    return normalize_param_name(flag.lstrip("-")) == _SOUL_REFERENCE_CANDIDATE


def classify_higgsfield_schema(schema: Any) -> dict[str, Any]:
    """Klassifiziert, ob das Schema echte Moodboard-/Style-Parameter anbietet."""
    raw_names = sorted(iter_param_names(schema))
    names = {normalize_param_name(name): name for name in raw_names}
    style_candidates = [
        candidate for candidate in _MOODBOARD_STYLE_CANDIDATES if candidate in names
    ]
    has_custom_reference = _SOUL_REFERENCE_CANDIDATE in names
    flag = moodboard_flag_from_schema(schema)
    uses_custom_reference_fallback = bool(flag and _flag_is_soul_reference(flag))
    can_use_moodboard = bool(flag and not uses_custom_reference_fallback)
    return {
        "params": raw_names,
        "style_candidates": style_candidates,
        "has_custom_reference_id": has_custom_reference,
        "selected_flag": flag,
        "can_use_moodboard": can_use_moodboard,
        "uses_custom_reference_fallback": uses_custom_reference_fallback,
        "only_custom_reference": bool(
            has_custom_reference and not style_candidates
        ),
    }


def diagnose_higgsfield_reference(model: str, moodboard: str) -> dict[str, Any]:
    """Prueft die lokale Higgsfield-CLI ohne Bildgenerierung."""
    executable = higgsfield_executable()
    diagnostic: dict[str, Any] = {
        "model": model,
        "moodboard": moodboard,
        "programmatic_support": "no" if is_uuid(moodboard) else "not_applicable",
        "reason": (
            "Higgsfield bestaetigt: Web-UI-Moodboards werden nicht ueber "
            "API, CLI oder MCP exponiert."
            if is_uuid(moodboard)
            else None
        ),
        "fallback": (
            "reference-image workflow only"
            if is_uuid(moodboard)
            else "CLI/API ohne Web-UI-Moodboard"
        ),
        "executable": executable,
        "schema_checked": False,
        "no_generation": True,
    }
    if is_uuid(moodboard):
        diagnostic.update(
            {
                "can_use_moodboard": False,
                "status": "web_ui_moodboard_only",
                "recommendation": (
                    "Moodboard-ID nur als Web-UI-Metadatum behalten. Fuer "
                    "Automation --no-reference, echte Soul-ID oder "
                    "reference_images/--image verwenden."
                ),
            }
        )
        return diagnostic
    if executable is None:
        diagnostic.update(
            {
                "can_use_moodboard": False,
                "status": "cli_missing",
                "recommendation": (
                    "higgsfield CLI installieren oder PATH pruefen: "
                    "npm install -g @higgsfield/cli"
                ),
            }
        )
        return diagnostic

    schema = run_json_command([executable, "model", "get", model, "--json"])
    classification = classify_higgsfield_schema(schema)
    diagnostic.update(classification)
    diagnostic["schema_checked"] = True
    if classification["only_custom_reference"]:
        diagnostic["status"] = "only_custom_reference_id"
        diagnostic["recommendation"] = (
            "Nicht automatisch ueber die CLI generieren: Korrekte "
            "Moodboard-Laeufe setzen params.style_id. Die CLI bietet hier "
            "nur --custom_reference_id; das erzeugt General + Character/"
            "Soul-Referenz und ist fuer Moodboards falsch. Private Web-UI-"
            "Moodboards sind laut Higgsfield nicht programmatisch nutzbar."
        )
    elif classification["can_use_moodboard"]:
        diagnostic["status"] = "moodboard_supported"
        diagnostic["recommendation"] = (
            f"Moodboard kann mit {classification['selected_flag']} uebergeben werden."
        )
    else:
        diagnostic["status"] = "no_moodboard_parameter"
        diagnostic["recommendation"] = (
            "Kein Moodboard-/Style-Parameter im CLI-Schema gefunden. "
            "Fuer private Web-UI-Moodboards ist das laut Higgsfield eine "
            "Produktgrenze; nutze Web-UI oder reference_images."
        )
    return diagnostic


def print_higgsfield_diagnostic(diagnostic: dict[str, Any]) -> None:
    """Menschenlesbare Diagnose plus JSON fuer Nachvollziehbarkeit."""
    print("=== Higgsfield Moodboard-Diagnose ===")
    print(f"Modell: {diagnostic.get('model')}")
    print(f"Moodboard/Style-UUID: {diagnostic.get('moodboard')}")
    executable = diagnostic.get("executable")
    print(f"CLI: {executable or 'nicht gefunden'}")
    print(f"Schema geprueft: {diagnostic.get('schema_checked')}")
    print(f"Status: {diagnostic.get('status')}")
    if diagnostic.get("programmatic_support"):
        print(f"Programmatic support: {diagnostic.get('programmatic_support')}")
    if diagnostic.get("reason"):
        print(f"Grund: {diagnostic.get('reason')}")
    if diagnostic.get("fallback"):
        print(f"Fallback: {diagnostic.get('fallback')}")
    if diagnostic.get("selected_flag"):
        label = (
            "Ausgewaehltes Moodboard-Flag"
            if diagnostic.get("can_use_moodboard")
            else "Nicht nutzbares Referenz-Flag"
        )
        print(f"{label}: {diagnostic.get('selected_flag')}")
    params = diagnostic.get("params") or []
    if params:
        print("Gefundene Parameter: " + ", ".join(params))
    print(f"Empfehlung: {diagnostic.get('recommendation')}")
    print("\nJSON:")
    print(json.dumps(diagnostic, ensure_ascii=False, indent=2))


def higgsfield_available() -> bool:
    return higgsfield_executable() is not None


def higgsfield_executable() -> str | None:
    for name in ("higgsfield.cmd", "higgsfield.exe", "higgsfield"):
        if found := shutil.which(name):
            return found
    return None


def validate_moodboard_support(model: str) -> tuple[str, Any]:
    """Validiert, dass das Higgsfield-Modell einen Referenzparameter anbietet."""
    executable = higgsfield_executable()
    if executable is None:
        raise SystemExit(
            "higgsfield CLI nicht gefunden. Installation unter Windows: "
            "npm install -g @higgsfield/cli"
        )
    schema = run_json_command([executable, "model", "get", model, "--json"])
    flag = moodboard_flag_from_schema(schema)
    if not flag:
        raise SystemExit(
            "Das Higgsfield-Modellschema enthaelt keinen Moodboard-/Preset-/Style-"
            "Parameter. Prompt und Metadaten wurden geschrieben; bitte CLI/UI "
            "pruefen, bevor automatisch generiert wird."
        )
    if _flag_is_soul_reference(flag):
        raise SystemExit(
            "Die aktuelle Higgsfield-CLI kann Moodboard-/Style-UUIDs fuer "
            f"'{model}' nicht korrekt uebergeben. Das Schema bietet nur "
            "``--custom_reference_id``; korrekte Higgsfield-History-Laeufe "
            "setzen aber ``params.style_id``. Automatische CLI-Generierung "
            "wurde abgebrochen, damit die Moodboard-UUID nicht als Character/"
            "Soul-Referenz verwendet wird.\n\n"
            "Optionen:\n"
            "  - Im Higgsfield Web-UI mit Moodboard generieren\n"
            "  - Bewusst getrennte reference_images/--image verwenden\n"
            "  - Bewusst ohne Moodboard mit --no-reference generieren\n\n"
            "Prompt und Metadaten wurden geschrieben."
        )
    return flag, schema


def validate_higgsfield_available() -> None:
    if higgsfield_executable() is None:
        raise SystemExit(
            "higgsfield CLI nicht gefunden. Installation unter Windows: "
            "npm install -g @higgsfield/cli"
        )


def normalize_backend(value: str) -> str:
    backend = value.strip().lower()
    if backend not in {"cli", "api", "auto"}:
        raise SystemExit(f"Unbekanntes Higgsfield-Backend: {value!r}")
    return backend


def has_moodboard(request: IllustrationRequest) -> bool:
    return bool(is_uuid(request.moodboard) and not request.no_reference)


def has_programmatic_reference(request: IllustrationRequest) -> bool:
    return bool(request.no_reference or request.images or request.soul_id)


def selected_backend(request: IllustrationRequest) -> str:
    backend = normalize_backend(request.backend)
    if backend == "auto":
        return "cli"
    return backend


def higgsfield_api_adapter_path() -> Path:
    return REPO_ROOT / "tools" / "higgsfield_api_adapter.mjs"


def run_higgsfield_api_adapter(payload: dict[str, Any]) -> dict[str, Any]:
    completed = subprocess.run(
        ["node", str(higgsfield_api_adapter_path())],
        input=json.dumps(payload, ensure_ascii=False),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    text = completed.stdout.strip()
    try:
        data = json.loads(text) if text else {}
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"Higgsfield-API-Adapter lieferte kein JSON: {exc}\n"
            f"stderr: {completed.stderr.strip()}"
        )
    if completed.returncode != 0 or not data.get("ok", False):
        code = data.get("error_code") or "HIGGSFIELD_API_ERROR"
        message = data.get("message") or completed.stderr.strip()
        raise SystemExit(f"{code}: {message}")
    return data


def list_higgsfield_api_styles() -> list[dict[str, Any]]:
    data = run_higgsfield_api_adapter({"action": "list_styles"})
    styles = data.get("styles") or []
    if not isinstance(styles, list):
        raise SystemExit("HIGGSFIELD_API_BAD_RESPONSE: styles ist keine Liste")
    return styles


def discover_higgsfield_style(style_id: str) -> dict[str, Any] | None:
    for style in list_higgsfield_api_styles():
        if style.get("id") == style_id:
            return style
    return None


def build_higgsfield_api_payload(
    request: IllustrationRequest,
    prompt: str,
    dry_run: bool,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "action": "generate",
        "prompt": prompt,
        "style_id": None,
        "style_strength": None,
        "soul_id": request.soul_id,
        "soul_strength": request.soul_strength,
        "aspect_ratio": request.aspect_ratio,
        "quality": request.quality,
        "batch_size": 1,
        "dry_run": dry_run,
    }
    return payload


def verification_status(
    response: Any,
    requested_style_id: str | None,
    requested_soul_id: str | None,
) -> str:
    if not isinstance(response, dict):
        return "unverified"
    text = json.dumps(response, ensure_ascii=False)
    if requested_style_id and f'"style_id": "{requested_style_id}"' not in text:
        return "unverified"
    if requested_soul_id and f'"custom_reference_id": "{requested_soul_id}"' not in text:
        return "unverified"
    if requested_style_id or requested_soul_id:
        return "verified"
    return "unverified"


def build_higgsfield_command(
    request: IllustrationRequest,
    prompt: str,
    moodboard_flag: str | None,
) -> list[str]:
    executable = higgsfield_executable() or "higgsfield"
    command = [
        executable,
        "generate",
        "create",
        request.model,
        "--prompt",
        prompt,
        "--aspect_ratio",
        request.aspect_ratio,
        "--quality",
        request.quality,
    ]
    if request.soul_id:
        command.extend(["--custom_reference_id", request.soul_id])
    for image in request.images:
        command.extend(["--image", image])
    command.extend(["--wait", "--json"])
    return command


def ensure_reference_inputs(request: IllustrationRequest) -> None:
    if request.no_reference:
        return
    if request.soul_id or request.images:
        return
    if is_url(request.moodboard):
        raise SystemExit(
            "Der Moodboard-Share-Link ist keine CLI-Referenz-UUID. Bitte eine "
            "Moodboard-/Custom-Reference-UUID mit --moodboard <uuid> oder "
            "Referenzbilder mit --image <uuid|pfad> uebergeben. Der Share-Link "
            "bleibt nur in den Metadaten dokumentiert."
        )
    raise SystemExit(
        "Keine gueltige Higgsfield-Referenz angegeben. Erwartet wird "
        "--no-reference, --soul-id oder mindestens ein --image <uuid|pfad>."
    )


def find_first_url(value: Any) -> str | None:
    if isinstance(value, str):
        match = re.search(r"https?://[^\s\"'<>]+", value)
        return match.group(0) if match else None
    if isinstance(value, dict):
        preferred_keys = [
            "url",
            "image_url",
            "media_url",
            "download_url",
            "asset_url",
            "result_url",
        ]
        for key in preferred_keys:
            if key in value:
                found = find_first_url(value[key])
                if found:
                    return found
        for item in value.values():
            found = find_first_url(item)
            if found:
                return found
    if isinstance(value, list):
        for item in value:
            found = find_first_url(item)
            if found:
                return found
    return None


def load_image_processing(book: dict[str, Any]) -> dict[str, Any]:
    """Merge book.yaml higgsfield.image_processing with defaults."""
    cfg: dict[str, Any] = dict(DEFAULT_IMAGE_PROCESSING)
    hf = book.get("higgsfield") or {}
    if not isinstance(hf, dict):
        return cfg
    ip = hf.get("image_processing")
    if not isinstance(ip, dict):
        return cfg
    for key in ("format", "jpeg_quality", "max_width", "max_height"):
        if key in ip:
            cfg[key] = ip[key]
    return cfg


def _resize_image(image: Image.Image, image_processing: dict[str, Any]) -> Image.Image:
    max_w = image_processing.get("max_width")
    max_h = image_processing.get("max_height")
    if not max_w and not max_h:
        return image
    orig_w, orig_h = image.size
    target_w = int(max_w) if max_w else orig_w
    target_h = int(max_h) if max_h else orig_h
    if orig_w <= target_w and orig_h <= target_h:
        return image
    image.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
    return image


def download_url(url: str, destination: Path,
                 image_processing: dict[str, Any] | None = None) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    http_request = urllib.request.Request(
        url,
        headers={"User-Agent": "peter-the-one-creator/illustration-tool"},
    )
    with urllib.request.urlopen(http_request, timeout=120) as response:
        data = response.read()
    ip = image_processing or DEFAULT_IMAGE_PROCESSING
    fmt = str(ip.get("format", "JPEG")).strip().upper()
    if fmt == "PNG":
        with Image.open(BytesIO(data)) as image:
            image = _resize_image(image, ip)
            image.save(destination, format="PNG")
    elif fmt == "KEEP":
        with Image.open(BytesIO(data)) as image:
            image = _resize_image(image, ip)
            if image.format == "PNG":
                image.save(destination, format="PNG")
            else:
                image = image.convert("RGB")
                image.save(destination, format="JPEG", quality=int(ip.get("jpeg_quality", 95)))
    else:
        with Image.open(BytesIO(data)) as image:
            image = _resize_image(image, ip)
            image = image.convert("RGB")
            image.save(destination, format="JPEG",
                       quality=int(ip.get("jpeg_quality", 95)))


def write_prompt_files(
    book: dict[str, Any],
    request: IllustrationRequest,
    source_path: Path,
    prompt: str,
    command: list[str],
    image_path: Path,
    dry_run: bool,
    schema_checked: bool,
    job_result: Any | None = None,
    media_url: str | None = None,
    api_metadata: dict[str, Any] | None = None,
) -> tuple[Path, Path]:
    prompt_md, meta_json = prompt_paths(book, request)
    prompt_md.parent.mkdir(parents=True, exist_ok=True)
    prompt_md.write_text(prompt + "\n", encoding="utf-8")
    meta = {
        "book": request.book_id,
        "chapter": request.chapter_id,
        "scene": request.scene_number,
        "kind": request.kind,
        "style": request.style,
        "model": request.model,
        "moodboard": request.moodboard,
        "images": list(request.images),
        "no_reference": request.no_reference,
        "aspect_ratio": request.aspect_ratio,
        "quality": request.quality,
        "source_path": str(source_path),
        "prompt_path": str(prompt_md),
        "output_path": str(image_path),
        "dry_run": dry_run,
        "schema_checked": schema_checked,
        "command": command,
        "media_url": media_url,
        "job_result": job_result,
    }
    if api_metadata:
        meta.update(api_metadata)
    meta_json.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return prompt_md, meta_json


def generate_illustration(
    request: IllustrationRequest,
    dry_run: bool = False,
) -> tuple[Path, Path, Path]:
    book = find_book_project(REPO_ROOT, request.book_id)
    image_processing = load_image_processing(book)
    image_path = output_image_path(book, request, image_processing)
    if image_path.exists() and not request.overwrite:
        raise SystemExit(f"Zielbild existiert bereits: {image_path}")

    source_path, source_text = read_scene_text(book, request)
    prompt = build_prompt(book, request, source_text)
    backend = selected_backend(request)
    planned_command = (
        ["node", str(higgsfield_api_adapter_path())]
        if backend == "api"
        else [
            "higgsfield",
            "generate",
            "create",
            request.model,
            "--prompt",
            prompt,
            "--aspect_ratio",
            request.aspect_ratio,
            "--quality",
            request.quality,
            "--wait",
            "--json",
        ]
    )
    api_metadata: dict[str, Any] = {}

    if has_moodboard(request) and not has_programmatic_reference(request):
        write_prompt_files(
            book,
            request,
            source_path,
            prompt,
            planned_command,
            image_path,
            dry_run=dry_run,
            schema_checked=False,
            api_metadata={
                "web_ui_moodboard_id": request.moodboard,
                "web_ui_moodboard_name": request.moodboard_name,
                "programmatic_support": "no",
                "programmatic_support_reason": (
                    "Higgsfield bestaetigt: Web-UI-Moodboards werden nicht "
                    "ueber API, CLI oder MCP exponiert."
                ),
                "fallback": "reference-image workflow only",
            },
        )
        raise SystemExit(
            "HIGGSFIELD_WEB_UI_MOODBOARD_NOT_PROGRAMMATIC: "
            "Web-UI-Moodboards sind laut Higgsfield nicht per API, CLI oder "
            "MCP nutzbar. Nutze --no-reference, --soul-id oder --image/"
            "reference_images."
        )

    if backend == "api":
        if request.images:
            raise SystemExit(
                "HIGGSFIELD_API_REFERENCE_IMAGES_NOT_IMPLEMENTED: "
                "Referenzbilder sind in diesem Tool derzeit ueber die CLI "
                "unterstuetzt. Nutze --backend cli."
            )
        api_metadata = {
            "generator_backend": "higgsfield_api_v1",
            "web_ui_moodboard_id": request.moodboard if is_uuid(request.moodboard) else None,
            "web_ui_moodboard_name": request.moodboard_name,
            "programmatic_support": (
                "no" if is_uuid(request.moodboard) else "not_applicable"
            ),
            "programmatic_support_reason": (
                "Higgsfield bestaetigt: Web-UI-Moodboards werden nicht ueber "
                "API, CLI oder MCP exponiert."
                if is_uuid(request.moodboard)
                else None
            ),
            "requested_style_id": None,
            "requested_style_name": None,
            "requested_style_strength": None,
            "requested_soul_id": request.soul_id,
            "requested_reference_images": list(request.images),
            "style_discovery_status": "not_applicable",
            "api_request_id": None,
            "api_job_id": None,
            "verification_status": "planned",
        }

    if dry_run:
        if backend == "api":
            validation = run_higgsfield_api_adapter(
                build_higgsfield_api_payload(request, prompt, dry_run=True)
            )
            api_metadata["api_dry_run_request"] = validation.get("request_payload")
        prompt_md, meta_json = write_prompt_files(
            book,
            request,
            source_path,
            prompt,
            planned_command,
            image_path,
            dry_run=True,
            schema_checked=False,
            api_metadata=api_metadata,
        )
        return prompt_md, meta_json, image_path

    prompt_md, meta_json = write_prompt_files(
        book,
        request,
        source_path,
        prompt,
        planned_command,
        image_path,
        dry_run=False,
        schema_checked=False,
        api_metadata=api_metadata,
    )
    if backend == "api":
        if not request.allow_paid_generation:
            validation = run_higgsfield_api_adapter(
                build_higgsfield_api_payload(request, prompt, dry_run=True)
            )
            api_metadata["api_dry_run_request"] = validation.get("request_payload")
            write_prompt_files(
                book,
                request,
                source_path,
                prompt,
                planned_command,
                image_path,
                dry_run=False,
                schema_checked=True,
                api_metadata=api_metadata,
            )
            raise SystemExit(
                "HIGGSFIELD_API_PAID_GENERATION_NOT_ALLOWED: Nutze "
                "--allow-paid-generation fuer echte API-Bildgenerierung."
            )

        api_result = run_higgsfield_api_adapter(
            build_higgsfield_api_payload(request, prompt, dry_run=False)
        )
        media_url = api_result.get("image_url")
        api_metadata["api_request_id"] = api_result.get("request_id")
        api_metadata["api_job_id"] = api_result.get("job_id")
        api_metadata["verification_status"] = verification_status(
            api_result.get("raw_response"),
            None,
            request.soul_id,
        )
        if not media_url:
            write_prompt_files(
                book,
                request,
                source_path,
                prompt,
                planned_command,
                image_path,
                dry_run=False,
                schema_checked=True,
                job_result=api_result,
                api_metadata=api_metadata,
            )
            raise SystemExit("Higgsfield-API-Antwort enthaelt keine Medien-URL")
        download_url(media_url, image_path, image_processing)
        write_prompt_files(
            book,
            request,
            source_path,
            prompt,
            planned_command,
            image_path,
            dry_run=False,
            schema_checked=True,
            job_result=api_result,
            media_url=media_url,
            api_metadata=api_metadata,
        )
        return prompt_md, meta_json, image_path

    ensure_reference_inputs(request)
    moodboard_flag = None
    validate_higgsfield_available()
    command = build_higgsfield_command(request, prompt, moodboard_flag)
    prompt_md, meta_json = write_prompt_files(
        book,
        request,
        source_path,
        prompt,
        command,
        image_path,
        dry_run=False,
        schema_checked=True,
    )
    job_result = run_json_command(command)
    media_url = find_first_url(job_result)
    if not media_url:
        write_prompt_files(
            book,
            request,
            source_path,
            prompt,
            command,
            image_path,
            dry_run=False,
            schema_checked=True,
            job_result=job_result,
        )
        raise SystemExit("Higgsfield-Antwort enthaelt keine Medien-URL")
    download_url(media_url, image_path, image_processing)
    write_prompt_files(
        book,
        request,
        source_path,
        prompt,
        command,
        image_path,
        dry_run=False,
        schema_checked=True,
        job_result=job_result,
        media_url=media_url,
    )
    return prompt_md, meta_json, image_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Erzeugt Buchillustrationen via Higgsfield."
    )
    parser.add_argument("--book", required=True, help="Buch-ID, z. B. peter-i-buch-01")
    parser.add_argument("--chapter", help="Kapitelnummer, z. B. 001")
    parser.add_argument("--scene", help="Szenennummer, z. B. 01")
    parser.add_argument("--style", help="Style-Slug; Default aus book.yaml")
    parser.add_argument("--kind", choices=("scene", "chapter"), default="scene")
    parser.add_argument("--model", help="Default aus book.yaml higgsfield.model")
    parser.add_argument(
        "--moodboard",
        help="Moodboard-UUID (nicht Share-Link); Default aus book.yaml higgsfield.moodboard",
    )
    parser.add_argument(
        "--image",
        action="append",
        default=[],
        help="Higgsfield Upload-/Job-UUID oder lokaler Referenzbildpfad; mehrfach nutzbar",
    )
    parser.add_argument(
        "--no-reference",
        action="store_true",
        help="Bewusst ohne Moodboard, Upload- oder Job-Referenz generieren",
    )
    parser.add_argument("--aspect-ratio", help="Default aus book.yaml higgsfield.aspect_ratio")
    parser.add_argument("--quality", help="Default aus book.yaml higgsfield.quality")
    parser.add_argument(
        "--backend",
        choices=("cli", "api", "auto"),
        help="Higgsfield-Backend; Default aus book.yaml higgsfield.backend oder auto",
    )
    parser.add_argument("--soul-id", help="Echte Soul-/Character-Referenz-ID")
    parser.add_argument("--soul-strength", type=float, help="Staerke fuer --soul-id")
    parser.add_argument(
        "--allow-paid-generation",
        action="store_true",
        help="Erlaubt echte bezahlte API-Bildgenerierung nach Style-Discovery.",
    )
    parser.add_argument(
        "--diagnose-higgsfield",
        action="store_true",
        help="Prueft CLI-Schema und Moodboard-Parameter ohne Bildgenerierung",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    book = find_book_project(REPO_ROOT, args.book)
    defaults = higgsfield_defaults(book)
    if args.diagnose_higgsfield:
        diagnostic = diagnose_higgsfield_reference(
            args.model or defaults["model"],
            args.moodboard or defaults["moodboard"],
        )
        print_higgsfield_diagnostic(diagnostic)
        return 0

    if not args.chapter:
        raise SystemExit("--chapter ist erforderlich, ausser mit --diagnose-higgsfield")

    style = args.style or str(book.get("style_mode") or "stil-01-original")
    reference_images = tuple(defaults.get("reference_images") or ())
    cli_images = tuple(args.image or ())
    request = IllustrationRequest(
        book_id=args.book,
        chapter_id=normalize_chapter_id(args.chapter),
        scene_number=normalize_scene_number(args.scene, args.kind),
        style=style,
        kind=args.kind,
        model=args.model or defaults["model"],
        moodboard=args.moodboard or defaults["moodboard"],
        images=cli_images or reference_images,
        no_reference=bool(args.no_reference),
        aspect_ratio=normalize_aspect_ratio(args.aspect_ratio or defaults["aspect_ratio"]),
        quality=args.quality or defaults["quality"],
        overwrite=args.overwrite,
        backend=args.backend or defaults["backend"],
        moodboard_name=defaults.get("moodboard_name"),
        moodboard_strength=float(defaults.get("moodboard_strength", 1.0)),
        soul_id=args.soul_id or defaults.get("soul_id"),
        soul_strength=(
            args.soul_strength
            if args.soul_strength is not None
            else float(defaults.get("soul_strength", 1.0))
        ),
        allow_paid_generation=bool(args.allow_paid_generation),
    )
    prompt_md, meta_json, image_path = generate_illustration(
        request,
        dry_run=bool(args.dry_run),
    )
    print(f"Prompt: {prompt_md}")
    print(f"Metadaten: {meta_json}")
    if args.dry_run:
        print(f"Geplantes Zielbild: {image_path}")
    else:
        print(f"Zielbild: {image_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
