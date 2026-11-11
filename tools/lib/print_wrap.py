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

# Rueckseiten-Gestaltung (2026-11-11). Gestaltet ist der STANDARD: jedes
# Buchpaket bekommt die gestaltete Umschlagrueckseite, auch ohne eigenen
# `print.back_cover`-Block. Schlicht (weisse Flaeche) nur noch bewusst mit
# `print.back_cover.styled: false`.
#
# Der Standard ist bewusst neutral (warmes Papierweiss, dunkle Schrift, gedeckte
# Akzente), damit er zu jedem Buch passt; Buchpakete koennen mit
# `print.back_cover.colors` ihre eigene Palette setzen (Vorbild: pharao).
DEFAULT_BACK_COLORS = {
    "background": "#f7f4ee",
    "text": "#1f1b16",
    "heading": "#3c332a",
    "rule": "#a89478",
}
BACK_ORNAMENT = "\u2766"  # ❦ Blattornament, in EB Garamond vorhanden


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
    fields = _book_fields(meta)
    title = str(fields.get("title") or "").strip() or "Motivatier Classics"
    author = str(fields.get("author") or "").strip()
    summary = str(fields.get("summary") or "").strip()
    if not summary:
        summary = str(fields.get("description") or "").strip()
    return title, author, summary


def _book_fields(meta: dict[str, Any]) -> dict[str, Any]:
    """Buchdaten lesen - flach oder unter ``book`` (Export-Dokument).

    `export_manuscript.py` uebergibt das ganze export.yaml (Buchdaten liegen
    unter ``book``), `build_cover.py` uebergibt dasselbe Dokument. Beide Formen
    werden bedient; flache Felder haben Vorrang.
    """
    out = dict(meta.get("book") or {}) if isinstance(meta.get("book"), dict) else {}
    for key in ("title", "author", "summary", "description", "author_bio"):
        value = meta.get(key)
        if value:
            out[key] = value
    return out


def back_cover_settings(meta: dict[str, Any]) -> dict[str, Any]:
    """Rueckseiten-Gestaltung aus ``print.back_cover``.

    Gestaltet ist der Standard, damit ein neuer Print-Lauf ohne Zutun im neuen
    Format entsteht. Schlicht nur mit ``print.back_cover.styled: false``.
    """
    raw = meta.get("back_cover")
    if not isinstance(raw, dict):
        print_block = meta.get("print")
        raw = print_block.get("back_cover") if isinstance(print_block, dict) else None
    if not isinstance(raw, dict):
        raw = {}
    colors = dict(DEFAULT_BACK_COLORS)
    given = raw.get("colors")
    if isinstance(given, dict):
        for key, value in given.items():
            text = str(value or "").strip()
            if key in colors and text:
                colors[key] = text
    return {
        "styled": bool(raw.get("styled", True)),
        "colors": colors,
        # Ohne eigene Angaben: Kurzbiografie und Zusammenfassung aus dem
        # Buchpaket, damit die Rueckseite auch ohne Pflege gefuellt ist.
        "tagline": str(raw.get("tagline") or "").strip(),
        "quote": str(raw.get("quote") or "").strip(),
        "quote_source": str(raw.get("quote_source") or "").strip(),
        "author_bio": str(
            raw.get("author_bio") or _book_fields(meta).get("author_bio") or ""
        ).strip(),
    }


def _summary_paragraphs(summary: str, limit: int = 4) -> list[str]:
    out: list[str] = []
    for block in summary.split("\n\n")[:limit]:
        clean = " ".join(block.split()).strip()
        if clean:
            out.append(clean)
    return out


