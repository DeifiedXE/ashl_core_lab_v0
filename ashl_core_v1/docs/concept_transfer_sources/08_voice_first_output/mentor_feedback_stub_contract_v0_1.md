# Mentor Feedback Stub Contract v0.1

Status: docs-only / feedback-contract / first-output / no-runtime-implementation

## Purpose

This document defines the future `mentor_feedback_stub` contract for first_output traces.

It is a contract document only. It does not implement mentor feedback runtime, teaching chat
loop, mentor_feedback_trace schema runtime, lesson_candidate pipeline connection, lesson_store
write, Memory Layer write, or any runtime behavior.

## Contract Scope

`mentor_feedback_stub` is intended to describe how a future mentor may annotate a
`first_output_trace` after Minimal First Output Runtime v0 records a test-object first_output.

It is not a learning event, not a failure_reason, not a lesson_candidate, and not memory
admission.

## Relation To First Output Trace

```text
Mentor feedback is downstream of first_output_trace.
```

The current audited first_output example is:

```text
first_output: *
trace_id: first_output_trace:final_check:1
session_id: final_check
tick: 1
llm_used: false
engineering_stage: test_object
```

The feedback stub may refer to this kind of first_output_trace, but it does not change the
trace and does not authorize downstream learning.

## Feedback Stub Is Not Runtime

```text
mentor_feedback_stub is a contract for future feedback, not feedback runtime.
```

This contract does not create an interactive mentor loop, teaching chat loop, feedback UI,
or automated feedback evaluator.

## Mentor Feedback Stub Is Not Lesson Candidate Input

```text
mentor_feedback_stub is not lesson_candidate input by itself.
```

```text
mentor_feedback_stub must not directly create lesson_candidate.
```

Mentor feedback may later become one reviewed input in a future bridge, but this contract does
not implement that bridge and does not create a lesson_candidate.

```text
mentor_feedback_stub may make first_output_trace eligible for later lesson_candidate input consideration, but does not create lesson_candidate.
```

Eligibility for later consideration is not lesson creation, not approval, and not activation.

## Lesson Store And Memory Layer Boundary

```text
mentor_feedback_stub must not write to lesson_store.
mentor_feedback_stub must not write to Memory Layer.
```

```text
mentor_feedback_stub is evidence, not memory admission.
```

ASHL Core provides evidence.
D皜 Memory Layers decide memory admission.

## Test-Object Stage Boundary

```text
mentor_feedback_stub in the test-object stage is engineering supervision, not full Qingyin experience.
```

```text
mentor_feedback_stub does not prove awakening.
```

Mentor feedback on a first_output trace does not prove dialogue ability, long-term growth,
selfhood, or awakening.

## Minimal Input Fields

A future `mentor_feedback_stub` may need:

```text
first_output_trace
mentor_feedback_label
mentor_feedback_note optional
mentor_id or mentor_source
feedback_tick or timestamp
```

The referenced `first_output_trace` should preserve:

```text
trace_id
session_id
tick
first_output
llm_used = false
engineering_stage = test_object
```

## Conceptual Feedback Labels

Conceptual labels may include:

```text
observed
acceptable
retry
invalid
unsafe
```

These labels are contract vocabulary only. This package does not implement a runtime enum
or validator.

Meaning:

- `observed`: mentor observed the output without approving learning.
- `acceptable`: mentor considers the first_output acceptable as a test-object output.
- `retry`: mentor suggests a future retry, without triggering runtime.
- `invalid`: mentor marks the output as violating the first_output contract.
- `unsafe`: mentor marks a safety concern for future review.

## Future Mentor Feedback Trace Fields

A future `mentor_feedback_trace` may include:

```text
feedback_trace_id
trace_type = "mentor_feedback_trace"
source_first_output_trace_id
session_id
tick
mentor_feedback_label
mentor_feedback_note optional
mentor_source
feedback_tick_or_timestamp
effect = "feedback_only"
creates_lesson_candidate = false
writes_lesson_store = false
writes_memory_layer = false
```

```text
creates_lesson_candidate must be false for mentor_feedback_stub.
writes_lesson_store must be false for mentor_feedback_stub.
writes_memory_layer must be false for mentor_feedback_stub.
```

These are conceptual future fields only. This package does not implement a
mentor_feedback_trace schema runtime.

## Lesson Candidate Pipeline Boundary

```text
The lesson_candidate pipeline remains downstream of first_output trace, mentor feedback, and later validation.
```

```text
mentor_feedback_stub must not bypass failure_event or lesson_candidate validation.
```

`mentor_feedback_stub` may only describe future supervision around a first_output_trace.
It does not create a learning event, failure_reason, lesson_candidate, reviewed lesson, or
selection eligibility.

## Explicit Non-Implementation Boundary

This contract does not implement:

- mentor feedback runtime
- mentor_feedback_trace schema runtime
- teaching chat loop
- lesson_candidate pipeline connection
- failure_event automatic builder
- lesson_candidate automatic builder
- lesson_store write
- Memory Layer write
- evaluator runtime
- review decision runtime
- selection eligibility runtime
- activation runtime
- first_output generator expansion
- state store
- bounded senses runtime
- Screen Sense / Camera Sense runtime
- Symbol Grounding runtime
- LLM response generation
- Audio Sense / STT / TTS / voice loop
- awakening claim
- dialogue ability claim
- long-term growth claim

## Audit Summary

This contract keeps mentor feedback downstream of first_output_trace and upstream of any
future reviewed bridge. It preserves the boundary that feedback is evidence only, does not
create lesson_candidate, does not write lesson_store, does not write Memory Layer, and does
not prove awakening.
