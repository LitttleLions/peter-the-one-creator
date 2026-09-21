"""Reihenkatalog fuer EPUB und Taschenbuch: andere Motivatier-Classics."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
CATALOG_HEADING = "Weitere Motivatier Classics"
SUMMARY_LIMIT = 520


@dataclass(frozen=True)
class CatalogEntry:
    book_id: str
    title: str
    author: str
    summary: str
    cover_path: Path | None
    sort_order: int


def _find_named_image(directory: Path, stem: str) -> Path | None:
    if not directory.is_dir():
        return None
    for ext in IMAGE_EXTENSIONS:
        candidate = directory / f"{stem}{ext}"
        if candidate.is_file():
            return candidate
    return None


def _summary_text(meta: dict[str, Any]) -> str:
    summary = str(meta.get("summary") or "").strip()
    if summary:
        return summary
    return str(meta.get("description") or "").strip()


def compact_summary(text: str, limit: int = SUMMARY_LIMIT) -> str:
    first = re.split(r"\n\s*\n", text.strip(), maxsplit=1)[0]
    clean = " ".join(first.split())
    if len(clean) <= limit:
        return clean
    clipped = clean[: limit - 1].rsplit(" ", 1)[0]
    return f"{clipped}…"


def _load_export_meta(book_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    export_path = book_root / "export.yaml"
    data = yaml.safe_load(export_path.read_text(encoding="utf-8")) or {}
    defaults = data.get("defaults") or {}
    book_cfg = data.get("book") or {}
    meta: dict[str, Any] = {**defaults, **book_cfg}
    meta["_base_dir"] = str(book_root)
    return meta, data


def _website_config(export_data: dict[str, Any]) -> dict[str, Any]:
    return export_data.get("website") or {}


def _include_in_catalog(website: dict[str, Any]) -> bool:
    if not bool(website.get("enabled")):
        return False
    if "catalog" not in website:
        return True
    return bool(website.get("catalog"))


def load_series_catalog(
    repo_root: Path,
    exclude_book_id: str | None = None,
) -> list[CatalogEntry]:
    books_root = Path(repo_root) / "books"
    if not books_root.is_dir():
        return []
    entries: list[CatalogEntry] = []
    skip = str(exclude_book_id or "").strip()
    for child in sorted(books_root.iterdir()):
        if not child.is_dir() or not (child / "export.yaml").is_file():
            continue
        if child.name == skip:
            continue
        try:
            meta, export_data = _load_export_meta(child)
        except (OSError, yaml.YAMLError):
            continue
        website = _website_config(export_data)
        if not _include_in_catalog(website):
            continue
        title = str(meta.get("title") or "").strip()
        author = str(meta.get("author") or "").strip()
        summary = compact_summary(_summary_text(meta))
        if not title or not author or not summary:
            continue
        sort_order = website.get("sort_order")
        entries.append(
            CatalogEntry(
                book_id=child.name,
                title=title,
                author=author,
                summary=summary,
                cover_path=_find_named_image(child / "assets" / "covers", "cover"),
                sort_order=int(sort_order) if sort_order is not None else 999,
            )
        )
    entries.sort(key=lambda item: (item.sort_order, item.title.casefold()))
    return entries


def _image_ref(path: Path, relative_to: Path) -> str:
    try:
        rel = path.resolve().relative_to(relative_to.parent.resolve())
        return rel.as_posix().replace(" ", "%20")
    except ValueError:
        return path.resolve().as_posix().replace(" ", "%20")


def catalog_markdown(entries: list[CatalogEntry], markdown_path: Path) -> list[str]:
    if not entries:
        return []
    lines = ["", f"# {CATALOG_HEADING} {{#series-catalog}}", ""]
    for item in entries:
        lines.append(f'<div class="series-entry">')
        if item.cover_path is not None and item.cover_path.is_file():
            ref = _image_ref(item.cover_path, markdown_path)
            alt = html.escape(item.title)
            lines.append(f'<img src="{html.escape(ref)}" alt="{alt}" />')
        lines.append("")
        lines.append(f"**{item.title}**  ")
        lines.append(f"{item.author}")
        lines.append("")
        lines.append(item.summary)
        lines.append("")
        lines.append("</div>")
        lines.append("")
    return lines


def catalog_html(entries: list[CatalogEntry], html_path: Path) -> list[str]:
    if not entries:
        return []
    lines = [
        '<section class="series-catalog" id="series-catalog">',
        f"<h1>{html.escape(CATALOG_HEADING)}</h1>",
    ]
    for item in entries:
        lines.append('<article class="series-entry">')
        if item.cover_path is not None and item.cover_path.is_file():
            ref = _image_ref(item.cover_path, html_path)
            lines.append(
                f'<img src="{html.escape(ref)}" alt="{html.escape(item.title)}" />'
            )
        lines.append('<div class="series-copy">')
        lines.append(f"<h2>{html.escape(item.title)}</h2>")
        lines.append(f'<p class="series-author">{html.escape(item.author)}</p>')
        lines.append(f"<p>{html.escape(item.summary)}</p>")
        lines.append("</div>")
        lines.append("</article>")
    lines.append("</section>")
    return lines
