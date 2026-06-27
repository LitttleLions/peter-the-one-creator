# peter-the-one

Python-Werkbank fuer kapitel- und szenenweise literarische Uebersetzung
(`ru -> de`) mit Style-Profilen, OpenRouter, lokales Ollama, Prompt-Datei-Modus,
Workspace-KI-Modus, Streamlit-Dashboard und DOCX-/EPUB-/PDF-Export.

Die wichtigste Architekturentscheidung: **Szenen werden einzeln uebersetzt,
Kapitel und Exporte werden danach per CLI aus Dateien zusammengesetzt.**
Dadurch werden fertige Kapitel nicht unnoetig erneut durch ein LLM geschickt.

## Schnellstart Fuer KI Und Menschen

1. Lies `AGENTS.md`, dann diese README.
2. Arbeite immer buchbezogen unter `books/<book-id>/`.
3. Aendere Originalquellen in `books/<book-id>/source/` und Material in
   `logic/` nicht ohne ausdrueckliche Rueckfrage.
4. Pruefe den Stand mit `python tools/status.py --book <book-id> summary`.
5. Produktive Style-Profile liegen in `books/<book-id>/styles/*.md`.

> **Keine Memory Bank:** Dieses Projekt pflegt bewusst keine Cline Memory Bank
> (`memory-bank/`). Massgeblicher Kontext sind AGENTS.md, README.md sowie die
> buchlokalen `book.yaml`- und `export.yaml`-Dateien. Der Ordner `memory-bank/`
> steht in `.gitignore`.

## Voraussetzungen

### Python-Abhaengigkeiten

```bash
pip install -r requirements.txt
```

### Externe Tools

| Tool | Zweck | Installation |
|------|-------|--------------|
| **Streamlit** (>= 1.36) | Dashboard | Enthalten in `requirements.txt` |
| **Pandoc** (>= 3.0) | EPUB-Export | `winget install --id JohnMacFarlane.Pandoc` oder manuell von https://pandoc.org/installing.html |
| **Playwright Chromium** | PDF-Export | `python -m playwright install chromium` nach `pip install -r requirements.txt` |
| **Higgsfield CLI** | Kapitel-/Szenenbilder | `npm install -g @higgsfield/cli`, Details in `docs/higgsfield-integration.md`. **Stand 2026-06-24:** Korrekte Moodboard-Laeufe setzen in der History `params.style_id`; die CLI bietet fuer `text2image_soul_v2` aber keinen `--style_id`-Parameter. `--custom_reference_id` ist dafuer nicht korrekt. |
| **Ollama** (optional) | Lokale LLM-Inference | https://ollama.ai/ - Modelle: `ollama pull gemma4:latest` (empfohlen), `ollama pull qwen3:8b` (optional) |

> **Hinweis:** Nach der Pandoc-Installation muss ein neues Terminal gestartet werden,
> damit der Pfad erkannt wird. Unter Windows liegt Pandoc typischerweise unter
> `C:\Users\<user>\AppData\Local\Pandoc\pandoc.exe`.

> **Ollama-Info:** Mit lokaler Ollama-Installation können Sie offline übersetzen.
> Verfügbare Modelle: `ollama list`. Ollama API läuft auf `http://localhost:11434`.
> Für `gemma4:latest` nutzen Sie: `python tools/translate_chapter.py --book <id> --chapter 001 --provider ollama --model gemma4:latest`

## Buchpakete

Jedes Buch ist ein transportierbares Paket:

```text
books/<book-id>/
  book.yaml
  export.yaml
  names.yaml
  source/
  assets/covers/
  assets/chapter/
  assets/scene/
  styles/
  work/
    chapters/
    scenes/<source_lang>/
    scenes/de/<style>/
    assembled/<style>/
    prompts/
    style-tests/
    legacy/
  exports/<style>/<chapter|book>/
  status/status.json
  status/logs/
```

