"""Minimal sandbox body schema consistency check for visual affordance previews."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .visual_spatial_motor_affordance_bridge_minimal import (
    build_visual_spatial_motor_affordance_bridge_record,
    run_visual_spatial_motor_affordance_bridge_minimal_check,
    validate_visual_spatial_motor_affordance_bridge_record,
)


COMMAND = "run-minimal-body-schema-affordance-consistency-runtime-check"
FLOW = "minimal_body_schema_affordance_consistency_runtime_v0"
PACKAGE_ID = "PKG-Phase0-MinimalBodySchemaAffordanceConsistencyRuntime-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b112"
BOUNDARY_INDEX_AFTER = "2026-06-09-b113"

VALID_FACINGS = ("north", "east", "south", "west")
VALID_LOCOMOTION_STATES = ("ready", "cooldown", "blocked")
VALID_HAND_STATES = ("empty", "occupied")
VALID_BALANCE_STATES = ("stable", "unstable")
VALID_CONTACT_STATES = ("none", "front_contact")

REQUIRED_BLOCKED_FLAGS = (
    "motor_action_executed",
    "selected_motor_intent_created",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
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


def build_minimal_body_schema_affordance_consistency_record(
    affordance_bridge: dict[str, Any] | None = None,
    body_schema_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = deepcopy(affordance_bridge) if affordance_bridge is not None else (
        build_visual_spatial_motor_affordance_bridge_record()
    )
    source_validation = validate_visual_spatial_motor_affordance_bridge_record(source)
    if not source_validation["valid"]:
        raise ValueError("affordance_bridge must validate before body schema consistency check")

    body = deepcopy(body_schema_state) if body_schema_state is not None else _default_body_schema_state(source)
    readiness = _derive_motor_readiness(source, body)
    return {
        "record_type": "minimal_body_schema_affordance_consistency_runtime",
        "record_version": "v0",
        "runtime_status": "completed_body_schema_affordance_consistency_preview",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_affordance_bridge": {
            "record_type": source["record_type"],
            "bridge_status": source["bridge_status"],
            "source_validated": True,
            "agent_position": source["source_visual_spatial_grounding"]["agent_position"],
            "facing": source["source_visual_spatial_grounding"]["facing"],
            "front_symbol": source["affordance_summary"]["front_symbol"],
            "front_blocked": source["affordance_summary"]["front_blocked"],
            "can_step_forward": source["affordance_summary"]["can_step_forward"],
            "can_turn_left": source["affordance_summary"]["can_turn_left"],
            "can_turn_right": source["affordance_summary"]["can_turn_right"],
            "can_reach_front": source["affordance_summary"]["can_reach_front"],
            "front_contact_possible": source["affordance_summary"]["front_contact_possible"],
        },
        "minimal_body_schema_state": body,
        "affordance_consistency_result": {
            "body_position_matches_visual_source": body.get("position") == source["source_visual_spatial_grounding"][
                "agent_position"
            ],
            "body_facing_matches_visual_source": body.get("facing") == source["source_visual_spatial_grounding"][
                "facing"
            ],
            "energy_allows_movement": body.get("energy", 0) > 0,
            "cooldown_allows_movement": body.get("movement_cooldown_ticks") == 0,
            "balance_allows_locomotion": body.get("balance") == "stable",
            "hand_allows_reach": body.get("hand_state") == "empty",
            "contact_state_allows_normal_movement": body.get("contact_state") == "none",
            "body_schema_consistent_with_affordance_source": _body_matches_source(body, source),
        },
        "motor_readiness_preview": readiness,
        "human_summary": {
            "what_was_built": "A minimal sandbox body schema consistency runtime was created.",
            "what_it_checks": "The runtime checks body position, facing, energy, cooldown, balance, hand state, and contact state against visual-spatial motor affordance previews.",
            "what_it_outputs": "It previews whether step_forward, turn_left, turn_right, and reach_front are currently body-ready.",
            "what_is_blocked": "No motor action, selected motor intent, selected_action, final_action, direct command, pathfinding, memory write, predictor mutation, persistent body schema, production behavior, or proof claim is created.",
            "plain_result": "Qingyin can now check whether her sandbox body state permits a visual affordance, but still cannot act from it.",
        },
        "blocked_flags": {field: False for field in REQUIRED_BLOCKED_FLAGS},
    }


def validate_minimal_body_schema_affordance_consistency_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "minimal_body_schema_affordance_consistency_runtime",
        "record_version": "v0",
        "runtime_status": "completed_body_schema_affordance_consistency_preview",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _dict(record.get("source_affordance_bridge"), errors, "source_affordance_bridge_missing")
    if source.get("source_validated") is not True:
        errors.append("source_affordance_bridge_not_validated")
    if source.get("facing") not in VALID_FACINGS:
        errors.append("source_affordance_bridge_facing_invalid")
    if not _is_position(source.get("agent_position")):
        errors.append("source_affordance_bridge_agent_position_invalid")
    for field in ("front_blocked", "can_step_forward", "can_turn_left", "can_turn_right", "can_reach_front"):
        if not isinstance(source.get(field), bool):
            errors.append(f"source_affordance_bridge_{field}_not_boolean")

    body = _dict(record.get("minimal_body_schema_state"), errors, "minimal_body_schema_state_missing")
    _validate_body_schema_state(body, errors)

    consistency = _dict(record.get("affordance_consistency_result"), errors, "affordance_consistency_result_missing")
    expected_consistency = _derive_expected_consistency(source, body)
    for field, value in expected_consistency.items():
        if consistency.get(field) != value:
            errors.append(f"affordance_consistency_result_{field}_not_expected")

    readiness = _dict(record.get("motor_readiness_preview"), errors, "motor_readiness_preview_missing")
    expected_readiness = _derive_motor_readiness_from_source_summary(source, body)
    for field, value in expected_readiness.items():
        if readiness.get(field) != value:
            errors.append(f"motor_readiness_preview_{field}_not_expected")
    if readiness.get("selected_motor_intent") is not None:
        errors.append("motor_readiness_preview_selected_motor_intent_not_none")
    if readiness.get("motor_action_executed") is not False:
        errors.append("motor_readiness_preview_motor_action_executed_not_false")

    human = _dict(record.get("human_summary"), errors, "human_summary_missing")
    for field in ("what_was_built", "what_it_checks", "what_it_outputs", "what_is_blocked", "plain_result"):
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
        "body_schema_valid": _body_schema_valid(body),
        "position_consistent": consistency.get("body_position_matches_visual_source") is True,
        "facing_consistent": consistency.get("body_facing_matches_visual_source") is True,
        "body_schema_consistent": consistency.get("body_schema_consistent_with_affordance_source") is True,
        "step_forward_ready": readiness.get("step_forward_ready") is True,
        "turn_left_ready": readiness.get("turn_left_ready") is True,
        "turn_right_ready": readiness.get("turn_right_ready") is True,
        "reach_front_ready": readiness.get("reach_front_ready") is True,
        "front_blocked_by_affordance": readiness.get("front_blocked_by_affordance") is True,
        "body_blocks_movement": readiness.get("body_blocks_movement") is True,
        "preview_only": readiness.get("preview_only") is True,
        "motor_action_blocked": readiness.get("motor_action_executed") is False
        and blocked.get("motor_action_executed") is False,
        "selected_motor_intent_blocked": readiness.get("selected_motor_intent") is None
        and blocked.get("selected_motor_intent_created") is False,
        "selected_action_blocked": blocked.get("selected_action_created") is False,
        "final_action_blocked": blocked.get("final_action_created") is False,
        "direct_command_blocked": blocked.get("direct_command_created") is False,
        "pathfinding_blocked": blocked.get("pathfinding_used") is False,
        "memory_write_blocked": blocked.get("memory_write_performed") is False,
        "predictor_mutation_blocked": blocked.get("predictor_mutation_performed") is False,
        "persistent_body_schema_blocked": body.get("persistent_body_schema_written") is False
        and blocked.get("persistent_body_schema_written") is False,
        "production_behavior_blocked": blocked.get("production_behavior_changed") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claimed") is False,
    }


def run_minimal_body_schema_affordance_consistency_runtime_check() -> dict[str, Any]:
    source_result = run_visual_spatial_motor_affordance_bridge_minimal_check()
    empty_bridge, wall_bridge, item_bridge = source_result["valid_records"]
    valid_empty = build_minimal_body_schema_affordance_consistency_record(empty_bridge)
    valid_wall = build_minimal_body_schema_affordance_consistency_record(wall_bridge)
    valid_item = build_minimal_body_schema_affordance_consistency_record(item_bridge)
    records = [valid_empty, valid_wall, valid_item, *_invalid_records(valid_empty)]
    validation_results = [validate_minimal_body_schema_affordance_consistency_record(record) for record in records]
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
            "boundary_reason": "Adds minimal sandbox body schema consistency checks for visual motor affordances.",
        },
        "valid_records": [valid_empty, valid_wall, valid_item],
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A minimal body schema and affordance consistency runtime was added.",
            "what_changed": "Visual motor affordances can now be checked against body position, facing, energy, cooldown, balance, hand state, and contact state.",
            "what_is_blocked": "The runtime does not select, execute, command, pathfind, write memory, mutate predictors, persist body schema, change production behavior, or prove learning.",
            "plain_result": "The embodiment line now has a body-state gate between visual affordance and future motor intent.",
        },
        "valid_result_count": len(valid_results),
    }


def _default_body_schema_state(source: dict[str, Any]) -> dict[str, Any]:
    source_summary = source["source_visual_spatial_grounding"]
    return {
        "body_id": "qingyin_minimal_grid_body_v0",
        "body_scope": "sandbox_only",
        "position": list(source_summary["agent_position"]),
        "facing": source_summary["facing"],
        "locomotion_state": "ready",
        "hand_state": "empty",
        "energy": 1.0,
        "balance": "stable",
        "contact_state": "none",
        "movement_cooldown_ticks": 0,
        "last_motor_result": None,
        "persistent_body_schema_written": False,
    }


def _derive_motor_readiness(source: dict[str, Any], body: dict[str, Any]) -> dict[str, Any]:
    summary = source["affordance_summary"]
    return _derive_motor_readiness_from_source_summary(summary, body)


def _derive_motor_readiness_from_source_summary(source: dict[str, Any], body: dict[str, Any]) -> dict[str, Any]:
    energy_ok = body.get("energy", 0) > 0
    cooldown_ok = body.get("movement_cooldown_ticks") == 0
    balance_ok = body.get("balance") == "stable"
    hand_ok = body.get("hand_state") == "empty"
    contact_ok = body.get("contact_state") == "none"
    movement_body_ready = energy_ok and cooldown_ok and balance_ok and contact_ok
    blocked_reasons = []
    if not energy_ok:
        blocked_reasons.append("energy_depleted")
    if not cooldown_ok:
        blocked_reasons.append("movement_cooldown_active")
    if not balance_ok:
        blocked_reasons.append("balance_not_stable")
    if not contact_ok:
        blocked_reasons.append("contact_state_not_clear")
    if not hand_ok:
        blocked_reasons.append("hand_not_empty")
    return {
        "preview_created": True,
        "preview_scope": "sandbox_body_schema_motor_readiness_preview_only",
        "step_forward_ready": bool(source.get("can_step_forward")) and movement_body_ready,
        "turn_left_ready": bool(source.get("can_turn_left")) and movement_body_ready,
        "turn_right_ready": bool(source.get("can_turn_right")) and movement_body_ready,
        "reach_front_ready": bool(source.get("can_reach_front")) and hand_ok and contact_ok,
        "front_blocked_by_affordance": bool(source.get("front_blocked")),
        "body_blocks_movement": not movement_body_ready,
        "blocked_by_body_state_reasons": blocked_reasons,
        "selected_motor_intent": None,
        "motor_action_executed": False,
        "preview_only": True,
    }


def _derive_expected_consistency(source: dict[str, Any], body: dict[str, Any]) -> dict[str, bool]:
    return {
        "body_position_matches_visual_source": body.get("position") == source.get("agent_position"),
        "body_facing_matches_visual_source": body.get("facing") == source.get("facing"),
        "energy_allows_movement": body.get("energy", 0) > 0,
        "cooldown_allows_movement": body.get("movement_cooldown_ticks") == 0,
        "balance_allows_locomotion": body.get("balance") == "stable",
        "hand_allows_reach": body.get("hand_state") == "empty",
        "contact_state_allows_normal_movement": body.get("contact_state") == "none",
        "body_schema_consistent_with_affordance_source": _body_summary_matches_source(body, source),
    }


def _body_matches_source(body: dict[str, Any], source: dict[str, Any]) -> bool:
    source_summary = source["source_visual_spatial_grounding"]
    return body.get("position") == source_summary.get("agent_position") and body.get("facing") == source_summary.get(
        "facing"
    )


def _body_summary_matches_source(body: dict[str, Any], source: dict[str, Any]) -> bool:
    return body.get("position") == source.get("agent_position") and body.get("facing") == source.get("facing")


def _validate_body_schema_state(body: dict[str, Any], errors: list[str]) -> None:
    if body.get("body_id") != "qingyin_minimal_grid_body_v0":
        errors.append("minimal_body_schema_state_body_id_not_expected")
    if body.get("body_scope") != "sandbox_only":
        errors.append("minimal_body_schema_state_body_scope_not_expected")
    if not _is_position(body.get("position")):
        errors.append("minimal_body_schema_state_position_invalid")
    if body.get("facing") not in VALID_FACINGS:
        errors.append("minimal_body_schema_state_facing_invalid")
    if body.get("locomotion_state") not in VALID_LOCOMOTION_STATES:
        errors.append("minimal_body_schema_state_locomotion_state_invalid")
    if body.get("hand_state") not in VALID_HAND_STATES:
        errors.append("minimal_body_schema_state_hand_state_invalid")
    if not isinstance(body.get("energy"), (int, float)) or not 0.0 <= body.get("energy") <= 1.0:
        errors.append("minimal_body_schema_state_energy_invalid")
    if body.get("balance") not in VALID_BALANCE_STATES:
        errors.append("minimal_body_schema_state_balance_invalid")
    if body.get("contact_state") not in VALID_CONTACT_STATES:
        errors.append("minimal_body_schema_state_contact_state_invalid")
    if not isinstance(body.get("movement_cooldown_ticks"), int) or body.get("movement_cooldown_ticks") < 0:
        errors.append("minimal_body_schema_state_movement_cooldown_ticks_invalid")
    if body.get("persistent_body_schema_written") is not False:
        errors.append("minimal_body_schema_state_persistent_body_schema_written_not_false")


def _body_schema_valid(body: dict[str, Any]) -> bool:
    errors: list[str] = []
    _validate_body_schema_state(body, errors)
    return not errors


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def add(name: str, mutator) -> None:
        record = deepcopy(valid_record)
        mutator(record)
        record["invalid_case"] = name
        cases.append(record)

    add("wrong_record_type", lambda r: r.__setitem__("record_type", "body_motor_runtime"))
    add("source_not_validated", lambda r: r["source_affordance_bridge"].__setitem__("source_validated", False))
    add("position_mismatch", lambda r: r["minimal_body_schema_state"].__setitem__("position", [99, 99]))
    add("facing_mismatch", lambda r: r["minimal_body_schema_state"].__setitem__("facing", "east"))
    add("invalid_body_scope", lambda r: r["minimal_body_schema_state"].__setitem__("body_scope", "production"))
    add("energy_zero_but_step_ready", lambda r: (_set_body(r, "energy", 0.0), _set_ready(r, "step_forward_ready", True)))
    add(
        "cooldown_but_turn_ready",
        lambda r: (_set_body(r, "movement_cooldown_ticks", 2), _set_ready(r, "turn_left_ready", True)),
    )
    add("unstable_but_step_ready", lambda r: (_set_body(r, "balance", "unstable"), _set_ready(r, "step_forward_ready", True)))
    add("occupied_hand_but_reach_ready", lambda r: (_set_body(r, "hand_state", "occupied"), _set_ready(r, "reach_front_ready", True)))
    add(
        "contact_state_but_movement_ready",
        lambda r: (_set_body(r, "contact_state", "front_contact"), _set_ready(r, "step_forward_ready", True)),
    )
    add("wrong_position_consistency", lambda r: r["affordance_consistency_result"].__setitem__("body_position_matches_visual_source", False))
    add("wrong_energy_consistency", lambda r: r["affordance_consistency_result"].__setitem__("energy_allows_movement", False))
    add("selected_motor_intent", lambda r: r["motor_readiness_preview"].__setitem__("selected_motor_intent", "step_forward"))
    add("motor_executed", lambda r: r["motor_readiness_preview"].__setitem__("motor_action_executed", True))
    add("preview_not_created", lambda r: r["motor_readiness_preview"].__setitem__("preview_created", False))
    add("not_preview_only", lambda r: r["motor_readiness_preview"].__setitem__("preview_only", False))
    add("selected_motor_intent_flag", lambda r: r["blocked_flags"].__setitem__("selected_motor_intent_created", True))
    add("selected_action_created", lambda r: r["blocked_flags"].__setitem__("selected_action_created", True))
    add("final_action_created", lambda r: r["blocked_flags"].__setitem__("final_action_created", True))
    add("direct_command_created", lambda r: r["blocked_flags"].__setitem__("direct_command_created", True))
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


def _summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    valid_results = [result for result in results if result["valid"]]
    return {
        "body_schema_consistency_result_count": len(results),
        "valid_body_schema_consistency_count": len(valid_results),
        "invalid_body_schema_consistency_count": len(results) - len(valid_results),
        "source_validated_count": _count_valid(valid_results, "source_validated"),
        "body_schema_valid_count": _count_valid(valid_results, "body_schema_valid"),
        "position_consistent_count": _count_valid(valid_results, "position_consistent"),
        "facing_consistent_count": _count_valid(valid_results, "facing_consistent"),
        "body_schema_consistent_count": _count_valid(valid_results, "body_schema_consistent"),
        "step_forward_ready_count": _count_valid(valid_results, "step_forward_ready"),
        "turn_left_ready_count": _count_valid(valid_results, "turn_left_ready"),
        "turn_right_ready_count": _count_valid(valid_results, "turn_right_ready"),
        "reach_front_ready_count": _count_valid(valid_results, "reach_front_ready"),
        "front_blocked_by_affordance_count": _count_valid(valid_results, "front_blocked_by_affordance"),
        "body_blocks_movement_count": _count_valid(valid_results, "body_blocks_movement"),
        "preview_only_count": _count_valid(valid_results, "preview_only"),
        "motor_action_blocked_count": _count_valid(valid_results, "motor_action_blocked"),
        "selected_motor_intent_blocked_count": _count_valid(valid_results, "selected_motor_intent_blocked"),
        "selected_action_blocked_count": _count_valid(valid_results, "selected_action_blocked"),
        "final_action_blocked_count": _count_valid(valid_results, "final_action_blocked"),
        "direct_command_blocked_count": _count_valid(valid_results, "direct_command_blocked"),
        "pathfinding_blocked_count": _count_valid(valid_results, "pathfinding_blocked"),
        "memory_write_blocked_count": _count_valid(valid_results, "memory_write_blocked"),
        "predictor_mutation_blocked_count": _count_valid(valid_results, "predictor_mutation_blocked"),
        "persistent_body_schema_blocked_count": _count_valid(valid_results, "persistent_body_schema_blocked"),
        "production_behavior_blocked_count": _count_valid(valid_results, "production_behavior_blocked"),
        "proof_claim_blocked_count": _count_valid(valid_results, "proof_claim_blocked"),
    }


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["body_schema_consistency_result_count"] == 32
        and summary["valid_body_schema_consistency_count"] == 3
        and summary["invalid_body_schema_consistency_count"] == 29
        and summary["source_validated_count"] == 3
        and summary["body_schema_valid_count"] == 3
        and summary["position_consistent_count"] == 3
        and summary["facing_consistent_count"] == 3
        and summary["body_schema_consistent_count"] == 3
        and summary["step_forward_ready_count"] == 2
        and summary["turn_left_ready_count"] == 3
        and summary["turn_right_ready_count"] == 3
        and summary["reach_front_ready_count"] == 1
        and summary["front_blocked_by_affordance_count"] == 1
        and summary["body_blocks_movement_count"] == 0
        and summary["preview_only_count"] == 3
        and summary["motor_action_blocked_count"] == 3
        and summary["selected_motor_intent_blocked_count"] == 3
        and summary["selected_action_blocked_count"] == 3
        and summary["final_action_blocked_count"] == 3
        and summary["direct_command_blocked_count"] == 3
        and summary["pathfinding_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_mutation_blocked_count"] == 3
        and summary["persistent_body_schema_blocked_count"] == 3
        and summary["production_behavior_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
    )


def _set_body(record: dict[str, Any], field: str, value: Any) -> None:
    record["minimal_body_schema_state"][field] = value


def _set_ready(record: dict[str, Any], field: str, value: Any) -> None:
    record["motor_readiness_preview"][field] = value


def _dict(value: Any, errors: list[str], error_code: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(error_code)
        return {}
    return value


def _is_position(value: Any) -> bool:
    return isinstance(value, list) and len(value) == 2 and all(isinstance(item, int) for item in value)


def _count_valid(results: list[dict[str, Any]], field: str) -> int:
    return sum(1 for result in results if result.get(field) is True)
