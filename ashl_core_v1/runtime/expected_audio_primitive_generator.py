"""Expected AudioPrimitive generation from positive Package 130 projections."""

from __future__ import annotations

from statistics import median
from typing import Any

from ashl_core_v1.perception.audio_primitive_compiler import (
    AUDIO_PRIMITIVE_COMPILER_ID,
    AUDIO_PRIMITIVE_COMPILER_VERSION,
    RELATIVE_BANDS,
)
from ashl_core_v1.perception.audio_primitive_schema import (
    AUDIO_PRIMITIVE_SCHEMA_VERSION,
    AudioPrimitiveRecord,
)
from ashl_core_v1.runtime.auditory_grounding_types import (
    BLUR_POLICY_VERSION,
    GENERATION_SCHEMA_VERSION,
    AuditoryConceptFeatureProjection,
    ExpectedAudioPrimitiveGenerationRecord,
)
from ashl_core_v1.runtime.host_sensor_types import canonical_json, sha256_payload, utc_now


FIXED_TOLERANCE_MARGIN = {
    "count": 0.0,
    "envelope": 0.34,
    "duration_ratio": 0.16,
    "interval_ratio": 0.26,
    "silence_ratio": 0.12,
    "spectral": 0.45,
    "pitch": 0.20,
}


def concept_candidate_identity(
    *,
    source_condition_profile_id: str,
    positive_episode_content_identities: tuple[str, ...],
    contrast_episode_content_identities: tuple[str, ...],
    positive_projection_refs: tuple[str, ...],
    contrast_projection_refs: tuple[str, ...],
    compiler_version: str,
    blur_policy_version: str,
) -> str:
    payload = {
        "schema_version": "ashl_grounded_auditory_event_concept_candidate_identity_v0",
        "source_condition_profile_id": source_condition_profile_id,
        "positive_episode_content_identities": tuple(positive_episode_content_identities),
        "contrast_episode_content_identities": tuple(contrast_episode_content_identities),
        "positive_projection_refs": tuple(positive_projection_refs),
        "contrast_projection_refs": tuple(contrast_projection_refs),
        "compiler_version": compiler_version,
        "blur_policy_version": blur_policy_version,
    }
    return "grounded_auditory_concept_candidate:" + sha256_payload(payload)


def generate_expected_audio_primitive(
    *,
    concept_candidate_id: str,
    positive_projections: tuple[AuditoryConceptFeatureProjection | dict[str, Any], ...],
    persist_primitive: Any | None = None,
    source_trace_refs: tuple[str, ...] = tuple(),
) -> tuple[AudioPrimitiveRecord, ExpectedAudioPrimitiveGenerationRecord]:
    projections = tuple(
        item if isinstance(item, AuditoryConceptFeatureProjection) else AuditoryConceptFeatureProjection(**dict(item))
        for item in positive_projections
    )
    if len(projections) < 1:
        raise ValueError("expected primitive requires positive projections")
    if len({item.episode_id for item in projections}) != len(projections):
        raise ValueError("expected primitive source projections must be distinct episodes")
    if len({item.compiler_version for item in projections}) != 1:
        raise ValueError("blocked_compiler_version_mismatch")
    if len({item.blur_policy_version for item in projections}) != 1:
        raise ValueError("blocked_blur_policy_mismatch")
    centers, tolerances = build_feature_template(projections)
    expected_identity = {
        "schema_version": AUDIO_PRIMITIVE_SCHEMA_VERSION,
        "primitive_role": "expected",
        "source_concept_id": concept_candidate_id,
        "source_positive_projection_refs": tuple(item.feature_projection_id for item in projections),
        "feature_centers": centers,
        "feature_tolerances": tolerances,
        "compiler_version": AUDIO_PRIMITIVE_COMPILER_VERSION,
        "blur_policy_version": BLUR_POLICY_VERSION,
    }
    primitive_id = "audio_primitive:expected:" + sha256_payload(expected_identity)
    onset_count = int(centers["onset_count"])
    offset_count = int(centers["offset_count"])
    expected = AudioPrimitiveRecord(
        audio_primitive_id=primitive_id,
        schema_version=AUDIO_PRIMITIVE_SCHEMA_VERSION,
        created_at=utc_now(),
        primitive_role="expected",
        source_kind="microphone",
        source_buffer_id=None,
        source_artifact_id=None,
        source_concept_id=concept_candidate_id,
        window_start_offset_ms=0,
        window_end_offset_ms=0,
        amplitude_envelope=tuple(centers["normalized_amplitude_envelope"]),
        relative_band_energy=tuple(
            (name, float(value))
            for (name, _center), value in zip(
                RELATIVE_BANDS,
                tuple(centers["relative_spectral_band_energy"]),
            )
        ),
        onset_events=tuple({"relative_index": index} for index in range(onset_count)),
        offset_events=tuple({"relative_index": index} for index in range(offset_count)),
        rhythm_interval_pattern=tuple(centers["normalized_inter_onset_interval_ratios"]),
        pause_intervals=tuple(),
        relative_pitch_contour=tuple(centers.get("coarse_pitch_contour") or ()),
        coarse_pitch_band="relative_only",
        harmonicity_proxy=tuple(),
        noisiness_proxy=tuple(),
        duration_ms=0,
        uncertainty=min(1.0, max(_flatten_numeric(tolerances), default=0.0)),
        compiler_id=AUDIO_PRIMITIVE_COMPILER_ID,
        compiler_version=AUDIO_PRIMITIVE_COMPILER_VERSION,
        privacy_policy_id="grounding_conservative_v0",
        semantic_label=None,
        speech_content=None,
        speaker_identity=None,
        emotion_label=None,
        source_trace_refs=tuple(source_trace_refs),
    )
    if persist_primitive is not None:
        persist_primitive(expected)
    generation_identity = {
        "concept_candidate_id": concept_candidate_id,
        "source_positive_projection_refs": tuple(item.feature_projection_id for item in projections),
        "expected_audio_primitive_refs": (primitive_id,),
        "feature_centers": centers,
        "feature_tolerances": tolerances,
    }
    generation = ExpectedAudioPrimitiveGenerationRecord(
        generation_id="expected_audio_primitive_generation:" + sha256_payload(generation_identity),
        schema_version=GENERATION_SCHEMA_VERSION,
        created_at=utc_now(),
        concept_candidate_id=concept_candidate_id,
        source_positive_projection_refs=tuple(item.feature_projection_id for item in projections),
        expected_audio_primitive_refs=(primitive_id,),
        aggregation_method="deterministic_coordinate_median",
        tolerance_method="maximum_positive_deviation_plus_fixed_margin_v0",
        observed_expected_schema_equal=True,
        deterministic_generation=True,
        stimulus_ground_truth_used=False,
        teacher_feature_values_used=False,
        feature_centers=centers,
        feature_tolerances=tolerances,
        source_record_refs=tuple(item.feature_projection_id for item in projections),
        source_trace_refs=tuple(source_trace_refs),
    )
    canonical_json(generation.to_dict())
    return expected, generation


