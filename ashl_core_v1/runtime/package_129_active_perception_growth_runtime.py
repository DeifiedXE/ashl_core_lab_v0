"""Package 129 real active-perception two-cycle orchestration."""

from __future__ import annotations

import os
from dataclasses import replace
from pathlib import Path
from typing import Any

from ashl_core_v1.perception.hard_soft_perception_primitive_compiler import (
    HardSoftPerceptionPrimitiveCompiler,
)
from ashl_core_v1.perception.host_state_primitive_compiler import (
    HOST_STATE_COMPILER_ID,
)
from ashl_core_v1.perception.perception_primitive_store import (
    PerceptionPrimitiveStore,
)
from ashl_core_v1.perception.visual_frame_primitive_compiler import (
    VISUAL_FRAME_COMPILER_ID,
)
from ashl_core_v1.runtime.active_perception_growth_types import (
    COMPARISON_SCHEMA_VERSION,
    CYCLE_2_PRESERVATION_SCHEMA_VERSION,
    CYCLE_SCHEMA_VERSION,
    EXPERIMENT_ID,
    READBACK_INFLUENCE_SCHEMA_VERSION,
    READBACK_TIMING_SCHEMA_VERSION,
    STAGE_SCHEMA_VERSION,
    ActivePerceptionCycle2PendingReviewPreservation,
    ActivePerceptionGrowthCycleRecord,
    ActivePerceptionReadbackInfluenceRecord,
    ActivePerceptionReadbackLoadTiming,
    ActivePerceptionStageRecord,
    ActivePerceptionTwoCycleComparison,
)
from ashl_core_v1.runtime.active_perception_readback_influence import (
    SCORER_ID,
    reject_stimulus_matching_provenance,
    score_extension_candidate_with_working_readback,
    validate_readback_loaded_before_candidate,
)
from ashl_core_v1.runtime.bounded_capture_deadline_controller import (
    BoundedCaptureDeadlineController,
)
from ashl_core_v1.runtime.bounded_multimodal_perception_session_runtime import (
    BoundedMultimodalPerceptionSessionRuntime,
)
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
    ContentAddressedSensorArtifactStore,
)
from ashl_core_v1.runtime.cross_window_temporal_link import (
    build_cross_window_temporal_link,
)
from ashl_core_v1.runtime.focused_visual_region_view import (
    build_focus_context_sidecar,
    build_focus_release_record,
)
from ashl_core_v1.runtime.host_sensor_types import (
    SensorCaptureError,
    canonical_json,
    monotonic_ns,
    sha256_payload,
    stable_id,
    utc_now,
)
from ashl_core_v1.runtime.host_state_sensor_adapter import (
    HostStateSensorAdapter,
)
from ashl_core_v1.runtime.internal_perception_focus_action import (
    create_internal_perception_focus_shift_action,
)
from ashl_core_v1.runtime.internal_perception_focus_candidate import (
    create_focus_candidates,
    select_focus_candidate,
)
from ashl_core_v1.runtime.internal_perception_focus_policy import (
    create_focus_authorization,
    create_focus_plan,
    decide_focus_policy,
)
from ashl_core_v1.runtime.local_active_perception_growth_stimulus_runtime import (
    LocalActivePerceptionGrowthStimulusRuntime,
)
from ashl_core_v1.runtime.local_operator_console_store import (
    build_default_console_store,
)
from ashl_core_v1.runtime.local_operator_event_stream import (
    LocalOperatorEventStream,
)
from ashl_core_v1.runtime.multimodal_perception_session_types import (
    ARTIFACT_REPLAY_MANIFEST_SCHEMA_VERSION,
    TIMELINE_INPUT_REF_SCHEMA_VERSION,
    ArtifactBackedPerceptionTimelineManifest,
    MultimodalPerceptionSessionMode,
    PerceptionTimelineInputRef,
    build_default_multimodal_session_config,
)
from ashl_core_v1.runtime.observation_extension_candidate import (
    create_observation_extension_candidate,
)
from ashl_core_v1.runtime.observation_extension_internal_action import (
    create_bounded_observation_extension_internal_action,
    execute_bounded_observation_extension,
)
from ashl_core_v1.runtime.observation_extension_policy import (
    decide_observation_extension_policy,
)
from ashl_core_v1.runtime.observation_stop_policy import (
    decide_observation_stop_policy,
)
from ashl_core_v1.runtime.observation_window_types import (
    ACTIVE_CAPTURE_SESSION_IDENTITY_SCHEMA_VERSION,
    OBSERVATION_EXTENSION_COMPARISON_SCHEMA_VERSION,
    OBSERVATION_EXTENSION_OUTCOME_SCHEMA_VERSION,
    OBSERVATION_WINDOW_STATE_SCHEMA_VERSION,
    ActiveCaptureSessionIdentity,
    ObservationExtensionEffectComparison,
    ObservationWindowExtensionOutcome,
    ObservationWindowState,
)
from ashl_core_v1.runtime.package_123_transport_integrity import (
    ALIGNMENT_LANE_COVERAGE_SCHEMA_VERSION,
    ALIGNMENT_WINDOW_COVERAGE_SCHEMA_VERSION,
    AlignmentLaneCoverage,
    AlignmentWindowCoverageRecord,
)
from ashl_core_v1.runtime.package_124a_temporal_store import (
    Package124ATemporalStore,
)
from ashl_core_v1.runtime.package_125_observation_extension_runtime import (
    build_observation_extension_authorization,
)
from ashl_core_v1.runtime.package_125_observation_extension_store import (
    Package125ObservationExtensionStore,
)
from ashl_core_v1.runtime.package_126_reacquisition_runtime import (
    ActiveReacquisitionCaptureSnapshot,
    _build_evidence_summary,
    _build_live_alignment_config,
    _build_plan_identity,
    _build_source_configs,
    _completed_parent_reference,
    capture_one_bounded_reacquisition_window,
)
from ashl_core_v1.runtime.package_126_reacquisition_store import (
    Package126ReacquisitionStore,
)
from ashl_core_v1.runtime.package_127_internal_focus_store import (
    Package127InternalFocusStore,
)
from ashl_core_v1.runtime.package_128_sufficiency_stop_runtime import (
    ACTIVE_ALIGNMENT_WINDOW_MS,
    _build_final_temporal_bundle,
    _evaluate_active_checkpoint,
    _initialize_active_contract,
)
from ashl_core_v1.runtime.package_128_sufficiency_stop_store import (
    Package128SufficiencyStopStore,
)
from ashl_core_v1.runtime.package_129_active_perception_growth_store import (
    Package129ActivePerceptionGrowthStore,
)
from ashl_core_v1.runtime.perception_reacquisition_internal_action import (
    create_bounded_reacquisition_internal_action,
)
from ashl_core_v1.runtime.perception_reacquisition_policy import (
    create_reacquisition_authorization,
    create_reacquisition_request,
    decide_reacquisition_eligibility,
)
from ashl_core_v1.runtime.perception_reacquisition_types import (
    ReacquisitionCaptureExecution,
)
from ashl_core_v1.runtime.sampling_plan_identity import (
    clone_sampling_plan_identity,
    configuration_identity_equal,
    target_identity_equal,
)
from ashl_core_v1.runtime.session_learning_evidence_identity import (
    FULL_COMMIT_APPROVAL_SCOPE,
)
from ashl_core_v1.runtime.stop_observation_internal_action import (
    build_observation_completion,
    build_observation_stop_execution,
)
from ashl_core_v1.runtime.structural_evidence_sufficiency_types import (
    CHECKPOINT_INTERVAL_NS,
    CHILD_HARD_WINDOW_NS,
    MAXIMUM_CHECKPOINT_COUNT,
    MINIMUM_ELAPSED_NS,
    MINIMUM_POST_EVENT_COVERAGE_NS,
)
from ashl_core_v1.runtime.teacher_gated_session_resume_commit import (
    TeacherGatedSessionResumeCommitRuntime,
)
from ashl_core_v1.runtime.teacher_gated_session_store import (
    TeacherGatedSessionStore,
)
from ashl_core_v1.runtime.temporal_tail_evidence_adapter import (
    build_closure_links,
    build_temporal_tail_evidence,
)
from ashl_core_v1.runtime.windows_bounded_window_capture_source import (
    WindowsBoundedWindowCaptureSource,
)


PARTICIPATING_LANES = ("screen", "host_state")
PARENT_BASE_WINDOW_NS = 5_000_000_000
PARENT_EXTENSION_NS = 1_500_000_000
PARENT_FINAL_WINDOW_NS = PARENT_BASE_WINDOW_NS + PARENT_EXTENSION_NS
PARENT_HARD_WINDOW_NS = 7_000_000_000
PARENT_CHECKPOINT_NS = (
    4_250_000_000,
    4_500_000_000,
    4_750_000_000,
    5_500_000_000,
    6_000_000_000,
    6_400_000_000,
)
SOURCE_SAMPLE_INTERVAL_NS = 750_000_000
HOST_SAMPLE_INTERVAL_MS = 750
PARENT_STRUCTURAL_CHANGE_FLOOR = 0.2
STIMULUS_CONFIG = {
    "fixture_kind": "nonsemantic_two_region_visual_sequence",
    "client_width": 128,
    "client_height": 72,
    "parent_base_window_ns": PARENT_BASE_WINDOW_NS,
    "parent_extension_ns": PARENT_EXTENSION_NS,
    "parent_hard_window_ns": PARENT_HARD_WINDOW_NS,
    "parent_structural_change_floor": 0.2,
    "child_hard_window_ns": CHILD_HARD_WINDOW_NS,
    "participating_lanes": PARTICIPATING_LANES,
    "audio": "not_participating_by_design",
    "camera": "not_participating_by_design",
}
STIMULUS_CONFIG_HASH = sha256_payload(STIMULUS_CONFIG)
SOURCE_PLAN_CONFIG_HASH = sha256_payload(
    {
        "required_lanes": PARTICIPATING_LANES,
        "screen_scope": "one_fixed_full_window_target_per_cycle",
        "host_state_sample_interval_ms": HOST_SAMPLE_INTERVAL_MS,
        "parent_base_window_ns": PARENT_BASE_WINDOW_NS,
        "parent_extension_ns": PARENT_EXTENSION_NS,
        "child_hard_window_ns": CHILD_HARD_WINDOW_NS,
        "visual_compiler_id": VISUAL_FRAME_COMPILER_ID,
        "host_state_compiler_id": HOST_STATE_COMPILER_ID,
        "audio": "not_participating_by_design",
        "camera": "not_participating_by_design",
    }
)
TEACHER_INTERPRETATION = (
    "A real low-level visual event remained structurally open near the end "
    "of one bounded observation window. The runtime extended that active "
    "window, preserved the full visual field, selected one changed grid "
    "region as read-only focus, acquired one fresh same-plan child sample, "
    "and stopped the child after the configured visual-closure and "
    "post-context evidence contract was satisfied. This interpretation is "
    "limited to the observed low-level evidence and audited internal "
    "perception-action sequence."
)


