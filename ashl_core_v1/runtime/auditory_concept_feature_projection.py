"""Deterministic low-level source blur for Package 130 AudioPrimitives."""

from __future__ import annotations

from statistics import median
from typing import Any

from ashl_core_v1.perception.audio_primitive_schema import AudioPrimitiveRecord
from ashl_core_v1.runtime.auditory_grounding_types import (
    BLUR_POLICY_VERSION,
    PROJECTION_SCHEMA_VERSION,
    AuditoryConceptFeatureProjection,
    AuditoryGroundingEpisodeRecord,
)
from ashl_core_v1.runtime.host_sensor_types import sha256_payload, utc_now


ENVELOPE_BIN_COUNT = 32
ACTIVE_ENVELOPE_FLOOR = 0.18
MINIMUM_ACTIVE_RUN_BINS = 3
ACTIVE_REGION_BOUNDARY_TRIM_BINS = 1


def build_auditory_concept_feature_projection(
    *,
    episode: AuditoryGroundingEpisodeRecord | dict[str, Any],
    audio_primitive: AudioPrimitiveRecord | dict[str, Any],
) -> AuditoryConceptFeatureProjection:
    episode_item = episode if isinstance(episode, AuditoryGroundingEpisodeRecord) else AuditoryGroundingEpisodeRecord(**dict(episode))
    primitive = audio_primitive if isinstance(audio_primitive, AudioPrimitiveRecord) else AudioPrimitiveRecord(**dict(audio_primitive))
    if primitive.primitive_role != "observed":
        raise ValueError("feature projection requires an observed AudioPrimitive")
    if primitive.audio_primitive_id not in episode_item.audio_primitive_refs:
        raise ValueError("AudioPrimitive does not belong to the grounding episode")
    if primitive.compiler_version != episode_item.compiler_version:
        raise ValueError("AudioPrimitive compiler version does not match episode")
    if primitive.privacy_policy_id != "grounding_conservative_v0":
        raise ValueError("Package 130 requires the grounding conservative compiler policy")
    feature_values = extract_source_blurred_auditory_feature_values(primitive)
    identity = {
        "schema_version": PROJECTION_SCHEMA_VERSION,
        "episode_id": episode_item.episode_id,
        "audio_primitive_refs": episode_item.audio_primitive_refs,
        "normalized_amplitude_envelope": feature_values["normalized_amplitude_envelope"],
        "active_region_count": feature_values["active_region_count"],
        "normalized_region_duration_ratios": feature_values["normalized_region_duration_ratios"],
        "normalized_inter_onset_interval_ratios": feature_values["normalized_inter_onset_interval_ratios"],
        "silence_ratio": feature_values["silence_ratio"],
        "relative_spectral_band_energy": feature_values["relative_spectral_band_energy"],
        "coarse_pitch_contour": feature_values["coarse_pitch_contour"],
        "compiler_version": primitive.compiler_version,
        "blur_policy_version": BLUR_POLICY_VERSION,
    }
    return AuditoryConceptFeatureProjection(
        feature_projection_id=(
            "auditory_concept_feature_projection:" + sha256_payload(identity)
        ),
        schema_version=PROJECTION_SCHEMA_VERSION,
        created_at=utc_now(),
        episode_id=episode_item.episode_id,
        audio_primitive_refs=(primitive.audio_primitive_id,),
        normalized_amplitude_envelope=feature_values["normalized_amplitude_envelope"],
        onset_count=int(feature_values["onset_count"]),
        offset_count=int(feature_values["offset_count"]),
        active_region_count=int(feature_values["active_region_count"]),
        normalized_region_duration_ratios=feature_values["normalized_region_duration_ratios"],
        normalized_inter_onset_interval_ratios=feature_values["normalized_inter_onset_interval_ratios"],
        silence_ratio=float(feature_values["silence_ratio"]),
        relative_spectral_band_energy=feature_values["relative_spectral_band_energy"],
        coarse_pitch_contour=feature_values["coarse_pitch_contour"],
        absolute_pitch_identity_removed=True,
        fine_spectral_identity_removed=True,
        intelligible_content_removed=True,
        semantic_label=None,
        compiler_version=primitive.compiler_version,
        blur_policy_version=BLUR_POLICY_VERSION,
        source_record_refs=(episode_item.episode_id, primitive.audio_primitive_id),
        source_trace_refs=tuple(dict.fromkeys(episode_item.source_trace_refs + primitive.source_trace_refs)),
    )


