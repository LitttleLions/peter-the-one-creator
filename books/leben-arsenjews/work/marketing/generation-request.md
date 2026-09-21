# Arbeitsanweisung: Marketingtexte fuer Das Leben Arsenjews

Ziel: die Datei

```text
books/leben-arsenjews/work/marketing/generated.json
```

befuellen. Struktur: `texts` (Beitrags-IDs) und `youtube`. Kopfdaten:

```json
{
  "schema_version": 1,
  "book_id": "leben-arsenjews",
  "style": "stil-02-poetisch",
  "generator": "workspace_ai",
  "model": "<Modellname der bearbeitenden KI>",
  "generated_at": "<ISO 8601>",
  "prompt_version": "marketing-1",
  "source_hash": "ac618e42dc46b8f3",
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

- Buch-ID: leben-arsenjews
- Titel: Das Leben Arsenjews
- Untertitel: Ein russischer Erinnerungsroman in neuer deutscher Ausgabe
- Autor: Iwan Bunin
- Originaltitel: Жизнь Арсеньева
- Originalautor: Iwan Bunin (Iwan Alexejewitsch Bunin, 1870–1953)
- Uebersetzung/Einrichtung: Motivatier Classics (Übersetzung und editorische Einrichtung)
- Herausgeber: Motivatier Stiftung
- Sprache: de
- Marke: Motivatier Classics

Kurzbeschreibung:
Iwan Bunins „Das Leben Arsenjews“ ist ein Erinnerungsroman über Kindheit, Jugend, Liebe, Herkunft und den Verlust einer vergangenen Welt. Diese neue deutsche Ausgabe wurde nach dem russischen gemeinfreien Original erstellt, KI-gestützt übersetzt und redaktionell geprüft.

Ausfuehrliche Inhaltsbeschreibung:
„Das Leben Arsenjews“ ist ein Roman der Erinnerung. Aus der Rückschau entsteht das Bild einer Kindheit und Jugend in der russischen Provinz, geprägt von Landschaften, Familienbindungen, ersten Erschütterungen, literarischem Erwachen und der allmählichen Erfahrung von Vergänglichkeit.

Bunin erzählt nicht in der Form einer äußeren Chronik, sondern aus der Bewegung des Bewusstseins. Gerüche, Licht, Jahreszeiten, Räume, Stimmen und einzelne Begegnungen werden zu Trägern einer inneren Geschichte. Das Vergangene erscheint dabei nicht als bloßer Besitz der Erinnerung, sondern als etwas Unwiederbringliches, das gerade im Erzählen seine schmerzliche Gegenwart behält.

Der Roman gehört zu den zentralen Prosawerken Bunins. In ihm verbindet sich die Genauigkeit realistischer Beobachtung mit einer elegischen, konzentrierten Sprache. „Das Leben Arsenjews“ ist ein Buch über Herkunft und Verlust, über Jugend und erstes Begehren, aber auch über die Frage, was von einem Leben bleibt, wenn die Welt, aus der es hervorgegangen ist, unwiderruflich verschwunden ist.

Zum Autor:
Iwan Bunin, geboren 1870 in Woronesch und gestorben 1953 in Paris, war ein russischer Schriftsteller, Dichter und Erzähler. Er stammte aus einer verarmten Adelsfamilie und wurde früh durch die Landschaften, Lebensformen und sozialen Umbrüche des alten Russland geprägt. Nach der Revolution verließ er Russland und lebte im Exil, vor allem in Frankreich.

Bunin gilt als einer der großen Stilisten der russischen Prosa. Zu seinen wichtigen Werken gehören Erzählungen und Romane wie „Das Dorf“, „Der Herr aus San Francisco“, „Mitjas Liebe“, „Dunkle Alleen“ und „Das Leben Arsenjews“. 1933 erhielt er als erster russischer Autor den Literaturnobelpreis.

„Жизнь Арсеньева" nimmt in Bunins Werk eine besondere Stellung ein. Der Roman ist keine einfache Autobiographie, sondern eine literarisch geformte Erinnerung an Jugend, Herkunft, Liebe und den Verlust einer historischen Welt. Gerade dadurch wurde er zu einem der bedeutenden russischen Prosawerke des Exils.

Belegte Editionsangaben:
- Originaltitel: Жизнь Арсеньева
- Originalautor: Iwan Bunin (Iwan Alexejewitsch Bunin, 1870–1953)
- Russische Vorlage: Жизнь Арсеньева
- Diese Ausgabe ist eine neue deutsche Ausgabe nach dem russischen gemeinfreien Original.
- Die Übersetzung und editorische Einrichtung wurden KI-gestützt erstellt und redaktionell geprüft.
- Bei diesem Werk wurde auf die vollständige russische Originalfassung und eine konsistente Kapitel- und Buchstruktur geachtet.
- Kurze Vorspänne, Motti oder Orientierungstexte vor den Kapiteln stammen nicht aus dem Original, sofern solche in dieser Ausgabe verwendet werden.
- Herausgegeben von der Motivatier Stiftung

Namensglossar (Schreibweise verbindlich):
- Иван Бунин -> Iwan Bunin
- Арсеньев -> Arsenjew
- Лика -> Lika
- Жизнь Арсеньева -> Das Leben Arsenjews

Echte Leseprobe aus der fertigen deutschen Ausgabe:
(Quelle: Kapitel 001, Szene 1)

"Ich wurde vor einem halben Jahrhundert geboren, im mittleren Russland, auf dem Dorf, im väterlichen Gutshof. Wir haben kein Gefühl für unseren Anfang und unser Ende. Und es ist sehr schade, dass man mir gesagt hat, wann genau ich geboren wurde."

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
