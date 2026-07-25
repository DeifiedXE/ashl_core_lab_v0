# ASHL Core Time Assumption Reconciliation v0.3

Status: Active decision record
Package: 124A
Runtime impact: Grounded temporal primitive foundation only

## Superseded Scope

This document supersedes only the time section of the earlier v0.2 time assumption.

The earlier v0.2 topics remain untouched and unimplemented here:

- curiosity satisfaction
- prediction error
- novelty score
- understanding satisfaction
- interest state
- interest tendency
- mimetic dopamine
- personality-weight adjustment

## Corrected Temporal Model

`action_tick` is an ordinal action counter.

`event_sequence_index` is an ordinal event counter.

Neither value is elapsed time.

Within a bounded active session, temporal structure is grounded in normalized event-time evidence from runtime records, sensor artifacts, perception primitives, alignment windows, internal actions, or other timestamped records.

Actions are one source of temporal events, not the sole source. Perception may provide temporal evidence without an action occurring.

While stopped or sleeping without active sensing, ASHL Core does not synthesize an internal experience timeline, invent idle ticks, or accumulate internal duration.

After resume, an external wall-clock gap may be discovered from persisted UTC anchors and clock-domain descriptors. That gap is not recorded as experienced duration.

## Boundary

Package 124A may derive ordering, spans, intervals, overlap, continuity and external gap records.

Package 124A does not create subjective time, waiting, impatience, rhythm semantics, deadlines, prediction timing, calendar concepts, or human clock understanding.

