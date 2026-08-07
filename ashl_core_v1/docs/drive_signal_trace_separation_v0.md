# Drive Signal Trace Separation v0

Package 135 establishes the first authoritative drive/regulatory signal trace
boundary. It records anonymous, bounded observations with source provenance,
event and processing time, value change, immutable same-session parent hashes,
and explicit fresh-session reset. It does not add drive modulation.

Passing audit status:

`passed_drive_signal_trace_separation_v0`

## Authority contract

The Package 135 authority is:

`package_135_anonymous_regulatory_observation_trace_only`

An authoritative trace contains only:

- one anonymous source channel and explicit bounded source kind;
- a normalized value from 0.0 through 1.0;
- event time and processing time;
- same-session sequence, parent record ID and parent SHA-256;
- previous value, exact delta and `initial_observation`, `increased`,
  `decreased` or `stable` change kind;
- source record and trace references.

The v0 source allowlist contains only
`explicit_bounded_local_regulatory_probe`. This is an engineering boundary
probe, not an endocrine chemistry claim or a semantic account of motivation.

Every semantic or authority-bearing field is either absent, null or false.
The constructor rejects purpose, desire, reward, semantic emotion, tendency,
affordance, selected-action identity, self-state content, memory content,
perception/attention modulation, candidate ordering, Thought Engine input,
action preference, output authority and cross-session persistence.

## Existing authority boundaries

Package 133 remains the sole self-state representation authority:

`package_133_immutable_self_state_lineage`

Its exact persistent field allowlist contains only opaque lineage, version,
generation, representation status and governance profile metadata. Drive is a
forbidden authority and is not self-state content.

Package 134 remains the sole active-head and structural identity recovery
authority:

`package_134_separate_active_head_cas_authority`

Package 135 opens the Package 133 and Package 134 stores read-only, verifies
their payload hashes and audits, and hashes each external evidence tree before
and after use. The Package 134 active head contains no drive field. Both
identity bindings and the Package 134 audit retain `drive_state_restored =
false` and `behavior_influence_created = false`.

## Legacy reconciliation

Package 135 inventories the actual repository instead of promoting old design
names into authority:

| Existing structure | Actual current role | Package 135 treatment |
| --- | --- | --- |
| `EndocrineSignal` | Four-axis first-stage fixture shape with free-form modulation notes | Historical value shape only; not Package 135 authority |
| cradle/manual endocrine flow | Fixed deterministic demo circulation into learning/thought/body fixture records | Conflict surface retained for regression; Package 135 traces never enter it |
| old mimetic endocrine design | Pre-Package-132 design concepts | Reuse only source/time/change and bounded-value ideas |
| `ThoughtSignal.source_endocrine_signal_refs` | Legacy fixed-circulation reference surface | Forbidden Package 135 consumer |
| tendency design | Directional candidate pressure concept | Not created and not equivalent to drive |
| affordance learning records | Teacher-governed semantic action-feasibility/outcome evidence | Owned by learning/memory; not drive |
| operator total-state snapshot | Derived process/sensor/gate status view | Not relabelled as drive |
| selected-action proposal/application | Teacher-gated Task Engine authority | Not drive and never created by a signal |
| Package 133 records | Opaque immutable self-state representation | Drive excluded |
| Package 134 active head | Structural identity CAS pointer | Drive excluded and never recovered |
| Package 132 closure | Frozen perception/attention capability and action surface | No Package 135 consumer or new action |

The old design suggestions that endocrine values could affect candidate
priority, thought, attention, memory or body intent are not current runtime
authority. Package 132-134 boundaries control.

## Drive, tendency, affordance, purpose and action

These identities remain separate:

- **Drive/regulatory trace:** an anonymous observed value and change history.
- **Tendency:** directional candidate pressure; Package 135 does not create it.
- **Affordance:** environment/action feasibility or reviewed semantic concept;
  Package 135 does not create or consume it.
- **Purpose:** pre-existing approved scope; a signal cannot create, widen or
  replace it.
- **Selected action:** teacher-gated Task Engine authority; a signal cannot
  propose, rank or select it.

No Package 135 record can serve as a synonym for any other item in this list.

## Real fresh-process reset

The official trace-boundary run uses two operating-system processes:

```text
Process A / Session A
  -> anonymous source observation
  -> trace root
  -> second source observation
  -> same-session successor with exact parent hash and delta
  -> process exits

Process B / Session B
  -> load the trace contract only
  -> do not read Session A traces or values
  -> anonymous source observation
  -> new trace root with a distinct lineage
```

Process A ends before Process B starts. The process IDs, process-instance IDs,
session IDs and signal lineage IDs differ. Process B has sequence index zero,
no parent, no previous value, and no reference to the Session A terminal trace.
Its value is not copied from Session A. The separate reset record cites the
verified Package 134 recovery pair while proving that structural identity
continuity did not carry drive state or change Package 133 content.

Package 135 has no active drive head, recovery table, latest-value authority or
cross-session restore API. Its SQLite store is append-only and external.

## External store

```text
<state-dir>/
  package_135_drive_signal_trace_separation_v0/
    package_135.sqlite3
```

The store contains legacy boundary records, one trace contract, read-only
Package 134 non-recovery evidence, source observations, signal traces, lineage
validations, authority separation, process receipts, cross-session reset and
pair records, controls, regressions and audits. It rejects private absolute
paths. Runtime artifacts remain outside the repository.

## CLI

```powershell
py -3 -m ashl_core_v1.endocrine.package_135_drive_signal_trace_cli `
  preflight --ashl-root <repo> --package-133-state-dir <p133> `
  --package-134-state-dir <p134> --state-dir <p135>

py -3 -m ashl_core_v1.endocrine.package_135_drive_signal_trace_cli `
  run-real-trace-boundary --ashl-root <repo> `
  --package-133-state-dir <p133> --package-134-state-dir <p134> `
  --state-dir <p135> --allow-drive-trace-observation

py -3 -m ashl_core_v1.endocrine.package_135_drive_signal_trace_cli `
  run-controls --state-dir <p135>

py -3 -m ashl_core_v1.endocrine.package_135_drive_signal_trace_cli `
  run-regressions --ashl-root <repo> --state-dir <p135>

py -3 -m ashl_core_v1.endocrine.package_135_drive_signal_trace_cli `
  audit --ashl-root <repo> --package-133-state-dir <p133> `
  --package-134-state-dir <p134> --state-dir <p135>
```

Inspection commands expose inventory, contract, traces, reset and audit. There
is deliberately no command to modulate perception, attention, thought, memory,
candidate ordering, action or output.

## Package 136 gates

Package 135 does not authorize Package 136. Any future same-session bounded
modulation requires all of these gates:

1. explicit same-session modulation authorization;
2. an allowlisted read-only consumer scope;
3. bounded absolute level and bounded delta;
4. same-session expiry with zero cross-session carry;
5. source, time, lineage and integrity validation;
6. purpose, desire, reward and semantic-emotion firewall;
7. no candidate-ordering, action-selection or output authority;
8. fail-to-neutral behavior;
9. before/after counterfactual and equivalence receipts;
10. preserved teacher and hard-safety authority.

Until Package 136 is separately implemented and proven, a Package 135 signal
can only be observed and audited.
