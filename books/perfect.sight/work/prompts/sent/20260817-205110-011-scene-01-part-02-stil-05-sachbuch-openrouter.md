# Gesendeter Prompt 011

- Zeitstempel: 20260817-205110
- Provider: openrouter
- Modell: deepseek/deepseek-v4-flash
- Stil: stil-05-sachbuch
- Kapitel: 011
- Szene: 01
- Chunk: 02/02
- Temperatur: 0.4
- max_tokens: 12000
- System-Zeichen: 2695
- User-Zeichen: 5945

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

So sensitive is this test that if the subject, whether his vision is ordinarily normal or not, pronounces the initials of his name correctly while looking at a blank surface without trying to see, there will be no error of refraction; but if he miscalls one initial, even without any consciousness of effort, and with full knowledge that he is deceiving no one, myopia will be produced.

Mental strain may produce many different kinds of eyestrain. According to the statement of most authorities there is only one kind of eyestrain, an indefinite thing resulting from so-called overuse of the eyes, or an effort to overcome a wrong shape of the eyeball. It can be demonstrated, however, that there is not only a different strain for each different error of refraction, but a different strain for most abnormal conditions of the eye. The strain that produces an error of refraction is not the same as the strain that produces a squint, or a cataract, or glaucoma, or amblyopia, or inflammation of the conjunctiva or of the margin of the lids, or disease of the optic nerve or retina. All these conditions may exist with only a slight error of refraction, and while the relief of one strain usually means the relief of any others that may coexist with it, it sometimes happens that the strain associated with such conditions as cataract and glaucoma is relieved without the complete relief of the strain that causes the error of refraction. Even the pain that so often accompanies errors of refraction is never caused by the same strain that causes these errors. Some myopes cannot read without pain or discomfort, but most of them suffer no inconvenience. When the hypermetrope regards an object at the distance the hypermetropia is lessened, but pain and discomfort may be increased. While there are many strains, however, there is only one cure for all of them. namely, relaxation.

The health of the eye depends upon the blood, and, circulation is very largely influenced by thought. When thought is normal - that is, not attended by any excitement or strain - the circulation in the brain is normal, the supply of blood to the optic nerve and the visual centers is normal, and the vision is perfect. When thought is abnormal the circulation is disturbed, the supply of blood to the optic nerve and visual centers is altered, and the vision lowered. We can consciously think thoughts which disturb the circulation and lower the visual power; we can also consciously think thoughts that will restore normal circulation, and thereby cure, not only all errors of refraction, but many other abnormal conditions of the eyes. We cannot by any amount of effort make ourselves see, but by learning to control our thoughts we can accomplish that end indirectly.

You can teach people how to produce any error of refraction, how to produce a squint, how to see two images of an object, one above another, or side by side, or at any desired angle from one another, simply by teaching them how to think in a particular way. When the disturbing thought is replaced by one that relaxes, the squint disappears, the double vision and the errors of refraction are corrected; and this is as true of abnormalities of long standing as of those produced voluntarily. No matter what their degree or their duration their cure is accomplished just as soon as the patient is able to secure mental control. The cause of any error of refraction, of a squint, or of any other functional disturbance of the eye, is simply a thought - a wrong thought - and the cure is as quick as the thought that relaxes. In a fraction of a second the highest degrees of refractive error may be corrected, a squint may disappear, or the blindness of amblyopia may be relieved. If the relaxation is only momentary, the correction is momentary. When it becomes permanent, the correction is permanent.

This relaxation cannot, however, be obtained by any sort of effort. It is fundamental that patients should understand this; for so long as they think, consciously or unconsciously, that relief from strain may be obtained by another strain their cure will be delayed.

In this case and others to be mentioned later, the large letter at the top of the card read by the eye with normal vision at two hundred feet, was a "C."

An opacity of the lens

A condition in which the eyeball becomes abnormally hard

condition in which there is a decline of vision without apparent cause

membrane covering the inner surface of the eyelid and the visible
part of the white of the eye.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
