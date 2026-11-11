# peter-the-one

Python-Werkbank fuer kapitel- und szenenweise literarische Uebersetzung
(`ru -> de`, teils `ja -> de`) mit Style-Profilen, OpenRouter, lokalem Ollama,
Prompt-Datei-Modus, Workspace-KI-Modus, FastAPI/React-Dashboard,
Motivatier-Regal-Website und DOCX-/EPUB-/PDF-Export.

Die wichtigste Architekturentscheidung: **Szenen werden einzeln uebersetzt,
Kapitel und Exporte werden danach per CLI aus Dateien zusammengesetzt.**
Dadurch werden fertige Kapitel nicht unnoetig erneut durch ein LLM geschickt.

## Schnellstart Fuer KI Und Menschen

1. Neues Chat-Fenster, gleicher Ordner: Kopiertext
   [docs/uebergabe-prompt.md](docs/uebergabe-prompt.md). Der Kopiertext sagt
   klar: **erst diese README (Schnellstart + Arbeitsplan) und
   `docs/kontextanalyse.md` (Abschnitt 1 + 5) lesen, dann den Stand melden
   und auf die Aufgabe warten.** `docs/HANDOVER.md` und
   `docs/offene-punkte.md` erst lesen, wenn die konkrete Aufgabe sie
   braucht. Unter Windows die Projektumgebung
   `.\.venv\Scripts\python.exe` verwenden (siehe Voraussetzungen).
2. Arbeite immer buchbezogen unter `books/<book-id>/`.
3. Aendere Originalquellen in `books/<book-id>/source/` und Material in
   `logic/` nicht ohne ausdrueckliche Rueckfrage. Neufassungen DE-Originale nur
   ueber RomanForge-Export (`docs/uebernahme-romanforge.md`), nicht mehr als
   Dateien unter `status/`. `source/` bleibt tabu.
4. Pruefe den Stand mit `.\.venv\Scripts\python.exe tools/status.py --book <book-id> summary`. Bei `Buch mit id=<x> nicht gefunden`: sofort stoppen, keine Alternativ-ID erfinden oder per Zweitordner anlegen; aehnliche IDs aus der Fehlermeldung beachten und per Rueckfrage klaeren. Suche immer mit Pfad-Filter (`Select-String -Path '<pfad>' -Pattern '<muster>'`), nie ungefiltert ueber das ganze Repo - der Suchindex enthaelt `node_modules/`, `.npm-cache/` und generierte Artefakte und liefert sonst 100 Kollateraltreffer.
5. Baue keine eigenen Pruef-Skripte oder Datei-Listen. Nutze die vorhandenen
   CLIs unter `tools/` (z. B. `review_manuscript.py`, `status.py`,
   `assemble_chapter.py`, `export_manuscript.py`). Alles andere ist unnoetiger
   Eigenbau. Keine `SUMMARY*.md` im Repo-Root, keine `tools/create_*.py` ohne
   Freigabe; Placeholder-Bilder gehoeren nicht zur Pipeline.
   In der PowerShell kein `head`/`grep` verwenden
   (`Select-Object -First N`); bei labiler Shell ein CLI pro Aufruf.
   Chronik-Gate: `.\.venv\Scripts\python.exe tools/review_manuscript.py --book die-dritte-chronik --style stil-01-original --all --llm none --fail-on-errors`
   (ERROR=0/WARNING=13/INFO=36; Details `docs/offene-punkte.md` Punkt 6 + 12).
   Print-Vergleich Pharao: `books/pharao/exports/stil-02-poetisch/book/print/print-comparison-20260921-pharao-abcd.md`
   (A 924 / B 788 / C 673 / D 643 Seiten; Cream-Limit 776).
6. Produktive Style-Profile liegen in `books/<book-id>/styles/*.md`.

> **Keine Memory Bank:** Dieses Projekt pflegt bewusst keine Cline Memory Bank
> (`memory-bank/`). Massgeblicher Kontext sind AGENTS.md, README.md,
> `docs/HANDOVER.md`, `docs/uebergabe-prompt.md` sowie die buchlokalen
> `book.yaml`- und `export.yaml`-Dateien. Der Ordner `memory-bank/`
> steht in `.gitignore`.
>
> **Einstiegskosten:** Warum der Einstieg so teuer ist und welche Hebel es
> gibt, steht gemessen in [docs/kontextanalyse.md](docs/kontextanalyse.md).

