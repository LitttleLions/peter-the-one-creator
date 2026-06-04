# AGENTS.md — Kontext für KI-Werkzeuge

> Dies ist die zentrale Kontextdatei. CLAUDE.md verweist auf diese Datei.
> Lese zuerst diese Datei und die README, dann beginne mit der Arbeit.

## Was dieses Projekt ist

Regelbasierte kapitelweise Übersetzung literarischer Werke. Aktuelles
Buch: Alexei Tolstois „Peter der Erste" (RU → DE) gemäß Regelkatalog
in `logic/peter the one - Regeln 001.txt`. Python-CLI-Pipeline mit
Status-, Log- und RTF-Parser-Modulen. Übersetzungs-Stil pro Buch
umschaltbar (`literal` / `middle` / `stylized`); die operativen
System-Prompts pro Modus liegen in `config/style_modes.yaml`. Anbindung
an externe LLM-Provider (OpenRouter) ist implementiert
(`tools/translate_chapter.py`).

## Struktur (Kurzüberblick)

- `books/` — Originalbücher (nicht verändern; auch keine „Duplikate" eigenmächtig löschen)
- `logic/` — Originale Regelkataloge (nicht verändern)
- `config/` — Bücher-Registry, Pipeline-Einstellungen, Regel-Overrides, Namenslogik
  - `books.yaml` — Bücher-Registry (Pflicht, pro Buch `id`, Stilmodus, `ai.*`-Block)
  - `pipeline.yaml` — Pipeline-Defaults (Encoding, Heading-Patterns, `ai_defaults`)
  - `rules-overrides.yaml` — Pro-Buch-Overrides (`style_mode`, `naming_reminder`, `custom_instructions`)
  - `style_modes.yaml` — **System-Prompts pro Stilmodus** (operativ, nicht nur Marker)
  - `models.yaml` — **Katalog verfügbarer OpenRouter-Modelle** (id, name, provider, description; `default_for: [book-id]` markiert das Default-Modell pro Buch)
  - `naming_proposal_peter_i.md` — drei Stile A/B/C
  - `naming_choices.yaml` — Kandidaten-Tabelle pro Person (zur Diskussion)
- `tools/` — Python-CLI
  - `extract_chapters.py` — Buch einlesen, Kapitel extrahieren
  - `status.py` — Status-Übersicht und -Manipulation
  - `translate_chapter.py` — OpenRouter-Übersetzung pro Kapitel (Szene oder Ganzes)
  - `lib/rtf_parser.py` — striprtf-basiert, Heading-Pattern (Книга/Глава/Часть/Эпилог/Пролог)
  - `lib/status_manager.py` — JSON-Status (`BookState`, `ChapterState`)
  - `lib/log_writer.py` — Pro-Kapitel-Log als Markdown
  - `lib/openrouter_client.py` — OpenRouter-Chat-Completion-Client (httpx, python-dotenv)
  - `lib/style_prompts.py` — Lädt `config/style_modes.yaml`, baut System-/User-Messages
  - `lib/scene_splitter.py` — Splittet MD in Szenen anhand von `## N`-Headings
  - `lib/models_registry.py` — Lädt `config/models.yaml`, validiert Modell-IDs
  - `lib/degeneration.py` — Erkennt Token-Loops, Sprach-Drift, Mojibake, Endlos-Sätze im LLM-Output
- `output/<Buch>/chapters/` — Übersetzungen je Kapitel
  - `NNN-source.md` (Originaltext RU)
  - `NNN-translation-vN-stil.md` (z. B. `v1-stylized`, `v2-literal`, `v3-stylized` …)
  - ggf. mehrere Versionen pro Stil (wird vom Tool automatisch nummeriert)
- `status/` — Status-JSON + Logfiles pro Kapitel
  - `<Buch>.status.json` (alle Kapitel mit Status)
  - `logs/<Buch>/NNN.log.md` (was wurde gemacht, Stil, Probleme, Anpassungen)
- `requirements.txt` — Python-Abhängigkeiten (pyyaml, python-docx, python-dotenv, httpx)
- `.env` (lokal) / `.env.example` (Vorlage) — OpenRouter-API-Key
- `README.md` — für Menschen
- `ONBOARDING.md` — Kurzfassung für neuen Chat

## Konventionen

- `AGENTS.md` ist die einzige Quelle der Wahrheit; `CLAUDE.md` ist nur ein Verweis.
- Dokumentation in Markdown.
- Datei-/Ordnernamen: ASCII, klein, Bindestrich, keine Umlaute/Leerzeichen —
  die bestehende Konvention `Peter I` wird respektiert.
- Versions-Suffix für Übersetzungen: `NNN-translation-v1-stylized.md`,
  `NNN-translation-v2-literal.md` etc. (Reihenfolge der Erstellung).
- Keine Secrets im Repo; Schlüssel in `.env` (per `.gitignore` ausgeschlossen).
- Zeilenenden via `.gitattributes` auf LF (Cross-OS).
- Quellcode-Zeilen möglichst unter 500 Zeichen.
- `AGENTS.md` kurz und von Hand gepflegt halten — nicht automatisch volllaufen lassen.
- Antworten und Doku auf Deutsch, sofern nicht anders gewünscht.

## Arbeitsweise für die KI

- Vor Änderungen am Originalbuch (`books/`) oder Originalregeln (`logic/`)
  **immer** beim Nutzer nachfragen.
- `books/` ist tabu, auch wenn etwas wie ein Duplikat aussieht. Niemals
  Dateien in `books/` eigenmächtig löschen, ersetzen, verschieben oder
  umbenennen — auch keine `.rtf` neben einer `.doc` — auch dann nicht,
  wenn ein Hygiene-Scan sie als überflüssig deklariert. Im Zweifel:
  liegen lassen, dem Nutzer melden, ihn entscheiden lassen.
- Große Dateien in `books/` (10+ MB) sind normal und kein Fehler — sie
  sind Eingabedaten, nicht zu „reparierender" Quellcode.
- Auch Output-Dateien (z. B. `output/.../*.md`) können groß werden
  (tausende Zeilen pro Kapitel). Das ist normal und kein Grund für
  Korrekturmaßnahmen oder Zeilenlängen-Empörung.
- Status & Logfiles werden über `python tools/status.py ...` aktualisiert,
  nicht direkt in JSON-Dateien herumschreiben.
- Vor jeder Kapitelübersetzung in `config/books.yaml` und
  `config/rules-overrides.yaml` prüfen, welcher Stilmodus aktiv ist
  (`literal` / `middle` / `stylized`).
- Pro Kapitel: in `status/logs/<Buch>/NNN.log.md` eintragen, welche Regeln
  angewendet wurden, welche Stellen schwierig waren, welche Anpassungen
  gemacht wurden.
- Keine automatischen Löschungen oder destruktiven Operationen ohne
  ausdrückliche Freigabe.
- Im Zweifel: kurze Rückfrage, keine stillen Annahmen.
- Mülldateien (z. B. `final_status.txt`, `status_mark*.txt`, `debug_*.txt`)
  im Repo-Root werden per `.gitignore` ausgeschlossen und **nicht**
  im Repo committet. Sie liegen bleiben lassen ist in Ordnung; ob sie
  am Ende gelöscht werden, entscheidet der Nutzer.

## Stil-Modi (Übersetzung)

In `config/books.yaml` pro Buch einstellbar unter `style_mode`. Die
**operativen System-Prompts** pro Modus liegen in
`config/style_modes.yaml`. Dort ist pro Modus auch `temperature` und
`rules_append` (ob die Regeln aus `logic/` an den User-Prompt
angehängt werden) konfiguriert.

- `literal` — wörtlich, keine Ausschmückung, Regelwerk wird **nicht**
  angehängt (`rules_append: false`). Vergleichbar mit `v2-literal.md`.
- `middle` — leichte Stilisierung, ausgewählte Regeln greifen
  (`rules_append: true`).
- `stylized` — volle Anwendung des Regelwerks (Sanderson-Struktur +
  Sorkin-Konfliktdynamik + sensorische Details + innere Monologe
  + Szene/Sequel + Lede-Block). `rules_append: true`.
  Vergleichbar mit `v1-stylized.md`.

Aktuell für Peter I auf `stylized` gestellt
(siehe `config/books.yaml: style_mode`). Der ältere Onboarding-Hinweis
„auf `literal` gestellt" ist **veraltet**.

## Namensschreibweise

- Stil A (Duden-Transliteration) ist für Peter I bestätigt
  (Пётр→Peter, Иван→Iwan, Софья→Sofja, Алексей→Alexei, etc.).
- Diskussion einzelner Namen läuft in `config/naming_choices.yaml`.
- Bei Anpassungen pro Kapitel: in `status/logs/.../NNN.log.md` unter
  „Regelanpassungen" vermerken.

## Befehle (Schnellreferenz)

```bash
pip install -r requirements.txt

# --- Setup (einmalig) ---
cp .env.example .env                       # dann OPENROUTER_API_KEY eintragen
python tools/extract_chapters.py          # Buch einlesen, Kapitel extrahieren

# --- Status ---
python tools/status.py summary             # Fortschritt
python tools/status.py list                # Kapitel-Liste
python tools/status.py next                # nächstes pending Kapitel
python tools/status.py mark 001 in_progress
python tools/status.py mark 001 done --words 2300 --title-de "..."
python tools/status.py mark 001 needs_review
python tools/status.py reset 001

# --- OpenRouter-Übersetzung (NEU) ---
python tools/translate_chapter.py --chapter 001 --style stylized --dry-run
python tools/translate_chapter.py --chapter 001 --style stylized
python tools/translate_chapter.py --chapter 001 --style stylized --auto-status
python tools/translate_chapter.py --chapter 001 --style literal --granularity chapter
python tools/translate_chapter.py --chapter 001 --style middle --model openai/gpt-4o
```

`--auto-status` setzt `in_progress` zu Beginn und am Ende
`needs_review` (mit `--no-review` direkt `done`).

## Wichtige Pfade (Kurzform)

- Originalbuch: `books/Peter I - Buch 01 - royallib.ru.doc`
- Regelwerk: `logic/peter the one - Regeln 001.txt` (heilig!)
- Bücher-Registry: `config/books.yaml` (inkl. `ai.*`-Block pro Buch)
- Pipeline-Defaults: `config/pipeline.yaml` (inkl. `ai_defaults`)
- Regel-Overrides: `config/rules-overrides.yaml`
- **Stilmodus-Prompts: `config/style_modes.yaml` (NEU)**
- **Modell-Katalog: `config/models.yaml` (NEU)**
- Namensschreibweise-Vorschlag: `config/naming_proposal_peter_i.md`
- Namens-Kandidaten-Tabelle: `config/naming_choices.yaml`
- OpenRouter-Client: `tools/lib/openrouter_client.py`
- OpenRouter-Key: `.env` (per `.gitignore` ausgeschlossen)
- Status-Datei: `status/Peter I.status.json`
- Log-Verzeichnis: `status/logs/Peter I/`
- Pilot-Übersetzungen Kapitel 1: `output/Peter I/chapters/001-translation-v1-stylized.md` und `001-translation-v2-literal.md`
- Pilot-Log Kapitel 1: `status/logs/Peter I/001.log.md`
- Onboarding-Kurzfassung: `ONBOARDING.md`

## Geplante nächste Schritte (Roadmap)

1. ✅ **OpenRouter-Provider anbinden** – `.env` mit `OPENROUTER_API_KEY`,
   pro Buch ein anderes Modell wählbar (`config/books.yaml: ai.model`).
2. ✅ **`tools/translate_chapter.py`** – ruft OpenRouter auf, schreibt
   Übersetzungs-MD und Log automatisch (Dry-Run getestet).
3. **Erster echter OpenRouter-Run** – mit echtem API-Key validieren.
4. **`tools/compare_chapters.py`** – erzeugt `001-compare.md` mit
   nebeneinander-Darstellung (v1 vs v2).
5. **Kapitel 1 fertigstellen** (Szenen 4–19), dann iterative Phase
   ab Kapitel 2.
6. **Namenslogik final festlegen** (Diskussion in `naming_choices.yaml`).
7. (Bonus) **Scene-Splitter verbessern** – Szenen-Headings in
   `NNN-source.md` einbauen, damit die Pipeline wirklich szeneweise
   übersetzen kann.
