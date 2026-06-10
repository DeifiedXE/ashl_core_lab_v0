# ASHL Core 研究計畫 v0.8

## 核心定位

ASHL Core 是低算力、可教、可糾正、可連續、能外接工具的唯一模型幼體核心。

本階段人格核心是「清音」，不是艾希米。

清音是研究者型人格：知性、溫柔、包容，但在研究時不妥協。

核心宣言：唯一模型的唯一性，不在出生，而在成長。

## v0 主循環

v0 的目標是能跑完整主循環：

```text
輸入
→ 概念
→ 事件
→ 狀態
→ 暫想
→ 審思
→ 表達
→ 檢查
→ 輸出
→ log
```

已完成：

- Core Seed Formalization v0.9
- Memory Layers v1.0
- Integrated Loop v0.1
- Persistent Candidate Layer v0.2
- Correction Label v0.3
- Rule Candidate v0.4
- Candidate Review / Audit v0.5
- Trial Rule Layer v0.6
- Trial Suggestion Feedback v0.7
- Core Senses Design v0.8

## Core Senses / 核心感官

Text Sense 已存在，代表目前的文字輸入能力。

Screen Sense 與 Camera Sense 是未來核心感官，不是娛樂外掛。

- Screen Sense：畫面監視、視窗內容、游標位置、畫面變化。
- Camera Sense：攝影機畫面、實物教學、指向教學。
- Audio Sense：未來語音與環境聲音，暫緩。
- Tool Sense：工具回傳結果，暫緩。

純文字不足以支援真實世界概念學習。文字能教清音「蘋果怎麼定義」，但視覺感官才有機會教她「這個東西就是蘋果」。

視覺教學的早期目標是建立 `visual_concept_candidate`：

- 使用者文字教學
- mock sensor event
- 視覺區域參照
- 場景來源
- 候選概念
- audit 狀態

真正硬體支援延後到主循環、狀態保存、CLI 穩定後。

## 實驗總順序

目前採用 [ASHL Core／D清音 實驗總順序 v0.2](experiment_order.md) 作為後續開發路線依據。

後續開發應優先補齊：

- Core Seed
- Memory Layers
- Teaching Event
- Confidence / Promotion
- Memory Economy

完成內在連續性與文字接地後，再進入：

- Core Perception
- Visual Impression
- Symbol Grounding v1

因此下一階段不急著接攝影機或螢幕監視。Screen Sense / Camera Sense 已納入核心感官規劃，但真正硬體接入應在主循環、記憶層、教學事件、信心/晉升機制穩定後進行。

## Core Seed

Core Seed 已正式文件化，詳見 [docs/core_seed.md](core_seed.md)。

Core Seed 是 D清音幼體的成長胚胎藍圖，用於定義身份、存在目的、成長方向、權限邊界與成長原則。

需要特別澄清：Core Seed 中的「知性、溫柔、包容、研究不妥協」等人格詞彙是成長目標與行為評估方向，不代表系統已理解完整含義。

Core Seed 預設不可由 memory candidate、correction label、rule candidate、trial suggestion 或 trial feedback 直接改寫。修改 Core Seed 必須是明確版本化人工決策。

## Memory Layers

Memory Layers v1.0 已建立 core / long-term / working / archive 四層記憶基礎結構。

- Core Memory：只讀，不由普通流程改寫。
- Long-term Memory：提供 append 入口，不自動從 memory candidate 固化。
- Working Memory：可保存 session snapshot。
- Archive Memory：提供 append 入口，用於未來封存資料。

`memory_candidates.jsonl` 仍是候選日誌，不是 Long-term Memory。Long-term Memory 必須透過未來 promotion / confirmation 流程產生。

## 尚未完成

- 真攝影機 / 真螢幕感知
- 狀態保存穩定化
- CLI workflow
- Rule Apply
- Rule Promotion
- Mood Layer
- SQLite / Persistence Layer 正式化
- Tool Adapter

## 限制

本階段不接真 LLM、Web、GUI、TTS、SQLite、OpenCV、image model，也不讀螢幕、不接真攝影機、不儲存真圖片。

## Windows PowerShell

Windows PowerShell 請優先使用 `py -3`，不要優先使用 `python`。

原因：`python` 可能指到 WindowsApps alias，而不是實際 Python 安裝。

常用指令：

```powershell
py -3 run_all_smoke_tests.py
py -3 -m unittest discover
where.exe python
where.exe py
```

## Unknown Failure Reason Boundary

v1.7b Unknown Failure Reason Boundary Test 驗證格式正確但未知的 `failure_reason = unmapped_obstacle_shadow` 會被明確標記為 `unknown_failure_reason`。
這個結果不得生成 executable action，不得產生 active lesson，不得 fallback 成 `not_facing_east`，不得產生 `turn(east)`，也不得改變 behavior。
v1.7b 不測 malformed / empty / ambiguous failure_reason，不證明開放式泛化能力，也不處理 multi-lesson conflict / priority。

目前順序：
- v1.6 Phase -1.2 Lesson Causality Test：已完成
- v1.7a Known Failure Reason Determinism Test：已完成
- v1.7b Unknown Failure Reason Boundary Test：本包
- v1.8 Minimal Teaching CLI：延後
- v1.9 Multi-lesson Conflict / Priority：延後
- v2.0 Stale / Supersede：延後

## Second Known Failure Reason Determinism

v1.7c Second Known Failure Reason Determinism Test 新增第二條 known failure_reason：`not_facing_west`。
它只驗證 `not_facing_west -> turn(west)` 在相同輸入、相同初始狀態、相同 generator 設定下，排除 volatile fields 後 lesson output 核心語義穩定一致。
v1.7c 不證明 multi-lesson conflict，不證明 priority，不證明 open-ended lesson generation，也不處理 malformed / empty / ambiguous failure_reason。

目前順序：
- v1.6 Phase -1.2 Lesson Causality Test：已完成
- v1.7a Known Failure Reason Determinism Test：已完成
- v1.7b Unknown Failure Reason Boundary Test：已完成
- v1.8 Minimal Teaching CLI：已完成
- v1.7c Second Known Failure Reason Determinism Test：本包
- v1.9a Multi-lesson Isolation Test：下一步
- v1.9b Conflict Detection / Require Review：延後
- v1.9c CLI conflict_check 補真實檢查：延後
- v2.0 Stale / Supersede：延後

## Multi-lesson Isolation

v1.9a Multi-lesson Isolation Test 驗證 `lesson_001` 與 `lesson_002` 可以同時存在，且在不衝突情境下互不干擾。
east case 只應選 `lesson_001 -> turn(east)`；west case 只應選 `lesson_002 -> turn(west)`；兩者都不得交叉觸發，也不得出現 `conflict_detected = true`。
v1.9a 不證明 conflict detection，不證明 priority，不做 require_review，不做 stale / supersede，也不更新 CLI 的 `conflict_check = not_implemented`。

目前順序：
- v1.6 Phase -1.2 Lesson Causality Test：已完成
- v1.7a Known Failure Reason Determinism Test：已完成
- v1.7b Unknown Failure Reason Boundary Test：已完成
- v1.8 Minimal Teaching CLI：已完成
- v1.7c Second Known Failure Reason Determinism Test：已完成
- v1.9a Multi-lesson Isolation Test：本包
- v1.9b Conflict Detection / Require Review：下一步
- v1.9c CLI conflict_check 補真實檢查：延後
- v2.0 Stale / Supersede：延後

## Conflict Detection / Require Review

v1.9b Conflict Detection / Require Review 只證明同一 decision point 上 incompatible active lessons 會被偵測為 conflict，並採用 `require_review`。
本包的最小互斥 action 是 `turn(east)` 與 `turn(west)`；conflict 時不自動套用 lesson，不自動選 priority，不刪除 lesson，不修改 lesson 狀態。
disable 其中一條 lesson 後會恢復單 lesson 因果控制；re-enable 後恢復 require_review。
v1.9b 不證明 priority，不做自動解衝突，不做 stale / supersede，也不更新 CLI 的 `conflict_check = not_implemented`。

目前順序：
- v1.9a Multi-lesson Isolation Test：已完成
- v1.9b Conflict Detection / Require Review：本包
- v1.9c CLI conflict_check 補真實檢查：下一步
- v2.0 Stale / Supersede：延後

## CLI Conflict Check Integration

v1.9c CLI conflict_check 真實檢查只把 CLI 顯示層接到 v1.9b conflict detection 結果。
CLI 現在會回傳 `implemented = true`，並在 conflict flow 中顯示 `conflict_detected = true`、`conflict_resolution = require_review`、`review_status = pending_human_review`。
v1.9c 不做 priority，不做自動解衝突，不新增 accept / reject / choose lesson CLI，不修改 lesson 狀態，也不做 stale / supersede。

目前順序：
- v1.9a Multi-lesson Isolation Test：已完成
- v1.9b Conflict Detection / Require Review：已完成
- v1.9c CLI conflict_check 真實檢查：本包
- v2.0 Stale / Supersede：下一步候選

## Cross-task Shared Prerequisite Isolation

v1.9d Cross-task Shared Prerequisite Isolation Test 驗證 selection helper 可依 task / object / decision_point 區分 lesson。
本包使用 `lesson_001: pick_up cube_001 -> turn(east)` 與 `lesson_003: pick_up cube_002 -> turn(east)`，確認共享同一前置 action 不會造成 false conflict，也不會交叉選用。
v1.9d 不證明 stale，不證明 supersede，不證明 priority，不新增 require_review，也不修改 CLI conflict_check。

目前順序：
- v1.9a Multi-lesson Isolation Test：已完成
- v1.9b Conflict Detection / Require Review：已完成
- v1.9c CLI conflict_check 真實檢查：已完成
- v1.9d Cross-task Shared Prerequisite Isolation Test：本包
- v2.0a Manual Stale Marking：下一步
- v2.0b Supersede Link：延後
- v2.0c CLI lifecycle display：延後

## Manual Stale Marking

v2.0a Manual Stale Marking 只採用人工標記 stale。
lesson 保留 `status = active`，但 `stale = true` 時 selection helper 會跳過它，trace 記錄 `skipped_reason = stale`。
取消 stale 後，lesson 可恢復選用，並接回既有單 lesson 因果控制。
v2.0a 不做自動 stale，不做時間過期，不做 unused-count / failure-count stale，不做 supersede，不更新 CLI lifecycle display。

目前順序：
- v1.9d Cross-task Shared Prerequisite Isolation Test：已完成
- v2.0a Manual Stale Marking：本包
- v2.0b Supersede Link：下一步
- v2.0c CLI lifecycle display：延後
- v2.1 Stale / Supersede activation behavior：延後

## Supersede Link

v2.0b Supersede Link only records lifecycle metadata:
- `old_lesson.superseded_by = new_lesson_id`
- `new_lesson.supersedes = old_lesson_id`
- trace/read result can show the link and confirm `status_changed = false`
- trace/read result can show `selection_behavior_changed = false`

v2.0b does not disable old lessons, does not enable new lessons, does not archive old lessons, does not change selection behavior, does not override stale behavior, and does not update CLI lifecycle display. Supersede activation behavior is deferred to v2.1 or later.

Current order:
- v2.0a Manual Stale Marking：已完成
- v2.0b Supersede Link：已完成
- v2.0c CLI lifecycle display：本包
- v2.1 Stale / Supersede activation behavior：延後
## CLI lifecycle display

v2.0c adds a read-only CLI lifecycle display command, `run-lifecycle-display`.
It can show lesson id, status, stale, stale_reason, superseded_by, supersedes, selection eligibility, skipped reason, and conflict participation.

v2.0c does not modify stale state, does not create or modify supersede links, does not change selection behavior, does not change conflict behavior, and does not add lifecycle write commands. Lifecycle activation is deferred to v2.1 or later.

Current order:
- v2.0a Manual Stale Marking：已完成
- v2.0b Supersede Link：已完成
- v2.0c CLI lifecycle display：本包
- v2.1 Stale / Supersede activation behavior：下一步候選
## Supersede Replacement Suggestion

v2.1a adds trace-only supersede replacement suggestions.
`replacement_suggestions` are produced only when a lesson is skipped because it is stale and that source lesson has `superseded_by`.

The suggestion records the stale source lesson, replacement candidate id, candidate existence, candidate status, candidate stale state, candidate eligibility, and a reason. `activation_applied` remains false.

v2.1a does not change selection behavior, does not change conflict behavior, does not activate supersede links, does not automatically select replacement lessons, and does not add lifecycle write CLI commands. Actual supersede selection activation is deferred to v2.1b or later.

Current order:
- v2.0a Manual Stale Marking：已完成
- v2.0b Supersede Link：已完成
- v2.0c CLI lifecycle display：已完成
- v2.1a Supersede Replacement Suggestion：本包
- v2.1b Supersede Selection Activation：下一步候選
## Strict Supersede Selection Activation

v2.1b adds strict supersede selection activation.
Supersede link is metadata, not authorization, and the replacement candidate must pass normal selection eligibility.

Activation only applies when the old lesson is skipped because it is stale. The activation trace records every condition: old lesson stale, old lesson has superseded_by, candidate exists, candidate active, candidate not stale, candidate eligible, activation source, activation_applied, failed_conditions, and chain_followed.

v2.1b does not add priority, does not auto-resolve conflicts, does not enable or disable lessons, does not auto-mark stale, does not let conflict logic prefer supersede links, does not support multi-layer supersede chains, and does not add lifecycle write CLI.

Current order:
- v2.1a Supersede Replacement Suggestion：已完成
- v2.1b Strict Supersede Selection Activation：本包
- v2.1c Activation Audit / Edge Case Hardening：下一步候選
## Activation Audit / Edge Case Hardening

v2.1c is audit / hardening only.
No new activation capability is added, and activation conditions are not relaxed.

This stage tests strict activation invariants, lifecycle metadata immutability during activation, conflict isolation, CLI read-only guarantees, trace completeness, failed condition reporting, and the unsupported multi-layer supersede chain boundary.

Conflict logic remains independent from supersede link. Priority, automatic conflict resolution, lifecycle write CLI, fallback search, and known / unknown failure_reason behavior changes remain unsupported.

Current order:
- v2.1b Strict Supersede Selection Activation：已完成
- v2.1c Activation Audit / Edge Case Hardening：本包
- Update log generation：下一步候選
- v2.2 Manual Review / Approval Gate or Activation Regression Suite：後續評估
## Activation Regression Suite

v2.2 adds a long-term activation regression suite.
No new activation capability is added, and strict activation conditions remain unchanged.

The suite protects the v2.1 strict supersede activation invariants before later Manual Review / Approval Gate work. Supersede link remains metadata, not authorization. Conflict logic remains independent from supersede relation. Lifecycle metadata remains immutable during activation. CLI lifecycle display remains read-only. Multi-layer supersede chain remains unsupported.

Manual Review / Approval Gate, review state, approval state, priority, automatic conflict resolution, automatic stale, lifecycle write CLI, fallback search, and known / unknown failure_reason behavior changes are not implemented in this package.

Current order:
- v2.1c Activation Audit / Edge Case Hardening：已完成
- v2.2 Activation Regression Suite：本包
- v2.2 Manual Review / Approval Gate：後續評估
## Manual Review State Foundation

v2.3a adds manual review state foundation.
Review metadata can record pending_review / reviewed and unreviewed / approved / rejected state, but it is metadata only.

Review metadata does not change selection behavior, does not change conflict behavior, and does not change strict supersede activation. Approval / rejection does not automatically select lessons, disable lessons, resolve conflicts, mark stale, or add priority. Lifecycle write CLI remains unsupported.

Current order:
- v2.2 Activation Regression Suite：已完成
- v2.3a Manual Review State Foundation：本包
- v2.3b Manual Review Persistence / Gate Design：後續評估
## Manual Review CLI Display

v2.3b adds read-only manual review CLI display.
`run-review-display` shows manual review items, review_state, approval_state, target metadata, lesson ids, reason, notes, and read-only review trace.

CLI display does not modify review metadata, does not modify lesson metadata, does not change selection behavior, does not change conflict behavior, and does not change strict supersede activation.

Test 5 / 6 / 7 are read-only guard tests for preventing future display side effects. CLI approve / reject, automatic conflict resolution, and priority are not implemented.

Current order:
- v2.3a Manual Review State Foundation：已完成
- v2.3b Manual Review CLI Display：本包
- v2.3c Manual Review Persistence or Gate Design：後續評估
## Manual Review Decision CLI

v2.3c adds metadata-only manual review decision CLI.
`run-review-approve` and `run-review-reject` update only review item metadata: review_state and approval_state, plus optional notes.

Approval does not change selection behavior. Rejection does not disable lessons. Review decisions do not change conflict behavior or strict supersede activation. Lesson lifecycle write CLI remains unsupported. Automatic conflict resolution and priority are not implemented.

Current order:
- v2.3b Manual Review CLI Display：已完成
- v2.3c Manual Review Decision CLI：本包
- v2.3d Manual Review Persistence or Gate Design：後續評估
## Manual Review Decision Audit / Regression

v2.3d is audit / regression only.
No new review capability is added.

Approve / reject remains metadata-only. Approval does not change selection behavior. Rejection does not disable lessons. Review decisions do not change conflict behavior or strict supersede activation. Lesson lifecycle write CLI remains unsupported.

Approval-driven behavior, rejection-driven behavior, automatic conflict resolution, and priority are not implemented.

Current order:
- v2.3c Manual Review Decision CLI：已完成
- v2.3d Manual Review Decision Audit / Regression：本包
- v2.4 Manual Review Persistence or Gate Design：後續評估
## Review-Gated Selection Eligibility

v2.4a adds review-gated selection eligibility.
Selection eligibility can read manual review metadata only for candidate lessons explicitly marked with `requires_review = true`.

Approved review may allow the review gate to pass. Rejected review blocks review-gated eligibility. `pending_review` / `unreviewed` / missing review do not pass the review gate.

Approval does not affect conflict behavior, does not affect strict supersede activation conditions, does not grant priority, and does not bypass normal selection eligibility. Rejection does not mark stale and does not disable lessons.

Batch review query, legacy `compatibility_approved` upgrade path, new review write CLI, automatic conflict resolution, and priority are not implemented in this package.

Current order:
- v2.3d Manual Review Decision Audit / Regression：已完成
- v2.4a Review-Gated Selection Eligibility：本包
- v2.4b Review Gate Regression / Audit：後續評估
## Review-Gated Eligibility Audit / Regression

v2.4b is audit / regression only.
No new review gate behavior is added.

The audit confirms that approved review only passes the review gate, does not grant priority, and does not bypass normal selection eligibility. Rejected review does not mark stale or disable lessons. Approval does not affect conflict behavior or strict supersede activation conditions.

Legacy lessons are not reclassified. `compatibility_approved` upgrade path, batch review query, new review write CLI, automatic conflict resolution, automatic stale, and priority are not implemented.

Current order:
- v2.4a Review-Gated Selection Eligibility：已完成
- v2.4b Review-Gated Eligibility Audit / Regression：本包
- v2.5 Review Gate Integration Planning：後續評估
## Conflict ID Stability Check

v2.4c confirms conflict id stability and adds deterministic `stable_conflict_key` when needed.
The stable key is generated from explicit deterministic conflict metadata and is intended only as a future matching anchor.

Conflict review resolution preview is not implemented. Review matching is not implemented. Notes / reason text matching and fallback search are prohibited. Stable key does not change conflict behavior, selection behavior, or strict supersede activation.

Current order:
- v2.4b Review-Gated Eligibility Audit / Regression：已完成
- v2.4c Conflict ID Stability Check：本包
- v2.5a Conflict Review Resolution Preview：後續評估
## Conflict Review Resolution Preview

v2.5a adds conflict review resolution preview.
The preview is trace-only and `resolution_preview_applied` remains false.

Approval does not resolve conflicts, approved candidate does not automatically win conflict, rejection does not disable lessons, and rejection does not mark stale. Preview does not change selection behavior or strict supersede activation.

Matching uses `stable_conflict_key` / explicit metadata only. Notes / reason text matching and fallback search are prohibited. Review-gated selection eligibility remains unchanged. Approval-driven and rejection-driven conflict resolution are not implemented.

Current order:
- v2.4c Conflict ID Stability Check：已完成
- v2.5a Conflict Review Resolution Preview：本包
- v2.5b Conflict Preview Audit / Regression：後續評估
## Conflict Review Preview Audit / Regression

v2.5b is audit / regression only.
No new conflict resolution capability is added.

Conflict review preview remains trace-only and `resolution_preview_applied` remains false. Approval does not resolve conflicts and approved candidate does not automatically win conflict. Rejection does not disable lessons and does not mark stale.

Matching uses `stable_conflict_key` / explicit metadata only. Notes / reason text matching is prohibited. Fallback search is prohibited. Runtime `conflict_id` cannot be the only matching anchor. Review-gated selection eligibility remains unchanged.

Approval-driven and rejection-driven conflict resolution are not implemented.

Current order:
- v2.5a Conflict Review Resolution Preview：已完成
- v2.5b Conflict Review Preview Audit / Regression：本包
- v2.6 Conflict Resolution Activation Design：後續評估
## Conflict Review Resolution Preconditions

v2.6a adds conflict review resolution preconditions.
This package does not perform dry-run and does not activate conflict resolution. `resolution_activation_applied` remains false.

Rejected reviews are blockers only: they do not disable lessons, mark stale, make candidates fail, or resolve conflict. Conflicting reviews and multiple approved candidates block resolution. Approval does not resolve conflicts and approved candidate does not automatically win conflict.

Matching uses `stable_conflict_key` / explicit metadata only. Notes / reason text matching and fallback search are prohibited. Runtime `conflict_id` cannot be the only matching anchor.

Current order:
- v2.5b Conflict Review Preview Audit / Regression：已完成
- v2.6a Conflict Review Resolution Preconditions：本包
- v2.6b Conflict Review Resolution Dry Run：後續評估
## Conflict Review Resolution Dry Run

v2.6b adds conflict review resolution dry-run.
This package does not activate conflict resolution.

Dry-run does not change conflict result, selection result, or strict supersede activation. `resolution_applied` remains false. Rejected reviews are blockers only and do not disable lessons or mark stale. Conflicting reviews and multiple approved candidates block dry-run resolution.

Approval does not resolve conflicts and approved candidate does not automatically win conflict. Matching uses `stable_conflict_key` / explicit metadata only. Notes / reason text matching and fallback search are prohibited. Runtime `conflict_id` cannot be the only matching anchor.

Current order:
- v2.6a Conflict Review Resolution Preconditions：已完成
- v2.6b Conflict Review Resolution Dry Run：本包
- v2.6c Conflict Review Dry Run Audit / Regression：後續評估
## Phase 0 Integration Assumption Docs

v2.6c-0 is docs / assumption integration.

This package adds the failure_reason design assumption v0.1 and the instinct / lesson layer relation assumption v0.1. It also adds a docs-only smoke check for the Phase 0 integration assumption documents.

The failure_reason assumption states that failure reasons should be derived from expected outcome vs actual outcome contrast, and that the result should be structured, traceable, and reviewable.

The instinct / lesson relation assumption states that the lesson layer remains traceable and reviewable, may assist or compete with future instinct / drive behavior, and may only become instinct-like through future familiarity-based internalization gates.

No runtime behavior changed. No activation behavior was added. No Phase 0 runtime integration was implemented. v2.6b dry-run remains completed, and v2.6c activation remains deferred.

## Phase 0 Behavior / Curiosity Assumption Docs

v2.6c-1 is docs-only behavior / curiosity assumption integration.

This package adds the Phase 0 minimal behavior set and curiosity design assumption v0.1. It documents why Qingyin acts, where motivation comes from, how curiosity is triggered, the minimal behavior set, and how curiosity may connect to the failure_reason / lesson_candidate loop.

The document records three motivation sources: external teaching motivation, instinct / curiosity motivation, and need motivation. It also records the minimal behavior names `observe`, `approach`, `avoid`, and `ask_for_help` as design assumptions only.

No runtime behavior changed. No curiosity runtime, attention weight runtime, motivation runtime, Phase 0 sandbox runtime, evaluator implementation, or perception implementation was added. Selection, conflict, review, activation, known / unknown failure_reason behavior, and v2.6b dry-run behavior remain unchanged.

## Phase 0 Failure Event Interface Assumption Docs

v2.6c-2 is docs-only.

This package adds the Phase 0 failure_event interface assumption doc. It defines the motivation -> goal -> action_intent -> expected_outcome -> actual_outcome -> evaluator -> failure_event -> failure_reason -> lesson_candidate chain.

The document states that Phase 0 should pass structured failure_event data into the lesson layer rather than raw natural language failure text.

No runtime behavior changed. No evaluator implementation was added. No Phase 0 sandbox runtime integration was implemented. No lesson_candidate builder runtime was implemented. v2.6c activation remains deferred.

## Perception and Lesson / Memory Relation Assumption Docs

v2.6c-3 is docs-only.

This package reconciles the missing perception assumption docs and adds the lesson / memory layer relation assumption doc.

The perception assumption describes how perception_input may become perceptual_features, perceptual_code, action_context, expected_outcome, actual_outcome, failure_reason, and lesson_candidate. It explicitly does not add perception runtime or visual input runtime.

The lesson / memory relation assumption states that lesson is action correction knowledge, while Long-term Memory is reviewed continuity memory. It defines learned_principle and lesson_to_memory_promotion as future assumption terms only.

No runtime behavior changed. No perception runtime, perceptual_code runtime, lesson_to_memory_promotion runtime, Long-term Memory write runtime, memory review runtime, or memory_contrast_set runtime was added. Selection, conflict, review, activation, and known / unknown failure_reason behavior remain unchanged. v2.6c activation remains deferred.

## Lesson / Memory Responsibility Boundary

v2.6c-4 clarifies the lesson_to_memory_promotion responsibility boundary and checks line ending status.

ASHL Core provides evidence. Qingyin Memory Layers decide memory admission.

ASHL Core may provide learned_principle_candidate and source evidence, but it does not directly write Long-term Memory. Long-term Memory admission remains the responsibility of Qingyin Memory Layers.

No runtime behavior changed. No lesson_to_memory_promotion runtime, Long-term Memory write runtime, memory review runtime, memory_contrast_set runtime, selection change, conflict change, review change, activation change, or known / unknown failure_reason behavior change was added. The line ending dirty state described in the work package was not reproduced in this checkout before edits; git status was clean.

## Phase 0 Assumption Consistency Audit

v2.6c-5 is docs-only / audit-only.

This package adds the Phase 0 assumption consistency audit doc. It checks failure_reason, failure_event, instinct / lesson, curiosity, similar-context, perception, and lesson / memory relation assumptions.

The audit result is PASS. No design contradiction was found among the current Phase 0 / Memory assumption docs.

No runtime behavior changed. No new runtime implementation was added. v2.6c activation remains deferred.

## Phase 0 Failure Event Schema Foundation

v2.7a adds Phase 0 failure_event schema foundation.

This package adds `ashl_core.failure_events`, `build_failure_event`, and `validate_failure_event`. Validation returns a structured trace that records whether a failure_event is valid, whether authoritative failure_reason is allowed, and why an event is valid, invalid, unclassified, or non-failure.

No Phase 0 sandbox runtime was implemented. No evaluator implementation was added. No lesson_candidate builder runtime was added. No conflict review resolution activation was added. v2.6c assumption docs remain the design source.

## v2.7b-0 Phase 0 Trust / Curiosity / Personality Boundary Docs

Status: docs-only.

Goal: Define boundary assumptions before Failure Event Normalization Trace and Failure Event to Lesson Candidate Input Bridge.

Scope:
- evaluator as observable evidence, not absolute truth
- evaluator error handled by human correction / user review
- no infinite evaluator reviewer chain
- failure_event review path placeholder: user_review / human_teacher_review, paired_subject_template_review, deferred_review
- curiosity_probe must be triggered by monitored event, not LLM-only declaration
- personality weight may auto-adjust but every adjustment must leave trace
- confirmation and trace are separate concerns

Non-goals:
- no runtime implementation
- no evaluator trust runtime
- no failure_event review runtime
- no paired subject runtime
- no curiosity runtime
- no personality weight runtime
- no lesson_candidate builder runtime
- no Long-term Memory write
- no selection / activation / conflict / review behavior changes

## v2.7b Failure Event Normalization Trace

Status: completed / trace-only.

Goal:
Create a deterministic trace-only normalized view for structured `failure_event`.

Scope:
- normalize structured `failure_event` fields into stable trace view
- preserve `evaluator_source`
- preserve `needs_review` / review boundary
- generate deterministic normalization key from structured fields
- ensure normalized view is not a new authority source

