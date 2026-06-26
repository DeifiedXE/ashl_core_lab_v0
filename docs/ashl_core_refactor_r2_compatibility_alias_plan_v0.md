# ASHL Core Refactor R2 Compatibility Alias Plan v0

Status: R2 compatibility alias plan / docs and checker target.
Runtime impact: none.
Boundary impact: planning validation boundary only.

## R2 Summary

R2 prepares compatibility aliases before any file movement.
No files are moved in this package.
No imports are changed in this package.

Plain version:

ASHL Core can later grow new line folders, but the old module doors must stay open first. This package plans the compatibility route so future file movement does not break existing imports, tests, smoke checks, or user-facing CLI behavior.

## Target Package Layout

Future target layout:

```text
ashl_core/
  spine/
  body/
  thought/
  memory/
  perception/
  bridge/
  endocrine/
  voice/
  lesson/
  governance/
```

The target layout is a plan only. This package does not create these folders as runtime homes, does not move files into them, and does not change imports to point at them.

## Compatibility Strategy

Future refactor work should preserve this sequence:

```text
old_module_path remains importable
new_module_path becomes canonical
old path re-exports from new path
tests first validate both paths
old path deprecation happens only after compatibility passes
```

Plain version:

New homes can be created, but old addresses stay valid until compatibility tests prove both old and new paths behave the same.

## Alias Candidate Table

| old_module_path | future_new_module_path | line | alias_strategy | risk_level | move_allowed_now |
| --- | --- | --- | --- | --- | --- |
| `ashl_core/phase1_runtime_session_trace_spine_minimal.py` | `ashl_core/spine/session_trace_spine.py` | `spine` | re-export old path from new module in future R4 | medium | false |
| `ashl_core/phase1_session_frame_materialization_minimal.py` | `ashl_core/spine/session_frame.py` | `spine` | re-export old path from new module in future R4 | medium | false |
| `ashl_core/phase1_session_frame_runtime_tick_handoff_minimal.py` | `ashl_core/spine/session_frame_tick_handoff.py` | `spine` | re-export old path from new module in future R4 | medium | false |
| `ashl_core/sandbox_candidate_ordering_arbitration_selected_action_minimal.py` | `ashl_core/body/selected_action.py` | `action_body_motor` | re-export old path from new module in future R4 | medium | false |
| `ashl_core/sandbox_candidate_ordering_arbitration_final_action_minimal.py` | `ashl_core/body/final_action.py` | `action_body_motor` | re-export old path from new module in future R4 | medium | false |
| `ashl_core/sandbox_candidate_ordering_arbitration_direct_command_minimal.py` | `ashl_core/body/direct_command.py` | `action_body_motor` | re-export old path from new module in future R4 | high | false |
| `ashl_core/sandbox_candidate_ordering_arbitration_direct_command_execution_minimal.py` | `ashl_core/body/direct_command_execution.py` | `action_body_motor` | re-export old path from new module in future R4 | high | false |
| `ashl_core/experience_derived_proto_purpose_candidate_trace_minimal.py` | `ashl_core/thought/proto_purpose_candidate_trace.py` | `thought_purpose` | re-export old path from new module in future R4 | medium | false |
| `ashl_core/proto_purpose_approval_boundary_minimal.py` | `ashl_core/thought/proto_purpose_approval_boundary.py` | `thought_purpose` | re-export old path from new module in future R4 | medium | false |
| `ashl_core/thought_memory_action_parallel_mini_loop_minimal.py` | `ashl_core/thought/three_line_mini_loop.py` | `thought_purpose` | re-export old path from new module in future R4 | high | false |
| `ashl_core/session_working_memory.py` | `ashl_core/memory/session_working_memory.py` | `memory_retention_influence` | re-export old path from new module in future R4 | medium | false |
| `ashl_core/memory_write_and_read_minimal.py` | `ashl_core/memory/write_read.py` | `memory_retention_influence` | re-export old path from new module in future R4 | high | false |
| `ashl_core/mentor_gated_experience_retention_minimal.py` | `ashl_core/memory/mentor_gated_retention.py` | `memory_retention_influence` | re-export old path from new module in future R4 | high | false |
| `ashl_core/visual_spatial_grounding_minimal.py` | `ashl_core/perception/visual_spatial_grounding.py` | `vision_eye_focus` | re-export old path from new module in future R4 | low | false |
| `ashl_core/focus_candidate_schema.py` | `ashl_core/perception/focus_candidate_schema.py` | `vision_eye_focus` | re-export old path from new module in future R4 | low | false |
| `ashl_core/focus_candidate_from_change_trace.py` | `ashl_core/perception/focus_candidate_from_change_trace.py` | `vision_eye_focus` | re-export old path from new module in future R4 | medium | false |
| `ashl_core/qingyin_bridge_grounded_capability_map_minimal.py` | `ashl_core/bridge/grounded_capability_map.py` | `qingyin_bridge_capability` | re-export old path from new module in future R4 | medium | false |
| `ashl_core/visual_spatial_motor_affordance_bridge_minimal.py` | `ashl_core/bridge/visual_spatial_motor_affordance.py` | `qingyin_bridge_capability` | re-export old path from new module in future R4 | medium | false |
| `ashl_core/phase2_perception_capability_evidence_source_link_minimal.py` | `ashl_core/bridge/phase2_evidence_source_link.py` | `qingyin_bridge_capability` | re-export old path from new module in future R4 | medium | false |
| `ashl_core/mimetic_endocrine_signal_schema.py` | `ashl_core/endocrine/signal_schema.py` | `mimetic_endocrine_settling` | re-export old path from new module in future R4 | medium | false |
| `ashl_core/mimetic_endocrine_four_axis_trace_integration.py` | `ashl_core/endocrine/four_axis_trace_integration.py` | `mimetic_endocrine_settling` | re-export old path from new module in future R4 | medium | false |
| `ashl_core/mimetic_endocrine_post_event_settling_design_minimal.py` | `ashl_core/endocrine/post_event_settling_design.py` | `mimetic_endocrine_settling` | re-export old path from new module in future R4 | low | false |
| `ashl_core/minimal_first_output_runtime.py` | `ashl_core/voice/first_output_runtime.py` | `voice_audio_first_output` | re-export old path from new module in future R4 | high | false |
| `ashl_core/minimal_non_llm_utterance_map.py` | `ashl_core/voice/non_llm_utterance_map.py` | `voice_audio_first_output` | re-export old path from new module in future R4 | medium | false |
| `ashl_core/minimal_mentor_feedback_stub_runtime.py` | `ashl_core/voice/mentor_feedback_stub.py` | `voice_audio_first_output` | re-export old path from new module in future R4 | medium | false |
| `ashl_core/failure_event_schema_foundation.py` | `ashl_core/lesson/failure_event_schema.py` | `lesson_review_evidence` | re-export old path from new module in future R4 | medium | false |
| `ashl_core/lesson_candidate_review_evidence_summary.py` | `ashl_core/lesson/review_evidence_summary.py` | `lesson_review_evidence` | re-export old path from new module in future R4 | medium | false |
| `ashl_core/reviewed_lesson_trace_preview.py` | `ashl_core/lesson/reviewed_lesson_trace_preview.py` | `lesson_review_evidence` | re-export old path from new module in future R4 | medium | false |
| `ashl_core/phase2_to_phase10_completed_capability_cross_check_minimal.py` | `ashl_core/governance/phase2_to_phase10_capability_cross_check.py` | `governance_audit_documentation` | re-export old path from new module in future R4 | medium | false |
| `ashl_core/structural_refactor_map_minimal.py` | `ashl_core/governance/structural_refactor_map.py` | `governance_audit_documentation` | re-export old path from new module in future R4 | low | false |
| `ashl_core/teaching_cli.py` | `ashl_core/governance/teaching_cli.py` | `governance_audit_documentation` | no move until CLI boundary plan exists | high | false |

