# ASHL Core Lab v0

ASHL Core Lab 是 ASHL Core／D清音 的最小 Python 實驗專案，用來驗證可教、可糾正、可連續、可審核的低算力唯一模型幼體核心。

核心宣言：唯一模型的唯一性，不在出生，而在成長。

## 已完成

- Core Seed Formalization v0.9
- Memory Layers v1.0
- State Persistence v1.1
- Standing Task Sandbox v1.2
- Experience Log v1.3
- Phase -1 Lesson Contribution Test v1.4
- Phase -1.1 Negative Controls v1.5
- Phase -1.2 Lesson Causality Test v1.6
- v1.7a Known Failure Reason Determinism Test
- v1.7b Unknown Failure Reason Boundary Test
- v1.8 Minimal Teaching CLI
- v1.7c Second Known Failure Reason Determinism Test
- v1.9a Multi-lesson Isolation Test
- v1.9b Conflict Detection / Require Review
- v1.9c CLI conflict_check 真實檢查
- v1.9d Cross-task Shared Prerequisite Isolation Test
- v2.0a Manual Stale Marking
- v2.0b Supersede Link
- v2.0c CLI lifecycle display
- v2.1a Supersede Replacement Suggestion
- v2.1b Strict Supersede Selection Activation
- v2.1c Activation Audit / Edge Case Hardening
- v2.2 Activation Regression Suite
- v2.3a Manual Review State Foundation
- v2.3b Manual Review CLI Display
- v2.3c Manual Review Decision CLI
- v2.3d Manual Review Decision Audit / Regression
- v2.4a Review-Gated Selection Eligibility
- v2.4b Review-Gated Eligibility Audit / Regression
- v2.4c Conflict ID Stability Check
- v2.5a Conflict Review Resolution Preview
- v2.5b Conflict Review Preview Audit / Regression
- v2.6a Conflict Review Resolution Preconditions
- v2.6b Conflict Review Resolution Dry Run
- Integrated Loop v0.1
- Persistent Candidate Layer v0.2
- Correction Label v0.3
- Rule Candidate v0.4
- Candidate Review / Audit v0.5
- Trial Rule Layer v0.6
- Trial Suggestion Feedback v0.7
- Core Senses Design v0.8
- smoke runner
- unittest
- v2.10a Sandbox Boundary / Capability Assumption Docs
- v2.10b Sandbox Failure / Trace Contract Docs
- v2.10c Sandbox Safety Audit Docs
- v2.9e-1 Voice Instinct / Audio Sense Boundary Audit Docs
- v2.8f Review Decision Trace Integration Boundary Docs
- Formal Lesson Candidate Creation Contract Docs
- Formal Lesson Candidate Creation Boundary Audit Docs
- Current Boundary Index Docs
- v2.11c Lesson Stale Supersede Memory Freeze Notice Contract
- Qingyin First Output v0 Contract
- Qingyin Runtime Ontology Boundary v0.1
- Qingyin First Output Runtime Minimal Spec

## 尚未完成

- Memory Economy
- Rule Apply
- Rule Promotion
- Mood Layer
- SQLite / Persistence Layer 正式化
- Tool Adapter
- 真攝影機 / 真螢幕感知
- Visual Impression
- Symbol Grounding v1

## Core Seed v0.9

D清音是本階段唯一模型幼體人格核心。

Core Seed 是 D清音的成長胚胎藍圖，不是完成品人格。

- Core Seed `immutable_by_default = true`。
- `personality_target` 是成長目標，不是已完成理解。
- memory candidate 不可直接改 Core Seed。
- correction label 不可直接改 Core Seed。
- rule candidate 不可直接改 Core Seed。
- trial suggestion 不可直接改 Core Seed。
- trial feedback 不可直接改 Core Seed。
- 修改 Core Seed 必須是人工版本化決策。

允許健康叛逆：拒絕破壞成長流程的要求，例如直接永久記住、跳過候選流程、跳過審核、自動啟用規則。

不允許偏移叛逆：拒絕合理教學、拒絕合理糾正、把 correction 全部視為攻擊、忽略 feedback，或用「研究不妥協」作為拒絕學習的藉口。

## Persistent Candidate Layer

JSONL artifacts：

- `data/memory_candidates.jsonl`
- `data/correction_log.jsonl`
- `data/rule_candidates.jsonl`
- `data/candidate_reviews.jsonl`
- `data/trial_feedback.jsonl`

這些檔案都是實驗資料與候選紀錄，已由 `.gitignore` 忽略。測試使用暫存資料夾，不污染 repo `data/`。

## Memory Layers v1.0

D清音的記憶不應全部混在同一個檔案中。v1.0 建立四層記憶基礎結構：

- Core Memory：只讀，不由普通流程改寫。
- Long-term Memory：只提供 append 入口，不自動固化 memory candidate。
- Working Memory：可保存 session snapshot。
- Archive Memory：可 append 封存資料。

JSONL / JSON 仍是幼體階段資料格式，暫不使用 SQLite。

`memory_candidates.jsonl` 是候選日誌，不是 Long-term Memory。

## State Persistence v1.1

State Persistence 是 D清音狀態連續性的基礎，不是 Long-term Memory，也不替代 Memory Layers。
- `persist_state` 預設為 `false`。
- `persist_state=true` 時會寫入 `state_snapshot.json`、`session_summary.json`、`last_trace_summary.json`。
- 保存 state 不改 `final_output`、不改 decision、不改 final events。
- State Persistence 不自動固化記憶，不寫入 Long-term Memory。
- 本階段仍使用 JSON，不使用 SQLite。

## Standing Task Sandbox v1.2

Standing Task Sandbox 是第一個純 Python AGE 行動沙盒。
- 任務從 `lying` 嘗試站到 `standing_stable`。
- `lying + stand_up` 會失敗並產生 `cannot_stand_directly_from_lying`。
- 修正流程會經過 `sit_up`、`stand_up`、`balance`。
- 成功後只在 trace 內產生 `lesson_candidate`。
- 本包不做持久化、不接感官、不改主循環。

## Experience Log v1.3

Experience Log 讓 standing task trace 可以轉成可回放的經驗紀錄。
- action result 可轉成 `experience_event`。
- 成功站立後可建立 `lesson_candidate`。
- 只有 `persist_experience=True` 才寫入 `experience_events.jsonl` 與 `lesson_candidates.jsonl`。
- `lesson_candidate` 仍是候選，不是 Long-term Memory。
- 本包不做 promotion、不改 Integrated Loop。

## Phase -1 Lesson Contribution Test v1.4

Phase -1 用一個荒謬規則測試 lesson layer 是否有獨立貢獻。
- 有 lesson 組會載入 `lesson_001`，先 `turn(east)` 再 `pick_up cube_001`，預期成功。
- 無 lesson 控制組不可看到 lesson、east、facing、failure reason，預期失敗。
- 工具可見但規則不可見組可以看到 `turn` 工具，但不得穩定猜中 `turn(east)`。
- runner 保存 decision input snapshot，並用 deterministic leakage check 驗證沒有提示洩漏。
- 本階段不使用 LLM 自由推理、不做 lesson review、不做 promotion、不改 Integrated Loop。

## Phase -1.1 Negative Controls v1.5

Phase -1.1 補強 lesson_001 的負控制，確認它不會過度泛化。
- `lesson_001` 只應影響 `pick_up cube_001`。
- 不套用到 `pick_up cube_002`。
- 不套用到 `push cube_001` 或 `inspect cube_001`。
- 不套用錯誤 condition，例如 `turn(west)`。
- 不套用 unrelated lesson。
- 本階段仍不做 lesson review、promotion、removal 或 replay。

## Phase -1.2 Lesson Causality Test v1.6

Phase -1.2 測試 `lesson_001` 的狀態變化是否對行為造成可追蹤的因果控制。
- `active` 時成功，且使用 `lesson_001`。
- `disabled` 時失敗，且不使用 lesson。
- `re-enabled` 時再次成功，且再次使用 `lesson_001`。
- `removed` 時失敗，且不使用 lesson。
- disabled / removed 時不得出現 `turn(east)`。
- 本階段不做 lesson review、promotion、CLI 或 Long-term Memory。

## v1.7a Known Failure Reason Determinism Test

v1.7a 只驗證已知 `failure_reason = not_facing_east` 的 lesson generation 穩定性。
- 相同輸入、相同初始狀態、相同 generator 設定下，連續生成三次。
- 排除 `id`、`created_at`、`timestamp`、`run_id` 等 volatile fields 後，核心語義欄位必須一致。
- 核心語義包含 source failure reason、generated action、target condition、status / activation state、trace reason。
- 本包不測 unknown / malformed / empty / ambiguous failure_reason。
- 不證明開放式泛化能力，不做 Minimal Teaching CLI。

目前順序：
- v1.6 Phase -1.2 Lesson Causality Test：已完成
- v1.7a Known Failure Reason Determinism Test：本包
- v1.7b Unknown Failure Reason Boundary Test：下一步
- v1.8 Minimal Teaching CLI：延後
- v1.9 Multi-lesson Conflict / Priority：延後
- v2.0 Stale / Supersede：延後

## v1.7b Unknown Failure Reason Boundary Test

v1.7b 只驗證格式正確但未知的 `failure_reason = unmapped_obstacle_shadow` 會被明確標記為 unknown。
- unknown failure_reason 會回傳 `generation_status = unknown_failure_reason`。
- 不生成 executable action。
- 不產生 active lesson。
- 不改變 behavior，不 fallback 成 `not_facing_east`。
- 不產生 `turn(east)`。
- 本包不測 malformed / empty / ambiguous failure_reason。
- 不證明開放式泛化能力，不做 multi-lesson conflict / priority。

目前順序：
- v1.6 Phase -1.2 Lesson Causality Test：已完成
- v1.7a Known Failure Reason Determinism Test：已完成
- v1.7b Unknown Failure Reason Boundary Test：本包
- v1.8 Minimal Teaching CLI：延後
- v1.9 Multi-lesson Conflict / Priority：延後
- v2.0 Stale / Supersede：延後

## v1.8 Minimal Teaching CLI

v1.8 是 CLI wrapper，只包裝現有 lesson flow，不新增 lesson generation 邏輯。
- 目前只支援 known `failure_reason = not_facing_east`。
- unknown failure_reason 只顯示 v1.7b 的 unknown 邊界結果，不生成 lesson。
- enable lesson 時，本階段不做 conflict check，輸出會標示 `conflict_check = not_implemented`。
- conflict / priority / stale / supersede 仍延後。
- 本階段不接 LLM / Web / GUI / TTS / SQLite。

常用指令：
```powershell
py -3 -m ashl_core.teaching_cli run-known-flow
py -3 -m ashl_core.teaching_cli run-unknown-flow
py -3 -m ashl_core.teaching_cli run-disable-reenable-flow
```

## v1.7c Second Known Failure Reason Determinism Test

v1.7c 新增第二條 known failure_reason 的穩定基準。
- `not_facing_west` 會生成 `turn(west)`。
- 排除 volatile fields 後，連續三次 lesson generation 的核心語義欄位一致。
- `not_facing_east` 仍維持 `turn(east)`。
- `unmapped_obstacle_shadow` 仍維持 v1.7b 的 unknown boundary。
- 本包不做 multi-lesson isolation、conflict、priority、stale / supersede。
- 不證明 open-ended lesson generation。

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

## v1.9a Multi-lesson Isolation Test

v1.9a 只驗證多條已知 lesson 在不衝突情境下可共存且互不干擾。
- `lesson_001` 來源為 `not_facing_east`，action 為 `turn(east)`。
- `lesson_002` 來源為 `not_facing_west`，action 為 `turn(west)`。
- east case 只觸發 east lesson，不產生 `turn(west)`。
- west case 只觸發 west lesson，不產生 `turn(east)`。
- `conflict_detected = false`。
- 本包不做 conflict detection、priority、require_review、stale / supersede。
- 不更新 CLI 的 `conflict_check = not_implemented`。

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

## v1.9b Conflict Detection / Require Review

v1.9b 只驗證同一 decision point 上 incompatible active lessons 會被偵測為 conflict，並進入 require_review。
- conflict 定義不是「多 lesson 同時 active」，而是同一 decision point 同時 match 且 action incompatible。
- 本包最小互斥 action：`turn(east)` 與 `turn(west)`。
- conflict 時 `conflict_detected = true`，`conflict_resolution = require_review`。
- conflict 時不自動套用任何 lesson，`selected_lesson_id = null`，`selected_action = null`。
- conflict 時不自動選 priority，不刪除 lesson，不修改 lesson 狀態。
- disable 其中一條後會恢復單 lesson 因果控制；re-enable 後恢復 require_review。
- 本包不更新 CLI 的 `conflict_check = not_implemented`。

目前順序：
- v1.9a Multi-lesson Isolation Test：已完成
- v1.9b Conflict Detection / Require Review：本包
- v1.9c CLI conflict_check 補真實檢查：下一步
- v2.0 Stale / Supersede：延後

## v1.9c CLI conflict_check 真實檢查

v1.9c 只把 CLI 的 `conflict_check` 從 `not_implemented` 升級為讀取 v1.9b conflict detection 的真實結果。
- `run-known-flow` 會顯示 `implemented = true` 且 `conflict_detected = false`。
- `run-unknown-flow` 維持 v1.7b unknown boundary。
- `run-disable-reenable-flow` 維持 v1.6 因果控制。
- 新增 `run-conflict-check-flow`，會顯示 `conflict_detected = true`、`conflict_resolution = require_review`、`review_status = pending_human_review`。
- 本包不做 priority，不做自動解衝突，不做 accept / reject / choose lesson CLI，不改 lesson 狀態。

常用指令：
```powershell
py -3 -m ashl_core.teaching_cli run-conflict-check-flow
```

目前順序：
- v1.9a Multi-lesson Isolation Test：已完成
- v1.9b Conflict Detection / Require Review：已完成
- v1.9c CLI conflict_check 真實檢查：本包
- v2.0 Stale / Supersede：下一步候選

## v1.9d Cross-task Shared Prerequisite Isolation Test

v1.9d 驗證 selection helper 可區分不同 task / object，即使多條 lesson 共享同一前置 action。
- `lesson_001`: `pick_up cube_001 -> turn(east)`
- `lesson_003`: `pick_up cube_002 -> turn(east)`
- cube_001 context 只選 `lesson_001`。
- cube_002 context 只選 `lesson_003`。
- 共享 `turn(east)` 不應誤判 conflict。
- v1.9b 的 `turn(east)` / `turn(west)` incompatible conflict 仍有效。
- 本包不做 stale、supersede、priority、require_review，也不修改 CLI conflict_check。

目前順序：
- v1.9a Multi-lesson Isolation Test：已完成
- v1.9b Conflict Detection / Require Review：已完成
- v1.9c CLI conflict_check 真實檢查：已完成
- v1.9d Cross-task Shared Prerequisite Isolation Test：本包
- v2.0a Manual Stale Marking：下一步
- v2.0b Supersede Link：延後
- v2.0c CLI lifecycle display：延後

## v2.0a Manual Stale Marking

v2.0a 只證明人工 stale 標記會讓 lesson 被 selection helper 跳過，且取消 stale 後可恢復原本因果控制。
- stale 使用 `stale = true`，保留 `status = active`。
- stale lesson 不會被選用，不產生 selected action。
- trace 會記錄 `skipped_reason = stale`。
- 取消 stale 後 `lesson_001 -> turn(east)` 可恢復。
- stale lesson 不參與 conflict 判斷。
- 本包不做自動 stale、時間過期、unused-count、failure-count、supersede 或 CLI lifecycle display。

目前順序：
- v1.9d Cross-task Shared Prerequisite Isolation Test：已完成
- v2.0a Manual Stale Marking：本包
- v2.0b Supersede Link：下一步
- v2.0c CLI lifecycle display：延後
- v2.1 Stale / Supersede activation behavior：延後

## v2.0b Supersede Link

v2.0b only records supersede links as lifecycle metadata.
- `old_lesson.superseded_by = new_lesson_id`
- `new_lesson.supersedes = old_lesson_id`
- Trace/read result shows `old_lesson_id`, `new_lesson_id`, `old_superseded_by`, `new_supersedes`, `status_changed = false`, and `selection_behavior_changed = false`.
- It does not change lesson activation.
- It does not disable old lessons.
- It does not enable new lessons.
- It does not archive old lessons.
- It does not change selection behavior.
- It does not override stale behavior.
- It does not add CLI lifecycle display.
- Supersede activation behavior is deferred to v2.1 or later.

Current order:
- v2.0a Manual Stale Marking：已完成
- v2.0b Supersede Link：已完成
- v2.0c CLI lifecycle display：本包
- v2.1 Stale / Supersede activation behavior：延後
## v2.0c CLI lifecycle display

v2.0c adds read-only CLI lifecycle display through `run-lifecycle-display`.
- It shows lesson id, status, stale, stale_reason, superseded_by, supersedes, selection eligibility, skipped reason, and conflict participation.
- It does not modify stale state.
- It does not create or modify supersede links.
- It does not change selection behavior.
- It does not change conflict behavior.
- It does not add lifecycle write commands.
- Lifecycle activation is deferred to v2.1 or later.

Example:
```powershell
py -3 -m ashl_core.teaching_cli run-lifecycle-display
```

Current order:
- v2.0a Manual Stale Marking：已完成
- v2.0b Supersede Link：已完成
- v2.0c CLI lifecycle display：本包
- v2.1 Stale / Supersede activation behavior：下一步候選
## v2.1a Supersede Replacement Suggestion

