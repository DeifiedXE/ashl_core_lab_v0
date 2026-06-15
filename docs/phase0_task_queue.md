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
- Completed: ASHL Core / Qingyin Repo Audit Minimal v0.
- Completed: Bucket Signal Human Interpretation Review + Audit Reconciliation Minimal v0.
- Completed: Memory Readiness Design for Approved Bucket-Derived Lesson Minimal v0.
- Completed: Memory Admission Package Design Minimal v0.
- Completed: Memory Admission Approval Boundary Minimal v0.
- Completed: Memory Admission Minimal v0.
- Completed: Memory Write Approval Boundary Minimal v0.
- Superseded: Memory Write Minimal v0.
- Completed: Memory Write and Read Minimal v0.
- Completed: Memory Influence Preview Minimal v0.
- Completed: Memory Runtime Influence Approval Boundary Minimal v0.
- Completed: Memory Runtime Influence Minimal v0.
- Completed: Memory-Influenced Sandbox Re-run Minimal v0.
- Completed: Level 3 Toy Repair Multi-Step Sandbox Minimal v0.
- Completed: Memory-Influenced Toy Repair Re-run Minimal v0.
- Completed: Sandbox Behavior Use Minimal v0.
- Completed: Doubt Action Trace Minimal v0.
- Completed: Doubt-Gated Sandbox Candidate Ordering Minimal v0.
- Completed: Verification Candidate Registry + Trace Minimal v0.
- Deferred: Level 2 Sandbox Readiness Minimal v0.
- Deferred: Memory Readiness Boundary Minimal v0.

## Workflow Boundary

No task queue entry, completed task, passing test, Codex-generated status, workflow record, or queue ordering counts as explicit human application approval or memory write approval.

No Codex-generated review conclusion or Level 2 readiness precheck counts as explicit human application approval.

Package IDs track Codex work packages. Boundary Index Version tracks safety, permission, persistence, runtime, retention, predictor, sandbox execution, production, action-selection, approval-validation, or validation-boundary state. A completed task, CLI, smoke test, unittest, documentation update, or queue status update does not automatically increment Boundary Index.

The Level 2 sandbox application package changes Boundary Index because it moves Level 2 from dry-run-only into sandbox-only application. This is a sandbox application permission boundary change, not a package-completion counter.

The Level 2 sandbox review conclusion / promotion readiness package does not change Boundary Index because it records conclusion and future-design-only readiness without changing permission scope, runtime behavior, persistence, predictor, action-selection, or production boundaries.

The Level 3 toy minefield package changes Boundary Index because it introduces a new Level 3 sandbox-only multi-step application trace scope. This is not runtime execution, production promotion, memory write, predictor mutation, action selection, final_action, direct command, or proof of learning.

The Level 3 toy minefield variant stability package does not change Boundary Index because it operates inside the existing Level 3 sandbox-only multi-step trace boundary and adds deterministic variants, stability evaluation, and review conclusion only.

The bucket-derived lesson candidate signal package does not change Boundary Index because it records a structured repeated-pattern signal only. It does not generate lesson text, write memory, create retained JSONL, influence runtime behavior, mutate predictors, select actions, promote production behavior, or claim proof of learning.

The bucket signal human interpretation review package does not change Boundary Index because it records human or human/GPT-assisted interpretation and human review for future memory readiness design only. It does not make Qingyin the author of natural-language lesson text, write memory, create retained JSONL, influence runtime behavior, mutate predictors, select actions, promote production behavior, or claim proof of learning.

The memory readiness design package does not change Boundary Index because it records design-only constraints required before any future memory write. It does not admit memory, write memory, create retained JSONL, write retention, influence runtime behavior, mutate predictors, select actions, promote production behavior, or claim proof of learning.

The memory admission package design does not change Boundary Index because it records a design-only future package contract. It does not admit memory, write memory, create retained JSONL, write retention, choose Long-term/Core Memory now, allow cross-session influence rebuild, influence runtime behavior, mutate predictors, select actions, promote production behavior, or claim proof of learning.

Memory Admission Approval Boundary Minimal v0 changes Boundary Index from b74 to b75 because it introduces an explicit human approval validation boundary for future memory admission packages. The approval only allows a separate future memory admission package to proceed; it does not admit memory, write memory or retained JSONL, influence runtime behavior, mutate predictors, select actions, promote production behavior, or prove learning.

Memory Admission Minimal v0 changes Boundary Index from b75 to b76 because it opens the minimal memory admission boundary for reviewed_lesson_memory_candidate records. This is candidate-layer admission only; it does not write Long-term/Core/Archive Memory, append retained JSONL, influence runtime behavior, mutate predictors, select actions, promote production behavior, or prove learning.

Memory Write Approval Boundary Minimal v0 changes Boundary Index from b76 to b77 because it introduces an explicit human approval validation boundary for future memory write packages. This approval does not write memory, write retained JSONL, write retention, influence runtime behavior, mutate predictors, select actions, promote production behavior, or prove learning.

