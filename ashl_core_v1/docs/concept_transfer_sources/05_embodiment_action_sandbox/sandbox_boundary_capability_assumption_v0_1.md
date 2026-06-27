# Sandbox Boundary / Capability Assumption v0.1

## 1. 目的

本文件定義沙盒的設計邊界假設，鎖定「沙盒是什麼、不是什麼」，避免後續一接 sandbox 就偷渡成自由 runtime、lesson_store 寫入通道、Memory Layer 寫入通道，或真實世界操作能力。

本文件是 docs-only / assumption-boundary / sandbox-prep。

本文件不實作任何 sandbox runtime。

---

## 2. 沙盒的定位

A sandbox is an observable, replayable, limited, interruptible, trace-producing experimental environment.

沙盒是可觀察、可回放、可限制、可中止、可產生 trace 的實驗環境。

沙盒不是：
- 自由 runtime
- lesson_store 寫入通道
- Memory Layer 寫入通道
- 真實世界操作通道
- 已核准知識的生成管道
- lesson_candidate 的直接來源

---

## 3. 沙盒能力邊界

沙盒允許的能力必須被明確列舉。未列舉的能力視為禁止。

沙盒可以：
- 在隔離環境內執行預定義的行動序列
- 產生可觀察的 trace
- 記錄實驗過程
- 提供 evidence（僅供後續 review 參考，不直接成為 lesson）

A sandbox is not free runtime.

沙盒內允許的行動必須被明確限制。

沙盒不能因為「只是實驗」就取得更高權限。

---

## 4. 沙盒禁止能力

沙盒不得：
- 執行任何不在預定義允許清單內的行動
- 寫入 lesson_store
- 寫入 Memory Layer
- 寫入 Long-term Memory
- 修改 Core Seed
- 執行 self-modification
- 存取 real-world action capability
- 自行決定哪些結果升格為知識

---

## 5. 沙盒輸出與 trace 的關係

沙盒產生的 trace 是實驗紀錄，不是 memory promotion。

沙盒 trace 的用途：
- 提供可回放的實驗過程紀錄
- 提供 evidence 供外部 review 參考
- 作為未來 lesson_candidate pipeline 的輸入來源候選

沙盒 trace 不得：
- 自動升格為 Long-term Memory
- 自動觸發 Memory Layer promotion
- 繞過 review gate 直接成為 lesson

---

## 6. result / success / failure / repair / trace 的非等價邊界

sandbox result is not a lesson

沙盒結果不能直接變成 lesson。

sandbox success is not approved knowledge

沙盒成功不能直接變成已核准知識。

sandbox failure is not automatic failure_reason

沙盒失敗不能直接變成 authoritative failure_reason。

sandbox repair is not executable action

沙盒修復建議不能直接變成可執行行動。

sandbox trace is not memory promotion

沙盒 trace 不能直接變成 Memory Layer promotion。

sandbox exploration is not authorized runtime behavior

沙盒探索不能直接授權 runtime 行為。

---

## 7. 沙盒與 lesson_candidate pipeline 的關係

Sandbox output may provide evidence.

Sandbox output must not directly create formal lesson_candidate.

Sandbox output must pass through existing failure_event / lesson_candidate / review boundaries before becoming learning material.

也就是：

- 沙盒只能提供 evidence。
- 沙盒不能直接建立 formal lesson_candidate。
- 若未來要把沙盒結果納入學習，仍必須經過 structured failure_event、lesson_candidate pipeline 與 review gate。

沙盒到 lesson 的路徑：

```text
sandbox output
→ evidence（只是參考，不是直接輸入）
→ failure_event（必須符合既有 failure_event schema）
→ normalized_failure_event
→ lesson_candidate_input_trace
→ lesson_candidate builder
→ lesson_candidate_draft
→ review_queue_entry / review_task
→ review_decision
→ approved lesson_candidate
```

每一步都必須通過現有 pipeline 的驗證與 review gate。沙盒輸出不能跳過任何一步。

---

## 8. 沙盒與 Memory Layer 的關係

Sandbox trace is not Long-term Memory.

Sandbox result must not write to Memory Layer directly.

ASHL Core may provide evidence, but Qingyin Memory Layers decide memory admission.

沿用既有責任邊界：

- ASHL Core provides evidence.
- D清音 Memory Layers decide memory admission.

沙盒不得：
- 直接寫入 Long-term Memory
- 直接寫入 Core Memory
- 直接寫入 Archive Memory
- 直接寫入 Working Memory snapshot（除非是 sandbox-internal state，不影響主循環）
- 觸發 memory promotion

---

## 9. 沙盒與真實世界操作的隔離

A sandbox must not perform real-world actions.

沙盒不得操作：
- 真實檔案系統中的非測試資料
- 網路服務
- 金錢 / 帳號 / 密碼 / 身分資料
- 使用者設備
- 外部工具
- 任何對真實世界產生不可逆影響的行動

沙盒只能在隔離的、可重置的實驗環境內運作。

---

## 10. 未來 runtime 前置要求

若未來要實作 sandbox runtime，必須先明確定義以下項目：

```text
allowed action set
blocked action set
environment reset rule
trace schema
replay rule
interrupt rule
capability boundary
failure capture rule
human review boundary
memory / lesson non-write guarantee
```

在以上項目全部明確定義並通過 review 之前，不得進入 sandbox runtime 實作。

本包只寫文件，不實作。

---

## 11. 目前不可宣稱

目前不可宣稱：
- 沙盒已有 runtime
- 沙盒結果已被審核為有效知識
- 沙盒輸出已被納入 lesson_store
- 沙盒探索授權了任何 runtime 行為
- 沙盒 trace 已升格為 Memory Layer 內容

---

## 12. 設計結論

沙盒是實驗工具，不是知識來源。

沙盒的設計邊界是：
- 可觀察：每個行動與結果必須可追蹤
- 可回放：實驗過程必須可重現
- 可限制：允許的能力必須明確列舉
- 可中止：外部必須可以在任何時間中止沙盒
- 可產生 trace：必須輸出結構化的實驗紀錄

沙盒的知識邊界是：
- 沙盒結果只是 evidence，不是 lesson
- 沙盒成功不是核准知識
- 沙盒失敗不是 authoritative failure_reason
- 沙盒修復不是可執行行動
- 沙盒 trace 不是 memory promotion
- 沙盒探索不授權 runtime 行為

沙盒的隔離邊界是：
- 不寫入 lesson_store
- 不寫入 Memory Layer
- 不執行真實世界操作
- 不修改 Core Seed
- 不觸發 self-modification
