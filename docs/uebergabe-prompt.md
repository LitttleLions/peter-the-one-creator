# Uebergabe-Prompt (neues Chat-Fenster, gleicher Ordner)

Kopiertext fuer ein neues Chat-Fenster im selben Verzeichnis
`E:\code\peter-the-one-creator` (Branch `cline/pveejb87`). Kein neues Setup.
Unter Windows CLI immer `.\.venv\Scripts\python.exe`, nicht `python`/`py -3`.
Kein OpenRouter ohne ausdrueckliche Freigabe. Nicht committen und keinen
Branch-Wechsel, solange der Nutzer es nicht verlangt.

---

Du arbeitest im bestehenden Repo `E:\code\peter-the-one-creator` (Branch
`cline/pveejb87`). Kein Clone, kein neues Setup. `main` bleibt unberuehrt.

Lies zuerst (lesend, keine Kosten):

1. `AGENTS.md` (Regeln, Pipeline, Release-Gate)
2. `README.md` (Schnellstart)
3. `docs/HANDOVER.md` (Titel = Stand-Datum; oben **Letzte Session**
   = Die Sprache des Anderen + Einstieg gehaertet, 2026-10-28, uncommittet)
4. `docs/uebernahme-romanforge.md` (Redaktions-/Uebernahme-Ablauf Chronik)
   und `docs/offene-punkte.md` Punkt 6 plus 12 (Chronik)

Danach Lage pruefen (ein Befehl pro Aufruf, kein `head`/`grep`):

```text
git --no-pager status --short --branch
.\.venv\Scripts\python.exe -m unittest tests.test_book_project
.\.venv\Scripts\python.exe -m unittest tests.test_import_markdown_original
.\.venv\Scripts\python.exe tools/status.py --book die-sprache-des-anderen summary
```

Erwartet: Branch `cline/pveejb87` (kein Checkout-Wechsel, uncommittet);
`test_book_project` gruen (inkl. `SuggestBookIdTests`);
`test_import_markdown_original` 41/41 gruen;
`die-sprache-des-anderen` 34/34 done; Gate dort ERROR=0/WARNING=0/INFO=0;
EPUB `book-die-sprache-des-anderen-stil-01-original-20261028-183226.epub`.
Chronik-Gate (unveraendert, Kosten-frei):
`.\.venv\Scripts\python.exe tools/review_manuscript.py --book die-dritte-chronik --style stil-01-original --all --llm none --fail-on-errors`
-> ERROR=0/WARNING=13/INFO=36. Chronik KDP-fertig, EPUB
`...-20260921-131112.epub` (nicht mit `20260919-222611` verwechseln).

## Was in der letzten Session passiert ist (nicht rueckgaengig machen)

Die Sprache des Anderen (2026-10-28, auf `cline/pveejb87`, uncommittet):

- Falsche Vor-Session-ID `sprache-des-anderen` als Stub entlarvt (kein
  `id`/`title`, leere Szenen); richtig ist `die-sprache-des-anderen`
  (34 Kapitel, `rf_id` 232–265, Status 34/34). Stub per Freigabe geloescht.
- Am vollstaendigen Paket verifiziert: Assembly 34/34 (110.375 Woerter),
  Review ERROR=0/WARNING=0/INFO=0, EPUB
  `book-die-sprache-des-anderen-stil-01-original-20261028-183226.epub`
  (3.917.106 Bytes, `review_gate_errors:0`, `review_gate_bypassed:false`).
- Einstieg gehaertet: `AGENTS.md` Regeln 2/3/4/5 (unbekannte ID und
  Doppelordner stoppen + Rueckfrage; kein Root-Scratch/Eigenbau; ein CLI
  pro Aufruf, `Select-Object -First N`).
- `tools/lib/book_project.py`: `_suggest_book_id()`; unbekannte IDs melden
  jetzt `meintest du ...?` (`find_book`, `book_project`).
- `tools/import_markdown_original.py --new`: Hinweis, wenn `--id` von
  `slugify(title)` abweicht.
- `tests/test_book_project.py`: neue `SuggestBookIdTests`.

Aelter (unveraendert): RomanForge-Uebernahme Stufe 1 (commit `e93f4a2` auf
`cline/pveejb87`):

- `tools/import_markdown_original.py` - compare/accept/keep/new fuer
  DE-Originale. `--compare`/`--dry-run` schreiben nichts (Exit 2 bei
  `konflikt`/`neu`/`entfallen`/`ohne-ausgangsstand`).
- `tests/test_import_markdown_original.py` - 31 Tests.
- `docs/uebernahme-romanforge.md` + `docs/plan-uebernahme-romanforge.md`
  (Stufe 1 umgesetzt/abgenommen; Stufe 2-4 offen).
- Chronik-Ausgangsstand versioniert:
  `books/die-dritte-chronik/work/imports/romanforge/` (state.yaml + runs/).
- `AGENTS.md`/`README.md`: Alter Redaktionsweg `status/<Titel> - NN ....md`
  ersetzt durch den RomanForge-Export.

Erstlauf Chronik: `--keep 008,031,033,036`; Folge-`--compare` ohne
`--baseline` -> nichts 35 / peter-behalten 11 / konflikt 2 (012, 025).
Print-Details (Trim/Profil/Bilder, Pharao-Innenleben A-D, Wrap-PDFs):
`docs/HANDOVER.md`, Abschnitt "Vorige Session".

## Harte Regeln

- `books/*/source/` und `logic/` nicht ohne Rueckfrage aendern.
- Keine Secrets, kein Force-Push, kein Hard-Reset, kein Branch-Wechsel.
- Uebersetzungslaeufe und Higgsfield nur nach Freigabe.
- Release-Gate: ERROR>0 stoppt den Export; Bypass nur
  `--allow-review-errors`.

## Offenes

0. Verifikation in stabiler Shell nachholen (ein Befehl pro Aufruf):
   `test_book_project`, `test_import_markdown_original`, `status.py
   --book die-sprache-des-anderen summary`. Danach Root-Scratch loeschen
   (`SUMMARY.md`, `SUMMARY_FINAL.md`, `tools/create_placeholders.py` —
   ungetrackt, Regelverstoß seit Vor-Session; kein Commit ohne Freigabe).
   Erst danach Bilder (`assets/covers`, Kapitelbilder) und
   Verlags-/Titelei-Texte in `books/die-sprache-des-anderen/export.yaml`
   entscheiden.
1. Nutzer liest Chronik 012/025 selbst und entscheidet (`--accept`, dann
   `assemble_chapter.py` + `review_manuscript --chapter NNN --llm none`).
2. Naechster Schritt laut Plan: `--new` fuer Ashkara (neues Buchpaket).
3. Chronik: Kindle-Preview + Leseprobe EPUB 131112; KDP-Upload durch Nutzer.
4. Pharao-Print-Leseprobe; `cover-print` fuer andere Titel.
5. Vor Merge nach `main`: 5 `test_print_export`-Fehler pruefen (CSS?).

Memory Bank gibt es in diesem Repo bewusst nicht. Massgeblich sind
AGENTS.md, README.md, HANDOVER.md und die buchlokalen yaml-Dateien.