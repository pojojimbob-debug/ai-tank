"""AI Tank scoring pack — Grok + judge engine as ONE unit.

Public entry: score_pitch(pitch) -> dict
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

JUDGES_PATH = Path(__file__).resolve().parent / "judges.md"
STARLINK_BONUS = 1.15


@dataclass
class Pitch:
    title: str
    problem: str
    solution: str
    why: str = ""
    uses_starlink: bool = False


def _load_prompts() -> dict[str, str]:
    text = JUDGES_PATH.read_text(encoding="utf-8") if JUDGES_PATH.exists() else ""
    prompts = {
        "builder": "Score whether a small team could build this in 90 days.",
        "market": "Is this a real market or a toy? What is the wedge?",
        "impact": "How much does this move American AI innovation / underserved reach?",
    }
    for key, label in (("builder", "Builder"), ("market", "Market"), ("impact", "Impact")):
        m = re.search(rf"{label}.{{0,200}}?\"([^\"]{{20,}})\"", text, re.I | re.S)
        if m:
            prompts[key] = m.group(1)
    return prompts


def _clamp(n: float, lo: float = 0, hi: float = 100) -> float:
    return max(lo, min(hi, n))


def _heuristic(key: str, pitch: Pitch) -> tuple[float, str]:
    blob = f"{pitch.title} {pitch.problem} {pitch.solution} {pitch.why}".lower()
    words = len(re.findall(r"[a-z0-9]+", blob))
    base = _clamp(40 + min(words, 120) * 0.35)
    if key == "builder":
        hits = sum(1 for w in ("api", "model", "edge", "offline", "mvp", "stack", "prototype") if w in blob)
        return _clamp(base + hits * 4), "Feasibility heuristic"
    if key == "market":
        hits = sum(1 for w in ("market", "customer", "revenue", "wedge", "buyer", "price") if w in blob)
        return _clamp(base + hits * 5), "Market heuristic"
    hits = sum(
        1
        for w in ("rural", "underserved", "jobs", "school", "clinic", "farm", "remote", "starlink", "community")
        if w in blob
    )
    return _clamp(base + hits * 5 + (8 if pitch.uses_starlink else 0)), "Impact heuristic"


def _grok(pitch: Pitch, prompts: dict[str, str]) -> Optional[dict[str, tuple[float, str]]]:
    key = os.environ.get("XAI_API_KEY") or os.environ.get("GROK_API_KEY")
    if not key:
        return None
    body = {
        "model": os.environ.get("XAI_MODEL", "grok-2-latest"),
        "temperature": 0.3,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are the AI Tank judge panel. Return ONLY JSON keys builder, market, impact. "
                    'Each value: {"score":0-100,"rationale":"short"}.'
                ),
            },
            {"role": "user", "content": json.dumps({"pitch": asdict(pitch), "prompts": prompts})},
        ],
    }
    req = urllib.request.Request(
        "https://api.x.ai/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        content = payload["choices"][0]["message"]["content"]
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
        data = json.loads(content)
        return {
            k: (float(data[k]["score"]), str(data[k].get("rationale", "")))
            for k in ("builder", "market", "impact")
        }
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError, TypeError, ValueError):
        return None


def score_pitch(pitch: Pitch) -> dict:
    prompts = _load_prompts()
    names = {"builder": "The Builder", "market": "The Market Shark", "impact": "The Impact Judge"}
    grok = _grok(pitch, prompts)
    mode = "grok" if grok else "heuristic"
    judges = []
    total = 0.0
    for key in ("builder", "market", "impact"):
        score, rationale = grok[key] if grok else _heuristic(key, pitch)
        score = round(_clamp(score), 1)
        total += score
        judges.append(
            {
                "key": key,
                "judge": names[key],
                "score": score,
                "rationale": rationale,
                "prompt": prompts[key],
            }
        )
    nova = round(total / 3.0, 1)
    applied = bool(pitch.uses_starlink)
    final = round(nova * STARLINK_BONUS, 1) if applied else nova
    return {
        "builder": judges[0]["score"],
        "market": judges[1]["score"],
        "impact": judges[2]["score"],
        "nova_score": nova,
        "starlink_bonus": STARLINK_BONUS if applied else 0,
        "starlink_bonus_applied": applied,
        "final_score": final,
        "judges": judges,
        "mode": mode,
        "pitch": asdict(pitch),
    }
