# Delivery Standards

Quality expectations for contributions to this repo. Every PR should meet these before merge.

## Code Quality

- [ ] `ruff check .` passes
- [ ] `black --check .` passes
- [ ] Type hints on new/changed function signatures
- [ ] No unused imports or dead code
- [ ] No `print()` debugging left in — use `st.write`/logging where output is actually needed
- [ ] Detection rules are pure functions (landmarks in, label out) — no Streamlit calls inside
      `taxonomy/` or `detection/`

## Testing

- [ ] New posture/gesture rules have a unit test with fixture landmark data
- [ ] LLM calls are mocked in tests — no live OpenAI calls in CI
- [ ] `pytest` passes locally
- See [TESTING.md](TESTING.md) for structure and fixture patterns

## Security & Secrets

- [ ] No API keys or tokens committed, including as a fallback default (e.g. never
      `st.secrets.get("OPENAI_API_KEY", "sk-...")`)
- [ ] `.env` stays git-ignored; only `.env.example` (blank) is tracked
- [ ] Uploaded video temp files are deleted after processing (`os.unlink` / `tempfile` cleanup)
- [ ] No sample/test videos containing real, identifiable people are committed to the repo

## Responsible Use (project-specific)

This project infers psychological states from body language — a domain where false
confidence causes real harm (HR screening, security screening are explicitly named use cases
in the project brief). Every PR touching the taxonomy or narrative layer should additionally
confirm:

- [ ] The UI/README/output still communicates that results are heuristic and not a clinical
      or forensic assessment
- [ ] New posture meanings avoid overstated claims (e.g. prefer "may suggest" over "indicates")
- [ ] No feature silently repurposes this as an identity/emotion-tracking tool without the
      uploader's awareness (this is a single-upload demo, not passive surveillance)

## Documentation

- [ ] Update [ARCHITECTURE.md](ARCHITECTURE.md) if module boundaries or the pipeline change
- [ ] Update the taxonomy table docs if posture/gesture entries are added or changed
- [ ] Update [GETTING_STARTED.md](GETTING_STARTED.md) if setup steps change

## PR Acceptance Criteria

A PR is ready to merge when:

- [ ] Lint, format, and tests pass
- [ ] Follows [../CONTRIBUTING.md](../CONTRIBUTING.md) coding standards
- [ ] Security and responsible-use checklists above are satisfied
- [ ] Relevant docs updated
- [ ] Known limitations called out in the PR description (e.g. "thresholds tuned on
      front-facing webcam footage only")
