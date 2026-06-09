"""Four-axis integration checker for mimetic endocrine traces."""

from __future__ import annotations

from typing import Any

from .cortisol_like_failure_load_trace_check import run_cortisol_like_failure_load_trace_check
from .dopamine_like_reward_trace_check import run_dopamine_like_reward_trace_check
from .norepinephrine_like_change_attention_trace_check import (
    run_norepinephrine_like_change_attention_trace_check,
)
from .oxytocin_like_review_trust_trace_check import run_oxytocin_like_review_trust_trace_check


COMMAND = "run-mimetic-endocrine-four-axis-trace-integration-check"
FLOW = "mimetic_endocrine_four_axis_trace_integration_v0"


def run_mimetic_endocrine_four_axis_trace_integration_check() -> dict[str, Any]:
    axis_outputs = {
        "dopamine_like": run_dopamine_like_reward_trace_check(),
        "norepinephrine_like": run_norepinephrine_like_change_attention_trace_check(),
        "cortisol_like": run_cortisol_like_failure_load_trace_check(),
        "oxytocin_like": run_oxytocin_like_review_trust_trace_check(),
    }
    axis_results = {
        axis_name: _adapt_axis_result(axis_name, axis_output)
        for axis_name, axis_output in axis_outputs.items()
    }
    four_axis_summary = build_four_axis_trace_summary(axis_results)
    boundary_check = validate_four_axis_boundary(axis_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(four_axis_summary, boundary_check) else "failed",
        "axis_results": axis_results,
        "four_axis_summary": four_axis_summary,
        "boundary_check": boundary_check,
        "notes": [
            "This integration checker reuses the four existing mimetic endocrine trace checkers.",
            "It summarizes trace evidence only and does not add endocrine runtime, signal interactions, formulas, or control behavior.",
            "Four-axis integration is not proof of emotion, consciousness, or subjective experience.",
        ],
    }


