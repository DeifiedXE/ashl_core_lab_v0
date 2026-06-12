# ASHL Core Phase0 Status

## Current Boundary Index

- Current version: `Boundary Index Version: 2026-06-09-b65`
- Current update log: Phase0 Documentation Inventory and Consistency Reconciliation Minimal v0
- This package is documentation-only and supersedes the simpler Phase0 Documentation Consolidation Minimal v0 as the current documentation map.

## Latest Completed Package

- Latest completed capability package: Level 1 Sandbox Lesson Application Outcome Observation Minimal v0.
- Latest documentation package: Phase0 Documentation Inventory and Consistency Reconciliation Minimal v0.

## Current Safe Capability Claim

ASHL Core can validate explicit user approval, apply one reviewed lesson inside the Phase0 Level 1 toy sandbox only, and observe the sandbox application outcome while preserving audit and rollback.

Phase0 Level 1 sandbox records may contain sandbox-only lesson application and sandbox-only observation records. These are not production/runtime memory-influenced behavior.

## Current Forbidden Claims

- No production/runtime behavior.
- No memory write or retained JSONL cross-session influence rebuild.
- No retention write.
- No predictor mutation.
- No `selected_action`, `final_action`, or direct command.
- No generalized behavior change.
- No production promotion.
- No proof-of-learning claim.

No production/runtime behavior, memory write, retention write, predictor mutation, selected_action, final_action, direct command, generalized behavior change, or proof-of-learning claim is implemented by this documentation package.

Runtime behavior, memory write, retention write, predictor mutation, production lesson application, selected_action, final_action, and proof of learning remain blocked outside the explicitly scoped Phase0 Level 1 sandbox records.

## Current Known Open Gaps

- Outcome evaluation is planned but not implemented.
- Outcome evaluation is planned next and is not marked complete.
- Human review summary is planned but not implemented.
- Approval anti-replay/session binding is not implemented.
- Technical sandbox isolation beyond record-level / validation-level checks is not implemented.
- Retained JSONL deletion/invalidation after rollback is not defined.
- Mentor override must not be overclaimed beyond existing checkers.

## Current Authoritative Docs

- `docs/current_boundary_index.md`: compact boundary/version index.
- `docs/phase0_status.md`: current human-readable status map.
- `docs/phase0_capability_matrix.md`: current capability status table.
- `docs/phase0_doc_index.md`: document authority and conflict-resolution rules.
- `docs/phase0_open_risk_ledger.md`: open risk/gap ledger.
- `docs/phase0_unresolved_doc_issues.md`: unresolved documentation issues.

## Older Design Assumptions

Older design assumptions remain historical or planning context. When an older design assumption conflicts with a newer boundary document, current status document, capability matrix, or Boundary Index entry, the newer boundary/current-status document controls the current capability claim.

## Next Recommended Work

1. Level 1 Sandbox Lesson Application Outcome Evaluation Minimal v0.
2. Human review summary after outcome evaluation.
3. Future boundary package for any runtime behavior, memory, retention, predictor, selected_action, final_action, production, or proof claim.
