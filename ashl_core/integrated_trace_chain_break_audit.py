"""Audit chain breaks in the integrated experience session trace."""

from __future__ import annotations

from typing import Any

from .integrated_experience_session_trace import run_integrated_experience_session_trace


def run_integrated_trace_chain_break_audit() -> dict[str, Any]:
    source_trace = run_integrated_experience_session_trace()
    source_summary = source_trace["session_summary"]
    break_audit_results = [
        audit_integrated_trace_step(step)
        for step in source_trace["step_trace"]
    ]
    audit_summary = _build_audit_summary(source_summary, break_audit_results)
    return {
        "command": "run-integrated-trace-chain-break-audit",
        "flow": "integrated_trace_chain_break_audit_v0",
        "status": "ok" if audit_summary["chain_break_explained"] else "failed",
        "source_trace_summary": _source_trace_summary(source_summary),
        "break_audit_results": break_audit_results,
        "audit_summary": audit_summary,
        "boundary_check": _boundary_check(),
        "notes": [
            "Integrated Trace Chain Break Audit v0 inspects the existing integrated trace output without modifying it.",
            "The reported v0 chain break is an expected terminal no-prior-prediction case, not a missing module connection.",
            "The audit does not fix the break, approve candidates, apply candidates, modify action selection, or write memory.",
        ],
    }


def audit_integrated_trace_step(step: dict[str, Any]) -> dict[str, Any]:
    field_state = _field_state(step)
    prediction_check = step.get("prediction_check") or {}
    candidate = step.get("candidate_result") or {}
    review_gate = step.get("review_gate_result")
    chain_status = step.get("chain_status")

    break_category = _break_category(field_state, prediction_check, candidate, review_gate, chain_status)
    expected = _expected_or_unexpected(break_category)
    return {
        "tick": step.get("tick"),
        "case_name": step.get("case_name"),
        "chain_status": chain_status,
        **field_state,
        "break_detected": break_category not in {"none", "intentional_terminal_no_candidate"},
        "break_category": break_category,
        "break_reason": _break_reason(break_category, step),
        "expected_or_unexpected": expected,
    }


def _field_state(step: dict[str, Any]) -> dict[str, bool]:
    return {
        "has_viewport": bool(step.get("viewport")),
        "has_front_symbol": step.get("front_symbol") is not None,
        "has_outcome": bool(step.get("outcome")),
        "has_experience_record": bool(step.get("experience_record")),
        "has_reason_classification": bool(step.get("reason_classification")),
        "has_similar_context_key": bool(step.get("similar_context_key")),
        "has_prediction": bool(step.get("prediction_before_action")),
        "has_prediction_check": bool(step.get("prediction_check")),
        "has_candidate_result": bool(step.get("candidate_result")),
        "has_review_gate_result": bool(step.get("review_gate_result")),
    }


def _break_category(
    fields: dict[str, bool],
    prediction_check: dict[str, Any],
    candidate: dict[str, Any],
    review_gate: dict[str, Any] | None,
    chain_status: str | None,
) -> str:
    required_fields = [
        ("has_viewport", "missing_viewport"),
        ("has_front_symbol", "missing_front_symbol"),
        ("has_outcome", "missing_outcome"),
        ("has_experience_record", "missing_experience_record"),
        ("has_reason_classification", "missing_reason_classification"),
        ("has_similar_context_key", "missing_similar_context_key"),
        ("has_prediction", "missing_prediction"),
        ("has_prediction_check", "missing_prediction_check"),
        ("has_candidate_result", "missing_candidate_result"),
    ]
    for field_name, category in required_fields:
        if fields[field_name] is False:
            return category

    mismatch_type = prediction_check.get("mismatch_type")
    candidate_created = candidate.get("candidate_created") is True
    if mismatch_type == "none" and not candidate_created:
        return "intentional_terminal_no_candidate"
    if mismatch_type in {"outcome_mismatch", "reason_mismatch"} and not candidate_created:
        return "missing_candidate_for_mismatch"
    if mismatch_type == "unknown_prediction" and not candidate_created:
        return "unknown_prediction_without_candidate"
    if candidate_created and review_gate is None:
        return "missing_review_gate_for_candidate"
    if chain_status == "prediction_unknown":
        return "intentional_no_prediction_available"
    if chain_status in {"classification_unknown", "skipped_no_prediction"}:
        return chain_status
    if chain_status in {"completed_no_mismatch", "candidate_pending_review", "mismatch_candidate_created"}:
        return "none"
    return "unknown_chain_break"


