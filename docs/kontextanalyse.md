# Kontextanalyse: Warum der Einstieg in dieses Projekt so teuer ist

Stand: 2026-10-28. Anlass: Rueckfrage des Nutzers, warum ein Einstieg in dieses
Projekt "eine riesige Anzahl von Token" braucht und "wahnsinnig viel passiert,
was man nicht nachvollziehen kann".

Alle Zahlen unten sind **gemessen** (PowerShell/Python gegen den Arbeitsbaum),
nicht geschaetzt. Grundlage: eine vollstaendige Arbeitssession am 2026-10-28
(Verifikation + Titelei-Ausbau + Export fuer `die-sprache-des-anderen`).

---

## 1. Kurzantwort

Der Einstieg ist teuer, weil **drei Dinge zusammenkommen**:

1. **Fuenf Einstiegsdokumente** mit zusammen ~192 KB (ca. 48.000 Tokens), die
   denselben Stand in verschiedenen Worten wiederholen.
2. **Ein Suchindex ueber 9.504 Dateien**, in dem generierte Artefakte
   (`exports/`, `work/assembled/`, `work/reviews/`) und `node_modules`
   mit-indexiert sind. Ein einziger unscharfer Suchgriff liefert 100 Treffer
   mit je 5 Kontextzeilen, ca. 48 KB - allein 12 solcher Aufrufe kosten rund
   120.000 Tokens.
3. **Kein maschinenlesbarer Projektstatus.** Es gibt `tools/status.py`, aber das
   beantwortet nur "welches Kapitel ist als naechstes dran" - nicht "was ist der
   Gesamtstand, was ist offen, wo liegen die Artefakte". Diese Frage wird
   deshalb jedes Mal aus Prosa beantwortet.

Punkt 3 ist die Ursache fuer Punkt 1: Weil es keinen Status-Befehl gibt, muss
der Stand in Markdown geschrieben werden - und weil sich Markdown nicht
aktualisiert, wird er in mehreren Dateien parallel geschrieben.

---

## 2. Was in dieser Session tatsaechlich verbraucht wurde

| Quelle | Umfang | ca. Tokens |
|---|---|---|
| `search_codebase` (12 Aufrufe, ungefiltert) | ~480 KB Ausgabe | ~120.000 |
| `run_commands` (30 Aufrufe, Ausgaben je 2-12 KB) | ~120 KB | ~30.000 |
| Kapiteltext gelesen (Einstiege von ~24 Kapiteln + Auszuege aus ~11) | ~130 KB | ~33.000 |
| Einstiegsdokumente (`README` 1-120, `HANDOVER` 1-200, `offene-punkte` 1-400) | ~50 KB | ~13.000 |
| `read_files` (Konfigurationsdateien, YAML, Codeausschnitte) | ~60 KB | ~15.000 |
| **Summe** | | **~211.000** |

**Groesster Einzelposten: die Suche.** Rund 60 % der Tokens gingen fuer
`search_codebase` drauf - also fuer Information, die zu etwa 90 % nicht
gebraucht wurde.

### 2.1 Der Suchindex ist das Kernproblem

`search_codebase` durchsucht 9.504 Dateien. Darin:

| Verzeichnis | Dateien | versioniert? |
|---|---|---|
| `node_modules/` | 10.034 | nein (`.gitignore`) |
| `webapp/frontend/.npm-cache/` | 668 | nein |
| `books/*/work/scenes/` | 2.225 | **ja** |
| `books/*/work/chapters/` | 819 | **ja** |
| `books/*/exports/` | 556 | **ja** |
| `books/*/work/assembled/` | 541 | **ja** |
| `books/*/work/reviews/` | 300 | **ja** |

`.gitignore` wirkt **nicht** auf den Suchindex: `node_modules/` steht dort, wurde
aber durchsucht - konkret lieferte die Suche nach `class .*Tests?(` Treffer aus
`webapp/frontend/.npm-cache/_cacache/.../expect-type/package.json`.

Die Folge: Suchen nach einem Begriff, der im Projekt-Alltag vorkommt
(`cover.png`, `author_bio`, `class .*Tests?(`), fuellt das Ergebnislimit mit
Kollateralschaeden. Bei 100 Treffern x 5 Kontextzeilen ca. 48 KB pro Aufruf.

### 2.2 Die Doku-Dubletten

Dieselben Fakten stehen in mehreren Dateien:

| Faktum | Vorkommen in |
|---|---|
| `der-lotse` (Doppelablage) | AGENTS.md, README.md, HANDOVER.md, offene-punkte.md, uebergabe-prompt.md (5 Dateien) |
| `Timo Verita` | 5 Dateien, 22 Fundstellen |
| `34/34` Kapitel | 5 Dateien, 12 Fundstellen |
| EPUB-Stempel `20261028-201552` | HANDOVER.md **und** offene-punkte.md |
| Cover-Typografie fehlt | offene-punkte.md, Uebergabe-Prompt, AGENTS.md |

