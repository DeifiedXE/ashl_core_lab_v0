"""Build canonical PerceptionReadableData from Package 121 primitives."""

from __future__ import annotations

from typing import Any

from ashl_core_v1.perception.audio_primitive_schema import AudioPrimitiveRecord
from ashl_core_v1.perception.host_state_primitive_schema import HostStatePrimitiveRecord
from ashl_core_v1.perception.types import PerceptionReadableData
from ashl_core_v1.perception.visual_primitive_schema import (
    VisualChangePrimitiveRecord,
    VisualFramePrimitiveRecord,
)
from ashl_core_v1.runtime.host_sensor_types import stable_id


ALLOWED_READABLE_TYPES = (
    "visual_frame_primitive",
    "visual_change_primitive",
    "audio_primitive",
    "host_state_primitive",
)

FORBIDDEN_PAYLOAD_KEYS = {
    "raw_pixels",
    "raw_pcm",
    "pcm_bytes",
    "pixel_bytes",
    "base64",
    "semantic_label",
    "teacher_interpretation",
    "memory_routing",
    "action_recommendation",
    "object_identity",
    "object_class",
    "speech_content",
    "speaker_identity",
    "emotion_label",
}


def build_perception_readable_data(
    primitive: object,
    *,
    compiler_config_sha256: str | None = None,
) -> PerceptionReadableData:
    if isinstance(primitive, VisualFramePrimitiveRecord):
        readable_type = "visual_frame_primitive"
        source_ref = primitive.source_artifact_id or primitive.source_buffer_id
        uncertainty = primitive.quality_uncertainty
        payload = {
            "primitive_record_id": primitive.visual_primitive_id,
            "compiler_id": primitive.compiler_id,
            "compiler_version": primitive.compiler_version,
            "compiler_config_sha256": primitive.compiler_config_sha256,
            "luminance_mean": primitive.luminance_mean,
            "luminance_stddev": primitive.luminance_stddev,
            "edge_density": primitive.edge_density,
            "grid_width": primitive.grid_width,
            "grid_height": primitive.grid_height,
            "clipped_dark_ratio": primitive.clipped_dark_ratio,
            "clipped_bright_ratio": primitive.clipped_bright_ratio,
            "bounded_low_level_summary": "visual luminance/color/contrast/edge/grid statistics only",
        }
        refs = primitive.source_trace_refs
        source_kind = primitive.source_kind
    elif isinstance(primitive, VisualChangePrimitiveRecord):
        readable_type = "visual_change_primitive"
        source_ref = primitive.current_source_artifact_id
        uncertainty = primitive.quality_uncertainty
        payload = {
            "primitive_record_id": primitive.visual_change_id,
            "compiler_id": primitive.compiler_id,
            "compiler_version": primitive.compiler_version,
            "compiler_config_sha256": primitive.compiler_config_sha256,
            "mean_absolute_difference": primitive.mean_absolute_difference,
            "changed_grid_cell_count": len(primitive.changed_grid_cells),
            "unchanged_grid_cell_count": primitive.unchanged_grid_cell_count,
            "changed_area_ratio": primitive.changed_area_ratio,
            "motion_proxy": primitive.motion_proxy,
            "stability_proxy": primitive.stability_proxy,
            "bounded_low_level_summary": "visual frame difference/grid change statistics only",
        }
        refs = primitive.source_trace_refs
        source_kind = primitive.source_kind
    elif isinstance(primitive, AudioPrimitiveRecord):
        readable_type = "audio_primitive"
        source_ref = primitive.source_artifact_id or primitive.source_buffer_id
        uncertainty = primitive.uncertainty
        payload = {
            "primitive_record_id": primitive.audio_primitive_id,
            "compiler_id": primitive.compiler_id,
            "compiler_version": primitive.compiler_version,
            "compiler_config_sha256": compiler_config_sha256,
            "privacy_policy_id": primitive.privacy_policy_id,
            "duration_ms": primitive.duration_ms,
            "amplitude_envelope_point_count": len(primitive.amplitude_envelope),
            "relative_band_names": tuple(name for name, _value in primitive.relative_band_energy),
            "onset_count": len(primitive.onset_events),
            "offset_count": len(primitive.offset_events),
            "pause_count": len(primitive.pause_intervals),
            "coarse_pitch_band": primitive.coarse_pitch_band,
            "bounded_low_level_summary": "audio amplitude/band/onset/pause/rhythm/relative-pitch structure only",
        }
        refs = primitive.source_trace_refs
        source_kind = primitive.source_kind
    elif isinstance(primitive, HostStatePrimitiveRecord):
        readable_type = "host_state_primitive"
        source_ref = primitive.source_artifact_id
        uncertainty = primitive.quality_uncertainty
        payload = {
            "primitive_record_id": primitive.host_state_primitive_id,
            "compiler_id": primitive.compiler_id,
            "compiler_version": primitive.compiler_version,
            "compiler_config_sha256": primitive.compiler_config_sha256,
            "cpu_utilization_ratio": primitive.cpu_utilization_ratio,
            "memory_available_ratio": primitive.memory_available_ratio,
            "battery_ratio": primitive.battery_ratio,
            "display_count": primitive.display_count,
            "missing_field_names": primitive.missing_field_names,
            "bounded_low_level_summary": "restricted host-state numeric/boolean normalization only",
        }
        refs = primitive.source_trace_refs
        source_kind = "host_state"
    else:
        raise TypeError("unsupported primitive type")
    _validate_readable_payload(payload)
    return PerceptionReadableData(
        perception_id=stable_id("perception_readable_data"),
        source_kind=source_kind,
        source_ref=source_ref,
        readable_type=readable_type,
        readable_payload=payload,
        uncertainty=float(uncertainty),
        source_trace_refs=refs,
        created_at_tick=None,
    )


def _validate_readable_payload(payload: dict[str, Any]) -> None:
    blocked = sorted(FORBIDDEN_PAYLOAD_KEYS.intersection(payload))
    if blocked:
        raise ValueError(f"PerceptionReadableData payload contains forbidden keys: {blocked}")
