# Plan: Uebernahme von Manuskripten aus RomanForge

Stand: 2026-10-07 · Status: **Stufe 1 umgesetzt und abgenommen (noch nicht
committet); naechster Schritt `--new` fuer Ashkara** · Gegenstueck: RomanForge AI
(`github.com/LitttleLions/NovelWriter`), Spezifikation der RomanForge-Seite dort
in `docs/plan-uebergabe-peter.md`, Verweis in `docs/plan-buch-ablauf.md`.
Arbeitsablauf fuer die KI: `docs/uebernahme-romanforge.md`.

## 1. Ausgangslage

- **RomanForge** (Next.js, PostgreSQL, live) entwickelt und schreibt Buecher:
  Expose, Figurenkartei, Kapitelplan, Stil, sequenzielle Kapitelgenerierung mit
  Erzaehlgedaechtnis und KI-Inhaltspruefung. Einheit ist das Kapitel; keine
  Szenen, keine Verlagsangaben. Export MD/DOCX/TXT, kein EPUB, kein Import von
  Manuskripten. Handbearbeitungen ueberschreiben den Kapiteltext ohne Verlauf
  (nur Revisionszaehler).
- **peter-the-one** macht aus fertigem Text ein veroeffentlichtes Buch:
  Uebersetzung, deterministisches Gate, Satz, EPUB/Print/KDP, Bilder,
  Marketing, Regal-Website. Dateibasiert unter `books/<id>/`, versioniert mit Git.
- **Die dritte Chronik** kam am 2026-07-28 als RomanForge-Markdown-Export nach
  `books/die-dritte-chronik/source/Die dritte Chronik.md`, wurde mit
  `tools/import_die_dritte_chronik.py` zerlegt und danach in peter redigiert.
  **Achtung:** `source/` wurde am 2026-09-18 per „Source-Sync" (`15566c0`) an die
  Redaktion angeglichen und ist kein reiner Export mehr. Der Ursprungs-Export
  liegt nur noch in Git: `git show 150f0c1:"books/die-dritte-chronik/source/Die dritte Chronik.md"`.

Probleme vor Stufe 1: Import-Skript pro Buch, das alles ohne Rueckfrage
ueberschreibt; keine Erkennung, welche Kapitel sich wo geaendert haben;
fuenf bis sechs Kopien pro Kapitel; zwei Kopfformate in den Szenendateien
(`## Titel` und Kapitelkopf `# Titel` + `*Buch: …*` + `*Kapitel-ID: …*` + `---`).

## 2. Entscheidungen

| # | Thema | Festlegung |
|---|---|---|
| 1 | Architektur | Getrennt lassen, kein Zusammenlegen. Wiederholbarer Abgleich statt harter Sperre nach der Uebergabe |
| 2 | Fuehrung des Texts | Inhaltliches (Logik, Stil, Szenen) in RomanForge; Formales (Satzzeichen, Gate-Fixes, Tippfehler) in peter. Abgleich gegen den letzten Uebernahmestand |
| 3 | Konflikte | Nur anzeigen, der Mensch entscheidet. Kein automatisches Zusammenfuehren |
| 4 | Eingang fuer Neufassungen | Nur noch ueber RomanForge. Die Ablage `status/<Titel> - NN ….md` faellt weg (`status/status.json` und `status/logs/` bleiben). Fuer DE-Originale ist `work/scenes/de/<style>/NNN/scene-01.md` die eine massgebliche Datei; das Werkzeug pflegt `work/chapters/` und `work/scenes/de/NNN/` mit |
| 5 | Uebergabe | **Ein** Uebergabe-Prompt mit zwei Modi: **NEU** (Buch in peter unbekannt) und **AKTUALISIEREN** (Buch existiert). Ausgeloest in RomanForge ueber die Export-Karte im Tab „Kapitel" („An peter uebergeben"), immer das ganze Buch |
| 6 | Transport | Stufe 1: Markdown-Export als Datei. Stufe 2: eingefrorener Uebergabe-Stand in RomanForge, Abruf durch peter per HTTPS mit **dauerhaftem persoenlichem API-Schluessel** in `.env` (`ROMANFORGE_URL`, `ROMANFORGE_API_KEY`); kein Geheimnis im Prompt |
| 7 | Referenz-Instanz | Nur Live-RomanForge. Lokale Kopien nur zum Entwickeln |
| 8 | Verlagsangaben | Nur in peter (`export.yaml`). peter fragt sie bei NEU ab; RomanForge bekommt keine neuen Felder |
| 9 | Stilprofile | Nicht synchronisieren (in RomanForge Schreibstimme, in peter Uebersetzungsregeln) |
| 10 | Datenbank fuer peter | Nein. Git versioniert besser als die RomanForge-Datenbank heute, alle Werkzeuge arbeiten auf Dateien |
| 11 | Arbeitsweise der KI | Vergleiche nur ueber das Werkzeug; die KI liest nur dessen Tabelle, keine Kapiteltexte. Text nur ausnahmsweise, hoechstens 3–5 Kapitel, nur Anfang. Kleine Schritte mit Kurzbericht |
| 12 | Testdaten | Keine erfundenen Texte. Tests arbeiten auf Tempokopien echter Chronik-Dateien; reine Logiktests mit Platzhalter-Pruefwerten sind erlaubt |

