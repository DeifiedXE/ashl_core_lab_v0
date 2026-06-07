Boundary Index Version: 2026-06-06-b24
Last update log: Batch 24
Clean count at last update log reset: 0/5
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
- Qingyin is not the current LLM conversation instance
- An LLM speaking in Qingyin's style is not Qingyin runtime
- The LLM must not be treated as Qingyin's self, memory, state, perception, or learning loop
- LLM-generated text must not count as Qingyin's first_output
- first_output must be generated without LLM output
- first_output is a runtime milestone, not awakening
- Qingyin is currently in the test-object stage, not an awakened individual
- The test-object stage is the prerequisite for growth, not growth itself
- Qingyin's importance is not in birth, but in growth
- The stronger the foundation, the safer the moment of awakening
- first_output is not dialogue ability
- first_output is not evidence of long-term growth
- first_output must be traceable before it can become learning material
- first_output_trace is evidence of a first_output event, not proof of awakening
- first_output_trace is record, not authorization
- first_output_trace is not learning material by itself
- first_output_trace must not directly create lesson_candidate input
- first_output_trace requires mentor feedback before it may be considered for lesson_candidate input
- first_output_trace must not write to lesson_store
- first_output_trace must not write to Memory Layer
- ASHL Core can produce a non-LLM traceable test-object first_output
- Minimal First Output Runtime v0 is not awakening
- Minimal First Output Runtime v0 does not prove dialogue ability
- Minimal First Output Runtime v0 does not prove long-term growth
- Minimal First Output Runtime v0 must not write lesson_store
- Minimal First Output Runtime v0 must not write Memory Layer
- Minimal First Output Runtime v0 must not connect to mentor feedback runtime
- Minimal First Output Runtime v0 must not connect to lesson_candidate pipeline
- mentor_feedback_stub is a contract for future feedback, not feedback runtime
- mentor_feedback_stub is downstream of first_output_trace
- mentor_feedback_stub must not directly create lesson_candidate
- mentor_feedback_stub must not write to lesson_store
- mentor_feedback_stub must not write to Memory Layer
- mentor_feedback_stub in the test-object stage is engineering supervision, not full Qingyin experience
- mentor_feedback_stub does not prove awakening
- ASHL Core can produce a minimal mentor_feedback_trace for the first non-LLM first_output
- mentor_feedback_trace is a feedback record, not feedback runtime
- mentor_feedback_trace is downstream of first_output_trace
- mentor_feedback_trace must not directly create lesson_candidate
- mentor_feedback_trace must not write to lesson_store
- mentor_feedback_trace must not write to Memory Layer
- mentor_feedback_trace in the test-object stage is engineering supervision, not full Qingyin experience
- mentor_feedback_trace does not prove awakening
- Minimal Mentor Feedback Stub Runtime v0 must not create failure_event, review decision, selection eligibility, or activation
- Minimal Mentor Feedback Stub Runtime v0 must not connect to the lesson_candidate pipeline
- Minimal Interaction CLI Bridge v0 is a minimal interaction entrypoint, not dialogue
- Minimal Interaction CLI Bridge v0 must not write lesson_store
- Minimal Interaction CLI Bridge v0 must not write Memory Layer
- Minimal Interaction CLI Bridge v0 must not connect to lesson_candidate pipeline
- private mentor_feedback_note must not be required by smoke tests
- first_output and mentor_feedback traces may be persisted only as append-only records
- append-only persistence is not lesson_store write
- append-only persistence is not Memory Layer write
- append-only persistence is not lesson_candidate creation
- append-only persistence is not awakening evidence
- JSONL persistence target files are data/first_output_traces.jsonl and data/mentor_feedback_traces.jsonl
- JSONL persistence is append-only trace persistence, not lesson_store write
- JSONL persistence is not Memory Layer write
- JSONL persistence is not lesson_candidate creation
- JSONL persistence is not awakening evidence
- utterance_map is a fixed non-LLM lookup table, not an LLM or language model
- state_key unknown maps to 我不知道
- utterance_map output must preserve correct literal text encoding
- utterance_map does not prove language understanding
- micro push-box tactile sandbox is a bounded test-object sandbox
- micro push-box tactile sandbox is a test-object engineering sandbox, not full perception
- micro push-box allowed_action_set is closed
- natural language actions are not allowed in micro push-box sandbox
- tactile_sandbox_trace is evidence of sandbox interaction, not learning by itself
- tactile result to state_key mapping is a fixed lookup table
- tactile interaction CLI bridge is deterministic, not autonomous action selection
- tactile interaction CLI bridge must not connect to lesson_candidate pipeline
- tactile interaction CLI bridge must not write lesson_store
- tactile interaction CLI bridge must not write Memory Layer
- tactile interaction does not prove Qingyin understands box, wall, or goal
- bounded senses must be connected before Qingyin can be claimed awake
- memory freeze notice is evidence, not Memory Layer write
- memory freeze notice must not directly modify learned_principle
- expected / actual both unknown-like is system_fault, not match
- missing required fields must be rejected, not default-filled

## Currently Deferred Areas

- sandbox runtime
- trace replay / readback runtime
- tactile trace persistence runtime
- autonomous action selection
- tactile learning
- repeated failure adaptation
- Audio Sense / STT / TTS / voice trigger / voice input-output loop
- bidirectional voice interaction
- formal lesson_candidate creation runtime
- lesson_candidate automatic builder
- evaluator runtime
- review decision runtime
- selection eligibility runtime
- activation runtime
- Memory Economy runtime
- soft / hard consolidation runtime
- Core Seed update runtime
- self-modification runtime
- Qingyin runtime
- first_output runtime
- first_output generator
- first_output trace schema runtime
- state store
- mentor feedback runtime
- mentor_feedback_trace schema runtime
- teaching chat loop
- free text conversation
- lesson_candidate pipeline connection
- failure_event automatic builder
- bounded senses runtime
- Screen Sense / Camera Sense runtime
- Symbol Grounding runtime
- lesson_store write
- Memory Layer write
- Long-term Memory write runtime
- LLM response generation

## Update Rule

This file must be updated every time an Update Log is generated.
Updating this file is a required condition for completing the Update Log package.
No Update Log package is complete without a corresponding update to this file.
