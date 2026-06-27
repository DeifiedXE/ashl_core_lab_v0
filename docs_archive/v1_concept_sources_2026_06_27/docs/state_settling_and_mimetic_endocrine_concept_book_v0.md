# State Settling and Mimetic Endocrine Concept Book v0

Status: Concept / Docs-Only
Runtime Impact: None
Boundary Index Impact: None

## Purpose

This note separates two ideas that can otherwise get mixed together:

```text
action rollback
state settling
```

Action rollback means undoing or discarding an action effect.
State settling means reducing temporary internal pressure after an event while
keeping the event trace intact.

For Qingyin, the safer concept is usually state settling.
The log remains observable.
Only temporary pressure, salience, or weighting is allowed to settle in future
designs.

## Core Model

An event may perturb a mimetic endocrine state:

```text
event
-> four-axis endocrine trace
-> temporary perturbation
-> post-event settling strategy
-> trace evidence only
```

The current repo does not implement a runtime endocrine state.
This document defines vocabulary for future bounded designs.

## Four Axes

```text
dopamine_like:
  approach / reward / satisfaction signal.
  Future settling role: reward signal decays toward baseline.

norepinephrine_like:
  salience / uncertainty / change signal.
  Future settling role: attention interrupt settles after mismatch resolution.

cortisol_like:
  pressure / failure load / conflict burden signal.
  Future settling role: pressure decays, or a safety reset is requested for unsafe spikes.

oxytocin_like:
  explicit-source trust / review safety / comfort signal.
  Future settling role: comfort-modulated settling can reduce pressure load.
```

These names are functional metaphors.
They are not biological hormone simulation.
They are not proof of emotion or consciousness.

## Natural Settling

Natural settling is the ordinary return toward baseline.

Example:

```text
minor mismatch
-> norepinephrine_like rises as salience annotation
-> mismatch resolves
-> future design may decay salience toward baseline
```

Natural settling does not erase the event.
It does not write memory.
It does not change action behavior.

## Comfort-Modulated Settling

Comfort-modulated settling is the external-support path.

Example:

```text
failure pressure rises
-> explicit mentor comfort / safe review appears
-> oxytocin_like trace marks trusted support
-> future design may reduce cortisol_like pressure faster
```

Comfort is not approval.
Trusted review does not override a review gate.
No action, memory, or predictor change is authorized by comfort alone.

## Safety Reset

Safety reset is the hard interruption path.

It is similar to the user's "sedative" metaphor, but only as a bounded design
metaphor:

```text
unsafe temporary spike
-> forced reset request
-> temporary state cleared or neutralized in future design
-> trace remains
```

This is not medical sedation.
This is not consciousness control.
This is not deleting evidence.
It is a future safety mechanism for temporary state only.

## Evidence For Review

Large events may leave review evidence:

```text
important success / failure / mismatch
-> trace evidence
-> human review candidate
```

Evidence is not memory.
Evidence is not learning.
Evidence is not behavior change.

## Boundary Rules

```text
state settling != action rollback
natural settling != memory write
comfort settling != approval
safety reset != medical sedation
trace evidence != lesson application
pressure reduction != proof of learning
endocrine metaphor != subjective emotion claim
```

## Current Repo Status

The current repo has:

```text
mimetic endocrine signal schema
dopamine_like trace checker
norepinephrine_like trace checker
cortisol_like trace checker
oxytocin_like trace checker
four-axis trace integration checker
```

The current repo does not have:

```text
runtime endocrine state
runtime settling formula
runtime safety reset
endocrine-driven action selection
endocrine memory write
predictor mutation
persistent mood
personality drift
subjective emotion proof
```

## Summary

State settling is the future mechanism for letting Qingyin return toward a
bounded internal baseline after an event.

Natural settling handles ordinary decay.
Comfort-modulated settling handles external support.
Safety reset handles unsafe temporary spikes.

All three remain design concepts until a later package explicitly adds runtime
behavior under a separate boundary review.
