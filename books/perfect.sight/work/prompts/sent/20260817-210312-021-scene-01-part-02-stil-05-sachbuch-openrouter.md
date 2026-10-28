# Gesendeter Prompt 021

- Zeitstempel: 20260817-210312
- Provider: openrouter
- Modell: deepseek/deepseek-v4-flash
- Stil: stil-05-sachbuch
- Kapitel: 021
- Szene: 01
- Chunk: 02/03
- Temperatur: 0.4
- max_tokens: 12000
- System-Zeichen: 2695
- User-Zeichen: 10207

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

It has been shown that when the eyes strain to see at the near-point the focus is always pushed farther away than it was before, in one or all meridians; and by means of simultaneous retinoscopy it can always be demonstrated that when a person with presbyopia tries to read fine print and fails, the focus is always pushed farther away than it was before the attempt was made, indicating that the failure was caused by strain. Even the thought of making such an effort will produce strain, so that the refraction may be changed, and pain, discomfort and fatigue produced, before the fine print is regarded. Furthermore, when a person with presbyopia rests the eyes by closing them, or palming, he always becomes able, for a few moments at least, to read fine print at six inches, again indicating that his previous failure was due, not to any fault of the eyes, but to a strain to see. When the strain is permanently relieved the presbyopia is permanently cured, and this has happened, not in a few cases, but in many, and at all ages, up to sixty, seventy and eighty.

The first patient that I cured of presbyopia was myself. Having demonstrated by means of experiments on the eyes of animals that the lens is not a factor in accommodation, I knew that presbyopia must be curable, and I realized that I could not look for any very general acceptance of the revolutionary conclusions I had reached so long as I wore glasses myself for a condition supposed to be due to the loss of the accommodative power of the lens. I was then suffering from the maximum degree of presbyopia. I had no accommodative power whatever, and had to have quite an outfit of glasses, because with a glass, for instance, which enabled me to read fine print at thirteen inches, I could not read it either at twelve inches or at fourteen. The retinoscope showed that when I tried to see anything at the near-point without glasses my eyes were focussed for the distance, and when I tried to see anything at the distance they were focussed for the near-point. My problem, then, was to find some way of reversing this condition and inducing my eyes to focus for the point I wished to see at the moment that I wished to see it. I consulted various eye specialists, but my language was to them like that of St. Paul to the Greeks, namely, foolishness. "Your lens is as hard as a stone," they said. "No one can do anything for you." Then I went to a nerve specialist. He used the retinoscope on me, and confirmed my own observations as to the peculiar contrariness of my accommodation; but he had no idea what I could do about it. He would consult some of his colleagues, he said, and asked me to come back in a month, which I did. Then he told me he had come to the conclusion that there was only one man who could cure me, and that was Dr. William H. Bates of New York.

"Why do you say that?" I asked.

"Because you are the only man who seems to know anything about it," he answered.

Thus thrown upon my own resources, I was fortunate enough to find a non-medical gentleman who was willing to do what he could to assist me, the Rev. R. B. B. Foote, of Brooklyn. He kindly used the retinoscope through many long and tedious hours while I studied my own case, and tried to find some way of accommodating when I wanted to read, instead of when I wanted to see something at the distance. One day, while looking at a picture of the Rock of Gibraltar which hung on the wall, I noted some black spots on its face. I imagined that these spots were the openings of caves, and that there were people in these caves moving about. When I did this my eyes were focussed for the reading distance. Then I looked at the same picture at the reading distance, still imagining that the spots were caves with people in them. The retinoscope showed that I had accommodated, and I was able to read the lettering beside the picture. I had, in fact, been temporarily cured by the use of my imagination. Later I found that when I imagined the letters black I was able to see them black, and when I saw them black I was able to distinguish their form. My progress after this was not what could be called rapid. It was six months before I could read the newspapers with any kind of comfort, and a year before I obtained my present accommodative range of fourteen inches, from four inches to eighteen; but the experience was extremely valuable, for I had in pronounced form every symptom subsequently observed in other presbyopic patients.

Fortunately for the patients, it has seldom taken me as long to cure other people as it did to cure myself. In some cases a complete and permanent cure was effected in a few minutes. Why, I do not know. I will never be satisfied till I find out. A patient who had worn glasses for presbyopia for about twenty years was cured in less than fifteen minutes by the use of his imagination.

When asked to read diamond type, he said he could not do so, because the letters were grey and looked all alike. I reminded him that the type was printer's ink and that there was nothing blacker than printer's ink. I asked him if he had ever seen printer's ink. He replied that he had. Did he remember how black it was? Yes. Did he believe that these letters were as black as the ink he remembered? He did, and then he read the letters; and because the improvement in his vision was permanent, he said that I had hypnotized him.

In another case a presbyope of ten years' standing was cured just as quickly by the same method. When reminded that the letters which he could not read were black, he replied that he knew they were black, but that they looked grey.

"If you know they are black, and yet see them grey," I said, "you must imagine them grey. Suppose you imagine that they are black. Can you do that ?"

"Yes," he said, "I can imagine that they are black"; and then he proceeded to read them.

These extremely quick cures are rare. In nine cases out of ten progress has been much slower, and it has been necessary to resort to all the methods of obtaining relaxation found useful in the treatment of other errors of refraction. In the more difficult cases of presbyopia the patients often suffer from the same illusions of color, size, form and number, when they try to read fine print, as do patients with hypermetropia, astigmatism, and myopia when they try to read the letters on the Snellen test card at the distance. They are unable to remember or imagine, when trying to see at the near-point, even such a simple thing as a small black spot, but can remember it perfectly when they do not try to see. Their sight for the distance is often very imperfect and always below normal, although they may have thought it perfect; and just as in the case of other errors of refraction, improvement of the distant vision improves the vision at the near-point. Regardless, however, of the difficulty of the case and the age of the patient; some improvement has always been obtained, and if the treatment was continued long enough, the patient has been cured.

The idea that presbyopia is "a normal result of growing old" is responsible for much defective eyesight. When people who have reached the presbyopic age experience difficulty in reading, they are very likely to resort at once to glasses, either with or without professional advice. In some cases such persons may be actually presbyopic; in others the difficulty may be something temporary, which they would have thought little about if they had been younger, and which would have passed away if Nature had been left to herself. But once the glasses are adopted, in the great majority of cases, they produce the condition they were designed to relieve, or, if it already existed, they make it worse, sometimes very rapidly, as every ophthalmologist knows. In a couple of weeks sometimes, the patient finds, as noted in the chapter on What Glasses Do to Us, that the large print which he could read without difficulty before he got his glasses, can no longer be read without their aid. In from five to ten years the accommodative power of the eye is usually gone; and if from this point the patient does not go on to cataract, glaucoma, or inflammation of the retina, he may consider himself fortunate. Only occasionally do the eyes refuse to submit to the artificial conditions imposed upon them; but in such cases they may keep up an astonishing struggle against them for long periods. A woman of seventy, who had worn glasses for twenty years, was still able to read diamond type and had good vision for the distance without them. She said the glasses tired her eyes and blurred her vision, but that she had persisted in wearing them, in spite of a continual temptation to throw them off, because she had been told that it was necessary for her to do so.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
