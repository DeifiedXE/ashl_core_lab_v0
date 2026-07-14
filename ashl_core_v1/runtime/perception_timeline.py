"""Monotonic perception timeline assembly for Package 122."""

from __future__ import annotations

from ashl_core_v1.runtime.host_sensor_types import monotonic_ns, stable_id, utc_now
from ashl_core_v1.runtime.multimodal_perception_session_types import (
    TIMELINE_SCHEMA_VERSION,
    MultimodalPerceptionSessionConfig,
    MultimodalPerceptionTimelineRecord,
    PerceptionLaneItem,
)


def build_multimodal_perception_timeline(
    *,
    session_id: str,
    config: MultimodalPerceptionSessionConfig,
    lane_items: tuple[PerceptionLaneItem, ...],
    alignment_window_ids: tuple[str, ...] = tuple(),
) -> MultimodalPerceptionTimelineRecord:
    sorted_items = tuple(sorted(lane_items, key=lambda item: (item.session_relative_ns, item.lane_item_id)))
    monotonic_order_valid = all(
        sorted_items[index].session_relative_ns <= sorted_items[index + 1].session_relative_ns
        for index in range(max(0, len(sorted_items) - 1))
    )
    max_relative_ns = max((item.session_relative_ns for item in sorted_items), default=0)
    bounded = len(alignment_window_ids) <= config.maximum_window_count and max_relative_ns <= config.maximum_session_duration_ms * 1_000_000
    return MultimodalPerceptionTimelineRecord(
        timeline_id=stable_id("multimodal_perception_timeline"),
        schema_version=TIMELINE_SCHEMA_VERSION,
        created_at=utc_now(),
        session_id=session_id,
        mode=config.mode,
        timeline_start_monotonic_ns=monotonic_ns(),
        timeline_end_monotonic_ns=monotonic_ns(),
        lane_item_ids=tuple(item.lane_item_id for item in sorted_items),
        alignment_window_ids=alignment_window_ids,
        total_lane_item_count=len(sorted_items),
        total_window_count=len(alignment_window_ids),
        monotonic_order_valid=monotonic_order_valid,
        bounded=bounded,
        source_trace_refs=tuple(dict.fromkeys(ref for item in sorted_items for ref in item.source_trace_refs)),
    )
