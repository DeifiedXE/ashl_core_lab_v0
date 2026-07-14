"""Deterministic visual frame primitive compiler for Package 121."""

from __future__ import annotations

import math
from statistics import mean, pstdev

from ashl_core_v1.perception.perception_compiler_types import (
    PerceptionCompilerConfig,
    PerceptionCompilerDescriptor,
    build_compiler_config,
    build_compiler_descriptor,
)
from ashl_core_v1.perception.perception_source_buffer import PerceptionSourceBuffer
from ashl_core_v1.perception.visual_primitive_schema import (
    VISUAL_FRAME_PRIMITIVE_SCHEMA_VERSION,
    VisualFramePrimitiveRecord,
)
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now


VISUAL_FRAME_COMPILER_ID = "visual_frame_compiler_v0"
VISUAL_FRAME_COMPILER_VERSION = "visual_frame_compiler_v0"


def build_visual_frame_compiler_descriptor() -> PerceptionCompilerDescriptor:
    return build_compiler_descriptor(
        compiler_id=VISUAL_FRAME_COMPILER_ID,
        compiler_version=VISUAL_FRAME_COMPILER_VERSION,
        supported_source_kinds=("camera", "screen"),
        supported_media_formats=("BGR8", "BGRA8"),
        implementation_module="ashl_core_v1.perception.visual_frame_primitive_compiler",
    )


def build_visual_frame_compiler_config(
    *,
    source_kind: str = "camera",
    grid_width: int = 8,
    grid_height: int = 8,
    luminance_histogram_bins: int = 16,
    channel_histogram_bins: int = 8,
    edge_threshold: float = 0.10,
) -> PerceptionCompilerConfig:
    return build_compiler_config(
        compiler_id=VISUAL_FRAME_COMPILER_ID,
        compiler_version=VISUAL_FRAME_COMPILER_VERSION,
        source_kind=source_kind,
        parameter_payload={
            "grid_width": grid_width,
            "grid_height": grid_height,
            "luminance_histogram_bins": luminance_histogram_bins,
            "channel_histogram_bins": channel_histogram_bins,
            "edge_operator": "first_order_horizontal_vertical_difference",
            "edge_threshold": edge_threshold,
            "normalization_range": "0.0_to_1.0",
            "input_resize_performed": False,
        },
    )


def compile_visual_frame_primitive(
    source: PerceptionSourceBuffer,
    *,
    config: PerceptionCompilerConfig | None = None,
) -> VisualFramePrimitiveRecord:
    if source.source_kind not in {"camera", "screen"}:
        raise ValueError("visual frame compiler requires camera or screen source")
    if source.media_format not in {"BGR8", "BGRA8"}:
        raise ValueError("unsupported visual media format")
    compiler_config = config or build_visual_frame_compiler_config(source_kind=source.source_kind)
    grid_width = int(compiler_config.parameter_payload["grid_width"])
    grid_height = int(compiler_config.parameter_payload["grid_height"])
    bins = int(compiler_config.parameter_payload["luminance_histogram_bins"])
    edge_threshold = float(compiler_config.parameter_payload["edge_threshold"])
    width = int(source.width or 0)
    height = int(source.height or 0)
    channels = 3 if source.media_format == "BGR8" else 4
    stride = int(source.row_stride_bytes or 0)
    if width <= 0 or height <= 0:
        raise ValueError("invalid_dimensions")
    if stride < width * channels:
        raise ValueError("invalid_stride")
    if len(source.readonly_bytes) < stride * height:
        raise ValueError("invalid_byte_length")

    luminance_rows, channel_sums = _luminance_rows(source, width, height, stride, channels)
    luminances = [value for row in luminance_rows for value in row]
    lum_mean = _round(mean(luminances))
    lum_std = _round(pstdev(luminances) if len(luminances) > 1 else 0.0)
    lum_min = _round(min(luminances))
    lum_max = _round(max(luminances))
    histogram = _histogram(luminances, bins)
    channel_distribution = tuple((name, _round(value / max(1, width * height * 255))) for name, value in channel_sums.items())
    edge_density, edge_map = _edge_density(luminance_rows, edge_threshold)
    grid_lum, grid_contrast, grid_edge = _grid_values(luminance_rows, edge_map, grid_width, grid_height)
    clipped_dark = _round(sum(1 for item in luminances if item <= 0.01) / len(luminances))
    clipped_bright = _round(sum(1 for item in luminances if item >= 0.99) / len(luminances))
    quality_uncertainty = _quality_uncertainty(lum_std, clipped_dark, clipped_bright)
    return VisualFramePrimitiveRecord(
        visual_primitive_id=stable_id("visual_frame_primitive"),
        schema_version=VISUAL_FRAME_PRIMITIVE_SCHEMA_VERSION,
        created_at=utc_now(),
        primitive_role="observed",
        source_kind=source.source_kind,
        source_buffer_id=source.buffer_id,
        source_artifact_id=source.source_artifact_id,
        width=width,
        height=height,
        pixel_format=source.media_format,
        luminance_mean=lum_mean,
        luminance_stddev=lum_std,
        luminance_min=lum_min,
        luminance_max=lum_max,
        luminance_histogram=histogram,
        relative_channel_distribution=channel_distribution,
        contrast_proxy=lum_std,
        edge_density=_round(edge_density),
        grid_width=grid_width,
        grid_height=grid_height,
        grid_luminance_means=tuple(_round(item) for item in grid_lum),
        grid_contrast_values=tuple(_round(item) for item in grid_contrast),
        grid_edge_density_values=tuple(_round(item) for item in grid_edge),
        clipped_dark_ratio=clipped_dark,
        clipped_bright_ratio=clipped_bright,
        quality_uncertainty=quality_uncertainty,
        compiler_id=VISUAL_FRAME_COMPILER_ID,
        compiler_version=VISUAL_FRAME_COMPILER_VERSION,
        compiler_config_sha256=compiler_config.config_sha256,
        semantic_label=None,
        object_identity=None,
        object_class=None,
        scene_meaning=None,
        primitive_payload_sha256="",
        source_trace_refs=source.source_trace_refs,
    )


