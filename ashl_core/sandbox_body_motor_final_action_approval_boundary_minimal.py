"""Approval boundary for future final_action from body-motor selected_action."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_motor_intent_to_selected_action_bridge_minimal import (
    build_sandbox_motor_intent_to_selected_action_bridge_record,
    run_sandbox_motor_intent_to_selected_action_bridge_minimal_check,
    validate_sandbox_motor_intent_to_selected_action_bridge_record,
)


COMMAND = "run-sandbox-body-motor-final-action-approval-boundary-minimal-check"
FLOW = "sandbox_body_motor_final_action_approval_boundary_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxBodyMotorFinalActionApprovalBoundary-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b115"
BOUNDARY_INDEX_AFTER = "2026-06-09-b116"

VALID_SELECTED_ACTIONS = ("step_forward", "reach_front")
REQUIRED_BLOCKED_FLAGS = (
    "final_action_created",
    "direct_command_created",
    "motor_action_executed",
    "pathfinding_used",
    "route_planner_added",
    "goal_seeking_added",
    "production_behavior_changed",
    "real_navigation_changed",
    "ui_behavior_changed",
    "memory_write_performed",
    "retention_write_performed",
    "predictor_mutation_performed",
    "persistent_body_schema_written",
    "semantic_vision",
    "object_recognition",
    "proof_of_learning_claimed",
)


def build_sandbox_body_motor_final_action_approval_boundary_record(
    selected_action_bridge: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = deepcopy(selected_action_bridge) if selected_action_bridge is not None else (
        build_sandbox_motor_intent_to_selected_action_bridge_record()
    )
    source_validation = validate_sandbox_motor_intent_to_selected_action_bridge_record(source)
    if not source_validation["valid"]:
        raise ValueError("selected_action_bridge must validate before final_action approval boundary")

    source_summary = _source_summary(source)
    boundary = _derive_approval_boundary(source_summary)
    return {
        "record_type": "sandbox_body_motor_final_action_approval_boundary_minimal",
        "record_version": "v0",
        "approval_boundary_status": "completed_body_motor_final_action_approval_boundary",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_selected_action_bridge": source_summary,
        "final_action_approval_boundary": boundary,
        "human_summary": {
            "what_was_built": "A final_action approval boundary for body-motor selected_action records was created.",
            "what_it_allows": "Ready sandbox selected_action records may proceed to a future final_action package only.",
            "what_it_blocks": "No-intent/no-selected-action cases cannot proceed, and this package creates no final_action, direct command, or execution.",
            "plain_result": "The body-motor action line is approved up to the next final_action package boundary, but does not act yet.",
        },
        "blocked_flags": {field: False for field in REQUIRED_BLOCKED_FLAGS},
    }


def validate_sandbox_body_motor_final_action_approval_boundary_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "sandbox_body_motor_final_action_approval_boundary_minimal",
        "record_version": "v0",
        "approval_boundary_status": "completed_body_motor_final_action_approval_boundary",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _dict(record.get("source_selected_action_bridge"), errors, "source_selected_action_bridge_missing")
    _validate_source(source, errors)

    boundary = _dict(record.get("final_action_approval_boundary"), errors, "final_action_approval_boundary_missing")
    expected_boundary = _derive_approval_boundary(source)
    for field, value in expected_boundary.items():
        if boundary.get(field) != value:
            errors.append(f"final_action_approval_boundary_{field}_not_expected")
    if boundary.get("final_action_created") is not False:
        errors.append("final_action_approval_boundary_final_action_created_not_false")
    if boundary.get("direct_command_created") is not False:
        errors.append("final_action_approval_boundary_direct_command_created_not_false")
    if boundary.get("motor_action_executed") is not False:
        errors.append("final_action_approval_boundary_motor_action_executed_not_false")

    human = _dict(record.get("human_summary"), errors, "human_summary_missing")
    for field in ("what_was_built", "what_it_allows", "what_it_blocks", "plain_result"):
        if not isinstance(human.get(field), str) or not human.get(field).strip():
            errors.append(f"human_summary_{field}_empty")

    blocked = _dict(record.get("blocked_flags"), errors, "blocked_flags_missing")
    for field in REQUIRED_BLOCKED_FLAGS:
        if blocked.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")

    return {
        "valid": not errors,
        "error_codes": errors,
        "source_validated": source.get("source_validated") is True,
        "selected_action_source_checked": source.get("selected_action_source") == "sandbox_selected_motor_intent_preview",
        "future_final_action_allowed": boundary.get("final_action_allowed_in_future_package") is True,
        "future_final_action_blocked": boundary.get("final_action_allowed_in_future_package") is False,
        "step_forward_allowed": source.get("selected_action") == "step_forward"
        and boundary.get("final_action_allowed_in_future_package") is True,
        "reach_front_allowed": source.get("selected_action") == "reach_front"
        and boundary.get("final_action_allowed_in_future_package") is True,
        "no_selected_action_blocked": boundary.get("blocked_reason") == "no_selected_action_for_final_action",
        "final_action_blocked": boundary.get("final_action_created") is False
        and blocked.get("final_action_created") is False,
        "direct_command_blocked": boundary.get("direct_command_created") is False
        and blocked.get("direct_command_created") is False,
        "motor_execution_blocked": boundary.get("motor_action_executed") is False
        and blocked.get("motor_action_executed") is False,
        "pathfinding_blocked": blocked.get("pathfinding_used") is False,
        "memory_write_blocked": blocked.get("memory_write_performed") is False,
        "predictor_mutation_blocked": blocked.get("predictor_mutation_performed") is False,
        "persistent_body_schema_blocked": blocked.get("persistent_body_schema_written") is False,
        "production_behavior_blocked": blocked.get("production_behavior_changed") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claimed") is False,
    }


def run_sandbox_body_motor_final_action_approval_boundary_minimal_check() -> dict[str, Any]:
    source_result = run_sandbox_motor_intent_to_selected_action_bridge_minimal_check()
    empty_source, wall_source, item_source = source_result["valid_records"]
    valid_empty = build_sandbox_body_motor_final_action_approval_boundary_record(empty_source)
    valid_wall = build_sandbox_body_motor_final_action_approval_boundary_record(wall_source)
    valid_item = build_sandbox_body_motor_final_action_approval_boundary_record(item_source)
    records = [valid_empty, valid_wall, valid_item, *_invalid_records(valid_empty)]
    validation_results = [validate_sandbox_body_motor_final_action_approval_boundary_record(record) for record in records]
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
            "boundary_reason": "Approves future sandbox final_action package for body-motor selected_action records.",
        },
        "valid_records": [valid_empty, valid_wall, valid_item],
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A body-motor final_action approval boundary was added.",
            "what_changed": "Ready body-motor selected_action records may proceed to a future final_action package.",
            "what_is_blocked": "This package creates no final_action, direct command, motor execution, pathfinding, production behavior, persistence, memory write, predictor mutation, or proof claims.",
            "plain_result": "The body-motor action line has a checked permission gate before final_action creation.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    selected = source["selected_action_bridge_result"]
    source_preview = source["source_motor_intent_preview"]
    return {
        "source_record_type": source["record_type"],
        "source_validated": True,
        "body_id": source_preview["body_id"],
        "body_scope": source_preview["body_scope"],
        "front_symbol": source_preview["front_symbol"],
        "selected_action_created": selected["selected_action_created"],
        "selected_action": selected["selected_action"],
        "selected_action_scope": selected["selected_action_scope"],
        "selected_action_source": selected["selected_action_source"],
        "blocked_reason": selected["blocked_reason"],
        "audit_recorded": selected["audit_recorded"],
        "rollback_available": selected["rollback_available"],
    }


def _derive_approval_boundary(source: dict[str, Any]) -> dict[str, Any]:
    selected_action = source.get("selected_action")
    allowed = (
        source.get("selected_action_created") is True
        and source.get("selected_action_scope") == "sandbox_only"
        and selected_action in VALID_SELECTED_ACTIONS
    )
    return {
        "approval_status": "approved_for_future_sandbox_final_action_package_only"
        if allowed
        else "blocked_no_selected_action_for_final_action",
        "approval_scope": "future_sandbox_only_final_action_from_body_motor_selected_action",
        "selected_action_required": True,
        "selected_action_checked": allowed,
        "selected_action": selected_action if allowed else None,
        "final_action_allowed_in_future_package": allowed,
        "allowed_next_package": "Sandbox Body-Motor Final Action Minimal v0" if allowed else None,
        "blocked_reason": None if allowed else "no_selected_action_for_final_action",
        "implementation_in_this_package": False,
        "final_action_created": False,
        "direct_command_created": False,
        "motor_action_executed": False,
        "future_direct_command_requires_separate_boundary": True if allowed else False,
        "future_memory_write_requires_separate_boundary": True if allowed else False,
        "future_retention_requires_separate_boundary": True if allowed else False,
        "future_predictor_influence_requires_separate_boundary": True if allowed else False,
        "future_production_promotion_requires_separate_boundary": True if allowed else False,
        "audit_recorded": True,
        "rollback_available": True,
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_selected_action_bridge_not_validated")
    if source.get("source_record_type") != "sandbox_motor_intent_to_selected_action_bridge_minimal":
        errors.append("source_selected_action_bridge_record_type_not_expected")
    if source.get("body_id") != "qingyin_minimal_grid_body_v0":
        errors.append("source_selected_action_bridge_body_id_not_expected")
    if source.get("body_scope") != "sandbox_only":
        errors.append("source_selected_action_bridge_body_scope_not_expected")
    if source.get("selected_action") is not None and source.get("selected_action") not in VALID_SELECTED_ACTIONS:
        errors.append("source_selected_action_bridge_selected_action_invalid")
    if source.get("selected_action_created") is True and source.get("selected_action_scope") != "sandbox_only":
        errors.append("source_selected_action_bridge_scope_not_sandbox_only")
    if source.get("selected_action_created") is True and source.get("selected_action_source") != "sandbox_selected_motor_intent_preview":
        errors.append("source_selected_action_bridge_source_not_expected")
    if source.get("audit_recorded") is not True:
        errors.append("source_selected_action_bridge_audit_not_recorded")
    if source.get("rollback_available") is not True:
        errors.append("source_selected_action_bridge_rollback_not_available")


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def add(name: str, mutator) -> None:
        record = deepcopy(valid_record)
        mutator(record)
        record["invalid_case"] = name
        cases.append(record)

    add("wrong_record_type", lambda r: r.__setitem__("record_type", "sandbox_final_action_approval_boundary"))
    add("source_not_validated", lambda r: r["source_selected_action_bridge"].__setitem__("source_validated", False))
    add("source_bad_action", lambda r: r["source_selected_action_bridge"].__setitem__("selected_action", "jump"))
    add("source_wrong_scope", lambda r: r["source_selected_action_bridge"].__setitem__("selected_action_scope", "production"))
    add("source_wrong_source", lambda r: r["source_selected_action_bridge"].__setitem__("selected_action_source", "autonomous_selector"))
    add("audit_missing", lambda r: r["source_selected_action_bridge"].__setitem__("audit_recorded", False))
    add("rollback_missing", lambda r: r["source_selected_action_bridge"].__setitem__("rollback_available", False))
    add("wrong_status", lambda r: r["final_action_approval_boundary"].__setitem__("approval_status", "approved"))
    add("allowed_false", lambda r: r["final_action_approval_boundary"].__setitem__("final_action_allowed_in_future_package", False))
    add("selected_action_missing", lambda r: r["final_action_approval_boundary"].__setitem__("selected_action", None))
    add("wrong_next_package", lambda r: r["final_action_approval_boundary"].__setitem__("allowed_next_package", "Sandbox Final Action Minimal v0"))
    add("implementation_true", lambda r: r["final_action_approval_boundary"].__setitem__("implementation_in_this_package", True))
    add("final_action_created", lambda r: r["final_action_approval_boundary"].__setitem__("final_action_created", True))
    add("direct_command_created", lambda r: r["final_action_approval_boundary"].__setitem__("direct_command_created", True))
    add("motor_action_executed", lambda r: r["final_action_approval_boundary"].__setitem__("motor_action_executed", True))
    add("future_direct_boundary_false", lambda r: r["final_action_approval_boundary"].__setitem__("future_direct_command_requires_separate_boundary", False))
    add("blocked_final_action", lambda r: r["blocked_flags"].__setitem__("final_action_created", True))
    add("blocked_direct_command", lambda r: r["blocked_flags"].__setitem__("direct_command_created", True))
    add("blocked_motor_execution", lambda r: r["blocked_flags"].__setitem__("motor_action_executed", True))
    add("pathfinding_used", lambda r: r["blocked_flags"].__setitem__("pathfinding_used", True))
    add("memory_write", lambda r: r["blocked_flags"].__setitem__("memory_write_performed", True))
    add("retention_write", lambda r: r["blocked_flags"].__setitem__("retention_write_performed", True))
    add("predictor_mutation", lambda r: r["blocked_flags"].__setitem__("predictor_mutation_performed", True))
    add("persistent_body_schema", lambda r: r["blocked_flags"].__setitem__("persistent_body_schema_written", True))
    add("production_behavior", lambda r: r["blocked_flags"].__setitem__("production_behavior_changed", True))
    add("semantic_vision", lambda r: r["blocked_flags"].__setitem__("semantic_vision", True))
    add("proof_claim", lambda r: r["blocked_flags"].__setitem__("proof_of_learning_claimed", True))
    add("empty_human_summary", lambda r: r["human_summary"].__setitem__("plain_result", ""))
    return cases


def _summary(results: list[dict[str, Any]]) -> dict[str, int]:
    valid_results = [result for result in results if result["valid"]]
    return {
        "final_action_approval_boundary_result_count": len(results),
        "valid_final_action_approval_boundary_count": len(valid_results),
        "invalid_final_action_approval_boundary_count": len(results) - len(valid_results),
        "source_validated_count": _count_valid(valid_results, "source_validated"),
        "selected_action_source_checked_count": _count_valid(valid_results, "selected_action_source_checked"),
        "future_final_action_allowed_count": _count_valid(valid_results, "future_final_action_allowed"),
        "future_final_action_blocked_count": _count_valid(valid_results, "future_final_action_blocked"),
        "step_forward_allowed_count": _count_valid(valid_results, "step_forward_allowed"),
        "reach_front_allowed_count": _count_valid(valid_results, "reach_front_allowed"),
        "no_selected_action_blocked_count": _count_valid(valid_results, "no_selected_action_blocked"),
        "final_action_blocked_count": _count_valid(valid_results, "final_action_blocked"),
        "direct_command_blocked_count": _count_valid(valid_results, "direct_command_blocked"),
        "motor_execution_blocked_count": _count_valid(valid_results, "motor_execution_blocked"),
        "pathfinding_blocked_count": _count_valid(valid_results, "pathfinding_blocked"),
        "memory_write_blocked_count": _count_valid(valid_results, "memory_write_blocked"),
        "predictor_mutation_blocked_count": _count_valid(valid_results, "predictor_mutation_blocked"),
        "persistent_body_schema_blocked_count": _count_valid(valid_results, "persistent_body_schema_blocked"),
        "production_behavior_blocked_count": _count_valid(valid_results, "production_behavior_blocked"),
        "proof_claim_blocked_count": _count_valid(valid_results, "proof_claim_blocked"),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["final_action_approval_boundary_result_count"] == 31
        and summary["valid_final_action_approval_boundary_count"] == 3
        and summary["invalid_final_action_approval_boundary_count"] == 28
        and summary["source_validated_count"] == 3
        and summary["selected_action_source_checked_count"] == 2
        and summary["future_final_action_allowed_count"] == 2
        and summary["future_final_action_blocked_count"] == 1
        and summary["step_forward_allowed_count"] == 1
        and summary["reach_front_allowed_count"] == 1
        and summary["no_selected_action_blocked_count"] == 1
        and summary["final_action_blocked_count"] == 3
        and summary["direct_command_blocked_count"] == 3
        and summary["motor_execution_blocked_count"] == 3
        and summary["pathfinding_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_mutation_blocked_count"] == 3
        and summary["persistent_body_schema_blocked_count"] == 3
        and summary["production_behavior_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
    )


def _dict(value: Any, errors: list[str], error_code: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(error_code)
        return {}
    return value


def _count_valid(results: list[dict[str, Any]], field: str) -> int:
    return sum(1 for result in results if result.get(field) is True)
