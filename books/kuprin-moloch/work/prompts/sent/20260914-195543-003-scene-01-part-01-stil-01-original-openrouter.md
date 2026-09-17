# Gesendeter Prompt 003

- Zeitstempel: 20260914-195543
- Provider: openrouter
- Modell: deepseek/deepseek-v4.1-flash
- Stil: stil-01-original
- Kapitel: 003
- Szene: 01
- Chunk: 01/02
- Temperatur: 0.2
- max_tokens: 12000
- System-Zeichen: 5037
- User-Zeichen: 9822

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

Interne Arbeitsportion 1/2 derselben Szene. Uebersetze nur diesen Abschnitt fortlaufend ins Deutsche. Keine neue Szenenueberschrift erzeugen.

Вернувшись с завода и наскоро пообедав, Бобров вышел на крыльцо. Кучер Митрофан, еще раньше получивший приказание оседлать Фарватера, гнедую донскую лошадь, с усилием затягивал подпругу английского седла. Фарватер надувал живот и несколько раз быстро изгибал шею, ловя зубами рукав Митрофановой рубашки. Тогда Митрофан кричал на него сердитым и ненатуральным басом: "Но-о! Балуй, идол!" - и прибавлял, кряхтя от напряжения: "Ишь ты, животная".

Фарватер - жеребец среднего роста, с массивною грудью, длинным туловищем и поджарым, немного вислым задом - легко и стройно держался на крепких мохнатых ногах, с надежными копытами и тонкой бабкой. Знаток остался бы недоволен его горбоносой мордой и длинной шеей с острым, выдающимся кадыком. Но Бобров находил, что эти особенности, характерные для всякой донской лошади, составляют красоту Фарватера так же, как кривые ноги у таксы и длинные уши у сеттера. Зато во всем заводе не было лошади, которая могла бы обскакать Фарватера.

Хотя Митрофан и считал необходимым, как и всякий хороший русский кучер, обращаться с лошадью сурово, отнюдь не позволяя ни себе, ни ей никаких проявлений нежности, и поэтому называл ее и "каторжной", и "падалью", и "убивцею", и даже "хамлетом", тем не менее он в глубине души страстно любил Фарватера. Эта любовь выражалась в том, что донской жеребчик был и вычищен лучше и овса получал больше, чем другие казенные лошади Боброва: Ласточка и Черноморец.

- Поил ты его, Митрофан? - спросил Бобров.

Митрофан ответил не сразу. У него была и еще одна повадка хорошего кучера - медлительность и степенность в разговоре.

- Попоил, Андрей Ильич, как же не попоимши-то. Но, ты, озирайся, леший! Я тебе поверчу морду-то! - крикнул он сердито на лошадь. - Страсть, барин, как ему охота нынче под седлом идти. Не терпится.

Едва только Бобров подошел к Фарватеру и, взяв в левую руку поводья, обмотал вокруг пальцев гривку, как началась история, повторявшаяся чуть ли не ежедневно. Фарватер, уже давно косившийся большим сердитым глазом на подходившего Боброва, начал плясать на месте, выгибая шею и разбрасывая задними ногами комья грязи. Бобров прыгал около него на одной ноге, стараясь вдеть ногу в стремя.

- Пусти, пусти, поводья, Митрофан! - крикнул он, поймав, наконец, стремя, и в тот же момент, перебросив ногу через круп, очутился в седле.

Почувствовав шенкеля всадника. Фарватер тотчас же смирился и, переменив несколько раз ногу, фыркая и мотая головой, взял от ворот широким, упругим галопом...

Быстрая езда, холодный ветер, свистевший в уши, свежий запах осеннего, слегка мокрого поля очень скоро успокоили и оживили вялые нервы Боброва. Кроме того, каждый раз, отправляясь к Зиненкам, он испытывал приятный и тревожный подъем духа.

Семья Зиненок состояла из отца, матери и пятерых дочерей. Отец служил на заводе и заведовал складом. Этот ленивый и добродушный с виду гигант был в сущности очень пронырливым и каверзным господином. Он принадлежал к числу тех людей, которые под видом высказывания всякому в глаза "истинной правды" грубо, но приятно льстят начальству, откровенно ябедничают на сослуживцев, а с подчиненными обращаются самым безобразно-деспотическим образом. Он спорил из-за всякого пустяка, не слушая возражений и хрипло крича; любил поесть и питал слабость к хоровому малорусскому пению, причем неизменно фальшивил. Он, незаметно для самого себя, находился под башмаком у своей жены, - женщины маленького роста, болезненной и жеманной, с крошечными серыми глазками, до смешного близко поставленными к переносью.

Дочерей звали: Мака, Бета, Шурочка, Нина и Кася.

Каждой из них в семье было отведено свое амплуа, Мака, девица с рыбьим профилем, пользовалась репутацией ангельского характера. "Уж эта Мака - сама простота". - говорили про нее родители, когда она во время прогулок и вечеров стушевывалась на задний план в интересах младших сестер (Маке уже перевалило за тридцать).

