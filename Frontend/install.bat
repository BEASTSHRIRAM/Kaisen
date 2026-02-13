@echo off
echo.
echo ========================================
echo Kaisen Frontend Installation Script
echo ========================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed. Please install Node.js 18+ first.
    pause
    exit /b 1
)

echo [OK] Node.js version:
node --version
echo [OK] npm version:
npm --version
echo.

REM Clean previous installations
echo [INFO] Cleaning previous installations...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del /f /q package-lock.json
echo.

REM Install dependencies
echo [INFO] Installing dependencies...
call npm install --legacy-peer-deps

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Installation failed. Trying alternative method...
    call npm install --force
    
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Installation failed. Please check the errors above.
        pause
        exit /b 1
    )
)

echo.
echo [OK] Dependencies installed successfully!
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo [INFO] Creating .env file...
    copy .env.example .env
    echo [OK] .env file created. Please edit it with your backend URL.
) else (
    echo [OK] .env file already exists.
)

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your backend URL
echo 2. Run 'npm run dev' to start the development server
echo 3. Open http://localhost:5173 in your browser
echo.
pause