Aktuelle Pakete:

- `books/peter-i-buch-01/`
- `books/anna-karenina/`
- `books/pharao/`

Alte zentrale Dateien aus der vorherigen Struktur liegen unter
`config/legacy/`. Neue Tools lesen `books/*/book.yaml`, nicht mehr
`config/books.yaml`.

## Quellformate und EPUB-Verarbeitung

`extract_chapters.py` unterstützt drei Quellformate:

| Format | Erkennung | Kapitelerkennung |
|--------|-----------|------------------|
| **RTF** | `{\rtf`-Header | Überschriften via `striprtf` + Heading-Patterns |
| **XHTML/HTML** | `<!doctype html>`, `<html>`, `<?xml>` | `<h3>`-Headings mit `Глава N`-Match |
| **Plaintext** | Alles andere | Heading-Patterns (`Глава`, `Книга`, `Часть`) |

**EPUB-Quellen müssen zuerst ausgepackt werden**, da EPUB ein ZIP-Container
ist. Zwei Wege:

1. **Empfohlen: XHTML entpacken** (genaueste Kapitelerkennung):
   ```bash
   # EPUB ist ein ZIP – einfach entpacken
   Expand-Archive -Path "books/feuriger-engel/source/mein-buch.epub" -DestinationPath "books/feuriger-engel/source/_epub/"
   # Das Haupt-XHTML liegt meist als OEBPS/*.xhtml – nach source/ kopieren
   Copy-Item "books/feuriger-engel/source/_epub/OEBPS/*.xhtml" "books/feuriger-engel/source/"
   # In book.yaml auf die XHTML-Datei verweisen
   ```
   Die `rtf_parser.py` erkennt XHTML automatisch und parst `<h3>`-Headings
   als Kapitelüberschriften. Nur Headings mit `Глава N` werden als
   Kapitelgrenzen gewertet – Unterüberschriften wie `1`, `I`, `II` werden
   in das aktuelle Kapitel mit aufgenommen.

2. **Pandoc-Konvertierung** (Plaintext, verliert Heading-Struktur):
   ```bash
   pandoc --from epub --to plain "quelle.epub" > "quelle.txt"
   ```
   Nachteil: Aus `<h3>` werden Fließtextabsätze – die Heading-Patterns
   müssen allein anhand des Texts matchen, was weniger zuverlässig ist.

## Befehle

```bash
pip install -r requirements.txt

# Dashboard
streamlit run tools/dashboard.py

# Status
python tools/status.py --book anna-karenina summary
python tools/status.py --book anna-karenina list

# Neues Buchpaket aus einer Quelle anlegen
python tools/init_book.py --source "books/Meine Quelle.rtf"

# Pipeline
python tools/extract_chapters.py --book anna-karenina
python tools/extract_scenes.py --book anna-karenina --chapter 001

# Mit OpenRouter (Standard, Remote-API mit Token-Limit)
python tools/translate_chapter.py --book anna-karenina --chapter 001 --style stil-01-original --provider openrouter

# Mit lokalem Ollama (offline, kostenlos, schnell)
python tools/translate_chapter.py --book anna-karenina --chapter 001 --style stil-01-original --provider ollama --model gemma4:latest
# Alternative Modellwahl
python tools/translate_chapter.py --book anna-karenina --chapter 001 --style stil-01-original --provider ollama --model qwen3:8b

# Batch-Übersetzung mit Ollama
python tools/translate_batch.py --book anna-karenina --missing --style stil-01-original --provider ollama --model gemma4:latest --assemble-after

# Oder mit Prompt-Dateien für manuelle Bearbeitung
python tools/translate_batch.py --book anna-karenina --from 001 --to 005 --style stil-01-original --provider prompt_file --dry-run
python tools/assemble_chapter.py --book anna-karenina --chapter 001 --style stil-01-original
python tools/export_manuscript.py --book anna-karenina --scope chapter --chapter 001 --style stil-01-original --format all --allow-partial
python tools/export_manuscript.py --book anna-karenina --scope chapter --chapter 001 --style stil-01-original --format pdf --allow-partial

# Review-Fixes aus vorhandenen Review-JSONs
python tools/apply_review_suggestions.py --book anna-karenina --style stil-01-original --plan
python tools/apply_review_suggestions.py --book anna-karenina --style stil-01-original --stage
python tools/apply_review_suggestions.py --book anna-karenina --style stil-01-original --promote

# Illustrationen (Kapitel-/Szenenbilder via Higgsfield)
python tools/generate_illustration.py --book pharao --chapter 001 --scene 01 --kind scene --style stil-02-poetisch
python tools/generate_illustration.py --book pharao --chapter 001 --kind chapter --style stil-02-poetisch
python tools/generate_illustration.py --book pharao --chapter 001 --scene 01 --kind scene --style stil-02-poetisch --overwrite
python tools/generate_illustration.py --book pharao --chapter 001 --scene 01 --kind scene --style stil-02-poetisch --dry-run
```