def _luminance_rows(source: PerceptionSourceBuffer, width: int, height: int, stride: int, channels: int) -> tuple[list[list[float]], dict[str, float]]:
    data = source.readonly_bytes
    rows: list[list[float]] = []
    channel_sums = {"blue": 0.0, "green": 0.0, "red": 0.0}
    for y in range(height):
        offset = y * stride
        row: list[float] = []
        for x in range(width):
            index = offset + x * channels
            blue = int(data[index])
            green = int(data[index + 1])
            red = int(data[index + 2])
            channel_sums["blue"] += blue
            channel_sums["green"] += green
            channel_sums["red"] += red
            row.append((0.114 * blue + 0.587 * green + 0.299 * red) / 255.0)
        rows.append(row)
    return rows, channel_sums


def _histogram(values: list[float], bins: int) -> tuple[float, ...]:
    counts = [0] * bins
    for value in values:
        index = min(bins - 1, max(0, int(value * bins)))
        counts[index] += 1
    total = max(1, len(values))
    return tuple(_round(count / total) for count in counts)


def _edge_density(rows: list[list[float]], threshold: float) -> tuple[float, list[list[float]]]:
    height = len(rows)
    width = len(rows[0]) if rows else 0
    edge_map = [[0.0 for _x in range(width)] for _y in range(height)]
    edge_count = 0
    comparisons = 0
    for y in range(height):
        for x in range(width):
            delta = 0.0
            if x + 1 < width:
                delta = max(delta, abs(rows[y][x] - rows[y][x + 1]))
                comparisons += 1
            if y + 1 < height:
                delta = max(delta, abs(rows[y][x] - rows[y + 1][x]))
                comparisons += 1
            edge_map[y][x] = delta
            if delta >= threshold:
                edge_count += 1
    return edge_count / max(1, width * height if comparisons else 1), edge_map


def _grid_values(rows: list[list[float]], edge_map: list[list[float]], grid_width: int, grid_height: int) -> tuple[list[float], list[float], list[float]]:
    height = len(rows)
    width = len(rows[0]) if rows else 0
    lum: list[float] = []
    contrast: list[float] = []
    edge: list[float] = []
    for gy in range(grid_height):
        y0 = int(gy * height / grid_height)
        y1 = max(y0 + 1, int((gy + 1) * height / grid_height))
        for gx in range(grid_width):
            x0 = int(gx * width / grid_width)
            x1 = max(x0 + 1, int((gx + 1) * width / grid_width))
            values = [rows[y][x] for y in range(y0, min(height, y1)) for x in range(x0, min(width, x1))]
            edges = [edge_map[y][x] for y in range(y0, min(height, y1)) for x in range(x0, min(width, x1))]
            lum.append(mean(values) if values else 0.0)
            contrast.append(pstdev(values) if len(values) > 1 else 0.0)
            edge.append(mean(edges) if edges else 0.0)
    return lum, contrast, edge


def _quality_uncertainty(luminance_stddev: float, clipped_dark: float, clipped_bright: float) -> float:
    clipping = min(1.0, clipped_dark + clipped_bright)
    low_contrast = max(0.0, 0.12 - luminance_stddev) / 0.12
    return _round(min(1.0, 0.55 * clipping + 0.45 * low_contrast))


def _round(value: float) -> float:
    if not math.isfinite(value):
        raise ValueError("nonfinite_output")
    return round(float(value), 6)
