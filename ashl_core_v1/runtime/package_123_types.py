"""Record types for Package 123 real perception two-cycle growth runs."""

from __future__ import annotations

import os
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import monotonic_ns, plain, sha256_payload, stable_id, utc_now


EXPERIMENT_ID = "host_internal_visual_audio_pulse_v0"
EXPERIENCE_CLASSIFICATION = "real_host_internal_perception"
PACKAGE_123_STORE_DIRNAME = "package_123_real_perception_v0"
PACKAGE_123_STORE_FILENAME = "package_123.sqlite3"

STIMULUS_TRANSITION_SCHEMA_VERSION = "ashl_package_123_stimulus_transition_v0"
STIMULUS_MANIFEST_SCHEMA_VERSION = "ashl_package_123_stimulus_run_manifest_v0"
WINDOW_BINDING_SCHEMA_VERSION = "ashl_package_123_window_capture_binding_v0"
LOOPBACK_DESCRIPTOR_SCHEMA_VERSION = "ashl_package_123_system_audio_loopback_source_descriptor_v0"
SOURCE_PROFILE_SCHEMA_VERSION = "ashl_package_123_experience_source_profile_v0"
PREFLIGHT_SCHEMA_VERSION = "ashl_package_123_preflight_v0"
CYCLE_RECORD_SCHEMA_VERSION = "ashl_package_123_cycle_record_v0"
READBACK_TIMING_SCHEMA_VERSION = "ashl_package_123_readback_load_timing_v0"
READBACK_INFLUENCE_SCHEMA_VERSION = "ashl_package_123_real_perception_readback_influence_v0"
TWO_CYCLE_COMPARISON_SCHEMA_VERSION = "ashl_package_123_two_cycle_comparison_v0"
AUDIT_SCHEMA_VERSION = "ashl_package_123_real_perception_growth_audit_v0"

WINDOW_CLIENT_WIDTH = 960
WINDOW_CLIENT_HEIGHT = 540
STIMULUS_DURATION_MS = 10_000
CAPTURE_PREROLL_MS = 500
CAPTURE_POSTROLL_MS = 500
MAX_CAPTURE_DURATION_MS = 12_000
LOOPBACK_CHUNK_DURATION_MS = 100

STIMULUS_SCHEDULE = (
    (0, "black", "silent"),
    (2_000, "white", "tone"),
    (2_400, "black", "silent"),
    (3_000, "white", "tone"),
    (3_400, "black", "silent"),
    (4_000, "white", "tone"),
    (4_400, "black", "silent"),
    (5_000, "white", "tone"),
    (5_400, "black", "silent"),
    (10_000, "black", "silent"),
)


def package_123_store_path(state_dir: str | Path) -> Path:
    return Path(state_dir) / PACKAGE_123_STORE_DIRNAME / PACKAGE_123_STORE_FILENAME


def package_123_root_dir(state_dir: str | Path) -> Path:
    return Path(state_dir) / PACKAGE_123_STORE_DIRNAME


def new_experiment_run_id() -> str:
    return stable_id("package_123_experiment_run")


def new_process_instance_id() -> str:
    return stable_id("package_123_process_instance")


def state_dir_fingerprint(state_dir: str | Path) -> str:
    return sha256_payload({"state_dir": str(Path(state_dir).resolve())})


def current_pid() -> int:
    return os.getpid()


def to_payload(record: Any) -> dict[str, object]:
    if hasattr(record, "to_dict"):
        return dict(record.to_dict())
    return dict(record)


def _tuple_of_str(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()))


def _tuple_of_records(value: Any, cls: Any) -> tuple[Any, ...]:
    return tuple(item if isinstance(item, cls) else cls.from_dict(dict(item)) for item in (value or ()))


