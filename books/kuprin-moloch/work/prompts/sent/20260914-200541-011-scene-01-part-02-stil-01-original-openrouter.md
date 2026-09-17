# Gesendeter Prompt 011

- Zeitstempel: 20260914-200541
- Provider: openrouter
- Modell: deepseek/deepseek-v4.1-flash
- Stil: stil-01-original
- Kapitel: 011
- Szene: 01
- Chunk: 02/03
- Temperatur: 0.2
- max_tokens: 12000
- System-Zeichen: 5037
- User-Zeichen: 9864

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

Но едва он отошел пять шагов от лошадей, как убедился, что то, что он принимал за черную стену, была большая, тесная толпа рабочих, запружавшая дорогу и медленно, в молчании подвигавшаяся вперед. Пройдя машинально вслед за рабочими шагов пятьдесят, Андрей Ильич повернул назад, чтобы найти Митрофана и объехать завод с другой стороны. Но ни Митрофана, ни лошадей на дороге не было. Митрофан ли поехал в другую сторону отыскивать барина, или сам Бобров заблудился - понять этого Андрей Ильич не мог. Он стал кричать кучера - никто ему не откликался. Тогда Бобров решил догнать только что оставленных рабочих и с этой целью опять повернулся и побежал, как ему казалось, в прежнюю сторону. Но, странно, рабочие точно провалились сквозь землю, и вместо них Бобров уперся с разбегу в невысокий деревянный забор.

Забору этому не было конца ни вправо, ни влево. Бобров перелез через него и стал взбираться по какому-то длинному, крутому откосу, поросшему частым бурьяном. Холодный пот струился по его лицу, язык во рту сделался сух и неподвижен, как кусок дерева; в груди При каждом вздохе ощущалась острая боль; кровь сильными, частыми ударами била в темя; ушибленный висок нестерпимо ныл...

Ему казалось, что подъем бесконечен, и тупое отчаяние овладевало его душой. Но он продолжал карабкаться наверх, ежеминутно падая, ссаживая колени и хватаясь руками за колючие кусты. Временами ему представлялось, что он спит и видит один из своих лихорадочных болезненных снов. И панический переполох после пикника, и долгое блуждание по дороге, и бесконечное карабканье по насыпи - все было так же тяжело, нелепо, неожиданно и ужасно, как эти кошмары.

Наконец откос кончился, и Бобров сразу узнал железнодорожную насыпь. С этого места фотограф снимал накануне, во время молебна, группу инженеров и рабочих. Совершенно обессиленный, он сел на шпалу, и в ту же минуту с ним произошло что-то странное: ноги его вдруг болезненно ослабли, в груди и в брюшной полости появилось тягучее, щемящее, отвратительное раздражение, лоб и щеки сразу похолодели. Потом все повернулось перед его глазами и вихрем понеслось мимо, куда-то в беспредельную глубину.

Андрей Ильич очнулся от обморока по крайней мере через полчаса. Внизу, у подножия насыпи, там, где обыкновенно с несмолкаемым грохотом день и ночь работал исполинский завод, была необычная жуткая тишина. Бобров с трудом поднялся на ноги и пошел по направлению к доменным печам. Голова его была так тяжела, что с трудом держалась на плечах, больной висок при каждом движении причинял невыносимую боль. Ощупывая рану, он опять почувствовал пальцами липкое и теплое прикосновение крови. Кровь была также у него во рту и на губах: он слышал ее соленый, металлический вкус. Сознание еще не вполне вернулось к нему, и усилие вспомнить и уяснить прошедшее причиняло ему сильную головную боль. Острая тоска и отчаянная, беспредметная злоба переполняли его душу...

Утро заметно уже близилось. Все было серо, холодно и мокро: и земля, и небо, и тощая желтая трава, и бесформенные кучи камня, сваленного по сторонам дороги. Бобров бесцельно бродил между опустевших заводских зданий и, как это случается иногда при особенно сильных душевных потрясениях, говорил сам с собою вслух. Ему хотелось удержать, привести в порядок разбегавшиеся мысли.

- Ну, скажи же, скажи, что мне делать? Скажи ради бога, - страстно шептал он, обращаясь к кому-то другому, постороннему, как будто сидевшему внутри его. - Ах, как мне тяжело! Ах, как мне больно!.. Невыносимо больно!.. Мне кажется, я убью себя... Я не выдержу этой муки...

А другой, посторонний, возражал из глубины его души, также вслух, но насмешливо-грубо:

- Нет, ты не убьешь себя. Зачем перед собой притворяться?.. Ты слишком любишь ощущение жизни, для того чтобы убить себя. Ты слишком немощен духом для этого. Ты слишком боишься физической боли. Ты слишком много размышляешь.

- Что же мне делать? Что же мне делать? - шептал опять Андрей Ильич, ломая руки. - Она такая нежная, такая чистая - моя Нина! Она была у меня одна во всем мире. И вдруг - о, какая гадость! - продать свою молодость, свое девственное тело!..

