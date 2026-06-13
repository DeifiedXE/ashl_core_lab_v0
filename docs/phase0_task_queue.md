# Phase0 Task Queue

Current queue source:

- `ashl_core/codex_task_queue_minimal.py`
- CLI: `run-codex-task-queue-minimal-check`
- Versioning policy: `docs/phase0_versioning_policy.md`

## Current Entries

- Completed: Phase0 Documentation Inventory and Consistency Reconciliation Minimal v0.
- Active: Codex Task Queue Minimal v0.
- Completed: Level 1 Sandbox Outcome Evaluation and Human Review Summary Minimal v0.
- Completed: Level 1 Sandbox Review Conclusion and Level 2 Readiness Precheck Minimal v0.
- Completed: Level 2 Sandbox Design Envelope Minimal v0.
- Completed: Level 2 Sandbox Scenario Plan Minimal v0.
- Completed: Level 2 Sandbox Dry Run, Observation, Evaluation, and Human Review Summary Minimal v0.
- Completed: Phase0 Package ID and Boundary Index Version Separation Minimal v0.
- Completed: Level 2 Sandbox Application, Observation, Evaluation, and Human Review Summary Minimal v0.
- Deferred: Level 2 Sandbox Readiness Minimal v0.
- Deferred: Memory Readiness Boundary Minimal v0.

## Workflow Boundary

No task queue entry, completed task, passing test, Codex-generated status, workflow record, or queue ordering counts as explicit human application approval.

No Codex-generated review conclusion or Level 2 readiness precheck counts as explicit human application approval.

Package IDs track Codex work packages. Boundary Index Version tracks safety, permission, persistence, runtime, retention, predictor, sandbox execution, production, action-selection, approval-validation, or validation-boundary state. A completed task, CLI, smoke test, unittest, documentation update, or queue status update does not automatically increment Boundary Index.

The Level 2 sandbox application package changes Boundary Index because it moves Level 2 from dry-run-only into sandbox-only application. This is a sandbox application permission boundary change, not a package-completion counter.

The Codex task queue coordinates work packages only. It does not approve, apply, observe, evaluate, promote, remember, retain, predict, select, finalize, command, or prove learning.

Deferred future memory, predictor, runtime, sandbox, production, selected_action, final_action, and proof-of-learning items remain not implemented and not approved.
