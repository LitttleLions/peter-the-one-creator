# Gesendeter Prompt 007

- Zeitstempel: 20260914-200145
- Provider: openrouter
- Modell: deepseek/deepseek-v4.1-flash
- Stil: stil-01-original
- Kapitel: 007
- Szene: 01
- Chunk: 01/03
- Temperatur: 0.2
- max_tokens: 12000
- System-Zeichen: 5037
- User-Zeichen: 9214

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

Закладка каменных работ и открытие кампании новой домны произошли через четыре дня после приезда Квашнина. Предполагалось отпраздновать оба эти события с возможно большим торжеством, почему на соседние металлургические заводы: Крутогорский, Воронинский и Львовский были заранее разосланы печатные приглашения.

Вслед за Василием Терентьевичем из Петербурга прибыли еще два члена правления, четверо бельгийских инженеров и несколько крупных акционеров. Между заводскими служащими носились слухи, будто бы правление ассигновало на устройство парадного обеда около двух тысяч рублей, однако эти слухи пока ничем еще не оправдались, и вся закупка вин и припасов легла тяжелой данью на подрядчиков.

День выдался очень удачный для торжества, - один из тех ярких, прозрачных дней ранней осени, когда небо кажется таким густым, синим и глубоким, а прохладный воздух пахнет тонким, крепким вином. Квадратные ямы, вырытые под фундаменты для новой воздуходувной машины и бессемеровой печи, были окружены в виде "покоя" густой толпою рабочих. В середине этой живой ограды, над самым краем ямы, возвышался простой некрашеный стол, покрытый белой скатертью, на котором лежали крест и Евангелие рядом с жестяной чашей для святой воды и кропилом. Священник, уже облаченный в зеленую, затканную золотыми крестами ризу, стоял в стороне, впереди пятнадцати рабочих, вызвавшихся быть певчими. Открытую сторону покоя занимали инженеры, подрядчики, старшие десятники, конторщики - пестрая, оживленная группа из двухсот с лишком человек. На насыпи поместился фотограф, который, накрыв черным платком и себя и свой аппарат, давно уже возился, отыскивая удачную точку.

Через десять минут Квашнин быстро подкатил к площадке на тройке великолепных серых лошадей. Он сидел в коляске один, потому что, при всем желании, никто не смог бы поместиться рядом с ним. Следом за Квашниным подъехало еще пять или шесть экипажей. Увидев Василия Терентьевича, рабочие инстинктом узнали в нем "набольшего" и тотчас же, как один человек, поснимали шапки. Квашнин величественно прошел вперед и кивнул головой священнику.

- Благословен бог наш, всегда, ныне и присно, и во веки веко-ов, раздался среди быстро наступившей тишины дребезжащий, кроткий и. гнусавый тенорок священника.

- Аминь, - подхватил довольно стройно импровизированный хор.

Рабочие - их было до трех тысяч человек - так же дружно, как кланялись Квашнину, перекрестились широкими крестами, склонили головы и потом, подняв их, встряхнули волосами... Бобров стал невольно присматриваться к ним. Впереди стояли двумя рядами степенные русаки-каменщики, все до одного в белых фартуках, почти все со льняными волосами и рыжими бородами, сзади них литейщики и кузнецы в широких темных блузах, перенятых от французских и английских рабочих, с лицами, никогда не отмываемыми от железной копоти, между ними виднелись и горбоносые профили иноземных увриеров [ рабочих - фр .]; сзади, из-за литейщиков, выглядывали рабочие при известковых печах, которых издали можно было узнать по лицам, точно обсыпанным густо мукою, и по воспаленным, распухшим, красным глазам...

Каждый раз, когда хор громко и стройно, хотя несколько в нос пел "Спаси от бед рабы твоя, богородице", все эти три тысячи человек с однообразным тихим шелестом творили свои усердные крестные знамения и клали низкие поклоны. Что-то стихийное, могучее и в то же время что-то детское и трогательное почудилось Боброву в этой общей молитве серой огромной массы. Завтра все рабочие примутся за свой тяжкий, упорный, полусуточный труд. Почем знать, кому из них уже предначертано судьбою поплатиться на этом труде жизнью: сорваться с высоких лесов, опалиться расплавленным металлом, быть засыпанным щебнем или кирпичом? И не об этом ли непреложном решении судьбы думают они теперь, отвешивая низкие поклоны и встряхивая русыми кудрями, в то время когда хор просит богородицу - спасти от бед рабы своя... И на кого, как не на одну только богородицу, надеяться этим большим детям, с мужественными и простыми сердцами, этим смиренным воинам, ежедневно выходящим из своих промозглых, настуженных землянок на привычный подвиг терпения и отваги?

