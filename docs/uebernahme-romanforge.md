# Uebernahme aus RomanForge (Stufe 1)

Stand: 2026-10-08 (Stufe 1c: `neu`-Kapitel per Exportposition, Paketgrenze im
Werkzeug; Stufe 1b: `--new` fertig, importiert alle Kapitel, legt
`status.json` an, nutzt die neutrale Vorlage aus `tools/init_book.py`).
Werkzeug: `tools/import_markdown_original.py`.
Tests: `tests/test_import_markdown_original.py` (41 Tests, echte
Chronik-Daten, gruen). Plan: `docs/plan-uebernahme-romanforge.md`
(bleibt fuehrend fuer Stufen 2–4; diese Datei beschreibt nur den Ablauf).

Der Ablauf hat zwei Modi:

- **NEU** - das Buch ist in peter noch unbekannt (neues Buchpaket).
- **AKTUALISIEREN** - das Buch existiert bereits (Abgleich + Uebernahme).

Passt der Modus nicht zum Stand in peter (NEU, aber das Buch existiert;
AKTUALISIEREN, aber das Buch fehlt): **anhalten und fragen**.

## Grundsatz

- Getrennt lassen, kein Zusammenlegen. Inhaltliches in RomanForge,
  Formales in peter. Konflikte nur anzeigen, nie automatisch fuehren.
- Neufassungen nur ueber den RomanForge-Export. Die Ablage
  `status/<Titel> - NN ….md` ist ersetzt. `status/status.json` und
  `status/logs/` bleiben unveraendert (pflegen weiter die CLIs).