def build_feature_template(
    projections: tuple[AuditoryConceptFeatureProjection, ...],
) -> tuple[dict[str, object], dict[str, object]]:
    scalar_names = ("onset_count", "offset_count", "active_region_count", "silence_ratio")
    vector_names = (
        "normalized_amplitude_envelope",
        "normalized_region_duration_ratios",
        "normalized_inter_onset_interval_ratios",
        "relative_spectral_band_energy",
    )
    centers: dict[str, object] = {}
    tolerances: dict[str, object] = {}
    for name in scalar_names:
        values = tuple(float(getattr(item, name)) for item in projections)
        center = float(median(values))
        if name.endswith("count"):
            center = float(round(center))
            margin = FIXED_TOLERANCE_MARGIN["count"]
        else:
            margin = FIXED_TOLERANCE_MARGIN["silence_ratio"]
        centers[name] = int(center) if name.endswith("count") else round(center, 6)
        tolerances[name] = round(max(abs(value - center) for value in values) + margin, 6)
    margin_by_vector = {
        "normalized_amplitude_envelope": FIXED_TOLERANCE_MARGIN["envelope"],
        "normalized_region_duration_ratios": FIXED_TOLERANCE_MARGIN["duration_ratio"],
        "normalized_inter_onset_interval_ratios": FIXED_TOLERANCE_MARGIN["interval_ratio"],
        "relative_spectral_band_energy": FIXED_TOLERANCE_MARGIN["spectral"],
    }
    for name in vector_names:
        vectors = tuple(tuple(float(value) for value in getattr(item, name)) for item in projections)
        center = _coordinate_median(vectors)
        centers[name] = center
        tolerances[name] = tuple(
            round(max(abs(vector[index] - center[index]) for vector in vectors) + margin_by_vector[name], 6)
            for index in range(len(center))
        )
    pitches = tuple(tuple(item.coarse_pitch_contour or ()) for item in projections)
    if pitches and all(pitches) and len({len(item) for item in pitches}) == 1:
        center_pitch = _coordinate_median(pitches)
        centers["coarse_pitch_contour"] = center_pitch
        tolerances["coarse_pitch_contour"] = tuple(
            round(max(abs(vector[index] - center_pitch[index]) for vector in pitches) + FIXED_TOLERANCE_MARGIN["pitch"], 6)
            for index in range(len(center_pitch))
        )
    else:
        centers["coarse_pitch_contour"] = None
        tolerances["coarse_pitch_contour"] = None
    return centers, tolerances


def _coordinate_median(vectors: tuple[tuple[float, ...], ...]) -> tuple[float, ...]:
    if not vectors:
        return tuple()
    lengths = {len(item) for item in vectors}
    if len(lengths) != 1:
        return tuple()
    size = next(iter(lengths))
    return tuple(round(float(median(vector[index] for vector in vectors)), 6) for index in range(size))


def _flatten_numeric(value: Any) -> tuple[float, ...]:
    result: list[float] = []
    if isinstance(value, dict):
        for item in value.values():
            result.extend(_flatten_numeric(item))
    elif isinstance(value, (list, tuple)):
        for item in value:
            result.extend(_flatten_numeric(item))
    elif isinstance(value, (int, float)):
        result.append(float(value))
    return tuple(result)
