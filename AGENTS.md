# AGENTS.md - Kontext fuer KI-Werkzeuge

> Dies ist die zentrale Kontextdatei. `CLAUDE.md` verweist auf diese Datei.
> Lies zuerst diese Datei und die README, dann beginne mit der Arbeit.
> Aktueller Arbeitsstand und naechste Schritte: [docs/HANDOVER.md](./docs/HANDOVER.md).

## Einstieg fuer neue KI-Sitzung (verbindlich, vor allem anderen lesen)

Wenn du in diesem Repo arbeitest – ob als Mensch oder als KI – gilt folgende Reihenfolge. Alles andere ist Eigenbau und vermeidbar.

1. Lies `AGENTS.md` (diese Datei), dann `README.md`, dann `docs/HANDOVER.md`. Stoppe dort, wenn du den Stand verstanden hast.
2. Frage nie den Status ab, den `py -3 tools/status.py --book <buch-id> summary` schon liefert.
3. Baue keine eigenen Pruef-Skripte oder Datei-Listen. Nutze die vorhandenen CLIs unter `tools/` (siehe Schnellstart in `README.md`).
4. Arbeite immer buchbezogen unter `books/<buch-id>/`. Nie eigenmaechtig in `source/` eingreifen.
5. Unter Windows ist `py -3` der Python-Befehl, nicht `python`.
6. EPUB-/ZIP-/Artifact-Probleme werden separat nach Absprache gelöst – sie sind kein Grund, den Einstieg zu verlassen.
7. Im Zweifel: erst fragen, dann schreiben. Keine Spekulation, keine Massendatei-Lesung, kein `tmp_*.py` im Repo-Root.

## Fortsetzung im gleichen Ordner / neues Chat-Fenster (gleiche LLM)

Kein neues Setup noetig. Im selben Repo-Ordner
(`E:\code\peter-the-one-creator`, Branch `cline/pveejb87`) weiterarbeiten,
neues Fenster reicht. `main` bleibt unberuehrt. Kopiertext:
[docs/uebergabe-prompt.md](./docs/uebergabe-prompt.md).

Einstieg in dieser Reihenfolge (alles lesend, keine Kosten):

1. `AGENTS.md` (diese Datei) + `README.md` (Schnellstart) lesen.
2. `docs/HANDOVER.md` (Titel = Stand-Datum; oben **Letzte Session** =
   RomanForge-Uebernahme Stufe 1, 2026-10-07) +
   `docs/uebernahme-romanforge.md` + `docs/offene-punkte.md` Punkt 6
   (Chronik-Tabelle).
3. Lage verifizieren: `git --no-pager status --short --branch`.
   Print-Vergleich: `books/pharao/exports/stil-02-poetisch/book/print/print-comparison-20260921-pharao-abcd.md`
   (A 924 / B 788 / C 673 / D 643; Cream 776). Gate Pharao erwartet ERROR=0
   (`py -3 tools/review_manuscript.py --book pharao --style stil-02-poetisch --all --llm none --fail-on-errors`).
   Chronik KDP-fertig: Gate ERROR=0/WARNING=13/INFO=36,
   EPUB `...-20260921-131112.epub`.
   Unter Windows CLI mit `py -3`, nicht `python`.
4. Review-Details Chronik: `books/die-dritte-chronik/work/reviews/stil-01-original/chapters/NNN-review.md`.
   Redaktions-Ablauf Chronik (RomanForge-Uebergabe, Stufe 1):
   Exportdatei nennen -> `import_markdown_original.py --compare`
   (mit `--baseline`, nur Bericht) -> `--accept` nur fuer freigegebene
   Kapitel (max. 5 pro Paket, im Werkzeug erzwungen; auch `neu`-Kapitel per
   Exportposition, z. B. `--accept 019`; `status/<Titel> - NN ….md` ist ersetzt) ->
   pro Kapitel `assemble_chapter.py` + `review_manuscript --chapter NNN --llm none`
   -> Kurzbericht (nur ERROR/WARNING/INFO), naechstes Paket.
   Kein OpenRouter fuer Redaktion. `status/status.json` und `status/logs/`
   bleiben unveraendert. Details: `docs/uebernahme-romanforge.md`.
   Offene Redaktionskandidaten und ihre Einstufung (C/c/b) stehen in
   `docs/offene-punkte.md` Punkt 6.

## Was Dieses Projekt Ist

Regelbasierte kapitel- und szenenweise Uebersetzung literarischer Werke
(`ru -> de`). Das Repo ist jetzt buchzentriert: jedes produktive Buch ist ein
eigenes Paket unter `books/<book-id>/`. Tools und Dashboard entdecken Buecher
ueber `books/*/book.yaml`; `config/books.yaml` ist nur noch Legacy unter
`config/legacy/`.

**Memory Bank:** Dieses Projekt pflegt **bewusst keine Cline Memory Bank**
(`projectbrief.md`, `activeContext.md` usw.), weil es parallel in mehreren
KIs bearbeitet wird und eine lokale Memory Bank dadurch schnell veraltet
bzw. widerspruechlich waere. Massgeblicher Kontext sind AGENTS.md, README.md,
`docs/HANDOVER.md` sowie die buchlokalen `book.yaml`- und `export.yaml`-Dateien.

Aktuelle Buchpakete (13):

