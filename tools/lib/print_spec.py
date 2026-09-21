"""Satzspiegel und KDP-Bundsteg fuer den Paperback-Innenexport.

Serie-Defaults: config/print.yaml
Buch-Overrides: top-level `print:` in books/<id>/export.yaml
CLI/Dashboard-Overlay: trim_size, layout_profile, illustration_mode, paper
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

TRIM_SIZES: dict[str, dict[str, Any]] = {
    "5.5x8.5": {
        "width_in": 5.5,
        "height_in": 8.5,
        "width_mm": 139.7,
        "height_mm": 215.9,
        "slug": "55x85",
    },
    "6x9": {
        "width_in": 6.0,
        "height_in": 9.0,
        "width_mm": 152.4,
        "height_mm": 228.6,
        "slug": "6x9",
    },
}

KDP_PAGE_LIMITS: dict[str, int] = {
    "white": 828,
    "cream": 776,
    "groundwood": 812,
}

LAYOUT_PROFILES: dict[str, dict[str, Any]] = {
    "classic": {
        "font_size_pt": 10.8,
        "line_height_pt": 13.6,
        "chapter_opening_mm": 32.0,
        "chapter_start": "next_page",
        "words_per_page": 280,
    },
    "long_classic": {
        "font_size_pt": 10.2,
        "line_height_pt": 12.5,
        "chapter_opening_mm": 32.0,
        "chapter_start": "next_page",
        "words_per_page": 320,
    },
}

ILLUSTRATION_MODES: dict[str, dict[str, Any]] = {
    "full_page": {
        "page_break_after": True,
        "max_height_ratio": None,
        "slug": "full",
    },
    "inline": {
        "page_break_after": False,
        "max_height_ratio": 0.45,
        "slug": "inline",
    },
}

CHAPTER_START_MODES = ("next_page", "recto")
PAPER_KINDS = tuple(KDP_PAGE_LIMITS.keys())
INK_KINDS = ("black",)
PRINT_OVERLAY_KEYS = (
    "trim_size",
    "layout_profile",
    "illustration_mode",
    "paper",
    "chapter_start",
    "bleed",
)

KDP_GUTTER_BANDS: tuple[tuple[int, float], ...] = (
    (150, 9.6),
    (300, 12.7),
    (500, 15.9),
    (700, 19.1),
    (828, 22.3),
)

KDP_MAX_PAGES_CREAM = KDP_PAGE_LIMITS["cream"]
KDP_SPINE_MM_PER_PAGE_CREAM = 0.0635
KDP_SPINE_MM_PER_PAGE = {
    "cream": 0.0635,
    "white": 0.0572,
    "groundwood": 0.0635,
}
KDP_BLEED_IN = 0.125
GUTTER_MAX_PASSES = 3
DEFAULT_TRIM_SIZE = "5.5x8.5"
DEFAULT_LAYOUT_PROFILE = "classic"
DEFAULT_ILLUSTRATION_MODE = "full_page"
DEFAULT_PAPER = "cream"
DEFAULT_INK = "black"
DEFAULT_CHAPTER_START = "next_page"

_TRIM_ALIASES = {
    "5.5x8.5": "5.5x8.5",
    "5.5×8.5": "5.5x8.5",
    "55x85": "5.5x8.5",
    "5,5x8,5": "5.5x8.5",
    "6x9": "6x9",
    "6×9": "6x9",
}

_PROFILE_ALIASES = {
    "classic": "classic",
    "long_classic": "long_classic",
    "long-classic": "long_classic",
}

_ILLUSTRATION_ALIASES = {
    "full_page": "full_page",
    "full-page": "full_page",
    "full": "full_page",
    "inline": "inline",
    "half_page": "inline",
    "half-page": "inline",
}


def kdp_gutter_mm(page_count: int) -> float:
    """KDP-Mindest-Bundsteg in mm nach Seitenzahl (ohne Beschnitt)."""
    n = max(1, int(page_count))
    for max_pages, gutter in KDP_GUTTER_BANDS:
        if n <= max_pages:
            return gutter
    return KDP_GUTTER_BANDS[-1][1]


def kdp_max_pages(paper: str) -> int:
    key = _as_str(paper, DEFAULT_PAPER).lower()
    if key not in KDP_PAGE_LIMITS:
        key = DEFAULT_PAPER
    return KDP_PAGE_LIMITS[key]


def kdp_spine_mm_per_page(paper: str = DEFAULT_PAPER) -> float:
    key = _as_str(paper, DEFAULT_PAPER).lower()
    return float(KDP_SPINE_MM_PER_PAGE.get(key, KDP_SPINE_MM_PER_PAGE_CREAM))


def kdp_spine_mm(page_count: int, paper: str = DEFAULT_PAPER) -> float:
    """KDP-Rueckenbreite: Seitenzahl x mm/Seite (creme/SW Standard 0,0635)."""
    return max(1, int(page_count)) * kdp_spine_mm_per_page(paper)


def wrap_width_in(
    page_count: int,
    trim_width_in: float | None = None,
    paper: str = DEFAULT_PAPER,
) -> float:
    """Gesamtbreite Wrap-PDF: Bleed + Rueckseite + Ruecken + Vorderseite + Bleed."""
    width = (
        TRIM_SIZES[DEFAULT_TRIM_SIZE]["width_in"]
        if trim_width_in is None
        else float(trim_width_in)
    )
    spine_in = kdp_spine_mm(page_count, paper) / 25.4
    return (2 * KDP_BLEED_IN) + (2 * width) + spine_in


def wrap_height_in(trim_height_in: float | None = None) -> float:
    height = (
        TRIM_SIZES[DEFAULT_TRIM_SIZE]["height_in"]
        if trim_height_in is None
        else float(trim_height_in)
    )
    return height + (2 * KDP_BLEED_IN)


def wrap_panel_width_in(trim_width_in: float | None = None) -> float:
    """Rueck- bzw. Vorderseitenbreite inkl. aussenliegendem Beschnitt."""
    width = (
        TRIM_SIZES[DEFAULT_TRIM_SIZE]["width_in"]
        if trim_width_in is None
        else float(trim_width_in)
    )
    return width + KDP_BLEED_IN


def kdp_gutter_band(page_count: int) -> int:
    """Obere Seitengrenze der Bundsteg-Bandbreite (150, 300, ...)."""
    n = max(1, int(page_count))
    for max_pages, _gutter in KDP_GUTTER_BANDS:
        if n <= max_pages:
            return max_pages
    return KDP_GUTTER_BANDS[-1][0]


def normalize_trim_size(value: Any, default: str = DEFAULT_TRIM_SIZE) -> str:
    raw = str(value or "").strip().lower().replace(" ", "")
    if not raw:
        return default
    return _TRIM_ALIASES.get(raw, default if raw not in TRIM_SIZES else raw)


def normalize_layout_profile(value: Any, default: str = DEFAULT_LAYOUT_PROFILE) -> str:
    raw = str(value or "").strip().lower()
    if not raw:
        return default
    return _PROFILE_ALIASES.get(raw, default if raw not in LAYOUT_PROFILES else raw)


def normalize_illustration_mode(
    value: Any, default: str = DEFAULT_ILLUSTRATION_MODE
) -> str:
    raw = str(value or "").strip().lower()
    if not raw:
        return default
    return _ILLUSTRATION_ALIASES.get(raw, default)


def normalize_paper(value: Any, default: str = DEFAULT_PAPER) -> str:
    raw = str(value or "").strip().lower()
    if raw in KDP_PAGE_LIMITS:
        return raw
    return default


def normalize_chapter_start(value: Any, default: str = DEFAULT_CHAPTER_START) -> str:
    raw = str(value or "").strip().lower().replace("-", "_")
    if raw in CHAPTER_START_MODES:
        return raw
    return default


def _as_float(value: Any, default: float) -> float:
    if value is None or value == "":
        return default
    return float(value)


def _as_str(value: Any, default: str) -> str:
    text = str(value).strip() if value is not None else ""
    return text or default


def _as_bool(value: Any, default: bool) -> bool:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = dict(base)
    for key, value in override.items():
        if (
            key in out
            and isinstance(out[key], dict)
            and isinstance(value, dict)
        ):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or {}


def apply_print_overlay(
    data: Mapping[str, Any], overlay: Mapping[str, Any] | None
) -> dict[str, Any]:
    """CLI/Job-Parameter ueber Serie+Buch legen. Leere Werte aendern nichts."""
    out = dict(data)
    if not overlay:
        return out
    for key in PRINT_OVERLAY_KEYS:
        value = overlay.get(key)
        if value is None or value == "":
            continue
        out[key] = value
        if key == "layout_profile":
            out["profile"] = value
        if key == "illustration_mode":
            illustrations = dict(out.get("illustrations") or {})
            illustrations["mode"] = value
            out["illustrations"] = illustrations
        if key == "chapter_start":
            chapter = dict(out.get("chapter") or {})
            chapter["start"] = value
            out["chapter"] = chapter
    return out


def _profile_mapping(data: Mapping[str, Any], layout_profile: str) -> dict[str, Any]:
    builtin = dict(LAYOUT_PROFILES.get(layout_profile) or LAYOUT_PROFILES[DEFAULT_LAYOUT_PROFILE])
    yaml_profiles = data.get("layout_profiles") or {}
    yaml_profile = yaml_profiles.get(layout_profile) if isinstance(yaml_profiles, Mapping) else None
    if not isinstance(yaml_profile, Mapping):
        return builtin
    font = yaml_profile.get("font") or {}
    chapter = yaml_profile.get("chapter") or {}
    estimate = yaml_profile.get("estimate") or {}
    if isinstance(font, Mapping):
        if font.get("size_pt") is not None:
            builtin["font_size_pt"] = float(font["size_pt"])
        if font.get("line_height_pt") is not None:
            builtin["line_height_pt"] = float(font["line_height_pt"])
    if yaml_profile.get("font_size_pt") is not None:
        builtin["font_size_pt"] = float(yaml_profile["font_size_pt"])
    if yaml_profile.get("line_height_pt") is not None:
        builtin["line_height_pt"] = float(yaml_profile["line_height_pt"])
    if isinstance(chapter, Mapping):
        if chapter.get("opening_space_mm") is not None:
            builtin["chapter_opening_mm"] = float(chapter["opening_space_mm"])
        if chapter.get("start"):
            builtin["chapter_start"] = normalize_chapter_start(
                chapter.get("start"), builtin["chapter_start"]
            )
    if yaml_profile.get("chapter_start"):
        builtin["chapter_start"] = normalize_chapter_start(
            yaml_profile.get("chapter_start"), builtin["chapter_start"]
        )
    if isinstance(estimate, Mapping) and estimate.get("words_per_page") is not None:
        builtin["words_per_page"] = int(estimate["words_per_page"])
    if yaml_profile.get("words_per_page") is not None:
        builtin["words_per_page"] = int(yaml_profile["words_per_page"])
    return builtin


@dataclass(frozen=True)
class PrintSpec:
    repo_root: Path
    trim_size: str = DEFAULT_TRIM_SIZE
    layout_profile: str = DEFAULT_LAYOUT_PROFILE
    illustration_mode: str = DEFAULT_ILLUSTRATION_MODE
    paper: str = DEFAULT_PAPER
    ink: str = DEFAULT_INK
    chapter_start: str = DEFAULT_CHAPTER_START
    bleed: bool = False
    trim_width_in: float = 5.5
    trim_height_in: float = 8.5
    trim_width_mm: float = 139.7
    trim_height_mm: float = 215.9
    font_family: str = "EB Garamond"
    font_regular: str = "assets/print-fonts/eb-garamond/EBGaramond.ttf"
    font_italic: str = "assets/print-fonts/eb-garamond/EBGaramond-Italic.ttf"
    font_size_pt: float = 10.8
    line_height_pt: float = 13.6
    chapter_opening_mm: float = 32.0
    first_line_indent_em: float = 1.2
    min_outer_mm: float = 12.7
    top_mm: float = 16.0
    bottom_mm: float = 18.0
    running_header_left: str = "author"
    running_header_right: str = "title"
    words_per_page: int = 280
    illustration_max_height_ratio: float | None = None
    enabled: bool = True

    @property
    def profile(self) -> str:
        return self.layout_profile

    @classmethod
    def from_dict(cls, data: Mapping[str, Any], repo_root: Path) -> "PrintSpec":
        layout_profile = normalize_layout_profile(
            data.get("layout_profile") or data.get("profile")
        )
        profile = _profile_mapping(data, layout_profile)
        trim_size = normalize_trim_size(data.get("trim_size"))
        trim_info = TRIM_SIZES[trim_size]
        trim = data.get("trim") or {}
        if not isinstance(trim, Mapping):
            trim = {}
        # Named trim_size wins over leftover series trim.width_in.
        trim_width_in = float(trim_info["width_in"])
        trim_height_in = float(trim_info["height_in"])
        if not data.get("trim_size") and trim.get("width_in") and trim.get("height_in"):
            trim_width_in = _as_float(trim.get("width_in"), trim_width_in)
            trim_height_in = _as_float(trim.get("height_in"), trim_height_in)
            inferred = _infer_trim_size(trim_width_in, trim_height_in)
            if inferred:
                trim_size = inferred
                trim_info = TRIM_SIZES[trim_size]

        font = data.get("font") or {}
        if not isinstance(font, Mapping):
            font = {}
        chapter = data.get("chapter") or {}
        if not isinstance(chapter, Mapping):
            chapter = {}
        paragraph = data.get("paragraph") or {}
        if not isinstance(paragraph, Mapping):
            paragraph = {}
        margins = data.get("margins") or {}
        if not isinstance(margins, Mapping):
            margins = {}
        header = data.get("running_header") or {}
        if not isinstance(header, Mapping):
            header = {}
        estimate = data.get("estimate") or {}
        if not isinstance(estimate, Mapping):
            estimate = {}
        illustrations = data.get("illustrations") or {}
        if not isinstance(illustrations, Mapping):
            illustrations = {}
        inline_cfg = illustrations.get("inline") or {}
        if not isinstance(inline_cfg, Mapping):
            inline_cfg = {}

        illustration_mode = normalize_illustration_mode(
            data.get("illustration_mode") or illustrations.get("mode")
        )
        mode_info = ILLUSTRATION_MODES[illustration_mode]
        max_height_ratio = mode_info["max_height_ratio"]
        if illustration_mode == "inline":
            max_height_ratio = _as_float(
                inline_cfg.get("max_height_ratio")
                or illustrations.get("max_height_ratio")
                or max_height_ratio,
                0.45,
            )

        font_size_pt = float(profile["font_size_pt"])
        line_height_pt = float(profile["line_height_pt"])
        if font.get("size_pt") is not None:
            font_size_pt = _as_float(font.get("size_pt"), font_size_pt)
        if font.get("line_height_pt") is not None:
            line_height_pt = _as_float(font.get("line_height_pt"), line_height_pt)

        chapter_start = normalize_chapter_start(
            data.get("chapter_start")
            or chapter.get("start")
            or profile.get("chapter_start")
        )
        chapter_opening_mm = _as_float(
            chapter.get("opening_space_mm"),
            float(profile["chapter_opening_mm"]),
        )
        words_per_page = max(1, int(profile["words_per_page"]))
        if estimate.get("words_per_page") is not None:
            words_per_page = max(1, int(_as_float(estimate.get("words_per_page"), words_per_page)))

        paper = normalize_paper(data.get("paper"))
        return cls(
            repo_root=Path(repo_root),
            trim_size=trim_size,
            layout_profile=layout_profile,
            illustration_mode=illustration_mode,
            paper=paper,
            ink=_as_str(data.get("ink"), DEFAULT_INK).lower() or DEFAULT_INK,
            chapter_start=chapter_start,
            bleed=_as_bool(data.get("bleed"), False),
            trim_width_in=trim_width_in,
            trim_height_in=trim_height_in,
            trim_width_mm=float(trim_info["width_mm"]),
            trim_height_mm=float(trim_info["height_mm"]),
            font_family=_as_str(font.get("family"), "EB Garamond"),
            font_regular=_as_str(
                font.get("regular"),
                "assets/print-fonts/eb-garamond/EBGaramond.ttf",
            ),
            font_italic=_as_str(
                font.get("italic"),
                "assets/print-fonts/eb-garamond/EBGaramond-Italic.ttf",
            ),
            font_size_pt=font_size_pt,
            line_height_pt=line_height_pt,
            chapter_opening_mm=chapter_opening_mm,
            first_line_indent_em=_as_float(
                paragraph.get("first_line_indent_em"), 1.2
            ),
            min_outer_mm=_as_float(margins.get("min_outer_mm"), 12.7),
            top_mm=_as_float(margins.get("top_mm"), 16.0),
            bottom_mm=_as_float(margins.get("bottom_mm"), 18.0),
            running_header_left=_as_str(header.get("left"), "author"),
            running_header_right=_as_str(header.get("right"), "title"),
            words_per_page=words_per_page,
            illustration_max_height_ratio=(
                float(max_height_ratio) if max_height_ratio is not None else None
            ),
            enabled=bool(data.get("enabled", True)),
        )

    @property
    def font_regular_path(self) -> Path:
        return (self.repo_root / self.font_regular).resolve()

    @property
    def font_italic_path(self) -> Path:
        return (self.repo_root / self.font_italic).resolve()

    @property
    def filename_slug(self) -> str:
        trim_slug = str(TRIM_SIZES.get(self.trim_size, {}).get("slug") or "55x85")
        illus = str(
            ILLUSTRATION_MODES.get(self.illustration_mode, {}).get("slug") or "full"
        )
        return f"{trim_slug}-{self.layout_profile}-{illus}"

    def kdp_max_pages(self) -> int:
        return kdp_max_pages(self.paper)

    def gutter_mm(self, page_count: int) -> float:
        return kdp_gutter_mm(page_count)

    def side_margin_mm(self, page_count: int) -> float:
        """Chromium: Innen = Aussen = max(Bundsteg, Mindest-Aussensteg)."""
        return max(self.gutter_mm(page_count), self.min_outer_mm)

    def type_height_mm(self) -> float:
        return max(1.0, self.trim_height_in * 25.4 - self.top_mm - self.bottom_mm)

    def type_width_mm(self, page_count: int) -> float:
        return max(1.0, self.trim_width_in * 25.4 - 2 * self.side_margin_mm(page_count))

    def illustration_max_height_mm(self) -> float:
        if self.illustration_mode == "inline":
            ratio = self.illustration_max_height_ratio or 0.45
            return self.type_height_mm() * ratio
        return 90.0

    def needs_rerender(self, assumed_pages: int, actual_pages: int) -> bool:
        assumed = round(self.side_margin_mm(assumed_pages), 1)
        actual = round(self.side_margin_mm(actual_pages), 1)
        return assumed != actual

    def scaled_words_per_page(self) -> int:
        """words_per_page ist auf 5.5x8.5 kalibriert; 6x9 skaliert ueber die Satzflaeche."""
        ref = TRIM_SIZES[DEFAULT_TRIM_SIZE]
        ref_area = (ref["width_in"] * 25.4 - 2 * self.min_outer_mm) * (
            ref["height_in"] * 25.4 - self.top_mm - self.bottom_mm
        )
        area = (self.trim_width_in * 25.4 - 2 * self.min_outer_mm) * (
            self.trim_height_in * 25.4 - self.top_mm - self.bottom_mm
        )
        scale = area / max(1.0, ref_area)
        return max(1, round(self.words_per_page * scale))

    def estimate_page_count(self, word_count: int, frontmatter_sections: int) -> int:
        body = max(1, round(max(0, int(word_count)) / self.scaled_words_per_page()))
        return max(1, int(frontmatter_sections) + body)

    def trim_css(self) -> str:
        w = f"{self.trim_width_in:.2f}".rstrip("0").rstrip(".")
        h = f"{self.trim_height_in:.2f}".rstrip("0").rstrip(".")
        return f"{w}in {h}in"

    def illustration_page_break_after(self) -> bool:
        return bool(
            ILLUSTRATION_MODES.get(self.illustration_mode, {}).get(
                "page_break_after", True
            )
        )


def _infer_trim_size(width_in: float, height_in: float) -> str | None:
    for key, info in TRIM_SIZES.items():
        if abs(float(info["width_in"]) - width_in) < 0.05 and abs(
            float(info["height_in"]) - height_in
        ) < 0.05:
            return key
    return None


def load_print_spec(
    repo_root: Path,
    meta: Mapping[str, Any] | None = None,
    overlay: Mapping[str, Any] | None = None,
) -> PrintSpec:
    series = load_yaml(Path(repo_root) / "config" / "print.yaml")
    book = (meta or {}).get("print") or {}
    if not isinstance(book, Mapping):
        book = {}
    merged = _deep_merge(series, book)
    merged = apply_print_overlay(merged, overlay)
    return PrintSpec.from_dict(merged, Path(repo_root))
