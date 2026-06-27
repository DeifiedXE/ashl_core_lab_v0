# Review Decision Contract v0.1

## Purpose

This document defines the v2.8d `review_decision` contract and boundary.

This document is docs-only / contract-only.

It does not implement manual_review runtime, review decision runtime, review decision creation helper, approved / rejected / deferred result runtime, lesson_candidate creation, lesson_store write, selection eligibility, activation logic, conflict resolution logic, or Memory Layer write.

## Historical Event Record

`review_decision is a historical event record, not a live lesson object.`

`review_decision has no runtime execution permission and no state-machine mutation privilege.`

A review decision records that a draft was reviewed with a verdict. It is not a lesson, active lesson, selection candidate, runtime behavior, action rule, memory entry, or lesson_store write command.

## Decision Status

At v2.8d, `decision_status` must be one of:

```text
approved
rejected
deferred
```

Decision status must be explicit. It must not be inferred from task state fields such as completed, done, finished, closed, task_state, or review_task_completed.

`Review decision is all-or-nothing at v2.8d.`

`Partial approval is not allowed.`

The following statuses are out of scope:

- partial_approved
- conditional_approve
- approved_with_exceptions
- approved_summary_only
- approved_conditions_only
- soft_approved
- auto_approved
- preapproved

## Review Task Completion Boundary

`review_task completion is not review_decision creation.`

`review_task completion does not imply approval.`

Task completed / closed / done states must not imply approved, rejected, deferred, review_decision_created, selection_eligible, active, or enabled.

## Approved Decision Boundary

`approved decision does not create an active lesson.`

`approved decision does not grant lesson_store write permission.`

`approved decision does not directly grant selection eligibility.`

Approved only records a review verdict. It does not mean:

- lesson active
- lesson enabled
- runtime behavior changed
- instinct modified
- selection eligible
- lesson_store write permission

An approved draft must pass through future independent lifecycle stages before selection:

```text
formal lesson_candidate creation
activation check
conflict check
selection eligibility
```

Review decision service has zero write permission to lesson_store.

Do not add fields such as:

- approved_but_not_selectable
- approved_but_not_active
- is_selectable
- is_active
- is_enabled

`decision_status only records review verdict.`

## Rejected / Deferred Masking Boundary

`Rejected or deferred proposed fields must be masked from evaluator and memory contrast reads.`

For rejected / deferred decisions, downstream-readable outputs must not expose:

- proposed_action_correction
- proposed_applicability_conditions
- proposed_lesson_summary
- semantic_key
- similar_context_hint_refs

Allowed to preserve:

- decision_id
- decision_status
- reason_for_rejection / reason_for_defer
- source_trace_id
- source_draft_id
- asserted_at
- reviewer_identity_ref

This package records the contract boundary only. It does not implement masking runtime.

## Deferred Boundary

`deferred is not soft approval.`

Deferred means no decision is made yet. It does not grant temporary approval, weak approval, provisional selection, or default later use.

## Identity / Authority Boundary

`reviewer_identity` and `decision_authority` are distinct.

`decision_authority / reviewer_identity / reviewer_session_token binding is required before runtime decision creation.`

This is a future runtime boundary only. v2.8d does not implement runtime decision creation.

`reviewer_identity must be supplied by runtime/session context, not LLM-generated content.`

## Decision Fields Must Not Grant Runtime Permission

`Decision fields must not imply runtime permission, state activation, or system override.`

Decision fields must not imply:

- write_permission
- store_permission
- allow_execution
- allow_selection
- set_active
- is_enabled_now
- system_override
- gate_bypass
- selection_permission
- activation_flag

## Contract Shape

A future `review_decision` may use a contract shape like:

```python
{
    "type": "review_decision_contract",
    "contract_only": True,
    "historical_event_record": True,
    "decision_id": "...",
    "decision_status": "approved | rejected | deferred",
    "source_review_task_id": "...",
    "source_draft_id": "...",
    "source_trace_id": "...",
    "reviewer_identity_ref": "...",
    "decision_authority_ref": "...",
    "asserted_at": "...",
    "reason": "...",
    "masked_proposed_fields_policy": {
        "rejected": "mask_proposed_fields_from_downstream_reads",
        "deferred": "mask_proposed_fields_from_downstream_reads"
    },
    "no_runtime_permission": True,
    "no_lesson_store_write_permission": True,
    "no_selection_eligibility": True,
    "no_activation": True,
    "not_active_lesson": True,
    "not_lesson_store_write_command": True,
    "not_selection_candidate": True,
    "not_memory_entry": True
}
```

This is a contract sketch, not an implemented runtime helper.

## Forbidden Interpretations

The following interpretations remain forbidden:

- review decision runtime exists
- approved creates lesson_candidate
- approved writes lesson_store
- approved grants selection eligibility
- approved activates lesson
- rejected / deferred proposed fields can be read by evaluator
- deferred is soft approval
- partial approval is supported
- decision fields grant runtime permission

## Non-goals

- no manual_review runtime
- no review decision runtime
- no review decision creation helper
- no approved / rejected / deferred result runtime
- no approved lesson_candidate creation
- no lesson_store write
- no selection / activation / conflict / review logic changes
- no Long-term Memory write
- no Memory Layer write
- no rejected / deferred proposed fields masking runtime
