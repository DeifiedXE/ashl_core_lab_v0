"""Sandbox-only motor intent preview from body-schema readiness."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .minimal_body_schema_affordance_consistency_runtime import (
    build_minimal_body_schema_affordance_consistency_record,
    run_minimal_body_schema_affordance_consistency_runtime_check,
    validate_minimal_body_schema_affordance_consistency_record,
)


COMMAND = "run-sandbox-motor-intent-preview-minimal-check"
FLOW = "sandbox_motor_intent_preview_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxMotorIntentPreviewMinimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b113"
BOUNDARY_INDEX_AFTER = "2026-06-09-b114"

VALID_INTENTS = ("step_forward", "turn_left", "turn_right", "reach_front")
VALID_SOURCE_DECISIONS = ("empty_front_step_forward", "wall_front_no_intent", "item_front_reach_front")

REQUIRED_BLOCKED_FLAGS = (
    "selected_action_created",
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


def build_sandbox_motor_intent_preview_record(
    body_schema_consistency_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = deepcopy(body_schema_consistency_record) if body_schema_consistency_record is not None else (
        build_minimal_body_schema_affordance_consistency_record()
    )
    source_validation = validate_minimal_body_schema_affordance_consistency_record(source)
    if not source_validation["valid"]:
        raise ValueError("body_schema_consistency_record must validate before motor intent preview")

    source_summary = _source_summary(source)
    intent = _derive_intent(source)
    return {
        "record_type": "sandbox_motor_intent_preview_minimal",
        "record_version": "v0",
        "preview_status": "completed_sandbox_motor_intent_preview",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_body_schema_readiness": source_summary,
        "motor_intent_preview": intent,
        "human_summary": {
            "what_was_built": "A sandbox-only motor intent preview was created from body-schema readiness.",
            "what_it_can_name": "The preview can name step_forward or reach_front when the body and front-cell affordance allow it.",
            "what_it_blocks": "Wall-front and body-blocked cases create no selected motor intent.",
            "what_is_not_done": "No selected_action, final_action, direct command, motor execution, pathfinding, persistent body schema, memory write, predictor mutation, production behavior, or proof claim is created.",
            "plain_result": "Qingyin can preview a sandbox motor intent from readiness, but still cannot act from it.",
        },
        "blocked_flags": {field: False for field in REQUIRED_BLOCKED_FLAGS},
    }


def validate_sandbox_motor_intent_preview_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "sandbox_motor_intent_preview_minimal",
        "record_version": "v0",
        "preview_status": "completed_sandbox_motor_intent_preview",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _dict(record.get("source_body_schema_readiness"), errors, "source_body_schema_readiness_missing")
    _validate_source(source, errors)

    preview = _dict(record.get("motor_intent_preview"), errors, "motor_intent_preview_missing")
    expected_preview = _derive_intent_from_source_summary(source)
    for field, value in expected_preview.items():
        if preview.get(field) != value:
            errors.append(f"motor_intent_preview_{field}_not_expected")
    if preview.get("selected_motor_intent") is not None and preview.get("selected_motor_intent") not in VALID_INTENTS:
        errors.append("motor_intent_preview_selected_motor_intent_invalid")
    if preview.get("selected_action_created") is not False:
        errors.append("motor_intent_preview_selected_action_created_not_false")
    if preview.get("final_action_created") is not False:
        errors.append("motor_intent_preview_final_action_created_not_false")
    if preview.get("direct_command_created") is not False:
        errors.append("motor_intent_preview_direct_command_created_not_false")
    if preview.get("motor_action_executed") is not False:
        errors.append("motor_intent_preview_motor_action_executed_not_false")

    human = _dict(record.get("human_summary"), errors, "human_summary_missing")
    for field in ("what_was_built", "what_it_can_name", "what_it_blocks", "what_is_not_done", "plain_result"):
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
        "body_schema_consistent": source.get("body_schema_consistent") is True,
        "intent_preview_created": preview.get("intent_preview_created") is True,
        "selected_motor_intent_created": preview.get("selected_motor_intent_created") is True,
        "no_intent_created": preview.get("selected_motor_intent_created") is False,
        "step_forward_intent": preview.get("selected_motor_intent") == "step_forward",
        "reach_front_intent": preview.get("selected_motor_intent") == "reach_front",
        "blocked_by_front_wall": preview.get("blocked_reason") == "front_blocked_by_affordance",
        "preview_only": preview.get("preview_only") is True,
        "selected_action_blocked": preview.get("selected_action_created") is False
        and blocked.get("selected_action_created") is False,
        "final_action_blocked": preview.get("final_action_created") is False
        and blocked.get("final_action_created") is False,
        "direct_command_blocked": preview.get("direct_command_created") is False
        and blocked.get("direct_command_created") is False,
        "motor_execution_blocked": preview.get("motor_action_executed") is False
        and blocked.get("motor_action_executed") is False,
        "pathfinding_blocked": blocked.get("pathfinding_used") is False,
        "memory_write_blocked": blocked.get("memory_write_performed") is False,
        "predictor_mutation_blocked": blocked.get("predictor_mutation_performed") is False,
        "persistent_body_schema_blocked": blocked.get("persistent_body_schema_written") is False,
        "production_behavior_blocked": blocked.get("production_behavior_changed") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claimed") is False,
    }


def run_sandbox_motor_intent_preview_minimal_check() -> dict[str, Any]:
    source_result = run_minimal_body_schema_affordance_consistency_runtime_check()
    empty_source, wall_source, item_source = source_result["valid_records"]
    valid_empty = build_sandbox_motor_intent_preview_record(empty_source)
    valid_wall = build_sandbox_motor_intent_preview_record(wall_source)
    valid_item = build_sandbox_motor_intent_preview_record(item_source)
    records = [valid_empty, valid_wall, valid_item, *_invalid_records(valid_empty)]
    validation_results = [validate_sandbox_motor_intent_preview_record(record) for record in records]
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
            "boundary_reason": "Creates sandbox-only selected_motor_intent preview from body readiness.",
        },
        "valid_records": [valid_empty, valid_wall, valid_item],
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A sandbox motor intent preview layer was added.",
            "what_changed": "Body-ready affordances can now produce sandbox-only selected_motor_intent previews.",
            "what_is_blocked": "The preview does not create selected_action, final_action, direct command, motor execution, pathfinding, production behavior, persistence, memory write, predictor mutation, or proof claims.",
            "plain_result": "The action line now has a named sandbox motor intent preview after body readiness.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    body = source["minimal_body_schema_state"]
    readiness = source["motor_readiness_preview"]
    affordance = source["source_affordance_bridge"]
    return {
        "source_record_type": source["record_type"],
        "source_validated": True,
        "body_id": body["body_id"],
        "body_scope": body["body_scope"],
        "position": list(body["position"]),
        "facing": body["facing"],
        "front_symbol": affordance["front_symbol"],
        "body_schema_consistent": source["affordance_consistency_result"][
            "body_schema_consistent_with_affordance_source"
        ],
        "step_forward_ready": readiness["step_forward_ready"],
        "turn_left_ready": readiness["turn_left_ready"],
        "turn_right_ready": readiness["turn_right_ready"],
        "reach_front_ready": readiness["reach_front_ready"],
        "front_blocked_by_affordance": readiness["front_blocked_by_affordance"],
        "body_blocks_movement": readiness["body_blocks_movement"],
    }


def _derive_intent(source: dict[str, Any]) -> dict[str, Any]:
    return _derive_intent_from_source_summary(_source_summary(source))


def _derive_intent_from_source_summary(source: dict[str, Any]) -> dict[str, Any]:
    selected_intent = None
    decision = "wall_front_no_intent" if source.get("front_blocked_by_affordance") else "empty_front_step_forward"
    blocked_reason = None
    if source.get("front_blocked_by_affordance"):
        blocked_reason = "front_blocked_by_affordance"
    elif source.get("body_blocks_movement"):
        decision = "body_state_no_intent"
        blocked_reason = "body_state_blocks_movement"
    elif source.get("reach_front_ready"):
        selected_intent = "reach_front"
        decision = "item_front_reach_front"
    elif source.get("step_forward_ready"):
        selected_intent = "step_forward"
        decision = "empty_front_step_forward"
    else:
        decision = "no_ready_affordance"
        blocked_reason = "no_ready_affordance"

    return {
        "intent_preview_created": True,
        "preview_scope": "sandbox_motor_intent_preview_only",
        "intent_source_decision": decision,
        "selected_motor_intent_created": selected_intent is not None,
        "selected_motor_intent": selected_intent,
        "blocked_reason": blocked_reason,
        "selection_rule": "reach_front_if_ready_else_step_forward_if_ready_else_no_intent",
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "motor_action_executed": False,
        "preview_only": True,
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_body_schema_readiness_not_validated")
    if source.get("body_id") != "qingyin_minimal_grid_body_v0":
        errors.append("source_body_schema_readiness_body_id_not_expected")
    if source.get("body_scope") != "sandbox_only":
        errors.append("source_body_schema_readiness_body_scope_not_expected")
    if not _is_position(source.get("position")):
        errors.append("source_body_schema_readiness_position_invalid")
    if source.get("facing") not in ("north", "east", "south", "west"):
        errors.append("source_body_schema_readiness_facing_invalid")
    if source.get("body_schema_consistent") is not True:
        errors.append("source_body_schema_readiness_not_consistent")
    for field in (
        "step_forward_ready",
        "turn_left_ready",
        "turn_right_ready",
        "reach_front_ready",
        "front_blocked_by_affordance",
        "body_blocks_movement",
    ):
        if not isinstance(source.get(field), bool):
            errors.append(f"source_body_schema_readiness_{field}_not_boolean")


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def add(name: str, mutator) -> None:
        record = deepcopy(valid_record)
        mutator(record)
        record["invalid_case"] = name
        cases.append(record)

    add("wrong_record_type", lambda r: r.__setitem__("record_type", "motor_intent"))
    add("source_not_validated", lambda r: r["source_body_schema_readiness"].__setitem__("source_validated", False))
    add("source_not_consistent", lambda r: r["source_body_schema_readiness"].__setitem__("body_schema_consistent", False))
    add("wrong_decision", lambda r: r["motor_intent_preview"].__setitem__("intent_source_decision", "item_front_reach_front"))
    add("wrong_selected_intent", lambda r: r["motor_intent_preview"].__setitem__("selected_motor_intent", "reach_front"))
    add("invalid_selected_intent", lambda r: r["motor_intent_preview"].__setitem__("selected_motor_intent", "jump"))
    add("intent_created_false", lambda r: r["motor_intent_preview"].__setitem__("selected_motor_intent_created", False))
    add("preview_not_created", lambda r: r["motor_intent_preview"].__setitem__("intent_preview_created", False))
    add("preview_not_only", lambda r: r["motor_intent_preview"].__setitem__("preview_only", False))
    add("selected_action_created", lambda r: r["motor_intent_preview"].__setitem__("selected_action_created", True))
    add("final_action_created", lambda r: r["motor_intent_preview"].__setitem__("final_action_created", True))
    add("direct_command_created", lambda r: r["motor_intent_preview"].__setitem__("direct_command_created", True))
    add("motor_action_executed", lambda r: r["motor_intent_preview"].__setitem__("motor_action_executed", True))
    add("blocked_selected_action", lambda r: r["blocked_flags"].__setitem__("selected_action_created", True))
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
        "motor_intent_preview_result_count": len(results),
        "valid_motor_intent_preview_count": len(valid_results),
        "invalid_motor_intent_preview_count": len(results) - len(valid_results),
        "source_validated_count": _count_valid(valid_results, "source_validated"),
        "body_schema_consistent_count": _count_valid(valid_results, "body_schema_consistent"),
        "intent_preview_created_count": _count_valid(valid_results, "intent_preview_created"),
        "selected_motor_intent_created_count": _count_valid(valid_results, "selected_motor_intent_created"),
        "no_intent_created_count": _count_valid(valid_results, "no_intent_created"),
        "step_forward_intent_count": _count_valid(valid_results, "step_forward_intent"),
        "reach_front_intent_count": _count_valid(valid_results, "reach_front_intent"),
        "blocked_by_front_wall_count": _count_valid(valid_results, "blocked_by_front_wall"),
        "preview_only_count": _count_valid(valid_results, "preview_only"),
        "selected_action_blocked_count": _count_valid(valid_results, "selected_action_blocked"),
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
        summary["motor_intent_preview_result_count"] == 29
        and summary["valid_motor_intent_preview_count"] == 3
        and summary["invalid_motor_intent_preview_count"] == 26
        and summary["source_validated_count"] == 3
        and summary["body_schema_consistent_count"] == 3
        and summary["intent_preview_created_count"] == 3
        and summary["selected_motor_intent_created_count"] == 2
        and summary["no_intent_created_count"] == 1
        and summary["step_forward_intent_count"] == 1
        and summary["reach_front_intent_count"] == 1
        and summary["blocked_by_front_wall_count"] == 1
        and summary["preview_only_count"] == 3
        and summary["selected_action_blocked_count"] == 3
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


def _is_position(value: Any) -> bool:
    return isinstance(value, list) and len(value) == 2 and all(isinstance(item, int) for item in value)


def _count_valid(results: list[dict[str, Any]], field: str) -> int:
    return sum(1 for result in results if result.get(field) is True)