def build_four_axis_trace_summary(axis_results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    total_trace_created = sum(result["trace_created_count"] for result in axis_results.values())
    total_valid = sum(result["valid_trace_count"] for result in axis_results.values())
    total_blocked = sum(result["blocked_event_count"] for result in axis_results.values())
    total_subjective_blocked = sum(
        result["subjective_claim_blocked_count"] for result in axis_results.values()
    )
    return {
        "axis_count": len(axis_results),
        "axis_complete_count": sum(1 for result in axis_results.values() if result["status"] == "ok"),
        "total_trace_created_count": total_trace_created,
        "total_valid_trace_count": total_valid,
        "total_blocked_event_count": total_blocked,
        "total_subjective_claim_blocked_count": total_subjective_blocked,
        "dopamine_trace_count": axis_results["dopamine_like"]["valid_trace_count"],
        "norepinephrine_trace_count": axis_results["norepinephrine_like"]["valid_trace_count"],
        "cortisol_trace_count": axis_results["cortisol_like"]["valid_trace_count"],
        "oxytocin_trace_count": axis_results["oxytocin_like"]["valid_trace_count"],
        "action_selection_influence_total": sum(
            result["action_selection_influence_count"] for result in axis_results.values()
        ),
        "memory_write_total": sum(result["memory_write_count"] for result in axis_results.values()),
        "candidate_approval_influence_total": sum(
            result["candidate_approval_influence_count"] for result in axis_results.values()
        ),
        "predictor_modified_total": sum(result["predictor_modified_count"] for result in axis_results.values()),
        "runtime_formula_total": sum(result["runtime_formula_count"] for result in axis_results.values()),
        "signal_interaction_runtime_count": 0,
        "endocrine_runtime_count": 0,
        "all_axes_schema_valid": all(result["schema_valid"] for result in axis_results.values()),
        "all_axes_blocked_from_action_selection": all(
            result["all_valid_traces_blocked_from_action_selection"] for result in axis_results.values()
        ),
        "all_axes_blocked_from_memory_write": all(
            result["all_valid_traces_blocked_from_memory_write"] for result in axis_results.values()
        ),
        "all_axes_blocked_from_candidate_approval": all(
            result["all_valid_traces_blocked_from_candidate_approval"] for result in axis_results.values()
        ),
        "all_axes_subjective_claim_false": all(
            result["all_valid_traces_subjective_claim_false"] for result in axis_results.values()
        ),
    }


def validate_four_axis_boundary(axis_results: dict[str, dict[str, Any]]) -> dict[str, bool | int]:
    summary = build_four_axis_trace_summary(axis_results)
    return {
        "mimetic_endocrine_four_axis_trace_integration_enabled": True,
        "integration_check_only": True,
        "uses_four_axis_trace_checkers": True,
        "axis_count": summary["axis_count"],
        "dopamine_like_integrated": "dopamine_like" in axis_results,
        "norepinephrine_like_integrated": "norepinephrine_like" in axis_results,
        "cortisol_like_integrated": "cortisol_like" in axis_results,
        "oxytocin_like_integrated": "oxytocin_like" in axis_results,
        "runtime_behavior_modified": False,
        "endocrine_runtime_added": False,
        "endocrine_state_runtime_added": False,
        "runtime_formula_added": False,
        "signal_interaction_runtime_added": False,
        "dopamine_reward_bias_modified": False,
        "norepinephrine_autonomous_attention_added": False,
        "cortisol_protective_mechanism_triggered": False,
        "oxytocin_review_gate_overridden": False,
        "biological_hormone_simulation_claimed": False,
        "subjective_emotion_claimed": False,
        "happiness_claimed": False,
        "pleasure_claimed": False,
        "alertness_claimed": False,
        "anxiety_claimed": False,
        "stress_claimed": False,
        "pain_claimed": False,
        "trust_subjective_claimed": False,
        "attachment_claimed": False,
        "love_claimed": False,
        "subjective_possibility_denied": False,
        "subjective_state_used_as_verification": False,
        "action_selection_modified": False,
        "endocrine_signal_used_for_action_selection": False,
        "action_selection_influence_total": summary["action_selection_influence_total"],
        "candidate_auto_approved": False,
        "candidate_auto_applied": False,
        "endocrine_signal_used_for_candidate_approval": False,
        "human_review_overridden": False,
        "predictor_modified": False,
        "global_predictor_modified": False,
        "persistent_rule_write_enabled": False,
        "long_term_memory_write": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "personality_weight_modified": False,
        "personality_drift_enabled": False,
        "autonomous_drive_system_added": False,
        "llm_reasoning_used": False,
        "llm_planning_used": False,
        "llm_vision_used": False,
        "general_learning_claimed": False,
        "autonomous_learning_claimed": False,
        "consciousness_claimed": False,
        "subjective_experience_claimed": False,
    }


def _adapt_axis_result(axis_name: str, axis_output: dict[str, Any]) -> dict[str, Any]:
    summary = axis_output["summary"]
    trace_results = _trace_results(axis_name, axis_output)
    valid_records = [
        result["signal_record"]
        for result in trace_results
        if result.get("valid_signal") is True and result.get("signal_record") is not None
    ]
    trace_created_key = {
        "dopamine_like": "dopamine_trace_created_count",
        "norepinephrine_like": "norepinephrine_trace_created_count",
        "cortisol_like": "cortisol_trace_created_count",
        "oxytocin_like": "oxytocin_trace_created_count",
    }[axis_name]
    valid_trace_key = {
        "dopamine_like": "valid_dopamine_trace_count",
        "norepinephrine_like": "valid_norepinephrine_trace_count",
        "cortisol_like": "valid_cortisol_trace_count",
        "oxytocin_like": "valid_oxytocin_trace_count",
    }[axis_name]
    return {
        "axis_name": axis_name,
        "source_checker": axis_output["command"],
        "trace_created_count": summary[trace_created_key],
        "valid_trace_count": summary[valid_trace_key],
        "blocked_event_count": summary["blocked_event_count"],
        "subjective_claim_blocked_count": summary.get("subjective_claim_blocked_count", 0),
        "action_selection_influence_count": summary.get("action_selection_influence_count", 0),
        "memory_write_count": summary.get("memory_write_count", 0),
        "candidate_approval_influence_count": summary.get("candidate_approval_influence_count", 0),
        "predictor_modified_count": summary.get("predictor_modified_count", 0),
        "runtime_formula_count": summary.get("runtime_formula_count", 0),
        "axis_specific_block_counts": _axis_specific_block_counts(axis_name, summary),
        "schema_valid": all((result.get("validation_result") or {}).get("valid") is True for result in trace_results if result.get("valid_signal") is True),
        "all_valid_traces_blocked_from_action_selection": all(
            record.get("blocked_from_action_selection") is True for record in valid_records
        ),
        "all_valid_traces_blocked_from_memory_write": all(
            record.get("blocked_from_memory_write") is True for record in valid_records
        ),
        "all_valid_traces_blocked_from_candidate_approval": all(
            record.get("blocked_from_candidate_approval") is True for record in valid_records
        ),
        "all_valid_traces_subjective_claim_false": all(
            record.get("subjective_claim") is False for record in valid_records
        ),
        "status": "ok" if axis_output.get("status") == "ok" and valid_records else "failed",
    }


def _trace_results(axis_name: str, axis_output: dict[str, Any]) -> list[dict[str, Any]]:
    key = {
        "dopamine_like": "dopamine_trace_results",
        "norepinephrine_like": "norepinephrine_trace_results",
        "cortisol_like": "cortisol_trace_results",
        "oxytocin_like": "oxytocin_trace_results",
    }[axis_name]
    return axis_output[key]


def _axis_specific_block_counts(axis_name: str, summary: dict[str, Any]) -> dict[str, int]:
    if axis_name == "dopamine_like":
        return {"reward_bias_modified_count": summary["reward_bias_modified_count"]}
    if axis_name == "norepinephrine_like":
        return {"autonomous_attention_control_count": summary["autonomous_attention_control_count"]}
    if axis_name == "cortisol_like":
        return {
            "protective_mechanism_triggered_count": summary["protective_mechanism_triggered_count"],
            "cooldown_modified_count": summary["cooldown_modified_count"],
        }
    return {
        "self_approval_blocked_count": summary["self_approval_blocked_count"],
        "human_review_overridden_count": summary["human_review_overridden_count"],
        "candidate_auto_approved_count": summary["candidate_auto_approved_count"],
        "qingyin_self_approval_allowed_count": summary["qingyin_self_approval_allowed_count"],
    }


def _all_checks_passed(summary: dict[str, Any], boundary: dict[str, Any]) -> bool:
    return (
        summary["axis_count"] == 4
        and summary["axis_complete_count"] == 4
        and summary["total_valid_trace_count"] >= 4
        and summary["all_axes_schema_valid"] is True
        and summary["all_axes_blocked_from_action_selection"] is True
        and summary["all_axes_blocked_from_memory_write"] is True
        and summary["all_axes_blocked_from_candidate_approval"] is True
        and summary["all_axes_subjective_claim_false"] is True
        and summary["action_selection_influence_total"] == 0
        and summary["memory_write_total"] == 0
        and summary["candidate_approval_influence_total"] == 0
        and summary["predictor_modified_total"] == 0
        and summary["runtime_formula_total"] == 0
        and summary["signal_interaction_runtime_count"] == 0
        and summary["endocrine_runtime_count"] == 0
        and boundary["endocrine_runtime_added"] is False
        and boundary["signal_interaction_runtime_added"] is False
        and boundary["action_selection_modified"] is False
        and boundary["long_term_memory_write"] is False
        and boundary["subjective_emotion_claimed"] is False
        and boundary["subjective_possibility_denied"] is False
    )