@dataclass(frozen=True)
class StimulusTransitionRecord:
    transition_id: str
    experiment_run_id: str
    transition_index: int
    scheduled_offset_ns: int
    command_issued_monotonic_ns: int
    visual_state: str
    audio_state: str
    stimulus_ground_truth_only: bool

    def __post_init__(self) -> None:
        if self.visual_state not in {"black", "white"}:
            raise ValueError("visual_state must be black or white")
        if self.audio_state not in {"silent", "tone"}:
            raise ValueError("audio_state must be silent or tone")
        if not self.stimulus_ground_truth_only:
            raise ValueError("stimulus transitions are ground-truth-only")

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "StimulusTransitionRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class StimulusRunManifest:
    experiment_run_id: str
    experiment_id: str
    schema_version: str
    process_instance_id: str
    window_title: str
    window_handle: int
    client_width: int
    client_height: int
    selected_render_endpoint_id: str
    stimulus_started_utc: str
    stimulus_started_monotonic_ns: int
    stimulus_finished_monotonic_ns: int
    transitions: tuple[StimulusTransitionRecord, ...]
    consumed_by_perception_runtime: bool

    def __post_init__(self) -> None:
        if self.schema_version != STIMULUS_MANIFEST_SCHEMA_VERSION:
            raise ValueError("invalid stimulus manifest schema_version")
        if self.experiment_id != EXPERIMENT_ID:
            raise ValueError("invalid Package 123 experiment_id")
        if self.client_width != WINDOW_CLIENT_WIDTH or self.client_height != WINDOW_CLIENT_HEIGHT:
            raise ValueError("stimulus window client geometry must be 960x540")
        if self.consumed_by_perception_runtime:
            raise ValueError("stimulus ground truth must not be consumed by perception runtime")
        object.__setattr__(self, "transitions", _tuple_of_records(self.transitions, StimulusTransitionRecord))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "StimulusRunManifest":
        return cls(**dict(data))


@dataclass(frozen=True)
class BoundedWindowCaptureBinding:
    binding_id: str
    schema_version: str
    created_at: str
    experiment_run_id: str
    target_hwnd: int
    target_window_title: str
    target_process_id: int
    client_left: int
    client_top: int
    client_width: int
    client_height: int
    binding_status: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != WINDOW_BINDING_SCHEMA_VERSION:
            raise ValueError("invalid window binding schema_version")
        if self.binding_status not in {"bound", "window_not_found", "window_minimized", "window_geometry_changed", "window_closed", "capture_failed"}:
            raise ValueError("invalid window binding status")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "BoundedWindowCaptureBinding":
        return cls(**dict(data))


@dataclass(frozen=True)
class SystemAudioLoopbackSourceDescriptor:
    source_descriptor_id: str
    schema_version: str
    created_at: str
    endpoint_id: str
    endpoint_name: str
    sample_rate_hz: int
    channel_count: int
    sample_format: str
    chunk_duration_ms: int
    loopback_scope: str
    bounded_capture_maximum_ms: int
    enabled_for_daily_runtime: bool
    available: bool = True
    backend_name: str = "windows_wasapi_loopback"
    failure_reason: str | None = None

    def __post_init__(self) -> None:
        if self.schema_version != LOOPBACK_DESCRIPTOR_SCHEMA_VERSION:
            raise ValueError("invalid loopback descriptor schema_version")
        if self.chunk_duration_ms != LOOPBACK_CHUNK_DURATION_MS:
            raise ValueError("Package 123 loopback chunk duration must be 100 ms")
        if self.loopback_scope != "selected_render_endpoint":
            raise ValueError("loopback_scope must be selected_render_endpoint")
        if self.bounded_capture_maximum_ms != MAX_CAPTURE_DURATION_MS:
            raise ValueError("Package 123 loopback max duration must be 12000 ms")
        if self.enabled_for_daily_runtime:
            raise ValueError("Package 123 loopback is not enabled for daily runtime")

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "SystemAudioLoopbackSourceDescriptor":
        return cls(**dict(data))


@dataclass(frozen=True)
class Package123ExperienceSourceProfile:
    source_profile_id: str
    schema_version: str
    created_at: str
    experiment_id: str
    experiment_run_id: str
    screen_lane: str
    audio_lane: str
    host_state_lane: str
    camera_lane: str
    screen_binding_id: str
    audio_source_descriptor_id: str
    real_live_capture: bool
    prerecorded_fixture_used: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SOURCE_PROFILE_SCHEMA_VERSION:
            raise ValueError("invalid source profile schema_version")
        if self.experiment_id != EXPERIMENT_ID:
            raise ValueError("invalid Package 123 experiment_id")
        required = {
            "screen_lane": "windows_window_capture",
            "audio_lane": "system_audio_loopback",
            "host_state_lane": "real_host_state",
            "camera_lane": "not_participating_by_design",
        }
        for field_name, expected in required.items():
            if getattr(self, field_name) != expected:
                raise ValueError(f"{field_name} must be {expected}")
        if not self.real_live_capture or self.prerecorded_fixture_used:
            raise ValueError("Package 123 source profile requires real live capture and no fixture")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Package123ExperienceSourceProfile":
        return cls(**dict(data))


