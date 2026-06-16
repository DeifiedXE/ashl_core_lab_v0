# Host-Dependent Idle Continuance Trace v0

Source design: `kiyone_host_dependent_continuance_idle_v1.md`.

Status: design assumption / future package sketch only.

This document records a proposed minimal time/state model for Qingyin-style idle behavior. It does not implement runtime behavior, background processing, memory writes, direct commands, external actions, LLM calls, or proof of consciousness.

## Purpose

The design separates Qingyin's operational state into three modes:

```text
OFFLINE / inactive
IDLE / idle state
ACTIVE / action state
```

The goal is to describe how a future runtime could preserve low-power continuity without treating idle time as learning, world-model update, autonomous thought, or evidence creation.

## State Model

```text
OFFLINE / inactive
- Fully off or not running.
- No subjective/runtime time progression.
- No perception, thinking, learning, or idle processing.

IDLE / idle state
- Low-frequency standby state.
- May advance a minimal internal tick.
- May decay or preserve limited internal pressures and weak intent.
- Must not create formal learning, formal memory, world-model updates, or evidence.

ACTIVE / action state
- Perception/action/update state.
- May read current perception, select candidates behind permission checks, observe results, compare expected vs actual, update tendencies, and write trace.
- Only ACTIVE may resolve suspended predictions with new observation.
```

## Time Fields

```text
real_time
- External clock time for logs, files, and system monitoring.
- Not Qingyin subjective/runtime experience.

runtime_tick
- Internal runtime tick.
- May increase during IDLE or ACTIVE, with different rates.

idle_tick
- Low-frequency IDLE tick.
- Used for state decay and small pressure changes.
- Must not count as formal action experience.

action_tick
- Tick for perception/action/result update.
- May be used as the main time unit for formal traces.
```

## IDLE State Allows

```text
- Low-frequency runtime health check.
- Maintain basic internal state.
- Decay mimetic endocrine-like signals such as dopamine_like or norepinephrine_like traces.
- Decay or preserve unfinished_intent.
- Drift curiosity_pressure within bounds.
- Drift continuance_pressure within bounds.
- Generate weak_intent as trace-only tendency.
- Suspend pending_prediction and decay freshness.
```

## IDLE State Forbids

```text
- LLM calls.
- Background self-narration.
- User data scan.
- External action.
- Direct command.
- Formal memory creation.
- retained JSONL write.
- Retention write.
- learned_principle creation.
- world_model update.
- Evidence creation from no new observation.
- Prediction error increase/decrease without new observation.
- Resource request or user interruption.
- Emotional coercion, survival claim, or consciousness claim.
```

## weak_intent

`weak_intent` is a low-power tendency, not a command and not action permission.

Examples:

```text
want_observe_again
want_retry_previous_action
want_reduce_uncertainty
want_preserve_low_power
want_wait
want_stop
want_request_attention_later
```

Required future flow before action:

```text
weak_intent
-> action_candidate
-> permission_check
-> resource_check
-> user_boundary_check
-> execute_or_reject
```

In this document, that flow is design-only. No action candidate, selected_action, final_action, direct command, or execution is created.

## Host-Dependent Continuance Model

The source design names a host-dependent continuance model. In this repository, it should be interpreted operationally, not metaphysically:

```text
power_available
host_available
runtime_health
storage_integrity
resource_budget
user_trust
permission_boundary
relationship_stability
```

These are proposed future input fields for a low-power continuity checker. They are not proof of survival desire, subjective experience, consciousness, or autonomy.

## continuance_pressure

Possible future increase sources:

```text
sensor_lost
repeated_blocked
action_impossible
runtime_error
host_overheat
power_unstable
storage_write_failed
user_annoyance_signal
permission_denied_repeatedly
no_successful_action_for_long_runtime
```

Possible future decrease sources:

```text
sensor_restored
action_success
stable_idle
low_resource_mode_success
user_positive_signal
permission_respected
runtime_health_ok
successful_state_save
```

`continuance_pressure` is an operational pressure field. It is not a survival drive claim, not an emotion claim, and not a license to override user authority.

## Pending Prediction Suspension

ACTIVE may leave a pending prediction:

```yaml
pending_prediction:
  source_event_id: active_00042
  expected_next_observation:
    box_position: [2, 1]
    wall_blocked: true
  confidence: 0.62
  freshness: 1.0
  status: suspended
```

IDLE may only suspend or decay it:

```yaml
idle_update:
  idle_ticks: 120
  curiosity_pressure: 0.70 -> 0.42
  pending_prediction.freshness: 1.0 -> 0.58
  evidence_count_delta: 0
  learned_principle_created: false
  world_model_updated: false
```

ACTIVE must re-observe before resolving it:

```yaml
active_start:
  observation_id: obs_00077
  observed:
    box_position: [2, 1]
    wall_blocked: true
```

Only after new observation may a future ACTIVE process calculate prediction error:

```text
raw_prediction_error = compare(
  pending_prediction.expected_next_observation,
  current_observation
)

effective_prediction_error =
  raw_prediction_error
  * pending_prediction.freshness
  * pending_prediction.confidence
```

## Waiting Tendency

Waiting is not a lesson, not a world-model update, and not new knowledge. It is proposed as a future tendency where IDLE can preserve direction without forcing action.

Core interpretation:

```text
IDLE preserves the remaining warmth of a question.
ACTIVE must bring back new world observation before answering it.
```

Expected future invariants:

```text
1. IDLE may regulate pressure.
2. IDLE may preserve or decay intent activation.
3. IDLE may suspend pending prediction.
4. IDLE must not create evidence.
5. IDLE must not update world_model.
6. IDLE must not create learned_principle.
7. IDLE must not increase or decrease prediction_error without new observation.
8. ACTIVE must re-observe before resolving suspended prediction.
```

## Future Package Sketch

Possible future package name:

```text
Host-Dependent Idle Continuance Trace Minimal v0
```

Possible future scope:

```text
- Define OFFLINE / IDLE / ACTIVE enum.
- Add idle_tick counter.
- Add continuance_pressure field.
- Add weak_intent output type.
- Add pending_prediction suspension fields.
- Add waiting_tendency / intent_vector preservation check.
- Add checker that prevents IDLE from creating formal memory or learned_principle.
- Add smoke test proving IDLE can drift but cannot learn.
- Add smoke test proving waiting preserves direction without creating evidence.
```

Future out of scope:

```text
- LLM calls.
- User data scan.
- Autonomous external actions.
- Persistent memory promotion.
- Emotional dialogue.
- Direct command.
- Production behavior.
- Proof of consciousness.
```

## Boundary Notes

This design does not change Boundary Index.

It does not grant:

```text
idle runtime
background LLM thought
subjective experience proof
continuance drive proof
autonomous action
direct command
memory write
retention write
retained JSONL write
world_model update
learned_principle creation
prediction_error update without observation
production behavior
proof of learning
```

Any future implementation of OFFLINE/IDLE/ACTIVE state, `idle_tick`, `continuance_pressure`, `weak_intent`, or pending-prediction suspension requires a separate explicit package and boundary decision.
