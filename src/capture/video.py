"""Video frame sampling — decode frames and yield every Nth one with its timestamp."""

from __future__ import annotations

from collections.abc import Iterator

import cv2


def sampled_frames(
    video_path: str, every_n: int = 10
) -> Iterator[tuple[int, float, "cv2.typing.MatLike"]]:
    """Yield (frame_index, timestamp_sec, frame) for every Nth frame of the video."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    try:
        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % every_n == 0:
                yield frame_idx, frame_idx / fps, frame
            frame_idx += 1
    finally:
        cap.release()


def video_duration_sec(video_path: str) -> tuple[float, float]:
    """Return (duration_sec, fps) for the given video without decoding every frame."""
    cap = cv2.VideoCapture(video_path)
    try:
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return total_frames / fps, fps
    finally:
        cap.release()
