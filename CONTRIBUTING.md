# Contributing to multimodal-behavior-insights

Guidelines for contributing to this project — a course demo that infers psychological
behavior signals from video using pose/gesture detection and LLM narrative synthesis.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [API Keys & Secrets](#api-keys--secrets)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Tracking](#issue-tracking)

## Code of Conduct

Be respectful and constructive in all interactions, including in code review comments.

## Getting Started

1. **Clone the repository**
2. **Set up the environment** — follow [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)
3. **Create a feature branch** from `develop`

## API Keys & Secrets

This project calls the OpenAI API to synthesize narratives. Never hardcode a key or use a
placeholder fallback like `st.secrets.get("OPENAI_API_KEY", "YOUR_KEY_HERE")` — if the key is
missing, fail loudly instead of silently running with a fake value.

- Store your key in `.env` (local, git-ignored) or Streamlit's `secrets.toml` (also git-ignored)
- Commit `.env.example` with a blank placeholder only
- Never commit a real token. If one is committed by accident, rotate it immediately.

## Development Workflow

### Branch Naming
- Use `<prefix>/<short-description>`, or `<prefix>/<issue-id>-<short-description>` when a
  GitHub issue exists
- Approved prefixes: `feature/`, `fix/`, `chore/`, `docs/`, `refactor/`, `test/`
- Examples: `feature/face-microexpression-detector`, `fix/17-hand-landmark-null-guard`,
  `docs/update-architecture`

### Local Development
1. Activate your virtualenv and run `streamlit run app.py` (see
   [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md))
2. Make your changes
3. Run `ruff check .`, `black --check .`, and `pytest` before opening a PR
4. Ensure all tests pass and linting is clean

## Coding Standards

### Architecture
Follow the module boundaries defined in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md):
- **Capture layer**: video/frame ingestion (OpenCV)
- **Detection layer**: MediaPipe pose/hand/face landmark extraction
- **Taxonomy layer**: mapping detected signals to the posture/gesture meaning table
- **Narrative layer**: LLM prompt construction and synthesis
- **UI layer**: Streamlit app wiring the above together

### Code Style
- Target Python 3.11+, use type hints on all function signatures
- Format with `black`, lint with `ruff`
- Use `snake_case` for functions/variables/modules, `PascalCase` for classes,
  `UPPER_SNAKE_CASE` for constants (e.g. `POSTURE_MEANINGS`)
- Prefer relative imports within the `src/` package
- Docstrings only where behavior isn't obvious from the name/signature (e.g. the geometric
  thresholds behind a posture rule) — don't restate what the code already says

### Naming Conventions (project-specific)
- Posture/gesture keys in the taxonomy are `snake_case` strings (e.g. `touching_ear`),
  matching the dict keys used for the LLM prompt and the JSON export
- New detection rules live next to the modality they belong to (pose, hand, head, face) —
  don't add unrelated detection logic to `app.py`

## Testing

- Write tests for new detection rules and taxonomy mappings
- Use `pytest`; place tests under `tests/`, mirroring the `src/` layout
- Mock MediaPipe landmark results with fixture objects — don't require a real camera or video
  file in unit tests
- Mock the OpenAI client in tests; never call the live API in CI
- See [docs/TESTING.md](docs/TESTING.md) for the full structure and fixture patterns

## Commit Guidelines

### Commit Message Format
```
type(scope): description

[optional body]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting only
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```
feat(taxonomy): add rule for steepled fingers

fix(hand-detection): guard against missing right_hand_landmarks

docs(readme): document OPENAI_API_KEY setup
```

## Pull Request Process

1. Ensure your branch is up to date with `develop`
2. Run `ruff check .`, `black --check .`, and `pytest` locally
3. Create a pull request targeting `develop` with a clear title and description
4. Reference any related issues
5. Address review feedback before merge

### PR Requirements
- All checks pass locally (lint, format, tests)
- Clear description of what changed and why
- Tests included for new detection rules or taxonomy entries
- Call out any known limitations (e.g. thresholds tuned on a specific camera framing)

If you're using Claude Code in this repository, the project-local `/to-pr` skill can walk the
PR workflow for you: it runs `ruff`/`black`/`pytest`, suggests a commit message following this
repo's single-line convention, targets `develop`, and opens a draft PR using
`.github/PULL_REQUEST_TEMPLATE.md`. It does not create commits or push branches.

## Issue Tracking

- Use GitHub Issues for bugs and feature ideas
- Reference the issue number in commits and PRs (`Fixes #12`)
- Keep the issue updated with progress if work spans multiple sessions

## Questions?

Check [docs/INDEX.md](docs/INDEX.md) for the full documentation map, or open an issue.
