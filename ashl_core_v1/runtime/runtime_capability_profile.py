"""Immutable runtime capability profile for bounded embodied sessions."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from ashl_core_v1.host_body.host_body_embodied_learning_closed_loop_audit import (
    build_demo_host_body_embodied_learning_closed_loop_pass,
    validate_host_body_embodied_learning_closed_loop_milestone_audit,
)
from ashl_core_v1.host_body.host_body_working_readback_integration import (
    build_demo_trace_spine_raw_evidence_boundary,
    validate_trace_spine_raw_evidence_boundary,
)
from ashl_core_v1.host_body.internal_action_home_surface_link import (
    build_demo_mark_uncertain_home_surface_link,
    validate_internal_action_home_surface_link_audit,
)
from ashl_core_v1.host_body.qingyin_host_body_v0_milestone_audit import (
    build_demo_qingyin_host_body_v0_milestone_pass,
    validate_qingyin_host_body_v0_milestone_audit,
)
from ashl_core_v1.runtime.session_learning_evidence_identity import calculate_sha256


PROFILE_SCHEMA_VERSION = "ashl_runtime_capability_profile_v0"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _plain(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


@dataclass(frozen=True)
class RuntimeCapabilityProfile:
    profile_id: str
    schema_version: str
    created_at: str
    profile_version: str
    fixture_only: bool
    host_body_v0_available: bool
    trace_spine_boundary_available: bool
    embodied_learning_loop_available: bool
    home_surface_link_available: bool
    allowed_fixture_kinds: tuple[str, ...]
    bound_module_paths: tuple[str, ...]
    bound_callable_names: tuple[str, ...]
    validation_results: tuple[dict[str, Any], ...]
    prerequisite_records: dict[str, dict[str, Any]]
    profile_sha256: str
    immutable_profile: bool

    def __post_init__(self) -> None:
        if self.schema_version != PROFILE_SCHEMA_VERSION:
            raise ValueError("schema_version must be ashl_runtime_capability_profile_v0")
        object.__setattr__(self, "allowed_fixture_kinds", tuple(str(item) for item in self.allowed_fixture_kinds))
        object.__setattr__(self, "bound_module_paths", tuple(str(item) for item in self.bound_module_paths))
        object.__setattr__(self, "bound_callable_names", tuple(str(item) for item in self.bound_callable_names))
        object.__setattr__(self, "validation_results", tuple(dict(item) for item in self.validation_results))
        object.__setattr__(self, "prerequisite_records", {str(key): dict(value) for key, value in self.prerequisite_records.items()})

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    def record(self, name: str) -> dict[str, Any]:
        if name not in self.prerequisite_records:
            raise KeyError(f"missing runtime capability prerequisite: {name}")
        return dict(self.prerequisite_records[name])


def _profile_payload_for_hash(data: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in data.items()
        if key not in {"created_at", "profile_sha256"}
    }


def build_verified_runtime_capability_profile() -> RuntimeCapabilityProfile:
    host_body_payload = build_demo_qingyin_host_body_v0_milestone_pass()
    closed_loop_payload = build_demo_host_body_embodied_learning_closed_loop_pass()
    boundary_payload = build_demo_trace_spine_raw_evidence_boundary()
    home_surface_payload = build_demo_mark_uncertain_home_surface_link()
    host_body_audit = host_body_payload["host_body_v0_milestone_audit"]
    closed_loop_audit = closed_loop_payload["host_body_embodied_learning_closed_loop_milestone_audit"]
    trace_spine_boundary = boundary_payload["trace_spine_raw_evidence_boundary"]
    home_surface_audit = home_surface_payload["internal_action_home_surface_link_audit"]
    validation_results = (
        {
            "record": "host_body_v0_audit",
            **validate_qingyin_host_body_v0_milestone_audit(host_body_audit),
        },
        {
            "record": "closed_loop_milestone_audit",
            **validate_host_body_embodied_learning_closed_loop_milestone_audit(closed_loop_audit),
        },
        {
            "record": "trace_spine_raw_evidence_boundary",
            **validate_trace_spine_raw_evidence_boundary(trace_spine_boundary),
        },
        {
            "record": "home_surface_link_audit",
            **validate_internal_action_home_surface_link_audit(home_surface_audit),
        },
    )
    data: dict[str, Any] = {
        "profile_id": f"runtime_capability_profile:{uuid4().hex[:12]}",
        "schema_version": PROFILE_SCHEMA_VERSION,
        "created_at": _now(),
        "profile_version": "fixture_package_117_v0",
        "fixture_only": True,
        "host_body_v0_available": True,
        "trace_spine_boundary_available": True,
        "embodied_learning_loop_available": True,
        "home_surface_link_available": True,
        "allowed_fixture_kinds": (
            "camera_unknown_low_level_event",
            "runtime_bridge_deferred",
        ),
        "bound_module_paths": (
            "ashl_core_v1.host_body.host_body_sensor_events",
            "ashl_core_v1.host_body.host_body_runtime_bridge",
            "ashl_core_v1.host_body.host_body_trace_history_lane",
            "ashl_core_v1.host_body.host_body_internal_action_choice",
            "ashl_core_v1.host_body.host_body_learning_feedback_bridge",
            "ashl_core_v1.host_body.host_body_existing_learning_pipeline_compatibility",
            "ashl_core_v1.host_body.internal_action_home_surface_link",
        ),
        "bound_callable_names": (
            "build_host_body_event_record",
            "map_host_body_event_to_runtime_eventframe",
            "build_host_body_trace_history_entry",
            "build_host_body_internal_action_choice",
            "build_host_body_learning_evidence_packet",
            "build_host_body_feedback_existing_review_adapter",
            "build_internal_action_home_surface_mapping",
        ),
        "validation_results": validation_results,
        "prerequisite_records": {
            "host_body_v0_audit": host_body_audit,
            "closed_loop_milestone_audit": closed_loop_audit,
            "trace_spine_raw_evidence_boundary": trace_spine_boundary,
            "home_surface_link_audit": home_surface_audit,
        },
        "profile_sha256": "",
        "immutable_profile": True,
    }
    data["profile_sha256"] = calculate_sha256(_profile_payload_for_hash(data))
    return RuntimeCapabilityProfile(**data)


def validate_runtime_capability_profile(
    profile: RuntimeCapabilityProfile | dict[str, object],
) -> dict[str, object]:
    try:
        item = profile if isinstance(profile, RuntimeCapabilityProfile) else RuntimeCapabilityProfile(**dict(profile))
    except Exception as error:
        return {"valid": False, "status": "blocked_invalid_runtime_capability_profile", "reasons": (str(error),)}
    payload = _profile_payload_for_hash(item.to_dict())
    reasons: list[str] = []
    if not item.fixture_only:
        reasons.append("profile_not_fixture_only")
    if not item.immutable_profile:
        reasons.append("profile_not_immutable")
    if not all(
        (
            item.host_body_v0_available,
            item.trace_spine_boundary_available,
            item.embodied_learning_loop_available,
            item.home_surface_link_available,
        )
    ):
        reasons.append("required_capability_missing")
    if not all(result.get("valid") for result in item.validation_results):
        reasons.append("validation_result_failed")
    if calculate_sha256(payload) != item.profile_sha256:
        reasons.append("profile_hash_mismatch")
    return {
        "valid": not reasons,
        "status": "runtime_capability_profile_valid" if not reasons else "blocked_invalid_runtime_capability_profile",
        "reasons": tuple(reasons),
        "profile_id": item.profile_id,
        "profile_sha256": item.profile_sha256,
    }
