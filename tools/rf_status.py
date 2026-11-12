"""rf_status.py - ein Befehl fuer den ganzen Abgleich mit einer RomanForge-Uebergabe (nur lesen).

Prueft die feste Bindung (Instanz, Projekt-ID, Eindeutigkeit), zeigt Kapitelvergleich, Figuren und
Buchangaben jeweils als Trockenlauf und legt eine Kopie der Uebergabe-Angaben (ohne Kapiteltext) unter
work/imports/romanforge/runs/<stempel>/handoff-meta.json ab. Es wird sonst nichts geschrieben.

Verwendung (immer mit der .venv):
    tools/rf_status.py --handoff <uebergabe-id>              Buch ueber die Bindung in book.yaml
    tools/rf_status.py --book <id> --handoff <uebergabe-id>
    ... --no-archive     auch das Archiv weglassen

Uebernommen wird danach einzeln und nur auf Freigabe:
    Kapitel:  import_markdown_original.py --book <id> --handoff <id> --accept 001,002 (max. 5)
    Figuren:  sync_romanforge_characters.py --book <id> --handoff <id> --apply
    Angaben:  rf_metadata.py --book <id> --handoff <id> --apply
Exit-Code: 0 in Ordnung, 1 Figuren-Konflikt, 2 Bindung/Zugang falsch.
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

import import_markdown_original as imp  # noqa: E402
from lib import rf_binding as rfb  # noqa: E402
from lib import rf_characters as rfc  # noqa: E402
from lib import rf_metadata as rfm  # noqa: E402
from lib.book_project import discover_projects  # noqa: E402
from lib.name_registry import load_names  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent


def archive_meta(book_root: Path, data: dict) -> Path:
    """Uebergabe-Angaben ohne Kapiteltext ablegen (Stand von Figuren, Buchangaben, Kapitel-IDs)."""
    slim = {k: v for k, v in data.items() if k != "chapters"}
    slim["chapters"] = [
        {k: v for k, v in chapter.items() if k != "content"} for chapter in data.get("chapters") or []
    ]
    run_dir = book_root / "work" / "imports" / "romanforge" / "runs" / imp.stamp_now()
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "handoff-meta.json"
    path.write_text(json.dumps(slim, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--handoff", required=True, help="RomanForge-Uebergabe-ID (ROMANFORGE_URL/-API_KEY aus .env)")
    parser.add_argument("--book", help="Buch-ID unter books/ (sonst ueber die Bindung der Uebergabe)")
    parser.add_argument("--no-archive", action="store_true", help="Keine Kopie der Uebergabe-Angaben ablegen")
    args = parser.parse_args(argv)

    from lib.romanforge_client import RomanForgeConfig, chapter_rf_ids, export_text_from_data, get_handoff_data  # noqa: E402

    config = RomanForgeConfig.from_env()
    data = get_handoff_data(config, args.handoff)
    projects = {p.id: p for p in discover_projects(REPO_ROOT)}
    books = [(p.id, p.config) for p in projects.values()]

    key = rfb.handoff_key(data)
    if key is None:
        print("FEHLER: Uebergabe nennt keine Instanz oder Projekt-ID.", file=sys.stderr)
        return 2
    book_id = args.book
    if not book_id:
        found = rfb.find_bound(books, key)
        if len(found) != 1:
            print(f"FEHLER: kein eindeutiges Buch fuer {key[0]} Projekt {key[1]} (Treffer: {', '.join(found) or 'keiner'}). "
                  "Neues Buch: import_markdown_original.py --new --handoff <id>; "
                  "bestehendes: --book <id> --handoff <id> --bind.", file=sys.stderr)
            return 2
        book_id = found[0]
    if book_id not in projects:
        print(f"FEHLER: Buch '{book_id}' nicht gefunden.", file=sys.stderr)
        return 2
    project = projects[book_id]
    book_root, book_cfg = project.root, project.config

    export_text = export_text_from_data(data)
    export_ids = chapter_rf_ids(data)
    state = imp.load_state(imp.state_path_for(book_root))
    state_ids = [str(c["rf_id"]) for c in (state.get("chapters") or {}).values()
                 if isinstance(c, dict) and c.get("rf_id")]
    errors = rfb.check_update(
        book_id=book_id, book_cfg=book_cfg, handoff_data=data, env_url=config.base_url,
        books=books, state_rf_ids=state_ids, snapshot_ids=[rid for rid in export_ids if rid],
    )
    if errors:
        for message in errors:
            print(f"FEHLER: {message}", file=sys.stderr)
        return 2

    title = str((data.get("project") or {}).get("title") or book_id)
    print(f"# RomanForge-Status: {title} -> Buch '{book_id}' (Projekt {key[1]}, Uebergabe {args.handoff[:8]}, "
          f"Modus {data.get('mode')})\n")

    # 1) Kapitel
    print("## Kapitel (nur Bericht)")
    chapters = imp.split_chapters(export_text)
    if export_ids is not None and len(export_ids) != len(chapters):
        export_ids = None
    if not (state.get("chapters")):
        print("state.yaml fehlt oder ist leer: Kapitelvergleich braucht --baseline "
              "(import_markdown_original.py --compare). Uebersprungen.")
        chapter_note = "Kapitelvergleich uebersprungen"
    else:
        style = str(book_cfg.get("style_mode") or "stil-01-original")
        imp.cmd_compare(
            book_title=str(book_cfg.get("title") or book_id), book_root=book_root, style=style,
            chapters=chapters, state=state, source_baseline={}, export_rf_ids=export_ids,
        )
        chapter_note = f"{len(chapters)} Kapitel in der Uebergabe"

    # 2) Figuren
    print("\n## Figuren (Trockenlauf)")
    characters = rfc.normalize_characters(data.get("characters"))
    entries = load_names(book_root / "names.yaml")
    same_language = bool(book_cfg.get("source_lang")) and book_cfg.get("source_lang") == book_cfg.get("target_lang")
    actions = rfc.plan_sync(entries, characters, same_language=same_language)
    print(f"{len(characters)} Figuren aus RomanForge, {len(entries)} Eintraege in names.yaml")
    print(rfc.render_plan(actions))
    if any(a.kind == rfc.APPEARANCE for a in actions):
        print("\nAussehen (RomanForge gegen visual):")
        print(rfc.render_appearance_report(rfc.appearance_report(entries, characters)))
    conflicts = [a for a in actions if a.kind == rfc.CONFLICT]

    # 3) Buchangaben
    print("\n## Buchangaben (Trockenlauf)")
    meta_actions = rfm.plan_metadata(
        rfm.rf_values(data), rfm.current_values(book_root), rfm.read_mirror(book_root)["adopted"])
    print(rfm.render_report(meta_actions))

    # 4) Archiv
    if not args.no_archive:
        print(f"\nArchiv: {archive_meta(book_root, data)}")

    figure_todo = [a for a in actions if a.kind not in (rfc.UNCHANGED, rfc.CONFLICT)]
    meta_todo = [a for a in meta_actions if a.kind in (rfm.SET, rfm.FOLLOWED, rfm.ADOPT, rfm.DIVERGED)]
    print("\n## Zusammenfassung")
    print(f"- Kapitel: {chapter_note}; Uebernahme nur auf Freigabe (--accept, max. 5 pro Lauf)")
    print(f"- Figuren: {len(figure_todo)} Aenderungen, {len(conflicts)} Konflikte"
          + (" -> sync_romanforge_characters.py ... --apply" if figure_todo else ""))
    print(f"- Buchangaben: {len(meta_todo)} offen" + (" -> rf_metadata.py ... --apply" if meta_todo else ""))
    print("Nichts uebernommen. Jede Uebernahme einzeln und erst nach ausdruecklicher Freigabe.")
    return 1 if conflicts else 0


if __name__ == "__main__":
    raise SystemExit(main())