## 3. Abgleich mit dem letzten Uebernahmestand

Zustand pro Kapitel in `books/<id>/work/imports/romanforge/state.yaml`
(`rf_base`, `peter_base`, `base_export`, `title`); pro schreibendem Lauf
`runs/<stempel>/{export.md,report.md}`. Nur `--accept`/`--keep` aendern Eintraege.
Gibt es noch keine `state.yaml`, ist `--baseline <datei>` Pflicht. Der erste
schreibende Lauf legt `state.yaml` fuer **alle** Kapitel an (unberuehrte mit
`rf_base = peter_base =` Hash aus `--baseline`); danach wird `--baseline`
ignoriert. Ein Kapitel ohne Eintrag gilt als `ohne-ausgangsstand` (Exit 2),
nie als Konflikt und nie mit leerer Baseline.

| RomanForge seit letzter Uebernahme | peter seit letzter Uebernahme | Einstufung / Aktion |
|---|---|---|
| unveraendert | unveraendert | nichts |
| geaendert | unveraendert | uebernahme-vorgeschlagen (`--accept`) |
| unveraendert | geaendert | peter-behalten, „noch nicht in RomanForge" (keine Aktion) |
| geaendert | geaendert | konflikt: `--keep` (peter bleibt) oder `--accept` (RomanForge ersetzt, mit Warnung) |
| Kapitel neu / entfallen | – | melden, nie automatisch; Paar an gleicher Position = „vermutlich umbenannt" |

Kapitelgrenzen nur an `## `. Vor dem Hash: Aufbereitung wie Alt-Import
(`normalize_body`), LF, Leerzeichen am Zeilenende, Leerzeilen, nur ein `---`
ganz am Ende; innere `---` (Szenentrenner) bleiben.

## 4. Stufen

### Stufe 1 – Uebernahme-Werkzeug (umgesetzt, nicht committet)

`tools/import_markdown_original.py` (`--dry-run`, `--compare`, `--accept`,
`--keep`, `--baseline`, `--new`), `tests/test_import_markdown_original.py`
(31/31 gruen), `docs/uebernahme-romanforge.md`, Verweise in `AGENTS.md` und
`README.md`. Das Werkzeug schreibt nur die drei Textkopien; Assemble und Gate
gibt es als Folgebefehle aus.

Abnahme 2026-10-07 (Baseline = Ursprungs-Export `150f0c1`):
- a) Selbstvergleich: peter geaendert genau 008, 009, 012, 018, 025, 026, 031,
  033, 034, 035, 036, 041, 043; Rest nichts; keine Konflikte.
- b) gegen das per Source-Sync geaenderte `source/`: Konflikt 012, 018, 026,
  031, 033, 034, 035, 036, 041, 043; peter-behalten 008, 009, 025.

Offen fuer den Commit: nur die Stufe-1-Dateien einzeln auf `cline/pveejb87`
(dieser Branch liegt einen Commit vor `main`), kein `git add -A`.

### Stufe 1b – `--new` fertigstellen, erster Fall „Ashkara" (naechster Schritt, ca. ½ Tag)

