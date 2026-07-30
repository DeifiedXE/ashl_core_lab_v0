"""Canonical internal-only action binding for Package 127."""

from __future__ import annotations

from ashl_core_v1.host_body.host_body_internal_action_choice import (
    ALLOWED_INTERNAL_ACTION_KINDS,
)
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.internal_perception_focus_types import (
    FOCUS_ACTION_KIND,
    InternalPerceptionFocusPlan,
    InternalPerceptionFocusShiftAction,
)


def create_internal_perception_focus_shift_action(
    *,
    plan: InternalPerceptionFocusPlan,
) -> InternalPerceptionFocusShiftAction:
    if FOCUS_ACTION_KIND not in ALLOWED_INTERNAL_ACTION_KINDS:
        raise ValueError("canonical Host Body focus action is not registered")
    return InternalPerceptionFocusShiftAction(
        internal_action_id=stable_id("internal_perception_focus_shift_action"),
        schema_version="ashl_package_127_internal_focus_shift_action_v0",
        created_at=utc_now(),
        action_kind=FOCUS_ACTION_KIND,
        focus_plan_id=plan.focus_plan_id,
        parent_observation_window_id=plan.parent_observation_window_id,
        internal_only=True,
        external_side_effect=False,
        sensor_target_changed=False,
        sensor_configuration_changed=False,
        screen_region_changed=False,
        selected_action_created=False,
        final_action_created=False,
        direct_command_created=False,
        action_source="bounded_low_level_visual_change_policy",
        source_record_refs=(plan.focus_plan_id,),
        source_trace_refs=plan.source_trace_refs,
    )
