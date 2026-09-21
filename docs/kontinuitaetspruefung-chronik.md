# Kontinuitaetspruefung fuer Die dritte Chronik (Plan, Stand 2026-09-21)

> Herkunft: Vorschlag aus dem Plan-Modus (21.09.2026) zur Frage, wie man
> inhaltliche Kontinuitaet pruefen koennte. Noch nicht umgesetzt.
> Zugehoeriger offener Punkt: `docs/offene-punkte.md` Punkt 12.

## Ziel

Ergaenzung zum deterministischen Regelcheck (`review_manuscript.py`,
Kategorien in `tools/lib/review_checks.py`) und zum Stil-
Wiederholungsdetektor (`tools/lib/repetition.py`, Kategorie
`repetition_style`, nur INFO/WARNING, nie ERROR): Pruefung, ob Figuren,
Wissen, Requisiten, Anwesenheit und Zeit ueber Kapitelgrenzen hinweg
zusammenpassen. Ergebnis ist ein Lese-Bericht, kein Release-Gate
(analog zu `repetition_style`: INFO/WARNING, nie ERROR).

## Modell: 4 Schichten

### Schicht 1 – Inventar (einmalig, dann wiederverwendet)

Figuren, Orte, Requisiten, Zeitachse, Akte. Hinweis: `names.yaml` der
Chronik ist derzeit leer (`entries: []`) und muesste dafuer aufgebaut
werden.

- Figuren: Shigi Qutuqu, Fatima, Juvaini, Toere gene, Gueyuek, Temuege
  Otchigin, Hoe'eluen, Jiguedei, Toghril u.a.
- Requisiten mit Eigenleben: blau-weisses Buch (offiziell), Privatakte
  (ehrlich), "ehrliche Minute", Siegel, Truhen, vergrabenes Buch.
- Zeitachse: Karakorum–Chorasan–Bagdad 1241–1258, Rahmung + vier Akte,
  drei Stimmen (siehe `export.yaml`: `summary`).

### Schicht 2 – Arc-Protokoll pro Figur und Kapitel

Fuer jede Figur pro Kapitel: `Zustand rein -> Zustand raus` auf vier
Achsen:

- **Macht** (Rang/Einfluss),
- **Wissen** (was weiss sie jetzt, was andere nicht wissen),
- **Moral** (wo steht sie zum Gesetz/zur Luege),
- **Beziehung** (wer schuldet wem was).

Plus: `Auftritt?` (aktiv/passiv/erwaehnt/abwesend-aber-wirksam, z.B.
Gueyuek in 025: "nicht anwesend", aber "war der Raum").

"Low rein / hoch raus" allein reicht nicht: Bei der Chronik laufen
Macht, Wissen und Moral getrennt (Shigi kann formal "hoch"
rauskommen und trotzdem moralisch gebrochen sein).

### Schicht 3 – Widerspruchs-Checks (5 Tests)

1. **Status-Test:** Ist der Sprung in *einem* Kapitel motiviert oder
   braucht er Zwischenschritte? Beispiel 025: Shigi mit sauberem Urteil
   rein -> Mann, der ahnt, dass sein Urteil als Praezedenz missbraucht
   wird, raus. Kein Macht-Sprung, sondern Moral-Knick – markieren.
2. **Wissens-Test:** Weiss Figur X in Kapitel N etwas, das sie erst in
   N+3 erfahren duerfte? Oder hat sie etwas vergessen, das sie wissen
   muesste? (Klassiker: Fatima-Briefe, Juvainis Liste in 028.)
3. **Requisiten-Test:** Wo ist das Objekt? Blau-weisses Buch auf dem
   Tisch (Gericht) vs. in der Lade (Kanzlei) vs. Privatakte hinter
   Steuerregistern Yunnan – zwei konsistente Orte oder wandert etwas
   unbemerkt?
