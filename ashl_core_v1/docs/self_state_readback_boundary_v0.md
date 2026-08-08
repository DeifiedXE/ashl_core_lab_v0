# Self-State Readback Boundary v0

Package 138 adds a bounded representation-access boundary. It does not add a
production behavior consumer, persistent working readback, semantic identity
or rollback.

Passing audit status:

`passed_bounded_same_session_self_state_readback_boundary_v0`

## Authority contract

Package 133 remains the sole immutable self-state schema and history authority.
Package 134 remains the sole exact active-head revision/hash CAS and recovery
authority. Package 137 remains the sole teacher-reviewed successor-mutation
gate. Package 138 owns only authorization, exact read binding, read-only
consumption, expiry, stale invalidation and audit evidence.

Every authorization and readback binds all of these exact values:

- active-head ID, revision and SHA-256;
- Package 133 self-state record ID and SHA-256;
- runtime session ID and Package 138 process instance;
- one exact consumer ID;
- one monotonic expiry.

The logical process identity must equal the current Package 134 head binding,
and successful consumption must run under that binding's recorded OS process.
Once the exact session has a clean-shutdown record, no new authorization or
readback may be created for it.

No path selects `latest`, follows a changed head, refreshes a stale readback or
automatically rebinds. Package 137 teacher approval authorizes only the exact
state mutation it reviewed; it never implies consumer authorization.

## Exposed representation

The readback exposes only the five Package 133 opaque structural fields:

- `self_state_lineage_id`
- `self_state_version`
- `lineage_generation`
- `representation_status`
- `governance_profile_version`

It also exposes the minimum exact-head, state-hash, parent-hash and session
provenance identifiers needed to validate the binding. Session provenance is
represented by a digest on the readback surface. It does not expose raw
perception, memory content, semantic history, output content, world facts,
personality text, autobiographical narrative or psychological interpretation.

## Consumer allowlist

The production allowlist is empty. There are zero implicit consumers.

The only v0 consumer is isolated audit infrastructure:

`package_138_audit_only_structural_readback_consumer`

Repository inventory rejects existing working-readback, learning, active
perception, candidate-ordering, drive-modulation and operator-view surfaces as
Package 138 consumers because those paths have owners or behavior authority
outside this package.

## Lifetime and recovery

A readback is active only inside the explicitly bound session and process. The
official authorization is capped at 30 seconds and the context expires earlier
when its worker ends. Expiry and consumption remain append-only audit records;
there is no persistent active readback slot.

The real run uses Package 134's existing exact recovery authority twice. A
fresh Session A process advances the reviewed Package 137 head from revision 3
to 4; a distinct fresh Session B process then advances it from revision 4 to
5. Both CAS operations preserve the same Package 133 state identity and only
rebind the active session/process. Session A's readback is marked stale after
the second CAS. Session B starts with no restored readback, is blocked without
a fresh authorization, and creates a distinct exact binding only after that
authorization. The prior context is never restored, consumed, refreshed or
rebound.

## Counterfactual boundary

The isolated absent/present comparison records one permitted difference:

`readback_surface`

The compared fingerprints for runtime behavior, selected action, memory,
drive, perception history, self-state history, active head, output and Package
134 recovery result remain equal. This is audit evidence for an empty
production allowlist, not permission to activate a future production consumer.

Package 138 creates no memory influence, drive influence, perception or
attention influence, candidate ordering, purpose expansion, Thought Engine
input, action or output.

## Append-only evidence

The external Package 138 store records consumer inventory, authority source
bindings, contract, allowlist, authorizations, readbacks, consumptions,
lifecycle transitions, blocked attempts, process receipts, fresh-process reset,
counterfactual snapshots, controls, regressions and audits. It contains neither
Package 133 self-state history nor the Package 134 active-head table.

Authorization failures, unknown consumers, expired or reused authorization,
session/process/head/state mismatch, stale invalidation, semantic or behavior
authority injection and corrupt evidence are visible as blocked or control
evidence. The store supports inserts only.

## Package 139 prerequisites

Package 138 does not implement rollback. Package 139 still requires:

1. rollback authorization distinct from Package 137 review;
2. exact current head and exact target historical state binding;
3. proof that the target is a verified ancestor in one Package 133 lineage;
4. append-only rollback attempt and outcome history;
5. a new exact Package 134 CAS head revision;
6. preservation of intervening history and failed attempts;
7. stale Package 138 readback invalidation before rollback commit;
8. conflict and cross-authority partial-failure handling;
9. a ban on restoring memory, perception, drive, action or output state;
10. counterfactual and cross-authority integrity audit.

Package 139 must not reinterpret readback authorization as rollback authority.
