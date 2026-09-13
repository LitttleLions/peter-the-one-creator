# Marketingexport (Motivatier Classics)

Status: umgesetzt 2026-09-13, erweitert 2026-09-14 (X-Clip). Erzeugt
Beitraege und ein Kampagnenmanifest aus vorhandenen Buchdaten. **Es wird
nichts veroeffentlicht** und **keine Plattform-API** angesprochen (kein X,
kein YouTube, kein Postiz).

## Ablauf im Alltag

1. Buch wie bisher bearbeiten und EPUB exportieren (`tools/export_manuscript.py`).
2. Nach der Veroeffentlichung den Amazon-Link eintragen (Abschnitt *Angaben pflegen*).
3. Marketingpaket erzeugen: `python tools/export_marketing.py --book <id>`.
4. Texte pruefen, offene Angaben abarbeiten, spaeter die YouTube-Adresse
   nachtragen und erneut exportieren.
5. Falls ein Song vorliegt: X-Clip rendern (Abschnitt *X-Clip fuer X*),
   z. B. `py -3 tools/render_x_clip.py --book <id> --song song-01`.

Fehlende Marketingdaten blockieren den Buch-Export **nicht**: Der EPUB-Pfad
liest den `marketing:`-Block nicht (Regressionstest:
`tests/test_marketing_campaign.py::ExportRegressionTests`).

## Datenquellen

Es werden ausschliesslich vorhandene Daten verwendet:

| Quelle | Verwendung |
|---|---|
| `books/<id>/book.yaml` | ID, Titel, Autor, `style_mode`, `ai.*` |
| `books/<id>/export.yaml` | Untertitel, `description`, `summary`, `author_bio`, `title_page_extra`, Uebersetzung/Herausgeber, `cover`, `illustrations`, `website.amazon_url`, `marketing.*` |
| `books/<id>/names.yaml` | Namensglossar fuer Prompttexte |
| `books/<id>/work/scenes/de/<style>/` | echte Leseprobe, Themenzuordnung der Bilder |
| `books/<id>/assets/` | Cover, Kapitelbilder, Szenenbilder, optional Audio/Video |

Song- und Dateinamen folgen einer festen Regel (kein Raten, nichts erfinden):

* Song-ID: `song-01`, `song-02`, … (laufend je Buch)
* Songtitel: `<Buchtitel> – Lied zum Roman` (aus `book.yaml:title`)
* Audiodatei: `assets/audio/<basis>-song-NN.mp3`, wobei `<basis>` die Buch-ID
  ohne trailing `-buch-NN` ist (z. B. `peter-i-buch-01` → `peter-i-song-01.mp3`)
* `ai_generated` neuer Songs: Default `true` (KI-generierte Vertonung; steht so
  im Manifest unter `delivery.requires_synthetic_media_disclosure`)
* Unbekannte Clip-Zeiten/Credits bleiben `null`/`[]`; die Datei-Existenz
  prueft der Exporter (`file_exists`)

Keine erfundenen Rezensionen, Zitate, Auszeichnungen, Verkaufszahlen oder
biografischen Tatsachen. Keine erfundenen Textstellen.

## Konfiguration

### Global: `config/marketing.yaml`

Marke (`label`, `publisher`, `shelf_url`, `shelf_intro`), Zeitzone, relative
Offsets je Beitrag, **zentrale Plattformlimits** und Lesezeichen fuer die
Themenzuordnung. Limits werden nur hier gepflegt.

### Buchlokal: top-level `marketing:` in `export.yaml`

```yaml
marketing:
  enabled: true                 # Default true, wenn der Block existiert
  campaign_start: ''            # ISO 8601 mit Offset, z. B. '2026-10-01T18:00:00+02:00'
  timezone: Europe/Berlin
  amazon_url: ''                # optionaler Override; sonst website.amazon_url
  media:                        # optionale Bildzuordnung Beitrag -> Datei
    x-t5-content: assets/chapter/chapter-012.jpg
  youtube:
    url: ''                     # oder video_id
    video_id: ''
    public: false               # 'jetzt online' erst bei true
  songs:
    - id: song-01
      title: ''
      file: ''                  # repo-relativ, z. B. assets/audio/song-01.mp3
      lyrics_file: ''
      clip_start_seconds: null  # unbekannt => null, nichts erfinden
      clip_duration_seconds: null
      full_video: ''
      short_clips: []
      credits: []               # nur belegte Produktionsangaben
      ai_generated: unknown     # true | false | unknown
```

