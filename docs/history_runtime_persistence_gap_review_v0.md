# History Runtime Persistence Gap Review v0

Status: design-only / review-only / no-runtime-change.

Snapshot:
- Boundary Index Version: 2026-06-09-b41
- latest completed commit: 9eb7b87 Add lesson candidate review evidence summary
- start smoke: py -3 run_all_smoke_tests.py PASS
- start unittest: py -3 -m unittest discover PASS, Ran 1739 tests
- git diff --check: PASS
- git status --short: clean

## Purpose

This review clarifies the gap between the current `Generalized Memory Exact-Key Bucket` checker and a future `history runtime`.

The question is whether current generalized memory cross-session behavior is backed by real persisted session history, or only by deterministic demo records. The cautious answer for v0 is:

The current Generalized Memory line demonstrates exact-key aggregation over cross-session demo experience records, not a true persisted history runtime.

This document records that gap without adding storage, memory write, persistent learning, persistent rule write, predictor mutation, action selection influence, lesson application, or runtime history lookup.

## Scope

This package reviews:
- Session Working Memory
- Generalized Memory Exact-Key Bucket
- cross-session demo experience records
- history runtime
- persistent history store
- repetition_key = not_evaluated
- similar_context_key exact-key aggregation
- safe next package options

It does not implement any runtime behavior.

## Terms

Session Working Memory:
Temporary in-session context/state. It does not by itself survive session boundaries.

Generalized Memory Exact-Key Bucket:
Deterministic aggregation/check over records grouped by exact `similar_context_key` or repetition-like key. In the current repository it is implemented as `ashl_core/generalized_memory_exact_key_bucket.py`.

Cross-session demo experience records:
Manually constructed or fixture-style records labeled as coming from multiple sessions. The current exact-key bucket checker builds these through `build_demo_cross_session_experience_records()`, and the records carry demo-style metadata.

History runtime:
Future mechanism that can query retained past event/experience records, including `repetition_key` / `similar_context_key` lookup.

Persistent history store:
Future storage layer that actually retains session A experience so session B can query it.

Long-term Memory:
A stronger memory layer for durable user/system knowledge or promoted tendencies. It is not the same as raw history runtime unless explicitly designed.

Memory Layer:
The broader project memory architecture. This review does not write to it and does not promote history records into it.

Persistent learning:
Any mechanism that changes future behavior or rules based on retained experience. It is not implemented by this review.

## Known Current Behavior

Current generalized memory exact-key behavior:
- builds deterministic demo records in code
- groups records by exact `similar_context_key`
- reports `pattern_count`
- reports `outcome_distribution`
- reports `source_session_ids`
- calculates confidence labels and future candidate eligibility
- keeps candidate creation disabled
- keeps predictor mutation disabled
- keeps action selection influence disabled
- keeps memory writes disabled

The checker boundary explicitly records that cross-session storage and persistent storage were not added.

## Generalized Memory Exact-Key Bucket Relationship

The Generalized Memory Exact-Key Bucket is a useful shape for future history runtime query logic.

It answers:
- if records are already available, can the system group exact matching contexts?
- can it compute pattern count, outcome distribution, dominant outcome ratio, and eligibility signals?
- can it keep fuzzy similarity, LLM similarity, predictor mutation, and action selection influence disabled?

It does not answer:
- where records came from
- whether records were retained from a previous real session
- who authorized retention
- whether session A records survive into session B
- whether runtime lookup exists

Therefore the bucket is evidence of aggregation logic, not proof of persistence.

## Session Working Memory vs History Runtime

Session Working Memory is the current in-session context/state surface. It can support immediate readback inside one running session, but it is not automatically a persistent history runtime.

History runtime would be a future read path over retained records. It would need defined record shape, retention rules, storage, lookup keys, and read-only evidence boundaries before it can safely exist.

Session Working Memory extended across sessions would become a different mechanism and must be explicitly designed. It should not be assumed from the exact-key bucket checker.

## Demo Cross-Session Records vs Real Persistence

Current cross-session generalized memory evidence uses cross-session demo experience records.

