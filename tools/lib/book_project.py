"""Book package discovery and path normalization.

The active project layout stores each production book under
``books/<book-id>/``.  Tools still receive a small dict because the older
pipeline was built around that shape; this module is the single place that
derives those compatibility fields.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


DEFAULT_AI = {
    "provider": "openrouter",
    "model": "deepseek/deepseek-v4-flash",
    "granularity": "scene",
    "max_tokens_per_scene": 10000,
}


@dataclass(frozen=True)
class BookProject:
    root: Path
    config: dict[str, Any]

    @property
    def id(self) -> str:
        return str(self.config["id"])

    def rel_to_repo(self, repo_root: Path, path: Path) -> str:
        try:
            return path.resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            return path.as_posix()

    def abs_path(self, key: str, default: str) -> Path:
        value = str(self.config.get(key) or default)
        path = Path(value)
        return path if path.is_absolute() else self.root / path

    def source_path(self) -> Path:
        return self.abs_path("source_path", "source")

    def work_dir(self) -> Path:
        return self.abs_path("work_dir", "work")

    def exports_dir(self) -> Path:
        return self.abs_path("exports_dir", "exports")

    def status_file(self) -> Path:
        return self.abs_path("status_file", "status/status.json")

    def log_dir(self) -> Path:
        return self.abs_path("log_dir", "status/logs")

    def styles_dir(self) -> Path:
        return self.abs_path("styles_dir", "styles")

    def assets_dir(self) -> Path:
        return self.abs_path("assets_dir", "assets")

    def names_file(self) -> Path:
        return self.abs_path("names_file", "names.yaml")

    def export_config_path(self) -> Path:
        return self.root / "export.yaml"

    def as_tool_config(self, repo_root: Path) -> dict[str, Any]:
        cfg = dict(self.config)
        cfg.setdefault("source_lang", "ru")
        cfg.setdefault("target_lang", "de")
        cfg.setdefault("ruleset_path", "")
        cfg.setdefault("ruleset_apply", False)
        cfg.setdefault("style_mode", "stil-01-original")
        cfg.setdefault("naming_convention", {"style": "", "example": []})
        cfg.setdefault("notes", "")
        cfg.setdefault("names_file", "names.yaml")
        cfg.setdefault("structure", {"mode": "scenes", "label": "Kapitel mit Szenen", "groups": []})
        cfg.setdefault("display", {
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
        })
        cfg["ai"] = {**DEFAULT_AI, **(cfg.get("ai") or {})}
        cfg["book_root"] = self.rel_to_repo(repo_root, self.root)
        cfg["source_path"] = self.rel_to_repo(repo_root, self.source_path())
        cfg["output_dir"] = self.rel_to_repo(repo_root, self.work_dir())
        cfg["work_dir"] = cfg["output_dir"]
        cfg["exports_dir"] = self.rel_to_repo(repo_root, self.exports_dir())
        cfg["status_file"] = self.rel_to_repo(repo_root, self.status_file())
        cfg["log_dir"] = self.rel_to_repo(repo_root, self.log_dir())
        cfg["styles_dir"] = self.rel_to_repo(repo_root, self.styles_dir())
        cfg["assets_dir"] = self.rel_to_repo(repo_root, self.assets_dir())
        cfg["names_file"] = self.rel_to_repo(repo_root, self.names_file())
        cfg["export_config"] = self.rel_to_repo(repo_root, self.export_config_path())
        return cfg


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def discover_projects(repo_root: Path) -> list[BookProject]:
    projects = []
    books_root = repo_root / "books"
    if not books_root.exists():
        return []
    for book_yaml in sorted(books_root.glob("*/book.yaml")):
        cfg = load_yaml(book_yaml)
        if not cfg:
            continue
        cfg.setdefault("id", book_yaml.parent.name)
        projects.append(BookProject(root=book_yaml.parent, config=cfg))
    return projects


def load_books(repo_root: Path) -> list[dict[str, Any]]:
    return [project.as_tool_config(repo_root) for project in discover_projects(repo_root)]


def find_book(repo_root: Path, book_id: str | None = None) -> dict[str, Any]:
    books = load_books(repo_root)
    if not books:
        raise SystemExit("Keine Buchpakete unter books/*/book.yaml gefunden")
    if book_id is None:
        return books[0]
    for book in books:
        if book["id"] == book_id:
            return book
    raise SystemExit(f"Buch mit id={book_id} nicht gefunden")


def book_project(repo_root: Path, book_id: str) -> BookProject:
    for project in discover_projects(repo_root):
        if project.id == book_id:
            return project
    raise SystemExit(f"Buch mit id={book_id} nicht gefunden")


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
