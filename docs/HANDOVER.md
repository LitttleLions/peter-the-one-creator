# Handover – Stand 2026-10-28 (Bilder für „Die Sprache des Anderen", Root-Scratch gelöscht, vollständig auf `main` gemergt)

> Für neue Chats: zuerst [AGENTS.md](../AGENTS.md), dann diese Datei.
> Kopierfertiger Einstieg: [uebergabe-prompt.md](./uebergabe-prompt.md).

## Letzte Session (2026-10-28, Bilder + Aufräumen + Merge nach `main`)

Branch **`main`** (Merge `ce7c1d2`), **kein Push**. Ausgangspunkt war
`cline/pveejb87` (4 Commits darauf, 8 weitere schon vorhanden, `main` 1 Commit
vorn). Alles ist jetzt auf `main`; `cline/pveejb87` ist vollständig
eingesmolzen und kann gelöscht werden.

### 1. Bilder für `die-sprache-des-anderen` (Credits freigegeben)

- `book.yaml`: `illustration_setting` (9. Jh., Straßburg/Ill/Rhein, Winter,
  Heerlager, Franken-Tracht) + `higgsfield:`-Block (`gpt_image_2_5`, 3:4, 1k,
  medium, `image_processing` JPEG q60/1024, Cover q75/1600×2400).
- `names.yaml`: 14 Einträge (6 Personen mit `visual`-Kurzbeschreibung für den
  Figurenblock, 8 Orte). Vorher leer.
- **Kapitelbilder 001–003** via `generate_illustration.py --kind chapter
  --no-reference` (kein Moodboard für dieses Buch, also reiner Prompt).
  Ergebnis: `assets/chapter/chapter-001..003.jpg` (772×1024), stilkonsistent
  und periodisch plausibel (Alda im Vordergrund, Raginbert zu Pferd, Kähne,
  Ketten, Lager).
- **Cover** über die Higgsfield-CLI direkt (`higgsfield generate create
  gpt_image_2_5 --aspect_ratio 2:3 --resolution 2k --quality medium --wait`),
  Job `f2f6da57-…`, 1360×2048 PNG → `assets/covers/cover.png`, dann
  `optimize_asset_images.py --scope cover` → `cover.jpg` (482 KB) +
  `cover_alt.jpg` (Archiv).
- **Wichtig:** `tools/generate_illustration.py` kann **kein Cover** (nur
  `--kind chapter|scene`). Cover laufen über die CLI + `optimize_asset_images.py`.
- Gate danach erneut: **ERROR=0 / WARNING=0 / INFO=0**, Exit 0.
- Neuer Buch-EPUB `book-die-sprache-des-anderen-stil-01-original-20261028-195240.epub`
  (4.806.312 Bytes), Manifest `partial:false`, `review_gate_errors:0`,
  `review_gate_bypassed:false`, 3 Illustrationen, Cover als `cover-image`
  registriert (`<meta name="cover" content="file11_jpg"/>`).

### 2. Aufräumen

- **Gelöscht** (per Freigabe): `SUMMARY.md`, `SUMMARY_FINAL.md`,
  `tools/create_placeholders.py`, `books/existing/` (Wegwerf-Testpaket:
  id `existing`, Autor „Testautor", Inhalt = Chronik-Kopie; stand mit
  `website.enabled: true` im **Reihenkatalog des EPUB**), `.scratch-lotse/`
  (Scratch im Repo-Root), `test.jpg`, `hub_logos_request.json`,
  `hub_logos_request_decoded.md`.
- **Behalten**: `books/perfect.sight/` (echtes Sachbuch-Paket, 594 Dateien) +
  `tools/{analyze,generate,import,process}_perfect_sight*.py`; die 4
  `books/der-lotse-von-ruegen/assets/chapter/chapter-00{5..9}`-PNG+`_alt`-Paare.
- `books/die-dritte-chronik/source/Die dritte Chronik(1).md` bleibt **lokal
  untracked** (Browser-Download-Kopie der versionierten Quelle, `source/` ist
  tabu).

### 3. Merge

- 4 Commits auf `cline/pveejb87`: `4d382d1` Einstieg-Härtung + Doku,
  `08087d0` beide Buchpakete, `8776da2` Perfect Sight, `9a3f625` Review-/
  Exportartefakte. Merge auf `main`: `ce7c1d2` (ort, keine Konflikte).
- Tests nach dem Merge: `test_book_project` 2/2 OK,
  `test_import_markdown_original` 41/41 OK.
- `status.py`: `die-sprache-des-anderen` 34/34 done,
  `der-lotse-von-ruegen` 33/33 done, Gate dort ERROR=0/WARNING=0/INFO=20.
- **Kein Push** – `main` ist 13 Commits vor `origin/main`.

### 4. Offen (nächster Chat)

- **Push nach `origin/main`** (13 Commits) – noch nicht erfolgt.
- `cline/pveejb87` kann gelöscht werden (alles auf `main`).
- Titelei-Texte `export.yaml` von `die-sprache-des-anderen` sind weiterhin
  neutral (leere `rights`/`description`/`summary`/`author_bio`). Autor bleibt
  laut Nutzerentscheidung **Timo Verita**; `export.yaml` schreibt aber
  „Timo Veritas" (mit s) – Schreibweise angleichen.
- `tools/assemble_chapter.py:65` hardcodiert im Kapitelkopf
  `*Buch: {title} - Alexei Tolstoi*`. Das ist bei **allen** Büchern falsch
  (auch beim Lotse-Buch). Wird beim Export weggefiltert, steckt aber in
  `work/assembled/`. Korrektur auf den Buch-Autor aus `book.yaml` ist offen.
- Weitere Kapitelbilder für `die-sprache-des-anderen` (004–034) und
  `der-lotse-von-ruegen` (011–033) sind nicht erzeugt; Cover-Typografie
  (Titel/Autor im Bild) fehlt – beim Lotse-Buch ist sie vorhanden.
- Regal: `der-lotse-von-ruegen` hat `website.enabled: true` (sort_order 90),
  ist aber im Live-Katalog noch nicht sichtbar.