## Arbeitsplan / Offene Punkte

Aktuelle Prioritaeten und Checklisten: [docs/offene-punkte.md](docs/offene-punkte.md).
Dort ist auch die vorgezogene **Pruefung Uebersetzung Peter der Erste** dokumentiert.

Aelita (LIVE 09/2026, veroeffentlicht): Regelcheck 0 Fehler / 0 Warnungen, Kommentare des
Schlusskapitels 030 sind aus der DE-Szene in den Anhang „Kommentare“
ausgelagert (neues `appendices:`-Feature im Export, siehe AGENTS.md), alle
vorhandenen Kapitelbilder als Export-JPG optimiert, Buch-EPUB 2026-09-17
nutzergeprueft. Rest: Amazon-URL + Marketing nach Amazon-Freigabe; 12 Kapitel bleiben bewusst ohne Bild.

Leben Arsenjews (Release-Kandidat 09/2026): Gate ERROR=0/WARNING=8, Buch-EPUB
`book-das-leben-arsenjews-stil-02-poetisch-20260917-212334.epub` ohne Bypass.
Offen: Kindle Previewer + menschliche Stichprobe (029/034/037/040).

Die dritte Chronik (DE-Original, Redaktion 09/2026 abgeschlossen, KDP-fertig
2026-09-21): Gate ERROR=0/WARNING=13/INFO=36, 29 von 48 Kapiteln clean 0/0.
Aktuelles Buch-EPUB `book-die-dritte-chronik-stil-01-original-20260921-131112.epub`
(48/48 Kapitel, 50 Bilder inkl. Cover, ohne Bypass; aelterer Stempel
`20260919-222611` ist ueberholt). Rest-Tabelle: `docs/offene-punkte.md`
Punkt 6 + 12. Offen: Kindle-Preview + Leseprobe, KDP-Upload durch Nutzer.

Redaktions-/Uebernahme fuer DE-Originale laeuft seit 2026-10-07 ueber RomanForge
(`docs/uebernahme-romanforge.md`, Stufe 1, commit `e93f4a2`); Ausgangsstand
versioniert unter `books/die-dritte-chronik/work/imports/romanforge/`.

Die Sprache des Anderen (`books/die-sprache-des-anderen/`, Timo Verita,
DE-Original): 34/34 Kapitel, Gate ERROR=0/WARNING=0/INFO=0, Buch-EPUB
`book-die-sprache-des-anderen-stil-01-original-20261110-132245.epub`
(8,0 MB, ohne Bypass) mit Cover (Titel/Autor im Bild) und Kapitelbildern
001-034. Titelei (Rechte, Untertitel, Zusammenfassung, Autorenbio, Impressum)
ist gefuellt; siehe `docs/HANDOVER.md`.
Bild-Prompt seit 2026-11-10 ueber **Vignetten**
(`work/prompts/higgsfield/vignettes/<kapitel>.json`): der Moment waehlt
Figuren und Gegenstaende, das Aussehen kommt aus `names.yaml` (RomanForge),
der Stilanker steht kurz am Ende. Print-Satz (Stempel `134427`,
`--illustration-mode chapter_head`): Innenleben 330 Seiten, Komplett-PDF 332,
Wrap 306,6 x 222,2 mm mit 20,96 mm Ruecken und Druckcover
`assets/covers/cover-print.jpg`. Offen: KDP-Upload und Kindle-Preview;
Details in `docs/higgsfield-integration.md` und `docs/offene-punkte.md`
Punkt 14.
Der Lotse von Ruegen (`books/der-lotse-von-ruegen/`, Timo Verita,
DE-Original): 33/33 Kapitel, Gate ERROR=0/WARNING=0/INFO=20, Cover +
Kapitelbilder 001-010; Regal-Freigabe `website.enabled: true`
(sort_order 90), Live-Deploy steht aus.
Zusaetzlich gibt es `books/der-lotse/` (id `der-lotse`, 32 Kapitel, 32
Bilder, Gate 0/1/42, `website.enabled: false`) aus `origin/main` - beide
Pakete gehoeren zum selben Roman und bleiben erhalten; vor Aktionen an
einem der beiden Rueckfrage.
Perfect Sight Without Glasses (`books/perfect.sight/`, Sachbuch `en->de`,
Stil `stil-05-sachbuch`) ist ebenfalls neu.

