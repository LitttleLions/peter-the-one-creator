# React-Dashboard: UX-Plan

Ziel: Die React-Oberflaeche bildet nicht die historisch gewachsene
Streamlit-Struktur nach. Navigation, Kontext und Aktionen werden getrennt,
damit jederzeit sichtbar ist, welche Einstellung welche Aktion beeinflusst.

## Grundregeln

- Die linke Navigation enthaelt nur App-Name, Buchauswahl, Navigation und
  globale Statushinweise.
- Workflow-Parameter liegen in der jeweiligen Seite, direkt bei den Aktionen:
  Stil, Kapitel, Provider, Modell, Umfang, Dry-run und Overwrite sind keine
  globalen Sidebar-Schalter.
- Jede Arbeitsseite beginnt mit einer Kontextleiste: Buch, Stil, Kapitel oder
  Umfang, Provider/Modell falls relevant, aktueller Jobstatus falls relevant.
- Lange Prozesse laufen ueber das globale Job-Panel. Das Panel zeigt Jobs,
  Details, Progress, Log-Tail und Stop-Aktion.
- Streamlit bleibt produktiv, bis die React-Ansichten echte Workflow-Paritaet
  erreicht haben.

## Navigation

| Route | Zweck | Primaere Aktionen | API |
|---|---|---|---|
| `/` | Einstiegsroute, leitet zum ersten Buch weiter | Buch waehlen | `/api/books` |
| `/books/:bookId/overview` | Buchstatus, Kapitelstatus, aktuelle Jobs | Jobdetail oeffnen, Job stoppen | `/api/books`, `/api/books/:id/chapters`, `/api/jobs`, SSE |
| `/books/:bookId/translate` | Uebersetzungsworkflow | spaeter planen/starten | spaeter `/api/actions/plan`, `/api/jobs` |
| `/books/:bookId/review` | Reviewworkflow | spaeter planen/starten | spaeter `/api/actions/plan`, `/api/jobs` |
| `/books/:bookId/export` | Exportworkflow | spaeter exportieren | spaeter `/api/actions/plan` |
| `/books/:bookId/names` | Namen und Begriffe | spaeter laden/speichern | spaeter Names-Endpunkte |
| `/books/:bookId/logs` | Logs und technische Details | spaeter Log ansehen | spaeter Log-Endpunkte |
| `/books/:bookId/settings` | Buchbezogener Arbeitskontext | aktiven Stil, Provider, Modelle und Defaults setzen | `/api/books`, `/api/books/:id/styles`, `/api/models` |
| `/setup` | Buch-Setup | spaeter neues Buch planen | spaeter `/api/actions/plan` |

## Erster Meilenstein

Phase 5d liefert nur Uebersicht und Job-Panel:

- Buchauswahl aus `/api/books`
- Kapitelstatus aus `/api/books/{book_id}/chapters`
- Jobliste aus `/api/jobs`
- Jobdetail aus `/api/jobs/{job_id}`
- Live-Updates ueber `/api/jobs/{job_id}/events`
- Stop ueber `POST /api/jobs/{job_id}/stop`

Nicht enthalten: Uebersetzungsformulare, Review-Formulare, Exporterzeugung,
Namen-Editor und Higgsfield-Reparatur.
