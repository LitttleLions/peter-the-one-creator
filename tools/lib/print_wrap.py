"""Vorderseite, Rueckseite und KDP-Wrap-PDF fuer Taschenbuch komplett."""

from __future__ import annotations

import colorsys
import html
import sys
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

# Barcode: KDP setzt den Barcode (ca. 2 x 1,2 in) als Bild unten rechts auf die
# Rueckseite. Hier wird NUR Platz freigehalten, nichts gemalt (Nutzerwunsch
# 2026-11-12). Masse vor Umstellung gegen die aktuelle KDP-Hilfe pruefen.
BARCODE_ZONE_W_IN = 2.0
BARCODE_ZONE_H_IN = 1.2
BARCODE_ZONE_MARGIN_IN = 0.25
BARCODE_TEXT_GAP_IN = 0.15
# KDP erlaubt Rueckentext erst ab 79 Seiten.
SPINE_TEXT_MIN_PAGES = 79
SPINE_ORNAMENT_MIN_MM = 12.0
SPINE_PUBLISHER_MIN_MM = 25.0
SPINE_FONT_MAX_PT = 14.0
SPINE_FONT_RATIO = 0.45
BLURB_MAX_WIDTH_MM = 108.0
SUBTITLE_MAX_CHARS = 60
MIN_CONTRAST = 7.0

# Rueckseiten-Gestaltung (2026-11-11). Gestaltet ist der STANDARD: jedes
# Buchpaket bekommt die gestaltete Umschlagrueckseite, auch ohne eigenen
# `print.back_cover`-Block. Schlicht (weisse Flaeche) nur noch bewusst mit
# `print.back_cover.styled: false`.
#
# Farben (2026-11-12): Ist ein Druckcover da, werden Rueckseite und Ruecken aus
# dem linken Randstreifen des Covers abgeleitet; ausdrueckliche Angaben in
# `print.back_cover.colors` gewinnen je Schluessel. Ohne lesbares Cover oder bei
# zu geringem Kontrast gilt der neutrale Standard (Vorbild: pharao).
DEFAULT_BACK_COLORS = {
    "background": "#f7f4ee",
    "text": "#1f1b16",
    "heading": "#3c332a",
    "rule": "#a89478",
    "spine": "#2a1d0f",
    "spine_text": "#e8dcc0",
}
BACK_ORNAMENT = "❦"  # Blattornament, in EB Garamond vorhanden

# Stufen der Passung: Fliesstext und Autoren-Bio werden schrittweise kleiner,
# erst zuletzt faellt das Zitat weg. Die Bio bleibt immer stehen.
FIT_LEVELS: tuple[dict[str, Any], ...] = (
    {"blurb_pt": 10.5, "bio_pt": 8.8, "lh": 1.38, "col": 0.88, "quote": True},
    {"blurb_pt": 10.0, "bio_pt": 8.6, "lh": 1.36, "col": 0.88, "quote": True},
    {"blurb_pt": 9.6, "bio_pt": 8.5, "lh": 1.35, "col": 0.90, "quote": True},
    {"blurb_pt": 9.4, "bio_pt": 8.4, "lh": 1.33, "col": 0.94, "quote": True},
    {"blurb_pt": 9.4, "bio_pt": 8.4, "lh": 1.33, "col": 0.94, "quote": False, "only_quote": True},
    {"blurb_pt": 9.2, "bio_pt": 8.3, "lh": 1.30, "col": 1.0, "quote": False},
    {"blurb_pt": 9.0, "bio_pt": 8.2, "lh": 1.28, "col": 1.0, "quote": False},
)
# Breitere Spalte erst in den engen Stufen (Zeilenlaenge sonst > 70 Zeichen).
WIDE_COLUMN_MAX_MM = 120.0


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
    for key in (
        "title",
        "author",
        "summary",
        "description",
        "author_bio",
        "subtitle",
        "publisher",
        "series",
        "language",
    ):
        value = meta.get(key)
        if value:
            out[key] = value
    return out


def _text_field(fields: dict[str, Any], key: str) -> str:
    return " ".join(str(fields.get(key) or "").split())


def header_line(meta: dict[str, Any]) -> str:
    """Kopfzeile ueber dem Titel: Reihe, sonst Verlag, sonst nichts."""
    fields = _book_fields(meta)
    return _text_field(fields, "series") or _text_field(fields, "publisher")


