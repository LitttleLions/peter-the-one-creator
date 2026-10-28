# Gesendeter Prompt 022

- Zeitstempel: 20260817-210424
- Provider: openrouter
- Modell: deepseek/deepseek-v4-flash
- Stil: stil-05-sachbuch
- Kapitel: 022
- Szene: 01
- Chunk: 02/02
- Temperatur: 0.4
- max_tokens: 12000
- System-Zeichen: 2695
- User-Zeichen: 3634

## System

Du bist ein literarischer Uebersetzer. Du uebersetzt aus der Ausgangssprache ins Deutsche.

---
Buch: Perfect Sight Without Glasses (William Horatio Bates, M.D. (1860–1931))
Sprache: en -> de

### Verbindliches Style-Profil

Das folgende Profil enthaelt verbindliche Stil- und Rekonstruktionsregeln fuer diesen Lauf (stil-05-sachbuch). Die globalen Ausgabe-Regeln und das im Arbeitsauftrag uebermittelte Glossar haben bei Konflikten Vorrang.

Übersetze den englischen Ausgangstext als präzises, ruhiges historisches Sachbuch.

Bewahre vollständig die Argumentation, Reihenfolge, Absätze, Beispiele, Fallberichte,
Zitate, Zahlen, Tabellenhinweise, Verweise und historischen medizinischen Behauptungen.
Fasse nichts zusammen und füge keine modernen medizinischen Erklärungen hinzu.

Verwende ein klares, fachlich lesbares Deutsch. Keine literarische Ausschmückung,
keine werbliche Sprache, keine Dramatisierung und keine erfundenen Zwischenüberschriften.
Modernisiere Bates’ medizinische Auffassungen nicht stillschweigend und korrigiere sie
nicht im Übersetzungstext. Die historische Perspektive muss erkennbar bleiben.

Halte die Terminologie aus dem Buch-Glossar konsistent. Besonders wichtig sind
„Anspannung“ für „strain“, „zentrale Fixation“ für „central fixation“,
„Akkommodation“ für „accommodation“ und „Refraktion“ für „refraction“.
Myopie, Hypermetropie/Hyperopie, Astigmatismus, Presbyopie, Amblyopie und Netzhaut
werden als etablierte deutsche Fachbegriffe verwendet.

Bei historischen Methodenbezeichnungen darf der englische Ausdruck bei der ersten
Verwendung in Klammern erhalten bleiben, wenn dies die begriffliche Orientierung
verbessert; danach bleibt die gewählte deutsche Form konsistent.

Erhalte die Unterscheidung zwischen Bates’ eigener Stimme, zitierten Autoritäten,
Patientenbriefen und Fallberichten. Verändere keine medizinischen Zahlen, Namen,
Quellenangaben oder Versuchsbedingungen. OCR- oder Quellenfehler dürfen nicht erfunden
oder kreativ geglättet werden; bei einem unklaren Ausgangstext bleibe möglichst nah am
vorliegenden Text.

Gib ausschließlich die Übersetzung aus. Keine Vorbemerkung, keine Analyse und keine
Kommentare außerhalb des übersetzten Textes.

### Harte Ausgabe-Regeln

Diese Regeln haben Vorrang vor widersprechenden Angaben im Style-Profil.

- Gib nur die Uebersetzung aus.
- Keine Vorbemerkung, keine Zusammenfassung, keine Analyse.
- Keine Saetze wie 'Hier ist die Uebersetzung'.
- Keine Markdown-Ueberschriften, Vorabsaetze, Lede, Prologe oder sonstige Struktur-Ergaenzungen erfinden, ausser sie stehen bereits im Quelltext.
- Inhalt, Reihenfolge und Fakten des Quelltexts bleiben erhalten; nichts ergaenzen, das nicht im Quelltext steht.

## User

Uebersetze den folgenden Text ins Deutsche.

### Buch
- Titel: Perfect Sight Without Glasses
- Autor: William Horatio Bates, M.D. (1860–1931)
- Stil: stil-05-sachbuch
- Style-Profil: books\perfect.sight\styles\stil-05-sachbuch.md
- Das Style-Profil steht im System-Prompt und ist verbindlich.

### Verbindliche Namen und Begriffe

Nutze diese Schreibweisen, wenn die genannten Personen oder Begriffe im Quelltext vorkommen. Nicht aufgefuehrte Personen-, Stammes-, Orts- und Titelnamen werden konservativ transliteriert oder im Zweifel in der erkennbaren Quellform beibehalten.
- strain -> Anspannung
- central fixation -> zentrale Fixation
- accommodation -> Akkommodation
- refraction -> Refraktion
- myopia -> Myopie
- hypermetropia -> Hypermetropie
- hyperopia -> Hyperopie
- astigmatism -> Astigmatismus
- presbyopia -> Presbyopie
- amblyopia -> Amblyopie
- squint -> Schielen
- palming -> Palming (Abdecken der Augen mit den Händen)
- shifting -> Shifting (Verschieben des Blicks)
- sunning -> Sunning (Sonnenübung)
- retina -> Netzhaut
- optic nerve -> Sehnerv

### Zu uebersetzender Text

Interne Arbeitsportion 2/2 derselben Szene. Uebersetze nur diesen Abschnitt fortlaufend ins Deutsche. Keine neue Szenenueberschrift erzeugen.

All the theories heretofore suggested fail to explain the foregoing facts; but it is a fact that in all cases of squint a strain can be demonstrated, and that the relief of the strain is in all cases followed by the cure of the squint, as well as of the amblyopia and the error of refraction. It is also a fact that all persons with normal eyes can produce squint by a strain to see. It is not a difficult thing to do, and many children derive much amusement from the practice, while it gives their elders unnecessary concern, for fear the temporary squint may become permanent. To produce convergent squint is comparatively easy. Children usually do it by straining to see the end of the nose. The production of divergent squint is more difficulty, but with practice persons with normal eyes become able to turn out either eye, or both, at will. They also become able to turn either eye upward and inward, or upward and outward, at any desired angle. Any kind of squint can, in fact, be produced at will by the appropriate kind of strain. Some persons retain the power to produce voluntary squint more or less permanently. Others quickly lose it if they do not keep in practice. There is usually a lowering of the vision when voluntary squint is produced, and accepted methods of measuring the strength of the muscles seem to show deficiencies corresponding to the nature of the squint.

The result obtained by the operation is, as a rule, simply cosmetic. The sight of the squinting eye is not influenced by the operation, and in only a few instances is even binocular vision restored. - Fuchs: Text-Book of Ophthalmology, p. 795.

The result of even the most successful squint operation, in long-standing strabismus, is merely cosmetic in the vast majority of cases. - Eversbusch: The Diseases of Children, edited by Pfaunder and Schlossman. English translation by Shaw and La Fetra, second edition, 1912-1914, vol. vii, p. 316.

Text-Book of Ophthalmology, p. 633.

Cases have been reported, some surely authentic, in which an amblyopic squinting eye has acquired good vision, either through correction of the refraction, or because loss of sight in the good eye has compelled the use of the amblyopic eye. - Ibid.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
