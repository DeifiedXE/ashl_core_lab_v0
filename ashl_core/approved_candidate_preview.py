"""Deterministic preview for approved rule candidates."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .rule_candidate_from_mismatch import run_rule_candidate_from_mismatch_check
from .rule_candidate_review_gate import enter_review, review_candidate


CREATED_BY = "deterministic_approved_candidate_preview_v0"
SUPPORTED_CANDIDATE_TYPES = {
    "outcome_rule_revision_candidate",
    "reason_rule_revision_candidate",
    "unknown_context_rule_candidate",
}


def build_approved_candidate_preview(
    candidate: dict[str, Any],
    current_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    candidate_status = candidate.get("candidate_status")
    preview_allowed = candidate_status == "approved" and candidate.get("candidate_type") in SUPPORTED_CANDIDATE_TYPES
    state_before = deepcopy(current_state) if current_state is not None else None
    proposed_state = _proposed_state(candidate)
    changed_fields = _changed_fields(state_before, proposed_state) if preview_allowed else []
    preview_type = _preview_type(state_before, preview_allowed)

    return {
        "preview_id": _preview_id(candidate, preview_type),
        "candidate_id": candidate.get("candidate_id"),
        "preview_created": preview_allowed,
        "preview_blocked_reason": None if preview_allowed else _blocked_reason(candidate),
        "candidate_status": candidate_status,
        "target_similar_context_key": candidate.get("target_similar_context_key"),
        "preview_type": preview_type,
        "current_state": state_before,
        "proposed_state": proposed_state if preview_allowed else None,
        "changed_fields": changed_fields,
        "would_modify_predictor": preview_allowed,
        "predictor_modified_now": False,
        "would_modify_action_selection": False,
        "would_write_lesson_store": False,
        "would_write_memory_layer": False,
        "application_allowed_later": preview_allowed,
        "applied_now": False,
        "requires_application_step": preview_allowed,
        "created_by": CREATED_BY,
    }


def run_approved_candidate_preview_check() -> dict[str, Any]:
    preview_results = []
    for case_name, candidate, current_state, expected in _check_cases():
        preview = build_approved_candidate_preview(candidate, current_state)
        preview_results.append(
            {
                "case_name": case_name,
                "candidate": candidate,
                "current_state": current_state,
                "preview": preview,
                "passed": _preview_matches_expected(preview, expected),
            }
        )

    summary = _build_summary(preview_results)
    return {
        "command": "run-approved-candidate-preview-check",
        "flow": "approved_candidate_preview_v0",
        "status": "ok" if summary["all_approved_candidate_preview_checks_passed"] else "failed",
        "preview_results": preview_results,
        "summary": summary,
        "boundary_check": _boundary_check(),
        "notes": [
            "Approved Candidate Preview v0 creates deterministic previews for approved rule candidates.",
            "Preview shows proposed predictor entry changes before any application step.",
            "No rule is applied, no predictor rule is modified now, and no action selection or memory write is changed.",
        ],
    }


def _check_cases() -> list[tuple[str, dict[str, Any], dict[str, Any] | None, dict[str, Any]]]:
    candidates = _source_candidates()
    approved_outcome = _approve(candidates["outcome_mismatch_candidate"])
    approved_reason = _approve(candidates["reason_mismatch_candidate"])
    approved_unknown = _approve(candidates["unknown_prediction_candidate"])
    pending_candidate = enter_review(candidates["outcome_mismatch_candidate"])["candidate_after"]
    rejected_candidate = review_candidate(pending_candidate, "reject")["candidate_after"]
    current_empty = _current_state("moved", "front_cell_empty_walkable")
    return [
        (
            "approved_outcome_revision_preview",
            approved_outcome,
            current_empty,
            _expected(True, "rule_revision_preview", ["predicted_outcome_type", "predicted_primary_reason"]),
        ),
        (
            "approved_reason_revision_preview",
            approved_reason,
            current_empty,
            _expected(True, "rule_revision_preview", ["predicted_primary_reason"]),
        ),
        (
            "approved_unknown_context_preview",
            approved_unknown,
            None,
            _expected(True, "new_prediction_entry_preview", ["new_prediction_entry"]),
        ),
        (
            "pending_candidate_preview_blocked",
            pending_candidate,
            current_empty,
            _expected(False, "preview_blocked", []),
        ),
        (
            "rejected_candidate_preview_blocked",
            rejected_candidate,
            current_empty,
            _expected(False, "preview_blocked", []),
        ),
    ]


def _source_candidates() -> dict[str, dict[str, Any]]:
    result = run_rule_candidate_from_mismatch_check()
    return {
        item["case_name"]: item["candidate"]
        for item in result["candidate_results"]
    }


def _approve(candidate: dict[str, Any]) -> dict[str, Any]:
    pending = enter_review(candidate)["candidate_after"]
    return review_candidate(pending, "approve")["candidate_after"]


def _current_state(outcome_type: str, primary_reason: str) -> dict[str, Any]:
    return {
        "predicted_outcome_type": outcome_type,
        "predicted_primary_reason": primary_reason,
    }


def _proposed_state(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "predicted_outcome_type": candidate.get("proposed_outcome_type"),
        "predicted_primary_reason": candidate.get("proposed_primary_reason"),
    }


def _changed_fields(current_state: dict[str, Any] | None, proposed_state: dict[str, Any]) -> list[str]:
    if current_state is None:
        return ["new_prediction_entry"]
    fields = []
    for field in ["predicted_outcome_type", "predicted_primary_reason"]:
        if current_state.get(field) != proposed_state.get(field):
            fields.append(field)
    return fields


def _preview_type(current_state: dict[str, Any] | None, preview_allowed: bool) -> str:
    if not preview_allowed:
        return "preview_blocked"
    if current_state is None:
        return "new_prediction_entry_preview"
    return "rule_revision_preview"


def _blocked_reason(candidate: dict[str, Any]) -> str:
    if candidate.get("candidate_status") != "approved":
        return "candidate_not_approved"
    if candidate.get("candidate_type") not in SUPPORTED_CANDIDATE_TYPES:
        return "unsupported_candidate_type"
    return "preview_not_allowed"


def _expected(preview_created: bool, preview_type: str, changed_fields: list[str]) -> dict[str, Any]:
    return {
        "preview_created": preview_created,
        "preview_type": preview_type,
        "changed_fields": changed_fields,
        "applied_now": False,
        "predictor_modified_now": False,
    }


def _preview_matches_expected(preview: dict[str, Any], expected: dict[str, Any]) -> bool:
    return (
        preview["preview_created"] is expected["preview_created"]
        and preview["preview_type"] == expected["preview_type"]
        and all(field in preview["changed_fields"] for field in expected["changed_fields"])
        and preview["applied_now"] is expected["applied_now"]
        and preview["predictor_modified_now"] is expected["predictor_modified_now"]
    )


def _build_summary(preview_results: list[dict[str, Any]]) -> dict[str, Any]:
    case_count = len(preview_results)
    passed_count = sum(1 for result in preview_results if result["passed"])
    previews = [result["preview"] for result in preview_results]
    return {
        "case_count": case_count,
        "passed_count": passed_count,
        "failed_count": case_count - passed_count,
        "preview_created_count": sum(1 for preview in previews if preview["preview_created"]),
        "preview_blocked_count": sum(1 for preview in previews if not preview["preview_created"]),
        "approved_preview_count": sum(
            1 for preview in previews if preview["preview_created"] and preview["candidate_status"] == "approved"
        ),
        "applied_now_count": sum(1 for preview in previews if preview["applied_now"]),
        "predictor_modified_now_count": sum(1 for preview in previews if preview["predictor_modified_now"]),
        "all_approved_candidate_preview_checks_passed": passed_count == case_count,
    }


def _preview_id(candidate: dict[str, Any], preview_type: str) -> str:
    return f"preview:{preview_type}:{_ascii_safe(candidate.get('candidate_id'))}"


def _ascii_safe(value: Any) -> str:
    text = "null" if value is None else str(value)
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in text)


def _boundary_check() -> dict[str, Any]:
    return {
        "approved_candidate_preview_enabled": True,
        "experience_abstraction_layer_continued": True,
        "requires_approved_candidate": True,
        "preview_only": True,
        "application_step_enabled": False,
        "candidate_application_enabled": False,
        "predictor_rule_modified": False,
        "action_selection_modified": False,
        "rule_learning_enabled": False,
        "rule_revision_enabled": False,
        "rule_application_enabled": False,
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
