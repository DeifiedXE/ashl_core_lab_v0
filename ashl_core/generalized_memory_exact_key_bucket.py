"""Exact-key generalized memory bucket checker."""

from __future__ import annotations

from collections import Counter
from typing import Any


DEFAULT_THRESHOLDS = {
    "high_confidence_min_dominant_outcome_ratio": 0.8,
    "high_confidence_min_session_count": 2,
    "high_confidence_min_pattern_count": 3,
    "medium_confidence_min_dominant_outcome_ratio": 0.6,
    "candidate_min_session_count": 2,
    "candidate_min_pattern_count": 3,
    "candidate_min_dominant_outcome_ratio": 0.8,
}


def build_exact_key_buckets(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = {}
    for record in records:
        key = record.get("similar_context_key")
        if not key:
            raise ValueError("record missing similar_context_key")
        bucket = buckets.setdefault(
            key,
            {
                "similar_context_key": key,
                "records": [],
            },
        )
        bucket["records"].append(dict(record))
    return buckets


def summarize_exact_key_bucket(
    bucket: dict[str, Any],
    thresholds: dict[str, Any] | None = None,
) -> dict[str, Any]:
    thresholds_used = dict(DEFAULT_THRESHOLDS)
    if thresholds:
        thresholds_used.update(thresholds)

    records = list(bucket.get("records", []))
    if not records:
        raise ValueError("bucket has no records")

    session_ids = sorted({record.get("session_id") for record in records if record.get("session_id")})
    experience_ids = [record.get("experience_id") for record in records if record.get("experience_id")]
    outcome_counts = Counter(record.get("outcome_type") for record in records)
    reason_counts = Counter(record.get("reason") for record in records)
    primary_outcome, primary_outcome_count = _primary_counter_value(outcome_counts)
    primary_reason, _ = _primary_counter_value(reason_counts)
    pattern_count = len(records)
    dominant_outcome_ratio = primary_outcome_count / pattern_count
    conflict_like_distribution = len(outcome_counts) > 1
    confidence_label = _confidence_label(
        dominant_outcome_ratio=dominant_outcome_ratio,
        session_count=len(session_ids),
        pattern_count=pattern_count,
        thresholds=thresholds_used,
    )
    eligible_for_generalized_candidate = (
        len(session_ids) >= thresholds_used["candidate_min_session_count"]
        and pattern_count >= thresholds_used["candidate_min_pattern_count"]
        and dominant_outcome_ratio >= thresholds_used["candidate_min_dominant_outcome_ratio"]
        and not conflict_like_distribution
    )

    return {
        "similar_context_key": bucket["similar_context_key"],
        "source_session_ids": session_ids,
        "source_experience_ids": experience_ids,
        "session_count": len(session_ids),
        "pattern_count": pattern_count,
        "outcome_distribution": dict(sorted(outcome_counts.items())),
        "reason_distribution": dict(sorted(reason_counts.items())),
        "primary_outcome": primary_outcome,
        "primary_reason": primary_reason,
        "dominant_outcome_ratio": dominant_outcome_ratio,
        "confidence_label": confidence_label,
        "conflict_like_distribution": conflict_like_distribution,
        "eligible_for_generalized_candidate": eligible_for_generalized_candidate,
        "candidate_created": False,
        "notes": [
            "Aggregated by exact similar_context_key only.",
            "Eligibility is calculated for review-gated future work; no generalized candidate is created.",
        ],
    }


def build_demo_cross_session_experience_records() -> list[dict[str, Any]]:
    records = []
    records.extend(
        _records_for_key(
            case_name="stable_wall_bucket",
            key="front_symbol=w|action=move_forward|primary_reason=front_cell_wall",
            sessions=["session_A", "session_B", "session_C"],
            outcome_type="blocked",
            reason="front_cell_wall",
        )
    )
    records.extend(
        _records_for_key(
            case_name="stable_item_bucket",
            key="front_symbol=i|action=move_forward|primary_reason=front_cell_item_contact",
            sessions=["session_A", "session_B", "session_C"],
            outcome_type="item_contact",
            reason="front_cell_item_contact",
        )
    )
    records.extend(
        [
            _record(
                "mixed_empty_bucket",
                "session_A",
                1,
                "front_symbol=e|action=move_forward|primary_reason=front_cell_empty_walkable",
                "move_forward",
                "moved",
                "front_cell_empty_walkable",
            ),
            _record(
                "mixed_empty_bucket",
                "session_B",
                1,
                "front_symbol=e|action=move_forward|primary_reason=front_cell_empty_walkable",
                "move_forward",
                "moved",
                "front_cell_empty_walkable",
            ),
            _record(
                "mixed_empty_bucket",
                "session_C",
                1,
                "front_symbol=e|action=move_forward|primary_reason=front_cell_empty_walkable",
                "move_forward",
                "blocked",
                "unexpected_blocked",
            ),
        ]
    )
    records.append(
        _record(
            "single_session_bucket",
            "session_A",
            2,
            "front_symbol=d|action=look|primary_reason=front_cell_door_observed",
            "look",
            "observed",
            "front_cell_door_observed",
        )
    )
    return records


def run_generalized_memory_exact_key_bucket_check() -> dict[str, Any]:
    records = build_demo_cross_session_experience_records()
    buckets = build_exact_key_buckets(records)
    bucket_summaries = [
        summarize_exact_key_bucket(bucket)
        for _, bucket in sorted(buckets.items(), key=lambda item: item[0])
    ]
    summary = _build_summary(records, bucket_summaries)
    return {
        "command": "run-generalized-memory-exact-key-bucket-check",
        "flow": "generalized_memory_exact_key_bucket_v0",
        "status": "ok" if summary["all_generalized_memory_exact_key_bucket_checks_passed"] else "failed",
        "bucket_summaries": bucket_summaries,
        "summary": summary,
        "thresholds_used": dict(DEFAULT_THRESHOLDS),
        "boundary_check": _boundary_check(),
        "notes": [
            "This checker aggregates demo records by exact similar_context_key only.",
            "It calculates pattern counts, outcome distributions, confidence labels, and future candidate eligibility.",
            "It does not create generalized candidates, modify predictors, write memory, or affect action selection.",
        ],
    }


def _records_for_key(
    case_name: str,
    key: str,
    sessions: list[str],
    outcome_type: str,
    reason: str,
) -> list[dict[str, Any]]:
    return [
        _record(case_name, session_id, index + 1, key, "move_forward", outcome_type, reason)
        for index, session_id in enumerate(sessions)
    ]


def _record(
    case_name: str,
    session_id: str,
    tick: int,
    key: str,
    action: str,
    outcome_type: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "case_name": case_name,
        "session_id": session_id,
        "experience_id": f"{session_id}:{case_name}:{tick}",
        "tick": tick,
        "similar_context_key": key,
        "action": action,
        "outcome_type": outcome_type,
        "reason": reason,
        "metadata": {
            "demo_fixture": True,
            "exact_key_only": True,
        },
    }


def _primary_counter_value(counter: Counter) -> tuple[Any, int]:
    return sorted(counter.items(), key=lambda item: (-item[1], str(item[0])))[0]


def _confidence_label(
    dominant_outcome_ratio: float,
    session_count: int,
    pattern_count: int,
    thresholds: dict[str, Any],
) -> str:
    if (
        dominant_outcome_ratio >= thresholds["high_confidence_min_dominant_outcome_ratio"]
        and session_count >= thresholds["high_confidence_min_session_count"]
        and pattern_count >= thresholds["high_confidence_min_pattern_count"]
    ):
        return "high"
    if dominant_outcome_ratio >= thresholds["medium_confidence_min_dominant_outcome_ratio"]:
        return "medium"
    return "low"


def _build_summary(records: list[dict[str, Any]], bucket_summaries: list[dict[str, Any]]) -> dict[str, Any]:
    confidence_counts = Counter(summary["confidence_label"] for summary in bucket_summaries)
    candidate_created_count = sum(1 for summary in bucket_summaries if summary["candidate_created"])
    return {
        "record_count": len(records),
        "bucket_count": len(bucket_summaries),
        "cross_session_bucket_count": sum(1 for summary in bucket_summaries if summary["session_count"] >= 2),
        "stable_bucket_count": sum(1 for summary in bucket_summaries if not summary["conflict_like_distribution"]),
        "mixed_bucket_count": sum(1 for summary in bucket_summaries if summary["conflict_like_distribution"]),
        "single_session_bucket_count": sum(1 for summary in bucket_summaries if summary["session_count"] == 1),
        "eligible_for_generalized_candidate_count": sum(
            1 for summary in bucket_summaries if summary["eligible_for_generalized_candidate"]
        ),
        "candidate_created_count": candidate_created_count,
        "high_confidence_bucket_count": confidence_counts.get("high", 0),
        "medium_confidence_bucket_count": confidence_counts.get("medium", 0),
        "low_confidence_bucket_count": confidence_counts.get("low", 0),
        "all_generalized_memory_exact_key_bucket_checks_passed": (
            len(records) == 10
            and len(bucket_summaries) == 4
            and candidate_created_count == 0
            and any(
                summary["primary_outcome"] == "blocked"
                and summary["dominant_outcome_ratio"] == 1.0
                and summary["confidence_label"] == "high"
                and summary["eligible_for_generalized_candidate"] is True
                for summary in bucket_summaries
            )
            and any(
                summary["conflict_like_distribution"] is True
                and summary["eligible_for_generalized_candidate"] is False
                for summary in bucket_summaries
            )
            and any(
                summary["session_count"] == 1
                and summary["eligible_for_generalized_candidate"] is False
                for summary in bucket_summaries
            )
        ),
    }


def _boundary_check() -> dict[str, bool]:
    return {
        "generalized_memory_exact_key_bucket_enabled": True,
        "exact_key_bucket_only": True,
        "runtime_check_only": True,
        "cross_session_aggregation_demo": True,
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
        "prediction_confidence_calculated": True,
        "prediction_confidence_applied_to_predictor": False,
        "prediction_rule_modified": False,
        "global_predictor_modified": False,
        "generalized_candidate_eligibility_calculated": True,
        "generalized_candidate_created": False,
        "candidate_auto_approved": False,
        "candidate_auto_applied": False,
        "action_selection_modified": False,
        "prediction_used_for_action_selection": False,
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
