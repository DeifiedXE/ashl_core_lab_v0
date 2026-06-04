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
