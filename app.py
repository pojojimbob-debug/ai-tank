"""AI Tank — Flask app.

Run:  pip install -r requirements.txt && python app.py
Open: http://127.0.0.1:5000
"""

from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

import db
from scoring_pack import Pitch, score_pitch

app = Flask(__name__)
ROOT = Path(__file__).resolve().parent

db.init_db()


def err(msg: str, code: int = 400):
    return jsonify({"error": msg}), code


@app.get("/")
def home():
    return send_from_directory(ROOT, "index.html")


@app.post("/api/pitches")
def create_pitch():
    data = request.get_json(force=True) or {}
    title = (data.get("title") or "").strip()
    problem = (data.get("problem") or "").strip()
    solution = (data.get("solution") or "").strip()
    why_now = (data.get("why_now") or data.get("why") or "").strip()
    starlink = bool(data.get("starlink_flag") or data.get("uses_starlink"))
    handle = (data.get("handle") or "pojo").strip() or "pojo"
    enroll_round1 = bool(data.get("enroll_round1", True))

    if not title or not problem or not solution:
        return err("title, problem, and solution are required")

    user = db.ensure_user(handle, ["originator"])
    result = score_pitch(
        Pitch(
            title=title,
            problem=problem,
            solution=solution,
            why=why_now,
            uses_starlink=starlink,
        )
    )
    pitch = db.create_pitch(
        originator_id=user["id"],
        title=title,
        problem=problem,
        solution=solution,
        why_now=why_now,
        starlink_flag=starlink,
        score_result=result,
    )
    if enroll_round1:
        board = db.get_board_by_slug("round-1-starlink")
        if board:
            db.enroll_pitch(pitch["id"], board["id"])
    return jsonify(db.public_pitch(pitch)), 201


@app.get("/api/pitches")
def list_pitches():
    return jsonify([db.public_pitch(p) for p in db.list_pitches()])


@app.get("/api/pitches/<pid>")
def get_pitch(pid: str):
    pitch = db.get_pitch(pid)
    if not pitch:
        return err("pitch not found", 404)
    return jsonify(db.public_pitch(pitch))


@app.post("/api/pitches/<pid>/interest")
def interest(pid: str):
    pitch = db.get_pitch(pid)
    if not pitch:
        return err("pitch not found", 404)
    data = request.get_json(force=True) or {}
    handle = (data.get("handle") or "investor_demo").strip() or "investor_demo"
    investor = db.ensure_user(handle, ["investor"])
    row = db.add_interest(pid, investor["id"])
    return jsonify({"interest": row, "pitch": db.public_pitch(db.get_pitch(pid))})


@app.post("/api/pitches/<pid>/permissions")
def permission_request(pid: str):
    pitch = db.get_pitch(pid)
    if not pitch:
        return err("pitch not found", 404)
    data = request.get_json(force=True) or {}
    handle = (data.get("handle") or "investor_demo").strip() or "investor_demo"
    scope = (data.get("scope") or "contact").strip()
    if scope not in ("contact", "data", "evaluate"):
        return err("scope must be contact|data|evaluate")
    investor = db.ensure_user(handle, ["investor"])
    row = db.create_permission_request(
        pitch_id=pid,
        investor_id=investor["id"],
        originator_id=pitch["originator_id"],
        scope=scope,
        message=(data.get("message") or "").strip(),
    )
    return jsonify(row), 201


@app.get("/api/permissions")
def list_permissions():
    handle = request.args.get("originator")
    originator_id = None
    if handle:
        user = db.get_user_by_handle(handle)
        if not user:
            return jsonify([])
        originator_id = user["id"]
    return jsonify(db.list_permission_requests(originator_id))


@app.post("/api/permissions/<rid>/decide")
def decide_permission(rid: str):
    data = request.get_json(force=True) or {}
    status = (data.get("status") or "").strip()
    # UI may send approved/denied
    status = {"approved": "approved", "denied": "denied", "countered": "countered"}.get(status, status)
    try:
        row = db.decide_permission(rid, status)
    except ValueError as e:
        return err(str(e))
    if not row:
        return err("request not found", 404)
    return jsonify(row)


@app.get("/api/boards")
def boards():
    return jsonify(db.list_boards())


@app.post("/api/boards/<slug>/enroll")
def enroll(slug: str):
    board = db.get_board_by_slug(slug)
    if not board:
        return err("board not found", 404)
    data = request.get_json(force=True) or {}
    pitch_id = (data.get("pitch_id") or "").strip()
    if not pitch_id or not db.get_pitch(pitch_id):
        return err("valid pitch_id required")
    return jsonify(db.enroll_pitch(pitch_id, board["id"]))


@app.get("/api/boards/<slug>/leaderboard")
def leaderboard(slug: str):
    board = db.get_board_by_slug(slug)
    if not board:
        return err("board not found", 404)
    return jsonify({"board": board, "entries": db.board_leaderboard(slug)})


@app.post("/api/boards/<slug>/vote")
def vote(slug: str):
    board = db.get_board_by_slug(slug)
    if not board:
        return err("board not found", 404)
    data = request.get_json(force=True) or {}
    pitch_id = (data.get("pitch_id") or "").strip()
    if not pitch_id or not db.get_pitch(pitch_id):
        return err("valid pitch_id required")
    return jsonify(db.add_vote(pitch_id, board["id"], float(data.get("value", 1))))


@app.post("/api/pitches/<pid>/recycle-offer")
def recycle_offer(pid: str):
    pitch = db.get_pitch(pid)
    if not pitch:
        return err("pitch not found", 404)
    data = request.get_json(force=True) or {}
    bot = db.ensure_user("recycle_bot", ["bot"])
    row = db.create_recycle_offer(
        pitch_id=pid,
        originator_id=pitch["originator_id"],
        opened_by=bot["id"],
        offer_type=(data.get("offer_type") or "credit").strip(),
        terms=(data.get("terms") or "Credit + optional collab if reused later.").strip(),
    )
    return jsonify(row), 201


@app.post("/api/recycle-offers/<oid>/decide")
def decide_recycle(oid: str):
    data = request.get_json(force=True) or {}
    try:
        row = db.decide_recycle_offer(oid, (data.get("status") or "").strip())
    except ValueError as e:
        return err(str(e))
    if not row:
        return err("offer not found", 404)
    return jsonify(row)


@app.get("/api/recycle-offers")
def list_recycle():
    return jsonify(db.list_recycle_offers())


@app.post("/api/bots/cluster")
def cluster():
    return jsonify({"clusters": db.cluster_similar()})


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "service": "ai-tank"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
