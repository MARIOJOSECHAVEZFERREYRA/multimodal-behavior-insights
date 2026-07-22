"""Posture/gesture -> psychological meaning lookup.

Speculative, not clinically validated (see docs/DELIVERY_STANDARDS.md — Responsible Use).
Rationale/citations for each entry are tracked in issue #1 (docs/TAXONOMY.md).
"""

from __future__ import annotations

POSTURE_MEANINGS: dict[str, str] = {
    "arms_crossed": "defensive or closed-off",
    "touching_ear": "boredom, reminiscence, or fabrication",
    "touching_hair": "anxiety or nervousness",
    "hand_on_chin": "deep thought or evaluation",
    "open_arms": "confidence, openness, or determination",
    "hands_clasped": "self-soothing or patience",
    "head_down": "submission, sadness, or defeat",
    "head_tilted": "curiosity or engagement",
    "hand_behind_head": "confidence or relaxation",
    "fidgeting": "restlessness or anxiety",
}
