# Host Body Read-Only Sensor Event Shell v0

Package 102 adds fixture-only HostBodyEvent records for Qingyin Host Body ports.

It can record low-level demo events for:

- camera fixture events such as `camera_frame_available`, `camera_frame_changed`, `camera_brightness_changed`, and `camera_motion_proxy_changed`
- mic fixture events such as `mic_level_changed`, `mic_peak_detected`, `mic_silence`, and `mic_sustained_noise`
- host idle/status fixture events such as `host_idle`, `host_power_on_observed`, and `host_status_available`

These records are event shells only. They do not connect real hardware, capture images or audio, recognize speech, create semantic vision, influence action selection, bridge into Runtime EventFrames, write memory, create `first_output`, or start a live runtime session.

Safe claim:

ASHL Core v1 can create fixture-only read-only HostBodyEvent records for low-level camera, microphone, and host-idle events, summarize them, audit them, and prepare them for a future Runtime EventFrame bridge while blocking real hardware access, semantic vision, speech recognition, action selection influence, external control, memory-layer writes, automatic learning approval, first_output, live runtime, and production behavior.
