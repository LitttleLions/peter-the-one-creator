# Gesendeter Prompt 005

- Zeitstempel: 20260914-200011
- Provider: openrouter
- Modell: deepseek/deepseek-v4.1-flash
- Stil: stil-01-original
- Kapitel: 005
- Szene: 01
- Chunk: 01/03
- Temperatur: 0.2
- max_tokens: 12000
- System-Zeichen: 5037
- User-Zeichen: 8821

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

Подъезжая к своей квартире, Бобров заметил свет в окнах. "Должно быть, без меня приехал доктор и теперь валяется на диване в ожидании моего приезда", подумал он, сдерживая взмыленную лошадь. В теперешнем настроении Боброва доктор Гольдберг был единственным человеком, присутствие которого он мог перенести без болезненного раздражения.

Он любил искренно этого беспечного, кроткого еврея за его разносторонний ум, юношескую живость характера и добродушную страсть к спорам отвлеченного свойства. Какой бы вопрос ни затрагивал Бобров, доктор Гольдберг возражал ему с одинаковым интересом к делу и с неизменной горячностью. И хотя между обоими в их бесконечных спорах до сих пор возникали только противоречия, тем не менее они скучали друг без друга и виделись чуть не ежедневно.

Доктор действительно лежал на диване, закинув ноги на его спинку, и читал какую-то брошюру, держа ее вплотную у своих близоруких глаз. Быстро скользнув взглядом по корешку, Бобров узнал "Учебный курс металлургии" Мевиуса и улыбнулся. Он хорошо знал привычку доктора читать с одинаковым увлечением, и непременно из середины, все, что только попадалось ему под руку.

- А я без вас распорядился чайком, - сказал доктор, отбросив в сторону книгу и глядя поверх очков на Боброва. - Ну, как попрыгиваете, государь мой Андрей Ильич? У-у, да какой же вы сердитый! Что? Опять веселая меланхолия?

- Ах, доктор, скверно на свете жить, - сказал устало Бобров.

- Отчего же так, голубчик?

- Да так... вообще... все скверно. Ну как, доктор, ваша больница?

- Наша больница ничего... живет. Сегодня очень интересный хирургический случай был. Ей-богу, и смешно и трогательно. Представьте себе, приходит на утренний осмотр парень, из масальских каменщиков. Эти масальские ребята, какого ни возьми, все, как на подбор, богатыри, "Что тебе?" - спрашиваю. "Да вот, господин дохтур, резал я хлеб для артели, так палец маненечко попортил, руду никак не уймешь". Осмотрел я его руку: так себе царапинка, пустяки, но нагноилась немного; я приказал фельдшеру положить пластырь. Только вижу, парень мой не уходит. "Ну, чего тебе еще надо? Заклеили тебе руку, и ступай". - "Это верно, говорит, заклеили, дай бог тебе здоровья, а только вот што, этто башка у меня трешшыть, так думаю, заодно и напротив башки чего-нибудь дашь". "Что же у тебя с башкой? Треснул кто-нибудь, верно?" Парень так и обрадовался, загоготал. "Есть, говорит, тот грех. Ономнясь, на Спаса (это, значит, дня три тому назад), загуляли мы артелью да вина выпили ведра полтора, ну, ребята и зачали баловать промеж себя... Ну, и я тоже. А опосля... в драке-то нешто разберешься?.. ка-ак он меня зубилом саданул по балде... починил, стало быть... Сначала-то оно ничего было, не больно, а вот теперь трешшыть башка-то". Стал я осматривать "балду", и что же вы думаете? - прямо в ужас пришел! Череп проломлен насквозь, дыра с пятак медный будет величиною, и обломки кости в мозг врезались... Теперь лежит в больнице без сознания. Изумительный, я вам скажу, народец: младенцы и герои в одно и то же время. Ей-богу, я не шутя думаю, что только русский терпеливый мужик и вынесет такую починку балды. Другой, не сходя с места, испустил бы дух. И потом, какое наивное незлобие: "В драке нешто разберешь?" Черт знает что такое!

Бобров ходил взад и вперед по комнате, щелкая хлыстом по голенищам высоких сапог и рассеянно слушал доктора. Горечь, осевшая ему на душу еще у Зиненок, до сих пор не могла успокоиться.

Доктор помолчал немного и, видя, что его собеседник не расположен к разговору, сказал с участием:

