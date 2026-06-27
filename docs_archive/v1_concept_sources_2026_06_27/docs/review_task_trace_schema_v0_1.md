# Review Task Trace-only Schema v0.1

## Purpose

This document defines the v2.8c trace-only `review_task_trace` schema.

`review_task_trace` is a to-do trace record for presenting a draft review task. It is not a manual review runtime, not a review decision, and not an approval / rejection / defer result.

This document sits after the lesson_candidate_draft review queue contract and before any future review task audit / regression package.

## Review Task Is Not A Review Decision

`review_task_trace is a trace-only to-do record, not a review decision.`

The trace must not represent:

- review decision
- approval
- rejection
- defer decision
- manual_review result
- approved lesson_candidate

## Completion Does Not Imply Approval

`review_task completion does not imply approval.`

Task states such as completed, closed, done, dismissed, or expired must not imply that a draft is approved, active, selection eligible, internalized, or written to lesson_store / Memory Layers.

The trace must keep:

- `completion_does_not_imply_approval = true`
- `not_approval = true`
- `not_review_decision = true`

## Reviewer Identity Source Boundary

`reviewer_identity must be supplied by runtime/session context, not LLM-generated content.`

The helper must not accept reviewer identity from:

- LLM output
- LLM-generated content
- draft JSON
- semantic summary
- review task description text
- external text payload
- injected queue entry fields

If runtime/session context is not available, the trace should use:

- `reviewer_identity = None`
- `reviewer_identity_source = "not_available_until_runtime_context"`
- `reviewer_identity_not_llm_generated = true`

## Semantic Key Display Boundary

The `semantic_key` may appear only as a secondary optional hint.

It must be:

- non_authoritative
- not proof
- not recommendation
- not conclusion

`semantic_key display level must be lower than source_failure_norm_key.`

`source_failure_norm_key must outrank semantic_key in review task presentation.`

The semantic key must not become the title, primary category, review reason, approval reason, sorting key, recommendation badge, proof, or conclusion.

## Structured Source References

The review task trace should preserve deterministic structured source references when available:

- `source_queue_entry_id`
- `source_draft_id`
- `source_failure_norm_key`

`source_failure_norm_key` is the primary structured reference for review task presentation.

## No Selection-facing Read API

`review_task_trace` must not expose selection-facing read APIs.

It must not feed:

- ActionSelection
- SelectionHelper
- ActionEngine
- instinct / drive layer
- lesson selection
- activation logic
- conflict resolver
- runtime evaluator
- curiosity engine
- memory_contrast_set

The trace must keep `no_selection_facing_read_api = true`.

## No Memory Layer Write

`review_task_trace` must not be written into:

- Working Memory
- Long-term Memory
- Archive Memory
- Core Memory

Expired, dismissed, closed, or completed review tasks remain trace-only records. They must not be archived into any Memory Layer by this package.

## Non-goals

This package does not implement:

- manual_review runtime
- review decision creation
- approved / rejected / deferred review result runtime
- approved lesson_candidate creation
- lesson_store write
- Memory Layer write
- review queue runtime expansion
- selection / activation / conflict / review logic changes
- draft mutation
- reviewer identity from LLM / draft / queue input
- semantic_key as title / primary category / proof / recommendation
- selection-facing read API
