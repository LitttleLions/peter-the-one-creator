"""Non-generative technical processing for one Perfect Sight figure.

Original files are never changed. Output goes to candidates/technical/.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

REPO_ROOT = Path(__file__).resolve().parent.parent
BOOK_ROOT = REPO_ROOT / "books" / "perfect.sight"
MANIFEST = BOOK_ROOT / "assets" / "figures" / "manifest.yaml"


def main() -> int:
    parser = argparse.ArgumentParser(description="Technische, nicht-generative Bildverbesserung.")
    parser.add_argument("--figure", required=True)
    parser.add_argument("--profile", choices=("technical-cleanup",), default="technical-cleanup")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    record = next((item for item in data.get("figures", []) if item.get("id") == args.figure), None)
    if not record:
        raise SystemExit(f"Unbekannte Abbildung: {args.figure}")
    source = BOOK_ROOT / str(record.get("original_path") or record.get("path") or "")
    if not source.exists():
        raise SystemExit(f"Originalbild fehlt: {source}")
    target = BOOK_ROOT / "assets" / "figures" / "candidates" / "technical" / f"{args.figure}-v01.jpg"
    if target.exists() and not args.overwrite:
        raise SystemExit(f"Kandidat existiert bereits: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        result = ImageOps.exif_transpose(image).convert("RGB")
        result = ImageEnhance.Contrast(result).enhance(1.08)
        result = ImageEnhance.Sharpness(result).enhance(1.12)
        result = result.filter(ImageFilter.MedianFilter(size=3))
        result.save(target, format="JPEG", quality=92, optimize=True)
    candidates = list(record.get("candidate_paths") or [])
    relative = target.relative_to(BOOK_ROOT).as_posix()
    if relative not in candidates:
        candidates.append(relative)
    record["candidate_paths"] = candidates
    record["technical_candidate"] = relative
    record["status"] = "candidate"
    data["figures"] = data.get("figures") or []
    MANIFEST.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"Technischer Kandidat: {target.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())