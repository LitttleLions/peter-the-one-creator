# Gesendeter Prompt 001

- Zeitstempel: 20260914-204912
- Provider: openrouter
- Modell: deepseek/deepseek-v4.1-flash
- Stil: stil-01-original
- Kapitel: 001
- Szene: 01
- Chunk: 02/02
- Temperatur: 0.2
- max_tokens: 12000
- System-Zeichen: 5046
- User-Zeichen: 11797

## System

Du bist ein literarischer Uebersetzer. Du uebersetzt aus der Ausgangssprache ins Deutsche.

---
Buch: Tausend Seelen (Alexei Feofilaktowitsch Pissemski)
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
- Titel: Tausend Seelen
- Autor: Alexei Feofilaktowitsch Pissemski
- Stil: stil-01-original
- Style-Profil: books\pissemski-tausend-seelen\styles\stil-01-original.md
- Das Style-Profil steht im System-Prompt und ist verbindlich.
- Namensschreibweise: Deutsche Transliteration russischer Namen nach Duden-Ueblichkeit.
- Beispiele:
  - Калинович -> Kalinowitsch
  - Настенька -> Nastjenka
  - Годнев -> Godnew
  - Белавин -> Belawin

### Verbindliche Namen und Begriffe

Nutze diese Schreibweisen, wenn die genannten Personen oder Begriffe im Quelltext vorkommen. Nicht aufgefuehrte Personen-, Stammes-, Orts- und Titelnamen werden konservativ transliteriert oder im Zweifel in der erkennbaren Quellform beibehalten.
- Калинович -> Kalinowitsch
- Настенька -> Nastjenka
- Петр Михайлыч Годнев -> Pjotr Michailytsch Godnew
- Полина -> Polina
- Белавин -> Belawin
- Князь -> Fuerst
- Палагея Евграфовна -> Pelageja Jewgrafowna
- Яков Васильич -> Jakow Wassiljitsch
- Медиокритский -> Mediokritski
- Тысяча душ -> Tausend Seelen

### Zu uebersetzender Text

Interne Arbeitsportion 2/2 derselben Szene. Uebersetze nur diesen Abschnitt fortlaufend ins Deutsche. Keine neue Szenenueberschrift erzeugen.

