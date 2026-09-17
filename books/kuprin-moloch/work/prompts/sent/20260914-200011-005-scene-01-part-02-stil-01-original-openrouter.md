# Gesendeter Prompt 005

- Zeitstempel: 20260914-200011
- Provider: openrouter
- Modell: deepseek/deepseek-v4.1-flash
- Stil: stil-01-original
- Kapitel: 005
- Szene: 01
- Chunk: 02/03
- Temperatur: 0.2
- max_tokens: 12000
- System-Zeichen: 5037
- User-Zeichen: 9639

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

Interne Arbeitsportion 2/3 derselben Szene. Uebersetze nur diesen Abschnitt fortlaufend ins Deutsche. Keine neue Szenenueberschrift erzeugen.

- Ну да, ну да, голубчик, все это я говорил, - заторопился он не совсем, однако, уверенно. - Я и теперь это утверждаю. Но надо же, голубчик, так сказать, приспособляться. Как же жить-то иначе? Во всякой профессии есть эти скользкие пунктики. Вот взять хоть нас, например, докторов... Вы думаете, у нас все это так ясно и хорошо, как в книжечке? Да ведь мы дальше хирургии ничего ровнешенько не знаем наверняка. Мы выдумываем новые лекарства и системы, но совершенно забываем, что из тысячи организмов нет двух, хоть сколько-нибудь похожих составом крови, деятельностью сердца, условиями наследственности и черт знает чем еще! Мы удалились от единого верного терапевтического пути - от медицины зверей и знахарок, мы наводнили фармакопею разными кокаинами, атропинами, фенацетинами, но мы упустили из виду, что если простому человеку дать чистой воды да уверить его хорошенько, что это сильное лекарство, то простой человек выздоровеет. А между тем в девяноста случаях из ста в нашей практике помогает только эта уверенность, внушаемая нашим профессиональным жреческим апломбом. Поверите ли? Один хороший врач, и в то же время умный и честный человек, признавался мне, что охотники лечат собак гораздо рациональнее, чем мы людей. Там одно средство - серный цвет, - вреда особенного он не принесет, а иногда все-таки и помогает... Не правда ли, голубчик, приятная картинка? А, однако, и мы делаем, что можем... Нельзя, мой дорогой, иначе: жизнь требует компромиссов... Иной раз хоть своим видом всезнающего авгура, а все-таки облегчишь страдания ближнего. И на том спасибо.

- Да, компромиссы - компромиссами, - возразил мрачным тоном Бобров, - а, однако, вы у масальского каменщика кости из черепа-то сегодня извлекли...

- Ах, голубчик, что значит один исправленный череп? Подумайте-ка, сколько ртов вы кормите и скольким рукам даете работу. Еще в истории Иловайского сказано, что "царь Борис, желая снискать расположение народных масс, предпринимал в голодные годы постройку общественных зданий". Что-то в этом роде... Вот вы и посчитайте, какую колоссальную сумму пользы вы...

При последних словах Боброва точно подбросило на кровати, и он быстро уселся на ней, свесив вниз голые ноги.

- Пользы?! - закричал он исступленно. - Вы мне говорите о пользе? В таком случае уж если подводить итоги пользе и вреду, то, позвольте, я вам приведу маленькую страничку из статистики. - И он начал мерным и резким тоном, как будто бы говорил с кафедры: - Давно известно, что работа в рудниках, шахтах, на металлических заводах и на больших фабриках сокращает жизнь рабочего приблизительно на целую четверть. Я не говорю уже о несчастных случаях или непосильном труде. Вам, как врачу, гораздо лучше моего известно, какой процент приходится на долю сифилиса, пьянства и чудовищных условий прозябания в этих проклятых бараках и землянках... Постойте, доктор, прежде чем возражать, вспомните, много ли вы видели на фабриках рабочих старее сорока - сорока пяти лет? Я положительно не встречал. Иными словами, это значит, что рабочий отдает предпринимателю три месяца своей жизни в год, неделю - в месяц или, короче, шесть часов в день. Теперь слушайте дальше... У нас, при шести домнах, будет занято до тридцати тысяч человек, - царю Борису, верно, и не снились такие цифры! Тридцать тысяч человек, которые все вместе, так сказать, сжигают в сутки сто восемьдесят тысяч часов своей собственной жизни, то есть семь с половиной тысяч дней, то есть, наконец, сколько же это будет лет?

- Около двадцати лет, - подсказал после небольшого молчания доктор.

- Около двадцати лет в сутки! - закричал Бобров. - Двое суток работы пожирают целого человека. Черт возьми! Вы помните из Библии, что какие-то там ассирияне или моавитяне приносили своим богам человеческие жертвы? Но ведь эти медные господа. Молох и Дагон, покраснели бы от стыда и от обиды перед теми цифрами, что я сейчас привел...

