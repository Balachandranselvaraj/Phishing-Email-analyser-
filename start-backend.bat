@echo off
REM Email Analyzer MVP - Backend Startup Script
REM This script starts only the Flask backend server

echo Starting Email Analyzer Backend...
echo.

REM Check if Python is installed
where python >nul 2>nul
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

cd backend

echo Installing dependencies...
python -m pip install -r requirements.txt -q

echo.
echo Starting Flask server on http://localhost:5000...
python app.py

pause