4. **Anwesenheits-Test:** Wer ist wo? Gueyuek in 025 "nicht anwesend",
   aber "war der Raum" – Stilmittel oder Behauptung (hinter dem
   Vorhang)? Gegen 024 (Dekrete aus der Kanzlei) und 026 abgleichen.
5. **Zeit-Test:** 025 Winter/Karakorum/Gericht -> Kanzlei am selben Tag?
   024 war "dritter Tag nach Kuriltai". Passt 024->025->026?

### Schicht 4 – Urteil: Stilmittel vs. Fehler

Anapher, Litanei, "Gueyuek war der Raum" sind Stil. Eine Figur, die tot
ist und wieder auftritt, ist ein Fehler. Dazwischen: markieren, nicht
blockieren.

## Angewandt auf Kapitel 025 ("Der Onkel") – konkrete Pruefpunkte

- **Temuege:** "Siebzig, vielleicht mehr", "juengster Bruder, letzter
  Ueberlebender" – gegen 028/037 abgleichen (Alter, Rang, lebt er nach
  025 noch?). 025 endet mit Verurteilung als Praezedenz – wird das in
  026–028 als Praezedenz *benutzt* (gut) oder vergessen (Bruch)?
- **Zwei Buecher:** blau-weisses Buch (offiziell, gesiegelt) vs.
  Privatakte mit "ehrlicher Minute" (025-Schluss). Passt zu
  044/046/047 ("drei Archive", leere Seite, Akte fuer Juvaini)? Das ist
  der tragende Bogen – hier lohnt der Abgleich am meisten.
- **Jiguedei-Chronik:** 025 sagt, Shigi habe "drei Tage zuvor mit
  Jiguedei die Chronik in die Steppe geschickt, vergrabenes Buch".
  Gegen 024 pruefen: war er da schon beobachtet? War Jiguedei schon
  eingefuehrt?
- **Gueyueks Dekrete (024) -> Temuege-Prozess (025):** 024 kuendigt
  Saeuberung an, 025 vollstreckt am Onkel. Kausalkette ok – aber ist die
  Anklage (Truppenbewegung im Interregnum ohne Genehmigung) dieselbe,
  die 024 angedroht hat?
- **Hoe'eluen-Satz** ("Gesetz verhindert Willkuer, garantiert keine
  Gerechtigkeit") – Erstauftritt oder Wiederholung? Wenn Wiederholung:
  Wortlaut identisch?

## Umsetzung – zwei Stufen, Kosten im Blick

### Stufe A (kostenlos, deterministisch)

Neues Skript `tools/check_continuity.py`:

```bat
py -3 tools/check_continuity.py --book die-dritte-chronik --chapter 025 --window 024-026
```

- Figuren-/Requisiten-Nennungen pro Kapitel zaehlen,
- Anwesenheits-Matrix bauen (aktiv/erwaehnt/abwesend),
- Requisiten-Orte extrahieren ("legte X in Y"),
- Wissens-Verben flaggen ("er wusste / sie erfuhr / er verschwieg"),
- Ausgabe: Continuity-Bericht als `.md` neben die Reviews, **kein
  Gate-Effekt** (INFO/WARNING, nie ERROR).

### Stufe B (mit LLM, nur nach Freigabe – kostet)

Dasselbe Fenster 024–026 an ein Modell geben mit Auftrag: "Finde genau
diese fuenf Widerspruchstypen, zitiere woertlich, erfinde nichts."
Ergebnis manuell bestaetigen, dann ggf. Arc-Protokoll als
`work/continuity/arcs.md` festschreiben.

## Offene Vorfragen (vom Nutzer zu entscheiden)

1. **Fenster:** Nur 025 + Nachbarn (024/026), oder gleich Shigi-Bogen
   024–033?
2. **Verbindlichkeit:** Nur Lese-Bericht, oder festes `arcs.md`, gegen
   das spaetere Kapitel automatisch geprueft werden?
3. **Gueyuek-Frage 025:** "War der Raum" als Stilmittel abhaken, oder
   pruefen, ob er physisch hinter dem Vorhang sass?
