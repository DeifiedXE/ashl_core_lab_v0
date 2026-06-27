# Body-Motor Affordance / Tendency / Endocrine Reconciliation Design v0

---

## Purpose

This document reconciles the action line and the mimetic endocrine line after:

```text
Body-Motor Feedback-Gated Candidate Reordering Approval Boundary Minimal v0
```

The goal is to define how these concepts must remain separate:

```text
affordance_confidence
tendency_score
endocrine_signal
ordering_score
purpose
selected_action
```

The core boundary is:

```text
tendency may affect candidate ordering only inside an existing approved purpose.
tendency must not create purpose.
```

And:

```text
endocrine signals may modulate context, but must not create purpose or directly choose action.
```

This document is design-only. It does not add runtime behavior, candidate ordering, selected_action, final_action, direct command, motor execution, memory write, retention write, predictor mutation, production behavior, or proof-of-learning claims.

---

## Source Documents

This design extends and constrains:

```text
docs/mimetic_endocrine_system_design_v0.md
docs/body_motor_feedback_to_affordance_confidence_design_v0.md
```

Relevant endocrine design rule:

```text
No endocrine signal may directly choose actions in v0.
No endocrine signal may approve candidates.
No endocrine signal may write memory.
No endocrine signal may modify predictor rules.
```

Relevant body-motor design correction:

```text
body feedback may change short-lived affordance confidence before it changes candidate ordering.
affordance confidence is not action selection.
```

---

## Layer Definitions

### 1. Purpose

Purpose answers:

```text
What is the current approved task / question / scope?
```

Examples:

```text
explore this sandbox
observe the front cell
test whether step_forward is feasible
inspect nearby item
stop after budget
```

Purpose must come from:

```text
human instruction
approved sandbox fixture
approved scenario
explicit task scope
validated test harness
```

Purpose must not come from:

```text
tendency_score
affordance_confidence
endocrine_signal
reward event
dopamine_like trace
successful movement feedback
memory influence preview
candidate ordering
```

### 2. Affordance Confidence

Affordance confidence answers:

```text
Does this body capability currently look feasible in this sandbox state?
```

Examples:

```text
movement_affordance_confidence
reach_affordance_confidence
blocked_affordance_confidence
```

Affordance confidence is body feasibility evidence.

It is not:

```text
desire
purpose
tendency
candidate ordering
selected_action
```

### 3. Tendency Score

Tendency score answers:

```text
Within the current approved purpose, which candidate looks more worth considering?
```

Examples:

```text
check_before_retry: 0.60
retry_same_action_without_check: 0.45
pause_and_observe: 0.50
```

Tendency score is action consideration pressure.

It is not:

```text
purpose
goal creation
task creation
desire
authorization
selected_action
```

### 4. Endocrine Signal

Endocrine signal answers:

```text
What functional regulatory context is active?
```

Examples from the mimetic endocrine design:

```text
dopamine_like: approach / reward-event weighting / curiosity satisfaction boost
norepinephrine_like: salience / uncertainty / alertness allocation
oxytocin_like: trust / source reliability / review receptivity
cortisol_like: pressure load / conflict burden / cooldown pressure
```

Endocrine signal is modulation context.

It is not:

```text
purpose
candidate approval
action selection
memory write
predictor mutation
subjective emotion proof
biological hormone simulation
```

### 5. Ordering Score

Ordering score answers:

```text
Given the current approved purpose and all allowed bounded signals,
what is the preview-only order of candidates?
```

Ordering score is a derived preview value.

It may be computed from:

```text
tendency_score
bounded affordance adjustment
bounded endocrine annotation / modulation
safety and doubt gates
hard boundary checks
```

It must not become:

```text
selected_action
final_action
direct command
execution
purpose
```

---

## Purpose Boundary

Hard rule:

```text
Regulatory and tendency signals may rank candidates only inside a pre-existing approved purpose.
They must not create, replace, expand, or persist purpose.
```

No signal in this layer may answer:

```text
What should I want?
```

Signals may only help answer:

```text
Given the current approved purpose,
which candidate should be considered earlier?
```

Forbidden transformations:

```text
dopamine_like rises
-> create purpose: find more candy

movement_success_feedback
-> create purpose: keep exploring

tendency_score rises
-> change question: from "is movement safe?" to "seek reward"

affordance_confidence rises
-> create task: go farther

candidate ordering changes
-> extend budget or scope
```

---

## Exploration Exception

There is one narrow exception:

```text
If the current approved purpose is explicitly exploration,
signals may reorder candidates within that exploration scope only.
```

Allowed:

```text
purpose: sandbox_exploration
candidates: inspect_nearby, step_forward, pause_and_observe, turn_left
movement_success_feedback -> step_forward may receive bounded ordering support
```

