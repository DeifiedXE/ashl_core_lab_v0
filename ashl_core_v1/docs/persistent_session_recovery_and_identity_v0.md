# Persistent Session Recovery And Identity v0

Package 134 performs the first explicitly authorized fresh-process recovery of
the immutable self-state lineage defined by Package 133. It proves structural
identity continuity across process and session boundaries. It does not restore
psychological content or grant recovered state any behavior authority.

Passing audit status:

`passed_persistent_session_recovery_and_identity_v0`

## Capability delta

Package 134 can resolve the one valid Package 133 lineage and canonical leaf,
initialize a separate active-head pointer for Process A, record Process A's
clean shutdown, and bind a new Process B session to that exact lineage through
an atomic compare-and-swap. Both operations require separately persisted,
single-use local-operator authorizations.

The official run uses two operating-system processes. Process A exits before
Process B starts. Recovery preserves the Package 133 state record ID, state
hash and lineage ID while changing only the session/process binding and active
head revision.

## Authorities

Package 133 remains the only self-state representation authority:

`package_133_immutable_self_state_lineage`

Package 134 owns only the separate mutable pointer authority:

`package_134_separate_active_head_cas_authority`

The Package 133 SQLite store is opened read-only and its complete external
state tree is hashed before and after recovery. Package 134 never inserts,
updates or deletes a Package 133 state, transition, validation or audit record.

The active head contains only opaque identity and integrity metadata:

- Package 133 lineage, leaf record and leaf SHA-256;
- self-state version and lineage generation;
- bound session and process identities;
- monotonic head revision;
- previous active-head SHA-256;
- authority and source references.

It is not a second self-state representation.

## Recovery protocol

```text
read-only Package 133 lineage validation
  -> explicit one-use Process A authorization
  -> active head revision 1
  -> Process A identity binding
  -> clean shutdown receipt
  -> explicit one-use Process B authorization against exact revision/hash
  -> unique-head and canonical-leaf resolution
  -> atomic CAS to active head revision 2
  -> Process B identity binding to the same Package 133 leaf
```

The CAS transaction updates the singleton active head and appends its CAS,
authorization-consumption, resolution and identity-binding evidence together.
History tables expose no update or delete API. A fault injected after the head
update but before commit rolls the whole transaction back.

## Conservative failure semantics

Recovery blocks instead of guessing when authorization is absent, expired,
reused or scoped to another lineage; when the active head is missing, corrupt,
stale or ambiguous; when Package 133 has more than one lineage or leaf; when
the previous shutdown is not clean; when an exact CAS loses; or when a partial
write is detected.

There is no `latest` fallback, automatic branch selection, repair-by-overwrite,
identity fork, or silent recovery. Failed attempts and control results remain
auditable.

## Content boundary

Recovery binds a new session to opaque Package 133 identity metadata only. It
does not load, restore, copy or create:

- memory content or working readback;
- perception or temporal history;
- drive or attention state;
- Thought Engine state;
- output or action state;
- learning, behavior influence or an automatic follow-up action.

Package 134 therefore proves structural cross-session identity continuity,
not complete psychological-state continuation and not a persistent-self claim.

## External store

Package 134 writes only beneath an explicitly supplied external state root:

```text
<state-dir>/
  package_134_persistent_session_recovery_v0/
    package_134.sqlite3
```

The singleton `active_self_state_head` table is the only mutable authority.
Authorization, CAS, binding, shutdown, resolution, process, pair, control,
regression and audit records are append-only and physically separate from it.
Private absolute paths are rejected from persisted records.

## CLI

```powershell
py -3 -m ashl_core_v1.state.package_134_persistent_session_recovery_cli `
  preflight `
  --ashl-root <ashl-root> `
  --package-133-state-dir <external-package-133-state> `
  --state-dir <external-package-134-state>

py -3 -m ashl_core_v1.state.package_134_persistent_session_recovery_cli `
  guided-run `
  --ashl-root <ashl-root> `
  --package-133-state-dir <external-package-133-state> `
  --state-dir <external-package-134-state> `
  --allow-session-recovery

py -3 -m ashl_core_v1.state.package_134_persistent_session_recovery_cli `
  run-regressions `
  --ashl-root <ashl-root> `
  --state-dir <external-package-134-state>

py -3 -m ashl_core_v1.state.package_134_persistent_session_recovery_cli `
  audit `
  --ashl-root <ashl-root> `
  --package-133-state-dir <external-package-133-state> `
  --state-dir <external-package-134-state>
```

`show-head`, `show-authorizations`, `show-cas-history`, `show-bindings`,
`show-recovery-run` and `show-audit` expose the corresponding evidence. The
recovery command blocks without `--allow-session-recovery`.

## Package 135 boundary

Before Package 135 there is still no drive-signal trace authority, same-session
drive modulation, self-state behavior influence, persistent working readback,
persistent attention, persistent Thought Engine state, automatic learning,
automatic action, automatic output or psychological continuity claim.

Package 135 is the next package. It must preserve Package 133 as representation
authority and Package 134 as the narrowly scoped active-head/recovery authority.