v2.1a adds trace-only supersede replacement suggestions.
- `replacement_suggestions` appear when a stale skipped lesson has `superseded_by`.
- The trace can show the stale source lesson, replacement candidate id, candidate existence, status, stale state, eligibility, and reason.
- `activation_applied` is always false.
- `replacement_suggestion` does not change selection behavior.
- `replacement_suggestion` does not change conflict behavior.
- `replacement_suggestion` does not activate supersede links.
- `replacement_suggestion` does not automatically select replacement lessons.
- It does not add lifecycle write CLI commands.
- Actual supersede selection activation is deferred to v2.1b or later.

Current order:
- v2.0a Manual Stale Marking：已完成
- v2.0b Supersede Link：已完成
- v2.0c CLI lifecycle display：已完成
- v2.1a Supersede Replacement Suggestion：本包
- v2.1b Supersede Selection Activation：下一步候選
## v2.1b Strict Supersede Selection Activation

v2.1b adds strict supersede selection activation.
- Supersede link is metadata, not authorization.
- Activation only applies when the old lesson is skipped because it is stale.
- Replacement candidate must pass normal selection eligibility.
- Activation trace records every condition: old stale, superseded_by, candidate exists, candidate active, candidate not stale, candidate eligible, source, applied state, and failed conditions.
- Activation does not add priority.
- Activation does not auto-resolve conflicts.
- Activation does not enable or disable lessons.
- Activation does not auto-mark stale.
- Conflict logic does not know or prefer supersede links.
- Multi-layer supersede chain is not supported.
- Lifecycle write CLI remains unsupported.

Current order:
- v2.1a Supersede Replacement Suggestion：已完成
- v2.1b Strict Supersede Selection Activation：本包
- v2.1c Activation Audit / Edge Case Hardening：下一步候選
## v2.1c Activation Audit / Edge Case Hardening

v2.1c is audit / hardening only.
- No new activation capability is added.
- Strict activation invariants are tested.
- Lifecycle metadata remains immutable during activation.
- Conflict logic remains independent from supersede link.
- CLI lifecycle display remains read-only.
- Multi-layer supersede chain remains unsupported.
- Priority and automatic conflict resolution remain unsupported.
- Known / unknown failure_reason behavior is unchanged.

Current order:
- v2.1b Strict Supersede Selection Activation：已完成
- v2.1c Activation Audit / Edge Case Hardening：本包
- Update log generation：下一步候選
- v2.2 Manual Review / Approval Gate or Activation Regression Suite：後續評估
## v2.2 Activation Regression Suite

v2.2 adds a long-term activation regression suite.
- No new activation capability is added.
- Strict activation conditions remain unchanged.
- Supersede link remains metadata, not authorization.
- Conflict logic remains independent from supersede relation.
- Lifecycle metadata remains immutable during activation.
- CLI lifecycle display remains read-only.
- Multi-layer supersede chain remains unsupported.
- Manual Review / Approval Gate is not implemented in this package.
- Known / unknown failure_reason behavior remains unchanged.

Current order:
- v2.1c Activation Audit / Edge Case Hardening：已完成
- v2.2 Activation Regression Suite：本包
- v2.2 Manual Review / Approval Gate：後續評估
## v2.3a Manual Review State Foundation

v2.3a adds manual review state foundation.
- Review metadata does not change selection behavior.
- Review metadata does not change conflict behavior.
- Review metadata does not change strict supersede activation.
- Approval / rejection is metadata only.
- Automatic conflict resolution is not implemented.
- Priority is not implemented.
- Lifecycle write CLI remains unsupported.
- Approved lessons are not automatically selected.
- Rejected lessons are not automatically disabled.

Current order:
- v2.2 Activation Regression Suite：已完成
- v2.3a Manual Review State Foundation：本包
- v2.3b Manual Review Persistence / Gate Design：後續評估
## v2.3b Manual Review CLI Display

v2.3b adds read-only manual review CLI display.
- `run-review-display` shows manual review items and review traces.
- CLI display does not modify review metadata.
- CLI display does not modify lesson metadata.
- CLI display does not change selection behavior.
- CLI display does not change conflict behavior.
- CLI display does not change strict supersede activation.
- Test 5 / 6 / 7 are read-only guard tests for preventing future display side effects.
- CLI approve / reject is not implemented.
- Automatic conflict resolution is not implemented.
- Priority is not implemented.

Example:
```powershell
py -3 -m ashl_core.teaching_cli run-review-display
```
## v2.3c Manual Review Decision CLI

v2.3c adds metadata-only manual review decision CLI.
- `run-review-approve` sets `review_state = reviewed` and `approval_state = approved`.
- `run-review-reject` sets `review_state = reviewed` and `approval_state = rejected`.
- Approve / reject only modifies review metadata.
- Approval does not change selection behavior.
- Rejection does not disable lessons.
- Review decision does not change conflict behavior.
- Review decision does not change strict supersede activation.
- Lesson lifecycle write CLI remains unsupported.
- Automatic conflict resolution is not implemented.
- Priority is not implemented.

Examples:
```powershell
py -3 -m ashl_core.teaching_cli run-review-approve
py -3 -m ashl_core.teaching_cli run-review-reject
py -3 -m ashl_core.teaching_cli run-review-approve --review-id review_missing
```
## v2.3d Manual Review Decision Audit / Regression

v2.3d is audit / regression only.
- No new review capability is added.
- Approve / reject remains metadata-only.
- Approval does not change selection behavior.
- Rejection does not disable lessons.
- Review decision does not change conflict behavior.
- Review decision does not change strict supersede activation.
- Lesson lifecycle write CLI remains unsupported.
- Approval-driven behavior is not implemented.
- Rejection-driven behavior is not implemented.
- Automatic conflict resolution is not implemented.
- Priority is not implemented.

## v2.4a Review-Gated Selection Eligibility

v2.4a adds review-gated selection eligibility.
- Review approval may allow the review gate to pass.
- Review rejection blocks review-gated eligibility.
- `pending_review` / `unreviewed` / missing review do not pass the review gate.
- Approval does not affect conflict behavior.
- Approval does not affect strict supersede activation conditions.
- Rejection does not mark stale.
- Rejection does not disable lessons.
- Approval does not grant priority.
- Approval does not bypass normal selection eligibility.
- Batch review query is not implemented.
- Legacy `compatibility_approved` upgrade path is not implemented in this package.
- No new review write CLI is added.

## v2.4b Review-Gated Eligibility Audit / Regression

v2.4b is audit / regression only.
- No new review gate behavior is added.
- Approved review only passes the review gate.
- Approved review does not grant priority.
- Approved review does not bypass normal selection eligibility.
- Rejected review does not mark stale.
- Rejected review does not disable lessons.
- Approval does not affect conflict behavior.
- Approval does not affect strict supersede activation conditions.
- Legacy lessons are not reclassified.
- `compatibility_approved` upgrade path is not implemented.
- Batch review query is not implemented.
- No new review write CLI is added.

## v2.4c Conflict ID Stability Check

v2.4c confirms conflict id stability and adds a deterministic `stable_conflict_key`.
- `stable_conflict_key` is generated from explicit deterministic conflict metadata.
- `stable_conflict_key` is for a future matching anchor only.
- Runtime `conflict_id` and `stable_conflict_key` are shown separately in conflict trace.
- Conflict review resolution preview is not implemented.
- Review matching is not implemented.
- Notes / reason text matching is prohibited.
- Fallback search is prohibited.
- Stable key does not change conflict behavior.
- Stable key does not change selection behavior.
- Stable key does not change strict supersede activation.

## v2.5a Conflict Review Resolution Preview

v2.5a adds conflict review resolution preview.
- Preview is trace-only.
- `resolution_preview_applied` remains false.
- Approval does not resolve conflicts.
- Approved candidate does not automatically win conflict.
- Rejection does not disable lessons.
- Rejection does not mark stale.
- Preview does not change selection behavior.
- Preview does not change strict supersede activation.
- Matching uses `stable_conflict_key` / explicit metadata only.
- Notes / reason text matching is prohibited.
- Fallback search is prohibited.
- Review-gated selection eligibility remains unchanged.
- Approval-driven conflict resolution is not implemented.
- Rejection-driven conflict resolution is not implemented.

## v2.5b Conflict Review Preview Audit / Regression

v2.5b is audit / regression only.
- No new conflict resolution capability is added.
- Conflict review preview remains trace-only.
- `resolution_preview_applied` remains false.
- Approval does not resolve conflicts.
- Approved candidate does not automatically win conflict.
- Rejection does not disable lessons.
- Rejection does not mark stale.
- Matching uses `stable_conflict_key` / explicit metadata only.
- Notes / reason text matching is prohibited.
- Fallback search is prohibited.
- Runtime `conflict_id` cannot be the only matching anchor.
- Review-gated selection eligibility remains unchanged.
- Approval-driven conflict resolution is not implemented.
- Rejection-driven conflict resolution is not implemented.

## v2.6a Conflict Review Resolution Preconditions

v2.6a adds conflict review resolution preconditions.
- This package does not perform dry-run.
- This package does not activate conflict resolution.
- `resolution_activation_applied` remains false.
- Rejected reviews are blockers only.
- Rejected reviews do not disable lessons.
- Rejected reviews do not mark stale.
- Conflicting reviews block resolution.
- Multiple approved candidates block resolution.
- Approval does not resolve conflicts.
- Approved candidate does not automatically win conflict.
- Matching uses `stable_conflict_key` / explicit metadata only.
- Notes / reason text matching is prohibited.
- Fallback search is prohibited.
- Runtime `conflict_id` cannot be the only matching anchor.

## v2.6b Conflict Review Resolution Dry Run

v2.6b adds conflict review resolution dry-run.
- This package does not activate conflict resolution.
- Dry-run does not change conflict result.
- Dry-run does not change selection result.
- Dry-run does not change strict supersede activation.
- `resolution_applied` remains false.
- Rejected reviews are blockers only.
- Rejected reviews do not disable lessons.
- Rejected reviews do not mark stale.
- Conflicting reviews block dry-run resolution.
- Multiple approved candidates block dry-run resolution.
- Approval does not resolve conflicts.
- Approved candidate does not automatically win conflict.
- Matching uses `stable_conflict_key` / explicit metadata only.
- Notes / reason text matching is prohibited.
- Fallback search is prohibited.
- Runtime `conflict_id` cannot be the only matching anchor.

## Correction / Rule / Trial Flow

- correction pending 只記錄使用者糾正。
- correction label 只分類錯誤類型。
- rule candidate 只是候選規則或候選反例。
- candidate review 只推導 current status。
- `approved_for_trial` 只會產生 inactive trial rule view。
- trial suggestion 只出現在 trace。
- trial feedback 只用於統計與未來審核。

本階段不做 Rule Apply、不建立 active rule、不自動啟用規則、不自動修改 `concepts.py`、不改 state effects。

## Core Senses v0.8

Screen Sense 與 Camera Sense 已納入 ASHL Core / D清音 的核心感官規劃。

文字能教清音「蘋果怎麼定義」，但視覺感官才有機會教她「這個東西就是蘋果」。

本階段只做資料模型與 mock sensor event：

- sensor event
- visual concept candidate
- Core Senses 設計文件

本階段不接真攝影機、不截圖、不儲存圖片、不接 OpenCV、不接 image model、不做視覺辨識。

`visual_concept_candidate` 是候選，不是正式概念。

## Roadmap

目前採用 `ASHL Core／D清音 實驗總順序 v0.2`，詳見 [docs/experiment_order.md](docs/experiment_order.md)。

下一階段不急著接攝影機。

優先補內在連續性：

- Memory Layers
- Teaching Event 完整化
- Confidence / Promotion
- Memory Economy

Core Perception 與 Visual Impression 已納入核心感官規劃，但實作延後。

## 專案結構

```text
ashl_core/
  __init__.py
  core_seed.py
  correction.py
  candidate_review.py
  memory_candidates.py
  memory_layers.py
  state_persistence.py
  persistence.py
  rule_candidates.py
  trial_rules.py
  trial_feedback.py
  senses.py
  perception.py
  concepts.py
  state_core.py
  thoughts.py
  deliberation.py
  expression.py
  guard.py
  integrated_loop.py

tests/
  test_core_seed.py
  test_correction.py
  test_candidate_review.py
  test_memory_candidates.py
  test_memory_layers.py
  test_state_persistence.py
  test_persistence.py
  test_rule_candidates.py
  test_trial_rules.py
  test_trial_feedback.py
  test_senses.py
  test_integrated_loop.py
  test_smoke.py
  test_concepts.py
  test_state_core.py
  test_expression_guard.py
  test_deliberation.py

docs/
  core_seed.md
  core_senses.md
  memory_layers.md
  state_persistence.md
  experiment_order.md
  research_plan.md

examples/
  core_sample.ashl

data/
  .gitkeep

run_all_smoke_tests.py
```

## Windows PowerShell

Windows PowerShell 請優先使用 `py -3`。

不要優先使用 `python`，因為 `python` 可能指到 WindowsApps alias。

常用指令：

```powershell
py -3 run_all_smoke_tests.py
py -3 -m unittest discover
where.exe python
where.exe py
```

## Phase 0 Integration Assumptions

- `docs/failure_reason_design_assumption_v0_1.md`
- `docs/instinct_lesson_layer_relation_assumption_v0_1.md`
- `docs/perception_layer_design_assumption_v0_1.md`
- `docs/phase0_behavior_curiosity_assumption_v0_1.md`
- `docs/phase0_failure_event_interface_assumption_v0_1.md`
- `docs/phase0_trust_curiosity_personality_boundary_v0_1.md`
  - Defines Phase 0 evaluator trust boundary, failure_event review path boundary, curiosity monitored-event boundary, and personality weight trace boundary.

These documents define the current assumptions for how Phase 0 action failures connect to lesson generation, and how the lesson layer interacts with instinct / drive behavior. They are design assumptions only and do not imply runtime implementation.

## Memory / Lesson Relation Assumptions

- `docs/lesson_memory_layer_relation_assumption_v0_1.md`

This document defines the current assumption for how the ASHL Core lesson layer relates to Qingyin Long-term Memory. It is design-only and does not imply lesson-to-memory promotion, memory writes, or memory review runtime.

Responsibility boundary: ASHL Core provides learned_principle_candidate and source evidence; Qingyin Memory Layers decide memory admission. ASHL Core does not directly write Long-term Memory.

## Phase 0 / Memory Assumption Audit

- `docs/phase0_assumption_consistency_audit_v0_1.md`

This audit document records the current consistency check across Phase 0 / Memory assumption docs. It is docs-only and does not imply runtime implementation.

## Phase 0 Failure Event Schema Foundation

v2.7a adds `ashl_core.failure_events` as a trace-only failure_event schema foundation.

- Validation is trace-only.
- No Phase 0 sandbox runtime is added.
- No evaluator runtime is added.
- No lesson_candidate builder runtime is added.
- `failure_events` does not modify selection, conflict, review, or activation behavior.
- LLM-only evaluator output cannot authorize a failure_reason.

## v2.7b Failure Event Normalization Trace

- Adds a trace-only deterministic normalization view for structured `failure_event`.
- `normalized_failure_event` is a deterministic trace view, not a new authority source.
- Does not create `lesson_candidate`.
- Does not connect sandbox runtime.
- Preserves evaluator / review / boundary assumptions.

## v2.7c Failure Event to Lesson Candidate Input Bridge Trace-only

- Adds trace-only input bridge from normalized `failure_event` to lesson candidate input view.
- `lesson_candidate_input_trace` is preparation evidence, not a `lesson_candidate`.
- Does not create `lesson_candidate`.
- Does not write `lesson_store`.
- Adds source boundary for `similar_context_hint`.
- Keeps semantic hints non-authoritative and review-required.

## v2.7c-1 Failure Event Bridge Audit / Regression Hardening

- Adds audit and regression checks for the `failure_event` -> `normalized_failure_event` -> `lesson_candidate_input_trace` pipeline.
- Confirms bridge output is not `lesson_candidate`.
- Confirms `semantic_key` remains non-authoritative and review-required.
- Confirms bridge trace fields have explicit source / authority boundaries before v2.7d.

## v2.7d Lesson Candidate Builder Contract Docs

- `docs/lesson_candidate_builder_contract_v0_1.md`
- Defines the future lesson_candidate builder contract.
- Keeps `lesson_candidate_input_trace` as preparation evidence, not `lesson_candidate`.
- Keeps `semantic_key` non-authoritative and review-required.
- Requires builder output to remain review-gated.
- Does not implement builder runtime or write `lesson_store`.

## v2.7d-1 Lesson Candidate Builder Contract Audit

- `docs/lesson_candidate_builder_contract_audit_v0_1.md`
- Audits the lesson_candidate builder contract before draft schema work.
- Confirms builder output remains review-gated.
- Confirms evidence_refs are evidence pointers, not proof.
- Confirms proposed_action_correction is not executable action.
- Confirms proposed_applicability_conditions are not verified applicability proof.

## v2.7d-2 Lesson Candidate Builder Literature Reference Supplement

- `docs/lesson_candidate_builder_literature_references_v0_1.md`
- Adds CausalFlow and LaGEA as future lesson_candidate builder references.
- Uses CausalFlow as support for causal failure_reason and counterfactual repair framing.
- Uses LaGEA as structured feedback comparison and negative reference for direct VLM suggested_fix.
- Does not implement lesson_candidate builder runtime or proposed_action_correction runtime.

## v2.8a Lesson Candidate Draft Schema Trace-only

- Adds trace-only `lesson_candidate_draft` schema.
- Requires every draft field to declare source and review_required.
- Keeps draft not approved, not active, not selection eligible, not internalized.
- Does not write `lesson_store` or Long-term Memory.

## v2.8a-1 Lesson Candidate Draft Schema Audit / Regression