Lueckenstand 2026-10-07:
1. `export.yaml` wird aus der Chronik kopiert inklusive Rechte,
   Herausgabevermerk, `original_title`, `title_page_extra` („Karakorum …"),
   Zusammenfassung, Website/Marketing. Ersetzen durch neutrale Vorlage:
   Struktur und Defaults uebernehmen, buchspezifische Texte leer, kein
   `website:`/`marketing:`-Block, leere Felder im Bericht als „offen".
2. `--new` legt nur das leere Paket an. Stattdessen alle Kapitel in einem Lauf
   importieren (drei Textkopien je Kapitel) und vollstaendige `state.yaml`
   schreiben. Paketweise Uebernahme gilt nur fuer AKTUALISIEREN.
3. `status/status.json` wie im Alt-Import anlegen (alle Kapitel, Wortzahl,
   Status done); vorher pruefen, was Dashboard/`status.py`/`export_manuscript.py`
   ohne sie tun wuerden.
4. Toter Code `source_baseline_hashes()` entfernen.

Tests auf Tempokopie des Chronik-Ursprungs-Exports (48 Kapitel, 48 Eintraege in
`state.yaml` und `status.json`, `export.yaml` ohne Chronik-Texte).

**Ashkara** ist der erste echte Abnahmefall: Voraussetzung deutschsprachiger
Roman in Live-RomanForge (kein Drehbuch, keine Uebersetzung). Ablauf: Export,
Uebergabe-Prompt Modus NEU, Verlagsangaben erfragen, `--new`, Assemble fuer alle
Kapitel, `review_manuscript --all --llm none`, Bericht. Cover, Bilder und EPUB
danach im normalen peter-Weg.

### Stufe 2 – Uebergabe aus der RomanForge-Oberflaeche (danach)

Spezifikation: NovelWriter `docs/plan-uebergabe-peter.md`. Kurz:
- Export-Karte im Tab „Kapitel": Zeile „An peter uebergeben" mit letzter
  Uebergabe und seitdem geaenderten Kapiteln; Klick friert den Stand ein und
  zeigt den fertigen Prompt (Modus NEU bei erster Uebergabe, sonst AKTUALISIEREN).
- Tabellen `api_keys` (dauerhafter Schluessel, nur Hash) und `project_handoffs`
  (Snapshot `romanforge-handoff/1` mit Kapitel-ID, Revision, Pruefwert, Text).
- peter: `--handoff <id>`, Abruf per `urllib`, Zuordnung per Kapitel-ID.
  Dafuer die interne Kapitelliste um optionale `rf_id` erweitern,
  `match_chapters` ID vor Titel, `state.yaml` speichert `rf_id`.
- Aufwand: RomanForge ca. 2 Tage plus Deploy, peter ca. ½ Tag.

### Stufe 3 – Rueckweg nach RomanForge (vor einem Folgeband, ca. 2 Tage)

- RomanForge speichert bei jeder Handbearbeitung den alten Stand als Revision.
- Manuskript-Import in RomanForge: Kapitel per ID aktualisieren, mit Vorschau;
  Erzaehlgedaechtnis nur als veraltet markieren, keine KI-Aufrufe beim Import.
- Bringt die Kapitel „noch nicht in RomanForge" zurueck und gibt einem Folgeband
  die Endfassung des Vorgaengers als Kontext.

Die fruehere Stufe 4 (API-Abruf) ist in Stufe 2 aufgegangen.

## 5. Uebergabe-Prompt

Ein Prompt fuer beide Faelle. Ab Stufe 2 fuellt RomanForge ihn aus; in Stufe 1
wird er von Hand ausgefuellt (unbekannte Felder leer lassen). Regeln und
Einzelschritte stehen in `docs/uebernahme-romanforge.md`, nicht im Prompt.

```text
Uebergabe aus RomanForge an peter-the-one

Lies AGENTS.md und docs/uebernahme-romanforge.md und folge dem Ablauf dort.

Modus: {NEU | AKTUALISIEREN}
Buch: {Titel} · {Genre} · {Kapitel} Kapitel · ca. {Woerter} Woerter
peter-Buch-ID: {id, falls bekannt}
RomanForge: {Instanz} · Projekt {ID} · Export/Uebergabe {ID} vom {Zeitpunkt}
Laut RomanForge seit der letzten Uebergabe geaendert: {Kapitelliste | erste Uebergabe}

Quelle: {Stufe 1: Frag mich nach dem Pfad der Exportdatei. | Stufe 2: --handoff {ID}}

NEU: Frag mich nach Autor/Pseudonym, Untertitel, Reihe, Verlag. Dann Buchpaket anlegen,
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

## 6. Ergebnis Chronik-Vergleich 2026-10-07

Frischer Export aus Live-RomanForge gegen Ursprungs-Export `150f0c1`:
nichts 35; peter-behalten 7 (009, 018, 026, 034, 035, 041, 043);
Konflikt 6 (008, 012, 025, 031, 033, 036); neu/entfallen 0.

Die Neufassungen 008, 012, 025, 031, 033, 036 wurden also in Live-RomanForge
geschrieben. Wortfolgen-Abgleich der Konflikte (RomanForge ~ peter):

| Kap. | Woerter Juli / RomanForge / peter | Aehnlichkeit | Entscheidung |
|---|---|---|---|
| 008, 031, 033, 036 | gleich | 1,00 | `--keep` (nur Formatierung/Satzzeichen; peter gate-geprueft, KDP-fertig) |
| 012 | 2746 / 4889 / 2341 | 0,05 | offen, Nutzer liest beide Fassungen |
| 025 | 860 / 2628 / 3092 | 0,12 | offen, Nutzer liest beide Fassungen |

Umgesetzt 2026-10-07 20:12: `--keep 008,031,033,036` mit Baseline `150f0c1`
(Export-Stempel `20261007-201221`); `state.yaml` mit 48 Eintraegen, kein
Kapiteltext geaendert. Folge-Vergleich ohne Baseline: nichts 35;
peter-behalten 11 (008, 009, 018, 026, 031, 033, 034, 035, 036, 041, 043 =
„noch nicht in RomanForge", Rueckweg Stufe 3); Konflikt 2 (012, 025).

`work/imports/romanforge/` (Zustand und Laufarchiv) gehoert ins Repo, weil der
Zustand sonst verloren geht. Die Download-Kopie `source/Die dritte Chronik(1).md`
gehoert nicht nach `source/` (identisch mit dem archivierten
`runs/20261007-201221/export.md`); der Nutzer entfernt sie.

## 7. Festgehalten, ohne Handlung jetzt

- Autor der Chronik uneinheitlich: `book.yaml` „Motivatier", `export.yaml`
  „Timo Verita".
- Beide `AGENTS.md` nennen `C:\code\…` als kanonischen Checkout; tatsaechlich
  liegen die Repos unter `E:\code\…`.
- `tools/import_die_dritte_chronik.py` ist durch das neue Werkzeug abgeloest;
  Entfernen nur nach Rueckfrage.
