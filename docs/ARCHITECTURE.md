# Architecture

## System Overview

The pipeline turns an uploaded video into a psychological narrative in four stages:

```
Video upload
     ↓
[1] Capture        — decode frames (OpenCV), sample every Nth frame
     ↓
[2] Detection       — MediaPipe landmark extraction: pose, hands, face
     ↓
[3] Taxonomy        — rule-based mapping from landmarks → posture/gesture labels
     ↓                  → each label carries a psychological meaning string
[4] Narrative        — aggregate label counts + timeline → LLM prompt → synthesized text
     ↓
Streamlit UI        — charts, timeline, narrative, JSON export
```

## Module Boundaries (target layout)

The original sample (`sample_code_HIITS.md`) is a single monolithic Streamlit script. The
target structure splits it by responsibility:

```
src/
├── capture/            # video → frame iterator
├── detection/           # MediaPipe wrappers: pose, hands, face landmarker
├── taxonomy/            # posture/gesture rules + meaning table
│   ├── rules.py         # geometric rule functions (one per posture/gesture)
│   └── meanings.py      # POSTURE_MEANINGS lookup table
├── narrative/            # LLM prompt construction + OpenAI client call
└── export/               # JSON report shape
app.py                   # Streamlit UI, wires the above together
```

Each detection rule should be a pure function taking landmark coordinates and returning a
bool/label, so it can be unit tested with fixture landmarks — no video or camera required.

## Modalities

| Modality | Source | Mid-term | Final deliverable |
|----------|--------|----------|--------------------|
| Body posture | MediaPipe Pose landmarks | In scope (subset of rules) | Extended rule set |
| Hand gestures | MediaPipe Hands landmarks | In scope (subset of rules) | Extended rule set |
| Head movement | MediaPipe Pose (ear/nose landmarks) | In scope (basic tilt/down) | Extended rule set |
| Facial micro-expressions | MediaPipe Face Landmarker | Out of scope | Required |

## Taxonomy Scope (confirmed with course reviewer, 2026-07-21)

The case spec calls for a taxonomy of 40 postures/gestures with psychological meanings. Scope
was confirmed in two phases:

**Mid-term:** 10 foundational postures/gestures, rule-based, no training data required:
`arms_crossed`, `touching_ear`, `touching_hair`, `hand_on_chin`, `open_arms`,
`hands_clasped`, `head_down`, `head_tilted`, `hand_behind_head`, `fidgeting` — this matches
the taxonomy already in the sample script.

**Final deliverable:** extend toward the full 40 via scenario-specific rules layered onto the
same geometric-rule approach (distances/angles between MediaPipe keypoints), plus facial
micro-expression detection (MediaPipe Face Landmarker) which is required for the final
submission but explicitly out of scope for mid-term.

## Classification Approach (confirmed)

Heuristic/rule-based classification using MediaPipe pose keypoint distances and angles —
no training data or ML model required. A trained ML classifier remains an acceptable
alternative per the course reviewer's guidance, but is not the current plan; revisit only if
the rule-based approach proves insufficient for the extended taxonomy.

## Dataset (confirmed)

No suitable public dataset exists for this task. The team records its own mock interview
videos (3–5 sessions, ~5 minutes each) to use as demo/test input. These are working data, not
committed to the repo (see [DELIVERY_STANDARDS.md](DELIVERY_STANDARDS.md)) — store them
locally or in a separate (non-git) location and reference them by path in local testing.

## Demo Format (confirmed)

A locally runnable Streamlit app is sufficient, accompanied by a pre-recorded demo video for
submission. Public deployment (e.g. Streamlit Community Cloud) is a stretch goal, attempted
only if time permits — not required for mid-term or final.

## Data Flow Detail

1. **Frame sampling**: process every Nth frame (configurable) to keep runtime manageable for
   demo-length videos.
2. **Landmark extraction**: MediaPipe returns normalized (0–1) coordinates per frame; convert
   to pixel space before computing distances.
3. **Rule evaluation**: each rule compares distances/angles between landmarks against
   thresholds derived from shoulder width (scale-invariant to camera distance).
4. **Aggregation**: detected labels accumulate into a `Counter` and a `(timestamp, label)`
   timeline across the video.
5. **Narrative synthesis**: aggregated counts + video duration are formatted into a prompt and
   sent to the LLM; the response is a short psychological profile, not a list of postures.
6. **Export**: counts, timeline, and narrative are serialized to a downloadable JSON report.

## Known Limitations (carried from the sample)

- Geometric thresholds are tuned by eye, not calibrated against a labeled dataset — expect
  false positives/negatives on different camera framings or body types.
- No face modality yet — head/face-driven meanings (e.g. brow furrow, eye contact avoidance)
  are out of scope until `detection/face.py` exists.
- Processing is synchronous and blocks the Streamlit thread for the whole video.
