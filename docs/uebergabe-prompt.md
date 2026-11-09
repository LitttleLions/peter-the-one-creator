# Uebergabe-Prompt (neues Chat-Fenster, gleicher Ordner)

Kopiertext fuer ein neues Chat-Fenster im peter-Ordner des jeweiligen Rechners
(z. B. `C:\code\peter-the-one`, Branch `main`). Kein neues Setup, kein Clone.
Unter Windows CLI immer `.\.venv\Scripts\python.exe`, nicht `python`/`py -3`.
Kein OpenRouter ohne ausdrueckliche Freigabe. Committen und Pushen nur nach
Freigabe des Nutzers, kein Branch-Wechsel.

Es gibt zwei Prompts: **A** (Aufgabe: neue Fassung aus RomanForge holen und
daraus Marketing machen, Stand 2026-11-09) und **B** (allgemeiner Einstieg
mit Warten auf die Aufgabe, ab „Schritt 1“).

---

## Prompt A: neue Fassung aus RomanForge holen, dann Marketing

peter ist das Programm; RomanForge liefert den Roman (die „Novel“-Fassung). Der
Ablauf holt eine neue Fassung ueber die Uebergabe-Schnittstelle, uebernimmt nur
freigegebene Kapitel und baut danach das Marketing aus der neuen Fassung.
Felder in `<...>` vor dem Einfuegen ausfuellen; unbekannte leer lassen.

```text
Arbeite im peter-Ordner (Branch main, kein neuer Clone). Hole zuerst den neuesten Stand:
git fetch, dann git pull --ff-only. Bei Abweichung oder uncommitteten Aenderungen anhalten und fragen.

Lies nur: AGENTS.md, docs/uebernahme-romanforge.md (und docs/romanforge-figuren.md, falls das Buch
RomanForge-Figuren hat), danach docs/marketing-export.md (Abschnitte "Ablauf im Alltag",
"Konfiguration", "Bedienung"). Keine Kapiteltexte lesen.

Aufgabe: Von <TITEL> (peter-Buch-ID <id>) liegt in RomanForge eine neue Fassung vor
(Projekt <ID>, Uebergabe <ID>). Hole sie mit dem Werkzeug, uebernimm freigegebene Kapitel und
baue danach das Marketing aus der neuen Fassung.

Ablauf (jeder Schritt mit Kurzbericht, dann weiter):
1. Zugang pruefen: In .env muessen ROMANFORGE_URL und ROMANFORGE_API_KEY stehen. Nur melden, ob sie
   vorhanden sind, Werte nie anzeigen. Fehlen sie, anhalten und mich fragen.
2. Modus: NEU (Buch in peter unbekannt) oder AKTUALISIEREN. Passt er nicht zum Stand: anhalten und fragen.
3. Vergleich (schreibt nichts), nur die Tabelle zeigen:
   .\.venv\Scripts\python.exe tools/import_markdown_original.py --book <id> --handoff <Uebergabe-ID> --compare
4. Auf meine Freigabe: --accept, hoechstens 5 Kapitel pro Lauf; --keep nur nach Absprache. Danach pro
   Kapitel assemble_chapter.py und review_manuscript.py --llm none, nur die Zusammenfassung
   (ERROR/WARNING/INFO). Bei ERROR>0 stoppt der Export.
5. Figuren (falls vorhanden): tools/sync_romanforge_characters.py --book <id> --handoff <Uebergabe-ID>
   als Trockenlauf; --apply nur nach Freigabe.
6. Marketing: erst tools/export_marketing.py --book <id> --dry-run. Das Paket aus vorhandenen Texten
   ist kostenlos. Neue Texterzeugung ueber OpenRouter (--provider openrouter --regenerate) und
   Higgsfield nur nach meiner ausdruecklichen Freigabe je Aufruf.

Regeln: Kapiteltexte nur ueber die Werkzeug-Tabelle vergleichen, nichts ueberschreiben ohne Freigabe,
books/*/source/ und logic/ nicht aendern. Secrets (API-Schluessel, Passwoerter, Tokens) nie in den
Chat oder ins Repo. Commit und Push nur nach meiner Freigabe. Fange nichts anderes an, ohne zu fragen.
```

---

## Prompt B: allgemeiner Einstieg

## Schritt 1 (jetzt): nur lesen, dann WARTEN

Lies **ausschliesslich** diese beiden Dinge:

1. `README.md` – nur die Abschnitte „Schnellstart Fuer KI Und Menschen"
   (Zeilen 12-46) und „Arbeitsplan / Offene Punkte" (Zeilen 47-96).
