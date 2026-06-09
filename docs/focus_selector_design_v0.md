# Focus Selector Design v0

Date: 2026-06-09

## Purpose

This document defines the first safe design for future `focus_candidate` records in ASHL Core / Qingyin.

A `focus_candidate` is a traceable low-level proposal that says:

```text
this position / feature / change may be worth inspecting next
```

This is design-only.
This is not runtime focus selection.
This is not attention control.
This is not action selection.
This is not visual understanding.

## Scope

Focus Selector Design v0 defines:

```text
validated low-level visual records
-> conceptual focus_candidate records
```

It does not implement:

```text
runtime focus selector
attention control
focus application
focus candidate ranking runtime
focus-to-action bridge
perception-to-action bridge
endocrine connection
action selection influence
memory write
predictor mutation
object recognition
object tracking
semantic vision
```

## Input Assumptions

Future focus candidates may come only from already validated low-level records:

```text
validated retina feature records
validated visual_frame records
validated visual frame change_records
```

For v0 design, focus candidates may refer to:

```text
feature_id
frame_id
change_id
position
changed_fields
source_trace
```

They must not require:

```text
object identity
object class
semantic label
scene meaning
LLM vision
learned visual embedding
```

## Focus Candidate Shape

Conceptual shape:

```python
{
    "focus_candidate_id": "focus_demo_001",
    "candidate_source": "visual_frame_change_trace",
    "source_frame_id": "frame_demo_001",
    "source_change_id": "change_demo_001",
    "source_feature_id": "feature_demo_001",
    "position": {"x": 1, "y": 0},
    "reason_codes": [
        "changed_fields_present",
        "high_contrast",
        "front_relation_present"
    ],
    "score_fields": {
        "change_salience": 0.5,
        "contrast_salience": 0.3,
        "front_relation_salience": 0.2,
        "novelty_proxy": 0.0,
        "total_score": 1.0
    },
    "semantic_label": None,
    "source_trace": {
        "retina_schema": "retina_decoder_feature_schema",
        "frame_schema": "visual_frame_buffer_schema",
        "change_schema": "visual_frame_change_schema",
        "design_layer": "focus_selector_design_v0"
    },
    "safety_flags": {
        "blocked_from_action_selection": True,
        "blocked_from_memory_write": True,
        "blocked_from_endocrine_control": True,
        "runtime_focus_selector": False,
        "attention_control": False,
        "focus_applied": False,
        "object_recognition": False,
        "object_tracking": False,
        "semantic_vision": False,
        "action_selection_influence": False,
        "memory_write": False,
        "endocrine_control": False,
        "predictor_modified": False
    }
}
```

This is a design shape only.

Required wording:

```text
semantic_label remains null
runtime_focus_selector = False
attention_control = False
focus_applied = False
```

## Focus Source Types

Allowed low-level source types:

```text
feature_salience
change_salience
contrast_salience
edge_like_salience
front_relation_salience
symbol_hint_salience
unknown_or_unstable_feature
```

Definitions:

```text
feature_salience:
A validated retina feature record has low-level fields that may be inspected further.

change_salience:
A validated change_record indicates low-level visual difference.

contrast_salience:
A retina feature has notable contrast field.

edge_like_salience:
A retina feature carries an edge_like field.

front_relation_salience:
A retina feature has front_relation information.

symbol_hint_salience:
A symbolic hint exists, but it is not a semantic label.

unknown_or_unstable_feature:
A low-level feature or change is unknown-like or unstable enough to remain trace-visible for review.
```

## Reason Codes

Possible low-level reason codes:

```text
changed_fields_present
contrast_present
edge_like_present
front_relation_present
symbol_hint_present
unknown_field_present
unstable_low_level_record
```

Reason codes explain trace provenance only. They are not object labels, action intents, or attention commands.

## Score Fields

Allowed design score fields:

```text
change_salience
contrast_salience
edge_salience
front_relation_salience
symbol_hint_salience
novelty_proxy
total_score
```

v0 design records score fields but does not define runtime score calculation.

No endocrine signal may alter focus score in v0.

No action selection may consume focus score in v0.

## Source Trace Rule

Every `focus_candidate` should keep source trace evidence for:

```text
retina feature schema
visual frame schema
change schema when sourced from change_records
source feature / frame / change identifiers
design layer name
runtime focus selector not active
attention control not active
focus not applied
```

Source trace is evidence only. It is not attention, memory, object identity, action selection input, or proof of understanding.

## Semantic Boundary

A `focus_candidate` is not attention.

A `focus_candidate` is not action intent.

A `focus_candidate` is not object recognition.

A `focus_candidate` is not object tracking.

A `focus_candidate` is not semantic vision.

A `focus_candidate` does not prove that Qingyin understands what she sees.

`semantic_label` remains null.

Symbol hints remain low-level hints, not semantic labels or object concepts.

## Downstream Safety Flags

Required v0 block flags:

```text
blocked_from_action_selection: true
blocked_from_memory_write: true
blocked_from_endocrine_control: true
```

Required v0 false or zero flags:

```text
runtime_focus_selector: false
attention_control: false
focus_applied: false
action_selection_influence: false or 0
memory_write: false or 0
endocrine_control: false or 0
predictor_modified: false or 0
object_recognition: false
object_tracking: false
semantic_vision: false
```

`blocked_from_focus_selection` is not used inside `focus_candidate`, because the record itself belongs to the future focus selector line. Instead v0 uses `runtime_focus_selector = False` and `focus_applied = False`.

## Explicitly Not Implemented

```text
No runtime focus selector.
No attention control.
No focus application.
No focus candidate ranking runtime.
No focus-to-action bridge.
No perception-to-action bridge.
No endocrine connection.
No norepinephrine-controlled attention.
No vision-driven action selection.
No action selection influence.
No visual memory write.
No memory write.
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
Focus Candidate Schema Check v0:
Validate static focus_candidate records with invalid controls for semantic labels and downstream unblocked flags.

Focus Candidate From Change Trace Check v0:
Create checker-only focus_candidate records from validated visual frame change_records.

Focus Candidate Ranking Trace Check v0:
Trace deterministic candidate ordering while keeping focus unapplied and blocked from action selection.

Perception-to-Action Boundary Review v0:
Review whether any future focus candidate may enter action context; required before any focus candidate can influence action context.
```

## Boundary Check

```text
focus_selector_design_enabled: true
design_only: true
runtime_behavior_modified: false
new_cli_added: false

focus_candidate_shape_defined: true
focus_source_types_defined: true
score_fields_defined_without_runtime_formula: true

runtime_focus_selector_added: false
attention_control_added: false
focus_application_added: false
focus_candidate_ranking_runtime_added: false
focus_to_action_bridge_added: false
perception_to_action_bridge_added: false
endocrine_connection_added: false
norepinephrine_controlled_attention_added: false

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