def footer_line(meta: dict[str, Any]) -> str:
    """Fusszeile links neben dem Barcode-Platz: Verlag, wenn nicht schon Kopfzeile."""
    fields = _book_fields(meta)
    publisher = _text_field(fields, "publisher")
    return "" if publisher == header_line(meta) else publisher


def _lang_attr(meta: dict[str, Any]) -> str:
    code = _text_field(_book_fields(meta), "language") or "de"
    return code.split("-")[0].lower() or "de"


# --- Farben ---------------------------------------------------------------


def _hex_to_rgb(value: str) -> tuple[float, float, float] | None:
    text = value.strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        return None
    try:
        return tuple(int(text[i : i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]
    except ValueError:
        return None


def _rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    r, g, b = (max(0, min(255, round(c * 255))) for c in rgb)
    return f"#{r:02x}{g:02x}{b:02x}"


def _hls_hex(h: float, l: float, s: float) -> str:
    return _rgb_to_hex(colorsys.hls_to_rgb(h, max(0.0, min(1.0, l)), max(0.0, min(1.0, s))))


def _luminance(rgb: tuple[float, float, float]) -> float:
    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a: str, b: str) -> float:
    ra, rb = _hex_to_rgb(a), _hex_to_rgb(b)
    if ra is None or rb is None:
        return 0.0
    la, lb = _luminance(ra), _luminance(rb)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def cover_edge_color(cover_path: Path) -> tuple[float, float, float] | None:
    """Mittlere Farbe des linken Randstreifens (5 %) - die Seite zum Ruecken."""
    try:
        from PIL import Image

        with Image.open(cover_path) as img:
            rgb = img.convert("RGB")
            strip = rgb.crop((0, 0, max(1, rgb.width // 20), rgb.height))
            r, g, b = strip.resize((1, 1), Image.BOX).getpixel((0, 0))
    except Exception:
        return None
    return (r / 255, g / 255, b / 255)


def derive_palette(cover_path: Path | None) -> dict[str, str] | None:
    """Farben fuer Rueckseite und Ruecken aus dem Cover; None bei Fehlschlag."""
    if cover_path is None:
        return None
    edge = cover_edge_color(cover_path)
    if edge is None:
        return None
    h, l, s = colorsys.rgb_to_hls(*edge)
    palette = {
        "background": _hls_hex(h, 0.94, min(s, 0.18)),
        "text": _hls_hex(h, 0.11, min(s, 0.20)),
        "heading": _hls_hex(h, 0.22, min(s, 0.35)),
        "rule": _hls_hex(h, 0.52, min(s, 0.30)),
        "spine": _hls_hex(h, min(l, 0.30) if l > 0.12 else 0.16, min(s, 0.60)),
        "spine_text": _hls_hex(h, 0.90, min(s, 0.25)),
    }
    if contrast_ratio(palette["text"], palette["background"]) < MIN_CONTRAST:
        return None
    if contrast_ratio(palette["spine_text"], palette["spine"]) < MIN_CONTRAST:
        palette["spine_text"] = "#f5f0e4"
        if contrast_ratio(palette["spine_text"], palette["spine"]) < MIN_CONTRAST:
            return None
    return palette


def _shade(color: str, factor: float) -> str:
    rgb = _hex_to_rgb(color)
    if rgb is None:
        return color
    return _rgb_to_hex(tuple(min(1.0, c * factor) for c in rgb))  # type: ignore[arg-type]


def back_cover_settings(
    meta: dict[str, Any], cover_path: Path | None = None
) -> dict[str, Any]:
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
    derived = derive_palette(cover_path)
    if derived:
        colors.update(derived)
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


def _paragraph_html(paragraphs: list[str], dropcap: bool) -> str:
    parts: list[str] = []
    for index, text in enumerate(paragraphs):
        # Initiale nur bei einem Buchstaben: aus "1241" wurde sonst "1 241".
        cls = " class='dropcap'" if dropcap and index == 0 and text[:1].isalpha() else ""
        parts.append(f"<p{cls}>{_escape(text)}</p>")
    return "\n".join(parts)


def back_cover_html(
    meta: dict[str, Any],
    cfg: dict[str, Any] | None = None,
    fit: dict[str, Any] | None = None,
) -> str:
    """Rueckseiteninhalt als HTML - schlicht oder gestaltet.

    Elemente ohne Wert werden gar nicht erst ausgegeben (kein leeres Autorenfeld,
    keine doppelten Trennlinien).
    """
    title, author, summary = back_cover_copy(meta)
    cfg = cfg or back_cover_settings(meta)
    fit = fit or FIT_LEVELS[0]
    fields = _book_fields(meta)
    paragraphs = _summary_paragraphs(summary)
    brand_text = header_line(meta)
    brand = f"<p class='brand'>{_escape(brand_text)}</p>" if brand_text else ""
    if not cfg["styled"]:
        body = "\n".join(f"<p>{_escape(text)}</p>" for text in paragraphs)
        author_line = f"<p class='author'>{_escape(author)}</p>" if author else ""
        return f"{brand}<h1>{_escape(title)}</h1>{author_line}{body}"

    tagline_text = cfg["tagline"]
    if not paragraphs and tagline_text:
        paragraphs = [tagline_text]
        tagline_text = ""
    body = _paragraph_html(paragraphs, dropcap=True)
    tagline = f"<p class='tagline'>{_escape(tagline_text)}</p>" if tagline_text else ""
    subtitle_text = _text_field(fields, "subtitle")
    subtitle = (
        f"<p class='subtitle'>{_escape(subtitle_text)}</p>"
        if subtitle_text and len(subtitle_text) <= SUBTITLE_MAX_CHARS
        else ""
    )
    author_line = f"<p class='author'>{_escape(author)}</p>" if author else ""
    quote = ""
    if cfg["quote"] and fit.get("quote", True):
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
            "<p class='bio-head'>Über den Autor</p>"
            f"<p>{_escape(cfg['author_bio'])}</p></div>"
        )
    blurb = f"<div class='blurb'>{body}{tagline}</div>" if (body or tagline) else ""
    head = (
        "<div class='back-head'>"
        f"{brand}"
        f"<h1>{_escape(title)}</h1>"
        f"{subtitle}"
        f"{author_line}"
        f"<div class='rule'>{BACK_ORNAMENT}</div>"
        "</div>"
    )
    return f"<div class='back-main'>{head}{blurb}{quote}{bio}</div>"


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
    """Rueckseite im Innenblock (Paperback-komplett): schlicht, ohne Barcode-Zeichnung."""
    title, author, summary = back_cover_copy(meta)
    cfg = back_cover_settings(meta)
    body = "\n".join(
        f"<p>{_escape(text)}</p>" for text in _summary_paragraphs(summary)
    )
    author_line = f"<p class='author'>{_escape(author)}</p>" if author else ""
    brand_text = header_line(meta)
    brand = f"<p class='brand'>{_escape(brand_text)}</p>" if brand_text else ""
    styled = (
        f"body {{ background: {cfg['colors']['background']}; "
        f"color: {cfg['colors']['text']}; }}\n"
        "h1 { color: %s; }\n" % cfg["colors"]["heading"]
        if cfg["styled"]
        else ""
    )
    return (
        f"<!doctype html><html lang='{_lang_attr(meta)}'><head><meta charset='utf-8' />"
        "<style>"
        f"{_font_css(spec, html_path)}\n"
        f"{styled}"
        f"@page {{ size: {spec.trim_css()}; margin: 16mm 16mm 24mm 16mm; }}\n"
        "html, body { margin: 0; padding: 0; }\n"
        ".brand { font-size: 9pt; letter-spacing: 0.14em; text-transform: uppercase; "
        "margin: 0 0 10mm; }\n"
        "h1 { font-size: 18pt; font-weight: normal; margin: 0 0 4mm; line-height: 1.15; }\n"
        ".author { font-size: 12pt; margin: 0 0 10mm; }\n"
        "p { font-size: 10pt; line-height: 1.35; margin: 0 0 0.8em; text-align: justify; "
        "hyphens: auto; }\n"
        "</style></head><body>"
        f"{brand}"
        f"<h1>{_escape(title)}</h1>"
        f"{author_line}"
        f"{body}"
        "</body></html>"
    )


def _spine_parts(
    meta: dict[str, Any], page_count: int, spine_mm: float, height_in: float
) -> dict[str, Any]:
    """Was auf den Ruecken kommt - abhaengig von Dicke und Seitenzahl."""
    title, author, _summary = back_cover_copy(meta)
    label = " · ".join(part for part in (author, title) if part)
    spine_in = spine_mm / 25.4
    show_text = page_count >= SPINE_TEXT_MIN_PAGES and bool(label)
    font_pt = min(SPINE_FONT_MAX_PT, SPINE_FONT_RATIO * spine_in * 72)
    publisher = _text_field(_book_fields(meta), "publisher")
    show_publisher = False
    if show_text and publisher and spine_mm >= SPINE_PUBLISHER_MIN_MM:
        # grobe Laengenschaetzung: Platz fuer Titelzeile in der Mitte und den
        # Verlag am Fuss, ohne dass sie sich beruehren
        label_mm = len(label) * font_pt * 0.45 * 0.3528
        pub_mm = len(publisher) * 8 * 0.5 * 0.3528
        room_mm = (height_in * 25.4) / 2 - 18
        show_publisher = label_mm / 2 + pub_mm + 8 < room_mm
    return {
        "label": label if show_text else "",
        "font_pt": font_pt,
        "ornaments": spine_mm >= SPINE_ORNAMENT_MIN_MM and show_text,
        "publisher": publisher if show_publisher else "",
    }


def render_wrap_html(
    *,
    meta: dict[str, Any],
    cover_path: Path,
    html_path: Path,
    spec: PrintSpec,
    page_count: int,
    fit: dict[str, Any] | None = None,
) -> str:
    fit = fit or FIT_LEVELS[0]
    cfg = back_cover_settings(meta, cover_path)
    colors = cfg["colors"]
    src = _asset_url(cover_path, html_path)
    width = wrap_width_in(page_count, spec.trim_width_in, spec.paper)
    height = wrap_height_in(spec.trim_height_in)
    panel = wrap_panel_width_in(spec.trim_width_in)
    spine_mm = kdp_spine_mm(page_count, spec.paper)
    spine_in = spine_mm / 25.4
    back_panel = back_cover_html(meta, cfg, fit)
    spine = _spine_parts(meta, page_count, spine_mm, height)

    pad_left = KDP_BLEED_IN + 0.5
    pad_right = 0.5
    pad_top = KDP_BLEED_IN + 0.40
    # Unterkante des Textbereichs liegt ueber dem Barcode-Platz (unten rechts).
    pad_bottom = (
        KDP_BLEED_IN + BARCODE_ZONE_MARGIN_IN + BARCODE_ZONE_H_IN + BARCODE_TEXT_GAP_IN
    )
    content_mm = (panel - pad_left - pad_right) * 25.4
    column_cap = WIDE_COLUMN_MAX_MM if fit['col'] >= 0.95 else BLURB_MAX_WIDTH_MM
    column_mm = round(min(column_cap, content_mm * fit['col']))
    foot_max_in = max(
        1.0,
        panel - pad_left - BARCODE_ZONE_W_IN - BARCODE_ZONE_MARGIN_IN - 0.3,
    )
    footer = footer_line(meta)

    spine_extra = ""
    if cfg["styled"]:
        back_bg = colors["background"]
        spine_color = colors["spine_text"]
        spine_bg = (
            f"linear-gradient(180deg, {_shade(colors['spine'], 0.8)} 0%, "
            f"{colors['spine']} 50%, {_shade(colors['spine'], 0.8)} 100%)"
            if _hex_to_rgb(colors["spine"]) is not None
            else colors["spine"]
        )
        spine_rule = ""
        if spine["ornaments"]:
            spine_rule = f"<div class='spine-rule top'>{BACK_ORNAMENT}</div>"
            if not spine["publisher"]:
                spine_rule += f"<div class='spine-rule bottom'>{BACK_ORNAMENT}</div>"
        spine_extra = (
            f"<span class='spine-pub'>{_escape(spine['publisher'])}</span>"
            if spine["publisher"]
            else ""
        )
        back_css = (
            ".back { display: flex; flex-direction: column; }\n"
            ".back-main { flex: 1; min-height: 0; overflow: hidden; display: flex; "
            "flex-direction: column; }\n"
            f".back-main > * {{ width: 100%; max-width: {column_mm}mm; "
            "margin-left: auto; margin-right: auto; box-sizing: border-box; }\n"
            ".back-head { text-align: center; margin-top: 0; margin-bottom: 6mm; }\n"
            ".brand { font-size: 8.5pt; letter-spacing: 0.14em; "
            "text-transform: uppercase; margin: 0 0 4mm; }\n"
            f"h1 {{ font-size: 19pt; font-weight: normal; margin: 0 0 2mm; "
            f"line-height: 1.12; color: {colors['heading']}; }}\n"
            ".subtitle { font-size: 10.5pt; font-style: italic; margin: 0 0 2.5mm; }\n"
            ".author { font-size: 11pt; margin: 0 0 4mm; letter-spacing: 0.06em; }\n"
            f".rule {{ color: {colors['rule']}; font-size: 12pt; "
            "display: flex; align-items: center; gap: 4mm; }\n"
            f".rule::before, .rule::after {{ content: ''; flex: 1; "
            f"border-top: 0.5pt solid {colors['rule']}; opacity: 0.55; }}\n"
            f".blurb p {{ font-size: {fit['blurb_pt']}pt; line-height: {fit['lh']}; "
            "margin: 0 0 0.7em; text-align: justify; hyphens: auto; "
            "text-justify: inter-word; }\n"
            ".blurb p.dropcap::first-letter { font-size: 2.55em; float: left; "
            "line-height: 0.8; padding: 0.05em 0.07em 0 0; }\n"
            f".tagline {{ font-style: italic; text-align: center !important; "
            f"color: {colors['heading']}; margin-top: 4mm; }}\n"
            f".quote {{ margin-top: 5mm; padding: 4mm 0 0; "
            f"border-top: 0.5pt solid {colors['rule']}; text-align: center; }}\n"
            ".quote p { font-style: italic; font-size: 9.6pt; line-height: 1.4; "
            "margin: 0 0 1.5mm; text-align: center; }\n"
            ".quote-source { font-size: 8pt; letter-spacing: 0.1em; "
            "text-transform: uppercase; opacity: 0.75; }\n"
            f".author-bio {{ margin-top: auto; padding: 4mm 0 0; "
            f"border-top: 0.5pt solid {colors['rule']}; }}\n"
            f".bio-head {{ font-size: 8.5pt; letter-spacing: 0.14em; "
            f"text-transform: uppercase; color: {colors['heading']}; "
            "margin: 0 0 2mm; text-align: left; }\n"
            f".author-bio p {{ font-size: {fit['bio_pt']}pt; line-height: {fit['lh']}; "
            "margin: 0; text-align: left; hyphens: auto; }\n"
            ".blurb + .author-bio, .quote + .author-bio { margin-top: auto; }\n"
            ".back-head + .author-bio { margin-top: auto; }\n"
            ".spine-rule { position: absolute; left: 50%; "
            "transform: translateX(-50%); font-size: 11pt; opacity: 0.75; }\n"
            ".spine-rule.top { top: 20mm; }\n"
            ".spine-rule.bottom { bottom: 20mm; }\n"
        )
        footer_html = (
            f"<p class='back-foot'>{_escape(footer)}</p>" if footer else ""
        )
        back_css += (
            f".back-foot {{ position: absolute; left: {_inches(pad_left)}; "
            f"bottom: {_inches(KDP_BLEED_IN + 0.3)}; margin: 0; "
            f"max-width: {_inches(foot_max_in)}; font-size: 7.5pt; "
            "letter-spacing: 0.14em; text-transform: uppercase; "
            f"color: {colors['heading']}; }}\n"
        )
    else:
        back_bg = "#ffffff"
        spine_bg = "#1a1a1a"
        spine_color = "#f4f0e6"
        spine_rule = ""
        footer_html = ""
        back_css = (
            ".brand { font-size: 8.5pt; letter-spacing: 0.14em; "
            "text-transform: uppercase; margin: 0 0 8mm; }\n"
            "h1 { font-size: 16pt; font-weight: normal; margin: 0 0 3mm; "
            "line-height: 1.12; }\n"
            ".author { font-size: 11pt; margin: 0 0 8mm; }\n"
            "p { font-size: 9.2pt; line-height: 1.32; margin: 0 0 0.7em; "
            "text-align: justify; hyphens: auto; }\n"
        )

    spine_label_html = (
        f"<span>{_escape(spine['label'])}</span>" if spine["label"] else ""
    )
    return (
        f"<!doctype html><html lang='{_lang_attr(meta)}'><head><meta charset='utf-8' />"
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
        f"font-size: {spine['font_pt']:.1f}pt; letter-spacing: 0.08em; }}\n"
        ".spine span.spine-pub { top: auto; bottom: 36mm; font-size: 8pt; "
        "letter-spacing: 0.14em; text-transform: uppercase; "
        "transform: translate(-50%, 50%) rotate(-90deg); }\n"
        f".back {{ background: {back_bg}; color: {colors['text']}; "
        f"padding: {_inches(pad_top)} {_inches(pad_right)} "
        f"{_inches(pad_bottom)} {_inches(pad_left)}; "
        "box-sizing: border-box; }\n"
        f"{back_css}"
        # Nur Platz, nichts gemalt: KDP legt den Barcode als Bild darueber.
        f".barcode-reserve {{ position: absolute; right: {_inches(BARCODE_ZONE_MARGIN_IN)}; "
        f"bottom: {_inches(KDP_BLEED_IN + BARCODE_ZONE_MARGIN_IN)}; "
        f"width: {_inches(BARCODE_ZONE_W_IN)}; height: {_inches(BARCODE_ZONE_H_IN)}; }}\n"
        ".front img { display: block; width: 100%; height: 100%; object-fit: cover; }\n"
        "</style></head><body>"
        "<div class='wrap'>"
        "<div class='panel back'>"
        f"{back_panel}"
        f"{footer_html}"
        "<div class='barcode-reserve' aria-hidden='true'></div>"
        "</div>"
        f"<div class='spine'>{spine_rule}{spine_label_html}{spine_extra}</div>"
        f"<div class='panel front'><img src='{_escape(src)}' alt='Cover' /></div>"
        "</div></body></html>"
    )


def measure_back_overflow(html_path: Path) -> float:
    """Ueberstand des Rueckseitentextes in CSS-Pixeln (0 = passt)."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(html_path.resolve().as_uri(), wait_until="load")
            try:
                page.evaluate("() => document.fonts.ready")
            except Exception:
                pass
            value = page.evaluate(
                "() => { const m = document.querySelector('.back-main'); "
                "return m ? m.scrollHeight - m.clientHeight : 0; }"
            )
        finally:
            browser.close()
    return float(value or 0)


def render_fitted_wrap_html(
    *,
    meta: dict[str, Any],
    cover_path: Path,
    html_path: Path,
    spec: PrintSpec,
    page_count: int,
    measure: Callable[[Path], float] | None = None,
) -> tuple[str, list[str], bool]:
    """Wrap-HTML mit passender Textgroesse.

    Gibt (html, Hinweise, passt) zurueck. Ohne ``measure`` oder bei schlichter
    Rueckseite gilt die erste Stufe. Passt auch die kleinste Stufe nicht, wird
    sie trotzdem geliefert, aber ``passt`` ist False - der Aufrufer meldet das.
    """
    cfg = back_cover_settings(meta, cover_path)
    levels = list(FIT_LEVELS)
    if not cfg["quote"]:
        # Die Stufe "Zitat entfaellt" ist ohne Zitat ein Duplikat der davor.
        levels = [lv for lv in levels if not lv.get("only_quote")]
    kwargs = dict(
        meta=meta,
        cover_path=cover_path,
        html_path=html_path,
        spec=spec,
        page_count=page_count,
    )
    if measure is None or not cfg["styled"]:
        return render_wrap_html(fit=levels[0], **kwargs), [], True

    notes: list[str] = []
    html_text = ""
    for index, level in enumerate(levels):
        html_text = render_wrap_html(fit=level, **kwargs)
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(html_text, encoding="utf-8")
        overflow = measure(html_path)
        if overflow <= 1:
            if index:
                notes.append(
                    f"Rueckseite: Text auf {level['blurb_pt']} pt "
                    f"(Bio {level['bio_pt']} pt) verkleinert"
                    + ("" if level["quote"] or not cfg["quote"] else ", Zitat entfallen")
                )
            return html_text, notes, True
    notes.append(
        "Rueckseite: Klappentext zu lang - passt auch bei der kleinsten Stufe "
        f"({levels[-1]['blurb_pt']} pt) nicht; ca. {overflow:.0f} px Ueberstand, "
        "Klappentext kuerzen."
    )
    return html_text, notes, False


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
    html_text, notes, _fits = render_fitted_wrap_html(
        meta=meta,
        cover_path=cover_path,
        html_path=html_path,
        spec=spec,
        page_count=page_count,
        # Mit eingespieltem Renderer (Tests) wird nicht im Browser gemessen.
        measure=measure_back_overflow if render_pdf is None else None,
    )
    for note in notes:
        print(f"WARNUNG: {note}", file=sys.stderr)
    return write_html_pdf(html_text, html_path, pdf_path, render_pdf)
