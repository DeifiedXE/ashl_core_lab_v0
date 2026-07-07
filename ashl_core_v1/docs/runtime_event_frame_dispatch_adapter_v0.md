# Package 96 / Runtime Event Frame Dispatch Adapter v0

Package 96 adds an adapter-only dispatch layer for bounded Runtime EventFrames.

It can classify an EventFrame event type, route it to a target engine lane, build
handler adapter records, build dispatch result records, create a safe return
payload, and audit that the dispatch stayed within Package 96 boundaries.

Supported demo lanes:

- task_event -> Task Engine
- sense_event -> Sense Interface
- learning_event -> Learning Engine
- memory_event -> Memory Engine
- state_event -> State Engine
- output_event -> Output Interface
- audit_event -> Audit Layer
- thought_event -> deferred Thought Engine, not faked
- unknown_event -> blocked

This package is not a scheduler and does not invoke live engine behavior. It does
not create dynamic child EventFrames, open-ended runtime loops, background
daemons, external execution, Unity or bridge execution, filesystem or network
execution, automatic learning approval, recursive learning, memory-layer writes,
Thought Engine cognition, first_output, voice, or production behavior.
