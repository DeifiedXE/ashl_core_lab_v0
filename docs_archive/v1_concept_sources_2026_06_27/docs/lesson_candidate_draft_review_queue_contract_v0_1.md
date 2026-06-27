# ASHL Core / Qingyin Lesson Candidate Draft Review Queue Contract v0.1

## Purpose

This document defines the contract boundary for sending `lesson_candidate_draft` into a future review queue.

It is not a manual_review runtime implementation. It does not create a review decision, approve / reject / defer a draft, write `lesson_store`, write Long-term Memory, or change selection / activation / conflict logic.

## Current Pipeline

```text
failure_event
-> normalized_failure_event
-> lesson_candidate_input_trace
-> lesson_candidate_draft
```

This document defines the next contract boundary:

```text
lesson_candidate_draft
-> review_queue_entry / review_task
```

## review_queue_entry Contract

`review_queue_entry` is a queue marker.

It means a `lesson_candidate_draft` has been scheduled for later review.

`review_queue_entry` is not:

- review decision
- approval
- rejection
- defer decision
- review result
- review started marker
- selection eligibility
- activation permission

```text
review_queue_entry is a queue marker, not a review decision.
```

## review_task Contract

`review_task` is a to-do item.

It means a review action is requested or scheduled for a draft.

`review_task` is not:

- review decision
- approval
- authorization
- review started signal
- review completed signal
- selection eligibility
- activation permission

```text
review_task is a to-do item, not a review decision.
```

```text
review_task completion does not imply approval.
```

## Queue May Reference Draft, Not Mutate Draft

The review queue may reference a draft.

The review queue must not mutate the draft.

The queue must not change:

- review_required
- needs_review
- review_state
- not_approved
- not_active
- not_selection_eligible
- not_internalized
- not_written_to_lesson_store
- not_written_to_long_term_memory
- insufficient_evidence
- not_approvable

The queue must not turn draft into:

- approved
- active
- selection eligible
- internalized
- written to lesson_store
- written to Long-term Memory

## Queue Is Scheduling, Not Reviewing

Entering the queue is not review start, review completion, or approval.

```text
entering the review queue is scheduling, not reviewing.
```

Forbidden interpretations:

```text
queued = reviewed
queued = review_started
queued = waiting_for_approval
queued = approved_by_default
queued = selection_eligible
```

## No Selection-facing Read APIs

```text
Review queue must expose no selection-facing read APIs.
```

The review queue must not expose draft entries to:

- ActionSelection
- SelectionHelper
- ActionEngine
- instinct / drive layer
- lesson selection
- activation logic
- conflict resolver
- runtime evaluator

The review queue must not provide:

- action_context
- selection_context
- runtime decision context
- evaluator expected_outcome source
- memory_contrast_set

The review queue is for review scheduling and display only.

## Memory Layer Boundary

```text
Unreviewed drafts must not be archived into any Memory Layer.
```

Queue entry / review_task must not be treated as timeout, deferred, stale, or archive workflow for:

- Working Memory
- Long-term Memory
- Archive Memory
- Core Memory

For now, abandoned queue items may only be described as:

- remove from queue
- drop / purge
- discarded_review_queue
- queue_expired

These are queue states, not Memory Layer writes.

## semantic_key Presentation Boundary

If `review_queue_entry` or `review_task` displays `semantic_key`, it must be presented as:

```text
non-authoritative hint
review-required hint
not proof
not recommendation
not conclusion
```

The UI / display layer must not style or phrase `semantic_key` as a conclusion, diagnosis, recommendation, or proof.

```text
semantic_key presentation must not create authority anchoring.
```

## review_queue_entry Minimal Contract

A future `review_queue_entry` may contain:

- queue_entry_id
- source_draft_id
- source_draft_ref
- queue_state
- created_at_tick or created_at_trace
- display_policy
- semantic_key_display_boundary
- not_review_decision
- not_approval
- not_selection_eligible
- no_selection_facing_read_api

Required safety flags:

```text
not_review_decision = true
not_approval = true
not_selection_eligible = true
no_selection_facing_read_api = true
```

## review_task Minimal Contract

A future `review_task` may contain:

- review_task_id
- source_queue_entry_id
- source_draft_id
- task_state
- assigned_reviewer_ref
- created_at_tick or created_at_trace
- not_review_decision
- not_approval
- completion_does_not_imply_approval
- no_draft_mutation

Required safety flags:

```text
not_review_decision = true
not_approval = true
completion_does_not_imply_approval = true
no_draft_mutation = true
```

## Not Implemented

This package does not implement:

- review queue runtime
- review_task runtime
- manual_review runtime
- review decision creation
- approved lesson_candidate creation
- lesson_store write
- Long-term Memory write
- Memory Layer write
- selection / activation / conflict behavior changes

Forbidden conclusions:

- queue entry is review decision
- review_task is review decision
- review_task completion equals approval
- queue mutates draft
- queue exposes selection-facing read API
- queued draft is visible to ActionSelection / ActionEngine
- queued draft writes lesson_store
- queued draft writes any Memory Layer
- semantic_key becomes review conclusion
