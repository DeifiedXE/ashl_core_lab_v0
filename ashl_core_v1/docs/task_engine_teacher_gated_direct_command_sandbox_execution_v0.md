# ASHL Core v1 Task Engine Teacher-Gated Direct Command Sandbox Execution v0

Package 85 converts a teacher-gated `final_action` into an actual
`direct_command`, then executes that command inside a bounded deterministic
sandbox.

This is not external execution. The package does not create OS commands,
network calls, filesystem writes, Unity operations, bridge operations, task
behavior learning, automatic learning approval, or memory-layer writes.

The v0 flow is demo/read-only:

1. Validate the final_action application and Package 84 audit.
2. Build a teacher gate for direct_command plus bounded sandbox execution only.
3. Map final_action to an allowlisted direct_command deterministically.
4. Create a pre-execution sandbox snapshot.
5. Execute the command inside an inert deterministic sandbox record.
6. Create restore data that can return the sandbox to the snapshot state.
7. Audit that no external execution, behavior learning, automatic approval, or
   memory-layer write occurred.

Safe claim:

ASHL Core v1 Task Engine can convert teacher-gated final_action into
direct_command and execute it inside a bounded deterministic sandbox with
pre-execution snapshot, restore record, and audit, while blocking external
execution, Unity/bridge execution, task behavior learning, automatic learning
approval, and memory-layer writes.
