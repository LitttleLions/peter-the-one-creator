# Handover – Stand 2026-09-13 (Top-5-Pakete auf `main`; Status-/Style-Drift bereinigt, Fallstricke dokumentiert, Mongolen-Befund W1 belegt)

> Für neue Chats: zuerst [AGENTS.md](../AGENTS.md), dann diese Datei,
> bei Bedarf [README.md](../README.md) und [webpage/README.md](../webpage/README.md).

## Git / Branch

| Item | Wert |
|------|------|
| Aktiver Branch | `main` (tracking `origin/main`) |
| Tip (inhaltlich) | `af6873c` Top-5-Buchpakete; danach am 2026-09-13 Fixes: Status-Drift (verlustfrei, 390 Kapitel), `style_mode`-Abgleich, Phantom-Kapitel in `chapter_ids()`, Peter-I-Artefakte nach `work/legacy/`, Doku; zuletzt W1-Belegpruefung (Mongolen 006/014, Anna-Cover) |
| Davor auf main | `6588800` (Titelsuche + Rangliste-45 als Vorlage); davor `a7c8c34` (Merge: FastAPI-Dashboard, Regal-Website, HANDOVER), `b376f5c`, `de91155` |
| Feature-Branch | `codex/geheime-geschichte-mongolen-prompts` – Inhalt ist in `main` enthalten; Branch kann später gelöscht werden |
| Arbeitsbaum (13.09.2026) | nach den W1-Doku-Commits clean bis auf lokale, bewusst untracked Reste: `books/pissemski-tausend-seelen/assets/covers/cover.png` und `books/grin-wellenlaeuferin/assets/covers/cover.png` (Cover-Entwuerfe von Hand, 13.09.2026), `books/leben-arsenjews/work/cover.png` (Platzhalter) und `staging/` (gitignored, lokale Audit-/Reparaturhelfer inkl. `run-w1-mongolen-dryrun.cmd`, `run-w1-summary.cmd`) |

**Warnung (schon passiert):** Checkout auf ein altes `main` ohne die Codex-Commits ließ Buchordner als leere Hüllen zurück. Nicht blind zwischen Branches wechseln, ohne vorher zu prüfen, ob `books/*/book.yaml` noch da sind.

Committet (09/2026): 4 Top-5-Buchpakete (s. unten, alle Roh-Anlage 0 %), Tool-Fix Глава-I/X, `website:`-Block der neuen Pakete von `book:` auf top-level korrigiert, Regressionstests, Doku-Sync auf 12 Pakete. Lokal geblieben: `staging/conv5.py + staging/top5-quellen/` (Arbeitsmüll, jetzt via `.gitignore` ausgenommen) und `books/leben-arsenjews/work/cover.png` (Platzhalter).

## Was das Repo ist

Buchzentrierte Übersetzungs-/Export-Werkbank (`books/<id>/`). Dashboard = FastAPI + React unter `webapp/`. Öffentliche Regal-Website = Vite + Three.js unter `webpage/` (nicht mit `webapp/` verwechseln).

## Buchpakete (12 mit `book.yaml`)

| ID | Titel | Default-Style | Website `sort_order` | Cover unter `assets/covers/` |
|----|-------|---------------|----------------------|------------------------------|
| `peter-i-buch-01` | Peter der Erste | stil-02-poetisch | 10 | `cover.jpg` |
| `aelita` | Aëlita | stil-03-branderson | 10 | `cover.jpg` / `.png` |
| `leben-arsenjews` | Das Leben Arsenjews | stil-02-poetisch | 20 | `cover.jpg` / `.png` |
| `anna-karenina` | Anna Karenina | stil-02-poetisch | 20 | prüfen (Regal nutzt ggf. anderes Cover) |
| `pharao` | Der Pharao | stil-02-poetisch | 30 | `cover.jpg` |
| `feuriger-engel` | Der feurige Engel | stil-02-poetisch | 50 | `cover.jpg` / `.png` |
| `die-dritte-chronik` | Die dritte Chronik | stil-01-original | 60 | `cover.jpg` / `.png` |
| `geheime-geschichte-mongolen` | Die Geheime Geschichte der Mongolen | stil-01-original | 70 | `cover.png` |
| `kuprin-duell` | Das Duell | stil-01-original | 40 (nicht freigegeben) | `cover.png` |
| `kuprin-moloch` | Der Moloch | stil-01-original | 40 (nicht freigegeben) | fehlt |
| `grin-wellenlaeuferin` | Die Wellenläuferin | stil-01-original | 40 (nicht freigegeben) | fehlt |
| `pissemski-tausend-seelen` | Tausend Seelen | stil-01-original | 40 (nicht freigegeben) | fehlt |

Freigabe fürs Regal: in `export.yaml`

```yaml
website:
  enabled: true
  amazon_url: ''      # Button nur wenn gesetzt
  sort_order: 10
```

Katalog neu bauen: `python tools/build_shelf_website.py` → `webpage/public/data/catalog.json` + `webpage/public/covers/`.

## Dashboard

- Start: `python tools/start_dashboard.py` oder `Dev-Start.cmd` / `dev.cmd`
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
- Branding: Motivatier Klassiks; Seiten Über uns / Impressum unter `webpage/public/`
- Mint-GLB-Hardcover: noch nicht eingebunden (Fallback-Boxen + Cover-Texturen)

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
| `pissemski-tausend-seelen` | `stil-01-original` | 44 | 0 | 44 |

