# React-Dashboard Paritaetscheckliste

Ziel: Das neue FastAPI/React-Dashboard ersetzt Streamlit erst, wenn die
produktiven Workflows aus `tools/dashboard.py` abgedeckt sind. Diese Liste ist
die Abarbeitungsgrundlage.

## Statusmatrix

| Bereich | Streamlit | React/FastAPI | Status | Akzeptanz fuer Paritaet |
|---|---|---|---|---|
| Uebersicht | vorhanden | vorhanden | erledigt | Buchstatus, Kapitelstatus und Jobs sind sichtbar. |
| Uebersetzen | vorhanden | vorhanden | erster produktiver Slice | Kapitel/Bereich/Missing, Provider, Modell, Chunk, Overwrite und Assemble-after starten echte Jobs. |
| Review | vorhanden | vorhanden | erledigt | Planen, Starten, Reports lesen und Review-Fixes plan/stage/promote sind in React nutzbar. |
| Export | vorhanden | vorhanden | erledigt | Kapitel/Buch, Format und Allow-partial starten echte Jobs; Vorpruefung, Kommando-Planung und letzte Dateien sind sichtbar. |
| Namen | vorhanden, editierbar | vorhanden | erledigt | Namen koennen hinzugefuegt, bearbeitet, geloescht und validiert gespeichert werden. |
| Stiltest | vorhanden | vorhanden | erledigt | Stiltest-Kontext, Prompt/Start, Zeichenzaehlung und Markdown-Leseansicht sind portiert. |
| Buch-Setup | vorhanden | vorhanden | erledigt | Neues Buch kann geplant, angelegt und initial extrahiert werden. |
| Logs | vorhanden | vorhanden | erster Slice | Dashboard- und Buchlogs sind lesend sichtbar; Copy/Download spaeter. |
| Higgsfield/Bilder | CLI vorhanden | vorhanden | erster produktiver Slice | Kapitel-/Szenenbilder koennen fuer Kapitelbereiche als Job geplant und gestartet werden. |
| Umschalten | Streamlit Backup | React/FastAPI primaer | erledigt | Vite-Build wird ueber FastAPI ausgeliefert; ein Startbefehl reicht lokal. |

## Abarbeitungsreihenfolge

- [x] Review vervollstaendigen: Reports, Summary, Review-Fixes.
- [x] Namen editierbar machen: `PUT /api/books/{book_id}/names`, React-Editor.
- [x] Higgsfield/Bilder vorbereiten: Batch-CLI, API-Action, React-Workflow.
- [x] Stiltest portieren.
- [x] Buch-Setup portieren.
- [x] Export abrunden: letzte Exportdateien und Fehler vor Jobstart.
- [x] Umschaltreife: statische Auslieferung, Startskript, Doku.
- [x] Buch-Settings mit explizitem Speichern in `book.yaml`.
- [x] Stiltest-Markdownanzeige fuer Zitate/Nebenabsatz-Zeilen.

## Higgsfield-Schnitt

Der Moodboard-`style_id`-Fix blockiert die Oberflaeche nicht. Der Workflow
nutzt zunaechst die bestehende CLI-Funktionalitaet und reicht Backend,
Dry-run, Overwrite, Modell, Qualitaet, Seitenverhaeltnis und Referenzoptionen
durch.

Akzeptanz:

- Kapitelbild fuer ein Kapitel starten.
- Szenenbilder fuer ein Kapitel starten.
- Kapitelbereich `von` bis `bis` starten.
- `--missing` ueberspringt vorhandene Bilder ohne destruktive Operation.
- `--dry-run` schreibt nur Prompts/Metadaten und erzeugt keine Bilder.
- Job erscheint im globalen Job-Panel.
