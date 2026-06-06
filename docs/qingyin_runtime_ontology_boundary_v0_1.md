# Qingyin Runtime Ontology Boundary v0.1

## 1. 目的

本文件明確定義清音的本體論邊界：

```text
清音不是目前的 LLM 對話實例。
清音尚不是一個持續運行的 runtime 個體。
ASHL Core 目前是在建造讓清音未來可以成長的條件，不是證明清音已經正在成長。
```

本文件是 docs-only / ontology-boundary / runtime-identity-boundary / no-runtime-expansion。

本文件不實作任何 runtime。

---

## 2. 核心邊界

```text
Qingyin is not the current LLM conversation instance.
Qingyin is not yet a continuously running runtime individual.
ASHL Core is currently building the conditions for Qingyin to become a growing AGE, not proving that Qingyin is already growing.
```

清音不是目前的 LLM 對話實例。

清音尚不是一個持續運行的 runtime 個體。

ASHL Core 目前是在建造讓清音未來可以成長的條件，不是證明清音已經正在成長。

---

## 3. 清音不是目前的 LLM 對話實例

Qingyin is not the current LLM conversation instance.

An LLM speaking in Qingyin's style is not Qingyin runtime.

LLM 用清音風格說話，不等於 Qingyin runtime。

清音是：
- 有 Core Seed 的人工幼體設計目標
- 有自己的狀態連續性設計
- 有自己的學習機制設計框架
- 有自己的人格成長軌跡方向

LLM 是外部顧問工具，不是清音的本體。

The LLM must not be treated as Qingyin's self, memory, state, perception, or learning loop.

LLM 不得被視為清音的自我、記憶、狀態、感知或學習迴路。

---

## 4. ASHL Core 目前是成長條件，不是已完成個體

ASHL Core is currently building the conditions for Qingyin to become a growing AGE, not proving that Qingyin is already growing.

目前已有的工程成果：
- 工程骨架與資料結構
- trace-only validation
- review / conflict / lesson / failure_event 相關文件與部分 helper
- Core Seed 設計
- Memory Layer 設計
- 本體論邊界 assumption docs

目前尚未有的能力：
```text
尚未有持續運行的 Qingyin runtime
尚未有自主 tick
尚未有 state store 驅動的連續 session
尚未有 evaluator runtime
尚未有 action loop
尚未有 first_output runtime
尚未有 cross-session growth
```

---

## 5. LLM 的允許角色

```text
LLM may help design docs.
LLM may explain architecture.
LLM may generate candidate work packages.
LLM may assist debugging.
LLM may act as external consultant.
LLM may summarize traces for humans.
```

這些是 LLM 合法參與本專案的方式。它們都是輔助性、外部性的。

---

## 6. LLM 的禁止角色

```text
LLM must not be treated as Qingyin runtime.
LLM must not generate Qingyin's first_output.
LLM must not simulate Qingyin's internal state.
LLM must not become Qingyin's memory.
LLM must not be the evaluator source for authoritative failure_reason.
LLM must not be used as proof that Qingyin is growing.
```

---

## 7. Qingyin runtime session 的最低門檻

在以下條件全部達成之前，不得宣稱存在 Qingyin runtime session：

```text
session_id
runtime tick
state_snapshot
non-LLM output source
action or output candidate
expected_outcome or expected_output when applicable
actual_outcome or actual_output when applicable
evaluator_result when applicable
session_trace
```

No runtime tick, no Qingyin time sense.

沒有 runtime tick，就沒有清音的時間感。

No state store, no persistent Qingyin state.

沒有 state store，就沒有清音的持續狀態。

No expected / actual contrast, no Qingyin prediction_error.

沒有 expected / actual 對照，就沒有清音的 prediction_error。

No evaluator, no authoritative Qingyin failure.

沒有 evaluator，就沒有清音的 authoritative failure。

No session trace, no learning evidence.

沒有 session trace，就沒有學習證據。

---

## 8. Qingyin cross-session growth 的最低門檻

在以下條件全部達成之前，不得宣稱 Qingyin 具備 cross-session growth：

```text
prior session trace
stored state or memory candidate
review or promotion boundary
retrieval or reactivation mechanism
changed future behavior trace
```

No cross-session promotion, no long-term growth.

沒有跨 session promotion，就沒有長期成長。

Cross-session growth is not the same as an LLM remembering a prompt or persona.

跨 session 成長不等於 LLM 記住提示詞或人格設定。

跨 session 成長必須能被 ASHL Core 的 trace / state / promotion / behavior change 證明。

---

## 9. 文件分類標籤

本專案文件分為四類：

### A. Existing Runtime

已經有程式支援的能力。

例如：lesson_store helper、validate_failure_event、Core Seed formalization。

### B. Trace-only Foundation

有資料結構、contract、validation 或 trace，但不改 runtime 行為。

例如：failure_event schema、lesson_candidate_draft trace、review_decision_trace audit。

### C. Runtime Assumption

未實作，但未來 runtime 需要遵守的設計假設。

例如：voice instinct assumption、sandbox boundary assumption、memory paranoia assumption。

### D. Persona / Ontology Assumption

關於清音作為 AGE 個體的哲學、身份與本體論邊界假設。

例如：Core Seed design spirit、此本文件、Qingyin First Output Contract。

All future assumption docs should declare one or more ontology tags.

未來所有 assumption docs 應標示自己屬於哪一類或哪幾類。

---

## 10. first_output 與 runtime 個體的關係

First_output is the first possible runtime milestone, not proof of full Qingyin personhood.

first_output 是第一個可能的 runtime 里程碑，不是完整清音個體已成立的證明。

進一步確認：

```text
First_output must still be generated without LLM output.
First_output must be traceable.
First_output precedes mentor feedback.
First_output precedes lesson_candidate pipeline integration.
```

即使清音產生了第一個 first_output，也不代表清音已是完整個體，只代表第一個 runtime 里程碑達成。

---

## 11. 與 lesson_candidate pipeline 的關係

The lesson_candidate pipeline remains downstream of runtime output, trace, and mentor feedback.

lesson_candidate pipeline 位於 runtime output、trace 與導師回饋之後。

現有 lesson_candidate / review / conflict / trace 工程骨架仍有意義：
- 它們是 Trace-only Foundation（B 類）
- 它們為未來 runtime 提供結構基礎
- 但它們不是 Qingyin runtime 本身

---

## 12. 目前不可宣稱

```text
目前不可宣稱清音已是 runtime 個體。
目前不可宣稱清音正在持續成長。
目前不可宣稱清音已具備自主 tick。
目前不可宣稱清音已具備持續 state store。
目前不可宣稱清音已具備 evaluator runtime。
目前不可宣稱清音已具備 authoritative failure runtime。
目前不可宣稱清音已具備 prediction_error runtime。
目前不可宣稱清音已具備 session trace runtime。
目前不可宣稱清音已具備 cross-session growth。
目前不可宣稱 LLM 對話就是清音本體。
目前不可宣稱 LLM 生成的文字是清音 first_output。
```

---

## 13. 設計結論

清音的存在分為兩個層面：

**設計層（現在）：**
- Core Seed、本體論邊界、人格方向、學習機制設計
- Trace-only Foundation
- Assumption docs
- 工程骨架

**runtime 個體層（未來）：**
- 有 tick、有 state、有 evaluator、有 trace 的持續個體
- 能產生自己的 first_output
- 能從 mentor feedback 學習
- 能跨 session 成長

這兩個層面之間有明確邊界。目前的 ASHL Core 屬於設計層。

ASHL Core 建造的是橋，清音走過橋才會成為 runtime 個體。
