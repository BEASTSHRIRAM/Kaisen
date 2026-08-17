@echo off
echo Starting Kaisen Log Collector (Continuous Mode)...
echo.
echo This will collect system metrics every 7 seconds
echo Press CTRL+C to stop
echo.

cd /d "%~dp0"
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)
python src\log_collection_main.py start