Status-Drift B (Status `done`, Dateien unvollstaendig) ist in allen Paketen 0; die
Review-Marker (`aelita` 1, `leben-arsenjews` 54, `peter-i-buch-01` 7) sind gewollt.
Top-5 im Trockenlauf: 111 Kapitel / 221 Kommandos, 299.226 Quellwoerter (Summe
`words_source`).

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
- **Offen:** restliche Kapitelbilder (Web-UI-Moodboard oder CLI); EPUB-Feinschliff

### Leben Arsenjews

- Cover unter `assets/covers/` (nicht nur `work/cover.png`)
- Stil aktiv oft `stil-02-poetisch`; Übersetzung noch unvollständig (viele Kapitel fehlen)

### Top-5-Anlage 09/2026 (auf `main`)

Vier neue Roh-Pakete, alle `structure.mode: chapter_as_scene`, Default
`stil-01-original`, `website.enabled: false` / `sort_order: 40`:

| ID | Titel | Kapitel | Cover |
|----|-------|---------|-------|
| `kuprin-duell` | Das Duell (Kuprin) | 23 (Глава I–XXIII) | `cover.png` |
| `kuprin-moloch` | Der Moloch (Kuprin) | 11 | fehlt |
| `grin-wellenlaeuferin` | Die Wellenläuferin (Grin) | 33 | fehlt |
| `pissemski-tausend-seelen` | Tausend Seelen (Pissemski) | 44 in 4 Teilen | fehlt |

- Stand: Kapitelquellen extrahiert, `work/scenes/de/` leer (0 %), Status `pending`
- Startbereit geprüft: `translate_batch --dry-run` plant 111 Kapitel / 221 Kommandos
  (kuprin-duell 23+22, kuprin-moloch 11+11, grin-wellenlaeuferin 33+33,
  pissemski-tausend-seelen 44+44); fehlende Quellszenen erzeugt der Batch selbst
- Offen vor dem Start: Style bestätigen (Default ist überall `stil-01-original`)
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

### Fixes zu diesen Befunden (alle umgesetzt 2026-09-13)

1. Status-Reparatur: dateibasiert und verlustfrei gesetzt – 390 Kapitel `done`, 62 `needs_review`; Metadaten aus der Git-Historie restauriert
2. `style_mode`: `book.yaml` von peter-i, feuriger-engel und anna auf `stil-02-poetisch`; `status.json.style_mode` in 5 Paketen angeglichen
3. Phantom-Kapitel bei `source_lang == target_lang`: `chapter_ids()` ueberspringt Style-Ordner (+ Regressionstests in `tests/test_workbench_state.py`)
4. Peter-I-Artefakte nach `work/legacy/style-artefakte-20260913/` verschoben (65 Dateien, README dort)

## Tools (Auswahl, neu / relevant)

| Tool | Zweck |
|------|--------|
| `tools/build_shelf_website.py` | Katalog + Cover für `webpage/` |
| `tools/build_webpage_dist.py` | Production-Build `webpage/dist/` (Windows: `npm.cmd`) |
| `tools/preview_webpage.py` | Lokale Vorschau Port 4173 |
| `tools/import_geheime_geschichte.py` | Mongolen-Import |
| `tools/import_die_dritte_chronik.py` | Chronik-Import |
| `tools/optimize_asset_images.py` | Export-JPGs verkleinern |
| `tools/generate_illustration.py` | Higgsfield Kapitel/Szenen |

Higgsfield: [docs/higgsfield-integration.md](higgsfield-integration.md). Web-UI-Moodboards sind CLI-seitig nicht wählbar.

## Sinnvolle nächste Schritte

1. Top-5-Pakete: Style bestätigen; Start dann mit `translate_batch.py --missing --style stil-01-original --auto-status --assemble-after` (ohne `--auto-status` bleibt `status.json` auf `pending` und es entsteht Status-Drift)
2. Regal-Freigabe nach den Covers (`website.enabled: true`, `sort_order` 41–43; `kuprin-duell` behält 40); `staging/` kann lokal gelöscht werden. Cover entstehen derzeit von Hand, nicht per CLI (`generate_illustration.py` kennt nur `--kind scene|chapter`); erster Entwurf: `books/pissemski-tausend-seelen/assets/covers/cover.png` (13.09.2026, noch untracked)
3. Anna Karenina: 73 offene Kapitel (167–239) in `stil-02-poetisch` – Default-Style ist jetzt korrekt gesetzt
4. Geheime Geschichte: 14 Monolith-Kapitel abschnittsweise in `stil-04-original-geheim` (000, 001–005, 007–013 = 284 Szenen) plus Szene 07 in 014; Kapitel 006 ist dateiseitig fertig und wartet nur auf Review
5. Dritte Chronik: fehlende Kapitelbilder (30/48 vorhanden); Leser-EPUB prüfen
6. Regal: Amazon-URLs setzen; optional Mint-Hardcover-GLBs; Deploy von `webpage/dist/`
7. Optional: Feature-Branch `codex/geheime-geschichte-mongolen-prompts` remote löschen, wenn alle Clients auf `main` sind
8. Anna-Cover: geprueft und erledigt – `export.yaml` setzt `cover.mode: image` mit `image_path: assets/covers/annakarenina.png` (Vorrang vor `find_named_image(..., "cover")`); nur bei geleertem Feld droht der Platzhalter

Covers und Übersetzungsläufe (OpenRouter-Kosten) nur nach ausdrücklicher Freigabe starten.

## Nicht anfassen ohne Rückfrage

- `books/<id>/source/`
- `logic/`
- Secrets / `.env`
- Destruktive Git-Operationen (force-push, hard reset) ohne explizite Freigabe
