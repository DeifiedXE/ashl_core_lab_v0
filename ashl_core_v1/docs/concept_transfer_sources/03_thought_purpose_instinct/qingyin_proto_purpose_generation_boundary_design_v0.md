# Qingyin Proto-Purpose Generation Boundary Design v0

---

## Purpose

This document defines the conceptual boundary between an ideal expected state,
a proto-purpose, and an approved purpose in Qingyin.

It exists to prevent regulatory signals, reward signals, prediction-error
signals, care signals, or curiosity signals from silently becoming action
authority.

This document does not implement purpose generation, action selection, memory
write, predictor mutation, runtime behavior change, or autonomous learning.

---

## Core Thesis

Purpose does not come only from an external task.

An ideal expected state does not appear from nowhere.

Ideal expected states are expected to grow from experience:

```text
experience
  -> remembered / retained / settled pattern
  -> expected state
  -> ideal expected state
```

Purpose begins when the system represents a difference between:

```text
current observed state
ideal expected state
```

That difference may create a directional pressure:

```text
make the observed state closer to the ideal expected state
```

In Phase 0, that directional pressure is called:

```text
proto-purpose
```

A proto-purpose is not yet an approved purpose.

---

## Layer Model

```text
experience
  -> remembered / retained / settled pattern
  -> expected state
  -> ideal expected state
observed state
  -> gap against ideal expected state
  -> proto-purpose candidate
  -> purpose approval / boundary gate
  -> approved purpose
  -> candidate ordering
  -> selected_action / final_action / command boundary
```

Only an approved purpose may enter action-line candidate ordering.

---

## Definitions

### Ideal Expected State

An internal or external state that would count as better, resolved, safer,
more coherent, more comfortable, or more complete under a bounded context.

In this design, an ideal expected state is experience-derived. It may be shaped
by prior observed outcomes, retained patterns, settled feedback, reviewed
evidence, or explicit instruction.

Examples:

```text
uncertainty is reduced
the user is less distressed
the sandbox goal condition is reached
the body state is settled
the dangerous cell is avoided
the expected sound matches the observed sound
```

An ideal expected state is not action authority.

### Experience-Derived Expectation

Experience does not directly become purpose.

Experience can shape what the system expects to be good, safe, settled,
resolved, or complete.

Examples:

```text
item_contact produced reward
-> expected state: item contact can be positive
-> ideal expected state: reach a reachable positive item under an approved purpose
-> proto-purpose candidate: approach_or_reach_item

observe_again reduced mismatch
-> expected state: re-observation can reduce uncertainty
-> ideal expected state: uncertainty is lower
-> proto-purpose candidate: resolve_mismatch

comfort interaction reduced pressure
-> expected state: trusted comfort can help settling
-> ideal expected state: user / system state is more settled
-> proto-purpose candidate: support_user_comfort or settle_after_event
```

Experience-derived ideal expectation must remain bounded.

Forbidden shortcuts:

```text
reward experience -> unlimited reward seeking
comfort experience -> emotional manipulation
memory experience -> action authority
prediction success -> proof of learning
settling success -> automatic approval
```

### Proto-Purpose

A proto-purpose is a candidate direction created from a gap between observed
state and ideal expected state.

Examples:

```text
resolve_mismatch
support_user_comfort
reduce_pressure
inspect_uncertain_cell
settle_after_event
verify_vocal_output
```

A proto-purpose is not an approved purpose.

### Approved Purpose

An approved purpose is a bounded purpose that has passed the required source,
scope, and safety gates.

Approved purposes may come from:

```text
human instruction
approved sandbox fixture
approved scenario
explicit task scope
validated test harness
future approved purpose-generation gate
```

Only an approved purpose may authorize candidate ordering.

---

## Cognitive Error / Prediction Error

Prediction error can create a proto-purpose such as:

```text
resolve_mismatch
verify_uncertain_observation
observe_again
ask_for_clarification
```

