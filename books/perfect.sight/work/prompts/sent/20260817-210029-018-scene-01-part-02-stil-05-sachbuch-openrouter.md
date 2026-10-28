# Gesendeter Prompt 018

- Zeitstempel: 20260817-210029
- Provider: openrouter
- Modell: deepseek/deepseek-v4-flash
- Stil: stil-05-sachbuch
- Kapitel: 018
- Szene: 01
- Chunk: 02/02
- Temperatur: 0.4
- max_tokens: 12000
- System-Zeichen: 2695
- User-Zeichen: 5275

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

Persons who wish to preserve their eyesight are frequently warned not to read in moving vehicles; but since under modern conditions of life many persons have to spend a large part of their time in moving vehicles, and many of them have no other time to read, it is useless to expect that they will ever discontinue the practice. Fortunately the theory of its injuriousness is not borne out by the facts. When the object regarded is moved more or less rapidly, strain and lowered vision are, at first, always produced; but this is always temporary, and ultimately the vision is improved by the practice.
Seven Truths of Normal Sight
1 - Normal Sight can always be demonstrated in the normal eye, but only under favorable conditions.
2 - Central Fixation: The letter or part of the letter regarded is always seen best.
3 - Shifting: The point regarded changes rapidly and continuously.
4 - Swinging: When the shifting is slow, the letters appear to move from side to side or in other directions with a pendulum-like motion.
5 - Memory is perfect The color and background of the letters, or other objects seen are remembered perfectly, instantaneously and continuously
6 - Imagination is good. One may even see the white part of the letters whiter than it really is, while the black is not altered by distance, illumination, size, or form, of the letters.
7 - Rest or relaxation of the eye and mind is perfect and can always be demonstrated.
When one of these seven fundamentals is perfect all are perfect.
Fig. 49. Specimen of Diamond Type
Many patients have been greatly benefited by reading type of this size.
Fig. 50. Photographic Type Reduction
Patients who can read photographic type reductions are instantly relieved of pain and discomfort when they do so and those who cannot read such type may be benefited simply by looking at it.

There is probably no visual habit against which we have been more persistently warned than that of reading in a recumbent posture. Many plausible reasons have been adduced for its supposed injuriousness; but so delightful is the practice that few, probably, have ever been deterred from it by fear of the consequences. It is gratifying to be able to state, therefore, that I have found these consequences to be beneficial rather than injurious. As in the case of the use of the eyes under other difficult conditions, it is a good thing to be able to read lying down, and the ability to do it improves with practice. In an upright position, with a good light coming over the left shoulder, one can read with the eyes under a considerable degree of strain; but in a recumbent posture, with the light and the angle of the page to the eye unfavorable, one cannot read unless one relaxes. Anyone who can read lying down without discomfort is not likely to have any difficulty in reading under ordinary conditions.

The fact is that vision under difficult conditions is good mental training. The mind may be disturbed at first by the unfavorable environment; but after it has become accustomed to such environments, the mental control, and, consequently, the eyesight are improved. To advise against using the eyes under unfavorable conditions is like telling a person who has been in bed for a few weeks and finds it difficult to walk to refrain from such exercise. Of course, discretion must be used in both cases.

But just as the invalid may gradually increase his strength until the Marathon has no terrors for him, so may the eye with defective sight be educated until all the rules with which we have so long allowed ourselves to be harassed in the name of "eye hygiene" may be disregarded, not only with safety but with benefit.

School Hygiene, Brief Course Series in Education, edited by Monroe, 1916, p. 240

Seventh Annual Report to the Maine State Board of Health, by the
secretary, Dr. A. G. Young, 1891, p. 193.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
