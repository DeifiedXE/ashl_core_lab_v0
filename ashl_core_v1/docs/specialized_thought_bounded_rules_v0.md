# Package 142 Specialized Thought Bounded Rules v0

Status: Completed only when the external Package 142 audit reports
`passed_specialized_thought_bounded_rules_v0`.

Package 142 adds a bounded deterministic layer above Package 141. It does not
read perception records directly and does not promote the legacy
`ThoughtSignal` fixture. Its sole production input authority is an explicit,
read-only consumer binding to typed Package 141
`BoundedInstinctSignalRecord` evidence from a passed Package 141 audit.

## Layering

The authoritative flow is:

```text
grounded structural evidence
-> Package 141 instinct precursor
-> Package 142 precursor binding
-> one versioned deterministic specialized rule
-> bounded specialized thought result
```

Package 141 answers whether a fixed structural trigger fired. Package 142
projects that typed trigger into one higher structural conclusion inside a
fixed rule family. The result remains nonsemantic, revocable, unconsumed, and
without behavior authority.

## Consumer Binding

The consumer scope is exactly:

`package_142_specialized_thought_only`

Allowed input schema:

`ashl_package_141_bounded_instinct_signal_v0`

Allowed precursor annotations:

- `bounded_visual_closed_span_present`
- `bounded_visual_open_region_present`

The binding records the exact Package 141 audit, boundary, rule contract,
source HEAD, and source database SHA-256. The Package 141 SQLite database is
opened query-only and its SHA-256 is verified before and after every complete
run. Package 141 history is never modified.

Drive, Package 138 self-state readback, direct perception, legacy thought,
and implicit output consumers are empty allowlists.

## Rule Families

Two independent v0 families exist:

1. `specialized_family:visual_closure_projection:v0`

   Exact input: `bounded_visual_closed_span_present`

   Exact output: `bounded_visual_phase_closed_candidate`

2. `specialized_family:visual_openness_projection:v0`

   Exact input: `bounded_visual_open_region_present`

   Exact output: `bounded_visual_phase_open_candidate`

Both outputs inhabit:

`bounded_visual_structural_phase_candidate_v0`

Each family accepts exactly one typed precursor for exactly one evaluation.
It uses no learned ranking, weighted score, randomness, LLM, Codex, network,
workspace, iterative search, or recursive feedback.

The word `candidate` names a bounded structural conclusion. It grants no
candidate-ordering or action-selection authority.

## Conflict

The closed and open results are incompatible values in the same bounded
output domain. If both are produced from one Package 141 conflict bundle,
Package 142 records:

`unresolved_cross_family_conflict_preserved`

Both results remain in append-only evidence. There is no winner, ranking,
vote, random tie-break, hidden arbitration, deliberation, or selected action.

## Lifetime And Revocation

Every precursor binding has a maximum one-second monotonic lease and one
evaluation. Every specialized result inherits that exact expiry and remains
revocable. A read-side validity transition records either:

- `upstream_precursor_expired`
- `upstream_precursor_revoked`

The transition invalidates all downstream Package 142 results while leaving
the Package 141 record untouched. No active result may remain after its bound
precursor scope closes.

## Counterfactual Boundary

The Package 142 counterfactual compares the frozen Package 141 database,
Package 132 perception closure, and Package 140 self-state/drive contract
before and after specialized evaluation. The only changed surface is the
Package 142 append-only evidence store.

The following remain equivalent:

- runtime behavior authority
- memory
- purpose
- action
- output
- self-state
- drive
- perception authority

Package 142 creates no purpose, candidate ordering, selected action, memory
write, self-state mutation, perception action, output, or external control.
Hard safety, teacher authority, approved purpose scope, and the Package 132
and Package 140 frozen boundaries retain precedence.

## Store And CLI

Generated evidence is external to Git:

```text
<state-dir>/
  package_142_specialized_thought_bounded_rules_v0/
    package_142.sqlite3
```

The store is append-only and contains only Package 142 contracts, bindings,
evaluations, results, conflicts, invalidations, counterfactuals, controls,
regression receipts, and audits.

Primary commands:

```text
py -3 -m ashl_core_v1.thought.package_142_specialized_thought_cli preflight ...
py -3 -m ashl_core_v1.thought.package_142_specialized_thought_cli run-bounded ...
py -3 -m ashl_core_v1.thought.package_142_specialized_thought_cli run-controls ...
py -3 -m ashl_core_v1.thought.package_142_specialized_thought_cli run-regressions ...
py -3 -m ashl_core_v1.thought.package_142_specialized_thought_cli audit ...
```

Operator events reuse the Package 122B local event stream. Delivery failure is
visible and prevents a passed audit. Operator translations are not Qingyin
output.

## Package 143 Boundary

Package 142 does not create a thought workspace. Package 143 still needs a
separate authority for bounded workspace admission, capacity, eviction,
expiry, revocation propagation, conflict carriage, and typed consumption of
Package 142 results. It must preserve the Package 141/142 source lineage and
must not turn a workspace into purpose, action, memory, or output authority.

Package 142 does not implement Package 143 or any later Thought Engine stage.
