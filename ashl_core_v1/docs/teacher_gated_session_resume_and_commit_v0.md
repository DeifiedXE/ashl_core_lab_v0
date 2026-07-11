# Package 116 / ASHL Core v1 Teacher-Gated Session Resume And Commit Minimal v0

Status: Implemented
Runtime Impact: Explicit state-dir, teacher-gated, bounded persistence/resume/commit only
Default Persistence: None

## Purpose

Package 116 persists a Package 115 bounded embodied session that is stopped at
`WAITING_TEACHER_REVIEW`, reloads it across processes from an explicit SQLite
`state_dir`, applies an explicit teacher decision, and then follows the matching
teacher-gated path:

- `approved` resumes the same session, invokes the existing Package 90 to 92
  learning pipeline, creates reviewed interpretation, creates memory/readback
  records, and atomically commits active working readback for future sessions.
- `rejected` rolls the session back without creating reviewed interpretation or
  memory/readback commits.
- `deferred`, `needs_more_evidence`, and `conflict_detected` pause the session
  without commits.

The package does not create a teacher decision automatically. It does not resume
until an explicit teacher decision record exists.

## Store

The persistence store is `TeacherGatedSessionStore`, backed by SQLite at:

`<state_dir>/ashl_bounded_session_v1.sqlite3`

The caller must provide `state_dir`. Package 116 does not create
`ashl_core_v1/data` and does not persist by default from demo commands unless an
explicit state directory is requested.

The store records:

- session heads and checkpoints
- append-only TraceEnvelope rows
- pending teacher reviews
- explicit teacher decisions
- reviewed interpretation commits
- working readback commits
- session commit and rollback records
- session journal entries

## Approved Commit Boundary

Approved commit is atomic. Reviewed interpretation, working readback, commit
record, session checkpoint, and commit trace envelopes are committed together.
If the transaction fails, no partial interpreted commit remains and a failure
journal entry is appended.

The approved path invokes existing builders and validators from:

- Package 90 learning feedback teacher review and ConceptCandidate draft path
- Package 91 ConceptCandidate review/refinement path
- Package 92 ReviewedConcept and working readback integration path
- existing memory record schemas for MemoryLearningTrace, MemoryRoutingTrace,
  and MemoryApplicationData

## Raw Trace Boundary

Raw TraceEnvelope rows remain append-only.

Package 116 confirms:

- raw trace is not deleted
- raw trace is not rewritten
- raw trace is not summarized
- interpreted commits store reviewed interpretation plus `source_trace_refs`
- raw payload is not copied into working readback
- `concept_id` is not embedded into raw history

## Non-Goals

Package 116 does not create:

- automatic teacher decisions
- automatic learning approval
- unreviewed interpretation commits
- unrestricted long-term memory
- Core Memory writes
- real hardware access
- external control
- file operations outside the explicit state directory
- first_output
- live scheduler
- open-ended loop
- Thought Engine behavior
- GCMC runtime
- CL tokens

## CLI

Persistent commands require `--state-dir`.

Examples:

```powershell
py -3 -m ashl_core_v1.runtime.teacher_gated_session_resume_commit_cli persist-demo-waiting-session --state-dir .tmp/package116
py -3 -m ashl_core_v1.runtime.teacher_gated_session_resume_commit_cli list-sessions --state-dir .tmp/package116
py -3 -m ashl_core_v1.runtime.teacher_gated_session_resume_commit_cli decide --state-dir .tmp/package116 --session-id <session> --review-id <review> --decision approved --reason-code teacher_verified --teacher-note "Approved."
py -3 -m ashl_core_v1.runtime.teacher_gated_session_resume_commit_cli resume-and-commit --state-dir .tmp/package116 --session-id <session>
py -3 -m ashl_core_v1.runtime.teacher_gated_session_resume_commit_cli show-active-readback --state-dir .tmp/package116
```

Demo commands without `--state-dir` use temporary directories:

```powershell
py -3 -m ashl_core_v1.runtime.teacher_gated_session_resume_commit_cli run-demo-approved-commit
py -3 -m ashl_core_v1.runtime.teacher_gated_session_resume_commit_cli run-demo-rejected-rollback
py -3 -m ashl_core_v1.runtime.teacher_gated_session_resume_commit_cli run-demo-needs-more-evidence-pause
py -3 -m ashl_core_v1.runtime.teacher_gated_session_resume_commit_cli validate-demo-resume-commit
```

## Safe Claim

ASHL Core v1 can persist a bounded embodied session waiting at the teacher gate,
reload it across processes, apply an explicit teacher decision, resume approved
sessions through the existing learning pipeline, and atomically commit approved
reviewed interpretation plus `source_trace_refs` for future-session working
readback.

It still cannot run autonomously, approve learning by itself, operate real
sensors, control the computer, produce first_output, or run an open-ended live
scheduler.
