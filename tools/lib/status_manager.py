"""
Status-Manager für peter-the-one
=================================

Verwaltet die Status-JSON-Dateien pro Buch.
Status pro Kapitel: pending, in_progress, done, needs_review.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional


STATUS_PENDING = "pending"
STATUS_IN_PROGRESS = "in_progress"
STATUS_DONE = "done"
STATUS_NEEDS_REVIEW = "needs_review"


@dataclass
class ChapterState:
    id: str
    title_ru: str = ""
    title_de: str = ""
    status: str = STATUS_PENDING
    words_source: int = 0
    words_target: int = 0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    needs_review: bool = False
    notes: str = ""


@dataclass
class BookState:
    book_id: str
    title: str
    source: str
    source_lang: str
    target_lang: str
    ruleset: str
    ruleset_apply: bool
    style_mode: str
    created_at: str
    updated_at: str
    chapters: List[ChapterState] = field(default_factory=list)

    def to_json(self) -> str:
        d = asdict(self)
        return json.dumps(d, ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, s: str) -> "BookState":
        d = json.loads(s)
        chs = [ChapterState(**c) for c in d.pop("chapters", [])]
        return cls(chapters=chs, **d)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def new_book_state(book_cfg: dict) -> BookState:
    """Erzeugt einen frischen BookState aus einem book_cfg-Dict."""
    return BookState(
        book_id=book_cfg["id"],
        title=book_cfg["title"],
        source=book_cfg["source_path"],
        source_lang=book_cfg["source_lang"],
        target_lang=book_cfg["target_lang"],
        ruleset=book_cfg.get("ruleset_path", ""),
        ruleset_apply=book_cfg.get("ruleset_apply", True),
        style_mode=book_cfg.get("style_mode", "stylized"),
        created_at=now_iso(),
        updated_at=now_iso(),
    )


def save_state(state: BookState, path: str | Path) -> None:
    state.updated_at = now_iso()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(state.to_json(), encoding="utf-8")


def load_state(path: str | Path) -> BookState:
    return BookState.from_json(Path(path).read_text(encoding="utf-8"))


def chapter_index(state: BookState, chapter_id: str) -> int:
    for i, c in enumerate(state.chapters):
        if c.id == chapter_id:
            return i
    raise KeyError(chapter_id)


def mark_in_progress(state: BookState, chapter_id: str) -> None:
    i = chapter_index(state, chapter_id)
    state.chapters[i].status = STATUS_IN_PROGRESS
    state.chapters[i].started_at = now_iso()


def mark_done(state: BookState, chapter_id: str, words_target: int = 0,
              title_de: str = "", needs_review: bool = False) -> None:
    i = chapter_index(state, chapter_id)
    ch = state.chapters[i]
    ch.status = STATUS_NEEDS_REVIEW if needs_review else STATUS_DONE
    ch.completed_at = now_iso()
    ch.words_target = words_target
    ch.needs_review = needs_review
    if title_de:
        ch.title_de = title_de


def mark_pending(state: BookState, chapter_id: str) -> None:
    i = chapter_index(state, chapter_id)
    state.chapters[i].status = STATUS_PENDING


def add_chapter(state: BookState, chapter: ChapterState) -> None:
    if any(c.id == chapter.id for c in state.chapters):
        raise ValueError(f"chapter {chapter.id} existiert bereits")
    state.chapters.append(chapter)


def summary(state: BookState) -> str:
    total = len(state.chapters)
    done = sum(1 for c in state.chapters if c.status == STATUS_DONE)
    review = sum(1 for c in state.chapters if c.status == STATUS_NEEDS_REVIEW)
    prog = sum(1 for c in state.chapters if c.status == STATUS_IN_PROGRESS)
    pending = sum(1 for c in state.chapters if c.status == STATUS_PENDING)
    pct = (done + review) / total * 100 if total else 0
    return (f"Buch: {state.title}\n"
            f"Stilmodus: {state.style_mode}, Regelwerk: "
            f"{'AN' if state.ruleset_apply else 'AUS'}\n"
            f"Fortschritt: {done + review}/{total} ({pct:.1f}%)  "
            f"[done: {done}, review: {review}, in_progress: {prog}, "
            f"pending: {pending}]")
