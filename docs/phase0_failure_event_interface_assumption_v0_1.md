# ASHL Core / Qingyin Phase 0 failure_event interface assumption v0.1

## Purpose

This document defines the Phase 0 failure_event interface assumption between the sandbox / action layer and the lesson layer.

It is one of the Phase 0 integration assumption foundations. It does not implement runtime behavior. It is a design assumption document that explains the information shape needed before a failure can become lesson-layer input.

Core question:

```text
How should a Phase 0 action failure be passed into the lesson layer?
```

## Core Chain

The assumed chain is:

```text
motivation
-> goal
-> action_intent
-> expected_outcome
-> actual_outcome
-> evaluator
-> failure_event
-> normalized failure_reason
-> lesson_candidate
-> manual review
-> approved lesson
```

Meaning:

- motivation produces goal
- goal produces expected_outcome
- expected_outcome and actual_outcome mismatch produces failure_event
- failure_event is normalized into a normalized failure_reason
- the lesson layer should receive structured failure input, not raw natural language failure text

## motivation

`motivation` records why an action was attempted.

Suggested `motivation_type` values:

- `teacher_instruction`
- `sandbox_task`
- `curiosity_probe`
- `task_dependency`
- `safety_response`

Examples:

```text
motivation_type: teacher_instruction
motivation_source: human_teacher
```

```text
motivation_type: curiosity_probe
motivation_source: unknown_object_detected
```

Without motivation, the system should not assume it understands why an action_intent exists.

## goal

`goal` is the action-layer objective derived from motivation.

Examples:

```text
motivation_type: teacher_instruction
goal: pick_up_object
```

```text
motivation_type: curiosity_probe
goal: gather_information_about_unknown_object
```

A goal should be connected to at least one expected_outcome.

## action_intent

`action_intent` records the intended action before execution.

Examples:

```text
action_type: observe
target_id: object_001
```

```text
action_type: approach
target_id: cube_001
```

```text
action_type: pick_up
target_id: cube_001
```

The action_intent should be traceable to motivation and goal. It is not the same thing as the final action result.

## expected_outcome

`expected_outcome` records what the action expects to change or learn.

Example:

```yaml
expected_outcome:
  type: object_state
  target_id: cube_001
  expected_state: held
```

Example:

```yaml
expected_outcome:
  type: information_gain
  target_id: object_001
  expected_state: basic_features_recorded
```

Without expected_outcome, there is no authoritative failure_event. The system may record an unclassified_event instead.

## actual_outcome

`actual_outcome` records what the sandbox, environment, action layer, or checker observed.

Example:

```yaml
actual_outcome:
  type: object_state
  target_id: cube_001
  actual_state: not_moved
```

Example:

```yaml
actual_outcome:
  type: observation_result
  target_id: object_001
  actual_state: no_features_detected
```

actual_outcome should come from sandbox / environment / action layer observation. It is not free-form LLM imagination.

## evaluator

`evaluator` compares expected_outcome and actual_outcome.

Current possible evaluator sources:

- `sandbox_checker`
- `rule_based_evaluator`
- `external_test_helper`
- `human_teacher`

Future possible evaluator inputs:

- `memory_contrast_set`
- `lesson_history`
- `familiarity_context`

The evaluator source must be recorded as `evaluator_source`. A future memory-based evaluator may assist comparison, but this document does not implement it.

## mismatch

`mismatch` is produced when the evaluator compares expected_outcome and actual_outcome and finds they do not match.

Example:

```text
expected: cube_001 is held
actual: cube_001 not moved
mismatch: true
```

If `mismatch == false`, a failure_event should not be generated. The system may instead record a success_event or observation_event.

If expected_outcome is missing, the system should not generate an authoritative failure_event.

## failure_event schema

Suggested structured schema:

- `failure_event_id`
- `trace_id`
- `timestamp`
- `motivation_type`
- `motivation_source`
- `goal`
- `action_intent`
- `expected_outcome`
- `actual_outcome`
- `evaluator_source`
- `mismatch`
- `failure_reason_id`
- `failure_type`
- `failure_scope`
- `confidence`
- `needs_review`
- `related_lesson_ids`
- `raw_event_ref`
- `human_notes`

The failure_event must be structured, traceable, and reviewable.

`human_notes` may support review, but it must not replace structured fields. `raw_event_ref` may point back to sandbox or action trace data, but the lesson layer should not depend on raw event text alone.

## normalized failure_reason

The failure_event can be normalized into failure_reason fields.

Example:

```yaml
failure_event:
  expected: cube_001 is held
  actual: cube_001 not_moved
  evaluator_source: sandbox_checker
  mismatch: true

normalized_failure_reason:
  failure_reason_id: object_not_picked_up
  failure_type: action_result_mismatch
```

`failure_reason_id` may be used by the lesson layer.

failure_reason is not free-form LLM text. LLM output may assist wording or categorization, but it is not the authority source.

## lesson_candidate input

A lesson_candidate builder should receive structured failure_event / normalized failure_reason data.

Suggested lesson_candidate input fields:

- `failure_reason_id`
- `failure_type`
- `motivation_type`
- `goal`
- `action_type`
- `target_type`
- `expected_outcome`
- `actual_outcome`
- `evaluator_source`
- `similar_context_hint`
- `needs_review`

The lesson_candidate should not depend only on raw natural language failure description.

## similar_context_hint

This document extends the v2.6c-1 similar situation assumption into the failure_event interface.

Early `similar_context_hint` may include:

- `structure_key`
- `semantic_key`
- `causal_key`
- `repetition_key`

similar_context_hint must come from structured metadata. It is only a hint, not proof, and should remain traceable and reviewable.

## review requirement

Phase 0 failure_event should default to human review when uncertainty is present.

Recommended default:

```text
needs_review = true
```

Possible reasons:

- evaluator confidence is low
- expected_outcome is incomplete
- actual_outcome is ambiguous
- multiple failure_reason values are possible
- failure_reason would create a lesson_candidate
- action is safety-related
- action is novel
- LLM-assisted wording was involved
- similar_context_hint is uncertain

## Summary

Phase 0 should not pass raw failure text directly into the lesson layer.

The bridge should be a structured failure_event.

failure_event should include motivation / goal / action_intent / expected_outcome / actual_outcome / evaluator / mismatch.

failure_reason is the normalized result of failure_event.

No expected / actual contrast means no authoritative failure_reason.

The lesson layer should receive structured, traceable, reviewable failure input.

## Boundaries

- This document does not implement Phase 0 sandbox runtime.
- This document does not implement failure_event runtime.
- This document does not implement an evaluator.
- This document does not implement motivation runtime.
- This document does not implement curiosity runtime.
- This document does not implement attention weight runtime.
- This document does not implement observe / approach / avoid / ask_for_help runtime behavior.
- This document does not implement perception.
- This document does not implement similar_context runtime.
- This document does not implement a lesson_candidate builder runtime.
- This document does not integrate Phase 0 sandbox with the lesson layer.
- This document does not let LLM output authoritatively declare mismatch.
- This document does not let LLM output become an authoritative failure_reason.
- This document does not change selection logic.
- This document does not change conflict logic.
- This document does not change review logic.
- This document does not change strict supersede activation.
- This document does not change known / unknown failure_reason behavior.
