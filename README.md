# AI Tank

Pitch platform for AI ideas — **not** a trading product. Separate website, layout, and concept.

Investors can take **immediate interest** and request permissions. Contests run like **Speedrun Charts** (many boards). AI judges + Grok scoring ship as **one scoring pack**. Recycling bots resurface ideas only via credit / offers to the originator.

## Quick start

```bash
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

Optional live judging:

```bash
export XAI_API_KEY=your_key   # or GROK_API_KEY
python app.py
```

Without a key, the scoring pack uses a deterministic heuristic (same API shape).

## What's built

- `index.html` — pitch / browse / boards / permissions UI
- `app.py` — Flask API
- `db.py` — SQLite (`aitank.db`) for pitches, interests, permissions, boards, scores, recycle offers
- `scoring_pack.py` + `judge_engine.py` — one scoring unit (prompts from `judges.md`)
- Round 1 board seeded: `round-1-starlink`

## Docs

- [CONCEPT.md](CONCEPT.md)
- [CONTEST.md](CONTEST.md)
- [SCORING_PACK.md](SCORING_PACK.md)
- [docs/DATA_MODEL.md](docs/DATA_MODEL.md)

## API sketch

- `POST /api/pitches` — submit + score (+ optional Round 1 enroll)
- `GET /api/pitches` — list
- `POST /api/pitches/:id/interest`
- `POST /api/pitches/:id/permissions` / `POST /api/permissions/:id/decide`
- `GET /api/boards` / `GET /api/boards/:slug/leaderboard`
- `POST /api/pitches/:id/recycle-offer`

Repo: https://github.com/pojojimbob-debug/ai-tank
