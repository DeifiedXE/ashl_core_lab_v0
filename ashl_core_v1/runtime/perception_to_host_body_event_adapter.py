"""Adapter from Package 122 perception windows to the canonical HostBodyEvent."""

from __future__ import annotations

from typing import Any

from ashl_core_v1.host_body.host_body_port_map import HostBodyPortMapRecord, build_demo_qingyin_host_body_port_map
from ashl_core_v1.host_body.host_body_sensor_events import HostBodyEventRecord, build_host_body_event_record, validate_host_body_event_record
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.multimodal_perception_session_types import (
    HOST_BODY_BRIDGE_SCHEMA_VERSION,
    LOW_LEVEL_EVENT_KINDS,
    MultimodalAlignmentWindowRecord,
    PerceptionHostBodyEventBridgeRecord,
    PerceptionLaneItem,
)


def build_perception_host_body_event(
    *,
    session_id: str,
    timeline_id: str,
    window: MultimodalAlignmentWindowRecord,
    lane_items: tuple[PerceptionLaneItem, ...],
    emitted_event_kind: str,
) -> HostBodyEventRecord:
    if emitted_event_kind not in LOW_LEVEL_EVENT_KINDS:
        raise ValueError("invalid emitted perception event kind")
    port_payload = build_demo_qingyin_host_body_port_map()
    port_map = HostBodyPortMapRecord.from_dict(port_payload["host_body_port_map"])
    event_payload: dict[str, Any] = {
        "multimodal_session_id": session_id,
        "timeline_id": timeline_id,
        "alignment_window_id": window.alignment_window_id,
        "event_kind": emitted_event_kind,
        "perception_readable_data_ids": tuple(item.perception_readable_data_id for item in lane_items),
        "primitive_record_ids": tuple(item.primitive_record_id for item in lane_items),
        "present_source_kinds": window.present_source_kinds,
        "missing_required_source_kinds": window.missing_required_source_kinds,
        "visual_change_present": window.visual_change_present,
        "audio_activity_present": window.audio_activity_present,
        "host_state_delta_present": window.host_state_delta_present,
        "aggregate_quality_uncertainty": window.aggregate_quality_uncertainty,
        "source_trace_refs": window.source_trace_refs,
        "raw_media_embedded": False,
        "semantic_binding_created": False,
    }
    event = build_host_body_event_record(
        source_host_body_port_map_id=port_map.host_body_port_map_id,
        source_port_id=None,
        source_port_kind="bounded_multimodal_perception_session",
        event_type=f"{emitted_event_kind}:{window.alignment_window_id}",
        event_payload=event_payload,
        semantic_label=None,
        real_hardware_event=False,
        real_camera_accessed=False,
        real_mic_accessed=False,
        camera_capture_started=False,
        mic_stream_started=False,
        image_frame_stored=False,
        audio_stored=False,
        source_trace_refs=window.source_trace_refs,
    )
    validation = validate_host_body_event_record(event)
    if not validation["valid"]:
        raise ValueError(f"invalid perception HostBodyEvent: {validation}")
    return event


def build_perception_host_body_event_bridge_record(
    *,
    session_id: str,
    timeline_id: str,
    window: MultimodalAlignmentWindowRecord,
    emitted_event_kind: str,
    host_body_event: HostBodyEventRecord,
    lane_items: tuple[PerceptionLaneItem, ...],
    package_115_injection_succeeded: bool,
) -> PerceptionHostBodyEventBridgeRecord:
    return PerceptionHostBodyEventBridgeRecord(
        bridge_record_id=stable_id("perception_host_body_event_bridge"),
        schema_version=HOST_BODY_BRIDGE_SCHEMA_VERSION,
        created_at=utc_now(),
        session_id=session_id,
        multimodal_timeline_id=timeline_id,
        alignment_window_id=window.alignment_window_id,
        emitted_event_kind=emitted_event_kind,
        host_body_event_id=host_body_event.host_body_event_id,
        perception_readable_data_ids=tuple(item.perception_readable_data_id for item in lane_items),
        primitive_record_ids=tuple(item.primitive_record_id for item in lane_items),
        raw_media_embedded=False,
        semantic_binding_created=False,
        package_115_injection_succeeded=package_115_injection_succeeded,
        source_trace_refs=tuple(dict.fromkeys(window.source_trace_refs + host_body_event.source_trace_refs)),
    )
