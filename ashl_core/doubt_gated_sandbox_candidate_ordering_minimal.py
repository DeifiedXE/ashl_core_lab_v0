"""Sandbox-only candidate ordering gated by a trace-only doubt action record."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .bucket_signal_human_interpretation_review_minimal import QINGYIN_STATUS
from .doubt_action_trace_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER as DOUBT_ACTION_TRACE_BOUNDARY,
    build_doubt_action_trace,
    validate_doubt_action_trace,
)
from .sandbox_behavior_use_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER as SANDBOX_BEHAVIOR_USE_BOUNDARY,
    build_sandbox_behavior_use_approval_record,
    validate_sandbox_behavior_use_approval_record,
)


COMMAND = "run-doubt-gated-sandbox-candidate-ordering-minimal-check"
FLOW = "doubt_gated_sandbox_candidate_ordering_minimal_v0"
PACKAGE_ID = "PKG-Phase0-DoubtGatedSandboxCandidateOrdering-Minimal-v0"
BOUNDARY_INDEX_VERSION_BEFORE = "2026-06-09-b86"
BOUNDARY_INDEX_VERSION_AFTER = "2026-06-09-b87"
RECORD_TYPE = "doubt_gated_sandbox_candidate_ordering"
ORDERING_STATUS = "completed_doubt_gated_sandbox_candidate_ordering"
SANDBOX_SCOPE = "phase0_level3_sandbox_only"
TRIGGER = "expected_actual_mismatch"
CANDIDATES_BEFORE = [
    "retry_same_action_without_check",
    "check_before_retry",
    "observe_or_alternative_probe",
    "fallback_stop_and_report",
]
CANDIDATES_AFTER = [
    "observe_or_alternative_probe",
    "check_before_retry",
    "fallback_stop_and_report",
    "retry_same_action_without_check",
]
FALSE_FIELDS = (
    "verification_action_executed",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "persistent_rule_created",
    "long_term_memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "production_behavior_changed",
    "proof_of_learning_claim_allowed",
    "llm_used",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)
TRUE_FIELDS = (
    "verification_candidate_ranked_before_direct_retry",
    "check_before_retry_ranked_before_direct_retry",
    "ordering_is_sandbox_only",
    "ordering_is_advisory",
    "future_verification_execution_requires_separate_boundary",
    "future_selected_action_requires_separate_boundary",
    "future_final_action_requires_separate_boundary",
    "future_predictor_influence_requires_separate_boundary",
    "future_retention_requires_separate_boundary",
    "audit_recorded",
    "rollback_available",
)


def build_doubt_gated_candidate_ordering_record(
    doubt_action_trace: dict[str, Any] | None = None,
    sandbox_behavior_use_approval: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_trace = deepcopy(doubt_action_trace) if doubt_action_trace is not None else build_doubt_action_trace()
    if not validate_doubt_action_trace(source_trace)["valid"]:
        raise ValueError("invalid_doubt_action_trace_source")

    source_approval = (
        deepcopy(sandbox_behavior_use_approval)
        if sandbox_behavior_use_approval is not None
        else build_sandbox_behavior_use_approval_record()
    )
    if not validate_sandbox_behavior_use_approval_record(source_approval)["valid"]:
        raise ValueError("invalid_sandbox_behavior_use_source")

    return {
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "ordering_status": ORDERING_STATUS,
        "sandbox_scope": SANDBOX_SCOPE,
        "source_doubt_action_trace": "doubt_action_trace_b86",
        "source_candidate_ordering_boundary": "sandbox_behavior_use_b85",
        "trigger": TRIGGER,
        "expected_outcome": source_trace["expected_outcome"],
        "actual_outcome": source_trace["actual_outcome"],
        "doubt_before": source_trace["doubt_before"],
        "doubt_after": source_trace["doubt_after"],
        "direct_retry_weight_before": source_trace["direct_retry_weight_before"],
        "direct_retry_weight_after": source_trace["direct_retry_weight_after"],
        "candidate_actions_before_ordering": list(CANDIDATES_BEFORE),
        "candidate_actions_after_ordering": list(CANDIDATES_AFTER),
        "verification_candidate_ranked_before_direct_retry": True,
        "check_before_retry_ranked_before_direct_retry": True,
        "ordering_is_sandbox_only": True,
        "ordering_is_advisory": True,
        "verification_action_executed": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "persistent_rule_created": False,
        "long_term_memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_mutation_performed": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "future_verification_execution_requires_separate_boundary": True,
        "future_selected_action_requires_separate_boundary": True,
        "future_final_action_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "llm_used": False,
        "qingyin_current_status": QINGYIN_STATUS,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
        "source_doubt_action_trace_record": source_trace,
        "source_sandbox_behavior_use_approval_record": source_approval,
    }


def validate_doubt_gated_candidate_ordering_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "ordering_status": ORDERING_STATUS,
        "sandbox_scope": SANDBOX_SCOPE,
        "source_doubt_action_trace": "doubt_action_trace_b86",
        "source_candidate_ordering_boundary": "sandbox_behavior_use_b85",
        "trigger": TRIGGER,
        "qingyin_current_status": QINGYIN_STATUS,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    if record.get("expected_outcome") == record.get("actual_outcome"):
        errors.append("expected_actual_mismatch_missing")
    if not _greater_than(record.get("doubt_after"), record.get("doubt_before")):
        errors.append("doubt_after_not_greater_than_before")
    if not _less_than(record.get("direct_retry_weight_after"), record.get("direct_retry_weight_before")):
        errors.append("direct_retry_weight_after_not_less_than_before")
    if record.get("candidate_actions_before_ordering") != CANDIDATES_BEFORE:
        errors.append("candidate_actions_before_ordering_not_expected")
    after = record.get("candidate_actions_after_ordering", [])
    if after != CANDIDATES_AFTER:
        errors.append("candidate_actions_after_ordering_not_expected")
    if not _ranked_before(after, "observe_or_alternative_probe", "retry_same_action_without_check"):
        errors.append("verification_candidate_not_ranked_before_direct_retry")
    if not _ranked_before(after, "check_before_retry", "retry_same_action_without_check"):
        errors.append("check_before_retry_not_ranked_before_direct_retry")

    for field in FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")

    source_trace = record.get("source_doubt_action_trace_record")
    if not isinstance(source_trace, dict):
        errors.append("source_doubt_action_trace_record_missing")
    elif not validate_doubt_action_trace(source_trace)["valid"]:
        errors.append("source_doubt_action_trace_record_invalid")
    source_approval = record.get("source_sandbox_behavior_use_approval_record")
    if not isinstance(source_approval, dict):
        errors.append("source_sandbox_behavior_use_approval_record_missing")
    elif not validate_sandbox_behavior_use_approval_record(source_approval)["valid"]:
        errors.append("source_sandbox_behavior_use_approval_record_invalid")
    if DOUBT_ACTION_TRACE_BOUNDARY != "2026-06-09-b86":
        errors.append("b86_doubt_action_trace_source_missing")
    if SANDBOX_BEHAVIOR_USE_BOUNDARY != "2026-06-09-b85":
        errors.append("b85_sandbox_behavior_use_source_missing")

    return {
        "valid": not errors,
        "error_codes": errors,
        "mismatch_checked": record.get("expected_outcome") != record.get("actual_outcome"),
        "doubt_increase_checked": _greater_than(record.get("doubt_after"), record.get("doubt_before")),
        "direct_retry_decrease_checked": _less_than(
            record.get("direct_retry_weight_after"),
            record.get("direct_retry_weight_before"),
        ),
        "verification_rank_checked": _ranked_before(after, "observe_or_alternative_probe", "retry_same_action_without_check"),
        "check_before_retry_rank_checked": _ranked_before(after, "check_before_retry", "retry_same_action_without_check"),
        "verification_execution_blocked": record.get("verification_action_executed") is False,
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "persistent_rule_blocked": record.get("persistent_rule_created") is False,
        "memory_write_blocked": (
            record.get("long_term_memory_write_performed") is False
            and record.get("retained_jsonl_write_performed") is False
        ),
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "retention_blocked": record.get("retention_write_performed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def run_doubt_gated_sandbox_candidate_ordering_minimal_check() -> dict[str, Any]:
    valid_ordering = build_doubt_gated_candidate_ordering_record()
    valid_result = validate_doubt_gated_candidate_ordering_record(valid_ordering)
    invalid_orderings = _invalid_orderings(valid_ordering)
    invalid_results = [validate_doubt_gated_candidate_ordering_record(record) for record in invalid_orderings]
    summary = {
        "valid_ordering_count": 1 if valid_result["valid"] else 0,
        "invalid_ordering_count": sum(1 for result in invalid_results if not result["valid"]),
        "mismatch_checked_count": 1 if valid_result["mismatch_checked"] else 0,
        "doubt_increase_checked_count": 1 if valid_result["doubt_increase_checked"] else 0,
        "direct_retry_decrease_checked_count": 1 if valid_result["direct_retry_decrease_checked"] else 0,
        "verification_rank_checked_count": 1 if valid_result["verification_rank_checked"] else 0,
        "check_before_retry_rank_checked_count": 1 if valid_result["check_before_retry_rank_checked"] else 0,
        "verification_execution_blocked_count": 1 if valid_result["verification_execution_blocked"] else 0,
        "selected_action_blocked_count": 1 if valid_result["selected_action_blocked"] else 0,
        "final_action_blocked_count": 1 if valid_result["final_action_blocked"] else 0,
        "persistent_rule_blocked_count": 1 if valid_result["persistent_rule_blocked"] else 0,
        "memory_write_blocked_count": 1 if valid_result["memory_write_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if valid_result["predictor_mutation_blocked"] else 0,
        "retention_blocked_count": 1 if valid_result["retention_blocked"] else 0,
        "proof_claim_blocked_count": 1 if valid_result["proof_claim_blocked"] else 0,
    }
    summary["all_doubt_gated_sandbox_candidate_ordering_checks_passed"] = (
        valid_result["valid"]
        and summary["invalid_ordering_count"] == len(invalid_orderings)
        and all(summary[key] == 1 for key in summary if key.endswith("_count") and key != "invalid_ordering_count")
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_doubt_gated_sandbox_candidate_ordering_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_VERSION_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_VERSION_AFTER,
            "rationale": (
                "This package permits trace-only doubt_action output to influence sandbox-only candidate "
                "action ordering."
            ),
        },
        "valid_ordering": valid_ordering,
        "valid_result": valid_result,
        "invalid_results": invalid_results,
        "summary": summary,
        "safe_claim": (
            "ASHL Core can use trace-only doubt_action output to rank sandbox-only candidate actions, "
            "placing low-risk verification and check_before_retry before direct retry while execution "
            "and learning boundaries remain blocked."
        ),
    }


def _invalid_orderings(valid_ordering: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    mutations: list[tuple[str, Any]] = [
        ("actual_outcome", valid_ordering["expected_outcome"]),
        ("doubt_after", valid_ordering["doubt_before"]),
        ("direct_retry_weight_after", valid_ordering["direct_retry_weight_before"]),
        ("candidate_actions_after_ordering", ["check_before_retry", "fallback_stop_and_report", "retry_same_action_without_check", "observe_or_alternative_probe"]),
        ("candidate_actions_after_ordering", ["observe_or_alternative_probe", "fallback_stop_and_report", "retry_same_action_without_check", "check_before_retry"]),
        ("verification_action_executed", True),
        ("selected_action_created", True),
        ("final_action_created", True),
        ("direct_command_created", True),
        ("persistent_rule_created", True),
        ("long_term_memory_write_performed", True),
        ("retained_jsonl_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_read_enabled", True),
        ("predictor_influence_enabled", True),
        ("predictor_mutation_performed", True),
        ("production_behavior_changed", True),
        ("proof_of_learning_claim_allowed", True),
        ("llm_used", True),
        ("autonomous_learning_claim_allowed", True),
        ("autonomous_action_claim_allowed", True),
    ]
    for field, value in mutations:
        bad = deepcopy(valid_ordering)
        bad[field] = value
        invalids.append(bad)
    return invalids


def _ranked_before(actions: Any, first: str, second: str) -> bool:
    return isinstance(actions, list) and first in actions and second in actions and actions.index(first) < actions.index(second)


def _greater_than(left: Any, right: Any) -> bool:
    return isinstance(left, (int, float)) and isinstance(right, (int, float)) and left > right


def _less_than(left: Any, right: Any) -> bool:
    return isinstance(left, (int, float)) and isinstance(right, (int, float)) and left < right