`translate_batch.py` ist ein Uebersetzungs-Batch, kein Export-Befehl. Er
erzeugt fehlende Quell-Arbeitseinheiten bei Bedarf und startet danach
`translate_chapter.py` fuer die ausgewaehlten Kapitel. Mit `--assemble-after`
werden anschliessend die Kapiteldateien per `assemble_chapter.py`
zusammengesetzt. DOCX/EPUB/PDF entstehen erst ueber `export_manuscript.py`.

Grosse Quell-Szenen werden beim Uebersetzen intern in Chunks geteilt. Die
sichtbare Buchstruktur bleibt gleich: Chunks unter `work/chunks/` werden nach
erfolgreicher Uebersetzung wieder zur urspruenglichen
`work/scenes/de/<style>/<chapter>/scene-XX.md` zusammengesetzt. Die Grenze
steht in `book.yaml` unter `ai.chunk_char_limit` (Fallback:
`config/pipeline.yaml`) und kann pro Lauf mit `--chunk-char-limit`
ueberschrieben werden.

Chunk-Aufrufe nutzen ein eigenes Token-Limit: `ai.max_tokens_per_chunk`
in `book.yaml` (Fallback: `max(max_tokens_per_scene, 12000)`). Das ist
noetig, weil deutsche Uebersetzungen oft laenger sind als das russische
Original und das normale `max_tokens` fuer Chunks nicht ausreicht.

Fuer neue Buecher liegt eine kopierbare KI-Vorlage unter
`docs/book-metadata-prompt.md`. Sie sammelt Titel, Autor, Zusammenfassung,
Autorenleben, Strukturvorschlag und erste Namensliste fuer `book.yaml`,
`export.yaml` und `names.yaml`. Das Dashboard zeigt diese Vorlage im Tab
`Buch-Setup` an.

## Provider

- `openrouter`: sendet Quell-Szenen an OpenRouter und schreibt DE-Szenen.
- `prompt_file`: schreibt vollstaendige Prompt-Dateien nach
  `books/<book-id>/work/prompts/`.
- `workspace_ai`: schreibt Arbeitsanweisungen fuer eine KI, die das Repo
  direkt im Editor nutzt.

## Style-Profile

Style-Profile sind Markdown-Dateien in `books/<book-id>/styles/`.
Der Dateiname ohne `.md` ist der technische Slug und zugleich der Ordnername
unter `work/scenes/de/<style>/`, `work/assembled/<style>/` und `exports/<style>/`.

Der aktive Default steht in `books/<book-id>/book.yaml` unter `style_mode`.
Nach Aenderungen an einem Style-Profil muessen vorhandene Szenenergebnisse
bewusst ersetzt werden, sonst zeigt die Pipeline weiter die alte Datei.

### Vorlagen- und produktiver Pfad

