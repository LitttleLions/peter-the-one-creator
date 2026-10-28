@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Projektumgebung fehlt. Siehe README: Python-Abhaengigkeiten.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" tools/preview_webpage.py
pause
