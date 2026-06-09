"""Deterministic persistent-candidate eligibility checker."""

from __future__ import annotations

from typing import Any


DEFAULT_THRESHOLDS = {
    "min_similar_context_validation_count": 3,
    "max_recent_failure_count": 0,
    "max_active_conflict_count": 0,
    "min_challenge_count": 1,
    "min_challenge_survival_rate": 1.0,
}


def evaluate_persistent_eligibility(
    record: dict[str, Any],
    thresholds: dict[str, Any] | None = None,
) -> dict[str, Any]:
    thresholds_used = dict(DEFAULT_THRESHOLDS)
    if thresholds:
        thresholds_used.update(thresholds)

    gate_results = _evaluate_gates(record, thresholds_used)
    block_reasons = _block_reasons(gate_results)
    eligible_for_review = not block_reasons
    eligibility_status = (
        "eligible_for_persistent_candidate_review"
        if eligible_for_review
        else _eligibility_status(block_reasons, record)
    )
    return {
        "case_name": record.get("case_name"),
        "candidate_id": record.get("candidate_id"),
        "eligibility_status": eligibility_status,
        "eligible_for_persistent_candidate_review": eligible_for_review,
        "eligible_for_persistent_rule": False,
        "persistent_rule_write_allowed": False,
        "gate_results": gate_results,
        "block_reasons": block_reasons,
        "thresholds_used": thresholds_used,
        "recommended_next_status": _recommended_next_status(eligibility_status),
        "human_persistent_approval_gate_observed": record.get("human_persistent_approval") is True,
    }


def build_demo_persistent_eligibility_cases() -> list[dict[str, Any]]:
    passing = _base_record("eligible_candidate")
    return [
        passing,
        {**_base_record("not_approved_candidate"), "candidate_status": "pending_review"},
        {**_base_record("self_approved_candidate_blocked"), "reviewer_type": "qingyin_self", "qingyin_self_approval": True},
        {**_base_record("temporary_apply_not_verified"), "temporary_apply_verified": False},
        {
            **_base_record("insufficient_similar_context_validation"),
            "similar_context_validation_count": 2,
            "similar_context_validation_pass_count": 2,
        },
        {
            **_base_record("challenge_failed"),
            "challenge_survival_count": 0,
            "challenge_failure_count": 1,
        },
        {**_base_record("recent_failure_blocked"), "recent_failure_count": 1, "recent_failure_severity": "high"},
        {**_base_record("active_conflict_blocked"), "active_conflict_count": 1, "conflict_status": "active"},
        {**_base_record("trace_missing_blocked"), "trace_preserved": False},
        {**_base_record("rollback_missing_blocked"), "rollback_path_exists": False},
    ]


def run_persistent_eligibility_checker_check() -> dict[str, Any]:
    case_results = [
        evaluate_persistent_eligibility(case)
        for case in build_demo_persistent_eligibility_cases()
    ]
    summary = _build_summary(case_results)
    return {
        "command": "run-persistent-eligibility-checker-check",
        "flow": "persistent_eligibility_checker_v0",
        "status": "ok" if summary["all_persistent_eligibility_checker_checks_passed"] else "failed",
        "case_results": case_results,
        "summary": summary,
        "boundary_check": _boundary_check(),
        "notes": [
            "Persistent Eligibility Checker v0 evaluates whether an approved candidate can enter persistent-candidate review.",
            "The checker requires temporary verification, repeated similar-context validation, challenge survival, low recent failure, low active conflict, preserved trace, and rollback path.",
            "It never writes persistent rules, activates persistent rules, modifies global predictors, or modifies action selection.",
        ],
    }


