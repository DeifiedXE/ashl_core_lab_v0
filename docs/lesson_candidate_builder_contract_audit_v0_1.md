# ASHL Core / Qingyin Lesson Candidate Builder Contract Audit v0.1

## Purpose

This document audits `lesson_candidate_builder_contract_v0_1.md`.

It is not a runtime implementation. It confirms that the v2.7d builder contract does not accidentally allow builder output to skip review, selection, activation, or Long-term Memory admission boundaries.

## Audit Result

Audit result: PASS

## Audited Contract

Audited document:

```text
docs/lesson_candidate_builder_contract_v0_1.md
```

Audited transition:

```text
lesson_candidate_input_trace
-> future lesson_candidate draft / candidate proposal
```

This is a contract audit, not a builder implementation.

## Checked Boundaries

- builder contract is docs-only / contract-only.
- builder output must be review-gated.
- builder output must not be approved by default.
- builder output must not be active by default.
- builder output must not be selection eligible by default.
- builder output must not be internalized by default.
- semantic_key remains non-authoritative and review-required.
- evidence_refs are evidence pointers, not proof or approval.
- proposed_action_correction is a review-gated draft, not an executable action.
- proposed_applicability_conditions are draft conditions, not verified applicability proof.
- evaluator judgment remains observable evidence, not absolute truth.
- ASHL Core provides evidence.
- Qingyin Memory Layers decide memory admission.

## Field Boundary Audit

### candidate_id / draft_id

Allowed as identifier only.

Must not imply approval, activation, or selection eligibility.

### proposed_lesson_summary

Allowed as draft summary.

If LLM-assisted in the future, it must be marked:

```text
summary_source = llm_assisted
summary_authority = non_authoritative
requires_review = true
```

Must not become authoritative failure_reason.

### proposed_applicability_conditions

Draft conditions only.

Not verified applicability proof.

Must not grant selection eligibility.

### proposed_action_correction

Draft correction only.

Not executable action.

Must not override instinct / drive layer without review.

### evidence_refs

Evidence pointers only.

Not proof.

Not approval.

Not Long-term Memory admission.

### similar_context_hint_refs

Hint pointers only.

semantic_key remains non-authoritative and review-required.

semantic_key is not proof.

semantic_key is not eligibility source.

### evaluator_source

Observable evidence only.

Not absolute truth.

### needs_review / review_state

Must remain pending / unreviewed unless a future review path explicitly changes it.

## v2.8a Dependency Note

v2.8a may define Lesson Candidate Draft Schema Trace-only only if it preserves the following:

```text
draft is not approved
draft is not active
draft is not selection eligible
draft is not internalized
draft does not write lesson_store
draft does not write Long-term Memory
draft remains review-gated
```

## Not Implemented

This audit does not implement:

- lesson_candidate builder runtime
- build_lesson_candidate()
- lesson_candidate draft schema implementation
- lesson_store write
- manual review runtime
- sandbox runtime
- evaluator runtime
- selection / activation / conflict behavior changes
- Long-term Memory write
- internalization / instinct-like behavior

Builder output must not bypass review.

Builder output must not enter selection automatically.

Builder output must not write lesson_store.

Builder output must not write Long-term Memory.

semantic_key is not proof.

evidence_refs are not proof.

proposed_action_correction is not executable action.

proposed_applicability_conditions are not verified applicability proof.