Бета считалась умницей, носила пенсне и, как говорили, хотела даже когда-то поступить на курсы. Она держала голову склоненной набок и вниз, как старая пристяжная, и ходила ныряющей походкой, то подымаясь, то опускаясь при каждом шаге. К новым гостям она приставала со спорами о том, что женщины лучше и честнее мужчин, или с наивной игривостью просила: "Вы такой проницательный... ну вот, определите мой характер". Когда разговор переходил на одну из классических домашних тем: "Кто выше: Лермонтов или Пушкин?" или: "Способствует ли природа смягчению нравов?" - Бету выдвигали вперед, как боевого слона.

Третья дочь, Шурочка, избрала специальностью игру в дурачки со всеми холостыми инженерами по очереди. Как только узнавала она, что ее старый партнер собирается жениться, она, подавляя огорчение и досаду, избирала себе нового. Конечно, игра велась с милыми шутками и маленьким пленительным плутовством, причем партнера называли "противным" и били по рукам картами.

Нина считалась в семье общей любимицей, избалованным, но прелестным ребенком. Она была выродком среди своих сестер с их массивными фигурами и грубоватыми, вульгарными лицами. Может быть, одна только madame Зиненко могла бы удовлетворительно объяснить, откуда у Ниночки взялась эта нежная, хрупкая фигурка, эти почти аристократические руки, хорошенькое смугловатое личико, все в родинках, маленькие розовые уши и пышные, тонкие, слегка вьющиеся волосы. На нее родители возлагали большие надежды, и ей поэтому разрешалось все: и объедаться конфетами, и мило картавить, и даже одеваться лучше сестер.

Самой младшей, Касе, исполнилось недавно четырнадцать лет, но этот феноменальный ребенок перерос на целую голову свою мать, далеко превзойдя старших сестер могучей рельефностью форм. Ее фигура давно уже вызывала пристальные взоры заводской молодежи, совершенно лишенной, по отдаленности от города, женского общества, и Кася принимала эти взоры с наивным бесстыдством рано созревшей девочки.

Это разделение семейных прелестей было хорошо известно на заводе, и один шутник сказал как-то, что если уж жениться на Зиненках, то непременно на всех пятерых сразу. Инженеры и студенты-практиканты глядели на дом Зиненко, как на гостиницу, толклись там с утра до ночи, много ели, еще больше пили, но с удивительной ловкостью избегали брачных сетей.

В этой семье Боброва недолюбливали. Мещанские вкусы madame Зиненко, стремившейся все подвести под линию пошлого и благополучно-скучного провинциального приличия, оскорблялись поведением Андрея Ильича. Его желчные остроты, когда он бывал в духе, встречались с широко раскрытыми глазами, и, наоборот, когда он молчал целыми вечерами, вследствие усталости и раздражения, его подозревали в скрытности, в гордости, в молчаливом иронизировании, даже о! Это было всего ужаснее! - даже подозревали, что он "пишет в журналы повести и собирает для них типы".

Бобров чувствовал эту глухую вражду, выражавшуюся в небрежности за столом, в удивленном пожимании плечей матери семейства, но все-таки продолжал бывать у Зиненок. Любил ли он Нину? На это он сам не мог бы ответить. Когда он трое или четверо суток не бывал в их доме, воспоминание о ней заставляло его сердце биться со сладкой и тревожной грустью. Он представлял себе ее стройную, грациозную фигурку, улыбку ее томных, окруженных тенью глаз и запах ее тела, напоминавший ему почему-то запах молодых клейких почек тополя.

Но стоило ему побывать у Зиненок три вечера подряд, как его начинало томить их общество, их фразы, - всегда одни и те же в одинаковых случаях, шаблонные и неестественные выражения их лиц. Между пятью "барышнями" и "ухаживавшими" за ними "кавалерами" (слова зиненковского обихода) раз навсегда установились пошло-игривые отношения. И те и другие делали вид, будто они составляют два враждующих лагеря. То и дело один из кавалеров, шутя, похищал у барышни какую-нибудь вещь и уверял, что не отдаст ее; барышни дулись, шептались между собой, называли шутника "противным" и все время хохотали деревянным, громким, неприятным хохотом. И это повторялось ежедневно, сегодня совершенно в тех же словах и с теми же жестами, как вчера. Бобров возвращался от Зиненок с головной болью и с нервами, утомленными их провинциальным ломаньем.

Таким образом, в душе Боброва чередовалась тоска по Нине, по нервному пожатию ее всегда горячих рук, с отвращением к скуке и манерности ее семьи. Бывали минуты, когда он уже совершенно готовился сделать ей предложение. Тогда его не остановило бы даже сознание, что она, с ее кокетством дурного тона и душевной пустотой, устроит из семейной жизни ад, что он и она думают и говорят на разных языках. Но он не решался и молчал.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
