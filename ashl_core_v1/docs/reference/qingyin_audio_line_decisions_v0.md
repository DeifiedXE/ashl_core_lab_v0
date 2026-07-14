# Qingyin Audio Line Decisions v0

Status: Reference
Runtime Impact: None
Created For: Package 120A

## Locked Decisions

- Daily recognition audio does not persist raw PCM by default.
- Grounding audio may persist temporarily with explicit consent and purpose.
- Observed and imagined `AudioPrimitiveRecord` values use one schema.
- Low-level prosody belongs in the AudioPrimitive schema.
- Semantic emotion labels do not belong in AudioPrimitive.
- Package 120A creates no `SpeakerVoiceProfile`.
- Package 120A creates no speaker embedding.
- Package 120A creates no speech-to-text.
- Package 120A creates no speech understanding.
- Package 120A creates no automatic promise or task detection.
- Package 120A creates no automatic retention decision.
- Deletion itself always leaves append-only trace evidence.

## Auditory Event Lane

The auditory event lane may use:

- onset and offset structure
- amplitude envelope
- relative band energy
- rhythm proxies
- relative pitch contour
- pause structure
- harmonicity and noisiness proxies

It does not preserve or interpret speech content.

## Future Speech Content Lane

Speech content remains reserved for a later package with a separate privacy and semantic-memory boundary. Commitments, tasks, exact quotations, and language grounding must not be reconstructed from deliberately content-minimized auditory-event primitives.

## Mentor Recognition Boundary

Package 120A creates no speaker identity, probable mentor label, person recognition, speaker profile, or voice embedding.

Future weak inputs may include coarse pitch band, relative pitch contour, appearance regularity, session context, and relationship context, but Package 120A only defines the schema surface and does not perform recognition.
