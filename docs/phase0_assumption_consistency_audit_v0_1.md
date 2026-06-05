# ASHL Core / Qingyin Phase 0 assumption consistency audit v0.1

## Purpose

This document audits the current Phase 0 / Memory assumption documents for consistency.

This is an audit document, not runtime implementation. It adds no capability. It checks whether the current design assumptions and negative boundaries are coherent across the docs set.

## Audit Target Docs

The audit covers:

- `docs/failure_reason_design_assumption_v0_1.md`
- `docs/instinct_lesson_layer_relation_assumption_v0_1.md`
- `docs/perception_layer_design_assumption_v0_1.md`
- `docs/phase0_behavior_curiosity_assumption_v0_1.md`
- `docs/phase0_failure_event_interface_assumption_v0_1.md`
- `docs/lesson_memory_layer_relation_assumption_v0_1.md`

## Index Consistency

Checked:

- README.md contains the Phase 0 Integration Assumptions index.
- README.md contains the Memory / Lesson Relation Assumptions index.
- docs/research_plan.md contains v2.6c-0.
- docs/research_plan.md contains v2.6c-1.
- docs/research_plan.md contains v2.6c-2.
- docs/research_plan.md contains v2.6c-3.
- docs/research_plan.md contains v2.6c-4.
- docs/research_plan.md contains v2.6c-5.

## failure_reason Consistency

Checked:

- failure_reason must be structured.
- failure_reason must be traceable.
- failure_reason must be reviewable.
- failure_reason must not be free-form LLM text.
- LLM is not the authoritative failure_reason source.
- no contrast, no authoritative failure_reason.

```text
No contradiction found in failure_reason assumptions.
```

## Phase 0 failure_event Consistency

Checked:

- Phase 0 lesson-layer input should be structured failure_event.
- Raw natural language failure description should not be the only lesson-layer input.
- failure_event should include motivation / goal / action_intent / expected_outcome / actual_outcome / evaluator / mismatch.
- failure_reason is normalized from failure_event.
- actual_outcome is not free-form LLM imagination.
- lesson_candidate should not depend only on raw natural language failure description.

```text
No contradiction found in failure_event interface assumptions.
```

## Instinct / Lesson Relation Consistency

Checked:

- Lesson can assist future instinct / drive behavior.
- Lesson can compete with other action candidates through explicit selection.
- A lesson may become instinct-like only through future familiarity-based internalization gates.
- Internalization is not implemented now.
- Lesson remains traceable and reviewable.
- Failure and conflict evidence remain part of lesson-layer governance.

```text
No contradiction found in instinct / lesson relation assumptions.
```

## Curiosity / Behavior Consistency

Checked:

- Phase 0 minimal behavior names are observe / approach / avoid / ask_for_help.
- Curiosity is a bounded trigger, not free roaming autonomy.
- Curiosity may suggest observe or ask_for_help candidates.
- Curiosity does not override selection, conflict, review, or activation logic.
- Curiosity runtime is not implemented.
- Attention weight runtime is not implemented.

```text
No contradiction found in curiosity / behavior assumptions.
```

## Similar-context Consistency

Checked:

- Similar situation should be based on explicit structured features.
- similar_context_hint is a trace hint, not proof.
- Similarity should not be fuzzy LLM-only matching.
- similar_context runtime is not implemented.

```text
No contradiction found in similar-context assumptions.
```

## Perception Consistency

Checked:

- Perception layer is not implemented.
- Visual input runtime is not implemented.
- perceptual_code runtime is not implemented.
- Perception remains a Phase 0 design assumption.
- perceptual_code is structured action-relevant representation.
- Phase 0 does not claim full symbol grounding.

```text
No contradiction found in perception assumptions.
```

## Lesson / Memory Relation Consistency

Checked:

- lesson is action correction knowledge.
- Long-term Memory is reviewed continuity memory.
- lesson is not automatically memory.
- lesson approved does not mean automatic Long-term Memory write.
- ASHL Core provides evidence.
- Qingyin Memory Layers decide memory admission.
- ASHL Core does not directly write Long-term Memory.
- lesson_to_memory_promotion runtime is not implemented.
- Long-term Memory write runtime is not implemented.

```text
No contradiction found in lesson / memory relation assumptions.
```

## Runtime Boundary Consistency

Checked that the current assumption docs do not claim the following runtime exists:

- Phase 0 sandbox runtime exists
- failure_event runtime exists
- evaluator runtime exists
- motivation runtime exists
- curiosity runtime exists
- attention weight runtime exists
- observe / approach / avoid / ask_for_help runtime exists
- perception runtime exists
- visual input runtime exists
- perceptual_code runtime exists
- similar_context runtime exists
- lesson_candidate builder runtime exists
- lesson_to_memory_promotion runtime exists
- Long-term Memory write runtime exists
- memory_contrast_set runtime exists
- conflict review resolution activation exists

```text
Runtime boundary remains docs-only.
```

## Audit Result

```text
Audit result: PASS
No design contradiction found among current Phase 0 / Memory assumption docs.
All checked assumptions remain docs-only and do not imply runtime implementation.
```
