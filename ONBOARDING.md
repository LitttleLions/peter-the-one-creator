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
- 3 lokale Commits noch nicht gepusht (`78071c4`, `b5fbc98`, `56d9ede`)
- **OpenRouter-Provider implementiert** (`tools/translate_chapter.py`,
  `tools/lib/openrouter_client.py`, `config/style_modes.yaml`).
  Dry-Run getestet; erster echter Lauf wartet auf den API-Key.

## Wie wir arbeiten

### Manueller Pilot-Workflow (bisher)
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

### OpenRouter-Workflow (NEU, ab jetzt möglich)
Pro Kapitel:
1. (optional) `python tools/status.py mark NNN in_progress`
2. `python tools/translate_chapter.py --chapter NNN --style {literal|middle|stylized}`
   - Lädt `config/style_modes.yaml` und baut die System-/User-Prompts
   - Hängt die Regeln aus `logic/` an (nur bei middle/stylized)
   - Ruft OpenRouter auf (Modell aus `config/books.yaml: ai.model`)
   - Schreibt `output/.../chapters/NNN-translation-vN-<stil>.md`
     (nächste freie vN-Version pro Stil, kein Überschreiben)
   - Schreibt Logfile und setzt Status auf `needs_review`
3. Mensch prüft das Ergebnis.

Dry-Run zum Testen ohne API-Call:
```bash
python tools/translate_chapter.py --chapter 001 --style stylized --dry-run
```

## Stil-Modi

Pro Buch in `config/books.yaml` unter `style_mode`. Die konkreten
System-Prompts liegen in `config/style_modes.yaml`:
- `literal` — wörtlich, regelfrei (Regeln werden NICHT angehängt)
- `middle` — leichte Stilisierung (Regeln werden angehängt)
- `stylized` — volle Regelanwendung (Regeln werden angehängt,
  inkl. Sanderson/Sorkin-Block)

Aktuell für Peter I auf `stylized` gestellt
(siehe `config/books.yaml: style_mode`).

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
  `config/rules-overrides.yaml`, `config/books.yaml`
- **Bei Stil-/Regelfragen**: `config/style_modes.yaml` und
  `logic/peter the one - Regeln 001.txt`
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

1. **Erster echter OpenRouter-Run** mit echtem API-Key (Validierung)
2. Vergleichsdatei `001-compare.md` (v1 vs v2 nebeneinander)
3. Namenslogik final festlegen
4. Iterative Phase ab Kapitel 2 (mit OpenRouter-Pipeline)
5. `tools/compare_chapters.py` (Szene-für-Szene nebeneinander)
6. (Bonus) Scene-Splitter verbessern: Szenen-Headings in `NNN-source.md`
   einbauen, damit die Pipeline wirklich szeneweise übersetzen kann

## Konventionen – kurz

- `books/` = heilig, `logic/` = heilig
- `output/.../NNN-source.md` = Original (RU)
- `output/.../NNN-translation-vN-<stil>.md` = Übersetzungs-Versionen
- `status/<Buch>.status.json` = maschinenlesbarer Status
- `status/logs/<Buch>/NNN.log.md` = pro Kapitel, ein File
- Versions-Suffix: `v1` = erste Version (z. B. stylized),
  `v2` = zweite Version (z. B. literal)
- `.env` (mit `OPENROUTER_API_KEY`) wird per `.gitignore` ausgeschlossen

## Aktueller task_progress-Stand

- ✅ Pipeline steht (Setup + 18 Kapitel extrahiert)
- ✅ Status & Logfiles etabliert
- ✅ Namensschreibweise festgelegt: Stil A (Transliteration)
- ✅ Pilot-Kapitel 1 in zwei Versionen angefangen
- ✅ Namens-Kandidaten-Tabelle angelegt
- ✅ Git initialisiert, Commits lokal
- ✅ **OpenRouter-Provider-System** (Code, Config, Doku, Dry-Run)
- ⏳ Erster echter OpenRouter-Run mit API-Key
- ⏳ Wartet auf Feedback zum Pilot (Ton, Stil, Namen)
- ⏳ Rest von Kapitel 1 fertigstellen
- ⏳ Vergleichsdatei `001-compare.md`
