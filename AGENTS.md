# AGENTS.md - Kontext fuer KI-Werkzeuge

> Dies ist die zentrale Kontextdatei. `CLAUDE.md` verweist auf diese Datei.
> Lies zuerst diese Datei und die README, dann beginne mit der Arbeit.

## Was Dieses Projekt Ist

Regelbasierte kapitel- und szenenweise Uebersetzung literarischer Werke
(`ru -> de`). Das Repo ist jetzt buchzentriert: jedes produktive Buch ist ein
eigenes Paket unter `books/<book-id>/`. Tools und Dashboard entdecken Buecher
ueber `books/*/book.yaml`; `config/books.yaml` ist nur noch Legacy unter
`config/legacy/`.

**Memory Bank:** Dieses Projekt pflegt **bewusst keine Cline Memory Bank**
(`projectbrief.md`, `activeContext.md` usw.), weil es parallel in mehreren
KIs bearbeitet wird und eine lokale Memory Bank dadurch schnell veraltet
bzw. widerspruechlich waere. Massgeblicher Kontext sind AGENTS.md, README.md
sowie die buchlokalen `book.yaml`- und `export.yaml`-Dateien.

Aktuelle Buchpakete:

- `books/peter-i-buch-01/` - Alexei Tolstoi, Peter der Erste
- `books/anna-karenina/` - Lew Tolstoi, Anna Karenina
- `books/pharao/` - Bolesław Prus, Der Pharao
- `books/feuriger-engel/` - Walerij Brjussow, Der feurige Engel
- `books/leben-arsenjews/` - Iwan Bunin, Das Leben Arsenjews
- `books/geheime-geschichte-mongolen/` - Anonym, Die Geheime Geschichte der Mongolen
- `books/aelita/` - Alexei Tolstoi, Aelita (in Vorbereitung)
- `books/die-dritte-chronik/` - Motivatier, Die dritte Chronik (DE-Original)

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
    style-tests/            # Vergleichs- und Referenzdateien
    legacy/                 # alte Dateien/Konflikte fuer dieses Buch
  exports/<style>/<scope>/  # DOCX-/EPUB-/PDF-Ausgaben
  status/status.json
  status/logs/NNN.log.md
```

Globale Ordner:

- `tools/` - Python-CLIs, Dashboard, Bibliotheken
- `tests/` - Smoke-/Unit-Tests
- `docs/` - Dashboard-Design und Projektinfos
- `config/models.yaml` - OpenRouter-Modellkatalog
- `config/pipeline.yaml` - globale Pipeline-Defaults
- `config/style_modes.yaml` - Legacy-Style-Modi
- `styles/` - globale Style-Vorlagen fuer neue Buchpakete
- `logic/` - Original-Regelmaterial; nicht ohne Rueckfrage aendern
- `config/legacy/` - alte zentrale Configs und Migrationsreste

## Voraussetzungen

- **Python-Abhaengigkeiten:** `pip install -r requirements.txt`
- **Dashboard:** Das primaere Dashboard ist FastAPI + React. Start mit
  `python tools/start_dashboard.py`; der Befehl baut das React-Frontend bei
  Bedarf und startet FastAPI auf `http://127.0.0.1:8000`.
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

PDF wird explizit mit `--format pdf` erzeugt. `--format all` bleibt
rueckwaertskompatibel bei DOCX+EPUB.

## Aktueller Stand

- Buchpakete sind fuehrend; alte zentrale `config/books.yaml` und
  `config/export.yaml` liegen unter `config/legacy/`.
- OpenRouter, Prompt-Datei-Modus, Workspace-KI-Modus, Assembly und Export sind
  produktiv nutzbar.
- Dashboard (FastAPI+React) liest Buchpakete aus `books/*/book.yaml`.
  Buch-Setup-Route: `/books/:bookId/setup` (nicht mehr globales `/setup`).
- Anna Karenina ist als zweites Buchpaket angelegt und hat ein Cover unter
  `books/anna-karenina/assets/covers/annakarenina.png`.
