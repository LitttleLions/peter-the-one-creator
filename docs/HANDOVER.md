# Handover – Stand 2026-11-11 (Pharao-Druckcover, KDP-Größen, Schriften)

> Für neue Chats: zuerst [AGENTS.md](../AGENTS.md), dann diese Datei.
> Kopierfertiger Einstieg: [uebergabe-prompt.md](./uebergabe-prompt.md) - dort
> steht: erst `README.md` und [kontextanalyse.md](./kontextanalyse.md)
> (Abschnitt 1 + 5) lesen, dann den Stand melden und auf die Aufgabe warten.
> **Diese Datei erst lesen, wenn die konkrete Aufgabe sie braucht.**
> Einstiegskosten und Hebel (gemessen): [kontextanalyse.md](./kontextanalyse.md).

## Letzte Session (2026-11-11 abends, `die-dritte-chronik`: RomanForge-Uebernahme + neue Saetze)

Branch **`main`**. Die Chronik wurde komplett auf die RomanForge-Uebergabe
`7357431a` vom 2026-11-11 14:49 gezogen (Modus AKTUALISIEREN, Stufe 2) und
danach in allen Formaten neu gesetzt.

- **48/48 Kapitel uebernommen**, in 10 Paketen zu max. 5 Kapiteln, je Paket
  `assemble_chapter.py` + `review_manuscript --chapter NNN --llm none`.
  Alle 12 Konflikte zugunsten von RomanForge aufgeloest (Nutzerentscheidung).
  **Gate ueber das ganze Buch: ERROR=0 / WARNING=0 / INFO=0.**
  Commits `9dcbbe6` (Pakete 1-3) und `7641489` (Pakete 4-10).
- **Kapitel 003 ersetzt**: RomanForge hat "Das Trinkgelage" (2297 Woerter)
  durch "Bittere Mandeln" (3419) getauscht. Der Import blockiert das, weil
  `import_markdown_original.py` bei kollidierender Exportposition der
  vorhandenen Kapitel-ID Vorrang gibt - der erste `--accept 003` setzte
  dadurch nur den Titel und leerte den Text (`state.yaml` mit Leer-Hash
  `e3b0c442…`). Aufgeloest durch Entfernen der 003-Dateien und des
  state-Eintrags, dann frischer Import. Der alte Text liegt in Git (`HEAD`)
  und im Roh-Export `work/imports/romanforge/runs/20261111-140609/`.
  **Bei allen weiteren Paketen vorab Trockenlauf** - keine weitere Kollision.
- `state.yaml`: alle 48 Kapitel mit `rf_base`/`peter_base` aus der neuen
  Uebergabe und fortlaufender `rf_id`.
- **Alle Formate neu** (Textstand 116.986 Woerter):
  - Paperback-Innenleben `6x9 / long_classic / chapter_head` = **304 Seiten**
    (vorher 262), Bundsteg 15,9 mm, Aussenrand 12,7 mm, Report `status: ok`
    ohne Warnungen
  - `paperback-complete.pdf` = 307 Seiten (Vorderseite + Text + Rueckseite)
  - **Wrap** `cover-wrap-20261111-220024-304.pdf`: 330,5 x 234,9 mm,
    Ruecken **19,3 mm** (vorher 16,64 mm bei 262 Seiten)
  - A5-Lese-PDF `…-20261111-220003.pdf`: 582 Seiten, 148,2 x 209,9 mm
- **Offen**: Chronik bei KDP hochladen (Trim 6 x 9, Creme; Interior
  `…-215856`, **nicht** das Komplett-PDF) und die Druckansicht pruefen.
  EPUB der Chronik ist noch der Stand `20260921-131112` mit altem Text.

## Vorige Session (2026-11-11 nachmittags, Chronik: 4k-Cover, Vita, Untertitel)

Branch **`main`**. Pharao ist bei KDP hochgeladen (Testbuch, Wartezeit) - der
erste Band, an dem die neue Satzlogik geprueft wird. Parallel die Chronik als
zweites Druckbuch aufgebaut.

- **Autorvita ersetzt** (`export.yaml: book.author_bio`, Nutzertext,
  2 Absaetze): Buchstabenspiel, zwei Haelfte Mensch/Maschine, Lehrjahre,
  Motivatier Classics; zweiter Absatz mit dem Zeitraum 1241-1251.
  Literaler YAML-Block (`|`), sonst faellt der Absatzabstand weg.
- **Untertitel festgelegt** (Nutzerentscheidung 2026-11-11): `book.subtitle`
  ist jetzt **"Im Schatten Dschingis Khans"** statt "Die Chronik derer, die
  nicht schreiben duerfen". Zieht in Titelei, EPUB und Druck durch.
- **Druckcover 4k, zweiter Lauf** (`gpt_image_2_5`, `2:3`, `resolution 4k`,
  `quality medium`, Job `444320e4`, 1,25 Credits): **Fatima sitzt in der
  MITTE**, links der alte Mongole (Shigi Qutuqu), rechts der persische
  Schreiber (Juvaini). In allen frueheren Entwuerfen (Ebook-Cover, cover2,
  cover-neu) sass die Frau links - das war falsch. Dazu **Dschingis Khan als
  Geist**: harte Silhouette eines Reiters vor der Sonnenscheibe, Geistheer
  dahinter, im Mittelgrund zwischen Titel und Tisch (Vorbild
  `assets/covers/cover-neu.png`). Prompt unter
  `work/prompts/higgsfield/cover-print-4k-20261111-v2.md`, erster Lauf als
  `…-20261111.md` daneben.

- **Druckdatei** `assets/covers/cover-print.jpg` aus dem zweiten Lauf:
  1838x2775 px, 300 dpi, 6,127 x 9,250 in, nur **0,7 %** Beschnitt (das
  4k-Bild ist 2:3, das Panel 0,662; der Zierrahmen bleibt vollstaendig - das
  Ebook-Cover ist 3:4 und haette 11,7 % seitlich verloren). Der CDN-Download
  brach in beiden Laeufen je einmal mit `WinError 10054` ab (bekannt); der
  Wiederholungsversuch holte die Datei.
- **Print-Satz** `6x9 / long_classic / chapter_head` = **262 Seiten**, Bundsteg
  12,7 mm (Band bis 300), Report `status: warning` nur wegen des
  Bundsteg-Neulaufs. Bei dieser Seitenzahl ist der Bundsteg genau so hoch wie
  der Aussenrand - die Entkopplung wirkt erst bei dicken Buechern.
- **Wrap** `cover-wrap-20261111-142937-262.pdf`: 327,7 x 234,9 mm, Ruecken
  16,64 mm. Gestaltete Rueckseite (Standardpalette) mit Klappentext und der
  neuen Vita.
- **Offen**: Chronik bei KDP als Paperback hochladen und die Druckansicht
  pruefen.

## Vorige Session (2026-11-11 spaeter, `pharao`: Druckcover 4k + 6x9-Satz + Wrap)

Branch **`main`**, gepusht (`32ce84b`). Pharao hatte bis dahin **kein**
Druckcover im KDP-Sinn: `cover-print.png` war 1024x1536 (~182 dpi) und damit
unter dem 300-dpi-Minimum, und seit dem A-D-Vergleich (2026-09-21/27) war kein
Print-Satz mehr gebaut worden - die Schrift-Fixes (`ee90790`) fehlten ihm also.

- **Cover-4k-Neulauf** (`gpt_image_2_5`, `2:3`, `resolution 4k`,
  `quality medium`, Job `eca4c437`, 1,25 Credits): Motiv wie das Ebook-Cover
  (Pharao im Profil, Sonnenscheibe, Heer, Tempel, Obelisk), **Typografie im
  Bild**: `DER` / `PHARAO` / `BOLESLAW PRUS` / `MOTIVATIER CLASSICS`. Ein Lauf,
  alle Woerter korrekt getrennt. Prompt, Job und PNG-Master unter
  `work/prompts/higgsfield/cover-print-4k-20261111.*`.
- **Druckdatei** `assets/covers/cover-print.jpg`: 1838x2775 px, **300 dpi**,
  6,127 x 9,250 in - genau die Panelbreite (6x9 + 0,125 in Beschnitt).
- **Print-Satz** `6x9 / long_classic / full_page` = **674 Seiten**, Bundsteg
  19,1 mm, Report `status: ok`, keine dpi-Warnung (die 1152x1536-Kapitelbilder
  ergeben bei `full_page` ~446 dpi). Schriften nur `EBGaramond-Regular` und
  `-Italic`, beide als Type0/`FontFile2` eingebettet.
- **Wrap** `cover-wrap-20261111-115542-674.pdf`: 13,930 x 9,250 in
  (353,9 x 234,9 mm), Ruecken **42,80 mm** (674 x 0,0635 mm), eine Seite.
- **`chapter_head` als Alternative gemessen** (verworfen): 640 statt 674 Seiten,
  also 34 weniger, Report ebenfalls `ok`. Das Bild sitzt dort als Vignette
  unter dem Kapiteltitel und ist schmaler; `full_page` gibt den Kapitelbildern
  die ganze Seite. Entscheidung beim Nutzer offen - ein Wechsel verlangt einen
  neuen Satz **und** einen neuen Wrap (Ruecken dann 40,64 mm).
- **`export.yaml` hat jetzt feste Print-Defaults** (`trim_size`, `layout_profile`,
  `illustration_mode`, `paper`). Vorher fiel Pharao ohne CLI-Flags auf
  5,5x8,5/classic/full_page zurueck = **924 Seiten**, ueber dem Cream-Limit 776.
- **Gestaltete Umschlagrueckseite** (2026-11-11): Papierweiss statt Weiss,
  Titel in Rotbraun, Zierlinie mit Ornament, Klappentext mit Initiale, Tagline,
  Herodot-Zitat, Block "Ueber den Autor", Ruecken mit Verlauf und Ornamenten.
  Gestaltet ist seit `d73694f`/diesem Stand der **Standard fuer alle Buecher**;
  schlicht nur noch mit `print.back_cover.styled: false`. Ohne eigene Farben
  gilt die neutrale Palette (`DEFAULT_BACK_COLORS`: #f7f4ee / #3c332a /
  #a89478), die Autorenbio kommt aus `book.author_bio`, wenn nichts gesetzt ist.
  Damit bekommt jede KI bei einem neuen Print-Lauf automatisch das neue Format.
- **Marke vs. Verlag, Cover-Textblock** (2026-11-12): Herausgeber = Marke "Motivatier Classics" (`book.editor`, oben auf Titel/Rueckseite/Ruecken), Verlag = "Motivatier Stiftung" (`book.publisher`, klein unten/Impressum). `lib/print_wrap.py brand_line()` mit Rueckfall (translator mit Herausgabe-Label, dann Verlag). Neu `tools/cover_text.py` (Typografie-Block fuer Titelbild-Prompts aus den Buchdaten). Sprache des Anderen: Prompt `cover-print-4k-20261112-v3.md` bereit, Titelbild noch nicht neu generiert; danach `build_cover.py` neu.
- **Umschlagrueckseite, Gestaltungsdurchgang** (2026-11-12, `tools/lib/print_wrap.py`):
  - Barcode: nur Platz (2 x 1,2 in unten rechts, `.barcode-reserve`), nichts
    gemalt; der Text endet darueber. Masse vor Umstellung gegen die KDP-Hilfe pruefen.
  - Farben: Rueckseite und Ruecken kommen aus dem linken Randstreifen des
    Druckcovers (hell/dunkel, Kontrast >= 7:1, sonst `DEFAULT_BACK_COLORS`);
    `print.back_cover.colors` gewinnt je Schluessel (neu: `spine`, `spine_text`).
  - Felder: Kopfzeile = `book.series`, sonst `book.publisher`, sonst leer; Untertitel
    (<= 60 Zeichen) unter dem Titel; Verlag als Fusszeile; leere Felder erzeugen
    keine Elemente.
  - Satz: `lang`, Silbentrennung, Spalte ca. 100 mm, Initiale nur bei Buchstaben.
  - Passung: `render_fitted_wrap_html` misst im Browser und geht ueber `FIT_LEVELS`
    (Fliesstext 10,5 -> 9,0 pt, Bio 8,8 -> 8,2 pt, zuletzt Zitat weg; die Bio bleibt).
    Passt nichts, meldet `build_cover.py` einen Fehler (Klappentext kuerzen), der
    Export eine Warnung. Es wird nie automatisch gekuerzt.
  - Ruecken: unter 79 Seiten kein Text; Schrift = min(14 pt, 0,45 x Rueckenbreite);
    Ornamente ab 12 mm, Verlag ab 25 mm.
- **Inhaltsverzeichnis auf Gruppen reduziert** (`front_matter.toc_depth: groups`,
  neu in `export_manuscript.py`): Pharao listet nur **Buch I-III** statt 69
  durchgezaehlter Kapitel ("Erstes Kapitel" ... "Neunundsechzigstes Kapitel"),
  die in einer Liste nichts sagen und bei KDP als viele Markierungen auffallen.
  Gilt fuer PDF/EPUB und DOCX; `chapters` bleibt der Default, andere Buecher
  sind nicht betroffen. Der Satz schrumpfte dadurch auf **638 Seiten**
  (vorher 640); mit der Kataloggrenze unten sind es **637 Seiten**.
- **Reihenkatalog auf zwei Seiten begrenzt** (`CATALOG_LIMIT = 6`, je drei
  Eintraege pro Seite): Pharao hatte 7 Katalogtitel, der siebte landete allein
  auf Seite 638 mit zwei Dritteln Leerraum. Jetzt endet der Katalog auf zwei
  vollen Seiten; Satz **637 Seiten**, Ruecken 40,44 mm, Wrap
  `cover-wrap-20261111-130901-637.pdf`. Gilt fuer alle Buecher und alle
  Formate (EPUB, PDF, Paperback, DOCX); die volle Liste gibt es weiter ueber
  `load_series_catalog(..., limit=None)`.
- Alte Stempel geloescht: die 674er-`full_page`-Familie (Interior + Wrap) und
  die 09/2026-Staende. Im print-Ordner liegt nur die aktuelle 637er-Familie.
- **Satzspiegel: Aussenrand vom Bundsteg entkoppelt** (Nutzerentscheidung
  2026-11-11, Befund aus der KDP-Druckvorschau). Bisher galt
  `aussen = innen = max(Bundsteg, min_outer)`; da der Bundsteg mit der
  Seitenzahl waechst, wurde der Satzspiegel bei dicken Buechern unnoetig
  schmal. Bei Pharao lagen aussen 19,1 mm an, wo KDP nur 6,4 mm verlangt.
  Jetzt: aussen fest 12,7 mm, innen 19,1 mm, umgesetzt ueber
  `@page :left`/`:right` in `print_css.py` (Chromium kann das; mit einem
  Testlauf geprueft). Satz **609 statt 637 Seiten**, Ruecken 38,67 mm,
  Wrap `cover-wrap-20261111-132822-609.pdf`. Gilt fuer alle Buecher - die
  Seitenzahlen aller Buchpakete aendern sich beim naechsten Printlauf.
- **Offen**: KDP-Upload (Interior `…-head-20261111-132746` + Wrap
  `cover-wrap-20261111-132822-609`), danach Druckansicht bei Amazon pruefen.

## Letzte Session (2026-11-11, KDP-Paperback: Covergröße und Schriften)

Branch **`main`**, gepusht (`4784d6a`). Der Paperback-Upload schlug zweimal fehl;
beide Ursachen sind gefunden und behoben.

### 1. Die Covergrößen-Meldung auseinanderrechnen (wichtig)

KDP: *"Die erwartete Covergröße beträgt 13.080x9.250, die eingereichte
Dateigröße jedoch 12.070x8.750."* Aus diesen zwei Zahlen liest man Trim und
Innenseitenzahl direkt ab:

```text
Höhe:      9,250 in − 2 x 0,125 in Beschnitt = 9,00 in  -> Trim 6 x 9 in
Breite:   13,080 in − 2 x 6 in − 2 x 0,125 in Beschnitt = 0,83 in Ruecken
Ruecken:   0,83 in / 0,025 in je Seite (0,0635 mm) = 332 Seiten
Unser PDF: 12,070 x 8,750 in  -> 5,5 x 8,5 in und 330 Seiten
```

**Merksatz:** Die Cover-Meldung nennt nie Trim und Seitenzahl direkt - man
rechnet sie zurueck. Formeln (Creme/SW):

```text
Breite  = 2 x Trim + Ruecken + 2 x 0,125 in     Ruecken = Seiten x 0,0635 mm
Hoehe   = Trim + 2 x 0,125 in
```

Gegenprobe fuer unseren 5,5x8,5-Satz: 2 x 5,5 + 0,25 + 330 x 0,0635/25,4
= **12,075 x 8,75 in** - genau die eingereichte Datei, also rechnerisch korrekt;
nur die Formularwerte passten nicht.

**Zwei typische Fehlerquellen:**
- **Komplett-PDF statt Interior hochgeladen.** `paperback-complete.pdf` enthaelt
  zwei zusaetzliche Umschlagseiten; KDP zaehlt dann 332 statt 330 und erwartet
  einen breiteren Ruecken. Hochzuladen ist immer `-paperback-interior.pdf`.
- **Trim im Assistenten** nicht auf den Satz gestellt (6x9 statt 5,5x8,5 bzw.
  umgekehrt).

### 2. Schriften: variable Fonts und Helvetica-Folios

KDP: *"Die Schriftarten wurden nicht ordnungsgemäß in Ihrer Datei eingebettet."*
Ursache war doppelt:

- `assets/print-fonts/eb-garamond/EBGaramond*.ttf` sind **variable Fonts**
  (`fvar`/`gvar`/`HVAR`). Chromium bettet variable Fonts nicht als TrueType ein,
  sondern zeichnet die Glyphen als **Type3-Pfade** - im PDF stehen dann
  Hunderte `/Type3`-Fonts ohne `/BaseFont`. Fix: statische Instanzen mit
  `wght=400` erzeugen und in `config/print.yaml` eintragen:
  `EBGaramond-Regular-static.ttf`, `EBGaramond-Italic-static.ttf`.
  Erzeugt mit `fontTools.varLib.instancer.instantiateVariableFont`.
- Die **Seitenzahlen (Folios)** kamen aus einem Helvetica-Overlay
  (`_helvetica_overlay_pdf`, base-14, nicht eingebettet). Chromium setzt selbst
  keine Seitenzahlen. Fix: `_folios_overlay_pdf()` rendert **alle** Folios in
  einem Chromium-Durchlauf mit der Hausschrift als ein Overlay-PDF, das
  seitenweise gemergt wird.

Ergebnis nach dem Fix: Schriftspannen im Innenleben nur noch
`EBGaramond-Regular` und `EBGaramond-Italic`, beide als `/Type0` mit
`/FontFile2` eingebettet; kein Helvetica, kein Type3.

### 3. Neues Werkzeug: nur den Umschlag bauen

`tools/build_cover.py` erzeugt **allein** den Wrap (Rueckseite, Ruecken,
Vorderseite) aus Trim, Papier und Seitenzahl - ohne den Satz neu zu rendern,
und prueft die Ausgabegroesse gegen die Rechnung (Exit 1 bei Abweichung).

```bash
python tools/build_cover.py --book die-sprache-des-anderen --page-count 332 --trim-size 6x9
python tools/build_cover.py --book die-sprache-des-anderen --page-count 330 --trim-size 5.5x8.5 --dry-run
```

Aufruf fuer den KDP-Stand dieser Sitzung: 6x9, 332 Seiten, Creme ->
Ruecken 21,08 mm, Umschlag 13,083 x 9,250 in (332,3 x 234,9 mm), eine Seite,
Titelbild 1725x2625 px, Schrift eingebettet. Datei:
`exports/stil-01-original/book/print/cover-wrap-<stempel>-332.pdf`.

### 4. Stand und Offenes

- **Print-Ordner ist geleert** (Nutzerwunsch): bis auf den frisch gebauten
  Umschlag liegt nichts mehr unter `exports/.../print/`. Vorher wurden
  Familien `172026` (5,5x8,5) und `234212` (6x9) samt Manifesten verworfen.
- Offen: im KDP-Formular **6 x 9 in, Creme** einstellen und den Wrap hochladen;
  danach den passenden Innenleben-Satz neu erzeugen
  (`--format paperback-complete --trim-size 6x9 --illustration-mode chapter_head`,
  ergab 271 Innenseiten - dann Ruecken mit 274 statt 332 neu bauen!).
- **Achtung Seitenzahl-Kopplung:** Der Rücken haengt an der Seitenzahl, und die
  Seitenzahl am Trim und am Bildmodus. Nach jedem Satzlauf mit
  `build_cover.py --page-count <echte Seiten>` den Wrap neu bauen. Die echte
  Zahl steht in `*-print-report.json` unter `page_count` - **nicht** aus dem
  Kopf oder aus einem aelteren Lauf nehmen. Gegenprobe: `build_cover.py`
  vergleicht die Wrap-Breite mit `2 x Trim + Ruecken + 2 x 0,125 in` (Exit 1
  bei Abweichung); zusaetzlich `page_count` im Report gegen die Seitenzahl im
  PDF (`PdfReader(...).get_num_pages()`) stellen.
- Nebenbefund: `tests.test_backend_api` hat zwei rote Tests
  (`translate_batch` mit `ollama_model=gemma4:latest`), weil lokal Ollama laeuft
  und nur `gemma4:e4b` kennt. Vor dieser Sitzung schon rot, unabhaengig vom
  Cover.

## Vorige Session (2026-11-10 spaeter, Autorenvita + Reihenmetadaten)

Branch **`main`**, gepusht. Zwei Nacharbeiten zum Cover-Stand:

- **Autorenvita ersetzt** (`export.yaml: book.author_bio`, 2 Absaetze,
  112 Woerter, Nutzertext): neuer Satz mit Herkunft (Buchstabenspiel),
  Lehrjahren (Handschriftensammlungen/Rechenzentren), Motivatier Classics,
  Arbeitsteilung Mensch/Maschine und dem Reihen-Leitsatz "politische Grenzen
  wandern schneller als die Verbindungen der Menschen" (842, Strassburg
  bis Verdun). Seite "Leben des Autors" im Druck-PDF (S. 4) geprueft.
