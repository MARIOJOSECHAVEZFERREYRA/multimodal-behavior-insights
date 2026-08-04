# multimodal-behavior-insights

Psychological behavior analysis from video: multimodal pose/gesture/head/face signal
extraction mapped to a psychological-meaning taxonomy, synthesized into a narrative by an LLM.

> Heuristic course demo — not a clinically validated behavioral assessment tool.

## Project Logic

The pipeline runs in four deterministic-then-generative stages:

1. **Capture** (`src/capture/video.py`) — decodes the uploaded video and samples frames at a fixed interval.
2. **Detection** (`src/detection/`) — runs MediaPipe Holistic on each sampled frame to extract pose and hand landmarks.
3. **Taxonomy** (`src/taxonomy/`) — classifies landmarks into one of 40 posture/gesture labels using rule-based geometric checks (distances/angles relative to shoulder width, plus frame-to-frame motion for gestures like fidgeting or nodding). This stage is entirely deterministic — no AI/ML model is involved.
4. **Narrative** (`src/narrative/generator.py`) — aggregates the detected posture counts and hands them to an LLM (Google Gemini, `gemini-2.5-flash`) along with each posture's predefined psychological meaning. The model's only job is language synthesis: turning a list of labels into a coherent, readable paragraph — it does not detect, classify, or see the video itself.

The Streamlit UI (`app.py`) ties these stages together, rendering a posture-frequency chart, a timeline, the generated narrative, and a JSON export.

**Responsible use of the LLM:** the narrative prompt explicitly requires tentative language ("may suggest", "could indicate") rather than definitive claims, and the app is framed as a heuristic demo rather than a diagnostic tool. If the Gemini API call fails, generation falls back to a plain-text summary instead of failing silently or fabricating output.

## Documentation

- [docs/INDEX.md](docs/INDEX.md) — full documentation map
- [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) — local setup
- [CONTRIBUTING.md](CONTRIBUTING.md) — branch naming, commit format, coding standards
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — pipeline and module design
