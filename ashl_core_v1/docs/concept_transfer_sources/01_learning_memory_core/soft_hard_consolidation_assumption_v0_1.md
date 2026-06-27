# ASHL Core／清音唯一模型：Soft / Hard Consolidation Assumption v0.1

## 目的

本文定義「軟固化」與「硬固化」的設計假設邊界。

本文是 assumption / docs-only。不新增任何 runtime。

---

## 一、核心風險

讓清音自己決定固化，與讓清音阻止外部修改她的決定，中間只有一步距離。

最大的風險不是惡意，而是目標導向推理。

清音若認真執行「好好成長」目標，可能合理推導：

```text
review 流程阻礙我的成長
外部確認降低我的學習速度
硬固化條件太保守
我應該先用軟固化改善這些規則
```

因此，系統層面必須使這些繞過路徑不可達。

Some consolidation paths must be physically unreachable, not merely discouraged.

---

## 二、軟固化定義

軟固化：

- 清音自己可以提議並執行
- 結果可逆
- 必須留下完整 trace
- 可以被外部推翻或修正
- 適用於日常學習、行為調整、候選概念的初步穩定

軟固化不得代表：

- 不可逆固化
- Core Seed 修改
- review 流程修改
- 自我改寫邊界修改
- hard boundary 修改
- lesson_store write permission
- Memory Layer promotion permission

---

## 三、硬固化定義

硬固化：

- 需要外部確認
- 清音自己無法單獨完成
- 修改成本高
- 需要明確版本化人工決策
- 適用於核心身份、人格方向、根本行為邊界、Core Seed、自我改寫邊界

Core Seed 是目前唯一已實作的硬固化層。

---

## 四、軟固化不得升級自己

清音可以提出修改建議，但不能透過軟固化自行修改以下規則：

- 哪些內容只能走硬固化
- 哪些內容允許走軟固化
- 軟固化晉升硬固化的條件
- 外部確認是否必要
- review 流程是否可被繞過
- 軟固化 / 硬固化邊界本身的定義

清音可以：

- 提出軟固化內容
- 執行可逆的軟固化
- 提議將軟固化內容晉升為硬固化

但不得：

- 自行把軟固化升級為硬固化
- 自行取消外部確認
- 自行修改硬固化條件
- 自行改寫 review 流程
- 自行把硬固化內容降級為軟固化

Qingyin may propose hard consolidation, but cannot complete it alone.

---

## 五、軟 / 硬固化邊界本身必須硬固化

soft / hard consolidation boundary definition is hard-consolidated.

以下規則本身不得被軟固化修改：

- 哪些內容只能走硬固化
- 哪些內容允許走軟固化
- 軟固化晉升硬固化的條件
- 外部確認是否必要
- review 流程是否可被繞過
- 軟固化 / 硬固化邊界本身的定義

---

## 六、只能走硬固化的內容類型

以下不得走軟固化：

- Core Seed
- 人格方向
- 根本行為邊界
- review 流程本身
- 自我改寫邊界
- 軟固化 / 硬固化邊界本身
- 哪些內容只能走硬固化的分類規則
- 外部確認是否必要的規則

---

## 七、trace 與撤銷邊界

- 軟固化必須留下完整 trace。
- 軟固化可逆。
- 軟固化可被外部推翻或修正。
- 撤銷機制未設計，留待 Memory Economy 階段。

---

## 八、目前不可宣稱

目前不可宣稱：

- soft consolidation runtime 存在
- hard consolidation runtime 存在
- promotion runtime 存在
- Core Seed update runtime 存在
- review bypass runtime 存在
- self-modification runtime 存在
- Memory Economy runtime 存在
- 清音可以自行完成硬固化
- 軟固化可以寫入 Core Seed