- Знаете что, Андрей Ильич? Попробуемте-ка на минуточку лечь спать да хватим на ночь ложечку-другую брому. Оно полезно в вашем настроении, а вреда все равно никакого не будет...

Они оба легли в одной комнате: Бобров на кровати, доктор на том же диване. Но и тому и другому не спалось. Гольдберг долго слушал в темноте, как ворочался с боку на бок и вздыхал Бобров, и наконец заговорил первый:

- Ну, что вы, голубчик? Ну, что терзаетесь? Уж говорите лучше прямо, что такое там в вас засело? Все легче будет. Чай, все-таки не чужой я вам человек, не из праздного любопытства спрашиваю.

Эти простые слова тронули Боброва. Хотя его и связывали с доктором почти дружеские отношения, однако ни один из них до сих пор ни словом не подтвердил этого вслух: оба были люди чуткие и боялись колючего стыда взаимных признаний. Доктор первый открыл свое сердце. Ночная темнота и жалость к Андрею Ильичу помогли этому.

- Все мне тяжело и гадко. Осип Осипович, - отозвался тихо Бобров. Первое, мне гадко то, что я служу на заводе и получаю за это большие деньги, а мне это заводское дело противно и противно! Я считаю себя честным человеком и потому прямо себя спрашиваю: "Что ты делаешь? Кому ты приносишь пользу?" Я начинаю разбираться в этих вопросах и вижу, что благодаря моим трудам сотня французских лавочников-рантье и десяток ловких русских пройдох со временем положат в карман миллионы. А другой цели, другого смысла нет в том труде, на подготовку к которому я убил лучшую половину жизни!..

- Ну, уж это даже смешно, Андрей Ильич, - возразил доктор, повернувшись в темноте лицом к Боброву. - Вы требуете, чтобы какие-то буржуи прониклись интересами гуманности. С тех пор, голубчик, как мир стоит, все вперед движется брюхом, иначе не было и не будет. Но суть-то в том, что вам наплевать на буржуев, потому что вы гораздо выше их. Неужели с вас не довольно мужественного и гордого сознания, что вы толкайте вперед, выражаясь языком передовых статей, "колесницу прогресса"? Черт возьми! Акции пароходных обществ приносят колоссальные дивиденды, но разве это мешает Фультону считаться благодетелем человечества?

- Ах, доктор, доктор! - Бобров досадливо поморщился. - Вы не были, кажется, сегодня у Зиненок, а вашими устами вдруг заговорила их житейская мудрость. Слава богу, мне не придется ходить далеко за возражениями, потому что я сейчас разобью вас вашей же возлюбленной теорией.

- То есть какой это теорией?.. Позвольте... я что-то не помню никакой теории... право, голубчик, не помню... забыл что-то...

- Забыли? А кто здесь же, на этом самом диване, с пеной у рта кричал, что мы, инженеры и изобретатели, своими открытиями ускоряем пульс общественной жизни до горячечной скорости? Кто сравнивал эту жизнь с состоянием животного, заключенного в банку с кислородом? О, я отлично помню, какой страшный перечень детей двадцатого века, неврастеников, сумасшедших, переутомленных, самоубийц, кидали вы в глаза этим самым благодетелям рода человеческого. Телеграф, телефон, стодвадцативерстные поезда, говорили вы, сократили расстояние до minimum'a, - уничтожили его... Время вздорожало до того, что скоро начнут ночь превращать в день, ибо уже чувствуется потребность в такой удвоенной жизни. Сделка, требовавшая раньше целых месяцев, теперь оканчивается в пять минут. Но уж и эта чертовская скорость не удовлетворяет нашему нетерпению... Скоро мы будем видеть друг друга по проволоке на расстоянии сотен и тысяч верст!.. А между тем всего пятьдесят лет тому назад наши предки, собираясь из деревни в губернию, не спеша служили молебен и пускались в путь с запасом, достаточным для полярной экспедиции... И мы несемся сломя голову вперед и вперед, оглушенные грохотом и треском чудовищных машин, одуревшие от этой бешеной скачки, с раздраженными нервами, извращенными вкусами и тысячами новых болезней... Помните, доктор? Все это ваши собственные слова, поборник благодетельного прогресса!

Доктор, уже несколько раз тщетно пытавшийся возразить, воспользовался минутной передышкой Боброва.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
