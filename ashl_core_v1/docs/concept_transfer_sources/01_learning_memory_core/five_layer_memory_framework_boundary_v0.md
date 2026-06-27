# Five-Layer Memory Framework Boundary Minimal v0

## Purpose

This document turns the five-layer memory design assumption into an explicit implementation boundary map.

This is boundary/design only. It does not implement Archive Memory, Anchor Layer, five-layer memory runtime, autonomous memory routing, anchor lookup, endocrine-driven memory lookup, semantic/fuzzy/vector retrieval, action influence, behavior change, predictor mutation, or proof-of-learning claims.

## Five-Layer Map

Core Memory:
mentor/system-defined root identity, safety boundary, and root rules. This layer has the highest modification threshold.

Long-term Memory:
mentor-gated retained experience and long-term accepted decisions. Current v0 maps only to mentor-gated JSONL retention.

Working Memory:
current session/task context. It may change automatically during a session. It is not durable.

Archive Memory:
future compressed historical memory. Archive Memory is not implemented.

Anchor Layer:
future navigation/index layer. Anchor Layer stores navigation/index paths, not memory content. Anchor Layer is not implemented.

## Allowed Current Claims

- Core Seed assumptions exist as a prototype boundary for root identity/rule constraints.
- Mentor-gated JSONL retention exists for exact `mentor_text == "留"` retained records.
- Retained records can be loaded, read back, and listed read-only.
- Session working memory exists for current-session context.

## Forbidden Claims

- No Archive Memory runtime.
- No Anchor Layer runtime.
- No five-layer memory runtime.
- No automatic memory routing.
- No semantic/fuzzy/vector retrieval.
- No retained exact-key lookup runtime in this package.
- No retained experience into dry-run in this package.
- No memory-influenced behavior in this package.
- No lesson application.
- No runtime action selection or action behavior change.
- No predictor mutation.
- No endocrine-driven anchor lookup.
- No self-built specialty anchors.
- No proof-of-learning claim.

## Implementation Order

1. Keep Core / Working / Long-term stable.
2. Add read-only exact-key lookup over retained records.
3. Allow retained records into dry-run only.
4. Only after boundary review, allow first memory-influenced behavior.
5. Archive Memory later, when retained records become too many.
6. Anchor Layer last, after self-model / stable memory behavior exists.

## Boundary Before Exact-Key Lookup

Retained Experience Exact-Key Lookup Minimal v0 may only read retained JSONL records.
It must use exact_key only.
It must not do semantic, fuzzy, or vector retrieval.
It must not apply lessons.
It must not influence action selection.
It must not change behavior.

## Boundary Before Retained Experience Into Dry-Run

Retained Experience Into Dry-Run may use retained records as dry-run context only.
Dry-run use is not behavior change.
Dry-run use is not lesson application.
Dry-run use must remain traceable and reversible.

## Boundary Before Memory-Influenced Behavior

Any real behavior influence from retained memory requires a separate high-risk boundary review.
That review must define scope, rollback, mentor override, conflict handling, stale handling, and audit trace.
No behavior influence is allowed in this package.

## Future Archive Memory Boundary

Archive Memory is not implemented.
Archive Memory is for compressed older memory, not active decision-making.

Future Archive Memory compression must preserve at least:

- 文字片段
- 來源情境摘要
- 信心等級
- 使用次數

No Archive Memory write, lookup, compaction, restoration, or action influence exists now.

## Future Anchor Layer Boundary

Anchor Layer stores navigation/index paths, not memory content.
Core anchors may be mentor/system defined in future.
Specialty anchors are not allowed until Qingyin has a stable self-model.
No anchor runtime exists now.
No anchor lookup exists now.
No endocrine-driven anchor lookup exists now.
