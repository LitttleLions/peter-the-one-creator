# Marketingpaket - Das Leben Arsenjews

Dieses Paket wurde aus den vorhandenen Buchdaten erzeugt. Es
veroeffentlicht nichts und spricht keine Plattform-API an.

## Dateien

- `campaign.json` - maschinenlesbares Kampagnenmanifest (Uebergabe an Postiz o. Ae.)
- `posts.md` - X-Beitraege zum Kopieren
- `youtube.md` - Liedvideo und Shorts (Titel, Beschreibung, Shotlist)
- `media.json` - Medienuebersicht mit repo-relativen Pfaden
- `README.md` - diese Hinweise

## Offene Angaben in diesem Paket

- `song_data` (missing) - betrifft: x-t1-song, x-t2-youtube, yt-main, yt-short-1 - marketing.songs in export.yaml pflegen und die Audiodatei repo-relativ unter books/<id>/assets/ ablegen
- `youtube_url` (missing) - betrifft: kampagnenweit - marketing.youtube.url oder marketing.youtube.video_id in export.yaml eintragen

## Angaben pflegen

- Amazon-Link: `books/leben-arsenjews/export.yaml` -> `website.amazon_url` (oder `marketing.amazon_url` fuer eine abweichende Ausgabe). Der Link wird als Benutzerangabe uebernommen; es findet keine Pruefung gegen die Amazon-Ausgabe statt.
- YouTube-Adresse spaeter: `books/leben-arsenjews/export.yaml` -> `marketing.youtube.url` (oder `video_id`) und `public: true`, sobald das Video oeffentlich ist. Ein erneuter Export aktualisiert dann nur Linkfeld, zusammengesetzte Texte und Validierung.
- Kampagnenstart: `books/leben-arsenjews/export.yaml` -> `marketing.campaign_start` (ISO 8601, Europe/Berlin). Ohne Startdatum bleiben die relativen Termine gueltig.
- Songdaten: `books/leben-arsenjews/export.yaml` -> `marketing.songs` mit `file`, `title`, `lyrics_file`, `clip_start_seconds`, `clip_duration_seconds`, `credits`, `ai_generated`. Fehlende Songs blockieren nur die Musikbestandteile.
- Bildzuordnung: `books/leben-arsenjews/export.yaml` -> `marketing.media` (`<post-id>: assets/chapter/chapter-012.jpg`).

## Texte erzeugen und bearbeiten

- Generierte Texte: `books/leben-arsenjews/work/marketing/generated.json`
- Manuelle Fassung: `books/leben-arsenjews/work/marketing/overrides/<post-id>.md` (hat Vorrang und wird als `override` gekennzeichnet)

```bash
python tools/export_marketing.py --book leben-arsenjews --dry-run
python tools/export_marketing.py --book leben-arsenjews
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
- Amazon-Link: https://www.amazon.de/Das-Leben-Arsenjews-Iwan-Bunin-ebook/dp/B0HJZJFKCQ/ (Quelle: website.amazon_url, Syntax: ok)
- YouTube: noch nicht bekannt (oeffentlich: False)
- Songs hinterlegt: 0
- Textgenerator: workspace_ai (Modell: Muse Spark (Repo-Editor), Prompt-Version: marketing-1)

## Zeichengrenzen

- X: 280 gewichtete Zeichen, Zielband 220-250
- YouTube-Titel: 100 Zeichen
- YouTube-Beschreibung: 5000 Zeichen

Die gewichtete Laenge ist eine konservative Naeherung (URLs zaehlen als 23
Zeichen, breite Zeichen als 2) und keine Plattformvalidierung.
