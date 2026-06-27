# Internal Auditory Feedback Design Supplement v0

## Purpose

Introduce an internal auditory feedback path for Qingyin.

This document extends the Audio Cochlea Decoder and Vocal Organ Engine designs. The purpose is not inner speech, self-awareness, or internal dialogue. The purpose is to allow Qingyin to observe the acoustic consequences of her own vocal output.

## Core Concept

External hearing answers:

```text
What happened in the environment?
```

Internal hearing answers:

```text
What sound did I just produce?
```

The system should treat self-generated sound as observable evidence.

## High-Level Architecture

```text
Vocal Intent
-> Phoneme Planner
-> Vocal Synth Engine
-> Generated Audio
-> Internal Auditory Feedback
-> Audio Cochlea Decoder
-> Audio Evidence
-> Prediction Comparison
```

## Design Goal

Future Qingyin may be able to:

```text
observe self-generated sound
distinguish self-generated sound from external sound
compare expected sound and observed sound
produce traceable vocal evidence
support future vocal refinement
```

without requiring language understanding.

## Self-Generated Audio Source

Internal auditory feedback receives audio directly from the vocal system.

Example:

```text
phoneme_plan
-> generated waveform
-> internal hearing input
```

This input is treated as sound evidence. It is not treated as language.

## Audio Source Classification

Every auditory observation should include origin metadata.

Examples:

```json
{
  "source": "self_vocal"
}
```

```json
{
  "source": "external"
}
```

Future systems may support additional categories.

```json
{
  "source": "sandbox_environment"
}
```

## Expected vs Observed Vocal Comparison

Future vocal generation may produce an expected output model.

Example:

```json
{
  "expected_phoneme": "ma"
}
```

Observed result:

```json
{
  "observed_phoneme": "mu"
}
```

Comparison:

```json
{
  "vocal_prediction_error": 0.32
}
```

This value remains observational. No automatic correction is permitted.

## Internal Audio Evidence

Example:

```json
{
  "source": "self_vocal",
  "duration_ms": 430,
  "dominant_band": 520,
  "volume": 0.48,
  "prediction_error": 0.11
}
```

Evidence remains bounded and traceable.

## Trace Requirements

All internal auditory observations should remain observable.

Example:

```json
{
  "trace_type": "internal_audio_feedback",
  "source": "self_vocal",
  "voice_profile": "qingyin_child_v0",
  "prediction_error": 0.08,
  "timestamp": "..."
}
```

Trace is evidence only. Trace is not learning, memory, or approval.

## Future Vocal Exploration

Internal auditory feedback may support sandbox-only vocal experimentation.

Example:

```text
generate sound A
-> observe sound A

generate sound B
-> observe sound B

compare
-> trace
```

This process does not imply learning. Human review remains required for any future memory or lesson pathway.

## Non-Goals

The following are explicitly out of scope:

```text
inner speech
silent internal narration
self-dialogue
consciousness claims
language reasoning
automatic learning
memory creation
personality generation
```

## Boundary Rules

The following must remain true:

```text
hearing own voice != self-awareness
internal auditory feedback != inner monologue
vocal prediction error != learning
trace != memory write
sound comparison != language understanding
self-generated audio != self-model
```

## Future Integration Targets

Potential future integrations:

```text
vocal organ engine
audio cochlea decoder
attention system
doubt system
verification planning
sandbox vocal experimentation
```

Each integration requires independent boundary review.

## Success Condition

The design is considered successful when future Qingyin can:

```text
produce sound
observe the produced sound
distinguish self-generated sound from external sound
compare expected and observed output
record traceable evidence
```

without requiring language understanding or autonomous learning.

## Summary

Internal Auditory Feedback is intended to function as Qingyin's internal hearing pathway.

The system observes self-generated vocal output, routes it through the auditory pipeline, and produces bounded evidence suitable for future sandbox experimentation while remaining fully observable and reviewable.
