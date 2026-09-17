# Gesendeter Prompt 004

- Zeitstempel: 20260914-195657
- Provider: openrouter
- Modell: deepseek/deepseek-v4.1-flash
- Stil: stil-01-original
- Kapitel: 004
- Szene: 01
- Chunk: 01/02
- Temperatur: 0.2
- max_tokens: 12000
- System-Zeichen: 5037
- User-Zeichen: 10095

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

Фарватер шел, звучно фыркая и допрашивая поводьев. Вдали показался дом Шепетовской экономии. Из густой зелени сиреней и акаций едва виднелись его белые стены и красная крыша. Под горой небольшой пруд выпукло подымался из окружавших его зеленых берегов.

На крыльце стояла женская фигура. Бобров издали узнал в ней Нину по ярко-желтой кофточке, так красиво оттенявшей смуглый цвет ее лица, и тотчас же, подтянув Фарватеру поводья, выпрямился и высвободил носки ног, далеко залезшие в стремена.

- Вы опять на своем сокровище приехали? Ну вот, просто видеть не могу этого урода! - крикнула с крыльца Нина веселым и капризным голосом избалованного ребенка. У нее уже давно вошло в привычку дразнить Боброва его лошадью, к которой он был так привязан. Вообще в доме Зиненок вечно кого-нибудь и чем-нибудь дразнили.

Бросив поводья подбежавшему заводскому конюху, Бобров похлопал крутую, потемневшую от пота шею лошади и вошел вслед за Ниной в гостиную. Анна Афанасьевна, сидевшая за самоваром, сделала вид, будто необычайно поражена приездом Боброва.

- А-а-а! Андрей Ильич! Наконец-то вы к нам пожаловали!.. - воскликнула она нараспев.

И, ткнув ему руку прямо в губы, когда он здоровался с ней, она своим громким носовым голосом спросила:

- Чаю? Молока? Яблоков? Говорите, чего хотите.

- Merci, Анна Афанасьевна.

- Merci - oui, ou merci - non? [ Спасибо - да, или спасибо - нет? (франц.) ]

Подобные французские фразы были неизменны в семье Зиненко. Бобров отказался от всего.

- Ну, так идите на террасу, там молодежь затеяла какие-то фанты, что ли, милостиво разрешила madame Зиненко.

Когда он вышел на балкон, все четыре барышни разом, совершенно тем же тоном и так же в нос, как их маменька, воскликнули:

- А-а-а! Андрей Ильич! Вот уж кого давно-то не было видно! Чего вам принести? Чаю? Яблоков? Молока? Не хотите? Нет, правда? А может быть, хотите? Ну, в таком случае садитесь здесь и принимайте участие.

Играли в "барыня прислала сто рублей", в "мнения" и еще в какую-то игру, которую шепелявая Кася называла "играть в пошуду". Из гостей были: три студента-практиканта, которые все время выпячивали грудь и принимали пластические позы, выставив вперед ногу и заложив руку в задний карман сюртука; был техник Миллер, отличавшийся красотою, глупостью и чудесным баритоном, и, наконец, какой-то молчаливый господин в сером, не обращавший на себя ничьего внимания.

Игра не ладилась. Мужчины исполняли свои фанты со снисходительным и скучающим видом: девицы вовсе от них отказывались, перешептывались и напряженно хохотали.

Смеркалось. Из-за крыш ближней Деревни медленно показывалась огромная красная луна.

- Дети, идите в комнаты! - крикнула из столовой Анна Афанасьевна. Попросите Миллера, чтобы он нам спел что-нибудь.

Через минуту голоса барышень уже слышались в комнатах.

- Нам было очень весело, - щебетали они вокруг матери, - мы так смеялись, так смеялись...

На балконе остались только Нина и Бобров. Она сидела на перилах, обхвативши столб левой рукой и прижавшись к нему в бессознательно-грациозной позе. Бобров поместился на низкой садовой скамеечке у самых ее ног и снизу вверх, заглядывая ей в лицо, видел нежные очертания ее шеи и подбородка.

- Ну, расскажите же что-нибудь интересное, Андрей Ильич, - нетерпеливо приказала Нина.

- Право, я не знаю, что бы вам рассказать, - возразил Бобров. - Ужасно трудно говорить по заказу. Я и то уж думаю: нет ли такого разговорного сборника, на разные темы...

- Фу-у! Какой вы ску-учный, - протянула Нина. - Скажите, когда вы бываете в духе?

- А вы мне скажите, почему вы так боитесь молчания? Чуть разговор немножко иссяк, вам уже и не по себе... А разве дурно разговаривать молча?

- "Мы будем с тобой молчали-ивы..." - пропела насмешливо Нина.

- Конечно, будем молчаливы. Посмотрите: небо ясное, луна рыжая, большущая, на балконе так тихо... Чего же еще?..

- "И эта глупая луна на этом глупом небосклоне", - продекламировала Нина. - A propos [ кстати - фр. ], вы слышали, что Зиночка Маркова выходит замуж за Протопопова? Выходит-таки! Удивительный человек этот Протопопов. - Она пожала плечами. Три раза ему Зина отказывала, и он все-таки не мог успокоиться, сделал в четвертый раз предложение. И пускай на себя пеняет. Она его, может быть, будет уважать, но любить - никогда!

