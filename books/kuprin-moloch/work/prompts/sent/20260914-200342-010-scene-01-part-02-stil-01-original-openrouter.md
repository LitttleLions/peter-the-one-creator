# Gesendeter Prompt 010

- Zeitstempel: 20260914-200342
- Provider: openrouter
- Modell: deepseek/deepseek-v4.1-flash
- Stil: stil-01-original
- Kapitel: 010
- Szene: 01
- Chunk: 02/03
- Temperatur: 0.2
- max_tokens: 12000
- System-Zeichen: 5037
- User-Zeichen: 10098

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

- О! Не беспокойтесь, сударыня: вашу барышню ничто не скомпрометирует! закричал ей вдогонку Бобров и вдруг расхохотался таким странным, горьким смехом, что и мать и дочь невольно обернулись.

- Ну! Не говорила я тебе, что это дурак и нахал? - дернула Анна Афанасьевна Нину за руку. - Ему хоть в глаза наплюй, а он хохочет... утешается... Сейчас будут дамы выбирать кавалеров, - прибавила она другим, более спокойным тоном. - Ступай и пригласи Квашнина. Он только что кончил играть. Видишь, стоит в дверях беседки.

- Мама! Да куда же ему танцевать? Он и поворачивается-то насилу-насилу.

- А я тебе говорю: ступай. Он когда-то считался одним из лучших танцоров в Москве... Во всяком случае, ему будет приятно.

Точно в далеком, сером колыхающемся тумане видел Бобров, как Нина быстро перебежала всю площадку и, улыбающаяся, кокетливая, легкая, остановилась перед Квашниным, грациозно и просительно наклонив набок голову. Василий Терентьевич слушал ее, слегка над ней нагнувшись; вдруг он расхохотался, отчего вся его огромная фигура затряслась, и замотал отрицательно головою. Нина долго настаивала, потом вдруг сделала обиженное лицо и капризно повернулась, чтобы отойти. Но Квашнин с вовсе несвойственной ему живостью догнал ее и, пожав плечами с таким видом, как будто бы хотел сказать: "Ну, уж ничего не поделаешь... надо баловать детей..." - протянул ей руку. Все танцующие остановились и с любопытством устремили глаза на новую пару. Зрелище Квашнина, танцующего мазурку, обещало быть чрезвычайно комичным.

Василий Терентьевич выждал такт и вдруг, повернувшись к своей даме движением, исполненным тяжелой, но своеобразно-величественной красоты, так самоуверенно и ловко сделал первое pas, что все сразу в нем почуяли бывшего отличного танцора. Глядя на Нину сверху вниз, с гордым, вызывающим и веселым поворотом головы, он сначала не танцевал, а шел под музыку эластичной, слегка покачивающейся походкой. И огромный рост и толщина, казалось, не только не мешали, но, наоборот, увеличивали в эту минуту тяжеловесную грацию его фигуры. Дойдя до поворота, он остановился на одну секунду, стукнул вдруг каблуком о каблук, быстро завертел Нину на месте и плавно, с улыбающимся снисходительно лицом, пронесся по самой середине площадки на толстых упругих ногах. Перед тем местом, откуда Квашнин взял Нину, он опять завертел свою даму в быстром, красивом движении и, неожиданно посадив на стул, сам остановился перед ней с низко опущенной головой.

Его тотчас же окружили со всех сторон дамы, упрашивая пройтись еще один тур. Но он, утомленный непривычным движением, тяжело дышал и обмахивался платком.

- Довольно, mesdames... пощадите старика... - говорил он, смеясь и насилу переводя дух. - Не в мои годы пускаться в пляс. Пойдемте лучше ужинать...

Общество садилось за столы, гремя придвигаемыми стульями... Бобров продолжал стоять на том самом месте, где его покинула Нина. Чувства унижения, обиды в безнадежной, отчаянной тоски попеременно терзали его. Слез не было, но что-то жгучее щипало глаза, и в горле стоял сухой и колючий клубок... Музыка продолжала болезненно и однообразно отзываться в его голове.

- Батюшка мой! А я-то вас ищу-ищу и никак не найду. Что это вы куда запропастились? - услышал Андрей Ильич рядом с собой веселый голос доктора. Как только приехал, меня сейчас же за винт усадили, насилу вырвался... Идем ужинать. Я нарочно два места захватил, чтобы вместе...

- Ах, доктор! Идите один. Я не пойду, не хочется, - через силу отозвался Бобров.

- Не пойдете? Вот так история! - Доктор пристально поглядел в лицо Боброву. - Да что с вами, голубушка? Вы совсем раскисли, - заговорил он серьезно и с участием. - Ну, уж как хотите, а я вас не оставлю одного. Идем, идем, без всяких разговоров.

- Тяжело мне, доктор. Гадко мне, - ответил тихо Бобров, машинально, однако, следуя за увлекавшим его Гольдбергом.

- Пустяки, пустяки, идем! Будьте мужчиной, плюньте... "Или есть недуг сердечный? Иль на совести гроза?" - неожиданно продекламировал Гольдберг, нежно и крепко обвивая рукой талию Боброва и ласково заглядывая ему в лицо. Я вам сейчас пропишу универсальное средство: "Выпьем, что ли, Ваня, с холода да с горя?.." Мы, по правде сказать, с этим Андреа уже порядочно наконьячились... Ах, и пьет же, курицын сын! Точно в пустую бочку льет... Ну, будьте мужчиной, милочка... Знаете ли, Андреа вами очень интересуется. Идем, идем!..