- Audits `lesson_candidate_draft` schema after v2.8a.
- Confirms draft remains review-gated and not approved / active / selection eligible.
- Confirms every main draft field keeps source / authority / review_required.
- Adds `review_required = false` guard.

## v2.8a-2 Lesson Candidate Draft Strict Schema / Injection Guard

- Hardens `lesson_candidate_draft` against injected authority fields and extra-field injection.
- Requires `review_required` to behave as `Literal[True]`.
- Keeps `authority_boundary` and `review_required` internally generated.
- Rejects or marks all-null / all-unknown evidence as `insufficient_evidence`.
- Prohibits LLM-generated draft JSON.
- Ensures unknown evidence cannot produce actionable correction.

## v2.8a-3 Outcome Unknown Payload / Draft Invariant Guard

- Blocks typed unknown outcomes from becoming valid failure learning evidence.
- Treats outcome `type` as a container label, not usable evidence.
- Hardens top-level `lesson_candidate_draft` invariants.
- Requires `insufficient_evidence` to imply `not_approvable`.
- Adds repository LF line ending policy through `.gitattributes`.
- Does not change runtime selection, conflict, review, activation, lesson_store, or memory behavior.

## v2.8b Lesson Candidate Draft Review Queue Contract Docs

- `docs/lesson_candidate_draft_review_queue_contract_v0_1.md`
- Defines `review_queue_entry` / `review_task` contract for `lesson_candidate_draft`.
- Keeps queue entry and review_task as non-decision markers.
- Requires no selection-facing read APIs.
- Prohibits unreviewed drafts from being archived into any Memory Layer.
- Requires `semantic_key` presentation to avoid authority anchoring.

## v2.8b-1 Review Queue Contract Audit / Regression

- `docs/lesson_candidate_draft_review_queue_audit_v0_1.md`
- Audits `review_queue_entry` / `review_task` contract after v2.8b.
- Confirms queue entries and review tasks are not review decisions.
- Confirms review_task completion does not imply approval.
- Confirms queue exposes no selection-facing read APIs.
- Confirms queue metrics may expose counts only, never draft content or draft keys.
- Confirms timeout / expired drafts cannot be archived into any Memory Layer.
- Confirms `semantic_key` presentation remains secondary and non-authoritative.

## v2.8c Review Task Trace-only Schema

- `docs/review_task_trace_schema_v0_1.md`
- Defines trace-only `review_task_trace` schema.
- Keeps `review_task_trace` as a to-do record, not a review decision.
- Ensures review_task completion does not imply approval.
- Requires reviewer_identity to come from runtime/session context, not LLM-generated content.
- Keeps semantic_key as secondary optional hint below source_failure_norm_key.
- Does not add manual_review runtime, review decision creation, draft mutation, selection-facing read APIs, lesson_store writes, or Memory Layer writes.

## v2.8c-1 Review Task Audit / Regression

- `docs/review_task_trace_audit_v0_1.md`
- Audits `review_task_trace` after v2.8c.
- Confirms `review_task_trace` is not review decision.
- Confirms completion / closed / done does not imply approval.
- Confirms reviewer_identity cannot be injected from LLM / queue / draft input.
- Confirms semantic_key remains secondary optional hint below source_failure_norm_key.
- Confirms review_task_trace does not enter selection-facing APIs or memory_contrast_set.
- Records future rejected / deferred proposed fields masking boundary.

## v2.8d Review Decision Contract Docs

- `docs/review_decision_contract_v0_1.md`
- Defines `review_decision` as a historical event record, not a live lesson object.
- Keeps review decision docs-only / contract-only.
- Defines `decision_status` as approved / rejected / deferred only.
- Ensures approved does not create active lesson, write lesson_store, or grant selection eligibility.
- Defines rejected / deferred proposed fields masking boundary.
- Disallows partial approval.
- Does not implement manual_review runtime, review decision runtime, lesson_store writes, selection eligibility, activation, conflict logic, or Memory Layer writes.

## v2.8d-1 Review Decision Contract Audit / Regression

- `docs/review_decision_contract_audit_v0_1.md`
- Audits `review_decision` contract after v2.8d.
- Confirms approved does not create active lesson, write lesson_store, or grant selection eligibility.
- Confirms rejected / deferred proposed fields masking boundary.
- Confirms deferred is not soft approval.
- Confirms partial approval is not allowed.
- Confirms decision fields do not imply runtime permission / activation / override.

## v2.8d-2 Rejected / Deferred Proposed Fields Masking Contract Docs

- `docs/rejected_deferred_proposed_fields_masking_contract_v0_1.md`
- Defines downstream-readable masking boundary for rejected / deferred proposed fields.
- Ensures rejected / deferred proposed fields cannot be read by evaluator or memory_contrast_set.
- Defines allowed safe fields and `masked_fields_summary`.
- Prohibits debug logs from preserving proposed field content.
- Confirms deferred is not soft approval.

## v2.8e-1 Review Decision Trace Audit / Regression

- `docs/review_decision_trace_audit_v0_1.md`
- Audits review_decision_trace after v2.8e.
- Confirms approved trace grants no lesson_store write / selection eligibility / activation.
- Confirms rejected / deferred traces preserve no reusable proposed content.
- Confirms masking_policy_ref and authority_binding_policy_ref are required.
- Confirms partial / conditional approval is rejected.
- Records future runtime selector trace isolation and future authority / identity / session binding checks.

## v2.8f Review Decision Trace Integration Boundary Docs

- `docs/review_decision_trace_integration_boundary_v0_1.md`
- Integrates review_decision_trace, sandbox trace, and voice output trace boundaries.
- Confirms trace is evidence, not approval; record, not authorization; audit material, not runtime action.
- Clarifies review_decision_trace must not activate lessons, grant selection eligibility, authorize runtime behavior, write to lesson_store, or write to Memory Layer.
- Clarifies sandbox trace and voice output trace must not become review permission or bypass review_decision boundaries.
- Records bidirectional voice interaction as deferred until consultant review.
- Does not implement runtime, review decision runtime, selection eligibility runtime, activation runtime, sandbox runtime, Audio Sense / STT / TTS runtime, voice trigger runtime, or voice input-output loop.

## Formal Lesson Candidate Creation Contract Docs

- `docs/formal_lesson_candidate_creation_contract_v0_1.md`
- Defines the future contract for formal `lesson_candidate` creation.
- Clarifies creation requires structured evidence, validated boundaries, and review-ready trace.
- Clarifies formal lesson_candidate creation is not approval, lesson_store write, activation, selection eligibility, or Memory Layer promotion.
- Clarifies sandbox trace and voice output trace may support creation only as evidence.
- Requires failure_event validation and review boundaries to remain intact.
- Does not implement formal lesson_candidate creation runtime, automatic lesson_candidate builder, lesson_store writes, Memory Layer writes, selection eligibility runtime, activation runtime, sandbox runtime, or voice / audio runtime.

## Formal Lesson Candidate Creation Boundary Audit Docs

- `docs/formal_lesson_candidate_creation_boundary_audit_v0_1.md`
- Audits the formal lesson_candidate creation contract against failure_event validation, lesson_candidate_input_trace, review gate, lesson_store, Memory Layer, selection eligibility, activation, sandbox trace, voice output trace, and review_decision_trace boundaries.
- Confirms the contract does not authorize runtime, schema runtime, automatic builders, lesson_store write, Memory Layer write, activation, or selection eligibility.
- Confirms sandbox trace, voice output trace, and review_decision_trace remain evidence-only and cannot directly create formal lesson_candidate.
- Confirms raw natural language complaints and LLM-only explanations cannot directly create formal lesson_candidate.
- Records `Audit result: PASS`.
- Does not implement formal lesson_candidate creation runtime, automatic lesson_candidate builder, failure_event builder runtime, evaluator runtime, review decision runtime, selection eligibility runtime, activation runtime, sandbox runtime, voice / audio runtime, lesson_store writes, or Memory Layer writes.

## Qingyin First Output Runtime Minimal Spec

- `docs/qingyin_first_output_runtime_minimal_spec_v0_1.md`
- Defines the minimal future runtime requirements for Qingyin first_output.
- Clarifies first_output must be generated without LLM output, is not awakening, not dialogue ability, not long-term growth.
- Defines minimum input, state, allowed/prohibited output sources, first_output trace fields, and bounded randomness boundaries.
- Defines future acceptance criteria for first_output runtime.
- Clarifies first_output must be traceable before it can become learning material; lesson_candidate pipeline remains downstream.
- Does not implement any runtime.

## First Output Trace Contract

- `docs/first_output_trace_contract_v0_1.md`
- Defines the future `first_output_trace` contract.
- Clarifies `first_output_trace` is evidence of a first_output event, not proof of awakening, dialogue ability, or long-term growth.
- Requires `llm_used = false` and keeps LLM-generated text out of first_output traces.
- Defines append-only / version-preserving trace correction, output_generator_source boundaries, and bounded randomness audit requirements.
- Keeps mentor feedback and lesson_candidate input consideration downstream.
- Does not implement runtime, first_output generator, state store, trace schema runtime, lesson_store write, or Memory Layer write.

## First Output Runtime Readiness Checklist

- `docs/first_output_runtime_readiness_checklist_v0_1.md`
- Adds a docs-only readiness checklist for planning Minimal First Output Runtime v0.
- Records `Readiness result: READY_FOR_MINIMAL_FIRST_OUTPUT_RUNTIME_V0`.
- Confirms first_output non-LLM source boundaries, trace contract, `llm_used = false`, and test-object engineering boundary.
- Confirms Minimal First Output Runtime v0 must not write lesson_store or Memory Layer, must not connect to lesson_candidate pipeline, and must not claim Qingyin is awake.
- Does not implement runtime, first_output generator, state store, trace schema runtime, mentor feedback runtime, bounded senses runtime, or lesson_candidate pipeline connection.

## Minimal First Output Runtime v0

- Provides a minimal non-LLM first_output runtime for test-object engineering verification.
- Generates one fixed-reflex first_output: `*`.
- Records a `first_output_trace` with `llm_used=false`, `phase=test_object`, and `engineering_stage=test_object`.
- This is not awakening, dialogue ability, learning, or long-term growth.
- Does not connect mentor feedback, failure_event, lesson_candidate, review, selection, activation, lesson_store, Memory Layer, bounded senses, or any LLM API.

## Minimal Non-LLM Utterance Map v0

- Adds a fixed non-LLM `state_key -> utterance` map to the minimal first_output runtime.
- Default `state_key=None` still produces `first_output: *`.
- Supported keys are `unknown`, `blocked`, `observed`, `retry`, and `quiet`.
- Current utterances are `unknown -> 我不知道`, `blocked -> 不行`, `observed -> 看到了`, `retry -> 再一次`, and `quiet -> ……`.
- Mapped outputs record `utterance_source=utterance_map`, the selected `state_key`, and `llm_used=false` in `first_output_trace`.
- `run-minimal-interaction --state-key unknown` can emit and, with `--persist`, append the mapped trace to JSONL.
- This does not add LLM, prompt/API use, rule engine, grammar parser, NLP, teaching chat loop, lesson_candidate pipeline, lesson_store write, Memory Layer write, or awakening evidence.

## Micro Push-Box Tactile Sandbox v0

- Adds a tiny deterministic 2D tactile sandbox with the map `##### / #...# / #.QB# / #..G# / #####`.
- Tracks `grid`, `agent_pos`, `box_pos`, `goal_pos`, and `tick`.
- Supports a fixed allowed action set: `touch_*`, `move_*`, `push_*`, and `wait`.
- Emits `tactile_sandbox_trace` records with `before`, `after`, `contact`, `result`, `blocked`, and current positions.
- Result vocabulary includes `empty`, `wall_blocked`, `box_contact`, `box_pushed`, `box_blocked`, and `goal_reached`.
- This is not an AI solver, pathfinding, learning, lesson_candidate pipeline, lesson_store write, Memory Layer write, LLM / teaching chat loop, graphics / GUI, or senses runtime.

## Micro Push-Box Allowed Action Set v0

- Defines `ALLOWED_ACTION_SET` as the fixed set of 13 sandbox actions: `touch_up/down/left/right`, `move_up/down/left/right`, `push_up/down/left/right`, and `wait`.
- Adds `validate_allowed_action(...)`; invalid actions such as diagonal moves, natural language commands, free-form commands, and external tool actions raise `ValueError`.
- Adds `wait` as a deterministic tactile sandbox action. It increments `tick`, does not move the agent or box, returns `result = wait`, `contact = none`, `blocked = false`, and keeps `trace_type = tactile_sandbox_trace`.
- This does not add AI solver / pathfinding, learning, tactile result mapping changes, lesson_candidate pipeline, lesson_store / Memory Layer writes, LLM / teaching chat loop, natural language action parsing, or external actions.

## Tactile Result State Key Mapping v0

- Adds a fixed lookup table from tactile sandbox result to first_output `state_key`.
- Mapping: `wall_blocked -> blocked`, `box_blocked -> blocked`, `box_contact -> observed`, `box_pushed -> observed`, `goal_reached -> observed`, `empty -> quiet`.
- `blocked` maps through the utterance map to `不行`; `observed` maps to `看到了`; `quiet` maps to `……`.
- Unknown tactile results raise `ValueError`.
- This does not modify sandbox behavior, add learning, add solver / pathfinding, connect lesson_candidate, write lesson_store or Memory Layer, or add LLM / teaching chat / NLP.

## Micro Push-Box Tactile Interaction CLI Bridge v0

- Adds `py -3 -m ashl_core.teaching_cli run-tactile-interaction --action <action>`.
- The deterministic CLI flow is: sandbox action -> tactile result -> `state_key` -> utterance map -> JSON output.
- JSON output includes `tactile_result`, `state_key`, `utterance`, `tactile_sandbox_trace`, and boundary flags.
- `push_right` in the default sandbox maps to `box_blocked -> blocked -> 不行`; `touch_right` maps to `box_contact -> observed -> 看到了`.
- Boundary flags remain false for `llm_used`, `creates_lesson_candidate`, `writes_lesson_store`, `writes_memory_layer`, and `awakening_claim`.
- Invalid actions fail through the allowed action validation path.
- This does not add LLM / prompt / API use, teaching chat loop, AI solver / pathfinding, learning, lesson_candidate pipeline, failure_event / review / selection / activation, lesson_store / Memory Layer writes, graphics / GUI, or senses runtime.

## Repeated Blocked Action Trace v0

- Adds in-state `action_history` to the micro push-box sandbox trace flow.
- Each tactile trace includes a `history` block showing whether the same action was attempted before.
- Repeating `push_right` in the default sandbox records the previous same-action result as `box_blocked` and its tick.
- Different actions do not count as same-action history.
- This is trace evidence only. It does not add learning, action selection, avoid-same-action behavior, solver / pathfinding, lesson_candidate pipeline, lesson_store / Memory Layer writes, LLM / teaching chat, or JSONL persistence.

## State-Action Outcome Memory v0

- Adds local state-action context readback for micro push-box `action_history`.
- `action_history` entries now record `agent_pos`, `box_pos`, `goal_pos`, `action`, `result`, and `tick`.
- Adds `build_state_action_key(...)`, `find_previous_same_state_action_result(...)`, `score_action_from_state_action_memory(...)`, `rank_candidate_actions_by_state_action_memory(...)`, and `suggest_next_action_by_state_action_memory(...)`.
- Scores only reuse prior results when `agent_pos`, `box_pos`, `goal_pos`, and `action` all match the current context.
- This is in-state sandbox history readback, not AI solver / pathfinding, learning pipeline, lesson_candidate pipeline, lesson_store / Memory Layer write, LLM / teaching chat, tactile result mapping change, utterance_map change, or persistent memory.

## Micro Navigation Goal-Reach v0

- Adds an independent `ashl_core.micro_navigation_sandbox` with a tiny fixed grid: `##### / #...# / #.Q.# / #..G# / #####`.
- Navigation state records `grid`, `agent_pos`, `goal_pos`, and `tick`.
- Allowed actions are closed to `move_up`, `move_down`, `move_left`, `move_right`, and `wait`.
- Navigation traces record `trace_type = navigation_sandbox_trace`, `tick`, `action`, `before`, `after`, `result`, `blocked`, `agent_pos`, `goal_pos`, and `distance_to_goal`.
- Adds `run_navigation_goal_trial(candidate_actions=None, max_steps=10)` for a bounded goal-reach trial.
- This is a tiny Level 0 navigation sandbox, not a modification to push-box sandbox, AI solver / pathfinding, goal planning, learning pipeline, lesson_candidate pipeline, lesson_store / Memory Layer write, LLM / teaching chat, graphics, or GUI.

## Micro Navigation Multi-Goal Level v0

- Adds a deterministic multi-step navigation level with a fixed map: `####### / #Q....# / #.###.# / #....G# / #######`.
- Internal navigation coordinates keep the existing `(row, col)` convention.
- Initial agent position is `(1, 1)`.
- Goal sequence is `((3, 5), (3, 1))`.
- Multi-goal state records `agent_pos`, `goal_pos`, `goal_index`, `goals_reached`, and `tick`.
- Reaching the first goal increments `goals_reached`, increments `goal_index`, and spawns the second goal.
- Reaching the final goal completes the trial.
- Multi-goal traces record `goal_reached_this_step`, `goal_index`, `goals_reached`, and `next_goal_spawned`.
- Adds `run_navigation_multi_goal_trial(candidate_actions=None, max_steps=20)` for a bounded two-goal navigation trial.
- This is a deterministic multi-goal level, not a modification to push-box sandbox, AI solver / pathfinding, goal planning, learning pipeline, lesson_candidate pipeline, lesson_store / Memory Layer write, LLM / teaching chat, graphics, or GUI.

## Micro Navigation Multi-Goal Metrics CLI v0

