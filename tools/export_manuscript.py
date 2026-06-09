"""
export_manuscript.py
====================

Exportiert fertige DE-Szenen als DOCX und/oder EPUB.

Quelle:
    books/<book-id>/work/scenes/de/<style>/<Kapitel>/scene-XX.md

Ausgabe:
    books/<book-id>/exports/<style>/chapter/docx/
    books/<book-id>/exports/<style>/chapter/epub/
    books/<book-id>/exports/<style>/chapter/work/
    books/<book-id>/exports/<style>/book/docx/
    books/<book-id>/exports/<style>/book/epub/
    books/<book-id>/exports/<style>/book/work/
"""

from __future__ import annotations

import argparse
import html
import io
import json
import re
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

import yaml

from lib.book_project import find_book as find_book_project
from lib.output_paths import (
    book_exports_root,
    book_output_root,
    find_scene_translations,
    list_chapter_ids_with_ru_scenes,
    list_ru_scene_paths,
    parse_scene_number,
    source_chapter_path,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class SceneExport:
    number: int
    text: str


@dataclass
class ChapterExport:
    chapter_id: str
    title: str
    scenes: list[SceneExport]
    missing: list[int]
    ru_count: int
    de_count: int


@dataclass
class ExportResult:
    chapters: list[ChapterExport]
    missing_by_chapter: dict[str, list[int]]
    partial: bool


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or {}


def find_book(book_id: str | None) -> dict[str, Any]:
    return find_book_project(REPO_ROOT, book_id)


def load_export_config(book: dict[str, Any]) -> dict[str, Any]:
    export_path = REPO_ROOT / book.get("export_config", "")
    data = load_yaml(export_path)
    defaults = data.get("defaults", {}) or {}
    book_cfg = data.get("book", {}) or {}
    meta = {**defaults, **book_cfg}
    for key in ("cover", "front_matter", "output"):
        merged = {
            **(defaults.get(key, {}) or {}),
            **(book_cfg.get(key, {}) or {}),
        }
        if merged:
            meta[key] = merged
    meta.setdefault("title", book.get("title", ""))
    meta.setdefault("author", book.get("author", ""))
    meta.setdefault("language", "de-DE")
    meta.setdefault("cover", defaults.get("cover", {}) or {})
    meta.setdefault("front_matter", defaults.get("front_matter", {}) or {})
    meta.setdefault("output", defaults.get("output", {}) or {})
    structure = book.get("structure") or {}
    meta.setdefault("structure_groups", structure.get("groups") or [])
    meta.setdefault("display", book.get("display") or {})
    meta["_base_dir"] = str(export_path.parent)
    return meta


def sanitize_filename(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "export"


def yaml_scalar(value: Any) -> str:
    dumped = yaml.safe_dump(
        str(value),
        default_flow_style=True,
        allow_unicode=True,
        sort_keys=False,
    )
    return dumped.splitlines()[0]


def export_dirs(exports_root: Path, style: str, scope: str) -> dict[str, Path]:
    root = exports_root / style / scope
    return {
        "root": root,
        "docx": root / "docx",
        "epub": root / "epub",
        "work": root / "work",
        "manifests": root / "manifests",
    }


def get_title(output_root: Path, chapter_id: str) -> str:
    src = source_chapter_path(output_root, chapter_id)
    if not src.exists():
        return f"Kapitel {chapter_id}"
    for line in src.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            return title or f"Kapitel {chapter_id}"
    return f"Kapitel {chapter_id}"


CONTROL_LINE_PATTERNS = [
    # Scene files may contain LLM-generated wrappers like "## 6",
    # "### Vier" or "## Szene 4". Reader exports should expose only
    # chapter-level structure; Pandoc uses Markdown headings for EPUB nav.
    re.compile(r"^#{1,6}\s+.+$"),
    re.compile(r"^\d+\s*$"),
    re.compile(r"^#{1,6}\s*szene\s+\d+\s*$", re.IGNORECASE),
    re.compile(r"^#{1,6}\s*scene\s+\d+\s*$", re.IGNORECASE),
    re.compile(r"^\*?buch:\s+.*\*?$", re.IGNORECASE),
    re.compile(r"^\*?stil:\s+.*\*?$", re.IGNORECASE),
    re.compile(r"^\*?erstellt am:\s+.*\*?$", re.IGNORECASE),
    re.compile(r"^\*?provider:\s+.*\*?$", re.IGNORECASE),
    re.compile(r"^\*?modell:\s+.*\*?$", re.IGNORECASE),
    re.compile(r"^\*?tokens?:\s+.*\*?$", re.IGNORECASE),
    re.compile(r"^-{3,}$"),
]


def clean_scene_markdown(text: str) -> str:
    lines = []
    for line in text.replace("\r\n", "\n").split("\n"):
        stripped = line.strip()
        if any(pattern.match(stripped) for pattern in CONTROL_LINE_PATTERNS):
            continue
        if stripped.startswith("Hier ist die ") or stripped.startswith(
            "Hier ist eine "
        ):
            continue
        lines.append(line.rstrip())
    cleaned = "\n".join(lines).strip()
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned


def markdown_to_plain_blocks(text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    for raw_block in re.split(r"\n\s*\n", text.strip()):
        block = raw_block.strip()
        if not block:
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", block)
        if heading:
            level = min(len(heading.group(1)), 3)
            blocks.append((f"heading{level}", heading.group(2).strip()))
        else:
            block = re.sub(r"\*\*(.*?)\*\*", r"\1", block)
            block = re.sub(r"\*(.*?)\*", r"\1", block)
            blocks.append(("paragraph", block.replace("\n", " ")))
    return blocks


def collect_chapter(
    output_root: Path,
    chapter_id: str,
    style: str,
    allow_partial: bool,
) -> ChapterExport:
    ru_paths = list_ru_scene_paths(output_root, chapter_id)
    ru_nums = [
        num for path in ru_paths
        if (num := parse_scene_number(path, chapter_id)) is not None
    ]
    scene_map = find_scene_translations(output_root, chapter_id, style)
    missing = [num for num in sorted(ru_nums) if num not in scene_map]
    if missing and not allow_partial:
        return ChapterExport(
            chapter_id=chapter_id,
            title=get_title(output_root, chapter_id),
            scenes=[],
            missing=missing,
            ru_count=len(ru_nums),
            de_count=len(scene_map),
        )
    scenes = []
    for num in sorted(scene_map):
        if ru_nums and num not in set(ru_nums):
            continue
        text = clean_scene_markdown(scene_map[num].read_text(encoding="utf-8"))
        if text:
            scenes.append(SceneExport(number=num, text=text))
    return ChapterExport(
        chapter_id=chapter_id,
        title=get_title(output_root, chapter_id),
        scenes=scenes,
        missing=missing,
        ru_count=len(ru_nums),
        de_count=len(scene_map),
    )


def collect_export(
    output_root: Path,
    style: str,
    scope: str,
    chapter_id: str | None,
    allow_partial: bool,
) -> ExportResult:
    if scope == "chapter":
        if not chapter_id:
            raise SystemExit("--chapter ist bei --scope chapter erforderlich")
        chapter_ids = [chapter_id]
    else:
        chapter_ids = list_chapter_ids_with_ru_scenes(output_root)
    chapters = [
        collect_chapter(output_root, cid, style, allow_partial)
        for cid in chapter_ids
    ]
    missing = {
        chapter.chapter_id: chapter.missing
        for chapter in chapters
        if chapter.missing
    }
    if missing and not allow_partial:
        return ExportResult(chapters=[], missing_by_chapter=missing, partial=False)
    return ExportResult(
        chapters=[chapter for chapter in chapters if chapter.scenes],
        missing_by_chapter=missing,
        partial=bool(missing),
    )


def document_title(meta: dict[str, Any], scope: str, chapter: ChapterExport | None) -> str:
    title = str(meta.get("title") or "Export")
    if scope == "chapter" and chapter is not None:
        return f"{title} - Kapitel {chapter.chapter_id}"
    return title


def make_cover(
    work_dir: Path,
    title: str,
    author: str,
    style: str,
    scope_label: str,
    meta: dict[str, Any],
) -> Path:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise RuntimeError(
            "Pillow ist fuer Platzhalter-Cover nicht installiert. "
            "Bitte `pip install -r requirements.txt` ausfuehren."
        ) from exc

    cover_cfg = meta.get("cover", {}) or {}
    bg = cover_cfg.get("background", "#f59e0b")
    fg = cover_cfg.get("foreground", "#ffffff")
    img = Image.new("RGB", (1600, 2400), bg)
    draw = ImageDraw.Draw(img)
    try:
        title_font = ImageFont.truetype("arial.ttf", 92)
        author_font = ImageFont.truetype("arial.ttf", 54)
        small_font = ImageFont.truetype("arial.ttf", 38)
    except OSError:
        title_font = ImageFont.load_default()
        author_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    def wrap(text: str, font: ImageFont.ImageFont, width: int) -> list[str]:
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            bbox = draw.textbbox((0, 0), candidate, font=font)
            if bbox[2] - bbox[0] <= width or not current:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    y = 520
    for line in wrap(title, title_font, 1240):
        bbox = draw.textbbox((0, 0), line, font=title_font)
        draw.text(((1600 - (bbox[2] - bbox[0])) / 2, y), line, fill=fg, font=title_font)
        y += 112
    y += 90
    for line in wrap(author, author_font, 1200):
        bbox = draw.textbbox((0, 0), line, font=author_font)
        draw.text(((1600 - (bbox[2] - bbox[0])) / 2, y), line, fill=fg, font=author_font)
        y += 70
    footer = f"{scope_label} | {style}"
    bbox = draw.textbbox((0, 0), footer, font=small_font)
    draw.text(((1600 - (bbox[2] - bbox[0])) / 2, 2040), footer, fill=fg, font=small_font)
    path = work_dir / "cover.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return path


def resolve_cover_image(path_text: str, base_dir: Path | None = None) -> Path:
    raw = Path(path_text)
    path = raw if raw.is_absolute() else (base_dir or REPO_ROOT) / raw
    if not path.exists():
        raise FileNotFoundError(f"Coverbild nicht gefunden: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"Coverpfad ist keine Datei: {path}")
    return path


def prepare_cover(
    work_dir: Path,
    title: str,
    author: str,
    style: str,
    scope_label: str,
    meta: dict[str, Any],
) -> Path:
    cover_cfg = meta.get("cover", {}) or {}
    image_path = str(cover_cfg.get("image_path") or "").strip()
    mode = str(cover_cfg.get("mode") or "placeholder").strip().lower()
    if mode == "image" or image_path:
        base_dir = Path(str(meta.get("_base_dir") or REPO_ROOT))
        return resolve_cover_image(image_path, base_dir)
    return make_cover(work_dir, title, author, style, scope_label, meta)


def markdown_image_path(path: Path, markdown_path: Path) -> str:
    try:
        rel = path.resolve().relative_to(markdown_path.parent.resolve())
        text = rel.as_posix()
    except ValueError:
        text = path.resolve().as_posix()
    return text.replace(" ", "%20")


def front_matter_config(meta: dict[str, Any]) -> dict[str, Any]:
    return meta.get("front_matter", {}) or {}


def should_show(meta: dict[str, Any], key: str, default: bool = True) -> bool:
    return bool(front_matter_config(meta).get(key, default))


def display_config(meta: dict[str, Any]) -> dict[str, Any]:
    return meta.get("display", {}) or {}


def cardinal_de_ascii(value: int) -> str:
    units = {
        1: "ein",
        2: "zwei",
        3: "drei",
        4: "vier",
        5: "fuenf",
        6: "sechs",
        7: "sieben",
        8: "acht",
        9: "neun",
        10: "zehn",
        11: "elf",
        12: "zwoelf",
        13: "dreizehn",
        14: "vierzehn",
        15: "fuenfzehn",
        16: "sechzehn",
        17: "siebzehn",
        18: "achtzehn",
        19: "neunzehn",
    }
    tens = {
        20: "zwanzig",
        30: "dreissig",
        40: "vierzig",
        50: "fuenfzig",
        60: "sechzig",
        70: "siebzig",
        80: "achtzig",
        90: "neunzig",
    }
    if value <= 0:
        return str(value)
    if value < 20:
        return units[value]
    if value < 100:
        ten = value // 10 * 10
        unit = value % 10
        if unit == 0:
            return tens[ten]
        return f"{units[unit]}und{tens[ten]}"
    if value < 1000:
        hundred = value // 100
        rest = value % 100
        prefix = "hundert" if hundred == 1 else f"{units.get(hundred, str(hundred))}hundert"
        return prefix if rest == 0 else f"{prefix}{cardinal_de_ascii(rest)}"
    return str(value)


def ordinal_de_ascii(value: int) -> str:
    irregular = {
        1: "erstes",
        2: "zweites",
        3: "drittes",
        4: "viertes",
        5: "fuenftes",
        6: "sechstes",
        7: "siebtes",
        8: "achtes",
        9: "neuntes",
        10: "zehntes",
        11: "elftes",
        12: "zwoelftes",
        13: "dreizehntes",
        14: "vierzehntes",
        15: "fuenfzehntes",
        16: "sechzehntes",
        17: "siebzehntes",
        18: "achtzehntes",
        19: "neunzehntes",
    }
    text = irregular.get(value)
    if text is None:
        text = f"{cardinal_de_ascii(value)}stes"
    return text[:1].upper() + text[1:]


def display_chapter_title(chapter: ChapterExport, meta: dict[str, Any] | None = None) -> str:
    if not meta:
        return clean_chapter_title(chapter)
    chapter_cfg = (display_config(meta).get("chapters") or {})
    fmt = str(chapter_cfg.get("format") or "").strip()
    if not fmt:
        return clean_chapter_title(chapter)
    try:
        number = int(chapter.chapter_id)
    except ValueError:
        number = 0
    suffix = str(chapter_cfg.get("suffix") or "")
    if fmt == "words_de":
        title = f"{ordinal_de_ascii(number)}{suffix}"
    elif fmt == "number_dot":
        title = f"{number}."
    elif fmt == "number":
        title = str(number)
    else:
        title = clean_chapter_title(chapter)
    if chapter_cfg.get("include_source_title"):
        source_title = clean_chapter_title(chapter)
        if source_title and source_title != f"Kapitel {chapter.chapter_id}":
            title = f"{title}: {source_title}"
    return title


def clean_chapter_title(chapter: ChapterExport) -> str:
    title = chapter.title.strip()
    title = re.sub(r"^Kapitel\s+\d+\s*:\s*", "", title, flags=re.IGNORECASE)
    has_cyrillic = bool(re.search(r"[\u0400-\u04ff]", title))
    looks_mojibake = any(token in title for token in ("\u00d0", "\u00d1", "\u00c3"))
    if not title or has_cyrillic or looks_mojibake:
        return f"Kapitel {chapter.chapter_id}"
    return f"Kapitel {chapter.chapter_id}: {title}"


def chapter_heading_markdown(chapter: ChapterExport) -> str:
    return f"# {clean_chapter_title(chapter)} {{#kapitel-{chapter.chapter_id}}}"


def chapter_heading_markdown_for_level(
    chapter: ChapterExport,
    level: int,
    meta: dict[str, Any] | None = None,
) -> str:
    level = max(1, min(level, 6))
    chapter_cfg = (display_config(meta or {}).get("chapters") or {})
    classes = []
    if chapter_cfg:
        classes.append("chapter-heading")
        if chapter_cfg.get("align") == "center":
            classes.append("centered")
    attr_bits = [f"#kapitel-{chapter.chapter_id}", *[f".{cls}" for cls in classes]]
    attrs = " ".join(attr_bits)
    return f"{'#' * level} {display_chapter_title(chapter, meta)} {{{attrs}}}"


def group_for_chapter(meta: dict[str, Any], chapter_id: str) -> dict[str, Any] | None:
    groups = meta.get("structure_groups") or []
    for group in groups:
        start = str(group.get("from") or "")
        end = str(group.get("to") or "")
        if start and end and start <= chapter_id <= end:
            return group
    return None


def group_heading_markdown(group: dict[str, Any]) -> str:
    label = str(group.get("label") or group.get("id") or "Buch").strip()
    group_id = sanitize_filename(str(group.get("id") or label))
    return f"# {label} {{#gruppe-{group_id}}}"


def add_imprint_lines(
    lines: list[str],
    title: str,
    meta: dict[str, Any],
    scope: str,
) -> None:
    lines.append(f"**Titel:** {title}")
    lines.append("")
    if meta.get("subtitle") and scope == "book":
        lines.extend([f"**Untertitel:** {meta['subtitle']}", ""])
    if meta.get("author"):
        lines.extend([f"**Autor:** {meta['author']}", ""])
    if meta.get("translator"):
        lines.extend([f"**Uebersetzung:** {meta['translator']}", ""])
    if meta.get("publisher"):
        lines.extend([f"**Herausgeber:** {meta['publisher']}", ""])
    if meta.get("rights"):
        lines.extend([f"**Rechte:** {meta['rights']}", ""])
    lines.extend([f"**Sprache:** {meta.get('language', 'de-DE')}", ""])


def html_paragraphs(text: str) -> str:
    paragraphs = []
    for paragraph in re.split(r"\n\s*\n", text.strip()):
        clean = " ".join(line.strip() for line in paragraph.splitlines()).strip()
        if clean:
            paragraphs.append(f"<p>{html.escape(clean)}</p>")
    return "\n".join(paragraphs)


def render_title_page_html(
    title: str,
    meta: dict[str, Any],
    scope: str,
    partial: bool,
) -> list[str]:
    lines = [
        '::: {.frontmatter-page .titlepage epub:type="titlepage"}',
        f"[{title}]{{.book-title}}",
        "",
    ]
    if meta.get("subtitle") and scope == "book":
        lines.extend([f"[{meta['subtitle']}]{{.subtitle}}", ""])
    if meta.get("author"):
        lines.extend([f"[{meta['author']}]{{.author}}", ""])
    if meta.get("translator"):
        lines.append(
            f"[Uebersetzung: {meta['translator']}]{{.translator}}"
        )
        lines.append("")
    if partial:
        lines.extend(["[Teil-Export: Es fehlen noch Szenen.]{.partial-note}", ""])
    lines.extend([":::", ""])
    return lines


def render_frontmatter_page_html(
    heading: str,
    body: str,
    anchor: str,
    epub_type: str,
) -> list[str]:
    return [
        f'<section id="{html.escape(anchor)}" class="frontmatter-page textpage" epub:type="{html.escape(epub_type)}">',
        f"  <h1>{html.escape(heading)}</h1>",
        html_paragraphs(body),
        "</section>",
        "",
    ]


def render_front_matter_markdown(
    meta: dict[str, Any],
    title: str,
    scope: str,
    partial: bool,
    cover_ref: str | None,
) -> list[str]:
    fm = front_matter_config(meta)
    description = str(meta.get("description") or "").strip()
    explicit_summary = str(meta.get("summary") or "").strip()
    summary = explicit_summary
    author_bio = str(meta.get("author_bio") or "").strip()
    # EPUB uses Pandoc's official cover image. Do not also emit a Markdown
    # cover chapter, otherwise readers show duplicate cover/title fragments.
    wants_cover = False
    wants_title = should_show(meta, "title_page", True)
    wants_summary = bool(summary and should_show(meta, "summary_page", True))
    wants_author_bio = bool(author_bio and should_show(meta, "author_bio_page", True))
    wants_description = bool(
        description
        and not explicit_summary
        and should_show(meta, "description_page", True)
    )
    wants_imprint = should_show(meta, "imprint_page", True)
    lines: list[str] = []
    if not (wants_cover or wants_title or wants_summary or wants_author_bio or wants_description or wants_imprint or partial):
        return lines

    if fm.get("combined_epub_front_matter", True):
        lines.extend([f"# {fm.get('combined_heading', 'Titelei')} {{#frontmatter}}", ""])
        if wants_cover:
            lines.extend([f"![Cover]({cover_ref})", ""])
        if wants_title:
            lines.extend([f"## {fm.get('title_heading', 'Titelseite')}", ""])
            lines.extend([f"**{title}**", ""])
            if meta.get("subtitle") and scope == "book":
                lines.extend([str(meta["subtitle"]), ""])
            if meta.get("author"):
                lines.extend([str(meta["author"]), ""])
            if meta.get("translator"):
                lines.extend([f"Uebersetzung: {meta['translator']}", ""])
        if partial:
            lines.extend(["> Teil-Export: Es fehlen noch Szenen.", ""])
        if wants_summary:
            lines.extend([f"## {fm.get('summary_heading', fm.get('description_heading', 'Zusammenfassung'))}", "", summary, ""])
        if wants_author_bio:
            lines.extend([f"## {fm.get('author_bio_heading', 'Leben des Autors')}", "", author_bio, ""])
        if wants_description:
            lines.extend([f"## {fm.get('description_heading', 'Zu dieser Ausgabe')}", "", description, ""])
        if wants_imprint:
            lines.extend([f"## {fm.get('imprint_heading', 'Impressum')}", ""])
            add_imprint_lines(lines, title, meta, scope)
        return lines

    if wants_title:
        lines.extend(render_title_page_html(title, meta, scope, partial))
    if partial:
        # The title page already carries the partial note when present.
        if not wants_title:
            lines.extend(["> Teil-Export: Es fehlen noch Szenen.", ""])
    if wants_summary:
        heading = fm.get("summary_heading", fm.get("description_heading", "Zusammenfassung"))
        lines.extend(render_frontmatter_page_html(str(heading), summary, "frontmatter-summary", "preface"))
    if wants_author_bio:
        heading = fm.get("author_bio_heading", "Leben des Autors")
        lines.extend(render_frontmatter_page_html(str(heading), author_bio, "frontmatter-author", "foreword"))
    if wants_description:
        heading = fm.get("description_heading", "Zu dieser Ausgabe")
        lines.extend([f"# {heading} {{#frontmatter-description}}", "", description, ""])
    if wants_imprint:
        heading = fm.get("imprint_heading", "Impressum")
        lines.extend([f"# {heading} {{#frontmatter-imprint}}", ""])
        add_imprint_lines(lines, title, meta, scope)
    return lines


def render_export_markdown(
    chapters: list[ChapterExport],
    meta: dict[str, Any],
    style: str,
    scope: str,
    partial: bool,
    cover_ref: str | None,
) -> str:
    title = document_title(meta, scope, chapters[0] if chapters else None)
    lines = [
        "---",
        f"title: {yaml_scalar(title)}",
        f"author: {yaml_scalar(meta.get('author', ''))}",
        f"lang: {meta.get('language', 'de-DE')}",
        f"date: {date.today().isoformat()}",
    ]
    if meta.get("rights"):
        lines.append(f"rights: {yaml_scalar(meta['rights'])}")
    lines.extend(["---", ""])
    lines.extend(render_front_matter_markdown(meta, title, scope, partial, cover_ref))
    if should_show(meta, "toc_page", False):
        fm = front_matter_config(meta)
        heading = fm.get("toc_heading", "Inhalt")
        lines.extend([f"# {heading} {{#frontmatter-toc}}", ""])
        for chapter in chapters:
            lines.append(f"- [{display_chapter_title(chapter, meta)}](#kapitel-{chapter.chapter_id})")
        lines.append("")
    last_group_id = None
    has_groups = bool(meta.get("structure_groups"))
    chapter_level = 2 if has_groups else 1
    for chapter in chapters:
        group = group_for_chapter(meta, chapter.chapter_id)
        group_id = group.get("id") if group else None
        if group and group_id != last_group_id:
            lines.append(group_heading_markdown(group))
            lines.append("")
            last_group_id = group_id
        lines.append(chapter_heading_markdown_for_level(chapter, chapter_level, meta))
        lines.append("")
        scene_cfg = (display_config(meta).get("scenes") or {})
        show_scene_marker = bool(scene_cfg.get("show"))
        has_display = bool(display_config(meta))
        for idx, scene in enumerate(chapter.scenes):
            if show_scene_marker:
                marker = str(scene.number if scene_cfg.get("format", "number") == "number" else scene.number)
                align_class = " .centered" if scene_cfg.get("align") == "center" else ""
                lines.extend([f"[{marker}]{{.scene-marker{align_class}}}", ""])
            elif idx and not has_display:
                lines.extend(["", str(meta.get("output", {}).get("scene_separator", "* * *")), ""])
            elif idx and str(scene_cfg.get("separator") or ""):
                lines.extend(["", str(scene_cfg.get("separator")), ""])
            lines.append(scene.text)
            lines.append("")
    return "\n".join(lines).strip() + "\n"


def write_docx(
    path: Path,
    chapters: list[ChapterExport],
    meta: dict[str, Any],
    style: str,
    scope: str,
    partial: bool,
    cover_path: Path,
) -> None:
    try:
        from docx import Document
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.shared import Inches, Pt, RGBColor
    except ImportError as exc:
        raise RuntimeError(
            "python-docx ist nicht installiert. "
            "Bitte `pip install -r requirements.txt` ausfuehren."
        ) from exc

    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.85)
    section.bottom_margin = Inches(0.85)
    section.left_margin = Inches(0.95)
    section.right_margin = Inches(0.95)

    styles = document.styles
    styles["Normal"].font.name = "Georgia"
    styles["Normal"].font.size = Pt(11.5)
    styles["Title"].font.name = "Georgia"
    styles["Title"].font.size = Pt(28)
    styles["Heading 1"].font.name = "Georgia"
    styles["Heading 1"].font.size = Pt(18)
    styles["Heading 1"].font.color.rgb = RGBColor(45, 45, 60)

    title = document_title(meta, scope, chapters[0] if chapters else None)
    fm = front_matter_config(meta)
    description = str(meta.get("description") or "").strip()
    explicit_summary = str(meta.get("summary") or "").strip()
    summary = explicit_summary
    author_bio = str(meta.get("author_bio") or "").strip()

    if should_show(meta, "cover_in_body", True):
        document.add_picture(str(cover_path), width=Inches(4.1))
        last = document.paragraphs[-1]
        last.alignment = WD_ALIGN_PARAGRAPH.CENTER
        document.add_page_break()

    if should_show(meta, "title_page", True):
        document.add_heading(title, 0)
        subtitle = meta.get("subtitle")
        if subtitle and scope == "book":
            p = document.add_paragraph(str(subtitle))
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p = document.add_paragraph(str(meta.get("author", "")))
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if meta.get("translator"):
            p = document.add_paragraph(f"Uebersetzung: {meta['translator']}")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if partial:
            p = document.add_paragraph("Teil-Export: Es fehlen noch Szenen.")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        document.add_page_break()

    if summary and should_show(meta, "summary_page", True):
        document.add_heading(str(fm.get("summary_heading", fm.get("description_heading", "Zusammenfassung"))), 1)
        for paragraph in summary.split("\n\n"):
            text = paragraph.strip()
            if text:
                p = document.add_paragraph(text)
                p.paragraph_format.space_after = Pt(7)
                p.paragraph_format.line_spacing = 1.12
        document.add_page_break()

    if author_bio and should_show(meta, "author_bio_page", True):
        document.add_heading(str(fm.get("author_bio_heading", "Leben des Autors")), 1)
        for paragraph in author_bio.split("\n\n"):
            text = paragraph.strip()
            if text:
                p = document.add_paragraph(text)
                p.paragraph_format.space_after = Pt(7)
                p.paragraph_format.line_spacing = 1.12
        document.add_page_break()

    wants_description = (
        description
        and not explicit_summary
        and should_show(meta, "description_page", True)
    )
    if wants_description:
        document.add_heading(str(fm.get("description_heading", "Zu dieser Ausgabe")), 1)
        for paragraph in description.split("\n\n"):
            text = paragraph.strip()
            if text:
                p = document.add_paragraph(text)
                p.paragraph_format.space_after = Pt(7)
                p.paragraph_format.line_spacing = 1.12
        document.add_page_break()

    subtitle = meta.get("subtitle")

    if should_show(meta, "imprint_page", True):
        document.add_heading(str(fm.get("imprint_heading", "Impressum")), 1)
        imprint_rows = [
            ("Titel", title),
            ("Untertitel", str(meta.get("subtitle", "")) if scope == "book" else ""),
            ("Autor", str(meta.get("author", ""))),
            ("Uebersetzung", str(meta.get("translator", ""))),
            ("Herausgeber", str(meta.get("publisher", ""))),
            ("Rechte", str(meta.get("rights", ""))),
            ("Sprache", str(meta.get("language", "de-DE"))),
        ]
        for label, value in imprint_rows:
            if not value:
                continue
            p = document.add_paragraph()
            p.add_run(f"{label}: ").bold = True
            p.add_run(value)
        document.add_page_break()

    if should_show(meta, "toc_page", True):
        document.add_heading(str(fm.get("toc_heading", "Inhalt")), 1)
        for chapter in chapters:
            document.add_paragraph(display_chapter_title(chapter, meta), style=None)
        document.add_page_break()

    last_group_id = None
    for cidx, chapter in enumerate(chapters):
        if cidx:
            document.add_page_break()
        group = group_for_chapter(meta, chapter.chapter_id)
        group_id = group.get("id") if group else None
        if group and group_id != last_group_id:
            document.add_heading(str(group.get("label") or group_id), 1)
            last_group_id = group_id
        heading = document.add_heading(display_chapter_title(chapter, meta), 2 if group else 1)
        chapter_cfg = (display_config(meta).get("chapters") or {})
        if chapter_cfg.get("align") == "center":
            heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        scene_cfg = (display_config(meta).get("scenes") or {})
        show_scene_marker = bool(scene_cfg.get("show"))
        has_display = bool(display_config(meta))
        for sidx, scene in enumerate(chapter.scenes):
            if show_scene_marker:
                marker = document.add_paragraph(str(scene.number))
                if scene_cfg.get("align") == "center":
                    marker.alignment = WD_ALIGN_PARAGRAPH.CENTER
                marker.paragraph_format.space_after = Pt(8)
            elif sidx and not has_display:
                sep_text = str(meta.get("output", {}).get("scene_separator", "* * *"))
                sep = document.add_paragraph(sep_text)
                sep.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif sidx and str(scene_cfg.get("separator") or ""):
                sep = document.add_paragraph(str(scene_cfg.get("separator")))
                if scene_cfg.get("align") == "center":
                    sep.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for kind, block in markdown_to_plain_blocks(scene.text):
                if kind.startswith("heading"):
                    level = int(kind[-1]) + 1
                    document.add_heading(block, min(level, 3))
                else:
                    p = document.add_paragraph(block)
                    p.paragraph_format.first_line_indent = Inches(0.25)
                    p.paragraph_format.space_after = Pt(7)
                    p.paragraph_format.line_spacing = 1.12
    path.parent.mkdir(parents=True, exist_ok=True)
    document.save(path)


def write_epub_css(path: Path) -> Path:
    css = (
        "body {\n"
        '  font-family: Georgia, "Times New Roman", serif;\n'
        "  line-height: 1.42;\n"
        "}\n"
        "\n"
        ".frontmatter-page {\n"
        "  break-before: page;\n"
        "  page-break-before: always;\n"
        "  margin: 0 auto;\n"
        "  max-width: 38em;\n"
        "}\n"
        "\n"
        ".frontmatter-page h1 {\n"
        "  margin-top: 0;\n"
        "  margin-bottom: 1em;\n"
        "  text-align: center;\n"
        "  font-size: 1.6em;\n"
        "  font-weight: normal;\n"
        "  letter-spacing: 0;\n"
        "}\n"
        "\n"
        ".frontmatter-page p {\n"
        "  text-indent: 0;\n"
        "  margin: 0 0 0.8em;\n"
        "}\n"
        "\n"
        ".frontmatter-page.textpage {\n"
        "  font-size: 0.93em;\n"
        "  line-height: 1.36;\n"
        "  max-width: 40em;\n"
        "}\n"
        "\n"
        ".frontmatter-page.textpage h1 {\n"
        "  font-size: 1.35em;\n"
        "}\n"
        "\n"
        "section.chapter-heading.centered {\n"
        "  text-align: left;\n"
        "}\n"
        "\n"
        "h1.chapter-heading,\n"
        "h2.chapter-heading,\n"
        "h3.chapter-heading {\n"
        "  font-size: 1.22em;\n"
        "  font-weight: normal;\n"
        "  margin: 1.35em 0 1em;\n"
        "}\n"
        "\n"
        "h1.chapter-heading.centered,\n"
        "h2.chapter-heading.centered,\n"
        "h3.chapter-heading.centered {\n"
        "  text-align: center;\n"
        "}\n"
        "\n"
        ".scene-marker {\n"
        "  display: block;\n"
        "  margin: 1.25em 0 1.05em;\n"
        "  text-indent: 0;\n"
        "}\n"
        "\n"
        ".scene-marker.centered {\n"
        "  text-align: center;\n"
        "}\n"
        "\n"
        ".titlepage {\n"
        "  padding-top: 28%;\n"
        "  text-align: center;\n"
        "}\n"
        "\n"
        ".titlepage p {\n"
        "  text-align: center;\n"
        "  text-indent: 0;\n"
        "  margin-left: 0;\n"
        "  margin-right: 0;\n"
        "}\n"
        "\n"
        ".titlepage .book-title {\n"
        "  display: block;\n"
        "  margin: 0 0 0.7em;\n"
        "  font-size: 2.15em;\n"
        "  font-weight: normal;\n"
        "  line-height: 1.15;\n"
        "}\n"
        "\n"
        ".titlepage .subtitle {\n"
        "  display: block;\n"
        "  margin-top: 0.3em;\n"
        "  font-size: 1.15em;\n"
        "}\n"
        "\n"
        ".titlepage .author {\n"
        "  display: block;\n"
        "  margin-top: 2.4em;\n"
        "  font-size: 1.18em;\n"
        "}\n"
        "\n"
        ".titlepage .translator {\n"
        "  display: block;\n"
        "  margin-top: 0.6em;\n"
        "  font-size: 0.95em;\n"
        "}\n"
        "\n"
        ".titlepage .partial-note {\n"
        "  display: block;\n"
        "  margin-top: 2.5em;\n"
        "  font-size: 0.85em;\n"
        "  font-style: italic;\n"
        "}\n"
        "\n"
        "blockquote {\n"
        "  margin: 1.1em 0 1.1em 0.8em;\n"
        "  padding: 0;\n"
        "  font-size: 0.88em;\n"
        "  font-style: italic;\n"
        "  line-height: 1.36;\n"
        "  color: #444;\n"
        "}\n"
        "\n"
        "blockquote p {\n"
        "  text-indent: 0;\n"
        "  margin: 0 0 0.4em;\n"
        "}\n"
    )
    path.write_text(css + "\n", encoding="utf-8")
    return path


def write_epub(
    path: Path,
    markdown_path: Path,
    cover_path: Path,
    meta: dict[str, Any],
) -> None:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise RuntimeError("Pandoc wurde nicht gefunden; EPUB-Export nicht moeglich.")
    path.parent.mkdir(parents=True, exist_ok=True)
    css_path = write_epub_css(markdown_path.parent / "epub.css")
    cmd = [
        pandoc,
        str(markdown_path),
        "-o",
        str(path),
        "--toc",
        "--toc-depth=1",
        "--split-level=1",
        "--epub-chapter-level=1",
        "--epub-title-page=false",
        f"--epub-cover-image={cover_path}",
        f"--css={css_path}",
        f"--metadata=lang:{meta.get('language', 'de-DE')}",
    ]
    if meta.get("description"):
        cmd.append(f"--metadata=description:{meta['description']}")
    if meta.get("publisher"):
        cmd.append(f"--metadata=publisher:{meta['publisher']}")
    if meta.get("rights"):
        cmd.append(f"--metadata=rights:{meta['rights']}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    if result.returncode != 0:
        raise RuntimeError(
            "Pandoc EPUB-Export fehlgeschlagen:\n"
            + result.stdout
            + result.stderr
        )


def check_epub(path: Path) -> list[str]:
    required = ["mimetype", "META-INF/container.xml"]
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
    missing = [item for item in required if item not in names]
    if not any(name.endswith(".opf") for name in names):
        missing.append("*.opf")
    if not any("nav" in name.lower() for name in names):
        missing.append("nav")
    if not any("cover" in name.lower() for name in names):
        missing.append("cover")
    return missing


def remove_auto_title_heading_from_epub(path: Path, title: str) -> None:
    """Pandoc emits a visible H1 before the custom title page.

    `--epub-title-page=false` disables Pandoc's generated title page, but the
    first body file may still start with a metadata-derived H1. Reader apps can
    paginate that as a lonely title page before our formatted title page.
    """
    with zipfile.ZipFile(path, "r") as zf:
        entries = [(info, zf.read(info.filename)) for info in zf.infolist()]

    title_re = re.escape(title.strip())
    h1_pattern = re.compile(
        rb'(<body[^>]*>\s*<section[^>]*>\s*)'
        rb'<h1[^>]*>\s*'
        + title_re.encode("utf-8")
        + rb'\s*</h1>\s*(?=<div class="frontmatter-page titlepage")',
        flags=re.DOTALL,
    )

    new_entries: list[tuple[zipfile.ZipInfo, bytes]] = []
    changed = False
    for info, data in entries:
        if info.filename.endswith(".xhtml") and b"frontmatter-page titlepage" in data:
            new_data, count = h1_pattern.subn(rb"\1", data, count=1)
            if count:
                data = new_data
                changed = True
        new_entries.append((info, data))

    if not changed:
        return

    tmp = path.with_suffix(path.suffix + ".tmp")
    with zipfile.ZipFile(tmp, "w") as zf:
        for info, data in new_entries:
            compression = zipfile.ZIP_STORED if info.filename == "mimetype" else zipfile.ZIP_DEFLATED
            new_info = zipfile.ZipInfo(info.filename, info.date_time)
            new_info.comment = info.comment
            new_info.extra = info.extra
            new_info.internal_attr = info.internal_attr
            new_info.external_attr = info.external_attr
            new_info.create_system = info.create_system
            zf.writestr(new_info, data, compress_type=compression)
    tmp.replace(path)


def rel_label(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def output_basename(
    meta: dict[str, Any],
    style: str,
    scope: str,
    chapter: str | None,
) -> str:
    title = sanitize_filename(str(meta.get("title", "export")))
    if scope == "chapter":
        return f"chapter-{chapter}-{title}-{style}"
    return f"book-{title}-{style}"


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                          errors="replace")

    ap = argparse.ArgumentParser(description="Exportiert DOCX/EPUB aus DE-Szenen.")
    ap.add_argument("--book", default=None, help="Buch-ID")
    ap.add_argument("--style", required=True, help="Style-Profil/Output-Ordner")
    ap.add_argument("--scope", choices=["chapter", "book"], required=True)
    ap.add_argument("--chapter", default=None, help="Kapitel-ID bei scope=chapter")
    ap.add_argument("--format", choices=["docx", "epub", "all"], default="all")
    ap.add_argument("--allow-partial", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    book = find_book(args.book)
    output_root = book_output_root(REPO_ROOT, book)
    meta = load_export_config(book)
    result = collect_export(
        output_root=output_root,
        style=args.style,
        scope=args.scope,
        chapter_id=args.chapter,
        allow_partial=args.allow_partial,
    )
    print(f"=== Export: {meta.get('title', book.get('title'))} ===")
    print(f"Scope: {args.scope}")
    print(f"Style: {args.style}")
    print(f"Format: {args.format}")
    if result.missing_by_chapter:
        print("Fehlende Szenen:")
        for cid, nums in result.missing_by_chapter.items():
            print(f"  {cid}: " + ", ".join(f"{num:02d}" for num in nums))
    if result.missing_by_chapter and not args.allow_partial:
        print("ABBRUCH: unvollstaendig. Nutze --allow-partial fuer Teil-Export.")
        return 2
    if not result.chapters:
        print("ABBRUCH: keine exportierbaren Szenen gefunden.")
        return 2

    for chapter in result.chapters:
        print(
            f"Kapitel {chapter.chapter_id}: "
            f"{len(chapter.scenes)} Szenen exportierbar "
            f"(RU={chapter.ru_count}, DE={chapter.de_count})"
        )
    if args.dry_run:
        print("(dry-run: keine Dateien geschrieben)")
        return 0

    dirs = export_dirs(book_exports_root(REPO_ROOT, book), args.style, args.scope)
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = output_basename(meta, args.style, args.scope, args.chapter)
    base = f"{base}-{timestamp}"
    scope_label = (
        f"Kapitel {args.chapter}" if args.scope == "chapter" else "Gesamtes Buch"
    )
    title = document_title(meta, args.scope, result.chapters[0])
    cover_path = prepare_cover(
        dirs["work"] / base,
        title=title,
        author=str(meta.get("author", book.get("author", ""))),
        style=args.style,
        scope_label=scope_label,
        meta=meta,
    )
    md_path = dirs["work"] / f"{base}.md"
    cover_ref = markdown_image_path(cover_path, md_path)
    md_text = render_export_markdown(
        result.chapters, meta, args.style, args.scope, result.partial, cover_ref
    )
    md_path.write_text(md_text, encoding="utf-8")

    outputs: list[Path] = []
    if args.format in ("docx", "all"):
        docx_path = dirs["docx"] / f"{base}.docx"
        write_docx(
            docx_path, result.chapters, meta, args.style, args.scope,
            result.partial, cover_path,
        )
        outputs.append(docx_path)
    if args.format in ("epub", "all"):
        epub_path = dirs["epub"] / f"{base}.epub"
        write_epub(epub_path, md_path, cover_path, meta)
        remove_auto_title_heading_from_epub(
            epub_path,
            document_title(meta, args.scope, result.chapters[0] if result.chapters else None),
        )
        missing = check_epub(epub_path)
        if missing:
            raise RuntimeError(
                "EPUB-Sanity-Check fehlgeschlagen: " + ", ".join(missing)
            )
        outputs.append(epub_path)
    manifest_path = dirs["manifests"] / f"{base}.json"
    manifest = {
        "book_id": book["id"],
        "book_title": meta.get("title", book.get("title")),
        "style": args.style,
        "scope": args.scope,
        "chapter": args.chapter if args.scope == "chapter" else None,
        "format": args.format,
        "partial": result.partial,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "chapters": [
            {
                "id": chapter.chapter_id,
                "scenes": len(chapter.scenes),
                "missing": chapter.missing,
            }
            for chapter in result.chapters
        ],
        "outputs": [rel_label(path) for path in outputs],
        "work_markdown": rel_label(md_path),
        "cover": rel_label(cover_path),
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("Geschrieben:")
    for path in outputs:
        print(f"  {rel_label(path)}")
    print(f"Arbeitsdatei: {rel_label(md_path)}")
    print(f"Manifest: {rel_label(manifest_path)}")
    cover_label = rel_label(cover_path)
    print(f"Cover: {cover_label}")
    return 0


if __name__ == "__main__":
    sys.exit(main())