# Instinct Random Walk + Item Reward Bias Design v0

## 1. Purpose

This design prepares the first bounded experiment where Qingyin can move from purely manual symbolic interaction toward an experience-driven behavior loop.

The experiment concept is:

- Round 1 starts with no prior experience.
- An instinct/random walk policy produces bounded action attempts.
- A wall collision creates a wall-blocked experience.
- An item contact creates an item reward event.
- The item reward event creates a reward-biased action tendency.
- Round 2 carries Round 1 experience into a new run for comparison.

This is not pathfinding. It is not planning. It is not consciousness. It is not goal understanding. It is a bounded design for testing whether local experience records can bias later immediate action tendencies.

## 2. Core Hypothesis

If an agent first explores with no prior experience, then wall collisions and item contacts can produce local experience records.

If those records are carried into a second round, immediate action selection can be biased away from previously bad outcomes and toward previously rewarded item contact.

The claim must stay bounded: a better Round 2 trace may suggest experience-mediated influence under the tested controls, but it is not proof of general learning, map understanding, or goal understanding.

## 3. Round Structure

### Round 1: No Prior Experience

Initial conditions:

- `experience_store = empty`
- `reward_store = empty`
- agent uses instinct/random walk policy

Expected events:

- `front_symbol=w + move_forward -> blocked / wall_blocked`
- `front_symbol=i + move_forward -> item_contact`
- `item_contact -> reward_event`

Expected behavior after events within Round 1:

- repeated wall action may be suppressed after blocked experience
- item contact may create item reward bias

Round 1 does not assume that seeing `w` or `i` has meaning before contact. It records outcomes from grounded interaction.

### Round 2: Carry Experience

Initial conditions:

- `experience_store = Round 1 output`
- `reward_store = Round 1 reward records`
- same or comparable sandbox start

Expected comparison:

- fewer repeated wall collisions
- fewer steps to first `I` contact
- more `I`-oriented actions when `I` is visible or later when a staged design allows remembered `I`

Round 2 should be compared against controls before making any experience-mediated claim.

## 4. Instinct / Random Walk Policy v0

The v0 policy is bounded random-like action selection over existing larger sandbox actions:

- `look`
- `turn_left`
- `turn_right`
- `move_forward`

Base random tendencies:

- sometimes look
- sometimes turn
- sometimes move forward

The policy must not use:

- pathfinding
- full-map knowledge
- route planning
- item seeking by semantic understanding

After experience:

- blocked experience can lower `move_forward` when the same front symbol/context predicts blocked
- rewarded item experience can raise action tendency toward item contact when `I` is visible

Useful future terms:

- `base_action_weight`
- `experience_penalty`
- `reward_bias`

This design does not implement exact weights.

## 5. Wall Experience

Wall experience definition:

```text
front_symbol=w + move_forward -> blocked / wall_blocked
```

Experience effect:

```text
later same front_symbol=w + move_forward can be suppressed or down-weighted
```

Control requirement:

```text
Without prior blocked experience, seeing w alone should not automatically suppress move_forward.
```

This preserves the experience-first rule: the system must first experience the bad outcome before treating it as a local negative action record.

## 6. Item Reward Event

Item contact definition:

```text
front_symbol=i + move_forward -> item_contact
```

Reward event:

```text
reward_type: item_contact_reward
reward_value: positive
source: grounded_action_experience
signal: dopamine_like_signal
```

`dopamine_like_signal` is a non-subjective trace label. It must not be described as pleasure, desire, wanting, or felt reward.

Experience effect:

```text
later visible I or remembered I can raise contact-oriented tendency
```

Recommended staged approach:

- v0 influence uses visible `front_symbol=i` only
- v1 can consider `observed_local_map` remembered `I`

Keeping v0 to visible `front_symbol=i` avoids prematurely turning observed map memory into route planning.

## 7. Metrics

Future runner metrics should include:

- `round`
- `step_count`
- `wall_blocked_count`
- `repeated_wall_blocked_count`
- `first_item_contact_step`
- `item_contact_count`
- `reward_event_count`
- `experience_store_size`
- `reward_store_size`
- `random_seed`
- `max_steps`

Round 2 comparison metrics:

- `delta_wall_blocked_count`
- `delta_first_item_contact_step`
- `delta_item_contact_count`
- `reward_bias_observed`

Lower step count alone is not proof of learning. Use A/B or no-experience controls before claiming an experience-mediated effect.

## 8. Controls

Future controls:

- Round 2 with carried experience
- Round 2 without carried experience
- same seed if deterministic comparison is desired
- different seeds if robustness check is desired

Required control claim:

```text
If Round 2 improves only with carried experience, the effect is likely experience-mediated.
```

## 9. UI Observation

The Qingyin Observation panel may eventually show:

- current mode: `instinct_random_walk_observation`
- current action tendency summary
- last reward event
- wall blocked count
- item contact count
- current cooldown

This design package does not implement UI changes. The UI must remain manual observation until a later package explicitly adds a bounded runner.

## 10. Staged Implementation Plan

### v0: Design Only

Define experiment, stores, metrics, controls, and non-claims.

### v1: Instinct Random Walk Runner

Add a random/manual-seeded action loop in CLI only. No reward bias yet.

### v2: Wall Experience Influence

Blocked experience suppresses repeated bad `move_forward` attempts in the same local context.

### v3: Item Reward Event

`item_contact` creates `dopamine_like_signal` / `reward_event`.

### v4: Reward-Biased Action Tendency

Visible `I` raises contact-oriented action tendency.

### v5: Two-Round Comparison

Compare Round 1 vs Round 2 with carried experience.

### v6: A/B Control

Compare with-experience vs without-experience Round 2.

## 11. Non-Claims

This design does not claim or add:

- consciousness
- self-awareness
- subjective desire
- pleasure
- subjective reward
- general learning proof
- pathfinding
- route planning
- full-map knowledge
- LLM planning
- LLM vision
- item seeking by semantic understanding
- long-term memory
- lesson_store write
- Memory Layer write
- home sandbox
- visual understanding
- solved symbol grounding

## 12. Next Recommended Package

Next recommended package:

```text
Instinct Random Walk Runner v0
```

Only after this design is reviewed.

## Boundary

This document is design-only.

It does not add runtime behavior, autonomous action loops, new CLI commands, random walk runners, reward runtime, dopamine runtime, action weighting, item collection, item pickup, inventory, exit activation, win condition, task completion, curiosity, prediction error, place memory, home sandbox, real image vision, LLM vision, LLM planning, pathfinding, BFS, A*, route planning, lesson_store writes, Memory Layer writes, long-term memory, or lesson_candidate pipeline connections.
