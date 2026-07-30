# Internal Perception Focus Shift Minimal v0

Status: Completed by Package 127

## Capability

Package 127 adds one bounded internal visual-focus action:
`shift_internal_perception_focus`.

The action consumes actual Package 121
`VisualChangePrimitiveRecord.changed_grid_cells` from a clean completed
screen observation. Cells at or above the configured low-level difference
floor become candidates. At most 16 candidates are retained, ordered by
`difference_strength`, then `grid_y`, then `grid_x`. Omitted cells are counted
without being described as unimportant.

The selected cell has no semantic label, object identity, object class,
novelty, uncertainty, memory, endocrine, Thought Engine, or learned-ranking
input.

## Capture Boundary

The focus action uses the Package 126 `capture_again` path. The child has new
screen and host-state capture-session identities and an explicit cross-window
gap. Its raw screen target, raw screen region, capture configuration, compiler
version, and sampling-plan identity remain equal to the parent.

The complete child frame is captured and compiled. Focus adds a read-only
index over one existing primitive grid cell; it does not recapture a crop,
change a sensor target, or persist raw pixels. Package 122 attaches the sidecar
only when its full-frame `PerceptionReadableData` lineage matches the child
perception session.

Focus applies to exactly one child observation window and then releases
automatically. An interruption and its release remain append-only history.

## Real Evidence

The official experiment is
`host_internal_visual_grid_focus_shift_v0`.

It uses a fixed local full-window screen target with screen and host-state
lanes. Two spatially separated nonsemantic regions change in the parent. The
runtime selects the actual highest changed-grid `difference_strength`, freezes
that result, and then opens the Package 126 child. The external fixture is
coordinated only after selection; its schedule never enters candidate creation
or policy provenance.

The passing run proved:

- at least two actual changed-grid candidates;
- deterministic highest-strength selection;
- distinct parent and child capture sessions;
- unchanged raw target, region, configuration, and full-frame capture;
- selected-cell low-level evidence in the child;
- one read-only focus sidecar and automatic release;
- zero required-lane drops, backpressure faults, capture failures, compile
  failures, and flush remainder.

## Boundaries

Package 127 changes no Package 112 score and creates no memory record, working
readback, output, selected action, final action, direct command, or external
control. It adds no audio focus, camera focus, sensor-priority runtime,
evidence-sufficiency policy, novelty, uncertainty, semantic vision, object
recognition, Package 128, Package 129, D-Laplace runtime component, or DLM-1.

Package 128, Evidence Sufficiency And Observation Stop Policy, is next.
Packages 128 through 132 remain the locked perception route. Package 132
closes the perception capability construction line; Package 133 begins
persistent self-state. No Package 132A is scheduled.
