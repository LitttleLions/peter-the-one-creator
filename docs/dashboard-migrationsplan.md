# Dashboard-Migrationsplan

> Ziel: Die aktuelle Streamlit-Werkbank schrittweise entflechten und die
> langfristige Zielarchitektur **FastAPI + Vite/React** vorbereiten, ohne einen
> Big-Bang-Rewrite zu erzwingen.

## Leitentscheidung

FastAPI + Vite/React bleibt die Zielarchitektur fuer ein dauerhaftes,
zuverlaessiges Dashboard. Der richtige Zwischenstand ist aber nicht sofort
React, sondern eine stabile Python-Service-Schicht unter dem bestehenden
Streamlit-Dashboard.

Diese Service-Schicht ist inzwischen angelegt:

- `tools/lib/dashboard_jobs.py` steuert Hintergrundjobs framework-neutral.
- `tools/lib/workbench_api.py` enthaelt Kommando-Builder, Lesemodelle und
  Kontextmodelle fuer Uebersetzen, Review und Export.
- `tools/dashboard.py` bleibt Uebergangs-UI: Anzeigen, Formulare, Buttons,
  Status und Logs.
- Die CLI-Pipeline bleibt fuehrende Produktionslogik.

NiceGUI ist damit fuer diesen Migrationspfad nicht der bevorzugte Nachfolger.
Es waere eine kleinere lokale UI-Migration, wuerde aber die spaetere echte
Webapp weniger klar vorbereiten.

## Aktueller Stand

| Phase | Status | Ergebnis |
|---|---:|---|
| Phase 1: Jobsteuerung aus Streamlit herausloesen | Erledigt | `dashboard_jobs.py`, Pro-Job-JSON, Log-Tail, Stop, Refresh |
| Phase 1b: Streamlit-Job-UI stabilisieren | Erledigt | globales Job-Panel, Kontextanzeige, Auto-Refresh per Fragment falls verfuegbar |
| Phase 1c: Ollama/Quality Guards | Erledigt | Gemma als stabilerer Default, Ollama-JSON fuer Review, Prompt-Echo-Guard fuer Uebersetzung |
| Phase 2a: Kommando-Builder | Erledigt | Translate/Batch/Review/Export/Fixes/Init-Book werden in `workbench_api.py` gebaut |
| Phase 2b: Lesemodelle | Erledigt | Export-Meta, Styles, Namen, Illustrationen, Chunk-Hinweise |
| Phase 2c: Dashboard-Wrapper entfernen | Erledigt | Dashboard nutzt `workbench_api` direkt |
| Phase 2d: Buch-Setup extrahieren | Erledigt | Quellen-Erkennung, Titel/Autor-Vorschlag, `init_book`-Command |
| Phase 2e: Kontextmodelle | Erledigt | `translation_context`, `review_context`, `export_context` |
| Phase 3: Doku bereinigen | Erledigt | README und Architekturdocs spiegeln den neuen Stand |
| Phase 4: FastAPI-Backend | Erledigt | 4a-4g erledigt: Grundgeruest, JSON-Adapter, lesende API, Jobdetail/Stop, Action-Plan, Job-Start, SSE |
| Nebenstrang: Higgsfield-Moodboard | In Arbeit | Higgsfield-History bestaetigt: korrekt ist `style_id`; CLI-`custom_reference_id` ist fuer Moodboards falsch |
| Phase 5: Vite/React | In Arbeit | 5a-5e erste Slices erledigt: Uebersicht + Jobs, Settings, Uebersetzen, Review, Export, Bilder/Higgsfield, Namen, Logs |

## Phase 1: Jobsteuerung Aus Streamlit Herausloesen

**Status:** Erledigt.

**Ziel:** Ein robuster, framework-neutraler Job-Service ersetzt die alte
globale `.dashboard-batch-job.json`-Logik im Dashboard.

Neues Modul:

```text
tools/lib/dashboard_jobs.py
```

Umgesetzt:

- Pro-Job-Dateien unter `var/dashboard-jobs/<job-id>.json` statt einer globalen
  `.dashboard-batch-job.json`.
- Job-ID als stabile Kennung, z. B. Timestamp + Kind + Buch + Style.
- Job-Statusmodell definieren: `queued`, `running`, `completed`, `failed`,
  `stopped`, `stale`.
- Runner schreibt Heartbeat: `updated_at`, optional `phase`, `done`, `total`.
- Stop-Request ueber Job-Service; Prozessbaum-Kill bleibt Windows-tauglich,
  aber nicht mehr an Streamlit gebunden.
- Log-Tailing als reine Funktion: `read_log_tail(job_id, lines=80)`.

Akzeptanz:

- Ein Job kann per Python-Funktion gestartet, gelistet, gestoppt und ausgelesen
  werden, ohne Streamlit zu importieren.
- Alte Streamlit-UI nutzt diese Funktionen.
- Kein Dashboard-Code schreibt mehr direkt finale Job-Statuswerte.
- Ein erfolgreicher Job kann nicht mehr als `failed` mit `returncode: 0`
  erscheinen.

