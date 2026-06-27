# ASHL Core v1 學入、審查、記憶追蹤流程

## 核心原則

第一階段的學習不是直接寫記憶。它是一條可追蹤流程：從觀察資料形成學習草稿，經人類教師審查後，才交給五重記憶模組建立記憶學習追蹤。

## 主流程

```text
PerceptionReadableData
+ EndocrineSignal
+ before_state
+ event_or_action
+ after_state
+ source_trace
→ LearningDigest
→ LearningReviewRecord
→ ReviewedLearningDigest
→ MemoryLearningTrace
→ MemoryRoutingTrace
→ MemoryApplicationData
→ ThoughtReadTrace
→ InfluenceTrace
```

## LearningDigest

`LearningDigest` 是學習草稿。它保存「這次發生了什麼、前後差異是什麼、來源在哪裡、狀態調控如何參與」。

必要欄位：

```text
learning_digest_id
source_perception_refs
source_endocrine_refs
before_state_ref
event_or_action_ref
after_state_ref
expected_actual_contrast
source_trace_refs
uncertainty
generalization_scope
review_required
```

## LearningReviewRecord

第一階段所有 `LearningDigest` 都進人類教師審查。

審查紀錄至少保存：

```text
review_record_id
source_learning_digest_id
reviewer_ref
review_status
review_comment
approved_scope
allowed_memory_route
needs_more_evidence_reason
conflict_note
```

`review_status` 建議值：

```text
approved_for_working_memory
approved_same_context_only
approved_limited_generalization
needs_more_evidence
rejected
conflict_detected
```

## ReviewedLearningDigest

`ReviewedLearningDigest` 是審查後的學習資料。只有它能交給五重記憶模組。

必要欄位：

```text
reviewed_digest_id
source_learning_digest_id
source_review_record_id
approved_scope
allowed_memory_route
source_trace_refs
reviewed_content
```

## MemoryLearningTrace

`MemoryLearningTrace` 記錄一筆審查後學習資料如何進入記憶系統。

它要追蹤：

```text
memory_learning_trace_id
source_reviewed_digest_id
source_review_record_id
source_perception_refs
source_endocrine_refs
before_state_ref
after_state_ref
memory_route
routing_reason
state_snapshot_ref
session_summary_ref
last_trace_summary_ref
later_read_refs
later_influence_refs
stale_status
supersede_ref
rollback_ref
```

## State Persistence 的角色

State Persistence 是連續性支撐，不是五重記憶本體。它提供學習追蹤用的地標：

```text
state_snapshot_ref
session_summary_ref
last_trace_summary_ref
```

這些參照讓系統知道一筆學習發生在哪個狀態、哪個 session 摘要、哪條 trace 之後。

## 記憶讀回與後續影響

當思考運算模組讀取 `MemoryApplicationData` 時，應建立 `ThoughtReadTrace`。

若讀回資料影響下一輪思考、具身訊號或觀察，應建立 `InfluenceTrace`。

這讓成長軌跡可回看：哪筆學入後來被讀了、怎麼被用、是否需要修正。

## 失效與修正

一筆學習資料後續可能出現：

```text
needs_more_evidence
conflict_detected
stale
superseded
rollback_required
```

這些狀態不應藏在註解裡，應成為記憶學習追蹤的一部分。