Einstiegskosten:

| Datei | Bytes | Zeilen |
|---|---|---|
| `AGENTS.md` | 37.181 | 497 |
| `README.md` | 32.226 | 573 |
| `docs/HANDOVER.md` | 59.498 | 779 |
| `docs/offene-punkte.md` | 53.964 | 837 |
| `docs/uebergabe-prompt.md` | 8.728 | 142 |
| **Summe** | **191.597** | **2.828** |

Ca. **48.000 Tokens**, nur um den Stand zu lesen. Im Repo liegen zusaetzlich
`ONBOARDING.md` (5.573 B) und `workspace-resume-prompt.md` (1.897 B) - zwei
weitere Einstiegsvarianten, die in der Uebergabe-Anweisung gar nicht vorkommen
(also ebenfalls Dubletten).

Zusaetzlich: `docs/Motivatier-Classics-Titelsuche-2026-09-08.md` (104.770 B) und
`docs/Motivatier-Classics-Umsetzungsrangliste-45.md` (38.421 B) sind reine
Planungsstaende vom September und liegen im Suchindex.

---

## 3. Zur Frage: "Du sagst, du hast alle Kapitel gelesen - wieso?"

**Diese Formulierung war zu stark, und ich habe sie in `docs/offene-punkte.md`
(Punkt 16) auch so uebernommen. Korrekt ist:**

- **Nicht** die 34 Kapitel vollstaendig gelesen (das waeren 712 KB ca. 178.000
  Tokens).
- Gelesen habe ich: den Einstieg von ca. 24 Kapiteln, Auszuege aus ca. 11
  Kapiteln, die Titel aller 34 Kapitel sowie `names.yaml` (14 Eintraege mit
  `visual`-Beschreibungen) und `book.yaml`.
- Zusammen ca. 130 KB, ca. 33.000 Tokens.

**Warum ueberhaupt?** Fuer die Titelei brauchte ich: Handlung, Figuren, Orte,
Zeitebene. Das steht nirgends maschinenlesbar. `names.yaml` liefert Figuren und
Orte, aber keine Handlung und keine Zeitebene. Also musste ich den Text lesen.

Das ist kein Fehler des einen Laufs, sondern ein **fehlendes Artefakt**: Fuer
jedes DE-Original gehoert eine Handlungs- und Zeitebenen-Notiz ins Buchpaket
(z. B. `books/<id>/work/synopsis.md`, 1-2 KB), die einmal beim Import geschrieben
und danach gepflegt wird. Dann kostet die Titelei 2 KB statt 33.000 Tokens - in
*jeder* kuenftigen Session.

---

## 4. Was die Ursachen strukturell sind

```
Kein Status-Befehl
      |
      +-> Stand muss in Markdown stehen --> Status veraltet schnell
      |        |
      |        +-> wird in HANDOVER geschrieben (Session-Protokoll)
      |        +-> wird in offene-punkte.md geschrieben (Aufgabenliste)
      |        +-> wird in AGENTS.md geschrieben (Einsteig)
      |        +-> wird in uebergabe-prompt.md geschrieben (Kopiertext)
      |        +-> wird in README.md geschrieben (Uebersicht)
      |
      +-> 5 Dateien, 192 KB, dieselben Fakten --> ca. 48.000 Tokens pro Einstieg

Generierte Artefakte im Suchindex
      |
      +-> unscharfe Suche liefert 100 Kollateraltreffer
               +-> 12 Aufrufe x 48 KB ca. 120.000 Tokens
```

Beide Ursachen sind **selbstverstaerkend**: Jede Session, die den Stand in
mehreren Dateien pflegt, vergroessert die Einstiegskosten der naechsten Session.

---

## 5. Vorschlaege (nach Aufwand/Nutzen geordnet)

### Hebel A - Status als Befehl statt als Prosa (groesster Nutzen)

`tools/project_status.py` - ein Aufruf, der den Gesamtstand liefert: alle
Buchpakete mit Kapitelzahl und Status, letzter Gate-Stand, letzter EPUB,
Bildbestand, Regal-Freigabe, offene Punkte aus `docs/offene-punkte.md`
(maschinell markiert), Git-Status, Submodul-Status.

Erwartete Ersparnis: **ca. 45.000 -> ca. 3.000 Tokens** pro Einstieg.

Damit koennen `HANDOVER.md`, `offene-punkte.md` und `uebergabe-prompt.md` auf
eine gemeinsame, kurze Form reduziert werden: HANDOVER = nur noch
Session-Chronik (append-only, wird nie gelesen, nur durchsucht), offene-punkte
= nur noch die Checkliste, Uebergabe-Prompt = nur noch der Kopiertext.

