# Qingyin Vocal Organ Engine Design v0

## Purpose

Define a future vocal organ architecture for Qingyin.

The goal is not chatbot speech, TTS dialogue, or language generation. The goal is to describe a future vocal organ that could transform internal state, pressure, attention, uncertainty, and future language structures into generated sound.

This design does not grant language understanding, learning, consciousness, autonomy, or production-world capability.

## Core Concept

Qingyin should not rely on fixed audio files whenever possible. The proposed future flow is:

```text
internal state
-> vocal intent
-> phoneme planning
-> vocal synthesis
-> generated sound
```

The vocal system should behave more like a biological vocal tract than a sound effect player.

## Design Goal

Future Qingyin may be able to produce:

```text
sound
phoneme-like structures
prosody
pauses
hesitation
exploratory vocalization
```

This should not require predefined spoken sentences.

## Non-Goals

The following are explicitly out of scope:

```text
chatbot response generation
LLM speech generation
conversational AI
semantic language understanding
self-awareness claims
consciousness claims
production-world communication
```

## High-Level Architecture

```text
Internal State
-> Vocal Intent Layer
-> Phoneme Planner
-> Prosody Planner
-> Vocal Synth Engine
-> Audio Output
-> Trace
```

## Layer 1: Vocal Intent

Purpose: convert internal state into vocal goals.

Example input signals:

```text
attention spike
prediction mismatch
uncertainty
success signal
curiosity
idle reactivation
```

Possible outputs:

```text
query
notice
hesitation
confirmation
exploration
orientation
```

Example:

```text
prediction_error_high -> vocal_intent=query
```

## Layer 2: Phoneme Planner

Purpose: generate candidate phoneme-like structures.

Example units:

```text
m
a
u
i
n
h
```

Combined examples:

```text
m-a
m-u
n-a
h-m
```

No semantic meaning is required. Generated sound may resemble:

```text
hmm
mm
na
ah
```

without representing language.

## Layer 3: Prosody Planner

Purpose: determine:

```text
pitch
duration
pause
intensity
rhythm
```

Examples:

```text
query -> rising pitch
hesitation -> longer pause
notice -> short duration
success -> soft upward ending
```

## Layer 4: Vocal Synth Engine

Purpose: convert phoneme plan and prosody plan into audio.

Inputs:

```text
voice_profile
phoneme_sequence
pitch_curve
breath_level
duration
```

Output:

```text
generated waveform
```

Future implementations may use:

```text
parametric synthesis
neural synthesis
hybrid synthesis
```

No implementation is required at this stage.

## Voice Profile

Voice profile defines:

```text
base pitch
formant characteristics
breathiness
brightness
resonance
```

Example:

```text
qingyin_child_v0
```

Voice profile changes sound identity. Voice profile does not contain language.

## Vocal Exploration

Future sandbox-only capability:

```text
generate sound
observe sound
compare sound
store evidence
```

Example:

```text
sound_a
sound_b
-> compare
-> trace
```

This would allow experimentation with vocal output without requiring language.

## Trace Requirements

Every generated sound should remain observable.

Example trace fields:

```text
vocal_intent
phoneme_plan
prosody_plan
voice_profile
generated_output_id
timestamp
```

Trace is evidence only. Trace is not approval, learning, memory write, or runtime identity.

## Boundary Rules

The following must remain true:

```text
vocal output != language understanding
phoneme generation != conversation
voice profile != personality
generated sound != consciousness
vocal exploration != learning approval
trace != memory write
sound production != production-world action
```

## Future Integration Targets

Potential future connections:

```text
attention system
doubt system
pressure system
sandbox action system
idle/active continuity
memory influence preview
```

These integrations require separate boundary review.

## Success Condition

The design is considered successful when future Qingyin can:

```text
receive vocal intent
generate phoneme structures
apply prosody
produce sound
record trace
```

without requiring predefined audio clips or chatbot-generated text.

## Summary

Qingyin Vocal Organ Engine is intended to function as a vocal organ rather than a speech player.

The future system should be able to transform internal state into generated sound through phoneme planning, prosody planning, and vocal synthesis while remaining fully sandboxed and bounded.