Alle Felder sind optional. Ein fehlender Block ist kein Fehler.

## Beitragsfunktionen

| ID | Plattform | Termin | Inhalt | harte Voraussetzungen |
|---|---|---|---|---|
| `x-t0-intro` | X | T+0 | Buchvorstellung ueber den zentralen Konflikt | Amazon-Link |
| `x-t1-song` | X | T+1 | Song-/Clipausschnitt | Song **und** Amazon-Link |
| `x-t2-youtube` | X | T+2 | Ankuendigung des vollstaendigen Songs | Song **und** YouTube-Link |
| `yt-main` | YouTube | T+2 | Liedvideo (Titel, Beschreibung, Shotlist) | Song, YouTube-Link, Amazon |
| `yt-short-1` | YouTube | T+3 | Short: musikalischer Einstieg | Song |
| `x-t5-content` | X | T+5 | eigenstaendiger inhaltlicher Gedanke | Amazon-Link |
| `x-t8-sample` | X | T+8 | echte Leseprobe oder belegbare Besonderheit | Amazon-Link |
| `yt-short-2` | YouTube | T+10 | Short: inhaltlicher Einstieg | – |
| `x-t12-second-angle` | X | T+12 | zweiter thematischer Zugang | Amazon-Link |

Ohne Songdaten werden die Musikpositionen **nicht** mit Ersatztext gefuellt,
sondern als `omitted` bzw. `blocked` mit Grund dokumentiert. Ein Link allein ist
kein Beitrag: X-Positionen ohne Text bleiben `needs_review`.

## Termine

`marketing.campaign_start` (ISO 8601) erzeugt konkrete Zeitpunkte in
`Europe/Berlin`. Ohne Startdatum bleibt `scheduled_at` leer und nur der relative
Termin (`T+0` … `T+12`) gilt. Der Kampagnenstart ist **nicht** das
Erscheinungsdatum; ein bereits veroeffentlichtes Buch kann spaeter eine neue
Kampagne erhalten.

Auf Windows liefert Python ohne `tzdata` keine Zeitzonendaten. Deshalb steht
`tzdata` in `requirements.txt`, und `marketing_campaign.berlin_tzinfo()` faellt
ohne Daten auf eine deterministische EU-Sommerzeitregel zurueck (Unsicherheit
nur innerhalb der Umstellungstunde).

## Statuswerte

Textlage und Veroeffentlichungsreife sind getrennt:

* `text_status`: `generated` | `ready` | `over_limit` | `missing`
* `publish_status` / `status`: `generated` | `ready` | `needs_review` |
  `needs_amazon_url` | `needs_youtube_url` | `blocked` | `omitted`

Jeder Beitrag fuehrt zusaetzlich `reasons[]` (konkrete Gruende) und
`depends_on[]` (Voraussetzungen):

* Amazon-Link fehlt → `needs_amazon_url`, Platzhalter `amazon_url`.
* YouTube-Link fehlt → Text fertig, `needs_youtube_url`.
* YouTube-Link vorhanden, Video privat → `blocked` (`youtube_video_not_public`).
* Song im Datensatz, Datei fehlt → `blocked` (`song_file_missing`).
* Kein Songdatensatz → `omitted` (`no_song_data`).
* Kein Text vorhanden → `needs_review` (`text_missing`).
* Text ueber Limit → `needs_review` (`weighted_chars_over_limit`).

Ein versandfertiger Beitrag (`publish_status: ready`) darf keinen offenen
Platzhalter enthalten; `check_no_placeholders_in_ready()` bricht sonst beim
Schreiben ab.

## Zeichengrenzen

Zentral in `config/marketing.yaml`:

* X: 280 gewichtete Zeichen, redaktionelles Zielband 220–250
* YouTube-Titel: 100 Zeichen
* YouTube-Beschreibung (Liedvideo und Shorts): 5000 Zeichen

`weighted_length()` ist eine **konservative Naeherung** und **keine
Plattformvalidierung**: URLs zaehlen als 23 Zeichen (t.co-Umleitung), breite
Zeichen (CJK/Vollbreite) und Emoji als 2, kombinierende Zeichen als 1 (bewusst
nicht 0, damit die Naeherung nicht untertreibt). Bei Ueberlaenge wird zuerst der
Text gekuerzt, niemals der Link und niemals mitten im Satz.

