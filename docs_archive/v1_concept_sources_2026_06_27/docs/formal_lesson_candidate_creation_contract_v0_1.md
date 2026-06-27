# ASHL Core / Qingyin Formal Lesson Candidate Creation Contract v0.1

## 1. Purpose

This document defines the contract boundary for future formal `lesson_candidate` creation.

This is docs-only / contract-only / formal-lesson-candidate-boundary work. It does not implement formal lesson_candidate creation runtime, formal lesson_candidate schema runtime, automatic lesson_candidate builder, failure_event automatic builder runtime, evaluator runtime, review decision runtime, selection eligibility runtime, activation runtime, sandbox runtime, voice / audio runtime, lesson_store writes, or Memory Layer writes.

## 2. Contract Summary

Formal lesson_candidate creation requires structured evidence, validated boundaries, and review-ready trace.

Formal lesson_candidate creation is not lesson approval.

Formal lesson_candidate creation is not lesson_store write.

Formal lesson_candidate creation is not activation.

Formal lesson_candidate creation does not grant selection eligibility.

Formal lesson_candidate creation is not Memory Layer promotion.

## 3. Formal lesson_candidate Creation Definition

Formal lesson_candidate creation means that enough structured and validated evidence exists to prepare a candidate for review.

It is not the same as approval. It is not the same as an active lesson. It is not a write command. It is not a runtime selector input.

The candidate remains review-facing material until existing review gates decide what happens next.

## 4. Creation Precondition Boundary

Future formal lesson_candidate creation must require:

- structured failure_event exists
- normalized_failure_event exists when applicable
- expected_outcome / actual_outcome contrast exists
- evaluator_source is identified
- mismatch is explicit
- failure_reason is traceable, not LLM-only
- lesson_candidate_input_trace exists
- source evidence is preserved
- review boundary is explicit
- no direct lesson_store write is performed
- no activation is performed

This list is a contract boundary, not a runtime completeness checker.

## 5. Allowed Evidence Sources

Allowed evidence sources may include:

- structured failure_event
- normalized_failure_event
- lesson_candidate_input_trace
- review_task_trace
- review_decision_trace as cold audit evidence
- sandbox trace as evidence only
- voice output trace as evidence only
- human review note
- source evidence document

Allowed evidence source does not mean direct creation permission. Each source remains subject to its own validation and review boundary.

## 6. Disallowed Direct Sources

The following must not directly create formal lesson_candidate:

- raw natural language complaint
- LLM-only explanation
- sandbox success
- sandbox failure without failure_event validation
- sandbox repair suggestion
- voice imitation result
- voice output mismatch without expected_output / actual_output contrast
- review_decision_trace alone
- memory entry alone
- user preference alone

## 7. failure_event Boundary

No structured failure_event, no authoritative failure_reason.

Formal lesson_candidate creation must not bypass failure_event validation.

If there is no structured failure_event and no expected_outcome / actual_outcome contrast, the system must not treat an explanation as authoritative failure evidence.

## 8. normalized_failure_event Boundary

When normalization is applicable, normalized_failure_event must preserve source evidence and traceability.

Normalization does not approve a lesson_candidate. It only prepares failure evidence for later candidate-building contracts.

## 9. lesson_candidate_input_trace Boundary

lesson_candidate_input_trace is evidence preparation, not formal lesson_candidate creation.

An input trace may organize evidence for a future builder. It must not become a formal candidate by itself, write lesson_store, grant selection eligibility, activate lessons, or bypass review.

## 10. Sandbox Trace Boundary

Sandbox trace may support formal lesson_candidate creation only as evidence.

Sandbox trace must not directly create formal lesson_candidate.

Sandbox trace must still pass through failure_event validation, lesson_candidate builder contract boundaries, and review gates.

## 11. Voice Output Trace Boundary

Voice output trace may support formal lesson_candidate creation only as evidence.

Voice output trace must not directly create formal lesson_candidate.

Voice output mismatch requires expected_output / actual_output contrast and must not become authoritative failure_reason from LLM-only explanation.

## 12. Review Gate Boundary

Formal lesson_candidate creation must remain review-gated before approval.

A formal lesson_candidate may be review-ready, but review-ready does not mean approved. Approval remains separate from creation.

## 13. lesson_store Boundary

Formal lesson_candidate creation is not lesson_store write.

Formal lesson_candidate creation must not write active lessons, modify existing lessons, create lesson_store records, enable lessons, disable lessons, mark stale, unmark stale, apply replacement, or resolve conflicts.

## 14. Memory Layer Boundary

Formal lesson_candidate creation is not Memory Layer promotion.

ASHL Core provides evidence.

D Qingyin Memory Layers decide memory admission.

D清音 Memory Layers decide memory admission.

Formal lesson_candidate creation must not write Long-term Memory, Core Memory, Archive Memory, Working Memory, Memory Economy structures, or any Memory Layer.

## 15. Activation / Selection Eligibility Boundary

Formal lesson_candidate creation is not activation.

Formal lesson_candidate creation does not grant selection eligibility.

A formal lesson_candidate must not be treated as an active lesson, selected action source, review-gated eligibility pass, priority signal, or runtime decision input.

## 16. Future Runtime Questions

Future packages must separately define and review:

1. formal lesson_candidate schema runtime
2. formal creation gate runtime
3. evidence completeness check runtime
4. evaluator_source trust policy runtime
5. sandbox / voice trace evidence-only path
6. review_decision_trace use as audit material, not permission
7. bidirectional voice interaction before voice output trace can be runtime input

This document does not answer those runtime questions.

## 17. Non-Permissions

This contract does not permit:

- formal lesson_candidate creation runtime
- formal lesson_candidate schema runtime
- automatic lesson_candidate builder
- failure_event automatic builder runtime
- evaluator runtime
- lesson_store write
- Memory Layer write
- Long-term Memory write runtime
- review decision runtime
- selection eligibility runtime
- activation runtime
- sandbox runtime
- voice instinct runtime
- Audio Sense / STT / TTS runtime
- voice trigger runtime
- voice input-output loop
- review / lesson / selection / activation / conflict behavior changes
- raw natural language complaint directly creating formal lesson_candidate
- LLM-only explanation directly creating formal lesson_candidate
- sandbox trace directly creating formal lesson_candidate
- voice output trace directly creating formal lesson_candidate
- review_decision_trace directly creating formal lesson_candidate

## 18. Final Result

Formal lesson_candidate creation requires structured evidence, validated boundaries, and review-ready trace.

The contract boundary is:

```text
evidence may support creation;
trace may organize evidence;
formal lesson_candidate remains review-facing;
approval, activation, lesson_store write, and memory promotion remain separate.
```
