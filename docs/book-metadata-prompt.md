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
- Quellsprache:
- Zielsprache:
- Erscheinungszeit / literarische Epoche:
- Genre / Form:

## Gewuenschtes Ergebnis

Bitte liefere die Antwort in genau dieser Struktur:

```yaml
title: ""
subtitle: ""
author: ""
translator: "Motivatier"
language: "de-DE"
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
`recommended_structure.groups`-Liste mit `label`, `from` und `to` vor.
