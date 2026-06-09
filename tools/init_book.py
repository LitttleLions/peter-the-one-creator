"""
init_book.py
============

Legt ein neues Buchpaket unter books/<book-id>/ an.

Beispiel:
    python tools/init_book.py --source "books/Lew Tolstoi - Anna Karenina.rtf"
"""

from __future__ import annotations

import argparse
import io
import re
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).parent))

from lib.book_project import discover_projects, write_yaml


REPO_ROOT = Path(__file__).resolve().parent.parent


def slugify(value: str) -> str:
    replacements = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
        "Ä": "ae",
        "Ö": "oe",
        "Ü": "ue",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "buch"


def derive_title_author(source_path: Path) -> tuple[str, str]:
    stem = source_path.stem.strip()
    if " - " in stem:
        author, title = stem.split(" - ", 1)
        return title.strip(), author.strip()
    return stem, ""


def relative_to(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def unique_book_id(base: str) -> str:
    existing = {project.id for project in discover_projects(REPO_ROOT)}
    if base not in existing:
        return base
    idx = 2
    while f"{base}-{idx}" in existing:
        idx += 1
    return f"{base}-{idx}"


def ensure_dirs(book_root: Path) -> list[Path]:
    paths = [
        book_root / "source",
        book_root / "assets" / "covers",
        book_root / "styles",
        book_root / "work" / "chapters",
        book_root / "work" / "scenes" / "ru",
        book_root / "work" / "scenes" / "de",
        book_root / "work" / "assembled",
        book_root / "work" / "prompts",
        book_root / "work" / "style-tests",
        book_root / "work" / "legacy",
        book_root / "exports",
        book_root / "status" / "logs",
    ]
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
    return paths


def copy_style_templates(book_root: Path, dry_run: bool) -> list[Path]:
    copied = []
    source_dir = REPO_ROOT / "styles"
    target_dir = book_root / "styles"
    if not source_dir.exists():
        return copied
    for source in sorted(source_dir.glob("*.md")):
        target = target_dir / source.name
        if target.exists():
            continue
        copied.append(target)
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    return copied


def build_book_yaml(args: argparse.Namespace, source_name: str, book_id: str) -> dict[str, Any]:
    return {
        "id": book_id,
        "title": args.title,
        "author": args.author,
        "source_path": f"source/{source_name}",
        "source_lang": args.source_lang,
        "target_lang": args.target_lang,
        "ruleset_path": args.ruleset_path,
        "ruleset_apply": args.ruleset_apply,
        "style_mode": args.style,
        "work_dir": "work",
        "exports_dir": "exports",
        "status_file": "status/status.json",
        "log_dir": "status/logs",
        "styles_dir": "styles",
        "assets_dir": "assets",
        "names_file": "names.yaml",
        "structure": {
            "mode": "scenes",
            "label": "Kapitel mit Szenen",
            "groups": [],
        },
        "display": {
            "chapters": {
                "format": "words_de",
                "suffix": " Kapitel",
                "align": "center",
                "include_source_title": False,
            },
            "scenes": {
                "show": False,
                "format": "number",
                "align": "center",
                "page_break": False,
                "separator": "",
            },
        },
        "naming_convention": {
            "style": "",
            "example": [],
        },
        "notes": args.notes or "Neu angelegtes Buch.",
        "ai": {
            "provider": "openrouter",
            "model": args.model,
            "granularity": "scene",
            "max_tokens_per_scene": args.max_tokens_per_scene,
        },
    }


def build_export_yaml(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "defaults": {
            "language": "de-DE" if args.target_lang == "de" else args.target_lang,
            "publisher": "",
            "rights": "",
            "description": "",
            "cover": {
                "mode": "placeholder",
                "image_path": "",
                "background": "#f59e0b",
                "foreground": "#ffffff",
            },
            "front_matter": {
                "cover_in_body": False,
                "description_page": True,
                "imprint_page": True,
                "toc_page": False,
                "combined_epub_front_matter": True,
                "combined_heading": "Titelei",
                "description_heading": "Zu dieser Ausgabe",
                "imprint_heading": "Impressum",
                "toc_heading": "Inhalt",
            },
            "output": {
                "chapter_headings": True,
                "scene_numbers": False,
                "strip_control_metadata": True,
                "scene_separator": "* * *",
            },
        },
        "book": {
            "title": args.title,
            "author": args.author,
            "language": "de-DE" if args.target_lang == "de" else args.target_lang,
            "publisher": "",
            "rights": "",
            "description": "",
            "cover": {
                "mode": "placeholder",
                "image_path": "",
            },
        },
    }


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description="Neues Buchpaket anlegen.")
    ap.add_argument("--source", required=True, help="Quelldatei, z.B. books/Anna.rtf")
    ap.add_argument("--id", default=None, help="Stabile Buch-ID; default aus Titel")
    ap.add_argument("--title", default=None)
    ap.add_argument("--author", default=None)
    ap.add_argument("--source-lang", default="ru")
    ap.add_argument("--target-lang", default="de")
    ap.add_argument("--style", default="stil-01-original")
    ap.add_argument("--ruleset-path", default="")
    ap.add_argument("--ruleset-apply", action=argparse.BooleanOptionalAction, default=False)
    ap.add_argument("--model", default="deepseek/deepseek-v4-flash")
    ap.add_argument("--max-tokens-per-scene", type=int, default=10000)
    ap.add_argument("--notes", default="")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    source = Path(args.source)
    if not source.is_absolute():
        source = REPO_ROOT / source
    if not source.exists():
        print(f"FEHLER: Quelldatei nicht gefunden: {source}", file=sys.stderr)
        return 1

    guessed_title, guessed_author = derive_title_author(source)
    args.title = args.title or guessed_title
    args.author = args.author if args.author is not None else guessed_author
    book_id = args.id or unique_book_id(slugify(args.title))
    book_root = REPO_ROOT / "books" / book_id
    target_source = book_root / "source" / source.name

    print(f"Buchpaket: {args.title} ({book_id})")
    print(f"Quelle: {relative_to(source, REPO_ROOT)}")
    print(f"Ziel: {relative_to(target_source, REPO_ROOT)}")
    print(f"Style: {args.style}")

    if args.dry_run:
        print("(dry-run: keine Dateien geschrieben oder verschoben)")
        return 0

    ensure_dirs(book_root)
    if source.resolve() != target_source.resolve():
        if target_source.exists():
            print(f"FEHLER: Zielquelle existiert bereits: {target_source}", file=sys.stderr)
            return 2
        target_source.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target_source))

    book_yaml = build_book_yaml(args, target_source.name, book_id)
    write_yaml(book_root / "book.yaml", book_yaml)
    export_yaml_path = book_root / "export.yaml"
    if not export_yaml_path.exists():
        write_yaml(export_yaml_path, build_export_yaml(args))
    names_yaml_path = book_root / "names.yaml"
    if not names_yaml_path.exists():
        write_yaml(names_yaml_path, {"entries": []})
    copied = copy_style_templates(book_root, dry_run=False)

    print("Angelegt/aktualisiert:")
    print(f"  {relative_to(book_root / 'book.yaml', REPO_ROOT)}")
    print(f"  {relative_to(export_yaml_path, REPO_ROOT)}")
    print(f"  {relative_to(names_yaml_path, REPO_ROOT)}")
    for path in copied:
        print(f"  {relative_to(path, REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