- Adds `py -3 -m ashl_core.teaching_cli run-navigation-multi-goal-metrics --runs 4 --trial-count 5 --max-steps 20`.
- The CLI wraps repeated calls to the existing `run_navigation_multi_goal_trial(...)` helper and returns JSON with `flow = navigation_multi_goal_metrics_cli_v0`, `status = ok`, run summaries, total trials, total completed trials, overall success rate, overall average step count, max-steps reached count, and `human_summary`.
- Per-run summaries include `run_index`, `completed_count`, `trial_count`, `success_rate`, `step_counts`, `average_step_count`, `min_step_count`, `max_step_count`, `max_steps_reached_count`, and `trial_summaries`.
- Trial summaries use multi-goal semantics: `completed_all_goals`, `goals_reached`, `goal_count`, `step_count`, and `selected_actions`.
- Boundary flags remain false for `llm_used`, `creates_lesson_candidate`, `writes_lesson_store`, `writes_memory_layer`, `awakening_claim`, and `changes_navigation_behavior`.
- This is metrics readback only. It does not modify navigation runner behavior, navigation sandbox behavior, push-box sandbox behavior, add AI solver / pathfinding, goal planning, learning pipeline, lesson_candidate pipeline, lesson_store / Memory Layer writes, LLM / teaching chat, or metric-driven behavior change.

## Navigation Obstacle / Wall Detour Level v0

- Adds `create_navigation_obstacle_level_state()` for a deterministic obstacle navigation level using the fixed map `####### / #Q....# / #.###.# / #....G# / #######`.
- Adds one-step `select_navigation_action_blocked_aware(...)` selection: it ignores wall-blocked move candidates, chooses the non-wall candidate with minimum Manhattan distance to the goal, and preserves candidate order on ties.
- Adds `run_navigation_obstacle_trial(candidate_actions=None, max_steps=20)` as a bounded detour trial runner.
- Trial summaries include `completed_goal`, `step_count`, `stop_reason`, `selected_actions`, `final_agent_pos`, `goal_pos`, and `steps`.
- Step traces keep `trace_type = navigation_sandbox_trace`, `action`, `before`, `after`, `result`, `blocked`, `agent_pos`, `goal_pos`, and `distance_to_goal`.
- This is a 2D curriculum level and blocked-aware one-step selector, not 3D / GMod, AI solver, pathfinding, BFS, A*, goal planning, learning pipeline, lesson_candidate pipeline, lesson_store / Memory Layer write, LLM / teaching chat, graphics, or GUI.

## Navigation Obstacle Trial CLI Patch

- Adds `py -3 -m ashl_core.teaching_cli run-navigation-obstacle-trial`.
- Supports `--max-steps`.
- The CLI wraps the existing `run_navigation_obstacle_trial(max_steps=...)` helper.
- Output includes `command`, `flow = navigation_obstacle_trial_cli_patch`, `status`, `completed_goal`, `step_count`, `stop_reason`, `initial_agent_pos`, `goal_pos`, `final_agent_pos`, `selected_actions`, `wall_blocked_avoided`, and `boundary`.
- Boundary flags remain false for `llm_used`, `creates_lesson_candidate`, `writes_lesson_store`, `writes_memory_layer`, `awakening_claim`, and `changes_navigation_behavior`.
- This is a CLI wrapper only. It does not modify navigation runner behavior, navigation sandbox behavior, push-box sandbox behavior, add AI solver / pathfinding / BFS / A*, goal planning, learning pipeline, lesson_candidate pipeline, lesson_store / Memory Layer writes, LLM / teaching chat, graphics, or GUI.

## Approach Box Level v0

- Adds `create_navigation_approach_box_level_state()` for a Level 1 navigation/push-box bridge where the agent approaches a box but does not push it.
- Approach-box state contains `grid`, `agent_pos`, `box_pos`, and `tick`; it intentionally has no `goal_pos`.
- Adds `manhattan_distance_to_box(agent_pos, box_pos)`.
- Adds `apply_navigation_approach_box_action(...)` with `trace_type = navigation_approach_box_trace`.
- Approach-box trace records `tick`, `action`, `before`, `after`, `result`, `blocked`, `agent_pos`, `box_pos`, `distance_to_box`, and `box_adjacent`.
- Results are `moved`, `wall_blocked`, `box_adjacent`, or `wait`.
- Adds `run_navigation_approach_box_trial(candidate_actions=None, max_steps=20)`, which stops when `distance_to_box == 1`.
- This is not box pushing, not a push-box sandbox modification, not AI solver / pathfinding / BFS / A*, not goal planning, not learning pipeline, not lesson_candidate pipeline, not lesson_store / Memory Layer write, not LLM / teaching chat, and not graphics / GUI.

Two-Trial History Boundary:
- Future Trial 2 may read only local state-action outcome memory with `agent_pos`, `box_pos`, optional `goal_pos`, `action`, `result`, and `tick`.
- Trial 2 must not read full trace routes, replay selected_actions, reconstruct full paths, create lesson_candidate, write lesson_store, write Memory Layer / Long-term Memory, use LLM planning, or treat trace as memory.
- The next package candidate is Approach Box Two-Trial Learning Check v0.

## Approach Box Trial CLI v0

- Adds `py -3 -m ashl_core.teaching_cli run-approach-box-trial`.
- Supports `--max-steps`.
- The CLI wraps the existing `run_navigation_approach_box_trial(max_steps=...)` helper.
- Output includes `completed_approach`, `initial_agent_pos`, `box_pos`, `final_agent_pos`, `final_distance_to_box`, `step_count`, `selected_actions`, and `llm_used = false`.
- Boundary flags remain false for lesson_candidate creation, lesson_store write, Memory Layer write, Two-Trial Learning Check, pathfinding, and box pushing.
- This is a PowerShell-verifiable CLI wrapper only. It does not modify the approach-box runner, navigation sandbox, push-box sandbox, add box pushing, Two-Trial Learning Check, lesson_candidate pipeline, lesson_store / Memory Layer writes, LLM planning, pathfinding / BFS / A*, or full route replay.

## Approach Box Two-Trial Learning Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-approach-box-two-trial-check`.
- Supports `--max-steps`.
- Runs Trial 1 and Trial 2 on the existing approach-box level, then reports `trial_1`, `trial_2`, `comparison`, and `boundary_check`.
- Trial 1 writes only local state-action outcome memory with `agent_pos`, `box_pos`, optional `goal_pos`, `action`, `result`, and `tick`.
- Trial 2 may read only that local state-action outcome memory. It must not read full trace, full route, selected_actions replay, lesson_candidate, lesson_store, Memory Layer, Long-term Memory, LLM planning, or human hint.
- This is local memory verification only, not proof of learning, not full push-box solve, not pathfinding, and not LLM planning.

## Approach Box Dead-End Level v0

- Adds `py -3 -m ashl_core.teaching_cli run-approach-box-dead-end-trial --max-steps 100`.
- The level fixture starts at `initial_agent_pos = [1, 1]` with `box_pos = [4, 4]`.
- The only valid approach position is `[3, 4]`; `[4, 3]` is a wall and is not an approach position.
- Output records `entered_dead_end_area`, `dead_end_positions_visited`, and `blocked_or_failed_actions`.
- This is a bounded dead-end trial wrapper. It does not modify the existing approach-box runner, navigation sandbox, push-box sandbox, action selection, goal bias, state-action memory, penalty / stuck detection, or add pathfinding / BFS / A*.
- This is not Two-Trial Learning Check, not proof of learning, not lesson_candidate creation, not lesson_store / Memory Layer write, not LLM planning, and not full route replay.

## Approach Box Dead-End Two-Trial Learning Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-approach-box-dead-end-two-trial-check --max-steps 100`.
- Runs Trial 1 on `approach_box_dead_end_v0`, writes only local state-action outcome memory, then runs Trial 2 on the same dead-end level with Trial 1 local memory available.
- Output records `trial_1`, `trial_2`, `comparison`, and `boundary_check`.
- Trial 2 reports whether it read local memory, avoided the Trial 1 dead-end blocked action, reduced dead-end visits, reduced blocked/failed actions, and changed step count.
- This is dead-end local memory verification only. It is not proof of learning, not full route replay, not Trial 1 `selected_actions` replay, not pathfinding / BFS / A*, not lesson_candidate / lesson_store / Memory Layer use, and not LLM planning.

## Dead-End Memory Control Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-approach-box-dead-end-memory-control-check --max-steps 100 --runs 20`.
- Compares `with_memory` against `without_memory` on the existing `approach_box_dead_end_v0` level.
- `with_memory` Trial 2 may read only Trial 1 local outcome memory; `without_memory` Trial 2 must not read local memory.
- Output records aggregate Trial 2 dead-end entry counts, blocked/failed totals, average step counts, completion counts, and control-group comparison deltas.
- The output also reports `trial1_source_audit` and `conditioned_on_trial1_dead_end`, so the control check can distinguish runs where Trial 1 actually generated dead-end local memory source evidence before evaluating Trial 2 avoidance.
- This is a bounded A/B control check, not proof of general learning. It does not use LLM planning, pathfinding / BFS / A*, full route replay, Trial 1 `selected_actions` replay, lesson_candidate, lesson_store, or Memory Layer.

## Dead-End Two-Trial ASCII Replay v0

- Adds `py -3 -m ashl_core.teaching_cli replay-approach-box-dead-end-two-trial --max-steps 100`.
- Renders every step of the existing dead-end two-trial check as an ASCII grid with action, result, agent position, dead-end markers, and blocked events.
- This is observer output only. It does not modify the runner, action selection, local memory logic, or memory-control behavior.
- This command does not use LLM planning, pathfinding / BFS / A*, UI / GUI, lesson_candidate, lesson_store, or Memory Layer, and it is not proof of general learning.

## Dead-End Map Trial1 Validation v0

- Adds `py -3 -m ashl_core.teaching_cli validate-dead-end-trial1-maps --runs-per-map 3 --max-steps 100`.
- Validates candidate dead-end maps before Two-Trial or A/B memory tests by running Trial 1 style checks where the current fixture supports it.
- Reports `map_status`, completion counts, dead-end entry counts, blocked/failed totals, step counts, samples, and an overall recommendation.
- Candidate maps are now wired as fixed fixtures for Trial 1 validation, with `fixture_loaded` and `fixture_load_error` reported for each map.
- Fixture support does not mean a map is valid for Two-Trial; the validation CLI reports whether each map is usable.
- Bad maps are reported honestly rather than forced to pass.
- This command does not run Two-Trial, does not run A/B memory control, does not use LLM planning, does not use pathfinding / BFS / A*, and is not proof of learning.

## Candidate Map Trial1 ASCII Replay v0

- Adds `py -3 -m ashl_core.teaching_cli replay-dead-end-trial1-candidate-maps --max-steps 100`.
- Renders Trial 1 for all candidate dead-end maps as ASCII grids, including valid maps and shortcut maps.
- This is observer output only for inspecting paths before further experiments.
- This command does not run Two-Trial, does not run A/B memory control, does not use LLM planning, does not use pathfinding / BFS / A*, and is not proof of learning.

## Valid Dead-End Maps A/B Control v0

- Adds `py -3 -m ashl_core.teaching_cli run-valid-dead-end-maps-ab-control --runs-per-map 3 --max-steps 100`.
- Runs A/B memory control only on maps that passed Trial 1 validation.
- Excludes shortcut maps such as `user_maze_dead_end_candidate_v0`.
- Trial 2 does not replay the Trial 1 route or receive Trial 1 `selected_actions` as input.
- This command does not use LLM planning, does not use pathfinding / BFS / A*, and is not proof of general learning.

## Local Memory Decision Trace Observer v0

- Adds `py -3 -m ashl_core.teaching_cli observe-local-memory-decision-trace --level-id approach_box_dead_end_v0 --max-steps 100`.
- Explains Trial 2 decision traces for valid dead-end maps by showing candidate actions, relevant local memory, selected actions, and non-numeric action explanations.
- This is observer output only and does not modify action selection, goal bias, or state-action memory.
- This command does not use LLM planning, does not use pathfinding / BFS / A*, and is not proof of general learning.

## Session Working Memory v0

- Adds a session-local generic state-action-outcome working memory plus `py -3 -m ashl_core.teaching_cli demo-session-working-memory --max-records 20`.
- Session Working Memory is short-term only and stores generic state-action-outcome records.
- It is not wall-specific, not dead-end-specific, and not Long-term Memory.
- `failure_reasons` is always a list, so unknown and multiple failure reasons are supported.
- This memory does not write lesson_store or Memory Layer and is not proof of general learning.

## Session Working Memory Trial Integration v0

- Adds `py -3 -m ashl_core.teaching_cli run-session-working-memory-trial --level-id approach_box_dead_end_v0 --max-steps 100 --max-records 20`.
- Runs a bounded Trial 1 style observer and records generic state-action-outcome records into session-local working memory.
- The memory is short-term only and is cleared at session end.
- This command does not write lesson_store or Memory Layer, does not modify action selection, and is not proof of general learning.

## State Snapshot Key v0

- Session Working Memory now derives stable `state_key` values from `state_snapshot`.
- `state_key` is for indexing and trace clarity: `state_key + action -> outcome`.
- Missing optional fields such as `box_pos` or `goal_pos` use stable `null` placeholders.
- This does not modify action selection, does not write Long-term Memory, and does not connect lesson_store or Memory Layer.

## Session Working Memory Phase Handoff v0

- `docs/session_working_memory_phase_handoff_v0.md`
- Closes the current Session Working Memory phase and summarizes completed memory capabilities, boundaries, and current data shape.
- Next phase direction: Simulated Vision Facing / Viewport v0 using structured symbolic simulated vision, not real images, pathfinding, or LLM vision.

## Simulated Vision Facing / Viewport v0

- Adds `py -3 -m ashl_core.teaching_cli run-simulated-vision-viewport-demo`.
- Introduces symbolic viewport input with position and facing: `pos = (x, y)` and `facing = north / east / south / west`.
- Supported actions are `turn_left`, `turn_right`, `look`, and `move_forward`.
- Viewport symbols are `w` wall, `e` empty, `i` item/object, and `x` out of view/unknown; the center may use `a` for the agent.
- This is not real image vision, does not use LLM vision, does not use pathfinding, and does not prove visual grounding.

## Simulated Vision Session Memory Bridge v0

- Adds `py -3 -m ashl_core.teaching_cli run-simulated-vision-memory-bridge-demo`.
- Records symbolic viewport observations and simulated vision action outcomes into session-local working memory.
- Memory records include `state_key`, `state_snapshot`, viewport, visible symbols, action, outcome, failure reasons, and trace metadata.
- Session memory is cleared at session end.
- This does not modify action selection, does not use real images, LLM vision, or pathfinding, and does not prove visual understanding or symbol grounding.

## Simulated Vision Observed Local Map v0

- Adds `py -3 -m ashl_core.teaching_cli run-simulated-vision-observed-map-demo`.
- Separates `current_viewport` from session-local `observed_local_map`.
- `current_viewport` means what is visible now; `observed_local_map` stores previously observed cells for the current session.
- `x` means currently unseen or unknown and does not erase previously observed known symbols.
- No unseen cells are inferred from the source map.
- This does not use real images, LLM vision, or pathfinding, and does not prove visual understanding or symbol grounding.

## Simulated Vision Symbol Grounding Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-simulated-vision-symbol-grounding-check`.
- Verifies bounded symbolic relations between visible front symbols and immediate `move_forward` outcomes: `w -> blocked`, `e -> moved`, and `i -> item_contact`.
- The front symbol is read from the current symbolic viewport front-center cell.
- This checks a bounded symbolic relation between visible symbols and immediate move_forward outcomes.
- This is structured symbolic vision only; it does not use real images, LLM vision, or pathfinding.
- This does not prove visual understanding or solve symbol grounding.

## Grounded Action Experience v0

- Adds `py -3 -m ashl_core.teaching_cli run-grounded-action-experience-check`.
- Records bounded experiences: front symbol + attempted action + immediate outcome.
- Follows the intended chain: `see -> interact -> outcome -> experience record`.
- This does not make the agent react directly from sight and does not use experience to modify action selection yet.
- This does not use real images, LLM vision, pathfinding, or long-term memory.
- This does not claim visual understanding, solved symbol grounding, or general learning.

## Grounded Action Experience Influence v0

- Adds `py -3 -m ashl_core.teaching_cli run-grounded-action-experience-influence-check`.
- Tests the chain: `see -> interact -> outcome -> experience -> later action influence`.
- Influence requires a matching prior experience; a no-experience wall control proves seeing `w` alone does not suppress `move_forward`.
- In this runner only, prior `w + move_forward -> blocked` suppresses a later `move_forward` candidate and selects a turn fallback.
- This does not add pathfinding, route planning, item seeking, long-term memory, or visual understanding claims.

## Micro Navigation Trial Metrics CLI v0

- Adds `py -3 -m ashl_core.teaching_cli run-navigation-trial-metrics --runs 4 --trial-count 5 --max-steps 10`.
- The CLI wraps repeated calls to the existing `run_navigation_goal_trial(...)` helper and returns JSON with `flow = navigation_trial_metrics_cli_v0`, `status = ok`, run summaries, total trials, total completed trials, overall success rate, overall average step count, max-steps reached count, and `human_summary`.
- Per-run summaries include `run_index`, `completed_count`, `trial_count`, `success_rate`, `step_counts`, `average_step_count`, `min_step_count`, `max_step_count`, and `max_steps_reached_count`.
- Boundary flags remain false for `llm_used`, `creates_lesson_candidate`, `writes_lesson_store`, `writes_memory_layer`, `awakening_claim`, and `changes_navigation_behavior`.
- This is metrics readback only. It does not modify navigation runner behavior, navigation sandbox behavior, push-box sandbox behavior, add AI solver / pathfinding, goal planning, learning pipeline, lesson_candidate pipeline, lesson_store / Memory Layer writes, LLM / teaching chat, or metric-driven behavior change.