## Ausgabedateien

```
books/<id>/exports/marketing/
  campaign.json   # maschinenlesbares Manifest (Uebergabe an Postiz o. Ae.)
  posts.md        # X-Beitraege mit Status, Zeichenzahl, Link, Medien
  youtube.md      # Liedvideo und Shorts inkl. Shotlist
  media.json      # Medienuebersicht, repo-relative POSIX-Pfade
  README.md       # Hinweise, offene Angaben, Pflegeanleitung
```

Das Manifest enthaelt u. a. `schema_version`, Buch-/Editionsdaten,
`data_sources`, `amazon`, `youtube`, `songs`, `campaign`, `posts`,
`youtube_materials`, `media`, `missing`, `validation`, `delivery` und
`text_provenance`. Jedes Beitragsobjekt enthaelt `id`, `campaign_id` (stabile ID
aus Buch-ID und Beitragsfunktion), `platform`, `type`, `offset_days`,
`scheduled_at`, `title`/`text`/`description`, `primary_link`, `secondary_links`,
`media`, `shotlist`, `related_video_ref`, `profile_ref`, `status`, `reasons`,
`depends_on`, `placeholders` und `validation`.

Medien werden **repo-relativ** referenziert, damit das Paket uebertragbar bleibt.

## Angaben pflegen

| Angabe | Ort |
|---|---|
| Amazon-Link der konkreten Ausgabe | `export.yaml` → `website.amazon_url` (oder `marketing.amazon_url`) |
| Kampagnenstart | `export.yaml` → `marketing.campaign_start` (ISO 8601) |
| YouTube-Adresse bzw. Video-ID | `export.yaml` → `marketing.youtube.url` / `.video_id` |
| Veroeffentlichungsstatus des Videos | `export.yaml` → `marketing.youtube.public` |
| Songdaten | `export.yaml` → `marketing.songs` (`file`, `title`, `lyrics_file`, `clip_start_seconds`, `clip_duration_seconds`, `credits`, `ai_generated`) |
| Bildzuordnung | `export.yaml` → `marketing.media` (`<post-id>: assets/chapter/chapter-012.jpg`) |
| Marke, Shelf-URL, Limits | `config/marketing.yaml` |

Der Amazon-Link wird als **Benutzerangabe** uebernommen; es findet keine Pruefung
gegen die Amazon-Ausgabe statt (keine Suchseite, keine erfundene URL). Eine
bloss syntaktisch gueltige URL ist kein Beleg fuer eine Veroeffentlichung.

## Texterzeugung

Ein Standardlauf (ohne `--provider`) erzeugt **keine** API-Kosten: es werden nur
vorhandene Texte verwendet.

| Provider | Wirkung |
|---|---|
| `workspace_ai` | schreibt `work/marketing/generation-request.md` (Datenbrief + Auftrag) und legt einen leeren Textrahmen in `generated.json` an |
| `prompt_file` | schreibt den vollstaendigen Prompt nach `work/prompts/marketing/<book>-marketing-<style>.md` |
| `openrouter` | nutzt den bestehenden Client, Modell und `ai.reasoning_effort` aus `book.yaml`; der gesendete Prompt wird unter `work/prompts/sent/` archiviert |

### Wiederholbarkeit

* Generierte Texte: `books/<id>/work/marketing/generated.json`
* Manuelle Fassung: `books/<id>/work/marketing/overrides/<post-id>.md` (hat
  Vorrang, wird als `source: override` gekennzeichnet und macht den Beitrag
  `ready`)
* Neu erzeugt wird nur bei geaendertem Quellhash (Metadaten + Leseprobe),
  geaenderter `prompt_version` oder `--regenerate`. `generated_at` allein loest
  **keine** Neuversion aus.
* Ein erneuter Export erzeugt keine neuen Beitrags-IDs und keine neuen Texte.
* Wird spaeter nur die Amazon- oder YouTube-Adresse ergaenzt, aendern sich
  Linkfeld, zusammengesetzte Texte und Validierung – nicht die Kampagne.

### Prompt-Eingaben

Der Datenbrief enthaelt Metadaten, Glossar, Limits und **eine** echte Leseprobe
– bewusst nicht den ganzen Roman. Editoriale Vorabsaetze (Blockzitate wie die
Vorspaenne in Peter I) werden als Zitatquelle uebersprungen, weil sie nicht aus
dem Original stammen.

