# Gesendeter Prompt 006

- Zeitstempel: 20260914-200102
- Provider: openrouter
- Modell: deepseek/deepseek-v4.1-flash
- Stil: stil-01-original
- Kapitel: 006
- Szene: 01
- Chunk: 02/02
- Temperatur: 0.2
- max_tokens: 12000
- System-Zeichen: 5037
- User-Zeichen: 9676

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

- Вы не хотели никогда меня понять, Андрей Ильич, - сказала она с упреком. - Вы нервны и нетерпеливы. Вы преувеличиваете все, что во мне есть хорошего, но зато не прощаете мне того, что я не могу же быть иной в той среде, где я живу. Это было бы смешно, это внесло бы в нашу семью несогласие. Я слишком слаба и, надо правду сказать, слишком ничтожна для борьбы и для самостоятельности... Я иду туда, куда идут все, гляжу на вещи и сужу о них, как все. И вы не думайте, чтобы я не сознавала своей обыденности... Но я с другими не чувствую ее тяжести, а с вами... с вами я всякую меру теряю, потому что... - она запнулась, - ну, да все равно... потому что вы совсем другой, потому что такого, как вы, человека я никогда еще в жизни не встречала.

Ей казалось, что она говорит искренно. Бодрящая свежесть осеннего воздуха, вокзальная суета, сознание своей красоты, удовольствие чувствовать на себе влюбленный взгляд Боброва - все это наэлектризовало ее до того состояния, в котором истеричные натуры лгут так вдохновенно, так пленительно и так незаметно для самих себя. С наслаждением любуясь собой в новой роли девицы, жаждущей духовной поддержки, она чувствовала потребность говорить Боброву приятное.

- Я знаю, что вы меня считаете кокеткой... Пожалуйста, не оправдывайтесь... И я согласна, я даю повод так думать... Например, я смеюсь и болтаю часто с Миллером. Но если бы вы знали, как мне противен этот вербный херувим! Или эти два студента... Красивый мужчина уже по тому одному неприятен, что вечно собой любуется... Поверите ли, хотя это, может быть, и странно, но мне всегда были особенно симпатичны некрасивые мужчины.

При этой милой фразе, произнесенной самым нежным тоном, Бобров грустно вздохнул. Увы! Он уже не раз из женских уст слышал это жестокое утешение, в котором женщины никогда не отказывают своим некрасивым поклонникам.

- Значит, и я могу надеяться заслужить когда-нибудь вашу симпатию? спросил он шутливым тоном, в котором, однако, явственно прозвучала горечь насмешки над самим собой.

Нина быстро спохватилась.

- Ну вот, какой вы, право. С вами нельзя разговаривать... Зачем вы напрашиваетесь на комплименты, милостивый государь? Стыдно!..

Она сама немного сконфузилась своей неловкости и, чтобы переменить разговор, спросила с игривой повелительностью:

- Ну-с, что же вы это собирались мне сказать при другой обстановке? Извольте немедленно отвечать!

- Я не знаю... не помню, - замялся расхоложенный Бобров.

- Я вам напомню, мой скрытный друг. Вы начали говорить о вчерашнем дне, потом о каких-то прекрасных мгновениях, потом сказали, что я, наверно, давно уже заметила... но что? Вы этого не докончили... Извольте же говорить теперь. Я требую этого, слышите!

Она глядела на него глазами, в которых сияла улыбка - лукавая, и обещающая, и нежная в одно и то же время... Сердце Боброва сладко замерло в груди, и он почувствовал опять прилив прежней отваги. "Она знает, она сама хочет, чтобы я говорил", - подумал он, собираясь с духом.

Они остановились на самом краю платформы, где совсем не было публики. Оба были взволнованы. Нина ждала ответа, наслаждаясь остротой затеянной ею игры. Бобров искал слов, тяжело дышал и волновался. Но в это время послышались резкие звуки сигнальных рожков, и на станции поднялась суматоха.

- Так слышите же... Я жду, - шепнула Нина, быстро отходя от Боброва. - Для меня это гораздо важнее, чем вы думаете...

Из-за поворота железной дороги выскочил окутанный черным дымом курьерский поезд. Через несколько минут, громыхая на стрелках, он плавно и быстро замедлил ход и остановился у платформы... На самом конце его был прицеплен длинный, блестящий свежей синей краской служебный вагон, к которому устремились все встречающие. Кондуктора почтительно бросились раскрывать дверь вагона; из нее тотчас же выскочила, с шумом развертываясь, складная лестница. Начальник станции, красный от волнения и беготни, с перепуганным лицом торопил рабочих с отцепкой служебного вагона. Квашнин был одним из главных акционеров N-ской железной дороги и ездил по ее ветвям с почетом, какого не всегда удостаивалось даже самое высшее железнодорожное начальство.

