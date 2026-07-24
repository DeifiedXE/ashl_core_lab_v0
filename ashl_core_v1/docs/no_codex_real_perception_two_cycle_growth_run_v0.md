# Package 123 / No-Codex Real Perception Two-Cycle Growth Run v0

Package 123 adds the critical-path runtime wrapper for the official experiment:

`host_internal_visual_audio_pulse_v0`

The participating lanes are:

- `screen_window`: a native local stimulus window captured through Windows client-area pixels.
- `system_audio_loopback`: the Windows default render endpoint captured through bounded WASAPI loopback and stored as Package 120 audio artifacts.
- `host_state`: the restricted Package 120 host-state adapter.

The camera lane is explicitly `not_participating_by_design`. It is not a missing or failed lane for this experiment.

## Boundary

The stimulus manifest is ground truth for audit only. It is not inserted into `PerceptionReadableData`, `HostBodyEvent`, learning evidence, interpreted memory, working readback, or readback scoring.

Package 123 reuses the actual runtime path:

`Package 120 SensorRawArtifact -> Package 121 primitive -> Package 122 alignment window -> HostBodyEvent -> Package 115 teacher gate -> Package 116/117 approval -> Package 90-92 commit -> working readback -> new process Cycle 2 readback scoring`

No parallel teacher gate, learning pipeline, memory scorer, or raw artifact format is introduced.

## Operational Commands

```text
py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli list-audio-endpoints
py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli preflight --state-dir <path> --render-endpoint default
py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli real-smoke --state-dir <path> --render-endpoint default
py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli transport-soak --state-dir <path> --render-endpoint default
py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli show-transport-soak --state-dir <path>
py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli run-cycle-1 --state-dir <path> --render-endpoint default --require-passed-transport-soak
py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli show-cycle-1-review --state-dir <path> --verbose-windows
py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli show-transport-integrity --state-dir <path> --cycle 1
py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli review-cycle-1 --state-dir <path> --decision approve --reviewer local_teacher --approval-text "I approve this exact low-level observed multimodal pattern only." --confirm
py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli review-cycle-1 --state-dir <path> --decision reject --reviewer local_teacher --pending-review-id <id> --evidence-snapshot-id <id> --evidence-identity <hash> --required-scope through_reviewed_concept_and_working_readback --allowed-interpretation-scope low_level_observed_multimodal_pattern_only --reason <text> --confirm
py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli run-cycle-2 --state-dir <path> --render-endpoint default
py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli show-comparison --state-dir <path>
py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli audit --state-dir <path>
py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli audit-transport-repair --state-dir <path> --rejected-evidence-identity <hash>
```

`guided-run` prints the stepwise commands and terminates. It does not keep one Python process alive across both cycles.

## Package 123-R1 Transport Repair

Package 123-R1 repairs the first Cycle 1 transport defect without creating a new roadmap package. The rejected evidence remains immutable and auditable; it is closed through the Package 116/117 teacher rejection path and must not create reviewed interpretation, memory application data, session commit, or active working readback.

The repaired Cycle 1 flow is:

`capture -> Package 121 compile -> Package 122 prepare transport -> Package 123 transport integrity summary -> integrity pass -> Package 115 teacher gate`

If required-lane drops, required-lane backpressure, capture failures, compile failures, timestamp-order failures, readiness failures, flush failures, or incomplete full alignment windows are detected, Package 123 records transport faults and stops before creating a pending teacher review.

Package 123 uses a local required-lane transport policy:

- required lanes: `screen`, `microphone`, `host_state`
- overflow policy: `abort_run_no_drop`
- host-state sampling interval: `250 ms`
- alignment ownership: half-open `[start, end)` windows
- replay speed: `1.0`

Review output separates source presence, primitive presence, alignment delivery, and salient change. A stable black screen or silent audio chunk is present, compiled, and delivered with `salient_change_present = false`; it is not a missing lane.

## Store

Package 123 records are stored under:

`<state_dir>/package_123_real_perception_v0/package_123.sqlite3`

Raw screen, audio, and host-state artifacts remain in the Package 120 content-addressed artifact store. Package 123 does not copy raw pixels or PCM into its SQLite database.

Package 123-R1 adds append-only metadata tables for readiness, flush, alignment-window coverage, transport faults, transport integrity summaries, transport soak records, rerun lineage, and repair audits. These tables store ids, timestamps, counts, status, artifact refs, primitive refs, and trace refs only.

## Safe Claim On Pass

After a passing audit, ASHL Core v1 has completed one bounded host-internal real perception two-cycle growth run without LLM, Codex runtime, network service, prerecorded fixture, OBS sensor input, hard-coded stimulus recognition, or Qingyin-authored output.

This does not create language understanding, object recognition, speaker identity, time perception, causal understanding, external control, first output, or open-ended autonomy.
