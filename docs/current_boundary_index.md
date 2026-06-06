Boundary Index Version: 2026-06-06-b17
Last update log: Batch 17
Current clean count: 0/5

## Global Hard Boundaries

- trace is evidence, not approval
- trace is record, not authorization
- trace is audit material, not runtime action
- no lesson_store write unless explicitly authorized by a future dedicated package
- no Memory Layer write unless explicitly authorized by a future dedicated package
- no Long-term Memory write unless explicitly authorized
- LLM output must not become authoritative failure_reason
- no expected_outcome / actual_outcome contrast, no authoritative failure_reason
- formal lesson_candidate creation is not lesson approval
- formal lesson_candidate creation is not activation
- formal lesson_candidate creation does not grant selection eligibility
- ASHL Core provides evidence; Qingyin Memory Layers decide memory admission
- semantic_key is non-authoritative and review-required
- builder output must be review-gated
- sandbox result is not a lesson
- sandbox trace is not memory promotion
- sandbox repair suggestion is not executable action

## Currently Deferred Areas

- sandbox runtime
- Audio Sense / STT / TTS / voice trigger / voice input-output loop
- bidirectional voice interaction
- formal lesson_candidate creation runtime
- automatic lesson_candidate builder
- evaluator runtime
- review decision runtime
- selection eligibility runtime
- activation runtime
- Memory Economy runtime
- soft / hard consolidation runtime
- Core Seed update runtime
- self-modification runtime

## Update Rule

This file must be updated every time an Update Log is generated.
Updating this file is a required condition for completing the Update Log package.
No Update Log package is complete without a corresponding update to this file.
