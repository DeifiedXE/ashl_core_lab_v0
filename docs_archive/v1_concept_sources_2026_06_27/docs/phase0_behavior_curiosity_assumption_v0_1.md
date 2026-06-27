# ASHL Core / Qingyin Phase 0 behavior / curiosity assumption v0.1

## Purpose

This document defines the Phase 0 minimal behavior set and curiosity trigger assumptions.

It is one of the Phase 0 integration assumption foundations. It answers:

- Why should Qingyin act?
- Where does her motivation come from?
- How does curiosity work?
- What is the Phase 0 minimal behavior set?

This is a design assumption document only. It does not implement runtime behavior.

## Three Motivation Sources

Phase 0 assumes three motivation sources:

1. External teaching motivation
2. Instinct / curiosity motivation
3. Need motivation

Stage mapping:

```text
Now: external teaching motivation
Early Phase 0: instinct / curiosity motivation begins to intervene
Later: need motivation
```

External teaching motivation comes from explicit user tasks, sandbox tasks, or guided teaching signals.

Instinct / curiosity motivation begins when Qingyin encounters uncertainty, novelty, mismatch, or incomplete understanding.

Need motivation is deferred. It may later represent internal maintenance needs, safety needs, or continuity needs, but it is not implemented in this package.

## Why Qingyin Acts

Qingyin acts because an input, task, uncertainty, or mismatch creates an action pressure. In Phase 0, action is not open-ended autonomy. It is a minimal response to a bounded situation.

The minimal action pressure can come from:

- A teacher gives a task.
- The environment presents an uncertain state.
- An expected outcome and an actual outcome do not match.
- A previous failure creates a lesson candidate opportunity.

## Curiosity Trigger Assumption

Curiosity is a bounded trigger, not a free roaming drive.

Curiosity may be triggered when Qingyin sees:

- novelty
- uncertainty
- contradiction
- unexpected failure
- incomplete observation
- similar situation with unknown outcome

Curiosity should produce a candidate behavior such as observe or ask_for_help. It should not directly override selection, conflict, review, or activation logic.

## Phase 0 Minimal Behavior Set

The Phase 0 minimal behavior set is:

- `observe`
- `approach`
- `avoid`
- `ask_for_help`

These names are design assumptions only in this document. This package does not add observe / approach / avoid / ask_for_help runtime behavior.

### observe

Use when the current state is incomplete, uncertain, or needs confirmation.

### approach

Use when a target looks relevant and there is no known blocker.

### avoid

Use when a known failure, danger, contradiction, or blocked state should prevent direct action.

### ask_for_help

Use when the system lacks enough information to safely choose an action or interpret a mismatch.

## Curiosity and the failure_reason / lesson_candidate Loop

Curiosity can connect to the existing failure loop as a design assumption:

```text
uncertain or novel situation
-> minimal behavior candidate
-> action / observation attempt
-> expected_outcome vs actual_outcome contrast
-> failure_reason candidate
-> lesson_candidate
-> reviewable trace
```

The loop must remain structured, traceable, and reviewable.

Curiosity does not create authoritative failure_reason values by itself. A failure_reason still requires contrast between expected outcome and actual outcome.

Curiosity does not automatically promote lesson_candidate values into memory, rules, instinct, or activation behavior.

## Similar Situation Assumption

A similar situation is not a fuzzy LLM guess.

In Phase 0, a similar situation should be defined by explicit features such as:

- same task
- same object type
- same object id when strict binding is required
- same action intent
- same expected outcome type
- same failure_reason family after review
- compatible decision point

Similarity is a candidate relation, not proof. It should be recorded in trace and remain reviewable.

## Boundaries

- This document does not add curiosity runtime.
- This document does not add attention weight runtime.
- This document does not add motivation runtime.
- This document does not add observe / approach / avoid / ask_for_help runtime behavior.
- This document does not add a Phase 0 sandbox runtime.
- This document does not add a Phase 0 failure_event runtime.
- This document does not implement an evaluator.
- This document does not implement perception.
- This document does not change selection logic.
- This document does not change conflict logic.
- This document does not change review logic.
- This document does not change strict supersede activation.
- This document does not change known / unknown failure_reason behavior.
- This document does not add a familiarity score.
- This document does not add an internalization gate.
- This document does not add an instinct-like behavior layer.
