# ASHL Core / Qingyin Phase 0 Trust / Curiosity / Personality Boundary v0.1

## Purpose

This document clarifies Phase 0 boundaries for failure_event evaluator trust, failure_event review path, curiosity_probe source, and personality weight trace requirements.

This is a design assumption document only. It does not implement runtime behavior.

The purpose is to prepare clean assumptions before later Failure Event Normalization Trace and Failure Event to Lesson Candidate Input Bridge work.

It covers:

- evaluator trust boundary
- failure_event review path boundary
- curiosity_probe monitored-event boundary
- personality weight trace boundary

## Evaluator Trust Boundary

In Phase 0, evaluator output is a source of evidence. It is not absolute truth.

Allowed evaluator sources may include:

- sandbox_checker
- rule_based_evaluator
- human_teacher
- another explicitly reviewed evaluator source

Core statement:

```text
evaluator judgment is observable evidence, not absolute truth.
```

Evaluator error should be handled by human correction / user review, not by an infinite evaluator-reviewer chain.

failure_event traces should be able to mark:

- disputable
- reviewable
- replayable
- correctable

The boundary is:

```text
evaluator
-> human correction / user review
```

It is not:

```text
evaluator
-> evaluator reviewer
-> evaluator reviewer reviewer
-> ...
```

## Authoritative Failure Boundary

Phase 0 should not treat an evaluator judgment by itself as an authoritative failure.

Authoritative failure requires:

- structured failure_event
- expected_outcome
- actual_outcome
- evaluator_source
- mismatch
- schema / validation trace

It does not automatically produce:

- final truth
- lesson_candidate
- Long-term Memory
- instinct-like behavior

## failure_event Review Path Boundary

Phase 0 failure_event should often default to:

```text
needs_review = true
```

Review path is an assumption placeholder, not runtime implementation.

Possible review paths:

1. user_review / human_teacher_review
2. paired_subject_template_review
3. deferred_review

### user_review / human_teacher_review

Human review can check:

- whether evaluator output is disputed
- whether failure_event is valid
- whether failure_reason is correct
- whether a lesson_candidate should exist
- whether the event should be accepted, corrected, rejected, or marked disputed

### paired_subject_template_review

Paired subject template review is a future pattern for comparing similar situations.

Sketch:

```text
subject X fails in context C
paired subject X' succeeds or differs in context C'
compare the two before treating failure_event as stable
mark disputed / environment_sensitive / needs_human_review if unclear
```

This is not a runtime feature in this package.

### deferred_review

If immediate review cannot be completed, the failure_event may remain in a deferred review state.

Deferred review does not mean approved. Deferred review does not allow Long-term Memory admission or internalization.

## Curiosity Probe Boundary

curiosity_probe is not an LLM free-text feeling.

Not enough:

```text
I feel curious.
```

Phase 0 curiosity should be tied to a monitored event.

Assumed shape:

```text
monitored event
-> novelty / repetition / uncertainty signal
-> curiosity_probe candidate
```

Core statement:

```text
LLM may describe curiosity, but must not be the authoritative source of novelty.
```

LLM may help phrase a curiosity explanation, but it must not create an authoritative curiosity_probe without monitored evidence.

## Novelty and Repetition Boundary

Phase 0 curiosity may use simple assumptions:

```text
first_seen_event -> curiosity increases
repeated_stable_event -> curiosity decreases
repeated_unstable_event -> curiosity may increase again
```

These are design assumptions only. They do not implement curiosity runtime or novelty detector runtime.

## Personality Weight Boundary

Personality weight may later be influenced by many signals:

- teaching direction
- interaction history
- correction history
- trial feedback
- safety boundary
- action context
- failure / lesson history

However, personality weight adjustment must not silently drift outside trace.

## Personality Weight Trace Boundary

Core statements:

```text
confirmation is not always required.
trace is always required.
```

Personality weight adjustment may not require human confirmation in every small case, but every adjustment must leave a trace.

Trace should separate confirmation from traceability.

## Personality Weight Trace Schema Assumption

A future personality weight adjustment trace may include:

- source_event
- trigger_type
- old_weight
- new_weight
- delta
- reason_trace
- affected_behavior
- timestamp
- reversible / rollback hint

Core statement:

```text
personality weight may adjust automatically,
but every adjustment must be traceable.
```

## Personality Weight Guardrails

Personality weight should remain bounded by:

- Core Seed
- teaching direction
- safety boundary
- review / correction history
- failure history
- rollback path

If personality weight drift conflicts with Core Seed or teaching direction, it should become conflict / needs_review rather than silent behavior change.

## Runtime Boundaries

This document does not implement:

- evaluator trust runtime
- evaluator dispute runtime
- failure_event review runtime
- paired subject review runtime
- curiosity runtime
- novelty detector runtime
- personality weight runtime
- personality weight auto-adjustment
- personality weight rollback
- lesson_candidate builder runtime

This document does not let:

- LLM become authoritative novelty source
- curiosity_probe come from LLM free-text alone
- evaluator judgment become absolute truth
- personality weight adjustment happen without trace

This document does not change selection, activation, conflict, or review behavior.

## Summary

Phase 0 boundary summary:

```text
evaluator judgment is observable evidence, not absolute truth.
evaluator error is handled by human correction / user review.

failure_event review paths:
user_review / human_teacher_review
paired_subject_template_review
deferred_review

curiosity_probe must be triggered by monitored event, not LLM-only declaration.

personality weight may adjust automatically,
but every adjustment must leave trace.

confirmation is not always required.
trace is always required.
```
