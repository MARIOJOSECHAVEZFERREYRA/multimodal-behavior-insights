# Getting Started

Get the project running locally.

## What is this project?

A Streamlit app that takes an uploaded interview/conversation video, extracts body posture,
hand gesture, head movement, and facial micro-expression signals with MediaPipe, maps them
against a psychological-meaning taxonomy, and uses an LLM to synthesize a narrative summary.
See [ARCHITECTURE.md](ARCHITECTURE.md) for the full pipeline.

**Disclaimer:** this is a heuristic, rule-based demo for course purposes — not a clinically
validated behavioral assessment tool.

## Prerequisites

- **Python 3.11+** (check with `python3 --version`)
- **pip** and **venv**
- **Git**
- An **OpenAI API key** (for narrative generation) — https://platform.openai.com/api-keys

## Step 1: Clone and Branch

```bash
git clone git@github.com:MARIOJOSECHAVEZFERREYRA/multimodal-behavior-insights.git
cd multimodal-behavior-insights
git checkout develop
git pull origin develop
```

## Step 2: Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
OPENAI_API_KEY=sk-your-key-here
```

Never commit `.env` — only `.env.example` (blank placeholder) is tracked.

## Step 5: Run the App

```bash
streamlit run app.py
```

Visit http://localhost:8501 and upload a short video (MP4/MOV/AVI) to test the pipeline.

## Step 6: Verify Your Setup

```bash
ruff check .        # Lint
black --check .     # Format check
pytest              # Test suite
```

## Project Structure

```
multimodal-behavior-insights/
├── app.py                  # Streamlit entrypoint
├── src/                    # Core pipeline modules (see ARCHITECTURE.md)
├── tests/                  # Test suite, mirrors src/
├── docs/                   # Documentation (you are here)
├── requirements.txt
├── .env.example
└── CONTRIBUTING.md
```

## Troubleshooting

### `mediapipe` fails to install
MediaPipe wheels lag behind the newest Python versions — if install fails, try Python 3.11
specifically rather than the latest 3.12/3.13.

### OpenCV can't open the uploaded video
Some MOV/AVI codecs aren't supported out of the box. Try re-exporting as H.264 MP4, or install
the system `ffmpeg` package.

### `OPENAI_API_KEY` not found
Confirm `.env` exists (not just `.env.example`) and that your shell/Streamlit process picks it
up — either via `python-dotenv` or Streamlit's `st.secrets`.

### Still stuck?
Open a GitHub issue with the error output and your OS/Python version.
