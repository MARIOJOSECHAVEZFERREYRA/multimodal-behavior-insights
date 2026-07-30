"""Geometric rules for the full 40-item posture/gesture taxonomy (10 mid-term + 30 extended).

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


def shoulder_midpoint(pose: PoseFrame) -> Point:
    return midpoint(pose.left_shoulder, pose.right_shoulder)


def hip_width(pose: PoseFrame) -> float:
    return dist(pose.left_hip, pose.right_hip)


def hip_y(pose: PoseFrame) -> float:
    return (pose.left_hip.y + pose.right_hip.y) / 2


def hip_midpoint(pose: PoseFrame) -> Point:
    return midpoint(pose.left_hip, pose.right_hip)


def torso_height(pose: PoseFrame) -> float:
    return hip_y(pose) - shoulder_y(pose)


def ear_y(pose: PoseFrame) -> float:
    return (pose.left_ear.y + pose.right_ear.y) / 2


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


# --- Body posture (extended taxonomy) --------------------------------------------------


def _wrist_near_own_hip(pose: PoseFrame, side: str) -> bool:
    sw = shoulder_width(pose)
    if side == "left":
        return dist(pose.left_wrist, pose.left_hip) < sw * 0.35
    return dist(pose.right_wrist, pose.right_hip) < sw * 0.35


def is_shoulder_shrug(pose: PoseFrame) -> bool:
    return (shoulder_y(pose) - ear_y(pose)) < shoulder_width(pose) * 0.35


def is_uneven_shoulders(pose: PoseFrame) -> bool:
    return abs(pose.left_shoulder.y - pose.right_shoulder.y) > shoulder_width(pose) * 0.12


def is_arms_akimbo(pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    hips = hip_midpoint(pose)
    elbows_out = (
        abs(pose.left_elbow.x - hips.x) > sw * 0.55 and abs(pose.right_elbow.x - hips.x) > sw * 0.55
    )
    return _wrist_near_own_hip(pose, "left") and _wrist_near_own_hip(pose, "right") and elbows_out


def is_hand_on_hip_single(pose: PoseFrame) -> bool:
    left_only = _wrist_near_own_hip(pose, "left") and not _wrist_near_own_hip(pose, "right")
    right_only = _wrist_near_own_hip(pose, "right") and not _wrist_near_own_hip(pose, "left")
    return left_only or right_only


def is_hands_on_shoulders(pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    return (
        dist(pose.left_wrist, pose.right_shoulder) < sw * 0.3
        and dist(pose.right_wrist, pose.left_shoulder) < sw * 0.3
    )


def is_hand_on_chest(pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    shoulders = shoulder_midpoint(pose)
    chest = Point(shoulders.x, shoulder_y(pose) + torso_height(pose) * 0.2)
    return dist(pose.left_wrist, chest) < sw * 0.3 or dist(pose.right_wrist, chest) < sw * 0.3


def is_hand_on_stomach(pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    hips = hip_midpoint(pose)
    stomach = Point(hips.x, hip_y(pose) - torso_height(pose) * 0.2)
    return dist(pose.left_wrist, stomach) < sw * 0.3 or dist(pose.right_wrist, stomach) < sw * 0.3


def is_body_leaning_sideways(pose: PoseFrame) -> bool:
    shoulders = shoulder_midpoint(pose)
    hips = hip_midpoint(pose)
    return abs(shoulders.x - hips.x) > shoulder_width(pose) * 0.25


def is_arms_pinned(pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    elbows_tucked = (
        abs(pose.left_elbow.x - pose.left_shoulder.x) < sw * 0.25
        and abs(pose.right_elbow.x - pose.right_shoulder.x) < sw * 0.25
    )
    return (
        _wrist_near_own_hip(pose, "left") and _wrist_near_own_hip(pose, "right") and elbows_tucked
    )


def is_torso_turned(pose: PoseFrame) -> bool:
    return shoulder_width(pose) < hip_width(pose) * 0.75


def is_elbows_spread_wide(pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    elbows_out = (
        abs(pose.left_elbow.x - pose.left_shoulder.x) > sw * 0.6
        and abs(pose.right_elbow.x - pose.right_shoulder.x) > sw * 0.6
    )
    not_akimbo = not (_wrist_near_own_hip(pose, "left") and _wrist_near_own_hip(pose, "right"))
    return elbows_out and not_akimbo


def is_praying_hands(pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    sy = shoulder_y(pose)
    close_together = dist(pose.left_wrist, pose.right_wrist) < sw * 0.3
    at_chest_height = (
        sy <= pose.left_wrist.y <= sy + sw * 0.5 and sy <= pose.right_wrist.y <= sy + sw * 0.5
    )
    return close_together and at_chest_height


# --- Hand gestures (extended taxonomy) --------------------------------------------------


def is_touching_nose(hand: Point, pose: PoseFrame) -> bool:
    return dist(hand, pose.nose) < shoulder_width(pose) * 0.15


def is_covering_mouth(hand: Point, pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    mouth_center = midpoint(pose.mouth_left, pose.mouth_right)
    return dist(hand, mouth_center) < sw * 0.2


def is_touching_neck(hand: Point, pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    neck = Point(shoulder_midpoint(pose).x, (shoulder_y(pose) + ear_y(pose)) / 2)
    return dist(hand, neck) < sw * 0.25


def is_touching_forehead(hand: Point, pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    eye_midpoint = midpoint(pose.left_eye, pose.right_eye)
    forehead = Point(eye_midpoint.x, eye_midpoint.y - sw * 0.15)
    return dist(hand, forehead) < sw * 0.22


def is_touching_eye(hand: Point, pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    return min(dist(hand, pose.left_eye), dist(hand, pose.right_eye)) < sw * 0.15


def is_touching_cheek(hand: Point, pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    cheek_left = midpoint(pose.left_ear, pose.mouth_left)
    cheek_right = midpoint(pose.right_ear, pose.mouth_right)
    return min(dist(hand, cheek_left), dist(hand, cheek_right)) < sw * 0.2


def is_touching_collarbone(hand: Point, pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    collarbone = Point(shoulder_midpoint(pose).x, shoulder_y(pose))
    return dist(hand, collarbone) < sw * 0.25


def is_touching_temple(hand: Point, pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    eye_midpoint = midpoint(pose.left_eye, pose.right_eye)
    temple_left = Point(eye_midpoint.x - sw * 0.35, eye_midpoint.y)
    temple_right = Point(eye_midpoint.x + sw * 0.35, eye_midpoint.y)
    return min(dist(hand, temple_left), dist(hand, temple_right)) < sw * 0.2


def is_hand_raised(hand: Point, pose: PoseFrame) -> bool:
    return hand.y < ear_y(pose) - shoulder_width(pose) * 0.3


def is_pointing_gesture(hand: Point, pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    shoulders = shoulder_midpoint(pose)
    return abs(hand.x - shoulders.x) > sw * 1.3 and abs(hand.y - shoulder_y(pose)) < sw * 0.4


def is_rubbing_hands(
    left_hand: Point | None,
    right_hand: Point | None,
    prev_left: Point | None,
    prev_right: Point | None,
    pose: PoseFrame,
) -> bool:
    if left_hand is None or right_hand is None or prev_left is None or prev_right is None:
        return False
    sw = shoulder_width(pose)
    hands_close = dist(left_hand, right_hand) < sw * 0.35
    movement = dist(left_hand, prev_left) + dist(right_hand, prev_right)
    return hands_close and movement > sw * 0.25


def is_waving_hand(hand: Point, prev_hand: Point | None, pose: PoseFrame) -> bool:
    if prev_hand is None:
        return False
    sw = shoulder_width(pose)
    raised = hand.y < shoulder_y(pose) - sw * 0.2
    return raised and dist(hand, prev_hand) > sw * 0.3


# --- Head movement (extended taxonomy) --------------------------------------------------


def is_head_up(pose: PoseFrame) -> bool:
    return (shoulder_y(pose) - pose.nose.y) > shoulder_width(pose) * 0.85


def is_head_averted(pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    left_dx = abs(pose.left_ear.x - pose.nose.x)
    right_dx = abs(pose.right_ear.x - pose.nose.x)
    return abs(left_dx - right_dx) > sw * 0.25


def is_chin_tucked(pose: PoseFrame) -> bool:
    sw = shoulder_width(pose)
    drop = pose.nose.y - shoulder_y(pose)
    return sw * 0.02 < drop <= sw * 0.15


def is_head_nodding(pose: PoseFrame, prev_nose: Point | None) -> bool:
    if prev_nose is None:
        return False
    sw = shoulder_width(pose)
    dy = pose.nose.y - prev_nose.y
    dx = pose.nose.x - prev_nose.x
    return abs(dy) > sw * 0.12 and abs(dy) > abs(dx) * 1.5


def is_head_shaking(pose: PoseFrame, prev_nose: Point | None) -> bool:
    if prev_nose is None:
        return False
    sw = shoulder_width(pose)
    dy = pose.nose.y - prev_nose.y
    dx = pose.nose.x - prev_nose.x
    return abs(dx) > sw * 0.12 and abs(dx) > abs(dy) * 1.5


def is_head_recoil(pose: PoseFrame, prev_nose: Point | None) -> bool:
    if prev_nose is None:
        return False
    dy = prev_nose.y - pose.nose.y
    return dy > shoulder_width(pose) * 0.18