Pharao (LIVE): Print-Optionen 2026-09-21 auf `main` (Trim/Profil/Bilder).
Innenleben A–D: 924 / 788 / 673 / 643 Seiten; Cream-Limit 776. Gate ERROR=0
nach restaurierter Einleitung 000. Vergleich:
`books/pharao/exports/stil-02-poetisch/book/print/print-comparison-20260921-pharao-abcd.md`.
Offen: Print-Leseprobe und Entscheidung 788 vs. 776 fuer 6x9 classic
(`docs/offene-punkte.md` Punkt 11).

## Voraussetzungen

### Python-Abhaengigkeiten

Unter Windows im Repository-Root eine Projektumgebung anlegen und Pakete
gezielt dort installieren (nur bei fehlender Umgebung bzw. fuer die Einrichtung):

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Bei vorhandener `.venv` den ersten Befehl nicht erneut ausfuehren. Fuer
Projektbefehle und Paketinstallation immer diesen Interpreter verwenden;
`py -3`, `python` und `pip` koennen unterschiedliche Installationen waehlen.
Eine Aktivierung ist nicht erforderlich. Die folgenden `python`-Beispiele gelten
unter Windows mit `.\.venv\Scripts\python.exe` anstelle von `python`.
Auf anderen Systemen entsprechend `.venv/bin/python` verwenden.

Bei Problemen in PowerShell pruefen:

```powershell
Get-Command py, python, pip -All
py -0p
.\.venv\Scripts\python.exe -c "import sys; print(sys.executable, sys.version)"
.\.venv\Scripts\python.exe -m pip check
```

Fehlende Pakete mit dem obigen `-m pip install` in der Projektumgebung
installieren. Ist `.venv` nicht startbar, zuerst die Fehlermeldung und den
Python-Pfad pruefen; die Umgebung nicht ungefragt loeschen. PowerShell nutzt
fuer npm bei Problemen mit `npm.ps1` den Aufruf `npm.cmd`.

### Externe Tools

| Tool | Zweck | Installation |
|------|-------|--------------|
| **Node.js / npm** | Dashboard-Frontend + Regal-Website | https://nodejs.org/ – unter Windows `npm.cmd` |
| **Pandoc** (>= 3.0) | EPUB-Export | `winget install --id JohnMacFarlane.Pandoc` oder manuell von https://pandoc.org/installing.html |
| **Playwright Chromium** | PDF-Export | `python -m playwright install chromium` nach `pip install -r requirements.txt` |
| **Higgsfield CLI** | Kapitel-/Szenenbilder | `npm install -g @higgsfield/cli`, Details in `docs/higgsfield-integration.md`. **Stand 2026-06-24:** Korrekte Moodboard-Laeufe setzen in der History `params.style_id`; die CLI bietet fuer `text2image_soul_v2` aber keinen `--style_id`-Parameter. `--custom_reference_id` ist dafuer nicht korrekt. |
| **Ollama** (optional) | Lokale LLM-Inference | https://ollama.ai/ - Modelle: `ollama pull gemma4:latest` (empfohlen), `ollama pull qwen3:8b` (optional) |
| **Streamlit** (>= 1.36) | Legacy-Dashboard | Enthalten in `requirements.txt` (nicht mehr Standardstart) |

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
    marketing/
    style-tests/
    legacy/
  exports/<style>/<chapter|book>/
  exports/<style>/book/print/   # KDP-Taschenbuch (interior/complete/wrap)
  exports/marketing/
  status/status.json
  status/logs/
