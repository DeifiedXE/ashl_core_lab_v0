# Phase0 Open Risk / Gap Ledger

This ledger records known documentation and design gaps. It is not a feature implementation.

## R1: Rollback and retained JSONL persistence

Rollback may reverse a sandbox application record/effect, but retained JSONL records may still exist unless a future package explicitly defines deletion or invalidation behavior.

Current rule: Retained JSONL records must not automatically rebuild memory influence across sessions after rollback. Any cross-session rebuild, replay, or influence reconstruction requires a future explicit boundary/package.

No deletion or invalidation behavior is claimed here.

## R2: influence_strength <= 0.3 threshold

The `influence_strength <= 0.3` threshold is a conservative Phase0 design cap, not an empirically validated proof of learning.

If influence_strength exceeds the allowed cap, the record must be blocked, invalid, or marked not eligible for the gated path. A checker/reviewer role must be responsible for detecting the threshold violation before any future behavior influence is permitted.

This ledger does not claim that a universal checker exists for every future path.

## R3: Sandbox isolation mechanism clarity

Current Level 1 sandbox isolation is record-level and validation-level only. Fields such as `sandbox_id` and `movement_executed: False` are not OS/process/container isolation mechanisms. They are not technical isolation proof by themselves.

A reviewer must not treat sandbox_id alone as independently verifiable technical isolation. Any stronger isolation mechanism requires a future package.

## R4: Memory warning sign vs practical gate wording

Conceptually, memory is treated as a warning signal rather than an unconditional philosophical ban. In current Phase0 implementation, however, memory-influenced behavior remains practically blocked until all required gates and checks are satisfied.

This reconciles "memory is a warning sign, not a ban command" with current Phase0 gating.

## R5: Gate order / status reconciliation

Level 1 sandbox lesson application has moved beyond design-only inside the Phase0 Level 1 sandbox path. Production/runtime lesson application remains design-only or blocked.

Phase0 Level 1 sandbox records may contain sandbox-only lesson application and sandbox-only observation records. These are not production/runtime memory-influenced behavior.

## R6: Mentor override availability mismatch

Mentor override may exist as a declared field or boundary concept, but it must not be claimed as independently verified unless the corresponding checker exists and passes.

If a TODO list says mentor override check is pending, do not claim full mentor override verification from the field alone.

## R7: Approval source correction history

The explicit user approval source boundary was added as corrective hardening after earlier design.

Current state is valid after correction, but docs must not imply this boundary existed from the beginning if it did not.

## R8: Approval replay / session binding gap

Current explicit approval validation requires `explicit_user_statement`, user actor, project_owner role, approved decision, and non-empty approval_text.

It does not yet provide session binding, nonce, timestamp freshness, package hash binding, record hash binding, or anti-replay guarantees unless separately implemented.

Approval replay protection is an open design gap and must not be claimed as implemented.

## R9: Unknown documentation consistency gaps

The known issues fixed in this package are not assumed to be exhaustive.

Any additional stale, conflicting, or ambiguous documentation claim discovered during inventory but not safely fixable is listed in `docs/phase0_unresolved_doc_issues.md` for future review.
