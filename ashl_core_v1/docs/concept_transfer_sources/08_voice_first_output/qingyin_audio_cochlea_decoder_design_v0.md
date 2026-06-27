# Qingyin Audio Cochlea Decoder Design v0

## Purpose

Define a future auditory architecture for Qingyin.

The purpose of this system is not speech recognition, transcription, conversation, or language understanding. The purpose is to describe a future hearing organ capable of detecting, filtering, predicting, and attending to acoustic events.

## Core Concept

Qingyin should not begin with language. Qingyin should begin with hearing.

The system should first answer:

```text
something happened
where did it happen
how loud was it
did it change
was it expected
```

before answering:

```text
what was said
```

## Design Goal

Future Qingyin may be able to:

```text
detect sound
track acoustic changes
select auditory focus
form auditory predictions
detect prediction mismatch
create traceable evidence
```

without requiring speech recognition.

## Non-Goals

The following are explicitly out of scope:

```text
conversation
chatbot behavior
language understanding
automatic transcription
speaker identity recognition
emotion detection
production-world surveillance
consciousness claims
```

## High-Level Architecture

```text
Audio Input
-> Cochlea Decoder
-> Acoustic Feature Layer
-> Audio Focus Layer
-> Audio Prediction Layer
-> Evidence / Trace
```

## Layer 1: Audio Input

Purpose: receive acoustic signals.

Potential future sources:

```text
microphone
sandbox audio
simulated environment audio
recorded sound stream
```

Input source is intentionally unspecified.

## Layer 2: Cochlea Decoder

Purpose: convert raw sound into low-level perceptual features.

Example outputs:

```text
volume
frequency band
duration
direction
rhythm
continuity
```

Example:

```json
{
  "volume": 0.72,
  "dominant_band": 450,
  "duration_ms": 800,
  "continuous": true
}
```

No semantic interpretation exists at this layer.

## Layer 3: Acoustic Feature Layer

Purpose: convert low-level signals into symbolic auditory evidence.

Examples:

```text
sudden
continuous
repeating
periodic
high_frequency
low_frequency
approaching
departing
```

Example:

```text
footsteps-like signal
-> repeating
-> approaching
-> rhythmic
```

No object label is produced.

## Layer 4: Audio Focus Layer

Purpose: select which auditory events deserve attention.

Example environment:

```text
air conditioner
keyboard
fan
footsteps-like signal
voice-like signal
```

Focus selection may produce:

```text
focus_target = event_7
```

Selection does not imply understanding. Focus only indicates priority.

## Layer 5: Audio Prediction Layer

Purpose: predict future auditory events.

Example:

```text
tick
tick
tick
```

System predicts:

```text
next_tick
```

Observed:

```text
tick
tick
crash
```

Result:

```text
prediction_error
```

Prediction error becomes evidence. Prediction error is not learning and is not memory.

## Audio Evidence

Example evidence record:

```json
{
  "feature": "approaching",
  "confidence": 0.74,
  "focus_priority": 0.81,
  "prediction_error": 0.12
}
```

Evidence remains observational. Evidence does not create behavior directly.

## Trace Requirements

All auditory processing should remain observable.

Trace example:

```json
{
  "audio_source": "sandbox",
  "focus_target": "event_7",
  "feature_set": [
    "repeating",
    "approaching"
  ],
  "prediction_error": 0.24
}
```

Trace is evidence only. Trace is not approval, memory, or runtime action.

## Future Semantic Layer

A future semantic layer may exist.

Possible future integrations:

```text
speech recognition
transcription
language parsing
speaker identification
```

These systems are outside this design. The cochlea architecture must remain useful even if semantic processing is disabled.

## Future Integration Targets

Potential future connections:

```text
attention system
visual focus system
doubt system
verification planning
sandbox candidate ordering
idle continuity
```

Each integration requires independent boundary review.

## Boundary Rules

The following must remain true:

```text
hearing != language understanding
acoustic features != object recognition
focus != belief
prediction != knowledge
prediction error != learning
trace != memory write
audio observation != production-world action
```

## Success Condition

The design is considered successful when future Qingyin can:

```text
detect sound
extract acoustic features
choose an auditory focus
form simple predictions
detect prediction mismatch
produce traceable evidence
```

without requiring language understanding.

## Summary

Qingyin Audio Cochlea Decoder is intended to function as an auditory organ rather than a speech recognition system.

The architecture focuses on perception, attention, prediction, and evidence generation while remaining fully sandboxed and bounded.
