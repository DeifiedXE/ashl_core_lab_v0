"""Canonical Package 126 sampling-plan identity without session-local fields."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import sha256_payload, stable_id, utc_now
from ashl_core_v1.runtime.perception_reacquisition_types import SamplingPlanIdentityRecord


SAMPLING_PLAN_IDENTITY_SCHEMA_VERSION = "ashl_package_126_sampling_plan_identity_v0"

_HASH_FIELDS = (
    "plan_kind",
    "modality_scope",
    "required_lanes",
    "participating_lanes",
    "screen_target_descriptor_hash",
    "screen_region_hash",
    "screen_capture_config_hash",
    "audio_endpoint_descriptor_hash",
    "audio_capture_config_hash",
    "audio_privacy_mode",
    "audio_blur_policy_version",
    "host_state_config_hash",
    "visual_compiler_version",
    "audio_compiler_version",
    "redaction_config_hash",
    "event_clock_domain",
    "processing_clock_domain",
    "replay_clock_domain",
)


def build_sampling_plan_identity(
    *,
    plan_kind: str,
    modality_scope: tuple[str, ...],
    required_lanes: tuple[str, ...],
    participating_lanes: tuple[str, ...],
    screen_target_descriptor_hash: str | None = None,
    screen_region_hash: str | None = None,
    screen_capture_config_hash: str | None = None,
    audio_endpoint_descriptor_hash: str | None = None,
    audio_capture_config_hash: str | None = None,
    audio_privacy_mode: str | None = None,
    audio_blur_policy_version: str | None = None,
    host_state_config_hash: str | None = None,
    visual_compiler_version: str | None = None,
    audio_compiler_version: str | None = None,
    redaction_config_hash: str | None = None,
    event_clock_domain: str = "windows_query_performance_counter_monotonic_ns",
    processing_clock_domain: str = "python_process_monotonic_ns",
    replay_clock_domain: str | None = None,
    source_record_refs: tuple[str, ...] = tuple(),
    source_trace_refs: tuple[str, ...] = tuple(),
) -> SamplingPlanIdentityRecord:
    payload: dict[str, Any] = {
        "plan_kind": plan_kind,
        "modality_scope": tuple(modality_scope),
        "required_lanes": tuple(required_lanes),
        "participating_lanes": tuple(participating_lanes),
        "screen_target_descriptor_hash": screen_target_descriptor_hash,
        "screen_region_hash": screen_region_hash,
        "screen_capture_config_hash": screen_capture_config_hash,
        "audio_endpoint_descriptor_hash": audio_endpoint_descriptor_hash,
        "audio_capture_config_hash": audio_capture_config_hash,
        "audio_privacy_mode": audio_privacy_mode,
        "audio_blur_policy_version": audio_blur_policy_version,
        "host_state_config_hash": host_state_config_hash,
        "visual_compiler_version": visual_compiler_version,
        "audio_compiler_version": audio_compiler_version,
        "redaction_config_hash": redaction_config_hash,
        "event_clock_domain": event_clock_domain,
        "processing_clock_domain": processing_clock_domain,
        "replay_clock_domain": replay_clock_domain,
    }
    return SamplingPlanIdentityRecord(
        sampling_plan_identity_id=stable_id("sampling_plan_identity"),
        schema_version=SAMPLING_PLAN_IDENTITY_SCHEMA_VERSION,
        created_at=utc_now(),
        canonical_plan_hash=sha256_payload({name: payload[name] for name in _HASH_FIELDS}),
        source_record_refs=tuple(source_record_refs),
        source_trace_refs=tuple(source_trace_refs),
        **payload,
    )


def clone_sampling_plan_identity(
    plan: SamplingPlanIdentityRecord,
    *,
    source_record_refs: tuple[str, ...] = tuple(),
    source_trace_refs: tuple[str, ...] = tuple(),
) -> SamplingPlanIdentityRecord:
    """Create a child identity record while preserving its material plan hash."""

    return replace(
        plan,
        sampling_plan_identity_id=stable_id("sampling_plan_identity"),
        created_at=utc_now(),
        source_record_refs=tuple(source_record_refs),
        source_trace_refs=tuple(source_trace_refs),
    )


def plan_identity_equal(
    parent: SamplingPlanIdentityRecord,
    child: SamplingPlanIdentityRecord,
) -> bool:
    return parent.canonical_plan_hash == child.canonical_plan_hash


def target_identity_equal(
    parent: SamplingPlanIdentityRecord,
    child: SamplingPlanIdentityRecord,
) -> bool:
    return (
        parent.screen_target_descriptor_hash == child.screen_target_descriptor_hash
        and parent.screen_region_hash == child.screen_region_hash
        and parent.audio_endpoint_descriptor_hash == child.audio_endpoint_descriptor_hash
    )


def configuration_identity_equal(
    parent: SamplingPlanIdentityRecord,
    child: SamplingPlanIdentityRecord,
) -> bool:
    return all(
        getattr(parent, name) == getattr(child, name)
        for name in (
            "screen_capture_config_hash",
            "audio_capture_config_hash",
            "audio_privacy_mode",
            "audio_blur_policy_version",
            "host_state_config_hash",
            "visual_compiler_version",
            "audio_compiler_version",
            "redaction_config_hash",
            "required_lanes",
            "participating_lanes",
            "event_clock_domain",
            "processing_clock_domain",
            "replay_clock_domain",
        )
    )