```

Aktuelle Pakete (12):

- `books/peter-i-buch-01/`
- `books/anna-karenina/`
- `books/pharao/`
- `books/feuriger-engel/`
- `books/leben-arsenjews/`
- `books/aelita/`
- `books/geheime-geschichte-mongolen/`
- `books/die-dritte-chronik/`
- `books/kuprin-duell/`
- `books/kuprin-moloch/`
- `books/grin-wellenlaeuferin/`
- `books/pissemski-tausend-seelen/`

Die vier letzten Pakete sind Roh-Anlagen (09/2026, 0 % uebersetzt); Quelle,
Metadaten und Kapitelquellen stehen bereits.

Alte zentrale Dateien aus der vorherigen Struktur liegen unter
`config/legacy/`. Neue Tools lesen `books/*/book.yaml`, nicht mehr
`config/books.yaml`. Aktueller Arbeitsstand: `docs/HANDOVER.md`.

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
python -m pip install -r requirements.txt

# Dashboard (FastAPI + React)
python tools/start_dashboard.py
# oder Dev-Start.cmd / dev.cmd → http://127.0.0.1:8000

# Regal-Website (webpage/, nicht webapp/)
python tools/build_shelf_website.py
python tools/preview_webpage.py
# → http://127.0.0.1:4173

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
python tools/export_manuscript.py --book pharao --scope book --style stil-02-poetisch --format paperback
python tools/export_manuscript.py --book pharao --scope book --style stil-02-poetisch --format paperback-complete

# Review-Fixes aus vorhandenen Review-JSONs
python tools/apply_review_suggestions.py --book anna-karenina --style stil-01-original --plan
python tools/apply_review_suggestions.py --book anna-karenina --style stil-01-original --stage
python tools/apply_review_suggestions.py --book anna-karenina --style stil-01-original --promote

# Illustrationen (Kapitel-/Szenenbilder via Higgsfield)
python tools/generate_illustration.py --book pharao --chapter 001 --scene 01 --kind scene --style stil-02-poetisch
python tools/generate_illustration.py --book pharao --chapter 001 --kind chapter --style stil-02-poetisch
python tools/generate_illustration.py --book pharao --chapter 001 --scene 01 --kind scene --style stil-02-poetisch --overwrite
python tools/generate_illustration.py --book pharao --chapter 001 --scene 01 --kind scene --style stil-02-poetisch --dry-run

# Marketingpaket (erzeugt nichts oeffentlich; ohne --provider keine API-Kosten)
python tools/export_marketing.py --book peter-i-buch-01 --dry-run
python tools/export_marketing.py --book peter-i-buch-01
python tools/export_marketing.py --book peter-i-buch-01 --provider workspace_ai
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

Vor dem eigentlichen Export laeuft ein **Release-Gate**: der deterministische
Regelcheck (`--llm none`, kostenlos) prueft die Scope-Kapitel und bricht bei
ERROR > 0 mit Exit 2 ab. So kann keine Fassung mit kyrillischen Resten,
gemischten Tokens (`Pitschuга`), Mojibake (`Ã`/`Ð`/`Ñ`), akzentuierten
Transliterationsfehlern (`Golowín`) oder starker Raffung live gehen.

Raffung wird seit 2026-09-17 mit drei Signalen geprueft: `length_ratio`
(Extremfaelle), `paragraph_drop` (Absatzdefizit **plus** geschrumpfte
Wortzahl, pro Szene) und `length_outlier` (Szene relativ zum Buch-Median,
buchweit). Der buchweite Median-Check braucht mindestens 10 Szenen im
geprueften Scope - im Dashboard und per CLI also `--all` bzw. Scope
"Ganzes Buch" waehlen, sonst greift nur `paragraph_drop`.

```bash
# Release-Gate einzeln pruefen (Exit 2 bei ERROR>0)
python tools/review_manuscript.py --book peter-i-buch-01 --style stil-02-poetisch --all --llm none --fail-on-errors

# Export ohne Gate-Bypass (Standard)
python tools/export_manuscript.py --book peter-i-buch-01 --scope book --style stil-02-poetisch --format epub --allow-partial
```

Details, Ausnahmeliste fuer echte Originalzitate und die Reparatur ohne
Neuuebersetzung stehen in `AGENTS.md` (Abschnitt `Release-Gate`).

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

**Reihe und Bandnummer.** `book.series` und `book.series_volume` in
`export.yaml` gehen als EPUB-3-Collection-Metadaten ins OPF
(`belongs-to-collection`, `collection-type: series`, `group-position`) und
zusaetzlich ins Export-Manifest (`series`, `series_volume`); geschrieben wird
das in `add_epub_series_metadata()`. Damit ordnen Haendler wie KDP die Baende
einer Reihe zu. Im Buchtext wird bewusst **keine** Bandnummer gedruckt - siesteht im Covermotiv und wird dort beim Coverlauf gepflegt. Mehrabsaetze in
`summary`, `description` und `author_bio` gehoeren in einen literalen
YAML-Block (`|`), weil `>-` den Absatzabstand zu einem einfachen Zeilenumbruch
faltet und der Export dann nur einen Absatz sieht.

EPUB-Hinweis: Das Cover wird nur als offizielles EPUB-Cover ueber Pandoc
eingebunden. Die sichtbare Titelseite wird als robuste Pandoc-Div/Span-Struktur
mit CSS-Klassen erzeugt; dadurch vermeiden wir doppelte Coverseiten und
Reader-abhaengige Titel-Fragmente. Langtext-Frontmatter wie Zusammenfassung und
Autorenleben nutzt nur relative CSS-Groessen, damit Reader-Schriftgroessen
weiterhin vom Nutzer gesteuert werden koennen.

PDF-Hinweis: `--format pdf` bleibt die A5-Vorschau (Playwright/Chromium,
`book-print.css`). Das druckfertige KDP-Innenleben ist `--format paperback`.
Trim und Satzprofil sind unabhaengig waehlbar (kein Auto-Wechsel nach
Seitenzahl). Default bleibt 5,5×8,5 Zoll / `classic` (EB Garamond 10,8/13,6 pt).

```bat
:: 5.5 x 8.5, classic, Kapitelbilder eigene Seite
py -3 tools/export_manuscript.py --book pharao --scope book --style stil-02-poetisch --format paperback --trim-size 5.5x8.5 --layout-profile classic --illustration-mode full_page

:: 6 x 9, gleicher Satz wie oben (nur Format wechselt)
py -3 tools/export_manuscript.py --book pharao --scope book --style stil-02-poetisch --format paperback --trim-size 6x9 --layout-profile classic --illustration-mode full_page

:: 6 x 9, long_classic (10,2/12,5 pt), Bilder inline (oben, Text darunter)
py -3 tools/export_manuscript.py --book pharao --scope book --style stil-02-poetisch --format paperback --trim-size 6x9 --layout-profile long_classic --illustration-mode inline

:: Kopfvignette: Kapiteltitel, Bild darunter (62 % Breite), Text laeuft sofort weiter
py -3 tools/export_manuscript.py --book die-sprache-des-anderen --scope book --style stil-01-original --format paperback --illustration-mode chapter_head
```

Bildmodi im Druck: `full_page` (Bild auf eigener Seite, +1 Seite je Kapitel),
`inline` (Bild oben auf der Kapitelseite, Titel rutscht darunter) und
`chapter_head` (Titel zuerst, Bild als Vignette darunter, Text fliesst direkt
weiter). `chapter_head` spart bei `die-sprache-des-anderen` 17 Seiten
gegenueber `full_page` und haelt die Bilder durch die schmalere Darstellung
ueber 300 dpi.

`--format paperback-complete` liefert Innenleben plus Rueckseite, Reihenkatalog
und – wenn `assets/covers/cover-print.jpg` oder `.png` existiert – Vorderseite
und Wrap-PDF (Rueckenbreite creme/SW = Seitenzahl × 0,0635 mm). Fehlt das
Druckcover, entsteht das Komplett-PDF ohne Coverbild. Ausgabe unter
`exports/<style>/book/print/`; Dateiname enthaelt Trim/Profil/Bilder
(`…-55x85-classic-full-…-paperback-interior.pdf`). Print-Report:
`*-print-report.json` (Seitenzahl, `kdp_max_pages`, Cream=776, White=828).
Ohne neue Flags gilt `config/print.yaml` (5.5x8.5 / classic / full_page / cream).
`--format all` bleibt DOCX+EPUB.

Drei Print-PDFs (nicht verwechseln):

| Datei | Was es ist |
|---|---|
| `*-paperback-interior.pdf` | Buchinhalt fuer KDP (ohne Cover) - **das ist die Upload-Datei** |
| `*-paperback-complete.pdf` | Zum Blaettern: Coverseite, Text, Rueckseite - **nicht hochladen** |
| `*-paperback-wrap.pdf` | Umschlag **als eine Flaeche** (Rueckseite \| Ruecken \| Vorderseite) fuer den KDP-Cover-Upload |

### Inhaltsverzeichnis: Kapitel oder Gruppen

`front_matter.toc_depth` steuert, was das Inhaltsverzeichnis listet:

| Wert | Wirkung |
| --- | --- |
| `chapters` (Default) | Jedes Kapitel mit Link (bisheriges Verhalten) |
| `groups` | Nur die Gruppen aus `book.yaml` `structure.groups` (z. B. Buch I-III) |

`groups` ist fuer Buecher mit vielen durchgezaehlten Kapiteln gedacht: Bei
`pharao` hiessen 69 Eintraege "Erstes Kapitel" bis "Neunundsechzigstes
Kapitel" - in einer Liste sagt das nichts, und KDP beanstandet die vielen
Markierungen. Mit `toc_depth: groups` steht dort nur noch `Buch I`, `Buch II`,
`Buch III`, verlinkt auf die Gruppenanfaenge; der Satz wurde dadurch zwei
Seiten kuerzer. Gilt fuer PDF/EPUB und DOCX. Die Kapitel selbst behalten ihre
Ueberschriften und Anker.

### KDP-Covergroessen nachrechnen

KDP meldet Abweichungen als zwei Zahlen, z. B.
*"Die erwartete Covergroesse betraegt 13.080x9.250, die eingereichte
Dateigroesse jedoch 12.070x8.750."* Trim und Seitenzahl stehen da nicht drin -
man rechnet sie zurueck:

```text
Hoehe:     Coverhoehe − 2 x 0,125 in Beschnitt                = Trimhoehe
Breite:    Coverbreite − 2 x Trim − 2 x 0,125 in Beschnitt    = Ruecken
Seiten:    Ruecken (in) / 0,025 in  (= 0,0635 mm Creme/SW)

Breite  = 2 x Trim + Ruecken + 2 x 0,125 in
Hoehe   = Trim + 2 x 0,125 in
```

Beispiel: 13,080 x 9,250 in -> Hoehe 9,00 in (Trim 6 x 9), Breite
13,08 − 12 − 0,25 = 0,83 in Ruecken = 332 Seiten.

Haeufigste Ursachen fuer die Meldung:

1. **`*-paperback-complete.pdf` hochgeladen** statt `*-paperback-interior.pdf`.
   Die Komplettdatei hat zwei Umschlagseiten mehr (332 statt 330), KDP erwartet
   dann einen breiteren Ruecken.
2. **Trim im Assistenten** passt nicht zum Satz (6x9 statt 5,5x8,5 usw.).

Nur den Umschlag bauen, ohne den Satz neu zu rendern:

```bash
python tools/build_cover.py --book die-sprache-des-anderen --page-count 332 --trim-size 6x9
python tools/build_cover.py --book die-sprache-des-anderen --page-count 330 --trim-size 5.5x8.5 --dry-run
```

Das Werkzeug rechnet Ruecken und Zielgroesse aus Trim, Papier und Seitenzahl,
rendert den Wrap nach `exports/<style>/book/print/cover-wrap-<stempel>-<seiten>.pdf`
und prueft die Ausgabegroesse gegen die Rechnung (Exit 1 bei Abweichung).
Report daneben: `*-report.json`.

**Nach jedem Satzlauf den Wrap neu bauen** - der Ruecken haengt an der
Innenseitenzahl, und die haengt an Trim und Bildmodus (`chapter_head` spart bei
diesem Buch 17 Seiten gegenueber `full_page`).

### Schriften im Print-PDF

KDP verlangt eingebettete Schriften; die Meldung *"Die Schriftarten wurden nicht
ordnungsgemäß eingebettet"* hatte zwei Ursachen, beide behoben:

- **Variable Fonts.** `EBGaramond*.ttf` sind variabel (`fvar`/`gvar`); Chromium
  bettet sie nicht als TrueType ein, sondern zeichnet Type3-Pfade. In
  `config/print.yaml` stehen deshalb die statischen Instanzen
  `EBGaramond-Regular-static.ttf` / `EBGaramond-Italic-static.ttf`
  (erzeugt mit `fontTools.varLib.instancer`, `wght=400`).
- **Folios.** Chromium setzt keine Seitenzahlen; sie kamen aus einem
  Helvetica-Overlay (base-14, nicht eingebettet). `_folios_overlay_pdf()` in
  `lib/print_pdf.py` rendert jetzt alle Seitenzahlen in einem Chromium-Durchlauf
  mit der Hausschrift als ein Overlay-PDF.

Pruefbefehl nach einem Satzlauf (erwartet: nur EBGaramond, jeweils eingebettet):

```bash
python -c "from pypdf import PdfReader; r=PdfReader('...interior.pdf'); fd=(r.pages[20].get('/Resources') or {}).get('/Font') or {}; print([(str(f.get_object().get('/BaseFont')), str(f.get_object().get('/Subtype'))) for f in fd.values()])"
```

Druck-Vorderseite: manuell `books/<id>/assets/covers/cover-print.jpg` oder `.png`.
Kein Fallback auf das Kindle-`cover.jpg`. Fehlt `cover-print`, entsteht das
Komplett-PDF ohne Coverbild, der Wrap entfaellt.

Reihenkatalog (andere Motivatier-Classics) haengt EPUB und Paperback an.
Abschalten pro Buch: `website.catalog: false` in `export.yaml`.

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
Fuer den Taschenbuch-Umschlag zusaetzlich (optional, manuell)
`cover-print.jpg` / `cover-print.png` im selben Ordner.

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

Der Prompt an Higgsfield wird aus der **Vignette** des Kapitels gebaut
(`work/prompts/higgsfield/vignettes/<kapitel>.json`) und hat vier Teile:

1. **Moment** – eine Handlung mit Person und Ort.
2. **Figuren** – nur wer in diesem Moment anwesend ist, mit Handlung und
   Aussehen (aus der Vignette, sonst `names.yaml`).
3. **Gegenstaende und Bildausschnitt.**
4. **Stilanker** – `illustration_setting` (Stil, Licht, Palette, Stimmung,
   max. 700 Zeichen) und `illustration_world` (Material/Epoche, max. 400
   Zeichen). Ein Ortskatalog gehoert dort nicht hinein.

Den Moment waehlt `--vignette-provider openrouter` (LLM, Bruchteile eines
Cents pro Kapitel), `none` (kostenfreie Heuristik) oder `auto` (vorhandene
Vignette, sonst Heuristik). `off` baut den bisherigen Prompt aus
`illustration_setting` plus den ersten zwei Absaetzen. Default steht in
`book.yaml` unter `higgsfield.vignette.provider`.

Bestehende Bilder werden nur mit `--overwrite` ersetzt; `--dry-run` zeigt den
Prompt ohne API-Call an und schreibt `*-dryrun.md`/`.json`, ohne den echten
Prompt zu ueberschreiben. Details: `docs/higgsfield-integration.md`.

Ausgaben landen unter:

```text
books/<book-id>/exports/<style>/chapter/docx/
books/<book-id>/exports/<style>/chapter/epub/
books/<book-id>/exports/<style>/chapter/pdf/
books/<book-id>/exports/<style>/book/docx/
books/<book-id>/exports/<style>/book/epub/
books/<book-id>/exports/<style>/book/pdf/
books/<book-id>/exports/marketing/        # Marketingpaket (campaign.json, posts.md, youtube.md, media.json, README.md, clips/)
```

## Marketingexport

`tools/export_marketing.py` erzeugt aus den vorhandenen Buchdaten ein
Marketingpaket: X-Beitraege, YouTube-Materialien (Liedvideo, zwei Shorts,
Shotlists) und ein maschinenlesbares Kampagnenmanifest. Es wird **nichts
veroeffentlicht**; eine Anbindung an X, YouTube oder Postiz gibt es bewusst
nicht.

```text
books/<book-id>/
  work/marketing/generated.json          # KI-/Repository-KI-Texte + Herkunft
  work/marketing/overrides/<post-id>.md  # manuelle Fassung (hat Vorrang)
  exports/marketing/campaign.json        # Manifest fuer die spaetere Uebergabe
  exports/marketing/posts.md             # X-Beitraege
  exports/marketing/youtube.md           # Liedvideo + Shorts
  exports/marketing/media.json           # Medien, repo-relative Pfade
  exports/marketing/README.md            # offene Angaben und Pflegeanleitung
```

Buchlokale Angaben stehen als top-level `marketing:`-Block in `export.yaml`:
Amazon-Link (`website.amazon_url` oder `marketing.amazon_url`),
`campaign_start`, `youtube.{url,video_id,public}`, `songs[]` und optionale
Bildzuordnungen `media{}`. Marke, Shelf-URL, Zeitplan und alle Plattformlimits
stehen in `config/marketing.yaml`.

Ein Standardlauf ohne `--provider` kostet nichts: Vorhandene Texte werden
wiederverwendet. Neu erzeugt wird nur bei geaenderten Quelldaten, geaenderter
`prompt_version` oder ausdruecklichem `--regenerate`. Fehlende Marketingdaten
blockieren den EPUB-Export nicht.

X kann keine reinen Audiodateien abspielen: `tools/render_x_clip.py` rendert
aus Cover + Song einen quadratischen MP4-Clip (`exports/marketing/clips/`,
H.264/AAC, braucht System-ffmpeg) – auch als Hintergrundjob aus der
Dashboard-Sektion **X-Clip** auf der Export-Seite.

Details: `docs/marketing-export.md`.

### A+ Content (KDP)

`tools/aplus_build.py` bereitet den A+-Content der Produktseite vor. Amazon
hat dafuer **keine API** – der Content-Manager ist ein Webformular –, deshalb
erzeugt das Werkzeug nur die Zutaten: einen Modulplan mit Zielmassen, die
zugeschnittenen Bilder und die Texte zum Einfuegen.

```text
books/<book-id>/work/aplus/
  modules.json      # Module, Texte, Bilddateien, Masse, Zeichenzaehlung
  copy.md           # Copy-Paste-Fassung, Modul fuer Modul
  assets/*.jpg      # 970x600 (Kopfmodul), 3x 300x300 (Dreibild-Modul)
```

```bash
python tools/aplus_build.py --book die-sprache-des-anderen
python tools/aplus_build.py --book die-sprache-des-anderen --dry-run
```

Texte kommen aus `book.title`, `book.description` (Absatz 1 und 2) und
`book.summary`; fehlende Ueberschriften stehen als `TODO` im Plan, es wird
nichts erfunden. Bildquellen sind die Kapitelvignetten, gleichmaessig
verteilt; `--images a.jpg b.jpg ...` waehlt eigene. Ein Logo-Modul wird
uebersprungen, solange `assets/covers/logo.png` fehlt. Die Masse folgen den
Amazon-Standardmodulen, stehen aber im Plan – vor dem Upload gegen die
aktuelle Vorgabe pruefen.

**Begleiteter Fahrer.** `tools/aplus_drive.py` bedient das Formular, aber nie
blind: erst Schnappschuss, dann Plan mit Pruefsummen, dann Ausfuehrung mit
Journal.

```bash
python tools/aplus_drive.py login                    # einmalig, Sitzung nach .kdp-session/
python tools/aplus_drive.py snapshot --url <A+-Seite>
python tools/aplus_drive.py plan --actions actions.json --out plan.json
python tools/aplus_drive.py execute --plan plan.json --journal journal.jsonl
```

Regeln im Code, nicht in der Disziplin: nur Amazon-Hosts als Ziel,
Passwort-/Steuer-/Bank-/Kontaktfelder werden nie gefuellt, Uploads muessen
dieselbe SHA-256 haben wie beim Planen, Klicks auf Speichern oder
Veroeffentlichen brauchen `--allow-submit`, und jede Aktion landet als JSONL
im Journal (ohne Werte sensibler Felder).

```json
{
  "url": "https://kdp.amazon.com/...",
  "steps": [
    {"action": "fill", "label": "Headline", "value": "Die Sprache des Anderen"},
    {"action": "upload", "label": "Bild 1", "path": "books/<id>/work/aplus/assets/hero-hero-970x600.jpg"},
    {"action": "click", "label": "Speichern"}
  ]
}
```

## Lokaler Start unter Windows

Doppelklick auf `dev.cmd` im Repository-Root startet das Dashboard ohne IDE.
Alternativ im Terminal aus dem Repo-Root:

```bat
dev.cmd
```

Voraussetzungen: Python 3 und Node.js/npm im `PATH`, optional eine lokale
`.env` (wird bei Bedarf aus `.env.example` kopiert; `OPENROUTER_API_KEY`
eintragen fuer OpenRouter-Jobs). `dev.cmd` installiert fehlende Python-
bzw. Frontend-Abhaengigkeiten nur bei Bedarf und ruft danach
`python tools/start_dashboard.py` auf.

Gestartet wird ein Prozess: FastAPI + gebautes React-Frontend auf
`http://127.0.0.1:8000` (Browser oeffnet sich nach kurzer Wartezeit).
Beenden mit `Ctrl+C` im Terminalfenster von `dev.cmd`.

## Dashboard

Start:

```bash
python tools/start_dashboard.py
```

URL: `http://127.0.0.1:8000`

Das Dashboard liest Buchpakete aus `books/*/book.yaml`. Es bietet Uebersicht,
Buchsetup, Uebersetzen, Stiltest, Review, Export (inkl. Karte
**Marketingpaket**), Higgsfield/Bilder, Namen, Logs und **Website**
(Regal-Freigabe, Katalog-/Dist-Jobs). Die verbindliche Optik-Referenz liegt in
`docs/dashboard-design-system.md`. Die oeffentliche Regal-Website selbst liegt
unter `webpage/` (siehe `webpage/README.md`).

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
