"""Prediction confidence suggestions from exact-key generalized memory buckets."""

from __future__ import annotations

from typing import Any

from .generalized_memory_exact_key_bucket import run_generalized_memory_exact_key_bucket_check


REQUIRED_BUCKET_FIELDS = {
    "similar_context_key",
    "session_count",
    "pattern_count",
    "outcome_distribution",
    "primary_outcome",
    "primary_reason",
    "dominant_outcome_ratio",
    "confidence_label",
    "conflict_like_distribution",
    "candidate_created",
}

DEFAULT_THRESHOLDS = {
    "increase_min_session_count": 2,
    "increase_min_pattern_count": 3,
    "increase_min_dominant_outcome_ratio": 0.8,
    "decrease_max_dominant_outcome_ratio": 0.4,
}


def evaluate_prediction_confidence_for_bucket(
    bucket_summary: dict[str, Any],
    thresholds: dict[str, Any] | None = None,
) -> dict[str, Any]:
    thresholds_used = dict(DEFAULT_THRESHOLDS)
    if thresholds:
        thresholds_used.update(thresholds)

    missing_fields = sorted(field for field in REQUIRED_BUCKET_FIELDS if field not in bucket_summary)
    if missing_fields:
        return _suggestion(
            bucket_summary,
            prediction_confidence_suggestion="blocked_missing_required_fields",
            suggested_confidence_label="unknown",
            suggestion_reason="missing_required_fields",
            block_reasons=[f"missing:{field}" for field in missing_fields],
        )

    session_count = int(bucket_summary["session_count"])
    pattern_count = int(bucket_summary["pattern_count"])
    dominant_ratio = float(bucket_summary["dominant_outcome_ratio"])
    conflict_like = bucket_summary["conflict_like_distribution"] is True

    if conflict_like:
        return _suggestion(
            bucket_summary,
            prediction_confidence_suggestion="blocked_conflict_like_distribution",
            suggested_confidence_label="hold",
            suggestion_reason="conflict_like_distribution_blocks_confidence_increase",
            block_reasons=["conflict_like_distribution"],
        )
    if session_count < thresholds_used["increase_min_session_count"]:
        return _suggestion(
            bucket_summary,
            prediction_confidence_suggestion="blocked_single_session_evidence",
            suggested_confidence_label="hold",
            suggestion_reason="single_session_evidence_is_not_enough",
            block_reasons=["single_session_evidence"],
        )
    if pattern_count < thresholds_used["increase_min_pattern_count"]:
        return _suggestion(
            bucket_summary,
            prediction_confidence_suggestion="blocked_insufficient_pattern_count",
            suggested_confidence_label="hold",
            suggestion_reason="pattern_count_below_threshold",
            block_reasons=["insufficient_pattern_count"],
        )
    if dominant_ratio >= thresholds_used["increase_min_dominant_outcome_ratio"]:
        return _suggestion(
            bucket_summary,
            prediction_confidence_suggestion="increase_confidence",
            suggested_confidence_label="high",
            suggestion_reason="stable_cross_session_exact_key_pattern",
            block_reasons=[],
        )
    if dominant_ratio <= thresholds_used["decrease_max_dominant_outcome_ratio"]:
        return _suggestion(
            bucket_summary,
            prediction_confidence_suggestion="decrease_confidence",
            suggested_confidence_label="low",
            suggestion_reason="dominant_outcome_ratio_too_low",
            block_reasons=[],
        )
    return _suggestion(
        bucket_summary,
        prediction_confidence_suggestion="hold_confidence",
        suggested_confidence_label="medium",
        suggestion_reason="enough_data_but_not_stable_enough_to_increase",
        block_reasons=[],
    )


def build_prediction_confidence_suggestions(
    bucket_summaries: list[dict[str, Any]],
    thresholds: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return [
        evaluate_prediction_confidence_for_bucket(bucket_summary, thresholds=thresholds)
        for bucket_summary in bucket_summaries
    ]


def run_generalized_prediction_confidence_check() -> dict[str, Any]:
    bucket_result = run_generalized_memory_exact_key_bucket_check()
    confidence_suggestions = build_prediction_confidence_suggestions(
        bucket_result["bucket_summaries"]
    )
    summary = _build_summary(confidence_suggestions)
    return {
        "command": "run-generalized-prediction-confidence-check",
        "flow": "generalized_prediction_confidence_check_v0",
        "status": "ok" if summary["all_generalized_prediction_confidence_checks_passed"] else "failed",
        "confidence_suggestions": confidence_suggestions,
        "summary": summary,
        "thresholds_used": dict(DEFAULT_THRESHOLDS),
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker consumes exact-key generalized memory bucket summaries.",
            "It generates prediction confidence suggestions only.",
            "It does not apply confidence to predictors, modify predictor rules, create candidates, or influence action selection.",
        ],
    }


