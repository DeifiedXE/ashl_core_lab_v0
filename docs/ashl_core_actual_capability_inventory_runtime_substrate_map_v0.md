# ASHL Core Actual Capability Inventory / Runtime Substrate Map v0

Status: docs-only actual capability inventory.
Runtime impact: none.
Boundary Index impact: none.

This file records what the repository can actually run or produce after Boundary Index `2026-06-09-b188`.

It is a work-start reality check. It does not grant runtime authority and does not replace:

- `docs/current_boundary_index.md`
- `docs/phase0_status.md`
- `docs/phase0_capability_matrix.md`
- `docs/codex_working_context_summary.md`

## Scan Baseline

Repository scan baseline after the b188 ASHL Core structural refactor map package:

- tracked files: 819
- `ashl_core/*.py`: 292
- `tests/*.py`: 362
- top-level `docs/*.md`: 150
- smoke functions in `run_all_smoke_tests.py`: 428
- expected refreshed full smoke report: 428 / 428 passed

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
- b182 creates read-only thought, action, and memory lane indexes from b181 tick1 handoff records
- b183 closes Phase1 substrate construction and blocks duplicate Phase1 substrate packages
- b184 starts Phase2 with record-only perception/capability grounding entry reports from the closed Phase1 substrate
- b185 links those Phase2 evidence candidates to existing visual-spatial and Qingyin Bridge capability-map source references while preserving unresolved unknowns
- b186 corrects wait/probe operation labels so they are not forced into capability and are deferred to future Phase4 settling work
- b187 creates a docs-backed Phase2-to-Phase10 completed capability cross-check report to block duplicate rebuilds and design-only runtime claims
- b188 adds a structural refactor map and read-only checker for nine ASHL Core repository lines without moving files or changing imports

Session and working memory substrate:

- `ashl_core/session_working_memory.py` provides session-local state-action-outcome memory append, query, and clear helpers
- session working memory trial CLI paths can show records before clear and no records after clear
- b176 can create same-session temporary working-memory update records from the second-cycle sandbox outcome
- b179 can index the closed Phase0 loop as one ordered session trace spine
- b180 can materialize that spine into one record-only same-session frame with current tick, trace snapshot, temporary working-memory reference slots, and evidence source references
- b181 can read that frame as tick0 input and append one record-only tick1 frame while preserving working-memory and evidence references
- b182 can expose those preserved references as a read-only memory lane, alongside thought and action lanes
- b183 confirms those Phase1 records are present without creating runtime memory or action authority

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
- Phase1 tick1 three-line substrate index records
- Phase1 closure audit records
- Phase2 perception/capability grounding entry reports
- Phase2 perception/capability evidence source-link reports
- Phase2 grounding unknown classification correction reports
- Phase2-to-Phase10 completed capability cross-check reports
- ASHL Core structural refactor map reports
- smoke test report data

## Not Present Yet

ASHL Core does not yet have:

- a live Qingyin runtime session
- a session frame promoted to live runtime
- a tick handoff promoted to live runtime
- a three-line index promoted to candidate ordering or action selection
- Phase1 duplicate substrate packages after closure
- Phase2 candidate input or action preparation
- Phase2 semantic vision or grounded capability binding
- structural refactor execution, file moves, import changes, module merges, or compatibility aliases
- Phase6-Phase10 runtime claims backed by an authoritative plan
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

## Phase 2 Direction Correction

The next useful Phase1 engineering step should not be duplicate frame classification.

Current implemented step:

```text
Phase2 Perception Capability Evidence Source Link Minimal v0
```

Plain meaning:

Status:

Completed at Boundary Index `2026-06-09-b185`.

Reads b184 Phase2 entry reports and creates record-only source-link reports.

The reports link perception evidence candidates to existing visual-spatial grounding source references and capability evidence candidates to existing Qingyin Bridge capability-map source references where available. Unresolved items stay unknown.

It still must not:

- start a live runtime loop
- create candidate input or ordering
- create another duplicate Phase1 substrate package
- create a new action
- create semantic vision or object recognition
- create active focus or focus application
- create or mutate a capability map or raw tool access
- write persistent memory
- call external tools
- admit memory
- read or mutate predictors
- feed endocrine or tendency directly
- change production behavior
- claim learning or consciousness

Current implemented correction:

```text
Phase2 Grounding Unknown Classification Correction Minimal v0
```

Plain meaning:

Status:

Completed at Boundary Index `2026-06-09-b186`.

Reads b185 source-link reports and corrects two values:

- `wait_or_observe`
- `observe_or_alternative_probe`

These are marked as `not_capability_binding` and deferred to future Phase4 endocrine/tendency/settling work. This does not apply endocrine feed, tendency feed, or state settling.

Better next direction:

```text
Phase2 Grounding Source Availability Readback Minimal v0
```

Plain meaning:

Read the b187 cross-check, b186 correction report, and b185 source-link reports; summarize which evidence references are linked, still unresolved, or deferred to Phase4. Do not create semantic vision, capability bindings, endocrine/tendency feed, candidate input, action preparation, execution, memory writes, or learning/consciousness claims.

Current implemented cross-check:

```text
Phase2-to-Phase10 Completed Capability Cross-Check Minimal v0
```

Plain meaning:

Status:

Completed at Boundary Index `2026-06-09-b187`.

Reads the capability inventory, matrix, status, line index, boundary index, and growth plan. It lists completed work that must not be rebuilt, partial work that can only be extended, unfinished work that can enter roadmap, and design-only docs that cannot be treated as runtime.

It still must not:

- create candidate input or ordering
- create selected_action / final_action / direct command / execution
- create semantic vision, capability binding, or capability-map mutation
- write memory or retention
- feed endocrine or tendency
- claim production behavior, learning, or consciousness

Current implemented structural map:

```text
ASHL Core Structural Refactor Map Minimal v0
```

Plain meaning:

Status:

Completed at Boundary Index `2026-06-09-b188`.

Adds `docs/ashl_core_structural_refactor_map_v0.md` and a read-only CLI checker. It groups existing files into nine structural lines, lists completed do-not-rebuild anchors, partial extend-only anchors, duplicate/merge candidate families, archive candidates, and future folder suggestions.

It still must not:

- move files
- delete files
- rename modules
- change imports
- merge modules
- create runtime behavior
- create action selection or execution
- write memory or retention
- feed endocrine or tendency
- claim production behavior, learning, or consciousness