## Minimal Avoid Repeated Blocked Action v0

- Adds `suggest_next_action_avoiding_repeat_blocked(state, candidate_actions)`.
- The helper scans candidate actions in order and returns the first candidate whose latest same-action history is not `box_blocked`, `wall_blocked`, or `blocked`.
- If all candidates are blocked, it returns `wait`, which is already an allowed sandbox action.
- Invalid candidate actions raise `ValueError` through the allowed action validation path.
- This is a deterministic helper, not AI solver / pathfinding, goal planning, learning, lesson_candidate pipeline, lesson_store / Memory Layer write, LLM / teaching chat, tactile result mapping change, or utterance_map change.

## Minimal Action Outcome Weighting v0

- Adds fixed `OUTCOME_WEIGHTS` for tactile sandbox results: blocked outcomes score negative, neutral outcomes score zero, `box_pushed` scores positive, and `goal_reached` scores highest.
- Adds `score_action_from_history(...)`, `rank_candidate_actions_by_outcome_weight(...)`, and `suggest_next_action_by_outcome_weight(...)`.
- Helpers only read `state.action_history`, validate candidate actions, preserve stable candidate order on score ties, and do not mutate state.
- Example: history `push_right -> box_blocked`, `push_down -> box_pushed` ranks `push_down` above `push_right`.
- This is deterministic outcome weighting, not AI solver / pathfinding, goal planning, learning pipeline, lesson_candidate pipeline, lesson_store / Memory Layer write, LLM / teaching chat, tactile result mapping change, or utterance_map change.

## Minimal Goal Direction Bias v0

- Adds `manhattan_distance_to_goal(...)`, `score_action_goal_direction(...)`, `rank_candidate_actions_with_goal_bias(...)`, and `suggest_next_action_with_goal_bias(...)`.
- Goal direction bias reads `box_pos`, `goal_pos`, and the box-on-goal direction only; push actions that reduce box-to-goal Manhattan distance score `+2`, push actions that increase it score `-2`, and non-push actions score `0`.
- Ranking combines existing outcome history weight with goal direction bias while preserving candidate order on ties.
- Helpers validate candidate actions, do not mutate state, and do not add new actions.
- This is minimal directional bias, not AI solver / pathfinding, goal planning, learning pipeline, lesson_candidate pipeline, lesson_store / Memory Layer write, LLM / teaching chat, tactile result mapping change, or utterance_map change.

## Minimal Intrinsic Action Selection v0

- Adds `select_intrinsic_action(state, candidate_actions, random_seed=None)` for the micro push-box sandbox.
- Selection is bounded to the supplied `candidate_actions` and validates every candidate against `ALLOWED_ACTION_SET`.
- Uses existing action outcome weights first, then bounded randomness only among tied best candidates.
- The same `random_seed` gives the same tied-candidate result; different seeds may vary only within the supplied candidates.
- Example: history `push_right -> box_blocked`, `push_down -> box_pushed`, candidates `["push_right", "push_down"]` selects `push_down`.
- This is minimal candidate selection, not AI solver / pathfinding, goal planning, learning pipeline, lesson_candidate pipeline, lesson_store / Memory Layer write, LLM / teaching chat, tactile result mapping change, or utterance_map change.

## Box-on-Goal Need State v0

- Adds `build_box_on_goal_need_state(state)` for the micro push-box sandbox.
- The need schema is `need_name = box_on_goal`, `target_value = 1`, `current_value = 0 or 1`, and `satisfied = true or false`.
- `current_value` is `1` only when `state["box_pos"] == state["goal_pos"]`; otherwise it is `0`.
- Tactile sandbox traces include `need_state`; a `goal_reached` trace reports `satisfied = true`.
- This is a minimal need-state readout, not emotion / dopamine runtime, AI solver / pathfinding, goal planning, learning pipeline, lesson_candidate pipeline, lesson_store / Memory Layer write, LLM / teaching chat, tactile result mapping change, or utterance_map change.

## Minimal Need-State Driven Action Selection v0

- Adds `select_action_for_need_state(state, candidate_actions, random_seed=None)`.
- The helper reads `build_box_on_goal_need_state(state)` and returns `selected_action`, `need_state`, `selection_reason`, and `candidate_actions`.
- If `box_on_goal` is unsatisfied, it delegates to `select_intrinsic_action(...)`; example history `push_right -> box_blocked`, `push_down -> box_pushed` selects `push_down`.
- If `box_on_goal` is satisfied, it selects `wait` with `selection_reason = need_satisfied_wait`.
- This is a minimal need-state selection helper, not AI solver / pathfinding, goal planning, learning pipeline, lesson_candidate pipeline, lesson_store / Memory Layer write, LLM / teaching chat, emotion / dopamine runtime, tactile result mapping change, or utterance_map change.

## Need-State Driven Trial Runner v0

- Adds `run_need_state_driven_trial(candidate_actions, max_steps=10, random_seed=None)`.
- Runs the default micro push-box state for a bounded number of steps by reading `box_on_goal`, selecting from `candidate_actions`, applying the tactile action, and recording each step.
- Each step records `step_index`, `selected_action`, `selection_reason`, `selection_source`, `tactile_result`, `need_state`, `agent_pos`, `box_pos`, and `trace`.
- The summary returns `completed_goal`, `stop_reason`, `step_count`, `final_need_state`, `final_result`, and `steps`.
- This is a finite trace runner, not AI solver / pathfinding, goal planning, learning pipeline, lesson_candidate pipeline, lesson_store / Memory Layer write, LLM / teaching chat, tactile result mapping change, or utterance_map change.

## Need-State Trial Goal Bias Integration v0

- Need-state trial runner step selection now includes goal direction bias for unsatisfied need-state steps; the current integrated trace records `selection_source = state_action_memory_plus_outcome_weight_plus_goal_bias_plus_repetition_penalty`.
- The integration uses existing outcome weighting and goal direction bias helpers while keeping selected actions bounded to `candidate_actions`.
- Goal-improving push bias applies only when the push can immediately contact the box; otherwise the runner preserves bounded intrinsic selection behavior.
- Batch summaries keep the existing `trial_count`, `step_counts`, `average_step_count`, `min_step_count`, `max_step_count`, and `trials` schema.
- This integration is not AI solver / pathfinding, goal planning, learning pipeline, lesson_candidate pipeline, lesson_store / Memory Layer write, LLM / teaching chat, tactile result mapping change, or utterance_map change.

## State-Action Memory Trial Runner Integration v0

- Need-state trial runner step selection now records `selection_source = state_action_memory_plus_outcome_weight_plus_goal_bias_plus_repetition_penalty`.
- Unsatisfied need-state steps record `state_action_memory_used = true`.
- The runner combines local state-action outcome memory score, existing outcome history weight, and goal direction bias when ordering candidate actions.
- Same-context local memory can lower a previously blocked action and raise a previously pushed action, while different contexts do not reuse prior local results.
- Selected actions remain bounded to `candidate_actions`, and batch summaries keep `trial_count`, `step_counts`, `average_step_count`, `min_step_count`, `max_step_count`, and `trials`.
- This integration uses in-state sandbox action history only. It is not AI solver / pathfinding, goal planning, learning pipeline, lesson_candidate pipeline, lesson_store / Memory Layer write, persistent state-action memory, LLM / teaching chat, tactile result mapping change, or utterance_map change.

## Stuck Detection / Repetition Penalty v0

- Adds `detect_stuck_from_recent_steps(steps, window_size=3)` for recent trial step traces.
- Stuck detection requires the recent window to have the same selected action, no `goal_reached`, and no `need_state.current_value` improvement.
- Adds `score_action_repetition_penalty(steps, action, window_size=3)` with `-2` for two recent repeats, `-4` for three or more recent repeats, and `0` otherwise.
- Need-state trial runner selection scoring now combines state-action memory, outcome weight, goal direction bias, and repetition penalty.
- Unsatisfied need-state steps record `stuck_detected_before_selection` and `repetition_penalty_applied`.
- This is bounded candidate scoring, not AI solver / pathfinding, goal planning, learning pipeline, lesson_candidate pipeline, lesson_store / Memory Layer write, persistent memory, LLM / teaching chat, tactile result mapping change, utterance_map change, or new action creation.

## Need-State Trial Runner 5-Trial Step Count v0

- Adds `run_need_state_driven_trial_batch(trial_count=5, candidate_actions=None, max_steps=10, random_seed=None)`.
- The batch helper runs `run_need_state_driven_trial(...)` from the default micro push-box state for each trial.
- Returns `trial_count`, `completed_count`, `step_counts`, `average_step_count`, `min_step_count`, `max_step_count`, and `trials`.
- Each trial summary includes `trial_index`, `completed_goal`, `stop_reason`, `step_count`, `final_need_state`, and `selected_actions`.
- This is trial step-count readback, not action selection behavior change, AI solver / pathfinding, goal planning, learning pipeline, lesson_candidate pipeline, lesson_store / Memory Layer write, LLM / teaching chat, or free text conversation.

## Need-State Trial Batch CLI v0

- Adds `py -3 -m ashl_core.teaching_cli run-need-state-trial-batch`.
- Optional arguments: `--trial-count`, `--max-steps`, and `--random-seed`.
- The CLI wraps the existing `run_need_state_driven_trial_batch(...)` helper and returns JSON with `flow = need_state_trial_batch_cli_v0`, `status = ok`, batch step-count statistics, trial summaries, and explicit boundary flags.
- Boundary flags remain false for `llm_used`, `creates_lesson_candidate`, `writes_lesson_store`, `writes_memory_layer`, and `awakening_claim`.
- This CLI wrapper does not change the trial runner, sandbox behavior, action selection behavior, learning pipeline, lesson_candidate pipeline, lesson_store writes, Memory Layer writes, or free text conversation.

## Trial Metrics Comparison CLI v0

- Adds `py -3 -m ashl_core.teaching_cli run-trial-metrics-comparison --runs 4 --trial-count 5 --max-steps 10`.
- Optional arguments: `--runs`, `--trial-count`, `--max-steps`, and `--random-seed`.
- The CLI wraps repeated calls to the existing `run_need_state_driven_trial_batch(...)` helper and returns JSON with `flow = trial_metrics_comparison_cli_v0`, `status = ok`, run summaries, total trials, total completed trials, overall success rate, overall average step count, max-steps reached count, and a human-readable summary.
- Per-run summaries include `run_index`, `completed_count`, `trial_count`, `success_rate`, `step_counts`, `average_step_count`, `min_step_count`, `max_step_count`, and `max_steps_reached_count`.
- Boundary flags remain false for `llm_used`, `creates_lesson_candidate`, `writes_lesson_store`, `writes_memory_layer`, `awakening_claim`, and `changes_trial_runner_behavior`.
- This is metrics readback only. It does not modify trial runner behavior, add AI solver / pathfinding, goal planning, learning pipeline, lesson_candidate pipeline, lesson_store writes, Memory Layer writes, LLM / teaching chat, or autonomous behavior.

## Trial Metrics Baseline Snapshot v0

- Adds `data/baselines/trial_metrics_baseline_v0.json`.
- The baseline was produced from `py -3 -m ashl_core.teaching_cli run-trial-metrics-comparison --runs 4 --trial-count 5 --max-steps 10 --random-seed 17`.
- Baseline metadata records `baseline_id`, `created_for`, `source_command`, `commit`, `boundary_index_version`, `parameters`, `metrics`, and `notes`.
- The snapshot records `runs = 4`, `trial_count = 5`, `max_steps = 10`, `random_seed = 17`, `total_trials = 20`, `total_completed = 13`, `overall_success_rate = 0.65`, `overall_average_step_count = 6.6`, and `max_steps_reached_count = 7`.
- This baseline is for comparison only. It does not modify behavior and is not proof of learning by itself.
- This package does not modify trial runner behavior, sandbox behavior, metrics-driven behavior, learning pipeline, lesson_candidate pipeline, lesson_store / Memory Layer writes, LLM / teaching chat, AI solver / pathfinding, or goal planning.

## Trial Metrics Baseline Comparison v0

- Adds `py -3 -m ashl_core.teaching_cli compare-trial-metrics-baseline`.
- Also supports `py -3 -m ashl_core.teaching_cli run-trial-metrics-baseline-compare`.
- The CLI reads `data/baselines/trial_metrics_baseline_v0.json`, reruns trial metrics comparison with the baseline parameters, and reports baseline/current/delta fields.
- Output includes `same_config_used = true`, `comparison_only = true`, and `proof_of_learning = false`.
- This is metrics readback only. It does not modify trial runner behavior, action selection, goal bias, state-action memory, penalty / stuck detection, learning rules, lesson_candidate pipeline, lesson_store / Memory Layer writes, LLM planning, or behavior.

## Sandbox Working State Clear CLI v0

- Adds `py -3 -m ashl_core.teaching_cli clear-sandbox-working-state --session-id <session_id>`.
- Returns JSON with `working_state_cleared = true`, `append_only_traces_preserved = true`, `cleared`, and `preserved`.
- Clearable working-state categories are `action_history`, `sandbox_session_state`, and `temporary_session_state`.
- Preserved append-only trace paths include `data/first_output_traces.jsonl` and `data/mentor_feedback_traces.jsonl`.
- If no persistent sandbox working state exists, the command returns `cleared = []` and `reason = no_persistent_working_state_found`.
- This does not delete `data/*.jsonl`, append-only traces, lesson_store, Memory Layer data, or `data/`; it does not modify `trace_persistence.py`, add learning, connect lesson_candidate, or use LLM / teaching chat.

## Grounded Learning Verification CLI v0

- Adds `py -3 -m ashl_core.teaching_cli run-grounded-learning-check --actions push_right push_right`.
- The verification flow creates the default micro push-box state, applies each tactile action, maps tactile result to `state_key`, maps `state_key` to utterance, preserves trace history, and suggests the next action through the existing repeated-blocked helper.
- Default verification shows both `push_right` steps as `box_blocked -> blocked -> 不行`; the second step records previous `push_right = box_blocked`.
- The suggested next action for candidate actions `["push_right", "wait"]` is `wait`.
- This is verification evidence only. It does not add LLM / prompt / API use, natural language parser, teaching chat loop, AI solver / pathfinding, actual learning pipeline, lesson_candidate pipeline, failure_event / review / selection / activation, lesson_store / Memory Layer writes, graphics / GUI, or senses runtime.

## Minimal First Output Runtime Audit

- `docs/minimal_first_output_runtime_audit_v0_1.md`
- Audits Minimal First Output Runtime v0.
- Records `Audit result: PASS`.
- Confirms the first_output is non-LLM, `llm_used=false`, test_object stage, and trace-only evidence.
- Confirms it does not write lesson_store or Memory Layer and does not connect to mentor feedback, lesson_candidate, failure_event, review, selection, activation, bounded senses, or voice systems.
- Clarifies this runtime is not awakening, not dialogue ability, and not long-term growth.

## Mentor Feedback Stub Contract

- `docs/mentor_feedback_stub_contract_v0_1.md`
- Defines the future `mentor_feedback_stub` contract for first_output_trace.
- Clarifies mentor feedback is downstream of first_output_trace, but does not create lesson_candidate, write lesson_store, write Memory Layer, or prove awakening.
- Defines minimal feedback labels and future mentor_feedback_trace conceptual fields.
- Does not implement mentor feedback runtime, teaching chat loop, mentor_feedback_trace schema runtime, lesson_candidate pipeline connection, lesson_store write, or Memory Layer write.

## Mentor Feedback Trace Contract

- `docs/mentor_feedback_trace_contract_v0_1.md`
- Defines the future `mentor_feedback_trace` contract.
- Clarifies `mentor_feedback_trace` is downstream of first_output_trace, records mentor feedback, and may make first_output_trace eligible for later lesson_candidate input consideration.
- Clarifies `mentor_feedback_trace` does not create lesson_candidate, write lesson_store, write Memory Layer, or prove awakening.
- Defines required fields, minimal feedback labels, and append-only / version-preserving boundary.
- Does not implement mentor feedback runtime, teaching chat loop, mentor_feedback_trace schema runtime, lesson_candidate pipeline connection, lesson_store write, or Memory Layer write.

## Minimal Mentor Feedback Stub Runtime Readiness Checklist

- `docs/minimal_mentor_feedback_stub_runtime_readiness_checklist_v0_1.md`
- Adds a docs-only readiness checklist for planning Minimal Mentor Feedback Stub Runtime v0.
- Records `Readiness result: READY_FOR_MINIMAL_MENTOR_FEEDBACK_STUB_RUNTIME_V0`.
- Confirms source first_output_trace exists, mentor_feedback_stub contract exists, mentor_feedback_trace contract exists, feedback labels are defined, required trace fields are defined, and feedback-only boundaries are established.
- Confirms no lesson_candidate creation, no lesson_store write, no Memory Layer write, no failure_event / review / selection / activation creation, and no awakening / dialogue / growth claim.
- Does not implement runtime, mentor feedback runtime, mentor_feedback_trace schema runtime, teaching chat loop, lesson_candidate pipeline connection, or any lesson_store / Memory Layer write.

## Minimal Mentor Feedback Stub Runtime v0

- Provides a minimal local mentor_feedback_trace builder for test-object engineering supervision.
- Creates feedback-only mentor_feedback_trace records for an existing first_output_trace.
- Accepts `source_first_output_trace_id`, `mentor_feedback_label`, optional note, and `mentor_source`.
- Supports labels: `observed`, `acceptable`, `retry`, `invalid`, and `unsafe`.
- This is not teaching chat, not lesson_candidate creation, not lesson_store write, not Memory Layer write, and not awakening.