Non-goals:
- no sandbox runtime
- no evaluator runtime
- no failure_event review runtime
- no curiosity runtime
- no novelty runtime
- no personality weight runtime
- no lesson_candidate builder
- no Long-term Memory write
- no selection / activation / conflict behavior changes
- no LLM-only authoritative failure or novelty source

## v2.7c Failure Event to Lesson Candidate Input Bridge Trace-only

Status: completed / trace-only.

Goal:
Create a trace-only input bridge from normalized `failure_event` to lesson candidate input view.

Scope:
- build `lesson_candidate_input_trace` from normalized `failure_event`
- preserve `evaluator_source`
- preserve `needs_review` / `review_state`
- preserve authority boundary
- add `similar_context_hint` source / authority boundary
- keep `semantic_key` non-authoritative and review-required
- ensure bridge output is not `lesson_candidate`

Non-goals:
- no lesson_candidate builder runtime
- no lesson_store write
- no manual review runtime
- no sandbox runtime
- no evaluator runtime
- no curiosity / novelty runtime
- no personality weight runtime
- no Long-term Memory write
- no selection / activation / conflict behavior changes

## v2.7c-1 Failure Event Bridge Audit / Regression Hardening

Status: completed / audit-regression-only.

Goal:
Audit and harden the trace-only pipeline before defining lesson_candidate builder contract.

Scope:
- confirm bridge output is not lesson_candidate
- confirm bridge does not write lesson_store
- confirm needs_review is preserved
- confirm evaluator_source is preserved
- confirm semantic_key is non-authoritative and review-required
- confirm missing expected_outcome / actual_outcome cannot produce normalized_failure_event
- confirm LLM-only raw description cannot become authoritative failure_reason at bridge stage
- audit lesson_candidate_input_trace field source / authority boundaries
- include similar_context_hint audit in this package

Non-goals:
- no lesson_candidate builder runtime
- no lesson_store write
- no manual review runtime
- no sandbox runtime
- no evaluator runtime
- no curiosity / novelty runtime
- no personality weight runtime
- no Long-term Memory write
- no selection / activation / conflict behavior changes

## v2.7d Lesson Candidate Builder Contract Docs

Status: completed / docs-only / contract-only.

Goal:
Define the future lesson_candidate builder contract before runtime implementation.

Scope:
- define builder input from `lesson_candidate_input_trace`
- define field source / authority boundary
- define `semantic_key` as non-authoritative review-required hint
- define minimal builder output contract
- require builder output to remain review-gated
- preserve Long-term Memory responsibility boundary

Non-goals:
- no lesson_candidate builder runtime
- no lesson_candidate creation
- no lesson_store write
- no manual review runtime
- no sandbox runtime
- no evaluator runtime
- no selection / activation / conflict behavior changes
- no Long-term Memory write
- no learned_principle generation runtime
- no internalization

## v2.7d-1 Lesson Candidate Builder Contract Audit

Status: completed / docs-only / audit-only.

Goal:
Audit the lesson_candidate builder contract before defining lesson_candidate draft schema.

Scope:
- confirm builder output must remain review-gated
- confirm proposed_lesson_summary is not authoritative lesson
- confirm proposed_action_correction is not executable action
- confirm proposed_applicability_conditions are not verified applicability proof
- confirm evidence_refs are evidence pointers, not proof or approval
- confirm semantic_key remains non-authoritative and review-required
- confirm evaluator_source remains observable evidence, not absolute truth
- confirm Long-term Memory / learned_principle are not smuggled into builder output

Non-goals:
- no lesson_candidate builder runtime
- no build_lesson_candidate()
- no lesson_candidate draft schema implementation
- no lesson_store write
- no manual review runtime
- no sandbox runtime
- no evaluator runtime
- no selection / activation / conflict behavior changes
- no Long-term Memory write

## v2.7d-2 Lesson Candidate Builder Literature Reference Supplement

Status: completed / docs-only / reference-only

Goal:
Add literature references for future lesson_candidate builder implementation.

Scope:
- add CausalFlow as reference for causal failure attribution and counterfactual repair
- connect Causal Responsibility Score to failure_reason causal grounding
- connect Counterfactual Repair to future proposed_action_correction generation
- add LaGEA as structured feedback schema comparison
- use LaGEA suggested_fix as a negative reference for direct VLM-generated correction
- preserve existing docs-only / trace-only boundaries

Non-goals:
- no lesson_candidate builder runtime
- no proposed_action_correction runtime
- no counterfactual repair runtime
- no Causal Responsibility Score runtime
- no VLM feedback runtime
- no LLM / VLM authoritative failure_reason
- no LLM / VLM approved correction generation

## v2.8a Lesson Candidate Draft Schema Trace-only

Status: completed / trace-only.

Goal:
Define and test a trace-only lesson_candidate_draft schema.

Scope:
- build lesson_candidate_draft from lesson_candidate_input_trace
- require every draft field to declare source / authority / review_required
- reject TBD / unknown field sources
- keep draft review-gated
- keep draft not approved / not active / not selection eligible / not internalized
- prevent semantic_key from becoming proof or eligibility source
- prevent proposed_action_correction from becoming executable action
- prevent evidence_refs from becoming proof or approval

Non-goals:
- no lesson_candidate builder runtime
- no approved lesson_candidate creation
- no lesson_store write
- no manual review runtime
- no sandbox runtime
- no evaluator runtime
- no selection / activation / conflict behavior changes
- no Long-term Memory write
- no internalization

## v2.8a-1 Lesson Candidate Draft Schema Audit / Regression

Status: completed / audit-regression-only.

Goal:
Audit and harden the lesson_candidate_draft schema after v2.8a.

Scope:
- confirm draft is not approved / active / selection eligible / internalized
- confirm draft does not write lesson_store or Long-term Memory
- confirm every main field declares source / authority / review_required
- confirm every main field has review_required = true
- prevent review_required = false without explicit reviewed authority path
- confirm semantic_key is not proof or eligibility source
- confirm evidence_refs are not proof or approval
- confirm proposed_action_correction is not executable action
- confirm proposed_applicability_conditions are not verified applicability proof
- confirm non-bridge input cannot produce draft

Non-goals:
- no lesson_candidate builder runtime
- no approved lesson_candidate creation
- no lesson_store write
- no manual review runtime
- no sandbox runtime
- no evaluator runtime
- no selection / activation / conflict behavior changes
- no Long-term Memory write
- no internalization

## v2.8a-2 Lesson Candidate Draft Strict Schema / Injection Guard

Status: completed / guard-hardening.

Goal:
Harden lesson_candidate_draft schema against injection, missing authority fields, all-null outcomes, and LLM-generated draft JSON.

Scope:
- forbid extra schema fields
- require review_required to behave as Literal[True]
- prevent authority_boundary injection / override
- prevent review_required false override
- reject or guard missing authority-critical fields
- ensure expected_outcome and actual_outcome both null / unknown are invalid for failure learning
- mark unknown / not_available core evidence as insufficient_evidence
- prevent unknown evidence from generating actionable correction
- prohibit LLM from directly writing draft JSON
- keep draft not approved / not active / not selection eligible

Non-goals:
- no lesson_candidate builder runtime
- no approved lesson_candidate creation
- no lesson_store write
- no manual review runtime
- no sandbox runtime
- no evaluator runtime
- no selection / activation / conflict behavior changes
- no Long-term Memory write
- no internalization

## v2.8a-3 Outcome Unknown Payload / Draft Invariant Guard

Status: completed / guard-hardening.

Goal:
Harden the failure_event and lesson_candidate_draft path against typed unknown outcome payloads and draft invariant drift.

Scope:
- treat outcome type as a container label, not usable evidence
- treat expected_outcome / actual_outcome with unknown, not_available, missing, or null status as unknown even when type exists
- block unknown vs unknown from becoming valid failure learning evidence
- prevent invalid typed unknown outcome traces from producing bridge / draft output
- validate top-level lesson_candidate_draft trace invariants
- require insufficient_evidence to imply not_approvable
- keep unknown / not_available core evidence non-actionable and human-diagnosis-required
- add LF line ending policy for common source and documentation files

Non-goals:
- no lesson_candidate builder runtime
- no approved lesson_candidate creation
- no lesson_store write
- no review queue runtime
- no manual_review runtime
- no sandbox runtime
- no evaluator runtime
- no selection / activation / conflict / review behavior changes
- no Long-term Memory write
- no Memory Layer write
- no familiarity score, internalization gate, or instinct-like behavior layer

## v2.8b Lesson Candidate Draft Review Queue Contract Docs

Status: completed / docs-only / contract-only.

Goal:
Define review_queue_entry / review_task contract for lesson_candidate_draft without implementing review runtime.

Scope:
- define review_queue_entry as queue marker, not review decision
- define review_task as to-do item, not review decision
- clarify review_task completion does not imply approval
- ensure queue can reference draft but cannot mutate draft
- prohibit queue from changing review_required / approved / active / selection_eligible state
- require no selection-facing read APIs
- prohibit unreviewed drafts from being archived into any Memory Layer
- define semantic_key presentation boundary to avoid authority anchoring

Non-goals:
- no review queue runtime
- no review_task runtime
- no manual_review runtime
- no review decision creation
- no approved lesson_candidate creation
- no lesson_store write
- no selection / activation / conflict behavior changes
- no Long-term Memory write
- no Memory Layer write

## v2.8b-1 Review Queue Contract Audit / Regression

Status: completed / docs-only / audit-only.

Goal:
Audit and harden the review queue contract before review_task schema work.

Scope:
- confirm review_queue_entry is not review decision
- confirm review_task is not review decision
- confirm review_task completion does not imply approval
- confirm queue can reference draft but cannot mutate draft
- confirm no selection-facing read APIs
- confirm metrics APIs expose integer counts only
- confirm metrics APIs do not expose draft content or keys
- confirm timeout / expired drafts do not enter any Memory Layer
- confirm expired draft debug logs contain identity and time only, not proposed fields
- confirm semantic_key display level remains lower than source_failure_norm_key

Non-goals:
- no review queue runtime
- no review_task runtime
- no manual_review runtime
- no review decision creation
- no approved lesson_candidate creation
- no lesson_store write
- no Memory Layer write
- no selection / activation / conflict behavior changes

## v2.8c Review Task Trace-only Schema

Status: completed / trace-only.

Goal:
Define trace-only review_task schema without implementing manual review runtime.

Scope:
- define review_task_trace as trace-only to-do record
- ensure review_task_trace is not review decision
- ensure review_task completion does not imply approval
- define reviewer_identity source boundary
- prohibit LLM-generated reviewer_identity
- keep semantic_key as secondary optional hint
- ensure semantic_key display level is lower than source_failure_norm_key
- keep review_task_trace isolated from selection/action/runtime contexts
- prevent lesson_store and Memory Layer writes

Non-goals:
- no manual_review runtime
- no review decision creation
- no approved / rejected / deferred review result
- no approved lesson_candidate creation
- no lesson_store write
- no review queue runtime expansion
- no draft mutation
- no selection / activation / conflict / review behavior changes
- no Long-term Memory write
- no Memory Layer write

## v2.8c-1 Review Task Audit / Regression

Status: completed / audit-regression-only.

Goal:
Audit and harden review_task_trace after v2.8c.

Scope:
- confirm review_task_trace is not review decision
- confirm completion / closed / done does not imply approval
- confirm reviewer_identity cannot be injected from LLM / queue / draft input
- confirm reviewer_identity_context source restrictions
- confirm semantic_key remains secondary optional hint
- confirm source_failure_norm_key outranks semantic_key
- confirm injected review decision fields do not affect output
- confirm no selection-facing read APIs
- confirm review_task_trace does not enter memory_contrast_set
- record future rejected / deferred proposed fields masking boundary

Non-goals:
- no manual_review runtime
- no review decision creation
- no approved / rejected / deferred review result runtime
- no approved lesson_candidate creation
- no lesson_store write
- no Memory Layer write
- no selection / activation / conflict behavior changes
- no rejected / deferred proposed fields masking runtime

## v2.8d Review Decision Contract Docs

Status: completed / docs-only / contract-only.

Goal:
Define review_decision contract before any review decision runtime exists.

Scope:
- define review_decision as historical event record, not live lesson object
- define decision_status as approved / rejected / deferred only
- separate review_task completion from review_decision creation
- ensure approved does not create active lesson
- ensure approved does not grant lesson_store write permission
- ensure approved does not grant selection eligibility
- define rejected / deferred proposed fields masking boundary
- define deferred as not soft approval
- record decision_authority / reviewer_identity / reviewer_session binding as future runtime boundary
- prohibit decision fields from implying runtime permission, activation, selection, bypass, or override

Non-goals:
- no manual_review runtime
- no review decision runtime
- no review decision creation helper
- no approved / rejected / deferred result runtime
- no lesson_candidate creation
- no lesson_store write
- no Memory Layer write
- no selection / activation / conflict behavior changes
- no partial approval
- no rejected / deferred proposed fields masking runtime

## v2.8d-1 Review Decision Contract Audit / Regression

Status: completed / docs-only / audit-regression-only.

Goal:
Audit and harden the review_decision contract before masking and identity binding docs.

Scope:
- confirm review_decision is historical event record, not live lesson object
- confirm approved does not create active lesson
- confirm approved does not grant lesson_store write permission
- confirm approved does not directly grant selection eligibility
- confirm Review Decision service is zero-permission to lesson_store
- confirm rejected / deferred proposed fields masking boundary
- confirm deferred is not soft approval
- confirm partial / conditional approval is not allowed
- confirm decision fields do not imply runtime permission / activation / override
- confirm review_task completion is not review_decision creation
- confirm decision_status is the only review verdict field

Non-goals:
- no manual_review runtime
- no review decision runtime
- no approved / rejected / deferred result runtime
- no lesson_candidate creation
- no lesson_store write
- no Memory Layer write
- no selection / activation / conflict behavior changes
- no masking runtime
- no identity / session binding runtime

## v2.8d-2 Rejected / Deferred Proposed Fields Masking Contract Docs

Status: completed / docs-only / contract-only.

Goal:
Define the masking boundary for proposed fields after rejected / deferred review decisions.

Scope:
- define rejected / deferred proposed fields must be masked from evaluator and memory_contrast_set reads
- define fields that must be masked
- define safe fields that may remain visible
- define allowed masking representations
- prohibit debug logs from preserving proposed field content
- confirm deferred is not soft approval
- confirm masking cannot be bypassed by task_completed / reason / priority / manual_note

Non-goals:
- no masking runtime
- no review decision runtime
- no manual_review runtime
- no evaluator runtime changes
- no memory_contrast_set runtime changes
- no approved / rejected / deferred result runtime
- no lesson_store write
- no Memory Layer write
- no selection / activation / conflict behavior changes

## v2.8e-1 Review Decision Trace Audit / Regression

Status: completed / audit-regression-only

Goal:
Audit and harden review_decision_trace after v2.8e.

Scope:
- confirm approved trace grants no runtime permission
- confirm approved trace grants no lesson_store write permission
- confirm approved trace grants no selection eligibility or activation
- confirm rejected / deferred traces contain no reusable proposed content
- confirm masked_fields_summary contains field names only
- confirm rejected / deferred traces require masking_policy_ref
- confirm all decision traces require authority_binding_policy_ref
- confirm partial / conditional approval is rejected
- confirm review_task completion cannot create review_decision_trace
- record future runtime selector trace isolation boundary
- record future authority / identity / session binding runtime boundary

Non-goals:
- no manual_review runtime
- no review decision runtime
- no approved / rejected / deferred result runtime
- no approved lesson_candidate creation
- no lesson_store write
- no Memory Layer write
- no selection / activation / conflict behavior changes
- no masking runtime
- no auth/session runtime
- no runtime selector implementation

## v2.8f Review Decision Trace Integration Boundary Docs

Status:
docs-only / boundary-integration / review-trace-audit

Summary:
Integrates review_decision_trace, sandbox trace, and voice output trace boundaries.
Confirms trace is evidence, not approval; record, not authorization; audit material, not runtime action.
Clarifies review_decision_trace must not activate lessons, grant selection eligibility, authorize runtime behavior, write to lesson_store, or write to Memory Layer.
Records bidirectional voice interaction as deferred until consultant review.

Boundary:
- No runtime.
- No review decision runtime.
- No selection eligibility runtime.
- No activation runtime.
- No lesson_store write.
- No Memory Layer write.
- No sandbox runtime.
- No Audio Sense / STT / TTS / voice trigger / voice input-output loop.

Non-goals:
- no runtime
- no review decision runtime
- no selection eligibility runtime
- no activation runtime
- no lesson_store write
- no Memory Layer write
- no sandbox runtime
- no voice instinct runtime
- no Audio Sense runtime
- no STT runtime
- no TTS runtime
- no voice trigger runtime
- no voice input-output loop
- no voice output runner
- no audio input runner
- no tool permission runtime
- no review / lesson / selection / activation / conflict behavior changes

## Formal Lesson Candidate Creation Contract Docs

Status:
docs-only / contract-only / formal-lesson-candidate-boundary

Summary:
Defines the future contract for formal lesson_candidate creation.
Clarifies creation requires structured evidence, validated boundaries, and review-ready trace.
Clarifies formal lesson_candidate creation is not approval, lesson_store write, activation, selection eligibility, or Memory Layer promotion.
Clarifies sandbox trace and voice output trace may support creation only as evidence.

Boundary:
- No formal lesson_candidate creation runtime.
- No automatic lesson_candidate builder.
- No lesson_store write.
- No Memory Layer write.
- No activation runtime.
- No selection eligibility runtime.
- No sandbox runtime.
- No voice / audio runtime.

Non-goals:
- no formal lesson_candidate creation runtime
- no formal lesson_candidate schema runtime
- no automatic lesson_candidate builder
- no failure_event automatic builder runtime
- no evaluator runtime
- no lesson_store write
- no Memory Layer write
- no Long-term Memory write runtime
- no review decision runtime
- no selection eligibility runtime
- no activation runtime
- no sandbox runtime
- no voice instinct runtime
- no Audio Sense / STT / TTS runtime
- no voice trigger runtime
- no voice input-output loop
- no review / lesson / selection / activation / conflict behavior changes

## Formal Lesson Candidate Creation Boundary Audit Docs

Status:
docs-only / audit-only / formal-lesson-candidate-boundary

Summary:
Audits the formal lesson_candidate creation contract against failure_event validation, lesson_candidate_input_trace, review gate, lesson_store, Memory Layer, selection eligibility, activation, sandbox trace, voice output trace, and review_decision_trace boundaries.
Confirms the contract does not authorize runtime, builders, lesson_store write, Memory Layer write, activation, selection eligibility, or direct creation from raw natural language / LLM-only explanation / sandbox trace / voice output trace / review_decision_trace.

Audit result:
PASS

Boundary:
- No formal lesson_candidate creation runtime.
- No automatic lesson_candidate builder.
- No lesson_store write.
- No Memory Layer write.
- No activation runtime.
- No selection eligibility runtime.
- No sandbox runtime.
- No voice / audio runtime.

Non-goals:
- no formal lesson_candidate creation runtime
- no formal lesson_candidate schema runtime
- no automatic lesson_candidate builder
- no failure_event automatic builder runtime
- no evaluator runtime
- no lesson_store write
- no Memory Layer write
- no Long-term Memory write runtime
- no review decision runtime
- no selection eligibility runtime
- no activation runtime
- no sandbox runtime
- no voice instinct runtime
- no Audio Sense / STT / TTS runtime
- no voice trigger runtime
- no voice input-output loop
- no review / lesson / selection / activation / conflict behavior changes

## Current Boundary Index Docs

Status:
docs-only / boundary-index / no-runtime-expansion

Summary:
Adds docs/current_boundary_index.md as a short, versioned, low-token source of global hard boundaries for future work packages.
Defines that the boundary index must be updated every time an Update Log is generated.
Future work packages must check the first-line Boundary Index Version before starting.

Boundary:
- No runtime.
- No existing design document content changes.
- No new boundary design decisions.
- No package-specific prohibitions added to the index.

Non-goals:
- no runtime
- no changes to existing detailed boundary docs
- no new boundary decisions beyond the indexed current global hard boundaries
- no v2.11a Unknown Expected / Actual System Fault Patch
- no required field strict validation patch
- no Memory Layer freeze notice
- no formal lesson_candidate positive spec
- no pipeline transition docs
- no sandbox allowed_action_set Gmod deferral

## Current Boundary Index Batch 18 Sync Patch

Status:
docs-only / boundary-index-sync / update-log-sync / no-runtime-expansion

Summary:
Updates docs/current_boundary_index.md from Batch 17 to Batch 18.
Adds Batch 18 hard boundaries for Qingyin non-LLM first_output, runtime ontology, memory freeze notice evidence-only, unknown expected/actual system_fault, and required field strict validation.

Boundary:
- No runtime.
- No new design document.
- No existing runtime behavior changes.
- No package-specific prohibitions added to the index.

Non-goals:
- no runtime
- no first_output generator
- no state store
- no first_output trace schema runtime
- no bounded senses runtime
- no Screen Sense / Camera Sense runtime
- no Symbol Grounding runtime
- no LLM response generation
- no teaching chat loop
- no mentor feedback runtime
- no lesson_candidate pipeline connection
- no lesson_store write
- no Memory Layer write
- no review / lesson / selection / activation / conflict behavior changes

## Current Boundary Index Batch 19 Sync Patch

Status:
docs-only / boundary-index-sync / update-log-sync / no-runtime-expansion

Summary:
Updates docs/current_boundary_index.md from Batch 18 to Batch 19.
Adds Batch 19 hard boundaries for Qingyin test-object / shallow-sleep / awakening ontology and first_output_trace evidence boundaries.

Boundary:
- No runtime.
- No new design document.
- No existing runtime behavior changes.
- No package-specific prohibitions added to the index.

## Current Boundary Index Batch 20 Sync Patch

Status:
docs-only / boundary-index-sync / update-log-sync / no-runtime-expansion

Summary:
Updates docs/current_boundary_index.md from Batch 19 to Batch 20.
Adds Batch 20 hard boundaries for Minimal First Output Runtime v0 and Mentor Feedback Stub Contract.

Boundary:
- No runtime.
- No new design document.
- No existing runtime behavior changes.
- No package-specific prohibitions added to the index.

## Current Boundary Index Batch 21 Sync Patch

Status:
docs-only / boundary-index-sync / update-log-sync / no-runtime-expansion

Summary:
Updates docs/current_boundary_index.md from Batch 20 to Batch 21.
Adds Batch 21 hard boundaries for mentor_feedback_trace, Minimal Mentor Feedback Stub Runtime v0, and the first minimal interaction loop.

Boundary:
- No runtime.
- No new design document.
- No existing runtime behavior changes.
- No package-specific prohibitions added to the index.

## Current Boundary Index Batch 22 Sync Patch

Status:
docs-only / boundary-index-sync / update-log-sync / no-runtime-expansion

Summary:
Updates docs/current_boundary_index.md from Batch 21 to Batch 22.
Adds Batch 22 hard boundaries for Minimal Interaction CLI Bridge v0 and First Output + Mentor Feedback append-only persistence.

Boundary:
- No runtime.
- No CLI behavior changes.
- No JSONL persistence.
- No lesson_store write.
- No Memory Layer write.
- No lesson_candidate pipeline connection.
- No new design document.

## Current Boundary Index Batch 23 Sync Patch

Status:
docs-only / boundary-index-sync / update-log-sync / no-runtime-expansion

Summary:
Updates docs/current_boundary_index.md from Batch 22 to Batch 23.
Adds Batch 23 hard boundaries for append-only JSONL trace persistence, fixed non-LLM utterance_map output, literal text encoding, and the micro push-box tactile sandbox.

Boundary:
- No runtime.
- No JSONL persistence behavior changes.
- No utterance_map behavior changes.
- No micro push-box sandbox behavior changes.
- No lesson_store write.
- No Memory Layer write.
- No lesson_candidate pipeline connection.
- No LLM / teaching chat loop / free text conversation.
- No senses runtime / Screen Sense / Camera Sense / Symbol Grounding.
- No new design document.

## Current Boundary Index Batch 24 Sync Patch

Status:
docs-only / boundary-index-sync / update-log-sync / no-runtime-expansion

Summary:
Updates docs/current_boundary_index.md from Batch 23 to Batch 24.
Adds Batch 24 hard boundaries for the closed micro push-box allowed_action_set, fixed tactile result to state_key mapping, and deterministic tactile interaction CLI bridge.
Marks tactile trace persistence, autonomous action selection, repeated failure adaptation, and downstream learning connections as deferred.

Boundary:
- No runtime.
- No sandbox behavior changes.
- No tactile mapping behavior changes.
- No CLI behavior changes.
- No lesson_store write.
- No Memory Layer write.
- No lesson_candidate pipeline connection.
- No LLM / teaching chat loop / free text conversation.
- No senses runtime / Screen Sense / Camera Sense / Symbol Grounding.
- No new design document.

## Current Boundary Index Batch 25 Sync Patch

Status:
docs-only / boundary-index-sync / update-log-sync / no-runtime-expansion

Summary:
Updates docs/current_boundary_index.md from Batch 24 to Batch 25.
Adds Batch 25 hard boundaries for repeated blocked action trace readback, repeated blocked action avoidance as candidate bias, grounded learning verification CLI as human-verifiable trace flow, sandbox working-state clear preservation, and suggested_next_action as candidate suggestion.
Marks intrinsic action selection runtime, action outcome weighting runtime integration, autonomous goal planning, full learning pipeline, and downstream learning connections as deferred.

Boundary:
- No runtime.
- No sandbox behavior changes.
- No CLI behavior changes.
- No action weighting behavior changes.
- No lesson_store write.
- No Memory Layer write.
- No lesson_candidate pipeline connection.
- No LLM / teaching chat loop / free text conversation.
- No autonomous behavior changes.

## Current Boundary Index Batch 27 Sync Patch

Status:
completed / docs-only / boundary-index-sync / no-runtime

Summary:
Updates docs/current_boundary_index.md from Batch 26 to Batch 27.
Adds Batch 27 hard boundaries for need-state trial runner measurement, need-state trial batch step counts, and distance-based goal direction bias.
Marks goal direction bias integration into trial runner, stable trial metrics comparison, stuck detection / repetition penalty, autonomous goal planning, full learning pipeline, lesson_candidate pipeline connection, lesson_store write, Memory Layer write, LLM response generation, teaching chat loop, and free text conversation as deferred.

Boundary:
No runtime behavior changes.
No sandbox behavior changes.
No CLI behavior changes.
No need-state or goal-bias behavior changes.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No AI solver / pathfinding.
- No new design document.

## Current Boundary Index Batch 28 Sync Patch

Status:
completed / docs-only / boundary-index-sync / no-runtime

Summary:
Updates docs/current_boundary_index.md from Batch 27 to Batch 28.
Adds Batch 28 hard boundaries for state-action outcome memory as local session memory, context-bound reuse, trial metrics comparison as measurement-only, and human_summary as report text rather than Qingyin utterance.
Marks stuck detection / repetition penalty runtime, stable metrics comparison across fixed seeds, automatic behavior modification from metrics, persistent state-action memory, full learning pipeline, lesson_candidate pipeline connection, lesson_store write, Memory Layer write, LLM response generation, teaching chat loop, and free text conversation as deferred.

Boundary:
No runtime behavior changes.
No sandbox behavior changes.
No CLI behavior changes.
No trial runner / metrics behavior changes.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No AI solver / pathfinding.

## Current Boundary Index Batch 29 Sync Patch

Status:
completed / docs-only / boundary-index-sync / no-runtime

Summary:
Updates docs/current_boundary_index.md from Batch 28 to Batch 29.
Adds Batch 29 hard boundaries for micro navigation goal-reach as curriculum level, multi-goal navigation as sequential marker following, multi-goal traces as evidence rather than pathfinding, stuck detection / repetition penalty as not-yet-proven improvement, and push-box full solve as deferred.
Marks micro navigation multi-goal metrics CLI, obstacle / wall detour navigation level, approach-box level, push-box full solve, stable navigation curriculum metrics, lesson_candidate pipeline connection, lesson_store write, Memory Layer write, LLM response generation, teaching chat loop, and free text conversation as deferred.

Boundary:
No runtime behavior changes.
No navigation sandbox logic changes.
No push-box sandbox logic changes.
No CLI behavior changes.
No lesson_store or Memory Layer changes.
No lesson_candidate pipeline changes.
No AI solver / pathfinding.

## Current Boundary Index Batch 30 Sync Patch

Status:
completed / docs-only / boundary-index-sync / no-runtime

