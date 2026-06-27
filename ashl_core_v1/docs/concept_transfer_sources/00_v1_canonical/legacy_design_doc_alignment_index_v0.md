# ASHL Core v1 Legacy Design Document Alignment Index v0

This document maps legacy ASHL Core / Qingyin design and status documents onto
the canonical ASHL Core v1 nine-line organ definition.

It is an alignment index only. It does not rewrite legacy documents, move docs,
delete docs, create dataclasses, implement bridge or voice, connect old CLI, or
create a runtime loop.

Plain wording:

> 先把舊文件貼上新器官標籤，決定哪些能沿用、哪些要改名、哪些只能當歷史，避免 v1 被舊名詞拉回迷宮。

## Source Documents Read

Primary v1 and current-status sources:

- `ashl_core_v1/docs/nine_line_definition_v0.md`
- `docs/phase0_line_document_index.md`
- `docs/codex_working_context_summary.md`
- `docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md`
- `docs/phase0_status.md`
- `docs/phase0_capability_matrix.md`

Legacy design sources referenced but not modified:

- `docs/body_motor_affordance_tendency_endocrine_reconciliation_design_v0.md`
- `docs/focus_selector_design_v0.md`
- `docs/qingyin_bridge_dual_eye_capability_perception_design_v0.md`
- `docs/qingyin_thought_system_layering_design_v0.md`
- `docs/phase0_minimal_learning_action_memory_loop_plan.md`
- `docs/state_persistence.md`
- `docs/lesson_application_boundary_review_v0.md`
- `docs/qingyin_vocal_organ_engine_design_v0.md`
- `docs/qingyin_audio_cochlea_decoder_design_v0.md`

## Known Alignment Status Values

- `aligned`
- `rename_needed`
- `historical_only`
- `design_only_reference`
- `deferred`
- `needs_review`

## Known Reuse Policy Values

- `reuse_as_design_source`
- `reuse_with_v1_terms`
- `reference_only`
- `do_not_use_for_v1_runtime`
- `defer_until_later_phase`

## Alignment Rules by v1 Module

### 擬態具身模組

Legacy action, body-motor, sandbox action, selected_action, final_action,
direct_command, execution, body schema, and motor affordance documents may only
inform v1 body signal and action signal shapes.

Policy: do not directly port the old selected_action -> final_action ->
direct_command -> execution chain into v1.

### 思考運算模組

Legacy thought, purpose, proto-purpose, approved_purpose, candidate hint, and
thought-layering documents may inform v1 thought signal and thought layering.

Policy: old approved_purpose chains do not become v1 purpose authority by
default.

### 五重記憶模組

Legacy memory layer, working memory, retention, exact-key lookup, memory
influence, and state persistence documents may inform v1 memory application data
and readback surfaces.

directly port retained JSONL / old memory influence into persistent authority.

### 硬軟感知模組

Legacy retina decoder, visual frame buffer, visual frame change, focus selector,
symbolic viewport, and soft/hard perception documents may inform v1 perception
data.

attention-control runtime.

### 無限制能力橋接及可操作結構視覺化編譯模組

Legacy Qingyin Bridge, dual-eye capability perception, capability map, action
gateway, and feedback packet documents are design alignment only in v1 first
stage.

Policy: do not implement bridge, raw API/tool access, or action gateway calls in
this alignment index.

### 擬態內分泌模組

Legacy mimetic endocrine, dopamine_like, norepinephrine_like, oxytocin_like,
cortisol_like, state settling, tendency, and affordance reconciliation documents
may inform v1 endocrine signal and settling context.

Policy: "control" means state modulation, not direct decision, direct purpose
creation, direct action output, or proof of emotion.

### 獨立音訊模組

Legacy voice, audio, first_output, vocal organ, cochlea, internal auditory
feedback, and mentor feedback documents are deferred design references in v1
first stage.

Policy: do not implement voice, speech runtime, conversation runtime, or
consciousness claims in this alignment index.

### 學習性泛化應用模組

Legacy lesson, review, evidence, failure event, expected/actual contrast, lesson
candidate, review decision, and learning digest documents may inform v1 learning
digest design.

Policy: old lesson application is not v1 automatic learning. Review and evidence
are digestion material, not direct memory authority.

### 稽核邊界模組

Legacy governance, audit, boundary, capability matrix, current status, repo
audit, task queue, and versioning-policy documents may inform v1 policy and
reality-check design.

Policy: do not implement governance runtime. Passing tests, task queues, or Codex
reports are not human approval.

## Legacy Design Alignment Table