def extract_source_blurred_auditory_feature_values(
    audio_primitive: AudioPrimitiveRecord | dict[str, Any],
) -> dict[str, Any]:
    """Return the shared Package 130/131 nonsemantic structural feature domain."""

    primitive = (
        audio_primitive
        if isinstance(audio_primitive, AudioPrimitiveRecord)
        else AudioPrimitiveRecord(**dict(audio_primitive))
    )
    if primitive.primitive_role != "observed":
        raise ValueError("source-blurred feature extraction requires an observed AudioPrimitive")
    source_envelope = tuple(float(item) for item in primitive.amplitude_envelope)
    window_envelope = _resample_normalized(source_envelope, ENVELOPE_BIN_COUNT)
    dense_envelope = _resample_normalized(source_envelope, ENVELOPE_BIN_COUNT * 4)
    regions = _active_regions(dense_envelope)
    normalized_envelope = _aggregate_active_region_shape(dense_envelope, regions)
    durations = tuple(end - start for start, end in regions)
    duration_total = sum(durations)
    duration_ratios = (
        tuple(round(item / duration_total, 6) for item in durations)
        if duration_total
        else tuple()
    )
    starts = tuple(start for start, _end in regions)
    intervals = tuple(right - left for left, right in zip(starts, starts[1:]))
    maximum_interval = max(intervals) if intervals else 0
    interval_ratios = (
        tuple(round(item / maximum_interval, 6) for item in intervals)
        if maximum_interval
        else tuple()
    )
    silence_ratio = round(
        sum(1 for value in window_envelope if value < ACTIVE_ENVELOPE_FLOOR)
        / max(1, len(window_envelope)),
        6,
    )
    spectral = tuple(float(value) for _name, value in primitive.relative_band_energy)
    spectral_total = sum(spectral)
    normalized_spectral = (
        tuple(sorted((round(value / spectral_total, 6) for value in spectral), reverse=True))
        if spectral_total > 0.0
        else tuple(0.0 for _ in spectral)
    )
    # The v0 concept intentionally removes absolute pitch and fine spectrum.
    return {
        "normalized_amplitude_envelope": normalized_envelope,
        "onset_count": len(primitive.onset_events),
        "offset_count": len(primitive.offset_events),
        "active_region_count": len(regions),
        "normalized_region_duration_ratios": duration_ratios,
        "normalized_inter_onset_interval_ratios": interval_ratios,
        "silence_ratio": silence_ratio,
        "relative_spectral_band_energy": normalized_spectral,
        "coarse_pitch_contour": None,
    }


def projection_active_regions(
    projection: AuditoryConceptFeatureProjection | dict[str, Any],
) -> tuple[tuple[int, int], ...]:
    item = projection if isinstance(projection, AuditoryConceptFeatureProjection) else AuditoryConceptFeatureProjection(**dict(projection))
    return _active_regions(item.normalized_amplitude_envelope)


def _active_regions(envelope: tuple[float, ...]) -> tuple[tuple[int, int], ...]:
    if not envelope:
        return tuple()
    threshold = _activity_threshold(envelope)
    runs: list[tuple[int, int]] = []
    start: int | None = None
    for index, value in enumerate(envelope):
        if value >= threshold and start is None:
            start = index
        elif value < threshold and start is not None:
            if index - start >= MINIMUM_ACTIVE_RUN_BINS:
                runs.append((start, index))
            start = None
    if start is not None and len(envelope) - start >= MINIMUM_ACTIVE_RUN_BINS:
        runs.append((start, len(envelope)))
    return tuple(runs)


def _aggregate_active_region_shape(
    envelope: tuple[float, ...],
    regions: tuple[tuple[int, int], ...],
) -> tuple[float, ...]:
    if not regions:
        return tuple(0.0 for _ in range(ENVELOPE_BIN_COUNT))
    region_shapes = tuple(
        _resample_normalized(
            envelope[trimmed_start:trimmed_end],
            ENVELOPE_BIN_COUNT,
        )
        for start, end in regions
        for trimmed_start, trimmed_end in (_trim_active_region(start, end),)
    )
    return tuple(
        round(float(median(shape[index] for shape in region_shapes)), 6)
        for index in range(ENVELOPE_BIN_COUNT)
    )


def _trim_active_region(start: int, end: int) -> tuple[int, int]:
    """Remove one detector-boundary bin without erasing a short event."""
    if end - start <= ACTIVE_REGION_BOUNDARY_TRIM_BINS * 2:
        return start, end
    return (
        start + ACTIVE_REGION_BOUNDARY_TRIM_BINS,
        end - ACTIVE_REGION_BOUNDARY_TRIM_BINS,
    )


def _activity_threshold(envelope: tuple[float, ...]) -> float:
    background = float(median(envelope))
    return min(0.72, max(ACTIVE_ENVELOPE_FLOOR, background + 0.12))


def _resample_normalized(values: tuple[float, ...], size: int) -> tuple[float, ...]:
    if not values:
        return tuple(0.0 for _ in range(size))
    peak = max(abs(item) for item in values)
    normalized = tuple(max(0.0, item / peak) for item in values) if peak > 0 else tuple(0.0 for _ in values)
    result: list[float] = []
    for index in range(size):
        start = int(index * len(normalized) / size)
        end = max(start + 1, int((index + 1) * len(normalized) / size))
        bucket = normalized[start:min(len(normalized), end)]
        result.append(round(sum(bucket) / len(bucket), 6) if bucket else 0.0)
    return tuple(result)
