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
- **externe LLM-Provider (OpenRouter) über `.env` anbindet** — implementiert
- den Stilmodus pro Buch umschaltbar macht: `literal` / `middle` / `stylized`
- die Stilmodi als **konkrete LLM-System-Prompts** in `config/style_modes.yaml`
  operationalisiert (nicht nur als Marker)

## Aktueller Stand (Juni 2026)

**Peter I – Buch 01**

- 18 Kapitel erkannt (Книга 1: 7, Книга 2: 5, Книга 3: 6)
- 228.951 Wörter Original (russisch)
- Status: 1/18 (5.6 %) – Kapitel 1 in `in_progress` (Pilotphase)

**Was existiert bereits:**

- `config/books.yaml` (Bücher-Registry, Namenskonvention, **AI-Block pro Buch**)
- `config/pipeline.yaml` (Pipeline-Defaults, Heading-Patterns, **AI-Defaults**)
- `config/rules-overrides.yaml` (Stil-Modus pro Buch, Naming-Reminder)
- `config/style_modes.yaml` (**neu** — System-Prompts pro Modus)
- `config/naming_proposal_peter_i.md` (drei Stile A/B/C)
- `config/naming_choices.yaml` (Kandidaten-Tabelle pro Name, zur Diskussion)
- `tools/extract_chapters.py`, `status.py`, `translate_chapter.py`
  + `tools/lib/` (5 Module: `rtf_parser`, `status_manager`, `log_writer`,
  `openrouter_client`, `style_prompts`, `scene_splitter`)
- `.env.example` (Vorlage für `OPENROUTER_API_KEY`)
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
- **OpenRouter-Provider implementiert, aber noch nicht mit echtem
  API-Key produktiv getestet** — Dry-Run funktioniert, der erste
  echte Run wartet auf deinen Key.

## Verzeichnisstruktur

```
.
├── AGENTS.md                    # zentrale KI-Kontextdatei (Pflicht)
├── CLAUDE.md                    # Verweis auf AGENTS.md
├── ONBOARDING.md                # Kurzfassung für neuen Chat
├── .env.example                 # Vorlage für OpenRouter-Key
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
│   ├── books.yaml               # Bücher-Registry (inkl. ai.* pro Buch)
│   ├── pipeline.yaml            # Pipeline-Defaults (Encoding, Heading-Patterns, AI)
│   ├── rules-overrides.yaml     # Pro-Buch-Overrides (style_mode, naming)
│   ├── style_modes.yaml         # System-Prompts pro Stilmodus (NEU)
│   ├── naming_proposal_peter_i.md
│   └── naming_choices.yaml      # Namens-Kandidaten-Tabelle pro Person
│
├── tools/                       # Python-CLI
│   ├── extract_chapters.py      # Buch einlesen, Kapitel extrahieren
│   ├── status.py                # Status-CLI (summary, list, next, mark, reset)
│   ├── translate_chapter.py     # OpenRouter-Übersetzung pro Kapitel (NEU)
│   └── lib/
│       ├── rtf_parser.py        # striprtf-basiert, Heading-Pattern (Книга/Глава/Часть)
│       ├── status_manager.py    # JSON-Status (BookState, ChapterState)
│       ├── log_writer.py        # Pro-Kapitel-Log als Markdown
│       ├── openrouter_client.py # OpenRouter-Chat-Completion-Client (NEU)
│       ├── style_prompts.py     # Prompt-Loader für style_modes.yaml (NEU)
│       └── scene_splitter.py    # Splittet MD in Szenen (NEU)
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

# OpenRouter-Key einrichten (einmalig):
cp .env.example .env
# .env editieren und OPENROUTER_API_KEY eintragen
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

# --- Manueller Workflow (Pilot) ---
# Russisches Quellkapitel aus output/.../chapters/001-source.md lesen,
# deutsche Version schreiben (z. B. 001-translation-v1-stylized.md
# und/oder 001-translation-v2-literal.md), dann:
python tools/status.py mark 001 done --words 2300 --title-de "Erstes Kapitel"
# oder:
python tools/status.py mark 001 needs_review

# --- OpenRouter-Workflow (NEU, ab jetzt möglich) ---
# Dry-Run (zeigt die fertigen Prompts, kein API-Call):
python tools/translate_chapter.py --chapter 001 --style stylized --dry-run

# Echter Lauf (schreibt z. B. 001-translation-v3-stylized.md,
#   nächste freie vN-Version, kein Überschreiben):
python tools/translate_chapter.py --chapter 001 --style stylized

# Mit Auto-Status (setzt in_progress / needs_review automatisch):
python tools/translate_chapter.py --chapter 001 --style stylized --auto-status

# Anderes Modell pro Lauf:
python tools/translate_chapter.py --chapter 001 --style middle \
    --model openai/gpt-4o

# Granularität: ganzes Kapitel in einem Call (statt Szene-für-Szene):
python tools/translate_chapter.py --chapter 001 --style literal \
    --granularity chapter
```