Так, или почти так, думал Бобров, всегда склонный к широким, поэтическим картинам; и хотя он давно уже отвык молиться, но каждый раз, когда дребезжащий, далекий голос священника сменялся дружным возгласом клира, по спине и по затылку Андрея Ильича пробегала холодная волна нервного возбуждения. Было что-то сильное, покорное и самоотверженное в наивной молитве этих серых тружеников, собравшихся бог весть откуда, из далеких губерний, оторванных от родного, привычного угла для тяжелой и опасной работы...

Молебен кончился. Квашнин с небрежным видом бросил в яму золотой, но нагнуться с лопаточкой никак не мог - это сделал за него Шелковников. Потом вся группа двинулась к доменным печам, возвышавшимся на каменных фундаментах своими круглыми черными массивными башнями.

Пятая, вновь выстроенная домна шла, как говорится на техническом жаргоне, "спелым ходом". Из проделанного внизу ее, на аршинной высоте, отверстия бил широким огненно-белым клокочущим потоком расплавленный шлак, от которого прыгали во все стороны голубые серные огоньки. Шлак стекал по наклонному желобу в котлы, подставленные к отвесному краю фундамента, и застывал в них зеленоватой густой массой, похожей на леденец. Рабочие, находившиеся на самой верхушке печи, продолжали без отдыха забрасывать в нее руду и каменный уголь, которые то и дело подымались наверх в железных вагонетках.

Священник окропил домну со всех сторон святою водой и, боязливо торопясь, спотыкающейся, старческой походкой отошел в сторону. Горновой мастер, жилистый, чернолицый старик, перекрестился и поплевал на руки. То же сделали четверо его подручных. Потом они подняли с земли очень длинный стальной лом, долго раскачивали его и, одновременно крякнув, ударили им в самый низ печи. Лом звонко стукнулся в глиняную втулку. Зрители в боязливо-нервном ожидании зажмурили глаза; некоторые подались назад. Рабочие ударили в другой раз, потом в третий, в четвертый... и вдруг из-под острия лома брызнул фонтан нестерпимо-яркого жидкого металла. Тогда горновой мастер кругообразными движениями лома расширил отверстие, и чугун медленно полился по песчаной бороздке, принимая оттенок огненной охры. Целые снопы блестящих крупных звезд летели во все стороны из отверстия печи, громко треща и исчезая в воздухе. От этого, тихо, как будто лениво текущего металла, шел такой страшный жар, что непривычные гости все время отодвигались и закрывали щеки руками.

От доменных печей инженеры двинулись в отдел воздуходувных машин. Квашнин заранее распорядился так, чтобы приехавшие с ними акционеры увидели завод во всей его колоссальной величине и сутолоке. Он совершенно верно рассчитал, что эти господа, пораженные массою сильных и совершенно новых для них впечатлений, будут потом рассказывать чудеса уполномочившему их общему собранию. И, глубоко зная психологию деловых людей, Василий Терентьевич уже считал делом решенным новый и весьма выгодный лично для него выпуск акций, на который до сих пор не соглашалось общее собрание.

И акционеры действительно были поражены до головной боли, до дрожи в ногах... В помещении воздуходувных машин они слышали, бледные от волнения, как воздух, нагнетаемый четырьмя вертикальными двухсаженными поршнями в трубы, устремлялся по ним с ревом, заставляющим трястись каменные стены здания. По этим чугунным массивным, в два обхвата шириною трубам воздух проходил сквозь каупера, нагревался в них горящими газами до шестисот градусов и оттуда уже проникал во внутренность доменной печи, расплавляя руду и уголь своим жарким дуновением. Инженер, заведывающий воздуходувным отделением, давал объяснения. И хотя он нагибался поочередно к самым ушам акционеров и кричал во весь голос, надсаживая грудь, но за страшным гулом машин его слов не было слышно, а казалось только, что он беззвучно и напряженно шевелит губами.

### Ausgabe
Gib ausschliesslich die fertige deutsche Uebersetzung aus. Keine Vorbemerkung, keine Analyse, keine Erklaerung, keine Formulierung wie 'Hier ist die Uebersetzung'.
