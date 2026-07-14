"""Bounded queue backpressure records for Package 122."""

from __future__ import annotations

from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.multimodal_perception_session_types import (
    BACKPRESSURE_SCHEMA_VERSION,
    DROPPED_SAMPLE_SCHEMA_VERSION,
    PerceptionBackpressureRecord,
    PerceptionDroppedSampleRecord,
    PerceptionLaneItem,
)


def build_backpressure_record(
    *,
    session_id: str,
    source_kind: str,
    queue_depth_before: int,
    queue_depth_limit: int,
    policy: str,
    action_taken: str,
    affected_source_record_ids: tuple[str, ...],
    source_trace_refs: tuple[str, ...],
    uncertainty_increase: float = 0.1,
) -> PerceptionBackpressureRecord:
    return PerceptionBackpressureRecord(
        backpressure_record_id=stable_id("perception_backpressure"),
        schema_version=BACKPRESSURE_SCHEMA_VERSION,
        created_at=utc_now(),
        session_id=session_id,
        source_kind=source_kind,
        queue_depth_before=queue_depth_before,
        queue_depth_limit=queue_depth_limit,
        policy=policy,
        action_taken=action_taken,
        affected_source_record_ids=affected_source_record_ids,
        uncertainty_increase=uncertainty_increase,
        source_trace_refs=source_trace_refs,
    )


def build_dropped_sample_record(
    *,
    item: PerceptionLaneItem,
    reason_code: str,
    drop_policy: str,
    timeline_gap_created: bool,
    uncertainty_increase: float = 0.1,
) -> PerceptionDroppedSampleRecord:
    source_record_id = item.source_artifact_id or item.source_buffer_id or item.primitive_record_id
    return PerceptionDroppedSampleRecord(
        dropped_sample_record_id=stable_id("perception_dropped_sample"),
        schema_version=DROPPED_SAMPLE_SCHEMA_VERSION,
        created_at=utc_now(),
        session_id=item.session_id,
        source_kind=item.source_kind,
        source_record_id=source_record_id,
        reason_code=reason_code,
        drop_policy=drop_policy,
        raw_artifact_deleted=False,
        primitive_deleted=False,
        timeline_gap_created=timeline_gap_created,
        uncertainty_increase=uncertainty_increase,
        source_trace_refs=item.source_trace_refs,
    )
