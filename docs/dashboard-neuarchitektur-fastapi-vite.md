# Dashboard-Neuarchitektur — FastAPI + Vite

> Status: **Zielarchitektur mit begonnenem Migrationspfad**. Die
> Streamlit-Werkbank bleibt produktiv, aber Job- und Workbench-Logik sind
> inzwischen teilweise in framework-neutrale Python-Services ausgelagert.
> Erstellt 2026-06-19. Nachfolger der Analyse in
> [dashboard-jobsteuerung-analyse.md](./dashboard-jobsteuerung-analyse.md).
> Konkreter inkrementeller Migrationspfad:
> [dashboard-migrationsplan.md](./dashboard-migrationsplan.md).

## Ziel & Begründung

Das Streamlit-Dashboard soll langfristig durch eine **echte Webapplikation**
ersetzt werden:
**FastAPI-Backend (Python) + Vite-Frontend (React), gekoppelt über eine
HTTP-API mit Server-Sent-Events (SSE) für Live-Updates.**

Der Kernfehler von Streamlit für diese Werkbank ist das fehlende persistente
Server-Modell (Rerun des ganzen Skripts, kein echter Owner der Jobs). Das wurde
im aktuellen Streamlit-Dashboard entschärft, indem Jobs über
`tools/lib/dashboard_jobs.py` gesteuert werden. Die Zielarchitektur löst es
vollständig: Ein dauerhaft laufender FastAPI-Server besitzt die Jobs und pusht
Fortschritt/Log aktiv in den Browser.

**Warum FastAPI als Backend:** Das Projekt ist komplett Python. Die bereits
ausgelagerten Services (`tools/lib/workbench_api.py`,
`tools/lib/dashboard_jobs.py`) koennen direkt hinter HTTP-Endpunkten liegen.
FastAPI ist async-first, SSE/WebSocket-tauglich, lokal via uvicorn startbar und
spaeter ohne grundlegenden Umbau „live schaltbar".

**Vite ≠ Konkurrenz zu FastAPI:** Vite baut das Frontend (Browser-UI), FastAPI
liefert die API. Das ist das Standard-Duo einer echten Webapp.

## Architektur

```text
┌─────────────────────────┐        HTTP (JSON)        ┌──────────────────────────┐
│  Vite-Frontend (Browser)│  ───────────────────────▶ │  FastAPI-Backend (uvicorn)│
│  React SPA              │  ◀───  SSE (Live-Stream) ── │  - besitzt Job-Prozesse   │
│  - Bücher/Status-Views  │                           │  - /api/* Endpunkte       │
│  - Job-Panel (live)     │                           │  - SSE: Fortschritt + Log │
└─────────────────────────┘                           └────────────┬─────────────┘
                                                                    │ startet/stoppt
                                                                    ▼
                                              bestehende Python-CLIs + Job-Runner
                                              (translate_batch, export, review …)
```

Single-PC-Betrieb: beides läuft lokal. Dev: Vite-Dev-Server (Port 5173) mit
Proxy auf das FastAPI-Backend (Port 8000). Prod/lokal „fertig": Vite-Build als
statische Dateien, vom FastAPI-Server direkt ausgeliefert → **ein** Prozess,
ein URL.

## Backend (FastAPI) — Skizze

Verzeichnis z. B. `webapp/backend/`. Wiederverwendung der vorhandenen Module:

- `tools/lib/workbench_api.py` fuer Kommando-Builder, Lesemodelle und
  Kontextdaten.
- `tools/lib/dashboard_jobs.py` fuer Start/Stopp/List/Log/Progress von Jobs.
- `tools/lib/book_project.py`, `tools/lib/workbench_state.py` und
  `tools/lib/status_manager.py` fuer Buch- und Statusdaten.
- Bestehende CLIs fuer die eigentliche Pipeline.

Endpunkte (erster sinnvoller Schnitt):

| Methode | Pfad | Zweck |
|---|---|---|
| `GET` | `/api/books` | Buchpakete + Status-Übersicht |
| `GET` | `/api/books/{id}` | Buchdetails |
| `GET` | `/api/books/{id}/chapters` | Kapitel/Szenen-Status |
| `GET` | `/api/jobs` | aktive + jüngste Jobs |
| `GET` | `/api/jobs/{id}` | Jobdetails + Log-Tail |
| `POST` | `/api/jobs/{id}/stop` | Job stoppen (Prozessbaum) |
| `POST` | `/api/jobs` | Job starten (kind, book, style, provider, scope) |
| `GET` | `/api/jobs/{id}/events` | **SSE-Stream**: Fortschritt + Log-Zeilen live |
| `GET` | `/api/books/{id}/names` | Namenliste |
| `PUT` | `/api/books/{id}/names` | Namenliste speichern |
| `POST` | `/api/actions/plan` | CLI-Kommando trocken planen |

Job-Verwaltung:
- **Job-Service persistiert Metadaten** unter
  `var/dashboard-jobs/<job-id>.json` und Logdateien daneben.
- **FastAPI wird Server-Owner** fuer neue Jobs; der aktuelle Runner-Mechanismus
  bleibt die Bruecke zu den bestehenden CLIs.
