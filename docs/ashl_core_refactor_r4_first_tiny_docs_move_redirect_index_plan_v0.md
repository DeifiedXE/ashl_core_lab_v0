# ASHL Core Refactor R4 First Tiny Docs Move Redirect Index Plan v0

Status: completed / first tiny docs move redirect-index plan.
Runtime impact: none.
Boundary Index: 2026-06-09-b191 -> 2026-06-09-b192.

## Summary

R4 plans the first tiny low-risk docs move.
No files are moved in this package.

Plain meaning: this is the first moving permit, not the move. It chooses one low-risk historical milestone log and plans how old and new paths would stay findable later.

## Source Documents Read

- `docs/ashl_core_structural_refactor_map_v0.md`
- `docs/ashl_core_refactor_r2_compatibility_alias_plan_v0.md`
- `docs/ashl_core_refactor_r3_low_risk_docs_folder_plan_v0.md`
- `docs/ashl_core_refactor_r3a_docs_authority_freeze_v0.md`
- `docs/current_boundary_index.md`
- `docs/phase0_status.md`
- `docs/phase0_capability_matrix.md`
- `docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md`
- `docs/codex_working_context_summary.md`
- `docs/phase0_line_document_index.md`

## Selected Candidate

selected_old_path: `docs/milestone_logs/mimetic_endocrine_line_milestone_2026-06-09.md`

planned_new_path: `docs/archive/milestone_logs/mimetic_endocrine_line_milestone_2026-06-09.md`

candidate_kind: `historical_milestone_log`

risk_level: `low`

why_low_risk:

- it is not a root authority doc
- it is not current boundary status
- it is not current phase status
- it is not the capability matrix
- it is not active working context
- it is a historical milestone log
- R3 lists milestone logs as archive candidates
- moving it later has lower risk than moving current status, boundary, or matrix documents

why_not_root_authority:

- it is not in the frozen root authority docs list
- it lives under `docs/milestone_logs/`, not root `docs/`
- it is historical context only

fallback_candidate_used=False

## Redirect Index Plan

Future redirect index entry:

```json
{
  "old_path": "docs/milestone_logs/mimetic_endocrine_line_milestone_2026-06-09.md",
  "new_path": "docs/archive/milestone_logs/mimetic_endocrine_line_milestone_2026-06-09.md",
  "move_type": "docs_archive_milestone_log",
  "authority_level": "historical_context_only",
  "old_path_policy": "redirect_lookup_required",
  "new_path_policy": "canonical_after_move",
  "requires_readme_update": true,
  "requires_working_context_update": false,
  "requires_current_boundary_update": false,
  "requires_doc_consistency_update": true
}
```

Lookup rule plan:

- old path lookup rule: check redirect index when the old path no longer exists
- new path lookup rule: treat the archive path as canonical only after the future execution package moves the file
- redirect index plan created only in this R4 plan document
- no redirect index file is created in this package

## Frozen Authority Protection

Frozen root authority docs protected by R3A:

- `docs/current_boundary_index.md`
- `docs/phase0_status.md`
- `docs/phase0_capability_matrix.md`
- `docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md`
- `docs/codex_working_context_summary.md`
- `docs/research_plan.md`
- `docs/phase0_line_document_index.md`
- `docs/phase1_to_phase5_growth_substrate_plan.md`

This package does not select any frozen root authority doc.

root_authority_candidate_selected=False
frozen_authority_docs_protected=True

## Future Move Preconditions

Before a future package actually moves the selected file, all of these must be true:

- `selected_candidate_exists=True`
- `selected_candidate_not_root_authority=True`
- `selected_candidate_is_historical_or_archive_candidate=True`
- `redirect_index_entry_created=True`
- `old_path_lookup_rule_created=True`
- `new_path_lookup_rule_created=True`
- `doc_consistency_tests_updated=True`
- `README_updated_if_referenced=True`
- `codex_working_context_updated_if_referenced=True`
- `current_boundary_index_updated_if_referenced=True`
- `all_old_paths_resolvable=True`
- `all_new_paths_resolvable=True`
- `git_diff_check_passed=True`
- `targeted_tests_passed=True`
- `smoke_passed=True`

## Current Package Non-Movement Statement

```text
docs_moved=False
docs_deleted=False
docs_renamed=False
docs_archived=False
docs_lines_created=False
archive_created=False
path_references_changed=False
python_imports_changed=False
runtime_behavior_changed=False
```

## Non-Goals

- No docs moved.
- No docs deleted.
- No docs renamed.
- No docs archived.
- No `docs/archive/` folder created.
- No `docs/lines/` folder created.
- No path reference changed.
- No Python import changed.
- No Python module moved.
- No alias implemented.
- No runtime behavior changed.
- No capability changed.
- No memory write.
- No predictor read, influence, or mutation.
- No endocrine or tendency feed.
