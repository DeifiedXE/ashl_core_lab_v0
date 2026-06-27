# ASHL Core / Qingyin perception layer design assumption v0.1

## Purpose

This document defines the Phase 0 perception layer design assumption.

It explains how Qingyin may later receive perceptual input, how perception relates to action context, and how perceptual information may become part of the failure_reason / lesson_candidate loop.

This is a design assumption document only. It does not implement perception runtime, visual input runtime, or perceptual_code runtime.

## Core Assumption

Perception is not just image input. Perception is the structured bridge from sensed features to action-relevant meaning.

Phase 0 does not assume full symbol grounding. Instead, Phase 0 assumes a small, reviewable path:

```text
perception_input
-> perceptual_features
-> perceptual_code
-> action_context
-> expected_outcome
-> actual_outcome
-> failure_reason
-> lesson_candidate
```

The purpose is to let perception participate in traceable action learning without pretending that Qingyin already has complete visual understanding.

## Perception Is Not Direct Understanding

Perception should not be treated as direct truth.

An image, screen state, or sensor result may produce candidates, but those candidates must remain structured, traceable, and reviewable.

LLM vision or image captioning may assist future wording or feature extraction, but it must not become the sole authority for perceptual truth.

## Perceptual Code

`perceptual_code` is the assumed structured representation between raw perception and action context.

Examples:

```text
perceptual_code:
  target_id: apple_id_001
  target_type: apple
  observed_features:
    - red
    - round
    - on_table
```

`perceptual_code` should be explicit enough to support trace, comparison, and review. It is not a hidden instinct signal.

## Action Context

Perception becomes useful for Phase 0 only when it can be connected to action_context.

Example:

```text
perceptual_code detects cube_001
action_context says cube_001 is target of pick_up
expected_outcome says cube_001 should become held
actual_outcome says cube_001 did not move
```

This allows perceptual information to connect to expected / actual mismatch.

## Recognition and Non-Recognition

Phase 0 distinguishes:

- recognition candidate
- non-recognition candidate
- uncertain perception candidate

Recognition candidate means the system has a structured candidate such as `target_type: apple`.

Non-recognition candidate means the system detects something but does not yet know what it is.

Uncertain perception candidate means the system has partial features but insufficient confidence.

All three are candidates, not proof.

## Relation to Lesson Flow

Perception may later contribute to lessons when it is connected to action and failure.

Example:

```text
perception_input: object appears reachable
action_intent: approach object
expected_outcome: distance decreases safely
actual_outcome: blocked path
failure_reason: approach_blocked_by_obstacle
lesson_candidate: observe / check distance before approach
```

The lesson layer should receive structured perception-linked failure input, not raw perceptual text alone.

## Symbol Grounding Boundary

Phase 0 does not claim full symbol grounding.

`perceptual_code` may connect a label, feature set, and action context, but that is still an assumption layer. It should remain reviewable and reversible.

## Boundaries

- This document does not add perception runtime.
- This document does not add visual input runtime.
- This document does not add perceptual_code runtime.
- This document does not add image model integration.
- This document does not add camera or screen monitoring.
- This document does not add symbol grounding runtime.
- This document does not change selection logic.
- This document does not change conflict logic.
- This document does not change review logic.
- This document does not change strict supersede activation.
- This document does not change known / unknown failure_reason behavior.
