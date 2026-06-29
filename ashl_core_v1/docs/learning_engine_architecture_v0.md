# Learning Engine Architecture v0

## Purpose

Learning Engine is the v1 engine line for turning repeated task experience into reviewed concept candidates.

It starts after State Engine resume continuity v0 because the system now has enough controlled task, review, memory trace, readback, and resume handoff structure to ask a different question:

What experience difference is stable enough to become a concept candidate?

## Why Learning Engine Is Independent

Learning Engine is independent because concept extraction is not the same as task running, memory storage, thought selection, or teacher review.

Learning Engine owns:

- experience difference extraction
- concept candidate building
- support evidence ledger
- counterexample evidence ledger
- scope refinement
- generalization gate
- teacher review bridge
- promotion candidate preparation

Learning Engine is not:

- Task Engine
- Memory Engine
- Thought Engine
- Teacher Interface

## Position In Runtime Architecture R2

Updated engine map:

```text
Runtime
├── Task Engine
├── State Engine
├── Learning Engine
├── Memory Engine
├── Teacher Interface
├── Sense Interface
└── Output Interface
```

Learning Engine reads controlled evidence from task and memory traces, but it does not run tasks and does not write memory by itself.

## What Learning Engine Does

Learning Engine compares experience records and asks whether a reusable difference exists.

It may later prepare concept candidates from:

- state / action / outcome differences
- repeated supports
- contradictions
- teacher-reviewed learning records
- readback contrast evidence
- counterexamples

## What Learning Engine Does Not Do

Learning Engine v0 does not add runtime behavior.

It does not:

- run a task
- resume a task
- create a tick
- select an action
- execute an action
- approve learning automatically
- write Core Memory
- write Long-term Memory
- write Archive Memory
- create Anchor Layer records
- claim general learning

## Concept Definition

Concept = a teacher-reviewed experience difference that changes future task handling and has passed counterexample-aware scope checks.

概念 = 會改變下一次任務處理的、被審查過、且經過反例檢查的經驗差異。

## Support Evidence

Support evidence is the set of cases that makes a concept candidate plausible.

Example:

```text
front_blocked + step_forward -> blocked
front_blocked + step_forward -> blocked
front_blocked + direct_retry -> blocked
```

This support suggests that direct retry may be unhelpful under some blocked-front situations.

## Counterexample Evidence

Counterexamples are not automatic deletion.

Counterexamples refine concept boundaries.

Possible outcomes:

1. invalidate concept
2. narrow concept scope
3. split concept into more specific candidates

Plain example:

```text
front_blocked + step_forward -> blocked
```

Later:

```text
front_blocked + step_forward -> success
```

This does not automatically mean the concept is useless.

It may mean `front_blocked` was too broad and should split into:

- `front_wall_blocked`
- `front_box_pushable`
- `front_temporary_blocked`
- `front_unknown_obstacle`

## Scope Refinement

Scope refinement decides where a concept candidate applies.

A broad candidate like "blocked front means do not retry forward" may become narrower after counterexamples:

```text
front_wall_blocked -> avoid direct retry
front_box_pushable -> pushing may be valid
front_unknown_obstacle -> observe before deciding
```

## Generalization Gate

The generalization gate decides whether a concept candidate is allowed to move beyond a narrow case.

It must check:

- support evidence
- counterexample evidence
- scope statement
- teacher review status
- whether the candidate changes future task handling

No generalization is automatic in v0.

## Teacher Review Relation

Teacher Interface reviews concept candidates before they can influence memory application or future task handling.

Teacher review may approve, reject, defer, request more support, or request counterexample checks.

## Memory Engine Relation

Memory Engine stores and routes memory application data.

Learning Engine may prepare promotion candidates for Memory Engine, but it does not directly write Core, Long-term, Archive, or Anchor memory.

## Task Engine Relation

Task Engine produces task traces, outcomes, closures, readback contrasts, and loop evidence.

Learning Engine reads those records as evidence. It does not run the task runner.

## Thought Engine Relation

Thought Engine may later consume reviewed concept influence as candidate hints or reasoning context.

Learning Engine does not select thoughts or actions.

## State Engine Relation

State Engine preserves session handoff and resume continuity.

Learning Engine may use State Engine bookmarks to find evidence across controlled handoff chains, but it does not create autonomous cross-session growth.

## Minimum Concept Candidate Shape

Future conceptual data shape only:

```text
ConceptCandidate
- concept_candidate_id
- source_task_ids
- source_case_ids
- source_state_action_outcome_refs
- concept_label
- concept_summary
- support_evidence_refs
- counterexample_evidence_refs
- scope_statement
- scope_confidence
- generalization_level
- teacher_review_required
- memory_application_candidate_allowed
- promotion_candidate_allowed
- status
```

Allowed status examples:

- candidate
- needs_more_support
- blocked_by_counterexample
- scope_narrowed
- split_required
- teacher_review_ready
- reviewed
- retired

## Future Package Direction

Recommended next package:

```text
Package 61 / ASHL Core v1 Learning Engine Concept Candidate Architecture And Schema Minimal v0
```

Plain meaning:

Create the first `ConceptCandidate` schema and checker with support evidence refs and counterexample evidence refs.

Do not extract concepts yet.
Do not write memory.
Do not change task behavior.