2. `docs/kontextanalyse.md` – nur Abschnitt 1 (Kurzantwort) und Abschnitt 5
   (Vorschlaege).

**Dann stoppst du.** Antworte mit:

- dem Stand in 3-5 knappen Saetzen (welche Buchpakete, was offen, was zuletzt
  passiert ist),
- der Frage, welche Aufgabe du machen soll.

**Lies jetzt NICHT** `docs/HANDOVER.md`, `docs/offene-punkte.md`,
`docs/uebernahme-romanforge.md`, `docs/kontinuitaetspruefung-chronik.md` und
keine Kapiteltexte unter `books/*/work/`. Diese Dateien stehen dir zur
Verfuegung, **sobald die konkrete Aufgabe sie braucht** - nicht vorher. Das
spart rund 45.000 Tokens pro Sitzung; die Messung steht in
`docs/kontextanalyse.md`, Abschnitt 2.

Mach aus dem Warten keine Eigenaktivitaet: keine Tests, keine Exporte, keine
Suche im Repo, keine Datei-Aenderung, bevor der Nutzer die Aufgabe genannt hat.

---

## Schritt 2 (erst wenn die Aufgabe klar ist)

So arbeitest du, sobald eine Aufgabe benannt wurde:

- **Stand maschinell abfragen, nicht aus Prosa lesen.**
  `.\.venv\Scripts\python.exe tools/status.py --book <id> summary`
  Bei `Buch mit id=<x> nicht gefunden`: sofort stoppen, keine Alternativ-ID
  erfinden und keinen Zweitordner anlegen; aehnliche IDs aus der Fehlermeldung
  beachten und per Rueckfrage klaeren.
- **Suche immer mit Pfad-Filter, nie ungefiltert ueber das ganze Repo.**
  `Select-String -Path '<pfad>' -Pattern '<muster>'` statt eines
  repo-weiten `search_codebase`. Der Suchindex enthaelt `node_modules/`,
  `.npm-cache/` und generierte Artefakte (`books/*/exports/`,
  `books/*/work/assembled/`, `books/*/work/reviews/`); ein ungefilterter Griff
  liefert 100 Kollateraltreffer mit Kontextzeilen und kostet ~48 KB pro Aufruf.
- **Keine Massendatei-Lesen.** Ein Buchpaket wird gezielt angefasst, nicht
  gelesen. Fuer Figuren und Orte reichen `names.yaml` und `book.yaml`.
- **Buchbezogen arbeiten** unter `books/<buch-id>/`. Nie eigenmaechtig in
  `source/` eingreifen. Zwei Ordner fuer einen Titel (z. B.
  `sprache-des-anderen` vs. `die-sprache-des-anderen`): sofort stoppen, per
  Rueckfrage klaeren, kein Assembly/Export vorher.
- **Keine eigenen Pruef-Skripte oder Datei-Listen.** Nutze die vorhandenen CLIs
  unter `tools/` (siehe Schnellstart in `README.md`). Keine `SUMMARY*.md` im
  Repo-Root, keine `tools/create_*.py` ohne Freigabe; Placeholder-Bilder
  gehoeren nicht zur Pipeline.
- **Release-Gate:** ERROR>0 stoppt den Export; Bypass nur
  `--allow-review-errors`.
- **Im Zweifel: erst fragen, dann schreiben.** Keine Spekulation, kein
  `tmp_*.py` im Repo-Root.

---

## Die wesentlichen Punkte zur Verbesserung

Diese vier Hebel sind die Ursache der bisherigen Einstiegskosten. Details,
Messungen und Umsetzungsskizzen stehen in `docs/kontextanalyse.md`.

