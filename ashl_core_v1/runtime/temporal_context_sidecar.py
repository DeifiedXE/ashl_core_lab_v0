"""Read-only temporal context sidecar helpers for Package 124A."""

from __future__ import annotations

from ashl_core_v1.runtime.host_sensor_types import utc_now
from ashl_core_v1.runtime.temporal_types import (
    TEMPORAL_CONTEXT_SIDECAR_SCHEMA_VERSION,
    GroundedTemporalPrimitiveBundle,
    TemporalPerceptionContextSidecar,
    temporal_identity,
)


TEMPORAL_OPERATOR_EVENT_FAMILIES = (
    "temporal_clock_domain_created",
    "temporal_clock_quality_verified",
    "temporal_anchor_created",
    "temporal_span_created",
    "temporal_interval_created",
    "temporal_relation_created",
    "temporal_continuity_created",
    "external_gap_discovered",
    "temporal_bundle_compiled",
    "temporal_sidecar_attached",
    "temporal_calibration_completed",
    "temporal_audit_failed",
)


def attach_temporal_context_sidecar(
    *,
    source_perception_record_id: str,
    bundle: GroundedTemporalPrimitiveBundle,
    anchor_refs: tuple[str, ...] = tuple(),
    span_refs: tuple[str, ...] = tuple(),
    relation_refs: tuple[str, ...] = tuple(),
    continuity_refs: tuple[str, ...] = tuple(),
    source_record_refs: tuple[str, ...] = tuple(),
    source_trace_refs: tuple[str, ...] = tuple(),
    created_at: str | None = None,
) -> TemporalPerceptionContextSidecar:
    payload = {
        "schema_version": TEMPORAL_CONTEXT_SIDECAR_SCHEMA_VERSION,
        "source_perception_record_id": source_perception_record_id,
        "temporal_bundle_id": bundle.temporal_bundle_id,
        "anchor_refs": tuple(anchor_refs or bundle.anchor_refs[:2]),
        "span_refs": tuple(span_refs or bundle.span_refs[:4]),
        "relation_refs": tuple(relation_refs or bundle.relation_refs[:4]),
        "continuity_refs": tuple(continuity_refs or bundle.continuity_refs),
        "sidecar_authority": "read_only_context",
        "read_only": True,
        "scoring_authority": False,
        "memory_write_authority": False,
        "action_selection_authority": False,
        "output_authority": False,
        "source_record_refs": tuple(source_record_refs or (source_perception_record_id, bundle.temporal_bundle_id)),
        "source_trace_refs": tuple(source_trace_refs or bundle.source_trace_refs),
    }
    return TemporalPerceptionContextSidecar(
        temporal_sidecar_id=temporal_identity("temporal_sidecar", payload),
        created_at=created_at or utc_now(),
        **payload,
    )


def verify_package_112_score_equivalence(before_score: float, after_score: float) -> dict[str, object]:
    """Package 124A sidecars are read-only context and contribute zero score."""
    changed = abs(float(before_score) - float(after_score)) > 0.000001
    return {
        "package_112_score_changed": changed,
        "score_before": float(before_score),
        "score_after": float(after_score),
        "temporal_score_contribution": 0.0,
        "sidecar_authority": "read_only_context",
    }
