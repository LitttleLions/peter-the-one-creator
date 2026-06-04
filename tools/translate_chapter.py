"""
translate_chapter.py
====================
Uebersetzt ein Kapitel (Szene fuer Szene oder als Ganzes) via
OpenRouter und schreibt das Ergebnis als Markdown-Datei.

Verwendung:
    # Dry-Run (zeigt Prompts, kein API-Call):
    python tools/translate_chapter.py --chapter 001 --style stylized --dry-run

    # Echter Lauf (schreibt v1-, v2-, ... pro Stil):
    python tools/translate_chapter.py --chapter 001 --style stylized

    # Auto-Status (in_progress / needs_review automatisch setzen):
    python tools/translate_chapter.py --chapter 001 --style stylized --auto-status

    # Anderes Modell:
    python tools/translate_chapter.py --chapter 001 --style middle --model openai/gpt-4o

Konvention fuer Output-Suffix:
    v1-stylized, v2-literal, v3-middle - wird automatisch aus
    --style und der Historie im Output-Verzeichnis abgeleitet.
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# UTF-8 fuer Windows cmd
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                      errors="replace")

import yaml

from lib.openrouter_client import OpenRouterClient, OpenRouterError
from lib.style_prompts import StylePrompts, StylePromptError
from lib.scene_splitter import (
    split_into_scenes, Scene, count_words,
)
from lib.status_manager import (
    BookState, load_state, save_state,
    mark_in_progress, mark_done, mark_pending,
    STATUS_DONE, STATUS_NEEDS_REVIEW,
)
from lib.log_writer import write_chapter_log


REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def find_book(book_id):
    data = load_yaml(REPO_ROOT / "config" / "books.yaml")
    books = data.get("books", [])
    if book_id is None:
        if not books:
            raise SystemExit("Keine Buecher in config/books.yaml")
        return books[0]
    for b in books:
        if b["id"] == book_id:
            return b
    raise SystemExit(f"Buch mit id={book_id} nicht gefunden")


def existing_translation_versions(chapters_dir, chapter_id, style):
    pattern = re.compile(
        rf"^{re.escape(chapter_id)}-translation-v(\d+)-{re.escape(style)}\.md$"
    )
    return sorted(
        [p for p in chapters_dir.iterdir() if pattern.match(p.name)],
        key=lambda p: int(pattern.match(p.name).group(1)),
    )


def next_translation_path(chapters_dir, chapter_id, style):
    existing = existing_translation_versions(chapters_dir, chapter_id, style)
    next_n = len(existing) + 1
    return chapters_dir / f"{chapter_id}-translation-v{next_n}-{style}.md"


def extract_de_title(translated_md):
    for line in translated_md.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            return s.lstrip("#").strip()
        return s
    return ""


# ---------------------------------------------------------------------------
# Pipeline-Schritte
# ---------------------------------------------------------------------------

def build_messages_for_scene(style_prompts, mode, book_cfg,
                             frontmatter, scene, rules_text):
    user_chunks = []
    if frontmatter:
        user_chunks.append(frontmatter)
        user_chunks.append("")
    user_chunks.append(scene.text)
    source_text = "\n".join(user_chunks)
    return style_prompts.build_messages(
        mode=mode,
        book_cfg=book_cfg,
        source_text=source_text,
        rules_text=rules_text,
    )


def translate_scene(client, messages, temperature, max_tokens):
    system = messages[0]["content"]
    user = messages[1]["content"]
    return client.chat(
        system=system,
        user=user,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def render_header(chapter_id, title_ru, book_title, mode, granularity):
    out = []
    out.append(f"# Kapitel {chapter_id}: {title_ru}")
    out.append("")
    out.append(f"*Buch: {book_title} - Alexei Tolstoi*")
    out.append(f"*Stil: **{mode}** (OpenRouter-Provider, "
               f"{granularity}-Granularitaet)*")
    out.append(f"*Erstellt am: "
               f"{datetime.now().isoformat(timespec='seconds')}*")
    out.append("")
    out.append("---")
    out.append("")
    return "\n".join(out)


def render_body_chapter(translated):
    return translated.rstrip() + "\n"


def render_body_scene(frontmatter, scene_translations):
    parts = []
    if frontmatter:
        parts.append(frontmatter.rstrip())
        parts.append("")
        parts.append("---")
        parts.append("")
    for sc, txt in scene_translations:
        parts.append(txt.rstrip())
        parts.append("")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Hauptprogramm
# ---------------------------------------------------------------------------

def parse_args():
    ap = argparse.ArgumentParser(
        description="Uebersetze ein Kapitel via OpenRouter."
    )
    ap.add_argument("--book", default=None,
                    help="Buch-ID (default: erstes aus books.yaml)")
    ap.add_argument("--chapter", required=True,
                    help="Kapitel-ID, z. B. '001'")
    ap.add_argument("--style",
                    choices=["literal", "middle", "stylized"],
                    help="Stilmodus (default: aus books.yaml: style_mode)")
    ap.add_argument("--model", default=None,
                    help="OpenRouter-Modellname (ueberschreibt .env / books.yaml)")
    ap.add_argument("--granularity", choices=["scene", "chapter"], default=None,
                    help="Szene-fuer-Szene oder ganzes Kapitel")
    ap.add_argument("--max-tokens", type=int, default=None,
                    help="max_tokens pro OpenRouter-Call")
    ap.add_argument("--temperature", type=float, default=None,
                    help="Ueberschreibt die stilmodus-spezifische Temperatur")
    ap.add_argument("--auto-status", action="store_true",
                    help="Setzt in_progress zu Beginn und needs_review am Ende")
    ap.add_argument("--no-review", action="store_true",
                    help="Mit --auto-status: direkt done setzen, nicht needs_review")
    ap.add_argument("--dry-run", action="store_true",
                    help="Baut die Prompts, sendet aber nichts an OpenRouter")
    ap.add_argument("--dry-run-first-scene", action="store_true",
                    help="Dry-Run nur fuer die erste Szene (sonst komplett)")
    ap.add_argument("--verbose", "-v", action="store_true",
                    help="Mehr Log-Ausgaben")
    return ap.parse_args()


def main():
    args = parse_args()
    book = find_book(args.book)

    # Stilmodus bestimmen
    mode = args.style or book.get("style_mode", "stylized")
    if mode not in ("literal", "middle", "stylized"):
        raise SystemExit(f"Ungueltiger Stilmodus: {mode}")

    # Buch-AI-Config
    ai_cfg = book.get("ai", {}) or {}
    granularity = args.granularity or ai_cfg.get("granularity", "scene")
    max_tokens = args.max_tokens or ai_cfg.get("max_tokens_per_scene", 6000)

    # Pipeline-AI-Defaults
    pipe = load_yaml(REPO_ROOT / "config" / "pipeline.yaml")
    ai_defaults = (pipe.get("pipeline", {})
                       .get("ai_defaults", {}) or {})

    # Style-Prompts laden
    try:
        sp = StylePrompts()
    except StylePromptError as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        return 2
    mode_cfg = sp.get_mode(mode)
    temperature = (
        args.temperature
        if args.temperature is not None
        else float(mode_cfg.get("temperature", 0.4))
    )

    # Regeln aus logic/ laden (nur wenn Modus rules_append will)
    rules_text = None
    if mode_cfg.get("rules_append") and book.get("ruleset_path"):
        rules_path = REPO_ROOT / book["ruleset_path"]
        if rules_path.exists():
            rules_text = rules_path.read_text(encoding="utf-8")
            if args.verbose:
                print(f"Regeln geladen: {rules_path} "
                      f"({len(rules_text)} Zeichen)")

    # Source-Datei
    chapters_dir = REPO_ROOT / book["output_dir"] / "chapters"
    src_path = chapters_dir / f"{args.chapter}-source.md"
    if not src_path.exists():
        print(f"FEHLER: Quelldatei nicht gefunden: {src_path}",
              file=sys.stderr)
        return 1

    frontmatter, scenes = split_into_scenes(src_path)
    if not scenes:
        print(f"WARNUNG: Keine Szenen in {src_path} gefunden - "
              f"ganze Datei wird als ein Block behandelt.",
              file=sys.stderr)
        full_text = src_path.read_text(encoding="utf-8")
        scenes = [Scene(number=1, title="", text=full_text)]
        frontmatter = ""

    print(f"=== Buch: {book['title']} ({book['id']}) ===")
    print(f"Kapitel: {args.chapter}")
    print(f"Stilmodus: {mode}  (rules_append="
          f"{mode_cfg.get('rules_append')})")
    print(f"Granularitaet: {granularity}")
    print(f"Szenen erkannt: {len(scenes)}")
    print(f"Modell: {ai_cfg.get('model', '(default)')}")
    print(f"Temperatur: {temperature}, max_tokens: {max_tokens}")
    if args.dry_run:
        print("** DRY-RUN - keine API-Calls **")
    print()

    # Status: in_progress (optional)
    state = None
    status_path = None
    if args.auto_status:
        status_path = REPO_ROOT / book["status_file"]
        if not status_path.exists():
            print(f"WARNUNG: Status-Datei fehlt ({status_path}), "
                  f"--auto-status wird ignoriert.", file=sys.stderr)
        else:
            state = load_state(status_path)
            mark_in_progress(state, args.chapter)
            save_state(state, status_path)
            print(f"-> {args.chapter} = in_progress")

    # Titel (RU) aus Status oder Frontmatter
    title_ru = ""
    if state is not None:
        for c in state.chapters:
            if c.id == args.chapter:
                title_ru = c.title_ru
                break
    if not title_ru and frontmatter:
        for line in frontmatter.splitlines():
            s = line.strip()
            if s.startswith("#"):
                title_ru = s.lstrip("#").strip()
                break
    if not title_ru:
        title_ru = f"Kapitel {args.chapter}"

    # OpenRouter-Client (nur wenn nicht dry-run)
    client = None
    if not args.dry_run:
        try:
            client = OpenRouterClient.from_env(
                model_override=args.model or ai_cfg.get("model"),
            )
        except OpenRouterError as e:
            print(f"FEHLER: {e}", file=sys.stderr)
            return 3
        if args.model:
            client.model = args.model
        print(f"OpenRouter-Client initialisiert "
              f"(Modell={client.model}).")
        print()

    # ---------------------------------------------------------------
    # Uebersetzung: chapter-Granularitaet vs. scene-Granularitaet
    # ---------------------------------------------------------------
    scene_translations = []   # type: ignore
    translated_full = None
    title_de = ""
    words_target = 0
    failed = False

    if granularity == "chapter":
        source_text = (
            (frontmatter + "\n\n" if frontmatter else "")
            + "\n\n".join(s.text for s in scenes)
        )
        messages = sp.build_messages(
            mode=mode,
            book_cfg=book,
            source_text=source_text,
            rules_text=rules_text,
        )
        if args.dry_run:
            print("---- DRY-RUN: System-Prompt (gekuerzt) ----")
            print(messages[0]["content"][:600] + "...")
            print()
            print("---- DRY-RUN: User-Prompt (gekuerzt) ----")
            print(messages[1]["content"][:1200] + "...")
            print()
            print(f"Total User-Laenge: {len(messages[1]['content'])}")
            print(f"Regeln angehaengt: {bool(rules_text)}")
            return 0
        assert client is not None
        print("-> Uebersetze ganzes Kapitel in einem Call...")
        try:
            translated_full = translate_scene(
                client, messages, temperature, max_tokens,
            )
        except OpenRouterError as e:
            print(f"FEHLER: {e}", file=sys.stderr)
            failed = True
        if not failed:
            title_de = extract_de_title(translated_full)
            words_target = count_words(translated_full)
    else:
        # Szene fuer Szene
        scene_translations = []
        dry_done = False
        for i, sc in enumerate(scenes, 1):
            print(f"-> Szene {i}/{len(scenes)} "
                  f"(## {sc.number}"
                  f"{'.' + sc.title if sc.title else ''}, "
                  f"{count_words(sc.text)} Woerter RU)...")
            messages = build_messages_for_scene(
                sp, mode, book, frontmatter, sc, rules_text,
            )
            if args.dry_run:
                if not dry_done:
                    print("---- DRY-RUN: System-Prompt (gekuerzt) ----")
                    print(messages[0]["content"][:600] + "...")
                    print()
                    print("---- DRY-RUN: User-Prompt (gekuerzt) ----")
                    print(messages[1]["content"][:1200] + "...")
                    print()
                    print(f"Total User-Laenge: "
                          f"{len(messages[1]['content'])}")
                    print(f"Regeln angehaengt: {bool(rules_text)}")
                    dry_done = True
                if args.dry_run_first_scene:
                    return 0
                # Im 'full' Dry-Run nur die erste Szene anzeigen
                continue
            assert client is not None
            try:
                txt = translate_scene(
                    client, messages, temperature, max_tokens,
                )
                scene_translations.append((sc, txt))
                words_target += count_words(txt)
            except OpenRouterError as e:
                print(f"   FEHLER bei Szene {i}: {e}", file=sys.stderr)
                failed = True
                break
        if args.dry_run:
            # Wenn wir hier ankommen ohne 'first_scene'-Abbruch,
            # sind wir durch alle Szenen gelaufen.
            return 0
        if scene_translations:
            title_de = extract_de_title(
                scene_translations[0][1]
            )

    if failed:
        print("Uebersetzung fehlgeschlagen.", file=sys.stderr)
        if status_path is not None and state is not None:
            mark_pending(state, args.chapter)
            save_state(state, status_path)
            print(f"-> {args.chapter} = pending "
                  f"(zurueckgesetzt wegen Fehler)")
        return 4

    # ---------------------------------------------------------------
    # Output-Datei schreiben
    # ---------------------------------------------------------------
    header = render_header(
        args.chapter, title_ru, book["title"], mode, granularity,
    )
    if granularity == "chapter":
        assert translated_full is not None
        body = header + render_body_chapter(translated_full)
    else:
        body = header + render_body_scene(frontmatter, scene_translations)

    out_path = next_translation_path(chapters_dir, args.chapter, mode)
    out_path.write_text(body, encoding="utf-8")
    print(f"Geschrieben: {out_path} ({words_target} Woerter DE)")

    # ---------------------------------------------------------------
    # Logfile schreiben
    # ---------------------------------------------------------------
    log_dir = REPO_ROOT / book["log_dir"]
    rules_applied = []
    if mode_cfg.get("rules_append"):
        rules_applied.append(
            f"Regelwerk aus {book.get('ruleset_path', '?')} an "
            f"User-Prompt angehaengt (Modus: {mode})"
        )
    rules_applied.extend([
        f"Stilmodus: {mode}",
        f"Modell: {ai_cfg.get('model', '(default)')}",
        f"Temperatur: {temperature}, max_tokens: {max_tokens}",
        f"Granularitaet: {granularity}",
    ])
    difficult = []
    if rules_text is not None:
        difficult.append(
            f"Regelwerk ist {len(rules_text)} Zeichen lang "
            f"(Prompt wird entsprechend gross)."
        )
    if granularity == "chapter":
        difficult.append(
            "chapter-Granularitaet: ein Call fuer das ganze Kapitel. "
            "Context-Limit beachten."
        )
    word_count_source = sum(count_words(s.text) for s in scenes)
    log_path = write_chapter_log(
        log_dir=log_dir,
        chapter_id=args.chapter,
        title_ru=title_ru,
        title_de=title_de or title_ru,
        words_source=word_count_source,
        words_target=words_target,
        rules_applied=rules_applied,
        difficult_spots=difficult,
        rule_adjustments=[],
        notes=(
            f"OpenRouter-Pipeline (Modell: "
            f"{ai_cfg.get('model', '(default)')}). "
            f"Output: {out_path.name}"
        ),
    )
    print(f"Logfile: {log_path}")

    # Status: needs_review / done (optional)
    if status_path is not None and state is not None:
        new_status = STATUS_DONE if args.no_review else STATUS_NEEDS_REVIEW
        mark_done(
            state, args.chapter,
            words_target=words_target,
            title_de=title_de or title_ru,
            needs_review=not args.no_review,
        )
        save_state(state, status_path)
        print(f"-> {args.chapter} = {new_status}")

    print()
    print("Fertig.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