Говоря таким образом, доктор тащил Боброва в павильон. Они уселись рядом. Соседом Андрея Ильича с другой стороны оказался Андреа.

Андреа, еще издали улыбавшийся Боброву, потеснился, чтобы дать ему место, и ласково догладил его по спине.

- Очень рад, очень рад, садитесь к нам поближе, - сказал он дружелюбно. Симпатичный человек... люблю таких... хороший человек... Коньяк пьете?

Андреа был пьян. Его стеклянные глаза странно оживились и блестели на побледневшем лице (только полгода спустя стало известно, что этот безупречно сдержанный, трудолюбивый, талантливый человек каждый вечер напивался в совершенном одиночестве до потери сознания)...

"А и в самом деле, может быть, станет легче, если выпить, - подумал Бобров, - надо попробовать, черт возьми!"

Андреа дожидался с наклоненной бутылкой в руке. Бобров подставил стакан.

- Та-ак? - протянул Андреа, высоко подымая брови.

- Так, - ответил Бобров с печальной и кроткой улыбкой.

- Ладно! До которых пор?

- Стакан сам скажет.

- Прекрасно. Можно подумать, что вы служили в шведском флоте. Довольно?

- Лейте, лейте.

- Друг мой, но вы, вероятно, выпустили из виду, что это Martel под маркой VSOP - настоящий, строгий, старый коньяк.

- Лейте, не беспокойтесь...

И Бобров подумал с злорадством: "Ну что ж, и буду пьян, как сапожник. Пусть полюбуется..."

Стакан был полон. Андреа поставил бутылку на стол и стал с любопытством наблюдать за своим соседом.

Бобров залпом выпил вино и весь содрогнулся от непривычки.

- Дитя мое, у вас червяк? - спросил Андреа, серьезно поглядев в глаза Боброва.

- Да, червяк, - уныло покачал головою Андрей Ильич.

- В сердце?

- Да.

- Гм!.. Значит, вы хотите еще?

- Лейте, - сказал Бобров покорно и печально.

Он с жадностью и с отвращением пил коньяк, стараясь забыться. Но странно, - вино не оказывало на него никакого действия. Наоборот, ему становилось еще тоскливее и слезы еще больше жгли глаза.

Между тем лакеи разнесли шампанское. Квашнин встал со стула, держа двумя пальцами свой бокал и разглядывая через него огонь высокого канделябра. Все затихли. Слышно было только, как шипел уголь в электрических фонарях и звонко стрекотал неугомонный кузнечик.

Квашнин откашлялся.

- Милостивые государыни и милостивые государи! - начал он и сделал внушительную паузу. - Я думаю, никто из вас не усомнится в том искреннем чувстве признательности, с которым я подымаю этот бокал! Я никогда не забуду сделанного мне в Иванкове радушного приема, и сегодняшний маленький пикник благодаря очаровательной любезности посетивших его дам останется для меня навсегда приятнейшим воспоминанием. Пью за ваше здоровье, mesdames!

Он поднял кверху свой бокал, сделал им в воздухе широкий полукруг, отпил из него немного и продолжал:

- К вам, мои ближайшие сотрудники и товарищи, обращаю слово. Не осудите, если оно будет носить характер поучения: по летам я старик, сравнительно с большинством присутствующих, а на старика за поучение можно и не обижаться.

Андреа нагнулся к уху Боброва и прошептал:

- Посмотрите, какие рожи делает этот каналья Свежевский.

Свежевский действительно выражал своим лицом самое подобострастное и преувеличенное внимание. Когда Василий Терентьевич упомянул о своей старости, он и головой и руками начал делать протестующие жесты.

- Я все-таки повторю старое, избитое выражение газетных передовых статей, - продолжал Квашнин. - Держите высоко наше знамя. Не забывайте, что мы соль земли, что нам принадлежит будущее... Не мы ли опутали весь земной шар сетью железных дорог? Не мы ли разверзаем недра земли и превращаем ее сокровища в пушки, мосты, паровозы, рельсы и колоссальные машины? Не мы ли, исполняя силой нашего гения почти невероятные предприятия, приводим в движение тысяче-миллионные капиталы?.. Знайте, господа, что премудрая природа тратит свои творческие силы на создание целой нации только для того, чтобы из нее вылепить два или три десятка избранников. Имейте же смелость и силу быть этими избранниками, господа! Ура!

- Ура! Ура! - закричали гости, и громче всех выделился голос Свежевского.

Все встали со своих мест и пошли чокаться с Василием Терентьевичем.

- Гнусная речь, - сказал доктор вполголоса.

После Квашнина поднялся Шелковников и закричал:

- Господа! За здоровье нашего уважаемого патрона, нашего дорогого учителя и в настоящее время нашего амфитриона: за здоровье Василия Терентьевича Квашнина! Ура!

- Ура-а! - подхватили единодушно все гости и опять пошли чокаться с Квашниным.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
