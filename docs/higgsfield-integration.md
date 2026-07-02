# Higgsfield-Integration

Dieses Projekt erzeugt Kapitel- und Szenenbilder mit der lokalen Higgsfield-CLI
ueber `tools/generate_illustration.py`. Die fertigen Bilder werden direkt in
der Export-Konvention des jeweiligen Buchpakets abgelegt:

```text
books/<book-id>/assets/chapter/chapter-001.jpg
books/<book-id>/assets/scene/001/scene-001.jpg
```

## Buch-Defaults

Die Higgsfield-Defaults werden pro Buch in `books/<book-id>/book.yaml`
gespeichert:

```yaml
higgsfield:
  model: text2image_soul_v2
  aspect_ratio: "3:4"
  quality: 2k
  moodboard:
    name: Buch Peter der Erste
    web_ui_moodboard_id: 8b79a5c6-5539-4257-9b42-537d82259bc4
    availability: web_ui_only
  reference_images: []
```

`tools/generate_illustration.py` liest diese Werte automatisch. Web-UI-
Moodboards sind aber nur Metadaten fuer manuelle Higgsfield-Laeufe; sie werden
nicht an CLI, API oder MCP uebergeben.

Wichtig: Higgsfield-Support hat am 02.07.2026 bestaetigt, dass private
Web-UI-Moodboards nicht in der API-Schicht exponiert werden. Die CLI bietet
ebenfalls keinen Moodboard-/`style_id`-Parameter. Automatische Generierung mit
eigenem Web-UI-Moodboard ist daher aktuell nicht moeglich.

`params.custom_reference_id` ist ein anderer Kanal (Character/Soul-Referenz)
und darf fuer Moodboards nicht verwendet werden. Der unterstuetzte
Automationsersatz sind bewusst gepflegte `reference_images` oder echte
Soul-IDs.

Aktuell erkannte Moodboards:

| Buch | Primaer | UUID |
| --- | --- | --- |
| `peter-i-buch-01` | Buch Peter der Erste | `8b79a5c6-5539-4257-9b42-537d82259bc4` |
| `aelita` | Aelite | `6fdd3fde-4c0d-4b21-a7fa-cf0f4aa1a7ba` |
| `pharao` | Pharao III | `b1808566-674b-4495-b268-756f2ea287d5` |

Fuer `pharao` sind ausserdem in `book.yaml` gespeichert:

| Alternative | UUID |
| --- | --- |
| Pharao | `810f82ce-f518-4c48-b545-515a63ad72ca` |
| Pharao II | `c38052cf-6afc-4ae7-9dbb-1cf083f97242` |

## Generieren

Kapitelbild mit Buch-Defaults:

```powershell
python tools\generate_illustration.py --book peter-i-buch-01 --chapter 001 --kind chapter --style stil-02-poetisch
```

Szenenbild mit Buch-Defaults:

```powershell
python tools\generate_illustration.py --book peter-i-buch-01 --chapter 001 --scene 01 --kind scene --style stil-02-poetisch
```

Bestehende Bilder werden nur mit `--overwrite` ersetzt. Fuer einen reinen
Prompt-/Metadatenlauf ohne Higgsfield-Aufruf `--dry-run` verwenden.

## CLI-Status

Installation unter Windows:

```powershell
npm install -g @higgsfield/cli
```

Login und Status:

```powershell
higgsfield auth login
higgsfield account status --json
```

Modellschema fuer Soul 2.0 pruefen:

```powershell
higgsfield model get text2image_soul_v2 --json
```

Projektinterne Diagnose ohne Bildgenerierung:

```powershell
python tools\generate_illustration.py --book pharao --diagnose-higgsfield
```

Stand 2026-06-24 akzeptiert Soul 2.0 in der CLI die relevanten Parameter
`prompt`, `aspect_ratio`, `quality`, `custom_reference_id`, `medias`, aber
keinen echten Moodboard-/Style-Parameter wie `style_id`. Ein Live-Test mit
`--style_id` wurde von der CLI als `Unknown params: style_id` abgelehnt.
Ein Lauf mit `--custom_reference_id <uuid>` liefert zwar ein Bild, setzt aber
`style.name: General` und behandelt die UUID als Character/Soul-Referenz.

## Character-/Soul-Referenzen

