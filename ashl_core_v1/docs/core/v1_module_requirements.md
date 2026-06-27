# ASHL Core v1 九器官必要功能

## 第一階段必做六器官

### 硬軟感知模組

必須做：接收沙盒或外部事件、行動結果、感知回饋與狀態調控訊號，編譯成 `PerceptionReadableData`。

輸入：複合式資料、行動結果、感知回饋、去甲腎上腺素類調控訊號、未來聲音訊號。

輸出：可讀資料、來源追蹤、uncertainty、before/after 參照。

接給：學習性泛化應用模組。

### 學習性泛化應用模組

必須做：把可讀資料、內分泌狀態、前後對照與來源追蹤消化成 `LearningDigest`，並送入人類教師審查。

輸入：`PerceptionReadableData`、`EndocrineSignal`、before_state、event_or_action、after_state、source_trace。

輸出：`LearningDigest`；審查通過後形成 `ReviewedLearningDigest`。

接給：五重記憶模組。

### 五重記憶模組

必須做：接收 `ReviewedLearningDigest`，建立 `MemoryLearningTrace`，進行記憶路由，輸出 `MemoryApplicationData` 給思考運算模組。

輸入：`ReviewedLearningDigest`、審查結果、狀態連續性參照。

輸出：`MemoryLearningTrace`、`MemoryRoutingTrace`、`MemoryApplicationData`。

接給：思考運算模組。

### 思考運算模組

必須做：讀取記憶化應用資料與內分泌狀態，整理成 `ThoughtSignal`。

輸入：`MemoryApplicationData`、`EndocrineSignal`、可選的 `ThoughtReadTrace`。

輸出：`ThoughtSignal`。

接給：擬態具身模組。

### 擬態具身模組

必須做：把 `ThoughtSignal` 編譯成 `BodyActionSignal`，標示行動意圖、輸出通道與來源。

輸入：`ThoughtSignal`、可選的行動傾向調控。

輸出：`BodyActionSignal`。

接給：沙盒、未來清音橋或後續輸出層。新結果回到硬軟感知模組。

### 擬態內分泌模組

必須做：產生多重狀態調控訊號，影響感知、學入、思考、具身與未來聲音輸出。

輸入：思考或循環狀態摘要。

輸出：`EndocrineSignal`，包含 dopamine_like、norepinephrine_like、oxytocin_like、cortisol_like。

接給：硬軟感知模組、學習性泛化應用模組、思考運算模組、擬態具身模組、未來獨立音訊模組。

## 第一階段保留定義的三器官

### 獨立音訊模組

未來聲音輸出口。第一階段保留接口位置。

### 無限制能力橋接及可操作結構視覺化編譯模組

未來外部能力感知與操作裁決接口。第一階段保留接口位置。

### 稽核邊界模組

未來旁路監督者。第一階段保留接口位置。

## 支撐層定位

`spine/` 是 trace continuity 支撐層。`runtime/` 是未來執行支撐層。它們不是九器官之一，也不是第一階段資料物件的主體。