Этих слов было достаточно, чтобы расшевелить желчь в душе Боброва. Его всегда выводил из себя узкий, мещанский словарь Зиненок, с выражениями вроде: "Она его любит, но не уважает", "Она его уважает, но не любит". Этими словами в их понятиях исчерпывались самые сложные отношения между мужчиной и женщиной, точно так же, как для определения нравственных, умственных и физических особенностей любой личности у них существовало только два выражения; "брюнет" и "блондин".

И Бобров из смутного желания разбередить свою злобу спросил:

- Что же такое представляет собою этот Протопопов?

- Протопопов? - задумалась на секунду Нина. - Он... как бы вам сказать... довольно высокого роста... шатен!..

- И больше ничего?

- Чего же еще? Ах, да: служит в акцизе...

- И только? Да неужели, Нина Григорьевна, у вас для характеристики человека не найдется ничего, кроме того, что он шатен и служит в акцизе! Подумайте: сколько в жизни встречается нам интересных, талантливых и умных людей. Неужели все это только "шатены" и "акцизные чиновники"? Посмотрите, с каким жадным любопытством наблюдают жизнь крестьянские дети и как они метки в своих суждениях. А вы, умная и чуткая девушка, проходите мимо всего равнодушно, потому что у вас есть в запасе десяток шаблонных, комнатных фраз. Я знаю, если кто-нибудь упомянет в разговоре про луну, вы сейчас же вставите: "Как эта глупая луна", - и так далее. Если я расскажу, положим, какой-нибудь выходящий из ряда обыкновенных случай, я наперед знаю, что вы заметите: "Свежо предание, а верится с трудом". И так во всем, во всем... Поверьте мне, ради бога, что все самобытное, своеобразное...

Он замолчал с ощущением горечи во рту, и они оба сидели минут пять тихо и не шевелясь. Вдруг из гостиной послышались звучные аккорды, и немного тронутый, но полный глубокого выражения голос Миллера запел:

Средь шумного бала, случайно,

В тревоге мирской суеты,

Тебя я увидел, но тайна

Твои покрывала черты.

Озлобленное настроение Боброва быстро улеглось, и он жалел теперь, что огорчил Нину. "Для чего вздумал я требовать от ее наивного, свежего, детского ума оригинальной смелости? - думал он. - Ведь она, как птичка: щебечет первое, что ей приходит в голову, и, почем знать, может быть, это щебетанье даже гораздо лучше, чем разговоры об эмансипации, и о Ницше, и о декадентах?"

- Нина Григорьевна, не сердитесь на меня. Я увлекся и наговорил глупостей, - сказал он вполголоса.

Нина молчала, отвернувшись от него и глядя на восходившую луну. Он отыскал в темноте ее свесившуюся руку и, нежно пожав ее, прошептал:

- Нина Григорьевна... Пожалуйста...

Нина вдруг быстро повернулась к нему и, ответив на его пожатие быстрым, нервным пожатием, воскликнула тоном прощения и упрека:

- Злючка! Всегда вы меня обижаете... Пользуетесь тем, что я на вас не умею сердиться!..

И, оттолкнув его внезапно задрожавшую руку, почти вырвавшись от него, она перебежала балкон и скрылась в дверях.

...И в грезах неведомых сплю...

Люблю ли тебя - я не знаю,

Но кажется мне, что люблю...

пел со страстным и тоскливым выражением Миллер.

"Но кажется мне, что люблю!" - повторил взволнованным шепотом Бобров, глубоко переводя дух и прижимая руку к забившемуся сердцу.

"Зачем же, - растроганно думал он, - утомляю я себя бесплодными мечтами о каком-то неведомом, возвышенном счастье, когда здесь, около меня, - простое, но глубокое счастье? Чего же еще нужно от женщины, от жены, если в ней столько нежности, кротости, изящества и внимания? Мы, бедные, нервные, больные люди, не умеем брать просто от жизни ее радостей, мы их нарочно отравляем ядом нашей неутомимой потребности копаться в каждом чувстве, в каждом своем и чужом помышлении... Тихая ночь, близость любимой девушки, милые, незатейливые речи, минутная вспышка гнева и потом внезапная ласка - господи! Разве не в этом вся прелесть существования?"

Он вошел в гостиную повеселевший, бодрый, почти торжествующий. Глаза его встретились с глазами Нины, и в ее долгом взоре он прочел нежный ответ на свои мысли. "Она будет моей женой", - подумал Бобров, ощущая в душе спокойную радость.

Разговор шел о Квашнине. Анна Афанасьевна, наполняя своим уверенным голосом всю комнату, говорила, что она думает завтра тоже повести "своих девочек" на: вокзал.

- Очень может быть, что Василий Терентьевич захочет сделать нам визит. По крайней мере о его приезде мне еще за месяц писала племянница мужа моей двоюродной сестры - Лиза Белоконская...

- Это, кажется, та Белоконская, брат которой женат на княжне Муховецкой? покорно вставил заученную реплику господин Зиненко.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
