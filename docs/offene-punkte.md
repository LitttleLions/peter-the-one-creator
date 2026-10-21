# Offene Punkte / Arbeitsplan

Stand: 2026-10-08. Quelle: `AGENTS.md`, `README.md`, `docs/HANDOVER.md`.

Pflege: Bei Erledigung Status + Datum in der jeweiligen Sektion aktualisieren.
Dieses Dokument ist die verbindliche Checkliste, auf die aus der `README.md`
(Sektion `Arbeitsplan / Offene Punkte`) verwiesen wird.

Grundregeln fuer alle Translate-Laeufe:

- Uebersetzungslaeufe mit `openrouter` nur nach ausdruecklicher Freigabe (Kosten).
- Immer zuerst `--dry-run` mit `--provider prompt_file` (read-only, keine Kosten).
- Batch-Laeufe immer mit `--auto-status`, sonst driftet `status.json` auf `pending`.
- `book.yaml`-Defaults (`ai.model`, `ai.reasoning_effort`) nicht per CLI ueberschreiben.
- Windows-Hinweis: `py -3` statt `python` nutzen (blockiertes hermes-venv).

## 0. [VORGEZOGEN] Pruefung Uebersetzung Peter der Erste (`peter-i-buch-01`)

Status: Phase A + B abgeschlossen 2026-09-17. **Nachtrag 2026-09-17:** Der
Vollscan aller 175 Szenen fand drei weitere geraffte Szenen, die der
Regelcheck nicht gemeldet hatte (Ratio-Blindfleck 0.76-0.91). Sie wurden mit
demselben Chunking-Verfahren neu uebersetzt, der Regelcheck wurde um zwei
Kategorien nachgeruestet (siehe 0.1, Abschnitt "Nachtrag").

Anlass: zwei 1-Stern-Kindle-Rezensionen ("schlecht uebersetzt",
"sinnentstellend"). Nutzerhinweis: Rezensionen koennen auch Konkurrenz sein,
Verkaeufe ungeprueft, nur eine Kindle-Version. Entscheidung des Nutzers:
Volluebersetzung (nicht Lesefassung), erst technische Fehler fixen, dann die
drei gerafften Szenen vollstaendig neu, dann Vollscan, dann Export neu.

Stand aus Repo (2026-09-16, read-only geprueft):

- `book.yaml`: `style_mode: stil-02-poetisch`, `structure.mode: scenes`,
  Gruppen erstes-buch 001-007, zweites-buch 008-012, drittes-buch 013-018.
  Modell: `deepseek/deepseek-v4-pro`.
- `status.json`: 001-007 `needs_review=true`, 008-018 `done`.
- `export.yaml`: `website.enabled: true` mit Amazon-URL,
  `marketing.enabled: true` mit Song-01.
- Vorhanden: `exports/stil-02-poetisch/book/{docx,epub,pdf}`,
  `exports/marketing/`, `work/assembled/stil-02-poetisch/`.

Pruefgegenstand (Vorschlag, vom Nutzer zu bestaetigen):

- DE-Szenen `work/scenes/de/stil-02-poetisch/NNN/` gegen RU-Szenen
  `work/scenes/ru/NNN/` fuer 001-007.
- Zusammengesetzte Kapitel `work/assembled/stil-02-poetisch/`.
- Buch-Export `exports/stil-02-poetisch/book/epub/*.epub` (Leseprobe).
- Namen aus `names.yaml`, Stil aus `styles/stil-02-poetisch.md`.

Checkliste:

```bat
:: 1. Status sichten
py -3 tools/status.py --book peter-i-buch-01 summary
py -3 tools/status.py --book peter-i-buch-01 list
:: 2. Dateien sichten (lesend, kein LLM):
:: books/peter-i-buch-01/work/scenes/de/stil-02-poetisch/001/ ...
:: books/peter-i-buch-01/work/assembled/stil-02-poetisch/ ...
:: books/peter-i-buch-01/exports/stil-02-poetisch/book/epub/*.epub
:: 3. Befunde unten eintragen, dann entscheiden: behalten / Profil schaerfen + --overwrite / Export neu
```

Noch vom Nutzer zu ergaenzen:

- ~~Welche Kapitel zuerst~~ erledigt: alle 18, plus Stichproben.
- ~~Voll vs. Lesefassung~~ entschieden: **Volluebersetzung**.
- ~~Freigabe fuer Phase B~~ erteilt 2026-09-17: Phase B laeuft.
- ~~Erfundene Auftakt-Blockquotes behalten?~~ entschieden 2026-09-17:
  **bleiben** (siehe Klasse 3).

## 0.1 Fehlerklassen und Vermeidung bei der Neuuebersetzung

Die gefundenen Fehler in drei Klassen, mit Ursache und Gegenmassnahme. Diese
Liste ist die Grundlage fuer Phase B und fuer alle weiteren Buecher.

### Klasse 1: Mischschrift / akzentuierte Transliteration (12 Stellen, ERROR)

Beispiel: `Dunkа` (kyrillisches а), `Boborykин`, `Dьяk`, `Wosnizyн`,
`Pitschuга`, `Golowín`, `Krapotkín`, `Dják`.

- Ursache A: Das Modell transliteriert selbst und bricht mitten im Wort ab;
  fehlende `names.yaml`-Eintraege erzwingen Raten.
- Ursache B: Das russische Betonungszeichen wird als Akut uebernommen
  (`Головин` -> `Golowín`) statt in die Glossarform `Golowin`.
- Gegenmassnahme: Glossar lueckenlos halten (jetzt ergaenzt: Golowin,
  Wosnizyn, Boborykin, Pitschuga, Dunka, Djak, Krapotkin, Wereschtschagin,
  Petelin). Der Prompt-Hierarchie-Mechanismus (Glossar schlaegt Profil) war
  korrekt, nur die Abdeckung fehlte. Zusaetzlich prueft
  `accented_transliteration` kuenftig automatisch gegen das Glossar.
- Frueher erkennen: `review_manuscript.py --llm none` (Sekunden, kostenlos).

### Klasse 2: Raffung langer Szenen (3 Szenen, ERROR/WARNING)

011/03 ratio 0.49, 002/11 0.69, 003/05 0.60.

- Ursache: sehr lange Szenen (011/03 = RU 9470 Woerter) liefen in einem
  einzigen Call; das Modell kuerzt dann Absaetze.
- Gegenmassnahme: Chunking aktiv lassen (`book.yaml`-Limit,
  `tools/lib/translation_chunks.py`), nicht per CLI aushebeln. Danach
  `length_ratio` pruefen; Ausreisser gegen die Quellabsaetze lesen, nicht
  blind eine Wortzahl fordern.
- Wichtig: keine Sinnverdrehung gefunden (kein wer-tut-was vertauscht, keine
  Verneinung gekippt). Die Rezension "sinnentstellend" trifft die Raffung,
  nicht eine Verdrehung.

### Nachtrag 2026-09-17: Raffung im Ratio-Blindfleck (3 weitere Szenen)

Der Vollscan **aller 175 Szenen** (DE/RU-Wortverhaeltnis plus Absatzvergleich
gegen die RU-Quelle) fand drei weitere geraffte Szenen. Der Regelcheck hatte
sie nicht gemeldet, weil die WARN-Schwelle bei `< 0.75` lag:

| Szene | DE/RU-Woerter | Ratio | Absaetze DE:RU |
| --- | --- | --- | --- |
| 010/scene-02 | 4490 / 5909 | 0.76 | 102:152 (-50) |
| 010/scene-01 | 4766 / 5678 | 0.84 | 107:169 (-62) |
| 009/scene-08 | 4932 / 5415 | 0.91 | 109:182 (-73) |

