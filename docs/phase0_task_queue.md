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
- Completed: Level 2 Sandbox Review Conclusion and Promotion Readiness Minimal v0.
- Completed: Level 3 Toy Minefield Multi-Step Sandbox Minimal v0.
- Completed: Level 3 Toy Minefield Variant Suite, Stability Evaluation, and Review Conclusion Minimal v0.
- Superseded: Sandbox-Stable Lesson Candidate Proposal Minimal v0.
- Completed: Bucket-Derived Lesson Candidate Signal Minimal v0.
- Deferred: Level 2 Sandbox Readiness Minimal v0.
- Deferred: Memory Readiness Boundary Minimal v0.

## Workflow Boundary

No task queue entry, completed task, passing test, Codex-generated status, workflow record, or queue ordering counts as explicit human application approval.

No Codex-generated review conclusion or Level 2 readiness precheck counts as explicit human application approval.

Package IDs track Codex work packages. Boundary Index Version tracks safety, permission, persistence, runtime, retention, predictor, sandbox execution, production, action-selection, approval-validation, or validation-boundary state. A completed task, CLI, smoke test, unittest, documentation update, or queue status update does not automatically increment Boundary Index.

The Level 2 sandbox application package changes Boundary Index because it moves Level 2 from dry-run-only into sandbox-only application. This is a sandbox application permission boundary change, not a package-completion counter.

The Level 2 sandbox review conclusion / promotion readiness package does not change Boundary Index because it records conclusion and future-design-only readiness without changing permission scope, runtime behavior, persistence, predictor, action-selection, or production boundaries.

The Level 3 toy minefield package changes Boundary Index because it introduces a new Level 3 sandbox-only multi-step application trace scope. This is not runtime execution, production promotion, memory write, predictor mutation, action selection, final_action, direct command, or proof of learning.

The Level 3 toy minefield variant stability package does not change Boundary Index because it operates inside the existing Level 3 sandbox-only multi-step trace boundary and adds deterministic variants, stability evaluation, and review conclusion only.

The bucket-derived lesson candidate signal package does not change Boundary Index because it records a structured repeated-pattern signal only. It does not generate lesson text, write memory, create retained JSONL, influence runtime behavior, mutate predictors, select actions, promote production behavior, or claim proof of learning.

The Codex task queue coordinates work packages only. It does not approve, apply, observe, evaluate, promote, remember, retain, predict, select, finalize, command, or prove learning.

Deferred future memory, predictor, runtime, sandbox, production, selected_action, final_action, and proof-of-learning items remain not implemented and not approved.
