# Wiederverwendbare Lösungen

Pfade ab Repo-Wurzel. Geprüft wurde der Code am lokalen Commit `d89376719f325a4b9974752d2b779bb82fd4f06b`. Die genannten Tests wurden in dieser Aufnahme nicht erneut ausgeführt. Keiner der Bausteine wurde hier in ein anderes Repository übernommen.

## Release-Gate vor dem Export

- Zweck: Ein Manuskript mit deterministischen Fehlern (fehlende Szene, Kyrillisch, Encoding, starke Raffung) nicht als EPUB oder Taschenbuch ausgeben.
- Quellpfade: `tools/review_manuscript.py`, `tools/lib/review_checks.py`, `tools/export_manuscript.py` (`preflight_review_gate`).
- Aufruf: `py -3 tools/review_manuscript.py --book <id> --style <style> --all --llm none --fail-on-errors`. Der Export ruft dasselbe Gate auf und endet mit Exit 2, solange ERROR größer als 0 ist.
- Abhängigkeiten: Python, Buchpaket unter `books/<id>/`. Kein LLM, wenn `--llm none`.
- Transferart: Anpassung. Die Fehlerklassen sind auf diese Übersetzungspipeline zugeschnitten; das Muster „Check vor Ausgabe, Bypass nur explizit und protokolliert“ ist übertragbar.
- Grenzen: WARNING und INFO blockieren nicht. Buchweite Ausreißer (`length_outlier`) brauchen den Scope ganzes Buch. Das Gate prüft keine Druck-Seitenzahl.
- Prüfbelege: `tests/test_review_manuscript.py`, `tests/test_print_export.py` (Gate-Felder im Manifest). In dieser Aufnahme nicht erneut ausgeführt.

## Taschenbuchsatz mit Trim, Profil und Bildmodus

- Zweck: KDP-Innenleben, Lese-PDF und Umschlagbogen aus denselben deutschen Szenen erzeugen, ohne den E-Book-Export zu ersetzen.
- Quellpfade: `config/print.yaml`, `tools/lib/print_spec.py`, `tools/lib/print_css.py`, `tools/lib/print_pdf.py`, `tools/lib/print_wrap.py`.
- Aufruf: `py -3 tools/export_manuscript.py --book <id> --scope book --style <style> --format paperback --trim-size 5.5x8.5|6x9 --layout-profile classic|long_classic --illustration-mode full_page|inline`.
- Abhängigkeiten: Playwright-Chromium. Schrift `assets/print-fonts/eb-garamond/`. Druckcover nur `assets/covers/cover-print.*`, ohne Fallback auf das Kindle-Cover.
- Transferart: Referenzimplementierung.
- Grenzen: Cream-Limit 776 Seiten wird gewarnt, der Satz wird nicht automatisch gekürzt. `--format all` bleibt DOCX plus EPUB und erzeugt kein Taschenbuch. Leerseitenmessung und die 2k-Masterbilder liegen nur im uncommitteten Arbeitsbaum, nicht in diesem Prüfcommit.
- Prüfbelege: `tests/test_print_export.py`. In dieser Aufnahme nicht erneut ausgeführt.

## Übernahme eines DE-Originals aus Markdown

- Zweck: Einen RomanForge-Export gegen den vorhandenen Buchtext vergleichen und nur freigegebene Kapitel schreiben.
- Quellpfade: `tools/import_markdown_original.py`, `docs/uebernahme-romanforge.md`.
- Aufruf: `py -3 tools/import_markdown_original.py --book <id> --source <export.md> --compare`. Schreiben nur mit `--accept` oder `--keep` (höchstens fünf Kapitel) bzw. Neuanlage mit `--new`.
- Abhängigkeiten: Python, Buchpaketlayout. Kein OpenRouter.
- Transferart: Anpassung.
- Grenzen: Quelle muss Markdown mit Kapitelüberschriften sein. `--compare` bricht bei Konflikt, neuen oder entfallenen Kapiteln ab (Exit 2). Ein älteres Skript `tools/import_die_dritte_chronik.py` bleibt daneben bestehen.
- Prüfbelege: `tests/test_import_markdown_original.py`. In dieser Aufnahme nicht erneut ausgeführt.

## Marketingpaket ohne Versand

- Zweck: Kampagnentexte und ein Manifest aus den Buchmetadaten erzeugen, ohne eine Plattform zu beliefern.
- Quellpfade: `tools/export_marketing.py`, `tools/lib/marketing_campaign.py`, `config/marketing.yaml`.
- Aufruf: `py -3 tools/export_marketing.py --book <id>`. Ohne `--provider` kein API-Aufruf.
- Abhängigkeiten: `export.yaml` (`book`, top-level `website`, optional `marketing`). Ausgabe unter `books/<id>/exports/marketing/`.
- Transferart: Referenzimplementierung.
- Grenzen: Fehlende Amazon-URL oder Songs werden als offener Status ausgewiesen, nicht erfunden. Der Manuskriptexport hängt davon nicht ab.
- Prüfbelege: `tests/test_marketing_campaign.py`. In dieser Aufnahme nicht erneut ausgeführt.
