"""Deterministic visual change primitive compiler for Package 121."""

from __future__ import annotations

from ashl_core_v1.perception.perception_compiler_types import (
    PerceptionCompilerConfig,
    PerceptionCompilerDescriptor,
    build_compiler_config,
    build_compiler_descriptor,
)
from ashl_core_v1.perception.visual_primitive_schema import (
    VISUAL_CHANGE_PRIMITIVE_SCHEMA_VERSION,
    VisualChangePrimitiveRecord,
    VisualFramePrimitiveRecord,
)
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now


VISUAL_CHANGE_COMPILER_ID = "visual_change_compiler_v0"
VISUAL_CHANGE_COMPILER_VERSION = "visual_change_compiler_v0"


def build_visual_change_compiler_descriptor() -> PerceptionCompilerDescriptor:
    return build_compiler_descriptor(
        compiler_id=VISUAL_CHANGE_COMPILER_ID,
        compiler_version=VISUAL_CHANGE_COMPILER_VERSION,
        supported_source_kinds=("camera", "screen"),
        supported_media_formats=("BGR8", "BGRA8"),
        implementation_module="ashl_core_v1.perception.visual_change_primitive_compiler",
    )


def build_visual_change_compiler_config(*, source_kind: str = "camera", changed_cell_threshold: float = 0.08) -> PerceptionCompilerConfig:
    return build_compiler_config(
        compiler_id=VISUAL_CHANGE_COMPILER_ID,
        compiler_version=VISUAL_CHANGE_COMPILER_VERSION,
        source_kind="visual_change",
        parameter_payload={
            "source_kind": source_kind,
            "changed_cell_threshold": changed_cell_threshold,
            "object_tracking_created": False,
        },
    )


def compile_visual_change_primitive(
    previous: VisualFramePrimitiveRecord,
    current: VisualFramePrimitiveRecord,
    *,
    config: PerceptionCompilerConfig | None = None,
) -> VisualChangePrimitiveRecord:
    if previous.source_kind != current.source_kind:
        raise ValueError("visual_pair_mismatch")
    if previous.width != current.width or previous.height != current.height:
        raise ValueError("visual_pair_mismatch")
    if previous.pixel_format != current.pixel_format:
        raise ValueError("visual_pair_mismatch")
    if previous.compiler_version != current.compiler_version or previous.compiler_config_sha256 != current.compiler_config_sha256:
        raise ValueError("visual_pair_mismatch")
    compiler_config = config or build_visual_change_compiler_config(source_kind=current.source_kind)
    threshold = float(compiler_config.parameter_payload["changed_cell_threshold"])
    changed_cells: list[dict[str, object]] = []
    grid_count = current.grid_width * current.grid_height
    max_difference = 0.0
    total_difference = 0.0
    for index in range(grid_count):
        lum_delta = current.grid_luminance_means[index] - previous.grid_luminance_means[index]
        contrast_delta = current.grid_contrast_values[index] - previous.grid_contrast_values[index]
        edge_delta = current.grid_edge_density_values[index] - previous.grid_edge_density_values[index]
        strength = max(abs(lum_delta), abs(contrast_delta), abs(edge_delta))
        total_difference += strength
        max_difference = max(max_difference, strength)
        if strength >= threshold:
            changed_cells.append(
                {
                    "grid_x": index % current.grid_width,
                    "grid_y": index // current.grid_width,
                    "difference_strength": round(strength, 6),
                    "luminance_delta": round(lum_delta, 6),
                    "contrast_delta": round(contrast_delta, 6),
                    "edge_density_delta": round(edge_delta, 6),
                }
            )
    changed_ratio = len(changed_cells) / max(1, grid_count)
    motion_proxy = min(1.0, changed_ratio * max_difference * 2.0)
    return VisualChangePrimitiveRecord(
        visual_change_id=stable_id("visual_change_primitive"),
        schema_version=VISUAL_CHANGE_PRIMITIVE_SCHEMA_VERSION,
        created_at=utc_now(),
        source_kind=current.source_kind,
        previous_visual_primitive_id=previous.visual_primitive_id,
        current_visual_primitive_id=current.visual_primitive_id,
        previous_source_artifact_id=previous.source_artifact_id,
        current_source_artifact_id=current.source_artifact_id,
        width=current.width,
        height=current.height,
        pixel_format=current.pixel_format,
        mean_absolute_difference=round(total_difference / max(1, grid_count), 6),
        maximum_grid_difference=round(max_difference, 6),
        changed_grid_cells=tuple(changed_cells),
        unchanged_grid_cell_count=grid_count - len(changed_cells),
        changed_area_ratio=round(changed_ratio, 6),
        motion_proxy=round(motion_proxy, 6),
        stability_proxy=round(max(0.0, 1.0 - motion_proxy), 6),
        global_luminance_delta=round(current.luminance_mean - previous.luminance_mean, 6),
        global_contrast_delta=round(current.contrast_proxy - previous.contrast_proxy, 6),
        global_edge_density_delta=round(current.edge_density - previous.edge_density, 6),
        quality_uncertainty=max(previous.quality_uncertainty, current.quality_uncertainty),
        compiler_id=VISUAL_CHANGE_COMPILER_ID,
        compiler_version=VISUAL_CHANGE_COMPILER_VERSION,
        compiler_config_sha256=compiler_config.config_sha256,
        semantic_label=None,
        object_tracking_created=False,
        primitive_payload_sha256="",
        source_trace_refs=tuple(dict.fromkeys(previous.source_trace_refs + current.source_trace_refs)),
    )
