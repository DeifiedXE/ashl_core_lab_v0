# ASHL Core Refactor R3A Docs Authority Freeze v0

Status: completed / docs authority freeze plan.
Runtime impact: none.
Boundary Index: 2026-06-09-b190 -> 2026-06-09-b191.

## Summary

R3A freezes the root authority docs before any future documentation movement.
This prevents future cleanup from moving the documents that humans, Codex, tests, and status summaries rely on.

Plain meaning: keep the main switches and maps in the root `docs/` room until a later explicit redirect/index package exists.

## Source Documents Read

- `docs/ashl_core_refactor_r3_low_risk_docs_folder_plan_v0.md`
- `docs/ashl_core_structural_refactor_map_v0.md`
- `docs/ashl_core_refactor_r2_compatibility_alias_plan_v0.md`
- `docs/phase0_line_document_index.md`
- `docs/current_boundary_index.md`
- `docs/phase0_status.md`
- `docs/phase0_capability_matrix.md`
- `docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md`
- `docs/codex_working_context_summary.md`
- `docs/research_plan.md`

## Frozen Root Authority Docs

The following root authority docs are frozen:

- `docs/current_boundary_index.md`
- `docs/phase0_status.md`
- `docs/phase0_capability_matrix.md`
- `docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md`
- `docs/codex_working_context_summary.md`
- `docs/research_plan.md`
- `docs/phase0_line_document_index.md`
- `docs/phase1_to_phase5_growth_substrate_plan.md`

frozen_root_authority_doc_count=8

## Why These Docs Are Frozen

- `docs/current_boundary_index.md`: current boundary master switch.
- `docs/phase0_status.md`: plain-language current status entry point.
- `docs/phase0_capability_matrix.md`: capability status table.
- `docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md`: actual capability inventory.
- `docs/codex_working_context_summary.md`: Codex work-start navigation.
- `docs/research_plan.md`: research direction entry point.
- `docs/phase0_line_document_index.md`: nine-line documentation map.
- `docs/phase1_to_phase5_growth_substrate_plan.md`: P1-P5 growth substrate plan entry point.

## Freeze Rule

root authority docs stay in docs/ root until a future explicit redirect/index package exists.

Current frozen meaning:

- currently must not move out of `docs/` root
- currently must not be renamed
- currently must not be archived
- currently must not be moved into `docs/lines/`

## Move Preconditions

Future movement of any frozen root authority doc requires a separate package where all of these are true:

- `redirect_index_created=True`
- `old_path_lookup_rule_created=True`
- `new_path_lookup_rule_created=True`
- `README_updated=True`
- `codex_working_context_updated=True`
- `current_boundary_index_updated=True`
- `doc_consistency_tests_updated=True`
- `all_old_paths_resolvable=True`
- `all_new_paths_resolvable=True`
- `user_explicitly_approved_authority_doc_move=True`

This package does not implement a future move. It only lists the preconditions.

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
- No `docs/lines/` folder created.
- No `docs/archive/` folder created.
- No document path reference changed.
- No Python import changed.
- No Python module moved.
- No compatibility alias implemented.
- No runtime behavior changed.
- No production behavior created.
- No memory write or retention write.
- No predictor read, influence, or mutation.
- No direct endocrine feed.
- No direct tendency feed.
- No proof-of-learning claim.
- No consciousness claim.
