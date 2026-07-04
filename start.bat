@echo off
REM Email Analyzer MVP - Startup Script
REM This script starts both the backend Flask server and frontend Vite dev server

echo ============================================
echo   Email Analyzer MVP - Starting Up
echo ============================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if errorlevel 1 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Starting Backend (Flask) on http://localhost:5000...
start "Email Analyzer - Backend" cmd /k "cd backend && python -m pip install -r requirements.txt -q && python app.py"

echo [2/3] Starting Frontend (Vite) on http://localhost:5173...
start "Email Analyzer - Frontend" cmd /k "cd frontend && npm install -q && npm run dev"

echo [3/3] Waiting for services to be ready...
timeout /t 5 /nobreak >nul

echo Opening browser at http://localhost:5173...
start "" "http://localhost:5173"

echo.
echo ============================================
echo   Both services are running!
echo   Backend:  http://localhost:5000
echo   Frontend: http://localhost:5173
echo ============================================
echo.
echo Close the Backend and Frontend windows to stop the services.
pause
