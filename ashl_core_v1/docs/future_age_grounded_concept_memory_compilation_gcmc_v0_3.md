Status: Future AGE Architecture
Type: Docs-Only
Runtime Impact: None
Qingyin v1 Runtime: Not Implemented

# Future AGE Grounded Concept Memory Compilation / GCMC v0.3

This document is carried as future AGE architecture context only. Qingyin v1 does not implement GCMC runtime behavior.

Current Qingyin v1 boundary imported from this future architecture:

- Trace Spine format must stay unified across lines.
- Raw trace is append-only during service period and must not be summarized.
- Memory layer stores reviewed interpretation plus `source_trace_refs`, not raw trace, and must not embed `concept_id` into raw history.

Explicit non-implementation in Qingyin v1:

- No CL token is created.
- No Concept Compiler is created.
- No Pattern Miner is created.
- `formed_under_assumption` is not a current runtime rule because Qingyin v1 does not use CL tokens.
