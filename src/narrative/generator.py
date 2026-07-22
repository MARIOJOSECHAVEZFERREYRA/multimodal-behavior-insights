"""Aggregate detected postures into an LLM prompt and synthesize a narrative."""

from __future__ import annotations

import os
from collections import Counter

from openai import OpenAI

from src.taxonomy.meanings import POSTURE_MEANINGS

_DEFAULT_MODEL = "gpt-4o-mini"


def _client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key "
            "(see docs/GETTING_STARTED.md)."
        )
    return OpenAI(api_key=api_key)


def _summary_lines(posture_counts: Counter) -> list[str]:
    lines = []
    for posture, count in posture_counts.most_common():
        meaning = POSTURE_MEANINGS.get(posture, "unknown behavior")
        freq = "frequently" if count > 5 else "occasionally"
        lines.append(
            f"- {posture.replace('_', ' ').title()} ({freq}, ~{count} detections): "
            f"may suggest {meaning}"
        )
    return lines


def generate_narrative(
    posture_counts: Counter, duration_sec: float, client: OpenAI | None = None
) -> str:
    """Synthesize a short psychological narrative from aggregated posture counts.

    Falls back to a plain listing of detected postures if the LLM call fails, rather than
    crashing the whole pipeline over a transient API error.
    """
    if not posture_counts:
        return "No significant postural behaviors were detected in this video."

    lines = _summary_lines(posture_counts)
    prompt = (
        f"You are a behavioral psychology assistant analyzing a video of "
        f"{duration_sec:.0f} seconds.\n"
        f"The following postures were detected:\n{chr(10).join(lines)}\n\n"
        "Write a concise 3-4 sentence psychological profile of the subject. Be speculative "
        "but grounded in body language research. Do not list the postures again; synthesize "
        "them into a coherent narrative about the person's mental state. Use tentative "
        "language ('may suggest', 'could indicate') rather than definitive claims."
    )

    active_client = client or _client()
    try:
        response = active_client.chat.completions.create(
            model=_DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as exc:
        fallback = ", ".join(p.replace("_", " ") for p in posture_counts)
        return f"[LLM Error: {exc}] Fallback: The subject showed signs of {fallback}."