def run_active_perception_cycle(
    *,
    state_dir: str | Path,
    cycle_index: int,
    process_instance_id: str | None = None,
    strict_event_stream: bool = True,
) -> dict[str, Any]:
    if cycle_index not in {1, 2}:
        raise ValueError("cycle_index must be 1 or 2")
    path = Path(state_dir)
    package_store = Package129ActivePerceptionGrowthStore(path)
    process_id = process_instance_id or stable_id(
        f"package_129_cycle_{cycle_index}_process"
    )
    pid = os.getpid()
    if package_store.latest_cycle(cycle_index) is not None:
        raise RuntimeError(f"Package 129 Cycle {cycle_index} already exists")
    cycle_one = package_store.latest_cycle(1)
    teacher_store = TeacherGatedSessionStore(path)
    active_readback = teacher_store.load_active_working_readback()
    readback_loaded_ns: int | None = None
    if cycle_index == 1:
        if any(
            item.get("evidence_theme")
            == "active_perception_sequence_observed"
            for item in active_readback
        ):
            raise RuntimeError(
                "Cycle 1 requires no matching Package 129 working readback"
            )
        active_readback = tuple()
    else:
        if cycle_one is None:
            raise RuntimeError("Cycle 2 requires a persisted Cycle 1")
        _assert_cycle_one_commit_present(path, cycle_one)
        previous_receipts = package_store.list_payloads(
            "active_perception_process_receipts"
        )
        if any(
            int(item.get("cycle_index", 0)) == 1
            and int(item.get("operating_system_process_id", -1)) == pid
            for item in previous_receipts
        ):
            raise RuntimeError(
                "Cycle 2 must run in a different operating-system process"
            )
        expected_snapshot = str(cycle_one["evidence_snapshot_id"])
        expected_hash = str(cycle_one["evidence_identity_hash"])
        active_readback = tuple(
            item
            for item in active_readback
            if item.get("source_evidence_snapshot_id") == expected_snapshot
            and item.get("evidence_identity_sha256") == expected_hash
            and item.get("evidence_theme")
            == "active_perception_sequence_observed"
        )
        if not active_readback:
            raise RuntimeError(
                "Cycle 2 requires approved Cycle 1 working readback"
            )
        readback_loaded_ns = monotonic_ns()

    experiment_run_id = stable_id(
        f"package_129_cycle_{cycle_index}_experiment_run"
    )
    parent_ids = {
        "runtime_session_id": stable_id(
            f"package_129_cycle_{cycle_index}_parent_runtime"
        ),
        "perception_session_id": stable_id(
            f"package_129_cycle_{cycle_index}_parent_perception"
        ),
        "observation_window_id": stable_id("observation_window"),
    }
    receipt_id = stable_id("package_129_process_receipt")
    package_store.append_payload(
        "active_perception_process_receipts",
        "process_receipt_id",
        receipt_id,
        {
            "process_receipt_id": receipt_id,
            "schema_version": "ashl_package_129_process_receipt_v0",
            "created_at": utc_now(),
            "cycle_index": cycle_index,
            "process_instance_id": process_id,
            "operating_system_process_id": pid,
            "receipt_kind": "cycle_process_started",
            "experiment_run_id": experiment_run_id,
        },
    )
    _emit_growth_event(
        path=path,
        package_store=package_store,
        event_kind=(
            "active_perception_cycle_started"
            if cycle_index == 1
            else "active_perception_cycle2_process_started"
        ),
        cycle_index=cycle_index,
        process_instance_id=process_id,
        runtime_session_id=parent_ids["runtime_session_id"],
        perception_session_id=parent_ids["perception_session_id"],
        observation_window_id=parent_ids["observation_window_id"],
        source_record_refs=(receipt_id,),
        source_trace_refs=(receipt_id,),
        strict=strict_event_stream,
    )
    if cycle_index == 2:
        _emit_growth_event(
            path=path,
            package_store=package_store,
            event_kind="active_perception_readback_loaded",
            cycle_index=cycle_index,
            process_instance_id=process_id,
            runtime_session_id=parent_ids["runtime_session_id"],
            perception_session_id=parent_ids["perception_session_id"],
            observation_window_id=parent_ids["observation_window_id"],
            source_record_refs=tuple(
                str(item["working_readback_commit_id"])
                for item in active_readback
            ),
            source_trace_refs=tuple(
                ref
                for item in active_readback
                for ref in tuple(item.get("source_trace_refs") or ())
            ),
            strict=strict_event_stream,
        )

    sequence = _run_real_active_perception_sequence(
        path=path,
        cycle_index=cycle_index,
        experiment_run_id=experiment_run_id,
        process_instance_id=process_id,
        parent_ids=parent_ids,
        working_readback=tuple(active_readback),
        readback_loaded_ns=readback_loaded_ns,
        strict_event_stream=strict_event_stream,
    )
    stage_records = _build_stage_records(
        cycle_index=cycle_index,
        sequence=sequence,
    )
    for stage in stage_records:
        package_store.append_record(
            "active_perception_stage_records", stage
        )
        _emit_growth_event(
            path=path,
            package_store=package_store,
            event_kind="active_perception_stage_completed",
            cycle_index=cycle_index,
            process_instance_id=process_id,
            runtime_session_id=stage.runtime_session_id,
            perception_session_id=stage.perception_session_id,
            observation_window_id=stage.observation_window_id,
            source_record_refs=(stage.stage_record_id,),
            source_trace_refs=stage.source_trace_refs,
            strict=strict_event_stream,
        )
    teacher = _run_teacher_gate(
        path=path,
        cycle_index=cycle_index,
        sequence=sequence,
        stage_records=stage_records,
        working_readback=tuple(active_readback),
    )
    cycle = ActivePerceptionGrowthCycleRecord(
        cycle_record_id=stable_id(
            f"package_129_cycle_{cycle_index}_record"
        ),
        schema_version=CYCLE_SCHEMA_VERSION,
        created_at=utc_now(),
        experiment_id=EXPERIMENT_ID,
        experiment_run_id=experiment_run_id,
        cycle_index=cycle_index,
        process_instance_id=process_id,
        operating_system_process_id=pid,
        stimulus_config_hash=STIMULUS_CONFIG_HASH,
        source_plan_hash=SOURCE_PLAN_CONFIG_HASH,
        stage_record_ids=tuple(item.stage_record_id for item in stage_records),
        parent_runtime_session_id=sequence["parent"][
            "runtime_session_id"
        ],
        parent_perception_session_id=sequence["parent"][
            "perception_session_id"
        ],
        parent_observation_window_id=sequence["parent"][
            "observation_window_id"
        ],
        child_runtime_session_id=sequence["child"]["runtime_session_id"],
        child_perception_session_id=sequence["child"][
            "perception_session_id"
        ],
        child_observation_window_id=sequence["child"][
            "observation_window_id"
        ],
        bounded_embodied_session_id=teacher["package_115_session_id"],
        final_session_state="WAITING_TEACHER_REVIEW",
        pending_teacher_review_id=teacher["pending_review_id"],
        evidence_snapshot_id=teacher["evidence_snapshot_id"],
        evidence_identity_hash=teacher["evidence_identity_hash"],
        readback_loaded_before_event=cycle_index == 2,
        loaded_readback_refs=tuple(
            str(item["working_readback_commit_id"])
            for item in active_readback
        ),
        parent_screen_artifact_refs=tuple(
            sequence["parent"]["screen_artifact_ids"]
        ),
        parent_host_state_artifact_refs=tuple(
            sequence["parent"]["host_artifact_ids"]
        ),
        child_screen_artifact_refs=tuple(
            sequence["child"]["screen_artifact_ids"]
        ),
        child_host_state_artifact_refs=tuple(
            sequence["child"]["host_artifact_ids"]
        ),
        source_record_refs=tuple(
            item.stage_record_id for item in stage_records
        )
        + (
            teacher["pending_review_id"],
            teacher["evidence_snapshot_id"],
        ),
        source_trace_refs=tuple(sequence["source_trace_refs"])
        + tuple(teacher["source_trace_refs"]),
    )
    package_store.append_record("active_perception_cycle_records", cycle)

    extra: dict[str, Any] = {}
    if cycle_index == 2:
        assert cycle_one is not None
        timing = _build_readback_timing(
            cycle=cycle,
            sequence=sequence,
            readback=tuple(active_readback),
            readback_loaded_ns=int(readback_loaded_ns or 0),
        )
        influence = _build_readback_influence(
            cycle_one=cycle_one,
            cycle=cycle,
            stage_records=stage_records,
            sequence=sequence,
            readback=tuple(active_readback),
        )
        preservation = ActivePerceptionCycle2PendingReviewPreservation(
            preservation_record_id=stable_id(
                "package_129_cycle_2_review_preservation"
            ),
            schema_version=CYCLE_2_PRESERVATION_SCHEMA_VERSION,
            created_at=utc_now(),
            cycle_2_session_id=cycle.bounded_embodied_session_id,
            pending_review_id=str(cycle.pending_teacher_review_id),
            evidence_identity_hash=str(cycle.evidence_identity_hash),
            preservation_reason=(
                "cycle_2_teacher_gate_is_growth_evidence_not_required_second_commit"
            ),
            teacher_decision_count=teacher_store.count_rows(
                "teacher_decisions", cycle.bounded_embodied_session_id
            ),
            reviewed_memory_commit_count=teacher_store.count_rows(
                "reviewed_interpretation_commits",
                cycle.bounded_embodied_session_id,
            ),
            preserved_unresolved=True,
            source_record_refs=(
                str(cycle.pending_teacher_review_id),
                str(cycle.evidence_snapshot_id),
            ),
            source_trace_refs=tuple(teacher["source_trace_refs"]),
        )
        comparison = _build_two_cycle_comparison(
            cycle_one=cycle_one,
            cycle_two=cycle,
            influence=influence,
            path=path,
        )
        package_store.append_record(
            "active_perception_readback_load_timing", timing
        )
        package_store.append_record(
            "active_perception_readback_influence", influence
        )
        package_store.append_record(
            "active_perception_cycle2_review_preservation", preservation
        )
        package_store.append_record(
            "active_perception_two_cycle_comparisons", comparison
        )
        controls = run_package_129_controls(
            state_dir=path,
            sequence=sequence,
            cycle_one=cycle_one,
            readback=tuple(active_readback),
            cycle_two_session_id=cycle.bounded_embodied_session_id,
        )
        _emit_growth_event(
            path=path,
            package_store=package_store,
            event_kind="active_perception_readback_influence_applied",
            cycle_index=2,
            process_instance_id=process_id,
            runtime_session_id=cycle.parent_runtime_session_id,
            perception_session_id=cycle.parent_perception_session_id,
            observation_window_id=cycle.parent_observation_window_id,
            source_record_refs=(influence.influence_record_id,),
            source_trace_refs=influence.source_trace_refs,
            strict=strict_event_stream,
        )
        _emit_growth_event(
            path=path,
            package_store=package_store,
            event_kind="active_perception_two_cycle_comparison_created",
            cycle_index=2,
            process_instance_id=process_id,
            runtime_session_id=cycle.parent_runtime_session_id,
            perception_session_id=cycle.parent_perception_session_id,
            observation_window_id=cycle.parent_observation_window_id,
            source_record_refs=(comparison.comparison_id,),
            source_trace_refs=comparison.source_trace_refs,
            strict=strict_event_stream,
        )
        extra = {
            "readback_load_timing": timing.to_dict(),
            "readback_influence": influence.to_dict(),
            "cycle_2_review_preservation": preservation.to_dict(),
            "comparison": comparison.to_dict(),
            "controls": controls,
        }

    waiting_event = (
        "active_perception_cycle_waiting_teacher_review"
        if cycle_index == 1
        else "active_perception_cycle2_waiting_teacher_review"
    )
    _emit_growth_event(
        path=path,
        package_store=package_store,
        event_kind=waiting_event,
        cycle_index=cycle_index,
        process_instance_id=process_id,
        runtime_session_id=cycle.parent_runtime_session_id,
        perception_session_id=cycle.parent_perception_session_id,
        observation_window_id=cycle.parent_observation_window_id,
        source_record_refs=(
            cycle.cycle_record_id,
            str(cycle.pending_teacher_review_id),
        ),
        source_trace_refs=cycle.source_trace_refs,
        strict=strict_event_stream,
    )
    end_receipt_id = stable_id("package_129_process_receipt")
    package_store.append_payload(
        "active_perception_process_receipts",
        "process_receipt_id",
        end_receipt_id,
        {
            "process_receipt_id": end_receipt_id,
            "schema_version": "ashl_package_129_process_receipt_v0",
            "created_at": utc_now(),
            "cycle_index": cycle_index,
            "process_instance_id": process_id,
            "operating_system_process_id": pid,
            "receipt_kind": "cycle_process_ended",
            "cycle_record_id": cycle.cycle_record_id,
        },
    )
    _emit_growth_event(
        path=path,
        package_store=package_store,
        event_kind="active_perception_cycle_process_ended",
        cycle_index=cycle_index,
        process_instance_id=process_id,
        runtime_session_id=cycle.parent_runtime_session_id,
        perception_session_id=cycle.parent_perception_session_id,
        observation_window_id=cycle.parent_observation_window_id,
        source_record_refs=(end_receipt_id, cycle.cycle_record_id),
        source_trace_refs=cycle.source_trace_refs,
        strict=strict_event_stream,
    )
    return {
        "status": (
            "cycle_1_waiting_teacher_review"
            if cycle_index == 1
            else "cycle_2_waiting_teacher_review"
        ),
        "cycle_record": cycle.to_dict(),
        "stage_records": tuple(item.to_dict() for item in stage_records),
        "teacher_gate": teacher,
        "sequence": _public_sequence(sequence),
        **extra,
    }


def review_cycle_one(
    *,
    state_dir: str | Path,
    decision: str,
    reviewer: str,
    expected_evidence_identity: str,
    approval_scope: str,
    confirm: bool,
) -> dict[str, Any]:
    if not confirm:
        raise ValueError("review-cycle-1 requires --confirm")
    if approval_scope != FULL_COMMIT_APPROVAL_SCOPE:
        raise ValueError(
            "Package 129 requires through_reviewed_concept_and_working_readback"
        )
    path = Path(state_dir)
    package_store = Package129ActivePerceptionGrowthStore(path)
    cycle = package_store.latest_cycle(1)
    if cycle is None:
        raise RuntimeError("no Package 129 Cycle 1 record found")
    if expected_evidence_identity != cycle["evidence_identity_hash"]:
        raise ValueError("expected evidence identity does not match Cycle 1")
    normalized = {
        "approve": "approved",
        "approved": "approved",
        "reject": "rejected",
        "rejected": "rejected",
        "defer": "deferred",
        "deferred": "deferred",
    }.get(decision, decision)
    runtime = TeacherGatedSessionResumeCommitRuntime()
    reason_codes = (
        "package_129_exact_teacher_review",
        f"reviewer:{reviewer}",
        "allowed_interpretation_scope:low_level_active_perception_sequence_only",
        f"evidence_identity:{expected_evidence_identity}",
    )
    decision_record = runtime.apply_teacher_decision(
        str(cycle["bounded_embodied_session_id"]),
        str(cycle["pending_teacher_review_id"]),
        normalized,
        reason_codes,
        TEACHER_INTERPRETATION,
        path,
        approval_scope=(
            approval_scope if normalized == "approved" else None
        ),
        expected_evidence_hash=expected_evidence_identity,
    )
    if normalized == "approved":
        result = runtime.resume_after_approval(
            str(cycle["bounded_embodied_session_id"]),
            decision_record.teacher_decision_id,
            path,
        )
    elif normalized == "rejected":
        result = runtime.close_rejected_session(
            str(cycle["bounded_embodied_session_id"]),
            decision_record.teacher_decision_id,
            path,
        )
    else:
        result = runtime.pause_nonfinal_review(
            str(cycle["bounded_embodied_session_id"]),
            decision_record.teacher_decision_id,
            path,
        )
    readback = TeacherGatedSessionStore(path).load_active_working_readback()
    matching = tuple(
        item
        for item in readback
        if item.get("source_evidence_snapshot_id")
        == cycle["evidence_snapshot_id"]
        and item.get("evidence_identity_sha256")
        == cycle["evidence_identity_hash"]
    )
    if normalized == "approved" and (
        result.final_status != "committed" or len(matching) != 1
    ):
        raise RuntimeError("Cycle 1 approved memory chain did not commit")
    for event_kind, refs in (
        (
            "active_perception_cycle_approved",
            (decision_record.teacher_decision_id,),
        ),
        (
            "active_perception_working_readback_committed",
            tuple(
                str(item["working_readback_commit_id"]) for item in matching
            ),
        ),
    ):
        if normalized != "approved":
            break
        _emit_growth_event(
            path=path,
            package_store=package_store,
            event_kind=event_kind,
            cycle_index=1,
            process_instance_id=str(cycle["process_instance_id"]),
            runtime_session_id=str(cycle["parent_runtime_session_id"]),
            perception_session_id=str(cycle["parent_perception_session_id"]),
            observation_window_id=str(
                cycle["parent_observation_window_id"]
            ),
            source_record_refs=refs,
            source_trace_refs=tuple(decision_record.source_trace_refs),
            strict=True,
        )
    return {
        "status": (
            "cycle_1_committed"
            if result.final_status == "committed"
            else f"cycle_1_{result.final_status.lower()}"
        ),
        "teacher_decision": decision_record.to_dict(),
        "commit_result": result.to_dict(),
        "working_readback": matching,
    }


