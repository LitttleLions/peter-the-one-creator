# Onboarding-Prompt für neuen Chat

> Diesen Text in einen neuen Chat kopieren, um der KI den aktuellen
> Projektstand in kompakter Form zu erklären.

---

Du arbeitest am Projekt **peter-the-one** (Repo auf GitHub:
`github.com/LitttleLions/peter-the-creator` — vom Nutzer
`LitttleLions`).

## Worum es geht

Regelbasierte kapitelweise Übersetzung literarischer Werke. Aktuelles
Buch: Alexei Tolstois „Peter der Erste" (Пётр Первый, RU → DE) gemäß
Regelkatalog in `logic/peter the one - Regeln 001.txt` (Sanderson-Stil
+ Sorkin-Konfliktdynamik). Python-CLI-Pipeline.

## Aktueller Stand (Juni 2026)

- 18 Kapitel erkannt (Книга 1: 7, Книга 2: 5, Книга 3: 6)
- 228.951 Wörter Original (russisch)
- Status: 1/18 in Bearbeitung – Kapitel 1 Pilotphase
- 2 lokale Commits noch nicht gepusht (`78071c4`, `b5fbc98`)

## Wie wir arbeiten

Pro Kapitel:
1. `python tools/status.py mark NNN in_progress`
2. Russischen Quelltext aus `output/.../chapters/NNN-source.md` lesen
3. Übersetzung schreiben – aktuell **zwei Versionen parallel**:
   - `NNN-translation-v1-stylized.md` (Regelwerk aktiv, ausgebaut)
   - `NNN-translation-v2-literal.md` (Regelwerk aus, wörtlich)
4. Pro Version ein Logeintrag in
   `status/logs/<Buch>/NNN.log.md` (welche Regeln, schwierige Stellen,
   Anpassungen)
5. `mark NNN done --words <Wortzahl> --title-de "..."` oder
   `mark NNN needs_review`

## Stil-Modi

Pro Buch in `config/rules-overrides.yaml` unter `style_mode`:
- `literal` — wörtlich, regelfrei
- `middle` — leichte Stilisierung
- `stylized` — volle Regelanwendung

Aktuell für Peter I auf `literal` gestellt (Pilot für `v2-literal.md`).

## Namensschreibweise

Stil A (Duden-Transliteration): Пётр→Peter, Иван→Iwan, Софья→Sofja,
Алексей→Alexei, Толстой→Tolstoi, etc. Kandidaten-Tabelle zur Diskussion
in `config/naming_choices.yaml` (offene Punkte: Iwanka vs. Iwan,
„Zigeuner", Alexander Menschikow).

## Wo zu lesen

- **Pflicht zuerst**: `AGENTS.md` (zentrale KI-Kontextdatei, mit
  Konventionen, Pfaden, Befehlen)
- **Für Menschen**: `README.md` (Status, Workflow, Roadmap)
- **Bei Pipeline-Fragen**: `config/pipeline.yaml`,
  `config/rules-overrides.yaml`
- **Bei Stil-/Regelfragen**: `logic/peter the one - Regeln 001.txt`
- **Bei Namensfragen**: `config/naming_proposal_peter_i.md` und
  `config/naming_choices.yaml`
- **Status-Übersicht**: `python tools/status.py summary`
- **Pilot-Log Kapitel 1**: `status/logs/Peter I/001.log.md`

## Was du nicht tust (harte Regeln)

- **`books/` ist tabu** – auch keine „Duplikate" (`.rtf` neben `.doc`)
  eigenmächtig löschen. Im Zweifel: liegen lassen, Nutzer fragen.
- **`logic/` ist heilig** – nie ohne Rückfrage ändern.
- **Status & Logs immer über CLI** (`tools/status.py`), nie direkt in
  JSON-Dateien herumschreiben.
- **Im Zweifel nachfragen**, nicht still annehmen.
- **Antworten auf Deutsch.**

## Offene Aufgaben (Roadmap, sortiert)

1. Kapitel 1 fertigstellen (Szenen 4–19 fehlen in v1 und v2)
2. Vergleichsdatei `001-compare.md` (v1 vs v2 nebeneinander)
3. **OpenRouter-Provider anbinden** – `.env` mit `OPENROUTER_API_KEY`,
   pro Buch anderes Modell wählbar; `tools/translate_chapter.py`
4. Namenslogik final festlegen
5. Iterative Phase ab Kapitel 2

## Konventionen – kurz

- `books/` = heilig, `logic/` = heilig
- `output/.../NNN-source.md` = Original (RU)
- `output/.../NNN-translation-vN-<stil>.md` = Übersetzungs-Versionen
- `status/<Buch>.status.json` = maschinenlesbarer Status
- `status/logs/<Buch>/NNN.log.md` = pro Kapitel, ein File
- Versions-Suffix: `v1` = erste Version (z. B. stylized),
  `v2` = zweite Version (z. B. literal)

## Aktueller task_progress-Stand

- ✅ Pipeline steht (Setup + 18 Kapitel extrahiert)
- ✅ Status & Logfiles etabliert
- ✅ Namensschreibweise festgelegt: Stil A (Transliteration)
- ✅ Pilot-Kapitel 1 in zwei Versionen angefangen
- ✅ Namens-Kandidaten-Tabelle angelegt
- ✅ Git initialisiert, 2 Commits lokal
- ⏳ **Nächster Planungsschritt**: OpenRouter-Provider-System
- ⏳ Wartet auf Feedback zum Pilot (Ton, Stil, Namen)
- ⏳ Rest von Kapitel 1 fertigstellen
- ⏳ Vergleichsdatei `001-compare.md`