- Я, ей-богу, ничего не делал; спросите всех. Они на меня, известно,
нападают. Мне сегодня нельзя: день базарный; у тятеньки в лавке некому
сидеть. - И лучше, что нельзя, лучше раскаешься и поймешь, что дурить и грубить
не следует, - говорил Петр Михайлыч и поскорее уходил. Калашников его передразнивал, так что старик все слышал:
- Грубить и дурить не следует, - ту, ту, ту, тетерев! Я и без шапки
убегу; много с меня возьмешь! - говорил он и с досады отламывал закраину у
карты. Вообще строгость и крутые меры были совершенно не в характере Петра
Михайлыча. Со школьниками он еще кое-как справлялся и, в крайней
необходимости, даже посекал их, возлагая это, без личного присутствия, на
Гаврилыча и давая ему каждый раз приказание наказывать не столько для боли,
сколько для стыда; однако Гаврилыч, питавший к школьникам какую-то глубокую
ненависть, если наказуемый был только ему по силе, распоряжался так, что
тот, выскочив из смотрительской, часа два отхлипывался. Но в совершенное
затруднение становился старик, когда ему нужно было делать замечание или
выговоры учителям. Этому, впрочем, подпадал один только преподаватель
истории Экзархатов, который был человек очень неглупый, из университета. В
продолжение всего месяца он был очень тих, задумчив, старателен, очень
молчалив и предмет свой знал прекрасно; но только что получал жалованье, на
другой же день являлся в класс развеселый; с учениками шутит, пойдет потом
гулять по улице - шляпа набоку, в зубах сигара, попевает, насвистывает,
пожалуй, где случай выпадет, готов и драку сочинить; к женскому полу
получает сильное стремление и для этого придет к реке, станет на берегу
около плотов, на которых прачки моют белье, и любуется... Посуда, окна,
домашние не попадайся: исколотит. А проспится, опять тише его нет. Еще в
Москве он женился на какой-то вдове, бог знает из какого звания, с пятерыми
детьми, - женщине глупой, вздорной, по милости которой он, говорят, и пить
начал. Во все время, покуда кутит муж, Экзархатова убегала к соседям; но
когда он приходил в себя, принималась его, как ржа железо, есть, и
достаточно было ему сказать одно слово - она пустит в него чем ни попало,
растреплет на себе волосы, платье и побежит к Петру Михайлычу жаловаться,
прямо ворвется в смотрительскую и кричит:
- Батюшка, Петр Михайлыч, сделайте божескую милость! Что это такое?.. Батюшка!.. - Что такое случилось? Что вам угодно от меня? - спрашивает Годнев,
хотя очень хорошо знал, что такое случилось. - Известно что: двои сутки пил! Что хошь, то и делайте. Нет моей
силушки: ни ложки, ни плошки в доме не стало: все перебил; сама еле жива
ушла; третью ночь с детками в бане ночую. - Боже мой! Боже мой! - говорил Петр Михайлыч, пожимая плечами. - Вы,
сударыня, успокойтесь; я ему поговорю и надеюсь, что это будет в последний
раз. - Батюшка, да ты хорошенько с него спроси; нельзя ли как-нибудь... хошь
бы ты посек его. - Как это можно, сударыня! Вам и говорить этого не следует, - возражал
Петр Михайлыч. - Гаврилыч! - кричал он. - Подите и попросите ко мне господина
Экзархатова. И Экзархатов являлся, немного сутуловатый, в потертом вицмундире, с
лицом истощенным, с синяком на левом глазу... вообще фигура очень печальная. - Вы, Николай Иваныч, опять вашей несчастной страсти начинаете
предаваться! Сами, я думаю, знаете греческую фразу: "Пьянство есть небольшое
бешенство!" И что за желание быть в полусумасшедшем состоянии! С вашим умом,
с вашим образованием... нехорошо, право, нехорошо! - Виноват, Петр Михайлыч, сам очень хорошо чувствую, - отвечал
Экзархатов и еще ниже потуплял голову. - Ты, рожа этакая безобразная! - вмешивалась Экзархатова, не стесняясь
присутствием смотрителя. - Только на словах винишься, а на сердце ничего не
чувствуешь. Пятеро у тебя ребят, какой ты поилец и кормилец! Не воровать
мне, не по миру идти из-за тебя! - Так, так, - говорил Годнев, качая головой. - Виноват, Петр Михайлыч, - повторял Экзархатов. - Верю, верю вашему раскаянию и надеюсь, что вы навсегда исправитесь. Прошу вас идти к вашим занятиям, - говорил Петр Михайлыч. - Ну вот,
сударыня, - присовокупил он, когда Экзархатов уходил, - видите, не
помиловал; приличное наставление сделал: теперь вам нечего больше
огорчаться. Но Экзархатова не оставалась этим довольна. - А что мне не огорчаться-то? Что вы ему сделали?.. По головке еще
погладили пса этакова? - говорила она. - Ай, ай, ай! Как это стыдно даме такие слова говорить! - возражал Петр
Михайлыч. - Супруги должны недостатки друг у друга исправлять любовью и
кротостью, а не бранью. - Тьфу мне на его любовь - вот он, криворожий, чего стоит! - возражала
Экзархатова. - Кабы знала, так бы не ходила, потатчики этакие! -
присовокупляла она, уходя. Петр Михайлыч усмехался и говорил сам с собой:
- Характерная женщина! Ах, какая характерная! Сгубила совсем человека;
а какой малый-то бесподобный! Что ты будешь делать? Проходя из училища домой, Петр Михайлыч всегда был очень рад, когда
встречал кого-нибудь из знакомых помещиков, приехавших на время в город. - Остановитесь на минуточку! - кричал он. Помещик останавливался. - Надолго ли? - спрашивал Петр Михайлыч. - До завтра. - А сегодня никуда не званы обедать? - Нет, ни у кого еще не был. - Так что же, приезжайте щей откушать; а если нет, так рассержусь,
право рассержусь. С год уж мы не видались. - Благодарю вас. Буду, если позволите. Сейчас только в суд заеду. - Добре, добре, вот это по-нашему, по-приятельски. До свиданья, -
говорил Петр Михайлыч. Против этой его привычки приглашать к себе обедать постоянно восставала
Палагея Евграфовна. - А что, мать-командирша, что мы будем сегодня обедать? - спрашивал он,
приходя домой. - Будете сыты, не беспокойтесь. - То-то; я пригласил одного человека... - Что это, Петр Михайлыч, никогда заблаговременно не скажете, и что у
вас все гости да гости! Не напасешься ничего, да и только. - Ну, ну, полно, командирша, ворчать! Кто не любит разделить своей
трапезы с приятелем, тот человек жадный. Впрочем, и Палагее Евграфовне было не жаль: она не любила только, когда
ее заставали, как она выражалась, неприпасенную. Кроме случайных
посетителей, у Петра Михайлыча был один каждодневный - родной его брат,
отставной капитан Флегонт Михайлыч Годнев. Капитан был холостяк, получал сто
рублей серебром пенсиона и жил на квартире, через дом от Петра Михайлыча, в
двух небольших комнатках. В противоположность разговорчивости и
обходительности Петра Михайлыча, капитан был очень молчалив, отвечал только
на вопросы и то весьма односложно. Он очень любил птиц, которых держал
различных пород до сотни; кроме того, он был охотник ходить с ружьем за
дичью и удить рыбу; но самым нежнейшим предметом его привязанности была
легавая собака Дианка. Он с ней спал, мыл ее, никогда с ней не разлучался и
по целым часам глядел на нее, когда она лежала под столом развалившись, а
потом усмехался. - Чему это, капитан, вы смеетесь? - спрашивал его Петр Михайлыч. Он
всегда называл брата "капитаном". - Да вон-с, Дианка спит, - отвечал тот. Постоянный костюм капитана был форменный военный вицмундир. Курил он, и
курил очень много, крепкий турецкий табак, который вместе с пенковой
коротенькой трубочкой носил всегда с собой в бисерном кисете. Кисет этот
вышила ему Настенька и, по желанию его, изобразила на одной стороне казака,
убивающего турка, а на другой - крепость Варну. Каждодневно, за полчаса да
прихода Петра Михайлыча, капитан являлся, раскланивался с Настенькой,
целовал у ней ручку и спрашивал о ее здоровье, а потом садился и молчал. - Что ж вы не курите? - говорила Настенька, чтоб занять его чем-нибудь. - А вот-с покурю, - отвечал капитан и набивал свою коротенькую
трубочку, высекал огонь к труту собственного изделия из толстой сахарной
бумаги и начинал курить. - Здравствуйте, капитан! - говорил приходя Петр Михайлыч. Капитан вставал и почтительно ему кланялся. Из одного этого поклона
можно было заключить, какое глубокое уважение питал капитан к брату. За
столом, если никого не было постороннего, говорил один только Петр Михайлыч;
Настенька больше молчала и очень мало кушала; капитан совершенно молчал и
очень много ел; Палагея Евграфовна беспрестанно вскакивала. После обеда
между братьями всегда почти происходил следующий разговор:
- Куда это путь изволите направлять: верно, на птиц своих посмотреть? -
говорил Петр Михайлыч, когда капитан, выкурив трубку, брался за фуражку. - Да-с, нужно побывать, - отвечал тот. - С богом! Вечером будете? - Буду-с, - отвечал капитан и уходил, а вечером действительно являлся к
самому чаю с своими обычными атрибутами: кисетом, трубкой и Дианкой. После чаю обыкновенно начиналось чтение. Капитан по преимуществу любил
книги исторического и военного содержания; впрочем, он и все прочее слушал
довольно внимательно, и, когда Дианка проскулит что-нибудь во сне, или
сильно начнет чесать лапой ухо, или заколотит хвостом от удовольствия, он
всегда погрозит ей пальцем и проговорит тихим голосом: "куш!"
В праздничные дни жизнь Годневых принимала несколько другой характер. Петр Михайлыч, в своей вседневной, старой бекеше и в старой фуражке,
отправлялся обыкновенно к заутрени в свой приход, куда также являлся и
Флегонт Михайлыч. После службы братья расходились по домам. К обедне Петр
Михайлыч шел уже с Настенькой и был одет в новую шинель и шляпу и средний
вицмундир; капитан являлся тоже в среднем вицмундире. Отслушав литургию,
братья подходили к кресту, потом целовались и поздравляли друг друга с
праздником. Капитан, кроме того, подходил к Настеньке, справлялся, по
обыкновению, о ее здоровье и поздравлял ее с праздником. Из церкви вся семья
отправлялась домой, где для них Палагея Евграфовна приготовляла кофе. По
праздникам Петр Михайлыч был еще спокойнее, еще веселее. - Не угодно ли вам, возлюбленный наш брат, одолжить нам вашей трубочки
и табачку? - говорил он, принимаясь за кофе, который пил один раз в неделю и
всегда при этом выкуривал одну трубку табаку. Эта просьба брата всегда доставляла капитану большое наслаждение. Он
старательно выдувал свою трубочку, аккуратно набивал табак и, положив
зажженного труту, подносил Петру Михайлычу, который за это целовал его. Известие об отставке Годнева удивило весь город. - Вы, Петр Михайлыч, в отставку вышли? - говорили ему. - Да, сударь, - отвечал он. - Что же вам вздумалось? - А что же? Будет с меня, послужил! - Да ведь вы бы двойной оклад получали? - Зачем мне двойной оклад? У меня, слава богу, кусок хлеба есть:
проживу как-нибудь.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
