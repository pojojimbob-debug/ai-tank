"""AI Tank — minimal Flask app (scaffold).

Run:  python app.py
Then open http://localhost:5000
"""

from flask import Flask, request, jsonify, render_template_string

from judge_engine import Pitch
from pitch_store import store

app = Flask(__name__)

INDEX = open("index.html").read() if False else None  # served as static for now


@app.route("/")
def home():
    return open("index.html").read()


@app.route("/api/pitch", methods=["POST"])
def api_pitch():
    data = request.get_json(force=True)
    pitch = Pitch(
        title=data.get("title", ""),
        problem=data.get("problem", ""),
        solution=data.get("solution", ""),
        why=data.get("why", ""),
        uses_starlink=bool(data.get("uses_starlink", False)),
    )
    stored = store.submit(pitch)
    return jsonify({"id": stored.id, "nova_score": stored.nova_score})


@app.route("/api/leaderboard")
def api_leaderboard():
    return jsonify([
        {"id": p.id, "title": p.pitch.title, "nova_score": p.nova_score, "starlink": p.pitch.uses_starlink}
        for p in store.leaderboard()
    ])


if __name__ == "__main__":
    app.run(debug=True, port=5000)