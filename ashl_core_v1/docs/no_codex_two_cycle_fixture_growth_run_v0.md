# Package 118 / No-Codex Two-Cycle Fixture Growth Run v0

Status: Implemented
Runtime Scope: Fixture-only, teacher-gated, bounded two-cycle run
External Control: Not Created
First Output: Not Created
Live Scheduler: Not Created

Package 118 proves one real cross-process fixture growth flow:

Cycle 1:
Host Body fixture event -> bounded embodied session runtime -> WAITING_TEACHER_REVIEW -> exact teacher approval -> Package 90-92 learning path -> reviewed interpretation commit -> active working readback commit -> process exit.

Cycle 2:
new process -> new runtime instance -> new store connection -> new session -> load Cycle 1 active working readback before event handling -> inject matching fixture -> evaluate readback through the existing Host Body readback influence path -> apply bounded candidate score deltas -> produce normal internal action ordering and choice -> stop at the next teacher gate.

The run is no-Codex at runtime. Worker processes install a runtime guard that blocks model client imports, socket creation, network requests through sockets, arbitrary subprocesses, eval, and exec. The parent orchestrator may launch exactly the fixed Package 118 worker module with `shell=False` as developer test orchestration only.

The package does not create automatic approval, unrestricted memory promotion, real camera or microphone access, external control, Task Engine external action, first_output, live scheduler, open-ended loop, GCMC runtime, CL token, or any consciousness claim.

Primary CLI:

```powershell
py -3 -m ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_cli run-two-cycle-demo `
  --teacher-decision approved `
  --approval-scope through_reviewed_concept_and_working_readback `
  --teacher-approval-text "I approve this exact reviewed evidence for interpretation and working readback." `
  --reason-code teacher_verified_exact_evidence
```

The success condition is not that readback merely exists in SQLite. Cycle 2 must record that committed readback was loaded before event handling, evaluated against the current fixture context, matched a rule, entered candidate scoring, applied at least one nonzero bounded delta, and retained provenance back to the Cycle 1 working readback commit and evidence identity.