def back_cover_html(meta: dict[str, Any]) -> str:
    """Rueckseiteninhalt als HTML - schlicht oder gestaltet."""
    title, author, summary = back_cover_copy(meta)
    cfg = back_cover_settings(meta)
    paragraphs = _summary_paragraphs(summary)
    if not cfg["styled"]:
        body = "\n".join(f"<p>{_escape(text)}</p>" for text in paragraphs)
        author_line = f"<p class='author'>{_escape(author)}</p>" if author else ""
        return (
            f"<p class='brand'>{_escape(SERIES_LINE)}</p>"
            f"<h1>{_escape(title)}</h1>"
            f"{author_line}"
            f"{body}"
        )

    body = "\n".join(f"<p>{_escape(text)}</p>" for text in paragraphs)
    tagline = (
        f"<p class='tagline'>{_escape(cfg['tagline'])}</p>"
        if cfg["tagline"]
        else ""
    )
    quote = ""
    if cfg["quote"]:
        source = (
            f"<span class='quote-source'>{_escape(cfg['quote_source'])}</span>"
            if cfg["quote_source"]
            else ""
        )
        quote = (
            "<div class='quote'>"
            f"<p>{_escape(cfg['quote'])}</p>{source}</div>"
        )
    bio = ""
    if cfg["author_bio"]:
        bio = (
            "<div class='author-bio'>"
            "<p class='bio-head'>Ueber den Autor</p>"
            f"<p>{_escape(cfg['author_bio'])}</p></div>"
        )
    return (
        "<div class='back-head'>"
        f"<p class='brand'>{_escape(SERIES_LINE)}</p>"
        f"<h1>{_escape(title)}</h1>"
        f"<p class='author'>{_escape(author)}</p>"
        f"<div class='rule'>{BACK_ORNAMENT}</div>"
        "</div>"
        f"<div class='blurb'>{body}{tagline}</div>"
        f"{quote}"
        f"{bio}"
    )


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
    cfg = back_cover_settings(meta)
    body = "\n".join(
        f"<p>{_escape(text)}</p>" for text in _summary_paragraphs(summary)
    )
    author_line = f"<p class='author'>{_escape(author)}</p>" if author else ""
    styled = (
        f"body {{ background: {cfg['colors']['background']}; "
        f"color: {cfg['colors']['text']}; }}\n"
        "h1 { color: %s; }\n" % cfg["colors"]["heading"]
        if cfg["styled"]
        else ""
    )
    return (
        "<!doctype html><html><head><meta charset='utf-8' />"
        "<style>"
        f"{_font_css(spec, html_path)}\n"
        f"{styled}"
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
    cfg = back_cover_settings(meta)
    colors = cfg["colors"]
    src = _asset_url(cover_path, html_path)
    width = wrap_width_in(page_count, spec.trim_width_in, spec.paper)
    height = wrap_height_in(spec.trim_height_in)
    panel = wrap_panel_width_in(spec.trim_width_in)
    spine_in = kdp_spine_mm(page_count, spec.paper) / 25.4
    paragraphs = _summary_paragraphs(summary)
    body = "\n".join(f"<p>{_escape(text)}</p>" for text in paragraphs)
    spine_label = " · ".join(part for part in (author, title) if part)
    back_panel = back_cover_html(meta)

    if cfg["styled"]:
        back_bg = colors["background"]
        spine_bg = "linear-gradient(180deg, #1c150e 0%, #33240f 50%, #1c150e 100%)"
        spine_color = "#e8dcc0"
        spine_rule = (
            f"<div class='spine-rule top'>{BACK_ORNAMENT}</div>"
            f"<div class='spine-rule bottom'>{BACK_ORNAMENT}</div>"
        )
        back_css = (
            ".back-head { text-align: center; margin: 0 0 7mm; }\n"
            ".brand { font-size: 8.5pt; letter-spacing: 0.14em; "
            "text-transform: uppercase; margin: 0 0 5mm; }\n"
            f"h1 {{ font-size: 19pt; font-weight: normal; margin: 0 0 2mm; "
            f"line-height: 1.12; color: {colors['heading']}; }}\n"
            ".author { font-size: 11pt; margin: 0 0 5mm; letter-spacing: 0.06em; }\n"
            f".rule {{ color: {colors['rule']}; font-size: 12pt; "
            "display: flex; align-items: center; gap: 4mm; }\n"
            f".rule::before, .rule::after {{ content: ''; flex: 1; "
            f"border-top: 0.5pt solid {colors['rule']}; opacity: 0.55; }}\n"
            ".blurb p { font-size: 9.2pt; line-height: 1.42; margin: 0 0 0.75em; "
            "text-align: justify; }\n"
            ".blurb p:first-child::first-letter { font-size: 2.1em; float: left; "
            "line-height: 0.86; padding: 0.04em 0.08em 0 0; }\n"
            f".tagline {{ font-style: italic; text-align: center; "
            f"color: {colors['heading']}; margin-top: 4mm; }}\n"
            f".quote {{ margin: 6mm 0 0; padding: 4mm 0 0; "
            f"border-top: 0.5pt solid {colors['rule']}; text-align: center; }}\n"
            ".quote p { font-style: italic; font-size: 9.6pt; line-height: 1.4; "
            "margin: 0 0 1.5mm; text-align: center; }\n"
            ".quote-source { font-size: 8pt; letter-spacing: 0.1em; "
            "text-transform: uppercase; opacity: 0.75; }\n"
            f".author-bio {{ margin: 6mm 0 0; padding: 4mm 0 0; "
            f"border-top: 0.5pt solid {colors['rule']}; }}\n"
            f".bio-head {{ font-size: 8.5pt; letter-spacing: 0.14em; "
            f"text-transform: uppercase; color: {colors['heading']}; "
            "margin: 0 0 2mm; }\n"
            ".author-bio p { font-size: 8.6pt; line-height: 1.38; margin: 0; "
            "text-align: justify; }\n"
            ".spine-rule { position: absolute; left: 50%; "
            "transform: translateX(-50%); font-size: 11pt; opacity: 0.75; }\n"
            ".spine-rule.top { top: 26mm; }\n"
            ".spine-rule.bottom { bottom: 26mm; }\n"
        )
    else:
        back_bg = "#ffffff"
        spine_bg = "#1a1a1a"
        spine_color = "#f4f0e6"
        spine_rule = ""
        back_css = (
            ".brand { font-size: 8.5pt; letter-spacing: 0.14em; "
            "text-transform: uppercase; margin: 0 0 8mm; }\n"
            "h1 { font-size: 16pt; font-weight: normal; margin: 0 0 3mm; "
            "line-height: 1.12; }\n"
            ".author { font-size: 11pt; margin: 0 0 8mm; }\n"
            "p { font-size: 9.2pt; line-height: 1.32; margin: 0 0 0.7em; "
            "text-align: justify; }\n"
        )

    return (
        "<!doctype html><html><head><meta charset='utf-8' />"
        "<style>"
        f"{_font_css(spec, html_path)}\n"
        f"@page {{ size: {_inches(width)} {_inches(height)}; margin: 0; }}\n"
        "html, body { margin: 0; padding: 0; }\n"
        f".wrap {{ display: flex; width: 100%; height: { _inches(height) }; }}\n"
        f".panel {{ width: {_inches(panel)}; height: 100%; position: relative; "
        "overflow: hidden; box-sizing: border-box; }\n"
        f".spine {{ width: {_inches(spine_in)}; height: 100%; position: relative; "
        f"background: {spine_bg}; color: {spine_color}; }}\n"
        ".spine span { position: absolute; top: 50%; left: 50%; "
        "transform: translate(-50%, -50%) rotate(-90deg); white-space: nowrap; "
        "font-size: 9pt; letter-spacing: 0.08em; }\n"
        f".back {{ background: {back_bg}; color: {colors['text']}; "
        f"padding: {_inches(KDP_BLEED_IN + 0.45)} {_inches(0.42)} "
        f"{_inches(KDP_BLEED_IN + 0.55)} {_inches(0.42)}; "
        "box-sizing: border-box; }\n"
        f"{back_css}"
        f".barcode-reserve {{ position: absolute; left: {_inches(KDP_BLEED_IN + 0.2)}; "
        f"bottom: {_inches(KDP_BLEED_IN + 0.2)}; width: {BARCODE_WIDTH_MM}mm; "
        f"height: {BARCODE_HEIGHT_MM}mm; "
        f"border: 0.3pt dashed {colors['rule'] if cfg['styled'] else '#bbb'}; "
        f"opacity: {0.5 if cfg['styled'] else 1}; }}\n"
        ".front img { display: block; width: 100%; height: 100%; object-fit: cover; }\n"
        "</style></head><body>"
        "<div class='wrap'>"
        "<div class='panel back'>"
        f"{back_panel}"
        "<div class='barcode-reserve' aria-hidden='true'></div>"
        "</div>"
        f"<div class='spine'>{spine_rule}<span>{_escape(spine_label)}</span></div>"
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
