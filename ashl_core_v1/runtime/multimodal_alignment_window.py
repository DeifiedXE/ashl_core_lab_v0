"""Alignment window assembly for Package 122 multimodal perception sessions."""

from __future__ import annotations

from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.multimodal_perception_session_types import (
    ALIGNMENT_WINDOW_SCHEMA_VERSION,
    MultimodalAlignmentWindowRecord,
    MultimodalPerceptionSessionConfig,
    PerceptionLaneItem,
)


def assemble_alignment_windows(
    *,
    session_id: str,
    config: MultimodalPerceptionSessionConfig,
    lane_items: tuple[PerceptionLaneItem, ...],
) -> tuple[MultimodalAlignmentWindowRecord, ...]:
    if not lane_items:
        return tuple()
    width_ns = config.alignment_window_ms * 1_000_000
    max_ns = max(item.session_relative_ns for item in lane_items)
    window_count = min(config.maximum_window_count, int(max_ns // width_ns) + 1)
    windows: list[MultimodalAlignmentWindowRecord] = []
    for index in range(window_count):
        start = index * width_ns
        end = start + width_ns
        items = tuple(item for item in lane_items if start <= item.session_relative_ns < end)
        present = tuple(sorted(set(item.source_kind for item in items)))
        missing = tuple(kind for kind in config.required_source_kinds if kind not in present)
        camera_ids = tuple(item.lane_item_id for item in items if item.source_kind == "camera")
        screen_ids = tuple(item.lane_item_id for item in items if item.source_kind == "screen")
        microphone_ids = tuple(item.lane_item_id for item in items if item.source_kind == "microphone")
        host_state_ids = tuple(item.lane_item_id for item in items if item.source_kind == "host_state")
        aggregate_uncertainty = max((item.quality_uncertainty for item in items), default=0.0)
        visual_change = any(item.primitive_record_kind == "visual_change_primitive" for item in items)
        audio_activity = any(item.source_kind == "microphone" and item.primitive_record_kind == "audio_primitive" for item in items)
        host_delta = _host_state_delta_present(items)
        windows.append(
            MultimodalAlignmentWindowRecord(
                alignment_window_id=stable_id("multimodal_alignment_window"),
                schema_version=ALIGNMENT_WINDOW_SCHEMA_VERSION,
                created_at=utc_now(),
                session_id=session_id,
                window_index=index,
                window_start_relative_ns=start,
                window_end_relative_ns=end,
                camera_lane_item_ids=camera_ids,
                screen_lane_item_ids=screen_ids,
                microphone_lane_item_ids=microphone_ids,
                host_state_lane_item_ids=host_state_ids,
                present_source_kinds=present,
                missing_required_source_kinds=missing,
                visual_change_present=visual_change,
                audio_activity_present=audio_activity,
                host_state_delta_present=host_delta,
                aggregate_quality_uncertainty=min(1.0, aggregate_uncertainty + (0.1 if missing else 0.0)),
                complete_for_config=not missing,
                semantic_binding_created=False,
                source_trace_refs=tuple(dict.fromkeys(ref for item in items for ref in item.source_trace_refs)),
            )
        )
    return tuple(windows)


def _host_state_delta_present(items: tuple[PerceptionLaneItem, ...]) -> bool:
    host_items = tuple(item for item in items if item.source_kind == "host_state")
    return len(host_items) > 1
