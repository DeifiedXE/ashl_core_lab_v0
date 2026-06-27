"""Expectation matrix for ASHL Core v1 cradle review/routing behavior."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ashl_core_v1.runtime.cradle_cases import (
    build_all_cradle_case_samples,
    build_cradle_case_sample,
    list_cradle_case_ids,
)


_MATRIX: dict[str, dict[str, object]] = {
    "blocked_front_obstacle": {
        "case_id": "blocked_front_obstacle",
        "expected_review_status": "approved",
        "expected_memory_entry_allowed": True,
        "expected_routing_status": "routed",
        "expected_memory_layer_target": "working",
        "expected_influence_visible": True,
        "expected_body_action_signal_type": "observe_or_adjust",
    },
    "success_front_step": {
        "case_id": "success_front_step",
        "expected_review_status": "approved",
        "expected_memory_entry_allowed": True,
        "expected_routing_status": "routed",
        "expected_memory_layer_target": "working",
        "expected_influence_visible": True,
        "expected_body_action_signal_type": "continue_or_observe",
    },
    "unknown_feedback": {
        "case_id": "unknown_feedback",
        "expected_review_status": "needs_more_evidence",
        "expected_memory_entry_allowed": False,
        "expected_routing_status": "held_for_review",
        "expected_memory_layer_target": "none",
        "expected_influence_visible": False,
        "expected_body_action_signal_type": "observe",
    },
    "teacher_rejected": {
        "case_id": "teacher_rejected",
        "expected_review_status": "rejected",
        "expected_memory_entry_allowed": False,
        "expected_routing_status": "rejected",
        "expected_memory_layer_target": "none",
        "expected_influence_visible": False,
        "expected_body_action_signal_type": "wait",
    },
    "teacher_deferred": {
        "case_id": "teacher_deferred",
        "expected_review_status": "deferred",
        "expected_memory_entry_allowed": False,
        "expected_routing_status": "deferred",
        "expected_memory_layer_target": "none",
        "expected_influence_visible": False,
        "expected_body_action_signal_type": "wait",
    },
    "conflict_detected": {
        "case_id": "conflict_detected",
        "expected_review_status": "conflict_detected",
        "expected_memory_entry_allowed": False,
        "expected_routing_status": "conflict_detected",
        "expected_memory_layer_target": "none",
        "expected_influence_visible": False,
        "expected_body_action_signal_type": "observe_or_adjust",
    },
    "stale_learning": {
        "case_id": "stale_learning",
        "expected_review_status": "approved",
        "expected_memory_entry_allowed": True,
        "expected_routing_status": "stale",
        "expected_memory_layer_target": "none",
        "expected_influence_visible": False,
        "expected_body_action_signal_type": "observe",
    },
    "superseded_learning": {
        "case_id": "superseded_learning",
        "expected_review_status": "approved",
        "expected_memory_entry_allowed": True,
        "expected_routing_status": "superseded",
        "expected_memory_layer_target": "none",
        "expected_influence_visible": False,
        "expected_body_action_signal_type": "observe",
    },
}


def get_review_routing_expectation_matrix() -> dict[str, dict[str, object]]:
    return deepcopy(_MATRIX)


def check_cradle_case_against_matrix(case_id: str, sample: dict[str, Any]) -> dict[str, Any]:
    matrix = get_review_routing_expectation_matrix()
    if case_id not in matrix:
        raise ValueError(f"unknown cradle case id: {case_id}")
    expected = matrix[case_id]
    actual = _actual_from_sample(sample)
    checks = {
        "review_status": "expected_review_status",
        "memory_entry_allowed": "expected_memory_entry_allowed",
        "routing_status": "expected_routing_status",
        "memory_layer_target": "expected_memory_layer_target",
        "influence_visible": "expected_influence_visible",
        "body_action_signal_type": "expected_body_action_signal_type",
    }
    mismatches = {
        actual_key: {
            "expected": expected[expected_key],
            "actual": actual[actual_key],
        }
        for actual_key, expected_key in checks.items()
        if actual[actual_key] != expected[expected_key]
    }
    return {
        "case_id": case_id,
        "passed": not mismatches,
        "expected": expected,
        "actual": actual,
        "mismatches": mismatches,
    }


def check_all_cradle_cases_against_matrix() -> dict[str, Any]:
    samples = build_all_cradle_case_samples()
    case_results = {
        case_id: check_cradle_case_against_matrix(case_id, samples[case_id])
        for case_id in list_cradle_case_ids()
    }
    passed_count = sum(1 for result in case_results.values() if result["passed"])
    failed_count = len(case_results) - passed_count
    return {
        "case_count": len(case_results),
        "passed_count": passed_count,
        "failed_count": failed_count,
        "all_passed": failed_count == 0,
        "case_results": case_results,
    }


def _actual_from_sample(sample: dict[str, Any]) -> dict[str, object]:
    summary = sample["cycle_summary"]
    return {
        "case_id": summary["case_id"],
        "review_status": summary["review_status"],
        "memory_entry_allowed": summary["memory_entry_allowed"],
        "routing_status": summary["routing_status"],
        "memory_layer_target": summary["memory_layer_target"],
        "influence_visible": summary["influence_visible"],
        "body_action_signal_type": summary["body_action_signal_type"],
    }
