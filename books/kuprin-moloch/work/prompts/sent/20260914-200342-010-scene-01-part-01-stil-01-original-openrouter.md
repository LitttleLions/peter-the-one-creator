# Gesendeter Prompt 010

- Zeitstempel: 20260914-200342
- Provider: openrouter
- Modell: deepseek/deepseek-v4.1-flash
- Stil: stil-01-original
- Kapitel: 010
- Szene: 01
- Chunk: 01/03
- Temperatur: 0.2
- max_tokens: 12000
- System-Zeichen: 5037
- User-Zeichen: 10239

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

На 303-й версте общество вышло из вагонов и длинной пестрой вереницей потянулось мимо сторожевой будки, по узкой дорожке, спускающейся в Бешеную балку... Еще издали на разгоряченные лица пахнуло свежестью и запахом осеннего леса... Дорожка, становясь все круче, исчезала в густых кустах орешника и дикой жимолости, которые сплелись над ней сплошным темным сводом. Под ногами уже шелестели желтые, сухие, скоробившиеся листья. Вдали сквозь густую сеть чащи алела вечерняя заря.

Кусты окончились. Перед глазами гостей неожиданно открылась окруженная лесом широкая площадка, утрамбованная и усыпанная мелким песком. На одном ее конце стоял восьмигранный павильон, весь разукрашенный флагами и зеленью, на другом - крытая эстрада для музыкантов. Едва только первые пары показались из чащи, как военный оркестр грянул с эстрады веселый марш. Резвые, красивые медные звуки игриво понеслись по лесу, звонко отражаясь от деревьев и сливаясь где-то далеко в другой оркестр, который, казалось, то перегонял первый, то отставал от него. В восьмигранном павильоне вокруг столов, расставленных покоем и уже покрытых новыми белыми скатертями, суетилась прислуга, гремя посудой...

Как только музыканты кончили марш, все приглашенные на пикник разразились дружными аплодисментами. Они были в самом деле изумлены, потому что не далее как две недели тому назад эта площадка представляла собою косогор, усеянный редкими кустами...

Оркестр заиграл вальс.

Бобров видел, как Свежевский, стоявший рядом с Ниной, тотчас же, без приглашения, обхватил ее талию, и они понеслись, быстро вертясь, по площадке.

Едва Нину оставил Свежевский, как к ней подбежал горный студент, за ним еще кто-то. Бобров танцевал плохо, да и не любил танцевать. Однако ему пришло в голову пригласить Нину на кадриль. "Может быть, - думал он, - мне удастся улучить минуту для объяснения". Он подошел к ней, когда она, только что сделав два тура, сидела и торопливо обмахивала веером пылавшее лицо.

- Надеюсь, Нина Григорьевна, что вы оставили для меня одну кадриль?

- Ах, боже мой... Такая досада! У меня все кадрили разобраны, - ответила она, не глядя на него.

- Неужели? Так скоро? - спросил глухим голосом Бобров.

- Ну да, - Нина нетерпеливо и насмешливо приподняла плечи. - Зачем же вы опоздали? Я еще в вагоне обещала все кадрили...

- Вы, значит, совсем позабыли обо мне? - сказал он печально.

Звук его голоса тронул Нину. Она нервно сложила; и опять развернула веер, но не подняла глаз.

- Вы сами виноваты. Почему вы не подошли?..

- Но ведь я только для того и приехал на пикник, чтобы вас видеть... Неужели вы шутили со мной, Нина Григорьевна?

Она молчала, в замешательстве теребя веер. Ее выручил подлетевший к ней молодой инженер. Она быстро встала и, даже не обернувшись на Боброва, положила свою тонкую руку в длинной белой перчатке на плечо инженера. Андрей Ильич следил за нею глазами... Сделав тур, она села, - конечно, умышленно, подумал Андрей Ильич, - на другом конце площадки. Она почти боялась его или стыдилась перед ним.

Прежняя, давно знакомая, тупая и равнодушная тоска овладела Бобровым. Все лица стали казаться ему пошлыми, жалкими, почти комичными. Размеренные звуки музыки непрерывными глухими ударами отзывались в его голове, причиняя раздражающую боль. Но он еще не потерял надежды и старался утешить себя разными предположениями: "Не сердится ли она за то, что я не прислал ей букета? Или, может быть, ей просто не хочется танцевать с таким мешком, как я? - догадался он. - Ну что же, она, пожалуй, и права. Ведь для девушек эти пустяки так много значат... Разве не они составляют их радости и огорчения, всю поэзию их жизни?"

Когда стало смеркаться, вокруг павильона зажгли длинные цепи из разноцветных китайских фонарей. Но этого оказалось мало: площадка оставалась почти не освещенною. Вдруг с обоих ее концов вспыхнули ослепительным голубоватым светом два электрические солнца, до сих пор тщательно замаскированные зеленью деревьев. Березы и грабы, окружавшие площадку, сразу выдвинулись вперед. Их неподвижные кудрявые ветви, ярко и фальшиво освещенные, стали похожи на театральную декорацию первого плана. За ними, окутанные в серо-зеленую мглу, слабо вырисовывались на совершенно черном небе круглые и зубчатые деревья чащи. Кузнечики в степи, не заглушаемые музыкой, кричали так странно, громко и дружно, что казалось, будто кричит только один кузнечик, но кричит отовсюду: и справа, и слева, и сверху.

