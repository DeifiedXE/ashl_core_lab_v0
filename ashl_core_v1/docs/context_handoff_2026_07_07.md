# ASHL Core v1 Context Handoff / 2026-07-07

This handoff captures the current repository state after Package 95. It is
intended for the next Codex/session after context loss.

## Current Repo State

- Workspace: `F:\Projects\ashl_core_lab_v0`
- Latest commit at handoff: `d50ffb6 Package 95 runtime continuous event loop`
- Git status at handoff creation: clean before this handoff file was added
- Latest full test result before this handoff: `py -3 -m unittest discover ashl_core_v1.tests` -> `2217 tests OK`
- Repo data pollution check before this handoff: `Test-Path ashl_core_v1\data` -> `False`

User communication preference:

- Completion reports should not include a next-package recommendation section.

## Current Safe Capability Summary

ASHL Core v1 has a bounded, teacher-gated path from reviewed-concept readback
through candidate ordering, selected action, final action, direct command,
deterministic sandbox execution, Sense observation, outcome evaluation, task
closure, learning feedback, feedback-derived concept refinement, feedback-derived
ReviewedConcept working readback, bounded replay, milestone audit, and bounded
runtime continuity records.

The system still does not have:

- autonomous scheduler authority
- open-ended live runtime loop
- background daemon
- free action selection
- external OS/network/filesystem execution
- Unity or bridge execution
- automatic learning approval
- Core / Long-term / Archive / Anchor memory writes
- Thought Engine cognition
- persistent cross-session growth

Important nuance:

- Package 85 introduced actual `direct_command` and deterministic sandbox
  execution records only inside the bounded sandbox path.
- Package 92 allows feedback-derived ReviewedConcept integration only into
  `working_readback`, not persistent memory layers.
- Package 95 introduced inert runtime continuity records, not a live runtime
  session.

## Package Spine

### Packages 66-80

Closed the advisory readback path:

`ReviewedConcept -> MemoryApplicationData -> TaskWorkingMemoryReadbackHint ->`
`future Task Working Memory advisory hint -> influence audit -> milestone audit`

The Package 80 milestone verified the advisory loop as complete, advisory-only,
single-task, future-task-initialization-only, visible, and inert.

Still blocked at that point:

- candidate ordering influence as actual behavior
- selected action
- final action
- direct command
- execution
- memory-layer write

### Packages 81-85

Opened a bounded teacher-gated action path:

1. Package 81: teacher-gated advisory readback influence may change actual
   candidate ordering in newly initialized Task Working Memory, with rollback
   and audit.
2. Package 82: teacher-gated selected_action proposal records can be created
   from the teacher-gated candidate ordering.
3. Package 83: teacher-gated actual `selected_action` can be applied from the
   selected_action proposal, with rollback and audit.
4. Package 84: teacher-gated actual `final_action` can be applied from
   selected_action, with rollback and audit.
5. Package 85: teacher-gated `final_action` can become `direct_command` and
   execute only inside a deterministic sandbox, with pre-execution snapshot,
   restore record, and audit.

Still blocked after Package 85:

- external execution
- OS command authority
- network / filesystem command authority
- Unity / bridge operation
- automatic learning approval
- memory-layer write

### Packages 86-90

Closed the first execution-to-learning-feedback intake path:

1. Package 86: Sense Interface can observe bounded sandbox execution and hand
   observation to Task Engine records.
2. Package 87: Task Engine can evaluate expected vs actual outcome from Sense
   observation.
3. Package 88: Task Engine can close a task from outcome evaluation.
4. Package 89: Learning Engine can create LearningFeedbackCandidate records
   from task closure.
5. Package 90: Learning Engine can create teacher-gated ConceptCandidate draft
   records from learning feedback.

See also:

- `ashl_core_v1/docs/package_81_90_repo_capability_log_v0.md`

### Packages 91-94

Closed the first action-to-feedback-derived-ReviewedConcept-to-next-task loop:

1. Package 91: feedback-derived ConceptCandidate drafts can be reviewed and
   refined with scope and counterexample checks.
2. Package 92: safe teacher-gated refined ConceptCandidate records can become
   feedback-derived ReviewedConcept records connected to `working_readback`.
3. Package 93: feedback-derived ReviewedConcept readback can be replayed in a
   bounded second task and audited.
4. Package 94: milestone audit seals the first bounded action-to-ReviewedConcept
   to next-task replay loop.