## Derzeitige Handhabung (Workflow pro Kapitel)

### Manueller Workflow (Pilot)

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

### OpenRouter-Workflow (automatisiert, NEU)

1. **Optional markieren**: `mark NNN in_progress` — kann auch das Tool
   selbst mit `--auto-status` machen.
2. **Übersetzen**: `python tools/translate_chapter.py --chapter NNN --style {literal|middle|stylized}`.
   - Lädt `config/style_modes.yaml` und baut System- + User-Prompt
   - Hängt die Regeln aus `logic/` an (nur bei `middle` / `stylized`)
   - Ruft OpenRouter auf (Modell aus `config/books.yaml: ai.model`)
   - Schreibt `output/.../chapters/NNN-translation-vN-<stil>.md`
     (nächste freie vN-Version pro Stil)
   - Schreibt `status/logs/<Buch>/NNN.log.md` mit Modell, Modus, Regeln,
     Token-Limits, schwierigen Stellen
   - Setzt Status auf `needs_review` (oder `done` mit `--no-review`)
3. **Review**: Mensch prüft das Ergebnis und korrigiert ggf. von Hand.
   Bei Bedarf: `mark NNN done`.

### Bekannte Einschränkung (Juni 2026)

Die `NNN-source.md`-Dateien haben **keine `## N`-Szenen-Headings** —
die Szenen-Trennung existiert nur in den bisherigen Pilot-Übersetzungen.
Der Scene-Splitter erkennt daher aktuell keine Szenen und behandelt das
ganze Kapitel als einen Block. Das ist für Kapitel mit ≤ 15k Wörtern
(Größenordnung von Buch 1) im `claude-3.5-sonnet`-Context (200k Tokens)
problemlos, aber suboptimal. Lösung für später: Szenen-Markup entweder
in `extract_chapters.py` einbauen oder einen manuellen Pre-Processing-Schritt.

## Stil-Modi

In `config/books.yaml` pro Buch einstellbar unter `style_mode`. Die
konkreten System-Prompts liegen in `config/style_modes.yaml`.

- `literal` — wörtliche Übersetzung, keine Ausschmückung, Regelwerk
  wird **nicht** an den Prompt angehängt (`rules_append: false`).
  Vergleichbar mit `v2-literal.md`.
- `middle` — leichte Stilisierung, ausgewählte Regeln greifen
  (`rules_append: true`).
- `stylized` — volle Anwendung des Regelwerks (Sanderson-Struktur +
  Sorkin-Konfliktdynamik + sensorische Details + innere Monologe
  + Szene/Sequel). Vergleichbar mit `v1-stylized.md`. Lede-Block
  vor Szene 1, beschreibende Szenen-Überschriften.

Pro Modus ist auch die **Temperatur** eingestellt (literal: 0.2,
middle: 0.35, stylized: 0.4), die bei Bedarf per
`--temperature <float>` überschrieben werden kann.

Aktuell für Peter I auf `stylized` gestellt
(siehe `config/books.yaml: style_mode`).

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

1. ✅ **OpenRouter-Provider anbinden** – `.env` mit `OPENROUTER_API_KEY`,
   pro Buch ein anderes Modell wählbar (`config/books.yaml: ai.model`).
2. ✅ **`tools/translate_chapter.py`** – ruft OpenRouter auf, schreibt
   Übersetzungs-MD und Log automatisch.
3. **Erster echter OpenRouter-Run** – Dry-Run ist getestet, jetzt
   brauchen wir einen Run mit echtem API-Key zur Validierung.
4. **`tools/compare_chapters.py`** – erzeugt `001-compare.md` mit
   nebeneinander-Darstellung (v1 vs v2).
5. **Kapitel 1 fertigstellen** (Szenen 4–19), dann iterative Phase
   ab Kapitel 2.
6. **Namenslogik final festlegen** (Diskussion in `naming_choices.yaml`).
