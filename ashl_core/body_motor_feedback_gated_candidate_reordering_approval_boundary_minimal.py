"""Approval boundary for future candidate reordering from body-motor feedback pressure."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .body_motor_feedback_gated_next_action_preview_minimal import (
    build_body_motor_feedback_gated_next_action_preview_record,
    run_body_motor_feedback_gated_next_action_preview_minimal_check,
    validate_body_motor_feedback_gated_next_action_preview_record,
)


COMMAND = "run-body-motor-feedback-gated-candidate-reordering-approval-boundary-minimal-check"
FLOW = "body_motor_feedback_gated_candidate_reordering_approval_boundary_minimal_v0"
PACKAGE_ID = "PKG-Phase0-BodyMotorFeedbackGatedCandidateReorderingApprovalBoundary-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b120"
BOUNDARY_INDEX_AFTER = "2026-06-09-b121"

ALLOWED_PRESSURE_TARGETS = (
    "continue_body_motor_exploration",
    "inspect_or_reach_nearby_item",
)
ALLOWED_NEXT_PACKAGE = "Body-Motor Feedback-Gated Candidate Reordering Minimal v0"
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


def build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(
    next_action_preview_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = deepcopy(next_action_preview_record) if next_action_preview_record is not None else (
        build_body_motor_feedback_gated_next_action_preview_record()
    )
    source_validation = validate_body_motor_feedback_gated_next_action_preview_record(source)
    if not source_validation["valid"]:
        raise ValueError("next_action_preview_record must validate before reordering approval boundary")

    source_summary = _source_summary(source)
    boundary = _derive_reordering_boundary(source_summary)
    return {
        "record_type": "body_motor_feedback_gated_candidate_reordering_approval_boundary_minimal",
        "record_version": "v0",
        "approval_boundary_status": "completed_body_motor_feedback_gated_candidate_reordering_approval_boundary",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_next_action_preview": source_summary,
        "candidate_reordering_approval_boundary": boundary,
        "human_summary": {
            "what_was_built": "A candidate reordering approval boundary was created for settled body-motor feedback pressure.",
            "what_it_allows": "Valid same-session pressure previews may proceed to a future sandbox-only candidate reordering package.",
            "what_it_blocks": "This package does not reorder candidates or create selected_action, final_action, direct command, or execution.",
            "plain_result": "Body feedback can now be approved up to the next candidate reordering boundary, but ordering is unchanged.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "body_motor_feedback_gated_candidate_reordering_approval_boundary_minimal",
        "record_version": "v0",
        "approval_boundary_status": "completed_body_motor_feedback_gated_candidate_reordering_approval_boundary",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _dict(record.get("source_next_action_preview"), errors, "source_next_action_preview_missing")
    _validate_source(source, errors)

    expected_boundary = _derive_reordering_boundary(source)
    boundary = _dict(
        record.get("candidate_reordering_approval_boundary"),
        errors,
        "candidate_reordering_approval_boundary_missing",
    )
    for field, value in expected_boundary.items():
        if boundary.get(field) != value:
            errors.append(f"candidate_reordering_approval_boundary_{field}_not_expected")
    if boundary.get("candidate_reordering_applied") is not False:
        errors.append("candidate_reordering_approval_boundary_candidate_reordering_applied_not_false")
    if boundary.get("selected_action_created") is not False:
        errors.append("candidate_reordering_approval_boundary_selected_action_created_not_false")
    if boundary.get("final_action_created") is not False:
        errors.append("candidate_reordering_approval_boundary_final_action_created_not_false")
    if boundary.get("direct_command_created") is not False:
        errors.append("candidate_reordering_approval_boundary_direct_command_created_not_false")
    if boundary.get("motor_execution_created") is not False:
        errors.append("candidate_reordering_approval_boundary_motor_execution_created_not_false")

    human = _dict(record.get("human_summary"), errors, "human_summary_missing")
    for field in ("what_was_built", "what_it_allows", "what_it_blocks", "plain_result"):
        if not isinstance(human.get(field), str) or not human.get(field).strip():
            errors.append(f"human_summary_{field}_empty")

    blocked = _dict(record.get("blocked_flags"), errors, "blocked_flags_missing")
    for field in BLOCKED_FLAGS:
        if blocked.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")

    return {
        "valid": not errors,
        "error_codes": errors,
        "source_validated": source.get("source_validated") is True,
        "pressure_preview_created": source.get("pressure_preview_created") is True,
        "future_reordering_allowed": boundary.get("candidate_reordering_allowed_in_future_package") is True,
        "future_reordering_blocked": boundary.get("candidate_reordering_allowed_in_future_package") is False,
        "movement_pressure_allowed": source.get("pressure_target") == "continue_body_motor_exploration"
        and boundary.get("candidate_reordering_allowed_in_future_package") is True,
        "reach_pressure_allowed": source.get("pressure_target") == "inspect_or_reach_nearby_item"
        and boundary.get("candidate_reordering_allowed_in_future_package") is True,
        "wall_pressure_blocked": boundary.get("blocked_reason") == "no_pressure_preview_for_candidate_reordering",
        "implementation_blocked": boundary.get("implementation_in_this_package") is False,
        "candidate_reordering_blocked": boundary.get("candidate_reordering_applied") is False
        and blocked.get("candidate_reordering_applied") is False,
        "action_creation_blocked": boundary.get("selected_action_created") is False
        and boundary.get("final_action_created") is False
        and boundary.get("direct_command_created") is False
        and boundary.get("motor_execution_created") is False
        and blocked.get("selected_action_created") is False
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
        "proof_claim_blocked": blocked.get("proof_of_learning_claimed") is False
        and blocked.get("autonomous_learning_claim_allowed") is False
        and blocked.get("autonomous_action_claim_allowed") is False,
    }


def run_body_motor_feedback_gated_candidate_reordering_approval_boundary_minimal_check() -> dict[str, Any]:
    source_result = run_body_motor_feedback_gated_next_action_preview_minimal_check()
    movement_source, wall_source, reach_source = source_result["valid_records"]
    valid_movement = build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(movement_source)
    valid_wall = build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(wall_source)
    valid_reach = build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(reach_source)
    records = [valid_movement, valid_wall, valid_reach, *_invalid_records(valid_movement)]
    validation_results = [
        validate_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(record)
        for record in records
    ]
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
            "boundary_reason": "Approves a future sandbox-only candidate reordering package from settled body-motor feedback pressure.",
        },
        "valid_records": [valid_movement, valid_wall, valid_reach],
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A body-motor feedback-gated candidate reordering approval boundary was added.",
            "what_changed": "Valid movement/reach pressure previews may proceed to a future sandbox-only reordering package.",
            "what_is_blocked": "This package does not reorder candidates, create actions, execute commands, persist feedback, write memory, mutate predictors, or change production behavior.",
            "plain_result": "The action line has a checked permission gate before feedback can affect candidate ordering.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    source_feedback = source["source_feedback_settling"]
    preview = source["candidate_pressure_preview"]
    rollback = source["rollback_preview"]
    return {
        "source_record_type": source["record_type"],
        "source_validated": True,
        "source_feedback_label": source_feedback["feedback_label"],
        "source_final_action": source_feedback["source_final_action"],
        "pressure_preview_created": preview["pressure_preview_created"],
        "pressure_target": preview["pressure_target"],
        "pressure_delta": preview["pressure_delta"],
        "preview_scope": preview["preview_scope"],
        "advisory_only": preview["advisory_only"],
        "candidate_order_before_preview": list(preview["candidate_order_before_preview"]),
        "candidate_order_after_preview": list(preview["candidate_order_after_preview"]),
        "candidate_reordering_applied": preview["candidate_reordering_applied"],
        "selected_action_created": preview["selected_action_created"],
        "final_action_created": preview["final_action_created"],
        "direct_command_created": preview["direct_command_created"],
        "motor_execution_created": preview["motor_execution_created"],
        "blocked_reason": preview["blocked_reason"],
        "audit_recorded": preview["audit_recorded"],
        "rollback_available": rollback["rollback_available"],
        "session_end_restores_baseline": rollback["session_end_restores_baseline"],
    }


def _derive_reordering_boundary(source: dict[str, Any]) -> dict[str, Any]:
    target = source.get("pressure_target")
    allowed = (
        source.get("source_validated") is True
        and source.get("pressure_preview_created") is True
        and source.get("preview_scope") == "same_session_sandbox_only"
        and source.get("advisory_only") is True
        and source.get("candidate_reordering_applied") is False
        and source.get("rollback_available") is True
        and source.get("session_end_restores_baseline") is True
        and target in ALLOWED_PRESSURE_TARGETS
    )
    return {
        "approval_status": "approved_for_future_sandbox_candidate_reordering_package_only"
        if allowed
        else "blocked_no_pressure_preview_for_candidate_reordering",
        "approval_scope": "future_sandbox_only_candidate_reordering_from_body_motor_feedback_pressure",
        "pressure_preview_required": True,
        "pressure_preview_checked": allowed,
        "pressure_target": target if allowed else None,
        "candidate_reordering_allowed_in_future_package": allowed,
        "allowed_next_package": ALLOWED_NEXT_PACKAGE if allowed else None,
        "blocked_reason": None if allowed else "no_pressure_preview_for_candidate_reordering",
        "implementation_in_this_package": False,
        "candidate_reordering_applied": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "motor_execution_created": False,
        "future_selected_action_requires_separate_boundary": True if allowed else False,
        "future_final_action_requires_separate_boundary": True if allowed else False,
        "future_direct_command_requires_separate_boundary": True if allowed else False,
        "future_memory_write_requires_separate_boundary": True if allowed else False,
        "future_retention_requires_separate_boundary": True if allowed else False,
        "future_predictor_influence_requires_separate_boundary": True if allowed else False,
        "future_production_promotion_requires_separate_boundary": True if allowed else False,
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_next_action_preview_not_validated")
    if source.get("source_record_type") != "body_motor_feedback_gated_next_action_preview_minimal":
        errors.append("source_next_action_preview_record_type_not_expected")
    if source.get("pressure_target") is not None and source.get("pressure_target") not in ALLOWED_PRESSURE_TARGETS:
        errors.append("source_next_action_preview_pressure_target_invalid")
    if source.get("pressure_preview_created") is True and source.get("preview_scope") != "same_session_sandbox_only":
        errors.append("source_next_action_preview_scope_not_same_session_sandbox_only")
    if source.get("advisory_only") is not True:
        errors.append("source_next_action_preview_not_advisory_only")
    if source.get("candidate_reordering_applied") is not False:
        errors.append("source_next_action_preview_candidate_reordering_already_applied")
    if source.get("selected_action_created") is not False:
        errors.append("source_next_action_preview_selected_action_created")
    if source.get("final_action_created") is not False:
        errors.append("source_next_action_preview_final_action_created")
    if source.get("direct_command_created") is not False:
        errors.append("source_next_action_preview_direct_command_created")
    if source.get("motor_execution_created") is not False:
        errors.append("source_next_action_preview_motor_execution_created")
    if source.get("audit_recorded") is not True:
        errors.append("source_next_action_preview_audit_not_recorded")
    if source.get("rollback_available") is not True:
        errors.append("source_next_action_preview_rollback_not_available")
    if source.get("session_end_restores_baseline") is not True:
        errors.append("source_next_action_preview_session_end_does_not_restore_baseline")


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def add(name: str, mutator) -> None:
        record = deepcopy(valid_record)
        mutator(record)
        record["invalid_case"] = name
        cases.append(record)

    add("wrong_record_type", lambda r: r.__setitem__("record_type", "candidate_reordering_boundary"))
    add("source_not_validated", lambda r: r["source_next_action_preview"].__setitem__("source_validated", False))
    add("source_bad_target", lambda r: r["source_next_action_preview"].__setitem__("pressure_target", "wander"))
    add("source_wrong_scope", lambda r: r["source_next_action_preview"].__setitem__("preview_scope", "production"))
    add("source_not_advisory", lambda r: r["source_next_action_preview"].__setitem__("advisory_only", False))
    add("source_reordering_already_applied", lambda r: r["source_next_action_preview"].__setitem__("candidate_reordering_applied", True))
    add("source_selected_action_created", lambda r: r["source_next_action_preview"].__setitem__("selected_action_created", True))
    add("source_final_action_created", lambda r: r["source_next_action_preview"].__setitem__("final_action_created", True))
    add("source_direct_command_created", lambda r: r["source_next_action_preview"].__setitem__("direct_command_created", True))
    add("source_motor_execution_created", lambda r: r["source_next_action_preview"].__setitem__("motor_execution_created", True))
    add("audit_missing", lambda r: r["source_next_action_preview"].__setitem__("audit_recorded", False))
    add("rollback_missing", lambda r: r["source_next_action_preview"].__setitem__("rollback_available", False))
    add("session_restore_false", lambda r: r["source_next_action_preview"].__setitem__("session_end_restores_baseline", False))
    add("wrong_status", lambda r: r["candidate_reordering_approval_boundary"].__setitem__("approval_status", "approved"))
    add("allowed_false", lambda r: r["candidate_reordering_approval_boundary"].__setitem__("candidate_reordering_allowed_in_future_package", False))
    add("wrong_next_package", lambda r: r["candidate_reordering_approval_boundary"].__setitem__("allowed_next_package", "Candidate Reordering Minimal v0"))
    add("implementation_true", lambda r: r["candidate_reordering_approval_boundary"].__setitem__("implementation_in_this_package", True))
    add("candidate_reordering_applied", lambda r: r["candidate_reordering_approval_boundary"].__setitem__("candidate_reordering_applied", True))
    add("selected_action_created", lambda r: r["candidate_reordering_approval_boundary"].__setitem__("selected_action_created", True))
    add("final_action_created", lambda r: r["candidate_reordering_approval_boundary"].__setitem__("final_action_created", True))
    add("direct_command_created", lambda r: r["candidate_reordering_approval_boundary"].__setitem__("direct_command_created", True))
    add("motor_execution_created", lambda r: r["candidate_reordering_approval_boundary"].__setitem__("motor_execution_created", True))
    add("future_selected_boundary_false", lambda r: r["candidate_reordering_approval_boundary"].__setitem__("future_selected_action_requires_separate_boundary", False))
    add("blocked_reordering", lambda r: r["blocked_flags"].__setitem__("candidate_reordering_applied", True))
    add("blocked_selected_action", lambda r: r["blocked_flags"].__setitem__("selected_action_created", True))
    add("blocked_direct_command", lambda r: r["blocked_flags"].__setitem__("direct_command_created", True))
    add("memory_write", lambda r: r["blocked_flags"].__setitem__("memory_write_performed", True))
    add("retention_write", lambda r: r["blocked_flags"].__setitem__("retention_write_performed", True))
    add("predictor_mutation", lambda r: r["blocked_flags"].__setitem__("predictor_mutation_performed", True))
    add("persistent_state", lambda r: r["blocked_flags"].__setitem__("persistent_body_schema_written", True))
    add("production_behavior", lambda r: r["blocked_flags"].__setitem__("production_behavior_changed", True))
    add("semantic_vision", lambda r: r["blocked_flags"].__setitem__("semantic_vision", True))
    add("proof_claim", lambda r: r["blocked_flags"].__setitem__("proof_of_learning_claimed", True))
    add("empty_human_summary", lambda r: r["human_summary"].__setitem__("plain_result", ""))
    return cases


def _summary(results: list[dict[str, Any]]) -> dict[str, int]:
    valid_results = [result for result in results if result["valid"]]
    return {
        "candidate_reordering_approval_boundary_result_count": len(results),
        "valid_candidate_reordering_approval_boundary_count": len(valid_results),
        "invalid_candidate_reordering_approval_boundary_count": len(results) - len(valid_results),
        "source_validated_count": _count_valid(valid_results, "source_validated"),
        "pressure_preview_created_count": _count_valid(valid_results, "pressure_preview_created"),
        "future_reordering_allowed_count": _count_valid(valid_results, "future_reordering_allowed"),
        "future_reordering_blocked_count": _count_valid(valid_results, "future_reordering_blocked"),
        "movement_pressure_allowed_count": _count_valid(valid_results, "movement_pressure_allowed"),
        "reach_pressure_allowed_count": _count_valid(valid_results, "reach_pressure_allowed"),
        "wall_pressure_blocked_count": _count_valid(valid_results, "wall_pressure_blocked"),
        "implementation_blocked_count": _count_valid(valid_results, "implementation_blocked"),
        "candidate_reordering_blocked_count": _count_valid(valid_results, "candidate_reordering_blocked"),
        "action_creation_blocked_count": _count_valid(valid_results, "action_creation_blocked"),
        "persistent_feedback_blocked_count": _count_valid(valid_results, "persistent_feedback_blocked"),
        "memory_write_blocked_count": _count_valid(valid_results, "memory_write_blocked"),
        "retention_blocked_count": _count_valid(valid_results, "retention_blocked"),
        "predictor_mutation_blocked_count": _count_valid(valid_results, "predictor_mutation_blocked"),
        "persistent_state_blocked_count": _count_valid(valid_results, "persistent_state_blocked"),
        "production_behavior_blocked_count": _count_valid(valid_results, "production_behavior_blocked"),
        "semantic_vision_blocked_count": _count_valid(valid_results, "semantic_vision_blocked"),
        "proof_claim_blocked_count": _count_valid(valid_results, "proof_claim_blocked"),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["candidate_reordering_approval_boundary_result_count"] == 37
        and summary["valid_candidate_reordering_approval_boundary_count"] == 3
        and summary["invalid_candidate_reordering_approval_boundary_count"] == 34
        and summary["source_validated_count"] == 3
        and summary["pressure_preview_created_count"] == 2
        and summary["future_reordering_allowed_count"] == 2
        and summary["future_reordering_blocked_count"] == 1
        and summary["movement_pressure_allowed_count"] == 1
        and summary["reach_pressure_allowed_count"] == 1
        and summary["wall_pressure_blocked_count"] == 1
        and summary["implementation_blocked_count"] == 3
        and summary["candidate_reordering_blocked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["persistent_feedback_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["retention_blocked_count"] == 3
        and summary["predictor_mutation_blocked_count"] == 3
        and summary["persistent_state_blocked_count"] == 3
        and summary["production_behavior_blocked_count"] == 3
        and summary["semantic_vision_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
    )


def _dict(value: Any, errors: list[str], error_code: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(error_code)
        return {}
    return value


def _count_valid(results: list[dict[str, Any]], field: str) -> int:
    return sum(1 for result in results if result.get(field) is True)