- `books/peter-i-buch-01/` - Alexei Tolstoi, Peter der Erste
- `books/anna-karenina/` - Lew Tolstoi, Anna Karenina (PARKIERT 09/2026)
- `books/pharao/` - Bolesław Prus, Der Pharao (LIVE; Print-Optionen 2026-09-21: Trim/Profil/Bilder, A–D 924/788/673/643, Cream 776, Gate ERROR=0, Einleitung 000 restauriert)
- `books/feuriger-engel/` - Walerij Brjussow, Der feurige Engel
- `books/aelita/` - Alexei Tolstoi, Aelita (LIVE 09/2026: Regelcheck 0/0, Kapitel-030-Kommentare als Anhang ausgelagert, Buch-EPUB 2026-09-17 nutzergeprueft und veroeffentlicht; 12 Kapitel bewusst ohne Bild; Amazon-Link + Marketing nach Amazon-Freigabe)
- `books/leben-arsenjews/` - Iwan Bunin, Das Leben Arsenjews (Release-Kandidat 09/2026: Gate ERROR=0/WARNING=8, EPUB 20260917-212334 ohne Bypass)
- `books/geheime-geschichte-mongolen/` - Anonym, Die Geheime Geschichte der Mongolen
- `books/die-dritte-chronik/` - Motivatier, Die dritte Chronik (DE-Original; Redaktion 2026-09-19 fertig, KDP-fertig 2026-09-21: 29/48 clean, Gate 0/13/36, Bilder 48/48, EPUB `...-20260921-131112.epub`; offen Kindle-Preview + KDP-Upload)
- `books/ashkara/` - Timo Verita, Ashkar I (Das Glasmeer) (DE-Original; RomanForge-Uebernahme 2026-10-07/08: 36/36 Kapitel, Buch-Gate 0/0/18, Abschlussvergleich 36x `nichts`, Kapitelbilder 001-025; offen Bilder 026-036, `status.json`, Buch-EPUB)
- `books/kuprin-duell/` - Alexander Kuprin, Das Duell (Roh-Anlage 09/2026)
- `books/kuprin-moloch/` - Alexander Kuprin, Der Moloch (Roh-Anlage 09/2026)
- `books/grin-wellenlaeuferin/` - Alexander Grin, Die Wellenlaeuferin (Roh-Anlage 09/2026)
- `books/pissemski-tausend-seelen/` - Alexei Pissemski, Tausend Seelen (Roh-Anlage 09/2026)

## Buchpaket-Struktur

```text
books/<book-id>/
  book.yaml                 # fuehrende Buchconfig, Style, AI-Defaults
  export.yaml               # DOCX-/EPUB-/PDF-Metadaten, Cover, Titelei
  names.yaml                # buchlokale Namen-/Begriffsliste fuer Prompts
  source/                   # Originalquellen; nicht ohne Rueckfrage aendern
  assets/covers/            # Cover
  assets/chapter/           # optionale Kapitelbilder chapter-NNN.*
  assets/scene/NNN/         # optionale Szenenbilder scene-NNN.*
  styles/                   # editierbare Style-Profile fuer dieses Buch
  work/
    chapters/               # NNN-source.md
    scenes/<source_lang>/NNN/ # Quell-Szenen, z. B. ru oder en
    scenes/de/<style>/NNN/  # DE-Szenen je Style
    assembled/<style>/      # zusammengesetzte Kapitelversionen
    prompts/                # prompt_file/workspace_ai-Ausgaben
    marketing/              # Marketingtexte (generated.json, overrides/, generation-request.md)
    style-tests/            # Vergleichs- und Referenzdateien
    legacy/                 # alte Dateien/Konflikte fuer dieses Buch
  exports/<style>/<scope>/  # DOCX-/EPUB-/PDF-Ausgaben
  exports/<style>/<scope>/print/  # KDP-Taschenbuch (interior/complete/wrap)
  exports/marketing/        # Marketingpaket (campaign.json, posts.md, youtube.md, media.json, README.md)
  status/status.json
  status/logs/NNN.log.md
```

Globale Ordner:

- `tools/` - Python-CLIs, Dashboard, Bibliotheken
- `webapp/` - FastAPI-Backend + React-Dashboard (nicht mit `webpage/` verwechseln)
- `webpage/` - oeffentliche Motivatier-Regal-Website (Vite + Three.js)
- `tests/` - Smoke-/Unit-Tests
- `docs/` - Dashboard-Design, Higgsfield, Handover
- `config/models.yaml` - OpenRouter-Modellkatalog
- `config/pipeline.yaml` - globale Pipeline-Defaults
- `config/marketing.yaml` - Marketingexport: Marke, Shelf-URL, Zeitplan, Plattformlimits
- `config/style_modes.yaml` - Legacy-Style-Modi
- `styles/` - globale Style-Vorlagen fuer neue Buchpakete
- `logic/` - Original-Regelmaterial; nicht ohne Rueckfrage aendern
- `config/legacy/` - alte zentrale Configs und Migrationsreste

## Voraussetzungen

- **Python-Abhaengigkeiten:** `pip install -r requirements.txt`
- **Dashboard:** Das primaere Dashboard ist FastAPI + React. Start mit
  `python tools/start_dashboard.py` (oder `Dev-Start.cmd` / `dev.cmd`); der
  Befehl baut das React-Frontend bei Bedarf und startet FastAPI auf
  `http://127.0.0.1:8000`. Unter Windows nutzt der Build `npm.cmd`.
- **Regal-Website:** `webpage/` – Katalog via
  `python tools/build_shelf_website.py`; Preview
  `python tools/preview_webpage.py` (nicht `file://`); Details
  `webpage/README.md` und Dashboard-Route `/website`.
