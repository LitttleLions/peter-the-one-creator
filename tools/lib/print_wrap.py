"""Vorderseite, Rueckseite und KDP-Wrap-PDF fuer Taschenbuch komplett."""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any, Callable

from lib.print_pdf import render_html_to_pdf
from lib.print_spec import (
    KDP_BLEED_IN,
    PrintSpec,
    kdp_spine_mm,
    wrap_height_in,
    wrap_panel_width_in,
    wrap_width_in,
)

SERIES_LINE = "Motivatier Classics"
BARCODE_WIDTH_MM = 30
BARCODE_HEIGHT_MM = 18


def _inches(value: float) -> str:
    text = f"{value:.4f}".rstrip("0").rstrip(".")
    return f"{text}in"


def _escape(text: str) -> str:
    return html.escape(text)


def _asset_url(path: Path, html_path: Path) -> str:
    try:
        rel = path.resolve().relative_to(html_path.parent.resolve())
        return rel.as_posix().replace(" ", "%20")
    except ValueError:
        return path.resolve().as_uri()


def back_cover_copy(meta: dict[str, Any]) -> tuple[str, str, str]:
    title = str(meta.get("title") or "").strip() or "Motivatier Classics"
    author = str(meta.get("author") or "").strip()
    summary = str(meta.get("summary") or "").strip()
    if not summary:
        summary = str(meta.get("description") or "").strip()
    return title, author, summary


def _font_css(spec: PrintSpec, html_path: Path) -> str:
    from lib.print_css import css_asset_url

    family = spec.font_family
    regular = css_asset_url(spec.font_regular_path, html_path)
    italic = css_asset_url(spec.font_italic_path, html_path)
    return (
        f"@font-face {{ font-family: '{family}'; "
        f"src: url('{regular}') format('truetype'); font-style: normal; }}\n"
        f"@font-face {{ font-family: '{family}'; "
        f"src: url('{italic}') format('truetype'); font-style: italic; }}\n"
        f"body {{ font-family: '{family}', 'Times New Roman', serif; color: #111; }}"
    )


def render_print_cover_html(cover_path: Path, html_path: Path, spec: PrintSpec) -> str:
    src = _asset_url(cover_path, html_path)
    return (
        "<!doctype html><html><head><meta charset='utf-8' />"
        "<style>"
        f"@page {{ size: {spec.trim_css()}; margin: 0; }}\n"
        "html, body { margin: 0; padding: 0; }\n"
        ".print-cover { width: 100%; height: 100%; }\n"
        ".print-cover img { display: block; width: 100%; height: 100%; "
        "object-fit: cover; }\n"
        "</style></head><body>"
        f"<div class='print-cover'><img src='{_escape(src)}' alt='Cover' /></div>"
        "</body></html>"
    )


def render_back_cover_html(meta: dict[str, Any], html_path: Path, spec: PrintSpec) -> str:
    title, author, summary = back_cover_copy(meta)
    paragraphs = []
    for block in summary.split("\n\n"):
        clean = " ".join(block.split()).strip()
        if clean:
            paragraphs.append(f"<p>{_escape(clean)}</p>")
    body = "\n".join(paragraphs)
    author_line = f"<p class='author'>{_escape(author)}</p>" if author else ""
    return (
        "<!doctype html><html><head><meta charset='utf-8' />"
        "<style>"
        f"{_font_css(spec, html_path)}\n"
        f"@page {{ size: {spec.trim_css()}; margin: 16mm 16mm 24mm 16mm; }}\n"
        "html, body { margin: 0; padding: 0; }\n"
        ".brand { font-size: 9pt; letter-spacing: 0.14em; text-transform: uppercase; "
        "margin: 0 0 10mm; }\n"
        "h1 { font-size: 18pt; font-weight: normal; margin: 0 0 4mm; line-height: 1.15; }\n"
        ".author { font-size: 12pt; margin: 0 0 10mm; }\n"
        "p { font-size: 10pt; line-height: 1.35; margin: 0 0 0.8em; text-align: justify; }\n"
        ".barcode-reserve { position: absolute; left: 16mm; bottom: 12mm; "
        f"width: {BARCODE_WIDTH_MM}mm; height: {BARCODE_HEIGHT_MM}mm; "
        "border: 0.3pt dashed #bbb; }\n"
        "</style></head><body>"
        f"<p class='brand'>{_escape(SERIES_LINE)}</p>"
        f"<h1>{_escape(title)}</h1>"
        f"{author_line}"
        f"{body}"
        "<div class='barcode-reserve' aria-hidden='true'></div>"
        "</body></html>"
    )


