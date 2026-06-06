# Sandbox Failure / Trace Contract v0.1

## 1. 目的

本文件承接 v2.10a Sandbox Boundary / Capability Assumption Docs，進一步定義：

- 沙盒中的 failure 如何被描述
- 沙盒 trace 應包含哪些欄位
- 沙盒 failure 為何不能直接變成 authoritative failure_reason
- 沙盒 failure 如何作為 future evidence 進入既有 failure_event / lesson_candidate / review 邊界

本文件是 docs-only / contract-boundary / sandbox-failure-trace-prep。

本文件不實作任何 sandbox runtime 或 trace schema runtime。

---

## 2. 與 v2.10a 的關係

v2.10a 已確立沙盒的能力邊界：

```text
sandbox result is not a lesson
sandbox success is not approved knowledge
sandbox failure is not automatic failure_reason
sandbox repair is not executable action
sandbox trace is not memory promotion
sandbox exploration is not authorized runtime behavior
```

本文件在此基礎上，進一步說明 sandbox failure 的定義與 sandbox trace 的結構要求。

v2.10a 的所有邊界在本文件中繼續有效，本文件不放寬任何 v2.10a 限制。

---

## 3. sandbox failure 的定義

Sandbox failure is an observed experimental mismatch inside a bounded sandbox.

沙盒失敗是在有邊界沙盒內觀察到的實驗性 mismatch。

具體說明：
- 「有邊界沙盒」指已明確定義 allowed_action_set、blocked_action_set 與 capability_boundary 的受控環境。
- 「觀察到的」指 mismatch 必須在 trace 中可見，不能是推斷。
- 「實驗性」指這是沙盒內的試驗結果，不是正式行為的一部分。
- 「mismatch」指 expected_outcome 與 actual_outcome 之間存在可記錄的差異。

---

## 4. sandbox failure 與 authoritative failure_reason 的邊界

Sandbox failure is not authoritative failure_reason.

沙盒內的失敗只能表示「該沙盒設定下，某次 action / expected / actual 對照出現 mismatch」。

它不能直接被視為正式 failure_reason。

### 核心邊界

No structured failure_event, no authoritative failure_reason.

No expected_outcome / actual_outcome contrast, no authoritative failure.

LLM-only explanation must not become authoritative failure_reason.

### 說明

沙盒 failure 不是 authoritative failure_reason，因為：
- 沙盒是受限的實驗環境，不是正式行為環境
- 沙盒的 expected_outcome 是實驗假設，不是系統行為規格
- 沙盒的 evaluator 可能是臨時性或局部性的，不能代表全局判斷
- 沙盒失敗沒有經過 failure_event validation、lesson_candidate review 或 review_decision gate

要成為 authoritative failure_reason，必須：
- 轉為 structured failure_event
- 通過 normalize_failure_event_trace
- 進入 lesson_candidate builder contract
- 通過 review gate

---

## 5. sandbox trace 的定位

Sandbox trace is evidence, not approval.

沙盒 trace 的用途是記錄「沙盒中發生了什麼」，不是核准任何知識或行為。

具體說明：
- trace 只能讓之後的人或流程回看沙盒中發生了什麼
- trace 本身不代表 lesson 被接受
- trace 本身不代表知識被核准
- trace 本身不代表 Memory Layer 可以寫入
- trace 是回放與審核的原材料，不是結論

---

## 6. sandbox failure trace 最小欄位

本欄位清單是未來若 runtime 化時的最低要求，不是目前 schema 實作。

```text
sandbox_id
sandbox_version
scenario_id
sandbox_capability_boundary
allowed_action_set
blocked_action_set
action_intent
expected_outcome
actual_outcome
observed_mismatch
mismatch_source
evaluator_source
interrupt_state
repair_suggestion
raw_observation
trace_timestamp_or_tick
replay_reference
```

各欄位說明：

- `sandbox_id`：識別這是哪個沙盒實例
- `sandbox_version`：沙盒設計版本，用於重現性驗證
- `scenario_id`：識別這是哪個實驗場景
- `sandbox_capability_boundary`：本次實驗的能力邊界快照
- `allowed_action_set`：本次允許的行動集合
- `blocked_action_set`：本次明確禁止的行動集合
- `action_intent`：清音或系統的行動意圖
- `expected_outcome`：實驗假設的預期結果
- `actual_outcome`：實際觀察到的結果
- `observed_mismatch`：expected 與 actual 的差異描述
- `mismatch_source`：mismatch 的來源（action error / env constraint / capability boundary 等）
- `evaluator_source`：評估 mismatch 的來源（sandbox internal / external observer 等）
- `interrupt_state`：沙盒是否被中止，以及中止原因
- `repair_suggestion`：沙盒內根據 mismatch 產生的候選修正方向（只是建議，不是指令）
- `raw_observation`：原始觀察記錄，未經解讀
- `trace_timestamp_or_tick`：實驗時間戳或 tick 計數
- `replay_reference`：重放此 trace 所需的參考資料