def _run_real_active_perception_sequence(
    *,
    path: Path,
    cycle_index: int,
    experiment_run_id: str,
    process_instance_id: str,
    parent_ids: dict[str, str],
    working_readback: tuple[dict[str, Any], ...],
    readback_loaded_ns: int | None,
    strict_event_stream: bool,
) -> dict[str, Any]:
    p125_store = Package125ObservationExtensionStore(path)
    p126_store = Package126ReacquisitionStore(path)
    p127_store = Package127InternalFocusStore(path)
    p128_store = Package128SufficiencyStopStore(path)
    sensor_store = ContentAddressedSensorArtifactStore(path)
    temporal_store = Package124ATemporalStore(path)
    primitive_store = PerceptionPrimitiveStore(path)
    compiler = HardSoftPerceptionPrimitiveCompiler(
        path, sensor_store=sensor_store
    )
    package_122 = BoundedMultimodalPerceptionSessionRuntime(path)
    stimulus = LocalActivePerceptionGrowthStimulusRuntime(
        experiment_run_id=experiment_run_id
    )
    window_source = WindowsBoundedWindowCaptureSource()
    host_adapter = HostStateSensorAdapter()
    root_event_id = stable_id("package_129_capture_root")
    result_frozen = False
    try:
        stimulus.open()
        stimulus.tick()
        binding = window_source.bind_by_title(
            experiment_run_id=experiment_run_id,
            window_title=stimulus.window_title,
        )
        if binding.binding_status != "bound":
            raise SensorCaptureError(
                "device_unavailable",
                f"Package 129 stimulus binding failed: {binding.binding_status}",
            )
        configs = _build_source_configs(
            path=path,
            action_kind="capture_again",
            binding=binding,
            window_source=window_source,
            audio_source=None,
            host_adapter=host_adapter,
            participating_lanes=PARTICIPATING_LANES,
            capture_duration_ms=7_000,
            host_sample_interval_ms=HOST_SAMPLE_INTERVAL_MS,
            maximum_artifact_count=64,
        )
        parent_plan = _build_plan_identity(
            action_kind="capture_again",
            binding=binding,
            window_source=window_source,
            audio_source=None,
            configs=configs,
            participating_lanes=PARTICIPATING_LANES,
        )
        p126_store.append_record(
            "sampling_plan_identity_records", parent_plan
        )
        parent_controller = BoundedCaptureDeadlineController(
            base_deadline_ns=PARENT_BASE_WINDOW_NS,
            hard_deadline_ns=PARENT_HARD_WINDOW_NS,
            participating_lanes=PARTICIPATING_LANES,
            maximum_extension_count=1,
            maximum_total_extension_ns=PARENT_EXTENSION_NS,
        )
        parent_active = _new_parent_active_state()

        def parent_hook(
            snapshot: ActiveReacquisitionCaptureSnapshot,
        ) -> None:
            _inspect_parent_extension_checkpoint(
                path=path,
                cycle_index=cycle_index,
                experiment_run_id=experiment_run_id,
                binding=binding,
                configs=configs,
                window_source=window_source,
                sensor_store=sensor_store,
                compiler=compiler,
                primitive_store=primitive_store,
                p125_store=p125_store,
                snapshot=snapshot,
                controller=parent_controller,
                active=parent_active,
                working_readback=working_readback,
                expected_evidence_snapshot_id=(
                    str(
                        Package129ActivePerceptionGrowthStore(
                            path
                        ).latest_cycle(1)["evidence_snapshot_id"]
                    )
                    if cycle_index == 2
                    else ""
                ),
                expected_evidence_identity_sha256=(
                    str(
                        Package129ActivePerceptionGrowthStore(
                            path
                        ).latest_cycle(1)["evidence_identity_hash"]
                    )
                    if cycle_index == 2
                    else ""
                ),
            )

        parent_capture_started_ns = monotonic_ns()
        parent = capture_one_bounded_reacquisition_window(
            path=path,
            store=p126_store,
            sensor_store=sensor_store,
            temporal_store=temporal_store,
            compiler=compiler,
            primitive_store=primitive_store,
            stimulus=stimulus,
            window_source=window_source,
            audio_source=None,
            host_adapter=host_adapter,
            binding=binding,
            configs=configs,
            action_kind="capture_again",
            experiment_run_id=experiment_run_id,
            root_event_id=root_event_id,
            plan=parent_plan,
            role=f"package_129_cycle_{cycle_index}_extended_parent",
            participating_lanes=PARTICIPATING_LANES,
            forced_ids=parent_ids,
            window_duration_ns=PARENT_BASE_WINDOW_NS,
            source_sample_interval_ns=SOURCE_SAMPLE_INTERVAL_NS,
            deadline_controller=parent_controller,
            active_capture_hook=parent_hook,
            compile_all_samples=True,
            compilation_cache=parent_active["compilation_cache"],
            alignment_window_ms=ACTIVE_ALIGNMENT_WINDOW_MS,
        )
        parent_extension = _finalize_parent_extension(
            parent=parent,
            controller=parent_controller,
            active=parent_active,
            p125_store=p125_store,
        )
        parent_ref = _completed_parent_reference(parent, parent_plan)
        p126_store.append_record("completed_parent_window_refs", parent_ref)
        parent_change, parent_current_frame = _strongest_actual_change(
            active=parent_active
        )
        batch, candidates = create_focus_candidates(
            parent=parent_ref,
            visual_change=parent_change,
            current_visual_frame=parent_current_frame,
        )
        if len(candidates) < 2:
            raise RuntimeError(
                "Package 129 real parent produced fewer than two focus candidates"
            )
        p127_store.append_record(
            "internal_focus_candidate_batches", batch
        )
        for candidate in candidates:
            p127_store.append_record(
                "internal_focus_candidates", candidate
            )
        selection = select_focus_candidate(
            parent_observation_window_id=parent[
                "observation_window_id"
            ],
            candidates=candidates,
        )
        p127_store.append_record(
            "internal_focus_selections", selection
        )
        selected = next(
            item
            for item in candidates
            if item.focus_candidate_id == selection.selected_candidate_id
        )
        focus_authorization = create_focus_authorization(parent=parent_ref)
        p127_store.append_record(
            "internal_focus_authorizations", focus_authorization
        )
        focus_decision = decide_focus_policy(
            selection=selection,
            candidate=selected,
            parent=parent_ref,
            authorization=focus_authorization,
        )
        p127_store.append_record(
            "internal_focus_policy_decisions", focus_decision
        )
        focus_plan = create_focus_plan(
            decision=focus_decision, candidate=selected
        )
        if focus_plan is None:
            raise RuntimeError("Package 127 focus policy blocked")
        p127_store.append_record("internal_focus_plans", focus_plan)
        focus_action = create_internal_perception_focus_shift_action(
            plan=focus_plan
        )
        p127_store.append_record(
            "internal_focus_actions", focus_action
        )

        child_plan = clone_sampling_plan_identity(
            parent_plan,
            source_record_refs=(
                parent_plan.sampling_plan_identity_id,
            ),
        )
        p126_store.append_record(
            "sampling_plan_identity_records", child_plan
        )
        reacquisition_authorization = create_reacquisition_authorization(
            parent=parent_ref,
            allowed_action_kinds=("capture_again",),
            authorization_source="explicit_session_configuration",
        )
        p126_store.append_record(
            "perception_reacquisition_authorizations",
            reacquisition_authorization,
        )
        request = create_reacquisition_request(
            parent=parent_ref,
            authorization=reacquisition_authorization,
            requested_action_kind="capture_again",
            requested_plan=child_plan,
            request_source="explicit_session_configuration",
            request_reason_codes=(
                "repeat_same_sampling_plan",
                "explicit_bounded_reacquisition",
                "controlled_real_capability_verification",
            ),
        )
        p126_store.append_record(
            "perception_reacquisition_requests", request
        )
        gap_at_request_ns = max(
            0, monotonic_ns() - int(parent["ended_monotonic_ns"])
        )
        eligibility = decide_reacquisition_eligibility(
            request=request,
            parent=parent_ref,
            parent_plan=parent_plan,
            requested_plan=child_plan,
            authorization=reacquisition_authorization,
            parent_to_request_gap_ns=gap_at_request_ns,
            chain_duration_ns=int(parent["actual_window_ns"])
            + gap_at_request_ns,
        )
        p126_store.append_record(
            "reacquisition_eligibility_decisions", eligibility
        )
        reacquisition_action = create_bounded_reacquisition_internal_action(
            request=request,
            eligibility=eligibility,
            parent=parent_ref,
        )
        if reacquisition_action is None:
            raise RuntimeError(
                "Package 126 child eligibility blocked: "
                + ",".join(eligibility.failure_reasons)
            )
        p126_store.append_record(
            "bounded_reacquisition_internal_actions",
            reacquisition_action,
        )
        child_ids = {
            "runtime_session_id": stable_id(
                f"package_129_cycle_{cycle_index}_child_runtime"
            ),
            "perception_session_id": stable_id(
                f"package_129_cycle_{cycle_index}_child_perception"
            ),
            "observation_window_id": stable_id("observation_window"),
        }
        child_result = _capture_focused_child_with_structural_stop(
            path=path,
            stimulus=stimulus,
            window_source=window_source,
            host_adapter=host_adapter,
            binding=binding,
            configs=configs,
            experiment_run_id=experiment_run_id,
            root_event_id=root_event_id,
            parent=parent,
            parent_ref=parent_ref,
            parent_plan=parent_plan,
            focus_plan=focus_plan,
            focus_action=focus_action,
            child_plan=child_plan,
            child_ids=child_ids,
            reacquisition_action=reacquisition_action,
            p126_store=p126_store,
            p127_store=p127_store,
            p128_store=p128_store,
            sensor_store=sensor_store,
            temporal_store=temporal_store,
            compiler=compiler,
            primitive_store=primitive_store,
            package_122=package_122,
            strict_event_stream=strict_event_stream,
        )
        result_frozen = True
        stimulus.mark_finished()
        fixture_manifest = stimulus.manifest()
        manifest_id = stable_id("package_129_fixture_manifest")
        Package129ActivePerceptionGrowthStore(path).append_payload(
            "active_perception_fixture_manifests",
            "fixture_manifest_id",
            manifest_id,
            {
                "fixture_manifest_id": manifest_id,
                **fixture_manifest,
                "result_frozen_before_manifest_audit": result_frozen,
            },
        )
        source_trace_refs = tuple(
            dict.fromkeys(
                tuple(parent.get("source_trace_refs") or ())
                + tuple(
                    child_result["child"].get("source_trace_refs") or ()
                )
            )
        )
        if not source_trace_refs:
            source_trace_refs = (
                f"package_129_runtime_trace:{experiment_run_id}",
            )
        return {
            "cycle_index": cycle_index,
            "experiment_run_id": experiment_run_id,
            "process_instance_id": process_instance_id,
            "parent_capture_started_monotonic_ns": (
                parent_capture_started_ns
            ),
            "parent": parent,
            "parent_plan": parent_plan,
            "parent_ref": parent_ref,
            "parent_extension": parent_extension,
            "parent_change": parent_change,
            "parent_current_frame": parent_current_frame,
            "candidate_batch": batch,
            "candidates": candidates,
            "selection": selection,
            "selected_candidate": selected,
            "focus_authorization": focus_authorization,
            "focus_decision": focus_decision,
            "focus_plan": focus_plan,
            "focus_action": focus_action,
            "child_plan": child_plan,
            "reacquisition_authorization": reacquisition_authorization,
            "reacquisition_request": request,
            "reacquisition_eligibility": eligibility,
            "reacquisition_action": reacquisition_action,
            **child_result,
            "fixture_manifest_id": manifest_id,
            "fixture_manifest_consumed_by_runtime": False,
            "source_trace_refs": source_trace_refs,
            "readback_loaded_monotonic_ns": readback_loaded_ns,
            "readback_score": parent_active.get("readback_score"),
            "candidate_evaluated_monotonic_ns": parent_active.get(
                "candidate_evaluated_monotonic_ns"
            ),
            "first_action_scored_monotonic_ns": parent_active.get(
                "first_action_scored_monotonic_ns"
            ),
            "first_action_executed_monotonic_ns": parent_active.get(
                "first_action_executed_monotonic_ns"
            ),
        }
    finally:
        stimulus.close()


def _new_parent_active_state() -> dict[str, Any]:
    return {
        "checkpoint_index": 0,
        "coverage_records": [],
        "compilation_cache": {},
        "frame_payload_cache": {},
        "visual_changes": [],
        "baseline_artifact_id": None,
        "identity_before": None,
        "identity_after": None,
        "observation_window": None,
        "authorization": None,
        "tail_result": None,
        "candidate": None,
        "policy": None,
        "action": None,
        "execution": None,
        "readback_score": None,
        "candidate_evaluated_monotonic_ns": None,
        "first_action_scored_monotonic_ns": None,
        "first_action_executed_monotonic_ns": None,
    }


