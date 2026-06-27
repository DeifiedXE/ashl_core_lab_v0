# Focus Candidate Ranking Trace Design v0

Date: 2026-06-09

## Purpose

This document defines a design-only `ranking_trace` layer for future ordering records over validated `focus_candidate` records in ASHL Core / Qingyin.

A `ranking_trace` is a trace-only record that says:

```text
Given these focus candidates, this is their proposed ordering and the reasons for that ordering.
```

This is design-only.
This is not runtime ranking.
This is not runtime focus selection.
This is not active focus selection.
This is not attention control.
This is not focus application.
This is not action selection.
This is not visual understanding.

## Scope

Focus Candidate Ranking Trace Design v0 defines:

```text
validated focus_candidate records
-> conceptual ranking_trace records
```

It does not implement:

```text
runtime ranking
runtime focus selector
active_focus selection
focus application
attention control
focus candidate ranking runtime
focus-to-action bridge
perception-to-action bridge
endocrine runtime
endocrine-controlled attention
action selection influence
memory write
predictor mutation
object recognition
object tracking
semantic vision
```

## Input Assumptions

`ranking_trace` may only consume validated `focus_candidate` records.

Each `focus_candidate` must have passed `focus_candidate_schema` validation.

The design may reference:

```text
focus_candidate_id
candidate_source
source_change_id
reason_codes
score_fields
safety_flags
source_trace
```

It must not require:

```text
object identity
semantic label
scene understanding
LLM vision
learned visual embedding
runtime attention state
endocrine runtime state
```

## ranking_trace Concept

A `ranking_trace` records proposed ordering only.

`ranking_trace` does not select `active_focus`.

`ranking_trace` does not apply focus.

`ranking_trace` does not control attention.

`ranking_trace` does not influence action selection.

Conceptual shape:

```python
{
    "ranking_trace_id": "focus_ranking_demo_001",
    "source": "focus_candidate_from_change_trace",
    "input_focus_candidate_count": 3,
    "ranked_candidate_count": 3,
    "ranking_items": [
        {
            "focus_candidate_id": "focus_demo_001",
            "rank_position": 1,
            "score_snapshot": {
                "change_salience": 0.7,
                "contrast_salience": 0.0,
                "edge_salience": 0.0,
                "front_relation_salience": 0.0,
                "symbol_hint_salience": 0.0,
                "novelty_proxy": 0.0,
                "total_score": 0.7
            },
            "ranking_reason_codes": [
                "higher_total_score",
                "changed_fields_present"
            ],
            "tie_breaker": {
                "used": False,
                "method": None,
                "reason": None
            },
            "lock_prevention": {
                "cooldown_state": "not_applied",
                "decay_state": "not_applied",
                "interruptible": True,
                "forced_interrupt_reason": None,
                "attention_duration_exceeded": False,
                "external_mentor_interrupt_allowed": True
            }
        }
    ],
    "active_focus_id": None,
    "focus_applied": False,
    "attention_control": False,
    "semantic_label": None,
    "source_trace": {
        "focus_candidate_schema": "focus_candidate_schema",
        "focus_candidate_source": "focus_candidate_from_change_trace",
        "design_layer": "focus_candidate_ranking_trace_design_v0"
    },
    "safety_flags": {
        "blocked_from_action_selection": True,
        "blocked_from_memory_write": True,
        "blocked_from_endocrine_control": True,
        "runtime_ranking": False,
        "runtime_focus_selector": False,
        "attention_control": False,
        "focus_applied": False,
        "object_recognition": False,
        "object_tracking": False,
        "semantic_vision": False
    }
}
```

This is a design shape only.

Required wording:

```text
active_focus_id = None
focus_applied = False
attention_control = False
runtime_ranking = False
runtime_focus_selector = False
semantic_label remains null
```

## Ranking Item Shape

Each ranking item should preserve:

```text
focus_candidate_id
rank_position
score_snapshot
ranking_reason_codes
tie_breaker
lock_prevention
```

`rank_position` is trace evidence only.

It is not an attention command, action intent, or memory write.

## score_snapshot Rule

`score_snapshot` records the candidate score fields at the time the ranking trace was produced.

`total_score is a ranking reference, not a sole winner condition.`

A higher `total_score` may affect `rank_position` in a trace, but it must not by itself select `active_focus`.

A future runtime system must consider cooldown, decay, interruption, mentor instruction, and boundary review before applying focus.

No endocrine signal may alter score values in v0.

No runtime formula may be introduced for focus selection in v0.

## Tie Breaker Rule

If two candidates share the same `total_score`, a future trace may record a deterministic tie breaker.

Allowed conceptual tie breaker examples:

