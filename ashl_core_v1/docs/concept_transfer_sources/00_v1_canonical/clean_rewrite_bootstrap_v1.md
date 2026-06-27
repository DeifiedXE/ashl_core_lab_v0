# ASHL Core Clean Rewrite Bootstrap v1

Status: bootstrap skeleton

This directory starts a clean ASHL Core v1 rewrite under `ashl_core_v1/`.
It is not a refactor of the legacy package. The legacy `ashl_core/` package
remains available only as a reference source.

## Scope

This bootstrap creates the v1 folder structure, package markers, a local docs
room, and a structure test. It does not copy legacy modules, move legacy docs,
rename legacy paths, create aliases, or connect to the old CLI and smoke suite.

## Core Lines

- `spine`: session, tick, frame, trace continuity.
- `body`: sandbox body and action records.
- `thought`: thought hints, purpose, and thought context.
- `memory`: working memory and controlled memory interface.
- `perception`: symbolic viewport and visual-spatial features.
- `bridge`: capability map and affordance binding.
- `endocrine`: endocrine signal, settling state, and tendency context.
- `voice`: first output and mentor feedback.
- `lesson`: failure event, lesson candidate, review decision, and evidence.

## Support Layers

- `governance`: policy gates, capability ledger, and reality checks.
- `runtime`: runtime session and runtime tick skeleton.

## Bootstrap Guarantees

- `ashl_core_v1_exists=True`
- `all_line_folders_exist=True`
- `runtime_folder_exists=True`
- `docs_folder_exists=True`
- `tests_folder_exists=True`
- `old_repo_modified=False`
- `old_imports_changed=False`
- `legacy_files_deleted=False`
- `bootstrap_doc_created=True`

## Not Implemented

- No migrated legacy capability.
- No old-file move, deletion, rename, or archive.
- No old import changes.
- No compatibility alias.
- No runtime loop.
- No complete Qingyin implementation.
- No external tool access.
- No docs reorganization.

## Next Step

Implement v1 core dataclasses for `spine`, `body`, `perception`, and `memory`
only. Keep each dataclass small, tested, and explicit about input and output.
