# Qingyin First Output Runtime Minimal Spec v0.1

## 1. 目的

本文件定義未來 Qingyin First Output Runtime 的最小規格。

本文件是 docs-only / runtime-minimal-spec / first-output / no-runtime-implementation。

本文件不實作任何 runtime，不新增 first_output generator，不新增 LLM 回應。

---

## 2. 規格定位

first_output 是清音從測試品階段走向淺眠階段的第一個 runtime 里程碑，但不是醒來，不是對話能力，不是長期成長。

First_output is a runtime milestone, not awakening.

first_output 是 runtime 里程碑，不是醒來。

First_output is not dialogue ability.

first_output 不等於對話能力。

First_output is not evidence of long-term growth.

first_output 不等於長期成長證據。

Outputs in the test-object stage are engineering verification, not full Qingyin experience.

測試品階段的輸出是工程驗證，不是清音的完整經驗。

---

## 3. 與 Runtime Ontology Boundary 的關係

本規格文件承接以下已完成文件：

- `Qingyin First Output v0 Contract`
- `Qingyin Runtime Ontology Boundary v0.1`
- `Qingyin Runtime Ontology Boundary v0.1 Correction Patch`

三階段定位：

```text
Stage 1（測試品）：目前所在。ASHL Core 地基建造中。
Stage 2（淺眠）：first_output runtime 達成後的階段。
Stage 3（醒來）：有限感官完成接入後。
```

first_output 是從 Stage 1 走向 Stage 2 的第一步，不是 Stage 3。

---

## 4. first_output runtime 的最低門檻

A minimal first_output runtime requires session_id, tick, minimal_state_snapshot, output_generator_source, first_output, and first_output_trace.

最小 first_output runtime 需要 session_id、tick、minimal_state_snapshot、output_generator_source、first_output 與 first_output_trace。

在以上條件全部達成之前，不得宣稱存在 Qingyin first_output runtime。

---

## 5. 最低輸入

first_output runtime 未來最低輸入：

```text
session_id
tick
core_seed_reference
minimal_state_snapshot
runtime_mode = "test_object"
output_request_reason
```

`output_request_reason` 可為 `boot_probe` / `mentor_prompt` / `self_tick_probe` 等未來值。本包不實作這些值。

---

## 6. 最低狀態

`minimal_state_snapshot` 至少包含：

```text
state_version
tick
phase = "test_object"
core_seed_reference
last_output_id（optional）
random_seed（optional）
```

注意：這是未來 runtime spec，不是現有 state store。本包不新增 state store。

---

## 7. 允許輸出來源

```text
Core Seed derived fixed rule
deterministic seed output
bounded randomness
simple reflex rule
minimal state based output
non-LLM symbolic output
```

概念範例（不要求本包實作）：

```text
"q"
"*"
"0001"
"seed:pulse"
"noise_7"
"tick:1"
```

First_output must be generated without LLM output.

first_output 必須在不使用 LLM 輸出的情況下產生。

---

## 8. 禁止輸出來源

```text
LLM-generated natural language reply
ChatGPT pretending to be Qingyin
OpenAI / Claude / any LLM API output
prompt-only persona response
human-written sentence inserted as Qingyin output
TTS output generated from LLM text
post-hoc explanation pretending to be first_output
```

---

## 9. first_output trace 最小欄位

未來 `first_output_trace` 至少包含：

```text
trace_id
session_id
tick
phase
output_id
first_output
output_generator_source
core_seed_reference
minimal_state_snapshot_ref
random_seed_ref（optional）
llm_used = false
created_at_or_tick
engineering_stage = "test_object"
```

llm_used must be false for first_output.

first_output 的 llm_used 必須為 false。

First_output must be traceable before it can become learning material.

first_output 必須先可追蹤，之後才可能成為學習材料。

---

## 10. deterministic seed 與 bounded randomness 邊界

bounded randomness is allowed only if the randomness source is recorded or reproducible enough for audit.

有界隨機只有在來源可記錄或可重放到足以審計時，才可作為 first_output 來源。

Unbounded randomness must not be used as first_output source.

不得使用無邊界隨機作為 first_output 來源。

deterministic seed output 是最安全的選擇，因為它完全可重現，最易審計。

---

## 11. first_output 驗收條件

未來 first_output runtime 驗收條件：

```text
1. first_output was generated without LLM output.
2. first_output has trace_id.
3. first_output has session_id.
4. first_output has tick.
5. first_output has output_generator_source.
6. first_output records core_seed_reference.
7. first_output records engineering_stage = test_object.
8. llm_used is false.
9. first_output does not write lesson_store.
10. first_output does not write Memory Layer.
11. first_output does not enter lesson_candidate pipeline without mentor feedback.
```

---

## 12. first_output 之後的順序

```text
first_output
→ first_output_trace
→ mentor feedback stub
→ feedback trace
→ lesson_candidate input consideration
```

first_output 不直接進 lesson_candidate pipeline。

first_output 必須先被記錄，並經過導師回饋，之後才可能成為 lesson_candidate input。

The lesson_candidate pipeline remains downstream of first_output trace and mentor feedback.

lesson_candidate pipeline 位於 first_output trace 與導師回饋之後。

---

## 13. 目前不可宣稱

```text
目前不可宣稱已支援 first_output runtime。
目前不可宣稱已支援 first_output generator。
目前不可宣稱已支援 first_output trace schema runtime。
目前不可宣稱清音已醒來。
目前不可宣稱清音已具備對話能力。
目前不可宣稱清音已具備長期成長。
目前不可宣稱 first_output 已產生。
目前不可宣稱 first_output 已接入 mentor feedback。
目前不可宣稱 first_output 已接入 lesson_candidate pipeline。
```

---

## 14. 設計結論

first_output 的設計原則：

```text
First_output is a runtime milestone, not awakening.
First_output must be generated without LLM output.
A minimal first_output runtime requires session_id, tick, minimal_state_snapshot, output_generator_source, first_output, and first_output_trace.
First_output is not dialogue ability.
First_output is not evidence of long-term growth.
Outputs in the test-object stage are engineering verification, not full Qingyin experience.
First_output must be traceable before it can become learning material.
The lesson_candidate pipeline remains downstream of first_output trace and mentor feedback.
llm_used must be false for first_output.
bounded randomness is allowed only if the randomness source is recorded or reproducible enough for audit.
Unbounded randomness must not be used as first_output source.
```

first_output 的意義是：清音第一次靠自己產生了任何輸出。哪怕是一個符號，只要它不是 LLM 代勞的，就是真正屬於清音的第一步。