Kontext: Buch-Median **1.30** (Q25/Q75 1.27/1.36) bei 175 Szenen; nur 4 Szenen
lagen unter 1.00 (davon 003/04 mit 0.97 = grenzwertig, aber unauffaellig,
Absatzdefizit nur -7). Ein Segmentvergleich ueber je 10 Textbloecke zeigte
**keine** Kuerzung am Ende, sondern gleichmaessige Verdichtung ueber die ganze
Szene - also Raffung, kein abgebrochener Lauf.

- Frueher erkennen: Der neue `paragraph_drop`-Check (Absatzdefizit) und der
  buchweite `length_outlier`-Check (relativ zum Buch-Median) melden genau
  diese Faelle automatisch. Siehe "Arbeitsweise, die das verhindert".

### Regelcheck-Nachruestung 2026-09-17

Zwei neue deterministische Kategorien in `tools/lib/review_checks.py`
(Release-Gate-Verhalten unveraendert: nur ERROR blockiert den Export):

- `paragraph_drop`: DE-Absaetze gegen Quell-Absaetze einer Szene. WARNING ab
  Verhaeltnis `< 0.85`, ERROR ab `< 0.55`; geprueft erst ab 20 Quellabsaetzen.
  Zusaetzlich muss die Wortzahl unter `0.95` x der Quelle liegen - reines
  Verschmelzen kurzer Dialogabsaetze laesst die Wortzahl unveraendert und ist
  kein Raffungssignal. Das ist der zuverlaessigste Raffungsindikator, weil die
  Wort-Ratio Raffung im Band 0.75-0.95 nicht von Straffung unterscheiden kann.
- `length_outlier`: buchweite Auswertung nach dem Sammeln aller Kapitel.
  Median aller Szenen-Ratios (>= 10 Szenen), WARNING ab `< 0.72` x Median,
  ERROR ab `< 0.55` x Median (obere Seite 1.5 x / 2.0 x). Damit wird die
  Schwelle nicht mehr fix geraten, sondern am Buchstil gemessen.
- Kalibrierung am Live-Bestand (Peter, 175 Szenen): Median 1.30. Mit 0.72 x
  Median liegen die drei echten Raffungen im Meldebereich, waehrend 003/04
  (0.97, Absatzdefizit nur -7) und die fuenf reinen Absatz-Verschmelzungen
  (Wortratio 1.23-1.38) nicht mehr gemeldet werden.
- Tests: 5 neue Faelle in `tests/test_review_manuscript.py` (22 Tests gesamt,
  gruen). Diagnose-Scan ohne Regelcheck:
  Szenen-Wortratio + Absatzvergleich ueber alle Szenen eines Buchs.

### Klasse 3: Erfundene Auftakt-Blockquotes (Lede)
018/01 begann mit einem erfundenen Zitat **komplett auf Russisch**, im
Original nicht vorhanden.

- Entscheidung des Nutzers (2026-09-17): Die erfundenen Auftakt-Blockquotes
  **bleiben** - sie sind auf Amazon als erfunden gekennzeichnet, beschreiben
  die Zeit gut, und der Roman ist selbst Fiktion. Abschnitt A des Profils
  bleibt also in Kraft.
- Der Fehler war nicht die Erfindung, sondern die **Sprache**: Der Auftakt
  stand in der Ausgangssprache und mit kyrillischen Zeichen, obwohl er Teil
  der deutschen Ausgabe ist.
- Gegenmassnahme (umgesetzt): `styles/stil-02-poetisch.md` Abschnitt A stellt
  jetzt klar: Auftakt immer auf Deutsch, niemals in der Ausgangssprache,
  niemals kyrillisch; Auftakt ist bewusst als redaktioneller Auftakt
  gekennzeichnet (Impressum). Zusaetzlich behaelt der Chunk-Frontmatter-Block
  `build_chunk_frontmatter()` den Auftakt nur fuer den **ersten** Chunk einer
  Szene, damit gechunkte Szenen nicht mehrere Auftakte bekommen.

### Klasse 4 (kosmetisch): doppelte Szenenueberschrift

`## Szene N` plus `## N` aus der Quelle. Behoben fuer 002/02, 03, 04, 07;
`duplicate_heading` ist jetzt eine eigene Kategorie im Regelcheck.

### Arbeitsweise, die das verhindert

1. Nach jedem Lauf `review_manuscript.py --llm none --fail-on-errors` laufen
   lassen; ERROR > 0 heisst: nicht assemblieren, nicht exportieren.
2. Export nur ohne Bypass. `--allow-review-errors` bleibt fuer Ausnahmen und
   steht danach im Manifest.
3. Kleine Stichprobe RU<->DE lesen (3-4 Szenen je Stil), weil der Regelcheck
   Sinnfragen nicht beantwortet. Das ist der Teil, den nur ein Mensch sieht.
4. Kein `--overwrite` ueber ganze Kapitel: nur die belegten Szenen neu.
5. Nach Profilaenderungen die betroffenen Szenen bewusst neu erzeugen, sonst
   bleibt der alte Stil neben dem neuen stehen.
6. Nach jedem vollen Buchlauf **beide** Laengen-Signale lesen:
   `paragraph_drop` (Absatzdefizit gegen die Quelle) und `length_outlier`
   (Szene relativ zum Buch-Median). Ein gruener `length_ratio`-Korridor
   allein ist kein Nachweis - er hatte 2026-09 drei geraffte Szenen mit
   Ratio 0.76-0.91 durchgelassen.
7. Die neueuebersetzten Szenen einzeln mit `--chunk-char-limit 7000`
   erzeugen (nicht 24000) und danach den vollen Regelcheck ohne Bypass
   laufen lassen.
8. Review im Dashboard (Action `review`) ruft `tools/review_manuscript.py` als
   CLI auf - die neuen Kategorien laufen also mit. **Scope beachten:** der
   buchweite `length_outlier`-Median braucht mindestens 10 Szenen im Scope,
   also "Ganzes Buch" waehlen; `paragraph_drop` laeuft auch kapitelweise.
   Neue Kategorien brauchen keine Frontend-Aenderung: die Befundliste rendert
   generisch ueber `severity`/`message` (ohne Auto-Ersetzung, weil
   `current_text`/`suggested_text` leer bleiben).

### Checkliste fuer die naechste Aktualisierung dieses Dokuments

- [ ] `paragraph_drop` + `length_outlier` in einem echten Buchlauf pruefen
      (Peter 2026-09-17 gelaufen) und Schwellen bei Fehlalarmen nachziehen.
- [ ] `names.yaml`-Abdeckung vor jedem neuen Buch pruefen, sonst laeuft
      `accented_transliteration` leer (Check greift nur fuer Glossarformen).
- [ ] Chunking-Limit pro Buch in `book.yaml` bewusst setzen (Default global
      24000; Peter wurde mit 7000 nachgezogen).
- [ ] Offen: `AGENTS.md`-Kategorienliste im Release-Gate-Abschnitt um
      `paragraph_drop`/`length_outlier` ergaenzen.
- [x] Fruehere `AGENTS.md`/`README.md`-Aenderungen aus dem Verifikationslauf:
      erledigt 2026-09-17 bewusst weitergefuehrt (Doku-Auftrag des Nutzers).
      `AGENTS.md`, `README.md`, `docs/HANDOVER.md` und dieses Dokument sind
      inhaltlich auf demselben Stand (Raffungs-Checks, Peter-Abschluss).
