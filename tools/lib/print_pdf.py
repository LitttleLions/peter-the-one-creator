"""Playwright-Render, Bundsteg-Iteration, Kolumnentitel/Folios und Print-Report."""

from __future__ import annotations

import io
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from lib.print_css import ILLUSTRATION_MAX_WIDTH_RATIO, write_paperback_css
from lib.print_spec import GUTTER_MAX_PASSES, PrintSpec, kdp_gutter_band

FRONTMATTER_CLASS_RE = re.compile(r'class="[^"]*frontmatter-page')


def count_frontmatter_sections(html: str) -> int:
    return len(FRONTMATTER_CLASS_RE.findall(html))


def count_export_words(chapters: list[Any]) -> int:
    total = 0
    for chapter in chapters:
        for scene in getattr(chapter, "scenes", []) or []:
            total += len(str(getattr(scene, "text", "") or "").split())
    return total


def count_pdf_pages(path: Path) -> int:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    return len(reader.pages)


def render_html_to_pdf(html_path: Path, pdf_path: Path) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright ist fuer den PDF-Export nicht installiert. "
            "Bitte `pip install -r requirements.txt` und danach "
            "`python -m playwright install chromium` ausfuehren."
        ) from exc

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(html_path.resolve().as_uri(), wait_until="load")
            try:
                page.evaluate("() => document.fonts.ready")
            except Exception:
                pass
            page.pdf(
                path=str(pdf_path),
                print_background=True,
                prefer_css_page_size=True,
                outline=True,
                tagged=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            )
        finally:
            browser.close()


def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _helvetica_overlay_pdf(
    width_pt: float,
    height_pt: float,
    x_pt: float,
    y_pt: float,
    text: str,
    font_size_pt: float = 9.0,
) -> bytes:
    """Einseitiges PDF mit einem Helvetica-String (ASCII/WinAnsi, z. B. Folios)."""
    content = (
        f"BT /F1 {font_size_pt:.2f} Tf {x_pt:.2f} {y_pt:.2f} Td "
        f"({_pdf_escape(text)}) Tj ET\n"
    )
    content_bytes = content.encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            f"<< /Type /Page /Parent 2 0 R "
            f"/MediaBox [0 0 {width_pt:.2f} {height_pt:.2f}] "
            f"/Resources << /Font << /F1 4 0 R >> >> "
            f"/Contents 5 0 R >>"
        ).encode("latin-1"),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length %d >>\nstream\n" % len(content_bytes) + content_bytes + b"\nendstream",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out.extend(f"{index} 0 obj\n".encode("latin-1"))
        out.extend(body)
        out.extend(b"\nendobj\n")
    xref_pos = len(out)
    xref = [b"xref\n", f"0 {len(objects) + 1}\n".encode("latin-1"), b"0000000000 65535 f \n"]
    for offset in offsets[1:]:
        xref.append(f"{offset:010d} 00000 n \n".encode("latin-1"))
    trailer = (
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n"
    ).encode("latin-1")
    out.extend(b"".join(xref))
    out.extend(trailer)
    return bytes(out)


def _render_header_stamp(
    spec: PrintSpec,
    work_dir: Path,
    *,
    side: str,
    label: str,
    side_margin_mm: float,
) -> Path:
    """Leere Trim-Seite mit Kolumnentitel (Garamond via @font-face)."""
    from lib.print_css import css_asset_url

    html_path = work_dir / f"header-stamp-{side}.html"
    pdf_path = work_dir / f"header-stamp-{side}.pdf"
    font_url = css_asset_url(spec.font_regular_path, html_path)
    family = spec.font_family
    align = "left" if side == "even" else "right"
    escaped = (
        label.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )
    html = (
        "<!doctype html><html><head><meta charset='utf-8' />"
        "<style>"
        f"@font-face {{ font-family: '{family}'; "
        f"src: url('{font_url}') format('truetype'); font-style: normal; }}"
        f"@page {{ size: {spec.trim_css()}; margin: 0; }}"
        "html, body { margin: 0; padding: 0; }"
        f".running {{ position: absolute; top: 8mm; "
        f"left: {side_margin_mm:.2f}mm; right: {side_margin_mm:.2f}mm; "
        f"font-family: '{family}', serif; font-size: 8.5pt; letter-spacing: 0.04em; "
        f"text-align: {align}; color: #222; }}"
        "</style></head><body>"
        f"<div class='running'>{escaped}</div>"
        "</body></html>"
    )
    html_path.write_text(html, encoding="utf-8")
    render_html_to_pdf(html_path, pdf_path)
    return pdf_path


