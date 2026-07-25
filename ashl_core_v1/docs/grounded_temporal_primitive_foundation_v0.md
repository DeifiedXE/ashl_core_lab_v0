# Grounded Temporal Primitive Foundation v0

Package: 124A
Status: Implemented
Runtime impact: Temporal primitive compilation only

## Purpose

Package 124A derives deterministic temporal anchors, spans, intervals, relations, continuity records, repeated occurrence structure and cross-process external gaps from actual Package 123/124 runtime evidence.

The compiler reads the certified Package 124 milestone archive in read-only mode and writes derived temporal records to a separate Package 124A store:

`package_124a_temporal_foundation_v0/package_124a_temporal.sqlite3`

## Authority

Within one process, event-time arithmetic uses normalized monotonic event times already present in Package 120-123 records.

Across processes, the compiler does not subtract monotonic values. It uses persisted UTC anchors plus clock-domain descriptors and recorded uncertainty.

Stimulus schedule data is audit-only. It is loaded only after primitive compilation for calibration and never enters primitive identity or provenance.

## Package 123 Evidence

The certified Cycle 1 evidence contains:

- 24 complete alignment windows
- 8 visual low-level change windows
- 4 audio-energy windows
- 4 visual/audio overlap windows
- 0 required-lane drops
- 0 required-lane capture or compile failures

Stable visual data and silent audio count as source coverage. Lack of salience is not a temporal gap.

## Sidecar Boundary

Temporal context sidecars are read-only:

- no scoring authority
- no memory-write authority
- no action-selection authority
- no output authority

They are prepared for future active-perception packages and do not alter Package 112 scoring or Package 115 session handling.

## Forbidden Claims

Package 124A does not claim that Qingyin feels time, knows waiting, understands rhythm, understands duration, knows clock time, or experienced time while stopped or sleeping.

