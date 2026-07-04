import json
import sqlite3
from datetime import datetime, timezone
from config import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                subject TEXT,
                sender TEXT,
                risk_score INTEGER NOT NULL,
                verdict TEXT NOT NULL,
                result_json TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_scan(result):
    created_at = datetime.now(timezone.utc).isoformat()
    email_summary = result.get("email_summary", {})
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO scans (created_at, subject, sender, risk_score, verdict, result_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                created_at,
                email_summary.get("subject", ""),
                email_summary.get("from", ""),
                result.get("risk", {}).get("score", 0),
                result.get("risk", {}).get("verdict", "Unknown"),
                json.dumps(result),
            ),
        )
        conn.commit()
        return cur.lastrowid


def list_scans(limit=50):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, created_at, subject, sender, risk_score, verdict
            FROM scans
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_scan(scan_id):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT result_json FROM scans WHERE id = ?", (scan_id,)).fetchone()
        if not row:
            return None
        return json.loads(row["result_json"])
