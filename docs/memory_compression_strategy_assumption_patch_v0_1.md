# ASHL Core/D清音：記憶壓縮策略設計假設 v0.1 補丁

## 目的

本文補充記憶壓縮策略在現階段的適用範圍與壓縮單位。

本文是設計假設補丁，不是 runtime 實作。

本補丁核心目標是避免文字記憶壓縮策略被誤用到未來的圖像記憶或 Symbol Grounding 階段。

---

## 一、現階段壓縮單位

現階段只處理文字記憶階段。

文字記憶的最小壓縮單位為：

- 文字片段
- 來源情境摘要
- 信心等級
- 使用次數

細節內容可以被壓縮，但以上四項必須保留。

Text memory compression must preserve text fragment, source context summary, confidence level, and usage count.

---

## 二、不得只保留結論

文字記憶如果只保留壓縮後的結論，會失去來源與可信度脈絡。

壓縮後的記憶不能只剩下結論，而必須保留：

- 這段記憶來自哪裡
- 它在什麼情境下形成
- 目前可信度如何
- 它被使用過幾次

---

## 三、文字記憶階段限定

本策略僅適用於文字記憶階段。

此階段的壓縮對象是：

- text memory
- text fragment
- dialogue-derived memory
- document-derived memory
- textual lesson / note / assumption summary

不得將本策略直接套用到：

- image memory
- visual impression
- object concept memory
- multimodal symbol grounding memory

---

## 四、圖像記憶壓縮

圖像記憶壓縮延後到圖像感官完成後再設計。

Image memory compression must not reuse the text-only compression strategy.

現階段不得：

- 沿用文字壓縮策略到圖像記憶
- 用文字片段壓縮邏輯直接處理圖像
- 把圖像記憶降格成單純文字標籤
- 提前定義圖像記憶壓縮 schema

---

## 五、未來圖像記憶壓縮方向

未來圖像記憶壓縮單位是：圖像 + 文字 的物體概念整體。

可能包含：

- visual impression
- object identity / label
- textual explanation
- interaction history
- grounding evidence

此處只記錄方向，不定 schema。

---

## 六、與 Symbol Grounding 的關係

Symbol Grounding v1 完成後，才統一考慮文字記憶與圖像記憶的關聯壓縮方式。

在 Symbol Grounding v1 完成前：

- 文字記憶壓縮 = 文字階段限定
- 圖像記憶壓縮 = 延後設計
- 文字 / 圖像關聯壓縮 = 不提前定義

---

## 七、目前不可宣稱

目前不可宣稱：

- 已支援記憶壓縮 runtime
- 已支援圖像記憶壓縮
- 已支援圖像 + 文字物體概念壓縮
- 已完成 Symbol Grounding v1
- 文字記憶壓縮策略可直接套用到圖像記憶
- 文字標籤等同於圖像概念