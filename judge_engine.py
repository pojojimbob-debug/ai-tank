"""Compatibility shim — scoring_pack is the real engine."""

from scoring_pack import JUDGES_PATH, Pitch, STARLINK_BONUS, score_pitch

__all__ = ["Pitch", "score_pitch", "STARLINK_BONUS", "JUDGES_PATH"]
