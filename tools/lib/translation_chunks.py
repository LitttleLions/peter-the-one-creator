"""Helpers for translating oversized scenes in internal chunks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lib.output_paths import book_output_root


DEFAULT_CHUNK_CHAR_LIMIT = 24000


@dataclass
class SceneChunk:
    scene_number: int
    part: int
    total: int
    text: str


def chunk_char_limit(book: dict[str, Any], pipeline: dict[str, Any]) -> int:
    ai_cfg = book.get("ai") or {}
    if ai_cfg.get("chunk_char_limit") is not None:
        return int(ai_cfg["chunk_char_limit"])
    if ai_cfg.get("chunk_char_limit_chars") is not None:
        return int(ai_cfg["chunk_char_limit_chars"])
    ai_defaults = (pipeline.get("pipeline") or {}).get("ai_defaults") or {}
    if ai_defaults.get("chunk_char_limit") is not None:
        return int(ai_defaults["chunk_char_limit"])
    if ai_defaults.get("chunk_char_limit_chars") is not None:
        return int(ai_defaults["chunk_char_limit_chars"])
    return DEFAULT_CHUNK_CHAR_LIMIT


def should_chunk(text: str, limit: int) -> bool:
    return limit > 0 and len(text) > limit


def split_long_paragraph(paragraph: str, limit: int) -> list[str]:
    if len(paragraph) <= limit:
        return [paragraph]
    sentences = re.split(r"(?<=[.!?…])\s+", paragraph)
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for sentence in sentences:
        if not sentence:
            continue
        add_len = len(sentence) + (1 if current else 0)
        if current and current_len + add_len > limit:
            chunks.append(" ".join(current).strip())
            current = [sentence]
            current_len = len(sentence)
        elif len(sentence) > limit:
            if current:
                chunks.append(" ".join(current).strip())
                current = []
                current_len = 0
            for idx in range(0, len(sentence), limit):
                chunks.append(sentence[idx:idx + limit].strip())
        else:
            current.append(sentence)
            current_len += add_len
    if current:
        chunks.append(" ".join(current).strip())
    return [chunk for chunk in chunks if chunk]


def split_text_chunks(text: str, limit: int) -> list[str]:
    if not should_chunk(text, limit):
        return [text.strip()]
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for paragraph in paragraphs:
        para_parts = split_long_paragraph(paragraph, limit)
        for part in para_parts:
            add_len = len(part) + (2 if current else 0)
            if current and current_len + add_len > limit:
                chunks.append("\n\n".join(current).strip())
                current = [part]
                current_len = len(part)
            else:
                current.append(part)
                current_len += add_len
    if current:
        chunks.append("\n\n".join(current).strip())
    return chunks or [text.strip()]


def scene_chunks(scene_number: int, text: str, limit: int) -> list[SceneChunk]:
    parts = split_text_chunks(text, limit)
    total = len(parts)
    return [
        SceneChunk(scene_number=scene_number, part=idx, total=total, text=part)
        for idx, part in enumerate(parts, 1)
    ]


def chunk_root(repo_root: Path, book: dict[str, Any]) -> Path:
    return book_output_root(repo_root, book) / "chunks"


def ru_chunk_path(
    repo_root: Path,
    book: dict[str, Any],
    chapter_id: str,
    scene_number: int,
    part: int,
) -> Path:
    return (
        chunk_root(repo_root, book)
        / "ru"
        / chapter_id
        / f"scene-{scene_number:02d}"
        / f"part-{part:02d}.md"
    )


def de_chunk_path(
    repo_root: Path,
    book: dict[str, Any],
    style: str,
    chapter_id: str,
    scene_number: int,
    part: int,
) -> Path:
    return (
        chunk_root(repo_root, book)
        / "de"
        / style
        / chapter_id
        / f"scene-{scene_number:02d}"
        / f"part-{part:02d}.md"
    )


def chunk_prompt_path(
    repo_root: Path,
    book: dict[str, Any],
    style: str,
    chapter_id: str,
    scene_number: int,
    part: int,
) -> Path:
    output_root = book_output_root(repo_root, book)
    return (
        output_root
        / "prompts"
        / f"{chapter_id}-scene-{scene_number:02d}-part-{part:02d}-{style}.md"
    )


def write_ru_chunks(
    repo_root: Path,
    book: dict[str, Any],
    chapter_id: str,
    chunks: list[SceneChunk],
) -> None:
    for chunk in chunks:
        path = ru_chunk_path(
            repo_root,
            book,
            chapter_id,
            chunk.scene_number,
            chunk.part,
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(chunk.text.rstrip() + "\n", encoding="utf-8")


OVERLAP_WINDOW = 80
OVERLAP_MIN_CHARS = 20


def _detect_overlap(tail: str, head: str) -> int:
    """Return length of exact suffix of *tail* that repeats at start of *head*."""
    if not tail or not head:
        return 0
    max_len = min(OVERLAP_WINDOW, len(tail), len(head))
    for n in range(max_len, OVERLAP_MIN_CHARS - 1, -1):
        if tail.endswith(head[:n]):
            return n
    return 0


def _strip_tail_overlap(prev: str, current: str) -> str:
    overlap_len = _detect_overlap(prev, current)
    if overlap_len == 0:
        return current
    return current[overlap_len:].lstrip()


def render_chunked_translation(parts: list[str]) -> str:
    cleaned: list[str] = []
    for idx, part in enumerate(parts):
        text = part.strip()
        if not text:
            continue
        if idx > 0 and cleaned:
            text = _strip_tail_overlap(cleaned[-1], text)
        if text:
            cleaned.append(text)
    return "\n\n".join(cleaned).strip()
