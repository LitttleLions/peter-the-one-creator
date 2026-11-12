"""Titelbild (Druckcover) aus einer Prompt-Datei mit Higgsfield erzeugen.

Liest den Abschnitt ``## Prompt`` aus ``books/<id>/work/prompts/higgsfield/<datei>.md``
(Handarbeit, Typografie-Block aus ``tools/cover_text.py``), ruft
``higgsfield generate create`` auf und legt das Ergebnis als
``assets/covers/cover-print.jpg`` ab. Ein vorhandenes Cover wird vorher als
``cover-print-vor-<stempel>.jpg`` gesichert, nichts wird geloescht.

Aufruf::

    python tools/generate_cover.py --book die-sprache-des-anderen \\
        --prompt cover-print-4k-20261112-v3.md --dry-run
    python tools/generate_cover.py --book die-sprache-des-anderen \\
        --prompt cover-print-4k-20261112-v3.md

Danach ``python tools/build_cover.py --book <id> --page-count <n>`` fuer den Wrap.
Jeder Lauf kostet Higgsfield-Credits; das Werkzeug macht genau einen Versuch.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from generate_illustration import (  # noqa: E402
    fetch_image_bytes,
    find_first_url,
    higgsfield_executable,
)
from lib.book_project import find_book as find_book_project  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL = "gpt_image_2_5"


def read_prompt(path: Path) -> str:
    """Prompt-Abschnitt als eine Zeile (die CLI nimmt keine Zeilenumbrueche)."""
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^## Prompt\s*\n(.*)\Z", text, re.S | re.M)
    if not match:
        raise SystemExit(f"Kein Abschnitt '## Prompt' in {path}")
    body = match.group(1).split("\n## ")[0]
    return " ".join(line.strip() for line in body.splitlines() if line.strip())


def build_command(prompt: str, aspect: str, resolution: str, quality: str) -> list[str]:
    exe = higgsfield_executable() or "higgsfield"
    return [
        exe, "generate", "create", MODEL,
        "--prompt", prompt,
        "--aspect_ratio", aspect,
        "--resolution", resolution,
        "--quality", quality,
        "--wait", "--json",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book", required=True)
    parser.add_argument("--prompt", required=True, help="Dateiname unter work/prompts/higgsfield/")
    parser.add_argument("--aspect-ratio", default="2:3")
    parser.add_argument("--resolution", default="4k")
    parser.add_argument("--quality", default="medium")
    parser.add_argument("--dry-run", action="store_true", help="Befehl zeigen, nichts erzeugen")
    args = parser.parse_args()

    book = find_book_project(REPO_ROOT, args.book)
    book_root = REPO_ROOT / book["root"] if "root" in book else REPO_ROOT / "books" / args.book
    prompt_file = book_root / "work" / "prompts" / "higgsfield" / args.prompt
    if not prompt_file.is_file():
        raise SystemExit(f"Prompt-Datei fehlt: {prompt_file}")
    prompt = read_prompt(prompt_file)
    command = build_command(prompt, args.aspect_ratio, args.resolution, args.quality)

    print(f"Prompt: {prompt_file.name} ({len(prompt)} Zeichen), Modell {MODEL}, "
          f"{args.aspect_ratio} {args.resolution} {args.quality}")
    if args.dry_run:
        print("Trockenlauf, nichts erzeugt.")
        return 0

    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=1800)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    covers = book_root / "assets" / "covers"
    covers.mkdir(parents=True, exist_ok=True)
    (covers.parent.parent / "work" / "prompts" / "higgsfield" / f"cover-generate-{stamp}.json").write_text(
        completed.stdout or completed.stderr, encoding="utf-8"
    )
    if completed.returncode != 0:
        print(completed.stderr or completed.stdout, file=sys.stderr)
        return 1
    try:
        url = find_first_url(json.loads(completed.stdout))
    except json.JSONDecodeError:
        url = find_first_url(completed.stdout)
    if not url:
        print("FEHLER: keine Bild-URL im Ergebnis.", file=sys.stderr)
        return 1

    from PIL import Image

    image = Image.open(io.BytesIO(fetch_image_bytes(url))).convert("RGB")
    target = covers / "cover-print.jpg"
    if target.exists():
        target.rename(covers / f"cover-print-vor-{stamp}.jpg")
    image.save(target, "JPEG", quality=92, dpi=(300, 300))
    print(f"Gespeichert: {target} ({image.width}x{image.height})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
