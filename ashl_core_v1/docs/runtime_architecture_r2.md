# ASHL Core v1 Runtime Architecture R2

Status: runtime architecture refactor definition

This document redefines the ASHL Core v1 runtime architecture after Packages 38
through 55. It does not add runtime capability, rename modules, move files, or
create another tick package. It names the runtime structure that already emerged
from the task, working-memory, review, memory trace, readback, closure, and
teacher-console work.

Plain meaning:

> Runtime is no longer centered on tick.
> Tick is one part of Task Engine.
> Task Engine is the runtime's main circulation spine.

## Runtime R2 Top Level

```text
Runtime
├── Task Engine
├── State Engine
├── Memory Engine
├── Teacher Interface
├── Sense Interface
└── Output Interface
```

The R2 architecture uses engines as stable ownership zones. Future runtime work
should attach to one of these engines instead of extending the old package chain
as another tick milestone.

## Task Engine

Task Engine is the runtime main loop.

It owns:

- Task Creation
- ActiveTaskFrame
- Working Memory
- Tick Builder
- Bounded Runner
- Task Closure
- Task Disposition
- Suspended Task
- Task Resume

The task loop is:

```text
Task
↓
Working Memory
↓
Tick
↓
Working Memory Update
↓
Task Continue?
↓
Yes: next Tick
↓
No: Task Closure
```

Tick is a unit inside Task Engine. It is not the runtime identity.

## Memory Engine

Memory Engine does not directly drive runtime execution.

It owns:

- Learning Candidate
- Teacher Review
- Reviewed Learning
- MemoryLearningTrace
- MemoryRoutingTrace
- MemoryApplicationData
- Readback
- Readback Apply

Its flow is:

```text
Learning Candidate
↓
Teacher Review
↓
Reviewed Learning
↓
Memory Trace
↓
Memory Application
↓
Readback
↓
Readback Apply
↓
Working Memory
```

Memory Engine provides advisory context back into Working Memory. It does not
create free action selection, execution, or direct promotion into Core,
Long-term, Archive, or Anchor memory.

## State Engine

State Engine owns continuity.

It includes:

- State Snapshot
- Session Summary
- Last Trace Summary
- Future State Persistence

State Engine answers:

- What was the last known runtime state?
- Which task or loop evidence should the next session read first?
- What summary is safe to preserve as continuity context?

State Engine does not decide actions.

## Teacher Interface

Teacher Interface is the external human control surface.

It includes:

- Teacher Console
- Review
- Task Start
- Task Stop
- Task Resume
- Candidate Review

The teacher can start, stop, inspect, review, and mark records. The teacher
interface does not become an automatic scheduler.

## Sense Interface

Sense Interface is the entry side for observed or supplied events.

Current sources:

- Sandbox Event
- Toy Cases

Future sources:

- Vision
- Audio
- Bridge

Sense Interface supplies input to Task Engine and Memory Engine through bounded
records. It does not perform semantic vision or external bridge operation in R2.

## Output Interface

Output Interface is the exit side for runtime-produced signals.

Current outputs:

- Body Signal

Future outputs:

- Voice
- External Bridge

Output Interface receives decisions or signals after the runtime path permits
them. It does not bypass Task Engine or Teacher Interface.

## Runtime Main Circulation

Runtime R2 is described as a task circulation:

```text
Task
↓
Working Memory
↓
Tick
↓
Working Memory Update
↓
Task Continue?
↓
Tick ...
↓
Task Closure
↓
Learning Candidate
↓
Teacher Review
↓
Memory Trace
↓
Memory Application
↓
Readback
↓
Apply To Working Memory
↓
Next Task
```

The important refactor is conceptual ownership:

- Task Engine owns task continuity and ticks.
- Memory Engine owns reviewed learning and readback.
- Teacher Interface owns human permission and inspection.
- State Engine owns session continuity.
- Sense and Output interfaces own future I/O edges.

## Package Mapping

| Package | Existing work | R2 owner |
| --- | --- | --- |
| 38 | Task Working Memory | Task Engine |
| 39 | Two Tick Working Memory Audit | Task Engine |
| 40 | Third Tick Readiness | Task Engine |
| 41 | Third Tick Stub | Task Engine |
| 42 | Three Tick Pattern and Manual Tick Builder | Task Engine |
| 43 | Bounded Task Runner | Task Engine |
| 44 | Task Closure and Learning Candidate Extraction | Task Engine, Memory Engine |
| 45 | Teacher Console | Teacher Interface |
| 46 | Multi Case Tasks | Task Engine, Sense Interface |
| 47 | Closure Candidate Audit | Task Engine, Memory Engine |
| 48 | Teacher Review | Teacher Interface, Memory Engine |
| 49 | Memory Trace | Memory Engine |
| 50 | Readback Preview | Memory Engine |
| 51 | Readback Apply | Memory Engine, Task Engine |
| 52 | Readback Contrast | Task Engine, Memory Engine |
| 53 | Closed Loop Evidence | Task Engine, Memory Engine |
| 54 | Guided Teacher Console | Teacher Interface |
| 55 | Controlled Growth Audit | Teacher Interface, Task Engine, Memory Engine |

## Engine Map

```text
Task Engine
  task creation
  active task frame
  bounded task runner
  tick builder
  task closure
  task disposition
  suspended task
  resume entry

Memory Engine
  learning candidate intake
  reviewed learning
  memory trace
  routing trace
  memory application data
  readback preview
  readback apply

State Engine
  state snapshot
  session summary
  last trace summary
  future state persistence

Teacher Interface
  guided console
  review command
  task start / stop / resume
  candidate review
  growth readiness inspection

Sense Interface
  sandbox event
  toy case
  future visual input
  future audio input
  future bridge input

Output Interface
  body signal
  future voice output
  future bridge output
```

## Refactor Goals

After R2, new runtime packages should be named by engine responsibility, not by
the next tick milestone.

Preferred wording:

- Task Engine state persistence
- Memory Engine readback use
- Teacher Interface review workflow
- State Engine session handoff
- Sense Interface sandbox input
- Output Interface body signal

Avoid returning to:

- Tick 4
- Tick 5
- next tick package
- another tick bridge

## Future Expansion Points

State Engine:

- persist last run summary
- persist active or suspended task handoff
- preserve last closed-loop evidence bookmark

Task Engine:

- resume task from persisted Working Memory
- bounded task continuation through engine API
- task resume audit

Memory Engine:

- apply readback hints under stricter review policy
- route reviewed learning beyond working-memory readback only after a future
  memory-layer package

Teacher Interface:

- single command guided workflow
- human-readable task state inspection
- review queue management

Sense Interface:

- sandbox event intake
- visual-spatial grounding intake
- bridge capability feedback intake

Output Interface:

- body signal preview
- future voice output review
- future bridge output review

## R2 Scope Boundary

This R2 document creates architecture ownership only.

It creates:

- Runtime Architecture R2
- Engine Map
- Package Mapping
- Future Expansion Points

It does not create:

- new runtime
- new tick
- new memory write
- new loop
- scheduler
- action execution
- free action selection
- automatic learning approval
- Core, Long-term, Archive, or Anchor memory write
- Unity, voice, or bridge operation

## Next Work Direction

Package 56 and later should be planned against engines.

Recommended next package:

```text
ASHL Core v1 State Engine Cradle Persistence Handoff Minimal v0
```

Plain meaning:

> Preserve the last run summary, active or suspended task state, and closed-loop
> evidence bookmark as State Engine continuity data for the next session.
