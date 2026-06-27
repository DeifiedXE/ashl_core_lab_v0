# Simulated Vision Larger Sandbox Design v0

## Purpose

This larger symbolic simulated vision sandbox is meant to move beyond the current 7x7 test room without turning the project into maze solving, route planning, or a home sandbox.

The sandbox is intended to test:

- first-person vision
- object interaction
- observed local map
- experience-based action influence
- future curiosity hooks
- future prediction error hooks

The sandbox is not intended to test:

- pathfinding
- route planning
- full map solving
- home behavior
- room semantic understanding

The current v0 boundary remains: "similar symbol" means exact same `front_symbol` only. No fuzzy similarity and no semantic class matching are introduced here.

## Map Definition

Future larger sandbox draft:

```text
# # # # # # # # # # # #
# . . . . # . . I . . #
# . A . . D . . . . . #
# . . . . # . I . . . #
# # # D # # # # . # # #
# . . . . . . . . . . #
# . I . . # . . . . . #
# . . . . # . . I . . E
# # # # # # # # # # # #
```

Coordinate convention for a future runtime should be stable and explicit:

```text
0-indexed x,y coordinates
x increases right
y increases downward
```

Runtime implementation must choose and preserve this convention when the map becomes executable.

## Symbols

Map symbols:

```text
# = wall
. = empty
A = agent start
I = interactable item / object
D = doorway / passage marker
E = exit, future conditional symbol
```

Viewport symbols should remain lower-case where possible:

```text
w = wall
e = empty
i = item / object
d = doorway / passage marker
x = out of view / unknown
a = agent
```

Exit viewport symbol is unresolved for v0 design. Do not overload `e` for exit because `e` already means empty. A later package should choose a distinct symbol such as `o`, `g`, or another non-conflicting marker.

## D / Doorway Design

`D` is a predefined passable passage marker at system level.

System-level rule:

```text
D is walkable.
D does not require opening.
D does not require a key.
D does not block movement.
D is visually distinct from empty.
```

Agent-observable experience:

```text
front_symbol=d
move_forward -> moved
effect_tags may include passage_crossed
before viewport context and after viewport context may differ
```

Design principle:

```text
D's physical rule is predefined.
D's spatial meaning should emerge from experience later.
```

v0 defines `D` as a passable symbol, not a taught semantic room boundary.

Future staged interpretation:

```text
v1: record crossing before/after viewport context
v2: create place_transition_candidate
v3: infer possible area boundary from repeated crossing experience
```

These future steps remain design notes only.

## I / Item Design

`I` is an interactable object placeholder.

Important future issue:

```text
Same symbol I may have different outcomes at different positions.
```

This motivates future context keys:

```text
front_symbol + action -> outcome
front_symbol + object_position + action -> outcome
front_symbol + object_id + action -> outcome
front_symbol + local_context + action -> outcome
```

Do not implement `object_id` yet.
Do not implement inventory yet.
Do not implement collection yet.

## E / Exit Design

`E` is a future conditional exit.

Current design:

```text
E is not active at v0.
E should appear only after three I objects are completed/collected in a future phase.
```

Future staged rule:

```text
v2 or later:
if completed_items >= 3:
    exit_visible = true
```

Do not implement exit spawn yet.
Do not implement task completion yet.

## Staged Roadmap

```text
v0: Larger Sandbox Design only
    define map, symbols, boundaries, D/I/E meaning

v1: Larger Sandbox Static Runtime
    load larger map and render first-person viewport
    no item collection
    no exit activation

v2: Multi-Item Contact
    I can be contacted and recorded
    no pickup/inventory
    same-symbol/different-position issue observed

v3: Item Completion State
    I can become completed/collected marker
    completed_count tracked
    no complex inventory

v4: Conditional Exit Appearance
    E appears after three I completed
    no route planning

v5: Curiosity Hook
    unknown I can produce curiosity_candidate
    no prediction error yet

v6: Prediction Error Hook
    expected outcome vs actual outcome mismatch can be recorded
```

## Current Non-Claims

- No pathfinding.
- No route planning.
- No home sandbox.
- No place memory.
- No semantic room understanding.
- No item seeking.
- No inventory.
- No curiosity implementation yet.
- No prediction error implementation yet.
- No long-term memory.
- No visual understanding claim.
- No solved symbol grounding claim.
- No general learning claim.
- No consciousness or subjective understanding claim.

## Next Recommended Package

Next recommended package:

```text
Simulated Vision Larger Sandbox Static Runtime v0
```

Only after this design is reviewed.
