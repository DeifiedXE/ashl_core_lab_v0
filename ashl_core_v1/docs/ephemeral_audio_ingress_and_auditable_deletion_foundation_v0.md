# Package 120A / ASHL Core v1 Ephemeral Audio Ingress And Auditable Deletion Foundation Minimal v0

Status: Implemented
Runtime Impact: Bounded local audio ingress foundation only

## Purpose

Package 120A separates microphone handling into two paths.

Recognition ephemeral path:

microphone PCM -> `EphemeralAudioRingBuffer` -> `PerceptionSourceBuffer` -> future Package 121 primitive compiler -> best-effort overwrite of RAM slots.

This path intentionally creates no `SensorRawArtifact`, no content-addressed audio blob, no raw PCM SQLite payload, no temporary audio file, no learning material, and no retention candidate by default.

Grounding capture path:

explicit user consent -> bounded microphone capture or manual excerpt -> `EvidenceAudioExcerpt` -> temporary `SensorRawArtifact` -> explicit service-period metadata -> auditable deletion.

## Ephemeral Scope

The supported claim is:

ASHL Core does not intentionally write `recognition_ephemeral` PCM to its artifact store, SQLite blob fields, or temporary files. The in-process ring buffer is overwritten within its configured retention window and cleared on normal shutdown.

The package does not claim cryptographic RAM erasure, protection from operating-system swap, hibernation images, kernel crash dumps, or forensic memory acquisition.

Recorded scope:

`application_no_persistent_write_best_effort_memory_overwrite`

## New Contracts

- `PerceptionSourceBuffer`: runtime-only audio byte view for future perception compilers.
- `AudioCapturePrivacyPolicy`: provisional recognition-ephemeral policy that blocks raw disk persistence, speaker embedding, absolute pitch persistence, fine spectral persistence, and speech-content interpretation.
- `AudioPrimitiveRecord`: schema-only shared contract for future observed and expected auditory primitives.

Package 120A defines the primitive schema only. It does not compile primitive values.

## AudioPrimitive Boundary

Allowed low-level fields include amplitude envelope, relative band energy, onset/offset structure, rhythm interval pattern, pause intervals, relative pitch contour, coarse pitch band, harmonicity proxy, and noisiness proxy.

Forced-null semantic fields:

- `semantic_label`
- `speech_content`
- `speaker_identity`
- `emotion_label`

No `SpeakerVoiceProfile`, speaker embedding, speech-to-text, promise detection, task detection, or semantic emotion label is created.

## Manual Excerpts

Manual excerpts require:

- explicit trigger source: `manual_teacher_command`
- requester: `user`
- requester role: `project_owner`
- explicit consent record
- allowed purpose
- bounded pre-roll and post-roll window

Allowed purposes:

- `grounding_example`
- `counterexample`
- `confusion_case`
- `important_source_evidence`
- `speaker_enrollment_candidate`
- `expression_evidence_candidate`

The final two remain candidates only and create no speaker or expression concept.

## Deletion Governance

Deletion is append-only. It removes recoverable waveform bytes when authorized, but preserves artifact metadata, content hash, source trace refs, deletion request, and deletion record.

The original `SensorRawArtifact` row is not updated.

Content-addressed blobs can be shared by multiple artifact rows. Deleting one artifact only removes the blob when no live artifact or retention reference remains. Earlier tombstoned artifacts remain authorized when a later last-reference deletion physically removes the shared blob.

The store audit distinguishes:

- accidental missing blob -> `blocked_missing_blob`
- authorized waveform deletion -> `authorized_waveform_deletion`

## TraceEnvelope Integration

New trace layers:

- `audio_ingress_control_trace`
- `audio_retention_governance_trace`

New record kinds include ephemeral audio sessions, lifecycle events, chunk descriptors, consent, excerpt requests, excerpts, retention candidates, retention references, deletion requests, and deletion records.

No TraceEnvelope contains raw PCM bytes or base64 audio.

## Non-Goals

Package 120A does not create audio primitive values, an audio compiler, speaker profiles, speech understanding, commitment detection, automatic excerpt selection, automatic retention, automatic deletion, memory writes, sensor-driven HostBodyEvents, external control, first_output, scheduler behavior, GCMC, CL, or any consciousness claim.

## Safe Claim

ASHL Core v1 can receive daily microphone PCM through a bounded RAM-only ring buffer without intentionally writing the waveform to its artifact store, SQLite blob fields, or temporary files. A user can explicitly extract bounded audio evidence excerpts with consent and later delete stored waveform bytes through a hash-bound append-only deletion process that preserves provenance and respects shared content-addressed blob references.
