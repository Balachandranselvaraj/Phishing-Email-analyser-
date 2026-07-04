@echo off
REM Email Analyzer MVP - Frontend Startup Script
REM This script starts only the Vite frontend dev server

echo Starting Email Analyzer Frontend...
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if errorlevel 1 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

cd frontend

echo Installing dependencies...
npm install -q

echo.
echo Starting Vite dev server on http://localhost:5173...
npm run dev

pause
