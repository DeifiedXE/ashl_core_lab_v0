# Learning Engine Concept Candidate Teacher Review v0

## Purpose

This package adds the first teacher review layer for drafted
`ConceptCandidate` records.

It lets a teacher mark a draft as:

- needs more support
- scope narrowed
- split required
- teacher review ready
- rejected

## Plain Meaning

Package 62 drafts concept candidates from deterministic task closure material.

Package 63 lets the teacher mark that draft with a review decision. The mark is
not a final concept approval.

## Records

`ConceptCandidateTeacherReviewTask` presents the drafted candidate, support
evidence count, counterexample count, scope status, and allowed decisions.

`ConceptCandidateTeacherReviewDecision` records the teacher mark, note, reason
codes, confirmed support or counterexample references, and requested scope,
split, or more-evidence changes.

`ConceptCandidateTeacherReviewSummary` maps the decision to the next Learning
Engine step.

## Decision Meaning

`teacher_review_ready` means the candidate may proceed to a future
reviewed-concept preparation package.

It does not mean:

- concept approved
- reviewed concept created
- memory write allowed
- task behavior changed

## Non-Goals

This package does not create reviewed concepts, concept memory writes,
MemoryLearningTrace, MemoryApplicationData, readback hints, task behavior
changes, automatic learning approval, scheduler behavior, action execution, or
Core / Long-term / Archive / Anchor writes.

## Safe Claim

ASHL Core v1 Learning Engine can create teacher review tasks and teacher review
decisions for drafted `ConceptCandidate` records, without approving concepts,
writing memory, or changing task behavior.
