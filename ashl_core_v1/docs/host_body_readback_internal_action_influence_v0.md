# Host Body Readback Internal Action Influence v0

Package 112 lets Host Body working readback visibility influence ordering among internal-only Host Body action choices:

- `observe_again`
- `mark_event_interesting`
- `mark_uncertain`
- `request_teacher_review`
- `shift_internal_focus`
- `update_home_status`
- `pause_event_processing`

The influence is deterministic, bounded, and record-only. It does not create Task Engine `selected_action`, `final_action`, direct commands, sandbox execution, external control, memory writes, learning candidates, teacher approval, `first_output`, or live runtime sessions.

Trace Spine boundaries remain enforced: raw trace is append-only, raw trace is not summarized, memory/readback carries interpretation plus `source_trace_refs`, and `concept_id` is not embedded into raw history.
