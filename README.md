# ASHL Core Lab v0

ASHL Core Lab 是 ASHL Core 的最小 Python 實驗專案，用來驗證可觀察、可糾正、可持續擴充的 Integrated Loop。

本階段人格核心是「清音」，不是艾希米。清音是研究者型人格：知性、溫柔、包容，但在研究時不妥協。

核心宣言：唯一模型的唯一性，不在出生，而在成長。

## 目前範圍

已完成：

- Integrated Loop v0.1
- smoke runner
- unittest
- decision priority 修正
- Persistent Candidate Layer v0.2
- JSONL Persistence Helper
- Memory Candidate v0.1
- Correction Pending Log v0.1
- Correction Label v0.3
- Rule Candidate v0.4

尚未完成：

- Rule Apply
- Concept Counterexample
- Mood Layer
- Persistence Layer
- Tool Adapter

本階段不接真 LLM、Web、工具系統、GUI、TTS、SQLite、資料庫，也不自動固化記憶或自動啟用規則。

## Persistent Candidate Layer v0.2

v0.2 新增最小持久化候選層，使用 JSONL 作為實驗用 artifact 格式。

- `data/memory_candidates.jsonl`：記錄 memory candidate，只是候選，不代表已寫入長期記憶。
- `data/correction_log.jsonl`：記錄 correction pending 與正式 correction label。
- `data/rule_candidates.jsonl`：記錄候選規則與候選概念反例。
- `data/candidate_reviews.jsonl`：記錄候選審核狀態。
- 測試預設使用暫存資料夾，避免污染 repo 的 `data/`。
- `data/*.jsonl` 被 `.gitignore` 忽略，避免把本機實驗資料提交進版控。

## Correction Flow v0.3

1. 使用者糾正時，系統建立 `correction.pending`。
2. 系統追問錯誤類型。
3. 使用者回答「判斷錯 / 反應太強 / 說法不對」。
4. 系統建立正式 correction label。
5. 本階段只分類，不自動建立規則，不自動修改核心。

正式 label：

- `correction.event_mismatch`：代表事件或理解分類錯。
- `correction.reaction_strength_mismatch`：代表反應強度錯。
- `correction.expression_mismatch`：代表語氣或表達錯。

本層不做：

- Rule Candidate
- Rule Apply
- Concept Counterexample
- Correction Label Apply
- 自動修改概念層
- 自動修改狀態層
- 自動啟用規則

## Rule Candidate v0.4

Rule Candidate v0.4 會在 `correction.event_mismatch` 產生後，建立候選規則或候選概念反例，並寫入 `data/rule_candidates.jsonl`。

- `rule_candidates.jsonl` 是候選規則/候選反例日誌。
- 本階段不自動啟用規則。
- 本階段不直接修改 Concept Layer。
- 本階段不修改 `concepts.py`。
- 所有候選都需要 audit。
- 這是「學習前的候選神經芽」，不是正式學習完成。

目前只有 `correction.event_mismatch` 會產生 rule candidate。

- `correction.reaction_strength_mismatch` 不產生 rule candidate。
- `correction.expression_mismatch` 不產生 rule candidate。
- unknown label 不產生 rule candidate。

## Candidate Review / Audit v0.5

Candidate Review v0.5 新增 append-only 候選審核日誌。

- `candidate_reviews.jsonl` 是候選審核日誌。
- review 不會直接改 `rule_candidates.jsonl`。
- `approved_for_trial` 不等於啟用規則。
- 本階段不做 Rule Apply。
- 本階段不修改 Concept Layer。
- 本階段不修改 `concepts.py`。
- 本階段不修改 state effects。
- 所有候選仍需人工或後續流程審核。

支援 review decision：

- `reviewed`
- `rejected`
- `approved_for_trial`

## 專案結構

```text
ashl_core/
  __init__.py
  correction.py
  candidate_review.py
  memory_candidates.py
  persistence.py
  rule_candidates.py
  perception.py
  concepts.py
  state_core.py
  thoughts.py
  deliberation.py
  expression.py
  guard.py
  integrated_loop.py

tests/
  test_correction.py
  test_candidate_review.py
  test_memory_candidates.py
  test_persistence.py
  test_rule_candidates.py
  test_integrated_loop.py
  test_smoke.py
  test_concepts.py
  test_state_core.py
  test_expression_guard.py
  test_deliberation.py

docs/
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

## Integrated Loop

主要 API：

```python
from ashl_core.integrated_loop import run_turn, run_script
```

`run_turn` 支援：

```python
run_turn(
    text: str,
    data_dir: str | Path = "data",
    previous_trace: dict | None = None,
    pending_correction: dict | None = None,
) -> dict
```

流程：

```text
input
-> perception
-> concept layer
-> state core
-> thoughts
-> deliberation
-> expression package
-> mock LLM
-> guard
-> final output + trace
```
