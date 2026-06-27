# Phase 0 Action / Lesson Loop Return Planning v0

Date: 2026-06-10

## Purpose

This document records the decision to return ASHL Core / Qingyin from the completed perception/focus boundary segment back to the Phase 0 action / outcome / failure_reason / lesson loop.

This is a design-only planning document.
It does not add runtime action selection, new action behavior, lesson application runtime, persistent learning, persistent rule write, memory write, predictor mutation, perception-to-action bridge, focus application, active_focus, attention control, endocrine runtime, object recognition, semantic vision, autonomy, or subjective claims.

## Why Perception / Focus Pauses Here

The perception/focus path has reached a safe trace/checker/review milestone.
Further work toward active_focus, focus_applied, attention_control, or perception-to-action bridge would cross into runtime control territory.

Before vision/focus can influence action, the action/lesson loop itself should remain the primary maturity target.

Current perception/focus state:

```text
Eye-Structure Simulation Line
-> Focus Selector Trace/Checker Line
-> Focus Application Boundary / Gate
-> Perception-to-Action Boundary Review
-> Focus / Perception Boundary Construction Log
```

Current safe claim:

```text
ASHL Core / Qingyin has deterministic trace/checker/review-only perception/focus paths from low-level retina features to ranking traces and boundary reviews.
```

Current hard boundary:

```text
no active_focus
no focus_applied
no attention_control
no perception-to-action bridge
no vision-driven action selection
no visual memory write
no predictor mutation
no endocrine runtime
no object recognition
no semantic vision
no subjective proof
```

## Phase 0 Return Target

The Phase 0 core loop remains:

```text
action_intent
-> expected_outcome
-> actual_outcome
-> mismatch
-> structured failure_reason
-> lesson_candidate
-> human review
-> approved lesson
-> future behavior correction
```

Qingyin's grounding priority remains action-result contrast, not visual action control.

The near-term target is to strengthen the action / expected_outcome / actual_outcome / mismatch / structured failure_reason / lesson_candidate / human review path before opening any perception-to-action runtime path.

## Safe Next Package Options

### Option A: Action Outcome Contrast Baseline Review v0

Purpose:

```text
Review the current action -> expected_outcome -> actual_outcome contrast path and identify the smallest missing pieces.
```

Does:

```text
documents current action/outcome/failure_reason path
lists existing modules/tests
identifies safe next check package
```

Does not do:

```text
no new runtime behavior
no action selection change
no learning write
no predictor mutation
```

### Option B: Failure Reason Coverage Audit v0

Purpose:

```text
Audit whether failure_reason categories cover the next Phase 0 sandbox cases.
```

Does:

```text
review existing failure_reason design and tests
identify missing categories or boundary risks
```

Does not do:

```text
no new action behavior
no lesson application
no persistent learning
```

### Option C: Lesson Candidate Review Path Audit v0

Purpose:

```text
Review how lesson_candidate is generated, reviewed, approved, and kept blocked from unsafe persistence/runtime mutation.
```

Does:

```text
summarizes current lesson review path
identifies next safe checker package
```

Does not do:

```text
no automatic lesson application
no persistent rule write
no predictor mutation
```

## Recommended Immediate Next Package

Recommended:

```text
Action Outcome Contrast Baseline Review v0
```

Reason:

```text
It re-centers the project on Phase 0 action grounding without opening runtime action selection or persistent learning.
```

This recommendation is not an implementation.
It is a planning handoff for the next work package.

## Do-Not-Cross Boundaries

```text
Do not resume perception-to-action bridge yet.
Do not introduce active_focus.
Do not introduce focus_applied.
Do not introduce attention_control.
Do not allow focus rank, total_score, or change_salience to affect action.
Do not add action selection influence from vision.
Do not add action candidate scoring from vision.
Do not add memory write from perception/focus traces.
Do not add predictor mutation.
Do not add persistent rule write.
Do not add endocrine-controlled action.
Do not add runtime action selection.
Do not add lesson application runtime.
Do not add persistent learning.
```

## Planning Snapshot

```text
latest completed commit: 32d4749 Add focus perception boundary construction log
py -3 run_all_smoke_tests.py: PASS
py -3 -m unittest discover: PASS, Ran 1559 tests
git diff --check: PASS
git status --short: clean
```

## Boundary Check

```text
phase0_action_lesson_loop_return_planning_enabled: true
planning_only: true
runtime_behavior_modified: false
new_schema_added: false
new_checker_added: false
new_cli_added: false

runtime_action_selection_added: false
action_selection_modified: false
new_action_behavior_added: false
lesson_application_runtime_added: false
automatic_lesson_application_added: false
persistent_learning_added: false
persistent_rule_write_added: false
long_term_memory_write: false
visual_memory_write: false
lesson_store_write: false
memory_layer_write: false
predictor_modified: false

perception_to_action_bridge_added: false
focus_to_action_bridge_added: false
active_focus_selection_added: false
focus_application_added: false
focus_applied_added: false
attention_control_added: false
runtime_focus_selector_added: false
runtime_ranking_added: false

endocrine_runtime_added: false
endocrine_controlled_action_added: false
autonomy_added: false
object_recognition_enabled: false
semantic_vision_claimed: false
consciousness_claimed: false
subjective_visual_experience_claimed: false
```