Character-/Soul-IDs sind ein separater Kanal und ersetzen kein Moodboard.
Der Test vom 01.07.2026 bestaetigt: Als `custom_reference_id` gesetzte
Soul-IDs beeinflussen Figuren, setzen aber nicht die gewuenschte Stilwelt.
Fuer konsistente Buchillustrationen bleibt das Moodboard nur im manuellen
Web-UI-Workflow der fuehrende Stilanker (`params.style_id`).

Produktive Aëlita-Bilder sollen bis auf Weiteres **ohne** Character-/Soul-ID
erzeugt werden. Einzelne Tests mit `Fairy I` und `Whispers of Aether` sahen
teilweise brauchbar aus, aber nicht stabil genug: die Referenz wirkt global
auf alle Personen im Bild. Die IDs bleiben dokumentiert, damit sie fuer
bewusste Character-Tests oder als Teil eines Referenzbild-Workflows gezielt
nutzbar sind.

Bekannte Aëlita-Referenzen:

| Name | ID | Typ | Status | Verwendung |
| --- | --- | --- | --- | --- |
| Fairy I | `0fb45e81-0939-41e4-bee4-f0d007a8ec43` | `soul_2` | completed | Bekannte Aëlita-Referenz; derzeit nicht produktiv verwenden |
| Whispers of Aether | `27e7e3ca-aa27-48f0-8a82-e59541dcfd20` | `soul_2` | completed | Testreferenz; derzeit nicht produktiv verwenden |

Aus der Higgsfield-History vom 01.07.2026:

- Gewuenschtes Moodboard: `style_id = 6fdd3fde-4c0d-4b21-a7fa-cf0f4aa1a7ba`
  (`Aelite`, `style_strength = 0.8`).
- Zusaetzliche Character-/Soul-Referenz:
  `custom_reference_id = 0fb45e81-0939-41e4-bee4-f0d007a8ec43` (`Fairy I`).
- Fruehere Versuche, Moodboard-IDs als `custom_reference_id` zu nutzen,
  waren falsch, weil sie als Soul-/Character-Referenz und nicht als
  Moodboard/Style interpretiert werden.

### Multi-Soul-Probe

Mehrere Soul-IDs in einem `text2image_soul_v2`-Call sind nicht dokumentiert.
Das CLI-Schema zeigt `custom_reference_id` nur einmal. Fuer kontrollierte
Experimente gibt es deshalb ein separates Probe-Skript:

```powershell
node tools\probe_higgsfield_multi_soul.mjs --dry-run
node tools\probe_higgsfield_multi_soul.mjs --allow-paid-generation --variant single_fairy
node tools\probe_higgsfield_multi_soul.mjs --allow-paid-generation --variants array_two,object_named
```

Die Probe schreibt Payloads und Ergebnisse nach
`books/aelita/work/prompts/higgsfield/soul-tests/`. Varianten:

- `single_fairy`: eine bekannte Aëlita-Referenz (`Fairy I`)
- `single_whispers`: Testreferenz `Whispers of Aether`
- `array_two`: zwei Soul-IDs als Array in `custom_reference_id`
- `object_named`: benannte Zuordnung `{ Aelita: ..., Los: ... }`

Echte Bildgenerierung startet nur mit `--allow-paid-generation`. Diese Probe
ist bewusst nicht Teil der produktiven Illustration-Pipeline.

## Moodboard-UUIDs Finden

Share-Links aus der Weboberflaeche, z. B. `https://higgsfield.ai/s/...`, sind
nicht automatisch CLI-UUIDs. Die nutzbaren UUIDs wurden bisher aus der
Generate-History ermittelt:

```powershell
$jobs = higgsfield generate list --image --size 100 --json | ConvertFrom-Json
$jobs |
  ForEach-Object { $_.params } |
  Where-Object { $_.style_name -or $_.style_id } |
  Select-Object style_name, style_id, custom_reference_id -Unique |
  Sort-Object style_name
```

Wenn das gesuchte Moodboard dort nicht auftaucht, im Web-UI testweise ein Bild
mit diesem Moodboard erzeugen und den Befehl danach erneut ausfuehren.

Quality-Optionen fuer Soul 2.0 sind `1.5k` und `2k`. Der Default ist `1.5k`,
da 2k fuer Buchillustrationen zu gross aufloest. Die Einstellung pro Buch
steht in `book.yaml` unter `higgsfield.quality`.

## Prompt-Strategie (wichtig)