Still forbidden:

```text
create a new exploration purpose
expand exploration radius
extend time budget
override stop_after_budget
remove pause_and_observe
turn candy reward into find_more_candy purpose
persist exploration drive
change production behavior
```

Exploration exception does not allow:

```text
autonomous goal creation
autonomous curiosity drive
open-ended wandering
reward chasing
```

---

## Score Relationship

Affordance confidence and tendency score are not the same thing.

```text
affordance_confidence = body feasibility signal
tendency_score = action consideration preference
endocrine_signal = regulatory modulation context
ordering_score = derived preview-only candidate ranking score
```

Suggested future formula, design-only:

```text
ordering_score =
  tendency_score
  + bounded_affordance_adjustment
  + bounded_endocrine_adjustment
  + bounded_doubt_or_safety_adjustment
```

This formula is illustrative only.

Any future runtime/checker package must define exact inputs, weights, clamps, and invalid cases.

---

## Affordance Adjustment

Affordance adjustment should remain small.

Suggested design-only shape:

```text
bounded_affordance_adjustment = clamp(
  (affordance_confidence - 0.50) * 0.5,
  -0.02,
  +0.02
)
```

Example:

```text
movement_affordance_confidence = 0.53
baseline = 0.50
difference = 0.03
weight = 0.5
adjustment = +0.015
```

This means:

```text
affordance confidence can nudge ordering only when candidates are already close.
```

It must not let one successful movement dominate memory, doubt, safety, or hard blocks.

---

## Endocrine Adjustment

Endocrine adjustment must be even more constrained because the mimetic endocrine design is currently design-only and forbids direct action selection.

Suggested role:

```text
endocrine_signal -> annotation / bounded modulation candidate
```

Not:

```text
endocrine_signal -> action selection
endocrine_signal -> purpose
endocrine_signal -> candidate approval
```

Examples:

```text
dopamine_like may annotate approach/support context
norepinephrine_like may annotate salience/uncertainty context
cortisol_like may annotate risk/cooldown context
oxytocin_like may annotate source trust/review context
```

If future packages permit numeric modulation, it must be bounded and preview-only.

Suggested design-only cap:

```text
abs(bounded_endocrine_adjustment) <= 0.01
```

This cap is intentionally smaller than memory-tendency and affordance confidence effects.

---

## Hard Block Precedence

Hard blocks always win over ordering scores.

Examples:

```text
wall ahead blocks step_forward
budget exhausted blocks continuation
human stop blocks action
unsafe fixture blocks direct retry
no approved purpose blocks all purpose-bound ordering
```

No score may override:

```text
hard safety block
human instruction
approval boundary
rollback requirement
scope boundary
stop_after_budget
```

---

## Candidate Ordering Preview Rules

Future candidate ordering preview may be allowed only if all are true:

```text
approved_purpose_exists == True
purpose_scope_explicit == True
all_candidates_preserved == True
hard_blocks_applied_first == True
ordering_score_is_preview_only == True
selected_action_created == False
final_action_created == False
direct_command_created == False
motor_execution_created == False
rollback_available == True
decay_required == True
same_session_only == True
```

Candidate ordering must not:

```text
remove alternatives
remove pause
remove stop
remove ask_for_help when available
create a new purpose
extend time budget
create selected_action
```

---

## Recommended Next Package

The next runtime/checker package should be:

```text
Body-Motor Feedback To Affordance Confidence Preview Minimal v0
```

Purpose:

```text
settled body-motor feedback
-> same-session affordance confidence preview
-> no candidate ordering change
```

It should not be:

```text
Body-Motor Feedback-Gated Candidate Reordering Minimal v0
```

Candidate reordering should wait until the confidence/tendency/endocrine reconciliation has at least one validated preview layer.

---

## Non-Goals

This design does not add:

```text
runtime endocrine system
runtime endocrine modulation
candidate reordering
selected_action
final_action
direct command
motor execution
pathfinding
goal creation
purpose creation
autonomous exploration
open-ended wandering
reward chasing
persistent feedback
cross-session feedback persistence
memory write
retention write
predictor read
predictor influence
predictor mutation
semantic vision
object recognition
subjective emotion claim
biological hormone simulation
autonomous learning claim
autonomous action claim
proof-of-learning claim
```

---

## Summary

The action line and mimetic endocrine line can connect only through bounded, explicit, preview-only layers.

Correct relationship:

```text
approved purpose
-> candidate set
-> tendency / affordance / endocrine annotations
-> bounded ordering_score preview
-> candidate ordering preview
```

Forbidden shortcut:

```text
reward / confidence / tendency / endocrine signal
-> purpose
```

Core rule:

```text
tendency can help order candidates under a purpose.
tendency cannot become the purpose.
```
