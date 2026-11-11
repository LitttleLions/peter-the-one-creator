"""Nur den KDP-Umschlag (Wrap) bauen, unabhaengig vom Manuskript.

Beim Paperback-Upload haengt die erwartete Umschlaggroesse an zwei Zahlen, die
KDP aus dem Formular nimmt: Trim-Groesse und Innenseitenzahl. Weicht eine davon
ab, meldet KDP "Die erwartete Covergroesse betraegt X, die eingereichte
Dateigroesse jedoch Y" - und man iteriert ohne dieses Werkzeug ueber den
kompletten Satz.

Dieses Werkzeug erzeugt nur den Wrap: eine Seite mit Rueckseite, Ruecken und
Vorderseite in der exakten Groesse fuer Trim, Papier und Seitenzahl. Das
Titelbild kommt aus ``assets/covers/cover-print.*``.

Rechnung (KDP, creme/SW): Gesamtbreite = 2 x Trim + Ruecken + 2 x 0,125 in
Beschnitt, Gesamthoehe = Trim + 2 x 0,125 in. Ruecken = Seiten x 0,0635 mm.

Aufruf::

    python tools/build_cover.py --book die-sprache-des-anderen --page-count 332
    python tools/build_cover.py --book die-sprache-des-anderen --page-count 332 --trim-size 6x9 --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from lib.book_project import find_book as find_book_project  # noqa: E402
from lib.kdp_mapping import load_export_document  # noqa: E402
from lib.print_pdf import count_pdf_pages, render_html_to_pdf  # noqa: E402
from lib.print_spec import (  # noqa: E402
    KDP_BLEED_IN,
    kdp_spine_mm,
    load_print_spec,
)
from lib.print_wrap import render_wrap_html  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
COVER_NAMES = ("cover-print.jpg", "cover-print.jpeg", "cover-print.png", "cover-print.webp")
MAX_KDP_PAGES = 828
MIN_KDP_PAGES = 24


def find_print_cover(book_root: Path) -> Path | None:
    for name in COVER_NAMES:
        candidate = book_root / "assets" / "covers" / name
        if candidate.is_file():
            return candidate
    return None


def wrap_geometry(spec: Any, page_count: int) -> dict[str, float]:
    spine_in = kdp_spine_mm(page_count, spec.paper) / 25.4
    trim_w = spec.trim_width_in
    trim_h = spec.trim_height_in
    width = (2 * KDP_BLEED_IN) + (2 * trim_w) + spine_in
    height = trim_h + (2 * KDP_BLEED_IN)
    return {
        "spine_mm": round(spine_in * 25.4, 2),
        "spine_in": round(spine_in, 3),
        "width_in": round(width, 3),
        "height_in": round(height, 3),
        "width_mm": round(width * 25.4, 1),
        "height_mm": round(height * 25.4, 1),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Nur den KDP-Umschlag (Wrap) bauen")
    parser.add_argument("--book", required=True, help="Buch-ID")
    parser.add_argument("--page-count", type=int, help="Innenseiten laut KDP-Formular")
    parser.add_argument("--trim-size", help="5.5x8.5 oder 6x9 (Default aus config/print.yaml)")
    parser.add_argument("--paper", help="cream oder white (Default aus config/print.yaml)")
    parser.add_argument("--out", help="Zielpfad; Default: neuester Satz-Stempel im print-Ordner")
    parser.add_argument("--dry-run", action="store_true", help="nur Masse zeigen, nichts schreiben")
    args = parser.parse_args(argv)

    book = find_book_project(REPO_ROOT, args.book)
    if not book:
        print(f"Buch mit id={args.book} nicht gefunden", file=sys.stderr)
        return 2

    book_root = REPO_ROOT / book["book_root"]
    meta = load_export_document(REPO_ROOT / book["export_config"])
    overlay: dict[str, Any] = {}
    if args.trim_size:
        overlay["trim_size"] = args.trim_size
    if args.paper:
        overlay["paper"] = args.paper
    spec = load_print_spec(REPO_ROOT, meta, overlay=overlay)

    page_count = int(args.page_count or 0)
    if page_count:
        if page_count < MIN_KDP_PAGES or page_count > MAX_KDP_PAGES:
            print(
                f"WARNUNG: {page_count} Seiten liegt ausserhalb von "
                f"{MIN_KDP_PAGES}-{MAX_KDP_PAGES} (KDP-Limit)",
                file=sys.stderr,
            )

    cover = find_print_cover(book_root)
    if cover is None:
        print("Kein Druckcover gefunden (assets/covers/cover-print.*)", file=sys.stderr)
        return 2

    geometry = wrap_geometry(spec, page_count) if page_count else {}
    print(f"Trim: {spec.trim_size} ({spec.trim_width_in} x {spec.trim_height_in} in), Papier {spec.paper}")
    if geometry:
        print(
            f"Seiten: {page_count} -> Ruecken {geometry['spine_mm']} mm, "
            f"Umschlag {geometry['width_in']} x {geometry['height_in']} in "
            f"({geometry['width_mm']} x {geometry['height_mm']} mm)"
        )
    else:
        print("Ohne --page-count wird keine Groesse gerechnet.")

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    print_dir = book_root / "exports" / str(book.get("style_mode") or "") / "book" / "print"
    target = Path(args.out) if args.out else print_dir / f"cover-wrap-{stamp}-{page_count or 'ohne-seiten'}.pdf"
    if not target.is_absolute():
        target = (REPO_ROOT / target).resolve()

    if args.dry_run:
        print(f"# Dry-Run: nichts geschrieben (Ziel waere {target})")
        return 0

    if not page_count:
        print("--page-count fehlt: ohne Seitenzahl ist der Ruecken nicht bestimmbar.", file=sys.stderr)
        return 2

    title = str(meta.get("book", {}).get("title") or "")
    # Wie export_manuscript.py das ganze Dokument uebergeben: der Wrap liest
    # `book` (Titel/Autor/Summary) und `print.back_cover` (Rueckseiten-Gestaltung).
    wrap_meta = dict(meta)
    html_path = target.with_suffix(".html")
    html_text = render_wrap_html(
        meta=wrap_meta,
        cover_path=cover,
        html_path=html_path,
        spec=spec,
        page_count=page_count,
    )
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html_text, encoding="utf-8")
    render_html_to_pdf(html_path, target)

    pages = count_pdf_pages(target)
    if pages != 1:
        print(f"WARNUNG: Wrap hat {pages} Seiten, erwartet 1", file=sys.stderr)

    from pypdf import PdfReader

    box = PdfReader(str(target)).pages[0].mediabox
    width_in = float(box.width) / 72
    height_in = float(box.height) / 72
    print(f"Wrap: {target}")
    print(f"  Seiten: {pages}")
    print(f"  Groesse: {width_in:.3f} x {height_in:.3f} in ({width_in * 25.4:.1f} x {height_in * 25.4:.1f} mm)")
    expected_w = geometry["width_in"]
    expected_h = geometry["height_in"]
    if abs(width_in - expected_w) > 0.01 or abs(height_in - expected_h) > 0.01:
        print(
            f"  ABWEICHUNG: erwartet {expected_w:.3f} x {expected_h:.3f} in",
            file=sys.stderr,
        )
        return 1

    report = {
        "book_id": book.get("id"),
        "title": title,
        "cover_source": cover.relative_to(book_root).as_posix(),
        "trim_size": spec.trim_size,
        "paper": spec.paper,
        "page_count": page_count,
        "spine_mm": geometry["spine_mm"],
        "size_in": [expected_w, expected_h],
        "size_mm": [geometry["width_mm"], geometry["height_mm"]],
        "wrap_pdf": target.as_posix(),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    report_path = target.with_name(target.stem + "-report.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
