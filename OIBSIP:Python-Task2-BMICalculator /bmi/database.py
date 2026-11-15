"""SQLite storage for BMI records (one table, many named users)."""
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "bmi_records.db"


class DatabaseError(Exception):
    """Raised when reading or writing the database fails."""


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    try:
        with closing(_connect()) as conn, conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS records (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL,
                       weight_kg REAL NOT NULL,
                       height_m REAL NOT NULL,
                       bmi REAL NOT NULL,
                       category TEXT NOT NULL,
                       recorded_at TEXT NOT NULL
                   )"""
            )
    except (sqlite3.Error, OSError) as exc:
        raise DatabaseError(f"Could not set up the database: {exc}") from exc


def add_record(username, weight_kg, height_m, bmi, category):
    try:
        with closing(_connect()) as conn, conn:
            conn.execute(
                "INSERT INTO records (username, weight_kg, height_m, bmi, category, recorded_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (username, weight_kg, height_m, bmi, category, datetime.now().isoformat(timespec="seconds")),
            )
    except (sqlite3.Error, OSError) as exc:
        raise DatabaseError(f"Could not save the record: {exc}") from exc


def get_records(username):
    """Records for one user, oldest first."""
    try:
        with closing(_connect()) as conn:
            rows = conn.execute(
                "SELECT recorded_at, weight_kg, height_m, bmi, category FROM records "
                "WHERE username = ? ORDER BY recorded_at, id",
                (username,),
            ).fetchall()
        return rows
    except (sqlite3.Error, OSError) as exc:
        raise DatabaseError(f"Could not read records: {exc}") from exc


def list_users():
    try:
        with closing(_connect()) as conn:
            rows = conn.execute("SELECT DISTINCT username FROM records ORDER BY username").fetchall()
        return [r[0] for r in rows]
    except (sqlite3.Error, OSError) as exc:
        raise DatabaseError(f"Could not read users: {exc}") from exc
