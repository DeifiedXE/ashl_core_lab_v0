# Package 122 / Bounded Multimodal Perception Session Runtime v0

Status: implemented

Package 122 adds a bounded multimodal perception session runtime that aligns Package 121 low-level perception outputs on one monotonic session timeline and injects one low-level perception window into the existing Package 115 Host Body runtime path.

## Implemented Flow

Artifact-backed replay:

1. Read explicit Package 120 `SensorRawArtifact` ids.
2. Compile each artifact through `HardSoftPerceptionPrimitiveCompiler`.
3. Store Package 121 primitive records and `PerceptionReadableData`.
4. Create bounded lane items for camera, screen, microphone, and host-state.
5. Assemble deterministic alignment windows.
6. Apply the low-level event emission policy.
7. Adapt the selected window into the existing `HostBodyEventRecord`.
8. Inject the event into `BoundedEmbodiedSessionRuntime`.
9. Run the actual Package 115 chain to `WAITING_TEACHER_REVIEW`.

This mode is an artifact-backed integration replay. It does not claim simultaneous capture or a real-life synchronized experience.

## Boundaries

The runtime stores ids, hashes, primitive summaries, and trace metadata only. It does not store raw camera pixels, screen pixels, or PCM bytes in multimodal records or TraceEnvelope payloads.

Package 122 creates no:

- object recognition
- OCR
- speech understanding
- speaker identity
- emotion label
- cross-modal semantic binding
- automatic teacher decision
- memory commit
- external control
- first_output
- live scheduler
- open-ended loop

Same-window low-level visual and audio activity means only that both signal families occurred within the configured bounded window.

## CLI

Create a replay manifest:

```powershell
py -3 -m ashl_core_v1.runtime.bounded_multimodal_perception_session_cli create-replay-manifest --state-dir <path> --camera-artifact <id>@100 --screen-artifact <id>@400 --screen-artifact <id>@650 --microphone-artifact <id>@250 --host-state-artifact <id>@0 --output <manifest.json>
```

Run artifact replay:

```powershell
py -3 -m ashl_core_v1.runtime.bounded_multimodal_perception_session_cli run-artifact-replay --state-dir <path> --manifest <manifest.json> --alignment-window-ms 250
```

Inspect:

```powershell
py -3 -m ashl_core_v1.runtime.bounded_multimodal_perception_session_cli show-session --state-dir <path> --session-id <id>
py -3 -m ashl_core_v1.runtime.bounded_multimodal_perception_session_cli show-timeline --state-dir <path> --session-id <id>
py -3 -m ashl_core_v1.runtime.bounded_multimodal_perception_session_cli audit-session --state-dir <path> --session-id <id>
```

## Safe Claim

ASHL Core v1 can place real low-level camera, screen, microphone, and restricted host-state perception data on one bounded replay timeline, construct nonsemantic alignment windows, handle bounded queues and drop records, convert one low-level perception window into the existing Host Body event format, and run it through the actual Package 115 path to the explicit teacher-review boundary.

The required completion run proves runtime integration, not a simultaneous real-world experience.
