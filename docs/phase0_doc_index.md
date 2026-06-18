# ASHL Core Phase0 Documentation Index

## Current Status Anchors

- `README.md`
- `docs/phase0_status.md`
- `docs/current_boundary_index.md`
- `docs/level1_sandbox_outcome_evaluation_and_human_review_summary_minimal_v0.md`

## Boundary Anchors

- `docs/current_boundary_index.md`
- `docs/reviewed_lesson_application_boundary_reconciliation_v0.md`
- `docs/explicit_user_approval_source_boundary_v0.md`
- `docs/five_layer_memory_framework_boundary_v0.md`
- `docs/phase0_versioning_policy.md`
- Boundary/contract/audit files listed in `docs/phase0_doc_inventory.md`.

## Capability / Status Matrix

- `docs/phase0_capability_matrix.md`

## Inventory / Audit Docs

- `docs/phase0_doc_inventory.md`
- `docs/phase0_doc_consistency_audit.md`
- `docs/phase0_b118_documentation_alignment_minimal_v0.md`

## Open-Gap / Risk Docs

- `docs/phase0_open_risk_ledger.md`
- `docs/phase0_unresolved_doc_issues.md`

## Design Assumptions

Design assumption files describe future or conceptual architecture. They do not grant current capability unless a newer boundary/current-status document says so.

Examples:

- `docs/five_layer_memory_design_assumption_v0_1.md`
- `docs/host_dependent_idle_continuance_trace_v0.md`
- `docs/internal_auditory_feedback_design_supplement_v0.md`
- `docs/memory_influence_behavior_gate_design_v0.md`
- `docs/qingyin_audio_cochlea_decoder_design_v0.md`
- `docs/qingyin_vocal_organ_engine_design_v0.md`
- `docs/voice_instinct_assumption_v0_1.md`

## Historical / Superseded Assumptions

Historical logs and archives preserve context only. They do not override current boundary docs.

Examples:

- `docs/boundary_index_archive_2026_06.md`
- `docs/milestone_logs/*.md`
- `docs/*progress_log*.md`

## Implementation-Specific Docs

Implementation notes describe local modules, prototypes, or support concepts. Newer boundary/current-status docs control current claims.

Examples:

- `docs/core_seed.md`
- `docs/core_senses.md`
- `docs/memory_layers.md`
- `docs/state_persistence.md`

## Planning Docs

- `docs/research_plan.md`
- `docs/experiment_order.md`
- `docs/phase0_task_queue.md`
- `docs/codex_task_queue_minimal_v0.md`

Planning docs guide next work. They are not standalone proof that a capability exists.

## Test-Support Docs

Docs whose main function is smoke/test support remain useful for regression but are not current capability anchors unless listed above as anchors.

## Conflict Resolution Rule

When an older design assumption conflicts with a newer boundary document, current status document, capability matrix, or Boundary Index entry, the newer boundary/current-status document controls the current capability claim. Older design assumptions remain historical context and do not grant current capability.

This index does not claim every old doc is fully reconciled. Files classified as `unknown_needs_review` or `needs_review` in `docs/phase0_doc_inventory.md` require future human review.
