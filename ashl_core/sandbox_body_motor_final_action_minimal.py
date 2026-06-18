"""Create sandbox-only final_action from approved body-motor selected_action."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_body_motor_final_action_approval_boundary_minimal import (
    build_sandbox_body_motor_final_action_approval_boundary_record,
    run_sandbox_body_motor_final_action_approval_boundary_minimal_check,
    validate_sandbox_body_motor_final_action_approval_boundary_record,
)


COMMAND = "run-sandbox-body-motor-final-action-minimal-check"
FLOW = "sandbox_body_motor_final_action_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxBodyMotorFinalAction-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b116"
BOUNDARY_INDEX_AFTER = "2026-06-09-b117"

VALID_FINAL_ACTIONS = ("step_forward", "reach_front")
REQUIRED_BLOCKED_FLAGS = (
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


def build_sandbox_body_motor_final_action_record(
    approval_boundary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = deepcopy(approval_boundary) if approval_boundary is not None else (
        build_sandbox_body_motor_final_action_approval_boundary_record()
    )
    source_validation = validate_sandbox_body_motor_final_action_approval_boundary_record(source)
    if not source_validation["valid"]:
        raise ValueError("approval_boundary must validate before body-motor final_action")

    source_summary = _source_summary(source)
    final_action = _derive_final_action(source_summary)
    return {
        "record_type": "sandbox_body_motor_final_action_minimal",
        "record_version": "v0",
        "final_action_status": "completed_sandbox_body_motor_final_action",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_final_action_approval_boundary": source_summary,
        "final_action_result": final_action,
        "human_summary": {
            "what_was_built": "A sandbox-only final_action record was created from an approved body-motor selected_action.",
            "what_can_be_finalized": "Approved step_forward and reach_front selected_action records can become final_action records.",
            "what_is_blocked": "No-selected-action cases remain blocked, and direct command, motor execution, pathfinding, persistence, production behavior, and proof claims remain blocked.",
            "plain_result": "Qingyin can now finalize a body-motor sandbox action, but still cannot command or execute it.",
        },
        "blocked_flags": {field: False for field in REQUIRED_BLOCKED_FLAGS},
    }


def validate_sandbox_body_motor_final_action_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "sandbox_body_motor_final_action_minimal",
        "record_version": "v0",
        "final_action_status": "completed_sandbox_body_motor_final_action",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _dict(record.get("source_final_action_approval_boundary"), errors, "source_final_action_approval_boundary_missing")
    _validate_source(source, errors)

    final_action = _dict(record.get("final_action_result"), errors, "final_action_result_missing")
    expected_final_action = _derive_final_action(source)
    for field, value in expected_final_action.items():
        if final_action.get(field) != value:
            errors.append(f"final_action_result_{field}_not_expected")
    if final_action.get("final_action") is not None and final_action.get("final_action") not in VALID_FINAL_ACTIONS:
        errors.append("final_action_result_final_action_invalid")
    if final_action.get("direct_command_created") is not False:
        errors.append("final_action_result_direct_command_created_not_false")
    if final_action.get("motor_action_executed") is not False:
        errors.append("final_action_result_motor_action_executed_not_false")

    human = _dict(record.get("human_summary"), errors, "human_summary_missing")
    for field in ("what_was_built", "what_can_be_finalized", "what_is_blocked", "plain_result"):
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
        "approval_checked": source.get("final_action_allowed_in_future_package") is True,
        "approval_blocked": source.get("final_action_allowed_in_future_package") is False,
        "final_action_created": final_action.get("final_action_created") is True,
        "final_action_blocked": final_action.get("final_action_created") is False,
        "step_forward_final_action": final_action.get("final_action") == "step_forward",
        "reach_front_final_action": final_action.get("final_action") == "reach_front",
        "no_final_action_blocked": final_action.get("blocked_reason") == "final_action_not_approved",
        "sandbox_only": final_action.get("final_action_scope") == "sandbox_only",
        "source_preserved": final_action.get("final_action_source") == "body_motor_selected_action_approval_boundary",
        "direct_command_blocked": final_action.get("direct_command_created") is False
        and blocked.get("direct_command_created") is False,
        "motor_execution_blocked": final_action.get("motor_action_executed") is False
        and blocked.get("motor_action_executed") is False,
        "pathfinding_blocked": blocked.get("pathfinding_used") is False,
        "memory_write_blocked": blocked.get("memory_write_performed") is False,
        "predictor_mutation_blocked": blocked.get("predictor_mutation_performed") is False,
        "persistent_body_schema_blocked": blocked.get("persistent_body_schema_written") is False,
        "production_behavior_blocked": blocked.get("production_behavior_changed") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claimed") is False,
    }


def run_sandbox_body_motor_final_action_minimal_check() -> dict[str, Any]:
    source_result = run_sandbox_body_motor_final_action_approval_boundary_minimal_check()
    empty_source, wall_source, item_source = source_result["valid_records"]
    valid_empty = build_sandbox_body_motor_final_action_record(empty_source)
    valid_wall = build_sandbox_body_motor_final_action_record(wall_source)
    valid_item = build_sandbox_body_motor_final_action_record(item_source)
    records = [valid_empty, valid_wall, valid_item, *_invalid_records(valid_empty)]
    validation_results = [validate_sandbox_body_motor_final_action_record(record) for record in records]
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
            "boundary_reason": "Creates sandbox-only final_action records from approved body-motor selected_actions.",
        },
        "valid_records": [valid_empty, valid_wall, valid_item],
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A body-motor sandbox final_action layer was added.",
            "what_changed": "Approved body-motor selected_actions can now become sandbox-only final_action records.",
            "what_is_blocked": "The layer does not create direct command, motor execution, pathfinding, production behavior, persistence, memory write, predictor mutation, or proof claims.",
            "plain_result": "The body-motor action line now reaches final_action while stopping before command and execution.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    boundary = source["final_action_approval_boundary"]
    selected_source = source["source_selected_action_bridge"]
    return {
        "source_record_type": source["record_type"],
        "source_validated": True,
        "body_id": selected_source["body_id"],
        "body_scope": selected_source["body_scope"],
        "front_symbol": selected_source["front_symbol"],
        "selected_action": boundary["selected_action"],
        "final_action_allowed_in_future_package": boundary["final_action_allowed_in_future_package"],
        "allowed_next_package": boundary["allowed_next_package"],
        "blocked_reason": boundary["blocked_reason"],
        "audit_recorded": boundary["audit_recorded"],
        "rollback_available": boundary["rollback_available"],
    }


def _derive_final_action(source: dict[str, Any]) -> dict[str, Any]:
    selected_action = source.get("selected_action")
    allowed = source.get("final_action_allowed_in_future_package") is True and selected_action in VALID_FINAL_ACTIONS
    return {
        "final_action_created": allowed,
        "final_action": selected_action if allowed else None,
        "final_action_scope": "sandbox_only" if allowed else None,
        "final_action_source": "body_motor_selected_action_approval_boundary" if allowed else None,
        "final_action_reason": "approved_body_motor_selected_action" if allowed else None,
        "blocked_reason": None if allowed else "final_action_not_approved",
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
        errors.append("source_final_action_approval_boundary_not_validated")
    if source.get("source_record_type") != "sandbox_body_motor_final_action_approval_boundary_minimal":
        errors.append("source_final_action_approval_boundary_record_type_not_expected")
    if source.get("body_id") != "qingyin_minimal_grid_body_v0":
        errors.append("source_final_action_approval_boundary_body_id_not_expected")
    if source.get("body_scope") != "sandbox_only":
        errors.append("source_final_action_approval_boundary_body_scope_not_expected")
    if source.get("selected_action") is not None and source.get("selected_action") not in VALID_FINAL_ACTIONS:
        errors.append("source_final_action_approval_boundary_selected_action_invalid")
    if source.get("final_action_allowed_in_future_package") is True and source.get("allowed_next_package") != "Sandbox Body-Motor Final Action Minimal v0":
        errors.append("source_final_action_approval_boundary_next_package_not_expected")
    if source.get("audit_recorded") is not True:
        errors.append("source_final_action_approval_boundary_audit_not_recorded")
    if source.get("rollback_available") is not True:
        errors.append("source_final_action_approval_boundary_rollback_not_available")


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def add(name: str, mutator) -> None:
        record = deepcopy(valid_record)
        mutator(record)
        record["invalid_case"] = name
        cases.append(record)

    add("wrong_record_type", lambda r: r.__setitem__("record_type", "sandbox_final_action"))
    add("source_not_validated", lambda r: r["source_final_action_approval_boundary"].__setitem__("source_validated", False))
    add("source_bad_action", lambda r: r["source_final_action_approval_boundary"].__setitem__("selected_action", "jump"))
    add("source_wrong_next_package", lambda r: r["source_final_action_approval_boundary"].__setitem__("allowed_next_package", "Other Package"))
    add("audit_missing", lambda r: r["source_final_action_approval_boundary"].__setitem__("audit_recorded", False))
    add("rollback_missing", lambda r: r["source_final_action_approval_boundary"].__setitem__("rollback_available", False))
    add("final_action_created_false", lambda r: r["final_action_result"].__setitem__("final_action_created", False))
    add("final_action_missing", lambda r: r["final_action_result"].__setitem__("final_action", None))
    add("wrong_final_action", lambda r: r["final_action_result"].__setitem__("final_action", "reach_front"))
    add("invalid_final_action", lambda r: r["final_action_result"].__setitem__("final_action", "jump"))
    add("wrong_scope", lambda r: r["final_action_result"].__setitem__("final_action_scope", "production"))
    add("wrong_source", lambda r: r["final_action_result"].__setitem__("final_action_source", "autonomous_selector"))
    add("direct_command_created", lambda r: r["final_action_result"].__setitem__("direct_command_created", True))
    add("motor_action_executed", lambda r: r["final_action_result"].__setitem__("motor_action_executed", True))
    add("future_direct_boundary_false", lambda r: r["final_action_result"].__setitem__("future_direct_command_requires_separate_boundary", False))
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
        "final_action_result_count": len(results),
        "valid_final_action_count": len(valid_results),
        "invalid_final_action_count": len(results) - len(valid_results),
        "source_validated_count": _count_valid(valid_results, "source_validated"),
        "approval_checked_count": _count_valid(valid_results, "approval_checked"),
        "approval_blocked_count": _count_valid(valid_results, "approval_blocked"),
        "final_action_created_count": _count_valid(valid_results, "final_action_created"),
        "final_action_blocked_count": _count_valid(valid_results, "final_action_blocked"),
        "step_forward_final_action_count": _count_valid(valid_results, "step_forward_final_action"),
        "reach_front_final_action_count": _count_valid(valid_results, "reach_front_final_action"),
        "no_final_action_blocked_count": _count_valid(valid_results, "no_final_action_blocked"),
        "sandbox_only_count": _count_valid(valid_results, "sandbox_only"),
        "source_preserved_count": _count_valid(valid_results, "source_preserved"),
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
        summary["final_action_result_count"] == 29
        and summary["valid_final_action_count"] == 3
        and summary["invalid_final_action_count"] == 26
        and summary["source_validated_count"] == 3
        and summary["approval_checked_count"] == 2
        and summary["approval_blocked_count"] == 1
        and summary["final_action_created_count"] == 2
        and summary["final_action_blocked_count"] == 1
        and summary["step_forward_final_action_count"] == 1
        and summary["reach_front_final_action_count"] == 1
        and summary["no_final_action_blocked_count"] == 1
        and summary["sandbox_only_count"] == 2
        and summary["source_preserved_count"] == 2
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
