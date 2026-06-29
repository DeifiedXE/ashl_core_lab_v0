# Learning Engine Concept Candidate Refinement From Teacher Review v0

## Purpose

This package turns teacher review decisions on drafted `ConceptCandidate`
records into explicit refinement outputs.

## Plain Meaning

The teacher can mark a draft as needing more evidence, needing a narrower scope,
needing a split, being ready for a future reviewed-concept preparation package,
or being rejected.

Package 64 records the next draft-level artifact for that mark.

## Refinement Outputs

- `ConceptEvidenceRequestRecord` for `needs_more_support`
- `ScopeNarrowedConceptDraftRecord` for `scope_narrowed`
- `SplitConceptDraftSetRecord` for `split_required`
- `FutureReviewedConceptPreparationMarker` for `teacher_review_ready`
- `ConceptCandidateStopRecord` for `rejected`

## Boundary

These outputs are still draft/refinement records.

They do not approve a concept.
They do not create a reviewed concept.
They do not write memory.
They do not change task behavior.

## Safe Claim

ASHL Core v1 Learning Engine can transform teacher review decisions on drafted
`ConceptCandidate` records into refinement outputs such as evidence requests,
narrowed-scope draft candidates, split draft candidates, future reviewed-concept
preparation markers, or stopped-candidate records, without approving concepts,
writing memory, or changing task behavior.

## Non-Goals

This package does not create reviewed concepts, concept memory writes,
MemoryLearningTrace, MemoryApplicationData, readback hints, concept promotion,
task behavior changes, persistent refinement storage, scheduler behavior,
action execution, or Core / Long-term / Archive / Anchor writes.
