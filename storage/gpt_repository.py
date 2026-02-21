import sqlite3
from datetime import datetime
from typing import List, Dict


class GptRepository:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS gpt_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    role TEXT,
                    content TEXT,
                    created_at TEXT
                )
            """)

    def save_message(self, user_id: int, role: str, content: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO gpt_messages (user_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
            """, (user_id, role, content, datetime.utcnow().isoformat()))

    def get_history(self, user_id: int, limit: int = 20) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT role, content
                FROM gpt_messages
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (user_id, limit))

            rows = cursor.fetchall()

        rows.reverse()

        return [{"role": r[0], "content": r[1]} for r in rows]

    def clear_history(self, user_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                DELETE FROM gpt_messages
                WHERE user_id = ?
            """, (user_id,))
