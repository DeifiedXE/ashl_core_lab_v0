"""Visual primitive schemas for Package 121."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.perception.perception_compiler_types import payload_sha256_without, tuple_of_str
from ashl_core_v1.runtime.host_sensor_types import plain


VISUAL_FRAME_PRIMITIVE_SCHEMA_VERSION = "ashl_visual_frame_primitive_v0"
VISUAL_CHANGE_PRIMITIVE_SCHEMA_VERSION = "ashl_visual_change_primitive_v0"


def _tuple_of_float(value: Any) -> tuple[float, ...]:
    return tuple(float(item) for item in (value or ()))


def _ratio(name: str, value: float) -> float:
    item = float(value)
    if not 0.0 <= item <= 1.0:
        raise ValueError(f"{name} must be in [0, 1]")
    return item


@dataclass(frozen=True)
class VisualFramePrimitiveRecord:
    visual_primitive_id: str
    schema_version: str
    created_at: str
    primitive_role: str
    source_kind: str
    source_buffer_id: str | None
    source_artifact_id: str | None
    width: int
    height: int
    pixel_format: str
    luminance_mean: float
    luminance_stddev: float
    luminance_min: float
    luminance_max: float
    luminance_histogram: tuple[float, ...]
    relative_channel_distribution: tuple[tuple[str, float], ...]
    contrast_proxy: float
    edge_density: float
    grid_width: int
    grid_height: int
    grid_luminance_means: tuple[float, ...]
    grid_contrast_values: tuple[float, ...]
    grid_edge_density_values: tuple[float, ...]
    clipped_dark_ratio: float
    clipped_bright_ratio: float
    quality_uncertainty: float
    compiler_id: str
    compiler_version: str
    compiler_config_sha256: str
    semantic_label: None
    object_identity: None
    object_class: None
    scene_meaning: None
    primitive_payload_sha256: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != VISUAL_FRAME_PRIMITIVE_SCHEMA_VERSION:
            raise ValueError("invalid visual frame primitive schema_version")
        if self.primitive_role != "observed":
            raise ValueError("Package 121 visual primitives are observed only")
        if self.source_kind not in {"camera", "screen"}:
            raise ValueError("visual primitive source_kind must be camera or screen")
        if self.pixel_format not in {"BGR8", "BGRA8"}:
            raise ValueError("visual primitive pixel_format must be BGR8 or BGRA8")
        if self.width <= 0 or self.height <= 0 or self.grid_width <= 0 or self.grid_height <= 0:
            raise ValueError("visual dimensions must be positive")
        if len(self.grid_luminance_means) != self.grid_width * self.grid_height:
            raise ValueError("grid_luminance_means length mismatch")
        if len(self.grid_contrast_values) != self.grid_width * self.grid_height:
            raise ValueError("grid_contrast_values length mismatch")
        if len(self.grid_edge_density_values) != self.grid_width * self.grid_height:
            raise ValueError("grid_edge_density_values length mismatch")
        if any(value is not None for value in (self.semantic_label, self.object_identity, self.object_class, self.scene_meaning)):
            raise ValueError("visual semantic fields must remain null")
        object.__setattr__(self, "luminance_histogram", _tuple_of_float(self.luminance_histogram))
        object.__setattr__(self, "relative_channel_distribution", tuple((str(name), float(value)) for name, value in self.relative_channel_distribution))
        object.__setattr__(self, "grid_luminance_means", _tuple_of_float(self.grid_luminance_means))
        object.__setattr__(self, "grid_contrast_values", _tuple_of_float(self.grid_contrast_values))
        object.__setattr__(self, "grid_edge_density_values", _tuple_of_float(self.grid_edge_density_values))
        for name in ("clipped_dark_ratio", "clipped_bright_ratio", "quality_uncertainty", "edge_density"):
            object.__setattr__(self, name, _ratio(name, getattr(self, name)))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))
        expected = payload_sha256_without(
            self.to_dict(),
            "visual_primitive_id",
            "created_at",
            "source_buffer_id",
            "primitive_payload_sha256",
        )
        if self.primitive_payload_sha256 and self.primitive_payload_sha256 != expected:
            raise ValueError("visual primitive payload hash mismatch")
        if not self.primitive_payload_sha256:
            object.__setattr__(self, "primitive_payload_sha256", expected)

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class VisualChangePrimitiveRecord:
    visual_change_id: str
    schema_version: str
    created_at: str
    source_kind: str
    previous_visual_primitive_id: str
    current_visual_primitive_id: str
    previous_source_artifact_id: str | None
    current_source_artifact_id: str | None
    width: int
    height: int
    pixel_format: str
    mean_absolute_difference: float
    maximum_grid_difference: float
    changed_grid_cells: tuple[dict[str, object], ...]
    unchanged_grid_cell_count: int
    changed_area_ratio: float
    motion_proxy: float
    stability_proxy: float
    global_luminance_delta: float
    global_contrast_delta: float
    global_edge_density_delta: float
    quality_uncertainty: float
    compiler_id: str
    compiler_version: str
    compiler_config_sha256: str
    semantic_label: None
    object_tracking_created: bool
    primitive_payload_sha256: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != VISUAL_CHANGE_PRIMITIVE_SCHEMA_VERSION:
            raise ValueError("invalid visual change primitive schema_version")
        if self.source_kind not in {"camera", "screen"}:
            raise ValueError("visual change source_kind must be camera or screen")
        if self.pixel_format not in {"BGR8", "BGRA8"}:
            raise ValueError("visual change pixel_format must be BGR8 or BGRA8")
        if self.semantic_label is not None:
            raise ValueError("visual change semantic_label must remain null")
        if self.object_tracking_created:
            raise ValueError("Package 121 visual change must not create object tracking")
        allowed_cell_keys = {
            "grid_x",
            "grid_y",
            "difference_strength",
            "luminance_delta",
            "contrast_delta",
            "edge_density_delta",
        }
        for cell in self.changed_grid_cells:
            if set(cell) - allowed_cell_keys:
                raise ValueError("changed grid cell contains forbidden semantic keys")
        for name in ("changed_area_ratio", "motion_proxy", "stability_proxy", "quality_uncertainty"):
            object.__setattr__(self, name, _ratio(name, getattr(self, name)))
        object.__setattr__(self, "changed_grid_cells", tuple(dict(item) for item in self.changed_grid_cells))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))
        expected = payload_sha256_without(
            self.to_dict(),
            "visual_change_id",
            "created_at",
            "previous_visual_primitive_id",
            "current_visual_primitive_id",
            "primitive_payload_sha256",
        )
        if self.primitive_payload_sha256 and self.primitive_payload_sha256 != expected:
            raise ValueError("visual change payload hash mismatch")
        if not self.primitive_payload_sha256:
            object.__setattr__(self, "primitive_payload_sha256", expected)

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}
