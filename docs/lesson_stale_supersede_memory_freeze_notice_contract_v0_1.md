# Lesson Stale / Supersede Memory Freeze Notice Contract v0.1

## 1. 目的

本文件定義 lesson stale / superseded 時，ASHL Core 應產生或記錄的 memory_freeze_required notice 的 contract 邊界。

本文件是 contract-only / cross-layer-boundary / memory-freeze-notice / no-direct-memory-write。

本文件不實作 Memory Layer freeze runtime。

---

## 2. 問題背景

Lesson 變 stale 或 superseded 時，對應 learned_principle 可能仍留在 Memory Layer 中可用。

這會造成跨層責任斷裂：

```text
lesson 已被標為 stale / superseded，
但 Memory Layer 仍可能保留並使用由該 lesson 衍生的 learned_principle。
```

但目前設計已明確：

```text
ASHL Core 不直接寫入 Memory Layer。
ASHL Core provides evidence.
D清音 Memory Layers decide memory admission.
```

因此，本包建立 memory_freeze_required notice contract，讓 ASHL Core 在 lesson stale / superseded 時，提供足夠 evidence，交由 Memory Layer 未來決定是否凍結 learned_principle。

---

## 3. 核心邊界

ASHL Core provides evidence.

D清音 Memory Layers decide memory admission.

D清音 Memory Layers decide memory freeze application.

ASHL Core 不得直接凍結 Memory Layer 條目。

---

## 4. memory_freeze_required notice 的定義

memory_freeze_required notice 是 ASHL Core 在 lesson stale 或 superseded 時，產生的 trace-only / evidence-only 通知結構。

Memory freeze notice is evidence, not Memory Layer write.

ASHL Core may emit or record evidence that a learned_principle should be frozen.

ASHL Core must not directly freeze Memory Layer entries.

Notice 的唯一用途：
- 作為 evidence，提供給 Memory Layer 未來的凍結決策流程
- 作為 audit trace，記錄 lesson lifecycle 變化與 memory 潛在影響
- 不是指令，不是寫入，不是授權

---

## 5. stale lesson 與 memory freeze notice

Lesson stale may require memory_freeze_required notice.

當 lesson 被標為 stale 時：
- lesson 已不再是 selection-eligible 的推薦來源
- 但 Memory Layer 可能仍保有由該 lesson 衍生的 learned_principle
- ASHL Core 應產生 notice，標記 source_lesson_id 與 stale 原因
- Memory Layer 根據 notice 決定是否凍結對應 learned_principle

stale notice 不得：
- 自動凍結 Memory Layer 條目
- 改變 lesson 的 selection eligibility（stale 已由 lesson_store 邏輯處理）
- 修改 learned_principle 的內容

---

## 6. superseded lesson 與 memory freeze notice

Lesson superseded may require memory_freeze_required notice.

當 lesson 被 superseded（被新 lesson 取代）時：
- 舊 lesson 已不應再被選用
- 但 Memory Layer 可能仍保有由舊 lesson 衍生的 learned_principle
- ASHL Core 應產生 notice，標記 source_lesson_id、superseded_by_lesson_id 與取代原因
- Memory Layer 根據 notice 決定是否凍結或更新對應 learned_principle

superseded notice 不得：
- 自動以新 lesson 覆蓋舊 learned_principle
- 繞過 Memory Layer 的 admission 決策流程
- 修改 learned_principle 的內容

---

## 7. notice 必要欄位

```text
notice_type: "memory_freeze_required"
source_lesson_id: 觸發 notice 的 lesson 的 ID
lesson_lifecycle_state: "stale" | "superseded" | "stale_and_superseded"
stale_or_supersede_reason: 觸發原因的文字說明
superseded_by_lesson_id: 取代的新 lesson ID（stale-only 時可為 None）
target: "learned_principle"
effect: "evidence_only"
direct_memory_write: False
lesson_store_write: False
selection_eligibility_changed: False
activation_changed: False
authority_boundary: "notice_evidence_only"
```

Memory freeze notice must preserve source_lesson_id.

Memory freeze notice must preserve stale_or_supersede_reason.

---

## 8. notice 與 Memory Layer 的邊界

Memory freeze notice must not directly modify learned_principle.

Notice 不得：
- 直接寫入 Long-term Memory
- 直接寫入 Core Memory
- 直接觸發 Memory Layer promotion 或 demotion
- 自動凍結任何 Memory Layer 條目
- 繞過 Memory Layer 的 admission 決策

Memory Layer 收到 notice 後的決策權完全屬於 Memory Layer。

---

## 9. notice 與 lesson_store 的邊界

Memory freeze notice must not write to lesson_store.

Notice 不改變 lesson_store 中任何 lesson 的狀態。

lesson 的 stale / superseded 狀態由 lesson_store 的既有函式管理：
- `mark_lesson_stale`
- `link_lesson_supersede`

notice 是在 lesson 狀態已變更後，額外產生的 evidence 結構，不是 lesson_store 狀態的一部分。

---

## 10. notice 與 selection / activation 的邊界

Memory freeze notice must not change selection eligibility.

Memory freeze notice must not activate or deactivate lessons.

Notice 不影響：
- lesson 的 selection eligibility（由 lesson_store 邏輯決定）
- lesson 的 activation state（由 activation 邏輯決定）
- 任何 runtime 行為

---

## 11. 未來 runtime 前置要求

若未來要實作 Memory Layer freeze runtime，必須先定義：

```text
learned_principle source_lesson_id mapping
Memory Layer freeze API or admission rule
notice schema
notice audit trace
stale / supersede reason preservation
human review boundary
no direct Memory Layer write guarantee
```

在以上項目全部明確定義並通過 review 之前，不得進入 Memory Layer freeze runtime 實作。

本包只建立 contract 與純資料 helper，不實作 freeze runtime。

---

## 12. 目前不可宣稱

目前不可宣稱：
- ASHL Core 已能直接凍結 Memory Layer
- notice 已被 Memory Layer 接收並執行
- learned_principle 已因 notice 被凍結或更新
- notice 已觸發任何 selection / activation 行為變化

---

## 13. 設計結論

memory_freeze_required notice 是跨層責任邊界的 evidence 橋樑。

核心設計原則：

```text
Memory freeze notice is evidence, not Memory Layer write.
Lesson stale may require memory_freeze_required notice.
Lesson superseded may require memory_freeze_required notice.
Memory freeze notice must not directly modify learned_principle.
Memory freeze notice must preserve source_lesson_id.
Memory freeze notice must preserve stale_or_supersede_reason.
ASHL Core provides evidence.
D清音 Memory Layers decide memory admission.
D清音 Memory Layers decide memory freeze application.
Memory freeze notice must not change selection eligibility.
Memory freeze notice must not activate or deactivate lessons.
Memory freeze notice must not write to lesson_store.
```

ASHL Core 的責任：產生 notice evidence。

D清音 Memory Layers 的責任：決定是否凍結 learned_principle。

兩層之間沒有直接寫入通道。
