"""Convert raw MediaPipe Holistic landmark results into plain, testable data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import mediapipe as mp

_mp_holistic = mp.solutions.holistic


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class PoseFrame:
    nose: Point
    left_shoulder: Point
    right_shoulder: Point
    left_elbow: Point
    right_elbow: Point
    left_wrist: Point
    right_wrist: Point
    left_ear: Point
    right_ear: Point
    left_eye: Point
    right_eye: Point
    mouth_left: Point
    mouth_right: Point


@dataclass(frozen=True)
class FrameDetections:
    pose: PoseFrame | None
    left_hand: Point | None
    right_hand: Point | None
    raw_pose_landmarks: Any = None


def _xy(landmark: Any, width: int, height: int) -> Point:
    return Point(landmark.x * width, landmark.y * height)


def extract_pose_frame(pose_landmarks: Any, width: int, height: int) -> PoseFrame | None:
    """Build a pixel-space PoseFrame from MediaPipe pose landmarks, or None if absent."""
    if pose_landmarks is None:
        return None
    lm = pose_landmarks.landmark
    pl = _mp_holistic.PoseLandmark
    return PoseFrame(
        nose=_xy(lm[pl.NOSE], width, height),
        left_shoulder=_xy(lm[pl.LEFT_SHOULDER], width, height),
        right_shoulder=_xy(lm[pl.RIGHT_SHOULDER], width, height),
        left_elbow=_xy(lm[pl.LEFT_ELBOW], width, height),
        right_elbow=_xy(lm[pl.RIGHT_ELBOW], width, height),
        left_wrist=_xy(lm[pl.LEFT_WRIST], width, height),
        right_wrist=_xy(lm[pl.RIGHT_WRIST], width, height),
        left_ear=_xy(lm[pl.LEFT_EAR], width, height),
        right_ear=_xy(lm[pl.RIGHT_EAR], width, height),
        left_eye=_xy(lm[pl.LEFT_EYE], width, height),
        right_eye=_xy(lm[pl.RIGHT_EYE], width, height),
        mouth_left=_xy(lm[pl.MOUTH_LEFT], width, height),
        mouth_right=_xy(lm[pl.MOUTH_RIGHT], width, height),
    )


def extract_hand_center(hand_landmarks: Any, width: int, height: int) -> Point | None:
    """Return a hand's reference point (middle finger MCP) in pixel space, or None if absent."""
    if hand_landmarks is None:
        return None
    lm = hand_landmarks.landmark
    hl = _mp_holistic.HandLandmark
    return _xy(lm[hl.MIDDLE_FINGER_MCP], width, height)
