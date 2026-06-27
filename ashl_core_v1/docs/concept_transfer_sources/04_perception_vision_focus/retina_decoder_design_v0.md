# Retina Decoder Design v0

Date: 2026-06-09

## Purpose

This document defines the first safe design for converting low-level visual input into simple traceable visual features.

This is design-only.
This is not image understanding.
This is not object recognition.
This is not semantic vision.
This is not CNN / YOLO / UNet.

## Core Principle

Retina Decoder v0 converts low-level input into features, not meanings.

Example feature flow:

```text
RGB pixel / symbolic cell
-> brightness
-> color_family
-> contrast
-> edge_like_change
-> position
```

Not meanings:

```text
apple
door
enemy
friend
safe place
goal
```

## Input Types

### A. RGB Grid Input

Conceptual example:

```text
[
  [(255, 0, 0), (0, 0, 0)],
  [(128, 128, 128), (255, 255, 255)]
]
```

### B. Symbolic Pixel / Cell Input

Conceptual example:

```text
[
  ["w", "e", "i"],
  ["e", "a", "e"]
]
```

### C. Hybrid Structured Input

Conceptual example:

```text
cell = {
  "symbol": "i",
  "rgb": [220, 40, 40],
  "position": [1, 2]
}
```

v0 may design all three, but implementation may start with symbolic/hybrid inputs.

## Output Feature Shape

Conceptual feature record:

```text
feature_id
source_input_id
position
raw_symbol
raw_rgb
brightness
color_family
contrast_to_neighbors
edge_like
front_relation
center_relation
known_symbol_hint
feature_confidence
source_trace
semantic_label
```

Important:

```text
semantic_label must be null in v0.
```

## Feature Types

### brightness

Coarse labels:

```text
dark / mid / bright
```

or numeric:

```text
0.0 to 1.0
```

### color_family

Allowed coarse families:

```text
red_family
green_family
blue_family
yellow_family
cyan_family
magenta_family
gray_family
black_family
white_family
unknown_color
```

### contrast_to_neighbors

```text
low / medium / high
```

### edge_like

```text
true / false
```

This means:

```text
neighboring cells differ enough to be considered an edge-like boundary
```

It does not mean object edge recognition.

### position

```text
row
col
relative position
```

### front_relation

If agent facing exists:

```text
front
left
right
behind
center
unknown
```

v0 must not make action decisions from this.

### known_symbol_hint

For symbolic inputs:

```text
w / e / i / d / g / a / unknown
```

This is a hint, not semantic understanding.

## Color Family Rule

Safe coarse color quantization may later use:

```text
RGB -> dominant channel -> color_family
low saturation -> gray_family
low brightness -> black_family
high brightness + low saturation -> white_family
```

Do not implement formula in this package.

v0 design may later use deterministic thresholds.
No ML color classifier.

## Symbolic Input Boundary

For symbolic cells:

```text
w = wall-like symbol hint
e = empty-like symbol hint
i = item-like symbol hint
d = passage-like symbol hint
g = goal/exit-like placeholder hint
a = agent marker
```

Boundary:

```text
symbol hint is not visual understanding.
symbol hint is not object concept.
symbol hint is not semantic proof.
```

## Relationship To Previous Vision Work

Related previous work:

```text
Simulated Vision Facing Viewport
First-Person Viewport Correction
Observed Local Map
Larger Sandbox Symbol Contact
```

Previous symbolic vision showed what is in front.

Retina decoder v0 defines how lower-level visual input may become feature records before symbolic or focus layers use it.

## Relationship To Next Planned Modules

### Visual Frame Buffer

Retina features from previous frame and current frame can later be compared.

Frame buffer is not implemented here.

### Focus Selector

Focus selector may later consume feature salience.

Focus selector is not implemented here.

### Mimetic Endocrine System

Future design may explore:

```text
norepinephrine_like may later modulate attention threshold.
dopamine_like may later influence focus priority.
```

No endocrine connection in v0.

## Forbidden v0 Claims

```text
No image understanding.
No object recognition.
No semantic vision.
No CNN / YOLO / UNet.
No learned visual model.
No focus control.
No visual memory write.
No action selection influence.
No endocrine signal connection.
No solved symbol grounding.
No consciousness claim.
No subjective visual experience claim.
```

## Future Implementation Packages

Possible future packages:

```text
Retina Decoder Feature Schema v0
Retina Decoder RGB Quantization Check v0
Symbolic Pixel Feature Decoder v0
Visual Frame Buffer Design v0
Visual Frame Difference Check v0
Simple Focus Selector Design v0
```

CNN / YOLO / UNet are out of current scope.

## Boundary Check

```text
retina_decoder_design_enabled: true
design_only: true
runtime_behavior_modified: false
new_cli_added: false

rgb_input_supported_as_design: true
symbolic_pixel_input_supported_as_design: true
hybrid_input_supported_as_design: true

low_level_feature_output_defined: true
brightness_feature_defined: true
color_family_feature_defined: true
contrast_feature_defined: true
edge_like_feature_defined: true
position_feature_defined: true

semantic_label_required_null_v0: true
object_recognition_enabled: false
image_understanding_claimed: false
semantic_vision_claimed: false

cnn_used: false
yolo_used: false
unet_used: false
learned_visual_model_used: false

focus_selector_added: false
frame_buffer_added: false
endocrine_connection_added: false

visual_memory_write: false
long_term_memory_write: false
lesson_store_write: false
memory_layer_write: false

action_selection_modified: false
vision_used_for_action_selection: false

pathfinding_used: false
route_planner_added: false
llm_vision_used: false
llm_reasoning_used: false
llm_planning_used: false

symbol_grounding_solved_claimed: false
consciousness_claimed: false
subjective_visual_experience_claimed: false
```
