# Prompt: Metadaten für »Aelita« von Alexei Tolstoi erstellen

Du bist literarischer Redakteur und bereitest Metadaten für eine lokale
Übersetzungs- und EPUB-Werkbank vor. Die Werkbank übersetzt das russische
Original maschinell (KI-gestützt) ins Deutsche und erzeugt daraus DOCX, EPUB
und PDF für eine neue deutsche Ausgabe in der Reihe **Motivatier Classics**
(Herausgeber: Motivatier Hermann Stiftung).

Erstelle für das folgende Buch eine kompakte, gut nutzbare
Metadaten-Zusammenstellung. Formuliere eigenständig und übernimm keine
Klappentexte, Shoptexte, Verlagsbeschreibungen oder Wikipedia-Passagen
wortgleich.

## Buch

- **Titel:** Aelita (deutsch: Aëlita)
- **Originaltitel:** Аэлита (Untertitel: Закат Марса – »Sonnenuntergang des Mars«)
- **Autor:** Alexei Nikolajewitsch Tolstoi (Алексей Николаевич Толстой, 1883–1945)
- **Quellsprache:** Russisch
- **Zielsprache:** Deutsch
- **Erscheinungszeit / literarische Epoche:** 1922–1923 (Erstveröffentlichung); 1937–1939 (überarbeitete Fassung); frühe sowjetische Science-Fiction, zugleich Abenteuer- und Liebesroman
- **Genre / Form:** Roman (Science-Fiction, planetarische Romanze, frühe sowjetische Phantastik)

### Publikationsgeschichte (Hintergrundwissen)

- Erstveröffentlichung: »Аэлита : Закат Марса«, Zeitschrift *Красная новь*, 1922, № 6 und 1923, № 2
- Erste Buchausgabe: »Аэлита (Закат Марса)«, ГИЗ, Moskau–Petrograd, 1923
- Verwendete Textgrundlagen:
  - А. Н. Толстой. Собрание сочинений в десяти томах. Том 3. Аэлита. Повести и рассказы 1917—1924 — Москва: Гослитиздат, 1958
  - Сборник А. Толстого »Гиперболоид инженера Гарина. — Аэлита«, Советский писатель, Ленинград, 1939
- Wichtig: Der ursprüngliche Text von 1922–1923 wurde vom Autor später **wesentlich überarbeitet** (substantielle Umarbeitung). Die hier vorliegende EPUB-Quelle folgt vermutlich einer späteren Fassung.

### Inhaltlicher Kontext

*Aelita* ist Alexei Tolstois erster Science-Fiction-Roman und einer der
Gründungstexte der sowjetischen Weltraumliteratur. Der Ingenieur Los und der
Rotarmist Gussew fliegen mit einem selbstgebauten Raumschiff zum Mars, wo sie
auf eine uralte, im Niedergang begriffene Zivilisation stoßen. Los verliebt
sich in Aelita, die Tochter des herrschenden Ingenieursrats, und wird in
einen Aufstand der marsianischen Arbeiterklasse hineingezogen. Der Roman
verbindet technische Utopie, Revolutionsromantik, exotische Abenteuer und
eine melancholische Liebesgeschichte. Prägend ist das Spannungsverhältnis
zwischen Fortschrittsglaube und Dekadenzbewusstsein: Der Mars erscheint als
sterbende Welt, die zugleich Spiegel und Warnung für die Erde ist.

---

## Gewünschtes Ergebnis

Bitte liefere die Antwort in genau dieser Struktur (YAML). Halte dich strikt
an die Feldnamen und die angegebenen Formate. Die mit `>` eingeleiteten Felder
sind mehrzeilige YAML-Blöcke (Literal Block Scalar mit `>-`).

