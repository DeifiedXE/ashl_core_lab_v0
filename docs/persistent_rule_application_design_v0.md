# Persistent Rule Application Design v0

## Purpose

This document defines the safety gate between an approved candidate and a persistent rule.

It does not implement persistent rule application. It prevents single-approval or single-success rules from becoming permanent.

## Core Principle

```text
approved candidate
-> temporary apply verification
-> repeated similar-context validation
-> challenge survival
-> low recent failure
-> low active conflict
-> trace preserved
-> rollback path exists
-> human persistent approval
-> persistent rule
```

Short rule:

```text
approved = allowed to enter validation
persistent = allowed to be written only after survival checks
```

## Definitions

- candidate: a proposed rule change created from mismatch evidence and requiring review.
- approved candidate: a candidate reviewed and approved by a human reviewer; this is not a persistent rule.
- temporary apply verification: a runner-local in-memory application check proving the candidate changes prediction as previewed without persistent writes.
- persistent rule candidate: an approved candidate that has passed enough later gates to be considered for persistent approval.
- persistent rule: a formally written rule entry that may be read by future predictor/rule systems after explicit human persistent approval.
- challenge: a counterexample or adversarial case intended to test whether the candidate overgeneralizes.
- recent failure: a recent validation or prediction failure associated with the candidate, key, or proposed behavior.
- active conflict: an unresolved incompatible rule, candidate, counterexample, supersede issue, stale state, or review blocker.
- trace: preserved evidence showing why the candidate exists, what changed in preview, and what happened during validation/challenge/review.
- rollback path: a documented way to disable the persistent rule and restore prior prediction behavior.
- human persistent approval: a separate human approval after validation and challenge survival; initial candidate approval does not count.

Important distinction:

```text
approved_candidate != persistent_rule
```

## Required Gates

### Gate 1: Approved Candidate

Required:

```text
candidate_status == approved
reviewer_type == human
qingyin_self_approval == false
applied == false
```

### Gate 2: Temporary Apply Verification

Required:

```text
temporary in-memory application passed
prediction changes as previewed
global predictor not modified
persistent write count == 0
```

### Gate 3: Repeated Similar-Context Validation

Candidate must pass multiple similar-context cases.

The threshold is intentionally unset in v0. A future implementation may use N similar-context cases.

Track:

```text
validation_count
validation_pass_count
validation_fail_count
similar_context_key coverage
```

### Gate 4: Challenge Survival

A candidate must survive challenge cases.

Challenge examples:

```text
same similar_context_key but different actual outcome
nearby context with conflicting result
known counterexample
recent mismatch
human-created adversarial check
```

Track:

```text
challenge_count
challenge_survival_count
challenge_failure_count
challenge_survival_rate
```

### Gate 5: Low Recent Failure

Candidate must have low recent failure.

No fixed number is defined in v0.

Track:

```text
recent_failure_count
recent_failure_window
recent_failure_severity
```

### Gate 6: Low Active Conflict

Candidate must not have active unresolved conflicts.

Track:

```text
active_conflict_count
conflict_status
conflict_severity
supersede_status
stale_status
```

### Gate 7: Trace Preserved

Persistent candidate must keep trace.

Required trace fields:

```text
source_candidate_id
source_experience_ids
source_failure_reasons
similar_context_keys
prediction_before
prediction_after_preview
temporary_apply_verification_result
validation_history
challenge_history
review_history
persistent_approval_record
rollback_rule_id / rollback_path
```

### Gate 8: Rollback Path Exists

Before persistence, there must be a rollback plan.

Required:

```text
can_disable_persistent_rule
can_restore_previous_prediction_behavior
can inspect why rule was created
can trace rule back to candidate and evidence
```

### Gate 9: Human Persistent Approval

A separate human approval is required after validation.

Important:

```text
initial candidate approval does not count as persistent approval
```

## Suggested Status Flow

```text
proposed
-> pending_review
-> approved
-> previewed
-> temporary_verified
-> persistent_candidate
-> persistent_pending_review
-> persistent_approved
-> persistent_active
```

Blocked / terminal statuses:

```text
rejected
deferred
temporary_verification_failed
validation_failed
challenge_failed
conflict_blocked
rollback_missing
persistent_rejected
superseded
stale
disabled
rolled_back
```

## Non-Automation Rule

No candidate may become persistent automatically in v0.

Human persistent approval is required.

## Relationship to Instinct / Lesson Internalization

Persistent rule application is not the same as instinct-like internalization.

Persistent rule:

```text
a formal predictor/rule entry may be written
```

Instinct-like internalization:

```text
a later familiarity-based lower-cost behavior pathway
```

Do not conflate them.

## Optional Machine-Readable Design Schema

This schema is documentation only. No code should consume it yet.

PersistentEligibilityRecord:

```text
candidate_id
candidate_status
temporary_verified
similar_context_validation_count
similar_context_validation_pass_count
challenge_count
challenge_survival_count
recent_failure_count
active_conflict_count
trace_preserved
rollback_path_exists
human_persistent_approval
eligibility_status
block_reasons
```

## Explicit Non-Claims

- No implementation of persistent rules.
- No persistent rule write.
- No global predictor modification.
- No action selection modification.
- No automatic learning.
- No autonomous learning.
- No lesson internalization.
- No instinct-like behavior.
- No long-term memory write.
- No lesson_store write.
- No Memory Layer write.
- No LLM reasoning.
- No LLM planning.
- No pathfinding.
- No consciousness claim.
- No subjective experience claim.

## Future Implementation Notes

A future implementation package may add:

```text
persistent eligibility checker
persistent candidate preview
persistent approval gate
persistent write dry-run
persistent rule table schema
rollback verification
```

Do not implement them in this package.
