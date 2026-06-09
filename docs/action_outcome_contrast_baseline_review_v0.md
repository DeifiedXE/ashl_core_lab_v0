# Action Outcome Contrast Baseline Review v0

Date: 2026-06-10

## Purpose

This document reviews the current Phase 0 action/outcome contrast path and identifies the smallest safe next trace/checker package.

This is a design-only baseline review.
It does not add runtime action selection, action behavior changes, lesson application runtime, automatic lesson application, persistent learning, persistent rule write, memory write, predictor mutation, perception-to-action bridge, focus application, active_focus, attention control, endocrine runtime, autonomy, object recognition, semantic vision, or subjective claims.

## Scope

Reviewed path:

```text
action_intent
-> expected_outcome
-> actual_outcome
-> mismatch
-> structured failure_reason
-> lesson_candidate
-> human review
```

This review inspects existing repository modules, tests, and docs related to action/outcome/failure/lesson traces.
It does not rewrite core modules.
It does not change action selection.
It does not create new learning behavior.

## Current Repository Review

Current repository appears to support a partial trace/review path for action-result contrast:

```text
structured failure_event
-> normalized_failure_event_trace
-> lesson_candidate_input_trace
-> lesson_candidate_draft_trace
-> review queue / review decision contracts
```

Current repository also contains deterministic sandbox/action outcome support:

```text
session-local state-action-outcome records
failure_reason classification for controlled action outcomes
action_outcome_predictor checks that remain read-only
manual/candidate review utilities
integrated loop trace and review-related tests
```

This review does not claim a complete runtime learning loop.
It only confirms that several trace/check/review pieces already exist.

## Existing Related Components

### Action / Intent Records

Confirmed:

```text
ashl_core/failure_events.py
```

`failure_event` requires `action_intent` as a structured field.

Also related:

```text
ashl_core/action_sandbox.py
ashl_core/micro_push_box_trial_runner.py
ashl_core/micro_navigation_trial_runner.py
ashl_core/integrated_loop.py
```

These provide action traces and sandbox/trial behaviors, but this review does not modify them.

### Expected Outcome Records

Confirmed:

```text
ashl_core/failure_events.py
```

`failure_event` requires `expected_outcome`.
`normalize_failure_event_trace` extracts `expected_outcome_type`.

Not fully confirmed in this review:

```text
a single reusable expected_outcome pair schema outside failure_event
```

### Actual Outcome Records

Confirmed:

```text
ashl_core/failure_events.py
ashl_core/session_working_memory.py
```

`failure_event` requires `actual_outcome`.
`session_working_memory` records `outcome_type`, `failure_reasons`, and `effect_tags` for session-local state-action-outcome records.

### Mismatch / Failure Detection

Confirmed:

```text
ashl_core/failure_events.py
```

`validate_failure_event` requires `mismatch` and classifies missing, non-failure, invalid, system_fault, and valid failure_event cases.

### Structured failure_reason

Confirmed:

```text
ashl_core/failure_events.py
ashl_core/failure_reason_classifier.py
```

`failure_event` requires `failure_reason_id` before authoritative failure reason is allowed.
`failure_reason_classifier` maps controlled action outcomes to deterministic reason categories.

Known classifier examples include:

```text
front_cell_wall
front_cell_empty_walkable
front_cell_item_contact
front_cell_passage_crossed
front_cell_exit_contact
turn_action_orientation_change
look_action_observation_only
unknown_outcome_reason
```

### Read-Only Outcome Prediction

Confirmed:

```text
ashl_core/action_outcome_predictor.py
tests/test_action_outcome_predictor.py
```

`action_outcome_predictor` predicts immediate outcomes from prior classified experiences, but its boundary states that predictions are read-only and are not used for action selection.

### lesson_candidate Creation / Drafting

Confirmed:

```text
ashl_core/failure_events.py
ashl_core/lesson_candidate_drafts.py
```

`build_lesson_candidate_input_trace` creates preparation evidence and explicitly marks `not_a_lesson_candidate`.
`lesson_candidate_drafts.py` builds trace-only `lesson_candidate_draft_trace` records that are review-gated, not approved, not active, not selection eligible, not internalized, and not written to lesson_store or long-term memory.

Not confirmed as safe for automatic runtime use in this review:

```text
automatic lesson_candidate creation
automatic lesson application
persistent lesson_store write from outcome contrast
```

### Candidate Review / Approval

Confirmed:

```text
ashl_core/candidate_review.py
ashl_core/review_tasks.py
ashl_core/review_decisions.py
ashl_core/rule_candidate_review_gate.py
ashl_core/approved_candidate_preview.py
ashl_core/reviewed_candidate_apply_verification.py
```

The repository has review records, review gates, previews, and verification checks.
This baseline review does not enable automatic approval or runtime application.

### Trial Rules / Review Paths

Confirmed:

