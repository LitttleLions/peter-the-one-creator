# Gesendeter Prompt 010

- Zeitstempel: 20260914-200342
- Provider: openrouter
- Modell: deepseek/deepseek-v4.1-flash
- Stil: stil-01-original
- Kapitel: 010
- Szene: 01
- Chunk: 03/03
- Temperatur: 0.2
- max_tokens: 12000
- System-Zeichen: 5037
- User-Zeichen: 5116

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

Interne Arbeitsportion 3/3 derselben Szene. Uebersetze nur diesen Abschnitt fortlaufend ins Deutsche. Keine neue Szenenueberschrift erzeugen.

Потом началась какая-то оргия красноречия. Произносили тосты и за успех предприятия, и за отсутствующих акционеров, и за дам, участвующих на пикнике, и за всех дам вообще. Некоторые тосты были двусмысленны и игриво-неприличны.

Шампанское, истребляемое дюжинами, оказывало свое действие: сплошной гул стоял в павильоне, и произносившему тост приходилось каждый раз, прежде чем начать говорить, долго и тщетно стучать ножом по стакану. В стороне, на отдельном маленьком столике, красавец Миллер приготовлял в большой серебряной чаше жженку... Вдруг опять поднялся Квашнин, на лице его играла добродушно-лукавая улыбка.

- Мне очень приятно, господа, что наш праздник как раз совпал с одним торжеством семейного характера, - сказал он с обворожительной любезностью. Поздравимте от всей души и пожелаем счастья нареченным жениху и невесте: за здоровье Нины Григорьевны Зиненко и... - он замялся, потому что позабыл имя и отчество Свежевского... - и нашего товарища, господина Свежевского...

Крики, встретившие слова Квашнина, были тем громче, что сообщаемая им новость оказалась совсем неожиданной. Андреа, услышавший рядом с собою восклицание, более похожее на мучительный стон, обернулся и увидел, что бледное лицо Боброва искривлено внутренним страданием.

- Коллега, вы еще не все знаете, - шепнул Андреа. - Послушайте-ка, я сейчас скажу пару теплых слов.

Он уверенно поднялся, уронив при этом свой стул и рукоплескав половину бокала, и воскликнул:

- Милостивые государи! Наш многоуважаемый хозяин из весьма понятной, великодушной скромности не докончил своего тоста... Мы должны поздравить нашего дорогого товарища, Станислава Ксаверьевича Свежевского, с новым назначением: с будущего месяца он займет ответственный пост управляющего делами правления общества... Это назначение будет, так сказать, свадебным подарком для молодых от глубокоуважаемого Василия Терентьевича... Я вижу на лице нашего высокочтимого патрона неудовольствие... Вероятно, я нечаянно выдал приготовленный им сюрприз и потому прошу прощения. Но, движимый чувством дружбы и уважения, я не могу не пожелать, чтобы наш дорогой товарищ, Станислав Ксаверьевич Свежевский, и на новом своем поприще в Петербурге оставался таким же деятельным работником и таким же любимым товарищем, как и здесь... Но я знаю, господа, никто из нас не позавидует Станиславу Ксаверьевичу (он остановился и с едкой насмешкой посмотрел на Свежевского)... потому что все мы так дружно желаем ему всего хорошего, что...

Речь его была внезапно прервана громким лошадиным топотом. Из чащи точно вынырнул верхом на взмыленной лошади какой-то человек без шапки, с лицом, на котором застыло, перекосив его, выражение ужаса. Это был десятник, служивший у подрядчика Дехтерева. Бросив на средине площадки лошадь, дрожавшую от усталости, он подбежал к Василию Терентьевичу и, фамильярно нагнувшись к его уху, стал что-то шептать... В павильоне сделалось вдруг страшно тихо и, как раньше, слышно было только шипение угля и назойливый крик кузнечика.

Красное от вина лицо Квашнина побледнело. Он нервно поставил на стол бокал, который держал в руке, и вино из бокала расплескалось по скатерти.

- А бельгийцы? - спросил он отрывисто и хрипло.

Десятник отрицательно замотал головой и опять зашептал что-то под самым ухом Квашнина.

- А, черт! - воскликнул вдруг Квашнин, вставая с места и комкая в руках салфетку. - Надо же было... Подожди, ты сейчас же отвезешь на станцию телеграмму к губернатору. Господа, - громко и взволнованно обратился он к присутствующим, - на заводе - беспорядки... Надо принимать меры, и... и, кажется, нам лучше всего будет немедленно уехать отсюда...

- Так я и знал, - презрительно, со спокойной злобой сказал Андреа.

И в то время, когда все засуетились, он медленно достал новую сигару, нащупал в кармане спички и налил себе в стакан коньяку.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