Summary:
Updates docs/current_boundary_index.md from Batch 29 to Batch 30.
Adds Batch 30 hard boundaries for approach-box as object-approach verification, not push behavior or box understanding.
Records the Two-Trial History Boundary: future Trial 2 may read only local state-action outcome memory with agent_pos, box_pos, optional goal_pos, action, result, and tick.
Marks Approach Box Trial CLI, Approach Box Two-Trial Learning Check, Trial Metrics Baseline Snapshot, Push Once Level, push-box full solve, lesson_candidate pipeline connection, lesson_store write, Memory Layer write, LLM response generation, teaching chat loop, and free text conversation as deferred.

Boundary:
No runtime behavior changes.
No navigation sandbox logic changes.
No push-box sandbox logic changes.
No CLI behavior changes.
No lesson_store or Memory Layer changes.
No lesson_candidate pipeline changes.
No LLM / teaching chat / free text conversation.
No AI solver / pathfinding.

## Current Boundary Index Compression Patch

Status:
docs-only / boundary-index-compression / no-batch-sync / no-runtime-expansion

Summary:
Compresses docs/current_boundary_index.md while preserving Boundary Index Version: 2026-06-06-b25.
Aggregates repeated hard boundaries and deferred areas into shorter umbrella lines to keep the index below the 150-line limit and leave room for future sync packages.
Does not add new boundaries and does not change runtime behavior.

Boundary:
- No new boundary.
- No b26 update.
- No Batch sync.
- No runtime.
- No sandbox / CLI / weighting / need_state behavior changes.
- No Update Rule removal.

## Current Boundary Index Batch 26 Sync Patch

Status:
docs-only / boundary-index-sync / update-log-sync / no-runtime-expansion

Summary:
Updates docs/current_boundary_index.md from Batch 25 to Batch 26.
Adds Batch 26 hard boundaries for outcome weighting as action candidate bias, intrinsic action selection as bounded candidate selection within candidate_actions, bounded randomness limited to candidate_actions, and box_on_goal need_state as target-state tracking rather than emotion / dopamine.
Marks need-state driven action loop, automatic trial improvement, long-term learning, autonomous goal planning, full learning pipeline, lesson_candidate pipeline connection, lesson_store write, Memory Layer write, emotion / dopamine runtime, and open language interfaces as deferred.

Boundary:
- No runtime.
- No sandbox behavior changes.
- No CLI behavior changes.
- No action weighting / intrinsic selection / need_state behavior changes.
- No lesson_store write.
- No Memory Layer write.
- No lesson_candidate pipeline connection.
- No LLM / teaching chat loop / free text conversation.
- No emotion / dopamine runtime.
- No autonomous behavior changes.

## v2.8e Review Decision Trace-only Schema

Status: completed / trace-only

Goal:
Define trace-only review_decision_trace schema after review decision contract, masking contract, and authority binding contract.

Scope:
- define review_decision_trace as trace-only historical event record
- support decision_status approved / rejected / deferred only
- prohibit partial / conditional approval
- ensure approved grants no lesson_store write / activation / selection eligibility
- require rejected / deferred masking policy ref
- require masked_fields_summary to contain field names only
- require decision authority / reviewer identity / session binding refs
- prohibit runtime permission / activation / override fields
- separate review_task completion from decision creation

Non-goals:
- no manual_review runtime
- no review decision runtime
- no approved / rejected / deferred result runtime
- no approved lesson_candidate creation
- no lesson_store write
- no Memory Layer write
- no selection / activation / conflict behavior changes
- no masking runtime
- no auth/session runtime

## v2.8d-3 Decision Authority / Reviewer Identity / Session Binding Contract Docs

Status: completed / docs-only / contract-only

Goal:
Define decision_authority / reviewer_identity / reviewer_session_token binding before review_decision_trace schema.

Scope:
- define decision_authority as review verdict authority only
- define reviewer_identity source boundary
- define reviewer_session_token source boundary
- require decision_authority / reviewer_identity / reviewer_session_token binding before runtime decision creation
- prohibit LLM / draft / queue / external text identity injection
- prohibit free-text decision_authority
- clarify authority does not grant lesson_store write / activation / selection eligibility / override permission

Non-goals:
- no auth runtime
- no session runtime
- no manual_review runtime
- no review decision runtime
- no identity verification runtime
- no approved / rejected / deferred result runtime
- no lesson_store write
- no Memory Layer write
- no selection / activation / conflict behavior changes

## Memory Compression Strategy Assumption Patch Index

Status: completed / docs-only / assumption-index

Goal:
Index memory compression strategy assumptions into Phase 0 / Memory Economy docs.

Scope:
- define text-stage memory compression unit
- require text fragment / source context summary / confidence level / usage count to be preserved
- clarify that detail can be compressed but provenance and confidence context cannot be dropped
- mark the strategy as text-memory-stage-only
- defer image memory compression until visual sensory grounding exists
- prohibit applying text-only compression strategy to image memory
- defer text / image relational compression until Symbol Grounding v1

Non-goals:
- no memory compression runtime
- no text memory compression runtime
- no image memory compression runtime
- no multimodal compression schema
- no Symbol Grounding runtime
- no Memory Layer behavior changes
- no lesson_store write
- no Memory Economy runtime

## v2.9b Soft / Hard Consolidation Assumption Index

Status: completed / docs-only / assumption-index

Goal:
Index soft / hard consolidation assumptions into Phase 0 docs.

Scope:
- define soft consolidation as reversible, trace-preserving, Qingyin-proposable adjustment
- define hard consolidation as externally confirmed, versioned, high-cost boundary change
- define Core Seed as current hard-consolidated layer
- define target-directed reasoning risk around review bypass
- require Core Seed / review flow / self-modification boundary / soft-hard boundary definition to be hard-consolidated
- state that Qingyin may propose hard consolidation but cannot complete it alone
- record that some consolidation paths must be physically unreachable, not merely discouraged

Non-goals:
- no soft consolidation runtime
- no hard consolidation runtime
- no Core Seed update runtime
- no review bypass runtime
- no self-modification runtime
- no Memory Economy runtime
- no lesson_store write
- no Memory Layer write
- no selection / activation / conflict behavior changes

## Qingyin First Output Runtime Minimal Spec Docs

Status: completed / docs-only / runtime-minimal-spec / first-output / no-runtime-implementation

Goal:
Define the minimal future runtime requirements for Qingyin first_output.

Summary:
Defines first_output must be generated without LLM output.
Clarifies first_output is a runtime milestone, not awakening, dialogue ability, or long-term growth.
Defines minimum input, state, allowed output sources, prohibited output sources, first_output trace fields, and bounded randomness boundaries.
Defines future acceptance criteria for first_output runtime.
Clarifies first_output must be traceable before it can become learning material; lesson_candidate pipeline remains downstream.

Boundary:
- No runtime.
- No first_output generator.
- No LLM response generation.
- No state store.
- No first_output trace schema runtime.
- No mentor feedback runtime.
- No lesson_candidate pipeline connection.
- No Audio Sense / STT / TTS / voice loop.

Non-goals:
- no deterministic seed runtime
- no bounded randomness runtime
- no teaching chat loop
- no lesson_store write
- no Memory Layer write

## First Output Trace Contract Docs

Status:
docs-only / trace-contract / first-output / no-runtime-implementation

Summary:
Defines the future `first_output_trace` contract.
Clarifies `first_output_trace` is evidence of a first_output event, not proof of awakening, dialogue ability, or long-term growth.
Defines required fields, append-only / version-preserving boundary, `llm_used = false`, `output_generator_source` boundaries, bounded randomness trace requirements, and downstream relationship to mentor feedback and lesson_candidate input consideration.

Boundary:
- No runtime.
- No first_output generator.
- No state store.
- No first_output trace schema runtime.
- No deterministic seed runtime.
- No bounded randomness runtime.
- No LLM response generation.
- No teaching chat loop.
- No mentor feedback runtime.
- No lesson_candidate pipeline connection.
- No failure_event automatic builder.
- No lesson_candidate automatic builder.
- No Audio Sense / STT / TTS / voice loop.
- No lesson_store write.
- No Memory Layer write.
- No review / lesson / selection / activation / conflict behavior changes.

## First Output Runtime Readiness Checklist Docs

Status:
docs-only / readiness-checklist / first-output / no-runtime-implementation

Summary:
Adds a readiness checklist for planning Minimal First Output Runtime v0.
Confirms first_output non-LLM source boundaries, trace contract, `llm_used = false`, test-object engineering boundary, no lesson_store write, no Memory Layer write, no lesson_candidate pipeline connection, no mentor feedback runtime, and no awakening claim.

Readiness result:
READY_FOR_MINIMAL_FIRST_OUTPUT_RUNTIME_V0

Boundary:
- No runtime.
- No first_output generator.
- No state store.
- No trace schema runtime.
- No mentor feedback runtime.
- No lesson_candidate pipeline connection.
- No lesson_store write.
- No Memory Layer write.
- No bounded senses runtime.

## Minimal First Output Runtime v0

Status:
minimal-runtime / first-output / test-object-stage / no-LLM / no-learning

Summary:
Adds a minimal non-LLM first_output runtime.
Generates a single fixed-reflex symbolic output and first_output_trace.
Records `llm_used=false`, `phase=test_object`, and `engineering_stage=test_object`.
Does not write lesson_store or Memory Layer.
Does not connect to mentor feedback, failure_event, lesson_candidate, review, selection, activation, or bounded senses.

Boundary:
- No LLM.
- No dialogue.
- No awakening claim.
- No lesson_candidate pipeline connection.
- No lesson_store write.
- No Memory Layer write.

## Minimal Non-LLM Utterance Map v0

Status:
minimal-runtime / non-llm-utterance-map / first-output / no-learning

Summary:
Adds a fixed non-LLM state_key to utterance map to the minimal first_output runtime.
Default state_key None still produces first_output `*`.
Supported state keys are unknown, blocked, observed, retry, and quiet.
Current utterances are `unknown -> 我不知道`, `blocked -> 不行`, `observed -> 看到了`, `retry -> 再一次`, and `quiet -> ……`.
Mapped output traces record `utterance_source=utterance_map`, `state_key`, and `llm_used=false`.
The minimal interaction CLI accepts `--state-key unknown`; with `--persist`, the persisted JSONL trace preserves the utterance map metadata.

Boundary:
No LLM / prompt / API.
No dialogue capability.
No teaching chat loop.
No rule engine.
No grammar parser.
No NLP inference.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No awakening evidence.

## Micro Push-Box Tactile Sandbox v0

Status:
minimal-runtime / tactile-sandbox / deterministic-grid / no-learning

Summary:
Adds a tiny deterministic 2D tactile sandbox with one agent, one box, one goal, walls, empty cells, and tactile traces.
The initial map is `##### / #...# / #.QB# / #..G# / #####`.
The sandbox tracks grid, agent_pos, box_pos, goal_pos, and tick.
Supported actions are touch, move, and push in four directions, plus wait.
Each action emits a `tactile_sandbox_trace` with before / after state, contact, result, blocked, agent_pos, box_pos, and goal_pos.

Boundary:
No AI solver.
No pathfinding.
No learning.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM / teaching chat loop / free text conversation.
No graphics / pygame / GUI.
No senses runtime / camera / screen.
No awakening evidence.

## Micro Push-Box Allowed Action Set v0

Status:
minimal-runtime / tactile-sandbox / fixed-action-set / deterministic-wait / no-parser

Summary:
Defines the explicit `ALLOWED_ACTION_SET` for the micro push-box sandbox.
The allowed set contains 13 actions: touch_up/down/left/right, move_up/down/left/right, push_up/down/left/right, and wait.
Adds `validate_allowed_action(...)` so invalid actions raise ValueError before sandbox execution.
Adds `wait` as a deterministic action that increments tick, does not move the agent or box, returns result `wait`, contact `none`, blocked false, and trace_type `tactile_sandbox_trace`.

Boundary:
No AI solver.
No pathfinding.
No learning.
No tactile result mapping changes.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM / teaching chat loop / free text conversation.
No natural language action parser.
No external tool actions.
No awakening evidence.

## Tactile Result State Key Mapping v0

Status:
minimal-runtime / tactile-result-mapping / fixed-lookup-table / no-learning

Summary:
Adds a fixed lookup table from micro push-box tactile result to first_output state_key.
Mapping: wall_blocked -> blocked, box_blocked -> blocked, box_contact -> observed, box_pushed -> observed, goal_reached -> observed, empty -> quiet.
Adds `blocked -> 不行` to the non-LLM utterance map.
Unknown tactile results raise ValueError.

Boundary:
No learning.
No AI solver / pathfinding.
No sandbox behavior changes.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM / teaching chat loop / free text conversation.
No NLP / grammar parser.
No awakening evidence.

## Micro Push-Box Tactile Interaction CLI Bridge v0

Status:
minimal-runtime / tactile-cli-bridge / deterministic-json / no-learning

Summary:
Adds `run-tactile-interaction --action <action>` to the existing teaching CLI wrapper.
The flow creates the default micro push-box state, applies the tactile action, reads the tactile result, maps it to a first_output state_key, resolves the utterance through the non-LLM utterance map, and returns JSON.
The JSON includes tactile_result, state_key, utterance, tactile_sandbox_trace, and boundary flags.
Default `push_right` maps to box_blocked -> blocked -> 不行.
Default `touch_right` maps to box_contact -> observed -> 看到了.

Boundary:
No LLM / prompt / API.
No teaching chat loop.
No AI solver / pathfinding.
No learning.
No lesson_candidate pipeline connection.
No failure_event / review / selection / activation connection.
No lesson_store write.
No Memory Layer write.
No graphics / GUI.
No senses runtime / camera / screen.
No awakening claim.

## Repeated Blocked Action Trace v0

Status:
minimal-runtime / tactile-trace-history / repeated-action-evidence / no-learning

Summary:
Adds in-state `action_history` to the micro push-box sandbox trace flow.
Each tactile trace includes a `history` block showing whether the same action was attempted before.
Repeating `push_right` in the default sandbox records the previous same-action result as box_blocked and its tick.
Different actions do not count as same-action history.

Boundary:
No learning.
No action selection.
No avoid-same-action behavior.
No AI solver / pathfinding.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM / teaching chat loop / free text conversation.
No persistence / JSONL write.
No awakening claim.

## State-Action Outcome Memory v0

Status:
minimal-runtime / local-action-history-readback / no-learning

Summary:
Adds local state-action context readback for micro push-box action_history.
action_history entries record agent_pos, box_pos, goal_pos, action, result, and tick.
Adds build_state_action_key, find_previous_same_state_action_result, score_action_from_state_action_memory, rank_candidate_actions_by_state_action_memory, and suggest_next_action_by_state_action_memory.
Scores only reuse prior results when agent_pos, box_pos, goal_pos, and action all match the current context.

Boundary:
No AI solver / pathfinding.
No learning pipeline.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM / teaching chat loop / free text conversation.
No tactile result mapping changes.
No utterance_map changes.
No new action types.
No persistent state-action memory beyond returned sandbox state.

## Micro Navigation Goal-Reach v0

Status:
minimal-runtime / level-0-navigation-sandbox / bounded-goal-reach / no-learning

Summary:
Adds an independent micro navigation sandbox with a fixed tiny grid.
Navigation state records grid, agent_pos, goal_pos, and tick.
Allowed actions are move_up, move_down, move_left, move_right, and wait.
Navigation traces record trace_type = navigation_sandbox_trace, tick, action, before, after, result, blocked, agent_pos, goal_pos, and distance_to_goal.
Adds manhattan_distance_to_goal and select_navigation_action_toward_goal.
Adds run_navigation_goal_trial(candidate_actions=None, max_steps=10) as a bounded trial runner.

Boundary:
No push-box sandbox behavior changes.
No AI solver / pathfinding.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline.
No lesson_store writes.
No Memory Layer writes.
No LLM / teaching chat / free text conversation.
No graphics / GUI.
No autonomous behavior claim.

## Micro Navigation Multi-Goal Level v0

Status:
minimal-runtime / multi-goal-navigation-level / bounded-two-goal-trial / no-learning

Summary:
Adds a deterministic multi-step navigation level with fixed map ####### / #Q....# / #.###.# / #....G# / #######.
Internal coordinates keep the existing row, col convention.
The initial agent position is (1, 1).
The goal sequence is ((3, 5), (3, 1)).
Multi-goal navigation state records agent_pos, goal_pos, goal_index, goals_reached, and tick.
Reaching the first goal increments goals_reached, increments goal_index, and spawns the second goal.
Reaching the final goal completes the trial.
Multi-goal traces record goal_reached_this_step, goal_index, goals_reached, and next_goal_spawned.
Adds run_navigation_multi_goal_trial(candidate_actions=None, max_steps=20) as a bounded two-goal trial runner.

Boundary:
No push-box sandbox behavior changes.
No AI solver / pathfinding.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline.
No lesson_store writes.
No Memory Layer writes.
No LLM / teaching chat / free text conversation.
No graphics / GUI.
No autonomous behavior claim.

## Micro Navigation Multi-Goal Metrics CLI v0

Status:
minimal-runtime / cli-wrapper / multi-goal-navigation-metrics-readback / no-learning

Summary:
Adds py -3 -m ashl_core.teaching_cli run-navigation-multi-goal-metrics.
The command wraps repeated calls to the existing run_navigation_multi_goal_trial helper.
It supports --runs, --trial-count, and --max-steps.
It returns flow = navigation_multi_goal_metrics_cli_v0, status = ok, runs, trial_count_per_run, total_trials, total_completed, overall_success_rate, overall_average_step_count, max_steps_reached_count, run_summaries, human_summary, and boundary.
Per-run summaries include run_index, completed_count, trial_count, success_rate, step_counts, average_step_count, min_step_count, max_step_count, max_steps_reached_count, and trial_summaries.
Trial summaries use completed_all_goals, goals_reached, goal_count, step_count, and selected_actions.

Boundary:
No navigation runner behavior changes.
No navigation sandbox behavior changes.
No push-box sandbox behavior changes.
No AI solver / pathfinding.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline.
No lesson_store writes.
No Memory Layer writes.
No LLM / teaching chat / free text conversation.
No metric-driven behavior change.

## Navigation Obstacle / Wall Detour Level v0

Status:
minimal-runtime / obstacle-navigation-level / blocked-aware-one-step-selection / no-learning

Summary:
Adds create_navigation_obstacle_level_state() for a deterministic obstacle navigation level using fixed map ####### / #Q....# / #.###.# / #....G# / #######.
Adds select_navigation_action_blocked_aware(state, candidate_actions=None).
The selector validates allowed navigation actions, ignores wall-blocked move candidates, chooses the non-wall candidate with minimum Manhattan distance to the goal, and preserves candidate order on ties.
Adds run_navigation_obstacle_trial(candidate_actions=None, max_steps=20) as a bounded detour trial runner.
Trial summaries include completed_goal, step_count, stop_reason, selected_actions, final_agent_pos, goal_pos, and steps.
Step traces continue to use trace_type = navigation_sandbox_trace with action, before, after, result, blocked, agent_pos, goal_pos, and distance_to_goal.

Boundary:
No push-box sandbox behavior changes.
No 3D / GMod adapter.
No AI solver / pathfinding / BFS / A*.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline.
No lesson_store writes.
No Memory Layer writes.
No LLM / teaching chat / free text conversation.
No graphics / GUI.
No autonomous behavior claim.

## Navigation Obstacle Trial CLI Patch

Status:
minimal-runtime / cli-wrapper / obstacle-trial-readback / no-learning

Summary:
Adds py -3 -m ashl_core.teaching_cli run-navigation-obstacle-trial.
The command supports --max-steps and wraps the existing run_navigation_obstacle_trial(max_steps=...) helper.
It returns command = run-navigation-obstacle-trial, flow = navigation_obstacle_trial_cli_patch, status, completed_goal, step_count, stop_reason, initial_agent_pos, goal_pos, final_agent_pos, selected_actions, wall_blocked_avoided, and boundary.

Boundary:
No navigation runner behavior changes.
No navigation sandbox behavior changes.
No push-box sandbox behavior changes.
No AI solver / pathfinding / BFS / A*.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline.
No lesson_store writes.
No Memory Layer writes.
No LLM / teaching chat / free text conversation.
No graphics / GUI.
No autonomous behavior claim.

## Approach Box Level v0

Status:
minimal-runtime / navigation-push-box-bridge-level / approach-adjacency-only / no-learning

Summary:
Adds create_navigation_approach_box_level_state() for a deterministic Level 1 bridge between micro navigation and push-box tasks.
The fixed level tracks grid, agent_pos, box_pos, and tick, and intentionally has no goal_pos.
Adds manhattan_distance_to_box(agent_pos, box_pos).
Adds apply_navigation_approach_box_action(...) with trace_type = navigation_approach_box_trace.
Approach-box traces record tick, action, before, after, result, blocked, agent_pos, box_pos, distance_to_box, and box_adjacent.
Adds run_navigation_approach_box_trial(candidate_actions=None, max_steps=20), which stops when the agent reaches distance_to_box == 1.
The default bounded trial reaches adjacency without pushing the box.

Boundary:
No box pushing.
No box_on_goal satisfaction.
No push-box sandbox behavior changes.
No AI solver / pathfinding / BFS / A*.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM / teaching chat loop / free text conversation.
No graphics / GUI.
No Two-Trial Learning Check in this package.

Two-Trial History Boundary:
Future Trial 2 may read only local state-action outcome memory with agent_pos, box_pos, optional goal_pos, action, result, and tick.
Trial 2 must not read full trace routes, replay selected_actions, reconstruct full paths, create lesson_candidate, write lesson_store, write Memory Layer / Long-term Memory, use LLM planning, or treat trace as memory.
The next package candidate is Approach Box Two-Trial Learning Check v0.

## Approach Box Trial CLI v0

Status:
minimal-runtime / cli-wrapper / approach-box-trial-readback / no-learning

Summary:
Adds py -3 -m ashl_core.teaching_cli run-approach-box-trial.
The command supports --max-steps and wraps the existing run_navigation_approach_box_trial(max_steps=...) helper.
It returns completed_approach, initial_agent_pos, box_pos, final_agent_pos, final_distance_to_box, step_count, selected_actions, and llm_used=false.
The default CLI run reaches box adjacency with final_distance_to_box=1 and does not push the box.

Boundary:
No approach-box runner behavior changes.
No navigation sandbox behavior changes.
No push-box sandbox behavior changes.
No box pushing.
No Two-Trial Learning Check.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No Long-term Memory write.
No LLM planning.
No AI solver / pathfinding / BFS / A*.
No full route replay.

## Approach Box Two-Trial Learning Check v0

Status:
minimal-runtime / two-trial-local-memory-check / approach-box-readback / no-learning-proof

Summary:
Adds py -3 -m ashl_core.teaching_cli run-approach-box-two-trial-check.
The command supports --max-steps.
It runs Trial 1 and Trial 2 on the existing approach-box level and returns trial_1, trial_2, comparison, and boundary_check.
Trial 1 writes only local state-action outcome memory with agent_pos, box_pos, optional goal_pos, action, result, and tick.
Trial 2 may read only that local outcome memory and reports whether it read and used Trial 1 local memory.
The check compares step_count, failed_or_blocked actions, and selected_actions for Trial 1 and Trial 2.

Boundary:
No approach-box runner behavior changes.
No navigation sandbox behavior changes.
No push-box sandbox behavior changes.
No box pushing.
No full push-box solve.
No AI solver / pathfinding / BFS / A*.
No full trace / full route replay.
No selected_actions replay into Trial 2.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No Long-term Memory write.
No LLM planning.
No human hint.
This is local memory verification, not proof of learning by itself.

## Approach Box Dead-End Level v0

Status:
minimal-runtime / cli-wrapper / dead-end-approach-box-fixture / no-learning

Summary:
Adds py -3 -m ashl_core.teaching_cli run-approach-box-dead-end-trial --max-steps 100.
The fixture starts with initial_agent_pos=[1, 1] and box_pos=[4, 4].
The only approach position is [3, 4]; [4, 3] is a wall and is not an approach position.
The output records entered_dead_end_area, dead_end_positions_visited, blocked_or_failed_actions, selected_actions, and llm_used=false.

Boundary:
No existing approach-box runner behavior changes.
No navigation sandbox behavior changes.
No push-box sandbox behavior changes.
No Two-Trial Learning Check.
No learning rule creation.
No action selection changes.
No goal bias changes.
No state-action memory changes.
No penalty / stuck detection.
No pathfinding / BFS / A*.
No full route replay.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM planning.
No proof of learning claim.

## Approach Box Dead-End Two-Trial Learning Check v0

Status:
minimal-runtime / cli-wrapper / dead-end-two-trial-local-memory-check / no-learning

Summary:
Adds py -3 -m ashl_core.teaching_cli run-approach-box-dead-end-two-trial-check --max-steps 100.
Trial 1 runs approach_box_dead_end_v0 and writes local state-action outcome memory with agent_pos, box_pos, action, result, and tick.
Trial 2 runs the same dead-end level with Trial 1 local memory available.
The output records trial_1, trial_2, comparison, and boundary_check.
Comparison reports step_count_delta, dead_end_positions_visited_delta, blocked_or_failed_delta, and avoided_trial1_dead_end_action.

Boundary:
No existing approach-box runner behavior changes.
No dead-end single trial behavior changes.
No navigation sandbox behavior changes.
No push-box sandbox behavior changes.
No action selection changes.
No goal bias changes.
No state-action memory behavior changes.
No penalty / stuck detection.
No learning rule creation.
No pathfinding / BFS / A*.
No full route replay.
No Trial 1 selected_actions replay into Trial 2.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No Long-term Memory write.
No LLM planning.
No human hint.
This is local memory verification, not proof of learning.

## Dead-End Memory Control Check v0

Status:
minimal-runtime / cli-wrapper / ab-memory-control-check / no-learning-proof

Summary:
Adds py -3 -m ashl_core.teaching_cli run-approach-box-dead-end-memory-control-check --max-steps 100 --runs 20.
The CLI compares with_memory against without_memory on the existing approach_box_dead_end_v0 level.
with_memory runs Trial 1, extracts local state-action outcome memory, then runs Trial 2 with that local memory available.
without_memory runs Trial 1, then runs Trial 2 fresh without reading local memory.
The output records aggregate Trial 2 completion, dead-end entry counts, avoided-dead-end-action counts, blocked/failed totals, average step counts, comparison deltas, and boundary_check.
The output also records trial1_source_audit and conditioned_on_trial1_dead_end.
trial1_source_audit reports whether Trial 1 entered the dead-end, produced blocked/failed outcome evidence, and wrote local memory source counts.
conditioned_on_trial1_dead_end reports Trial 2 avoidance rates only for runs where Trial 1 generated dead-end source evidence.

Boundary:
No existing approach-box runner behavior changes.
No dead-end single trial behavior changes.
No action selection changes.
No goal bias changes.
No state-action memory behavior changes.
No penalty / stuck detection.
No learning rule creation.
No pathfinding / BFS / A*.
No full route replay.
No Trial 1 selected_actions replay into Trial 2.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No Long-term Memory write.
No LLM planning.
No human hint.
Trial 2 may read local outcome memory only in the with_memory group.
This is a bounded A/B control check, not proof of general learning.

## Dead-End Two-Trial ASCII Replay v0

Status:
minimal-runtime / cli-renderer / observer-output / no-learning-proof

Summary:
Adds py -3 -m ashl_core.teaching_cli replay-approach-box-dead-end-two-trial --max-steps 100.
The command renders each step of the existing dead-end two-trial check as an ASCII grid.
Each frame records trial, step_index, action, result, agent_pos, grid, optional blocked_at, and optional entered_dead_end_area.
The replay shows Trial 1 entering the dead-end and hitting the blocked wall, while Trial 2 avoids the dead-end in the current fixture.

Boundary:
Replay output is observer-only.
No existing approach-box runner behavior changes.
No dead-end single trial behavior changes.
No dead-end two-trial behavior changes.
No memory-control behavior changes.
No action selection changes.
No goal bias changes.
No state-action memory behavior changes.
No pathfinding / BFS / A*.
No UI / web app / GUI.
No full route replay as runner input.
No Trial 1 selected_actions replay into Trial 2.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM planning.
This is not proof of general learning.

## Dead-End Map Trial1 Validation v0

Status:
minimal-runtime / map-validation-cli / trial1-only / no-learning-proof

