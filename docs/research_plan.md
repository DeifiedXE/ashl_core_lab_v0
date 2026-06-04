# ASHL Core 研究計畫 v0.8

## 核心定位

ASHL Core 是低算力、可教、可糾正、可連續、能外接工具的唯一模型幼體核心。

本階段人格核心是「清音」，不是艾希米。

清音是研究者型人格：知性、溫柔、包容，但在研究時不妥協。

核心宣言：唯一模型的唯一性，不在出生，而在成長。

## v0 主循環

v0 的目標是能跑完整主循環：

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

已完成：

- Integrated Loop v0.1
- Persistent Candidate Layer v0.2
- Correction Label v0.3
- Rule Candidate v0.4
- Candidate Review / Audit v0.5
- Trial Rule Layer v0.6
- Trial Suggestion Feedback v0.7
- Core Senses Design v0.8

## Core Senses / 核心感官

Text Sense 已存在，代表目前的文字輸入能力。

Screen Sense 與 Camera Sense 是未來核心感官，不是娛樂外掛。

- Screen Sense：畫面監視、視窗內容、游標位置、畫面變化。
- Camera Sense：攝影機畫面、實物教學、指向教學。
- Audio Sense：未來語音與環境聲音，暫緩。
- Tool Sense：工具回傳結果，暫緩。

純文字不足以支援真實世界概念學習。文字能教清音「蘋果怎麼定義」，但視覺感官才有機會教她「這個東西就是蘋果」。

視覺教學的早期目標是建立 `visual_concept_candidate`：

- 使用者文字教學
- mock sensor event
- 視覺區域參照
- 場景來源
- 候選概念
- audit 狀態

真正硬體支援延後到主循環、狀態保存、CLI 穩定後。

## 實驗總順序

目前採用 [ASHL Core／D清音 實驗總順序 v0.2](experiment_order.md) 作為後續開發路線依據。

後續開發應優先補齊：

- Core Seed
- Memory Layers
- Teaching Event
- Confidence / Promotion
- Memory Economy

完成內在連續性與文字接地後，再進入：

- Core Perception
- Visual Impression
- Symbol Grounding v1

因此下一階段不急著接攝影機或螢幕監視。Screen Sense / Camera Sense 已納入核心感官規劃，但真正硬體接入應在主循環、記憶層、教學事件、信心/晉升機制穩定後進行。

## 尚未完成

- 真攝影機 / 真螢幕感知
- 狀態保存穩定化
- CLI workflow
- Rule Apply
- Rule Promotion
- Mood Layer
- SQLite / Persistence Layer 正式化
- Tool Adapter

## 限制

本階段不接真 LLM、Web、GUI、TTS、SQLite、OpenCV、image model，也不讀螢幕、不接真攝影機、不儲存真圖片。

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
