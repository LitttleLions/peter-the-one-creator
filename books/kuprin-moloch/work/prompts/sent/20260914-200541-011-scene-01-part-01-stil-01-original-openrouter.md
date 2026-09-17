# Gesendeter Prompt 011

- Zeitstempel: 20260914-200541
- Provider: openrouter
- Modell: deepseek/deepseek-v4.1-flash
- Stil: stil-01-original
- Kapitel: 011
- Szene: 01
- Chunk: 01/03
- Temperatur: 0.2
- max_tokens: 12000
- System-Zeichen: 5037
- User-Zeichen: 10154

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

Interne Arbeitsportion 1/3 derselben Szene. Uebersetze nur diesen Abschnitt fortlaufend ins Deutsche. Keine neue Szenenueberschrift erzeugen.

Началась бестолковая, нелепая сумятица. Все поднялись с мест и забегали по павильону, толкаясь, крича и спотыкаясь об опрокинутые стулья. Дамы торопливо надевали дрожащими руками шляпки. Кто-то распорядился вдобавок погасить электрические фонари, и это еще больше усилило общее смятение... В темноте послышались истерические женские крики.

Было около пяти часов. Солнце еще не всходило, но небо заметно посветлело, предвещая своим серым, однообразным тоном начало ненастного дня. Бледный, тусклый, однообразный полусвет занимающегося утра, так быстро и неожиданно сменивший яркое сияние электричества, придавал картине общего смятения страшный, удручающий, почти фантастический характер. Человеческие фигуры казались привидениями из какой-то фантастической, бредовой сказки. Измятые бессонной ночью, взволнованные лица были страшны. Обеденный стол, залитый вином и беспорядочно загроможденный посудой, напоминал о каком-то чудовищном, внезапно прерванном пиршестве.

Около экипажей суматоха была еще безобразнее: испуганные лошади храпели, взвивались на дыбы и не давались зануздывать; колеса сцеплялись с колесами, и слышался треск ломающихся осей; инженеры выкрикивали по именам своих кучеров, озлобленно ругавшихся между собою. В общем, получалось впечатление того оглушительного хаоса, который бывает только на больших ночных пожарах. Кого-то переехали или, может быть, раздавили. Был слышен вопль.

Бобров никак не мог отыскать Митрофана. Раза два или три ему послышалось, будто его кучер отзывается на крик откуда-то из самой середины перепутавшихся экипажей. Но проникнуть туда не было никакой возможности, потому что давка становилась с каждой минутой все сильнее и сильнее.

Вдруг в темноте вспыхнул высоко над толпой красным пламенем огромный керосиновый факел. Послышались крики: "С дороги! С дороги! Посторонитесь, господа! С дороги!" Стремительная человеческая волна, гонимая сильным напором, подхватила Андрея Ильича, понесла его за собой, чуть не сбросив с ног, и плотно. прижала между задком одной пролетки и дышлом другой. Отсюда Бобров увидел, как между экипажами быстро образовалась широкая дорога и как по этой дороге проехал на своей тройке серых лошадей Квашнин. Факел, колебавшийся над коляской, обливал массивную фигуру Василия Терентьевича зловещим, точно кровавым, дрожащим светом.

Вокруг его коляски выла от боли, страха и озлобления стиснутая со всех сторон обезумевшая толпа... У Боброва что-то стукнуло в висках. На мгновение ему. показалось, что это едет вовсе не Квашнин, а какое-то окровавленное, уродливое и грозное божество, вроде тех идолов восточных культов, под колесницы которых бросаются во время религиозных шествий опьяневшие от экстаза фанатики. И он задрожал от бессильного бешенства.

Когда проехал Квашнин, сразу стало немного свободнее, и Бобров, обернувшись назад, увидел, что дышло, давившее ему спину, принадлежало его же собственной пролетке. Митрофан стоял около козел и зажигал факел.

- Скорей на завод, Митрофан! - крикнул Андрей Ильич, садясь. - Чтоб через десять минут поспеть, слышишь!

- Слушаю-с, - ответил мрачно Митрофан.

Он обошел пролетку кругом, чтобы влезть на козлы, как подобает всякому хорошему кучеру, справа, разобрал вожжи и прибавил, полуобернувшись назад:

- Только ежели лошадей зарежем, вы тогда, барин не серчайте.

- Ах, все равно...

Осторожно, с громадным трудом выбравшись из этой массы сбившихся в кучу лошадей и экипажей и выехав на узкую лесную дорогу, Митрофан пустил вожжи. Застоявшиеся, возбужденные лошади подхватили, и началась сумасшедшая скачка. Пролетка подпрыгивала на длинных, протянувшихся поперек дороги корнях, раскатывалась на ухабах и сильно накренялась то на левый, то на правый бок, заставляя и кучера и седока балансировать.

Красное пламя факела металось во все стороны с бурным ропотом. Вместе с ним метались вокруг пролетки длинные, причудливые тени деревьев... Казалось, что тесная толпа высоких, тонких и расплывчатых призраков неслась рядом с пролеткой в какой-то нелепой пляске. Призраки то перегоняли лошадей, вырастая до исполинских размеров, то вдруг падали на землю и, быстро уменьшаясь, исчезали за спиной Боброва, то забегали на несколько секунд в чащу и опять внезапно появлялись около самой пролетки, то сдвигались тесными рядами и покачивались и вздрагивали, точно перешептываясь о чем-то между собою... Несколько раз ветви частого кустарника, окаймлявшего дорогу, хлестали Митрофана и Боброва по лицам, будто чьи-то цепкие, тонкие, протянутые вперед руки.

