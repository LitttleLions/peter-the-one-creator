# peter-the-one

Regelbasierte kapitelweise Übersetzung literarischer Werke. Pipeline
zum kapitelweisen Übersetzen von Romanen aus einer Quellsprache (aktuell
Russisch) ins Deutsche, mit optionaler Anwendung eines Regelkatalogs
und Konfigurierbarkeit pro Buch.

**Aktuelles Buch:** „Peter der Erste" (Пётр Первый) von Alexei Tolstoi.

## Was das Projekt ist und wozu

Eine Python-CLI-Pipeline, die

- Bücher in beliebiger Ausgangssprache kapitelweise einliest (RTF/DOCX)
- pro Kapitel den Status trackt (`pending` → `in_progress` → `done` / `needs_review`)
- pro Kapitel eine oder mehrere Übersetzungsversionen erzeugt, optional
  unter Anwendung eines Regelkatalogs (siehe `logic/`)
- Logfiles pro Kapitel schreibt
- über `config/books.yaml` mehrere Bücher parallel verwalten kann
- externe LLM-Provider (z. B. OpenRouter) über `.env` anbindet (geplant)
- den Stilmodus pro Buch umschaltbar macht: `literal` / `middle` / `stylized`

## Aktueller Stand (Juni 2026)

**Peter I – Buch 01**

- 18 Kapitel erkannt (Книга 1: 7, Книга 2: 5, Книга 3: 6)
- 228.951 Wörter Original (russisch)
- Status: 1/18 (5.6 %) – Kapitel 1 in `in_progress` (Pilotphase)

**Was existiert bereits:**

- `config/books.yaml` (Bücher-Registry, Namenskonvention)
- `config/pipeline.yaml` (Pipeline-Defaults, Heading-Patterns)
- `config/rules-overrides.yaml` (Stil-Modus pro Buch, Naming-Reminder)
- `config/naming_proposal_peter_i.md` (drei Stile A/B/C)
- `config/naming_choices.yaml` (Kandidaten-Tabelle pro Name, zur Diskussion)
- `tools/extract_chapters.py`, `status.py` + `tools/lib/` (3 Module + `__init__.py`)
- `output/Peter I/chapters/001-source.md` … `018-source.md`
- `output/Peter I/chapters/001-translation-v1-stylized.md` (Pilot, ~2.700 Wörter, Szenen 1–3)
- `output/Peter I/chapters/001-translation-v2-literal.md` (Pilot, ~2.700 Wörter, Szenen 1–5)
- `status/Peter I.status.json` (18 Einträge)
- `status/logs/Peter I/001.log.md` (Pilot-Log)

**Was offen ist:**

- Kapitel 1: Szenen 4–19 (v1) und 6–19 (v2) stehen noch aus
- Kapitel 2–18: noch nicht übersetzt
- Vergleichsdatei `001-compare.md` (Szene 1 nebeneinander)
- Namenslogik final festlegen
- OpenRouter-Provider-System (geplant, nächster Schritt)
- LLM-Client-Schicht: aktuell ist `provider: "cline"` nur dokumentiert
  in `pipeline.yaml`; tatsächliche Übersetzungen passieren im Chat

## Verzeichnisstruktur

```
.
├── AGENTS.md                    # zentrale KI-Kontextdatei (Pflicht)
├── CLAUDE.md                    # Verweis auf AGENTS.md
├── .gitignore                   # Müll, Secrets, Python-Build
├── .gitattributes               # LF-Zeilenenden, Binärflags
├── README.md                    # dieses Dokument
├── requirements.txt             # Python-Abhängigkeiten
│
├── books/                       # Original-Bücher (nicht verändern!)
│   ├── Peter I - Buch 01 - royallib.ru.doc
│   └── Peter I - Buch 01 - royallib.ru.rtf   # Duplikat, auf Wunsch behalten
├── logic/                       # Original-Regelkataloge (nicht verändern!)
│   └── peter the one - Regeln 001.txt
│
├── config/                      # Konfiguration
│   ├── books.yaml               # Bücher-Registry
│   ├── pipeline.yaml            # Pipeline-Defaults (Encoding, Heading-Patterns)
│   ├── rules-overrides.yaml     # Pro-Buch-Overrides (style_mode, naming)
│   ├── naming_proposal_peter_i.md
│   └── naming_choices.yaml      # Namens-Kandidaten-Tabelle pro Person
│
├── tools/                       # Python-CLI
│   ├── extract_chapters.py      # Buch einlesen, Kapitel extrahieren
│   ├── status.py                # Status-CLI (summary, list, next, mark, reset)
│   └── lib/
│       ├── rtf_parser.py        # striprtf-basiert, Heading-Pattern (Книга/Глава/Часть)
│       ├── status_manager.py    # JSON-Status (BookState, ChapterState)
│       └── log_writer.py        # Pro-Kapitel-Log als Markdown
│
├── output/                      # Übersetzungen (im Repo)
│   └── Peter I/
│       └── chapters/
│           ├── 001-source.md
│           ├── 001-translation-v1-stylized.md   # regelbasiert
│           ├── 001-translation-v2-literal.md    # regelfrei
│           └── ...
│
└── status/                      # Status & Logs (im Repo)
    ├── Peter I.status.json
    └── logs/
        └── Peter I/
            └── 001.log.md
```

