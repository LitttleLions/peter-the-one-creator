# Uebergabe-Prompt (neues Chat-Fenster, gleicher Ordner)

Kopiertext fuer ein neues Chat-Fenster im selben Verzeichnis
`c:\code\peter-the-one` (Branch `main`). Kein neues Setup.
Unter Windows CLI immer `py -3`, nicht `python`. Kein OpenRouter
ohne ausdrueckliche Freigabe. Nicht committen, solange der Nutzer
es nicht verlangt.

---

Du arbeitest im bestehenden Repo `c:\code\peter-the-one` (Branch
`main` = `origin/main`). Kein Clone, kein neues Setup.

Lies zuerst (lesend, keine Kosten):

1. `AGENTS.md` (Regeln, Pipeline, Release-Gate)
2. `README.md` (Schnellstart, Print-Formate)
3. `docs/HANDOVER.md` (Titel = Stand-Datum; oben **Letzte Session**
   = Pharao Print-Optionen 2026-09-21, auf `main` committet)
4. `docs/offene-punkte.md` Punkt 11 (Print, umgesetzt) und Punkt 6
   plus 12 (Chronik)

Danach Lage pruefen:

```text
git --no-pager status --short --branch
py -3 tools/review_manuscript.py --book pharao --style stil-02-poetisch --all --llm none --fail-on-errors
```

Pharao-Gate erwartet ERROR=0. Trim/Profil/Bilder sind waehlbar
(`config/print.yaml`, CLI `--trim-size` / `--layout-profile` /
`--illustration-mode`). Vergleichstabelle:
`books/pharao/exports/stil-02-poetisch/book/print/print-comparison-20260921-pharao-abcd.md`.

Print-PDFs liegen lokal unter
`books/pharao/exports/stil-02-poetisch/book/print/` (Interior-Stempel
A `…-55x85-classic-full-20260921-162938`, B `…-6x9-classic-full-20260921-163022`,
C `…-6x9-long_classic-full-20260921-163059`,
D `…-6x9-long_classic-inline-20260921-163133`). Die grossen PDFs
sind regenerierbar und nicht zwingend im Git.

Chronik ist KDP-fertig (Text + Bilder), Gate 0/13/36, EPUB
`...-20260921-131112.epub`. Nicht mit dem aelteren Stempel
`20260919-222611` verwechseln.

## Was in der letzten Session passiert ist (nicht rueckgaengig machen)

Taschenbuch-Export mit waehlbarem Trim, Satzprofil und Bildmodus
ist auf `main` (Code + Tests + Doku + Pharao-000 + `cover-print.png`):

- `config/print.yaml`
- `tools/lib/print_spec.py`, `print_css.py`, `print_pdf.py`,
  `print_wrap.py`, `print_compare.py`
- `tools/lib/series_catalog.py`
- `tools/export_manuscript.py`: Formate `paperback` und
  `paperback-complete`; Overlay-Flags `--trim-size`,
  `--layout-profile`, `--illustration-mode`
- Dashboard (React + Streamlit): Dropdowns nur bei Taschenbuch
- Tests: `tests/test_print_export.py`, `tests/test_series_catalog.py`
- Schrift: `assets/print-fonts/eb-garamond/` (OFL)
- Pharao Kapitel 000: Juni-Wstep (Herodot) aus Git restauriert
- `books/pharao/assets/covers/cover-print.png` (manuell, kein Fallback
  auf Kindle-`cover.jpg`)
- `website.catalog: false` bei Anna, Grin, Pissemski
- Stale-Job-Recovery in `tools/lib/dashboard_jobs.py` (Windows
  `tasklist` / cp1252, plus Manifest+Report). Dashboard zuletzt
  mit Frontend-Build: http://127.0.0.1:8000

Default bleibt 5.5×8.5 / `classic` / `full_page` (kein stiller
Satzwechsel). Cream-Limit 776 (White 828, Groundwood 812).
Ueberschreitung warnt, aendert den Satz nicht.

Pharao-Innenleben A–D (creme):

| Test | Trim | Profil | Bilder | Seiten | vs. 776 |
|---|---|---|---|---:|---|
| A | 5.5x8.5 | classic | full_page | 924 | +148, nicht KDP-creme |
| B | 6x9 | classic | full_page | 788 | +12, noch knapp drueber |
| C | 6x9 | long_classic | full_page | 673 | ok |
| D | 6x9 | long_classic | inline | 643 | ok |

A→B: −136 Seiten (−14,7 %). Drei Print-PDFs (nicht verwechseln):

| Datei | Rolle |
|---|---|
| `*-paperback-interior.pdf` | KDP-Innenleben, kein Cover |
| `*-paperback-complete.pdf` | Lese-PDF: Vorderseite + Buch + Rueckseite |
| `*-paperback-wrap.pdf` | Umschlag **als eine Flaeche** (Rueckseite \| Ruecken \| Vorderseite) fuer den KDP-Cover-Upload |

Wrap ist nicht der Buchtext. Ruecken cremefarben/SW = Seitenzahl ×
0,0635 mm.

## Harte Regeln

- Originalquellen unter `books/<id>/source/` und `logic/` nicht ohne
  Rueckfrage aendern.
- Keine Secrets, kein Force-Push, kein Hard-Reset.
- Uebersetzungslaeufe und Higgsfield nur nach Freigabe.
- Release-Gate: ERROR>0 stoppt den Export; Bypass nur
  `--allow-review-errors`.
- Grosse Print-PDFs und `exports/.../work/`-HTML nicht ungefragt
  ins Git nehmen; Code/Config/Tests/Doku reichen zum Regenerieren.

## Offenes Produkt (kein Code noetig, bis der Nutzer fragt)

1. Menschliche Print-Leseprobe Pharao (Kindle/Druck, Wrap visuell).
2. 924 bzw. 788 Seiten vs. KDP-Creme 776 (Variante C/D sind drin;
   B nur +12). Keine Auto-Typo-Optimierung.
3. `cover-print` fuer andere Titel.
4. Chronik: Kindle-Preview + Leseprobe EPUB 131112; KDP-Upload durch
   Nutzer; Amazon-URL zurueckspielen.

Memory Bank gibt es in diesem Repo bewusst nicht. Massgeblich sind
AGENTS.md, README.md, HANDOVER.md und die buchlokalen yaml-Dateien.
