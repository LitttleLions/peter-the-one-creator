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
    custom_reference_id: 8b79a5c6-5539-4257-9b42-537d82259bc4
```

`tools/generate_illustration.py` liest diese Werte automatisch. CLI-Argumente
ueberschreiben die Buch-Defaults, z. B. `--moodboard <uuid>`.

Aktuell erkannte Moodboards:

| Buch | Primaer | UUID |
| --- | --- | --- |
| `peter-i-buch-01` | Buch Peter der Erste | `8b79a5c6-5539-4257-9b42-537d82259bc4` |
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

Stand 2026-06-16 akzeptiert Soul 2.0 diese relevanten Parameter:
`prompt`, `aspect_ratio`, `quality`, `custom_reference_id`, `medias`.
Das Tool nutzt deshalb fuer erkannte Moodboard-/Style-UUIDs
`--custom_reference_id <uuid>`.

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

1. **Szenen-Auszug** (automatisch aus der Quell-Szene): Die ersten 1–3
   zusammenhaengenden Absaetze, max. 1000 Zeichen. Mottos, Zitate und
   Ueberschriften werden herausgefiltert, da sie Higgsfield verleiten,
   Text im Bild zu rendern.
2. **`illustration_setting`** (aus `book.yaml`): Eine vom Nutzer
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

Die Reihenfolge ist **Excerpt zuerst, Setting hinten** – das hat sich in
Tests als wirksamer erwiesen als die umgekehrte Reihenfolge.

### Prompt-Ausgabe

Der finale Prompt ist ein **Single-Line-String**. Die Higgsfield-CLI kann
mehrzeilige `--prompt`-Werte nicht korrekt parsen (Zeilenumbrueche werden
als Argument-Trenner interpretiert).

### Prompt nachvollziehen

Generierte Prompts werden als `.md`-Dateien gespeichert:
`books/<book-id>/work/prompts/higgsfield/<chapter>-scene-<nn>-<style>.md`

Daneben liegt eine `.json`-Metadatendatei mit Kommando, Modell, Moodboard
und Job-Ergebnis.

Hinweis: Beim ersten Peter-Test wurde `--custom_reference_id
8b79a5c6-5539-4257-9b42-537d82259bc4` an die CLI uebergeben. Die Higgsfield-
Antwort meldete trotzdem `style_name: General`. Das kann ein Anzeigeproblem
oder eine CLI-Einschraenkung sein; vor grossen Serienlaeufen einen visuellen
Vergleich oder einen erneuten Schema-/History-Check machen.

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
