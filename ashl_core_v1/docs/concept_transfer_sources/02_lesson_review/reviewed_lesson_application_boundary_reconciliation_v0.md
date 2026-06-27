# Reviewed Lesson Application Boundary Reconciliation v0

Date: 2026-06-12

## Purpose

This document reconciles the completed generic lesson evidence pipeline with the existing reviewed lesson application boundary.

ASHL Core can bridge generic lesson review decisions into the existing reviewed lesson evidence pipeline.
ASHL Core cannot apply lessons from that evidence yet.

Evidence may approach the application boundary, but evidence is not permission to apply a lesson.

## Current Generic Evidence Path

The current generic evidence path is:

```text
generic_lesson_review_decision
-> existing reviewed_lesson_trace_preview
-> existing reviewed_lesson_dry_run_correction_minimal
-> existing dry_run_correction_into_trial_trace
-> existing before_after_trial_contrast
-> existing lesson_effect_evidence_trace_minimal
```

The path is generic and reuses existing modules.
It does not create source-specific review, dry-run, trial-trace, contrast, or evidence channels.

## Existing Application Boundary

The existing application boundary remains defined by:

```text
docs/lesson_application_boundary_review_v0.md
docs/minimal_lesson_effect_retention_boundary_review_v0.md
```

This reconciliation does not replace those documents.
It aligns the generic evidence path with them.

## What Evidence May Do

Generic evidence may:

- enter reviewed lesson preview after a valid accepted generic lesson review decision
- enter dry-run correction through the existing dry-run path
- enter dry-run trial trace preview through the existing trial trace path
- enter before/after contrast through the existing contrast path
- enter lesson effect evidence trace through the existing evidence path
- support a future application gate review

## What Evidence May Not Do

lesson_effect_evidence_trace is evidence only.
reviewed_lesson_preview is preview only.
dry_run_correction is dry-run only.
before_after_trial_contrast is contrast only.
None of these are application approval.

Evidence must not:

- apply a lesson
- write memory
- write retained JSONL
- write retention
- mutate predictors
- change runtime behavior
- create production action selection
- create selected_action
- create final_action
- create a direct command
- claim proof of learning

## Required Future Application Gates

Before any lesson application package may exist, all of these gates are required:

- valid generic lesson review decision
- decision == accepted_for_reviewed_lesson_preview
- valid reviewed_lesson_trace_preview
- valid reviewed_lesson_dry_run_correction
- valid dry_run_correction_into_trial_trace
- valid before_after_trial_contrast
- valid lesson_effect_evidence_trace
- explicit human application approval
- application scope defined
- rollback path defined
- audit trace required
- mentor override preserved
- runtime behavior boundary checked
- memory write boundary checked
- predictor mutation boundary checked
- retention boundary checked

## Required Rejection Conditions

A future application gate must reject if any of these are true:

- generic decision is rejected
- generic decision needs_more_evidence
- missing reviewed_lesson_preview
- missing dry_run_correction
- missing trial_trace
- missing before_after_contrast
- missing lesson_effect_evidence_trace
- missing explicit human application approval
- missing rollback path
- missing audit trace
- mentor override unavailable
- application scope unclear
- would write memory
- would write retention
- would mutate predictor
- would change runtime behavior outside sandbox/application scope
- would create production action selection
- would create selected_action
- would create final_action
- would create direct command
- would claim proof of learning

## Future Design-Only Output Shape

The future application gate may use this design-only shape:

```text
reviewed_lesson_application_gate_result_id
source_lesson_effect_evidence_trace_id
application_gate_status
application_scope
explicit_human_application_approval
rollback_available
audit_trace_required
mentor_override_available
allowed_for_sandbox_application
allowed_for_runtime_application
allowed_for_memory_write
allowed_for_retention_write
allowed_for_predictor_mutation
allowed_for_runtime_behavior_change
blocked_flags
```

Allowed future status values:

```text
eligible_for_future_sandbox_application
rejected
needs_more_evidence
```

Required v0 rules:

- allowed_for_sandbox_application may be true only in a future separate package.
- allowed_for_runtime_application must remain False.
- allowed_for_memory_write must remain False.
- allowed_for_retention_write must remain False.
- allowed_for_predictor_mutation must remain False.
- allowed_for_runtime_behavior_change must remain False.

## Mentor Override Requirement

mentor override preserved is mandatory.

If mentor override is unavailable, the future application gate must reject.
No application package may bypass mentor override.
