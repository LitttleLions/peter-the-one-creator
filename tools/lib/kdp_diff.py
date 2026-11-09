"""Soll/Ist-Vergleich für Phase 1. Schlägt keine Amazon-Änderung vor."""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

from lib.kdp_mapping import normalize_description


READ_ONLY_NOTE = "nur Anzeige, kein Schreiben nach Amazon"
NO_LOCAL_SOLL = "kein lokales Soll, Amazon-Wert bleibt unverändert"


def diff_listing(soll: dict[str, Any], ist: dict[str, Any] | None, *, fmt: str) -> list[dict[str, Any]]:
    remote = ist or {}
    spec = (soll.get("formats") or {}).get(fmt) or {}
    rows = [
        _text_row("title", soll.get("title"), remote.get("title")),
        _text_row("subtitle", soll.get("subtitle"), remote.get("subtitle")),
        _text_row("language", soll.get("language"), remote.get("language")),
        _text_row("publisherLabel", soll.get("publisherLabel"), remote.get("publisherLabel")),
        _author_row(soll.get("primaryAuthor") or {}, remote.get("primaryAuthor") or {}),
        _contributors_row(soll.get("contributors") or [], remote.get("contributors") or []),
        _description_row(soll.get("description") or "", remote.get("description") or ""),
        _bool_row("isPublicDomain", soll.get("isPublicDomain"), remote.get("isPublicDomain")),
        _bool_row("isAdultContent", soll.get("isAdultContent"), remote.get("isAdultContent")),
        _missing_local_row("keywords", soll.get("keywords"), remote.get("keywords")),
        _missing_local_row("categories", soll.get("categories"), remote.get("categories")),
        _missing_local_row("prices", soll.get("prices"), _amazon_prices(remote)),
        _missing_local_row("isbn", None, remote.get("isbn")),
        _missing_local_row("kdpSelect", None, remote.get("kdpSelect")),
        _missing_local_row("territory", None, remote.get("territory")),
        _missing_local_row("royaltyPlan", None, remote.get("royaltyPlan")),
        _file_row(
            "interior",
            spec.get("interior_path"),
            remote.get("interiorFileName"),
        ),
        _file_row(
            "cover",
            spec.get("cover_path"),
            remote.get("coverFileName"),
        ),
    ]
    for row in rows:
        row["apply"] = False
    return rows


