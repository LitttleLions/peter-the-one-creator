# Prompt: Buchmetadaten Fuer Die Werkbank Erstellen

Du bist literarischer Redakteur und bereitest Metadaten fuer eine lokale
Uebersetzungs- und EPUB-Werkbank vor.

Erstelle fuer das folgende Buch eine kompakte, gut nutzbare Metadaten-Zusammenstellung.
Formuliere eigenstaendig und uebernimm keine Klappentexte, Shoptexte,
Verlagsbeschreibungen oder Wikipedia-Passagen wortgleich.

## Buch

  - Titel:
  - Originaltitel, falls bekannt:
  - Autor:
  - Übersetzer / Herausgeber (Standard: "Motivatier"):
  - Quellsprache:
  - Zielsprache:
  - Erscheinungszeit / literarische Epoche:
  - Genre / Form:

## Gewuenschtes Ergebnis

Bitte liefere die Antwort in genau dieser Struktur. Die `front_matter`-Konfiguration
ist essentiell fuer den EPUB-Export: `combined_epub_front_matter: false` sorgt dafuer,
dass Titelseite, Zusammenfassung, Leben des Autors und Impressum als getrennte Seiten
mit eigenem Seitenumbruch erscheinen – nicht als eine einzige Sammelseite.


```yaml
title: ""
subtitle: ""
author: ""
translator: "Motivatier"
translator_label: "Übersetzung und editorische Einrichtung"
language: "de-DE"
publisher: "Motivatier Hermann Stiftung"
rights: >-
  © YYYY Motivatier Hermann Stiftung für diese deutsche Übersetzung,
  editorische Einrichtung, Zusatztexte und Covergestaltung.
original_language: ""
genre: ""
period: ""
short_description: >-
  Ein kurzer, sachlicher Ein-Satz-Text fuer Uebersichten.
summary: >-
  Eine gut lesbare Zusammenfassung fuer die EPUB-Frontmatter. 2-4 Absaetze,
  literarisch, aber nicht werblich. Keine Spoilerwarnungen, keine Stichpunkte.
author_bio: >-
  Kurzbiografie des Autors oder der Autorin. 1-3 Absaetze. Geburts- und
  Sterbedaten, wichtigste Werke, literarische Bedeutung, Bezug zum vorliegenden
  Buch.
title_page_extra:
  - "Originaltitel: ..."
  - "Originalautor: ... (YYYY–YYYY)"
  - >-
    Diese Ausgabe ist eine neue deutsche Übersetzung aus dem [Sprache]
    Original. Die Übersetzung und editorische Einrichtung wurden KI-gestützt
    erstellt und redaktionell geprüft.
  - "Herausgegeben von der Motivatier Hermann Stiftung"
imprint_text: |
  [Titel des Buches]

  [Autor]

  [Untertitel]

  Originaltitel: ...
  Originalautor: ... (YYYY–YYYY)

  Diese Ausgabe ist eine neue deutsche Übersetzung aus dem [Sprache] Original. Die Übersetzung und editorische Einrichtung wurden KI-gestützt erstellt und redaktionell geprüft.

  Herausgegeben von der Motivatier Hermann Stiftung
  Übersetzung und editorische Einrichtung: Motivatier

  © YYYY Motivatier Hermann Stiftung für diese deutsche Übersetzung, editorische Einrichtung, Zusatztexte und Covergestaltung.

  Das [Sprache] Originalwerk ist gemeinfrei. Rechte an dieser Ausgabe bestehen, soweit sie die neue deutsche Übersetzung, die redaktionellen Ergänzungen, die Gestaltung, das Cover und die konkrete Einrichtung des Textes betreffen.

  Alle Rechte an dieser Ausgabe vorbehalten.
keywords:
  - ""
  - ""
recommended_structure:
  mode: "scenes"
  note: "scenes fuer Kapitel mit Szenen; chapter_as_scene fuer viele kurze Kapitel."
recommended_display:
  chapters:
    format: "words_de"
    suffix: " Kapitel"
    align: "center"
    include_source_title: false
  scenes:
    show: false
    format: "number"
    align: "center"
    page_break: false
    separator: ""
name_seed:
  - source: ""
    target: ""
    type: "person"
    status: "draft"
    note: ""
```

## Stil Der Ausgabe

- Deutsch.
- Klar, ruhig, literarisch.
- Keine Superlative ohne Grund.
- Keine direkte Uebernahme fremder Texte.
- Bei unsicheren Angaben `draft` oder kurze Notiz setzen.
- Namen in einer fuer deutsche Leser stabilen Form vorschlagen.

## Zusatz

Wenn das Werk aus Teilen, Baenden oder Binnenbuechern besteht, schlage eine
`recommended_structure.groups`-Liste mit `label`, `from` und `to` vor
(fuer fortlaufende Kapitelbereiche) oder mit `label` und `chapters`
(fuer explizite Kapitellisten, z. B. wenn ein Band mehrere nicht
zusammenhängende Kapitel umfasst). Beispiel:

```yaml
recommended_structure:
  groups:
    - id: einleitung
      label: "Einleitung"
      chapters: [0]
    - id: erstes-buch
      label: "Erstes Buch"
      from: "001"
      to: "007"
    - id: zweites-buch
      label: "Zweites Buch"
      chapters: [8, 9, 10]
```

Bei `chapter_as_scene` und Kapiteln mit Nullen in der ID (z. B. `000`
fuer Prolog) funktionieren `from`/`to`-Bereiche wegen String-Vergleich
nicht zuverlaessig – hier immer `chapters`-Listen verwenden.
