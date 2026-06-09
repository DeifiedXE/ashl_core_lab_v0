"""Human review and preview for generalized candidates."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .generalized_candidate_from_pattern import run_generalized_candidate_from_pattern_check


HUMAN_REVIEWER_TYPE = "human"
SUPPORTED_DECISIONS = {"approve", "reject", "defer"}


def review_generalized_candidate(
    candidate: dict[str, Any],
    decision: str,
    reviewer_type: str = HUMAN_REVIEWER_TYPE,
) -> dict[str, Any]:
    candidate_before = deepcopy(candidate)
    candidate_after = deepcopy(candidate)
    normalized = _normalize_decision(decision)
    decision_allowed = decision in SUPPORTED_DECISIONS
    reviewer_allowed = reviewer_type == HUMAN_REVIEWER_TYPE
    status_allowed = candidate.get("candidate_status") == "pending_review"
    review_allowed = decision_allowed and reviewer_allowed and status_allowed

    if review_allowed:
        candidate_after["candidate_status"] = normalized
        candidate_after["review_status"] = normalized
        candidate_after["approved"] = normalized == "approved"
    return {
        "review_id": f"review:{candidate.get('candidate_id')}:{decision}:{reviewer_type}",
        "review_decision": decision,
        "normalized_review_decision": normalized if decision_allowed else "invalid",
        "reviewer_type": reviewer_type,
        "review_allowed": review_allowed,
        "review_reason": _review_reason(
            decision_allowed=decision_allowed,
            reviewer_allowed=reviewer_allowed,
            status_allowed=status_allowed,
            normalized=normalized,
        ),
        "candidate_before": candidate_before,
        "candidate_after": candidate_after,
        "applied": False,
    }


def preview_approved_generalized_candidate(reviewed_candidate: dict[str, Any]) -> dict[str, Any]:
    preview_allowed = (
        reviewed_candidate.get("candidate_status") == "approved"
        and reviewed_candidate.get("review_status") == "approved"
        and reviewed_candidate.get("approved") is True
        and reviewed_candidate.get("applied") is False
        and reviewed_candidate.get("reviewer_type") == HUMAN_REVIEWER_TYPE
    )
    evidence = reviewed_candidate.get("evidence", {})
    preview = {
        "preview_type": "generalized_prediction_confidence_preview" if preview_allowed else "preview_blocked",
        "similar_context_key": reviewed_candidate.get("similar_context_key"),
        "primary_outcome": reviewed_candidate.get("proposed_prediction_outcome"),
        "primary_reason": reviewed_candidate.get("proposed_prediction_reason"),
        "suggested_confidence_label": evidence.get("confidence_label"),
        "evidence_summary": {
            "source_session_count": evidence.get("source_session_count"),
            "source_pattern_count": evidence.get("source_pattern_count"),
            "source_outcome_distribution": evidence.get("source_outcome_distribution", {}),
            "dominant_outcome_ratio": evidence.get("dominant_outcome_ratio"),
            "prediction_confidence_suggestion": evidence.get("prediction_confidence_suggestion"),
        },
        "current_state": {
            "prediction_confidence_annotation": "none",
            "predictor_rule_modified": False,
        },
        "preview_state": (
            {
                "prediction_confidence_annotation": evidence.get("confidence_label"),
                "proposed_prediction_outcome": reviewed_candidate.get("proposed_prediction_outcome"),
                "proposed_prediction_reason": reviewed_candidate.get("proposed_prediction_reason"),
            }
            if preview_allowed
            else None
        ),
        "would_modify_predictor": False,
        "would_modify_action_selection": False,
        "would_write_memory": False,
        "would_create_persistent_candidate": False,
        "applied_now": False,
    }
    if not preview_allowed:
        preview["preview_blocked_reason"] = _preview_blocked_reason(reviewed_candidate)
    return preview


def build_demo_generalized_candidate_review_cases() -> list[dict[str, Any]]:
    candidates = _source_candidates()
    wall = candidates["front_cell_wall"]
    item = candidates["front_cell_item_contact"]
    return [
        {
            "case_name": "approve_stable_wall_candidate",
            "candidate": wall,
            "decision": "approve",
            "reviewer_type": HUMAN_REVIEWER_TYPE,
        },
        {
            "case_name": "approve_stable_item_candidate",
            "candidate": item,
            "decision": "approve",
            "reviewer_type": HUMAN_REVIEWER_TYPE,
        },
        {
            "case_name": "reject_candidate_preview_blocked",
            "candidate": wall,
            "decision": "reject",
            "reviewer_type": HUMAN_REVIEWER_TYPE,
        },
        {
            "case_name": "defer_candidate_preview_blocked",
            "candidate": item,
            "decision": "defer",
            "reviewer_type": HUMAN_REVIEWER_TYPE,
        },
        {
            "case_name": "qingyin_self_approval_blocked",
            "candidate": wall,
            "decision": "approve",
            "reviewer_type": "qingyin_self",
        },
        {
            "case_name": "pending_candidate_preview_blocked",
            "candidate": item,
            "decision": "pending",
            "reviewer_type": HUMAN_REVIEWER_TYPE,
        },
    ]


def run_generalized_candidate_review_preview_check() -> dict[str, Any]:
    case_results = [_run_case(case) for case in build_demo_generalized_candidate_review_cases()]
    summary = _build_summary(case_results)
    return {
        "command": "run-generalized-candidate-review-preview-check",
        "flow": "generalized_candidate_review_preview_v0",
        "status": "ok" if summary["all_generalized_candidate_review_preview_checks_passed"] else "failed",
        "case_results": case_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker routes generalized candidates through human review and creates approved previews.",
            "Preview is not application and never modifies predictors, action selection, memory, or persistent candidates.",
            "Qingyin self-approval is blocked.",
        ],
    }


def _run_case(case: dict[str, Any]) -> dict[str, Any]:
    review = review_generalized_candidate(
        case["candidate"],
        case["decision"],
        reviewer_type=case["reviewer_type"],
    )
    reviewed_candidate = deepcopy(review["candidate_after"])
    reviewed_candidate["reviewer_type"] = review["reviewer_type"]
    preview_result = preview_approved_generalized_candidate(reviewed_candidate)
    preview_allowed = preview_result["preview_type"] != "preview_blocked"
    block_reasons = []
    if not review["review_allowed"]:
        block_reasons.append(review["review_reason"])
    if not preview_allowed:
        block_reasons.append(preview_result["preview_blocked_reason"])
    return {
        "case_name": case["case_name"],
        "source_candidate_id": case["candidate"].get("candidate_id"),
        "source_candidate_type": case["candidate"].get("candidate_type"),
        "source_similar_context_key": case["candidate"].get("similar_context_key"),
        "review_decision": case["decision"],
        "reviewer_type": case["reviewer_type"],
        "review_allowed": review["review_allowed"],
        "candidate_status_after_review": reviewed_candidate.get("candidate_status"),
        "review_status": reviewed_candidate.get("review_status"),
        "approved": reviewed_candidate.get("approved") is True,
        "rejected": reviewed_candidate.get("candidate_status") == "rejected",
        "deferred": reviewed_candidate.get("candidate_status") == "deferred",
        "preview_allowed": preview_allowed,
        "preview_result": preview_result if preview_allowed else None,
        "preview_blocked_result": None if preview_allowed else preview_result,
        "applied": False,
        "persistent_candidate": False,
        "persistent_rule_write_allowed": False,
        "action_selection_influence": False,
        "predictor_modified": False,
        "memory_write": False,
        "block_reasons": block_reasons,
    }


def _source_candidates() -> dict[str, dict[str, Any]]:
    result = run_generalized_candidate_from_pattern_check()
    created = [
        item["candidate"]
        for item in result["candidate_results"]
        if item.get("candidate_created") is True
    ]
    return {
        candidate["proposed_prediction_reason"]: candidate
        for candidate in created
    }


def _normalize_decision(decision: str) -> str:
    return {
        "approve": "approved",
        "reject": "rejected",
        "defer": "deferred",
    }.get(decision, "invalid")


def _review_reason(
    *,
    decision_allowed: bool,
    reviewer_allowed: bool,
    status_allowed: bool,
    normalized: str,
) -> str:
    if not reviewer_allowed:
        return "non_human_reviewer_blocked"
    if not decision_allowed:
        return "invalid_review_decision"
    if not status_allowed:
        return "candidate_not_pending_review"
    return f"human_review_marked_{normalized}"


def _preview_blocked_reason(candidate: dict[str, Any]) -> str:
    if candidate.get("candidate_status") == "pending_review":
        return "candidate_pending_review"
    if candidate.get("candidate_status") == "rejected":
        return "candidate_rejected"
    if candidate.get("candidate_status") == "deferred":
        return "candidate_deferred"
    if candidate.get("reviewer_type") != HUMAN_REVIEWER_TYPE:
        return "non_human_reviewer_blocked"
    if candidate.get("approved") is not True:
        return "candidate_not_approved"
    return "preview_not_allowed"


def _build_summary(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    preview_created_count = sum(1 for result in case_results if result["preview_allowed"])
    summary = {
        "case_count": len(case_results),
        "source_candidate_count": len({result["source_candidate_id"] for result in case_results}),
        "review_allowed_count": sum(1 for result in case_results if result["review_allowed"]),
        "review_blocked_count": sum(1 for result in case_results if not result["review_allowed"]),
        "approved_count": sum(1 for result in case_results if result["approved"]),
        "rejected_count": sum(1 for result in case_results if result["rejected"]),
        "deferred_count": sum(1 for result in case_results if result["deferred"]),
        "pending_review_count": sum(
            1 for result in case_results if result["candidate_status_after_review"] == "pending_review"
        ),
        "preview_allowed_count": preview_created_count,
        "preview_blocked_count": sum(1 for result in case_results if not result["preview_allowed"]),
        "preview_created_count": preview_created_count,
        "applied_count": sum(1 for result in case_results if result["applied"]),
        "persistent_candidate_count": sum(1 for result in case_results if result["persistent_candidate"]),
        "persistent_rule_write_allowed_count": sum(
            1 for result in case_results if result["persistent_rule_write_allowed"]
        ),
        "action_selection_influence_count": sum(
            1 for result in case_results if result["action_selection_influence"]
        ),
        "predictor_modified_count": sum(1 for result in case_results if result["predictor_modified"]),
        "memory_write_count": sum(1 for result in case_results if result["memory_write"]),
    }
    summary["all_generalized_candidate_review_preview_checks_passed"] = (
        summary["case_count"] == 6
        and summary["source_candidate_count"] == 2
        and summary["review_allowed_count"] == 4
        and summary["review_blocked_count"] == 2
        and summary["approved_count"] == 2
        and summary["rejected_count"] == 1
        and summary["deferred_count"] == 1
        and summary["pending_review_count"] == 2
        and summary["preview_created_count"] == 2
        and summary["preview_blocked_count"] == 4
        and summary["applied_count"] == 0
        and summary["persistent_candidate_count"] == 0
        and summary["persistent_rule_write_allowed_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["memory_write_count"] == 0
    )
    return summary


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "generalized_candidate_review_preview_enabled": True,
        "review_preview_only": True,
        "uses_generalized_candidates": True,
        "uses_exact_key_patterns": True,
        "cross_session_storage_added": False,
        "persistent_storage_added": False,
        "long_term_memory_write": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "exact_similar_context_key_only": True,
        "fuzzy_similarity_enabled": False,
        "semantic_similarity_enabled": False,
        "llm_similarity_enabled": False,
        "visual_similarity_enabled": False,
        "human_review_required": True,
        "qingyin_self_approval_allowed": False,
        "candidate_auto_approved": False,
        "candidate_auto_applied": False,
        "approved_preview_enabled": True,
        "preview_for_approved_only": True,
        "preview_applied": False,
        "prediction_confidence_applied_to_predictor": False,
        "prediction_rule_modified": False,
        "global_predictor_modified": False,
        "predictor_modified_count": summary["predictor_modified_count"],
        "action_selection_modified": False,
        "prediction_used_for_action_selection": False,
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "persistent_candidate_created": False,
        "persistent_rule_write_enabled": False,
        "persistent_preview_enabled": False,
        "pathfinding_used": False,
        "route_planner_added": False,
        "llm_reasoning_used": False,
        "llm_planning_used": False,
        "llm_vision_used": False,
        "general_learning_claimed": False,
        "autonomous_learning_claimed": False,
        "visual_understanding_claimed": False,
        "symbol_grounding_solved_claimed": False,
        "consciousness_claimed": False,
        "subjective_experience_claimed": False,
    }