- **Prompt-Generator** (Stand 2026-07-22):
  - `tools/lib/style_prompts.py`: Profil-Intro ohne Lede-/Struktur-Hintertuer;
    harte Ausgabe-Regeln haben Vorrang; Glossar-Einleitung sprachneutral.
  - `tools/lib/name_registry.py`: Prompt-Glossar nur `source -> target`
    (Meta optional via `include_meta=True`).
  - Style-Dateien muessen Embed-Profile sein, keine vollstaendigen
    Standalone-Prompts.
  - `books/geheime-geschichte-mongolen/styles/stil-04-original-geheim.md`
    ist ein reines Embed-Profil (kein SYSTEMPROMPT/USERPROMPT):
    Interlinear-Rekonstruktion ohne Doppelglossen/Glossenketten,
    differenzierter Editionsapparat, Glossar-Verweis ohne konkrete Liste,
    Anwendungsregel Temuedschin vs. Dschingis Khan.
- **Geheime Geschichte der Mongolen** (Stand 2026-07-22, Abend):
  - Quelle: Japanische Uebersetzung 成吉思汗実録 von 那珂通世 (1907), via
    Wikisource-EPUB. Quellsprache `ja`, Ziel `de`.
  - Branch: `codex/geheime-geschichte-mongolen-prompts` (Commit `d8330eb`
    gepusht: Buchpaket + Generator + stil-04). Spaetere Szenen-Umbau-
    und Doku-Aenderungen waren danach lokal noch uncommitted.
  - Struktur: `structure.mode: scenes` (nicht mehr `chapter_as_scene`).
    15 Kapitel (000 Prolog/序論 + 001–014 = 12 Baende). Arbeitseinheiten
    sind die §-Abschnitte der Edition als
    `work/scenes/ja/NNN/scene-NN.md` (~317 Abschnitte; Kapitel 006 = 20
    Szenen). Gruppen-Labels („Einleitung“, „Erstes Buch“, …). Export ohne
    Szenenmarker (`display.scenes.show: false`).
  - Import: `tools/import_geheime_geschichte.py` schreibt `scene-NN.md`
    und Kapitelquellen mit `## N`-Headings. Einmalige Migration alter
    `NN-source.md`:
    `python tools/import_geheime_geschichte.py --migrate-existing`.
    Danach kann `extract_scenes.py` die Kapitelquelle erneut zerlegen.
  - Frueher: Kapitel als ein `scene-01.md`-Monolith + mechanisches
    Zeichen-Chunking (9500). Die Import-`NN-source.md` wurden ignoriert,
    weil `list_source_scene_paths` nur `scene-*.md` sucht.
  - UI: Kapitel-Dropdowns zeigen `006 — Sechstes Buch`; Batch-Log
    `Kapitel ausgewaehlt (N): 006`.
  - Uebersetzung: stil-01-original fuer Grossteil 000–010 als alte
    Kapitel-Monolithe in DE-`scene-01.md`. stil-04 + DeepSeek V4 Flash
    fuer Kapitel 006 (zuerst Chunks auf Monolith, dann Profil-Fixes).
    **Achtung:** Alte DE-`scene-01.md` = Ganzkapitel, nicht der neue
    kurze Abschnitt 01. Neuuebersetzung braucht `--overwrite` bzw.
    manuelles Beiseitelegen der Legacy-DEs. Abschnittsweise Neu-
    uebersetzung von 006 steht aus.
  - Prompt-Archiv: `work/prompts/sent/` fuer OpenRouter-Laeufe.
  - Export: EPUB mit Seitenumbruechen (`--split-level=1`), Cover und
    Kapitelbilder; `group_for_chapter()` kennt `chapters`-Listen.
  - OpenRouter-Client: Timeout 300s, keine Retries bei Timeouts
    (teils noch uncommitted neben dem Prompt-Commit).
  - Review: `length_ratio` fuer CJK (ja/zh/ko) uebersprungen; Deep-Check
    mit names.yaml; Dashboard Erstpruefung vs. Deep-Check getrennt
    (teils noch lokal uncommitted).
