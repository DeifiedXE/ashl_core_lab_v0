"""Leave-one-positive-out structural validation for Package 130."""

from __future__ import annotations

from statistics import mean
from typing import Any

from ashl_core_v1.runtime.auditory_grounding_types import (
    VALIDATION_SCHEMA_VERSION,
    AuditoryConceptFeatureProjection,
    AuditoryConceptPredictiveValidation,
)
from ashl_core_v1.runtime.expected_audio_primitive_generator import build_feature_template
from ashl_core_v1.runtime.host_sensor_types import sha256_payload, utc_now


def validate_grounding_corpus_prediction(
    *,
    concept_candidate_id: str,
    positive_projections: tuple[AuditoryConceptFeatureProjection | dict[str, Any], ...],
    contrast_projections: tuple[AuditoryConceptFeatureProjection | dict[str, Any], ...],
    source_trace_refs: tuple[str, ...] = tuple(),
) -> tuple[AuditoryConceptPredictiveValidation, tuple[dict[str, Any], ...]]:
    positives = tuple(_projection(item) for item in positive_projections)
    contrasts = tuple(_projection(item) for item in contrast_projections)
    if len(positives) != 4:
        raise ValueError("Package 130 predictive validation requires four positives")
    if len(contrasts) != 3:
        raise ValueError("Package 130 predictive validation requires three contrasts")
    error_records: list[dict[str, Any]] = []
    supported: list[bool] = []
    for held_out in positives:
        training = tuple(item for item in positives if item.episode_id != held_out.episode_id)
        centers, tolerances = build_feature_template(training)
        record = compare_projection_to_template(
            projection=held_out,
            centers=centers,
            tolerances=tolerances,
            evaluation_kind="positive_holdout",
        )
        error_records.append(record)
        supported.append(bool(record["inside_all_structural_tolerances"]))
    full_centers, full_tolerances = build_feature_template(positives)
    confusion: list[str] = []
    for contrast in contrasts:
        record = compare_projection_to_template(
            projection=contrast,
            centers=full_centers,
            tolerances=full_tolerances,
            evaluation_kind="contrast",
        )
        error_records.append(record)
        if record["inside_all_structural_tolerances"]:
            confusion.append(contrast.episode_id)
    all_supported = all(supported)
    all_distinguished = not confusion
    improvement = _prediction_improves_over_unconditioned(positives, contrasts, full_centers)
    passed = all_supported and all_distinguished and improvement
    identity = {
        "concept_candidate_id": concept_candidate_id,
        "positive_holdouts": tuple(item.episode_id for item in positives),
        "contrasts": tuple(item.episode_id for item in contrasts),
        "error_record_ids": tuple(item["prediction_error_record_id"] for item in error_records),
        "passed": passed,
    }
    validation = AuditoryConceptPredictiveValidation(
        predictive_validation_id="auditory_concept_predictive_validation:" + sha256_payload(identity),
        schema_version=VALIDATION_SCHEMA_VERSION,
        created_at=utc_now(),
        concept_candidate_id=concept_candidate_id,
        positive_holdout_episode_refs=tuple(item.episode_id for item in positives),
        contrast_episode_refs=tuple(item.episode_id for item in contrasts),
        positive_holdout_error_records=tuple(item["prediction_error_record_id"] for item in error_records[:4]),
        contrast_error_records=tuple(item["prediction_error_record_id"] for item in error_records[4:]),
        positive_holdout_count=len(positives),
        contrast_count=len(contrasts),
        all_positive_holdouts_supported=all_supported,
        all_contrasts_distinguished=all_distinguished,
        confusion_episode_refs=tuple(confusion),
        prediction_improvement_over_unconditioned_baseline=improvement,
        predictive_validation_passed=passed,
        runtime_recognition_enabled=False,
        new_event_classification_performed=False,
        source_record_refs=tuple(item.feature_projection_id for item in positives + contrasts),
        source_trace_refs=tuple(source_trace_refs),
    )
    return validation, tuple(error_records)


def compare_projection_to_template(
    *,
    projection: AuditoryConceptFeatureProjection,
    centers: dict[str, object],
    tolerances: dict[str, object],
    evaluation_kind: str,
) -> dict[str, Any]:
    feature_values = {
        name: getattr(projection, name)
        for name in (
            "normalized_amplitude_envelope",
            "onset_count",
            "offset_count",
            "active_region_count",
            "normalized_region_duration_ratios",
            "normalized_inter_onset_interval_ratios",
            "silence_ratio",
            "relative_spectral_band_energy",
            "coarse_pitch_contour",
        )
    }
    errors, checks, inside = compare_low_level_auditory_features_to_template(
        observed_feature_values=feature_values,
        centers=centers,
        tolerances=tolerances,
    )
    payload = {
        "schema_version": "ashl_auditory_concept_prediction_error_v0",
        "episode_id": projection.episode_id,
        "feature_projection_id": projection.feature_projection_id,
        "evaluation_kind": evaluation_kind,
        "per_feature_errors": errors,
        "per_feature_tolerance_checks": checks,
        "inside_all_structural_tolerances": inside,
        "opaque_confidence_score_used": False,
        "runtime_recognition_performed": False,
        "created_at": utc_now(),
    }
    payload["prediction_error_record_id"] = "auditory_prediction_error:" + sha256_payload(
        {key: value for key, value in payload.items() if key != "created_at"}
    )
    return payload