Es gibt **zwei** Style-Ordner mit klar getrennten Rollen:

- `styles/` (Repo-Root) enthaelt **nur Vorlagen**: `stil-01-original.md`,
  `stil-02-poetisch.md`, `stil-03-branderson.md`. Diese Dateien sind
  Referenz und werden gepflegt, wenn sich der Stil grundsaetzlich aendert.
- `books/<book-id>/styles/` ist der **produktive** Ordner pro Buch. Hier
  liegen die Profile, mit denen das jeweilige Buch tatsaechlich uebersetzt
  wird.

Workflow:

1. **Buchpaket anlegen** mit `python tools/init_book.py ...`. Das Skript
   ruft `copy_style_templates(book_root)` auf und kopiert alle `*.md` aus
   `styles/` in das neue `books/<id>/styles/`. `migrate_book_projects.py`
   macht das gleiche fuer migrierte Buecher.
2. **Pro Buch anpassen.** Sobald die Profile im Buchordner liegen, gehoeren
   Aenderungen dorthin. Anna Karenina und Peter der Erste koennen so
   unabhaengig voneinander einen anderen `stil-02-poetisch` pflegen.
3. **Globale Vorlagen aktualisieren** nur, wenn ein Stil sich grundsaetzlich
   aendert. Anschliessend `copy_style_templates` neu ausfuehren oder
   einzelne Dateien manuell nachkopieren.

### Fallback und Fehlerbild

`tools/translate_chapter.py` und `tools/translate_batch.py` laden Profile
**strikt** aus `books/<id>/styles/`. Es gibt **keinen** automatischen
Fallback auf das globale `styles/`. Fehlt eine Datei, bricht das Tool mit
`StylePromptError: Unbekannter Stil: 'stil-XX-...' ...` ab.

Das Workbench-/Dashboard-Modul `tools/lib/workbench_state.py` hat
hingegen einen Fallback, damit der Stil-Picker auch fuer Buecher ohne
kopierte Profile funktioniert. CLI-Aufrufe folgen dieser Logik **nicht**.

Wenn ein Buchpaket ohne lokale Profile existiert, muessen die gewuenschten
Stile einmalig in `books/<id>/styles/` kopiert werden, z. B.:

```bash
copy styles\stil-01-original.md books\<id>\styles\
copy styles\stil-02-poetisch.md books\<id>\styles\
copy styles\stil-03-branderson.md books\<id>\styles\
```

Danach ist der Buchordner produktiv, und die globalen Vorlagen koennen
weiterhin als Referenz dienen.

## Buchstruktur Und Namen

Jedes Buchpaket beschreibt seine Arbeitseinheiten in `book.yaml`:

```yaml
structure:
  mode: scenes           # oder chapter_as_scene
  groups: []             # optionale Teile/Binnen-Buecher
```

`scenes` bedeutet: Kapitel werden in mehrere Szenen zerlegt. `chapter_as_scene`
bedeutet: jedes Kapitel ist selbst die kleinste Arbeitseinheit. Anna Karenina
nutzt `chapter_as_scene`; Peter I nutzt `scenes`.

Die Leseranzeige von Kapiteln und Szenen wird pro Buch ueber `display`
gesteuert:

```yaml
display:
  chapters:
    format: words_de
    suffix: " Kapitel"
    align: center
    include_source_title: false
  scenes:
    show: true
    format: number
    align: center
    page_break: false
    separator: ""
```

Anna nutzt ausgeschriebene Kapitelueberschriften ohne Szenenmarker. Peter nutzt
ausgeschriebene Kapitelueberschriften und zentrierte Szenenzahlen ohne neue
Seite.

Namen und feste Begriffe liegen pro Buch in `names.yaml`:

```yaml
entries:
- source: Анна Аркадьевна Каренина
  target: Anna Arkadjewna Karenina
  aliases: [Anna Karenina]
  type: person
  status: draft
  note: Patronymisch in formellen Kontexten erhalten.
```

