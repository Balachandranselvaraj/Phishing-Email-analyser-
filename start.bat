@echo off
REM Email Analyzer MVP - Startup Script
REM This script starts both the backend Flask server and frontend Vite dev server

echo Starting Email Analyzer MVP...
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

echo.
echo Starting Backend (Flask) on http://localhost:5000...
start "Email Analyzer Backend" cmd /k "cd backend && python -m pip install -r requirements.txt -q && python app.py"

timeout /t 3 /nobreak

echo Starting Frontend (Vite) on http://localhost:5173...
start "Email Analyzer Frontend" cmd /k "cd frontend && npm install -q && npm run dev"

echo.
echo Both services are starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Press Ctrl+C in each window to stop the services.
