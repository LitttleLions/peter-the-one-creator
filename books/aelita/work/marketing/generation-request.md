# Arbeitsanweisung: Marketingtexte fuer Aëlita

Ziel: die Datei

```text
books/aelita/work/marketing/generated.json
```

befuellen. Struktur: `texts` (Beitrags-IDs) und `youtube`. Kopfdaten:

```json
{
  "schema_version": 1,
  "book_id": "aelita",
  "style": "stil-03-branderson",
  "generator": "workspace_ai",
  "model": "<Modellname der bearbeitenden KI>",
  "generated_at": "<ISO 8601>",
  "prompt_version": "marketing-1",
  "source_hash": "ab2b327d9521b2f6",
  "texts": {},
  "youtube": {}
}
```

Die `source_hash` muss exakt uebernommen werden; sie steuert, ob ein
erneuter Export die Texte als aktuell ansieht.

## System

Du schreibst Verkaufsbegleittexte fuer eine deutsche Buchausgabe der Marke Motivatier Classics.

Harte Regeln:
- Erfasse ausschliesslich Aussagen, die aus dem gelieferten Datenbrief belegt
  sind. Erfinde keine Rezensionen, Zitate, Auszeichnungen, Verkaufszahlen,
  biografischen oder historischen Tatsachen.
- Erfinde keine Textstellen. Wenn du eine Buchpassage zitierst, nutze nur die
  gelieferte Leseprobe und kennzeichne sie als Zitat aus der Ausgabe.
- Schreibe keine werblichen Saetze, die wie ein Zitat des Autors wirken.
- "Jetzt erschienen" nur, wenn der Datenbrief das ausdruecklich belegt. Sonst
  nutze "Unsere Ausgabe", "Heute stellen wir vor" oder einen direkten
  inhaltlichen Einstieg.
- Keine generischen Superlative, keine kuenstliche Dringlichkeit, keine
  erfundenen Leserreaktionen, keine Hashtag-Wolken.
- Variiere Satzbau und Einstieg zwischen den Beitraegen. Wiederhole nicht den
  Klappentext.
- Beschreibe die Ausgabe nur mit belegbaren Eigenschaften.
- Jeder Beitrag hat einen klaren naechsten Schritt, aber KEINE URL im Text:
  die Adressen haengt das Exportprogramm an.
- Rede ueber das Buch, nicht ueber die Kampagne.

## Auftrag

Datenbrief zur Ausgabe:

- Buch-ID: aelita
- Titel: Aëlita
- Untertitel: Ein Mars-Roman zwischen Liebe, Revolution und Untergang
- Autor: Alexei Nikolajewitsch Tolstoi
- Originaltitel: Аэлита (Закат Марса)
- Originalautor: Alexei Nikolajewitsch Tolstoi (1883–1945)
- Uebersetzung/Einrichtung: Motivatier Classics (Übersetzung und editorische Einrichtung)
- Herausgeber: Motivatier Stiftung
- Sprache: de
- Marke: Motivatier Classics

Kurzbeschreibung:
Alexei Tolstois Mars-Roman »Aëlita« ist einer der Gründungstexte der sowjetischen Weltraumliteratur und erscheint hier in einer neuen deutschen Ausgabe nach dem russischen gemeinfreien Original. Die Übersetzung und editorische Einrichtung wurden KI-gestützt erstellt und redaktionell geprüft.

Ausfuehrliche Inhaltsbeschreibung:
Der Ingenieur Mstislaw Los baut im Petrograd der frühen 1920er Jahre ein
ungewöhnliches Raumschiff und lädt Freiwillige zu einem Flug zum Mars ein.
Begleitet wird er von dem ehemaligen Rotarmisten Alexei Gussew. Die Reise
führt die beiden aus einer von Krieg, Entbehrung und Unruhe geprägten Erde
in eine Welt, die fremdartig erscheint und doch die Konflikte der Menschen
auf andere Weise wiederholt.

Auf dem Mars, den seine Bewohner Tuma nennen, finden Los und Gussew eine
alte Kultur vor, deren Städte, Kanäle und technische Hinterlassenschaften
vom Glanz einer vergangenen Epoche zeugen. Hinter dieser Architektur steht
jedoch eine Gesellschaft, die von sozialer Spaltung, Herrschaft und dem
Bewusstsein des eigenen Niedergangs geprägt ist. Während Gussew sich den
Unzufriedenen und ihrem Widerstand nähert, gerät Los in den Bann Aëlitas,
der Tochter des Herrschers Tuskub.

Der Roman verbindet die planetarische Romanze zwischen Los und Aëlita mit
einer Revolutionsallegorie und der Frage, ob Technik, Macht oder Liebe eine
erschöpfte Welt noch verändern können. Sein Mars ist zugleich Schauplatz
des Abenteuers, Spiegel der nachrevolutionären Erde und melancholisches
Bild einer Zivilisation, die ihren Untergang bereits vor Augen hat.

Zum Autor:
Alexei Nikolajewitsch Tolstoi (1883–1945) gehörte zu den vielseitigsten und
zugleich widersprüchlichsten Autoren der russischen Literatur des
20. Jahrhunderts. Sein Werk reicht von einem durch Symbolismus und
Modernismus geprägten Frühwerk über Exilprosa bis zu historischen Romanen,
Zukunftsphantastik, Kinderliteratur und der sowjetischen Literatur der
1930er und 1940er Jahre.

