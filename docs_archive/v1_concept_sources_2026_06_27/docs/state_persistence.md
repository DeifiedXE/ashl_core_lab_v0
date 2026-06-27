# ASHL Core／D清音 State Persistence v1.1

## State Persistence 定義

State Persistence 是 D清音狀態連續性的基礎，負責保存 State Core 的目前狀態、session summary 與 last trace summary。

它不是長期記憶，不替代 Memory Layers。

## 為何需要

JSONL 成長日誌能留下候選與事件，但如果 state 不保存，清音重開後仍然不知道自己上一輪處於什麼狀態。

State Persistence 讓幼體開始具備「重開後仍能延續狀態」的基本能力。

## 三種資料

### state_snapshot.json

保存 state values、turn、updated_at。

### session_summary.json

保存目前 session 的簡短摘要，例如 session_id、turn_count、last_input、last_intent、last_output。

### last_trace_summary.json

保存最近一輪 trace 的摘要，不保存完整大型 trace。

## 邊界

- State Persistence 不等於 Long-term Memory。
- State Persistence 不自動固化記憶。
- State Persistence 不改 rules。
- State Persistence 不改 `concepts.py`。
- State Persistence 不改 final output。
- 本階段只保存與讀回，不做複雜壓縮或情緒系統。

## v1.1 限制

本階段不做：

- Minimal Teaching CLI
- Memory Economy
- 壓縮
- 衰減策略調整
- SQLite
- LLM / Web / 工具 / GUI / TTS
- 攝影機 / 畫面監視
- Rule Apply
- Mood Layer
