"""Posture/gesture -> psychological meaning lookup.

Speculative, not clinically validated (see docs/DELIVERY_STANDARDS.md — Responsible Use).
Rationale/citations for each entry are tracked in issue #1 (docs/TAXONOMY.md).

Covers the full 40-item taxonomy: the 10 mid-term entries plus the 30 extended body
posture/hand gesture/head movement entries added in issue #10. Facial micro-expressions
remain out of scope (see docs/ARCHITECTURE.md — Modalities).
"""

from __future__ import annotations

POSTURE_MEANINGS: dict[str, str] = {
    # Mid-term (10)
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
    # Extended: body posture (11)
    "shoulder_shrug": "uncertainty or non-commitment",
    "uneven_shoulders": "tension or one-sided guardedness",
    "arms_akimbo": "assertiveness or impatience",
    "hand_on_hip_single": "casual defiance or impatience",
    "hands_on_shoulders": "self-soothing or seeking reassurance",
    "hand_on_chest": "sincerity or emotional appeal",
    "hand_on_stomach": "anxious self-protection",
    "body_leaning_sideways": "restlessness or discomfort",
    "arms_pinned": "nervous rigidity or closed-off tension",
    "torso_turned": "avoidance or disengagement",
    "elbows_spread_wide": "dominance or expansive confidence",
    # Extended: hand gestures (13)
    "touching_nose": "doubt or possible fabrication",
    "covering_mouth": "suppressed reaction or holding back words",
    "touching_neck": "insecurity or self-soothing under stress",
    "touching_forehead": "frustration or overwhelm",
    "touching_eye": "disbelief or fatigue",
    "touching_cheek": "evaluation or mild boredom",
    "touching_collarbone": "vulnerability or reassurance-seeking",
    "touching_temple": "stress or tension self-soothe",
    "hand_raised": "eagerness to interject or assert a point",
    "pointing_gesture": "emphasis or confrontation",
    "praying_hands": "pleading, hope, or contemplation",
    "rubbing_hands": "anticipation or nervous eagerness",
    "waving_hand": "greeting, farewell, or friendliness",
    # Extended: head movement (6)
    "head_up": "confidence, pride, or defiance",
    "head_averted": "avoidance or discomfort",
    "chin_tucked": "wariness or mild reserve",
    "head_nodding": "agreement or active listening",
    "head_shaking": "disagreement or refusal",
    "head_recoil": "surprise or aversion",
}
