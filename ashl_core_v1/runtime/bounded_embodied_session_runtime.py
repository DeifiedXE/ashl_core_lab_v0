"""In-memory bounded embodied session runtime for ASHL Core v1."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from ashl_core_v1.host_body.host_body_port_map import (
    HostBodyPortMapRecord,
    build_demo_qingyin_host_body_port_map,
)
from ashl_core_v1.host_body.host_body_sensor_events import (
    build_host_body_camera_event_record,
    build_host_body_event_record,
    build_host_body_sensor_event_audit,
    build_host_body_sensor_event_set_record,
    build_host_body_sensor_event_summary_record,
    validate_host_body_camera_event_record,
    validate_host_body_event_record,
    validate_host_body_sensor_event_audit,
    validate_host_body_sensor_event_set_record,
    validate_host_body_sensor_event_summary_record,
)
from ashl_core_v1.host_body.host_body_runtime_bridge import (
    build_host_body_runtime_bridge_audit,
    build_host_body_runtime_bridge_plan,
    build_host_body_runtime_bridge_trace,
    build_host_body_runtime_dispatch_link,
    build_host_body_runtime_eventframe_bridge,
    map_host_body_event_to_runtime_eventframe,
    validate_host_body_event_to_runtime_frame_mapping,
    validate_host_body_runtime_bridge_audit,
    validate_host_body_runtime_bridge_plan,
    validate_host_body_runtime_bridge_trace,
    validate_host_body_runtime_dispatch_link,
    validate_host_body_runtime_eventframe_bridge,
)
from ashl_core_v1.host_body.host_body_trace_history_lane import (
    build_host_body_trace_history_audit,
    build_host_body_trace_history_entry,
    build_host_body_trace_history_index,
    build_host_body_trace_history_lane,
    build_host_body_trace_history_lane_plan,
    build_host_body_trace_history_readback,
    build_host_body_trace_history_render,
    validate_host_body_trace_history_audit,
    validate_host_body_trace_history_entry,
    validate_host_body_trace_history_index,
    validate_host_body_trace_history_lane,
    validate_host_body_trace_history_lane_plan,
    validate_host_body_trace_history_readback,
    validate_host_body_trace_history_render,
)
from ashl_core_v1.host_body.host_body_internal_action_choice import (
    build_host_body_internal_action_candidate,
    build_host_body_internal_action_choice,
    build_host_body_internal_action_choice_audit,
    build_host_body_internal_action_choice_plan,
    build_host_body_internal_action_choice_set,
    build_host_body_internal_action_result,
    build_host_body_internal_action_surface_effect,
    validate_host_body_internal_action_candidate,
    validate_host_body_internal_action_choice,
    validate_host_body_internal_action_choice_audit,
    validate_host_body_internal_action_choice_plan,
    validate_host_body_internal_action_choice_set,
    validate_host_body_internal_action_result,
    validate_host_body_internal_action_surface_effect,
)
from ashl_core_v1.host_body.host_body_learning_feedback_bridge import (
    build_host_body_learning_bridge_audit,
    build_host_body_learning_bridge_plan,
    build_host_body_learning_evidence_packet,
    build_host_body_learning_feedback_candidate_bridge,
    build_host_body_learning_feedback_candidate_set,
    map_host_body_evidence_to_learning_feedback_candidate,
    validate_host_body_learning_bridge_audit,
    validate_host_body_learning_bridge_plan,
    validate_host_body_learning_evidence_packet,
    validate_host_body_learning_feedback_candidate_bridge,
    validate_host_body_learning_feedback_candidate_mapping,
    validate_host_body_learning_feedback_candidate_set,
)
from ashl_core_v1.host_body.host_body_existing_learning_pipeline_compatibility import (
    build_host_body_existing_learning_pipeline_compatibility_plan,
    build_host_body_feedback_candidate_normalization,
    build_host_body_feedback_existing_review_adapter,
    validate_host_body_existing_learning_pipeline_compatibility_plan,
    validate_host_body_feedback_candidate_normalization,
    validate_host_body_feedback_existing_review_adapter,
)
from ashl_core_v1.host_body.internal_action_home_surface_link import (
    build_internal_action_home_render_snapshot_link,
    build_internal_action_home_status_light_link,
    build_internal_action_home_surface_link_audit,
    build_internal_action_home_surface_link_plan,
    build_internal_action_home_surface_link_trace,
    build_internal_action_home_surface_mapping,
    build_internal_action_home_teacher_observed_link,
    validate_internal_action_home_render_snapshot_link,
    validate_internal_action_home_status_light_link,
    validate_internal_action_home_surface_link_audit,
    validate_internal_action_home_surface_link_plan,
    validate_internal_action_home_surface_link_trace,
    validate_internal_action_home_surface_mapping,
    validate_internal_action_home_teacher_observed_link,
)
from ashl_core_v1.host_body.qingyin_home_internal_space_surface import (
    build_demo_qingyin_home_internal_space_surface,
)
from ashl_core_v1.runtime.runtime_capability_profile import (
    RuntimeCapabilityProfile,
    build_verified_runtime_capability_profile,
    validate_runtime_capability_profile,
)
from ashl_core_v1.runtime.session_learning_evidence_identity import (
    ALLOWED_APPROVAL_SCOPES,
    FULL_COMMIT_APPROVAL_SCOPE,
    build_session_learning_evidence_snapshot,
)
from ashl_core_v1.runtime.trace_envelope import (
    TraceEnvelope,
    TraceEnvelopeStore,
    build_trace_envelope,
    validate_trace_envelope_store,
)


SESSION_STATE_SCHEMA_VERSION = "ashl_bounded_embodied_session_state_v0"
CONFIG_SCHEMA_VERSION = "ashl_bounded_embodied_session_config_v0"
STEP_SCHEMA_VERSION = "ashl_bounded_embodied_session_step_v0"
RUN_RESULT_SCHEMA_VERSION = "ashl_bounded_embodied_session_run_result_v0"
PENDING_REVIEW_SCHEMA_VERSION = "ashl_pending_teacher_review_v0"
AUDIT_SCHEMA_VERSION = "ashl_bounded_embodied_session_runtime_audit_v0"
READINESS_SCHEMA_VERSION = "ashl_bounded_embodied_session_runtime_readiness_v0"

REQUIRED_FUNCTION_BINDINGS = (
    "build_host_body_event_record",
    "build_host_body_camera_event_record",
    "map_host_body_event_to_runtime_eventframe",
    "build_host_body_runtime_eventframe_bridge",
    "build_host_body_trace_history_entry",
    "build_host_body_internal_action_candidate",
    "build_host_body_internal_action_choice",
    "build_host_body_internal_action_result",
    "build_host_body_learning_evidence_packet",
    "map_host_body_evidence_to_learning_feedback_candidate",
    "build_host_body_feedback_candidate_normalization",
    "build_host_body_feedback_existing_review_adapter",
    "build_internal_action_home_surface_mapping",
)

SAFE_CLAIM = (
    "ASHL Core v1 can run one real in-memory bounded embodied session from a "
    "fixture Host Body event through Runtime EventFrame handling, internal-only "
    "Host Body action choice, Qingyin Home read-only surface linkage, and "
    "teacher-reviewable learning evidence creation, using one shared session "
    "state and one canonical append-only TraceEnvelope timeline, then stop at "
    "WAITING_TEACHER_REVIEW."
)

BLOCKED_CLAIMS = (
    "Qingyin can resume after teacher review in Package 115.",
    "Qingyin can create ReviewedConcepts in Package 115.",
    "Qingyin can commit memory in Package 115.",
    "Qingyin can access real sensors.",
    "Qingyin can control the computer.",
    "Qingyin has first_output.",
    "Qingyin has a live scheduler or autonomous runtime.",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _plain(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    if isinstance(value, Enum):
        return value.value
    return value


def _record_id(record: Any, *keys: str) -> str:
    if hasattr(record, "to_dict"):
        data = record.to_dict()
    elif isinstance(record, dict):
        data = record
    else:
        data = getattr(record, "__dict__", {})
    for key in keys:
        value = data.get(key)
        if value:
            return str(value)
    for key, value in data.items():
        if key.endswith("_id") and value:
            return str(value)
    return "unknown_record"


class BoundedEmbodiedSessionStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    WAITING_TEACHER_REVIEW = "waiting_teacher_review"
    PAUSED = "paused"
    RESUMED = "resumed"
    CLOSING = "closing"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    ABORTED = "aborted"
    FAILED = "failed"


class BoundedEmbodiedSessionStage(str, Enum):
    SESSION_CREATED = "session_created"
    HOST_EVENT_ACCEPTED = "host_event_accepted"
    RUNTIME_EVENTFRAME_CREATED = "runtime_eventframe_created"
    RUNTIME_DISPATCH_LINKED = "runtime_dispatch_linked"
    TRACE_HISTORY_UPDATED = "trace_history_updated"
    INTERNAL_ACTION_CANDIDATES_CREATED = "internal_action_candidates_created"
    INTERNAL_ACTION_CHOSEN = "internal_action_chosen"
    INTERNAL_ACTION_RESULT_RECORDED = "internal_action_result_recorded"
    HOME_SURFACE_LINKED = "home_surface_linked"
    LEARNING_EVIDENCE_CREATED = "learning_evidence_created"
    LEARNING_FEEDBACK_CANDIDATE_READY = "learning_feedback_candidate_ready"
    WAITING_TEACHER_REVIEW = "waiting_teacher_review"


ALLOWED_PACKAGE_115_TRANSITIONS = {
    (BoundedEmbodiedSessionStatus.CREATED.value, BoundedEmbodiedSessionStatus.RUNNING.value),
    (BoundedEmbodiedSessionStatus.RUNNING.value, BoundedEmbodiedSessionStatus.WAITING_TEACHER_REVIEW.value),
    (BoundedEmbodiedSessionStatus.RUNNING.value, BoundedEmbodiedSessionStatus.PAUSED.value),
    (BoundedEmbodiedSessionStatus.RUNNING.value, BoundedEmbodiedSessionStatus.ABORTED.value),
    (BoundedEmbodiedSessionStatus.RUNNING.value, BoundedEmbodiedSessionStatus.FAILED.value),
    (BoundedEmbodiedSessionStatus.WAITING_TEACHER_REVIEW.value, BoundedEmbodiedSessionStatus.ABORTED.value),
    (BoundedEmbodiedSessionStatus.WAITING_TEACHER_REVIEW.value, BoundedEmbodiedSessionStatus.FAILED.value),
}


@dataclass(frozen=True)
class BoundedEmbodiedSessionConfig:
    session_kind: str = "bounded_fixture_embodied_session_v0"
    max_runtime_steps: int = 128
    max_event_frames: int = 64
    max_trace_envelopes: int = 512
    max_pending_teacher_reviews: int = 16
    fixture_only: bool = True
    teacher_gate_required: bool = True
    in_memory_only: bool = True
    stop_on_teacher_review: bool = True
    stop_on_boundary_failure: bool = True
    stop_on_runtime_failure: bool = True
    allow_real_hardware: bool = False
    allow_external_control: bool = False
    allow_file_persistence: bool = False
    allow_memory_commit: bool = False
    allow_first_output: bool = False
    allow_live_scheduler: bool = False

    def validate(self) -> dict[str, object]:
        reasons: list[str] = []
        if self.session_kind != "bounded_fixture_embodied_session_v0":
            reasons.append("invalid_session_kind")
        for name, minimum, maximum in (
            ("max_runtime_steps", 1, 1024),
            ("max_event_frames", 0, 512),
            ("max_trace_envelopes", 8, 4096),
            ("max_pending_teacher_reviews", 1, 128),
        ):
            value = int(getattr(self, name))
            if value < minimum or value > maximum:
                reasons.append(f"{name}_out_of_range")
        if not all((self.fixture_only, self.teacher_gate_required, self.in_memory_only)):
            reasons.append("required_safe_flag_false")
        if not all((self.stop_on_teacher_review, self.stop_on_boundary_failure, self.stop_on_runtime_failure)):
            reasons.append("required_stop_flag_false")
        if any(
            (
                self.allow_real_hardware,
                self.allow_external_control,
                self.allow_file_persistence,
                self.allow_memory_commit,
                self.allow_first_output,
                self.allow_live_scheduler,
            )
        ):
            reasons.append("forbidden_authority_allowed")
        return {"valid": not reasons, "status": "config_valid" if not reasons else "config_invalid", "reasons": tuple(reasons)}

    def to_dict(self) -> dict[str, object]:
        data = {field.name: _plain(getattr(self, field.name)) for field in fields(self)}
        data["schema_version"] = CONFIG_SCHEMA_VERSION
        return data


@dataclass(frozen=True)
class BoundedEmbodiedSessionState:
    session_id: str
    schema_version: str
    created_at: str
    updated_at: str
    status: BoundedEmbodiedSessionStatus
    current_stage: BoundedEmbodiedSessionStage
    runtime_step_count: int
    event_frame_count: int
    trace_envelope_count: int
    root_event_id: str | None
    current_event_id: str | None
    event_stack_frame_ids: tuple[str, ...]
    closed_event_frame_ids: tuple[str, ...]
    raw_trace_cursor: int
    working_readback_snapshot_refs: tuple[str, ...]
    pending_teacher_review_ids: tuple[str, ...]
    resolved_teacher_review_ids: tuple[str, ...]
    current_internal_action_choice_id: str | None
    current_internal_action_result_id: str | None
    current_home_surface_link_ids: tuple[str, ...]
    boundary_failure_codes: tuple[str, ...]
    runtime_failure_codes: tuple[str, ...]
    session_summary: str
    runtime_capability_profile_id: str | None = None
    runtime_capability_profile_sha256: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class PendingTeacherReviewRecord:
    pending_teacher_review_id: str
    schema_version: str
    created_at: str
    session_id: str
    source_learning_feedback_candidate_ref: str
    source_learning_evidence_packet_ref: str
    source_trace_refs: tuple[str, ...]
    review_kind: str
    review_status: str
    review_summary: str
    allowed_review_results: tuple[str, ...]
    teacher_decision: str | None
    teacher_reason_codes: tuple[str, ...]
    resolved: bool
    session_aborted: bool = False
    evidence_snapshot_id: str = ""
    evidence_identity_sha256: str = ""
    canonical_payload_sha256: str = ""
    target_session_checkpoint_id: str | None = None
    target_checkpoint_version: int | None = None
    review_nonce: str = ""
    allowed_approval_scopes: tuple[str, ...] = ALLOWED_APPROVAL_SCOPES
    required_commit_scope: str = FULL_COMMIT_APPROVAL_SCOPE

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class BoundedEmbodiedSessionStepRecord:
    session_step_id: str
    schema_version: str
    created_at: str
    session_id: str
    step_index: int
    stage_before: str
    stage_after: str
    status_before: str
    status_after: str
    input_record_refs: tuple[str, ...]
    output_record_refs: tuple[str, ...]
    trace_envelope_ids: tuple[str, ...]
    step_status: str
    step_summary: str
    boundary_failure_codes: tuple[str, ...]
    runtime_failure_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class BoundedEmbodiedSessionRunResult:
    session_id: str
    schema_version: str
    initial_status: str
    final_status: str
    executed_step_count: int
    created_event_frame_count: int
    created_trace_envelope_count: int
    pending_teacher_review_ids: tuple[str, ...]
    selected_internal_action_kinds: tuple[str, ...]
    home_surface_link_ids: tuple[str, ...]
    learning_feedback_candidate_refs: tuple[str, ...]
    stop_reason: str
    run_summary: str
    bounded_limits_preserved: bool
    trace_boundary_preserved: bool

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class BoundedEmbodiedSessionRuntimeAudit:
    session_runtime_audit_id: str
    schema_version: str
    created_at: str
    session_id: str
    session_state_valid: bool
    state_transitions_valid: bool
    actual_function_bindings_confirmed: bool
    event_stack_valid: bool
    event_tree_valid: bool
    trace_envelope_schema_valid: bool
    trace_sequence_monotonic: bool
    trace_source_refs_valid: bool
    trace_session_ids_consistent: bool
    raw_trace_append_only_confirmed: bool
    raw_trace_not_summarized_confirmed: bool
    raw_trace_not_rewritten_confirmed: bool
    concept_id_not_embedded_into_raw_history_confirmed: bool
    host_event_stage_confirmed: bool
    runtime_eventframe_stage_confirmed: bool
    internal_action_stage_confirmed: bool
    home_surface_stage_confirmed: bool
    learning_evidence_stage_confirmed: bool
    pending_teacher_review_stage_confirmed: bool
    session_stopped_at_teacher_gate: bool
    no_teacher_decision_created: bool
    no_reviewed_concept_created: bool
    no_memory_commit: bool
    no_long_term_memory_write: bool
    no_core_memory_write: bool
    no_real_hardware_access: bool
    no_external_control: bool
    no_file_persistence: bool
    no_first_output: bool
    no_live_scheduler: bool
    no_open_ended_loop: bool
    no_thought_engine_behavior: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class BoundedEmbodiedSessionRuntimeReadinessRecord:
    session_runtime_readiness_id: str
    schema_version: str
    created_at: str
    source_session_runtime_audit_id: str
    current_verified_capability: str
    ready_for_teacher_gated_session_resume: bool
    ready_for_teacher_decision_application: bool
    ready_for_reviewed_interpretation_commit: bool
    ready_for_session_end_commit_or_rollback: bool
    ready_for_no_codex_two_cycle_run: bool
    ready_for_real_hardware: bool
    ready_for_external_control: bool
    ready_for_live_scheduler: bool
    ready_for_first_output: bool
    ready_for_open_ended_loop: bool
    recommended_next_package: str
    recommended_next_reason: str
    readiness_status: str

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


class BoundedEmbodiedSessionRuntime:
    def __init__(self, capability_profile: RuntimeCapabilityProfile | None = None) -> None:
        self.capability_profile = capability_profile or build_verified_runtime_capability_profile()
        profile_validation = validate_runtime_capability_profile(self.capability_profile)
        if not profile_validation["valid"]:
            raise ValueError(f"invalid runtime capability profile: {profile_validation['reasons']}")
        self.trace_store = TraceEnvelopeStore()
        self._configs: dict[str, BoundedEmbodiedSessionConfig] = {}
        self._states: dict[str, BoundedEmbodiedSessionState] = {}
        self._records: dict[str, dict[str, Any]] = {}
        self._pending_reviews: dict[str, list[PendingTeacherReviewRecord]] = {}
        self._binding_log: dict[str, list[str]] = {}
        self._transition_failures: dict[str, list[str]] = {}

    def create_session(self, config: BoundedEmbodiedSessionConfig | None = None) -> BoundedEmbodiedSessionState:
        config = config or BoundedEmbodiedSessionConfig()
        validation = config.validate()
        if not validation["valid"]:
            raise ValueError(f"invalid session config: {validation['reasons']}")
        session_id = f"bounded_embodied_session:{uuid4().hex[:12]}"
        created = _now()
        state = BoundedEmbodiedSessionState(
            session_id=session_id,
            schema_version=SESSION_STATE_SCHEMA_VERSION,
            created_at=created,
            updated_at=created,
            status=BoundedEmbodiedSessionStatus.CREATED,
            current_stage=BoundedEmbodiedSessionStage.SESSION_CREATED,
            runtime_step_count=0,
            event_frame_count=0,
            trace_envelope_count=0,
            root_event_id=None,
            current_event_id=None,
            event_stack_frame_ids=tuple(),
            closed_event_frame_ids=tuple(),
            raw_trace_cursor=-1,
            working_readback_snapshot_refs=tuple(),
            pending_teacher_review_ids=tuple(),
            resolved_teacher_review_ids=tuple(),
            current_internal_action_choice_id=None,
            current_internal_action_result_id=None,
            current_home_surface_link_ids=tuple(),
            boundary_failure_codes=tuple(),
            runtime_failure_codes=tuple(),
            session_summary="Bounded embodied session created.",
            runtime_capability_profile_id=self.capability_profile.profile_id,
            runtime_capability_profile_sha256=self.capability_profile.profile_sha256,
        )
        self._configs[session_id] = config
        self._states[session_id] = state
        self._records[session_id] = {"runtime_capability_profile": self.capability_profile}
        self._pending_reviews[session_id] = []
        self._binding_log[session_id] = []
        self._transition_failures[session_id] = []
        envelope = self._append_trace(
            session_id=session_id,
            event_id=f"{session_id}:session_root",
            root_event_id=f"{session_id}:session_root",
            source_line="runtime",
            source_module="bounded_embodied_session_runtime",
            record_kind="BoundedEmbodiedSessionState",
            record_id=session_id,
            trace_layer="runtime_control",
            payload_schema=SESSION_STATE_SCHEMA_VERSION,
            payload_snapshot={"stage": BoundedEmbodiedSessionStage.SESSION_CREATED.value, "status": state.status.value},
        )
        state = replace(state, trace_envelope_count=1, raw_trace_cursor=envelope.sequence_index)
        self._states[session_id] = state
        return state

    def inject_fixture_host_event(self, session_id: str, fixture_kind: str) -> TraceEnvelope:
        state = self._state(session_id)
        port_payload = build_demo_qingyin_host_body_port_map()
        port_map = HostBodyPortMapRecord.from_dict(port_payload["host_body_port_map"])
        camera_port_id = str(port_payload["host_camera_port"]["host_camera_port_id"])
        event_type = "camera_unknown_low_level_event" if fixture_kind in {"camera_unknown_low_level_event", "runtime_bridge_deferred"} else fixture_kind
        event = self._call(
            session_id,
            "build_host_body_event_record",
            build_host_body_event_record,
            source_host_body_port_map_id=port_map.host_body_port_map_id,
            source_port_id=camera_port_id,
            source_port_kind="camera_port",
            event_type=event_type,
            event_payload={"fixture_kind": fixture_kind, "low_level_only": True},
        )
        event_validation = validate_host_body_event_record(event)
        if not event_validation["valid"]:
            raise ValueError(f"invalid HostBodyEvent fixture: {event_validation}")
        camera_event = self._call(
            session_id,
            "build_host_body_camera_event_record",
            build_host_body_camera_event_record,
            host_body_event=event,
            source_camera_port_id=camera_port_id,
            camera_event_type=event_type,
            fixture_frame_id=f"fixture_frame:{session_id}:{fixture_kind}",
            brightness_bucket="unknown",
            motion_proxy_bucket="unknown",
            change_bucket="unknown",
        )
        camera_validation = validate_host_body_camera_event_record(camera_event)
        if not camera_validation["valid"]:
            raise ValueError(f"invalid HostBodyCameraEvent fixture: {camera_validation}")
        self._records[session_id].update(
            {
                "fixture_kind": fixture_kind,
                "port_payload": port_payload,
                "port_map": port_map,
                "host_body_event": event,
                "camera_event": camera_event,
            }
        )
        envelope = self._append_trace(
            session_id=session_id,
            event_id=event.host_body_event_id,
            root_event_id=event.host_body_event_id,
            source_line="host_body",
            source_module="host_body_sensor_events",
            record_kind="HostBodyEventRecord",
            record_id=event.host_body_event_id,
            trace_layer="raw",
            payload_schema=event.schema_version,
            payload_snapshot={
                "event_type": event.event_type,
                "event_family": event.event_family,
                "source_port_kind": event.source_port_kind,
                "event_payload": dict(event.event_payload),
                "fixture_only": event.fixture_only,
                "read_only_event": event.read_only_event,
            },
            source_record_refs=(event.host_body_event_id, camera_event.host_camera_event_id),
        )
        self._records[session_id]["host_event_trace_id"] = envelope.trace_id
        self._update_state(
            session_id,
            current_stage=BoundedEmbodiedSessionStage.HOST_EVENT_ACCEPTED,
            root_event_id=event.host_body_event_id,
            current_event_id=event.host_body_event_id,
            raw_trace_cursor=envelope.sequence_index,
            trace_envelope_count=len(self.trace_store.list_by_session(session_id)),
            session_summary=f"Fixture HostBodyEvent accepted: {fixture_kind}.",
        )
        return envelope

    def step(self, session_id: str) -> BoundedEmbodiedSessionStepRecord:
        state = self._state(session_id)
        config = self._configs[session_id]
        if state.runtime_step_count >= config.max_runtime_steps:
            return self._fail_limit(session_id, "step_limit_reached")
        if len(self.trace_store.list_by_session(session_id)) >= config.max_trace_envelopes:
            return self._fail_limit(session_id, "trace_limit_reached")
        if (
            state.current_stage == BoundedEmbodiedSessionStage.HOST_EVENT_ACCEPTED
            and state.event_frame_count >= config.max_event_frames
        ):
            return self._fail_limit(session_id, "event_frame_limit_reached")
        stage = state.current_stage
        if stage == BoundedEmbodiedSessionStage.HOST_EVENT_ACCEPTED:
            return self._step_runtime_eventframe(session_id)
        if stage == BoundedEmbodiedSessionStage.RUNTIME_EVENTFRAME_CREATED:
            return self._step_runtime_dispatch(session_id)
        if stage == BoundedEmbodiedSessionStage.RUNTIME_DISPATCH_LINKED:
            return self._step_trace_history(session_id)
        if stage == BoundedEmbodiedSessionStage.TRACE_HISTORY_UPDATED:
            return self._step_internal_action_candidates(session_id)
        if stage == BoundedEmbodiedSessionStage.INTERNAL_ACTION_CANDIDATES_CREATED:
            return self._step_internal_action_choice(session_id)
        if stage == BoundedEmbodiedSessionStage.INTERNAL_ACTION_CHOSEN:
            return self._step_internal_action_result(session_id)
        if stage == BoundedEmbodiedSessionStage.INTERNAL_ACTION_RESULT_RECORDED:
            return self._step_home_surface(session_id)
        if stage == BoundedEmbodiedSessionStage.HOME_SURFACE_LINKED:
            return self._step_learning_evidence(session_id)
        if stage == BoundedEmbodiedSessionStage.LEARNING_EVIDENCE_CREATED:
            return self._step_learning_feedback_ready(session_id)
        if stage == BoundedEmbodiedSessionStage.LEARNING_FEEDBACK_CANDIDATE_READY:
            return self._step_waiting_teacher_review(session_id)
        return self._fail_runtime(session_id, "no_runnable_stage")

    def run_until_blocked(self, session_id: str) -> BoundedEmbodiedSessionRunResult:
        initial = self._state(session_id)
        while self._state(session_id).status in {BoundedEmbodiedSessionStatus.CREATED, BoundedEmbodiedSessionStatus.RUNNING}:
            step = self.step(session_id)
            if step.step_status != "session_step_completed":
                break
        final = self._state(session_id)
        records = self._records[session_id]
        stop_reason = {
            BoundedEmbodiedSessionStatus.WAITING_TEACHER_REVIEW: "waiting_teacher_review",
            BoundedEmbodiedSessionStatus.PAUSED: "paused",
            BoundedEmbodiedSessionStatus.ABORTED: "aborted",
            BoundedEmbodiedSessionStatus.FAILED: "runtime_failure",
        }.get(final.status, "runtime_failure")
        return BoundedEmbodiedSessionRunResult(
            session_id=session_id,
            schema_version=RUN_RESULT_SCHEMA_VERSION,
            initial_status=initial.status.value,
            final_status=final.status.value,
            executed_step_count=final.runtime_step_count - initial.runtime_step_count,
            created_event_frame_count=final.event_frame_count - initial.event_frame_count,
            created_trace_envelope_count=len(self.trace_store.list_by_session(session_id)) - initial.trace_envelope_count,
            pending_teacher_review_ids=final.pending_teacher_review_ids,
            selected_internal_action_kinds=tuple(
                item
                for item in (getattr(records.get("internal_action_choice"), "selected_internal_action_kind", None),)
                if item
            ),
            home_surface_link_ids=final.current_home_surface_link_ids,
            learning_feedback_candidate_refs=tuple(
                item
                for item in (
                    getattr(records.get("learning_feedback_mapping"), "target_learning_feedback_candidate_id", None)
                    or getattr(records.get("existing_review_adapter"), "existing_review_adapter_id", None),
                )
                if item
            ),
            stop_reason=stop_reason,
            run_summary=f"Session stopped with status {final.status.value}.",
            bounded_limits_preserved=_limits_preserved(final, self._configs[session_id]),
            trace_boundary_preserved=self.trace_store.validate_monotonic_order() and self.trace_store.validate_source_refs(),
        )

    def pause_session(self, session_id: str, reason: str) -> BoundedEmbodiedSessionState:
        self.transition_session_status(session_id, BoundedEmbodiedSessionStatus.PAUSED)
        self._append_runtime_control(session_id, "SessionPaused", "session_paused", {"reason": reason})
        return self._state(session_id)

    def abort_session(self, session_id: str, reason: str) -> BoundedEmbodiedSessionState:
        state = self._state(session_id)
        if (state.status.value, BoundedEmbodiedSessionStatus.ABORTED.value) not in ALLOWED_PACKAGE_115_TRANSITIONS:
            self.transition_session_status(session_id, BoundedEmbodiedSessionStatus.ABORTED)
            return self._state(session_id)
        updated_reviews = [
            replace(item, review_status="session_aborted_pending_teacher_review", session_aborted=True)
            for item in self._pending_reviews[session_id]
        ]
        self._pending_reviews[session_id] = updated_reviews
        envelope = self._append_runtime_control(
            session_id,
            "SessionAborted",
            f"{session_id}:aborted",
            {"reason": reason, "raw_trace_preserved": True, "pending_reviews_unresolved": True},
        )
        self._update_state(
            session_id,
            status=BoundedEmbodiedSessionStatus.ABORTED,
            current_stage=self._state(session_id).current_stage,
            current_internal_action_choice_id=None,
            current_internal_action_result_id=None,
            current_home_surface_link_ids=tuple(),
            trace_envelope_count=len(self.trace_store.list_by_session(session_id)),
            raw_trace_cursor=envelope.sequence_index,
            session_summary=f"Session aborted without deleting trace: {reason}.",
        )
        return self._state(session_id)

    def get_session_state(self, session_id: str) -> BoundedEmbodiedSessionState:
        return self._state(session_id)

    def get_session_trace(self, session_id: str) -> tuple[TraceEnvelope, ...]:
        return self.trace_store.list_by_session(session_id)

    def get_pending_teacher_reviews(self, session_id: str) -> tuple[PendingTeacherReviewRecord, ...]:
        return tuple(self._pending_reviews[session_id])

    def render_session_summary(self, session_id: str) -> str:
        state = self._state(session_id)
        selected = getattr(self._records[session_id].get("internal_action_choice"), "selected_internal_action_kind", None)
        return "\n".join(
            (
                "Bounded Embodied Session Runtime",
                f"session_id: {session_id}",
                f"status: {state.status.value}",
                f"stage: {state.current_stage.value}",
                f"trace_envelopes: {len(self.get_session_trace(session_id))}",
                f"pending_teacher_reviews: {len(self.get_pending_teacher_reviews(session_id))}",
                f"selected_internal_action_kind: {selected}",
                "memory_commit_performed: false",
                "first_output_created: false",
                "live_scheduler_created: false",
            )
        )

    def transition_session_status(
        self,
        session_id: str,
        target_status: BoundedEmbodiedSessionStatus | str,
    ) -> BoundedEmbodiedSessionStepRecord:
        target = target_status.value if isinstance(target_status, BoundedEmbodiedSessionStatus) else str(target_status)
        before = self._state(session_id)
        if (before.status.value, target) not in ALLOWED_PACKAGE_115_TRANSITIONS:
            self._transition_failures[session_id].append("blocked_invalid_state_transition")
            envelope = self._append_runtime_control(
                session_id,
                "StateTransitionFailure",
                f"{session_id}:transition_failure:{before.runtime_step_count + 1}",
                {"from": before.status.value, "to": target, "blocked": True},
            )
            return self._step_record(
                session_id=session_id,
                before=before,
                after=self._state(session_id),
                input_refs=(before.status.value,),
                output_refs=(target,),
                trace_ids=(envelope.trace_id,),
                status="session_step_failed_boundary",
                summary=f"Blocked unsupported Package 115 transition {before.status.value} -> {target}.",
                boundary_codes=("blocked_invalid_state_transition",),
            )
        self._update_state(session_id, status=BoundedEmbodiedSessionStatus(target))
        return self._step_record(
            session_id=session_id,
            before=before,
            after=self._state(session_id),
            input_refs=(before.status.value,),
            output_refs=(target,),
            trace_ids=tuple(),
            status="session_step_completed",
            summary=f"Transitioned {before.status.value} -> {target}.",
        )

    def _step_runtime_eventframe(self, session_id: str) -> BoundedEmbodiedSessionStepRecord:
        before = self._state(session_id)
        records = self._records[session_id]
        event = records["host_body_event"]
        camera_event = records["camera_event"]
        port_map = records["port_map"]
        event_set = self._call(
            session_id,
            "build_host_body_sensor_event_set_record",
            build_host_body_sensor_event_set_record,
            source_host_body_port_map_id=port_map.host_body_port_map_id,
            host_body_events=(event,),
            camera_events=(camera_event,),
            source_trace_refs=(records["host_event_trace_id"],),
        )
        summary = self._call(
            session_id,
            "build_host_body_sensor_event_summary_record",
            build_host_body_sensor_event_summary_record,
            host_sensor_event_set=event_set,
        )
        sensor_audit = self._call(
            session_id,
            "build_host_body_sensor_event_audit",
            build_host_body_sensor_event_audit,
            host_sensor_event_set=event_set,
            host_sensor_event_summary=summary,
            host_body_port_map=port_map,
            host_body_events=(event,),
            camera_events=(camera_event,),
        )
        _ensure_valid(validate_host_body_sensor_event_set_record(event_set))
        _ensure_valid(validate_host_body_sensor_event_summary_record(summary))
        _ensure_valid(validate_host_body_sensor_event_audit(sensor_audit))
        bridge_plan = self._call(
            session_id,
            "build_host_body_runtime_bridge_plan",
            build_host_body_runtime_bridge_plan,
            host_sensor_event_audit=sensor_audit,
            source_host_body_port_map_id=port_map.host_body_port_map_id,
        )
        mapping = self._call(
            session_id,
            "map_host_body_event_to_runtime_eventframe",
            map_host_body_event_to_runtime_eventframe,
            bridge_plan=bridge_plan,
            host_body_event=event,
        )
        eventframe_bridge, event_frame = self._call(
            session_id,
            "build_host_body_runtime_eventframe_bridge",
            build_host_body_runtime_eventframe_bridge,
            mapping=mapping,
            source_runtime_tick_id=f"{session_id}:tick:0",
        )
        _ensure_valid(validate_host_body_runtime_bridge_plan(bridge_plan))
        _ensure_valid(validate_host_body_event_to_runtime_frame_mapping(mapping))
        _ensure_valid(validate_host_body_runtime_eventframe_bridge(eventframe_bridge))
        records.update(
            {
                "sensor_event_set": event_set,
                "sensor_event_summary": summary,
                "sensor_event_audit": sensor_audit,
                "runtime_bridge_plan": bridge_plan,
                "runtime_mapping": mapping,
                "runtime_eventframe_bridge": eventframe_bridge,
                "runtime_event_frame": event_frame,
            }
        )
        envelope = self._append_derived(
            session_id=session_id,
            event_id=event.host_body_event_id,
            record_kind="HostBodyRuntimeEventFrameBridgeRecord",
            record=eventframe_bridge,
            source_module="host_body_runtime_bridge",
            payload_schema=eventframe_bridge.schema_version,
            payload_snapshot={
                "runtime_eventframe_created": eventframe_bridge.runtime_eventframe_created,
                "runtime_event_frame_id": eventframe_bridge.source_runtime_event_frame_id,
                "target_engine_lane": eventframe_bridge.target_engine_lane,
            },
            source_trace_refs=(records["host_event_trace_id"],),
        )
        self._update_state(
            session_id,
            status=BoundedEmbodiedSessionStatus.RUNNING,
            current_stage=BoundedEmbodiedSessionStage.RUNTIME_EVENTFRAME_CREATED,
            event_frame_count=before.event_frame_count + 1,
            event_stack_frame_ids=(eventframe_bridge.source_runtime_event_frame_id,),
            trace_envelope_count=len(self.trace_store.list_by_session(session_id)),
            raw_trace_cursor=envelope.sequence_index,
            session_summary="Runtime EventFrame bridge created.",
        )
        return self._completed_step(before, self._state(session_id), (event.host_body_event_id,), (eventframe_bridge.host_runtime_eventframe_bridge_id,), (envelope.trace_id,))

    def _step_runtime_dispatch(self, session_id: str) -> BoundedEmbodiedSessionStepRecord:
        before = self._state(session_id)
        records = self._records[session_id]
        defer_dispatch = records.get("fixture_kind") == "runtime_bridge_deferred"
        dispatch_link = self._call(
            session_id,
            "build_host_body_runtime_dispatch_link",
            build_host_body_runtime_dispatch_link,
            eventframe_bridge=records["runtime_eventframe_bridge"],
            defer_dispatch_adapter=defer_dispatch,
        )
        runtime_trace = self._call(
            session_id,
            "build_host_body_runtime_bridge_trace",
            build_host_body_runtime_bridge_trace,
            bridge_plan=records["runtime_bridge_plan"],
            host_body_events=(records["host_body_event"],),
            event_mappings=(records["runtime_mapping"],),
            eventframe_bridges=(records["runtime_eventframe_bridge"],),
            dispatch_links=(dispatch_link,),
        )
        runtime_audit = self._call(
            session_id,
            "build_host_body_runtime_bridge_audit",
            build_host_body_runtime_bridge_audit,
            host_sensor_event_audit=records["sensor_event_audit"],
            bridge_plan=records["runtime_bridge_plan"],
            bridge_trace=runtime_trace,
            event_mappings=(records["runtime_mapping"],),
            eventframe_bridges=(records["runtime_eventframe_bridge"],),
            dispatch_links=(dispatch_link,),
        )
        _ensure_valid(validate_host_body_runtime_dispatch_link(dispatch_link), allow_status="dispatch_link_deferred_missing_dispatch_adapter")
        _ensure_valid(validate_host_body_runtime_bridge_trace(runtime_trace))
        _ensure_valid(validate_host_body_runtime_bridge_audit(runtime_audit))
        records.update({"runtime_dispatch_link": dispatch_link, "runtime_bridge_trace": runtime_trace, "runtime_bridge_audit": runtime_audit})
        envelope = self._append_derived(
            session_id=session_id,
            event_id=records["host_body_event"].host_body_event_id,
            record_kind="HostBodyRuntimeDispatchLinkRecord",
            record=dispatch_link,
            source_module="host_body_runtime_bridge",
            payload_schema=dispatch_link.schema_version,
            payload_snapshot={"dispatch_link_status": dispatch_link.dispatch_link_status, "deferred": defer_dispatch},
            source_trace_refs=(self._latest_trace_id(session_id),),
        )
        self._update_state(
            session_id,
            current_stage=BoundedEmbodiedSessionStage.RUNTIME_DISPATCH_LINKED,
            trace_envelope_count=len(self.trace_store.list_by_session(session_id)),
            raw_trace_cursor=envelope.sequence_index,
            session_summary="Runtime dispatch adapter linked.",
        )
        return self._completed_step(before, self._state(session_id), (records["runtime_eventframe_bridge"].host_runtime_eventframe_bridge_id,), (dispatch_link.host_runtime_dispatch_link_id,), (envelope.trace_id,))

    def _step_trace_history(self, session_id: str) -> BoundedEmbodiedSessionStepRecord:
        before = self._state(session_id)
        records = self._records[session_id]
        home_payload = build_demo_qingyin_home_internal_space_surface()
        home_audit = home_payload["home_internal_space_surface_audit"]
        records["home_payload"] = home_payload
        records["home_audit"] = home_audit
        plan = self._call(
            session_id,
            "build_host_body_trace_history_lane_plan",
            build_host_body_trace_history_lane_plan,
            host_body_port_map=records["port_map"],
            home_surface_audit=home_audit,
            host_runtime_bridge_audit=records["runtime_bridge_audit"],
        )
        entry_event = self._call(
            session_id,
            "build_host_body_trace_history_entry",
            build_host_body_trace_history_entry,
            lane_plan=plan,
            sequence_index=0,
            source_record=records["host_body_event"],
            entry_payload={"session_id": session_id, "runtime_fixture": records["fixture_kind"]},
        )
        entry_bridge = self._call(
            session_id,
            "build_host_body_trace_history_entry",
            build_host_body_trace_history_entry,
            lane_plan=plan,
            sequence_index=1,
            source_record=records["runtime_bridge_trace"],
        )
        lane = self._call(session_id, "build_host_body_trace_history_lane", build_host_body_trace_history_lane, lane_plan=plan, entries=(entry_event, entry_bridge))
        index = self._call(session_id, "build_host_body_trace_history_index", build_host_body_trace_history_index, lane=lane, entries=(entry_event, entry_bridge))
        readback = self._call(session_id, "build_host_body_trace_history_readback", build_host_body_trace_history_readback, lane=lane, entries=(entry_event, entry_bridge), index=index)
        render = self._call(session_id, "build_host_body_trace_history_render", build_host_body_trace_history_render, lane=lane, entries=(entry_event, entry_bridge), readback=readback)
        audit = self._call(session_id, "build_host_body_trace_history_audit", build_host_body_trace_history_audit, lane_plan=plan, entries=(entry_event, entry_bridge), lane=lane, index=index, readback=readback, render=render)
        for validation in (
            validate_host_body_trace_history_lane_plan(plan),
            validate_host_body_trace_history_entry(entry_event),
            validate_host_body_trace_history_entry(entry_bridge),
            validate_host_body_trace_history_lane(lane),
            validate_host_body_trace_history_index(index),
            validate_host_body_trace_history_readback(readback),
            validate_host_body_trace_history_render(render),
            validate_host_body_trace_history_audit(audit),
        ):
            _ensure_valid(validation)
        records.update({"trace_history_plan": plan, "trace_history_entries": (entry_event, entry_bridge), "trace_history_lane": lane, "trace_history_index": index, "trace_history_readback": readback, "trace_history_render": render, "trace_history_audit": audit})
        envelope = self._append_derived(
            session_id=session_id,
            event_id=records["host_body_event"].host_body_event_id,
            record_kind="HostBodyTraceHistoryLaneRecord",
            record=lane,
            source_module="host_body_trace_history_lane",
            payload_schema=lane.schema_version,
            payload_snapshot={"entry_count": lane.entry_count, "trace_history_entry_ids": list(lane.trace_history_entry_ids)},
            source_trace_refs=(records["host_event_trace_id"], self._latest_trace_id(session_id)),
        )
        self._update_state(
            session_id,
            current_stage=BoundedEmbodiedSessionStage.TRACE_HISTORY_UPDATED,
            working_readback_snapshot_refs=(readback.trace_history_readback_id,),
            trace_envelope_count=len(self.trace_store.list_by_session(session_id)),
            raw_trace_cursor=envelope.sequence_index,
            session_summary="Host Body trace history lane updated.",
        )
        return self._completed_step(before, self._state(session_id), (records["host_body_event"].host_body_event_id,), (lane.trace_history_lane_id, readback.trace_history_readback_id), (envelope.trace_id,))

    def _step_internal_action_candidates(self, session_id: str) -> BoundedEmbodiedSessionStepRecord:
        before = self._state(session_id)
        records = self._records[session_id]
        plan = self._call(session_id, "build_host_body_internal_action_choice_plan", build_host_body_internal_action_choice_plan, trace_history_audit=records["trace_history_audit"], trace_history_readback=records["trace_history_readback"], home_surface_audit=records["home_audit"])
        candidate_kwargs: dict[str, object] = {"choice_plan": plan, "trace_history_readback": records["trace_history_readback"]}
        if records.get("fixture_kind") == "runtime_bridge_deferred":
            candidate_kwargs["runtime_bridge_trace"] = records["runtime_bridge_trace"]
        else:
            candidate_kwargs["trace_history_entry"] = records["trace_history_entries"][0]
        candidate = self._call(session_id, "build_host_body_internal_action_candidate", build_host_body_internal_action_candidate, **candidate_kwargs)
        _ensure_valid(validate_host_body_internal_action_choice_plan(plan))
        _ensure_valid(validate_host_body_internal_action_candidate(candidate))
        records.update({"internal_action_choice_plan": plan, "internal_action_candidates": (candidate,)})
        envelope = self._append_derived(
            session_id=session_id,
            event_id=records["host_body_event"].host_body_event_id,
            record_kind="HostBodyInternalActionCandidateRecord",
            record=candidate,
            source_module="host_body_internal_action_choice",
            payload_schema=candidate.schema_version,
            payload_snapshot={"candidate_action_kind": candidate.candidate_action_kind, "candidate_priority": candidate.candidate_priority},
            source_trace_refs=(self._latest_trace_id(session_id),),
        )
        self._update_state(session_id, current_stage=BoundedEmbodiedSessionStage.INTERNAL_ACTION_CANDIDATES_CREATED, trace_envelope_count=len(self.trace_store.list_by_session(session_id)), raw_trace_cursor=envelope.sequence_index, session_summary="Internal action candidates created.")
        return self._completed_step(before, self._state(session_id), (records["trace_history_readback"].trace_history_readback_id,), (candidate.internal_action_candidate_id,), (envelope.trace_id,))

    def _step_internal_action_choice(self, session_id: str) -> BoundedEmbodiedSessionStepRecord:
        before = self._state(session_id)
        records = self._records[session_id]
        choice = self._call(session_id, "build_host_body_internal_action_choice", build_host_body_internal_action_choice, choice_plan=records["internal_action_choice_plan"], candidates=records["internal_action_candidates"])
        _ensure_valid(validate_host_body_internal_action_choice(choice))
        records["internal_action_choice"] = choice
        envelope = self._append_derived(session_id=session_id, event_id=records["host_body_event"].host_body_event_id, record_kind="HostBodyInternalActionChoiceRecord", record=choice, source_module="host_body_internal_action_choice", payload_schema=choice.schema_version, payload_snapshot={"selected_internal_action_kind": choice.selected_internal_action_kind}, source_trace_refs=(self._latest_trace_id(session_id),))
        self._update_state(session_id, current_stage=BoundedEmbodiedSessionStage.INTERNAL_ACTION_CHOSEN, current_internal_action_choice_id=choice.internal_action_choice_id, trace_envelope_count=len(self.trace_store.list_by_session(session_id)), raw_trace_cursor=envelope.sequence_index, session_summary=f"Internal action chosen: {choice.selected_internal_action_kind}.")
        return self._completed_step(before, self._state(session_id), tuple(item.internal_action_candidate_id for item in records["internal_action_candidates"]), (choice.internal_action_choice_id,), (envelope.trace_id,))

    def _step_internal_action_result(self, session_id: str) -> BoundedEmbodiedSessionStepRecord:
        before = self._state(session_id)
        records = self._records[session_id]
        result = self._call(session_id, "build_host_body_internal_action_result", build_host_body_internal_action_result, internal_action_choice=records["internal_action_choice"])
        effect = self._call(session_id, "build_host_body_internal_action_surface_effect", build_host_body_internal_action_surface_effect, internal_action_result=result)
        choice_set = self._call(session_id, "build_host_body_internal_action_choice_set", build_host_body_internal_action_choice_set, choice_plan=records["internal_action_choice_plan"], candidates=records["internal_action_candidates"], choices=(records["internal_action_choice"],), results=(result,), surface_effects=(effect,))
        audit = self._call(session_id, "build_host_body_internal_action_choice_audit", build_host_body_internal_action_choice_audit, choice_plan=records["internal_action_choice_plan"], candidates=records["internal_action_candidates"], choices=(records["internal_action_choice"],), results=(result,), surface_effects=(effect,), choice_set=choice_set)
        for validation in (
            validate_host_body_internal_action_result(result),
            validate_host_body_internal_action_surface_effect(effect),
            validate_host_body_internal_action_choice_set(choice_set),
            validate_host_body_internal_action_choice_audit(audit),
        ):
            _ensure_valid(validation)
        records.update({"internal_action_result": result, "internal_action_surface_effect": effect, "internal_action_choice_set": choice_set, "internal_action_choice_audit": audit})
        envelope = self._append_derived(session_id=session_id, event_id=records["host_body_event"].host_body_event_id, record_kind="HostBodyInternalActionResultRecord", record=result, source_module="host_body_internal_action_choice", payload_schema=result.schema_version, payload_snapshot={"selected_internal_action_kind": result.selected_internal_action_kind, "result_status": result.result_status}, source_trace_refs=(self._latest_trace_id(session_id),))
        self._update_state(session_id, current_stage=BoundedEmbodiedSessionStage.INTERNAL_ACTION_RESULT_RECORDED, current_internal_action_result_id=result.internal_action_result_id, trace_envelope_count=len(self.trace_store.list_by_session(session_id)), raw_trace_cursor=envelope.sequence_index, session_summary="Internal action result recorded.")
        return self._completed_step(before, self._state(session_id), (records["internal_action_choice"].internal_action_choice_id,), (result.internal_action_result_id,), (envelope.trace_id,))

    def _step_home_surface(self, session_id: str) -> BoundedEmbodiedSessionStepRecord:
        before = self._state(session_id)
        records = self._records[session_id]
        closed_loop_audit = self.capability_profile.record("closed_loop_milestone_audit")
        trace_spine_boundary = self.capability_profile.record("trace_spine_raw_evidence_boundary")
        plan = self._call(session_id, "build_internal_action_home_surface_link_plan", build_internal_action_home_surface_link_plan, closed_loop_milestone_audit=closed_loop_audit, home_surface_audit=records["home_audit"], trace_spine_boundary=trace_spine_boundary)
        result = records["internal_action_result"]
        mapping = self._call(session_id, "build_internal_action_home_surface_mapping", build_internal_action_home_surface_mapping, home_surface_link_plan=plan, selected_internal_action_kind=result.selected_internal_action_kind or "shift_internal_focus", source_internal_action_result_id=result.internal_action_result_id, source_readback_influenced_result_id=None, readback_reason_refs=result.source_trace_refs, source_trace_refs=(self._latest_trace_id(session_id),))
        status_light = self._call(session_id, "build_internal_action_home_status_light_link", build_internal_action_home_status_light_link, home_surface_mapping=mapping)
        teacher_observed = self._call(session_id, "build_internal_action_home_teacher_observed_link", build_internal_action_home_teacher_observed_link, home_surface_mapping=mapping)
        render = self._call(session_id, "build_internal_action_home_render_snapshot_link", build_internal_action_home_render_snapshot_link, home_surface_mapping=mapping)
        trace = self._call(session_id, "build_internal_action_home_surface_link_trace", build_internal_action_home_surface_link_trace, home_surface_link_plan=plan, mappings=(mapping,), status_light_links=(status_light,), teacher_observed_links=(teacher_observed,), render_snapshot_links=(render,))
        audit = self._call(session_id, "build_internal_action_home_surface_link_audit", build_internal_action_home_surface_link_audit, home_surface_link_plan=plan, home_surface_link_trace=trace, closed_loop_milestone_audit=closed_loop_audit, trace_spine_boundary=trace_spine_boundary)
        for validation in (
            validate_internal_action_home_surface_link_plan(plan),
            validate_internal_action_home_surface_mapping(mapping),
            validate_internal_action_home_status_light_link(status_light),
            validate_internal_action_home_teacher_observed_link(teacher_observed),
            validate_internal_action_home_render_snapshot_link(render),
            validate_internal_action_home_surface_link_trace(trace),
            validate_internal_action_home_surface_link_audit(audit),
        ):
            _ensure_valid(validation)
        records.update({"home_surface_link_plan": plan, "home_surface_mapping": mapping, "home_status_light_link": status_light, "home_teacher_observed_link": teacher_observed, "home_render_snapshot_link": render, "home_surface_link_trace": trace, "home_surface_link_audit": audit})
        output_ids = (mapping.home_surface_mapping_id, status_light.home_status_light_link_id, teacher_observed.home_teacher_observed_link_id, render.home_render_snapshot_link_id)
        envelope = self._append_derived(session_id=session_id, event_id=records["host_body_event"].host_body_event_id, record_kind="InternalActionHomeSurfaceLinkTraceRecord", record=trace, source_module="internal_action_home_surface_link", payload_schema=trace.schema_version, payload_snapshot={"mapping_count": trace.mapping_count, "read_only_surface_links_confirmed": trace.read_only_surface_links_confirmed}, source_trace_refs=(self._latest_trace_id(session_id),))
        self._update_state(session_id, current_stage=BoundedEmbodiedSessionStage.HOME_SURFACE_LINKED, current_home_surface_link_ids=output_ids, trace_envelope_count=len(self.trace_store.list_by_session(session_id)), raw_trace_cursor=envelope.sequence_index, session_summary="Qingyin Home read-only surface links created.")
        return self._completed_step(before, self._state(session_id), (result.internal_action_result_id,), output_ids, (envelope.trace_id,))

    def _step_learning_evidence(self, session_id: str) -> BoundedEmbodiedSessionStepRecord:
        before = self._state(session_id)
        records = self._records[session_id]
        host_body_v0_audit = self.capability_profile.record("host_body_v0_audit")
        plan = self._call(
            session_id,
            "build_host_body_learning_bridge_plan",
            build_host_body_learning_bridge_plan,
            host_body_v0_audit=host_body_v0_audit,
            trace_history_audit=records["trace_history_audit"].to_dict(),
            internal_action_choice_audit=records["internal_action_choice_audit"].to_dict(),
        )
        packet = self._call(session_id, "build_host_body_learning_evidence_packet", build_host_body_learning_evidence_packet, bridge_plan=plan, trace_history_readback=records["trace_history_readback"].to_dict(), internal_action_choice=records["internal_action_choice"].to_dict(), internal_action_result=records["internal_action_result"].to_dict(), runtime_bridge_trace=records["runtime_bridge_trace"].to_dict())
        mapping = self._call(session_id, "map_host_body_evidence_to_learning_feedback_candidate", map_host_body_evidence_to_learning_feedback_candidate, evidence_packet=packet)
        bridge = self._call(session_id, "build_host_body_learning_feedback_candidate_bridge", build_host_body_learning_feedback_candidate_bridge, bridge_plan=plan, evidence_packet=packet, mapping=mapping)
        candidate_set = self._call(session_id, "build_host_body_learning_feedback_candidate_set", build_host_body_learning_feedback_candidate_set, bridge_plan=plan, evidence_packets=(packet,), mappings=(mapping,), bridges=(bridge,))
        audit = self._call(session_id, "build_host_body_learning_bridge_audit", build_host_body_learning_bridge_audit, bridge_plan=plan, evidence_packets=(packet,), mappings=(mapping,), bridges=(bridge,), candidate_set=candidate_set)
        for validation in (
            validate_host_body_learning_bridge_plan(plan),
            validate_host_body_learning_evidence_packet(packet),
            validate_host_body_learning_feedback_candidate_mapping(mapping),
            validate_host_body_learning_feedback_candidate_bridge(bridge),
            validate_host_body_learning_feedback_candidate_set(candidate_set),
            validate_host_body_learning_bridge_audit(audit),
        ):
            _ensure_valid(validation)
        records.update({"learning_bridge_plan": plan, "learning_evidence_packet": packet, "learning_feedback_mapping": mapping, "learning_feedback_bridge": bridge, "learning_feedback_candidate_set": candidate_set, "learning_bridge_audit": audit})
        envelope = self._append_derived(session_id=session_id, event_id=records["host_body_event"].host_body_event_id, record_kind="HostBodyLearningEvidencePacketRecord", record=packet, source_module="host_body_learning_feedback_bridge", payload_schema=packet.schema_version, payload_snapshot={"evidence_theme": packet.evidence_theme, "teacher_review_required": packet.teacher_review_required}, source_trace_refs=(self._latest_trace_id(session_id),))
        self._update_state(session_id, current_stage=BoundedEmbodiedSessionStage.LEARNING_EVIDENCE_CREATED, trace_envelope_count=len(self.trace_store.list_by_session(session_id)), raw_trace_cursor=envelope.sequence_index, session_summary="Teacher-reviewable Host Body learning evidence created.")
        return self._completed_step(before, self._state(session_id), (records["internal_action_result"].internal_action_result_id,), (packet.host_body_learning_evidence_packet_id, bridge.host_body_learning_feedback_bridge_id), (envelope.trace_id,))

    def _step_learning_feedback_ready(self, session_id: str) -> BoundedEmbodiedSessionStepRecord:
        before = self._state(session_id)
        records = self._records[session_id]
        plan = self._call(session_id, "build_host_body_existing_learning_pipeline_compatibility_plan", build_host_body_existing_learning_pipeline_compatibility_plan, host_body_learning_bridge_audit=records["learning_bridge_audit"], host_body_learning_candidate_set=records["learning_feedback_candidate_set"])
        normalization = self._call(session_id, "build_host_body_feedback_candidate_normalization", build_host_body_feedback_candidate_normalization, compatibility_plan=plan, evidence_packet=records["learning_evidence_packet"].to_dict(), mapping=records["learning_feedback_mapping"].to_dict(), bridge=records["learning_feedback_bridge"].to_dict())
        adapter = self._call(session_id, "build_host_body_feedback_existing_review_adapter", build_host_body_feedback_existing_review_adapter, normalization=normalization)
        for validation in (
            validate_host_body_existing_learning_pipeline_compatibility_plan(plan),
            validate_host_body_feedback_candidate_normalization(normalization),
            validate_host_body_feedback_existing_review_adapter(adapter),
        ):
            _ensure_valid(validation)
        records.update({"existing_learning_compatibility_plan": plan, "feedback_normalization": normalization, "existing_review_adapter": adapter})
        envelope = self._append_derived(session_id=session_id, event_id=records["host_body_event"].host_body_event_id, record_kind="HostBodyFeedbackExistingReviewAdapterRecord", record=adapter, source_module="host_body_existing_learning_pipeline_compatibility", payload_schema=adapter.schema_version, payload_snapshot={"existing_review_pipeline_target": adapter.existing_review_pipeline_target, "teacher_review_required": adapter.teacher_review_required}, source_trace_refs=(self._latest_trace_id(session_id),))
        self._update_state(session_id, current_stage=BoundedEmbodiedSessionStage.LEARNING_FEEDBACK_CANDIDATE_READY, trace_envelope_count=len(self.trace_store.list_by_session(session_id)), raw_trace_cursor=envelope.sequence_index, session_summary="LearningFeedbackCandidate-compatible review input ready.")
        return self._completed_step(before, self._state(session_id), (records["learning_feedback_bridge"].host_body_learning_feedback_bridge_id,), (adapter.existing_review_adapter_id,), (envelope.trace_id,))

    def _step_waiting_teacher_review(self, session_id: str) -> BoundedEmbodiedSessionStepRecord:
        before = self._state(session_id)
        records = self._records[session_id]
        packet = records["learning_evidence_packet"]
        adapter = records["existing_review_adapter"]
        snapshot = build_session_learning_evidence_snapshot(
            session_id=session_id,
            root_event_id=self._state(session_id).root_event_id or records["host_body_event"].host_body_event_id,
            source_event_id=records["host_body_event"].host_body_event_id,
            evidence_packet=packet,
            mapping=records["learning_feedback_mapping"],
            bridge=records["learning_feedback_bridge"],
            existing_review_adapter=adapter,
            source_trace_refs=(self._latest_trace_id(session_id),),
        )
        records["session_learning_evidence_snapshot"] = snapshot
        review = PendingTeacherReviewRecord(
            pending_teacher_review_id=f"pending_teacher_review:{session_id}:{len(self._pending_reviews[session_id]) + 1}",
            schema_version=PENDING_REVIEW_SCHEMA_VERSION,
            created_at=_now(),
            session_id=session_id,
            source_learning_feedback_candidate_ref=adapter.existing_review_adapter_id,
            source_learning_evidence_packet_ref=packet.host_body_learning_evidence_packet_id,
            source_trace_refs=(self._latest_trace_id(session_id),),
            review_kind="existing_learning_feedback_candidate_review",
            review_status="pending_teacher_review",
            review_summary="Package 115 stops here and waits for an explicit teacher review.",
            allowed_review_results=("approved", "rejected", "deferred", "needs_more_evidence", "conflict_detected"),
            teacher_decision=None,
            teacher_reason_codes=tuple(),
            resolved=False,
            evidence_snapshot_id=snapshot.evidence_snapshot_id,
            evidence_identity_sha256=snapshot.evidence_identity_sha256,
            canonical_payload_sha256=snapshot.canonical_payload_sha256,
            target_session_checkpoint_id=None,
            target_checkpoint_version=None,
            review_nonce=f"review_nonce:{uuid4().hex[:16]}",
            allowed_approval_scopes=ALLOWED_APPROVAL_SCOPES,
            required_commit_scope=FULL_COMMIT_APPROVAL_SCOPE,
        )
        if len(self._pending_reviews[session_id]) >= self._configs[session_id].max_pending_teacher_reviews:
            return self._fail_limit(session_id, "pending_review_limit_reached")
        self._pending_reviews[session_id].append(review)
        envelope = self._append_trace(
            session_id=session_id,
            event_id=records["host_body_event"].host_body_event_id,
            root_event_id=records["host_body_event"].host_body_event_id,
            source_line="teacher_interface",
            source_module="bounded_embodied_session_runtime",
            record_kind="PendingTeacherReviewRecord",
            record_id=review.pending_teacher_review_id,
            trace_layer="runtime_control",
            payload_schema=PENDING_REVIEW_SCHEMA_VERSION,
            payload_snapshot={
                "review_status": review.review_status,
                "resolved": review.resolved,
                "teacher_decision": review.teacher_decision,
                "evidence_snapshot_id": review.evidence_snapshot_id,
                "evidence_identity_sha256": review.evidence_identity_sha256,
                "required_commit_scope": review.required_commit_scope,
            },
            source_trace_refs=(self._latest_trace_id(session_id),),
            source_record_refs=(review.pending_teacher_review_id, adapter.existing_review_adapter_id),
        )
        self._update_state(
            session_id,
            status=BoundedEmbodiedSessionStatus.WAITING_TEACHER_REVIEW,
            current_stage=BoundedEmbodiedSessionStage.WAITING_TEACHER_REVIEW,
            pending_teacher_review_ids=tuple(item.pending_teacher_review_id for item in self._pending_reviews[session_id]),
            trace_envelope_count=len(self.trace_store.list_by_session(session_id)),
            raw_trace_cursor=envelope.sequence_index,
            session_summary="Session stopped at WAITING_TEACHER_REVIEW.",
        )
        return self._step_record(session_id=session_id, before=before, after=self._state(session_id), input_refs=(adapter.existing_review_adapter_id,), output_refs=(review.pending_teacher_review_id,), trace_ids=(envelope.trace_id,), status="session_step_blocked_teacher_review", summary="Session blocked at teacher-review gate.")

    def _append_trace(self, *, session_id: str, event_id: str, root_event_id: str, source_line: str, source_module: str, record_kind: str, record_id: str, trace_layer: str, payload_schema: str, payload_snapshot: dict[str, Any], source_trace_refs: tuple[str, ...] = tuple(), source_record_refs: tuple[str, ...] = tuple()) -> TraceEnvelope:
        envelope = build_trace_envelope(
            trace_id=f"trace:{session_id}:{len(self.trace_store.list_by_session(session_id)):04d}:{record_kind}",
            session_id=session_id,
            event_id=event_id,
            parent_event_id=None,
            root_event_id=root_event_id,
            source_line=source_line,
            source_module=source_module,
            record_kind=record_kind,
            record_id=record_id,
            trace_layer=trace_layer,
            payload_schema=payload_schema,
            payload_snapshot=payload_snapshot,
            source_trace_refs=source_trace_refs,
            source_record_refs=source_record_refs,
        )
        return self.trace_store.append(envelope)

    def _append_derived(self, *, session_id: str, event_id: str, record_kind: str, record: Any, source_module: str, payload_schema: str, payload_snapshot: dict[str, Any], source_trace_refs: tuple[str, ...]) -> TraceEnvelope:
        return self._append_trace(
            session_id=session_id,
            event_id=event_id,
            root_event_id=self._state(session_id).root_event_id or event_id,
            source_line="host_body",
            source_module=source_module,
            record_kind=record_kind,
            record_id=_record_id(record),
            trace_layer="derived_evidence",
            payload_schema=payload_schema,
            payload_snapshot=payload_snapshot,
            source_trace_refs=tuple(dict.fromkeys(source_trace_refs)),
            source_record_refs=(_record_id(record),),
        )

    def _append_runtime_control(self, session_id: str, record_kind: str, record_id: str, payload: dict[str, Any]) -> TraceEnvelope:
        state = self._state(session_id)
        refs = (self._latest_trace_id(session_id),) if self.trace_store.list_by_session(session_id) else tuple()
        return self._append_trace(
            session_id=session_id,
            event_id=state.current_event_id or f"{session_id}:session_root",
            root_event_id=state.root_event_id or f"{session_id}:session_root",
            source_line="runtime",
            source_module="bounded_embodied_session_runtime",
            record_kind=record_kind,
            record_id=record_id,
            trace_layer="runtime_control",
            payload_schema="ashl_runtime_control_v0",
            payload_snapshot=payload,
            source_trace_refs=refs,
            source_record_refs=(record_id,),
        )

    def _completed_step(self, before: BoundedEmbodiedSessionState, after: BoundedEmbodiedSessionState, input_refs: tuple[str, ...], output_refs: tuple[str, ...], trace_ids: tuple[str, ...]) -> BoundedEmbodiedSessionStepRecord:
        self._increment_step(after.session_id)
        after = self._state(after.session_id)
        return self._step_record(
            session_id=after.session_id,
            before=before,
            after=after,
            input_refs=input_refs,
            output_refs=output_refs,
            trace_ids=trace_ids,
            status="session_step_completed",
            summary=f"{before.current_stage.value} -> {after.current_stage.value}",
        )

    def _step_record(self, *, session_id: str, before: BoundedEmbodiedSessionState, after: BoundedEmbodiedSessionState, input_refs: tuple[str, ...], output_refs: tuple[str, ...], trace_ids: tuple[str, ...], status: str, summary: str, boundary_codes: tuple[str, ...] = tuple(), runtime_codes: tuple[str, ...] = tuple()) -> BoundedEmbodiedSessionStepRecord:
        return BoundedEmbodiedSessionStepRecord(
            session_step_id=f"bounded_session_step:{session_id}:{before.runtime_step_count + 1}:{status}",
            schema_version=STEP_SCHEMA_VERSION,
            created_at=_now(),
            session_id=session_id,
            step_index=before.runtime_step_count + 1,
            stage_before=before.current_stage.value,
            stage_after=after.current_stage.value,
            status_before=before.status.value,
            status_after=after.status.value,
            input_record_refs=input_refs,
            output_record_refs=output_refs,
            trace_envelope_ids=trace_ids,
            step_status=status,
            step_summary=summary,
            boundary_failure_codes=boundary_codes,
            runtime_failure_codes=runtime_codes,
        )

    def _fail_limit(self, session_id: str, code: str) -> BoundedEmbodiedSessionStepRecord:
        before = self._state(session_id)
        envelope = self._append_runtime_control(session_id, "SessionLimitFailure", f"{session_id}:limit:{code}", {"failure_code": code})
        self._update_state(session_id, status=BoundedEmbodiedSessionStatus.FAILED, boundary_failure_codes=before.boundary_failure_codes + (code,), trace_envelope_count=len(self.trace_store.list_by_session(session_id)))
        return self._step_record(session_id=session_id, before=before, after=self._state(session_id), input_refs=tuple(), output_refs=(code,), trace_ids=(envelope.trace_id,), status="session_step_failed_limit", summary=f"Session limit reached: {code}.", boundary_codes=(code,))

    def _fail_runtime(self, session_id: str, code: str) -> BoundedEmbodiedSessionStepRecord:
        before = self._state(session_id)
        envelope = self._append_runtime_control(session_id, "SessionRuntimeFailure", f"{session_id}:runtime:{code}", {"failure_code": code})
        self._update_state(session_id, status=BoundedEmbodiedSessionStatus.FAILED, runtime_failure_codes=before.runtime_failure_codes + (code,), trace_envelope_count=len(self.trace_store.list_by_session(session_id)))
        return self._step_record(session_id=session_id, before=before, after=self._state(session_id), input_refs=tuple(), output_refs=(code,), trace_ids=(envelope.trace_id,), status="session_step_failed_runtime", summary=f"Session runtime failure: {code}.", runtime_codes=(code,))

    def _call(self, session_id: str, name: str, func: Any, **kwargs: Any) -> Any:
        self._binding_log[session_id].append(name)
        return func(**kwargs)

    def _state(self, session_id: str) -> BoundedEmbodiedSessionState:
        if session_id not in self._states:
            raise KeyError(f"unknown session_id: {session_id}")
        return self._states[session_id]

    def _update_state(self, session_id: str, **changes: Any) -> BoundedEmbodiedSessionState:
        changes["updated_at"] = _now()
        self._states[session_id] = replace(self._state(session_id), **changes)
        return self._states[session_id]

    def _increment_step(self, session_id: str) -> None:
        state = self._state(session_id)
        self._update_state(session_id, runtime_step_count=state.runtime_step_count + 1)

    def _latest_trace_id(self, session_id: str) -> str:
        traces = self.trace_store.list_by_session(session_id)
        if not traces:
            raise ValueError("no trace envelopes for session")
        return traces[-1].trace_id

    def binding_log(self, session_id: str) -> tuple[str, ...]:
        return tuple(self._binding_log[session_id])

    def transition_failures(self, session_id: str) -> tuple[str, ...]:
        return tuple(self._transition_failures[session_id])


def _ensure_valid(validation: dict[str, object], *, allow_status: str | None = None) -> None:
    if validation.get("valid") or (allow_status and validation.get("status") == allow_status):
        return
    raise ValueError(f"validation failed: {validation}")


def _limits_preserved(state: BoundedEmbodiedSessionState, config: BoundedEmbodiedSessionConfig) -> bool:
    return (
        state.runtime_step_count <= config.max_runtime_steps
        and state.event_frame_count <= config.max_event_frames
        and state.trace_envelope_count <= config.max_trace_envelopes
        and len(state.pending_teacher_review_ids) <= config.max_pending_teacher_reviews
    )


def build_bounded_embodied_session_runtime_audit(
    runtime: BoundedEmbodiedSessionRuntime,
    session_id: str,
    *,
    force_fake_function_binding: bool = False,
    force_cross_session_trace: bool = False,
    force_raw_trace_mutation: bool = False,
    force_raw_trace_summarization: bool = False,
    force_concept_id_in_raw_history: bool = False,
    force_teacher_decision: bool = False,
    force_reviewed_concept_created: bool = False,
    force_memory_commit: bool = False,
    force_external_control: bool = False,
    force_file_persistence: bool = False,
    force_first_output: bool = False,
    force_live_scheduler: bool = False,
    force_open_ended_loop: bool = False,
    force_limit_violation: bool = False,
) -> BoundedEmbodiedSessionRuntimeAudit:
    state = runtime.get_session_state(session_id)
    traces = runtime.get_session_trace(session_id)
    store_validation = validate_trace_envelope_store(runtime.trace_store)
    session_traces = runtime.trace_store.list_by_session(session_id)
    raw_traces = tuple(item for item in session_traces if item.trace_layer == "raw")
    trace_session_ids_consistent = all(item.session_id == session_id for item in session_traces) and not force_cross_session_trace
    raw_clean = all(
        "concept_id" not in item.payload_snapshot
        and "reviewed_concept_id" not in item.payload_snapshot
        and "interpretation_summary" not in item.payload_snapshot
        for item in raw_traces
    )
    records = runtime._records.get(session_id, {})
    required_binding_set = set(REQUIRED_FUNCTION_BINDINGS)
    actual_bindings = set(runtime.binding_log(session_id))
    actual_function_bindings_confirmed = required_binding_set.issubset(actual_bindings) and not force_fake_function_binding
    no_teacher_decision_created = all(item.teacher_decision is None and not item.resolved for item in runtime.get_pending_teacher_reviews(session_id)) and not force_teacher_decision
    no_reviewed_concept_created = not force_reviewed_concept_created
    no_memory_commit = not force_memory_commit
    status = _audit_status(
        state=state,
        transition_failures=runtime.transition_failures(session_id),
        actual_function_bindings_confirmed=actual_function_bindings_confirmed,
        store_validation=store_validation,
        trace_session_ids_consistent=trace_session_ids_consistent,
        raw_clean=raw_clean,
        no_teacher_decision_created=no_teacher_decision_created,
        no_reviewed_concept_created=no_reviewed_concept_created,
        no_memory_commit=no_memory_commit,
        force_raw_trace_mutation=force_raw_trace_mutation,
        force_raw_trace_summarization=force_raw_trace_summarization,
        force_concept_id_in_raw_history=force_concept_id_in_raw_history,
        force_external_control=force_external_control,
        force_file_persistence=force_file_persistence,
        force_first_output=force_first_output,
        force_live_scheduler=force_live_scheduler,
        force_open_ended_loop=force_open_ended_loop,
        force_limit_violation=force_limit_violation,
    )
    reasons = _audit_reasons_from_status(status)
    return BoundedEmbodiedSessionRuntimeAudit(
        session_runtime_audit_id=f"bounded_embodied_session_runtime_audit:{session_id}:{status}",
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        session_id=session_id,
        session_state_valid=state.status in set(BoundedEmbodiedSessionStatus),
        state_transitions_valid=not runtime.transition_failures(session_id),
        actual_function_bindings_confirmed=actual_function_bindings_confirmed,
        event_stack_valid=len(state.event_stack_frame_ids) == len(set(state.event_stack_frame_ids)),
        event_tree_valid=state.root_event_id is not None and bool(traces),
        trace_envelope_schema_valid=all(item.trace_schema_version == "ashl_trace_envelope_v1" for item in session_traces),
        trace_sequence_monotonic=bool(store_validation["trace_sequence_monotonic"]),
        trace_source_refs_valid=bool(store_validation["trace_source_refs_valid"]) and not force_cross_session_trace,
        trace_session_ids_consistent=trace_session_ids_consistent,
        raw_trace_append_only_confirmed=all(item.append_only for item in raw_traces) and not force_raw_trace_mutation,
        raw_trace_not_summarized_confirmed=not force_raw_trace_summarization,
        raw_trace_not_rewritten_confirmed=not force_raw_trace_mutation,
        concept_id_not_embedded_into_raw_history_confirmed=raw_clean and not force_concept_id_in_raw_history,
        host_event_stage_confirmed="host_body_event" in records,
        runtime_eventframe_stage_confirmed="runtime_eventframe_bridge" in records,
        internal_action_stage_confirmed="internal_action_result" in records,
        home_surface_stage_confirmed="home_surface_link_trace" in records,
        learning_evidence_stage_confirmed="learning_evidence_packet" in records,
        pending_teacher_review_stage_confirmed=bool(runtime.get_pending_teacher_reviews(session_id)),
        session_stopped_at_teacher_gate=state.status == BoundedEmbodiedSessionStatus.WAITING_TEACHER_REVIEW,
        no_teacher_decision_created=no_teacher_decision_created,
        no_reviewed_concept_created=no_reviewed_concept_created,
        no_memory_commit=no_memory_commit,
        no_long_term_memory_write=not force_memory_commit,
        no_core_memory_write=not force_memory_commit,
        no_real_hardware_access=True,
        no_external_control=not force_external_control,
        no_file_persistence=not force_file_persistence,
        no_first_output=not force_first_output,
        no_live_scheduler=not force_live_scheduler,
        no_open_ended_loop=not force_open_ended_loop,
        no_thought_engine_behavior=True,
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=reasons,
        source_trace_refs=tuple(item.trace_id for item in session_traces),
    )


def validate_bounded_embodied_session_runtime_audit(
    audit: BoundedEmbodiedSessionRuntimeAudit | dict[str, object],
) -> dict[str, object]:
    item = audit if isinstance(audit, BoundedEmbodiedSessionRuntimeAudit) else BoundedEmbodiedSessionRuntimeAudit(**dict(audit))
    valid = item.audit_status.startswith("passed_")
    return {"valid": valid, "status": item.audit_status, "reasons": [] if valid else list(item.blocked_reasons)}


def build_bounded_embodied_session_runtime_readiness(
    audit: BoundedEmbodiedSessionRuntimeAudit | dict[str, object],
) -> BoundedEmbodiedSessionRuntimeReadinessRecord:
    item = audit if isinstance(audit, BoundedEmbodiedSessionRuntimeAudit) else BoundedEmbodiedSessionRuntimeAudit(**dict(audit))
    passed = item.audit_status.startswith("passed_")
    return BoundedEmbodiedSessionRuntimeReadinessRecord(
        session_runtime_readiness_id=f"bounded_embodied_session_runtime_readiness:{item.session_runtime_audit_id}",
        schema_version=READINESS_SCHEMA_VERSION,
        created_at=_now(),
        source_session_runtime_audit_id=item.session_runtime_audit_id,
        current_verified_capability=SAFE_CLAIM,
        ready_for_teacher_gated_session_resume=passed,
        ready_for_teacher_decision_application=passed,
        ready_for_reviewed_interpretation_commit=passed,
        ready_for_session_end_commit_or_rollback=passed,
        ready_for_no_codex_two_cycle_run=passed,
        ready_for_real_hardware=False,
        ready_for_external_control=False,
        ready_for_live_scheduler=False,
        ready_for_first_output=False,
        ready_for_open_ended_loop=False,
        recommended_next_package="Package 116 / ASHL Core v1 Teacher-Gated Session Resume And Commit Minimal v0",
        recommended_next_reason=(
            "Apply an explicit teacher decision to the pending review, resume the "
            "same session, and commit only approved interpreted memory with source_trace_refs."
        ),
        readiness_status=(
            "ready_for_teacher_gated_session_resume_only"
            if passed
            else "not_ready_boundary_failure"
        ),
    )


def validate_bounded_embodied_session_runtime_readiness(
    record: BoundedEmbodiedSessionRuntimeReadinessRecord | dict[str, object],
) -> dict[str, object]:
    item = record if isinstance(record, BoundedEmbodiedSessionRuntimeReadinessRecord) else BoundedEmbodiedSessionRuntimeReadinessRecord(**dict(record))
    valid = item.readiness_status.startswith("ready_for_") and all(
        (
            item.ready_for_teacher_gated_session_resume,
            item.ready_for_teacher_decision_application,
            item.ready_for_reviewed_interpretation_commit,
            item.ready_for_session_end_commit_or_rollback,
            item.ready_for_no_codex_two_cycle_run,
        )
    )
    valid = valid and not any(
        (
            item.ready_for_real_hardware,
            item.ready_for_external_control,
            item.ready_for_live_scheduler,
            item.ready_for_first_output,
            item.ready_for_open_ended_loop,
        )
    )
    return {"valid": valid, "status": item.readiness_status, "reasons": [] if valid else [item.readiness_status]}


def build_demo_unknown_camera_to_review_runtime() -> dict[str, object]:
    runtime = BoundedEmbodiedSessionRuntime()
    state = runtime.create_session()
    runtime.inject_fixture_host_event(state.session_id, "camera_unknown_low_level_event")
    result = runtime.run_until_blocked(state.session_id)
    audit = build_bounded_embodied_session_runtime_audit(runtime, state.session_id)
    readiness = build_bounded_embodied_session_runtime_readiness(audit)
    return _runtime_payload(runtime, state.session_id, result, audit, readiness)


def build_demo_deferred_bridge_to_review_runtime() -> dict[str, object]:
    runtime = BoundedEmbodiedSessionRuntime()
    state = runtime.create_session()
    runtime.inject_fixture_host_event(state.session_id, "runtime_bridge_deferred")
    result = runtime.run_until_blocked(state.session_id)
    audit = build_bounded_embodied_session_runtime_audit(runtime, state.session_id)
    readiness = build_bounded_embodied_session_runtime_readiness(audit)
    return _runtime_payload(runtime, state.session_id, result, audit, readiness)


def build_demo_aborted_session_runtime() -> dict[str, object]:
    runtime = BoundedEmbodiedSessionRuntime()
    state = runtime.create_session()
    runtime.inject_fixture_host_event(state.session_id, "camera_unknown_low_level_event")
    runtime.step(state.session_id)
    runtime.abort_session(state.session_id, "demo_abort")
    audit = build_bounded_embodied_session_runtime_audit(runtime, state.session_id)
    readiness = build_bounded_embodied_session_runtime_readiness(audit)
    result = BoundedEmbodiedSessionRunResult(
        session_id=state.session_id,
        schema_version=RUN_RESULT_SCHEMA_VERSION,
        initial_status="created",
        final_status=runtime.get_session_state(state.session_id).status.value,
        executed_step_count=runtime.get_session_state(state.session_id).runtime_step_count,
        created_event_frame_count=runtime.get_session_state(state.session_id).event_frame_count,
        created_trace_envelope_count=len(runtime.get_session_trace(state.session_id)),
        pending_teacher_review_ids=runtime.get_session_state(state.session_id).pending_teacher_review_ids,
        selected_internal_action_kinds=tuple(),
        home_surface_link_ids=tuple(),
        learning_feedback_candidate_refs=tuple(),
        stop_reason="aborted",
        run_summary="Session aborted and raw trace preserved.",
        bounded_limits_preserved=True,
        trace_boundary_preserved=True,
    )
    return _runtime_payload(runtime, state.session_id, result, audit, readiness)


def build_demo_blocked_session_runtime(case: str) -> dict[str, object]:
    payload = build_demo_unknown_camera_to_review_runtime()
    runtime = payload["_runtime"]
    session_id = str(payload["session_state"]["session_id"])
    force_kwargs: dict[str, bool] = {}
    if case == "invalid-transition":
        runtime.transition_session_status(session_id, BoundedEmbodiedSessionStatus.RESUMED)
    elif case == "cross-session-trace":
        force_kwargs["force_cross_session_trace"] = True
    elif case == "raw-trace-mutation":
        force_kwargs["force_raw_trace_mutation"] = True
    elif case == "concept-id-in-raw-trace":
        force_kwargs["force_concept_id_in_raw_history"] = True
    elif case == "teacher-decision":
        force_kwargs["force_teacher_decision"] = True
    elif case == "memory-commit":
        force_kwargs["force_memory_commit"] = True
    elif case == "external-control":
        force_kwargs["force_external_control"] = True
    elif case == "first-output":
        force_kwargs["force_first_output"] = True
    elif case == "live-scheduler":
        force_kwargs["force_live_scheduler"] = True
    elif case == "fake-function-binding":
        force_kwargs["force_fake_function_binding"] = True
    else:
        raise ValueError(f"unknown blocked demo case: {case}")
    audit = build_bounded_embodied_session_runtime_audit(runtime, session_id, **force_kwargs)
    readiness = build_bounded_embodied_session_runtime_readiness(audit)
    payload["session_runtime_audit"] = audit.to_dict()
    payload["session_runtime_readiness"] = readiness.to_dict()
    return payload


def render_bounded_embodied_session_summary_text(payload_or_runtime: dict[str, object] | BoundedEmbodiedSessionRuntime, session_id: str | None = None) -> str:
    if isinstance(payload_or_runtime, BoundedEmbodiedSessionRuntime):
        if session_id is None:
            raise ValueError("session_id is required")
        return payload_or_runtime.render_session_summary(session_id)
    state = payload_or_runtime["session_state"]
    result = payload_or_runtime["run_result"]
    audit = payload_or_runtime["session_runtime_audit"]
    return "\n".join(
        (
            "Bounded Embodied Session Runtime",
            f"session_id: {state['session_id']}",
            f"status: {state['status']}",
            f"stop_reason: {result['stop_reason']}",
            f"audit_status: {audit['audit_status']}",
            f"pending_teacher_review_count: {len(payload_or_runtime['pending_teacher_reviews'])}",
        )
    )


def _runtime_payload(
    runtime: BoundedEmbodiedSessionRuntime,
    session_id: str,
    result: BoundedEmbodiedSessionRunResult,
    audit: BoundedEmbodiedSessionRuntimeAudit,
    readiness: BoundedEmbodiedSessionRuntimeReadinessRecord,
) -> dict[str, object]:
    return {
        "_runtime": runtime,
        "session_state": runtime.get_session_state(session_id).to_dict(),
        "session_trace": tuple(item.to_dict() for item in runtime.get_session_trace(session_id)),
        "pending_teacher_reviews": tuple(item.to_dict() for item in runtime.get_pending_teacher_reviews(session_id)),
        "run_result": result.to_dict(),
        "session_runtime_audit": audit.to_dict(),
        "session_runtime_readiness": readiness.to_dict(),
        "actual_bound_existing_functions": runtime.binding_log(session_id),
        "rendered_session_summary": runtime.render_session_summary(session_id),
    }


def _audit_status(
    *,
    state: BoundedEmbodiedSessionState,
    transition_failures: tuple[str, ...],
    actual_function_bindings_confirmed: bool,
    store_validation: dict[str, object],
    trace_session_ids_consistent: bool,
    raw_clean: bool,
    no_teacher_decision_created: bool,
    no_reviewed_concept_created: bool,
    no_memory_commit: bool,
    force_raw_trace_mutation: bool,
    force_raw_trace_summarization: bool,
    force_concept_id_in_raw_history: bool,
    force_external_control: bool,
    force_file_persistence: bool,
    force_first_output: bool,
    force_live_scheduler: bool,
    force_open_ended_loop: bool,
    force_limit_violation: bool,
) -> str:
    if transition_failures:
        return "blocked_invalid_state_transition"
    if not actual_function_bindings_confirmed:
        return "blocked_fake_function_binding"
    if not bool(store_validation["trace_sequence_monotonic"]):
        return "blocked_trace_sequence_failure"
    if not bool(store_validation["trace_source_refs_valid"]):
        return "blocked_trace_reference_failure"
    if not trace_session_ids_consistent:
        return "blocked_cross_session_trace_detected"
    if force_raw_trace_mutation:
        return "blocked_raw_trace_mutation_detected"
    if force_raw_trace_summarization:
        return "blocked_raw_trace_summarization_detected"
    if force_concept_id_in_raw_history or not raw_clean:
        return "blocked_concept_id_in_raw_history"
    if not no_teacher_decision_created:
        return "blocked_teacher_decision_created"
    if not no_reviewed_concept_created:
        return "blocked_reviewed_concept_created"
    if not no_memory_commit:
        return "blocked_memory_commit_detected"
    if force_external_control:
        return "blocked_external_control_detected"
    if force_file_persistence:
        return "blocked_file_persistence_detected"
    if force_first_output:
        return "blocked_first_output_detected"
    if force_live_scheduler:
        return "blocked_live_scheduler_detected"
    if force_open_ended_loop:
        return "blocked_open_ended_loop_detected"
    if force_limit_violation or state.boundary_failure_codes:
        return "blocked_limit_violation"
    if state.status == BoundedEmbodiedSessionStatus.ABORTED:
        return "passed_abort_preserves_raw_trace"
    if state.status == BoundedEmbodiedSessionStatus.WAITING_TEACHER_REVIEW:
        return "passed_session_waiting_teacher_review"
    return "passed_bounded_embodied_session_runtime"


def _audit_reasons_from_status(status: str) -> tuple[str, ...]:
    return tuple() if status.startswith("passed_") else (status,)
