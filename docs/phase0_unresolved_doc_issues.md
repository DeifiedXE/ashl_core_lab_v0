# Phase0 Unresolved Documentation Issues

This file records ambiguous or suspicious documentation findings that were not safely auto-fixed.

| issue_id | file_path | suspicious / conflicting wording summary | why not auto-fixed | suggested future action | risk |
| --- | --- | --- | --- | --- | --- |
| U1 | `README.md`, `docs/research_plan.md` | Historical sections mention local memory checks, selected_actions, proof-of-learning disclaimers, Long-term Memory, mentor override, and runtime tendency evidence across many older milestones. | These sections are historical and often include correct negative boundary language; broad rewriting could erase useful project history. | Use `docs/phase0_status.md`, `docs/phase0_capability_matrix.md`, and `docs/current_boundary_index.md` as current controls; audit older sections incrementally when touched. | medium |
| U2 | Files classified `unknown_needs_review` in `docs/phase0_doc_inventory.md` | Exact current authority could not be safely determined from filename alone. | The inventory is conservative and avoids guessing authority. | Human review should either reclassify these files or add file-local authority notes. | low |
| U3 | Long-term Memory design docs | Some wording describes future five-layer architecture while boundary docs describe current prototypes. | Both are useful if read with version priority; deletion or large rewrite is unnecessary. | Keep version-priority notes and review before any Long-term Memory expansion. | medium |
| U4 | Mentor override references | Some docs describe mentor override as availability/readiness while others describe a specific checker result. | Context differs by package; broad replacement could make true scoped checks less precise. | Future docs should distinguish declared field, readiness concept, and passed checker result. | medium |

The known issues fixed in this package are not assumed to be exhaustive. No additional unresolved documentation issues were identified during this pass beyond the open risk ledger items and the inventory entries marked for review. This is not proof that none exist.
