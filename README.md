# ASHL Core Lab v0

ASHL Core Lab v0.1 is a small Python project skeleton for testing an integrated ASHL Core loop.

This version only includes:

- Project structure cleanup
- Smoke runner
- Integrated Loop v0.1
- Decision priority correction
- `unittest` coverage

It does not connect a real LLM, web, tool system, GUI, TTS, Mood Layer, long-term database, or automatic memory solidification.

## Project Structure

```text
ashl_core/
  __init__.py
  perception.py
  concepts.py
  state_core.py
  thoughts.py
  deliberation.py
  expression.py
  guard.py
  integrated_loop.py

tests/
  test_smoke.py
  test_concepts.py
  test_state_core.py
  test_expression_guard.py
  test_deliberation.py
  test_integrated_loop.py

docs/
  research_plan.md

examples/
  core_sample.ashl

run_all_smoke_tests.py
```

## Windows PowerShell

Windows PowerShell should prefer `py -3`, not `python`.

Reason: `python` may point to the WindowsApps alias instead of the intended Python installation.

Common commands:

```powershell
py -3 run_all_smoke_tests.py
py -3 -m unittest discover
```

## Integrated Loop

The main API is:

```python
from ashl_core.integrated_loop import run_turn, run_script
```

Flow:

```text
input
-> perception
-> concept layer
-> state core
-> thoughts
-> deliberation
-> expression package
-> mock LLM
-> guard
-> final output + trace
```

`run_turn(text: str) -> dict` returns a trace containing:

- `input`
- `candidate_events`
- `concept_result`
- `state_result`
- `thoughts`
- `decision`
- `expression_package`
- `raw_output`
- `guard_result`
- `final_output`
