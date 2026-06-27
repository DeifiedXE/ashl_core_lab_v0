# Simple Visual Frame Buffer Design v0

Date: 2026-06-09

## Purpose

This document defines a simple visual frame buffer design for grouping already validated Retina Decoder feature records into visual frames.

This is design-only.
This is not runtime frame buffering.
This is not frame comparison.
This is not focus selection.
This is not visual understanding.

## Scope

Simple Visual Frame Buffer v0 defines:

```text
validated retina feature records
-> visual_frame
-> future current_frame / previous_frame relationship
```

It does not implement:

```text
runtime storage
automatic frame replacement
frame comparison
change detection
focus candidate generation
action selection influence
memory write
```

## Input Assumptions

A visual frame may only contain retina feature records that pass `retina_decoder_feature_schema` validation.

The expected upstream source in the current line is:

```text
Retina Decoder Symbolic Feature Decode Check v0
-> Retina Decoder Feature Schema v0 validation
-> valid retina feature records
```

Invalid feature records must not enter a valid frame.

## Visual Frame Shape

Conceptual shape:

```python
{
    "frame_id": "frame_demo_001",
    "frame_source": "symbolic_demo",
    "frame_index": 0,
    "tick": None,
    "created_from": "retina_decoder_symbolic_feature_decode",
    "feature_records": [...],
    "feature_record_count": 4,
    "valid_feature_record_count": 4,
    "invalid_feature_record_count": 0,
    "semantic_label_non_null_count": 0,
    "source_trace": {
        "input_type": "symbolic_or_hybrid_demo",
        "decoder": "retina_decoder_symbolic_feature_decode",
        "schema": "retina_decoder_feature_schema"
    },
    "safety_flags": {
        "blocked_from_action_selection": True,
        "blocked_from_memory_write": True,
        "blocked_from_focus_selection": True,
        "blocked_from_endocrine_control": True,
        "object_recognition": False,
        "semantic_vision": False,
        "runtime_frame_buffer": False,
        "frame_change_runtime": False
    }
}
```

This is a design shape only.

## Frame Metadata

Suggested metadata:

```text
frame_id
frame_source
frame_index
tick
created_from
feature_record_count
valid_feature_record_count
invalid_feature_record_count
semantic_label_non_null_count
source_trace
safety_flags
```

`tick` may remain `None` for demo or design-only contexts.

## current_frame / previous_frame Relationship

Future relationship:

```text
previous_frame = last accepted visual frame
current_frame = newest accepted visual frame
```

For this package:

```text
no runtime storage
no automatic frame replacement
no frame comparison
no change detection
no focus candidate generation
```

## Feature Record Reference Rule

A valid visual frame may reference or contain only retina feature records that pass Retina Decoder Feature Schema v0 validation.

Required feature-level boundary:

```text
semantic_label remains null
blocked_from_action_selection remains true
blocked_from_memory_write remains true
blocked_from_focus_selection remains true
blocked_from_endocrine_control remains true
```

The frame may summarize counts, but it must not reinterpret features as objects, scenes, goals, or meanings.

## Source Trace Rule

Every visual frame should keep a source trace showing:

```text
input type
decoder/check source
schema validation source
feature record ids
runtime frame buffer not active
frame change runtime not active
```

Source trace is evidence only. It is not visual memory, runtime perception, action selection input, or proof of understanding.

## Safety Flags

Required v0 safety flags:

```text
blocked_from_action_selection: true
blocked_from_memory_write: true
blocked_from_focus_selection: true
blocked_from_endocrine_control: true
object_recognition: false
semantic_vision: false
runtime_frame_buffer: false
frame_change_runtime: false
visual_memory_write: false
long_term_memory_write: false
lesson_store_write: false
memory_layer_write: false
predictor_mutation: false
```

## Semantic Boundary

A visual frame is not an object map.

A visual frame is not scene understanding.

A visual frame does not prove that Qingyin understands what she sees.

`semantic_label` remains null at the retina feature level.

Symbol hints and feature groupings remain low-level trace data, not object concepts or semantic proof.

## Explicitly Not Implemented

```text
No runtime visual frame buffer.
No runtime current_frame / previous_frame storage.
No automatic frame replacement.
No frame comparison.
No frame change detection.
No focus selector.
No focus candidate generation.
No attention mechanism.
No endocrine connection.
No vision-driven action selection.
No visual memory write.
No long-term memory write.
No lesson_store write.
No Memory Layer write.
No predictor mutation.
No CNN / YOLO / UNet.
No image processing runtime.
No RGB quantization runtime.
No object recognition.
No semantic labels.
No scene understanding.
No symbol grounding claim.
No consciousness claim.
No subjective visual experience claim.
```

## Future Follow-Up Packages

Possible future packages:

```text
Simple Visual Frame Buffer Schema v0
Visual Frame Construction Check v0
Visual Frame Difference Design v0
Visual Frame Difference Check v0
Simple Focus Selector Design v0
```

Next implementation should stay checker-only unless a future work package explicitly authorizes runtime frame buffering.

## Boundary Check

```text
simple_visual_frame_buffer_design_enabled: true
design_only: true
runtime_behavior_modified: false
new_cli_added: false

visual_frame_shape_defined: true
current_frame_defined_as_design: true
previous_frame_defined_as_design: true

validated_retina_feature_records_required: true
invalid_feature_records_allowed_in_valid_frame: false
semantic_label_required_null_v0: true

runtime_frame_buffer_added: false
current_frame_runtime_storage_added: false
previous_frame_runtime_storage_added: false
automatic_frame_replacement_added: false
frame_comparison_added: false
frame_change_runtime_added: false

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
