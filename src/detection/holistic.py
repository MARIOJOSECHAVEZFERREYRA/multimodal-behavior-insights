"""Thin wrapper around MediaPipe Holistic for per-frame pose/hand detection."""

from __future__ import annotations

from typing import Any

import cv2
import mediapipe as mp

from src.detection.landmarks import FrameDetections, extract_hand_center, extract_pose_frame

_mp_holistic = mp.solutions.holistic


class HolisticDetector:
    """Wraps a single MediaPipe Holistic session across a video's frames.

    Mid-term scope: pose + hands only (see docs/ARCHITECTURE.md) — face landmarks from
    Holistic's internal model are not extracted or used here.
    """

    def __init__(self, model_complexity: int = 1) -> None:
        self._holistic = _mp_holistic.Holistic(
            static_image_mode=False, model_complexity=model_complexity
        )

    def process(self, frame_bgr: Any) -> FrameDetections:
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self._holistic.process(rgb)
        height, width = frame_bgr.shape[:2]
        return FrameDetections(
            pose=extract_pose_frame(results.pose_landmarks, width, height),
            left_hand=extract_hand_center(results.left_hand_landmarks, width, height),
            right_hand=extract_hand_center(results.right_hand_landmarks, width, height),
            raw_pose_landmarks=results.pose_landmarks,
        )

    def close(self) -> None:
        self._holistic.close()

    def __enter__(self) -> "HolisticDetector":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