def _evaluate_gates(record: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    challenge_count = int(record.get("challenge_count", 0) or 0)
    challenge_survival_count = int(record.get("challenge_survival_count", 0) or 0)
    challenge_survival_rate = (
        challenge_survival_count / challenge_count
        if challenge_count > 0
        else 0.0
    )
    return {
        "approved_human_candidate": {
            "passed": (
                record.get("candidate_status") == "approved"
                and record.get("reviewer_type") == "human"
                and record.get("qingyin_self_approval") is False
                and record.get("applied") is False
            ),
            "required": {
                "candidate_status": "approved",
                "reviewer_type": "human",
                "qingyin_self_approval": False,
                "applied": False,
            },
        },
        "temporary_apply_verification": {
            "passed": (
                record.get("temporary_apply_verified") is True
                and record.get("temporary_apply_prediction_changed_as_previewed") is True
                and record.get("global_predictor_modified") is False
            ),
            "required": {
                "temporary_apply_verified": True,
                "temporary_apply_prediction_changed_as_previewed": True,
                "global_predictor_modified": False,
            },
        },
        "repeated_similar_context_validation": {
            "passed": (
                record.get("similar_context_validation_count", 0)
                >= thresholds["min_similar_context_validation_count"]
                and record.get("similar_context_validation_fail_count") == 0
                and record.get("similar_context_validation_pass_count")
                == record.get("similar_context_validation_count")
            ),
            "validation_count": record.get("similar_context_validation_count", 0),
            "validation_pass_count": record.get("similar_context_validation_pass_count", 0),
            "validation_fail_count": record.get("similar_context_validation_fail_count", 0),
        },
        "challenge_survival": {
            "passed": (
                challenge_count >= thresholds["min_challenge_count"]
                and record.get("challenge_failure_count") == 0
                and challenge_survival_rate >= thresholds["min_challenge_survival_rate"]
            ),
            "challenge_count": challenge_count,
            "challenge_survival_count": challenge_survival_count,
            "challenge_failure_count": record.get("challenge_failure_count", 0),
            "challenge_survival_rate": challenge_survival_rate,
        },
        "low_recent_failure": {
            "passed": (
                record.get("recent_failure_count", 0) <= thresholds["max_recent_failure_count"]
                and record.get("recent_failure_severity") in {"none", "low", None}
            ),
            "recent_failure_count": record.get("recent_failure_count", 0),
            "recent_failure_severity": record.get("recent_failure_severity"),
        },
        "low_active_conflict": {
            "passed": (
                record.get("active_conflict_count", 0) <= thresholds["max_active_conflict_count"]
                and record.get("conflict_status") in {"none", "resolved", None}
                and record.get("supersede_status") != "superseded"
                and record.get("stale_status") != "stale"
            ),
            "active_conflict_count": record.get("active_conflict_count", 0),
            "conflict_status": record.get("conflict_status"),
            "supersede_status": record.get("supersede_status"),
            "stale_status": record.get("stale_status"),
        },
        "trace_preserved": {
            "passed": record.get("trace_preserved") is True,
        },
        "rollback_path_exists": {
            "passed": record.get("rollback_path_exists") is True,
        },
        "human_persistent_approval": {
            "observed": record.get("human_persistent_approval") is True,
            "consumed_for_persistent_rule_write": False,
            "persistent_rule_write_allowed": False,
        },
    }


def _block_reasons(gate_results: dict[str, Any]) -> list[str]:
    reasons = []
    mapping = {
        "approved_human_candidate": "approved_human_candidate_gate_failed",
        "temporary_apply_verification": "temporary_apply_verification_gate_failed",
        "repeated_similar_context_validation": "repeated_similar_context_validation_gate_failed",
        "challenge_survival": "challenge_survival_gate_failed",
        "low_recent_failure": "low_recent_failure_gate_failed",
        "low_active_conflict": "low_active_conflict_gate_failed",
        "trace_preserved": "trace_preserved_gate_failed",
        "rollback_path_exists": "rollback_path_exists_gate_failed",
    }
    for gate_name, reason in mapping.items():
        if gate_results[gate_name]["passed"] is False:
            reasons.append(reason)
    return reasons


def _eligibility_status(block_reasons: list[str], record: dict[str, Any]) -> str:
    if record.get("qingyin_self_approval") is True or record.get("reviewer_type") == "qingyin_self":
        return "blocked_self_approval"
    if record.get("global_predictor_modified") is True:
        return "blocked_global_predictor_modified"
    first = block_reasons[0] if block_reasons else ""
    mapping = {
        "approved_human_candidate_gate_failed": "blocked_not_approved",
        "temporary_apply_verification_gate_failed": "blocked_temporary_apply_not_verified",
        "repeated_similar_context_validation_gate_failed": "blocked_insufficient_similar_context_validation",
        "challenge_survival_gate_failed": "blocked_challenge_not_survived",
        "low_recent_failure_gate_failed": "blocked_recent_failure",
        "low_active_conflict_gate_failed": "blocked_active_conflict",
        "trace_preserved_gate_failed": "blocked_trace_missing",
        "rollback_path_exists_gate_failed": "blocked_rollback_missing",
    }
    return mapping.get(first, "blocked_unknown")


def _recommended_next_status(eligibility_status: str) -> str:
    if eligibility_status == "eligible_for_persistent_candidate_review":
        return "persistent_candidate"
    if eligibility_status in {"blocked_insufficient_similar_context_validation", "blocked_challenge_not_survived"}:
        return "defer_for_more_validation"
    if eligibility_status in {"blocked_active_conflict", "blocked_recent_failure"}:
        return "reject_or_supersede"
    if eligibility_status in {"blocked_not_approved", "blocked_self_approval"}:
        return "return_to_review"
    return "remain_approved"


def _build_summary(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    gate_pass_counts: dict[str, int] = {}
    for result in case_results:
        status = result["eligibility_status"]
        status_counts[status] = status_counts.get(status, 0) + 1
        for gate_name, gate_result in result["gate_results"].items():
            if gate_result.get("passed") is True:
                gate_pass_counts[gate_name] = gate_pass_counts.get(gate_name, 0) + 1

    return {
        "case_count": len(case_results),
        "eligible_for_persistent_candidate_review_count": sum(
            1 for result in case_results if result["eligible_for_persistent_candidate_review"]
        ),
        "eligible_for_persistent_rule_count": sum(
            1 for result in case_results if result["eligible_for_persistent_rule"]
        ),
        "blocked_count": sum(
            1 for result in case_results if not result["eligible_for_persistent_candidate_review"]
        ),
        "persistent_rule_write_allowed_count": sum(
            1 for result in case_results if result["persistent_rule_write_allowed"]
        ),
        "status_counts": status_counts,
        "gate_pass_counts": gate_pass_counts,
        "all_persistent_eligibility_checker_checks_passed": (
            len(case_results) == 10
            and status_counts.get("eligible_for_persistent_candidate_review") == 1
            and sum(1 for result in case_results if result["eligible_for_persistent_rule"]) == 0
            and sum(1 for result in case_results if result["persistent_rule_write_allowed"]) == 0
            and all(result["block_reasons"] for result in case_results if not result["eligible_for_persistent_candidate_review"])
        ),
    }


def _base_record(case_name: str) -> dict[str, Any]:
    return {
        "case_name": case_name,
        "candidate_id": f"candidate:{case_name}",
        "candidate_status": "approved",
        "reviewer_type": "human",
        "qingyin_self_approval": False,
        "applied": False,
        "temporary_apply_verified": True,
        "temporary_apply_prediction_changed_as_previewed": True,
        "global_predictor_modified": False,
        "similar_context_validation_count": 3,
        "similar_context_validation_pass_count": 3,
        "similar_context_validation_fail_count": 0,
        "challenge_count": 1,
        "challenge_survival_count": 1,
        "challenge_failure_count": 0,
        "recent_failure_count": 0,
        "recent_failure_severity": "none",
        "active_conflict_count": 0,
        "conflict_status": "none",
        "supersede_status": "none",
        "stale_status": "fresh",
        "trace_preserved": True,
        "rollback_path_exists": True,
        "human_persistent_approval": False,
    }


def _boundary_check() -> dict[str, bool]:
    return {
        "persistent_eligibility_checker_enabled": True,
        "checker_only": True,
        "persistent_candidate_review_eligibility_only": True,
        "persistent_rule_write_enabled": False,
        "persistent_rule_storage_added": False,
        "persistent_rule_table_added": False,
        "persistent_rule_active_enabled": False,
        "human_persistent_approval_recorded_only": True,
        "candidate_auto_persistent_enabled": False,
        "candidate_auto_approved": False,
        "qingyin_self_approval_allowed": False,
        "global_predictor_modified": False,
        "action_selection_modified": False,
        "prediction_used_for_action_selection": False,
        "temporary_apply_verification_required": True,
        "repeated_similar_context_validation_required": True,
        "challenge_survival_required": True,
        "low_recent_failure_required": True,
        "low_active_conflict_required": True,
        "trace_required": True,
        "rollback_required": True,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "long_term_memory_write": False,
        "persistent_memory_write": False,
        "lesson_internalization_enabled": False,
        "instinct_like_behavior_enabled": False,
        "pathfinding_used": False,
        "route_planner_added": False,
        "llm_reasoning_used": False,
        "llm_planning_used": False,
        "llm_vision_used": False,
        "general_learning_claimed": False,
        "autonomous_learning_claimed": False,
        "consciousness_claimed": False,
        "subjective_experience_claimed": False,
    }
