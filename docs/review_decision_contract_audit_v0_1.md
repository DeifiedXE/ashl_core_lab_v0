# Review Decision Contract Audit v0.1

## Purpose

This document audits the v2.8d `Review Decision Contract` boundary.

This audit is docs-only / audit-regression-only.

It does not implement manual_review runtime, review decision runtime, approved / rejected / deferred result runtime, lesson_store writes, selection / activation / conflict logic, or Memory Layer writes.

## Audit Result

Audit result: PASS.

## Audited Surface

Audited document:

- `docs/review_decision_contract_v0_1.md`

Pipeline:

```text
review_task_trace
-> review_decision contract
```

## Confirmed Contract Invariants

- `review_decision is a historical event record, not a live lesson object.`
- `review_decision has no runtime execution permission and no state-machine mutation privilege.`
- `review_task completion is not review_decision creation.`
- `decision_status is the only review verdict field.`
- `decision_status` only allows `approved`, `rejected`, or `deferred`.
- `approved decision does not create an active lesson.`
- `approved decision does not grant lesson_store write permission.`
- `approved decision does not directly grant selection eligibility.`
- `Review decision service has zero write permission to lesson_store.`
- `Rejected or deferred proposed fields must be masked from evaluator and memory contrast reads.`
- `deferred is not soft approval.`
- `Partial approval is not allowed.`
- `Decision fields must not imply runtime permission, state activation, or system override.`
- `decision_authority / reviewer_identity / reviewer_session_token binding is required before runtime decision creation.`

## Approved Boundary

Approved is a review verdict only.

Approved must not imply:

- active lesson
- enabled lesson
- lesson_store write
- selection eligibility
- activation
- runtime behavior change
- Memory Layer write

Approved draft must pass through future independent lifecycle stages before selection:

```text
formal lesson_candidate creation
activation check
conflict check
selection eligibility
```

## Rejected / Deferred Masking Boundary

Rejected or deferred proposed fields must be masked from evaluator and memory contrast reads.

Fields to mask:

- proposed_action_correction
- proposed_applicability_conditions
- proposed_lesson_summary
- semantic_key
- similar_context_hint_refs

Allowed safe fields:

- decision_id
- decision_status
- reason
- source_trace_id
- source_draft_id
- asserted_at
- reviewer_identity_ref
- decision_authority_ref

Masking runtime is not implemented in this package.

## Deferred Boundary

Deferred is not soft approval.

Deferred must not grant:

- temporary selection
- activation
- lesson_store write
- future default approval
- usable runtime knowledge

## Partial Approval Boundary

Review decision is all-or-nothing at v2.8d.

Partial approval is not allowed.

The following are not valid decision_status values:

- partial_approved
- conditional_approve
- approved_with_exceptions
- approved_summary_only
- approved_conditions_only
- soft_approved
- auto_approved
- preapproved

## Runtime Permission Boundary

Decision fields must not imply runtime permission, state activation, or system override.

Decision contract must not define fields that imply:

- execution permission
- store write permission
- selection permission
- activation
- bypass
- override

Forbidden field names include:

- approved_but_not_selectable
- approved_but_not_active
- is_selectable
- is_active
- is_enabled
- set_active
- activation_flag
- selection_permission
- write_permission
- store_permission
- allow_execution
- allow_selection
- system_override
- gate_bypass

## Forbidden Interpretations

The following interpretations remain forbidden:

- review decision runtime exists
- approved creates active lesson
- approved writes lesson_store
- approved grants selection eligibility
- rejected / deferred proposed fields are readable by evaluator
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
- no Memory Layer write
- no selection / activation / conflict behavior changes
- no masking runtime
- no identity / session binding runtime
