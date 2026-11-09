#!/usr/bin/env python3
"""Erzeugt/aktualisiert JPEG-Exportkopien fuer Asset-Bilder.

- PNG-Originale und ``*_alt.jpg``-Archive bleiben erhalten.
- Vor dem Ueberschreiben eines Export-JPG wird ggf. ``stem_alt.jpg`` angelegt
  (aus PNG in hoher Qualitaet, sonst Kopie des bisherigen JPG).
- Quelle bevorzugt PNG, sonst ``*_alt.jpg``, sonst vorhandenes JPEG.
- Ziel ist immer ``stem.jpg`` (Export bevorzugt .jpg vor .png).
- Cover nutzt grosszuegigere Masse aus book.yaml ``image_processing.cover``.
- ``--source master`` liest stattdessen die Druckoriginale aus
  ``assets/master/``; geschrieben wird weiter nach ``assets/chapter`` bzw.
  ``assets/scene``. Die Master-Ebene ist nie Ziel eines Laufs.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from lib.asset_images import (  # noqa: E402
    MASTER_DIRNAME,
    discover_export_assets,
    is_master_path,
    load_cover_processing,
    load_illustration_processing,
    plan_conversions,
    preserve_existing_jpeg,
    save_as_jpeg,
)
from lib.book_project import find_book as find_book_project  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Asset-Bilder als kompakte JPEG-Exportkopien speichern "
            "(PNG bleibt erhalten; bestehende JPGs werden nachgezogen)."
        )
    )
    parser.add_argument("--book", required=True, help="Buch-ID, z. B. die-dritte-chronik")
    parser.add_argument(
        "--scope",
        choices=("all", "cover", "chapter", "scene"),
        default="all",
        help="Welche Asset-Typen verarbeiten (Default: all)",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Vorhandene .jpg nicht neu schreiben (nur fehlende Sidecars)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help=argparse.SUPPRESS,  # legacy no-op: rewrite is now default
    )
    parser.add_argument(
        "--include-test",
        action="store_true",
        help="Auch assets/chapter/test/* einbeziehen",
    )
    parser.add_argument(
        "--source",
        choices=("auto", "master"),
        default="auto",
        help=(
            "auto = PNG / *_alt.jpg / vorhandenes JPEG wie bisher; "
            f"master = Druckoriginale aus assets/{MASTER_DIRNAME}/ als Quelle "
            "(Ziel bleibt assets/chapter bzw. assets/scene)"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Nur planen, keine Dateien schreiben",
    )
    return parser.parse_args()


def format_kb(num_bytes: int) -> str:
    return f"{num_bytes / 1024:.1f} KB"


def main() -> int:
    args = parse_args()
    book = find_book_project(REPO_ROOT, args.book)
    book_root = REPO_ROOT / str(book["book_root"])
    ill = load_illustration_processing(book)
    cov = load_cover_processing(book)

    include_cover = args.scope in ("all", "cover")
    include_chapter = args.scope in ("all", "chapter")
    include_scene = args.scope in ("all", "scene")

    from_master = args.source == "master"
    assets = discover_export_assets(
        book_root,
        include_cover=include_cover,
        include_chapter=include_chapter,
        include_scene=include_scene,
        include_test=args.include_test,
        illustration_processing=ill,
        cover_processing=cov,
        from_master=from_master,
    )
    # Sicherheitsnetz: die Druckoriginale duerfen nie ueberschrieben werden.
    master_targets = [i for i in assets if is_master_path(i.jpeg_target)]
    if master_targets:
        raise SystemExit(
            "Abbruch: Ziel im Master-Ordner gefunden: "
            + ", ".join(str(t.jpeg_target) for t in master_targets)
        )
    todo, skipped = plan_conversions(assets, skip_existing=args.skip_existing)

    print(f"Buch: {args.book}")
    print(f"Quelle: {'assets/' + MASTER_DIRNAME if from_master else 'PNG / *_alt.jpg / JPEG'}")
    print(
        "Kapitel/Szenen: "
        f"JPEG q{ill.get('jpeg_quality')} "
        f"max {ill.get('max_width')}x{ill.get('max_height')}"
    )
    print(
        "Cover: "
        f"JPEG q{cov.get('jpeg_quality')} "
        f"max {cov.get('max_width')}x{cov.get('max_height')}"
    )
    print(
        f"Gefunden: {len(assets)} Assets | geplant: {len(todo)} | "
        f"uebersprungen: {len(skipped)}"
    )
    if skipped:
        for item in skipped:
            rel = item.source.relative_to(book_root)
            print(f"  skip  {rel} -> {item.jpeg_target.name}")

    if not todo:
        print("Nichts zu tun.")
        return 0

    wrote = 0
    for item in todo:
        rel = item.source.relative_to(book_root)
        target_rel = item.jpeg_target.relative_to(book_root)
        via = "png" if item.source.suffix.lower() == ".png" else "jpg"
        result_alt = None if args.dry_run else preserve_existing_jpeg(
            item.source, item.jpeg_target, item.processing
        )
        if args.dry_run:
            print(
                f"  dry   [{item.name}/{via}] {rel} -> {target_rel} "
                f"(q{item.processing.get('jpeg_quality')}, "
                f"max {item.processing.get('max_width')}x"
                f"{item.processing.get('max_height')})"
            )
            continue
        if result_alt is not None:
            alt_rel = result_alt.relative_to(book_root)
            print(f"  keep  [{item.name}] Archiv -> {alt_rel}")
        result = save_as_jpeg(item.source, item.jpeg_target, item.processing)
        wrote += 1
        w0, h0 = result["size_before"]
        w1, h1 = result["size_after"]
        print(
            f"  write [{item.name}/{via}] {rel} -> {target_rel} "
            f"{w0}x{h0}->{w1}x{h1} "
            f"{format_kb(result['bytes_source'])} -> "
            f"{format_kb(result['bytes_dest'])}"
        )

    if args.dry_run:
        print(f"Dry-run: {len(todo)} JPEG-Exportkopien wuerden geschrieben.")
    else:
        print(
            f"Fertig: {wrote} JPEG-Exportkopien geschrieben. "
            "PNG- und *_alt.jpg-Archive unveraendert."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
