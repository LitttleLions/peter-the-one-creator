"""
build_shelf_website.py
======================

Regenerates the Motivatier Shelf website catalog from book packages.

Scans ``books/*/export.yaml`` for ``website.enabled: true``, resolves covers
via the same logic as ``export_manuscript.prepare_cover``, writes
``webpage/public/data/catalog.json`` and copies cover images to
``webpage/public/covers/<book-id>.<ext>``.

Usage::

    python tools/build_shelf_website.py

Opt-in fields in each ``books/<id>/export.yaml``::

    website:
      enabled: true
      amazon_url: ""      # optional; empty hides the Amazon CTA in the UI
      sort_order: 10      # optional; lower numbers appear first
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WEBPAGE_PUBLIC = REPO_ROOT / "webpage" / "public"
CATALOG_PATH = WEBPAGE_PUBLIC / "data" / "catalog.json"
COVERS_DIR = WEBPAGE_PUBLIC / "covers"

sys.path.insert(0, str(Path(__file__).parent))

from export_manuscript import prepare_cover  # noqa: E402

ALLOWED_COVER_SUFFIXES = {".jpg", ".jpeg", ".png"}


def load_export_meta(book_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    export_path = book_root / "export.yaml"
    try:
        data = yaml.safe_load(export_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"export.yaml ist ungueltig: {exc}") from exc
    defaults = data.get("defaults", {}) or {}
    book_cfg = data.get("book", {}) or {}
    meta: dict[str, Any] = {**defaults, **book_cfg}
    for key in ("cover", "front_matter", "output", "illustrations"):
        merged = {
            **(defaults.get(key, {}) or {}),
            **(book_cfg.get(key, {}) or {}),
        }
        if merged:
            meta[key] = merged
    meta["_base_dir"] = str(book_root)
    return meta, data


def website_config(export_data: dict[str, Any]) -> dict[str, Any]:
    return export_data.get("website") or {}


def summary_text(meta: dict[str, Any]) -> str:
    summary = str(meta.get("summary") or "").strip()
    if summary:
        return summary
    return str(meta.get("description") or "").strip()


def normalize_cover_suffix(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".jpeg":
        return ".jpg"
    if suffix in ALLOWED_COVER_SUFFIXES:
        return suffix
    raise ValueError(f"Coverformat nicht unterstuetzt fuer Website: {path}")


def build_catalog_entry(
    book_id: str,
    meta: dict[str, Any],
    website: dict[str, Any],
    cover_dest_name: str,
) -> dict[str, Any]:
    amazon_url = str(website.get("amazon_url") or "").strip()
    sort_order = website.get("sort_order")
    entry: dict[str, Any] = {
        "id": book_id,
        "title": str(meta.get("title") or "").strip(),
        "subtitle": str(meta.get("subtitle") or "").strip(),
        "author": str(meta.get("author") or "").strip(),
        "summary": summary_text(meta),
        "coverUrl": f"./covers/{cover_dest_name}",
        "amazonUrl": amazon_url,
    }
    if sort_order is not None:
        entry["sortOrder"] = int(sort_order)
    return entry


def discover_book_roots(repo_root: Path) -> list[Path]:
    books_root = repo_root / "books"
    if not books_root.is_dir():
        return []
    roots: list[Path] = []
    for child in sorted(books_root.iterdir()):
        if child.is_dir() and (child / "export.yaml").is_file():
            roots.append(child)
    return roots


def ensure_output_dirs() -> None:
    (WEBPAGE_PUBLIC / "data").mkdir(parents=True, exist_ok=True)
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    for directory in (WEBPAGE_PUBLIC / "data", COVERS_DIR):
        gitkeep = directory / ".gitkeep"
        if not any(directory.iterdir()):
            gitkeep.touch()


def build_shelf_website(repo_root: Path = REPO_ROOT) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    ensure_output_dirs()
    errors: list[str] = []
    warnings: list[str] = []
    entries: list[dict[str, Any]] = []
    enabled_ids: list[str] = []
    written_paths: list[str] = []

    for book_root in discover_book_roots(repo_root):
        book_id = book_root.name
        try:
            meta, export_data = load_export_meta(book_root)
        except ValueError as exc:
            warnings.append(f"{book_id}: {exc}")
            continue
        website = website_config(export_data)
        if not bool(website.get("enabled")):
            continue

        enabled_ids.append(book_id)
        title = str(meta.get("title") or "").strip()
        author = str(meta.get("author") or "").strip()
        if not title:
            errors.append(f"{book_id}: website.enabled, aber kein Titel in export.yaml")
            continue
        if not author:
            errors.append(f"{book_id}: website.enabled, aber kein Autor in export.yaml")
            continue

        try:
            cover_src = prepare_cover(
                work_dir=book_root / "work",
                title=title,
                author=author,
                style="shelf",
                scope_label="website",
                meta=meta,
            )
            suffix = normalize_cover_suffix(cover_src)
            cover_dest_name = f"{book_id}{suffix}"
            cover_dest = COVERS_DIR / cover_dest_name
            shutil.copy2(cover_src, cover_dest)
            written_paths.append(str(cover_dest.relative_to(repo_root)))
        except (FileNotFoundError, ValueError, OSError) as exc:
            errors.append(f"{book_id}: Cover konnte nicht aufgeloest werden ({exc})")
            continue

        entries.append(
            build_catalog_entry(book_id, meta, website, cover_dest_name)
        )

    entries.sort(
        key=lambda item: (
            item.get("sortOrder", 10_000),
            str(item.get("title") or "").casefold(),
        )
    )

    catalog = {"books": entries}
    CATALOG_PATH.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    written_paths.insert(0, str(CATALOG_PATH.relative_to(repo_root)))

    return entries, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Motivatier Shelf: Katalog und Cover nach webpage/public/ schreiben.",
    )
    parser.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    entries, errors, warnings = build_shelf_website()
    enabled = [entry["id"] for entry in entries]

    if warnings:
        print("Warnungen:", file=sys.stderr)
        for message in warnings:
            print(f"  - {message}", file=sys.stderr)

    if errors:
        print("Fehler:", file=sys.stderr)
        for message in errors:
            print(f"  - {message}", file=sys.stderr)

    print(f"Katalog: {len(entries)} Buch/Buecher")
    for entry in entries:
        print(f"  - {entry['id']}: {entry['title']}")
    print(f"Geschrieben: {CATALOG_PATH.relative_to(REPO_ROOT)}")

    if errors:
        return 1
    if not entries:
        print("Hinweis: Keine Buecher mit website.enabled: true gefunden.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
