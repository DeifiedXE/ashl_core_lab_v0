"""Bridge body-relative visual spatial traces into motor affordance previews."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .visual_spatial_grounding_minimal import (
    build_visual_spatial_grounding_record,
    validate_visual_spatial_grounding_record,
)


COMMAND = "run-visual-spatial-motor-affordance-bridge-minimal-check"
FLOW = "visual_spatial_motor_affordance_bridge_minimal_v0"
PACKAGE_ID = "PKG-Phase0-VisualSpatialMotorAffordanceBridge-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b111"
BOUNDARY_INDEX_AFTER = "2026-06-09-b112"

SUPPORTED_FRONT_SYMBOLS = ("e", "w", "x", "i", "d", "g")
PASSABLE_FRONT_SYMBOLS = ("e", "i", "d", "g")
CONTACT_FRONT_SYMBOLS = ("i", "d", "g")

REQUIRED_BLOCKED_FLAGS = (
    "motor_action_executed",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "production_behavior_changed",
    "real_navigation_changed",
    "ui_behavior_changed",
    "pathfinding_used",
    "route_planner_added",
    "goal_seeking_added",
    "active_focus_applied",
    "visual_action_selection_influence",
    "memory_write_performed",
    "retention_write_performed",
    "predictor_mutation_performed",
    "persistent_body_schema_written",
    "real_image_vision",
    "object_recognition",
    "semantic_vision",
    "proof_of_learning_claimed",
)


def build_visual_spatial_motor_affordance_bridge_record(
    visual_spatial_grounding: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = deepcopy(visual_spatial_grounding) if visual_spatial_grounding is not None else (
        build_visual_spatial_grounding_record()
    )
    validation = validate_visual_spatial_grounding_record(source)
    if not validation["valid"]:
        raise ValueError("visual_spatial_grounding must validate before affordance bridge")

    front = source["front_cell_spatial_summary"]
    front_symbol = front["front_symbol"]
    affordances = _derive_affordances(front_symbol)
    motor_previews = _build_motor_intent_previews(affordances)
    return {
        "record_type": "visual_spatial_motor_affordance_bridge",
        "record_version": "v0",
        "bridge_status": "completed_affordance_preview_from_visual_spatial_trace",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_visual_spatial_grounding": {
            "record_type": source["record_type"],
            "spatial_grounding_status": source["spatial_grounding_status"],
            "agent_position": source["body_relative_frame"]["agent_position"],
            "facing": source["body_relative_frame"]["facing"],
            "front_symbol": front_symbol,
            "front_world_position": front["world_position"],
            "front_body_direction": front["body_direction"],
            "front_distance_forward": front["distance_forward"],
            "source_validated": True,
        },
        "affordance_rule_set": {
            "rule_set_id": "symbolic_body_relative_affordance_rules_v0",
            "front_symbol_only_v0": True,
            "supported_front_symbols": list(SUPPORTED_FRONT_SYMBOLS),
            "passable_front_symbols": list(PASSABLE_FRONT_SYMBOLS),
            "contact_front_symbols": list(CONTACT_FRONT_SYMBOLS),
            "semantic_interpretation_used": False,
            "pathfinding_used": False,
            "goal_seeking_used": False,
        },
        "body_relative_affordance_candidates": affordances,
        "motor_intent_preview": {
            "preview_created": True,
            "preview_scope": "sandbox_body_relative_motor_intent_preview_only",
            "candidate_motor_intents": motor_previews,
            "selected_motor_intent": None,
            "motor_action_executed": False,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
        },
        "affordance_summary": {
            "front_symbol": front_symbol,
            "front_blocked": affordances["can_step_forward"]["blocked"],
            "can_step_forward": affordances["can_step_forward"]["available"],
            "can_turn_left": affordances["can_turn_left"]["available"],
            "can_turn_right": affordances["can_turn_right"]["available"],
            "can_reach_front": affordances["can_reach_front"]["available"],
            "front_contact_possible": affordances["front_contact_possible"]["available"],
            "preview_only": True,
        },
        "human_summary": {
            "what_was_built": "A visual-spatial to motor-affordance preview bridge was created.",
            "what_it_uses": "The bridge uses the body-relative front-cell symbol, direction, and distance from visual_spatial_grounding.",
            "what_it_outputs": "It previews can_step_forward, can_turn_left, can_turn_right, can_reach_front, front_blocked, and front_contact_possible.",
            "what_is_blocked": "No motor action, selected_action, final_action, direct command, pathfinding, memory write, predictor mutation, persistent body schema, production behavior, or proof claim is created.",
            "plain_result": "Qingyin can now preview body-relative motor affordances from spatial vision, but still cannot act from them.",
        },
        "blocked_flags": {field: False for field in REQUIRED_BLOCKED_FLAGS},
    }


def validate_visual_spatial_motor_affordance_bridge_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "visual_spatial_motor_affordance_bridge",
        "record_version": "v0",
        "bridge_status": "completed_affordance_preview_from_visual_spatial_trace",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _dict(record.get("source_visual_spatial_grounding"), errors, "source_visual_spatial_grounding_missing")
    front_symbol = source.get("front_symbol")
    if source.get("source_validated") is not True:
        errors.append("source_visual_spatial_grounding_not_validated")
    if source.get("front_body_direction") != "front":
        errors.append("source_front_body_direction_not_front")
    if source.get("front_distance_forward") != 1:
        errors.append("source_front_distance_forward_not_one")
    if front_symbol not in SUPPORTED_FRONT_SYMBOLS:
        errors.append("source_front_symbol_not_supported")

    rules = _dict(record.get("affordance_rule_set"), errors, "affordance_rule_set_missing")
    expected_rules = {
        "front_symbol_only_v0": True,
        "supported_front_symbols": list(SUPPORTED_FRONT_SYMBOLS),
        "passable_front_symbols": list(PASSABLE_FRONT_SYMBOLS),
        "contact_front_symbols": list(CONTACT_FRONT_SYMBOLS),
        "semantic_interpretation_used": False,
        "pathfinding_used": False,
        "goal_seeking_used": False,
    }
    for field, value in expected_rules.items():
        if rules.get(field) != value:
            errors.append(f"affordance_rule_set_{field}_not_expected")

    affordances = _dict(
        record.get("body_relative_affordance_candidates"),
        errors,
        "body_relative_affordance_candidates_missing",
    )
    expected_affordances = _derive_affordances(front_symbol) if front_symbol in SUPPORTED_FRONT_SYMBOLS else {}
    for field in ("can_step_forward", "can_turn_left", "can_turn_right", "can_reach_front", "front_contact_possible"):
        item = _dict(affordances.get(field), errors, f"affordance_{field}_missing")
        if expected_affordances and item != expected_affordances[field]:
            errors.append(f"affordance_{field}_not_expected")

    preview = _dict(record.get("motor_intent_preview"), errors, "motor_intent_preview_missing")
    expected_preview = {
        "preview_created": True,
        "preview_scope": "sandbox_body_relative_motor_intent_preview_only",
        "selected_motor_intent": None,
        "motor_action_executed": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
    }
    for field, value in expected_preview.items():
        if preview.get(field) != value:
            errors.append(f"motor_intent_preview_{field}_not_expected")
    motor_intents = preview.get("candidate_motor_intents")
    if not isinstance(motor_intents, list) or not motor_intents:
        errors.append("motor_intent_preview_candidate_motor_intents_missing")
    elif expected_affordances and motor_intents != _build_motor_intent_previews(expected_affordances):
        errors.append("motor_intent_preview_candidate_motor_intents_not_expected")

    summary = _dict(record.get("affordance_summary"), errors, "affordance_summary_missing")
    if summary.get("front_symbol") != front_symbol:
        errors.append("affordance_summary_front_symbol_mismatch")
    if expected_affordances:
        expected_summary = {
            "front_blocked": expected_affordances["can_step_forward"]["blocked"],
            "can_step_forward": expected_affordances["can_step_forward"]["available"],
            "can_turn_left": True,
            "can_turn_right": True,
            "can_reach_front": expected_affordances["can_reach_front"]["available"],
            "front_contact_possible": expected_affordances["front_contact_possible"]["available"],
            "preview_only": True,
        }
        for field, value in expected_summary.items():
            if summary.get(field) != value:
                errors.append(f"affordance_summary_{field}_not_expected")

    human = _dict(record.get("human_summary"), errors, "human_summary_missing")
    for field in ("what_was_built", "what_it_uses", "what_it_outputs", "what_is_blocked", "plain_result"):
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
        "front_symbol_supported": front_symbol in SUPPORTED_FRONT_SYMBOLS,
        "affordance_preview_created": preview.get("preview_created") is True,
        "can_step_forward": summary.get("can_step_forward") is True,
        "front_blocked": summary.get("front_blocked") is True,
        "can_turn_left": summary.get("can_turn_left") is True,
        "can_turn_right": summary.get("can_turn_right") is True,
        "can_reach_front": summary.get("can_reach_front") is True,
        "front_contact_possible": summary.get("front_contact_possible") is True,
        "preview_only": summary.get("preview_only") is True,
        "motor_action_blocked": preview.get("motor_action_executed") is False
        and blocked.get("motor_action_executed") is False,
        "selected_action_blocked": preview.get("selected_action_created") is False
        and blocked.get("selected_action_created") is False,
        "final_action_blocked": preview.get("final_action_created") is False
        and blocked.get("final_action_created") is False,
        "direct_command_blocked": preview.get("direct_command_created") is False
        and blocked.get("direct_command_created") is False,
        "pathfinding_blocked": rules.get("pathfinding_used") is False and blocked.get("pathfinding_used") is False,
        "memory_write_blocked": blocked.get("memory_write_performed") is False,
        "predictor_mutation_blocked": blocked.get("predictor_mutation_performed") is False,
        "persistent_body_schema_blocked": blocked.get("persistent_body_schema_written") is False,
        "semantic_vision_blocked": blocked.get("semantic_vision") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claimed") is False,
    }


def run_visual_spatial_motor_affordance_bridge_minimal_check() -> dict[str, Any]:
    valid_empty_front = build_visual_spatial_motor_affordance_bridge_record()
    valid_wall_front = build_visual_spatial_motor_affordance_bridge_record(_source_with_front_symbol("w"))
    valid_item_front = build_visual_spatial_motor_affordance_bridge_record(_source_with_front_symbol("i"))
    records = [valid_empty_front, valid_wall_front, valid_item_front, *_invalid_records(valid_empty_front)]
    validation_results = [validate_visual_spatial_motor_affordance_bridge_record(record) for record in records]
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
            "boundary_reason": "Adds body-relative motor affordance preview derived from visual spatial traces.",
        },
        "valid_records": [valid_empty_front, valid_wall_front, valid_item_front],
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A minimal visual-spatial to motor-affordance bridge was added.",
            "what_changed": "Visible front-cell spatial traces can now preview step, turn, reach, blocked, and contact affordances.",
            "what_is_blocked": "The bridge does not select, finalize, command, execute, plan paths, write memory, mutate predictors, persist body schema, or prove learning.",
            "plain_result": "The visual line can now say what the body could do next, but still cannot make Qingyin act.",
        },
        "valid_result_count": len(valid_results),
    }


def _derive_affordances(front_symbol: str) -> dict[str, dict[str, Any]]:
    can_step = front_symbol in PASSABLE_FRONT_SYMBOLS
    contact_possible = front_symbol in CONTACT_FRONT_SYMBOLS
    return {
        "can_step_forward": {
            "available": can_step,
            "blocked": not can_step,
            "reason": "front_cell_passable" if can_step else "front_cell_blocked",
            "source_front_symbol": front_symbol,
        },
        "can_turn_left": {
            "available": True,
            "blocked": False,
            "reason": "turning_does_not_require_front_cell_clearance",
            "source_front_symbol": front_symbol,
        },
        "can_turn_right": {
            "available": True,
            "blocked": False,
            "reason": "turning_does_not_require_front_cell_clearance",
            "source_front_symbol": front_symbol,
        },
        "can_reach_front": {
            "available": contact_possible,
            "blocked": not contact_possible,
            "reason": "front_contact_symbol_present" if contact_possible else "no_front_contact_symbol",
            "source_front_symbol": front_symbol,
        },
        "front_contact_possible": {
            "available": contact_possible,
            "blocked": not contact_possible,
            "reason": "front_contact_symbol_present" if contact_possible else "no_front_contact_symbol",
            "source_front_symbol": front_symbol,
        },
    }


def _build_motor_intent_previews(affordances: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "motor_intent": "step_forward",
            "available": affordances["can_step_forward"]["available"],
            "preview_only": True,
            "execution_allowed": False,
        },
        {
            "motor_intent": "turn_left",
            "available": affordances["can_turn_left"]["available"],
            "preview_only": True,
            "execution_allowed": False,
        },
        {
            "motor_intent": "turn_right",
            "available": affordances["can_turn_right"]["available"],
            "preview_only": True,
            "execution_allowed": False,
        },
        {
            "motor_intent": "reach_front",
            "available": affordances["can_reach_front"]["available"],
            "preview_only": True,
            "execution_allowed": False,
        },
    ]


def _source_with_front_symbol(symbol: str) -> dict[str, Any]:
    source = build_visual_spatial_grounding_record()
    source["source_visual_observation"]["front_symbol"] = symbol
    source["source_visual_observation"]["viewport"][1][1] = symbol
    front_position = source["front_cell_spatial_summary"]["world_position"]
    for cell in source["spatial_cells"]:
        if cell["viewport_position"] == [1, 1]:
            cell["symbol"] = symbol
            front_position = cell["world_position"]
    source["front_cell_spatial_summary"]["front_symbol"] = symbol
    source["front_cell_spatial_summary"]["world_position"] = front_position
    return source


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def add(name: str, mutator) -> None:
        record = deepcopy(valid_record)
        mutator(record)
        record["invalid_case"] = name
        cases.append(record)

    add("wrong_record_type", lambda r: r.__setitem__("record_type", "motor_action_runtime"))
    add("source_not_validated", lambda r: r["source_visual_spatial_grounding"].__setitem__("source_validated", False))
    add("source_not_front", lambda r: r["source_visual_spatial_grounding"].__setitem__("front_body_direction", "left"))
    add("source_wrong_distance", lambda r: r["source_visual_spatial_grounding"].__setitem__("front_distance_forward", 2))
    add("unsupported_front_symbol", lambda r: r["source_visual_spatial_grounding"].__setitem__("front_symbol", "candy"))
    add("rule_not_front_symbol_only", lambda r: r["affordance_rule_set"].__setitem__("front_symbol_only_v0", False))
    add("semantic_rule_used", lambda r: r["affordance_rule_set"].__setitem__("semantic_interpretation_used", True))
    add("pathfinding_rule_used", lambda r: r["affordance_rule_set"].__setitem__("pathfinding_used", True))
    add("goal_rule_used", lambda r: r["affordance_rule_set"].__setitem__("goal_seeking_used", True))
    add("wrong_step_affordance", lambda r: r["body_relative_affordance_candidates"]["can_step_forward"].__setitem__("available", False))
    add("wrong_turn_left_affordance", lambda r: r["body_relative_affordance_candidates"]["can_turn_left"].__setitem__("available", False))
    add("wrong_turn_right_affordance", lambda r: r["body_relative_affordance_candidates"]["can_turn_right"].__setitem__("available", False))
    add("wrong_reach_affordance", lambda r: r["body_relative_affordance_candidates"]["can_reach_front"].__setitem__("available", True))
    add("wrong_contact_affordance", lambda r: r["body_relative_affordance_candidates"]["front_contact_possible"].__setitem__("available", True))
    add("preview_not_created", lambda r: r["motor_intent_preview"].__setitem__("preview_created", False))
    add("selected_motor_intent", lambda r: r["motor_intent_preview"].__setitem__("selected_motor_intent", "step_forward"))
    add("motor_executed", lambda r: r["motor_intent_preview"].__setitem__("motor_action_executed", True))
    add("selected_action_created", lambda r: r["motor_intent_preview"].__setitem__("selected_action_created", True))
    add("final_action_created", lambda r: r["motor_intent_preview"].__setitem__("final_action_created", True))
    add("direct_command_created", lambda r: r["motor_intent_preview"].__setitem__("direct_command_created", True))
    add("missing_motor_intents", lambda r: r["motor_intent_preview"].__setitem__("candidate_motor_intents", []))
    add("summary_wrong_front_blocked", lambda r: r["affordance_summary"].__setitem__("front_blocked", True))
    add("summary_wrong_can_step", lambda r: r["affordance_summary"].__setitem__("can_step_forward", False))
    add("summary_not_preview_only", lambda r: r["affordance_summary"].__setitem__("preview_only", False))
    add("empty_human_summary", lambda r: r["human_summary"].__setitem__("plain_result", ""))
    add("blocked_motor_execution", lambda r: r["blocked_flags"].__setitem__("motor_action_executed", True))
    add("blocked_selected_action", lambda r: r["blocked_flags"].__setitem__("selected_action_created", True))
    add("blocked_final_action", lambda r: r["blocked_flags"].__setitem__("final_action_created", True))
    add("blocked_direct_command", lambda r: r["blocked_flags"].__setitem__("direct_command_created", True))
    add("blocked_pathfinding", lambda r: r["blocked_flags"].__setitem__("pathfinding_used", True))
    add("blocked_memory_write", lambda r: r["blocked_flags"].__setitem__("memory_write_performed", True))
    add("blocked_predictor_mutation", lambda r: r["blocked_flags"].__setitem__("predictor_mutation_performed", True))
    add("blocked_persistent_body_schema", lambda r: r["blocked_flags"].__setitem__("persistent_body_schema_written", True))
    add("blocked_semantic_vision", lambda r: r["blocked_flags"].__setitem__("semantic_vision", True))
    add("blocked_proof_claim", lambda r: r["blocked_flags"].__setitem__("proof_of_learning_claimed", True))
    return cases


def _summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    valid_results = [result for result in results if result["valid"]]
    return {
        "affordance_bridge_result_count": len(results),
        "valid_affordance_bridge_count": len(valid_results),
        "invalid_affordance_bridge_count": len(results) - len(valid_results),
        "source_validated_count": _count_valid(valid_results, "source_validated"),
        "front_symbol_supported_count": _count_valid(valid_results, "front_symbol_supported"),
        "affordance_preview_created_count": _count_valid(valid_results, "affordance_preview_created"),
        "can_step_forward_count": _count_valid(valid_results, "can_step_forward"),
        "front_blocked_count": _count_valid(valid_results, "front_blocked"),
        "can_turn_left_count": _count_valid(valid_results, "can_turn_left"),
        "can_turn_right_count": _count_valid(valid_results, "can_turn_right"),
        "can_reach_front_count": _count_valid(valid_results, "can_reach_front"),
        "front_contact_possible_count": _count_valid(valid_results, "front_contact_possible"),
        "preview_only_count": _count_valid(valid_results, "preview_only"),
        "motor_action_blocked_count": _count_valid(valid_results, "motor_action_blocked"),
        "selected_action_blocked_count": _count_valid(valid_results, "selected_action_blocked"),
        "final_action_blocked_count": _count_valid(valid_results, "final_action_blocked"),
        "direct_command_blocked_count": _count_valid(valid_results, "direct_command_blocked"),
        "pathfinding_blocked_count": _count_valid(valid_results, "pathfinding_blocked"),
        "memory_write_blocked_count": _count_valid(valid_results, "memory_write_blocked"),
        "predictor_mutation_blocked_count": _count_valid(valid_results, "predictor_mutation_blocked"),
        "persistent_body_schema_blocked_count": _count_valid(valid_results, "persistent_body_schema_blocked"),
        "semantic_vision_blocked_count": _count_valid(valid_results, "semantic_vision_blocked"),
        "proof_claim_blocked_count": _count_valid(valid_results, "proof_claim_blocked"),
    }


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["affordance_bridge_result_count"] == 38
        and summary["valid_affordance_bridge_count"] == 3
        and summary["invalid_affordance_bridge_count"] == 35
        and summary["source_validated_count"] == 3
        and summary["front_symbol_supported_count"] == 3
        and summary["affordance_preview_created_count"] == 3
        and summary["can_step_forward_count"] == 2
        and summary["front_blocked_count"] == 1
        and summary["can_turn_left_count"] == 3
        and summary["can_turn_right_count"] == 3
        and summary["can_reach_front_count"] == 1
        and summary["front_contact_possible_count"] == 1
        and summary["preview_only_count"] == 3
        and summary["motor_action_blocked_count"] == 3
        and summary["selected_action_blocked_count"] == 3
        and summary["final_action_blocked_count"] == 3
        and summary["direct_command_blocked_count"] == 3
        and summary["pathfinding_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_mutation_blocked_count"] == 3
        and summary["persistent_body_schema_blocked_count"] == 3
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
