"""AI Tank — SQLite persistence (API-aligned)."""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional

DB_PATH = Path(__file__).resolve().parent / "aitank.db"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _id() -> str:
    return uuid.uuid4().hex[:10]


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
              id TEXT PRIMARY KEY,
              handle TEXT UNIQUE NOT NULL,
              roles TEXT NOT NULL DEFAULT '[]',
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pitches (
              id TEXT PRIMARY KEY,
              originator_id TEXT NOT NULL,
              title TEXT NOT NULL,
              problem TEXT NOT NULL,
              solution TEXT NOT NULL,
              why_now TEXT DEFAULT '',
              starlink_flag INTEGER NOT NULL DEFAULT 0,
              status TEXT NOT NULL DEFAULT 'public',
              license_terms TEXT DEFAULT 'originator-owns',
              nova_score REAL,
              score_breakdown TEXT,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS interests (
              id TEXT PRIMARY KEY,
              pitch_id TEXT NOT NULL,
              investor_id TEXT NOT NULL,
              created_at TEXT NOT NULL,
              UNIQUE(pitch_id, investor_id)
            );

            CREATE TABLE IF NOT EXISTS permission_requests (
              id TEXT PRIMARY KEY,
              pitch_id TEXT NOT NULL,
              investor_id TEXT NOT NULL,
              originator_id TEXT NOT NULL,
              scope TEXT NOT NULL,
              message TEXT DEFAULT '',
              status TEXT NOT NULL DEFAULT 'pending',
              created_at TEXT NOT NULL,
              decided_at TEXT
            );

            CREATE TABLE IF NOT EXISTS boards (
              id TEXT PRIMARY KEY,
              slug TEXT UNIQUE NOT NULL,
              title TEXT NOT NULL,
              theme TEXT NOT NULL,
              window_start TEXT,
              window_end TEXT,
              score_types TEXT NOT NULL,
              rules TEXT NOT NULL DEFAULT '{}',
              prizes TEXT NOT NULL DEFAULT '{}',
              status TEXT NOT NULL DEFAULT 'open'
            );

            CREATE TABLE IF NOT EXISTS board_enrollments (
              pitch_id TEXT NOT NULL,
              board_id TEXT NOT NULL,
              enrolled_at TEXT NOT NULL,
              PRIMARY KEY (pitch_id, board_id)
            );

            CREATE TABLE IF NOT EXISTS score_entries (
              id TEXT PRIMARY KEY,
              pitch_id TEXT NOT NULL,
              board_id TEXT,
              score_type TEXT NOT NULL,
              value REAL NOT NULL,
              breakdown TEXT,
              source TEXT NOT NULL,
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS idea_clusters (
              id TEXT PRIMARY KEY,
              label TEXT NOT NULL,
              pitch_ids TEXT NOT NULL,
              notes TEXT DEFAULT '',
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS recycle_offers (
              id TEXT PRIMARY KEY,
              pitch_id TEXT NOT NULL,
              originator_id TEXT NOT NULL,
              opened_by TEXT NOT NULL,
              offer_type TEXT NOT NULL,
              terms TEXT DEFAULT '',
              status TEXT NOT NULL DEFAULT 'pending',
              created_at TEXT NOT NULL,
              resolved_at TEXT
            );
            """
        )
        _seed(conn)


def _seed(conn: sqlite3.Connection) -> None:
    for handle, roles in (
        ("pojo", ["originator", "admin"]),
        ("investor_demo", ["investor"]),
        ("voter_demo", ["voter"]),
        ("recycle_bot", ["bot"]),
    ):
        if not conn.execute("SELECT 1 FROM users WHERE handle = ?", (handle,)).fetchone():
            conn.execute(
                "INSERT INTO users (id, handle, roles, created_at) VALUES (?, ?, ?, ?)",
                (_id(), handle, json.dumps(roles), _now()),
            )

    if not conn.execute("SELECT 1 FROM boards WHERE slug = ?", ("round-1-starlink",)).fetchone():
        conn.execute(
            """
            INSERT INTO boards (
              id, slug, title, theme, window_start, window_end,
              score_types, rules, prizes, status
            ) VALUES (?, ?, ?, ?, NULL, NULL, ?, ?, ?, 'open')
            """,
            (
                _id(),
                "round-1-starlink",
                "Round 1 — Starlink / Orbital / Edge",
                "AI ideas using Starlink, orbital data, or edge compute for underserved areas.",
                json.dumps(["judge_panel", "vote", "popularity"]),
                json.dumps({"starlink_checkbox": True}),
                json.dumps(
                    {
                        "top_10_pct": "Featured on site",
                        "top_1_pct": "Backed or built (TBD)",
                        "vote_bonus": "Most creative callout",
                    }
                ),
            ),
        )


def get_user_by_handle(handle: str) -> Optional[dict]:
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE handle = ?", (handle,)).fetchone()
        return dict(row) if row else None


def ensure_user(handle: str, roles: Optional[list] = None) -> dict:
    existing = get_user_by_handle(handle)
    if existing:
        return existing
    with connect() as conn:
        conn.execute(
            "INSERT INTO users (id, handle, roles, created_at) VALUES (?, ?, ?, ?)",
            (_id(), handle, json.dumps(roles or ["originator"]), _now()),
        )
    user = get_user_by_handle(handle)
    assert user
    return user


def create_pitch(
    *,
    originator_id: str,
    title: str,
    problem: str,
    solution: str,
    why_now: str = "",
    starlink_flag: bool = False,
    status: str = "public",
    score_result: Optional[dict] = None,
) -> dict:
    pid = _id()
    now = _now()
    breakdown = json.dumps(score_result) if score_result else None
    nova = float(score_result["final_score"]) if score_result else None
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO pitches (
              id, originator_id, title, problem, solution, why_now, starlink_flag,
              status, nova_score, score_breakdown, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pid,
                originator_id,
                title.strip(),
                problem.strip(),
                solution.strip(),
                (why_now or "").strip(),
                1 if starlink_flag else 0,
                status,
                nova,
                breakdown,
                now,
                now,
            ),
        )
        if score_result:
            conn.execute(
                """
                INSERT INTO score_entries
                  (id, pitch_id, board_id, score_type, value, breakdown, source, created_at)
                VALUES (?, ?, NULL, 'judge_panel', ?, ?, 'scoring_pack', ?)
                """,
                (_id(), pid, float(score_result["final_score"]), breakdown, now),
            )
    pitch = get_pitch(pid)
    assert pitch
    return pitch


def get_pitch(pid: str) -> Optional[dict]:
    with connect() as conn:
        row = conn.execute("SELECT * FROM pitches WHERE id = ?", (pid,)).fetchone()
        if not row:
            return None
        pitch = dict(row)
        pitch["starlink_flag"] = bool(pitch["starlink_flag"])
        pitch["interest_count"] = conn.execute(
            "SELECT COUNT(*) AS c FROM interests WHERE pitch_id = ?", (pid,)
        ).fetchone()["c"]
        return pitch


def list_pitches(limit: int = 50) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT p.*,
              (SELECT COUNT(*) FROM interests i WHERE i.pitch_id = p.id) AS interest_count
            FROM pitches p
            WHERE p.status IN ('public', 'contest_only')
            ORDER BY COALESCE(p.nova_score, 0) DESC, p.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["starlink_flag"] = bool(d["starlink_flag"])
            out.append(d)
        return out


def add_interest(pitch_id: str, investor_id: str) -> dict:
    iid = _id()
    with connect() as conn:
        try:
            conn.execute(
                "INSERT INTO interests (id, pitch_id, investor_id, created_at) VALUES (?, ?, ?, ?)",
                (iid, pitch_id, investor_id, _now()),
            )
        except sqlite3.IntegrityError:
            row = conn.execute(
                "SELECT * FROM interests WHERE pitch_id = ? AND investor_id = ?",
                (pitch_id, investor_id),
            ).fetchone()
            return dict(row)
        return dict(conn.execute("SELECT * FROM interests WHERE id = ?", (iid,)).fetchone())


def create_permission_request(
    *,
    pitch_id: str,
    investor_id: str,
    originator_id: str,
    scope: str,
    message: str = "",
) -> dict:
    rid = _id()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO permission_requests
              (id, pitch_id, investor_id, originator_id, scope, message, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
            """,
            (rid, pitch_id, investor_id, originator_id, scope, message, _now()),
        )
        return dict(conn.execute("SELECT * FROM permission_requests WHERE id = ?", (rid,)).fetchone())


def list_permission_requests(originator_id: Optional[str] = None) -> list[dict]:
    with connect() as conn:
        if originator_id:
            rows = conn.execute(
                "SELECT * FROM permission_requests WHERE originator_id = ? ORDER BY created_at DESC",
                (originator_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM permission_requests ORDER BY created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]


def decide_permission(request_id: str, status: str) -> Optional[dict]:
    if status not in ("approved", "denied", "countered"):
        raise ValueError("status must be approved|denied|countered")
    with connect() as conn:
        conn.execute(
            "UPDATE permission_requests SET status = ?, decided_at = ? WHERE id = ?",
            (status, _now(), request_id),
        )
        row = conn.execute("SELECT * FROM permission_requests WHERE id = ?", (request_id,)).fetchone()
        return dict(row) if row else None


def list_boards() -> list[dict]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM boards ORDER BY title").fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["score_types"] = json.loads(d["score_types"])
            d["rules"] = json.loads(d["rules"])
            d["prizes"] = json.loads(d["prizes"])
            out.append(d)
        return out


def get_board_by_slug(slug: str) -> Optional[dict]:
    with connect() as conn:
        row = conn.execute("SELECT * FROM boards WHERE slug = ?", (slug,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["score_types"] = json.loads(d["score_types"])
        d["rules"] = json.loads(d["rules"])
        d["prizes"] = json.loads(d["prizes"])
        return d


def enroll_pitch(pitch_id: str, board_id: str) -> dict:
    with connect() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO board_enrollments (pitch_id, board_id, enrolled_at) VALUES (?, ?, ?)",
            (pitch_id, board_id, _now()),
        )
        pitch = conn.execute("SELECT * FROM pitches WHERE id = ?", (pitch_id,)).fetchone()
        if pitch and pitch["nova_score"] is not None:
            exists = conn.execute(
                """
                SELECT id FROM score_entries
                WHERE pitch_id = ? AND board_id = ? AND score_type = 'judge_panel'
                """,
                (pitch_id, board_id),
            ).fetchone()
            if not exists:
                conn.execute(
                    """
                    INSERT INTO score_entries
                      (id, pitch_id, board_id, score_type, value, breakdown, source, created_at)
                    VALUES (?, ?, ?, 'judge_panel', ?, ?, 'scoring_pack', ?)
                    """,
                    (_id(), pitch_id, board_id, float(pitch["nova_score"]), pitch["score_breakdown"], _now()),
                )
    return {"pitch_id": pitch_id, "board_id": board_id}


def board_leaderboard(slug: str, limit: int = 25) -> list[dict]:
    board = get_board_by_slug(slug)
    if not board:
        return []
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT p.id, p.title, p.starlink_flag, p.nova_score,
              COALESCE(se.value, p.nova_score, 0) AS board_score,
              (SELECT COUNT(*) FROM interests i WHERE i.pitch_id = p.id) AS interest_count
            FROM board_enrollments be
            JOIN pitches p ON p.id = be.pitch_id
            LEFT JOIN score_entries se
              ON se.pitch_id = p.id AND se.board_id = ? AND se.score_type = 'judge_panel'
            WHERE be.board_id = ?
            ORDER BY board_score DESC
            LIMIT ?
            """,
            (board["id"], board["id"], limit),
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["starlink_flag"] = bool(d["starlink_flag"])
            out.append(d)
        return out


def add_vote(pitch_id: str, board_id: str, value: float = 1.0) -> dict:
    sid = _id()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO score_entries
              (id, pitch_id, board_id, score_type, value, breakdown, source, created_at)
            VALUES (?, ?, ?, 'vote', ?, '{}', 'user', ?)
            """,
            (sid, pitch_id, board_id, value, _now()),
        )
    return {"id": sid, "pitch_id": pitch_id, "value": value}


def create_recycle_offer(
    *,
    pitch_id: str,
    originator_id: str,
    opened_by: str,
    offer_type: str = "credit",
    terms: str = "",
) -> dict:
    oid = _id()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO recycle_offers
              (id, pitch_id, originator_id, opened_by, offer_type, terms, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
            """,
            (oid, pitch_id, originator_id, opened_by, offer_type, terms, _now()),
        )
        return dict(conn.execute("SELECT * FROM recycle_offers WHERE id = ?", (oid,)).fetchone())


def decide_recycle_offer(offer_id: str, status: str) -> Optional[dict]:
    if status not in ("accepted", "declined", "negotiating"):
        raise ValueError("invalid status")
    with connect() as conn:
        conn.execute(
            "UPDATE recycle_offers SET status = ?, resolved_at = ? WHERE id = ?",
            (status, _now(), offer_id),
        )
        row = conn.execute("SELECT * FROM recycle_offers WHERE id = ?", (offer_id,)).fetchone()
        return dict(row) if row else None


def list_recycle_offers() -> list[dict]:
    with connect() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM recycle_offers ORDER BY created_at DESC")]


def cluster_similar(limit_scan: int = 100) -> list[dict]:
    pitches = list_pitches(limit=limit_scan)
    buckets: dict[str, list[str]] = {}
    keywords = ("starlink", "edge", "offline", "farm", "health", "school", "mesh", "satellite")
    for p in pitches:
        blob = f"{p['title']} {p['problem']} {p['solution']}".lower()
        for kw in keywords:
            if kw in blob:
                buckets.setdefault(kw, []).append(p["id"])
    clusters = []
    with connect() as conn:
        for label, ids in buckets.items():
            if len(ids) < 2:
                continue
            cid = _id()
            conn.execute(
                "INSERT INTO idea_clusters (id, label, pitch_ids, notes, created_at) VALUES (?, ?, ?, ?, ?)",
                (cid, label, json.dumps(ids), "auto-cluster by keyword", _now()),
            )
            clusters.append({"id": cid, "label": label, "pitch_ids": ids})
    return clusters


def public_pitch(p: dict) -> dict:
    breakdown = None
    raw = p.get("score_breakdown")
    if raw:
        try:
            breakdown = json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            breakdown = None
    return {
        "id": p["id"],
        "originator_id": p.get("originator_id"),
        "title": p["title"],
        "problem": p["problem"],
        "solution": p["solution"],
        "why_now": p.get("why_now") or "",
        "starlink_flag": bool(p.get("starlink_flag")),
        "status": p["status"],
        "nova_score": p.get("nova_score"),
        "interest_count": p.get("interest_count", 0),
        "score": breakdown,
        "created_at": p.get("created_at"),
    }
