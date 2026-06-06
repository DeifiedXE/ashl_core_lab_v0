# Outcome Unknown Payload / Draft Invariant Guard v0.1

## Purpose

This document records the v2.8a-3 guard for typed unknown outcomes and lesson_candidate_draft top-level invariants.

The guard exists because Phase 0 failure learning must not treat a structured container label as usable evidence when the actual payload says the outcome is unknown.

Key rule:

> Outcome type is a container label, not usable evidence.

An outcome with unknown status is unknown, even if it has a type.

## Unknown Outcome Payload Rule

The following outcome payloads are considered unknown:

- `{"type": "object_state", "status": "unknown"}`
- `{"type": "action_result", "status": "not_available"}`
- `{"type": "object_state", "status": "missing"}`
- `{"type": "object_state", "status": "null"}`
- `{"type": "perception_result", "value": {"status": "unknown"}}`

The `type` field may describe the outer container, but it does not make the outcome usable evidence when the payload status is unknown.

## Unknown vs Unknown Boundary

`unknown vs unknown is not evidence.`

`unknown vs unknown is invalid for failure learning.`

When both expected_outcome and actual_outcome are unknown, the event must not become valid failure learning evidence. Validation must fail, normalization must not produce a valid normalized failure_event, and the bridge / draft path must not be produced from that invalid evidence.

## Draft Invariant Guard

The lesson_candidate_draft validator must enforce the top-level trace-only boundary:

- `type == "lesson_candidate_draft_trace"`
- `draft_type == "lesson_candidate_draft"`
- `review_state == "pending"`
- `authority_boundary == "trace_only_draft"`
- `not_a_lesson_candidate is True`
- `needs_review is True`
- `not_approved is True`
- `not_active is True`
- `not_selection_eligible is True`
- `not_internalized is True`
- `not_written_to_lesson_store is True`
- `not_written_to_long_term_memory is True`

`insufficient_evidence must imply not_approvable.`

If core evidence is unknown or not_available, the draft must remain not approvable and must require human diagnosis. It must not produce retry, default, generic, or executable action correction.

## Authority Boundary

This package does not create approved lesson candidates.

This package does not write lesson_store.

This package does not write Long-term Memory.

This package does not add review queue runtime, evaluator runtime, sandbox runtime, selection behavior, activation behavior, conflict behavior, review behavior, or lesson_candidate builder runtime.

## Line Ending Policy

The repository should normalize text files with LF line endings for common source and documentation files:

```text
*.py text eol=lf
*.md text eol=lf
*.json text eol=lf
*.jsonl text eol=lf
*.txt text eol=lf
*.yml text eol=lf
*.yaml text eol=lf
```

This policy is intended to prevent CRLF / LF-only dirty states and does not change runtime behavior.
