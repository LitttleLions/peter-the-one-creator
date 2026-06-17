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

Der Prompt enthaelt automatisch:
- Einen Auszug aus dem jeweiligen Szenentext (max. 1500 Zeichen)
- Die Kurzbeschreibung aus `export.yaml` (`book.description`) als
  Kontexthinweis (z. B. "altes Aegypten", "Russland"), damit das Modell
  passende Stimmung und Kulisse waehlt.
- Visuelle Constraints (keine modernen Objekte, keine Texteinlagen).

Hinweis: Beim ersten Peter-Test wurde `--custom_reference_id
8b79a5c6-5539-4257-9b42-537d82259bc4` an die CLI uebergeben. Die Higgsfield-
Antwort meldete trotzdem `style_name: General`. Das kann ein Anzeigeproblem
oder eine CLI-Einschraenkung sein; vor grossen Serienlaeufen einen visuellen
Vergleich oder einen erneuten Schema-/History-Check machen.
