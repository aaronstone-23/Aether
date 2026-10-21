"""Persistent local fallback for anonymous region and scam-type reports."""
import sqlite3
from contextlib import closing
from pathlib import Path

from flask import current_app


def _database_path() -> Path:
    configured_path = current_app.config.get("AETHER_REPORT_DB")
    path = Path(configured_path) if configured_path else Path(current_app.instance_path) / "reports.sqlite3"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(_database_path(), timeout=5)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS scam_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state TEXT NOT NULL,
            scam_type TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    return connection


def local_report_counts() -> list[dict]:
    with closing(_connect()) as connection:
        rows = connection.execute(
            "SELECT state, COUNT(*) FROM scam_reports GROUP BY state ORDER BY state"
        ).fetchall()
    return [{"state": state, "count": count} for state, count in rows]


def add_local_report(state: str, scam_type: str) -> None:
    with closing(_connect()) as connection:
        with connection:
            connection.execute(
                "INSERT INTO scam_reports (state, scam_type) VALUES (?, ?)",
                (state, scam_type),
            )
