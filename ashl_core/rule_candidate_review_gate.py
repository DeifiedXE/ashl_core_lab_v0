"""Deterministic review gate for rule candidates."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .rule_candidate_from_mismatch import run_rule_candidate_from_mismatch_check


CREATED_BY = "deterministic_review_gate_v0"
HUMAN_REVIEWER_TYPE = "human"


def enter_review(candidate: dict[str, Any]) -> dict[str, Any]:
    candidate_before = deepcopy(candidate)
    candidate_after = deepcopy(candidate)
    allowed = candidate.get("candidate_status") == "proposed" and candidate.get("requires_review") is True
    if allowed:
        candidate_after["candidate_status"] = "pending_review"
    return _review_result(
        candidate_before=candidate_before,
        candidate_after=candidate_after,
        review_decision="pending_review",
        review_status="pending_review" if allowed else candidate.get("candidate_status"),
        review_reason="candidate_entered_pending_review" if allowed else "candidate_not_review_required",
        reviewer_type=HUMAN_REVIEWER_TYPE,
        review_allowed=allowed,
    )


def review_candidate(
    candidate: dict[str, Any],
    decision: str,
    reviewer_type: str = HUMAN_REVIEWER_TYPE,
    reason: str | None = None,
) -> dict[str, Any]:
    candidate_before = deepcopy(candidate)
    candidate_after = deepcopy(candidate)
    normalized = _normalize_decision(decision)
    human_allowed = reviewer_type == HUMAN_REVIEWER_TYPE
    decision_allowed = normalized in {"approved", "rejected", "deferred"}
    status_allowed = candidate.get("candidate_status") == "pending_review"
    review_allowed = human_allowed and decision_allowed and status_allowed

    if review_allowed:
        candidate_after["candidate_status"] = normalized

    return _review_result(
        candidate_before=candidate_before,
        candidate_after=candidate_after,
        review_decision=normalized if decision_allowed else "invalid",
        review_status=candidate_after.get("candidate_status"),
        review_reason=reason or _review_reason(
            human_allowed=human_allowed,
            decision_allowed=decision_allowed,
            status_allowed=status_allowed,
            normalized=normalized,
        ),
        reviewer_type=reviewer_type,
        review_allowed=review_allowed,
    )


def run_rule_candidate_review_gate_check() -> dict[str, Any]:
    base_candidate = _source_candidate()
    pending_candidate = enter_review(base_candidate)["candidate_after"]
    review_results = []
    for case_name, candidate, review_input, expected in _check_cases(base_candidate, pending_candidate):
        if review_input["operation"] == "enter_review":
            review_result = enter_review(candidate)
        else:
            review_result = review_candidate(
                candidate,
                review_input["decision"],
                reviewer_type=review_input["reviewer_type"],
                reason=review_input.get("reason"),
            )
        review_results.append(
            {
                "case_name": case_name,
                "candidate_before": review_result["candidate_before"],
                "review_input": review_input,
                "review_result": review_result,
                "candidate_after": review_result["candidate_after"],
                "passed": _review_matches_expected(review_result, expected),
            }
        )

    summary = _build_summary(review_results)
    return {
        "command": "run-rule-candidate-review-gate-check",
        "flow": "rule_candidate_review_gate_v0",
        "status": "ok" if summary["all_rule_candidate_review_gate_checks_passed"] else "failed",
        "review_results": review_results,
        "summary": summary,
        "boundary_check": _boundary_check(),
        "notes": [
            "Rule Candidate Review Gate v0 moves proposed candidates into pending_review and records human review decisions.",
            "Approval is a review state only; approved candidates are not applied and predictor rules are not revised.",
            "Qingyin self-approval is blocked; only human reviewers are accepted in v0.",
        ],
    }


def _source_candidate() -> dict[str, Any]:
    result = run_rule_candidate_from_mismatch_check()
    return next(
        item["candidate"]
        for item in result["candidate_results"]
        if item["case_name"] == "outcome_mismatch_candidate"
    )


def _check_cases(base_candidate: dict[str, Any], pending_candidate: dict[str, Any]) -> list[tuple[str, dict[str, Any], dict[str, Any], dict[str, Any]]]:
    return [
        (
            "enter_pending_review",
            base_candidate,
            {"operation": "enter_review"},
            _expected("pending_review", "pending_review", True),
        ),
        (
            "approve_candidate",
            pending_candidate,
            {"operation": "review", "decision": "approve", "reviewer_type": HUMAN_REVIEWER_TYPE},
            _expected("approved", "approved", True),
        ),
        (
            "reject_candidate",
            pending_candidate,
            {"operation": "review", "decision": "reject", "reviewer_type": HUMAN_REVIEWER_TYPE},
            _expected("rejected", "rejected", True),
        ),
        (
            "defer_candidate",
            pending_candidate,
            {"operation": "review", "decision": "defer", "reviewer_type": HUMAN_REVIEWER_TYPE},
            _expected("deferred", "deferred", True),
        ),
        (
            "non_human_self_approval_blocked",
            pending_candidate,
            {"operation": "review", "decision": "approve", "reviewer_type": "qingyin_self"},
            _expected("approved", "pending_review", False),
        ),
    ]


def _expected(review_decision: str, candidate_status: str, review_allowed: bool) -> dict[str, Any]:
    return {
        "review_decision": review_decision,
        "candidate_status": candidate_status,
        "review_allowed": review_allowed,
        "applied": False,
    }


def _review_result(
    *,
    candidate_before: dict[str, Any],
    candidate_after: dict[str, Any],
    review_decision: str,
    review_status: str | None,
    review_reason: str,
    reviewer_type: str,
    review_allowed: bool,
) -> dict[str, Any]:
    candidate_id = candidate_before.get("candidate_id")
    return {
        "review_id": f"review:{candidate_id}:{review_decision}:{_ascii_safe(reviewer_type)}",
        "candidate_id": candidate_id,
        "reviewer_type": reviewer_type,
        "review_decision": review_decision,
        "review_status": review_status,
        "review_allowed": review_allowed,
        "review_reason": review_reason,
        "candidate_before": candidate_before,
        "candidate_after": candidate_after,
        "applied": False,
        "requires_manual_review": True,
        "created_by": CREATED_BY,
    }


def _review_matches_expected(review_result: dict[str, Any], expected: dict[str, Any]) -> bool:
    return (
        review_result["review_decision"] == expected["review_decision"]
        and review_result["candidate_after"]["candidate_status"] == expected["candidate_status"]
        and review_result["review_allowed"] is expected["review_allowed"]
        and review_result["applied"] is expected["applied"]
    )


def _normalize_decision(decision: str) -> str:
    mapping = {
        "approve": "approved",
        "approved": "approved",
        "reject": "rejected",
        "rejected": "rejected",
        "defer": "deferred",
        "deferred": "deferred",
    }
    return mapping.get(decision, "invalid")


def _review_reason(*, human_allowed: bool, decision_allowed: bool, status_allowed: bool, normalized: str) -> str:
    if not human_allowed:
        return "non_human_reviewer_blocked"
    if not decision_allowed:
        return "invalid_review_decision"
    if not status_allowed:
        return "candidate_not_pending_review"
    return f"human_review_marked_{normalized}"


def _build_summary(review_results: list[dict[str, Any]]) -> dict[str, Any]:
    case_count = len(review_results)
    passed_count = sum(1 for result in review_results if result["passed"])
    statuses = [result["candidate_after"]["candidate_status"] for result in review_results]
    blocked = [
        result
        for result in review_results
        if result["review_input"].get("reviewer_type") != HUMAN_REVIEWER_TYPE
        and result["review_result"]["review_allowed"] is False
    ]
    return {
        "case_count": case_count,
        "passed_count": passed_count,
        "failed_count": case_count - passed_count,
        "pending_review_count": statuses.count("pending_review"),
        "approved_count": statuses.count("approved"),
        "rejected_count": statuses.count("rejected"),
        "deferred_count": statuses.count("deferred"),
        "self_approval_blocked_count": len(blocked),
        "all_rule_candidate_review_gate_checks_passed": passed_count == case_count,
    }


def _ascii_safe(value: Any) -> str:
    text = "null" if value is None else str(value)
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in text)


def _boundary_check() -> dict[str, Any]:
    return {
        "rule_candidate_review_gate_enabled": True,
        "experience_abstraction_layer_continued": True,
        "human_reviewer_required": True,
        "qingyin_self_approval_allowed": False,
        "candidate_review_only": True,
        "candidate_application_enabled": False,
        "rule_learning_enabled": False,
        "rule_revision_enabled": False,
        "rule_application_enabled": False,
        "predictor_rule_modified": False,
        "action_selection_modified": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "long_term_memory_write": False,
        "persistent_memory_write": False,
        "pathfinding_used": False,
        "route_planner_added": False,
        "llm_reasoning_used": False,
        "llm_planning_used": False,
        "llm_vision_used": False,
        "general_learning_claimed": False,
        "visual_understanding_claimed": False,
        "symbol_grounding_solved_claimed": False,
        "consciousness_claimed": False,
        "subjective_experience_claimed": False,
    }