## Einrichtung

```bash
pip install -r requirements.txt
```

## Benutzung

```bash
# Buch einlesen, Kapitel extrahieren, Status initialisieren
python tools/extract_chapters.py

# Status anzeigen
python tools/status.py summary
python tools/status.py list
python tools/status.py next

# Kapitel zur Bearbeitung markieren
python tools/status.py mark 001 in_progress

# Nach dem Übersetzen:
python tools/status.py mark 001 done --words 2300 --title-de "Erstes Kapitel"
# oder:
python tools/status.py mark 001 needs_review
```

## Derzeitige Handhabung (Workflow pro Kapitel)

1. **Markieren**: `python tools/status.py mark NNN in_progress`
2. **Übersetzen**: Russisches Quellkapitel aus `output/.../chapters/NNN-source.md` lesen,
   deutsche Version schreiben (z. B. `NNN-translation-v1-stylized.md` und/oder
   `NNN-translation-v2-literal.md`).
3. **Loggen**: Pro Version ein Eintrag in `status/logs/<Buch>/NNN.log.md`
   (welche Regeln, welche Stilmodi, schwierige Stellen, Anpassungen).
4. **Markieren**: `mark NNN done --words <Wortzahl> --title-de "…"`
   oder `mark NNN needs_review` (bei Pilot/Review).
5. **Konsistenz-Check** nach jeweils 3–5 Kapiteln (Namen, Ton, Regelanwendung).
6. **Regelanpassungen** dokumentiert in `config/rules-overrides.yaml` pro Buch.

## Stil-Modi

In `config/rules-overrides.yaml` pro Buch einstellbar unter `style_mode`:

- `literal` — wörtliche Übersetzung, keine Ausschmückung, Regelwerk
  wird nicht angewendet (außer Namensschreibweise). Vergleichbar mit
  `v2-literal.md`.
- `middle` — leichte Stilisierung, ausgewählte Regeln greifen
  (noch zu definieren, wenn Bedarf entsteht).
- `stylized` — volle Anwendung des Regelwerks (Sanderson-Struktur +
  Sorkin-Konfliktdynamik + sensorische Details + innere Monologe
  + Szene/Sequel). Vergleichbar mit `v1-stylized.md`.

## Namensschreibweise

- Stil A (Duden-Transliteration) ist für Peter I bestätigt
  (Пётр→Peter, Иван→Iwan, Софья→Sofja, Алексей→Alexei, etc.).
- Diskussion einzelner Namen läuft in `config/naming_choices.yaml`
  (Stand: Iwanka vs. Iwan, Zigeuner, Alexander Menschikow, etc.).
- Bei Anpassungen pro Kapitel: in `status/logs/.../NNN.log.md`
  unter „Regelanpassungen" vermerken.

## Wichtige Regeln für neue Mitwirkende

- `AGENTS.md` zuerst lesen – dort sind die Konventionen und Pfade
  dokumentiert.
- `logic/`-Dateien sind **heilig** – nie ohne Rückfrage ändern.
- `books/`-Dateien sind **heilig** – nie ohne Rückfrage ändern
  (auch nicht „offensichtliche Duplikate" wie `.rtf` neben `.doc`).
- Status & Logfiles immer über die CLI ändern, nie direkt in JSON-Dateien.
- Im Zweifel nachfragen, nicht still annehmen.

## Geplante nächste Schritte (Roadmap)

1. **OpenRouter-Provider anbinden** – `.env` mit `OPENROUTER_API_KEY`,
   pro Buch ein anderes Modell wählbar (`config/books.yaml: ai.model`).
2. **`tools/translate_chapter.py`** – ruft OpenRouter auf, schreibt
   Übersetzungs-MD und Log automatisch.
3. **`tools/compare_chapters.py`** – erzeugt `001-compare.md` mit
   nebeneinander-Darstellung (v1 vs v2).
4. **Kapitel 1 fertigstellen** (Szenen 4–19), dann iterative Phase
   ab Kapitel 2.
5. **Namenslogik final festlegen** (Diskussion in `naming_choices.yaml`).