Бал длился, становясь все оживленнее и шумнее. Один танец следовал за другим. Оркестр почти не отдыхал... Женщины, как от вина, опьянели от музыки и от сказочной обстановки вечера.

Аромат их духов и разгоряченных тел странно смешивался с запахом степной полыни, увядающего листа, лесной сырости и с отдаленным тонким запахом скошенной отавы. Повсюду - то медленно, то быстро колыхались веера, точно крылья красивых разноцветных птиц, собирающихся лететь... Громкий говор, смех, шарканье ног о песок площадки сплетались в один монотонный и веселый гул, который вдруг с особенной силой вырывался вперед, когда музыка переставала играть.

Бобров все время неотступно следил за Ниной. Раза два она чуть-чуть не задела его своим платьем. На него даже пахнуло ветром, когда она пронеслась мимо. Танцуя, она красиво и как будто беспомощно изгибала левую руку на плече своего кавалера и так склоняла голову, как будто бы хотела к этому плечу прислониться... Иногда мелькал край ее нижней белой кружевной юбки, развеваемой быстрым движением, и маленькая ножка в черном чулке с тонкой щиколоткой и крутым подъемом икры. Тогда Боброву становилось почему-то стыдно, и он чувствовал в душе злобу на всех, кто мог видеть Нину в эти моменты.

Началась мазурка. Было уже около девяти часов. Нина, танцевавшая со Свежевским, воспользовалась тем временем, когда ее кавалер, дирижировавший мазуркой, устраивал какую-то сложную фигуру, и побежала в уборную, легко и быстро скользя ногами в такт музыке и придерживая обеими руками распустившиеся волосы. Бобров, видевший это с другого конца площадки, тотчас же поспешил за нею следом и стал у дверей..., Здесь было почти темно; вся уборная - маленькая дощатая комнатка, пристроенная сзади павильона, - находилась в густой тени. Бобров решился дождаться Нины и во что бы то ни стало заставить ее объясниться. Сердце его часто и больно билось, пальцы, которые он, судорожно стискивал, сделались влажными и холодными.

Через пять минут Нина вышла. Бобров выдвинулся из тени и преградил ей дорогу. Нина слабо вскрикнула и отшатнулась.

- Нина Григорьевна, за что вы меня так мучите? - сказал Андрей Ильич, незаметно для себя складывая руки умоляющим жестом. - Разве вы не видите, как мне больно. О! Вы забавляетесь моим горем... Вы смеетесь надо мной...

- Я не понимаю, что вам нужно. Я и не думала смеяться над вами, - ответила Нина упрямо и заносчиво.

В ней проснулся дух ее семейства.

- Нет? - уныло спросил Бобров. - Что же значит ваше сегодняшнее обращение со мной?

- Какое обращение?

- Вы холодны со мной, почти враждебны. Вы отворачиваетесь от меня... Вам даже самое присутствие мое на вечере неприятно...

- Мне решительно все равно...

- Это еще хуже... Я чувствую в вас какую-то непостижимую для меня и ужасную перемену... Ну, будьте же откровенны, Нина, будьте такой правдивой, какой я вас еще сегодня считал... Как бы ни была страшна истина, скажите ее. Лучше уж для вас и для меня сразу кончить...

- Что кончить? Я не понимаю вас...

Бобров сжал руками виски, в которые лихорадочно билась кровь.

- Нет, вы понимаете. Не притворяйтесь. Нам есть что кончить. У нас были нежные слова, почти граничившие с признанием, у нас были прекрасные минуты, соткавшие между нами какие-то нежные, тонкие узы... Я знаю, - вы хотите сказать, что я заблуждаюсь... Может быть, может быть... Но разве не вы велели мне приехать на пикник, чтобы иметь возможность поговорить без посторонних?

Нине вдруг стало жаль его.

- Да... Я просила вас приехать... - произнесла она, низко опустив голову. - Я хотела вам сказать... Я хотела... что нам надо проститься навсегда.

Бобров покачнулся, точно его толкнули в грудь. Даже в темноте было заметно, как его лицо побледнело.

- Проститься... - проговорил он, задыхаясь. - Нина Григорьевна!.. Слово прощальное - тяжелое, горькое слово... Не говорите его...

- Я его должна сказать.

- Должны?

- Да, должна. Это не моя воля.

- Чья же?

Кто-то подходил к ним. Нина вгляделась в темноту и прошептала:

- Вот чья.

Это была Анна Афанасьевна. Она подозрительно оглядела Боброва и Нину и взяла свою дочь за руку.

- Зачем ты, Нина, убежала от танцев? - сказала она тоном выговора. - Стала где-то в темноте и болтаешь... Хорошее, нечего сказать, занятие... А я тебя ищи по всем закоулкам. Вы, сударь, - обратилась она вдруг бранчиво и громко к Боброву, - вы, сударь, если сами не умеете или не любите танцевать, то хоть барышням бы не мешали, и не компрометировали бы их беседой tete-a-tete...[ наедине - фр .] в темных углах...

Она отошла и увлекла за собою Нину.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
