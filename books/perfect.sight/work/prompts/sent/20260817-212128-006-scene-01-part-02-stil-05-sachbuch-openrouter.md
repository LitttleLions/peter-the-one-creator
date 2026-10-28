# Gesendeter Prompt 006

- Zeitstempel: 20260817-212128
- Provider: openrouter
- Modell: deepseek/deepseek-v4-flash
- Stil: stil-05-sachbuch
- Kapitel: 006
- Szene: 01
- Chunk: 02/03
- Temperatur: 0.4
- max_tokens: 12000
- System-Zeichen: 2695
- User-Zeichen: 9331

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

With some adjustments of the light multiple images were seen reflected from the front of the lens. Sometimes these images were arranged in a horizontal line, sometimes in a vertical one and sometimes at angles of different degrees, while their distance from each other also varied. Usually there were three of them; sometimes there were more; and sometimes there were only two. Occasionally they were all of the same size, but usually they varied, there being apparently no limit to their possibilities of change in this and other respects. Some of them were photographed, indicating that they were real reflections. Changes in the distance of the diaphragm from the light and from the condenser, and alterations in the size and shape of its opening, appeared to make no difference. Different adjustments of the condenser were equally without effect. Changes in the angle at which the light was adjusted sometimes lessened the number of images and sometimes increased them, until at last an angle was found at which but one image was seen. The images appear, in fact, to have been caused by reflections from the globe of the electric light.

Even after the light had been so adjusted as to eliminate reflections it was often difficult, or impossible, to get a clear and distinct image of the electric filament upon the front of the lens. One could rearrange the condenser and the diaphragm and change the axis of fixation, and still the image would be clouded or obscured and its outline distorted. The cause of the difficulty appeared to be that the light was not adjusted at the best angle for the purpose and it was not always possible to determine the exact axis at which a clear, distinct image would be produced. As in the case of the reflections from the sides of the globe, it seemed to vary without a known cause. This was true, however: that there were angles of the axis of the globe which gave better images than others, and that what these angles were could not be determined with exactness. I have labored with the light for two or three hours without finding the right angle. At other times the axis would remain unchanged for days, giving always a clear, distinct image.
Fig. 29. Image of Electric Filament on the Front of the Sclera
R, rest; A, accommodation. During accommodation the front of the sclera becomes more convex, because the eyeball has elongated, just as a camera is elongated when it is focussed upon a near object. The spot of light on the cornea is an accidental reflection.

The results of these experiments confirmed the conclusions drawn from the previous ones, namely, that accommodation is due to a lengthening of the eyeball, and not to a change in the curvature of the lens. They also confirmed, in a striking manner, my earlier conclusions as to the conditions under which myopia and hypermetropia are produced.

The images photographed from the front of the lens did not show any change in size or form during accommodation. The image on the back of the lens also remained unchanged, as observed through the telescope of the ophthalmometer; but as there is no dispute about its behavior during accommodation, it was not photographed. Images photographed from the iris before and during accommodation were also the same in size and form, as was to be expected from the character of the lens images. If the lens changed during accommodation, the iris, which rests upon it, would change also.
Fig. 30. Images on the Side of the Sclera
R, rest; A, accommodation. The image in A is the larger, indicating a flattening of the side of the sclera as the eyeball elongates. My, Myopia. The eye is straining to see at the distance and the image is larger, indicating that the eyeball has elongated, resulting in a flattening of the side of the sclera. Hy, Hypermetropia. The eye is straining to see at two inches. The image is the smallest of the series, indicating that the eyeball has become shorter than in any of the other pictures, and the side of the sclera more convex. The two lower pictures confirm the author's previous observations that farsight is produced when the eye strains to see near objects and nearsight when it strains to see distant objects.
Fig. 31. Multiple Images Upon the Front of the Lens
This picture illustrates one of the difficulties that had to be overcome in photographing images reflected from various parts of the eyeball. Unless the light was adjusted at precisely the right angle the filament was multiplied by reflection from the sides of the globe. Usually the image was doubled, sometimes it was tripled, as shown in the picture, and sometimes it was quadrupled. Often days of labor were required to eliminate these reflections, and for reasons that were not definitely determined the same adjustment did not always give the same results Sometimes all would go well for days, and then, without any apparent reason, the multiple images would return.

The images photographed from the cornea and from the front and side of the sclera showed, however, a series of four well-marked changes, according to whether the vision was normal or accompanied by a strain. During accommodation the images from the cornea were smaller than when the eye was at rest, indicating elongation of the eyeball and a consequent increase in the convexity of the cornea. But when an unsuccessful effort was made to see at the near-point, the image became larger, indicating that the cornea had become less convex, a condition which one would expect when the optic axis was shortened, as in hypermetropia. When a strain was made to see at a distance the image was smaller than when the eye was at rest, again indicating elongation of the eyeball and increased convexity of the cornea.

The images photographed from the front of the sclera showed the same series of changes as the corneal images, but those obtained from the side of the sclera were found to have changed in exactly the opposite manner, being larger where the former were smaller and vice versa, a difference which one would naturally expect from the fact that when the front of the sclera becomes more convex the sides must become flatter.
Fig. 32. Reflection of the Electric Filament From the Iris
This picture is shown to illustrate the fact that it is possible to get a reflection from any reflecting surface of the eyeball without reflections from the other parts, although these may be exposed. This is done by changing the angle of the light to the eye. In No. 1 observations of the eye at the time the picture was taken demonstrated that the image was from the iris, not from the cornea, and the fact is also apparent in the picture. (Compare the image with the corneal reflection in Fig. 28.) In No. 2, where the image overlaps the margin of the pupil, the fact that the reflection is from the iris is manifest from the circumstance that only part of the filament is seen. If it were from the cornea, the whole of it would be reflected. Note in this picture that there is no reflection from the lens. The images on the iris did not change their size or shape during accommodation, demonstrating again that the lens, upon which the iris rests, does not change its shape when the eye adjusts itself for near vision.

When an effort was made to see at a distance the image reflected from the side of the sclera was larger than the image obtained when the eye was at rest, indicating that this part of the sclera had become less convex or flatter, because of elongation of the eyeball. The image obtained during normal accommodation was also larger than when the eye was at rest, indicating again a flattening of the side of the sclera. The image obtained, however, when an effort was made to see near was much smaller than any of the other images, indicating that the sclera had become more convex at the side, a condition which one would expect when the eyeball was shortened, as in hypermetropia.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
