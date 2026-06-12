# Codex Task Queue Minimal v0

## Purpose

The Codex task queue is a Phase0 workflow coordination record for ASHL Core work packages.

It tracks package status, dependencies, blockers, and deferrals so future work can avoid package drift.

## Boundary Principle

No task queue entry, completed task, passing test, Codex-generated status, workflow record, or queue ordering counts as explicit human application approval.

The Codex task queue coordinates work packages only. It does not approve, apply, observe, evaluate, promote, remember, retain, predict, select, finalize, command, or prove learning.

## Supported Statuses

- `pending`
- `active`
- `blocked`
- `completed`
- `superseded`
- `deferred`

## Supported Task Types

- `documentation_only`
- `workflow_only`
- `capability_boundary`
- `sandbox_only`
- `risk_register`
- `cleanup`

## Current Safe Claim

ASHL Core has a minimal Codex task queue for Phase0 work package coordination, while no approval, runtime, memory, retention, predictor, sandbox, action-selection, final-action, production, or proof-of-learning capability is added.

## Explicit Non-Capabilities

- No approval is created or inferred.
- No lesson is applied.
- No sandbox outcome is observed or evaluated.
- No memory or retained JSONL is written.
- No retention write is created.
- No predictor is mutated.
- No runtime behavior changes.
- No selected_action, final_action, or direct command is created.
- No proof-of-learning claim is made.

## CLI

```text
run-codex-task-queue-minimal-check
```