def compare_low_level_auditory_features_to_template(
    *,
    observed_feature_values: dict[str, object],
    centers: dict[str, object],
    tolerances: dict[str, object],
) -> tuple[dict[str, Any], dict[str, bool], bool]:
    """Compare one source-blurred payload to the frozen Package 130 template."""

    errors: dict[str, Any] = {}
    checks: dict[str, bool] = {}
    for name in ("onset_count", "offset_count", "active_region_count", "silence_ratio"):
        error = abs(float(observed_feature_values[name]) - float(centers[name]))
        errors[name] = round(error, 6)
        checks[name] = error <= float(tolerances[name])
    for name in (
        "normalized_amplitude_envelope",
        "normalized_region_duration_ratios",
        "normalized_inter_onset_interval_ratios",
        "relative_spectral_band_energy",
    ):
        values = tuple(float(item) for item in (observed_feature_values[name] or ()))
        expected = tuple(float(item) for item in centers[name])
        allowed = tuple(float(item) for item in tolerances[name])
        vector_errors = _vector_errors(values, expected)
        errors[name] = vector_errors
        checks[name] = len(values) == len(expected) and all(
            value <= allowed[index] for index, value in enumerate(vector_errors)
        )
    expected_pitch = centers.get("coarse_pitch_contour")
    allowed_pitch = tolerances.get("coarse_pitch_contour")
    if expected_pitch is None:
        errors["coarse_pitch_contour"] = None
        checks["coarse_pitch_contour"] = True
    else:
        values = tuple(
            float(item)
            for item in (observed_feature_values.get("coarse_pitch_contour") or ())
        )
        expected = tuple(float(item) for item in expected_pitch)
        vector_errors = _vector_errors(values, expected)
        errors["coarse_pitch_contour"] = vector_errors
        checks["coarse_pitch_contour"] = len(values) == len(expected) and all(
            value <= float(tuple(allowed_pitch)[index])
            for index, value in enumerate(vector_errors)
        )
    return errors, checks, all(checks.values())


def _prediction_improves_over_unconditioned(
    positives: tuple[AuditoryConceptFeatureProjection, ...],
    contrasts: tuple[AuditoryConceptFeatureProjection, ...],
    positive_centers: dict[str, object],
) -> bool:
    corpus = positives + contrasts
    unconditioned_centers, _ = build_feature_template(corpus)
    positive_error = mean(_template_distance(item, positive_centers) for item in positives)
    unconditioned_error = mean(_template_distance(item, unconditioned_centers) for item in positives)
    contrast_separation = mean(_template_distance(item, positive_centers) for item in contrasts)
    return positive_error < unconditioned_error and contrast_separation > positive_error


def _template_distance(item: AuditoryConceptFeatureProjection, centers: dict[str, object]) -> float:
    errors = [
        abs(float(item.active_region_count) - float(centers["active_region_count"])),
        abs(float(item.silence_ratio) - float(centers["silence_ratio"])),
    ]
    for name in (
        "normalized_amplitude_envelope",
        "normalized_region_duration_ratios",
        "normalized_inter_onset_interval_ratios",
        "relative_spectral_band_energy",
    ):
        values = tuple(float(value) for value in getattr(item, name))
        expected = tuple(float(value) for value in centers[name])
        vector_errors = _vector_errors(values, expected)
        errors.append(mean(vector_errors) if vector_errors else (0.0 if not values and not expected else 1.0))
    return float(mean(errors))


def _vector_errors(values: tuple[float, ...], expected: tuple[float, ...]) -> tuple[float, ...]:
    if len(values) != len(expected):
        return tuple(1.0 for _ in range(max(len(values), len(expected), 1)))
    return tuple(round(abs(left - right), 6) for left, right in zip(values, expected))


def _projection(value: AuditoryConceptFeatureProjection | dict[str, Any]) -> AuditoryConceptFeatureProjection:
    return value if isinstance(value, AuditoryConceptFeatureProjection) else AuditoryConceptFeatureProjection(**dict(value))
