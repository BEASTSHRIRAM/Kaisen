@echo off
echo ========================================
echo   Kaisen Backend - Starting All Services
echo ========================================
echo.
echo This will start:
echo   1. Log Collector (collects metrics every 7 seconds)
echo   2. API Server (serves data to frontend on port 8000)
echo.
echo Press CTRL+C to stop all services
echo.

cd /d "%~dp0"

REM Start both services using Python's multiprocessing
python start_all_services.py