注意：本包只定義欄位清單，不實作 schema 或 runtime。

---

## 7. sandbox trace 與 failure_event 的關係

Sandbox trace may support later failure_event construction, but must not bypass failure_event validation.

沙盒 trace 可以作為 future evidence。

但如果未來要進入 lesson_candidate pipeline，仍必須：
- 轉為 structured failure_event（符合既有 failure_event schema）
- 通過 normalize_failure_event_trace
- 通過 lesson_candidate_input_trace 驗證

沙盒 trace 到 failure_event 的路徑：

```text
sandbox trace
→ evidence（只是參考，不是直接輸入）
→ structured failure_event（必須手動或明確轉換，不得自動）
→ normalized_failure_event
→ lesson_candidate_input_trace
→ lesson_candidate builder contract
→ lesson_candidate_draft
→ review_queue_entry / review_task
→ review_decision
```

每一步都必須通過既有 pipeline 的驗證。沙盒 trace 不能跳過任何一步。

---

## 8. sandbox trace 與 lesson_candidate 的關係

Sandbox failure must not directly create formal lesson_candidate.

沙盒 failure 最多只能作為 evidence，支援後續人工或流程建立 failure_event。

沙盒不得：
- 直接建立 approved lesson_candidate
- 直接寫入 lesson_store
- 繞過 review gate
- 直接激活任何 lesson

沙盒 failure 進入 lesson_candidate pipeline 的前提：
- 必須先轉為 structured failure_event
- 必須明確標記來源為 sandbox evidence
- 必須通過完整的 review 流程

---

## 9. sandbox trace 與 Memory Layer 的關係

Sandbox failure trace must not write to Memory Layer directly.

沿用既有責任邊界：

ASHL Core provides evidence.

D清音 Memory Layers decide memory admission.

沙盒 trace 不得：
- 直接寫入 Long-term Memory
- 直接寫入 Core Memory
- 直接寫入 Archive Memory
- 直接觸發 Working Memory snapshot 更新（sandbox-internal 狀態除外）
- 觸發 Memory Layer promotion

---

## 10. sandbox repair suggestion 的邊界

Sandbox repair suggestion is not executable action.

repair suggestion 只是沙盒內根據 mismatch 產生的候選修正方向。

它不能：
- 直接變成 runtime action
- 直接授權外部工具操作
- 直接修改真實資料或系統狀態
- 直接成為 lesson
- 直接繞過 review

repair suggestion 的唯一合法用途：
- 在 sandbox trace 中記錄「沙盒內觀察到的可能修正方向」
- 作為未來 evidence，供人工或流程參考

---

## 11. 未來 runtime 前置要求

若未來要實作 sandbox failure / trace runtime，必須先定義：

```text
sandbox failure schema（符合 v2.10a allowed_action_set / blocked_action_set 結構）
trace schema（包含本文件第 6 節所有欄位）
mismatch_source taxonomy（mismatch 來源分類）
evaluator_source taxonomy（評估來源分類）
repair_suggestion scope（修正建議的允許範圍）
failure_event bridge rule（沙盒 trace 轉 failure_event 的明確規則）
human review gate（沙盒 evidence 進入 lesson pipeline 前的人工確認要求）
```

在以上項目全部明確定義並通過 review 之前，不得進入 sandbox failure trace runtime 實作。

本包只寫文件，不實作。

---

## 12. 目前不可宣稱

目前不可宣稱：
- 沙盒 failure 已被確認為 authoritative failure_reason
- 沙盒 trace 已被審核為有效知識來源
- 沙盒 trace 已升格為 Memory Layer 內容
- 沙盒 repair suggestion 已被核准為可執行行動
- 沙盒 evidence 已被納入 lesson_candidate pipeline

---

## 13. 設計結論

沙盒 failure 是實驗觀察，不是正式判斷。

核心設計原則：

```text
Sandbox failure is an observed experimental mismatch inside a bounded sandbox.
Sandbox failure is not authoritative failure_reason.
Sandbox trace is evidence, not approval.
Sandbox trace may support later failure_event construction, but must not bypass failure_event validation.
Sandbox failure must not directly create formal lesson_candidate.
Sandbox failure trace must not write to Memory Layer directly.
Sandbox repair suggestion is not executable action.
No structured failure_event, no authoritative failure_reason.
No expected_outcome / actual_outcome contrast, no authoritative failure.
LLM-only explanation must not become authoritative failure_reason.
```

沙盒 failure 的知識邊界：
- 沙盒 failure 只是 evidence
- evidence 需要人工或明確流程轉換才能進入 failure_event pipeline
- failure_event pipeline 必須完整通過 validation 與 review
- 沙盒不能成為知識的捷徑，只能成為知識的原材料