- Shell-Integration flackert in dieser Umgebung („Command completion could
  not be observed"). Workaround: Ausgabe per `Out-File` in eine Datei und
  diese lesen.

## Vorige Session (2026-10-28, Doppelablage geklärt + Einstieg gehärtet)

Branch **`cline/pveejb87`**, **nicht committet, kein Push**.
Vor-Session behauptete Buch-ID `sprache-des-anderen` (Stub, 12-Zeilen-`book.yaml`
ohne `id`/`title`, leere Szenen). Richtig ist **`die-sprache-des-anderen`**
(`slugify("Die Sprache des Anderen")`, 34 Kapitel, `rf_id` 232–265,
`state.yaml` + `status.json` 34/34 `done`).
Falscher Stub `books/sprache-des-anderen/` per Freigabe gelöscht
(`Remove-Item -Recurse -Force`); in `git status` nicht mehr enthalten.
Danach am vollständigen Paket verifiziert (lesend + Standard-CLIs,
kein OpenRouter, keine Bilder):

- `assemble_chapter.py --book die-sprache-des-anderen --all --style stil-01-original`:
  **34/34 Kapitel, 110.375 Wörter** (eine Zeile `stil-01-original` ohne Szenen
  erwartbar übersprungen → `34/35` in der Zählung).
- `review_manuscript.py --all --llm none --fail-on-errors`:
  **ERROR=0 / WARNING=0 / INFO=0, Exit 0**.
- `export_manuscript.py --scope book --style stil-01-original --format epub`:
  `exports/stil-01-original/book/epub/book-die-sprache-des-anderen-stil-01-original-20261028-183226.epub`
  (**3.917.106 Bytes**), Manifest `partial:false`, `review_gate_errors:0`,
  `review_gate_bypassed:false`, 34× `missing:[]`.
- `status.py summary`: **34/34 (100 %) done**.
- `tests.test_import_markdown_original`: **41/41 OK** (Stand vorige Verifikation).
- Mit dem Stub sind dessen 4 Placeholder-Bilder (`cover.jpg`,
  `chapter-001..003.jpg`) entfallen; `die-sprache-des-anderen/assets/` enthält
  nur leeres `covers/`. `export.yaml` dort ist neutral (Platzhalter-Cover, leere
  `rights`/`description`/`summary`/`author_bio`, kein `website:`/`marketing:`).

Danach gehärtet (gegen Wiederholung, Plan→Act in derselben Session):

- `AGENTS.md` Einstieg Regeln 2/3/4/5: unbekannte ID → stoppen + Rückfrage
  (keine Alternativ-ID, kein Zweitordner); keine `SUMMARY*.md` im Root, keine
  `tools/create_*.py` ohne Freigabe, keine Placeholder-Bilder als Pipeline;
  Doppelordner → stoppen + Rückfrage, kein Assembly/Export vorher; PowerShell
  nur `Select-Object -First N`, ein CLI pro Aufruf bei labiler Shell.
- `tools/lib/book_project.py`: `_suggest_book_id()` (difflib, max. 3, cutoff
  0.55, read-only); `find_book()` + `book_project()` melden jetzt z. B.
  `Buch mit id=sprache-des-anderen nicht gefunden, meintest du 'die-sprache-des-anderen'?`.
- `tools/import_markdown_original.py --new`: Hinweis nach stderr, wenn `--id`
  von `slugify(title)` abweicht (kein Abbruch, kein Verhalten-Change).
- `tests/test_book_project.py`: neue `SuggestBookIdTests` (Temp-Paket
  `die-sprache-des-anderen`, falsche ID muss `meintest du`-Vorschlag werfen).

Offen (nächster Chat, alles lesend zuerst): `unittest`-Läufe
(`test_book_project`, `test_import_markdown_original`) + `status.py summary`
in stabiler Shell nachholen (diese Session hing die Shell-Integration:
`Command completion could not be observed`); danach entscheiden, ob
Placeholder-Bilder neu oder Higgsfield (`text2image_soul_v2`-Vorgabe lag nur
im gelöschten Stub) sowie Verlags-/Titelei-Texte in `export.yaml`.
`SUMMARY.md`/`SUMMARY_FINAL.md` im Root und `tools/create_placeholders.py`
sind noch ungetrackt vorhanden und sollen gelöscht werden (Regelverstoß,
kein Commit ohne Freigabe).

## Vorige Session (2026-10-08, Ashkar I: AKTUALISIEREN + Stufe 1c)

Branch **`cline/pveejb87`** (nicht `main`).

## Letzte Session (2026-10-08, Ashkar I: AKTUALISIEREN + Stufe 1c)

Branch **`cline/pveejb87`**. Übergabe aus RomanForge im Modus AKTUALISIEREN
(`Ashkar I c3.md`, byte-identisch mit `Ashkar I(2).md`: 36 Kapitel,
112.304 Wörter). `--compare` gegen
`books/ashkara/work/imports/romanforge/state.yaml`: 18× `nichts` (001–018),
18× `neu` (Exportposition 019–036), 0 Konflikte, 0 `entfallen`. Der Modus
passte (Buch existiert), aber Stufe 1 konnte `neu` nur melden – deshalb
angehalten und gefragt; auf Freigabe erweitert.

- Werkzeug (Stufe 1c, `tools/import_markdown_original.py`): `neu`-Kapitel sind
  über ihre **Exportposition** freigebbar (`--accept 019`), `--keep` bleibt für
  sie verboten (Exit 2), Paketgrenze **5** Kapitel pro Lauf im Werkzeug
  erzwungen (Exit 2, kein Schreibzugriff). Dazu Pfadfix: `--book` liefert
  `work_dir`/`source_path` repo-relativ (`book_project.as_tool_config`),
  `_output_root_for` verdoppelte den Buchordner (`books/<id>/books/<id>/work`).
- Tests `tests/test_import_markdown_original.py`: **41/41 grün** (34 alt,
  5 für `neu`/Paketgrenze, 2 Regression Pfadauflösung).
- Paket 019–023 übernommen (Lauf `20261008-154946`; der erste Versuch
  `20261008-154530` schrieb wegen der Pfadverdopplung daneben und liegt unter
  `books/ashkara/work/legacy/import-pfadfehler-20261008/`): drei Textkopien je
  Kapitel, Assembly 5/5, Gate je Kapitel **ERROR=0/WARNING=0** (INFO 1/0/1/1/0).
- Paket 024–028 übernommen (Lauf `20261008-155643`): Assembly 5/5, Gate je
  Kapitel **ERROR=0/WARNING=0** (INFO 0/0/1/0/0).
- Pakete 029–033 (`20261008-155915`) und 034–036 (`20261008-155935`) übernommen:
  Assembly je 5/5 bzw. 3/3, Gate je Kapitel **ERROR=0/WARNING=0** (INFO 0/0
  außer 026/034/036 mit je 1). **Stand: 36/36 Kapitel in peter**, `state.yaml`
  36 Einträge, Buch-Gate `--all --llm none` **ERROR=0 / WARNING=0 / INFO=18**,
  Abschlussvergleich **36× `nichts`** (Exit 0).
- Kapitelbilder **019–025** erzeugt (2026-10-08): `generate_illustration.py --book
  ashkara --chapter NNN --kind chapter **--no-reference**` mit den Buch-Defaults
  (`gpt_image_2`, 3:4, `1k`, Render `high`). Ergebnis 772×1024 RGB, 69–103 KB,
  Verbrauch **31,5 Credits** (1148,94 → 1117,44). Prompts/Metadaten je Kapitel
  unter `books/ashkara/work/prompts/higgsfield/NNN-chapter-stil-01-original.*`.
  Zwei Betriebshinweise: ohne `--no-reference` bricht das Werkzeug ab, weil
  `DEFAULT_MOODBOARD` in `generate_illustration.py` ein reiner Share-Link ist;
  Higgsfield antwortete zweimal mit HTTP 503 (Service vorübergehend weg),
  einmaliges Wiederholen half.
- Offen: Bilder 026–036, `status/status.json` (weiterhin 18 Einträge; `status.py
  mark` ändert nur vorhandene Kapitel), neuer Buch-EPUB (bisheriger
  `...-20261008-002805.epub` deckt nur 001–018; die Bilder 019–025 sind dafür
  aber schon einsatzbereit), Stufe 2 (`--handoff <id>`; der Übergabe-Prompt
  implementiert in `tools/import_markdown_original.py` + `tools/lib/romanforge_client.py`, Endpunkt `/api/handoffs/{id}` verifiziert).

## Vorige Session (2026-10-07, RomanForge-Übernahme Stufe 1)

Branch **`cline/pveejb87`** (nicht `main`). Neues, allgemeines
Übernahme-Werkzeug für DE-Originale aus RomanForge ist fertig, getestet und
committet (`e93f4a2`). Vorgänger `import_die_dritte_chronik.py` bleibt liegen
(Entfernen nur nach Rückfrage).

- `tools/import_markdown_original.py` – vergleicht einen RomanForge-Markdown-
  Export per Tabelle (Nummer, Titel, Wörter RF/peter, Einstufung, Hinweis).
  `--compare`/`--dry-run` schreiben nichts (Exit 2 bei `konflikt`/`neu`/
  `entfallen`/`ohne-ausgangsstand`); `--accept`/`--keep` schreiben nur die
  freigegebenen Kapitel (max. 5 pro Paket). `--new` legt ein unbekanntes
  Buchpaket an (braucht `--id/--title/--author`).
- Erstlauf (Option B): der erste schreibende Lauf legt `state.yaml` für
  **alle** Kapitel an (unberührt: `rf_base = peter_base = Hash aus
  --baseline`). Danach ist `--baseline` nicht mehr nötig; wird sie trotzdem
  übergeben, kommt nur ein Hinweis. Fehlt ein Kapitel in `state.yaml`, ist es
  `ohne-ausgangsstand` (Exit 2), **nie** `konflikt` (keine leere Baseline).
- „vermutlich umbenannt": `neu`+`entfallen` an gleicher Exportposition →
  Hinweis in der Berichtsspalte, kein Auto-Merge.
- Tests `tests/test_import_markdown_original.py`: **31/31 grün** (echte
  Chronik-Daten; der Frisch-Export ist der echt archivierte Export). Doku
  `docs/uebernahme-romanforge.md`; Plan `docs/plan-uebernahme-romanforge.md`
  (Stufe 2–4 offen, Stufe 1 „umgesetzt und abgenommen").
- Chronik-Erstlauf im Buch: `--keep 008,031,033,036 --baseline <150f0c1>`;
  Folge-`--compare` ohne `--baseline` ergab **nichts 35 / peter-behalten 11 /
  konflikt 2 (012, 025)**. Ausgangsstand versioniert unter
  `books/die-dritte-chronik/work/imports/romanforge/` (state.yaml + runs/).
- Offen: Nutzer liest 012/025 selbst und entscheidet. Nächster Schritt laut
  Plan: `--new` für Ashkara (neues Buchpaket über den Übernahme-Weg).

## Vorige Session (2026-09-21, Print-Optionen Trim/Profil/Bilder)

Paperback-Export waehlt Trim, Satzprofil und Bildmodus pro Job. Default
bleibt 5.5×8.5 / classic / full_page (kein stiller Satzwechsel). Cream-Limit
ist 776 (White 828, Groundwood 812). Dashboard: Dropdowns nur bei
Taschenbuch-Formaten. CLI:

`py -3 tools/export_manuscript.py --book pharao --scope book --style stil-02-poetisch --format paperback --trim-size 6x9 --layout-profile classic --illustration-mode full_page`

Dateiname enthaelt Slug `55x85-classic-full` bzw. `6x9-long_classic-inline`.
Print-Report: `within_kdp_page_limit`, `kdp_max_pages`. Keine automatische
Typo-Optimierung. Stale-Jobs koennen ueber Manifest+Report auf completed
gehoben werden.

Aelterer Komplett-Pilot ohne Varianten-Slug: Stempel `20260921-155209`
(924 Seiten, Limit damals 828). Neue Varianten 2026-09-21:

- A 5.5x8.5 classic full: **924** Seiten (nicht KDP-creme)
- B 6x9 classic full: **788** Seiten (–136 / –14,7 % gegen A; noch +12 ueber 776)
- C 6x9 long_classic full: **673** Seiten
- D 6x9 long_classic inline: **643** Seiten

Vergleich: `books/pharao/exports/stil-02-poetisch/book/print/print-comparison-20260921-pharao-abcd.md`.
Code, Tests, Doku, Pharao-000 und `cover-print.png` sind auf `main`.
Die grossen Interior-/Complete-/Wrap-PDFs bleiben lokal (regenerierbar).

| Datei | Rolle |
|---|---|
| `*-paperback-interior.pdf` | KDP-Innenleben (kein Cover, 924 Seiten) |
| `*-paperback-complete.pdf` | Lese-PDF: Vorderseite + Buch + Rueckseite (~926) |
| `*-paperback-wrap.pdf` | **Umschlag als eine Flaeche:** Rueckseite \| Ruecken \| Vorderseite (KDP-Cover-Upload) |
| `*-print-report.json` | Seitenzahl, Bundsteg, Warnungen |

Wrap ist nicht der Buchtext. Rueckenbreite cremefarben/SW = Seitenzahl ×
0,0635 mm (hier 924 → ~58,7 mm). Vorderseite nur aus manuellem
`assets/covers/cover-print.png` (kein Fallback auf Kindle-`cover.jpg`).
KDP-Creme-Maximum 776 Seiten — Report warnt, Satz bleibt unveraendert.

Kapitel **000** (Einleitung): Arbeitsdatei war ein erfundener Essay; Juni-Wstęp
mit Herodot-Zitat wiederhergestellt. Gate-Abbruch kam, weil das Release-Gate
erst 16./17.09. scharf wurde. Buch-Gate ERROR=0.

Reihenkatalog am Buchende in EPUB und Print (`tools/lib/series_catalog.py`).
`website.catalog: false` bei Anna, Grin, Pissemski.

Dashboard: http://127.0.0.1:8000 — Dropdowns Trim/Profil/Bilder nur bei
Taschenbuch-Formaten. Stale-Jobs: `tasklist`-Encoding plus Manifest+Report
(`tools/lib/dashboard_jobs.py`). Frontend zuletzt mit `--build` neu gestartet.

## Git / Branch

| Item | Wert |
|------|------|
| Aktiver Branch | `cline/pveejb87` (tracking `origin/cline/pveejb87`); `main` bleibt unberührt |
| Tip | `e93f4a2` RomanForge-Übernahme Stufe 1 (`import_markdown_original.py` + 31 Tests + Doku + Chronik-Ausgangsstand) |
| Vorher auf diesem Branch | `main`/Print-Workflow 2026-09-21 (Trim/Profil/Bilder, Pharao A–D, Reihenkatalog, Pharao-000). Davor `1beb55d` Chronik KDP-fertig + Tausend Seelen `stil-02-poetisch` Gate 0/0/5 + Aelita/Arsenjew Amazon |
| Davor auf main | `15566c0` Chronik Gate-Fixes; `bc5a1c6` / `c293fdc` Peter-I Raffung; `081b1ca` Marketingexport |
| Feature-Branch | `codex/geheime-geschichte-mongolen-prompts` – Inhalt ist in `main` enthalten; Branch kann später gelöscht werden |
| Arbeitsbaum | Print-Code ist versioniert. Lokal bleiben regenerierbare Print-PDFs unter `books/pharao/exports/.../print/` sowie `exports/.../work/`-HTML. `staging/` und `var/` gitignored. |

**Warnung (schon passiert):** Checkout auf ein altes `main` ohne die Codex-Commits ließ Buchordner als leere Hüllen zurück. Nicht blind zwischen Branches wechseln, ohne vorher zu prüfen, ob `books/*/book.yaml` noch da sind.

Committet (09/2026): 4 Top-5-Buchpakete (s. unten, alle Roh-Anlage 0 %), Tool-Fix Глава-I/X, `website:`-Block der neuen Pakete von `book:` auf top-level korrigiert, Regressionstests, Doku-Sync auf 12 Pakete. Lokal geblieben: `staging/conv5.py + staging/top5-quellen/` (Arbeitsmüll, jetzt via `.gitignore` ausgenommen) und `books/leben-arsenjews/work/cover.png` (Platzhalter).

**Bekannte Fehler (nicht von Stufe 1, Stand 2026-10-07):** volle Suite `py -3 -m unittest discover -s tests` → 319 Tests, 7 Fehler außerhalb des Import-Tools: 5 in `tests/test_print_export.py` (Print/PDF-Pipeline) und 2 in `tests/test_backend_api.py` (Webapp-API). Die 5 Print-Fehler sind nicht als bekannt dokumentiert; vor einem Merge nach `main` prüfen, ob sie von den offenen CSS-Änderungen (`book-print.css`/`epub.css`) kommen. Die Stufe-1-Suite (`tests/test_import_markdown_original.py`) ist isoliert 31/31 grün.

## Was das Repo ist

Buchzentrierte Übersetzungs-/Export-Werkbank (`books/<id>/`). Dashboard = FastAPI + React unter `webapp/`. Öffentliche Regal-Website = Vite + Three.js unter `webpage/` (nicht mit `webapp/` verwechseln).

## Buchpakete (12 mit `book.yaml`)

| ID | Titel | Default-Style | Website `sort_order` | Cover unter `assets/covers/` | Stand 09/2026 |
|----|-------|---------------|----------------------|------------------------------|---|
| `peter-i-buch-01` | Peter der Erste | stil-02-poetisch | 10 | `cover.jpg` | **LIVE** |
| `aelita` | Aëlita | stil-03-branderson | 10 | `cover.png` + `cover.jpg`-Sidecar + `coverII.jpg` | **LIVE 09/2026** (Amazon-Link + Marketing nach Amazon-Freigabe) |
| `leben-arsenjews` | Das Leben Arsenjews | stil-02-poetisch | 20 | `cover.jpg` / `.png` | **Release-Kandidat 09/2026** (Gate ERROR=0/WARNING=8, EPUB 20260917-212334 ohne Bypass; Kindle-Preview + Stichprobe offen) |
| `anna-karenina` | Anna Karenina | stil-02-poetisch | 20 | `annakarenina.png` (per `image_path`) + Regal-Kopie | **PARKIERT** (Nutzerentscheidung 09/2026) |
| `pharao` | Der Pharao | stil-02-poetisch | 30 | `cover.jpg` + `cover-print.png` | **LIVE**; Print-Optionen 2026-09-21 (A 924 / B 788 / C 673 / D 643; Cream 776) |
| `feuriger-engel` | Der feurige Engel | stil-02-poetisch | 50 | `cover.jpg` / `.png` | **LIVE** |
| `die-dritte-chronik` | Die dritte Chronik | stil-01-original | 60 | `cover.jpg` / `.png` | **KDP-fertig 2026-09-21** (Gate 0/13/36, 29/48 clean, 48/48 bebildert, EPUB 20260921-131112 mit 50 Bildern ohne Bypass; offen: Kindle-Preview, KDP-Upload). Seit 2026-10-07 Redaktionsweg über RomanForge (Stufe 1, `e93f4a2`); Ausgangsstand `work/imports/romanforge/` versioniert |
| `geheime-geschichte-mongolen` | Die Geheime Geschichte der Mongolen | stil-01-original | 70 | `cover.png` (neu 09/2026) + `coverII.png` |
| `kuprin-duell` | Das Duell | stil-01-original | 40 (nicht freigegeben) | `cover.png` |
| `kuprin-moloch` | Der Moloch | stil-01-original | 40 (nicht freigegeben) | `cover.png` (neu 09/2026) |
| `grin-wellenlaeuferin` | Die Wellenläuferin | stil-01-original | 40 (nicht freigegeben) | `cover.png` (neu 09/2026) |
| `pissemski-tausend-seelen` | Tausend Seelen | stil-01-original | 40 (nicht freigegeben) | `cover.png` (neu 09/2026) |

Die neuen Cover sind von Hand erstellte Hochformat-PNGs (688×1024, Regal nutzt
`object-fit: cover`); Vorgaenger wurden als `coverII.*` behalten. **Entscheidung
2026-09-13:** EPUB-first – 688×1024 reicht (auch fuer die Amazon-Auslieferung),
ein hoeher aufgeloestes Print-Cover wird erst fuer KDP-Paperback gebraucht. Die
Regal-Kopien unter `webpage/public/covers/` sind fuer `aelita` und
`geheime-geschichte-mongolen` noch die alten Bilder – nach der finalen
Cover-Wahl `python tools/build_shelf_website.py` laufen lassen.

Freigabe fürs Regal: in `export.yaml`

```yaml
website:
  enabled: true
  amazon_url: ''      # Button nur wenn gesetzt
  sort_order: 10
  catalog: false      # optional; false = nicht im Reihenkatalog am Buchende
```

Katalog neu bauen: `python tools/build_shelf_website.py` → `webpage/public/data/catalog.json` + `webpage/public/covers/`.

## Dashboard

- Start: `python tools/start_dashboard.py` oder `Dev-Start.cmd` / `dev.cmd`
- **Uebersetzungslaeufe laufen ueber das Dashboard** (Buch, Style, Kapitel/Scope,
  Provider); es benutzt dieselben `book.yaml`-Defaults (Modell,
  `ai.reasoning_effort`) und schreibt dieselben Szenen/Status wie die CLI.
- **Erster Start in dieser Umgebung (13.09.2026 geprueft):** `fastapi`/`uvicorn`
  fehlen im globalen Python 3.13 (`import fastapi` schlaegt fehl) und
  `webapp/frontend/node_modules` fehlt. Vorher einmalig
  `pip install -r requirements.txt` und `npm install` in `webapp/frontend/`
  (Node v22.22.2 / npm 10.9.7 sind vorhanden).
- **Fallstrick `python` im PATH (13.09.2026):** In dieser Umgebung zeigt `python`
  auf ein fremdes, per Anwendungssteuerungsrichtlinie blockiertes venv
  (`C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv`). Jeder
  `python …`-Aufruf scheitert dann mit „Eine Anwendungssteuerungsrichtlinie hat
  diese Datei blockiert" – auch `dev.cmd`. **Loesung: `py -3` verwenden**
  (Python 3.13.12 unter `AppData\Local\Programs\Python\Python313`) und dort
  `py -3 -m pip install -r requirements.txt` ausfuehren.
- **Bekannter Testfehler `test_backend_api` (2 Tests, belegt 2026-09-13):**
  `test_action_plan_translate_batch` und `test_job_start_allows_translate_batch`
  senden `ollama_model: gemma4:latest`, waehrend das lokal laufende Ollama nur
  `gemma4:e4b` anbietet. `_validate_ollama_model` antwortet deshalb korrekt mit
  400. Kein Regressionssignal des Repos – entweder Modell-Tag lokal anpassen
  (`ollama pull gemma4:latest`) oder den Test auf ein vorhandenes Modell
  umstellen.
- URL: http://127.0.0.1:8000
- Unter Windows nutzt `start_dashboard.py` `npm.cmd` für Frontend-Builds
- Nav **Website** (`/website`): Freigabe-Übersicht, Jobs „Katalog neu bauen“ / „Website-Build (dist)“
- Buch-Settings: Website-Felder (enabled, Amazon-URL, Sortierung) → schreiben in `export.yaml`
- API: `GET/PUT /api/books/{id}/website`, `GET /api/website/books`, Jobs `build_shelf_website` / `build_webpage_dist`
- Nach Frontend-Änderungen Frontend neu bauen und Dashboard neu starten

## Regal-Website (`webpage/`)

- Details: [webpage/README.md](../webpage/README.md)
- Preview (nicht `file://`): `python tools/preview_webpage.py` oder `Dev-Start-Webpage.cmd` → http://127.0.0.1:4173
- Production: `python tools/build_webpage_dist.py` → Inhalt von `webpage/dist/` deployen
- Live: https://stiftung.motivatier.de/classics/ auf der IONOS-VPS 87.106.3.155
  (Apache mit Plesk, dieselbe Maschine wie RomanForge). Docroot
  `/var/www/vhosts/motivatier.de/stiftung.motivatier.de`, Unterordner `classics/`,
  Eigentümer `motiadmin:psaserv`.
- Deploy 2026-10-21: `build_shelf_website.py` + `build_webpage_dist.py`, Upload per
  `scp` nach `/tmp/` und `rsync -a --delete` in den Docroot → **10 Bände live**
  (vorher 8). SSH als `root` mit `~/.ssh/codex_boddenblick_deploy`
  (`-o IdentitiesOnly=yes`), kein Standard-Key. Sicherung davor:
  `/root/classics-backup-20261021-144558.tar.gz`. Details:
  [offene-punkte.md](offene-punkte.md) Punkt 7.
- Branding: Motivatier Klassiks; Seiten Über uns / Impressum unter `webpage/public/`
- Mint-GLB-Hardcover: noch nicht eingebunden (Fallback-Boxen + Cover-Texturen)

## Marketingexport (neu 2026-09-13, X-Clip 2026-09-14)

Erzeugt aus vorhandenen Buchdaten X-Beitraege, YouTube-Materialien und ein
Kampagnenmanifest. Es wird **nichts veroeffentlicht** und **keine
Plattform-API** angesprochen. Details:
[marketing-export.md](marketing-export.md).

| Baustein | Pfad |
|---|---|
| CLI | `tools/export_marketing.py` (`--book`, `--style`, `--all`, `--dry-run`, `--provider`, `--regenerate`, `--no-texts`) |
| Kernlogik | `tools/lib/marketing_campaign.py` (IDs, Termine, Zeichengewichtung, Medien, Status, Manifest, Rendering) |
| Prompts | `tools/lib/marketing_prompts.py` (Datenbrief, JSON-Auswertung, Provenienz) |
| Globale Config | `config/marketing.yaml` (Marke, Shelf-URL, Zeitplan, **alle Plattformlimits**) |
| Buchlokal | top-level `marketing:` in `export.yaml` |
| Ausgabe | `books/<id>/exports/marketing/{campaign.json,posts.md,youtube.md,media.json,README.md}` |
| Texte | `work/marketing/generated.json`, Overrides `work/marketing/overrides/<post-id>.md` |
| Dashboard | Export-Seite → Karte **Marketingpaket** (+ Sektion **X-Clip**); `GET /api/books/{id}/marketing`, Actions `marketing_export` / `render_x_clip` |
| Tests | `tests/test_marketing_campaign.py`, `tests/test_marketing_prompts.py`, `tests/test_marketing_api.py`, `tests/test_render_x_clip.py` |
| X-Clip | `tools/render_x_clip.py` + `tools/lib/x_clip.py` (Cover + Song → quadratisches MP4, H.264/AAC, `faststart`); Ausgabe `exports/marketing/clips/<song>-x-<dauer>s.mp4` + `-check.jpg`; braucht System-ffmpeg, veraendert keine Quellen |

Wichtige Eigenschaften:

- **Keine Kosten ohne Auftrag:** ohne `--provider` werden nur vorhandene Texte
  verwendet. Neu erzeugt wird nur bei geaendertem Quellhash (Metadaten +
  Leseprobe), geaenderter `prompt_version` oder `--regenerate`;
  `generated_at` allein loest keine Neuversion aus.
- **EPUB bleibt unberuehrt:** der Manuskript-Export liest den
  `marketing:`-Block nicht (Regressionstest vorhanden).
- **Offene Angaben statt Luecken:** fehlender Amazon-Link →
  `needs_amazon_url` (Platzhalter bleibt im Manifest strukturiert sichtbar),
  fehlender YouTube-Link → `needs_youtube_url`, privates Video → `blocked`,
  Songdatei fehlt → `blocked`, kein Songdatensatz → `omitted`. Musik- und
  Videopositionen werden **nicht** mit Ersatztext gefuellt.
- **Editoriale Vorabsaetze sind keine Zitate:** die Leseprobe ueberspringt
  Blockzitate am Szenenanfang (Peter-I-Vorspaenne), damit kein redaktioneller
  Text als Autorenstelle erscheint.
- **Bilder:** thematische Zuordnung ueber Inhaltswoerter, nie automatisch nur
  das erste Bild; `_alt`-Dateien und `chapter-007-a.jpg` zaehlen nicht als
  eigenes Kapitelbild.
- **Zeichenpruefung:** konservative Naeherung (URL = 23, breite Zeichen = 2),
  Zielband 220–250, Limit 280 – ausdruecklich keine Plattformvalidierung.

**Pilot (`peter-i-buch-01`, 2026-09-13):** Texte als Repository-KI aus dem
Datenbrief erzeugt (keine API-Kosten). Ergebnis: `x-t0-intro` 232,
`x-t5-content` 239, `x-t8-sample` 228, `x-t12-second-angle` 206 gewichtete
Zeichen (alle `needs_amazon_url`), `yt-short-2` 443 Zeichen (`generated`),
Musikpositionen `omitted` (kein Songdatensatz). Offen im Pilot: Amazon-URL,
YouTube-Adresse, Songdaten, Kampagnenstart.

**Peter I Nachpflege (2026-09-14, keine Kosten, kein Publish):**
`website.amazon_url = https://amzn.to/4vLjAlF` (Kurzlink: Syntax ok,
`is_amazon_host: false`, `user_provided`); Song `song-01`
(`Peter der Erste – Lied zum Roman`, `assets/audio/peter-i-song-01.mp3`,
`ai_generated: true`) nach fester Namensregel; X-Clip
`exports/marketing/clips/song-01-x-45s.mp4` (45,0 s, 1080x1080, H.264/AAC,
ffmpeg-verifiziert) + Kontrollbild. Offen: 4 Songtexte (`text_missing`),
YouTube-URL, Kampagnenstart; X-Texte teils ueber Zielband (Override-Kuerzung).

**Umgebung:** `tzdata` wurde in `requirements.txt` aufgenommen (Windows liefert
ohne Daten keine `Europe/Berlin`-Zeitzone); `berlin_tzinfo()` faellt sonst
deterministisch auf die EU-Sommerzeitregel zurueck.

## Wichtige Buchstände

Verifizierter Fortschritt (dateibasiert im Default-Style, `staging/audit_progress.py`, 2026-09-13):

| Buch | Default-Style | Kapitel | komplett (Default) | offen |
|------|---------------|---------|--------------------|-------|
| `aelita` | `stil-03-branderson` | 30 | 30 | 0 (29 done, 1 review) |
| `anna-karenina` | `stil-02-poetisch` | 239 | 166 | 73 |
| `die-dritte-chronik` | `stil-01-original` | 48 | 48 | 0 |
| `feuriger-engel` | `stil-02-poetisch` | 16 | 16 | 0 |
| `geheime-geschichte-mongolen` | `stil-01-original` | 15 | 1 (13 Monolithe nur teilweise) | 1 |
| `grin-wellenlaeuferin` | `stil-01-original` | 33 | 0 | 33 |
| `kuprin-duell` | `stil-01-original` | 23 | 0 | 23 |
| `kuprin-moloch` | `stil-01-original` | 11 | 0 | 11 |
| `leben-arsenjews` | `stil-02-poetisch` | 104 | 104 | 0 (50 done, 54 review) |
| `peter-i-buch-01` | `stil-02-poetisch` | 18 | 18 | 0 (11 done, 7 review) |
| `pharao` | `stil-02-poetisch` | 69 | 69 | 0 |
| `pissemski-tausend-seelen` | `stil-01-original` | 44 | 0 | 44 (`stil-02-poetisch` komplett, `1beb55d`) |

Status-Drift B (Status `done`, Dateien unvollstaendig) ist in allen Paketen 0; die
Review-Marker (`aelita` 1, `leben-arsenjews` 54, `peter-i-buch-01` 7) sind gewollt.
Top-5 im Trockenlauf: 111 Kapitel / 221 Kommandos, 299.226 Quellwoerter (Summe
`words_source`).

**Pissemski / Chronik-Bilder:** Seit `1beb55d` auf `main`. Tausend Seelen
in `stil-02-poetisch` (Gate 0/0/5 + EPUB); Default-Style in `book.yaml`
bleibt `stil-01-original`. Chronik-Szenenbilder 021–048 sind versioniert
(Bebilderung 48/48).

### Geheime Geschichte der Mongolen

- Quelle `ja` → Ziel `de`; `structure.mode: scenes`; ~317 Abschnitte als `work/scenes/ja/NNN/scene-NN.md`
- Import: `python tools/import_geheime_geschichte.py` (Migration: `--migrate-existing`)
- Style `stil-04-original-geheim.md` = Embed-Profil (Interlinear/Edition)
- **Offen:** 14 Monolith-Kapitel in `stil-01-original` (`NNN/scene-01.md` = Ganzkapitel) abschnittsweise in `stil-04-original-geheim` neu uebersetzen: 000 (1 Szene) und 001–005, 007–013 (283 Szenen) = 284 Szenen, dazu Szene 07 in 014 (Provider-Fehler „Antwort ohne Text-Content“, `status/logs/014.log.md`)
- **Kapitel 006 – kein Drift:** dateiseitig fertig (20/20 Szenen in `stil-04-original-geheim`), aber aus einem Modellvergleich (deepseek-v4-pro/-flash, `anthropic/claude-sonnet-4.6`, zuletzt `qwen/qwen3.6-flash` am 2026-07-22, siehe `status/logs/006.log.md`). Der Review-Marker bleibt bewusst stehen
- **Style beim Batch zwingend explizit:** `tools/translate_batch.py --book geheime-geschichte-mongolen --missing --style stil-04-original-geheim --dry-run` plant 14 Kapitel (000, 001–005, 007–014) und ueberspringt 006 korrekt. Ohne `--style` (Default `stil-01-original`) plant derselbe Lauf 14 Kapitel **inkl. 006** – also ein bereits fertiges Kapitel erneut (Trockenlauf 2026-09-13, beide Varianten 14 Kommandos)

### Die dritte Chronik

- DE-Original (kein Übersetzungsprojekt); Import: `python tools/import_die_dritte_chronik.py`
- `chapter_as_scene`, Display `format: literary`
- Cover liegt; Export-Pfad bereit
- Redaktion 2026-09-18/19 ohne OpenRouter abgeschlossen: 008+012 clean 0/0,
  034 nur Satzzeichen, komplett-Runde 031/033/036 (Neufassungen; 031 bei
  0W/1I Stilmittel, 033+036 clean 0/0), mini 009/026/035 clean, 018 0W/4I,
  041 0W/1I. Gate ERROR=0/WARNING=13/INFO=36, 29/48 clean
- **Bebilderung komplett (2026-09-19):** 48/48 Kapitel bebildert
  (Kapitelbild 001-014, Szenenbild 008 + 015-048 = 49 Bilder + Cover).
  KDP-EPUB `book-die-dritte-chronik-stil-01-original-20260921-131112.epub`
  (50 Bilder, Gate 0 Fehler, ohne Bypass; aelterer Stempel
  `20260919-222611` ist ueberholt). Die Szenenbilder 021-048 sind noch
  untracked (Parallel-Session)
- **Offen (Release-Einschaetzung 2026-09-21):** Kindle Previewer +
  Leseprobe dieses EPUBs, KDP-Upload durch Nutzer, Amazon-URL
  zurueckspielen. Kontinuitaet: `docs/offene-punkte.md` Punkt 12.

### Leben Arsenjews

- Cover unter `assets/covers/` (nicht nur `work/cover.png`)
- Stil aktiv oft `stil-02-poetisch`; Übersetzung noch unvollständig (viele Kapitel fehlen)

### Top-5-Anlage 09/2026 (auf `main`)

Vier neue Roh-Pakete, alle `structure.mode: chapter_as_scene`, Default
`stil-01-original`, KI-Modell seit 2026-09-13 `deepseek/deepseek-v4.1-flash`
(Eintrag in `config/models.yaml` + `book.yaml: ai.model`),
`website.enabled: false` / `sort_order: 40`:

| ID | Titel | Kapitel | Cover |
|----|-------|---------|-------|
| `kuprin-duell` | Das Duell (Kuprin) | 23 (Глава I–XXIII) | `cover.png` |
| `kuprin-moloch` | Der Moloch (Kuprin) | 11 | `cover.png` |
| `grin-wellenlaeuferin` | Die Wellenläuferin (Grin) | 33 | `cover.png` |
| `pissemski-tausend-seelen` | Tausend Seelen (Pissemski) | 44 in 4 Teilen | `cover.png` |

- **Pilot 2026-09-13 gelaufen:** `kuprin-moloch` Kapitel 001 in `stil-01-original`
  mit `deepseek/deepseek-v4.1-flash` + `reasoning_effort: none`: 6682 Tokens
  (Prompt 4206 / Completion 2476), `finish_reason=stop`, 1245 DE-Woerter
  (119 % der 1049 RU-Woerter), Status `needs_review`
- Kette geprueft: `extract_scenes` → `translate_chapter` → `assemble_chapter`
  (`work/assembled/stil-01-original/001-translation-v1-…md`) → `export_manuscript
   --scope chapter --format epub` (`exports/stil-01-original/chapter/epub/…epub`,
  1,1 MB, nutzt `assets/covers/cover.png`)
- Rest offen: Moloch 002–011, Duell 23, Grin 33, Pissemski 44; Stilurteil anhand
  der Pilot-Szene noch offen (Default ueberall `stil-01-original`)
- Startbereit geprüft: `translate_batch --dry-run` plant 111 Kapitel / 221 Kommandos
  (kuprin-duell 23+22, kuprin-moloch 11+11, grin-wellenlaeuferin 33+33,
  pissemski-tausend-seelen 44+44); fehlende Quellszenen erzeugt der Batch selbst
- **Wichtig fuer Batch-Laeufe:** zuerst Quellszenen erzeugen (`extract_scenes`,
  macht der Batch automatisch). Ohne Quellszenen bleibt der Kapitelstatus auf
  `in_progress`, weil `chapter_translations_complete()` die Quellszenen braucht
- `--model` und `--reasoning-effort` muessen nicht mitgegeben werden – beides
  kommt aus `book.yaml`
- Tool-Fix: `Глава I` / `Глава X` (römische Ziffern, case-insensitive) in
  `tools/extract_chapters.py` + `tools/lib/rtf_parser.py`; Regressionstests in
  `tests/test_extract_chapters.py` (5 Tests grün)
- `website:`-Block lag eingerückt unter `book:` und wurde auf top-level
  gezogen. Generator und Dashboard lesen nur top-level (siehe AGENTS.md,
  Abschnitt Export); das Dashboard hätte sonst einen zweiten Block angehängt
- `staging/` (`conv5.py`, `top5-quellen/`) ist Arbeitsmüll und seit 09/2026 via
  `.gitignore` ausgenommen (lokal gefahrlos löschbar)
- Auswahlgrundlage: `docs/Motivatier-Classics-Umsetzungsrangliste-45.md`,
  Titelsuche: `docs/Motivatier-Classics-Titelsuche-2026-09-08.md`

## Bekannte Fallstricke (geprueft 2026-09-13)

Alle drei Punkte stammen aus einem lesenden Audit. Kernbefund-Quelle: `--missing`
arbeitet **dateibasiert** ueber `chapter_complete()` (`lib/output_paths.py`), nicht
ueber `status.json`. Reproduzierbarer Check, ohne etwas zu schreiben:

```bash
python tools/translate_batch.py --book <id> --missing --style <style> --provider prompt_file --dry-run
```

### 1. `status.json` ist durchgaengig zu pessimistisch

Der Status wird nur von `translate_chapter --auto-status` und `tools/status.py mark`
geschrieben; Importe und Migrationen setzen ihn nicht nach. Ergebnis: Kapitel, deren
DE-Szenen-Dateien vollstaendig vorliegen, stehen weiter auf `pending`.

| Buch | Datei komplett (Default-Style) | Status `done` | Drift |
|------|-------------------------------|---------------|-------|
| `aelita` | 30/30 | 0 | 30 |
| `leben-arsenjews` | 104/104 | 0 | 104 |
| `pharao` | 69/69 | 10 | 59 |
| `feuriger-engel` | 5/16 | 0 | 5 |
| `anna-karenina` | 2/239 | 0 | 2 |
| `geheime-geschichte-mongolen` | 1 komplett, 13 teilweise | 0 | 1 |
| `die-dritte-chronik` | 48/48 | 48 | 0 (konsistent) |

Der umgekehrte Fall (Status `done`, Dateien unvollstaendig) kam in keinem Paket vor –
der Status ist nie zu optimistisch, nur nie nachgefuehrt.

Reparatur ueber den offiziellen CLI-Weg, kein manuelles JSON:
`python tools/status.py --book <id> mark <nnn> done`.
Geplanter Umfang dieser Reparatur (Dry-Run geprueft): 193 Kapitel –
`aelita` 30, `leben-arsenjews` 104, `pharao` 59.

Zusatz: `status.json.style_mode` ist nur ein Snapshot vom Anlagezeitpunkt und lief nicht
nach (`aelita` `stil-01-original` vs. `book.yaml` `stil-03-branderson`, `leben-arsenjews`
`stil-01-original` vs. `stil-02-poetisch`). **Behoben 2026-09-13:** an `book.yaml`
angeglichen (5 Pakete, ueber `load_state`/`save_state`); `status.py` selbst hat fuer
dieses Feld keinen Schreibbefehl.

**Behoben 2026-09-13 (verlustfrei):** Alle Kapitel mit vollstaendigen DE-Szenen im
Default-Style haben jetzt den Endstatus. Ergebnis: `aelita` 30/30 (29 done, 1 review),
`leben-arsenjews` 104/104 (50 done, 54 review), `pharao` 69/69, `peter-i-buch-01` 18/18
(11 done, 7 review), `feuriger-engel` 16/16, `anna-karenina` 166/239 (73 offen),
`geheime-geschichte-mongolen` 14/15, `die-dritte-chronik` 48/48 (war schon konsistent).
Summe: 390 Kapitel auf `done`, 62 auf `needs_review`.

**Warnung aus diesem Fix:** `status.py mark <nnn> done` setzt `needs_review=false`,
`words_target=0` und `completed_at=<jetzt>`. Fuer das Nachreparieren bereits fertiger
Kapitel daher die Bibliotheks-API (`lib/status_manager.load_state`/`save_state`) nutzen und
die Review-Marker stehen lassen – sonst gehen Metadaten verloren. Der erste Anlauf wurde
genau deshalb am 2026-09-13 zurueckgerollt und aus der Git-Historie restauriert.

### 2. Default-Style weicht vom Arbeits-Style ab (Doppeluebersetzungsgefahr)

| Buch | `book.yaml` → `style_mode` | tatsaechlich komplett | Export-Ordner | Evidenz |
|------|---------------------------|-----------------------|---------------|---------|
| `peter-i-buch-01` | `stil-03-branderson` | 18/18 in `stil-02-poetisch` | nur `exports/stil-02-poetisch` | `status/logs/005.log.md`: „Style-Profil … stil-02-poetisch.md verwendet“ |
| `feuriger-engel` | `stil-01-original` | 16/16 in `stil-02-poetisch` | nur `exports/stil-02-poetisch` | – |
| `anna-karenina` | `stil-01-original` | 166/239 in `stil-02-poetisch` | `exports/stil-02-poetisch` + `stil-01-original` | – |
| `leben-arsenjews`, `pharao`, `aelita` | passt zum Arbeits-Style | vollstaendig | passend | – |

Folge im Trockenlauf: `peter-i-buch-01 --missing` mit dem Default plant **18 Kapitel
(~229k Quellwoerter)**, mit `--style stil-02-poetisch` dagegen **0**. Bei
`feuriger-engel` 11 statt 0, bei `anna-karenina` 237 statt 73.

**Behoben 2026-09-13:** `style_mode` in `book.yaml` auf den realen Arbeits-Style gesetzt –
`peter-i-buch-01`, `feuriger-engel` und `anna-karenina` auf `stil-02-poetisch`. Trockenlauf
ohne `--style` plant jetzt 0 / 0 / 73 Kapitel.

**Offen (2026-09-13 belegt):** `geheime-geschichte-mongolen` ist ein zweiter Fall.
`book.yaml` und `status.json` stehen auf `stil-01-original`, produktiv ist aber
`stil-04-original-geheim` (Kapitel 006 vollstaendig, 014 teilweise). Trockenlauf wie
oben: der Default plant 14 Kapitel **inklusive 006** (schon fertig ->
Doppeluebersetzung), `--style stil-04-original-geheim` plant 14 Kapitel mit 000 statt
006. Der Default bleibt vorerst unveraendert, weil die 13 Monolith-Kapitel noch in
`stil-01` liegen; bis zur Entscheidung gilt hier zwingend die explizite Style-Angabe.

**Regel:** Vor jedem `--missing`-Lauf Style explizit mitgeben und gegen die
Export-/Log-Evidenz pruefen.

Nebenbefund: `peter-i-buch-01` enthaelt Style-Ordner ohne Profil –
`work/scenes/de/stylized` (38 Szenen), `work/scenes/de/gemma4-vergleich` (4) sowie
`work/assembled/literal` und `work/assembled/stylized`. Alt-Vergleichsartefakte, die
die CLI nie erzeugen wuerde; verschoben am 2026-09-13 nach
`work/legacy/style-artefakte-20260913/` (65 Dateien: 38 + 4 + 1 + 22, siehe README dort).

### 3. `source_lang == target_lang` erzeugt Phantom-Kapitel (aktuell Die dritte Chronik)

In `books/die-dritte-chronik/work/scenes/de/` liegen die Kapitelordner `001…048`
(Quellszenen) **und** darunter `stil-01-original/001…048` (Zielszenen). Weil
`chapter_ids()` (`lib/workbench_state.py`) alle Verzeichnisse unter
`scenes/<source_lang>` als Kapitel-IDs sammelt, wird der Style-Ordner selbst zur
Kapitel-ID:

```
=== Batch: Die dritte Chronik ===
Kapitel ausgewaehlt (1): stil-01-original
[1/2] python tools/extract_scenes.py --book die-dritte-chronik --chapter stil-01-original
[2/2] python tools/translate_chapter.py --book die-dritte-chronik --chapter stil-01-original ...
```

Betroffen war jedes Paket mit `source_lang == target_lang` (aktuell nur die Chronik).

**Behoben 2026-09-13:** `chapter_ids()` ueberspringt Style-Ordner – ueber Namensabgleich
mit `styles/*.md` und, bei gleicher Quell- und Zielsprache, zusaetzlich ueber das
Strukturmerkmal „Ordner ohne direkte `scene-*.md`“. Regressionstests in
`tests/test_workbench_state.py`. Beleg nach dem Fix: `--missing --dry-run` plant
0 Kapitel (vorher 1), der Fortschritt meldet 48/48 statt 49/1. Der Guard entfaellt.

### 4. Reasoning-Modelle verbrennen `max_tokens` im Denkschritt (V4.1 Flash)

`deepseek/deepseek-v4.1-flash` ist reasoning-faehig. Ohne Steuerung schreibt das
Modell den kompletten `max_tokens`-Vorrat (`book.yaml: max_tokens_per_scene: 10000`)
in den Denkschritt und liefert **keinen** Text; der Client meldet dann korrekt
`OpenRouter-Antwort ohne Text-Content` (`finish_reason=length|error`).

Gemessen 2026-09-13 mit Mini-Calls (je ~400 Token Budget, `max_tokens=400`):

| `reasoning.effort` | Ergebnis | reasoning_tokens |
|--------------------|----------|------------------|
| nicht gesetzt | kein Content | 400/400 |
| `minimal` | kein Content | 142 |
| `low` | kein Content | 400/400 |
| **`none`** | **Text, `finish_reason=stop`** | **0** |

Nebenbei: Ein ungesetzter Lauf kann sehr lange „haengen“ (Header kommen, Body
nicht) – ein `httpx`-ReadTimeout greift dann nicht zuverlaessig; nicht blind
weiterwarten, sondern Prozess beenden und `status.py`-Status per
`lib/status_manager.mark_pending` zuruecksetzen.

**Behoben 2026-09-13:** `OpenRouterClient.reasoning_effort` +
`build_chat_payload()` in `tools/lib/openrouter_client.py`, CLI-Flag
`translate_chapter.py --reasoning-effort`, Fallback `book.yaml:
ai.reasoning_effort`. Die vier Top-5-Pakete stehen auf `none`; Regressionstests
in `tests/test_openrouter_client.py` (4 Tests). Laeufe ohne Angabe bleiben
unveraendert (Payload ohne `reasoning`).

### 5. Technische Kopfzeilen der Quelle landeten in der Uebersetzung

`work/chapters/NNN-source.md` beginnt mit `# Kapitel N: Глава I`, `*Buch: …*` und
`<!-- status: pending -->`. Im `chapter_as_scene`-Modus geht die ganze Datei in
den Prompt – das Modell uebernahm diese Zeilen unveraendert in die DE-Szene
(inklusive Kyrillisch in der Ueberschrift).

**Behoben 2026-09-13:** harte Ausgabe-Regel in `tools/lib/style_prompts.py`
(„Technische Kopfzeilen … weder uebersetzt noch uebernommen noch ersetzt“).
Beleg: Kapitel 001 beginnt nach `--overwrite` direkt mit dem Fliesstext.

Nebenbefund: `output.strip_control_metadata` in `export.yaml` ist ein **toter
Schalter** – kein Code liest ihn (nur `init_book.py` schreibt ihn). Die
Metadaten-Hygiene muss daher im Prompt bzw. in der Szene passieren.

Kleinigkeit: `status.json: title_de` ist bei Kapiteln ohne Ueberschrift der erste
Absatz (Log-Kopfzeile wird lang). Nur kosmetisch – der Export nutzt `title_de`
nicht.



### Fixes zu diesen Befunden (Fallstricke 1-5, alle umgesetzt 2026-09-13)

1. Status-Reparatur: dateibasiert und verlustfrei gesetzt – 390 Kapitel `done`, 62 `needs_review`; Metadaten aus der Git-Historie restauriert
2. `style_mode`: `book.yaml` von peter-i, feuriger-engel und anna auf `stil-02-poetisch`; `status.json.style_mode` in 5 Paketen angeglichen
3. Phantom-Kapitel bei `source_lang == target_lang`: `chapter_ids()` ueberspringt Style-Ordner (+ Regressionstests in `tests/test_workbench_state.py`)
4. Peter-I-Artefakte nach `work/legacy/style-artefakte-20260913/` verschoben (65 Dateien, README dort)
5. Reasoning-Steuerung fuer `deepseek/deepseek-v4.1-flash`: Client-Feld + `build_chat_payload()`, CLI `--reasoning-effort`, `book.yaml: ai.reasoning_effort: none`, 4 Regressionstests (Fallstrick 4)
6. Technische Kopfzeilen der Quelle (`# Kapitel …`, `*Buch: …*`, `<!-- … -->`) aus der Uebersetzung ausgeschlossen (Fallstrick 5)

### 6. Der Wort-Ratio-Korridor liess Raffung durch (Peter, entdeckt 2026-09-17)

`length_ratio` ist bewusst ein Ausreisser-Melder (ERROR `< 0.55`/`> 2.60`,
WARNING `< 0.75`/`> 2.10`) - und damit **kein Vollstaendigkeitsnachweis**.
Bei Peter der Erste lagen drei geraffte Szenen bei 0.76-0.91, der Buch-Median
bei 1.30: alle durchgerutscht, obwohl der Absatzschwund (-50 bis -73 Absaetze)
so gross war wie bei den drei bereits behobenen Szenen. Ein "0 Fehler, 0
Warnungen" aus dem alten Korridor war also kein Beweis fuer Vollstaendigkeit.

**Erkennen (read-only, ohne LLM):** Szenen-Wortratio und Absatzbestand ueber
alle Szenen rechnen; Median, Minimum und die unteren Ausreisser ansehen.
Segmentvergleich ueber 10 Textbloecke trennt Raffung (gleichmaessig duenn)
von einem abgebrochenen Lauf (leeres Ende).

**Behoben 2026-09-17:** zwei neue Kategorien (`paragraph_drop`,
`length_outlier`, Details in `AGENTS.md` -> Release-Gate), buchweite
Auswertung in `review_manuscript.py` **vor** dem KI-Review (damit
`--llm-scope flagged` die Szenen mitprueft), 7 neue Tests (23 gesamt), und
die drei Szenen selbst neu uebersetzt.

**Lehre fuer neue Buecher:** Nach jedem Buchlauf beide neuen Kategorien lesen,
Chunking-Limit bewusst setzen (globaler Default 24000 Zeichen, Peter wurde
mit 7000 nachgezogen), und `names.yaml` vorher fuellen - sonst laeuft
`accented_transliteration` leer.

## Tools (Auswahl, neu / relevant)

| Tool | Zweck |
|------|--------|
| `tools/lib/repetition.py` | Stil-Wiederholungsdetektor (Anapher/Trigramm/Echo/Stapelung/TTR/Leerformel), Kategorie `repetition_style`, nur INFO/WARNING; Tests `tests/test_repetition.py` + Fixtures `tests/repetition_fixtures.py` |
| `tools/build_shelf_website.py` | Katalog + Cover für `webpage/` |
| `tools/build_webpage_dist.py` | Production-Build `webpage/dist/` (Windows: `npm.cmd`) |
| `tools/preview_webpage.py` | Lokale Vorschau Port 4173 |
| `tools/import_geheime_geschichte.py` | Mongolen-Import |
| `tools/import_die_dritte_chronik.py` | Chronik-Import |
| `tools/optimize_asset_images.py` | Export-JPGs verkleinern |
| `tools/generate_illustration.py` | Higgsfield Kapitel/Szenen |
| `tools/review_manuscript.py` | Deterministischer Regelcheck + Release-Gate (`--llm none --fail-on-errors`); seit 2026-09-17 inkl. `paragraph_drop` + buchweitem `length_outlier`. Im Dashboard = Action `review` (Scope "Ganzes Buch" fuer den Median-Check) |
| `tools/export_manuscript.py --format paperback` | KDP-Taschenbuch-Innenleben (5,5×8,5, Bundsteg-Iteration, Kolumnentitel). `--format paperback-complete` addiert Cover-Print/Rueckseite/Wrap und Reihenkatalog. A5-Vorschau bleibt `--format pdf`. Wrap = Umschlagbogen, nicht der Buchtext. |
| `tools/lib/print_{spec,css,pdf,wrap}.py` | Print-Spec, EB-Garamond-CSS, Playwright-PDF, Wrap-Bogen |
| `tools/lib/series_catalog.py` | Reihenkatalog am Buchende (`website.enabled`, `website.catalog: false`) |
| `tools/export_marketing.py` | Marketingpaket (Beitraege, YouTube-Materialien, `campaign.json`); siehe [marketing-export.md](marketing-export.md) |

Higgsfield: [docs/higgsfield-integration.md](higgsfield-integration.md). Web-UI-Moodboards sind CLI-seitig nicht wählbar.

## Sinnvolle nächste Schritte

0. **Peter der Erste (`peter-i-buch-01`) – vorgezogen 2026-09-16, abgeschlossen 2026-09-17.** Anlass: zwei
   1-Stern-Kindle-Rezensionen („schlecht uebersetzt", „sinnentstellend";
   Konkurrenz-These moeglich, Verkaeufe ungeprueft). Entscheidung: Volluebersetzung.
   Phase A (deterministisch, ohne LLM): Vollscan `--llm none` ueber 18 Kapitel
   (Ausgangsstand ERROR=7/WARNING=6, der alte Report von 2026-06-15 war veraltet),
   danach 18 Fixes per `apply_review_suggestions.py --plan/--stage/--promote`
   (5 gemischte Kyrillisch-Tokens, 7 Akzent-Transliterationen, 4 doppelte
   Szenenheader, erfundene russische Lede in 018/01, `names.yaml` um 9 Eintraege
   erweitert).
   Phase B (mit Freigabe): die 3 gerafften Szenen (011/03 ratio 0.49 = ERROR,
   002/11 0.69, 003/05 0.60) mit Chunking + `--overwrite` neu uebersetzt.
   **Nachtrag 2026-09-17:** Der Vollscan **aller 175 Szenen** (Wortratio +
   Absatzvergleich + Segmentprofil) fand drei weitere geraffte Szenen, die der
   Wort-Korridor nie gemeldet hatte: `009/scene-08` (0.91, Absaetze 109:182),
   `010/scene-01` (0.84, 107:169), `010/scene-02` (0.76, 102:152) - alle in
   Buch II, also derselbe damalige Lauf. Ebenfalls neu uebersetzt
   (`--chunk-char-limit 7000`, 5/6/6 Chunks, `Finish-Reason=stop`); Endstand:
   1.35 / 1.31 / 1.29 mit Absaetzen 183:182 / 170:169 / 153:152.
   Endstand Buch: **175 Szenen, Ratio-Median 1.30, Minimum 0.97**
   (`003/scene-04`, inhaltlich unauffaellig: Absatzdefizit -7).
   Regelcheck danach: **18 Kapitel, 0 ERROR / 0 WARNING / 0 INFO**
   (mit aktiven neuen Kategorien), Export `book-peter-der-erste-stil-02-poetisch-20260917-113509.epub`
   mit `review_gate_errors: 0` und `review_gate_bypassed: false`.
   Offen (bewusst, keine Code-Aufgabe): EPUB-Groesse/ Bilder, Kindle Previewer,
   und eine menschliche Stichprobe der drei neu uebersetzten Szenen (der
   Regelcheck beweist Form, nicht Sinn).
   **Nutzerentscheidung 2026-09-17:** Stilfragen werden zurueckgestellt - es
   geht nur um belegbare Fehler und die Nachweisbarkeit der Regelchecks, nicht
   um ein Stilurteil.
   Details + Fehlerklassen: `docs/offene-punkte.md` (Punkt 0 und 0.1).
1. **Release-Gate (umgesetzt 2026-09-16).** `export_manuscript.py::preflight_review_gate`
   bricht bei Review-ERROR>0 mit Exit 2 ab; Bypass nur `--allow-review-errors`
   (wird im Manifest protokolliert). Neue Kategorien in `review_checks.py`:
   `mojibake`, `accented_transliteration`, `duplicate_heading`; Ausnahmen fuer
   echte Originalzitate via `work/review-allowlist.yaml`. Ein Export mit ERROR>0
   hat 2026-09 den live veroeffentlichten Peter-I-Band erreicht – das ist jetzt
   technisch verhindert. Doku: `AGENTS.md` (Abschnitt `Release-Gate`).
2. Marketingexport ist auf `main` (seit 2026-09-13/21). Offen: Amazon-URLs
   in den restlichen `export.yaml`-Dateien, optional Songdaten, optional
   `marketing.campaign_start`. Ein echter OpenRouter-Textlauf ist
   kostenpflichtig und braucht ausdrueckliche Freigabe.

3. Top-5-Pakete: Pilot `kuprin-moloch` 001 ist gelaufen (2026-09-13, `needs_review`, 6682 Tokens, EPUB-Kette geprueft) – naechster Schritt ist das Stilurteil anhand dieser Szene; danach je Buch `translate_batch.py --missing --style stil-01-original --auto-status --assemble-after` (batch-seitig kein `--model`/`--reasoning-effort` noetig, beides kommt aus `book.yaml`; ohne `--auto-status` bleibt `status.json` auf `pending` → Status-Drift)
4. Regal-Freigabe nach der finalen Cover-Wahl (`website.enabled: true`, `sort_order` 41–43; `kuprin-duell` behält 40), danach `python tools/build_shelf_website.py` – die Handcover sind seit `0162ef9` im Repo, die Regal-Kopien fuer aelita/mongolen aber noch alt. Cover entstehen weiter von Hand (kein CLI-Weg: `generate_illustration.py` kennt nur `--kind scene|chapter`)
5. Anna Karenina: 73 offene Kapitel (167–239) in `stil-02-poetisch` – Default-Style ist jetzt korrekt gesetzt
6. Geheime Geschichte: 14 Monolith-Kapitel abschnittsweise in `stil-04-original-geheim` (000, 001–005, 007–013 = 284 Szenen) plus Szene 07 in 014; Kapitel 006 ist dateiseitig fertig und wartet nur auf Review
7. Dritte Chronik (2026-09-21 nachm., KDP-fertig): Gate
   ERROR=0/WARNING=13/INFO=36, Bilder 48/48 (EPUB
   `...-20260921-131112.epub`, 50 Bilder, ohne Bypass). Redaktion
   kapitelweise ohne OpenRouter abgeschlossen (Stand 19.09.):
   komplett-Runde 031 (Neufassung 3753 W), 033 (3539 W, clean),
   036 (785 W, clean); mini 009/026/035 clean, 018 0W/4I, 041 0W/1I;
   025-Neufassung ("Der Onkel", 3103 W, 0/0/0 + repetitonsfrei).
   KDP-Rollen 21.09.: Autor Timo Verita, Editor Motivatier Classics
   (kein Uebersetzer – deutsches Original!), Verlag/Herausgeber
   Motivatier Stiftung (ohne "Hermann", repo-weit 71 Stellen
   ersetzt). Bio Variante 3 ("zwei Haelften", Buchstabenspiel,
   Welt-von-gestern + aktueller Schauplatz). Titelei + Impressum
   mit Classics oben, Stiftung unten. KDP-Texte:
   `docs/kdp-texte-dritte-chronik.md`. Rest-Tabelle
   `docs/offene-punkte.md` Punkt 6 + Punkt 12 (Kontinuitaet,
   Bio, Reihen-Auftritt; Kontinuitaets-Modell
   `docs/kontinuitaetspruefung-chronik.md`). Umgesetzt 21.09.
   nachm.: Untertitel "Die Chronik derer, die nicht schreiben
   duerfen" in `export.yaml: book.subtitle` + EPUB-Titelei
   (verifiziert) + Regal-Katalog neu; KDP-Serie "Chroniken des
   Mongolenreichs" (Band 1 Chronik, Band 2 Geheime Geschichte)
   nur in KDP anzulegen (Serientexte in `docs/kdp-texte-dritte-chronik.md`
   Abschnitt 5). Offen nur noch: Kindle Previewer +
   Leseprobe, KDP-Upload durch Nutzer, Amazon-URL zurueckspielen.
8. Regal: Amazon-URLs setzen; optional Mint-Hardcover-GLBs; Deploy von `webpage/dist/`
9. Optional: Feature-Branch `codex/geheime-geschichte-mongolen-prompts` remote löschen, wenn alle Clients auf `main` sind
10. Anna-Cover: geprueft und erledigt – `export.yaml` setzt `cover.mode: image` mit `image_path: assets/covers/annakarenina.png` (Vorrang vor `find_named_image(..., "cover")`); nur bei geleertem Feld droht der Platzhalter
11. Aelita Release-Kandidat (2026-09-17): Regelcheck 0/0 ueber alle 30 Kapitel. Kapitel 030: Romantext endet in der DE-Szene, Editionskommentare der RU-Quelle sind vollstaendig in den Anhang „Kommentare“ ausgelagert (`work/appendices/de/stil-03-branderson/kommentare.md`; alte Fassung in `work/legacy/`). Neues `appendices:`-Feature: `tools/lib/editorial_appendices.py`, Export EPUB/DOCX/PDF, Gate-Anrechnung in `review_checks.py` (27 Export-Tests gruen). 16 Kapitelbilder optimiert (Export-JPG q60, max 1600x2400, ~14,8 → ~2,4 MB); 12 Kapitel bleiben bewusst ohne Bild (009, 010, 011, 012, 016-019, 022-027); 11 wiedergefundene Motive fuer 020-030 liegen in `work/image-recovery/20260917-165216/verified/` zur freien Nutzung. Buch-EPUB `...-20260917-180435.epub` (Gate 0 Fehler) von Nutzer geprueft. Offen: Kindle Previewer.
12. Taschenbuch (2026-09-21, auf `main`): `--format paperback` =
    Innenleben; `--format paperback-complete` = Lese-PDF plus Wrap.
    Trim `--trim-size 5.5x8.5|6x9`, Profil `classic|long_classic`, Bilder
    `full_page|inline` getrennt waehlbar. Cream-Limit 776. Wrap =
    Umschlagbogen Rueckseite|Ruecken|Vorderseite, nicht der Text.
    Pharao A–D: 924 / 788 / 673 / 643 Seiten. Offen: menschliche
    Print-Leseprobe, Entscheidung 788 vs. 776 fuer 6x9 classic,
    `cover-print` fuer andere Titel.

Covers und Übersetzungsläufe (OpenRouter-Kosten) nur nach ausdrücklicher Freigabe starten.

## Nicht anfassen ohne Rückfrage

- `books/<id>/source/`
- `logic/`
- Secrets / `.env`
- Destruktive Git-Operationen (force-push, hard reset) ohne explizite Freigabe
