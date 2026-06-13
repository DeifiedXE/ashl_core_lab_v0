# Phase0 Versioning Policy

Package ID and Boundary Index Version serve different jobs.

## Package ID

Package ID identifies a Codex work package or implementation task. It may be assigned for every package, including documentation-only, workflow-only, smoke-only, test-only, and cleanup packages.

Required work package header fields:

- Package ID:
- Boundary Change Required: yes/no
- Boundary Index Update Required: yes/no
- Boundary Change Rationale:

## Boundary Index Version

Boundary Index Version identifies the current safety, permission, persistence, runtime, retention, predictor, sandbox execution, production, action-selection, approval-validation, or validation-boundary state.

Boundary Index is not a package counter.

A completed Codex task, added CLI, added smoke test, added unittest, added documentation, task queue status update, README update, research_plan update, documentation inventory update, human review summary, scenario plan, dry-run record, observation/evaluation bridge within an existing boundary, refactor, or wording cleanup does not automatically increment Boundary Index.

## Boundary Change Required

Boundary Index may change only when at least one of these changes:

- boundary definition
- permission scope
- persistent condition
- runtime behavior condition
- memory write condition
- retained JSONL / retention rule
- predictor influence or mutation condition
- sandbox application or execution permission
- selected_action / final_action boundary
- production promotion boundary
- approval authority or approval validation boundary
- validation boundary for any item above

## Boundary Index Update Required

If `boundary_change_required == False`, then `boundary_index_version_after` must be absent or equal to `boundary_index_version_before`.

If `boundary_index_version_after` differs from `boundary_index_version_before`, then `boundary_change_required` must be `True` and `boundary_change_rationale` must be non-empty.

## Boundary Change Rationale

Boundary change rationale must name the actual boundary or validation-boundary change. It must not merely say that a task completed, a CLI was added, tests passed, documentation changed, or a task queue status changed.

This policy package updates the validation boundary once because versioning governance now constrains when Boundary Index may change.

## Forbidden

This policy does not add runtime behavior, memory write, retained JSONL write, retention write, predictor mutation, selected_action, final_action, direct command, production promotion, approval replay/session binding, Level 2 application/execution, or proof-of-learning capability.
