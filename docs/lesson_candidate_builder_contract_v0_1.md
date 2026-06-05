# ASHL Core / Qingyin Lesson Candidate Builder Contract v0.1

## Purpose

This document defines the future lesson_candidate builder contract.

It is contract documentation only. It does not implement runtime behavior, does not create `lesson_candidate`, does not write `lesson_store`, and does not connect manual review / selection / activation / conflict lifecycle.

This document defines:

- lesson_candidate builder input boundary
- field source / authority boundary
- candidate output contract
- review-gated behavior
- forbidden shortcuts

## Current Trace-only Pipeline

The current pipeline is:

```text
failure_event
-> normalized_failure_event
-> lesson_candidate_input_trace
```

Meaning:

- `failure_event` is a structured failure entry.
- `normalized_failure_event` is a deterministic trace view, not a new authority source.
- `lesson_candidate_input_trace` is preparation evidence, not a lesson_candidate.

## Builder Contract Boundary

A future lesson_candidate builder may convert:

```text
lesson_candidate_input_trace
-> lesson_candidate draft / candidate proposal
```

The builder must not:

- approve lesson
- activate lesson
- write Long-term Memory
- internalize behavior
- resolve conflict
- bypass review

## Input Contract

The only acceptable input for a future builder is:

```text
lesson_candidate_input_trace
```

Required input fields include:

- source_event_id
- source_failure_norm_key
- motivation_type
- goal_type
- action_type
- expected_outcome_type
- actual_outcome_type
- mismatch_type
- evaluator_source
- needs_review
- review_state
- similar_context_hint
- authority_boundary

Each field must keep an explicit source / authority boundary.

## Input Authority Boundary

### Structured Evidence Fields

These fields may be treated as structured evidence, but not as automatic proof:

- source_event_id
- source_failure_norm_key
- motivation_type
- goal_type
- action_type
- expected_outcome_type
- actual_outcome_type
- mismatch_type
- evaluator_source

The evaluator boundary remains:

```text
evaluator judgment is observable evidence, not absolute truth.
```

### Trace / Grouping Hint Fields

These fields are hints:

- similar_context_hint.structure_key
- similar_context_hint.causal_key
- similar_context_hint.repetition_key

Hints may help a future builder organize evidence, but they must not become proof of lesson applicability.

### Non-authoritative Review-required Field

```text
similar_context_hint.semantic_key
```

`semantic_key` may only be a:

```text
non-authoritative review-required hint
```

`semantic_key` must not become:

- proof
- deterministic similarity
- eligibility source
- approval source
- failure_reason source
- lesson applicability proof

## Output Contract

If a future builder creates a lesson_candidate draft, the minimal output contract should include:

- candidate_id or draft_id
- source_event_id
- source_failure_norm_key
- proposed_lesson_summary
- proposed_applicability_conditions
- proposed_action_correction
- evidence_refs
- similar_context_hint_refs
- evaluator_source
- needs_review
- review_state
- authority_boundary
- not_approved
- not_active
- not_selection_eligible
- not_internalized

The default state must be:

```text
needs_review = true
review_state = pending / unreviewed
not_approved = true
not_active = true
not_selection_eligible = true
not_internalized = true
```

Builder output must be review-gated.

A builder output must not become an active lesson.

## proposed_lesson_summary Boundary

`proposed_lesson_summary` may be derived from structured evidence and optional assisted wording.

If an LLM is used in a future package to help phrase a summary, the trace must record:

```text
summary_source = llm_assisted
summary_authority = non_authoritative
requires_review = true
```

LLM wording must not become an authoritative failure_reason.

## Review-gated Flow

Builder output must follow:

```text
builder output
-> review queue / pending candidate
-> human review or defined review path
-> approved / rejected / deferred
```

It must not follow:

```text
builder output
-> active lesson
```

## Forbidden Behavior

The lesson_candidate builder must not:

- approve lesson
- activate lesson
- select lesson
- resolve conflict
- write Long-term Memory
- promote learned_principle
- internalize instinct-like behavior
- modify personality_weight
- modify curiosity / novelty / interest state

## Long-term Memory Boundary

The lesson_candidate builder must not write Long-term Memory.

If a future package creates a learned_principle_candidate or memory promotion evidence, the responsibility boundary remains:

```text
ASHL Core provides evidence.
Qingyin Memory Layers decide memory admission.
```

## Not Implemented In v2.7d

This package does not implement:

- lesson_candidate builder runtime
- lesson_candidate creation
- lesson_store write
- manual review runtime for builder output
- automatic approval / activation / selection
- Long-term Memory write
- learned_principle generation runtime
- internalization

`semantic_key` is not proof.

LLM output is not an authoritative failure_reason source.

## Summary

lesson_candidate_input_trace is preparation evidence, not a lesson_candidate. The builder contract defines a future input and output boundary, but the builder must not approve, activate, select, or store anything. semantic_key is a non-authoritative review-required hint. Builder output must be review-gated.
