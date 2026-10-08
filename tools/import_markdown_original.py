"""import_markdown_original.py - Uebernahme-Werkzeug fuer RomanForge-Manuskripte (Stufe 1).

Allgemeiner Nachfolger von import_die_dritte_chronik.py fuer deutsche
Originale (DE -> DE, chapter_as_scene). Vergleicht einen RomanForge-
Markdown-Export mit dem letzten Uebernahmestand (state.yaml, K1) und dem
aktuellen peter-Text, berichtet nach Abgleichtabelle und uebernimmt nur
ausdruecklich freigegebene Kapitel (--accept) bzw. markiert peter-Staende
als fuehrend (--keep). Schreibt sonst nichts (--dry-run/--compare nur stdout).

Kapitel, die im Export neu sind ('neu'), haben in peter noch keine ID; sie
werden ueber ihre Exportposition freigegeben (--accept 019 = 19. Kapitel des
Exports) und dabei als neue Kapitelquelle angelegt. --keep ist fuer sie nicht
moeglich. Pro Lauf hoechstens MAX_ACCEPT_PER_RUN Kapitel (--accept/--keep
zusammen).

Kein OpenRouter-, kein Higgsfield-, kein anderer kostenpflichtiger Aufruf.
Kein Eingabeprompt (K4). source/ wird nie beschrieben (ausser --new-Erstkopie).
"""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))

from lib.output_paths import de_scene_path, source_chapter_path  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parent.parent

CHAPTER_SPLIT_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
NUMBERED_PREFIX_RE = re.compile(r"^\d+\.\s+")
KAPITEL_PREFIX_RE = re.compile(r"^Kapitel\s+\d+\s*[–—:\-]\s*(.+)$", re.IGNORECASE)
WORD_RE = re.compile(r"\w+", re.UNICODE)

ACTION_NOTHING = "nichts"
ACTION_PROPOSE = "uebernahme-vorgeschlagen"
ACTION_KEEP_PETER = "peter-behalten"
ACTION_CONFLICT = "konflikt"
ACTION_NO_BASELINE = "ohne-ausgangsstand"
ACTION_NEW = "neu"
# Paketgrenze fuer --accept/--keep (docs/uebernahme-romanforge.md): hoechstens
# fuenf Kapitel pro Lauf, damit Assembly und Gate pro Kapitel nachvollziehbar
# bleiben. Gilt fuer uebernommene und behaltene Kapitel zusammen.
MAX_ACCEPT_PER_RUN = 5


def literary_title(raw: str) -> str:
    """Gleiche Titelaufbereitung wie import_die_dritte_chronik.py (K3)."""
    title = raw.strip()
    title = NUMBERED_PREFIX_RE.sub("", title).strip()
    match = KAPITEL_PREFIX_RE.match(title)
    if match:
        return match.group(1).strip()
    return title


def normalize_body(title: str, body: str) -> str:
    """Gleiche Koerperaufbereitung wie import_die_dritte_chronik.py (K3)."""
    lines = body.replace("\r\n", "\n").split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if lines:
        first = lines[0].strip().strip("*").strip()
        if first == title or first.casefold() == title.casefold():
            lines.pop(0)
            while lines and not lines[0].strip():
                lines.pop(0)
        elif first.startswith("# ") and literary_title(first[2:]).casefold() == title.casefold():
            lines.pop(0)
            while lines and not lines[0].strip():
                lines.pop(0)
    while lines and lines[0].strip() in {"---", "***", "* * *"}:
        lines.pop(0)
        while lines and not lines[0].strip():
            lines.pop(0)
    text = "\n".join(lines).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def split_chapters(source_text: str) -> list[tuple[str, str]]:
    """Zerlegt RomanForge-Markdown in (Titel, Koerper)."""
    matches = list(CHAPTER_SPLIT_RE.finditer(source_text))
    if not matches:
        raise SystemExit("Keine ##-Kapitelueberschriften in der Quelle gefunden.")
    chapters: list[tuple[str, str]] = []
    for idx, match in enumerate(matches):
        raw_heading = match.group(1).strip()
        title = literary_title(raw_heading)
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(source_text)
        body = normalize_body(title, source_text[start:end])
        if not body:
            raise SystemExit(f"Leerer Kapitelkoerper nach Heading: {raw_heading}")
        chapters.append((title, body))
    return chapters


