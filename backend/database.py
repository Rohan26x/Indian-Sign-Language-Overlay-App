import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from config import DB_PATH

class DatabaseManager:
    """Manages SQLite schema and queries for ISL sign dictionary and fingerspelling."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = str(db_path or DB_PATH)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Signs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gloss TEXT UNIQUE NOT NULL,
                    english_keywords TEXT NOT NULL,
                    category TEXT,
                    emoji TEXT,
                    card_asset TEXT,
                    keyframe_track TEXT,
                    nmm_expression TEXT
                )
            """)

            # Fingerspelling table (A-Z and digits)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fingerspelling (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character TEXT UNIQUE NOT NULL,
                    gloss TEXT NOT NULL,
                    card_asset TEXT,
                    keyframe_track TEXT
                )
            """)

            # Interpreter feedback table (FR-7 / Use Case Diagram 4.2.2)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interpreter_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gloss TEXT NOT NULL,
                    original_phrase TEXT,
                    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    notes TEXT
                )
            """)
            conn.commit()

    def record_feedback(self, gloss: str, original_phrase: str = "", notes: str = "") -> int:
        """Logs missing or inaccurate signs for ISL interpreter review."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO interpreter_feedback (gloss, original_phrase, notes)
                VALUES (?, ?, ?)
            """, (gloss, original_phrase, notes))
            conn.commit()
            return cursor.lastrowid

    def get_all_feedback(self) -> List[Dict[str, Any]]:
        """Retrieves all interpreter feedback records."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM interpreter_feedback ORDER BY reported_at DESC")
            return [dict(r) for r in cursor.fetchall()]

    def lookup_sign(self, gloss: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM signs WHERE gloss = ? COLLATE NOCASE", (gloss,))
            row = cursor.fetchone()
            if row:
                res = dict(row)
                if res.get("keyframe_track"):
                    try:
                        res["keyframe_track"] = json.loads(res["keyframe_track"])
                    except Exception:
                        pass
                return res
            return None

    def lookup_fingerspelling(self, char: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM fingerspelling WHERE character = ? COLLATE NOCASE", (char,))
            row = cursor.fetchone()
            if row:
                res = dict(row)
                if res.get("keyframe_track"):
                    try:
                        res["keyframe_track"] = json.loads(res["keyframe_track"])
                    except Exception:
                        pass
                return res
            return None

    def get_all_glosses(self) -> List[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT gloss FROM signs ORDER BY gloss")
            return [r["gloss"] for r in cursor.fetchall()]

