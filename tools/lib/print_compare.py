"""Vergleich mehrerer Print-Reports (Trim/Profil/Bilder/Seitenzahl/KDP-Limit)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping


def load_print_report(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("report_path", str(path))
    return data


def collect_print_reports(directory: Path) -> list[dict[str, Any]]:
    if not directory.is_dir():
        return []
    reports = [
        load_print_report(path)
        for path in sorted(directory.glob("*-print-report.json"))
    ]
    return reports


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def comparison_rows(reports: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for report in reports:
        page_count = _int(report.get("page_count"))
        kdp_max = _int(report.get("kdp_max_pages"), 776)
        within = bool(report.get("within_kdp_page_limit", page_count <= kdp_max))
        difference = page_count - kdp_max
        rows.append(
            {
                "trim_size": str(report.get("trim_size") or ""),
                "layout_profile": str(
                    report.get("layout_profile") or report.get("profile") or ""
                ),
                "illustration_mode": str(report.get("illustration_mode") or ""),
                "paper": str(report.get("paper") or "cream"),
                "page_count": page_count,
                "kdp_max_pages": kdp_max,
                "difference": difference,
                "within_kdp_page_limit": within,
                "status": "KDP COMPATIBLE" if within else "NOT KDP COMPATIBLE",
                "output_pdf": str(report.get("output_pdf") or ""),
                "report_path": str(report.get("report_path") or ""),
            }
        )
    return rows


def render_print_comparison_markdown(
    reports: Iterable[Mapping[str, Any]], title: str = ""
) -> str:
    rows = comparison_rows(reports)
    heading = title.strip() or "Print-Vergleich"
    lines = [
        f"# {heading}",
        "",
        "| Format | Satzprofil | Bilder | Papier | Seiten | KDP max | Differenz | Status |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        diff = row["difference"]
        diff_text = f"+{diff}" if diff > 0 else str(diff)
        lines.append(
            f"| {row['trim_size']} | {row['layout_profile']} | "
            f"{row['illustration_mode']} | {row['paper']} | {row['page_count']} | "
            f"{row['kdp_max_pages']} | {diff_text} | {row['status']} |"
        )
    lines.append("")
    for row in rows:
        if row["output_pdf"]:
            lines.append(f"- `{row['trim_size']}` / `{row['layout_profile']}` / "
                         f"`{row['illustration_mode']}`: `{row['output_pdf']}`")
    lines.append("")
    return "\n".join(lines)


def write_print_comparison(
    reports: Iterable[Mapping[str, Any]], dest: Path, title: str = ""
) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        render_print_comparison_markdown(reports, title=title),
        encoding="utf-8",
    )
    return dest