| # | Hebel | Kernaussage | Nutzen |
|---|---|---|---|
| **A** | **Status als Befehl statt als Prosa** | Es gibt keinen maschinenlesbaren Gesamtstatus. `tools/status.py` beantwortet nur „welches Kapitel ist als naechstes dran". Deshalb muss der Stand in Markdown stehen - und steht deshalb in 5 Dateien parallel. Baue `tools/project_status.py` (alle Buchpakete, Gate, letzter EPUB, Bildbestand, Regal, offene Punkte, Git-Status). | ~45.000 -> ~3.000 Tokens pro Einstieg |
| **B** | **Suchindex auf Doku und Code begrenzen** | `search_codebase` durchsucht 9.504 Dateien, inklusive `node_modules/`, `.npm-cache/` und generierter Artefakte. `.gitignore` wirkt nicht auf den Index. 12 ungefilterte Aufrufe kosteten ~120.000 Tokens, davon ~90 % ungenutzt. | ~120.000 -> ~20.000 Tokens |
| **C** | **Buch-Synopse als Artefakt** | Handlung, Figuren, Orte und Zeitebene eines Romans stehen nirgends maschinenlesbar. Deshalb wurden fuer eine Titelei ~130 KB Kapiteltext gelesen. Braucht `books/<id>/work/synopsis.md` (1-2 KB), geschrieben beim Import. | ~33.000 -> ~2.000 Tokens pro Titelei-Aufgabe |
| **D** | **Doku entschlacken** | `AGENTS.md` (497 Z.) + `README.md` (573 Z.) + `HANDOVER.md` (779 Z.) + `offene-punkte.md` (837 Z.) + `uebergabe-prompt.md` = 191.597 Bytes fuer denselben Stand. Dazu zwei weitere Einstiegsvarianten (`ONBOARDING.md`, `workspace-resume-prompt.md`) und zwei September-Planungsdokumente. | ~48.000 -> ~12.000 Tokens pro Einstieg |

**E (optional, mit Datenverlust-Risiko):** `books/*/work/` aus der Versionierung
nehmen (`work/scenes/` 2.225 Dateien, `work/chapters/` 819). Das senkt den
Suchindex um ca. 3.000 Dateien - aber diese Dateien sind teils der einzige
Ort, an dem der Redaktionstext liegt, und die RomanForge-Uebernahme stuetzt
sich auf `work/imports/romanforge/state.yaml`. **Nur mit ausdruecklicher
Freigabe.**

Zusammen A-D: **~211.000 -> ~34.000 Tokens pro Sitzung (-84 %)**, ohne Verlust
fachlicher Faehigkeit. Der eigentliche Gewinn ist die Nachvollziehbarkeit: Der
Stand wird eine Zahl an einem Ort statt fuenf Prosa-Abschnitte, die man
gegeneinander abgleichen muss.

---

## Orientierung Stand 2026-10-28 (nur Kurzfassung)

Hinweis (2026-11-09): Seitdem kamen die RomanForge-Schnittstelle (`--handoff`,
`rf_id`, Figuren-Abgleich, Verlagsangaben) und weitere Uebernahmen dazu; aktueller
Stand in `docs/HANDOVER.md` (Kopf) und `docs/uebernahme-romanforge.md`. Der Stand
unten ist nur noch Hintergrund.

Details nur bei Bedarf: `docs/HANDOVER.md` (Session-Chronik),
`docs/offene-punkte.md` (Checkliste).

- **17 Buchpakete** unter `books/<id>/`. Live: `aelita`, `leben-arsenjews`,
  `pharao`, `peter-i-buch-01`. DE-Originale: `die-dritte-chronik` (KDP-fertig),
  `die-sprache-des-anderen`, `der-lotse-von-ruegen`, `der-lotse`, `ashkara`,
  `perfect.sight`.
- **`die-sprache-des-anderen`** (Timo Verita, 34 Kapitel): Gate 0/0/0,
  Titelei gefuellt (2026-10-28), Buch-EPUB `...-20261028-203757.epub`
  mit Cover + Kapitelbildern 001-003.
- **Chronik** (`die-dritte-chronik`, 48 Kapitel): Gate 0/13/36, KDP-fertig,
  EPUB `...-20260921-131112.epub`. Offen: Kindle-Preview + KDP-Upload durch
  Nutzer; Nutzer entscheidet Kapitel 012/025.
- **Offen und teuer:** weitere Kapitelbilder 004-034 (Sprache des Anderen)
  bzw. 011-033 (Lotse) - Higgsfield, nur nach Freigabe; Regal-Deploy fuer den
  Lotse; Pharao-Print-Leseprobe; Ashkara `--new`.
- **Vorgemerkt im Working Tree** (nicht von diesem Chat erzeugt, nicht
  committen): neues Cover der Sprache des Anderen, neue Lotse-Kapitelbilder
  011-032. `books/die-dritte-chronik/source/Die dritte Chronik(1).md` bleibt
  untracked - `source/` ist tabu.
- **Regeln, die immer gelten:** `books/*/source/` und `logic/` nicht ohne
  Rueckfrage aendern; keine Secrets, kein Force-Push, kein Hard-Reset, kein
  Branch-Wechsel; Uebersetzungslaeufe und Higgsfield nur nach Freigabe.

---

## Historie (nur falls jemand fragt)

Die vollstaendige Session-Chronik liegt in `docs/HANDOVER.md`; die
verbindliche Aufgabenliste in `docs/offene-punkte.md`. Beide **nicht** beim
Einstieg lesen.

