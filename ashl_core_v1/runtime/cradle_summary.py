"""Human-readable summaries for ASHL Core v1 cradle cases."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.cradle_cases import build_cradle_case_sample, list_cradle_case_ids
from ashl_core_v1.runtime.cradle_runner import load_last_cradle_run


_HUMAN_SUMMARIES = {
    "blocked_front_obstacle": (
        "approved blocked learning can enter working memory trace and influence next "
        "observe_or_adjust signal."
    ),
    "success_front_step": (
        "approved success learning can enter working memory trace and support a "
        "continue_or_observe signal."
    ),
    "unknown_feedback": (
        "unknown feedback remains held for more evidence and does not influence the next signal."
    ),
    "teacher_rejected": (
        "rejected learning is preserved as review trace but does not enter memory application."
    ),
    "teacher_deferred": (
        "deferred learning waits for later teacher decision and does not enter active memory."
    ),
    "conflict_detected": (
        "conflicting learning stays out of memory application until the conflict is resolved."
    ),
    "stale_learning": (
        "approved but stale learning is trace-visible but not routed into active memory layer."
    ),
    "superseded_learning": (
        "approved but superseded learning is trace-visible while later learning replaces active use."
    ),
}


def summarize_cradle_case(case_id: str) -> dict[str, Any]:
    sample = build_cradle_case_sample(case_id)
    summary = sample["cycle_summary"]
    return _summary_from_cycle_summary(summary)


def summarize_all_cradle_cases() -> dict[str, Any]:
    case_summaries = [summarize_cradle_case(case_id) for case_id in list_cradle_case_ids()]
    approved_count = sum(1 for item in case_summaries if item["review_status"] == "approved")
    routed_count = sum(1 for item in case_summaries if item["routing_status"] == "routed")
    influence_visible_count = sum(1 for item in case_summaries if item["influence_visible"])
    return {
        "case_count": len(case_summaries),
        "approved_count": approved_count,
        "blocked_by_review_count": len(case_summaries) - approved_count,
        "routed_count": routed_count,
        "not_routed_count": len(case_summaries) - routed_count,
        "influence_visible_count": influence_visible_count,
        "case_summaries": case_summaries,
    }


def summarize_last_run(data_dir: str | Path | None = None) -> dict[str, Any] | None:
    last_run = load_last_cradle_run(data_dir)
    if last_run is None:
        return None
    if "case_summaries" in last_run:
        case_summaries = [
            _summary_from_cycle_summary(item)
            for item in last_run["case_summaries"]
        ]
    else:
        case_summaries = [_summary_from_cycle_summary(last_run["cycle_summary"])]
    approved_count = sum(1 for item in case_summaries if item["review_status"] == "approved")
    routed_count = sum(1 for item in case_summaries if item["routing_status"] == "routed")
    influence_visible_count = sum(1 for item in case_summaries if item["influence_visible"])
    return {
        "source_run_id": last_run["run_id"],
        "case_count": len(case_summaries),
        "approved_count": approved_count,
        "blocked_by_review_count": len(case_summaries) - approved_count,
        "routed_count": routed_count,
        "not_routed_count": len(case_summaries) - routed_count,
        "influence_visible_count": influence_visible_count,
        "case_summaries": case_summaries,
    }


def _summary_from_cycle_summary(summary: dict[str, Any]) -> dict[str, Any]:
    case_id = summary["case_id"]
    return {
        "case_id": case_id,
        "review_status": summary["review_status"],
        "routing_status": summary["routing_status"],
        "memory_entry_allowed": summary["memory_entry_allowed"],
        "memory_layer_target": summary.get("memory_layer_target", "none"),
        "influence_visible": summary["influence_visible"],
        "body_action_signal_type": summary["body_action_signal_type"],
        "human_readable_summary": _HUMAN_SUMMARIES[case_id],
    }
