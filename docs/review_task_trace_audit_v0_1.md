# Review Task Trace Audit v0.1

## Purpose

This document audits the v2.8c `review_task_trace` schema boundary.

This audit does not implement manual_review runtime.

This audit does not create review decisions, approve / reject / defer drafts, write lesson_store, or write any Memory Layer.

## Audit Result

Audit result: PASS.

## Audited Surface

Audited files:

- `ashl_core/review_tasks.py`
- `docs/review_task_trace_schema_v0_1.md`
- `tests/test_review_tasks.py`

Pipeline:

```text
review_queue_entry
-> review_task_trace
```

## Confirmed Boundaries

- `review_task_trace is a trace-only to-do record, not a review decision.`
- `review_task completion does not imply approval.`
- `reviewer_identity must be supplied by runtime/session context, not LLM-generated content.`
- reviewer_identity injection from queue / draft / LLM content is ignored or rejected.
- semantic_key is a secondary optional hint.
- semantic_key display level is lower than source_failure_norm_key.
- source_failure_norm_key remains the primary structured reference.
- review_task_trace does not mutate draft.
- review_task_trace exposes no selection-facing read API.
- `review_task_trace must not enter memory_contrast_set.`
- review_task_trace is not written to lesson_store or any Memory Layer.

## Reviewer Identity Boundary

reviewer_identity may only come from:

- runtime_session_context
- authenticated_human_session
- system_runtime_context

reviewer_identity must not come from:

- LLM-generated content
- queue payload
- draft payload
- semantic summary
- task description text
- external text payload

Invalid reviewer_identity_context sources are rejected.

## Semantic Key Presentation Boundary

semantic_key is a secondary optional hint.

semantic_key must not be used as:

- title
- primary category
- diagnosis
- approval reason
- recommendation badge
- sorting key
- proof

`source_failure_norm_key must outrank semantic_key in review task presentation.`

## No Selection-facing Read API

review_task_trace must not expose:

- action_context
- selection_context
- selection_api
- action_api
- ActionSelection
- SelectionHelper
- ActionEngine
- lesson selection
- activation logic
- conflict resolver
- runtime evaluator
- curiosity engine

## Memory Contrast Boundary

`review_task_trace must not enter memory_contrast_set.`

review_task_trace is not a learned experience and must not be used as evaluator contrast evidence.

It must not expose:

- memory_contrast_set
- evaluator expected_outcome source
- runtime decision context
- Long-term Memory promotion evidence

## Future Rejected / Deferred Proposed Fields Masking

Future review decision work must enforce:

```text
Rejected or deferred proposed fields must be masked from evaluator and memory contrast reads.
```

Fields to mask include:

- proposed_action_correction
- proposed_applicability_conditions
- proposed_lesson_summary
- semantic_key

Until masking is implemented, rejected / deferred proposed fields must not be exposed to evaluator or memory contrast pipelines.

## Forbidden Interpretations

The following interpretations remain forbidden:

- review_task_trace is review decision
- review_task completion equals approval
- reviewer_identity can be supplied by LLM
- semantic_key can be title / primary category / proof
- review_task_trace can mutate draft
- review_task_trace can be read by ActionSelection / SelectionHelper / ActionEngine
- review_task_trace can enter memory_contrast_set
- review_task_trace can write lesson_store or any Memory Layer

## Non-goals

- no manual_review runtime
- no review decision creation
- no approved / rejected / deferred review result runtime
- no approved lesson_candidate creation
- no lesson_store write
- no Memory Layer write
- no selection / activation / conflict behavior changes
- no rejected / deferred proposed fields masking runtime
