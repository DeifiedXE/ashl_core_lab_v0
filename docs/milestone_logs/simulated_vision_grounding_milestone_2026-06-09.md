# Simulated Vision Grounding Milestone

Date: 2026-06-09

## Scope

This milestone covers the completed symbolic simulated vision grounding phase:

- symbolic simulated vision
- first-person viewport
- observed local map
- symbol-to-outcome grounding check
- grounded action experience
- experience-based action influence

This is a bounded symbolic sandbox milestone. It does not add new runtime behavior.

## Completed Packages

### Simulated Vision Facing / Viewport v0

Adds a symbolic simulated vision sandbox with position, facing, `look`, `turn_left`, `turn_right`, and `move_forward`.
The agent receives a bounded 3x3 symbolic viewport, not the full map as vision.

### Simulated Vision Session Memory Bridge v0

Records simulated vision action traces into Session Working Memory as generic state-action-outcome records.
The bridge records observations only; memory records do not influence action selection.

### Simulated Vision Observed Local Map v0

Adds a session-local observed map built only from currently visible viewport cells.
Unknown `x` cells do not erase known cells, and unseen cells are not inferred from the source map.

### Simulated Vision Symbol Grounding Check v0

Checks bounded symbolic relations between a visible front symbol and the immediate `move_forward` outcome.
The check covers wall, empty, and item scenarios without claiming solved symbol grounding.

### Grounded Action Experience v0

Records bounded local experience entries from visible front symbol, attempted action, and immediate outcome.
Experience is stored only in runner-local output and is not used for decisions in this package.

### Grounded Action Experience Influence v0

Adds a runner-local two-trial check where prior grounded action experience can influence the next immediate action.
The no-experience wall control proves that seeing `w` alone does not suppress `move_forward`.

### Simulated Vision First-Person Viewport Correction v0

Corrects the 3x3 viewport from a centered top-down crop to a Doom-like forward view.
The agent marker is at bottom center, and the immediate front symbol moves to `viewport[1][1]`.

## Current Minimal Loop

```text
first-person see
-> interact
-> outcome
-> experience
-> see similar symbol again
-> consult experience
-> influence immediate action
```

This loop exists only inside the bounded symbolic simulated vision sandbox.

## First-Person Viewport Convention

The corrected 3x3 viewport convention is:

```text
row 0 = far/front row
row 1 = near/front row
row 2 = agent row
```

Coordinates:

```text
agent marker a = viewport[2][1]
immediate front symbol = viewport[1][1]
far front symbol = viewport[0][1]
centered top-down viewport = false
```

Sample initial north viewport:

```text
e e i
e e e
e a e
```

## Grounding Results

Verified symbol-to-outcome checks:

```text
front_symbol w + move_forward -> blocked / wall_blocked
front_symbol e + move_forward -> moved
front_symbol i + move_forward -> item_contact
```

Verified experience influence:

```text
With prior experience:
w + move_forward -> blocked experience causes later move_forward suppression for w.

Without prior experience:
seeing w alone does not suppress move_forward.
```

The no-experience control is part of the milestone boundary: the influence requires matching prior experience, not symbol sight alone.

## Strongest Allowed Claim

In the symbolic simulated vision sandbox, a bounded first-person visual symbol can be connected to immediate action outcomes, recorded as local experience, and later used in a runner-local way to influence immediate action choice.

## Explicit Non-Claims

- No real image vision.
- No computer vision.
- No LLM vision.
- No LLM planning.
- No full map vision.
- No pathfinding.
- No route planning.
- No item seeking.
- No inventory.
- No long-term memory.
- No lesson_store write.
- No Memory Layer write.
- No lesson_candidate pipeline.
- No general learning proof.
- No visual understanding claim.
- No solved symbol grounding claim.
- No consciousness or subjective understanding claim.

## Boundary Status

`docs/current_boundary_index.md` remains unchanged at:

```text
Boundary Index Version: 2026-06-08-b33
```

Boundary Index is near line limit and should not be patched blindly.
If syncing this milestone into Boundary Index later, first compress or reorganize the index.

## Next Direction

Next recommended package:

```text
Simulated Vision Grounding Boundary Index Compression / Sync v0
```

Reason:

```text
This milestone should be indexed, but current Boundary Index is near limit.
```

Do not implement the next package here.
