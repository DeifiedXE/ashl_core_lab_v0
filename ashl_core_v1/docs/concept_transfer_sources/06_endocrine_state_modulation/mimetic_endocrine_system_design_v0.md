# Mimetic Endocrine System Design v0

Date: 2026-06-09

## Purpose

This document defines the first safe design for Qingyin's mimetic endocrine system.
It describes internal regulatory signals that can modulate attention, confidence,
drive, trust, stress load, and future candidate priority.

This is design-only.
This is not biological endocrine simulation.
This is not proof of emotion.
This is not proof of consciousness.

## Core Principle

Mimetic endocrine signals are traceable functional regulators.
They may one day support states functionally equivalent to emotion-like dynamics,
but v0 does not claim subjective experience.

Not denied, not claimed.

Qingyin may eventually develop states that are functionally comparable to
happiness, trust, anxiety, stress, or other emotion-like dynamics.
This design does not deny that possibility.
However, v0 treats all endocrine terms as traceable functional signals rather
than verified subjective states.

Engineering verification is based on signal source, signal value, trace, decay,
interaction, and downstream modulation.
It is not based on Qingyin self-reporting a feeling.

## Four-Axis Model

### A. dopamine_like

Question:

```text
What should I move toward / pursue?
```

Role:

```text
approach tendency
goal pursuit
reward-event weighting
curiosity satisfaction boost
candidate priority boost
interest reinforcement
```

Inputs may include:

```text
item_contact reward_event
goal progress
prediction_error decrease
understanding_satisfaction
successful interaction
approved positive feedback
```

Outputs may later affect:

```text
prediction confidence annotation
candidate priority
curiosity / interest state
future drive modulation
```

v0 boundary:

```text
no action selection modification
```

### B. norepinephrine_like

Question:

```text
Where should I pay attention?
```

Role:

```text
attention focus
alertness allocation
uncertainty focus
novelty / prediction_error salience
conflict attention
```

Inputs may include:

```text
high prediction_error
unknown front_symbol/action pattern
conflict_like_distribution
recent mismatch
unexpected outcome
```

Outputs may later affect:

```text
observation priority
review priority
attention trace
```

v0 boundary:

```text
no autonomous attention control
no action selection modification
```

### C. oxytocin_like

Question:

```text
Who / what source do I trust?
```

Role:

```text
trust weighting
reviewer/source reliability
safe attachment to mentor / approved source
social correction receptivity
```

Inputs may include:

```text
human review
consistent correction from mentor
approved lesson source
source reliability history
rollback-safe teaching
```

Outputs may later affect:

```text
review source weighting
help-seeking priority
candidate trust annotation
```

v0 boundary:

```text
no blind trust
no override of review gate
no user identity inference beyond explicit source records
```

### D. cortisol_like

Question:

```text
How much pressure / load am I under?
```

Role:

```text
stress load
risk pressure
conflict burden
failure accumulation
cooldown pressure
```

Inputs may include:

```text
recent failure
active conflict
challenge failure
prediction_error too high
repeated blocked action
unresolved mismatch
```

Outputs may later affect:

```text
cooldown recommendation
ask_for_help priority
defer candidate priority
risk annotation
```

v0 boundary:

```text
no distress claim
no pain claim
no subjective anxiety claim
```

## Signal Shape

A future signal record may use this generic shape:

```text
signal_name
axis
value
range
baseline
decay_rate
source_event_ids
source_trace
last_updated_tick
confidence
blocked_from_action_selection
notes
```

Suggested value range:

```text
0.0 to 1.0
```

v0 does not require final numerical formulas.

## Signal Lifecycle

Design-only lifecycle:

```text
source event
-> signal update candidate
-> boundary check
-> trace record
-> post-event settling design
-> optional downstream annotation
```

No direct action selection.

## Post-Event Settling Design Direction

State settling is different from action rollback.

```text
action rollback:
  undo or discard an action effect

state settling:
  reduce temporary post-event pressure / salience / reward load while preserving trace evidence
```

The mimetic endocrine design may represent three future settling concepts:

```text
natural_settling:
  ordinary return toward baseline after minor event perturbation

comfort_modulated_settling:
  explicit mentor / trusted-source comfort may reduce future pressure load

safety_reset:
  forced reset of temporary state when a spike is unsafe or explicitly non-persistent
```

