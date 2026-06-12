# ASHL Core Phase0 Status

## Current Boundary Index

- Current version: `Boundary Index Version: 2026-06-09-b64`
- Current update log: Phase0 Documentation Consolidation Minimal v0
- This consolidation is documentation-only.

## Latest Completed Work

- Latest capability package before this consolidation: Level 1 Sandbox Lesson Application Outcome Observation Minimal v0.
- Latest capability boundary: ASHL Core can validate explicit user approval, apply one reviewed lesson inside the Phase0 Level 1 toy sandbox only, and observe that sandbox application outcome while preserving audit and rollback.

## Current Safe Capability

ASHL Core can observe the outcome of one reviewed lesson application inside the Phase0 Level 1 toy sandbox scope only, with explicit user approval, audit, and rollback, while production/runtime behavior, memory, retention, predictor mutation, action selection, and proof of learning remain blocked.

## Still Blocked

- Production lesson application.
- Runtime behavior change.
- Memory write or retained JSONL write.
- Retention write.
- Predictor mutation.
- `selected_action`, `final_action`, or direct command creation.
- Generalized behavior change.
- Production promotion.
- Proof of learning.

## Current Level 1 Sandbox Chain

```text
reviewed lesson evidence trace
-> sandbox application readiness
-> explicit user approval source validation
-> Level 1 sandbox application
-> Level 1 sandbox outcome observation
```

Outcome evaluation is planned next and is not marked complete.

## CLI Inventory

- `run-generic-lesson-evidence-pipeline-completion-bridge-minimal-check`
- `run-reviewed-lesson-sandbox-application-readiness-minimal-check`
- `run-level1-explicit-lesson-application-approval-minimal-check`
- `run-level1-sandbox-lesson-application-minimal-check`
- `run-level1-sandbox-lesson-application-outcome-observation-minimal-check`

These CLIs validate records and boundaries only. They do not authorize production behavior, memory writes, retention writes, predictor mutation, final actions, or proof claims.

## Test Status

- Last full smoke status before this consolidation package: `py -3 run_all_smoke_tests.py` PASS, all passed.
- Last full unittest status before this consolidation package: `py -3 -m unittest discover` PASS, Ran 2652 tests.

## Next Recommended Work

1. Level 1 Sandbox Lesson Application Outcome Evaluation Minimal v0.
2. Human review summary after outcome evaluation.
3. Keep Level 2, memory readiness, retention write, predictor mutation, runtime behavior change, and production lesson application blocked until separate boundary packages authorize them.
