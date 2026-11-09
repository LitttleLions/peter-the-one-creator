"""Soll-Listing aus export.yaml für den KDP-Adapter.

Liest nur `book.*` plus die top-level Blöcke `website`, `marketing` und
`amazon`. `book.yaml` ist hier keine Quelle: Autor und Titel einer Chronik
weichen dort vom Export ab.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any

import yaml


LANGUAGE_TO_KDP = {
    "de": "German",
    "de-de": "German",
}

EDITOR_ORG = "Motivatier Classics"
TITLE_ID_RE = re.compile(r"^[A-Z0-9]{10,14}$")
ASIN_RE = re.compile(r"/dp/([A-Z0-9]{10})(?:[/?#]|$)", re.IGNORECASE)
STAMP_RE = re.compile(r"(\d{8}-\d{6})")
KINDLE_COVER_NAMES = ("cover.jpg", "cover.jpeg", "cover.png", "cover.webp")
PRINT_COVER_NAMES = (
    "cover-print.png",
    "cover-print.jpg",
    "cover-print.jpeg",
    "cover-print.webp",
)


class KdpMatchStop(Exception):
    """0 oder mehr als 1 Treffer. Es wird nichts geraten und nichts geschrieben."""

    def __init__(self, message: str, candidates: list[dict[str, Any]] | None = None):
        super().__init__(message)
        self.candidates = candidates or []


def load_export_document(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"export.yaml fehlt: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise SystemExit(f"export.yaml ist kein Mapping: {path}")
    return data


def map_kdp_soll(
    export: dict[str, Any],
    *,
    book_root: Path,
    style: str,
) -> dict[str, Any]:
    book = export.get("book") or {}
    if not isinstance(book, dict):
        raise SystemExit("export.yaml book: ist kein Mapping")
    title = str(book.get("title") or "").strip()
    author = str(book.get("author") or "").strip()
    if not title or not author:
        raise SystemExit("export.yaml braucht book.title und book.author")

    website = export.get("website") or {}
    marketing = export.get("marketing") or {}
    amazon = export.get("amazon") or {}
    if not isinstance(website, dict):
        website = {}
    if not isinstance(marketing, dict):
        marketing = {}
    if not isinstance(amazon, dict):
        amazon = {}

    kindle_cfg = amazon.get("kindle") or {}
    paperback_cfg = amazon.get("paperback") or {}
    if not isinstance(kindle_cfg, dict):
        kindle_cfg = {}
    if not isinstance(paperback_cfg, dict):
        paperback_cfg = {}

    url_asin = asin_from_store_url(_store_url(website, marketing))
    kindle_asin = str(kindle_cfg.get("asin") or amazon.get("asin") or url_asin or "").strip()
    paperback_asin = str(paperback_cfg.get("asin") or "").strip()

    author_parts = split_person_name(author)
    description = normalize_description(str(book.get("description") or ""))
    language = map_kdp_language(str(book.get("language") or ""))

    return {
        "marketplace": str(amazon.get("marketplace") or "DE"),
        "title": title,
        "subtitle": str(book.get("subtitle") or "").strip(),
        "primaryAuthor": author_parts,
        "contributors": build_contributors(book),
        "publisherLabel": str(book.get("publisher") or "").strip(),
        "language": language,
        "description": description,
        "isPublicDomain": False,
        "isAdultContent": False,
        "keywords": _optional_list(amazon.get("keywords")),
        "categories": _optional_list(amazon.get("categories")),
        "prices": _optional_prices(kindle_cfg),
        "asin": kindle_asin,
        "formats": {
            "kindle": {
                "enabled": bool(kindle_cfg.get("enabled", True)),
                "title_id": str(kindle_cfg.get("title_id") or "").strip(),
                "asin": kindle_asin,
                "interior_path": _rel(book_root, newest_epub(book_root, style)),
                "cover_path": _rel(book_root, kindle_cover(book_root, book)),
            },
            "paperback": {
                "enabled": bool(paperback_cfg.get("enabled", False)),
                "title_id": str(paperback_cfg.get("title_id") or "").strip(),
                "asin": paperback_asin,
                "interior_path": _rel(book_root, newest_paperback_interior(book_root, style)),
                "cover_path": _rel(book_root, print_cover(book_root)),
            },
        },
    }


def split_person_name(name: str) -> dict[str, str]:
    cleaned = " ".join(str(name or "").split())
    if not cleaned or cleaned == EDITOR_ORG:
        return {"firstName": "", "lastName": cleaned}
    parts = cleaned.split(" ")
    if len(parts) == 1:
        return {"firstName": "", "lastName": parts[0]}
    return {"firstName": parts[0], "lastName": " ".join(parts[1:])}


def build_contributors(book: dict[str, Any]) -> list[dict[str, str]]:
    contributors: list[dict[str, str]] = []
    translator = str(book.get("translator") or "").strip()
    if translator:
        person = split_person_name(translator)
        contributors.append({"role": "Translator", **person})
    if str(book.get("translator_label") or "").strip():
        contributors.append(
            {"role": "Editor", "firstName": "", "lastName": EDITOR_ORG}
        )
    return contributors


def map_kdp_language(language: str) -> str:
    token = str(language or "").strip()
    mapped = LANGUAGE_TO_KDP.get(token.casefold())
    if mapped:
        return mapped
    return token


def normalize_description(text: str) -> str:
    raw = str(text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    paragraphs = []
    for part in re.split(r"\n\s*\n", raw):
        collapsed = re.sub(r"[ \t]*\n[ \t]*", " ", part)
        collapsed = re.sub(r"[ \t]+", " ", collapsed).strip()
        if collapsed:
            paragraphs.append(collapsed)
    return "\n\n".join(paragraphs)


def asin_from_store_url(url: str) -> str:
    match = ASIN_RE.search(str(url or "").strip())
    if not match:
        return ""
    return match.group(1).upper()


def match_kdp_title(
    soll: dict[str, Any],
    *,
    fmt: str,
    bookshelf: dict[str, Any],
    catalog: dict[str, Any],
    cache: dict[str, Any],
) -> dict[str, str]:
    """title_id, sonst ASIN, sonst exakter Titel plus Nachname.

    Der Bookshelf-Scan des Skills liefert nur titleId und Format. Ein
    Katalogtreffer wird deshalb nur verbunden, wenn der Katalogschlüssel
    selbst eine Bookshelf-titleId ist oder der Metadaten-Cache den Titel
    schon gelesen hat. Sonst Stopp.
    """
    refs = [
        item
        for item in (bookshelf.get("refs") or [])
        if isinstance(item, dict) and item.get("format") == fmt and item.get("titleId")
    ]
    title_ids = {str(item["titleId"]) for item in refs}
    spec = (soll.get("formats") or {}).get(fmt) or {}
    wanted_id = str(spec.get("title_id") or "").strip()
    wanted_asin = str(spec.get("asin") or "").strip().upper()

    if wanted_id:
        if wanted_id in title_ids:
            return {"title_id": wanted_id, "asin": wanted_asin, "via": "title_id"}
        raise KdpMatchStop(
            f"Gespeicherte title_id {wanted_id} steht nicht im Bookshelf ({fmt}).",
            _bookshelf_candidates(refs),
        )

    cache_books = [
        item
        for item in (cache.get("books") or [])
        if isinstance(item, dict) and item.get("format") == fmt
    ]
    catalog_books = [
        item for item in (catalog.get("books") or []) if isinstance(item, dict)
    ]

    if wanted_asin:
        cache_hits = [
            item
            for item in cache_books
            if str(item.get("asin") or "").upper() == wanted_asin
            and str(item.get("titleId") or "") in title_ids
        ]
        key_hits = [
            item
            for item in catalog_books
            if _catalog_asin(item, fmt).upper() == wanted_asin
            and str(item.get("key") or "") in title_ids
        ]
        return _one_hit(
            cache_hits,
            key_hits,
            fmt=fmt,
            via="asin",
            empty=(
                f"ASIN {wanted_asin} ist keinem Bookshelf-Titel ({fmt}) zugeordnet. "
                "Der Katalog hat keine titleId; bitte bind --title-id."
            ),
            many=f"ASIN {wanted_asin} trifft mehr als einen {fmt}-Titel.",
            refs=refs,
        )

    title = str(soll.get("title") or "")
    last_name = str((soll.get("primaryAuthor") or {}).get("lastName") or "")
    cache_hits = [
        item
        for item in cache_books
        if str(item.get("titleId") or "") in title_ids
        and _same_title(title, str(item.get("title") or ""))
        and _author_has_token(str(item.get("author") or _author_text(item)), last_name)
    ]
    key_hits = [
        item
        for item in catalog_books
        if str(item.get("key") or "") in title_ids
        and _same_title(title, str(item.get("title") or ""))
        and _author_has_token(str(item.get("author") or ""), last_name)
    ]
    catalog_named = [
        item
        for item in catalog_books
        if _same_title(title, str(item.get("title") or ""))
        and _author_has_token(str(item.get("author") or ""), last_name)
    ]
    if len(cache_hits) == 1 and not key_hits:
        hit = cache_hits[0]
        return {
            "title_id": str(hit.get("titleId") or ""),
            "asin": str(hit.get("asin") or ""),
            "via": "cache_title",
        }
    if len(cache_hits) > 1 or len(key_hits) > 1 or (cache_hits and key_hits and _ids(cache_hits) != _ids(key_hits)):
        raise KdpMatchStop(
            f"Titel {title!r} plus Autor {last_name!r} trifft mehr als einen {fmt}-Titel.",
            _cache_candidates(cache_hits) + _catalog_candidates(key_hits or catalog_named),
        )
    if len(key_hits) == 1 and (not cache_hits or _ids(cache_hits) == _ids(key_hits)):
        hit = key_hits[0]
        return {
            "title_id": str(hit.get("key") or ""),
            "asin": _catalog_asin(hit, fmt),
            "via": "catalog_key",
        }
    note = (
        "Bookshelf-Scan liefert nur titleId und Format, keinen Titel. "
        "Ohne title_id, ASIN oder Cache-Treffer wird nichts zugeordnet."
    )
    raise KdpMatchStop(
        f"Kein eindeutiger {fmt}-Treffer für {title!r} / {last_name!r}. {note}",
        _catalog_candidates(catalog_named) + _bookshelf_candidates(refs),
    )


def newest_epub(book_root: Path, style: str) -> Path | None:
    folder = book_root / "exports" / style / "book" / "epub"
    return _newest_stamped(folder.glob("*.epub") if folder.is_dir() else [])


def newest_paperback_interior(book_root: Path, style: str) -> Path | None:
    folder = book_root / "exports" / style / "book" / "print"
    if not folder.is_dir():
        return None
    paths = [
        path
        for path in folder.glob("*.pdf")
        if path.name.endswith("-paperback-interior.pdf")
    ]
    return _newest_stamped(paths)


def kindle_cover(book_root: Path, book: dict[str, Any]) -> Path | None:
    cover = book.get("cover") or {}
    image_path = str(cover.get("image_path") or "").strip() if isinstance(cover, dict) else ""
    if image_path:
        candidate = book_root / image_path
        if candidate.is_file():
            return candidate
    covers = book_root / "assets" / "covers"
    for name in KINDLE_COVER_NAMES:
        candidate = covers / name
        if candidate.is_file():
            return candidate
    return None


def print_cover(book_root: Path) -> Path | None:
    covers = book_root / "assets" / "covers"
    for name in PRINT_COVER_NAMES:
        candidate = covers / name
        if candidate.is_file():
            return candidate
    return None


def upsert_amazon_join(
    text: str,
    *,
    fmt: str,
    title_id: str,
    asin: str,
) -> str:
    if fmt not in {"kindle", "paperback"}:
        raise SystemExit(f"Unbekanntes Format: {fmt}")
    if not TITLE_ID_RE.fullmatch(title_id):
        raise SystemExit(f"title_id hat nicht die Form einer KDP-Titel-ID: {title_id}")
    asin_value = str(asin or "").strip().upper()
    if asin_value and not re.fullmatch(r"[A-Z0-9]{10}", asin_value):
        raise SystemExit(f"ASIN hat nicht 10 Zeichen: {asin_value}")

    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    span = _amazon_span(lines)
    if span is None:
        block = _fresh_amazon_block(fmt, title_id, asin_value)
        suffix = "" if text.endswith(("\n", "\r")) or not text else newline
        return text + suffix + newline + block.replace("\n", newline)

    start, end = span
    block_lines = lines[start:end]
    updated = _set_format_fields(block_lines, fmt, title_id, asin_value)
    merged = lines[:start] + updated + lines[end:]
    trailer = newline if text.endswith(("\n", "\r")) else ""
    return newline.join(merged) + trailer


def _store_url(website: dict[str, Any], marketing: dict[str, Any]) -> str:
    override = str(marketing.get("amazon_url") or "").strip()
    if override:
        return override
    return str(website.get("amazon_url") or "").strip()


def _optional_list(value: Any) -> list[str] | None:
    if not isinstance(value, list):
        return None
    items = [str(item).strip() for item in value if str(item).strip()]
    return items or None


def _optional_prices(kindle_cfg: dict[str, Any]) -> dict[str, str] | None:
    prices = {}
    eur = str(kindle_cfg.get("price_eur") or "").strip()
    usd = str(kindle_cfg.get("price_usd") or "").strip()
    if eur:
        prices["EUR"] = eur
    if usd:
        prices["USD"] = usd
    return prices or None


def _rel(book_root: Path, path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(book_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _newest_stamped(paths) -> Path | None:
    found = [path for path in paths if path.is_file()]
    if not found:
        return None

    def sort_key(path: Path) -> tuple[str, float]:
        match = STAMP_RE.search(path.name)
        return (match.group(1) if match else "", path.stat().st_mtime)

    return max(found, key=sort_key)


def _catalog_asin(item: dict[str, Any], fmt: str) -> str:
    if fmt == "paperback":
        return str(item.get("printAsin") or "")
    if fmt == "hardcover":
        return str(item.get("hardcoverAsin") or "")
    return str(item.get("digitalAsin") or "")


def _same_title(local: str, remote: str) -> bool:
    return _fold(local) == _fold(remote) and bool(_fold(local))


def _author_has_token(author: str, token: str) -> bool:
    needle = _fold(token)
    if not needle:
        return False
    return re.search(rf"(?<!\w){re.escape(needle)}(?!\w)", _fold(author)) is not None


def _author_text(item: dict[str, Any]) -> str:
    author = item.get("primaryAuthor") or {}
    if isinstance(author, dict):
        return f"{author.get('firstName') or ''} {author.get('lastName') or ''}"
    return str(author or "")


def _fold(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", str(value or "")).strip()).casefold()


def _ids(items: list[dict[str, Any]]) -> set[str]:
    found = set()
    for item in items:
        found.add(str(item.get("titleId") or item.get("key") or ""))
    found.discard("")
    return found


def _one_hit(
    cache_hits: list[dict[str, Any]],
    key_hits: list[dict[str, Any]],
    *,
    fmt: str,
    via: str,
    empty: str,
    many: str,
    refs: list[dict[str, Any]],
) -> dict[str, str]:
    if len(cache_hits) > 1 or len(key_hits) > 1 or (
        cache_hits and key_hits and _ids(cache_hits) != _ids(key_hits)
    ):
        raise KdpMatchStop(
            many,
            _cache_candidates(cache_hits) + _catalog_candidates(key_hits),
        )
    if len(cache_hits) == 1:
        hit = cache_hits[0]
        return {
            "title_id": str(hit.get("titleId") or ""),
            "asin": str(hit.get("asin") or ""),
            "via": via,
        }
    if len(key_hits) == 1:
        hit = key_hits[0]
        return {
            "title_id": str(hit.get("key") or ""),
            "asin": _catalog_asin(hit, fmt),
            "via": via,
        }
    raise KdpMatchStop(
        empty,
        _cache_candidates(cache_hits) + _catalog_candidates(key_hits) + _bookshelf_candidates(refs),
    )


def _bookshelf_candidates(refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [
        {"source": "bookshelf", "titleId": item.get("titleId"), "format": item.get("format")}
        for item in refs[:20]
    ]
    if len(refs) > 20:
        rows.append({"source": "bookshelf", "omitted": len(refs) - 20})
    return rows


def _catalog_candidates(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "source": "catalog",
            "key": item.get("key"),
            "title": item.get("title"),
            "author": item.get("author"),
            "digitalAsin": item.get("digitalAsin"),
            "printAsin": item.get("printAsin"),
        }
        for item in items[:20]
    ]


def _cache_candidates(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "source": "cache",
            "titleId": item.get("titleId"),
            "format": item.get("format"),
            "title": item.get("title"),
            "asin": item.get("asin"),
        }
        for item in items[:20]
    ]


def _amazon_span(lines: list[str]) -> tuple[int, int] | None:
    start = None
    for index, line in enumerate(lines):
        if line.startswith("amazon:"):
            start = index
            break
    if start is None:
        return None
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if re.match(r"^[A-Za-z0-9_]+:", lines[index]):
            end = index
            break
    return start, end


def _fresh_amazon_block(fmt: str, title_id: str, asin: str) -> str:
    kindle_id = title_id if fmt == "kindle" else ""
    kindle_asin = asin if fmt == "kindle" else ""
    paper_id = title_id if fmt == "paperback" else ""
    paper_asin = asin if fmt == "paperback" else ""
    paper_enabled = "true" if fmt == "paperback" else "false"
    return (
        "amazon:\n"
        "  marketplace: DE\n"
        "  kindle:\n"
        "    enabled: true\n"
        f"    title_id: {_yaml_quote(kindle_id)}\n"
        f"    asin: {_yaml_quote(kindle_asin)}\n"
        "  paperback:\n"
        f"    enabled: {paper_enabled}\n"
        f"    title_id: {_yaml_quote(paper_id)}\n"
        f"    asin: {_yaml_quote(paper_asin)}\n"
    )


def _set_format_fields(
    block_lines: list[str],
    fmt: str,
    title_id: str,
    asin: str,
) -> list[str]:
    section = _section_span(block_lines, fmt)
    if section is None:
        addition = [
            f"  {fmt}:",
            "    enabled: false" if fmt == "paperback" else "    enabled: true",
            f"    title_id: {_yaml_quote(title_id)}",
            f"    asin: {_yaml_quote(asin)}",
        ]
        return block_lines + addition
    start, end = section
    body = block_lines[start:end]
    body = _replace_or_insert_key(body, "title_id", _yaml_quote(title_id))
    body = _replace_or_insert_key(body, "asin", _yaml_quote(asin))
    return block_lines[:start] + body + block_lines[end:]


def _section_span(block_lines: list[str], fmt: str) -> tuple[int, int] | None:
    start = None
    for index, line in enumerate(block_lines):
        if re.match(rf"^  {re.escape(fmt)}:\s*$", line):
            start = index
            break
    if start is None:
        return None
    end = len(block_lines)
    for index in range(start + 1, len(block_lines)):
        if re.match(r"^  [A-Za-z0-9_]+:\s*$", block_lines[index]):
            end = index
            break
    return start, end


def _replace_or_insert_key(section: list[str], key: str, rendered: str) -> list[str]:
    pattern = re.compile(rf"^(\s*){re.escape(key)}\s*:")
    for index, line in enumerate(section):
        if pattern.match(line):
            indent = pattern.match(line).group(1) or "    "
            section[index] = f"{indent}{key}: {rendered}"
            return section
    section.append(f"    {key}: {rendered}")
    return section


def _yaml_quote(value: str) -> str:
    if value == "":
        return "''"
    return "'" + value.replace("'", "''") + "'"
