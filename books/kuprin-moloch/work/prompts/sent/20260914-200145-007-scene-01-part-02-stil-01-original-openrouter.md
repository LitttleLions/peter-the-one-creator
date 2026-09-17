# Gesendeter Prompt 007

- Zeitstempel: 20260914-200145
- Provider: openrouter
- Modell: deepseek/deepseek-v4.1-flash
- Stil: stil-01-original
- Kapitel: 007
- Szene: 01
- Chunk: 02/03
- Temperatur: 0.2
- max_tokens: 12000
- System-Zeichen: 5037
- User-Zeichen: 10297

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

Потом Шелковников повел гостей в сарай пудлинговых печей, - высокое железное здание такой длины, что с одного его конца другой конец казался едва заметным просветом. Вдоль одной из стен сарая тянулась каменная платформа, на которой помещалось двадцать пудлинговых печей, формой напоминавших снятые с колес вагоны. В этих печах жидкий чугун смешивался с рудой и перерабатывался в сталь. Готовая сталь, стекая вниз по трубам, наполняла собой высокие железные штамбы - нечто вроде футляров без дна, но с ручками наверху - и застывала в них сплошными кусками, пудов по сорока весом. Свободная сторона сарая была занята рельсовым путем, по которому сновали, пыхтя, шипя и стуча, паровые краны, похожие на послушных и ловких животных, снабженных гибкими хоботами. Один кран хватал штамбу крючком за ручку, поднимал ее кверху, и из нее тяжело вываливался кусок стали в виде длинного правильного бруска ослепительно красного цвета. Но прежде чем этот кусок успевал упасть на землю, рабочий с необыкновенной ловкостью обматывал его цепью в руку толщиной. Второй кран, ухватив крючком эту цепь, плавно нес "штуку" в воздухе и клал рядом с другими на платформу, прикрепленную к третьему крану. Третий - влек этот груз на другой конец сарая, где четвертый, снабженный вместо крючка щипцами, снимал "штуки" с вагона и опускал их в раскрытые люки газовых печей, устроенных под полом. Наконец пятый кран вытаскивал их из этих люков совершенно белыми от жара, клал поочередно под круглое колесо с острыми зубьями, вращавшееся чрезвычайно быстро на горизонтальной оси, и сорокапудовая стальная "штука" в течение пяти секунд разрезалась на две половины, как кусок мягкого пряника. Каждая половина поступала под семисотпудовый пресс парового молота, обжимавшего ее с такой силой и такой легкостью, точно она была из воска. Рабочие подхватывали ее тотчас же на ручные тележки и бегом тащили дальше, обдавая всех встречных блеском и жаром раскаленного железа.

Затем Шелковников показал своим гостям рельсопрокатный цех. Огромный брусок раскаленного металла проходил через целый ряд станков, катясь от одного к другому по валикам, которые вращались под полом, виднеясь на его поверхности только самой верхней своей частью. Брусок втискивался в отверстие, образуемое двумя стальными, вертевшимися в разные стороны цилиндрами, и пролезал между ними, заставляя их раздаваться и дрожать от напряжения. Дальше его ждал станок с еще меньшим отверстием между цилиндрами. Кусок стали делался после каждого станка все тоньше и длиннее и, несколько раз перебежав рельсопрокатку взад и вперед, принимал мало-помалу форму десятисаженного красного рельса. Сложным движением пятнадцати станков управлял всего один человек, помещавшийся над паровой машиной, на возвышении вроде капитанского мостика. Он двигал рукоятку вперед, и все цилиндры и валики начинали вертеться в одну сторону; двигал ее назад - и цилиндры и валики вертелись в обратную сторону. Когда рельс окончательно вытягивался, круглая пила, оглушительно визжа и сыпля фонтаном золотых искр, разрезала его на три части.

Затем все перешли в токарный цех, где главным образом отделывались вагонные и паровозные колеса. Кожаные приводы спускались там с потолка от толстого стального стержня, проходившего через весь сарай, и приводили в движение сотни две или три станков самых разных величин и фасонов. Этих приводов было так много, и они перекрещивались во стольких направлениях, что производили впечатление одной сплошной, запутанной и дрожащей ременной сети. Колеса некоторых станков вращались с быстротой двадцати оборотов в секунду, движение же других было так медленно, что почти не замечалось глазом. Стальные, железные и медные стружки, в виде красивых длинных спиралей, густо покрывали пол. Сверлильные станки оглашали воздух нестерпимым, тонким и резким визжанием. Там же была показана гостям машина, работающая гайки, - нечто вроде двух огромных стальных регулярно чавкающих челюстей. Двое рабочих всовывали в эту пасть конец накаленного длинного прута, и машина, равномерно отгрызая по куску металла, выплевывала их на землю в виде совершенно готовых гаек.