## Medienzuordnung

* Cover → `x-t0-intro` und als Thumbnail-Vorschlag (`yt-main`)
* `x-t8-sample` → Kapitelbild des Kapitels der Leseprobe
* `x-t5-content`, `x-t12-second-angle`, `yt-short-2` → thematisch passendes
  Kapitelbild (Vergleich der Inhaltswoerter von Beitrag und Kapiteltext); ohne
  Treffer ein gleichmaessig verteiltes, noch nicht verwendetes Kapitel
* `x-t1-song`, `yt-main`, `yt-short-1` → Szenenbild, sonst Kapitelbild, sonst Cover
* `_alt`-Dateien und Varianten wie `chapter-007-a.jpg` gelten nicht als eigenes
  Kapitelbild
* explizite Zuordnung ueber `marketing.media` gewinnt immer

Es wird nie automatisch nur das erste Bild des Buches verwendet; bei knappem
Bildmaterial werden Bilder gleichmaessig wiederverwendet (`reused: true`),
statt Beitraege ohne Bild zu lassen.

Fuer noch nicht produzierte Videos entsteht eine **Shotlist** (Reihenfolge,
Bildquelle, Texteinblendung, Buchbezug, Audioquelle, bekannte Startzeit/Dauer,
fehlende Angaben). Vorgeschlagene Dauern und tatsaechlich gemessene Timecodes
werden getrennt gefuehrt (`duration_measured: false`).

## YouTube: Beschreibung und Shorts

```
Das Buch auf Amazon: <Amazon-URL>
Weitere Buecher von Motivatier Classics: <shelf_url>

<Vorschau>
<2-4 Saetze zu Roman und Song>
<Autor - Buch>
<belegte Editionsangaben>

Begleitsong zum Roman: eigenstaendige Musik zum Buch, kein Hoerbuch und
kein Originaltext des Autors.
```

Titelmuster (`build_youtube_title`): `Buchtitel - Songtitel | Lied zum Roman von
Autor`, ohne Songtitel `Buchtitel - Lied zum Roman von Autor | Motivatier
Classics`; gekuerzt auf die maximale Titellaenge, ohne mitten im Wort
abzuschneiden.

Normale URLs in Shorts-Beschreibungen sind nicht zuverlaessig anklickbar.
Deshalb enthalten die Shorts strukturierte Anweisungen (`related_video_ref`,
`profile_ref`) fuer die spaetere Veroeffentlichung – es wird **nicht**
behauptet, dass der Export einen klickbaren Verweis eingerichtet hat.

## KI-Kennzeichnung

`delivery.requires_synthetic_media_disclosure` ist `true` (mindestens ein Song
als KI-generiert gefuehrt), `false` (alle Songs als nicht KI-generiert gefuehrt)
oder `unknown` (keine oder unklare Angaben) – jeweils mit `..._basis` als
Begruendung. `made_for_kids` bleibt `not_set` und ist ausdruecklich unabhaengig
davon; aus der Kennzeichnungspflicht wird keine Zielgruppenangabe abgeleitet.

## Bedienung

```bash
# Nur planen, nichts schreiben, kein API-Call
python tools/export_marketing.py --book peter-i-buch-01 --dry-run

# Paket aus vorhandenen Texten erzeugen (keine Kosten)
python tools/export_marketing.py --book peter-i-buch-01

# Textrahmen als Repository-KI anlegen
python tools/export_marketing.py --book peter-i-buch-01 --provider workspace_ai

# Texte ueber OpenRouter neu erzeugen (kostenpflichtig, nur mit Freigabe)
python tools/export_marketing.py --book peter-i-buch-01 --provider openrouter --regenerate

# Alle Buecher mit marketing-Block (ohne Provider keine Kosten)
python tools/export_marketing.py --all --dry-run
```

Dashboard: Seite **Export** → Karte **Marketingpaket** (Amazon-Status,
Musikmaterial, offene Beitraege, Beitragstabelle, Dry-Run und Start als
Hintergrundjob) plus Sektion **X-Clip (MP4 aus Cover + Song)**. API:
`GET /api/books/{id}/marketing?style=<style>` und die Actions
`marketing_export` bzw. `render_x_clip` ueber `/api/actions/plan` bzw. `/api/jobs`.

## X-Clip fuer X (MP4 aus Cover + Song)

