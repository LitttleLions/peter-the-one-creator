"""Read-only helpers for the local translation workbench."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from lib.book_project import load_books as load_book_projects
from lib.output_paths import (
    assembled_dir,
    book_output_root,
    de_scene_dir,
    de_scene_path,
    existing_translation_versions,
    list_ru_scene_paths,
    parse_scene_number,
    source_chapter_path,
)
from lib.status_manager import load_state
from lib.style_prompts import available_style_profiles


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_books(repo_root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    return load_book_projects(repo_root)


def load_models(repo_root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    data = load_yaml(repo_root / "config" / "models.yaml")
    return data.get("models", [])


def load_style_profiles(
    repo_root: Path = REPO_ROOT,
    book: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if book and book.get("styles_dir"):
        profiles = available_style_profiles(repo_root / book["styles_dir"])
        if profiles:
            return profiles
    return available_style_profiles(repo_root / "styles")


def book_by_id(book_id: str | None, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    books = load_books(repo_root)
    if not books:
        raise ValueError("Keine Buchpakete unter books/*/book.yaml gefunden")
    if book_id is None:
        return books[0]
    for book in books:
        if book["id"] == book_id:
            return book
    raise ValueError(f"Buch nicht gefunden: {book_id}")


def load_book_state(book: dict[str, Any], repo_root: Path = REPO_ROOT):
    status_path = repo_root / book["status_file"]
    if not status_path.exists():
        return None
    return load_state(status_path)


def chapter_ids(book: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    output_root = book_output_root(repo_root, book)
    ids = set()
    chapters_dir = output_root / "chapters"
    if chapters_dir.exists():
        ids.update(p.name[:3] for p in chapters_dir.glob("*-source.md"))
    ru_root = output_root / "scenes" / "ru"
    if ru_root.exists():
        ids.update(p.name for p in ru_root.iterdir() if p.is_dir())
    state = load_book_state(book, repo_root)
    if state is not None:
        ids.update(ch.id for ch in state.chapters)
    return sorted(ids)


def scene_counts(
    book: dict[str, Any],
    chapter_id: str,
    style: str,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    output_root = book_output_root(repo_root, book)
    ru_paths = list_ru_scene_paths(output_root, chapter_id)
    ru_nums = [
        num for p in ru_paths
        if (num := parse_scene_number(p, chapter_id)) is not None
    ]
    de_dir = de_scene_dir(output_root, style, chapter_id)
    de_paths = sorted(de_dir.glob("scene-*.md")) if de_dir.exists() else []
    de_nums = [
        num for p in de_paths
        if (num := parse_scene_number(p, chapter_id)) is not None
    ]
    missing = [num for num in sorted(ru_nums) if num not in set(de_nums)]
    return {
        "ru": len(ru_nums),
        "de": len(de_nums),
        "missing": missing,
        "next_missing": missing[0] if missing else None,
        "complete": bool(ru_nums) and not missing,
    }


def chapter_rows(
    book: dict[str, Any],
    style: str,
    repo_root: Path = REPO_ROOT,
) -> list[dict[str, Any]]:
    state = load_book_state(book, repo_root)
    by_id = {ch.id: ch for ch in state.chapters} if state else {}
    output_root = book_output_root(repo_root, book)
    rows = []
    for cid in chapter_ids(book, repo_root):
        counts = scene_counts(book, cid, style, repo_root)
        versions = existing_translation_versions(output_root, cid, style)
        ch = by_id.get(cid)
        rows.append({
            "Kapitel": cid,
            "Status": ch.status if ch else "",
            "Titel RU": ch.title_ru if ch else "",
            "RU": counts["ru"],
            "DE": counts["de"],
            "Fehlt": len(counts["missing"]),
            "Naechste Szene": (
                f"{counts['next_missing']:02d}"
                if counts["next_missing"] is not None
                else ""
            ),
            "Assemblies": len(versions),
        })
    return rows


def latest_assembly(
    book: dict[str, Any],
    chapter_id: str,
    style: str,
    repo_root: Path = REPO_ROOT,
) -> Path | None:
    output_root = book_output_root(repo_root, book)
    versions = existing_translation_versions(output_root, chapter_id, style)
    return versions[-1] if versions else None


def assembly_paths(
    book: dict[str, Any],
    chapter_id: str,
    style: str,
    repo_root: Path = REPO_ROOT,
) -> list[Path]:
    output_root = book_output_root(repo_root, book)
    return existing_translation_versions(output_root, chapter_id, style)


def log_path(book: dict[str, Any], chapter_id: str, repo_root: Path = REPO_ROOT) -> Path:
    return repo_root / book["log_dir"] / f"{chapter_id}.log.md"


def source_exists(
    book: dict[str, Any],
    chapter_id: str,
    repo_root: Path = REPO_ROOT,
) -> bool:
    output_root = book_output_root(repo_root, book)
    return source_chapter_path(output_root, chapter_id).exists()


def de_scene_exists(
    book: dict[str, Any],
    chapter_id: str,
    scene_number: int,
    style: str,
    repo_root: Path = REPO_ROOT,
) -> bool:
    output_root = book_output_root(repo_root, book)
    return de_scene_path(output_root, chapter_id, scene_number, style).exists()
