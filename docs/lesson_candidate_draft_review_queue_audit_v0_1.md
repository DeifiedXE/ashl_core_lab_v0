# ASHL Core / Qingyin Lesson Candidate Draft Review Queue Audit v0.1

## Purpose

This document audits the v2.8b `Lesson Candidate Draft Review Queue Contract`.

It is not a review queue runtime implementation. It does not implement review_task runtime, create review decisions, write `lesson_store`, or write any Memory Layer.

## Audit Result

Audit result: PASS

## Audited Contract

Audited document:

```text
docs/lesson_candidate_draft_review_queue_contract_v0_1.md
```

Pipeline:

```text
lesson_candidate_draft
-> review_queue_entry / review_task contract
```

## Checked Boundaries

- review_queue_entry is a queue marker, not a review decision.
- review_task is a to-do item, not a review decision.
- review_task completion does not imply approval.
- entering the review queue is scheduling, not reviewing.
- queue may reference draft but must not mutate draft.
- Review queue must expose no selection-facing read APIs.
- Queue metrics may expose counts only, never draft content or draft keys.
- Unreviewed drafts must not be archived into any Memory Layer.
- Expired draft debug logs must not contain reusable lesson content.
- semantic_key presentation must not create authority anchoring.
- semantic_key display level must be lower than source_failure_norm_key.

## Metrics API Boundary

Metrics / telemetry may expose counts only:

```text
pending_count
expired_count
total_count
```

Metrics must not expose:

- draft_id list
- source_event_id
- source_failure_norm_key
- proposed_lesson_summary
- proposed_action_correction
- proposed_applicability_conditions
- semantic_key
- evidence_refs
- evaluator_source

Metrics must not become a shadow read API for ActionSelection, SelectionHelper, ActionEngine, CuriosityEngine, or runtime evaluator.

## Timeout / Expired Draft Boundary

Timeout / expired unreviewed drafts must not be archived into any Memory Layer.

They must not be serialized as reusable content into:

```text
expired_drafts.jsonl
debug_expired_drafts.json
archive_expired_drafts.md
llm_context_dump
```

If debug logging is necessary, it may only include:

```text
draft_id
queue_entry_id
timeout timestamp / tick
event type
```

It must not include proposed fields or semantic hints.

## semantic_key Presentation Boundary

semantic_key is a secondary optional hint.

semantic_key display level must be lower than source_failure_norm_key.

semantic_key must not be used as:

- title
- primary category
- diagnosis
- recommendation badge
- sorting key
- approval reason

This must be carried forward into v2.8c Review Task Trace-only Schema.

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

- review_task completion equals approval
- queue can mutate draft
- queue exposes selection-facing read APIs
- queue metrics may expose draft content
- timeout drafts may be archived into Memory Layers
- expired draft debug logs may contain proposed_action_correction
- semantic_key may be presented as conclusion / recommendation / proof
