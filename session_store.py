"""
session_store.py
SQLite-backed cross-session memory: stores conversation history,
user profiles, and analytics across browser sessions.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data/sessions.db")


def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(DB_PATH))
    c.row_factory = sqlite3.Row
    return c


_READY = False


def _init():
    global _READY
    if _READY:
        return
    with _conn() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id   TEXT PRIMARY KEY,
                user_profile TEXT DEFAULT 'Citizen',
                created_at   TEXT,
                last_seen    TEXT
            );
            CREATE TABLE IF NOT EXISTS messages (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id   TEXT,
                role         TEXT,
                content      TEXT,
                intent       TEXT,
                is_fallback  INTEGER DEFAULT 0,
                language     TEXT DEFAULT 'en',
                created_at   TEXT
            );
            CREATE TABLE IF NOT EXISTS events (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id   TEXT,
                intent       TEXT,
                is_fallback  INTEGER DEFAULT 0,
                language     TEXT DEFAULT 'en',
                created_at   TEXT
            );
        """)
    _READY = True


def upsert_session(session_id: str, user_profile: str = "Citizen"):
    _init()
    now = datetime.utcnow().isoformat()
    with _conn() as c:
        c.execute(
            """
            INSERT INTO sessions (session_id, user_profile, created_at, last_seen)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                user_profile = excluded.user_profile,
                last_seen    = excluded.last_seen
            """,
            (session_id, user_profile, now, now),
        )


def save_turn(session_id: str, role: str, content: str, meta: dict | None = None):
    """Persist one message turn; also logs an analytics event for assistant turns."""
    _init()
    meta = meta or {}
    now = datetime.utcnow().isoformat()
    lang = "ar" if meta.get("is_arabic") else "en"

    with _conn() as c:
        c.execute(
            """
            INSERT INTO messages (session_id, role, content, intent, is_fallback, language, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id, role, content,
                meta.get("intent"), 1 if meta.get("is_fallback") else 0,
                lang, now,
            ),
        )
        if role == "assistant":
            c.execute(
                """
                INSERT INTO events (session_id, intent, is_fallback, language, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session_id, meta.get("intent", "general"),
                    1 if meta.get("is_fallback") else 0,
                    lang, now,
                ),
            )


def load_history(session_id: str, limit: int = 8) -> list[dict]:
    """Return the most recent `limit` turns for this session (chronological)."""
    _init()
    with _conn() as c:
        rows = c.execute(
            """
            SELECT role, content FROM messages
            WHERE session_id = ?
            ORDER BY created_at DESC LIMIT ?
            """,
            (session_id, limit),
        ).fetchall()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


def get_session_profile(session_id: str) -> dict | None:
    _init()
    with _conn() as c:
        row = c.execute(
            "SELECT user_profile, created_at, last_seen FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
    return dict(row) if row else None


def analytics_summary() -> dict:
    """Aggregate stats across all sessions — used by the Admin tab."""
    _init()
    with _conn() as c:
        total       = c.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        arabic      = c.execute("SELECT COUNT(*) FROM events WHERE language = 'ar'").fetchone()[0]
        fallbacks   = c.execute("SELECT COUNT(*) FROM events WHERE is_fallback = 1").fetchone()[0]
        sessions    = c.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        top_intents = c.execute(
            "SELECT intent, COUNT(*) AS cnt FROM events GROUP BY intent ORDER BY cnt DESC LIMIT 5"
        ).fetchall()
        daily = c.execute(
            """
            SELECT substr(created_at,1,10) AS day, COUNT(*) AS cnt
            FROM events GROUP BY day ORDER BY day DESC LIMIT 7
            """
        ).fetchall()

    return {
        "total":       total,
        "arabic":      arabic,
        "fallbacks":   fallbacks,
        "fallback_rate": round(fallbacks / max(total, 1) * 100, 1),
        "sessions":    sessions,
        "top_intents": [(r["intent"], r["cnt"]) for r in top_intents],
        "daily":       [(r["day"], r["cnt"]) for r in reversed(daily)],
    }
