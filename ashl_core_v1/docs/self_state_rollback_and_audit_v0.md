# Package 139 Self-State Rollback And Audit v0

Status: Completed after the real rollback, exact roll-forward, controls, regressions, and final audit pass.

## Capability

Package 139 adds one explicitly authorized structural active-head rollback to an exact verified Package 133 ancestor. It does not restore a payload. The selected state already exists in the immutable Package 133 lineage; Package 139 changes only which existing state Package 134 selects as active.

The operation is followed by a separately authorized exact roll-forward to the preserved pre-rollback descendant. Rollback and roll-forward each append one Package 134 active-head CAS revision. Neither operation updates, deletes, replaces, or recreates a Package 133 state.

## Existing Authorities

- Package 133 remains the sole self-state schema and immutable-history authority.
- Package 134 remains the sole active-head CAS and recovery authority.
- Package 137 remains the sole teacher-reviewed successor-mutation gate.
- Package 138 remains the bounded same-session readback authority.
- Package 139 owns only exact ancestor proof, rollback/roll-forward authorization, readback invalidation gating, commit intent, receipt, failure, control, and audit evidence.

Readback authorization and teacher-review authorization do not authorize rollback or roll-forward.

## Exact Rollback Contract

A rollback authorization binds all of the following:

- current active-head ID, revision, and SHA-256;
- current self-state ID and SHA-256;
- explicit target historical self-state ID and SHA-256;
- one complete target-to-current state and transition proof;
- one lineage ID;
- one target session and process;
- one bounded lifetime and one use.

The target must be a strict ancestor. There is no `latest` selection, cross-lineage target, automatic rebase, silent refresh, or guessed fallback.

Before Package 134 CAS, every Package 138 readback bound to the changing head must already be terminal or receive an append-only invalidation lifecycle record. A readback authorization grants no rollback authority. After any head change, a fresh readback authorization is required.

## No-Fork Rule

Package 133 enforces one child per parent. An ancestor that already has a preserved descendant cannot receive another successor without forking identity. Package 139 therefore uses this formal rule:

1. Rollback selects an existing strict ancestor through a new Package 134 revision.
2. The original descendants remain immutable and addressable.
3. While that ancestor is active, Package 137 mutation preflight is blocked.
4. While that ancestor is active, ordinary Package 134 recovery is blocked.
5. No successor may be appended from the selected ancestor.
6. Only a separately authorized roll-forward to the exact preserved pre-rollback descendant recorded in the rollback receipt is allowed.
7. Once the canonical leaf is restored, normal mutation and recovery eligibility can resume.

If a process stops while an ancestor is selected, startup remains blocked. It must not guess the canonical leaf. An operator must use the exact preserved-descendant roll-forward authority. Arbitrary descendant selection is forbidden.

## Partial Failure Semantics

- Failure before or inside the Package 134 transaction leaves the active head unchanged and preserves a blocked attempt.
- A Package 134 CAS conflict leaves the authoritative head unchanged.
- A stale or reused authorization cannot execute another CAS.
- Corrupt Package 133 history blocks proof and selection.
- If Package 134 CAS commits but the Package 139 receipt append is interrupted, Package 134 remains source truth. Reconciliation binds the consumed authorization to the one matching committed CAS event and appends the missing receipt without executing a second CAS.
- Ambiguous or mismatched reconciliation blocks.

## Append-Only Evidence

The external Package 139 store contains:

- boundary contracts and source-authority bindings;
- verified ancestor proofs;
- rollback and roll-forward authorizations;
- Package 138 invalidation gates;
- commit intents and one-use authorization consumptions;
- commit and process receipts;
- blocked attempts and no-fork guards;
- counterfactual comparisons, controls, regression receipts, and audits.

It contains no Package 133 history table and no Package 134 active-head table.

## Boundaries

Rollback changes structural self-state selection only. It does not restore or copy:

- memory content;
- perception history;
- working readback;
- drive traces or modulation;
- attention or Thought Engine state;
- action or output state.

Package 135 traces remain fresh-session evidence. Package 136 modulation remains neutral after session end. Package 138 readback must be reauthorized. Package 140 is not implemented by this package.

## CLI

The CLI provides `preflight`, `show-lineage`, `authorize-rollback`, `rollback`, `authorize-roll-forward`, `roll-forward`, `reconcile`, `guided-run`, `controls`, and `audit`. Guided execution requires both explicit allow flags and an explicit target state ID.

Generated SQLite evidence stays in an external `state_dir` and is not committed.

## Next

Package 140 / Persistent Self-State And Drive Milestone closes the Package 133-139 authority line. It must preserve the no-fork and exact-roll-forward rule above.
