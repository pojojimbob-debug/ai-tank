# AI Tank — Data model (concept)

Lightweight schema for implementation. Names can map to SQLite first, Postgres later.

## User

- `id`, `handle`, `roles[]` (`originator`, `investor`, `voter`, `admin`, `bot`)
- `contact` (private until permission grants)

## Pitch

- `id`, `originator_id`, `title`, `problem`, `solution`, `why_now`
- `starlink_flag` (bool)
- `status`: `draft` | `public` | `contest_only` | `withdrawn` | `rejected` | `archived`
- `license_terms` (text / enum)
- `created_at`, `updated_at`

## Interest

- `id`, `pitch_id`, `investor_id`, `created_at`
- Soft signal only; no originator approval required

## PermissionRequest

- `id`, `pitch_id`, `investor_id`, `originator_id`
- `scope`: `contact` | `data` | `evaluate`
- `message`, `status`: `pending` | `approved` | `denied` | `countered`
- `decided_at`

## Board

- `id`, `slug`, `title`, `theme`, `window_start`, `window_end`
- `score_types[]`, `rules` (JSON), `prizes` (JSON)
- `status`: `draft` | `open` | `closed` | `archived`

## BoardEnrollment

- `pitch_id`, `board_id`, `enrolled_at`

## ScoreEntry

- `id`, `pitch_id`, `board_id`
- `score_type`: `judge_panel` | `vote` | `rating` | `popularity` | `hybrid`
- `value` (float), `breakdown` (JSON — e.g. builder/market/impact)
- `source`: `scoring_pack` | `user_id` | `system`
- `created_at`

## IdeaCluster

- `id`, `label`, `pitch_ids[]`, `similarity_notes`
- Maintained by recycling bots

## RecycleOffer

- `id`, `pitch_id`, `originator_id`, `opened_by` (bot or user)
- `offer_type`: `credit` | `license` | `collab` | `buyout` | `attribution`
- `terms`, `status`: `pending` | `accepted` | `declined` | `negotiating`
- `created_at`, `resolved_at`

## Relationships (summary)

```
User 1—* Pitch
Pitch 1—* Interest
Pitch 1—* PermissionRequest
Pitch *—* Board (via BoardEnrollment)
Pitch 1—* ScoreEntry (per board / type)
Pitch *—* IdeaCluster
Pitch 1—* RecycleOffer
```

## Privacy rules

- Investor Interest is visible to originator (and optionally public count).
- PermissionRequest details stay private to parties until approved scopes unlock.
- RecycleOffer never publishes pitch content to a new context without acceptance.
