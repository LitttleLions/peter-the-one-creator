"""A+-Content fuer KDP aus den Buchdaten bauen.

Amazon KDP hat keine API fuer A+ Content; der Content-Manager ist ein
Webformular. Dieses Werkzeug erzeugt deshalb nur die Zutaten: einen
Modulplan mit Zielmassen, die zugeschnittenen Bilder und die Texte zum
Einfuegen. Der Upload bleibt eine begleitete Handarbeit.

Ausgabe unter ``books/<id>/work/aplus/``:

``modules.json``
    Plan: Module, Texte, Bilddateien, Zielmasse, Zeichenzaehlung, Hinweise.
``copy.md``
    Copy-Paste-Fassung fuer den Content-Manager (Modul fuer Modul).
``assets/*.jpg``
    Bilder in den Zielmassen (Mittiger Zuschnitt, JPEG q90).

Keine Netzwerkaufrufe, keine Kosten. Die Bildmasse folgen den Standardmodulen
von Amazon (970x600 Kopfmodul, 300x300 Dreibild-Modul); sie werden im Plan
mitgeschrieben, weil Amazon sie gelegentlich anpasst.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))

from lib.book_project import find_book as find_book_project  # noqa: E402
from lib.kdp_mapping import load_export_document  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
TEXT_SOFT_LIMIT = 300
SUMMARY_LIMIT = 1000
EPSILON = 3  # Zeichen Reserve fuer "..."


@dataclass(frozen=True)
class ModuleImage:
    role: str
    width: int
    height: int
    source: Path | None = None


@dataclass(frozen=True)
class Module:
    module_id: str
    title: str
    headline: str
    body: str
    images: tuple[ModuleImage, ...] = ()
    note: str = ""


@dataclass
class Plan:
    book_id: str
    book_title: str
    modules: list[Module] = field(default_factory=list)
    skipped: list[dict[str, str]] = field(default_factory=list)


def trim_text(text: str, limit: int) -> str:
    """Auf Wortgrenze kuerzen und mit Auslassungszeichen markieren."""
    clean = " ".join(str(text or "").split())
    if len(clean) <= limit:
        return clean
    cut = clean[: limit - EPSILON]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:") + "..."


def split_paragraphs(text: str) -> list[str]:
    return [part.strip() for part in str(text or "").split("\n\n") if part.strip()]


def chapter_images(book_root: Path) -> list[Path]:
    folder = book_root / "assets" / "chapter"
    if not folder.is_dir():
        return []
    found = [
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]
    return sorted(found, key=lambda path: path.name)


def pick_sources(
    book_root: Path,
    count: int,
    explicit: list[Path] | None = None,
) -> list[Path]:
    """Bildquellen waehlen: entweder uebergeben oder gleichmaessig verteilt."""
    if explicit:
        chosen = [path for path in explicit if path.is_file()]
        if len(chosen) < count:
            raise SystemExit(
                f"--images: {count} brauchbare Bilder noetig, {len(chosen)} gefunden"
            )
        return chosen[:count]
    available = chapter_images(book_root)
    if len(available) < count:
        return available
    step = len(available) / count
    return [available[min(len(available) - 1, int(index * step))] for index in range(count)]


def build_plan(
    meta: dict[str, Any],
    book_id: str,
    book_root: Path,
    explicit_images: list[Path] | None = None,
) -> Plan:
    title = str(meta.get("title") or book_id).strip()
    subtitle = str(meta.get("subtitle") or "").strip()
    series = str(meta.get("series") or "").strip()
    volume = meta.get("series_volume")
    description = split_paragraphs(meta.get("description") or "")
    summary = " ".join(str(meta.get("summary") or "").split())

    plan = Plan(book_id=book_id, book_title=title)
    sources = pick_sources(book_root, 4, explicit_images)

    head_body = trim_text(description[0] if description else summary, TEXT_SOFT_LIMIT)
    plan.modules.append(
        Module(
            module_id="hero",
            title="Standard-Bild mit Textueberlagerung (Kopfmodul)",
            headline=title,
            body=head_body,
            images=(
                ModuleImage(
                    role="hero",
                    width=970,
                    height=600,
                    source=sources[0] if sources else None,
                ),
            ),
            note="Headline kurz halten; sie liegt im Bildbereich.",
        )
    )

    three_body = trim_text(description[1] if len(description) > 1 else summary, TEXT_SOFT_LIMIT)
    thumbnails = tuple(
        ModuleImage(
            role=f"thumb-{index + 1}",
            width=300,
            height=300,
            source=sources[index + 1] if len(sources) > index + 1 else None,
        )
        for index in range(3)
    )
    plan.modules.append(
        Module(
            module_id="three",
            title="Standard-Drei-Bilder-und-Text",
            headline="TODO: Kurze Ueberschrift fuer das Dreibild-Modul",
            body=three_body,
            images=thumbnails,
            note="Bild 1-3 aus den Kapitelvignetten; Text aus der Beschreibung uebernommen.",
        )
    )

    series_headline = (
        f"{series} - Band {volume}" if series and volume not in (None, "") else series
    )
    plan.modules.append(
        Module(
            module_id="text",
            title="Standard-Textmodul",
            headline=series_headline or "TODO: Ueberschrift",
            body=trim_text(summary, SUMMARY_LIMIT),
            note="Reiner Text; nutzt die Zusammenfassung aus export.yaml.",
        )
    )

    if not (book_root / "assets" / "covers" / "logo.png").is_file():
        plan.skipped.append(
            {
                "module": "logo",
                "reason": "kein Logo-Asset (assets/covers/logo.png) vorhanden",
            }
        )
    if not sources:
        plan.skipped.append(
            {
                "module": "bilder",
                "reason": "keine Kapitelbilder unter assets/chapter/ gefunden",
            }
        )
    return plan


def render_image(source: Path, target: ModuleImage, destination: Path) -> Path:
    """Mittig auf das Zielmass zuschneiden (cover + center crop)."""
    with Image.open(source) as handle:
        image = handle.convert("RGB")
        source_ratio = image.width / image.height
        target_ratio = target.width / target.height
        if source_ratio > target_ratio:
            new_width = int(round(image.height * target_ratio))
            left = (image.width - new_width) // 2
            image = image.crop((left, 0, left + new_width, image.height))
        else:
            new_height = int(round(image.width / target_ratio))
            top = (image.height - new_height) // 2
            image = image.crop((0, top, image.width, top + new_height))
        image = image.resize((target.width, target.height), Image.LANCZOS)
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination, format="JPEG", quality=90, optimize=True)
    return destination


def _rel(path: Path | None) -> str | None:
    """Repo-relativer Pfad, sonst absolut (z. B. bei temporaeren Quellen)."""
    if path is None:
        return None
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def plan_as_json(plan: Plan, out_dir: Path) -> dict[str, Any]:
    return {
        "book_id": plan.book_id,
        "book_title": plan.book_title,
        "generated_by": "tools/aplus_build.py",
        "note": (
            "Amazon hat keine A+-API. Upload im KDP-Content-Manager von Hand; "
            "Masse vor dem Upload gegen die aktuelle Amazon-Vorgabe pruefen."
        ),
        "modules": [
            {
                "id": module.module_id,
                "title": module.title,
                "headline": module.headline,
                "body": module.body,
                "body_chars": len(module.body),
                "note": module.note,
                "images": [
                    {
                        "role": image.role,
                        "width": image.width,
                        "height": image.height,
                        "source": _rel(image.source),
                        "file": (
                            f"assets/{module.module_id}-{image.role}-{image.width}x{image.height}.jpg"
                            if image.source
                            else None
                        ),
                    }
                    for image in module.images
                ],
            }
            for module in plan.modules
        ],
        "skipped": plan.skipped,
    }


def write_copy_markdown(plan: Plan) -> str:
    lines = [
        f"# A+ Content: {plan.book_title}",
        "",
        "Copy-Paste-Fassung fuer den A+-Content-Manager. Die Bilder liegen in",
        "`assets/` in den genannten Massen.",
        "",
    ]
    for module in plan.modules:
        lines.append(f"## {module.title}")
        lines.append("")
        lines.append("**Headline**")
        lines.append("")
        lines.append("```text")
        lines.append(module.headline)
        lines.append("```")
        lines.append("")
        if module.body:
            lines.append(f"**Text** ({len(module.body)} Zeichen)")
            lines.append("")
            lines.append("```text")
            lines.append(module.body)
            lines.append("```")
            lines.append("")
        if module.images:
            lines.append("**Bilder**")
            lines.append("")
            for image in module.images:
                if image.source:
                    lines.append(
                        f"- `{module.module_id}-{image.role}-{image.width}x{image.height}.jpg`"
                        f" ({image.width}x{image.height} px)"
                    )
                else:
                    lines.append(
                        f"- {image.role}: kein Bild vorhanden ({image.width}x{image.height} px)"
                    )
            lines.append("")
        if module.note:
            lines.append(f"> {module.note}")
            lines.append("")
    if plan.skipped:
        lines.append("## Bewusst ausgelassen")
        lines.append("")
        for item in plan.skipped:
            lines.append(f"- **{item['module']}**: {item['reason']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(plan: Plan, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for module in plan.modules:
        for image in module.images:
            if not image.source:
                continue
            destination = out_dir / "assets" / (
                f"{module.module_id}-{image.role}-{image.width}x{image.height}.jpg"
            )
            written.append(render_image(image.source, image, destination))
    modules_path = out_dir / "modules.json"
    modules_path.write_text(
        json.dumps(plan_as_json(plan, out_dir), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    written.append(modules_path)
    copy_path = out_dir / "copy.md"
    copy_path.write_text(write_copy_markdown(plan), encoding="utf-8")
    written.append(copy_path)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="A+ Content (KDP) aus den Buchdaten vorbereiten"
    )
    parser.add_argument("--book", required=True, help="Buch-ID, z. B. die-sprache-des-anderen")
    parser.add_argument(
        "--out",
        help="Zielordner; Default books/<id>/work/aplus",
    )
    parser.add_argument(
        "--images",
        nargs="*",
        help="Bildquellen (Pfade); Default: Kapitelvignetten gleichmaessig verteilt",
    )
    parser.add_argument("--dry-run", action="store_true", help="nur Plan zeigen, nichts schreiben")
    args = parser.parse_args(argv)

    book = find_book_project(REPO_ROOT, args.book)
    if not book:
        print(f"Buch mit id={args.book} nicht gefunden", file=sys.stderr)
        return 2
    book_root = REPO_ROOT / book["book_root"]
    meta = load_export_document(REPO_ROOT / book["export_config"]).get("book") or {}
    explicit = [Path(item) for item in args.images] if args.images else None
    plan = build_plan(meta, str(book.get("id") or args.book), book_root, explicit)

    out_dir = Path(args.out) if args.out else book_root / "work" / "aplus"
    if not out_dir.is_absolute():
        out_dir = (REPO_ROOT / out_dir).resolve()
    if args.dry_run:
        print(json.dumps(plan_as_json(plan, out_dir), ensure_ascii=False, indent=2))
        print(f"# Dry-Run: nichts geschrieben (Ziel waere {out_dir})", file=sys.stderr)
        return 0

    written = write_outputs(plan, out_dir)
    print(f"A+ Content: {plan.book_title}")
    for module in plan.modules:
        print(f"  {module.module_id}: {module.title} ({len(module.body)} Zeichen)")
    for item in plan.skipped:
        print(f"  ausgelassen: {item['module']} ({item['reason']})")
    print("Geschrieben:")
    for path in written:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
