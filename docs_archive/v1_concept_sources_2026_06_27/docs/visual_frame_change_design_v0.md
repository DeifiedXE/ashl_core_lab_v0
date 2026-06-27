# Visual Frame Change Design v0

Date: 2026-06-09

## Purpose

This document defines a design-only visual frame change layer for comparing a future `previous_frame` and `current_frame` pair and describing deterministic low-level differences as `change_record` structures.

This is design-only.
This is not runtime frame storage.
This is not runtime change detection.
This is not focus selection.
This is not object tracking.
This is not visual understanding.

## Scope

Visual Frame Change Design v0 defines:

```text
valid previous_frame
+ valid current_frame
-> conceptual change_record structures
```

It does not implement:

```text
runtime frame storage
runtime current_frame / previous_frame storage
automatic frame replacement
frame comparison runner
change detection runtime
visual change records runtime
focus selector
focus candidates
attention mechanism
action selection influence
memory write
predictor mutation
```

## Input Assumptions

`previous_frame` and `current_frame` must each be valid `visual_frame` records.

Each `visual_frame` must have passed `visual_frame_buffer_schema` validation.

Each feature record inside each frame must have passed `retina_decoder_feature_schema` validation.

No invalid frame may be used for a valid change comparison.

## previous_frame / current_frame Relationship

Future relationship:

```text
previous_frame = the earlier accepted valid visual_frame
current_frame = the later accepted valid visual_frame
```

For v0 design, this relationship is conceptual only:

```text
no runtime frame storage
no automatic current_frame replacement
no automatic previous_frame retention
no frame comparison runner
no change detection runtime
```

## Change Record Shape

A `change_record` is a deterministic description of low-level differences between two valid visual frames.

Conceptual shape:

```python
{
    "change_id": "change_demo_001",
    "previous_frame_id": "frame_demo_000",
    "current_frame_id": "frame_demo_001",
    "change_type": "feature_modified",
    "position": {"x": 1, "y": 0},
    "previous_feature_id": "feature_prev_001",
    "current_feature_id": "feature_curr_001",
    "changed_fields": ["brightness", "color_family"],
    "previous_values": {
        "brightness": "dark",
        "color_family": "blue_family"
    },
    "current_values": {
        "brightness": "bright",
        "color_family": "red_family"
    },
    "semantic_label": None,
    "source_trace": {
        "previous_frame_source": "visual_frame_assembly_from_retina_features",
        "current_frame_source": "visual_frame_assembly_from_retina_features",
        "comparison_layer": "visual_frame_change_design_v0"
    },
    "safety_flags": {
        "blocked_from_action_selection": True,
        "blocked_from_memory_write": True,
        "blocked_from_focus_selection": True,
        "blocked_from_endocrine_control": True,
        "object_recognition": False,
        "semantic_vision": False,
        "runtime_change_detection": False,
        "focus_candidate_created": False,
        "action_selection_influence": False,
        "memory_write": False,
        "focus_selection": False,
        "endocrine_control": False,
        "predictor_modified": False
    }
}
```

This is a design shape only.

## Change Types

Allowed low-level change types:

```text
feature_appeared
feature_disappeared
feature_modified
position_changed
no_change
```

Definitions:

```text
feature_appeared:
A position or feature key exists in current_frame but not previous_frame.

feature_disappeared:
A position or feature key exists in previous_frame but not current_frame.

feature_modified:
A feature exists in both frames but one or more low-level fields changed.

position_changed:
A feature-like record appears to have moved position under a deterministic non-semantic matching rule.

no_change:
No relevant low-level change was detected.
```

The definitions are low-level only. They do not identify objects, scenes, intentions, or meanings.

## Matching Rule Assumptions

v0 matching may only use deterministic low-level keys such as:

```text
position
feature_id if explicitly stable
source_trace if deterministic
symbol_hint only as non-semantic hint
```

v0 matching must not use:

```text
object identity tracking
semantic matching
LLM similarity
fuzzy visual similarity
learned visual embedding
```

`position_changed` is not object tracking.
It is only a low-level deterministic relation when safe matching keys exist.

## Source Trace Rule

Every `change_record` should keep source trace evidence for:

```text
previous_frame source
current_frame source
comparison layer name
validation lineage for both frames
retina feature schema lineage
runtime change detection not active
focus selection not active
memory write not active
```

Source trace is evidence only. It is not visual memory, object identity, action selection input, or proof of understanding.

## Semantic Boundary

A `change_record` is not scene understanding.

A `change_record` is not object tracking.

A `change_record` is not attention.

A `change_record` is not focus selection.

A `change_record` does not prove that Qingyin understands what changed.

`semantic_label` remains null.

Required wording:

```text
semantic_label remains null
```

Symbol hints and low-level matching keys are trace data, not semantic labels or object concepts.

## Safety Flags

Required v0 block flags:

```text
blocked_from_action_selection: true
blocked_from_memory_write: true
blocked_from_focus_selection: true
blocked_from_endocrine_control: true
```

Required v0 false or zero flags:

```text
object_recognition: false
semantic_vision: false
runtime_change_detection: false
focus_candidate_created: false
action_selection_influence: false or 0
memory_write: false or 0
focus_selection: false or 0
endocrine_control: false or 0
predictor_modified: false or 0
```

## Explicitly Not Implemented

```text
No runtime frame storage.
No runtime current_frame / previous_frame storage.
No automatic frame replacement.
No frame comparison runner.
No change detection runtime.
No visual change records runtime.
No focus selector.
No focus candidates.
No attention mechanism.
No endocrine connection.
No vision-driven action selection.
No action selection influence.
No visual memory write.
No memory write.
No long-term memory write.
No lesson_store write.
No Memory Layer write.
No predictor mutation.
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
Visual Frame Change Schema Check v0:
Define and validate a static change_record schema with invalid controls.

Visual Frame Pair Demo Assembly Check v0:
Construct a deterministic previous_frame / current_frame demo pair from valid visual_frame records.

Visual Frame Change Trace Check v0:
Produce checker-only change_record traces from a controlled frame pair without runtime storage.

Focus Selector Design v0:
Design how a future focus layer may inspect approved low-level change traces while staying blocked from action selection and memory writes.
```

## Boundary Check

```text
visual_frame_change_design_enabled: true
design_only: true
runtime_behavior_modified: false
new_cli_added: false

previous_frame_defined_as_design: true
current_frame_defined_as_design: true
change_record_shape_defined: true
change_types_defined: true

valid_visual_frame_required: true
visual_frame_buffer_schema_validation_required: true
retina_feature_schema_validation_required: true
invalid_frame_allowed_for_valid_comparison: false

runtime_frame_storage_added: false
current_frame_runtime_storage_added: false
previous_frame_runtime_storage_added: false
automatic_frame_replacement_added: false
frame_comparison_runner_added: false
change_detection_runtime_added: false
visual_change_records_runtime_added: false

focus_selector_added: false
focus_candidate_generation_added: false
attention_mechanism_added: false
endocrine_connection_added: false

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
