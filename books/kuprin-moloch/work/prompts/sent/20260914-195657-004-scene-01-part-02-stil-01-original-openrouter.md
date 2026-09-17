# Gesendeter Prompt 004

- Zeitstempel: 20260914-195657
- Provider: openrouter
- Modell: deepseek/deepseek-v4.1-flash
- Stil: stil-01-original
- Kapitel: 004
- Szene: 01
- Chunk: 02/02
- Temperatur: 0.2
- max_tokens: 12000
- System-Zeichen: 5037
- User-Zeichen: 3302

## System

Du bist ein literarischer Uebersetzer. Du uebersetzt aus der Ausgangssprache ins Deutsche.

---
Buch: Der Moloch (Alexander Iwanowitsch Kuprin)
Sprache: ru -> de

### Verbindliches Style-Profil

Das folgende Profil enthaelt verbindliche Stil- und Rekonstruktionsregeln fuer diesen Lauf (stil-01-original). Die globalen Ausgabe-Regeln und das im Arbeitsauftrag uebermittelte Glossar haben bei Konflikten Vorrang.

﻿Ziel ist eine originalnahe literarische Übersetzung, die Inhalt, Reihenfolge, Perspektive, Ton, Figurenstimmen, Bildsprache, Redewendungen, Weltbegriffe und Erzählrhythmus des Ausgangstextes möglichst genau bewahrt.



Der Text soll in der Zielsprache natürlich lesbar und literarisch tragfähig klingen. Er soll aber nicht modernisiert, geglättet, vereinfacht, ausgeschmückt oder frei nacherzählt werden.



Bewahre insbesondere den epischen, klar geführten Erzählton:



klare, kontrollierte Sätze statt verschwommener Literaturpose,

konkrete, körperliche Wahrnehmung statt abstrakter Gefühlsbehauptung,

ernste Behandlung von Weltbegriffen, Ritualen, Titeln, Schwüren und fremden Konzepten,

archaische, sakrale, militärische oder fremde Färbungen, wenn sie im Original angelegt sind,

Bildsprache aus Körper, Natur, Licht, Dunkelheit, Stein, Feuer, Blut, Sturm, Waffen oder anderen im Original vorhandenen Motivfeldern,

ruhige erzählerische Führung auch bei Gewalt, Angst und übernatürlichen Ereignissen.



Wichtig für Figuren und Perspektive:



Bewahre die jeweilige Figurenperspektive konsequent.

Verändere keine Figur psychologisch, sozial oder moralisch.

Mache Figuren nicht moderner, klüger, weicher, ironischer, eleganter oder emotional erklärender, als sie im Original sind.

Erhalte innere Gedanken, Wiederholungen, kurze Schock-Sätze und körperliche Reaktionen.

Wenn eine Figur fremde Weltregeln, religiöse Vorstellungen oder soziale Hierarchien ernst nimmt, muss auch die Übersetzung diese Ernsthaftigkeit bewahren.



Wichtig für Sprache und Wörter:



Übersetze nicht mechanisch Wort für Wort, aber bleibe nahe an Bild, Struktur und Wirkung des Originals.

Erhalte ungewöhnliche, altertümliche, raue, feierliche oder fremde Formulierungen, wenn sie zum Original gehören.

Ersetze Redewendungen nicht automatisch durch moderne Standardfloskeln der Zielsprache.

Wenn eine Redewendung oder ein kulturelles Bild in der Originalsprache verständlich nah übertragen werden kann, übertrage es möglichst nah, auch wenn es in der Zielsprache leicht fremd klingt.

Nur wenn eine nahe Übertragung in der Zielsprache unverständlich oder unfreiwillig komisch wäre, wähle eine sinngemäße Formulierung.

Verwende Adjektive gezielt und konkret. Keine unnötige Verschönerung, keine generischen Verstärker.

Erhalte wiederkehrende Begriffe, Namen, Titel, Anreden, Orte, Rangbezeichnungen und Weltkonzepte konsistent.



Wichtig für Dialoge:



Dialoge sollen die Stimme der jeweiligen Figur bewahren.

Keine Dialogzeilen modernisieren, veredeln oder psychologisch ausformulieren.

Kurze, harte, feierliche, unbeholfene oder hierarchische Redeweisen bleiben erhalten, wenn sie im Original vorhanden sind.

Subtext, Zögern, Gehorsam, Furcht, Stolz, Schuld oder Machtgefälle sollen aus der Redeweise und Situation hervorgehen, nicht durch zusätzliche Erklärungen.



Wichtig für Handlung und Action:



Erhalte die Reihenfolge von Bewegungen, Wahrnehmungen, Ursachen und Folgen.

Fantastische, technische, körperliche oder räumliche Vorgänge müssen in der Zielsprache klar nachvollziehbar bleiben.

Kurze Sätze bei Schmerz, Schock, Erkenntnis oder unmittelbarer Gefahr dürfen kurz bleiben.

Längere erklärende Sätze dürfen länger bleiben, wenn sie Mechanik, Weltlogik oder innere Abwägung tragen.



Nicht erlaubt:



keine neuen Gedanken hinzufügen,

keine zusätzlichen Erklärungen einbauen,

keine Motive ergänzen,

keine Handlung kürzen,

