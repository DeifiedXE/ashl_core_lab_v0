# ASHL Core Actual Capability Inventory / Runtime Substrate Map v0

Status: docs-only actual capability inventory.
Runtime impact: none.
Boundary Index impact: none.

This file records what the repository can actually run or produce after Boundary Index `2026-06-09-b181`.

It is a work-start reality check. It does not grant runtime authority and does not replace:

- `docs/current_boundary_index.md`
- `docs/phase0_status.md`
- `docs/phase0_capability_matrix.md`
- `docs/codex_working_context_summary.md`

## Scan Baseline

Repository scan baseline after the b181 tick handoff package:

- tracked files: 803
- `ashl_core/*.py`: 285
- `tests/*.py`: 355
- top-level `docs/*.md`: 148
- smoke functions in `run_all_smoke_tests.py`: 421
- expected refreshed full smoke report: 421 / 421 passed

Important caveat:

`docs/phase0_doc_inventory.md` listed 129 documentation rows before this file was added. Later docs have moved faster than that inventory table, so the inventory is a navigation aid, not a complete fresh file count. This file is the current compact capability inventory, not a regenerated full documentation table.

## Capability Tiers

ASHL Core has several kinds of "can do".

1. Executable sandbox/helper capability:
   deterministic Python helpers and CLI paths can run inside local test scope.
2. Record/checker capability:
   modules can build and validate trace records, boundaries, audits, and summaries.
3. Controlled file helper capability:
   some helper paths can write JSON or JSONL only when explicitly called by tests or CLI.
4. Design-only capability:
   docs describe future architecture but do not make runtime behavior real.

The current Qingyin-safe capability is the boundary-constrained subset, not every helper function in the repo.

## Actual Executable Substrate

Core primitives:

- core seed and state helper surfaces exist
- body-state action sandbox helpers exist
- persistence helper modules exist
- fixed non-LLM first-output and mentor-feedback trace helpers exist

Action and sandbox substrate:

- deterministic body-state action transitions can produce `action_result`
- micro navigation trial runners can produce bounded traces and metrics
- micro push-box / tactile sandbox helpers can produce action history, outcome weighting, and local state-action comparisons
- same-session sandbox action-line records exist through candidate ordering, selected_action, final_action, direct_command, execution, outcome observation, feedback, application, reordering, and later selected action paths
- b170 through b178 create a bounded two-cycle thought/action/memory mini-loop as same-session sandbox record evidence
- b179 creates a record-only Phase1 session trace spine over that completed mini-loop
- b181 creates a same-session sandbox-only tick handoff from b180 frames, including tick1 context, appended frame, and tick0/tick1 continuity comparison

Session and working memory substrate:

- `ashl_core/session_working_memory.py` provides session-local state-action-outcome memory append, query, and clear helpers
- session working memory trial CLI paths can show records before clear and no records after clear
- b176 can create same-session temporary working-memory update records from the second-cycle sandbox outcome
- b179 can index the closed Phase0 loop as one ordered session trace spine
- b180 can materialize that spine into one record-only same-session frame with current tick, trace snapshot, temporary working-memory reference slots, and evidence source references
- b181 can read that frame as tick0 input and append one record-only tick1 frame while preserving working-memory and evidence references

Memory and retention substrate:

- memory layer helper files exist for Core / long-term / working / archive shaped storage
- reviewed lesson memory write/read minimal paths exist only inside their explicit controlled record scope
- mentor-gated retained JSONL append/read/list/exact-key style helpers exist inside their explicit scopes
- memory influence preview and reversible tendency influence checks exist only in controlled runners
- there is no unrestricted Qingyin long-term memory runtime

Lesson, review, and evidence substrate:

- failure events, lesson candidates, review gates, review decisions, dry-run application, evidence traces, and human-readable summaries have modules and tests
- these are evidence and review surfaces, not automatic learning authority

Vision, focus, and capability perception substrate:

