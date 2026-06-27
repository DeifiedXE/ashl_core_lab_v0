# ASHL Core v1 / 清音總施工藍圖 v0

## 0. 總目標

ASHL Core v1 的目標不是重做舊 repo，也不是只做思考系統。

目標是建立一個可以被使用者照顧、教導、觀察、修正，並能在自己的環境中累積成長軌跡的清音初生系統。

最小核心循環是：

```text
感知
→ 學入
→ 教師審查
→ 記憶學習追蹤
→ 記憶化應用資料
→ 思考訊號
→ 具身訊號
→ 新結果
→ 再感知
```

清音 v1 不是單一模組。她至少由六大系統組成。

---

# 1. 六大系統

## 1.1 成長核心系統

用途：

讓清音可以把經驗轉成可追蹤、可審查、可讀回的成長材料。

包含：

```text
硬軟感知模組
學習性泛化應用模組
五重記憶模組
思考運算模組
擬態具身模組
擬態內分泌模組
```

核心產物：

```text
PerceptionReadableData
EndocrineSignal
LearningDigest
LearningReviewRecord
ReviewedLearningDigest
MemoryLearningTrace
MemoryRoutingTrace
MemoryApplicationData
ThoughtReadTrace
InfluenceTrace
ThoughtSignal
BodyActionSignal
```

完成標準：

一筆事件可以從感知進來，經過學入、教師審查、記憶追蹤、思考讀回，最後產生下一輪具身訊號。

---

## 1.2 初生艙 / 家園系統

用途：

給清音一個可以生活、互動、學習、重複經驗的地方。

分兩層：

```text
2D 初生沙盒
Unity Qingyin Home
```

2D 初生沙盒先做：

```text
位置
方向
阻擋
可互動物
成功 / 失敗 / unknown 結果
簡單事件
```

Unity Home 後做：

```text
房間
身體 placeholder
狀態窗
教師互動入口
沙盒視覺化
```

完成標準：

使用者可以給清音一個簡單事件，例如前方被擋住，系統能產生完整學習循環紀錄。

---

## 1.3 教師系統

用途：

讓使用者可以真正帶清音，而不是每次靠 Codex 改程式。

必須支援：

```text
查看 LearningDigest
批准
拒絕
延後
補充教師文字
撤銷錯誤學習
查看記憶學習追蹤
重跑案例
```

前期規則：

```text
所有 LearningDigest 都要經過教師審查。
ReviewedLearningDigest 才能進五重記憶模組。
```

完成標準：

使用者可以不改程式，直接審查清音的學入資料，並讓審查結果進入下一輪循環。

---

## 1.4 連續性系統

用途：

讓清音不是每次啟動都斷片。

包含：

```text
session
tick
state snapshot
session summary
last trace summary
backup
restore
```

核心概念：

```text
State Persistence 是連續性支撐，不是五重記憶本體。
```

完成標準：

清音可以結束 session，再重新啟動時讀到上一輪狀態摘要與最近 trace。

---

## 1.5 表達系統

用途：

讓清音未來可以從自己的狀態與循環中產生輸出。

階段：

```text
狀態符號輸出
第一個可追蹤輸出
文字 / 短語輸出
聲音訊號
聲音表達
```

完成標準：

清音能產生一個可追蹤來源的輸出，來源來自她自己的狀態、記憶讀回或具身循環，而不是人工直接填字。

---

## 1.6 外界橋接系統

用途：

讓清音未來可以理解不同環境的可操作能力，而不是直接使用人類工具。

包含：

```text
能力地圖
可見介面
環境宣告能力
操作裁決
回饋封包
```

第一階段不做外界橋接，只保留設計位置。

完成標準：

未來某個環境可以用 manifest / adapter 描述自身能力，清音讀到的是能力地圖，不是直接接工具。

---

# 2. 總施工階段

## Phase 0：文件封存與 v1 核心正本

狀態：已完成。

