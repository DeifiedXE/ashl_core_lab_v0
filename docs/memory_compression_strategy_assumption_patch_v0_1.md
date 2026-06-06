# ASHL Core / Qingyin Memory Compression Strategy Assumption Patch v0.1

## Purpose

This document records the Phase 0 / Memory Economy assumption patch for memory compression strategy.

It is an assumption document only. It does not implement memory compression runtime, Memory Layer behavior, Symbol Grounding runtime, or lesson_store writes.

The purpose is to define the current safe boundary:

- text memory compression can be discussed as a text-stage assumption
- image memory compression remains deferred
- text / image relational compression remains deferred until Symbol Grounding v1
- ASHL Core must not treat the text-only strategy as a universal compression method

## Text-Stage Memory Compression Boundary

The current strategy is text-memory-stage-only.

It applies only to text-stage memory compression assumptions. It does not define runtime compression behavior.

The text memory compression unit is:

```text
text fragment
+ source context summary
+ confidence level
+ usage count
```

Text memory compression must preserve text fragment, source context summary, confidence level, and usage count.

Details may be compressed, shortened, or summarized in future designs, but provenance and confidence context must not be dropped. A compressed text memory that loses where it came from, how confident it is, or how often it has been used is not acceptable under this assumption.

## Applies To

This assumption applies to:

- text memory
- text fragment
- dialogue-derived memory
- document-derived memory
- textual lesson / note / assumption summary

This assumption does not apply to:

- image memory
- visual impression
- object concept memory
- multimodal symbol grounding memory

## Image Memory Compression Boundary

Image memory compression is not defined in this patch.

Image memory compression must not reuse the text-only compression strategy.

Image memory compression is deferred until visual sensory grounding exists. The system must not create an image memory compression schema, visual impression compression schema, object concept compression schema, or multimodal compression schema from the text-stage strategy alone.

The reason is simple: text can preserve a fragment and context summary, but image memory needs grounded visual evidence and object relations that do not yet exist in Phase 0 runtime.

## Text / Image Relational Compression Boundary

Text / image relational compression is not yet defined.

The future relational compression unit may need to connect:

- visual impression
- object identity / label
- textual explanation
- interaction history
- grounding evidence

This is not a text memory problem alone. It requires Symbol Grounding v1 or later.

Therefore, text / image relational compression is deferred until Symbol Grounding v1.

## Symbol Grounding v1 Boundary

Before Symbol Grounding v1:

```text
text memory compression = text-stage assumption only
image memory compression = undefined sensory-memory boundary
text / image relational compression = undefined cross-modal boundary
```

Symbol Grounding v1 is the earliest stage where cross-modal text / image memory compression can be designed responsibly.

## Non-Goals

This patch does not implement:

- memory compression runtime
- text memory compression runtime
- image memory compression runtime
- multimodal compression runtime
- Symbol Grounding runtime
- Memory Layer behavior changes
- Memory Economy runtime
- lesson_store writes
- Long-term Memory writes
- image memory compression schema
- visual impression compression schema
- object concept compression schema
- text / image relational compression schema

## Invariant

ASHL Core may document compression assumptions, but it must not silently convert them into runtime memory behavior.

The current invariant is:

```text
text-stage compression assumptions may be indexed;
image and multimodal compression remain deferred;
runtime Memory Layer behavior remains unchanged.
```
