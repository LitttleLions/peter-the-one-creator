# Higgsfield API-Moodboard-Backend

Diese API-Anbindung verwendet den historischen, offiziell bereitgestellten
Soul-Endpunkt `/v1/text2image/soul`. Sie ist ein kontrollierter
Kompatibilitaetspfad fuer Moodboards, nicht der allgemein bevorzugte
Higgsfield-V2-Standard.

## Architektur

`tools/generate_illustration.py` unterstuetzt drei Backends:

- `cli`: nutzt die bestehende Higgsfield-CLI. Moodboards werden blockiert,
  weil die CLI fuer `text2image_soul_v2` aktuell keinen echten `style_id`
  anbietet.
- `api`: nutzt `tools/higgsfield_api_adapter.mjs` und den V1-Soul-Endpunkt.
  Dieses Backend ist fuer Moodboard-Pilotlaeufe reserviert.
- `auto`: Default. Bei Moodboard-UUID wird `api` gewaehlt, sonst bleibt der
  bestehende CLI-Pfad aktiv.

Die Kanaele bleiben getrennt:

```yaml
higgsfield:
  moodboard:
    style_id: "<Moodboard-UUID>"
    strength: 1.0

  soul:
    id: null
    strength: 1.0

  reference_images: []
```

`style_id` ist Moodboard/Stilwelt. `custom_reference_id` ist eine echte
Soul-/Character-Referenz. `reference_images` sind konkrete Bildreferenzen.
Eine Moodboard-UUID darf nicht als Soul-ID, Bildreferenz oder `medias`
verwendet werden.

## Credentials und Setup

Lokale Node-Abhaengigkeit installieren:

```powershell
npm install
```

Credentials werden nur ueber Umgebungsvariablen gelesen:

```powershell
$env:HF_CREDENTIALS="KEY_ID:KEY_SECRET"
```

Alternativ:

```powershell
$env:HF_API_KEY="KEY_ID"
$env:HF_API_SECRET="KEY_SECRET"
```

`HF_CREDENTIALS` hat Vorrang. Credentials werden nicht in YAML, Metadaten,
Promptdateien oder Logs geschrieben.

## Probe ohne Credits

```powershell
node tools\probe_higgsfield_moodboards.mjs
```

Der Probe-Befehl liest `books/*/book.yaml`, extrahiert nur
`higgsfield.moodboard.style_id`, ruft `getSoulStyles()` auf und meldet, ob die
bekannten Moodboards in der API-Liste auffindbar sind. Er startet keine
Generierung.

## Dry Run

Adapter direkt:

```powershell
'{
  "action": "generate",
  "prompt": "A quiet cinematic science-fiction scene at dusk near old gates by a river embankment.",
  "style_id": "6fdd3fde-4c0d-4b21-a7fa-cf0f4aa1a7ba",
  "style_strength": 1.0,
  "soul_id": null,
  "soul_strength": 1.0,
  "aspect_ratio": "3:4",
  "quality": "hd",
  "batch_size": 1,
  "dry_run": true
}' | node tools\higgsfield_api_adapter.mjs
```

Ueber Python:

```powershell
python tools\generate_illustration.py --book aelita --chapter 001 --kind scene --backend api --dry-run
```

## Paid Pilot

Ein echter API-Bildlauf startet nur, wenn alle Bedingungen erfuellt sind:

- `--backend api` oder `backend:auto` mit Moodboard;
- `--allow-paid-generation`;
- Moodboard-ID wurde vorher per `getSoulStyles()` gefunden.

Beispiel:

```powershell
python tools\generate_illustration.py --book aelita --chapter 001 --kind scene --backend api --allow-paid-generation
```

Ohne `--allow-paid-generation` fuehrt Python nur Style-Discovery und
Request-Validierung aus und bricht vor dem bezahlten Generate-Aufruf ab.

## Verifikation

Metadaten enthalten unter anderem:

```json
{
  "generator_backend": "higgsfield_api_v1",
  "requested_style_id": "...",
  "requested_style_name": "...",
  "requested_style_strength": 1.0,
  "requested_soul_id": null,
  "requested_reference_images": [],
  "style_discovery_status": "found",
  "api_request_id": null,
  "api_job_id": null,
  "verification_status": "planned"
}
```

Nach echter Generierung ist `verification_status` nur dann `verified`, wenn die
API-/Jobantwort eindeutig `style_id == requested_style_id` und
`custom_reference_id == requested_soul_id` zeigt. Fehlen diese Felder, bleibt
der Status `unverified`.

## Grenzen

- Der API-Pfad ist kein Serienmodus.
- Die CLI bleibt fuer Nicht-Moodboard-Laeufe der Standard.
- Legacy-Werte wie `higgsfield.moodboard.custom_reference_id` werden nicht als
  Moodboard interpretiert und nicht migriert.
- Die API-Qualitaetswerte koennen vom CLI-Vokabular abweichen; Pilotlaeufe
  muessen deshalb mit Dry Run und Style-Discovery vorbereitet werden.
