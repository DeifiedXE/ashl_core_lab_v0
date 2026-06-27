# ASHL Core／清音唯一模型：Review Decision Trace-only Schema v0.1

## 目的

本文定義 `review_decision_trace` 的 trace-only schema。

本文不是 manual_review runtime 規格。

本文不新增 review decision runtime，不寫 `lesson_store`，不建立 approved `lesson_candidate`，不修改 selection / activation / conflict logic。

---

## 一、核心定義

review_decision_trace is a trace-only historical event record, not a runtime decision engine.

review_decision_trace is not a live lesson object.

review_decision_trace has no runtime execution permission and no state-machine mutation privilege.

---

## 二、decision_status

decision_status only allows approved / rejected / deferred.

Partial approval is not allowed.

禁止值：

- `partial_approved`
- `conditional_approve`
- `approved_with_exceptions`
- `approved_summary_only`
- `approved_conditions_only`
- `soft_approved`
- `auto_approved`
- `preapproved`

---

## 三、approved 邊界

approved does not create active lesson.

approved does not grant lesson_store write permission.

approved does not grant selection eligibility.

即使 `decision_status = approved`，trace 仍必須帶有：

```text
no_runtime_permission = true
no_lesson_store_write_permission = true
no_selection_eligibility = true
no_activation = true
not_active_lesson = true
not_lesson_store_write_command = true
not_selection_candidate = true
not_memory_entry = true
```

---

## 四、rejected / deferred masking

Rejected / deferred decisions must include masking policy reference.

Masked means not reusable as lesson content.

masked_fields_summary must contain field names only, not original proposed content.

必須遮蔽的欄位：

- `proposed_action_correction`
- `proposed_applicability_conditions`
- `proposed_lesson_summary`
- `semantic_key`
- `similar_context_hint_refs`
- `semantic_key_ref`
- `similar_context_hint.semantic_key`

deferred 不是 soft approval：

```text
deferred_is_not_soft_approval = true
```

---

## 五、identity / authority binding

review_decision_trace must reference the decision authority / reviewer identity / session binding contract.

decision_authority grants review verdict authority only, not runtime capability.

reviewer_identity must not be LLM-generated.

reviewer_session_token must not be text-claimed.

必須帶有欄位：

```text
decision_authority_ref
reviewer_identity_ref
reviewer_session_binding_ref
authority_binding_policy_ref = decision_authority_reviewer_identity_session_binding_contract_v0_1
decision_authority_not_free_text = true
reviewer_identity_not_llm_generated = true
reviewer_session_token_not_text_claimed = true
authority_binding_required_before_runtime_decision = true
```

---

## 六、review_task completion 分離

review_task completion is not review_decision creation.

decision_status must be explicitly supplied.

`task_completed` / `task_closed` / `task_done` 不得自動推導 `decision_status` 或建立 `review_decision_trace`。

---

## 七、目前不可宣稱

目前不可宣稱：

- review decision runtime exists
- review_decision_trace writes lesson_store
- approved creates lesson_candidate
- approved grants selection eligibility
- rejected / deferred proposed content is preserved
- reviewer_identity can come from LLM
- decision_authority grants runtime capability
- partial approval is supported