def render_wrap_html(
    *,
    meta: dict[str, Any],
    cover_path: Path,
    html_path: Path,
    spec: PrintSpec,
    page_count: int,
) -> str:
    title, author, summary = back_cover_copy(meta)
    src = _asset_url(cover_path, html_path)
    width = wrap_width_in(page_count, spec.trim_width_in, spec.paper)
    height = wrap_height_in(spec.trim_height_in)
    panel = wrap_panel_width_in(spec.trim_width_in)
    spine_in = kdp_spine_mm(page_count, spec.paper) / 25.4
    paragraphs = []
    for block in summary.split("\n\n")[:4]:
        clean = " ".join(block.split()).strip()
        if clean:
            paragraphs.append(f"<p>{_escape(clean)}</p>")
    body = "\n".join(paragraphs)
    spine_label = " · ".join(part for part in (author, title) if part)
    return (
        "<!doctype html><html><head><meta charset='utf-8' />"
        "<style>"
        f"{_font_css(spec, html_path)}\n"
        f"@page {{ size: {_inches(width)} {_inches(height)}; margin: 0; }}\n"
        "html, body { margin: 0; padding: 0; }\n"
        f".wrap {{ display: flex; width: 100%; height: { _inches(height) }; }}\n"
        f".panel {{ width: {_inches(panel)}; height: 100%; position: relative; "
        "overflow: hidden; box-sizing: border-box; }}\n"
        f".spine {{ width: {_inches(spine_in)}; height: 100%; display: flex; "
        "align-items: center; justify-content: center; background: #1a1a1a; "
        "color: #f4f0e6; writing-mode: vertical-rl; transform: rotate(180deg); "
        "font-size: 9pt; letter-spacing: 0.08em; padding: 12mm 0; box-sizing: border-box; }}\n"
        f".back {{ padding: {_inches(KDP_BLEED_IN + 0.35)} {_inches(0.35)} "
        f"{_inches(KDP_BLEED_IN + 0.55)} {_inches(KDP_BLEED_IN + 0.3)}; "
        "box-sizing: border-box; }}\n"
        ".brand { font-size: 8.5pt; letter-spacing: 0.14em; text-transform: uppercase; "
        "margin: 0 0 8mm; }\n"
        "h1 { font-size: 16pt; font-weight: normal; margin: 0 0 3mm; line-height: 1.12; }\n"
        ".author { font-size: 11pt; margin: 0 0 8mm; }\n"
        "p { font-size: 9.2pt; line-height: 1.32; margin: 0 0 0.7em; text-align: justify; }\n"
        f".barcode-reserve {{ position: absolute; left: {_inches(KDP_BLEED_IN + 0.2)}; "
        f"bottom: {_inches(KDP_BLEED_IN + 0.2)}; width: {BARCODE_WIDTH_MM}mm; "
        f"height: {BARCODE_HEIGHT_MM}mm; border: 0.3pt dashed #bbb; }}\n"
        ".front img { display: block; width: 100%; height: 100%; object-fit: cover; }\n"
        "</style></head><body>"
        "<div class='wrap'>"
        "<div class='panel back'>"
        f"<p class='brand'>{_escape(SERIES_LINE)}</p>"
        f"<h1>{_escape(title)}</h1>"
        f"<p class='author'>{_escape(author)}</p>"
        f"{body}"
        "<div class='barcode-reserve' aria-hidden='true'></div>"
        "</div>"
        f"<div class='spine'>{_escape(spine_label)}</div>"
        f"<div class='panel front'><img src='{_escape(src)}' alt='Cover' /></div>"
        "</div></body></html>"
    )


def write_html_pdf(
    html_text: str,
    html_path: Path,
    pdf_path: Path,
    render_pdf: Callable[[Path, Path], None] | None = None,
) -> Path:
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html_text, encoding="utf-8")
    render = render_pdf or render_html_to_pdf
    render(html_path, pdf_path)
    return pdf_path


def concat_pdfs(sources: list[Path], dest: Path) -> Path:
    from pypdf import PdfReader, PdfWriter

    writer = PdfWriter()
    for path in sources:
        reader = PdfReader(str(path))
        for page in reader.pages:
            writer.add_page(page)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".concat.pdf")
    with tmp.open("wb") as handle:
        writer.write(handle)
    tmp.replace(dest)
    return dest


def export_print_cover_page(
    *,
    cover_path: Path,
    html_path: Path,
    pdf_path: Path,
    spec: PrintSpec,
    render_pdf: Callable[[Path, Path], None] | None = None,
) -> Path:
    html_text = render_print_cover_html(cover_path, html_path, spec)
    return write_html_pdf(html_text, html_path, pdf_path, render_pdf)


def export_print_back_page(
    *,
    meta: dict[str, Any],
    html_path: Path,
    pdf_path: Path,
    spec: PrintSpec,
    render_pdf: Callable[[Path, Path], None] | None = None,
) -> Path:
    html_text = render_back_cover_html(meta, html_path, spec)
    return write_html_pdf(html_text, html_path, pdf_path, render_pdf)


def export_print_wrap(
    *,
    meta: dict[str, Any],
    cover_path: Path,
    html_path: Path,
    pdf_path: Path,
    spec: PrintSpec,
    page_count: int,
    render_pdf: Callable[[Path, Path], None] | None = None,
) -> Path:
    html_text = render_wrap_html(
        meta=meta,
        cover_path=cover_path,
        html_path=html_path,
        spec=spec,
        page_count=page_count,
    )
    return write_html_pdf(html_text, html_path, pdf_path, render_pdf)