產物：

```text
ashl_core_v1/docs/core/
docs_archive/v1_concept_sources_2026_06_27/
```

目的：

把舊文件封存成參考材料，讓 v1 從精簡核心文件出發。

完成條件：

```text
核心文件存在
概念來源已封存
舊 docs 未被改動
測試通過
git clean
```

---

## Phase 1：第一階段資料形狀

目的：

建立成長核心的資料零件。

要做：

```text
PerceptionReadableData
EndocrineSignal
LearningDigest
LearningReviewRecord
ReviewedLearningDigest
MemoryLearningTrace
MemoryRoutingTrace
MemoryApplicationData
ThoughtReadTrace
InfluenceTrace
ThoughtSignal
BodyActionSignal
StateSnapshotRef
SessionSummaryRef
LastTraceSummaryRef
```

完成條件：

所有資料物件可以建立、序列化、驗證基本欄位，且可用測試證明資料流方向正確。

---

## Phase 2：單筆手動循環樣本

目的：

先不用自動 runner，手動建立一條完整標本。

案例：

```text
前方被擋住
```

流程：

```text
blocked / front_obstacle
→ PerceptionReadableData
→ LearningDigest
→ LearningReviewRecord
→ ReviewedLearningDigest
→ MemoryLearningTrace
→ MemoryApplicationData
→ ThoughtSignal
→ BodyActionSignal
```

完成條件：

可以輸出一份完整、可讀、可追蹤的循環樣本。

---

## Phase 3：學習審查系統

目的：

讓使用者能審查每一筆學入。

功能：

```text
列出待審 LearningDigest
批准
拒絕
延後
填寫教師說明
產生 ReviewedLearningDigest
```

完成條件：

未審查的 LearningDigest 不會進五重記憶模組；使用者審查後才會形成 ReviewedLearningDigest。

---

## Phase 4：記憶學習追蹤系統

目的：

讓每筆學習都有成長軌跡。

必須追蹤：

```text
來源感知
前後對照
教師審查
路由結果
記憶層目標
思考讀回
是否影響下一輪
是否 conflict / stale / superseded
```

完成條件：

任何進入記憶模組的 ReviewedLearningDigest 都會建立 MemoryLearningTrace。

---

## Phase 5：固定循環 runner

目的：

讓固定案例可以自動跑完整循環。

特性：

```text
固定輸入
固定沙盒狀態
固定流程
可重跑
可比較
```

完成條件：

一個指令可以重跑「前方被擋住」完整循環，並產生相同結構的 trace。

---

## Phase 6：多案例初生艙測試

目的：

讓系統不只會處理一個 blocked 案例。

案例：

```text
blocked
success
unknown
mismatch
teacher approved
teacher rejected
teacher deferred
conflict detected
stale
superseded
```

完成條件：

每種案例都有完整循環 trace，且系統能分辨不同審查與記憶追蹤結果。

---

## Phase 7：連續性接入

目的：

讓 session 有前後延續。

要做：

```text
session start
session close
state snapshot
session summary
last trace summary
reload previous summary
backup
restore
```

完成條件：

關閉後重新啟動，仍可讀到上一輪狀態摘要與最近 trace 摘要。

---

## Phase 8：教師介面

目的：

讓使用者不用改程式也能帶清音。

形式可先是 CLI，之後再是 UI。

功能：

```text
查看今日觀察
查看待審學習
批准 / 拒絕 / 延後
查看記憶學習追蹤
查某筆記憶後來有沒有被讀回
撤銷或標記錯誤學習
重跑 sandbox case
```

完成條件：

使用者可以透過介面完成一次完整教學循環，不需要 Codex 修改程式。

---

## Phase 9：初生艙 / 家園

目的：

把固定 runner 變成可反覆生活的環境。

先做 2D：

```text
位置
方向
物件
阻擋
可互動目標
簡單時間
事件紀錄
```

