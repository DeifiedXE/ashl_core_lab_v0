# Cross-Session Self-State Schema v0

Package 133 creates the first authoritative representation contract for
persistent self-state. It is a State Engine schema and persistence boundary,
not a recovery runtime and not proof that a continuous self already exists.

Passing audit status:

`passed_cross_session_self_state_schema_v0`

Representation status:

`representation_only_not_recovery`

## Capability delta

Package 133 can create and validate one immutable parent-to-child structural
self-state lineage with distinct session provenance, monotonic versions and a
canonical SHA-256 parent link. It can persist the records in an external,
append-only State Engine store.

Package 133 does not load that lineage during session startup, select an active
head, recover a session, affect behavior, emit a drive signal, write memory,
change perception, select an action, call Thought Engine, or create output.

## Existing state-like structures

The Package 133 inventory statically parses and hashes the actual source files.
These structures retain their existing roles:

| Structure | Actual role | Package 133 boundary |
| --- | --- | --- |
| Legacy `session_persistence` snapshot | Overwritten session convenience file with arbitrary `state_values` | Not self-state; payload and overwrite store are not reused |
| State Engine cradle handoff | Teacher-visible task/session continuity handoff and bookmarks | Reuse State Engine ownership, explicit state directory and validation boundary only |
| State Engine resume chain | Manual, teacher-gated future resume handoff | Not self-state; no recovery entry or command is imported |
| Teacher-gated session checkpoint | Session runtime, stack, readback and review checkpoint | Session provenance only; checkpoint payload and mutable session head are excluded |
| Task working memory | One task's active/suspended frame | Ephemeral task context, not self-state |
| Working readback | Reviewed, interpreted advisory context | Memory content and behavior influence are excluded |
| Governed memory records | Reviewed concepts, routing and application data | Memory content is never copied into self-state |
| Perception and temporal history | Raw/derived evidence and grounded temporal provenance | History remains authoritative in its own append-only stores; no payload is copied |
| Operator runtime status | Derived running/sleeping/stopped and hardware status view | Operational display state, not persistent self-state |

The earlier State Engine remains the continuity authority. A dedicated store is
required because the old handoff files overwrite prior state and can contain
task, working-memory and trace summaries. Reusing those payloads would collapse
the boundary Package 133 is required to establish.

## Authoritative persistent fields

The contract permits exactly five persistent structural fields:

- `self_state_lineage_id`: opaque canonical lineage identity;
- `self_state_version`: monotonic record version;
- `lineage_generation`: zero-based parent-to-child generation;
- `representation_status`: fixed to `representation_only_not_recovery`;
- `governance_profile_version`: fixed Package 133 boundary version.

Session IDs, parent IDs, transition IDs, hashes and source references are
provenance/integrity metadata. They are not self-state content.

The schema has no generic `state_values`, notes, summary text, labels, facts,
memory items, perceptual payloads, output text or extension dictionary.

## Forbidden content

Constructors, lineage validation, store validation and negative controls reject:

- raw or derived perception payloads;
- world facts or environment state;
- memory content or working readback;
- semantic or autobiographical history;
- output content;
- unknown persistent field names;
- private absolute paths.

Opaque source record references remain references only. Package 133 does not
dereference them into content.

## Parent-to-child lineage

One valid v0 chain has this shape:

```text
parent representation
  version = 1
  generation = 0
  source session = A
  parent = null

validated_schema_successor transition
  scope = representation_only
  source session = B
  recovery performed = false

child representation
  version = 2
  generation = 1
  source session = B
  parent id/hash = exact parent
```

Sessions A and B must differ. The child accumulates both opaque session
provenance references. A second child from the same parent is rejected in v0;
there is no fork, merge, active-head selection or rollback authority.

Every state record and transition has canonical SHA-256 integrity. The SQLite
store also hashes each serialized payload and verifies the parent/child chain,
foreign keys, uniqueness constraints and absence of forbidden authority tables.

## Store

Package 133 writes only to an explicitly supplied external state directory:

```text
<state-dir>/
  package_133_cross_session_self_state_schema_v0/
    package_133.sqlite3
```

The store contains append-only inventory, contract, state, transition, lineage,
control, regression and audit records. It exposes no update, delete, recovery or
active-head API. It does not write to `ashl_core_v1/data`.

## CLI

```powershell
py -3 -m ashl_core_v1.state.package_133_cross_session_self_state_schema_cli `
  preflight `
  --ashl-root <ashl-root> `
  --state-dir <external-package-133-state> `
  --package-132-state-dir <external-package-132-state>

py -3 -m ashl_core_v1.state.package_133_cross_session_self_state_schema_cli `
  inventory-state-like-structures `
  --ashl-root <ashl-root>

py -3 -m ashl_core_v1.state.package_133_cross_session_self_state_schema_cli `
  create-schema-chain `
  --ashl-root <ashl-root> `
  --state-dir <external-package-133-state> `
  --parent-session-id <opaque-session-a> `
  --child-session-id <opaque-session-b>

py -3 -m ashl_core_v1.state.package_133_cross_session_self_state_schema_cli `
  run-regressions `
  --ashl-root <ashl-root> `
  --state-dir <external-package-133-state>

py -3 -m ashl_core_v1.state.package_133_cross_session_self_state_schema_cli `
  audit `
  --ashl-root <ashl-root> `
  --state-dir <external-package-133-state> `
  --package-132-state-dir <external-package-132-state>
```

`synthetic-smoke`, `show-contract`, `show-boundaries`, `show-lineage` and
`show-audit` provide explicit schema/test inspection. No command applies a
self-state to runtime behavior.

## Package 134 gap

Package 134 must still implement and prove all of the following before a real
cross-session recovery claim is possible:

- explicit recovery authorization;
- authoritative active-head compare-and-swap semantics;
- session-startup load and identity binding;
- crash, interruption and partial-write handling;
- recovery selection and conflict policy;
- append-only recovery/rollback audit history;
- a real fresh-process recovery run.

Package 133 deliberately leaves each item absent. Package 134 may use this
schema only under its own authority and tests.
