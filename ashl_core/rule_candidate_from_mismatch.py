"""Deterministic rule candidates from prediction mismatches."""

from __future__ import annotations

from typing import Any

from .prediction_accuracy_check import run_prediction_accuracy_check


CREATED_BY = "deterministic_mismatch_candidate_builder_v0"


def build_rule_candidate_from_prediction_check(prediction_check: dict[str, Any]) -> dict[str, Any]:
    mismatch_type = prediction_check.get("mismatch_type")
    candidate_type = _candidate_type(mismatch_type)
    candidate_created = candidate_type != "no_candidate_for_match"
    target_key = prediction_check.get("similar_context_key")
    confidence = 1.0 if candidate_created else 0.0
    return {
        "candidate_id": _candidate_id(candidate_type, target_key),
        "candidate_created": candidate_created,
        "candidate_type": candidate_type,
        "source_mismatch_type": mismatch_type,
        "target_similar_context_key": target_key,
        "candidate_status": "proposed",
        "proposed_outcome_type": prediction_check.get("actual_outcome_type") if candidate_created else None,
        "proposed_primary_reason": prediction_check.get("actual_primary_reason") if candidate_created else None,
        "evidence": {
            "prediction_check_id": prediction_check.get("prediction_check_id"),
            "predicted_outcome_type": prediction_check.get("predicted_outcome_type"),
            "actual_outcome_type": prediction_check.get("actual_outcome_type"),
            "predicted_primary_reason": prediction_check.get("predicted_primary_reason"),
            "actual_primary_reason": prediction_check.get("actual_primary_reason"),
            "mismatch_type": mismatch_type,
            "similar_context_key": target_key,
            "mismatch_reasons": list(prediction_check.get("mismatch_reasons", [])),
        },
        "confidence": confidence,
        "requires_review": candidate_created,
        "created_by": CREATED_BY,
        "notes": _notes(candidate_created, candidate_type),
    }


def run_rule_candidate_from_mismatch_check() -> dict[str, Any]:
    prediction_result = run_prediction_accuracy_check()
    source_checks = {
        result["case_name"]: result["prediction_check"]
        for result in prediction_result["check_results"]
    }
    candidate_results = []
    for case_name, source_case_name, expected in _check_cases():
        prediction_check = source_checks[source_case_name]
        candidate = build_rule_candidate_from_prediction_check(prediction_check)
        candidate_results.append(
            {
                "case_name": case_name,
                "prediction_check": prediction_check,
                "candidate": candidate,
                "passed": _candidate_matches_expected(candidate, expected),
            }
        )

    summary = _build_summary(candidate_results)
    return {
        "command": "run-rule-candidate-from-mismatch-check",
        "flow": "rule_candidate_from_mismatch_v0",
        "status": "ok" if summary["all_rule_candidate_from_mismatch_checks_passed"] else "failed",
        "candidate_results": candidate_results,
        "summary": summary,
        "boundary_check": _boundary_check(),
        "notes": [
            "Rule Candidate From Prediction Mismatch v0 converts prediction mismatches into proposed review-required candidates.",
            "Candidates are not auto-approved, applied, persisted, or used for action selection.",
            "No predictor rule revision, rule learning, LLM reasoning, pathfinding, or memory write is added.",
        ],
    }


def _candidate_type(mismatch_type: str | None) -> str:
    if mismatch_type == "outcome_mismatch":
        return "outcome_rule_revision_candidate"
    if mismatch_type == "reason_mismatch":
        return "reason_rule_revision_candidate"
    if mismatch_type == "unknown_prediction":
        return "unknown_context_rule_candidate"
    return "no_candidate_for_match"


def _candidate_id(candidate_type: str, target_key: Any) -> str:
    return f"candidate:{candidate_type}:{_ascii_safe(target_key)}"


def _ascii_safe(value: Any) -> str:
    text = "null" if value is None else str(value)
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in text)


def _notes(candidate_created: bool, candidate_type: str) -> list[str]:
    if not candidate_created:
        return ["Prediction matched actual observation; no rule candidate is created."]
    return [
        f"{candidate_type} is proposed from direct mismatch evidence.",
        "Review is required before any later approval or rule application.",
    ]


def _check_cases() -> list[tuple[str, str, dict[str, Any]]]:
    return [
        (
            "match_no_candidate",
            "wall_prediction_match",
            _expected(False, "no_candidate_for_match"),
        ),
        (
            "outcome_mismatch_candidate",
            "outcome_mismatch",
            _expected(True, "outcome_rule_revision_candidate"),
        ),
        (
            "reason_mismatch_candidate",
            "reason_mismatch",
            _expected(True, "reason_rule_revision_candidate"),
        ),
        (
            "unknown_prediction_candidate",
            "unknown_prediction",
            _expected(True, "unknown_context_rule_candidate"),
        ),
    ]


def _expected(candidate_created: bool, candidate_type: str) -> dict[str, Any]:
    return {
        "candidate_created": candidate_created,
        "candidate_type": candidate_type,
        "requires_review": candidate_created,
        "candidate_status": "proposed",
    }


def _candidate_matches_expected(candidate: dict[str, Any], expected: dict[str, Any]) -> bool:
    return (
        candidate["candidate_created"] is expected["candidate_created"]
        and candidate["candidate_type"] == expected["candidate_type"]
        and candidate["requires_review"] is expected["requires_review"]
        and candidate["candidate_status"] == expected["candidate_status"]
    )


def _build_summary(candidate_results: list[dict[str, Any]]) -> dict[str, Any]:
    case_count = len(candidate_results)
    passed_count = sum(1 for result in candidate_results if result["passed"])
    candidates = [result["candidate"] for result in candidate_results]
    return {
        "case_count": case_count,
        "passed_count": passed_count,
        "failed_count": case_count - passed_count,
        "candidate_created_count": sum(1 for candidate in candidates if candidate["candidate_created"]),
        "no_candidate_count": sum(1 for candidate in candidates if not candidate["candidate_created"]),
        "outcome_revision_candidate_count": _count_type(candidates, "outcome_rule_revision_candidate"),
        "reason_revision_candidate_count": _count_type(candidates, "reason_rule_revision_candidate"),
        "unknown_context_candidate_count": _count_type(candidates, "unknown_context_rule_candidate"),
        "all_rule_candidate_from_mismatch_checks_passed": passed_count == case_count,
    }


def _count_type(candidates: list[dict[str, Any]], candidate_type: str) -> int:
    return sum(1 for candidate in candidates if candidate["candidate_type"] == candidate_type)


def _boundary_check() -> dict[str, Any]:
    return {
        "rule_candidate_from_mismatch_enabled": True,
        "experience_abstraction_layer_continued": True,
        "uses_prediction_accuracy_check": True,
        "candidate_creation_only": True,
        "requires_review": True,
        "rule_learning_enabled": False,
        "rule_revision_enabled": False,
        "rule_application_enabled": False,
        "candidate_auto_approved": False,
        "action_selection_modified": False,
        "prediction_used_for_action_selection": False,
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