- **Streamlit** (>= 1.36): Bleibt als Legacy-Werkbank in `tools/dashboard.py`
  als Backup erhalten, ist aber nicht mehr der Standardstart.
- **Pandoc** (>= 3.0): Wird fuer den EPUB-Export benoetigt.
  Installation: `winget install --id JohnMacFarlane.Pandoc`
  Nach Installation muss ein neues Terminal gestartet werden.
- **Playwright Chromium:** Wird fuer den PDF-Export benoetigt.
  Installation nach `pip install -r requirements.txt`:
  `python -m playwright install chromium`
- **Higgsfield CLI:** Wird fuer Kapitel-/Szenenbilder benoetigt.
  Installation: `npm install -g @higgsfield/cli`; Auth mit
  `higgsfield auth login`. Details und Moodboard-Discovery stehen in
  `docs/higgsfield-integration.md`.
- **`.env`-Datei:** Kopiere `.env.example` nach `.env` und trage
  den `OPENROUTER_API_KEY` ein (OpenRouter-Account noetig).

## Quellformate und EPUB-Verarbeitung

`extract_chapters.py` akzeptiert RTF, XHTML/HTML und Plaintext. EPUB ist ein
ZIP-Container und muss vor der Pipeline ausgepackt werden.

**Workflow fuer neue EPUB-Quellen:**

1. EPUB entpacken (z. B. `Expand-Archive` unter Windows, `unzip` auf Linux/macOS)
2. Das Haupt-XHTML (meist `OEBPS/*.xhtml`) nach `source/` kopieren
3. `book.yaml` → `source_path` auf die `.xhtml`-Datei setzen
4. `extract_chapters.py` ausfuehren – der Parser erkennt `<!doctype html>`
   und parst `<h3>`-Headings als Kapitel (nur Headings mit `Глава N`
   werden als Kapitelgrenzen gewertet, Unterueberschriften wie `1`, `I`, `II`
   werden in das Kapitel eingeschlossen)

Pandoc (`pandoc --from epub --to plain`) ist ein Fallback, verliert aber
die Heading-Struktur (`<h3>` → Fliess-Text).

## Harte Regeln

- Originalquellen unter `books/<book-id>/source/` niemals eigenmaechtig
  loeschen, ersetzen, umbenennen oder bereinigen.
- `logic/` bleibt Originalmaterial und wird nicht ohne ausdrueckliche
  Rueckfrage bearbeitet.
- Produktive Style-Aenderungen gehoeren in
  `books/<book-id>/styles/*.md`. Globale `styles/` sind nur Vorlagen.
- `tools/translate_chapter.py` und `tools/translate_batch.py` laden Profile
  **strikt** aus `books/<id>/styles/`. Es gibt **keinen** Fallback auf
  globale `styles/`. Wenn ein Buchpaket ohne lokale Profile existiert
  (z. B. nach Migration oder partiellem Anlegen), muessen die gewuenschten
  Stile einmalig aus `styles/` nach `books/<id>/styles/` kopiert werden,
  sonst wirft `translate_chapter.py` `StylePromptError: Unbekannter Stil`.
  Das Workbench-/Dashboard-Modul `tools/lib/workbench_state.py` hat
  hingegen einen Fallback; CLI-Aufrufe folgen dieser Logik **nicht**.
- Namen und feste Begriffe werden pro Buch in `books/<book-id>/names.yaml`
  gepflegt und automatisch in Prompts injiziert.
- Status und Logs laufen ueber die CLIs; nicht manuell JSON zurechtbiegen,
  wenn es einen Befehl dafuer gibt.
- Keine Secrets ins Repo; `.env` bleibt lokal.
- Keine automatischen Loeschungen oder destruktiven Operationen ohne klare
  Freigabe.

## Pipeline

```bash
# Buchpaket anlegen
python tools/init_book.py --source "books/Meine Quelle.rtf"

# Kapitelquellen erzeugen
python tools/extract_chapters.py --book anna-karenina

# Quell-Szenen erzeugen
python tools/extract_scenes.py --book anna-karenina --chapter 001
python tools/extract_scenes.py --book anna-karenina --all

# Uebersetzen oder Prompt bauen
python tools/translate_chapter.py --book anna-karenina --chapter 001 --style stil-01-original --provider openrouter
python tools/translate_chapter.py --book anna-karenina --chapter 001 --scene 01 --style stil-01-original --provider prompt_file

# Mehrere Kapitel planen oder laufen lassen
python tools/translate_batch.py --book anna-karenina --from 001 --to 005 --style stil-01-original --provider prompt_file --dry-run
python tools/translate_batch.py --book anna-karenina --missing --style stil-01-original --provider openrouter --assemble-after

# Kapitel ohne LLM zusammensetzen
python tools/assemble_chapter.py --book anna-karenina --chapter 001 --style stil-01-original

# DOCX/EPUB/PDF exportieren
python tools/export_manuscript.py --book anna-karenina --scope chapter --chapter 001 --style stil-01-original --format all --allow-partial
python tools/export_manuscript.py --book anna-karenina --scope chapter --chapter 001 --style stil-01-original --format pdf --allow-partial
python tools/export_manuscript.py --book pharao --scope book --style stil-02-poetisch --format paperback
python tools/export_manuscript.py --book pharao --scope book --style stil-02-poetisch --format paperback --trim-size 6x9 --layout-profile classic --illustration-mode full_page
python tools/export_manuscript.py --book pharao --scope book --style stil-02-poetisch --format paperback --trim-size 6x9 --layout-profile long_classic --illustration-mode inline
python tools/export_manuscript.py --book pharao --scope book --style stil-02-poetisch --format paperback-complete

# Marketingpaket erzeugen (nichts veroeffentlichen; ohne --provider keine Kosten)
python tools/export_marketing.py --book anna-karenina --dry-run
python tools/export_marketing.py --book anna-karenina

# Status
python tools/status.py --book anna-karenina summary
python tools/status.py --book anna-karenina list
python tools/status.py --book anna-karenina next

# Dashboard
python tools/start_dashboard.py
```