- **Stopp laeuft ueber den Job-Service**: Prozessbaum-Kill bleibt
  Windows-tauglich, Status/Log bleiben auslesbar.
- **Live-Update via SSE**: der Server liest die Log-Datei inkrementell (tail)
  und pusht `progress`- und `log`-Events. Kein Polling, kein `tasklist`-Aufruf
  pro Refresh, keine blockierenden `sleep`.

## Frontend (Vite + React) — Skizze

Verzeichnis z. B. `webapp/frontend/` (Vite-Template `react-ts`).
- Views entsprechen den produktiven Dashboard-Bereichen: Überblick, Setup,
  Namen, Übersetzen, Stiltest, Export, Logs.
- **Routing:** React Router (eine Route je View).
- **Datenabruf/Caching:** TanStack Query (`useQuery` für Bücher/Status,
  `useMutation` für Start/Stopp/Export) — übernimmt Refetch & Invalidierung.
- **Job-Panel:** ein `useEventSource`-Hook abonniert
  `EventSource("/api/jobs/{id}/events")`; `progress`- und `log`-Events landen in
  State → Fortschrittsbalken + Log-Tail aktualisieren sich von selbst, ohne
  Reload und ohne Polling.
- Styling: das bestehende Design-System aus
  [dashboard-design-system.md](./dashboard-design-system.md) als CSS-Grundlage
  (CSS-Variablen lassen sich direkt übernehmen).

## Was migriert — was wird neu

| Bestandteil | Schicksal |
|---|---|
| Job-Runner, Subprozess-/Status-Mechanik | **bleibt**; `dashboard_jobs.py` ist bereits die framework-neutrale Schicht |
| `workbench_api.py` | **bleibt**; wird wichtigste Quelle fuer FastAPI-Responses und Commands |
| `lib/`-Module (book_project, workbench_state, status_manager, …) | **bleibt** |
| Bestehende CLIs (translate_batch, export_manuscript, …) | **bleibt 1:1** (werden weiter als Subprozess gestartet) |
| Streamlit-Widgets + CSS in `dashboard.py` | **wird ersetzt** durch React-Komponenten; Logik darunter bleibt erhalten |
| Globale `.dashboard-batch-job.json` | **ersetzt** durch Pro-Job-Dateien |

Wesentliche Erkenntnis: Es wird vor allem die **Präsentationsschicht** neu
gebaut. Die Domänen-/Job-Logik ist framework-unabhängig und bleibt.

## Lokaler Betrieb & „live schalten"

- **Standard lokal:** `python tools/start_dashboard.py`. Der Befehl baut das
  React-Frontend bei Bedarf und startet FastAPI auf `http://127.0.0.1:8000`.
- **Dev:** `python -m uvicorn webapp.backend.main:app --reload --host
  127.0.0.1 --port 8000` + `npm run dev` (Vite, Proxy `/api` → :8000). Zwei
  Terminals.
- **Lokal fertig / 1-Klick:** umgesetzt. `vite build` erzeugt statische Files;
  FastAPI liefert sie unter `/` aus.
- **Später online:** derselbe Stack hinter einem Reverse-Proxy; nur dann Auth
  ergänzen (lokal nicht nötig).

## Migrationsphasen (inkrementell, Streamlit bleibt bis zur Parität)

0. **Streamlit entflechten:** Job-Service und Workbench-API auslagern.
   → Status: erledigt, siehe `dashboard-migrationsplan.md`.
1. **Backend-Skelett:** FastAPI + `/api/books`, `/api/jobs` (list/detail/stop),
   danach start und SSE. Bestehende Services verwenden.
   → verify: Job per `curl`/Swagger starten/stoppen, SSE liefert Live-Log.
2. **Frontend-Skelett:** Vite-Projekt, Überblick-View + Job-Panel mit SSE.
   → verify: Übersetzungs-Batch im Browser starten/stoppen, Live-Fortschritt.
3. **Views portieren:** restliche Bereiche (Export, Stiltest, Namen, Logs)
   schrittweise.
4. **Umschalten:** Ein-Prozess-Start und statische Auslieferung sind umgesetzt;
   Streamlit bleibt vorerst als Legacy-Werkbank erhalten.

Streamlit kann während 1–3 parallel weiterlaufen → kein „Big Bang".

## Bewertung / Wahrscheinlichkeiten

- Löst Live-Update + zuverlässiges Start/Stopp (Owner + SSE): **~90 %**.
- Skaliert für „viele Ansichten / später online": **~90 %** (richtige Form).
- Hauptrisiko: einmaliger Mehraufwand fürs Frontend-Setup + Lernkurve FastAPI
  (überschaubar, da Backend klein bleibt).

## Offene Entscheidungen

- **Frontend-Framework:** ✅ **entschieden: React** (Vite-Template `react-ts`,
  React Router + TanStack Query).
- **Job-State:** Pro-Job-JSON-Dateien (einfach, reicht hier) vs. SQLite
  (History/Queries, wenn Job-Historie wichtig wird).
- **Echtzeit:** SSE (einfach, einseitig server→client — reicht für Logs/
  Fortschritt) vs. WebSocket (bidirektional, nur falls interaktivere Features
  kommen).
