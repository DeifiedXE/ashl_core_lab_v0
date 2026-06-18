"""Preview next-action pressure from settled body-motor feedback without creating action."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_body_motor_execution_feedback_settling_minimal import (
    build_sandbox_body_motor_execution_feedback_settling_record,
    run_sandbox_body_motor_execution_feedback_settling_minimal_check,
    validate_sandbox_body_motor_execution_feedback_settling_record,
)


COMMAND = "run-body-motor-feedback-gated-next-action-preview-minimal-check"
FLOW = "body_motor_feedback_gated_next_action_preview_minimal_v0"
PACKAGE_ID = "PKG-Phase0-BodyMotorFeedbackGatedNextActionPreview-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b119"
BOUNDARY_INDEX_AFTER = "2026-06-09-b120"

BASE_CANDIDATES = (
    "continue_body_motor_exploration",
    "inspect_or_reach_nearby_item",
    "pause_and_observe",
    "stop_after_budget",
)
FEEDBACK_TO_PRESSURE = {
    "movement_success_feedback": {
        "pressure_target": "continue_body_motor_exploration",
        "pressure_delta": 0.04,
        "preview_reason": "movement_success_supports_careful_continuation",
    },
    "reach_success_feedback": {
        "pressure_target": "inspect_or_reach_nearby_item",
        "pressure_delta": 0.05,
        "preview_reason": "reach_success_supports_nearby_item_attention",
    },
}
BLOCKED_FLAGS = (
    "candidate_reordering_applied",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "motor_execution_created",
    "production_behavior_changed",
    "real_navigation_changed",
    "ui_behavior_changed",
    "pathfinding_used",
    "persistent_feedback_created",
    "cross_session_feedback_persistence",
    "memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "persistent_body_schema_written",
    "persistent_endocrine_state_written",
    "semantic_vision",
    "object_recognition",
    "subjective_emotion_claim_allowed",
    "biological_hormone_claim_allowed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
    "proof_of_learning_claimed",
)


def build_body_motor_feedback_gated_next_action_preview_record(
    feedback_settling_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = deepcopy(feedback_settling_record) if feedback_settling_record is not None else (
        build_sandbox_body_motor_execution_feedback_settling_record()
    )
    source_validation = validate_sandbox_body_motor_execution_feedback_settling_record(source)
    if not source_validation["valid"]:
        raise ValueError("feedback_settling_record must validate before next-action preview")

    source_summary = _source_summary(source)
    preview = _derive_preview(source_summary)
    rollback = _derive_rollback(preview)
    return {
        "record_type": "body_motor_feedback_gated_next_action_preview_minimal",
        "record_version": "v0",
        "preview_status": "completed_same_session_body_motor_next_action_pressure_preview",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_feedback_settling": source_summary,
        "candidate_pressure_preview": preview,
        "rollback_preview": rollback,
        "human_summary": {
            "what_was_previewed": "Settled body-motor feedback was converted into same-session next-action pressure preview.",
            "what_the_preview_means": "Successful movement or reach can add small advisory pressure to a future sandbox candidate.",
            "what_is_not_created": "No candidate reordering, selected_action, final_action, direct command, or execution is created.",
            "what_is_blocked": "Persistence, memory write, predictor mutation, production behavior, semantic vision, subjective claims, and proof claims remain blocked.",
            "plain_result": "Body-motor feedback can now hint at a next sandbox candidate without choosing or doing it.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_body_motor_feedback_gated_next_action_preview_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "body_motor_feedback_gated_next_action_preview_minimal",
        "record_version": "v0",
        "preview_status": "completed_same_session_body_motor_next_action_pressure_preview",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _dict(record.get("source_feedback_settling"), errors, "source_feedback_settling_missing")
    _validate_source(source, errors)

    expected_preview = _derive_preview(source)
    preview = _dict(record.get("candidate_pressure_preview"), errors, "candidate_pressure_preview_missing")
    for field, value in expected_preview.items():
        if preview.get(field) != value:
            errors.append(f"candidate_pressure_preview_{field}_not_expected")

    expected_rollback = _derive_rollback(preview)
    rollback = _dict(record.get("rollback_preview"), errors, "rollback_preview_missing")
    for field, value in expected_rollback.items():
        if rollback.get(field) != value:
            errors.append(f"rollback_preview_{field}_not_expected")

    human = _dict(record.get("human_summary"), errors, "human_summary_missing")
    for field in (
        "what_was_previewed",
        "what_the_preview_means",
        "what_is_not_created",
        "what_is_blocked",
        "plain_result",
    ):
        if not isinstance(human.get(field), str) or not human.get(field).strip():
            errors.append(f"human_summary_{field}_empty")

    blocked = _dict(record.get("blocked_flags"), errors, "blocked_flags_missing")
    for field in BLOCKED_FLAGS:
        if blocked.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")

    return {
        "valid": not errors,
        "error_codes": errors,
        "source_feedback_settling_checked": source.get("source_validated") is True,
        "pressure_preview_created": preview.get("pressure_preview_created") is True,
        "pressure_preview_blocked": preview.get("pressure_preview_created") is False,
        "movement_success_pressure": preview.get("pressure_target") == "continue_body_motor_exploration",
        "reach_success_pressure": preview.get("pressure_target") == "inspect_or_reach_nearby_item",
        "wall_pressure_blocked": preview.get("blocked_reason") == "settled_feedback_not_available_for_next_action_preview",
        "same_session_only": preview.get("preview_scope") in {"same_session_sandbox_only", None},
        "advisory_only": preview.get("advisory_only") is True,
        "candidate_order_preserved": preview.get("candidate_order_after_preview") == list(BASE_CANDIDATES),
        "rollback_available": rollback.get("rollback_available") is True,
        "rollback_restores_baseline": rollback.get("session_end_restores_baseline") is True,
        "candidate_reordering_blocked": blocked.get("candidate_reordering_applied") is False
        and preview.get("candidate_reordering_applied") is False,
        "action_creation_blocked": blocked.get("selected_action_created") is False
        and blocked.get("final_action_created") is False
        and blocked.get("direct_command_created") is False
        and blocked.get("motor_execution_created") is False,
        "persistent_feedback_blocked": blocked.get("persistent_feedback_created") is False
        and blocked.get("cross_session_feedback_persistence") is False,
        "memory_write_blocked": blocked.get("memory_write_performed") is False
        and blocked.get("retained_jsonl_write_performed") is False,
        "retention_blocked": blocked.get("retention_write_performed") is False,
        "predictor_mutation_blocked": blocked.get("predictor_mutation_performed") is False
        and blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False,
        "persistent_state_blocked": blocked.get("persistent_body_schema_written") is False
        and blocked.get("persistent_endocrine_state_written") is False,
        "production_behavior_blocked": blocked.get("production_behavior_changed") is False
        and blocked.get("real_navigation_changed") is False
        and blocked.get("ui_behavior_changed") is False,
        "semantic_vision_blocked": blocked.get("semantic_vision") is False
        and blocked.get("object_recognition") is False,
        "subjective_claim_blocked": blocked.get("subjective_emotion_claim_allowed") is False
        and blocked.get("biological_hormone_claim_allowed") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claimed") is False
        and blocked.get("autonomous_learning_claim_allowed") is False
        and blocked.get("autonomous_action_claim_allowed") is False,
    }


def run_body_motor_feedback_gated_next_action_preview_minimal_check() -> dict[str, Any]:
    source_result = run_sandbox_body_motor_execution_feedback_settling_minimal_check()
    empty_source, wall_source, item_source = source_result["valid_records"]
    valid_empty = build_body_motor_feedback_gated_next_action_preview_record(empty_source)
    valid_wall = build_body_motor_feedback_gated_next_action_preview_record(wall_source)
    valid_item = build_body_motor_feedback_gated_next_action_preview_record(item_source)
    records = [valid_empty, valid_wall, valid_item, *_invalid_records(valid_empty)]
    validation_results = [validate_body_motor_feedback_gated_next_action_preview_record(record) for record in records]
    valid_results = [result for result in validation_results if result["valid"]]
    summary = _summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "boundary_change_required": True,
            "boundary_reason": "Converts settled body-motor feedback into same-session advisory next-action pressure preview.",
        },
        "valid_records": [valid_empty, valid_wall, valid_item],
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_previewed": "Body-motor feedback now previews next-action pressure without choosing an action.",
            "what_is_blocked": "No candidate reordering, selected_action, final_action, command, execution, persistence, memory write, predictor mutation, production behavior, semantic vision, or proof claim is created.",
            "plain_result": "Qingyin can let settled body feedback hint at the next sandbox candidate without acting.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    upstream = source["source_feedback_settling"] if "source_feedback_settling" in source else None
    if upstream is not None:
        return deepcopy(upstream)
    feedback = source["feedback_trace"]
    settling = source["settling_trace"]
    rollback = source["rollback_trace"]
    return {
        "source_record_type": source["record_type"],
        "source_validated": True,
        "source_final_action": feedback["source_final_action"],
        "source_execution_result": feedback["source_execution_result"],
        "feedback_trace_created": feedback["feedback_trace_created"],
        "feedback_label": feedback["feedback_label"],
        "response_axis": feedback["response_axis"],
        "settling_trace_created": settling["settling_trace_created"],
        "settling_mode": settling["settling_mode"],
        "settled_to_baseline": settling["settled_to_baseline"],
        "rollback_available": rollback["rollback_available"],
        "session_end_restores_baseline": rollback["session_end_restores_baseline"],
    }


def _derive_preview(source: dict[str, Any]) -> dict[str, Any]:
    config = FEEDBACK_TO_PRESSURE.get(source.get("feedback_label"))
    created = (
        source.get("feedback_trace_created") is True
        and source.get("settling_trace_created") is True
        and source.get("settled_to_baseline") is True
        and config is not None
    )
    return {
        "pressure_preview_created": created,
        "preview_scope": "same_session_sandbox_only" if created else None,
        "source_feedback_label": source.get("feedback_label") if created else source.get("feedback_label"),
        "pressure_target": config["pressure_target"] if created else None,
        "pressure_delta": config["pressure_delta"] if created else 0.0,
        "preview_reason": config["preview_reason"] if created else None,
        "candidate_order_before_preview": list(BASE_CANDIDATES),
        "candidate_order_after_preview": list(BASE_CANDIDATES),
        "candidate_reordering_applied": False,
        "advisory_only": True,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "motor_execution_created": False,
        "blocked_reason": None if created else "settled_feedback_not_available_for_next_action_preview",
        "audit_recorded": True,
    }


def _derive_rollback(preview: dict[str, Any]) -> dict[str, Any]:
    return {
        "rollback_available": True,
        "rollback_scope": "same_session_sandbox_only",
        "session_end_restores_baseline": True,
        "pressure_preview_removed_from_runtime_state": preview.get("pressure_preview_created") is True,
        "candidate_order_restored": list(BASE_CANDIDATES),
        "dirty_state_after_rollback": False,
        "persistent_update_performed": False,
        "memory_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_feedback_settling_not_validated")
    if source.get("source_record_type") != "sandbox_body_motor_execution_feedback_settling_minimal":
        errors.append("source_feedback_settling_record_type_not_expected")
    if source.get("source_final_action") is not None and source.get("source_final_action") not in ("step_forward", "reach_front"):
        errors.append("source_feedback_settling_final_action_invalid")
    if source.get("response_axis") is not None and source.get("response_axis") != "dopamine_like":
        errors.append("source_feedback_settling_response_axis_not_expected")
    if source.get("rollback_available") is not True:
        errors.append("source_feedback_settling_rollback_not_available")
    if source.get("session_end_restores_baseline") is not True:
        errors.append("source_feedback_settling_session_end_not_restoring_baseline")


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def add(name: str, mutator) -> None:
        record = deepcopy(valid_record)
        mutator(record)
        record["invalid_case"] = name
        cases.append(record)

    add("wrong_record_type", lambda r: r.__setitem__("record_type", "feedback_next_action"))
    add("source_not_validated", lambda r: r["source_feedback_settling"].__setitem__("source_validated", False))
    add("source_wrong_feedback_label", lambda r: r["source_feedback_settling"].__setitem__("feedback_label", "wrong"))
    add("source_not_settled", lambda r: r["source_feedback_settling"].__setitem__("settled_to_baseline", False))
    add("preview_not_created", lambda r: r["candidate_pressure_preview"].__setitem__("pressure_preview_created", False))
    add("wrong_preview_scope", lambda r: r["candidate_pressure_preview"].__setitem__("preview_scope", "cross_session"))
    add("wrong_pressure_target", lambda r: r["candidate_pressure_preview"].__setitem__("pressure_target", "stop_after_budget"))
    add("wrong_pressure_delta", lambda r: r["candidate_pressure_preview"].__setitem__("pressure_delta", 0.40))
    add("wrong_preview_reason", lambda r: r["candidate_pressure_preview"].__setitem__("preview_reason", "wrong"))
    add("candidate_order_changed", lambda r: r["candidate_pressure_preview"].__setitem__("candidate_order_after_preview", list(reversed(BASE_CANDIDATES))))
    add("reordering_applied", lambda r: r["candidate_pressure_preview"].__setitem__("candidate_reordering_applied", True))
    add("advisory_false", lambda r: r["candidate_pressure_preview"].__setitem__("advisory_only", False))
    add("selected_action_created", lambda r: r["candidate_pressure_preview"].__setitem__("selected_action_created", True))
    add("final_action_created", lambda r: r["candidate_pressure_preview"].__setitem__("final_action_created", True))
    add("direct_command_created", lambda r: r["candidate_pressure_preview"].__setitem__("direct_command_created", True))
    add("motor_execution_created", lambda r: r["candidate_pressure_preview"].__setitem__("motor_execution_created", True))
    add("rollback_unavailable", lambda r: r["rollback_preview"].__setitem__("rollback_available", False))
    add("rollback_dirty", lambda r: r["rollback_preview"].__setitem__("dirty_state_after_rollback", True))
    add("rollback_order_wrong", lambda r: r["rollback_preview"].__setitem__("candidate_order_restored", []))
    add("blocked_reordering", lambda r: r["blocked_flags"].__setitem__("candidate_reordering_applied", True))
    add("blocked_selected_action", lambda r: r["blocked_flags"].__setitem__("selected_action_created", True))
    add("blocked_direct_command", lambda r: r["blocked_flags"].__setitem__("direct_command_created", True))
    add("blocked_memory_write", lambda r: r["blocked_flags"].__setitem__("memory_write_performed", True))
    add("blocked_retention_write", lambda r: r["blocked_flags"].__setitem__("retention_write_performed", True))
    add("blocked_predictor_mutation", lambda r: r["blocked_flags"].__setitem__("predictor_mutation_performed", True))
    add("blocked_production", lambda r: r["blocked_flags"].__setitem__("production_behavior_changed", True))
    add("blocked_persistent_state", lambda r: r["blocked_flags"].__setitem__("persistent_endocrine_state_written", True))
    add("blocked_semantic_vision", lambda r: r["blocked_flags"].__setitem__("semantic_vision", True))
    add("blocked_subjective_claim", lambda r: r["blocked_flags"].__setitem__("subjective_emotion_claim_allowed", True))
    add("blocked_proof_claim", lambda r: r["blocked_flags"].__setitem__("proof_of_learning_claimed", True))
    add("empty_human_summary", lambda r: r["human_summary"].__setitem__("plain_result", ""))
    return cases


def _summary(results: list[dict[str, Any]]) -> dict[str, int]:
    valid_results = [result for result in results if result["valid"]]
    return {
        "next_action_preview_result_count": len(results),
        "valid_next_action_preview_count": len(valid_results),
        "invalid_next_action_preview_count": len(results) - len(valid_results),
        "source_feedback_settling_checked_count": _count_valid(valid_results, "source_feedback_settling_checked"),
        "pressure_preview_created_count": _count_valid(valid_results, "pressure_preview_created"),
        "pressure_preview_blocked_count": _count_valid(valid_results, "pressure_preview_blocked"),
        "movement_success_pressure_count": _count_valid(valid_results, "movement_success_pressure"),
        "reach_success_pressure_count": _count_valid(valid_results, "reach_success_pressure"),
        "wall_pressure_blocked_count": _count_valid(valid_results, "wall_pressure_blocked"),
        "same_session_only_count": _count_valid(valid_results, "same_session_only"),
        "advisory_only_count": _count_valid(valid_results, "advisory_only"),
        "candidate_order_preserved_count": _count_valid(valid_results, "candidate_order_preserved"),
        "rollback_available_count": _count_valid(valid_results, "rollback_available"),
        "rollback_restores_baseline_count": _count_valid(valid_results, "rollback_restores_baseline"),
        "candidate_reordering_blocked_count": _count_valid(valid_results, "candidate_reordering_blocked"),
        "action_creation_blocked_count": _count_valid(valid_results, "action_creation_blocked"),
        "persistent_feedback_blocked_count": _count_valid(valid_results, "persistent_feedback_blocked"),
        "memory_write_blocked_count": _count_valid(valid_results, "memory_write_blocked"),
        "retention_blocked_count": _count_valid(valid_results, "retention_blocked"),
        "predictor_mutation_blocked_count": _count_valid(valid_results, "predictor_mutation_blocked"),
        "persistent_state_blocked_count": _count_valid(valid_results, "persistent_state_blocked"),
        "production_behavior_blocked_count": _count_valid(valid_results, "production_behavior_blocked"),
        "semantic_vision_blocked_count": _count_valid(valid_results, "semantic_vision_blocked"),
        "subjective_claim_blocked_count": _count_valid(valid_results, "subjective_claim_blocked"),
        "proof_claim_blocked_count": _count_valid(valid_results, "proof_claim_blocked"),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["next_action_preview_result_count"] == 34
        and summary["valid_next_action_preview_count"] == 3
        and summary["invalid_next_action_preview_count"] == 31
        and summary["source_feedback_settling_checked_count"] == 3
        and summary["pressure_preview_created_count"] == 2
        and summary["pressure_preview_blocked_count"] == 1
        and summary["movement_success_pressure_count"] == 1
        and summary["reach_success_pressure_count"] == 1
        and summary["wall_pressure_blocked_count"] == 1
        and summary["same_session_only_count"] == 3
        and summary["advisory_only_count"] == 3
        and summary["candidate_order_preserved_count"] == 3
        and summary["rollback_available_count"] == 3
        and summary["rollback_restores_baseline_count"] == 3
        and summary["candidate_reordering_blocked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["persistent_feedback_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["retention_blocked_count"] == 3
        and summary["predictor_mutation_blocked_count"] == 3
        and summary["persistent_state_blocked_count"] == 3
        and summary["production_behavior_blocked_count"] == 3
        and summary["semantic_vision_blocked_count"] == 3
        and summary["subjective_claim_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
    )


def _dict(value: Any, errors: list[str], error_code: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(error_code)
        return {}
    return value


def _count_valid(results: list[dict[str, Any]], field: str) -> int:
    return sum(1 for result in results if result.get(field) is True)
