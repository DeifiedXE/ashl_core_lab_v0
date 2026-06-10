# Five-Layer Memory Design Assumption v0.1

## Purpose

This document records the future ASHL Core / Qingyin five-layer memory architecture as a design assumption.

It is design-only. It does not implement Archive Memory, Anchor Layer, four-layer memory runtime, five-layer memory runtime, autonomous memory routing, endocrine-driven memory lookup, action influence, lesson application, predictor mutation, or proof-of-learning claims.

## Version

- Document: Five-Layer Memory Design Assumption v0.1
- Status: design assumption only
- Current Boundary Index remains unchanged by this document.

## Five-Layer Architecture

The future memory architecture has five layers:

1. Core Memory
2. Long-term Memory
3. Working Memory
4. Archive Memory
5. Anchor Layer

## Core Memory

Core Memory is the highest-stability identity and value layer.

Core Memory is mentor-defined and cannot be self-modified by Qingyin.

Core Memory is not a place for ordinary experience records, trial traces, or temporary observations.

Current implementation status:

- Core Seed exists as a prototype / assumption line.
- Core Memory runtime is not implemented as a complete memory layer.
- Qingyin self-modification of Core Memory is not allowed.

## Long-term Memory

Long-term Memory stores retained experience that has passed a review gate / mentor review.

In current Minimal v0 implementation, Long-term Memory maps only to mentor-gated JSONL retention:

```text
session_experience_record
+ exact mentor_text == "留"
-> append-only JSONL
-> load retained record
-> readback preview
-> read-only listing
```

This is a minimal prototype, not a complete Long-term Memory system.

Current implementation status:

- mentor-gated JSONL retention exists as a minimal prototype.
- Retained records can be appended, loaded back, previewed read-only, and listed read-only.
- Automatic retention is not implemented.
- Semantic / fuzzy / vector retrieval is not implemented.
- Action influence from retained records is not implemented.

## Working Memory

Working Memory is session-local.

Working Memory may help hold current session context, local trace state, and short-lived handoff data.

Working Memory clears after session.

Current implementation status:

- session working memory exists.
- temporary cross-session experience space is demo / fixture handoff only and is not durable memory.

## Archive Memory

Archive Memory is compressed historical memory.

Archive Memory is for future archival compression, not immediate action selection.

Archive Memory is not implemented yet.

Archive Memory compression must preserve these minimum fields:

- 文字片段
- 來源情境摘要
- 信心等級
- 使用次數

Current implementation status:

- Archive Memory: not implemented
- No archive compression runtime exists.
- No Archive Memory write, lookup, compaction, or restoration is implemented.

## Anchor Layer

Anchor Layer is a navigation index.

Anchor Layer does not store memory content.

Anchor Layer stores navigation/index paths that may help future systems find relevant memory locations.

Anchor Layer is not implemented.

Core anchors come from Core Memory and are mentor-defined.

Specialty anchors are future self-built anchors.

Specialty anchors are not open until Qingyin can recognize herself.

Current implementation status:

- Anchor Layer: not implemented
- No anchor runtime exists.
- No anchor lookup exists.
- No specialty anchors exist.
- No self-built anchors exist.

## Anchor Layer Role

The Anchor Layer is not an additional content memory store.

Its role is to help future memory systems navigate across Core Memory, Long-term Memory, Working Memory, and Archive Memory without copying their content into the anchor.

The Anchor Layer must preserve a strict boundary:

```text
Anchor Layer = navigation/index path
Memory layers = content
```

## Relationship To Mimetic Endocrine System

The design relation is:

```text
mimetic endocrine system = compass
Anchor Layer = map
```

Directional assumptions:

- dopamine-like: query reward-related anchors
- norepinephrine-like: query change-related anchors
- cortisol-like: move away from failure-accumulated anchors
- oxytocin-like: query trusted-source anchors

No endocrine-driven anchor lookup is implemented in this package.

No endocrine-controlled memory routing is implemented.

No endocrine-controlled action selection is implemented.

## Current Implementation Status

Current implemented / prototype lines:

- Core Memory: Core Seed exists as a prototype / assumption line.
- Long-term Memory: mentor-gated JSONL retention exists as a minimal prototype.
- Working Memory: session working memory exists.
- Archive Memory: not implemented.
- Anchor Layer: not implemented.

The current system can only claim:

- mentor-gated durable retention Minimal v0 exists.
- retained JSONL records can be loaded back.
- retained JSONL records can be shown in read-only preview.
- retained JSONL records can be listed read-only.

## Not-Allowed Claims

Do not claim 五層記憶系統已完整實作.

Do not claim Archive Memory exists.

Do not claim Anchor Layer exists.

Do not claim specialty anchors exist.

Do not claim endocrine-driven anchor lookup exists.

Do not claim automatic retention exists.

Do not claim semantic / fuzzy / vector retrieval exists.

Do not claim retained records apply lessons.

Do not claim retained records influence action selection.

Do not claim retained records change behavior.

Do not claim retained records mutate predictors.

Do not claim proof of learning from this design document.
