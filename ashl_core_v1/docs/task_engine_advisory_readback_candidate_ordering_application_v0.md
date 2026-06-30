# Task Engine Advisory Readback Candidate Ordering Application v0

Package 81 allows reviewed-concept advisory readback hints to influence
candidate ordering only after a teacher gate passes.

Allowed authority:

- Reorder an existing candidate id list.
- Apply only to newly initialized Task Working Memory.
- Preserve the candidate id set.
- Create rollback data for restoring baseline ordering.
- Audit that selected_action, final_action, direct_command, execution, task
  behavior, and memory-layer writes remain unchanged.

Forbidden authority:

- Select an action.
- Change final_action.
- Create a direct command.
- Execute an action.
- Mutate a running task.
- Write Core / Long-term / Archive / Anchor memory.
- Create automatic learning approval.

The deterministic demo changes:

`("step_forward", "observe", "turn_left")`

into:

`("observe", "turn_left", "step_forward")`

because `observe_before_direct_retry` promotes observe-like candidates and
`avoid_same_failed_direct_retry` demotes repeated direct retry.
