# Email Analyzer Website MVP

A defensive phishing email analyzer web app with:

- React frontend
- Python Flask backend
- Raw email paste or `.eml` upload
- Header checks: SPF/DKIM/DMARC hints, Reply-To mismatch, Return-Path mismatch
- URL analysis: shortened links, IP-based links, HTTP, suspicious TLDs, phishing words, simple brand impersonation hints
- Attachment analysis: risky extensions, SHA256 hash, entropy, suspicious strings
- Content analysis: phishing keyword and pattern detection
- Risk score and verdict
- SQLite scan history
- PDF report download

## Folder Structure

```text
email-analyzer-mvp/
├── backend/
└── frontend/
```

## Backend Setup

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

Backend runs on:

```text
http://localhost:5000
```

Health check:

```text
http://localhost:5000/api/health
```

## Frontend Setup

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on:

```text
http://localhost:5173
```

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Backend health check |
| POST | `/api/analyze` | Analyze pasted email or `.eml` file |
| GET | `/api/history` | Show scan history |
| GET | `/api/history/<id>` | Show one scan result |
| GET | `/api/report/<id>` | Download PDF report |

## Analyze Request Format

Use `multipart/form-data`:

- `raw_email`: pasted email text
- `email_file`: optional `.eml` or `.txt` file
- `attachments`: optional one or more attachment files

## Important Safety Notes

This MVP performs static analysis only. Do not execute uploaded attachments. For advanced malware attachment analysis, use a sandboxed isolated VM/container environment.

## Next Improvements

- Add login/signup with JWT
- Add MongoDB/PostgreSQL instead of SQLite
- Add DNS SPF/DMARC lookup using `dnspython`
- Add YARA scanning
- Add VirusTotal or other threat intelligence API integration
- Add admin dashboard charts
- Add Docker Compose
