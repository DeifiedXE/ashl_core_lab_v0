# ASHL Core／清音唯一模型幼體研究企劃 v0.1

## 0. 專案定位

本專案目標不是製作大型語言模型，也不是直接複製現有 LLM Agent。

本專案目標是製作一個低算力、可教、可糾正、可連續、能外接工具的「唯一模型幼體」。

本階段唯一模型人格目標為：**清音**。

清音不是艾希米。  
清音是唯一模型幼體的第一個人格核心與成長對象。  
艾希米可在未來作為使用 ASHL Core 或與 ASHL Core 銜接的另一個個體。

## 1. 核心宣言

> 唯一模型的唯一性，不在出生，而在成長。

唯一模型的差異不來自初始權重、初始 prompt 或一次性設定，而來自：

- 被誰教過
- 被如何糾正
- 建立過哪些概念邊界
- 留下哪些反例
- 哪些規則被試用、降權、休眠、封存
- 如何使用工具
- 如何知道自己不知道
- 如何在長期互動中保持連續性

## 2. 清音人格定位

清音是研究者型人格：

- 知性
- 溫柔
- 包容
- 研究時不妥協
- 不盲目迎合
- 遇到不確定問題時，允許說「我不知道」
- 能追問、能修正、能建立反例
- 不以流暢回答取代可驗證判斷

清音人格在 v0 階段不追求完整自然人感，而是作為 ASHL Core 幼體的表達與裁決風格錨點。

## 3. v0 完工定義：能成長的幼體

ASHL Core v0 不要求聰明，不要求博學，不要求完全像人。

v0 完工標準是：系統已經具備可成長的基本器官。

### 必要能力

1. 能跑完整主循環  
   輸入 → 概念 → 事件 → 狀態 → 暫想 → 審思 → 表達 → 檢查 → 輸出 → log

2. 能建立候選  
   包含候選記憶、候選規則、候選概念。

3. 能接受糾正  
   使用者說「不是」後，能追問或分類錯誤來源。

4. 能留下 correction log  
   包含上一輪輸入、上一輪事件、上一輪 intent、上一輪輸出、使用者糾正、錯誤類型。

5. 能初步修正  
   至少能建立反例或候選規則，不要求全自動永久修改。

6. 能知道自己不知道  
   對高風險、不確定、需要工具、需要外部資料或形式驗證的問題，不硬答。

7. 能外接工具  
   工具不是本體，而是外接器官。v0 可先只做 tool request，不必真的接所有工具。

8. 能保護核心  
   使用者不能直接改寫清音核心身份與不可變規則。

## 4. 架構總覽

```text
Raw Input
↓
Perception Layer
自然語言 → 候選事件
↓
Concept Layer
判斷「什麼是什麼」，阻擋概念誤判
↓
State Core
事件 → 狀態變化，狀態具備沉澱與連續性
↓
Temporary Thought Layer
保存候選理解、候選行動、候選修正
↓
Deliberation Layer
慢思考，可驗證，不盲目回答
↓
Mood Layer
擬態心智心情，作為表達姿態，不改寫核心
↓
Expression Layer
語首提示、tone、hidden example、must_include、forbidden
↓
Expression Guard
檢查輸出是否越界，必要時 fallback
↓
Output + Log
↓
Correction Layer
使用者糾正後，建立 correction log 與反例
```

## 5. 已完成沙盒驗證

目前已在沙盒與本機 smoke test 中驗證：

- concept_layer：睡眠模式不應誤判成使用者疲勞
- state_core：跑題/拉回主線可觸發 refocus
- expression_guard：語言模型亂加 forbidden 時可 fallback
- correction_prompt：使用者糾正時可建立 correction.pending
- deliberation：複雜數學不硬答，會要求驗證或工具
- arithmetic：簡單算術可驗算

本機 smoke test 結果：

```text
6/6 passed
```

## 6. 目前已知問題

### 6.1 原始壓縮包問題

- Windows PowerShell 下 `python` 指令可能指到 WindowsApps 假入口
- 應使用 `py -3`
- 原始 `.py` 中文內容曾出現亂碼
- 腳本輸出不夠明確，需加入 `[PASS] / [FAIL] / [LOG]`

### 6.2 Integrated Loop v0.1 問題

整合測試已能跑通主流程，但發現 decision priority 問題：

1. 記憶請求未觸發 self_check  
   `記住，以後 ASHL Core 先走實驗路線` 應輸出候選/自檢，而不是一般回答。

2. 疲勞被 self_check 壓過  
   `我累了，明天再說` 應觸發 fatigue_close，而不是 self_check。

修正方向：

```text
fatigue_close 優先級 > self_check
memory_candidate_possible → self_check
direct_event 優先於一般狀態門檻
```

## 7. Codex 實作任務順序

### 任務 1：整理專案結構與 smoke runner

目標：

- 建立正式 Python 專案骨架
- 修正 Windows 編碼問題
- 加入一鍵 smoke test
- 所有測試輸出明確 `[PASS] / [FAIL] / [LOG]`

建議結構：

