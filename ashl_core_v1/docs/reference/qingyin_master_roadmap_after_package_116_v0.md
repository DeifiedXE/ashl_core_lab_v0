# Qingyin Master Roadmap After Package 116 v0

Status: Reference
Runtime Impact: None
Created For: Package 117 repair baseline
Updated Through: Package 122A architecture, module and roadmap gap reconciliation

## Current Baseline

Package 115 created a bounded in-memory embodied session runtime that runs from fixture Host Body event to `WAITING_TEACHER_REVIEW`.

Package 116 created teacher-gated session resume and commit:

Host Body evidence awaiting review -> explicit teacher decision -> Package 90-92 learning path -> reviewed interpretation commit -> persisted working readback.

Package 117 completed the identity and approval-scope repair around that path before the no-Codex two-cycle fixture growth run.

Package 118 completed the first no-Codex, fixture-only, teacher-gated, cross-process two-cycle growth run.

Package 119 sealed the stored Package 118 run as the no-Codex fixture embodied growth-loop milestone.

Package 120 added bounded foreground real host sensor ingress for camera, screen, microphone, and restricted host-state adapter-output samples, with immutable content-addressed raw artifact storage and `raw_sensor_trace` TraceEnvelope metadata.

Package 120A added the audio-specific foundation: recognition-mode microphone PCM can remain in a bounded RAM-only ring buffer without intentional raw disk persistence, while explicit grounding/evidence excerpts can be materialized with consent and later deleted through hash-bound append-only deletion records.

Package 121 added deterministic low-level perception primitive compilation for stored camera/screen/microphone/host-state artifacts and ephemeral microphone source buffers. It creates visual, audio, and host-state primitives plus `PerceptionReadableData`, but still creates no semantic vision, speech understanding, speaker identity, learning, memory write, or action influence.

Package 122 added a bounded multimodal perception session runtime. It can replay real Package 120 artifacts on an explicit deterministic integration timeline, compile them through Package 121, assemble nonsemantic alignment windows, convert one low-level window into the existing Host Body event format, and run the actual Package 115 bounded embodied session path to `WAITING_TEACHER_REVIEW`. The required completion path is artifact-backed integration replay and does not claim simultaneous real-world experience.

Package 122A added an executable repo architecture scanner, module capability ledger, interface graph, store/CLI/test inventory, gap and bottleneck analysis, and conflict-free Package 123+ route. It changed no Qingyin runtime behavior.

## Current Safe Chain

Fixture Host Body event
-> Runtime EventFrame
-> Host Body internal action
-> Home surface link
-> learning evidence
-> pending teacher review
-> exact teacher decision target binding
-> Package 90-92
-> interpreted memory commit
-> working readback commit

## Immediate Schedule

- Package 117 / Session Evidence Identity And Teacher Approval Scope Repair - completed
- Package 118 / No-Codex Two-Cycle Fixture Growth Run - completed
- Package 119 / No-Codex Fixture Growth Loop Milestone Audit - completed
- Package 120 / Real Host Sensor Ingress And Raw Artifact Store - completed
- Package 120A / Ephemeral Audio And Auditable Deletion Foundation - completed
- Package 121 / Hard-Soft Perception Primitive Compiler - completed
- Package 122 / Bounded Multimodal Perception Session Runtime - completed
- Package 122A / Architecture, Module And Roadmap Gap Reconciliation - completed
- Package 123 / No-Codex Real Perception Two-Cycle Growth Run - next
- Package 124 / Real Host Perception Growth Loop Milestone - later

## Authoritative Route After Package 124

The Package 122A generated registry supersedes conflicting placeholder routes
that reused Package 125-129 for both active perception and auditory work.

- 125-132: Active Perception And Attention, including visual/audio temporal continuity, focus state, recapture/relisten actions, novelty/uncertainty integration, grounded auditory event concepts, and auditory predictive recognition.
- 133-140: Persistent Self-State And Drive.
- 141-148: Bounded Thought Engine.
- 149-156: Self-Proposed Verification.
- 157-164: First Non-LLM Output.
- 165-172: Daily No-Codex Runtime.
- 173+: Selective audio retention governance, optional Speaker Profile decision, and speech content / commitment / expression memory.

For the detailed generated route, see `package_123_to_daily_runtime_revised_route_v0.md`.

## Later Milestones

- Real low-level sensor ingress is now bounded, foreground-only, read-only raw adapter-output capture
- Real camera and microphone adapters remain raw-capture only and do not create semantic perception
- Daily recognition audio no longer needs to become a stored waveform artifact
- Manual audio evidence excerpts remain nonsemantic and deletable with append-only deletion provenance
- Real sensor safety and noise audit before semantic perception work
- Real sensor bytes are now readable only as low-level deterministic primitives, not semantic objects or speech content
- Real low-level perception records can now enter a bounded Host Body session through a nonsemantic multimodal alignment window

## Boundaries

Still not created:

- automatic teacher decisions
- unrestricted memory promotion
- teacher-approved real perception commit
- cross-session real perception readback
- real sensor semantic perception
- semantic vision
- speech recognition
- speaker identification
- speech understanding
- automatic audio retention
- Task Engine external action influence
- external control
- OS, mouse, keyboard, browser, file, network, shell, or API operation
- first_output
- voice output
- live scheduler
- open-ended loop
- Thought Engine runtime
- GCMC runtime
- CL token
- Concept Compiler
- Pattern Miner