def render_diff_markdown(book_id: str, fmt: str, rows: list[dict[str, Any]]) -> str:
    lines = [
        f"# KDP-Diff {book_id} ({fmt})",
        "",
        "Phase 1 vergleicht nur. Kein Feld wird nach Amazon geschrieben.",
        "",
    ]
    for row in rows:
        lines.append(f"## {row['field']}")
        lines.append(f"- status: {row['status']}")
        lines.append(f"- local: {_one_line(row.get('local'))}")
        lines.append(f"- amazon: {_one_line(row.get('amazon'))}")
        if row.get("note"):
            lines.append(f"- note: {row['note']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_diff(path: Path, markdown: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _text_row(field: str, local: Any, amazon: Any) -> dict[str, Any]:
    local_text = "" if local is None else str(local).strip()
    amazon_text = "" if amazon is None else str(amazon).strip()
    return {
        "field": field,
        "status": _presence(local_text, amazon_text, same=_fold(local_text) == _fold(amazon_text)),
        "local": local_text,
        "amazon": amazon_text,
        "note": READ_ONLY_NOTE,
    }


def _author_row(local: dict[str, Any], amazon: dict[str, Any]) -> dict[str, Any]:
    local_text = _author_label(local)
    amazon_text = _author_label(amazon if isinstance(amazon, dict) else {})
    return {
        "field": "primaryAuthor",
        "status": _presence(local_text, amazon_text, same=_fold(local_text) == _fold(amazon_text)),
        "local": local_text,
        "amazon": amazon_text,
        "note": READ_ONLY_NOTE,
    }


def _contributors_row(local: list[dict[str, Any]], amazon: list[Any]) -> dict[str, Any]:
    local_norm = _contributor_key(local)
    amazon_norm = _contributor_key(amazon if isinstance(amazon, list) else [])
    local_text = _contributor_label(local)
    amazon_text = _contributor_label(amazon if isinstance(amazon, list) else [])
    return {
        "field": "contributors",
        "status": _presence(local_text, amazon_text, same=local_norm == amazon_norm),
        "local": local_text,
        "amazon": amazon_text,
        "note": READ_ONLY_NOTE,
    }


def _description_row(local: str, amazon: str) -> dict[str, Any]:
    local_plain = normalize_description(local)
    amazon_plain = _html_to_text(amazon)
    return {
        "field": "description",
        "status": _presence(
            local_plain,
            amazon_plain,
            same=_fold(local_plain) == _fold(amazon_plain),
        ),
        "local": local_plain,
        "amazon": amazon_plain,
        "note": READ_ONLY_NOTE,
    }


def _bool_row(field: str, local: Any, amazon: Any) -> dict[str, Any]:
    if amazon is None or amazon == "":
        status = "amazon_missing"
    elif bool(local) == bool(amazon):
        status = "same"
    else:
        status = "different"
    return {
        "field": field,
        "status": status,
        "local": bool(local),
        "amazon": amazon,
        "note": READ_ONLY_NOTE,
    }


def _missing_local_row(field: str, local: Any, amazon: Any) -> dict[str, Any]:
    if local in (None, "", [], {}):
        status = "amazon_missing" if amazon in (None, "", [], {}) else "local_missing"
        return {
            "field": field,
            "status": status,
            "local": None,
            "amazon": amazon,
            "note": NO_LOCAL_SOLL,
        }
    return _text_row(field, local, amazon)


def _file_row(field: str, local_path: Any, amazon_name: Any) -> dict[str, Any]:
    local_name = Path(str(local_path)).name if local_path else ""
    remote_name = str(amazon_name or "").strip()
    return {
        "field": field,
        "status": _presence(local_name, remote_name, same=_fold(local_name) == _fold(remote_name)),
        "local": local_path,
        "amazon": remote_name,
        "note": "Pfad nur zur Anzeige, kein Upload",
    }


def _amazon_prices(remote: dict[str, Any]) -> dict[str, str] | None:
    prices = dict(remote.get("prices") or {})
    if remote.get("listPriceUsd"):
        prices.setdefault("USD", str(remote.get("listPriceUsd")))
    return prices or None


def _presence(local: str, amazon: str, *, same: bool) -> str:
    if not local and not amazon:
        return "same"
    if not local:
        return "local_missing"
    if not amazon:
        return "amazon_missing"
    return "same" if same else "different"


def _author_label(author: dict[str, Any]) -> str:
    return " ".join(
        part
        for part in (str(author.get("firstName") or "").strip(), str(author.get("lastName") or "").strip())
        if part
    )


def _contributor_key(items: list[Any]) -> list[tuple[str, str, str]]:
    rows = []
    for item in items:
        if not isinstance(item, dict):
            continue
        rows.append(
            (
                _fold(str(item.get("role") or "")),
                _fold(str(item.get("firstName") or "")),
                _fold(str(item.get("lastName") or "")),
            )
        )
    return sorted(rows)


def _contributor_label(items: list[Any]) -> str:
    parts = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = _author_label(item)
        role = str(item.get("role") or "").strip()
        parts.append(f"{role}: {name}".strip())
    return "; ".join(parts)


def _html_to_text(value: str) -> str:
    text = str(value or "")
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</p>", "\n\n", text)
    text = re.sub(r"(?i)<[^>]+>", "", text)
    text = html.unescape(text)
    return normalize_description(text)


def _fold(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def _one_line(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("\r\n", "\n").replace("\n", " / ")
