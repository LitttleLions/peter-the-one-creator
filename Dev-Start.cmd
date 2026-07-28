@echo off
cd /d "%~dp0"
python tools/start_dashboard.py --build
pause