def _suggestion(
    bucket_summary: dict[str, Any],
    prediction_confidence_suggestion: str,
    suggested_confidence_label: str,
    suggestion_reason: str,
    block_reasons: list[str],
) -> dict[str, Any]:
    return {
        "similar_context_key": bucket_summary.get("similar_context_key"),
        "session_count": bucket_summary.get("session_count"),
        "pattern_count": bucket_summary.get("pattern_count"),
        "primary_outcome": bucket_summary.get("primary_outcome"),
        "primary_reason": bucket_summary.get("primary_reason"),
        "outcome_distribution": bucket_summary.get("outcome_distribution", {}),
        "dominant_outcome_ratio": bucket_summary.get("dominant_outcome_ratio"),
        "bucket_confidence_label": bucket_summary.get("confidence_label"),
        "conflict_like_distribution": bucket_summary.get("conflict_like_distribution"),
        "prediction_confidence_suggestion": prediction_confidence_suggestion,
        "suggested_confidence_label": suggested_confidence_label,
        "suggestion_reason": suggestion_reason,
        "applied_to_predictor": False,
        "action_selection_influence": False,
        "candidate_created": False,
        "block_reasons": block_reasons,
    }


def _build_summary(confidence_suggestions: list[dict[str, Any]]) -> dict[str, Any]:
    suggestion_count = len(confidence_suggestions)
    increase_count = _count_suggestion(confidence_suggestions, "increase_confidence")
    applied_count = sum(1 for item in confidence_suggestions if item["applied_to_predictor"])
    action_influence_count = sum(1 for item in confidence_suggestions if item["action_selection_influence"])
    candidate_created_count = sum(1 for item in confidence_suggestions if item["candidate_created"])
    return {
        "bucket_count": suggestion_count,
        "suggestion_count": suggestion_count,
        "increase_confidence_count": increase_count,
        "hold_confidence_count": _count_suggestion(confidence_suggestions, "hold_confidence"),
        "decrease_confidence_count": _count_suggestion(confidence_suggestions, "decrease_confidence"),
        "blocked_conflict_like_count": _count_suggestion(
            confidence_suggestions,
            "blocked_conflict_like_distribution",
        ),
        "blocked_single_session_count": _count_suggestion(
            confidence_suggestions,
            "blocked_single_session_evidence",
        ),
        "blocked_insufficient_pattern_count": _count_suggestion(
            confidence_suggestions,
            "blocked_insufficient_pattern_count",
        ),
        "blocked_missing_required_fields_count": _count_suggestion(
            confidence_suggestions,
            "blocked_missing_required_fields",
        ),
        "applied_to_predictor_count": applied_count,
        "action_selection_influence_count": action_influence_count,
        "candidate_created_count": candidate_created_count,
        "all_generalized_prediction_confidence_checks_passed": (
            suggestion_count == 4
            and increase_count == 2
            and _count_suggestion(confidence_suggestions, "blocked_conflict_like_distribution") == 1
            and _count_suggestion(confidence_suggestions, "blocked_single_session_evidence") == 1
            and applied_count == 0
            and action_influence_count == 0
            and candidate_created_count == 0
        ),
    }


def _count_suggestion(confidence_suggestions: list[dict[str, Any]], suggestion: str) -> int:
    return sum(
        1
        for item in confidence_suggestions
        if item["prediction_confidence_suggestion"] == suggestion
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "generalized_prediction_confidence_check_enabled": True,
        "confidence_check_only": True,
        "uses_exact_key_buckets": True,
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
        "prediction_confidence_suggestions_generated": True,
        "prediction_confidence_applied_to_predictor": False,
        "prediction_rule_modified": False,
        "global_predictor_modified": False,
        "generalized_candidate_created": False,
        "candidate_auto_approved": False,
        "candidate_auto_applied": False,
        "action_selection_modified": False,
        "prediction_used_for_action_selection": False,
        "action_selection_influence_count": summary["action_selection_influence_count"],
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
