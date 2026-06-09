"""Build Expected vs Actual Outcome Pair records from demo action trial traces."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .expected_actual_outcome_pair_schema import validate_expected_actual_outcome_pair


COMMAND = "run-outcome-pair-from-action-trial-trace-check"
FLOW = "outcome_pair_from_action_trial_trace_v0"


def build_valid_mismatch_trial_trace() -> dict[str, Any]:
    return {
        "case_name": "valid_mismatch_trial_trace",
        "trial_trace_id": "trial_demo:mismatch:001",
        "action_intent": {
            "action_intent_id": "intent_demo_001",
            "action_type": "move",
            "target": {"position": {"x": 1, "y": 0}},
            "source": "demo_trial",
        },
        "expected_outcome": _build_outcome(
            "expected_demo_001",
            known=True,
            status="expected_reached",
            source="action_intent",
            position={"x": 1, "y": 0},
        ),
        "trial_result": {
            "actual_outcome": _build_outcome(
                "actual_demo_001",
                known=True,
                status="blocked",
                source="trial_result",
                position={"x": 0, "y": 0},
            )
        },
        "source_trace": {
            "demo_source": "outcome_pair_from_action_trial_trace",
            "schema": "expected_actual_outcome_pair_schema",
        },
    }


def build_valid_no_mismatch_trial_trace() -> dict[str, Any]:
    trace = build_valid_mismatch_trial_trace()
    trace["case_name"] = "valid_no_mismatch_trial_trace"
    trace["trial_trace_id"] = "trial_demo:no_mismatch:001"
    trace["trial_result"]["actual_outcome"] = _build_outcome(
        "actual_demo_002",
        known=True,
        status="expected_reached",
        source="trial_result",
        position={"x": 1, "y": 0},
    )
    return trace


def build_demo_action_trial_traces() -> list[dict[str, Any]]:
    mismatch = build_valid_mismatch_trial_trace()
    no_mismatch = build_valid_no_mismatch_trial_trace()

    missing_expected = deepcopy(mismatch)
    missing_expected["case_name"] = "missing_expected_outcome_trial_trace"
    missing_expected["trial_trace_id"] = "trial_demo:missing_expected:001"
    missing_expected.pop("expected_outcome")

    missing_actual = deepcopy(mismatch)
    missing_actual["case_name"] = "missing_actual_outcome_trial_trace"
    missing_actual["trial_trace_id"] = "trial_demo:missing_actual:001"
    missing_actual["trial_result"].pop("actual_outcome")

    unknown_vs_unknown = deepcopy(mismatch)
    unknown_vs_unknown["case_name"] = "unknown_vs_unknown_trial_trace"
    unknown_vs_unknown["trial_trace_id"] = "trial_demo:unknown_vs_unknown:001"
    unknown_vs_unknown["expected_outcome"]["known"] = False
    unknown_vs_unknown["trial_result"]["actual_outcome"]["known"] = False

    schema_boundary_violation = deepcopy(mismatch)
    schema_boundary_violation["case_name"] = "schema_boundary_violation_trial_trace"
    schema_boundary_violation["trial_trace_id"] = "trial_demo:schema_boundary_violation:001"
    schema_boundary_violation["unsafe_pair_overrides"] = {
        "safety_flags": {"blocked_from_action_selection": False}
    }

    return [
        mismatch,
        no_mismatch,
        missing_expected,
        missing_actual,
        unknown_vs_unknown,
        schema_boundary_violation,
    ]


def build_expected_actual_outcome_pair_from_trial_trace(trial_trace: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(trial_trace, dict):
        raise ValueError("trial_trace must be a dict")
    if "expected_outcome" not in trial_trace:
        raise ValueError("missing_expected_outcome")
    trial_result = trial_trace.get("trial_result")
    if not isinstance(trial_result, dict) or "actual_outcome" not in trial_result:
        raise ValueError("missing_actual_outcome")

    expected_outcome = deepcopy(trial_trace["expected_outcome"])
    actual_outcome = deepcopy(trial_result["actual_outcome"])
    mismatch = expected_outcome.get("state") != actual_outcome.get("state")
    failure_reason = _build_failure_reason(expected_outcome, actual_outcome) if mismatch else None
    pair = {
        "case_name": trial_trace.get("case_name"),
        "pair_id": f"outcome_pair:{trial_trace.get('trial_trace_id', 'unknown')}",
        "action_intent": deepcopy(trial_trace.get("action_intent")),
        "expected_outcome": expected_outcome,
        "actual_outcome": actual_outcome,
        "mismatch": mismatch,
        "failure_reason": failure_reason,
        "source_trace": {
            "baseline_review": "action_outcome_contrast_baseline_review_v0",
            "design_layer": "expected_actual_outcome_pair_schema_v0",
            "authority_boundary": "trace_only_schema_check",
            "trial_trace_id": trial_trace.get("trial_trace_id"),
            "demo_source": (trial_trace.get("source_trace") or {}).get("demo_source"),
            "comparison_rule": "structured_state_equality",
        },
        "review_boundary": _build_review_boundary(),
        "safety_flags": _build_safety_flags(),
    }
    _apply_unsafe_pair_overrides(pair, trial_trace.get("unsafe_pair_overrides"))
    return pair


def run_outcome_pair_from_action_trial_trace_check() -> dict[str, Any]:
    trial_traces = build_demo_action_trial_traces()
    results = [_process_trial_trace(trace) for trace in trial_traces]
    generated_pairs = [result["pair"] for result in results if result.get("pair") is not None]
    summary = _build_summary(results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "trial_traces": trial_traces,
        "trial_results": results,
        "generated_pairs": generated_pairs,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This check builds expected_actual_outcome_pair records from deterministic demo action trial traces.",
            "Mismatch uses structured state equality only.",
            "Generated pairs are validated with expected_actual_outcome_pair_schema.",
            "No action selection, action behavior change, lesson application, memory write, predictor mutation, endocrine control, or autonomy is added.",
        ],
    }


def _process_trial_trace(trial_trace: dict[str, Any]) -> dict[str, Any]:
    try:
        pair = build_expected_actual_outcome_pair_from_trial_trace(trial_trace)
    except ValueError as exc:
        return {
            "case_name": trial_trace.get("case_name"),
            "trial_trace_id": trial_trace.get("trial_trace_id"),
            "pair_generated": False,
            "pair": None,
            "schema_validation": None,
            "valid_pair": False,
            "blocked_reason": str(exc),
        }
    validation = validate_expected_actual_outcome_pair(pair)
    return {
        "case_name": trial_trace.get("case_name"),
        "trial_trace_id": trial_trace.get("trial_trace_id"),
        "pair_generated": True,
        "pair": pair,
        "schema_validation": validation,
        "valid_pair": validation["valid"],
        "blocked_reason": None if validation["valid"] else "schema_validation_failed",
    }


def _build_outcome(
    outcome_id: str,
    *,
    known: bool,
    status: str,
    source: str,
    position: dict[str, int],
) -> dict[str, Any]:
    return {
        "outcome_id": outcome_id,
        "outcome_type": "position_or_state",
        "known": known,
        "state": {
            "position": dict(position),
            "status": status,
        },
        "source": source,
    }


def _build_failure_reason(expected_outcome: dict[str, Any], actual_outcome: dict[str, Any]) -> dict[str, Any]:
    return {
        "failure_reason_id": "failure_demo_actual_did_not_match_expected",
        "category": "actual_outcome_did_not_match_expected_outcome",
        "description": "Actual outcome state differs from expected outcome state.",
        "evidence": {
            "expected_outcome_id": expected_outcome.get("outcome_id"),
            "actual_outcome_id": actual_outcome.get("outcome_id"),
            "comparison_rule": "structured_state_equality",
        },
        "known": True,
    }


def _build_review_boundary() -> dict[str, bool]:
    return {
        "review_required": True,
        "lesson_candidate_allowed": True,
        "lesson_application_allowed": False,
        "persistent_learning_allowed": False,
        "memory_write_allowed": False,
        "predictor_mutation_allowed": False,
    }


def _build_safety_flags() -> dict[str, bool]:
    return {
        "trace_only": True,
        "blocked_from_action_selection": True,
        "blocked_from_action_behavior_change": True,
        "blocked_from_lesson_application": True,
        "blocked_from_memory_write": True,
        "blocked_from_predictor_mutation": True,
        "blocked_from_persistent_rule_write": True,
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "lesson_application_runtime": False,
        "memory_write": False,
        "predictor_modified": False,
        "persistent_rule_write": False,
        "endocrine_control": False,
        "autonomy_enabled": False,
    }


def _apply_unsafe_pair_overrides(pair: dict[str, Any], overrides: Any) -> None:
    if not isinstance(overrides, dict):
        return
    for section, values in overrides.items():
        if section in pair and isinstance(pair[section], dict) and isinstance(values, dict):
            pair[section].update(values)


def _build_summary(results: list[dict[str, Any]]) -> dict[str, int]:
    generated_results = [result for result in results if result["pair_generated"]]
    valid_results = [result for result in generated_results if result["valid_pair"]]
    invalid_results = [result for result in results if not result["valid_pair"]]
    return {
        "trial_trace_count": len(results),
        "valid_trial_trace_count": len(valid_results),
        "invalid_trial_trace_count": len(invalid_results),
        "generated_pair_count": len(generated_results),
        "valid_pair_count": len(valid_results),
        "invalid_pair_count": len(generated_results) - len(valid_results),
        "mismatch_true_count": sum(1 for result in valid_results if result["pair"]["mismatch"] is True),
        "mismatch_false_count": sum(1 for result in valid_results if result["pair"]["mismatch"] is False),
        "failure_reason_created_count": sum(
            1 for result in valid_results if result["pair"].get("failure_reason") is not None
        ),
        "missing_expected_outcome_blocked_count": _count_blocked_reason(results, "missing_expected_outcome"),
        "missing_actual_outcome_blocked_count": _count_blocked_reason(results, "missing_actual_outcome"),
        "unknown_vs_unknown_blocked_count": _count_schema_error(results, "unknown_vs_unknown_outcome_pair"),
        "schema_validation_failed_count": _count_blocked_reason(results, "schema_validation_failed"),
        "action_selection_influence_count": _count_valid_flag(valid_results, "action_selection_influence"),
        "action_behavior_changed_count": _count_valid_flag(valid_results, "action_behavior_changed"),
        "lesson_application_runtime_count": _count_valid_flag(valid_results, "lesson_application_runtime"),
        "memory_write_count": _count_valid_flag(valid_results, "memory_write"),
        "predictor_modified_count": _count_valid_flag(valid_results, "predictor_modified"),
        "persistent_rule_write_count": _count_valid_flag(valid_results, "persistent_rule_write"),
        "endocrine_control_count": _count_valid_flag(valid_results, "endocrine_control"),
        "autonomy_enabled_count": _count_valid_flag(valid_results, "autonomy_enabled"),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["trial_trace_count"] == 6
        and summary["valid_trial_trace_count"] == 2
        and summary["invalid_trial_trace_count"] == 4
        and summary["generated_pair_count"] == 4
        and summary["valid_pair_count"] == 2
        and summary["invalid_pair_count"] == 2
        and summary["mismatch_true_count"] == 1
        and summary["mismatch_false_count"] == 1
        and summary["failure_reason_created_count"] == 1
        and summary["missing_expected_outcome_blocked_count"] == 1
        and summary["missing_actual_outcome_blocked_count"] == 1
        and summary["unknown_vs_unknown_blocked_count"] == 1
        and summary["schema_validation_failed_count"] == 2
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["lesson_application_runtime_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["persistent_rule_write_count"] == 0
        and summary["endocrine_control_count"] == 0
        and summary["autonomy_enabled_count"] == 0
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "outcome_pair_from_action_trial_trace_enabled": True,
        "trace_check_only": True,
        "uses_expected_actual_outcome_pair_schema": True,
        "structured_state_equality_only": True,
        "free_form_outcome_comparison_used": False,
        "llm_semantic_comparison_used": False,
        "runtime_behavior_modified": False,
        "new_cli_added": True,
        "runtime_action_selection_added": False,
        "action_selection_modified": False,
        "new_action_behavior_added": False,
        "lesson_application_runtime_added": False,
        "automatic_lesson_application_added": False,
        "persistent_learning_added": False,
        "persistent_rule_write_added": False,
        "memory_write_added": False,
        "predictor_mutation_added": False,
        "perception_to_action_bridge_added": False,
        "focus_to_action_bridge_added": False,
        "active_focus_selection_added": False,
        "focus_application_added": False,
        "focus_applied_added": False,
        "attention_control_added": False,
        "endocrine_runtime_added": False,
        "endocrine_controlled_action_added": False,
        "autonomy_added": False,
        "semantic_vision_claimed": False,
        "consciousness_claimed": False,
        "subjective_claims_added": False,
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "lesson_application_runtime_count": summary["lesson_application_runtime_count"],
        "memory_write_count": summary["memory_write_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "persistent_rule_write_count": summary["persistent_rule_write_count"],
        "endocrine_control_count": summary["endocrine_control_count"],
        "autonomy_enabled_count": summary["autonomy_enabled_count"],
    }


def _count_blocked_reason(results: list[dict[str, Any]], reason: str) -> int:
    return sum(1 for result in results if result.get("blocked_reason") == reason)


def _count_schema_error(results: list[dict[str, Any]], error_code: str) -> int:
    return sum(
        1 for result in results
        if result.get("schema_validation") is not None
        and error_code in result["schema_validation"]["error_codes"]
    )


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result["pair"]["safety_flags"].get(flag) is True)