В вагон вошли только Шелковников, Андреа и двое влиятельных инженеров-бельгийцев. Квашнии сидел в кресле, расставив свои колоссальные ноги и выпятив вперед живот. На нем была круглая фетровая шляпа, из-под которой сияли огненные волосы; бритое, как у актера, лицо с обвисшими щеками и тройным подбородком, испещренное крупными веснушками, казалось заспанным и недовольным; губы складывались в презрительную, кислую гримасу.

При виде инженеров он с усилием приподнялся.

- Здравствуйте, господа, - сказал он сиплым басом, протягивая им поочередно для почтительных прикосновений свою огромную пухлую руку. - Ну-с, как у вас на заводе?

Шелковников начал докладывать языком служебной бумаги. На заводе все благополучно. Ждут только приезда Василия Терентьевича, чтобы в его присутствии пустить доменную печь и сделать закладку новых зданий... Рабочие и мастера наняты по хорошим ценам. Наплыв заказов так велик, что побуждает как можно скорее приступить к работам.

Квашнин слушал, отворотясь лицом к окну, и рассеянно разглядывал собравшуюся у служебного вагона толпу. Лицо его ничего не выражало, кроме брезгливого утомления.

Вдруг он прервал директора неожиданным вопросом:

- Э... па... послушайте... Кто эта девочка?

Шелковников заглянул в окно.

- Ну, вот эта... с желтым пером на шляпе, - нетерпеливо показал пальцем Квашнин.

- Ах, эта? - встрепенулся директор и, наклонившись к уху Квашнина, прошептал таинственно по-французски: - Это дочь нашего заведующего складом. Его фамилия Зиненко.

Квашнин грузно кивнул головой. Шелковников продолжал свой доклад, но принципал опять перебил его:

- Зиненко... Зиненко... - протянул он задумчиво и не отрываясь от окна. Зиненко... кто же такой этот Зиненко?.. Где я эту фамилию слышал?.. Зиненко?

- Он у нас заведует складом, - почтительно и умышленно бесстрастно повторил Шелковников.

- Ах, вспомнил! - догадался вдруг Василий Терентьевич. - Мне о нем в Петербурге говорили... Ну-с, продолжайте, пожалуйста.

Нина безошибочным женским чутьем поняла, что именно на нее смотрит Квашнин и о ней говорит в настоящую минуту. Она немного отвернулась, но лицо ее, разрумянившееся от кокетливого удовольствия, все-таки было, со всеми своими хорошенькими родинками, видно Василию Терентьевичу.

Наконец доклад окончился, и Квашнин вышел на площадку, устроенную в виде просторного стеклянного павильона сзади вагона.

Это был момент, для увековечения которого, как подумал Бобров, не хватало только хорошего фотографического аппарата. Квашнин почему-то медлил сходить вниз и стоял за стеклянной стеной, возвышаясь своей массивной фигурой над теснящейся около вагона группой, с широко расставленными ногами и брезгливой миной на лице, похожий на японского идола грубой работы. Эта неподвижность патрона, очевидно, коробила встречающих: на их губах застыли, сморщив их, заранее приготовленные улыбки, между тем как глаза, устремленные вверх, смотрели на Квашнина с подобострастием, почти с испугом. По сторонам дверцы застыли в солдатских позах молодцеватые кондуктора. Заглянув случайно в лицо опередившей его Нины, Бобров с горечью заметил и на ее лице ту же улыбку и тот же тревожный страх дикаря, взирающего на своего идола.

"Неужели же здесь только бескорыстное, почтительное изумление перед тремястами тысячами годового дохода? - подумал Андрей Ильич. - Что же заставляет всех этих людей так униженно вилять хвостом перед человеком, который даже и не взглянет на них никогда внимательно? Или здесь есть какой-нибудь не доступный пониманию психологический закон подобострастия?"

Постояв немного, Квашнин решился двинуться и, предшествуемый своим животом, поддерживаемый бережно под руки поездной прислугой, спустился по ступеням на платформу.

На почтительные поклоны быстро расступившейся перед ним вправо и влево толпы он небрежно кивнул головой, выпятив вперед толстую нижнюю губу, и сказал гнусаво:

- Господа, вы свободны до завтрашнего дня.

Не дойдя до подъезда, он знаком подозвал к себе директора.

- Так вы, Сергей Валерьянович, представьте мне его, - сказал он вполголоса.

- Зиненку? - предупредительно догадался Шелконников.

- Ну да, черт возьми! - внезапно раздражаясь, буркнул Квашнин: - Только не здесь, не здесь, - остановил он за рукав устремившегося было директора. Когда я буду на заводе...

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
