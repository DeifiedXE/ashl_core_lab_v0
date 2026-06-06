# ASHL Core/D清音：Lesson Candidate Builder Literature References v0.1

## 目的

本文補充 lesson_candidate builder 未來實作階段的文獻參考。

本文是 reference-only 文件，不是 runtime 規格。

本文不新增 lesson_candidate builder runtime，不新增 proposed_action_correction runtime，不修改現有 docs-only / trace-only 邊界。

---

## 一、CausalFlow

### Reference

CausalFlow: Causal Attribution and Counterfactual Repair for LLM Agent Failures
arXiv:2605.25338
Date: 2026-05-25

### Design relevance

CausalFlow supports the ASHL Core principle that failure_reason must not be an arbitrary failed step.

Only a step whose counterfactual intervention flips the final outcome should be treated as a causal failure reason candidate.

Corresponding ASHL Core principle:

failure_reason must be grounded in expected_outcome vs actual_outcome evidence.

Future direction:

expected_outcome vs actual_outcome
→ counterfactual intervention
→ outcome-flipping step
→ causal failure_reason candidate

### Counterfactual Repair relevance

CausalFlow counterfactual repair provides a future reference for proposed_action_correction generation.

Future proposed_action_correction should be grounded in which change would flip the outcome,
not in LLM free-form repair suggestion.

Corresponding ASHL Core principle:

proposed_action_correction should be supported by causal / counterfactual evidence, not LLM free-form repair suggestion.

### Boundary

This reference does not add Causal Responsibility Score runtime, counterfactual repair runtime, lesson_candidate builder runtime, or proposed_action_correction runtime.

---

## 二、LaGEA

### Reference

LaGEA: Language Guided Embodied Agents for Robotic Manipulation
arXiv:2509.23155
Date: 2025-09-27

### Structured feedback mapping

LaGEA's structured feedback schema can be used as a comparison reference for future ASHL Core failure_event / lesson_candidate builder fields:

outcome → mismatch
primary_error.code → failure_reason_id
primary_error.explanation → failure_type
suggested_fix → proposed_action_correction
confidence → evaluator_confidence
key_frame_indices → actual_outcome source trace

This mapping is a reference only and does not imply direct schema adoption.

### Negative reference

LaGEA uses VLM-generated suggested_fix.

ASHL Core explicitly does not allow LLM / VLM generated suggested_fix to become authoritative proposed_action_correction.

ASHL Core principles:

proposed_action_correction must be review-gated.

LLM / VLM may provide non-authoritative hints or wording, but must not directly author authoritative correction fields.

proposed_action_correction must not be directly authored as authoritative by LLM / VLM.

### Boundary

This reference does not add VLM feedback runtime, suggested_fix runtime, lesson_candidate builder runtime, or proposed_action_correction runtime.

---

## 三、目前不可宣稱

目前不可宣稱：

- Causal Responsibility Score runtime exists
- counterfactual repair runtime exists
- lesson_candidate builder runtime exists
- proposed_action_correction runtime exists
- VLM suggested_fix can directly become proposed_action_correction
- LLM / VLM can author authoritative failure_reason
- LLM / VLM can author approved correction