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
from PIL import Image


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = "text2image_soul_v2"
DEFAULT_MOODBOARD = "https://higgsfield.ai/s/R0FemgKUPW4"
DEFAULT_ASPECT_RATIO = "3:4"
DEFAULT_QUALITY = "720p"
OUTPUT_EXT = ".jpg"
UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)

VISUAL_CONSTRAINTS = (
    "Period-accurate clothing, architecture, tools, horse tack, carts, sledges, "
    "boats, weapons, and environment. No modern objects, no cars, no trucks, no "
    "engines, no electric lights. No readable text, lettering, captions, "
    "inscriptions, logos, watermarks, artist signatures, or marks in the image "
    "corners. A single, unified composition depicting one coherent moment. "
    "No split screens, no multiple panels, no comic-style layouts, "
    "no before-and-after sequences."
)


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


def output_image_path(book: dict[str, Any], request: IllustrationRequest) -> Path:
    book_root = REPO_ROOT / str(book["book_root"])
    assets_root = book_root / "assets"
    if request.kind == "chapter":
        return assets_root / "chapter" / f"chapter-{request.chapter_id}{OUTPUT_EXT}"
    if request.scene_number is None:
        raise SystemExit("--scene ist fuer Szenenbilder erforderlich")
    return (
        assets_root
        / "scene"
        / request.chapter_id
        / f"scene-{request.scene_number:03d}{OUTPUT_EXT}"
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


_MAX_PARAGRAPHS = 3


def clean_markdown_excerpt(text: str, limit: int = 1000) -> str:
    # Erst alle irrelevanten Zeilen herausfiltern
    filtered_lines: list[str] = []
    in_motto_block = False
    for raw in text.splitlines():
        line = raw.strip()
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


def load_book_description(book: dict[str, Any]) -> str:
    """Load book description from export.yaml for prompt context."""
    export_cfg_path = book.get("export_config")
    if not export_cfg_path:
        return ""
    export_path = REPO_ROOT / export_cfg_path
    if not export_path.exists():
        return ""
    try:
        export_cfg = yaml.safe_load(export_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return ""
    description = (export_cfg.get("book") or {}).get("description") or ""
    # Trim to a reasonable length for prompt context (max 500 chars)
    description = description.strip()
    if len(description) > 500:
        description = description[:500].rsplit(" ", 1)[0].rstrip(".,;:") + "..."
    return description


def build_prompt(book: dict[str, Any], request: IllustrationRequest, source_text: str) -> str:
    excerpt = clean_markdown_excerpt(source_text)
    title = str(book.get("title") or request.book_id)
    description = load_book_description(book)
    context = f" Novel context: {description}" if description else ""
    scene_label = (
        f", scene {request.scene_number:02d}"
        if request.scene_number is not None
        else ""
    )
    return (
        f"Novel illustration for \"{title}\" by {book.get('author', '')}."
        f" Setting: ancient {description.split('.')[0] if description else 'historical'}."
        f" Scene location: chapter {request.chapter_id}{scene_label}."
        f" Passage (use for atmosphere and mood, not for literal multi-scene depiction):"
        f" {excerpt}.{context}"
        f" Create ONE unified image capturing the atmosphere of this passage."
        f" {VISUAL_CONSTRAINTS}"
    )


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
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"Keine JSON-Ausgabe von {' '.join(cmd)}: {exc}\n{text[:1000]}"
        ) from exc


def is_uuid(value: str) -> bool:
    return bool(UUID_RE.match(value.strip()))


def is_url(value: str) -> bool:
    return value.strip().lower().startswith(("http://", "https://"))


def higgsfield_defaults(book: dict[str, Any]) -> dict[str, str]:
    cfg = book.get("higgsfield") or {}
    moodboard = cfg.get("moodboard") if isinstance(cfg, dict) else None
    if isinstance(moodboard, dict):
        moodboard_value = (
            moodboard.get("custom_reference_id")
            or moodboard.get("id")
            or moodboard.get("uuid")
            or moodboard.get("share_url")
        )
    else:
        moodboard_value = moodboard
    return {
        "model": (
            str(cfg.get("model") or DEFAULT_MODEL)
            if isinstance(cfg, dict)
            else DEFAULT_MODEL
        ),
        "moodboard": str(moodboard_value or DEFAULT_MOODBOARD),
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


def moodboard_flag_from_schema(schema: Any) -> str | None:
    candidates = [
        "moodboard",
        "moodboard_id",
        "moodboard_url",
        "custom_reference_id",
        "preset",
        "preset_id",
        "style",
        "style_id",
    ]
    names = {name.replace("-", "_").lower(): name for name in iter_param_names(schema)}
    for candidate in candidates:
        if candidate in names:
            return "--" + names[candidate]
    return None


def higgsfield_available() -> bool:
    return higgsfield_executable() is not None


def higgsfield_executable() -> str | None:
    for name in ("higgsfield.cmd", "higgsfield.exe", "higgsfield"):
        if found := shutil.which(name):
            return found
    return None


def validate_moodboard_support(model: str) -> tuple[str, Any]:
    executable = higgsfield_executable()
    if executable is None:
        raise SystemExit(
            "higgsfield CLI nicht gefunden. Installation laut Higgsfield-Skill: "
            "curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh"
        )
    schema = run_json_command([executable, "model", "get", model, "--json"])
    flag = moodboard_flag_from_schema(schema)
    if not flag:
        raise SystemExit(
            "Das Higgsfield-Modellschema enthaelt keinen Moodboard-/Preset-/Style-"
            "Parameter. Prompt und Metadaten wurden geschrieben; bitte CLI/UI "
            "pruefen, bevor automatisch generiert wird."
        )
    return flag, schema


def validate_higgsfield_available() -> None:
    if higgsfield_executable() is None:
        raise SystemExit(
            "higgsfield CLI nicht gefunden. Installation unter Windows: "
            "npm install -g @higgsfield/cli"
        )


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
    if moodboard_flag and is_uuid(request.moodboard):
        command.extend([moodboard_flag, request.moodboard])
    for image in request.images:
        command.extend(["--image", image])
    command.extend(["--wait", "--json"])
    return command


def ensure_reference_inputs(request: IllustrationRequest) -> None:
    if request.no_reference:
        return
    if is_uuid(request.moodboard) or request.images:
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
        "--moodboard <uuid> oder mindestens ein --image <uuid|pfad>."
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


def download_url(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "peter-the-one-creator/illustration-tool"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        data = response.read()
    if destination.suffix.lower() in {".jpg", ".jpeg"}:
        with Image.open(BytesIO(data)) as image:
            image.convert("RGB").save(destination, format="JPEG", quality=95)
    else:
        destination.write_bytes(data)


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
    image_path = output_image_path(book, request)
    if image_path.exists() and not request.overwrite:
        raise SystemExit(f"Zielbild existiert bereits: {image_path}")

    source_path, source_text = read_scene_text(book, request)
    prompt = build_prompt(book, request, source_text)
    planned_command = [
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

    if dry_run:
        prompt_md, meta_json = write_prompt_files(
            book,
            request,
            source_path,
            prompt,
            planned_command,
            image_path,
            dry_run=True,
            schema_checked=False,
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
    )
    ensure_reference_inputs(request)
    moodboard_flag = None
    if is_uuid(request.moodboard) and not request.no_reference:
        moodboard_flag, _schema = validate_moodboard_support(request.model)
    else:
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
    download_url(media_url, image_path)
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
    parser.add_argument("--chapter", required=True, help="Kapitelnummer, z. B. 001")
    parser.add_argument("--scene", help="Szenennummer, z. B. 01")
    parser.add_argument("--style", help="Style-Slug; Default aus book.yaml")
    parser.add_argument("--kind", choices=("scene", "chapter"), default="scene")
    parser.add_argument("--model", help="Default aus book.yaml higgsfield.model")
    parser.add_argument(
        "--moodboard",
        help="Moodboard-/Custom-Reference-UUID; Default aus book.yaml higgsfield.moodboard",
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
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    book = find_book_project(REPO_ROOT, args.book)
    defaults = higgsfield_defaults(book)
    style = args.style or str(book.get("style_mode") or "stil-01-original")
    request = IllustrationRequest(
        book_id=args.book,
        chapter_id=normalize_chapter_id(args.chapter),
        scene_number=normalize_scene_number(args.scene, args.kind),
        style=style,
        kind=args.kind,
        model=args.model or defaults["model"],
        moodboard=args.moodboard or defaults["moodboard"],
        images=tuple(args.image or []),
        no_reference=bool(args.no_reference),
        aspect_ratio=args.aspect_ratio or defaults["aspect_ratio"],
        quality=args.quality or defaults["quality"],
        overwrite=args.overwrite,
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
