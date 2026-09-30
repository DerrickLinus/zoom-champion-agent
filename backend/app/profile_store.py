from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "hongshan.db"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS user_companions (
            user_id TEXT PRIMARY KEY,
            companion TEXT NOT NULL,
            source TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    return connection


def save_companion(user_id: str, companion: str, source: str) -> dict[str, str]:
    updated_at = datetime.now(timezone.utc).isoformat()
    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO user_companions (user_id, companion, source, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                companion = excluded.companion,
                source = excluded.source,
                updated_at = excluded.updated_at
            """,
            (user_id, companion, source, updated_at),
        )
    return {"user_id": user_id, "companion": companion, "source": source, "updated_at": updated_at}


def get_companion(user_id: str) -> dict[str, str] | None:
    with _connect() as connection:
        row = connection.execute(
            "SELECT user_id, companion, source, updated_at FROM user_companions WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None
