# Uebergabe-Prompt (neues Chat-Fenster, gleicher Ordner)

Kopiertext fuer ein neues Chat-Fenster im selben Verzeichnis
`c:\code\peter-the-one` (Branch `main`). Kein neues Setup.
Unter Windows CLI immer `py -3`, nicht `python`. Kein OpenRouter
ohne ausdrueckliche Freigabe. Nicht committen und nicht pushen,
solange der Nutzer es nicht verlangt.

---

Du arbeitest im bestehenden Repo `c:\code\peter-the-one` (Branch
`main`). Kein Clone, kein neues Setup. Die Commits von
`cline/pveejb87` liegen lokal auf `main` und sind noch nicht gepusht.

Lies zuerst (lesend, keine Kosten):

1. `AGENTS.md` (Regeln, Pipeline, Release-Gate)
2. `README.md` (Schnellstart, Print-Formate, Buchbilder)
3. `docs/HANDOVER.md` (Titel = Stand-Datum; oben **Letzte Session**
   = Ashkar I / RomanForge Stufe 1c, 2026-10-08, jetzt auf lokalem `main`)
4. `docs/uebernahme-romanforge.md` und `docs/offene-punkte.md` Punkt 6,
   11, 12, 13 (RomanForge) und 14 (Buchbilder, lokal 2026-09-27)

Danach Lage pruefen:

```text
git --no-pager status --short --branch
py -3 -m unittest tests.test_import_markdown_original -v
py -3 tools/review_manuscript.py --book pharao --style stil-02-poetisch --all --llm none --fail-on-errors
py -3 tools/sync_book_gitignore.py --check
```

Erwartet: Branch `main`, vier Commits vor `origin/main`. Stufe-1-Tests
gruen. Pharao-Gate ERROR=0. `sync_book_gitignore.py --check` ohne Drift.
Chronik-Gate (kostenfrei):
`py -3 tools/review_manuscript.py --book die-dritte-chronik --style stil-01-original --all --llm none --fail-on-errors`
-> ERROR=0/WARNING=13/INFO=36. EPUB `...-20260921-131112.epub`
(nicht mit `20260919-222611` verwechseln).

## Was in der letzten Session passiert ist (nicht rueckgaengig machen)

RomanForge-Uebernahme Stufe 1 bis 1c liegt jetzt auf lokalem `main`
(Fast-Forward von `cline/pveejb87`, Tip `d893767`):

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
Ashkar I: 36/36 Kapitel, Buch-Gate 0/0/18. Offen: Bilder 026-036,
`status.json`, neuer Buch-EPUB.

## Lokal 2026-09-27 (noch nicht committet, nicht rueckgaengig machen)

Buchbilder haben zwei Ebenen. Pro Bild entstehen aus einem Download:

```text
assets/master/chapter/chapter-001.jpg   2k, q92  – nur Paperback
assets/chapter/chapter-NNN.jpg          1024, q60 – EPUB/DOCX/A5
```

Ohne `assets/master/` faellt der Paperback-Export auf die E-Reader-Bilder
zurueck. Leerseiten-Bug behoben (`min-height` nur noch Satzspiegel).
`der-lotse` ist vollstaendig (32 Kapitel). Pharao-Innenleben ohne Leerseiten:
923 / 787 / 672 / 642. Details in `docs/HANDOVER.md`.

Default bleibt 5.5×8.5 / `classic` / `full_page`. Cream-Limit 776
(White 828, Groundwood 812). Ueberschreitung warnt, aendert den Satz nicht.

| Datei | Rolle |
|---|---|
| `*-paperback-interior.pdf` | KDP-Innenleben, kein Cover |
| `*-paperback-complete.pdf` | Lese-PDF: Vorderseite + Buch + Rueckseite |
| `*-paperback-wrap.pdf` | Umschlag als eine Flaeche (Rueckseite \| Ruecken \| Vorderseite) |

## Harte Regeln

- `books/*/source/` und `logic/` nicht ohne Rueckfrage aendern.
- Keine Secrets, kein Force-Push, kein Hard-Reset, kein Branch-Wechsel.
- Uebersetzungslaeufe und Higgsfield nur nach Freigabe.
- Release-Gate: ERROR>0 stoppt den Export; Bypass nur
  `--allow-review-errors`.

## Offenes

1. Nutzer liest Chronik 012/025 selbst und entscheidet (`--accept`, dann
   `assemble_chapter.py` + `review_manuscript --chapter NNN --llm none`).
2. Ashkar I: Bilder 026-036, `status.json` auf 36 Kapitel, neuer Buch-EPUB.
3. Chronik: Kindle-Preview + Leseprobe EPUB 131112; KDP-Upload durch Nutzer.
4. Pharao-Print-Leseprobe; `cover-print` fuer andere Titel.
5. Lokaler Stand 2026-09-27 (Bilder, Leerseiten, der Lotse) ist nicht
   committet. `test_print_export` pruefen, bevor der Stand committet wird.

Memory Bank gibt es in diesem Repo bewusst nicht. Massgeblich sind
AGENTS.md, README.md, HANDOVER.md und die buchlokalen yaml-Dateien.