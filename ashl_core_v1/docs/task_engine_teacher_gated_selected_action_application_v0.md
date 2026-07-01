# ASHL Core v1 Task Engine Teacher-Gated Selected Action Application v0

Package 83 applies an actual `selected_action` from a teacher-gated
`selected_action` proposal created by Package 82.

This is the first package in this path that may set actual `selected_action`.
The authority is narrow: it applies only under a teacher gate, only from an
existing proposal candidate, and only with rollback and post-application audit.

It does not create `final_action`, `direct_command`, execution, task behavior
execution, candidate ordering changes by this package, automatic learning
approval, or memory-layer writes.

The v0 flow is demo/read-only:

1. Validate the selected_action proposal and Package 82 proposal audit.
2. Build a teacher gate for actual selected_action authority only.
3. Apply the proposed candidate id as actual selected_action.
4. Create rollback data to restore the previous selected_action.
5. Audit that final_action, command, execution, behavior, ordering, and memory
   boundaries remain unchanged.

Safe claim:

ASHL Core v1 Task Engine can apply a teacher-gated selected_action from a
teacher-gated selected_action proposal, with rollback and audit, while
preserving final_action, direct_command, execution, task behavior, candidate
ordering, and memory-layer boundaries unchanged.