Memory Write and Read Minimal v0 changes Boundary Index from b77 to b78 because it opens the minimal memory write and controlled memory read boundary for one approved reviewed_lesson_memory_candidate. It writes a minimal reviewed lesson memory record and reads the stored text through a controlled read path only; it does not write retained JSONL/data JSONL, write retention, enable runtime influence, provide predictor input, mutate predictors, select actions, promote production behavior, or prove learning.

Memory Influence Preview Minimal v0 changes Boundary Index from b78 to b79 because it introduces a preview-only memory influence validation boundary from controlled memory read. The preview may state that the memory would favor check_before_retry in a future influence design, but it does not enable runtime influence, provide predictor input, mutate predictors, select actions, write retained JSONL, write retention, promote production behavior, or prove learning.

Memory Runtime Influence Approval Boundary Minimal v0 changes Boundary Index from b79 to b80 because it introduces explicit human approval validation for future memory runtime influence packages. The approved decision only allows a separate future package to proceed; it does not perform runtime influence, mutate predictors, create selected_action or final_action, select actions, write retained JSONL, write retention, promote production behavior, or prove learning.

Memory Runtime Influence Minimal v0 changes Boundary Index from b80 to b81 because it opens the minimal bounded memory runtime influence boundary for one approved memory record inside a deterministic controlled runner. It applies a small tendency score shift and rolls it back to baseline; it does not create selected_action, final_action, direct command, predictor mutation, retained JSONL write, retention write, production promotion, or proof of learning.

Memory-Influenced Sandbox Re-run Minimal v0 changes Boundary Index from b81 to b82 because it introduces memory-influenced Level 3 sandbox re-run tendency traces using the approved bounded runtime influence. It compares memory_off, memory_on, and rollback traces across deterministic Level 3 toy minefield variants; it does not create selected_action, final_action, direct command, predictor mutation, retained JSONL write, retention write, production promotion, or proof of learning.

Level 3 Toy Repair Multi-Step Sandbox Minimal v0 changes Boundary Index from b82 to b83 because it introduces a second deterministic Phase0 Level 3 sandbox-only multi-step scenario family. It blocks repeating the same failed quick repair without inspection, observes `inspect_device` before `attempt_safe_repair`, and does not create memory runtime influence, selected_action, final_action, direct command, predictor mutation, retained JSONL write, retention write, production behavior, autonomous learning/action, or proof of learning.

Memory-Influenced Toy Repair Re-run Minimal v0 changes Boundary Index from b83 to b84 because it introduces memory-influenced Level 3 toy repair sandbox re-run tendency traces using the approved bounded runtime influence. It compares memory_off, memory_on, and rollback traces across deterministic toy repair contexts; it does not create selected_action, final_action, direct command, predictor read/influence/mutation, retained JSONL write, retention write, production promotion, or proof of learning.

Sandbox Behavior Use Minimal v0 changes Boundary Index from b84 to b85 because it permits approved memory-influenced tendency to affect sandbox-only candidate action ordering. It ranks `check_before_retry` above `retry_same_action_without_check` as advisory sandbox-only ordering; it does not create selected_action, final_action, direct command, predictor read/influence/mutation, production behavior, retained JSONL write, retention write, autonomous learning/action, or proof of learning.

Doubt Action Trace Minimal v0 changes Boundary Index from b85 to b86 because it introduces a trace-only doubt_action validation boundary: expected/actual mismatch may raise doubt_score, lower direct retry weight, and propose a low-risk verification candidate. It does not execute verification, create selected_action, final_action, direct command, persistent rule, memory write, retention write, predictor mutation, production behavior, autonomous learning/action, or proof of learning.

Doubt-Gated Sandbox Candidate Ordering Minimal v0 changes Boundary Index from b86 to b87 because it permits trace-only doubt_action output to influence sandbox-only candidate action ordering. It ranks low-risk verification and check_before_retry before direct retry after expected/actual mismatch; it does not execute verification, create selected_action, final_action, direct command, persistent rule, memory write, retention write, predictor mutation, production behavior, autonomous learning/action, or proof of learning.

Verification Candidate Registry + Trace Minimal v0 changes Boundary Index from b87 to b88 because it introduces a validation boundary for named low-risk verification candidates. Doubt-gated sandbox ordering may reference only registered trace-only candidates; this does not execute verification, create selected_action, final_action, direct command, persistent rule, memory write, retention write, predictor mutation, production behavior, autonomous learning/action, or proof of learning.

The Codex task queue coordinates work packages only. It does not approve, apply, observe, evaluate, promote, remember, retain, predict, select, finalize, command, or prove learning.

Deferred future memory, predictor, runtime, sandbox, production, selected_action, final_action, and proof-of-learning items remain not implemented and not approved.
