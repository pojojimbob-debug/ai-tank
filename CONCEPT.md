# AI Tank — Platform Concept

**Source of truth for product design.** Separate site, layout, and concept from any trading products.

Shark Tank energy, website-native: people pitch AI ideas; **investors can act immediately**; contests and AI judges are optional layers, not the only door.

Primary wedge (v1 theme boards): **Starlink + AI / orbital / edge** for underserved areas — connectivity where the cloud can’t reach, local AI that syncs when the link comes up.

---

## North star

1. **Investor lane first** — interest and permission requests without waiting on a show, episode, or judge panel.
2. **Crowdsource + fund under the hood** — similar ideas, feedback, collaborators, and backing with clear provenance.
3. **Contests like Speedrun Charts** — many boards and score types in parallel, not one floor.
4. **Recycling bots** — rejected or discarded ideas get a second life via credit / offer to the originator.
5. **Scoring pack is one unit** — Grok API judging + `judge_engine.py` ship together (see [SCORING_PACK.md](SCORING_PACK.md)).

---

## Roles

| Role | What they do |
|------|----------------|
| **Originator** | Submits pitches; owns rights; approves permissions and recycle offers |
| **Investor** | Signals interest; requests permissions; may back / fund |
| **Voter / rater** | Community scoreboards (vote, rate, popularity) |
| **Bot** | Clusters similar ideas; resurfaces rejects; opens credit/offer flows |
| **Judge pack** | Builder / Market / Impact personas via Grok + Nova Score engine |

---

## Pillar 1 — Investor lane (priority)

Investors browse public pitch cards and can:

- **Interest** — soft signal (follow / interested). No originator approval required.
- **Permission request** — ask for contact, limited extra data, or right to evaluate further. **Originator must approve or deny.**
- **Back / fund** — when crowdfunding or deal terms exist (see Pillar 2).

Interest is first-class UX on every pitch, independent of contest placement or judge scores.

### Flow: interest → permission

```
Investor views pitch
  → Interest (logged)
  → Optional: PermissionRequest (contact | data | evaluate)
       → Originator notified
       → Approve / deny / counter
       → If approved: unlock scoped contact or data; audit trail kept
```

---

## Pillar 2 — Crowdsource / fund (under the hood)

- **Crowdsource:** similar-idea clusters, comments, collaborator asks, “build with me” flags.
- **Fund:** backing campaigns or soft commits tied to a pitch (terms TBD per campaign).
- **Provenance:** every pitch stores originator id, timestamps, license/terms, and status (`draft` | `public` | `contest_only` | `withdrawn` | `rejected` | `archived`).

Nothing is handed to a third party for reuse without an originator path when rights matter.

---

## Pillar 3 — Contest layer (Speedrun Charts model)

Not one show / one episode / one floor.

- Many **Boards** run in parallel (theme, time window, prize, score type).
- Same pitch can appear on multiple boards.
- Score types include: judge/Grok panel, community vote, rating, popularity/engagement, hybrids.

See [CONTEST.md](CONTEST.md) for board rules and Round 1 (Starlink / orbital / edge) as an example board.

---

## Pillar 4 — Idea recycling bots

Bots watch the vault of rejected, withdrawn, and low-ranked pitches plus public corpus:

1. Detect similarity or new fit (theme board, partner ask, another originator’s gap).
2. Open a **RecycleOffer** to the **originator** (credit, license, collab, buyout, attribution).
3. Originator accepts / declines / negotiates.
4. Only then may the idea be resurfaced, merged, or offered onward.

Never silent republish.

---

## Pillar 5 — Scoring pack (one unit)

Grok prompts in `judges.md` + `judge_engine.py` (Nova Score, Starlink bonus) are **one pack**. Flask (and later APIs) call the pack as a single entry point. Do not ship “random scores” and “Grok” as separate products.

Details: [SCORING_PACK.md](SCORING_PACK.md).

---

## Key product flows

| Flow | Summary |
|------|---------|
| Submit | Originator creates pitch → public or contest-eligible |
| Interest | Investor soft-signals without blocking |
| Permission | Scoped ask → originator decision → unlock |
| Board list | Pitch enrolled on one or more boards |
| Score | Scoring pack and/or community metrics write ScoreEntries |
| Recycle | Bot → RecycleOffer → credit/offer → optional resurface |

---

## Data model

Canonical entities: Pitch, Interest, PermissionRequest, Board, ScoreEntry, IdeaCluster, RecycleOffer, User.

See [docs/DATA_MODEL.md](docs/DATA_MODEL.md).

---

## What’s in the repo today (scaffold)

- Landing: `index.html`
- Flask: `app.py` (form not fully wired to engine yet)
- Judge personas: `judges.md` (Builder, Market, Impact)
- Engine: `judge_engine.py` (Nova Score + Starlink bonus)
- Store: `pitch_store.py` (in-memory)
- Docs: this file, `CONTEST.md`, `SCORING_PACK.md`, `docs/DATA_MODEL.md`

## Explicit non-goals (for now)

- No public posting from bots without Pojo approval
- No live deploy required for this concept pass
- No secrets / API keys in repo
- Not part of the trading desk UI or product

## Suggested build order (after concept sign-off)

1. Investor interest + permission UX + data model in storage
2. Multi-board schema + Round 1 board config
3. Wire Flask → scoring pack (Grok + engine) as one call
4. Persistence (SQLite prototype or Postgres)
5. Recycling bot MVP (cluster + RecycleOffer)
6. Round 1 prizes / rules polish