`translate_batch.py` ist ein Uebersetzungs-Batch, kein Export-Befehl. Er
erzeugt fehlende Quell-Arbeitseinheiten bei Bedarf und ruft danach
`translate_chapter.py` fuer mehrere Kapitel auf. Kapitel-Assembly passiert
nur mit `--assemble-after` oder separat ueber `assemble_chapter.py`;
DOCX/EPUB/PDF entstehen erst ueber `export_manuscript.py`.

## Release-Gate

Kein Export ohne bestandenen deterministischen Regelcheck. Ein Export mit
offenen Review-ERRORs hat 2026-09 bereits einen live veroeffentlichten Band
(Kindle) erreicht; das ist jetzt technisch verhindert.

```text
Translation -> Deterministic QA -> ERROR>0 ? STOP
            -> Length/Completeness -> Ausreisser ? manuell/LLM
            -> Glossar/Name-Validierung -> EPUB -> Kindle Preview -> Release
```

```bash
# Regelcheck ohne KI (kostenlos), Exit 2 bei ERROR>0
python tools/review_manuscript.py --book peter-i-buch-01 --style stil-02-poetisch --all --llm none --fail-on-errors

# Export bricht bei ERROR>0 ab (Exit 2); Bypass nur bewusst
python tools/export_manuscript.py --book peter-i-buch-01 --scope book --style stil-02-poetisch --format epub
python tools/export_manuscript.py --book peter-i-buch-01 --scope book --style stil-02-poetisch --format epub --allow-review-errors
```

- Gate-Code: `tools/export_manuscript.py::preflight_review_gate` laeuft vor
  `collect_export` ueber die Scope-Kapitel. `--allow-review-errors` ist der
  einzige Bypass (CLI-Flag oder Dashboard-Checkbox) und wird im Export-Manifest
  als `review_gate_errors` + `review_gate_bypassed` protokolliert.
- Release-blockierende Kategorien in `tools/lib/review_checks.py`:
  `missing_de_scene`, `cyrillic_in_translation` (inkl. gemischter Tokens wie
  `Pitschuга`), `encoding_garbage`, `mojibake` (`Ã`, `Ð`, `Ñ`, `U+FFFD`),
  `accented_transliteration` (`Golowín` statt Glossarform `Golowin`),
  `length_ratio` bei starker Raffung, `paragraph_drop` bei Raffung im
  Ratio-Blindfleck.
- **Raffung erkennen (nachgeruestet 2026-09-17).** Der feste `length_ratio`-
  Korridor (ERROR `< 0.55` / `> 2.60`, WARNING `< 0.75` / `> 2.10`) ist nur ein
  Extremfall-Melder: bei Peter der Erste hatte er drei geraffte Szenen mit
  Ratio 0.76-0.91 durchgelassen (Buch-Median 1.30). Deshalb zwei zusaetzliche
  Signale:
  - `paragraph_drop` (pro Szene): DE-Absaetze gegen Quell-Absaetze, WARNING
    `< 0.85`, ERROR `< 0.55`, erst ab 20 Quellabsaetzen **und** nur wenn die
    Wortzahl unter `0.95` x der Quelle liegt. Das reine Verschmelzen kurzer
    Dialogabsaetze loest bewusst keinen Befund aus.
  - `length_outlier` (buchweit, nach dem Sammeln aller Kapitel): Median der
    Szenen-Ratios, WARNING `< 0.72` x Median, ERROR `< 0.55` x Median. Greift
    erst ab 10 Szenen - **im Dashboard also Scope "Ganzes Buch" waehlen**,
    sonst laeuft nur `paragraph_drop`.
  - Beide melden WARNING, solange der Fall nicht extrem ist; nur ERROR
    blockiert den Export.
- Ausnahmen nur fuer echte Originalzitate: `books/<id>/work/review-allowlist.yaml`
  mit `original_quotes: [{chapter, scene, text}]`; exakt hinterlegte Zitate
  werden vor dem Zeichen-Check entfernt. Ohne Datei bleibt Kyrillisch in
  DE-Szenen ein ERROR.
- Reparatur ohne neuen LLM-Lauf:
  `python tools/apply_review_suggestions.py --book <id> --style <style> --plan | --stage | --promote`.
  `--promote` prueft Hash + Regelcheck erneut, legt `*.bak-<stamp>` daneben und
  setzt betroffene Kapitel neu zusammen.

## Style-Profile

Jedes Buchpaket hat eigene Profile in `books/<book-id>/styles/*.md`.
Der Dateiname ohne `.md` ist der Style-Slug und zugleich der Output-Ordner.
Der aktive Default steht in `books/<book-id>/book.yaml` unter `style_mode`.

Das Profil wird als Block unter „Verbindliches Style-Profil“ in den
System-Prompt eingebettet (`tools/lib/style_prompts.py`). Es soll **nur**
Stil- und Rekonstruktionsregeln enthalten – kein eigener SYSTEMPROMPT/
USERPROMPT, kein Quelltextplatzhalter, keine zweite Rollenbeschreibung.

