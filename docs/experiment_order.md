# ASHL Core／D清音 實驗總順序 v0.2

本文件定義 ASHL Core／D清音 後續實驗總順序，作為開發路線依據。

## 實驗順序

1. Core Seed

   定義 D清音是誰、為何存在、人格方向、權限邊界、成長原則。

2. Memory Layers

   建立核心、長期、工作、歸檔記憶四層，先穩住連續性。

3. Teaching Event

   讓俊誠能用文字教她、修正她、確認她。

4. Confidence / Promotion

   建立信心分數、錯誤次數、確認次數、晉升規則。

5. Memory Economy

   加入壓縮、衰減、歸檔、重複合併，避免記憶臃腫。

6. Symbol Grounding v0

   先用文字建立「詞、概念、情境、行動、結果」的基本連結。

7. Core Perception

   加入畫面監視與攝影機支援，作為核心感知入口。

8. Visual Impression

   不保存完整錄影，而是形成模糊性影像印象、重點、位置、場景感與不確定標記。

9. Symbol Grounding v1

   把字、詞、物件、畫面、行動、情境與記憶正式接起來。

## 階段分界

1～6 是內在連續性與文字接地階段。

7～9 是核心感官與視覺接地階段。

Screen Sense / Camera Sense 是核心感官規劃，不是娛樂外掛。

真正硬體接入應在主循環、記憶層、教學事件、信心/晉升機制穩定後進行。

## 目前 repo 對應狀態

已完成 / 部分完成：

- Teaching Event：部分完成，已有 correction pending / correction label / rule candidate / review / trial feedback。
- Confidence / Promotion：部分完成，已有 candidate review、approved_for_trial、trial feedback，但尚未 promotion gate。
- Symbol Grounding v0：部分完成，已有文字概念邊界與 concept counterexample candidate。

尚未完整完成：

- Core Seed：需正式文件化。
- Memory Layers：目前只有 JSONL candidate / log，尚未形成核心、長期、工作、歸檔四層。
- Memory Economy：尚未開始。
- Core Perception：尚未實作，只納入規劃。
- Visual Impression：尚未開始。
- Symbol Grounding v1：尚未開始。
