"""
migrate_book_projects.py
========================

Migriert die alte verteilte Struktur in Buchpakete unter books/<book-id>/.

Vorher immer pruefen:
    python tools/migrate_book_projects.py --dry-run

Echter Lauf:
    python tools/migrate_book_projects.py
"""

from __future__ import annotations

import argparse
import io
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).parent))

from lib.book_project import write_yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
VALID_BOOK_IDS = {"peter-i-buch-01", "anna-karenina"}


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def move_file(source: Path, target: Path, dry_run: bool, moves: list[str]) -> None:
    if not source.exists():
        return
    moves.append(f"{rel(source)} -> {rel(target)}")
    if dry_run:
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise RuntimeError(f"Ziel existiert bereits: {target}")
    shutil.move(str(source), str(target))


def conflict_target(book_root: Path, source: Path) -> Path:
    root = book_root / "work" / "legacy" / "migration-conflicts"
    target = root / source.name
    idx = 2
    while target.exists():
        target = root / f"{source.stem}-{idx}{source.suffix}"
        idx += 1
    return target


def merge_dir_contents(source: Path, target: Path, dry_run: bool, moves: list[str], book_root: Path) -> None:
    if not source.exists():
        return
    for item in sorted(source.iterdir(), key=lambda p: p.name.lower()):
        dest = target / item.name
        if item.is_dir():
            if dest.exists() and dest.is_dir():
                merge_dir_contents(item, dest, dry_run, moves, book_root)
            elif dest.exists():
                ctarget = conflict_target(book_root, item)
                moves.append(f"{rel(item)} -> {rel(ctarget)}  [Konflikt]")
                if not dry_run:
                    ctarget.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(item), str(ctarget))
            else:
                moves.append(f"{rel(item)} -> {rel(dest)}")
                if not dry_run:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(item), str(dest))
        else:
            if dest.exists():
                ctarget = conflict_target(book_root, item)
                moves.append(f"{rel(item)} -> {rel(ctarget)}  [Konflikt]")
                if not dry_run:
                    ctarget.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(item), str(ctarget))
            else:
                moves.append(f"{rel(item)} -> {rel(dest)}")
                if not dry_run:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(item), str(dest))


def ensure_dirs(book_root: Path, dry_run: bool) -> None:
    dirs = [
        "source",
        "assets/covers",
        "styles",
        "work/chapters",
        "work/scenes/ru",
        "work/scenes/de",
        "work/assembled",
        "work/prompts",
        "work/style-tests",
        "work/legacy",
        "exports",
        "status/logs",
    ]
    if dry_run:
        return
    for item in dirs:
        (book_root / item).mkdir(parents=True, exist_ok=True)


def export_config_for(book: dict[str, Any], legacy_export: dict[str, Any]) -> dict[str, Any]:
    defaults = legacy_export.get("defaults", {}) or {}
    old_book = (legacy_export.get("books", {}) or {}).get(book["id"], {}) or {}
    old_cover = old_book.get("cover", {}) or {}
    image_path = ""
    mode = old_cover.get("mode", "placeholder")
    if book["id"] == "peter-i-buch-01":
        mode = "image"
        image_path = "assets/covers/peteri.png"
    if book["id"] == "anna-karenina":
        mode = "image"
        image_path = "assets/covers/annakarenina.png"
    return {
        "defaults": defaults,
        "book": {
            "title": old_book.get("title") or book.get("title", ""),
            "subtitle": old_book.get("subtitle", ""),
            "author": old_book.get("author") or book.get("author", ""),
            "language": old_book.get("language", "de-DE"),
            "publisher": old_book.get("publisher", ""),
            "rights": old_book.get("rights", ""),
            "description": old_book.get("description", ""),
            "cover": {
                "mode": mode,
                "image_path": image_path,
            },
        },
    }


