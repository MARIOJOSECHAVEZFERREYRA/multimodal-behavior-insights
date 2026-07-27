"""Pure geometric helpers shared by the posture/gesture rules."""

from __future__ import annotations

import math

from src.detection.landmarks import Point


def dist(p1: Point, p2: Point) -> float:
    return math.hypot(p1.x - p2.x, p1.y - p2.y)


def midpoint(p1: Point, p2: Point) -> Point:
    return Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