```text
ashl_core/trial_rules.py
ashl_core/trial_feedback.py
tests/test_trial_rules.py
tests/test_trial_feedback.py
```

Trial-related review paths exist.
This review does not modify trial behavior.

### Integrated Loop Trace

Confirmed:

```text
ashl_core/integrated_loop.py
tests/test_integrated_loop.py
tests/test_integrated_experience_session_trace.py
```

The integrated loop has trace fields for correction, rule candidates, trial suggestions, and trial feedback.
This review does not change the integrated loop.

## Known Completed Components

Current tests cover these related pieces:

```text
failure_event schema foundation
failure_event normalization trace
failure_event to lesson_candidate_input_trace bridge
lesson_candidate_draft schema trace
lesson_candidate_draft schema audit
lesson_candidate_draft strict schema injection guard
outcome unknown payload draft invariant guard
review task trace schema and audit
review decision contract and audit
formal lesson_candidate creation contract and boundary audit
failure_reason_classifier
action_outcome_predictor
session_working_memory
session_working_memory trial integration
candidate_review
trial_rules
trial_feedback
integrated_loop
```

## Known Gaps

Current missing pieces appear to be:

```text
whether expected_outcome and actual_outcome are consistently recorded together outside failure_event
whether mismatch fields are standardized across all action/outcome trace families
whether failure_reason coverage is complete for the next Phase 0 sandbox cases
whether lesson_candidate source_trace is complete across draft/review paths
whether review-gated boundaries are consistently documented across action/outcome contrast records
whether action selection remains unaffected by all review-only traces
whether predictor outputs are consistently blocked from action selection
```

These are auditability gaps, not requests for runtime behavior.

## Baseline Review Result

Baseline status:

```text
Phase 0 action/outcome contrast path exists in partial trace/review form.
The next safe step should strengthen auditability before changing behavior.
```

The repository already has a structured `failure_event` path with `action_intent`, `expected_outcome`, `actual_outcome`, `mismatch`, and `failure_reason_id`.
It also has session-local state-action-outcome records and deterministic classifier/predictor checks.

The contrast pair exists most clearly inside `failure_event`, but a focused checker for expected-vs-actual outcome pair invariants is not yet confirmed as a standalone package.

## Recommended Next Minimal Package

This is the recommended next minimal package after this baseline review.

Package name:

```text
Expected vs Actual Outcome Pair Schema Check v0
```

What it is for:

```text
Validate the smallest reusable expected_outcome / actual_outcome / mismatch record shape before any behavior change.
```

What it does:

```text
checks that expected_outcome and actual_outcome are both present
checks that unknown-vs-unknown is not valid learning evidence
checks that mismatch is explicit and boolean
checks that structured failure_reason remains required before lesson_candidate input
checks that the pair is trace-only and review-gated
checks that predictor/action selection/memory boundaries remain blocked
```

What it does NOT do:

```text
no runtime action selection
no action behavior change
no lesson application runtime
no automatic lesson application
no persistent learning
no persistent rule write
no memory write
no predictor mutation
```

Reason for this recommendation:

```text
The expected_outcome / actual_outcome pair already appears in failure_event.
Making the pair invariant explicit is smaller and more grounded than designing a broader action outcome contrast trace schema immediately.
```

## Safety Boundaries

```text
no runtime action selection
no action selection influence
no new action behavior
no action candidate scoring changes
no movement control changes
no lesson application runtime
no automatic lesson application
no persistent learning
no persistent rule write
no long-term memory write
no lesson_store write
no visual memory write
no predictor mutation
no perception-to-action bridge
no focus-to-action bridge
no active_focus
no focus_applied
no attention_control
no runtime focus selector
no runtime ranking
no endocrine runtime
no endocrine-controlled action
no autonomy
no object recognition
no semantic vision
no subjective claims
```

## Do-Not-Cross Lines

```text
Do not use predictor output for action selection.
Do not turn expected-vs-actual mismatch into automatic learning.
Do not create approved lessons without human review.
Do not write lesson_store, Memory Layer, long-term memory, or persistent rules.
Do not mutate predictor behavior from review-only traces.
Do not connect perception/focus traces to action_context or action_selection.
Do not introduce active_focus, focus_applied, or attention_control.
```

## Boundary Check

```text
action_outcome_contrast_baseline_review_enabled: true
review_only: true
runtime_behavior_modified: false
new_schema_added: false
new_checker_added: false
new_cli_added: false

runtime_action_selection_added: false
action_selection_modified: false
new_action_behavior_added: false
action_candidate_scoring_modified: false
movement_control_modified: false
lesson_application_runtime_added: false
automatic_lesson_application_added: false
persistent_learning_added: false
persistent_rule_write_added: false
long_term_memory_write: false
lesson_store_write: false
visual_memory_write: false
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
subjective_claims_added: false
```