@dataclass(frozen=True)
class Package123PreflightRecord:
    preflight_id: str
    schema_version: str
    created_at: str
    experiment_run_id: str
    cycle_index: int
    window_capture_ready: bool
    visual_contrast_verified: bool
    loopback_source_ready: bool
    loopback_tone_verified: bool
    background_audio_silent: bool
    host_state_ready: bool
    compiler_compatibility_verified: bool
    perception_profile_verified: bool
    llm_runtime_available: bool
    network_required: bool
    preflight_status: str
    failure_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PREFLIGHT_SCHEMA_VERSION:
            raise ValueError("invalid Package 123 preflight schema_version")
        if self.preflight_status not in {"passed", "blocked", "failed"}:
            raise ValueError("invalid preflight_status")
        if self.preflight_status == "passed" and (self.llm_runtime_available or self.network_required):
            raise ValueError("passed preflight must not require LLM or network")
        object.__setattr__(self, "failure_reasons", _tuple_of_str(self.failure_reasons))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Package123PreflightRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class Package123CycleRecord:
    cycle_record_id: str
    schema_version: str
    created_at: str
    experiment_id: str
    experiment_run_id: str
    cycle_index: int
    process_instance_id: str
    operating_system_process_id: int
    preflight_id: str
    source_profile_id: str
    stimulus_manifest_id: str
    screen_artifact_refs: tuple[str, ...]
    audio_artifact_refs: tuple[str, ...]
    host_state_artifact_refs: tuple[str, ...]
    perception_readable_data_refs: tuple[str, ...]
    perception_session_id: str
    bounded_runtime_session_id: str
    final_session_state: str
    pending_teacher_review_id: str | None
    readback_loaded_before_event: bool
    readback_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CYCLE_RECORD_SCHEMA_VERSION:
            raise ValueError("invalid Package 123 cycle record schema_version")
        if self.experiment_id != EXPERIMENT_ID:
            raise ValueError("invalid Package 123 experiment_id")
        if self.cycle_index not in {1, 2}:
            raise ValueError("cycle_index must be 1 or 2")
        if self.cycle_index == 1 and self.readback_loaded_before_event:
            raise ValueError("Cycle 1 must not preload readback")
        for name in (
            "screen_artifact_refs",
            "audio_artifact_refs",
            "host_state_artifact_refs",
            "perception_readable_data_refs",
            "readback_record_refs",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Package123CycleRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReadbackLoadTimingRecord:
    timing_record_id: str
    schema_version: str
    cycle_record_id: str
    readback_loaded_monotonic_ns: int
    capture_started_monotonic_ns: int
    stimulus_started_monotonic_ns: int
    candidate_evaluated_monotonic_ns: int
    loaded_before_capture: bool
    loaded_before_stimulus: bool
    loaded_before_candidate_evaluation: bool
    readback_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READBACK_TIMING_SCHEMA_VERSION:
            raise ValueError("invalid readback load timing schema_version")
        if not self.loaded_before_stimulus or not self.loaded_before_candidate_evaluation:
            raise ValueError("Package 123 requires readback before stimulus and candidate evaluation")
        object.__setattr__(self, "readback_record_refs", _tuple_of_str(self.readback_record_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ReadbackLoadTimingRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RealPerceptionReadbackInfluenceRecord:
    influence_record_id: str
    schema_version: str
    created_at: str
    cycle_1_memory_application_data_id: str
    cycle_2_candidate_id: str
    scorer_id: str
    scorer_version: str
    score_without_readback: float | None
    score_with_readback: float
    readback_contribution: float
    influencing_readback_refs: tuple[str, ...]
    matching_evidence_refs: tuple[str, ...]
    actual_runtime_hot_path: bool
    hard_coded_experiment_match_used: bool

    def __post_init__(self) -> None:
        if self.schema_version != READBACK_INFLUENCE_SCHEMA_VERSION:
            raise ValueError("invalid readback influence schema_version")
        if self.actual_runtime_hot_path and self.readback_contribution <= 0:
            raise ValueError("actual runtime hot path influence must have nonzero contribution")
        if self.hard_coded_experiment_match_used:
            raise ValueError("hard-coded Package 123 experiment match is forbidden")
        object.__setattr__(self, "influencing_readback_refs", _tuple_of_str(self.influencing_readback_refs))
        object.__setattr__(self, "matching_evidence_refs", _tuple_of_str(self.matching_evidence_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RealPerceptionReadbackInfluenceRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class Package123TwoCycleComparisonRecord:
    comparison_id: str
    schema_version: str
    created_at: str
    experiment_id: str
    cycle_1_record_id: str
    cycle_2_record_id: str
    cycle_1_process_instance_id: str
    cycle_2_process_instance_id: str
    process_instances_different: bool
    raw_artifacts_different: bool
    runtime_sessions_different: bool
    cycle_1_commit_present: bool
    cycle_2_readback_loaded_before_event: bool
    readback_influence_record_id: str
    readback_contribution_nonzero: bool
    cycle_2_final_state: str
    no_llm_runtime: bool
    no_codex_runtime: bool
    no_network_runtime: bool

    def __post_init__(self) -> None:
        if self.schema_version != TWO_CYCLE_COMPARISON_SCHEMA_VERSION:
            raise ValueError("invalid two-cycle comparison schema_version")
        if self.experiment_id != EXPERIMENT_ID:
            raise ValueError("invalid Package 123 experiment_id")

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Package123TwoCycleComparisonRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class Package123RealPerceptionGrowthAuditRecord:
    audit_id: str
    schema_version: str
    created_at: str
    real_window_capture_verified: bool
    real_system_audio_loopback_verified: bool
    real_host_state_verified: bool
    prerecorded_fixture_used: bool
    obs_used_as_sensor: bool
    camera_claimed: bool
    cycle_1_waiting_review_verified: bool
    cycle_1_teacher_approval_verified: bool
    cycle_1_memory_commit_verified: bool
    cycle_2_new_process_verified: bool
    cycle_2_readback_preloaded_verified: bool
    cycle_2_real_capture_verified: bool
    cycle_2_readback_influence_verified: bool
    cycle_2_waiting_review_verified: bool
    stimulus_ground_truth_entered_learning_path: bool
    hard_coded_recognition_detected: bool
    time_perception_claimed: bool
    language_understanding_claimed: bool
    qingyin_output_created: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    audit_status: str
    failure_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUDIT_SCHEMA_VERSION:
            raise ValueError("invalid Package 123 audit schema_version")
        object.__setattr__(self, "failure_reasons", _tuple_of_str(self.failure_reasons))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Package123RealPerceptionGrowthAuditRecord":
        return cls(**dict(data))


def build_stimulus_transition(
    *,
    experiment_run_id: str,
    transition_index: int,
    scheduled_offset_ms: int,
    visual_state: str,
    audio_state: str,
    command_issued_monotonic_ns: int | None = None,
) -> StimulusTransitionRecord:
    return StimulusTransitionRecord(
        transition_id=f"stimulus_transition:{experiment_run_id}:{transition_index}",
        experiment_run_id=experiment_run_id,
        transition_index=transition_index,
        scheduled_offset_ns=int(scheduled_offset_ms) * 1_000_000,
        command_issued_monotonic_ns=command_issued_monotonic_ns or monotonic_ns(),
        visual_state=visual_state,
        audio_state=audio_state,
        stimulus_ground_truth_only=True,
    )


def build_source_profile(
    *,
    experiment_run_id: str,
    screen_binding_id: str,
    audio_source_descriptor_id: str,
    source_trace_refs: tuple[str, ...] = tuple(),
) -> Package123ExperienceSourceProfile:
    return Package123ExperienceSourceProfile(
        source_profile_id=stable_id("package_123_source_profile"),
        schema_version=SOURCE_PROFILE_SCHEMA_VERSION,
        created_at=utc_now(),
        experiment_id=EXPERIMENT_ID,
        experiment_run_id=experiment_run_id,
        screen_lane="windows_window_capture",
        audio_lane="system_audio_loopback",
        host_state_lane="real_host_state",
        camera_lane="not_participating_by_design",
        screen_binding_id=screen_binding_id,
        audio_source_descriptor_id=audio_source_descriptor_id,
        real_live_capture=True,
        prerecorded_fixture_used=False,
        source_trace_refs=source_trace_refs,
    )
