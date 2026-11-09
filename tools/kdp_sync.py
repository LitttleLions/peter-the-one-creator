"""KDP-Adapter Phase 1: Status, Login, Pull, Diff, Bind.

Spricht nur HTTP mit tools/vendor/amazon-kdp-skill. Schreibt nicht nach Amazon.
`bind` trägt eine bestätigte title_id lokal in export.yaml ein.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from lib.book_project import find_book as find_book_project
from lib.kdp_client import KdpClient, KdpClientError, ensure_kdp_server
from lib.kdp_diff import diff_listing, render_diff_markdown, write_diff
from lib.kdp_mapping import (
    KdpMatchStop,
    load_export_document,
    map_kdp_soll,
    match_kdp_title,
    upsert_amazon_join,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="KDP-Adapter Phase 1. Liest Amazon, schreibt nur lokal bei bind."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="Session-Status des Skill-Servers")
    sub.add_parser("login", help="Chromium-Login starten, wenn keine Session da ist")
    pull = sub.add_parser("pull", help="Soll bauen, Titel lesen, Ist speichern")
    pull.add_argument("--book", required=True)
    diff = sub.add_parser("diff", help="Gespeichertes Soll gegen Ist vergleichen")
    diff.add_argument("--book", required=True)
    bind = sub.add_parser("bind", help="Bestätigte title_id in export.yaml schreiben")
    bind.add_argument("--book", required=True)
    bind.add_argument("--title-id", required=True)
    bind.add_argument("--asin", default="")
    bind.add_argument("--format", choices=["kindle", "paperback"], default="kindle")
    args = parser.parse_args(argv)
    try:
        if args.command == "status":
            return cmd_status()
        if args.command == "login":
            return cmd_login()
        if args.command == "pull":
            return cmd_pull(args.book)
        if args.command == "diff":
            return cmd_diff(args.book)
        if args.command == "bind":
            return cmd_bind(args.book, args.title_id, args.asin, args.format)
    except KdpClientError as exc:
        print(f"KDP: {exc}", file=sys.stderr)
        return 1
    except KdpMatchStop as exc:
        print(str(exc), file=sys.stderr)
        for row in exc.candidates:
            print(json.dumps(row, ensure_ascii=False), file=sys.stderr)
        return 2
    return 2


def cmd_status() -> int:
    client = ensure_kdp_server(REPO_ROOT)
    payload = client.status()
    print(
        "connected={connected} loginInProgress={login} accountCreationDate={created}".format(
            connected=payload.get("connected"),
            login=payload.get("loginInProgress"),
            created=payload.get("accountCreationDate"),
        )
    )
    if payload.get("loginError"):
        print(f"loginError={payload.get('loginError')}")
    return 0


def cmd_login() -> int:
    client = ensure_kdp_server(REPO_ROOT)
    payload = client.status()
    if payload.get("connected"):
        print("Bereits verbunden. Login wird nicht erneut gestartet.")
        return 0
    if payload.get("loginInProgress"):
        print("Login läuft schon. MFA im Chromium-Fenster abschließen, danach status.")
        return 0
    client.start_login()
    print("Chromium ist offen. Anmeldung und MFA dort abschließen, danach status.")
    return 0


def cmd_pull(book_id: str) -> int:
    book = find_book_project(REPO_ROOT, book_id)
    client = ensure_kdp_server(REPO_ROOT)
    result = pull_book(book, REPO_ROOT, client)
    print(
        f"Pull {book_id}: {result['format']} title_id={result['title_id']} via={result['via']}"
    )
    print(f"Soll: {result['soll_path']}")
    print(f"Ist: {result['ist_path']}")
    print("title_id steht noch nicht automatisch in export.yaml. Speichern mit bind.")
    return 0


def cmd_diff(book_id: str) -> int:
    book = find_book_project(REPO_ROOT, book_id)
    folder = _kdp_dir(REPO_ROOT, book)
    soll_path = folder / "soll.json"
    ist_path = folder / "ist.json"
    if not soll_path.is_file() or not ist_path.is_file():
        print("Erst pull ausführen. soll.json oder ist.json fehlt.", file=sys.stderr)
        return 2
    soll = json.loads(soll_path.read_text(encoding="utf-8"))
    ist = json.loads(ist_path.read_text(encoding="utf-8"))
    fmt = str(ist.get("format") or "kindle")
    rows = diff_listing(soll, ist.get("book") or ist, fmt=fmt)
    markdown = render_diff_markdown(book_id, fmt, rows)
    diff_path = folder / "diff.md"
    write_diff(diff_path, markdown)
    print(markdown, end="")
    print(f"Diff: {diff_path}")
    return 0


def cmd_bind(book_id: str, title_id: str, asin: str, fmt: str) -> int:
    book = find_book_project(REPO_ROOT, book_id)
    path = REPO_ROOT / book["export_config"]
    original = path.read_text(encoding="utf-8")
    updated = upsert_amazon_join(original, fmt=fmt, title_id=title_id.strip(), asin=asin)
    path.write_text(updated, encoding="utf-8")
    print(f"{fmt} title_id in {path} gespeichert. Amazon wurde nicht beschrieben.")
    return 0


def pull_book(book: dict[str, Any], repo_root: Path, client: KdpClient) -> dict[str, str]:
    export_path = repo_root / book["export_config"]
    book_root = repo_root / book["book_root"]
    export = load_export_document(export_path)
    soll = map_kdp_soll(export, book_root=book_root, style=str(book.get("style_mode") or ""))
    fmt = _pull_format(soll)
    folder = _kdp_dir(repo_root, book)
    _write_json(folder / "soll.json", soll)
    status = client.status()
    if not status.get("connected"):
        raise KdpClientError("Keine KDP-Session. Zuerst login, MFA im Chromium abschließen.")
    bookshelf = client.get_json("/api/kdp/bookshelf")
    catalog = client.get_json("/api/kdp/catalog")
    cache = client.get_json("/api/kdp/metadata")
    matched = match_kdp_title(
        soll,
        fmt=fmt,
        bookshelf=bookshelf,
        catalog=catalog,
        cache=cache,
    )
    remote = client.sync_format(matched["title_id"], fmt)
    ist = {"format": fmt, "via": matched["via"], "book": remote}
    _write_json(folder / "ist.json", ist)
    return {
        "format": fmt,
        "title_id": matched["title_id"],
        "via": matched["via"],
        "soll_path": str(folder / "soll.json"),
        "ist_path": str(folder / "ist.json"),
    }


def _pull_format(soll: dict[str, Any]) -> str:
    formats = soll.get("formats") or {}
    kindle = formats.get("kindle") or {}
    paperback = formats.get("paperback") or {}
    if kindle.get("enabled", True):
        return "kindle"
    if paperback.get("enabled"):
        return "paperback"
    raise SystemExit("Weder kindle noch paperback ist in amazon: aktiv.")


def _kdp_dir(repo_root: Path, book: dict[str, Any]) -> Path:
    return repo_root / book["work_dir"] / "kdp"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
