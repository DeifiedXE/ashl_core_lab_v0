# ASHL Core Structural Refactor Map v0

Status: structural map / docs and checker target.
Runtime impact: none.
Boundary impact: structural validation boundary only if referenced by the current Boundary Index.

## Summary

This document maps the current ASHL Core repository into nine structural lines.
It does not move files or change runtime behavior.

Plain version:

This is a map of the current organs of ASHL Core. It shows where the parts live now, which parts should not be rebuilt, which parts should only be extended, and which families may later be merged. This package does not perform surgery.

## Nine-Line Current Map

## action_body_motor

Plain role:
Sandbox body, action selection surfaces, final action, direct command, execution, outcome, feedback, and body-motor settling.

Current core modules:
- `ashl_core/action_sandbox.py`
- `ashl_core/sandbox_candidate_ordering_signal_arbitration_minimal.py`
- `ashl_core/sandbox_candidate_ordering_arbitration_selected_action_minimal.py`
- `ashl_core/sandbox_candidate_ordering_arbitration_final_action_minimal.py`
- `ashl_core/sandbox_candidate_ordering_arbitration_direct_command_minimal.py`
- `ashl_core/sandbox_candidate_ordering_arbitration_direct_command_execution_minimal.py`
- `ashl_core/sandbox_body_motor_final_action_minimal.py`
- `ashl_core/sandbox_body_motor_command_execution_loop_minimal.py`

Current tests:
- `tests/test_action_sandbox.py`
- `tests/test_sandbox_candidate_ordering_signal_arbitration_minimal.py`
- `tests/test_sandbox_candidate_ordering_arbitration_selected_action_minimal.py`
- `tests/test_sandbox_candidate_ordering_arbitration_final_action_minimal.py`
- `tests/test_sandbox_candidate_ordering_arbitration_direct_command_minimal.py`
- `tests/test_sandbox_candidate_ordering_arbitration_direct_command_execution_minimal.py`

Current docs:
- `docs/current_boundary_index.md`
- `docs/phase0_status.md`
- `docs/phase0_capability_matrix.md`
- `docs/sandbox_boundary_capability_assumption_v0_1.md`

Current outputs:
- sandbox candidate ordering records
- selected_action records
- final_action records
- direct_command records
- sandbox execution records
- outcome observation and feedback records

Partial or design-only parts:
- production action execution is not present
- runtime action loop is not present
- real UI or external tool operation is not present

Duplicate or merge candidates:
- selected_action approval / selected_action minimal
- final_action approval / final_action minimal
- direct_command approval / direct_command minimal
- execution approval / execution minimal

Historical or archive candidates:
- older b95-b104 action-line audit/status compression docs
- earlier sandbox final/direct-command boundary summaries after current index archives

Future folder suggestion:
- `ashl_core/body/`

## thought_purpose

Plain role:
Purpose, proto-purpose, thought preview, candidate hints, approved-purpose ordering, and future layered thought.

Current core modules:
- `ashl_core/experience_derived_proto_purpose_candidate_trace_minimal.py`
- `ashl_core/proto_purpose_approval_boundary_minimal.py`
- `ashl_core/approved_purpose_candidate_ordering_boundary_minimal.py`
- `ashl_core/approved_purpose_candidate_ordering_minimal.py`
- `ashl_core/thought_memory_action_parallel_mini_loop_minimal.py`
- `ashl_core/thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_minimal.py`

Current tests:
- `tests/test_experience_derived_proto_purpose_candidate_trace_minimal.py`
- `tests/test_proto_purpose_approval_boundary_minimal.py`
- `tests/test_approved_purpose_candidate_ordering_minimal.py`
- `tests/test_thought_memory_action_parallel_mini_loop_minimal.py`
- `tests/test_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_minimal.py`

Current docs:
- `docs/qingyin_thought_system_layering_design_v0.md`
- `docs/qingyin_proto_purpose_generation_boundary_design_v0.md`
- `docs/phase0_thought_memory_action_parallel_loop_plan.md`

Current outputs:
- proto-purpose candidate records
- approved_purpose records
- thought/action/memory mini-loop records
- weak candidate hint records

Partial or design-only parts:
- runtime layered thought is design-only
- specialty anchors and habits are not implemented
- thought preview is not observed outcome

Duplicate or merge candidates:
- approval-boundary / minimal pairs in approved-purpose action paths
- readback / hint / ordering packages that may later become one template

