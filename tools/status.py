"""
status.py – CLI für die peter-the-one-Pipeline
==============================================

Verwendung:
    python tools/status.py                       # Übersicht erstes Buch
    python tools/status.py --book peter-i-buch-01
    python tools/status.py list                 # Kapitel-Liste
    python tools/status.py next                 # nächstes pending Kapitel
    python tools/status.py mark 001 done --words 2100
    python tools/status.py mark 001 in_progress
    python tools/status.py mark 001 needs_review
    python tools/status.py reset 001
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# UTF-8 Output für Windows cmd
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                      errors="replace")

import yaml
from lib.status_manager import (
    BookState, load_state, save_state,
    mark_in_progress, mark_done, mark_pending,
    STATUS_DONE, STATUS_IN_PROGRESS, STATUS_NEEDS_REVIEW, STATUS_PENDING,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def find_book(book_id: str | None) -> dict:
    p = REPO_ROOT / "config" / "books.yaml"
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    books = data.get("books", [])
    if book_id is None:
        if not books:
            raise SystemExit("Keine Bücher in config/books.yaml")
        return books[0]
    for b in books:
        if b["id"] == book_id:
            return b
    raise SystemExit(f"Buch mit id={book_id} nicht gefunden")


def load_book_state(book: dict) -> tuple[BookState, Path]:
    p = REPO_ROOT / book["status_file"]
    if not p.exists():
        raise SystemExit(f"Status-Datei nicht gefunden: {p}\n"
                         f"Erst extract_chapters.py laufen lassen.")
    return load_state(p), p


def cmd_summary(args) -> int:
    book = find_book(args.book)
    state, _ = load_book_state(book)
    from lib.status_manager import summary
    print(summary(state))
    return 0


def cmd_list(args) -> int:
    book = find_book(args.book)
    state, _ = load_book_state(book)
    print(f"Buch: {state.title}")
    print(f"Regelwerk: {'AN' if state.ruleset_apply else 'AUS'}, "
          f"Stil: {state.style_mode}")
    print("-" * 80)
    print(f"{'ID':>3}  {'Status':<14}  {'Wörter':>10}  {'Titel RU'}")
    print("-" * 80)
    for c in state.chapters:
        words = c.words_target or c.words_source
        title = c.title_ru[:55]
        print(f"{c.id:>3}  {c.status:<14}  {words:>10,}  {title}")
    print("-" * 80)
    return 0


def cmd_next(args) -> int:
    book = find_book(args.book)
    state, _ = load_book_state(book)
    for c in state.chapters:
        if c.status == STATUS_PENDING:
            print(f"{c.id}  {c.title_ru}  ({c.words_source} Wörter Original)")
            return 0
    print("Keine pending Kapitel mehr.")
    return 0


def cmd_mark(args) -> int:
    book = find_book(args.book)
    state, path = load_book_state(book)
    if args.status == STATUS_IN_PROGRESS:
        mark_in_progress(state, args.chapter)
        print(f"-> {args.chapter} = in_progress")
    elif args.status == STATUS_DONE:
        mark_done(state, args.chapter, words_target=args.words or 0,
                  title_de=args.title_de or "", needs_review=False)
        print(f"-> {args.chapter} = done ({args.words or 0} Wörter)")
    elif args.status == STATUS_NEEDS_REVIEW:
        mark_done(state, args.chapter, words_target=args.words or 0,
                  title_de=args.title_de or "", needs_review=True)
        print(f"-> {args.chapter} = needs_review")
    elif args.status == STATUS_PENDING:
        mark_pending(state, args.chapter)
        print(f"-> {args.chapter} = pending")
    else:
        raise SystemExit(f"Unbekannter Status: {args.status}")
    save_state(state, path)
    return 0


def cmd_reset(args) -> int:
    book = find_book(args.book)
    state, path = load_book_state(book)
    mark_pending(state, args.chapter)
    save_state(state, path)
    print(f"-> {args.chapter} zurück auf pending")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", default=None)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("summary", help="Übersicht anzeigen")
    sub.add_parser("list", help="Kapitel-Liste anzeigen")
    sub.add_parser("next", help="Nächstes pending Kapitel")

    p_mark = sub.add_parser("mark", help="Status setzen")
    p_mark.add_argument("chapter")
    p_mark.add_argument("status", choices=[
        STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_DONE, STATUS_NEEDS_REVIEW,
    ])
    p_mark.add_argument("--words", type=int, default=0)
    p_mark.add_argument("--title-de", default="")

    p_reset = sub.add_parser("reset", help="Zurück auf pending")
    p_reset.add_argument("chapter")

    args = ap.parse_args()
    if args.cmd == "summary":
        return cmd_summary(args)
    if args.cmd == "list":
        return cmd_list(args)
    if args.cmd == "next":
        return cmd_next(args)
    if args.cmd == "mark":
        return cmd_mark(args)
    if args.cmd == "reset":
        return cmd_reset(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
