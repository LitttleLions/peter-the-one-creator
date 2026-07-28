# Motivatier Bücherregal

Interaktive Three.js-Regal-Website für Motivatier-Ausgaben. Statischer Build — der Inhalt von `dist/` kann auf jede Domain kopiert werden.

## Voraussetzungen

- Node.js 18+
- Python 3 (für `npm run sync` → `tools/build_shelf_website.py`)

## Workflow

### 1. Katalog synchronisieren

Bücher werden aus den Buchpaketen unter `books/*/export.yaml` generiert. Nur Einträge mit `website.enabled: true` erscheinen im Regal.

```bash
# Aus dem Repo-Root
python tools/build_shelf_website.py

# Oder aus webpage/
npm run sync
```

Der Generator schreibt:

- `public/data/catalog.json` — Metadaten (Titel, Autor, Summary, Cover-URL, Amazon-Link)
- `public/covers/<id>.jpg` — normalisierte Cover-Kopien

### 2. Lokal entwickeln

```bash
cd webpage
npm install
npm run sync   # optional, falls Katalog noch nicht erzeugt
npm run dev
```

Öffnet Vite auf `http://localhost:5173` (Port kann abweichen).

### 3. Production-Build

Wichtig: Ordner heisst **`webpage/`** (Regal-Website), nicht `webapp/` (Dashboard).

```bash
# Aus dem Repo-Root
python tools/build_webpage_dist.py

# Oder
cd webpage
npm run build
npm run preview   # optional: dist/ lokal testen
```

Ergebnis: `webpage/dist/` — **diesen Ordnerinhalt auf die Domain legen** (relative Pfade, kein Server nötig).

Lokal testen **nicht** per Doppelklick auf `index.html` (`file://` blockiert die 3D-Module):

```bash
python tools/preview_webpage.py
# oder Dev-Start-Webpage.cmd
# dann http://127.0.0.1:4173
```

## Steuerung

| Aktion | Browse | Inspect (Buch geöffnet) |
|--------|--------|---------------------------|
| Maus ziehen | Regal horizontal scrollen | — |
| Mausrad | Regal scrollen | Zoom |
| Pfeiltasten ← → | Regal scrollen | — |
| Klick auf Buch | Buch öffnen | — |
| « Regal» / Escape | — | Zurück zum Regal |
| Orbit | — | Drehen um das Buch (Maustaste) |

## export.yaml — Website-Felder

Pro Buchpaket in `books/<id>/export.yaml`:

```yaml
website:
  enabled: true
  amazon_url: "https://www.amazon.de/..."   # optional; Button nur wenn gesetzt
  sort_order: 10                              # optional
```

Erforderlich für die Aufnahme: `enabled: true`, auflösbares Cover, Titel und Autor.

## Projektstruktur

```text
webpage/
  public/
    data/catalog.json    # generiert
    covers/              # generiert
    models/              # optional: Mint-GLBs
  src/
    main.js              # Einstieg, UI-Overlay
    catalog.js           # Katalog-Laden
    shelf/ShelfScene.js  # Three.js-Regal
  dist/                  # Deploy-Artefakt (nach build)
```

Ohne `catalog.json` zeigt die App eine freundliche deutsche Meldung — der Build schlägt trotzdem nicht fehl.

## 3D-Assets

Aktuell: Fallback-Hardcover-Boxen mit echten Cover-Texturen aus `/covers/`.

Später können Mint-GLBs unter `public/models/` eingebunden werden (siehe Plan im Repo).
