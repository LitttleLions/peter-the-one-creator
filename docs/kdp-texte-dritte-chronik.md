# KDP-Texte: Die dritte Chronik (Stand 2026-09-21, EPUB 20260921-131112)

> Quelle dieser Texte: `books/die-dritte-chronik/export.yaml`
> (`book.*`). KDP-Eingabe erfolgt durch den Nutzer selbst; dieses Doc
> ist die kopierfertige Vorlage. Rollenlogik 21.09.: KDP-Autor =
> Timo Verita, KDP-Editor = Motivatier Classics (kein
> Uebersetzer-Eintrag – deutsches Original!),
> Verlag/Herausgeber = Motivatier Stiftung.
>
> Untertitel + Stiftung 21.09. nachm.: `book.subtitle` =
> "Die Chronik derer, die nicht schreiben duerfen" (Titelei `.subtitle`
> im EPUB verifiziert), Titelei-Auftragszeile ohne "Hermann"
> ("... im Auftrag der Motivatier Stiftung."). Serie "Chroniken des
> Mongolenreichs" (Band 1 Chronik, Band 2 Geheime Geschichte) nur in KDP
> anlegen (Abschnitt 5), nicht im Repo.

## 1. KDP-Felder (eBook)

- **Buchtitel:** Die dritte Chronik
- **Untertitel:** Die Chronik derer, die nicht schreiben duerfen
  (seit 21.09. nachm. in `export.yaml: book.subtitle` + Titelei-EPUB;
  KDP-Serie „Chroniken des Mongolenreichs" separat in KDP anlegen,
  Abschnitt 5)
