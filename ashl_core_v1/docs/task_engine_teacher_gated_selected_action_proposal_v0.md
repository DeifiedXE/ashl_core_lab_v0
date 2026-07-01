# ASHL Core v1 Task Engine Teacher-Gated Selected Action Proposal v0

Package 82 creates teacher-gated selected_action proposal records from a
teacher-gated candidate ordering produced by Package 81.

The proposal is not an actual `selected_action`. It does not set
`final_action`, create `direct_command`, execute actions, change task behavior,
change candidate ordering, approve learning, or write memory layers.

The v0 flow is demo/read-only:

1. Validate the Package 81 candidate-ordering application and audit.
2. Build a teacher gate for selected_action proposal authority only.
3. Create a proposal record from the top ordered candidate.
4. Create rollback data that can withdraw proposal availability.
5. Audit that no actual selected_action, final_action, command, execution,
   behavior, candidate-ordering, or memory-layer authority was created.

Safe claim:

ASHL Core v1 Task Engine can create teacher-gated selected_action proposal
records from teacher-gated candidate ordering, with rollback and audit, while
preserving actual selected_action, final_action, direct_command, execution,
task behavior, candidate ordering, and memory-layer boundaries unchanged.
