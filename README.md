# AI Tank

Pitch platform for AI ideas — **not** a trading product. Separate website, layout, and concept.

Investors can take **immediate interest** and request permissions. Contests run like **Speedrun Charts** (many boards and score types). AI judges + Grok scoring ship as **one scoring pack**. Recycling bots can resurface rejected ideas only via credit / offer to the originator.

Wedge theme for early boards: Starlink + AI / orbital / edge for underserved areas.

## Read first

- [CONCEPT.md](CONCEPT.md) — platform source of truth
- [CONTEST.md](CONTEST.md) — multi-board contest model + Round 1
- [SCORING_PACK.md](SCORING_PACK.md) — Grok + judge engine as one unit
- [docs/DATA_MODEL.md](docs/DATA_MODEL.md) — entities and flows

## Core loop

1. Originator submits a pitch
2. Investors Interest / Permission-request (contest optional)
3. Pitches enroll on one or more boards
4. Scoring pack and/or community metrics write scores
5. Bots may open RecycleOffers on vaulted ideas

## Status

Scaffold: landing (`index.html`), Flask (`app.py`), personas (`judges.md`), engine (`judge_engine.py`), in-memory store (`pitch_store.py`). Concept docs expanded on branch `concept/platform-v1`.

Next build (after sign-off): wire form → scoring pack, persistence, investor permission UX, multi-board config.

## Run (local scaffold)

```bash
pip install -r requirements.txt
python app.py
```

Repo: https://github.com/pojojimbob-debug/ai-tank
