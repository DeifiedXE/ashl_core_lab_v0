"""Bridge sandbox motor intent previews into sandbox-only selected_action records."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_motor_intent_preview_minimal import (
    build_sandbox_motor_intent_preview_record,
    run_sandbox_motor_intent_preview_minimal_check,
    validate_sandbox_motor_intent_preview_record,
)


COMMAND = "run-sandbox-motor-intent-to-selected-action-bridge-minimal-check"
FLOW = "sandbox_motor_intent_to_selected_action_bridge_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxMotorIntentToSelectedActionBridge-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b114"
BOUNDARY_INDEX_AFTER = "2026-06-09-b115"

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


def build_sandbox_motor_intent_to_selected_action_bridge_record(
    motor_intent_preview: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = deepcopy(motor_intent_preview) if motor_intent_preview is not None else (
        build_sandbox_motor_intent_preview_record()
    )
    source_validation = validate_sandbox_motor_intent_preview_record(source)
    if not source_validation["valid"]:
        raise ValueError("motor_intent_preview must validate before selected_action bridge")

    source_summary = _source_summary(source)
    selected_action = _derive_selected_action(source_summary)
    return {
        "record_type": "sandbox_motor_intent_to_selected_action_bridge_minimal",
        "record_version": "v0",
        "bridge_status": "completed_sandbox_motor_intent_to_selected_action_bridge",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_motor_intent_preview": source_summary,
        "selected_action_bridge_result": selected_action,
        "human_summary": {
            "what_was_built": "A sandbox-only bridge from selected_motor_intent preview to selected_action was created.",
            "what_can_be_selected": "Only ready sandbox motor intents such as step_forward or reach_front can become selected_action records.",
            "what_is_blocked": "Wall-front no-intent cases remain blocked, and final_action, direct command, motor execution, pathfinding, persistence, production behavior, and proof claims remain blocked.",
            "plain_result": "Qingyin can now name a sandbox selected_action from a ready motor intent, but still cannot execute it.",
        },
        "blocked_flags": {field: False for field in REQUIRED_BLOCKED_FLAGS},
    }


def validate_sandbox_motor_intent_to_selected_action_bridge_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "sandbox_motor_intent_to_selected_action_bridge_minimal",
        "record_version": "v0",
        "bridge_status": "completed_sandbox_motor_intent_to_selected_action_bridge",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _dict(record.get("source_motor_intent_preview"), errors, "source_motor_intent_preview_missing")
    _validate_source(source, errors)

    selected = _dict(record.get("selected_action_bridge_result"), errors, "selected_action_bridge_result_missing")
    expected_selected = _derive_selected_action(source)
    for field, value in expected_selected.items():
        if selected.get(field) != value:
            errors.append(f"selected_action_bridge_result_{field}_not_expected")
    if selected.get("selected_action") is not None and selected.get("selected_action") not in VALID_SELECTED_ACTIONS:
        errors.append("selected_action_bridge_result_selected_action_invalid")
    if selected.get("final_action_created") is not False:
        errors.append("selected_action_bridge_result_final_action_created_not_false")
    if selected.get("direct_command_created") is not False:
        errors.append("selected_action_bridge_result_direct_command_created_not_false")
    if selected.get("motor_action_executed") is not False:
        errors.append("selected_action_bridge_result_motor_action_executed_not_false")

    human = _dict(record.get("human_summary"), errors, "human_summary_missing")
    for field in ("what_was_built", "what_can_be_selected", "what_is_blocked", "plain_result"):
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
        "source_intent_preview_created": source.get("intent_preview_created") is True,
        "selected_action_created": selected.get("selected_action_created") is True,
        "selected_action_blocked": selected.get("selected_action_created") is False,
        "step_forward_selected": selected.get("selected_action") == "step_forward",
        "reach_front_selected": selected.get("selected_action") == "reach_front",
        "no_intent_blocked": selected.get("blocked_reason") == "no_selected_motor_intent",
        "sandbox_only": selected.get("selected_action_scope") == "sandbox_only",
        "preview_source_preserved": selected.get("selected_action_source") == "sandbox_selected_motor_intent_preview",
        "final_action_blocked": selected.get("final_action_created") is False
        and blocked.get("final_action_created") is False,
        "direct_command_blocked": selected.get("direct_command_created") is False
        and blocked.get("direct_command_created") is False,
        "motor_execution_blocked": selected.get("motor_action_executed") is False
        and blocked.get("motor_action_executed") is False,
        "pathfinding_blocked": blocked.get("pathfinding_used") is False,
        "memory_write_blocked": blocked.get("memory_write_performed") is False,
        "predictor_mutation_blocked": blocked.get("predictor_mutation_performed") is False,
        "persistent_body_schema_blocked": blocked.get("persistent_body_schema_written") is False,
        "production_behavior_blocked": blocked.get("production_behavior_changed") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claimed") is False,
    }


def run_sandbox_motor_intent_to_selected_action_bridge_minimal_check() -> dict[str, Any]:
    source_result = run_sandbox_motor_intent_preview_minimal_check()
    empty_source, wall_source, item_source = source_result["valid_records"]
    valid_empty = build_sandbox_motor_intent_to_selected_action_bridge_record(empty_source)
    valid_wall = build_sandbox_motor_intent_to_selected_action_bridge_record(wall_source)
    valid_item = build_sandbox_motor_intent_to_selected_action_bridge_record(item_source)
    records = [valid_empty, valid_wall, valid_item, *_invalid_records(valid_empty)]
    validation_results = [validate_sandbox_motor_intent_to_selected_action_bridge_record(record) for record in records]
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
            "boundary_reason": "Creates sandbox-only selected_action records from selected_motor_intent previews.",
        },
        "valid_records": [valid_empty, valid_wall, valid_item],
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A sandbox motor intent to selected_action bridge was added.",
            "what_changed": "Ready sandbox motor intents can now produce sandbox-only selected_action records.",
            "what_is_blocked": "The bridge does not create final_action, direct command, motor execution, pathfinding, production behavior, persistence, memory write, predictor mutation, or proof claims.",
            "plain_result": "The embodiment/action line now reaches sandbox selected_action from body-ready motor intent.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    preview = source["motor_intent_preview"]
    source_readiness = source["source_body_schema_readiness"]
    return {
        "source_record_type": source["record_type"],
        "source_validated": True,
        "body_id": source_readiness["body_id"],
        "body_scope": source_readiness["body_scope"],
        "front_symbol": source_readiness["front_symbol"],
        "intent_preview_created": preview["intent_preview_created"],
        "selected_motor_intent_created": preview["selected_motor_intent_created"],
        "selected_motor_intent": preview["selected_motor_intent"],
        "blocked_reason": preview["blocked_reason"],
        "preview_only": preview["preview_only"],
    }


def _derive_selected_action(source: dict[str, Any]) -> dict[str, Any]:
    intent = source.get("selected_motor_intent")
    selected_action_created = intent in VALID_SELECTED_ACTIONS and source.get("selected_motor_intent_created") is True
    return {
        "selected_action_created": selected_action_created,
        "selected_action": intent if selected_action_created else None,
        "selected_action_scope": "sandbox_only" if selected_action_created else None,
        "selected_action_source": "sandbox_selected_motor_intent_preview" if selected_action_created else None,
        "selection_reason": "ready_body_motor_intent" if selected_action_created else None,
        "blocked_reason": None if selected_action_created else "no_selected_motor_intent",
        "final_action_created": False,
        "direct_command_created": False,
        "motor_action_executed": False,
        "rollback_available": True,
        "audit_recorded": True,
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_motor_intent_preview_not_validated")
    if source.get("source_record_type") != "sandbox_motor_intent_preview_minimal":
        errors.append("source_motor_intent_preview_record_type_not_expected")
    if source.get("body_id") != "qingyin_minimal_grid_body_v0":
        errors.append("source_motor_intent_preview_body_id_not_expected")
    if source.get("body_scope") != "sandbox_only":
        errors.append("source_motor_intent_preview_body_scope_not_expected")
    if source.get("intent_preview_created") is not True:
        errors.append("source_motor_intent_preview_not_created")
    if source.get("selected_motor_intent") is not None and source.get("selected_motor_intent") not in VALID_SELECTED_ACTIONS:
        errors.append("source_motor_intent_preview_selected_motor_intent_invalid")
    if source.get("preview_only") is not True:
        errors.append("source_motor_intent_preview_not_preview_only")


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def add(name: str, mutator) -> None:
        record = deepcopy(valid_record)
        mutator(record)
        record["invalid_case"] = name
        cases.append(record)

    add("wrong_record_type", lambda r: r.__setitem__("record_type", "sandbox_selected_action"))
    add("source_not_validated", lambda r: r["source_motor_intent_preview"].__setitem__("source_validated", False))
    add("source_not_preview", lambda r: r["source_motor_intent_preview"].__setitem__("intent_preview_created", False))
    add("source_bad_intent", lambda r: r["source_motor_intent_preview"].__setitem__("selected_motor_intent", "jump"))
    add("selected_action_missing", lambda r: r["selected_action_bridge_result"].__setitem__("selected_action_created", False))
    add("wrong_selected_action", lambda r: r["selected_action_bridge_result"].__setitem__("selected_action", "reach_front"))
    add("invalid_selected_action", lambda r: r["selected_action_bridge_result"].__setitem__("selected_action", "jump"))
    add("wrong_scope", lambda r: r["selected_action_bridge_result"].__setitem__("selected_action_scope", "production"))
    add("wrong_source", lambda r: r["selected_action_bridge_result"].__setitem__("selected_action_source", "autonomous_selector"))
    add("final_action_created", lambda r: r["selected_action_bridge_result"].__setitem__("final_action_created", True))
    add("direct_command_created", lambda r: r["selected_action_bridge_result"].__setitem__("direct_command_created", True))
    add("motor_action_executed", lambda r: r["selected_action_bridge_result"].__setitem__("motor_action_executed", True))
    add("audit_missing", lambda r: r["selected_action_bridge_result"].__setitem__("audit_recorded", False))
    add("rollback_missing", lambda r: r["selected_action_bridge_result"].__setitem__("rollback_available", False))
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
        "selected_action_bridge_result_count": len(results),
        "valid_selected_action_bridge_count": len(valid_results),
        "invalid_selected_action_bridge_count": len(results) - len(valid_results),
        "source_validated_count": _count_valid(valid_results, "source_validated"),
        "source_intent_preview_created_count": _count_valid(valid_results, "source_intent_preview_created"),
        "selected_action_created_count": _count_valid(valid_results, "selected_action_created"),
        "selected_action_blocked_count": _count_valid(valid_results, "selected_action_blocked"),
        "step_forward_selected_count": _count_valid(valid_results, "step_forward_selected"),
        "reach_front_selected_count": _count_valid(valid_results, "reach_front_selected"),
        "no_intent_blocked_count": _count_valid(valid_results, "no_intent_blocked"),
        "sandbox_only_count": _count_valid(valid_results, "sandbox_only"),
        "preview_source_preserved_count": _count_valid(valid_results, "preview_source_preserved"),
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
        summary["selected_action_bridge_result_count"] == 29
        and summary["valid_selected_action_bridge_count"] == 3
        and summary["invalid_selected_action_bridge_count"] == 26
        and summary["source_validated_count"] == 3
        and summary["source_intent_preview_created_count"] == 3
        and summary["selected_action_created_count"] == 2
        and summary["selected_action_blocked_count"] == 1
        and summary["step_forward_selected_count"] == 1
        and summary["reach_front_selected_count"] == 1
        and summary["no_intent_blocked_count"] == 1
        and summary["sandbox_only_count"] == 2
        and summary["preview_source_preserved_count"] == 2
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
