# Instinct / Wall / Item Reward Immediate-Tendency Milestone

Date: 2026-06-09

## Purpose

This milestone records completion of a bounded immediate-tendency line:

```text
random/instinct action sample
-> wall experience influence
-> item reward event
-> reward-biased visible-I action tendency
-> two-round controlled comparison
```

This is a documentation milestone only. It does not add new runtime behavior, CLI, UI, or Boundary Index changes.

## Completed Packages

### Instinct Random Walk Runner v0

Adds a bounded seeded random/instinct action sample in the larger symbolic sandbox.
It records local experience outcomes such as wall-blocked and item-contact observations without carrying prior experience or reward bias.

### Wall Experience Influence v0

Verifies that a prior matching `front_symbol=w|action=move_forward` wall-blocked experience can suppress a later known bad immediate `move_forward` action.
The no-experience control proves that seeing `w` alone does not trigger suppression.

### Item Reward Event v0

Creates a non-subjective `reward_event` when `front_symbol=i + move_forward` produces `item_contact`.
The `dopamine_like_signal` field is data only and does not imply subjective pleasure.

### Reward-Biased Action Tendency v0

Verifies that a prior non-subjective `item_contact_reward` can increase immediate `move_forward` score when `front_symbol=i` is visible again.
The no-reward control proves that seeing `i` alone does not apply reward bias.

### Reward-Biased Random Walk Check v0

Compares no-reward vs with-item-reward action sampling under a controlled visible-`i` condition.
It verifies score increase and non-lower `move_forward` selection when a prior `item_contact_reward` exists.

### Two-Round Instinct Reward Comparison v0

Closes this line with a controlled two-round comparison.
Round 1 has no carried wall experience and no carried item reward.
Round 2 carries wall experience and item reward experience for immediate tendency checks.

### Earlier UI Support, Now Paused

Completed UI-support packages:

- Larger Sandbox Flask Visual UI Prototype v0
- Adjustable Action Cooldown v0
- Qingyin UI Observation Bridge v0
- Larger Sandbox Live Step Playback UI v0

UI line is paused after this point.

## Current Minimal Immediate-Tendency Chain

Round 1:

```text
no carried wall experience
no carried item reward
baseline immediate tendencies
```

Round 2:

```text
carried wall_blocked experience suppresses a known bad move_forward under front_symbol=w
carried item_contact_reward raises immediate move_forward/contact tendency under front_symbol=i
```

## Key Results

Latest reported two-round comparison:

Round 1:

```text
wall selected_action = move_forward
wall experience_used_for_decision = false
item reward_bias_applied = false
item move_forward_score = 1.0
item move_forward_selected_count = 7
```

Round 2:

```text
wall carried_wall_experience = true
wall selected_action = turn_right
wall experience_used_for_decision = true
item carried_item_reward = true
item reward_bias_applied = true
item move_forward_score = 1.5
item move_forward_selected_count = 8
```

Comparison:

```text
wall_round2_improved = true
item_round2_bias_improved = true
move_forward_score_delta_for_i = 0.5
move_forward_selected_count_delta_for_i = 1
whole_map_item_seeking_claimed = false
whole_map_random_walk_improvement_claimed = false
```

## Strongest Allowed Claim

In controlled immediate-tendency scenarios, carried wall-blocked experience can suppress a known bad immediate action, and carried non-subjective item reward can increase visible-I contact tendency.

## Explicit Non-Claims

- No route-level item seeking.
- No observed_map navigation toward I.
- No pathfinding / BFS / A*.
- No route planner.
- No autonomous exploration.
- No decision loop.
- No item collection.
- No item pickup.
- No inventory.
- No exit activation.
- No curiosity implementation.
- No prediction error implementation.
- No place memory.
- No home sandbox.
- No real image vision.
- No LLM vision.
- No LLM planning.
- No long-term memory.
- No lesson_store write.
- No Memory Layer write.
- No lesson_candidate pipeline.
- No pleasure claim.
- No desire claim.
- No self-awareness claim.
- No consciousness claim.
- No subjective experience claim.
- No visual understanding claim.
- No solved symbol grounding claim.
- No general learning claim.

## UI Line Status

UI line is paused and pushed later.

Reason:

```text
Do not keep expanding UI now.
UI should wait until the eye-structure simulation system, generalized memory loop, and mimetic endocrine system are more developed.
```

No more UI expansion packages should be prioritized for now.

## Next Major Line

Next major line:

```text
Experience Abstraction Layer
```

Intended chain:

```text
experience
-> failure_reason classification
-> similar_context matching
-> predicted_outcome
-> rule challenge / revision
```

Recommended package sequence:

```text
1. Failure Reason Classifier v0
2. Similar Context Key v0
3. Action Outcome Predictor v0
4. Rule Challenge / Revision v0
```

## Boundary Index Status

Boundary Index remains unchanged at:

```text
Boundary Index Version: 2026-06-09-b34
```

This milestone should be synced later, but not in this package.

## Next Recommended Package

Next recommended package:

```text
Failure Reason Classifier v0
```

Reason:

```text
The next main line is Experience Abstraction Layer, and UI is paused.
```

Do not implement the next package here.
