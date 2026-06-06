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
