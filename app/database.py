import sqlite3
import uuid
from pathlib import Path
from typing import Dict, List

from app.api.config import DB_PATH


def get_db_connection() -> sqlite3.Connection:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    conn = get_db_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                dialog_id TEXT NOT NULL,
                participant_index INT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def insert_message(
    id: uuid.UUID,
    text: str,
    dialog_id: uuid.UUID,
    participant_index: int,
) -> None:
    conn = get_db_connection()
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO messages (id, text, dialog_id, participant_index)
            VALUES (?, ?, ?, ?)
            """,
            (str(id), text, str(dialog_id), participant_index),
        )
        conn.commit()
    finally:
        conn.close()


def select_messages_by_dialog(dialog_id: uuid.UUID) -> List[Dict[str, str]]:
    conn = get_db_connection()
    try:
        rows = conn.execute(
            """
            SELECT text, participant_index
            FROM messages
            WHERE dialog_id = ?
            ORDER BY created_at ASC
            """,
            (str(dialog_id),),
        ).fetchall()
        return [{"text": row["text"], "participant_index": row["participant_index"]} for row in rows]
    finally:
        conn.close()
