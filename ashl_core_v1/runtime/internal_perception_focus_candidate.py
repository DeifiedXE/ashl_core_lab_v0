"""Changed-grid candidate generation and deterministic selection."""

from __future__ import annotations

import math
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.internal_perception_focus_types import (
    DEFAULT_DIFFERENCE_STRENGTH_FLOOR,
    FOCUS_SELECTION_RULE,
    MAXIMUM_FOCUS_CANDIDATES,
    InternalPerceptionFocusCandidate,
    InternalPerceptionFocusCandidateBatch,
    InternalPerceptionFocusSelection,
)
from ashl_core_v1.runtime.perception_reacquisition_types import (
    CompletedObservationWindowReference,
)


def create_focus_candidates(
    *,
    parent: CompletedObservationWindowReference,
    visual_change: dict[str, Any],
    current_visual_frame: dict[str, Any],
    difference_strength_floor: float = DEFAULT_DIFFERENCE_STRENGTH_FLOOR,
) -> tuple[
    InternalPerceptionFocusCandidateBatch,
    tuple[InternalPerceptionFocusCandidate, ...],
]:
    if not parent.completed_clean:
        raise ValueError("parent_window_not_completed_clean")
    if "screen" not in parent.participating_lanes:
        raise ValueError("parent_screen_lane_absent")
    if not math.isfinite(float(difference_strength_floor)):
        raise ValueError("difference_strength_floor_nonfinite")
    if visual_change.get("source_kind") != "screen":
        raise ValueError("visual_change_source_must_be_screen")
    change_id = str(visual_change.get("visual_change_id") or "")
    frame_id = str(current_visual_frame.get("visual_primitive_id") or "")
    if not change_id or not frame_id:
        raise ValueError("visual_source_lineage_incomplete")
    if visual_change.get("current_visual_primitive_id") != frame_id:
        raise ValueError("visual_change_frame_lineage_mismatch")
    grid_width = int(current_visual_frame.get("grid_width", 0))
    grid_height = int(current_visual_frame.get("grid_height", 0))
    if grid_width <= 0 or grid_height <= 0:
        raise ValueError("visual_grid_geometry_missing")

    changed_cells = tuple(visual_change.get("changed_grid_cells") or ())
    eligible: list[dict[str, Any]] = []
    for raw_cell in changed_cells:
        cell = dict(raw_cell)
        strength = float(cell.get("difference_strength", float("nan")))
        if not math.isfinite(strength):
            raise ValueError("changed_grid_difference_nonfinite")
        grid_x = int(cell.get("grid_x", -1))
        grid_y = int(cell.get("grid_y", -1))
        if not 0 <= grid_x < grid_width or not 0 <= grid_y < grid_height:
            raise ValueError("changed_grid_coordinate_invalid")
        if strength > difference_strength_floor:
            eligible.append(
                {
                    "grid_x": grid_x,
                    "grid_y": grid_y,
                    "difference_strength": strength,
                }
            )

    eligible.sort(
        key=lambda cell: (
            -float(cell["difference_strength"]),
            int(cell["grid_y"]),
            int(cell["grid_x"]),
        )
    )
    retained = eligible[:MAXIMUM_FOCUS_CANDIDATES]
    candidates = tuple(
        InternalPerceptionFocusCandidate(
            focus_candidate_id=stable_id("internal_focus_candidate"),
            schema_version="ashl_package_127_internal_focus_candidate_v0",
            created_at=utc_now(),
            parent_runtime_session_id=parent.runtime_session_id,
            parent_perception_session_id=parent.perception_session_id,
            parent_observation_window_id=parent.observation_window_id,
            source_visual_change_primitive_id=change_id,
            source_visual_frame_primitive_id=frame_id,
            source_grid_width=grid_width,
            source_grid_height=grid_height,
            grid_x=int(cell["grid_x"]),
            grid_y=int(cell["grid_y"]),
            difference_strength=float(cell["difference_strength"]),
            reason_codes=("changed_grid_cell_present",),
            semantic_label=None,
            object_identity=None,
            object_class=None,
            memory_used=False,
            endocrine_signal_used=False,
            thought_engine_used=False,
            uncertainty_signal_used=False,
            novelty_signal_used=False,
            candidate_status="eligible",
            source_record_refs=(
                parent.completed_window_reference_id,
                change_id,
                frame_id,
            ),
            source_trace_refs=tuple(
                visual_change.get("source_trace_refs") or ()
            ),
        )
        for cell in retained
    )
    batch = InternalPerceptionFocusCandidateBatch(
        focus_candidate_batch_id=stable_id("internal_focus_candidate_batch"),
        schema_version="ashl_package_127_internal_focus_candidate_batch_v0",
        created_at=utc_now(),
        parent_observation_window_id=parent.observation_window_id,
        source_visual_change_primitive_id=change_id,
        difference_strength_floor=float(difference_strength_floor),
        changed_grid_cell_count=len(changed_cells),
        eligible_cell_count=len(eligible),
        candidate_ids=tuple(
            candidate.focus_candidate_id for candidate in candidates
        ),
        omitted_candidate_count=max(
            0,
            len(eligible) - MAXIMUM_FOCUS_CANDIDATES,
        ),
        maximum_candidate_count=MAXIMUM_FOCUS_CANDIDATES,
        candidate_count=len(candidates),
        stable_frame=not changed_cells,
        source_record_refs=(
            parent.completed_window_reference_id,
            change_id,
            frame_id,
        ),
        source_trace_refs=tuple(
            visual_change.get("source_trace_refs") or ()
        ),
    )
    return batch, candidates