## Phase 2: Workbench-API Aus Streamlit Herausloesen

**Status:** Erledigt.

**Ziel:** Die Daten- und Kommando-Logik der Werkbank wird als Python-API
verfuegbar. Streamlit bleibt nur Anzeige, Formulare und Buttons.

Neues Modul:

```text
tools/lib/workbench_api.py
```

Umgesetzt:

- Lesemodelle fuer Styles, Namen, Export-Meta, Illustrationen, Chunk-Hinweise
  und Kontextdaten.
- Kommando-Builder aus `tools/dashboard.py` herausziehen:
  - Kapitel extrahieren
  - Szenen extrahieren
  - einzelne Szene/Kapitel uebersetzen
  - Batch-Uebersetzung planen/starten
  - Review planen/starten
  - Export erzeugen
  - Review-Fixes planen/stagen/promoten
- Buch-Setup-Operationen kapseln: lose Quellen finden, Titel/Autor aus
  Dateinamen vorschlagen, `init_book.py`-Command bauen.
- Namen-Editor-Operationen kapseln: laden und normalisieren.
- Kontextmodelle fuer spaetere JSON-Responses:
  - `translation_context`
  - `review_context`
  - `export_context`

Akzeptanz:

- `tools/dashboard.py` enthaelt keine grossen Kommando-Bau-Bloecke mehr.
- Streamlit ruft `workbench_api` und `dashboard_jobs` auf.
- Bestehende CLI-Tools bleiben unveraendert nutzbar.

## Phase 3: Streamlit Stabilisieren Und Verschlanken

**Status:** Erledigt mit dieser Doku-Aktualisierung.

**Ziel:** Das aktuelle Dashboard bleibt produktiv, wird aber duenner und
robuster.

Umgesetzt:

- Job-Panel nutzt den neuen Job-Service.
- Auto-Refresh nur fuer das Job-Panel einsetzen, z. B. Streamlit Fragment,
  falls die installierte Version es sauber unterstuetzt.
- Alle synchronen Kurzlaeufe laufen weiter ueber bestehende CLI-Aufrufe.
- Lange Laeufe laufen ausschliesslich ueber den Job-Service.
- README aktualisieren: Streamlit ist Uebergangs-UI, FastAPI + Vite/React ist
  Zielarchitektur.

Akzeptanz:

- Start/Stopp/Log-Anzeige funktionieren verlaesslich im aktuellen Dashboard.
- Ein aktiver Job bleibt nach Seitenwechsel sichtbar.
- Alte `.dashboard-batch-job.json` wird nicht mehr fuer neue Jobs genutzt.

## Phase 4: FastAPI-Backend Aufsetzen

**Status:** Erledigt. Phase 4a-4g ist umgesetzt.

**Ziel:** Die neue Service-Schicht wird ueber HTTP verfuegbar, noch ohne
vollstaendige React-UI.

Neuer Pfad:

```text
webapp/backend/
```

Backend-Endpunkte:

| Methode | Pfad | Zweck |
|---|---|---|
| `GET` | `/api/books` | Buecher + Kurzstatus |
| `GET` | `/api/books/{book_id}` | Buchdetails |
| `GET` | `/api/books/{book_id}/chapters` | Kapitel/Szenenstatus |
| `GET` | `/api/books/{book_id}/names` | Namenliste |
| `PUT` | `/api/books/{book_id}/names` | Namenliste speichern |
| `POST` | `/api/actions/plan` | CLI-Kommando trocken planen |
| `POST` | `/api/jobs` | Hintergrundjob starten |
| `GET` | `/api/jobs` | Jobs listen |
| `GET` | `/api/jobs/{job_id}` | Jobdetails |
| `POST` | `/api/jobs/{job_id}/stop` | Job stoppen |
| `GET` | `/api/jobs/{job_id}/events` | SSE fuer Status und Log-Tail |

Technik:

- `fastapi`, `uvicorn`, optional `sse-starlette` in `requirements.txt`.
- Backend nutzt nur `tools/lib/workbench_api.py` und
  `tools/lib/dashboard_jobs.py`.
- Kein Kopieren von Pipeline-Logik in FastAPI.

Pragmatischer erster Schnitt:

1. `webapp/backend/main.py` mit FastAPI-App und Healthcheck. **Erledigt.**
2. JSON-Adapter fuer lokale `Path`-/Dataclass-Strukturen. **Erledigt.**
3. `GET /api/books`, `GET /api/books/{book_id}`,
   `GET /api/books/{book_id}/chapters` und `GET /api/jobs`. **Erledigt.**
4. `GET /api/jobs/{job_id}` und `POST /api/jobs/{job_id}/stop`. **Erledigt.**
5. `POST /api/actions/plan` fuer trockene Kommando-Planung ohne Prozessstart.
   **Erledigt.**
