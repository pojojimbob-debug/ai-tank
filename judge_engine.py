"""AI Tank — Judge Engine (scaffold)

Simulates the three AI judges scoring a pitch.
Replace the score_pitch() body with a real LLM call later.
"""

import random
from dataclasses import dataclass, asdict


@dataclass
class Pitch:
    title: str
    problem: str
    solution: str
    why: str = ""


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
        "focus": "Jobs, underserved users, does this actually help people build?",
    },
}


def score_pitch(pitch: Pitch) -> dict:
    """Return Nova Score + per-judge breakdown.

    TODO: swap random for real LLM calls using the prompts in judges.md.
    """
    scores = []
    for key, meta in JUDGES.items():
        base = random.randint(55, 95)
        scores.append(JudgeScore(judge=meta["name"], score=base, rationale=f"{meta['focus']} (simulated)"))

    nova = sum(s.score for s in scores) / len(scores)

    return {
        "pitch": asdict(pitch),
        "nova_score": round(nova, 1),
        "judges": [asdict(s) for s in scores],
    }


if __name__ == "__main__":
    sample = Pitch(
        title="Farm Log Voice",
        problem="Field notes get lost when hands are dirty.",
        solution="Voice-to-structured crop logs on a phone.",
        why="Cheap phones are everywhere; typing in a field is not.",
    )
    import json
    print(json.dumps(score_pitch(sample), indent=2))
