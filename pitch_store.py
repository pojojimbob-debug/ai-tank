"""AI Tank — Pitch Store (scaffold)

In-memory store for now. Swap for SQLite / Postgres later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
import uuid

from judge_engine import Pitch, score_pitch


@dataclass
class StoredPitch:
    id: str
    pitch: Pitch
    nova_score: float
    judges: list = field(default_factory=list)
    judged: bool = False


class PitchStore:
    def __init__(self):
        self._pitches: dict[str, StoredPitch] = {}

    def submit(self, pitch: Pitch) -> StoredPitch:
        pid = str(uuid.uuid4())[:8]
        result = score_pitch(pitch)
        stored = StoredPitch(
            id=pid,
            pitch=pitch,
            nova_score=result["nova_score"],
            judges=result["judges"],
            judged=True,
        )
        self._pitches[pid] = stored
        return stored

    def leaderboard(self, limit: int = 10) -> List[StoredPitch]:
        return sorted(self._pitches.values(), key=lambda p: p.nova_score, reverse=True)[:limit]

    def get(self, pid: str) -> Optional[StoredPitch]:
        return self._pitches.get(pid)


store = PitchStore()


if __name__ == "__main__":
    store.submit(Pitch("Edge Sync", "Offline tools lose state", "Local-first log that syncs later"))
    store.submit(Pitch("Voice Farm", "Farmers can't type", "Voice AI for crop logs"))
    for p in store.leaderboard():
        print(p.id, p.nova_score, p.pitch.title)