**text2image_soul_v2 hat KEINEN `negative_prompt`-Parameter.** Das Modell
liest *alle* Woerter im Prompt als positive Anweisung. Formulierungen wie
"keine Autos" oder "keine modernen Objekte" bewirken genau das Gegenteil
und fuehren zu Collagen, Split-Screens und modernen Artefakten.

Deshalb:
- **Nur positive Beschreibungen** – was das Bild zeigen SOLL, nicht was es
  vermeiden soll.
- Keine "No X", "avoid Y", "ohne Z"-Formulierungen.
- Keine Meta-Instruktionen wie "Create ONE unified image" oder
  "Scene location: chapter 001".

### Prompt-Aufbau

Der Prompt besteht aus genau zwei Teilen (in dieser Reihenfolge):

1. **`illustration_setting`** (aus `book.yaml`): Eine vom Nutzer
   editierbare positive Beschreibung von Epoche, Ort, Kleidung,
   Architektur und Atmosphaere. Beispiel:

   ```yaml
   illustration_setting: |
     Ancient Egypt, reign of Pharaoh Ramses XII 12th Century BC. Period-accurate clothing,
     architecture, and environment. Historical style, richly detailed, atmospheric.
   ```

   Der YAML-Block-Scalar (`|`) erlaubt mehrzeilige Eingabe; Zeilenumbrueche
   werden automatisch zu Spaces komprimiert (Higgsfield-CLI verarbeitet
   nur Single-Line-Prompts).
2. **Szenen-/Kapitel-Auszug** (automatisch aus der Arbeitsdatei): Die ersten
   zusammenhaengenden Absaetze, aktuell max. 6 Absaetze bzw. 2000 Zeichen.
   Mottos, Zitate, Ueberschriften und Tracking-Header wie
   `*Buch: Aëlita* <!-- status: pending -->` werden herausgefiltert, da sie
   Higgsfield verleiten koennen, Text oder Metadaten im Bild zu rendern.

Optional wird zwischen Setting und Szenenauszug ein knapper Figurenblock aus
`names.yaml` eingefuegt. Dafuer koennen Personen pro Buch ein Feld `visual`
bekommen:

```yaml
entries:
- source: Аэлита
  target: Aëlita
  aliases: []
  type: person
  status: confirmed
  visual: Junge marsianische Prinzessin, schlank, ruhig, helle Augen, vogelhaft feine Gesichtszuege.
  higgsfield:
    character_id: null
```

`generate_illustration.py` sucht im verwendeten Szenentext nach `source`,
`target` und `aliases` und fuegt maximal drei passende `visual`-Beschreibungen
in den Prompt ein. Das Feld bleibt bewusst kurz und positiv formuliert.
`higgsfield.character_id` ist fuer echte Character-/Soul-Referenzen reserviert
und wird nicht als Moodboard-ID interpretiert.

Die Reihenfolge ist **Setting zuerst, Auszug danach**. Der Grund ist
praktisch: Die buchweite Bildsprache aus `book.yaml` setzt den visuellen
Rahmen, bevor der konkrete Szeneninhalt folgt. Die Stil-/Setting-Ergaenzung
kommt ausschliesslich aus `book.yaml` unter `illustration_setting`; sie wird
nicht im Code gepflegt.

### Prompt-Ausgabe

Der finale Prompt ist ein **Single-Line-String**. Die Higgsfield-CLI kann
mehrzeilige `--prompt`-Werte nicht korrekt parsen (Zeilenumbrueche werden
als Argument-Trenner interpretiert).

### Prompt nachvollziehen

Generierte Prompts werden als `.md`-Dateien gespeichert:
`books/<book-id>/work/prompts/higgsfield/<chapter>-scene-<nn>-<style>.md`

Daneben liegt eine `.json`-Metadatendatei mit Kommando, Modell, Moodboard
und Job-Ergebnis.

### Bekannte Produktgrenze: Web-UI-Moodboards (Stand 2026-07-02)

Higgsfield-Support hat bestaetigt: Private Web-UI-Moodboards werden nicht ueber
API, CLI oder MCP exponiert. `getSoulStyles()` listet API-verfuegbare bzw.
vordefinierte Styles, nicht die privaten Moodboards aus der Weboberflaeche.

