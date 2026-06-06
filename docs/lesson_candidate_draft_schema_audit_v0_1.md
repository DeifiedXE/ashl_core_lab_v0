# ASHL Core / Qingyin Lesson Candidate Draft Schema Audit v0.1

## Purpose

This document audits the v2.8a `lesson_candidate_draft` schema and `build_lesson_candidate_draft_trace()`.

It is not a runtime implementation. It confirms that `lesson_candidate_draft` remains a trace-only / review-gated draft and cannot be used as an approved, active, executable, selectable, or memory-writing lesson.

## Audit Result

Audit result: PASS

## Audited Files

```text
ashl_core/lesson_candidate_drafts.py
docs/lesson_candidate_draft_schema_v0_1.md
tests/test_lesson_candidate_drafts.py
```

Pipeline:

```text
lesson_candidate_input_trace
-> lesson_candidate_draft
```

## Checked Boundaries

- lesson_candidate_draft is not an approved lesson_candidate.
- lesson_candidate_draft is not active.
- lesson_candidate_draft is not selection eligible.
- lesson_candidate_draft is not internalized.
- lesson_candidate_draft is not written to lesson_store.
- lesson_candidate_draft is not written to Long-term Memory.
- every main draft field declares source / authority / review_required.
- semantic_key is not proof.
- evidence_refs are evidence pointers, not proof or approval.
- proposed_action_correction is a draft correction, not an executable action.
- proposed_applicability_conditions are draft conditions, not verified applicability proof.
- review_required is a review gate, not a convenience flag.
- review_required must not be set to false without an explicit reviewed authority path.

## review_required False Boundary

At v2.8a stage:

```text
review_required must be True for every main draft field.
```

The draft helper must not produce:

```text
review_required = false
review_required = null
missing review_required
```

If a future system allows `review_required = false`, it must define:

- who can set it
- which review path authorizes it
- which reviewed result is required
- what trace is recorded
- whether it can only occur after draft review

Until that design exists:

```text
review_required = false is not allowed in lesson_candidate_draft generation.
```

## Field Audit

### proposed_lesson_summary

Must have source / authority / review_required.

Must remain non-authoritative.

### proposed_applicability_conditions

Draft conditions only.

Not verified applicability proof.

### proposed_action_correction

Draft correction only.

Not executable action.

### evidence_refs

Evidence pointers only.

Not proof.

Not approval.

### similar_context_hint_refs

Hint pointers only.

semantic_key remains non-authoritative and review-required.

### evaluator_source

Observable evidence only.

Not absolute truth.

## v2.8a-1 Invariant

v2.8a draft schema may remain trace-only if:

```text
draft is not approved
draft is not active
draft is not selection eligible
draft is not internalized
draft does not write lesson_store
draft does not write Long-term Memory
all main fields require review
review_required cannot be false without reviewed authority path
```

## Forbidden Conclusions

The current draft must not imply:

- draft is approved lesson_candidate
- draft can skip review
- draft can be selected
- draft can be activated
- draft can be internalized
- draft can write lesson_store
- draft can write Long-term Memory
- review_required can be false by default
- semantic_key can be proof
- evidence_refs can be proof
- proposed_action_correction can be executed
- proposed_applicability_conditions are verified applicability proof
