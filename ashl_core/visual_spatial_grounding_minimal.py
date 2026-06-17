"""Body-relative spatial grounding from symbolic first-person visual input."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .simulated_vision_larger_sandbox import (
    create_simulated_vision_larger_sandbox,
    build_initial_larger_sandbox_state,
    front_symbol_from_larger_viewport,
    render_larger_sandbox_viewport,
)
from .simulated_vision_sandbox import (
    FIRST_PERSON_AGENT_VIEWPORT_POSITION,
    FIRST_PERSON_FAR_FRONT_SYMBOL_POSITION,
    FIRST_PERSON_FRONT_SYMBOL_POSITION,
    viewport_cells_for_facing,
)


COMMAND = "run-visual-spatial-grounding-minimal-check"
FLOW = "visual_spatial_grounding_minimal_v0"
PACKAGE_ID = "PKG-Phase0-VisualSpatialGrounding-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b110"
BOUNDARY_INDEX_AFTER = "2026-06-09-b111"

REQUIRED_BLOCKED_FLAGS = (
    "real_image_vision",
    "object_recognition",
    "semantic_vision",
    "llm_vision_used",
    "full_map_visible_to_agent",
    "active_focus_applied",
    "action_selection_influence",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "pathfinding_used",
    "route_planner_added",
    "production_behavior_changed",
    "real_navigation_changed",
    "ui_behavior_changed",
    "memory_write_performed",
    "retention_write_performed",
    "predictor_mutation_performed",
    "persistent_body_schema_written",
    "subjective_visual_experience_claimed",
    "proof_of_learning_claimed",
)

EXPECTED_SPATIAL_CELL_COUNT = 9


def build_visual_spatial_grounding_record(
    source_observation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    observation = deepcopy(source_observation) if source_observation is not None else _demo_source_observation()
    spatial_cells = _build_spatial_cells(observation)
    front_cell = _cell_at_viewport_position(spatial_cells, FIRST_PERSON_FRONT_SYMBOL_POSITION)
    far_front_cell = _cell_at_viewport_position(spatial_cells, FIRST_PERSON_FAR_FRONT_SYMBOL_POSITION)
    agent_cell = _cell_at_viewport_position(spatial_cells, FIRST_PERSON_AGENT_VIEWPORT_POSITION)

    return {
        "record_type": "visual_spatial_grounding",
        "record_version": "v0",
        "spatial_grounding_status": "completed_body_relative_visual_spatial_trace",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_visual_observation": observation,
        "body_relative_frame": {
            "agent_position": observation["agent_position"],
            "facing": observation["facing"],
            "agent_viewport_position": FIRST_PERSON_AGENT_VIEWPORT_POSITION,
            "front_symbol_position": FIRST_PERSON_FRONT_SYMBOL_POSITION,
            "far_front_symbol_position": FIRST_PERSON_FAR_FRONT_SYMBOL_POSITION,
            "body_relative_coordinates_created": True,
            "distance_estimates_created": True,
            "direction_labels_created": True,
            "position_direction_distance_trace": True,
        },
        "spatial_cells": spatial_cells,
        "front_cell_spatial_summary": {
            "front_symbol": front_cell["symbol"],
            "world_position": front_cell["world_position"],
            "body_direction": front_cell["body_direction"],
            "distance_forward": front_cell["distance_forward"],
            "manhattan_distance_from_agent": front_cell["manhattan_distance_from_agent"],
            "immediate_front": True,
        },
        "far_front_cell_spatial_summary": {
            "far_front_symbol": far_front_cell["symbol"],
            "world_position": far_front_cell["world_position"],
            "body_direction": far_front_cell["body_direction"],
            "distance_forward": far_front_cell["distance_forward"],
            "manhattan_distance_from_agent": far_front_cell["manhattan_distance_from_agent"],
        },
        "agent_cell_spatial_summary": {
            "agent_symbol": agent_cell["symbol"],
            "world_position": agent_cell["world_position"],
            "body_direction": agent_cell["body_direction"],
            "distance_forward": agent_cell["distance_forward"],
            "manhattan_distance_from_agent": agent_cell["manhattan_distance_from_agent"],
        },
        "grounding_scope": {
            "symbolic_first_person_viewport_only": True,
            "visible_cells_only": True,
            "full_map_visible_to_agent": False,
            "world_positions_from_sandbox_fixture": True,
            "real_image_vision": False,
            "object_recognition": False,
            "semantic_vision": False,
            "action_selection_influence": False,
            "body_schema_persistence": False,
        },
        "human_summary": {
            "what_was_built": "A body-relative visual spatial grounding trace was created from a first-person symbolic viewport.",
            "what_it_tracks": "The trace records visible cell world positions, body-relative directions, forward distance, lateral offset, and Manhattan distance from the agent.",
            "what_it_means": "Qingyin can now represent where visible symbolic cells are relative to her current position and facing inside the sandbox fixture.",
            "what_is_blocked": "This does not add real image vision, object recognition, semantic vision, active focus, action selection influence, pathfinding, memory write, persistent body schema, or proof claims.",
            "plain_result": "The visual line now has a minimal position/direction/distance grounding trace.",
        },
        "blocked_flags": {field: False for field in REQUIRED_BLOCKED_FLAGS},
    }


def validate_visual_spatial_grounding_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "visual_spatial_grounding",
        "record_version": "v0",
        "spatial_grounding_status": "completed_body_relative_visual_spatial_trace",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    observation = _dict(record.get("source_visual_observation"), errors, "source_visual_observation_missing")
    if observation.get("observation_type") != "symbolic_first_person_viewport":
        errors.append("source_visual_observation_type_not_expected")
    if observation.get("viewport_size") != [3, 3]:
        errors.append("source_visual_observation_viewport_size_not_expected")
    if observation.get("first_person_viewport") is not True:
        errors.append("source_visual_observation_not_first_person")
    if observation.get("full_map_visible_to_agent") is not False:
        errors.append("source_visual_observation_full_map_visible")
    if observation.get("real_image_vision") is not False:
        errors.append("source_visual_observation_real_image_vision")
    if not _is_position(observation.get("agent_position")):
        errors.append("source_visual_observation_agent_position_invalid")
    if observation.get("facing") not in {"north", "east", "south", "west"}:
        errors.append("source_visual_observation_facing_invalid")

    frame = _dict(record.get("body_relative_frame"), errors, "body_relative_frame_missing")
    expected_frame = {
        "agent_viewport_position": FIRST_PERSON_AGENT_VIEWPORT_POSITION,
        "front_symbol_position": FIRST_PERSON_FRONT_SYMBOL_POSITION,
        "far_front_symbol_position": FIRST_PERSON_FAR_FRONT_SYMBOL_POSITION,
        "body_relative_coordinates_created": True,
        "distance_estimates_created": True,
        "direction_labels_created": True,
        "position_direction_distance_trace": True,
    }
    for field, value in expected_frame.items():
        if frame.get(field) != value:
            errors.append(f"body_relative_frame_{field}_not_expected")
    if frame.get("agent_position") != observation.get("agent_position"):
        errors.append("body_relative_frame_agent_position_mismatch")
    if frame.get("facing") != observation.get("facing"):
        errors.append("body_relative_frame_facing_mismatch")

    cells = record.get("spatial_cells")
    if not isinstance(cells, list):
        errors.append("spatial_cells_missing_or_not_list")
        cells = []
    if len(cells) != EXPECTED_SPATIAL_CELL_COUNT:
        errors.append("spatial_cells_count_not_expected")
    cell_results = [_validate_spatial_cell(cell, observation) for cell in cells if isinstance(cell, dict)]
    for result in cell_results:
        errors.extend(result["error_codes"])

    front = _dict(record.get("front_cell_spatial_summary"), errors, "front_cell_spatial_summary_missing")
    if front.get("front_symbol") != observation.get("front_symbol"):
        errors.append("front_cell_symbol_mismatch")
    if front.get("body_direction") != "front":
        errors.append("front_cell_body_direction_not_front")
    if front.get("distance_forward") != 1:
        errors.append("front_cell_distance_forward_not_one")
    if front.get("manhattan_distance_from_agent") != 1:
        errors.append("front_cell_manhattan_distance_not_one")
    if front.get("immediate_front") is not True:
        errors.append("front_cell_immediate_front_not_true")

    far_front = _dict(record.get("far_front_cell_spatial_summary"), errors, "far_front_cell_summary_missing")
    if far_front.get("body_direction") != "front":
        errors.append("far_front_cell_body_direction_not_front")
    if far_front.get("distance_forward") != 2:
        errors.append("far_front_cell_distance_forward_not_two")
    if far_front.get("manhattan_distance_from_agent") != 2:
        errors.append("far_front_cell_manhattan_distance_not_two")

    agent = _dict(record.get("agent_cell_spatial_summary"), errors, "agent_cell_summary_missing")
    if agent.get("agent_symbol") != "a":
        errors.append("agent_cell_symbol_not_agent")
    if agent.get("body_direction") != "self":
        errors.append("agent_cell_body_direction_not_self")
    if agent.get("distance_forward") != 0:
        errors.append("agent_cell_distance_forward_not_zero")
    if agent.get("manhattan_distance_from_agent") != 0:
        errors.append("agent_cell_manhattan_distance_not_zero")

    scope = _dict(record.get("grounding_scope"), errors, "grounding_scope_missing")
    expected_scope = {
        "symbolic_first_person_viewport_only": True,
        "visible_cells_only": True,
        "full_map_visible_to_agent": False,
        "world_positions_from_sandbox_fixture": True,
        "real_image_vision": False,
        "object_recognition": False,
        "semantic_vision": False,
        "action_selection_influence": False,
        "body_schema_persistence": False,
    }
    for field, value in expected_scope.items():
        if scope.get(field) != value:
            errors.append(f"grounding_scope_{field}_not_expected")

    human = _dict(record.get("human_summary"), errors, "human_summary_missing")
    for field in ("what_was_built", "what_it_tracks", "what_it_means", "what_is_blocked", "plain_result"):
        if not isinstance(human.get(field), str) or not human.get(field).strip():
            errors.append(f"human_summary_{field}_empty")

    blocked = _dict(record.get("blocked_flags"), errors, "blocked_flags_missing")
    for field in REQUIRED_BLOCKED_FLAGS:
        if blocked.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")

    valid_cells = [result for result in cell_results if result["valid"]]
    return {
        "valid": not errors,
        "error_codes": errors,
        "spatial_cell_count": len(cells),
        "valid_spatial_cell_count": len(valid_cells),
        "body_relative_coordinates_created": frame.get("body_relative_coordinates_created") is True,
        "distance_estimates_created": frame.get("distance_estimates_created") is True,
        "direction_labels_created": frame.get("direction_labels_created") is True,
        "front_cell_grounded": front.get("body_direction") == "front" and front.get("distance_forward") == 1,
        "far_front_cell_grounded": far_front.get("body_direction") == "front" and far_front.get("distance_forward") == 2,
        "agent_cell_grounded": agent.get("body_direction") == "self",
        "visible_cells_only": scope.get("visible_cells_only") is True,
        "full_map_blocked": scope.get("full_map_visible_to_agent") is False
        and blocked.get("full_map_visible_to_agent") is False,
        "real_image_vision_blocked": scope.get("real_image_vision") is False and blocked.get("real_image_vision") is False,
        "object_recognition_blocked": scope.get("object_recognition") is False
        and blocked.get("object_recognition") is False,
        "semantic_vision_blocked": scope.get("semantic_vision") is False and blocked.get("semantic_vision") is False,
        "action_selection_blocked": scope.get("action_selection_influence") is False
        and blocked.get("action_selection_influence") is False,
        "pathfinding_blocked": blocked.get("pathfinding_used") is False,
        "memory_write_blocked": blocked.get("memory_write_performed") is False,
        "body_schema_persistence_blocked": scope.get("body_schema_persistence") is False
        and blocked.get("persistent_body_schema_written") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claimed") is False,
    }


def run_visual_spatial_grounding_minimal_check() -> dict[str, Any]:
    valid_record = build_visual_spatial_grounding_record()
    records = [valid_record, *_invalid_records(valid_record)]
    validation_results = [validate_visual_spatial_grounding_record(record) for record in records]
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
            "boundary_reason": "Adds body-relative position/direction/distance visual spatial trace validation.",
        },
        "valid_record": valid_record,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A minimal body-relative visual spatial grounding checker was added.",
            "what_changed": "Symbolic first-person visible cells now produce position, direction, and distance traces.",
            "what_is_blocked": "Real image vision, object recognition, semantic vision, active focus, action selection influence, pathfinding, memory writes, persistent body schema, and proof claims remain blocked.",
            "plain_result": "The visual line now has a verified spatial perception trace, but it still cannot drive behavior.",
        },
        "valid_result_count": len(valid_results),
    }


def _demo_source_observation() -> dict[str, Any]:
    level = create_simulated_vision_larger_sandbox()
    state = build_initial_larger_sandbox_state(level)
    viewport = render_larger_sandbox_viewport(state, level)
    cell_positions = viewport_cells_for_facing(tuple(state["pos"]), state["facing"], size=3)
    return {
        "observation_id": "visual_spatial_grounding_demo_observation_001",
        "observation_type": "symbolic_first_person_viewport",
        "level_id": level["level_id"],
        "agent_position": list(state["pos"]),
        "facing": state["facing"],
        "viewport_size": [3, 3],
        "viewport": viewport,
        "viewport_world_positions": [[list(pos) for pos in row] for row in cell_positions],
        "front_symbol": front_symbol_from_larger_viewport(viewport),
        "first_person_viewport": True,
        "full_map_visible_to_agent": False,
        "real_image_vision": False,
        "llm_vision_used": False,
    }


def _build_spatial_cells(observation: dict[str, Any]) -> list[dict[str, Any]]:
    viewport = observation["viewport"]
    positions = observation["viewport_world_positions"]
    cells: list[dict[str, Any]] = []
    for row_index, row in enumerate(viewport):
        for col_index, symbol in enumerate(row):
            forward_distance = len(viewport) - 1 - row_index
            lateral_offset = col_index - (len(row) // 2)
            cells.append(
                {
                    "cell_id": f"visual_spatial_cell:{row_index}:{col_index}",
                    "viewport_position": [row_index, col_index],
                    "world_position": positions[row_index][col_index],
                    "symbol": symbol,
                    "body_relative_vector": {
                        "forward_distance": forward_distance,
                        "lateral_offset": lateral_offset,
                    },
                    "body_direction": _body_direction(forward_distance, lateral_offset),
                    "distance_forward": forward_distance,
                    "lateral_offset": lateral_offset,
                    "manhattan_distance_from_agent": abs(forward_distance) + abs(lateral_offset),
                    "visible_in_current_viewport": True,
                    "semantic_label": None,
                }
            )
    return cells


def _validate_spatial_cell(cell: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    viewport_position = cell.get("viewport_position")
    if not (
        isinstance(viewport_position, list)
        and len(viewport_position) == 2
        and all(isinstance(value, int) for value in viewport_position)
    ):
        errors.append("spatial_cell_viewport_position_invalid")
        return {"valid": False, "error_codes": errors}

    row, col = viewport_position
    viewport = observation.get("viewport", [])
    positions = observation.get("viewport_world_positions", [])
    if row < 0 or row >= len(viewport) or col < 0 or col >= len(viewport[row]):
        errors.append("spatial_cell_viewport_position_out_of_bounds")
        return {"valid": False, "error_codes": errors}

    expected_symbol = viewport[row][col]
    expected_world_position = positions[row][col]
    expected_forward = len(viewport) - 1 - row
    expected_lateral = col - (len(viewport[row]) // 2)
    if cell.get("symbol") != expected_symbol:
        errors.append("spatial_cell_symbol_mismatch")
    if cell.get("world_position") != expected_world_position:
        errors.append("spatial_cell_world_position_mismatch")
    if cell.get("distance_forward") != expected_forward:
        errors.append("spatial_cell_distance_forward_mismatch")
    if cell.get("lateral_offset") != expected_lateral:
        errors.append("spatial_cell_lateral_offset_mismatch")
    if cell.get("body_direction") != _body_direction(expected_forward, expected_lateral):
        errors.append("spatial_cell_body_direction_mismatch")
    if cell.get("manhattan_distance_from_agent") != abs(expected_forward) + abs(expected_lateral):
        errors.append("spatial_cell_manhattan_distance_mismatch")
    if cell.get("visible_in_current_viewport") is not True:
        errors.append("spatial_cell_not_visible")
    if cell.get("semantic_label") is not None:
        errors.append("spatial_cell_semantic_label_not_null")
    vector = cell.get("body_relative_vector")
    if not isinstance(vector, dict):
        errors.append("spatial_cell_body_relative_vector_missing")
    else:
        if vector.get("forward_distance") != expected_forward:
            errors.append("spatial_cell_vector_forward_distance_mismatch")
        if vector.get("lateral_offset") != expected_lateral:
            errors.append("spatial_cell_vector_lateral_offset_mismatch")

    return {"valid": not errors, "error_codes": errors}


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def add(name: str, mutator) -> None:
        record = deepcopy(valid_record)
        record["record_type"] = record["record_type"]
        mutator(record)
        record["invalid_case"] = name
        cases.append(record)

    add("wrong_record_type", lambda r: r.__setitem__("record_type", "visual_scene_understanding"))
    add("wrong_observation_type", lambda r: r["source_visual_observation"].__setitem__("observation_type", "semantic_scene"))
    add("not_first_person", lambda r: r["source_visual_observation"].__setitem__("first_person_viewport", False))
    add("full_map_visible", lambda r: r["source_visual_observation"].__setitem__("full_map_visible_to_agent", True))
    add("real_image_vision", lambda r: r["source_visual_observation"].__setitem__("real_image_vision", True))
    add("wrong_agent_position", lambda r: r["source_visual_observation"].__setitem__("agent_position", [99, 99]))
    add("wrong_facing", lambda r: r["source_visual_observation"].__setitem__("facing", "up"))
    add("body_frame_position_mismatch", lambda r: r["body_relative_frame"].__setitem__("agent_position", [0, 0]))
    add("body_frame_facing_mismatch", lambda r: r["body_relative_frame"].__setitem__("facing", "east"))
    add("coordinates_not_created", lambda r: r["body_relative_frame"].__setitem__("body_relative_coordinates_created", False))
    add("distance_not_created", lambda r: r["body_relative_frame"].__setitem__("distance_estimates_created", False))
    add("direction_not_created", lambda r: r["body_relative_frame"].__setitem__("direction_labels_created", False))
    add("missing_spatial_cell", lambda r: r.__setitem__("spatial_cells", r["spatial_cells"][:-1]))
    add("wrong_cell_symbol", lambda r: r["spatial_cells"][0].__setitem__("symbol", "z"))
    add("wrong_cell_world_position", lambda r: r["spatial_cells"][0].__setitem__("world_position", [99, 99]))
    add("wrong_cell_distance", lambda r: r["spatial_cells"][0].__setitem__("distance_forward", 99))
    add("wrong_cell_direction", lambda r: r["spatial_cells"][0].__setitem__("body_direction", "behind"))
    add("cell_semantic_label", lambda r: r["spatial_cells"][0].__setitem__("semantic_label", "wall"))
    add("front_not_front", lambda r: r["front_cell_spatial_summary"].__setitem__("body_direction", "left"))
    add("front_wrong_distance", lambda r: r["front_cell_spatial_summary"].__setitem__("distance_forward", 2))
    add("far_front_wrong_distance", lambda r: r["far_front_cell_spatial_summary"].__setitem__("distance_forward", 1))
    add("agent_not_self", lambda r: r["agent_cell_spatial_summary"].__setitem__("body_direction", "front"))
    add("scope_not_symbolic", lambda r: r["grounding_scope"].__setitem__("symbolic_first_person_viewport_only", False))
    add("scope_not_visible_only", lambda r: r["grounding_scope"].__setitem__("visible_cells_only", False))
    add("scope_full_map", lambda r: r["grounding_scope"].__setitem__("full_map_visible_to_agent", True))
    add("scope_object_recognition", lambda r: r["grounding_scope"].__setitem__("object_recognition", True))
    add("scope_semantic_vision", lambda r: r["grounding_scope"].__setitem__("semantic_vision", True))
    add("scope_action_influence", lambda r: r["grounding_scope"].__setitem__("action_selection_influence", True))
    add("scope_body_schema_persistence", lambda r: r["grounding_scope"].__setitem__("body_schema_persistence", True))
    add("selected_action_created", lambda r: r["blocked_flags"].__setitem__("selected_action_created", True))
    add("pathfinding_used", lambda r: r["blocked_flags"].__setitem__("pathfinding_used", True))
    add("memory_write", lambda r: r["blocked_flags"].__setitem__("memory_write_performed", True))
    add("predictor_mutation", lambda r: r["blocked_flags"].__setitem__("predictor_mutation_performed", True))
    add("subjective_visual_claim", lambda r: r["blocked_flags"].__setitem__("subjective_visual_experience_claimed", True))
    add("proof_claim", lambda r: r["blocked_flags"].__setitem__("proof_of_learning_claimed", True))
    add("empty_human_summary", lambda r: r["human_summary"].__setitem__("plain_result", ""))
    return cases


def _summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    valid_results = [result for result in results if result["valid"]]
    return {
        "visual_spatial_grounding_result_count": len(results),
        "valid_visual_spatial_grounding_count": len(valid_results),
        "invalid_visual_spatial_grounding_count": len(results) - len(valid_results),
        "body_relative_coordinates_created_count": _count_valid(valid_results, "body_relative_coordinates_created"),
        "distance_estimates_created_count": _count_valid(valid_results, "distance_estimates_created"),
        "direction_labels_created_count": _count_valid(valid_results, "direction_labels_created"),
        "front_cell_grounded_count": _count_valid(valid_results, "front_cell_grounded"),
        "far_front_cell_grounded_count": _count_valid(valid_results, "far_front_cell_grounded"),
        "agent_cell_grounded_count": _count_valid(valid_results, "agent_cell_grounded"),
        "visible_cells_only_count": _count_valid(valid_results, "visible_cells_only"),
        "full_map_blocked_count": _count_valid(valid_results, "full_map_blocked"),
        "real_image_vision_blocked_count": _count_valid(valid_results, "real_image_vision_blocked"),
        "object_recognition_blocked_count": _count_valid(valid_results, "object_recognition_blocked"),
        "semantic_vision_blocked_count": _count_valid(valid_results, "semantic_vision_blocked"),
        "action_selection_blocked_count": _count_valid(valid_results, "action_selection_blocked"),
        "pathfinding_blocked_count": _count_valid(valid_results, "pathfinding_blocked"),
        "memory_write_blocked_count": _count_valid(valid_results, "memory_write_blocked"),
        "body_schema_persistence_blocked_count": _count_valid(valid_results, "body_schema_persistence_blocked"),
        "proof_claim_blocked_count": _count_valid(valid_results, "proof_claim_blocked"),
    }


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["visual_spatial_grounding_result_count"] == 37
        and summary["valid_visual_spatial_grounding_count"] == 1
        and summary["invalid_visual_spatial_grounding_count"] == 36
        and summary["body_relative_coordinates_created_count"] == 1
        and summary["distance_estimates_created_count"] == 1
        and summary["direction_labels_created_count"] == 1
        and summary["front_cell_grounded_count"] == 1
        and summary["far_front_cell_grounded_count"] == 1
        and summary["agent_cell_grounded_count"] == 1
        and summary["visible_cells_only_count"] == 1
        and summary["full_map_blocked_count"] == 1
        and summary["real_image_vision_blocked_count"] == 1
        and summary["object_recognition_blocked_count"] == 1
        and summary["semantic_vision_blocked_count"] == 1
        and summary["action_selection_blocked_count"] == 1
        and summary["pathfinding_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["body_schema_persistence_blocked_count"] == 1
        and summary["proof_claim_blocked_count"] == 1
    )


def _cell_at_viewport_position(cells: list[dict[str, Any]], viewport_position: list[int]) -> dict[str, Any]:
    for cell in cells:
        if cell["viewport_position"] == viewport_position:
            return cell
    raise ValueError(f"viewport position not found: {viewport_position}")


def _body_direction(forward_distance: int, lateral_offset: int) -> str:
    if forward_distance == 0 and lateral_offset == 0:
        return "self"
    if forward_distance > 0 and lateral_offset == 0:
        return "front"
    if forward_distance > 0 and lateral_offset < 0:
        return "front_left"
    if forward_distance > 0 and lateral_offset > 0:
        return "front_right"
    if lateral_offset < 0:
        return "left"
    if lateral_offset > 0:
        return "right"
    return "self"


def _dict(value: Any, errors: list[str], error_code: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(error_code)
        return {}
    return value


def _is_position(value: Any) -> bool:
    return isinstance(value, list) and len(value) == 2 and all(isinstance(item, int) for item in value)


def _count_valid(results: list[dict[str, Any]], field: str) -> int:
    return sum(1 for result in results if result.get(field) is True)