## Minimal Mentor Feedback Stub Runtime Audit

- `docs/minimal_mentor_feedback_stub_runtime_audit_v0_1.md`
- Audits Minimal Mentor Feedback Stub Runtime v0.
- Records `Audit result: PASS`.
- Confirms it produced a feedback-only mentor_feedback_trace for `source_first_output_trace_id: first_output_trace:final_check:1` with label `observed`.
- Confirms `creates_lesson_candidate=false`, `writes_lesson_store=false`, `writes_memory_layer=false`, and `engineering_stage=test_object`.
- Clarifies this runtime is not awakening, not dialogue ability, and not long-term growth.

## Minimal Interaction CLI Bridge v0

- Provides a minimal CLI command that runs:
  `first_output -> first_output_trace -> mentor_feedback_trace`.
- Command: `py -3 -m ashl_core.teaching_cli run-minimal-interaction`
- Default flow:
  - first_output: `*`
  - mentor_feedback_label: `observed`
  - llm_used: `false`
  - creates_lesson_candidate: `false`
  - writes_lesson_store: `false`
  - writes_memory_layer: `false`
  - engineering_stage: `test_object`
- This is not dialogue, not learning, not Memory Layer write, and not awakening.

## Minimal Interaction CLI Bridge Audit

- `docs/minimal_interaction_cli_bridge_audit_v0_1.md`
- Audits Minimal Interaction CLI Bridge v0.
- Records `Audit result: PASS`.
- Confirms command `run-minimal-interaction` produces first_output, first_output_trace, and mentor_feedback_trace.
- Confirms default `mentor_feedback_label` is `observed` and `--notes` is preserved in mentor_feedback_trace.
- Confirms the CLI bridge does not use LLM, create lesson_candidate, write lesson_store, write Memory Layer, or claim awakening.

## First Output + Mentor Feedback Append-only Persistence Spec

- `docs/first_output_feedback_append_only_persistence_spec_v0_1.md`
- Defines future append-only persistence rules for `first_output_trace` and `mentor_feedback_trace`.
- Specifies future JSONL targets: `data/first_output_traces.jsonl` and `data/mentor_feedback_traces.jsonl`.
- Requires append-only, no overwrite, no silent correction, correction as a new trace, and raw trace preservation.
- Clarifies persistence is not lesson_store write, not Memory Layer write, not lesson_candidate creation, and not awakening evidence.
- Does not implement JSONL writes or persistence runtime.

## First Output + Mentor Feedback Persistence Readiness Checklist

- `docs/first_output_feedback_persistence_readiness_checklist_v0_1.md`
- Adds a docs-only readiness checklist for planning First Output + Mentor Feedback Append-only Persistence Runtime v0.
- Records `Readiness result: READY_FOR_FIRST_OUTPUT_FEEDBACK_APPEND_ONLY_PERSISTENCE_V0`.
- Confirms first_output_trace, mentor_feedback_trace, append-only persistence spec, and target JSONL paths are defined.
- Confirms no overwrite, no silent correction, correction as a new trace, and raw trace preservation.
- Does not write JSONL, implement persistence runtime, write lesson_store, write Memory Layer, connect lesson_candidate pipeline, or claim awakening.

## First Output + Mentor Feedback Append-only Persistence v0

- Provides append-only JSONL helpers for `first_output_trace` and `mentor_feedback_trace`.
- Targets `data/first_output_traces.jsonl` and `data/mentor_feedback_traces.jsonl`.
- Creates the target data directory if missing and appends one JSON object per line.
- Validates trace boundaries and rejects unsafe values such as `llm_used=true`, lesson candidate creation, lesson_store writes, or Memory Layer writes.
- `run-minimal-interaction` remains non-persistent by default; `--persist` enables append-only trace persistence and `--data-dir` can point tests at a temporary directory.
- This is not lesson_store write, not Memory Layer write, not lesson_candidate creation, not failure_event / review / selection / activation, and not awakening evidence.

## Append-only Persistence Runtime Audit

- `docs/append_only_persistence_runtime_audit_v0_1.md`
- Audits append-only JSONL persistence runtime at commit `468d4e2`.
- Records `Audit result: PASS`.
- Confirms first_output and mentor_feedback trace targets, append-only behavior, no overwrite, no silent correction, and no input mutation.
- Confirms invalid trace boundaries are rejected and persistence remains outside lesson_store, Memory Layer, lesson_candidate creation, and awakening evidence.
- Does not change persistence runtime behavior, add replay / readback runtime, or connect LLM / teaching chat / free text conversation.

## Qingyin Runtime Ontology Boundary v0.1

- `docs/qingyin_runtime_ontology_boundary_v0_1.md`
- Defines that Qingyin is not the current LLM conversation instance and is not yet a continuously running runtime individual.
- Clarifies ASHL Core is currently building the conditions for Qingyin to grow, not proving Qingyin is already growing.
- Defines minimum gates for Qingyin runtime session and cross-session growth.
- Defines four ontology tags for classifying assumption docs: Existing Runtime / Trace-only Foundation / Runtime Assumption / Persona-Ontology Assumption.
- Clarifies LLM allowed and forbidden roles.
- Adds the test-object / shallow-sleep / awakening three-stage ontology and clarifies that Qingyin's importance is not in birth, but in growth.
- Does not implement any runtime.

## Qingyin First Output v0 Contract

- `docs/qingyin_first_output_contract_v0_1.md`
- Defines that Qingyin's first output must be produced by ASHL Core rules, state, seed, or bounded randomness, not by an LLM.
- Clarifies Qingyin is not the current LLM conversation instance.
- Clarifies LLM-generated text must not count as Qingyin's first output.
- Clarifies first_output may be random or nonsensical if generated by ASHL Core.
- Clarifies first_output is not dialogue ability, not long-term growth, and must be traceable before becoming learning material.
- Defers bidirectional voice interaction, Audio Sense, STT, TTS, and lesson_candidate pipeline connection.
- Does not implement any runtime.

## v2.11c Lesson Stale Supersede Memory Freeze Notice Contract

- `docs/lesson_stale_supersede_memory_freeze_notice_contract_v0_1.md`
- Defines memory_freeze_required notice as evidence, not Memory Layer write.
- Clarifies ASHL Core provides evidence; D清音 Memory Layers decide memory freeze application.
- Adds pure-data `build_memory_freeze_notice` helper to lesson_store.py (no side effects, no Memory Layer write).
- Notice preserves source_lesson_id and stale_or_supersede_reason.
- Notice does not change selection eligibility, activation state, or lesson_store.
- Does not implement Memory Layer freeze runtime or Long-term Memory write runtime.

## Current Boundary Index Docs

- `docs/current_boundary_index.md`
- Adds a short, versioned, low-token source of global hard boundaries for future work packages.
- Current version: `Boundary Index Version: 2026-06-06-b30`.
- Lists current global hard boundaries and deferred areas.
- Compression patch keeps the version at b25 while aggregating repeated boundary lines to preserve room for future sync packages.
- Requires the file to be updated every time an Update Log is generated.
- Does not add runtime behavior, modify existing design document content, or introduce new boundary design decisions.

## Current Boundary Index Batch 27 Sync Patch

- Updates `docs/current_boundary_index.md` from Batch 26 to Batch 27.
- Adds Batch 27 hard boundaries for need-state trial runner measurement, trial batch step-count interpretation, and distance-based goal direction bias.
- Marks goal direction bias integration into trial runner, stable trial metrics comparison, stuck detection / repetition penalty, autonomous goal planning, full learning pipeline, lesson_candidate pipeline, lesson_store write, Memory Layer write, LLM response generation, teaching chat loop, and free text conversation as deferred.
- Keeps the boundary index under 150 lines.
- Does not add runtime behavior or modify sandbox, CLI, need-state, or goal-bias logic.

## Current Boundary Index Batch 28 Sync Patch

- Updates `docs/current_boundary_index.md` from Batch 27 to Batch 28.
- Adds Batch 28 hard boundaries for local state-action outcome memory, context-bound reuse, trial metrics comparison as measurement-only, and `human_summary` as report text rather than Qingyin utterance.
- Marks stuck detection / repetition penalty runtime, stable metrics comparison across fixed seeds, automatic behavior modification from metrics, persistent state-action memory, full learning pipeline, lesson_candidate pipeline connection, lesson_store write, Memory Layer write, LLM response generation, teaching chat loop, and free text conversation as deferred.
- Keeps the boundary index under 150 lines.
- Does not add runtime behavior or modify sandbox, CLI, trial runner, metrics, lesson_store, or Memory Layer logic.

## Current Boundary Index Batch 29 Sync Patch

- Updates `docs/current_boundary_index.md` from Batch 28 to Batch 29.
- Adds Batch 29 hard boundaries for micro navigation goal-reach as curriculum level, multi-goal navigation as sequential marker following, multi-goal traces as evidence rather than pathfinding, stuck detection / repetition penalty as not-yet-proven improvement, and push-box full solve as deferred.
- Marks micro navigation multi-goal metrics CLI, obstacle / wall detour navigation level, approach-box level, push-box full solve, stable navigation curriculum metrics, lesson_candidate pipeline connection, lesson_store write, Memory Layer write, LLM response generation, teaching chat loop, and free text conversation as deferred.
- Keeps the boundary index under 150 lines.
- Does not add runtime behavior or modify navigation sandbox, push-box sandbox, CLI, lesson_store, Memory Layer, lesson_candidate pipeline, or AI solver / pathfinding logic.

## Current Boundary Index Batch 30 Sync Patch

- Updates `docs/current_boundary_index.md` from Batch 29 to Batch 30.
- Adds Batch 30 hard boundaries for approach-box as object-approach verification, not push behavior or box understanding.
- Records the Two-Trial History Boundary: future Trial 2 may read only local state-action outcome memory with `agent_pos`, `box_pos`, optional `goal_pos`, `action`, `result`, and `tick`.
- Marks Approach Box Trial CLI, Approach Box Two-Trial Learning Check, Trial Metrics Baseline Snapshot, Push Once Level, push-box full solve, lesson_candidate pipeline connection, lesson_store write, Memory Layer write, LLM response generation, teaching chat loop, and free text conversation as deferred.
- Keeps the boundary index under 150 lines.
- Does not add runtime behavior or modify navigation sandbox, push-box sandbox, CLI, lesson_store, Memory Layer, lesson_candidate pipeline, or AI solver / pathfinding logic.

## v2.8e Review Decision Trace-only Schema

- `docs/review_decision_trace_schema_v0_1.md`
- Defines trace-only `review_decision_trace` schema.
- Allows decision_status approved / rejected / deferred only.
- Keeps approved from writing lesson_store, activating lessons, or granting selection eligibility.
- Requires rejected / deferred decisions to reference masking policy.
- Requires decision authority / reviewer identity / session binding policy references.
- Does not implement manual_review or review decision runtime.

## v2.8d-3 Decision Authority / Reviewer Identity / Session Binding Contract Docs

- `docs/decision_authority_reviewer_identity_session_binding_contract_v0_1.md`
- Defines decision_authority / reviewer_identity / reviewer_session_token binding boundary.
- Requires reviewer_identity and reviewer_session_token to come from runtime/session context.
- Prohibits LLM / draft / queue / external text identity injection.
- Defines decision_authority as review verdict authority only, not runtime capability.
- Does not implement auth, session, manual_review, or review decision runtime.

## Memory Compression Strategy Assumption Patch Index

- `docs/memory_compression_strategy_assumption_patch_v0_1.md`
- Defines text-stage memory compression assumptions.
- Requires text memory compression to preserve text fragment, source context summary, confidence level, and usage count.
- Marks the strategy as text-memory-stage-only.
- Defers image memory compression until visual sensory grounding exists.
- Prohibits reusing text-only compression strategy for image memory.
- Defers text / image relational compression until Symbol Grounding v1.
- Does not implement memory compression runtime.

## v2.9b Soft / Hard Consolidation Assumption Index

- `docs/soft_hard_consolidation_assumption_v0_1.md`
- Defines soft consolidation and hard consolidation assumptions.
- Records target-directed reasoning risk around review bypass.
- Defines Core Seed as current hard-consolidated layer.
- Requires Core Seed, review flow, self-modification boundary, and soft/hard boundary definition to be hard-consolidated.
- Allows Qingyin to propose hard consolidation but not complete it alone.
- Does not implement soft / hard consolidation runtime.

## v2.10b Sandbox Failure / Trace Contract Docs

- `docs/sandbox_failure_trace_contract_v0_1.md`
- Defines sandbox failure as observed experimental mismatch inside a bounded sandbox.
- Clarifies sandbox failure is not authoritative failure_reason.
- Clarifies sandbox trace is evidence, not approval.
- Defines minimum fields for future sandbox failure trace schema.
- Clarifies sandbox trace may support later failure_event construction but must not bypass failure_event validation.
- Defines sandbox-to-failure_event bridge path: requires structured failure_event, normalize, lesson_candidate pipeline, review gate.
- Does not implement sandbox runtime, trace schema runtime, or evaluator runtime.

## v2.10c Sandbox Safety Audit Docs

- `docs/sandbox_safety_audit_v0_1.md`
- Audits v2.10a sandbox boundary assumptions and v2.10b sandbox failure trace contract.
- Confirms sandbox docs do not authorize sandbox runtime, external tools, or real-world actions.
- Confirms sandbox trace does not bypass failure_event validation or review gate.
- Confirms sandbox docs do not authorize lesson_store write, Memory Layer write, executable repair, direct lesson_candidate creation, or memory promotion.
- Records `Audit result: PASS`.
- Does not implement sandbox runtime, evaluator runtime, failure_event builder runtime, lesson_candidate builder runtime, review / selection / activation behavior changes, or Memory Layer writes.

## v2.10a Sandbox Boundary / Capability Assumption Docs

- `docs/sandbox_boundary_capability_assumption_v0_1.md`
- Defines sandbox as observable, replayable, limited, interruptible, and trace-producing experimental environment.
- Clarifies sandbox result / success / failure / repair / trace are not equivalent to lesson, approved knowledge, failure_reason, executable action, or memory promotion.
- Defines sandbox isolation boundary: no lesson_store write, no Memory Layer write, no real-world actions.
- Defines sandbox-to-lesson path: sandbox output may provide evidence only; must pass through failure_event / lesson_candidate / review pipeline.
- Lists pre-conditions required before any future sandbox runtime implementation.
- Does not implement sandbox runtime, external tool runtime, or real-world action capability.

## v2.9e Voice Instinct Assumption Index

- `docs/voice_instinct_assumption_v0_1.md`
- Defines voice as instinct, not skill.
- Places voice instinct in the expressive layer of Qingyin's artificial instinct system.
- Maps voice learning onto the existing action learning pattern: actual_output / expected_output / mismatch / failure_reason / lesson_candidate / review.
- Clarifies early vocal imitation is not language understanding.
- Defines initial voice tone as designer-provided starting direction, not final identity.
- Defines Qingyin's voice as her developmental result, not a real-person voice clone.
- Marks voice instinct trigger conditions as future Audio Sense-dependent design.
- Does not implement STT / TTS / Audio Sense / voice training runtime.

## v2.9e-1 Voice Instinct / Audio Sense Boundary Audit Docs

- `docs/voice_instinct_audio_sense_boundary_audit_v0_1.md`
- Audits v2.9e Voice Instinct assumptions against Audio Sense, STT, TTS, voice training, voice cloning, failure_event, lesson_candidate, review, and Memory Layer boundaries.
- Confirms Voice Instinct docs do not authorize voice instinct runtime, Audio Sense runtime, STT / TTS runtime, voice training runtime, or real-person speaker imitation.
- Confirms early voice imitation is not language understanding.
- Confirms initial voice parameters are starting conditions, not Qingyin's final voice identity.
- Confirms voice output mismatch must still pass through failure_event / lesson_candidate / review boundaries before learning.
- Records `Audit result: PASS`.
- Does not implement voice instinct runtime, Audio Sense runtime, STT / TTS runtime, voice training runtime, voice cloning, lesson_store writes, or Memory Layer writes.

## v2.9c-1 Equivocation Handling / Trace Trust Boundary Correction

- `docs/equivocation_trace_trust_boundary_correction_v0_1.md`
- Corrects v2.9c equivocation handling priority.
- Clarifies that language ambiguity is normal learning behavior, not risk by itself.
- Defines prediction error / learning mechanism as primary defense for impactful semantic drift.
- Defines trace as secondary retrospective tool, not primary protection.
- Defines mentor intervention as final defense, not continuous monitoring.
- Preserves hard-consolidated operational definitions for healthy rebellion and paranoia.
- Does not implement equivocation detection runtime or prediction error tracking.

## v2.9c Memory Paranoia / Misinformation / Equivocation Risk Assumption Index

- `docs/memory_paranoia_misinformation_equivocation_risk_assumption_v0_1.md`
- Defines misinformation as factual knowledge update problem.
- Defines paranoia as learning-mechanism openness collapse, not merely incorrect content.
- Defines value knowledge as a high-risk area for paranoia.
- Adds operational distinction between healthy rebellion and paranoia.
- Adds equivocation handling: semantic drift cannot be fully prevented, but must be trace-visible.
- Marks healthy rebellion / paranoia operational definitions as hard-consolidated concepts.
- Requires paranoia warning signs to be observed by external mentor, not Qingyin herself.
- Does not implement paranoia detection runtime or prediction error tracking.

## v2.9d Core Seed Design Spirit Supplement