Historical or archive candidates:
- old thought-loop planning docs after b178 closure
- earlier purpose design assumptions superseded by current boundaries

Future folder suggestion:
- `ashl_core/thought/`

## memory_retention_influence

Plain role:
Same-session working memory, reviewed memory candidates, controlled memory write/read, retention helpers, and bounded memory influence previews.

Current core modules:
- `ashl_core/session_working_memory.py`
- `ashl_core/memory_admission_minimal.py`
- `ashl_core/memory_write_and_read_minimal.py`
- `ashl_core/memory_influence_preview_minimal.py`
- `ashl_core/memory_runtime_influence_minimal.py`
- `ashl_core/mentor_gated_experience_retention_minimal.py`
- `ashl_core/retained_experience_exact_key_lookup_minimal.py`

Current tests:
- `tests/test_session_working_memory.py`
- `tests/test_memory_admission_minimal.py`
- `tests/test_memory_write_and_read_minimal.py`
- `tests/test_memory_influence_preview_minimal.py`
- `tests/test_memory_runtime_influence_minimal.py`
- `tests/test_mentor_gated_experience_retention_minimal.py`

Current docs:
- `docs/memory_layers.md`
- `docs/five_layer_memory_design_assumption_v0_1.md`
- `docs/five_layer_memory_framework_boundary_v0.md`
- `docs/memory_influence_behavior_gate_design_v0.md`
- `docs/retention_line_progress_log_2026-06-10.md`

Current outputs:
- session working-memory records
- reviewed memory candidate records
- minimal reviewed lesson memory records
- controlled memory read records
- retained experience read/list/lookup records
- bounded memory influence preview records

Partial or design-only parts:
- Core Memory, Archive Memory, and full Long-term Memory runtime are not present
- automatic memory admission is not present
- retained JSONL rebuild as runtime influence is blocked

Duplicate or merge candidates:
- memory admission approval / admission / write approval / write-read packages
- retained readback / listing / exact-key lookup helpers

Historical or archive candidates:
- old memory influence roadmap logs once current matrix controls the claim
- stale cross-session temporary-space docs after current memory boundary docs

Future folder suggestion:
- `ashl_core/memory/`

## vision_eye_focus

Plain role:
Symbolic visual input, visual frame traces, visual-spatial grounding, focus candidates, and perception evidence surfaces.

Current core modules:
- `ashl_core/simulated_vision_viewport.py`
- `ashl_core/simulated_vision_first_person_viewport.py`
- `ashl_core/visual_spatial_grounding_minimal.py`
- `ashl_core/visual_frame_buffer_schema.py`
- `ashl_core/visual_frame_change_trace.py`
- `ashl_core/focus_candidate_schema.py`
- `ashl_core/focus_candidate_from_change_trace.py`

Current tests:
- `tests/test_simulated_vision_viewport.py`
- `tests/test_simulated_vision_first_person_viewport.py`
- `tests/test_visual_spatial_grounding_minimal.py`
- `tests/test_visual_frame_change_trace.py`
- `tests/test_focus_candidate_schema.py`
- `tests/test_focus_candidate_from_change_trace.py`

Current docs:
- `docs/retina_decoder_design_v0.md`
- `docs/simple_visual_frame_buffer_design_v0.md`
- `docs/visual_frame_change_design_v0.md`
- `docs/focus_selector_design_v0.md`
- `docs/focus_application_boundary_review_v0.md`

Current outputs:
- symbolic viewport records
- visual frame records
- visual change records
- focus candidate records
- visual-spatial grounding records

Partial or design-only parts:
- semantic vision is not present
- object recognition is not present
- active focus authority is not present

Duplicate or merge candidates:
- focus candidate schema / ranking trace / ranking trace design records
- visual frame schema / frame assembly / frame change records

Historical or archive candidates:
- early simulated vision milestone logs after current visual grounding docs
- older visual retention progress logs once retained visual path is formalized

Future folder suggestion:
- `ashl_core/perception/`

## qingyin_bridge_capability

Plain role:
Capability perception bridge, affordance binding, and grounded capability map records.