Still blocked after Package 94:

- autonomous learning
- recursive learning from replay
- free action selection
- external execution
- persistent memory promotion
- Thought Engine behavior

### Package 95

Added bounded runtime continuity records:

- `RuntimePowerWindowRecord`
- `RuntimeTickRecord`
- `RuntimeEventFrameRecord`
- `RuntimeEventStackRecord`
- `RuntimeEventReturnRecord`
- `RuntimeEventTreeRecord`
- `RuntimeContinuousLoopTrace`
- `RuntimeContinuousLoopAudit`

Timeline notation:

- space: power-off gap, no tick created
- `.`: idle heartbeat tick
- `1` to `9`: event depth tick
- `(` and `)`: visual notation only

Deterministic nested demo timeline:

```text
.......1(22222(333(4444)333)222222222)1
```

Package 95 does not start a live runtime session, background process,
autonomous scheduler, daemon, open-ended loop, external execution, memory write,
automatic learning approval, recursive learning, or production behavior.

## Key Files For Re-Entry

Package 95:

- `ashl_core_v1/runtime/continuous_event_loop.py`
- `ashl_core_v1/runtime/continuous_event_loop_cli.py`
- `ashl_core_v1/tests/test_continuous_event_loop.py`
- `ashl_core_v1/docs/runtime_continuous_event_loop_v0.md`

Recent loop/milestone docs:

- `ashl_core_v1/docs/package_81_90_repo_capability_log_v0.md`
- `ashl_core_v1/docs/learning_engine_feedback_concept_candidate_review_refinement_v0.md`
- `ashl_core_v1/docs/learning_engine_feedback_refined_concept_reviewed_readback_integration_v0.md`
- `ashl_core_v1/docs/feedback_reviewed_concept_closed_loop_replay_v0.md`
- `ashl_core_v1/docs/first_action_to_reviewed_concept_loop_milestone_v0.md`

Guided console integration:

- `ashl_core_v1/runtime/guided_cradle_growth_teacher_console.py`
- `ashl_core_v1/runtime/guided_cradle_growth_teacher_console_cli.py`
- `ashl_core_v1/runtime/__init__.py`

## Package 95 Verification Commands

Targeted:

```powershell
py -3 -m unittest ashl_core_v1.tests.test_continuous_event_loop
```

Adjacent regression:

```powershell
py -3 -m unittest ashl_core_v1.tests.test_first_action_to_reviewed_concept_loop_milestone
```

Full v1 discovery:

```powershell
py -3 -m unittest discover ashl_core_v1.tests
```

Diff hygiene:

```powershell
git diff --check
git diff --cached --check
```

Repo data pollution:

```powershell
Test-Path ashl_core_v1\data
```

Useful Package 95 CLI smoke checks:

```powershell
py -3 -m ashl_core_v1.runtime.continuous_event_loop_cli validate-demo-loop
py -3 -m ashl_core_v1.runtime.continuous_event_loop_cli show-demo-nested
py -3 -m ashl_core_v1.runtime.continuous_event_loop_cli show-demo-blocked --case invalid-depth-jump
py -3 -m ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli runtime-validate-continuous-event-loop-demo
```

## Known Context Notes

- Four older structure/alignment tests were updated during Package 95 to stop
  treating the string `RuntimeTick` as forbidden. The real forbidden boundary is
  now live runtime authority: no `RuntimeSession`, no `while True`, no
  `run_forever`.
- `ashl_core_v1/audit/first_action_to_reviewed_concept_loop_milestone.py`
  still contains a stale Package 94 readiness string naming an older intended
  Package 95 as "Bounded Multi-Trial Feedback Loop Planning". The actual latest
  Package 95 is `Runtime Continuous Event Loop And Nested Event Frame`. Do not
  let that stale string steer new work unless a future package explicitly asks
  to revise readiness wording.
- Do not modify old docs or root README unless explicitly requested.
- Do not create `ashl_core_v1/data`.
- Use `apply_patch` for manual file edits.

## Current Boundary Statement

The repo currently supports bounded teacher-gated records through deterministic
sandbox execution and feedback-derived readback replay, plus bounded runtime
continuity record modeling. It can demonstrate and audit these paths, but it is
not an autonomous agent runtime. It does not run an open-ended event loop, choose
freely, execute outside the deterministic sandbox, write persistent memory
layers, or approve learning automatically.
