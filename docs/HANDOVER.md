# Handover – Stand 2026-09-10 (Top-5-Anlage: 4 Buchpakete auf `main`, Roh-Anlage 0 %)

> Für neue Chats: zuerst [AGENTS.md](../AGENTS.md), dann diese Datei,
> bei Bedarf [README.md](../README.md) und [webpage/README.md](../webpage/README.md).

## Git / Branch

| Item | Wert |
|------|------|
| Aktiver Branch | `main` (tracking `origin/main`) |
| Tip (inhaltlich) | `af6873c` – Top-5-Buchpakete (Kuprin/Grin/Pissemski), roemische Kapitelziffern (Глава I/X), Regressionstests, Doku-Sync; danach folgen nur Doku-Nachzuege |
| Davor auf main | `6588800` (Titelsuche + Rangliste-45 als Vorlage); davor `a7c8c34` (Merge: FastAPI-Dashboard, Regal-Website, HANDOVER), `b376f5c`, `de91155` |
| Feature-Branch | `codex/geheime-geschichte-mongolen-prompts` – Inhalt ist in `main` enthalten; Branch kann später gelöscht werden |
| Arbeitsbaum (10.09.2026) | clean bis auf lokale Reste: `staging/` (jetzt in `.gitignore` ausgenommen) und `books/leben-arsenjews/work/cover.png` (Platzhalter) |

**Warnung (schon passiert):** Checkout auf ein altes `main` ohne die Codex-Commits ließ Buchordner als leere Hüllen zurück. Nicht blind zwischen Branches wechseln, ohne vorher zu prüfen, ob `books/*/book.yaml` noch da sind.

Committet (09/2026): 4 Top-5-Buchpakete (s. unten, alle Roh-Anlage 0 %), Tool-Fix Глава-I/X, `website:`-Block der neuen Pakete von `book:` auf top-level korrigiert, Regressionstests, Doku-Sync auf 12 Pakete. Lokal geblieben: `staging/conv5.py + staging/top5-quellen/` (Arbeitsmüll, jetzt via `.gitignore` ausgenommen) und `books/leben-arsenjews/work/cover.png` (Platzhalter).

## Was das Repo ist

Buchzentrierte Übersetzungs-/Export-Werkbank (`books/<id>/`). Dashboard = FastAPI + React unter `webapp/`. Öffentliche Regal-Website = Vite + Three.js unter `webpage/` (nicht mit `webapp/` verwechseln).

## Buchpakete (12 mit `book.yaml`)

| ID | Titel | Default-Style | Website `sort_order` | Cover unter `assets/covers/` |
|----|-------|---------------|----------------------|------------------------------|
| `peter-i-buch-01` | Peter der Erste | stil-03-branderson | 10 | `cover.jpg` |
| `aelita` | Aëlita | stil-03-branderson | 10 | `cover.jpg` / `.png` |
| `leben-arsenjews` | Das Leben Arsenjews | stil-02-poetisch | 20 | `cover.jpg` / `.png` |
| `anna-karenina` | Anna Karenina | stil-01-original | 20 | prüfen (Regal nutzt ggf. anderes Cover) |
| `pharao` | Der Pharao | stil-02-poetisch | 30 | `cover.jpg` |
| `feuriger-engel` | Der feurige Engel | stil-01-original | 50 | `cover.jpg` / `.png` |
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

### Geheime Geschichte der Mongolen

- Quelle `ja` → Ziel `de`; `structure.mode: scenes`; ~317 Abschnitte als `work/scenes/ja/NNN/scene-NN.md`
- Import: `python tools/import_geheime_geschichte.py` (Migration: `--migrate-existing`)
- Style `stil-04-original-geheim.md` = Embed-Profil (Interlinear/Edition)
- **Offen:** Legacy-DE-Monolithe (`scene-01.md` = Ganzkapitel) quarantineieren; Kapitel 006 abschnittsweise neu mit stil-04 + `--overwrite`

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

Zusatz: `status.json.style_mode` ist ebenfalls nur ein Snapshot vom Anlagezeitpunkt und
laeuft nicht nach. Aktuell abweichend: `aelita` (`status.json` `stil-01-original` vs.
`book.yaml` `stil-03-branderson`) und `leben-arsenjews` (`stil-01-original` vs.
`stil-02-poetisch`). Bei `peter-i-buch-01` stimmen beide formal auf
`stil-03-branderson`, obwohl real in `stil-02-poetisch` gearbeitet und exportiert wurde –
das Feld ist also kein verlaesslicher Hinweis auf den Arbeits-Style. `status.py` hat
fuer dieses Feld keinen Schreibbefehl; die `mark`-Reparatur laesst es unveraendert.

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

**Regel:** Vor jedem `--missing`-Lauf Style explizit mitgeben und gegen die
Export-/Log-Evidenz pruefen.

Nebenbefund: `peter-i-buch-01` enthaelt Style-Ordner ohne Profil –
`work/scenes/de/stylized` (38 Szenen), `work/scenes/de/gemma4-vergleich` (4) sowie
`work/assembled/literal` und `work/assembled/stylized`. Alt-Vergleichsartefakte, die
die CLI nie erzeugen wuerde; noch nicht verschoben.

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

Betroffen ist jedes Paket mit `source_lang == target_lang`. **Guard:** bei der Chronik
`--missing` nur mit `--from/--to` laufen lassen. Fix-Kandidat:
`chapter_ids()` darf Style-Ordner nicht als Kapitel-IDs zaehlen.

### Offene Fixes aus diesen Befunden

1. Status-Reparatur per `status.py mark … done` (aelita 30, leben-arsenjews 104, pharao 59; laesst `status.json.style_mode` unberuehrt)
2. `style_mode` korrigieren (peter-i, feuriger-engel, anna – redaktionelle Entscheidung)
3. `chapter_ids()` gegen Phantom-Kapitel absichern (+ Regressionstest)
4. Peter-I-Artefaktordner nach `work/legacy/` verschieben

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

1. Top-5-Pakete: Style bestätigen; Covers für Moloch/Wellenläuferin/Tausend Seelen; Start mit `translate_batch.py --missing --style …` (Style immer explizit)
2. Fallstricke abarbeiten (siehe „Bekannte Fallstricke“): Status-Reparatur, `style_mode` korrigieren, `chapter_ids()` absichern, Peter-I-Artefakte verschieben
3. Regal-Freigabe nach den Covers (`website.enabled: true`, `sort_order` 41–43); `staging/` kann lokal gelöscht werden
4. Geheime Geschichte: Legacy-DE-Monolithe beiseite legen; 006 abschnittsweise stil-04
5. Dritte Chronik: fehlende Kapitelbilder; Leser-EPUB prüfen
6. Regal: Amazon-URLs setzen; optional Mint-Hardcover-GLBs; Deploy von `webpage/dist/`
7. Optional: Feature-Branch `codex/geheime-geschichte-mongolen-prompts` remote löschen, wenn alle Clients auf `main` sind
8. Anna-Cover-Pfad im Paket prüfen (Regal hat Cover-Kopie unter `webpage/public/covers/`)

## Nicht anfassen ohne Rückfrage

- `books/<id>/source/`
- `logic/`
- Secrets / `.env`
- Destruktive Git-Operationen (force-push, hard reset) ohne explizite Freigabe
