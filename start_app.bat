@echo off
title ISL 3D Overlay Application Launcher
echo ===============================================================
echo   Real-Time Audio to ISL 3D Avatar Overlay Application
echo ===============================================================
echo.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo [1/3] Checking Database...
if not exist "backend\sign_lexicon.db" (
    echo Seeding ISL dictionary and fingerspelling database...
    python backend\seed_db.py
)

echo [2/3] Launching Python Async WebSocket Pipeline Server...
start "ISL Backend Pipeline" /min python backend\main.py

timeout /t 2 /nobreak >nul

echo [3/3] Launching Electron Transparent Overlay Frontend...
cd frontend
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)
call npx electron .

echo.
echo Application session ended.
