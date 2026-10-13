# peter-the-one

## Zweck und Nutzer

Werkbank für Motivatier Classics: literarische Werke werden kapitel- und szenenweise übersetzt (überwiegend `ru` nach `de`, teils `ja` oder `pl` nach `de`) oder als deutsches Original redigiert und danach als EPUB, DOCX, A5-PDF und KDP-Taschenbuch ausgegeben. Nutzer ist die Redaktion selbst, nicht ein öffentliches Mandantenportal. Jedes Buch ist ein Paket unter `books/<id>/` mit eigener `book.yaml` und `export.yaml`.

## Tatsächlich vorhandene Funktionen

Geprüft am Commit `d89376719f325a4b9974752d2b779bb82fd4f06b` auf `main`. Der Arbeitsbaum ist zusätzlich verändert (siehe Manifest). Die folgenden Punkte sind im Commit im Code vorhanden:

- Buchfindung über `books/*/book.yaml` in `tools/lib/book_project.py`. Pipeline: Kapitel und Szenen extrahieren, übersetzen, zusammensetzen (`tools/extract_chapters.py`, `tools/translate_chapter.py`, `tools/assemble_chapter.py`).
- Deterministischer Regelcheck ohne LLM (`tools/review_manuscript.py`, `tools/lib/review_checks.py`). Der Export bricht bei ERROR ab (`tools/export_manuscript.py`, `preflight_review_gate`); Bypass nur mit `--allow-review-errors`.
- Exportformate `docx`, `epub`, `pdf` (A5-Vorschau), `paperback` und `paperback-complete` (`EXPORT_FORMATS` in `tools/export_manuscript.py`). Taschenbuch: Trim, Satzprofil und Bildmodus (`tools/lib/print_spec.py`, `print_pdf.py`, `print_wrap.py`).
- Dashboard FastAPI und React (`webapp/`, Start `tools/start_dashboard.py`) und öffentliche Regal-Website (`webpage/`, `tools/build_shelf_website.py`). Freigabe nur über top-level `website:` in `export.yaml`.
- Marketingpaket ohne Veröffentlichung (`tools/export_marketing.py`). Es spricht keine Plattform-API an.
- Übernahme von DE-Originalen aus einem RomanForge-Markdown-Export (`tools/import_markdown_original.py`: `--compare`, `--accept`, `--keep`, `--new`). Am Prüfcommit enthält das Repo 13 Buchpakete, darunter `books/ashkara/`.

Im Commit nicht enthalten, nur lokal uncommittet: Leerseitenmessung im PDF-Satz, zwei Bildauflösungen (`assets/master/` und `assets/chapter/`), Git-Schalter für große Medien und das Buchpaket `books/der-lotse/`.

## Aufbau und Integrationen

Python-CLIs unter `tools/`, gemeinsame Bibliothek unter `tools/lib/`. Konfiguration: `config/pipeline.yaml`, `config/models.yaml`, `config/print.yaml`, `config/marketing.yaml`. Übersetzungsaufrufe gehen an OpenRouter oder lokales Ollama; Prompts können auch nur als Datei geschrieben werden. EPUB braucht Pandoc, PDF und Taschenbuch Playwright-Chromium. Kapitelbilder optional über die Higgsfield-CLI. Amazon-Store-Links stehen als `website.amazon_url` in `export.yaml` (bei Aëlita, Arsenjew und Peter I gesetzt). Ein automatischer KDP-Upload ist nicht implementiert.

## Interessante Bausteine

Siehe `docs/reuse.md`: Release-Gate, Taschenbuchsatz, RomanForge-Übernahme, Marketingexport ohne Versand.

## Grenzen und offene Punkte

- Kein öffentliches KDP-API. Ein Adapter ist nur geplant und nicht Teil dieses Commits.
- `docs/kampagne-kdp-automatisierung.md` (2026-06-17) beschreibt einen nicht gebauten Kampagnenweg und ist nicht der aktuelle Export.
- Übersetzungsläufe und Higgsfield nur nach ausdrücklicher Freigabe. Originalquellen unter `books/<id>/source/` und `logic/` bleiben unangetastet.
- Live-Status einzelner Titel (Amazon, Kindle-Preview) steht in `docs/HANDOVER.md` und `export.yaml`. In dieser Aufnahme wurde kein Amazon-Konto und kein laufendes Dashboard geprüft.
- Der geprüfte Commit reproduziert den uncommitteten Arbeitsbaum nicht.
