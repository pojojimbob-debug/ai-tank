"""AI Tank — Judge Engine (scaffold)

Simulates the three AI judges scoring a pitch.
Replace the score_pitch() body with a real Grok / LLM call later.
"""

import random
from dataclasses import dataclass, asdict


@dataclass
class Pitch:
    title: str
    problem: str
    solution: str
    why: str = ""
    uses_starlink: bool = False


@dataclass
class JudgeScore:
    judge: str
    score: int
    rationale: str


JUDGES = {
    "builder": {
        "name": "The Builder",
        "focus": "Feasibility, tech stack, can it ship in 90 days?",
    },
    "market": {
        "name": "The Market Shark",
        "focus": "Market size, competition, why now.",
    },
    "impact": {
        "name": "The Impact Judge",
        "focus": "Jobs, underserved areas, sparks American AI creativity.",
    },
}

STARLINK_BONUS = 1.15  # 15% multiplier for connectivity-focused pitches


def score_pitch(pitch: Pitch) -> dict:
    """Return Nova Score + per-judge breakdown.

    TODO: swap random for real LLM calls using the prompts in judges.md.
    """
    scores = []
    for key, meta in JUDGES.items():
        base = random.randint(55, 95)
        scores.append(JudgeScore(judge=meta["name"], score=base, rationale=f"{meta['focus']} (simulated)"))

    nova = sum(s.score for s in scores) / len(scores)
    if pitch.uses_starlink:
        nova *= STARLINK_BONUS

    return {
        "pitch": asdict(pitch),
        "nova_score": round(nova, 1),
        "judges": [asdict(s) for s in scores],
        "starlink_bonus_applied": pitch.uses_starlink,
    }


if __name__ == "__main__":
    sample = Pitch(
        title="Orbital Farm AI",
        problem="Rural farms lack real-time crop data.",
        solution="AI models on satellite imagery, delivered over Starlink.",
        why="Starlink just reached these areas.",
        uses_starlink=True,
    )
    import json
    print(json.dumps(score_pitch(sample), indent=2))