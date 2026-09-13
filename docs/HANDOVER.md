# Handover – Stand 2026-09-10 (Top-5-Anlage: 4 Buchpakete auf `main`, Roh-Anlage 0 %)

> Für neue Chats: zuerst [AGENTS.md](../AGENTS.md), dann diese Datei,
> bei Bedarf [README.md](../README.md) und [webpage/README.md](../webpage/README.md).

## Git / Branch

| Item | Wert |
|------|------|
| Aktiver Branch | `main` (tracking `origin/main`) |
| Tip (committet) | `af6873c` – Top-5-Buchpakete (Kuprin/Grin/Pissemski), roemische Kapitelziffern (Глава I/X), Regressionstests, Doku-Sync; davor `6588800` (Titelsuche + Rangliste-45 als Vorlage) |
| Davor auf main | `a7c8c34` (Merge origin/main: FastAPI-Dashboard, Regal-Website, HANDOVER), `b376f5c`, `de91155` (Shelf-Website + Dashboard-Website-Controls) |
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

1. Top-5-Pakete: Covers für Moloch/Wellenläuferin/Tausend Seelen; `extract_scenes.py --all`; Start mit `translate_batch.py --missing`
2. Regal-Freigabe nach den Covers (`website.enabled: true`, `sort_order` 41–43); `staging/` kann lokal gelöscht werden
3. Geheime Geschichte: Legacy-DE-Monolithe beiseite legen; 006 abschnittsweise stil-04
4. Dritte Chronik: fehlende Kapitelbilder; Leser-EPUB prüfen
5. Regal: Amazon-URLs setzen; optional Mint-Hardcover-GLBs; Deploy von `webpage/dist/`
6. Optional: Feature-Branch `codex/geheime-geschichte-mongolen-prompts` remote löschen, wenn alle Clients auf `main` sind
7. Anna-Cover-Pfad im Paket prüfen (Regal hat Cover-Kopie unter `webpage/public/covers/`)

## Nicht anfassen ohne Rückfrage

- `books/<id>/source/`
- `logic/`
- Secrets / `.env`
- Destruktive Git-Operationen (force-push, hard reset) ohne explizite Freigabe