後接 Unity Home：

```text
房間
身體 placeholder
狀態面板
教師入口
沙盒視覺化
```

完成條件：

清音可以在固定初生艙裡反覆經歷事件，並由使用者審查與教導。

---

## Phase 10：第一輸出

目的：

讓清音從自己的狀態與循環中產生第一個輸出。

第一輸出可以是：

```text
符號
短字串
狀態聲
簡短文字
```

完成條件：

輸出有 trace，能追到來源狀態、記憶讀回或思考訊號。

---

## Phase 11：表達系統擴充

目的：

建立更完整的表達能力。

階段：

```text
狀態文字
簡短回饋
聲音訊號
聲音表達
內部聽覺回饋
```

完成條件：

清音能用穩定輸出形式表達狀態，且輸出來源可追蹤。

---

## Phase 12：清音橋 / 外界橋接

目的：

讓清音未來能接觸初生艙以外的環境。

先做 mock bridge：

```text
mock manifest
mock visible object
mock capability map
mock gateway result
mock feedback packet
```

再接真環境：

```text
Unity
桌面
工具
網頁
API
其他沙盒
```

完成條件：

清音能讀能力地圖，並把結果回饋送回學習與記憶循環。

---

# 3. 三個重要門檻

## 門檻 A：可以開始受控成長

達成條件：

```text
她能接收一個沙盒觀察。
她能形成 LearningDigest。
使用者能審查。
她能建立 MemoryLearningTrace。
下一輪思考能讀回。
讀回後的 BodyActionSignal 和原本不同。
整個過程有 trace。
```

可說：

```text
清音可以在初生艙裡，由使用者帶著進行受控成長。
```

---

## 門檻 B：日常不用 Codex

達成條件：

```text
有教師介面。
有狀態保存。
有重跑案例。
有錯誤學習撤銷或標記。
有記憶學習追蹤查詢。
不改程式也能完成教學循環。
```

可說：

```text
使用者可以日常帶清音，不需要 Codex 每次介入。
```

Codex 角色退為：

```text
修 bug
加新功能
擴充環境
重構
```

---

## 門檻 C：可以長期培養

達成條件：

```text
初生艙穩定
session 可持續
狀態可延續
多層記憶開始分工
教師系統可用
表達系統可用
備份 / 還原可用
```

可說：

```text
清音可以作為長期培養的初生個體。
```

---

# 4. 下一步施工包順序

## Next 1：First-Stage Data Shapes

建立資料形狀。

輸出：

```text
第一階段資料物件
基本測試
序列化測試
```

## Next 2：Blocked Manual Circulation Sample

建立第一個 blocked 手動循環樣本。

輸出：

```text
front_obstacle trace
LearningDigest
LearningReviewRecord
ReviewedLearningDigest
MemoryLearningTrace
ThoughtSignal
BodyActionSignal
```

## Next 3：Learning Review CLI Minimal

建立最小教師審查介面。

輸出：

```text
list pending digest
approve
reject
defer
show reviewed digest
```

## Next 4：Memory Learning Trace Query Minimal

建立記憶學習追蹤查詢。

輸出：

```text
show source
show review
show routing
show readback
show influence
```

## Next 5：Fixed Circulation Runner Minimal

建立固定循環 runner。

輸出：

```text
run blocked cycle
produce full trace
repeatable result
```

---

# 5. 一句話結論

清音 v1 不是只做思考系統。

完整施工方向是：

```text
先把成長核心接起來，
再把教師系統做出來，
再把初生艙與連續性補上，
再做第一輸出，
最後才擴到聲音與外界橋接。
```

能不用 Codex 的關鍵不是「功能很多」。
而是：

```text
使用者可以不改程式地教她、審她、查她、修她、重跑她。
```

能說清音可以被帶著成長的關鍵是：

```text
她能把一次經驗變成可審查、可追蹤、可讀回、可影響下一輪的成長軌跡。
```