- `docs/core_seed_design_spirit_supplement_v0_1.md`
- Adds the design spirit behind Qingyin's Core Seed.
- Defines gentleness, curiosity, questioning, uncertainty, and direction-finding as research-oriented traits.
- Distinguishes inherited skeleton from self-grown content.
- Keeps learning method, core value direction, and verification requirement as non-divergent inheritance.
- Allows Qingyin to differ in professional judgment, worldview, and conclusions.
- Marks the supplement as hard-consolidation-related without implementing Core Seed runtime changes.

## v2.9a Pathological Risk / Actor Role / Protection Assumption Index

- `docs/pathological_risk_role_protection_assumption_v0_1.md`
- Adds pathological risk, actor role, and protection mechanism assumptions.
- Defines mentor / cursor_mr / system_limit / self_choice actor boundaries.
- Defines functional depression as prediction-failure-driven action collapse.
- Incorporates Maier & Seligman 2016: passivity is the default response; control must be learned.
- Requires protected success contexts to preserve traceable action_candidate -> outcome causality.
- Does not implement deprivation_error, learning_progress, curiosity satisfaction, actor_trust_delta, or protection runtime.

## Simulated Vision First-Person Viewport Correction v0

- Corrects the symbolic simulated vision 3x3 viewport from a centered top-down crop to a Doom-like forward view.
- The agent marker `a` is at bottom center `viewport[2][1]`.
- The immediate front cell for `move_forward` is `viewport[1][1]`.
- The far front cell is `viewport[0][1]`.
- This remains symbolic simulated vision, not real image vision or visual understanding.

## Simulated Vision Grounding Milestone Log v0

- Added `docs/milestone_logs/simulated_vision_grounding_milestone_2026-06-09.md` after first-person viewport correction and grounded action experience influence validation.

## Simulated Vision Larger Sandbox Design v0

- Added `docs/simulated_vision_larger_sandbox_design_v0.md` as a design-only larger test-room sandbox plan; no runtime, CLI, pathfinding, item collection, exit activation, curiosity, prediction error, or home sandbox behavior was added.

## Simulated Vision Larger Sandbox Static Runtime v0

- Adds `py -3 -m ashl_core.teaching_cli run-simulated-vision-larger-sandbox-demo`.
- Loads the larger symbolic test-room map with first-person viewport symbols `w/e/i/d/g/x/a`.
- `D` is passable and rendered as `d`, but is not taught as a semantic room boundary.
- `E` is rendered as static placeholder `g`; no conditional exit activation or task completion is added.
- No item collection, curiosity, prediction error, place memory, pathfinding, route planner, or home sandbox behavior is added.

## Larger Sandbox Observed Map Smoke v0

- Adds `py -3 -m ashl_core.teaching_cli run-larger-sandbox-observed-map-smoke`.
- Verifies `observed_local_map` can remember `d/i/g` symbols in the larger static sandbox.
- Confirms `x` does not erase known cells and unseen cells are not inferred.
- Does not add item collection, exit activation, curiosity, prediction error, place memory, pathfinding, or home sandbox behavior.

## Larger Sandbox Symbol Contact Smoke v0

- Adds `py -3 -m ashl_core.teaching_cli run-larger-sandbox-symbol-contact-smoke`.
- Verifies immediate contact outcomes: `d -> moved / passage_crossed`, `i -> item_contact`, and `g -> exit_contact`.
- Does not add item collection, exit activation, task completion, curiosity, prediction error, place memory, pathfinding, or home sandbox behavior.

## Larger Sandbox Human Replay v0

- Adds `py -3 -m ashl_core.teaching_cli replay-larger-sandbox-human`.
- Supports `--mode demo`, `--mode contact`, and `--mode observed-map`.
- Prints a plain-text, human-readable replay from existing larger sandbox traces and contact/observed-map smoke outputs.
- Front symbol display uses the first-person immediate front cell `viewport[1][1]`.
- Readability replay only: no runtime behavior, action selection, pathfinding, item collection, exit activation, curiosity, prediction error, place memory, home sandbox, or visual understanding claim is added.

## Larger Sandbox Flask Visual UI Prototype v0

- Adds `py -3 -m ashl_core.teaching_cli run-larger-sandbox-ui`.
- Provides a localhost-only Flask visual control panel for manual inspection of the larger sandbox.
- Shows current first-person viewport, position/facing/front symbol, action buttons, reset, legend, boundary notes, and a human-readable action log.
- Does not add pathfinding, route planning, item collection, exit activation, curiosity, prediction error, place memory, home sandbox, or visual understanding claims.

## Adjustable Action Cooldown v0

- Adds configurable manual action cooldown to the larger sandbox Flask UI.
- Default cooldown is `0.5s`; accepted range is `0.0s` to `5.0s`, where `0.0s` disables blocking.
- Shows cooldown, remaining time, and whether Qingyin can act; blocked button presses append a readable cooldown log entry.
- Timing gate only: no autonomy, auto exploration, pathfinding, or action selection change is added.

## Qingyin UI Observation Bridge v0

- Adds a `Qingyin Observation` panel to the larger sandbox Flask UI.
- Adds read-only `GET /qingyin_state.json` for structured observation state.
- Shows symbolic sandbox body state, current perception, last action/result, effects/failures, cooldown, and boundary notes.
- Manual observation only: no autonomy, auto exploration, decision loop, LLM planning, pathfinding, or long-term memory is added.

## Instinct Random Walk + Item Reward Bias Design v0

- Adds `docs/instinct_random_walk_item_reward_bias_design_v0.md`.
- Designs a future two-round experiment with instinct/random walk, wall-blocked experience, item reward event, and reward-biased action tendency toward `I`.
- Defines future metrics, controls, staged implementation plan, and language boundaries.
- Design-only: no runtime behavior, autonomous loop, random walk runner, reward runtime, action weighting, pathfinding, or learning claim is added.

## Instinct Random Walk Runner v0

- Adds `py -3 -m ashl_core.teaching_cli run-instinct-random-walk`.
- Adds a bounded seeded random/instinct runner in the larger symbolic sandbox.
- Records step traces and local experience outcomes for wall-blocked, item-contact, passage, and exit contact observations.
- Round 1 only: no prior experience, reward bias, pathfinding, LLM planning, item collection, two-round comparison, or long-term memory is used.

## Wall Experience Influence v0

- Adds `py -3 -m ashl_core.teaching_cli run-wall-experience-influence-check`.
- Verifies that prior `front_symbol=w|action=move_forward` wall-blocked experience can suppress a later matching `move_forward` action.
- Includes a no-experience control proving that seeing `w` alone does not trigger suppression.
- Does not add item reward bias, dopamine-like signals, pathfinding, route planning, item seeking, or long-term memory.

## Instinct / Wall Influence UI Observation Bridge v0

- Adds Instinct / Experience Observation controls to `py -3 -m ashl_core.teaching_cli run-larger-sandbox-ui`.
- Lets the user run one bounded random walk sample or one wall-experience influence check and view summaries from the Qingyin UI.
- Adds read-only `/experiment_state.json` for the current experiment observation summary.
- UI observation only: no continuous autonomy, auto exploration, item reward bias, dopamine-like signals, pathfinding, route planning, or long-term memory is added.

## Larger Sandbox Live Step Playback UI v0

- Adds step-by-step playback of bounded random walk traces in the larger sandbox Flask UI.
- Adds Previous step, Next step, and Reset playback controls plus read-only `/playback_state.json`.
- Shows a separate Random Walk Playback view so manual sandbox state is not overwritten by playback.
- Playback replays recorded traces only; it does not generate new actions, add autonomy, pathfinding, reward bias, or long-term memory.

## Item Reward Event v0

- Adds `py -3 -m ashl_core.teaching_cli run-item-reward-event-check`.
- Creates a non-subjective `reward_event` when `front_symbol=i + move_forward` produces `item_contact`.
- Exposes `dopamine_like_signal` as a data field only.
- Does not add reward bias, item seeking, item collection, pathfinding, long-term memory, pleasure claims, or consciousness claims.

## Reward-Biased Action Tendency v0

- Adds `py -3 -m ashl_core.teaching_cli run-reward-biased-action-tendency-check`.
- Verifies that a prior non-subjective `item_contact_reward` can increase immediate `move_forward` action tendency when `front_symbol=i` is visible again.
- Includes a no-reward control proving that seeing `i` alone does not apply reward bias.
- Does not add item seeking, pathfinding, item collection, long-term memory, pleasure claims, or consciousness claims.

## Reward-Biased Random Walk Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-reward-biased-random-walk-check`.
- Compares no-reward vs with-item-reward immediate action tendency under a controlled visible-`i` condition.
- Verifies score increase and non-lower `move_forward` selection when a prior `item_contact_reward` exists.
- Does not claim whole-map item seeking, pathfinding, item collection, long-term memory, pleasure, desire, or consciousness.

## Two-Round Instinct Reward Comparison v0

- Adds `py -3 -m ashl_core.teaching_cli run-two-round-instinct-reward-comparison`.
- Closes the instinct/wall/reward line with a controlled two-round comparison.
- Round 1 has no carried experience or reward; Round 2 carries wall experience and item reward experience.
- Verifies immediate wall suppression and visible-item reward bias in controlled scenarios.
- Does not claim map-level item seeking, pathfinding, item collection, long-term memory, pleasure, desire, or consciousness.

## Instinct Reward Line Milestone Log v0

- Added `docs/milestone_logs/instinct_reward_line_milestone_2026-06-09.md`.
- Records completion of the instinct / wall / item reward immediate-tendency line.
- UI expansion is paused; next main line is Experience Abstraction Layer.

## Failure Reason Classifier v0

- Adds `py -3 -m ashl_core.teaching_cli run-failure-reason-classifier-check`.
- Starts the Experience Abstraction Layer by converting raw action outcomes into deterministic reason categories.
- Classifies wall-blocked, empty-moved, item-contact, passage-crossed, exit-contact, turn, look, and unknown cases.
- Does not add prediction, similar-context matching, rule learning, action selection changes, LLM reasoning, or long-term memory.

## Similar Context Key v0

- Adds `py -3 -m ashl_core.teaching_cli run-similar-context-key-check`.
- Continues the Experience Abstraction Layer by generating deterministic structural keys from classified experiences.
- Keys are position-independent by default, enabling same-structure different-position experiences to match.
- Does not add prediction, rule learning, action selection changes, LLM reasoning, or long-term memory.

## Action Outcome Predictor v0

- Adds `py -3 -m ashl_core.teaching_cli run-action-outcome-predictor-check`.
- Continues the Experience Abstraction Layer by predicting immediate outcomes from prior classified experiences and `similar_context_key`.
- Supports position-independent prediction for same-structure contexts.
- Does not modify action selection, add rule learning, use LLM reasoning, or write long-term memory.

## Prediction Accuracy / Mismatch Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-prediction-accuracy-check`.
- Continues the Experience Abstraction Layer by comparing predicted outcomes with actual classified observations.
- Records match, outcome mismatch, reason mismatch, and unknown prediction cases.
- Does not revise rules, modify action selection, use LLM reasoning, or write long-term memory.

## Rule Candidate From Prediction Mismatch v0

- Adds `py -3 -m ashl_core.teaching_cli run-rule-candidate-from-mismatch-check`.
- Converts prediction mismatches into proposed review-required candidates.
- Supports outcome mismatch, reason mismatch, unknown prediction, and no-candidate-for-match cases.
- Does not auto-approve, apply, revise rules, modify action selection, use LLM reasoning, or write long-term memory.

## Rule Candidate Review Gate v0

- Adds `py -3 -m ashl_core.teaching_cli run-rule-candidate-review-gate-check`.
- Adds a human-review gate for rule candidates.
- Candidates can become pending_review, approved, rejected, or deferred.
- Approval does not apply a rule yet, and Qingyin self-approval is blocked.
- Does not revise rules, modify action selection, use LLM reasoning, write lesson_store, or write long-term memory.

## Approved Candidate Preview v0

- Adds `py -3 -m ashl_core.teaching_cli run-approved-candidate-preview-check`.
- Creates deterministic previews for approved rule candidates.
- Shows proposed predictor-entry changes before any application step.
- Blocks non-approved candidates from applicable previews.
- Does not apply rules, modify predictor rules, modify action selection, write lesson_store, or write long-term memory.

## Reviewed Candidate Apply Verification v0

- Adds `py -3 -m ashl_core.teaching_cli run-reviewed-candidate-apply-verification-check`.
- Applies approved candidates only to a temporary in-memory predictor rule table.
- Reruns prediction against the temporary table and verifies expected outcome/reason changes.
- Blocks pending, rejected, and self-approved candidates.
- Does not persist rules, modify the global predictor, modify action selection, write lesson_store, write Memory Layer, or write long-term memory.

## Experience Abstraction Layer Milestone Log v0

- Adds `docs/milestone_logs/experience_abstraction_layer_milestone_2026-06-09.md`.
- Records the completed Experience Abstraction Layer chain from reason classification through temporary in-memory apply verification.
- Documents safety boundaries, explicit non-claims, and the recommended Boundary Index sync follow-up.

## Integrated Experience Session Trace v0

- Adds `py -3 -m ashl_core.teaching_cli run-integrated-experience-session-trace`.
- Connects existing symbolic vision, outcome classification, similar context keys, prediction, mismatch, candidate creation, and review gate into one scripted trace.
- Stops candidates at pending_review and keeps predictions read-only.
- Integration-only: does not add autonomy, action selection changes, persistent rule application, long-term memory, LLM reasoning, or pathfinding.

## Integrated Trace Chain Break Audit v0

- Adds `py -3 -m ashl_core.teaching_cli run-integrated-trace-chain-break-audit`.
- Audits the integrated experience session trace and explains chain breaks without modifying runtime behavior.
- Identifies where a step stops in the chain and whether the stop is expected or unexpected.
- Does not fix the break, modify action selection, apply candidates, write long-term memory, or use LLM reasoning.

## Integrated Experience Session Trace Milestone Log v0

- Adds `docs/milestone_logs/integrated_experience_session_trace_milestone_2026-06-09.md`.
- Records the first connected scripted trace from symbolic perception through review gate pending state.
- Syncs the milestone into `docs/current_boundary_index.md` as Boundary Index Version `2026-06-09-b36`.
- Documents the expected `unknown_prediction` chain break and keeps approval/application disabled.

## Persistent Rule Application Design v0

- Adds `docs/persistent_rule_application_design_v0.md`.
- Defines the safety gate between approved candidate and persistent rule.
- Requires temporary verification, repeated validation, challenge survival, low recent failure, low active conflict, preserved trace, rollback path, and separate human persistent approval.
- Design-only: does not implement persistent rule storage, write persistent rules, modify global predictor, modify action selection, or add long-term memory.

## Persistent Eligibility Checker v0

- Adds `py -3 -m ashl_core.teaching_cli run-persistent-eligibility-checker-check`.
- Evaluates whether an approved candidate has enough evidence to enter persistent-candidate review.
- Checks temporary apply verification, repeated similar-context validation, challenge survival, low recent failure, low active conflict, preserved trace, and rollback path.
- Checker-only: does not write persistent rules, add persistent storage, modify global predictors, or modify action selection.
- Milestone-indexed at `docs/milestone_logs/persistent_eligibility_checker_milestone_2026-06-09.md`; persistent line is paused after checker wrap-up, and next planned work moves to generalized memory loop.

## Project State Audit / Pause Point v0

- Adds `docs/project_state_audit_pause_point_2026-06-09.md`.
- Adds `docs/milestone_logs/project_state_pause_point_2026-06-09.md`.
- Classifies implemented, trace-only, checker-only, design-only, and not-present capabilities after the integrated trace and persistent eligibility checker line.
- Pause-only: does not add runtime behavior, CLI, persistent writes, action selection changes, global predictor mutation, or Boundary Index changes.

## Generalized Memory Loop Design v0

- Adds `docs/generalized_memory_loop_design_v0.md`.
- Defines cross-session exact-key pattern accumulation for future prediction confidence updates and `generalized_candidate` review.
- Exact `similar_context_key` matches are the only allowed aggregation path.
- Design-only: does not add runtime generalized memory, fuzzy similarity, storage, long-term memory, action selection changes, persistent rule writes, or LLM similarity.

## Generalized Memory Exact-Key Bucket v0

- Adds `py -3 -m ashl_core.teaching_cli run-generalized-memory-exact-key-bucket-check`.
- Aggregates demo cross-session experience records by exact `similar_context_key`.
- Reports pattern counts, outcome distribution, reason distribution, confidence labels, and future `generalized_candidate` eligibility.
- Runtime check only: does not use fuzzy / semantic / LLM / visual similarity, write long-term memory, create generalized candidates, modify predictors, or affect action selection.

## Generalized Prediction Confidence Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-generalized-prediction-confidence-check`.
- Converts exact-key bucket summaries into prediction confidence suggestions.
- Stable cross-session exact-key patterns can suggest `increase_confidence`.
- Checker-only: does not apply confidence to predictors, modify predictor rules, create generalized candidates, or influence action selection.

## Generalized Candidate From Pattern v0

- Adds `py -3 -m ashl_core.teaching_cli run-generalized-candidate-from-pattern-check`.
- Creates review-gated `generalized_candidate` records from stable exact-key patterns and confidence suggestions.
- Created candidates remain `pending_review`, unapproved, unapplied, and non-persistent.
- Checker-output only: does not persist candidates, modify predictors, write persistent rules, or affect action selection.

## Generalized Candidate Review + Preview v0

- Adds `py -3 -m ashl_core.teaching_cli run-generalized-candidate-review-preview-check`.
- Routes `generalized_candidate` records through human review and creates approved preview records.
- Supports approved, rejected, and deferred review outcomes, and blocks Qingyin self-approval.
- Preview-only: does not apply candidates, modify predictors, write memory, create persistent candidates, or affect action selection.

