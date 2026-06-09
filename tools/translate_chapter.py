"""
translate_chapter.py
====================
Uebersetzt Szenen oder ein ganzes Kapitel via OpenRouter.
Szenenlaeufe schreiben nur Szenendateien; Kapitelversionen entstehen
separat durch tools/assemble_chapter.py.

Verwendung:
    # Dry-Run (zeigt Prompts, kein API-Call):
    python tools/translate_chapter.py --chapter 001 --style stil-03-branderson --dry-run

    # Echter Szenenlauf (schreibt scenes/de/<style>/NNN/scene-XX.md):
    python tools/translate_chapter.py --chapter 001 --style stil-03-branderson

    # Auto-Status (in_progress / needs_review automatisch setzen):
    python tools/translate_chapter.py --chapter 001 --style stil-03-branderson --auto-status

    # Anderes Modell:
    python tools/translate_chapter.py --chapter 001 --style stil-02-poetisch --model openai/gpt-4o

Kapitelversionen:
    python tools/assemble_chapter.py --chapter 001 --style stil-03-branderson
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

from lib.book_project import find_book as find_book_project
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
from lib.log_writer import append_to_log
from lib.models_registry import (
    load_models_registry, ModelError as ModelsModelError,
)
from lib.degeneration import detect_degeneration
from lib.output_paths import (
    book_output_root,
    de_scene_path,
    list_ru_scene_paths,
    next_translation_path as next_assembled_translation_path,
    parse_scene_number,
    prompt_path,
    source_chapter_path,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def find_book(book_id):
    return find_book_project(REPO_ROOT, book_id)


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


def format_last_usage(client) -> str:
    usage = getattr(client, "last_usage", None) or {}
    response_meta = (
        client.response_meta_summary()
        if hasattr(client, "response_meta_summary")
        else ""
    )
    if not usage:
        if response_meta:
            return f"Tokens: keine Usage-Daten; {response_meta}"
        return "Tokens: keine Usage-Daten"
    preferred = ["prompt_tokens", "completion_tokens", "total_tokens"]
    parts = []
    for key in preferred:
        if key in usage:
            parts.append(f"{key}={usage[key]}")
    for key in sorted(usage):
        if key not in preferred and isinstance(usage[key], int):
            parts.append(f"{key}={usage[key]}")
    if response_meta:
        parts.append(response_meta)
    return "Tokens: " + ", ".join(parts)


# Maximale Anzahl Retries bei Degeneration (1 = ein Retry,
# bevor endgueltig abgebrochen wird)
DEGENERATION_MAX_RETRIES = 1


def safe_translate_with_check(client, messages, temperature, max_tokens,
                              expected_language=None, label=""):
    """
    Wie translate_scene, aber mit Degeneration-Check und einem
    automatischen Retry. Liefert (text, degeneration_warnings) oder
    raises OpenRouterError.
    """
    text = translate_scene(client, messages, temperature, max_tokens)
    warnings = []

    for attempt in range(DEGENERATION_MAX_RETRIES + 1):
        result = detect_degeneration(text, expected_language=expected_language)
        if result.get("ok", True):
            if warnings:
                return text, warnings
            return text, []
        # Degeneration erkannt
        reason = result.get("reason", "unbekannt")
        if attempt < DEGENERATION_MAX_RETRIES:
            if label:
                print(f"   [{label}] Degeneration erkannt, Retry: "
                      f"{reason[:80]}", file=sys.stderr)
            warnings.append(reason)
            text = translate_scene(client, messages, temperature, max_tokens)
        else:
            # Letzter Versuch immer noch degeneriert
            warnings.append(reason)
            if label:
                print(f"   [{label}] Degeneration nach Retry immer noch da: "
                      f"{reason[:80]}", file=sys.stderr)
            return text, warnings

    return text, warnings


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


def render_scene_single(scene_number, translated_text):
    """Einzelne Szene als Markdown-Block fuer Einzeldatei."""
    out = []
    out.append(f"## Szene {scene_number}")
    out.append("")
    out.append(translated_text.rstrip())
    out.append("")
    return "\n".join(out)


def render_manual_prompt(messages, target_path, chapter_id, mode):
    out = [
        f"# Workspace-Prompt Kapitel {chapter_id}",
        "",
        f"*Stil: {mode}*",
        f"*Zielpfad: {target_path}*",
        "",
        "## System",
        "",
        messages[0]["content"].rstrip(),
        "",
        "## User",
        "",
        messages[1]["content"].rstrip(),
        "",
    ]
    return "\n".join(out)


def scene_translations_complete(output_root, chapter_id, mode, scenes):
    return all(
        de_scene_path(output_root, chapter_id, sc.number, mode).exists()
        for sc in scenes
    )


def chapter_translations_complete(output_root, chapter_id, mode):
    ru_paths = list_ru_scene_paths(output_root, chapter_id)
    if not ru_paths:
        return False
    for ru_path in ru_paths:
        scene_number = parse_scene_number(ru_path, chapter_id)
        if scene_number is None:
            return False
        if not de_scene_path(output_root, chapter_id, scene_number, mode).exists():
            return False
    return True


# ---------------------------------------------------------------------------
# Hauptprogramm
# ---------------------------------------------------------------------------

def parse_args():
    ap = argparse.ArgumentParser(
        description="Uebersetze ein Kapitel via OpenRouter."
    )
    ap.add_argument("--book", default=None,
                    help="Buch-ID (default: erstes Buchpaket)")
    ap.add_argument("--chapter", required=True,
                    help="Kapitel-ID, z. B. '001'")
    ap.add_argument("--scene", default=None,
                    help="Nur eine einzelne Szene übersetzen (z.B. '01')")
    ap.add_argument("--style",
                    help="Style-Profil aus books/<id>/styles/ (default: book.yaml: style_mode)")
    ap.add_argument("--model", default=None,
                    help="OpenRouter-Modellname (ueberschreibt .env / book.yaml)")
    ap.add_argument("--provider",
                    choices=["openrouter", "prompt_file", "workspace_ai", "manual_codex"],
                    default="openrouter",
                    help="openrouter ruft die API auf; prompt_file/workspace_ai schreiben Anweisungen")
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
    ap.add_argument("--overwrite", action="store_true",
                    help="Vorhandene Überschreibungen überschreiben (statt versionieren)")
    ap.add_argument("--timeout", type=int, default=120,
                    help="Timeout pro OpenRouter-Call in Sekunden (default: 120)")
    ap.add_argument("--verbose", "-v", action="store_true",
                    help="Mehr Log-Ausgaben")
    return ap.parse_args()


def main():
    args = parse_args()
    book = find_book(args.book)

    # Style-Profil bestimmen
    mode = args.style or book.get("style_mode", "stil-03-branderson")

    # Buch-AI-Config
    ai_cfg = book.get("ai", {}) or {}
    granularity = args.granularity or ai_cfg.get("granularity", "scene")
    max_tokens = args.max_tokens or ai_cfg.get("max_tokens_per_scene", 6000)
    prompt_only = args.provider in ("prompt_file", "workspace_ai", "manual_codex")

    chosen_model = f"({args.provider})"
    model_info = {
        "name": "Workspace/Prompt",
        "provider": args.provider,
        "description": "Promptdatei oder Arbeitsanweisung fuer eine Workspace-KI",
    }
    if args.provider == "openrouter":
        # Modell bestimmen (Prioritaet: --model > book.yaml > registry.default_for(book) > registry.fallback())
        try:
            models_reg = load_models_registry()
        except ModelsModelError as e:
            print(f"FEHLER: {e}", file=sys.stderr)
            return 2
        chosen_model = (
            args.model
            or ai_cfg.get("model")
            or models_reg.default_for(book["id"])
            or models_reg.fallback()
        )
        try:
            model_info = models_reg.validate(chosen_model)
        except ModelsModelError as e:
            print(f"FEHLER: {e}", file=sys.stderr)
            return 2
        if args.verbose:
            print(f"Modell gewaehlt: {model_info['name']} ({model_info['provider']})")
            print(f"  {model_info['description']}")

    # Pipeline-AI-Defaults
    pipe = load_yaml(REPO_ROOT / "config" / "pipeline.yaml")
    ai_defaults = (pipe.get("pipeline", {})
                       .get("ai_defaults", {}) or {})

    # Style-Prompts laden
    try:
        sp = StylePrompts(profiles_dir=REPO_ROOT / book["styles_dir"])
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
    output_root = book_output_root(REPO_ROOT, book)
    src_path = source_chapter_path(output_root, args.chapter)
    if not src_path.exists():
        print(f"FEHLER: Quelldatei nicht gefunden: {src_path}",
              file=sys.stderr)
        return 1

    # Szenen aus Source-Dateien lesen (Phase 1b: scenes/ru/NNN/scene-NN.md)
    scene_files_src = list_ru_scene_paths(output_root, args.chapter)
    if scene_files_src:
        # Szenen aus aufgeteilten Dateien lesen
        scenes = []
        frontmatter = ""
        for sf in scene_files_src:
            text = sf.read_text(encoding="utf-8")
            # Szenen-Nummer aus Dateiname extrahieren
            num = parse_scene_number(sf, args.chapter)
            if num is not None:
                # Nur eine Szene wenn --scene angegeben
                if args.scene and int(args.scene) != num:
                    continue
                # Heading-Zeile extrahieren für Titel
                title = ""
                for line in text.splitlines():
                    hm = re.match(r"^##\s+\d+\.?\s*(.*?)\s*$", line)
                    if hm:
                        title = hm.group(1).strip()
                        break
                scenes.append(Scene(number=num, title=title, text=text))
        if not scenes:
            print(f"WARNUNG: Keine Szenen fuer Kapitel {args.chapter} gefunden.",
                  file=sys.stderr)
    else:
        # Fallback: Aus NNN-source.md splitten (Legacy-Modus)
        frontmatter, scenes = split_into_scenes(src_path)
        if not scenes:
            print(f"WARNUNG: Keine Szenen in {src_path} gefunden - "
                  f"ganze Datei wird als ein Block behandelt.",
                  file=sys.stderr)
            full_text = src_path.read_text(encoding="utf-8")
            scenes = [Scene(number=1, title="", text=full_text)]
            frontmatter = ""

    if not scenes:
        print(f"FEHLER: Keine passende Szene fuer Kapitel {args.chapter} gefunden.",
              file=sys.stderr)
        return 1

    print(f"=== Buch: {book['title']} ({book['id']}) ===")
    print(f"Kapitel: {args.chapter}")
    print(f"Stil: {mode}  (rules_append="
          f"{mode_cfg.get('rules_append')})")
    print(f"Granularitaet: {granularity}")
    print(f"Szenen erkannt: {len(scenes)}")
    print(f"Modell: {chosen_model} ({model_info['name']}, {model_info['provider']})")
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

    # OpenRouter-Client (nur wenn nicht dry-run und nicht prompt_only)
    client = None
    if not args.dry_run and args.provider == "openrouter":
        try:
            client = OpenRouterClient.from_env(
                model_override=chosen_model,
            )
        except OpenRouterError as e:
            print(f"FEHLER: {e}", file=sys.stderr)
            return 3
        client.timeout_sec = float(args.timeout)
        if args.model:
            client.model = args.model
        print(f"OpenRouter-Client initialisiert "
              f"(Modell={client.model}).")
        print()

    # ---------------------------------------------------------------
    # Uebersetzung: chapter-Granularitaet vs. scene-Granularitaet
    # ---------------------------------------------------------------
    scene_files = []    # Liste von dicts: {number, translated, error, ru_words}
    prompt_files = []
    translated_full = None
    title_de = ""
    words_target = 0
    failed_scenes = 0

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
        if prompt_only:
            target = next_assembled_translation_path(output_root, args.chapter, mode)
            p_path = prompt_path(output_root, args.chapter, mode)
            prompt_text = render_manual_prompt(
                messages, target.relative_to(output_root), args.chapter, mode
            )
            if args.dry_run:
                print("---- DRY-RUN: Ziel ----")
                print(target.relative_to(output_root))
                print()
                print("---- DRY-RUN: Prompt (gekuerzt) ----")
                print(prompt_text[:1800] + "...")
                return 0
            p_path.parent.mkdir(parents=True, exist_ok=True)
            p_path.write_text(prompt_text, encoding="utf-8")
            print(f"Prompt geschrieben: {p_path.relative_to(output_root)}")
            print(f"Ziel fuer manuelle Kapiteluebersetzung: {target.relative_to(output_root)}")
            return 0
        if args.dry_run:
            print("---- DRY-RUN: System-Prompt (gekuerzt) ----")
            print(messages[0]["content"][:600] + "...")
            print()
            print("---- DRY-RUN: User-Prompt (gekuerzt) ----")
            print(messages[1]["content"][:1200] + "...")
            print()
            print(f"Total User-Laenge: {len(messages[1]['content'])}")
            print(f"Style-Profil angehaengt: {bool(mode_cfg.get('profile_text'))}")
            print(f"Legacy-Regeln angehaengt: {bool(rules_text)}")
            return 0
        assert client is not None
        client.model = chosen_model
        print("-> Uebersetze ganzes Kapitel in einem Call...")
        try:
            translated_full, _warn = safe_translate_with_check(
                client, messages, temperature, max_tokens,
                expected_language=book.get("target_lang", "deutsch"),
                label="chapter",
            )
            print(f"   {format_last_usage(client)}")
        except OpenRouterError as e:
            print(f"FEHLER: {e}", file=sys.stderr)
            failed_scenes = 1
        if not failed_scenes:
            title_de = extract_de_title(translated_full)
            words_target = count_words(translated_full)
    else:
        # Szene fuer Szene – JEDE SZENE IN EIGENE DATEI
        for i, sc in enumerate(scenes, 1):
            sf = {"number": sc.number, "translated": None, "error": None,
                  "ru_words": count_words(sc.text)}
            existing_scene_path = de_scene_path(
                output_root, args.chapter, sc.number, mode,
            )
            if existing_scene_path.exists() and not args.overwrite:
                existing_text = existing_scene_path.read_text(encoding="utf-8")
                sf["translated"] = existing_text
                words_target += count_words(existing_text)
                scene_files.append(sf)
                print(f"-> Szene {i}/{len(scenes)} "
                      f"(## {sc.number}) bereits vorhanden: "
                      f"{existing_scene_path.relative_to(output_root)}")
                continue
            print(f"-> Szene {i}/{len(scenes)} "
                  f"(## {sc.number}"
                  f"{'.' + sc.title if sc.title else ''}, "
                  f"{sf['ru_words']} Woerter RU)...")
            messages = build_messages_for_scene(
                sp, mode, book, frontmatter, sc, rules_text,
            )
            if prompt_only:
                target = de_scene_path(output_root, args.chapter, sc.number, mode)
                p_path = prompt_path(output_root, args.chapter, mode, sc.number)
                prompt_text = render_manual_prompt(
                    messages, target.relative_to(output_root), args.chapter, mode
                )
                if args.dry_run:
                    if i == 1:
                        print("---- DRY-RUN: Ziel ----")
                        print(target.relative_to(output_root))
                        print()
                        print("---- DRY-RUN: Prompt (gekuerzt) ----")
                        print(prompt_text[:1800] + "...")
                    if args.dry_run_first_scene:
                        return 0
                    continue
                p_path.parent.mkdir(parents=True, exist_ok=True)
                p_path.write_text(prompt_text, encoding="utf-8")
                prompt_files.append(p_path)
                print(f"   -> Prompt: {p_path.relative_to(output_root)}")
                continue
            if args.dry_run:
                if i == 1:
                    print("---- DRY-RUN: System-Prompt (gekuerzt) ----")
                    print(messages[0]["content"][:600] + "...")
                    print()
                    print("---- DRY-RUN: User-Prompt (gekuerzt) ----")
                    print(messages[1]["content"][:1200] + "...")
                    print()
                    print(f"Total User-Laenge: "
                          f"{len(messages[1]['content'])}")
                    print(f"Style-Profil angehaengt: {bool(mode_cfg.get('profile_text'))}")
                    print(f"Legacy-Regeln angehaengt: {bool(rules_text)}")
                if args.dry_run_first_scene:
                    return 0
                continue

            assert client is not None
            client.model = chosen_model
            try:
                txt, _warn = safe_translate_with_check(
                    client, messages, temperature, max_tokens,
                    expected_language=book.get("target_lang", "deutsch"),
                    label=f"szene {i}",
                )
                print(f"   {format_last_usage(client)}")
                sf["translated"] = txt

                # Sofort in eigene Szenen-Translationsdatei schreiben
                if args.overwrite:
                    # Direkt überschreiben ohne Version
                    s_path = de_scene_path(
                        output_root, args.chapter, sc.number, mode,
                    )
                else:
                    s_path = de_scene_path(
                        output_root, args.chapter, sc.number, mode,
                    )
                    if s_path.exists():
                        existing_text = s_path.read_text(encoding="utf-8")
                        sf["translated"] = existing_text
                        words_target += count_words(existing_text)
                        print(f"   -> {s_path.relative_to(output_root)} "
                              f"existiert, ueberspringe ohne --overwrite")
                        scene_files.append(sf)
                        continue
                s_body = render_scene_single(sc.number, txt)
                s_path.parent.mkdir(parents=True, exist_ok=True)
                s_path.write_text(s_body, encoding="utf-8")
                words_target += count_words(txt)
                print(f"   -> {s_path.relative_to(output_root)} "
                      f"({count_words(txt)} Woerter DE)")

            except OpenRouterError as e:
                print(f"   FEHLER bei Szene {i}: {e}", file=sys.stderr)
                sf["error"] = str(e)[:200]
                failed_scenes += 1
                # NICHT abbrechen – weiter mit naechster Szene

            scene_files.append(sf)

        if args.dry_run:
            return 0

        if scene_files:
            first_ok = next((sf for sf in scene_files if sf["translated"]), None)
            if first_ok:
                title_de = extract_de_title(first_ok["translated"])

    # ---------------------------------------------------------------
    # Output schreiben: Kapitelmodus erzeugt eine Kapiteldatei,
    # Szenenmodus schreibt bewusst nur Einzeldateien.
    # ---------------------------------------------------------------
    out_path = None
    output_note = ""

    if prompt_only:
        output_note = (
            f"Prompt/Workspace-Anweisungen: {len(prompt_files)} Datei(en) unter "
            f"prompts/. Ziel: scenes/de/{mode}/{args.chapter}/scene-NN.md"
        )
        print(f"Prompt/Workspace-Anweisungen geschrieben: {len(prompt_files)}")
    elif granularity == "scene" and failed_scenes == len(scenes):
        print("ALLE Szenen fehlgeschlagen.", file=sys.stderr)
        if status_path is not None and state is not None:
            mark_pending(state, args.chapter)
            save_state(state, status_path)
            print(f"-> {args.chapter} = pending "
                  f"(zurueckgesetzt wegen Fehler)")
        return 4
    elif granularity == "chapter":
        header = render_header(
            args.chapter, title_ru, book["title"], mode, granularity,
        )
        assert translated_full is not None
        body = header + render_body_chapter(translated_full)
        out_path = next_assembled_translation_path(output_root, args.chapter, mode)
        out_path.write_text(body, encoding="utf-8")
        status_mark = ""
        if failed_scenes:
            status_mark = f" (! {failed_scenes} Szenen fehlgeschlagen)"
        output_note = f"Output: {out_path.relative_to(output_root)}."
        print(f"Geschrieben: {out_path} ({words_target} Woerter DE){status_mark}")
    else:
        complete = chapter_translations_complete(output_root, args.chapter, mode)
        output_note = (
            f"Einzeldateien: scenes/de/{mode}/{args.chapter}/scene-NN.md. "
            "Keine Kapitelversion erzeugt; dafuer separat "
            f"`python tools/assemble_chapter.py --chapter {args.chapter} "
            f"--style {mode}` ausfuehren."
        )
        if complete:
            print("Alle Szenen fuer dieses Kapitel liegen vor.")
        else:
            print("Szenenlauf fertig; Kapitel ist noch nicht vollstaendig.")

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
    elif mode_cfg.get("profile_path"):
        rules_applied.append(
            f"Style-Profil aus {mode_cfg['profile_path']} verwendet"
        )
    rules_applied.extend([
        f"Stil: {mode}",
        f"Modell-ID: {chosen_model}",
        f"Temperatur: {temperature}, max_tokens: {max_tokens}",
        f"Granularitaet: {granularity}",
    ])
    if client is not None and args.provider == "openrouter":
        rules_applied.append(client.usage_summary())
    difficult = []
    if rules_text is not None:
        difficult.append(
            f"Regelwerk ist {len(rules_text)} Zeichen lang "
            f"(Prompt wird entsprechend gross)."
        )
    if mode_cfg.get("profile_text"):
        difficult.append(
            f"Style-Profil ist {len(mode_cfg['profile_text'])} Zeichen lang "
            f"({mode_cfg.get('profile_path', mode)})."
        )
    if granularity == "chapter":
        difficult.append(
            "chapter-Granularitaet: ein Call fuer das ganze Kapitel. "
            "Context-Limit beachten."
        )
    if failed_scenes:
        for sf in scene_files:
            if sf["error"]:
                difficult.append(
                    f"Szene {sf['number']} FEHLER: {sf['error']}"
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
            f"Provider: {args.provider}. Modell: {chosen_model}. "
            f"{output_note} "
            f"Szenen: {len(scenes)} erkannt, "
            f"{failed_scenes} fehlgeschlagen."
        ),
    )
    if client is not None and args.provider == "openrouter":
        if args.scene:
            scope = f"Kapitel {args.chapter}, Szene {int(args.scene):02d}"
        elif granularity == "scene":
            scope = f"Kapitel {args.chapter}, Szenenlauf"
        else:
            scope = f"Kapitel {args.chapter}, Kapitelmodus"
        append_to_log(
            log_dir,
            args.chapter,
            "Token-Historie",
            f"{datetime.now().isoformat(timespec='seconds')} - "
            f"{scope} - {chosen_model} - {client.usage_summary()}",
        )
    print(f"Logfile: {log_path}")

    # Status: needs_review / done (optional)
    if status_path is not None and state is not None:
        can_finish = (
            args.provider == "openrouter"
            and (
                granularity == "chapter"
                or chapter_translations_complete(output_root, args.chapter, mode)
            )
        )
        if can_finish:
            new_status = STATUS_DONE if args.no_review else STATUS_NEEDS_REVIEW
            mark_done(
                state, args.chapter,
                words_target=words_target,
                title_de=title_de or title_ru,
                needs_review=not args.no_review,
            )
            save_state(state, status_path)
            print(f"-> {args.chapter} = {new_status}")
        else:
            save_state(state, status_path)
            print(f"-> {args.chapter} bleibt in_progress")

    print()
    print("Fertig.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
