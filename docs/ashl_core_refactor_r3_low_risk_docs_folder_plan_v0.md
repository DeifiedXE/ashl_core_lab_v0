# ASHL Core Refactor R3 Low-Risk Docs Folder Plan v0

Status: R3 low-risk documentation folder plan / docs and checker target.
Runtime impact: none.
Boundary impact: planning validation boundary plus B10/10 self-check.

## R3 Summary

R3 plans future documentation organization before any documentation movement.
No docs are moved in this package.
No folders are created in this package.
No Python modules are moved or imported differently in this package.

Plain version:

This is a filing-cabinet plan. It says which documents should stay at the front desk, which documents may later be grouped by line, which documents may later be archived, and which design-only documents must not be treated as runtime authority. It does not move the papers.

## Source Documents Read

This plan is aligned to these source documents:

- `docs/ashl_core_structural_refactor_map_v0.md`
- `docs/ashl_core_refactor_r2_compatibility_alias_plan_v0.md`
- `docs/phase0_line_document_index.md`
- `docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md`
- `docs/phase0_status.md`
- `docs/phase0_capability_matrix.md`
- `docs/current_boundary_index.md`
- `docs/codex_working_context_summary.md`

## Proposed Future Docs Folder Layout

Future docs layout:

```text
docs/
  authority/
  lines/
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
  archive/
    boundary_index/
    milestone_logs/
    historical_progress/
    superseded_designs/
  planning/
  audits/
```

This package only plans the layout. It does not create `docs/authority/`, `docs/lines/`, `docs/archive/`, `docs/planning/`, or `docs/audits/`.

Full planned archive and support paths:

- `docs/archive/boundary_index/`
- `docs/archive/milestone_logs/`
- `docs/archive/historical_progress/`
- `docs/archive/superseded_designs/`
- `docs/planning/`
- `docs/audits/`

## Root Authority Docs

These docs must stay in the root docs surface until a later explicit move package proves redirects, indexes, and human/Codex lookup rules:

- `docs/current_boundary_index.md`
- `docs/phase0_status.md`
- `docs/phase0_capability_matrix.md`
- `docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md`
- `docs/codex_working_context_summary.md`
- `docs/research_plan.md`
- `docs/phase0_line_document_index.md`
- `docs/phase1_to_phase5_growth_substrate_plan.md`

Reason:

These are navigation, boundary, current status, capability inventory, and planning entry documents. Moving them without redirects would make Codex, humans, and future checkers look in the wrong place.

## Line Docs Folder Plan

### spine

Future docs folder:
`docs/lines/spine/`

Candidate docs:
- `docs/phase1_to_phase5_growth_substrate_plan.md`
- `docs/phase0_minimal_learning_action_memory_loop_plan.md`
- `docs/current_boundary_index.md`

Keep in root docs:
- `docs/current_boundary_index.md`
- `docs/phase1_to_phase5_growth_substrate_plan.md`

Archive candidates:
- older Phase1 handoff summaries after redirects exist
- superseded session trace planning notes after current status controls

Needs review before move:
- any document referenced by `docs/codex_working_context_summary.md`

Reason:
Spine docs connect session trace, frame, handoff, and closure evidence. They are lookup-critical.

move_allowed_now=false

### body

Future docs folder:
`docs/lines/body/`

Candidate docs:
- `docs/sandbox_boundary_capability_assumption_v0_1.md`
- `docs/sandbox_failure_trace_contract_v0_1.md`
- `docs/sandbox_safety_audit_v0_1.md`
- `docs/body_motor_feedback_to_affordance_confidence_design_v0.md`
- `docs/body_motor_affordance_tendency_endocrine_reconciliation_design_v0.md`

Keep in root docs:
- none by default; root authority docs still stay root

Archive candidates:
- historical b95-b104 direct-command compression notes after current indexes cover them
- older action-line progress notes after matrix references are stable

Needs review before move:
- docs that mention direct command, execution, final_action, or selected_action

Reason:
Body docs describe sandbox action, body-motor, selected_action, final_action, direct_command, execution, and affordance boundaries.

move_allowed_now=false

### thought

Future docs folder:
`docs/lines/thought/`

Candidate docs:
- `docs/qingyin_thought_system_layering_design_v0.md`
- `docs/qingyin_proto_purpose_generation_boundary_design_v0.md`
- `docs/phase0_thought_memory_action_parallel_loop_plan.md`

Keep in root docs:
- none by default; root authority docs still stay root

Archive candidates:
- superseded thought-loop planning notes after b178 closure controls
- older proto-purpose drafts after current boundary docs control

Needs review before move:
- docs that could be misread as runtime thought or LLM runtime authority

