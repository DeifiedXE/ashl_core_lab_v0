# Mentor-Gated Experience Retention Boundary v0

## Purpose

This is the first true retention boundary for `session_experience_record`.

Retention v0 writes a minimal durable append-only JSONL record only after explicit mentor approval.

## Mentor Gate

The only v0 approval phrase is `留`.

No automatic retention exists.

Any mentor text other than exact `留` must block retention.

## Retention Target

Retention writes durable append-only JSONL.

Retained experience is a minimal durable record that can be read back.

Retained experience is not four-layer memory.

Retained experience is not proof of learning.

## Runtime Boundary

Retained experience must not influence action selection in v0.

Retained experience must not modify action behavior in v0.

Retained experience must not mutate predictors in v0.

Retention v0 does not add semantic, fuzzy, or vector retrieval.

Retention v0 does not apply lessons.

## Rollback v0

Rollback v0 is manual removal or archival of the appended JSONL line.

No destructive automatic deletion is implemented.

Every retained record must include enough IDs to locate and remove it manually.