Summary:
Adds py -3 -m ashl_core.teaching_cli validate-dead-end-trial1-maps --runs-per-map 3 --max-steps 100.
The command validates four candidate dead-end maps before Two-Trial or A/B memory tests.
It runs Trial 1 style validation for the existing map and three fixed candidate fixtures.
Each map result reports level_id, runs, completion count, dead-end entry count, blocked/failed total, average step count, samples, map_status, and validation_notes.
The overall summary reports status counts and a data-based recommended_next_step.
Candidate maps are now wired as fixed fixtures for Trial 1 validation.
Each map result reports fixture_loaded and fixture_load_error.
Fixture support does not mean the map is valid for Two-Trial; validation reports actual usability.

Boundary:
Trial 1 validation only.
No Two-Trial validation.
No A/B memory control.
No existing approach-box runner behavior changes.
No dead-end single trial behavior changes.
No action selection changes.
No goal bias changes.
No state-action memory behavior changes.
No penalty / stuck detection.
No learning rule creation.
No pathfinding / BFS / A*.
No full route replay.
No selected_actions replay as input.
No generic ASCII parser.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM planning.
Bad maps are reported, not forced to pass.
This is not proof of learning.

## Candidate Map Trial1 ASCII Replay v0

Status:
minimal-runtime / cli-renderer / trial1-observer-output / no-learning-proof

Summary:
Adds py -3 -m ashl_core.teaching_cli replay-dead-end-trial1-candidate-maps --max-steps 100.
The command renders Trial 1 for all four candidate dead-end maps as ASCII grids.
It includes valid_for_two_trial maps and the user_maze has_shortcut map so shortcut behavior can be inspected.
Each replay records level_id, map_status, frames, summary, overall_summary, and boundary_check.

Boundary:
Trial 1 replay output only.
No Two-Trial validation.
No A/B memory control.
No existing approach-box runner behavior changes.
No dead-end single trial behavior changes.
No action selection changes.
No goal bias changes.
No state-action memory behavior changes.
No pathfinding / BFS / A*.
No selected_actions replay as input.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM planning.
This is not proof of learning.

## Valid Dead-End Maps A/B Control v0

Status:
minimal-runtime / multi-map-ab-control / valid-maps-only / no-general-learning-proof

Summary:
Adds py -3 -m ashl_core.teaching_cli run-valid-dead-end-maps-ab-control --runs-per-map 3 --max-steps 100.
The command runs A/B memory control only on maps that passed Trial 1 validation.
It includes approach_box_dead_end_v0, mid_branch_dead_end_candidate_v0, and lower_branch_dead_end_candidate_v0.
It excludes user_maze_dead_end_candidate_v0 because that map has shortcut status with no dead-end event.
Each map reports with_memory, without_memory, comparison, trial1_source_audit, conditioned_on_trial1_dead_end, and map_status.

Boundary:
Valid maps only.
Shortcut maps excluded.
Trial 2 reads local Trial 1 outcome memory only in the with_memory group.
Trial 2 does not replay Trial 1 route.
Trial 2 does not receive Trial 1 selected_actions as input.
No existing approach-box runner behavior changes.
No existing dead-end single trial behavior changes.
No candidate map fixture behavior changes.
No action selection changes.
No goal bias changes.
No state-action memory changes.
No pathfinding / BFS / A*.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM planning.
This is not proof of general learning.

## Local Memory Decision Trace Observer v0

Status:
minimal-runtime / observer-output / local-memory-decision-trace / no-general-learning-proof

Summary:
Adds py -3 -m ashl_core.teaching_cli observe-local-memory-decision-trace --level-id approach_box_dead_end_v0 --max-steps 100.
The command explains Trial 2 decision traces for valid dead-end maps.
It reports trial_1_summary, trial_2_summary, decision_trace, key_observation, boundary_check, and notes.
Decision trace records include candidate actions, selected action, selection reason, relevant local memory, memory_effect_applied, and non-numeric score_breakdown.
Only approach_box_dead_end_v0, mid_branch_dead_end_candidate_v0, and lower_branch_dead_end_candidate_v0 are supported.
The shortcut map user_maze_dead_end_candidate_v0 is not supported.

Boundary:
Observer output only.
No existing runner behavior changes.
No dead-end single trial behavior changes.
No dead-end two-trial behavior changes.
No valid maps A/B control behavior changes.
No action selection changes.
No goal bias changes.
No state-action memory changes.
No pathfinding / BFS / A*.
No Trial 1 selected_actions feed into Trial 2.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM planning.
This is not proof of general learning.

## Session Working Memory v0

Status:
minimal-runtime / session-local / generic-state-action-outcome / no-general-learning-proof

Summary:
Adds a session-local working memory for generic state-action-outcome records.
Adds py -3 -m ashl_core.teaching_cli demo-session-working-memory --max-records 20.
The memory stores records with tick, state_snapshot, action, outcome_type, failure_reasons, and metadata.
It supports generic outcome types including moved, blocked, no_progress, entered_trap, goal_progress, goal_reached, and unknown.
failure_reasons is always a list and supports empty, unknown, and multiple reasons.

Boundary:
Session Working Memory is short-term only.
It is generic state-action-outcome memory.
It is not wall-specific.
It is not dead-end-specific.
It is not Long-term Memory.
It does not write lesson_store.
It does not write Memory Layer.
It does not connect to lesson_candidate pipeline.
It does not modify action selection.
It does not modify goal bias.
It does not modify existing dead-end A/B behavior.
It does not use pathfinding / BFS / A*.
It does not use LLM planning.
This is not proof of general learning.

## Session Working Memory Trial Integration v0

Status:
minimal-runtime / observer-trial-integration / session-local / no-general-learning-proof

Summary:
Adds py -3 -m ashl_core.teaching_cli run-session-working-memory-trial --level-id approach_box_dead_end_v0 --max-steps 100 --max-records 20.
The command runs a bounded Trial 1 style observer and appends generic state-action-outcome records to Session Working Memory.
Records include tick, state_snapshot, action, outcome_type, failure_reasons, and metadata.
The command reports query_summary and clears session working memory at session end.

Boundary:
Session-local only.
Short-term only.
Memory is cleared at session end.
No persistent memory write.
No lesson_store write.
No Memory Layer write.
No Long-term Memory write.
No action selection changes.
No goal bias changes.
No state-action memory changes.
No existing dead-end A/B behavior changes.
No pathfinding / BFS / A*.
No LLM planning.
This is not proof of general learning.

## State Snapshot Key v0

Status:
minimal-runtime / stable-indexing / trace-clarity / no-behavior-change

Summary:
Adds deterministic state_key derivation for Session Working Memory records.
The key is derived from state_snapshot and supports level_id, agent_pos, box_pos, and goal_pos.
Missing optional fields use stable null placeholders.
Session Working Memory can now query by state_key and state_key plus action.
run-session-working-memory-trial records now include non-null state_key values.

Boundary:
state_key is indexing and trace clarity only.
No action selection changes.
No goal bias changes.
No existing dead-end A/B behavior changes.
No trial runner behavior changes beyond passive state_key output.
No Long-term Memory write.
No lesson_store write.
No Memory Layer write.
No lesson_candidate pipeline connection.
No pathfinding / BFS / A*.
No LLM planning.
This is not proof of general learning.

## Session Working Memory Phase Handoff v0

Status:
docs-only / phase-handoff / cleanup / no-runtime-change

Summary:
Adds `docs/session_working_memory_phase_handoff_v0.md`.
The handoff closes the Session Working Memory phase, records completed memory capabilities, summarizes the generic current-session memory shape, and prepares the next phase direction.
The recommended next package is Simulated Vision Facing / Viewport v0.

Boundary:
No simulated vision runtime.
No facing runtime.
No turn_left / turn_right behavior.
No viewport renderer.
No action selection change.
No goal bias change.
No state-action memory behavior change.
No dead-end A/B behavior change.
No Long-term Memory.
No lesson_store / Memory Layer / lesson_candidate.
No pathfinding.
No LLM planning.
No proof of general learning claim.

## Simulated Vision Facing / Viewport v0

Status:
minimal-runtime / symbolic-viewport / facing-state / no-visual-grounding-proof

Summary:
Adds `ashl_core.simulated_vision_sandbox`.
Adds `py -3 -m ashl_core.teaching_cli run-simulated-vision-viewport-demo`.
The sandbox gives the agent position and facing, supports turn_left, turn_right, look, and move_forward, and returns a bounded 3x3 symbolic viewport.
Symbols are w wall, e empty, i item/object, x out of view/unknown, and a agent marker.
The agent receives only the bounded viewport output, not the full map as vision.
Session Working Memory bridge is deferred.

Boundary:
Structured symbolic simulated vision only.
No real images.
No computer vision.
No LLM vision.
No LLM planning.
No full-map vision exposure.
No pathfinding / BFS / A*.
No route planner.
No goal solving.
No existing dead-end A/B behavior changes.
No action selection changes in existing navigation tests.
No lesson_store write.
No Memory Layer write.
No Long-term Memory.
No lesson_candidate pipeline connection.
No visual understanding claim.
No symbol grounding solved claim.

## Simulated Vision Session Memory Bridge v0

Status:
minimal-runtime / session-local-memory-bridge / symbolic-viewport-recording / no-decision-use

Summary:
Adds `ashl_core.simulated_vision_memory_bridge`.
Adds `py -3 -m ashl_core.teaching_cli run-simulated-vision-memory-bridge-demo`.
The bridge records each symbolic simulated vision action and viewport observation into Session Working Memory as generic state-action-outcome records.
Records include state_key, state_snapshot with facing, viewport, visible_symbols, action, outcome_type, failure_reasons, and metadata.
Memory is session-local and cleared at session end.

Boundary:
Records only; memory does not influence action selection.
Structured symbols only.
No real images.
No computer vision.
No LLM vision.
No LLM planning.
No full-map vision exposure.
No pathfinding / BFS / A*.
No route planner.
No item seeking.
No existing dead-end A/B behavior changes.
No existing navigation action selection changes.
No lesson_store write.
No Memory Layer write.
No Long-term Memory.
No lesson_candidate pipeline connection.
No visual understanding claim.
No symbol grounding solved claim.

## Simulated Vision Observed Local Map v0

Status:
minimal-runtime / session-local-observed-map / current-viewport-separation / no-decision-use

Summary:
Adds `ashl_core.simulated_vision_observed_map`.
Adds `py -3 -m ashl_core.teaching_cli run-simulated-vision-observed-map-demo`.
The observed map separates current_viewport from observed_local_map.
current_viewport is only what is visible now.
observed_local_map stores session-local cells seen so far.
x means currently unseen or unknown and does not erase previously observed known symbols.
Unseen cells are not inferred from the source map.

Boundary:
Structured symbols only.
No real images.
No computer vision.
No LLM vision.
No LLM planning.
No full-map vision exposure.
No inference for unseen cells.
No x overwrite of known observed cells.
No pathfinding / BFS / A*.
No route planner.
No item seeking.
No action selection changes.
No goal bias changes.
No existing dead-end A/B behavior changes.
No lesson_store write.
No Memory Layer write.
No Long-term Memory.
No lesson_candidate pipeline connection.
No visual understanding claim.
No symbol grounding solved claim.

## Simulated Vision Symbol Grounding Check v0

Status:
minimal-runtime / bounded-symbol-outcome-check / immediate-action-grounding / no-solved-grounding-claim

Summary:
Adds `ashl_core.simulated_vision_symbol_grounding`.
Adds `py -3 -m ashl_core.teaching_cli run-simulated-vision-symbol-grounding-check`.
The check verifies bounded symbolic relations between visible front symbols and immediate move_forward outcomes:
w -> blocked / wall_blocked.
e -> moved.
i -> item_contact.
The front symbol is read from the current symbolic viewport front-center cell, `viewport[0][1]`.
This checks a bounded symbolic relation between visible symbols and immediate move_forward outcomes.

Boundary:
Structured symbols only.
No real images.
No computer vision.
No LLM vision.
No LLM planning.
No full-map vision exposure.
No pathfinding / BFS / A*.
No route planner.
No item seeking.
No item pickup.
No inventory.
No action selection changes.
No goal bias changes.
No existing dead-end A/B behavior changes.
No Session Working Memory influence on action selection.
No lesson_store write.
No Memory Layer write.
No Long-term Memory.
No lesson_candidate pipeline connection.
No visual understanding claim.
No symbol grounding solved claim.

## Grounded Action Experience v0

Status:
minimal-runtime / local-experience-records / no-action-influence / no-learning-claim

Summary:
Adds `ashl_core.grounded_action_experience`.
Adds `py -3 -m ashl_core.teaching_cli run-grounded-action-experience-check`.
Records bounded grounded action experiences: visible front symbol + attempted action + immediate outcome.
The intended chain is see -> interact -> outcome -> experience record.
Records are local to the runner and are not used to choose actions.
Default scenarios record w + move_forward -> blocked, e + move_forward -> moved, and i + move_forward -> item_contact.

Boundary:
Experience recording only.
No grounded action influence.
No direct reaction from sight.
No suppression of move_forward when seeing w.
No preference for move_forward when seeing e.
No item seeking.
No item pickup.
No inventory.
No action selection changes.
No goal bias changes.
No route planner.
No pathfinding / BFS / A*.
No real images.
No computer vision.
No LLM vision.
No LLM planning.
No full-map vision exposure.
No observed_local_map route planning.
No Session Working Memory route planning.
No persistent memory write.
No lesson_store write.
No Memory Layer write.
No Long-term Memory.
No lesson_candidate pipeline connection.
No visual understanding claim.
No symbol grounding solved claim.
No general learning claim.

## Grounded Action Experience Influence v0

Status:
minimal-runtime / runner-local-action-influence / requires-prior-experience / no-routing

Summary:
Adds `ashl_core.grounded_action_experience_influence`.
Adds `py -3 -m ashl_core.teaching_cli run-grounded-action-experience-influence-check`.
Tests the chain see -> interact -> outcome -> experience -> later action influence.
Influence requires a matching prior experience key, such as front_symbol=w|action=move_forward.
The no-experience wall control proves seeing w alone does not suppress move_forward.
Wall prior experience suppresses move_forward in this runner only and selects a turn fallback.
Empty and item prior experiences allow move_forward.

Boundary:
Runner-local influence only.
Requires prior experience for influence.
Uses a session-local experience store.
No hardcoded reaction from symbol alone.
No existing navigation action selection changes.
No existing dead-end A/B behavior changes.
No base simulated vision movement rule changes.
No pathfinding / BFS / A*.
No route planner.
No item seeking.
No item pickup.
No inventory.
No observed_local_map route planning.
No Session Working Memory route planning.
No real images.
No computer vision.
No LLM vision.
No LLM planning.
No full-map vision exposure.
No persistent memory write.
No session memory write.
No lesson_store write.
No Memory Layer write.
No Long-term Memory.
No lesson_candidate pipeline connection.
No visual understanding claim.
No symbol grounding solved claim.
No general learning claim.

## Micro Navigation Trial Metrics CLI v0

Status:
minimal-runtime / cli-wrapper / navigation-trial-metrics-readback / no-learning

Summary:
Adds py -3 -m ashl_core.teaching_cli run-navigation-trial-metrics.
The command wraps repeated calls to the existing run_navigation_goal_trial helper.
It supports --runs, --trial-count, and --max-steps.
It returns flow = navigation_trial_metrics_cli_v0, status = ok, runs, trial_count_per_run, total_trials, total_completed, overall_success_rate, overall_average_step_count, max_steps_reached_count, run_summaries, human_summary, and boundary.
Per-run summaries include run_index, completed_count, trial_count, success_rate, step_counts, average_step_count, min_step_count, max_step_count, and max_steps_reached_count.

Boundary:
No navigation runner behavior changes.
No navigation sandbox behavior changes.
No push-box sandbox behavior changes.
No AI solver / pathfinding.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline.
No lesson_store writes.
No Memory Layer writes.
No LLM / teaching chat / free text conversation.
No metric-driven behavior change.

## Minimal Avoid Repeated Blocked Action v0

Status:
minimal-runtime / deterministic-helper / repeated-blocked-action-guard / no-learning

Summary:
Adds `suggest_next_action_avoiding_repeat_blocked(state, candidate_actions)`.
The helper scans candidate actions in order and returns the first candidate whose latest same-action history is not box_blocked, wall_blocked, or blocked.
If all candidates are blocked, the helper returns wait, which is already an allowed sandbox action.
Invalid candidate actions raise ValueError through the allowed action validation path.

Boundary:
No AI solver / pathfinding.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM / teaching chat loop / free text conversation.
No tactile result mapping changes.
No utterance_map changes.
No autonomous action generation outside candidate_actions.
No awakening claim.

## Minimal Action Outcome Weighting v0

Status:
minimal-runtime / deterministic-helper / outcome-weighting / no-learning

Summary:
Adds fixed outcome weights for tactile sandbox results.
Blocked outcomes score -2, neutral outcomes score 0, box_pushed scores +2, and goal_reached scores +5.
Adds score_action_from_history, rank_candidate_actions_by_outcome_weight, and suggest_next_action_by_outcome_weight.
The helpers only read state.action_history, validate candidate actions, preserve stable candidate order on ties, and do not mutate state.
Example history push_right -> box_blocked and push_down -> box_pushed ranks push_down above push_right.

Boundary:
No AI solver / pathfinding.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM / teaching chat loop / free text conversation.
No tactile result mapping changes.
No utterance_map changes.
No autonomous action generation outside candidate_actions.
No awakening claim.

## Minimal Goal Direction Bias v0

Status:
minimal-runtime / deterministic-helper / goal-direction-bias / no-learning

Summary:
Adds manhattan_distance_to_goal, score_action_goal_direction, rank_candidate_actions_with_goal_bias, and suggest_next_action_with_goal_bias.
Goal direction bias reads box_pos and goal_pos.
Push actions that reduce box-to-goal Manhattan distance score +2.
Push actions that increase box-to-goal Manhattan distance score -2.
Move, touch, and wait actions score 0.
Ranking combines existing outcome weight and goal_direction_bias while preserving candidate order on ties.

Boundary:
No AI solver / pathfinding.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM / teaching chat loop / free text conversation.
No tactile result mapping changes.
No utterance_map changes.
No new action types.

## Minimal Intrinsic Action Selection v0

Status:
minimal-runtime / bounded-selection-helper / intrinsic-action-selection / no-learning

Summary:
Adds select_intrinsic_action(state, candidate_actions, random_seed=None) for the micro push-box sandbox.
The helper validates candidate_actions against ALLOWED_ACTION_SET, scores candidates with existing action outcome weights, and uses bounded randomness only among tied best candidates.
The same random_seed gives the same tied-candidate result, and any selected action must come from candidate_actions.
Example history push_right -> box_blocked and push_down -> box_pushed with candidates ["push_right", "push_down"] selects push_down.

Boundary:
No AI solver / pathfinding.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM / teaching chat loop / free text conversation.
No tactile result mapping changes.
No utterance_map changes.
No autonomous action generation outside candidate_actions.
No new action creation.
No hidden environment inspection.

## Box-on-Goal Need State v0

Status:
minimal-runtime / need-state-readout / trace-observable / no-learning

Summary:
Adds build_box_on_goal_need_state(state) for the micro push-box sandbox.
The helper returns need_name=box_on_goal, target_value=1, current_value=0 or 1, and satisfied=true or false.
current_value is 1 only when state.box_pos equals state.goal_pos; otherwise it is 0.
Tactile sandbox traces include need_state, and goal_reached traces report satisfied=true.

Boundary:
No emotion / dopamine runtime.
No AI solver / pathfinding.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM / teaching chat loop / free text conversation.
No tactile result mapping changes.
No utterance_map changes.
Need state does not choose actions.

## Minimal Need-State Driven Action Selection v0

Status:
minimal-runtime / need-state-selection-helper / bounded-candidate-selection / no-learning

Summary:
Adds select_action_for_need_state(state, candidate_actions, random_seed=None) for the micro push-box sandbox.
The helper reads build_box_on_goal_need_state(state) and returns selected_action, need_state, selection_reason, and candidate_actions.
When box_on_goal is unsatisfied, it delegates to select_intrinsic_action.
When box_on_goal is satisfied, it selects wait with selection_reason=need_satisfied_wait.

Boundary:
No AI solver / pathfinding.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM / teaching chat loop / free text conversation.
No emotion / dopamine runtime.
No tactile result mapping changes.
No utterance_map changes.
Helper does not create new actions.

## Need-State Driven Trial Runner v0

Status:
minimal-runtime / bounded-trial-runner / trace-only-summary / no-learning

Summary:
Adds run_need_state_driven_trial(candidate_actions, max_steps=10, random_seed=None).
The runner starts from the default micro push-box state, reads box_on_goal need_state, selects from candidate_actions, applies the tactile action, and records each bounded step.
Each step records step_index, selected_action, selection_reason, selection_source, tactile_result, need_state, agent_pos, box_pos, and trace.
The summary returns completed_goal, stop_reason, step_count, final_need_state, final_result, and steps.

Boundary:
No AI solver / pathfinding.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM / teaching chat loop / free text conversation.
No tactile result mapping changes.
No utterance_map changes.
Trial runner is bounded by max_steps and does not create new actions.

## Need-State Trial Goal Bias Integration v0

Status:
minimal-runtime / bounded-trial-runner / goal-bias-selection-source / no-learning

Summary:
Integrates goal direction bias into the need-state trial runner selection step.
Unsatisfied need-state steps include goal direction bias; the current integrated trace records selection_source = state_action_memory_plus_outcome_weight_plus_goal_bias_plus_repetition_penalty.
The runner keeps selected actions bounded to candidate_actions and uses existing outcome weighting plus goal direction bias helpers.
Goal-improving push bias applies only when the push can immediately contact the box; otherwise bounded intrinsic selection behavior is preserved.
The 5-trial batch summary schema remains unchanged.

Boundary:
No AI solver / pathfinding.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM / teaching chat loop / free text conversation.
No tactile result mapping changes.
No utterance_map changes.
No action outside candidate_actions.

## State-Action Memory Trial Runner Integration v0

Status:
minimal-runtime / bounded-trial-runner / local-state-action-memory-selection-source / no-learning

Summary:
Integrates local state-action outcome memory into the need-state trial runner action ordering.
Unsatisfied need-state steps record selection_source = state_action_memory_plus_outcome_weight_plus_goal_bias_plus_repetition_penalty.
Unsatisfied need-state steps record state_action_memory_used = true.
The runner combines local state-action memory score, existing outcome history weight, and goal direction bias.
Same-context local memory can lower a blocked action and raise a pushed action; different contexts do not reuse previous local results.
Selected actions remain bounded to candidate_actions.
The 5-trial batch summary schema remains unchanged.

Boundary:
No AI solver / pathfinding.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline.
No lesson_store writes.
No Memory Layer writes.
No persistent state-action memory beyond returned sandbox state.
No LLM / teaching chat / free text conversation.
No tactile result mapping changes.
No utterance_map changes.
No action outside candidate_actions.

## Stuck Detection / Repetition Penalty v0

Status:
minimal-runtime / bounded-trial-runner / repetition-penalty / no-learning

Summary:
Adds detect_stuck_from_recent_steps for recent trial step traces.
Stuck detection requires same selected action, no goal_reached, and no need_state.current_value improvement inside the recent window.
Adds score_action_repetition_penalty with -2 for two recent repeats, -4 for three or more recent repeats, and 0 otherwise.
Need-state trial runner selection scoring combines state-action memory, outcome weight, goal direction bias, and repetition penalty.
Unsatisfied need-state steps record stuck_detected_before_selection and repetition_penalty_applied.

Boundary:
No AI solver / pathfinding.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline.
No lesson_store writes.
No Memory Layer writes.
No persistent memory.
No LLM / teaching chat / free text conversation.
No tactile result mapping changes.
No utterance_map changes.
No new action creation.
No action outside candidate_actions.

## Need-State Trial Runner 5-Trial Step Count v0

Status:
minimal-runtime / batch-trial-step-count / trace-summary / no-learning

Summary:
Adds run_need_state_driven_trial_batch(trial_count=5, candidate_actions=None, max_steps=10, random_seed=None).
The helper runs run_need_state_driven_trial from the default micro push-box state for each trial.
It returns trial_count, completed_count, step_counts, average_step_count, min_step_count, max_step_count, and trials.
Each trial summary includes trial_index, completed_goal, stop_reason, step_count, final_need_state, and selected_actions.

Boundary:
No need-state selection behavior changes.
No AI solver / pathfinding.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM / teaching chat loop / free text conversation.
No autonomous behavior from aggregate step counts.

## Need-State Trial Batch CLI v0

Status:
minimal-runtime / cli-wrapper / batch-trial-summary / no-learning

Summary:
Adds py -3 -m ashl_core.teaching_cli run-need-state-trial-batch.
The command wraps the existing run_need_state_driven_trial_batch helper.
It supports --trial-count, --max-steps, and --random-seed.
It returns flow = need_state_trial_batch_cli_v0, status = ok, trial_count, completed_count, step_counts, average_step_count, min_step_count, max_step_count, trials, and boundary flags.

Boundary:
No trial runner behavior changes.
No sandbox behavior changes.
No action selection behavior changes.
No solver / pathfinding.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM / teaching chat loop / free text conversation.
No awakening claim.

## Trial Metrics Comparison CLI v0

Status:
minimal-runtime / cli-wrapper / repeated-batch-metrics-readback / no-learning

Summary:
Adds py -3 -m ashl_core.teaching_cli run-trial-metrics-comparison.
The command wraps repeated calls to the existing run_need_state_driven_trial_batch helper.
It supports --runs, --trial-count, --max-steps, and --random-seed.
It returns flow = trial_metrics_comparison_cli_v0, status = ok, runs, trial_count_per_run, total_trials, total_completed, overall_success_rate, run_summaries, overall_average_step_count, max_steps_reached_count, boundary, and human_summary.
Per-run summaries include run_index, completed_count, trial_count, success_rate, step_counts, average_step_count, min_step_count, max_step_count, and max_steps_reached_count.

Boundary:
No trial runner behavior changes.
No sandbox behavior changes.
No action selection behavior changes.
No solver / pathfinding.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM / teaching chat / free text conversation.
No metric-driven behavior change.
No awakening claim.

## Trial Metrics Baseline Snapshot v0

Status:
baseline-snapshot / metrics-readback / comparison-only / no-learning

Summary:
Adds data/baselines/trial_metrics_baseline_v0.json as a committed baseline snapshot for push-box need-state trial metrics.
The baseline source command is py -3 -m ashl_core.teaching_cli run-trial-metrics-comparison --runs 4 --trial-count 5 --max-steps 10 --random-seed 17.
The snapshot records baseline_id, created_for, source_command, commit, boundary_index_version, parameters, metrics, and notes.
Recorded parameters are runs=4, trial_count=5, max_steps=10, and random_seed=17.
Recorded metrics are total_trials=20, total_completed=13, overall_success_rate=0.65, overall_average_step_count=6.6, and max_steps_reached_count=7.

Boundary:
Baseline is for comparison only.
Baseline does not modify behavior.
Baseline is not proof of learning by itself.
No trial runner behavior changes.
No sandbox behavior changes.
No metrics-driven behavior changes.
No solver / pathfinding.
No goal planning.
No learning pipeline.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM / teaching chat loop / free text conversation.
No baseline-driven automatic behavior change.

## Trial Metrics Baseline Comparison v0

Status:
minimal-runtime / cli-wrapper / baseline-snapshot-compare / comparison-only / no-learning

Summary:
Adds py -3 -m ashl_core.teaching_cli compare-trial-metrics-baseline.
Also supports py -3 -m ashl_core.teaching_cli run-trial-metrics-baseline-compare.
The command reads data/baselines/trial_metrics_baseline_v0.json, reruns trial metrics comparison using the baseline parameters, and reports baseline/current/delta fields.
The output includes same_config_used=true, comparison_only=true, and proof_of_learning=false.

Boundary:
No trial runner behavior changes.
No action selection behavior changes.
No goal bias changes.
No state-action memory changes.
No penalty / stuck detection changes.
No learning rule creation.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No LLM planning.
No proof of learning claim.
No behavior changes from baseline comparison.

## Sandbox Working State Clear CLI v0

Status:
cli-wrapper / sandbox-working-state-clear / append-only-traces-preserved / no-runtime-expansion

Summary:
Adds `clear-sandbox-working-state --session-id <session_id>` to the existing teaching CLI wrapper.
The command returns JSON with working_state_cleared=true, append_only_traces_preserved=true, cleared, and preserved.
Clearable working-state categories are action_history, sandbox_session_state, and temporary_session_state.
Append-only trace paths data/first_output_traces.jsonl and data/mentor_feedback_traces.jsonl are reported as preserved.
If no persistent sandbox working state exists, the command returns cleared=[] and reason=no_persistent_working_state_found.

