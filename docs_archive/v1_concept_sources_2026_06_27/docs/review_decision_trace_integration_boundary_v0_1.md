# ASHL Core / Qingyin Review Decision Trace Integration Boundary v0.1

## 1. Purpose

This document integrates the boundary between:

- `review_decision_trace`
- sandbox trace
- voice output trace

The purpose is to keep all trace-like artifacts in the correct layer:

- trace is evidence, not approval
- trace is record, not authorization
- trace is audit material, not runtime action

This is docs-only / boundary-integration / review-trace-audit work. It does not implement runtime behavior, review decision runtime, selection eligibility runtime, activation runtime, lesson_store writes, Memory Layer writes, sandbox runtime, voice instinct runtime, Audio Sense runtime, STT runtime, TTS runtime, voice trigger runtime, or a voice input-output loop.

## 2. Source Boundaries

This integration boundary relates existing documents and contracts:

- review_decision contract
- review_decision_trace
- review_decision_trace audit
- sandbox boundary / capability assumption
- sandbox failure / trace contract
- sandbox safety audit
- voice instinct / audio sense boundary audit

The common rule across these artifacts is:

```text
trace is evidence, not approval
trace is record, not authorization
trace is audit material, not runtime action
```

## 3. Core Result

Review decision trace is cold audit evidence, not permission.

Review decision trace must not activate lessons.

Review decision trace must not grant selection eligibility.

Review decision trace must not authorize runtime behavior.

Review decision trace must not write to lesson_store or Memory Layer.

## 4. review_decision_trace Definition

`review_decision_trace` is a cold trace / historical audit record.

It may record that a review decision happened. It must not become the review decision engine itself. It must not be treated as a live lesson object, runtime selector input, state-machine command, lesson lifecycle command, or Memory Layer promotion trigger.

## 5. Permission Boundary

Trace is evidence, not approval.

Trace is record, not authorization.

Trace is audit material, not runtime action.

No trace artifact may be interpreted as permission to act. This applies to review_decision_trace, sandbox trace, voice output trace, and future trace-like audit artifacts.

## 6. Selection Eligibility Boundary

Review decision trace must not grant selection eligibility.

Selection eligibility must come from explicit eligibility logic and review-gated selection boundaries, not from historical trace existence.

An approved review_decision_trace is still cold trace. It must not silently become:

- selectable lesson
- selection candidate
- review gate pass
- priority signal
- runtime decision input

## 7. Lesson Activation Boundary

Review decision trace must not activate lessons.

Approved / rejected / deferred trace status must not mutate lesson lifecycle. It must not enable lessons, disable lessons, mark stale, unmark stale, apply replacement, activate supersede links, or resolve conflicts.

## 8. lesson_store Boundary

Review decision trace must not write to lesson_store.

Review decision trace must not create active lessons, update existing lessons, or write lesson_candidate records directly.

## 9. Memory Layer Boundary

Review decision trace must not write to Memory Layer.

ASHL Core provides evidence.

D Qingyin Memory Layers decide memory admission.

D清音 Memory Layers decide memory admission.

Review decision trace must not trigger Long-term Memory write, Memory Layer promotion, Memory Economy behavior, Core Memory write, Archive Memory write, or Working Memory admission.

## 10. Sandbox Trace Boundary

Sandbox trace must not become review permission.

Sandbox trace must not bypass review_decision boundaries.

Sandbox trace is evidence produced by bounded experimental observation. It must not become approval, direct lesson_candidate creation, review_decision_trace creation, lesson_store write, Memory Layer write, or runtime action permission.

## 11. Voice Output Trace Boundary

Voice output trace must not become review permission.

Voice output trace must not bypass review_decision boundaries.

Voice output trace is evidence produced by future voice-related observations. It must not become authoritative failure_reason, formal lesson_candidate, review decision, Memory Layer write, voice training command, or audio runtime permission.

## 12. Bidirectional Voice Interaction Deferral

Bidirectional voice interaction is deferred.

Audio Sense / STT / TTS / voice trigger / voice input-output loop are deferred until consultant review.

This document does not define bidirectional voice interaction. It does not add Audio Sense, STT, TTS, voice trigger, speech recognition, speech synthesis, voice output runner, audio input runner, or any voice input-output loop.

## 13. Future Runtime Questions

Future packages must separately review:

1. when, if ever, review_decision_trace can be read by runtime systems
2. how sandbox trace and voice output trace enter review pipelines as evidence only
3. how review decision and selection eligibility remain separated from trace storage
4. how Memory Layer admission remains owned by D Qingyin Memory Layers
5. what bidirectional voice interaction means after Audio Sense / STT / TTS boundaries are reviewed

This document answers none of those runtime questions.

## 14. Non-Permissions

This document does not permit:

- runtime
- review decision runtime
- selection eligibility runtime
- activation runtime
- lesson_store write
- Memory Layer write
- sandbox runtime
- voice instinct runtime
- Audio Sense runtime
- STT runtime
- TTS runtime
- voice trigger runtime
- voice input-output loop
- voice output runner
- audio input runner
- tool permission runtime
- review / lesson / selection / activation / conflict behavior changes
- treating review_decision_trace as permission
- using review_decision_trace to activate lessons
- using review_decision_trace to grant selection eligibility
- turning sandbox trace into review_decision
- turning voice output trace into review_decision

## 15. Final Result

Review decision trace is cold audit evidence, not permission.

The integration boundary is:

```text
review_decision_trace = cold audit evidence
sandbox trace = evidence, not approval
voice output trace = evidence, not approval
runtime authorization = not provided by trace
```
