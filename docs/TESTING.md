# Testing

## Test Types

| Scenario | Test type |
|----------|-----------|
| Geometric posture/gesture rule (e.g. `is_arms_crossed`) | Unit — fixture landmarks in, bool out |
| Taxonomy label → meaning lookup | Unit |
| Narrative prompt construction | Unit — assert prompt content, not LLM output |
| `generate_narrative()` with the OpenAI client | Unit — mock `client.chat.completions.create` |
| Full pipeline (video in → JSON report out) | Integration — use a short fixture video, optional |

## Structure

```
tests/
├── detection/
│   ├── test_pose_rules.py
│   ├── test_hand_rules.py
│   └── test_face_rules.py
├── taxonomy/
│   └── test_meanings.py
├── narrative/
│   └── test_generate_narrative.py
└── fixtures/
    └── landmarks.py        # helpers to build fake MediaPipe landmark objects
```

Mirror the `src/` layout under `tests/`.

## Fixture Pattern for Landmarks

MediaPipe landmark objects aren't trivial to construct by hand in tests. Use a small helper
that builds a fake landmark list from a dict of named points, e.g.:

```python
def make_pose_landmarks(overrides: dict[str, tuple[float, float]]) -> FakePoseLandmarks:
    """Build fake normalized pose landmarks for rule testing.

    overrides maps landmark name (e.g. "LEFT_WRIST") to (x, y) in 0-1 normalized space.
    Unspecified landmarks default to a neutral standing pose.
    """
```

This keeps rule tests readable — you only specify the coordinates relevant to the posture
under test, e.g. wrist/elbow positions for an `arms_crossed` test.

## Mocking the LLM

Never call the live OpenAI API in tests. Mock `client.chat.completions.create` and assert:
- The prompt includes the expected posture summary lines
- The function handles an API error gracefully (falls back instead of crashing)

```python
def test_generate_narrative_falls_back_on_api_error(monkeypatch):
    monkeypatch.setattr(client.chat.completions, "create", lambda **_: (_ for _ in ()).throw(RuntimeError("boom")))
    result = generate_narrative(Counter({"touching_ear": 3}), duration_sec=30)
    assert "touching ear" in result.lower()
```

## Running Tests

```bash
pytest                  # run all tests
pytest -k arms_crossed  # run tests matching a name
pytest --cov=src        # with coverage
```

## Coverage Expectations

This is a course-scale project — aim for meaningful coverage of the detection rules and
taxonomy mapping (the logic most likely to silently regress), not 100% line coverage on the
Streamlit UI code.