```text
source_order
stable_focus_candidate_id_order
manual_order_for_demo
```

Tie breakers are trace explanations only.
They do not select `active_focus`.
They do not apply focus.

## Cooldown / Decay / Interrupt Fields

Every ranking item should include lock-prevention fields:

```text
cooldown_state
decay_state
interruptible
forced_interrupt_reason
attention_duration_exceeded
external_mentor_interrupt_allowed
```

Future optional fields may include:

```text
attention_intensity_cap_state
attention_duration_tick_count
norepinephrine_like_interrupt_candidate
cortisol_like_forced_diffusion_required
```

These are design fields only in v0.

No endocrine runtime is implemented.

No attention runtime is implemented.

## Forced Interruption Priority

`external_mentor_interrupt` has unconditional priority in future focus application.

No focus application exists in this package.

The rule is recorded only as a future safety requirement.

## Allowed Ranking Reason Codes

Allowed design-level ranking reason codes:

```text
higher_total_score
lower_total_score
tie_same_total_score
changed_fields_present
change_salience_present
cooldown_would_reduce_rank
decay_would_reduce_rank
interruptible_candidate
external_mentor_interrupt_allowed
manual_order_for_demo
```

Any future checker should reject unknown reason codes.

For v0, these are documented only.

## Hard Boundaries

```text
no runtime focus selector
no runtime ranking
no active_focus selection
no focus application
no attention control
no focus candidate ranking runtime
no focus-to-action bridge
no perception-to-action bridge
no endocrine runtime
no endocrine-controlled attention
no norepinephrine-controlled attention runtime
no cortisol-controlled focus runtime
no action selection influence
no memory write
no predictor mutation
```

## Explicitly Not Implemented

```text
No runtime focus selector.
No runtime ranking.
No active_focus selection.
No focus application.
No attention control.
No focus candidate ranking runtime.
No focus-to-action bridge.
No perception-to-action bridge.
No endocrine runtime.
No endocrine-controlled attention.
No norepinephrine-controlled attention runtime.
No cortisol-controlled focus runtime.
No vision-driven action selection.
No action selection influence.
No memory write.
No visual memory write.
No long-term memory write.
No lesson_store write.
No Memory Layer write.
No predictor mutation.
No runtime frame storage.
No continuous frame comparison runtime.
No continuous change detection runtime.
No LLM vision.
No CNN / YOLO / UNet.
No image processing runtime.
No RGB quantization runtime.
No object recognition.
No object tracking.
No semantic matching.
No semantic labels.
No scene understanding.
No symbol grounding claim.
No consciousness claim.
No subjective visual experience claim.
```

## Future Follow-Up Packages

```text
Focus Candidate Ranking Trace Schema Check v0:
Validate static ranking_trace records, ranking items, score snapshots, tie breakers, allowed reason codes, and safety flags.

Focus Candidate Ranking Trace Check v0:
Create deterministic ranking_trace records from validated focus_candidates while keeping focus unapplied.

Focus Application Boundary Review v0:
Review whether any future active_focus or focus_applied behavior may exist and which safety gates are required.

Perception-to-Action Boundary Review v0:
Review whether any future perception or focus trace may enter action context.
```

Before any `active_focus` or `focus_applied` behavior exists, Perception-to-Action Boundary Review v0 must be completed.

## Boundary Check

```text
focus_candidate_ranking_trace_design_enabled: true
design_only: true
runtime_behavior_modified: false
new_cli_added: false

ranking_trace_shape_defined: true
ranking_item_shape_defined: true
score_snapshot_rule_defined: true
tie_breaker_rule_defined: true
lock_prevention_fields_defined: true

runtime_ranking_added: false
runtime_focus_selector_added: false
active_focus_selection_added: false
focus_application_added: false
attention_control_added: false
focus_candidate_ranking_runtime_added: false
focus_to_action_bridge_added: false
perception_to_action_bridge_added: false
endocrine_runtime_added: false
endocrine_controlled_attention_added: false

action_selection_modified: false
vision_used_for_action_selection: false
visual_memory_write: false
long_term_memory_write: false
lesson_store_write: false
memory_layer_write: false
predictor_modified: false
global_predictor_modified: false

object_recognition_enabled: false
object_tracking_enabled: false
semantic_matching_enabled: false
semantic_vision_claimed: false
scene_understanding_claimed: false
image_understanding_claimed: false

cnn_used: false
yolo_used: false
unet_used: false
llm_vision_used: false
llm_reasoning_used: false
llm_planning_used: false

symbol_grounding_solved_claimed: false
consciousness_claimed: false
subjective_visual_experience_claimed: false
```
