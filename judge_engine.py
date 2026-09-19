"""AI Tank judge engine — thin compatibility layer over the scoring pack.

Prefer: from scoring_pack import Pitch, score_pitch
"""

from scoring_pack import Pitch, score_pitch, STARLINK_BONUS, JUDGES_PATH

__all__ = ["Pitch", "score_pitch", "STARLINK_BONUS", "JUDGES_PATH"]


if __name__ == "__main__":
    import json

    sample = Pitch(
        title="Orbital Farm AI",
        problem="Rural farms lack real-time crop data.",
        solution="AI models on satellite imagery, delivered over Starlink.",
        why="Connectivity finally reached these acres.",
        uses_starlink=True,
    )
    print(json.dumps(score_pitch(sample), indent=2))