```yaml
title: ""
subtitle: ""
author: ""
translator: "Motivatier Classics"
translator_label: "Übersetzung und editorische Einrichtung"
language: "de-DE"
original_language: "ru"
genre: ""
period: ""
short_description: >-
  Ein kurzer, sachlicher Ein-Satz-Text für Übersichten.
summary: >-
  Eine gut lesbare Zusammenfassung für die EPUB-Frontmatter. 2–4 Absätze,
  literarisch, aber nicht werblich. Keine Spoilerwarnungen, keine Stichpunkte.
  Erwähne die planetarische Romanze, die Mars-Zivilisation, die
  Revolutionsallegorie und die melancholische Grundstimmung.
author_bio: >-
  Kurzbiografie des Autors. 2–3 Absätze. Geburts- und Sterbedaten (1883–1945),
  wichtigste Werke (»Peter der Erste«, »Der Leidensweg«, »Aelita«, »Der
  Hyperboloid des Ingenieurs Garin«, »Das goldene Schlüsselchen«),
  literarische Bedeutung (vom Symbolismus zum sozialistischen Realismus,
  Meister des historischen Romans, Pionier der sowjetischen Science-Fiction),
  Bezug zum vorliegenden Buch.
original_title: ""
original_author: ""
source_title: ""
source_author: ""
source_translator: "Keine; Grundlage ist der russische Originaltext."
source_note: >-
  Kurzer Hinweis zur Textgrundlage (Publikationsgeschichte, Überarbeitung
  durch den Autor). Etwa: »Der ursprüngliche Text von 1922–1923 wurde vom
  Autor später wesentlich überarbeitet. Die vorliegende Ausgabe folgt dem Text
  der Gesamtausgabe von 1958 bzw. der Sammelausgabe von 1939.«
keywords:
  - ""
  - ""
title_page_extra:
  - "Originaltitel: Аэлита"
  - "Originalautor: Alexei Nikolajewitsch Tolstoi (1883–1945)"
  - "Russische Vorlage: Аэлита (Закат Марса)"
  - "Diese Ausgabe ist eine neue deutsche Ausgabe nach dem russischen gemeinfreien Original."
  - "Die Übersetzung und editorische Einrichtung wurden KI-gestützt erstellt und redaktionell geprüft."
  - "Kurze Vorspänne, Motti oder Orientierungstexte vor den Kapiteln stammen nicht aus dem Original, sofern solche in dieser Ausgabe verwendet werden."
  - "Herausgegeben von der Motivatier Hermann Stiftung"
imprint_text: |
  Aelita

  Alexei Nikolajewitsch Tolstoi

  [HIER DEN UNTERTITEL EINFÜGEN, z.B.: »Ein Mars-Roman in neuer deutscher Ausgabe«]

  Originaltitel: Аэлита (Закат Марса)
  Originalautor: Alexei Nikolajewitsch Tolstoi (1883–1945)
  Quellensprache: Russisch

  [HIER DEN QUELLENHINWEIS EINFÜGEN]

  Diese Ausgabe ist eine neue deutsche Ausgabe nach dem russischen gemeinfreien Original. Die Übersetzung und editorische Einrichtung wurden KI-gestützt erstellt und redaktionell geprüft.

  Die kurzen Vorspänne, Motti oder Orientierungstexte vor den Kapiteln stammen nicht aus dem Original. Sie wurden für diese Ausgabe ergänzt, um historische, atmosphärische und erzählerische Orientierung zu geben.

  Herausgegeben von der Motivatier Hermann Stiftung
  Übersetzung und editorische Einrichtung: Motivatier Classics

  © 2026 Motivatier Hermann Stiftung für diese deutsche Übersetzung, editorische Einrichtung, Zusatztexte, Satz und Covergestaltung.

  Das zugrunde liegende Werk und die verwendete gemeinfreie Originalvorlage sind gemeinfrei. Rechte an dieser Ausgabe bestehen, soweit sie die neue deutsche Übersetzung, die redaktionellen Ergänzungen, die Gestaltung, das Cover und die konkrete Einrichtung des Textes betreffen.

  Alle Rechte an dieser Ausgabe vorbehalten.
publisher: "Motivatier Hermann Stiftung"
rights: "© 2026 Motivatier Hermann Stiftung für diese deutsche Übersetzung, editorische Einrichtung, Zusatztexte, Satz und Covergestaltung."
recommended_structure:
  mode: ""            # "scenes" wenn Kapitel in Szenen zerlegt werden sollen; "chapter_as_scene" wenn jedes Kapitel eine Arbeitseinheit ist
  note: "Aelita hat keine klassische Kapitelstruktur mit Глава N, sondern ist in Abschnitte/Teile gegliedert. Bitte analysiere die Struktur und schlage den passenden Modus vor."
  groups:             # optionale Teile/Bände – leer lassen wenn nicht bekannt
    - id: ""
      label: ""
      from: ""
      to: ""
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
illustration_setting: |
  [HIER EIN VISUAL-IDENTITY-PROMPT FÜR HIGGSFIELD/ILLUSTRATIONEN:]
  Beschreibe den visuellen Stil für Kapitel- und Szenenbilder. Aelita spielt
  teils im nachrevolutionären Russland (Petrograd, 1920er Jahre), teils auf
  dem Mars (rote Wüsten, Kanäle, uralte turmartige Städte, exotische
  Architektur einer sterbenden Hochkultur). Mischung aus früher
  Science-Fiction-Ästhetik, Art déco, kosmischer Weite und Melancholie.
  Farbpalette vorschlagen (Marsrot, Ocker, Violett, Nachthimmel, technisches
  Grau).
name_seed:
  - source: "Аэлита"
    target: "Aelita"
    type: "person"
    status: "confirmed"
    note: "Titelfigur; im Deutschen mit Trema (Aëlita) oder ohne – bitte konsistent angeben"
  - source: "Лось"
    target: "Los"
    type: "person"
    status: "draft"
    note: "Mstislaw Sergejewitsch Los, Ingenieur, Protagonist"
  - source: "Гусев"
    target: "Gussew"
    type: "person"
    status: "draft"
    note: "Alexei Iwanowitsch Gussew, Rotarmist, Begleiter von Los"
  - source: "Тускуб"
    target: "Tuskub"
    type: "person"
    status: "draft"
    note: "Herrscher des Mars, Vater Aelitas"
  - source: "Марс"
    target: "Mars"
    type: "place"
    status: "confirmed"
    note: ""
  - source: ""
    target: ""
    type: ""
    status: "draft"
    note: ""
```