Лес кончился. Лошади зашлепали ногами по какой-то луже, в которой запрыгало и зарябилось багровое блестящее пламя факела, и вдруг дружным галопом вывезли на крутой пригорок. Впереди расстилалось черное, однообразное поле.

- Да погоняй же, Митрофан, мы с тобой никогда не доедем! - крикнул Бобров нетерпеливо, хотя пролетка и без того неслась так, что дыхание захватывало. Митрофан проворчал что-то недовольным басом и ударил кнутом Фарватера, скакавшего, изогнувшись кольцом, на пристяжке. Кучер недоумевал, что сделалось с его барином, всегда любившим и жалевшим своих лошадей.

На горизонте огромное зарево отражалось неровным трепетанием в ползущих по небу тучах. Бобров глядел на вспыхивающее небо, и торжествующее, нехорошее злорадство шевелилось в нем. Дерзкий, жестокий тост Андреа сразу открыл ему глаза на все: и на холодную сдержанность Нины в продолжении нынешнего вечера, и на негодование ее мамаши во время мазурки, и на близость Свежевского к Василию Терентьевичу, и на все слухи и сплетни, ходившие по заводу об ухаживании самого Квашнина за Ниной... "Так и надо ему, так и надо, рыжему чудовищу, - шептал Бобров, ощущая такой прилив злобы и такое глубокое сознание своего унижения, что даже во рту у него пересохло. - О, если бы мне теперь встретиться с ним лицом к лицу, я бы надолго смутил самодовольный покой этого покупателя свежего мяса, этого грязного, жирного мешка, битком набитого золотом. Я бы оставил хорошую печать на его медном лбу!.."

Чрезмерное количество выпитого сегодня вина не опьянило Андрея Ильича, но действие его выразилось в необычайном подъеме энергии, в нетерпеливой и болезненной жажде движения... Сильный озноб потрясал его тело, зубы так сильно стучали, что приходилось крепко стискивать челюсти, мысль работала быстро, ярко и беспорядочно, как в горячке. Андрей Ильич, незаметно для самого себя, то разговаривал вслух, то стонал, то громко и отрывисто смеялся, между тем как пальцы его сами собой крепко сжимались в кулаки.

- Барин, да вы, никак, больны? Нам бы домой ехать, - сказал несмело Митрофан.

Эти слова вдруг привели Боброва в неистовство, и он закричал хрипло:

- Не разговаривай, дурак!.. Гони!..

Скоро с горы стал виден и весь завод, окутанный мелочно-розовым дымом. Сзади, точно исполинский костер, горел лесной склад. На ярком фоне огня суетливо копошилось множество маленьких черных человеческих фигур. Еще издали было слышно, как трещало в пламени сухое дерево. Круглые башни кауперов и доменных печей то резко и отчетливо выдвигались из мрака, то опять совершенно тонули в нем. Красное зарево пожара ярким и грозным блеском отражалось в бурной воде большого четырехугольного пруда. Высокая плотина этого пруда вся сплошь, без просветов, была покрыта огромной черной толпой, которая медленно подвигалась вперед и, казалось, кипела. И необычайный - смутный и зловещий гул, похожий, на рев отдаленного моря, доносился от этой страшной, густой, сжатой на узком пространстве человеческой массы.

- Куда тебя несет, дьявол! Не видишь разве, что едешь на людей, сволочь! услыхал Бобров впереди грубый окрик, и на дороге, точно вынырнув из-под лошадей, показался рослый бородатый мужик, без шапки, с головой, сплошь забинтованной белыми тряпками.

- Погоняй, Митрофан! - крикнул Бобров.

- Барин! Подожгли, - услышал он дрожащий голос Митрофана.

Но тотчас же он услышал свист брошенного сзади камня и почувствовал острую боль удара немного выше правого виска. На руке, которую он поднес к ушибленному месту, оказалась теплая, липкая кровь.

Пролетка опять понеслась с прежней быстротой. Зарево становилось все сильнее. Длинные тени от лошадей перебегали с одной стороны дороги на другую. Временами Боброву начинало казаться, что он мчится по какому-то крутому косогору и вот-вот вместе с экипажем и лошадьми полетит с отвесной кручи в глубокую пропасть. Он совершенно потерял способность опознаваться и никак не мог узнать места, по которому проезжал. Вдруг лошади стали.

- Ну, чего же ты остановился, Митрофан? - раздражительно закричал Бобров.

- А куда ж я поеду, коли впереди люди? - отозвался Митрофан с угрюмым озлоблением в голосе.

Бобров, как ни всматривался в серый предутренний полумрак, ничего не видел, кроме какой-то черной неровной стены, над которою пламенело небо.

- Каких ты там еще людей видишь, черт возьми! - выругался он, слезая с пролетки и обходя лошадей, покрытых белыми комьями пены.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
