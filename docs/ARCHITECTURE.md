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

| Modality | Source | Status |
|----------|--------|--------|
| Body posture | MediaPipe Pose landmarks | Implemented in sample (subset of rules) |
| Hand gestures | MediaPipe Hands landmarks | Implemented in sample (subset of rules) |
| Head movement | MediaPipe Pose (ear/nose landmarks) | Partial — only basic tilt/down detection |
| Facial micro-expressions | MediaPipe Face Landmarker | Not yet implemented |

## Taxonomy Scope

The case spec calls for a taxonomy of 40 postures/gestures with psychological meanings; the
sample implements 10. The final taxonomy size and how the remaining rules get authored
(manual geometric rules vs. a learned classifier) is an open scope decision — track it in a
GitHub issue before starting implementation so the taxonomy table and detection rules stay in
sync.

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