- symbolic viewport and visual frame buffer record/checker paths exist
- visual frame change and focus candidate record paths exist
- Qingyin Bridge grounded capability map records can bind symbolic visible sandbox affordances to declared sandbox body capabilities
- semantic vision, object recognition, active focus authority, and raw tool authority are not present

Voice, audio, and output substrate:

- first-output helpers can produce fixed non-LLM output traces
- a fixed utterance map exists for small symbolic states
- voice, cochlea, vocal-organ, and internal auditory feedback docs are design-only unless a module and boundary say otherwise

Mimetic endocrine and state-settling substrate:

- endocrine-like traces and state-settling records exist as checked data surfaces
- they do not directly create purpose, select action, write memory, or prove emotion

Governance and audit substrate:

- Boundary Index, phase status, capability matrix, doc index, open risk ledger, task queue, smoke runner, and many boundary validators exist
- these keep claims honest, but passing a smoke test is not a proof of consciousness or production behavior

## Data ASHL Core Can Produce

Representative data shapes already produced by existing modules/tests include:

- `body_state`
- `action_result`
- `navigation_sandbox_trace`
- `tactile_sandbox_trace`
- `session_working_memory`
- `session_outcome_record`
- `experience_event`
- `lesson_candidate`
- review task / review decision / review trace records
- memory candidate, memory write, memory read, and retained experience records inside bounded scopes
- selected_action, final_action, direct_command, execution, and outcome_observation records inside sandbox scopes
- feedback evaluation, feedback application, and advisory reordering records inside sandbox scopes
- visual feature, visual frame, visual change, and focus candidate records
- grounded capability map records
- first_output_trace and mentor_feedback_trace
- mimetic endocrine / settling trace records
- Phase0 closure audit records
- Phase1 session trace spine records
- Phase1 same-session frame records
- Phase1 same-session runtime tick handoff records
- smoke test report data

## Not Present Yet

ASHL Core does not yet have:

- a live Qingyin runtime session
- a session frame promoted to live runtime
- a tick handoff promoted to live runtime
- a runtime tick scheduler
- automatic runtime ticks
- a persistent runtime session store
- an open-ended runtime action loop
- production action execution
- real UI or real-world tool operation as Qingyin behavior
- semantic vision or object recognition
- free-form runtime language generation
- LLM use inside Qingyin runtime
- unrestricted long-term memory growth
- automatic memory admission
- habit or skill anchor formation
- production predictor read, influence, or mutation
- direct endocrine or tendency authority over purpose/action
- proof of learning
- proof of consciousness or subjective experience

## Docs vs Code Corrections

Current docs are useful but uneven.

- `docs/current_boundary_index.md` is a compact current boundary pointer, not a full capability inventory.
- `docs/phase0_capability_matrix.md` is a milestone/status matrix, not an exhaustive map of all 285 core Python files.
- A previous scan found no broken references inside the capability matrix, but many core files are not directly named there.
- `docs/phase0_doc_inventory.md` is stale as a full file count; use it for navigation and authority classification, not exact coverage.
- A readback-only package after b179 would be redundant because b179 already returns and tests session trace spine records.

## Phase 1 Direction Correction

The next useful Phase1 engineering step should not be duplicate frame classification.

Current implemented step:

```text
Phase1 Session Frame Runtime Tick Handoff Minimal v0
```

Plain meaning:

Status:

Completed at Boundary Index `2026-06-09-b181`.

Reads the b180 frame as tick0 input, creates tick1 context, appends one record-only frame, and compares tick0/tick1 continuity.

It makes the same-session trace move one checked step forward without becoming a live runtime.

It still must not:

- start a live runtime loop
- create a new action
- write persistent memory
- call external tools
- admit memory
- read or mutate predictors
- feed endocrine or tendency directly
- change production behavior
- claim learning or consciousness

Better next direction:

```text
Phase1 Tick1 Context Sandbox Readback Minimal v0
```

Plain meaning:

Read the b181 tick1 context and report what the next sandbox tick is allowed to know, without selecting or executing an action.
