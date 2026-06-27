# ASHL Core / Qingyin lesson layer / Long-term Memory relation assumption v0.1

## Purpose

This document defines the relationship assumption between the ASHL Core lesson layer and Qingyin Long-term Memory.

It is a design assumption, not runtime implementation. It clarifies that the lesson layer and Long-term Memory are related but not identical.

## Core Statement

lesson is action correction knowledge.

Long-term Memory is reviewed continuity memory.

A lesson is not automatically memory. An approved lesson is not automatically written into Long-term Memory.

Only after repeated evidence, challenge, review, and conflict / stale / supersede checks may a lesson be summarized into a learned_principle candidate for future Long-term Memory review.

## Lesson Layer Role

The lesson layer supports:

- action selection
- action correction
- action retry strategy
- risk gates
- conflict / stale / supersede tracking

Example:

```text
Before approach unknown_object, observe / check_distance first.
```

This is a lesson because it corrects or constrains action.

## Long-term Memory Role

Long-term Memory stores reviewed continuity memory.

It may support:

- durable autobiographical context
- stable learned principles
- long-range continuity
- memory_contrast_set
- future evaluator input

Example:

```text
Qingyin has repeatedly learned that unknown objects should be observed before approach.
```

This is memory-like only after review and consolidation.

## Why Lesson Is Not Automatically Memory

Approval means a lesson may be used by the lesson layer. Approval does not mean the lesson becomes Long-term Memory.

Reasons:

- A lesson may be local to one task.
- A lesson may later become stale.
- A lesson may be superseded.
- A lesson may conflict with another lesson.
- A lesson may work only in a narrow action context.

Long-term Memory requires a separate review and consolidation path.

## learned_principle

`learned_principle` is the proposed bridge from reviewed lesson evidence to Long-term Memory.

Possible future flow:

```text
approved lesson
-> repeated usage evidence
-> challenge survival
-> review
-> learned_principle summary
-> Long-term Memory
```

`learned_principle` is not a raw lesson copy. It should summarize evidence, source_lessons, review state, and conflict / stale / supersede status.

## lesson_to_memory_promotion

`lesson_to_memory_promotion` is the proposed future process for moving from lesson evidence to a memory candidate.

Responsibility boundary:

```text
ASHL Core provides evidence.
Qingyin Memory Layers decide memory admission.
```

ASHL Core may provide a `learned_principle_candidate`, source lesson ids, usage evidence, challenge evidence, review evidence, conflict state, stale state, and supersede state.

Qingyin Memory Layers own the final decision about whether anything becomes Long-term Memory. ASHL Core does not directly write Long-term Memory.

It should require:

- source lesson
- usage history
- review history
- conflict state
- stale state
- supersede state
- learned_principle candidate
- human review

This document does not implement lesson_to_memory_promotion runtime.

This document does not implement Long-term Memory admission. The promotion boundary is intentionally split so that the lesson layer remains an evidence provider, while Memory Layers remain responsible for memory admission, persistence, and later memory review.

## Stale / Supersede and Memory Review

If a source lesson becomes stale or superseded after a learned_principle was created, related memory may need review.

Possible future flags:

```text
memory_may_need_review
source_lesson_superseded
source_lesson_stale
```

These are assumption terms only. This package does not implement memory review runtime.

## Negative Rules

This assumption explicitly rejects:

- lesson approved means automatic Long-term Memory write
- ASHL Core directly writes Long-term Memory
- learned_principle_candidate is automatically admitted into Long-term Memory
- Long-term Memory automatically controls lesson selection
- lesson stale / supersede automatically rewrites Long-term Memory
- Long-term Memory is directly treated as action rule
- raw lesson is stored as memory without review
- LLM output is directly written to Long-term Memory

## Boundary

- This document does not implement lesson_to_memory_promotion runtime.
- This document does not implement learned_principle generation.
- This document does not implement learned_principle_candidate admission.
- This document does not implement Long-term Memory write runtime.
- This document does not let ASHL Core directly write Long-term Memory.
- This document does not implement memory review runtime.
- This document does not implement memory_contrast_set runtime.
- This document does not implement lesson / memory automatic synchronization.
- This document does not change selection logic.
- This document does not change conflict logic.
- This document does not change review logic.
- This document does not change strict supersede activation.
- This document does not change known / unknown failure_reason behavior.
