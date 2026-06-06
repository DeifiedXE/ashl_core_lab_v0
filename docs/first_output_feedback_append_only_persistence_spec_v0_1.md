# First Output + Mentor Feedback Append-only Persistence Spec v0.1

## Purpose

This document specifies future append-only persistence rules for:

```text
first_output_trace
mentor_feedback_trace
```

It is docs-only. It does not implement JSONL writing, persistence runtime, or data migration.

## Future files

Future persistence may use:

```text
data/first_output_traces.jsonl
data/mentor_feedback_traces.jsonl
```

These paths are specified as future append-only targets only. This package does not create or write these files.

## Append-only rule

The persistence rule is append-only.

Required persistence properties:

```text
append-only
no overwrite
no silent correction
correction must be new trace
raw trace preserved
```

If a trace is wrong or superseded, the original raw trace must remain preserved. Correction must be a new trace that references the prior trace, not an in-place edit.

## Minimum record identity

Each persisted trace record must include:

```text
trace_id
trace_type
session_id
tick
created_at_or_tick
engineering_stage
```

These fields provide minimum identity and replay anchoring. They are not approval, learning, or Memory Layer admission.

## first_output_trace persistence boundary

first_output_trace must preserve llm_used = false.

first_output_trace must preserve:

```text
llm_used = false
first_output: *
engineering_stage = test_object
not awakening
not dialogue ability
not long-term growth
```

Persisting first_output_trace is evidence preservation only. It is not proof of awakening, dialogue ability, or long-term growth.

## mentor_feedback_trace persistence boundary

mentor_feedback_trace must preserve effect = feedback_only.

mentor_feedback_trace must preserve:

```text
source_first_output_trace_id
mentor_feedback_label
effect = feedback_only
creates_lesson_candidate = false
writes_lesson_store = false
writes_memory_layer = false
```

Persisting mentor_feedback_trace keeps mentor feedback evidence, but it does not turn feedback into learning, review, selection, or activation.

## Non-authority boundaries

persistence is not lesson_store write

persistence is not Memory Layer write

persistence is not lesson_candidate creation

persistence is not awakening evidence

Persistence stores trace evidence. It does not grant lesson approval, review decision, selection eligibility, activation, Memory Layer admission, or ontology claims.

## Future implementation boundaries

A future persistence runtime must not:

```text
overwrite existing JSONL rows
silently correct existing trace records
write lesson_store
write Memory Layer
create lesson_candidate
connect to lesson_candidate pipeline
create failure_event
create review decision
create selection eligibility
create activation
call LLM
implement teaching chat loop
implement free text conversation
claim awakening
claim dialogue ability
claim long-term growth
```

## Conclusion

This spec only defines append-only persistence expectations for first_output_trace and mentor_feedback_trace. It does not implement persistence runtime, JSONL writes, lesson_store writes, Memory Layer writes, lesson_candidate creation, or any learning behavior.
