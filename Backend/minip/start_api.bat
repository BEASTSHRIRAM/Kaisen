@echo off
echo Starting Kaisen API Server...
cd /d "%~dp0"
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)
python src/api_server.py
pause