Die Liste wird kompakt in Prompts injiziert. Nicht gepflegte russische Namen
werden konservativ transliteriert oder im Zweifel beibehalten.

## Export

`tools/export_manuscript.py` erzeugt DOCX, EPUB und PDF aus fertigen DE-Szenen.
Metadaten, Cover, Zusammenfassung, Autorenleben, Impressum und Titelei stehen
in `books/<book-id>/export.yaml`.

Die bevorzugte Frontmatter-Folge fuer Leserexporte ist:

```text
Coverbild
Titelseite mit Titel, Autor und optionaler Uebersetzerzeile
Zusammenfassung
Leben des Autors
Textbeginn mit Teil-/Buchgruppe und Kapiteln
```

Gesteuert wird das ueber `front_matter.cover_in_body`, `title_page`,
`summary_page`, `author_bio_page`, `imprint_page` und die Buchfelder
`subtitle`, `translator`, `summary` und `author_bio`.

EPUB-Hinweis: Das Cover wird nur als offizielles EPUB-Cover ueber Pandoc
eingebunden. Die sichtbare Titelseite wird als robuste Pandoc-Div/Span-Struktur
mit CSS-Klassen erzeugt; dadurch vermeiden wir doppelte Coverseiten und
Reader-abhaengige Titel-Fragmente. Langtext-Frontmatter wie Zusammenfassung und
Autorenleben nutzt nur relative CSS-Groessen, damit Reader-Schriftgroessen
weiterhin vom Nutzer gesteuert werden koennen.

PDF-Hinweis: PDF wird explizit mit `--format pdf` erzeugt. `--format all`
bleibt rueckwaertskompatibel bei DOCX+EPUB. Der PDF-Export rendert eine
eigene HTML-/CSS-Datei mit Playwright/Chromium; Seitenformat und Raender
kommen aus dem Print-CSS (`A5` als Standard).

Coverpfade sind relativ zum Buchpaket:

```yaml
book:
  cover:
    mode: image
    image_path: assets/covers/annakarenina.png
```

Wird keine `image_path` in `export.yaml` gesetzt, erkennt der Export
automatisch eine Datei `cover.png`, `cover.jpg`, `cover.jpeg` oder
`cover.webp` in `books/<id>/assets/covers/` (case-insensitive). Erst
wenn gar kein Bild gefunden wird, entsteht ein Platzhalter-Cover.

Optionale Kapitel- und Szenenbilder werden beim Export automatisch eingebunden,
wenn `illustrations.enabled` aktiv ist und passende Dateien im Buchpaket
liegen:

```yaml
defaults:
  illustrations:
    enabled: true
    chapter_images: true
    scene_images: true
    chapter_page_break_after_image: true
    scene_page_break_after_image: false
```

Namenskonvention:

```text
books/<book-id>/assets/chapter/chapter-001.jpg
books/<book-id>/assets/scene/001/scene-002.png
```

Erlaubte Formate sind `.jpg`, `.jpeg`, `.png` und `.webp`. Fehlt ein Bild,
wird es still uebersprungen.

### Illustrationen Erzeugen

`tools/generate_illustration.py` erzeugt Kapitel- und Szenenbilder via
Higgsfield-CLI. Die Defaults (Modell, Moodboard-UUID, Seitenverhaeltnis,
Qualitaet) stehen pro Buch in `book.yaml` unter `higgsfield`.

Der Prompt an Higgsfield enthaelt automatisch:

- Einen Auszug aus der jeweiligen DE-Szene (max. 1500 Zeichen).
- Die Kurzbeschreibung des Buches aus `export.yaml` (`book.description`) als
  Kontexthinweis – z. B. "altes Aegypten", "Russland" – damit das Modell
  passende Stimmung und Kulisse waehlt.
