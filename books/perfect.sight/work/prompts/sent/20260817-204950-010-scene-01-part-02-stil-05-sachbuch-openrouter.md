# Gesendeter Prompt 010

- Zeitstempel: 20260817-204950
- Provider: openrouter
- Modell: deepseek/deepseek-v4-flash
- Stil: stil-05-sachbuch
- Kapitel: 010
- Szene: 01
- Chunk: 02/03
- Temperatur: 0.4
- max_tokens: 12000
- System-Zeichen: 2695
- User-Zeichen: 10261

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

Interne Arbeitsportion 2/3 derselben Szene. Uebersetze nur diesen Abschnitt fortlaufend ins Deutsche. Keine neue Szenenueberschrift erzeugen.

Primarily the strain to see is a strain of the mind, and, as in all cases in which there is a strain of the mind, there is a loss of mental control. Anatomically the results of straining to see at a distance may be the same as those of regarding an object at the near point without strain; but in one case the eye does what the mind desires, and in the other it does not.

These facts appear sufficiently to explain why visual acuity declines as civilization advances. Under the conditions of civilized life men's minds are under a continual strain. They have more things to worry them than uncivilized man had, and they are not obliged to keep cool and collected in order that they may see and do other things upon which existence depends. If he allowed himself to get nervous, primitive man was promptly eliminated; but civilized man survives and transmits his mental characteristics to posterity. The lower animals when subjected to civilized conditions respond to them in precisely the same way as do human creatures. I have examined many domestic and menagerie animals, and have found them, in many cases, myopic, although they neither read, nor write, nor sew, nor set type.
Fig. 39. A Family Group Strikingly Illustrating the Effect of the Mind Upon the Vision
No. 1. - Girl of four with normal eyes. No. 2. - The child's mother with myopia. No. 3. - The same girl at nine with myopia. Note that her expression has completely changed, and is now exactly like her mother's. Nos. 4, 5 and 6. - The girl's brother at two, six and eight. His eyes are normal in all three pictures. The girl has either inherited her mother's disposition to take things hard, or has been injuriously effected by her personality of strain. The boy has escaped both influences. In view of the prevailing theories about the relation of heredity to myopia, this picture is particularly interesting.

A decline in visual acuity at the distance, however, is no more a peculiarity of civilization than is a similar decline at the near-point. Myopes, although they see better at the near-point than they do at the distance, never see as well as does the eye with normal sight; and in hypermetropia, which is more common than myopia, the sight is worse at the near-point than at the distance.
Fig. 40. Myopes Who Never Went to School, or Read in the Subway
No. 1. - Myopic elephant in the Central Park Zoo, New York thirtynine years old. Young elephants and other young animals were found to have normal vision.
No. 2. - Cape buffalo with myopia, Central Park Zoo.
No. 3. - Myopic monkey, also in the Central Park Zoo.
No. 4. - Pet dog with myopia which progressed from year to year.

The remedy is not to avoid either near work or distant vision, but to get rid of the mental strain which underlies the imperfect functioning of the eye at both points; and it has: been demonstrated in thousands of cases that this can always be done.

Fortunately, all persons are able to relax under certain conditions at will. In all uncomplicated errors of refraction the strain to see can be relieved, temporarily, by having the patient look at a blank wall without trying to see. -To secure permanent relaxation sometimes requires considerable time and much ingenuity. The same method cannot be used with everyone. The ways in which people strain to see are infinite, and the methods used to relieve the strain must be almost equally varied. Whatever the method that brings most relief, however, the end is always the same, namely relaxation. By constant repetition and frequent demonstration and by all means possible, the fact must be impressed upon the patient that perfect sight can be obtained only by relaxation. Nothing else matters.

Most people, when told that rest, or relaxation, will cure their eye troubles, ask why sleep does not do so. The answer to this question was given in Chapter VII. The eyes are rarely, if ever, completely relaxed in sleep, and if they are under a strain when the subject is awake, that strain will certainly be continued during sleep, to a greater or less degree, just as a strain of other parts of the body is continued.

The idea that it rests the eyes not to use them is also erroneous. The eyes were made to see with, and if when they are open they do not see, it is because they are under such a strain and have such a great error of refraction that they cannot see. Near vision, although accomplished by a muscular act, is no more a strain on them than is distant vision, although accomplished without the intervention of the muscles. The use of the muscles does not necessarily produce fatigue. Some men can run for hours without becoming tired. Many birds support themselves upon one foot during sleep, the toes tightly clasping the swaying bough and the muscles remaining unfatigued by the apparent strain. Fabre tells of an insect which hung back downward for ten months from the roof of its wire cage, and in that position performed all the functions of life, even to mating and laying its eggs. Those who fear the effect of civilization, with its numerous demands for near vision, upon the eye may take courage from the example of this marvelous little animal which, in a state of nature, hangs by its feet only at intervals, but in captivity can do it for ten months on end, the whole of its life's span, apparently without inconvenience or fatigue.

The fact is that when the mind is at rest nothing can tire the eyes, and when the mind is under a strain nothing can rest them. Anything that rests the mind will benefit the eyes. Almost everyone has observed that the eyes tire less quickly when reading an interesting book than when perusing something tiresome or difficult to comprehend. A schoolboy can sit up all night reading a novel without even thinking of his eyes, but if he tried to sit up all night studying his lessons he would soon find them getting very tired. A child whose vision was ordinarily so acute that she could see the moons of Jupiter with the naked eye became myopic when asked to do a sum in mental arithmetic, mathematics being a subject which was extremely distasteful to her. Sometimes the conditions which produce mental relaxation are very curious. One patient, for instance, was able to correct her error of refraction when she looked at the test card with her body bent over at an angle of about forty-five degrees, and the relaxation continued after she had assumed the upright position. Although the position was an unfavorable one, she had somehow got the idea that it improved her sight, and therefore it did so.

The time required to effect a permanent cure varies greatly with different individuals. In some cases five, ten, or fifteen minutes is sufficient, and I believe the time is coming when it will be possible to cure everyone quickly. It is only a question of accumulating more facts, and presenting these facts in such a way that the patient can grasp them quickly. At present, however, it is often necessary to continue the treatment for weeks and months, although the error of refraction may be no greater nor of longer duration than in those cases that are cured quickly. In most cases, too, the treatment must be continued for a few minutes every day to prevent relapse. Because a familiar object tends to relax the strain to see, the daily reading of the Snellen test card is usually sufficient for this purpose. It is also useful, particularly when the vision at the near-point is imperfect, to read fine print every day as close to the eyes as it can be done. When a cure is complete it is always permanent; but complete cures, which mean the attainment, not of what is ordinarily called normal sight, but of a measure of telescopic and microscopic vision, are very rare. Even in these cases, too, the treatment can be continued with benefit; for it is impossible to place limits to the visual powers of man, and no matter how good the sight, it is always possible to improve it. Daily practice of the art of vision is also necessary to prevent those visual lapses to which every eye is liable, no matter how good its sight may ordinarily be. It is true that no system of training will provide an absolute safeguard against such lapses in all circumstances; but the daily reading of small distant, familiar letters will do much to lessen the tendency to strain when disturbing circumstances arise, and all persons upon whose eyesight the safety of others depends should be required to do this.
Fig. 41. - One of Many Thousands of Patients Cured of Errors of Refraction by the Methods Presented in This Book
No. 1. - Man of thirty-six, 1902, wearing glasses for myopia. Note the appearance of effort in his eyes. He was relieved in 1904 by means of exercises in distant vision and obtained normal sight without glasses.
No. 2. - The same man five years later. No relapse.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
