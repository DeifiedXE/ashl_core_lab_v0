# Learning Engine Concept Candidate Schema v0

## Purpose

This note records the first concrete Learning Engine schema boundary.

Package 61 defines `ConceptCandidate`, `ConceptEvidenceRef`, `ConceptScopeStatement`, and validation checks.

It does not extract concepts from task records.

## Candidate Only

The schema encodes the project definition:

Concept = a teacher-reviewed experience difference that changes future task handling and has passed counterexample-aware scope checks.

概念 = 會改變下一次任務處理的、被審查過、且經過反例檢查的經驗差異。

Package 61 only creates `ConceptCandidate`, not a final concept.

## Evidence

Support evidence makes a candidate plausible.

Counterexample evidence does not automatically delete a candidate.

Counterexamples force one of:

1. invalidate concept candidate
2. narrow concept scope
3. split concept into more specific candidates

## Minimum Demo

Support:

```text
front_blocked + step_forward -> blocked
```

Counterexample:

```text
front_blocked + step_forward -> success
```

The counterexample should force refinement such as:

- `front_wall_blocked`
- `front_box_pushable`
- `front_temporary_blocked`
- `front_unknown_obstacle`

## Non-Goals

No concept extraction runtime.
No automatic concept candidate creation from task closures.
No teacher review flow for concept candidates.
No MemoryLearningTrace.
No MemoryApplicationData.
No readback hint.
No task behavior change.
No memory write.
No concept promotion.