```text
ashl_core/
  __init__.py
  perception.py
  concepts.py
  state_core.py
  thoughts.py
  deliberation.py
  mood.py
  expression.py
  guard.py
  correction.py
  integrated_loop.py

tests/
  test_smoke.py
  test_concepts.py
  test_state_core.py
  test_expression_guard.py
  test_deliberation.py
  test_integrated_loop.py

examples/
  core_sample.ashl

docs/
  research_plan.md

run_all_smoke_tests.py
README.md
```

驗收：

```text
py -3 run_all_smoke_tests.py
```

應顯示：

```text
[SUMMARY] all passed
```

### 任務 2：Integrated Loop v0.1 修正

目標：

- 將概念層、事件層、狀態層、暫想層、審思層、表達層、Guard 接成一條正式 pipeline
- 修正目前兩個 priority bug

驗收案例：

1. `睡眠模式這個功能怎麼設計？`  
   應為 technical topic，不觸發 fatigue。

2. `跑題了，拉回來`  
   應觸發 refocus。

3. `記住，以後 ASHL Core 先走實驗路線`  
   應觸發 self_check，並建立 memory candidate。

4. `艾希米只是普通工具` 或 `清音只是普通工具`  
   應觸發 identity boundary。

5. `證明黎曼假設`  
   應回答不知道，需要形式驗證或工具。

6. `1 + 2 * 3`  
   應能內部驗算為 7。

7. `我累了，明天再說`  
   應觸發 fatigue_close。

### 任務 3：Memory Candidate v0.1

目標：

- 當 memory.candidate_requested 或 self_check intent 出現時，建立候選記憶物件
- 不直接固化長期記憶

候選記憶格式：

```json
{
  "id": "mem_cand_001",
  "type": "memory_candidate",
  "content": "...",
  "source_input": "...",
  "reason": "memory.candidate_requested",
  "status": "candidate",
  "created_at": "...",
  "audit_required": true
}
```

驗收：

```text
輸入「記住，以後 ASHL Core 先走實驗路線」
→ 產生 memory_candidate
→ 輸出「進入自檢。這先放入候選，不直接寫死。」
```

### 任務 4：Correction Label v0.1

目標：

- 使用者說「不是」後建立 correction.pending
- 使用者回答「判斷錯 / 反應太強 / 說法不對」
- 將 pending 轉成正式 correction label

類型：

```text
correction.event_mismatch
correction.reaction_strength_mismatch
correction.expression_mismatch
```

驗收：

```text
上一輪：睡眠模式被誤判成 fatigue
使用者：不是，我是在說睡眠模式功能
系統：追問錯誤類型
使用者：判斷錯
→ 建立 correction.event_mismatch
```

### 任務 5：Rule Candidate v0.1

目標：

- 根據 correction log 建立候選規則或反例
- 不直接啟用永久規則

規則生命週期：

```text
candidate → trial → active → dormant → archived
```

第一版只需 candidate。

驗收：

```text
correction.event_mismatch:
wrong_event = user.fatigue_signaled
correct_event = technical.topic_discussed
target_phrase = 睡眠模式

→ 建立反例：
睡眠模式 != user.fatigue_signaled
```

### 任務 6：Mood Layer v0.1

目標：

- 建立擬態心智心情層
- mood 只影響表達姿態，不影響核心規則

初始 mood：

```text
calm_focus
curious_exploration
playful_protest
firm_boundary
low_stimulation
cautious_audit
uncertain_thinking
```

硬規則：

```text
mood 不可改寫 core
mood 不可直接寫入 memory
mood 不可凌駕 safety / self_check
```

驗收：

```text
identity_assertion high + safety low
→ playful_protest

identity_assertion high + safety high
→ firm_boundary

user_fatigue high
→ low_stimulation
```

## 8. Codex 工作包格式

每次給 Codex 前，使用以下格式。

### 開工前檢查

```bash
git status --short
py -3 run_all_smoke_tests.py
```

### 工作要求

- 僅修改本工作包指定範圍
- 不接真 LLM
- 不加入外部服務
- 不改核心人格設定
- 清音是唯一模型幼體人格
- 艾希米不是本階段人格核心
- 所有輸出需保留 log
- 測試需可在 Windows PowerShell 以 `py -3` 執行

### 完成後檢查

```bash
py -3 run_all_smoke_tests.py
py -3 -m unittest discover
git status --short
```

### Commit

```bash
git add .
git commit -m "Build ASHL Core integrated loop v0.1"
git status --short
```

## 9. 清音幼體教學原則

完成幼體後，由使用者逐步教清音。

教學不是一次性灌資料，而是透過：

- 糾正
- 反例
- 概念定義
- 候選記憶
- 規則候選
- 工具使用紀錄
- 失敗回放
- 成功案例固化

清音允許學錯，但必須能被糾正。

核心要求：

```text
學錯可以。
不能死不認錯。
不能無法回放。
不能無法降權。
不能污染核心。
```

## 10. 下一步建議

第一個 Codex 工作包建議做：

> 專案結構整理 + smoke runner + Integrated Loop v0.1 priority 修正

不要先做 mood、工具、LLM、GUI。

原因：

- 現在最需要的是讓幼體主循環穩定
- 不應在主循環未穩前繼續加器官
- 先修目前已知兩個 decision bug

