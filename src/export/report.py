"""Build the downloadable JSON report shape."""

from __future__ import annotations

import json
from collections import Counter


def build_report(
    duration_sec: float,
    posture_counts: Counter,
    timeline: list[tuple[float, str]],
    narrative: str,
) -> dict:
    return {
        "video_duration_sec": duration_sec,
        "posture_counts": dict(posture_counts),
        "timeline": [{"time_sec": round(t, 1), "posture": p} for t, p in timeline],
        "narrative": narrative,
    }


def report_to_json(report: dict) -> str:
    return json.dumps(report, indent=2)
