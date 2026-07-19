# Package 122B / Non-LLM Local Output Surface And Operator Console Foundation v0

Status: Implemented
Runtime Impact: Operator console store and local output transport only

## Purpose

Package 122B adds the local operator-facing upper console foundation for Qingyin Home. It provides a stable view-model for runtime status, microphone/camera indicators, output-volume preference, hardware settings, a local text timeline, local text input records, raw output-token transport, output cancellation, mute/rate-limit/failure reporting, a status log, a JSON event stream, and reserved neutral sound-pattern descriptors.

This package does not create Qingyin's first output. Fixture token dispatch is visibly marked `fixture_only` and `qingyin_authored = false`.

## Boundaries

- Operator status messages are system translations, not Qingyin language.
- User text is stored as `received_unprocessed` and `not_grounded`.
- Raw output tokens `T00` through `T15` have no semantic label or predefined meaning.
- Reserved sound patterns `P00` through `P07` have no semantic label or predefined meaning, and sound output remains disabled by policy.
- Output dispatch transports a supplied intent; it does not choose tokens.
- Hardware preferences do not open camera or microphone devices.
- No sensor artifact, perception primitive, learning record, memory record, teacher decision, external control, scheduler, LLM, or network use is created.

## Store

The local operator console store is:

`<state_dir>/local_operator_console_v0/operator_console.sqlite3`

Tables:

- `operator_console_snapshots`
- `hardware_enable_preferences`
- `output_volume_states`
- `external_text_inputs`
- `text_timeline_entries`
- `raw_output_sequences`
- `output_intents`
- `output_dispatch_results`
- `output_cancellations`
- `status_log_entries`
- `operator_json_events`
- `output_rate_limit_policies`

The store does not contain raw camera frames, raw PCM, perception primitive payload copies, or memory payload copies.

## Preview

The static schema-driven preview is:

`ashl_core_v1/ui_preview/qingyin_home_upper_console_preview_v0.html`

It contains the required top status bar, text timeline, text input, status log, and separated Developer Test Controls for fixture tokens only.

## CLI

Primary CLI:

`py -3 -m ashl_core_v1.runtime.local_operator_console_cli`

Commands:

- `show-console`
- `show-total-state`
- `set-camera-preference`
- `set-microphone-preference`
- `set-output-volume`
- `show-hardware-settings`
- `submit-text`
- `dispatch-fixture-token`
- `cancel-output`
- `set-output-muted`
- `show-status-log`
- `stream-json-events`
- `audit-console`

Guided teacher console aliases are available under `home-console-*`. These commands are operational controls and do not create teacher approvals or learning decisions.

## Safe Claim

ASHL Core v1 now has a local operator console foundation that can show actual runtime and hardware status, store local user text as unprocessed input, display fixture or future runtime raw output tokens with explicit provenance, and maintain a separate technical status log and JSON event stream. The output dispatcher supports cancellation, mute state, output volume, rate limits, and failure reporting.

No token, sound pattern, or text is assigned a Qingyin meaning. No Qingyin-authored first output is created.
