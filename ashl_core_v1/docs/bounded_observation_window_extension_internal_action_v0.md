# Bounded Observation Window Extension Internal Action v0

Status: Completed by Package 125

## Capability

ASHL Core v1 can use grounded low-level temporal-tail evidence to create and
execute one bounded internal perception action that extends an already active
observation window. The screen, system-audio, and host-state capture lanes use
one shared deadline and remain in their original active capture sessions.

The action kind is `extend_observation_window`. It is authorized per runtime
and perception session, limited to one fixed extension, interruptible by an
operator stop, and blocked by capture or transport faults. Authorization does
not open a sensor and expires when the session ends.

Package 125 does not restart, reopen, replay, or redirect a source. Those
capabilities remain outside this package.

## Official Real Profile

- Base observation window: 5 seconds
- Tail guard: 750 milliseconds
- Single extension: 1.5 seconds
- Maximum extension count: 1
- Hard session duration: 7 seconds
- Applied final deadline: 6.5 seconds
- Required lanes: screen, system audio, host state

The real late-event run begins a visual and audio event near the base deadline.
The extension decision consumes only Package 120/121 capture evidence adapted
through Package 124A temporal sidecars. Stimulus schedule ground truth is
retained only for post-run audit and is not available to the runtime decision.

The final Package 122 session must flush all three lanes through the applied
deadline. A passing real audit requires the same source identities before and
after extension, an event closure after the original deadline, post-event
context, zero required-lane transport faults, and zero remaining flush records.

## Evidence Chain

The append-only Package 125 chain is:

1. Active observation-window state
2. Grounded temporal-tail evidence
3. Extension candidate
4. Session authorization and policy decision
5. Internal action and atomic deadline execution
6. Extended-window outcome
7. Before/after comparison
8. Package 112 score-equivalence record
9. Package 125 audit

Every link is scoped to the exact experiment run, audit group, runtime session,
perception session, observation window, and active source identities. Controls
are isolated by scenario and cannot satisfy the official real audit.

Raw Package 120 traces, Package 121 artifacts, Package 122 transport artifacts,
and Package 124A temporal evidence are append-only. Package 125 adds provenance
records; it does not rewrite source evidence.

## Controls

The verification suite includes early-complete, stable-baseline,
authorization-off, transport-fault, and operator-stop controls. None may
produce an applied extension outside the explicitly authorized late-event
case.

## Boundaries

Package 125 creates no sensor restart, repeat observation, focus selection,
semantic uncertainty, novelty, waiting or subjective-time semantics, Thought
Engine behavior, endocrine behavior, recognition, memory write, working
readback, teacher learning commit, output, external control, D-Laplace use,
LLM call, Codex call, or network call.

Package 112 scoring is executed through its authoritative scorer before and
after Package 125 provenance is attached. The score must remain equivalent.

## Safe Claim

ASHL Core v1 can keep the same active screen, system-audio, and host-state
capture sessions open for one bounded extension when actual low-level temporal
evidence remains open near the observation deadline. This can capture the
event's closure and additional context.

This does not mean that Qingyin understands the event, feels curiosity or
time, knows that she waited, selects visual attention, repeats or redirects
sensors, writes memory, produces output, or operates the host computer.

The next critical-path package is Package 126, Bounded Re-Sampling And
Listen-Again Internal Action. Reopening or replaying a bounded source belongs
there, not in Package 125.