Reason:
Thought docs describe purpose, preview, layered thought, and candidate-hint planning without granting runtime thought authority.

move_allowed_now=false

### memory

Future docs folder:
`docs/lines/memory/`

Candidate docs:
- `docs/memory_layers.md`
- `docs/five_layer_memory_design_assumption_v0_1.md`
- `docs/five_layer_memory_framework_boundary_v0.md`
- `docs/memory_influence_behavior_gate_design_v0.md`
- `docs/retention_line_progress_log_2026-06-10.md`

Keep in root docs:
- none by default; root authority docs still stay root

Archive candidates:
- old memory progress logs after capability inventory references are stable
- stale temporary cross-session handoff docs after current memory boundary docs control

Needs review before move:
- any doc that could imply automatic long-term memory or retained JSONL runtime influence

Reason:
Memory docs separate working memory, reviewed memory, retention, and influence previews from unrestricted persistent memory.

move_allowed_now=false

### perception

Future docs folder:
`docs/lines/perception/`

Candidate docs:
- `docs/retina_decoder_design_v0.md`
- `docs/simple_visual_frame_buffer_design_v0.md`
- `docs/visual_frame_change_design_v0.md`
- `docs/focus_selector_design_v0.md`
- `docs/focus_application_boundary_review_v0.md`

Keep in root docs:
- none by default; root authority docs still stay root

Archive candidates:
- older simulated-vision milestone notes after visual grounding docs control
- stale visual-retention progress logs after retained visual path is formalized

Needs review before move:
- docs that could be misread as semantic vision, object recognition, or active focus authority

Reason:
Perception docs cover symbolic vision, visual frame change, focus candidates, and grounding evidence without granting semantic vision.

move_allowed_now=false

### bridge

Future docs folder:
`docs/lines/bridge/`

Candidate docs:
- `docs/qingyin_bridge_dual_eye_capability_perception_design_v0.md`
- `docs/perception_to_action_boundary_review_v0.md`
- `docs/focus_perception_boundary_construction_log_v0.md`

Keep in root docs:
- none by default; root authority docs still stay root

Archive candidates:
- older bridge/capability design drafts after capability-map boundaries control
- source-link planning notes after Phase2 source-link reports control

Needs review before move:
- docs that mention raw tool access, capability map mutation, or action preparation

Reason:
Bridge docs connect perception evidence to capability perception while blocking raw tool access and action authority.

move_allowed_now=false

### endocrine

Future docs folder:
`docs/lines/endocrine/`

Candidate docs:
- `docs/mimetic_endocrine_system_design_v0.md`
- `docs/state_settling_and_mimetic_endocrine_concept_book_v0.md`
- `docs/body_motor_affordance_tendency_endocrine_reconciliation_design_v0.md`
- `docs/milestone_logs/mimetic_endocrine_line_milestone_2026-06-09.md`

Keep in root docs:
- none by default; root authority docs still stay root

Archive candidates:
- old endocrine milestone logs after archive redirect exists
- superseded settling drafts after current state-settling docs control

Needs review before move:
- docs that could imply direct endocrine feed, tendency override, or emotion proof

Reason:
Endocrine docs describe traceable modulation and settling context without granting direct action authority.

move_allowed_now=false

### voice

Future docs folder:
`docs/lines/voice/`

Candidate docs:
- `docs/qingyin_first_output_runtime_minimal_spec_v0.md`
- `docs/qingyin_first_output_contract_v0.md`
- `docs/voice_instinct_assumption_v0_1.md`
- `docs/qingyin_audio_cochlea_decoder_design_v0.md`
- `docs/qingyin_vocal_organ_engine_design_v0.md`
- `docs/internal_auditory_feedback_design_supplement_v0.md`

Keep in root docs:
- none by default; root authority docs still stay root

Archive candidates:
- stale first-output readiness checklists after runtime readiness docs control
- older voice instinct notes after current voice boundary docs control

Needs review before move:
- docs that could be misread as speech recognition, TTS runtime, conversation, or proof of consciousness

Reason:
Voice docs cover first output, mentor feedback, voice instinct, cochlea, vocal organ, and internal auditory feedback.

move_allowed_now=false

### lesson

Future docs folder:
`docs/lines/lesson/`

Candidate docs:
- `docs/failure_event_schema_foundation_v0.md`
- `docs/lesson_candidate_builder_contract_v0.md`
- `docs/lesson_candidate_draft_review_queue_contract_v0.md`
- `docs/review_decision_contract_v0.md`
- `docs/lesson_application_boundary_review_v0.md`

Keep in root docs:
- none by default; root authority docs still stay root

