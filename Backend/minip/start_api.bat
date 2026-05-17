@echo off
echo Starting Kaisen API Server...
cd /d "%~dp0"
python src/api_server.py
pause
