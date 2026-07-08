# Host Body Event Runtime EventFrame Bridge v0

Package 103 maps fixture-only read-only HostBodyEvent records into bounded Runtime EventFrame bridge records.

Allowed v0 mappings:

- `camera_low_level_event` -> `host_camera_event` -> `sense_event` -> `sense_interface`
- `mic_low_level_event` -> `host_mic_event` -> `sense_event` -> `sense_interface`
- `host_idle_event` -> `host_idle_event` -> `runtime_event` -> `runtime`
- `host_status_event` -> `host_status_event` -> `state_event` -> `state_engine`

The bridge produces record-only RuntimeEventFrame-compatible evidence and adapter-only dispatch links. It does not connect real sensors, create semantic interpretation, select actions, call live handlers, start a live runtime session, write memory, or create `first_output`.

Safe claim:

ASHL Core v1 can map fixture-only read-only HostBodyEvent records into bounded Runtime EventFrame bridge records, route low-level camera and microphone events as Sense EventFrames, route host idle events as Runtime EventFrames, and create adapter-only dispatch links while blocking real hardware access, semantic vision, speech recognition, action selection influence, external control, memory-layer writes, automatic learning approval, first_output, live runtime sessions, live engine invocation, dynamic scheduling, and production behavior.
