# Higgsfield API und Web-UI-Moodboards

Stand: 2026-07-02.

Higgsfield-Support hat bestaetigt: Web-UI-Moodboards werden nicht ueber API,
CLI oder MCP exponiert. Private Moodboard-UUIDs aus der Weboberflaeche sind
daher Projektmetadaten fuer manuelle Web-UI-Laeufe, aber kein gueltiger
programmatischer Eingabekanal.

## Konsequenz

Diese Kanaele bleiben strikt getrennt:

```yaml
higgsfield:
  moodboard:
    name: Aelite
    web_ui_moodboard_id: "<Web-UI-Moodboard-UUID>"
    availability: web_ui_only

  soul:
    id: null
    strength: 1.0

  reference_images: []
```

- `web_ui_moodboard_id`: nur fuer manuelle Web-UI-Generierung dokumentieren.
- `soul.id`: echte trainierte Soul-/Character-Referenz, wird als
  `custom_reference_id` genutzt.
- `reference_images`: konkrete Bildreferenzen, werden per CLI `--image`
  uebergeben.

Eine Web-UI-Moodboard-UUID darf nicht als `custom_reference_id`, `--soul-id`,
`--image`, API-`style_id` oder `medias` verwendet werden.

## Backend-Verhalten

`tools/generate_illustration.py` unterstuetzt weiterhin:

- `cli`: Standard fuer automatische Generierung ohne Web-UI-Moodboard.
- `api`: experimenteller API-Pfad fuer Generierung ohne privates Web-UI-
  Moodboard.
- `auto`: Default auf CLI.

Wenn ein Web-UI-Moodboard vorhanden ist und kein bewusst getrennter
programmatischer Eingang gesetzt wird, bricht das Tool ab mit:

```text
HIGGSFIELD_WEB_UI_MOODBOARD_NOT_PROGRAMMATIC
```

Bewusste Alternativen:

```powershell
# Ohne Referenz generieren
python tools\generate_illustration.py --book aelita --chapter 020 --kind chapter --style stil-03-branderson --no-reference

# Mit echter Soul-ID
python tools\generate_illustration.py --book aelita --chapter 020 --kind chapter --style stil-03-branderson --soul-id <Soul-UUID>

# Mit konkreten Referenzbildern
python tools\generate_illustration.py --book aelita --chapter 020 --kind chapter --style stil-03-branderson --image <pfad-oder-uuid>
```

## API-Credentials

API-Credentials bleiben fuer regulare API-Experimente nutzbar, aber nicht fuer
private Web-UI-Moodboards:

```env
HF_CREDENTIALS=KEY_ID:KEY_SECRET
```

Quelle fuer Key und Secret ist `cloud.higgsfield.ai`. Secrets gehoeren nur in
`.env` oder die lokale Shell-Umgebung, nie in YAML, Prompt-Metadaten oder Logs.

## Probe-Befehl

Der Probe-Befehl bleibt als Nachweis/Regressionstest erhalten:

```powershell
node tools\probe_higgsfield_moodboards.mjs
```

Er darf fuer Web-UI-Moodboards erwartbar `found: false` melden, weil
`getSoulStyles()` nur API-verfuegbare Styles beziehungsweise vordefinierte
Styles listet, nicht private Web-UI-Moodboards.

## Praktischer Workflow

Fuer hochwertige, moodboardtreue Kapitelbilder:

1. Web-UI mit Moodboard verwenden.
2. Ergebnis lokal ablegen, z. B. `books/<id>/assets/chapter/chapter-020.jpg`.
3. Job-/Bildreferenz in Prompt-Metadaten oder Buchnotizen dokumentieren.

Fuer Automation:

1. Prompt- und Variantenlaeufe ohne Web-UI-Moodboard per CLI/API erzeugen.
2. Falls Stilnaehe gebraucht wird, 6-15 repraesentative Referenzbilder bewusst
   in `higgsfield.reference_images` pflegen.
3. Diese Bilder per `--image` beziehungsweise Buchconfig an die CLI geben.

Das ist kein echtes Moodboard, aber der einzige aktuell von Higgsfield
unterstuetzte programmatische Ersatz fuer private Moodboards.
