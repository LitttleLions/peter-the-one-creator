# Onboarding-Prompt Fuer Neuen Chat

Du arbeitest im Repo **peter-the-one**. Antworte und dokumentiere auf Deutsch,
sofern nichts anderes gewuenscht ist.

## Pflicht Zuerst

1. Lies `AGENTS.md`.
2. Lies `README.md`.
3. Pruefe den Stand, z. B.:

```bash
python tools/status.py --book peter-i-buch-01 summary
python tools/status.py --book anna-karenina summary
```

## Projekt In Einem Satz

Python-Pipeline fuer szenenweise literarische Uebersetzung mit
buchzentrierter Struktur, Style-Profilen, OpenRouter, Prompt-Datei-Modus,
Workspace-KI-Modus, Dashboard und DOCX-/EPUB-Export.

## Harte Regeln

- Buchpakete liegen unter `books/<book-id>/`.
- Originalquellen in `books/<book-id>/source/` nicht ohne Rueckfrage aendern,
  loeschen, umbenennen oder bereinigen.
- `logic/` nicht ohne Rueckfrage bearbeiten.
- Produktive Style-Profile liegen in `books/<book-id>/styles/*.md`.
- Keine Secrets ins Repo.

## Struktur

```text
books/<book-id>/
  book.yaml
  export.yaml
  names.yaml
  source/
  assets/covers/
  styles/
  work/
    chapters/
    scenes/ru/
    scenes/de/<style>/
    assembled/<style>/
    prompts/
    style-tests/
    legacy/
  exports/<style>/<chapter|book>/
  status/status.json
  status/logs/
```

Aktuelle Pakete:

- `books/peter-i-buch-01/`
- `books/anna-karenina/`

Alte zentrale Configs liegen nur noch als Migrationsmaterial in
`config/legacy/`.

Fuer neue Buecher gibt es eine kopierbare KI-Vorlage:
`docs/book-metadata-prompt.md`. Sie wird auch im Dashboard-Tab `Buch-Setup`
angezeigt und hilft beim Sammeln von Metadaten fuer `book.yaml`,
`export.yaml` und `names.yaml`.

## Pipeline

```bash
python tools/extract_chapters.py --book anna-karenina
python tools/extract_scenes.py --book anna-karenina --chapter 001
python tools/translate_chapter.py --book anna-karenina --chapter 001 --style stil-01-original --provider openrouter
python tools/translate_batch.py --book anna-karenina --from 001 --to 005 --style stil-01-original --provider prompt_file --dry-run
python tools/translate_batch.py --book anna-karenina --missing --style stil-01-original --provider openrouter --assemble-after
python tools/assemble_chapter.py --book anna-karenina --chapter 001 --style stil-01-original
python tools/export_manuscript.py --book anna-karenina --scope chapter --chapter 001 --style stil-01-original --format all --allow-partial
```

`translate_batch.py` bereitet fehlende RU-Arbeitseinheiten vor und startet
dann mehrere Uebersetzungs-/Prompt-Laeufe. Es baut nur mit
`--assemble-after` Kapiteldateien zusammen und exportiert keine DOCX/EPUB.

## Provider

- `openrouter`: echter API-Call, schreibt DE-Szenen.
- `prompt_file`: schreibt Prompt-Dateien nach `work/prompts/`.
- `workspace_ai`: schreibt Arbeitsauftraege fuer eine KI im Repo.

## Struktur Und Namen

`book.yaml` enthaelt `structure.mode`:

- `scenes`: Kapitel mit echten Szenen, z. B. Peter I.
- `chapter_as_scene`: jedes Kapitel ist eine Arbeitseinheit, z. B.
  Anna Karenina.

`book.yaml.display` steuert die Leseranzeige im Export: Anna zeigt
ausgeschriebene Kapitelueberschriften ohne Szenenmarker, Peter zeigt
ausgeschriebene Kapitelueberschriften und zentrierte Szenenzahlen.

`names.yaml` enthaelt buchlokale Namen und Begriffe. Die Liste wird kompakt in
Prompts injiziert. Pflege sie im Dashboard-Tab **Namen** oder direkt in der
YAML-Datei.

## Dashboard

```bash
streamlit run tools/dashboard.py
```

URL: `http://localhost:8501`

Design-Referenz: `docs/dashboard-design-system.md`.

## Export Und Cover

Export-Metadaten liegen in `books/<book-id>/export.yaml`.
Coverpfade sind relativ zum Buchpaket, z. B.
`assets/covers/annakarenina.png`.
Die Frontmatter-Folge wird dort ebenfalls gesteuert: Coverbild, Titelseite,
Zusammenfassung, Leben des Autors, danach Textbeginn.

Anna Karenina hat aktuell:

```text
books/anna-karenina/assets/covers/annakarenina.png
```

## Wichtige Dateien

- KI-Kontext: `AGENTS.md`
- Menschliche Uebersicht: `README.md`
- Buchresolver: `tools/lib/book_project.py`
- Pfadlogik: `tools/lib/output_paths.py`
- Dashboard: `tools/dashboard.py`
- Modellkatalog: `config/models.yaml`
- Pipeline-Defaults: `config/pipeline.yaml`
