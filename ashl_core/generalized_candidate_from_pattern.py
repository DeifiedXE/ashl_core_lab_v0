"""Review-gated generalized candidates from stable exact-key patterns."""

from __future__ import annotations

from typing import Any

from .generalized_prediction_confidence_check import run_generalized_prediction_confidence_check


REQUIRED_SUGGESTION_FIELDS = {
    "similar_context_key",
    "session_count",
    "pattern_count",
    "primary_outcome",
    "primary_reason",
    "outcome_distribution",
    "dominant_outcome_ratio",
    "bucket_confidence_label",
    "conflict_like_distribution",
    "prediction_confidence_suggestion",
    "suggested_confidence_label",
    "applied_to_predictor",
    "action_selection_influence",
    "candidate_created",
    "block_reasons",
}

DEFAULT_THRESHOLDS = {
    "min_session_count": 2,
    "min_pattern_count": 3,
    "min_dominant_outcome_ratio": 0.8,
}


def evaluate_generalized_candidate_eligibility(
    suggestion: dict[str, Any],
    thresholds: dict[str, Any] | None = None,
) -> dict[str, Any]:
    thresholds_used = dict(DEFAULT_THRESHOLDS)
    if thresholds:
        thresholds_used.update(thresholds)

    missing_fields = sorted(field for field in REQUIRED_SUGGESTION_FIELDS if field not in suggestion)
    if missing_fields:
        return _blocked_result(
            suggestion,
            [f"missing_required_field:{field}" for field in missing_fields],
        )

    block_reasons = _block_reasons(suggestion, thresholds_used)
    if block_reasons:
        return _blocked_result(suggestion, block_reasons)
    return _created_result(suggestion)


def build_generalized_candidates_from_confidence_suggestions(
    suggestions: list[dict[str, Any]],
    thresholds: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return [
        evaluate_generalized_candidate_eligibility(suggestion, thresholds=thresholds)
        for suggestion in suggestions
    ]


def run_generalized_candidate_from_pattern_check() -> dict[str, Any]:
    confidence_result = run_generalized_prediction_confidence_check()
    candidate_results = build_generalized_candidates_from_confidence_suggestions(
        confidence_result["confidence_suggestions"]
    )
    summary = _build_summary(candidate_results)
    return {
        "command": "run-generalized-candidate-from-pattern-check",
        "flow": "generalized_candidate_from_pattern_v0",
        "status": "ok" if summary["all_generalized_candidate_from_pattern_checks_passed"] else "failed",
        "candidate_results": candidate_results,
        "summary": summary,
        "thresholds_used": dict(DEFAULT_THRESHOLDS),
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker creates review-gated generalized candidates in output only.",
            "Created candidates remain pending_review, unapproved, unapplied, and non-persistent.",
            "It does not write candidates, modify predictors, or influence action selection.",
        ],
    }


def _block_reasons(suggestion: dict[str, Any], thresholds: dict[str, Any]) -> list[str]:
    reasons = []
    if suggestion.get("conflict_like_distribution") is True:
        reasons.append("conflict_like_distribution")
    if int(suggestion.get("session_count", 0) or 0) < thresholds["min_session_count"]:
        reasons.append("single_session_evidence")
    if int(suggestion.get("pattern_count", 0) or 0) < thresholds["min_pattern_count"]:
        reasons.append("insufficient_pattern_count")
    if suggestion.get("suggested_confidence_label") != "high":
        reasons.append("confidence_not_high")
    if suggestion.get("prediction_confidence_suggestion") != "increase_confidence":
        reasons.append("suggestion_not_increase_confidence")
    if float(suggestion.get("dominant_outcome_ratio", 0.0) or 0.0) < thresholds["min_dominant_outcome_ratio"]:
        reasons.append("dominant_outcome_ratio_below_threshold")
    if suggestion.get("applied_to_predictor") is not False:
        reasons.append("confidence_application_not_allowed")
    if suggestion.get("action_selection_influence") is not False:
        reasons.append("action_selection_influence_not_allowed")
    return reasons


def _created_result(suggestion: dict[str, Any]) -> dict[str, Any]:
    candidate = _candidate(suggestion, candidate_created=True, block_reasons=[])
    return {
        "similar_context_key": suggestion.get("similar_context_key"),
        "primary_reason": suggestion.get("primary_reason"),
        "candidate_created": True,
        "candidate": candidate,
        "block_reasons": [],
    }


def _blocked_result(suggestion: dict[str, Any], block_reasons: list[str]) -> dict[str, Any]:
    candidate = _candidate(suggestion, candidate_created=False, block_reasons=block_reasons)
    return {
        "similar_context_key": suggestion.get("similar_context_key"),
        "primary_reason": suggestion.get("primary_reason"),
        "candidate_created": False,
        "candidate": candidate,
        "block_reasons": block_reasons,
    }


