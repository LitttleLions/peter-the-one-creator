@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "DASHBOARD_HOST=127.0.0.1"
set "DASHBOARD_PORT=8000"
set "DASHBOARD_URL=http://%DASHBOARD_HOST%:%DASHBOARD_PORT%"
set "FRONTEND_DIR=webapp\frontend"

echo.
echo === peter-the-one: lokaler Start ===
echo Arbeitsverzeichnis: %CD%
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo FEHLER: "python" wurde nicht gefunden.
  echo Bitte Python 3 installieren und sicherstellen, dass es im PATH liegt.
  goto :fail
)

for /f "delims=" %%P in ('where python 2^>nul') do (
  echo Python ^(PATH^): %%P
  goto :python_shown
)
:python_shown
python -c "import sys; print('Python aktiv: ' + sys.executable + ' (' + sys.version.split()[0] + ')')"
echo Dashboard-Ziel: %DASHBOARD_URL%
echo.

where node >nul 2>&1
if errorlevel 1 (
  echo FEHLER: "node" wurde nicht gefunden.
  echo Node.js wird fuer den Frontend-Build unter %FRONTEND_DIR% benoetigt.
  goto :fail
)

where npm >nul 2>&1
if errorlevel 1 (
  echo FEHLER: "npm" wurde nicht gefunden.
  echo npm kommt mit Node.js; bitte Node.js neu installieren oder PATH pruefen.
  goto :fail
)

if not exist "tools\start_dashboard.py" (
  echo FEHLER: tools\start_dashboard.py fehlt.
  echo Bitte dieses Skript aus dem Repository-Root starten.
  goto :fail
)

if not exist "requirements.txt" (
  echo FEHLER: requirements.txt fehlt im Repository-Root.
  goto :fail
)

if not exist "%FRONTEND_DIR%\package.json" (
  echo FEHLER: Frontend-package.json fehlt: %FRONTEND_DIR%\package.json
  goto :fail
)

REM --- .env ---------------------------------------------------------------
if not exist ".env" (
  if exist ".env.example" (
    echo .env fehlt. Kopiere Vorlage aus .env.example ...
    copy /Y ".env.example" ".env" >nul
    if errorlevel 1 (
      echo FEHLER: Konnte .env nicht aus .env.example erzeugen.
      goto :fail
    )
    echo.
    echo HINWEIS: .env wurde aus .env.example angelegt.
    echo Bitte OPENROUTER_API_KEY in .env mit einem echten Key ersetzen,
    echo bevor OpenRouter-Uebersetzungen laufen sollen.
    echo Das Dashboard startet trotzdem; API-Calls ohne Key schlagen fehl.
    echo.
  ) else (
    echo FEHLER: Weder .env noch .env.example gefunden.
    echo Bitte .env anlegen ^(siehe Projekt-Doku^) und OPENROUTER_API_KEY setzen.
    goto :fail
  )
) else (
  findstr /R /C:"^OPENROUTER_API_KEY=sk-or-v1-DEIN_KEY_HIER" ".env" >nul 2>&1
  if not errorlevel 1 (
    echo HINWEIS: OPENROUTER_API_KEY in .env sieht noch nach Platzhalter aus.
    echo OpenRouter-Jobs brauchen einen echten Key; Dashboard-UI startet trotzdem.
    echo.
  )
  findstr /B /C:"OPENROUTER_API_KEY=" ".env" >nul 2>&1
  if errorlevel 1 (
    echo HINWEIS: In .env fehlt OPENROUTER_API_KEY.
    echo Ohne Key starten OpenRouter-Uebersetzungen nicht.
    echo.
  )
)

REM --- Python-Abhaengigkeiten --------------------------------------------
REM Nicht nur fastapi/uvicorn: start_dashboard importiert u. a. yaml via book_project.
python -c "import fastapi, uvicorn, yaml, dotenv, httpx, docx, PIL" >nul 2>&1
if errorlevel 1 (
  echo Python-Abhaengigkeiten fehlen oder sind unvollstaendig.
  echo Installiere aus requirements.txt fuer:
  python -c "import sys; print(sys.executable)"
  python -m pip install -r requirements.txt
  if errorlevel 1 (
    echo FEHLER: pip install -r requirements.txt ist fehlgeschlagen.
    goto :fail
  )
  python -c "import fastapi, uvicorn, yaml, dotenv, httpx, docx, PIL" >nul 2>&1
  if errorlevel 1 (
    echo FEHLER: Kernmodule sind nach der Installation weiterhin nicht importierbar.
    echo Pruefe, ob "python" und "python -m pip" dieselbe Installation nutzen.
    goto :fail
  )
  echo Python-Abhaengigkeiten installiert.
  echo.
)

REM --- Frontend npm-Abhaengigkeiten --------------------------------------
if not exist "%FRONTEND_DIR%\node_modules\" (
  echo Frontend node_modules fehlt unter %FRONTEND_DIR%.
  pushd "%FRONTEND_DIR%"
  if exist "package-lock.json" (
    echo Installiere reproduzierbar mit npm ci ...
    call npm ci
    if errorlevel 1 (
      echo FEHLER: npm ci ist fehlgeschlagen.
      popd
      goto :fail
    )
  ) else (
    echo HINWEIS: Keine package-lock.json - verwende npm install.
    call npm install
    if errorlevel 1 (
      echo FEHLER: npm install ist fehlgeschlagen.
      popd
      goto :fail
    )
  )
  popd
  echo Frontend-Abhaengigkeiten installiert.
  echo.
)

echo Starte Dashboard ueber tools\start_dashboard.py
echo URL: %DASHBOARD_URL%
echo Beenden: Ctrl+C in diesem Fenster
echo.

REM Browser oeffnen, sobald der Server typischerweise bereit ist (fester Port).
start "" cmd /c "timeout /t 3 /nobreak >nul && start %DASHBOARD_URL%"

python tools\start_dashboard.py --host %DASHBOARD_HOST% --port %DASHBOARD_PORT%
set "EXITCODE=%ERRORLEVEL%"

echo.
if not "%EXITCODE%"=="0" (
  echo Dashboard wurde mit Fehlercode %EXITCODE% beendet.
  pause
) else (
  echo Dashboard beendet.
  pause
)
exit /b %EXITCODE%

:fail
echo.
echo Start abgebrochen.
pause
exit /b 1