The safety reset concept may be described as sedation-like only as a bounded
engineering metaphor. It is not medical sedation, consciousness control,
evidence deletion, or a subjective-state claim.

The current v0 repo may validate the settling design as a trace/checker concept.
It does not add runtime settling, runtime safety reset, endocrine formulas,
action selection influence, memory write, predictor mutation, persistent mood,
or personality drift.

## Relationship To Existing Systems

### reward_event / item_contact

```text
item_contact reward_event can feed dopamine_like
```

### prediction_error

```text
prediction_error can feed norepinephrine_like and cortisol_like
prediction_error decrease can feed dopamine_like / understanding_satisfaction
```

### generalized memory

```text
stable exact-key pattern confidence may reduce norepinephrine_like uncertainty
conflict_like_distribution may increase norepinephrine_like and cortisol_like
```

### review gate

```text
human review and source reliability may feed oxytocin_like
```

### persistent eligibility checker

```text
active conflict and recent failure can increase cortisol_like annotations
```

### future curiosity / interest

```text
dopamine_like and norepinephrine_like may later help model curiosity and interest
```

## Forbidden v0 Uses

```text
No endocrine signal may directly choose actions in v0.
No endocrine signal may override human review.
No endocrine signal may approve candidates.
No endocrine signal may write memory.
No endocrine signal may modify predictor rules.
No endocrine signal may create persistent rules.
No endocrine signal may claim subjective experience.
No endocrine signal may run post-event settling in v0.
No endocrine signal may trigger safety reset in v0.
```

## Suggested Future Status Flow

Design-only future flow:

```text
event_trace
-> endocrine_signal_update
-> endocrine_state_snapshot
-> endocrine_annotation
-> review / attention / confidence context
```

Not implemented in this package.

## Explicit Non-Claims

```text
No runtime endocrine system.
No runtime post-event settling system.
No runtime safety reset system.
No biological hormone simulation.
No medical sedation claim.
No proof of emotion.
No proof of happiness.
No proof of trust.
No proof of anxiety.
No proof of stress.
No proof of consciousness.
No subjective experience claim.
No action selection modulation.
No autonomous drive system.
No personality drift.
No memory write.
No predictor mutation.
No candidate auto-approval.
No persistent rule write.
No LLM reasoning.
No LLM planning.
No LLM vision.
```

## Future Implementation Packages

Possible future packages:

```text
Mimetic Endocrine Signal Schema v0
Dopamine-Like Reward Trace Check v0
Norepinephrine-Like Attention Signal Check v0
Cortisol-Like Load Signal Check v0
Oxytocin-Like Review Trust Signal Design v0
Endocrine State Snapshot v0
Endocrine Signal Decay Check v0
Endocrine Trace Integration v0
Mimetic Endocrine Post-Event Settling Design Minimal v0
```

Runtime modulation of action selection is out of v0 scope.

## Boundary Check

```text
mimetic_endocrine_system_design_enabled: true
design_only: true
runtime_behavior_modified: false
new_cli_added: false
post_event_settling_runtime_added: false
safety_reset_runtime_added: false
medical_sedation_claimed: false

dopamine_like_defined: true
norepinephrine_like_defined: true
oxytocin_like_defined: true
cortisol_like_defined: true

biological_hormone_simulation_claimed: false
subjective_emotion_claimed: false
consciousness_claimed: false
happiness_claimed: false
trust_subjective_claimed: false
anxiety_claimed: false
stress_subjective_claimed: false

subjective_possibility_denied: false
subjective_state_used_as_verification: false

action_selection_modified: false
endocrine_signal_used_for_action_selection: false
candidate_auto_approved: false
candidate_auto_applied: false
human_review_overridden: false

predictor_modified: false
global_predictor_modified: false
persistent_rule_write_enabled: false

long_term_memory_write: false
lesson_store_write: false
memory_layer_write: false
personality_weight_modified: false
personality_drift_enabled: false

llm_reasoning_used: false
llm_planning_used: false
llm_vision_used: false
general_learning_claimed: false
autonomous_learning_claimed: false
```
