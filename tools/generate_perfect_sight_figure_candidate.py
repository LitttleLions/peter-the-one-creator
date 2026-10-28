"""Generate a Higgsfield candidate for one Perfect Sight figure.

This tool is intentionally separate from ``generate_illustration.py``.  It
never writes into assets/chapter or assets/scene and never changes the active
figure version.  Use ``--dry-run`` first; a paid generation requires the
explicit ``--allow-paid-generation`` flag inherited by the Higgsfield tool.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
BOOK_ID = "perfect.sight"
BOOK_ROOT = REPO_ROOT / "books" / BOOK_ID
FIGURE_ROOT = BOOK_ROOT / "assets" / "figures"

PROFILES = {
    "historical-photograph": (
        "Create a faithful visual enhancement candidate based strictly on the supplied "
        "historical source photograph from a 1920 ophthalmology book. Preserve identity, "
        "pose, facial features, clothing, period character, composition, crop, background "
        "and documentary meaning. Improve only tonal range, clarity, contrast, scan damage "
        "and visual readability. Do not add, remove or invent people, objects, text, symbols, "
        "labels, background elements or medical information. Do not modernize the image."
    ),
    "historical-illustration": (
        "Create a faithful enhancement candidate for this historical 1920 medical-book "
        "illustration. Preserve the exact composition, anatomy, proportions, line structure "
        "and documentary character. Improve clarity and print readability only. Do not add "
        "or remove visual information and do not generate or alter text, labels, numbers, "
        "arrows, symbols or geometry."
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Erzeugt einen Higgsfield-Kandidaten für eine Perfect-Sight-Abbildung.")
    parser.add_argument("--figure", required=True)
    parser.add_argument("--profile", choices=tuple(PROFILES), required=True)
    parser.add_argument("--model", default="nano_banana_2")
    parser.add_argument("--resolution", default="2k")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-paid-generation", action="store_true")
    args = parser.parse_args()
    manifest_path = FIGURE_ROOT / "manifest.yaml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    record = next((item for item in data.get("figures", []) if item.get("id") == args.figure), None)
    if not record:
        raise SystemExit(f"Unbekannte Abbildung: {args.figure}")
    kind = str(record.get("kind") or "review")
    if kind in {"diagram", "eye_chart", "table_or_text"}:
        raise SystemExit(f"Generative Variante für {kind} ist geschützt; technische Bearbeitung verwenden.")
    source = BOOK_ROOT / str(record.get("original_path") or record.get("path") or "")
    if not source.exists():
        raise SystemExit(f"Originalbild fehlt: {source}")
    output = FIGURE_ROOT / "candidates" / "higgsfield" / f"{args.figure}-v01.png"
    prompt = PROFILES[args.profile]
    prompt_dir = BOOK_ROOT / "work" / "prompts" / "figures"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = prompt_dir / f"{args.figure}-{args.profile}.md"
    prompt_path.write_text(prompt + "\n", encoding="utf-8")
    command = [
        sys.executable,
        "tools/generate_illustration.py",
        "--book", BOOK_ID,
        "--chapter", str(record.get("chapter_id") or "000"),
        "--kind", "chapter",
        "--model", args.model,
        "--quality", args.resolution,
        "--image", str(source),
        "--no-reference",
        "--dry-run" if args.dry_run else "",
    ]
    command = [part for part in command if part]
    metadata = {
        "figure": args.figure,
        "profile": args.profile,
        "model": args.model,
        "resolution": args.resolution,
        "source": str(source.relative_to(BOOK_ROOT)),
        "candidate": str(output.relative_to(BOOK_ROOT)),
        "prompt_path": str(prompt_path.relative_to(BOOK_ROOT)),
        "command": command,
        "status": "planned" if args.dry_run else "candidate_pending_review",
        "paid_generation_explicit": args.allow_paid_generation,
    }
    meta_path = prompt_dir / f"{args.figure}-{args.profile}.json"
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Prompt: {prompt_path.relative_to(REPO_ROOT)}")
    print(f"Zielkandidat: {output.relative_to(REPO_ROOT)}")
    print("Kein automatischer Ersatz des Originals.")
    if args.dry_run:
        print("(dry-run: keine Higgsfield-Generierung)")
        return 0
    raise SystemExit(
        "Kandidaten-Workflow ist vorbereitet. Die direkte Higgsfield-Erzeugung "
        "wird erst nach Prüfung des Prompts und expliziter Freigabe ergänzt."
    )


if __name__ == "__main__":
    raise SystemExit(main())