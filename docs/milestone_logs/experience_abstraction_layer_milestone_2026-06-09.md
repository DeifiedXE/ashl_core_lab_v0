# Experience Abstraction Layer Milestone

Date: 2026-06-09

## Purpose

This milestone records completion of the first safe Experience Abstraction Layer loop.

It turns raw controlled experience records into:

```text
reason classification
position-independent context keys
outcome prediction
prediction accuracy/mismatch records
review-required rule candidates
human review gate
approved candidate preview
temporary in-memory apply verification
```

This is a documentation milestone only. It does not add runtime behavior, a new CLI, UI, action selection changes, predictor rule changes, persistent rule application, or Boundary Index changes.

## Completed Packages

### Failure Reason Classifier v0

Converts raw action outcome records into deterministic reason categories.
It starts the abstraction layer by turning event outcomes into explainable reason labels.

### Similar Context Key v0

Builds deterministic structural context keys from classified experiences.
The keys are position-independent by default so same-structure cases at different positions can match.

### Action Outcome Predictor v0

Predicts immediate action outcomes from prior classified experiences and `similar_context_key`.
Predictions are read-only and are not used for action selection.

### Prediction Accuracy / Mismatch Check v0

Compares predicted outcomes with actual classified observations.
It records prediction matches, outcome mismatches, reason mismatches, and unknown predictions without correcting predictor behavior.

### Rule Candidate From Prediction Mismatch v0

Converts prediction mismatches into proposed review-required candidates.
Prediction matches create no candidate.

### Rule Candidate Review Gate v0

Adds a human-review gate for proposed rule candidates.
Candidates can become `pending_review`, `approved`, `rejected`, or `deferred`, and Qingyin self-approval is blocked.

### Approved Candidate Preview v0

Creates deterministic previews for approved candidates before any application step.
It shows proposed predictor-entry changes and blocks non-approved candidates from applicable previews.

### Reviewed Candidate Apply Verification v0

Applies approved candidates only to a temporary in-memory predictor rule table.
It reruns prediction against that runner-local table and verifies expected outcome/reason changes without persistent writes.

## Completed Chain

```text
experience
-> failure_reason
-> similar_context_key
-> predicted_outcome
-> prediction_match / mismatch
-> candidate
-> human review
-> approved / rejected / deferred
-> approved preview
-> temporary in-memory apply
-> prediction verification
```

## Key Results

### Failure Reason Classifier

- `wall_blocked -> front_cell_wall`
- `empty_moved -> front_cell_empty_walkable`
- `item_contact -> front_cell_item_contact`
- `passage_crossed -> front_cell_passage_crossed`
- `exit_contact -> front_cell_exit_contact`
- `unknown -> unknown_outcome_reason`

### Similar Context Key

- Same structure at different positions can produce the same key.
- Example: `front_symbol=w|action=move_forward|primary_reason=front_cell_wall`

### Action Outcome Predictor

- Supports position-independent prediction.
- Wall transfer predicts `blocked / front_cell_wall`.

### Prediction Accuracy / Mismatch

- Records match, outcome mismatch, reason mismatch, and unknown prediction.
- Mismatch is recorded only.

### Rule Candidate From Mismatch

- Mismatch becomes a proposed review-required candidate.
- Match creates no candidate.

### Review Gate

- Human reviewer is required.
- Qingyin self-approval is blocked.
- Approved does not mean applied.

### Approved Preview

- Approved candidates can show a preview diff.
- Pending and rejected candidates are blocked from applicable preview.

### Reviewed Apply Verification

- Approved candidates can be applied only to a temporary in-memory rule table.
- Prediction changes are verified against that table.
- No persistent writes occur.

## Strongest Allowed Claim

ASHL Core can convert controlled experience records into deterministic reason classifications, position-independent context keys, immediate outcome predictions, mismatch records, review-required rule candidates, human-gated review states, approved previews, and temporary in-memory apply verification without modifying global predictors or action selection.

## Explicit Non-Claims

- No general learning proof.
- No autonomous rule learning.
- No persistent rule application.
- No global predictor modification.
- No action selection modification.
- No long-term memory write.
- No lesson_store write.
- No Memory Layer write.
- No lesson_candidate pipeline connection.
- No LLM reasoning.
- No LLM planning.
- No LLM vision.
- No pathfinding.
- No route planning.
- No item seeking.
- No UI expansion.
- No consciousness claim.
- No subjective experience claim.
- No visual understanding claim.
- No solved symbol grounding claim.

## Safety Boundaries

- Candidates are proposed and require review.
- Human reviewer is required in v0.
- Qingyin self-approval is blocked.
- Approved means reviewed, not applied.
- Preview means display diff, not change.
- Apply verification uses a temporary in-memory rule table only.
- No persistent writes occur.

## Current Boundary Index Status

Boundary Index remains unchanged at Boundary Index Version: 2026-06-09-b34.

This milestone should be synced later, but not in this package.

## Next Major Direction

Next recommended package:

```text
Experience Abstraction Boundary Index Sync v0
```

Reason:

```text
This milestone should be indexed before moving into persistent rule application or endocrine/eye-structure lines.
```

If moving quickly into the next functional package, the next candidate can be:

```text
Persistent Rule Application Design v0
```

Do not implement that in this milestone package.