- Massgeblich: `work/scenes/de/<style>/NNN/scene-01.md`.
- Nie still ueberschreiben: nur per `--accept` freigegebene Kapitel.
- `--keep` ist **kein Modus**, sondern eine Entscheidung innerhalb von
  AKTUALISIEREN: den Konflikt zugunsten von peter aufloesen (peter-Text
  bleibt, wird als „noch nicht in RomanForge" markiert).
- Keine kostenpflichtigen Aufrufe. Windows: `py -3`.
- `books/*/source/` wird nie beschrieben (ausser `--new`-Erstkopie).
- `tools/import_die_dritte_chronik.py` bleibt liegen (Entfernung nur nach
  Rueckfrage).

## NEU (Buch in peter unbekannt)

```bash
py -3 tools/import_markdown_original.py --new --source <export.md> \
    --title <Titel> --author <Autor> \
    [--id <id>] [--subtitle <u>] [--series <r>] [--publisher <v>]
py -3 tools/import_markdown_original.py --new --handoff <id> \
    --title <Titel> --author <Autor> \
    [--id <id>] [--subtitle <u>] [--series <r>] [--publisher <v>]
```

- `--title` und `--author` sind Pflicht. `--id` wird aus dem Titel
  abgeleitet, wenn nicht angegeben. Ist `--title` nicht angegeben, meldet
  das Werkzeug die erste `# `-Zeile des Exports als **Vorschlag** und
  bricht ab (nichts wird still uebernommen). Existiert das Buchpaket
  bereits, Abbruch (Exit 2).
- Der Lauf importiert **alle** Kapitel in einem Durchgang (drei Textkopien
  je Kapitel wie bei `--accept`), archiviert
  `work/imports/romanforge/runs/<stempel>/{export.md,report.md}` und
  schreibt die vollstaendige `state.yaml` (`rf_base = peter_base = Hash des
  Exports`, alle Kapitel) sowie `status/status.json` (alle Kapitel, Status
  `done`). Danach funktioniert `--compare` ohne `--baseline`.
- `book.yaml` und `export.yaml` entstehen aus der **neutralen** Vorlage von
  `tools/init_book.py` (`build_book_yaml`/`build_export_yaml`) - kein
  Kopieren aus einem anderen Buch. Kein `website:`/`marketing:`-Block.
  Buchspezifische Texte (rights, translator/translator_label,
  original_title, original_author, title_page_extra, Zusammenfassung,
  Autorenleben) bleiben leer; der Lauf listet sie als „offen".
- **Stufe 1:** Das Markdown-Export enthaelt **kein Exposé**. Nach
  Zusammenfassung/Klappentext wird nur **gefragt**, nichts erfunden.
- Am Ende gibt der Lauf die Folgebefehle aus:

```bash
py -3 tools/assemble_chapter.py --book <id> --all --style <style>
py -3 tools/review_manuscript.py --book <id> --style <style> --all --llm none
```

Der `--book-root <pfad>`-Schalter legt das Paket an einem freien Pfad an
(nur fuer Tests; schreibt nie ins echte `books/`).

## AKTUALISIEREN (Buch existiert)

### Ausgangsstand (Baseline)

- Ohne `state.yaml` ist `--baseline <ursprungs-export>` Pflicht, sonst
  Abbruch (Exit 2). Kein stilles Zurueckfallen auf `source_path`.
- `source/…` gilt NICHT als Uebernahmestand (Chronik: per 15566c0 an die
  Redaktion angeglichen). Ausgangsstand Chronik:
  `git show 150f0c1:"books/die-dritte-chronik/source/Die dritte Chronik.md"`.
- Zustand: `work/imports/romanforge/state.yaml` pro Kapitel
  `title/rf_base/peter_base/base_export`. Nur `--accept`/`--keep`
  schreiben neu. Schreiblauf archiviert `runs/<stempel>/export.md`
  (roh, byte-identisch) + `report.md`.
- **Erstlauf (Option B, 2026-10-07):** Der erste schreibende Lauf
  (`--accept`/`--keep`) legt `state.yaml` fuer **alle** Kapitel an:
  unberuehrte Kapitel mit `rf_base = peter_base = Hash aus --baseline`,
  bearbeitete mit den neuen Werten. Danach ist `--baseline` nicht mehr
  noetig. Wird `--baseline` bei vorhandener `state.yaml` uebergeben,
  kommt der Hinweis, dass sie ignoriert wird (Ausgangsstand = `state.yaml`).
- Fehlt ein Kapitel in `state.yaml` (z. B. im Export neu hinzugekommen),
  bekommt es die Einstufung `ohne-ausgangsstand` (Exit 2), **nicht**
  `konflikt`. Aufloesen: mit `--baseline` erneut laufen. Nie eine leere
  Baseline als Wert.

### Befehle

```bash
py -3 tools/import_markdown_original.py --book <id> --source <export.md> --baseline <ursprung.md> --dry-run
py -3 tools/import_markdown_original.py --book <id> --source <export.md> --baseline <ursprung.md> --compare
py -3 tools/import_markdown_original.py --book <id> --source <export.md> --accept 008,012
py -3 tools/import_markdown_original.py --book <id> --source <export.md> --keep 008
```

- `--dry-run`/`--compare`: nur stdout, schreiben nichts. Exit 2 bei
  Konflikt/neu/entfallen (Bericht trotzdem vollstaendig).
- Nach `--accept`: pro Kapitel
  `assemble_chapter.py --book <id> --chapter NNN --style <stil>` +
  `review_manuscript --book <id> --style <stil> --chapter NNN --llm none`.

### Einstufungen

nichts / uebernahme-vorgeschlagen / peter-behalten / konflikt / neu /
entfallen / ohne-ausgangsstand. `neu`+`entfallen` an gleicher Position heisst
`vermutlich umbenannt` (nur Hinweis, kein Auto-Merge). Die Erkennung
(`find_presumed_renames`, Stufe 1 Schritt 3) ergaenzt genau diesen
Hinweis in der Berichtsspalte „Hinweis" der beiden betroffenen Zeilen;
Einstufung und Exit-Code (2 bei neu/entfallen) bleiben unveraendert.

### Neue Kapitel im Export (`neu`, ergaenzt 2026-10-08)

Ein Exportkapitel ohne peter-Entsprechung hat in peter noch keine ID. Es wird
ueber seine **Exportposition** freigegeben (1-basierte Reihenfolge im Export):

```bash
py -3 tools/import_markdown_original.py --book <id> --source <export.md> --accept 019
```

- Angelegt werden `work/chapters/NNN-source.md`, `work/scenes/de/NNN/scene-01.md`
  und `work/scenes/de/<style>/NNN/scene-01.md` (wie bei jedem `--accept`) plus
  ein `state.yaml`-Eintrag mit `rf_base = peter_base = Export-Hash`.
- `--keep` ist fuer `neu` nicht moeglich (kein peter-Text vorhanden, Exit 2).
- Kollidiert eine Exportposition mit einer vorhandenen Kapitel-ID, gewinnt die
  vorhandene ID; das Werkzeug meldet die Mehrdeutigkeit auf stderr.
- Paketgrenze jetzt im Werkzeug: hoechstens **5** Kapitel pro Lauf
  (`--accept`/`--keep` zusammen), sonst Exit 2 ohne Schreibzugriff.
- Danach wie ueblich pro Kapitel `assemble_chapter.py` +
  `review_manuscript --chapter NNN --llm none`.
- `status/status.json` wird auch hier nicht angefasst; `review --all` und das
  Dashboard finden die neuen Kapitel ueber `work/chapters/` und die Szenenordner
  (`workbench_state.chapter_ids`).

## Arbeitsweise der KI (verbindlich)

- Kontext sparen: Kapiteltexte, Dateien, Diffs NICHT in den Kontext holen.
  Vergleich nur ueber das Werkzeug; es gibt die kompakte Tabelle aus
  (Nummer, Titel, Woerter RomanForge/peter, Einstufung, Hinweis).
- Ursprungs-Export per `git show … --output=$TEMP/…` binär umleiten,
  ohne ihn anzuzeigen.
- Textansicht nur im Notfall: max. 3–5 Kapitel, nur erste ~5 Zeilen,
  dann Befund + warten.
- Kleine Schritte: ein Schritt, Kurzbericht (≤ 15 Zeilen), naechster.
- Pakete ≤ 5 Kapitel: `--accept` fuers Paket, Folgebefehle fuers Paket,
  Kurzbericht, naechstes Paket.
- Vom Review nur Zusammenfassung (ERROR/WARNING/INFO pro Kapitel),
  keine Einzelbefunde (ausser auf Nachfrage).

## Abnahme 2026-10 (Chronik, 48 Kapitel)

- a) `--compare --source <ursprung> --baseline <ursprung>`: 48/48
  RF-unveraendert, peter-geaendert genau 008, 009, 012, 018, 025, 026,
  031, 033, 034, 035, 036, 041, 043; Rest nichts; 0 Konflikte.