Prompt-Hierarchie (Stand 2026-07-22):

1. globale harte Ausgabe-Regeln (nur Uebersetzung, nichts erfinden)
2. Glossar aus `names.yaml` im User-Prompt
3. Style-Profil (Stil/Rekonstruktion)

Bei Konflikten haben Ausgabe-Regeln und Glossar Vorrang vor dem Profil.
Struktur-Extras (Lede, Vorabsatz, Prolog, erfundene Ueberschriften) sind im
Uebersetzungs-Call **nicht** erlaubt, auch wenn ein Profil danach klingt.
Nach Profil-Aenderungen vorhandene Szenenergebnisse bewusst mit
`--overwrite`, Dashboard-Ersetzen oder Loeschen neu erzeugen.

Gesendete OpenRouter-/Ollama-Prompts werden unter
`work/prompts/sent/YYYYMMDD-HHMMSS-…-<provider>.md` archiviert.

## Buchstruktur Und Namen

`books/<book-id>/book.yaml` enthaelt `structure.mode`:

- `scenes`: Kapitel enthalten mehrere echte Szenen, wie bei Peter I.
- `chapter_as_scene`: jedes Kapitel ist die kleinste Arbeitseinheit, wie bei
  Anna Karenina.

Optionale `structure.groups` koennen Teile oder Binnen-Buecher abbilden, ohne
das Dateiformat zu aendern. Status und Logs bleiben pro Kapitel.

`book.yaml.display` steuert die Leseranzeige im Export. Aktueller Standard:
Kapitel als deutsche ausgeschriebene Ordinaltitel (`Erstes Kapitel` usw.).
Anna zeigt keine Szenenmarker; Peter zeigt innerhalb eines Kapitels zentrierte
Szenenzahlen ohne neue Seite.

`books/<book-id>/names.yaml` enthaelt Eintraege mit `source`, `target`,
`aliases`, `type`, `status` und `note`. Status/Alias/Note sind
Redaktionsmeta; in LLM-Prompts landen standardmaessig nur Zeilen
`Quelle -> Ziel` (`compact_name_lines(..., include_meta=False)`).
Anwendungsregeln (z. B. Temuedschin vs. Dschingis Khan) gehoeren ins
Style-Profil oder in knappe kuratierte Regeln, nicht als widerspruechliche
Notes hinter jedem Eintrag. Nicht aufgefuehrte Personen-, Stammes-, Orts-
und Titelnamen werden konservativ transliteriert oder im Zweifel in der
erkennbaren Quellform beibehalten.

## Provider

- `openrouter`: echter API-Call; schreibt DE-Szenen und loggt Token/Modell.
- Reasoning-Modelle: `book.yaml: ai.reasoning_effort` bzw.
  `translate_chapter.py --reasoning-effort`. Fuer `deepseek/deepseek-v4.1-flash`
  ist `none` noetig, sonst landet der komplette `max_tokens`-Vorrat im
  Denkschritt und es kommt kein Text zurueck (HANDOVER, Fallstrick 4).
- `prompt_file`: schreibt vollstaendige Prompt-Dateien in `work/prompts/`.
- `workspace_ai`: schreibt Arbeitsanweisungen fuer eine KI, die das Repo
  direkt im Editor nutzt.

## Export

DOCX/EPUB/PDF liest fertige DE-Szenen aus
`books/<book-id>/work/scenes/de/<style>/` und schreibt nach
`books/<book-id>/exports/<style>/<scope>/`. Cover, Titelseite,
Zusammenfassung, Autorenleben, Impressum und Inhaltslogik stehen in
`books/<book-id>/export.yaml`. Coverpfade sind relativ zum Buchpaket. Wird keine explizite `image_path` in
`export.yaml` angegeben, sucht `prepare_cover()` automatisch nach
`cover.png`, `cover.jpg`, `cover.jpeg` oder `cover.webp` in
`books/<id>/assets/covers/`. Die Erkennung erfolgt case-insensitive; ein
Platzhalter-Cover wird nur generiert, wenn gar kein Bild gefunden wird.

Optionale Exportbilder liegen ebenfalls relativ zum Buchpaket. Kapitelbilder
werden als `assets/chapter/chapter-NNN.*` abgelegt, Szenenbilder als
`assets/scene/NNN/scene-NNN.*`. Unterstuetzt werden `.jpg`, `.jpeg`, `.png`
und `.webp`; fehlende Bilder werden uebersprungen. Bei mehreren Formaten
gleicher Stem gewinnt `.jpg` vor `.png` (siehe
`docs/higgsfield-integration.md`). Gesteuert wird dies ueber
`illustrations` in `export.yaml`.

Higgsfield-Generierungsdefaults liegen pro Buch in `book.yaml` unter
`higgsfield`. `tools/generate_illustration.py` liest dort Modell,
Moodboard-/Custom-Reference-UUID, Qualitaet und Seitenverhaeltnis.
Nachbearbeitung beim Download: `higgsfield.image_processing`. Kompakte
Export-JPGs nachtraeglich (ohne PNG/`*_alt.jpg` zu loeschen):
`tools/optimize_asset_images.py` bzw. Dashboard „Bilder → Exportbilder
optimieren“. Erkannte Moodboards und der Discovery-Workflow sind in
`docs/higgsfield-integration.md` dokumentiert.

Standardfolge fuer Leserexporte: Coverbild, Titelseite, Zusammenfassung,
Leben des Autors, dann Textbeginn mit Teil-/Buchgruppe und Kapiteln.

