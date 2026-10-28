# Gesendeter Prompt 005

- Zeitstempel: 20260817-201754
- Provider: openrouter
- Modell: deepseek/deepseek-v4-flash
- Stil: stil-05-sachbuch
- Kapitel: 005
- Szene: 01
- Chunk: 02/03
- Temperatur: 0.4
- max_tokens: 12000
- System-Zeichen: 2695
- User-Zeichen: 10388

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

It should be emphasized that in order to paralyze either the recti muscles, or the obliques, it was found necessary to inject the atropine far back behind the eyeball with a hypodermic needle. This drug is supposed to paralyze the accommodation when dropped into the eyes of human beings or animals, but in all of my experiments it was found that when used in this way it had very little effect upon the power of the eye to change its focus.
Fig. 17.
No. 1. - Production of mixed astigmatism in the eye of a carp by pulling strings attached to the conjunctiva in opposite directions. Note the oval shape of the front of the eyeball.
No. 2. - With the cutting of the strings the eyeball returns to its normal shape, and the refraction becomes normal.
Fig. 18. Demonstration Upon the Eyeball of a Rabbit That the Obliques Lengthen the Visual Axis in Myopia
R, rest. The eyeball is of normal length and emmetropic - that is, perfectly adjusted for distant vision. My, myopia. The pull of the oblique muscles has been strengthened by advancement and the retinoscope shows that myopia has been produced. It can easily be noted that the eyeball is longer. It was impossible to avoid some movement of the head between the taking of the two pictures as a result of the manipulation of the strings, but the rule shows that the focus of the camera was not appreciably changed by such movements.

Astigmatism was usually produced in combination with myopic or hypermetropic refraction. It was also produced by various manipulations of both the oblique and recti muscles. Mixed astigmatism, which is a combination of myopic with hypermetropic refraction, was always produced by traction on the insertion of the superior or inferior rectus in a direction parallel to the plane of the iris, so long as both obliques were present and active; but if either or both of the obliques had been cut, the myopic part of the astigmatism disappeared. Similarly after the superior or the inferior rectus had been cut the hypermetropic part of the astigmatism disappeared. Advancement of the two obliques, with advancement of the superior and inferior recti, always produced mixed astigmatism.
Fig. 19. Demonstration Upon the Eye of a Carp That the Recti Shorten the Visual Axis in Hypermetropia
R, rest. The eyeball is of normal length and emmetropic. Hy, hypermetropia. The pull of the external and internal recti has been strengthened by advancement, and the retinoscope shows that hypermetropia has been produced. It may easily be noted that the eyeball is shorter. The rule shows that the focus of the camera was not appreciably changed between the taking of the two pictures.

Eyes from which the lens had been removed, or in which it had been pushed out of the axis of vision, responded to electrical stimulation precisely as did the normal eye, so long as the muscles were active; but when they had been paralyzed by the injection of atropine deep into the orbit, electrical stimulation had no effect on the refraction.
Fig. 20. Lens Pushed Out of the Axis of Vision
In this experiment on the eye of a carp the lens was pushed out of the axis of vision. Accommodation took place after this displacement just as it did before. Note the point of the knife in the pupil in front of the lens.

In one experiment the lens was removed from the right eye of a rabbit, the refraction of each eye having first been tested by retinoscopy and found to be normal. The wound was then allowed to heal. Thereafter, for a period extending from one month to two years, electrical stimulation always produced accommodation in the lensless eye precisely to the same extent as in the eye which had a lens. The same experiment with the same result was performed on a number of other rabbits, on dogs and on fish. The obvious conclusion is that the lens is not a factor in accommodation.
Fig. 21. Rabbit With Lens Removed
The animal was exhibited at a meeting of the Ophthalmological Section of the American Medical Association, held in Atlantic City, and was examined by a number of ophthalmologists present, all of whom testified that electrical stimulation of the eyeball produced accommodation, or myopic refraction, precisely as in the normal eye.

In most text-books on physiology it is stated that accommodation is controlled by the third cranial nerve, which supplies all the muscles of the eyeball except the superior oblique and the external rectus; but the fourth cranial nerve, which supplies only the superior oblique, was found in these experiments to be just as much a nerve of accommodation as the third. When either the third or the fourth nerve was stimulated with electricity near its point of origin in the brain accommodation always resulted in the normal eye. When the origin of either nerve was covered with a small wad of cotton soaked in a two per cent solution of atropine sulphate in a normal salt solution, stimulation of that nerve produced no accommodation, while stimulation of the unparalyzed nerve did produce it. When the origin of both nerves was covered with cotton soaked in atropine, accommodation could not be produced by electrical stimulation of either or both. When the cotton was removed and the nerves washed with normal salt solution, electrical stimulation of either or both produced accommodation just as before the atropine had been applied. This experiment, which was performed repeatedly for more than an hour by alternately applying and removing the atropine, not only demonstrated clearly what had not been known before, namely, that the fourth nerve is a nerve of accommodation, but also demonstrated that the superior oblique muscle which is supplied by it is an important factor in accommodation. It was further found that when the action of the oblique muscles was prevented by dividing them, the stimulation of the third nerve produced, not accommodation, but hypermetropia.
Fig. 22. Experiment Upon the Eye of a Cat Demonstrating That the Fourth Nerve, Which Supplies Only the Superior Oblique Muscle, Is Just as Much a Nerve of Accommodation As the Third, and That the Superior Oblique Muscle Which It Supplies Is a Muscle of Accommodation.
No. 1. - Both nerves have been exposed near their origin in the brain, and a strip of black paper has been inserted beneath each to render it visible. The fourth nerve is the smaller one The superior oblique muscle has been advanced by a tucking operation, as this muscle is always rudimentary in cats, and unless its pull is strengthened accommodation cannot be produced in these animals. Stimulation of either or both nerves by the faradic current produced accommodation.
No. 2. - When the fourth nerve was covered with cotton soaked in a normal salt solution, the application of the faradic current to the cotton produced accommodation. When the cotton was soaked in a one per cent solution of atropine sulphate in a normal salt solution, such application produced no accommodation, but stimulation of the third nerve did produce it.
No. 3. When the third nerve was covered with cotton soaked in a normal salt solution, the application of the faradic current to the cotton produced accommodation. When the cotton was soaked with atropine sulphate in a normal salt solution, such application produced no accommodation, but the stimulation of the fourth nerve did produce it.
No. 4. - When both nerves were covered with cotton soaked in atropine sulphate in a normal salt solution, the application of electricity to the cotton produced no accommodation. When the parts had been washed with a warm salt solution electrical stimulation of either nerve always produced accommodation. The nerves were alternately covered with the atropine-soaked cotton and then washed with the warm saline solution for an hour the electricity being applied in each condition with invariably the same result. Accommodation could never be produced by electrical stimulation when the nerves were paralyzed with the atropine, but always resulted from the stimulation of either or both when they had been washed with the salt solution. The experiment was performed with the same results on many rabbits and dogs.
Fig. 23. Pithing a Fish Preparatory to Operating Upon Its Eyes
The object of this operation is to secure greater relaxation of the muscles of the eyes and head, which would work for hours, without external stimulus, if the brain cells were not destroyed by the probe.

In all the experiments all sources of error are believed to have been eliminated. They were all repeated many times and always with the same result. They seemed, therefore, to leave no room for doubt that neither the lens nor any muscle inside the eyeball has anything to do with accommodation, but that the process whereby the eye adjusts itself for vision at different distances is entirely controlled by the action of the muscles on the outside of the globe.

The refractive system.

On the Anomalies of Accommodation and Refraction of the Eye, p. 22.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
