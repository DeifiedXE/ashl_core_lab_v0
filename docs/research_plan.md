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
