"""Combine per-rule checks into the set of postures/gestures detected in a frame."""

from __future__ import annotations

from dataclasses import dataclass

from src.detection.landmarks import Point, PoseFrame
from src.taxonomy.rules import (
    is_arms_crossed,
    is_fidgeting,
    is_hand_behind_head,
    is_hand_on_chin,
    is_hands_clasped,
    is_head_down,
    is_head_tilted,
    is_open_arms,
    is_touching_ear,
    is_touching_hair,
)

_POSE_RULES = (
    ("arms_crossed", is_arms_crossed),
    ("open_arms", is_open_arms),
    ("hands_clasped", is_hands_clasped),
    ("head_down", is_head_down),
    ("head_tilted", is_head_tilted),
)

_HAND_RULES = (
    ("touching_ear", is_touching_ear),
    ("touching_hair", is_touching_hair),
    ("hand_on_chin", is_hand_on_chin),
    ("hand_behind_head", is_hand_behind_head),
)


@dataclass
class HandState:
    """Previous-frame hand positions, used to detect fidgeting movement between frames."""

    left: Point | None = None
    right: Point | None = None


def detect_postures(
    pose: PoseFrame | None,
    left_hand: Point | None,
    right_hand: Point | None,
    prev_hands: HandState,
) -> tuple[set[str], HandState]:
    """Evaluate all mid-term rules for one frame.

    Returns the set of detected posture/gesture labels and the updated hand-position state to
    pass into the next frame's call (needed for the fidgeting rule).
    """
    detected: set[str] = set()
    if pose is None:
        return detected, prev_hands

    for label, rule in _POSE_RULES:
        if rule(pose):
            detected.add(label)

    new_hands = HandState()
    for hand, prev, side in (
        (left_hand, prev_hands.left, "left"),
        (right_hand, prev_hands.right, "right"),
    ):
        if hand is None:
            setattr(new_hands, side, getattr(prev_hands, side))
            continue

        for label, rule in _HAND_RULES:
            if rule(hand, pose):
                detected.add(label)
        if is_fidgeting(hand, prev, pose):
            detected.add("fidgeting")

        setattr(new_hands, side, hand)

    return detected, new_hands
