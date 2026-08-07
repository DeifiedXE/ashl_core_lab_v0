# Persistent Self-State Review Gate v0

Package 137 adds one explicit teacher-review gate for structural self-state
successors. It does not add self-state readback or runtime behavior influence.

Passing audit status:

`passed_persistent_self_state_review_gate_v0`

## Authority ownership

Package 133 remains the only self-state schema and immutable-history authority:

`package_133_immutable_self_state_lineage`

Package 134 remains the only active-head and compare-and-swap authority:

`package_134_separate_active_head_cas_authority`

Package 137 owns only the exact review and cross-authority commit gate. Its
store contains proposals, reviews, intents, receipts, blocked attempts,
controls and audits. It contains neither self-state history nor an active-head
table.

The gate reuses existing State Engine teacher actors, roles, explicit-action
semantics and exact-target binding. It does not reuse the learning approval
scope and does not create a second teacher identity or teacher store.

## Exact proposal and review

Every proposal binds:

- the current Package 134 active-head ID, revision and SHA-256;
- the exact Package 133 parent record ID and SHA-256;
- the exact immutable proposed delta and its SHA-256;
- the deterministic proposed child and transition identities.

The v0 delta changes only `self_state_version` and `lineage_generation`, each
by exactly one. It preserves lineage ID, representation status and governance
profile. The complete Package 133 persistent-field allowlist remains five
opaque structural fields. Raw perception, world facts, memory, semantic
history, drive, modulation and output are rejected.

An approval is explicit and single-use. Rejection and deferral append review
and invariance evidence but do not touch Package 133 or Package 134.

## Append-only commit

The approved commit order is fixed:

1. append the exact immutable successor, transition and validation through the
   Package 133 store;
2. advance the Package 134 active head by exact revision/hash CAS;
3. append the Package 137 commit receipt.

The parent is never edited in place. Package 134 records the review ID in its
CAS event, so an approval cannot be reused even if a later Package 137 receipt
write is unavailable.

Because SQLite cannot atomically span the separate Package 133 and Package 134
authority databases, a crash after step 1 is a visible partial state: Package
133 has a newer leaf while Package 134 still points at its prior head. The
system blocks all further review commits in that condition. It does not hide
the attempted child, select it silently, roll it back, or rebase an old
approval. Repair requires a separately authorized future recovery procedure.

## Failure evidence

The control suite executes twenty real validators or isolated authority-store
transactions. It proves:

- non-allowlisted, semantic, drive, modulation and behavior fields fail;
- missing teacher action and invalid teacher identity fail;
- proposal or review tampering fails;
- wrong or stale head/parent bindings fail before another history append;
- CAS conflict rolls back Package 134 and performs no automatic rebase;
- approval reuse fails;
- reject and defer preserve both authorities;
- cross-authority partial failure remains visible and blocked;
- corrupt Package 133, Package 134 or Package 137 evidence cannot pass;
- the Package 137 store is append-only and owns no competing authority.

## Runtime boundary

Package 137 creates no self-state readback, working readback, memory influence,
drive persistence, perception or attention, Thought Engine signal, candidate
ordering, action, output or external control. Package 135 traces and Package
136 modulation still expire at session end and Package 134 recovery restores
neither.

Structural self-state mutation is not psychological-state continuation. The
new record remains opaque and carries no semantic description of Qingyin.

## External stores

```text
<package-133-state-dir>/package_133_cross_session_self_state_schema_v0/package_133.sqlite3
<package-134-state-dir>/package_134_persistent_session_recovery_v0/package_134.sqlite3
<package-137-state-dir>/package_137_persistent_self_state_review_gate_v0/package_137.sqlite3
```

Package 137 reads and coordinates the first two authorities but writes its own
audit evidence only to the third store. Approved mutation calls the existing
Package 133 append API and the existing Package 134 store's exact CAS API.

## Package 138 gates

Before any self-state readback is safe, Package 138 must add all of these:

1. a read-only consumer allowlist with zero implicit consumers;
2. exact active-head revision/hash and self-state record/hash binding;
3. stale readback invalidation when the head revision changes;
4. same-session expiry with no recovery as active runtime context;
5. opaque structural fields only, with no semantic inference;
6. drive, memory, perception, attention, thought, action and output firewalls;
7. no candidate ordering or behavior influence without separate authority;
8. counterfactual behavior equivalence before consumer activation;
9. no expansion of teacher scope through readback;
10. append-only consumption and failure auditing.

Package 138 is next. It is not implemented by Package 137.