def canonical_text(text: str) -> str:
    """Vergleichs-Normalisierung nach normalize_body (K3): LF, RTRIM, Blanks.

    Entfernt genau ein '---' ganz am Ende (Regex), identisch auf beiden
    Seiten; innere '---' (Szenentrenner) bleiben unangetastet.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n\s*-{3,}\s*\Z", "", text)
    lines = [line.rstrip() for line in text.split("\n")]
    out: list[str] = []
    blanks = 0
    for line in lines:
        if line.strip():
            blanks = 0
            out.append(line)
        else:
            blanks += 1
            if blanks <= 1:
                out.append("")
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out)


def text_hash(canonical: str) -> str:
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def _strip_scene_head(lines: list[str], idx: int) -> int:
    """Ueberspringt Szenenkopf in beiden Formaten (025/031/033/036 vs. Rest).

    Format A: '## Titel'. Format B: '# Titel', '*Buch[:]* …',
    '*Kapitel-ID:* …', '---'. Dateien werden nicht umgeschrieben,
    der Kopf faellt nur vor dem Hash weg.
    """
    if idx < len(lines) and lines[idx].strip().startswith("##"):
        return idx + 1
    if idx < len(lines) and re.match(r"^#\s+[^#]", lines[idx].strip()):
        idx += 1
        while idx < len(lines):
            stripped = lines[idx].strip()
            if not stripped:
                idx += 1
                continue
            if re.match(r"^\*Buch", stripped) or re.match(r"^\*Kapitel-ID", stripped):
                idx += 1
                continue
            if stripped in {"---", "***", "* * *"}:
                idx += 1
                while idx < len(lines) and not lines[idx].strip():
                    idx += 1
                if idx < len(lines) and lines[idx].strip().startswith("##"):
                    return idx + 1
                return idx
            if stripped.startswith("##"):
                return idx + 1
            return idx
    return idx


def scene_body(scene_text: str) -> str:
    """Koerper aus Szene ohne Titel-/Kapitelkopf.

    Format B ('# Titel'-Kopf) nur am Dateianfang, nur das ERSTE '---'
    direkt nach den Kopfzeilen. Format A ('## Titel') sucht nie nach
    '---'; innere Szenentrenner bleiben erhalten. Kein Text-Schneiden
    am Ende (das erledigt canonical_text per Regex).
    """
    text = scene_text.replace("\r\n", "\n")
    lines = text.split("\n")
    idx = 0
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    idx = _strip_scene_head(lines, idx)
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    return "\n".join(lines[idx:])


def scene_title(scene_text: str) -> str:
    for line in scene_text.replace("\r\n", "\n").split("\n"):
        stripped = line.strip()
        if stripped.startswith("##"):
            return literary_title(stripped.lstrip("#").strip())
        match = re.match(r"^#\s+([^#].*)$", stripped)
        if match:
            return literary_title(match.group(1).strip())
    return ""


def render_scene(title: str, body: str) -> str:
    return "\n".join([f"## {title}", "", body.rstrip() + "\n", ""])


def render_chapter_source(chapter_id: str, title: str, body: str, book_title: str) -> str:
    return "\n".join(
        [
            f"# {title}",
            "",
            f"*Buch: {book_title}*",
            f"*Kapitel-ID: {chapter_id}*",
            "",
            "---",
            "",
            body.rstrip() + "\n",
            "",
        ]
    )


def classify_chapter(rf_changed: bool, peter_changed: bool) -> str:
    if rf_changed and peter_changed:
        return ACTION_CONFLICT
    if rf_changed:
        return ACTION_PROPOSE
    if peter_changed:
        return ACTION_KEEP_PETER
    return ACTION_NOTHING


def _norm_title_key(title: str) -> str:
    return literary_title(title).casefold()


def match_chapters(
    export: list[tuple[str, str]], known_titles: dict[str, str]
) -> list[dict[str, str | None]]:
    """Ordnet Export-Kapitel per Titel zu (Titel vor Position, K-A4).

    Rueckgabe pro Export-Kapitel: chapter_id (oder None bei 'neu'),
    title_export, action ('zugeordnet' oder 'neu'). Entfallene und
    verschobene Kapitel meldet der Aufrufer anhand der bekannten IDs.
    """
    by_title: dict[str, list[str]] = {}
    for chapter_id, title in known_titles.items():
        by_title.setdefault(_norm_title_key(title), []).append(chapter_id)
    used: set[str] = set()
    rows: list[dict[str, str | None]] = []
    for position, (title, _body) in enumerate(export, 1):
        candidates = [c for c in by_title.get(_norm_title_key(title), []) if c not in used]
        if candidates:
            chapter_id = sorted(candidates)[0]
            used.add(chapter_id)
            rows.append({"chapter_id": chapter_id, "title_export": title, "action": "zugeordnet"})
            continue
        rows.append({"chapter_id": None, "title_export": title, "action": ACTION_NEW})
    return rows


def find_presumed_renames(
    export_rows: list[dict[str, str | None]], dropped_ids: list[str]
) -> dict[str, str]:
    """neu+entfallen an gleicher Position -> {entfallene chapter_id: neuer Titel}.

    Reine Heuristik: steht an Exportposition N ein unzugeordnetes Kapitel
    ('neu') und faellt gleichzeitig die bekannte chapter_id 'NNN' weg
    ('entfallen'), dann ist das vermutlich eine Umbenennung. Nur Hinweis,
    kein Auto-Merge (Stufe 1, Schritt 3). Position ist die 1-basierte
    Exportreihenfolge; eine chapter_id entspricht ihrer urspruenglichen
    Exportposition.
    """
    dropped = {cid for cid in dropped_ids if str(cid).isdigit()}
    out: dict[str, str] = {}
    for position, row in enumerate(export_rows, 1):
        chapter_id = f"{position:03d}"
        if row.get("action") == ACTION_NEW and chapter_id in dropped:
            out[chapter_id] = str(row.get("title_export") or "")
    return out


def state_path_for(book_root: Path) -> Path:
    return book_root / "work" / "imports" / "romanforge" / "state.yaml"


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"book": "", "chapters": {}}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    data.setdefault("chapters", {})
    return data


def write_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(state, allow_unicode=True, sort_keys=False), encoding="utf-8")


def update_state_chapter(
    state: dict, chapter_id: str, *, title: str, rf_base: str, peter_base: str, base_export: str
) -> None:
    state.setdefault("chapters", {})[chapter_id] = {
        "title": title,
        "rf_base": rf_base,
        "peter_base": peter_base,
        "base_export": base_export,
    }


def apply_keep(state: dict, chapter_id: str, *, new_rf_base: str, base_export: str) -> None:
    """K2: peter-Text bleibt, rf_base folgt dem Export (Konflikt erledigt)."""
    chapter = state.setdefault("chapters", {}).setdefault(chapter_id, {})
    chapter["rf_base"] = new_rf_base
    chapter["base_export"] = base_export


def accept_warning(chapter_id: str, action: str) -> str:
    if action == ACTION_CONFLICT:
        return (
            f"WARNUNG Kapitel {chapter_id}: Konflikt per --accept uebernommen; "
            "peter-Aenderungen wurden ersetzt (Git hat sie)."
        )
    if action == ACTION_NEW:
        return (
            f"Kapitel {chapter_id} ist neu (in peter unbekannt); wird per "
            "--accept als neue Kapitelquelle angelegt."
        )
    return f"Kapitel {chapter_id} per --accept uebernommen."


def build_row(
    *, chapter_id: str, title_export: str, title_peter: str,
    body_export: str, body_peter: str, rf_base: str, peter_base: str,
) -> dict:
    export_hash = text_hash(canonical_text(body_export))
    peter_hash = text_hash(canonical_text(body_peter))
    rf_changed = export_hash != rf_base
    peter_changed = peter_hash != peter_base
    action = classify_chapter(rf_changed, peter_changed)
    details: list[str] = []
    if _norm_title_key(title_export) != _norm_title_key(title_peter):
        details.append(f"Titel geaendert: '{title_peter}' -> '{title_export}'")
    if action == ACTION_NOTHING:
        details.append("beide unveraendert")
    elif action == ACTION_PROPOSE:
        details.append("nur RomanForge geaendert")
    elif action == ACTION_KEEP_PETER:
        details.append("nur peter geaendert (noch nicht in RomanForge)")
    else:
        details.append("beide geaendert (Konflikt)")
    return {
        "chapter_id": chapter_id,
        "title_export": title_export,
        "title_peter": title_peter,
        "words_export": count_words(body_export),
        "words_peter": count_words(body_peter),
        "rf_changed": rf_changed,
        "peter_changed": peter_changed,
        "action": action,
        "detail": "; ".join(details),
        "export_hash": export_hash,
        "peter_hash": peter_hash,
    }


def render_report(book_title: str, rows: list[dict]) -> str:
    lines = [
        f"# Uebernahmebericht {book_title}",
        "",
        "| Kapitel | Titel | Woerter RomanForge | Woerter peter | Einstufung | Hinweis |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {chapter_id} | {title} | {we} | {wp} | {action} | {detail} |".format(
                chapter_id=row.get("chapter_id", "?"),
                title=row.get("title_export", row.get("title_peter", "")),
                we=row.get("words_export", ""),
                wp=row.get("words_peter", ""),
                action=row.get("action", ""),
                detail=row.get("detail", ""),
            )
        )
    return "\n".join(lines) + "\n"


def parse_id_list(values: list[str] | None) -> list[str]:
    out: list[str] = []
    for value in values or []:
        for part in str(value).split(","):
            part = part.strip()
            if not part:
                continue
            if re.fullmatch(r"\d{1,3}", part):
                part = f"{int(part):03d}"
            out.append(part)
    seen: set[str] = set()
    unique = [p for p in out if not (p in seen or seen.add(p))]  # type: ignore[func-returns-value]
    return unique


def read_scene_text(book_root: Path, style: str, chapter_id: str) -> tuple[str, str, Path]:
    path = book_root / "work" / "scenes" / "de" / style / chapter_id / "scene-01.md"
    if not path.exists():
        return "", "", path
    text = path.read_text(encoding="utf-8")
    return scene_title(text), scene_body(text), path


def chapter_baseline(
    state: dict, chapter_id: str, source_baseline: dict[str, str]
) -> tuple[str, str, str, bool]:
    """Ausgangsstand eines Kapitels: (rf_base, peter_base, title, has_baseline).

    Quelle 1: state.yaml (nach dem Erstlauf fuer ALLE Kapitel gesetzt).
    Quelle 2: --baseline (nur solange noch keine state.yaml existiert).
    Nie eine leere Baseline als Wert: fehlt beides, meldet has_baseline=False
    (Einstufung 'ohne-ausgangsstand', nie 'konflikt').
    """
    entry = state.get("chapters", {}).get(chapter_id) or {}
    title = str(entry.get("title") or "")
    rf_base = str(entry.get("rf_base") or "")
    peter_base = str(entry.get("peter_base") or "")
    if rf_base or peter_base:
        rf_base = rf_base or peter_base
        peter_base = peter_base or rf_base
        return rf_base, peter_base, title, True
    if chapter_id in source_baseline:
        base = str(source_baseline[chapter_id])
        return base, base, title, True
    return "", "", title, False


def seed_state_from_baseline(
    state: dict, source_baseline: dict[str, str], rows: list[dict], stamp: str
) -> int:
    """Erstlauf: state.yaml fuer ALLE Kapitel anlegen (Option B).

    Unberuehrte Kapitel bekommen rf_base = peter_base = Hash aus --baseline;
    bearbeitete Kapitel werden danach von --keep/--accept ueberschrieben.
    Kapitel ohne Ausgangsstand (nicht in --baseline/state) werden NICHT
    geseedet - sie bleiben 'ohne-ausgangsstand'. Rueckgabe: Anzahl Seeds.
    """
    seeded = 0
    for row in rows:
        chapter_id = str(row.get("chapter_id") or "")
        action = str(row.get("action") or "")
        if not chapter_id.isdigit() or action in (ACTION_NEW, "entfallen", ACTION_NO_BASELINE):
            continue
        base = source_baseline.get(chapter_id)
        if not base:
            continue
        title = str(row.get("title_export") or row.get("title_peter") or "")
        update_state_chapter(
            state, chapter_id, title=title, rf_base=base, peter_base=base,
            base_export=stamp,
        )
        seeded += 1
    return seeded


def stamp_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def write_run_artifacts(
    book_root: Path, stamp: str, *, export_text: str, report: str
) -> Path:
    run_dir = book_root / "work" / "imports" / "romanforge" / "runs" / stamp
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "export.md").write_text(export_text, encoding="utf-8")
    (run_dir / "report.md").write_text(report, encoding="utf-8")
    return run_dir


def resolve_book_root(book_id: str | None, book_root_arg: str | None) -> tuple[Path, dict]:
    if book_root_arg:
        book_root = Path(book_root_arg)
        book_yaml = book_root / "book.yaml"
        if not book_yaml.exists():
            raise SystemExit(f"FEHLER: kein book.yaml unter {book_root}")
        cfg = yaml.safe_load(book_yaml.read_text(encoding="utf-8")) or {}
        cfg.setdefault("id", book_root.name)
        return book_root, cfg
    if not book_id:
        raise SystemExit("FEHLER: --book oder --book-root angeben.")
    from lib.book_project import book_project as _book_project  # noqa: E402

    project = _book_project(REPO_ROOT, book_id)
    return project.root, project.as_tool_config(REPO_ROOT)


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="RomanForge-Markdown uebernehmen (Stufe 1).")
    ap.add_argument("--book", default=None, help="Buch-ID unter books/<id>/")
    ap.add_argument("--book-root", default=None, help="Direkter Buchpfad (fuer Tests)")
    ap.add_argument("--source", default=None, help="RomanForge-Exportdatei (.md)")
    ap.add_argument("--baseline", default=None,
                    help="Ursprungs-Export als Ausgangsstand (Pflicht ohne state.yaml)")
    ap.add_argument("--dry-run", action="store_true", help="Nur Kapitelliste, schreibt nichts")
    ap.add_argument("--compare", action="store_true", help="Nur Bericht, schreibt nichts")
    ap.add_argument("--accept", action="append", default=None, help="Kapitel uebernehmen, z.B. 008 oder 008,012")
    ap.add_argument("--keep", action="append", default=None, help="peter-Text behalten, z.B. 008 oder 008,012")
    ap.add_argument("--new", action="store_true", help="Neues DE-Original anlegen")
    ap.add_argument("--id", default=None)
    ap.add_argument("--title", default=None)
    ap.add_argument("--author", default=None)
    ap.add_argument("--subtitle", default=None)
    ap.add_argument("--series", default=None)
    ap.add_argument("--publisher", default=None)
    return ap


def cmd_dry_run(book_title: str, chapters: list[tuple[str, str]]) -> int:
    total = 0
    print(f"=== {book_title} ===")
    print(f"Kapitel: {len(chapters)}")
    print("-" * 60)
    for idx, (title, body) in enumerate(chapters, 1):
        words = count_words(body)
        total += words
        print(f"{idx:03d}  {words:6,}  {title}")
    print("-" * 60)
    print(f"Summe: {total:,} Woerter")
    print("(dry-run: keine Dateien geschrieben)")
    return 0


def cmd_compare(
    *, book_title: str, book_root: Path, style: str,
    chapters: list[tuple[str, str]], state: dict, source_baseline: dict[str, str],
) -> tuple[int, list[dict]]:
    known = {f"{idx:03d}": title for idx, (title, _b) in enumerate(chapters, 1)}
    # Bekannte Titel aus Szenen (fuer Zuordnung); Exporttitel zuerst per Titel matchen.
    scene_titles: dict[str, str] = {}
    for idx in range(1, len(chapters) + 1):
        chapter_id = f"{idx:03d}"
        title_p, _b, path = read_scene_text(book_root, style, chapter_id)
        if path.exists():
            scene_titles[chapter_id] = title_p or known[chapter_id]
    matched = match_chapters(chapters, scene_titles or known)
    matched_ids = {
        str(r["chapter_id"]) for r in matched
        if r["action"] == "zugeordnet" and r["chapter_id"]
    }
    dropped_ids = sorted(set(scene_titles) - matched_ids)
    presumed = find_presumed_renames(matched, dropped_ids)
    rows: list[dict] = []
    for position, row in enumerate(matched, 1):
        if row["action"] != "zugeordnet" or not row["chapter_id"]:
            detail = "neues Kapitel im Export; nur melden, nie automatisch"
            renamed_from = presumed.get(f"{position:03d}")
            if renamed_from is not None:
                old_title = scene_titles.get(renamed_from, "")
                detail += f"; vermutlich umbenannt von {renamed_from} '{old_title}'"
            rows.append({
                "chapter_id": ACTION_NEW, "title_export": row["title_export"],
                "title_peter": "", "words_export": count_words(
                    next(b for t, b in chapters if t == row["title_export"])),
                "words_peter": "", "action": ACTION_NEW,
                "detail": detail,
                # Position = Reihenfolge im Export. Ein neues Kapitel hat noch
                # keine peter-ID und ist deshalb ueber seine Position
                # ansprechbar (--accept 019 = 19. Kapitel des Exports).
                "position": f"{position:03d}",
            })
            continue
        chapter_id = str(row["chapter_id"])
        title_export, body_export = chapters[int(chapter_id) - 1] if chapter_id.isdigit() else ("", "")
        # Bei Positions-Abweichung echten Exporttitel suchen:
        for t, b in chapters:
            if _norm_title_key(t) == _norm_title_key(str(row["title_export"])):
                title_export, body_export = t, b
                break
        title_peter, body_peter, _p = read_scene_text(book_root, style, chapter_id)
        rf_base, peter_base, _t, has_base = chapter_baseline(
            state, chapter_id, source_baseline)
        if not has_base:
            rows.append({
                "chapter_id": chapter_id, "title_export": title_export,
                "title_peter": title_peter or title_export,
                "words_export": count_words(body_export),
                "words_peter": count_words(body_peter),
                "action": ACTION_NO_BASELINE,
                "detail": "kein Ausgangsstand (nicht in state.yaml/--baseline); "
                          "mit --baseline (oder nach Erstlauf) erneut pruefen",
            })
            continue
        built = build_row(
            chapter_id=chapter_id, title_export=title_export,
            title_peter=title_peter or title_export,
            body_export=body_export, body_peter=body_peter,
            rf_base=rf_base, peter_base=peter_base,
        )
        rows.append(built)
    for chapter_id in dropped_ids:
        title_peter, body_peter, _p = read_scene_text(book_root, style, chapter_id)
        detail = "im Export nicht enthalten; Datei bleibt stehen"
        if chapter_id in presumed:
            detail += f"; vermutlich umbenannt zu '{presumed[chapter_id]}'"
        rows.append({
            "chapter_id": chapter_id, "title_export": "", "title_peter": title_peter,
            "words_export": "", "words_peter": count_words(body_peter),
            "action": "entfallen",
            "detail": detail,
        })
    report = render_report(book_title, rows)
    print(report, end="")
    blocked = [
        r for r in rows
        if r["action"] in (ACTION_CONFLICT, ACTION_NO_BASELINE, ACTION_NEW, "entfallen")
    ]
    return (2 if blocked else 0, rows)


def _resolve_under_book(book_root: Path, value: str) -> Path:
    """Pfadangabe aus der Config in einen Pfad unter `book_root` aufloesen.

    Zwei Quellen mit zwei Formaten: `--book` kommt ueber `book_project`
    (`as_tool_config`) und liefert **repo-relative** Werte
    (`work_dir = "books/<id>/work"`, `source_path = "books/<id>/source/…"`),
    `--book-root` liest die rohe `book.yaml` (`work_dir = "work"`). Beides
    muss am selben Buchordner landen, sonst entsteht ein doppelter Pfad
    (`books/<id>/books/<id>/work`) - Regression 2026-10-08 (Ashkar I).
    """
    path = Path(value)
    if path.is_absolute():
        return path
    if len(path.parts) > 1:
        repo_candidate = REPO_ROOT / path
        book_root_abs = book_root if book_root.is_absolute() else REPO_ROOT / book_root
        if repo_candidate == book_root_abs or repo_candidate.is_relative_to(book_root_abs):
            return repo_candidate
    return book_root / path


def _output_root_for(book_root: Path, book_cfg: dict) -> Path:
    work = str(book_cfg.get("work_dir") or book_cfg.get("output_dir") or "work")
    return _resolve_under_book(book_root, work)


def write_accepted_chapter(
    *, book_root: Path, output_root: Path, book_cfg: dict,
    chapter_id: str, title: str, body: str, style: str,
) -> list[Path]:
    book_title = str(book_cfg.get("title") or book_cfg.get("id") or "")
    chapter_path = output_root / "chapters" / f"{chapter_id}-source.md"
    chapter_path.parent.mkdir(parents=True, exist_ok=True)
    chapter_path.write_text(
        render_chapter_source(chapter_id, title, body, book_title), encoding="utf-8")
    scene_text = render_scene(title, body)
    written = [chapter_path]
    src_scene = output_root / "scenes" / "de" / chapter_id / "scene-01.md"
    src_scene.parent.mkdir(parents=True, exist_ok=True)
    src_scene.write_text(scene_text, encoding="utf-8")
    written.append(src_scene)
    de_scene = de_scene_path(output_root, chapter_id, 1, style)
    de_scene.parent.mkdir(parents=True, exist_ok=True)
    de_scene.write_text(scene_text, encoding="utf-8")
    written.append(de_scene)
    _ = book_root
    return written


def slugify(value: str) -> str:
    repl = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "ae", "Ö": "oe", "Ü": "ue"}
    for src, tgt in repl.items():
        value = value.replace(src, tgt)
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value or "buch"


NEW_STYLE_DEFAULT = "stil-01-original"


def export_title_suggestion(export_text: str) -> str | None:
    """Erste '# '-Zeile des Exports als Titelvorschlag (nicht still uebernehmen)."""
    match = re.search(r"^#\s+(.+?)\s*$", export_text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _neutral_book_yaml(args: argparse.Namespace, source_name: str, book_id: str) -> dict:
    """Neutrale book.yaml aus tools/init_book.py (kein Chronik-Klon)."""
    from init_book import build_book_yaml  # noqa: E402

    ns = argparse.Namespace(
        title=args.title, author=args.author, source_lang="de", target_lang="de",
        ruleset_path="", ruleset_apply=False, style=NEW_STYLE_DEFAULT,
        model="deepseek/deepseek-v4-pro", max_tokens_per_scene=10000,
        notes="Deutsches Original aus RomanForge (Stufe 1).",
    )
    cfg = build_book_yaml(ns, source_name, book_id)
    # RomanForge-DE-Originale sind kapitelweise (chapter_as_scene), nicht szenig.
    cfg["structure"] = {
        "mode": "chapter_as_scene", "label": "Kapitel als Szenen", "groups": [],
    }
    return cfg


def _neutral_export_yaml(args: argparse.Namespace) -> dict:
    """Neutrale export.yaml aus tools/init_book.py; buchspezifische Texte leer.

    Kein website:/marketing:-Block. Buchspezifische Texte (rights, translator,
    translator_label, title_page_extra) bleiben leer und werden im Bericht als
    'offen' gelistet; der Chronik-Klon faellt weg.
    """
    from init_book import build_export_yaml  # noqa: E402

    ns = argparse.Namespace(
        title=args.title, author=args.author,
        subtitle=args.subtitle or "", target_lang="de",
    )
    cfg = build_export_yaml(ns)
    book = cfg.setdefault("book", {})
    for key in ("translator", "translator_label", "publisher", "rights",
                "description", "imprint_text"):
        book[key] = ""
    book["title_page_extra"] = []
    if args.publisher:
        book["publisher"] = args.publisher
    if args.series:
        book["series"] = args.series
    return cfg


def cmd_new(args: argparse.Namespace) -> int:
    if not args.source:
        print("FEHLER: --source mit RomanForge-Export angeben.", file=sys.stderr)
        return 2
    source = Path(args.source)
    if not source.exists():
        print(f"FEHLER: Quelle nicht gefunden: {source}", file=sys.stderr)
        return 1
    export_text = source.read_text(encoding="utf-8")

    # --dry-run: nur Kapitelliste + Wortzahlen, schreibt nichts.
    if args.dry_run:
        chapters = split_chapters(export_text)
        report_title = (
            args.title or export_title_suggestion(export_text) or "(ohne Titel)")
        return cmd_dry_run(report_title, chapters)

    # Titel aus der '# '-Zeile nur vorschlagen, nie still uebernehmen.
    if not args.title:
        suggestion = export_title_suggestion(export_text)
        if suggestion:
            print(f"Vorschlag aus '# '-Zeile: --title \"{suggestion}\"")
        print(
            "FEHLER: --new braucht --title (und --author)."
            + (" Titelvorschlag siehe oben." if suggestion else ""),
            file=sys.stderr,
        )
        return 2
    if not args.author:
        print("FEHLER: --new braucht --author.", file=sys.stderr)
        return 2

    book_id = args.id or slugify(args.title)
    if args.book_root:
        book_root = Path(args.book_root)
        exists = (book_root / "book.yaml").exists()
    else:
        book_root = REPO_ROOT / "books" / str(book_id)
        exists = book_root.exists()
    if exists:
        print(f"FEHLER: Buchpaket existiert bereits: {book_root}", file=sys.stderr)
        return 2

    chapters = split_chapters(export_text)
    for sub in ("source", "work/chapters", "work/scenes/de", "styles",
                "status/logs", "assets/covers", "exports"):
        (book_root / sub).mkdir(parents=True, exist_ok=True)
    target_source = book_root / "source" / source.name
    if source.resolve() != target_source.resolve():
        shutil.copy2(source, target_source)
    book_yaml = _neutral_book_yaml(args, source.name, book_id)
    (book_root / "book.yaml").write_text(
        yaml.safe_dump(book_yaml, allow_unicode=True, sort_keys=False), encoding="utf-8")
    (book_root / "export.yaml").write_text(
        yaml.safe_dump(_neutral_export_yaml(args), allow_unicode=True, sort_keys=False),
        encoding="utf-8")
    (book_root / "names.yaml").write_text(
        yaml.safe_dump({"entries": []}, allow_unicode=True), encoding="utf-8")
    style_src = REPO_ROOT / "styles" / f"{NEW_STYLE_DEFAULT}.md"
    if style_src.exists():
        shutil.copy2(style_src, book_root / "styles" / f"{NEW_STYLE_DEFAULT}.md")
    # Alle Kapitel in einem Lauf importieren (drei Textkopien je Kapitel).
    style = NEW_STYLE_DEFAULT
    output_root = _output_root_for(book_root, book_yaml)
    stamp = stamp_now()
    state: dict = {"book": book_id, "chapters": {}}
    rows: list[dict] = []
    for idx, (title, body) in enumerate(chapters, 1):
        chapter_id = f"{idx:03d}"
        write_accepted_chapter(
            book_root=book_root, output_root=output_root, book_cfg=book_yaml,
            chapter_id=chapter_id, title=title, body=body, style=style,
        )
        chapter_hash = text_hash(canonical_text(body))
        update_state_chapter(
            state, chapter_id, title=title,
            rf_base=chapter_hash, peter_base=chapter_hash, base_export=stamp,
        )
        rows.append(build_row(
            chapter_id=chapter_id, title_export=title, title_peter=title,
            body_export=body, body_peter=body,
            rf_base=chapter_hash, peter_base=chapter_hash,
        ))
    write_state(state_path_for(book_root), state)
    run_dir = write_run_artifacts(
        book_root, stamp, export_text=export_text,
        report=render_report(str(args.title), rows),
    )

    # status/status.json wie im Alt-Import: alle Kapitel done.
    from lib.status_manager import (  # noqa: E402
        STATUS_DONE, ChapterState, add_chapter, new_book_state, now_iso, save_state,
    )

    status_state = new_book_state(book_yaml)
    for idx, (title, body) in enumerate(chapters, 1):
        words = count_words(body)
        add_chapter(status_state, ChapterState(
            id=f"{idx:03d}", title_ru=title, title_de=title,
            status=STATUS_DONE, words_source=words, words_target=words,
            completed_at=now_iso(),
        ))
    status_path = book_root / str(book_yaml.get("status_file") or "status/status.json")
    save_state(status_state, status_path)

    open_items: list[str] = []
    if not args.subtitle:
        open_items.append("Untertitel")
    if not args.series:
        open_items.append("Reihe (title_page_extra)")
    if not args.publisher:
        open_items.append("Verlag")
    open_items += [
        "Rechte (rights)", "Uebersetzer/Etikett (translator)",
        "Originaltitel", "Originalautor",
        "Zusammenfassung (summary)", "Autorenleben (author_bio)",
    ]
    print(f"Buchpaket angelegt: {book_root}")
    print(f"Kapitel importiert: {len(chapters)} (je 3 Textkopien)")
    print(f"state.yaml: {len(chapters)} Eintraege (rf_base = peter_base = Export-Hash)")
    print(f"status.json: {len(chapters)} Kapitel, Status done")
    print(f"lauf: {run_dir}/export.md + report.md")
    print("Offen (nicht erfunden): " + ", ".join(open_items))
    print(
        f"Folge: py -3 tools/assemble_chapter.py --book {book_id} --all --style {style}")
    print(
        "Folge: py -3 tools/review_manuscript.py --book "
        f"{book_id} --style {style} --all --llm none")
    return 0


def baseline_hashes(baseline_path: Path) -> dict[str, str]:
    """K1 korrigiert: Ausgangsstand aus --baseline-Datei (nur lesen)."""
    if not baseline_path.exists():
        raise SystemExit(f"FEHLER: Baseline nicht gefunden: {baseline_path}")
    chapters = split_chapters(baseline_path.read_text(encoding="utf-8"))
    return {
        f"{idx:03d}": text_hash(canonical_text(body))
        for idx, (_t, body) in enumerate(chapters, 1)
    }


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    args = build_parser().parse_args(argv)
    if args.new:
        return cmd_new(args)
    book_root, book_cfg = resolve_book_root(args.book, args.book_root)
    book_title = str(book_cfg.get("title") or book_cfg.get("id") or book_root.name)
    style = str(book_cfg.get("style_mode") or "stil-01-original")
    source_arg = args.source or str(
        _resolve_under_book(book_root, str(book_cfg.get("source_path") or "")))
    source_path = Path(source_arg)
    if not source_path.exists():
        print(f"FEHLER: Quelle nicht gefunden: {source_path}", file=sys.stderr)
        return 1
    export_text = source_path.read_text(encoding="utf-8")
    chapters = split_chapters(export_text)
    if args.dry_run:
        return cmd_dry_run(book_title, chapters)
    output_root = _output_root_for(book_root, book_cfg)
    state_path = state_path_for(book_root)
    state = load_state(state_path)
    state.setdefault("book", str(book_cfg.get("id") or book_root.name))
    has_state = bool(state.get("chapters"))
    baseline_arg = args.baseline
    if not has_state and not baseline_arg:
        print(
            "FEHLER: keine state.yaml gefunden; --baseline <ursprungs-export> angeben. "
            "Kein stilles Zurueckfallen auf source_path.",
            file=sys.stderr,
        )
        return 2
    if has_state and baseline_arg:
        print(
            "Hinweis: state.yaml vorhanden; --baseline wird ignoriert "
            "(Ausgangsstand kommt aus state.yaml).",
            file=sys.stderr,
        )
    source_baseline = {} if has_state else (
        baseline_hashes(Path(baseline_arg)) if baseline_arg else {}
    )
    if args.compare or (not args.accept and not args.keep):
        code, _rows = cmd_compare(
            book_title=book_title, book_root=book_root, style=style,
            chapters=chapters, state=state, source_baseline=source_baseline,
        )
        return code
    accept = parse_id_list(args.accept)
    keep = parse_id_list(args.keep)
    if len(accept) + len(keep) > MAX_ACCEPT_PER_RUN:
        print(
            f"FEHLER: {len(accept) + len(keep)} Kapitel in einem Paket; hoechstens "
            f"{MAX_ACCEPT_PER_RUN} pro Lauf (--accept/--keep). Paket kleiner "
            "schneiden; es wurde nichts geschrieben.",
            file=sys.stderr,
        )
        return 2
    code, rows = cmd_compare(
        book_title=book_title, book_root=book_root, style=style,
        chapters=chapters, state=state, source_baseline=source_baseline,
    )
    by_id = {r["chapter_id"]: r for r in rows if r["chapter_id"] != ACTION_NEW}
    # Neue Exportkapitel ('neu') haben keine peter-ID. Sie sind ueber ihre
    # Exportposition ansprechbar (--accept 019 = 19. Kapitel des Exports) und
    # werden in peter neu angelegt; --keep ist fuer sie nicht moeglich.
    # Kollidiert eine Position mit einer vorhandenen Kapitel-ID, gewinnt die
    # vorhandene ID (nur Hinweis, keine stille Zuordnung).
    for row in rows:
        if row.get("chapter_id") != ACTION_NEW:
            continue
        position = str(row.get("position") or "")
        if not position:
            continue
        if position in by_id:
            print(
                f"Hinweis: Exportposition {position} ist mehrdeutig (Kapitel "
                f"{position} existiert bereits); das neue Kapitel ist nicht "
                "ueber die Positionsnummer ansprechbar.",
                file=sys.stderr,
            )
            continue
        by_id[position] = row
    stamp = stamp_now()
    changed = False
    if not has_state and source_baseline:
        seeded = seed_state_from_baseline(state, source_baseline, rows, stamp)
        if seeded:
            changed = True
            print(f"state.yaml neu: {seeded} Kapitel mit Ausgangsstand aus --baseline.")
    for chapter_id in keep:
        row = by_id.get(chapter_id)
        if row is None:
            print(f"FEHLER: --keep {chapter_id} unbekannt.", file=sys.stderr)
            return 2
        if row["action"] == ACTION_NEW:
            print(
                f"FEHLER: --keep {chapter_id}: Kapitel ist in peter unbekannt "
                "(neu); --keep nicht moeglich.",
                file=sys.stderr,
            )
            return 2
        if "export_hash" not in row:
            print(
                f"FEHLER: --keep {chapter_id}: kein Ausgangsstand; "
                "mit --baseline erneut laufen.",
                file=sys.stderr,
            )
            return 2
        apply_keep(state, chapter_id, new_rf_base=str(row["export_hash"]), base_export=stamp)
        changed = True
        print(f"--keep {chapter_id}: peter-Text bleibt; als 'noch nicht in RomanForge' markiert.")
    export_by_title = {t: b for t, b in chapters}
    for chapter_id in accept:
        row = by_id.get(chapter_id)
        if row is None:
            print(f"FEHLER: --accept {chapter_id} unbekannt.", file=sys.stderr)
            return 2
        print(accept_warning(chapter_id, str(row["action"])))
        title = str(row["title_export"] or row["title_peter"])
        body = export_by_title.get(str(row["title_export"]), "")
        if not body:
            for t, b in chapters:
                if _norm_title_key(t) == _norm_title_key(title):
                    body = b
                    break
        write_accepted_chapter(
            book_root=book_root, output_root=output_root, book_cfg=book_cfg,
            chapter_id=chapter_id, title=title, body=body, style=style,
        )
        new_hash = text_hash(canonical_text(body))
        update_state_chapter(
            state, chapter_id, title=title,
            rf_base=new_hash, peter_base=new_hash, base_export=stamp,
        )
        changed = True
    if not changed:
        return code
    write_state(state_path, state)
    run_dir = write_run_artifacts(
        book_root, stamp, export_text=export_text,
        report=render_report(book_title, rows),
    )
    print(f"state: {state_path}")
    print(f"lauf: {run_dir}/export.md + report.md")
    for chapter_id in accept:
        print(f"Folge: py -3 tools/assemble_chapter.py --book {state['book']} --chapter {chapter_id} --style {style}")
        print(
            "Folge: py -3 tools/review_manuscript.py --book "
            f"{state['book']} --style {style} --chapter {chapter_id} --llm none"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())





