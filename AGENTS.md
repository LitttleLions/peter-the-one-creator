# AGENTS.md — Kontext für KI-Werkzeuge

> Dies ist die zentrale Kontextdatei. CLAUDE.md verweist auf diese Datei.
> Lese zuerst diese Datei und die README, dann beginne mit der Arbeit.

## Was dieses Projekt ist

Regelbasierte kapitelweise Übersetzung literarischer Werke. Aktuelles
Buch: Alexei Tolstois „Peter der Erste" (RU → DE) gemäß Regelkatalog
in `logic/peter the one - Regeln 001.txt`. Python-CLI-Pipeline mit
Status-, Log- und RTF-Parser-Modulen. Übersetzungs-Stil pro Buch
umschaltbar (`literal` / `middle` / `stylized`). Anbindung an externe
LLM-Provider (z. B. OpenRouter) ist geplant.

## Struktur (Kurzüberblick)

- `books/` — Originalbücher (nicht verändern; auch keine „Duplikate" eigenmächtig löschen)
- `logic/` — Originale Regelkataloge (nicht verändern)
- `config/` — Bücher-Registry, Pipeline-Einstellungen, Regel-Overrides, Namenslogik
  - `books.yaml` — Bücher-Registry (Pflicht, pro Buch `id`, Stilmodus, etc.)
  - `pipeline.yaml` — Pipeline-Defaults (Encoding, Heading-Patterns, AI-Block)
  - `rules-overrides.yaml` — Pro-Buch-Overrides (`style_mode`, `naming_reminder`, `custom_instructions`)
  - `naming_proposal_peter_i.md` — drei Stile A/B/C
  - `naming_choices.yaml` — Kandidaten-Tabelle pro Person (zur Diskussion)
- `tools/` — Python-CLI
  - `extract_chapters.py` — Buch einlesen, Kapitel extrahieren
  - `status.py` — Status-Übersicht und -Manipulation
  - `lib/rtf_parser.py` — striprtf-basiert, Heading-Pattern (Книга/Глава/Часть/Эпилог/Пролог)
  - `lib/status_manager.py` — JSON-Status (`BookState`, `ChapterState`)
  - `lib/log_writer.py` — Pro-Kapitel-Log als Markdown
- `output/<Buch>/chapters/` — Übersetzungen je Kapitel
  - `NNN-source.md` (Originaltext RU)
  - `NNN-translation-v1-stylized.md` (regelbasiert, mit Sanderson/Sorkin)
  - `NNN-translation-v2-literal.md` (regelfrei, wörtlich)
  - ggf. weitere Versionen mit Versions-Suffix
- `status/` — Status-JSON + Logfiles pro Kapitel
  - `<Buch>.status.json` (alle Kapitel mit Status)
  - `logs/<Buch>/NNN.log.md` (was wurde gemacht, Stil, Probleme, Anpassungen)
- `requirements.txt` — Python-Abhängigkeiten
- `README.md` — für Menschen

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

In `config/rules-overrides.yaml` pro Buch einstellbar unter `style_mode`:

- `literal` — wörtlich, keine Ausschmückung, Regelwerk wird nicht angewendet
  (außer Namensschreibweise). Vergleichbar mit `v2-literal.md`.
- `middle` — leichte Stilisierung, ausgewählte Regeln greifen
  (zu definieren, wenn Bedarf entsteht).
- `stylized` — volle Anwendung des Regelwerks (Sanderson-Struktur +
  Sorkin-Konfliktdynamik + sensorische Details + innere Monologe
  + Szene/Sequel). Vergleichbar mit `v1-stylized.md`.

## Namensschreibweise

- Stil A (Duden-Transliteration) ist für Peter I bestätigt
  (Пётр→Peter, Иван→Iwan, Софья→Sofja, Алексей→Alexei, etc.).
- Diskussion einzelner Namen läuft in `config/naming_choices.yaml`.
- Bei Anpassungen pro Kapitel: in `status/logs/.../NNN.log.md` unter
  „Regelanpassungen" vermerken.

## Befehle (Schnellreferenz)

```bash
pip install -r requirements.txt
python tools/extract_chapters.py          # Buch einlesen, Kapitel extrahieren
python tools/status.py summary             # Fortschritt
python tools/status.py list                # Kapitel-Liste
python tools/status.py next                # nächstes pending Kapitel
python tools/status.py mark 001 in_progress
python tools/status.py mark 001 done --words 2300 --title-de "..."
python tools/status.py mark 001 needs_review
python tools/status.py reset 001
```

## Wichtige Pfade (Kurzform)

- Originalbuch: `books/Peter I - Buch 01 - royallib.ru.doc`
- Regelwerk: `logic/peter the one - Regeln 001.txt`
- Bücher-Registry: `config/books.yaml`
- Pipeline-Defaults: `config/pipeline.yaml`
- Regel-Overrides: `config/rules-overrides.yaml`
- Namensschreibweise-Vorschlag: `config/naming_proposal_peter_i.md`
- Namens-Kandidaten-Tabelle: `config/naming_choices.yaml`
- Status-Datei: `status/Peter I.status.json`
- Log-Verzeichnis: `status/logs/Peter I/`
- Pilot-Übersetzungen Kapitel 1: `output/Peter I/chapters/001-translation-v1-stylized.md` und `001-translation-v2-literal.md`
- Pilot-Log Kapitel 1: `status/logs/Peter I/001.log.md`

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
