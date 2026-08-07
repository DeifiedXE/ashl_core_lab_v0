# Same-Session Drive Modulation v0

Package 136 adds an explicitly authorized, bounded and fail-to-neutral
modulation infrastructure outside the frozen perception capability line. It
does not add a production modulation consumer or change production runtime
behavior.

Passing audit status:

`passed_same_session_drive_modulation_infrastructure_v0`

## Authority separation

Package 135 remains the only signal evidence authority:

`package_135_anonymous_regulatory_observation_trace_only`

Package 136 owns only the temporary derivation and application boundary:

`package_136_same_session_bounded_modulation_infrastructure`

A Package 135 trace is immutable evidence. A Package 136 modulation is a
separate, explicitly authorized, single-use same-session effect derived from
that evidence. Neither record is self-state, memory, purpose, desire, reward,
semantic emotion, preference or action authority.

## Consumer inventory and allowlist

The source-grounded inventory scans fourteen current surfaces. Existing
perception, attention, deadline, focus, sufficiency, candidate ordering,
selected action, memory, self-state, recovery, output and continuous-loop
parameters all retain their current authority owners. None is eligible as a
Package 136 production consumer.

The authoritative v0 allowlist therefore contains:

- production consumers: none;
- audit-only consumers:
  `package_136_audit_only_counterfactual_scalar_surface`.

The audit-only scalar exists solely to exercise authorization, clamp,
expiration, fault and counterfactual behavior. It is not imported by runtime,
perception, thought, task, memory, state or body modules and cannot influence
production behavior.

## Bounded contract

The v0 contract fixes these limits:

- neutral offset: `0.0`;
- maximum absolute offset: `0.2`;
- maximum delta per application: `0.1`;
- maximum authorization lifetime: `30,000,000,000 ns`;
- one authorized application in one exact runtime session and signal lineage;
- read-only Package 135 trace consumption;
- no cross-session carry.

Authorization binds the exact consumer, runtime session, signal lineage,
source trace ID and trace SHA-256. The policy validates source, event time,
processing time, lineage and authorization expiry before deriving a value.
Both level and per-application delta are clamped.

## Fail to neutral

The effective offset returns to `0.0` when authorization is missing or
invalid, signal integrity fails, the consumer is not allowlisted, session or
lineage does not match, authorization expires or was already consumed, the
consumer faults, or the session ends.

Package 134 recovery never restores Package 136 authorization, application or
effective offset. A fresh process starts neutral, while Package 135 separately
creates a fresh signal root. Structural identity recovery therefore remains
equivalent with and without the prior same-session modulation.

## Counterfactual evidence

The official A/B evidence freezes two complete boundary snapshots. The neutral
and bounded-modulated paths differ only at:

`audit_only_regulatory_offset`

The following authoritative fingerprints remain equal:

- hard safety;
- teacher authority;
- approved purpose scope;
- candidate set and ordering;
- selected action;
- memory;
- perception history;
- Package 133 self-state;
- output;
- Package 134 recovery result.

Process A applies the audit-only bounded offset and neutralizes it at session
end. Fresh Process B loads no Package 136 authorization or application, begins
at neutral, and verifies the independent Package 135 fresh-root trace. The two
process IDs and process-instance IDs are distinct.

## Forbidden capability

Package 136 creates no perception or attention capability, Thought Engine,
candidate ordering, action, purpose, memory write, self-state write,
observation extension, focus change, output or external control. It does not
interpret a drive trace as desire, reward, emotion, purpose or preference.
There is no persistent modulation head and no recovery API.

## External store

```text
<state-dir>/
  package_136_same_session_drive_modulation_v0/
    package_136.sqlite3
```

The store is append-only and contains inventory, source binding, contract,
allowlist, authorization, policy, derivation, audit-only application,
neutralization, counterfactual, process, cross-session, control, regression
and audit records. It stores no production consumer state and no current
modulation value.

## CLI

```powershell
py -3 -m ashl_core_v1.endocrine.package_136_drive_modulation_cli `
  preflight --ashl-root <repo> --package-133-state-dir <p133> `
  --package-134-state-dir <p134> --package-135-state-dir <p135> `
  --state-dir <p136>

py -3 -m ashl_core_v1.endocrine.package_136_drive_modulation_cli `
  run-real-counterfactual --ashl-root <repo> `
  --package-133-state-dir <p133> --package-134-state-dir <p134> `
  --package-135-state-dir <p135> --state-dir <p136> `
  --allow-same-session-drive-modulation

py -3 -m ashl_core_v1.endocrine.package_136_drive_modulation_cli `
  run-controls --state-dir <p136>

py -3 -m ashl_core_v1.endocrine.package_136_drive_modulation_cli `
  run-regressions --ashl-root <repo> --state-dir <p136>

py -3 -m ashl_core_v1.endocrine.package_136_drive_modulation_cli `
  audit --ashl-root <repo> --package-133-state-dir <p133> `
  --package-134-state-dir <p134> --package-135-state-dir <p135> `
  --state-dir <p136>
```

There is no CLI that selects a production consumer or supplies an arbitrary
offset.

## Package 137 gates

Package 137 may add teacher-gated self-state mutation only after proving:

1. Package 133 remains the sole self-state representation schema.
2. The exact Package 134 active head and expected CAS revision are bound.
3. Teacher authorization names the exact immutable parent state.
4. Persistent fields remain opaque and allowlisted.
5. Drive and modulation remain excluded from self-state content.
6. Memory, perception, semantic history and output content remain excluded.
7. An append-only transition precedes active-head CAS.
8. Stale, conflicting, corrupt and ambiguous mutations block.
9. Teacher rejection and defer remain in history.
10. Mutation creates no runtime behavior influence before a separate readback
    gate.