def _candidate(
    suggestion: dict[str, Any],
    candidate_created: bool,
    block_reasons: list[str],
) -> dict[str, Any]:
    status = "pending_review" if candidate_created else "blocked"
    return {
        "candidate_id": _candidate_id(suggestion),
        "candidate_type": "generalized_prediction_confidence_candidate",
        "candidate_status": status,
        "source": "generalized_memory_exact_key_pattern",
        "similar_context_key": suggestion.get("similar_context_key"),
        "proposed_prediction_outcome": suggestion.get("primary_outcome") if candidate_created else None,
        "proposed_prediction_reason": suggestion.get("primary_reason") if candidate_created else None,
        "evidence": {
            "source_session_count": suggestion.get("session_count"),
            "source_pattern_count": suggestion.get("pattern_count"),
            "source_outcome_distribution": suggestion.get("outcome_distribution", {}),
            "dominant_outcome_ratio": suggestion.get("dominant_outcome_ratio"),
            "confidence_label": suggestion.get("suggested_confidence_label"),
            "prediction_confidence_suggestion": suggestion.get("prediction_confidence_suggestion"),
            "source_similar_context_key": suggestion.get("similar_context_key"),
        },
        "review_required": candidate_created,
        "review_status": "pending_review" if candidate_created else "not_created",
        "approved": False,
        "applied": False,
        "persistent_candidate": False,
        "persistent_rule_write_allowed": False,
        "action_selection_influence": False,
        "block_reasons": block_reasons,
    }


def _candidate_id(suggestion: dict[str, Any]) -> str | None:
    key = suggestion.get("similar_context_key")
    if not key:
        return None
    normalized = str(key).replace("|", "__").replace("=", "-")
    return f"generalized_candidate:{normalized}"


def _build_summary(candidate_results: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [result["candidate"] for result in candidate_results]
    created = [candidate for candidate in candidates if candidate["candidate_status"] == "pending_review"]
    blocked = [candidate for candidate in candidates if candidate["candidate_status"] == "blocked"]
    summary = {
        "suggestion_count": len(candidate_results),
        "candidate_created_count": len(created),
        "pending_review_count": sum(1 for candidate in candidates if candidate["review_status"] == "pending_review"),
        "blocked_count": len(blocked),
        "approved_count": sum(1 for candidate in candidates if candidate["approved"]),
        "applied_count": sum(1 for candidate in candidates if candidate["applied"]),
        "persistent_candidate_count": sum(1 for candidate in candidates if candidate["persistent_candidate"]),
        "persistent_rule_write_allowed_count": sum(
            1 for candidate in candidates if candidate["persistent_rule_write_allowed"]
        ),
        "action_selection_influence_count": sum(
            1 for candidate in candidates if candidate["action_selection_influence"]
        ),
        "blocked_conflict_like_count": _count_block(candidate_results, "conflict_like_distribution"),
        "blocked_single_session_count": _count_block(candidate_results, "single_session_evidence"),
        "blocked_insufficient_pattern_count": _count_block(candidate_results, "insufficient_pattern_count"),
        "blocked_confidence_not_high_count": _count_block(candidate_results, "confidence_not_high"),
    }
    summary["all_generalized_candidate_from_pattern_checks_passed"] = (
        summary["suggestion_count"] == 4
        and summary["candidate_created_count"] == 2
        and summary["pending_review_count"] == 2
        and summary["blocked_count"] == 2
        and summary["approved_count"] == 0
        and summary["applied_count"] == 0
        and summary["persistent_candidate_count"] == 0
        and summary["persistent_rule_write_allowed_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["blocked_conflict_like_count"] == 1
        and summary["blocked_single_session_count"] == 1
    )
    return summary


def _count_block(candidate_results: list[dict[str, Any]], reason: str) -> int:
    return sum(1 for result in candidate_results if reason in result["block_reasons"])


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "generalized_candidate_from_pattern_enabled": True,
        "candidate_generation_check_only": True,
        "uses_exact_key_buckets": True,
        "uses_prediction_confidence_suggestions": True,
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
        "generalized_candidate_created_in_output": summary["candidate_created_count"] > 0,
        "generalized_candidate_persisted": False,
        "candidate_auto_approved": False,
        "candidate_auto_applied": False,
        "review_required": True,
        "review_status_pending_only": True,
        "prediction_confidence_applied_to_predictor": False,
        "prediction_rule_modified": False,
        "global_predictor_modified": False,
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