Zu seinen wichtigsten Werken zählen die Trilogie »Der Leidensweg«, der
historische Roman »Peter der Erste«, »Aëlita«, »Der Hyperboloid des
Ingenieurs Garin« sowie »Das goldene Schlüsselchen oder Die Abenteuer des
Burattino«. Tolstoi gilt als bedeutender Meister des historischen Romans und
als einer der frühen Wegbereiter der sowjetischen Science-Fiction. »Aëlita«
steht dabei an einer Schnittstelle seines Werks: Der Roman verbindet noch
die poetische und symbolistische Atmosphäre seiner frühen Prosa mit
technischem Zukunftsdenken, Abenteuerhandlung und politischer Allegorie.

Belegte Editionsangaben:
- Originaltitel: Аэлита (Закат Марса)
- Originalautor: Alexei Nikolajewitsch Tolstoi (1883–1945)
- Russische Vorlage: Аэлита
- Diese Ausgabe ist eine neue deutsche Ausgabe nach dem russischen gemeinfreien Original.
- Die Übersetzung und editorische Einrichtung wurden KI-gestützt erstellt und redaktionell geprüft.
- Kurze Vorspänne, Motti oder Orientierungstexte vor den Kapiteln stammen nicht aus dem Original, sofern solche in dieser Ausgabe verwendet werden.
- Herausgegeben von der Motivatier Stiftung

Namensglossar (Schreibweise verbindlich):
- Аэлита -> Aëlita
- Мстислав Сергеевич Лось -> Mstislaw Sergejewitsch Los
- Алексей Иванович Гусев -> Alexei Iwanowitsch Gussew
- Маша -> Mascha
- Арчибальд Скайльс -> Archibald Skyles
- Тускуб -> Tuskub
- Иха -> Icha
- Гор -> Gor
- Магр -> Magr
- Тубал -> Tubal
- Рама -> Rama
- Уру -> Uru
- Марс -> Mars
- Тума -> Tuma
- Талцетл -> Talzetl
- Петроград -> Petrograd
- Нева -> Newa
- Соацера -> Soazera
- Азора -> Asora
- Лизиазира -> Lisiasira
- Соам -> Soam
- Священный Порог -> Heilige Schwelle
- Ро -> Ro
- Атлантида -> Atlantis
- Магацитлы -> Magazitlen
- Аолы -> Aolen
- племя Гор -> Volk der Gor
- Сыны Неба -> Himmelsöhne
- Высший совет -> Oberster Rat
- лабиринт царицы Магр -> Labyrinth der Königin Magr
- Хавра -> Chawra
- Хао -> Chao
- Шохо -> Schocho
- Хаши -> Chaschi
- Ча -> Tscha
- Ихи -> Ichi
- Цитли -> Zitli
- Улла -> Ulla
- Олла -> Olla
- Лихта -> Lichta

Echte Leseprobe aus der fertigen deutschen Ausgabe:
(Quelle: Kapitel 001, Szene 1)

"In der Straße der Roten Morgenröte war ein seltsamer Anschlag erschienen: ein kleiner, grauer Zettel, an die abblätternde Mauer eines verlassenen Hauses genagelt."

Musikmaterial:
- kein Song vorhanden; musikalische Beitraege entfallen

Laengenvorgaben (gewichtet, URLs zaehlen als 23 Zeichen):
- X-Beitraege: hoechstens 280 Zeichen, Ziel 220-250 Zeichen, eine bis drei kurze Absaetze, kein Link im Text
- YouTube-Titel: hoechstens 100 Zeichen
- YouTube-Beschreibung: hoechstens 5000 Zeichen

Liefere ausschliesslich JSON in genau dieser Struktur:

{
  "texts": {
    "x-t0-intro": {
      "text": "<Buchvorstellung: zentraler Konflikt, Titel und Autor, belegbare Aussage zur Ausgabe>",
      "notes": "<kurze Begruendung der Motivwahl>"
    },
    "x-t1-song": {
      "text": "<nur wenn ein Song vorhanden ist, sonst leer>"
    },
    "x-t2-youtube": {
      "text": "<Ankuendigung des vollstaendigen Songs; ohne 'jetzt online', solange die Veroeffentlichung nicht belegt ist>"
    },
    "x-t5-content": {
      "text": "<eigenstaendiger inhaltlicher Gedanke>"
    },
    "x-t8-sample": {
      "text": "<kurze echte Passage mit Zitatkennzeichnung oder eine belegbare Besonderheit der Ausgabe>"
    },
    "x-t12-second-angle": {
      "text": "<zweiter Aspekt, andere Perspektive als T+0 und T+5>"
    }
  },
  "youtube": {
    "title": "<Titel nach Muster 'Buchtitel - Songtitel | Lied zum Roman von Autor'>",
    "prequel": "<eine bis zwei Saetze Vorschau>",
    "body": "<zwei bis vier Saetze zu Roman und musikalischer Interpretation>",
    "thumbnail_label": "<kurze Beschriftung fuer das Vorschaubild>",
    "shorts": {
      "yt-short-1": {
        "title": "<Titel>",
        "description": "<kurze Beschreibung>",
        "overlays": [
          "<Texteinblendung 1>",
          "<Texteinblendung 2>"
        ]
      },
      "yt-short-2": {
        "title": "<Titel>",
        "description": "<kurze Beschreibung>",
        "overlays": [
          "<Texteinblendung 1>",
          "<Texteinblendung 2>"
        ]
      }
    }
  }
}

Musikalische Bestandteile (x-t1-song, x-t2-youtube, youtube) bleiben leer, wenn kein Song vorhanden ist. Erfinde keine Instrumentierung, Stimmlage oder Klangfarbe.
