# AI Tank

Shark Tank for AI ideas. Website, not TV. AI judges, not a human panel.

Pitch a concept. Three judge personas score it. Nova Score hits the leaderboard.

Round 1 prize: featured on the board. Independent project — not affiliated with any hardware, satellite, or connectivity brand.

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000

Judges are still random ranges. Swap `score_pitch()` in `judge_engine.py` for a real LLM later.

Store is in-memory. Board clears on restart.

Canonical repo: https://github.com/pojojimbob-debug/ai-tank