| old_doc_path | old_line_name | v1_module_name | alignment_status | reuse_policy | notes |
| --- | --- | --- | --- | --- | --- |
| `docs/body_motor_affordance_tendency_endocrine_reconciliation_design_v0.md` | body-motor action separation | 擬態具身模組 | rename_needed | reuse_with_v1_terms | Use as body signal and action signal design source only. Do not port selected_action, final_action, direct_command, or execution chain directly. |
| `docs/body_motor_affordance_tendency_endocrine_reconciliation_design_v0.md` | endocrine and tendency reconciliation | 擬態內分泌模組 | aligned | reuse_with_v1_terms | Reuse the separation rule: endocrine signal modulates context and must not create purpose or directly choose action. |
| `docs/qingyin_bridge_dual_eye_capability_perception_design_v0.md` | Qingyin Bridge dual-eye capability perception | 無限制能力橋接及可操作結構視覺化編譯模組 | deferred | defer_until_later_phase | Keep as bridge design source only. No raw API access, tool access, action gateway call, or bridge implementation in v1 first stage. |
| `docs/qingyin_thought_system_layering_design_v0.md` | thought layering | 思考運算模組 | aligned | reuse_as_design_source | Reuse instinct, specialized thought, coarse thought, and deep thought as thought architecture. Keep no-LLM runtime boundary. |
| `docs/phase0_minimal_learning_action_memory_loop_plan.md` | sandbox learning/action/memory loop | 學習性泛化應用模組 | rename_needed | reuse_with_v1_terms | Use as loop-evidence design source for learning digestion. It remains sandbox evidence, not proof of learning or runtime consciousness. |
| `docs/phase0_minimal_learning_action_memory_loop_plan.md` | same-session working memory influence | 五重記憶模組 | rename_needed | reuse_with_v1_terms | Use as temporary working-memory design evidence. Do not convert it into persistent memory authority. |
| `docs/phase0_minimal_learning_action_memory_loop_plan.md` | compact sandbox action path | 擬態具身模組 | rename_needed | reuse_with_v1_terms | Use only for body/action signal vocabulary. Do not import the old package chain. |
| `docs/state_persistence.md` | state persistence | 五重記憶模組 | needs_review | reference_only | State persistence is continuity support, not long-term memory and not a replacement for v1 five-layer memory. |
| `docs/lesson_application_boundary_review_v0.md` | lesson review and application boundary | 學習性泛化應用模組 | aligned | reuse_as_design_source | Reuse preview, dry-run, evidence, and application distinctions. Do not treat reviewed preview as v1 automatic learning. |
| `docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md` | actual capability inventory | 稽核邊界模組 | aligned | reference_only | Use as current repo reality check. It is not v1 runtime authority and not a capability grant. |
| `docs/codex_working_context_summary.md` | work-start orientation and user role | 稽核邊界模組 | aligned | reference_only | Use as human/project context and anti-fake-claim guard. It does not override current status files. |
| `docs/phase0_line_document_index.md` | legacy line document index | 稽核邊界模組 | aligned | reference_only | Use as navigation aid for old lines. It is not a v1 architecture source by itself. |
| `docs/phase0_status.md` | current status ledger | 稽核邊界模組 | aligned | reference_only | Use for current completed/blocked status. Do not treat package list as runtime capability. |
| `docs/phase0_capability_matrix.md` | capability matrix | 稽核邊界模組 | aligned | reference_only | Use for allowed/forbidden claims. It is not human approval and not v1 runtime. |
| `docs/qingyin_vocal_organ_engine_design_v0.md` | vocal organ design | 獨立音訊模組 | deferred | defer_until_later_phase | Keep as voice design source only. No speech runtime or conversation runtime in v1 first stage. |
| `docs/qingyin_audio_cochlea_decoder_design_v0.md` | cochlea and audio decoder design | 獨立音訊模組 | deferred | defer_until_later_phase | Keep as audio design source only. No hearing runtime or internal auditory feedback implementation now. |
| `docs/simple_visual_frame_buffer_design_v0.md` | visual frame buffer design | 硬軟感知模組 | design_only_reference | reuse_as_design_source | Use for visual frame data shape only. Do not create active perception runtime. |

## v1 First-Stage Reuse Scope

The first implementation stage may use aligned design sources for only these six
modules:

- 思考運算模組
- 擬態具身模組
- 硬軟感知模組
- 學習性泛化應用模組
- 五重記憶模組
- 擬態內分泌模組

The first implementation stage must not implement these three deferred modules:

- 獨立音訊模組
- 無限制能力橋接及可操作結構視覺化編譯模組
- 稽核邊界模組
