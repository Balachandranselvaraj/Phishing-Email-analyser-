# Email Analyzer MVP - PowerShell Startup Script
# This script starts both the backend Flask server and frontend Vite dev server

Write-Host "Starting Email Analyzer MVP..." -ForegroundColor Green
Write-Host ""

# Check if Python is installed
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Node.js is installed
$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
    Write-Host "Error: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Python found: $(python --version)" -ForegroundColor Green
Write-Host "✓ Node.js found: $(node --version)" -ForegroundColor Green
Write-Host ""

# Start Backend
Write-Host "Starting Backend (Flask) on http://localhost:5000..." -ForegroundColor Cyan
$backendScript = {
    cd backend
    python -m pip install -r requirements.txt -q
    python app.py
}
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

Start-Sleep -Seconds 3

# Start Frontend
Write-Host "Starting Frontend (Vite) on http://localhost:5173..." -ForegroundColor Cyan
$frontendScript = {
    cd frontend
    npm install -q
    npm run dev
}
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

Write-Host ""
Write-Host "Services are starting..." -ForegroundColor Green
Write-Host "Backend:  http://localhost:5000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C in each window to stop the services." -ForegroundColor Gray
