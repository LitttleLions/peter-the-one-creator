# Gesendeter Prompt 016

- Zeitstempel: 20260817-205711
- Provider: openrouter
- Modell: deepseek/deepseek-v4-flash
- Stil: stil-05-sachbuch
- Kapitel: 016
- Szene: 01
- Chunk: 03/03
- Temperatur: 0.4
- max_tokens: 12000
- System-Zeichen: 2695
- User-Zeichen: 5451

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

Interne Arbeitsportion 3/3 derselben Szene. Uebersetze nur diesen Abschnitt fortlaufend ins Deutsche. Keine neue Szenenueberschrift erzeugen.

When the vision is imperfect it often happens that, when the patient looks at a small letter, some of the larger letters on the upper lines, or the big C at the top, look blacker than the letter regarded. This makes it impossible to see the smaller letters perfectly. To correct this eccentric fixation regard the letter which is seen best, and shift to the smaller letter. If successful, the small letter, after a few movements, will appear blacker than the larger one. If not successful after a few trials, rest the eyes by closing and palming, and try again. One may also shift from the large letter to a point some distance below the small letter, gradually approaching the latter as the vision improves.

*No. 7 -

Shifting from a card at three or five feet to one at ten or twenty feet often proves helpful, as the unconscious
memory of the letter seen at the near-point helps to bring out the one at the distance.

Different people will find these various methods of shifting more or less satisfactory. If any method does not succeed, it should be abandoned after one or two trials and something else tried. It is a mistake to continue the practice of any method which does not yield prompt results. The cause of the failure is strain, and it does no good to continue the strain.

When it is not possible to practice with the Snellen test card, other objects may be utilized. One can shift, for instance, from one window of a distant building to another, or from one part of a window to another part of the same window, from one auto to another, or from one part of an auto to another part, producing, in each case, the illusion that the objects are moving in a direction contrary to the movement of the eye. When talking to people, one can shift from one person to another, or from one part of the face to another part. When reading a book, or newspaper, one can shift consciously from one word or letter to another, or from one part of a letter to another.

Shifting and swinging, as they give the patient something definite to do, are often more successful than other methods of obtaining relaxation, and in some cases remarkable results have been obtained simply by demonstrating to the patient that staring lowers the vision and shifting improves it. One patient, a girl of sixteen with progressive myopia, obtained very prompt relief by shifting. She came to the office wearing a pair of glasses tinted a pale yellow, with shades at the sides; and in spite of this protection she was so annoyed by the light that her eyes were almost closed, and she had great difficulty in finding her way about the room. Her vision without glasses was 3/200. All reading had been forbidden, playing the piano from the notes was not allowed, and she had been obliged to give up the idea of going to college. The sensitiveness to light was relieved in a few minutes by focussing the light of the sun upon the upper part of the eyeball when she looked far down, by means of a burning glass (see Chapter XVII). The patient was then seated before a Snellen test card and directed to look away from it, rest her eyes, and then look at the big C. For a fraction of a second her vision was improved, and by frequent demonstrations she was made to realize that any effort to see the letters always lowered the vision. By alternately looking away, and then looking back at the letters for a fraction of a second, her vision improved so rapidly that in the course of half an hour it was almost normal for the distance. Then diamond type was given her to read. The attempt to read it at once brought on a severe pain. She was directed to proceed as she had in reading the Snellen test card; and in a few minutes, by alternately looking away and then looking at the first letter of each word in turn, she became able to read without fatigue, discomfort, or pain. She left the office without her glasses, and was able to see her way without difficulty. Other patients have been benefited as promptly by this simple method.

Double and multiple vision.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
