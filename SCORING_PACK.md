# Scoring pack (Grok + judge engine) — one unit

Ship and call these together. Do not split “random placeholder scores” and “Grok judging” into separate products.

## Contents

| Piece | Role |
|-------|------|
| `judges.md` | Personas + prompts: Builder, Market, Impact |
| `judge_engine.py` | Aggregates judge scores → **Nova Score**; applies **Starlink bonus** |
| Grok (or compatible) API | Fills each persona score from pitch text using `judges.md` prompts |
| Flask / API entry | Single call: `score_pitch(pitch) → { judges, nova_score, starlink_bonus, breakdown }` |

## Contract (target)

```text
score_pitch(pitch) ->
  {
    "builder": 0-100,
    "market": 0-100,
    "impact": 0-100,
    "nova_score": float,          # average or engine rule
    "starlink_bonus": float,      # 0 if box unchecked / not eligible
    "final_score": float,         # nova + bonus (engine-defined)
    "raw": { ... }                # model traces for audit
  }
```

## Current scaffold status

- Personas and prompts live in `judges.md`.
- `judge_engine.py` implements Nova Score + Starlink bonus logic.
- Flask form is **not** fully wired; placeholder / random scoring may still exist — replace with this pack’s entry point.
- No API keys in repo. Use env vars locally when enabling live Grok.

## Wiring order

1. Expose one function/module entry used by `app.py`.
2. Swap any `alert()` / random path to `score_pitch`.
3. Persist ScoreEntry rows per Board (`judge_panel` type).
4. Keep community vote/rating on separate ScoreEntry types (not inside this pack).

## Non-goals

- This pack does **not** own Interest, PermissionRequest, or RecycleOffer.
- This pack does **not** replace multi-board contests; it feeds the `judge_panel` score type only.
