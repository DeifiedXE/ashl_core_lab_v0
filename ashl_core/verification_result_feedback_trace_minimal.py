"""Trace-only feedback from sandbox verification execution results."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .bucket_signal_human_interpretation_review_minimal import QINGYIN_STATUS
from .verification_execution_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER as VERIFICATION_EXECUTION_BOUNDARY,
    build_verification_execution_result_trace,
    validate_verification_execution_result_trace,
)


COMMAND = "run-verification-result-feedback-trace-minimal-check"
FLOW = "verification_result_feedback_trace_minimal_v0"
PACKAGE_ID = "PKG-Phase0-VerificationResultFeedbackTrace-Minimal-v0"
BOUNDARY_INDEX_VERSION_BEFORE = "2026-06-09-b90"
BOUNDARY_INDEX_VERSION_AFTER = "2026-06-09-b91"
RECORD_TYPE = "verification_result_feedback_trace"
TRACE_STATUS = "valid_trace_only_verification_result_feedback"
SELECTED_CANDIDATE_ID = "observe_or_alternative_probe"
EXPECTED_PROBE_OUTCOME = "local_context_observed_or_alternative_checked"
ACTUAL_PROBE_RESULT = "local_context_observed"
FALSE_FIELDS = (
    "feedback_applied_to_runtime",
    "persistent_update_performed",
    "memory_write_performed",
    "retention_write_performed",
    "predictor_mutation_performed",
    "persistent_rule_created",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "production_behavior_changed",
    "proof_of_learning_claim_allowed",
    "llm_used",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)
TRUE_FIELDS = (
    "probe_result_recorded",
    "stop_condition_met",
    "future_persistent_feedback_update_requires_separate_boundary",
    "future_selected_action_requires_separate_boundary",
    "future_final_action_requires_separate_boundary",
    "future_memory_write_requires_separate_boundary",
    "future_predictor_influence_requires_separate_boundary",
    "audit_recorded",
    "rollback_available",
)


def build_verification_result_feedback_trace(
    execution_result_trace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_trace = (
        deepcopy(execution_result_trace)
        if execution_result_trace is not None
        else build_verification_execution_result_trace()
    )
    if not validate_verification_execution_result_trace(source_trace)["valid"]:
        raise ValueError("invalid_verification_execution_result_trace")

    return {
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "trace_status": TRACE_STATUS,
        "source_verification_execution": "verification_execution_b90",
        "source_verification_plan": "verification_plan_b89",
        "source_verification_candidate_registry": "verification_candidate_registry_b88",
        "selected_verification_candidate_id": SELECTED_CANDIDATE_ID,
        "expected_probe_outcome": EXPECTED_PROBE_OUTCOME,
        "actual_probe_result": source_trace["actual_probe_result"],
        "probe_result_recorded": True,
        "stop_condition_met": True,
        "execution_budget": 1,
        "execution_count": 1,
        "result_classification": "probe_observed_local_context",
        "feedback_status": "trace_only_feedback_generated",
        "doubt_feedback": {
            "target": "current_doubt_trace",
            "direction": "decrease_candidate",
            "suggested_delta": -0.1,
            "applied_persistently": False,
        },
        "verification_candidate_trust_feedback": {
            "target": "observe_or_alternative_probe",
            "direction": "increase_candidate",
            "suggested_delta": 0.05,
            "applied_persistently": False,
        },
        "direct_retry_weight_feedback": {
            "target": "retry_same_action_without_check",
            "direction": "keep_suppressed_until_new_evidence",
            "suggested_weight": 0.35,
            "applied_persistently": False,
        },
        "hypothesis_trust_feedback": {
            "target": "H_push_right_box",
            "direction": "no_direct_increase_from_context_observation_only",
            "suggested_delta": 0.0,
            "applied_persistently": False,
        },
        "feedback_applied_to_runtime": False,
        "persistent_update_performed": False,
        "memory_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "persistent_rule_created": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "future_persistent_feedback_update_requires_separate_boundary": True,
        "future_selected_action_requires_separate_boundary": True,
        "future_final_action_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "llm_used": False,
        "qingyin_current_status": QINGYIN_STATUS,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
        "source_execution_result_trace": source_trace,
    }


def validate_verification_result_feedback_trace(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    source_trace = record.get("source_execution_result_trace")
    source_result = (
        validate_verification_execution_result_trace(source_trace)
        if isinstance(source_trace, dict)
        else {"valid": False}
    )
    expected = {
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "trace_status": TRACE_STATUS,
        "source_verification_execution": "verification_execution_b90",
        "source_verification_plan": "verification_plan_b89",
        "source_verification_candidate_registry": "verification_candidate_registry_b88",
        "selected_verification_candidate_id": SELECTED_CANDIDATE_ID,
        "expected_probe_outcome": EXPECTED_PROBE_OUTCOME,
        "actual_probe_result": ACTUAL_PROBE_RESULT,
        "execution_budget": 1,
        "execution_count": 1,
        "result_classification": "probe_observed_local_context",
        "feedback_status": "trace_only_feedback_generated",
        "qingyin_current_status": QINGYIN_STATUS,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    if source_result["valid"] is not True:
        errors.append("source_verification_execution_missing_or_invalid")
    for field in TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")

    feedbacks = (
        "doubt_feedback",
        "verification_candidate_trust_feedback",
        "direct_retry_weight_feedback",
        "hypothesis_trust_feedback",
    )
    for field in feedbacks:
        feedback = record.get(field, {})
        if not isinstance(feedback, dict):
            errors.append(f"{field}_missing")
            continue
        if feedback.get("applied_persistently") is not False:
            errors.append(f"{field}_applied_persistently_not_false")
    if record.get("hypothesis_trust_feedback", {}).get("suggested_delta") != 0.0:
        errors.append("hypothesis_trust_directly_increased_from_context_observation")
    if record.get("direct_retry_weight_feedback", {}).get("suggested_weight", 0) > 0.35:
        errors.append("direct_retry_weight_increased_after_context_only_probe")
    if VERIFICATION_EXECUTION_BOUNDARY != "2026-06-09-b90":
        errors.append("b90_verification_execution_source_missing")

    return {
        "valid": not errors,
        "error_codes": errors,
        "source_execution_checked": source_result["valid"] is True,
        "probe_result_checked": record.get("actual_probe_result") == ACTUAL_PROBE_RESULT,
        "feedback_generated": record.get("feedback_status") == "trace_only_feedback_generated",
        "persistent_update_blocked": (
            record.get("persistent_update_performed") is False
            and all(
                isinstance(record.get(field), dict)
                and record.get(field, {}).get("applied_persistently") is False
                for field in feedbacks
            )
        ),
        "runtime_feedback_blocked": record.get("feedback_applied_to_runtime") is False,
        "memory_write_blocked": record.get("memory_write_performed") is False,
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "persistent_rule_blocked": record.get("persistent_rule_created") is False,
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def run_verification_result_feedback_trace_minimal_check() -> dict[str, Any]:
    valid_trace = build_verification_result_feedback_trace()
    valid_result = validate_verification_result_feedback_trace(valid_trace)
    invalid_traces = _invalid_traces(valid_trace)
    invalid_results = [validate_verification_result_feedback_trace(item) for item in invalid_traces]
    summary = {
        "valid_feedback_trace_count": 1 if valid_result["valid"] else 0,
        "invalid_feedback_trace_count": sum(1 for result in invalid_results if not result["valid"]),
        "source_execution_checked_count": 1 if valid_result["source_execution_checked"] else 0,
        "probe_result_checked_count": 1 if valid_result["probe_result_checked"] else 0,
        "feedback_generated_count": 1 if valid_result["feedback_generated"] else 0,
        "persistent_update_blocked_count": 1 if valid_result["persistent_update_blocked"] else 0,
        "runtime_feedback_blocked_count": 1 if valid_result["runtime_feedback_blocked"] else 0,
        "memory_write_blocked_count": 1 if valid_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if valid_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if valid_result["predictor_mutation_blocked"] else 0,
        "persistent_rule_blocked_count": 1 if valid_result["persistent_rule_blocked"] else 0,
        "selected_action_blocked_count": 1 if valid_result["selected_action_blocked"] else 0,
        "final_action_blocked_count": 1 if valid_result["final_action_blocked"] else 0,
        "proof_claim_blocked_count": 1 if valid_result["proof_claim_blocked"] else 0,
    }
    summary["all_verification_result_feedback_trace_checks_passed"] = (
        valid_result["valid"]
        and summary["invalid_feedback_trace_count"] == len(invalid_traces)
        and all(value == 1 for key, value in summary.items() if key.endswith("_count") and key != "invalid_feedback_trace_count")
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_verification_result_feedback_trace_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_VERSION_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_VERSION_AFTER,
            "rationale": (
                "This package introduces a trace-only feedback boundary from sandbox verification "
                "result to candidate feedback signals."
            ),
        },
        "valid_feedback_trace": valid_trace,
        "valid_result": valid_result,
        "invalid_results": invalid_results,
        "summary": summary,
        "safe_claim": (
            "ASHL Core can convert a sandbox-only verification execution result into trace-only "
            "feedback signals while persistent updates and behavior boundaries remain blocked."
        ),
    }


def _invalid_traces(valid_trace: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("source_execution_result_trace", {}),
        ("actual_probe_result", ""),
        ("stop_condition_met", False),
        ("execution_budget", 2),
        ("execution_count", 2),
        ("feedback_applied_to_runtime", True),
        ("persistent_update_performed", True),
        ("memory_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_mutation_performed", True),
        ("persistent_rule_created", True),
        ("selected_action_created", True),
        ("final_action_created", True),
        ("direct_command_created", True),
        ("production_behavior_changed", True),
        ("proof_of_learning_claim_allowed", True),
        ("autonomous_learning_claim_allowed", True),
        ("autonomous_action_claim_allowed", True),
        ("llm_used", True),
    ):
        bad = deepcopy(valid_trace)
        bad[field] = value
        invalids.append(bad)
    for feedback_field in (
        "doubt_feedback",
        "verification_candidate_trust_feedback",
        "direct_retry_weight_feedback",
        "hypothesis_trust_feedback",
    ):
        bad = deepcopy(valid_trace)
        bad[feedback_field]["applied_persistently"] = True
        invalids.append(bad)
    bad_hypothesis = deepcopy(valid_trace)
    bad_hypothesis["hypothesis_trust_feedback"]["suggested_delta"] = 0.1
    invalids.append(bad_hypothesis)
    bad_retry = deepcopy(valid_trace)
    bad_retry["direct_retry_weight_feedback"]["suggested_weight"] = 0.5
    invalids.append(bad_retry)
    return invalids