Archive candidates:
- old lesson application progress logs after review boundary docs control
- stale readiness checklists after current capability matrix controls

Needs review before move:
- docs that could imply automatic learning, unreviewed lesson application, or production lesson behavior

Reason:
Lesson docs cover failure events, lesson candidates, review tasks, review decisions, evidence, and lesson application boundaries.

move_allowed_now=false

### governance

Future docs folder:
`docs/lines/governance/`

Candidate docs:
- `docs/repo_audit_minimal_v0_2026-06-12.md`
- `docs/phase0_doc_inventory.md`
- `docs/phase0_doc_consistency_audit.md`
- `docs/phase0_versioning_policy.md`
- `docs/phase0_task_queue.md`
- `docs/ashl_core_structural_refactor_map_v0.md`
- `docs/ashl_core_refactor_r2_compatibility_alias_plan_v0.md`

Keep in root docs:
- `docs/current_boundary_index.md`
- `docs/phase0_status.md`
- `docs/phase0_capability_matrix.md`
- `docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md`
- `docs/codex_working_context_summary.md`
- `docs/research_plan.md`
- `docs/phase0_line_document_index.md`

Archive candidates:
- historical status compression docs after active index references exist
- old boundary index snapshots after archive index references exist

Needs review before move:
- any document named by current boundary, working context, README, smoke tests, or targeted unit tests

Reason:
Governance docs are the lookup and claim-control layer. Moving them is highest risk and must wait for redirect/index plans.

move_allowed_now=false

## Archive Plan

Archive candidate types:

- old boundary index snapshots
- milestone logs
- progress logs
- historical status compression docs
- superseded planning docs
- stale readiness checklists

This package lists archive candidates only. It does not move files into `docs/archive/`.

## Design-Only Docs Marking

design_only_not_runtime_docs:

- retina decoder design
- focus selector design
- mimetic endocrine system design
- Qingyin Bridge dual-eye design
- voice/audio/cochlea/vocal-organ design
- thought layering design
- memory framework design

Design-only docs can guide future packages, but they must not be treated as runtime capability, production behavior, memory write, predictor influence, emotion proof, learning proof, or consciousness proof.

## Needs Review Before Move

needs_review_before_move:

- root authority docs
- docs referenced by `docs/current_boundary_index.md`
- docs referenced by `docs/codex_working_context_summary.md`
- docs referenced by `README.md`
- docs referenced by `run_all_smoke_tests.py`
- docs referenced by targeted unit tests
- docs that mention runtime, production, memory write, predictor influence, direct endocrine feed, direct tendency feed, action selection, execution, learning, or consciousness

## B10/10 Hallucination Self-Check

b190 requires B10/10 hallucination self-check.

Self-check terms:

- report keys only from parsed runtime/checker output
- verified facts separated from assumptions
- exact key echo for boundary / records / observed results
- no repo mutation beyond this package
- no claim that planned folder movement already happened
- no claim that docs were moved
- no claim that imports changed
- no claim that runtime behavior changed

Self-check result: pass when the checker validates every term above and all movement/runtime flags are false.

## Boundary Audit

Boundary audit terms:

- no production behavior
- no runtime behavior leak
- no memory write / retention write
- no predictor read / influence / mutation
- no direct endocrine feed
- no direct tendency feed
- no proof-of-learning claim
- no cross-purpose feedback
- no raw weighted sum direct decision
- no affordance used as desire
- no tendency override purpose or affordance gate
- no next-layer boundary content implemented

Boundary audit result: pass when this package remains documentation planning only.

## Non-Goals

- No docs moved.
- No docs/lines folder created.
- No docs/archive folder created.
- No docs deleted.
- No docs renamed.
- No document path references changed.
- No Python import changed.
- No Python module moved.
- No alias implemented.
- No module merged.
- No runtime behavior changed.
- No candidate input.
- No action selection.
- No execution.
- No memory write.
- No retention write.
- No predictor use.
- No endocrine feed.
- No tendency feed.
- No production behavior.
- No learning claim.
- No consciousness claim.

## CLI-Visible Claims

- `r3_docs_folder_plan_created=True`
- `source_docs_read=True`
- `root_authority_docs_listed=True`
- `nine_line_docs_candidates_listed=True`
- `archive_candidates_listed=True`
- `design_only_docs_marked=True`
- `needs_review_before_move_listed=True`
- `move_allowed_now_all_false=True`
- `docs_moved=False`
- `docs_deleted=False`
- `docs_renamed=False`
- `python_modules_touched_for_refactor=False`
- `imports_changed=False`
- `runtime_behavior_changed=False`
- `b10_self_check_required=True`
- `b10_self_check_passed=True`