- **Die dritte Chronik** (Stand 2026-07-24):
  - DE-Originalroman (kein Uebersetzungsprojekt); Autor-Platzhalter
    „Motivatier“; Impressum analog Peter (Motivatier Hermann Stiftung).
  - Quelle fuehrend: `source/Die dritte Chronik.md` (~117k Woerter,
    48 `##`-Kapitel). DOCX nur Backup.
  - Paket: `book.yaml` / `export.yaml` / `names.yaml` / `stil-01-original`.
    `structure.mode: chapter_as_scene`; Display `format: literary`
    (literarische Titel, kein „Erstes Kapitel“).
  - Import: `python tools/import_die_dritte_chronik.py` zerlegt MD in
    `work/chapters/NNN-source.md` und DE-Szenen unter
    `work/scenes/de/stil-01-original/NNN/scene-01.md` (Status done).
  - Export-Pfad bereit (DOCX/EPUB/PDF); Fokus bisher: Kapitelbilder.
  - Expose in `export.yaml` (summary/description) aus dem Buch-Expose
    eingetragen; Autor-Bio weiterhin Platzhalter.
- **Higgsfield / Dashboard-Bilder** (Stand 2026-07-24):
  - Modellkatalog: `config/higgsfield_models.yaml` +
    `tools/lib/higgsfield_models.py` (Soul 2.0, Nano Banana Pro /
    `nano_banana_2`, GPT Image 2, Seedream 5.0 Pro/Lite).
  - Dashboard „Bilder“: Dropdown Bildmodell; bei GPT zusaetzlich
    Aufloesung + Render-Qualitaet (`low`/`medium`/`high` via
    `--render-quality`). API: `GET /api/higgsfield-models`.
  - Prompt-Bau: kurzer Marker `Chapter NNN.` (bzw. `Chapter NNN Scene NN.`)
    oben, dann `illustration_setting` aus `book.yaml`, dann Textauszug.
    Kein Buch-/Titel-Tracking, keine No-Lettering-Floskeln.
  - Web-UI-Moodboards und „Unlimited“ sind CLI/API-seitig **nicht**
    waehlbar (nur manuell in der Higgsfield-Web-UI). Workflow: CLI-Draft
    ohne Moodboard → in Web-UI mit Moodboard neu erzeugen → Download
    manuell nach `assets/chapter/chapter-NNN.jpg` (Dateiname von HF ist
    `hf_…_uuid.png`; UUID = Job-ID).
  - Dry-run darf vorhandene Zielbilder nicht mehr abbrechen (nur echte
    Generierung ohne `--overwrite` bricht ab). Batch-Fehler zuletzt:
    Dry-run auf schon fertigen Bildern; gelegentlich Higgsfield HTTP 502.
  - **Asset-Optimierung** fuer schlanke EPUBs: CLI
    `tools/optimize_asset_images.py` und Dashboard-Panel „Exportbilder
    optimieren“ (Action `optimize_assets`). Export-JPG nach
    `image_processing` (Kapitel/Szenen oft 1024/q60; Cover eigener
    Block); PNG und grossere Vorversionen bleiben als `*_alt.jpg`.
    Export-Prioritaet: `.jpg` vor `.png`. Details:
    `docs/higgsfield-integration.md`.
- **Noch offen / naechster sinnvoller Schritt:**
  1. *Die dritte Chronik:* restliche Kapitelbilder erzeugen (Web-UI-
     Moodboard-Workflow oder CLI ohne Moodboard); Cover ablegen;
     EPUB-Export.
  2. Optional: Dashboard neu starten nach Frontend-/API-Aenderungen;
     uncommitted Tool-/Buch-Aenderungen committen (nur auf Wunsch).
  3. *Geheime Geschichte:* Legacy-DE-Monolithe quarantäneieren;
     Kapitel 006 abschnittsweise neu (stil-04); optional PR.
