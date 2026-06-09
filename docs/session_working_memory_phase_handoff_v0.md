# Session Working Memory Phase Handoff v0

## 1. Purpose

This handoff closes the current Session Working Memory phase and prepares the project for simulated vision grounding.

The purpose is to summarize what the current memory foundation can do, what it cannot do, and what the next phase needs before starting Simulated Vision Facing / Viewport v0.

This document is cleanup and handoff only. It adds no runtime behavior.

## 2. Completed Capabilities

### Session Working Memory v0

Provides a session-local store for generic state-action-outcome records.
Records are short-term only and are cleared at session end.
It is not long-term memory and does not write lesson_store or Memory Layer data.

### State Snapshot Key v0

Derives deterministic `state_key` values from `state_snapshot`.
The key gives a stable index for querying current-session records by state, or by state plus action.
Missing optional fields use stable `null` values.

### Session Working Memory Trial Integration v0

Connects the existing approach-box dead-end trial output to Session Working Memory records.
The trial reports query summaries, records non-null state keys, and clears session memory at session end.
It does not modify action selection or prove learning.

### Local Memory Decision Trace Observer v0

Observes local decision traces around dead-end behavior.
It makes local memory effects visible as trace evidence.
It does not change the runner, select actions, or write persistent memory.

### Valid Dead-End Maps A/B Control v0

Adds valid dead-end map A/B control coverage across three valid maps.
It supports the current strongest bounded claim that a local memory effect was observed across 3 valid dead-end maps.
It is not proof of general learning, map understanding, or solver ability.

## 3. Current Data Shape

Current generic Session Working Memory records use this shape:

```text
tick
state_key
state_snapshot
action
target
outcome_type
outcome_detail
failure_reasons
effect_tags
metadata
```

Field notes:

```text
state_key = deterministic key generated from state_snapshot
failure_reasons = list
metadata can hold blocked_at / target_pos / raw_result / source
```

The record shape is generic. It is not wall-specific, dead-end-specific, or visual-specific.

## 4. Supported outcome_type Values

Supported generic outcome categories:

```text
moved
blocked
no_progress
entered_trap
goal_progress
goal_reached
unknown
```

These are generic outcome categories. They are not wall-specific memories and not dead-end-specific memories.

## 5. Confirmed Boundaries

```text
No long-term memory write.
No lesson_store write.
No Memory Layer write.
No lesson_candidate pipeline.
No action selection modification from Session Working Memory yet.
No pathfinding.
No LLM planning.
No proof of general learning.
```

## 6. What Is Proven / What Is Not

Current supported claims:

```text
Bounded local memory effect was observed across 3 valid dead-end maps.
Session-local memory can record and query generic state-action-outcome records.
state_key indexing works.
```

Claims not supported:

```text
general learning
map understanding
maze solving
pathfinding
long-term memory
visual grounding
cross-map transfer of learned rules
consciousness / subjective understanding
```

## 7. Why Maze Line Should Pause

Continuing maze-style tests now risks turning the project into a pathfinding evaluation.

The current decision is:

```text
Do not continue maze / solver direction for now.
Move toward simulated vision grounding after memory phase cleanup.
```

## 8. Next Phase Direction

Next phase:

```text
Simulated Vision Facing / Viewport v0
```

Initial symbolic simulated vision plan:

```text
w = wall
e = empty
i = item / object
x = out of view / unknown
```

Planned minimal body/view state:

```text
pos = (x, y)
facing = north / east / south / west
```

Planned minimal actions:

```text
turn_left
turn_right
look
move_forward
```

Important next-phase boundary:

```text
This next phase should not use real images yet.
It should use structured symbolic simulated vision.
It should not use pathfinding.
It should not use LLM vision.
```

## 9. Next Package Recommendation

Recommended next package:

```text
Simulated Vision Facing / Viewport v0
```

Do not implement it in this package.
