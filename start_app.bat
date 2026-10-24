@echo off
title ISL 3D Overlay Application Launcher
echo ===============================================================
echo   Real-Time Audio to ISL 3D Avatar Overlay Application
echo ===============================================================
echo.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PY_CMD=python
) else if exist "D:\Python3.13.3\python.exe" (
    set PY_CMD="D:\Python3.13.3\python.exe"
) else (
    set PY_CMD=python
)

where npm >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set NPM_CMD=npm
) else if exist "D:\Node\npm.cmd" (
    set NPM_CMD="D:\Node\npm.cmd"
) else (
    set NPM_CMD=npm
)

echo [1/3] Checking Database...
if not exist "backend\sign_lexicon.db" (
    echo Seeding ISL dictionary and fingerspelling database...
    %PY_CMD% backend\seed_db.py
)

echo [2/3] Launching Python Async Streaming WebSocket Server (ws://127.0.0.1:8765)...
start "ISL Streaming Backend" /min %PY_CMD% backend\main.py

timeout /t 2 /nobreak >nul

echo [3/3] Launching Electron Transparent Overlay Frontend...
cd frontend
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call %NPM_CMD% install
)
call %NPM_CMD% start


echo.
echo Application session ended.
