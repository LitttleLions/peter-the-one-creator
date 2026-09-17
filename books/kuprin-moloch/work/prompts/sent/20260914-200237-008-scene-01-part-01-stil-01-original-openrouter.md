# Gesendeter Prompt 008

- Zeitstempel: 20260914-200237
- Provider: openrouter
- Modell: deepseek/deepseek-v4.1-flash
- Stil: stil-01-original
- Kapitel: 008
- Szene: 01
- Chunk: 01/02
- Temperatur: 0.2
- max_tokens: 12000
- System-Zeichen: 5037
- User-Zeichen: 10286

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

Злые языки начали звонить. Про Квашнина еще до его приезда ходило на заводе так много пикантных анекдотов, что теперь никто не сомневался в настоящей причине его внезапного сближения с семейством Зиненок. Дамы говорили об этом с двусмысленными улыбками, мужчины в своем кругу называли вещи с циничной откровенностью их именами. Однако наверняка никто ничего не знал. Все с удовольствием ждали соблазнительного скандала.

В сплетне была доля правды. Сделав визит семейству Зиненок, Квашнин стал ежедневно проводить у них вечера. По утрам, около одиннадцати часов, в Шепетовскую экономию приезжала его прекрасная тройка серых, и кучер неизменно докладывал, что "барин просит барыню и барышень пожаловать к ним на завтрак". К этим завтракам посторонние не приглашались. Кушанье готовил повар-француз, которого Василий Терентьевич всюду возил за собою в своих частых разъездах, даже и за границу.

Внимание Квашнина к его новым знакомым выражалось очень своеобразно. Относительно всех пятерых девиц он сразу стал на бесцеремонную ногу холостого и веселого дядюшки. Через три дня он уже называл их уменьшительными именами с прибавлением отчества - Шура Григорьевна, Ниночка Григорьевна, а самую младшую, Касю, часто брал за пухлый, с ямочкой, подбородок и дразнил "младенцем" и "цыпленочком", отчего она краснела до слез, но не сопротивлялась.

Анна Афанасьевна с игривой ворчливостью пеняла ему, что он совсем избалует ее девочек! Действительно, стоило только одной из них выразить какое-нибудь мимолетное желание, как оно тотчас же исполнялось. Едва Мака заикнулась, без всякого, впрочем, заднего умысла, что ей хотелось бы выучиться ездить на велосипеде, как на другой же день нарочный привез из Харькова прекрасную машину, стоившую по меньшей мере рублей триста... Бете он проиграл, держа с нею пари по поводу каких-то пустяков, пуд конфет, а Касе - брошку, в которой последовательно чередовались камни - коралл, аметист, сапфир и яшма, обозначавшие составные буквы ее имени. Он услышал однажды, что Нина любит верховую езду и лошадей. Через два дня ей привели кровную английскую кобылу, в совершенстве выезженную под дамское седло. Барышни были очарованы. В их доме поселился добрый сказочный дух, угадывавший и тотчас же исполнявший их малейшие капризы. Анна Афанасьевна смутно чувствовала в этой щедрости что-то неприличное для хорошей семьи, но у нее не хватало ни смелости, ни такта, чтобы дать незаметно понять это Квашнину. На ее льстивые выговоры он только махал рукой и отвечал своим грубоватым, решительным басом:

- Ну вот еще, дорогая моя... пустяки какие выдумали...

Однако ни одну из ее дочерей он не предпочитал явно, всем им одинаково угождая и над всеми бесцеремонно подтрунивая. Молодые люди, посещавшие раньше дом Зиненок, предупредительно и бесследно исчезли. Зато постоянным гостем сделался Свежевский, бывший у них до того всего-навсего раза два или три. Его никто не звал; он явился сам, точно по чьему-то таинственному приглашению, и сразу сумел сделаться необходимым для всех членов семьи.

Впрочем, появлению его у Зиненок предшествовал маленький анекдот. Как-то, месяцев пять тому назад, Свежевский проговорился в кругу своих сослуживцев, что мечта его жизни - сделаться со временем миллионером и что он к сорока годам непременно будет им.

- Как же вы этого добьетесь, Станислав Ксаверьевич? - спросили его.

Свежевский захихикал и, загадочно потирая свои мокрые руки, ответил:

- Все дороги ведут в Рим.

Чутье ему подсказывало, что теперь в Шепетовской экономии обстоятельства складываются весьма удобно для его будущей карьеры. Так или иначе, он мог пригодиться всемогущему патрону. И Свежевский, ставя все на карту, смело лез Квашнину на глаза со своим угодливым хихиканьем. Он заигрывал с ним, как веселый дворовый щенок со свирепым меделянским псом, выражая и лицом и голосом ежеминутную готовность учинить какую угодно пакость по одному только мановению Василия Терентьевича.

Патрон не препятствовал. Тот самый Квашнин, который прогонял со службы без объяснения причин директоров и управляющих заводами, - этот самый Квашнин молча терпел в своем присутствии какого-то Свежевского... Тут пахло важной услугой, и будущий миллионер напряженно ждал своего момента.

