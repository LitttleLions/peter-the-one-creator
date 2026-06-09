"""Output path helpers for the multi-book translation pipeline."""

from __future__ import annotations

import re
from pathlib import Path


def book_output_root(repo_root: Path, book_cfg: dict) -> Path:
    return repo_root / (book_cfg.get("work_dir") or book_cfg["output_dir"])


def book_exports_root(repo_root: Path, book_cfg: dict) -> Path:
    if book_cfg.get("exports_dir"):
        return repo_root / book_cfg["exports_dir"]
    return book_output_root(repo_root, book_cfg) / "exports"


def chapters_dir(output_root: Path) -> Path:
    return output_root / "chapters"


def source_chapter_path(output_root: Path, chapter_id: str) -> Path:
    return chapters_dir(output_root) / f"{chapter_id}-source.md"


def ru_scene_dir(output_root: Path, chapter_id: str) -> Path:
    return output_root / "scenes" / "ru" / chapter_id


def de_scene_dir(output_root: Path, style: str, chapter_id: str) -> Path:
    return output_root / "scenes" / "de" / style / chapter_id


def assembled_dir(output_root: Path, style: str) -> Path:
    return output_root / "assembled" / style


def prompts_dir(output_root: Path) -> Path:
    return output_root / "prompts"


def ru_scene_path(output_root: Path, chapter_id: str, scene_number: int) -> Path:
    return ru_scene_dir(output_root, chapter_id) / f"scene-{scene_number:02d}.md"


def de_scene_path(
    output_root: Path,
    chapter_id: str,
    scene_number: int,
    style: str,
) -> Path:
    return de_scene_dir(output_root, style, chapter_id) / (
        f"scene-{scene_number:02d}.md"
    )


def assembled_translation_path(
    output_root: Path,
    chapter_id: str,
    version: int,
    style: str,
) -> Path:
    return assembled_dir(output_root, style) / (
        f"{chapter_id}-translation-v{version}-{style}.md"
    )


def prompt_path(
    output_root: Path,
    chapter_id: str,
    style: str,
    scene_number: int | None = None,
) -> Path:
    if scene_number is None:
        name = f"{chapter_id}-chapter-{style}.md"
    else:
        name = f"{chapter_id}-scene-{scene_number:02d}-{style}.md"
    return prompts_dir(output_root) / name


def parse_scene_number(path: Path, chapter_id: str | None = None) -> int | None:
    patterns = [
        r"^scene-(\d+)\.md$",
        r"^\d+-scene-(\d+)-ru\.md$",
        r"^\d+-scene-(\d+)-de-[a-z]+\.md$",
        r"^\d+-scene-(\d+)-v\d+-[a-z]+\.md$",
        r"^\d+-scene-(\d+)\.md$",
    ]
    for pat in patterns:
        m = re.match(pat, path.name)
        if m:
            return int(m.group(1))
    if chapter_id:
        m = re.match(rf"^{re.escape(chapter_id)}-szene-(\d+)\.md$", path.name)
        if m:
            return int(m.group(1))
    return None


def list_ru_scene_paths(output_root: Path, chapter_id: str) -> list[Path]:
    new_paths = sorted(ru_scene_dir(output_root, chapter_id).glob("scene-*.md"))
    if new_paths:
        return new_paths
    return sorted(chapters_dir(output_root).glob(f"{chapter_id}-scene-*-ru.md"))


def version_from_translation_name(name: str) -> int:
    m = re.search(r"-translation-v(\d+)", name)
    if not m:
        return 0
    return int(m.group(1))


def existing_translation_versions(
    output_root: Path,
    chapter_id: str,
    style: str,
) -> list[Path]:
    new_pattern = re.compile(
        rf"^{re.escape(chapter_id)}-translation-v(\d+)-"
        rf"{re.escape(style)}\.md$"
    )
    new_pattern_without_style = re.compile(
        rf"^{re.escape(chapter_id)}-translation-v(\d+)\.md$"
    )
    legacy_pattern = re.compile(
        rf"^{re.escape(chapter_id)}-translation-v(\d+)-"
        rf"{re.escape(style)}\.md$"
    )
    paths = []
    new_dir = assembled_dir(output_root, style)
    if new_dir.exists():
        paths.extend(p for p in new_dir.iterdir() if new_pattern.match(p.name))
        paths.extend(
            p for p in new_dir.iterdir()
            if new_pattern_without_style.match(p.name)
        )
    old_dir = chapters_dir(output_root)
    if old_dir.exists():
        paths.extend(p for p in old_dir.iterdir() if legacy_pattern.match(p.name))
    return sorted(paths, key=lambda p: version_from_translation_name(p.name))


def next_translation_path(output_root: Path, chapter_id: str, style: str) -> Path:
    existing = existing_translation_versions(output_root, chapter_id, style)
    next_v = 1
    if existing:
        next_v = max(version_from_translation_name(p.name) for p in existing) + 1
    out = assembled_translation_path(output_root, chapter_id, next_v, style)
    out.parent.mkdir(parents=True, exist_ok=True)
    return out


def find_scene_translations(
    output_root: Path,
    chapter_id: str,
    style: str,
) -> dict[int, Path]:
    result: dict[int, Path] = {}

    new_dir = de_scene_dir(output_root, style, chapter_id)
    if new_dir.exists():
        for p in sorted(new_dir.glob("scene-*.md")):
            num = parse_scene_number(p)
            if num is not None:
                result[num] = p
        if result:
            return result

    old_dir = chapters_dir(output_root)
    pattern_new = re.compile(
        rf"^{re.escape(chapter_id)}-scene-(\d+)-de-"
        rf"{re.escape(style)}\.md$"
    )
    pattern_old = re.compile(
        rf"^{re.escape(chapter_id)}-scene-(\d+)-v(\d+)-"
        rf"{re.escape(style)}\.md$"
    )
    versioned: dict[int, tuple[Path, int]] = {}
    if old_dir.exists():
        for p in old_dir.iterdir():
            m = pattern_new.match(p.name)
            if m:
                result[int(m.group(1))] = p
                continue
            m = pattern_old.match(p.name)
            if m:
                num = int(m.group(1))
                ver = int(m.group(2))
                if num not in versioned or ver > versioned[num][1]:
                    versioned[num] = (p, ver)
    for num, val in versioned.items():
        result.setdefault(num, val[0])
    return result


def list_chapter_ids_with_ru_scenes(output_root: Path) -> list[str]:
    ids = set()
    ru_root = output_root / "scenes" / "ru"
    if ru_root.exists():
        ids.update(p.name for p in ru_root.iterdir() if p.is_dir())
    old_dir = chapters_dir(output_root)
    if old_dir.exists():
        for p in old_dir.glob("*-scene-*-ru.md"):
            m = re.match(r"(\d+)-scene-\d+-ru\.md", p.name)
            if m:
                ids.add(m.group(1))
    return sorted(ids)
