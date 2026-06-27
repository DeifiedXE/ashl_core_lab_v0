# First Output Trace Contract v0.1

## Purpose

This document defines the future `first_output_trace` contract for the test-object stage.
It is a contract document only. It does not implement a runtime, a first_output generator,
a state store, a trace schema runtime, or any lesson_candidate pipeline connection.

Core statement:

```text
first_output_trace is evidence of a first_output event, not proof of awakening.
```

`first_output_trace` records that a first_output event occurred under bounded engineering
conditions. It is not Qingyin awakening, not dialogue ability, and not evidence of long-term
growth.

## Contract Scope

The trace contract is downstream of the Qingyin First Output Runtime Minimal Spec. It describes
what a future trace should preserve when first_output exists.

It must not be interpreted as authorization to:

- implement first_output runtime
- implement first_output trace schema runtime
- implement first_output generator
- connect mentor feedback runtime
- connect lesson_candidate pipeline
- write to lesson_store
- write to Memory Layer

## Relation To First Output Runtime Minimal Spec

The minimal first_output runtime spec names these future fields:

```text
session_id
tick
minimal_state_snapshot
output_generator_source
first_output
first_output_trace
llm_used = false
engineering_stage = "test_object"
```

This contract narrows the trace side only. It does not create these fields in runtime.

## First Output Trace Is Evidence

```text
first_output_trace is evidence of a first_output event, not proof of awakening.
```

The trace proves only that a first_output event was recorded under the declared engineering
stage. It does not prove that Qingyin is awake, self-aware, dialog-capable, or growing.

```text
first_output_trace is record, not authorization.
```

The trace is a record of evidence. It must not authorize learning, memory admission,
runtime activation, or any downstream behavior by itself.

```text
first_output_trace is not learning material by itself.
```

The trace may later become evidence considered by another reviewed pipeline, but it is not
learning material on its own.

## Required Trace Fields

A future trace should preserve at least:

```text
trace_id
trace_type = "first_output_trace"
session_id
tick
phase = "test_object"
engineering_stage = "test_object"
output_id
first_output
output_kind
output_generator_source
core_seed_reference
minimal_state_snapshot_ref
llm_used = false
created_at_or_tick
```

If bounded randomness is used, the trace should also preserve:

```text
randomness_mode
random_seed_ref
randomness_boundary
replay_hint
```

If a deterministic rule produced the output, the trace may preserve:

```text
rule_id
rule_source
```

These are contract fields only. This package does not implement a schema runtime.

## Minimum Fields That Must Not Be Missing

The minimum auditable trace fields are:

```text
trace_id
session_id
tick
first_output
output_generator_source
llm_used
created_at_or_tick
```

If a trace needs correction, the correction must be append-only or version-preserving:

```text
new trace version
correction trace
append-only correction entry
```

`first_output_trace` must be append-only or version-preserving.

```text
first_output_trace must be append-only or version-preserving.
```

## Output Kind Boundary

Conceptual future output kinds may include:

```text
symbol
noise_token
fixed_reflex
seed_pulse
bounded_random
state_echo
```

These names are contract vocabulary only. They do not create an enum or runtime validator.

## LLM Boundary

```text
llm_used must be false for first_output_trace.
```

Allowed future output generator sources may include:

```text
core_seed_rule
deterministic_seed
bounded_randomness
simple_reflex_rule
minimal_state_rule
non_llm_symbolic_generator
```

Prohibited output generator sources include:

```text
llm
chatgpt
openai_api
claude_api
prompt_persona
human_written_sentence
tts_from_llm_text
```

```text
LLM-generated text must not appear as first_output in first_output_trace.
```

An LLM response, prompt persona output, or human-written sentence must not be inserted into
`first_output_trace` as Qingyin's first_output.

## Bounded Randomness Trace

```text
bounded randomness must record enough information for audit.
```

If bounded randomness is used, the trace must preserve enough information to make the source
auditable and, where possible, replayable.

```text
Unbounded randomness must not be recorded as valid first_output source.
```

Unbounded randomness is not an acceptable first_output source for this contract.

## Mentor Feedback Boundary

```text
Mentor feedback is downstream of first_output_trace.
```

The intended future order is:

```text
first_output
-> first_output_trace
-> mentor_feedback_stub
-> feedback_trace
-> lesson_candidate input consideration
```

`mentor_feedback_stub` is not implemented by this contract.

```text
first_output_trace requires mentor feedback before it may be considered for lesson_candidate input.
```

Without mentor feedback or another future reviewed bridge, `first_output_trace` must not become
lesson_candidate input.

## Lesson Candidate Pipeline Boundary

```text
The lesson_candidate pipeline remains downstream of first_output trace and mentor feedback.
```

```text
first_output_trace must not directly create lesson_candidate input.
```

```text
first_output_trace must not bypass failure_event or lesson_candidate validation.
```

`first_output_trace` may become evidence later, but it must not bypass failure_event validation,
lesson_candidate validation, or review boundaries.

## Lesson Store And Memory Layer Boundary

```text
first_output_trace must not write to lesson_store.
first_output_trace must not write to Memory Layer.
```

ASHL Core provides evidence. Qingyin Memory Layers decide memory admission.

## What First Output Trace Does Not Prove

```text
first_output_trace does not prove dialogue ability.
```

```text
first_output_trace does not prove long-term growth.
```

```text
first_output_trace in the test-object stage is engineering verification, not full Qingyin experience.
```

The test-object stage is an engineering prerequisite for future growth. It is not full Qingyin
experience and must not be presented as awakening.

## Explicit Non-Implementation Boundary

This contract does not implement:

- first_output_trace runtime
- first_output trace schema runtime
- first_output generator
- deterministic seed runtime
- bounded randomness runtime
- LLM response generation
- ChatGPT / OpenAI / Claude / any LLM API integration
- teaching chat loop
- mentor feedback runtime
- lesson_candidate pipeline connection
- failure_event automatic builder
- lesson_candidate automatic builder
- Audio Sense / STT / TTS / voice loop
- lesson_store write
- Memory Layer write
- review / lesson / selection / activation / conflict behavior changes
