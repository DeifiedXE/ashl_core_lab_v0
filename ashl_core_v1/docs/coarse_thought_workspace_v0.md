# Package 143 Coarse Thought Workspace v0

Status: Completed only when the external audit reports
`passed_coarse_thought_workspace_v0`.

Package 143 adds one capacity-limited, short-lived context in which existing
Package 142 bounded specialized-thought results can coexist. It is not memory,
deliberation, a solver, persistent working state, or a complete conscious
blackboard.

## Typed Input Boundary

The sole production input scope is:

`package_143_coarse_thought_workspace_only`

The allowed source records are exact Package 142 schemas for:

- bounded specialized-thought results
- unresolved cross-family conflict evidence
- result expiry/revocation invalidation evidence

The binding records the passed Package 142 audit, source HEAD, source database
SHA-256, consumer binding, and two family contracts. Package 142 is opened
query-only and hashed before and after each complete run. Package 143 does not
read perception directly and does not consume legacy `ThoughtSignal`, Package
136 drive modulation, or Package 138 self-state readback.

## Workspace Contract

The workspace kind is:

`ephemeral_bounded_coarse_thought_context`

Its fixed v0 bounds are:

- maximum entries: 3
- maximum process-local workspace lifetime: 2 seconds
- maximum entry lifetime: 1 second
- each entry expiry is the earliest of its Package 142 source expiry, the
  workspace expiry, and the one-second entry bound
- session scope: one process and one runtime session
- fresh process initial occupancy: 0
- cross-session recovery: forbidden

Active occupancy exists only in the process-local workspace object. The
external SQLite store contains immutable lifecycle evidence, not an active
workspace snapshot or recovery head.

## Admission

A single result can enter only when it is a typed, active, revocable Package
142 result with complete family lineage and no semantic or behavior authority.
An unresolved Package 142 conflict enters as one atomic two-entry admission
group. A known conflict member cannot be admitted separately.

Admission does not assign priority, rank, truth, importance, confidence, or
action eligibility.

## Capacity And Eviction

When capacity is full, the deterministic rule is:

`oldest_admission_group_then_group_id`

Whole admission groups are evicted until the incoming group fits. Conflict
groups are never split. Eviction means only that an entry is no longer
temporarily retained. It does not mean error, negation, forgetting, low
importance, behavioral suppression, or winner selection.

## Conflict Carriage

The Package 142 status remains exactly:

`unresolved_cross_family_conflict_preserved`

Both incompatible results coexist as one atomic group. Insertion order,
capacity bookkeeping, and eviction policy do not choose a winner, rank the
results, vote, resolve truth, deliberate, or select an action.

## Expiry And Revocation

Package 142 expiry or revocation immediately invalidates every matching
workspace entry. If one member of an unresolved conflict becomes invalid, the
entire conflict group leaves together so no incomplete conflict or orphan
thought remains. Session closure invalidates any remaining entries and ends
with occupancy zero.

All admissions, evictions, cascades, conflict carriage, closures, and reset
proofs are append-only audit records. They cannot be loaded as active context.

## Fresh-Process Reset

The official run opens and closes the populated workspace in one OS process,
then starts a distinct subprocess. The new process creates a new workspace
session with zero initial and zero recovered entries. It does not inspect the
prior lifecycle store to reconstruct occupancy.

## Authority Boundary

Package 143 creates no:

- iterative reasoning or recursive rule chaining
- deep search or conflict resolution
- verification proposal
- purpose or candidate ordering
- selected action or perception action
- memory write or self-state mutation
- drive/readback consumption
- output or external control
- semantic identity
- LLM, Codex, or network runtime call

Counterfactual evidence verifies that runtime behavior, memory, purpose,
action, output, self-state, drive, and perception authority are unchanged when
the workspace lifecycle evidence exists.

## Store And CLI

Generated evidence remains outside Git:

```text
<state-dir>/
  package_143_coarse_thought_workspace_v0/
    package_143.sqlite3
```

Primary commands:

```text
py -3 -m ashl_core_v1.thought.package_143_coarse_workspace_cli preflight ...
py -3 -m ashl_core_v1.thought.package_143_coarse_workspace_cli run-workspace ...
py -3 -m ashl_core_v1.thought.package_143_coarse_workspace_cli run-controls ...
py -3 -m ashl_core_v1.thought.package_143_coarse_workspace_cli run-regressions ...
py -3 -m ashl_core_v1.thought.package_143_coarse_workspace_cli audit ...
```

Operator events use the existing local operator stream. They are engineering
translations, not Qingyin output.

## Package 144 Boundary

Package 143 does not deliberate. Package 144 must define a separate bounded
deliberation authorization and budget over an immutable workspace view. It
still needs explicit limits on steps, elapsed time, input snapshot, allowed
operations, conflict handling, cancellation, expiry propagation, trace
closure, and fail-neutral behavior. It must not reinterpret eviction as a
judgment or turn workspace presence into purpose, action, memory, or output
authority.

Package 143 does not implement Package 144 or any later Thought Engine stage.
