# ASHL Core / Qingyin failure_reason design assumption v0.1

## Definition

`failure_reason` is not free-form LLM text.

In Phase 0 design, a failure reason should be derived from a contrast between an expected outcome and an actual outcome. The value must be structured, traceable, and reviewable. If there is no contrast, there is no authoritative failure_reason.

LLM output may help with wording, categorization, or candidate generation, but it is not the sole authority for declaring a failure reason.

## Runtime Assumption

The assumed minimal runtime shape is:

1. An external task or sandbox defines `expected_outcome`.
2. Qingyin produces an action or response.
3. A checker observes `actual_outcome`.
4. A rule-based evaluator compares `expected_outcome` with `actual_outcome`.
5. A mismatch produces a structured `failure_reason`.

This keeps the failure reason grounded in observable contrast rather than hidden interpretation.

## Future Model

A later implementation may use:

```text
action_intent + expected_outcome
-> action execution
-> actual_outcome
-> memory_contrast_set / evaluator comparison
-> failure_reason_candidate
-> confidence gate / human review
-> reviewed failure_reason
```

The future model still preserves the same rule: no contrast, no authoritative failure_reason.

## Boundaries

- This document does not implement Phase 0 runtime integration.
- This document does not implement an evaluator.
- This document does not implement memory_contrast_set-based generation.
- This document does not let LLM output become automatic failure_reason authority.
- This document does not change known / unknown failure_reason behavior.
- This document does not change lesson generation behavior.
