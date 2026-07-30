"""Package 124A-compatible explicit gap between completed capture windows."""

from __future__ import annotations

from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.perception_reacquisition_types import (
    CrossWindowTemporalContinuityLink,
)


CROSS_WINDOW_LINK_SCHEMA_VERSION = "ashl_package_126_cross_window_temporal_continuity_link_v0"


def build_cross_window_temporal_link(
    *,
    parent_observation_window_id: str,
    child_observation_window_id: str,
    parent_final_anchor_ref: str,
    child_start_anchor_ref: str,
    parent_final_event_time_ns: int,
    child_start_event_time_ns: int,
    parent_clock_domain: str,
    child_clock_domain: str,
    parent_processing_clock_domain: str,
    child_processing_clock_domain: str,
    source_temporal_refs: tuple[str, ...] = tuple(),
    source_record_refs: tuple[str, ...] = tuple(),
    source_trace_refs: tuple[str, ...] = tuple(),
) -> CrossWindowTemporalContinuityLink:
    gap_ns = int(child_start_event_time_ns) - int(parent_final_event_time_ns)
    return CrossWindowTemporalContinuityLink(
        continuity_link_id=stable_id("cross_window_temporal_continuity_link"),
        schema_version=CROSS_WINDOW_LINK_SCHEMA_VERSION,
        created_at=utc_now(),
        parent_observation_window_id=parent_observation_window_id,
        child_observation_window_id=child_observation_window_id,
        parent_final_anchor_ref=parent_final_anchor_ref,
        child_start_anchor_ref=child_start_anchor_ref,
        parent_final_event_time_ns=int(parent_final_event_time_ns),
        child_start_event_time_ns=int(child_start_event_time_ns),
        external_gap_ns=gap_ns,
        same_event_clock_domain=parent_clock_domain == child_clock_domain,
        same_processing_clock_domain=(
            parent_processing_clock_domain == child_processing_clock_domain
        ),
        windows_temporally_contiguous=False,
        gap_explicit=True,
        source_temporal_refs=tuple(source_temporal_refs),
        source_record_refs=tuple(source_record_refs),
        source_trace_refs=tuple(source_trace_refs),
    )