**Anhänge (editorische Nachspanne):** Ein top-level `appendices:`-Block in
`books/<id>/export.yaml` haengt Buchtexte hinter das letzte Kapitel
(`style`, `title`, `path` buchrelativ, `source_chapter`/`source_scene`).
Gedacht fuer ausgelagerte Uebersetzungen (z. B. Editionskommentare wie bei
Aelita Kapitel 030: Romantext endet in der DE-Szene, Kommentare stehen im
Anhang "Kommentare"). Der Loader (`tools/lib/editorial_appendices.py`)
erlaubt nur Dateien innerhalb des Buchpakets; `review_checks.py` rechnet
Anhangtexte der verknuepften Szene beim Deterministischen Check wieder zu,
damit der Wegzug in den Anhang keine Raffung vortaeuscht. Das Release-Gate
bleibt scharf. EPUB, DOCX und PDF geben den Anhang aus.

Die Regal-Freigabe steht als **top-level** `website:`-Block in
`books/<id>/export.yaml` (`enabled`, `amazon_url`, `sort_order`, optional
`catalog: false` = nicht im Reihenkatalog am Buchende).
`tools/build_shelf_website.py` (`website_config()`) und
`tools/lib/workbench_api.py` (`load_website_settings()`) lesen
ausschliesslich diesen top-level Block. Ein eingeruecktes `website:` unter
`book:` ist toter Code; das Dashboard haengt beim Speichern dann einen
zweiten top-level Block an (`_write_website_settings_preserving_yaml`).

PDF wird explizit mit `--format pdf` erzeugt (A5-Vorschau). Das
KDP-Taschenbuch-Innenleben ist `--format paperback`. Trim (`--trim-size 5.5x8.5|6x9`)
und Satzprofil (`--layout-profile classic|long_classic`) sind getrennt;
Kapitelbilder `--illustration-mode full_page|inline`. Default 5,5×8,5 / classic /
full_page, Cream-Limit 776 (White 828). Ohne Flags bleibt der bisherige Satz.
Ausgabe unter `exports/<style>/<scope>/print/` mit Varianten-Slug im Dateinamen.
`--format paperback-complete` haengt Vorderseite (`assets/covers/cover-print.*`,
sonst ohne Bild), generierte Rueckseite und Wrap-PDF (Ruecken = Seitenzahl ×
0,0635 mm, creme/SW) an. Reihenkatalog (andere `website.enabled`-Titel) steht in EPUB und
Paperback. `--format all` bleibt rueckwaertskompatibel bei DOCX+EPUB.

## Marketingexport

`tools/export_marketing.py` erzeugt aus den vorhandenen Buchdaten ein
Marketingpaket unter `books/<id>/exports/marketing/` (`campaign.json`,
`posts.md`, `youtube.md`, `media.json`, `README.md`, `clips/` fuer X-MP4s). Details:
[docs/marketing-export.md](./docs/marketing-export.md).

- Es wird **nichts veroeffentlicht** und **keine Plattform-API** angesprochen.
- Der Buch-/EPUB-Export bleibt unberuehrt: Fehlende Marketingdaten blockieren
  ihn nicht (Regressionstest in `tests/test_marketing_campaign.py`).
- Buchlokale Angaben stehen als **top-level** `marketing:`-Block in
  `export.yaml` (analog zu `website:`): `campaign_start`, `amazon_url`,
  `youtube.{url,video_id,public}`, `songs[]`, `media{}`, `enabled`.
  Der Amazon-Link kommt primaer aus `website.amazon_url`.
- Globale Defaults und **alle Plattformlimits** stehen in
  `config/marketing.yaml`.
- Texte liegen in `work/marketing/generated.json`; manuelle Fassungen in
  `work/marketing/overrides/<post-id>.md` haben Vorrang. Ohne `--provider`
  entstehen **keine** API-Kosten; neu erzeugt wird nur bei geaenderten
  Quelldaten, geaenderter `prompt_version` oder `--regenerate`.
- Medien werden repo-relativ zugeordnet; Musik-/Videopositionen bleiben ohne
  Songdaten `omitted`/`blocked` mit Grund, statt Ersatztexte zu erfinden.
- Dashboard: Seite **Export** → Karte **Marketingpaket** (+ Sektion **X-Clip**:
  `tools/render_x_clip.py`, Cover + Song → quadratisches MP4 unter
  `exports/marketing/clips/`, braucht System-ffmpeg); API
  `GET /api/books/{id}/marketing`, Actions `marketing_export` / `render_x_clip`.

## Aktueller Stand

Kurzfassung und Checkliste fuer neue Chats: **[docs/HANDOVER.md](./docs/HANDOVER.md)**
(Stand 2026-10-07). Kopiertext neues Fenster:
[docs/uebergabe-prompt.md](./docs/uebergabe-prompt.md).
Branch: `cline/pveejb87` (nicht `main`); Tip `e93f4a2` RomanForge-Uebernahme
Stufe 1. `main` traegt weiter den Print-Workflow 2026-09-21
(Trim/Profil/Bilder), davor `1beb55d` Chronik KDP-fertig EPUB
`...-20260921-131112.epub` plus Tausend Seelen `stil-02-poetisch`; davor
Peter-I-Raffung 2026-09-17.

- Buchpakete sind fuehrend; alte zentrale `config/books.yaml` und
  `config/export.yaml` liegen unter `config/legacy/`.
- OpenRouter, Ollama, Prompt-Datei-Modus, Workspace-KI-Modus, Assembly und
  Export sind produktiv nutzbar.