Those records are useful for deterministic testing because they simulate multiple `session_id` values and allow exact-key aggregation to be checked.

They do not prove:
- real persisted cross-session storage
- real session A to session B retention
- runtime history lookup
- runtime repetition_key evaluation
- persistent learning
- Memory Layer write
- Long-term Memory write

The safe interpretation is:

cross-session demo experience records are fixtures; they are not a true persisted history runtime.

## Repetition Key Issue

`repetition_key = not_evaluated` remains unresolved if no persisted history runtime exists.

A bucket can aggregate records if records are already present. But it cannot itself retain session A records into session B.

Therefore demo cross-session aggregation does not solve real repetition_key evaluation.

To evaluate repetition in a real runtime, the project still needs:
- a session experience record
- a retention / commit policy
- a persisted history store
- exact-key lookup by `repetition_key` / `similar_context_key`
- bucket aggregation over retained records
- read-only evidence for review

## Gap Statement

The missing layer is not the bucket algorithm. The missing layer is the persistence / retention path before the bucket:

session experience record -> retention / commit policy -> persisted history store -> exact-key lookup by repetition_key / similar_context_key -> bucket aggregation -> read-only evidence for review

Until that layer exists, generalized memory exact-key aggregation remains a deterministic checker over supplied records.

## Risk Areas Before Implementation

Before implementing any persisted history runtime, the project must review:
- what counts as an experience record
- what can be retained
- who authorizes retention
- whether retention is raw event history or promoted memory
- how long retained records survive
- whether retained history can influence action selection
- whether retained history can influence lesson review
- whether retained history can become persistent learning
- rollback / deletion / stale handling
- privacy / over-retention boundary

## Do-Not-Cross Boundaries

Do not add storage in this package.
Do not write memory in this package.
Do not enable persistent learning.
Do not create persistent rules.
Do not mutate predictor behavior.
Do not influence action selection.
Do not apply lessons.
Do not allow history runtime to approve or reject lessons.
Do not add runtime history lookup.
Do not evaluate repetition_key at runtime.
Do not add lesson_store write.
Do not add Long-term Memory write.
Do not add Memory Layer write.
Do not add autonomy.
Do not add endocrine runtime.
Do not add semantic vision.
Do not add consciousness or subjective claims.

## Safe Next Package Options

Option A: History Runtime Persistence Gap Review v0

Purpose:
Record the current gap between demo exact-key aggregation and true persisted history runtime.

Does:
Documents terms, current evidence, gap, risks, and safe follow-up options.

Does not do:
No storage, no memory write, no persistence, no runtime lookup.

Option B: Session Experience Record Schema Design v0

Purpose:
Design the shape of an experience record that could be retained later.

Does:
Defines fields, trace, safety flags, and retention eligibility fields.

Does not do:
No storage, no memory write, no persistence.

Option C: History Retention Boundary Review v0

Purpose:
Define what may be retained, who authorizes retention, and what remains forbidden.

Does:
Documents retention policy boundary.

Does not do:
No storage, no retained database, no write path.

Option D: Generalized Memory Exact-Key Bucket Source Audit v0

Purpose:
Audit which records currently feed exact-key buckets and whether they are demo fixtures or runtime outputs.

Does:
Maps source types and trust levels.

Does not do:
No new bucket logic, no persistence.

## Recommended Next Step

Recommended immediate next package:

Session Experience Record Schema Design v0

Reason:
Before persistent history can exist, the project needs a safe, trace-only definition of what an experience record is. This remains safer than implementing storage.

Alternative if the project wants more review before schema:

History Retention Boundary Review v0

## Boundary Summary

review_only: true
design_only: true
storage_added: false
memory_write_added: false
persistent_learning_added: false
persistent_rule_write_added: false
runtime_history_lookup_added: false
runtime_repetition_key_evaluation_added: false
action_selection_influence_added: false
lesson_application_added: false
predictor_mutation_added: false
autonomy_added: false
semantic_vision_claimed: false
consciousness_claimed: false
subjective_claims_added: false