- b) `--compare --source books/…/Die dritte Chronik.md --baseline <ursprung>`:
  Konflikt 012, 018, 026, 031, 033, 034, 035, 036, 041, 043;
  peter-behalten 008, 009, 025; Rest nichts.

## Stufe 2 (RomanForge-API) – implementiert

- **`--handoff <id>`** ist als Alternative zu `--source` verfuegbar (fuer NEU und AKTUALISIEREN).
- `tools/lib/romanforge_client.py` liest `ROMANFORGE_URL`/`ROMANFORGE_API_KEY` aus `.env` und fragt den Endpunkt `/api/handoffs/{id}` ab. Die API liefert die vollen Uebergabe-Daten (Metadaten, `publication`-Block, alle Kapitel mit Content, `expose`-Feld); es gibt keinen separaten Export-Endpunkt. `download_export` baut den Markdown-Export aus den Kapiteln der API-Antwort auf.
- `rf_id` (aus `chapter.id` der API) wird pro Kapitel in `state.yaml` gespeichert; `match_chapters` priorisiert ID vor Titel.
- Verlagsangaben stammen aus dem `publication`-Block der API: `author_name`, `publisher`, `series_name`, `series_number`, `subtitle` (kann `null` sein -> bleibt leer). Fehlende Angaben werden erfragt, nicht erfunden.
- **NEU:** `--new --handoff <id> --title <Titel> --author <Autor> [--publisher <v>] [--series <r>]` importiert alle Kapitel in einem Lauf, speichert `rf_id` pro Kapitel und schreibt `state.yaml` + `status/status.json`.
- **AKTUALISIEREN:** `--handoff <id>` lädt die aktuelle Übergabe vom Server; danach gilt der normale `--compare`/`--accept`/`--keep`-Ablauf (max. 5 Kapitel pro Paket).

## Uebergabe-Prompt

Ein Prompt fuer beide Faelle. Ab Stufe 2 fuellt RomanForge ihn aus; in
Stufe 1 wird er von Hand ausgefuellt (unbekannte Felder leer lassen).
Regeln und Einzelschritte stehen in dieser Datei, nicht im Prompt.

```text
Uebergabe aus RomanForge an peter-the-one

Lies AGENTS.md und docs/uebernahme-romanforge.md und folge dem Ablauf dort.

Modus: {NEU | AKTUALISIEREN}
Buch: {Titel} · {Genre} · {Kapitel} Kapitel · ca. {Woerter} Woerter
peter-Buch-ID: {id, falls bekannt}
RomanForge: {Instanz} · Projekt {ID} · Export/Uebergabe {ID} vom {Zeitpunkt}
Laut RomanForge seit der letzten Uebergabe geaendert: {Kapitelliste | erste Uebergabe}

Quelle: {Stufe 1: Frag mich nach dem Pfad der Exportdatei. | Stufe 2: --handoff {ID}}

NEU: Verlagsangaben aus der Uebergabe vorschlagen (ab Stufe 2), fehlende erfragen
(Autor/Pseudonym, Untertitel, Reihe, Verlag). Dann Buchpaket anlegen,
alle Kapitel in einem Lauf importieren, Gate ohne KI, Kurzbericht.
AKTUALISIEREN: Vergleich, nur die Tabelle zeigen. Uebernahmen (--accept) und Konfliktloesungen
(--keep) nur nach meiner Freigabe, hoechstens 5 Kapitel pro Paket.
Passt der Modus nicht zum Stand in peter (NEU, aber Buch existiert; AKTUALISIEREN, aber Buch fehlt):
anhalten und fragen.

Arbeitsweise: Vergleiche nur ueber tools/import_markdown_original.py, du liest nur dessen Tabelle,
keine Kapiteltexte. Keine Uebersetzung, keine Bilder, nichts ueberschreiben ohne meine Freigabe.
```

Hinweis zu den Begriffen: `--keep` ist kein Modus, sondern eine Entscheidung
innerhalb von AKTUALISIEREN (Konflikt zugunsten von peter aufloesen).