Current core modules:
- `ashl_core/visual_spatial_motor_affordance_bridge_minimal.py`
- `ashl_core/qingyin_bridge_grounded_capability_map_minimal.py`
- `ashl_core/minimal_body_schema_affordance_consistency_runtime.py`
- `ashl_core/phase2_closed_phase1_substrate_perception_capability_grounding_entry_minimal.py`
- `ashl_core/phase2_perception_capability_evidence_source_link_minimal.py`
- `ashl_core/phase2_grounding_unknown_classification_correction_minimal.py`

Current tests:
- `tests/test_visual_spatial_motor_affordance_bridge_minimal.py`
- `tests/test_qingyin_bridge_grounded_capability_map_minimal.py`
- `tests/test_minimal_body_schema_affordance_consistency_runtime.py`
- `tests/test_phase2_closed_phase1_substrate_perception_capability_grounding_entry_minimal.py`
- `tests/test_phase2_perception_capability_evidence_source_link_minimal.py`
- `tests/test_phase2_grounding_unknown_classification_correction_minimal.py`

Current docs:
- `docs/qingyin_bridge_dual_eye_capability_perception_design_v0.md`
- `docs/perception_to_action_boundary_review_v0.md`
- `docs/current_boundary_index.md`
- `docs/phase1_to_phase5_growth_substrate_plan.md`

Current outputs:
- body-relative affordance bridge records
- grounded capability map records
- Phase2 perception/capability entry reports
- evidence source-link reports
- not-capability correction records for wait/probe cues

Partial or design-only parts:
- raw tool access is not present
- Action Gateway calls are not present
- capability-map mutation is not present

Duplicate or merge candidates:
- Phase2 entry / source-link / correction reports should become a single grounding read path later
- bridge design docs and grounded map modules should be kept distinct until compatibility aliases exist

Historical or archive candidates:
- early bridge design notes after current grounded capability map becomes the active claim
- old body-affordance status summaries after current matrix controls them

Future folder suggestion:
- `ashl_core/bridge/`

## mimetic_endocrine_settling

Plain role:
Mimetic endocrine-like traces, tendency context, state-settling records, and bounded modulation evidence.

Current core modules:
- `ashl_core/mimetic_endocrine_sweetness_preference_sandbox_minimal.py`
- `ashl_core/mimetic_endocrine_cost_sensitive_choice_sandbox_minimal.py`
- `ashl_core/dopamine_like_reward_trace_check.py`
- `ashl_core/norepinephrine_like_change_attention_trace_check.py`
- `ashl_core/cortisol_like_failure_load_trace_check.py`
- `ashl_core/oxytocin_like_review_trust_trace_check.py`
- `ashl_core/mimetic_endocrine_post_event_settling_design_minimal.py`

Current tests:
- `tests/test_mimetic_endocrine_sweetness_preference_sandbox_minimal.py`
- `tests/test_mimetic_endocrine_cost_sensitive_choice_sandbox_minimal.py`
- `tests/test_dopamine_like_reward_trace_check.py`
- `tests/test_norepinephrine_like_change_attention_trace_check.py`
- `tests/test_cortisol_like_failure_load_trace_check.py`
- `tests/test_oxytocin_like_review_trust_trace_check.py`

Current docs:
- `docs/mimetic_endocrine_system_design_v0.md`
- `docs/state_settling_and_mimetic_endocrine_concept_book_v0.md`
- `docs/body_motor_affordance_tendency_endocrine_reconciliation_design_v0.md`
- `docs/milestone_logs/mimetic_endocrine_line_milestone_2026-06-09.md`

Current outputs:
- dopamine-like reward trace records
- norepinephrine-like change-attention trace records
- cortisol-like failure-load trace records
- oxytocin-like review-trust trace records
- post-event settling design records

Partial or design-only parts:
- direct endocrine feed is not present
- direct tendency feed is not present
- endocrine/tendency cannot create purpose or select action

Duplicate or merge candidates:
- four-axis endocrine trace checks may later share one trace schema
- body-motor feedback settling and endocrine settling need a shared context boundary later

Historical or archive candidates:
- older endocrine milestone logs after current line map controls navigation
- old tendency notes that imply direct action authority

Future folder suggestion:
- `ashl_core/endocrine/`

## voice_audio_first_output

Plain role:
First output traces, fixed non-LLM utterance mapping, mentor feedback trace, and future voice/audio design.

