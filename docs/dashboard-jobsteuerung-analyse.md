# Dashboard-Jobsteuerung — Analyse & Empfehlung

> Status: **Analyse / Entscheidungsvorlage** (kein Code geändert).
> Erstellt 2026-06-19. Bezieht sich auf `tools/dashboard.py` (Job-Logik
> Zeilen ~62–429) und `tools/dashboard_job_runner.py`. Umgebung: Streamlit
> **1.58.0** installiert (`requirements.txt` pinnt `streamlit>=1.36.0`).

## Problemstellung

Das Dashboard kann Hintergrund-Läufe (Übersetzungs-/Review-/Export-Batches)
starten und stoppen. In der Praxis fühlt sich das unzuverlässig an:

- Die **Aktualisierung** läuft nicht — Fortschritt/Log frieren während eines
  Laufs ein.
- **Start/Stopp** verhält sich inkonsistent (Status springt, Stopp scheint
  nicht zu greifen).
- Insgesamt wirkt es träge und „schwierig".

## Aktueller Aufbau

**Modell: ein detached Subprozess + eine globale JSON-Statusdatei.**

1. Dashboard startet per `subprocess.Popen` den `dashboard_job_runner.py`
   (eigene Prozessgruppe via `CREATE_NEW_PROCESS_GROUP` auf Windows,
   `stdout/stderr → DEVNULL`).
2. Der **Runner** ist Eigentümer der Datei `.dashboard-batch-job.json`:
   schreibt `running` + eigene PID, dann `child_pid`, beim Ende
   `completed/failed` + Returncode. Die Kind-Ausgabe wird nach
   `var/dashboard-jobs/<stamp>-<kind>-<book>-<style>.log` geteed.
3. Das Dashboard liest die Datei **bei jedem Rerun** (`_refresh_batch_job`):
   terminaler Status → fertig; sonst PID-Lebendcheck (Windows: `tasklist`,
   sonst `os.kill(pid,0)`); lebt → `running`; tot → Abschluss aus dem Log
   **erraten** (`"Summary:"` / `"Traceback"`).
4. Fortschritt = Regex `^[done/total]` über den Log-Text. Stopp =
   `taskkill /PID … /T /F` (ganzer Baum) bzw. `kill -TERM`. „Ausblenden" =
   Jobdatei löschen.

## Ursachen (Symptom → Code)

| Symptom | Ursache |
|---|---|
| **„Aktualisierung funktioniert nicht"** | **Kein Auto-Refresh vorhanden.** Kein `st_autorefresh`, kein `@st.fragment(run_every=…)`. Das Panel rendert nur bei einem Rerun, der nur durch Nutzer-Interaktion ausgelöst wird. Während des Laufs friert Fortschritt + Log ein. **Hauptursache.** |
| **„Start/Stopp funktioniert nicht"** | **Doppelter Schreiber + Windows-Latenz.** Beim Stopp schreibt das Dashboard `stopped`, gleichzeitig schreibt der gekillte Runner `failed (Code …)` → **Write-Race**, letzter gewinnt → Label springt auf „fehlgeschlagen" statt „gestoppt". Zusätzlich braucht `taskkill /F` einen Moment; `_process_running` macht dann ein **blockierendes `time.sleep(1.0)`** und meldet evtl. noch „läuft". |
| **Träge / „schwierig"** | Jeder Refresh führt das **gesamte ~3076-Zeilen-Skript** neu aus + startet `tasklist` als Subprozess (inkl. 1-s-Pause), was den Render-Thread blockiert. |
| **Edge-Cases** | **Eine globale Jobdatei** für die ganze App (`_clear_batch_job()` vor jedem Start) → nur *ein* Job gleichzeitig; zweiter Start überschreibt das Tracking des ersten. Completion-Erkennung per String-Matching statt autoritativ. Äußere `Popen`-Ausgabe ist `DEVNULL` → Runner-Crash vor erstem Dateischreiben ist nicht diagnostizierbar. |

## Empfehlung (in dieser Reihenfolge)

Prozent = Wahrscheinlichkeit, dass die Maßnahme das adressierte Problem mit
Streamlit 1.58 zuverlässig löst.

### 1. Auto-Refresh via `@st.fragment(run_every="2s")` — Pflicht ⟶ ~90 %
Das Job-Panel in eine Fragment-Funktion mit `run_every` kapseln. Dann
aktualisiert sich **nur das Panel** alle ~2 s selbst (Fortschritt + Log-Tail
live), ohne das ganze Skript neu auszuführen. Genau dafür gebaut, ab Streamlit
1.37 verfügbar (1.58 vorhanden). Löst „Aktualisierung funktioniert nicht"
praktisch vollständig. Alternative: Paket `streamlit-autorefresh` — simpler,
aber rerun-schwer → zweite Wahl.

### 2. Stopp race-frei machen — Pflicht ⟶ ~80 %
Nur **ein** Eigentümer der Jobdatei (der Runner). Das Dashboard schreibt beim
Stopp **nicht** selbst `stopped`, sondern killt den Baum und setzt eine sticky
`stop_requested`-Markierung; das vom Runner anschließend geschriebene
„failed (killed)" wird dann als „gestoppt" angezeigt. Den blockierenden
`tasklist` + `sleep(1.0)`-Check ersetzen (siehe 3).

### 3. Heartbeat statt `tasklist`-Polling — empfohlen ⟶ ~75 %
Runner schreibt periodisch `updated_at` (+ optional strukturiertes
`done/total/phase`). Entscheidung im Dashboard: terminaler Status → fertig;
Heartbeat frisch (< ~30 s) → läuft; sonst → abgestürzt/stale. Entfernt den
Subprozess-Aufruf und die 1-s-Blockade und macht den Fortschritt zuverlässig
(kein Regex-Raten mehr).

**Kombiniert (1+2+3): ~85–90 %**, dass sich Start/Stopp/Update solide
anfühlen. Aufwand moderat, alles innerhalb des bestehenden Subprozess-Modells —
keine neue Infrastruktur.

## Optional / später (nur bei Bedarf)

- **Pro-Job-Dateien** statt einer globalen (`var/dashboard-jobs/<id>.json`) →
  mehrere Bücher parallel, kein Überschreib-Footgun. ~70 %, mehr Aufwand,
  nicht der Hauptschmerz.
- **SQLite-Job-Tabelle** (Queue/Status/Progress/History) ⟶ ~85 % Robustheit,
  aber deutlich mehr Code.
- **Orchestrierung aus Streamlit ziehen** (kleiner Worker-/FastAPI-Service,
  Streamlit nur als Viewer) ⟶ ~90 % Robustheit, aber für ein lokales
  Single-User-Dashboard überdimensioniert.

## Fazit

Der eigentliche Defekt ist **„kein Auto-Refresh"** + **„zwei Schreiber
kämpfen um die Statusdatei"**. Schicht 1+2(+3) räumt das mit hoher
Wahrscheinlichkeit auf, ohne Architektur-Umbau. D/E erst angehen, wenn echte
Parallel-Läufe oder Scheduling gebraucht werden.
