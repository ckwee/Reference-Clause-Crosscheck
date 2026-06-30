import json
import sqlite3
from pathlib import Path
from typing import Any

from config import settings
from models import ClauseSetSchema, StatementCheckSchema


def _connect():
    db_path = Path(settings.database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reference_check_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                review_title TEXT,
                reference_names TEXT,
                statement_count INTEGER NOT NULL,
                reference_clauses_json TEXT NOT NULL,
                checks_json TEXT NOT NULL
            )
        """)


def save_reference_check_run(
    review_title: str,
    reference_names: str,
    reference_clauses: ClauseSetSchema,
    checks: list[StatementCheckSchema],
) -> int:
    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO reference_check_runs (
                review_title,
                reference_names,
                statement_count,
                reference_clauses_json,
                checks_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                review_title,
                reference_names,
                len(checks),
                reference_clauses.model_dump_json(),
                json.dumps([item.model_dump() for item in checks]),
            ),
        )
        return int(cursor.lastrowid)


def list_reference_check_runs(limit: int = 25) -> list[dict[str, Any]]:
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, created_at, review_title, reference_names, statement_count
            FROM reference_check_runs
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_reference_check_run(run_id: int) -> dict[str, Any] | None:
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM reference_check_runs WHERE id = ?",
            (run_id,),
        ).fetchone()

    if not row:
        return None

    data = dict(row)
    data["reference_clauses"] = json.loads(data.pop("reference_clauses_json"))
    data["checks"] = json.loads(data.pop("checks_json"))
    return data
