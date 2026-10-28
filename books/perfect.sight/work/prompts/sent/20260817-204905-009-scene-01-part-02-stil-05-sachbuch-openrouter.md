# Gesendeter Prompt 009

- Zeitstempel: 20260817-204905
- Provider: openrouter
- Modell: deepseek/deepseek-v4-flash
- Stil: stil-05-sachbuch
- Kapitel: 009
- Szene: 01
- Chunk: 02/02
- Temperatur: 0.4
- max_tokens: 12000
- System-Zeichen: 2695
- User-Zeichen: 7054

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

It has been demonstrated, however, that the lens is not a factor, either in the production of accommodation, or in the correction of errors of refraction. Therefore under no circumstances can there be a strain of the ciliary muscle to be relieved. It has also been demonstrated that when the vision is normal no error of refraction is present, and the extrinsic muscles of the eyeball are at rest. Therefore there can be no strain of the extrinsic muscles to be relieved in these cases. When a strain of these muscles does exist, glasses may correct its effects upon the refraction, but the strain itself they cannot relieve. On the contrary, as has been shown, they must make it worse. Nevertheless persons with normal vision who wear glasses for the relief of a supposed muscular strain are often benefited by them. This is a striking illustration of the effect of mental suggestion, and plane glass, if it could inspire the same faith, would produce the same result. In fact, many patients have told me that they had been relieved of various discomforts by glasses which I found to be simply plane glass. One of these patients was an optician who had fitted the glasses himself and was under no illusions whatever about them; yet he assured me that when he didn't wear them he got headaches.

Some patients are so responsive to mental suggestion that you can relieve their discomfort, or improve their sight, with almost any glasses you like to put on them. I have seen people with hypermetropia wearing myopic glasses with a great deal of comfort, and people with no astigmatism getting much satisfaction from glasses designed for the correction of this defect.

Landolt mentions the case of a patient who had for years worn prisms for insufficiency of the internal recti, and who found them absolutely indispensable for work, although the apices were toward the nose. The prescription, which the patient was able to produce, called for prisms adjusted in the usual manner, with the apices toward the temples; but the optician had made a mistake which, owing to the patient's satisfaction with the result, had never been discovered. Landolt explained the case by "the slight effect of weak prisms and the great power of imagination"; and doubtless the benefit derived from the glasses was real, resulting from the patient's great faith in the specialist - described as "one of the most competent of ophthalmologists" - who prescribed them.

Some patients will even imagine that they see better with glasses that markedly lower the vision. A number of years ago a patient for whom I had prescribed glasses consulted an ophthalmologist whose reputation was much greater than my own, and who gave him another pair of glasses and spoke slightingly of the ones that I had prescribed. The patient returned to me and told me how much better he could see with the second pair of glasses than he did with the first. I tested his vision with the new glasses, and found that while mine had given him a vision of 20/20 those of my colleague enabled him to see only 20/40. The simple fact was that he had been hypnotized by a great reputation into thinking he could see better when he actually saw worse; and it was hard to convince him that he was wrong, although he had to admit that when he looked at the test card he could see only half as much with the new glasses as with the old ones.

When glasses do not relieve headaches and other nervous symptoms it is assumed to be because they were not properly fitted, and some practitioners and their patients exhibit an astounding degree of patience and perseverance in their joint attempts to arrive at the proper prescription. A patient who suffered from severe pains at the base of his brain was fitted sixty times by one specialist alone, and had besides visited many other eye and nerve specialists in this country and in Europe. He was relieved of the pain in five minutes by the methods presented in this book, while his vision, at the same time, became temporarily normal.

It is fortunate that many people for whom glasses have been prescribed refuse to wear them, thus escaping not only much discomfort but much injury to their eyes. Others, having less independence of mind, or a larger share of the martyr's spirit, or having been more badly frightened by the oculists, submit to an amount of unnecessary torture which is scarcely conceivable. One such patient wore glasses for twenty-five years, although they did not prevent her from suffering continual misery and lowered her vision to such an extent that she had to look over the tops when she wanted to see anything at a distance. Her oculist assured her that she might expect the most serious consequences if she did not wear the glasses, and was very severe about her practice of looking over instead of through them.

As refractive abnormalities are continually changing, not only from day to day and from hour to hour, but from minute to minute, even under the influence of atropine, the accurate fitting of glasses is, of course; impossible. In some cases these fluctuations are so extreme, or the patient so unresponsive to mental suggestion, that no relief whatever is obtained from correcting lenses, which necessarily become under such circumstances an added discomfort. At their best it cannot be maintained that glasses are anything more than a very unsatisfactory substitute for normal vision.

Archiv. f. Augenh., vol. lxxix, 1915, translated in Arch. Ophth., vol. xlv, No. 6, 1916.

Lancaster: Wearing Glasses, p. 15.

Anomalies of the Motor Apparatus of the Eye, System of Diseases of the Eye, vol. iv, pp. 154-155.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
