"""rf_metadata.py - Buchangaben (Autor, Untertitel, Reihe, Band, Verlag, Herausgeber, Klappentext)
aus einer RomanForge-Uebergabe nach peter uebernehmen.

Standard ist ein Trockenlauf (nur Tabelle). Ist nichts zu tun, erscheint eine Zeile.

Verwendung (immer mit der .venv):
    tools/rf_metadata.py --book <id> --handoff <uebergabe-id>
    tools/rf_metadata.py --handoff <uebergabe-id>              (Buch ueber die Bindung in book.yaml)
    tools/rf_metadata.py --book <id> --handoff <id> --apply    schreibt book.yaml/export.yaml und den Spiegel
    ... --force-meta blurb     auch einen von Hand geaenderten Langtext uebernehmen
    tools/rf_metadata.py --book <id> --fuer-romanforge         peter-Werte als Tabelle zum Eintragen in RomanForge

Regeln: siehe tools/lib/rf_metadata.py. Der Titel wird nie geschrieben, nur gemeldet.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from lib import rf_binding as rfb  # noqa: E402
from lib import rf_characters as rfc  # noqa: E402
from lib import rf_metadata as rfm  # noqa: E402
from lib.book_project import discover_projects  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book", help="Buch-ID unter books/ (sonst ueber die Bindung der Uebergabe)")
    parser.add_argument("--handoff", help="RomanForge-Uebergabe-ID (ROMANFORGE_URL/-API_KEY aus .env)")
    parser.add_argument("--apply", action="store_true", help="Aenderungen schreiben (sonst Trockenlauf)")
    parser.add_argument("--force-meta", action="append", default=[], metavar="FELD",
                        help="Von Hand geaenderten Langtext trotzdem uebernehmen, z. B. blurb")
    parser.add_argument("--fuer-romanforge", action="store_true",
                        help="Nur Tabelle: peter-Werte der RomanForge-Felder (zum Eintragen in RomanForge)")
    args = parser.parse_args(argv)

    projects = {p.id: p for p in discover_projects(REPO_ROOT)}

    if args.fuer_romanforge:
        if not args.book or args.book not in projects:
            print("FEHLER: --fuer-romanforge braucht --book <id>.", file=sys.stderr)
            return 2
        values = rfm.current_values(projects[args.book].root)
        print(f"Buch {args.book}: Werte in peter (in RomanForge unter \"Veroeffentlichung\" eintragen)")
        print("| Feld | Wert in peter |\n|---|---|")
        for f in rfm.FIELDS:
            print(f"| {f.label} | {' '.join(values[f.rf_key].split()) or '-'} |")
        return 0

    if not args.handoff:
        print("FEHLER: --handoff <uebergabe-id> angeben.", file=sys.stderr)
        return 2
    from lib.romanforge_client import RomanForgeConfig, get_handoff_data  # noqa: E402
    config = RomanForgeConfig.from_env()
    data = get_handoff_data(config, args.handoff)

    key = rfb.handoff_key(data)
    book_id = args.book
    if not book_id:
        found = rfb.find_bound([(p.id, p.config) for p in projects.values()], key) if key else []
        if len(found) != 1:
            print(f"FEHLER: kein eindeutiges Buch fuer diese Uebergabe (Treffer: {', '.join(found) or 'keiner'}). "
                  "Erst binden: import_markdown_original.py --book <id> --handoff <id> --bind", file=sys.stderr)
            return 2
        book_id = found[0]
    if book_id not in projects:
        print(f"FEHLER: Buch '{book_id}' nicht gefunden.", file=sys.stderr)
        return 2
    project = projects[book_id]
    errors = rfb.check_update(
        book_id=book_id, book_cfg=project.config, handoff_data=data, env_url=config.base_url,
        books=[(p.id, p.config) for p in projects.values()], state_rf_ids=[], snapshot_ids=[],
    )
    if errors:
        for message in errors:
            print(f"FEHLER: {message}", file=sys.stderr)
        return 2

    unknown = [name for name in args.force_meta if name not in rfm.FIELD_BY_KEY]
    if unknown:
        print(f"FEHLER: unbekanntes Feld fuer --force-meta: {', '.join(unknown)}", file=sys.stderr)
        return 2

    book_root = project.root
    mirror = rfm.read_mirror(book_root)
    actions = rfm.plan_metadata(rfm.rf_values(data), rfm.current_values(book_root), mirror["adopted"])
    print(f"Buch {book_id}: Metadaten (RomanForge, Uebergabe {args.handoff[:8]}) gegen book.yaml/export.yaml")
    print(rfm.render_report(actions))
    todo = [a for a in actions if a.kind in (rfm.SET, rfm.FOLLOWED, rfm.ADOPT)
            or (a.kind == rfm.DIVERGED and a.rf_key in args.force_meta)]
    if not args.apply:
        if todo:
            print("\nTrockenlauf - nichts geschrieben. Mit --apply uebernehmen.")
        return 0
    notes = rfm.apply_actions(book_root, actions, args.handoff, force=set(args.force_meta),
                              adopted=mirror["adopted"])
    expose_path = rfc.write_expose(book_root, args.handoff, data.get("expose"))
    print(f"Geschrieben: {len([a for a in todo if a.kind != rfm.ADOPT])} Felder, "
          f"{len([a for a in todo if a.kind == rfm.ADOPT])} angeglichen; Spiegel {rfm.mirror_path(book_root)}")
    if expose_path:
        print(f"Exposé-Vorlage aktualisiert: {expose_path} (nicht ins Buch uebernommen)")
    for note in notes:
        print(note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