def _header_label(kind: str, author: str, title: str) -> str:
    if kind == "author":
        return author
    if kind == "title":
        return title
    return title


def stamp_running_matter(
    pdf_path: Path,
    spec: PrintSpec,
    *,
    author: str,
    title: str,
    skip_pages: int,
    work_dir: Path,
    side_margin_mm: float,
) -> None:
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(str(pdf_path))
    page_count = len(reader.pages)
    if page_count == 0:
        return

    even_label = _header_label(spec.running_header_left, author, title)
    odd_label = _header_label(spec.running_header_right, author, title)
    even_stamp_path = _render_header_stamp(
        spec, work_dir, side="even", label=even_label, side_margin_mm=side_margin_mm,
    )
    odd_stamp_path = _render_header_stamp(
        spec, work_dir, side="odd", label=odd_label, side_margin_mm=side_margin_mm,
    )
    even_stamp = PdfReader(str(even_stamp_path)).pages[0]
    odd_stamp = PdfReader(str(odd_stamp_path)).pages[0]

    width_pt = spec.trim_width_in * 72
    height_pt = spec.trim_height_in * 72
    margin_pt = side_margin_mm * 72 / 25.4
    folio_y = 10 * 72 / 25.4
    skip = max(0, int(skip_pages))

    writer = PdfWriter()
    for index, page in enumerate(reader.pages):
        page_no = index + 1
        if page_no > skip:
            stamp = odd_stamp if page_no % 2 else even_stamp
            page.merge_page(stamp)
            folio = str(page_no)
            if page_no % 2:
                folio_x = width_pt - margin_pt - (5.0 * len(folio))
            else:
                folio_x = margin_pt
            overlay = PdfReader(
                io.BytesIO(
                    _helvetica_overlay_pdf(
                        width_pt, height_pt, folio_x, folio_y, folio, 9.0
                    )
                )
            ).pages[0]
            page.merge_page(overlay)
        writer.add_page(page)

    tmp_path = pdf_path.with_suffix(".stamped.pdf")
    with tmp_path.open("wb") as handle:
        writer.write(handle)
    tmp_path.replace(pdf_path)


def illustration_dpi_warnings(
    illustrations: list[Any],
    spec: PrintSpec,
    page_count: int,
) -> list[str]:
    try:
        from PIL import Image
    except ImportError:
        return []

    side_mm = spec.side_margin_mm(page_count)
    type_width_in = max(0.5, spec.trim_width_in - (2 * side_mm / 25.4))
    display_width_in = max(0.5, type_width_in * ILLUSTRATION_MAX_WIDTH_RATIO)
    warnings: list[str] = []
    for item in illustrations or []:
        path = getattr(item, "path", None)
        if path is None or not Path(path).is_file():
            continue
        try:
            with Image.open(path) as image:
                width_px, _height_px = image.size
        except OSError:
            continue
        dpi = width_px / display_width_in if display_width_in else 0
        if dpi < 300:
            label = getattr(item, "kind", "image")
            chapter_id = getattr(item, "chapter_id", "?")
            warnings.append(
                f"{label} {chapter_id}: {width_px}px bei Anzeigebreite "
                f"{display_width_in:.2f}in ergibt {dpi:.0f} dpi (< 300)"
            )
    return warnings