Эта своеобразная математика только что пришла в, голову Боброву (он, как и многие очень впечатлительные люди, находил новые мысли только среди разговора). Тем не менее и его самого и Гольдберга поразила оригинальность вычисления.

- Черт возьми, вы меня ошеломили, - отозвался с дивана доктор. - Хотя цифры могут быть и не совсем точными...

- А известна ли вам, - продолжал с еще большей горячностью Бобров, известна ли вам другая статистическая таблица, по которой вы с чертовской точностью можете вычислить, во сколько человеческих жизней обойдется каждый шаг вперед вашей дьявольской колесницы, каждое изобретение какой-нибудь поганой веялки, сеялки или рельсопрокатки? Хороша, нечего сказать, ваша цивилизация, если ее плоды исчисляются цифрами, где в виде единиц стоит железная машина, а в виде нулей - целый ряд человеческих существований!

- Но, послушайте, голубчик вы мой, - возразил доктор, сбитый с толку пылкостью Боброва, - тогда, по-вашему, лучше будет возвратиться к первобытному труду, что ли? Зачем же вы всё черные стороны берете? Ведь вот у нас, несмотря на вашу математику, и школа есть при заводе, и церковь, и больница хорошая, и общество дешевого кредита для рабочих...

Бобров совсем вскочил с постели и босой забегал по комнате.

- И больница ваша и школа - все это пустяки! Цаца детская для таких гуманистов, как вы, - уступка общественному мнению... Если хотите, я вам скажу, как мы на самом деле смотрим... Вызнаете, что такое финиш?

- Финиш? Это что-то лошадиное, кажется? Что-то такое на скачках?

- Да, на скачках. Финишем называются последние сто сажен перед верстовым столбом. Лошадь должна их проскакать с наибольшей скоростью, - за столбом она может хоть издохнуть. Финиш - это полнейшее, максимальное напряжение сил, и, чтобы выжать из лошади финиш, ее истязают хлыстом до крови... Так вот и мы. А когда финиш выжат и кляча упала с переломленной спиной и разбитыми ногами, - к черту ее, она больше никуда не годится! Вот тогда и извольте утешать павшую на финише клячу вашими школами да больницами... Вы видели ли когда-нибудь, доктор, литейное и прокатное дело? Если видали, то вы должны знать, что оно требует адской крепости нервов, стальных мускулов и ловкости циркового артиста... Вы должны знать, что каждый мастер несколько раз в день избегает смертельной опасности только благодаря удивительному присутствию духа... И сколько за этот труд рабочий получает, хотите вы знать?

- А все-таки, пока стоит завод, труд этого рабочего обеспечен, - сказал упрямо Гольдберг.

- Доктор, не говорите наивных вещей! - воскликнул Бобров, садясь на подоконник. - Теперь рабочий более чем когда-либо зависит от рыночного спроса, от биржевой игры, от разных закулисных интриг. Каждое громадное предприятие, прежде чем оно пойдет в ход, насчитывает трех или четырех покойников-патронов. Вам известно, как создалось наше общество? Его основала за наличные деньги небольшая компания капиталистов. Дело предполагалось устроить сначала в небольших размерах. Но целая банда инженеров, директоров и подрядчиков ухнула капитал так скоро, что предприниматели не успели и оглянуться. Возводились громадные постройки, которые потом оказывались негодными... Капитальные здания шли, как у нас говорят, "на мясо", то есть рвались динамитом. И когда в конце концов предприятие пошло по десять копеек за рубль, только тогда стало понятно, что вся эта сволочь действовала по заранее обдуманной системе и получала за свой подлый образ действий определенное жалованье от другой, более богатой и ловкой компании. Теперь дело идет в гораздо больших размерах, но мне хорошо известно, что при крахе первого покойника восемьсот рабочих не получили двухмесячного жалованья. Вот вам и обеспеченный труд! Да стоит только акциям упасть на бирже, как это сейчас же отражается на заработной плате. А вам, я думаю, известно, как поднимаются и падают на бирже акции? Для этого нужно мне приехать в Петербург - шепнуть маклеру, что вот, мол, хочу я продать тысяч на триста акций, "только, мол, ради бога, это между нами, уж лучше я вам заплачу хороший куртаж, только молчите...". Потом другому и третьему шепнуть то же самое по секрету, и акции мгновенно падают на несколько десятков рублей. И чем больше секрет, тем скорее и вернее упадут акции... Хороша обеспеченность!..

Сильным движением руки Бобров разом распахнул окно. В комнату ворвался холодный, воздух.

- Посмотрите, посмотрите сюда, доктор! - крикнул Андрей Ильич, показывая пальцем по направлению завода.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