Current core modules:
- `ashl_core/minimal_first_output_runtime.py`
- `ashl_core/minimal_non_llm_utterance_map.py`
- `ashl_core/minimal_mentor_feedback_stub_runtime.py`
- `ashl_core/minimal_interaction_cli_bridge.py`
- `ashl_core/first_output_feedback_append_only_persistence.py`

Current tests:
- `tests/test_minimal_first_output_runtime.py`
- `tests/test_minimal_non_llm_utterance_map.py`
- `tests/test_minimal_mentor_feedback_stub_runtime.py`
- `tests/test_minimal_interaction_cli_bridge.py`
- `tests/test_first_output_feedback_append_only_persistence.py`

Current docs:
- `docs/qingyin_first_output_runtime_minimal_spec_v0_1.md`
- `docs/qingyin_first_output_contract_v0_1.md`
- `docs/first_output_trace_contract_v0_1.md`
- `docs/mentor_feedback_trace_contract_v0_1.md`
- `docs/qingyin_vocal_organ_engine_design_v0.md`
- `docs/qingyin_audio_cochlea_decoder_design_v0.md`

Current outputs:
- first_output_trace records
- fixed utterance-map outputs
- mentor feedback stub records
- interaction bridge trace records

Partial or design-only parts:
- free-form runtime language generation is not present
- hearing, STT, TTS, vocal organ runtime, and internal auditory feedback are design-only

Duplicate or merge candidates:
- first output contract / runtime spec / readiness checklist / audit docs
- mentor feedback contract / runtime checklist / audit docs

Historical or archive candidates:
- first-output readiness checklists after the current first-output trace contract is stable
- older voice instinct docs if they imply runtime audio authority

Future folder suggestion:
- `ashl_core/voice/`

## lesson_review_evidence

Plain role:
Failure events, lesson candidates, review gates, human review decisions, dry-run application, and evidence summaries.

Current core modules:
- `ashl_core/failure_reason_classifier.py`
- `ashl_core/failure_event_schema_foundation.py`
- `ashl_core/lesson_candidate_from_failure_reason.py`
- `ashl_core/lesson_candidate_review_gate.py`
- `ashl_core/generic_lesson_review_decision_minimal.py`
- `ashl_core/reviewed_lesson_trace_preview.py`
- `ashl_core/reviewed_lesson_dry_run_correction_minimal.py`
- `ashl_core/lesson_effect_evidence_trace_minimal.py`

Current tests:
- `tests/test_failure_reason_classifier.py`
- `tests/test_failure_event_schema_foundation.py`
- `tests/test_lesson_candidate_from_failure_reason.py`
- `tests/test_lesson_candidate_review_gate.py`
- `tests/test_generic_lesson_review_decision_minimal.py`
- `tests/test_reviewed_lesson_dry_run_correction_minimal.py`
- `tests/test_lesson_effect_evidence_trace_minimal.py`

Current docs:
- `docs/lesson_candidate_builder_contract_v0_1.md`
- `docs/lesson_candidate_draft_schema_v0_1.md`
- `docs/review_decision_contract_v0_1.md`
- `docs/reviewed_lesson_application_boundary_reconciliation_v0.md`
- `docs/lesson_application_boundary_review_v0.md`

Current outputs:
- failure event records
- lesson candidate records
- review task and review decision records
- dry-run correction records
- lesson effect evidence records

Partial or design-only parts:
- review decision is not application approval
- evidence is not memory write approval
- Qingyin-authored natural-language lesson generation is not present

Duplicate or merge candidates:
- lesson candidate schema / audit / strict injection guard docs
- review task / review decision / review trace schema and audit docs

Historical or archive candidates:
- older lesson draft docs after current contract docs become the active source
- early generic evidence pipeline logs after matrix controls the claim

Future folder suggestion:
- `ashl_core/lesson/`

## governance_audit_documentation

Plain role:
Boundary index, audits, status docs, capability matrix, planning docs, task queue, smoke runner, and repository hygiene checks.

Current core modules:
- `ashl_core/phase0_package_boundary_versioning_policy_minimal.py`
- `ashl_core/codex_task_queue_minimal.py`
- `ashl_core/phase2_to_phase10_completed_capability_cross_check_minimal.py`
- `ashl_core/teaching_cli.py`
- `run_all_smoke_tests.py`

Current tests:
- `tests/test_phase0_documentation_inventory_and_consistency_reconciliation.py`
- `tests/test_phase0_package_boundary_versioning_policy_minimal.py`
- `tests/test_codex_task_queue_minimal.py`
- `tests/test_phase2_to_phase10_completed_capability_cross_check_minimal.py`

