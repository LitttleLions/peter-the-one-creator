# Marketingpaket - Peter der Erste

Dieses Paket wurde aus den vorhandenen Buchdaten erzeugt. Es
veroeffentlicht nichts und spricht keine Plattform-API an.

## Dateien

- `campaign.json` - maschinenlesbares Kampagnenmanifest (Uebergabe an Postiz o. Ae.)
- `posts.md` - X-Beitraege zum Kopieren
- `youtube.md` - Liedvideo und Shorts (Titel, Beschreibung, Shotlist)
- `media.json` - Medienuebersicht mit repo-relativen Pfaden
- `README.md` - diese Hinweise

## Offene Angaben in diesem Paket

- `youtube_url` (missing) - betrifft: x-t2-youtube, yt-main - marketing.youtube.url oder marketing.youtube.video_id in export.yaml eintragen
- `text:x-t1-song` (missing) - betrifft: x-t1-song - work/marketing/generated.json erzeugen oder work/marketing/overrides/x-t1-song.md anlegen
- `text:x-t2-youtube` (missing) - betrifft: x-t2-youtube - work/marketing/generated.json erzeugen oder work/marketing/overrides/x-t2-youtube.md anlegen
- `text:yt-main` (missing) - betrifft: yt-main - work/marketing/generated.json erzeugen oder work/marketing/overrides/yt-main.md anlegen
- `text:yt-short-1` (missing) - betrifft: yt-short-1 - work/marketing/generated.json erzeugen oder work/marketing/overrides/yt-short-1.md anlegen
- `text:yt-short-2` (missing) - betrifft: yt-short-2 - work/marketing/generated.json erzeugen oder work/marketing/overrides/yt-short-2.md anlegen

## Angaben pflegen

- Amazon-Link: `books/peter-i-buch-01/export.yaml` -> `website.amazon_url` (oder `marketing.amazon_url` fuer eine abweichende Ausgabe). Der Link wird als Benutzerangabe uebernommen; es findet keine Pruefung gegen die Amazon-Ausgabe statt.
- YouTube-Adresse spaeter: `books/peter-i-buch-01/export.yaml` -> `marketing.youtube.url` (oder `video_id`) und `public: true`, sobald das Video oeffentlich ist. Ein erneuter Export aktualisiert dann nur Linkfeld, zusammengesetzte Texte und Validierung.
- Kampagnenstart: `books/peter-i-buch-01/export.yaml` -> `marketing.campaign_start` (ISO 8601, Europe/Berlin). Ohne Startdatum bleiben die relativen Termine gueltig.
- Songdaten: `books/peter-i-buch-01/export.yaml` -> `marketing.songs` mit `file`, `title`, `lyrics_file`, `clip_start_seconds`, `clip_duration_seconds`, `credits`, `ai_generated`. Fehlende Songs blockieren nur die Musikbestandteile.
- Bildzuordnung: `books/peter-i-buch-01/export.yaml` -> `marketing.media` (`<post-id>: assets/chapter/chapter-012.jpg`).

## Texte erzeugen und bearbeiten

- Generierte Texte: `books/peter-i-buch-01/work/marketing/generated.json`
- Manuelle Fassung: `books/peter-i-buch-01/work/marketing/overrides/<post-id>.md` (hat Vorrang und wird als `override` gekennzeichnet)

```bash
python tools/export_marketing.py --book peter-i-buch-01 --dry-run
python tools/export_marketing.py --book peter-i-buch-01
```

Ein erneuter Export erzeugt keine neuen Beitrags-IDs und keine neuen Texte; neu
erzeugt wird nur bei geaenderten Quelldaten, geaenderter Prompt-Version oder
`--regenerate`.

## Statuswerte

- `generated`: Text liegt vor, ist aber noch nicht redaktionell freigegeben
- `ready`: Text und alle Voraussetzungen sind erfuellt (manuell uebernommen)
- `needs_review`: Text fehlt oder ueberschreitet ein Plattformlimit
- `needs_amazon_url`: Text fertig, Amazon-Link fehlt
- `needs_youtube_url`: Text fertig, YouTube-Adresse fehlt
- `blocked`: Medium/Adresse vorhanden, aber unbrauchbar oder nicht oeffentlich
- `omitted`: Position bewusst ausgelassen, weil Material fehlt

Textlage (`text_status`) und Veroeffentlichungsreife (`publish_status`) sind
getrennt: ein Text kann fertig sein, waehrend ein Video noch nicht oeffentlich ist.

## Angaben zu diesem Lauf

- Kampagnenstart: nicht gesetzt (Quelle: unset)
- Zeitzone: Europe/Berlin
- Amazon-Link: https://amzn.to/4vLjAlF (Quelle: website.amazon_url, Syntax: ok)
- YouTube: noch nicht bekannt (oeffentlich: False)
- Songs hinterlegt: 1
- Textgenerator: openrouter (Modell: deepseek/deepseek-v4-pro, Prompt-Version: marketing-1)

## Zeichengrenzen

- X: 280 gewichtete Zeichen, Zielband 220-250
- YouTube-Titel: 100 Zeichen
- YouTube-Beschreibung: 5000 Zeichen

Die gewichtete Laenge ist eine konservative Naeherung (URLs zaehlen als 23
Zeichen, breite Zeichen als 2) und keine Plattformvalidierung.
