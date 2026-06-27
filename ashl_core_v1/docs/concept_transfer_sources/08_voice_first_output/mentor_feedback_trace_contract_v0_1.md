# Mentor Feedback Trace Contract v0.1

Status: docs-only / trace-contract / mentor-feedback / no-runtime-implementation

## Purpose

This document defines the future `mentor_feedback_trace` contract.

It records how future mentor feedback may be attached to a `first_output_trace`. It is a
trace contract only. It does not implement mentor feedback runtime, teaching chat loop,
mentor_feedback_trace schema runtime, lesson_candidate pipeline connection, lesson_store
write, Memory Layer write, or any runtime behavior.

## Relation To Mentor Feedback Stub

`mentor_feedback_stub` is the future feedback contract. `mentor_feedback_trace` is the future
record shape for a feedback entry.

The current source first_output example remains:

```text
first_output: *
trace_id: first_output_trace:final_check:1
session_id: final_check
tick: 1
llm_used: false
engineering_stage: test_object
```

## Trace Is Record, Not Runtime

```text
mentor_feedback_trace is a feedback record, not feedback runtime.
```

This trace contract does not implement an interactive mentor loop, teaching chat loop,
feedback UI, feedback evaluator, or runtime feedback processor.

## Downstream Of First Output Trace

```text
mentor_feedback_trace is downstream of first_output_trace.
```

```text
mentor_feedback_trace must reference exactly one source_first_output_trace_id.
```

```text
mentor_feedback_trace must not exist without a source first_output_trace.
```

The feedback trace must be tied to exactly one source first_output trace. It must not be
free-floating feedback.

## Not Lesson Candidate Input By Itself

```text
mentor_feedback_trace is not lesson_candidate input by itself.
```

```text
mentor_feedback_trace must not directly create lesson_candidate.
```

```text
mentor_feedback_trace may make first_output_trace eligible for later lesson_candidate input consideration, but does not create lesson_candidate.
```

Eligibility for later consideration is not lesson_candidate creation, approval, activation,
or selection eligibility.

## Lesson Store And Memory Layer Boundary

```text
mentor_feedback_trace must not write to lesson_store.
mentor_feedback_trace must not write to Memory Layer.
```

```text
mentor_feedback_trace is evidence, not memory admission.
```

ASHL Core provides evidence.
D皜 Memory Layers decide memory admission.

## Test-Object Stage Boundary

```text
mentor_feedback_trace in the test-object stage is engineering supervision, not full Qingyin experience.
```

```text
mentor_feedback_trace does not prove awakening.
```

The trace does not prove dialogue ability, long-term growth, selfhood, or awakening.

## Required Conceptual Fields

A future `mentor_feedback_trace` should preserve:

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
engineering_stage = "test_object"
```

```text
creates_lesson_candidate must be false for mentor_feedback_trace.
writes_lesson_store must be false for mentor_feedback_trace.
writes_memory_layer must be false for mentor_feedback_trace.
```

These fields are contract vocabulary only. This package does not implement a trace schema
runtime.

## Conceptual Feedback Labels

Conceptual labels may include:

```text
observed
acceptable
retry
invalid
unsafe
```

These labels are contract vocabulary only. This package does not implement an enum or
validator.

Meaning:

- `observed`: mentor observed the output without authorizing learning.
- `acceptable`: mentor considers the test-object first_output acceptable.
- `retry`: mentor suggests future retry, without triggering runtime.
- `invalid`: mentor marks the output as violating the first_output contract.
- `unsafe`: mentor marks a safety concern for future review.

## Append-Only Boundary

```text
mentor_feedback_trace must be append-only or version-preserving.
```

Feedback traces must not overwrite prior feedback. Later corrections should create a new trace
version, correction trace, or append-only correction entry.

## Lesson Candidate Pipeline Boundary

```text
The lesson_candidate pipeline remains downstream of first_output_trace, mentor_feedback_trace, and later validation.
```

```text
mentor_feedback_trace must not bypass failure_event or lesson_candidate validation.
```

`mentor_feedback_trace` is one possible future evidence record. It is not a learning event,
failure_reason, lesson_candidate, reviewed lesson, or selection eligibility.

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

This contract defines `mentor_feedback_trace` as an append-only or version-preserving feedback
record tied to exactly one `source_first_output_trace_id`. It preserves the boundaries that
feedback traces are evidence only, do not create lesson_candidate, do not write lesson_store,
do not write Memory Layer, and do not prove awakening.
