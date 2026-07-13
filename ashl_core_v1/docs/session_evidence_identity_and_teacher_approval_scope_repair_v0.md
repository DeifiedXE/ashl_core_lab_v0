# Session Evidence Identity And Teacher Approval Scope Repair v0

Status: Implemented in Package 117
Runtime Impact: Teacher-gated session resume/commit repair
Scope: Exact evidence identity, approval scope, runtime capability profile, and trace collision policy

## Purpose

Package 117 repairs the Package 116 resume path so a teacher decision is bound to one immutable Host Body learning-evidence snapshot. The same evidence identity is preserved through the existing Package 90-92 learning path, interpreted memory commit, and working readback commit.

The repaired invariant is:

pending review evidence identity = teacher decision target identity = Package 90 input identity = Package 91 refinement identity = Package 92 ReviewedConcept identity = interpreted commit identity = working readback identity.

## Evidence Snapshot

`SessionLearningEvidenceSnapshot` stores immutable reviewable evidence metadata:

- `evidence_snapshot_id`
- `evidence_identity_sha256`
- `canonical_payload_sha256`
- `session_id`
- `root_event_id`
- `source_event_id`
- source Package 108/109 record ids
- `source_trace_refs`

The canonical identity payload excludes teacher decisions, ReviewedConcept fields, memory commit fields, raw camera bytes, raw audio bytes, mutable Python object references, runtime instance ids, and unrelated timestamps.

## Approval Scope

Teacher approval is explicit. Allowed scopes are:

- `feedback_candidate_only`
- `through_concept_candidate`
- `through_reviewed_concept`
- `through_reviewed_concept_and_working_readback`

Resume-and-commit requires `through_reviewed_concept_and_working_readback`. A narrower approval can be recorded, but it pauses the session and creates no ReviewedConcept commit or working readback commit.

## Canonical Adapter

The runtime uses `adapt_session_evidence_to_learning_feedback_candidate(...)` instead of reconstructing a fixed uncertainty candidate. Host Body evidence themes remain distinct, including `runtime_bridge_deferred` and `interesting_event_marked`.

Unsupported evidence is blocked. It is not relabeled as uncertainty.

## Identity Sidecars

`LearningPipelineEvidenceIdentityBindingRecord` binds each downstream output to the same evidence identity:

- learning feedback candidate
- teacher review application
- concept candidate draft
- concept candidate refinement
- reviewed concept
- memory learning trace
- memory routing trace
- memory application data
- working readback commit
- reviewed interpretation commit

The interpreted commit and active working readback metadata carry the same `source_evidence_snapshot_id` and `evidence_identity_sha256`.

## Runtime Capability Profile

`RuntimeCapabilityProfile` is built once and injected into `BoundedEmbodiedSessionRuntime`. Package 115 runtime hot path no longer imports or calls demo milestone builders.

## Trace Collision Policy

Duplicate trace ids are no longer silently accepted:

- Same `trace_id` and same canonical trace identity: accepted as idempotent replay.
- Same `trace_id` and different canonical trace identity: raises `TraceIdentityCollisionError`.

Raw trace remains append-only and unsummarized during service period. `concept_id` is not embedded into raw history.

## Store v1

`ashl_teacher_gated_session_store` schema v1 adds:

- `learning_evidence_snapshots`
- `teacher_decision_target_bindings`
- `learning_pipeline_identity_bindings`
- `interpretation_provenance_bindings`
- `runtime_capability_profiles`

v0 stores are migrated safely with a beside-the-database backup. Legacy waiting sessions without evidence snapshots are not automatically assigned invented evidence.

## Safe Claim

ASHL Core v1 can bind a teacher decision to one exact immutable Host Body learning-evidence snapshot and preserve that evidence identity through Package 90-92, interpreted memory commit, and working readback commit.

## Forbidden Claim

- Qingyin can self-approve learning.
- Qingyin can widen approval scope automatically.
- Qingyin can commit unreviewed evidence.
- Qingyin can silently accept conflicting trace ids.
- Qingyin has a no-Codex two-cycle growth run in this package.
- Qingyin has real perception.
- Qingyin has external control.
- Qingyin has first_output.
- Qingyin has live autonomy.

