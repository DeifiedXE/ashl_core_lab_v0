# ASHL Core / Qingyin Failure Event Bridge Audit v0.1

## Purpose

This document audits the v2.7a to v2.7c trace-only pipeline:

```text
failure_event
-> normalized_failure_event
-> lesson_candidate_input_trace
```

The audit is regression hardening only. It does not introduce runtime behavior.

## Audit Result

Audit result: PASS

## Checked Boundaries

- bridge output is not lesson_candidate
- bridge does not write lesson_store
- needs_review is preserved
- evaluator_source is preserved
- evaluator remains observable evidence, not absolute truth
- semantic_key is non-authoritative and review-required
- missing expected_outcome cannot produce normalized_failure_event
- missing actual_outcome cannot produce normalized_failure_event
- LLM-only raw description cannot become authoritative failure_reason at bridge stage

## lesson_candidate_input_trace Field Source / Authority Audit

| Field | Source | Authority | can_feed_future_builder_contract | Notes |
| --- | --- | --- | --- | --- |
| source_event_id | normalized failure_event trace | trace reference | conditional | Identifier only, not proof. |
| source_failure_norm_key | structured normalized fields | deterministic trace key | conditional | Grouping hint, not proof. |
| motivation_type | structured failure_event field | structured evidence | conditional | Preserved from source. |
| goal_type | normalized goal field | structured evidence | conditional | Derived from schema fields only. |
| action_type | normalized action_intent field | structured evidence | conditional | Derived from schema fields only. |
| expected_outcome_type | normalized expected_outcome field | structured evidence | conditional | Required for valid normalized bridge input. |
| actual_outcome_type | normalized actual_outcome field | structured evidence | conditional | Required for valid normalized bridge input. |
| mismatch_type | structured mismatch field | structured evidence | conditional | Not a semantic conclusion. |
| evaluator_source | structured evaluator_source field | observable evidence | conditional | evaluator judgment is observable evidence, not absolute truth. |
| needs_review | normalized review boundary | review boundary | yes | Must not become approved / eligible / active. |
| review_state | normalized review boundary | review boundary | conditional | Preserved as trace state only. |
| similar_context_hint.structure_key | schema fields | deterministic_hint | conditional | Deterministic hint, not proof. |
| similar_context_hint.causal_key | mismatch_type | structured_hint | conditional | Structured hint, not proof. |
| similar_context_hint.repetition_key | event history placeholder | trace_hint | conditional | `not_evaluated` until a real history runtime exists. |
| similar_context_hint.semantic_key | not_provided | non_authoritative_review_required | no | Must not be proof or eligibility. |
| authority_boundary | bridge helper constant | trace boundary | no | Marks bridge as trace-only input view. |
| not_a_lesson_candidate | bridge helper constant | safety boundary | no | Explicitly prevents treating trace as a candidate. |

## Semantic Key Boundary

semantic_key is not proof.

semantic_key may exist as a non-authoritative review-required hint only.

semantic_key must not become:

- deterministic proof
- eligibility flag
- approval source
- replacement for evaluator_source
- replacement for expected / actual outcome comparison

## v2.7d Dependency Note

v2.7d may define a lesson_candidate builder contract only after this audit confirms that bridge input fields have explicit source / authority boundaries.

v2.7d must not inherit unmarked semantic fields as authoritative evidence.
