# Active Perception Real Two-Cycle Growth Run v0

Status: Completed by Package 129

Package 129 proves one teacher-gated, cross-process growth loop using only
the perception capabilities already completed in Packages 125-128. It adds
no fifth perception action, sensor source, primitive compiler, focus mode, or
sufficiency-contract kind.

## Real Sequence

Both cycles use real screen and host-state capture. Audio and camera are
`not_participating_by_design`.

The exact persisted action sequence is:

1. `extend_observation_window`
2. `shift_internal_perception_focus`
3. `capture_again`
4. `stop_observation`

The parent starts with a 5-second base window, receives one bounded
1.5-second extension from actual temporal-tail evidence, and finalizes. A
Package 127 changed-grid candidate is selected deterministically. Package 126
opens one fresh same-plan child window, and Package 128 stops that child
before its 3-second hard deadline after the configured low-level closure and
post-context contract is satisfied.

Package 125 continues to preserve the same active capture sessions. Its
execution record now identifies the actual participating lanes, so the
Package 129 visual run records only `screen` and `host_state`; it does not
claim an audio deadline update.

## Teacher Gate

Cycle 1 persists an exact Package 117 evidence snapshot and stops at
`WAITING_TEACHER_REVIEW`. The snapshot contains source identities, low-level
visual and temporal evidence, all four action/execution identities, and
transport integrity. It excludes the stimulus schedule, expected focus cell,
expected stop point, raw sensor payload, and semantic claims.

Explicit approval requires:

`through_reviewed_concept_and_working_readback`

Approval follows the existing Package 90-92 path through ReviewedConcept,
MemoryLearningTrace, MemoryRoutingTrace, MemoryApplicationData, and one
working-readback commit. Reject and defer create none of those commits and
block Cycle 2.

## Cross-Process Influence

Cycle 2 runs in a different operating-system process with fresh runtime,
perception, window, capture-session, and raw-artifact identities. The approved
Cycle 1 readback is loaded before capture, candidate evaluation, action
scoring, and action execution.

The existing Package 112 scorer consumes the approved structural evidence at
the real `extend_observation_window` candidate hot path. The persisted
comparison records both the score without readback and the score with
readback. The contribution is advisory and nonzero; Package 125-128
authorization, integrity, lineage, and hard policy gates remain authoritative.

Cycle 2 completes the same four existing actions and again stops at
`WAITING_TEACHER_REVIEW`. It is not automatically approved and creates no
second memory commit.

## Boundaries

Package 129 creates no semantic vision, object recognition, auditory concept,
auditory prediction, uncertainty, novelty, curiosity, Thought Engine signal,
endocrine influence, Qingyin output, or external control. It imports no
D-Laplace runtime component and does not implement DLM-1.

Raw artifacts remain in the existing Package 120 external store. Package 129
stores only append-only wrappers, cycle identities, process receipts,
readback timing and influence, controls, comparison, and audit records under
the explicitly supplied external `state_dir`.

## CLI

Cycle 1 and Cycle 2 commands spawn isolated worker processes:

```text
py -3 -m ashl_core_v1.runtime.package_129_active_perception_growth_cli preflight --state-dir <path>
py -3 -m ashl_core_v1.runtime.package_129_active_perception_growth_cli run-cycle-1 --state-dir <path>
py -3 -m ashl_core_v1.runtime.package_129_active_perception_growth_cli show-cycle-1-review --state-dir <path>
py -3 -m ashl_core_v1.runtime.package_129_active_perception_growth_cli review-cycle-1 --state-dir <path> --decision approve --reviewer local_teacher --expected-evidence-identity <hash> --approval-scope through_reviewed_concept_and_working_readback --confirm
py -3 -m ashl_core_v1.runtime.package_129_active_perception_growth_cli run-cycle-2 --state-dir <path>
py -3 -m ashl_core_v1.runtime.package_129_active_perception_growth_cli show-readback-influence --state-dir <path>
py -3 -m ashl_core_v1.runtime.package_129_active_perception_growth_cli show-comparison --state-dir <path>
py -3 -m ashl_core_v1.runtime.package_129_active_perception_growth_cli audit --state-dir <path>
```

`guided-run` runs Cycle 1, prints the exact review command, and exits. It does
not approve Cycle 1 or keep a process alive for Cycle 2.

## Roadmap

Package 130, Grounded Auditory Event Concept Formation, is next. Package 131
adds bounded auditory predictive recognition, and Package 132 closes the
perception capability construction line. DLM-1 remains after Package 132.