- Не ломайся, не ломайся; к чему эти пышные слова старых мелодрам, иронически говорил другой. - Если ты так ненавидишь Квашнина, поди и убей его.

- И убью! - закричал Бобров, останавливаясь бешено подымая кверху кулаки. - И убью! Пусть он заражает больше честных людей своим мерзким дыханием. И убью!

Но другой заметил с ядовитой насмешкой:

- И не убьешь... И отлично знаешь это. У тебя нет на это ни решимости, ни силы... Завтра же опять будешь благоразумен и слаб...

Среди этого ужасного состояния внутреннего раздвоения наступали минутные проблески, когда Бобров с недоумением спрашивал себя: что с ним, и как он подал сюда, и что ему надо делать? А сделать что-то нужно было непременно, сделать что-то большое и важное, но что именно, - Бобров забыл и морщился от боли, стараясь вспомнить. В один из таких светлых промежутков он увидел себя стоящим над кочегарной ямой. Ему тотчас же с необычайной яркостью вспомнился недавний разговор с доктором на этом самом месте.

Внизу никого из кочегаров не было: все они разбежались. Котлы давно успели охладеть. Только в двух крайних топках еще рдел еле-еле каменный уголь... Безумная мысль вдруг, как молния, мелькнула в мозгу Андрея Ильича. Он быстро нагнулся, свесил ноги вниз, потом повис на руках и спрыгнул в кочегарку.

В куче угля была воткнута лопата. Бобров схватил ее и торопливыми движениями принялся совать уголь в оба топочные отверстия. Через две минуты белое бурное пламя уже гудело в топках, а в котле глухо забурлила вода. Бобров все бросал и бросал, лопату за лопатой, уголь; в то же время он лукаво улыбался, кивал кому-то невидимому головой и издавал отрывистые, бессмысленные восклицания. Болезненная, мстительная и страшная мысль, мелькнувшая еще там, на дороге, овладевала им все более. Он смотрел на огромное тело котла, начинавшего гудеть и освещаться огненными отблесками, и оно казалось ему все более живым и ненавистным.

Никто не мешал. Вода быстро убавлялась в водомере. Клокотание котла и гудение топок становилось все грознее и громче.

Но непривычная работа скоро утомила Боброва. Жилы в висках стали биться с горячечной быстротой и напряженностью, кровь из раны потекла по щеке теплой струей. Безумная вспышка энергии прошла, а внутренний, посторонний, голос заговорил громко и насмешливо:

- Ну, что же, остается сделать одно еще движение! Но ты его не сделаешь... Basta...[ хватит, довольно - итал .] Ведь все это смешно, и завтра ты не посмеешь даже признаться, что ночью хотел взрывать паровые котлы.

Солнце уже показалось на горизонте в виде тусклого большого пятна, когда Андреи Ильич пришел в заводскую больницу.

Доктор, только что прервавший на минуту перевязку, раненых и изувеченных людей, умывал руки под медным рукомойником. Фельдшер стоял рядом и держал полотенце. Увидев вошедшего Боброва, доктор попятился назад от изумления.

- Что с вами, Андрей Ильич, на вас лица нет? - проговорил он с испугом.

Действительно, вид у Боброва был ужасный. Кровь запеклась черными сгустками на его бледном лице, выпачканном во многих местах угольною пылью. Мокрая одежда висела клочьями на рукавах и на коленях; волосы падали беспрядочными прядями на лоб.

- Да говорите же, Андрей Ильич, ради бога, что с вами случилось? - повторил Гольдберг, наскоро вытирая руки и подходя к Боброву.

- Ах, это все пустяки... - простонал Бобров. - Ради бога, доктор, дайте морфия... Скорее морфия, или я сойду с ума!.. Я невыразимо страдаю!..

Гольдберг взял Андрея Ильича за руку, поспешно увел в другую комнату и, плотно прикрыв дверь, сказал:

- Послушайте, я догадываюсь, что вас терзает... Поверьте, мне вас глубоко жаль, и я готов помочь вам... Но... голубушка моя, - в голосе доктора послышались слезы, - милый мой Андрей Ильич... не можете ли вы перетерпеть как-нибудь? Вы только вспомните, скольких нам трудов стоило побороть эту поганую привычку! Беда, если я вам теперь сделаю инъекцию... вы уже больше никогда... понимаете, никогда не отстанете...

Бобров повалился на широкий клеенчатый диван лицом вниз и пробормотал сквозь стиснутые зубы, весь дрожа от озноба:

- Все равно... мне все равно, доктор... Я не могу больше выносить.

Доктор вздохнул, пожал плечами и вынул из аптечного шкафа футляр с правацовским шприцем. Через пять минут Бобров уже лежал на клеенчатом диване в глубоком сне. Сладкая улыбка играла на его бледном, исхудавшем за ночь лице. Доктор осторожно обмывал его голову.

## 1896

------------------------------------------------------------------------------

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