def book_yaml_for(book: dict[str, Any], source_name: str) -> dict[str, Any]:
    return {
        "id": book["id"],
        "title": book.get("title", ""),
        "author": book.get("author", ""),
        "source_path": f"source/{source_name}",
        "source_lang": book.get("source_lang", "ru"),
        "target_lang": book.get("target_lang", "de"),
        "ruleset_path": book.get("ruleset_path", ""),
        "ruleset_apply": bool(book.get("ruleset_apply", False)),
        "style_mode": book.get("style_mode", "stil-01-original"),
        "work_dir": "work",
        "exports_dir": "exports",
        "status_file": "status/status.json",
        "log_dir": "status/logs",
        "styles_dir": "styles",
        "assets_dir": "assets",
        "names_file": "names.yaml",
        "structure": {
            "mode": "chapter_as_scene" if book["id"] == "anna-karenina" else "scenes",
            "label": "Kapitel als Szenen" if book["id"] == "anna-karenina" else "Kapitel mit Szenen",
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
        "naming_convention": book.get("naming_convention") or {"style": "", "example": []},
        "notes": book.get("notes", ""),
        "ai": book.get("ai") or {},
    }


def copy_styles(book_root: Path, dry_run: bool, moves: list[str]) -> None:
    styles_root = REPO_ROOT / "styles"
    if not styles_root.exists():
        return
    for style in sorted(styles_root.glob("*.md")):
        target = book_root / "styles" / style.name
        if target.exists():
            continue
        moves.append(f"{rel(style)} -> {rel(target)}  [Kopie]")
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(style, target)


def migrate_book(book: dict[str, Any], legacy_export: dict[str, Any], dry_run: bool, moves: list[str]) -> None:
    book_id = book["id"]
    book_root = REPO_ROOT / "books" / book_id
    ensure_dirs(book_root, dry_run)

    source = REPO_ROOT / str(book.get("source_path", ""))
    source_name = source.name
    move_file(source, book_root / "source" / source_name, dry_run, moves)

    if book_id == "peter-i-buch-01":
        extra_source = REPO_ROOT / "books" / "Peter I - Buch 01 - royallib.ru.rtf"
        move_file(extra_source, book_root / "source" / extra_source.name, dry_run, moves)
        move_file(REPO_ROOT / "assets" / "covers" / "peteri.png", book_root / "assets" / "covers" / "peteri.png", dry_run, moves)
    if book_id == "anna-karenina":
        move_file(
            REPO_ROOT / "assets" / "books" / "anna-karenina" / "covers" / "annakarenina.png",
            book_root / "assets" / "covers" / "annakarenina.png",
            dry_run,
            moves,
        )

    output_dir = REPO_ROOT / str(book.get("output_dir", ""))
    if output_dir.exists():
        exports_dir = output_dir / "exports"
        merge_dir_contents(exports_dir, book_root / "exports", dry_run, moves, book_root)
        for item in sorted(output_dir.iterdir(), key=lambda p: p.name.lower()):
            if item.name == "exports":
                continue
            if item.is_dir():
                merge_dir_contents(item, book_root / "work" / item.name, dry_run, moves, book_root)
            else:
                target = book_root / "work" / "legacy" / item.name
                move_file(item, target, dry_run, moves)

    status_file = REPO_ROOT / str(book.get("status_file", ""))
    move_file(status_file, book_root / "status" / "status.json", dry_run, moves)
    log_dir = REPO_ROOT / str(book.get("log_dir", ""))
    merge_dir_contents(log_dir, book_root / "status" / "logs", dry_run, moves, book_root)

    copy_styles(book_root, dry_run, moves)

    if dry_run:
        moves.append(f"[write] {rel(book_root / 'book.yaml')}")
        moves.append(f"[write] {rel(book_root / 'export.yaml')}")
    else:
        if not (book_root / "book.yaml").exists():
            write_yaml(book_root / "book.yaml", book_yaml_for(book, source_name))
        if not (book_root / "export.yaml").exists():
            write_yaml(book_root / "export.yaml", export_config_for(book, legacy_export))


def migrate_legacy_configs(dry_run: bool, moves: list[str]) -> None:
    legacy_root = REPO_ROOT / "config" / "legacy"
    for name in ("books.yaml", "export.yaml"):
        source = REPO_ROOT / "config" / name
        if not source.exists():
            continue
        target = legacy_root / name
        if target.exists():
            target = legacy_root / f"{source.stem}-pre-book-packages{source.suffix}"
        move_file(source, target, dry_run, moves)


def write_skipped_registry(books: list[dict[str, Any]], dry_run: bool, moves: list[str]) -> None:
    skipped = [book for book in books if book.get("id") not in VALID_BOOK_IDS]
    if not skipped:
        return
    target = REPO_ROOT / "config" / "legacy" / "skipped-book-registries.yaml"
    moves.append(f"[write] {rel(target)}")
    if not dry_run:
        write_yaml(target, {"skipped": skipped})


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description="Migriert Buchdaten in books/<id>/ Pakete.")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    books_data = load_yaml(REPO_ROOT / "config" / "books.yaml")
    legacy_export = load_yaml(REPO_ROOT / "config" / "export.yaml")
    books = books_data.get("books", [])
    if not books:
        print("Keine alte config/books.yaml mit Buechern gefunden.")
        return 1

    moves: list[str] = []
    for book in books:
        if book.get("id") not in VALID_BOOK_IDS:
            continue
        migrate_book(book, legacy_export, args.dry_run, moves)
    write_skipped_registry(books, args.dry_run, moves)
    migrate_legacy_configs(args.dry_run, moves)

    print("Migrationsplan:" if args.dry_run else "Migration ausgefuehrt:")
    for item in moves:
        print(f"  {item}")
    if args.dry_run:
        print("(dry-run: keine Dateien geschrieben oder verschoben)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
