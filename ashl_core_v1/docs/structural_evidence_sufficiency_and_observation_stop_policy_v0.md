# Structural Evidence Sufficiency And Observation Stop Policy Minimal v0

Status: Completed by Package 128

## Capability

Package 128 adds one internal perception-lifecycle action:
`stop_observation`.

An explicitly authorized, active Package 127 focused visual child is inspected
at bounded checkpoints. The only public v0 contract is
`focused_visual_event_closure_with_post_context`. It requires screen and
host-state source coverage, at least one focused low-level visual region,
closure of every observed region, no open visual region, 500 ms of event-time
post-context, at least three complete Package 122 alignment windows, one second
minimum elapsed time, full-frame preservation, matching lineage, and zero
transport or compiler faults.

The contract is structural. It contains no semantic goal, expected object,
expected label, confidence score, uncertainty score, weighted score, memory
input, endocrine input, or Thought Engine input.

## Active Stop Path

Package 128 uses the existing Package 125
`BoundedCaptureDeadlineController.request_stop` latch. It does not create a
second stop controller. Package 122 provides a read-only active alignment view;
the final child still uses the existing live transport finalization and
Package 123 flush barrier. Visual onset and closure remain actual Package 121
evidence and Package 124A anchors/spans.

Precedence is fixed:

1. operator stop;
2. transport, capture, or compiler failure;
3. hard deadline;
4. authorized structural sufficiency stop;
5. continue the current window.

An insufficient checkpoint returns `continue_current_window`. It does not
extend, reacquire, listen again, refocus, or open another sensor. At the hard
deadline, unmet criteria become `inconclusive_at_hard_deadline`.

## Real Evidence

The official experiment is
`host_internal_focused_visual_structural_sufficiency_stop_v0`.

It first creates a real Package 127 changed-grid focus from a clean screen and
host-state parent, then opens one Package 126 full-frame child with a
3,000,000,000 ns hard deadline. The external fixture produces one low-level
visual onset and offset in the selected region. Runtime checkpoints use only
captured artifacts and compiled primitives. The fixture manifest is read only
after the result is frozen.

The passing run proves:

- actual full-frame and focused-region evidence;
- an observed region, Package 124A closure span, and at least 500 ms stable
  post-event coverage;
- at least three complete alignment windows;
- exactly one `stop_observation` action;
- a shared stop across screen and host-state lanes before the hard deadline;
- no source reopen, alignment-origin change, or focus-context change before
  completion;
- final transport flush and automatic focus release;
- zero required-lane drops, backpressure faults, capture failures, compile
  failures, and flush remainder.

## Boundaries

Package 128 changes no Package 112 score. Its stop policy creates no memory
record, working readback, extension action, additional reacquisition action,
additional focus-shift action, novelty, uncertainty, Thought Engine use,
endocrine signal, output, external control, semantic understanding,
recognition, certainty, or subjective-time claim. The prerequisite Package 126
child action and Package 127 focus action remain separately attributed records.

Package 129 is next. Packages 130 and 131 remain auditory capability work, and
Package 132 closes the perception capability construction line. After Package
132, DLM-1 remains a separate organ-growth infrastructure lane and Package 133
begins persistent self-state. No Package 132A or additional perception package
is scheduled.
