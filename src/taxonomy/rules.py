"""Geometric rules for the 10 mid-term postures/gestures.

Each rule is a pure function: pose/hand coordinates in, a bool out. Thresholds are expressed
as a fraction of shoulder width so they scale with the subject's distance from the camera.
See docs/ARCHITECTURE.md ("Known Limitations") — thresholds are tuned by eye, not calibrated
against a labeled dataset.
"""

from __future__ import annotations

from src.detection.landmarks import Point, PoseFrame
from src.taxonomy.geometry import dist, midpoint


def shoulder_width(pose: PoseFrame) -> float:
    return dist(pose.left_shoulder, pose.right_shoulder)


def shoulder_y(pose: PoseFrame) -> float:
    return (pose.left_shoulder.y + pose.right_shoulder.y) / 2


def is_arms_crossed(pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    wrists_near_opposite_elbows = (
        dist(pose.left_wrist, pose.right_elbow) < sw * 0.4
        and dist(pose.right_wrist, pose.left_elbow) < sw * 0.4
    )
    wrists_crossed_midline = (
        pose.left_wrist.x > pose.right_shoulder.x and pose.right_wrist.x < pose.left_shoulder.x
    )
    return wrists_near_opposite_elbows and wrists_crossed_midline


def is_open_arms(pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    sy = shoulder_y(pose)
    return (
        dist(pose.left_wrist, pose.right_wrist) > sw * 1.8
        and pose.left_wrist.y < sy
        and pose.right_wrist.y < sy
    )


def is_hands_clasped(pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    sy = shoulder_y(pose)
    return (
        dist(pose.left_wrist, pose.right_wrist) < sw * 0.3
        and pose.left_wrist.y > sy
        and pose.right_wrist.y > sy
    )


def is_head_down(pose: PoseFrame) -> bool:
    return pose.nose.y > shoulder_y(pose) + shoulder_width(pose) * 0.15


def is_head_tilted(pose: PoseFrame) -> bool:
    return abs(pose.left_ear.y - pose.right_ear.y) > shoulder_width(pose) * 0.15


def is_touching_ear(hand: Point, pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    return min(dist(hand, pose.left_ear), dist(hand, pose.right_ear)) < sw * 0.25


def is_touching_hair(hand: Point, pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    eye_midpoint = midpoint(pose.left_eye, pose.right_eye)
    forehead = Point(eye_midpoint.x, eye_midpoint.y - sw * 0.3)
    return dist(hand, forehead) < sw * 0.3


def is_hand_on_chin(hand: Point, pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    mouth_center = midpoint(pose.mouth_left, pose.mouth_right)
    return dist(hand, mouth_center) < sw * 0.25


def is_hand_behind_head(hand: Point, pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    ear_midpoint = midpoint(pose.left_ear, pose.right_ear)
    back_of_head = Point(ear_midpoint.x, ear_midpoint.y - sw * 0.1)
    return dist(hand, back_of_head) < sw * 0.3


def is_fidgeting(hand: Point, prev_hand: Point | None, pose: PoseFrame) -> bool:
    if prev_hand is None:
        return False
    return dist(hand, prev_hand) > shoulder_width(pose) * 0.35