Current docs:
- `docs/current_boundary_index.md`
- `docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md`
- `docs/phase0_status.md`
- `docs/phase0_capability_matrix.md`
- `docs/phase0_line_document_index.md`
- `docs/research_plan.md`

Current outputs:
- boundary index records
- capability inventory and matrix entries
- documentation consistency checks
- package/version governance records
- smoke test report data
- completed capability cross-check reports

Partial or design-only parts:
- governance checks do not create runtime behavior
- passing tests do not count as explicit user approval
- package IDs are not Boundary Index versions

Duplicate or merge candidates:
- readback / index / closure audit packages
- boundary audit / status compression / docs sync packages
- package approval boundary / minimal implementation pairs

Historical or archive candidates:
- archived current boundary index files
- old status compression docs after active index replacement
- milestone logs once current inventory and matrix control the claim

Future folder suggestion:
- `ashl_core/governance/`
- `ashl_core/spine/` for Phase1 session trace, frame, tick handoff, and continuity substrate

## Completed Do-Not-Rebuild Anchors

- Phase0 thought/action/memory mini-loop.
- Phase1 session trace spine / frame / tick handoff / three-line index / closure.
- Phase2 entry / source-link / unknown classification correction.
- reviewed lesson memory candidate / memory write-read / retention / readback.
- first_output / first_output_trace / mentor_feedback_trace.
- symbolic eye / visual-spatial grounding.
- Qingyin Bridge grounded capability map.
- sandbox action chain.
- endocrine-like trace / settling trace.

## Partial Extend-Only Anchors

- memory line should be integrated, not rebuilt.
- first_output should be persisted / connected, not rebuilt.
- symbolic eye should be connected to runtime focus, not replaced.
- endocrine trace should become bounded context surface, not direct action authority.
- Phase2 grounding should summarize availability and unresolved/deferred evidence, not restart entry/source-link packages.
- governance should keep claims honest, not become a substitute for runtime progress.

## Duplicate / Merge Candidate Families

- selected_action approval / selected_action minimal.
- final_action approval / final_action minimal.
- direct_command approval / direct_command minimal.
- execution approval / execution minimal.
- outcome feedback approval / outcome feedback minimal.
- candidate reordering approval / candidate reordering minimal.
- readback / index / closure audit packages.
- docs sync / boundary audit / compression packages.

This package only lists candidates. It does not merge them.

## Historical / Archive Candidates

- older boundary index snapshots already referenced from `docs/current_boundary_index.md`.
- old status compression docs after the active current index has replaced their short-term role.
- milestone logs once current capability matrix and inventory control the current claim.
- early design assumptions that conflict with newer boundary/current-status docs.
- readiness checklists that are superseded by implemented record/checker paths.

This package only lists candidates. It does not delete, move, or archive them.

## Proposed Refactor Phases

- R1: structural map only.
- R2: add package `__init__` wrappers / aliases.
- R3: move low-risk docs into line folders.
- R4: move modules with compatibility shims.
- R5: merge duplicate gate families.
- R6: update imports and tests.
- R7: deprecate old paths only after compatibility passes.

No phase after R1 is performed by this package.

## Suggested Future Folder Map

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

Folder intent:

```text
spine       -> Phase1 session trace / tick handoff / frame / continuity
body        -> sandbox action, body-motor, selected_action, final_action, command, execution
thought     -> purpose, proto-purpose, thought layers, candidate hints
memory      -> working memory, memory admission, retention, readback, influence preview
perception  -> symbolic eye, visual-spatial grounding, focus candidate
bridge      -> Qingyin Bridge, capability map, affordance binding
endocrine   -> mimetic endocrine, tendency, settling
voice       -> first_output, voice/audio design, mentor feedback trace
lesson      -> failure, lesson candidate, review, dry-run, evidence
governance  -> boundary index, audits, capability matrix, roadmap, status docs
```

## Non-Goals

- No runtime behavior change.
- No file move.
- No file delete.
- No rename.
- No import path change.
- No module merge.
- No boundary expansion.
- No candidate input.
- No action selection.
- No execution.
- No memory write.
- No retention write.
- No predictor use.
- No endocrine feed.
- No production behavior.
- No learning or consciousness claim.