- [x] Wissen fuer neue Chats aktualisiert (2026-09-17): `AGENTS.md`
      (Release-Gate-Kategorien, Aktueller Stand), `README.md` (Export/
      Release-Gate), `docs/HANDOVER.md` (Stand 2026-09-17, Fallstrick 6,
      Tools, naechste Schritte), dieses Dokument.

## 0.2 Release-Gate (gilt fuer alle Buecher, umgesetzt 2026-09-16)

Der eigentliche systemische Fehler war: **ein Export durfte mit ERROR=7 nicht
live gehen.** Das ist jetzt technisch verhindert.

```text
Translation -> Deterministic QA -> ERROR>0 ? -> STOP
            -> Length/Completeness -> Ausreisser ? -> manuell/LLM
            -> Glossar/Name-Validierung -> EPUB -> Kindle Preview -> Release
```

Umgesetzt in:

- `tools/export_manuscript.py`: `preflight_review_gate()` laeuft vor jedem
  Export deterministisch ueber die Scope-Kapitel und bricht bei ERROR>0 mit
  Exit 2 ab. Bypass nur explizit mit `--allow-review-errors`; der Bypass wird
  im Export-Manifest als `review_gate_bypassed` + `review_gate_errors`
  protokolliert.
- `tools/lib/review_checks.py`: neue release-blockierende Kategorie
  `mojibake` (UTF-8-als-Latin-1: `Ã`, `Ð`, `Ñ`) und
  `accented_transliteration` (akzentuierte Variante einer Glossarform, z. B.
  `Golowín` -> `Golowin`; nur wenn die akzentfreie Form in `names.yaml` steht,
  damit `Molière`, `Báthory` unberuehrt bleiben).
- Ausnahme-Mechanik fuer echte Originalzitate: `work/review-allowlist.yaml`
  (`review_allowlist_path()` + `load_original_quote_allowlist()`); nur exakt
  hinterlegte Zitate werden vor dem Zeichen-Check entfernt.
- `tools/review_manuscript.py --fail-on-errors`: Exit 2 bei ERROR>0 fuer
  Skripte/CI.

Verifikation 2026-09-16:

```bat
:: Gate blockt (Exit 2) - Kapitel 011 hat ERROR
py -3 tools/export_manuscript.py --book peter-i-buch-01 --scope chapter --chapter 011 --style stil-02-poetisch --format epub --allow-partial --dry-run
:: Gate laesst durch (Exit 0) - Kapitel 004 ist jetzt sauber
py -3 tools/export_manuscript.py --book peter-i-buch-01 --scope chapter --chapter 004 --style stil-02-poetisch --format epub --allow-partial --dry-run
```

Befunde / Entscheidungen:

- 2026-09-16 Scan `--llm none` ueber alle 18 Kapitel, Ausgangsstand:
  **ERROR=7, WARNING=6**. Der vorherige Report (2026-06-15, 0 Befunde, nur
  Kap. 006 OK) war veraltet und hat nichts geprueft.
- **Korrektur eines frueheren Befunds:** `GÃ¼te`/`MÃ¤rz` standen nie in den
  Dateien; das war ein PowerShell-Anzeigeartefakt (UTF-8 als CP1252 gelesen).
  Buchweite Pruefung auf `Ã|Ð|Ñ|U+FFFD` in allen `.md` des Buchpakets: 0
  Treffer. Der neue `mojibake`-Check bleibt trotzdem drin (er kostet nichts
  und faengt echte Faelle kuenftig ab).
- **Behoben, ohne neuen LLM-Lauf** (`apply_review_suggestions.py --plan`,
  `--stage`, `--promote`; Sicherungskopien `*.bak-<stamp>` daneben):
  - Mischschrift/kyrillische Reste: 004/04 `Dunkа`->`Dunka`,
    005/13 `Boborykин`->`Boborykin`, 007/03 `Dьяk`->`Djak`,
    007/06 `Wosnizyн`->`Wosnizyn`, 007/10 `Pitschuга`->`Pitschuga`.
  - Akzent-Transliteration (neuer Check, 7 Stellen): 005/20, 007/08,
    007/16 `Golowín`->`Golowin`; 007/10 `Krapotkín`->`Krapotkin`,
    `Wereschtschagín`->`Wereschtschagin`, `Petelín`->`Petelin`;
    009/09 `Dják`->`Djak`.
  - Doppelte Szenenheader: 002/02, 002/03, 002/04, 002/07.
  - Lede 018/01: der erfundene Auftakt-Blockquote stand **komplett auf
    Russisch** (nicht im Original) und war doppelt encodiert. Ersetzt durch
    eine deutsche Fassung.
  - `names.yaml` erweitert (Golowin, Wosnizyn, Boborykin, Pitschuga,
    Dunka, Djak, Krapotkin, Wereschtschagin, Petelin), damit der neue
    Akzent-Check greifen kann und weitere Laeufe die Formen kennen.
