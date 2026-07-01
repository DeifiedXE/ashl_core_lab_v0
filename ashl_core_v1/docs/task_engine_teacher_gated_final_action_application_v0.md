# ASHL Core v1 Task Engine Teacher-Gated Final Action Application v0

Package 84 applies an actual `final_action` from a teacher-gated actual
`selected_action` created by Package 83.

This is the first package in this path that may set actual `final_action`. The
authority is narrow: it applies only under a teacher gate, only from an existing
selected_action candidate, and only with rollback and post-application audit.

It does not create `direct_command`, execution, task behavior execution,
selected_action changes by this package, candidate ordering changes by this
package, automatic learning approval, or memory-layer writes.

The v0 flow is demo/read-only:

1. Validate the selected_action application and Package 83 audit.
2. Build a teacher gate for actual final_action authority only.
3. Apply the selected_action candidate id as actual final_action.
4. Create rollback data to restore the previous final_action.
5. Audit that command, execution, behavior, selected_action, ordering, and
   memory boundaries remain unchanged.

Safe claim:

ASHL Core v1 Task Engine can apply a teacher-gated final_action from an actual
selected_action, with rollback and audit, while preserving direct_command,
execution, task behavior, selected_action, candidate ordering, and memory-layer
boundaries unchanged.
