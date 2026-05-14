import json
import os
import sqlite3
from datetime import datetime
from typing import Any

DB_PATH = os.path.join(os.path.dirname(__file__), "shadowbyte.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                created_at TEXT NOT NULL,
                text TEXT NOT NULL,
                data TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS progress (
                session_id TEXT PRIMARY KEY,
                quiz_attempts INTEGER DEFAULT 0,
                quiz_score_total INTEGER DEFAULT 0,
                flashcards_total INTEGER DEFAULT 0,
                flashcards_mastered INTEGER DEFAULT 0,
                updated_at TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS card_schedule (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                front TEXT NOT NULL,
                easiness REAL DEFAULT 2.5,
                interval INTEGER DEFAULT 1,
                repetitions INTEGER DEFAULT 0,
                next_review TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
            """
        )


def _normalise_session(data: dict[str, Any]) -> dict[str, Any]:
    session_id = data.get("id") or data.get("session_id")
    title = data.get("title") or data.get("filename") or "Untitled"
    created_at = data.get("created_at") or datetime.utcnow().isoformat()
    full_text = data.get("full_text") or data.get("text") or ""
    data["id"] = session_id
    data["session_id"] = session_id
    data["title"] = title
    data["filename"] = data.get("filename") or data.get("original_filename") or title
    data["original_filename"] = data.get("original_filename") or data["filename"]
    data["created_at"] = created_at
    data["full_text"] = full_text
    data["text"] = full_text
    return data


def save_session_data(session_id: str, data: dict[str, Any]):
    data = _normalise_session(dict(data))
    with get_conn() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO sessions (session_id, filename, created_at, text, data)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session_id,
                data["filename"],
                data["created_at"],
                data["full_text"],
                json.dumps(data),
            ),
        )


def get_session_data(session_id: str) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE session_id=?",
            (session_id,),
        ).fetchone()
    if not row:
        return None
    try:
        data = json.loads(row["data"])
    except Exception:
        data = {}
    data.setdefault("id", row["session_id"])
    data.setdefault("session_id", row["session_id"])
    data.setdefault("title", row["filename"])
    data.setdefault("filename", row["filename"])
    data.setdefault("original_filename", row["filename"])
    data.setdefault("created_at", row["created_at"])
    data.setdefault("full_text", row["text"])
    data.setdefault("text", row["text"])
    return data


def list_session_data() -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT session_id FROM sessions ORDER BY created_at DESC"
        ).fetchall()
    return [data for row in rows if (data := get_session_data(row["session_id"]))]


def delete_session_data(session_id: str):
    with get_conn() as conn:
        conn.execute("DELETE FROM messages WHERE session_id=?", (session_id,))
        conn.execute("DELETE FROM progress WHERE session_id=?", (session_id,))
        conn.execute("DELETE FROM card_schedule WHERE session_id=?", (session_id,))
        conn.execute("DELETE FROM sessions WHERE session_id=?", (session_id,))


def save_message(session_id: str, role: str, content: str, created_at: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (session_id, role, content, created_at),
        )


def get_history(session_id: str, limit: int = 6) -> list[dict[str, str]]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT role, content FROM messages
            WHERE session_id=?
            ORDER BY id DESC
            LIMIT ?
            """,
            (session_id, limit),
        ).fetchall()
    return list(reversed([dict(row) for row in rows]))


def record_quiz_score(session_id: str, score: int | float):
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO progress (session_id, quiz_attempts, quiz_score_total, updated_at)
            VALUES (?, 1, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                quiz_attempts = quiz_attempts + 1,
                quiz_score_total = quiz_score_total + excluded.quiz_score_total,
                updated_at = excluded.updated_at
            """,
            (session_id, score, now),
        )


def upsert_flashcard_progress(session_id: str, total: int, mastered: int):
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO progress (session_id, flashcards_total, flashcards_mastered, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                flashcards_total = excluded.flashcards_total,
                flashcards_mastered = excluded.flashcards_mastered,
                updated_at = excluded.updated_at
            """,
            (session_id, total, mastered, now),
        )


def get_progress(session_id: str) -> dict[str, float | int]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM progress WHERE session_id=?",
            (session_id,),
        ).fetchone()
    if not row:
        return {"quiz_avg": 0, "mastery_pct": 0}
    quiz_avg = row["quiz_score_total"] / max(row["quiz_attempts"], 1)
    mastery_pct = row["flashcards_mastered"] / max(row["flashcards_total"], 1) * 100
    return {"quiz_avg": round(quiz_avg, 1), "mastery_pct": round(mastery_pct)}


def upsert_card_schedule(session_id: str, card_id: str, front: str, next_review: str):
    with get_conn() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO card_schedule (id, session_id, front, next_review)
            VALUES (?, ?, ?, ?)
            """,
            (card_id, session_id, front, next_review),
        )


def get_card_schedule(card_id: str):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM card_schedule WHERE id=?",
            (card_id,),
        ).fetchone()


def update_card_schedule(card_id: str, easiness: float, interval: int, repetitions: int, next_review: str):
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE card_schedule
            SET easiness=?, interval=?, repetitions=?, next_review=?
            WHERE id=?
            """,
            (easiness, interval, repetitions, next_review, card_id),
        )


def get_due_card_ids(session_id: str) -> list[str]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id FROM card_schedule
            WHERE session_id=?
            ORDER BY
                CASE WHEN next_review <= datetime('now') THEN 0 ELSE 1 END,
                next_review ASC
            """,
            (session_id,),
        ).fetchall()
    return [row["id"] for row in rows]