def _expected_or_unexpected(category: str) -> str:
    if category in {"none", "intentional_terminal_no_candidate"}:
        return "expected_no_break"
    if category == "intentional_no_prediction_available":
        return "expected_break"
    return "unexpected_break"


def _break_reason(category: str, step: dict[str, Any]) -> str:
    if category == "none":
        return "chain_completed_with_required_fields_present"
    if category == "intentional_terminal_no_candidate":
        return "prediction matched actual observation, so no candidate or review gate is expected"
    if category == "intentional_no_prediction_available":
        return "no prior prediction was available for the observed front_symbol/action; candidate and review gate are present"
    if category == "missing_candidate_for_mismatch":
        return "prediction mismatch did not produce a rule candidate"
    if category == "missing_review_gate_for_candidate":
        return "candidate was created but did not enter the review gate"
    if category == "unknown_prediction_without_candidate":
        return "unknown prediction did not produce a candidate"
    if category.startswith("missing_"):
        return f"required field missing: {category.removeprefix('missing_')}"
    if category == "classification_unknown":
        return "reason classification returned unknown_reason"
    if category == "skipped_no_prediction":
        return "prediction was skipped and no candidate was created"
    return f"unclassified chain status: {step.get('chain_status')}"


def _source_trace_summary(source_summary: dict[str, Any]) -> dict[str, int]:
    return {
        "step_count": source_summary["step_count"],
        "source_chain_break_count": source_summary["chain_break_count"],
        "prediction_match_count": source_summary["prediction_match_count"],
        "prediction_mismatch_count": source_summary["prediction_mismatch_count"],
        "candidate_created_count": source_summary["candidate_created_count"],
        "pending_review_count": source_summary["pending_review_count"],
        "approved_count": source_summary["approved_count"],
        "applied_count": source_summary["applied_count"],
    }


def _build_audit_summary(
    source_summary: dict[str, Any],
    audit_results: list[dict[str, Any]],
) -> dict[str, Any]:
    break_results = [result for result in audit_results if result["break_detected"]]
    expected_break_count = sum(1 for result in break_results if result["expected_or_unexpected"] == "expected_break")
    unexpected_break_count = sum(1 for result in break_results if result["expected_or_unexpected"] == "unexpected_break")
    categories = sorted({result["break_category"] for result in break_results})
    source_matches = source_summary["chain_break_count"] == len(break_results)
    chain_break_explained = source_matches and unexpected_break_count == 0
    return {
        "step_count": len(audit_results),
        "break_detected_count": len(break_results),
        "expected_break_count": expected_break_count,
        "unexpected_break_count": unexpected_break_count,
        "break_categories": categories,
        "chain_break_explained": chain_break_explained,
        "source_chain_break_count_matches_audit": source_matches,
        "recommended_next_action": "document_expected_skip" if chain_break_explained and expected_break_count else "fix_integration_bug",
    }


def _boundary_check() -> dict[str, bool]:
    return {
        "integrated_trace_chain_break_audit_enabled": True,
        "audit_only": True,
        "source_trace_modified": False,
        "runtime_behavior_modified": False,
        "action_selection_modified": False,
        "candidate_application_enabled": False,
        "candidate_auto_approved": False,
        "qingyin_self_approval_allowed": False,
        "global_predictor_modified": False,
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