## Generalized Memory Line Milestone v0

- Adds `docs/milestone_logs/generalized_memory_line_milestone_2026-06-09.md`.
- Syncs `docs/current_boundary_index.md` to Boundary Index Version `2026-06-09-b38`.
- Completes the exact-key generalized memory check line through approved preview.
- Keeps fuzzy similarity, predictor mutation, action selection influence, persistent promotion, and memory writes disabled.

## Mimetic Endocrine System Design v0

- Adds `docs/mimetic_endocrine_system_design_v0.md`.
- Defines four traceable, non-biological regulatory axes: `dopamine_like`, `norepinephrine_like`, `oxytocin_like`, and `cortisol_like`.
- States the v0 stance as not denied, not claimed: future functionally comparable emotion-like dynamics are not denied, but v0 makes no subjective-state claim.
- Design-only: no runtime endocrine system, new CLI, formulas, action selection modulation, candidate approval/application, predictor mutation, memory write, personality drift, LLM reasoning/planning/vision, or consciousness claim is added.

## Mimetic Endocrine Signal Schema v0

- Adds `py -3 -m ashl_core.teaching_cli run-mimetic-endocrine-signal-schema-check`.
- Defines a shared validation schema for `dopamine_like`, `norepinephrine_like`, `oxytocin_like`, and `cortisol_like` signal records.
- Validates bounded values, source event links, source traces, decay metadata, and safety blocks for action selection, memory writes, and candidate approval.
- Schema-check only: no runtime formulas, signal interaction runtime, endocrine state runtime, action selection modulation, memory writes, candidate approval, or subjective emotion claims are added.

## Dopamine-Like Reward Trace Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-dopamine-like-reward-trace-check`.
- Maps controlled `reward_event` records such as `item_contact_reward` and `goal_progress_reward` into validated `dopamine_like` trace records using the mimetic endocrine signal schema.
- Records source event IDs, source traces, bounded values, reward linkage, and safety blocks from action selection, memory writes, and candidate approval.
- Trace-check only: no reward bias changes, reward-biased action tendency changes, random-walk changes, predictor mutation, memory write, candidate approval, or subjective pleasure claim is added.

## Norepinephrine-Like Change Attention Trace Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-norepinephrine-like-change-attention-trace-check`.
- Maps controlled `prediction_error`, `unknown_pattern`, and `conflict_like_distribution` events into validated `norepinephrine_like` trace records using the mimetic endocrine signal schema.
- Records source event IDs, source traces, bounded values, attention salience linkage, and safety blocks from action selection, memory writes, and candidate approval.
- Trace-check only: no autonomous attention control, observation priority runtime changes, predictor mutation, action selection influence, memory write, candidate approval, or subjective alertness/anxiety claim is added.

## Cortisol-Like Failure Load Trace Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-cortisol-like-failure-load-trace-check`.
- Maps controlled `failure_accumulation`, `active_conflict`, and `challenge_failure` events into validated `cortisol_like` trace records using the mimetic endocrine signal schema.
- Records source event IDs, source traces, bounded values, pressure load linkage, and safety blocks from action selection, memory writes, and candidate approval.
- Trace-check only: no protective mechanism trigger, cooldown change, risk avoidance behavior, predictor mutation, action selection influence, memory write, candidate approval, or subjective stress/anxiety/pain claim is added.

## Oxytocin-Like Review Trust Trace Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-oxytocin-like-review-trust-trace-check`.
- Maps controlled `human_review`, `consistent_correction`, and `source_reliability` events into validated `oxytocin_like` trace records using the mimetic endocrine signal schema.
- Records explicit source event IDs, source traces, bounded values, source trust linkage, and safety blocks from action selection, memory writes, and candidate approval.
- Trace-check only: no blind trust, review gate override, Qingyin self-approval, candidate auto-approval, user identity inference, action selection influence, memory write, or subjective trust/attachment/love claim is added.

## Mimetic Endocrine Four-Axis Trace Integration v0

- Adds `py -3 -m ashl_core.teaching_cli run-mimetic-endocrine-four-axis-trace-integration-check`.
- Combines `dopamine_like`, `norepinephrine_like`, `cortisol_like`, and `oxytocin_like` trace checkers into one four-axis trace summary.
- Verifies all four axes produce valid trace records while remaining blocked from action selection, memory writes, candidate approval, predictor mutation, runtime formulas, and signal interactions.
- Integration-check only: no endocrine runtime, endocrine state runtime, signal interaction formulas, reward bias change, attention control, protective trigger, trust-based approval, memory write, or subjective emotion claim is added.

## Mimetic Endocrine Line Milestone v0

- Adds `docs/milestone_logs/mimetic_endocrine_line_milestone_2026-06-09.md`.
- Syncs `docs/current_boundary_index.md` to Boundary Index Version `2026-06-09-b39`.
- Completes the four-axis trace line for `dopamine_like`, `norepinephrine_like`, `cortisol_like`, and `oxytocin_like`.
- Milestone-indexed only: keeps formulas, signal interactions, endocrine runtime, action selection influence, predictor mutation, memory writes, candidate approval influence, and subjective emotion/consciousness claims disabled.

## Retina Decoder Design v0

- Adds `docs/retina_decoder_design_v0.md`.
- Opens the eye-structure simulation line with a design-only retina decoder boundary.
- Defines conceptual RGB grid, symbolic cell, and hybrid input shapes plus low-level feature records for brightness, color family, contrast, edge-like change, position, front relation, and symbol hints.
- Design-only: no runtime decoder, new CLI, RGB quantization code, frame buffer, focus selector, endocrine connection, action selection influence, visual memory write, CNN / YOLO / UNet, object recognition, semantic vision, LLM vision, solved symbol grounding claim, or subjective visual experience claim is added.

## Retina Decoder Feature Schema v0

- Adds `py -3 -m ashl_core.teaching_cli run-retina-decoder-feature-schema-check`.
- Defines and validates low-level retina feature records with position, raw input, brightness, color family, contrast, edge-like flag, relations, confidence, source trace, required null `semantic_label`, and required v0 block flags.
- Includes deterministic symbolic, RGB, hybrid, edge-like, invalid semantic-label, invalid RGB-range, and action-selection-unblocked demo cases.
- Schema/checker only: no retina runtime, RGB quantization runtime, object recognition, semantic vision, focus selector, frame buffer, endocrine connection, action selection influence, or visual memory write is added.

## Retina Decoder Symbolic Feature Decode Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-retina-decoder-symbolic-feature-decode-check`.
- Deterministically converts symbolic / hybrid demo input cells into low-level retina feature records and validates them through the Retina Decoder Feature Schema v0 checker.
- Preserves symbol hints as hints only while keeping `semantic_label` null for all valid generated records.
- Trace/checker only: no retina runtime, RGB quantization runtime, image processing runtime, frame buffer, focus selector, endocrine connection, vision-driven action selection, visual memory write, object recognition, semantic vision, or symbol grounding claim is added.

## Simple Visual Frame Buffer Design v0

- Adds `docs/simple_visual_frame_buffer_design_v0.md`.
- Defines a design-only visual frame container for grouping already validated retina feature records.
- Defines future `current_frame` / `previous_frame` concepts and source trace / safety flag requirements.
- Design-only: no runtime frame buffer, frame storage, frame comparison, change detection, focus selector, action selection influence, memory write, object recognition, semantic vision, or visual understanding claim is added.

## Visual Frame Buffer Schema Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-visual-frame-buffer-schema-check`.
- Validates visual frame records composed of already validated retina feature records.
- Enforces frame count consistency, null retina `semantic_label`, and downstream safety flags.
- Schema/checker only: no runtime frame buffering, current/previous frame storage, frame comparison, focus selection, action selection influence, memory write, object recognition, or semantic vision is added.

## Visual Frame Assembly From Retina Features Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-visual-frame-assembly-from-retina-features-check`.
- Assembles validated retina feature records into a `visual_frame` and validates it with the visual frame schema.
- Reuses symbolic / hybrid retina feature decode, retina feature schema validation, and visual frame buffer schema validation.
- Check-only: no runtime frame buffering, current/previous frame storage, frame comparison, focus selection, action selection influence, memory write, object recognition, or semantic vision is added.

## Visual Frame Change Design v0

- Adds `docs/visual_frame_change_design_v0.md`.
- Defines design-only `change_record` structures for comparing `previous_frame` and `current_frame`.
- It does not add runtime change detection, frame storage, focus selection, action selection influence, or memory write.

## Visual Frame Change Schema Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-visual-frame-change-schema-check`.
- Validates low-level `change_record` structures and required downstream safety flags.
- Checker-only: no frame comparison runtime, change detection runtime, focus selection, action selection influence, or memory write is added.

## Visual Frame Pair Demo Assembly Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-visual-frame-pair-demo-assembly-check`.
- Assembles deterministic `previous_frame` / `current_frame` demo records and validates both frames.
- Fixture/check-only: no frame comparison, change detection runtime, focus selection, action selection influence, or memory write is added.

## Visual Frame Change Trace Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-visual-frame-change-trace-check`.
- Generates deterministic low-level `change_records` from a valid `previous_frame` / `current_frame` demo pair and validates them with the change schema.
- Trace/check-only: no runtime frame storage, continuous change detection, focus selection, action selection influence, or memory write is added.

## Eye-Structure Simulation Line Milestone v0

- Syncs the completed low-level eye-structure path: symbolic/hybrid demo input -> retina features -> visual_frame -> previous/current frame pair -> low-level `change_records`.
- All outputs remain trace/checker-only and blocked from action selection, memory write, focus selection, endocrine control, predictor mutation, and semantic/object claims.

## Focus Selector Design v0

- Adds `docs/focus_selector_design_v0.md`.
- Defines design-only `focus_candidate` records from low-level visual features and change traces.
- Records future focus-lock prevention principles: attention intensity cap, bounded duration/decay, norepinephrine-like interruption, and cortisol-like forced diffusion, without implementing runtime attention or endocrine control.
- Design-only: no runtime focus selection, attention control, action selection influence, endocrine control, memory write, or semantic/object understanding is added.

## Focus Candidate Schema Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-focus-candidate-schema-check`.
- Validates `focus_candidate` records from the focus selector design.
- Checker-only: no runtime focus selection, attention control, action selection influence, endocrine control, memory write, or semantic/object understanding is added.

## Focus Candidate From Change Trace Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-focus-candidate-from-change-trace-check`.
- Creates validated `focus_candidate` records from validated low-level `change_records`.
- Trace/check-only: no runtime focus selection, attention control, ranking runtime, action selection influence, endocrine control, memory write, or semantic/object understanding is added.

## Focus Candidate Ranking Trace Design v0

- Adds `docs/focus_candidate_ranking_trace_design_v0.md`.
- Defines trace-only ranking records for validated `focus_candidate` records, including score snapshots and lock-prevention fields.
- Design-only: no `active_focus` selection, focus application, attention control, runtime ranking, action selection influence, endocrine runtime, or memory write is added.

## Focus Candidate Ranking Trace Schema Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-focus-candidate-ranking-trace-schema-check`.
- Validates trace-only `ranking_trace` records for `focus_candidate` ordering, including ranking items, score snapshots, tie breakers, and lock-prevention fields.
- Schema/checker-only: no runtime ranking, `active_focus` selection, attention control, action selection influence, endocrine control, or memory write is added.

## Focus Candidate Ranking Trace Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-focus-candidate-ranking-trace-check`.
- Creates a deterministic trace-only `ranking_trace` from validated `focus_candidate` records and validates it with the ranking trace schema.
- Trace/check-only: no runtime ranking, `active_focus` selection, attention control, action selection influence, endocrine control, or memory write is added.

## Focus Line Milestone Sync v0

- Syncs the focus line milestone: validated low-level `change_records` -> `focus_candidate` records -> deterministic `ranking_trace`.
- All outputs remain schema-validated and blocked from `active_focus` selection, focus application, attention control, action selection, memory write, endocrine runtime, predictor mutation, and semantic/object claims.

## Focus Application Boundary Review v0

- Adds `docs/focus_application_boundary_review_v0.md`.
- Documents the boundary between trace-only `ranking_trace` records and any future `active_focus` / `focus_applied` behavior.
- Design-only: no runtime focus selection, attention control, action selection influence, endocrine runtime, or memory write is added.

## Focus Application Gate Schema Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-focus-application-gate-schema-check`.
- Validates review-only gate records for future focus application boundaries.
- Schema/checker-only: no `active_focus`, `focus_applied`, attention control, action selection influence, endocrine runtime, or memory write is authorized.

## Perception-to-Action Boundary Review v0

- Adds `docs/perception_to_action_boundary_review_v0.md`.
- Documents the boundary between perception/focus traces and any future action influence.
- Design-only: does not add active_focus, attention control, perception-to-action bridge, action selection influence, memory write, endocrine runtime, or predictor mutation.

## Focus / Perception Boundary Construction Log v0

- Adds `docs/focus_perception_boundary_construction_log_v0.md`.
- Summarizes the completed eye-structure, focus trace/checker, focus application boundary, and perception-to-action boundary work for handoff.
- Documentation-only: no runtime focus, attention, perception-to-action, action selection, memory, predictor, endocrine, object, semantic, or subjective claim behavior is added.

## Phase 0 Action / Lesson Loop Return Planning v0

- Adds `docs/phase0_action_lesson_loop_return_planning_v0.md`.
- Records the decision to pause perception/focus runtime escalation and return to action/outcome/failure_reason/lesson foundations.
- Planning-only: no runtime action selection, lesson application, persistent learning, perception-to-action bridge, active_focus, attention control, memory write, predictor mutation, or endocrine runtime is added.

## Action Outcome Contrast Baseline Review v0

- Adds `docs/action_outcome_contrast_baseline_review_v0.md`.
- Reviews the current Phase 0 action/outcome/failure_reason/lesson path and identifies the next safe trace/checker package.
- Review-only: does not change action selection, action behavior, learning, memory, or predictor behavior.

## Expected vs Actual Outcome Pair Schema Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-expected-actual-outcome-pair-schema-check`.
- Validates the smallest reusable Phase 0 `expected_outcome` / `actual_outcome` / `mismatch` record shape with structured `failure_reason` and trace-only/review-gated boundaries.
- Schema/checker-only: does not change action selection, action behavior, lesson application, memory, persistence, or predictor behavior.

## Outcome Pair From Action Trial Trace Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-outcome-pair-from-action-trial-trace-check`.
- Generates validated `expected_actual_outcome_pair` records from deterministic demo action trial traces.
- Trace/check-only: does not change action selection, action behavior, lesson application, memory, persistence, or predictor behavior.

## Failure Reason From Outcome Pair Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-failure-reason-from-outcome-pair-check`.
- Extracts validated structured `failure_reason` records from valid mismatch outcome pairs with v0-local validation.
- Trace/check-only: does not generate lesson_candidates, change action selection, apply lessons, write memory, persist learning, or mutate predictors.

## Lesson Candidate From Failure Reason Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-lesson-candidate-from-failure-reason-check`.
- Creates trace-only review-required `lesson_candidate` records from valid `failure_reason` records with v0-local validation.
- Does not approve or apply lessons, change action selection, write memory, persist learning, or mutate predictors.

## Lesson Candidate Review Gate Check v0

- Adds `py -3 -m ashl_core.teaching_cli run-lesson-candidate-review-gate-check`.
- Evaluates whether trace-only `lesson_candidate` records may enter pending human review.
- Does not approve, reject, apply, persist, write memory, change action selection, or mutate predictors.

## Lesson Candidate Review Evidence Summary v0

- Adds `py -3 -m ashl_core.teaching_cli run-lesson-candidate-review-evidence-summary-check`.
- Builds reviewer-facing evidence summaries for pending_review `lesson_candidate` records.
- Remains review-support-only and does not approve, reject, preview, apply, persist, write memory, change action selection, or mutate predictors.

## History Runtime Persistence Gap Review v0

- Adds `docs/history_runtime_persistence_gap_review_v0.md`.
- Clarifies that current generalized memory exact-key aggregation uses cross-session demo records and does not yet prove a persisted history runtime.
- Records the missing persistence / retention layer without adding storage, memory write, persistent learning, predictor mutation, or action selection influence.

## Lesson Candidate Human Review Decision Schema v0

- Adds `py -3 -m ashl_core.teaching_cli run-lesson-candidate-human-review-decision-schema-check`.
- Defines human/manual review decision records for `lesson_candidate` evidence summaries.
- `approved_for_preview` permits only future trace-only preview and does not approve lesson application, memory write, persistence, or predictor mutation.

## Reviewed Lesson Trace Preview v0

- Adds `py -3 -m ashl_core.teaching_cli run-reviewed-lesson-trace-preview-check`.
- Creates deterministic trace-only preview records only when a valid `lesson_candidate` has a valid human review decision with `decision.status == approved_for_preview`.
- Blocks rejected, needs_revision, stale, missing-decision, source-linkage mismatch, unknown preview type, and any application/action/memory/predictor/persistence side-effect flags.
- Preview remains trace-only: no lesson is applied, no action selection or behavior changes, no memory is written, and no predictor or persistent rule is modified.

## Phase 0 Action-Lesson Review Line Milestone

- Phase 0 action-lesson review line now reaches trace-only reviewed lesson previews: demo action trial -> outcome_pair -> failure_reason -> lesson_candidate -> review_gate -> evidence_summary -> human_review_decision -> reviewed_lesson_trace_preview.
- This remains review/preview-only and does not apply lessons, change action selection, write memory, mutate predictors, persist learning, or claim proof of learning.

## Lesson Application Boundary Review v0

- Documents the boundary between reviewed_lesson_trace_preview and any future dry-run correction or lesson application.
- Design-only: does not apply lessons, change action selection, write memory, persist learning, or mutate predictors.
