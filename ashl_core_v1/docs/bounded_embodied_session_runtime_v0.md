# Bounded Embodied Session Runtime v0

Status: Package 115 / ASHL Core v1

Package 115 creates one in-memory bounded embodied session runtime. It is not a dashboard and does not persist state. It drives the existing Host Body package functions in order, keeps one `session_id`, appends one canonical `TraceEnvelope` timeline, and stops at `WAITING_TEACHER_REVIEW`.

## Runtime Path

Fixture HostBodyEvent -> Runtime EventFrame bridge -> bounded dispatch adapter -> Host Body trace history lane -> internal-only Host Body action choice -> internal action result -> Qingyin Home read-only surface links -> Host Body learning evidence packet -> existing LearningFeedbackCandidate review adapter input -> pending teacher review.

The normal demo uses `camera_unknown_low_level_event` and selects `mark_uncertain`. The deferred bridge demo uses `runtime_bridge_deferred` and selects `request_teacher_review` through the existing Package 106 deterministic ordering.

## TraceEnvelope Contract

`TraceEnvelope` is the v1 canonical trace wrapper:

- `trace_schema_version = ashl_trace_envelope_v1`
- one `session_id`
- one monotonic `sequence_index`
- non-decreasing `monotonic_tick`
- `append_only = true`
- `time_aligned = true`

Raw trace envelopes contain only event/state/action/outcome data. Raw trace rejects `concept_id`, `reviewed_concept_id`, `MemoryLearningTrace` ids, and interpretation summaries.

Derived or interpreted envelopes must use `source_trace_refs`. The append-only store rejects duplicate trace ids, missing refs, future refs, and cross-session refs.

## Boundaries

Package 115 does not create teacher decisions, session resume, ReviewedConcepts, memory commits, long-term memory, Core Memory, file persistence, real hardware access, external control, first_output, a live scheduler, open-ended loops, Thought Engine behavior, or production behavior.

Abort is not deletion. Abort appends a runtime-control envelope, preserves raw trace, leaves pending teacher reviews unresolved, and marks the session `ABORTED`.

## Safe Claim

ASHL Core v1 can run one real in-memory bounded embodied session from a fixture Host Body event through Runtime EventFrame handling, Host Body internal action choice, Qingyin Home read-only surface linkage, and teacher-reviewable learning evidence creation, using one shared session state and one canonical append-only TraceEnvelope timeline, then stop at `WAITING_TEACHER_REVIEW`.

## Next Package

Package 116 / ASHL Core v1 Teacher-Gated Session Resume And Commit Minimal v0.