def _inspect_parent_extension_checkpoint(
    *,
    path: Path,
    cycle_index: int,
    experiment_run_id: str,
    binding: Any,
    configs: dict[str, Any],
    window_source: WindowsBoundedWindowCaptureSource,
    sensor_store: ContentAddressedSensorArtifactStore,
    compiler: HardSoftPerceptionPrimitiveCompiler,
    primitive_store: PerceptionPrimitiveStore,
    p125_store: Package125ObservationExtensionStore,
    snapshot: ActiveReacquisitionCaptureSnapshot,
    controller: BoundedCaptureDeadlineController,
    active: dict[str, Any],
    working_readback: tuple[dict[str, Any], ...],
    expected_evidence_snapshot_id: str,
    expected_evidence_identity_sha256: str,
) -> None:
    elapsed_ns = (
        snapshot.observed_at_monotonic_ns
        - snapshot.started_monotonic_ns
    )
    if active["identity_before"] is None and snapshot.capture_session_refs:
        screen_session_id = snapshot.capture_session_refs[0]
        host_session_id = snapshot.capture_session_refs[-1]
        identity = _build_parent_capture_identity(
            stage="capture_started",
            experiment_run_id=experiment_run_id,
            snapshot=snapshot,
            binding=binding,
            configs=configs,
            window_source=window_source,
            screen_session_id=screen_session_id,
            host_session_id=host_session_id,
            observed_deadline_ns=PARENT_BASE_WINDOW_NS,
        )
        active["identity_before"] = identity
        p125_store.append_record(
            "active_capture_session_identities", identity
        )
        observation = ObservationWindowState(
            observation_window_id=snapshot.observation_window_id,
            observation_window_state_id=stable_id(
                "package_129_parent_observation_window_state"
            ),
            schema_version=OBSERVATION_WINDOW_STATE_SCHEMA_VERSION,
            created_at=utc_now(),
            runtime_session_id=snapshot.runtime_session_id,
            perception_session_id=snapshot.perception_session_id,
            participating_lanes=PARTICIPATING_LANES,
            required_lanes=PARTICIPATING_LANES,
            base_start_event_time_ns=0,
            base_deadline_event_time_ns=PARENT_BASE_WINDOW_NS,
            current_deadline_event_time_ns=PARENT_BASE_WINDOW_NS,
            hard_deadline_event_time_ns=PARENT_HARD_WINDOW_NS,
            extension_count=0,
            total_extension_ns=0,
            window_status="observing_base_window",
            operator_stop_requested=False,
            operator_pause_requested=False,
            source_record_refs=tuple(snapshot.capture_session_refs),
            source_trace_refs=tuple(),
            experiment_run_id=experiment_run_id,
            audit_group_id=experiment_run_id,
            scenario_name="package_129_late_event",
            capture_mode="real_active_capture",
            active_capture_identity_id=identity.active_capture_identity_id,
            alignment_origin_monotonic_ns=snapshot.started_monotonic_ns,
            clock_domain_ids=(
                f"package_129_parent_clock:{snapshot.runtime_session_id}",
            ),
            transport_flush_record_id=None,
        )
        authorization = build_observation_extension_authorization(
            runtime_session_id=snapshot.runtime_session_id,
            perception_session_id=snapshot.perception_session_id,
            bounded_extension_allowed=True,
        )
        active["observation_window"] = observation
        active["authorization"] = authorization
        p125_store.append_record("observation_window_states", observation)
        p125_store.append_record(
            "observation_window_authorizations", authorization
        )

    checkpoint_index = int(active["checkpoint_index"])
    if checkpoint_index >= len(PARENT_CHECKPOINT_NS):
        return
    if elapsed_ns < PARENT_CHECKPOINT_NS[checkpoint_index]:
        return
    if not (snapshot.screen_artifact_ids and snapshot.host_artifact_ids):
        return
    coverage = _build_parent_coverage(
        cycle_index=cycle_index,
        experiment_run_id=experiment_run_id,
        snapshot=snapshot,
        sensor_store=sensor_store,
        compiler=compiler,
        primitive_store=primitive_store,
        active=active,
        window_index=checkpoint_index,
    )
    active["coverage_records"].append(coverage)
    active["checkpoint_index"] = checkpoint_index + 1
    if active["execution"] is not None:
        return
    observation = active["observation_window"]
    tail_result = build_temporal_tail_evidence(
        observation_window=observation,
        coverage_records=tuple(active["coverage_records"]),
        temporal_bundle_or_context_id=(
            f"package_129_parent_live_tail:{experiment_run_id}"
        ),
        evaluated_at_event_time_ns=min(
            PARENT_BASE_WINDOW_NS,
            int(coverage.end_event_time_ns),
        ),
        clock_domain_id=observation.clock_domain_ids[0],
    )
    active["tail_result"] = tail_result
    p125_store.append_record(
        "temporal_tail_evidence", tail_result.tail_evidence
    )
    for region in tail_result.open_regions:
        p125_store.append_record(
            "open_temporal_region_observations", region
        )
    candidate = create_observation_extension_candidate(
        observation_window=observation,
        tail_evidence=tail_result.tail_evidence,
        authorization=active["authorization"],
        requested_extension_ns=PARENT_EXTENSION_NS,
    )
    if candidate is None:
        return
    active["candidate"] = candidate
    active["candidate_evaluated_monotonic_ns"] = monotonic_ns()
    p125_store.append_record(
        "observation_extension_candidates", candidate
    )
    if cycle_index == 2:
        score_result = score_extension_candidate_with_working_readback(
            extension_candidate=candidate,
            working_readback_items=working_readback,
            expected_evidence_snapshot_id=expected_evidence_snapshot_id,
            expected_evidence_identity_sha256=(
                expected_evidence_identity_sha256
            ),
        )
        active["first_action_scored_monotonic_ns"] = monotonic_ns()
        active["readback_score"] = score_result
    policy = decide_observation_extension_policy(
        candidate=candidate,
        authorization=active["authorization"],
        observation_window=observation,
        transport_integrity_valid=True,
        same_sensor_configuration=True,
    )
    active["policy"] = policy
    p125_store.append_record(
        "observation_extension_policy_decisions", policy
    )
    action = create_bounded_observation_extension_internal_action(
        policy_decision=policy,
        observation_window=observation,
    )
    if action is None:
        raise RuntimeError("Package 125 policy allowed no extension action")
    active["action"] = action
    p125_store.append_record(
        "observation_extension_internal_actions", action
    )

    def snapshot_after(deadline_ns: int) -> ActiveCaptureSessionIdentity:
        identity_after = _build_parent_capture_identity(
            stage="deadline_extended",
            experiment_run_id=experiment_run_id,
            snapshot=snapshot,
            binding=binding,
            configs=configs,
            window_source=window_source,
            screen_session_id=snapshot.capture_session_refs[0],
            host_session_id=snapshot.capture_session_refs[-1],
            observed_deadline_ns=deadline_ns,
        )
        active["identity_after"] = identity_after
        p125_store.append_record(
            "active_capture_session_identities", identity_after
        )
        return identity_after

    execution = execute_bounded_observation_extension(
        action=action,
        controller=controller,
        previous_deadline_ns=PARENT_BASE_WINDOW_NS,
        participating_lanes=PARTICIPATING_LANES,
        capture_identity_before=active["identity_before"],
        capture_identity_snapshotter=snapshot_after,
    )
    if execution.execution_status != "applied":
        raise RuntimeError(
            f"Package 125 extension failed: {execution.failure_kind}"
        )
    active["execution"] = execution
    active["first_action_executed_monotonic_ns"] = monotonic_ns()
    p125_store.append_record(
        "observation_extension_executions", execution
    )


def _build_parent_coverage(
    *,
    cycle_index: int,
    experiment_run_id: str,
    snapshot: ActiveReacquisitionCaptureSnapshot,
    sensor_store: ContentAddressedSensorArtifactStore,
    compiler: HardSoftPerceptionPrimitiveCompiler,
    primitive_store: PerceptionPrimitiveStore,
    active: dict[str, Any],
    window_index: int,
) -> AlignmentWindowCoverageRecord:
    current_id = snapshot.screen_artifact_ids[-1]
    baseline_id = active.get("baseline_artifact_id")
    if baseline_id is None:
        artifacts = tuple(
            sensor_store.get_artifact(artifact_id)
            for artifact_id in snapshot.screen_artifact_ids
        )
        counts: dict[str, int] = {}
        for artifact in artifacts:
            content_hash = str(artifact["content_sha256"])
            counts[content_hash] = counts.get(content_hash, 0) + 1
        stable_hash = max(
            counts,
            key=lambda item: (counts[item], item),
        )
        baseline_id = next(
            str(artifact["artifact_id"])
            for artifact in reversed(artifacts)
            if artifact["content_sha256"] == stable_hash
        )
        active["baseline_artifact_id"] = baseline_id
    host_id = snapshot.host_artifact_ids[-1]
    for artifact_id in (baseline_id, current_id, host_id):
        if artifact_id not in active["compilation_cache"]:
            active["compilation_cache"][artifact_id] = (
                compiler.compile_artifact(artifact_id)
            )
    baseline_bundle = active["compilation_cache"][baseline_id]
    current_bundle = active["compilation_cache"][current_id]
    host_bundle = active["compilation_cache"][host_id]
    for bundle in (baseline_bundle, current_bundle):
        if bundle.primitive_record_id not in active["frame_payload_cache"]:
            active["frame_payload_cache"][bundle.primitive_record_id] = (
                primitive_store.get_primitive(bundle.primitive_record_id)
            )
    from ashl_core_v1.perception.visual_change_primitive_compiler import (
        compile_visual_change_primitive,
    )
    from ashl_core_v1.perception.visual_primitive_schema import (
        VisualFramePrimitiveRecord,
    )

    previous = VisualFramePrimitiveRecord(
        **active["frame_payload_cache"][baseline_bundle.primitive_record_id]
    )
    current = VisualFramePrimitiveRecord(
        **active["frame_payload_cache"][current_bundle.primitive_record_id]
    )
    change = compile_visual_change_primitive(previous, current)
    primitive_store.append_visual_change_primitive(change)
    active["visual_changes"].append(
        (change.to_dict(), current.to_dict())
    )
    screen_artifact = sensor_store.get_artifact(current_id)
    host_artifact = sensor_store.get_artifact(host_id)
    relative_ns = max(
        0,
        min(
            int(screen_artifact["captured_at_monotonic_ns"]),
            int(host_artifact["captured_at_monotonic_ns"]),
        )
        - snapshot.started_monotonic_ns,
    )
    screen = AlignmentLaneCoverage(
        lane="screen",
        schema_version=ALIGNMENT_LANE_COVERAGE_SCHEMA_VERSION,
        source_artifact_present=True,
        compiled_primitive_present=True,
        delivered_to_alignment=True,
        salient_change_present=bool(
            change.changed_grid_cells
            and float(change.maximum_grid_difference)
            >= PARENT_STRUCTURAL_CHANGE_FLOOR
        ),
        dropped_record_count=0,
        capture_failure_count=0,
        compile_failure_count=0,
        source_artifact_refs=(current_id,),
        primitive_record_refs=(
            current_bundle.primitive_record_id,
            change.visual_change_id,
        ),
    )
    audio = AlignmentLaneCoverage(
        lane="microphone",
        schema_version=ALIGNMENT_LANE_COVERAGE_SCHEMA_VERSION,
        source_artifact_present=False,
        compiled_primitive_present=False,
        delivered_to_alignment=False,
        salient_change_present=False,
        dropped_record_count=0,
        capture_failure_count=0,
        compile_failure_count=0,
        source_artifact_refs=tuple(),
        primitive_record_refs=tuple(),
    )
    host = AlignmentLaneCoverage(
        lane="host_state",
        schema_version=ALIGNMENT_LANE_COVERAGE_SCHEMA_VERSION,
        source_artifact_present=True,
        compiled_primitive_present=True,
        delivered_to_alignment=True,
        salient_change_present=False,
        dropped_record_count=0,
        capture_failure_count=0,
        compile_failure_count=0,
        source_artifact_refs=(host_id,),
        primitive_record_refs=(host_bundle.primitive_record_id,),
    )
    return AlignmentWindowCoverageRecord(
        coverage_record_id=stable_id(
            "package_129_parent_alignment_coverage"
        ),
        schema_version=ALIGNMENT_WINDOW_COVERAGE_SCHEMA_VERSION,
        created_at=utc_now(),
        experiment_run_id=experiment_run_id,
        cycle_index=cycle_index,
        alignment_window_id=(
            f"package_129_parent_alignment:{cycle_index}:{window_index}"
        ),
        window_index=window_index,
        start_event_time_ns=relative_ns,
        end_event_time_ns=relative_ns,
        screen=screen,
        audio=audio,
        host_state=host,
        full_window_inside_common_envelope=True,
        partial_edge_window=False,
        required_lanes_complete=screen.complete and host.complete,
        visual_audio_overlap_present=False,
        incomplete_reason_codes=tuple(),
        source_trace_refs=tuple(
            dict.fromkeys(
                tuple(current_bundle.source_trace_refs)
                + tuple(host_bundle.source_trace_refs)
            )
        ),
    )


def _build_parent_capture_identity(
    *,
    stage: str,
    experiment_run_id: str,
    snapshot: ActiveReacquisitionCaptureSnapshot,
    binding: Any,
    configs: dict[str, Any],
    window_source: WindowsBoundedWindowCaptureSource,
    screen_session_id: str,
    host_session_id: str,
    observed_deadline_ns: int,
) -> ActiveCaptureSessionIdentity:
    return ActiveCaptureSessionIdentity(
        active_capture_identity_id=stable_id(
            "package_129_active_capture_identity"
        ),
        schema_version=ACTIVE_CAPTURE_SESSION_IDENTITY_SCHEMA_VERSION,
        created_at=utc_now(),
        identity_stage=stage,
        experiment_run_id=experiment_run_id,
        audit_group_id=experiment_run_id,
        scenario_name="package_129_late_event",
        runtime_session_id=snapshot.runtime_session_id,
        perception_session_id=snapshot.perception_session_id,
        observation_window_id=snapshot.observation_window_id,
        screen_capture_session_id=screen_session_id,
        audio_capture_session_id="not_participating_by_design",
        host_state_capture_session_id=host_session_id,
        screen_descriptor_id=(
            window_source.descriptor().device_descriptor_id
        ),
        audio_descriptor_id="not_participating_by_design",
        host_state_descriptor_id=(
            configs["host_descriptor"].device_descriptor_id
        ),
        screen_config_sha256=configs[
            "screen"
        ].capture_config_sha256,
        audio_config_sha256="not_participating_by_design",
        host_state_config_sha256=configs[
            "host"
        ].capture_config_sha256,
        window_handle=int(binding.target_hwnd),
        render_endpoint_id="not_participating_by_design",
        alignment_origin_monotonic_ns=snapshot.started_monotonic_ns,
        clock_domain_ids=(
            f"package_129_parent_clock:{snapshot.runtime_session_id}",
        ),
        observed_deadline_ns=int(observed_deadline_ns),
        real_source_capture=True,
        sources_open=True,
        sources_reopened=False,
        source_record_refs=(
            screen_session_id,
            host_session_id,
            "audio:not_participating_by_design",
        ),
        source_trace_refs=tuple(),
    )


def _finalize_parent_extension(
    *,
    parent: dict[str, Any],
    controller: BoundedCaptureDeadlineController,
    active: dict[str, Any],
    p125_store: Package125ObservationExtensionStore,
) -> dict[str, Any]:
    if (
        active["execution"] is None
        or controller.extension_count != 1
        or controller.current_deadline_ns() != PARENT_FINAL_WINDOW_NS
    ):
        raise RuntimeError("Package 129 parent did not extend exactly once")
    tail_result = active["tail_result"]
    closure_links = build_closure_links(
        open_regions=tail_result.open_regions,
        coverage_records=tuple(active["coverage_records"]),
        base_deadline_event_time_ns=PARENT_BASE_WINDOW_NS,
        final_deadline_event_time_ns=PARENT_FINAL_WINDOW_NS,
        clock_domain_id=active["observation_window"].clock_domain_ids[0],
    )
    if not closure_links or not any(
        int(item.closure_event_time_ns) > PARENT_BASE_WINDOW_NS
        for item in closure_links
    ):
        raise RuntimeError(
            "Package 129 parent event did not close after base deadline"
        )
    for link in closure_links:
        p125_store.append_record("temporal_region_closure_links", link)
    final_state = replace(
        active["observation_window"],
        observation_window_state_id=stable_id(
            "package_129_parent_observation_window_state"
        ),
        created_at=utc_now(),
        current_deadline_event_time_ns=PARENT_FINAL_WINDOW_NS,
        extension_count=1,
        total_extension_ns=PARENT_EXTENSION_NS,
        window_status="completed",
        active_capture_identity_id=(
            active["identity_after"].active_capture_identity_id
        ),
        transport_flush_record_id=parent["transport_flush_record_id"],
        source_record_refs=(
            active["execution"].extension_execution_id,
            parent["transport_flush_record_id"],
            parent["temporal_bundle_id"],
        ),
        source_trace_refs=tuple(parent.get("source_trace_refs") or ()),
    )
    p125_store.append_record("observation_window_states", final_state)
    closure_time = max(int(item.closure_event_time_ns) for item in closure_links)
    post_context_ns = max(0, PARENT_FINAL_WINDOW_NS - closure_time)
    outcome = ObservationWindowExtensionOutcome(
        extension_outcome_id=stable_id(
            "package_129_observation_extension_outcome"
        ),
        schema_version=OBSERVATION_EXTENSION_OUTCOME_SCHEMA_VERSION,
        created_at=utc_now(),
        extension_execution_id=active["execution"].extension_execution_id,
        observation_window_id=parent["observation_window_id"],
        additional_observation_ns=PARENT_EXTENSION_NS,
        open_visual_regions_before=len(
            tail_result.tail_evidence.open_visual_region_refs
        ),
        open_audio_regions_before=0,
        finalized_visual_spans_after=len(closure_links),
        finalized_audio_spans_after=0,
        post_event_context_ns=post_context_ns,
        required_lane_drops=parent["required_lane_drop_count"],
        transport_faults=parent["backpressure_fault_count"],
        capture_failures=parent["capture_failure_count"],
        compile_failures=parent["compile_failure_count"],
        extension_effect_status="event_closure_observed",
        semantic_interpretation_created=False,
        source_record_refs=(
            active["execution"].extension_execution_id,
            parent["transport_flush_record_id"],
            parent["temporal_bundle_id"],
        )
        + tuple(item.closure_link_id for item in closure_links),
        source_trace_refs=tuple(parent.get("source_trace_refs") or ()),
        runtime_session_id=parent["runtime_session_id"],
        perception_session_id=parent["perception_session_id"],
        experiment_run_id=active[
            "observation_window"
        ].experiment_run_id,
        audit_group_id=active["observation_window"].audit_group_id,
        scenario_name=active["observation_window"].scenario_name,
    )
    p125_store.append_record("observation_extension_outcomes", outcome)
    comparison = ObservationExtensionEffectComparison(
        comparison_id=stable_id(
            "package_129_observation_extension_comparison"
        ),
        schema_version=OBSERVATION_EXTENSION_COMPARISON_SCHEMA_VERSION,
        created_at=utc_now(),
        observation_window_id=parent["observation_window_id"],
        base_boundary_event_time_ns=PARENT_BASE_WINDOW_NS,
        final_boundary_event_time_ns=PARENT_FINAL_WINDOW_NS,
        base_tail_evidence_id=(
            tail_result.tail_evidence.temporal_tail_evidence_id
        ),
        final_temporal_bundle_id=parent["temporal_bundle_id"],
        base_open_region_count=len(tail_result.open_regions),
        final_open_region_count=0,
        newly_observed_closure_count=len(closure_links),
        newly_observed_post_event_context_ns=post_context_ns,
        same_source_sessions=True,
        same_alignment_origin=True,
        extension_changed_capture_result=True,
        memory_influence_used=False,
        stimulus_ground_truth_used_for_runtime_decision=False,
        source_trace_refs=tuple(parent.get("source_trace_refs") or ()),
        runtime_session_id=parent["runtime_session_id"],
        perception_session_id=parent["perception_session_id"],
        experiment_run_id=active[
            "observation_window"
        ].experiment_run_id,
        audit_group_id=active["observation_window"].audit_group_id,
        scenario_name=active["observation_window"].scenario_name,
        extension_execution_id=active["execution"].extension_execution_id,
        extension_outcome_id=outcome.extension_outcome_id,
        capture_identity_before_id=(
            active["identity_before"].active_capture_identity_id
        ),
        capture_identity_after_id=(
            active["identity_after"].active_capture_identity_id
        ),
        transport_flush_record_id=parent["transport_flush_record_id"],
        transport_flush_verified=parent["flush_remaining_count"] == 0,
        flush_remaining_required_records=parent[
            "flush_remaining_count"
        ],
    )
    p125_store.append_record(
        "observation_extension_comparisons", comparison
    )
    return {
        "tail_result": tail_result,
        "authorization": active["authorization"],
        "candidate": active["candidate"],
        "policy": active["policy"],
        "action": active["action"],
        "execution": active["execution"],
        "closure_links": closure_links,
        "outcome": outcome,
        "comparison": comparison,
        "final_state": final_state,
    }


