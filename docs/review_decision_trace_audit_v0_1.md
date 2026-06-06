# ASHL Core／清音唯一模型：Review Decision Trace Audit v0.1

## 目的

本文審查 v2.8e `review_decision_trace` 的 trace-only schema 邊界。

本文不是 manual_review runtime 規格。

本文不新增 review decision runtime，不寫 `lesson_store`，不建立 approved `lesson_candidate`，不修改 selection / activation / conflict logic。

---

## 一、審查結論

Audit result: PASS.

---

## 二、審查範圍

審查對象：

```text
ashl_core/review_decisions.py
tests/test_review_decisions.py
docs/review_decision_trace_schema_v0_1.md
```

pipeline 範圍：

```text
review_task_trace
→ review_decision_trace
```

---

## 三、已確認邊界

- review_decision_trace is a trace-only historical event record, not a runtime decision engine.
- approved trace is still cold trace, not runtime permission.
- approved trace does not grant lesson_store write permission.
- approved trace does not grant selection eligibility.
- approved trace does not grant activation.
- rejected / deferred traces must not contain reusable proposed content.
- Masked means not reusable as lesson content.
- masked_fields_summary contains field names only.
- rejected / deferred traces require masking_policy_ref.
- all review_decision_trace outputs require authority_binding_policy_ref.
- partial / conditional approval is rejected.
- review_task completion is not review_decision creation.
- review_task completion alone cannot create review_decision_trace.

---

## 四、Absolute Masking Invariant

If decision_status is rejected or deferred, reusable proposed content must not appear in output.

If approved_payload or equivalent exists, it must be None for rejected / deferred traces.

If no approved_payload field exists, the equivalent invariant is:

```text
rejected / deferred traces must not contain reusable proposed content.
```

---

## 五、Future Trace Isolation Guard

Future runtime selector must not read review_decision_trace as decision input.

review_decision_trace path must not appear in runtime query paths.

review_decision_trace must remain cold trace data for future runtime selectors.

This package does not implement runtime selector checks because runtime selector does not exist yet.

---

## 六、Future Triple-Binding Runtime Check

Future runtime decision creation must validate decision_authority / reviewer_identity / reviewer_session_token binding.

Binding must not rely on free-text claims or weak string-prefix checks.

This package does not implement auth / session runtime.

---

## 七、目前不可宣稱

目前不可宣稱：

- review_decision_trace is runtime decision engine
- approved trace grants lesson_store write permission
- approved trace grants selection eligibility
- rejected / deferred trace preserves proposed content
- masked_fields_summary may include proposed content
- runtime selector can read review_decision_trace
- identity/session binding runtime exists
- review_task completion creates review_decision_trace
