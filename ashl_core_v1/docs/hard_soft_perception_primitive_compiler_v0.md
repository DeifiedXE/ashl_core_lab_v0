# Package 121 / ASHL Core v1 Hard-Soft Perception Primitive Compiler Minimal v0

Status: implemented

## Purpose

Package 121 compiles bounded real sensor input into deterministic, low-level perception primitives and `PerceptionReadableData`.

Inputs:

- stored `SensorRawArtifact` records from Package 120
- RAM-only microphone `PerceptionSourceBuffer` windows from Package 120A

Outputs:

- `VisualFramePrimitiveRecord`
- `VisualChangePrimitiveRecord`
- observed `AudioPrimitiveRecord`
- `HostStatePrimitiveRecord`
- `PerceptionReadableData`
- append-only source/compilation/replay/trace records

## Boundaries

The compiler is deterministic signal processing only.

It does not create:

- object recognition
- OCR or text recognition
- speech recognition or speech understanding
- speaker identity
- emotion labels
- semantic labels
- sensor-driven HostBodyEvent records
- learning material
- teacher review
- memory writes
- action influence
- external control
- first_output

## Stored Artifact Flow

`SensorRawArtifact`
-> content-addressed blob verification
-> readonly `PerceptionSourceBuffer`
-> primitive
-> `PerceptionReadableData`
-> source primitive link
-> perception TraceEnvelope

The perception store does not copy raw sensor blobs.

## Ephemeral Audio Flow

RAM-only microphone buffer
-> readonly `PerceptionSourceBuffer`
-> observed `AudioPrimitiveRecord`
-> `EphemeralPerceptionCompilationReceipt`
-> `PerceptionReadableData`

The ephemeral path creates no `SensorRawArtifact`, content-addressed audio blob, raw temporary file, or source content hash.

## Replay

Stored artifact compilations can be replayed through the same compiler version and compiler configuration when the source blob is still available.

Ephemeral or physically deleted sources report `source_not_available`; missing media is never reconstructed.

## Safe Claim

ASHL Core v1 can deterministically compile camera/screen pixels, stored microphone PCM, ephemeral RAM-only microphone PCM, and restricted host-state JSON into low-level perception primitives and `PerceptionReadableData`.

The output remains nonsemantic signal structure only.