def _strongest_actual_change(
    *, active: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    eligible = tuple(
        pair
        for pair in active["visual_changes"]
        if len(pair[0].get("changed_grid_cells") or ()) >= 2
    )
    if not eligible:
        raise RuntimeError("no actual multi-cell visual change was compiled")
    return max(
        eligible,
        key=lambda pair: (
            float(pair[0].get("maximum_grid_difference", 0.0)),
            len(pair[0].get("changed_grid_cells") or ()),
        ),
    )


def _capture_focused_child_with_structural_stop(
    *,
    path: Path,
    stimulus: LocalActivePerceptionGrowthStimulusRuntime,
    window_source: WindowsBoundedWindowCaptureSource,
    host_adapter: HostStateSensorAdapter,
    binding: Any,
    configs: dict[str, Any],
    experiment_run_id: str,
    root_event_id: str,
    parent: dict[str, Any],
    parent_ref: Any,
    parent_plan: Any,
    focus_plan: Any,
    focus_action: Any,
    child_plan: Any,
    child_ids: dict[str, str],
    reacquisition_action: Any,
    p126_store: Package126ReacquisitionStore,
    p127_store: Package127InternalFocusStore,
    p128_store: Package128SufficiencyStopStore,
    sensor_store: ContentAddressedSensorArtifactStore,
    temporal_store: Package124ATemporalStore,
    compiler: HardSoftPerceptionPrimitiveCompiler,
    primitive_store: PerceptionPrimitiveStore,
    package_122: BoundedMultimodalPerceptionSessionRuntime,
    strict_event_stream: bool,
) -> dict[str, Any]:
    controller = BoundedCaptureDeadlineController(
        base_deadline_ns=CHILD_HARD_WINDOW_NS,
        hard_deadline_ns=CHILD_HARD_WINDOW_NS,
        participating_lanes=PARTICIPATING_LANES,
        maximum_extension_count=0,
        maximum_total_extension_ns=0,
    )
    alignment_config = _build_live_alignment_config(
        path=path,
        participating_lanes=PARTICIPATING_LANES,
        window_duration_ns=CHILD_HARD_WINDOW_NS,
        queue_depth=64,
        alignment_window_ms=ACTIVE_ALIGNMENT_WINDOW_MS,
    )
    compilation_cache: dict[str, Any] = {}
    lane_item_cache: dict[str, Any] = {}
    active: dict[str, Any] = {
        "contract": None,
        "active_sidecar": None,
        "initial_view": None,
        "latest_view": None,
        "active_clock": None,
        "baseline_frame": None,
        "baseline_artifact_id": None,
        "next_checkpoint_ns": None,
        "checkpoints": [],
        "assessments": [],
        "decisions": [],
        "stop_action": None,
        "stop_requested_event_time_ns": None,
        "observed_region_refs": [],
        "open_region_ref": None,
        "open_region_started_ns": None,
        "closed_spans": [],
        "temporal_records": [],
        "focused_evidence_view_ids": [],
        "initial_capture_session_refs": tuple(),
        "initial_alignment_origin_ref": None,
    }

    def compile_cached(artifact_id: str) -> Any:
        if artifact_id not in compilation_cache:
            compilation_cache[artifact_id] = compiler.compile_artifact(
                artifact_id
            )
        return compilation_cache[artifact_id]

    def lane_item_for(
        artifact_id: str,
        *,
        started_ns: int,
        perception_session_id: str,
    ) -> Any:
        if artifact_id not in lane_item_cache:
            bundle = compile_cached(artifact_id)
            artifact = sensor_store.get_artifact(artifact_id)
            relative_ms = max(
                0,
                (
                    int(artifact["captured_at_monotonic_ns"])
                    - started_ns
                )
                // 1_000_000,
            )
            lane_item_cache[artifact_id] = (
                package_122.lane_item_from_compilation(
                    session_id=perception_session_id,
                    session_relative_ms=relative_ms,
                    compilation_bundle=bundle,
                )
            )
        return lane_item_cache[artifact_id]

    def active_hook(snapshot: ActiveReacquisitionCaptureSnapshot) -> None:
        if not (snapshot.screen_artifact_ids and snapshot.host_artifact_ids):
            return
        screen_items = tuple(
            lane_item_for(
                artifact_id,
                started_ns=snapshot.started_monotonic_ns,
                perception_session_id=snapshot.perception_session_id,
            )
            for artifact_id in snapshot.screen_artifact_ids
        )
        host_items = tuple(
            lane_item_for(
                artifact_id,
                started_ns=snapshot.started_monotonic_ns,
                perception_session_id=snapshot.perception_session_id,
            )
            for artifact_id in snapshot.host_artifact_ids
        )
        lane_items = screen_items + host_items
        if active["contract"] is None:
            _initialize_active_contract(
                path=path,
                store=p128_store,
                focus_store=p127_store,
                temporal_store=temporal_store,
                package_122=package_122,
                primitive_store=primitive_store,
                focus_plan=focus_plan,
                focus_action_id=focus_action.internal_action_id,
                reacquisition_action_id=(
                    reacquisition_action.internal_action_id
                ),
                snapshot=snapshot,
                first_screen_bundle=compile_cached(
                    snapshot.screen_artifact_ids[0]
                ),
                first_screen_lane_item=screen_items[0],
                active=active,
                strict_event_stream=strict_event_stream,
            )
        if (
            snapshot.observed_at_monotonic_ns
            < int(active["next_checkpoint_ns"])
            or len(active["checkpoints"]) >= MAXIMUM_CHECKPOINT_COUNT
            or controller.stop_requested
        ):
            return
        if active["closed_spans"]:
            closure_ns = int(active["closed_spans"][-1].end_event_time_ns)
            latest_screen = sensor_store.get_artifact(
                snapshot.screen_artifact_ids[-1]
            )
            latest_host = sensor_store.get_artifact(
                snapshot.host_artifact_ids[-1]
            )
            coverage_ns = min(
                int(latest_screen["captured_at_monotonic_ns"]),
                int(latest_host["captured_at_monotonic_ns"]),
            )
            if coverage_ns < closure_ns + MINIMUM_POST_EVENT_COVERAGE_NS:
                return
        _evaluate_active_checkpoint(
            path=path,
            store=p128_store,
            focus_store=p127_store,
            sensor_store=sensor_store,
            temporal_store=temporal_store,
            primitive_store=primitive_store,
            package_122=package_122,
            alignment_config=alignment_config,
            focus_plan=focus_plan,
            snapshot=snapshot,
            lane_items=lane_items,
            compilation_cache=compilation_cache,
            active=active,
            controller=controller,
            contract_authorized=True,
            strict_event_stream=strict_event_stream,
        )
        active["next_checkpoint_ns"] = (
            active["checkpoints"][-1].evaluated_at_event_time_ns
            + CHECKPOINT_INTERVAL_NS
        )

    stimulus.begin_child_phase()
    child = capture_one_bounded_reacquisition_window(
        path=path,
        store=p126_store,
        sensor_store=sensor_store,
        temporal_store=temporal_store,
        compiler=compiler,
        primitive_store=primitive_store,
        stimulus=stimulus,
        window_source=window_source,
        audio_source=None,
        host_adapter=host_adapter,
        binding=binding,
        configs=configs,
        action_kind="capture_again",
        experiment_run_id=experiment_run_id,
        root_event_id=root_event_id,
        plan=child_plan,
        role="package_129_focused_child",
        participating_lanes=PARTICIPATING_LANES,
        forced_ids=child_ids,
        window_duration_ns=CHILD_HARD_WINDOW_NS,
        source_sample_interval_ns=SOURCE_SAMPLE_INTERVAL_NS,
        deadline_controller=controller,
        active_capture_hook=active_hook,
        compile_all_samples=True,
        compilation_cache=compilation_cache,
        alignment_window_ms=ACTIVE_ALIGNMENT_WINDOW_MS,
        stop_event_time_provider=lambda: active[
            "stop_requested_event_time_ns"
        ],
    )
    if not active["assessments"] or active["stop_action"] is None:
        raise RuntimeError(
            "Package 128 structural stop was not reached in Package 129 child"
        )
    final_assessment = active["assessments"][-1]
    final_decision = active["decisions"][-1]
    if (
        final_assessment.assessment_status != "sufficient"
        or final_decision.decision != "allow_policy_stop"
    ):
        raise RuntimeError("Package 128 child did not finish sufficient")
    continuity = build_cross_window_temporal_link(
        parent_observation_window_id=parent["observation_window_id"],
        child_observation_window_id=child["observation_window_id"],
        parent_final_anchor_ref=parent["end_anchor_id"],
        child_start_anchor_ref=child["start_anchor_id"],
        parent_final_event_time_ns=parent["ended_monotonic_ns"],
        child_start_event_time_ns=child["started_monotonic_ns"],
        parent_clock_domain=parent_plan.event_clock_domain,
        child_clock_domain=child_plan.event_clock_domain,
        parent_processing_clock_domain=(
            parent_plan.processing_clock_domain
        ),
        child_processing_clock_domain=(
            child_plan.processing_clock_domain
        ),
        source_temporal_refs=(
            parent["temporal_bundle_id"],
            child["temporal_bundle_id"],
        ),
        source_record_refs=(
            parent_ref.completed_window_reference_id,
            reacquisition_action.internal_action_id,
            focus_action.internal_action_id,
        ),
    )
    p126_store.append_record(
        "cross_window_temporal_links", continuity
    )
    shared_sessions = set(parent["capture_session_refs"]).intersection(
        child["capture_session_refs"]
    )
    targets_equal = target_identity_equal(parent_plan, child_plan)
    configs_equal = configuration_identity_equal(parent_plan, child_plan)
    execution = ReacquisitionCaptureExecution(
        reacquisition_execution_id=stable_id(
            "package_129_reacquisition_execution"
        ),
        schema_version="ashl_package_126_reacquisition_capture_execution_v0",
        created_at=utc_now(),
        internal_action_id=reacquisition_action.internal_action_id,
        parent_runtime_session_id=parent["runtime_session_id"],
        parent_perception_session_id=parent["perception_session_id"],
        parent_observation_window_id=parent["observation_window_id"],
        child_runtime_session_id=child["runtime_session_id"],
        child_perception_session_id=child["perception_session_id"],
        child_observation_window_id=child["observation_window_id"],
        parent_plan_identity_ref=parent_plan.sampling_plan_identity_id,
        child_plan_identity_ref=child_plan.sampling_plan_identity_id,
        parent_capture_session_refs=tuple(parent["capture_session_refs"]),
        child_capture_session_refs=tuple(child["capture_session_refs"]),
        parent_alignment_origin_ref=parent["start_anchor_id"],
        child_alignment_origin_ref=child["start_anchor_id"],
        event_clock_domain_preserved=True,
        processing_clock_domain_preserved=True,
        capture_session_ids_reused=bool(shared_sessions),
        source_targets_preserved=targets_equal,
        source_configuration_preserved=configs_equal,
        privacy_policy_preserved=True,
        sources_reopened=bool(
            not shared_sessions
            and targets_equal
            and configs_equal
            and parent["sessions_stopped"]
            and child["sessions_started"]
        ),
        old_artifact_reused=False,
        requested_window_ns=reacquisition_action.requested_window_ns,
        actual_window_ns=child["actual_window_ns"],
        execution_status="completed_clean",
        failure_kind=None,
        source_record_refs=(
            reacquisition_action.internal_action_id,
            parent["observation_window_state_id"],
            child["observation_window_state_id"],
        )
        + tuple(parent["capture_session_refs"])
        + tuple(child["capture_session_refs"]),
        source_trace_refs=tuple(child.get("source_trace_refs") or ()),
    )
    p126_store.append_record(
        "reacquisition_capture_executions", execution
    )
    evidence_summary = _build_evidence_summary(
        execution, child, "capture_again"
    )
    p126_store.append_record(
        "reacquired_evidence_summaries", evidence_summary
    )
    final_temporal_bundle = _build_final_temporal_bundle(
        temporal_store=temporal_store,
        child=child,
        active=active,
    )
    child_for_completion = dict(child)
    child_for_completion["temporal_bundle_id"] = (
        final_temporal_bundle.temporal_bundle_id
    )
    active_sidecar = active["active_sidecar"]
    latest_view = active["latest_view"]
    released_sidecar = build_focus_context_sidecar(
        plan=focus_plan,
        view=latest_view,
        full_frame_perception_readable_data_id=(
            latest_view.source_perception_readable_data_id
        ),
        active_from_event_time_ns=child["started_monotonic_ns"],
        active_until_event_time_ns=child["ended_monotonic_ns"],
        focus_state="released",
    )
    package_122.attach_internal_perception_focus_context(
        released_sidecar
    )
    p127_store.append_record(
        "internal_focus_context_sidecars", released_sidecar
    )
    release = build_focus_release_record(sidecar=active_sidecar)
    p127_store.append_record(
        "internal_focus_release_records", release
    )
    stop_execution = build_observation_stop_execution(
        action=active["stop_action"],
        controller=controller,
        child_window=child_for_completion,
        stop_requested_at_event_time_ns=int(
            active["stop_requested_event_time_ns"]
        ),
        focus_context_id_before=active_sidecar.focus_context_id,
        focus_context_id_at_completion=active_sidecar.focus_context_id,
        active_capture_session_refs=active[
            "initial_capture_session_refs"
        ],
        active_alignment_origin_ref=active[
            "initial_alignment_origin_ref"
        ],
    )
    p128_store.append_record(
        "observation_stop_executions", stop_execution
    )
    completion = build_observation_completion(
        contract=active["contract"],
        assessment=final_assessment,
        decision=final_decision,
        execution=stop_execution,
        child_window=child_for_completion,
        final_focus_context_id=released_sidecar.focus_context_id,
    )
    p128_store.append_record(
        "observation_completion_records", completion
    )
    if not (
        int(child["actual_window_ns"]) < CHILD_HARD_WINDOW_NS
        and child["flush_remaining_count"] == 0
        and stop_execution.all_required_lanes_received_stop
        and released_sidecar.automatically_released
    ):
        raise RuntimeError("Package 129 focused child completion gate failed")
    return {
        "child": child,
        "continuity": continuity,
        "reacquisition_execution": execution,
        "reacquired_evidence_summary": evidence_summary,
        "focus_active_sidecar": active_sidecar,
        "focus_latest_view": latest_view,
        "focus_released_sidecar": released_sidecar,
        "focus_release": release,
        "structural_contract": active["contract"],
        "structural_checkpoints": tuple(active["checkpoints"]),
        "structural_assessments": tuple(active["assessments"]),
        "stop_policy_decision": final_decision,
        "stop_action": active["stop_action"],
        "stop_execution": stop_execution,
        "completion": completion,
        "final_temporal_bundle": final_temporal_bundle,
    }


def _build_stage_records(
    *,
    cycle_index: int,
    sequence: dict[str, Any],
) -> tuple[ActivePerceptionStageRecord, ...]:
    parent = sequence["parent"]
    child = sequence["child"]
    extension = sequence["parent_extension"]
    trace_refs = tuple(sequence["source_trace_refs"])
    parent_counts = {
        "required_lane_drop_count": int(
            parent["required_lane_drop_count"]
        ),
        "backpressure_fault_count": int(
            parent["backpressure_fault_count"]
        ),
        "capture_failure_count": int(parent["capture_failure_count"]),
        "compile_failure_count": int(parent["compile_failure_count"]),
        "flush_remaining_count": int(parent["flush_remaining_count"]),
    }
    child_counts = {
        "required_lane_drop_count": int(
            child["required_lane_drop_count"]
        ),
        "backpressure_fault_count": int(
            child["backpressure_fault_count"]
        ),
        "capture_failure_count": int(child["capture_failure_count"]),
        "compile_failure_count": int(child["compile_failure_count"]),
        "flush_remaining_count": int(child["flush_remaining_count"]),
    }
    records = (
        ActivePerceptionStageRecord(
            stage_record_id=stable_id(
                f"package_129_cycle_{cycle_index}_late_event_extension"
            ),
            schema_version=STAGE_SCHEMA_VERSION,
            created_at=utc_now(),
            cycle_index=cycle_index,
            stage_index=1,
            stage_kind="late_event_extension",
            runtime_session_id=parent["runtime_session_id"],
            perception_session_id=parent["perception_session_id"],
            observation_window_id=parent["observation_window_id"],
            source_evidence_refs=(
                extension["tail_result"].tail_evidence.temporal_tail_evidence_id,
                extension["outcome"].extension_outcome_id,
            )
            + tuple(
                item.closure_link_id
                for item in extension["closure_links"]
            ),
            policy_decision_refs=(
                extension["policy"].extension_policy_decision_id,
            ),
            internal_action_kind="extend_observation_window",
            internal_action_id=extension["action"].internal_action_id,
            execution_record_id=(
                extension["execution"].extension_execution_id
            ),
            stage_status="completed",
            semantic_label=None,
            source_record_refs=(
                extension["candidate"].extension_candidate_id,
                extension["policy"].extension_policy_decision_id,
                extension["action"].internal_action_id,
                extension["execution"].extension_execution_id,
                extension["outcome"].extension_outcome_id,
            ),
            source_trace_refs=trace_refs,
            **parent_counts,
        ),
        ActivePerceptionStageRecord(
            stage_record_id=stable_id(
                f"package_129_cycle_{cycle_index}_focus_selection"
            ),
            schema_version=STAGE_SCHEMA_VERSION,
            created_at=utc_now(),
            cycle_index=cycle_index,
            stage_index=2,
            stage_kind="focus_selection",
            runtime_session_id=parent["runtime_session_id"],
            perception_session_id=parent["perception_session_id"],
            observation_window_id=parent["observation_window_id"],
            source_evidence_refs=tuple(
                item.focus_candidate_id for item in sequence["candidates"]
            )
            + (
                sequence["selection"].focus_selection_id,
                sequence[
                    "focus_latest_view"
                ].focused_region_view_id,
            ),
            policy_decision_refs=(
                sequence["focus_decision"].policy_decision_id,
            ),
            internal_action_kind="shift_internal_perception_focus",
            internal_action_id=(
                sequence["focus_action"].internal_action_id
            ),
            execution_record_id=(
                sequence["focus_active_sidecar"].focus_context_id
            ),
            stage_status="completed",
            semantic_label=None,
            source_record_refs=(
                sequence["candidate_batch"].focus_candidate_batch_id,
                sequence["selection"].focus_selection_id,
                sequence["focus_decision"].policy_decision_id,
                sequence["focus_plan"].focus_plan_id,
                sequence["focus_action"].internal_action_id,
                sequence["focus_active_sidecar"].focus_context_id,
            ),
            source_trace_refs=trace_refs,
            **parent_counts,
        ),
        ActivePerceptionStageRecord(
            stage_record_id=stable_id(
                f"package_129_cycle_{cycle_index}_fresh_child"
            ),
            schema_version=STAGE_SCHEMA_VERSION,
            created_at=utc_now(),
            cycle_index=cycle_index,
            stage_index=3,
            stage_kind="fresh_child_reacquisition",
            runtime_session_id=child["runtime_session_id"],
            perception_session_id=child["perception_session_id"],
            observation_window_id=child["observation_window_id"],
            source_evidence_refs=tuple(child["screen_artifact_ids"])
            + tuple(child["host_artifact_ids"])
            + (
                sequence["continuity"].continuity_link_id,
                sequence[
                    "reacquired_evidence_summary"
                ].reacquired_evidence_summary_id,
            ),
            policy_decision_refs=(
                sequence[
                    "reacquisition_eligibility"
                ].eligibility_decision_id,
            ),
            internal_action_kind="capture_again",
            internal_action_id=(
                sequence["reacquisition_action"].internal_action_id
            ),
            execution_record_id=(
                sequence[
                    "reacquisition_execution"
                ].reacquisition_execution_id
            ),
            stage_status="completed",
            semantic_label=None,
            source_record_refs=(
                sequence[
                    "reacquisition_request"
                ].reacquisition_request_id,
                sequence[
                    "reacquisition_eligibility"
                ].eligibility_decision_id,
                sequence["reacquisition_action"].internal_action_id,
                sequence[
                    "reacquisition_execution"
                ].reacquisition_execution_id,
                sequence["continuity"].continuity_link_id,
            ),
            source_trace_refs=trace_refs,
            **child_counts,
        ),
        ActivePerceptionStageRecord(
            stage_record_id=stable_id(
                f"package_129_cycle_{cycle_index}_structural_stop"
            ),
            schema_version=STAGE_SCHEMA_VERSION,
            created_at=utc_now(),
            cycle_index=cycle_index,
            stage_index=4,
            stage_kind="structural_sufficiency_stop",
            runtime_session_id=child["runtime_session_id"],
            perception_session_id=child["perception_session_id"],
            observation_window_id=child["observation_window_id"],
            source_evidence_refs=tuple(
                item.checkpoint_id
                for item in sequence["structural_checkpoints"]
            )
            + tuple(
                item.assessment_id
                for item in sequence["structural_assessments"]
            )
            + (
                sequence["completion"].completion_record_id,
                sequence[
                    "final_temporal_bundle"
                ].temporal_bundle_id,
                sequence[
                    "focus_release"
                ].focus_release_record_id,
            ),
            policy_decision_refs=(
                sequence[
                    "stop_policy_decision"
                ].policy_decision_id,
            ),
            internal_action_kind="stop_observation",
            internal_action_id=sequence["stop_action"].internal_action_id,
            execution_record_id=(
                sequence["stop_execution"].stop_execution_id
            ),
            stage_status="completed",
            semantic_label=None,
            source_record_refs=(
                sequence["structural_contract"].contract_id,
                sequence[
                    "stop_policy_decision"
                ].policy_decision_id,
                sequence["stop_action"].internal_action_id,
                sequence["stop_execution"].stop_execution_id,
                sequence["completion"].completion_record_id,
            ),
            source_trace_refs=trace_refs,
            **child_counts,
        ),
    )
    if tuple(item.stage_index for item in records) != (1, 2, 3, 4):
        raise RuntimeError("Package 129 stage order is incomplete")
    if any(
        value
        for item in records
        for value in (
            item.required_lane_drop_count,
            item.backpressure_fault_count,
            item.capture_failure_count,
            item.compile_failure_count,
            item.flush_remaining_count,
        )
    ):
        raise RuntimeError("Package 129 stage transport integrity failed")
    return records


def _run_teacher_gate(
    *,
    path: Path,
    cycle_index: int,
    sequence: dict[str, Any],
    stage_records: tuple[ActivePerceptionStageRecord, ...],
    working_readback: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    sensor_store = ContentAddressedSensorArtifactStore(path)
    package_122 = BoundedMultimodalPerceptionSessionRuntime(path)
    context = _build_teacher_evidence_context(
        cycle_index=cycle_index,
        sequence=sequence,
        stage_records=stage_records,
    )
    refs = _teacher_manifest_artifact_refs(sequence)
    artifacts = tuple(sensor_store.get_artifact(item) for item in refs)
    if not all(
        sensor_store.verify_artifact(str(item["artifact_id"]))["valid"]
        and bool(item.get("real_device_capture"))
        for item in artifacts
    ):
        raise RuntimeError("teacher evidence requires verified real artifacts")
    first_ns = min(
        int(item["captured_at_monotonic_ns"]) for item in artifacts
    )
    specs = sorted(
        (
            (
                str(item["source_kind"]),
                str(item["artifact_id"]),
                max(
                    0,
                    (
                        int(item["captured_at_monotonic_ns"]) - first_ns
                    )
                    // 1_000_000,
                ),
                str(item["capture_config_sha256"]),
            )
            for item in artifacts
        ),
        key=lambda item: (item[2], item[0], item[1]),
    )
    input_refs = tuple(
        PerceptionTimelineInputRef(
            input_ref_id=stable_id(
                f"package_129_teacher_input_{index}"
            ),
            schema_version=TIMELINE_INPUT_REF_SCHEMA_VERSION,
            source_kind=kind,
            source_artifact_id=artifact_id,
            source_ephemeral_buffer_id=None,
            replay_relative_offset_ms=offset_ms,
            compiler_id=(
                VISUAL_FRAME_COMPILER_ID
                if kind == "screen"
                else HOST_STATE_COMPILER_ID
            ),
            compiler_config_id=config_id,
            privacy_policy_id=None,
            source_trace_refs=tuple(sequence["source_trace_refs"]),
        )
        for index, (kind, artifact_id, offset_ms, config_id) in enumerate(
            specs
        )
    )
    manifest = ArtifactBackedPerceptionTimelineManifest(
        manifest_id=stable_id("package_129_teacher_evidence_manifest"),
        schema_version=ARTIFACT_REPLAY_MANIFEST_SCHEMA_VERSION,
        created_at=utc_now(),
        input_refs=input_refs,
        source_artifacts_are_real=True,
        sources_captured_simultaneously=False,
        deterministic_replay=True,
        manifest_sha256="",
    )
    config = build_default_multimodal_session_config(
        state_dir=path,
        alignment_window_ms=250,
        maximum_window_count=64,
        maximum_session_duration_ms=30_000,
    )
    config_payload = config.to_dict()
    config_payload.update(
        {
            "config_id": stable_id(
                "package_129_teacher_evidence_config"
            ),
            "enabled_source_kinds": PARTICIPATING_LANES,
            "required_source_kinds": PARTICIPATING_LANES,
            "optional_source_kinds": tuple(),
            "screen_queue_depth": 64,
            "host_state_queue_depth": 64,
            "config_sha256": "",
        }
    )
    config = type(config)(**config_payload)
    result = package_122.run_artifact_backed_alignment_replay(
        manifest,
        config=config,
        working_readback_snapshot=working_readback,
        learning_evidence_context={
            "evidence_theme": "active_perception_sequence_observed",
            "canonical_evidence_context": context,
            "evidence_summary": (
                "Bounded low-level active-perception action sequence "
                "presented for exact teacher review."
            ),
            "source_record_refs": tuple(
                item.stage_record_id for item in stage_records
            )
            + tuple(refs),
            "source_trace_refs": tuple(sequence["source_trace_refs"]),
        },
        fixture_kind="package_129_real_active_perception_teacher_evidence",
    )
    if (
        not result.stopped_at_teacher_gate
        or result.automatic_teacher_decision_created
        or len(result.pending_teacher_review_ids) != 1
    ):
        raise RuntimeError("Package 129 did not stop at exact teacher gate")
    resume_runtime = TeacherGatedSessionResumeCommitRuntime()
    checkpoint_id = resume_runtime.persist_waiting_session(
        package_122.embodied_runtime,
        str(result.package_115_session_id),
        path,
    )
    teacher_store = TeacherGatedSessionStore(path)
    pending = teacher_store.get_pending_review(
        result.pending_teacher_review_ids[0]
    )
    snapshot = teacher_store.load_evidence_snapshot(
        str(pending.evidence_snapshot_id)
    )
    snapshot_context = dict(
        snapshot.canonical_evidence_payload.get(
            "canonical_evidence_context"
        )
        or {}
    )
    if canonical_json(snapshot_context) != canonical_json(context):
        raise RuntimeError("teacher evidence context changed before persistence")
    if (
        snapshot.evidence_theme
        != "active_perception_sequence_observed"
        or pending.required_commit_scope != FULL_COMMIT_APPROVAL_SCOPE
        or teacher_store.count_rows(
            "teacher_decisions", str(result.package_115_session_id)
        )
        != 0
    ):
        raise RuntimeError("Package 129 teacher gate scope is invalid")
    return {
        "package_122_session_id": result.session_id,
        "package_122_result_id": result.result_id,
        "package_115_session_id": result.package_115_session_id,
        "pending_review_id": pending.pending_teacher_review_id,
        "evidence_snapshot_id": snapshot.evidence_snapshot_id,
        "evidence_identity_hash": snapshot.evidence_identity_sha256,
        "canonical_payload_sha256": snapshot.canonical_payload_sha256,
        "persisted_checkpoint_id": checkpoint_id,
        "manifest_id": manifest.manifest_id,
        "manifest_artifact_refs": refs,
        "automatic_teacher_decision_created": False,
        "source_trace_refs": tuple(snapshot.source_trace_refs),
    }


def _build_teacher_evidence_context(
    *,
    cycle_index: int,
    sequence: dict[str, Any],
    stage_records: tuple[ActivePerceptionStageRecord, ...],
) -> dict[str, Any]:
    parent = sequence["parent"]
    child = sequence["child"]
    extension = sequence["parent_extension"]
    selection = sequence["selection"]
    selected = sequence["selected_candidate"]
    final_assessment = sequence["structural_assessments"][-1]
    return {
        "scope": "low_level_active_perception_sequence_only",
        "cycle_index": cycle_index,
        "stage_record_ids": tuple(
            item.stage_record_id for item in stage_records
        ),
        "action_sequence": tuple(
            {
                "stage_index": item.stage_index,
                "action_kind": item.internal_action_kind,
                "internal_action_id": item.internal_action_id,
                "execution_record_id": item.execution_record_id,
            }
            for item in stage_records
        ),
        "parent_evidence": {
            "runtime_session_id": parent["runtime_session_id"],
            "perception_session_id": parent["perception_session_id"],
            "observation_window_id": parent["observation_window_id"],
            "screen_artifact_refs": tuple(parent["screen_artifact_ids"]),
            "host_state_artifact_refs": tuple(parent["host_artifact_ids"]),
            "visual_primitive_refs": tuple(
                parent["visual_primitive_refs"]
            ),
            "visual_change_primitive_id": sequence["parent_change"][
                "visual_change_id"
            ],
            "temporal_tail_evidence_id": (
                extension[
                    "tail_result"
                ].tail_evidence.temporal_tail_evidence_id
            ),
            "base_deadline_ns": PARENT_BASE_WINDOW_NS,
            "extended_deadline_ns": PARENT_FINAL_WINDOW_NS,
            "hard_deadline_ns": PARENT_HARD_WINDOW_NS,
            "closure_link_refs": tuple(
                item.closure_link_id
                for item in extension["closure_links"]
            ),
            "closure_after_original_deadline": all(
                int(item.closure_event_time_ns)
                > PARENT_BASE_WINDOW_NS
                for item in extension["closure_links"]
            ),
            "transport": _transport_summary(parent),
        },
        "focus_evidence": {
            "candidate_ids": tuple(
                item.focus_candidate_id
                for item in sequence["candidates"]
            ),
            "candidate_omitted_count": (
                sequence["candidate_batch"].omitted_candidate_count
            ),
            "selection_rule": selection.selection_rule,
            "selected_grid_x": selection.selected_grid_x,
            "selected_grid_y": selection.selected_grid_y,
            "selected_difference_strength": (
                selected.difference_strength
            ),
            "focus_plan_id": sequence["focus_plan"].focus_plan_id,
            "full_frame_preserved": True,
        },
        "child_evidence": {
            "runtime_session_id": child["runtime_session_id"],
            "perception_session_id": child["perception_session_id"],
            "observation_window_id": child["observation_window_id"],
            "capture_session_refs": tuple(
                child["capture_session_refs"]
            ),
            "screen_artifact_refs": tuple(child["screen_artifact_ids"]),
            "host_state_artifact_refs": tuple(
                child["host_artifact_ids"]
            ),
            "sampling_plan_hash": (
                sequence["child_plan"].canonical_plan_hash
            ),
            "parent_child_external_gap_ns": (
                sequence["continuity"].external_gap_ns
            ),
            "focused_region_view_id": (
                sequence[
                    "focus_latest_view"
                ].focused_region_view_id
            ),
            "full_frame_visual_primitive_refs": tuple(
                child["visual_primitive_refs"]
            ),
            "checkpoint_ids": tuple(
                item.checkpoint_id
                for item in sequence["structural_checkpoints"]
            ),
            "final_assessment_id": final_assessment.assessment_id,
            "final_assessment_status": (
                final_assessment.assessment_status
            ),
            "stop_execution_id": (
                sequence["stop_execution"].stop_execution_id
            ),
            "final_temporal_bundle_id": (
                sequence[
                    "final_temporal_bundle"
                ].temporal_bundle_id
            ),
            "focus_release_record_id": (
                sequence["focus_release"].focus_release_record_id
            ),
            "transport": _transport_summary(child),
        },
        "semantic_boundaries": {
            "object_identity": None,
            "object_class": None,
            "semantic_label": None,
            "event_meaning": None,
            "causal_claim": None,
            "curiosity": None,
            "uncertainty": None,
            "recognition": None,
            "subjective_attention": None,
        },
        "stimulus_ground_truth_used": False,
        "raw_sensor_payload_included": False,
        "qingyin_output_created": False,
        "external_control_created": False,
    }


def _teacher_manifest_artifact_refs(
    sequence: dict[str, Any],
) -> tuple[str, ...]:
    parent = sequence["parent"]
    child = sequence["child"]
    change = sequence["parent_change"]
    refs = (
        str(change["previous_source_artifact_id"]),
        str(change["current_source_artifact_id"]),
        str(parent["host_artifact_ids"][0]),
        str(parent["host_artifact_ids"][-1]),
        str(child["screen_artifact_ids"][0]),
        str(child["screen_artifact_ids"][-1]),
        str(child["host_artifact_ids"][0]),
        str(child["host_artifact_ids"][-1]),
    )
    return tuple(dict.fromkeys(refs))


def _transport_summary(window: dict[str, Any]) -> dict[str, int]:
    return {
        "required_lane_drop_count": int(
            window["required_lane_drop_count"]
        ),
        "backpressure_fault_count": int(
            window["backpressure_fault_count"]
        ),
        "capture_failure_count": int(window["capture_failure_count"]),
        "compile_failure_count": int(window["compile_failure_count"]),
        "flush_remaining_count": int(window["flush_remaining_count"]),
    }


def _build_readback_timing(
    *,
    cycle: ActivePerceptionGrowthCycleRecord,
    sequence: dict[str, Any],
    readback: tuple[dict[str, Any], ...],
    readback_loaded_ns: int,
) -> ActivePerceptionReadbackLoadTiming:
    candidate_ns = int(sequence["candidate_evaluated_monotonic_ns"])
    scored_ns = int(sequence["first_action_scored_monotonic_ns"])
    executed_ns = int(sequence["first_action_executed_monotonic_ns"])
    capture_ns = int(sequence["parent_capture_started_monotonic_ns"])
    validate_readback_loaded_before_candidate(
        readback_loaded_monotonic_ns=readback_loaded_ns,
        candidate_evaluated_monotonic_ns=candidate_ns,
    )
    refs = tuple(
        str(item["working_readback_commit_id"]) for item in readback
    )
    traces = tuple(
        dict.fromkeys(
            ref
            for item in readback
            for ref in tuple(item.get("source_trace_refs") or ())
        )
    )
    return ActivePerceptionReadbackLoadTiming(
        timing_record_id=stable_id(
            "package_129_readback_load_timing"
        ),
        schema_version=READBACK_TIMING_SCHEMA_VERSION,
        created_at=utc_now(),
        cycle_2_record_id=cycle.cycle_record_id,
        working_readback_refs=refs,
        readback_loaded_monotonic_ns=readback_loaded_ns,
        parent_capture_started_monotonic_ns=capture_ns,
        parent_late_event_candidate_evaluated_monotonic_ns=(
            candidate_ns
        ),
        first_internal_action_scored_monotonic_ns=scored_ns,
        first_internal_action_executed_monotonic_ns=executed_ns,
        loaded_before_parent_capture=readback_loaded_ns <= capture_ns,
        loaded_before_candidate_evaluation=(
            readback_loaded_ns <= candidate_ns
        ),
        loaded_before_action_scoring=readback_loaded_ns <= scored_ns,
        loaded_before_action_execution=(
            readback_loaded_ns <= executed_ns
        ),
        source_record_refs=(cycle.cycle_record_id,) + refs,
        source_trace_refs=traces,
    )


def _build_readback_influence(
    *,
    cycle_one: dict[str, Any],
    cycle: ActivePerceptionGrowthCycleRecord,
    stage_records: tuple[ActivePerceptionStageRecord, ...],
    sequence: dict[str, Any],
    readback: tuple[dict[str, Any], ...],
) -> ActivePerceptionReadbackInfluenceRecord:
    result = sequence.get("readback_score")
    if not result or not result.get("matched"):
        raise RuntimeError("Cycle 2 readback did not match Cycle 1 evidence")
    if result.get("policy_authority_created"):
        raise RuntimeError("readback scorer created forbidden policy authority")
    score = result["score"]
    contribution = float(result["contribution"])
    if contribution <= 0:
        raise RuntimeError("Cycle 2 readback contribution was not positive")
    matched = tuple(result["matched_readback_items"])
    expected_snapshot = str(cycle_one["evidence_snapshot_id"])
    expected_hash = str(cycle_one["evidence_identity_hash"])
    if any(
        item.get("source_evidence_snapshot_id") != expected_snapshot
        or item.get("evidence_identity_sha256") != expected_hash
        for item in matched
    ):
        raise RuntimeError("Cycle 2 readback lineage does not match Cycle 1")
    candidate_id = sequence[
        "parent_extension"
    ]["candidate"].extension_candidate_id
    if score.source_internal_action_candidate_id != candidate_id:
        raise RuntimeError("readback score did not target the live candidate")
    traces = tuple(
        dict.fromkeys(
            ref
            for item in matched
            for ref in tuple(item.get("source_trace_refs") or ())
        )
    )
    return ActivePerceptionReadbackInfluenceRecord(
        influence_record_id=stable_id(
            "package_129_readback_influence"
        ),
        schema_version=READBACK_INFLUENCE_SCHEMA_VERSION,
        created_at=utc_now(),
        cycle_1_working_readback_id=str(
            matched[0]["working_readback_commit_id"]
        ),
        cycle_2_stage_record_id=stage_records[0].stage_record_id,
        cycle_2_internal_action_candidate_id=candidate_id,
        cycle_2_action_kind="extend_observation_window",
        package_112_scorer_id=SCORER_ID,
        package_112_scorer_version=score.schema_version,
        score_without_readback=float(score.base_candidate_priority),
        score_with_readback=float(score.final_candidate_priority),
        readback_contribution=contribution,
        influencing_readback_refs=tuple(
            str(item["working_readback_commit_id"])
            for item in matched
        ),
        matching_evidence_refs=(expected_snapshot, expected_hash),
        actual_runtime_hot_path=True,
        hard_policy_gate_bypassed=False,
        hard_coded_experiment_match_used=False,
        stimulus_ground_truth_used=False,
        source_record_refs=(
            cycle.cycle_record_id,
            stage_records[0].stage_record_id,
            candidate_id,
            score.candidate_readback_score_id,
        ),
        source_trace_refs=traces,
    )


def _build_two_cycle_comparison(
    *,
    cycle_one: dict[str, Any],
    cycle_two: ActivePerceptionGrowthCycleRecord,
    influence: ActivePerceptionReadbackInfluenceRecord,
    path: Path,
) -> ActivePerceptionTwoCycleComparison:
    _assert_cycle_one_commit_present(path, cycle_one)
    cycle_one_parent = set(
        tuple(cycle_one.get("parent_screen_artifact_refs") or ())
        + tuple(cycle_one.get("parent_host_state_artifact_refs") or ())
    )
    cycle_one_child = set(
        tuple(cycle_one.get("child_screen_artifact_refs") or ())
        + tuple(cycle_one.get("child_host_state_artifact_refs") or ())
    )
    cycle_two_parent = set(cycle_two.parent_screen_artifact_refs).union(
        cycle_two.parent_host_state_artifact_refs
    )
    cycle_two_child = set(cycle_two.child_screen_artifact_refs).union(
        cycle_two.child_host_state_artifact_refs
    )
    raw_distinct = not (
        cycle_one_parent.intersection(cycle_two_parent)
        or cycle_one_child.intersection(cycle_two_child)
        or cycle_one_parent.intersection(cycle_two_child)
        or cycle_one_child.intersection(cycle_two_parent)
    )
    return ActivePerceptionTwoCycleComparison(
        comparison_id=stable_id(
            "package_129_two_cycle_comparison"
        ),
        schema_version=COMPARISON_SCHEMA_VERSION,
        created_at=utc_now(),
        experiment_id=EXPERIMENT_ID,
        cycle_1_record_id=str(cycle_one["cycle_record_id"]),
        cycle_2_record_id=cycle_two.cycle_record_id,
        cycle_1_process_instance_id=str(
            cycle_one["process_instance_id"]
        ),
        cycle_2_process_instance_id=cycle_two.process_instance_id,
        process_instances_distinct=(
            cycle_one["process_instance_id"]
            != cycle_two.process_instance_id
        ),
        operating_system_processes_distinct=(
            int(cycle_one["operating_system_process_id"])
            != cycle_two.operating_system_process_id
        ),
        parent_sessions_distinct=all(
            (
                cycle_one["parent_runtime_session_id"]
                != cycle_two.parent_runtime_session_id,
                cycle_one["parent_perception_session_id"]
                != cycle_two.parent_perception_session_id,
                cycle_one["parent_observation_window_id"]
                != cycle_two.parent_observation_window_id,
            )
        ),
        child_sessions_distinct=all(
            (
                cycle_one["child_runtime_session_id"]
                != cycle_two.child_runtime_session_id,
                cycle_one["child_perception_session_id"]
                != cycle_two.child_perception_session_id,
                cycle_one["child_observation_window_id"]
                != cycle_two.child_observation_window_id,
            )
        ),
        raw_artifacts_distinct=raw_distinct,
        stimulus_config_hash_equal=(
            cycle_one["stimulus_config_hash"]
            == cycle_two.stimulus_config_hash
        ),
        source_plan_hash_equal=(
            cycle_one["source_plan_hash"] == cycle_two.source_plan_hash
        ),
        cycle_1_approved_commit_present=True,
        cycle_2_readback_loaded_before_event=(
            cycle_two.readback_loaded_before_event
        ),
        cycle_2_readback_influence_record_id=(
            influence.influence_record_id
        ),
        cycle_2_readback_contribution_nonzero=(
            influence.readback_contribution > 0
        ),
        cycle_2_completed_active_perception_sequence=(
            len(cycle_two.stage_record_ids) == 4
        ),
        cycle_2_final_state=cycle_two.final_session_state,
        policy_gate_bypass_detected=False,
        semantic_recognition_created=False,
        llm_runtime_calls=0,
        codex_runtime_calls=0,
        network_runtime_calls=0,
        source_record_refs=(
            str(cycle_one["cycle_record_id"]),
            cycle_two.cycle_record_id,
            influence.influence_record_id,
        ),
        source_trace_refs=tuple(
            dict.fromkeys(
                tuple(cycle_one.get("source_trace_refs") or ())
                + cycle_two.source_trace_refs
                + influence.source_trace_refs
            )
        ),
    )


def run_package_129_controls(
    *,
    state_dir: str | Path,
    sequence: dict[str, Any],
    cycle_one: dict[str, Any],
    readback: tuple[dict[str, Any], ...],
    cycle_two_session_id: str,
) -> dict[str, bool]:
    path = Path(state_dir)
    candidate = sequence["parent_extension"]["candidate"]
    observation = sequence["parent_extension"]["final_state"]
    original_observation = replace(
        observation,
        observation_window_state_id=stable_id(
            "package_129_control_observation"
        ),
        current_deadline_event_time_ns=PARENT_BASE_WINDOW_NS,
        extension_count=0,
        total_extension_ns=0,
        window_status="observing_base_window",
    )
    empty = score_extension_candidate_with_working_readback(
        extension_candidate=candidate,
        working_readback_items=tuple(),
        expected_evidence_snapshot_id=str(
            cycle_one["evidence_snapshot_id"]
        ),
        expected_evidence_identity_sha256=str(
            cycle_one["evidence_identity_hash"]
        ),
    )
    empty_passed = (
        empty["matched"] is False and empty["contribution"] == 0
    )
    no_open_tail = replace(
        sequence["parent_extension"]["tail_result"].tail_evidence,
        temporal_tail_evidence_id=stable_id(
            "package_129_no_open_tail_control"
        ),
        open_visual_region_refs=tuple(),
        open_audio_region_refs=tuple(),
        recent_onset_anchor_refs=tuple(),
    )
    p125_authorization = sequence["parent_extension"]["authorization"]
    no_open_candidate = create_observation_extension_candidate(
        observation_window=original_observation,
        tail_evidence=no_open_tail,
        authorization=p125_authorization,
        requested_extension_ns=PARENT_EXTENSION_NS,
    )
    mismatched_context_passed = no_open_candidate is None
    authorization_off = decide_observation_extension_policy(
        candidate=candidate,
        authorization=None,
        observation_window=original_observation,
        transport_integrity_valid=True,
        same_sensor_configuration=True,
    )
    authorization_off_passed = (
        authorization_off.decision == "block"
        and "authorization_absent_or_invalid"
        in authorization_off.failure_reasons
    )
    transport_fault = decide_observation_extension_policy(
        candidate=candidate,
        authorization=p125_authorization,
        observation_window=original_observation,
        transport_integrity_valid=False,
        same_sensor_configuration=True,
    )
    transport_fault_passed = (
        transport_fault.decision == "block"
        and "transport_integrity_invalid"
        in transport_fault.failure_reasons
    )
    wrong_lineage_item = dict(readback[0])
    wrong_lineage_item["source_evidence_snapshot_id"] = (
        "session_learning_evidence_snapshot:wrong"
    )
    wrong_lineage = score_extension_candidate_with_working_readback(
        extension_candidate=candidate,
        working_readback_items=(wrong_lineage_item,),
        expected_evidence_snapshot_id=str(
            cycle_one["evidence_snapshot_id"]
        ),
        expected_evidence_identity_sha256=str(
            cycle_one["evidence_identity_hash"]
        ),
    )
    wrong_lineage_passed = (
        wrong_lineage["matched"] is False
        and wrong_lineage["contribution"] == 0
    )
    late_load_passed = False
    try:
        validate_readback_loaded_before_candidate(
            readback_loaded_monotonic_ns=20,
            candidate_evaluated_monotonic_ns=10,
        )
    except ValueError:
        late_load_passed = True
    same_process_passed = not _processes_distinct(
        int(cycle_one["operating_system_process_id"]),
        int(cycle_one["operating_system_process_id"]),
    )
    reused_artifact_passed = not _artifact_sets_distinct(
        tuple(cycle_one["parent_screen_artifact_refs"]),
        tuple(cycle_one["parent_screen_artifact_refs"]),
    )
    stimulus_match_passed = False
    try:
        reject_stimulus_matching_provenance(
            {"experiment_id": EXPERIMENT_ID}
        )
    except ValueError:
        stimulus_match_passed = True
    teacher_store = TeacherGatedSessionStore(path)
    auto_approval_passed = (
        teacher_store.count_rows(
            "teacher_decisions", cycle_two_session_id
        )
        == 0
        and teacher_store.count_rows(
            "reviewed_interpretation_commits",
            cycle_two_session_id,
        )
        == 0
        and teacher_store.count_rows(
            "working_readback_commits",
            cycle_two_session_id,
        )
        == 0
    )
    stage_ids = tuple(
        item.get("stage_record_id")
        for item in Package129ActivePerceptionGrowthStore(
            path
        ).list_payloads("active_perception_stage_records")
        if int(item.get("cycle_index", 0)) == 2
    )
    fabricated_sequence_passed = not _four_stage_lineage_complete(
        stage_ids[:3]
    )
    semantic_injection_passed = False
    actual_stage = next(
        item
        for item in Package129ActivePerceptionGrowthStore(
            path
        ).list_payloads("active_perception_stage_records")
        if int(item.get("cycle_index", 0)) == 2
    )
    try:
        ActivePerceptionStageRecord.from_dict(
            {**actual_stage, "semantic_label": "important region"}
        )
    except ValueError:
        semantic_injection_passed = True
    results = {
        "empty_readback_control_passed": empty_passed,
        "mismatched_context_control_passed": (
            mismatched_context_passed
        ),
        "authorization_off_control_passed": (
            authorization_off_passed
        ),
        "transport_fault_control_passed": transport_fault_passed,
        "wrong_readback_lineage_control_passed": (
            wrong_lineage_passed
        ),
        "readback_loaded_late_control_passed": late_load_passed,
        "same_process_control_passed": same_process_passed,
        "reused_artifact_control_passed": reused_artifact_passed,
        "stimulus_match_control_passed": stimulus_match_passed,
        "auto_approval_control_passed": auto_approval_passed,
        "fabricated_sequence_control_passed": (
            fabricated_sequence_passed
        ),
        "semantic_injection_control_passed": (
            semantic_injection_passed
        ),
    }
    control_id = stable_id("package_129_control_results")
    Package129ActivePerceptionGrowthStore(path).append_payload(
        "active_perception_control_results",
        "control_result_id",
        control_id,
        {
            "control_result_id": control_id,
            "schema_version": "ashl_package_129_control_results_v0",
            "created_at": utc_now(),
            **results,
        },
    )
    if not all(results.values()):
        raise RuntimeError(
            "Package 129 controls failed: "
            + ",".join(
                key for key, value in results.items() if not value
            )
        )
    return results


def _assert_cycle_one_commit_present(
    path: Path,
    cycle_one: dict[str, Any],
) -> tuple[dict[str, Any], ...]:
    store = TeacherGatedSessionStore(path)
    session_id = str(cycle_one["bounded_embodied_session_id"])
    decisions = store.list_teacher_decisions(session_id)
    matching_decisions = tuple(
        item
        for item in decisions
        if item.get("decision") == "approved"
        and item.get("approval_scope") == FULL_COMMIT_APPROVAL_SCOPE
        and item.get("target_evidence_snapshot_id")
        == cycle_one["evidence_snapshot_id"]
        and item.get("target_evidence_identity_sha256")
        == cycle_one["evidence_identity_hash"]
    )
    readback = tuple(
        item
        for item in store.load_active_working_readback()
        if item.get("source_evidence_snapshot_id")
        == cycle_one["evidence_snapshot_id"]
        and item.get("evidence_identity_sha256")
        == cycle_one["evidence_identity_hash"]
        and item.get("evidence_theme")
        == "active_perception_sequence_observed"
    )
    if len(matching_decisions) != 1 or len(readback) != 1:
        raise RuntimeError(
            "Cycle 1 exact approved commit/readback is unavailable"
        )
    required_tables = (
        "reviewed_interpretation_commits",
        "working_readback_commits",
        "session_commit_records",
    )
    if any(store.count_rows(name, session_id) != 1 for name in required_tables):
        raise RuntimeError("Cycle 1 reviewed memory chain is incomplete")
    required_stages = {
        "reviewed_concept",
        "memory_learning_trace",
        "memory_routing_trace",
        "memory_application_data",
        "working_readback_commit",
        "reviewed_interpretation_commit",
    }
    identity_bindings = store.list_learning_pipeline_identity_bindings(
        session_id
    )
    observed_stages = {
        str(item.get("pipeline_stage")) for item in identity_bindings
    }
    if not required_stages.issubset(observed_stages) or not all(
        item.get("identity_preserved") is True
        and item.get("validator_passed") is True
        for item in identity_bindings
        if item.get("pipeline_stage") in required_stages
    ):
        raise RuntimeError("Cycle 1 memory identity lineage is incomplete")
    required_readback_refs = (
        "source_reviewed_concept_ref",
        "memory_learning_trace_ref",
        "memory_routing_trace_ref",
        "memory_application_data_ref",
    )
    if not all(readback[0].get(name) for name in required_readback_refs):
        raise RuntimeError("Cycle 1 working readback provenance is incomplete")
    return readback


def _processes_distinct(first_pid: int, second_pid: int) -> bool:
    return int(first_pid) != int(second_pid)


def _artifact_sets_distinct(
    first: tuple[str, ...],
    second: tuple[str, ...],
) -> bool:
    return not set(first).intersection(second)


def _four_stage_lineage_complete(
    stage_ids: tuple[str | None, ...],
) -> bool:
    return len(stage_ids) == 4 and all(stage_ids)


def _emit_growth_event(
    *,
    path: Path,
    package_store: Package129ActivePerceptionGrowthStore,
    event_kind: str,
    cycle_index: int,
    process_instance_id: str,
    runtime_session_id: str,
    perception_session_id: str,
    observation_window_id: str | None,
    source_record_refs: tuple[str, ...],
    source_trace_refs: tuple[str, ...],
    strict: bool,
) -> None:
    try:
        LocalOperatorEventStream(
            build_default_console_store(path)
        ).append_event(
            event_kind=event_kind,
            cycle_index=cycle_index,
            process_instance_id=process_instance_id,
            runtime_session_id=runtime_session_id,
            perception_session_id=perception_session_id,
            observation_window_id=observation_window_id,
            source_record_refs=source_record_refs,
            source_trace_refs=source_trace_refs,
        )
    except Exception as error:
        failure_id = stable_id("package_129_event_delivery_failure")
        package_store.append_payload(
            "active_perception_event_delivery_failures",
            "event_delivery_failure_id",
            failure_id,
            {
                "event_delivery_failure_id": failure_id,
                "schema_version": (
                    "ashl_package_129_event_delivery_failure_v0"
                ),
                "created_at": utc_now(),
                "event_kind": event_kind,
                "cycle_index": cycle_index,
                "process_instance_id": process_instance_id,
                "error": str(error),
            },
        )
        if strict:
            raise


def _public_sequence(sequence: dict[str, Any]) -> dict[str, Any]:
    parent = sequence["parent"]
    child = sequence["child"]
    return {
        "experiment_run_id": sequence["experiment_run_id"],
        "cycle_index": sequence["cycle_index"],
        "parent": {
            "runtime_session_id": parent["runtime_session_id"],
            "perception_session_id": parent["perception_session_id"],
            "observation_window_id": parent["observation_window_id"],
            "capture_session_refs": tuple(
                parent["capture_session_refs"]
            ),
            "screen_artifact_count": len(
                parent["screen_artifact_ids"]
            ),
            "host_state_artifact_count": len(
                parent["host_artifact_ids"]
            ),
            "actual_window_ns": parent["actual_window_ns"],
            "transport": _transport_summary(parent),
        },
        "extension": {
            "candidate_id": sequence[
                "parent_extension"
            ]["candidate"].extension_candidate_id,
            "action_id": sequence[
                "parent_extension"
            ]["action"].internal_action_id,
            "execution_id": sequence[
                "parent_extension"
            ]["execution"].extension_execution_id,
            "closure_link_ids": tuple(
                item.closure_link_id
                for item in sequence[
                    "parent_extension"
                ]["closure_links"]
            ),
        },
        "focus": {
            "candidate_count": len(sequence["candidates"]),
            "selection_id": sequence["selection"].focus_selection_id,
            "selected_grid_x": (
                sequence["selection"].selected_grid_x
            ),
            "selected_grid_y": (
                sequence["selection"].selected_grid_y
            ),
            "action_id": sequence["focus_action"].internal_action_id,
        },
        "child": {
            "runtime_session_id": child["runtime_session_id"],
            "perception_session_id": child["perception_session_id"],
            "observation_window_id": child["observation_window_id"],
            "capture_session_refs": tuple(child["capture_session_refs"]),
            "screen_artifact_count": len(
                child["screen_artifact_ids"]
            ),
            "host_state_artifact_count": len(
                child["host_artifact_ids"]
            ),
            "actual_window_ns": child["actual_window_ns"],
            "transport": _transport_summary(child),
        },
        "reacquisition": {
            "action_id": (
                sequence["reacquisition_action"].internal_action_id
            ),
            "execution_id": sequence[
                "reacquisition_execution"
            ].reacquisition_execution_id,
            "external_gap_ns": sequence["continuity"].external_gap_ns,
        },
        "structural_stop": {
            "contract_id": sequence["structural_contract"].contract_id,
            "checkpoint_count": len(
                sequence["structural_checkpoints"]
            ),
            "final_assessment": sequence[
                "structural_assessments"
            ][-1].assessment_status,
            "action_id": sequence["stop_action"].internal_action_id,
            "execution_id": (
                sequence["stop_execution"].stop_execution_id
            ),
            "completion_id": (
                sequence["completion"].completion_record_id
            ),
            "stopped_before_hard_deadline": sequence[
                "stop_execution"
            ].stopped_before_hard_deadline,
        },
        "focus_released": sequence[
            "focus_released_sidecar"
        ].automatically_released,
        "fixture_manifest_consumed_by_runtime": False,
        "raw_payload_included": False,
    }