- Dashboard (FastAPI+React) liest Buchpakete aus `books/*/book.yaml`.
  Buch-Setup: `/books/:bookId/setup`; Website-Verwaltung: `/website`.
- **Motivatier-Regal** (`webpage/`): opt-in via `export.yaml` → `website.enabled`;
  Generator `tools/build_shelf_website.py`; Dashboard-Jobs + Buch-Settings.
  Preview: `tools/preview_webpage.py` / `Dev-Start-Webpage.cmd`.
- **Prompt-Generator:** `style_prompts.py` ohne Lede-/Struktur-Hintertuer;
  Glossar nur `source -> target` (`name_registry`); Style-Dateien = Embed-
  Profile. `stil-04-original-geheim.md` = Interlinear/Edition (Mongolen).
- **Geheime Geschichte der Mongolen** (auf `main`): Quelle `ja`→`de`,
  `structure.mode: scenes`, ~317 Abschnitte `scene-NN.md`, Import
  `tools/import_geheime_geschichte.py`. Kapitel 006 ist dateiseitig fertig
  (20/20 Szenen in `stil-04-original-geheim`, aus einem Modellvergleich und
  deshalb mit Review-Marker). Offen sind 14 Monolith-Kapitel in
  `stil-01-original` (000, 001–005, 007–013 = 284 Szenen) sowie Szene 07 in
  014. Vor jedem Lauf `--style stil-04-original-geheim` explizit mitgeben,
  sonst plant der Default `stil-01-original` Kapitel 006 mit. Feature-Branch-
  Inhalt wurde 2026-07-28 per Fast-Forward nach `main` gemerged.
- **Die dritte Chronik** (auf `main`): DE-Original; Import
  `tools/import_die_dritte_chronik.py`; Cover vorhanden. Redaktion
  2026-09-18: 008+012 clean 0/0 (Nutzer-Neufassungen), 034 nur
  Satzzeichen (Monster 672W in 6 Absaetze, 5W->2W). Redaktion
  2026-09-19 ohne OpenRouter abgeschlossen: komplett-Runde 031
  (Neufassung 3753 W, 0W/1I `sie-dachte`-Anapher = Stilmittel), 033
  (Neufassung 3539 W, clean 0/0), 036 (Neuschreibung 785 W, clean 0/0);
  mini 009/026/035 clean 0/0, 018 0W/4I und 041 0W/1I (Anaphern/TTR =
  Stilmittel). Endstand: Gate ERROR=0/WARNING=13/INFO=36, 29/48 clean.
  Bilder 2026-09-19 komplett: 48/48 Kapitel bebildert (Kapitelbild 001-014,
  Szenenbild 008 + 015-048 = 49 Bilder + Cover), EPUB
  `...-20260921-131112.epub` (50 Bilder, ohne Bypass; aelterer Stempel
  `20260919-222611` ist ueberholt). Rest-Tabelle siehe
  `docs/offene-punkte.md` Punkt 6 + 12. Offen: Kindle-Preview + Leseprobe,
  KDP-Upload durch Nutzer. Redaktionsweg seit 2026-10-07 ueber RomanForge
  (`docs/uebernahme-romanforge.md`, Stufe 1, `e93f4a2`); Ausgangsstand unter
  `books/die-dritte-chronik/work/imports/romanforge/`. Offen: Nutzer liest
  012/025 selbst, naechster Schritt `--new` (Ashkara).
- **Higgsfield / Bilder:** `config/higgsfield_models.yaml`, Dashboard-Dropdown,
  Asset-Optimierung `optimize_asset_images.py`. Web-UI-Moodboards nur manuell.
  Details: `docs/higgsfield-integration.md`.
- **Top-5-Anlage 09/2026** (auf `main`): `books/kuprin-duell/`,
  `books/kuprin-moloch/`, `books/grin-wellenlaeuferin/`,
  `books/pissemski-tausend-seelen/`. Kapitelquellen und Metadaten stehen,
  Modell `deepseek/deepseek-v4.1-flash` mit `ai.reasoning_effort: none`.
  Pilot gelaufen: `kuprin-moloch` Kapitel 001 in `stil-01-original`
  (Review-Marker, EPUB-Kette geprueft); offen sind 110 Kapitel. Der
  `website:`-Block wurde von `book:` auf top-level korrigiert. Auswahlvorlage:
  `docs/Motivatier-Classics-Umsetzungsrangliste-45.md`.
- **Noch offen (Prioritaet):** siehe `docs/offene-punkte.md` (verbindliche
  Checkliste mit Befehlen) und `docs/HANDOVER.md` – Leben Arsenjews:
  Release-Kandidat 09/2026 (Gate ERROR=0/WARNING=8, EPUB 20260917-212334
  ohne Bypass); offen nur noch Kindle Previewer + menschliche Stichprobe
  (029/034/037/040). Aelita ist LIVE (Amazon-Link + Marketing nach
  Amazon-Freigabe). Anna Karenina ist PARKIERT. Peter der Erste:
  deterministische Fixes und alle 6 gerafften Szenen gelaufen
  (011/03, 002/11, 003/05, 009/08, 010/01, 010/02), Buch-EPUB neu mit Gate
  0 Fehler; offen nur noch Kindle Previewer und eine menschliche Stichprobe
  der drei zuletzt neu uebersetzten Szenen; Mongolen: 14 Monolith-Kapitel abschnittsweise in
  `stil-04-original-geheim`; Chronik (2026-09-21): Text + Bilder + KDP-Titelei
  fertig, Gate 0/13/36, EPUB 20260921-131112 - offen Kindle-Preview, KDP-Upload,
  RomanForge-Entscheidung 012/025 (Stufe 1, `e93f4a2`);
  Pharao-Taschenbuch 2026-09-21 umgesetzt (Punkt 11, auf `main`),
  offen Print-Leseprobe + KDP-Creme 776 vs. 924/788 (C/D liegen unter 776);
  Top-5: Pilot `kuprin-moloch` 001 fertig, Pissemski `stil-02-poetisch`
  (Gate 0/0/5, `1beb55d`); Stilurteil und Rest-Kapitel nur nach Freigabe;
  Regal Amazon-URLs / Deploy; optional Mint-GLBs. Uebersetzungslaeufe
  weiterhin nur nach ausdruecklicher Freigabe.
