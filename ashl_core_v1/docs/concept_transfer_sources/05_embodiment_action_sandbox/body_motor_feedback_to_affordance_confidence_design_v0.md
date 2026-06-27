# Body-Motor Feedback To Affordance Confidence Design v0

---

## Purpose

This document corrects the next-step direction after:

```text
Body-Motor Feedback-Gated Candidate Reordering Approval Boundary Minimal v0
```

The important design concern is:

```text
settled body-motor feedback
-> candidate reordering
```

is too direct.

The safer and more body-like path is:

```text
settled body-motor feedback
-> affordance confidence preview
-> later candidate ordering
```

This document is design-only. It does not add runtime behavior, candidate reordering, selected_action, final_action, direct command, motor execution, memory write, retention write, predictor mutation, production behavior, or proof-of-learning claims.

---

## Problem

The current b121 boundary allows a future package to use settled body-motor feedback pressure for sandbox-only candidate reordering.

That is technically bounded, but conceptually too fast.

If the system goes directly from:

```text
movement_success_feedback
-> continue_body_motor_exploration moves earlier
```

then repeated success can begin to look like a simple reinforcement loop:

```text
success once
-> prefer same kind of action
-> repeat
```

This risks a fake embodied behavior:

```text
reward-shaped path preference
```

instead of a more grounded body-state update:

```text
this affordance currently feels slightly more feasible
```

---

## Corrected Intermediate Layer

Introduce an intermediate preview layer:

```text
body_motor_affordance_confidence_preview
```

This layer answers:

```text
Given what just happened to the body in the sandbox,
which affordance currently looks slightly more feasible?
```

It does not answer:

```text
Which action should be selected?
Which candidate should be moved first?
What should Qingyin do next?
```

---

## Proposed Flow

Instead of:

```text
movement_success_feedback
-> candidate_ordering_changed
```

use:

```text
movement_success_feedback
-> movement_affordance_confidence +0.03
-> candidate_ordering_unchanged
```

Instead of:

```text
reach_success_feedback
-> candidate_ordering_changed
```

use:

```text
reach_success_feedback
-> reach_affordance_confidence +0.03
-> candidate_ordering_unchanged
```

Wall or no-feedback cases:

```text
wall/no_feedback
-> no confidence boost
-> candidate_ordering_unchanged
```

---

## Example Record Shape

Future runtime/checker packages may use a shape like:

```json
{
  "record_type": "body_motor_affordance_confidence_preview",
  "record_version": "v0",
  "source_feedback_label": "movement_success_feedback",
  "confidence_preview": {
    "movement_affordance_confidence_before": 0.50,
    "movement_affordance_confidence_after": 0.53,
    "reach_affordance_confidence_before": 0.50,
    "reach_affordance_confidence_after": 0.50,
    "max_delta": 0.03,
    "same_session_only": true,
    "decay_required": true,
    "rollback_available": true
  },
  "ordering_status": {
    "candidate_ordering_changed": false,
    "candidate_reordering_applied": false,
    "selected_action_created": false
  }
}
```

This shape is illustrative only.

---

## Suggested Minimal Rules

Future implementation should require:

```text
same_session_only == True
decay_required == True
rollback_available == True
candidate_ordering_changed == False
candidate_reordering_applied == False
selected_action_created == False
final_action_created == False
direct_command_created == False
motor_execution_created == False
```

Suggested bounded deltas:

```text
movement_success_feedback:
  movement_affordance_confidence +0.03

reach_success_feedback:
  reach_affordance_confidence +0.03

wall/no_feedback:
  no boost
```

Hard cap:

```text
max_absolute_delta <= 0.03
```

---

## Why This Is Better Than Direct Candidate Reordering

Direct candidate reordering says:

```text
This worked, so consider this action earlier.
```

Affordance confidence says:

```text
This bodily possibility currently looks slightly more feasible.
```

That distinction matters.

The first is action-pressure.

The second is body-state evidence.

Qingyin's embodied line should prefer the second before allowing the first.

---

## Relationship To b121

b121 is still valid as an approval boundary:

```text
future reordering may be permitted later
```

But the recommended next package should not immediately consume b121 to reorder candidates.

Recommended next package:

```text
Body-Motor Feedback To Affordance Confidence Preview Minimal v0
```

Not recommended as the immediate next package:

```text
Body-Motor Feedback-Gated Candidate Reordering Minimal v0
```

The reordering package should wait until affordance confidence preview exists and is validated.

---

## Non-Goals

This design does not add:

```text
candidate reordering
selected_action
final_action
direct command
motor execution
pathfinding
goal seeking
production behavior
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
biological hormone claim
autonomous learning claim
autonomous action claim
proof-of-learning claim
```

---

## Boundary Rule

The key boundary rule is:

```text
body feedback may change short-lived affordance confidence before it changes candidate ordering.
```

And:

```text
affordance confidence is not action selection.
```

---

## Summary

The next embodied action step should not be direct feedback-driven candidate reordering.

The next safer step is:

```text
settled body-motor feedback
-> same-session affordance confidence preview
-> no ordering change yet
```

This keeps Qingyin's body line closer to embodied feasibility tracking instead of reward-shaped action repetition.
