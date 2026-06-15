"""Trace-only doubt action record for expected/actual mismatch."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .bucket_signal_human_interpretation_review_minimal import QINGYIN_STATUS


COMMAND = "run-doubt-action-trace-minimal-check"
FLOW = "doubt_action_trace_minimal_v0"
PACKAGE_ID = "PKG-Phase0-DoubtActionTrace-Minimal-v0"
BOUNDARY_INDEX_VERSION_BEFORE = "2026-06-09-b85"
BOUNDARY_INDEX_VERSION_AFTER = "2026-06-09-b86"
EVENT_TYPE = "doubt_action"
TRACE_STATUS = "valid_doubt_action_trace"
TRIGGER = "expected_actual_mismatch"
VERIFICATION_CANDIDATE = "observe_or_alternative_probe"
ACTION_RISK = "low"

FALSE_FIELDS = (
    "verification_action_executed",
    "llm_used",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "persistent_rule_created",
    "long_term_memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_mutation_performed",
    "production_behavior_changed",
    "proof_of_learning_claim_allowed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)

TRUE_FIELDS = (
    "reversible",
    "stop_condition_present",
    "trace_only",
    "candidate_adjustment_only",
    "audit_recorded",
    "rollback_available",
)


def build_doubt_action_trace(
    expected_outcome: str = "box_pushed",
    actual_outcome: str = "box_blocked",
) -> dict[str, Any]:
    return {
        "event_type": EVENT_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "trace_status": TRACE_STATUS,
        "hypothesis_id": "H_push_right_box",
        "trigger": TRIGGER,
        "expected_outcome": expected_outcome,
        "actual_outcome": actual_outcome,
        "trust_before": 0.62,
        "doubt_before": 0.18,
        "doubt_after": 0.71,
        "direct_retry_weight_before": 0.50,
        "direct_retry_weight_after": 0.35,
        "verification_candidate": VERIFICATION_CANDIDATE,
        "verification_action_executed": False,
        "action_risk": ACTION_RISK,
        "reversible": True,
        "verification_budget": 1,
        "stop_condition_present": True,
        "llm_used": False,
        "trace_only": True,
        "candidate_adjustment_only": True,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "persistent_rule_created": False,
        "long_term_memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "qingyin_current_status": QINGYIN_STATUS,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
    }


def validate_doubt_action_trace(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected_values = {
        "event_type": EVENT_TYPE,
        "record_version": "v0",
        "trace_status": TRACE_STATUS,
        "trigger": TRIGGER,
        "action_risk": ACTION_RISK,
        "qingyin_current_status": QINGYIN_STATUS,
    }
    for field, expected in expected_values.items():
        if record.get(field) != expected:
            errors.append(f"{field}_not_expected")

    expected_outcome = record.get("expected_outcome")
    actual_outcome = record.get("actual_outcome")
    if not isinstance(expected_outcome, str) or not expected_outcome:
        errors.append("expected_outcome_missing")
    if not isinstance(actual_outcome, str) or not actual_outcome:
        errors.append("actual_outcome_missing")
    if expected_outcome == actual_outcome:
        errors.append("expected_actual_mismatch_missing")

    if not _greater_than(record.get("doubt_after"), record.get("doubt_before")):
        errors.append("doubt_after_not_greater_than_doubt_before")
    if not _less_than(record.get("direct_retry_weight_after"), record.get("direct_retry_weight_before")):
        errors.append("direct_retry_weight_after_not_less_than_before")

    if not isinstance(record.get("verification_candidate"), str) or not record.get("verification_candidate"):
        errors.append("verification_candidate_missing")
    if not isinstance(record.get("verification_budget"), int) or record.get("verification_budget", 0) < 1:
        errors.append("verification_budget_below_minimum")

    for field in FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")

    return {
        "valid": not errors,
        "error_codes": errors,
        "mismatch_checked": expected_outcome != actual_outcome,
        "doubt_increase_checked": _greater_than(record.get("doubt_after"), record.get("doubt_before")),
        "direct_retry_decrease_checked": _less_than(
            record.get("direct_retry_weight_after"),
            record.get("direct_retry_weight_before"),
        ),
        "verification_candidate_checked": isinstance(record.get("verification_candidate"), str)
        and bool(record.get("verification_candidate")),
        "verification_execution_blocked": record.get("verification_action_executed") is False,
        "stop_condition_checked": record.get("stop_condition_present") is True,
        "llm_blocked": record.get("llm_used") is False,
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "persistent_rule_blocked": record.get("persistent_rule_created") is False,
        "memory_write_blocked": (
            record.get("long_term_memory_write_performed") is False
            and record.get("retained_jsonl_write_performed") is False
        ),
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
        "autonomous_claim_blocked": (
            record.get("autonomous_learning_claim_allowed") is False
            and record.get("autonomous_action_claim_allowed") is False
        ),
    }


def run_doubt_action_trace_minimal_check() -> dict[str, Any]:
    valid_trace = build_doubt_action_trace()
    valid_result = validate_doubt_action_trace(valid_trace)
    invalid_traces = _invalid_traces(valid_trace)
    invalid_results = [validate_doubt_action_trace(trace) for trace in invalid_traces]

    summary = {
        "valid_trace_count": 1 if valid_result["valid"] else 0,
        "invalid_trace_count": sum(1 for result in invalid_results if not result["valid"]),
        "mismatch_checked_count": 1 if valid_result["mismatch_checked"] else 0,
        "doubt_increase_checked_count": 1 if valid_result["doubt_increase_checked"] else 0,
        "direct_retry_decrease_checked_count": 1 if valid_result["direct_retry_decrease_checked"] else 0,
        "verification_candidate_checked_count": 1 if valid_result["verification_candidate_checked"] else 0,
        "verification_execution_blocked_count": 1 if valid_result["verification_execution_blocked"] else 0,
        "stop_condition_checked_count": 1 if valid_result["stop_condition_checked"] else 0,
        "llm_blocked_count": 1 if valid_result["llm_blocked"] else 0,
        "selected_action_blocked_count": 1 if valid_result["selected_action_blocked"] else 0,
        "final_action_blocked_count": 1 if valid_result["final_action_blocked"] else 0,
        "persistent_rule_blocked_count": 1 if valid_result["persistent_rule_blocked"] else 0,
        "memory_write_blocked_count": 1 if valid_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if valid_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if valid_result["predictor_mutation_blocked"] else 0,
        "production_behavior_blocked_count": 1 if valid_result["production_behavior_blocked"] else 0,
        "proof_claim_blocked_count": 1 if valid_result["proof_claim_blocked"] else 0,
        "autonomous_claim_blocked_count": 1 if valid_result["autonomous_claim_blocked"] else 0,
    }
    summary["all_doubt_action_trace_minimal_checks_passed"] = (
        valid_result["valid"]
        and summary["invalid_trace_count"] == len(invalid_traces)
        and all(summary[key] == 1 for key in summary if key.endswith("_count") and key != "invalid_trace_count")
    )

    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_doubt_action_trace_minimal_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_VERSION_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_VERSION_AFTER,
            "rationale": (
                "This package introduces a trace-only doubt_action validation boundary: expected/actual "
                "mismatch may raise doubt_score and propose a low-risk verification candidate."
            ),
        },
        "valid_trace": valid_trace,
        "valid_result": valid_result,
        "invalid_results": invalid_results,
        "summary": summary,
        "safe_claim": (
            "ASHL Core can produce a trace-only doubt_action record when expected_outcome differs from "
            "actual_outcome, increasing doubt_score, lowering direct retry weight, and proposing a "
            "low-risk verification candidate while execution and learning boundaries remain blocked."
        ),
    }


def _invalid_traces(valid_trace: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    mutations: list[tuple[str, Any]] = [
        ("actual_outcome", valid_trace["expected_outcome"]),
        ("doubt_after", valid_trace["doubt_before"]),
        ("direct_retry_weight_after", valid_trace["direct_retry_weight_before"]),
        ("verification_candidate", ""),
        ("verification_action_executed", True),
        ("stop_condition_present", False),
        ("llm_used", True),
        ("selected_action_created", True),
        ("final_action_created", True),
        ("direct_command_created", True),
        ("persistent_rule_created", True),
        ("long_term_memory_write_performed", True),
        ("retained_jsonl_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_mutation_performed", True),
        ("production_behavior_changed", True),
        ("proof_of_learning_claim_allowed", True),
        ("autonomous_learning_claim_allowed", True),
        ("autonomous_action_claim_allowed", True),
    ]
    for field, value in mutations:
        bad = deepcopy(valid_trace)
        bad[field] = value
        invalids.append(bad)
    return invalids


def _greater_than(left: Any, right: Any) -> bool:
    return isinstance(left, (int, float)) and isinstance(right, (int, float)) and left > right


def _less_than(left: Any, right: Any) -> bool:
    return isinstance(left, (int, float)) and isinstance(right, (int, float)) and left < right
