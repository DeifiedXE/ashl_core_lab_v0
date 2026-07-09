# Trace Spine Raw Evidence Boundary v1

Qingyin v1 treats Trace Spine cleanliness as a hard boundary.

Required current rules:

- `trace_spine_format_unified = true`
- `trace_spine_time_aligned = true`
- `raw_trace_append_only_confirmed = true`
- `raw_trace_summarized_during_service_period = false`
- `memory_layer_stores_interpretation_only = true`
- `source_trace_refs_preserved = true`
- `concept_id_embedded_into_raw_history = false`
- `raw_trace_dumped_into_memory_learning_trace = false`

The memory/readback path may carry reviewed interpretation and source references. It must not carry raw trace payloads, mutate raw history, summarize raw trace during the service period, or embed concept IDs into raw Host Body trace history.

GCMC v0.3 remains future AGE architecture only. Qingyin v1 does not create CL tokens, a Concept Compiler, a Pattern Miner, or a GCMC runtime.