- **Reihenmetadaten sind jetzt Code, nicht nur YAML.** Neu:
  `add_epub_series_metadata()` in `tools/export_manuscript.py` schreibt
  `belongs-to-collection`, `collection-type: series` und `group-position` aus
  `book.series` + `book.series_volume` ins OPF (idempotent, XML-escaped,
  ohne `series` ein No-op); das Export-Manifest traegt `series` und
  `series_volume`. Zwei neue Tests in `tests/test_export_manuscript.py`,
  volle Suite **400 Tests OK**. Dokumentiert in `README.md` (Export) und
  `AGENTS.md` (Export).
- **Fallstrick notiert**: `>-` in YAML faltet den Absatzabstand zu einem
  einzelnen `\n`; mehrAbsatzige Felder (`summary`, `author_bio`,
  `description`) brauchen einen literalen Block (`|`), sonst sieht der Export
  nur einen Absatz. Die Bio stand zuerst als `>-` im YAML und wurde deshalb
  umgestellt.
- **Neue Exporte** (Bio + Reihenmetadaten): EPUB `...-20261110-155537.epub`,
  Print-Satz `155553` (Innenleben 330, Komplett 332, Wrap 306,6 x 222,2 mm -
  Seitenzahl unveraendert, Ruecken bleibt 20,96 mm), A5-PDF `...-155607.pdf`.
  Die vorherigen Staende `141553`, `143217`, `143234` sind ueberholt.
- **Offen**: KDP-Upload (Manuskript `155553` + Wrap), Kindle-Preview,
  Cover-Text "Band 1" -> "Band 2" beim naechsten Coverlauf,
  Tippfehler `ann, 25 Jahre` bei Gerwin in RomanForge.

## Vorige Session (2026-11-10 abends, 4k-Druckcover + Wrap-Fehler behoben)

Branch **`main`**. Schwerpunkt Cover: das Druckcover war ein 2k-Motiv (real
~241 dpi) mit per Skript gesetzter Typografie, ohne Zierlinie, Tagline und
Badge, und mit einem anderen Motiv als das Ebook-Cover.

- **Druckcover neu, Text im Bild** (`gpt_image_2_5`, `2:3`, `resolution 4k`,
  `quality medium`): 2336x3504, alle Texte im Bild - Titel mit grossem A und
  Zierschleife, Zierlinie mit Ornament, `Zwischen Rhein und Maas`, Vierzeiler,
  `Historischer Roman`, Badge `Romanreihe Band 1`, `Motivatier Stiftung`.
  In 100 %-Ansicht geprueft, fehlerfrei. Prompt und Job-JSON unter
  `work/prompts/higgsfield/cover-print-4k-20261110*.md|json`;
  `-v2` brachte die Randregel.
- **Druckdatei**: auf 5,75 x 8,75 in beschnitten (1725x2625 px, 300 dpi im
  JPEG), Bild 20 px nach unten verschoben und die obere Himmelszeile
  gespiegelt/geblurrt ergaenzt, damit jeder Text im 0,25-in-Sicherheitsabstand
  liegt (Titel y=118, Fusszeile 174, Tagline x=114; Beschnitt 37,5 px).
  Das Panel des Wrap ist 5,625 in breit, deshalb liegen die Raender im PDF
  bei ~0,25 in.
- **Ebook-Cover**: `cover.png` (720x1004) ersetzt durch `cover.jpg`
  (1725x2625, dasselbe 4k-Motiv). Zwei 3:4-Versuche wurden verworfen, weil der
  Renderer Wortabstaende verschluckte (`DESANDEREN`, `MOTIVATIERSTIFTUNG`);
  Kandidaten und Vergleiche in `work/cover-candidates/`.
- **Wrap-Fehler gefunden und behoben** (`tools/lib/print_wrap.py`): in
  `.panel`, `.spine` und `.back` stand ein `}}` in einem Nicht-f-String.
  Chromium verwirft darauf die jeweils naechste Regel - `.spine`,
  `.spine span` und `.brand` fielen weg. Folge: Ruecken 2,25 in statt
  0,825 in, Vorderseite gestaucht, Rueckentext ungedreht am Seitenkopf. Das
  galt auch fuer den bis dahin aktuellen Satz `134427`. Fix plus
  Regressionstest in `tests/test_print_export.py`, volle Suite **398 Tests OK**.
- **Neuer Satz `141553`**: Innenleben 330 Seiten, Komplett 332, Wrap
  306,6 x 222,2 mm mit Ruecken 0,825 in; Vorderseite mit dem 1725x2625-Bild
  1:1 eingebettet. Wrap-PDF mit MuPDF gerendert und geprueft. Buch-EPUB
  `...-20261110-143217.epub` (8,03 MB, Cover 1725x2625), A5-PDF
  `...-20261110-143234.pdf`. Alte Print-Familien `134427` und `141334` geloescht.
- **Kosten**: 5,00 Credits fuer die Bilder (Guthaben 563,53 -> 558,53), davon
  0,25 fuer einen Fehlstart (PowerShell schnitt den mehrzeiligen Prompt ab,
  1k/1:1 verworfen) und 2 x 1,25 fuer die verworfenen 3:4-Versuche.
- **Reihe**: `Die Sprache des Anderen` ist **Band 2** der Reihe "Zwischen Rhein
  und Maas"; Band 1 entsteht spaeter (Prequel, ungewoehnliche Reihenfolge).
  Vermerkt in `export.yaml` als `book.series_volume: 2`. Cover (`cover.jpg`,
  `cover-print.jpg`) und die Cover-Prompts nennen noch `BAND 1`; das wird
  bewusst erst beim naechsten Coverlauf gestellt. Epub/PDF drucken keine
  Bandnummer.
- **Offen**: KDP-Upload (Manuskript `141553` + Wrap), Kindle-Preview,
  Tippfehler `ann, 25 Jahre` bei Gerwin in RomanForge. Die ueberholten
  Exporte `132245` (EPUB) und `132328` (A5-PDF, altes Cover) sind geloescht;
  im EPUB-Ordner liegen noch fuenf aeltere Staende aus 2026-10-28/11-09 und
  sechs alte Manifest-Eintraege aus dem Print-Vergleich (132356 ... 134343).

## Vorige Session (2026-11-10 mittags, `die-sprache-des-anderen`: Bilder, Print, Cover)

Branch **`main`**, bis `bbb136e` gepusht. Schwerpunkt war das Bildproblem: die
Kapitelbilder 001-003 sahen fast gleich aus, die Figuren waren zu alt/uneinheitlich.

- **Vignetten-Stufe** (neu, `tools/lib/illustration_vignette.py`): pro Kapitel
  wird *ein* bildtragender Moment gewaehlt und als
  `work/prompts/higgsfield/vignettes/<kapitel>.json` abgelegt (Moment, Figuren,
  Gegenstaende, Ausschnitt, Belegabsaetze, Quelle `heuristic|openrouter|manual`).
  `build_prompt()` baut daraus: Moment -> Figuren -> Gegenstaende/Ausschnitt ->
  kurzer Stilanker (`illustration_setting` max. 700 Zeichen,
  `illustration_world` max. 400). Vorher standen 1.642 Zeichen Ortskatalog vor
  zwei Anfangsabsaetzen; das machte alle Bilder gleich.
- **Aussehen kommt aus dem Glossar**: `names.yaml` (`visual`, aus RomanForge)
  schlaegt das per-Kapitel-`look` der Vignette; die Vignette liefert es nur fuer
  Figuren ohne Eintrag (Folmar, Schmied, Raeuberhauptmann, Guntram, Vogt).
  `figure_looks()` loest `visual_label` zuerst auf - sonst trug `Berto der Sohn`
  das Gesicht des alten Knechts (beide heissen in RomanForge `Berto`).
- **Figuren neu importiert** (Uebergabe `feebc32e`, Modus `update`, 10 Figuren):
  `sync_romanforge_characters.py --force-visual --apply` (neues Flag). 9
  Aussehen-Texte + Umbenennung `Berto der Sohn` -> `Berto`. Alda ist jetzt ~32,
  Raginbert 50 mit Kettenhemd und Schwert, Otwin 29 mit Tonsur.
  `Graf Adalhard` von Hand in `names.yaml` (RomanForge hat ihn nicht; Schreibweise
  des Romans, Alias `Adelhardt`). `Isenbart` war schon von Hand drin.
- **Bilder 001-034** alle neu erzeugt (Vignette je Kapitel, LLM waehlt den Moment,
  ~0,0007 USD pro Kapitel). Kosten der 34 Bilder: je 1 Credit. Ablauf je Kapitel:
  `--vignette-provider openrouter --vignette-overwrite --dry-run` (schreibt
  Vignette + `*-dryrun.md`, kostet kein Bild) -> `--overwrite` (Bild).
- **Download-Fix**: ein fertig gerendertes Bild ging verloren, weil der
  CDN-Download mit TLS-Reset abbrach (`WinError 10054`). `download_url` versucht
  es jetzt dreimal; die Metadaten werden mit `job_result` und `media_url`
  **vor** dem Download geschrieben. Der eine verlorene Job wurde manuell aus der
  `result_url` geholt.
- **Export** (`die-sprache-des-anderen`): EPUB
  `book-die-sprache-des-anderen-stil-01-original-20261110-132245.epub` (8,0 MB,
  34 Kapitelbilder + Cover, Gate 0/0/0), A5-PDF `...-20261110-132328.pdf`
  (6,1 MB). Playwright-Chromium war nicht installiert und wurde nachgezogen
  (118 MB in den Benutzer-Cache).
- **Print**: neuer Bildmodus `chapter_head` (Titel -> Vignette 62 % Breite,
  max. 40 % Satzhoehe -> Text laeuft weiter). Messung bei gleichem Trim/Profil:
  `full_page` 347 Seiten, `inline` 334, `chapter_head` 330. Die dpi-Pruefung
  rechnet jetzt mit der echten Anzeigebreite (Minimum aus Breiten- und
  Hoehenbegrenzung) statt pauschal 72 %: `chapter_head` meldet 0 Warnungen,
  die Bilder liegen bei ~355 dpi (vorher 252 dpi Warnung).
- **Druckcover** neu: Motiv in 2:3 bei 2k erzeugt (1360x2048), auf
  5,5x8,5 + 3,175 mm Beschnitt geschnitten, Typografie mit EB Garamond
  (Titel, Untertitel, Autor, Fusszeile) -> `assets/covers/cover-print.jpg`
  (1690x2585 px). Achtung: die Motivdatei hat real ~241 dpi, wurde auf 300 dpi
  hochskaliert.
- **KDP-Satz** (Stempel `134427`): Innenleben 330 Seiten, Komplett-PDF 332
  Seiten, Wrap 306,6 x 222,2 mm mit Ruecken 20,96 mm (330 Seiten Cream).
  Rueckentext im Wrap ist jetzt zentriert (`print_wrap.py`).
- **Aufgeraeumt**: 10 ueberholte Print-PDFs (258 MB) und ihre Reports geloescht;
  es bleiben nur die drei `134427`-Dateien.
- **Offen**: KDP-Upload (Manuskript + Wrap), Kindle-Preview, ggf. 2k-Neulauf der
  Bilder fuer echten 300-dpi-Druck, Tippfehler `ann, 25 Jahre` bei Gerwin in
  RomanForge korrigieren.

## Vorige Session (2026-11-01, RomanForge-Figuren-Abgleich)

Branch **`main`** (`1535a63`), gepusht. Ausführlich zur Zusammenarbeit beider Repos:
`docs/sitzungs-uebergabe.md` im Repo NovelWriter (RomanForge, `C:\code\NovelWriter` bzw.
`E:\code\NovelWriter`) und [romanforge-figuren.md](./romanforge-figuren.md).

- **Entscheidung:** RomanForge führt nur eigene Originale; Übersetzungen fremder Vorlagen
  bleiben hier und haben keine RomanForge-Figuren. Austausch nur über die Übergabe (API-Schlüssel,
  `.env`: `ROMANFORGE_URL=https://romanforge.littlelionsfilms.de`, `ROMANFORGE_API_KEY`), kein
  direkter Datenbankzugriff, kein Rückkanal.
- **Neu:** `tools/lib/rf_characters.py` und `tools/sync_romanforge_characters.py` (Trockenlauf ist
  Standard, `--apply` schreibt): Spiegel `books/<id>/romanforge/characters.json` und Abgleich mit
  `names.yaml` über `rf_uid`. Peter-Felder (`target`, `aliases`, `type`, `note`, `visual`, `status`)
  werden nie überschrieben. `import_markdown_original.py --new --handoff` legt Spiegel und
  `names.yaml` gleich mit an. 16 Tests in `tests/test_rf_characters.py`.
- **Durchgeführt (Übergaben vom 01.11.2026):** Lotse von Rügen (33 Kapitel identisch, 15 Figuren
  verknüpft), Die Sprache des Anderen (Kapitel 001 aus RomanForge übernommen, Gate 0/0/0; 10 Figuren,
  `Berto` ist der Junge, `Berto der Knecht` der alte Knecht), Ashkar I (36 Kapitel identisch, 8
  Figuren als `draft`, `visual` leer). Commits `36cf93f`, `096dc1e`, `959e035`, `1535a63`.
- **Ablauf je Buch:** `import_markdown_original.py --book <id> --handoff <id> --compare` →
  `sync_romanforge_characters.py --book <id> --handoff <id>` (Trockenlauf) → nach Freigabe `--apply`
  → committen. Abweichende Namen zuerst in RomanForge korrigieren (dort ist die Quelle).
- **Offen:** Lotse Kapitel 31 und 33 enthalten noch „Bille“ (Roman nutzt Holm); `format`/`mode` der
  Übergabe werden nicht geprüft, `rf_id` wird nicht zum Abgleich genutzt, `publication`/Exposé werden
  nicht gelesen (Liste der 19 Punkte: `docs/schnittstelle-peter-offene-punkte.md` im Repo NovelWriter);
  Lektor-Hinweise zu einem Buch stehen aus (Buch, Fassung, Hinweise fehlen noch).
- **Nicht von dieser Session, nicht committet (Rechner C:):** KDP-Werkzeug (`tools/kdp_sync.py`,
  `tests/test_kdp_*`, `tools/lib/kdp_*`), `tools/import_de_original.py`, `tools/sync_book_gitignore.py`,
  `docs/jev-review-plan.md` – bitte sichern oder zuordnen.

## Vorige Session (2026-10-28 abends, Titelei + Cover + Verifikation, Rechner E:)