- **Offen, nur per Neuuebersetzung zu loesen (Phase B, Volluebersetzung):**
  - 011/03 ratio **0.49** (RU 9470 / DE 4652) -> ERROR. Schlacht-Vorgeschichte,
    Marketender-Verkauf, Golikow-Verhoer, komplette Zelt-Rede fehlen.
  - 002/11 ratio 0.69 (WARNING) -> Menuett-Aufzug, Contretanz-Figuren, Ritt,
    Zotow-Segen fehlen.
  - 003/05 ratio 0.60 (WARNING) -> Anchen-Sonntage, Kreml-Klatsch, Filka,
    Lopuchina-Brautwerbung fehlen.
  - Manuell gegen RU geprueft: keine Sinnverdrehung (kein wer-tut-was
    vertauscht, keine Verneinung gekippt), aber spuerbare Raffung.
  - Vorgehen: gezielt je Szene mit `--overwrite` und aktivem Chunking
    (`work/chunks/`, `translation_chunks.py`), nicht ganze Kapitel.
  - Erledigt 2026-09-16: `styles/stil-02-poetisch.md` Abschnitt A verlangte
    erfundene Auftakt-Blockquotes je Szene — das war die Quelle der
    018/01-Lede und widersprach den harten Ausgabe-Regeln ("nichts
    ergaenzen"). Abschnitt A ist jetzt ein Uebernahme-Auftrag: vorhandener
    Auftakt/Motto/Zitat aus der Quelle wird uebernommen, nichts erfunden;
    ohne Auftakt in der Quelle beginnt die Ausgabe direkt mit der
    Uebersetzung. Damit produziert der Phase-B-Neulauf keine neuen
    Lede-Artefakte mehr.
- Stichproben (RU<->DE gegenlesen): 001/01 OK; 004/04, 007/10, 018/01
  inhaltlich treu (nur Zeichenfehler); 011/03, 002/11, 003/05 gerafft aber
  nicht verdreht.
- Systematik: kein Hinweis auf Totalverhunzung. Zwei reale Muster erklaeren
  die 1-Stern-Rezensionen auch ohne Konkurrenz-These: (a) Mischschrift/
  Akzent-Artefakte an ~12 Stellen (auf Kindle Kauderwelsch), (b) Raffung
  langer Szenen (0.49-0.69), was Kennern des Originals als "sinnentstellt"
  erscheint.
- Endstand nach den Fixes: **ERROR=1** (nur 011/03), WARNING=2
  (002/11, 003/05). Report:
  `work/reviews/stil-02-poetisch/review-summary.md`.
- Nach Phase B: Vollscan erneut (`--fail-on-errors`), danach Buch-EPUB neu
  exportieren (`--format epub`, ohne `--allow-review-errors`) und im Kindle
  Previewer pruefen. Ergebnis hier eintragen.

## 1. Marketingexport pruefen + committen

Was: `tools/export_marketing.py` + Libs + `config/marketing.yaml` +
Dashboard-Karte Export -> Marketingpaket + X-Clip sind implementiert,
Stand HANDOVER 09-14 noch nicht (vollstaendig) committet. Pilot fuer
`peter-i-buch-01` lief ohne Kosten; Amazon-Link + Songs werden als
`omitted/blocked` ausgewiesen statt erfunden.

Warum zuerst: kein Kostenrisiko, kein Stilrisiko, macht `git status` sauber.

Checkliste:

```bat
git status --short
git diff --stat
py -3 -m unittest tests.test_marketing_campaign tests.test_marketing_prompts tests.test_marketing_api
py -3 tools/export_marketing.py --book peter-i-buch-01 --dry-run
py -3 tools/start_dashboard.py
:: -> http://127.0.0.1:8000 -> peter-i-buch-01 -> Export -> Marketingpaket pruefen
:: -> X-Clip nur pruefen (braucht System-ffmpeg fuer echten Render)
```

Offen danach: `export.yaml` top-level `marketing:` mit `campaign_start`,
`youtube.{url,video_id,public}`, `songs[]`, `amazon_url` (primaer aus
`website.amazon_url`). Echter Textlauf nur mit Freigabe. Details:
`docs/marketing-export.md`.

Status: OFFEN.

## 2. Top-5-Pakete: Stilurteil + 110 offene Kapitel [KERN]

Was: 4 Roh-Pakete 09/2026, alle `structure.mode: chapter_as_scene`,
Default `stil-01-original`, Modell `deepseek/deepseek-v4.1-flash` +
`ai.reasoning_effort: none` in `book.yaml`:

- `kuprin-duell` - 23 Kap. (I-XXIII)
- `kuprin-moloch` - 11 Kap.
- `grin-wellenlaeuferin` - 33 Kap.
- `pissemski-tausend-seelen` - 44 Kap. in 4 Teilen

Stand: Pilot `kuprin-moloch` 001 vom 2026-09-13: 6682 Tokens
(Prompt 4206 / Completion 2476), `finish_reason=stop`, 1245 DE-Woerter
(119% von 1049 RU), Status `needs_review`. Kette belegt: extract ->
translate -> assemble -> epub (1,1 MB, nutzt `assets/covers/cover.png`).

Warum Stilurteil zuerst: alle 4 nutzen Default `stil-01-original`.
Bei Missfallen nach 110 Kapiteln alles mit `--overwrite` neu noetig.

Fallstricke: ohne `--auto-status` driftet `status.json`; `--model` und
`--reasoning-effort` nicht am Batch mitgeben (kommen aus `book.yaml`,
`none` ist Pflicht); `website:` nur top-level; Dry-Run 111 Kap. /
221 Kommandos belegt.

Checkliste:

```bat
:: A. Stilurteil lesend (kein LLM):
:: books/kuprin-moloch/work/scenes/de/stil-01-original/001/scene-*.md
:: + assembled 001-*.md + exports/.../chapter/epub/*.epub
:: B. Trockenlaeufe je Buch (read-only):
py -3 tools/translate_batch.py --book kuprin-moloch --missing --style stil-01-original --provider prompt_file --dry-run
py -3 tools/translate_batch.py --book kuprin-duell --missing --style stil-01-original --provider prompt_file --dry-run
py -3 tools/translate_batch.py --book grin-wellenlaeuferin --missing --style stil-01-original --provider prompt_file --dry-run
py -3 tools/translate_batch.py --book pissemski-tausend-seelen --missing --style stil-01-original --provider prompt_file --dry-run
:: C. Echt NUR mit Freigabe, pro Buch:
:: py -3 tools/translate_batch.py --book kuprin-moloch --missing --style stil-01-original --provider openrouter --auto-status --assemble-after
:: D. Status pruefen
py -3 tools/status.py --book kuprin-moloch summary
```

Reihenfolge: Moloch-Rest (10) -> Duell (23) -> Grin (33) -> Pissemski (44).

Status: OFFEN (Pilot gelesen, Stilurteil fehlt).

## 3. Regal-Freigabe Top-5 + Cover-Sync

Was: Handcover 688x1024 PNG je Top-5-Buch liegen im Repo. Entscheidung
09-13: EPUB-first, reicht auch fuer Amazon; Print erst fuer KDP-Paperback.
Regal-Kopien fuer aelita/mongolen unter `webpage/public/covers/` noch alt.
Offen: `website.enabled: false`, `sort_order: 40` bei allen 4.

Checkliste:

```bat
py -3 tools/build_shelf_website.py
py -3 tools/preview_webpage.py
```

In je `export.yaml` top-level setzen (NICHT unter `book:` einruecken):
`enabled: true`, `amazon_url: ''`, `sort_order: 40` (Vorschlag: duell 40,
moloch 41, grin 42, pissemski 43 nach Cover-Wahl). Cover bleiben Handarbeit.

Status: OFFEN.

## 4. Anna Karenina: 73 offene Kapitel

Was: `chapter_as_scene`, Default jetzt korrekt `stil-02-poetisch`.
Stand nach Status-Fix: 166/239 fertig (Teil `needs_review`), 167-239 offen.

Checkliste:

```bat
py -3 tools/status.py --book anna-karenina summary
py -3 tools/translate_batch.py --book anna-karenina --missing --style stil-02-poetisch --provider prompt_file --dry-run
```

Echt nur mit Freigabe mit `--provider openrouter --auto-status --assemble-after`.

Status: OFFEN.

## 5. Geheime Geschichte der Mongolen: 284 Szenen Monolithen

Was: Quelle `ja->de`, `structure.mode: scenes`, ca. 317 Abschnitte.
`stil-04-original-geheim` = Interlinear/Edition (kein Lesestil).
Stand: Kap. 006 fertig (20/20 in stil-04, Review-Marker bleibt).
Offen: 000, 001-005, 007-013 = 284 Szenen + Szene 07 in 014.
Kritisch: immer `--style stil-04-original-geheim` explizit mitgeben.

Checkliste:

```bat
py -3 tools/status.py --book geheime-geschichte-mongolen summary
py -3 tools/translate_batch.py --book geheime-geschichte-mongolen --missing --style stil-04-original-geheim --provider prompt_file --dry-run
```

Echt nur abschnittsweise + Freigabe.

Status: OFFEN.

## 6. Dritte Chronik: Gate 0/13/36 + Redaktionstabelle (Stand 2026-09-19 abends)

Was: DE-Original, kein Uebersetzungsprojekt. Cover liegt.
2026-09-18 frueh: 4 ERROR + 7 WARNING redaktionell behoben (041 `решил`/
`别的`-CJK/`für warhielt`, 043 `Fдер`, 033/036 + 012/018/026/031/034/035
`long_sentence` gegliedert; Work-Spiegel + `source/` synchronisiert mit
`.bak-20260918`); echter Buch-EPUB
`book-die-dritte-chronik-stil-01-original-20260918-172522.epub`
(Gate 0/0 ohne Bypass). Danach Stil-Detektor `tools/lib/repetition.py`
(6 Signale: Anapher/Trigramm/Echo/Stapelung/TTR/Leerformel, Kategorie
`repetition_style`, nur INFO/WARNING, nie ERROR) in
`tools/lib/review_checks.py` eingebunden; Review war
ERROR=0/WARNING=41/INFO=48 (Gate weiter gruen, EXIT 0); Tests
`tests/test_repetition.py` (6) + `tests/test_review_manuscript.py`
(23) + Full Suite (248) gruen. `test_chapter_008_is_clean_after_redaction`
belegt 008 clean 0/0 (Nutzer-Neufassung); die Fixtures
(`EXAMPLE_ANAPHORA` INFO, `EXAMPLE_CHINQAI` WARNING) decken den Detektor
weiter ab.
2026-09-18 abends (Redaktion ohne OpenRouter, keine Kosten): 008 clean
0/0 (Nutzer-Neufassung 2429 W, Chinqai-Stapelungen + `er-las` +
`morgen-kommt` weg), 012 clean 0/0 (Nutzer-Neufassung 2362 W,
Gouverneur-Mahmud-Falle + Blatt-Test; `work/chapters/012-source.md` im
Kopfformat synchronisiert, `source/` unberuehrt), 034 nur Satzzeichen
(Monster-Zeile 45: 672 W/4012 Zeichen ohne Punkt -> 6 Absaetze, dazu
Zeile 39 + 68 mit Komma/Punkt; 5W->2W, Rest `mein`/`brannt`-Litanei).
Voll-Review danach ERROR=0/WARNING=31/INFO=46 (Zwischenstand 18.09.,
von der 19.09.-Runde auf 0/13/36 abgeloest); Buch-EPUB
`book-die-dritte-chronik-stil-01-original-20260918-201109.epub`
(48/48, ohne Bypass). Ablauf je Kapitel: Nutzer legt Neufassung unter
`books/die-dritte-chronik/status/Die dritte Chronik - NN <Titel>.md`
(nutzt auch mal `work/scenes/de/NNN/scene-01.md`) -> KI prueft auf
Textbruch und kopiert nach
`work/scenes/de/stil-01-original/NNN/scene-01.md` (+ bei Neuschreibung
`work/chapters/NNN-source.md` synchronisieren) -> `assemble_chapter.py`
-> `review_manuscript --chapter NNN --llm none` -> Voll-Review ->
Buch-EPUB neu. Bei Textbruch (Fassung passt nicht zur Kapitelquelle)
STOPP + Rueckfrage (Fall 012-Entwurf mit 4893 W, 2026-09-18).
Bilder: komplett seit 2026-09-19 (48/48 - Kapitelbild 001-014, Szenenbild
008 + 015-048 = 49 Bilder + Cover). Das EPUB mit Bebilderung ist
`...-20260919-222611.epub` (50 Bilder, alle JPEGs validiert).
Offen: Leser-EPUB pruefen (Kindle Previewer) + frischer DOCX/PDF-Bau.

2026-09-19 (Redaktion ohne OpenRouter, keine Kosten; komplett- + mini-Runde):
komplett-Runde = Nutzer-Neufassungen 031/033/036. 031 `Der Handel`
(3753 W; Schachtelsaetze 133/87/59 W + `dies`/`sprach`-Echos weg, Rest
`sie-dachte`-Anapher = Stilmittel), 033 `Das Siegel` (3539 W; die drei
Tuerme 166/164/160 W + `anders`-Echo + TTR 0,21 weg = clean 0/0),
036 `Eingenäht` (Neuschreibung 785 W; Stapelungen 130/149/116 W +
`anders`-Echo + TTR 0,22 weg = clean 0/0). `work/chapters/031|033|036-source.md`
im Kopfformat synchronisiert, `source/` unberuehrt. mini-Runde von der KI
selbst (nur Satzzeichen/Gliederung, Backups `*.bak-20260919-mini`):
009 clean 0/0 (Echo-Ketten `hinaus`/`zurueck`/`mitten` gegliedert),
026 clean 0/0 (122-W-Litanei), 035 clean 0/0 (127-W-Notizbuchsatz;
Hinweis: die Stelle `als sie 'dich' sagte` wurde zu „so vertraut mit ihm
sprach wie nie zuvor" umformuliert, weil die Anfuehrungszeichen um das
Einzelwort die Ersetzung stoerten - inhaltlich identisch), 018 0W/4I und
041 0W/1I (Anaphern/TTR-Folge = Stilmittel). Endstand: Voll-Review
ERROR=0/WARNING=13/INFO=36 (Exit 0), 29/48 Kapitel clean. Tagesbilanz:
WARNING 31 -> 13, INFO 46 -> 36.
2026-09-19 abends (Bebilderung nachgezogen): Szenenbilder 021-048
generiert -> 48/48 Kapitel bebildert (Kapitelbild 001-014, Szenenbild
008 + 015-048 = 49 Bilder + Cover). Buch-EPUB
`book-die-dritte-chronik-stil-01-original-20260919-222611.epub`
(4,99 MB, 50 Bilder, alle JPEGs validiert, 48/48 Kapitel, Gate 0 Fehler,
ohne Bypass).
Release-Einschaetzung 2026-09-19: Text + Bilder bereit; offen sind
(1) frischer DOCX/PDF-Bau vom aktuellen Stand, (2) menschliche Leseprobe
(Kindle Previewer + Stichprobe 031/033/036 und je eine Stelle aus
009/035/041).

### Chronik-Redaktionstabelle (24 Eintraege: 19 Kapitel mit Restbefund + 5 erledigte Faelle, die jetzt clean 0/0 sind und deshalb keine Review-Datei mehr haben - das Tool loescht sie bewusst, `review_checks.py` `write_reports`. Insgesamt 29/48 Kapitel clean)

| Kap | W | I | Befund-Kurzform | Einschaetzung |
|-----|---|---|---|---|
| 005 | 1 | 0 | Anapher `ich hoffe` 10x (Briefschluss) | b behalten (Stilmittel) |
| 009 | 0 | 0 | — | c erledigt 2026-09-19 (Mini-Fix: Schachtelsaetze gegliedert, Echos variiert, clean) |
| 013 | 0 | 1 | Anapher `er las` 4x | b behalten |
| 016 | 0 | 3 | Stapelung 74/59/28 W (`dass`-Kette) | b ignorieren (kurz) |
| 018 | 0 | 4 | Anaphern `ich liebe` 4x / `sag mir` 6x (Stilmittel) + INFO 69/59 W | b/c erledigt 2026-09-19 (Mini-Fix: 2 WARNING-Schachtelsaetze gegliedert; Rest Stilmittel) |
| 020 | 0 | 1 | Trigramm `deine entscheidung khatun` 4x | b Leitmotiv |
| 023 | 0 | 3 | Stapelung 66/26/43 W | b ignorieren (kurz) |
| 026 | 0 | 0 | — | c erledigt 2026-09-19 (Mini-Fix: 122W-Schachtelsatz + 2 INFO gegliedert, clean) |
| 027 | 0 | 1 | Anapher `sie schrieb` 4x | b behalten |
| 028 | 0 | 2 | Stapelung 47 W; TTR 0,22/3802 W | b ignorieren |
| 030 | 2 | 3 | Anapher `er dachte` 20x + `der morgen` 10x; `er wusste` 5x; Echo `siegel`; TTR 0,19 | b behalten (Klimax-Litanei) |
| 031 | 0 | 1 | Anapher `sie dachte` 5x (Abs.117-121) | b/c erledigt 2026-09-19 (Neufassung, 3753 W; Schachtelsaetze+Echos weg, Anapher bleibt Stilmittel) |
| 032 | 0 | 2 | Stapelung 78/31 W | b ignorieren |
| 033 | 0 | 0 | — | C erledigt 2026-09-19 (Neufassung, 3539 W; 3 Tuerme + Echos + TTR weg, clean) |
| 034 | 2 | 4 | Echo `mein` 9x, `brannt` 8x; Rest-Stapelung INFO | b/c erledigt 2026-09-18 (Monster weg; Litanei bleibt) |
| 035 | 0 | 0 | — | c erledigt 2026-09-19 (Mini-Fix: Schachtelsaetze gegliedert, Echos variiert, clean) |
| 036 | 0 | 0 | — | C erledigt 2026-09-19 (Neuschreibung, 785 W; Stapelungen + `anders`-Echo + TTR weg, clean) |
| 038 | 0 | 1 | Stapelung 86 W | b ignorieren |
| 040 | 0 | 3 | Stapelung 53/59 W; TTR 0,18/5306 W | b ignorieren |
| 041 | 0 | 1 | TTR 0,20/4860 W (Folge) | b/c erledigt 2026-09-19 (Mini-Fix: 171W + 2 INFO-Stapelungen gegliedert; TTR-Folge bleibt) |
| 044 | 0 | 2 | Anapher `er dachte` 4x + 4x | b behalten |
| 045 | 2 | 0 | Echo `dies` 11x; Stapelung `jedes/jede` 15x in 49 W | b Litanei (ggf. 1 Echo) |
| 046 | 3 | 1 | Echo `richtung` 13x + `voll` 9x; Stapelung `jede/jedes` 14x + 122 W | b Litanei (ggf. 1 Echo) |
| 047 | 3 | 3 | Echo `richtung` 13x, `laeng` 10x, `trennt` 7x; Stapelung 43 W (`laenger als`) + 38/41 W | b Litanei (ggf. 1 Echo) |

Legende: C = komplett (mehrere Schachtelsaetze gliedern), c = Mini
(1-2 Satzzeichen oder 1 Echo), b = behalten/ignorieren (Stilmittel,
Litanei, kurzes Segment, TTR-Folge). Details je Kapitel:
`books/die-dritte-chronik/work/reviews/stil-01-original/chapters/NNN-review.md`.

Checkliste:

```bat
py -3 -m unittest tests.test_repetition tests.test_review_manuscript
py -3 tools/review_manuscript.py --book die-dritte-chronik --style stil-01-original --all --llm none --fail-on-errors
py -3 tools/export_manuscript.py --book die-dritte-chronik --scope book --style stil-01-original --format epub --dry-run
```

Bilder: `docs/higgsfield-integration.md` beachten.

Status: Gate gruen (ERROR=0/WARNING=13/INFO=36, Exit 0), Redaktion
komplett+mini fertig (29/48 clean; Rest Stilmittel/Litanei/TTR), Bilder
komplett 48/48 (EPUB 20260919-222611, 50 Bilder). Offen: DOCX/PDF-Neubau,
Leseprobe.

## 7. Regal: Amazon-URLs + Deploy

Was: Button erscheint nur bei gesetzter `website.amazon_url`.
Deploy = `webpage/dist/` bauen + hosten.

Checkliste:

```bat
py -3 tools/build_shelf_website.py
py -3 tools/build_webpage_dist.py
py -3 tools/preview_webpage.py
```

URLs in `export.yaml` top-level `website:` setzen.

Deploy-Ziel (2026-10-21 geprueft):

- Live: https://stiftung.motivatier.de/classics/ – Server antwortet mit `Apache`
  und `X-Powered-By: PleskLin`, IP 87.106.3.155. Das ist dieselbe IONOS-VPS wie
  `romanforge.littlelionsfilms.de`; der Ordner `/classics/` liegt also im
  Plesk-Docroot dieser Domain (Pfad dort bestaetigen, erwartet
  `.../httpdocs/classics/`).
- Stand live: `Last-Modified` 2026-10-07, 8 Baende. `webpage/public/data/catalog.json`
  enthaelt 10 Baende; es fehlen live `grin-wellenlaeuferin` und
  `pissemski-tausend-seelen`.
- Kein SSH-Zugang vom Entwicklungsrechner (`ssh root@87.106.3.155` ->
  `Permission denied (publickey,password)`). Upload deshalb ueber den
  Plesk-Dateimanager oder von Hand per SSH von einem Rechner mit Schluessel.
- `webpage/dist/` ist per `.gitignore` nicht versioniert; hochzuladen ist der
  komplette Inhalt (`index.html`, `assets/`, `covers/`, `data/`, `models/`,
  `impressum.html`, `ueber-uns.html`), bestehende Dateien ersetzen.

Status: OFFEN – Katalog und Build mit 10 Baenden sind fertig (lokal HTTP 200,
10 Buecher), der Upload auf die Domain steht aus.

## 8. Optional: Feature-Branch aufraeumen

`codex/geheime-geschichte-mongolen-prompts` ist per Fast-Forward in `main`.
Nur remote loeschen wenn alle Clients auf `main` sind.

```bat
git branch -a --contains af6873c
```

Status: OFFEN, optional.

## 9. Bekannte rote Tests (Umgebung)

**Stand 2026-10-07:** volle Suite `py -3 -m unittest discover -s tests` ergibt
**319 Tests mit 7 Failures/Errors** ausserhalb der Stufe-1-Arbeit: 5 in
`tests/test_print_export.py` (Print/PDF-Pipeline) und die 2 bekannten in
`tests/test_backend_api.py`. Die 5 Print-Fehler sind noch nicht als bekannt
dokumentiert - vor einem Merge nach `main` pruefen, ob sie von den offenen
CSS-Aenderungen (`book-print.css`/`epub.css`) kommen. Die Stufe-1-Suite
(`tests/test_import_markdown_original.py`) ist isoliert 31/31 gruen.

**Stand 2026-09-17 (2 Failures, umgebungsabhaengig):**

`py -3 -m unittest discover -s tests` → **240 Tests, 2 Failures, beide
vorbestehend und umgebungsabhaengig** (nicht Review/Export):

- `tests/test_backend_api.py::test_action_plan_translate_batch`
- `tests/test_backend_api.py::test_job_start_allows_translate_batch`

Beide erwarten HTTP 200, bekommen aber 400. Ursache: `_validate_model_available`
in `webapp/backend/main.py` (~Zeile 597) prueft das gesendete `ollama_model`
gegen `list_ollama_models()` und blockt, wenn das Modell lokal fehlt. Der Test
sendet `gemma4:latest`; lokal laeuft Ollama mit anderen Modellen (Katalog:
`ollama/gemma4:e4b`). Ohne laufende Ollama-Instanz waeren die Tests gruen
(frueher `return` bei leerer Liste).

Fixvorschlag (nicht dringend): im Test `list_ollama_models()` monkeypatchen
oder eine vorhandene Modell-ID senden. Vorher pruefen, ob das Verhalten
gewuenscht ist (400 bei fehlendem Modell ist im Dashboard beabsichtigt).

## 10. Aelita: LIVE (5. Release 09/2026)

Was: Am 2026-09-17 abgeschlossen, vom Nutzer veroeffentlicht 09/2026:
Review-Lauf ohne KI ueber alle 30 Kapitel (ERROR=0, WARNING=0), Kapitel 005
(gewollte fiktionale Einschuebe), Kapitel 030 bereinigt – Romantext endet in
der DE-Szene, der Kommentarteil der RU-Quelle ist vollstaendig in den Anhang
„Kommentare“ uebersetzt und als Nachspann konfiguriert (top-level
`appendices:`-Block in `export.yaml`, Loader `tools/lib/editorial_appendices.py`,
Ausgabe in EPUB/DOCX/PDF, Anrechnung beim Deterministischen Check in
`review_checks.py`, 27 Export-Tests gruen). 16 vorhandene Kapitelbilder als
Export-JPG optimiert (q60, max 1600x2400). Nutzer hat das Buch-EPUB
`...-20260917-180435.epub` geprueft.

Entscheidungen des Nutzers:

- 12 Kapitel bleiben bewusst ohne Bild (009, 010, 011, 012, 016-019, 022-027).
- Wiedergefundene Higgsfield-Motive fuer 022-027 liegen zur freien Nutzung in
  `books/aelita/work/image-recovery/20260917-165216/verified/`; 011/012 sind
  nicht wiederherstellbar (403/„Job nicht gefunden“).
- Die gewollten fiktionalen Einschuebe (Blockquotes, erfundene Interviews)
  bleiben Stilmerkmal der Ausgabe; sie sind im Anhang nicht enthalten.

Checkliste:

```bat
:: Rest vor Veroeffentlichung
py -3 tools\export_manuscript.py --book aelita --scope book --style stil-03-branderson --format epub
:: EPUB im Kindle Previewer pruefen; danach Regal/Amazon-URL setzen
```

Status: LIVE. Rest: Amazon-URL + Marketingpaket nach Amazon-Freigabe (Punkt 7 + Punkt 1), Cover-JPG-Sidecar `assets/covers/cover.jpg` 09/2026 erzeugt.

## 11. Leben Arsenjews: Amazon-Freigabe + Chronik-Gate (Stand 2026-09-18)

Was: 104/104 Szenen in `stil-02-poetisch` vorhanden. Voll-Review
`--llm none --fail-on-errors` **ERROR=0, WARNING=8** (nur
`049/051/086/087 long_sentence`, `015/025/032/033 length_outlier`).
Kindle gelesen/passt, Buch auf Amazon veroeffentlicht, wartet auf
Freigabe (Stand 2026-09-18, keine Aenderung mehr).
Anna Karenina ist auf Nutzerentscheidung PARKIERT (73 pending bleiben liegen).
Dritte Chronik (DE-Original, 48/48 done): Gate 0/0 seit 2026-09-18
(EPUB `...-20260918-172522.epub` ohne Bypass); Repetition-Detektor
liefert zusaetzlich 41 WARNING + 48 INFO (Kategorie
`repetition_style`, nie ERROR) — Redaktion b/c steht aus.

Was: 104/104 Szenen in `stil-02-poetisch` vorhanden (Status 50 done / 54 review, Stand 2026-09-13, nicht nachgezogen). Voll-Review `--llm none --fail-on-errors` **ERROR=0, WARNING=8** (nur `049/051/086/087 long_sentence`, `015/025/032/033 length_outlier`-WARNING, alle nicht blockierend). Geleistet 2026-09-17 ohne OpenRouter-Kosten: 7 geraffte Szenen neu uebersetzt (029 Totalschaden 0.19, 034, 035, 039, 040, 027 Qualitaet, 037 Vorspann ca. 434 Woerter ergaenzt, Ratio 0.59 auf 1.13); Klein-Fixes 024 `Ksjucha`, 033 `stiernackiger`, 053 RU-Strophe entfernt, Allowlist `work/review-allowlist.yaml` (Puschkin 086, Gogol 096), 050 `long_sentence` redaktionell geteilt; Blockquote-Fix in 18 Szenen (002/003/005/007/008/009/013/014/023/028/041/043/065/082/083/084/086/088, je `.bak-quote`, danach je genau 1 Zitatblock); Cover neu (`cover.png` 1024x1536, 2,75 MB zu `cover.jpg` q60 ~185 KB); Buch-EPUB `book-das-leben-arsenjews-stil-02-poetisch-20260917-212334.epub` mit Gate ohne Bypass (`review_gate_errors: 0`, 104/104 Kapitel je 1/1 Szenen, 19 Kapitelbilder). Stand 2026-09-18: Kindle gelesen/passt, auf Amazon veroeffentlicht, wartet auf Freigabe — keine Aenderung mehr.
Anna Karenina ist auf Nutzerentscheidung PARKIERT (73 pending bleiben liegen).
Dritte Chronik (DE-Original, 48/48 done): Gate 0/0 seit 2026-09-18
(EPUB `...-20260918-172522.epub` ohne Bypass); Repetition-Detektor
liefert zusaetzlich 41 WARNING + 48 INFO (`repetition_style`, nie
ERROR) — Redaktion b/c steht aus.

Checkliste (Release-Kandidat, naechste Schritte):

```bat
:: Gate erneut bestaetigen (lesend, keine Kosten)
py -3 tools/review_manuscript.py --book leben-arsenjews --style stil-02-poetisch --all --llm none --fail-on-errors
:: EPUB im Kindle Previewer pruefen + menschliche Stichprobe (029/034/037/040)
:: Danach: Amazon-URL/Regal/Marketing (Punkt 7 + Punkt 1)
```

Status: Release-Kandidat, Gate gruen. Offen nur Kindle Previewer + Stichprobe.

## 12. Chronik: Kontinuitaetspruefung, Autorenbio, Reihen-Auftritt (Stand 2026-09-21)

Was: Vorschlag zur inhaltlichen Kontinuitaetspruefung liegt als
`docs/kontinuitaetspruefung-chronik.md` vor (4-Schichten-Modell:
Inventar, Arc-Protokoll, 5 Widerspruchs-Checks, Stilmittel-vs-Fehler;
Stufe A deterministisch/kostenlos, Stufe B LLM nur nach Freigabe).
Kapitel 025 ("Der Onkel", Neufassung 19.09., 3103 W) ist regelbasiert
clean (0/0/0) und repetitonsfrei, aber inhaltlich (Temuege-Bogen,
zwei Buecher, Jiguedei-Chronik, 024->025 Kausalkette) noch nicht
quergelesen.

Offen (vom Nutzer zu entscheiden, siehe Doc-Abschnitt "Offene
Vorfragen"): (1) Fenster 024-026 vs. Shigi-Bogen 024-033,
(2) nur Lese-Bericht vs. festes `work/continuity/arcs.md`,
(3) Gueyuek "war der Raum" als Stilmittel vs. physische Anwesenheit.

Was: Chronik-Release braucht (a) Autorenbio fuer Timo Verita
(Variante 3 "zwei Haelften" in `export.yaml` eingebaut) und (b)
staerkeren Reihen-Auftritt "Motivatier Classics" auf den ersten
Seiten (Titelei/Impressum, umgesetzt).

Festgelegte KDP-Rollenlogik 21.09. (Vorgabe auch fuer alle
Uebersetzungs-Buecher, dort Autor = Originalautor):
KDP-Autor = Timo Verita (Chronik) bzw. Originalautor (Uebersetzung);
KDP-Editor = Motivatier Classics (bei Uebersetzungen ZUSAETZLICH
KDP-Uebersetzer = Motivatier Classics; bei der Chronik als
deutschem Original KEIN Uebersetzer-Eintrag!);
Geschaeftsperson/Herausgeber = Motivatier Stiftung
(`publisher`, Rechte, Impressum weiter unten, Classics als
ausfuehrende Reihe darueber). Repo-weit 21.09.: "Motivatier
Hermann Stiftung" -> "Motivatier Stiftung" (71 Stellen).

Umgesetzt 21.09. nachm.: Untertitel "Die Chronik derer, die nicht
schreiben duerfen" (ersetzt "Historischer Roman") in
`export.yaml: book.subtitle` + EPUB-Titelei (verifiziert) +
Regal-Katalog neu; KDP-Serie "Chroniken des Mongolenreichs"
(Band 1 Chronik, Band 2 Geheime Geschichte; Serienbeschreibung in
`docs/kdp-texte-dritte-chronik.md` Abschnitt 5) nur in KDP
anzulegen, nicht im Repo.

```bat
:: Nach Entscheidung + YAML-Pflege: Gate + Export neu
py -3 tools/review_manuscript.py --book die-dritte-chronik --style stil-01-original --all --llm none --fail-on-errors
py -3 tools/export_manuscript.py --book die-dritte-chronik --scope book --style stil-01-original --format epub
```

Status 2026-09-21 nachm. (umgesetzt): Doc + offener Punkt angelegt;
Timo-Verita-Umstellung in `export.yaml` (author/original_author,
translator Motivatier Classics, Bio Variante 3); Classics auf
Titelseite + Impressum, Stiftung als Herausgeber unten; Gate
0/13/36; neuer EPUB `...-20260921-131112.epub` (Untertitel +
Stiftung-Fix, Titelei verifiziert, Regal-Katalog neu); KDP-Texte in
`docs/kdp-texte-dritte-chronik.md` (Abschnitt 5 = Serientexte zum
Anlegen in KDP); Rollenlogik auf alle 12 Pakete uebertragen
(Anna + Mongolen nachgezogen). Offen nur noch:
(1) Kindle-Preview + Leseprobe dieses EPUBs, (2)
Kontinuitaets-Vorfragen (Fenster, Bericht-vs-arcs,
Gueyuek-Deutung), (3) KDP-Serie in KDP anlegen (Band 1) +
KDP-Upload durch Nutzer + Amazon-URL zurueckspielen.

## 11. Taschenbuch: Cover-Wrap, Rueckseite, Reihenkatalog

Status: UMGESETZT und erweitert (2026-09-21, Trim/Profil/Bilder waehlbar).

- Druckcover: manuell `books/<id>/assets/covers/cover-print.{jpg,png,…}`.
  Kein Fallback auf Kindle-`cover.jpg`, kein Platzhalter.
- `--format paperback`: KDP-Innenleben ohne Coverseite
  (`*-paperback-interior.pdf`).
- `--format paperback-complete`: Lese-PDF (`*-paperback-complete.pdf`) =
  optionale Vorderseite + Innenleben + generierte Rueckseite
  (Barcode-Freiflaeche). Wrap-PDF (`*-paperback-wrap.pdf`) nur wenn
  cover-print vorliegt: Umschlag **als eine Flaeche**
  (Rueckseite \| Ruecken \| Vorderseite), nicht der Buchtext.
  Ohne Bild entsteht das Komplett-PDF trotzdem, der Wrap entfaellt.
- Rueckenbreite cremefarben/SW: `Seitenzahl × 0,0635 mm`.
- Trim und Satzprofil getrennt: `--trim-size 5.5x8.5|6x9`,
  `--layout-profile classic|long_classic`. Kein Auto-Trim nach Seitenzahl.
- Kapitelbilder: `--illustration-mode full_page` (eigene Seite, Ist-Verhalten)
  oder `inline` (Bild oben, Text darunter, max. 45 % Satzhoehe).
- KDP-Seitenlimits zentral: cream 776, white 828, groundwood 812.
  Ueberschreitung warnt, aendert den Satz nicht.
- Reihenkatalog am Buchende in EPUB und Paperback
  (`tools/lib/series_catalog.py`, `website.enabled`, `website.catalog: false`
  schliesst PARKIERT/WIP aus).
- Dateiname: `…-55x85-classic-full-TIMESTAMP-paperback-interior.pdf`.
  Report: `*-print-report.json`. Vergleich: `tools/lib/print_compare.py`.
- Pharao A–D (creme, 2026-09-21): 924 / 788 / 673 / 643 Seiten.
  Tabelle: `books/pharao/exports/stil-02-poetisch/book/print/print-comparison-20260921-pharao-abcd.md`.
  A und B liegen ueber 776; C und D sind KDP-creme-tauglich.
- Kopiertext neues Chat-Fenster: `docs/uebergabe-prompt.md`.

## 13. RomanForge-Uebernahme Stufe 1 (2026-10-07)

DE-Originale kommen jetzt ueber den RomanForge-Export nach peter, nicht mehr
ueber `status/<Titel> - NN ....md`. Werkzeug
`tools/import_markdown_original.py`; Ablauf `docs/uebernahme-romanforge.md`;
Plan (Stufen 2-4) `docs/plan-uebernahme-romanforge.md`.

- Committet auf Branch `cline/pveejb87` (`e93f4a2`): Tool + 31 Tests
  (`tests/test_import_markdown_original.py`) + Doku + Chronik-Ausgangsstand
  (`books/die-dritte-chronik/work/imports/romanforge/`).
- Erstlauf Chronik: `--keep 008,031,033,036`; Folge-`--compare` ohne `--baseline`
  ergab nichts 35 / peter-behalten 11 / konflikt 2 (012, 025).
- Offen: Nutzer liest Chronik 012/025 selbst und entscheidet (`--accept`, dann
  `assemble_chapter.py` + `review_manuscript --chapter NNN --llm none`).
- **Ashkara (2026-10-08):** `--new` lief am 2026-10-07 (`20261007-210822`,
  18 Kapitel, Gate 0/0/12). Die Uebergabe vom 2026-10-08 (`Ashkar I c3.md`,
  36 Kapitel) ergab 18x `nichts` + 18x `neu` (019-036). Stufe 1c: `neu`-Kapitel
  per Exportposition freigebbar, Paketgrenze 5 erzwungen.
  Pakete 019-023 (`20261008-154946`), 024-028 (`20261008-155643`),
  029-033 (`20261008-155915`) und 034-036 (`20261008-155935`) uebernommen,
  Assembly 36/36, Gate je Kapitel 0/0. Stand peter: 36/36 Kapitel,
  Buch-Gate 0/0/18, Abschlussvergleich 36x `nichts` (Exit 0).
  Offen: `status/status.json` (18 Eintraege; `status.py mark` kennt nur
  vorhandene Kapitel), Kapitelbilder 026-036, neuer Buch-EPUB.
  Kapitelbilder 001-025 liegen in `assets/chapter/` (019-025 am 2026-10-08 mit
  `generate_illustration.py --no-reference`, 31,5 Credits).
- Offen (Stufe 2): `--handoff <id>` mit `ROMANFORGE_URL`/`ROMANFORGE_API_KEY`
  (in `.env` vorhanden). Uebergabe-Prompt nennt den Schalter, das Werkzeug hat
  ihn noch nicht; Abruf laeuft per Exportdatei.

## Empfohlene Reihenfolge

1. Punkt 0 (Peter-I-Pruefung, vorgezogen) - lesend, ohne Kosten.
2. Punkt 1 (Marketingexport) - pruefen + committen.
3. Punkt 2 + 3 (Top-5 Stilurteil, Cover/Regal-Sync).
4. Punkt 2-Rest (Moloch -> Duell -> Grin -> Pissemski), je mit Freigabe.
5. Punkte 5 / 4 / 6 / 7 nach Kapazitaet.
6. Punkt 11 ist auf `main` (Taschenbuch komplett + Katalog + Trim/Profil/Bilder);
   offen bleibt die menschliche Print-Leseprobe, 788 vs. 776 bei 6x9 classic,
   und ein manuelles `cover-print` je Titel.
7. Punkt 13 (RomanForge Stufe 1, Branch `cline/pveejb87`): Chronik
   012/025-Entscheidung und `--new` (Ashkara) nur nach Freigabe.