def select_focus_candidate(
    *,
    parent_observation_window_id: str,
    candidates: tuple[InternalPerceptionFocusCandidate, ...],
) -> InternalPerceptionFocusSelection:
    candidate_ids = tuple(
        candidate.focus_candidate_id for candidate in candidates
    )
    if any(
        candidate.parent_observation_window_id
        != parent_observation_window_id
        for candidate in candidates
    ):
        return InternalPerceptionFocusSelection(
            focus_selection_id=stable_id("internal_focus_selection"),
            schema_version="ashl_package_127_internal_focus_selection_v0",
            created_at=utc_now(),
            parent_observation_window_id=parent_observation_window_id,
            candidate_ids=candidate_ids,
            selected_candidate_id=None,
            selection_rule=FOCUS_SELECTION_RULE,
            selected_grid_x=None,
            selected_grid_y=None,
            selected_difference_strength=None,
            candidate_set_preserved=True,
            deterministic_tie_break_used=False,
            selection_status="blocked",
            failure_reasons=("candidate_parent_window_mismatch",),
            source_record_refs=candidate_ids,
            source_trace_refs=tuple(),
        )
    if not candidates:
        return InternalPerceptionFocusSelection(
            focus_selection_id=stable_id("internal_focus_selection"),
            schema_version="ashl_package_127_internal_focus_selection_v0",
            created_at=utc_now(),
            parent_observation_window_id=parent_observation_window_id,
            candidate_ids=tuple(),
            selected_candidate_id=None,
            selection_rule=FOCUS_SELECTION_RULE,
            selected_grid_x=None,
            selected_grid_y=None,
            selected_difference_strength=None,
            candidate_set_preserved=True,
            deterministic_tie_break_used=False,
            selection_status="no_candidate",
            failure_reasons=tuple(),
            source_record_refs=tuple(),
            source_trace_refs=tuple(),
        )
    ordered = sorted(
        candidates,
        key=lambda candidate: (
            -candidate.difference_strength,
            candidate.grid_y,
            candidate.grid_x,
        ),
    )
    selected = ordered[0]
    tie_used = (
        len(ordered) > 1
        and ordered[1].difference_strength
        == selected.difference_strength
    )
    return InternalPerceptionFocusSelection(
        focus_selection_id=stable_id("internal_focus_selection"),
        schema_version="ashl_package_127_internal_focus_selection_v0",
        created_at=utc_now(),
        parent_observation_window_id=parent_observation_window_id,
        candidate_ids=candidate_ids,
        selected_candidate_id=selected.focus_candidate_id,
        selection_rule=FOCUS_SELECTION_RULE,
        selected_grid_x=selected.grid_x,
        selected_grid_y=selected.grid_y,
        selected_difference_strength=selected.difference_strength,
        candidate_set_preserved=True,
        deterministic_tie_break_used=tie_used,
        selection_status="selected",
        failure_reasons=tuple(),
        source_record_refs=candidate_ids,
        source_trace_refs=tuple(),
    )
