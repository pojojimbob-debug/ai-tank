# AI Tank

Shark Tank for AI ideas. Website, not TV. AI judges, not a human panel.

Pitch your AI concept. Get scored by three judge personas. Nova Score hits the leaderboard.

Round 1 prize: featured on the board. No compute or hardware awards yet.

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000

1. Submit title / problem / solution / why now.
2. Check Starlink if the idea uses satellite or remote connectivity (15% Nova bonus).
3. Simulated judges score it. The live board updates.

Judges are still random ranges. Swap `score_pitch()` in `judge_engine.py` for a real LLM later.

## Status

Form is wired to `/api/pitch` and `/api/leaderboard`. Store is in-memory (board clears on restart).

Canonical repo: https://github.com/pojojimbob-debug/ai-tank
