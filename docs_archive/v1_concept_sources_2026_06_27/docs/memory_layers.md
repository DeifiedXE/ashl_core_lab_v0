# ASHL Core／D清音 Memory Layers v1.0

## Memory Layers 定義

D清音的記憶不應全部混在同一個檔案中。

記憶需要分層，避免核心污染、工作記憶臃腫、候選資料直接固化。

## 四層記憶

### Core Memory

- 存放核心身份、Core Seed 參照、不可由普通流程改寫的核心資料。
- 本包只讀，不開放普通寫入。
- 任何 memory candidate / correction / rule candidate / trial feedback 都不能直接改 Core Memory。

### Long-term Memory

- 存放未來經過確認與晉升的穩定記憶。
- 本包只提供資料模型與 append 入口。
- 不自動從 memory candidate 晉升。

### Working Memory

- 存放目前 session、最近互動摘要、暫時任務上下文。
- 可覆蓋 snapshot。
- 可在未來與 state persistence 連接。

### Archive Memory

- 存放過期、封存、降權或不再主動使用的記憶。
- 本包只提供 append 入口。

## 與現有 JSONL 的關係

現有：

- `memory_candidates.jsonl`
- `correction_log.jsonl`
- `rule_candidates.jsonl`
- `candidate_reviews.jsonl`
- `trial_feedback.jsonl`

這些是成長日誌與候選資料，不等於 Long-term Memory。

Long-term Memory 必須透過未來 promotion / confirmation 流程產生。

## 安全邊界

- Core Memory 不可由普通流程寫入。
- Core Seed 不等於普通記憶。
- Memory Candidate 不等於 Long-term Memory。
- Correction 不等於直接改記憶。
- Trial Feedback 不等於直接改記憶。

## v1.0 限制

本包不做：

- 自動固化
- Memory Economy
- 壓縮
- 衰減
- 重複合併
- SQLite
- LLM / Web / 工具 / GUI / TTS
