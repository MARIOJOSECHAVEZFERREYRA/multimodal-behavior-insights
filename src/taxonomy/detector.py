"""Combine per-rule checks into the set of postures/gestures detected in a frame."""

from __future__ import annotations

from dataclasses import dataclass

from src.detection.landmarks import Point, PoseFrame
from src.taxonomy.rules import (
    is_arms_akimbo,
    is_arms_crossed,
    is_arms_pinned,
    is_body_leaning_sideways,
    is_chin_tucked,
    is_covering_mouth,
    is_elbows_spread_wide,
    is_fidgeting,
    is_hand_behind_head,
    is_hand_on_chest,
    is_hand_on_chin,
    is_hand_on_hip_single,
    is_hand_on_stomach,
    is_hand_raised,
    is_hands_clasped,
    is_hands_on_shoulders,
    is_head_averted,
    is_head_down,
    is_head_nodding,
    is_head_recoil,
    is_head_shaking,
    is_head_tilted,
    is_head_up,
    is_open_arms,
    is_pointing_gesture,
    is_praying_hands,
    is_rubbing_hands,
    is_shoulder_shrug,
    is_torso_turned,
    is_touching_cheek,
    is_touching_collarbone,
    is_touching_ear,
    is_touching_eye,
    is_touching_forehead,
    is_touching_hair,
    is_touching_neck,
    is_touching_nose,
    is_touching_temple,
    is_uneven_shoulders,
    is_waving_hand,
)

_POSE_RULES = (
    # Mid-term
    ("arms_crossed", is_arms_crossed),
    ("open_arms", is_open_arms),
    ("hands_clasped", is_hands_clasped),
    ("head_down", is_head_down),
    ("head_tilted", is_head_tilted),
    # Extended: body posture
    ("shoulder_shrug", is_shoulder_shrug),
    ("uneven_shoulders", is_uneven_shoulders),
    ("arms_akimbo", is_arms_akimbo),
    ("hand_on_hip_single", is_hand_on_hip_single),
    ("hands_on_shoulders", is_hands_on_shoulders),
    ("hand_on_chest", is_hand_on_chest),
    ("hand_on_stomach", is_hand_on_stomach),
    ("body_leaning_sideways", is_body_leaning_sideways),
    ("arms_pinned", is_arms_pinned),
    ("torso_turned", is_torso_turned),
    ("elbows_spread_wide", is_elbows_spread_wide),
    ("praying_hands", is_praying_hands),
    # Extended: head movement (static)
    ("head_up", is_head_up),
    ("head_averted", is_head_averted),
    ("chin_tucked", is_chin_tucked),
)

_HAND_RULES = (
    # Mid-term
    ("touching_ear", is_touching_ear),
    ("touching_hair", is_touching_hair),
    ("hand_on_chin", is_hand_on_chin),
    ("hand_behind_head", is_hand_behind_head),
    # Extended: hand gestures
    ("touching_nose", is_touching_nose),
    ("covering_mouth", is_covering_mouth),
    ("touching_neck", is_touching_neck),
    ("touching_forehead", is_touching_forehead),
    ("touching_eye", is_touching_eye),
    ("touching_cheek", is_touching_cheek),
    ("touching_collarbone", is_touching_collarbone),
    ("touching_temple", is_touching_temple),
    ("hand_raised", is_hand_raised),
    ("pointing_gesture", is_pointing_gesture),
)


@dataclass
class MotionState:
    """Previous-frame positions, used by rules that need motion between frames."""

    left_hand: Point | None = None
    right_hand: Point | None = None
    nose: Point | None = None


def detect_postures(
    pose: PoseFrame | None,
    left_hand: Point | None,
    right_hand: Point | None,
    prev_state: MotionState,
) -> tuple[set[str], MotionState]:
    """Evaluate all taxonomy rules for one frame.

    Returns the set of detected posture/gesture labels and the updated motion state to pass
    into the next frame's call (needed for fidgeting, rubbing_hands, waving_hand, and the
    head-movement rules).
    """
    detected: set[str] = set()
    if pose is None:
        return detected, prev_state

    for label, rule in _POSE_RULES:
        if rule(pose):
            detected.add(label)

    if is_head_nodding(pose, prev_state.nose):
        detected.add("head_nodding")
    if is_head_shaking(pose, prev_state.nose):
        detected.add("head_shaking")
    if is_head_recoil(pose, prev_state.nose):
        detected.add("head_recoil")

    if is_rubbing_hands(left_hand, right_hand, prev_state.left_hand, prev_state.right_hand, pose):
        detected.add("rubbing_hands")

    new_state = MotionState(nose=pose.nose)
    for hand, prev, side in (
        (left_hand, prev_state.left_hand, "left"),
        (right_hand, prev_state.right_hand, "right"),
    ):
        if hand is None:
            setattr(new_state, f"{side}_hand", getattr(prev_state, f"{side}_hand"))
            continue

        for label, rule in _HAND_RULES:
            if rule(hand, pose):
                detected.add(label)
        if is_fidgeting(hand, prev, pose):
            detected.add("fidgeting")
        if is_waving_hand(hand, prev, pose):
            detected.add("waving_hand")

        setattr(new_state, f"{side}_hand", hand)

    return detected, new_state