Die aktuelle Higgsfield-CLI exponiert fuer `text2image_soul_v2` ebenfalls kein
`style_id`. Der verfuegbare Parameter `--custom_reference_id` ist ein
Character-/Soul-Kanal und nicht gleichwertig.

**`tools/generate_illustration.py` verhaelt sich seit dem 02.07.2026 wie folgt:**

- Web-UI-Moodboard-UUIDs werden nur als Metadaten behandelt.
- Automatische Generierung mit Web-UI-Moodboard bricht mit
  `HIGGSFIELD_WEB_UI_MOODBOARD_NOT_PROGRAMMATIC` ab.
- Moodboard-UUIDs werden nicht an `custom_reference_id`, `--image`, API
  `style_id` oder `medias` uebergeben.
- Automatische Generierung ist nur ohne Web-UI-Moodboard, mit echter Soul-ID
  oder mit bewusst gepflegten `reference_images` vorgesehen.

**Warum war das unklar?** Fruehere CLI-Laeufe lieferten Bilder, weil
`--custom_reference_id` technisch akzeptiert wurde. Die History zeigt aber den
Unterschied: falsche Laeufe haben `style_id = General` plus
`custom_reference_id`; korrekte Web-UI-Laeufe haben `style_id = <Moodboard-UUID>`
und kein `custom_reference_id`.

Konkreter Aëlita-Befund vom 24.06.2026:

| Job | Ergebnis |
| --- | --- |
| `9ccfe23c-711e-4021-b589-08aa6e246391` | falscher CLI-Lauf: `style.name = General`, `custom_reference_id = 6fdd3fde-...` |
| `5c245b6d-b117-418c-8c26-ccc128be3edf` | korrekter Web-UI-Lauf: `style.name = Aelite`, `style_id = 6fdd3fde-...`, kein `custom_reference_id` |

**Aktuelle Workarounds:**

1. **Higgsfield Web-UI**: Moodboards funktionieren dort (Style wird korrekt
   gesetzt). Bilder manuell generieren und in `books/<id>/assets/` ablegen.
2. **`--no-reference`**: Generierung ohne Referenz (reiner Prompt).
3. **Echte Soul-ID**: Character-/Soul-Referenz bewusst mit `--soul-id` setzen.
4. **`--image <referenzbild-uuid|pfad>`**: Konkrete Referenzbilder statt
   Moodboard nutzen.

**Ausblick:** Automatische private Moodboard-Generierung kann erst wieder
aktiviert werden, wenn Higgsfield Web-UI-Moodboards offiziell ueber API, CLI
oder MCP exponiert.

## Bild-Nachbearbeitung (Image Processing)

Nach dem Download von Higgsfield werden die Bilder automatisch mit Pillow
nachbearbeitet. Die Einstellungen dafuer stehen pro Buch in `book.yaml` unter
`higgsfield.image_processing`:

```yaml
higgsfield:
  # ... bestehende Keys ...
  image_processing:
    format: JPEG           # JPEG | PNG | KEEP (Original beibehalten)
    jpeg_quality: 60       # 1–100, nur fuer JPEG
    max_width: 1600        # px, optional – skaliert proportional
    max_height: 2400       # px, optional – skaliert proportional
```

**Defaults** (wenn der Block fehlt):

| Key | Default | Beschreibung |
| --- | --- | --- |
| `format` | `JPEG` | Ausgabeformat; `KEEP` belaesst das Originalformat |
| `jpeg_quality` | `95` | JPEG-Qualitaet 1–100 |
| `max_width` | — | Keine Breitenbeschraenkung |
| `max_height` | — | Keine Hoehenbeschraenkung |

**Verhalten:**

- `format: JPEG` + `jpeg_quality`: Bild wird als JPEG mit der angegebenen
  Qualitaet gespeichert. PNG-Originale werden nach RGB konvertiert.
- `format: PNG`: Bild wird als PNG gespeichert (verlustfrei, groessere Datei).
- `format: KEEP`: Originalformat bleibt erhalten. JPEG wird mit
  `jpeg_quality` komprimiert, PNG bleibt PNG.
- `max_width` / `max_height`: Wenn gesetzt, wird das Bild mit
  `Image.thumbnail()` proportional verkleinert, falls es die Maximalmasse
  ueberschreitet. Das Seitenverhaeltnis bleibt erhalten.

Die Dateiendung des Ausgabebilds passt sich automatisch an (`format: PNG` →
`.png`, sonst `.jpg`).
