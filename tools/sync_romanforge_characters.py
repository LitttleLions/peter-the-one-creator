"""sync_romanforge_characters.py - RomanForge-Figuren in names.yaml abgleichen.

Standard ist ein Trockenlauf (nur Tabelle, keine Dateien geaendert).

Verwendung (immer mit der .venv):
    tools/sync_romanforge_characters.py --book <id> --handoff <uebergabe-id>
    tools/sync_romanforge_characters.py --book <id> --snapshot handoff.json
    tools/sync_romanforge_characters.py --book <id>          (vorhandener Spiegel)
    ... --apply     schreibt den Spiegel (bei neuem Abruf) und names.yaml
    ... --aussehen  nur Tabelle: Aussehen in RomanForge gegen visual (schreibt nichts)

Eigentum: RomanForge liefert source/rf_uid; target, aliases, type, note und status
pflegt Peter und werden nie ueberschrieben. visual folgt einem geaenderten Aussehen
aus RomanForge nur, wenn es leer oder von Hand unberuehrt ist. Siehe tools/lib/rf_characters.py.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from lib.book_project import find_book  # noqa: E402
from lib.name_registry import load_names, write_names  # noqa: E402
from lib import rf_binding as rfb  # noqa: E402
from lib import rf_characters as rfc  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_source(
    args: argparse.Namespace, book_root: Path, book_id: str = "", book_cfg: dict | None = None,
) -> tuple[str, list[dict], bool]:
    """Liefert (handoff_id, Figuren, neu_abgerufen)."""
    if args.snapshot:
        data = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
        handoff_id = str((data.get("handoff") or {}).get("id") or "datei")
        return handoff_id, rfc.normalize_characters(data.get("characters")), True
    if args.handoff:
        from lib.romanforge_client import RomanForgeConfig, get_handoff_data  # noqa: E402
        config = RomanForgeConfig.from_env()
        data = get_handoff_data(config, args.handoff)
        from lib.book_project import discover_projects  # noqa: E402
        errors = rfb.check_update(
            book_id=book_id, book_cfg=book_cfg or {}, handoff_data=data, env_url=config.base_url,
            books=[(p.id, p.config) for p in discover_projects(REPO_ROOT)],
            state_rf_ids=[], snapshot_ids=[],
        )
        if errors:
            raise SystemExit("\n".join(f"FEHLER: {message}" for message in errors))
        if "characters" not in data:
            raise SystemExit(
                "Diese Uebergabe enthaelt keine Figuren (aeltere RomanForge-Version?). "
                "Neue Uebergabe erzeugen."
            )
        return args.handoff, rfc.normalize_characters(data.get("characters")), True
    mirror = rfc.read_mirror(book_root)
    return str(mirror.get("handoff_id") or ""), rfc.normalize_characters(mirror.get("characters")), False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book", required=True, help="Buch-ID unter books/")
    parser.add_argument("--handoff", help="RomanForge-Uebergabe-ID (ROMANFORGE_URL/-API_KEY aus .env)")
    parser.add_argument("--snapshot", help="Handoff-JSON aus einer Datei (offline)")
    parser.add_argument("--apply", action="store_true", help="Aenderungen schreiben (sonst Trockenlauf)")
    parser.add_argument(
        "--force-visual",
        action="store_true",
        help=(
            "Geaendertes Aussehen aus RomanForge auch dann nach visual uebernehmen, "
            "wenn visual in peter von Hand angepasst wurde (sonst nur rf_visual_check)"
        ),
    )
    parser.add_argument("--aussehen", action="store_true",
                        help="Nur Tabelle: Aussehen in RomanForge gegen visual in names.yaml (schreibt nichts)")
    args = parser.parse_args(argv)
    if args.aussehen and args.apply:
        parser.error("--aussehen schreibt nichts und passt nicht zu --apply")

    book = find_book(REPO_ROOT, args.book)
    book_root = REPO_ROOT / "books" / args.book
    source_lang = str(book.get("source_lang") or "")
    target_lang = str(book.get("target_lang") or "")
    same_language = bool(source_lang) and source_lang == target_lang

    handoff_id, characters, fetched = _load_source(args, book_root, args.book, book)
    names_path = book_root / "names.yaml"
    entries = load_names(names_path)
    if args.aussehen:
        print(f"Buch {args.book}: Aussehen (RomanForge, Uebergabe {handoff_id[:8] or '-'}) gegen visual in names.yaml")
        print(rfc.render_appearance_report(rfc.appearance_report(entries, characters)))
        return 0
    actions = rfc.plan_sync(
        entries, characters, same_language=same_language, force_visual=args.force_visual
    )

    print(f"Buch {args.book}: {len(characters)} Figuren aus RomanForge, {len(entries)} Eintraege in names.yaml")
    print(rfc.render_plan(actions))
    if not args.force_visual and any(a.kind == rfc.APPEARANCE for a in actions):
        print(
            "\nHinweis: bei 'aussehen-geaendert' bleibt visual stehen (von Hand "
            "angepasst). Mit --force-visual wird das RomanForge-Aussehen uebernommen."
        )
    conflicts = [a for a in actions if a.kind == rfc.CONFLICT]
    if not args.apply:
        print("\nTrockenlauf - nichts geschrieben. Mit --apply uebernehmen.")
        return 1 if conflicts else 0
    if fetched:
        print(f"Spiegel: {rfc.write_mirror(book_root, handoff_id, characters)}")
    changed = [a for a in actions if a.kind not in (rfc.UNCHANGED, rfc.CONFLICT)]
    if changed:
        write_names(names_path, rfc.apply_sync(entries, actions))
        print(f"names.yaml aktualisiert ({len(changed)} Aenderungen).")
    else:
        print("names.yaml unveraendert.")
    return 1 if conflicts else 0


if __name__ == "__main__":
    raise SystemExit(main())
