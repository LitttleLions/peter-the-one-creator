# AGENTS.md - Kontext fuer KI-Werkzeuge

> Dies ist die zentrale Kontextdatei. `CLAUDE.md` verweist auf diese Datei.
> Lies zuerst diese Datei und die README, dann beginne mit der Arbeit.

## Was Dieses Projekt Ist

Regelbasierte kapitel- und szenenweise Uebersetzung literarischer Werke
(`ru -> de`). Das Repo ist jetzt buchzentriert: jedes produktive Buch ist ein
eigenes Paket unter `books/<book-id>/`. Tools und Dashboard entdecken Buecher
ueber `books/*/book.yaml`; `config/books.yaml` ist nur noch Legacy unter
`config/legacy/`.

Aktuelle Buchpakete:

- `books/peter-i-buch-01/` - Alexei Tolstoi, Peter der Erste
- `books/anna-karenina/` - Lew Tolstoi, Anna Karenina

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
    scenes/ru/NNN/          # RU-Szenen
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
- **Streamlit** (>= 1.36): Wird fuer das Dashboard benoetigt.
  Enthalten in `requirements.txt`. Start mit `streamlit run tools/dashboard.py`.
- **Pandoc** (>= 3.0): Wird fuer den EPUB-Export benoetigt.
  Installation: `winget install --id JohnMacFarlane.Pandoc`
  Nach Installation muss ein neues Terminal gestartet werden.
- **Playwright Chromium:** Wird fuer den PDF-Export benoetigt.
  Installation nach `pip install -r requirements.txt`:
  `python -m playwright install chromium`
- **`.env`-Datei:** Kopiere `.env.example` nach `.env` und trage
  den `OPENROUTER_API_KEY` ein (OpenRouter-Account noetig).

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

# RU-Szenen erzeugen
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
streamlit run tools/dashboard.py
```

`translate_batch.py` ist ein Uebersetzungs-Batch, kein Export-Befehl. Er
erzeugt fehlende RU-Arbeitseinheiten bei Bedarf und ruft danach
`translate_chapter.py` fuer mehrere Kapitel auf. Kapitel-Assembly passiert
nur mit `--assemble-after` oder separat ueber `assemble_chapter.py`;
DOCX/EPUB/PDF entstehen erst ueber `export_manuscript.py`.

## Style-Profile

Jedes Buchpaket hat eigene Profile in `books/<book-id>/styles/*.md`.
Der Dateiname ohne `.md` ist der Style-Slug und zugleich der Output-Ordner.
Der aktive Default steht in `books/<book-id>/book.yaml` unter `style_mode`.

Das gewaehlte Profil wird als verbindlicher Block in den System-Prompt
gehoben. Wenn ein Profil Vorabsatz, Lede, Ueberschriften oder andere
Struktur-Ergaenzungen erzwingen soll, muss das ausdruecklich in der
Markdown-Datei stehen. Nach Profil-Aenderungen vorhandene Szenenergebnisse
bewusst mit `--overwrite`, Dashboard-Ersetzen oder Loeschen neu erzeugen.

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
`aliases`, `type`, `status` und `note`. Diese Liste wird kompakt in den Prompt
eingefuegt. Nicht gepflegte russische Namen werden konservativ transliteriert
oder im Zweifel beibehalten.

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
`books/<book-id>/export.yaml`. Coverpfade sind relativ zum Buchpaket, z. B.
`assets/covers/annakarenina.png`.

Optionale Exportbilder liegen ebenfalls relativ zum Buchpaket. Kapitelbilder
werden als `assets/chapter/chapter-NNN.*` abgelegt, Szenenbilder als
`assets/scene/NNN/scene-NNN.*`. Unterstuetzt werden `.jpg`, `.jpeg`, `.png`
und `.webp`; fehlende Bilder werden uebersprungen. Gesteuert wird dies ueber
`illustrations` in `export.yaml`.

Standardfolge fuer Leserexporte: Coverbild, Titelseite, Zusammenfassung,
Leben des Autors, dann Textbeginn mit Teil-/Buchgruppe und Kapiteln.

PDF wird explizit mit `--format pdf` erzeugt. `--format all` bleibt
rueckwaertskompatibel bei DOCX+EPUB.

## Aktueller Stand

- Buchpakete sind fuehrend; alte zentrale `config/books.yaml` und
  `config/export.yaml` liegen unter `config/legacy/`.
- OpenRouter, Prompt-Datei-Modus, Workspace-KI-Modus, Assembly und Export sind
  produktiv nutzbar.
- Dashboard liest Buchpakete aus `books/*/book.yaml`.
- Anna Karenina ist als zweites Buchpaket angelegt und hat ein Cover unter
  `books/anna-karenina/assets/covers/annakarenina.png`.
