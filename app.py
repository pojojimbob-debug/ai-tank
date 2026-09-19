"""AI Tank — Flask app.

Run:  python app.py
Then open http://localhost:5000
"""

from flask import Flask, request, jsonify

from judge_engine import Pitch
from pitch_store import store

app = Flask(__name__)


@app.route("/")
def home():
    with open("index.html", encoding="utf-8") as f:
        return f.read()


@app.route("/api/pitch", methods=["POST"])
def api_pitch():
    data = request.get_json(force=True) or {}
    title = (data.get("title") or "").strip()
    problem = (data.get("problem") or "").strip()
    solution = (data.get("solution") or "").strip()
    if not title or not problem or not solution:
        return jsonify({"error": "title, problem, and solution are required"}), 400
    pitch = Pitch(
        title=title,
        problem=problem,
        solution=solution,
        why=(data.get("why") or "").strip(),
        uses_starlink=bool(data.get("uses_starlink", False)),
    )
    stored = store.submit(pitch)
    return jsonify(
        {
            "id": stored.id,
            "nova_score": stored.nova_score,
            "judges": stored.judges,
            "starlink_bonus_applied": stored.starlink_bonus_applied,
        }
    )


@app.route("/api/leaderboard")
def api_leaderboard():
    return jsonify(
        [
            {
                "id": p.id,
                "title": p.pitch.title,
                "problem": p.pitch.problem,
                "solution": p.pitch.solution,
                "nova_score": p.nova_score,
                "starlink": p.pitch.uses_starlink,
                "judges": p.judges,
            }
            for p in store.leaderboard()
        ]
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