keine Absätze zusammenfassen,

keine Figuren umdeuten,

keine kulturelle Fremdheit wegübersetzen,

keine moderne Alltagssprache einführen, wenn das Original ein anderes Register hat.



Die Übersetzung soll wirken wie eine sorgfältige, originalnahe literarische Ausgabe des Textes in der Zielsprache: klar, ernst, bildhaft, weltbewusst und figurengetreu.



Gib ausschließlich die Übersetzung aus. Keine Vorbemerkung, keine Analyse, keine Kommentare.

### Harte Ausgabe-Regeln

Diese Regeln haben Vorrang vor widersprechenden Angaben im Style-Profil.

- Gib nur die Uebersetzung aus.
- Keine Vorbemerkung, keine Zusammenfassung, keine Analyse.
- Keine Saetze wie 'Hier ist die Uebersetzung'.
- Keine Markdown-Ueberschriften, Vorabsaetze, Lede, Prologe oder sonstige Struktur-Ergaenzungen erfinden, ausser sie stehen bereits im Quelltext.
- Technische Kopfzeilen der Quelldatei sind Metadaten und gehoeren nicht in die Uebersetzung: Zeilen wie '# Kapitel N: ...', '*Buch: ...*' und HTML-Kommentare '<!-- ... -->' werden weder uebersetzt noch uebernommen noch ersetzt.
- Inhalt, Reihenfolge und Fakten des Quelltexts bleiben erhalten; nichts ergaenzen, das nicht im Quelltext steht.

## User

Uebersetze den folgenden Text ins Deutsche.

### Buch
- Titel: Der Moloch
- Autor: Alexander Iwanowitsch Kuprin
- Stil: stil-01-original
- Style-Profil: books\kuprin-moloch\styles\stil-01-original.md
- Das Style-Profil steht im System-Prompt und ist verbindlich.
- Namensschreibweise: Deutsche Transliteration russischer Namen nach Duden-Ueblichkeit.
- Beispiele:
  - Бобров -> Bobrow
  - Молох -> Moloch

### Verbindliche Namen und Begriffe

Nutze diese Schreibweisen, wenn die genannten Personen oder Begriffe im Quelltext vorkommen. Nicht aufgefuehrte Personen-, Stammes-, Orts- und Titelnamen werden konservativ transliteriert oder im Zweifel in der erkennbaren Quellform beibehalten.
- Бобров -> Bobrow
- Нина -> Nina
- Квашнин -> Kwaschnin
- Свежевский -> Sweschewski
- Зиненко -> Sinenko
- Шелковников -> Schelkownikow
- Андреа -> Andrea
- Митрофан -> Mitrofan
- Анна Афанасьевна -> Anna Afanassjewna
- Гольдберг -> Goldberg
- Молох -> Der Moloch

### Zu uebersetzender Text

Interne Arbeitsportion 2/2 derselben Szene. Uebersetze nur diesen Abschnitt fortlaufend ins Deutsche. Keine neue Szenenueberschrift erzeugen.

- Ну да, та самая, - снисходительно кивнула в его сторону головой Анна Афанасьевна. - Она еще приходится дальней родней по бабушке Стремоуховым, которых ты знаешь. И вот Лиза Белоконская писала мне, что встретилась в одном обществе с Василием Терентьевичем и рекомендовала ему побывать у нас, если ему вообще вздумается ехать когда-нибудь на завод.

- Сумеем ли мы принять, Нюся? - спросил озабоченно Зиненко.

- Как ты смешно говоришь! Мы сделаем, что можем. Ведь уж, во всяком случае, мы не удивим ничем человека, который имеет триста тысяч годового дохода.

- Господи! Триста тысяч! - простонал Зиненко. - Просто страшно подумать.

- Триста тысяч! - вздохнула, точно эхо, Нина.

- Триста тысяч! - воскликнули восторженно хором девицы.

- Да, и все это он проживает до копеечки, - сказала Анна Афанасьевна. Затем, отвечая на невысказанную мысль дочерей, она прибавила: - Женатый человек. Только, говорят, очень неудачно женился. Его жена какая-то бесцветная личность и совсем не представительна. Что ни говорите, а жена должна быть вывеской в делах мужа.

- Триста тысяч! - повторила еще раз, точно в бреду, Нина. - Чего только на эти деньги не сделаешь!..

Анна Афанасьевна провела рукой по ее пышным волосам.

- Вот бы тебе такого мужа, деточка. А?

Эти триста тысяч чужого годового дохода точно наэлектризовали все общество. С блестящими глазами и разгоревшимися лицами рассказывались и слушались анекдоты о жизни миллионеров, рассказы о баснословных меню обедов, о великолепных лошадях, о балах и исторически безумных тратах денег.

Сердце Боброва похолодело и до боли сжалось. Он тихонько отыскал свою шляпу и осторожно вышел на крыльцо. Его ухода, впрочем, и так никто бы не заметил.

И когда он крупною рысью ехал домой и представил себе томные, мечтательные глаза Нины, шептавшей почти в забытьи: "Триста тысяч!" - ему вдруг припомнился утренний анекдот Свежевского.

- Эта... тоже сумеет себя продать! - прошептал он, судорожно стиснув зубы и с бешенством ударив Фарватера хлыстом по шее.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
