"""Create a safe, book-local inventory and contact sheets for figure assets."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent
BOOK_ID = "perfect.sight"
BOOK_ROOT = REPO_ROOT / "books" / BOOK_ID
FIGURES = BOOK_ROOT / "assets" / "figures"
MANIFEST = FIGURES / "manifest.yaml"


def make_contact_sheets(records: list[dict], per_sheet: int = 16) -> list[Path]:
    out_dir = FIGURES / "contact-sheets"
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for start in range(0, len(records), per_sheet):
        subset = records[start : start + per_sheet]
        sheet = Image.new("RGB", (1600, 1800), "white")
        draw = ImageDraw.Draw(sheet)
        for local, record in enumerate(subset):
            path = BOOK_ROOT / str(record.get("path") or "")
            if not path.exists():
                continue
            with Image.open(path) as source:
                image = source.convert("RGB")
                image.thumbnail((360, 360), Image.Resampling.LANCZOS)
                col = local % 4
                row = local // 4
                x = 20 + col * 395 + (360 - image.width) // 2
                y = 20 + row * 440
                sheet.paste(image, (x, y))
                draw.text((20 + col * 395, y + 370), record["id"], fill="black")
                draw.text((20 + col * 395, y + 392), f"scan page {record.get('source_page', '?')}", fill="black")
        target = out_dir / f"contact-sheet-{start // per_sheet + 1:02d}.jpg"
        sheet.save(target, quality=90, optimize=True)
        paths.append(target)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Analysiert die Perfect-Sight-Abbildungen ohne Originale zu verändern.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not MANIFEST.exists():
        raise SystemExit(f"Manifest fehlt: {MANIFEST}")
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    records = data.get("figures") or []
    for record in records:
        path = BOOK_ROOT / str(record.get("path") or "")
        if path.exists():
            with Image.open(path) as image:
                record["dimensions"] = {"width": image.width, "height": image.height}
        record.setdefault("kind", "review")
        record.setdefault("status", "original_only")
        record.setdefault("original_path", record.get("path", ""))
        record.setdefault("active_path", record.get("path", ""))
        record.setdefault("candidate_paths", [])
        record.setdefault("approved_path", "")
    if args.dry_run:
        print(f"{len(records)} Bilder inventarisiert (dry-run)")
        return 0
    data["figures"] = records
    MANIFEST.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    sheets = make_contact_sheets(records)
    report = FIGURES / "analysis-report.md"
    lines = ["# Perfect Sight – Bildinventar", "", f"Bilder: {len(records)}", "", "| ID | Scan-Seite | Maße | Kategorie | Status |", "|---|---:|---:|---|---|"]
    for record in records:
        dims = record.get("dimensions") or {}
        lines.append(f"| {record['id']} | {record.get('source_page', '')} | {dims.get('width', '')}×{dims.get('height', '')} | {record.get('kind', 'review')} | {record.get('status', 'original_only')} |")
    lines += ["", "## Kontaktbögen", ""] + [f"- `{path.relative_to(BOOK_ROOT).as_posix()}`" for path in sheets]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Manifest aktualisiert: {MANIFEST.relative_to(REPO_ROOT)}")
    print(f"Kontaktbögen: {len(sheets)}")
    print(f"Bericht: {report.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())