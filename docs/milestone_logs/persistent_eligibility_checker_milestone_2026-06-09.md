# Persistent Eligibility Checker Milestone

Date: 2026-06-09

## Purpose

This milestone records completion of the checker that evaluates whether an approved candidate has enough evidence to enter `persistent_candidate` review.

This is checker-only. This is not persistent rule application. This does not write persistent rules.

## Preceding Design

This milestone follows Persistent Rule Application Design v0.

Key distinction:

```text
approved = allowed to enter validation
persistent = allowed to be written only after survival checks
```

## Implemented Checker

The checker evaluates these gates:

```text
approved human candidate
temporary apply verification
repeated similar-context validation
challenge survival
low recent failure
low active conflict
trace preserved
rollback path exists
```

## CLI Result

```text
command = run-persistent-eligibility-checker-check
case_count = 10
eligible_for_persistent_candidate_review_count = 1
eligible_for_persistent_rule_count = 0
blocked_count = 9
persistent_rule_write_allowed_count = 0
```

## Strongest Allowed Claim

ASHL Core can deterministically evaluate whether an approved candidate has enough evidence to enter persistent_candidate review, while keeping persistent rule write, persistent activation, global predictor mutation, and action selection modification disabled.

## Explicit Boundary

```text
eligible_for_persistent_candidate_review may be true.
eligible_for_persistent_rule must remain false.
persistent_rule_write_allowed must remain false.
```

## Explicit Non-Claims

- No persistent rule write.
- No persistent rule table.
- No persistent rule storage.
- No persistent rule activation.
- No global predictor modification.
- No action selection modification.
- No prediction-driven action selection.
- No candidate auto-approval.
- No Qingyin self-approval.
- No candidate persistent auto-promotion.
- No lesson_store write.
- No Memory Layer write.
- No long-term memory write.
- No lesson internalization.
- No instinct-like behavior.
- No autonomous learning.
- No general learning proof.
- No consciousness claim.
- No subjective experience claim.

## Why Stop Here

The persistent line is intentionally paused after eligibility checking.

Persistent Candidate Preview / Dry-run v0 is a future candidate, not part of the current plan.

The next planned direction after this wrap-up is generalized memory loop.

## Next Planned Direction

```text
Generalized Memory Loop
```

Do not define its implementation yet.
