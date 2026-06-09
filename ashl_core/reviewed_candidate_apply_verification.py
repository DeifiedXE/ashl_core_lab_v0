"""Temporary in-memory application verification for reviewed candidates."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .rule_candidate_from_mismatch import run_rule_candidate_from_mismatch_check
from .rule_candidate_review_gate import enter_review, review_candidate


APPLICATION_SOURCE = "deterministic_reviewed_candidate_apply_verification_v0"
SUPPORTED_CANDIDATE_TYPES = {
    "outcome_rule_revision_candidate",
    "reason_rule_revision_candidate",
    "unknown_context_rule_candidate",
}


def apply_candidate_to_rule_table(candidate: dict[str, Any], rule_table: dict[str, dict[str, Any]]) -> dict[str, Any]:
    before = deepcopy(rule_table)
    updated = deepcopy(rule_table)
    allowed, blocked_reason = _application_allowed(candidate)
    changed_fields: list[str] = []
    if allowed:
        key = candidate["target_similar_context_key"]
        existing = updated.get(key)
        new_entry = _rule_entry(candidate)
        if existing is None:
            changed_fields.append("new_rule_entry")
        else:
            for field in ["predicted_outcome_type", "predicted_primary_reason"]:
                if existing.get(field) != new_entry.get(field):
                    changed_fields.append(field)
        updated[key] = new_entry

    return {
        "application_attempted": True,
        "application_allowed": allowed,
        "applied_in_memory": allowed,
        "persistent_write": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "long_term_memory_write": False,
        "application_blocked_reason": blocked_reason,
        "changed_fields": changed_fields,
        "rule_table_before": before,
        "rule_table_after": updated,
        "rule_table_changed": before != updated,
        "predictor_global_modified": False,
    }


def predict_with_rule_table(candidate_context: dict[str, Any], rule_table: dict[str, dict[str, Any]]) -> dict[str, Any]:
    key = candidate_context["similar_context_key"]
    entry = rule_table.get(key)
    if entry is None:
        return {
            "prediction_id": "prediction:temporary_rule_table:unknown",
            "similar_context_key": key,
            "predicted_outcome_type": "unknown",
            "predicted_primary_reason": "unknown_outcome_reason",
            "confidence": 0.0,
            "unknown_prediction": True,
            "prediction_source": "temporary_in_memory_rule_table_v0",
        }
    return {
        "prediction_id": f"prediction:temporary_rule_table:{_ascii_safe(key)}",
        "similar_context_key": key,
        "predicted_outcome_type": entry["predicted_outcome_type"],
        "predicted_primary_reason": entry["predicted_primary_reason"],
        "predicted_failure_reasons": list(entry.get("failure_reasons", [])),
        "predicted_effect_tags": list(entry.get("effect_tags", [])),
        "confidence": 1.0,
        "unknown_prediction": False,
        "prediction_source": "temporary_in_memory_rule_table_v0",
    }


def run_reviewed_candidate_apply_verification_check() -> dict[str, Any]:
    application_results = []
    for case_name, candidate, rule_table, expected in _check_cases():
        table_before = deepcopy(rule_table)
        application_result = apply_candidate_to_rule_table(candidate, rule_table)
        table_after = application_result["rule_table_after"]
        prediction_after = predict_with_rule_table(_candidate_context(candidate), table_after)
        verification = _verify_prediction(prediction_after, candidate, expected)
        application_results.append(
            {
                "case_name": case_name,
                "candidate": candidate,
                "rule_table_before": table_before,
                "application_result": _public_application_result(application_result),
                "prediction_after_apply": prediction_after,
                "rule_table_after": table_after,
                "verification": verification,
                "passed": _case_passed(application_result, verification, expected, table_before, table_after),
            }
        )

    summary = _build_summary(application_results)
    return {
        "command": "run-reviewed-candidate-apply-verification-check",
        "flow": "reviewed_candidate_apply_verification_v0",
        "status": "ok" if summary["all_reviewed_candidate_apply_verification_checks_passed"] else "failed",
        "application_results": application_results,
        "summary": summary,
        "boundary_check": _boundary_check(),
        "notes": [
            "Reviewed Candidate Apply Verification v0 applies approved candidates only to a temporary in-memory predictor rule table.",
            "Prediction is rerun against the runner-local table to verify the expected outcome and reason.",
            "No persistent rule, global predictor, action selection, lesson_store, Memory Layer, or long-term memory write is changed.",
        ],
    }


def _check_cases() -> list[tuple[str, dict[str, Any], dict[str, dict[str, Any]], dict[str, Any]]]:
    candidates = _source_candidates()
    approved_outcome = _with_review_metadata(_approve(candidates["outcome_mismatch_candidate"]), "human", "approved")
    approved_reason = _with_review_metadata(_approve(candidates["reason_mismatch_candidate"]), "human", "approved")
    approved_unknown = _with_review_metadata(_approve(candidates["unknown_prediction_candidate"]), "human", "approved")
    pending = enter_review(candidates["outcome_mismatch_candidate"])["candidate_after"]
    rejected = _with_review_metadata(review_candidate(pending, "reject")["candidate_after"], "human", "rejected")
    self_approved = _with_review_metadata(deepcopy(approved_outcome), "qingyin_self", "approved")
    self_approved["candidate_status"] = "approved"
    return [
        (
            "approved_outcome_revision_apply",
            approved_outcome,
            _base_rule_table(),
            _expected(True, "blocked", "front_cell_wall"),
        ),
        (
            "approved_reason_revision_apply",
            approved_reason,
            _base_rule_table(),
            _expected(True, "moved", "front_cell_passage_crossed"),
        ),
        (
            "approved_unknown_context_apply",
            approved_unknown,
            {},
            _expected(True, "moved", "front_cell_empty_walkable"),
        ),
        (
            "pending_candidate_blocked",
            pending,
            _base_rule_table(),
            _expected(False, "moved", "front_cell_empty_walkable", "candidate_not_approved"),
        ),
        (
            "rejected_candidate_blocked",
            rejected,
            _base_rule_table(),
            _expected(False, "moved", "front_cell_empty_walkable", "candidate_not_approved"),
        ),
        (
            "self_approved_candidate_blocked",
            self_approved,
            _base_rule_table(),
            _expected(False, "moved", "front_cell_empty_walkable", "invalid_reviewer"),
        ),
    ]


def _source_candidates() -> dict[str, dict[str, Any]]:
    result = run_rule_candidate_from_mismatch_check()
    return {item["case_name"]: item["candidate"] for item in result["candidate_results"]}


def _approve(candidate: dict[str, Any]) -> dict[str, Any]:
    pending = enter_review(candidate)["candidate_after"]
    return review_candidate(pending, "approve")["candidate_after"]


def _with_review_metadata(candidate: dict[str, Any], reviewer_type: str, review_status: str) -> dict[str, Any]:
    updated = deepcopy(candidate)
    updated["review_metadata"] = {
        "reviewer_type": reviewer_type,
        "review_status": review_status,
        "review_decision": review_status,
    }
    return updated


def _base_rule_table() -> dict[str, dict[str, Any]]:
    key = "front_symbol=e|action=move_forward|primary_reason=front_cell_empty_walkable"
    return {
        key: {
            "predicted_outcome_type": "moved",
            "predicted_primary_reason": "front_cell_empty_walkable",
            "failure_reasons": [],
            "effect_tags": [],
            "source": "controlled_initial_rule_table_v0",
        }
    }


def _candidate_context(candidate: dict[str, Any]) -> dict[str, Any]:
    return {"similar_context_key": candidate["target_similar_context_key"]}


def _application_allowed(candidate: dict[str, Any]) -> tuple[bool, str | None]:
    if candidate.get("candidate_status") != "approved":
        return False, "candidate_not_approved"
    review = candidate.get("review_metadata", {})
    if review.get("reviewer_type") != "human":
        return False, "invalid_reviewer"
    if review.get("review_status") != "approved" and review.get("review_decision") != "approved":
        return False, "review_not_approved"
    if candidate.get("candidate_type") not in SUPPORTED_CANDIDATE_TYPES:
        return False, "unsupported_candidate_type"
    return True, None


def _rule_entry(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "predicted_outcome_type": candidate["proposed_outcome_type"],
        "predicted_primary_reason": candidate["proposed_primary_reason"],
        "failure_reasons": [],
        "effect_tags": [],
        "source": APPLICATION_SOURCE,
    }


def _verify_prediction(prediction: dict[str, Any], candidate: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    expected_outcome = expected["expected_outcome_type"]
    expected_reason = expected["expected_primary_reason"]
    actual_outcome = prediction["predicted_outcome_type"]
    actual_reason = prediction["predicted_primary_reason"]
    passed = actual_outcome == expected_outcome and actual_reason == expected_reason
    return {
        "prediction_changed_as_expected": passed if expected["application_allowed"] else True,
        "expected_outcome_type": expected_outcome,
        "actual_outcome_type": actual_outcome,
        "expected_primary_reason": expected_reason,
        "actual_primary_reason": actual_reason,
        "verification_passed": passed,
    }


def _expected(
    application_allowed: bool,
    expected_outcome_type: str,
    expected_primary_reason: str,
    blocked_reason: str | None = None,
) -> dict[str, Any]:
    return {
        "application_allowed": application_allowed,
        "expected_outcome_type": expected_outcome_type,
        "expected_primary_reason": expected_primary_reason,
        "blocked_reason": blocked_reason,
    }


def _case_passed(
    application_result: dict[str, Any],
    verification: dict[str, Any],
    expected: dict[str, Any],
    table_before: dict[str, Any],
    table_after: dict[str, Any],
) -> bool:
    allowed = expected["application_allowed"]
    blocked_ok = application_result["application_blocked_reason"] == expected["blocked_reason"]
    table_ok = table_before != table_after if allowed else table_before == table_after
    return (
        application_result["application_allowed"] is allowed
        and application_result["applied_in_memory"] is allowed
        and application_result["persistent_write"] is False
        and application_result["lesson_store_write"] is False
        and application_result["memory_layer_write"] is False
        and application_result["long_term_memory_write"] is False
        and blocked_ok
        and table_ok
        and verification["verification_passed"] is True
    )


def _public_application_result(application_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "application_attempted": application_result["application_attempted"],
        "application_allowed": application_result["application_allowed"],
        "applied_in_memory": application_result["applied_in_memory"],
        "persistent_write": application_result["persistent_write"],
        "lesson_store_write": application_result["lesson_store_write"],
        "memory_layer_write": application_result["memory_layer_write"],
        "long_term_memory_write": application_result["long_term_memory_write"],
        "application_blocked_reason": application_result["application_blocked_reason"],
        "changed_fields": list(application_result["changed_fields"]),
        "rule_table_changed": application_result["rule_table_changed"],
        "predictor_global_modified": application_result["predictor_global_modified"],
    }


def _build_summary(application_results: list[dict[str, Any]]) -> dict[str, Any]:
    case_count = len(application_results)
    passed_count = sum(1 for result in application_results if result["passed"])
    applications = [result["application_result"] for result in application_results]
    return {
        "case_count": case_count,
        "passed_count": passed_count,
        "failed_count": case_count - passed_count,
        "applied_in_memory_count": sum(1 for item in applications if item["applied_in_memory"]),
        "blocked_application_count": sum(1 for item in applications if not item["application_allowed"]),
        "persistent_write_count": sum(1 for item in applications if item["persistent_write"]),
        "predictor_global_modified_count": sum(1 for item in applications if item["predictor_global_modified"]),
        "lesson_store_write_count": sum(1 for item in applications if item["lesson_store_write"]),
        "memory_layer_write_count": sum(1 for item in applications if item["memory_layer_write"]),
        "long_term_memory_write_count": sum(1 for item in applications if item["long_term_memory_write"]),
        "all_reviewed_candidate_apply_verification_checks_passed": passed_count == case_count,
    }


def _ascii_safe(value: Any) -> str:
    text = "null" if value is None else str(value)
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in text)


def _boundary_check() -> dict[str, Any]:
    return {
        "reviewed_candidate_apply_verification_enabled": True,
        "experience_abstraction_layer_continued": True,
        "requires_approved_candidate": True,
        "requires_human_review": True,
        "temporary_in_memory_rule_table": True,
        "persistent_rule_application_enabled": False,
        "candidate_application_enabled_in_runner": True,
        "global_predictor_modified": False,
        "predictor_rule_modified_in_memory_only": True,
        "action_selection_modified": False,
        "prediction_used_for_action_selection": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "long_term_memory_write": False,
        "persistent_memory_write": False,
        "rule_learning_enabled": False,
        "automatic_rule_revision_enabled": False,
        "candidate_auto_approved": False,
        "qingyin_self_approval_allowed": False,
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