X spielt keine reinen Audiodateien ab. Deshalb rendert
`tools/render_x_clip.py` ein quadratisches Covervideo: unscharfer
Vollformat-Hintergrund aus dem Cover, scharfes Cover mittig, darunter der
Song-Ausschnitt als AAC-Ton (H.264, 1080x1080, 30 fps, `faststart`).

```bash
py -3 tools/render_x_clip.py --book peter-i-buch-01 --dry-run
py -3 tools/render_x_clip.py --book peter-i-buch-01 --song song-01 --start 0 --duration 45
py -3 tools/render_x_clip.py --book peter-i-buch-01 --song song-01 --start 0 --duration 45 --overwrite
```

Ausgabe: `books/<id>/exports/marketing/clips/<song>-x-<dauer>s.mp4` plus
Kontrollbild `-check.jpg`. Quellen (Cover, Audio) werden nicht veraendert.
Benoetigt System-ffmpeg/ffprobe im PATH (kein Python-Paket; z. B.
`winget install --id Gyan.FFmpeg`).

Der Clip ist bewusst ein Derivat unter `exports/` (reproduzierbar, Parameter
im Job-Log) und gehoert nicht unter `assets/`.

Grenzen (V1): statisches Cover (kein Ken-Burns), keine Refrain-Automatik
(Start/Dauer sind Parameter und werden dokumentiert), keine
Lautheitsnormalisierung (nur Warnung bei fuehrender Stille).

## Beitraege fuer X kopierfertig posten

Quelle ist immer `exports/marketing/posts.md`. Jeder Beitrag steht dort als
Fenced-Text-Block und enthaelt Status, gewichtete Zeichenzahl, Hauptlink und die
zugeordneten Medien.

* **Ohne hinterlegten Amazon-Link** enthaelt der Text nur den redaktionellen
  Teil – die Zeichenzahl im Manifest entspricht dann genau dem Text.
* **Mit hinterlegtem Amazon-Link** setzt der Exporter `\n\n` + Adresse an das
  Ende. Fuer die Zeichenrechnung gilt deshalb
  `gewichtete Zeichen = Text + 2 + 23`. Liegt das Ergebnis ueber dem Zielband,
  den Text kuerzen – nicht den Link.
* Ein Link ist fuer die Veroeffentlichung nicht zwingend: Der Beitrag bleibt
  auch ohne Adresse verstaendlich. Sobald die Amazon-URL gepflegt ist, ergaenzt
  ein erneuter Export sie automatisch.
* Ein gekuerzter oder redaktionell ueberarbeiteter Text gehoert nach
  `work/marketing/overrides/<post-id>.md`; er hat Vorrang, wird als
  `source: override` gefuehrt und macht den Beitrag bei vorhandenem Link
  `ready`.
* Als Bild dient die im Manifest zugeordnete Datei. Fuer X ist die kompakte
  Exportkopie (z. B. `assets/covers/<name>.jpg`) meist geeigneter als der
  PNG-Master.
* Hashtags, kuenstliche Dringlichkeit und „Jetzt erschienen" sind bewusst nicht
  Teil der Texte; „Jetzt erschienen" nur bei belegter Neuveroeffentlichung.

## Grenzen

* Keine Anbindung an X, YouTube oder Postiz; das Manifest ist die
  Uebergabeschnittstelle (`delivery.handover`).
* Kein Video-/Audio-Rendering im Marketingexport selbst: das Paket liefert
  Texte und Shotlists; MP4-Clips entstehen separat ueber
  `tools/render_x_clip.py` (Dashboard-Sektion X-Clip).
* Eine URL ist kein Beleg fuer eine Veroeffentlichung: geprueft werden Syntax
  und Herkunft aus dem Buchdatensatz (`assignment: user_provided`).
* `weighted_length` ist eine Naeherung; die Plattformpruefung bleibt beim
  Veroeffentlichen.

## Tests

```bash
python -m unittest tests.test_marketing_campaign tests.test_marketing_prompts tests.test_marketing_api tests.test_render_x_clip
```

Abgedeckt sind u. a. Zeichengewichtung, Zeitzone/Fallback, Termine,
Linkherkunft, Songdatei-Pruefung, Leseproben-Auswahl (ohne Vorspann),
Wiederholbarkeit, Overrides, Statuslogik, Medienzuordnung, Manifest- und
Dateischreiben sowie die unveraenderte Manuskript-Export-Kette.


