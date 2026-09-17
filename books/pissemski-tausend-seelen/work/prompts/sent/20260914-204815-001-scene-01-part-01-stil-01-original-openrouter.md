# Gesendeter Prompt 001

- Zeitstempel: 20260914-204815
- Provider: openrouter
- Modell: deepseek/deepseek-v4.1-flash
- Stil: stil-01-original
- Kapitel: 001
- Szene: 01
- Chunk: 01/02
- Temperatur: 0.2
- max_tokens: 12000
- System-Zeichen: 5046
- User-Zeichen: 13385

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

Interne Arbeitsportion 1/2 derselben Szene. Uebersetze nur diesen Abschnitt fortlaufend ins Deutsche. Keine neue Szenenueberschrift erzeugen.

В приказах гражданского ведомства было, между прочим, сказано:
"Увольняется штатный смотритель эн-ского уездного училища, коллежский
асессор Годнев с мундиром и пенсионом, службе присвоенными"; потом далее:
"Определяется смотрителем эн-ского училища кандидат Калинович". Прочитав этот приказ, автор невольно задумался. "Увы! - сказал он сам
себе. - В мире ничего нет прочного. И Петр Михайлыч Годнев больше не
смотритель, тогда как по точному счету он носил это звание ровно двадцать
пять лет. Что-то теперь старик станет поделывать? Не переменит ли образа
своей жизни и где будет каждое утро сидеть с восьми часов до двух вместо
своей смотрительской каморы?"
В Эн-ске Годнев имел собственный домик с садом, а под городом тридцать
благоприобретенных душ. Он был вдов, имел дочь Настеньку и экономку Палагею
Евграфовну, девицу лет сорока пяти и не совсем красивого лица. Несмотря на
это, тамошняя исправница, дама весьма неосторожная на язык, говорила, что
ему гораздо бы лучше следовало на своей прелестной ключнице жениться, чтоб
прикрыть грех, хотя более умеренное мнение других было таково, что какой уж
может быть грех у таких стариков, и зачем им жениться? Петра Михайлыча знали не только в городе и уезде, но, я думаю, и в
половине губернии: каждый день, часов в семь утра, он выходил из дома за
припасами на рынок и имел, при этом случае, привычку поговорить со встречным
и поперечным. Проходя, например, мимо полуразвалившегося домишка
соседки-мещанки, в котором из волокового окна{4} выглядывала голова хозяйки,
повязанная платком, он говорил:
- Здравствуй, Фекла Никифоровна. - Здравствуйте, батюшка Петр Михайлыч, - отвечала та. - Давно ли из губернии воротилась? - Вчерашним днем, сударь, прибыла. Не на конной, батюшка, подводе,
пешком отшлепала по экой по грязи. - Как дела-то идут? - Дела мои, Петр Михайлыч, по начальству пошли. - Ну, коли по начальству, так хорошо. - Да хорошо ли, отец мой? - Хорошо... хорошо... - говорил Годнев, идя далее. Сказать правду, Петр Михайлыч даже и не знал, в чем были дела у
соседки, и действительно ли хорошо, что они по начальству пошли, а говорил
это только так, для утешения ее. У каменного купеческого дома стоял кучер в накинутом на плечи
полушубке, и его Петр Михайлыч считал за нужное обласкать. - Что, брат, объездил ли лошадку-то? - спрашивал он. - Нешто-с... выламывается поманеньку, - отвечал тот. - Видел я... видел... Ты молодец... ловкий ездок! Кучер самодовольно улыбался. Мясную лавку, куда шел Годнев, купец только еще отпирал. - Эге, Силиверст Петрович, поздненько нынче выплыл, - говорил Годнев. - Что делать, Петр Михайлыч! Позамешкался грешным делом, - отвечал
купец. - Что парнишко-то мой: как там у вас? - прибавлял он, уходя за
прилавок. - Что парнишко? Ничего, хорошо: способности есть; резов только; вчера
опять два стекла в классе вышиб, - отвечал Петр Михайлыч. - Фу ты, господи, твоя воля! - восклицал купец, пожимая плечами. - Что
только мне с этим парнем делать - ума не приложу; спуску, кажись, не даю ему
ни в чем, а хошь ты брось! - Ну, зачем же? Чересчур не надобно: хуже заколотишь. - Заколотишь его, пострела, как бы не так! - возражал купец и потом
прибавлял: - Говядинки, что ли, прикажете отвесить? - Да, сударь, хоть говядинки; смотри, только помягче. - Неужели жесткой! Худой вам не отпустим... худое мы про генеральш
здешних бережем. - Ну, вот уж и про генеральш! Экой вы, торговый народ, зубоскалы! - Право, так. Не знаем только, куда эта барыня с почтмейстером деньги
берегут. Петр Михайлыч только усмехался и качал головой. Из мясной лавки он проходил во внутренность гостиного двора, где
торговки торговали калачами, горшками, зеленью, нитками и разного рода
другими припасами. - Ты, луковница, опять с своим товаром выехала! - говорил Петр Михайлыч
бабе, около которой стояла большая корзина с луком. Он терпеть не мог луку. - Полно-ка, полно, старый барин хороший, на почине оговаривать,
возьми-ка лучше прядку да и разговаривай. - Дура, я не ем луку. - То-то вы, баря: "луку не ем", все бы вам сахару. - Ну, уж не сердчай, давай прядочку, - говорил Годнев и покупал лук,
который тотчас же отдавал первому попавшемуся нищему, говоря: - На-ка лучку! Только без хлеба не ешь: горько будет... Поди ко мне на двор: там тебе хлеба
дадут, поди! Навстречу ему шел священник. Петр Михайлыч еще издали ему кланялся. - Здравствуйте, - говорил он, снимая картуз и подходя к благословению. - Здравствуйте, - отвечал тот густым басом. - Что, отче, прочли мою книжку али еще нет? - Прочел и намеревался сего же дня возвратить ее с моею благодарностью. Приятное сочинение. - Да, да, поучительная книга... Занесите как-нибудь. - Непременно, - отвечал священник и истово раскланивался. Возвратившись домой, Петр Михайлыч проходил прямо на кухню, где
стряпуха, под личным надзором Палагеи Евграфовны, затапливала уж печь. - Вот тебе, командирша, снеди и блага земные! - говорил он, подавая
экономке кулек, который та, приняв, начинала вынимать из него запас, качая
головой и издавая восклицания вроде: "Э... э... э... хе, хе, хе..."
- Ну, заворчала! Эх ты, ворчунья, сударыня... Дурно, что ли, купил? - Хорошо, - отвечала на это Палагея Евграфовна насмешливым тоном. Она никогда не оставалась покупками Петра Михайлыча довольною и была в
этом совершенно права: приятели купцы то обвешивали его, то продавали ему
гнилое за свежее, тогда как в самой Палагее Евграфовне расчетливое хозяйство
и чистоплотность были какими-то ненасытными страстями. Будучи родом из
каких-то немок, она, впрочем, ни на каком языке, кроме русского, пикнуть не
умела. Приехав неизвестно как и зачем в уездный городишко, сначала чуть было
не умерла с голоду, потом попала в больницу, куда придя Петр Михайлыч и
увидев больную незнакомую даму, по обыкновению разговорился с ней; и так как
в этот год овдовел, то взял ее к себе ходить за маленькой Настенькой. Но
Палагея Евграфовна, вступив нянькой, прибрала мало-помалу к своим рукам и
все домоправление. С самого раннего утра до поздней ночи она мелькала то
тут, то там по разным хозяйственным заведениям: лезла зачем-то на сеновал,
бегала в погреб, рылась в саду; везде, где только можно было, обтирала,
подметала и, наконец, с восьми часов утра, засучив рукава и надев передник,
принималась стряпать - и надобно отдать ей честь: готовить многие кушанья
была она великая мастерица. Особенно хороши выходили у ней все соленые и
маринованные приготовления; коренная рыба{6}, например, заготовляемая ею в
великий пост, была такова, что Петр Михайлыч всякий раз, когда ел ее в
летние жары с ботвиньей, говорил:
- Этакой, господа, рыбы и ботвиньи сам Лукулл{6} не едал! Манишки и шейные платки для Петра Михайлыча, воротнички, нарукавнички и
модести{6} для Настеньки Палагея Евграфовна чистила всегда сама и сама бы,
кажется, если б только сил ее доставало, мыла и все прочее, потому что, по
собственному ее выражению, у нее кровью сердце обливалось, глядя на вымытое
прачкою белье. Когда спала и чем была сыта Палагея Евграфовна - определить было
довольно трудно, и она даже не любила, если ей напоминали об этом. Чай пила
как-то урывками, за стол (хоть и накрывался для нее всегда прибор) садилась
на минуточку; только что подавалось горячее, она вдруг вскакивала и уходила
за чем-то в кухню, и потом, когда снова появлялась и когда Петр Михайлыч ей
говорил: "Что же ты сама, командирша, никогда ничего не кушаешь?", Палагея
Евграфовна только усмехалась и, ответив: "Кабы не ела, так и жива бы не
была", снова отправлялась на кухню. Жалованье (сто двадцать рублей ассигнациями в год) Палагея Евграфовна
всегда принимала с некоторым принуждением. В конце каждого месяца Петр
Михайлыч приносил ей обыкновенно десять рублей. - Это что еще? - говорила экономка. - Деньги ваши. Деньги - вещь хорошая. Не угодно ли получить и
расписаться? - отвечал тот. - Э... перестаньте с вашими глупостями! - говорила, отворачиваясь,
экономка и начинала смотреть в окно. - Порядок, мать-командирша, не глупость. Изволь взять! - говорил Годнев
настоятельнее. - Точно я у вас не сыта, не одета, - говорила Палагея Евграфовна и
продолжала смотреть в окно. - Изволь, изволь брать; знаешь, не люблю! - говорил Годнев еще
настоятельнее. Палагея Евграфовна сердито брала деньги и с пренебрежением кидала их в
рабочий ящик. Всякий раз при этой сцене, несмотря на недовольное выражение лица, у
ней навертывались на глазах слезы. - Взял нищую с дороги, не дал с голоду умереть да еще жалованье
положил, бесстыдник этакой! У самого дочка есть: лучше бы дочке что-нибудь
скопил! - ворчала она себе под нос. - А ты мне этого, командирша, не смей и говорить, - слышишь ли? Тебе
меня не учить! - прикрикивал на нее Петр Михайлыч, и Палагея Евграфовна
больше не говорила, но все-таки продолжала принимать жалованье с
неудовольствием. Передав запас экономке, Петр Михайлыч отправлялся в гостиную и садился
пить чай с Настенькой. Разговор у отца с дочерью почти каждое утро шел
такого рода:
- Вы, Настасья Петровна, опять до утра засиделись... Нехорошо, моя
милушка, право, нехорошо... надо давать время занятиям, время отдыху и время
сну. - Я зачиталась, папенька. Вчерашнюю повесть я уж кончила. - И то дурно: что ж мы будем сегодня читать? Вот вечером и нечего
читать. - Нет, я вам ее дочитаю, я с удовольствием прочту ее еще раз; и
вообразите себе, Валентин этот вышел ужасно какой дурной человек. - Ну, ну, не рассказывай! Изволь-ка мне лучше прочесть: мне приятнее от
автора узнать, как и что было, - перебивал Петр Михайлыч, и Настенька не
рассказывала. После этого они обыкновенно расходились. Настенька садилась или читать,
или переписывать что-нибудь, или уходила в сад гулять. Ни хозяйством, ни
рукодельем она не занималась. Петр Михайлыч, в свою очередь, надевал
форменный вицмундир и шел в училище. В прихожей обыкновенно встречал его
сторож, отставной солдат Гаврилыч, прозванный школьниками за необыкновенно
рябое лицо "Теркой". Надобно было иметь истинно христианское терпение Петра
Михайлыча, чтобы держать Гаврилыча в продолжение десяти лет сторожем при
училище, потому что инвалид, по старости лет, был и глуп, и ленив, и груб;
никогда почти ничего не прибирал, не чистил, так что Петр Михайлыч принужден
был, по крайней мере раз в месяц, нанимать на свой счет поломоек для
приведения здания училища в надлежащий порядок. Кроме того, у сторожа была
любимая привычка позавтракать рано поутру разогретыми щами, которые он
обыкновенно и становил с вечера в смотрительской комнате в печку на целую
ночь. Петр Михайлыч, почти каждый раз, приходя поутру, говорил:
- Ты, гренадер, опять щи парил. Экую душину напустил! Смотри-ка: не
дохнешь! - Ну да, парил, у тебя все парил! - возражал Гаврилыч. - Да как же не парил! Еще запираешься, лжешь на старости лет,
греховодник! - Погляди сам в печку, так, може, и увидишь, что тамотка ничего нет. - Знаю, что в печке ничего нет: съел! И сало-то еще с рыла не вытер,
дурак!.. Огрызается туда же! Прогоню, так и знаешь... шляйся по миру! - Гони! Словно миром не живут, - отвечал Терка и уходил. - Дурак! - повторял ему вслед Петр Михайлыч. Впрочем, тем все и кончалось. Занявшись в смотрительской составлением отчетов и рапортов, во время
перемены классов Петр Михайлыч обходил училище и начинал, как водится, с
первого класса, в котором, тоже, как водится, была пыль столбом. - Ах вы, эфиопы! Татарская орда! А?.. Тише!.. Молчать!.. Чтобы муха
пролетала, слышно у меня было! - говорил старик, принимая строгий вид. В классе несколько утихало. - Зашумите вы у меня еще раз! Всех переберу - из девяти возьму десятого
на выдержку! - заключал он торжественно и уходил. В коридоре прямо летел на него сорванец и чуть не сшибал его с ног. - Что ты? Что ты, братец? - говорил, разводя руками, Петр Михайлыч. -
Этакая лошадь степная! Вот я на тебя недоуздок надену, погоди ты у меня! - Петр Михайлыч, меня Модест Васильич без обеда оставил; я не
виноват-с! - говорил третьего класса ученик Калашников, парень лет
восьмнадцати, дюжий на взгляд, нечесаный, неумытый и в чуйке. - Когда оставил, стало, ты это заслужил, - возражал ему Петр Михайлыч.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