- **Marketingexport** (umgesetzt 2026-09-13, X-Clip 2026-09-14): `tools/export_marketing.py`,
  `tools/lib/marketing_campaign.py`, `tools/lib/marketing_prompts.py`,
  `tools/render_x_clip.py`, `tools/lib/x_clip.py`, `config/marketing.yaml`, Dashboard-Karte **Marketingpaket** (+ **X-Clip**-Sektion) auf der
  Export-Seite, API `GET /api/books/{id}/marketing` + Actions
  `marketing_export` / `render_x_clip`. Pilot gelaufen fuer `peter-i-buch-01` (Texte als
  Repository-KI, Amazon-Link und Songdaten fehlen bewusst und werden als offene
  Status ausgewiesen). Details: [docs/marketing-export.md](./docs/marketing-export.md).

<!-- motivatier-project-hub:start -->
## Motivatier Project Hub - Anbindung

- Hub: https://github.com/LitttleLions/motivatier-project-hub. Einstieg `INDEX.md`; Vertrag `docs/CONTRACT.md`, Version 1. Dieses Projekt: `litttlelions-peter-the-one-creator`.
- Der Hub ist privat. Zugriff prüfen über die vorhandene authentifizierte GitHub-Integration oder `gh`/Git (z. B. `gh auth status`). Ein 404 beim unauthentifizierten Web-/Raw-Zugriff belegt nicht, dass Hub-Dateien fehlen.
- Bestehende Anbindung aktualisieren – keine Neuanmeldung, keine neue Projektkennung.
- Vor neuer API, größerer Funktion oder gemeinsamer Infrastruktur nach Vorhandenem suchen (Hub-Metadaten, REUSE, Quellpfade). Relevante Ergebnisse/Änderungen/Grenzen gebündelt am Abschluss melden.
- Kleine UI-/Textänderungen, lokale Bugfixes und Refactorings ohne übergreifenden Nutzen benötigen keine zusätzliche Hubarbeit.
- Keine erneute Projektanalyse ohne Anlass. `source_commit` und `reviewed_at` bleiben unverändert, solange keine neue inhaltliche Prüfung stattgefunden hat.
- Nach einem relevanten abgeschlossenen Arbeitspaket `docs/project-brief.md`, optional `docs/reuse.md` und `.atlas/manifest.json` aktualisieren: neue/ersetzte wiederverwendbare Lösungen, wesentliche Architektur-/API-Änderungen oder wichtige Grenzen/Fehlversuche. Mehrere Änderungen einmal gebündelt veröffentlichen.
- Standardexport: die gepflegten Dokumente und `.atlas/manifest.json` unverändert nach `projects/litttlelions-peter-the-one-creator/` im Hub kopieren (`PROJECT_BRIEF.md` und `REUSE.md`), dann dort mit dem aktuellen zentralen Werkzeug `py -3 scripts/hub.py seal litttlelions-peter-the-one-creator` und `py -3 scripts/hub.py validate` prüfen. Ein eigener Exporter ist optional. Ein vorhandener Exporter aus dem Portfolio-Cockpit passt nicht: er verlangt einen sauberen Arbeitsbaum. Quellrepo-Freigaben beachten; Hub-Veröffentlichung über denselben offenen Projekt-PR. Transport ist keine neue inhaltliche Prüfung und verändert deren Datum nicht.
- Committe gezielt den eigenen Anweisungs-/Dokumentationszusatz und pushe nur die freigegebene Commitkette. Erhalte fremde Änderungen, auch innerhalb derselben AGENTS-Datei. Zusätzliche vorausliegende Produktcommits nicht ungefragt veröffentlichen.
- Ein reines lokales Regelupdate benötigt keinen neuen Hub-Export-PR. Falls sich die veröffentlichten Projektbeschreibungen oder der Logo-Export tatsächlich ändern, aktualisiere den bestehenden Projekt-PR oder eröffne genau einen Update-PR; Quelle, Export und CONTEXT.md abgleichen.
- Am Ende kurz nennen: lokale Regel aktualisiert, veröffentlichter Stand und eventuell konkrete Blockade. Keine vermeintlich neue Agentenverbindung melden.
- Passende Agentenprofile und Notes nur aufgabengesteuert lesen. Rückfragen über Issues; eine Empfängerkennung beweist keine Erreichbarkeit. WissenOne bleibt das getrennte Unternehmerwissen.
- Ein optionales echtes App-Logo kann beim Hub-Export bytegetreu mit relativem Quellpfad ergänzt werden. Kein Logo generieren oder ersetzen; fehlendes/unklares Logo blockiert die Aufnahme nicht. Ein Logo allein ändert den Code-Prüfstand nicht.
<!-- motivatier-project-hub:end -->