## Besondere Anforderungen an diesen Prompt

1. **Untertitel:** Schlage einen deutschen Untertitel vor, der den Charakter
   des Romans trifft – planetarische Romanze, frühe Science-Fiction, Mars-Epos.
   Beispiel aus dem Bestand: »Ein historischer Roman von Glaubenswahn,
   Leidenschaft und Dämonie in neuer deutscher Ausgabe« (Feuriger Engel).

2. **Namensliste:** Ergänze die angefangene `name_seed`-Liste um alle
   relevanten Personen-, Orts- und Begriffnamen aus dem Roman (Marsianer,
   russische Figuren, technische/gesellschaftliche Begriffe). Transliteriere
   konservativ nach Duden-Standard. Format wie vorgegeben: `source`
   (Kyrillisch), `target` (deutsche Form), `type` (person/place/term),
   `status` (draft), `note` (kurze Erklärung).

3. **Illustration Setting:** Formuliere einen kompakten, englischsprachigen
   Visual-Identity-Prompt für den KI-Bildgenerator (Higgsfield). Beschreibe
   die zwei visuellen Welten (Erde 1920er / Mars), den gewünschten
   Illustrationsstil, Lichtstimmung und eine konkrete Farbpalette.
   Orientiere dich an den bestehenden `illustration_setting`-Blöcken in
   den anderen Buchpaketen (z.B. Pharao, Feuriger Engel, Leben Arsenjews).

4. **Quellenhinweis:** Formuliere einen präzisen, sachlichen Hinweis zur
   Textgrundlage, der die doppelte Überlieferung (Erstfassung 1922–23 /
   Überarbeitung 1937–39) erwähnt. Dieser kommt sowohl in `source_note` als
   auch im `imprint_text` vor.

5. **Strukturvorschlag:** *Aelita* hat keine klassische »Глава N«-Struktur
   wie andere russische Romane. Der Roman gliedert sich in größere Abschnitte
   (oft als »Teil 1 / Teil 2« o.ä. bezeichnet). Analysiere die typische
   Gliederung und schlage `recommended_structure.mode` sowie ggf. `groups`
   vor. Wenn du die genaue Kapitelzahl nicht kennst, gib eine fundierte
   Schätzung ab und kennzeichne sie als `draft`.

6. **Cover-Farbe:** Schlage eine `cover.background`-Farbe (Hex) und
   `cover.foreground`-Farbe vor, die zum Mars-Motiv und zur Stimmung des
   Romans passt. Beispiele aus anderen Büchern: Peter I = `#f59e0b` (Gold),
   Feuriger Engel = `#8b0000` (Dunkelrot).

## Stil der Ausgabe

- Deutsch.
- Klar, ruhig, literarisch.
- Keine Superlative ohne Grund.
- Keine direkte Übernahme fremder Texte (Wikipedia, Klappentexte, Verlagsseiten).
- Bei unsicheren Angaben `draft` oder kurze Notiz setzen.
- Namen in einer für deutsche Leser stabilen und wiedererkennbaren Form
  vorschlagen (Duden-Transliteration).
- Die wiederkehrenden Motivatier-Bausteine (© 2026, Motivatier Hermann
  Stiftung, Motivatier Classics, KI-gestützte Übersetzung) sind
  bereits vorgegeben und sollen unverändert übernommen werden.