- Visuelle Constraints: epochengerechte Kleidung/Architektur, keine modernen
  Objekte, keine lesbaren Texte oder Signaturen.

Qualitaet ist standardmaessig `1.5k` (Soul 2.0 unterstuetzt `1.5k` und `2k`).
Bestehende Bilder werden nur mit `--overwrite` ersetzt; `--dry-run` zeigt den
Prompt ohne API-Call an. Details: `docs/higgsfield-integration.md`.

Ausgaben landen unter:

```text
books/<book-id>/exports/<style>/chapter/docx/
books/<book-id>/exports/<style>/chapter/epub/
books/<book-id>/exports/<style>/chapter/pdf/
books/<book-id>/exports/<style>/book/docx/
books/<book-id>/exports/<style>/book/epub/
books/<book-id>/exports/<style>/book/pdf/
```

## Dashboard

Start:

```bash
python tools/start_dashboard.py
```

URL: `http://127.0.0.1:8000`

Das Dashboard liest Buchpakete aus `books/*/book.yaml`. Es bietet Uebersicht,
Buchsetup, Uebersetzen, Stiltest, Review, Export, Higgsfield/Bilder, Namen und
Logs. Die verbindliche Optik-Referenz liegt in
`docs/dashboard-design-system.md`.

Lange Uebersetzungs- und Review-Laeufe werden ueber den framework-neutralen
Job-Service `tools/lib/dashboard_jobs.py` als Hintergrundprozesse gestartet.
Job-Metadaten liegen pro Lauf unter `var/dashboard-jobs/<job-id>.json`, Logs
daneben als `.log`. Das globale Job-Panel bleibt nach Seitenwechsel sichtbar,
zeigt Fortschritt/Log-Tail und kann den Prozessbaum stoppen. Trockenlaeufe
(`Batch planen`, `Review planen`) bleiben synchron und schreiben nichts.

Das dauerhafte Dashboard ist **FastAPI + Vite/React**. Der Startbefehl baut
das React-Frontend bei Bedarf (`webapp/frontend/dist/`) und FastAPI liefert den
Build direkt unter `/` aus. Die API bleibt unter `/api/...` erreichbar.
Kommando-Builder, Lesemodelle und Kontextdaten fuer Uebersetzen, Review,
Export, Namen, Stiltest und Bilder liegen in `tools/lib/workbench_api.py`. Die
CLI-Tools bleiben weiterhin die produktive Pipeline.

Die Buch-Settings-Seite arbeitet zweistufig: Aenderungen wirken sofort als
lokaler Arbeitskontext in der Oberflaeche. Erst der Button
`In book.yaml speichern` schreibt die buchnahen Produktionsdefaults
(`style_mode`, `ai.provider`, `ai.model`, `ai.chunk_char_limit`) in das
Buchpaket. Das Speichern aktualisiert diese YAML-Zeilen gezielt und erzeugt
`book.yaml` nicht komplett neu. Review- und Export-Auswahl bleiben lokale
UI-Voreinstellungen.
Der Stiltest rendert Markdown-Blockquotes und geklammerte Nebenabsatz-Zeilen
typografisch eingerueckt/kursiv, ohne die gespeicherten Markdown-Dateien zu
veraendern.

Entwicklungsmodus mit zwei Terminals:

```bash
python -m uvicorn webapp.backend.main:app --reload --host 127.0.0.1 --port 8000
cd webapp/frontend
npm install
npm run dev
```

Der Vite-Dev-Server laeuft standardmaessig auf `http://127.0.0.1:5173` und
proxyt `/api` an das FastAPI-Backend auf `http://127.0.0.1:8000`.

Legacy-Streamlit bleibt als Backup-Werkbank verfuegbar:

```bash
streamlit run tools/dashboard.py
```

## Tests

```bash
python -m py_compile tools/dashboard.py tools/export_manuscript.py
python -m unittest discover -s tests
```