6. `POST /api/jobs` fuer einen ersten eng begrenzten Jobtyp, z. B. Review oder
   Translate-Batch, der intern die bestehenden Command-Builder nutzt.
   **Erledigt fuer `review` und `translate_batch`.**
7. `GET /api/jobs/{job_id}/events` als SSE fuer Log-Tail und Progress.
   **Erledigt.**

Akzeptanz:

- Backend kann per `uvicorn webapp.backend.main:app --reload` gestartet werden.
- Swagger zeigt die Endpunkte.
- Job per HTTP starten/stoppen funktioniert.
- SSE liefert Status- und Log-Updates.

## Phase 5: Vite/React-Frontend

**Status:** In Arbeit. Phase 5a-5d und die ersten Phase-5e-Slices fuer
Settings, Uebersetzen, Review, Export, Namen und Logs sind umgesetzt.

**Ziel:** React ersetzt Streamlit schrittweise als UI, waehrend FastAPI die
einzige Backend-Schicht bleibt.

Neuer Pfad:

```text
webapp/frontend/
```

Technik:

- Vite `react-ts`.
- React Router fuer Ansichten: Uebersicht, Buch-Setup, Namen, Uebersetzen,
  Stiltest, Review, Export, Logs.
- TanStack Query fuer API-Daten und Mutationen.
- `EventSource` fuer `/api/jobs/{job_id}/events`.
- CSS orientiert sich an `docs/dashboard-design-system.md`.

Akzeptanz:

- Erste Paritaet: Uebersicht + Job-Panel. **Erledigt.**
- Settings erster Slice: buchbezogener Arbeitskontext pro Buch im
  Browser-LocalStorage; aktiver Stil, Translate-/Review-Defaults und
  Exportformat steuern Uebersicht und Workflows, ohne `book.yaml` zu schreiben.
  **Erledigt.**
- Uebersetzen erster Slice: sichtbarer Kontext, Kapitel-/Bereich-/Fehlende-
  Scope, Stil, Provider, Modell, Chunk-Grenze, Overwrite, Assemble-after und
  Start als echter `translate_batch`-Hintergrundjob. **Erledigt.**
- Review erster Slice: sichtbarer Kontext, Kapitel-/Bereich-/Alle-Scope, Stil,
  LLM-Auswahl, LLM-Scope, Modell, Fail-on-errors und Start als echter
  `review`-Hintergrundjob. **Erledigt.**
- Export erster Slice: sichtbarer Kontext, Stil, Kapitel-/Buch-Scope, Format,
  Allow-partial und Start als echter `export`-Hintergrundjob. **Erledigt.**
- Namen erster Slice: Namen-/Begriffsliste aus `names.yaml` lesend als Tabelle
  mit kompakten Kennzahlen. **Erledigt.**
- Logs erster Slice: Dashboard-Joblogs und buchlokale Statuslogs lesend als
  Liste mit Detailansicht. **Erledigt.**
- Streamlit wird erst entfernt, wenn die produktiven Workflows in React
  vollstaendig abgedeckt sind.

## Phase 6: Umschalten Und Aufraeumen

**Ziel:** React/FastAPI wird primaeres Dashboard.

Aufgaben:

- Vite-Build als statische Dateien ueber FastAPI ausliefern. **Erledigt.**
- Startskript fuer lokalen Ein-Prozess-Betrieb. **Erledigt:**

```powershell
python tools/start_dashboard.py
```

- README und AGENTS.md auf neue Startbefehle aktualisieren. **Erledigt.**
- Streamlit bleibt bewusst als Backup-Werkbank erhalten.
- Alte Jobdatei- und Streamlit-spezifische Hilfsfunktionen loeschen.

Akzeptanz:

- Lokaler Start ueber einen Befehl.
- Bestehende Buchpakete und CLI-Pipeline bleiben kompatibel.
- Keine produktive Logik haengt mehr an Streamlit.

Nachtrag: Die React-Buch-Settings speichern erst nach explizitem Klick auf
`In book.yaml speichern`. Bis dahin bleiben Aenderungen wie bisher lokale
UI-Defaults im Browser. Der Speichern-Endpunkt aktualisiert nur die betroffenen
YAML-Zeilen fuer `style_mode` und `ai.*`, statt `book.yaml` komplett neu zu
serialisieren.

## Reihenfolge Der Naechsten Konkreten Arbeiten

1. Nebenstrang Higgsfield: REST-/Web-UI-Pfad fuer `style_id` klaeren, bevor
   Bildgenerierung wieder ins Dashboard/React-Frontend kommt.
2. Danach Uebersetzen/Review erweitern: Detailvalidierung und bessere
   Modell-Defaults.
3. Spaeter: Buch-Settings aus React gezielt in die produktive Konfiguration
   ueberfuehren, wenn klar ist, welche Einstellungen wirklich global wirken
   sollen.
4. Zurueckgestellt: Namen editierbar machen, Log-Copy/Download und
   Fehlermeldungen vor Jobstart.
