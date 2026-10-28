
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "cyberpulse.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_type TEXT NOT NULL,
                target TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_scan(scan_type, target, result):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO scan_history (scan_type, target, result)
            VALUES (?, ?, ?)
            """,
            (scan_type, target, result)
        )


def get_history():
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            """
            SELECT id, scan_type, target, result, created_at
            FROM scan_history
            ORDER BY id DESC
            """
        ).fetchall()
