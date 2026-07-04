# Email Analyzer MVP - Startup Guide

## Prerequisites

Before running the application, ensure you have:

- **Python 3.8+** - [Download](https://www.python.org/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **npm** (comes with Node.js)

## Quick Start

### Option 1: Start Both Services (Recommended)

**Windows (Batch):**
```bash
start.bat
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -File start.ps1
```

This will open two windows:
- Backend Flask server on `http://localhost:5000`
- Frontend Vite dev server on `http://localhost:5173`

### Option 2: Start Services Individually

**Backend Only:**
```bash
start-backend.bat
```

**Frontend Only:**
```bash
start-frontend.bat
```

Then open your browser to `http://localhost:5173` (frontend) or `http://localhost:5000/api/health` (backend health check).

## Manual Setup (If Batch Files Don't Work)

### Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
python app.py
```

The backend will be available at `http://localhost:5000`

### Frontend Setup (In a New Terminal)
```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Endpoints

- **Health Check:** `GET http://localhost:5000/api/health`
- **Analyze Email:** `POST http://localhost:5000/api/analyze`
- **Get History:** `GET http://localhost:5000/api/history`
- **Get Report:** `GET http://localhost:5000/api/report/<scan_id>`

## Troubleshooting

### "Python is not installed or not in PATH"
- Install Python from https://www.python.org/
- Make sure to check "Add Python to PATH" during installation
- Restart your terminal after installation

### "Node.js is not installed or not in PATH"
- Install Node.js from https://nodejs.org/
- Restart your terminal after installation

### Port Already in Use
If port 5000 or 5173 is already in use:
- Modify `backend/app.py` (line 48) to change port
- Modify `frontend/package.json` to change the dev server port in the "dev" script

### pip/npm Install Issues
Delete the lock files and try again:
```bash
# For backend
cd backend
del -r venv
python -m pip install -r requirements.txt

# For frontend
cd frontend
del -r node_modules package-lock.json
npm install
```

## Development

- **Backend:** Hot-reload enabled by default (debug=True in app.py)
- **Frontend:** Hot Module Replacement (HMR) enabled by default in Vite

Simply save your files and the servers will automatically reload changes.
