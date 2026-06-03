# AGENTS.md — Kontext für KI-Werkzeuge

> Dies ist die zentrale Kontextdatei. CLAUDE.md verweist auf diese Datei.

## Was dieses Projekt ist

Regelbasierte kapitelweise Übersetzung literarischer Werke. Aktuelles
Buch: Alexei Tolstois „Peter der Erste" (RU → DE) gemäß Regelkatalog
in `logic/peter the one - Regeln 001.txt`. Python-CLI-Pipeline mit
Status-, Log- und RTF-Parser-Modulen.

## Struktur (Kurzüberblick)

- `books/` — Originalbücher (nicht verändern)
- `logic/` — Originale Regelkataloge (nicht verändern)
- `config/` — Bücher-Registry, Pipeline-Einstellungen, Regel-Overrides
- `tools/` — Python-CLI (`extract_chapters.py`, `status.py`, `lib/`)
- `output/<Buch>/chapters/` — Übersetzungen je Kapitel (`*-source.md`,
  `*-translation.md`)
- `status/` — Status-JSON + Logfiles pro Kapitel
- `requirements.txt` — Python-Abhängigkeiten
- `README.md` — für Menschen

## Konventionen

- `AGENTS.md` ist die einzige Quelle der Wahrheit; `CLAUDE.md` ist nur ein Verweis.
- Dokumentation in Markdown.
- Datei-/Ordnernamen: ASCII, klein, Bindestrich, keine Umlaute/Leerzeichen —
  die bestehende Konvention `Peter I` wird respektiert.
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
- Vor jeder Kapitelübersetzung in `config/books.yaml` prüfen, welcher
  Stilmodus aktiv ist (`literal` / `middle` / `stylized`).
- Kapitel nur in dem Stil übersetzen, der in `config/books.yaml` und
  `config/rules-overrides.yaml` gesetzt ist.
- Keine automatischen Löschungen oder destruktiven Operationen ohne
  ausdrückliche Freigabe.
- Im Zweifel: kurze Rückfrage, keine stillen Annahmen.
- Mülldateien (z. B. `final_status.txt`, `status_mark*.txt`, `debug_*.txt`)
  im Repo-Root werden per `.gitignore` ausgeschlossen und **nicht**
  im Repo committet. Sie liegen bleiben lassen ist in Ordnung; ob sie
  am Ende gelöscht werden, entscheidet der Nutzer.

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
- Status-Datei: `status/Peter I.status.json`
- Log-Verzeichnis: `status/logs/Peter I/`
