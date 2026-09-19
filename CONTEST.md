# AI Tank Contests — Multi-board (Speedrun Charts style)

Contests are **boards**, not a single episode. Many boards can run at once. A pitch can sit on several boards and earn different scores on each.

Think **speedrun.com leaderboards**: categories, rulesets, and charts — not one show floor.

---

## Board model

Each **Board** has:

| Field | Meaning |
|-------|---------|
| `id` / `slug` | Stable id (e.g. `round-1-starlink`) |
| `title` | Human name |
| `theme` | Who should enter |
| `window` | Open / close times |
| `score_types` | One or more: `judge_panel`, `vote`, `rating`, `popularity`, `hybrid` |
| `rules` | Eligibility, Starlink checkbox, etc. |
| `prizes` | Featured, backed, compute, merch, etc. |
| `status` | `draft` \| `open` \| `closed` \| `archived` |

### Score types

- **judge_panel** — Scoring pack (Builder / Market / Impact via Grok + Nova Score + optional Starlink bonus).
- **vote** — Community up/down or ranked choice.
- **rating** — 1–5 or 0–100 quality ratings.
- **popularity** — Views, follows, interest signals, shares (define weights per board).
- **hybrid** — Weighted mix declared in board rules.

Same pitch → multiple **ScoreEntry** rows (one per board × score type as needed).

---

## Example board: Round 1 — Starlink / orbital / edge

### Theme
AI ideas that use **Starlink**, **orbital data**, or **edge compute** to reach people who never had the tools.

### How to enter
1. Open the site (or run locally).
2. Submit: title, problem, solution, why now.
3. Check the Starlink / connectivity box if it applies (feeds Starlink bonus in the scoring pack).
4. Enroll in board `round-1-starlink` (and any other open boards you want).

### Default score types for Round 1
- Primary: `judge_panel` (scoring pack)
- Secondary: `vote` (community creativity bonus)
- Optional later: `popularity`

### Prizes (proposed)
- Top 10% on judge board: featured on the site
- Top 1%: backed or built (compute / Starlink access TBD)
- Community vote bonus: most creative pitch callout

### Why this round
Contest = marketing. Every pitch is a reason for someone new to try AI — and investors can still Interest / Permission-request **outside** the board race.

---

## Relationship to investor lane

Boards do **not** gate investor Interest or PermissionRequest. A pitch can be cold on the charts and still get investor heat. A chart winner is not automatically sold — originator rights and permission flows still apply.

---

## Future boards (examples)

- `edge-offline-first` — no satellite required; sync-when-online
- `jobs-america` — Impact-heavy rubric
- `weekend-speedrun` — 48h submission window, vote-only
- `recycled-vault` — only pitches that accepted a RecycleOffer

Add boards by config, not by forking the site.
