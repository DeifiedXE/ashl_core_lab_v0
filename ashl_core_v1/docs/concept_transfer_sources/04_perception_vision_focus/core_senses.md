# Core Senses v0.8

ASHL Core / 清音需要逐步建立核心感官。Screen Sense 與 Camera Sense 不是娛樂外掛，而是未來讓唯一模型理解真實世界概念的基礎。

## Core Senses 定義

- Text Sense：文字輸入。這是目前已存在的核心感官。
- Screen Sense：畫面監視、視窗內容、游標位置、畫面變化。未來可用於理解使用者正在看的介面與指向的畫面區域。
- Camera Sense：攝影機畫面、實物教學、指向教學。未來可用於把實物、場景來源、文字標籤與候選概念建立關聯。
- Audio Sense：未來語音與環境聲音，暫緩。
- Tool Sense：工具回傳結果，暫緩。

## 為何 Screen / Camera 是核心感官

純文字可以教清音「蘋果怎麼定義」，但視覺感官才有機會教她「這個東西就是蘋果」。

如果使用者指著蘋果並說「這是蘋果」，系統需要能把以下資訊連在一起：

- 使用者文字教學
- 視覺區域
- 場景來源
- 候選概念
- 審核狀態

因此 Screen Sense 與 Camera Sense 應被納入核心感官規劃，而不是視為可有可無的外掛。

## v0.8 範圍

本階段只做：

- sensor event 資料模型
- visual concept candidate 資料模型
- mock sensor input 測試
- 設計文件

本階段不做：

- 真攝影機
- 螢幕截圖
- OpenCV
- image model
- 手勢辨識
- 物件辨識
- 真圖片儲存
- LLM / Web / GUI / TTS / SQLite

## Sensor Event

Sensor event 是未來感官輸入的標準紀錄格式。v0.8 只建立資料模型，不收集真實感官資料。

必要欄位：

- `id`
- `type`
- `source`
- `event_type`
- `payload`
- `created_at`

允許的 source：

- `text`
- `screen`
- `camera`
- `audio`
- `tool`

## Visual Concept Candidate

Visual concept candidate 是由 sensor event 與使用者教學建立的候選概念。

它是候選，不是正式概念。

必要限制：

- `status = candidate`
- `audit_required = true`
- 不包含真圖片資料
- 不自動固化概念
- 不修改 Integrated Loop 行為
