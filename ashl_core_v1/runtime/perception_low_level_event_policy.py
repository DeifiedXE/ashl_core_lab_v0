"""Deterministic low-level event emission policy for Package 122."""

from __future__ import annotations

from dataclasses import dataclass, fields

from ashl_core_v1.runtime.host_sensor_types import plain, utc_now
from ashl_core_v1.runtime.multimodal_perception_session_types import LOW_LEVEL_EVENT_KINDS, MultimodalAlignmentWindowRecord


EVENT_POLICY_SCHEMA_VERSION = "ashl_perception_low_level_event_emission_policy_v0"


@dataclass(frozen=True)
class PerceptionLowLevelEventEmissionPolicy:
    event_emission_policy_id: str
    schema_version: str
    created_at: str
    visual_change_enabled: bool
    audio_activity_enabled: bool
    host_state_delta_enabled: bool
    multimodal_change_requires_changed_lane_count: int
    semantic_binding_created: bool

    def __post_init__(self) -> None:
        if self.schema_version != EVENT_POLICY_SCHEMA_VERSION:
            raise ValueError("invalid event policy schema_version")
        if self.semantic_binding_created:
            raise ValueError("Package 122 event policy must not create semantic binding")

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


def build_default_low_level_event_policy() -> PerceptionLowLevelEventEmissionPolicy:
    return PerceptionLowLevelEventEmissionPolicy(
        event_emission_policy_id="perception_low_level_event_emission_policy_v0",
        schema_version=EVENT_POLICY_SCHEMA_VERSION,
        created_at=utc_now(),
        visual_change_enabled=True,
        audio_activity_enabled=True,
        host_state_delta_enabled=True,
        multimodal_change_requires_changed_lane_count=2,
        semantic_binding_created=False,
    )


def choose_low_level_event_kind(
    window: MultimodalAlignmentWindowRecord,
    *,
    policy: PerceptionLowLevelEventEmissionPolicy | None = None,
) -> str:
    policy = policy or build_default_low_level_event_policy()
    if window.missing_required_source_kinds:
        return "perception_window_incomplete_event"
    changed = 0
    if policy.visual_change_enabled and window.visual_change_present:
        changed += 1
    if policy.audio_activity_enabled and window.audio_activity_present:
        changed += 1
    if policy.host_state_delta_enabled and window.host_state_delta_present:
        changed += 1
    if changed >= policy.multimodal_change_requires_changed_lane_count:
        return "multimodal_low_level_change_event"
    if policy.visual_change_enabled and window.visual_change_present:
        return "visual_low_level_change_event"
    if policy.audio_activity_enabled and window.audio_activity_present:
        return "audio_low_level_activity_event"
    if policy.host_state_delta_enabled and window.host_state_delta_present:
        return "host_state_low_level_delta_event"
    return "multimodal_low_level_observation_event"


def validate_low_level_event_kind(event_kind: str) -> bool:
    return event_kind in LOW_LEVEL_EVENT_KINDS