## First Alias Candidates

Spine candidates:

- `ashl_core/phase1_runtime_session_trace_spine_minimal.py` -> `ashl_core/spine/session_trace_spine.py`
- `ashl_core/phase1_session_frame_materialization_minimal.py` -> `ashl_core/spine/session_frame.py`
- `ashl_core/phase1_session_frame_runtime_tick_handoff_minimal.py` -> `ashl_core/spine/session_frame_tick_handoff.py`

Nine structural line candidates:

- `action_body_motor`: selected_action, final_action, direct_command, direct_command_execution
- `thought_purpose`: proto-purpose candidate, proto-purpose approval, thought-memory-action mini-loop
- `memory_retention_influence`: session working memory, memory write-read, mentor-gated retention
- `vision_eye_focus`: visual-spatial grounding, focus candidate schema, focus candidate from change trace
- `qingyin_bridge_capability`: grounded capability map, visual-spatial motor affordance bridge, Phase2 source link
- `mimetic_endocrine_settling`: endocrine signal schema, four-axis trace integration, post-event settling design
- `voice_audio_first_output`: first_output runtime, non-LLM utterance map, mentor feedback stub
- `lesson_review_evidence`: failure event schema, reviewed lesson evidence summary, reviewed lesson trace preview
- `governance_audit_documentation`: Phase2-to-Phase10 cross-check, structural refactor map checker, teaching CLI

## Import Compatibility Test Plan

Future R4 move packages must prove:

```text
old import still works
new import works
old and new expose same public function names
old and new output same deterministic sample record
all existing tests still pass
smoke still passes
```

This package only writes the test plan. It does not implement aliases, does not import from new paths, and does not change existing import statements.

## Refactor Phase Gate

Required sequence:

```text
R1 structural map completed
R2 compatibility alias plan
R3 low-risk docs folder plan
R4 first small module move with compatibility shim
R5 duplicate gate family consolidation plan
R6 import/test update
R7 old-path deprecation only after compatibility passes
```

## R2 Non-Movement Rule

R2 must not move files.
R2 must not rename modules.
R2 must not change imports.
R2 must not merge modules.
R2 must not delete old paths.

Additional non-goals:

- No runtime behavior change.
- No candidate input.
- No candidate ordering.
- No selected_action.
- No final_action.
- No direct command.
- No execution.
- No outcome observation.
- No memory write.
- No retention write.
- No predictor use or mutation.
- No endocrine feed.
- No tendency feed.
- No production behavior.
- No learning or consciousness claim.

## CLI-Visible Claims

- `r2_alias_plan_created=True`
- `target_package_layout_present=True`
- `compatibility_strategy_present=True`
- `alias_candidate_table_present=True`
- `nine_lines_have_alias_candidates=True`
- `import_compatibility_test_plan_present=True`
- `refactor_phase_gate_present=True`
- `files_moved=False`
- `files_renamed=False`
- `imports_changed=False`
- `modules_merged=False`
- `old_paths_deleted=False`
- `runtime_behavior_changed=False`
