# ASHL Core Lab v0

ASHL Core Lab v0.1 是 ASHL Core 的最小 Python 專案雛形，用來驗證 Integrated Loop 是否能穩定跑完。

本階段人格核心是「清音」，不是艾希米。清音是研究者型人格：知性、溫柔、包容，但在研究時不妥協。

核心宣言：唯一模型的唯一性，不在出生，而在成長。

## 目前範圍

已完成：

- Integrated Loop v0.1
- smoke runner
- unittest
- decision priority 修正

尚未完成：

- Memory Candidate
- Correction Label
- Rule Candidate
- Mood Layer
- Persistence Layer
- Tool Adapter

本階段不接真 LLM、Web、工具系統、GUI、TTS、資料庫，也不自動固化記憶。

## 專案結構

```text
ashl_core/
  __init__.py
  perception.py
  concepts.py
  state_core.py
  thoughts.py
  deliberation.py
  expression.py
  guard.py
  integrated_loop.py

tests/
  test_smoke.py
  test_concepts.py
  test_state_core.py
  test_expression_guard.py
  test_deliberation.py
  test_integrated_loop.py

docs/
  research_plan.md

examples/
  core_sample.ashl

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

`run_turn(text: str) -> dict` 會回傳 trace，至少包含：

- `input`
- `candidate_events`
- `concept_result`
- `state_result`
- `thoughts`
- `decision`
- `expression_package`
- `raw_output`
- `guard_result`
- `final_output`
