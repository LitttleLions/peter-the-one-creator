# Gesendeter Prompt 027

- Zeitstempel: 20260817-210807
- Provider: openrouter
- Modell: deepseek/deepseek-v4-flash
- Stil: stil-05-sachbuch
- Kapitel: 027
- Szene: 01
- Chunk: 02/02
- Temperatur: 0.4
- max_tokens: 12000
- System-Zeichen: 2695
- User-Zeichen: 4915

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

The prevalence of myopia, the unsatisfactoriness of all explanations of its origin, and the futility of all methods of prevention, have led some writers of repute to the conclusion that the elongated eyeball is a natural physiological adaptation to the needs of civilization. Against this view two unanswerable arguments can be brought. One is that the myopic eye does not see so well even at the near point as the normal eye, and the other that the defect tends to progression with very serious results, often ending in blindness. If Nature has attempted to adapt the eye to civilized conditions by an elongation of the globe, she has done it in a very clumsy manner. It is true that many authorities assume the existence of two kinds of myopia, one physiological, or at least harmless, and the other pathological; but since it is impossible to say with certainty whether a given case is going to progress or not, this distinction, even if it were correct, would be more important theoretically than practically.

Into such a slough of despond and contradiction have the misdirected labors of a hundred years led us ! But in the light of truth the problem turns out to be a very simple one. In view of the facts given in Chapters V and IX, it is easy to understand why all previous attempts to prevent myopia have failed. All these attempts have aimed at lessening the strain of near work upon the eye, leaving the strain to see distant objects unaffected, and totally ignoring 4 the mental strain which underlies the optical one. There are many differences between the conditions to which the children of primitive man were subjected, and those under which the offspring of civilized races spend their developing years, besides the mere fact that the latter learn things out of books and write things on paper, and the former did not. In the process of education civilized children are shut up for hours every day within four walls, in the charge of teachers who are too often nervous and irritable. They. are even compelled to remain for long periods in the same position. The things they are required to learn may be presented in such a way as to be excessively uninteresting; and they are under a continual compulsion to think of the gaining of marks and prizes rather than the acquisition of knowledge for its own sake. Some children endure these unnatural conditions better than others. Many cannot stand the strain, and thus the schools become the hotbed, not only of myopia, but of all other errors of refraction.

A satisfactory explanation of the mechanism by which near work produces myopia has not yet been given. - Tscherning: Physiologic Optics, p. 86
It is not yet determined how near work changes the longitudinal structure of the eye. - Eversbusch: The Diseases of Children, vol. vii, p. 291.

The Hygiene of the Eye in Schools, p 127.

School Hygiene, System of Diseases of the Eye, vol. ii, p. 361.

American Encyclopedia and Dictionary of Ophthalmology, edited by Wood, 1913-1919, vol. xi, p. 8271.

Lawson: Brit. Med. Jour., June 18, 1898.

It seems to have been amply demonstrated, by the studies of Motais, Steiger, Miss Barrington, and Karl Pearson, that errors of refraction are inherited. And while the use of the eyes for near work is probably a secondary cause, determining largely the development of the defects it is not the primary cause. - Cyclopedia of Education, edited by Monroe, 1911-1913.

Fox (quoted by Risley): System of Diseases of the Eye, vol. ii, p. 357.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
