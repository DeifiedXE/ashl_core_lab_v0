# Rejected / Deferred Proposed Fields Masking Contract v0.1

## Purpose

This document defines the masking boundary for proposed fields after rejected / deferred review decisions.

This document is docs-only / contract-only.

It does not implement masking runtime, review decision runtime, manual_review runtime, evaluator read path changes, memory_contrast_set read path changes, lesson_store writes, or Memory Layer writes.

## Core Rule

`Rejected or deferred proposed fields must be masked from evaluator and memory contrast reads.`

`Masked means not reusable as lesson content.`

Masking applies to downstream-readable outputs.

This contract applies when:

```text
decision_status = rejected
decision_status = deferred
```

This contract does not define the approved flow. Approved fields still require future independent lifecycle stages before any lesson_store or selection use.

## Fields That Must Be Masked

Rejected / deferred downstream-readable outputs must not expose:

- proposed_action_correction
- proposed_applicability_conditions
- proposed_lesson_summary
- semantic_key
- semantic_key_ref
- similar_context_hint_refs
- similar_context_hint.semantic_key
- evidence_refs that expose proposed reasoning as reusable lesson content
- draft field values that contain candidate lesson content
- LLM-assisted wording suggestions tied to proposed fields

## Safe Fields That May Remain Visible

The following safe metadata may remain visible:

- decision_id
- decision_status
- reason
- reason_code
- source_trace_id
- source_draft_id
- source_review_task_id
- asserted_at
- reviewer_identity_ref
- decision_authority_ref
- masking_policy_id
- masked_fields_summary

`masked_fields_summary` may list field names only. It must not include original proposed field content.

masked_fields_summary may list field names only.

Allowed example:

```json
{
  "masked_fields_summary": [
    "proposed_action_correction",
    "proposed_applicability_conditions",
    "proposed_lesson_summary",
    "semantic_key"
  ]
}
```

Forbidden example:

```json
{
  "masked_fields_summary": {
    "proposed_action_correction": "retry_with_default"
  }
}
```

## Allowed Masking Representations

Allowed masking representations include:

- field omitted
- field = null
- field = "[MASKED]"
- field = `{"masked": true, "reason": "rejected_decision"}`
- field = `{"masked": true, "reason": "deferred_decision"}`

Forbidden representations include:

- replacing content with low_confidence
- preserving content in debug / metadata / raw_payload
- exposing content to evaluator reads
- exposing content to memory_contrast_set reads

## Debug / Audit Log Boundary

`Debug logs must not preserve rejected or deferred proposed field content.`

Debug / audit logs may record:

- decision_id
- source_draft_id
- masked_field_names
- masking_reason
- timestamp / tick

Debug / audit logs must not preserve proposed field values.

## Rejected Boundary

Rejected proposed fields may exist in the rejected draft source, but they must not become:

- reusable lesson content
- action correction
- applicability condition
- semantic hint
- evaluator contrast evidence
- memory_contrast_set evidence

## Deferred Boundary

`Deferred proposed fields must be masked.`

Deferred is not:

- temporary approval
- weak approval
- pending but usable knowledge
- provisional selection hint
- future default approval

Deferred proposed fields must not become runtime-readable lesson content.

## Masking Triggers

Masking must not be inferred from vague non-status fields.

The following must not bypass or trigger masking by themselves:

- task_completed
- review_task_closed
- reviewed = true
- reason
- priority
- manual_note
- reviewer_comment

Only explicit review decision status controls this contract:

```text
decision_status == rejected
decision_status == deferred
```

Only explicit `decision_status == approved` may allow proposed fields to enter future independent lifecycle stages. Approved still does not write lesson_store or grant selection eligibility.

## Forbidden Interpretations

The following interpretations remain forbidden:

- masking runtime exists
- rejected proposed fields can be read by evaluator
- deferred proposed fields can be read by memory_contrast_set
- deferred is soft approval
- debug logs may preserve proposed field content
- masked_fields_summary may include original proposed content
- approved writes lesson_store

## Non-goals

- no masking runtime
- no review decision runtime
- no manual_review runtime
- no evaluator runtime changes
- no memory_contrast_set runtime changes
- no approved / rejected / deferred result runtime
- no lesson_store write
- no Long-term Memory write
- no Memory Layer write
- no selection / activation / conflict / review logic changes
