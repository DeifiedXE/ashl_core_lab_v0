"""Read-only focused grid view and one-child-window sidecar."""

from __future__ import annotations

from typing import Any

from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.internal_perception_focus_types import (
    FocusedVisualRegionView,
    InternalPerceptionFocusContextSidecar,
    InternalPerceptionFocusPlan,
    InternalPerceptionFocusReleaseRecord,
)


def build_focused_visual_region_view(
    *,
    plan: InternalPerceptionFocusPlan,
    child_runtime_session_id: str,
    child_perception_session_id: str,
    child_observation_window_id: str,
    visual_frame: dict[str, Any],
    perception_readable_data_id: str,
    visual_change: dict[str, Any] | None = None,
) -> FocusedVisualRegionView:
    grid_width = int(visual_frame.get("grid_width", 0))
    grid_height = int(visual_frame.get("grid_height", 0))
    if (grid_width, grid_height) != (plan.grid_width, plan.grid_height):
        raise ValueError("child_visual_grid_geometry_changed")
    index = plan.grid_y * grid_width + plan.grid_x
    luminance = tuple(visual_frame.get("grid_luminance_means") or ())
    contrast = tuple(visual_frame.get("grid_contrast_values") or ())
    edges = tuple(visual_frame.get("grid_edge_density_values") or ())
    if index >= min(len(luminance), len(contrast), len(edges)):
        raise ValueError("focused_region_grid_values_missing")
    changed_cells = (
        tuple(visual_change.get("changed_grid_cells") or ())
        if visual_change
        else tuple()
    )
    source_cell_change_present = any(
        int(cell.get("grid_x", -1)) == plan.grid_x
        and int(cell.get("grid_y", -1)) == plan.grid_y
        for cell in changed_cells
    )
    frame_id = str(visual_frame.get("visual_primitive_id") or "")
    if not frame_id or not perception_readable_data_id:
        raise ValueError("focused_region_source_lineage_incomplete")
    refs = (
        plan.focus_plan_id,
        frame_id,
        perception_readable_data_id,
    ) + (
        (str(visual_change.get("visual_change_id")),)
        if visual_change
        else ()
    )
    return FocusedVisualRegionView(
        focused_region_view_id=stable_id("focused_visual_region_view"),
        schema_version="ashl_package_127_focused_visual_region_view_v0",
        created_at=utc_now(),
        focus_plan_id=plan.focus_plan_id,
        child_runtime_session_id=child_runtime_session_id,
        child_perception_session_id=child_perception_session_id,
        child_observation_window_id=child_observation_window_id,
        source_visual_frame_primitive_id=frame_id,
        source_perception_readable_data_id=perception_readable_data_id,
        grid_x=plan.grid_x,
        grid_y=plan.grid_y,
        luminance_mean=float(luminance[index]),
        contrast_value=float(contrast[index]),
        edge_density_value=float(edges[index]),
        source_cell_change_present=source_cell_change_present,
        raw_pixel_payload_present=False,
        image_crop_persisted=False,
        semantic_label=None,
        object_identity=None,
        read_only_context=True,
        action_selection_authority=False,
        memory_write_authority=False,
        scoring_authority=False,
        output_authority=False,
        source_record_refs=refs,
        source_trace_refs=tuple(
            visual_frame.get("source_trace_refs") or ()
        ),
    )


def build_focus_context_sidecar(
    *,
    plan: InternalPerceptionFocusPlan,
    view: FocusedVisualRegionView,
    full_frame_perception_readable_data_id: str,
    active_from_event_time_ns: int,
    active_until_event_time_ns: int,
    focus_state: str = "released",
) -> InternalPerceptionFocusContextSidecar:
    return InternalPerceptionFocusContextSidecar(
        focus_context_id=stable_id("internal_focus_context"),
        schema_version="ashl_package_127_internal_focus_context_sidecar_v0",
        created_at=utc_now(),
        child_perception_session_id=view.child_perception_session_id,
        child_observation_window_id=view.child_observation_window_id,
        focus_plan_id=plan.focus_plan_id,
        focused_region_view_id=view.focused_region_view_id,
        full_frame_perception_readable_data_id=(
            full_frame_perception_readable_data_id
        ),
        focus_state=focus_state,
        active_from_event_time_ns=active_from_event_time_ns,
        active_until_event_time_ns=active_until_event_time_ns,
        automatically_released=(focus_state == "released"),
        read_only_context=True,
        source_record_refs=(
            plan.focus_plan_id,
            view.focused_region_view_id,
            full_frame_perception_readable_data_id,
        ),
        source_trace_refs=view.source_trace_refs,
    )


def build_focus_release_record(
    *,
    sidecar: InternalPerceptionFocusContextSidecar,
    interrupted: bool = False,
) -> InternalPerceptionFocusReleaseRecord:
    return InternalPerceptionFocusReleaseRecord(
        focus_release_record_id=stable_id("internal_focus_release"),
        schema_version="ashl_package_127_internal_focus_release_v0",
        created_at=utc_now(),
        focus_context_id=sidecar.focus_context_id,
        child_observation_window_id=sidecar.child_observation_window_id,
        previous_focus_state="interrupted" if interrupted else "focused",
        new_focus_state="released",
        release_reason=(
            "operator_stop_after_child_started"
            if interrupted
            else "child_window_completed"
        ),
        child_window_count=1,
        history_preserved=True,
        source_record_refs=(
            sidecar.focus_context_id,
            sidecar.focused_region_view_id,
        ),
        source_trace_refs=sidecar.source_trace_refs,
    )
