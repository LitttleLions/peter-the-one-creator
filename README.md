# peter-the-one

Python-Werkbank fuer kapitel- und szenenweise literarische Uebersetzung
(`ru -> de`) mit Style-Profilen, OpenRouter, Prompt-Datei-Modus,
Workspace-KI-Modus, Streamlit-Dashboard und DOCX-/EPUB-Export.

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

## Buchpakete

Jedes Buch ist ein transportierbares Paket:

```text
books/<book-id>/
  book.yaml
  export.yaml
  names.yaml
  source/
  assets/covers/
  styles/
  work/
    chapters/
    scenes/ru/
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

Alte zentrale Dateien aus der vorherigen Struktur liegen unter
`config/legacy/`. Neue Tools lesen `books/*/book.yaml`, nicht mehr
`config/books.yaml`.

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
python tools/translate_chapter.py --book anna-karenina --chapter 001 --style stil-01-original --provider openrouter
python tools/translate_batch.py --book anna-karenina --from 001 --to 005 --style stil-01-original --provider prompt_file --dry-run
python tools/translate_batch.py --book anna-karenina --missing --style stil-01-original --provider openrouter --assemble-after
python tools/assemble_chapter.py --book anna-karenina --chapter 001 --style stil-01-original
python tools/export_manuscript.py --book anna-karenina --scope chapter --chapter 001 --style stil-01-original --format all --allow-partial
```

`translate_batch.py` ist ein Uebersetzungs-Batch, kein Export-Befehl. Er
erzeugt fehlende RU-Arbeitseinheiten bei Bedarf und startet danach
`translate_chapter.py` fuer die ausgewaehlten Kapitel. Mit `--assemble-after`
werden anschliessend die Kapiteldateien per `assemble_chapter.py`
zusammengesetzt. DOCX/EPUB entstehen erst ueber `export_manuscript.py`.

Fuer neue Buecher liegt eine kopierbare KI-Vorlage unter
`docs/book-metadata-prompt.md`. Sie sammelt Titel, Autor, Zusammenfassung,
Autorenleben, Strukturvorschlag und erste Namensliste fuer `book.yaml`,
`export.yaml` und `names.yaml`. Das Dashboard zeigt diese Vorlage im Tab
`Buch-Setup` an.

## Provider

- `openrouter`: sendet RU-Szenen an OpenRouter und schreibt DE-Szenen.
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

`tools/export_manuscript.py` erzeugt DOCX und EPUB aus fertigen DE-Szenen.
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

Coverpfade sind relativ zum Buchpaket:

```yaml
book:
  cover:
    mode: image
    image_path: assets/covers/annakarenina.png
```

Ausgaben landen unter:

```text
books/<book-id>/exports/<style>/chapter/docx/
books/<book-id>/exports/<style>/chapter/epub/
books/<book-id>/exports/<style>/book/docx/
books/<book-id>/exports/<style>/book/epub/
```

## Dashboard

Start:

```bash
streamlit run tools/dashboard.py
```

URL: `http://localhost:8501`

Das Dashboard liest Buchpakete aus `books/*/book.yaml`. Es bietet Uebersicht,
Buchsetup, Uebersetzen, Stiltest, Versionen, Export und Logs. Die verbindliche
Optik-Referenz liegt in `docs/dashboard-design-system.md`.

Lange Batch-Laeufe im Uebersetzen-Tab werden als Hintergrundprozess gestartet.
Das Dashboard zeigt PID und Logdatei an; der Stop-Button beendet unter Windows
den gesamten Prozessbaum. Trockenlaeufe (`Batch planen`) bleiben synchron und
schreiben nichts.

Architektur-Notiz fuer spaeter: Streamlit bleibt vorerst die lokale Werkbank,
weil es schnell startbar ist und die eigentliche Pipeline in CLI-Tools liegt.
Das Dashboard soll deshalb moeglichst duenn bleiben: Anzeigen, Formulare,
Buttons, Status und Logs; keine eigene komplexe Pipeline-Logik. Robustheit
entsteht ueber klare Service-/CLI-Funktionen, Job-Statusdateien und saubere
Prozessausgaben.

Falls Streamlit trotz dieser Entkopplung zu schwer steuerbar wird, ist
NiceGUI der bevorzugte Nachfolger. Es bleibt Python-first und lokal im Browser,
ist aber staerker event- und zustandsorientiert. Electron oder Tauri waeren
erst sinnvoll, wenn daraus eine echte verteilbare Desktop-App werden soll.

## Tests

```bash
python -m py_compile tools/dashboard.py tools/export_manuscript.py
python -m unittest discover -s tests
```