Когда, выйдя из токарного цеха, Шелковников предложил акционерам (он все время исключительно к ним обращался со своими разъяснениями) осмотреть гордость завода, девятисотсильный "Компаунд", то петербургские господа уже в достаточной степени были оглушены и расстроены всем виденным и слышанным. Новые впечатления не внушали им более никакого интереса, а только еще сильнее утомляли их. Лица их пылали от жара рельсопрокатки, руки и костюмы были перепачканы угольной сажей. На предложение директора они согласились, по-видимому, скрепя сердце, чтобы только не уронить достоинства уполномочившего их собрания.

Девятисотсильный "Компаунд" помещался в отдельном здании, очень чистеньком и нарядном, со светлыми окнами и мозаичным полом. Несмотря на громадность машины, она почти не издавала стука... Два поршня, в четыре сажени каждый, мягко и быстро ходили в цилиндрах, обитых деревянными планками. Двадцатифутовое колесо, со скользящими по нем двенадцатью канатами, вращалось также беззвучно и быстро; от его широкого движения суховатый жаркий воздух машинного отделения колебался сильными, равномерными порывами. Эта машина приводила в движение и воздуходувки, и прокатные станки, и все машины токарного цеха.

Осмотрев "Компаунд", акционеры были уже совершенно убеждены, что их испытания окончились, но неутомимый Шелковников вдруг обратился к ним с новым любезным предложением:

- Теперь, господа, я вам покажу сердце всего завода, тот пункт, от которого он получает свою жизнь.

Он не повел, а почти повлек их в отделение паровых котлов. Однако после всего виденного "сердце завода" - двенадцать цилиндрических котлов пятисаженной длины и полутора сажен высоты каждый - не произвело на уставших акционеров особенно внушительного впечатления. Их мысли давно вращались вокруг ожидавшего их обеда, и они уже ничего не расспрашивали, как раньше, а только рассеянно и равнодушно кивали головами на все разъяснения Шелковникова. Когда директор кончил, акционеры вздохнули с облегчением и очень искренно, с нескрываемым удовольствием принялись жать ему руку.

Теперь только один Андрей Ильич остался около паровых котлов. Стоя на краю глубокой полутемной каменной ямы, в которой помещались топки, он долго глядел вниз на тяжелую работу шестерых обнаженных до пояса людей. На их обязанности лежало беспрерывно, и днем и ночью, подбрасывать каменный уголь в топочные отверстия. То и дело со звоном отворялись круглые чугунные заслонки, и тогда видно было, как в топках с гудением и ревом клокотало ярко-белое бурное пламя. То и дело голые тела рабочих, высушенные огнем, черные от пропитавшей их угольной пыли, нагибались вниз, причем на их спинах резко выступали все мускулы и все позвонки спинного хребта. То и дело худые, цепкие руки набирали полную лопатку угля и затем быстрым, ловким движением всовывали его в раскрытое пылающее жерло. Двое других рабочих, стоя наверху и также не останавливаясь ни на мгновение, сбрасывали вниз все новые и новые кучи угля, который громадными черными валами возвышался вокруг котельного отделения. Что-то удручающее, нечеловеческое чудилось Боброву в бесконечной работе кочегаров. Казалось, какая-то сверхъестественная сила приковала их на всю жизнь к этим разверстым пастям, и они, под страхом ужасной смерти, должны были без устали кормить и кормить ненасытное, прожорливое чудовище...

- Что, коллега, смотрите, как вашего Молоха упитывают? - услышал Бобров за своей спиной веселый, добродушный голос.

Андрей Ильич задрожал и чуть-чуть не полетел в кочегарную яму. Его поразило, почти потрясло это неожиданное соответствие шутливого восклицания доктора с его собственными мыслями. Даже и овладев собою, он долго не мог отделаться от странности такого совпадения. Его всегда интересовали и казались ему загадочными те случаи, когда, задумавшись о каком-нибудь предмете или читая о чем-нибудь в книге, он тотчас же слышал рядом с собою разговор о том же самом.

- Я вас, кажется, напугал, дорогой мой? - спросил доктор, внимательно заглянув в лицо Боброва. - Прошу прощения.

- Да, немножко... вы так неслышно подошли... я совсем не ожидал.

- Ох, батенька Андрей Ильич, давайте-ка полечим наши нервы. Никуда они у нас не годятся... Послушайтесь моего совета: берите отпуск да махните куда-нибудь за границу... Ну, что вам себя здесь растравлять? Поживите полгодика в свое удовольствие: пейте хорошее вино, ездите верхом побольше, насчет ламура [ любви (от франц. l'amour) ] пройдитесь...

Доктор подошел к краю кочегарки.

- Вот так преисподняя! - воскликнул он, заглянув вниз. - Сколько каждый такой самоварчик должен весить? Пудов восемьсот, я думаю?..

- Нет, побольше. Тысячи полторы.

- Ой, ой, ой... А ну как такая штучка вздумает того... лопнуть? Эффектное выйдет зрелище? А?

- Очень эффектное, доктор. Наверно, от всех этих зданий не останется камня на камне...

Гольдберг покачал головой и многозначительно свистнул.

- Отчего же это может случиться?

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
