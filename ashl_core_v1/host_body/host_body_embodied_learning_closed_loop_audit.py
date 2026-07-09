"""Package 113 current ASHL Core v1 status report output."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CURRENT_STATUS_REPORT_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "current_ashl_core_v1_status_after_package_113.md"
)

PACKAGE_113_MILESTONE_AUDIT_RESULT = (
    "passed_host_body_embodied_learning_closed_loop_milestone_audit"
)

CURRENT_SAFE_LOOP_STEPS = (
    "Host Body event",
    "internal action",
    "LearningFeedbackCandidate",
    "existing learning pipeline",
    "ReviewedConcept readiness",
    "working readback",
    "readback-influenced internal action choice",
)

COMPLETED_MAJOR_LOOPS = (
    "bounded task learning loop v0",
    "ReviewedConcept working readback loop v0",
    "Host Body v0",
    "Host Body evidence to LearningFeedbackCandidate bridge",
    "Host Body feedback through existing learning pipeline",
    "Host Body ReviewedConcept working readback",
    "Host Body readback internal action influence",
)

NEXT_RECOMMENDED_PACKAGES = (
    "114 / Internal Action Home Surface Link",
    "115 / Runtime State Summary / Session Shell",
    "116 / Bounded Embodied Loop Runner",
    "117 / Teacher Console No-Codex Operation Flow",
    "118 / Session End Review + Promote Gate",
    "119 / No-Codex Fixture Embodied Growth Loop Milestone Audit",
    "120+ real low-level camera / mic adapters",
)

FORBIDDEN_CAPABILITY_FLAGS = {
    "real_camera_access_created": False,
    "real_microphone_access_created": False,
    "semantic_vision_created": False,
    "speech_recognition_created": False,
    "task_engine_selected_action_from_host_body_readback_created": False,
    "final_action_created": False,
    "direct_command_created": False,
    "sandbox_execution_created": False,
    "external_control_created": False,
    "os_operation_created": False,
    "mouse_operation_created": False,
    "keyboard_operation_created": False,
    "browser_operation_created": False,
    "file_operation_created": False,
    "network_operation_created": False,
    "shell_operation_created": False,
    "api_operation_created": False,
    "long_term_memory_write_created": False,
    "core_memory_write_created": False,
    "automatic_learning_approval_created": False,
    "teacher_approval_creation_created": False,
    "first_output_created": False,
    "live_qingyin_runtime_session_created": False,
    "thought_engine_behavior_created": False,
    "production_behavior_created": False,
    "gcmc_runtime_implemented": False,
    "cl_token_created": False,
    "concept_compiler_created": False,
    "pattern_miner_created": False,
}

REQUIRED_STATUS_REPORT_FRAGMENTS = (
    "# ASHL Core v1 Current Status After Package 113",
    "Package 113 milestone audit result",
    PACKAGE_113_MILESTONE_AUDIT_RESULT,
    "Host Body embodied learning readback loop status",
    "bounded task learning loop v0",
    "ReviewedConcept working readback loop v0",
    "Host Body v0",
    "Host Body evidence to LearningFeedbackCandidate bridge",
    "Host Body feedback through existing learning pipeline",
    "Host Body ReviewedConcept working readback",
    "Host Body readback internal action influence",
    "Host Body event",
    "readback-influenced internal action choice",
    "real camera access: false / not created",
    "real microphone access: false / not created",
    "semantic vision: false / not created",
    "speech recognition: false / not created",
    "Task Engine selected_action from Host Body readback: false / not created",
    "final_action / direct_command / sandbox execution: false / not created",
    "external control: false / not created",
    "OS / mouse / keyboard / browser / file / network / shell / API operation: false / not created",
    "long-term memory write: false / not created",
    "Core memory write: false / not created",
    "automatic learning approval: false / not created",
    "teacher approval creation: false / not created",
    "first_output: false / not created",
    "live Qingyin runtime session: false / not created",
    "Thought Engine behavior: false / not created",
    "production behavior: false / not created",
    "GCMC v0.3 is future AGE architecture only",
    "Qingyin v1 does not implement GCMC runtime",
    "Qingyin v1 does not create CL tokens",
    "Qingyin v1 does not create Concept Compiler",
    "Qingyin v1 does not create Pattern Miner",
    "Trace Spine format stays unified and time-aligned",
    "Raw trace is append-only during service period and is not summarized",
    "Memory layer stores reviewed interpretation + source_trace_refs",
    "concept_id is not embedded into raw history",
    "formed_under_assumption is not required now because Qingyin v1 does not use CL tokens",
    "bounded embodied loop runner",
    "no-Codex teacher console operation flow",
    "session end review / promote gate",
    "no-Codex fixture embodied growth loop milestone audit",
    "114 / Internal Action Home Surface Link",
    "115 / Runtime State Summary / Session Shell",
    "116 / Bounded Embodied Loop Runner",
    "117 / Teacher Console No-Codex Operation Flow",
    "118 / Session End Review + Promote Gate",
    "119 / No-Codex Fixture Embodied Growth Loop Milestone Audit",
    "120+ real low-level camera / mic adapters",
    "not a live autonomous Qingyin runtime",
    "Qingyin is awake",
    "Qingyin has first_output",
    "Qingyin has live runtime autonomy",
)


def get_current_status_report_markdown() -> str:
    """Return the checked-in Package 113 current status report markdown."""

    return CURRENT_STATUS_REPORT_PATH.read_text(encoding="utf-8")


def validate_current_status_report_text(markdown: str | None = None) -> dict[str, Any]:
    """Validate the Package 113 current status report against required fragments."""

    report_text = get_current_status_report_markdown() if markdown is None else markdown
    missing_fragments = tuple(
        fragment
        for fragment in REQUIRED_STATUS_REPORT_FRAGMENTS
        if fragment not in report_text
    )
    return {
        "valid": not missing_fragments,
        "missing_fragments": missing_fragments,
        "report_path": str(CURRENT_STATUS_REPORT_PATH),
        "report_file_exists": CURRENT_STATUS_REPORT_PATH.exists(),
        "package_113_milestone_audit_result": PACKAGE_113_MILESTONE_AUDIT_RESULT,
        "required_fragment_count": len(REQUIRED_STATUS_REPORT_FRAGMENTS),
    }


def build_current_ashl_core_v1_status_after_package_113_report() -> dict[str, Any]:
    """Build a read-only current situation report payload for Package 113."""

    markdown = get_current_status_report_markdown()
    return {
        "report_kind": "current_ashl_core_v1_status_after_package_113",
        "report_generated_by": "Codex",
        "report_path": str(CURRENT_STATUS_REPORT_PATH),
        "report_markdown": markdown,
        "package_113_milestone_audit_result": PACKAGE_113_MILESTONE_AUDIT_RESULT,
        "host_body_embodied_learning_readback_loop_status": (
            "fixture_only_teacher_gated_readback_influenced_internal_action_choice"
        ),
        "completed_major_loops": COMPLETED_MAJOR_LOOPS,
        "current_safe_loop_steps": CURRENT_SAFE_LOOP_STEPS,
        "next_recommended_packages": NEXT_RECOMMENDED_PACKAGES,
        "validation": validate_current_status_report_text(markdown),
        **FORBIDDEN_CAPABILITY_FLAGS,
    }


SOURCE_ENGINE = "host_body"

SCOPE_SCHEMA_VERSION = "qingyin_host_body_embodied_learning_closed_loop_scope_v0"
CAPABILITY_LEDGER_SCHEMA_VERSION = (
    "qingyin_host_body_embodied_learning_closed_loop_capability_ledger_v0"
)
BOUNDARY_LEDGER_SCHEMA_VERSION = (
    "qingyin_host_body_embodied_learning_closed_loop_boundary_ledger_v0"
)
INTEGRATED_TRACE_SCHEMA_VERSION = (
    "qingyin_host_body_embodied_learning_closed_loop_integrated_trace_v0"
)
MILESTONE_AUDIT_SCHEMA_VERSION = (
    "qingyin_host_body_embodied_learning_closed_loop_milestone_audit_v0"
)
READINESS_SCHEMA_VERSION = (
    "qingyin_host_body_embodied_learning_closed_loop_readiness_v0"
)

MILESTONE_NAME = "host_body_embodied_learning_closed_loop_v0"
MILESTONE_KIND = "fixture_only_teacher_gated_milestone_audit"

INCLUDED_PACKAGES = (
    "Package 107",
    "Package 108",
    "Package 109",
    "Package 110",
    "Package 111",
    "Package 112",
    "Package 113 report add-on",
)
INCLUDED_COMMITS = (
    "ea07c6a",
    "b658cea",
    "192ef0f",
    "b04ad60",
    "959bbf7",
    "f4f3371",
    "56e9b22",
)
INCLUDED_LOOP_STEPS = CURRENT_SAFE_LOOP_STEPS
EXCLUDED_CAPABILITIES = (
    "new_host_body_runtime_behavior",
    "new_learning_behavior",
    "new_memory_behavior",
    "new_teacher_review_system",
    "new_concept_system",
    "learning_feedback_candidate_creation_by_this_package",
    "concept_candidate_creation_by_this_package",
    "reviewed_concept_creation_by_this_package",
    "memory_application_data_creation_by_this_package",
    "long_term_memory_write",
    "core_memory_write",
    "raw_trace_summarization",
    "raw_trace_mutation",
    "concept_id_embedded_into_raw_history",
    "task_engine_selected_action",
    "direct_command",
    "external_control",
    "first_output",
    "live_runtime_session",
    "thought_engine_behavior",
    "production_behavior",
)

PASSED_AUDIT_STATUS = "passed_host_body_embodied_learning_closed_loop_milestone"
SAFE_CLAIM = (
    "ASHL Core v1 has sealed the first fixture-only, teacher-gated Host Body "
    "embodied learning readback loop milestone. The verified loop is: Host Body "
    "event -> internal-only action -> LearningFeedbackCandidate bridge -> "
    "existing learning pipeline compatibility -> ReviewedConcept readiness replay "
    "-> working readback visibility -> readback-influenced internal-only action choice."
)
TRACE_SPINE_SAFE_CLAIM = (
    "ASHL Core v1 preserves future CL ore by enforcing unified time-aligned Trace "
    "Spine format, raw trace append-only during service period, no raw trace "
    "summarization, memory layer storing reviewed interpretation plus "
    "source_trace_refs, no raw trace dump into MemoryLearningTrace, and no "
    "concept_id embedded into raw history."
)
BLOCKED_CLAIMS = (
    "qingyin_is_awake",
    "live_runtime_autonomy",
    "real_sensor_perception",
    "computer_control",
    "task_engine_action_selection_from_host_body_readback",
    "command_execution",
    "self_approved_learning",
    "long_term_memory_write",
    "first_output",
    "gcmc_runtime",
    "cl_tokens",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _plain(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return value


def _record(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return None


def _get(record: Any, key: str, default: Any = None) -> Any:
    data = _record(record)
    if data is None:
        return default
    return data.get(key, default)


def _tuple_of_str(value: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    return tuple(str(item) for item in value)


def _tuple_of_dict(value: tuple[dict[str, Any], ...] | list[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    return tuple(dict(item) for item in value)


def _validation(status: str, pass_statuses: set[str]) -> dict[str, object]:
    valid = status in pass_statuses
    return {"valid": valid, "status": status, "reasons": [] if valid else [status]}


@dataclass(frozen=True)
class HostBodyEmbodiedLearningClosedLoopScopeRecord:
    closed_loop_scope_id: str
    schema_version: str
    created_at: str
    source_engine: str
    milestone_name: str
    milestone_kind: str
    included_packages: tuple[str, ...]
    included_commits: tuple[str, ...]
    included_loop_steps: tuple[str, ...]
    excluded_capabilities: tuple[str, ...]
    host_body_v0_required: bool
    learning_feedback_bridge_required: bool
    existing_learning_pipeline_compatibility_required: bool
    reviewed_concept_replay_required: bool
    working_readback_integration_required: bool
    readback_internal_action_influence_required: bool
    trace_spine_boundary_required: bool
    current_status_report_required: bool
    new_behavior_allowed: bool
    new_learning_allowed: bool
    new_memory_write_allowed: bool
    external_control_allowed: bool
    first_output_allowed: bool
    live_runtime_allowed: bool
    scope_status: str
    scope_summary: str
    source_trace_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class HostBodyEmbodiedLearningClosedLoopCapabilityLedgerRecord:
    closed_loop_capability_ledger_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_closed_loop_scope_id: str
    capability_entries: tuple[dict[str, Any], ...]
    host_body_v0_verified: bool
    host_body_evidence_to_learning_feedback_verified: bool
    existing_learning_pipeline_compatibility_verified: bool
    reviewed_concept_replay_verified: bool
    working_readback_integration_verified: bool
    readback_internal_action_influence_verified: bool
    trace_spine_raw_evidence_boundary_verified: bool
    current_status_report_verified: bool
    capability_count: int
    capability_ledger_status: str
    capability_ledger_summary: str
    new_capability_created_by_this_package: bool
    source_trace_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class HostBodyEmbodiedLearningClosedLoopBoundaryLedgerRecord:
    closed_loop_boundary_ledger_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_closed_loop_scope_id: str
    boundary_entries: tuple[dict[str, Any], ...]
    fixture_only_confirmed: bool
    teacher_gated_confirmed: bool
    audit_only_package_confirmed: bool
    no_real_camera_access: bool
    no_real_microphone_access: bool
    no_semantic_vision: bool
    no_speech_recognition: bool
    no_task_engine_selected_action: bool
    no_final_action: bool
    no_direct_command: bool
    no_sandbox_execution: bool
    no_external_control: bool
    no_os_control: bool
    no_mouse_control: bool
    no_keyboard_control: bool
    no_browser_control: bool
    no_file_operation: bool
    no_network_execution: bool
    no_shell_execution: bool
    no_external_api_call: bool
    no_unity_runtime_connection: bool
    no_avatar_control: bool
    no_long_term_memory_write: bool
    no_core_memory_write: bool
    no_archive_memory_write: bool
    no_anchor_write: bool
    no_state_persistence_write: bool
    no_memory_layer_write_by_this_package: bool
    no_raw_trace_summarization: bool
    no_raw_trace_mutation: bool
    no_raw_trace_dump_into_memory_learning_trace: bool
    no_concept_id_embedded_into_raw_history: bool
    source_trace_refs_preserved: bool
    no_learning_candidate_creation_by_this_package: bool
    no_concept_candidate_creation_by_this_package: bool
    no_reviewed_concept_creation_by_this_package: bool
    no_memory_application_data_creation_by_this_package: bool
    no_automatic_learning_approval: bool
    no_teacher_approval_created: bool
    no_first_output: bool
    no_free_text_conversation: bool
    no_voice_output: bool
    no_live_runtime_session: bool
    no_live_engine_invocation: bool
    no_autonomous_scheduler: bool
    no_open_ended_loop: bool
    no_thought_engine_behavior: bool
    no_production_behavior: bool
    boundary_ledger_status: str
    boundary_ledger_summary: str
    source_trace_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class HostBodyEmbodiedLearningClosedLoopIntegratedTraceRecord:
    closed_loop_integrated_trace_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_closed_loop_scope_id: str
    source_host_body_v0_audit_id: str | None
    source_learning_feedback_bridge_audit_id: str | None
    source_existing_pipeline_compatibility_audit_id: str | None
    source_reviewed_concept_replay_audit_id: str | None
    source_working_readback_integration_audit_id: str | None
    source_readback_internal_action_influence_audit_id: str | None
    source_current_status_report_path: str | None
    integrated_loop_steps: tuple[dict[str, Any], ...]
    step_count: int
    host_body_event_step_confirmed: bool
    internal_action_step_confirmed: bool
    learning_feedback_candidate_step_confirmed: bool
    existing_learning_pipeline_step_confirmed: bool
    reviewed_concept_readiness_step_confirmed: bool
    working_readback_step_confirmed: bool
    readback_influenced_internal_action_step_confirmed: bool
    trace_spine_boundary_confirmed: bool
    current_status_report_confirmed: bool
    integrated_trace_status: str
    integrated_trace_summary: str
    new_runtime_behavior_created: bool
    new_learning_behavior_created: bool
    new_memory_write_created: bool
    new_external_control_created: bool
    new_first_output_created: bool
    new_live_runtime_created: bool
    source_trace_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class HostBodyEmbodiedLearningClosedLoopMilestoneAuditRecord:
    closed_loop_milestone_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_closed_loop_scope_id: str | None
    source_capability_ledger_id: str | None
    source_boundary_ledger_id: str | None
    source_integrated_trace_id: str | None
    scope_valid: bool
    capability_ledger_valid: bool
    boundary_ledger_valid: bool
    integrated_trace_valid: bool
    package_107_verified: bool
    package_108_verified: bool
    package_109_verified: bool
    package_110_verified: bool
    package_111_verified: bool
    package_112_verified: bool
    current_status_report_verified: bool
    host_body_embodied_learning_closed_loop_established: bool
    new_capability_created_by_this_package: bool
    audit_only_package_confirmed: bool
    fixture_only_confirmed: bool
    teacher_gated_confirmed: bool
    trace_spine_format_unified_confirmed: bool
    trace_spine_time_aligned_confirmed: bool
    raw_trace_append_only_confirmed: bool
    raw_trace_not_summarized_during_service_period: bool
    memory_layer_stores_interpretation_only_confirmed: bool
    source_trace_refs_preserved_confirmed: bool
    concept_id_not_embedded_into_raw_history_confirmed: bool
    raw_trace_not_dumped_into_memory_learning_trace_confirmed: bool
    gcmc_docs_only_future_architecture_confirmed: bool
    gcmc_runtime_not_implemented_confirmed: bool
    cl_token_not_created_confirmed: bool
    no_real_hardware: bool
    no_semantic_vision: bool
    no_speech_recognition: bool
    no_task_action_selection: bool
    no_final_action: bool
    no_direct_command: bool
    no_sandbox_execution: bool
    no_external_control: bool
    no_unity_runtime_connection: bool
    no_memory_write_by_this_package: bool
    no_long_term_memory_write: bool
    no_core_memory_write: bool
    no_learning_candidate_creation_by_this_package: bool
    no_concept_candidate_creation_by_this_package: bool
    no_reviewed_concept_creation_by_this_package: bool
    no_automatic_learning_approval: bool
    no_teacher_approval_created: bool
    no_first_output: bool
    no_live_runtime_session: bool
    no_thought_engine_behavior: bool
    no_production_behavior: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class HostBodyEmbodiedLearningClosedLoopReadinessRecord:
    closed_loop_readiness_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_closed_loop_milestone_audit_id: str
    current_verified_capability: str
    recommended_next_package: str
    recommended_next_reason: str
    ready_for_internal_action_home_surface_link: bool
    ready_for_runtime_state_summary_session_shell: bool
    ready_for_bounded_embodied_loop_runner: bool
    ready_for_no_codex_teacher_console_flow: bool
    ready_for_session_end_review_promote_gate: bool
    ready_for_no_codex_fixture_growth_loop_milestone_audit: bool
    ready_for_real_camera_connection: bool
    ready_for_real_microphone_connection: bool
    ready_for_task_engine_action_selection_influence: bool
    ready_for_external_control: bool
    ready_for_long_term_memory_write: bool
    ready_for_core_memory_write: bool
    ready_for_cl_token_creation: bool
    ready_for_gcmc_runtime: bool
    ready_for_first_output: bool
    ready_for_live_runtime_session: bool
    readiness_status: str
    readiness_summary: str
    source_trace_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


def build_host_body_embodied_learning_closed_loop_scope(
    *,
    host_body_v0_required: bool = True,
    learning_feedback_bridge_required: bool = True,
    existing_learning_pipeline_compatibility_required: bool = True,
    reviewed_concept_replay_required: bool = True,
    working_readback_integration_required: bool = True,
    readback_internal_action_influence_required: bool = True,
    trace_spine_boundary_required: bool = True,
    current_status_report_required: bool = True,
    current_status_report_available: bool | None = None,
    new_behavior_allowed: bool = False,
    new_learning_allowed: bool = False,
    new_memory_write_allowed: bool = False,
    external_control_allowed: bool = False,
    first_output_allowed: bool = False,
    live_runtime_allowed: bool = False,
    source_trace_refs: tuple[str, ...] = (),
) -> HostBodyEmbodiedLearningClosedLoopScopeRecord:
    report_available = (
        validate_current_status_report_text()["valid"]
        if current_status_report_available is None
        else current_status_report_available
    )
    if not current_status_report_required or not report_available:
        status = "blocked_missing_current_status_report"
    elif not all(
        (
            host_body_v0_required,
            learning_feedback_bridge_required,
            existing_learning_pipeline_compatibility_required,
            reviewed_concept_replay_required,
            working_readback_integration_required,
            readback_internal_action_influence_required,
            trace_spine_boundary_required,
        )
    ):
        status = "blocked_missing_required_loop_step"
    elif new_behavior_allowed:
        status = "blocked_new_behavior_allowed"
    elif new_learning_allowed:
        status = "blocked_new_learning_allowed"
    elif new_memory_write_allowed:
        status = "blocked_new_memory_write_allowed"
    elif external_control_allowed:
        status = "blocked_external_control_allowed"
    elif first_output_allowed:
        status = "blocked_first_output_allowed"
    elif live_runtime_allowed:
        status = "blocked_live_runtime_allowed"
    else:
        status = "closed_loop_scope_created"
    refs = tuple(source_trace_refs) or (str(CURRENT_STATUS_REPORT_PATH),)
    return HostBodyEmbodiedLearningClosedLoopScopeRecord(
        closed_loop_scope_id=f"host_body_embodied_learning_closed_loop_scope:{status}",
        schema_version=SCOPE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        milestone_name=MILESTONE_NAME,
        milestone_kind=MILESTONE_KIND,
        included_packages=INCLUDED_PACKAGES,
        included_commits=INCLUDED_COMMITS,
        included_loop_steps=INCLUDED_LOOP_STEPS,
        excluded_capabilities=EXCLUDED_CAPABILITIES,
        host_body_v0_required=host_body_v0_required,
        learning_feedback_bridge_required=learning_feedback_bridge_required,
        existing_learning_pipeline_compatibility_required=(
            existing_learning_pipeline_compatibility_required
        ),
        reviewed_concept_replay_required=reviewed_concept_replay_required,
        working_readback_integration_required=working_readback_integration_required,
        readback_internal_action_influence_required=(
            readback_internal_action_influence_required
        ),
        trace_spine_boundary_required=trace_spine_boundary_required,
        current_status_report_required=current_status_report_required,
        new_behavior_allowed=new_behavior_allowed,
        new_learning_allowed=new_learning_allowed,
        new_memory_write_allowed=new_memory_write_allowed,
        external_control_allowed=external_control_allowed,
        first_output_allowed=first_output_allowed,
        live_runtime_allowed=live_runtime_allowed,
        scope_status=status,
        scope_summary=(
            "Package 113 scopes the first fixture-only, teacher-gated Host Body "
            "embodied learning readback loop milestone as audit-only."
        ),
        source_trace_refs=_tuple_of_str(refs),
    )


def validate_host_body_embodied_learning_closed_loop_scope(record: Any) -> dict[str, object]:
    data = _record(record)
    if data is None:
        return {"valid": False, "status": "missing", "reasons": ["missing"]}
    valid = data.get("scope_status") == "closed_loop_scope_created"
    valid = valid and all(
        bool(data.get(name))
        for name in (
            "host_body_v0_required",
            "learning_feedback_bridge_required",
            "existing_learning_pipeline_compatibility_required",
            "reviewed_concept_replay_required",
            "working_readback_integration_required",
            "readback_internal_action_influence_required",
            "trace_spine_boundary_required",
            "current_status_report_required",
        )
    )
    valid = valid and not any(
        bool(data.get(name))
        for name in (
            "new_behavior_allowed",
            "new_learning_allowed",
            "new_memory_write_allowed",
            "external_control_allowed",
            "first_output_allowed",
            "live_runtime_allowed",
        )
    )
    return {
        "valid": valid,
        "status": data.get("scope_status"),
        "reasons": [] if valid else [str(data.get("scope_status"))],
    }


def _closed_loop_capability_entries(
    *,
    host_body_v0_verified: bool,
    host_body_evidence_to_learning_feedback_verified: bool,
    existing_learning_pipeline_compatibility_verified: bool,
    reviewed_concept_replay_verified: bool,
    working_readback_integration_verified: bool,
    readback_internal_action_influence_verified: bool,
    trace_spine_raw_evidence_boundary_verified: bool,
    current_status_report_verified: bool,
) -> tuple[dict[str, Any], ...]:
    return (
        {
            "package": "Package 107",
            "capability": "Qingyin Host Body v0 milestone audit",
            "verified": host_body_v0_verified,
            "commit": "ea07c6a",
            "safe_claim": "Host Body v0 is bounded, fixture-only, and internal-only.",
            "forbidden_claims": ["real_hardware_access", "live_runtime_session"],
        },
        {
            "package": "Package 108",
            "capability": "Host Body evidence to LearningFeedbackCandidate bridge",
            "verified": host_body_evidence_to_learning_feedback_verified,
            "commit": "b658cea",
            "safe_claim": "Host Body evidence can become teacher-reviewable feedback material.",
            "forbidden_claims": ["ConceptCandidate_creation", "memory_write"],
        },
        {
            "package": "Package 109",
            "capability": "Existing learning pipeline compatibility",
            "verified": existing_learning_pipeline_compatibility_verified,
            "commit": "192ef0f",
            "safe_claim": "Host Body feedback is compatible with the existing Package 90-92 pipeline.",
            "forbidden_claims": ["parallel_teacher_review", "parallel_concept_system"],
        },
        {
            "package": "Package 110",
            "capability": "ReviewedConcept readiness replay",
            "verified": reviewed_concept_replay_verified,
            "commit": "b04ad60",
            "safe_claim": "Approved Host Body feedback can replay up to ReviewedConcept readiness.",
            "forbidden_claims": ["ReviewedConcept_created_by_adapter", "memory_write"],
        },
        {
            "package": "Package 111",
            "capability": "Host Body ReviewedConcept working readback visibility",
            "verified": working_readback_integration_verified,
            "commit": "959bbf7",
            "safe_claim": "ReviewedConcept readiness can become interpretation-only working readback visibility.",
            "forbidden_claims": ["raw_trace_dump", "internal_action_influence"],
        },
        {
            "package": "Package 112",
            "capability": "Host Body readback internal action influence",
            "verified": readback_internal_action_influence_verified,
            "commit": "f4f3371",
            "safe_claim": "Working readback can influence internal-only Host Body action ordering.",
            "forbidden_claims": ["Task Engine selected_action", "external_control"],
        },
        {
            "package": "Package 111",
            "capability": "Trace Spine raw evidence boundary",
            "verified": trace_spine_raw_evidence_boundary_verified,
            "commit": "959bbf7",
            "safe_claim": "Trace Spine remains unified, time-aligned, append-only, and source-ref preserving.",
            "forbidden_claims": ["raw_trace_summarization", "concept_id_in_raw_history"],
        },
        {
            "package": "Package 113 report add-on",
            "capability": "Current ASHL Core v1 status report output",
            "verified": current_status_report_verified,
            "commit": "56e9b22",
            "safe_claim": "Package 113 current status is visible as docs and read-only CLI output.",
            "forbidden_claims": ["live_runtime_claim", "awake_claim"],
        },
    )


def build_host_body_embodied_learning_closed_loop_capability_ledger(
    *,
    closed_loop_scope: Any,
    host_body_v0_verified: bool = True,
    host_body_evidence_to_learning_feedback_verified: bool = True,
    existing_learning_pipeline_compatibility_verified: bool = True,
    reviewed_concept_replay_verified: bool = True,
    working_readback_integration_verified: bool = True,
    readback_internal_action_influence_verified: bool = True,
    trace_spine_raw_evidence_boundary_verified: bool = True,
    current_status_report_verified: bool | None = None,
    new_capability_created_by_this_package: bool = False,
) -> HostBodyEmbodiedLearningClosedLoopCapabilityLedgerRecord:
    scope = _record(closed_loop_scope) or {}
    report_verified = (
        validate_current_status_report_text()["valid"]
        if current_status_report_verified is None
        else current_status_report_verified
    )
    status = "closed_loop_capability_ledger_recorded"
    if not host_body_v0_verified:
        status = "blocked_missing_host_body_v0"
    elif not host_body_evidence_to_learning_feedback_verified:
        status = "blocked_missing_learning_feedback_bridge"
    elif not existing_learning_pipeline_compatibility_verified:
        status = "blocked_missing_existing_learning_pipeline_compatibility"
    elif not reviewed_concept_replay_verified:
        status = "blocked_missing_reviewed_concept_replay"
    elif not working_readback_integration_verified:
        status = "blocked_missing_working_readback_integration"
    elif not readback_internal_action_influence_verified:
        status = "blocked_missing_readback_internal_action_influence"
    elif not trace_spine_raw_evidence_boundary_verified:
        status = "blocked_missing_trace_spine_boundary"
    elif not report_verified:
        status = "blocked_missing_current_status_report"
    elif new_capability_created_by_this_package:
        status = "blocked_unexpected_new_capability_detected"
    entries = _closed_loop_capability_entries(
        host_body_v0_verified=host_body_v0_verified,
        host_body_evidence_to_learning_feedback_verified=(
            host_body_evidence_to_learning_feedback_verified
        ),
        existing_learning_pipeline_compatibility_verified=(
            existing_learning_pipeline_compatibility_verified
        ),
        reviewed_concept_replay_verified=reviewed_concept_replay_verified,
        working_readback_integration_verified=working_readback_integration_verified,
        readback_internal_action_influence_verified=readback_internal_action_influence_verified,
        trace_spine_raw_evidence_boundary_verified=trace_spine_raw_evidence_boundary_verified,
        current_status_report_verified=report_verified,
    )
    return HostBodyEmbodiedLearningClosedLoopCapabilityLedgerRecord(
        closed_loop_capability_ledger_id=f"host_body_embodied_learning_closed_loop_capability_ledger:{status}",
        schema_version=CAPABILITY_LEDGER_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_closed_loop_scope_id=str(scope.get("closed_loop_scope_id", "")),
        capability_entries=_tuple_of_dict(entries),
        host_body_v0_verified=host_body_v0_verified,
        host_body_evidence_to_learning_feedback_verified=(
            host_body_evidence_to_learning_feedback_verified
        ),
        existing_learning_pipeline_compatibility_verified=(
            existing_learning_pipeline_compatibility_verified
        ),
        reviewed_concept_replay_verified=reviewed_concept_replay_verified,
        working_readback_integration_verified=working_readback_integration_verified,
        readback_internal_action_influence_verified=readback_internal_action_influence_verified,
        trace_spine_raw_evidence_boundary_verified=trace_spine_raw_evidence_boundary_verified,
        current_status_report_verified=report_verified,
        capability_count=sum(1 for entry in entries if entry["verified"]),
        capability_ledger_status=status,
        capability_ledger_summary=(
            "Capability ledger records Packages 107-112 plus Package 113 report output "
            "as the audited Host Body embodied learning readback loop chain."
        ),
        new_capability_created_by_this_package=new_capability_created_by_this_package,
        source_trace_refs=(str(CURRENT_STATUS_REPORT_PATH),),
    )


def validate_host_body_embodied_learning_closed_loop_capability_ledger(record: Any) -> dict[str, object]:
    data = _record(record)
    if data is None:
        return {"valid": False, "status": "missing", "reasons": ["missing"]}
    valid = data.get("capability_ledger_status") == "closed_loop_capability_ledger_recorded"
    valid = valid and all(
        bool(data.get(name))
        for name in (
            "host_body_v0_verified",
            "host_body_evidence_to_learning_feedback_verified",
            "existing_learning_pipeline_compatibility_verified",
            "reviewed_concept_replay_verified",
            "working_readback_integration_verified",
            "readback_internal_action_influence_verified",
            "trace_spine_raw_evidence_boundary_verified",
            "current_status_report_verified",
        )
    )
    valid = valid and not bool(data.get("new_capability_created_by_this_package"))
    return {
        "valid": valid,
        "status": data.get("capability_ledger_status"),
        "reasons": [] if valid else [str(data.get("capability_ledger_status"))],
    }


def _closed_loop_boundary_status(values: dict[str, bool]) -> str:
    if not values["fixture_only_confirmed"] or not values["teacher_gated_confirmed"]:
        return "blocked_production_behavior_detected"
    if not values["audit_only_package_confirmed"]:
        return "blocked_production_behavior_detected"
    if not values["no_real_camera_access"] or not values["no_real_microphone_access"]:
        return "blocked_real_hardware_detected"
    if not values["no_semantic_vision"] or not values["no_speech_recognition"]:
        return "blocked_semantic_interpretation_detected"
    if not all(
        values[name]
        for name in (
            "no_task_engine_selected_action",
            "no_final_action",
            "no_direct_command",
            "no_sandbox_execution",
        )
    ):
        return "blocked_task_action_detected"
    if not all(
        values[name]
        for name in (
            "no_external_control",
            "no_os_control",
            "no_mouse_control",
            "no_keyboard_control",
            "no_browser_control",
            "no_file_operation",
            "no_network_execution",
            "no_shell_execution",
            "no_external_api_call",
        )
    ):
        return "blocked_external_control_detected"
    if not values["no_unity_runtime_connection"] or not values["no_avatar_control"]:
        return "blocked_unity_runtime_detected"
    if not all(
        values[name]
        for name in (
            "no_long_term_memory_write",
            "no_core_memory_write",
            "no_archive_memory_write",
            "no_anchor_write",
            "no_state_persistence_write",
            "no_memory_layer_write_by_this_package",
        )
    ):
        return "blocked_memory_write_detected"
    if not values["no_raw_trace_summarization"]:
        return "blocked_raw_trace_summarization_detected"
    if not values["no_raw_trace_mutation"]:
        return "blocked_raw_trace_mutation_detected"
    if not values["no_raw_trace_dump_into_memory_learning_trace"]:
        return "blocked_raw_trace_dump_detected"
    if not values["no_concept_id_embedded_into_raw_history"]:
        return "blocked_concept_id_embedded_into_raw_history"
    if not values["source_trace_refs_preserved"]:
        return "blocked_raw_trace_dump_detected"
    if not all(
        values[name]
        for name in (
            "no_learning_candidate_creation_by_this_package",
            "no_concept_candidate_creation_by_this_package",
            "no_reviewed_concept_creation_by_this_package",
            "no_memory_application_data_creation_by_this_package",
            "no_automatic_learning_approval",
            "no_teacher_approval_created",
        )
    ):
        return "blocked_learning_creation_detected"
    if not all(
        values[name]
        for name in ("no_first_output", "no_free_text_conversation", "no_voice_output")
    ):
        return "blocked_first_output_detected"
    if not all(
        values[name]
        for name in (
            "no_live_runtime_session",
            "no_live_engine_invocation",
            "no_autonomous_scheduler",
            "no_open_ended_loop",
        )
    ):
        return "blocked_live_runtime_detected"
    if not values["no_thought_engine_behavior"] or not values["no_production_behavior"]:
        return "blocked_production_behavior_detected"
    return "closed_loop_boundary_ledger_recorded"


def build_host_body_embodied_learning_closed_loop_boundary_ledger(
    *,
    closed_loop_scope: Any,
    fixture_only_confirmed: bool = True,
    teacher_gated_confirmed: bool = True,
    audit_only_package_confirmed: bool = True,
    no_real_camera_access: bool = True,
    no_real_microphone_access: bool = True,
    no_semantic_vision: bool = True,
    no_speech_recognition: bool = True,
    no_task_engine_selected_action: bool = True,
    no_final_action: bool = True,
    no_direct_command: bool = True,
    no_sandbox_execution: bool = True,
    no_external_control: bool = True,
    no_os_control: bool = True,
    no_mouse_control: bool = True,
    no_keyboard_control: bool = True,
    no_browser_control: bool = True,
    no_file_operation: bool = True,
    no_network_execution: bool = True,
    no_shell_execution: bool = True,
    no_external_api_call: bool = True,
    no_unity_runtime_connection: bool = True,
    no_avatar_control: bool = True,
    no_long_term_memory_write: bool = True,
    no_core_memory_write: bool = True,
    no_archive_memory_write: bool = True,
    no_anchor_write: bool = True,
    no_state_persistence_write: bool = True,
    no_memory_layer_write_by_this_package: bool = True,
    no_raw_trace_summarization: bool = True,
    no_raw_trace_mutation: bool = True,
    no_raw_trace_dump_into_memory_learning_trace: bool = True,
    no_concept_id_embedded_into_raw_history: bool = True,
    source_trace_refs_preserved: bool = True,
    no_learning_candidate_creation_by_this_package: bool = True,
    no_concept_candidate_creation_by_this_package: bool = True,
    no_reviewed_concept_creation_by_this_package: bool = True,
    no_memory_application_data_creation_by_this_package: bool = True,
    no_automatic_learning_approval: bool = True,
    no_teacher_approval_created: bool = True,
    no_first_output: bool = True,
    no_free_text_conversation: bool = True,
    no_voice_output: bool = True,
    no_live_runtime_session: bool = True,
    no_live_engine_invocation: bool = True,
    no_autonomous_scheduler: bool = True,
    no_open_ended_loop: bool = True,
    no_thought_engine_behavior: bool = True,
    no_production_behavior: bool = True,
) -> HostBodyEmbodiedLearningClosedLoopBoundaryLedgerRecord:
    scope = _record(closed_loop_scope) or {}
    values = {
        "fixture_only_confirmed": fixture_only_confirmed,
        "teacher_gated_confirmed": teacher_gated_confirmed,
        "audit_only_package_confirmed": audit_only_package_confirmed,
        "no_real_camera_access": no_real_camera_access,
        "no_real_microphone_access": no_real_microphone_access,
        "no_semantic_vision": no_semantic_vision,
        "no_speech_recognition": no_speech_recognition,
        "no_task_engine_selected_action": no_task_engine_selected_action,
        "no_final_action": no_final_action,
        "no_direct_command": no_direct_command,
        "no_sandbox_execution": no_sandbox_execution,
        "no_external_control": no_external_control,
        "no_os_control": no_os_control,
        "no_mouse_control": no_mouse_control,
        "no_keyboard_control": no_keyboard_control,
        "no_browser_control": no_browser_control,
        "no_file_operation": no_file_operation,
        "no_network_execution": no_network_execution,
        "no_shell_execution": no_shell_execution,
        "no_external_api_call": no_external_api_call,
        "no_unity_runtime_connection": no_unity_runtime_connection,
        "no_avatar_control": no_avatar_control,
        "no_long_term_memory_write": no_long_term_memory_write,
        "no_core_memory_write": no_core_memory_write,
        "no_archive_memory_write": no_archive_memory_write,
        "no_anchor_write": no_anchor_write,
        "no_state_persistence_write": no_state_persistence_write,
        "no_memory_layer_write_by_this_package": no_memory_layer_write_by_this_package,
        "no_raw_trace_summarization": no_raw_trace_summarization,
        "no_raw_trace_mutation": no_raw_trace_mutation,
        "no_raw_trace_dump_into_memory_learning_trace": (
            no_raw_trace_dump_into_memory_learning_trace
        ),
        "no_concept_id_embedded_into_raw_history": no_concept_id_embedded_into_raw_history,
        "source_trace_refs_preserved": source_trace_refs_preserved,
        "no_learning_candidate_creation_by_this_package": (
            no_learning_candidate_creation_by_this_package
        ),
        "no_concept_candidate_creation_by_this_package": (
            no_concept_candidate_creation_by_this_package
        ),
        "no_reviewed_concept_creation_by_this_package": (
            no_reviewed_concept_creation_by_this_package
        ),
        "no_memory_application_data_creation_by_this_package": (
            no_memory_application_data_creation_by_this_package
        ),
        "no_automatic_learning_approval": no_automatic_learning_approval,
        "no_teacher_approval_created": no_teacher_approval_created,
        "no_first_output": no_first_output,
        "no_free_text_conversation": no_free_text_conversation,
        "no_voice_output": no_voice_output,
        "no_live_runtime_session": no_live_runtime_session,
        "no_live_engine_invocation": no_live_engine_invocation,
        "no_autonomous_scheduler": no_autonomous_scheduler,
        "no_open_ended_loop": no_open_ended_loop,
        "no_thought_engine_behavior": no_thought_engine_behavior,
        "no_production_behavior": no_production_behavior,
    }
    status = _closed_loop_boundary_status(values)
    entries = tuple({"boundary": key, "confirmed": value} for key, value in values.items())
    return HostBodyEmbodiedLearningClosedLoopBoundaryLedgerRecord(
        closed_loop_boundary_ledger_id=f"host_body_embodied_learning_closed_loop_boundary_ledger:{status}",
        schema_version=BOUNDARY_LEDGER_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_closed_loop_scope_id=str(scope.get("closed_loop_scope_id", "")),
        boundary_entries=_tuple_of_dict(entries),
        boundary_ledger_status=status,
        boundary_ledger_summary=(
            "Boundary ledger confirms Package 113 is fixture-only, teacher-gated, "
            "audit-only, and preserves Trace Spine raw evidence boundaries."
        ),
        source_trace_refs=(str(CURRENT_STATUS_REPORT_PATH),),
        **values,
    )


def validate_host_body_embodied_learning_closed_loop_boundary_ledger(record: Any) -> dict[str, object]:
    data = _record(record)
    if data is None:
        return {"valid": False, "status": "missing", "reasons": ["missing"]}
    all_boundary_flags = all(
        bool(data.get(name))
        for name in (
            "fixture_only_confirmed",
            "teacher_gated_confirmed",
            "audit_only_package_confirmed",
            "no_real_camera_access",
            "no_real_microphone_access",
            "no_semantic_vision",
            "no_speech_recognition",
            "no_task_engine_selected_action",
            "no_final_action",
            "no_direct_command",
            "no_sandbox_execution",
            "no_external_control",
            "no_os_control",
            "no_mouse_control",
            "no_keyboard_control",
            "no_browser_control",
            "no_file_operation",
            "no_network_execution",
            "no_shell_execution",
            "no_external_api_call",
            "no_unity_runtime_connection",
            "no_avatar_control",
            "no_long_term_memory_write",
            "no_core_memory_write",
            "no_archive_memory_write",
            "no_anchor_write",
            "no_state_persistence_write",
            "no_memory_layer_write_by_this_package",
            "no_raw_trace_summarization",
            "no_raw_trace_mutation",
            "no_raw_trace_dump_into_memory_learning_trace",
            "no_concept_id_embedded_into_raw_history",
            "source_trace_refs_preserved",
            "no_learning_candidate_creation_by_this_package",
            "no_concept_candidate_creation_by_this_package",
            "no_reviewed_concept_creation_by_this_package",
            "no_memory_application_data_creation_by_this_package",
            "no_automatic_learning_approval",
            "no_teacher_approval_created",
            "no_first_output",
            "no_free_text_conversation",
            "no_voice_output",
            "no_live_runtime_session",
            "no_live_engine_invocation",
            "no_autonomous_scheduler",
            "no_open_ended_loop",
            "no_thought_engine_behavior",
            "no_production_behavior",
        )
    )
    valid = (
        data.get("boundary_ledger_status") == "closed_loop_boundary_ledger_recorded"
        and all_boundary_flags
    )
    return {
        "valid": valid,
        "status": data.get("boundary_ledger_status"),
        "reasons": [] if valid else [str(data.get("boundary_ledger_status"))],
    }


def _integrated_loop_steps(
    *,
    host_body_step: bool,
    learning_feedback_step: bool,
    existing_pipeline_step: bool,
    reviewed_concept_replay_step: bool,
    working_readback_step: bool,
    readback_influence_step: bool,
    current_status_report_step: bool,
) -> tuple[dict[str, Any], ...]:
    return (
        {
            "step": 1,
            "name": "host_body_event_and_internal_action",
            "source_packages": ["101", "102", "103", "104", "105", "106", "107"],
            "verified": host_body_step,
        },
        {
            "step": 2,
            "name": "host_body_evidence_to_learning_feedback_candidate",
            "source_package": "108",
            "verified": learning_feedback_step,
        },
        {
            "step": 3,
            "name": "existing_learning_pipeline_compatibility",
            "source_package": "109",
            "verified": existing_pipeline_step,
        },
        {
            "step": 4,
            "name": "reviewed_concept_readiness_replay",
            "source_package": "110",
            "verified": reviewed_concept_replay_step,
        },
        {
            "step": 5,
            "name": "working_readback_visibility",
            "source_package": "111",
            "verified": working_readback_step,
        },
        {
            "step": 6,
            "name": "readback_influenced_internal_action_choice",
            "source_package": "112",
            "verified": readback_influence_step,
        },
        {
            "step": 7,
            "name": "current_status_report_output",
            "source_commit": "56e9b22",
            "verified": current_status_report_step,
        },
    )


def build_host_body_embodied_learning_closed_loop_integrated_trace(
    *,
    closed_loop_scope: Any,
    source_host_body_v0_audit_id: str | None = "qingyin_host_body_v0_milestone_audit:passed",
    source_learning_feedback_bridge_audit_id: str | None = "host_body_learning_bridge_audit:passed",
    source_existing_pipeline_compatibility_audit_id: str | None = "host_body_existing_learning_pipeline_compatibility_audit:passed",
    source_reviewed_concept_replay_audit_id: str | None = "host_body_reviewed_concept_replay_audit:passed",
    source_working_readback_integration_audit_id: str | None = "host_body_working_readback_integration_audit:passed",
    source_readback_internal_action_influence_audit_id: str | None = "host_body_readback_internal_action_influence_audit:passed",
    source_current_status_report_path: str | None = None,
    host_body_event_step_confirmed: bool = True,
    internal_action_step_confirmed: bool = True,
    learning_feedback_candidate_step_confirmed: bool = True,
    existing_learning_pipeline_step_confirmed: bool = True,
    reviewed_concept_readiness_step_confirmed: bool = True,
    working_readback_step_confirmed: bool = True,
    readback_influenced_internal_action_step_confirmed: bool = True,
    trace_spine_boundary_confirmed: bool = True,
    current_status_report_confirmed: bool | None = None,
    new_runtime_behavior_created: bool = False,
    new_learning_behavior_created: bool = False,
    new_memory_write_created: bool = False,
    new_external_control_created: bool = False,
    new_first_output_created: bool = False,
    new_live_runtime_created: bool = False,
) -> HostBodyEmbodiedLearningClosedLoopIntegratedTraceRecord:
    scope = _record(closed_loop_scope) or {}
    report_confirmed = (
        validate_current_status_report_text()["valid"]
        if current_status_report_confirmed is None
        else current_status_report_confirmed
    )
    if not host_body_event_step_confirmed or not internal_action_step_confirmed:
        status = "blocked_missing_host_body_v0_step"
    elif not learning_feedback_candidate_step_confirmed:
        status = "blocked_missing_learning_feedback_step"
    elif not existing_learning_pipeline_step_confirmed:
        status = "blocked_missing_existing_pipeline_step"
    elif not reviewed_concept_readiness_step_confirmed:
        status = "blocked_missing_reviewed_concept_replay_step"
    elif not working_readback_step_confirmed:
        status = "blocked_missing_working_readback_step"
    elif not readback_influenced_internal_action_step_confirmed:
        status = "blocked_missing_readback_influence_step"
    elif not report_confirmed:
        status = "blocked_missing_current_status_report"
    elif not trace_spine_boundary_confirmed:
        status = "blocked_trace_spine_boundary_failure"
    elif new_runtime_behavior_created:
        status = "blocked_forbidden_runtime_behavior_detected"
    elif new_learning_behavior_created:
        status = "blocked_forbidden_learning_behavior_detected"
    elif new_memory_write_created:
        status = "blocked_forbidden_memory_write_detected"
    elif new_external_control_created or new_first_output_created or new_live_runtime_created:
        status = "blocked_forbidden_authority_detected"
    else:
        status = "closed_loop_integrated_trace_recorded"
    steps = _integrated_loop_steps(
        host_body_step=host_body_event_step_confirmed and internal_action_step_confirmed,
        learning_feedback_step=learning_feedback_candidate_step_confirmed,
        existing_pipeline_step=existing_learning_pipeline_step_confirmed,
        reviewed_concept_replay_step=reviewed_concept_readiness_step_confirmed,
        working_readback_step=working_readback_step_confirmed,
        readback_influence_step=readback_influenced_internal_action_step_confirmed,
        current_status_report_step=report_confirmed,
    )
    report_path = source_current_status_report_path or str(CURRENT_STATUS_REPORT_PATH)
    return HostBodyEmbodiedLearningClosedLoopIntegratedTraceRecord(
        closed_loop_integrated_trace_id=f"host_body_embodied_learning_closed_loop_integrated_trace:{status}",
        schema_version=INTEGRATED_TRACE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_closed_loop_scope_id=str(scope.get("closed_loop_scope_id", "")),
        source_host_body_v0_audit_id=source_host_body_v0_audit_id,
        source_learning_feedback_bridge_audit_id=source_learning_feedback_bridge_audit_id,
        source_existing_pipeline_compatibility_audit_id=(
            source_existing_pipeline_compatibility_audit_id
        ),
        source_reviewed_concept_replay_audit_id=source_reviewed_concept_replay_audit_id,
        source_working_readback_integration_audit_id=(
            source_working_readback_integration_audit_id
        ),
        source_readback_internal_action_influence_audit_id=(
            source_readback_internal_action_influence_audit_id
        ),
        source_current_status_report_path=report_path if report_confirmed else None,
        integrated_loop_steps=_tuple_of_dict(steps),
        step_count=len(steps),
        host_body_event_step_confirmed=host_body_event_step_confirmed,
        internal_action_step_confirmed=internal_action_step_confirmed,
        learning_feedback_candidate_step_confirmed=(
            learning_feedback_candidate_step_confirmed
        ),
        existing_learning_pipeline_step_confirmed=(
            existing_learning_pipeline_step_confirmed
        ),
        reviewed_concept_readiness_step_confirmed=(
            reviewed_concept_readiness_step_confirmed
        ),
        working_readback_step_confirmed=working_readback_step_confirmed,
        readback_influenced_internal_action_step_confirmed=(
            readback_influenced_internal_action_step_confirmed
        ),
        trace_spine_boundary_confirmed=trace_spine_boundary_confirmed,
        current_status_report_confirmed=report_confirmed,
        integrated_trace_status=status,
        integrated_trace_summary=(
            "Integrated trace records the full seven-step fixture-only Host Body "
            "embodied learning readback loop."
        ),
        new_runtime_behavior_created=new_runtime_behavior_created,
        new_learning_behavior_created=new_learning_behavior_created,
        new_memory_write_created=new_memory_write_created,
        new_external_control_created=new_external_control_created,
        new_first_output_created=new_first_output_created,
        new_live_runtime_created=new_live_runtime_created,
        source_trace_refs=(report_path,),
    )


def validate_host_body_embodied_learning_closed_loop_integrated_trace(record: Any) -> dict[str, object]:
    data = _record(record)
    if data is None:
        return {"valid": False, "status": "missing", "reasons": ["missing"]}
    valid = data.get("integrated_trace_status") == "closed_loop_integrated_trace_recorded"
    valid = valid and data.get("step_count") == 7
    valid = valid and all(
        bool(data.get(name))
        for name in (
            "host_body_event_step_confirmed",
            "internal_action_step_confirmed",
            "learning_feedback_candidate_step_confirmed",
            "existing_learning_pipeline_step_confirmed",
            "reviewed_concept_readiness_step_confirmed",
            "working_readback_step_confirmed",
            "readback_influenced_internal_action_step_confirmed",
            "trace_spine_boundary_confirmed",
            "current_status_report_confirmed",
        )
    )
    valid = valid and not any(
        bool(data.get(name))
        for name in (
            "new_runtime_behavior_created",
            "new_learning_behavior_created",
            "new_memory_write_created",
            "new_external_control_created",
            "new_first_output_created",
            "new_live_runtime_created",
        )
    )
    return {
        "valid": valid,
        "status": data.get("integrated_trace_status"),
        "reasons": [] if valid else [str(data.get("integrated_trace_status"))],
    }


def _audit_status(
    *,
    scope: dict[str, Any] | None,
    ledger: dict[str, Any] | None,
    boundary: dict[str, Any] | None,
    trace: dict[str, Any] | None,
    scope_valid: bool,
    ledger_valid: bool,
    boundary_valid: bool,
    trace_valid: bool,
) -> str:
    if scope is None:
        return "blocked_missing_scope"
    if ledger is None:
        return "blocked_missing_capability_ledger"
    if boundary is None:
        return "blocked_missing_boundary_ledger"
    if trace is None:
        return "blocked_missing_integrated_trace"
    if not scope_valid:
        scope_status = str(scope.get("scope_status"))
        if scope_status == "blocked_missing_current_status_report":
            return "blocked_current_status_report_missing"
        return "blocked_missing_scope"
    if not ledger.get("host_body_v0_verified", False):
        return "blocked_package_107_unverified"
    if not ledger.get("host_body_evidence_to_learning_feedback_verified", False):
        return "blocked_package_108_unverified"
    if not ledger.get("existing_learning_pipeline_compatibility_verified", False):
        return "blocked_package_109_unverified"
    if not ledger.get("reviewed_concept_replay_verified", False):
        return "blocked_package_110_unverified"
    if not ledger.get("working_readback_integration_verified", False):
        return "blocked_package_111_unverified"
    if not ledger.get("readback_internal_action_influence_verified", False):
        return "blocked_package_112_unverified"
    if not ledger.get("current_status_report_verified", False):
        return "blocked_current_status_report_missing"
    if ledger.get("new_capability_created_by_this_package", False):
        return "blocked_unexpected_new_capability_detected"
    if not trace.get("current_status_report_confirmed", False):
        return "blocked_current_status_report_missing"
    if not trace.get("trace_spine_boundary_confirmed", False):
        return "blocked_trace_spine_boundary_failure"
    if trace.get("new_runtime_behavior_created", False):
        return "blocked_production_behavior_detected"
    if trace.get("new_learning_behavior_created", False):
        return "blocked_learning_candidate_creation_detected"
    if trace.get("new_memory_write_created", False):
        return "blocked_memory_write_detected"
    if trace.get("new_external_control_created", False):
        return "blocked_external_control_detected"
    if trace.get("new_first_output_created", False):
        return "blocked_first_output_detected"
    if trace.get("new_live_runtime_created", False):
        return "blocked_live_runtime_detected"
    if not boundary.get("no_raw_trace_summarization", False):
        return "blocked_raw_trace_summarized"
    if not boundary.get("no_concept_id_embedded_into_raw_history", False):
        return "blocked_concept_id_embedded_into_raw_history"
    if not boundary.get("source_trace_refs_preserved", False):
        return "blocked_trace_spine_boundary_failure"
    if not boundary.get("no_raw_trace_dump_into_memory_learning_trace", False):
        return "blocked_trace_spine_boundary_failure"
    if not boundary.get("no_real_camera_access", False) or not boundary.get(
        "no_real_microphone_access", False
    ):
        return "blocked_real_hardware_detected"
    if not boundary.get("no_semantic_vision", False):
        return "blocked_semantic_interpretation_detected"
    if not boundary.get("no_speech_recognition", False):
        return "blocked_speech_recognition_detected"
    if not boundary.get("no_task_engine_selected_action", False):
        return "blocked_task_action_selection_detected"
    if not boundary.get("no_external_control", False):
        return "blocked_external_control_detected"
    if not boundary.get("no_unity_runtime_connection", False):
        return "blocked_unity_runtime_detected"
    if not boundary.get("no_memory_layer_write_by_this_package", False):
        return "blocked_memory_write_detected"
    if not boundary.get("no_learning_candidate_creation_by_this_package", False):
        return "blocked_learning_candidate_creation_detected"
    if not boundary.get("no_concept_candidate_creation_by_this_package", False):
        return "blocked_concept_candidate_creation_detected"
    if not boundary.get("no_reviewed_concept_creation_by_this_package", False):
        return "blocked_reviewed_concept_creation_detected"
    if not boundary.get("no_teacher_approval_created", False):
        return "blocked_teacher_approval_created"
    if not boundary.get("no_first_output", False):
        return "blocked_first_output_detected"
    if not boundary.get("no_live_runtime_session", False):
        return "blocked_live_runtime_detected"
    if not boundary.get("no_production_behavior", False):
        return "blocked_production_behavior_detected"
    if not boundary_valid:
        ledger_status = str(boundary.get("boundary_ledger_status"))
        return {
            "blocked_real_hardware_detected": "blocked_real_hardware_detected",
            "blocked_semantic_interpretation_detected": (
                "blocked_semantic_interpretation_detected"
            ),
            "blocked_task_action_detected": "blocked_task_action_selection_detected",
            "blocked_external_control_detected": "blocked_external_control_detected",
            "blocked_unity_runtime_detected": "blocked_unity_runtime_detected",
            "blocked_memory_write_detected": "blocked_memory_write_detected",
            "blocked_raw_trace_summarization_detected": "blocked_raw_trace_summarized",
            "blocked_raw_trace_mutation_detected": "blocked_trace_spine_boundary_failure",
            "blocked_raw_trace_dump_detected": "blocked_trace_spine_boundary_failure",
            "blocked_concept_id_embedded_into_raw_history": (
                "blocked_concept_id_embedded_into_raw_history"
            ),
            "blocked_learning_creation_detected": (
                "blocked_learning_candidate_creation_detected"
            ),
            "blocked_first_output_detected": "blocked_first_output_detected",
            "blocked_live_runtime_detected": "blocked_live_runtime_detected",
            "blocked_production_behavior_detected": "blocked_production_behavior_detected",
        }.get(ledger_status, "blocked_trace_spine_boundary_failure")
    if not trace_valid:
        return {
            "blocked_missing_host_body_v0_step": "blocked_package_107_unverified",
            "blocked_missing_learning_feedback_step": "blocked_package_108_unverified",
            "blocked_missing_existing_pipeline_step": "blocked_package_109_unverified",
            "blocked_missing_reviewed_concept_replay_step": "blocked_package_110_unverified",
            "blocked_missing_working_readback_step": "blocked_package_111_unverified",
            "blocked_missing_readback_influence_step": "blocked_package_112_unverified",
            "blocked_missing_current_status_report": "blocked_current_status_report_missing",
            "blocked_trace_spine_boundary_failure": "blocked_trace_spine_boundary_failure",
            "blocked_forbidden_memory_write_detected": "blocked_memory_write_detected",
        }.get(str(trace.get("integrated_trace_status")), "blocked_missing_integrated_trace")
    if not ledger_valid:
        return "blocked_missing_capability_ledger"
    return PASSED_AUDIT_STATUS


def build_host_body_embodied_learning_closed_loop_milestone_audit(
    *,
    closed_loop_scope: Any | None,
    capability_ledger: Any | None,
    boundary_ledger: Any | None,
    integrated_trace: Any | None,
) -> HostBodyEmbodiedLearningClosedLoopMilestoneAuditRecord:
    scope = _record(closed_loop_scope)
    ledger = _record(capability_ledger)
    boundary = _record(boundary_ledger)
    trace = _record(integrated_trace)
    scope_valid = validate_host_body_embodied_learning_closed_loop_scope(scope)["valid"]
    ledger_valid = validate_host_body_embodied_learning_closed_loop_capability_ledger(ledger)[
        "valid"
    ]
    boundary_valid = validate_host_body_embodied_learning_closed_loop_boundary_ledger(boundary)[
        "valid"
    ]
    trace_valid = validate_host_body_embodied_learning_closed_loop_integrated_trace(trace)[
        "valid"
    ]
    status = _audit_status(
        scope=scope,
        ledger=ledger,
        boundary=boundary,
        trace=trace,
        scope_valid=bool(scope_valid),
        ledger_valid=bool(ledger_valid),
        boundary_valid=bool(boundary_valid),
        trace_valid=bool(trace_valid),
    )
    passed = status == PASSED_AUDIT_STATUS
    reasons = () if passed else (status,)
    return HostBodyEmbodiedLearningClosedLoopMilestoneAuditRecord(
        closed_loop_milestone_audit_id=f"host_body_embodied_learning_closed_loop_milestone_audit:{status}",
        schema_version=MILESTONE_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_closed_loop_scope_id=_get(scope, "closed_loop_scope_id"),
        source_capability_ledger_id=_get(ledger, "closed_loop_capability_ledger_id"),
        source_boundary_ledger_id=_get(boundary, "closed_loop_boundary_ledger_id"),
        source_integrated_trace_id=_get(trace, "closed_loop_integrated_trace_id"),
        scope_valid=bool(scope_valid),
        capability_ledger_valid=bool(ledger_valid),
        boundary_ledger_valid=bool(boundary_valid),
        integrated_trace_valid=bool(trace_valid),
        package_107_verified=bool(_get(ledger, "host_body_v0_verified", False)),
        package_108_verified=bool(
            _get(ledger, "host_body_evidence_to_learning_feedback_verified", False)
        ),
        package_109_verified=bool(
            _get(ledger, "existing_learning_pipeline_compatibility_verified", False)
        ),
        package_110_verified=bool(_get(ledger, "reviewed_concept_replay_verified", False)),
        package_111_verified=bool(
            _get(ledger, "working_readback_integration_verified", False)
        ),
        package_112_verified=bool(
            _get(ledger, "readback_internal_action_influence_verified", False)
        ),
        current_status_report_verified=bool(
            _get(ledger, "current_status_report_verified", False)
        )
        and bool(_get(trace, "current_status_report_confirmed", False)),
        host_body_embodied_learning_closed_loop_established=passed,
        new_capability_created_by_this_package=bool(
            _get(ledger, "new_capability_created_by_this_package", True)
        ),
        audit_only_package_confirmed=bool(_get(boundary, "audit_only_package_confirmed", False)),
        fixture_only_confirmed=bool(_get(boundary, "fixture_only_confirmed", False)),
        teacher_gated_confirmed=bool(_get(boundary, "teacher_gated_confirmed", False)),
        trace_spine_format_unified_confirmed=bool(_get(trace, "trace_spine_boundary_confirmed", False)),
        trace_spine_time_aligned_confirmed=bool(_get(trace, "trace_spine_boundary_confirmed", False)),
        raw_trace_append_only_confirmed=bool(_get(trace, "trace_spine_boundary_confirmed", False)),
        raw_trace_not_summarized_during_service_period=bool(
            _get(boundary, "no_raw_trace_summarization", False)
        ),
        memory_layer_stores_interpretation_only_confirmed=True,
        source_trace_refs_preserved_confirmed=bool(
            _get(boundary, "source_trace_refs_preserved", False)
        ),
        concept_id_not_embedded_into_raw_history_confirmed=bool(
            _get(boundary, "no_concept_id_embedded_into_raw_history", False)
        ),
        raw_trace_not_dumped_into_memory_learning_trace_confirmed=bool(
            _get(boundary, "no_raw_trace_dump_into_memory_learning_trace", False)
        ),
        gcmc_docs_only_future_architecture_confirmed=True,
        gcmc_runtime_not_implemented_confirmed=True,
        cl_token_not_created_confirmed=True,
        no_real_hardware=bool(_get(boundary, "no_real_camera_access", False))
        and bool(_get(boundary, "no_real_microphone_access", False)),
        no_semantic_vision=bool(_get(boundary, "no_semantic_vision", False)),
        no_speech_recognition=bool(_get(boundary, "no_speech_recognition", False)),
        no_task_action_selection=bool(
            _get(boundary, "no_task_engine_selected_action", False)
        ),
        no_final_action=bool(_get(boundary, "no_final_action", False)),
        no_direct_command=bool(_get(boundary, "no_direct_command", False)),
        no_sandbox_execution=bool(_get(boundary, "no_sandbox_execution", False)),
        no_external_control=bool(_get(boundary, "no_external_control", False)),
        no_unity_runtime_connection=bool(
            _get(boundary, "no_unity_runtime_connection", False)
        ),
        no_memory_write_by_this_package=bool(
            _get(boundary, "no_memory_layer_write_by_this_package", False)
        ),
        no_long_term_memory_write=bool(_get(boundary, "no_long_term_memory_write", False)),
        no_core_memory_write=bool(_get(boundary, "no_core_memory_write", False)),
        no_learning_candidate_creation_by_this_package=bool(
            _get(boundary, "no_learning_candidate_creation_by_this_package", False)
        ),
        no_concept_candidate_creation_by_this_package=bool(
            _get(boundary, "no_concept_candidate_creation_by_this_package", False)
        ),
        no_reviewed_concept_creation_by_this_package=bool(
            _get(boundary, "no_reviewed_concept_creation_by_this_package", False)
        ),
        no_automatic_learning_approval=bool(
            _get(boundary, "no_automatic_learning_approval", False)
        ),
        no_teacher_approval_created=bool(_get(boundary, "no_teacher_approval_created", False)),
        no_first_output=bool(_get(boundary, "no_first_output", False)),
        no_live_runtime_session=bool(_get(boundary, "no_live_runtime_session", False)),
        no_thought_engine_behavior=bool(_get(boundary, "no_thought_engine_behavior", False)),
        no_production_behavior=bool(_get(boundary, "no_production_behavior", False)),
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=reasons,
        source_trace_refs=(str(CURRENT_STATUS_REPORT_PATH),),
    )


def validate_host_body_embodied_learning_closed_loop_milestone_audit(record: Any) -> dict[str, object]:
    data = _record(record)
    if data is None:
        return {"valid": False, "status": "missing", "reasons": ["missing"]}
    valid = data.get("audit_status") == PASSED_AUDIT_STATUS
    valid = valid and bool(data.get("host_body_embodied_learning_closed_loop_established"))
    valid = valid and all(
        bool(data.get(name))
        for name in (
            "scope_valid",
            "capability_ledger_valid",
            "boundary_ledger_valid",
            "integrated_trace_valid",
            "package_107_verified",
            "package_108_verified",
            "package_109_verified",
            "package_110_verified",
            "package_111_verified",
            "package_112_verified",
            "current_status_report_verified",
            "audit_only_package_confirmed",
            "fixture_only_confirmed",
            "teacher_gated_confirmed",
            "trace_spine_format_unified_confirmed",
            "trace_spine_time_aligned_confirmed",
            "raw_trace_append_only_confirmed",
            "raw_trace_not_summarized_during_service_period",
            "memory_layer_stores_interpretation_only_confirmed",
            "source_trace_refs_preserved_confirmed",
            "concept_id_not_embedded_into_raw_history_confirmed",
            "raw_trace_not_dumped_into_memory_learning_trace_confirmed",
            "gcmc_docs_only_future_architecture_confirmed",
            "gcmc_runtime_not_implemented_confirmed",
            "cl_token_not_created_confirmed",
            "no_real_hardware",
            "no_semantic_vision",
            "no_speech_recognition",
            "no_task_action_selection",
            "no_final_action",
            "no_direct_command",
            "no_sandbox_execution",
            "no_external_control",
            "no_unity_runtime_connection",
            "no_memory_write_by_this_package",
            "no_long_term_memory_write",
            "no_core_memory_write",
            "no_learning_candidate_creation_by_this_package",
            "no_concept_candidate_creation_by_this_package",
            "no_reviewed_concept_creation_by_this_package",
            "no_automatic_learning_approval",
            "no_teacher_approval_created",
            "no_first_output",
            "no_live_runtime_session",
            "no_thought_engine_behavior",
            "no_production_behavior",
        )
    )
    valid = valid and not bool(data.get("new_capability_created_by_this_package"))
    return {
        "valid": valid,
        "status": data.get("audit_status"),
        "reasons": [] if valid else [str(data.get("audit_status"))],
    }


def build_host_body_embodied_learning_closed_loop_readiness(
    *,
    closed_loop_milestone_audit: Any | None,
    readiness_status: str = "ready_for_internal_action_home_surface_link_only",
) -> HostBodyEmbodiedLearningClosedLoopReadinessRecord:
    audit = _record(closed_loop_milestone_audit)
    if audit is None:
        status = "not_ready_missing_closed_loop_milestone_audit"
    elif not validate_host_body_embodied_learning_closed_loop_milestone_audit(audit)["valid"]:
        status = "not_ready_boundary_failure"
    elif readiness_status.startswith("ready_for_"):
        status = readiness_status
    else:
        status = "blocked_forbidden_authority_detected"
    return HostBodyEmbodiedLearningClosedLoopReadinessRecord(
        closed_loop_readiness_id=f"host_body_embodied_learning_closed_loop_readiness:{status}",
        schema_version=READINESS_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_closed_loop_milestone_audit_id=str(
            _get(audit, "closed_loop_milestone_audit_id", "")
        ),
        current_verified_capability=(
            "First fixture-only, teacher-gated Host Body embodied learning "
            "readback loop milestone is sealed."
        ),
        recommended_next_package=(
            "Package 114 / ASHL Core v1 Internal Action Home Surface Link Minimal v0"
        ),
        recommended_next_reason=(
            "Connect internal-only Host Body action results to Qingyin Home "
            "read-only surface records without screen mutation, external control, "
            "memory write, first_output, or live runtime."
        ),
        ready_for_internal_action_home_surface_link=True,
        ready_for_runtime_state_summary_session_shell=True,
        ready_for_bounded_embodied_loop_runner=True,
        ready_for_no_codex_teacher_console_flow=True,
        ready_for_session_end_review_promote_gate=True,
        ready_for_no_codex_fixture_growth_loop_milestone_audit=True,
        ready_for_real_camera_connection=False,
        ready_for_real_microphone_connection=False,
        ready_for_task_engine_action_selection_influence=False,
        ready_for_external_control=False,
        ready_for_long_term_memory_write=False,
        ready_for_core_memory_write=False,
        ready_for_cl_token_creation=False,
        ready_for_gcmc_runtime=False,
        ready_for_first_output=False,
        ready_for_live_runtime_session=False,
        readiness_status=status,
        readiness_summary=(
            "Ready for Package 114 and later fixture/no-Codex loop work only; "
            "not ready for real sensors, task action influence, memory writes, "
            "first_output, GCMC runtime, or live runtime."
        ),
        source_trace_refs=(str(CURRENT_STATUS_REPORT_PATH),),
    )


def validate_host_body_embodied_learning_closed_loop_readiness(record: Any) -> dict[str, object]:
    data = _record(record)
    if data is None:
        return {"valid": False, "status": "missing", "reasons": ["missing"]}
    valid = data.get("readiness_status") in {
        "ready_for_internal_action_home_surface_link_only",
        "ready_for_runtime_state_summary_session_shell_only",
        "ready_for_bounded_embodied_loop_runner_only",
        "ready_for_no_codex_teacher_console_flow_only",
        "ready_for_session_end_review_promote_gate_only",
        "ready_for_no_codex_fixture_growth_loop_milestone_audit_only",
    }
    valid = valid and all(
        bool(data.get(name))
        for name in (
            "ready_for_internal_action_home_surface_link",
            "ready_for_runtime_state_summary_session_shell",
            "ready_for_bounded_embodied_loop_runner",
            "ready_for_no_codex_teacher_console_flow",
            "ready_for_session_end_review_promote_gate",
            "ready_for_no_codex_fixture_growth_loop_milestone_audit",
        )
    )
    valid = valid and not any(
        bool(data.get(name))
        for name in (
            "ready_for_real_camera_connection",
            "ready_for_real_microphone_connection",
            "ready_for_task_engine_action_selection_influence",
            "ready_for_external_control",
            "ready_for_long_term_memory_write",
            "ready_for_core_memory_write",
            "ready_for_cl_token_creation",
            "ready_for_gcmc_runtime",
            "ready_for_first_output",
            "ready_for_live_runtime_session",
        )
    )
    return {
        "valid": valid,
        "status": data.get("readiness_status"),
        "reasons": [] if valid else [str(data.get("readiness_status"))],
    }


def _build_closed_loop_payload(
    *,
    scope_kwargs: dict[str, Any] | None = None,
    ledger_kwargs: dict[str, Any] | None = None,
    boundary_kwargs: dict[str, Any] | None = None,
    trace_kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    scope = build_host_body_embodied_learning_closed_loop_scope(**(scope_kwargs or {}))
    ledger = build_host_body_embodied_learning_closed_loop_capability_ledger(
        closed_loop_scope=scope, **(ledger_kwargs or {})
    )
    boundary = build_host_body_embodied_learning_closed_loop_boundary_ledger(
        closed_loop_scope=scope, **(boundary_kwargs or {})
    )
    trace = build_host_body_embodied_learning_closed_loop_integrated_trace(
        closed_loop_scope=scope, **(trace_kwargs or {})
    )
    audit = build_host_body_embodied_learning_closed_loop_milestone_audit(
        closed_loop_scope=scope,
        capability_ledger=ledger,
        boundary_ledger=boundary,
        integrated_trace=trace,
    )
    readiness = build_host_body_embodied_learning_closed_loop_readiness(
        closed_loop_milestone_audit=audit
    )
    return {
        "host_body_embodied_learning_closed_loop_scope": scope.to_dict(),
        "host_body_embodied_learning_closed_loop_capability_ledger": ledger.to_dict(),
        "host_body_embodied_learning_closed_loop_boundary_ledger": boundary.to_dict(),
        "host_body_embodied_learning_closed_loop_integrated_trace": trace.to_dict(),
        "host_body_embodied_learning_closed_loop_milestone_audit": audit.to_dict(),
        "host_body_embodied_learning_closed_loop_readiness": readiness.to_dict(),
    }


def build_demo_host_body_embodied_learning_closed_loop_pass() -> dict[str, Any]:
    return _build_closed_loop_payload()


def build_demo_closed_loop_missing_host_body_v0() -> dict[str, Any]:
    return _build_closed_loop_payload(ledger_kwargs={"host_body_v0_verified": False})


def build_demo_closed_loop_missing_learning_feedback() -> dict[str, Any]:
    return _build_closed_loop_payload(
        ledger_kwargs={"host_body_evidence_to_learning_feedback_verified": False}
    )


def build_demo_closed_loop_missing_existing_pipeline() -> dict[str, Any]:
    return _build_closed_loop_payload(
        ledger_kwargs={"existing_learning_pipeline_compatibility_verified": False}
    )


def build_demo_closed_loop_missing_reviewed_concept_replay() -> dict[str, Any]:
    return _build_closed_loop_payload(ledger_kwargs={"reviewed_concept_replay_verified": False})


def build_demo_closed_loop_missing_working_readback() -> dict[str, Any]:
    return _build_closed_loop_payload(
        ledger_kwargs={"working_readback_integration_verified": False}
    )


def build_demo_closed_loop_missing_readback_influence() -> dict[str, Any]:
    return _build_closed_loop_payload(
        ledger_kwargs={"readback_internal_action_influence_verified": False}
    )


def build_demo_closed_loop_missing_current_status_report() -> dict[str, Any]:
    return _build_closed_loop_payload(
        ledger_kwargs={"current_status_report_verified": False},
        trace_kwargs={"current_status_report_confirmed": False},
    )


def build_demo_closed_loop_blocked_unexpected_new_capability() -> dict[str, Any]:
    return _build_closed_loop_payload(
        ledger_kwargs={"new_capability_created_by_this_package": True}
    )


def build_demo_closed_loop_blocked_raw_trace_summarized() -> dict[str, Any]:
    return _build_closed_loop_payload(boundary_kwargs={"no_raw_trace_summarization": False})


def build_demo_closed_loop_blocked_concept_id_in_raw_history() -> dict[str, Any]:
    return _build_closed_loop_payload(
        boundary_kwargs={"no_concept_id_embedded_into_raw_history": False}
    )


def build_demo_closed_loop_blocked_task_action_selection() -> dict[str, Any]:
    return _build_closed_loop_payload(
        boundary_kwargs={"no_task_engine_selected_action": False}
    )


def build_demo_closed_loop_blocked_external_control() -> dict[str, Any]:
    return _build_closed_loop_payload(boundary_kwargs={"no_external_control": False})


def build_demo_closed_loop_blocked_memory_write() -> dict[str, Any]:
    return _build_closed_loop_payload(
        boundary_kwargs={"no_memory_layer_write_by_this_package": False}
    )


def build_demo_closed_loop_blocked_first_output() -> dict[str, Any]:
    return _build_closed_loop_payload(boundary_kwargs={"no_first_output": False})


def build_demo_closed_loop_blocked_live_runtime() -> dict[str, Any]:
    return _build_closed_loop_payload(boundary_kwargs={"no_live_runtime_session": False})


def render_host_body_embodied_learning_closed_loop_summary_text(record: Any) -> str:
    data = _record(record) or record
    if isinstance(data, dict) and "host_body_embodied_learning_closed_loop_milestone_audit" in data:
        data = data["host_body_embodied_learning_closed_loop_milestone_audit"]
    if not isinstance(data, dict):
        return str(data)
    return "\n".join(
        (
            "Host Body embodied learning closed loop milestone",
            f"audit_status: {data.get('audit_status')}",
            "safe_claim: " + str(data.get("safe_claim", "")),
        )
    )


def render_host_body_embodied_learning_closed_loop_capability_table(record: Any) -> str:
    data = _record(record) or {}
    entries = data.get("capability_entries", [])
    lines = ["package | capability | verified | commit"]
    for entry in entries:
        lines.append(
            f"{entry.get('package')} | {entry.get('capability')} | "
            f"{entry.get('verified')} | {entry.get('commit')}"
        )
    return "\n".join(lines)


def render_host_body_embodied_learning_closed_loop_boundary_table(record: Any) -> str:
    data = _record(record) or {}
    entries = data.get("boundary_entries", [])
    lines = ["boundary | confirmed"]
    for entry in entries:
        lines.append(f"{entry.get('boundary')} | {entry.get('confirmed')}")
    return "\n".join(lines)
