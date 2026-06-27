# Generalized Memory Loop Design v0

## Purpose

Generalized Memory Loop Design v0 defines the first safe generalized memory loop for ASHL Core.

This is a design-only boundary document for cross-session exact-key pattern accumulation. It is not long-term memory, fuzzy similarity, action selection, autonomous learning, lesson internalization, or persistent rule application.

The goal is to describe how repeated exact-context evidence could later update prediction confidence and propose review-gated generalized candidates without changing runtime behavior in this package.

## Core v0 Definition

v0 is defined as:

```text
cross-session exact-key pattern accumulation
```

Required flow:

```text
session A experience records
session B experience records
session C experience records
-> exact similar_context_key match
-> pattern_count / outcome_distribution
-> prediction confidence update
-> generalized_candidate if threshold met
-> pending_review
```

The loop aggregates records only when their `similar_context_key` is exactly equal. It does not infer similarity from nearby shapes, semantic labels, visual resemblance, or natural-language interpretation.

## The Wrong Version

The unsafe version is free association:

- fuzzy similarity
- room or object semantic similarity
- LLM semantic similarity
- visual resemblance matching
- "this looks kind of like that" matching
- treating nearby contexts as equivalent without an exact key

v0 does not allow fuzzy matching.

The wrong version would turn separate experiences into a generalized rule before the project has evidence boundaries, conflict handling, challenge survival, rollback, or review authority. That would blur trace evidence into unreviewed behavior.

## Exact Key Only

An exact `similar_context_key` is a deterministic structural key produced from already classified experience context.

Example allowed key:

```text
front_symbol=w|action=move_forward|primary_reason=front_cell_wall
```

Records may be aggregated only when the full key string matches exactly.

Not allowed:

- `front_symbol=w` is kind of like `d`
- wall near door
- same room shape
- LLM similarity
- visual resemblance
- semantically related obstacle names
- partial key match unless a future package explicitly defines a reviewed exact-key projection

## Generalized Pattern Record

Conceptual fields:

```text
generalized_pattern_id
similar_context_key
source_session_ids
source_experience_ids
pattern_count
outcome_distribution
primary_outcome
primary_reason
confidence
conflict_count
recent_failure_count
last_seen_tick_or_session
candidate_status
review_status
```

This is design only. No schema, runtime model, storage table, JSONL artifact, CLI output, or persistence behavior is implemented by this package.

## Prediction Confidence

The generalized memory loop may increase or decrease prediction confidence only.

It may not:

- choose actions
- suppress actions
- prefer actions
- reorder candidate actions
- mutate the global predictor
- apply a rule
- write a persistent rule

Confidence is based on stable outcome ratio across exact-key records. For example:

- 5 matching outcomes out of 5 exact-key records suggests high confidence.
- 3 matching outcomes out of 5 exact-key records suggests low confidence or conflict.

No final formula is defined in v0. Future packages may define a deterministic formula after the exact-key bucket and conflict audit exist.

## Generalized Candidate

A `generalized_candidate` may be proposed when repeated exact-key evidence is stable enough.

The candidate is:

- review-gated
- traceable to source sessions and source experience records
- not auto-approved
- not auto-applied
- not persistent
- not action selection
- not prediction-driven action selection

The candidate remains `pending_review` until a future review package handles it. Approval, rejection, deferment, persistent eligibility, and application are separate concerns.

## Required Safety Gates

Any future generalized candidate or confidence increase must pass safety gates:

- evidence from more than one session
- exact key only
- pattern count above threshold
- stable outcome distribution
- low recent failure
- no active conflict
- traceable sources
- review required

Illustrative thresholds only:

```text
min_session_count >= 2
min_pattern_count >= 3
dominant_outcome_ratio >= 0.8
```

These are examples, not final thresholds. This design package does not set production gates or implement a checker.

## Block Conditions

Block candidate creation or confidence increase for:

```text
single_session_evidence_only
unresolved_conflict
high_recent_failure_rate
missing_trace
rollback_path_missing
human_review_missing_for_candidate
fuzzy_match_required
LLM_similarity_required
```

Consultant rule:

Any generalized pattern not survived challenge must not affect action selection.

v0 stronger rule:

No generalized pattern affects action selection at all.

## Relationship to Existing Systems

`similar_context_key`: The generalized memory loop uses exact-key cross-session aggregation. It does not redefine key construction and does not allow fuzzy matching.

Session working memory: Session working memory is local to one session. This design aggregates summaries across sessions conceptually, but no storage or cross-session database is implemented here.

Action outcome predictor: The generalized loop may later update prediction confidence. It does not modify predictor rules, the global predictor, or action selection.

Rule candidates: Stable generalized patterns may later produce `generalized_candidate` records for review. They are not approved, applied, or persistent by default.

Persistent rule checker: A `generalized_candidate` is not a `persistent_candidate`. Persistent eligibility remains a separate checker and must not be bypassed.

## Status Flow

```text
raw_experience
-> exact_key_bucket
-> generalized_pattern_observed
-> generalized_candidate_proposed
-> pending_review
-> approved / rejected / deferred
```

Not in v0:

- persistent promotion
- action selection influence
- long-term personality change
- instinct-like behavior

## Explicit Non-Claims

This design does not claim or implement:

- generalized memory runtime
- fuzzy similarity
- semantic similarity
- LLM similarity
- autonomous learning
- long-term memory write
- lesson_store write
- Memory Layer write
- persistent rule write
- global predictor mutation
- action selection modification
- prediction-driven action selection
- pathfinding
- visual understanding
- solved symbol grounding
- consciousness
- subjective experience

## Future Implementation Packages

Possible future packages:

- `Generalized Memory Exact-Key Bucket v0`
- `Generalized Prediction Confidence Check v0`
- `Generalized Candidate From Pattern v0`
- `Generalized Memory Conflict Audit v0`
- `Generalized Memory Review Gate v0`

`Fuzzy Similarity v1 is explicitly out of v0 scope.`

## Boundary Check

```text
generalized_memory_loop_design_enabled: true
design_only: true
runtime_behavior_modified: false
new_cli_added: false
generalized_memory_runtime_enabled: false
cross_session_storage_added: false
long_term_memory_write: false
lesson_store_write: false
memory_layer_write: false

exact_similar_context_key_only: true
fuzzy_similarity_enabled: false
semantic_similarity_enabled: false
llm_similarity_enabled: false
visual_similarity_enabled: false

prediction_confidence_only: true
prediction_rule_modified: false
global_predictor_modified: false
action_selection_modified: false
prediction_used_for_action_selection: false

generalized_candidate_design_only: true
candidate_auto_approved: false
candidate_auto_applied: false
persistent_rule_write_enabled: false

pathfinding_used: false
route_planner_added: false
llm_reasoning_used: false
llm_planning_used: false
llm_vision_used: false

general_learning_claimed: false
autonomous_learning_claimed: false
visual_understanding_claimed: false
symbol_grounding_solved_claimed: false
consciousness_claimed: false
subjective_experience_claimed: false
```
