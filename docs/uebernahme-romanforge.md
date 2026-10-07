# Uebernahme aus RomanForge (Stufe 1)

Stand: 2026-10-07. Werkzeug: `tools/import_markdown_original.py`.
Tests: `tests/test_import_markdown_original.py` (31 Tests, alle auf echten
Chronik-Daten, gruen). Plan: `docs/plan-uebernahme-romanforge.md`
(bleibt fuehrend fuer Stufen 2–4; diese Datei beschreibt nur den Ablauf).

## Grundsatz

- Getrennt lassen, kein Zusammenlegen. Inhaltliches in RomanForge,
  Formales in peter. Konflikte nur anzeigen, nie automatisch fuehren.
- Neufassungen nur ueber den RomanForge-Export. Die Ablage
  `status/<Titel> - NN ….md` ist ersetzt. `status/status.json` und
  `status/logs/` bleiben unveraendert (pflegen weiter die CLIs).
- Massgeblich: `work/scenes/de/<style>/NNN/scene-01.md`.
- Nie still ueberschreiben: nur per `--accept` freigegebene Kapitel.
- Keine kostenpflichtigen Aufrufe. Windows: `py -3`.
- `books/*/source/` wird nie beschrieben (ausser `--new`-Erstkopie).
- `tools/import_die_dritte_chronik.py` bleibt liegen (Entfernung nur nach
  Rueckfrage).

## Ausgangsstand (Baseline)

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

## Befehle

```bash
py -3 tools/import_markdown_original.py --book <id> --source <export.md> --baseline <ursprung.md> --dry-run
py -3 tools/import_markdown_original.py --book <id> --source <export.md> --baseline <ursprung.md> --compare
py -3 tools/import_markdown_original.py --book <id> --source <export.md> --accept 008,012
py -3 tools/import_markdown_original.py --book <id> --source <export.md> --keep 008
py -3 tools/import_markdown_original.py --new --id <id> --title <t> --author <a> [--subtitle --series --publisher] --source <export.md>
```

- `--dry-run`/`--compare`: nur stdout, schreiben nichts. Exit 2 bei
  Konflikt/neu/entfallen (Bericht trotzdem vollstaendig).
- Nach `--accept`: pro Kapitel
  `assemble_chapter.py --book <id> --chapter NNN --style <stil>` +
  `review_manuscript --book <id> --style <stil> --chapter NNN --llm none`.

## Einstufungen

nichts / uebernahme-vorgeschlagen / peter-behalten / konflikt / neu /
entfallen / ohne-ausgangsstand. `neu`+`entfallen` an gleicher Position heisst
`vermutlich umbenannt` (nur Hinweis, kein Auto-Merge). Die Erkennung
(`find_presumed_renames`, Stufe 1 Schritt 3) ergaenzt genau diesen
Hinweis in der Berichtsspalte „Hinweis" der beiden betroffenen Zeilen;
Einstufung und Exit-Code (2 bei neu/entfallen) bleiben unveraendert.

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

## Offen fuer Stufe 2 (RomanForge-API)

Interne Kapitelliste um optionale `rf_id` erweitern, `match_chapters`
ID vor Titel, `state.yaml` speichert `rf_id` pro Kapitel. Spec:
`E:\code\NovelWriter\docs\plan-uebergabe-peter.md` Abschnitt 5+8;
spaeter `--handoff <id>` mit `ROMANFORGE_URL`/`ROMANFORGE_API_KEY` (.env).

## Uebergabe-Prompt

```text
Uebergabe aus RomanForge an peter-the-one

Ich habe in RomanForge ein Manuskript exportiert und moechte es in die Produktion uebernehmen.
Lies AGENTS.md und docs/uebernahme-romanforge.md und folge dem Ablauf dort.

Buch: {Titel} · {Genre} · {Kapitel} Kapitel · ca. {Woerter} Woerter
RomanForge: Projekt {ID} · Instanz {live/lokal} · Export {Zeitpunkt}

Frag mich zuerst, wo die Exportdatei liegt.
Keine Uebersetzung, keine Bilder, nichts ueberschreiben ohne meine Freigabe.
```
