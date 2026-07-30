# Bounded Re-Sampling And Listen-Again Internal Action v0

Status: Completed by Package 126

## Capability

Package 126 adds one explicitly authorized fresh-world reacquisition after a
parent observation window has completed cleanly. It registers exactly two new
internal perception action kinds:

- `capture_again`: reacquire screen, system audio, and host state with the same
  target, region, endpoint, configuration, privacy policy, compilers, and
  required-lane policy.
- `listen_again`: reacquire system audio and host state with the same endpoint,
  audio configuration, `recognition_ephemeral` policy, compiler contract, and
  clock-domain names. Screen and camera remain absent by design.

Each chain permits one child window of at most 2.5 seconds, a parent-to-child
gap of at most 5 seconds, and a total chain duration of at most 10 seconds.
Authorization is explicit, local-operator-bound, and expires with the chain.

## Package 125 Distinction

Package 125 operates while one observation window is still active. It keeps the
same screen, audio, and host-state capture sessions open, atomically extends
their shared deadline once, and does not reopen a source.

Package 126 starts only after a parent window has completed and flushed. It
creates a distinct child observation window, runtime session, perception
session, alignment session, and sensor capture-session IDs. The canonical plan,
physical targets, configuration, privacy policy, and compiler versions remain
equal. An explicit external-gap record separates the windows; their timestamps
and evidence are never concatenated or merged.

## Evidence Chain

The append-only Package 126 chain is:

1. Completed parent-window reference and canonical sampling-plan identity
2. Explicit authorization and reacquisition request
3. Deterministic eligibility decision
4. Canonical Host Body internal perception action
5. New child sensor sessions and observation-window state
6. Package 121 low-level primitive compilation
7. Package 122 live compiled-lane alignment and flush record
8. Package 124A temporal bundle and cross-window gap
9. Ephemeral audio deletion verification
10. Child evidence summary and nonsemantic effect comparison
11. Package 112 score-equivalence record
12. Package 126 audit

The parent remains immutable. Failed, cancelled, and interrupted attempts remain
visible. A second reacquisition in the same chain is blocked, so no third
window or recurring scheduler exists.

## Real Verification

`host_internal_same_plan_capture_again_v0` proves that two separate 2.5-second
multimodal windows use equal HWND target, screen region, render endpoint,
configuration, privacy, compiler, and plan hashes while all screen, audio,
host-state, perception, observation, and alignment session identities differ.
The child contains new low-level evidence from all three participating lanes.

`host_internal_listen_again_ephemeral_v0` proves a separate audio and host-state
child capture. WASAPI samples enter the Package 120A RAM-only
`recognition_ephemeral` ring, Package 121 emits only an AudioPrimitive, and the
ring is overwritten and cleared. No raw waveform, transient file,
EvidenceAudioExcerpt, RetentionCandidate, transcript, speaker profile, voice
embedding, or recognition result remains.

Both real runs require zero required-lane drops, backpressure faults, capture
failures, compile failures, and remaining flush records. Operator event
delivery failures are append-only and prevent a false audit pass.

## Boundaries

Package 126 does not generate an autonomous request, evaluate evidence
sufficiency, select focus, create uncertainty or novelty signals, use the
Thought Engine, read or write memory, change Package 112 scoring, create output,
control the host, recognize an object or sound, identify a speaker, transcribe
language, or claim subjective listening.

The external stimulus fixture can create a second real event for audit, but its
schedule is inspected only after the runtime result is frozen. It cannot choose
the action or fabricate a primitive.

DLM-0 / Q-M0 remains a read-only completed audit. Package 126 imports no
D-Laplace component, migrates no organ, and does not implement DLM-1.

## Safe Claim

ASHL Core v1 can close one bounded observation and, after an explicit local
authorization, open one new bounded sample using the same sensory plan.
`listen_again` means acquiring fresh system audio from the world, not replaying
or recompiling an old recording. The second sample is linked to the first
without pretending that the external gap did not occur.

Package 127, Internal Perception Focus Shift, is next. DLM-1 remains scheduled
only after Package 132.