def write_print_report(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def export_paperback_interior(
    *,
    spec: PrintSpec,
    chapters: list[Any],
    html_text: str,
    html_path: Path,
    css_path: Path,
    pdf_path: Path,
    report_path: Path,
    author: str,
    title: str,
    illustrations: list[Any] | None = None,
    render_pdf: Callable[[Path, Path], None] | None = None,
    stamp: bool = True,
) -> dict[str, Any]:
    """Setzt HTML/CSS, rendert, zaehlt Seiten, setzt Bundsteg bis zu 3 Laeufen."""
    render = render_pdf or render_html_to_pdf
    illustrations = illustrations or []
    words = count_export_words(chapters)
    frontmatter_sections = count_frontmatter_sections(html_text)
    assumed_pages = spec.estimate_page_count(words, frontmatter_sections)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html_text, encoding="utf-8")

    write_paperback_css(css_path, spec, assumed_pages)
    render(html_path, pdf_path)
    actual_pages = count_pdf_pages(pdf_path)
    iterations = 1
    rerendered = False
    previous_pages = assumed_pages
    while iterations < GUTTER_MAX_PASSES and spec.needs_rerender(
        previous_pages, actual_pages
    ):
        if kdp_gutter_band(previous_pages) == kdp_gutter_band(actual_pages):
            break
        previous_pages = actual_pages
        write_paperback_css(css_path, spec, actual_pages)
        render(html_path, pdf_path)
        actual_pages = count_pdf_pages(pdf_path)
        iterations += 1
        rerendered = True

    side_mm = spec.side_margin_mm(actual_pages)
    if stamp:
        stamp_running_matter(
            pdf_path,
            spec,
            author=author,
            title=title,
            skip_pages=frontmatter_sections,
            work_dir=html_path.parent,
            side_margin_mm=side_mm,
        )

    kdp_max = spec.kdp_max_pages()
    within_limit = actual_pages <= kdp_max
    warnings: list[str] = []
    if rerendered:
        warnings.append("Bundsteg nach erstem Satzlauf neu berechnet.")
    if not within_limit:
        warnings.append(
            f"Seitenzahl {actual_pages} ueber KDP-Maximum {spec.paper} "
            f"({kdp_max})."
        )
    elif actual_pages >= kdp_max - 20:
        warnings.append(
            f"Seitenzahl {actual_pages} nahe am KDP-Maximum {kdp_max}."
        )
    warnings.extend(illustration_dpi_warnings(illustrations, spec, actual_pages))
    status = "ok" if within_limit and not warnings else "warning"

    report = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "trim_size": spec.trim_size,
        "trim_in": [spec.trim_width_in, spec.trim_height_in],
        "trim_width_mm": spec.trim_width_mm,
        "trim_height_mm": spec.trim_height_mm,
        "paper": spec.paper,
        "ink": spec.ink,
        "layout_profile": spec.layout_profile,
        "profile": spec.profile,
        "illustration_mode": spec.illustration_mode,
        "chapter_start": spec.chapter_start,
        "bleed": spec.bleed,
        "font_family": spec.font_family,
        "font_size_pt": spec.font_size_pt,
        "line_height_pt": spec.line_height_pt,
        "assumed_pages": assumed_pages,
        "page_count": actual_pages,
        "kdp_max_pages": kdp_max,
        "within_kdp_page_limit": within_limit,
        "gutter_mm": spec.gutter_mm(actual_pages),
        "side_margin_mm": side_mm,
        "iterations": iterations,
        "gutter_rerendered": rerendered,
        "cover_omitted": True,
        "frontmatter_sections_unstamped": frontmatter_sections,
        "word_count": words,
        "warnings": warnings,
        "output_pdf": str(pdf_path),
    }
    write_print_report(report_path, report)
    return report
