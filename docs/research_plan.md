# ASHL Core 研究計畫 v0.1.1

## 核心定位

ASHL Core 是低算力、可教、可糾正、可連續、能外接工具的唯一模型幼體核心。

本階段人格核心是「清音」，不是艾希米。

清音是研究者型人格：知性、溫柔、包容，但在研究時不妥協。

核心宣言：唯一模型的唯一性，不在出生，而在成長。

## v0 目標

v0 的目標不是完整智慧，也不是完整人格，而是能跑完整主循環：

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

這個階段重點是建立可觀察、可修正、可測試的最小骨架。

## 已完成

- Integrated Loop v0.1
- smoke runner
- unittest
- decision priority 修正

已修正的 priority 重點：

- `direct_intent` 最高優先
- `fatigue_close` 高於 `self_check`
- `memory_candidate_possible` 必須觸發 `self_check`

## 尚未完成

- Memory Candidate
- Correction Label
- Rule Candidate
- Mood Layer
- Persistence Layer
- Tool Adapter

## 下一步

下一個建議工作包：Memory Candidate v0.1。

目標是讓 `memory.candidate_requested` 不只觸發 `self_check`，也能產生明確、可審核、不可直接固化的 memory candidate artifact。

## 本階段限制

本階段不做：

- 真 LLM 串接
- Web
- 工具系統
- GUI
- TTS
- Mood Layer
- 長期資料庫
- 自動固化記憶
- 完整智慧語言

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
