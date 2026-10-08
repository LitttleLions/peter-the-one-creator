# Uebergabe-Prompt (neues Chat-Fenster, gleicher Ordner)

Kopiertext fuer ein neues Chat-Fenster im selben Verzeichnis
`E:\code\peter-the-one-creator` (Branch `cline/pveejb87`). Kein neues Setup.
Unter Windows CLI immer `py -3`, nicht `python`. Kein OpenRouter
ohne ausdrueckliche Freigabe. Nicht committen und keinen Branch-Wechsel,
solange der Nutzer es nicht verlangt.

---

Du arbeitest im bestehenden Repo `E:\code\peter-the-one-creator` (Branch
`cline/pveejb87`). Kein Clone, kein neues Setup. `main` bleibt unberuehrt.

Lies zuerst (lesend, keine Kosten):

1. `AGENTS.md` (Regeln, Pipeline, Release-Gate)
2. `README.md` (Schnellstart)
3. `docs/HANDOVER.md` (Titel = Stand-Datum; oben **Letzte Session**
   = RomanForge-Uebernahme Stufe 1, 2026-10-07, committet `e93f4a2`)
4. `docs/uebernahme-romanforge.md` (Redaktions-/Uebernahme-Ablauf Chronik)
   und `docs/offene-punkte.md` Punkt 6 plus 12 (Chronik)

Danach Lage pruefen:

```text
git --no-pager status --short --branch
py -3 -m unittest tests.test_import_markdown_original -v
```

Erwartet: Branch `cline/pveejb87` (kein Checkout-Wechsel); Stufe-1-Tests
31/31 gruen. Chronik-Gate (unveraendert, Kosten-frei):
`py -3 tools/review_manuscript.py --book die-dritte-chronik --style stil-01-original --all --llm none --fail-on-errors`
-> ERROR=0/WARNING=13/INFO=36. Chronik KDP-fertig, EPUB
`...-20260921-131112.epub` (nicht mit `20260919-222611` verwechseln).

## Was in der letzten Session passiert ist (nicht rueckgaengig machen)

RomanForge-Uebernahme Stufe 1 (commit `e93f4a2` auf `cline/pveejb87`):

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

1. Nutzer liest Chronik 012/025 selbst und entscheidet (`--accept`, dann
   `assemble_chapter.py` + `review_manuscript --chapter NNN --llm none`).
2. Naechster Schritt laut Plan: `--new` fuer Ashkara (neues Buchpaket).
3. Chronik: Kindle-Preview + Leseprobe EPUB 131112; KDP-Upload durch Nutzer.
4. Pharao-Print-Leseprobe; `cover-print` fuer andere Titel.
5. Vor Merge nach `main`: 5 `test_print_export`-Fehler pruefen (CSS?).

Memory Bank gibt es in diesem Repo bewusst nicht. Massgeblich sind
AGENTS.md, README.md, HANDOVER.md und die buchlokalen yaml-Dateien.