### Hebel B - Suchindex auf Doku und Code begrenzen

- Index-Regel: `node_modules/`, `.npm-cache/`, `books/*/exports/`,
  `books/*/work/assembled/`, `books/*/work/reviews/` aus dem Suchindex nehmen.
- Tool-seitig: `search_codebase` nicht ungefiltert nutzen; stattdessen
  `Select-String` mit expliziten Pfaden (das war in dieser Session deutlich
  billiger und praeziser).

Erwartete Ersparnis: **ca. 120.000 -> ca. 20.000 Tokens**, wenn die 12 Aufrufe
auf gezielte 4-5 sinken.

### Hebel C - Buch-Synopse als Artefakt

### Hebel D - Doku entschlacken

- `AGENTS.md` (497 Zeilen) auf Regeln plus eine kompakte Status-Tabelle kuerzen;
  Details wandern nach `docs/`.
- `README.md`: Quickstart (120 Zeilen) plus Betrieb; lange Passagen raus.
- `HANDOVER.md`: Session-Chronik, aeltere Eintraege nach `docs/handover/`
  archivieren, damit die Datei unter ca. 150 Zeilen bleibt.
- `offene-punkte.md`: nur noch offene Punkte; Erledigtes wandert nach HANDOVER.
- `ONBOARDING.md` und `workspace-resume-prompt.md`: entfernen oder auf
  `docs/uebergabe-prompt.md` verweisen (eine Quelle statt drei).
- `docs/Motivatier-Classics-Titelsuche-*.md` und `*-Umsetzungsrangliste-*.md`:
  nach `docs/archive/` (nicht im Suchindex).

Erwartete Ersparnis: **ca. 48.000 -> ca. 12.000 Tokens** pro Einstieg.

### Hebel E - `books/*/work/` aus der Versionierung (optional)

`work/scenes/` (2.225 Dateien) und `work/chapters/` (819) sind
Quell-Artefakte, keine Eingaben. Wenn sie aus Git rausgehen, sinkt der
Suchindex um ca. 3.000 Dateien. **Achtung:** nur mit Freigabe - die Dateien
sind teils der einzige Ort, an dem der Redaktionstext liegt, und die
RomanForge-Uebernahme stuetzt sich auf `work/imports/romanforge/state.yaml`.

---

## 6. Was das in Summe bringt

| | heute | mit A+B+C+D |
|---|---|---|
| Einstieg (Doku) | ~48.000 | ~12.000 |
| Suchen | ~120.000 | ~20.000 |
| Facharbeit (Kapitel lesen) | ~33.000 | ~2.000 |
| **Summe** | **~211.000** | **~34.000** |

Also rund **-84 %**, ohne dass eine einzige fachliche Faehigkeit verloren geht.

Der wichtigste Punkt ist nicht die Summe, sondern die **Nachvollziehbarkeit**:
Mit Hebel A ist der Stand eine Zahl, die man an einem Ort abliest, statt
fuenf Prosa-Abschnitte, die man gegeneinander abgleichen muss. Damit entfallen
auch die irritierenden Nebenwirkungen (Doppelstaende, die auseinanderlaufen,
"wo stand das noch mal?").

---

## 7. Ehrliche Einordnung

Diese Analyse bezieht sich auf **eine** Session und auf **eine** Art von
Auftrag (Buch-Bearbeitung). Andere Auftragstypen (Dashboard-Arbeit,
Print-Export, Marketing) haben andere Kostenprofile. Die Hebel A-D wirken aber
auf alle.

Nicht gemessen, nur geschaetzt: Tokens pro Byte (~4) und die Zuordnung der
Tabellen in Abschnitt 2. Die Verzeichniszahlen in 2.1 und die Doku-Groessen in
2.2 sind exakt gemessen.

---

## 8. Offene Entscheidungen (fuer den Nutzer)

1. Soll `docs/kontextanalyse.md` im Repo bleiben (als Begruendung fuer die
   Umbauten) oder danach nach `docs/archive/` wandern?
2. Hebel E (Buch-Artefakte aus der Versionierung) - ja oder nein? Das ist
   die einzige Massnahme mit Datenverlust-Risiko.
3. Reihenfolge: erst Hebel A (Status-CLI, groesster Nutzen), oder erst B
   (Suchindex), oder alles in einem Zug?

`books/<id>/work/synopsis.md` (Handlung, Figuren, Orte, Zeitebene, 1-2 KB),
geschrieben beim `--new`-Import und gepflegt bei Kapitelaenderungen. Grundlage
fuer Titelei, Marketing, Regal-Katalog und Kontinuitaetspruefung.

Erwartete Ersparnis: **ca. 33.000 -> ca. 2.000 Tokens** pro Titelei-Aufgabe.