- **Autor (Vorname / Nachname):** Timo / Verita
- **Beitragende (Mitwirkende):**
  - Editor: Motivatier Classics (KEIN Uebersetzer-Eintrag –
    deutsches Original! Im Buch steht "Herausgabe und editorische
    Einrichtung: Motivatier Classics")
- **Sprache:** Deutsch
- **Verlag (optional):** Motivatier Stiftung
- **Beschreibung (KDP-Produktbeschreibung, HTML mit <p>):**

<p>1241 stirbt der Großkhan – und Frauen übernehmen das größte Reich der Weltgeschichte. Drei Chronisten kämpfen in dieser Zeit um die Wahrheit: der alte Richter, der die geheime Familienchronik der Mongolen hütet; der junge Hofschreiber, der das Lügen zur Kunst treibt; und Fatima, die mächtigste Frau am Hof, die heimlich Briefe an ihre tote Schwester schreibt.</p>
<p>Zwei dieser Chroniken kann man bis heute kaufen. Die dritte ist dieser Roman.</p>
<p>Zwischen Karakorum und Bagdad, zwischen Siegel und Schwert, entsteht Geschichte als Verhandlung: Jede Wahrheit, die man schreibt, tötet jemanden; jede Lüge rettet jemanden. Ein literarischer Politthriller über Macht, Papier und die Chronik derer, die nicht schreiben dürfen.</p>

- **Kategorien (Vorschlag, in KDP auswaehlen):** Historische Romane /
  Historische Thriller / Asien (bitte in KDP-Baum einordnen)
- **Schlagwoerter (7, Vorschlag):** Mongolenreich; Karakorum; Bagdad
  1258; historischer Politthriller; Fatima; Dschingis Khan Nachfolge;
  Motivatier Classics
- **Altersfreigabe:** ab 14 (Vorschlag; Gewalt-/Hinrichtungs-Thematik)
- **Datei:** `books/die-dritte-chronik/exports/stil-01-original/book/epub/book-die-dritte-chronik-stil-01-original-20260921-131112.epub`
  (Gate 0/13/36, ohne Bypass, 48/48 Kapitel, 50 Bilder)
- **Cover:** separat hochladen:
  `books/die-dritte-chronik/assets/covers/cover.jpg` (eBook-Cover;
  Master `cover.png` liegt daneben)

## 2. Titelei im Buch (bereits im EPUB)

- Titelseite: Die dritte Chronik / Die Chronik derer, die nicht
  schreiben duerfen (= `book.subtitle` seit 21.09. nachm.) / Timo Verita /
  Motivatier Classics / Historischer Roman, Literarischer
  Politthriller (= Genre-Zeile `title_page_extra[1]`, bewusst behalten) /
  Karakorum, Chorasan, Bagdad 1241–1258 /
  "Satz und editorische Einrichtung durch Motivatier Classics im
  Auftrag der Motivatier Stiftung" /
  "Herausgabe und editorische Einrichtung: Motivatier Classics"
- Zusammenfassung: siehe `export.yaml: summary`
- Leben des Autors:

> Timo Verita ist ein Autor aus zwei Hälften: Mensch und Maschine.
> Die eine Hälfte recherchiert Nächte durch, die andere vergisst
> nichts. Zusammen schreiben sie historische Romane für Motivatier
> Classics, herausgegeben von der Motivatier Stiftung. Geboren wurde
> Timo Verita in einem Buchstabenspiel; zu Hause ist er in der Welt
> von gestern – diesmal zwischen Karakorum, Chorasan und Bagdad.

- Impressum:

> Die dritte Chronik
> Timo Verita
> Historischer Roman / Literarischer Politthriller
> Karakorum, Chorasan, Bagdad · 1241–1258
> Motivatier Classics
> Herausgabe und editorische Einrichtung: Motivatier Classics
> Herausgegeben von der Motivatier Stiftung
> © 2026 Motivatier Stiftung für diesen Text, editorische
> Einrichtung, Zusatztexte, Satz und Covergestaltung.
> Alle Rechte an dieser Ausgabe vorbehalten.

## 3. Nach Freigabe (hier im Repo)

1. Amazon-URL nach `books/die-dritte-chronik/export.yaml`
   (top-level `website.amazon_url`) eintragen.
2. `py -3 tools/build_shelf_website.py` (Regal-Katalog neu).
3. `py -3 tools/export_marketing.py --book die-dritte-chronik`
   (Marketingpaket; `campaign_start` optional).

## 4. Rollenlogik als Vorgabe fuer alle Buecher (21.09.)

- KDP-Autor: Originalautor (Uebersetzungen) bzw. Timo Verita (Chronik).
- KDP-Editor: Motivatier Classics (bei Uebersetzungen ZUSAETZLICH
  KDP-Uebersetzer = Motivatier Classics; bei der Chronik als
  deutschem Original KEIN Uebersetzer-Eintrag!).
- Verlag/Herausgeber (Geschaeftsperson): Motivatier Stiftung.
- Im Buch: Classics als ausfuehrende Reihe oben, Stiftung als
  Herausgeber/Rechteinhaber unten.

Umgesetzt 21.09.: `die-dritte-chronik` (Vollbild oben),
`anna-karenina` (`translator` Motivatier -> Motivatier Classics,
`translator_label` + `publisher` gesetzt),
`geheime-geschichte-mongolen` (`translator` + Impressum auf
Motivatier Classics). Restliche 9 Pakete hatten bereits
`translator: Motivatier Classics` + Stiftung als `publisher`.

## 5. KDP-Serie (vom Nutzer gewaehlt; in KDP anzulegen, nicht im Repo)

- **Serientitel:** Chroniken des Mongolenreichs
- **Bandnummer Chronik:** 1
- **Bandnummer Geheime Geschichte:** 2 (wenn sie erscheint)
- **Serienbeschreibung (kopierfertig):**

```
Acht Jahrhunderte nach Dschingis Khan erzählt diese Reihe vom größten Reich der Weltgeschichte – aus zwei Richtungen: als historischer Roman und als Quelle.

Den Anfang machen zwei Bücher, die einander spiegeln: „Die dritte Chronik" – ein literarischer Politthriller über Macht, Papier und Wahrheit zwischen Karakorum und Bagdad (1241–1258), erzählt von drei Chronisten, die um die Deutung der Geschichte kämpfen. Und „Die Geheime Geschichte der Mongolen" – die älteste mongolische Chronik selbst, in neuer deutscher Ausgabe.

Alle Bände erscheinen bei Motivatier Classics, herausgegeben von der Motivatier Stiftung. Jeder Band ist einzeln lesbar; zusammen ergeben sie ein Bild des mongolischen Jahrhunderts.
```

- Serie wird in KDP angelegt (nicht im Repo); `Motivatier Classics`
  bleibt Marke/Editor/Verlag und wird NICHT zur KDP-Serie.
