# Uebergabe-Prompt (neues Chat-Fenster, gleicher Ordner)

Kopiertext fuer ein neues Chat-Fenster im selben Verzeichnis
`E:\code\peter-the-one-creator` (Branch `main`). Kein neues Setup.
Unter Windows CLI immer `.\.venv\Scripts\python.exe`, nicht `python`/`py -3`.
Kein OpenRouter ohne ausdrueckliche Freigabe. Nicht committen und keinen
Branch-Wechsel, solange der Nutzer es nicht verlangt.

---

Du arbeitest im bestehenden Repo `E:\code\peter-the-one-creator` (Branch
`main`). Kein Clone, kein neues Setup. `main` ist gepusht; der Branch
`cline/pveejb87` ist geloescht.

Lies zuerst (lesend, keine Kosten):

1. `AGENTS.md` (Regeln, Pipeline, Release-Gate)
2. `README.md` (Schnellstart)
3. `docs/HANDOVER.md` (Titel = Stand-Datum; oben **Letzte Session** =
   Autor-Fix + Merge von origin/main + Push, 2026-10-28)
4. `docs/uebernahme-romanforge.md` (Redaktions-/Uebernahme-Ablauf Chronik)
   und `docs/offene-punkte.md` Punkt 6 plus 12 (Chronik) plus 14 plus 15

Danach Lage pruefen (ein Befehl pro Aufruf, kein `head`/`grep`):

```text
git --no-pager status --short --branch
.\.venv\Scripts\python.exe -m unittest tests.test_book_project
.\.venv\Scripts\python.exe -m unittest tests.test_import_markdown_original
.\.venv\Scripts\python.exe tools/status.py --book die-sprache-des-anderen summary
```

Erwartet: Branch `main`, mit `origin/main` synchron;
`test_book_project` gruen (inkl. `SuggestBookIdTests`);
`test_import_markdown_original` 41/41 gruen;
`die-sprache-des-anderen` 34/34 done; Gate dort ERROR=0/WARNING=0/INFO=0;
EPUB `book-die-sprache-des-anderen-stil-01-original-20261028-201552.epub`
(mit Cover + Kapitelbildern 001-003).
Chronik-Gate (unveraendert, Kosten-frei):
`.\.venv\Scripts\python.exe tools/review_manuscript.py --book die-dritte-chronik --style stil-01-original --all --llm none --fail-on-errors`
-> ERROR=0/WARNING=13/INFO=36. Chronik KDP-fertig, EPUB
`...-20260921-131112.epub` (nicht mit `20260919-222611` verwechseln).

## Was in der letzten Session passiert ist (nicht rueckgaengig machen)

Bilder + Aufräumen + Merge nach `main` (2026-10-28, Merge `ce7c1d2`):

- **Bilder** fuer `die-sprache-des-anderen`: `book.yaml` um
  `illustration_setting` + `higgsfield:`-Block erweitert (`gpt_image_2_5`,
  3:4, 1k, medium), `names.yaml` mit 14 Eintraegen (6 Personen mit
  `visual`, 8 Orte). Kapitelbilder 001-003 via
  `generate_illustration.py --kind chapter --no-reference`; Cover ueber die
  Higgsfield-CLI (`--aspect_ratio 2:3 --resolution 2k`) plus
  `optimize_asset_images.py --scope cover`. Gate danach 0/0/0, neuer EPUB
  `...-20261028-195240.epub` (4.806.312 Bytes) ohne Bypass.
- **Wichtig:** `generate_illustration.py` kann kein Cover; Cover laufen ueber
  die CLI + `optimize_asset_images.py`.
- **Geloescht** (per Freigabe): `SUMMARY.md`, `SUMMARY_FINAL.md`,
  `tools/create_placeholders.py`, `books/existing/` (Wegwerf-Testpaket, stand
  im Reihenkatalog des EPUB), `.scratch-lotse/`, `test.jpg`,
  `hub_logos_request*.json|md`.
- **Behalten**: `books/perfect.sight/` + die 4 `tools/*perfect_sight*.py`;
  `books/der-lotse-von-ruegen/` mit Cover + Bildern 001-010 (33/33 done,
  Gate 0/0/20, `website.enabled: true`, sort_order 90).
- **Merge**: 4 Commits auf `cline/pveejb87`, dann `git merge
  cline/pveejb87 --no-ff` auf `main` (`ce7c1d2`, keine Konflikte). Kein Push.
- Lokal untracked bleibt `books/die-dritte-chronik/source/Die dritte
  Chronik(1).md` (Browser-Download-Kopie, `source/` ist tabu).
- Offen: Push nach `origin/main`; `assemble_chapter.py:65` hardcodiert
  `Alexei Tolstoi` im Kapitelkopf; `export.yaml` der Sprache des Anderen
  schreibt „Timo Veritas" statt „Timo Verita"; weitere Kapitelbilder
  004-034 bzw. 011-033; Regal-Deploy fuer den Lotse.

Aelter (unveraendert): Einstieg gehaertet (2026-10-28, `cline/pveejb87`):

- Falsche Vor-Session-ID `sprache-des-anderen` als Stub entlarvt (kein
  `id`/`title`, leere Szenen); richtig ist `die-sprache-des-anderen`
  (34 Kapitel, `rf_id` 232–265, Status 34/34). Stub per Freigabe geloescht.
- Einstieg gehaertet: `AGENTS.md` Regeln 2/3/4/5 (unbekannte ID und
  Doppelordner stoppen + Rueckfrage; kein Root-Scratch/Eigenbau; ein CLI
  pro Aufruf, `Select-Object -First N`).
- `tools/lib/book_project.py`: `_suggest_book_id()`; unbekannte IDs melden
  jetzt `meintest du ...?` (`find_book`, `book_project`).
- `tools/import_markdown_original.py --new`: Hinweis, wenn `--id` von
  `slugify(title)` abweicht.
- `tests/test_book_project.py`: neue `SuggestBookIdTests`.

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