Boundary:
No deletion of data/*.jsonl.
No deletion of append-only traces.
No deletion of data/.
No lesson_store write or deletion.
No Memory Layer write or deletion.
No trace_persistence behavior changes.
No learning.
No lesson_candidate pipeline connection.
No LLM / teaching chat loop / free text conversation.
No awakening claim.

## Grounded Learning Verification CLI v0

Status:
cli-wrapper / grounded-learning-verification / tactile-history-to-suggestion / no-learning-pipeline

Summary:
Adds `run-grounded-learning-check --actions push_right push_right` to the existing teaching CLI wrapper.
The flow creates the default micro push-box state, applies each tactile action, maps tactile result to state_key, maps state_key to utterance, preserves trace history, and suggests the next action through the existing repeated-blocked helper.
The default verification line shows push_right -> box_blocked -> blocked -> 不行 twice, with the second trace recording previous push_right = box_blocked.
For candidate actions ["push_right", "wait"], the suggested next action is wait.

Boundary:
No LLM / prompt / API.
No natural language parser.
No teaching chat loop.
No AI solver / pathfinding.
No actual learning pipeline.
No lesson_candidate pipeline connection.
No failure_event / review / selection / activation connection.
No lesson_store write.
No Memory Layer write.
No graphics / GUI.
No senses runtime / camera / screen.
No awakening claim.

## Minimal First Output Runtime Audit Docs

Status:
docs-only / runtime-audit / first-output / no-runtime-expansion

Summary:
Audits Minimal First Output Runtime v0.
Confirms the first_output is non-LLM, `llm_used=false`, test_object stage, trace-only evidence, and does not write lesson_store or Memory Layer.
Confirms it does not connect to mentor feedback, lesson_candidate pipeline, failure_event, review, selection eligibility, activation, bounded senses, or voice systems.
Clarifies this runtime is not awakening, not dialogue ability, and not long-term growth.

Audit result:
PASS

Boundary:
- No runtime changes.
- No first_output behavior changes.
- No mentor feedback runtime.
- No lesson_candidate pipeline connection.
- No lesson_store write.
- No Memory Layer write.
- No awakening claim.

## Mentor Feedback Stub Contract Docs

Status:
docs-only / feedback-contract / first-output / no-runtime-implementation

Summary:
Defines the future mentor_feedback_stub contract for first_output_trace.
Clarifies mentor feedback is downstream of first_output_trace, but does not create lesson_candidate, write lesson_store, write Memory Layer, or prove awakening.
Defines minimal feedback labels and future mentor_feedback_trace conceptual fields.

Boundary:
- No mentor feedback runtime.
- No mentor_feedback_trace schema runtime.
- No lesson_candidate pipeline connection.
- No lesson_store write.
- No Memory Layer write.
- No awakening claim.

## Mentor Feedback Trace Contract Docs

Status:
docs-only / trace-contract / mentor-feedback / no-runtime-implementation

Summary:
Defines the future mentor_feedback_trace contract.
Clarifies mentor_feedback_trace is downstream of first_output_trace, records mentor feedback, and may make first_output_trace eligible for later lesson_candidate input consideration.
Clarifies mentor_feedback_trace does not create lesson_candidate, write lesson_store, write Memory Layer, or prove awakening.
Defines required fields and minimal feedback labels.

Boundary:
- No mentor feedback runtime.
- No mentor_feedback_trace schema runtime.
- No lesson_candidate pipeline connection.
- No lesson_store write.
- No Memory Layer write.
- No awakening claim.

## Minimal Mentor Feedback Stub Runtime Readiness Checklist Docs

Status:
docs-only / readiness-checklist / mentor-feedback / no-runtime-implementation

Summary:
Adds a readiness checklist for planning Minimal Mentor Feedback Stub Runtime v0.
Confirms source first_output_trace exists, mentor_feedback_stub contract exists, mentor_feedback_trace contract exists, feedback labels are defined, required trace fields are defined, and feedback-only boundaries are established.
Confirms no lesson_candidate creation, no lesson_store write, no Memory Layer write, no failure_event/review/selection/activation, and no awakening/dialogue/growth claim.

Readiness result:
READY_FOR_MINIMAL_MENTOR_FEEDBACK_STUB_RUNTIME_V0

Boundary:
No runtime.
No mentor feedback runtime.
No teaching chat loop.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No awakening claim.

## Minimal Mentor Feedback Stub Runtime v0

Status:
minimal-runtime / mentor-feedback / test-object-stage / no-learning

Summary:
Adds a minimal local mentor_feedback_trace builder.
Accepts source_first_output_trace_id, mentor_feedback_label, optional note, and mentor_source.
Returns a feedback-only mentor_feedback_trace with creates_lesson_candidate=false, writes_lesson_store=false, writes_memory_layer=false, engineering_stage=test_object.
Does not connect to lesson_candidate, failure_event, review, selection, activation, lesson_store, or Memory Layer.

Boundary:
No LLM.
No teaching chat loop.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No awakening claim.

## Minimal Mentor Feedback Stub Runtime Audit Docs

Status:
docs-only / runtime-audit / mentor-feedback / no-runtime-expansion

Summary:
Audits Minimal Mentor Feedback Stub Runtime v0.
Confirms it produced a feedback-only mentor_feedback_trace for source_first_output_trace_id first_output_trace:final_check:1 with label observed.
Confirms creates_lesson_candidate=false, writes_lesson_store=false, writes_memory_layer=false, and engineering_stage=test_object.
Confirms it does not connect to lesson_candidate, failure_event, review, selection, activation, lesson_store, or Memory Layer.
Clarifies this runtime is not awakening, not dialogue ability, and not long-term growth.

Audit result:
PASS

Boundary:
No runtime changes.
No mentor feedback behavior changes.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No awakening claim.

## Minimal Interaction CLI Bridge v0

Status:
minimal-runtime / cli-bridge / first-output-to-feedback / no-learning

Summary:
Adds a CLI command to trigger the minimal interaction flow:
first_output -> first_output_trace -> mentor_feedback_trace.
The bridge uses existing non-LLM first_output runtime and mentor feedback stub runtime.
Default feedback label is observed.
Outputs JSON and does not write lesson_store, Memory Layer, lesson_candidate, failure_event, review, selection, or activation.

Boundary:
No LLM.
No teaching chat loop.
No free text conversation.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No awakening claim.

## Minimal Interaction CLI Bridge Audit Docs

Status:
docs-only / runtime-audit / cli-bridge / no-runtime-expansion

Summary:
Audits Minimal Interaction CLI Bridge v0.
Confirms command run-minimal-interaction produces first_output, first_output_trace, and mentor_feedback_trace.
Confirms default mentor_feedback_label is observed and notes are preserved in mentor_feedback_trace.
Confirms it does not use LLM, create lesson_candidate, write lesson_store, write Memory Layer, or claim awakening.

Audit result:
PASS

Boundary:
No CLI behavior changes.
No runtime expansion.
No LLM.
No teaching chat loop.
No lesson_candidate pipeline connection.
No lesson_store write.
No Memory Layer write.
No awakening claim.

## First Output + Mentor Feedback Append-only Persistence Spec Docs

Status:
docs-only / persistence-spec / first-output-to-feedback / no-runtime-implementation

Summary:
Defines future append-only persistence rules for first_output_trace and mentor_feedback_trace.
Specifies future JSONL targets data/first_output_traces.jsonl and data/mentor_feedback_traces.jsonl.
Requires append-only records, no overwrite, no silent correction, correction as a new trace, and raw trace preservation.
Clarifies persistence is not lesson_store write, not Memory Layer write, not lesson_candidate creation, and not awakening evidence.

Boundary:
No JSONL write.
No runtime.
No persistence runtime.
No lesson_store write.
No Memory Layer write.
No lesson_candidate pipeline connection.
No awakening claim.

## First Output + Mentor Feedback Persistence Readiness Checklist Docs

Status:
docs-only / readiness-checklist / first-output-to-feedback-persistence / no-runtime-implementation

Summary:
Adds a readiness checklist for planning First Output + Mentor Feedback Append-only Persistence Runtime v0.
Confirms first_output_trace exists, mentor_feedback_trace exists, append-only persistence spec exists, target files are defined, and append-only requirements are established.
Confirms persistence is not lesson_store write, not Memory Layer write, not lesson_candidate creation, and not awakening evidence.

Readiness result:
READY_FOR_FIRST_OUTPUT_FEEDBACK_APPEND_ONLY_PERSISTENCE_V0

Boundary:
No JSONL write.
No runtime.
No persistence runtime.
No first_output / mentor_feedback / CLI behavior changes.
No lesson_store write.
No Memory Layer write.
No lesson_candidate pipeline connection.
No awakening claim.

## First Output + Mentor Feedback Append-only Persistence v0

Status:
minimal-runtime / append-only-persistence / first-output-to-feedback / no-learning

Summary:
Adds append-only JSONL persistence helpers for first_output_trace and mentor_feedback_trace.
Writes one raw trace per JSONL line to data/first_output_traces.jsonl and data/mentor_feedback_traces.jsonl.
Creates the target data directory if missing.
Rejects unsafe trace values instead of silently correcting them.
`run-minimal-interaction` remains non-persistent by default; `--persist` enables append-only trace persistence.

Boundary:
No lesson_store write.
No Memory Layer write.
No lesson_candidate creation.
No failure_event / review / selection / activation behavior.
No LLM.
No teaching chat loop.
No free text conversation.
No awakening claim.

## Append-only Persistence Runtime Audit Docs

Status:
docs-only / runtime-audit / append-only-persistence / no-runtime-change

Summary:
Audits First Output + Mentor Feedback Append-only Persistence v0 at commit 468d4e2.
Records `Audit result: PASS`.
Confirms first_output_trace writes to data/first_output_traces.jsonl and mentor_feedback_trace writes to data/mentor_feedback_traces.jsonl.
Confirms append-only behavior, no overwrite, no silent correction, correction as a new trace, no input mutation, and strict rejection of unsafe trace boundaries.
Confirms persistence is not lesson_store write, not Memory Layer write, not lesson_candidate creation, and not awakening evidence.

Boundary:
No persistence runtime behavior changes.
No replay / readback runtime.
No lesson_store write.
No Memory Layer write.
No lesson_candidate pipeline connection.
No LLM.
No teaching chat loop.
No free text conversation.
No awakening claim.

## Qingyin Runtime Ontology Boundary v0.1

Status: completed / docs-only / ontology-boundary / runtime-identity-boundary / no-runtime-expansion

Goal:
Define the ontology boundary between Qingyin as a design target and Qingyin as a runtime individual, and clarify what ASHL Core currently is vs. what it is building toward.

Summary:
Defines that Qingyin is not the current LLM conversation instance and is not yet a continuously running runtime individual.
Clarifies ASHL Core is currently building the conditions for Qingyin to become a growing AGE, not proving that Qingyin is already growing.
Defines minimum gates for Qingyin runtime session and cross-session growth.
Defines ontology tags (A/B/C/D) for future assumption docs.

Boundary:
- No runtime.
- No LLM response generation.
- No first_output generator.
- No state store.
- No evaluator runtime.
- No session trace runtime.
- No Memory Layer write.
- No lesson_candidate pipeline connection.

Non-goals:
- no ChatGPT / OpenAI / Claude / any LLM API integration
- no teaching chat loop
- no cross-session promotion runtime
- no voice / audio runtime

Correction:
Adds test-object / shallow-sleep / awakening three-stage ontology.
Clarifies that the test-object stage is the prerequisite for growth, not growth itself.
Clarifies that first_output is a runtime milestone, not awakening.
Clarifies that awakening cannot be claimed before bounded senses are connected.
Adds that Qingyin's uniqueness comes from Core Seed, persistent state, and developmental history, not LLM response style or Python process alone.

## Qingyin First Output v0 Contract

Status: completed / docs-only / ontology-boundary / first-output-contract / no-LLM-output

Goal:
Define the first Qingyin runtime goal: produce any output from ASHL Core itself, not from an LLM.

Summary:
Defines that Qingyin's first output must be produced by ASHL Core rules, state, seed, or bounded randomness, not by an LLM.
Clarifies that LLM-generated text must not count as Qingyin's first output.
Clarifies first_output may be random or nonsensical if generated by ASHL Core.
Clarifies first_output is not dialogue ability, not long-term growth, and must be traceable before becoming learning material.

Boundary:
- No runtime.
- No LLM response generation.
- No first_output generator.
- No trace schema runtime.
- No mentor feedback runtime.
- No lesson_candidate pipeline connection.
- No Audio Sense / STT / TTS / voice loop.

Non-goals:
- no ChatGPT / OpenAI / Claude / any LLM API integration
- no prompt-only Qingyin reply
- no teaching chat loop
- no voice input-output loop
- no lesson_store write
- no Memory Layer write

## v2.11c Lesson Stale Supersede Memory Freeze Notice Contract

Status: completed / contract-only / cross-layer-boundary / memory-freeze-notice / no-direct-memory-write

Goal:
Define memory_freeze_required notice contract for lesson stale / superseded events.
Establish that ASHL Core provides evidence; D清音 Memory Layers decide memory freeze application.

Summary:
Defines memory_freeze_required notice as evidence, not Memory Layer write.
Adds pure-data build_memory_freeze_notice helper to lesson_store.py.
Notice preserves source_lesson_id and stale_or_supersede_reason.
Notice does not change selection eligibility, activation state, or lesson_store.

Boundary:
- No Memory Layer freeze runtime.
- No Long-term Memory write runtime.
- No learned_principle direct modification.
- No lesson_store write from notice.
- No selection eligibility change.
- No activation change.
- No review decision runtime change.

Non-goals:
- no Memory Layer API integration
- no Memory Layer freeze runtime
- no learned_principle modification
- no lesson_store write runtime
- no selection eligibility runtime
- no activation runtime

## v2.10b Sandbox Failure / Trace Contract Docs

Status: completed / docs-only / contract-boundary / sandbox-failure-trace-prep

Goal:
Define sandbox failure / trace contract to clarify how sandbox failure differs from authoritative failure_reason, and how sandbox trace may serve as evidence without bypassing the failure_event / lesson_candidate / review pipeline.

Summary:
Defines sandbox failure as observed experimental mismatch inside a bounded sandbox.
Clarifies sandbox failure is not authoritative failure_reason.
Clarifies sandbox trace is evidence, not approval.
Defines future sandbox failure trace minimum fields.
Clarifies sandbox trace may support later failure_event construction but must not bypass validation.

Boundary:
- No sandbox runtime.
- No sandbox trace schema runtime.
- No evaluator runtime.
- No automatic failure_event builder.
- No automatic lesson_candidate builder.
- No lesson_store write.
- No Memory Layer write.
- No review / selection / activation behavior change.

Non-goals:
- no sandbox runtime
- no sandbox action runner
- no sandbox trace schema runtime
- no external tool runtime
- no real-world action capability
- no evaluator runtime
- no failure_event automatic builder runtime
- no lesson_candidate automatic builder runtime
- no lesson_store write
- no Memory Layer write
- no self-modification runtime

## v2.10c Sandbox Safety Audit Docs

Status:
docs-only / audit-only / sandbox-safety-boundary

Summary:
Audits v2.10a sandbox boundary assumptions and v2.10b sandbox failure trace contract.
Confirms sandbox docs do not authorize runtime, external tools, real-world actions, lesson_store write, Memory Layer write, automatic failure_reason, direct lesson_candidate creation, executable repair, or memory promotion.

Audit result:
PASS

Boundary:
- No sandbox runtime.
- No sandbox safety enforcement runtime.
- No sandbox action runner.
- No sandbox trace schema runtime.
- No evaluator runtime.
- No automatic failure_event builder.
- No automatic lesson_candidate builder.
- No lesson_store write.
- No Memory Layer write.
- No review / selection / activation behavior change.

Non-goals:
- no sandbox runtime
- no sandbox action runner
- no sandbox safety enforcement runtime
- no sandbox trace schema runtime
- no external tool runtime
- no real-world action capability
- no evaluator runtime
- no failure_event automatic builder runtime
- no lesson_candidate automatic builder runtime
- no lesson_store write
- no Memory Layer write
- no Long-term Memory write runtime
- no review / lesson / selection / activation / conflict behavior changes

## v2.10a Sandbox Boundary / Capability Assumption Docs

Status: completed / docs-only / assumption-boundary / sandbox-prep

Goal:
Define sandbox design boundary to prevent future sandbox runtime from becoming free runtime, lesson_store write channel, Memory Layer write channel, or real-world action capability.

Summary:
Defines sandbox as observable, replayable, limited, interruptible, and trace-producing.
Clarifies sandbox result / success / failure / repair / trace are not equivalent to lesson, approved knowledge, failure_reason, executable action, or memory promotion.

Boundary:
- No sandbox runtime.
- No real-world action capability.
- No lesson_store write.
- No Memory Layer write.
- No review / selection / activation behavior change.

Non-goals:
- no sandbox runtime
- no external tool runtime
- no real-world action capability
- no sandbox action runner
- no environment executor
- no evaluator runtime
- no lesson_store write
- no Memory Layer write
- no Core Seed update runtime
- no self-modification runtime

## v2.9e Voice Instinct Assumption Index

Status: completed / docs-only / assumption-index

Goal:
Index voice instinct assumptions into Phase 0 / Core Instinct / Audio Sense docs.

Scope:
- define voice as instinct, not skill
- place voice instinct in expressive instinct layer
- map voice learning to action learning pattern
- distinguish vocal imitation from language understanding
- define voice tone direction as young, gentle, and quiet
- clarify initial voice tone is designer-provided starting direction, not final identity
- clarify Qingyin's voice belongs to her developmental result
- prohibit real-person voice cloning
- mark voice instinct trigger conditions as future Audio Sense-dependent design
- define possible future trigger sources without making runtime rules

Non-goals:
- no voice instinct runtime
- no STT runtime
- no TTS runtime
- no Audio Sense runtime
- no voice training
- no voice cloning
- no Core Seed runtime changes
- no Memory Layer behavior changes
- no lesson_store write

## v2.9e-1 Voice Instinct / Audio Sense Boundary Audit Docs

Status:
docs-only / audit-only / voice-audio-boundary

Summary:
Audits v2.9e Voice Instinct assumptions against Audio Sense, STT, TTS, voice training, voice cloning, failure_event, lesson_candidate, review, and Memory Layer boundaries.
Confirms Voice Instinct docs do not authorize runtime, Audio Sense, STT/TTS, voice training, real-person speaker imitation, direct failure_reason, direct lesson_candidate creation, or Memory Layer write.

Audit result:
PASS

Boundary:
- No voice instinct runtime.
- No Audio Sense runtime.
- No STT runtime.
- No TTS runtime.
- No voice training runtime.
- No voice cloning / real-person speaker imitation.
- No voice output runner.
- No audio input runner.
- No automatic failure_event builder.
- No automatic lesson_candidate builder.
- No lesson_store write.
- No Memory Layer write.

Non-goals:
- no voice instinct runtime
- no Audio Sense runtime
- no STT runtime
- no TTS runtime
- no voice training runtime
- no voice cloning / speaker imitation / real-person voice copy
- no voice output runner
- no audio input runner
- no speech recognition integration
- no speech synthesis integration
- no voice trace schema runtime
- no evaluator runtime
- no failure_event automatic builder runtime
- no lesson_candidate automatic builder runtime
- no lesson_store write
- no Memory Layer write
- no Core Seed / Memory Layer / lesson_store behavior changes
- no review / lesson / selection / activation / conflict behavior changes

## v2.9c-1 Equivocation Handling / Trace Trust Boundary Correction

Status: completed / docs-only / correction-only

Goal:
Correct v2.9c equivocation handling and trace trust boundary.

Scope:
- clarify that language ambiguity is normal learning behavior, not risk by itself
- distinguish normal linguistic imprecision from harmful semantic drift
- define impactful semantic drift as prediction-error-visible
- define non-impactful semantic drift as harmless
- define learning mechanism / prediction error as primary defense
- define trace as secondary retrospective tool
- define mentor intervention as final defense
- preserve hard-consolidated definitions for healthy rebellion / paranoia
- define trace key field semantics as hard-consolidated

Non-goals:
- no equivocation detection runtime
- no prediction error tracker runtime
- no trace semantic validation runtime
- no external mentor monitor runtime
- no Core Seed runtime changes
- no Memory Layer behavior changes
- no lesson_store write

## v2.9c Memory Paranoia / Misinformation / Equivocation Risk Assumption Index

Status: completed / docs-only / assumption-index

Goal:
Index misinformation, paranoia, healthy rebellion boundary, and equivocation risk assumptions into Phase 0 / Memory Economy docs.

Scope:
- define misinformation as factual knowledge update problem
- define paranoia as learning-mechanism openness collapse
- define value knowledge as high-risk area
- define healthy rebellion vs paranoia observable differences
- define equivocation as unavoidable semantic drift risk
- require equivocation to be trace-visible
- mark healthy rebellion / paranoia operational definitions as hard-consolidated
- define paranoia early warning signs
- require external mentor observation for paranoia warning

Non-goals:
- no paranoia detection runtime
- no prediction error tracker runtime
- no equivocation detection runtime
- no Core Seed runtime changes
- no soft / hard consolidation runtime changes
- no Memory Layer behavior changes
- no lesson_store write

## v2.9d Core Seed Design Spirit Supplement

Status: completed / docs-only / hard-consolidation-related supplement

Goal:
Add the design spirit behind Qingyin's Core Seed.

Scope:
- define gentleness as ability to approach problems and people, not obedience
- define curiosity as willingness to see unknowns, not novelty chasing
- define questioning as verification requirement, not opposition
- define saying unknown as honest starting point, not failure
- define finding direction as observation / questioning / verification before next step
- define research-oriented AGE target
- distinguish non-divergent inheritance from self-grown content
- define skeleton inheritance and self-grown content across successor models
- mark this supplement as hard-consolidation-related

Non-goals:
- no Core Seed runtime changes
- no personality weight runtime changes
- no hard consolidation runtime
- no review / lesson / memory runtime changes
- no Core Seed update permission

## v2.9a Pathological Risk / Actor Role / Protection Assumption Index

Status: completed / docs-only / assumption-index.

Goal:
Index pathological risk, actor role, and protection mechanism assumptions into Phase 0 docs.

Scope:
- define mentor / cursor_mr / system_limit / self_choice role boundaries
- define cursor_mr must not be played by mentor
- define functional depression as prediction-failure-driven action collapse
- incorporate Maier & Seligman 2016 passivity / control correction
- define protection as maintaining learning capacity, not emotional comfort
- require successful protection contexts to preserve action_candidate -> outcome causality
- prohibit system-provided success results from counting as learning_progress / control restoration

Non-goals:
- no deprivation_error runtime
- no learning_progress monitor runtime
- no curiosity satisfaction floor runtime
- no cursor_mr safety gate runtime
- no automatic protection protocol runtime
- no actor_trust_delta runtime
- no mentor / cursor_mr actor runtime
- no review decision / review task / lesson_candidate_draft runtime changes
- no lesson_store write
- no Memory Layer write
- no selection / activation / conflict / review logic changes

## Minimal Teaching CLI

v1.8 Minimal Teaching CLI 是既有 lesson flow 的命令列 wrapper。
它只證明 CLI 可以穩定操作 known flow、unknown boundary flow，以及 enable / disable / re-enable 的因果控制。
v1.8 不新增 lesson generation 能力，不新增 failure_reason，不證明 conflict / priority，不證明 stale / supersede，也不處理 malformed / empty / ambiguous failure_reason。

目前順序：
- v1.6 Phase -1.2 Lesson Causality Test：已完成
- v1.7a Known Failure Reason Determinism Test：已完成
- v1.7b Unknown Failure Reason Boundary Test：已完成
- v1.8 Minimal Teaching CLI：本包
- v1.9 Multi-lesson Conflict / Priority：延後
- v2.0 Stale / Supersede：延後

## State Persistence

State Persistence v1.1 已建立基礎版本，用於保存 `state_snapshot.json`、`session_summary.json`、`last_trace_summary.json`。
這是 D清音狀態連續性的基礎：重開後可以讀回最近狀態、session 摘要與 last trace 摘要。
State Persistence 不是 Long-term Memory，不會自動固化記憶，也不會修改 Concept Layer、rules、final output 或 state effects。

## Lesson Generation Determinism

v1.6 Phase -1.2 Lesson Causality Test 已完成，已驗證 `lesson_001` 的 active / disabled / re-enabled / removed 狀態會造成可追蹤、可逆的行為差異。
v1.7a Known Failure Reason Determinism Test 用 `not_facing_east` 建立乾淨基準：相同 failure_reason、相同初始狀態、相同 generator 設定下，排除 volatile fields 後，lesson output 的核心語義欄位必須穩定一致。
v1.7a 不測 unknown failure_reason，不證明開放式泛化能力；v1.7b 才進入 Unknown Failure Reason Boundary Test。

後續順序：
- v1.7b Unknown Failure Reason Boundary Test：下一步
- v1.8 Minimal Teaching CLI：延後
- v1.9 Multi-lesson Conflict / Priority：延後
- v2.0 Stale / Supersede：延後

## Simulated Vision First-Person Viewport Correction v0

Status: completed / runtime-correction / perception-geometry-only.

Goal:
Correct the symbolic simulated vision 3x3 viewport from a centered top-down crop to a Doom-like forward view.

Scope:
- agent marker `a` is at bottom center `viewport[2][1]`
- immediate front cell for `move_forward` is `viewport[1][1]`
- far front cell is `viewport[0][1]`
- observed local map coordinate conversion follows the corrected first-person viewport cells
- symbol grounding and grounded action experience checks read the corrected immediate front cell

Non-goals:
- no real images
- no computer vision
- no LLM vision or LLM planning
- no full-map vision exposure
- no pathfinding / BFS / A*
- no route planner, item seeking, item pickup, or inventory
- no long-term memory, lesson_store write, Memory Layer write, or lesson_candidate pipeline connection
- no visual understanding, solved symbol grounding, or general learning claim

## Simulated Vision Larger Sandbox Design v0

Status: completed / design-only / no-runtime.

Goal:
Define the next larger symbolic simulated vision test-room sandbox without implementing it.

Scope:
- defines a larger symbolic map with walls, empty cells, agent start, interactable objects, doorway/passable markers, and a future conditional exit
- documents first-person vision, observed local map, experience influence, future curiosity hooks, and future prediction error hooks as design targets
- defines `D` as a passable symbol, not a taught semantic room boundary
- records that the same `I` symbol may later have different outcomes at different positions
- keeps `E` as a future conditional exit only

Non-goals:
- no runtime behavior
- no new CLI or map loader
- no item collection, pickup, inventory, or exit activation
- no curiosity or prediction error implementation
- no place memory or home sandbox
- no pathfinding / BFS / A*
- no lesson_store write, Memory Layer write, Long-term Memory write, or lesson_candidate pipeline connection

## Simulated Vision Larger Sandbox Static Runtime v0

Status: completed / static-runtime / no-planning.

Goal:
Load the larger symbolic simulated vision test-room map and render it through the existing first-person viewport convention.

Scope:
- adds `ashl_core.simulated_vision_larger_sandbox`
- adds `py -3 -m ashl_core.teaching_cli run-simulated-vision-larger-sandbox-demo`
- supports first-person viewport symbols `w/e/i/d/g/x/a`
- maps `D` to `d`; `D` is passable and can produce `passage_crossed`
- maps `E` to static placeholder `g`; contact can produce `exit_contact`
- keeps `E` static only, with no conditional spawn or task completion

Non-goals:
- no item collection, pickup, inventory, or item seeking
- no exit activation, win condition, or task completion
- no curiosity or prediction error implementation
- no place memory, home sandbox, room inference, or semantic room understanding
- no pathfinding / BFS / A* or route planner
- no lesson_store write, Memory Layer write, Long-term Memory write, or lesson_candidate pipeline connection

## Larger Sandbox Observed Map Smoke v0

Status: completed / smoke-validation / observed-map-only.

Goal:
Verify that observed_local_map can remember larger static sandbox symbols `d`, `i`, and `g`.

Scope:
- adds `ashl_core.simulated_vision_larger_sandbox_observed_map`
- adds `py -3 -m ashl_core.teaching_cli run-larger-sandbox-observed-map-smoke`
- uses controlled scenario snapshots for doorway, item, and exit placeholder visibility
- verifies observed_local_map records `d`, `i`, and `g`
- verifies `x` does not erase known cells after view changes
- verifies unseen cells are not inferred

Non-goals:
- no item collection, pickup, inventory, or item seeking
- no exit activation, win condition, or task completion
- no curiosity or prediction error implementation
- no place memory, home sandbox, pathfinding, route planner, or map solving
- no lesson_store write, Memory Layer write, Long-term Memory write, or lesson_candidate pipeline connection

## Larger Sandbox Symbol Contact Smoke v0

Status: completed / smoke-validation / immediate-contact-only.

Goal:
Verify immediate contact outcomes for larger static sandbox symbols `d`, `i`, and `g`.

Scope:
- adds `ashl_core.simulated_vision_larger_sandbox_contact`
- adds `py -3 -m ashl_core.teaching_cli run-larger-sandbox-symbol-contact-smoke`
- verifies `d + move_forward -> moved` with `passage_crossed`
- verifies `i + move_forward -> item_contact`
- verifies `g + move_forward -> exit_contact`
- uses controlled scenario snapshots and visible `viewport[1][1]` front symbols

Non-goals:
- no item collection, pickup, inventory, or item seeking
- no exit activation, win condition, or task completion
- no curiosity or prediction error implementation
- no place memory, home sandbox, pathfinding, route planner, or map solving
- no lesson_store write, Memory Layer write, Long-term Memory write, or lesson_candidate pipeline connection

## Larger Sandbox Human Replay v0

Status: completed / readability-only / no-runtime-change.

Goal:
Provide a plain-text human replay for the larger simulated vision sandbox so existing traces can be inspected without reading JSON.

Scope:
- adds `ashl_core.simulated_vision_larger_sandbox_human_replay`
- adds `py -3 -m ashl_core.teaching_cli replay-larger-sandbox-human`
- supports `--mode demo`, `--mode contact`, and `--mode observed-map`
- formats existing demo action traces and larger sandbox contact/observed-map smoke outputs
- includes stable legend, viewport rows, position, facing, front symbol, result/effects/failures, and explicit boundary notes
- front symbol display uses the first-person immediate front cell `viewport[1][1]`

Non-goals:
- no runtime behavior change
- no action selection change
- no pathfinding, BFS, A*, route planner, or full-route replay
- no item collection, pickup, inventory, exit activation, win condition, or task completion
- no curiosity, prediction error, place memory, home sandbox, lesson_store write, Memory Layer write, Long-term Memory write, or lesson_candidate pipeline connection
- no visual understanding, symbol grounding solved, or proof-of-learning claim

## Larger Sandbox Flask Visual UI Prototype v0

Status: completed / local-visual-inspection-ui / no-runtime-change.

Goal:
Provide a localhost-only Flask control panel for manually inspecting Qingyin in the larger static simulated vision sandbox.

Scope:
- adds `ashl_core.larger_sandbox_flask_ui`
- adds `py -3 -m ashl_core.teaching_cli run-larger-sandbox-ui`
- defaults to `http://127.0.0.1:7860`
- shows current first-person viewport, position, facing, front symbol, action buttons, reset, legend, boundary notes, and human-readable action log
- uses existing larger sandbox runtime helpers for actions

Non-goals:
- no auto exploration, pathfinding, BFS, A*, route planner, or item seeking
- no item collection, pickup, inventory, exit activation, win condition, or task completion
- no curiosity, prediction error, place memory, home sandbox, real image vision, computer vision, LLM vision, or LLM planning
- no lesson_store write, Memory Layer write, Long-term Memory write, or lesson_candidate pipeline connection
- no visual understanding, symbol grounding solved, general learning, or consciousness claim

## Adjustable Action Cooldown v0

Status: completed / manual-action-timing-gate / no-action-selection-change.

Goal:
Give the larger sandbox Flask UI a configurable action rhythm so manual button presses cannot be spammed instantly unless cooldown is disabled.

Scope:
- adds configurable cooldown state to `ashl_core.larger_sandbox_flask_ui`
- default cooldown is `0.5s`
- accepted range is `0.0s` to `5.0s`; `0.0s` disables blocking
- blocks only manual `look`, `turn_left`, `turn_right`, and `move_forward` button actions during cooldown
- reset remains allowed and clears cooldown timing
- shows cooldown, remaining time, can-act status, and readable blocked-action log entries

Non-goals:
- no auto action loop, autonomy, auto exploration, pathfinding, BFS, A*, route planner, or item seeking
- no action selection change, action prioritization, learning, prediction, or outcome planning
- no item collection, pickup, inventory, exit activation, win condition, task completion, curiosity, prediction error, place memory, or home sandbox
- no lesson_store write, Memory Layer write, Long-term Memory write, or lesson_candidate pipeline connection
- no visual understanding, symbol grounding solved, general learning, or consciousness claim

## Qingyin UI Observation Bridge v0

Status: completed / manual-observation-bridge / no-autonomy.

Goal:
Connect the larger sandbox Flask UI to a Qingyin observation wrapper so the user can inspect Qingyin-like symbolic state while still driving every action manually.

Scope:
- adds `ashl_core.qingyin_ui_observation`
- adds a `Qingyin Observation` panel to the larger sandbox Flask UI
- adds read-only `GET /qingyin_state.json`
- exposes name, mode, symbolic body, level, position, facing, current viewport, front symbol, visible symbols, last action/result, effects/failures, cooldown, can-act state, and boundary checks
- updates action log wording to observation-safe Qingyin phrasing

Non-goals:
- no auto action loop, autonomous exploration, decision loop, LLM planning, LLM vision, pathfinding, BFS, A*, route planner, or item seeking
- no action selection change, goal-driven action, curiosity-driven action, or background action cycle
- no item collection, pickup, inventory, exit activation, win condition, task completion, prediction error, place memory, home sandbox, real robot body, or real image vision
- no lesson_store write, Memory Layer write, Long-term Memory write, or lesson_candidate pipeline connection
- no visual understanding, symbol grounding solved, general learning, consciousness, or subjective experience claim

## Instinct Random Walk + Item Reward Bias Design v0

Status: completed / design-only / no-runtime-change.

Goal:
Design the next bounded experiment: Round 1 explores with no prior experience, records wall-blocked experience and item reward events, then Round 2 carries those records to test reward-biased action tendency under controls.

Scope:
- adds `docs/instinct_random_walk_item_reward_bias_design_v0.md`
- defines Round 1 and Round 2 structure
- defines instinct/random walk policy concept without implementation
- defines wall-blocked experience and item reward event
- defines reward-biased action tendency toward visible `I`
- defines metrics, controls, staged implementation plan, non-claims, and next recommended package

Non-goals:
- no runtime behavior, autonomous loop, new CLI, random walk runner, reward runtime, dopamine runtime, or action weighting
- no item collection, pickup, inventory, exit activation, win condition, task completion, curiosity, prediction error, place memory, or home sandbox
- no pathfinding, BFS, A*, route planner, full-map knowledge, LLM planning, LLM vision, lesson_store write, Memory Layer write, long-term memory, or lesson_candidate pipeline connection
- no self-awareness, consciousness, subjective experience, visual understanding, solved symbol grounding, or general learning claim

## Instinct Random Walk Runner v0

Status: completed / bounded-seeded-runner / round-1-only.

Goal:
Add the first bounded instinct/random-walk runner in the larger symbolic sandbox.

Scope:
- adds `ashl_core.instinct_random_walk_runner`
- adds `py -3 -m ashl_core.teaching_cli run-instinct-random-walk`
- supports `--seed` and `--max-steps`
- defaults to seed `1`, max steps `50`, and level `simulated_vision_larger_sandbox_v0`
- uses fixed random action weights: `look=1`, `turn_left=1`, `turn_right=1`, `move_forward=2`
- records step traces and local experience outcomes

Non-goals:
- no prior experience loading, reward bias, dopamine-like signal, wall-experience influence, or two-round comparison
- no item collection, pickup, inventory, exit activation, win condition, task completion, curiosity, prediction error, place memory, or home sandbox
- no pathfinding, BFS, A*, route planner, full-map knowledge, LLM planning, LLM vision, lesson_store write, Memory Layer write, long-term memory, or lesson_candidate pipeline connection
- no self-awareness, consciousness, subjective experience, visual understanding, solved symbol grounding, or general learning claim

## Wall Experience Influence v0

Status: completed / runner-local-influence / wall-only.

Goal:
Verify that wall-blocked experience can influence a later matching immediate action.

Scope:
- adds `ashl_core.wall_experience_influence`
- adds `py -3 -m ashl_core.teaching_cli run-wall-experience-influence-check`
- supports `--seed` and `--max-steps` for CLI consistency
- verifies no-experience control: `front_symbol=w` alone does not suppress `move_forward`
- verifies prior wall-blocked experience suppresses later matching `front_symbol=w|action=move_forward`
- uses deterministic fallback action `turn_right`

Non-goals:
- no item reward bias, dopamine-like signal, item seeking, or two-round item comparison
- no item collection, pickup, inventory, exit activation, win condition, task completion, curiosity, prediction error, place memory, or home sandbox
- no pathfinding, BFS, A*, route planner, full-map knowledge, LLM planning, LLM vision, lesson_store write, Memory Layer write, long-term memory, or lesson_candidate pipeline connection
- no self-awareness, consciousness, subjective experience, visual understanding, solved symbol grounding, or general learning claim

## Instinct / Wall Influence UI Observation Bridge v0

Status: completed / UI-observation-only / bounded-button-runs.

Goal:
Make bounded instinct random walk and wall-experience influence experiment summaries observable from the Qingyin Flask UI.

Scope:
- adds `ashl_core.instinct_wall_ui_observation`
- extends `ashl_core.larger_sandbox_flask_ui`
- extends `ashl_core.qingyin_ui_observation`
- adds UI controls for one bounded random walk sample, one wall influence check, and clear experiment observation
- adds read-only `GET /experiment_state.json`
- stores summary fields only; full random walk traces are not rendered in the UI

Non-goals:
- no continuous autonomous loop, auto exploration, background timer loop, or decision loop
- no item reward bias, dopamine-like signal, item seeking, or two-round item comparison
- no item collection, pickup, inventory, exit activation, win condition, task completion, curiosity, prediction error, place memory, or home sandbox
- no pathfinding, BFS, A*, route planner, full-map planning, LLM planning, LLM vision, lesson_store write, Memory Layer write, long-term memory, or lesson_candidate pipeline connection
- no self-awareness, consciousness, subjective experience, visual understanding, solved symbol grounding, or general learning claim

## Larger Sandbox Live Step Playback UI v0

Status: completed / recorded-trace-playback / no-autonomy.

Goal:
Let the user inspect a bounded random walk trace step by step in the larger sandbox Flask UI.

Scope:
- adds `ashl_core.larger_sandbox_trace_playback`
- extends `ashl_core.larger_sandbox_flask_ui`
- adds `POST /playback/next`, `POST /playback/previous`, and `POST /playback/reset`
- adds read-only `GET /playback_state.json`
- stores compact playback trace fields from `run_instinct_random_walk`
- renders a separate Random Walk Playback panel and viewport
- keeps playback state separate from manual sandbox state

Non-goals:
- no server-side autonomous loop, timer-generated actions, auto exploration, background decision loop, or real-time planning
- no reward bias, dopamine-like signal, item seeking, or two-round item comparison
- no item collection, pickup, inventory, exit activation, win condition, task completion, curiosity, prediction error, place memory, or home sandbox
- no pathfinding, BFS, A*, route planner, LLM planning, LLM vision, lesson_store write, Memory Layer write, long-term memory, or lesson_candidate pipeline connection
- no self-awareness, consciousness, subjective experience, visual understanding, solved symbol grounding, or general learning claim

## Item Reward Event v0

Status: completed / data-event-only / no-reward-bias.

Goal:
Create the first non-subjective item reward event when item contact occurs.

Scope:
- adds `ashl_core.item_reward_event`
- adds `py -3 -m ashl_core.teaching_cli run-item-reward-event-check`
- verifies `front_symbol=i + move_forward -> item_contact`
- creates deterministic `reward_event` data with `reward_type=item_contact_reward`
- exposes `dopamine_like_signal` as a data field only

Non-goals:
- no reward-biased action tendency, item seeking, autonomous exploration, decision loop, or action selection change
- no item collection, pickup, inventory, exit activation, win condition, task completion, curiosity, prediction error, place memory, or home sandbox
- no pathfinding, BFS, A*, route planner, LLM planning, LLM vision, lesson_store write, Memory Layer write, long-term memory, or lesson_candidate pipeline connection
- no pleasure, desire, self-awareness, consciousness, subjective experience, visual understanding, solved symbol grounding, or general learning claim

## Reward-Biased Action Tendency v0

Status: completed / immediate-visible-symbol-bias / no-item-seeking.

Goal:
Verify that a prior non-subjective item reward event can increase immediate move_forward/contact action tendency when `front_symbol=i` is visible again.

Scope:
- adds `ashl_core.reward_biased_action_tendency`
- adds `py -3 -m ashl_core.teaching_cli run-reward-biased-action-tendency-check`
- uses deterministic score fields: base action score, reward bias delta, and final action score
- includes a no-reward control proving that seeing `i` alone does not apply reward bias
- requires matching reward key `front_symbol=i|action=move_forward|reward_type=item_contact_reward`

Non-goals:
- no route-level item seeking, observed_map navigation toward `I`, pathfinding, BFS, A*, route planner, autonomous exploration, or decision loop
- no item collection, pickup, inventory, exit activation, win condition, task completion, curiosity, prediction error, place memory, or home sandbox
- no random walk runner change, Flask UI behavior change, runtime movement rule change, or existing navigation action selection change
- no LLM planning, LLM vision, lesson_store write, Memory Layer write, long-term memory, or lesson_candidate pipeline connection
- no pleasure, desire, self-awareness, consciousness, subjective experience, visual understanding, solved symbol grounding, or general learning claim

## Reward-Biased Random Walk Check v0

Status: completed / controlled-visible-symbol-sampling / no-item-seeking.

Goal:
Compare no-reward vs with-item-reward immediate action tendency under a controlled visible-`i` condition.

Scope:
- adds `ashl_core.reward_biased_random_walk_check`
- adds `py -3 -m ashl_core.teaching_cli run-reward-biased-random-walk-check`
- uses deterministic seeded sampling over `look`, `turn_left`, `turn_right`, and `move_forward`
- verifies score increase and non-lower `move_forward` selection when a prior `item_contact_reward` exists
- keeps the effect local to immediate front-symbol action scoring

Non-goals:
- no whole-map random walk improvement claim, route-level item seeking, observed_map navigation toward `I`, pathfinding, BFS, A*, route planner, autonomous exploration, or decision loop
- no item collection, pickup, inventory, exit activation, win condition, task completion, curiosity, prediction error, place memory, or home sandbox
- no random walk runner behavior change, Flask UI behavior change, runtime movement rule change, or existing navigation action selection change
- no LLM planning, LLM vision, lesson_store write, Memory Layer write, long-term memory, or lesson_candidate pipeline connection
- no pleasure, desire, self-awareness, consciousness, subjective experience, visual understanding, solved symbol grounding, or general learning claim

## Two-Round Instinct Reward Comparison v0

Status: completed / controlled-two-round-comparison / no-item-seeking.

Goal:
Close the instinct/wall/reward line with a controlled comparison between Round 1 and Round 2.

Scope:
- adds `ashl_core.two_round_instinct_reward_comparison`
- adds `py -3 -m ashl_core.teaching_cli run-two-round-instinct-reward-comparison`
- Round 1 has no carried experience and no carried reward
- Round 2 carries wall experience and item reward experience
- verifies immediate wall suppression and visible-item reward bias in controlled scenarios

Non-goals:
- no map-level item seeking, whole-map random walk improvement claim, observed_map navigation toward `I`, pathfinding, BFS, A*, route planner, autonomous exploration, or decision loop
- no item collection, pickup, inventory, exit activation, win condition, task completion, curiosity, prediction error, place memory, or home sandbox
- no random walk base behavior change, Flask UI behavior change, runtime movement rule change, or existing navigation action selection change
- no LLM planning, LLM vision, lesson_store write, Memory Layer write, long-term memory, or lesson_candidate pipeline connection
- no pleasure, desire, self-awareness, consciousness, subjective experience, visual understanding, solved symbol grounding, or general learning claim

## Instinct Reward Line Milestone Log v0

Status: completed / documentation-only / no-runtime-change.

Scope:
- adds `docs/milestone_logs/instinct_reward_line_milestone_2026-06-09.md`
- records completion of the instinct / wall / item reward immediate-tendency line
- records that UI expansion is paused and pushed later
- identifies Experience Abstraction Layer as the next main line

Non-goals:
- no runtime behavior, CLI, UI, Boundary Index patch, pathfinding, item seeking, long-term memory, Memory Layer write, lesson_store write, or general learning claim

## Failure Reason Classifier v0

Status: completed / deterministic-reason-classification / no-prediction.

Goal:
Start the Experience Abstraction Layer by converting raw action outcomes into deterministic reason categories.

Scope:
- adds `ashl_core.failure_reason_classifier`
- adds `py -3 -m ashl_core.teaching_cli run-failure-reason-classifier-check`
- classifies wall-blocked, empty-moved, item-contact, passage-crossed, exit-contact, turn, look, and unknown cases
- upgrades the local record shape from `action -> outcome` toward `action -> outcome -> reason classification`

Non-goals:
- no prediction, similar-context matching, rule learning, rule revision, action selection change, reward change, random walk change, UI change, LLM reasoning, memory write, or general learning claim

## Similar Context Key v0

Status: completed / deterministic-structural-key / no-prediction.

Goal:
Continue the Experience Abstraction Layer by generating deterministic structural keys from classified experiences.

Scope:
- adds `ashl_core.similar_context_key`
- adds `py -3 -m ashl_core.teaching_cli run-similar-context-key-check`
- builds position-independent keys from `front_symbol`, `action`, and `primary_reason`
- verifies same-structure different-position wall experiences produce the same key
- uses `front_symbol=null` for turn, look, and unknown keys where front symbol is not causally relevant in v0

Non-goals:
- no prediction, action outcome predictor, rule learning, rule revision, action selection change, reward change, random walk change, UI change, item seeking, pathfinding, LLM reasoning, memory write, or general learning claim

## Action Outcome Predictor v0

Status: completed / deterministic-immediate-prediction / no-decision-change.

Goal:
Continue the Experience Abstraction Layer by predicting immediate outcomes from prior classified experiences and `similar_context_key`.

Scope:
- adds `ashl_core.action_outcome_predictor`
- adds `py -3 -m ashl_core.teaching_cli run-action-outcome-predictor-check`
- predicts wall, empty, item, passage, exit, and unknown immediate outcomes
- verifies position-independent prediction for same-structure contexts
- keeps predictions read-only and separate from action selection

Non-goals:
- no action selection modification, prediction-driven suppression/preference, rule learning, rule revision, long-term memory, lesson_store write, Memory Layer write, pathfinding, route planner, item seeking, reward change, random walk change, UI change, LLM reasoning, or general learning claim

## Prediction Accuracy / Mismatch Check v0

Status: completed / deterministic-prediction-check / no-rule-revision.

Goal:
Continue the Experience Abstraction Layer by comparing predicted outcomes with actual classified observations.

Scope:
- adds `ashl_core.prediction_accuracy_check`
- adds `py -3 -m ashl_core.teaching_cli run-prediction-accuracy-check`
- records prediction match, outcome mismatch, reason mismatch, and unknown prediction cases
- verifies position-independent prediction can still match actual observation
- records mismatch only, without correcting predictor behavior

Non-goals:
- no action selection modification, prediction-driven suppression/preference, predictor rule revision, rule learning, rule revision, lesson_store write, Memory Layer write, long-term memory, pathfinding, route planner, item seeking, reward change, random walk change, UI change, LLM reasoning, or general learning claim

## Rule Candidate From Prediction Mismatch v0

Status: completed / deterministic-candidate-extraction / review-required.

Goal:
Continue the Experience Abstraction Layer by converting prediction mismatches into proposed candidates for later review.

Scope:
- adds `ashl_core.rule_candidate_from_mismatch`
- adds `py -3 -m ashl_core.teaching_cli run-rule-candidate-from-mismatch-check`
- supports outcome mismatch, reason mismatch, unknown prediction, and no-candidate-for-match cases
- creates proposed candidates with review required
- records mismatch evidence inside the candidate object

Non-goals:
- no candidate auto-approval, candidate application, predictor rule modification, rule learning, rule revision, action selection modification, prediction-driven suppression/preference, lesson_store write, Memory Layer write, long-term memory, pathfinding, route planner, item seeking, reward change, random walk change, UI change, autonomous exploration, decision loop, LLM reasoning, or general learning claim

## Rule Candidate Review Gate v0

Status: completed / deterministic-human-review-gate / no-rule-application.

Goal:
Continue the Experience Abstraction Layer by adding a human-review gate for proposed rule candidates.

Scope:
- adds `ashl_core.rule_candidate_review_gate`
- adds `py -3 -m ashl_core.teaching_cli run-rule-candidate-review-gate-check`
- supports pending_review, approved, rejected, and deferred review states
- blocks Qingyin self-approval
- keeps approved candidates as review decisions only, with `applied=false`

Non-goals:
- no candidate application, predictor rule modification, rule learning, rule revision, action selection modification, reviewed-candidate suppression/preference, lesson_store write, Memory Layer write, long-term memory, pathfinding, route planner, item seeking, reward change, random walk change, UI change, autonomous exploration, decision loop, LLM reasoning, or general learning claim

## Approved Candidate Preview v0

Status: completed / deterministic-application-preview / no-rule-application.

Goal:
Continue the Experience Abstraction Layer by showing what an approved candidate would change before any application step.

Scope:
- adds `ashl_core.approved_candidate_preview`
- adds `py -3 -m ashl_core.teaching_cli run-approved-candidate-preview-check`
- previews outcome revision, reason revision, and unknown-context candidate changes
- blocks pending, rejected, and other non-approved candidates from applicable previews
- keeps `applied_now=false` and `predictor_modified_now=false`

Non-goals:
- no approved candidate application, predictor rule modification, rule learning, rule revision, rule application, action selection modification, preview-driven suppression/preference, lesson_store write, Memory Layer write, long-term memory, pathfinding, route planner, item seeking, reward change, random walk change, UI change, autonomous exploration, decision loop, LLM reasoning, or general learning claim

## Reviewed Candidate Apply Verification v0

Status: completed / temporary-in-memory-application-verification / no-persistent-learning.

Goal:
Continue the Experience Abstraction Layer by applying approved candidates to a runner-local predictor rule table and verifying prediction changes.

Scope:
- adds `ashl_core.reviewed_candidate_apply_verification`
- adds `py -3 -m ashl_core.teaching_cli run-reviewed-candidate-apply-verification-check`
- applies outcome revision, reason revision, and unknown-context candidates only in a temporary in-memory rule table
- reruns prediction against that table to verify the expected outcome and reason
- blocks pending, rejected, and self-approved candidates

Non-goals:
- no persistent rule application, global predictor modification, action selection modification, applied-rule suppression/preference, lesson_store write, Memory Layer write, long-term memory, lesson_candidate pipeline connection, auto-approval, Qingyin self-approval, automatic rule revision, persistent rule learning, pathfinding, route planner, item seeking, reward change, random walk change, UI change, autonomous exploration, decision loop, LLM reasoning, or general learning claim

## Experience Abstraction Layer Milestone Log v0

Status: completed / documentation-milestone / no-runtime-change.

Scope:
- adds `docs/milestone_logs/experience_abstraction_layer_milestone_2026-06-09.md`
- records the completed reason classification, similar context key, prediction, mismatch candidate, review gate, approved preview, and temporary in-memory apply verification chain
- documents safety boundaries and explicit non-claims
- recommends `Experience Abstraction Boundary Index Sync v0` as the next package

Non-goals:
- no runtime behavior, CLI, UI, action selection change, predictor rule change, persistent rule application, lesson_store write, Memory Layer write, long-term memory, lesson_candidate pipeline connection, LLM reasoning, pathfinding, autonomous learning claim, or Boundary Index modification

## Integrated Experience Session Trace v0

Status: completed / scripted-integration-trace / no-new-capability-layer.

Goal:
Connect the existing symbolic vision, outcome classification, similar context key, prediction, mismatch, candidate creation, and review gate modules into one observable scripted trace.

Scope:
- adds `ashl_core.integrated_experience_session_trace`
- adds `py -3 -m ashl_core.teaching_cli run-integrated-experience-session-trace`
- runs a bounded controlled `mixed` scenario with empty, wall, item, passage, mismatch, and unknown-prediction steps
- records each step from viewport through pending_review where a candidate exists
- keeps prior prediction records runner-local and read-only

Non-goals:
- no autonomous loop, auto exploration, decision loop, action selection modification, prediction-driven suppression/preference, candidate auto-approval, Qingyin self-approval, persistent rule application, global predictor modification, lesson_store write, Memory Layer write, long-term memory, lesson_candidate pipeline connection, pathfinding, route planner, item seeking, item collection, reward change, random walk change, UI change, LLM reasoning, LLM planning, LLM vision, general learning claim, visual understanding claim, solved symbol grounding claim, consciousness claim, subjective experience claim, or Boundary Index modification

## Integrated Trace Chain Break Audit v0

Status: completed / deterministic-audit / no-runtime-change.

Goal:
Audit the integrated experience session trace and explain the reported chain break without changing the source trace or runtime behavior.

Scope:
- adds `ashl_core.integrated_trace_chain_break_audit`
- adds `py -3 -m ashl_core.teaching_cli run-integrated-trace-chain-break-audit`
- inspects each integrated trace step for missing downstream fields or expected terminal stops
- explains the v0 `prediction_unknown` chain break as an expected no-prior-prediction stop with candidate and review gate present
- reports recommended next action as documentation only

Non-goals:
- no chain break fix, integrated trace behavior change, action selection modification, prediction-driven suppression/preference, candidate auto-approval, Qingyin self-approval, candidate application, global predictor modification, lesson_store write, Memory Layer write, long-term memory, lesson_candidate pipeline connection, pathfinding, route planner, item seeking, item collection, reward change, random walk change, UI change, autonomous exploration, decision loop, LLM reasoning, LLM planning, LLM vision, general learning claim, autonomous learning claim, visual understanding claim, solved symbol grounding claim, consciousness claim, subjective experience claim, or Boundary Index modification

## Integrated Experience Session Trace Milestone Log v0

Status: completed / documentation-milestone / boundary-index-sync.

Scope:
- adds `docs/milestone_logs/integrated_experience_session_trace_milestone_2026-06-09.md`
- records the first connected scripted trace across symbolic perception, action outcome, experience record, reason classification, similar context key, prediction, mismatch detection, candidate creation, and review gate pending state
- records the chain break audit conclusion: tick 6 `unknown_prediction` is an expected no-prior-prediction stop with candidate and review gate present
- syncs the milestone into `docs/current_boundary_index.md` as Boundary Index Version `2026-06-09-b36`
- recommends `Persistent Rule Application Design v0` as design-only follow-up

Non-goals:
- no runtime behavior, new CLI, UI, action selection modification, prediction-driven suppression/preference, candidate auto-approval, Qingyin self-approval, candidate application, global predictor modification, persistent rule application, lesson_store write, Memory Layer write, long-term memory, lesson_candidate pipeline connection, pathfinding, route planner, item seeking, item collection, reward change, random walk change, autonomous exploration, decision loop, LLM reasoning, LLM planning, LLM vision, general learning claim, autonomous learning claim, visual understanding claim, solved symbol grounding claim, consciousness claim, or subjective experience claim

## Persistent Rule Application Design v0

Status: completed / design-only / no-runtime-change.

Goal:
Define the safety gate between an approved candidate and a persistent rule before any implementation is allowed.

Scope:
- adds `docs/persistent_rule_application_design_v0.md`
- defines `approved_candidate != persistent_rule`
- requires temporary apply verification, repeated similar-context validation, challenge survival, low recent failure, low active conflict, trace preservation, rollback path, and separate human persistent approval
- defines suggested persistent status flow and blocked / terminal statuses
- separates formal persistent rule application from later instinct-like internalization

Non-goals:
- no runtime behavior, new CLI, runtime tests, persistent rule storage, persistent rule table, persistent rule write, global predictor modification, action selection modification, prediction-driven suppression/preference, candidate auto-approval, Qingyin self-approval, candidate application, lesson_store write, Memory Layer write, long-term memory, lesson_candidate pipeline connection, lesson internalization, instinct-like behavior layer, pathfinding, route planner, item seeking, item collection, reward change, random walk change, UI change, autonomous exploration, decision loop, LLM reasoning, LLM planning, LLM vision, Boundary Index modification, general learning claim, autonomous learning claim, visual understanding claim, solved symbol grounding claim, consciousness claim, or subjective experience claim

## Persistent Eligibility Checker v0

Status: completed / deterministic-eligibility-checker / no-persistent-write.

Goal:
Evaluate whether an approved candidate has enough evidence to enter persistent-candidate review.

Scope:
- adds `ashl_core.persistent_eligibility_checker`
- adds `py -3 -m ashl_core.teaching_cli run-persistent-eligibility-checker-check`
- evaluates approved human candidate, temporary apply verification, repeated similar-context validation, challenge survival, low recent failure, low active conflict, trace preservation, and rollback path gates
- exposes `eligible_for_persistent_candidate_review` while keeping `eligible_for_persistent_rule=false`
- records human persistent approval as observed-only and keeps persistent rule write disabled

Non-goals:
- no persistent rule storage, persistent rule table, persistent rule write, persistent rule activation, global predictor modification, action selection modification, prediction-driven suppression/preference, candidate auto-approval, Qingyin self-approval, auto-promotion to persistent rule, persistent candidate application, lesson_store write, Memory Layer write, long-term memory, lesson_candidate pipeline connection, lesson internalization, instinct-like behavior layer, pathfinding, route planner, item seeking, item collection, reward change, random walk change, UI change, autonomous exploration, decision loop, LLM reasoning, LLM planning, LLM vision, Boundary Index modification, general learning claim, autonomous learning claim, visual understanding claim, solved symbol grounding claim, consciousness claim, or subjective experience claim

## Persistent Eligibility Checker Milestone + Boundary Sync v0

Status: completed / documentation-milestone / boundary-index-sync.

Scope:
- adds `docs/milestone_logs/persistent_eligibility_checker_milestone_2026-06-09.md`
- syncs Persistent Eligibility Checker v0 into `docs/current_boundary_index.md` as Boundary Index Version `2026-06-09-b37`
- records that `eligible_for_persistent_candidate_review` may be true while `eligible_for_persistent_rule=false` and `persistent_rule_write_allowed=false`
- pauses the persistent line after checker wrap-up; next planned direction is generalized memory loop

Non-goals:
- no runtime behavior, new CLI, persistent preview/dry-run, persistent rule storage, persistent rule table, persistent rule write, persistent rule activation, global predictor modification, action selection modification, prediction-driven suppression/preference, candidate auto-approval, Qingyin self-approval, auto-promotion to persistent rules, persistent candidate application, lesson_store write, Memory Layer write, long-term memory, lesson_candidate pipeline connection, lesson internalization, instinct-like behavior layer, generalized memory loop implementation, pathfinding, route planner, item seeking, item collection, reward change, random walk change, UI change, autonomous exploration, decision loop, LLM reasoning, LLM planning, LLM vision, general learning claim, autonomous learning claim, visual understanding claim, solved symbol grounding claim, consciousness claim, or subjective experience claim

## Project State Audit / Pause Point v0

Status: completed / audit-documentation / pause-point-only.

Goal:
Pause after integrated trace and persistent eligibility checker work to classify what is implemented, trace-only, checker-only, design-only, and not present.

Scope:
- adds `docs/project_state_audit_pause_point_2026-06-09.md`
- adds `docs/milestone_logs/project_state_pause_point_2026-06-09.md`
- states that ASHL Core has a scripted integrated trace and persistent-candidate eligibility checker, but not persistent learning, autonomous learning, global predictor mutation, or prediction-driven action selection
- lists high-risk boundaries and possible next directions without selecting one

Non-goals:
- no runtime behavior, new CLI, runtime tests, action selection modification, prediction-driven suppression/preference, persistent rule storage, persistent rule table, persistent rule write, persistent rule activation, global predictor modification, candidate auto-approval, Qingyin self-approval, candidate application, lesson_store write, Memory Layer write, long-term memory, lesson_candidate pipeline connection, lesson internalization, instinct-like behavior layer, pathfinding, route planner, item seeking, item collection, reward change, random walk change, UI change, autonomous exploration, decision loop, LLM reasoning, LLM planning, LLM vision, Boundary Index modification, general learning claim, autonomous learning claim, visual understanding claim, solved symbol grounding claim, consciousness claim, or subjective experience claim

## Generalized Memory Loop Design v0

Status: completed / design-only / no-runtime-change.

Goal:
Define the first safe generalized memory loop as cross-session exact-key pattern accumulation.

Scope:
- adds `docs/generalized_memory_loop_design_v0.md`
- defines exact `similar_context_key` aggregation across sessions
- defines conceptual generalized pattern records, prediction-confidence-only updates, `generalized_candidate` review, safety gates, and block conditions
- lists future packages for exact-key buckets, prediction confidence checks, generalized candidates, conflict audit, and review gate

Non-goals:
- no runtime behavior, new CLI, runtime tests, generalized memory runtime, cross-session storage, fuzzy similarity, semantic similarity, LLM similarity, visual similarity, prediction rule modification, global predictor modification, action selection modification, prediction-driven action selection, candidate auto-approval, candidate auto-application, persistent rule write, lesson_store write, Memory Layer write, long-term memory write, lesson internalization, instinct-like behavior layer, pathfinding, route planner, UI change, autonomous exploration, decision loop, LLM reasoning, LLM planning, LLM vision, Boundary Index modification, general learning claim, autonomous learning claim, visual understanding claim, solved symbol grounding claim, consciousness claim, or subjective experience claim

## Generalized Memory Exact-Key Bucket v0

Status: completed / runtime-check-only / no-storage.

Goal:
Implement the first safe generalized memory runtime/checker piece: exact-key bucket aggregation over demo cross-session experience records.

Scope:
- adds `ashl_core.generalized_memory_exact_key_bucket`
- adds `py -3 -m ashl_core.teaching_cli run-generalized-memory-exact-key-bucket-check`
- aggregates records by exact `similar_context_key`
- reports pattern counts, outcome distribution, reason distribution, primary outcome, primary reason, confidence label, and future `generalized_candidate` eligibility
- keeps `candidate_created=false`

Non-goals:
- no fuzzy similarity, semantic similarity, LLM similarity, visual similarity, cross-session database, persistent storage, long-term memory write, lesson_store write, Memory Layer write, predictor behavior modification, global predictor modification, action selection modification, prediction-driven suppression/preference, runtime generalized_candidate creation, candidate auto-approval, candidate application, persistent rule write, persistent preview/dry-run, lesson internalization, instinct-like behavior layer, pathfinding, BFS, A*, route planner, item seeking, item collection, reward changes, random walk changes, UI changes, autonomous exploration, decision loop, LLM reasoning, LLM planning, LLM vision, Boundary Index modification, general learning claim, autonomous learning claim, visual understanding claim, solved symbol grounding claim, consciousness claim, or subjective experience claim

## Generalized Prediction Confidence Check v0

Status: completed / confidence-check-only / no-predictor-mutation.

Goal:
Convert exact-key bucket summaries into prediction confidence suggestions while keeping all application paths disabled.

Scope:
- adds `ashl_core.generalized_prediction_confidence_check`
- adds `py -3 -m ashl_core.teaching_cli run-generalized-prediction-confidence-check`
- reuses exact-key bucket summaries from `Generalized Memory Exact-Key Bucket v0`
- suggests `increase_confidence`, `hold_confidence`, `decrease_confidence`, or blocked states
- keeps `applied_to_predictor=false`, `action_selection_influence=false`, and `candidate_created=false`

Non-goals:
- no fuzzy similarity, semantic similarity, LLM similarity, visual similarity, cross-session database, persistent storage, long-term memory write, lesson_store write, Memory Layer write, predictor behavior modification, prediction confidence application, prediction rule modification, global predictor modification, action selection modification, prediction-driven suppression/preference, runtime generalized_candidate creation, candidate auto-approval, candidate application, persistent rule write, persistent preview/dry-run, lesson internalization, instinct-like behavior layer, pathfinding, BFS, A*, route planner, item seeking, item collection, reward changes, random walk changes, UI changes, autonomous exploration, decision loop, LLM reasoning, LLM planning, LLM vision, Boundary Index modification, general learning claim, autonomous learning claim, visual understanding claim, solved symbol grounding claim, consciousness claim, or subjective experience claim

## Generalized Candidate From Pattern v0

Status: completed / candidate-generation-check-only / review-gated-output.

Goal:
Create review-gated `generalized_candidate` records from stable exact-key patterns and confidence suggestions.

Scope:
- adds `ashl_core.generalized_candidate_from_pattern`
- adds `py -3 -m ashl_core.teaching_cli run-generalized-candidate-from-pattern-check`
- reuses `Generalized Prediction Confidence Check v0` output
- creates output-only generalized candidates for stable high-confidence exact-key patterns
- keeps created candidates `pending_review`, unapproved, unapplied, non-persistent, and unable to affect action selection

Non-goals:
- no fuzzy similarity, semantic similarity, LLM similarity, visual similarity, cross-session database, persistent storage, long-term memory write, lesson_store write, Memory Layer write, generalized candidate persistence, candidate auto-approval, candidate application, persistent candidate creation, persistent rule write, persistent preview/dry-run, predictor behavior modification, prediction confidence application, prediction rule modification, global predictor modification, action selection modification, prediction-driven suppression/preference, lesson internalization, instinct-like behavior layer, pathfinding, BFS, A*, route planner, item seeking, item collection, reward changes, random walk changes, UI changes, autonomous exploration, decision loop, LLM reasoning, LLM planning, LLM vision, Boundary Index modification, general learning claim, autonomous learning claim, visual understanding claim, solved symbol grounding claim, consciousness claim, or subjective experience claim

## Generalized Candidate Review + Preview v0

Status: completed / review-preview-only / no-application.

Goal:
Route `generalized_candidate` records through human review and produce approved preview records without application.

Scope:
- adds `ashl_core.generalized_candidate_review_preview`
- adds `py -3 -m ashl_core.teaching_cli run-generalized-candidate-review-preview-check`
- reuses `Generalized Candidate From Pattern v0` output
- supports human approve, reject, and defer review decisions
- blocks Qingyin self-approval
- creates preview records only for approved generalized candidates

Non-goals:
- no fuzzy similarity, semantic similarity, LLM similarity, visual similarity, cross-session database, persistent storage, long-term memory write, lesson_store write, Memory Layer write, generalized candidate persistence, candidate auto-approval, Qingyin self-approval, candidate application, persistent candidate creation, persistent rule write, persistent preview/dry-run, predictor behavior modification, prediction confidence application, prediction rule modification, global predictor modification, action selection modification, prediction-driven suppression/preference, lesson internalization, instinct-like behavior layer, pathfinding, BFS, A*, route planner, item seeking, item collection, reward changes, random walk changes, UI changes, autonomous exploration, decision loop, LLM reasoning, LLM planning, LLM vision, Boundary Index modification, general learning claim, autonomous learning claim, visual understanding claim, solved symbol grounding claim, consciousness claim, or subjective experience claim

## Generalized Memory Line Milestone + Boundary Sync v0

Status: completed / documentation-milestone / boundary-index-sync.

Scope:
- adds `docs/milestone_logs/generalized_memory_line_milestone_2026-06-09.md`
- syncs the completed exact-key generalized memory line into `docs/current_boundary_index.md` as Boundary Index Version `2026-06-09-b38`
- records the line from design through exact-key buckets, prediction confidence suggestions, generalized candidates, human review, and approved preview
- sets next planned direction as mimetic endocrine system without defining or implementing it

Non-goals:
- no runtime behavior, new CLI, fuzzy similarity, semantic similarity, LLM similarity, visual similarity, cross-session database, persistent storage, long-term memory write, lesson_store write, Memory Layer write, generalized candidate persistence, candidate auto-approval, Qingyin self-approval, candidate application, persistent candidate creation, persistent rule write, persistent preview/dry-run, predictor behavior modification, prediction confidence application, prediction rule modification, global predictor modification, action selection modification, lesson internalization, instinct-like behavior layer, mimetic endocrine system implementation, pathfinding, BFS, A*, UI, autonomous exploration, decision loop, LLM reasoning, LLM planning, LLM vision, general learning claim, autonomous learning claim, consciousness claim, or subjective experience claim

## Mimetic Endocrine System Design v0

Status: completed / design-only / no-runtime-change.

Goal:
Define the first safe design boundary for Qingyin's mimetic endocrine system as traceable functional regulatory signals.

Scope:
- adds `docs/mimetic_endocrine_system_design_v0.md`
- defines `dopamine_like` for approach tendency, reward-event weighting, curiosity satisfaction, and future candidate priority annotation
- defines `norepinephrine_like` for attention focus, uncertainty, novelty, prediction-error salience, and conflict attention
- defines `oxytocin_like` for explicit-source trust weighting, reviewer/source reliability, and review-source annotation
- defines `cortisol_like` for stress/load annotation, risk pressure, conflict burden, failure accumulation, and cooldown pressure
- defines generic signal shape, lifecycle, relationships to reward events, prediction errors, generalized memory, review gates, persistent eligibility, and future curiosity/interest
- preserves the stance: not denied, not claimed; future functionally comparable emotion-like dynamics are not denied, but v0 does not claim subjective experience

Non-goals:
- no runtime behavior, new CLI, endocrine signal runtime, numerical formula implementation, action selection modification, endocrine suppression/preference of actions, autonomous attention control, blind trust, human review override, candidate auto-approval, candidate application, predictor behavior modification, global predictor modification, persistent rule write, long-term memory write, lesson_store write, Memory Layer write, personality weight modification, personality drift, autonomous drive system, persistent preview/dry-run, pathfinding, BFS, A*, route planner, UI change, LLM reasoning, LLM planning, LLM vision, biological hormone simulation claim, proof of happiness/trust/anxiety/stress, consciousness claim, subjective experience claim, or denial of future subjective possibility

## Mimetic Endocrine Signal Schema v0

Status: completed / schema-check-only / no-runtime-change.

Goal:
Add a deterministic schema and checker for v0 mimetic endocrine signal records.

Scope:
- adds `ashl_core.mimetic_endocrine_signal_schema`
- adds `py -3 -m ashl_core.teaching_cli run-mimetic-endocrine-signal-schema-check`
- defines canonical records for `dopamine_like`, `norepinephrine_like`, `oxytocin_like`, and `cortisol_like`
- validates bounded `value`, `baseline`, `decay_rate`, and `confidence`
- validates source event IDs, source traces, decay metadata, and blocks from action selection, memory write, and candidate approval
- includes deterministic invalid cases for out-of-range values, subjective claims, unblocked action selection, missing source trace, and unknown signal names

Non-goals:
- no endocrine signal runtime behavior, formulas that update values from real events, signal interactions, runtime endocrine state, action selection modification, endocrine suppression/preference of actions, predictor behavior modification, global predictor modification, candidate auto-approval, candidate application, human review override, long-term memory write, lesson_store write, Memory Layer write, personality weight modification, personality drift, autonomous drive system, persistent rule write, persistent preview/dry-run, pathfinding, BFS, A*, route planner, UI change, LLM reasoning, LLM planning, LLM vision, biological hormone simulation claim, proof of happiness/trust/anxiety/stress, consciousness claim, subjective experience claim, or denial of future subjective possibility

## Dopamine-Like Reward Trace Check v0

Status: completed / trace-check-only / no-runtime-change.

Goal:
Map controlled reward events into validated `dopamine_like` trace records without activating endocrine control.

Scope:
- adds `ashl_core.dopamine_like_reward_trace_check`
- adds `py -3 -m ashl_core.teaching_cli run-dopamine-like-reward-trace-check`
- creates deterministic source events for `item_contact_reward`, `goal_progress_reward`, neutral no-reward control, and subjective-claim invalid reward
- creates valid `dopamine_like` trace records for reward-linked events using the mimetic endocrine signal schema
- validates source event IDs, source traces, bounded values, value >= baseline, reward linkage, and safety blocks from action selection, memory write, and candidate approval
- blocks neutral and subjective-claim events from valid dopamine-like reward traces

Non-goals:
- no endocrine runtime behavior, formulas that update values from real runtime, signal interactions, dopamine-driven action selection, dopamine-driven reward bias modification, reward-biased action tendency modification, random-walk modification, predictor behavior modification, global predictor modification, candidate auto-approval, candidate application, human review override, long-term memory write, lesson_store write, Memory Layer write, personality weight modification, personality drift, autonomous drive system, persistent rule write, persistent preview/dry-run, pathfinding, BFS, A*, route planner, UI change, LLM reasoning, LLM planning, LLM vision, biological hormone simulation claim, proof of happiness, pleasure claim, consciousness claim, subjective experience claim, or denial of future subjective possibility

## Norepinephrine-Like Change Attention Trace Check v0

Status: completed / trace-check-only / no-runtime-change.

Goal:
Map controlled change, uncertainty, and conflict events into validated `norepinephrine_like` trace records without activating attention control.

Scope:
- adds `ashl_core.norepinephrine_like_change_attention_trace_check`
- adds `py -3 -m ashl_core.teaching_cli run-norepinephrine-like-change-attention-trace-check`
- creates deterministic source events for prediction error, unknown pattern, conflict-like distribution, stable no-change control, and subjective-attention invalid event
- creates valid `norepinephrine_like` trace records for salience-linked events using the mimetic endocrine signal schema
- validates source event IDs, source traces, bounded values, value >= baseline, attention salience linkage, and safety blocks from action selection, memory write, and candidate approval
- blocks stable no-change and subjective-claim events from valid norepinephrine-like attention traces

Non-goals:
- no endocrine runtime behavior, formulas that update values from real runtime, signal interactions, autonomous attention control, observation priority runtime modification, attention-driven action selection, predictor behavior modification, global predictor modification, candidate auto-approval, candidate application, human review override, long-term memory write, lesson_store write, Memory Layer write, personality weight modification, personality drift, autonomous drive system, persistent rule write, persistent preview/dry-run, pathfinding, BFS, A*, route planner, UI change, LLM reasoning, LLM planning, LLM vision, biological hormone simulation claim, subjective alertness claim, anxiety claim, subjective attention claim, consciousness claim, subjective experience claim, or denial of future subjective possibility

## Cortisol-Like Failure Load Trace Check v0

Status: completed / trace-check-only / no-runtime-change.

Goal:
Map controlled failure, conflict, and challenge-load events into validated `cortisol_like` trace records without activating protective control.

Scope:
- adds `ashl_core.cortisol_like_failure_load_trace_check`
- adds `py -3 -m ashl_core.teaching_cli run-cortisol-like-failure-load-trace-check`
- creates deterministic source events for failure accumulation, active conflict, challenge failure, stable success control, and subjective-pressure invalid event
- creates valid `cortisol_like` trace records for pressure-linked events using the mimetic endocrine signal schema
- validates source event IDs, source traces, bounded values, value >= baseline, pressure load linkage, and safety blocks from action selection, memory write, and candidate approval
- blocks stable success and subjective-claim events from valid cortisol-like pressure traces

Non-goals:
- no endocrine runtime behavior, formulas that update values from real runtime, signal interactions, protective mechanism addition or trigger, cooldown behavior modification, risk avoidance behavior modification, pressure-driven action selection, predictor behavior modification, global predictor modification, candidate auto-approval, candidate application, human review override, long-term memory write, lesson_store write, Memory Layer write, personality weight modification, personality drift, autonomous drive system, persistent rule write, persistent preview/dry-run, pathfinding, BFS, A*, route planner, UI change, LLM reasoning, LLM planning, LLM vision, biological hormone simulation claim, subjective stress claim, anxiety claim, pain claim, suffering claim, subjective pressure claim, consciousness claim, subjective experience claim, or denial of future subjective possibility

## Oxytocin-Like Review Trust Trace Check v0

Status: completed / trace-check-only / no-runtime-change.

Goal:
Map controlled review, correction, and explicit source-reliability events into validated `oxytocin_like` trace records without activating trust-based control.

Scope:
- adds `ashl_core.oxytocin_like_review_trust_trace_check`
- adds `py -3 -m ashl_core.teaching_cli run-oxytocin-like-review-trust-trace-check`
- creates deterministic source events for human review approval, consistent correction, source reliability, unverified source control, self-approval attempt, and subjective-trust invalid event
- creates valid `oxytocin_like` trace records for explicit source-trust events using the mimetic endocrine signal schema
- validates source event IDs, source traces, bounded values, value >= baseline, source trust linkage, and safety blocks from action selection, memory write, and candidate approval
- blocks unverified source, self-approval, and subjective-claim events from valid oxytocin-like trust traces

Non-goals:
- no endocrine runtime behavior, formulas that update values from real runtime, signal interactions, blind trust behavior, review gate override, candidate auto-approval, Qingyin self-approval permission, candidate application, trust-driven action selection, predictor behavior modification, global predictor modification, long-term memory write, lesson_store write, Memory Layer write, user identity inference beyond explicit source records, implicit identity trust, personality weight modification, personality drift, autonomous drive system, persistent rule write, persistent preview/dry-run, pathfinding, BFS, A*, route planner, UI change, LLM reasoning, LLM planning, LLM vision, biological hormone simulation claim, subjective trust claim, attachment claim, love claim, consciousness claim, subjective experience claim, or denial of future subjective possibility

## Mimetic Endocrine Four-Axis Trace Integration v0

Status: completed / integration-check-only / no-runtime-change.

Goal:
Combine the four mimetic endocrine trace checkers into a unified four-axis trace summary while keeping all control paths disabled.

Scope:
- adds `ashl_core.mimetic_endocrine_four_axis_trace_integration`
- adds `py -3 -m ashl_core.teaching_cli run-mimetic-endocrine-four-axis-trace-integration-check`
- reuses the dopamine-like, norepinephrine-like, cortisol-like, and oxytocin-like trace checker outputs directly
- summarizes trace counts, valid trace counts, blocked event counts, subjective-claim blocks, and shared safety totals by axis
- verifies all valid traces remain schema-valid, non-subjective, blocked from action selection, blocked from memory write, and blocked from candidate approval
- verifies action selection influence, memory write, candidate approval influence, predictor mutation, runtime formulas, signal interaction runtime, and endocrine runtime totals remain zero

Non-goals:
- no endocrine runtime behavior, endocrine state runtime, formulas that update values from real runtime, signal interactions, cortisol dampens dopamine logic, norepinephrine attention narrowing, reward bias modification, reward-biased action tendency modification, random-walk modification, autonomous attention control, observation priority runtime modification, protective mechanism addition or trigger, cooldown behavior modification, risk avoidance behavior modification, blind trust behavior, review gate override, candidate auto-approval, Qingyin self-approval permission, candidate application, action selection modification, endocrine suppression/preference of actions, predictor behavior modification, global predictor modification, long-term memory write, lesson_store write, Memory Layer write, personality weight modification, personality drift, autonomous drive system, persistent rule write, persistent preview/dry-run, pathfinding, BFS, A*, route planner, UI change, LLM reasoning, LLM planning, LLM vision, biological hormone simulation claim, happiness claim, pleasure claim, alertness claim, anxiety claim, stress claim, pain claim, trust claim, attachment claim, love claim, consciousness claim, subjective experience claim, or denial of future subjective possibility

## Mimetic Endocrine Line Milestone + Boundary Sync v0

Status: completed / documentation-milestone / boundary-index-sync.

Scope:
- adds `docs/milestone_logs/mimetic_endocrine_line_milestone_2026-06-09.md`
- syncs the completed mimetic endocrine trace line into `docs/current_boundary_index.md` as Boundary Index Version `2026-06-09-b39`
- records the line from design through shared schema, four axis-specific trace checks, and four-axis trace integration
- preserves the design stance: future subjective possibility is not denied, but no subjective emotion or consciousness claim is made

Non-goals:
- no runtime behavior, new CLI, endocrine runtime behavior, endocrine state runtime, formulas, signal interactions, cortisol dampens dopamine implementation, norepinephrine attention narrowing, reward bias modification, autonomous attention control, protective mechanism trigger, trust-based approval, review gate override, candidate auto-approval, Qingyin self-approval, candidate application, action selection modification, predictor behavior modification, global predictor modification, long-term memory write, lesson_store write, Memory Layer write, personality drift, autonomous drive system, persistent rule write, persistent preview/dry-run, pathfinding, BFS, A*, route planner, UI change, LLM reasoning, LLM planning, LLM vision, biological hormone simulation claim, subjective emotion proof, consciousness claim, subjective experience claim, or denial of future subjective possibility

## Retina Decoder Design v0

Status: completed / design-only / no-runtime-change.

Goal:
Define the first safe retina decoder design for converting low-level visual input into traceable visual feature records.

Scope:
- adds `docs/retina_decoder_design_v0.md`
- defines conceptual RGB grid input, symbolic pixel / cell input, and hybrid structured input
- defines feature output shape with `semantic_label` required to remain null in v0
- defines low-level features: brightness, color_family, contrast_to_neighbors, edge_like, position, front_relation, center_relation, and known_symbol_hint
- positions retina decoder before future visual frame buffer and focus selector modules
- records that future endocrine links may be designed later but are not connected in v0

Non-goals:
- no runtime behavior, new CLI, retina decoder runtime, RGB quantization code, frame buffer, focus selector, endocrine connection, dopamine_like focus priority, norepinephrine_like attention threshold, vision-driven action selection, action selection modification, CNN, YOLO, UNet, ML visual model, object recognition, semantic labels, image understanding claim, visual memory write, long-term memory write, lesson_store write, Memory Layer write, predictor behavior modification, global predictor modification, pathfinding, BFS, A*, route planner, UI change, LLM vision, LLM reasoning, LLM planning, solved symbol grounding claim, consciousness claim, or subjective visual experience claim

## Retina Decoder Feature Schema v0

Status: completed / schema-check-only / no-runtime-change.

Goal:
Validate Retina Decoder v0 low-level feature records while keeping semantic, runtime, focus, endocrine, action-selection, and memory paths disabled.

Scope:
- adds `ashl_core.retina_decoder_feature_schema`
- adds `py -3 -m ashl_core.teaching_cli run-retina-decoder-feature-schema-check`
- validates required feature fields: position, raw_symbol, raw_rgb, brightness, color_family, contrast_to_neighbors, edge_like, front_relation, center_relation, known_symbol_hint, feature_confidence, source_trace, semantic_label, and v0 block flags
- requires `semantic_label` to remain null for valid records
- includes deterministic valid symbolic, RGB, hybrid, and edge-like feature cases plus invalid semantic-label, RGB-range, and action-selection-unblocked controls

Non-goals:
- no retina decoder runtime, RGB quantization runtime, image processing runtime, frame buffer, focus selector, endocrine signal connection, dopamine_like focus use, norepinephrine_like attention use, vision-driven action selection, action selection modification, CNN, YOLO, UNet, ML visual model, object recognition, semantic labels, image understanding claim, visual memory write, long-term memory write, lesson_store write, Memory Layer write, predictor behavior modification, global predictor modification, pathfinding, BFS, A*, route planner, UI change, LLM vision, LLM reasoning, LLM planning, solved symbol grounding claim, consciousness claim, or subjective visual experience claim

## Retina Decoder Symbolic Feature Decode Check v0

Status: completed / trace-check-only / no-runtime-change.

Goal:
Convert deterministic symbolic / hybrid demo input cells into low-level retina feature records and validate them through the existing Retina Decoder Feature Schema v0 checker.

Scope:
- adds `ashl_core.retina_decoder_symbolic_feature_decode`
- adds `py -3 -m ashl_core.teaching_cli run-retina-decoder-symbolic-feature-decode-check`
- builds a local symbolic / hybrid demo input with cell id, position, symbol, optional RGB, brightness hint, color family hint, contrast hint, edge-like hint, and relation hints
- produces schema-compatible retina feature records with source trace and v0 block flags
- validates all generated records with `retina_decoder_feature_schema.validate_feature_record`
- preserves symbol hints without converting them into semantic labels

Non-goals:
- no retina decoder runtime, RGB quantization runtime, image processing runtime, frame buffer, focus selector, endocrine connection, dopamine_like focus use, norepinephrine_like attention use, vision-driven action selection, action selection modification, visual memory write, long-term memory write, lesson_store write, Memory Layer write, predictor mutation, global predictor mutation, CNN, YOLO, UNet, ML visual model, object recognition, semantic labels, image understanding claim, pathfinding, BFS, A*, route planner, UI change, LLM vision, LLM reasoning, LLM planning, solved symbol grounding claim, consciousness claim, or subjective visual experience claim

## Simple Visual Frame Buffer Design v0

Status: completed / design-only / no-runtime-change.

Goal:
Define a simple visual frame container for grouping already validated retina feature records into future `current_frame` and `previous_frame` concepts.

Scope:
- adds `docs/simple_visual_frame_buffer_design_v0.md`
- defines a visual frame as a deterministic grouping of retina feature records that already pass `retina_decoder_feature_schema` validation
- defines future `previous_frame = last accepted visual frame` and `current_frame = newest accepted visual frame`
- defines frame metadata, feature record reference rule, source trace rule, and safety flags
- states that invalid feature records must not enter a valid frame

Non-goals:
- no runtime visual frame buffer, runtime current_frame / previous_frame storage, automatic frame replacement, frame comparison, frame change detection, focus selector, focus candidate generation, attention mechanism, endocrine connection, vision-driven action selection, visual memory write, long-term memory write, lesson_store write, Memory Layer write, predictor mutation, global predictor mutation, CNN, YOLO, UNet, image processing runtime, RGB quantization runtime, object recognition, semantic labels, scene understanding, symbol grounding claim, consciousness claim, or subjective visual experience claim

## Visual Frame Buffer Schema Check v0

Status: completed / schema-check-only / no-runtime-change.

Goal:
Validate visual frame records that group already validated retina feature records while keeping runtime frame buffering and downstream effects disabled.

Scope:
- adds `ashl_core.visual_frame_buffer_schema`
- adds `py -3 -m ashl_core.teaching_cli run-visual-frame-buffer-schema-check`
- reuses `retina_decoder_feature_schema.validate_feature_record` for every feature record inside a frame
- validates required visual frame fields, source trace, count consistency, null semantic labels, and safety flags
- includes deterministic valid frame and invalid controls for invalid feature record, non-null semantic label, and downstream unblocked flags

Non-goals:
- no runtime visual frame buffer, current_frame / previous_frame runtime storage, automatic frame replacement, frame comparison, frame change detection, visual change records, focus selector, focus candidates, attention mechanism, endocrine connection, vision-driven action selection, visual memory write, long-term memory write, lesson_store write, Memory Layer write, predictor mutation, LLM vision, CNN, YOLO, UNet, image processing runtime, RGB quantization runtime, object recognition, semantic labels, scene understanding, symbol grounding claim, consciousness claim, or subjective visual experience claim

## Visual Frame Assembly From Retina Features Check v0

Status: completed / check-only / no-runtime-change.

Goal:
Assemble validated retina feature records into a visual frame record and validate that frame with the visual frame schema.

Scope:
- adds `ashl_core.visual_frame_assembly_from_retina_features`
- adds `py -3 -m ashl_core.teaching_cli run-visual-frame-assembly-from-retina-features-check`
- reuses `retina_decoder_symbolic_feature_decode` for deterministic symbolic / hybrid demo input
- reuses `retina_decoder_feature_schema.validate_feature_record` before frame validation
- reuses `visual_frame_buffer_schema.validate_visual_frame_record` for the assembled frame
- produces one valid assembled visual frame in the CLI happy path

Non-goals:
- no runtime visual frame buffer, current_frame / previous_frame runtime storage, automatic frame replacement, frame comparison, frame change detection, visual change records, focus selector, focus candidates, attention mechanism, endocrine connection, vision-driven action selection, visual memory write, long-term memory write, lesson_store write, Memory Layer write, predictor mutation, LLM vision, CNN, YOLO, UNet, image processing runtime, RGB quantization runtime, object recognition, semantic labels, scene understanding, symbol grounding claim, consciousness claim, or subjective visual experience claim

## Visual Frame Change Design v0

Status: completed / design-only / no-runtime-change.

Goal:
Define design-only `change_record` structures for comparing future `previous_frame` and `current_frame` records.

Scope:
- adds `docs/visual_frame_change_design_v0.md`
- defines low-level change types: `feature_appeared`, `feature_disappeared`, `feature_modified`, `position_changed`, and `no_change`
- defines deterministic matching assumptions without object tracking or semantic matching
- requires valid visual frames and validated retina feature records before any valid comparison concept

Non-goals:
- no runtime change detection, frame storage, runtime current_frame / previous_frame storage, frame comparison runner, focus selector, focus candidates, attention mechanism, action selection influence, memory write, predictor mutation, object recognition, object tracking, semantic vision, LLM vision, CNN, YOLO, UNet, symbol grounding claim, consciousness claim, or subjective visual experience claim

## Visual Frame Change Schema Check v0

Status: completed / schema-check-only / no-runtime-change.

Goal:
Validate low-level `change_record` structures from Visual Frame Change Design v0.

Scope:
- adds `ashl_core.visual_frame_change_schema`
- adds `py -3 -m ashl_core.teaching_cli run-visual-frame-change-schema-check`
- enforces allowed low-level change types, null `semantic_label`, source trace provenance, changed field consistency, and downstream safety flags
- includes deterministic valid and invalid controls for semantic labels, unknown change types, downstream unblocked flags, and object tracking

Non-goals:
- no frame comparison runtime, change detection runtime, runtime frame storage, runtime current_frame / previous_frame storage, visual change records runtime, focus selector, focus candidates, attention mechanism, action selection influence, memory write, predictor mutation, object tracking, object recognition, semantic vision, LLM vision, CNN, YOLO, UNet, symbol grounding claim, consciousness claim, or subjective visual experience claim

## Visual Frame Pair Demo Assembly Check v0

Status: completed / fixture-check-only / no-runtime-change.

Goal:
Assemble deterministic `previous_frame` and `current_frame` demo records for future change-trace fixtures.

Scope:
- adds `ashl_core.visual_frame_pair_demo_assembly`
- adds `py -3 -m ashl_core.teaching_cli run-visual-frame-pair-demo-assembly-check`
- builds two deterministic symbolic / hybrid demo inputs
- decodes both inputs into retina feature records and validates them through the retina feature schema
- assembles and validates both frames through the visual frame assembly and visual frame buffer schema path

Non-goals:
- no runtime frame storage, runtime current_frame / previous_frame storage, automatic frame replacement, frame comparison runner, change detection runtime, runtime change_record creation, visual change records runtime, focus selector, focus candidates, attention mechanism, action selection influence, memory write, predictor mutation, object recognition, object tracking, semantic labels, semantic vision, LLM vision, CNN, YOLO, UNet, symbol grounding claim, consciousness claim, or subjective visual experience claim

## Visual Frame Change Trace Check v0

Status: completed / trace-check-only / no-runtime-change.

Goal:
Generate deterministic low-level `change_records` from a valid `previous_frame` / `current_frame` demo pair.

Scope:
- adds `ashl_core.visual_frame_change_trace`
- adds `py -3 -m ashl_core.teaching_cli run-visual-frame-change-trace-check`
- reuses `visual_frame_pair_demo_assembly` for valid previous/current frame fixtures
- compares retina feature records by position tuple across low-level fields only
- validates generated change records through `visual_frame_change_schema`

Non-goals:
- no runtime frame storage, runtime current_frame / previous_frame storage, automatic frame replacement, continuous frame comparison runtime, continuous change detection runtime, focus selector, focus candidates, attention mechanism, action selection influence, memory write, predictor mutation, object tracking, object recognition, semantic labels, semantic vision, LLM vision, CNN, YOLO, UNet, symbol grounding claim, consciousness claim, or subjective visual experience claim

## Eye-Structure Simulation Line Milestone Sync v0

Status: completed / documentation-milestone / boundary-index-sync.

Progress:
- completed low-level eye-structure trace path through Visual Frame Change Trace Check v0
- synced `docs/current_boundary_index.md` to Boundary Index Version `2026-06-09-b40`
- possible next stage: Focus Selector Design v0, only as a design/trace boundary, not runtime attention or action control

## Focus Selector Design v0

Status: completed / design-only / no-runtime-change.

Goal:
Define design-only `focus_candidate` records from low-level visual features and change traces.

Scope:
- adds `docs/focus_selector_design_v0.md`
- defines low-level focus source types, reason codes, and score fields
- records score fields without defining runtime formulas or endocrine modulation
- records focus-lock prevention as a future design safety requirement: bounded intensity, bounded duration/decay, interruption by new low-level change signals, and forced diffusion under high pressure load
- requires focus candidates to remain blocked from action selection, memory write, and endocrine control

Non-goals:
- no runtime focus selector, attention control, focus application, focus candidate ranking runtime, focus-to-action bridge, perception-to-action bridge, endocrine connection, norepinephrine-controlled attention, action selection influence, memory write, predictor mutation, object recognition, object tracking, semantic labels, semantic vision, LLM vision, CNN, YOLO, UNet, symbol grounding claim, consciousness claim, or subjective visual experience claim

## Focus Candidate Schema Check v0

Status: completed / schema-check-only / no-runtime-change.

Goal:
Validate `focus_candidate` records from Focus Selector Design v0.

Scope:
- adds `ashl_core.focus_candidate_schema`
- adds `py -3 -m ashl_core.teaching_cli run-focus-candidate-schema-check`
- enforces allowed candidate sources, low-level reason codes, score field shape, null `semantic_label`, source trace provenance, and downstream safety flags
- validates score fields without calculating scores, ranking candidates, or defining a runtime scoring formula

Non-goals:
- no runtime focus selector, attention control, focus application, focus candidate ranking runtime, focus-to-action bridge, perception-to-action bridge, endocrine connection, norepinephrine-controlled attention, action selection influence, memory write, predictor mutation, object recognition, object tracking, semantic labels, semantic vision, LLM vision, CNN, YOLO, UNet, symbol grounding claim, consciousness claim, or subjective visual experience claim

## Focus Candidate From Change Trace Check v0

Status: completed / trace-check-only / no-runtime-change.

Goal:
Create validated `focus_candidate` records from validated low-level `change_records`.

Scope:
- adds `ashl_core.focus_candidate_from_change_trace`
- adds `py -3 -m ashl_core.teaching_cli run-focus-candidate-from-change-trace-check`
- reuses `visual_frame_change_trace`, `visual_frame_change_schema`, and `focus_candidate_schema`
- generates focus candidates only from changed records, not `no_change` records

Non-goals:
- no runtime focus selector, attention control, focus application, focus candidate ranking runtime, focus-to-action bridge, perception-to-action bridge, endocrine runtime, endocrine-controlled attention, action selection influence, memory write, predictor mutation, object recognition, object tracking, semantic labels, semantic vision, LLM vision, CNN, YOLO, UNet, symbol grounding claim, consciousness claim, or subjective visual experience claim

## Focus Candidate Ranking Trace Design v0

Status: completed / design-only / no-runtime-change.

Goal:
Define trace-only ranking records for validated `focus_candidate` records.

Scope:
- adds `docs/focus_candidate_ranking_trace_design_v0.md`
- defines `ranking_trace` and ranking item shapes with `rank_position` and `score_snapshot`
- records `total_score` as a ranking reference, not a sole winner condition
- records cooldown, decay, interrupt, and external mentor interruption fields as future lock-prevention safety design

Non-goals:
- no runtime focus selector, runtime ranking, active_focus selection, focus application, attention control, focus candidate ranking runtime, focus-to-action bridge, perception-to-action bridge, endocrine runtime, endocrine-controlled attention, action selection influence, memory write, predictor mutation, object recognition, object tracking, semantic labels, semantic vision, LLM vision, CNN, YOLO, UNet, symbol grounding claim, consciousness claim, or subjective visual experience claim

## Focus Candidate Ranking Trace Schema Check v0

Status: completed / schema-check-only / no-runtime-change.

Goal:
Validate trace-only `ranking_trace` records for focus candidate ordering.

Scope:
- adds `ashl_core.focus_candidate_ranking_trace_schema`
- adds `py -3 -m ashl_core.teaching_cli run-focus-candidate-ranking-trace-schema-check`
- validates ranking items, rank positions, score snapshots, ranking reason codes, tie breakers, lock-prevention fields, source trace, and safety flags
- enforces `total_score` as a ranking reference only, not active focus selection

Non-goals:
- no runtime focus selector, runtime ranking, active_focus selection, focus application, attention control, focus candidate ranking runtime, focus-to-action bridge, perception-to-action bridge, endocrine runtime, endocrine-controlled attention, action selection influence, memory write, predictor mutation, object recognition, object tracking, semantic labels, semantic vision, LLM vision, CNN, YOLO, UNet, symbol grounding claim, consciousness claim, or subjective visual experience claim

## Focus Candidate Ranking Trace Check v0

Status: completed / trace-check-only / no-runtime-change.

Goal:
Create a deterministic trace-only `ranking_trace` from validated `focus_candidate` records and validate it with the ranking trace schema.

Scope:
- adds `ashl_core.focus_candidate_ranking_trace`
- adds `py -3 -m ashl_core.teaching_cli run-focus-candidate-ranking-trace-check`
- reuses `focus_candidate_from_change_trace`, `focus_candidate_schema`, and `focus_candidate_ranking_trace_schema`
- orders candidates by `score_fields.total_score` descending with stable `focus_candidate_id` tie ordering as trace generation only

Non-goals:
- no runtime focus selector, runtime ranking, active_focus selection, focus application, attention control, focus candidate ranking runtime, focus-to-action bridge, perception-to-action bridge, endocrine runtime, endocrine-controlled attention, action selection influence, memory write, predictor mutation, object recognition, object tracking, semantic labels, semantic vision, LLM vision, CNN, YOLO, UNet, symbol grounding claim, consciousness claim, or subjective visual experience claim

## Focus Line Milestone Sync v0

Status: completed / documentation-milestone / boundary-index-sync.

Progress:
- completed focus trace/checker path through Focus Candidate Ranking Trace Check v0
- synced `docs/current_boundary_index.md` to Boundary Index Version `2026-06-09-b41`
- possible next stage: Focus Application Boundary Review v0 or Perception-to-Action Boundary Review v0 before any `active_focus` or `focus_applied` behavior

## Focus Application Boundary Review v0

Status: completed / design-boundary-review / no-runtime-change.

Goal:
Document the boundary between trace-only `ranking_trace` records and any future `active_focus` / `focus_applied` behavior.

Scope:
- adds `docs/focus_application_boundary_review_v0.md`
- records that `ranking_trace`, `rank_position 1`, and highest `total_score` do not select focus
- defines future focus application gate concepts, mentor interrupt priority, endocrine boundary, and Perception-to-Action Boundary Review dependency

Non-goals:
- no runtime focus selector, runtime ranking, active_focus selection, focus application, attention control, focus-to-action bridge, perception-to-action bridge, endocrine runtime, action selection influence, memory write, predictor mutation, object recognition, object tracking, semantic vision, LLM vision, CNN, YOLO, UNet, symbol grounding claim, consciousness claim, or subjective visual experience claim

## Focus Application Gate Schema Check v0

Status: completed / schema-check-only / no-runtime-change.

Goal:
Validate review-only `focus_application_gate` records for future focus application boundaries.

Scope:
- adds `ashl_core.focus_application_gate_schema`
- adds `py -3 -m ashl_core.teaching_cli run-focus-application-gate-schema-check`
- validates required review-only gates, required reason codes, source trace, and safety flags
- enforces all gates remain not passed in v0 and do not authorize runtime focus

Non-goals:
- no runtime focus selector, runtime ranking, active_focus selection, focus application, attention control, focus-to-action bridge, perception-to-action bridge, endocrine runtime, action selection influence, memory write, predictor mutation, object recognition, object tracking, semantic vision, LLM vision, CNN, YOLO, UNet, symbol grounding claim, consciousness claim, or subjective visual experience claim

## Perception-to-Action Boundary Review v0

Status: completed / design-only / no-runtime-change.

Goal:
Document the boundary between perception/focus traces and any future action influence.

Scope:
- adds `docs/perception_to_action_boundary_review_v0.md`
- states that retina features, visual_frame records, change_records, focus_candidate records, ranking_trace records, and focus_application_gate records are not action reasons, action context, action triggers, action intent, or action selection
- defines future review gates and dry-run/human-review preconditions before any perception-to-action bridge
- records mentor override, endocrine, memory, and predictor boundaries

Non-goals:
- does not add active_focus, focus_applied, attention control, perception-to-action bridge, focus-to-action bridge, action selection influence, action candidate scoring from vision, memory write, predictor mutation, persistent rule creation, endocrine runtime, object recognition, object tracking, semantic vision, symbol grounding claim, consciousness claim, or subjective visual experience claim

## Focus / Perception Boundary Construction Log v0

Status: completed / documentation-only / no-runtime-change.

Goal:
Summarize the completed eye-structure, focus trace/checker, focus application boundary, and perception-to-action boundary work for handoff.

Scope:
- adds `docs/focus_perception_boundary_construction_log_v0.md`
- records the current Boundary Index / test snapshot
- summarizes the eye-structure simulation line, focus selector trace/checker line, focus lock-prevention additions, focus application boundary/gate work, and perception-to-action boundary review
- records current safe claim, forbidden claims, next recommended options, and commit timeline

Non-goals:
- does not add runtime behavior, schemas, checks, runtime focus selector, runtime ranking, active_focus selection, focus application, attention control, perception-to-action bridge, focus-to-action bridge, vision-driven action selection, action selection influence, memory write, predictor mutation, persistent rule creation, endocrine runtime, object recognition, object tracking, semantic vision, symbol grounding claim, consciousness claim, or subjective visual experience claim

## Phase 0 Action / Lesson Loop Return Planning v0

Status: completed / planning-only / no-runtime-change.

Goal:
Record the decision to pause perception/focus runtime escalation and return to Phase 0 action/outcome/failure_reason/lesson foundations.

Scope:
- adds `docs/phase0_action_lesson_loop_return_planning_v0.md`
- explains why perception/focus work pauses at the trace/checker/review boundary
- re-states the Phase 0 action_intent -> expected_outcome -> actual_outcome -> mismatch -> structured failure_reason -> lesson_candidate -> human review loop
- lists safe next package options and recommends Action Outcome Contrast Baseline Review v0 as the immediate next planning target

Non-goals:
- does not add runtime action selection, action selection influence, new action behavior, lesson application runtime, automatic lesson application, persistent learning, persistent rule write, memory write, predictor mutation, perception-to-action bridge, focus-to-action bridge, active_focus, focus_applied, attention control, runtime focus selector, runtime ranking, endocrine runtime, endocrine-controlled action, autonomy, object recognition, semantic vision, consciousness claim, or subjective claim

## Action Outcome Contrast Baseline Review v0

Status: completed / review-only / no-runtime-change.

Goal:
Review the current Phase 0 action/outcome/failure_reason/lesson path and identify the next safe trace/checker package.

Scope:
- adds `docs/action_outcome_contrast_baseline_review_v0.md`
- reviews existing action_intent / expected_outcome / actual_outcome / mismatch / structured failure_reason / lesson_candidate / human review components
- lists related modules, tests, docs, known completed pieces, and current auditability gaps
- recommends `Expected vs Actual Outcome Pair Schema Check v0` as the next minimal package

Non-goals:
- does not add runtime action selection, action selection influence, new action behavior, action candidate scoring changes, movement control changes, lesson application runtime, automatic lesson application, persistent learning, persistent rule write, memory write, predictor mutation, perception-to-action bridge, focus-to-action bridge, active_focus, focus_applied, attention control, runtime focus selector, runtime ranking, endocrine runtime, endocrine-controlled action, autonomy, object recognition, semantic vision, consciousness claim, or subjective claim

## Expected vs Actual Outcome Pair Schema Check v0

Status: completed / schema-check-only / no-runtime-change.

Goal:
Validate the smallest reusable Phase 0 `expected_outcome` / `actual_outcome` / `mismatch` record shape with structured `failure_reason` and trace-only/review-gated boundaries.

Scope:
- adds `ashl_core.expected_actual_outcome_pair_schema`
- adds `py -3 -m ashl_core.teaching_cli run-expected-actual-outcome-pair-schema-check`
- enforces expected_outcome and actual_outcome presence
- enforces explicit boolean mismatch and blocks unknown-vs-unknown contrast pairs
- requires structured failure_reason when mismatch is true
- enforces review boundary and safety flags that block action selection, behavior change, lesson application, memory write, predictor mutation, persistent rule write, endocrine control, and autonomy

Non-goals:
- does not add runtime action selection, action selection influence, new action behavior, action candidate scoring changes, movement control changes, lesson application runtime, automatic lesson application, persistent learning, persistent rule write, memory write, predictor mutation, perception-to-action bridge, focus-to-action bridge, active_focus, focus_applied, attention control, runtime focus selector, runtime ranking, endocrine runtime, endocrine-controlled action, autonomy, object recognition, semantic vision, consciousness claim, or subjective claim

## Outcome Pair From Action Trial Trace Check v0

Status: completed / trace-check-only / no-runtime-change.

Goal:
Generate validated `expected_actual_outcome_pair` records from deterministic demo action trial traces.

Scope:
- adds `ashl_core.outcome_pair_from_action_trial_trace`
- adds `py -3 -m ashl_core.teaching_cli run-outcome-pair-from-action-trial-trace-check`
- builds expected_actual_outcome_pair records from action_intent, expected_outcome, and trial_result.actual_outcome
- uses structured state equality to set explicit mismatch in demo traces
- generates structured failure_reason when mismatch is true
- reuses `expected_actual_outcome_pair_schema` validation

Non-goals:
- does not add runtime action selection, action selection influence, new action behavior, action candidate scoring changes, movement control changes, lesson application runtime, automatic lesson application, persistent learning, persistent rule write, memory write, predictor mutation, perception-to-action bridge, focus-to-action bridge, active_focus, focus_applied, attention control, runtime focus selector, runtime ranking, endocrine runtime, endocrine-controlled action, autonomy, object recognition, semantic vision, LLM semantic comparison, free-form outcome comparison, consciousness claim, or subjective claim

## Failure Reason From Outcome Pair Check v0

Status: completed / trace-check-only / no-runtime-change.

Goal:
Extract validated structured `failure_reason` records from valid mismatch outcome pairs.

Scope:
- adds `ashl_core.failure_reason_from_outcome_pair`
- adds `py -3 -m ashl_core.teaching_cli run-failure-reason-from-outcome-pair-check`
- reuses `outcome_pair_from_action_trial_trace` and `expected_actual_outcome_pair_schema`
- uses a v0-local failure_reason validator because no standalone reusable failure_reason record schema exists
- counts mismatch false as `no_failure_reason_needed`

Non-goals:
- does not generate lesson_candidates, change action selection, change action behavior, apply lessons, write memory, persist learning, mutate predictors, add endocrine runtime, add autonomy, or claim semantic vision / consciousness / subjective experience

## Lesson Candidate From Failure Reason Check v0

Status: completed / trace-check-only / no-runtime-change.

Goal:
Create trace-only review-required `lesson_candidate` records from valid `failure_reason` records.

Scope:
- adds `ashl_core.lesson_candidate_from_failure_reason`
- adds `py -3 -m ashl_core.teaching_cli run-lesson-candidate-from-failure-reason-check`
- reuses `failure_reason_from_outcome_pair`
- uses a v0-local lesson_candidate validator because existing lesson candidate draft/review modules do not provide this standalone trace-only record schema
- enforces no approval, no lesson application, no memory write, no persistence, and no predictor mutation

Non-goals:
- does not approve lesson_candidates, apply lessons, change action selection, change action behavior, write memory, persist learning, mutate predictors, add endocrine runtime, add autonomy, or claim semantic vision / consciousness / subjective experience

## Lesson Candidate Review Gate Check v0

Status: completed / trace-check-only / no-runtime-change.

Goal:
Evaluate whether trace-only `lesson_candidate` records may enter pending human review.

Scope:
- adds `ashl_core.lesson_candidate_review_gate`
- adds `py -3 -m ashl_core.teaching_cli run-lesson-candidate-review-gate-check`
- reuses `lesson_candidate_from_failure_reason`
- produces only `pending_review` or `blocked` review gate results
- keeps `pending_review` and `eligible_for_human_review` explicitly separate from approval

Non-goals:
- does not approve or reject lesson_candidates as a human decision, apply lessons, change action selection, change action behavior, create persistent candidates, write memory, persist learning, mutate predictors, add endocrine runtime, add autonomy, or claim semantic vision / consciousness / subjective experience

## Lesson Candidate Review Evidence Summary v0

Status: completed / review-support-only / trace-check-only / no-runtime-change.

Goal:
Build reviewer-facing evidence summaries for pending_review `lesson_candidate` records.

Scope:
- adds `ashl_core.lesson_candidate_review_evidence_summary`
- adds `py -3 -m ashl_core.teaching_cli run-lesson-candidate-review-evidence-summary-check`
- reuses the lesson_candidate review gate and upstream action/outcome/failure evidence pipeline
- summarizes action_intent, outcome_pair, failure_reason, lesson_candidate, and review_gate evidence

Non-goals:
- does not add human review decision schema, approval, rejection, needs_revision, stale decision, behavior correction preview, lesson application, action selection influence, persistent learning, memory write, predictor mutation, endocrine runtime, autonomy, or semantic vision / consciousness / subjective claims

## History Runtime Persistence Gap Review v0

Status: completed / design-only / review-only / no-runtime-change.

Goal:
Clarify whether current generalized memory exact-key aggregation proves a real persisted history runtime.

Scope:
- adds `docs/history_runtime_persistence_gap_review_v0.md`
- distinguishes Session Working Memory, Generalized Memory Exact-Key Bucket, cross-session demo experience records, history runtime, persistent history store, Long-term Memory, Memory Layer, and persistent learning
- records that current generalized memory exact-key aggregation uses cross-session demo records and does not yet prove a persisted history runtime
- identifies the missing session experience record / retention / persisted history store / exact-key lookup layer
- recommends Session Experience Record Schema Design v0 as the immediate next safe package

Non-goals:
- does not add storage, memory write, persistent learning, persistent rule write, runtime history lookup, repetition_key runtime evaluation, predictor mutation, action selection influence, lesson approval, lesson rejection, behavior preview, lesson application, autonomy, semantic vision, consciousness, or subjective claims

## Lesson Candidate Human Review Decision Schema v0

Status: completed / schema-check-only / no-runtime-change.

Goal:
Define deterministic human/manual review decision records for `lesson_candidate` evidence summaries.

Scope:
- adds `ashl_core.lesson_candidate_human_review_decision_schema`
- adds `py -3 -m ashl_core.teaching_cli run-lesson-candidate-human-review-decision-schema-check`
- allows only `approved_for_preview`, `rejected`, `needs_revision`, and `stale`
- enforces source linkage to evidence_summary, lesson_candidate, review_gate, failure_reason, outcome_pair, and action_intent
- keeps `approved_for_preview` separate from lesson application approval

Non-goals:
- does not create behavior correction preview, apply lessons, add runtime action selection, modify action selection or action behavior, add persistent learning, create persistent candidates, write persistent rules, write memory, mutate predictors, add perception-to-action or focus-to-action bridge, add endocrine runtime, autonomy, semantic vision, consciousness, or subjective claims

## Reviewed Lesson Trace Preview v0

Status: completed / trace-check-only / no-runtime-change.

Goal:
Create deterministic trace-only preview records from valid human-reviewed `lesson_candidate` records.

Scope:
- adds `ashl_core.reviewed_lesson_trace_preview`
- adds `py -3 -m ashl_core.teaching_cli run-reviewed-lesson-trace-preview-check`
- reuses `lesson_candidate_from_failure_reason`, `lesson_candidate_review_gate`, `lesson_candidate_review_evidence_summary`, and `lesson_candidate_human_review_decision_schema`
- permits a valid preview only for a valid human review decision with `decision.status == approved_for_preview`
- blocks rejected, needs_revision, stale, missing review decision, source linkage mismatch, unknown preview type, lesson application, action selection influence, action behavior change, memory write, predictor mutation, persistent rule write, and persistent learning flags

Non-goals:
- does not apply lessons, change action selection, change action behavior, write memory, persist learning, write persistent rules, mutate predictors, add runtime lesson application, add LLM planning, add pathfinding, replay routes, or claim proof of learning / consciousness / subjective experience

## Lesson Review Line Milestone Sync v0

Status: completed / documentation-only / no-runtime-change.

Progress:
- Completed milestone: Phase 0 action-lesson review/preview line through Reviewed Lesson Trace Preview v0.
- Next priority group: Lesson Application Boundary Review v0, then combined Reviewed Lesson Dry-Run Correction design/schema/check, followed by dry-run correction into trial traces and before/after contrast checks.

## Lesson Application Boundary Review v0

Status: completed / design-only / no-runtime-change.

Progress:
- Documents the boundary between reviewed_lesson_trace_preview and any future dry-run correction or lesson application.
- Does not apply lessons, change action selection, write memory, persist learning, or mutate predictors.

## Reviewed Lesson Dry-Run Correction Minimal v0

Status: completed / trace-check-only / no-runtime-change.

Progress:
- Creates a small trace-only `dry_run_correction` record from `reviewed_lesson_trace_preview` and blocks all side effects.
- Does not apply lessons, change action selection or action behavior, write memory, mutate predictors, create persistent rules, or claim proof of learning.
