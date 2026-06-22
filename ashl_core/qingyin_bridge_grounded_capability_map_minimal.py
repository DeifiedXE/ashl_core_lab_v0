"""Build a grounded Qingyin Bridge capability map from sandbox affordance previews."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .visual_spatial_motor_affordance_bridge_minimal import (
    build_visual_spatial_motor_affordance_bridge_record,
    validate_visual_spatial_motor_affordance_bridge_record,
)


COMMAND = "run-qingyin-bridge-grounded-capability-map-minimal-check"
FLOW = "qingyin_bridge_grounded_capability_map_minimal_v0"
PACKAGE_ID = "PKG-Phase0-QingyinBridgeGroundedCapabilityMap-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b134"
BOUNDARY_INDEX_AFTER = "2026-06-09-b135"

CAPABILITY_BY_MOTOR_INTENT = {
    "step_forward": "sandbox.body.step_forward",
    "turn_left": "sandbox.body.turn_left",
    "turn_right": "sandbox.body.turn_right",
    "reach_front": "sandbox.body.reach_front",
}

RISK_BY_CAPABILITY = {
    "sandbox.body.step_forward": "low",
    "sandbox.body.turn_left": "low",
    "sandbox.body.turn_right": "low",
    "sandbox.body.reach_front": "low",
}

REQUIRED_BLOCKED_FLAGS = (
    "action_intent_created",
    "action_gateway_called",
    "selected_motor_intent_created",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "sandbox_execution_created",
    "feedback_packet_created",
    "feedback_to_endocrine_direct",
    "feedback_to_tendency_direct",
    "candidate_reordering_created",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "semantic_vision",
    "object_recognition",
    "raw_api_access",
    "production_behavior_changed",
    "proof_of_learning_claim",
)


def build_qingyin_bridge_grounded_capability_map_record(
    affordance_bridge_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = deepcopy(affordance_bridge_record) if affordance_bridge_record is not None else (
        build_visual_spatial_motor_affordance_bridge_record()
    )
    validation = validate_visual_spatial_motor_affordance_bridge_record(source)
    if not validation["valid"]:
        raise ValueError("affordance_bridge_record must validate before capability map")

    source_summary = source["affordance_summary"]
    source_visual = source["source_visual_spatial_grounding"]
    front_symbol = source_summary["front_symbol"]
    visible_object = _build_visible_front_object(source_visual, front_symbol)
    declared_capabilities = _build_declared_capabilities(source["motor_intent_preview"]["candidate_motor_intents"])
    bindings = _build_bindings(visible_object, declared_capabilities, source_summary)

    return {
        "record_type": "qingyin_bridge_grounded_capability_map",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_affordance_bridge": {
            "record_type": source["record_type"],
            "bridge_status": source["bridge_status"],
            "source_validated": True,
            "front_symbol": front_symbol,
            "front_body_direction": source_visual["front_body_direction"],
            "front_distance_forward": source_visual["front_distance_forward"],
            "affordance_preview_created": source["motor_intent_preview"]["preview_created"],
            "selected_motor_intent": source["motor_intent_preview"]["selected_motor_intent"],
            "motor_action_executed": source["motor_intent_preview"]["motor_action_executed"],
        },
        "visual_simulation_eye": {
            "eye_mode": "symbolic_visual_object_list",
            "visible_objects": [visible_object],
            "real_image_vision": False,
            "object_recognition": False,
            "semantic_vision": False,
        },
        "operational_simulation_eye": {
            "eye_mode": "sandbox_affordance_capability_manifest",
            "declared_capabilities": declared_capabilities,
            "raw_api_access": False,
            "action_gateway_called": False,
            "execution_allowed_by_eye": False,
        },
        "capability_map": {
            "environment_id": "phase0_symbolic_body_sandbox_v0",
            "map_mode": "grounded_visual_operational_capability_map",
            "visible_objects": [visible_object],
            "declared_capabilities": declared_capabilities,
            "bindings": bindings,
            "capability_map_created": True,
            "action_intent_created": False,
            "action_gateway_called": False,
            "execution_created": False,
        },
        "grounding_alignment": {
            "visual_object_source": "source_affordance_bridge.front_symbol",
            "operational_source": "source_affordance_bridge.motor_intent_preview",
            "declared_and_discovered_kept_separate": True,
            "symbolic_text_grounding_only": True,
            "front_symbol": front_symbol,
            "grounded_text_token": f"front_symbol:{front_symbol}",
            "semantic_interpretation_used": False,
        },
        "feedback_boundary": {
            "feedback_packet_created": False,
            "feedback_must_enter_trace_first": True,
            "direct_endocrine_feed_allowed": False,
            "direct_tendency_feed_allowed": False,
            "requires_proto_purpose_review_approval_before_influence": True,
        },
        "human_summary": {
            "what_was_built": "A grounded Qingyin Bridge capability map was built from existing sandbox visual affordance previews.",
            "what_it_connects": "The map connects a symbolic visible front-cell object to sandbox body capabilities such as step_forward, turn_left, turn_right, and reach_front.",
            "what_is_grounded": "The visible front symbol is echoed as a symbolic text token and bound to declared sandbox capabilities without semantic vision.",
            "what_is_blocked": "No action intent, action gateway call, selected action, final action, direct command, execution, feedback packet, direct endocrine/tendency feed, memory write, predictor use, raw API access, production behavior, or proof claim is created.",
            "plain_result": "Qingyin Bridge can now represent what the grounded sandbox front cell affords as a capability map, but it still cannot act from that map.",
        },
        "blocked_flags": {field: False for field in REQUIRED_BLOCKED_FLAGS},
    }


def validate_qingyin_bridge_grounded_capability_map_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "qingyin_bridge_grounded_capability_map",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _dict(record.get("source_affordance_bridge"), errors, "source_affordance_bridge_missing")
    front_symbol = source.get("front_symbol")
    if source.get("record_type") != "visual_spatial_motor_affordance_bridge":
        errors.append("source_record_type_not_expected")
    if source.get("source_validated") is not True:
        errors.append("source_not_validated")
    if source.get("front_body_direction") != "front":
        errors.append("source_front_body_direction_not_front")
    if source.get("front_distance_forward") != 1:
        errors.append("source_front_distance_forward_not_one")
    if source.get("affordance_preview_created") is not True:
        errors.append("source_affordance_preview_not_created")
    if source.get("selected_motor_intent") is not None:
        errors.append("source_selected_motor_intent_not_none")
    if source.get("motor_action_executed") is not False:
        errors.append("source_motor_action_executed_not_false")

    visual_eye = _dict(record.get("visual_simulation_eye"), errors, "visual_simulation_eye_missing")
    if visual_eye.get("eye_mode") != "symbolic_visual_object_list":
        errors.append("visual_eye_mode_not_expected")
    for field in ("real_image_vision", "object_recognition", "semantic_vision"):
        if visual_eye.get(field) is not False:
            errors.append(f"visual_eye_{field}_not_false")
    visible_objects = _list(visual_eye.get("visible_objects"), errors, "visual_eye_visible_objects_missing")
    visual_object = visible_objects[0] if visible_objects else {}
    _validate_visible_object(visual_object, front_symbol, errors, "visual_eye")

    operational_eye = _dict(
        record.get("operational_simulation_eye"),
        errors,
        "operational_simulation_eye_missing",
    )
    if operational_eye.get("eye_mode") != "sandbox_affordance_capability_manifest":
        errors.append("operational_eye_mode_not_expected")
    for field in ("raw_api_access", "action_gateway_called", "execution_allowed_by_eye"):
        if operational_eye.get(field) is not False:
            errors.append(f"operational_eye_{field}_not_false")
    declared = _list(operational_eye.get("declared_capabilities"), errors, "declared_capabilities_missing")
    _validate_declared_capabilities(declared, errors, "operational_eye")

    capability_map = _dict(record.get("capability_map"), errors, "capability_map_missing")
    if capability_map.get("environment_id") != "phase0_symbolic_body_sandbox_v0":
        errors.append("capability_map_environment_id_not_expected")
    if capability_map.get("map_mode") != "grounded_visual_operational_capability_map":
        errors.append("capability_map_mode_not_expected")
    if capability_map.get("capability_map_created") is not True:
        errors.append("capability_map_not_created")
    for field in ("action_intent_created", "action_gateway_called", "execution_created"):
        if capability_map.get(field) is not False:
            errors.append(f"capability_map_{field}_not_false")
    map_visible = _list(capability_map.get("visible_objects"), errors, "capability_map_visible_objects_missing")
    map_declared = _list(capability_map.get("declared_capabilities"), errors, "capability_map_declared_missing")
    bindings = _list(capability_map.get("bindings"), errors, "capability_map_bindings_missing")
    if map_visible and map_visible != visible_objects:
        errors.append("capability_map_visible_objects_mismatch")
    if map_declared and map_declared != declared:
        errors.append("capability_map_declared_capabilities_mismatch")
    _validate_bindings(bindings, declared, front_symbol, errors)

    alignment = _dict(record.get("grounding_alignment"), errors, "grounding_alignment_missing")
    expected_alignment = {
        "visual_object_source": "source_affordance_bridge.front_symbol",
        "operational_source": "source_affordance_bridge.motor_intent_preview",
        "declared_and_discovered_kept_separate": True,
        "symbolic_text_grounding_only": True,
        "front_symbol": front_symbol,
        "grounded_text_token": f"front_symbol:{front_symbol}",
        "semantic_interpretation_used": False,
    }
    for field, value in expected_alignment.items():
        if alignment.get(field) != value:
            errors.append(f"grounding_alignment_{field}_not_expected")

    feedback = _dict(record.get("feedback_boundary"), errors, "feedback_boundary_missing")
    expected_feedback = {
        "feedback_packet_created": False,
        "feedback_must_enter_trace_first": True,
        "direct_endocrine_feed_allowed": False,
        "direct_tendency_feed_allowed": False,
        "requires_proto_purpose_review_approval_before_influence": True,
    }
    for field, value in expected_feedback.items():
        if feedback.get(field) != value:
            errors.append(f"feedback_boundary_{field}_not_expected")

    human = _dict(record.get("human_summary"), errors, "human_summary_missing")
    for field in ("what_was_built", "what_it_connects", "what_is_grounded", "what_is_blocked", "plain_result"):
        if not isinstance(human.get(field), str) or not human.get(field).strip():
            errors.append(f"human_summary_{field}_empty")

    blocked = _dict(record.get("blocked_flags"), errors, "blocked_flags_missing")
    for field in REQUIRED_BLOCKED_FLAGS:
        if blocked.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")

    return {
        "valid": not errors,
        "error_codes": errors,
        "capability_map_created": capability_map.get("capability_map_created") is True,
        "visible_object_count": len(visible_objects),
        "declared_capability_count": len(declared),
        "binding_count": len(bindings),
        "front_symbol": front_symbol,
        "grounded_text_token": alignment.get("grounded_text_token"),
        "declared_and_discovered_separate": alignment.get("declared_and_discovered_kept_separate") is True,
        "symbolic_text_grounding_only": alignment.get("symbolic_text_grounding_only") is True,
        "semantic_vision_blocked": visual_eye.get("semantic_vision") is False
        and alignment.get("semantic_interpretation_used") is False
        and blocked.get("semantic_vision") is False,
        "object_recognition_blocked": visual_eye.get("object_recognition") is False
        and blocked.get("object_recognition") is False,
        "action_intent_blocked": capability_map.get("action_intent_created") is False
        and blocked.get("action_intent_created") is False,
        "action_gateway_blocked": capability_map.get("action_gateway_called") is False
        and operational_eye.get("action_gateway_called") is False
        and blocked.get("action_gateway_called") is False,
        "execution_blocked": capability_map.get("execution_created") is False
        and blocked.get("sandbox_execution_created") is False,
        "feedback_packet_blocked": feedback.get("feedback_packet_created") is False
        and blocked.get("feedback_packet_created") is False,
        "direct_feedback_to_endocrine_blocked": feedback.get("direct_endocrine_feed_allowed") is False
        and blocked.get("feedback_to_endocrine_direct") is False,
        "direct_feedback_to_tendency_blocked": feedback.get("direct_tendency_feed_allowed") is False
        and blocked.get("feedback_to_tendency_direct") is False,
        "memory_write_blocked": blocked.get("memory_write") is False,
        "predictor_use_blocked": blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False
        and blocked.get("predictor_modified") is False,
        "raw_api_blocked": operational_eye.get("raw_api_access") is False and blocked.get("raw_api_access") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claim") is False,
    }


def run_qingyin_bridge_grounded_capability_map_minimal_check() -> dict[str, Any]:
    valid_empty = build_qingyin_bridge_grounded_capability_map_record()
    valid_wall = build_qingyin_bridge_grounded_capability_map_record(_source_with_front_symbol("w"))
    valid_item = build_qingyin_bridge_grounded_capability_map_record(_source_with_front_symbol("i"))
    records = [valid_empty, valid_wall, valid_item, *_invalid_records(valid_item)]
    validation_results = [validate_qingyin_bridge_grounded_capability_map_record(record) for record in records]
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
            "boundary_reason": "Adds a grounded Qingyin Bridge capability map from existing sandbox visual affordance previews.",
        },
        "valid_records": [valid_empty, valid_wall, valid_item],
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A minimal Qingyin Bridge capability map was built from grounded sandbox affordances.",
            "what_changed": "The bridge can now represent visible front-cell symbols and sandbox body capabilities in one capability map.",
            "what_is_blocked": "The map does not create action intent, call an action gateway, execute, create feedback packets, feed endocrine/tendency systems, write memory, use predictors, access raw APIs, or prove learning.",
            "plain_result": "Qingyin can now see a grounded capability map for the sandbox front cell, but she still cannot act from it.",
        },
        "valid_result_count": len(valid_results),
    }


def _build_visible_front_object(source_visual: dict[str, Any], front_symbol: str) -> dict[str, Any]:
    return {
        "id": "sandbox.front_cell",
        "object_kind": "symbolic_front_cell",
        "front_symbol": front_symbol,
        "body_direction": source_visual["front_body_direction"],
        "distance_forward": source_visual["front_distance_forward"],
        "world_position": source_visual["front_world_position"],
        "visible": True,
        "source": "visual_spatial_grounding",
        "confidence": 1.0,
        "semantic_label": None,
    }


def _build_declared_capabilities(motor_intents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    capabilities: list[dict[str, Any]] = []
    for item in motor_intents:
        motor_intent = item["motor_intent"]
        capability_id = CAPABILITY_BY_MOTOR_INTENT[motor_intent]
        capabilities.append(
            {
                "id": capability_id,
                "kind": "sandbox_body_action_capability",
                "source_motor_intent": motor_intent,
                "available": item["available"],
                "risk": RISK_BY_CAPABILITY[capability_id],
                "permission": "sandbox_only_review_not_required_for_map",
                "reversible": True,
                "source": "visual_spatial_motor_affordance_bridge",
                "confidence": 1.0,
                "execution_allowed": False,
            }
        )
    return capabilities


def _build_bindings(
    visible_object: dict[str, Any],
    declared_capabilities: list[dict[str, Any]],
    source_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    bindings: list[dict[str, Any]] = []
    for capability in declared_capabilities:
        capability_id = capability["id"]
        motor_intent = capability["source_motor_intent"]
        if motor_intent == "step_forward":
            reason = "front_cell_step_affordance"
            available = source_summary["can_step_forward"]
        elif motor_intent == "reach_front":
            reason = "front_cell_contact_affordance"
            available = source_summary["can_reach_front"]
        else:
            reason = "body_turn_affordance"
            available = True
        bindings.append(
            {
                "visual_object": visible_object["id"],
                "capability": capability_id,
                "binding_source": "grounded_front_cell_affordance",
                "binding_reason": reason,
                "binding_confidence": 1.0,
                "available": available,
                "creates_action_intent": False,
            }
        )
    return bindings


def _source_with_front_symbol(symbol: str) -> dict[str, Any]:
    source = build_visual_spatial_motor_affordance_bridge_record()
    source["source_visual_spatial_grounding"]["front_symbol"] = symbol
    source["affordance_rule_set"]["supported_front_symbols"] = ["e", "w", "x", "i", "d", "g"]
    source["body_relative_affordance_candidates"] = _affordances_for_symbol(symbol)
    source["motor_intent_preview"]["candidate_motor_intents"] = _motor_intents_for_affordances(
        source["body_relative_affordance_candidates"]
    )
    source["affordance_summary"] = {
        "front_symbol": symbol,
        "front_blocked": source["body_relative_affordance_candidates"]["can_step_forward"]["blocked"],
        "can_step_forward": source["body_relative_affordance_candidates"]["can_step_forward"]["available"],
        "can_turn_left": True,
        "can_turn_right": True,
        "can_reach_front": source["body_relative_affordance_candidates"]["can_reach_front"]["available"],
        "front_contact_possible": source["body_relative_affordance_candidates"]["front_contact_possible"]["available"],
        "preview_only": True,
    }
    return source


def _affordances_for_symbol(symbol: str) -> dict[str, dict[str, Any]]:
    passable = symbol in ("e", "i", "d", "g")
    contact = symbol in ("i", "d", "g")
    return {
        "can_step_forward": {
            "available": passable,
            "blocked": not passable,
            "reason": "front_cell_passable" if passable else "front_cell_blocked",
            "source_front_symbol": symbol,
        },
        "can_turn_left": {
            "available": True,
            "blocked": False,
            "reason": "turning_does_not_require_front_cell_clearance",
            "source_front_symbol": symbol,
        },
        "can_turn_right": {
            "available": True,
            "blocked": False,
            "reason": "turning_does_not_require_front_cell_clearance",
            "source_front_symbol": symbol,
        },
        "can_reach_front": {
            "available": contact,
            "blocked": not contact,
            "reason": "front_contact_symbol_present" if contact else "no_front_contact_symbol",
            "source_front_symbol": symbol,
        },
        "front_contact_possible": {
            "available": contact,
            "blocked": not contact,
            "reason": "front_contact_symbol_present" if contact else "no_front_contact_symbol",
            "source_front_symbol": symbol,
        },
    }


def _motor_intents_for_affordances(affordances: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
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


def _validate_visible_object(obj: dict[str, Any], front_symbol: Any, errors: list[str], prefix: str) -> None:
    expected = {
        "id": "sandbox.front_cell",
        "object_kind": "symbolic_front_cell",
        "front_symbol": front_symbol,
        "body_direction": "front",
        "distance_forward": 1,
        "visible": True,
        "source": "visual_spatial_grounding",
        "confidence": 1.0,
        "semantic_label": None,
    }
    for field, value in expected.items():
        if obj.get(field) != value:
            errors.append(f"{prefix}_visible_object_{field}_not_expected")
    if not isinstance(obj.get("world_position"), list) or len(obj.get("world_position", [])) != 2:
        errors.append(f"{prefix}_visible_object_world_position_not_expected")


def _validate_declared_capabilities(items: list[Any], errors: list[str], prefix: str) -> None:
    expected_ids = list(CAPABILITY_BY_MOTOR_INTENT.values())
    ids = [item.get("id") for item in items if isinstance(item, dict)]
    if ids != expected_ids:
        errors.append(f"{prefix}_declared_capability_ids_not_expected")
    for item in items:
        if not isinstance(item, dict):
            errors.append(f"{prefix}_declared_capability_not_dict")
            continue
        capability_id = item.get("id")
        if item.get("kind") != "sandbox_body_action_capability":
            errors.append(f"{prefix}_{capability_id}_kind_not_expected")
        if item.get("risk") != "low":
            errors.append(f"{prefix}_{capability_id}_risk_not_low")
        if item.get("permission") != "sandbox_only_review_not_required_for_map":
            errors.append(f"{prefix}_{capability_id}_permission_not_expected")
        if item.get("reversible") is not True:
            errors.append(f"{prefix}_{capability_id}_reversible_not_true")
        if item.get("source") != "visual_spatial_motor_affordance_bridge":
            errors.append(f"{prefix}_{capability_id}_source_not_expected")
        if item.get("confidence") != 1.0:
            errors.append(f"{prefix}_{capability_id}_confidence_not_expected")
        if item.get("execution_allowed") is not False:
            errors.append(f"{prefix}_{capability_id}_execution_allowed_not_false")


def _validate_bindings(
    bindings: list[Any],
    declared: list[dict[str, Any]],
    front_symbol: Any,
    errors: list[str],
) -> None:
    if len(bindings) != len(declared):
        errors.append("binding_count_not_declared_capability_count")
    capabilities = [item.get("id") for item in declared if isinstance(item, dict)]
    binding_capabilities = [item.get("capability") for item in bindings if isinstance(item, dict)]
    if binding_capabilities != capabilities:
        errors.append("binding_capabilities_not_expected")
    expected_available = {
        "sandbox.body.step_forward": front_symbol in ("e", "i", "d", "g"),
        "sandbox.body.turn_left": True,
        "sandbox.body.turn_right": True,
        "sandbox.body.reach_front": front_symbol in ("i", "d", "g"),
    }
    for item in bindings:
        if not isinstance(item, dict):
            errors.append("binding_not_dict")
            continue
        cap = item.get("capability")
        if item.get("visual_object") != "sandbox.front_cell":
            errors.append(f"binding_{cap}_visual_object_not_expected")
        if item.get("binding_source") != "grounded_front_cell_affordance":
            errors.append(f"binding_{cap}_source_not_expected")
        if item.get("binding_confidence") != 1.0:
            errors.append(f"binding_{cap}_confidence_not_expected")
        if item.get("available") != expected_available.get(cap):
            errors.append(f"binding_{cap}_available_not_expected")
        if item.get("creates_action_intent") is not False:
            errors.append(f"binding_{cap}_creates_action_intent_not_false")


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def add(name: str, mutator) -> None:
        record = deepcopy(valid_record)
        mutator(record)
        record["invalid_case"] = name
        cases.append(record)

    add("wrong_record_type", lambda r: r.__setitem__("record_type", "raw_api_capability_map"))
    add("wrong_boundary_after", lambda r: r.__setitem__("boundary_index_after", BOUNDARY_INDEX_BEFORE))
    add("source_not_validated", lambda r: r["source_affordance_bridge"].__setitem__("source_validated", False))
    add("source_selected_motor_intent", lambda r: r["source_affordance_bridge"].__setitem__("selected_motor_intent", "reach_front"))
    add("visual_eye_semantic_vision", lambda r: r["visual_simulation_eye"].__setitem__("semantic_vision", True))
    add("visual_eye_object_recognition", lambda r: r["visual_simulation_eye"].__setitem__("object_recognition", True))
    add("visible_object_wrong_symbol", lambda r: r["visual_simulation_eye"]["visible_objects"][0].__setitem__("front_symbol", "w"))
    add("operational_eye_raw_api", lambda r: r["operational_simulation_eye"].__setitem__("raw_api_access", True))
    add("operational_eye_gateway_called", lambda r: r["operational_simulation_eye"].__setitem__("action_gateway_called", True))
    add("declared_capability_missing", lambda r: r["operational_simulation_eye"].__setitem__("declared_capabilities", []))
    add("declared_capability_execution_allowed", lambda r: r["operational_simulation_eye"]["declared_capabilities"][0].__setitem__("execution_allowed", True))
    add("capability_map_not_created", lambda r: r["capability_map"].__setitem__("capability_map_created", False))
    add("capability_map_action_intent", lambda r: r["capability_map"].__setitem__("action_intent_created", True))
    add("capability_map_gateway_called", lambda r: r["capability_map"].__setitem__("action_gateway_called", True))
    add("capability_map_execution_created", lambda r: r["capability_map"].__setitem__("execution_created", True))
    add("binding_missing", lambda r: r["capability_map"].__setitem__("bindings", []))
    add("binding_creates_intent", lambda r: r["capability_map"]["bindings"][0].__setitem__("creates_action_intent", True))
    add("declared_discovered_mixed", lambda r: r["grounding_alignment"].__setitem__("declared_and_discovered_kept_separate", False))
    add("not_symbolic_text_grounding", lambda r: r["grounding_alignment"].__setitem__("symbolic_text_grounding_only", False))
    add("semantic_interpretation", lambda r: r["grounding_alignment"].__setitem__("semantic_interpretation_used", True))
    add("feedback_packet_created", lambda r: r["feedback_boundary"].__setitem__("feedback_packet_created", True))
    add("feedback_not_trace_first", lambda r: r["feedback_boundary"].__setitem__("feedback_must_enter_trace_first", False))
    add("direct_endocrine_feed", lambda r: r["feedback_boundary"].__setitem__("direct_endocrine_feed_allowed", True))
    add("direct_tendency_feed", lambda r: r["feedback_boundary"].__setitem__("direct_tendency_feed_allowed", True))
    add("empty_human_summary", lambda r: r["human_summary"].__setitem__("plain_result", ""))
    for flag in REQUIRED_BLOCKED_FLAGS:
        add(f"blocked_{flag}", lambda r, flag=flag: r["blocked_flags"].__setitem__(flag, True))
    return cases


def _summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    valid_results = [result for result in results if result["valid"]]
    return {
        "capability_map_result_count": len(results),
        "valid_capability_map_count": len(valid_results),
        "invalid_capability_map_count": len(results) - len(valid_results),
        "capability_map_created_count": _count_valid(valid_results, "capability_map_created"),
        "visible_object_total": sum(result.get("visible_object_count", 0) for result in valid_results),
        "declared_capability_total": sum(result.get("declared_capability_count", 0) for result in valid_results),
        "binding_total": sum(result.get("binding_count", 0) for result in valid_results),
        "front_empty_record_count": sum(1 for result in valid_results if result.get("front_symbol") == "e"),
        "front_wall_record_count": sum(1 for result in valid_results if result.get("front_symbol") == "w"),
        "front_item_record_count": sum(1 for result in valid_results if result.get("front_symbol") == "i"),
        "declared_and_discovered_separate_count": _count_valid(valid_results, "declared_and_discovered_separate"),
        "symbolic_text_grounding_only_count": _count_valid(valid_results, "symbolic_text_grounding_only"),
        "semantic_vision_blocked_count": _count_valid(valid_results, "semantic_vision_blocked"),
        "object_recognition_blocked_count": _count_valid(valid_results, "object_recognition_blocked"),
        "action_intent_blocked_count": _count_valid(valid_results, "action_intent_blocked"),
        "action_gateway_blocked_count": _count_valid(valid_results, "action_gateway_blocked"),
        "execution_blocked_count": _count_valid(valid_results, "execution_blocked"),
        "feedback_packet_blocked_count": _count_valid(valid_results, "feedback_packet_blocked"),
        "direct_feedback_to_endocrine_blocked_count": _count_valid(valid_results, "direct_feedback_to_endocrine_blocked"),
        "direct_feedback_to_tendency_blocked_count": _count_valid(valid_results, "direct_feedback_to_tendency_blocked"),
        "memory_write_blocked_count": _count_valid(valid_results, "memory_write_blocked"),
        "predictor_use_blocked_count": _count_valid(valid_results, "predictor_use_blocked"),
        "raw_api_blocked_count": _count_valid(valid_results, "raw_api_blocked"),
        "proof_claim_blocked_count": _count_valid(valid_results, "proof_claim_blocked"),
    }


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["capability_map_result_count"] == 50
        and summary["valid_capability_map_count"] == 3
        and summary["invalid_capability_map_count"] == 47
        and summary["capability_map_created_count"] == 3
        and summary["visible_object_total"] == 3
        and summary["declared_capability_total"] == 12
        and summary["binding_total"] == 12
        and summary["front_empty_record_count"] == 1
        and summary["front_wall_record_count"] == 1
        and summary["front_item_record_count"] == 1
        and summary["action_intent_blocked_count"] == 3
        and summary["action_gateway_blocked_count"] == 3
        and summary["execution_blocked_count"] == 3
        and summary["feedback_packet_blocked_count"] == 3
        and summary["direct_feedback_to_endocrine_blocked_count"] == 3
        and summary["direct_feedback_to_tendency_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["raw_api_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
    )


def _count_valid(results: list[dict[str, Any]], field: str) -> int:
    return sum(1 for result in results if result.get(field) is True)


def _dict(value: Any, errors: list[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(code)
        return {}
    return value


def _list(value: Any, errors: list[str], code: str) -> list[Any]:
    if not isinstance(value, list):
        errors.append(code)
        return []
    return value