Branch **`main`**, **kein Commit**, **kein Branch-Wechsel**, keine
kostenpflichtigen Läufe, keine Bildgenerierung.

- **Verifikation komplett grün**: `tests.test_book_project` 2/2,
  `tests.test_import_markdown_original` 41/41, **volle Suite
  `python -m unittest discover -s tests` → 330 Tests OK**. Die in
  `docs/offene-punkte.md` Punkt 9 dokumentierten 5 `test_print_export`-Fehler
  und 2 `test_backend_api`-Fehler sind **nicht mehr reproduzierbar**.
  Chronik-Gate unverändert **ERROR=0/WARNING=13/INFO=36**;
  `die-sprache-des-anderen` 34/34 done, Gate **0/0/0**.
- **Titelei `die-sprache-des-anderen` gefüllt**
  (`books/die-sprache-des-anderen/export.yaml`): `subtitle`
  („Ein Straßburger Roman aus dem 9. Jahrhundert"), `translator`
  („Motivatier Classics") + `translator_label` („Herausgabe und editorische
  Einrichtung"), `rights`, `original_title`, `original_author`,
  `title_page_extra` (4 Zeilen), `imprint_text`, `description`, `summary`,
  `author_bio`. Stoffbasis: Titel aller 34 Kapitel, Einstiege von ca. 24 und
  Auszüge aus ca. 11 Kapiteln (ca. 130 KB); Zeitebene im Text
  (Fontenoy, zwei Könige vor Straßburg, Teilung in drei Reiche) →
  **keine** fixe Jahreszahl im Klappentext, nur „9. Jahrhundert".
  `front_matter.description_page: false` wie bei den Schwestertiteln.
- **Neues Cover vorgefunden** (nicht in diesem Chat erzeugt):
  `assets/covers/cover.png` 720×1004 / 1.045.591 Bytes mit Titel, Autor,
  Serie „Zwischen Rhein und Maas", „Romanreihe Band 1" und Motivatier-Stiftung;
  `cover.jpg` und `cover_alt.jpg` wurden dabei entfernt. Export nutzt daher
  jetzt `cover.png` statt `cover.jpg`.
- **Neuer Buch-EPUB**
  `book-die-sprache-des-anderen-stil-01-original-20261028-203757.epub`
  (5.361.120 Bytes), Manifest `partial:false`, `review_gate_errors:0`,
  `review_gate_bypassed:false`. Im EPUB verifiziert: Cover
  (`<meta name="cover" content="file11_png"/>`), `dc:publisher` „Motivatier
  Stiftung", `dc:rights`, Titelseite + Zusammenfassung + Leben des Autors +
  Impressum als getrennte Seiten, Kapitelbilder 001-003, Reihenkatalog
  „Weitere Motivatier Classics".
- **Doku**: `AGENTS.md`, `README.md`, `docs/offene-punkte.md` (Punkt 14
  abgehakt, neuer Punkt 16).
- **Offen für den Nutzer**: neues Cover gewollt? Soll daraus wieder eine
  kompakte `cover.jpg` entstehen (`optimize_asset_images.py --scope cover`)?
  Commit erst nach Freigabe.

## Vorige Session (2026-10-28 abends, Autor-Fix + Push)

Branch **`main`**, **gepusht** (mit `origin/main` synchron). Der Branch
`cline/pveejb87` ist gelöscht.

- **Autor-Fix**: `tools/assemble_chapter.py` hardcodierte im Kapitelkopf
  `*Buch: {title} - Alexei Tolstoi*`. `render_header()`/`assemble_chapter()`
  nehmen jetzt `book_author`; der Aufrufer reicht `book.get("author")` aus
  `book.yaml` durch. **457** Alt-Dateien in 8 Büchern auf den echten
  Buch-Autor umgeschrieben (Ashkara, Chronik, Arsenjews, Mongolen,
  Kuprin-Moloch, Pissemski, Perfect Sight u. a.). `peter-i-buch-01` bleibt
  korrekt bei „Alexei Tolstoi".
- **Autorenschreibweise**: `die-sprache-des-anderen` schrieb „Timo Veritas"
  (mit s) → jetzt „Timo Verita" in `book.yaml` + `export.yaml`, passend zu
  allen übrigen Büchern. Neuer Export
  `...-20261028-201552.epub` (Autorenzeile „Timo Verita").
- **`origin/main` war 2 Commits vorn** und brachte ein **zweites
  Lotse-Paket** `books/der-lotse` (id `der-lotse`, 32 Kapitel, 32 Bilder,
  Gate ERROR=0/WARNING=1/INFO=42, `website.enabled: false`,
  sort_order 70). Merge konfliktfrei; **beide** Lotse-Pakete bleiben
  erhalten (Kapitel 1–29 Titel identisch, Schlusskapitel unterscheiden sich).
- **Neues Submodul** `tools/vendor/amazon-kdp-skill` (`9194489d`) aus
  `origin/main`; lokal per `git submodule update --init --recursive`
  eingerichtet.
- Offen (nächster Chat): Push ist erledigt; `docs/offene-punkte.md` Punkt 15
  dokumentiert die Details.

## Vorige Session (2026-10-28, Bilder + Aufräumen + Merge nach `main`)

Branch **`main`** (Merge `ce7c1d2`), **kein Push**. Ausgangspunkt war
`cline/pveejb87` (4 Commits darauf, 8 weitere schon vorhanden, `main` 1 Commit
vorn). Alles ist jetzt auf `main`; `cline/pveejb87` ist vollständig
eingesmolzen und kann gelöscht werden.

### 1. Bilder für `die-sprache-des-anderen` (Credits freigegeben)

- `book.yaml`: `illustration_setting` (9. Jh., Straßburg/Ill/Rhein, Winter,
  Heerlager, Franken-Tracht) + `higgsfield:`-Block (`gpt_image_2_5`, 3:4, 1k,
  medium, `image_processing` JPEG q60/1024, Cover q75/1600×2400).
- `names.yaml`: 14 Einträge (6 Personen mit `visual`-Kurzbeschreibung für den
  Figurenblock, 8 Orte). Vorher leer.
- **Kapitelbilder 001–003** via `generate_illustration.py --kind chapter
  --no-reference` (kein Moodboard für dieses Buch, also reiner Prompt).
  Ergebnis: `assets/chapter/chapter-001..003.jpg` (772×1024), stilkonsistent
  und periodisch plausibel (Alda im Vordergrund, Raginbert zu Pferd, Kähne,
  Ketten, Lager).
- **Cover** über die Higgsfield-CLI direkt (`higgsfield generate create
  gpt_image_2_5 --aspect_ratio 2:3 --resolution 2k --quality medium --wait`),
  Job `f2f6da57-…`, 1360×2048 PNG → `assets/covers/cover.png`, dann
  `optimize_asset_images.py --scope cover` → `cover.jpg` (482 KB) +
  `cover_alt.jpg` (Archiv).
- **Wichtig:** `tools/generate_illustration.py` kann **kein Cover** (nur
  `--kind chapter|scene`). Cover laufen über die CLI + `optimize_asset_images.py`.
- Gate danach erneut: **ERROR=0 / WARNING=0 / INFO=0**, Exit 0.
- Neuer Buch-EPUB `book-die-sprache-des-anderen-stil-01-original-20261028-195240.epub`
  (4.806.312 Bytes), Manifest `partial:false`, `review_gate_errors:0`,
  `review_gate_bypassed:false`, 3 Illustrationen, Cover als `cover-image`
  registriert (`<meta name="cover" content="file11_jpg"/>`).

### 2. Aufräumen

- **Gelöscht** (per Freigabe): `SUMMARY.md`, `SUMMARY_FINAL.md`,
  `tools/create_placeholders.py`, `books/existing/` (Wegwerf-Testpaket:
  id `existing`, Autor „Testautor", Inhalt = Chronik-Kopie; stand mit
  `website.enabled: true` im **Reihenkatalog des EPUB**), `.scratch-lotse/`
  (Scratch im Repo-Root), `test.jpg`, `hub_logos_request.json`,
  `hub_logos_request_decoded.md`.
- **Behalten**: `books/perfect.sight/` (echtes Sachbuch-Paket, 594 Dateien) +
  `tools/{analyze,generate,import,process}_perfect_sight*.py`; die 4
  `books/der-lotse-von-ruegen/assets/chapter/chapter-00{5..9}`-PNG+`_alt`-Paare.
- `books/die-dritte-chronik/source/Die dritte Chronik(1).md` bleibt **lokal
  untracked** (Browser-Download-Kopie der versionierten Quelle, `source/` ist
  tabu).

### 3. Merge

- 4 Commits auf `cline/pveejb87`: `4d382d1` Einstieg-Härtung + Doku,
  `08087d0` beide Buchpakete, `8776da2` Perfect Sight, `9a3f625` Review-/
  Exportartefakte. Merge auf `main`: `ce7c1d2` (ort, keine Konflikte).
- Tests nach dem Merge: `test_book_project` 2/2 OK,
  `test_import_markdown_original` 41/41 OK.
- `status.py`: `die-sprache-des-anderen` 34/34 done,
  `der-lotse-von-ruegen` 33/33 done, Gate dort ERROR=0/WARNING=0/INFO=20.
- **Kein Push** – `main` ist 13 Commits vor `origin/main`.

### 4. Offen (nächster Chat)

- **Push nach `origin/main`** (13 Commits) – noch nicht erfolgt.
- `cline/pveejb87` kann gelöscht werden (alles auf `main`).
- Titelei-Texte `export.yaml` von `die-sprache-des-anderen` sind weiterhin
  neutral (leere `rights`/`description`/`summary`/`author_bio`). Autor bleibt
  laut Nutzerentscheidung **Timo Verita**; `export.yaml` schreibt aber
  „Timo Veritas" (mit s) – Schreibweise angleichen.
- `tools/assemble_chapter.py:65` hardcodiert im Kapitelkopf
  `*Buch: {title} - Alexei Tolstoi*`. Das ist bei **allen** Büchern falsch
  (auch beim Lotse-Buch). Wird beim Export weggefiltert, steckt aber in
  `work/assembled/`. Korrektur auf den Buch-Autor aus `book.yaml` ist offen.
- Weitere Kapitelbilder für `die-sprache-des-anderen` (004–034) und
  `der-lotse-von-ruegen` (011–033) sind nicht erzeugt; Cover-Typografie
  (Titel/Autor im Bild) fehlt – beim Lotse-Buch ist sie vorhanden.
- Regal: `der-lotse-von-ruegen` hat `website.enabled: true` (sort_order 90),
  ist aber im Live-Katalog noch nicht sichtbar.
- Shell-Integration flackert in dieser Umgebung („Command completion could
  not be observed"). Workaround: Ausgabe per `Out-File` in eine Datei und
  diese lesen.

## Vorige Session (2026-10-28, Doppelablage geklärt + Einstieg gehärtet)

Branch **`cline/pveejb87`**, **nicht committet, kein Push**.
Vor-Session behauptete Buch-ID `sprache-des-anderen` (Stub, 12-Zeilen-`book.yaml`
ohne `id`/`title`, leere Szenen). Richtig ist **`die-sprache-des-anderen`**
(`slugify("Die Sprache des Anderen")`, 34 Kapitel, `rf_id` 232–265,
`state.yaml` + `status.json` 34/34 `done`).
Falscher Stub `books/sprache-des-anderen/` per Freigabe gelöscht
(`Remove-Item -Recurse -Force`); in `git status` nicht mehr enthalten.
Danach am vollständigen Paket verifiziert (lesend + Standard-CLIs,
kein OpenRouter, keine Bilder):

- `assemble_chapter.py --book die-sprache-des-anderen --all --style stil-01-original`:
  **34/34 Kapitel, 110.375 Wörter** (eine Zeile `stil-01-original` ohne Szenen
  erwartbar übersprungen → `34/35` in der Zählung).
- `review_manuscript.py --all --llm none --fail-on-errors`:
  **ERROR=0 / WARNING=0 / INFO=0, Exit 0**.
- `export_manuscript.py --scope book --style stil-01-original --format epub`:
  `exports/stil-01-original/book/epub/book-die-sprache-des-anderen-stil-01-original-20261028-183226.epub`
  (**3.917.106 Bytes**), Manifest `partial:false`, `review_gate_errors:0`,
  `review_gate_bypassed:false`, 34× `missing:[]`.
- `status.py summary`: **34/34 (100 %) done**.
- `tests.test_import_markdown_original`: **41/41 OK** (Stand vorige Verifikation).
- Mit dem Stub sind dessen 4 Placeholder-Bilder (`cover.jpg`,
  `chapter-001..003.jpg`) entfallen; `die-sprache-des-anderen/assets/` enthält
  nur leeres `covers/`. `export.yaml` dort ist neutral (Platzhalter-Cover, leere
  `rights`/`description`/`summary`/`author_bio`, kein `website:`/`marketing:`).

Danach gehärtet (gegen Wiederholung, Plan→Act in derselben Session):

- `AGENTS.md` Einstieg Regeln 2/3/4/5: unbekannte ID → stoppen + Rückfrage
  (keine Alternativ-ID, kein Zweitordner); keine `SUMMARY*.md` im Root, keine
  `tools/create_*.py` ohne Freigabe, keine Placeholder-Bilder als Pipeline;
  Doppelordner → stoppen + Rückfrage, kein Assembly/Export vorher; PowerShell
  nur `Select-Object -First N`, ein CLI pro Aufruf bei labiler Shell.
- `tools/lib/book_project.py`: `_suggest_book_id()` (difflib, max. 3, cutoff
  0.55, read-only); `find_book()` + `book_project()` melden jetzt z. B.
  `Buch mit id=sprache-des-anderen nicht gefunden, meintest du 'die-sprache-des-anderen'?`.
- `tools/import_markdown_original.py --new`: Hinweis nach stderr, wenn `--id`
  von `slugify(title)` abweicht (kein Abbruch, kein Verhalten-Change).
- `tests/test_book_project.py`: neue `SuggestBookIdTests` (Temp-Paket
  `die-sprache-des-anderen`, falsche ID muss `meintest du`-Vorschlag werfen).

Offen (nächster Chat, alles lesend zuerst): `unittest`-Läufe
(`test_book_project`, `test_import_markdown_original`) + `status.py summary`
in stabiler Shell nachholen (diese Session hing die Shell-Integration:
`Command completion could not be observed`); danach entscheiden, ob
Placeholder-Bilder neu oder Higgsfield (`text2image_soul_v2`-Vorgabe lag nur
im gelöschten Stub) sowie Verlags-/Titelei-Texte in `export.yaml`.
`SUMMARY.md`/`SUMMARY_FINAL.md` im Root und `tools/create_placeholders.py`
sind noch ungetrackt vorhanden und sollen gelöscht werden (Regelverstoß,
kein Commit ohne Freigabe).

## Vorige Session (2026-10-08, Ashkar I: AKTUALISIEREN + Stufe 1c)

Branch **`cline/pveejb87`** (nicht `main`).

## Letzte Session (2026-10-08, Ashkar I: AKTUALISIEREN + Stufe 1c)

Branch **`cline/pveejb87`**. Übergabe aus RomanForge im Modus AKTUALISIEREN
(`Ashkar I c3.md`, byte-identisch mit `Ashkar I(2).md`: 36 Kapitel,
112.304 Wörter). `--compare` gegen
`books/ashkara/work/imports/romanforge/state.yaml`: 18× `nichts` (001–018),
18× `neu` (Exportposition 019–036), 0 Konflikte, 0 `entfallen`. Der Modus
passte (Buch existiert), aber Stufe 1 konnte `neu` nur melden – deshalb
angehalten und gefragt; auf Freigabe erweitert.

- Werkzeug (Stufe 1c, `tools/import_markdown_original.py`): `neu`-Kapitel sind
  über ihre **Exportposition** freigebbar (`--accept 019`), `--keep` bleibt für
  sie verboten (Exit 2), Paketgrenze **5** Kapitel pro Lauf im Werkzeug
  erzwungen (Exit 2, kein Schreibzugriff). Dazu Pfadfix: `--book` liefert
  `work_dir`/`source_path` repo-relativ (`book_project.as_tool_config`),
  `_output_root_for` verdoppelte den Buchordner (`books/<id>/books/<id>/work`).
- Tests `tests/test_import_markdown_original.py`: **41/41 grün** (34 alt,
  5 für `neu`/Paketgrenze, 2 Regression Pfadauflösung).
- Paket 019–023 übernommen (Lauf `20261008-154946`; der erste Versuch
  `20261008-154530` schrieb wegen der Pfadverdopplung daneben und liegt unter
  `books/ashkara/work/legacy/import-pfadfehler-20261008/`): drei Textkopien je
  Kapitel, Assembly 5/5, Gate je Kapitel **ERROR=0/WARNING=0** (INFO 1/0/1/1/0).
- Paket 024–028 übernommen (Lauf `20261008-155643`): Assembly 5/5, Gate je
  Kapitel **ERROR=0/WARNING=0** (INFO 0/0/1/0/0).
- Pakete 029–033 (`20261008-155915`) und 034–036 (`20261008-155935`) übernommen:
  Assembly je 5/5 bzw. 3/3, Gate je Kapitel **ERROR=0/WARNING=0** (INFO 0/0
  außer 026/034/036 mit je 1). **Stand: 36/36 Kapitel in peter**, `state.yaml`
  36 Einträge, Buch-Gate `--all --llm none` **ERROR=0 / WARNING=0 / INFO=18**,
  Abschlussvergleich **36× `nichts`** (Exit 0).
- Kapitelbilder **019–025** erzeugt (2026-10-08): `generate_illustration.py --book
  ashkara --chapter NNN --kind chapter **--no-reference**` mit den Buch-Defaults
  (`gpt_image_2`, 3:4, `1k`, Render `high`). Ergebnis 772×1024 RGB, 69–103 KB,
  Verbrauch **31,5 Credits** (1148,94 → 1117,44). Prompts/Metadaten je Kapitel
  unter `books/ashkara/work/prompts/higgsfield/NNN-chapter-stil-01-original.*`.
  Zwei Betriebshinweise: ohne `--no-reference` bricht das Werkzeug ab, weil
  `DEFAULT_MOODBOARD` in `generate_illustration.py` ein reiner Share-Link ist;
  Higgsfield antwortete zweimal mit HTTP 503 (Service vorübergehend weg),
  einmaliges Wiederholen half.
- Offen: Bilder 026–036, `status/status.json` (weiterhin 18 Einträge; `status.py
  mark` ändert nur vorhandene Kapitel), neuer Buch-EPUB (bisheriger
  `...-20261008-002805.epub` deckt nur 001–018; die Bilder 019–025 sind dafür
  aber schon einsatzbereit), Stufe 2 (`--handoff <id>`; der Übergabe-Prompt
  implementiert in `tools/import_markdown_original.py` + `tools/lib/romanforge_client.py`, Endpunkt `/api/handoffs/{id}` verifiziert).

## Vorige Session (2026-10-07, RomanForge-Übernahme Stufe 1)

Branch **`cline/pveejb87`** (nicht `main`). Neues, allgemeines
Übernahme-Werkzeug für DE-Originale aus RomanForge ist fertig, getestet und
committet (`e93f4a2`). Vorgänger `import_die_dritte_chronik.py` bleibt liegen
(Entfernen nur nach Rückfrage).

- `tools/import_markdown_original.py` – vergleicht einen RomanForge-Markdown-
  Export per Tabelle (Nummer, Titel, Wörter RF/peter, Einstufung, Hinweis).
  `--compare`/`--dry-run` schreiben nichts (Exit 2 bei `konflikt`/`neu`/
  `entfallen`/`ohne-ausgangsstand`); `--accept`/`--keep` schreiben nur die
  freigegebenen Kapitel (max. 5 pro Paket). `--new` legt ein unbekanntes
  Buchpaket an (braucht `--id/--title/--author`).
- Erstlauf (Option B): der erste schreibende Lauf legt `state.yaml` für
  **alle** Kapitel an (unberührt: `rf_base = peter_base = Hash aus
  --baseline`). Danach ist `--baseline` nicht mehr nötig; wird sie trotzdem
  übergeben, kommt nur ein Hinweis. Fehlt ein Kapitel in `state.yaml`, ist es
  `ohne-ausgangsstand` (Exit 2), **nie** `konflikt` (keine leere Baseline).
- „vermutlich umbenannt": `neu`+`entfallen` an gleicher Exportposition →
  Hinweis in der Berichtsspalte, kein Auto-Merge.
- Tests `tests/test_import_markdown_original.py`: **31/31 grün** (echte
  Chronik-Daten; der Frisch-Export ist der echt archivierte Export). Doku
  `docs/uebernahme-romanforge.md`; Plan `docs/plan-uebernahme-romanforge.md`
  (Stufe 2–4 offen, Stufe 1 „umgesetzt und abgenommen").
- Chronik-Erstlauf im Buch: `--keep 008,031,033,036 --baseline <150f0c1>`;
  Folge-`--compare` ohne `--baseline` ergab **nichts 35 / peter-behalten 11 /
  konflikt 2 (012, 025)**. Ausgangsstand versioniert unter
  `books/die-dritte-chronik/work/imports/romanforge/` (state.yaml + runs/).
- Offen: Nutzer liest 012/025 selbst und entscheidet. Nächster Schritt laut
  Plan: `--new` für Ashkara (neues Buchpaket über den Übernahme-Weg).


## Vorige Session (2026-09-27 abends, lokal noch nicht committet: Buch `der-lotse` vollständig integriert)

**Auslöser:** Der Nutzer hat die Vollfassung unter
`books/der-lotse/source/Der Lotse von Rügen Full I.md` geliefert (623 KB,
27.09. 22:54) mit dem Auftrag, die neuen Kapitel zu integrieren. **Buch ist
jetzt vollständig: 32 Kapitel / 104.080 Wörter**, Umfangsziel 100.000–115.000
Wörter aus `book.yaml:notes` damit erreicht. Kapitel 032 „Der Vermerk von
Eldena" ist der **Epilog (Anno 1725)**, Kapitel 031 schließt mit dem
Verlustregister der Kirchgemeinde Middelhagen.

**Befund vor dem Import (read-only, `import_de_original.split_chapters` auf
beide Quellen):**

| | alt `Der Lotse von Rügen.md` | neu `… Full I.md` |
| --- | --- | --- |
| `##`-Kapitel | 10 | **32** |
| Wörter | 32.849 | **104.080** |
| Kapitel 001–009 | — | **byte-identisch** (Titel und Text) |
| **Kapitel 010 „Das alte Ufer"** | 3.107 W / 113 Abs. | **3.655 W / 111 Abs., Wort-Ähnlichkeit 0,039** |
| Kapitel 011–032 | — | neu, 2.438–4.058 W (Median 3.335) |

Kapitel 010 ist also **kein Nachtrag, sondern eine Neufassung**; die bis
dahin gültige DE-Szene 010 und das Kapitelbild 010 gehörten zum alten Text.
Kein Textbruch, keine Lücke – die Neufassung ist die gültige Quelle.

**Ablauf (kein LLM, keine OpenRouter-Kosten):**

1. `books/der-lotse/book.yaml`: `source_path` auf
   `source/Der Lotse von Rügen Full I.md` umgestellt. Die **alte Datei bleibt
   unangetastet** im Ordner (Quellen werden nie gelöscht) und ist der Backup
   des 10-Kapitel-Stands; `status.json:source` folgt beim Import automatisch.
2. `py -3 tools/import_de_original.py --book der-lotse --dry-run` →
   32 Kapitel / 104.080 W, keine Fehlermeldung.
3. `py -3 tools/import_de_original.py --book der-lotse` → schreibt
   `work/chapters/001–032-source.md`, `work/scenes/de/NNN/scene-01.md`,
   `work/scenes/de/stil-01-original/NNN/scene-01.md` und
   `status/status.json` (32 × `done`, `status.py summary` = 32/32).
   Weil es ein DE-Original ist, ist die DE-Szene eine 1:1-Kopie des
   Quelltexts – ein Überschreiben verliert also nichts.
   **Kein `assemble_chapter.py` nötig:** der Export liest DE-Szenen direkt,
   `work/assembled/` war schon beim 10-Kapitel-Export leer.
4. `book.yaml:notes` auf den Vollstand-Stand gebracht (32 Kapitel, Epilog in
   032, Vollfassung als Quelle, alte Datei als Backup benannt).

**Gate:** `py -3 tools/review_manuscript.py --book der-lotse --style
stil-01-original --all --llm none --fail-on-errors` →
**ERROR=0 / WARNING=1 / INFO=42** (10 Kapitel davor 0/0/14). Die einzige
Warnung ist `repetition_style` in **021**: eine 16-fache Anaphorenkette
(„…und er spürte, wie das Schiff sich bewegte, wie es sich drehte, wie es in
die Rinne glitt…") plus TTR 0,22. Das ist **Autortext und Stilmittel**, kein
Mangel – wie bei der Chronik nicht angefasst. Nur ERROR blockiert den Export.

**Bilder (Nutzerentscheidung: neue Bilder für 011–032, Kapitel 010 neu,
Cover bleibt):** 23 Generierungen mit `gpt_image_2`, `quality: 2k`,
`render_quality: medium`, 3:4, `--no-reference --allow-paid-generation
--overwrite`, Lauf im Hintergrund mit Log
`books/der-lotse/work/imagegen-010-032.log` (Muster wie das frühere
`work/imagegen-004-010.log`), ~47 s pro Bild. Dank `keep_master: true` schreibt
jeder Lauf **beide** Ebenen aus einem Download: `assets/master/` 1529×2048
(2k, ~300 dpi im Paperback) und `assets/chapter/` 764×1024 (E-Reader). Nachweis
an Kapitel 010: Master 874 KB, Reader 113 KB, beide 23:35:10.
`chapter-001_alt.jpg` und `assets/covers/cover.png` bleiben unangetastet; das
alte 1k-Bild für Kapitel 010 liegt als Sicherung in
`work/legacy/chapter-010-20260927-1k-alt.jpg`. **001–009 bleiben bewusst 1k**
(Nutzerentscheidung) – der Print-Report nennt für diese neun Kapitel weiter
die dpi-Warnung, das ist ein Hinweis, kein Fehler.

**Doku:** `AGENTS.md` und `README.md` auf „Roman vollständig, 32 Kapitel"
nachgezogen; `docs/offene-punkte.md` Punkt 13 bleibt für die anderen Bücher
offen.

**Exporte (alle ohne `--allow-review-errors`, Manifest mit 32 Illustrationen
und `cover.png`, `review_gate_errors: 0`, `review_gate_bypassed: false`):**

- EPUB `...-20260927-235509.epub` (8,96 MB, 36 XHTML-Teile, **40 Bilder**,
  Nav mit 32 Kapiteln)
- DOCX `...-20260927-235521.docx` (5,84 MB)
- A5-PDF `...-20260927-235527.pdf` (7,85 MB, **446 S.**, `blank_pages: []`)
- Paperback 5.5x8.5 classic full `...-20260927-235631` (41,07 MB,
  **332 S.**, KDP-Limit 776, `within_kdp_page_limit: true`)

Print-Report-Status `warning` mit **genau den zwei bereits bekannten, bewusst
akzeptierten Punkten** – keine neue Meldung:

1. **dpi 001–009:** 250–252 dpi (< 300), weil diese neun Kapitel bewusst
   1k-Bilder behalten. `illustration_tier` zählt `master: 23, reader: 9` –
   die Master-Ebene greift also nachweislich für 010–032.
2. **Frontmatter Seite 3 (Autorenbio) 20 %** – bleibt laut deiner früheren
   Entscheidung stehen, ist dauerhaft keine Reparatur.

**Doku:** `AGENTS.md` und `README.md` auf „Roman vollständig, 32 Kapitel"
nachgezogen; `docs/offene-punkte.md` Punkt 13 um einen `der-lotse`-Nachtrag
ergänzt; `book.yaml:notes` auf den Vollstand-Stand gebracht.

**Offen für `der-lotse`:** `assets/covers/cover-print.*` für die komplette
KDP-Titelei (`--format paperback-complete`), `website.enabled` bleibt bewusst
`false`, Kindle-Previewer und Leseprobe stehen aus. Kapitel 001–009 bleiben
1k – ein Neugriff wäre 9 Generierungen, falls du die 300 dpi durchziehen willst.

## Vorherige Session (2026-09-27, zwei Ebenen fuer Buchbilder: 2k-Druckoriginal plus E-Reader-Fassung, Git-Schalter fuer grosse Medien)

Nutzerentscheidungen: Modell **`gpt_image_2` mit `quality: 2k`**, **keine
Neuerzeugung im Bestand** (gilt nur fuer kuenftige Laeufe), und **keine
grossen Dateien ins Git** – mit einem Schalter *pro Buch*, der auch
Audio und Video abdeckt.

**Befund vor der Umsetzung.** Die Ursache der dpi-Warnungen war nicht
„1K", sondern eine einzige Bilddatei fuer zwei Zwecke:
`chapter_illustration()` lieferte per `find_named_image()` dieselbe Datei
an EPUB, DOCX, A5 **und** Paperback, waehrend `image_processing` auf
E-Reader getrimmt ist (1024 px / q60). Der Druck braucht bei
`(trim - 2*Rand) * 0.72` Anzeigebreite rund **970 px** (5.5x8.5) bzw.
**1170 px** (6x9), also bei 1k-Material nur 237 dpi.

**Korrektur:**

- `tools/lib/asset_images.py`: zweite Ebene `assets/master/`
  (`MASTER_DIRNAME`, `DEFAULT_MASTER_PROCESSING` 2048 px / q92,
  `load_master_processing()`, `master_assets_enabled()`,
  `is_master_path()`). `discover_export_assets(..., from_master=True)`
  liest dort, schreibt aber weiter nach `assets/chapter` bzw.
  `assets/scene` – die Master sind nie Ziel eines Laufs.
- `tools/generate_illustration.py`: `download_url()` in
  `fetch_image_bytes()` + `_write_image()` zerlegt, neue
  `store_illustration()` schreibt **beide** Ebenen aus einem Download
  (Reader = saubere Verkleinerung desselben Originals). CLI-Flag
  `--no-master`, Buchschalter `higgsfield.keep_master`.
- `tools/export_manuscript.py`: `resolve_illustration(..., prefer_master=)`;
  `chapter_illustration` / `scene_illustration` / `collect_illustrations`
  entsprechend erweitert. Nur der Paperback-Zweig sammelt mit
  `prefer_master=True`; EPUB/DOCX/A5 bleiben unveraendert. Rueckfall auf
  die E-Reader-Bilder, wenn `assets/master/` fehlt.
- `tools/lib/print_pdf.py`: dpi-Warnung nennt die Herkunft in Klammern,
  neuer Report-Feld `illustration_tier` (`total`/`master`/`reader`).
- `tools/optimize_asset_images.py`: `--source auto\|master` plus
  Sicherheitsnetz, das abbricht, falls ein Ziel im Master-Ordner liegt.

**Git-Schalter:** `config/gitignore-assets.yaml` (Muster),
`tools/lib/gitignore_assets.py` (Logik), `tools/sync_book_gitignore.py`
(CLI mit `--check`/`--dry-run`). Geschrieben wird nur der Abschnitt
zwischen zwei Markern in `books/<id>/.gitignore`, eigene Zeilen bleiben
stehen. Schalter pro Buch: `book.yaml` -> `gitignore.large_assets` plus
`extra_patterns` / `disabled_patterns`. Alle **13** Buchpakete haben den
Abschnitt; `git check-ignore` bestaetigt, dass `assets/master/`,
`assets/audio/` und `exports/marketing/clips/` greifen. `.git` war
bereits 2288 MB, die Assets im Worktree 251 MB.

**Dashboard-Schalter (Nachtrag derselben Session).** Der Git-Schalter ist
jetzt auch im UI bedienbar, damit niemand dafür die CLI braucht:

- `webapp/backend/main.py`: `GET`/`PUT /api/books/{id}/gitignore`,
  Request-Modell `GitignoreSettingsUpdateRequest`, generischer Helfer
  `_write_nested_scalar_preserving_yaml()` (baut auf dem bestehenden
  `_set_nested_scalar` auf, wie `_write_website_settings_preserving_yaml`).
  Nach dem Schreiben wird `books/<id>/.gitignore` **sofort** neu gerendert,
  damit der Schalter nicht erst per CLI wirkt.
- `tools/lib/gitignore_assets.py`: `load_settings()` (Zustand für API inkl.
  repo-relativem `gitignore_path`), `write_gitignore()` (CLI und API teilen
  sich damit denselben Pfad), `with_switch()`. Das CLI benutzt dieselben
  zwei Funktionen – keine doppelte Logik.
- Frontend: Panel **Grosse Medien aus Git halten** auf der Bilder-Seite
  unter der Illustration-Setting-Karte, im vorhandenen `toggle-row`-Stil.
  Zeigt die aktiven Muster, meldet einen veralteten Abschnitt und hat
  Speichern/Zuruecksetzen. `getBookGitignore` / `saveBookGitignore` in
  `api.ts`, Typ `GitignoreSettings` in `types.ts`.
- `tsc --noEmit` Exit 0, `vite build` Exit 0. ESLint hat im Frontend keine
  Config (vorbestehend, nicht angefasst).

**Dabei zwei echte Fehler gefunden und behoben:** (1) Der Fallback in
`load_config()` gab bei fehlender `config/gitignore-assets.yaml`
`begin_marker: None` zurück, woran `render_block()` mit
`TypeError: sequence item 0: expected str instance, NoneType` starb. Marker
sind jetzt Konstanten und werden immer gefüllt – Regressionstest
`test_config_fallback_keeps_markers`. (2) `gitignore_path` kam absolut
zurück; ist jetzt repo-relativ wie der Rest der API. Tests 296 → **318**,
OK (22 neu: 19 Bild-/Gitignore-Logik, 3 API-Routen inkl. 404).


**Buchkonfiguration:** sieben Buecher mit Bildbestand (aelita,
die-dritte-chronik, feuriger-engel, leben-arsenjews, peter-i-buch-01,
pharao, der-lotse) auf `gpt_image_2` / `2k` / `render_quality: medium`
plus `image_processing.master` umgestellt. `anna-karenina`, `mongolen`
und die vier Roh-Anlagen haben bewusst kein `higgsfield:`-Block.

**Wichtig:** Der Bildbestand wurde **nicht** angefasst. Messung, welche
Quelle (PNG → `_alt.jpg` → JPEG) je Bild noch hergibt:

| Buch | ≥ 1000 px | zu klein | breiteste Quelle |
| --- | ---: | ---: | ---: |
| pharao | 70 | 0 | 1200 |
| leben-arsenjews | 27 | 0 | 1600 |
| peter-i-buch-01 | 21 | 0 | 1122 |
| feuriger-engel | 16 | 1 | 1152 |
| aelita | 15 | 3 | 1600 |
| die-dritte-chronik | 5 | 47 | 1086 |
| pissemski-tausend-seelen | 0 | 45 | 880 |
| der-lotse | 0 | 10 | 772 |

`die-dritte-chronik` und `pissemski-tausend-seelen` haben **keine**
auflösbare Quelle mehr; deren Master koennen nur durch Neuerzeugung
entstehen (92 Bilder, kostet Credits). Bewusst offen gelassen. Die
uebrigen Bucher koennten kostenlos hochskaliert werden – Detailtreue
waechst dadurch aber nicht, und nur 6x9 braucht > 1000 px.

**Nachweis** (Temp-Buch mit 768 px Reader- und 1536 px Master-Datei):
`collect_illustrations(..., prefer_master=True)` liefert
`assets/master/chapter/chapter-001.jpg`, `illustration_tier` meldet
`master=1`, und die dpi-Warnung schweigt; der Reader-Pfad meldet
weiterhin 237 dpi. Tests 296 → **314**, OK (18 neue in
`MasterAssetTests` und `GitignoreAssetsTests`). Dabei fiel auf, dass
`AssetKind.name` die Kategorie und nicht den Stem traegt.

**Nebenbei behoben:** `tests/test_generate_illustration.py` mockte noch
`download_url`; die vier Tests wurden auf die neue Seam `store_illustration`
umgestellt. Zwischendurch hatte ein PowerShell-Replace die Datei
doppelkodiert (Mojibake + BOM) – mit `git checkout` zurueckgesetzt und
die Ersetzungen ueber den Editor wiederholt. **Merke:** unter Windows
niemals `Get-Content -Raw` + `Set-Content -Encoding utf8` auf Dateien mit
Umlauten/Kyrillisch anwenden, das zerstoert die Kodierung.

## Übergabepunkt 2026-09-27 (Ende dieser Arbeitsrunde)

Der Stand liegt fertig im Worktree, **es wurde bewusst kein Commit erzeugt** –
das bleibt dem Nutzer vorbehalten (`git --no-pager status --short` zeigt
die Änderungen).

Erledigt in dieser Runde:

1. **Leerseiten-Bug im A5-/Paperback-Satz** behoben (`min-height` stand auf
   voller Seiten-/Trim-Höhe statt auf dem Satzspiegel). `der-lotse` 155→153 /
   112→111, Pharao A–D 924/788/673/643 → **923/787/672/642**, alle ohne
   Leerseiten. `blank_pages` und `frontmatter_fill` werden jetzt bei jedem
   Export gemessen.
2. **Zwei Bild-Ebenen** (`assets/master/` 2k für Paperback, `assets/chapter|scene/`
   1024 für E-Reader), Standard `gpt_image_2` / `2k`, sieben Buchpakete
   umgestellt.
3. **Git-Schalter pro Buch** für Druckoriginale, Audio, Video und Clips –
   als CLI (`tools/sync_book_gitignore.py`) und im Dashboard (Panel **Grosse
   Medien aus Git halten** auf der Bilder-Seite, `GET`/`PUT
   /api/books/{id}/gitignore`).
4. Doku: `AGENTS.md`, `README.md`, `docs/handover.md` (dieser Eintrag),
   `docs/higgsfield-integration.md`, `docs/offene-punkte.md` (Punkt 13 neu),
   `docs/uebergabe-prompt.md`, `.gitignore`.

Tests **318 grün** (vor der Runde 296), `tsc --noEmit` 0, `vite build` 0,
`sync_book_gitignore.py --check` 0.

**Nicht erledigt und bewusst so:**

- Kein einziges Bild neu erzeugt (Nutzerentscheidung). Punkt 13 in
  `docs/offene-punkte.md` hält fest, welche 102 Bilder eine Neuerzeugung
  brauchen (die-dritte-chronik 47, pissemski 45, der-lotse 10) und welche
  Bücher kostenlos aus dem Bestand hochskaliert werden könnten.
- `anna-karenina` und `geheime-geschichte-mongolen` bleiben wie besprochen
  liegen (A5-Vorschau bzw. Gate blockiert wegen Kyrillisch).
- `der-lotse`: `assets/covers/cover-print.*` fehlt weiterhin, 1k-Material
  ergibt 236–238 DPI, `website.enabled` bleibt `false`.
- Pharao A (923) und B (787) liegen über dem Cream-Limit 776; die
  Print-Leseprobe steht aus.
- Nichts committet, nichts gepusht.

Direkt als Nächstes sinnvoll: entweder Punkt 13 freigeben (Bild-Master
nachziehen) oder den Print-Leseprobe-Abschnitt abarbeiten. Beides wartet auf
eine Entscheidung des Nutzers.

## Vorherige Session (2026-09-27, Buch `der-lotse`: Leerseiten-Bug im PDF-/Taschenbuch-Satz behoben)



Ursachenanalyse plus Korrektur eines Satzbugs, der **alle** Bücher betraf
hat. Dazu der Abschluss der Bilder-/Cover-Session vom selben Tag (unten
unter „Buch `der-lotse`" weitergeführt).

**Der Fehler:** `min-height` der Titelei stand auf der vollen Seiten- bzw.
Trim-Hoehe (A5: `210mm`, Paperback: `8.5in`), nicht auf dem Satzspiegel
(A5: 172mm, 5.5x8.5: 181.9mm). Chromium schiebt den Inhalt eines zu hohen
Blocks komplett auf die naechste Seite; der Rest bleibt als Leerseite im
PDF. Beim A5-Pfad kam hinzu, dass `.cover-image img` mit `max-height: 175mm`
selbst hoeher war als der Satzspiegel - Folge war nicht nur eine Leerseite,
sondern ein **schwarzer Ueberlaufstreifen des Coverbilds oben auf der
Titelei** (in `books/der-lotse/.../book/work/...163024.pdf.html` nachweisbar).

Isoliert mit einem 5-Faelle-Playwright-Testdokument: `break-before: page`
auf dem ersten Element ist unschuldig (2 Seiten), `min-height` = volle
Seitenhoehe erzeugt die Leerseite (3 Seiten), Satzspiegelhoehe laesst sie
weg (2 Seiten).

**Messung des Bestands** (`find_blank_pages()`, neuester Export je Buch):

| Buch | Format | Seiten | Leerseiten |
| --- | --- | ---: | --- |
| anna-karenina | A5 | 829 | 1, 4 |
| feuriger-engel | A5 | 456 | 1, 4 |
| geheime-geschichte-mongolen | A5 | 193 | 1, 4 |
| peter-i-buch-01 | A5 | 1098 | 1, 4 |
| pharao | A5 | 1134 | 1, 4 |
| pharao | Paperback 5.5x8.5 | 643 | 2 |
| der-lotse (vorher) | A5 / Paperback | 155 / 112 | 1+4 / 2 |

**Korrektur:**
- `tools/lib/print_spec.py`: `FILL_HEIGHT_SAFETY_MM = 1.0` und
  `PrintSpec.fill_height_mm()` (Satzspiegel minus Sicherheitszugabe gegen
  die Pixelrundung in Chromium).
- `tools/lib/print_css.py`: `.titlepage { min-height: … }` nutzt jetzt
  `spec.fill_height_mm()` statt `spec.trim_height_in` (5.5x8.5 → 180.9mm,
  6x9 → 193.6mm).
- `tools/export_manuscript.py`: A5-Masse als Konstanten
  (`PDF_PREVIEW_PAGE_MM`, `PDF_PREVIEW_MARGIN_MM`) plus
  `pdf_preview_type_mm()`; `min-height: 171mm`, Coverbild `max-height: 170mm`.
- `tools/lib/print_pdf.py`: `find_blank_pages()` + `blank_page_warning()`,
  Ergebnis als `blank_pages` im Print-Report **und** im Export-Manifest
  (Feld `blank_pages`), A5-Pfad gibt die Warnung auf der Konsole aus.
  Messung bewusst vor `stamp_running_matter()`.
- `tools/lib/print_pdf.py`: `frontmatter_fill_report()` +
  `sparse_frontmatter_warning()` messen den **Füllgrad der Frontmatter-Seiten**
  (unterste Tintenzeile gegen Satzspiegel) und schreiben `frontmatter_fill` in
  den Report; unter 40 % kommt als Warnung plus konkreten Schaltern
  (`summary_page` / `author_bio_page` / `imprint_page: false`).
  Umsetzung per Rastermessung über pypdfium2: pypdf liefert für
  Chromium-PDFs keine verlässlichen Textpositionen (geprüft, Werte sind
  antikorrekt), und die Zeilenzahl taugt nicht als Ersatz, weil der
  Impressumsatz Schriftgrade mischt. `pypdfium2` ist optional in
  `requirements.txt` – fehlt es, wird nur diese Messung übersprungen.
  Wichtig auf Windows: Dokument **und** Seiten schließen, sonst blockiert
  das Datei-Handle das Löschen der Temp-Dateien in den Tests.

**Ergebnis `der-lotse`:** A5 155 → **153** Seiten, Paperback 112 → **111**,
`blank_pages: []`. Titelei ist Seite 1, Cover im A5-Pfad Seite 1, Ueberlauf­
streifen weg, Folio stimmt wieder (Frontmatter 1–4, Text beginnt S5 mit
Kolumnentitel). Frontmatter-Füllgrade: Titelei 72 %, Zusammenfassung 48 %,
**Leben des Autors 20 % (als `sparse` gemeldet)**, Impressum 64 %. Tests: 296
statt 288 (8 neue Regressionstests in `tests/test_print_export.py` und
`tests/test_export_manuscript.py`), OK.

**Entscheidung des Nutzers zur `sparse`-Meldung:** Die Bio-Seite
(`author_bio_page`) bleibt. Bei 111 Seiten spart ihr Weglassen eine Seite, der
Bestand ist bewusst so (Autorenbio separat ist im Buchhandel üblich, Amazon
führt sie ohnehin). Die Warnung im Report bleibt also dauerhaft stehen und
ist **kein Fehler**, nicht "reparieren". Pharao ist nicht betroffen (5
Frontmatter-Seiten, 73/49/47/73/99 % Füllung).

**Pharao Print-Vergleich neu gefahren** (4 Varianten, siehe
`books/pharao/exports/stil-02-poetisch/book/print/`), weil die alte Tabelle
`print-comparison-20260921-pharao-abcd.md` je eine Seite zu hoch war. Neue
Zahlen: **923 / 787 / 672 / 642** (vorher 924 / 788 / 673 / 643), überall
`blank_pages: []`. Frontmatter dort 5 Seiten, Füllgrade 73 / 49 / 47 / 73 /
99 % – nichts Einsparbares. A und B liegen weiter über dem Cream-Limit 776.

**A5-Vorschaupfade nachgezogen:** peter-i-buch-01, feuriger-engel und pharao
neu gerendert – dort sind die 2 Leerseiten je Buch ebenfalls weg (454 / 1167
/ 1132 Seiten). Bei peter-i-buch-01 ist die Seitenzahl gegenüber dem alten
PDF vom 17.06.2026 (1098) **gestiegen**, das liegt am Textstand der
Neuebersetzungen vom 17.09.2026 (6 Szenen), nicht an dieser Korrektur.
Offen bleiben: `anna-karenina` (PARKIERT, A5 weiterhin mit Leerseiten 1+4)
und `geheime-geschichte-mongolen` (Export bricht im Gate ab, exit 2, weil die
Monolith-Kapitel noch Kyrillisch enthalten – das Gate hat hier korrekt
blockiert, nicht neu zu rendern). Neu laufen lassen:
`py -3 tools/export_manuscript.py --book <id> --scope book --style <style> --format pdf`.

## Buch `der-lotse` (2026-09-27, echtes Cover + alle 10 Kapitelbilder, Export neu)

Nachtrag zum selben Tag, siehe Abschnitt darunter. **Der Lotse von Rügen** ist
ein **eigenständiges deutschsprachiges Original von Timo Verita** wie Die
dritte Chronik – gleiche Autoren-/Herausgeberlogik, gleiche
Motivatier-Classes-Rollen. Stand des Pakets: **10 von 32 Kapiteln (ca. 31 %,
32.849 Wörter)**, Ziel des Gesamtwerks 100.000–115.000 Wörter.

- Romanvorlage (Entwicklungsfassung 1.0, 26.09.2026) in `book.yaml:notes` und
  `export.yaml` eingearbeitet: Genre „historischer Abenteuer- und
  Familienroman", September 1715 über ca. drei Wochen plus Nachklang 1725,
  Schauplätze Thiessow/Middelhagen auf Mönchgut, Greifswalder Bodden,
  Fahrwasser an der schwedischen Schiffssperre, Eldena; Perspektive
  ausschließlich Joren und Maren Voss, personale dritte Person.
  `description`/`summary` nach dem Leserversprechen formuliert, Fiktionshinweis
  im Impressum.
- **Bilder-Modell auf GPT Image 2 umgestellt** (Nutzerwunsch):
  `higgsfield: model: gpt_image_2, quality: 1k, render_quality: medium`.
  Hinweis: die globale Voreinstellung in `config/higgsfield_models.yaml` und
  in den anderen Buchpaketen ist weiterhin `text2image_soul_v2` – die
  Umstellung gilt nur für `der-lotse`.
- `illustration_setting` um „no frame, no canvas edge, no signature,
  full-bleed" ergänzt. Grund: Soul 2.0 lieferte gerahmte Gemälde mit
  Signatur-Kante, die im Buchsatz unbrauchbar waren. Die Soul-Variante von
  Kapitel 001 liegt als `assets/chapter/chapter-001_alt.jpg` (wird vom Export
  ignoriert).
- Erzeugt mit `tools/generate_illustration_batch.py --kind chapter
  --no-reference --allow-paid-generation --missing` (kein Moodboard vorhanden,
  deshalb `--no-reference`; ohne das Flag bricht der Lauf mit dem
  Share-Link-Fehler ab). 3 Bilder, 1K, je 70–115 KB:
  `assets/chapter/chapter-001.jpg` … `chapter-003.jpg`. Bild 001 zeigt Joren
  im Wasser mit der roten Mütze des schwedischen Leutnants, Pfahlsperre und
  Eldena, 002 die Requisition mit Maren und den Abschriften, 003 die Fahrt
  an der Sperre.
- Gate unverändert **ERROR=0/WARNING=0/INFO=14**. Neu exportiert (alle ohne
  Bypass, 3 Illustrationen im Manifest):
  EPUB `...-20260927-161440.epub`, DOCX `...-20260927-161501.docx`,
  A5-PDF `...-20260927-161506.pdf` (148 S.),
  Paperback 5.5×8.5 classic `...-161514` (**105 S.**, KDP-Limit 776).
- **Echtes Cover vom Nutzer geliefert**: `assets/covers/cover.png`
  (1024×1536, Renditionsmotiv mit Titel „Der Lotse von Rügen", Autor
  „Timo Verita", Serie „MOTIVATIER CLASSICS"). `export.yaml:book.cover` steht
  jetzt explizit auf `mode: image` + `image_path: assets/covers/cover.png`
  (vorher `placeholder` mit leerem Pfad; die Auto-Erkennung hätte es auch
  gefunden, explizit ist aber sauberer und im Dashboard sichtbar).
- **Kapitelbilder 004–010 nachgezogen**, damit 10/10 vorhanden sind. Erzeugt
  mit `py -3 tools/generate_illustration.py --book der-lotse --chapter NNN
  --kind chapter --no-reference --allow-paid-generation`, gleiche Defaults wie
  001–003 (`gpt_image_2`, 1K, `render_quality: medium`, 3:4, ~40–50 s pro
  Bild). Motivkette jetzt durchgehend: Pfahlwerk im Greifswalder Bodden vor
  Eldena, Requisition/Offiziere, Fischerei am Bodden, Seekarte mit
  schwedischer Flagge, Maren im Watt zwischen den Pfählen. `chapter-001_alt.jpg`
  bleibt die ignorierte Soul-V2-Variante.
- Gate erneut **ERROR=0/WARNING=0/INFO=14**, danach alle vier Formate neu
  exportiert (ohne `--allow-review-errors`, Manifest mit 10 Illustrationen und
  `cover.png`):
  - EPUB `...-20260927-163021.epub` (6,8 MB, 18 Bilder: 10 Kapitelbilder,
    Cover + 7 Cover der Reihenkatalog-Titel)
  - DOCX `...-20260927-163021.docx` (3,7 MB), A5-PDF `...-20260927-163024.pdf`
    (4,96 MB, **155 S.**)
  - Paperback 5.5×8.5 classic full `...-20260927-163028` (11,25 MB,
    **112 S.**, KDP-Limit 776, `within_kdp_page_limit: true`)
- Print-Report-Status `warning`, **nur** wegen DPI: die 1K-Bilder ergeben bei
  3,24 in Anzeigebreite 236–238 dpi (< 300). Für echten Print-Qualitätsanspruch
  müsste `higgsfield.quality` für `der-lotse` auf `2k` hochgehen und die Bilder
  neu erzeugt werden; EPUB/DOCX/PDF sind davon nicht betroffen.
- Offen: `assets/covers/cover-print.*` für die komplette KDP-Titelei
  (`--format paperback-complete`) fehlt weiterhin, `website.enabled` bewusst
  `false`, und `gpt_image_2 / 1K / medium` gilt weiterhin nur für dieses eine
  Buchpaket.

## Vorherige Session am selben Tag (2026-09-27, Buch angelegt + exportiert)

**Der Lotse von Rügen** (Timo Verita) ist als 13. Buchpaket unter
`books/der-lotse/` entstanden und vollständig exportiert. Kein
Übersetzungsprojekt, kein LLM-Lauf, keine OpenRouter-Kosten.

- DE-Original wie die Dritte Chronik: `source_lang/target_lang: de`,
  `structure.mode: chapter_as_scene`, `display.chapters.format: literary`.
- Metadaten nach Nutzerentscheidung: Autor **Timo Verita**, Herausgabe
  **Motivatier Classics**, Verlag **Motivatier Stiftung**, Untertitel
  „Roman". Titelblock, Impressum, Zusammenfassung, Autorenbio und
  Klartext-Beschreibung selbst formuliert – **fachlich prüfen**, ebenso die
  Zeile „Greifswalder Bodden, Insel Rügen · um 1715" (das steht so nicht
  als Quelle im Dokument, die Quellen nennen 1700–1715).
- Neues generisches Tool **`tools/import_de_original.py`** (Kapitelgrenze =
  `## `-Überschrift, DE-Szene = Kapiteltext, Status `done`). Das Skript
  `tools/import_die_dritte_chronik.py` ist davon unabhaengig und bleibt
  bestehen. Aufruf: `py -3 tools/import_de_original.py --book <id> [--dry-run]`.
- Quelle: `books/der-lotse/source/Der Lotse von Rügen.md` (10 Kapitel,
  32.849 Wörter) + `.docx`-Backup. **Quelle unangetastet.**
- Gate: `py -3 tools/review_manuscript.py --book der-lotse --style
  stil-01-original --all --llm none --fail-on-errors` → **ERROR=0,
  WARNING=0, INFO=14** (nur `repetition_style`: Anaphorenketten „weil/dass/
  oder" + TTR-Hinweise – bewusstes Stilmittel, nicht angefasst).
- Exporte (alle ohne `--allow-review-errors`):
  - EPUB `book-der-lotse-von-r-gen-stil-01-original-20260927-155754.epub`
    (3,3 MB, 12 XHTML-Teile, Nav mit 10 Kapiteln + Reihenkatalog)
  - DOCX `...-20260927-155817.docx`, PDF (A5) `...-20260927-155831.pdf`
  - Paperback 5.5×8.5 classic full: **102 Seiten** (KDP-Limit 776)
- Offen: Cover ist nur ein **Platzhalter** (`cover.mode: placeholder`), keine
  Kapitelbilder. Für KDP fehlen `assets/covers/cover-print.*` und eine
  `website:`-Freigabe ist bewusst `enabled: false`.
- Tests: `py -3 -m unittest discover -s tests` → 288 Tests, OK.
- Datei-Slugs enthalten `r-gen` statt `ruegen` (globale
  `sanitize_filename()` in `export_manuscript.py` – betrifft alle Bücher mit
  Umlauten im Titel, z. B. auch „Der feurige Engel" → `der-feurige-engel`).
  Nur Dateiname, kein Inhaltsproblem.


## Vorige Session (2026-09-21, Print-Optionen Trim/Profil/Bilder)

Paperback-Export waehlt Trim, Satzprofil und Bildmodus pro Job. Default
bleibt 5.5×8.5 / classic / full_page (kein stiller Satzwechsel). Cream-Limit
ist 776 (White 828, Groundwood 812). Dashboard: Dropdowns nur bei
Taschenbuch-Formaten. CLI:

`py -3 tools/export_manuscript.py --book pharao --scope book --style stil-02-poetisch --format paperback --trim-size 6x9 --layout-profile classic --illustration-mode full_page`

Dateiname enthaelt Slug `55x85-classic-full` bzw. `6x9-long_classic-inline`.
Print-Report: `within_kdp_page_limit`, `kdp_max_pages`. Keine automatische
Typo-Optimierung. Stale-Jobs koennen ueber Manifest+Report auf completed
gehoben werden.

Aelterer Komplett-Pilot ohne Varianten-Slug: Stempel `20260921-155209`
(924 Seiten, Limit damals 828). Neue Varianten 2026-09-21:

- A 5.5x8.5 classic full: **923** Seiten (nicht KDP-creme)
- B 6x9 classic full: **787** Seiten (–136 / –14,7 % gegen A; noch +11 ueber 776)
- C 6x9 long_classic full: **672** Seiten
- D 6x9 long_classic inline: **642** Seiten

Vergleich: `books/pharao/exports/stil-02-poetisch/book/print/print-comparison-20260927-pharao-abcd.md`.
Code, Tests, Doku, Pharao-000 und `cover-print.png` sind auf `main`.
Die grossen Interior-/Complete-/Wrap-PDFs bleiben lokal (regenerierbar).

| Datei | Rolle |
|---|---|
| `*-paperback-interior.pdf` | KDP-Innenleben (kein Cover, 924 Seiten) |
| `*-paperback-complete.pdf` | Lese-PDF: Vorderseite + Buch + Rueckseite (~926) |
| `*-paperback-wrap.pdf` | **Umschlag als eine Flaeche:** Rueckseite \| Ruecken \| Vorderseite (KDP-Cover-Upload) |
| `*-print-report.json` | Seitenzahl, Bundsteg, Warnungen |

Wrap ist nicht der Buchtext. Rueckenbreite cremefarben/SW = Seitenzahl ×
0,0635 mm (hier 924 → ~58,7 mm). Vorderseite nur aus manuellem
`assets/covers/cover-print.png` (kein Fallback auf Kindle-`cover.jpg`).
KDP-Creme-Maximum 776 Seiten — Report warnt, Satz bleibt unveraendert.

Kapitel **000** (Einleitung): Arbeitsdatei war ein erfundener Essay; Juni-Wstęp
mit Herodot-Zitat wiederhergestellt. Gate-Abbruch kam, weil das Release-Gate
erst 16./17.09. scharf wurde. Buch-Gate ERROR=0.

Reihenkatalog am Buchende in EPUB und Print (`tools/lib/series_catalog.py`).
`website.catalog: false` bei Anna, Grin, Pissemski.

Dashboard: http://127.0.0.1:8000 — Dropdowns Trim/Profil/Bilder nur bei
Taschenbuch-Formaten. Stale-Jobs: `tasklist`-Encoding plus Manifest+Report
(`tools/lib/dashboard_jobs.py`). Frontend zuletzt mit `--build` neu gestartet.

## Git / Branch

| Item | Wert |
|------|------|
| Aktiver Branch | `cline/pveejb87` (tracking `origin/cline/pveejb87`); `main` bleibt unberührt |
| Tip | `e93f4a2` RomanForge-Übernahme Stufe 1 (`import_markdown_original.py` + 31 Tests + Doku + Chronik-Ausgangsstand) |
| Vorher auf diesem Branch | `main`/Print-Workflow 2026-09-21 (Trim/Profil/Bilder, Pharao A–D, Reihenkatalog, Pharao-000). Davor `1beb55d` Chronik KDP-fertig + Tausend Seelen `stil-02-poetisch` Gate 0/0/5 + Aelita/Arsenjew Amazon |
| Davor auf main | `15566c0` Chronik Gate-Fixes; `bc5a1c6` / `c293fdc` Peter-I Raffung; `081b1ca` Marketingexport |
| Feature-Branch | `codex/geheime-geschichte-mongolen-prompts` – Inhalt ist in `main` enthalten; Branch kann später gelöscht werden |
| Arbeitsbaum | Print-Code ist versioniert. Lokal bleiben regenerierbare Print-PDFs unter `books/pharao/exports/.../print/` sowie `exports/.../work/`-HTML. `staging/` und `var/` gitignored. |

**Warnung (schon passiert):** Checkout auf ein altes `main` ohne die Codex-Commits ließ Buchordner als leere Hüllen zurück. Nicht blind zwischen Branches wechseln, ohne vorher zu prüfen, ob `books/*/book.yaml` noch da sind.

Committet (09/2026): 4 Top-5-Buchpakete (s. unten, alle Roh-Anlage 0 %), Tool-Fix Глава-I/X, `website:`-Block der neuen Pakete von `book:` auf top-level korrigiert, Regressionstests, Doku-Sync auf 12 Pakete. Lokal geblieben: `staging/conv5.py + staging/top5-quellen/` (Arbeitsmüll, jetzt via `.gitignore` ausgenommen) und `books/leben-arsenjews/work/cover.png` (Platzhalter).

**Bekannte Fehler (nicht von Stufe 1, Stand 2026-10-07):** volle Suite `py -3 -m unittest discover -s tests` → 319 Tests, 7 Fehler außerhalb des Import-Tools: 5 in `tests/test_print_export.py` (Print/PDF-Pipeline) und 2 in `tests/test_backend_api.py` (Webapp-API). Die 5 Print-Fehler sind nicht als bekannt dokumentiert; vor einem Merge nach `main` prüfen, ob sie von den offenen CSS-Änderungen (`book-print.css`/`epub.css`) kommen. Die Stufe-1-Suite (`tests/test_import_markdown_original.py`) ist isoliert 31/31 grün.

## Was das Repo ist

Buchzentrierte Übersetzungs-/Export-Werkbank (`books/<id>/`). Dashboard = FastAPI + React unter `webapp/`. Öffentliche Regal-Website = Vite + Three.js unter `webpage/` (nicht mit `webapp/` verwechseln).

## Buchpakete (12 mit `book.yaml`)

| ID | Titel | Default-Style | Website `sort_order` | Cover unter `assets/covers/` | Stand 09/2026 |
|----|-------|---------------|----------------------|------------------------------|---|
| `peter-i-buch-01` | Peter der Erste | stil-02-poetisch | 10 | `cover.jpg` | **LIVE** |
| `aelita` | Aëlita | stil-03-branderson | 10 | `cover.png` + `cover.jpg`-Sidecar + `coverII.jpg` | **LIVE 09/2026** (Amazon-Link + Marketing nach Amazon-Freigabe) |
| `leben-arsenjews` | Das Leben Arsenjews | stil-02-poetisch | 20 | `cover.jpg` / `.png` | **Release-Kandidat 09/2026** (Gate ERROR=0/WARNING=8, EPUB 20260917-212334 ohne Bypass; Kindle-Preview + Stichprobe offen) |
| `anna-karenina` | Anna Karenina | stil-02-poetisch | 20 | `annakarenina.png` (per `image_path`) + Regal-Kopie | **PARKIERT** (Nutzerentscheidung 09/2026) |
| `pharao` | Der Pharao | stil-02-poetisch | 30 | `cover.jpg` + `cover-print.png` | **LIVE**; Print-Optionen 2026-09-21 (A 924 / B 788 / C 673 / D 643; Cream 776) |
| `feuriger-engel` | Der feurige Engel | stil-02-poetisch | 50 | `cover.jpg` / `.png` | **LIVE** |
| `die-dritte-chronik` | Die dritte Chronik | stil-01-original | 60 | `cover.jpg` / `.png` | **KDP-fertig 2026-09-21** (Gate 0/13/36, 29/48 clean, 48/48 bebildert, EPUB 20260921-131112 mit 50 Bildern ohne Bypass; offen: Kindle-Preview, KDP-Upload). Seit 2026-10-07 Redaktionsweg über RomanForge (Stufe 1, `e93f4a2`); Ausgangsstand `work/imports/romanforge/` versioniert |
| `geheime-geschichte-mongolen` | Die Geheime Geschichte der Mongolen | stil-01-original | 70 | `cover.png` (neu 09/2026) + `coverII.png` |
| `kuprin-duell` | Das Duell | stil-01-original | 40 (nicht freigegeben) | `cover.png` |
| `kuprin-moloch` | Der Moloch | stil-01-original | 40 (nicht freigegeben) | `cover.png` (neu 09/2026) |
| `grin-wellenlaeuferin` | Die Wellenläuferin | stil-01-original | 40 (nicht freigegeben) | `cover.png` (neu 09/2026) |
| `pissemski-tausend-seelen` | Tausend Seelen | stil-01-original | 40 (nicht freigegeben) | `cover.png` (neu 09/2026) |

Die neuen Cover sind von Hand erstellte Hochformat-PNGs (688×1024, Regal nutzt
`object-fit: cover`); Vorgaenger wurden als `coverII.*` behalten. **Entscheidung
2026-09-13:** EPUB-first – 688×1024 reicht (auch fuer die Amazon-Auslieferung),
ein hoeher aufgeloestes Print-Cover wird erst fuer KDP-Paperback gebraucht. Die
Regal-Kopien unter `webpage/public/covers/` sind fuer `aelita` und
`geheime-geschichte-mongolen` noch die alten Bilder – nach der finalen
Cover-Wahl `python tools/build_shelf_website.py` laufen lassen.

Freigabe fürs Regal: in `export.yaml`

```yaml
website:
  enabled: true
  amazon_url: ''      # Button nur wenn gesetzt
  sort_order: 10
  catalog: false      # optional; false = nicht im Reihenkatalog am Buchende
```

Katalog neu bauen: `python tools/build_shelf_website.py` → `webpage/public/data/catalog.json` + `webpage/public/covers/`.

## Dashboard

- Start: `python tools/start_dashboard.py` oder `Dev-Start.cmd` / `dev.cmd`
- **Uebersetzungslaeufe laufen ueber das Dashboard** (Buch, Style, Kapitel/Scope,
  Provider); es benutzt dieselben `book.yaml`-Defaults (Modell,
  `ai.reasoning_effort`) und schreibt dieselben Szenen/Status wie die CLI.
- **Erster Start in dieser Umgebung (13.09.2026 geprueft):** `fastapi`/`uvicorn`
  fehlen im globalen Python 3.13 (`import fastapi` schlaegt fehl) und
  `webapp/frontend/node_modules` fehlt. Vorher einmalig
  `pip install -r requirements.txt` und `npm install` in `webapp/frontend/`
  (Node v22.22.2 / npm 10.9.7 sind vorhanden).
- **Fallstrick `python` im PATH (13.09.2026):** In dieser Umgebung zeigt `python`
  auf ein fremdes, per Anwendungssteuerungsrichtlinie blockiertes venv
  (`C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv`). Jeder
  `python …`-Aufruf scheitert dann mit „Eine Anwendungssteuerungsrichtlinie hat
  diese Datei blockiert" – auch `dev.cmd`. **Loesung: `py -3` verwenden**
  (Python 3.13.12 unter `AppData\Local\Programs\Python\Python313`) und dort
  `py -3 -m pip install -r requirements.txt` ausfuehren.
- **Bekannter Testfehler `test_backend_api` (2 Tests, belegt 2026-09-13):**
  `test_action_plan_translate_batch` und `test_job_start_allows_translate_batch`
  senden `ollama_model: gemma4:latest`, waehrend das lokal laufende Ollama nur
  `gemma4:e4b` anbietet. `_validate_ollama_model` antwortet deshalb korrekt mit
  400. Kein Regressionssignal des Repos – entweder Modell-Tag lokal anpassen
  (`ollama pull gemma4:latest`) oder den Test auf ein vorhandenes Modell
  umstellen.
- URL: http://127.0.0.1:8000
- Unter Windows nutzt `start_dashboard.py` `npm.cmd` für Frontend-Builds
- Nav **Website** (`/website`): Freigabe-Übersicht, Jobs „Katalog neu bauen“ / „Website-Build (dist)“
- Buch-Settings: Website-Felder (enabled, Amazon-URL, Sortierung) → schreiben in `export.yaml`
- API: `GET/PUT /api/books/{id}/website`, `GET /api/website/books`, Jobs `build_shelf_website` / `build_webpage_dist`
- Nach Frontend-Änderungen Frontend neu bauen und Dashboard neu starten

## Regal-Website (`webpage/`)

- Details: [webpage/README.md](../webpage/README.md)
- Preview (nicht `file://`): `python tools/preview_webpage.py` oder `Dev-Start-Webpage.cmd` → http://127.0.0.1:4173
- Production: `python tools/build_webpage_dist.py` → Inhalt von `webpage/dist/` deployen
- Live: https://stiftung.motivatier.de/classics/ auf der IONOS-VPS 87.106.3.155
  (Apache mit Plesk, dieselbe Maschine wie RomanForge). Docroot
  `/var/www/vhosts/motivatier.de/stiftung.motivatier.de`, Unterordner `classics/`,
  Eigentümer `motiadmin:psaserv`.
- Deploy 2026-10-21: `build_shelf_website.py` + `build_webpage_dist.py`, Upload per
  `scp` nach `/tmp/` und `rsync -a --delete` in den Docroot → **10 Bände live**
  (vorher 8). SSH als `root` mit `~/.ssh/codex_boddenblick_deploy`
  (`-o IdentitiesOnly=yes`), kein Standard-Key. Sicherung davor:
  `/root/classics-backup-20261021-144558.tar.gz`. Details:
  [offene-punkte.md](offene-punkte.md) Punkt 7.
- Branding: Motivatier Klassiks; Seiten Über uns / Impressum unter `webpage/public/`
- Mint-GLB-Hardcover: noch nicht eingebunden (Fallback-Boxen + Cover-Texturen)

## Marketingexport (neu 2026-09-13, X-Clip 2026-09-14)

Erzeugt aus vorhandenen Buchdaten X-Beitraege, YouTube-Materialien und ein
Kampagnenmanifest. Es wird **nichts veroeffentlicht** und **keine
Plattform-API** angesprochen. Details:
[marketing-export.md](marketing-export.md).

| Baustein | Pfad |
|---|---|
| CLI | `tools/export_marketing.py` (`--book`, `--style`, `--all`, `--dry-run`, `--provider`, `--regenerate`, `--no-texts`) |
| Kernlogik | `tools/lib/marketing_campaign.py` (IDs, Termine, Zeichengewichtung, Medien, Status, Manifest, Rendering) |
| Prompts | `tools/lib/marketing_prompts.py` (Datenbrief, JSON-Auswertung, Provenienz) |
| Globale Config | `config/marketing.yaml` (Marke, Shelf-URL, Zeitplan, **alle Plattformlimits**) |
| Buchlokal | top-level `marketing:` in `export.yaml` |
| Ausgabe | `books/<id>/exports/marketing/{campaign.json,posts.md,youtube.md,media.json,README.md}` |
| Texte | `work/marketing/generated.json`, Overrides `work/marketing/overrides/<post-id>.md` |
| Dashboard | Export-Seite → Karte **Marketingpaket** (+ Sektion **X-Clip**); `GET /api/books/{id}/marketing`, Actions `marketing_export` / `render_x_clip` |
| Tests | `tests/test_marketing_campaign.py`, `tests/test_marketing_prompts.py`, `tests/test_marketing_api.py`, `tests/test_render_x_clip.py` |
| X-Clip | `tools/render_x_clip.py` + `tools/lib/x_clip.py` (Cover + Song → quadratisches MP4, H.264/AAC, `faststart`); Ausgabe `exports/marketing/clips/<song>-x-<dauer>s.mp4` + `-check.jpg`; braucht System-ffmpeg, veraendert keine Quellen |

Wichtige Eigenschaften:

- **Keine Kosten ohne Auftrag:** ohne `--provider` werden nur vorhandene Texte
  verwendet. Neu erzeugt wird nur bei geaendertem Quellhash (Metadaten +
  Leseprobe), geaenderter `prompt_version` oder `--regenerate`;
  `generated_at` allein loest keine Neuversion aus.
- **EPUB bleibt unberuehrt:** der Manuskript-Export liest den
  `marketing:`-Block nicht (Regressionstest vorhanden).
- **Offene Angaben statt Luecken:** fehlender Amazon-Link →
  `needs_amazon_url` (Platzhalter bleibt im Manifest strukturiert sichtbar),
  fehlender YouTube-Link → `needs_youtube_url`, privates Video → `blocked`,
  Songdatei fehlt → `blocked`, kein Songdatensatz → `omitted`. Musik- und
  Videopositionen werden **nicht** mit Ersatztext gefuellt.
- **Editoriale Vorabsaetze sind keine Zitate:** die Leseprobe ueberspringt
  Blockzitate am Szenenanfang (Peter-I-Vorspaenne), damit kein redaktioneller
  Text als Autorenstelle erscheint.
- **Bilder:** thematische Zuordnung ueber Inhaltswoerter, nie automatisch nur
  das erste Bild; `_alt`-Dateien und `chapter-007-a.jpg` zaehlen nicht als
  eigenes Kapitelbild.
- **Zeichenpruefung:** konservative Naeherung (URL = 23, breite Zeichen = 2),
  Zielband 220–250, Limit 280 – ausdruecklich keine Plattformvalidierung.

**Pilot (`peter-i-buch-01`, 2026-09-13):** Texte als Repository-KI aus dem
Datenbrief erzeugt (keine API-Kosten). Ergebnis: `x-t0-intro` 232,
`x-t5-content` 239, `x-t8-sample` 228, `x-t12-second-angle` 206 gewichtete
Zeichen (alle `needs_amazon_url`), `yt-short-2` 443 Zeichen (`generated`),
Musikpositionen `omitted` (kein Songdatensatz). Offen im Pilot: Amazon-URL,
YouTube-Adresse, Songdaten, Kampagnenstart.

**Peter I Nachpflege (2026-09-14, keine Kosten, kein Publish):**
`website.amazon_url = https://amzn.to/4vLjAlF` (Kurzlink: Syntax ok,
`is_amazon_host: false`, `user_provided`); Song `song-01`
(`Peter der Erste – Lied zum Roman`, `assets/audio/peter-i-song-01.mp3`,
`ai_generated: true`) nach fester Namensregel; X-Clip
`exports/marketing/clips/song-01-x-45s.mp4` (45,0 s, 1080x1080, H.264/AAC,
ffmpeg-verifiziert) + Kontrollbild. Offen: 4 Songtexte (`text_missing`),
YouTube-URL, Kampagnenstart; X-Texte teils ueber Zielband (Override-Kuerzung).

**Umgebung:** `tzdata` wurde in `requirements.txt` aufgenommen (Windows liefert
ohne Daten keine `Europe/Berlin`-Zeitzone); `berlin_tzinfo()` faellt sonst
deterministisch auf die EU-Sommerzeitregel zurueck.

## Wichtige Buchstände

Verifizierter Fortschritt (dateibasiert im Default-Style, `staging/audit_progress.py`, 2026-09-13):

| Buch | Default-Style | Kapitel | komplett (Default) | offen |
|------|---------------|---------|--------------------|-------|
| `aelita` | `stil-03-branderson` | 30 | 30 | 0 (29 done, 1 review) |
| `anna-karenina` | `stil-02-poetisch` | 239 | 166 | 73 |
| `die-dritte-chronik` | `stil-01-original` | 48 | 48 | 0 |
| `feuriger-engel` | `stil-02-poetisch` | 16 | 16 | 0 |
| `geheime-geschichte-mongolen` | `stil-01-original` | 15 | 1 (13 Monolithe nur teilweise) | 1 |
| `grin-wellenlaeuferin` | `stil-01-original` | 33 | 0 | 33 |
| `kuprin-duell` | `stil-01-original` | 23 | 0 | 23 |
| `kuprin-moloch` | `stil-01-original` | 11 | 0 | 11 |
| `leben-arsenjews` | `stil-02-poetisch` | 104 | 104 | 0 (50 done, 54 review) |
| `peter-i-buch-01` | `stil-02-poetisch` | 18 | 18 | 0 (11 done, 7 review) |
| `pharao` | `stil-02-poetisch` | 69 | 69 | 0 |
| `pissemski-tausend-seelen` | `stil-01-original` | 44 | 0 | 44 (`stil-02-poetisch` komplett, `1beb55d`) |

Status-Drift B (Status `done`, Dateien unvollstaendig) ist in allen Paketen 0; die
Review-Marker (`aelita` 1, `leben-arsenjews` 54, `peter-i-buch-01` 7) sind gewollt.
Top-5 im Trockenlauf: 111 Kapitel / 221 Kommandos, 299.226 Quellwoerter (Summe
`words_source`).

**Pissemski / Chronik-Bilder:** Seit `1beb55d` auf `main`. Tausend Seelen
in `stil-02-poetisch` (Gate 0/0/5 + EPUB); Default-Style in `book.yaml`
bleibt `stil-01-original`. Chronik-Szenenbilder 021–048 sind versioniert
(Bebilderung 48/48).

### Geheime Geschichte der Mongolen

- Quelle `ja` → Ziel `de`; `structure.mode: scenes`; ~317 Abschnitte als `work/scenes/ja/NNN/scene-NN.md`
- Import: `python tools/import_geheime_geschichte.py` (Migration: `--migrate-existing`)
- Style `stil-04-original-geheim.md` = Embed-Profil (Interlinear/Edition)
- **Offen:** 14 Monolith-Kapitel in `stil-01-original` (`NNN/scene-01.md` = Ganzkapitel) abschnittsweise in `stil-04-original-geheim` neu uebersetzen: 000 (1 Szene) und 001–005, 007–013 (283 Szenen) = 284 Szenen, dazu Szene 07 in 014 (Provider-Fehler „Antwort ohne Text-Content“, `status/logs/014.log.md`)
- **Kapitel 006 – kein Drift:** dateiseitig fertig (20/20 Szenen in `stil-04-original-geheim`), aber aus einem Modellvergleich (deepseek-v4-pro/-flash, `anthropic/claude-sonnet-4.6`, zuletzt `qwen/qwen3.6-flash` am 2026-07-22, siehe `status/logs/006.log.md`). Der Review-Marker bleibt bewusst stehen
- **Style beim Batch zwingend explizit:** `tools/translate_batch.py --book geheime-geschichte-mongolen --missing --style stil-04-original-geheim --dry-run` plant 14 Kapitel (000, 001–005, 007–014) und ueberspringt 006 korrekt. Ohne `--style` (Default `stil-01-original`) plant derselbe Lauf 14 Kapitel **inkl. 006** – also ein bereits fertiges Kapitel erneut (Trockenlauf 2026-09-13, beide Varianten 14 Kommandos)

### Die dritte Chronik

- DE-Original (kein Übersetzungsprojekt); Import: `python tools/import_die_dritte_chronik.py`
- `chapter_as_scene`, Display `format: literary`
- Cover liegt; Export-Pfad bereit
- Redaktion 2026-09-18/19 ohne OpenRouter abgeschlossen: 008+012 clean 0/0,
  034 nur Satzzeichen, komplett-Runde 031/033/036 (Neufassungen; 031 bei
  0W/1I Stilmittel, 033+036 clean 0/0), mini 009/026/035 clean, 018 0W/4I,
  041 0W/1I. Gate ERROR=0/WARNING=13/INFO=36, 29/48 clean
- **Bebilderung komplett (2026-09-19):** 48/48 Kapitel bebildert
  (Kapitelbild 001-014, Szenenbild 008 + 015-048 = 49 Bilder + Cover).
  KDP-EPUB `book-die-dritte-chronik-stil-01-original-20260921-131112.epub`
  (50 Bilder, Gate 0 Fehler, ohne Bypass; aelterer Stempel
  `20260919-222611` ist ueberholt). Die Szenenbilder 021-048 sind noch
  untracked (Parallel-Session)
- **Offen (Release-Einschaetzung 2026-09-21):** Kindle Previewer +
  Leseprobe dieses EPUBs, KDP-Upload durch Nutzer, Amazon-URL
  zurueckspielen. Kontinuitaet: `docs/offene-punkte.md` Punkt 12.

### Leben Arsenjews

- Cover unter `assets/covers/` (nicht nur `work/cover.png`)
- Stil aktiv oft `stil-02-poetisch`; Übersetzung noch unvollständig (viele Kapitel fehlen)

### Top-5-Anlage 09/2026 (auf `main`)

Vier neue Roh-Pakete, alle `structure.mode: chapter_as_scene`, Default
`stil-01-original`, KI-Modell seit 2026-09-13 `deepseek/deepseek-v4.1-flash`
(Eintrag in `config/models.yaml` + `book.yaml: ai.model`),
`website.enabled: false` / `sort_order: 40`:

| ID | Titel | Kapitel | Cover |
|----|-------|---------|-------|
| `kuprin-duell` | Das Duell (Kuprin) | 23 (Глава I–XXIII) | `cover.png` |
| `kuprin-moloch` | Der Moloch (Kuprin) | 11 | `cover.png` |
| `grin-wellenlaeuferin` | Die Wellenläuferin (Grin) | 33 | `cover.png` |
| `pissemski-tausend-seelen` | Tausend Seelen (Pissemski) | 44 in 4 Teilen | `cover.png` |

- **Pilot 2026-09-13 gelaufen:** `kuprin-moloch` Kapitel 001 in `stil-01-original`
  mit `deepseek/deepseek-v4.1-flash` + `reasoning_effort: none`: 6682 Tokens
  (Prompt 4206 / Completion 2476), `finish_reason=stop`, 1245 DE-Woerter
  (119 % der 1049 RU-Woerter), Status `needs_review`
- Kette geprueft: `extract_scenes` → `translate_chapter` → `assemble_chapter`
  (`work/assembled/stil-01-original/001-translation-v1-…md`) → `export_manuscript
   --scope chapter --format epub` (`exports/stil-01-original/chapter/epub/…epub`,
  1,1 MB, nutzt `assets/covers/cover.png`)
- Rest offen: Moloch 002–011, Duell 23, Grin 33, Pissemski 44; Stilurteil anhand
  der Pilot-Szene noch offen (Default ueberall `stil-01-original`)
- Startbereit geprüft: `translate_batch --dry-run` plant 111 Kapitel / 221 Kommandos
  (kuprin-duell 23+22, kuprin-moloch 11+11, grin-wellenlaeuferin 33+33,
  pissemski-tausend-seelen 44+44); fehlende Quellszenen erzeugt der Batch selbst
- **Wichtig fuer Batch-Laeufe:** zuerst Quellszenen erzeugen (`extract_scenes`,
  macht der Batch automatisch). Ohne Quellszenen bleibt der Kapitelstatus auf
  `in_progress`, weil `chapter_translations_complete()` die Quellszenen braucht
- `--model` und `--reasoning-effort` muessen nicht mitgegeben werden – beides
  kommt aus `book.yaml`
- Tool-Fix: `Глава I` / `Глава X` (römische Ziffern, case-insensitive) in
  `tools/extract_chapters.py` + `tools/lib/rtf_parser.py`; Regressionstests in
  `tests/test_extract_chapters.py` (5 Tests grün)
- `website:`-Block lag eingerückt unter `book:` und wurde auf top-level
  gezogen. Generator und Dashboard lesen nur top-level (siehe AGENTS.md,
  Abschnitt Export); das Dashboard hätte sonst einen zweiten Block angehängt
- `staging/` (`conv5.py`, `top5-quellen/`) ist Arbeitsmüll und seit 09/2026 via
  `.gitignore` ausgenommen (lokal gefahrlos löschbar)
- Auswahlgrundlage: `docs/Motivatier-Classics-Umsetzungsrangliste-45.md`,
  Titelsuche: `docs/Motivatier-Classics-Titelsuche-2026-09-08.md`

## Bekannte Fallstricke (geprueft 2026-09-13)

Alle drei Punkte stammen aus einem lesenden Audit. Kernbefund-Quelle: `--missing`
arbeitet **dateibasiert** ueber `chapter_complete()` (`lib/output_paths.py`), nicht
ueber `status.json`. Reproduzierbarer Check, ohne etwas zu schreiben:

```bash
python tools/translate_batch.py --book <id> --missing --style <style> --provider prompt_file --dry-run
```

### 1. `status.json` ist durchgaengig zu pessimistisch

Der Status wird nur von `translate_chapter --auto-status` und `tools/status.py mark`
geschrieben; Importe und Migrationen setzen ihn nicht nach. Ergebnis: Kapitel, deren
DE-Szenen-Dateien vollstaendig vorliegen, stehen weiter auf `pending`.

| Buch | Datei komplett (Default-Style) | Status `done` | Drift |
|------|-------------------------------|---------------|-------|
| `aelita` | 30/30 | 0 | 30 |
| `leben-arsenjews` | 104/104 | 0 | 104 |
| `pharao` | 69/69 | 10 | 59 |
| `feuriger-engel` | 5/16 | 0 | 5 |
| `anna-karenina` | 2/239 | 0 | 2 |
| `geheime-geschichte-mongolen` | 1 komplett, 13 teilweise | 0 | 1 |
| `die-dritte-chronik` | 48/48 | 48 | 0 (konsistent) |

Der umgekehrte Fall (Status `done`, Dateien unvollstaendig) kam in keinem Paket vor –
der Status ist nie zu optimistisch, nur nie nachgefuehrt.

Reparatur ueber den offiziellen CLI-Weg, kein manuelles JSON:
`python tools/status.py --book <id> mark <nnn> done`.
Geplanter Umfang dieser Reparatur (Dry-Run geprueft): 193 Kapitel –
`aelita` 30, `leben-arsenjews` 104, `pharao` 59.

Zusatz: `status.json.style_mode` ist nur ein Snapshot vom Anlagezeitpunkt und lief nicht
nach (`aelita` `stil-01-original` vs. `book.yaml` `stil-03-branderson`, `leben-arsenjews`
`stil-01-original` vs. `stil-02-poetisch`). **Behoben 2026-09-13:** an `book.yaml`
angeglichen (5 Pakete, ueber `load_state`/`save_state`); `status.py` selbst hat fuer
dieses Feld keinen Schreibbefehl.

**Behoben 2026-09-13 (verlustfrei):** Alle Kapitel mit vollstaendigen DE-Szenen im
Default-Style haben jetzt den Endstatus. Ergebnis: `aelita` 30/30 (29 done, 1 review),
`leben-arsenjews` 104/104 (50 done, 54 review), `pharao` 69/69, `peter-i-buch-01` 18/18
(11 done, 7 review), `feuriger-engel` 16/16, `anna-karenina` 166/239 (73 offen),
`geheime-geschichte-mongolen` 14/15, `die-dritte-chronik` 48/48 (war schon konsistent).
Summe: 390 Kapitel auf `done`, 62 auf `needs_review`.

**Warnung aus diesem Fix:** `status.py mark <nnn> done` setzt `needs_review=false`,
`words_target=0` und `completed_at=<jetzt>`. Fuer das Nachreparieren bereits fertiger
Kapitel daher die Bibliotheks-API (`lib/status_manager.load_state`/`save_state`) nutzen und
die Review-Marker stehen lassen – sonst gehen Metadaten verloren. Der erste Anlauf wurde
genau deshalb am 2026-09-13 zurueckgerollt und aus der Git-Historie restauriert.

### 2. Default-Style weicht vom Arbeits-Style ab (Doppeluebersetzungsgefahr)

| Buch | `book.yaml` → `style_mode` | tatsaechlich komplett | Export-Ordner | Evidenz |
|------|---------------------------|-----------------------|---------------|---------|
| `peter-i-buch-01` | `stil-03-branderson` | 18/18 in `stil-02-poetisch` | nur `exports/stil-02-poetisch` | `status/logs/005.log.md`: „Style-Profil … stil-02-poetisch.md verwendet“ |
| `feuriger-engel` | `stil-01-original` | 16/16 in `stil-02-poetisch` | nur `exports/stil-02-poetisch` | – |
| `anna-karenina` | `stil-01-original` | 166/239 in `stil-02-poetisch` | `exports/stil-02-poetisch` + `stil-01-original` | – |
| `leben-arsenjews`, `pharao`, `aelita` | passt zum Arbeits-Style | vollstaendig | passend | – |

Folge im Trockenlauf: `peter-i-buch-01 --missing` mit dem Default plant **18 Kapitel
(~229k Quellwoerter)**, mit `--style stil-02-poetisch` dagegen **0**. Bei
`feuriger-engel` 11 statt 0, bei `anna-karenina` 237 statt 73.

**Behoben 2026-09-13:** `style_mode` in `book.yaml` auf den realen Arbeits-Style gesetzt –
`peter-i-buch-01`, `feuriger-engel` und `anna-karenina` auf `stil-02-poetisch`. Trockenlauf
ohne `--style` plant jetzt 0 / 0 / 73 Kapitel.

**Offen (2026-09-13 belegt):** `geheime-geschichte-mongolen` ist ein zweiter Fall.
`book.yaml` und `status.json` stehen auf `stil-01-original`, produktiv ist aber
`stil-04-original-geheim` (Kapitel 006 vollstaendig, 014 teilweise). Trockenlauf wie
oben: der Default plant 14 Kapitel **inklusive 006** (schon fertig ->
Doppeluebersetzung), `--style stil-04-original-geheim` plant 14 Kapitel mit 000 statt
006. Der Default bleibt vorerst unveraendert, weil die 13 Monolith-Kapitel noch in
`stil-01` liegen; bis zur Entscheidung gilt hier zwingend die explizite Style-Angabe.

**Regel:** Vor jedem `--missing`-Lauf Style explizit mitgeben und gegen die
Export-/Log-Evidenz pruefen.

Nebenbefund: `peter-i-buch-01` enthaelt Style-Ordner ohne Profil –
`work/scenes/de/stylized` (38 Szenen), `work/scenes/de/gemma4-vergleich` (4) sowie
`work/assembled/literal` und `work/assembled/stylized`. Alt-Vergleichsartefakte, die
die CLI nie erzeugen wuerde; verschoben am 2026-09-13 nach
`work/legacy/style-artefakte-20260913/` (65 Dateien: 38 + 4 + 1 + 22, siehe README dort).

### 3. `source_lang == target_lang` erzeugt Phantom-Kapitel (aktuell Die dritte Chronik)

In `books/die-dritte-chronik/work/scenes/de/` liegen die Kapitelordner `001…048`
(Quellszenen) **und** darunter `stil-01-original/001…048` (Zielszenen). Weil
`chapter_ids()` (`lib/workbench_state.py`) alle Verzeichnisse unter
`scenes/<source_lang>` als Kapitel-IDs sammelt, wird der Style-Ordner selbst zur
Kapitel-ID:

```
=== Batch: Die dritte Chronik ===
Kapitel ausgewaehlt (1): stil-01-original
[1/2] python tools/extract_scenes.py --book die-dritte-chronik --chapter stil-01-original
[2/2] python tools/translate_chapter.py --book die-dritte-chronik --chapter stil-01-original ...
```

Betroffen war jedes Paket mit `source_lang == target_lang` (aktuell nur die Chronik).

**Behoben 2026-09-13:** `chapter_ids()` ueberspringt Style-Ordner – ueber Namensabgleich
mit `styles/*.md` und, bei gleicher Quell- und Zielsprache, zusaetzlich ueber das
Strukturmerkmal „Ordner ohne direkte `scene-*.md`“. Regressionstests in
`tests/test_workbench_state.py`. Beleg nach dem Fix: `--missing --dry-run` plant
0 Kapitel (vorher 1), der Fortschritt meldet 48/48 statt 49/1. Der Guard entfaellt.

### 4. Reasoning-Modelle verbrennen `max_tokens` im Denkschritt (V4.1 Flash)

`deepseek/deepseek-v4.1-flash` ist reasoning-faehig. Ohne Steuerung schreibt das
Modell den kompletten `max_tokens`-Vorrat (`book.yaml: max_tokens_per_scene: 10000`)
in den Denkschritt und liefert **keinen** Text; der Client meldet dann korrekt
`OpenRouter-Antwort ohne Text-Content` (`finish_reason=length|error`).

Gemessen 2026-09-13 mit Mini-Calls (je ~400 Token Budget, `max_tokens=400`):

| `reasoning.effort` | Ergebnis | reasoning_tokens |
|--------------------|----------|------------------|
| nicht gesetzt | kein Content | 400/400 |
| `minimal` | kein Content | 142 |
| `low` | kein Content | 400/400 |
| **`none`** | **Text, `finish_reason=stop`** | **0** |

Nebenbei: Ein ungesetzter Lauf kann sehr lange „haengen“ (Header kommen, Body
nicht) – ein `httpx`-ReadTimeout greift dann nicht zuverlaessig; nicht blind
weiterwarten, sondern Prozess beenden und `status.py`-Status per
`lib/status_manager.mark_pending` zuruecksetzen.

**Behoben 2026-09-13:** `OpenRouterClient.reasoning_effort` +
`build_chat_payload()` in `tools/lib/openrouter_client.py`, CLI-Flag
`translate_chapter.py --reasoning-effort`, Fallback `book.yaml:
ai.reasoning_effort`. Die vier Top-5-Pakete stehen auf `none`; Regressionstests
in `tests/test_openrouter_client.py` (4 Tests). Laeufe ohne Angabe bleiben
unveraendert (Payload ohne `reasoning`).

### 5. Technische Kopfzeilen der Quelle landeten in der Uebersetzung

`work/chapters/NNN-source.md` beginnt mit `# Kapitel N: Глава I`, `*Buch: …*` und
`<!-- status: pending -->`. Im `chapter_as_scene`-Modus geht die ganze Datei in
den Prompt – das Modell uebernahm diese Zeilen unveraendert in die DE-Szene
(inklusive Kyrillisch in der Ueberschrift).

**Behoben 2026-09-13:** harte Ausgabe-Regel in `tools/lib/style_prompts.py`
(„Technische Kopfzeilen … weder uebersetzt noch uebernommen noch ersetzt“).
Beleg: Kapitel 001 beginnt nach `--overwrite` direkt mit dem Fliesstext.

Nebenbefund: `output.strip_control_metadata` in `export.yaml` ist ein **toter
Schalter** – kein Code liest ihn (nur `init_book.py` schreibt ihn). Die
Metadaten-Hygiene muss daher im Prompt bzw. in der Szene passieren.

Kleinigkeit: `status.json: title_de` ist bei Kapiteln ohne Ueberschrift der erste
Absatz (Log-Kopfzeile wird lang). Nur kosmetisch – der Export nutzt `title_de`
nicht.



### Fixes zu diesen Befunden (Fallstricke 1-5, alle umgesetzt 2026-09-13)

1. Status-Reparatur: dateibasiert und verlustfrei gesetzt – 390 Kapitel `done`, 62 `needs_review`; Metadaten aus der Git-Historie restauriert
2. `style_mode`: `book.yaml` von peter-i, feuriger-engel und anna auf `stil-02-poetisch`; `status.json.style_mode` in 5 Paketen angeglichen
3. Phantom-Kapitel bei `source_lang == target_lang`: `chapter_ids()` ueberspringt Style-Ordner (+ Regressionstests in `tests/test_workbench_state.py`)
4. Peter-I-Artefakte nach `work/legacy/style-artefakte-20260913/` verschoben (65 Dateien, README dort)
5. Reasoning-Steuerung fuer `deepseek/deepseek-v4.1-flash`: Client-Feld + `build_chat_payload()`, CLI `--reasoning-effort`, `book.yaml: ai.reasoning_effort: none`, 4 Regressionstests (Fallstrick 4)
6. Technische Kopfzeilen der Quelle (`# Kapitel …`, `*Buch: …*`, `<!-- … -->`) aus der Uebersetzung ausgeschlossen (Fallstrick 5)

### 6. Der Wort-Ratio-Korridor liess Raffung durch (Peter, entdeckt 2026-09-17)

`length_ratio` ist bewusst ein Ausreisser-Melder (ERROR `< 0.55`/`> 2.60`,
WARNING `< 0.75`/`> 2.10`) - und damit **kein Vollstaendigkeitsnachweis**.
Bei Peter der Erste lagen drei geraffte Szenen bei 0.76-0.91, der Buch-Median
bei 1.30: alle durchgerutscht, obwohl der Absatzschwund (-50 bis -73 Absaetze)
so gross war wie bei den drei bereits behobenen Szenen. Ein "0 Fehler, 0
Warnungen" aus dem alten Korridor war also kein Beweis fuer Vollstaendigkeit.

**Erkennen (read-only, ohne LLM):** Szenen-Wortratio und Absatzbestand ueber
alle Szenen rechnen; Median, Minimum und die unteren Ausreisser ansehen.
Segmentvergleich ueber 10 Textbloecke trennt Raffung (gleichmaessig duenn)
von einem abgebrochenen Lauf (leeres Ende).

**Behoben 2026-09-17:** zwei neue Kategorien (`paragraph_drop`,
`length_outlier`, Details in `AGENTS.md` -> Release-Gate), buchweite
Auswertung in `review_manuscript.py` **vor** dem KI-Review (damit
`--llm-scope flagged` die Szenen mitprueft), 7 neue Tests (23 gesamt), und
die drei Szenen selbst neu uebersetzt.

**Lehre fuer neue Buecher:** Nach jedem Buchlauf beide neuen Kategorien lesen,
Chunking-Limit bewusst setzen (globaler Default 24000 Zeichen, Peter wurde
mit 7000 nachgezogen), und `names.yaml` vorher fuellen - sonst laeuft
`accented_transliteration` leer.

## Tools (Auswahl, neu / relevant)

| Tool | Zweck |
|------|--------|
| `tools/lib/repetition.py` | Stil-Wiederholungsdetektor (Anapher/Trigramm/Echo/Stapelung/TTR/Leerformel), Kategorie `repetition_style`, nur INFO/WARNING; Tests `tests/test_repetition.py` + Fixtures `tests/repetition_fixtures.py` |
| `tools/build_shelf_website.py` | Katalog + Cover für `webpage/` |
| `tools/build_webpage_dist.py` | Production-Build `webpage/dist/` (Windows: `npm.cmd`) |
| `tools/preview_webpage.py` | Lokale Vorschau Port 4173 |
| `tools/import_geheime_geschichte.py` | Mongolen-Import |
| `tools/import_die_dritte_chronik.py` | Chronik-Import |
| `tools/optimize_asset_images.py` | Export-JPGs verkleinern |
| `tools/generate_illustration.py` | Higgsfield Kapitel/Szenen |
| `tools/review_manuscript.py` | Deterministischer Regelcheck + Release-Gate (`--llm none --fail-on-errors`); seit 2026-09-17 inkl. `paragraph_drop` + buchweitem `length_outlier`. Im Dashboard = Action `review` (Scope "Ganzes Buch" fuer den Median-Check) |
| `tools/export_manuscript.py --format paperback` | KDP-Taschenbuch-Innenleben (5,5×8,5, Bundsteg-Iteration, Kolumnentitel). `--format paperback-complete` addiert Cover-Print/Rueckseite/Wrap und Reihenkatalog. A5-Vorschau bleibt `--format pdf`. Wrap = Umschlagbogen, nicht der Buchtext. |
| `tools/lib/print_{spec,css,pdf,wrap}.py` | Print-Spec, EB-Garamond-CSS, Playwright-PDF, Wrap-Bogen |
| `tools/lib/series_catalog.py` | Reihenkatalog am Buchende (`website.enabled`, `website.catalog: false`) |
| `tools/export_marketing.py` | Marketingpaket (Beitraege, YouTube-Materialien, `campaign.json`); siehe [marketing-export.md](marketing-export.md) |
| `tools/kdp_sync.py` | KDP-Adapter Phase 1 (2026-10-13): `status`, `login`, `pull`, `diff`, `bind`. Skill als Submodule `tools/vendor/amazon-kdp-skill` (HTTP `127.0.0.1:3001`). Soll aus `export.yaml` `book.*`, Join-Keys nur in top-level `amazon:`. Kein Update, Preis, Upload oder Publish. Vor `status`: `npm install` im Vendor-Ordner. |

Higgsfield: [docs/higgsfield-integration.md](higgsfield-integration.md). Web-UI-Moodboards sind CLI-seitig nicht wählbar.

## Sinnvolle nächste Schritte

0. **Peter der Erste (`peter-i-buch-01`) – vorgezogen 2026-09-16, abgeschlossen 2026-09-17.** Anlass: zwei
   1-Stern-Kindle-Rezensionen („schlecht uebersetzt", „sinnentstellend";
   Konkurrenz-These moeglich, Verkaeufe ungeprueft). Entscheidung: Volluebersetzung.
   Phase A (deterministisch, ohne LLM): Vollscan `--llm none` ueber 18 Kapitel
   (Ausgangsstand ERROR=7/WARNING=6, der alte Report von 2026-06-15 war veraltet),
   danach 18 Fixes per `apply_review_suggestions.py --plan/--stage/--promote`
   (5 gemischte Kyrillisch-Tokens, 7 Akzent-Transliterationen, 4 doppelte
   Szenenheader, erfundene russische Lede in 018/01, `names.yaml` um 9 Eintraege
   erweitert).
   Phase B (mit Freigabe): die 3 gerafften Szenen (011/03 ratio 0.49 = ERROR,
   002/11 0.69, 003/05 0.60) mit Chunking + `--overwrite` neu uebersetzt.
   **Nachtrag 2026-09-17:** Der Vollscan **aller 175 Szenen** (Wortratio +
   Absatzvergleich + Segmentprofil) fand drei weitere geraffte Szenen, die der
   Wort-Korridor nie gemeldet hatte: `009/scene-08` (0.91, Absaetze 109:182),
   `010/scene-01` (0.84, 107:169), `010/scene-02` (0.76, 102:152) - alle in
   Buch II, also derselbe damalige Lauf. Ebenfalls neu uebersetzt
   (`--chunk-char-limit 7000`, 5/6/6 Chunks, `Finish-Reason=stop`); Endstand:
   1.35 / 1.31 / 1.29 mit Absaetzen 183:182 / 170:169 / 153:152.
   Endstand Buch: **175 Szenen, Ratio-Median 1.30, Minimum 0.97**
   (`003/scene-04`, inhaltlich unauffaellig: Absatzdefizit -7).
   Regelcheck danach: **18 Kapitel, 0 ERROR / 0 WARNING / 0 INFO**
   (mit aktiven neuen Kategorien), Export `book-peter-der-erste-stil-02-poetisch-20260917-113509.epub`
   mit `review_gate_errors: 0` und `review_gate_bypassed: false`.
   Offen (bewusst, keine Code-Aufgabe): EPUB-Groesse/ Bilder, Kindle Previewer,
   und eine menschliche Stichprobe der drei neu uebersetzten Szenen (der
   Regelcheck beweist Form, nicht Sinn).
   **Nutzerentscheidung 2026-09-17:** Stilfragen werden zurueckgestellt - es
   geht nur um belegbare Fehler und die Nachweisbarkeit der Regelchecks, nicht
   um ein Stilurteil.
   Details + Fehlerklassen: `docs/offene-punkte.md` (Punkt 0 und 0.1).
1. **Release-Gate (umgesetzt 2026-09-16).** `export_manuscript.py::preflight_review_gate`
   bricht bei Review-ERROR>0 mit Exit 2 ab; Bypass nur `--allow-review-errors`
   (wird im Manifest protokolliert). Neue Kategorien in `review_checks.py`:
   `mojibake`, `accented_transliteration`, `duplicate_heading`; Ausnahmen fuer
   echte Originalzitate via `work/review-allowlist.yaml`. Ein Export mit ERROR>0
   hat 2026-09 den live veroeffentlichten Peter-I-Band erreicht – das ist jetzt
   technisch verhindert. Doku: `AGENTS.md` (Abschnitt `Release-Gate`).
2. Marketingexport ist auf `main` (seit 2026-09-13/21). Offen: Amazon-URLs
   in den restlichen `export.yaml`-Dateien, optional Songdaten, optional
   `marketing.campaign_start`. Ein echter OpenRouter-Textlauf ist
   kostenpflichtig und braucht ausdrueckliche Freigabe.

3. Top-5-Pakete: Pilot `kuprin-moloch` 001 ist gelaufen (2026-09-13, `needs_review`, 6682 Tokens, EPUB-Kette geprueft) – naechster Schritt ist das Stilurteil anhand dieser Szene; danach je Buch `translate_batch.py --missing --style stil-01-original --auto-status --assemble-after` (batch-seitig kein `--model`/`--reasoning-effort` noetig, beides kommt aus `book.yaml`; ohne `--auto-status` bleibt `status.json` auf `pending` → Status-Drift)
4. Regal-Freigabe nach der finalen Cover-Wahl (`website.enabled: true`, `sort_order` 41–43; `kuprin-duell` behält 40), danach `python tools/build_shelf_website.py` – die Handcover sind seit `0162ef9` im Repo, die Regal-Kopien fuer aelita/mongolen aber noch alt. Cover entstehen weiter von Hand (kein CLI-Weg: `generate_illustration.py` kennt nur `--kind scene|chapter`)
5. Anna Karenina: 73 offene Kapitel (167–239) in `stil-02-poetisch` – Default-Style ist jetzt korrekt gesetzt
6. Geheime Geschichte: 14 Monolith-Kapitel abschnittsweise in `stil-04-original-geheim` (000, 001–005, 007–013 = 284 Szenen) plus Szene 07 in 014; Kapitel 006 ist dateiseitig fertig und wartet nur auf Review
7. Dritte Chronik (2026-09-21 nachm., KDP-fertig): Gate
   ERROR=0/WARNING=13/INFO=36, Bilder 48/48 (EPUB
   `...-20260921-131112.epub`, 50 Bilder, ohne Bypass). Redaktion
   kapitelweise ohne OpenRouter abgeschlossen (Stand 19.09.):
   komplett-Runde 031 (Neufassung 3753 W), 033 (3539 W, clean),
   036 (785 W, clean); mini 009/026/035 clean, 018 0W/4I, 041 0W/1I;
   025-Neufassung ("Der Onkel", 3103 W, 0/0/0 + repetitonsfrei).
   KDP-Rollen 21.09.: Autor Timo Verita, Editor Motivatier Classics
   (kein Uebersetzer – deutsches Original!), Verlag/Herausgeber
   Motivatier Stiftung (ohne "Hermann", repo-weit 71 Stellen
   ersetzt). Bio Variante 3 ("zwei Haelften", Buchstabenspiel,
   Welt-von-gestern + aktueller Schauplatz). Titelei + Impressum
   mit Classics oben, Stiftung unten. KDP-Texte:
   `docs/kdp-texte-dritte-chronik.md`. Rest-Tabelle
   `docs/offene-punkte.md` Punkt 6 + Punkt 12 (Kontinuitaet,
   Bio, Reihen-Auftritt; Kontinuitaets-Modell
   `docs/kontinuitaetspruefung-chronik.md`). Umgesetzt 21.09.
   nachm.: Untertitel "Die Chronik derer, die nicht schreiben
   duerfen" in `export.yaml: book.subtitle` + EPUB-Titelei
   (verifiziert) + Regal-Katalog neu; KDP-Serie "Chroniken des
   Mongolenreichs" (Band 1 Chronik, Band 2 Geheime Geschichte)
   nur in KDP anzulegen (Serientexte in `docs/kdp-texte-dritte-chronik.md`
   Abschnitt 5). Offen nur noch: Kindle Previewer +
   Leseprobe, KDP-Upload durch Nutzer, Amazon-URL zurueckspielen.
8. Regal: Amazon-URLs setzen; optional Mint-Hardcover-GLBs; Deploy von `webpage/dist/`
9. Optional: Feature-Branch `codex/geheime-geschichte-mongolen-prompts` remote löschen, wenn alle Clients auf `main` sind
10. Anna-Cover: geprueft und erledigt – `export.yaml` setzt `cover.mode: image` mit `image_path: assets/covers/annakarenina.png` (Vorrang vor `find_named_image(..., "cover")`); nur bei geleertem Feld droht der Platzhalter
11. Aelita Release-Kandidat (2026-09-17): Regelcheck 0/0 ueber alle 30 Kapitel. Kapitel 030: Romantext endet in der DE-Szene, Editionskommentare der RU-Quelle sind vollstaendig in den Anhang „Kommentare“ ausgelagert (`work/appendices/de/stil-03-branderson/kommentare.md`; alte Fassung in `work/legacy/`). Neues `appendices:`-Feature: `tools/lib/editorial_appendices.py`, Export EPUB/DOCX/PDF, Gate-Anrechnung in `review_checks.py` (27 Export-Tests gruen). 16 Kapitelbilder optimiert (Export-JPG q60, max 1600x2400, ~14,8 → ~2,4 MB); 12 Kapitel bleiben bewusst ohne Bild (009, 010, 011, 012, 016-019, 022-027); 11 wiedergefundene Motive fuer 020-030 liegen in `work/image-recovery/20260917-165216/verified/` zur freien Nutzung. Buch-EPUB `...-20260917-180435.epub` (Gate 0 Fehler) von Nutzer geprueft. Offen: Kindle Previewer.
12. Taschenbuch (2026-09-21, auf `main`; Zahlen 2026-09-27 aktualisiert):
    `--format paperback` = Innenleben; `--format paperback-complete` =
    Lese-PDF plus Wrap. Trim `--trim-size 5.5x8.5|6x9`, Profil
    `classic|long_classic`, Bilder `full_page|inline` getrennt waehlbar.
    Cream-Limit 776. Wrap = Umschlagbogen Rueckseite|Ruecken|Vorderseite,
    nicht der Text. Pharao A–D: 923 / 787 / 672 / 642 Seiten (vorher je eine
    zu hoch, Leerseiten-Bug behoben). Offen: menschliche Print-Leseprobe,
    Entscheidung 787 vs. 776 fuer 6x9 classic, `cover-print` fuer andere
    Titel.
13. Buchbilder (2026-09-27): `assets/master/` (2k) eingefuehrt, Paperback liest
    dort zuerst. Bestand bewusst nicht neu erzeugt – siehe
    `docs/offene-punkte.md` Punkt 13.

Covers und Übersetzungsläufe (OpenRouter-Kosten) nur nach ausdrücklicher Freigabe starten.

## Nicht anfassen ohne Rückfrage

- `books/<id>/source/`
- `logic/`
- Secrets / `.env`
- Destruktive Git-Operationen (force-push, hard reset) ohne explizite Freigabe
