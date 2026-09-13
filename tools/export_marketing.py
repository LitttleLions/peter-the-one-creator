#!/usr/bin/env python
"""
export_marketing.py
===================

Erzeugt das Marketingpaket eines Buchs aus vorhandenen Buchdaten.

Quelle:
    books/<id>/book.yaml, books/<id>/export.yaml, books/<id>/names.yaml,
    books/<id>/work/scenes/de/<style>/ und books/<id>/assets/

Ausgabe:
    books/<id>/exports/marketing/campaign.json
    books/<id>/exports/marketing/posts.md
    books/<id>/exports/marketing/youtube.md
    books/<id>/exports/marketing/media.json
    books/<id>/exports/marketing/README.md

Der Befehl veroeffentlicht nichts und spricht keine Plattform-API an. Ohne
``--provider`` entstehen keine API-Kosten: es werden nur bereits vorliegende
Texte verwendet.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import marketing_campaign as campaign  # noqa: E402
from lib import marketing_prompts as prompts  # noqa: E402
from lib.book_project import discover_projects, find_book  # noqa: E402

PROVIDERS = ("openrouter", "prompt_file", "workspace_ai")
PLANNED_FILES = (
    "campaign.json",
    "posts.md",
    "youtube.md",
    "media.json",
    "README.md",
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Marketingpaket (Texte + Kampagnenmanifest) buchbezogen exportieren."
    )
    parser.add_argument("--book", default=None, help="Buch-ID (Default: erstes Buchpaket)")
    parser.add_argument(
        "--style",
        default=None,
        help="Style-Profil fuer die Leseprobe (Default: book.yaml style_mode)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Alle Buchpakete mit marketing-Block in export.yaml bearbeiten",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Nur planen und anzeigen, nichts schreiben, kein API-Call",
    )
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="Texte neu erzeugen; erfordert --provider",
    )
    parser.add_argument(
        "--provider",
        choices=PROVIDERS,
        default=None,
        help=(
            "Texterzeugung: openrouter (bestehender Client), prompt_file "
            "(Promptdatei schreiben) oder workspace_ai (Repository-KI)"
        ),
    )
    parser.add_argument(
        "--no-texts",
        action="store_true",
        help="Texterzeugung komplett ueberspringen (nur vorhandene Texte nutzen)",
    )
    return parser.parse_args(argv)


def _print_header(book: dict[str, Any], style: str) -> None:
    print(f"=== Marketingexport: {book.get('title')} ({book.get('id')}) ===")
    print(f"Style: {style}")


def _print_state(
    amazon: dict[str, Any],
    youtube: dict[str, Any],
    songs: list[dict[str, Any]],
    enabled: bool,
) -> None:
    print(f"marketing-Block in export.yaml: {'ja' if enabled else 'nein'}")
    if amazon["url"]:
        print(
            f"Amazon-Link: {amazon['url']} (Quelle {amazon['source']}, "
            f"Syntax {amazon['syntax']}, Zuordnung: Benutzerangabe)"
        )
    else:
        print("Amazon-Link: nicht hinterlegt -> Verkaufsposts bleiben offen")
    if youtube["url"]:
        print(f"YouTube: {youtube['url']} (oeffentlich: {youtube['public']})")
    else:
        print("YouTube: noch nicht bekannt -> Songhinweis wartet auf Linkaufloesung")
    if not songs:
        print("Musikmaterial: keines hinterlegt -> Musikbestandteile entfallen")
    else:
        for song in songs:
            state = "Datei vorhanden" if song["file_exists"] else "Datei fehlt"
            print(
                f"Musikmaterial: {song['id']} ({song['title'] or 'ohne Titel'}) - {state}"
            )


def _generate(
    book: dict[str, Any],
    style: str,
    brief: dict[str, Any],
    provider: str,
    dry_run: bool,
) -> tuple[list[str], list[str]]:
    """Erzeugt bzw. plant Texte. Gibt (Meldungen, Probleme) zurueck."""
    messages: list[str] = []
    system, user = prompts.build_prompt(brief)
    if provider == "prompt_file":
        if dry_run:
            messages.append(
                "[dry-run] Promptdatei wuerde geschrieben: "
                f"{prompts.prompt_file_path(book, REPO_ROOT, style)}"
            )
        else:
            path = prompts.write_prompt_file(
                book, REPO_ROOT, style, brief, system, user
            )
            messages.append(
                f"Promptdatei geschrieben: {campaign.rel_path(REPO_ROOT, path)}"
            )
        return messages, []
    if provider == "workspace_ai":
        if dry_run:
            messages.append(
                "[dry-run] Arbeitsanweisung wuerde geschrieben: "
                f"{campaign.book_root(book, REPO_ROOT) / 'work' / 'marketing'}"
            )
            return messages, []
        path = prompts.write_workspace_order(
            book, REPO_ROOT, style, brief, system, user
        )
        payload = prompts.workspace_payload(book, brief, style)
        generated_path = prompts.write_generated(book, REPO_ROOT, payload)
        messages.append(
            f"Arbeitsanweisung geschrieben: {campaign.rel_path(REPO_ROOT, path)}"
        )
        messages.append(
            f"Textrahmen angelegt: {campaign.rel_path(REPO_ROOT, generated_path)}"
        )
        return messages, []
    if dry_run:
        messages.append("[dry-run] OpenRouter-Call wuerde ausgefuehrt (keine Kosten)")
        return messages, []
    generated, problems = prompts.generate_with_openrouter(
        book, REPO_ROOT, style, brief, system, user
    )
    path = prompts.write_generated(book, REPO_ROOT, generated)
    messages.append(f"Texte erzeugt: {campaign.rel_path(REPO_ROOT, path)}")
    return messages, problems


def run_book(book: dict[str, Any], args: argparse.Namespace) -> int:
    style = str(args.style or book.get("style_mode") or "stil-01-original")
    global_cfg = campaign.load_global_config(REPO_ROOT)
    export_data = campaign.load_export_data(book, REPO_ROOT)
    enabled = campaign.marketing_enabled(export_data)
    if args.all and not enabled:
        print(
            f"[{book.get('id')}] uebersprungen: kein top-level marketing-Block "
            "in export.yaml"
        )
        return 0

    _print_header(book, style)
    if not enabled:
        print(
            "Hinweis: kein marketing-Block in export.yaml. Es gelten die globalen "
            "Defaults; der Amazon-Link kommt aus website.amazon_url."
        )

    brief = campaign.campaign_brief(book, REPO_ROOT, style, global_cfg)
    brief_hash = campaign.source_hash(brief)
    book_root_dir = campaign.book_root(book, REPO_ROOT)
    generated = campaign.load_generated(book_root_dir)
    stale, reason = campaign.needs_regeneration(
        brief_hash, generated, force=bool(args.regenerate)
    )
    problems: list[str] = []
    messages: list[str] = []
    text_hint = ""

    if args.regenerate and not args.provider:
        print("ABBRUCH: --regenerate erfordert --provider.")
        return 2

    if args.no_texts:
        messages.append("Texterzeugung uebersprungen (--no-texts)")
    elif stale and args.provider:
        print(f"Texterzeugung: {reason} -> Provider {args.provider}")
        messages, problems = _generate(
            book, style, brief, args.provider, bool(args.dry_run)
        )
    elif stale:
        text_hint = (
            f"Texte fehlen oder sind veraltet ({reason}). Mit --provider "
            "workspace_ai|prompt_file|openrouter erzeugen."
        )
    else:
        messages.append("Vorhandene Texte werden unveraendert weiterverwendet.")

    texts = campaign.collect_texts(book_root_dir)
    manifest = campaign.build_campaign(
        book, REPO_ROOT, style, global_cfg=global_cfg, texts=texts
    )
    for message in messages:
        print(message)
    if text_hint:
        print(text_hint)
    for problem in problems:
        print(f"Warnung aus der Antwortauswertung: {problem}")
    _print_state(manifest["amazon"], manifest["youtube"], manifest["songs"], enabled)
    _print_report(manifest, book)
    return _finish(manifest, book, args)


def _print_report(manifest: dict[str, Any], book: dict[str, Any]) -> None:
    print("Beitraege:")
    for post in manifest["posts"]:
        print(
            f"  - {post['offset_label']:>5} {post['id']:<20} {post['status']:<18} "
            f"Zeichen {post['validation']['weighted_chars']}"
        )
    print("Offene Angaben:")
    if manifest["missing"]:
        for item in manifest["missing"]:
            print(
                f"  - {item['item']} ({item['status']}): betrifft "
                f"{', '.join(item['affects']) or 'kampagnenweit'}"
            )
    else:
        print("  - keine")


def _finish(
    manifest: dict[str, Any], book: dict[str, Any], args: argparse.Namespace
) -> int:
    export_dir = campaign.marketing_export_dir(book, REPO_ROOT)
    if args.dry_run:
        print(f"[dry-run] Zielordner: {campaign.rel_path(REPO_ROOT, export_dir)}")
        for name in PLANNED_FILES:
            print(f"[dry-run] wuerde schreiben: {name}")
        print("[dry-run] keine Dateien geschrieben")
        return 0
    written = campaign.write_package(manifest, export_dir)
    print("Geschrieben:")
    for path in written:
        print(f"  - {campaign.rel_path(REPO_ROOT, path)}")
    print(
        "Kampagnenstart: "
        + (manifest["campaign"]["start"] or "nicht gesetzt (relative Termine)")
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
    args = parse_args(argv)
    if args.all and args.book:
        print("ABBRUCH: --all und --book schliessen sich aus.")
        return 2
    if args.all:
        books = [
            project.as_tool_config(REPO_ROOT)
            for project in discover_projects(REPO_ROOT)
        ]
        if not books:
            print("Keine Buchpakete unter books/*/book.yaml gefunden.")
            return 1
    else:
        books = [find_book(REPO_ROOT, args.book)]
    exit_code = 0
    for index, book in enumerate(books):
        if index:
            print()
        try:
            result = run_book(book, args)
        except (ValueError, FileNotFoundError, RuntimeError) as exc:
            print(f"FEHLER bei {book.get('id')}: {exc}")
            exit_code = 1
            continue
        exit_code = exit_code or result
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())