Все это, передаваясь из уст в уста, стало известно и Боброву. Он не удивился: на семейство Зиненок у него сложился свой твердый и точный взгляд. Его взволновало лишь то, что сплетня не преминет задеть грязным хвостом и Нину... После разговора на вокзале эта девушка стала ему еще милее и дороже. Ему одному она доверчиво открыла свою душу, прекрасную даже в колебаниях и в слабостях. Все другие знали - думалось ему - только ее костюм и наружность. Ревность же с ее циничными сомнениями, вечно раздраженным самолюбием, с ее мелочностью и грубостью была чужда доверчивой и нежной натуре Боброва.

Хорошая, искренняя женская любовь ни разу еще не улыбнулась Андрею Ильичу. Он был слишком застенчив и неуверен в себе, чтобы брать от жизни то, что ему, может быть, принадлежало по праву. Не удивительно, что теперь его душа радостно устремилась навстречу новому, сильному чувству.

Все эти дни Бобров находился под обаянием разговора на вокзале. Сотни раз он вспоминал его в мельчайших подробностях и с каждым разом прозревал в словах Нины более глубокое значение. По утрам он просыпался со смутным сознанием чего-то большого и светлого, что посетило его душу и обещает ему в будущем много блаженства.

Его неудержимо тянуло к Зиненкам: хотелось еще раз убедиться в своем счастье, еще раз слышать от Нины то робкие, то наивно-смелые полупризнания. Но его стесняло присутствие Квашнина, и он утешал себя только тем, что патрон ни в каком случае не мог пробыть в Иванкове более двух недель.

Однако случай помог ему увидеться с Ниной до отъезда Квашнина. Это произошло в воскресенье, через три дня после торжественного открытия кампании доменной печи. Бобров ехал верхом на Фарватере по широкой, хорошо набитой дороге, ведущей с завода на станцию. Было часа два прохладного, безоблачного дня. Фарватер шел бойкой ходой, прядая ушами и мотая косматой головой. На повороте около склада Бобров заметил даму в амазонке, спускавшуюся с горы на крупной гнедой лошади, и следом за нею - всадника на маленьком белом киргизе. Скоро он убедился, что это была Нина в темно-зеленой длинной развевающейся юбке, в желтых перчатках с крагами, с низеньким блестящим цилиндром на голове. Она уверенно и красиво сидела в седле. Стройная английская кобыла шла под нею эластической, широкой рысью, круто собрав шею и высоко подымая тонкие, сухие ноги. Сопровождавший Нину Свежевский далеко отстал и старался, болтая локтями, трясясь и горбясь, поймать носком потерянное стремя.

Заметив Боброва, Нина пустила лошадь галопом. Встречный ветер заставлял ее придерживать правой рукой перед шляпы и наклонять вниз голову. Поравнявшись с Андреем Ильичом, она сразу осадила лошадь, и та остановилась, нетерпеливо переступая ногами, раздувая широкие, порывистые ноздри и звучно перебирая зубами удила, с которых комьями падала пена. От езды у Нины раскраснелось лицо, и волосы, выбившиеся на висках из-под шляпы, откинулись назад длинными тонкими завитками.

- Откуда у вас такая прелесть? - спросил Бобров, когда ему, наконец, удалось осадить танцевавшего Фарватера и, перегнувшись на седле, подать кончики пальцев Нины.

- А правда, красавица? Это - подарок Квашнина.

- Я бы отказался от такого подарка, - грубо сказал Андрей Ильич, внезапно рассерженный беспечным ответом Нины.

Нина вспыхнула.

- На каком основании?

- Да на том, что... кто же для вас в самом деле Квашнин?.. Родственник?.. Жених?..

- Ах, боже мой, как вы щепетильны за других! - воскликнула Нина язвительно.

Но, увидев его страдающее лицо, она тотчас же смягчилась.

- Ведь ему это ничего не стоит... Он так богат...

Свежевский был уже в десяти шагах. Нина вдруг нагнулась к Боброву, ласково дотронулась концом хлыста до его руки и сказала вполголоса, тоном маленькой девочки, сознающейся в своей вине:

- Ну, будет... будет, не сердитесь... Я ему возвращу лошадь назад, злючка вы этакий!.. Видите, что значит для меня ваше мнение.

Глаза Андрея Ильича засияли счастьем, и руки невольно протянулись к Нине. Но он ничего не сказал, а только глубоко, всей грудью, вздохнул. Свежевский подъезжал к нему, раскланиваясь и стараясь принять небрежную посадку.

- Вы, конечно, знаете о нашем пикнике? - крикнул еще издали Свежевский.

- В первый раз слышу, - ответил Андрей Ильич.

- Пикник по инициативе Василия Терентьевича? В Бешеной балке?..

- Не слыхал...

- Да, да. Пожалуйста, приезжайте же, Андрей Ильич, - вмешалась Нина. - В среду, в пять часов вечера... сборный пункт - станция...

- Пикник по подписке?

- Кажется. Наверно не знаю.

Нина вопросительно и растерянно взглянула на Свежевского.

- По подписке, - подтвердил Свежевский. - Василий Терентьевич поручил мне исполнить некоторые его распоряжения. И я вам скажу, пикник будет колоссальный. Нечто сверхшикарное... Только все это покамест секрет. Вы будете поражены неожиданностью...

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
