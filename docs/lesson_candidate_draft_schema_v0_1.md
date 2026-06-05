# ASHL Core / Qingyin Lesson Candidate Draft Schema v0.1

## Purpose

This document defines the trace-only `lesson_candidate_draft` schema.

It does not implement a lesson_candidate builder runtime. It does not create an approved `lesson_candidate`, does not write `lesson_store`, does not call manual review runtime, and does not change selection / activation / conflict behavior.

## Pipeline

```text
failure_event
-> normalized_failure_event
-> lesson_candidate_input_trace
-> lesson_candidate builder contract
-> lesson_candidate_draft_schema
```

`lesson_candidate_draft` is a review-gated draft, not an approved lesson_candidate.

## Required Draft Boundary

Every draft field must declare source and review_required.

Every structured draft field must include:

- value
- source
- authority
- review_required

Forbidden source values:

- TBD
- unknown
- inferred_without_trace
- llm_default
- empty / missing source

If a value is not available, the future schema should use:

```text
source = not_available
included = false
```

and must not promote that field into active draft evidence.

## Schema Shape

```python
{
    "draft_trace": True,
    "draft_type": "lesson_candidate_draft",
    "source_input_trace_id": "...",
    "source_event_id": "...",
    "source_failure_norm_key": "...",

    "proposed_lesson_summary": {
        "value": "...",
        "source": "structured_evidence_summary",
        "authority": "non_authoritative",
        "review_required": True
    },

    "proposed_applicability_conditions": {
        "value": [...],
        "source": "structured_fields",
        "authority": "draft_conditions_not_proof",
        "review_required": True
    },

    "proposed_action_correction": {
        "value": "...",
        "source": "mismatch_and_action_context",
        "authority": "draft_correction_not_executable",
        "review_required": True
    },

    "evidence_refs": {
        "value": [...],
        "source": "lesson_candidate_input_trace",
        "authority": "evidence_pointers_not_proof",
        "review_required": True
    },

    "similar_context_hint_refs": {
        "value": {...},
        "source": "lesson_candidate_input_trace.similar_context_hint",
        "authority": "hint_not_proof",
        "review_required": True
    },

    "evaluator_source": {
        "value": "...",
        "source": "lesson_candidate_input_trace.evaluator_source",
        "authority": "observable_evidence_not_absolute_truth",
        "review_required": True
    },

    "needs_review": True,
    "review_state": "pending",
    "not_approved": True,
    "not_active": True,
    "not_selection_eligible": True,
    "not_internalized": True,
    "not_written_to_lesson_store": True,
    "not_written_to_long_term_memory": True,
    "authority_boundary": "trace_only_draft",
    "not_a_lesson_candidate": True
}
```

## Field Boundaries

### proposed_lesson_summary

Default source:

```text
structured_evidence_summary
```

If an LLM assists with wording in the future:

```text
source = llm_assisted_summary
authority = non_authoritative
review_required = true
```

It must not become:

- authoritative_failure_reason
- approved_lesson
- final_rule

### proposed_applicability_conditions

Allowed sources:

- structured_fields
- lesson_candidate_input_trace
- similar_context_hint.structure_key
- similar_context_hint.causal_key

Forbidden sources:

- semantic_key
- LLM semantic summary

Authority:

```text
draft_conditions_not_proof
```

### proposed_action_correction

Allowed sources:

- mismatch_type
- action_type
- expected_outcome_type
- actual_outcome_type
- structured failure evidence

Authority:

```text
draft_correction_not_executable
```

It is not an executable action.

### evidence_refs

Allowed sources:

- source_event_id
- source_failure_norm_key
- lesson_candidate_input_trace
- normalized_failure_event

Authority:

```text
evidence_pointers_not_proof
```

### similar_context_hint_refs

Source:

```text
lesson_candidate_input_trace.similar_context_hint
```

`semantic_key` remains:

```text
non_authoritative_review_required
```

semantic_key must not become proof, eligibility source, or verified applicability condition.

### evaluator_source

Source:

```text
lesson_candidate_input_trace.evaluator_source
```

Authority:

```text
observable_evidence_not_absolute_truth
```

It must not become absolute truth.

## Review-gated Defaults

The draft must always start as:

```text
needs_review = true
review_state = pending
not_approved = true
not_active = true
not_selection_eligible = true
not_internalized = true
not_written_to_lesson_store = true
not_written_to_long_term_memory = true
```

It must not contain:

```text
approved = true
active = true
selection_eligible = true
internalized = true
```

## Input Validation

`build_lesson_candidate_draft_trace()` must only accept `lesson_candidate_input_trace`.

Required input boundary:

```text
bridge_trace = true
not_a_lesson_candidate = true
authority_boundary = trace_only_input_view
```

Raw `failure_event` or `normalized_failure_event` input must not silently produce `lesson_candidate_draft`.

## Not Implemented

This package does not implement:

- lesson_candidate builder runtime
- approved lesson_candidate creation
- lesson_store write
- manual review runtime
- sandbox runtime
- evaluator runtime
- selection / activation / conflict behavior changes
- Long-term Memory write
- internalization