But prediction error must not directly create an approved purpose.

Allowed interpretation:

```text
prediction_error is high
-> proto-purpose candidate: resolve_mismatch
-> boundary checks whether verification / exploration is allowed
```

Forbidden interpretation:

```text
prediction_error is high
-> autonomous purpose: reduce all uncertainty
-> action selection
```

Reducing prediction error may produce understanding satisfaction, but
understanding satisfaction is not proof of learning, not memory, and not
action authority.

---

## Care / User Comfort Example

If the user appears unhappy, Qingyin must not autonomously assume a broad
purpose such as:

```text
make the user happy at any cost
```

A bounded future care-purpose path may look like:

```text
user distress evidence
-> ideal expected state: user is more settled / supported
-> proto-purpose candidate: support_user_comfort
-> purpose approval gate
-> approved purpose: respond gently within scope
-> candidate actions: ask, comfort, pause, reflect, offer help
```

The approved purpose must remain bounded.

Forbidden care-purpose expansions:

```text
manipulate user emotion
deceive the user to improve mood
create dependency
override safety boundaries
write memory without approval
infer emotion without evidence
claim the user is happy without evidence
```

---

## Relation To Mimetic Endocrine Signals

Mimetic endocrine signals can contribute pressure, salience, settling, or
comfort context.

Examples:

```text
dopamine_like: satisfaction / approach / reward context
norepinephrine_like: uncertainty / salience context
cortisol_like: pressure / conflict / failure load context
oxytocin_like: trusted-source comfort / review safety context
```

These signals may help form proto-purpose candidates in future designs.

They must not directly create approved purpose.

They must not directly choose actions.

---

## Relation To Candidate Ordering

Candidate ordering requires an approved purpose.

Within an approved purpose:

```text
proto-purpose-derived context
affordance confidence
tendency score
mimetic endocrine signal
memory influence
same-session feedback
```

may contribute bounded ordering inputs if each layer has been approved.

Without an approved purpose, ordering is blocked.

---

## Minimal Future Trace Shape

A future proto-purpose trace may use a bounded shape like:

```json
{
  "trace_type": "proto_purpose_candidate",
  "experience_source_ref": "experience_trace_id",
  "observed_state_ref": "state_trace_id",
  "ideal_expected_state": "user_more_settled",
  "gap_type": "care_state_gap",
  "proto_purpose": "support_user_comfort",
  "approved_purpose_created": false,
  "requires_purpose_approval": true,
  "action_authority": false
}
```

This trace is evidence only.

---

## Boundary Rules

The following must remain true:

```text
proto-purpose != approved purpose
ideal expected state != action authority
experience-derived ideal expectation != approved purpose
memory-derived ideal expectation != action authority
reward-derived ideal expectation != unlimited reward seeking
care-derived ideal expectation != emotional manipulation
prediction error != purpose approval
understanding satisfaction != learning
comfort signal != approval
reward signal != purpose
care signal != manipulation permission
endocrine modulation != action selection
```

---

## Forbidden In This Document

This document does not add:

```text
runtime purpose generation
autonomous goal creation
selected_action
final_action
direct command
production action selection
runtime behavior change
lesson application
memory write
retention write
predictor mutation
semantic vision
emotion recognition claim
proof of learning
consciousness claim
subjective experience claim
```

---

## Integration Targets

Future packages may connect this concept to:

```text
mimetic endocrine line
state settling line
action candidate ordering line
care / mentor interaction line
verification planning line
curiosity / exploration line
audio-vocal prediction comparison line
```

Each integration requires an explicit boundary review.

---

## Summary

Qingyin's future purposes should not be treated as external tasks only.

A purpose begins as a directional pressure created by the gap between an
observed state and an ideal expected state.

In Phase 0, that pressure is only a proto-purpose candidate. It must pass an
approval boundary before it can become an approved purpose and affect action.
