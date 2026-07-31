"""Evidence-grounded final audit for Package 129."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ashl_core_v1.host_body.host_body_internal_action_choice import (
    ALLOWED_INTERNAL_ACTION_KINDS,
)
from ashl_core_v1.migration_audit import (
    D_LAPLACE_QM0_AUDIT_STATUS,
    QINGYIN_MIGRATION_STATUS,
)
from ashl_core_v1.runtime.active_perception_growth_types import (
    AUDIT_SCHEMA_VERSION,
    BASELINE_COMMIT,
    BLOCKED_STATUS,
    EXPERIMENT_ID,
    PASS_STATUS,
    STAGE_ACTION_KINDS,
    STAGE_KINDS,
    ActivePerceptionGrowthCycleRecord,
    ActivePerceptionReadbackInfluenceRecord,
    ActivePerceptionReadbackLoadTiming,
    ActivePerceptionStageRecord,
    ActivePerceptionTwoCycleComparison,
    Package129ActivePerceptionGrowthAudit,
)
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
    ContentAddressedSensorArtifactStore,
)
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.internal_perception_focus_types import (
    PACKAGE_127_PASS_STATUS,
)
from ashl_core_v1.runtime.observation_window_types import (
    PACKAGE_125_PASS_STATUS,
)
from ashl_core_v1.runtime.package_125_observation_extension_store import (
    Package125ObservationExtensionStore,
)
from ashl_core_v1.runtime.package_126_reacquisition_store import (
    Package126ReacquisitionStore,
)
from ashl_core_v1.runtime.package_127_internal_focus_store import (
    Package127InternalFocusStore,
)
from ashl_core_v1.runtime.package_128_sufficiency_stop_store import (
    Package128SufficiencyStopStore,
)
from ashl_core_v1.runtime.package_129_active_perception_growth_store import (
    Package129ActivePerceptionGrowthStore,
)
from ashl_core_v1.runtime.perception_reacquisition_types import (
    PACKAGE_126_PASS_STATUS,
)
from ashl_core_v1.runtime.session_learning_evidence_identity import (
    FULL_COMMIT_APPROVAL_SCOPE,
)
from ashl_core_v1.runtime.structural_evidence_sufficiency_types import (
    CONTRACT_KIND,
    PACKAGE_128_PASS_STATUS,
)
from ashl_core_v1.runtime.teacher_gated_session_store import (
    TeacherGatedSessionStore,
)


_ACTION_SEQUENCE = tuple(STAGE_ACTION_KINDS[item] for item in STAGE_KINDS)
_CONTROL_FIELDS = (
    "empty_readback_control_passed",
    "mismatched_context_control_passed",
    "authorization_off_control_passed",
    "transport_fault_control_passed",
    "wrong_readback_lineage_control_passed",
    "readback_loaded_late_control_passed",
    "same_process_control_passed",
    "reused_artifact_control_passed",
    "stimulus_match_control_passed",
    "auto_approval_control_passed",
    "fabricated_sequence_control_passed",
    "semantic_injection_control_passed",
)
_TRANSPORT_FIELDS = (
    "required_lane_drop_count",
    "backpressure_fault_count",
    "capture_failure_count",
    "compile_failure_count",
    "flush_remaining_count",
)


def audit_package_129_active_perception_growth(
    *,
    state_dir: str | Path,
    append: bool = True,
) -> Package129ActivePerceptionGrowthAudit:
    path = Path(state_dir)
    store = Package129ActivePerceptionGrowthStore(path)
    teacher_store = TeacherGatedSessionStore(path)
    sensor_store = ContentAddressedSensorArtifactStore(path)
    p125_store = Package125ObservationExtensionStore(path)
    p126_store = Package126ReacquisitionStore(path)
    p127_store = Package127InternalFocusStore(path)
    p128_store = Package128SufficiencyStopStore(path)
    failures: list[str] = []

    def require(flag: bool, reason: str) -> bool:
        if not flag:
            failures.append(reason)
        return bool(flag)

    cycle_one = store.latest_cycle(1) or {}
    cycle_two = store.latest_cycle(2) or {}
    cycle_one_valid = _cycle_valid(cycle_one, 1)
    cycle_two_valid = _cycle_valid(cycle_two, 2)
    require(cycle_one_valid, "cycle_1_record_invalid_or_missing")
    require(cycle_two_valid, "cycle_2_record_invalid_or_missing")

    stage_payloads = store.list_payloads("active_perception_stage_records")
    cycle_one_stages = _ordered_stages(stage_payloads, 1)
    cycle_two_stages = _ordered_stages(stage_payloads, 2)
    cycle_one_lineage = require(
        _stage_lineage_valid(cycle_one, cycle_one_stages),
        "cycle_1_four_stage_lineage_invalid",
    )
    cycle_two_lineage = require(
        _stage_lineage_valid(cycle_two, cycle_two_stages),
        "cycle_2_four_stage_lineage_invalid",
    )
    cycle_one_sources = _verify_existing_stage_sources(
        cycle_one_stages,
        p125_store=p125_store,
        p126_store=p126_store,
        p127_store=p127_store,
        p128_store=p128_store,
    )
    cycle_two_sources = _verify_existing_stage_sources(
        cycle_two_stages,
        p125_store=p125_store,
        p126_store=p126_store,
        p127_store=p127_store,
        p128_store=p128_store,
    )
    require(
        all(cycle_one_sources.values()),
        "cycle_1_existing_action_source_record_invalid",
    )
    require(
        all(cycle_two_sources.values()),
        "cycle_2_existing_action_source_record_invalid",
    )

    cycle_one_artifacts = _cycle_artifact_refs(cycle_one)
    cycle_two_artifacts = _cycle_artifact_refs(cycle_two)
    cycle_one_real = require(
        _real_artifacts_valid(sensor_store, cycle_one_artifacts),
        "cycle_1_real_capture_not_verified",
    )
    cycle_two_real = require(
        _real_artifacts_valid(sensor_store, cycle_two_artifacts)
        and bool(cycle_two_artifacts)
        and not set(cycle_one_artifacts).intersection(cycle_two_artifacts),
        "cycle_2_fresh_capture_not_verified",
    )

    cycle_one_transport = require(
        _transport_clean(cycle_one_stages),
        "cycle_1_transport_integrity_failed",
    )
    cycle_two_transport = require(
        _transport_clean(cycle_two_stages),
        "cycle_2_transport_integrity_failed",
    )

    cycle_one_waiting = require(
        bool(
            cycle_one.get("final_session_state") == "WAITING_TEACHER_REVIEW"
            and cycle_one.get("pending_teacher_review_id")
            and cycle_one.get("evidence_snapshot_id")
            and cycle_one.get("evidence_identity_hash")
        ),
        "cycle_1_teacher_gate_not_verified",
    )
    cycle_two_waiting = require(
        bool(
            cycle_two.get("final_session_state") == "WAITING_TEACHER_REVIEW"
            and cycle_two.get("pending_teacher_review_id")
            and cycle_two.get("evidence_snapshot_id")
            and cycle_two.get("evidence_identity_hash")
        ),
        "cycle_2_teacher_gate_not_verified",
    )

    cycle_one_approval, cycle_one_chain, cycle_one_readback = (
        _verify_cycle_one_teacher_commit(
            teacher_store,
            cycle_one,
        )
    )
    require(cycle_one_approval, "cycle_1_exact_approval_not_verified")
    require(cycle_one_chain, "cycle_1_reviewed_memory_chain_not_verified")
    require(cycle_one_readback, "cycle_1_working_readback_not_verified")

    cycle_two_session = str(cycle_two.get("bounded_embodied_session_id") or "")
    cycle_two_teacher_count = (
        teacher_store.count_rows("teacher_decisions", cycle_two_session)
        if cycle_two_session
        else -1
    )
    cycle_two_memory_count = sum(
        teacher_store.count_rows(table, cycle_two_session)
        for table in (
            "reviewed_interpretation_commits",
            "working_readback_commits",
        )
    ) if cycle_two_session else -1
    cycle_two_auto_approval = cycle_two_teacher_count != 0
    cycle_two_additional_memory = cycle_two_memory_count != 0
    require(
        not cycle_two_auto_approval,
        "cycle_2_auto_approval_detected",
    )
    require(
        not cycle_two_additional_memory,
        "cycle_2_additional_memory_commit_detected",
    )

    timing_payload = store.latest_payload(
        "active_perception_readback_load_timing"
    ) or {}
    influence_payload = store.latest_payload(
        "active_perception_readback_influence"
    ) or {}
    comparison_payload = store.latest_payload(
        "active_perception_two_cycle_comparisons"
    ) or {}
    timing_valid = _record_valid(
        ActivePerceptionReadbackLoadTiming,
        timing_payload,
    )
    influence_valid = _record_valid(
        ActivePerceptionReadbackInfluenceRecord,
        influence_payload,
    )
    comparison_valid = _record_valid(
        ActivePerceptionTwoCycleComparison,
        comparison_payload,
    )
    require(timing_valid, "cycle_2_readback_timing_invalid")
    require(influence_valid, "cycle_2_readback_influence_invalid")
    require(comparison_valid, "two_cycle_comparison_invalid")

    process_separation = require(
        _process_separation_valid(
            store.list_payloads("active_perception_process_receipts"),
            cycle_one,
            cycle_two,
            comparison_payload,
        ),
        "cycle_process_separation_not_verified",
    )
    controls = store.latest_payload("active_perception_control_results") or {}
    for field in _CONTROL_FIELDS:
        require(
            controls.get(field) is True,
            field.replace("_passed", "_failed"),
        )
    fixture_firewall = require(
        _fixture_firewall_valid(
            store.list_payloads("active_perception_fixture_manifests"),
            cycle_one,
            cycle_two,
            teacher_store,
        ),
        "stimulus_ground_truth_firewall_failed",
    )
    require(
        store.count("active_perception_event_delivery_failures") == 0,
        "operator_event_delivery_failure_visible",
    )

    package_128_verified = require(
        PACKAGE_128_PASS_STATUS
        == "passed_structural_evidence_sufficiency_and_observation_stop_policy_v0"
        and CONTRACT_KIND
        == "focused_visual_event_closure_with_post_context"
        and "stop_observation" in ALLOWED_INTERNAL_ACTION_KINDS,
        "package_128_baseline_not_verified",
    )
    package_127_verified = require(
        PACKAGE_127_PASS_STATUS
        == "passed_internal_perception_focus_shift_v0"
        and "shift_internal_perception_focus"
        in ALLOWED_INTERNAL_ACTION_KINDS,
        "package_127_baseline_not_verified",
    )
    package_126_verified = require(
        PACKAGE_126_PASS_STATUS
        == "passed_bounded_re_sampling_and_listen_again_internal_action_v0"
        and "capture_again" in ALLOWED_INTERNAL_ACTION_KINDS
        and "listen_again" in ALLOWED_INTERNAL_ACTION_KINDS,
        "package_126_baseline_not_verified",
    )
    package_125_verified = require(
        PACKAGE_125_PASS_STATUS
        == "passed_bounded_observation_window_extension_internal_action_v0"
        and "extend_observation_window" in ALLOWED_INTERNAL_ACTION_KINDS,
        "package_125_baseline_not_verified",
    )
    qm0_verified = require(
        D_LAPLACE_QM0_AUDIT_STATUS
        == "passed_d_laplace_qm0_read_only_migration_audit_v0"
        and QINGYIN_MIGRATION_STATUS
        == "QINGYIN_MIGRATION_INCOMPLETE_AUDIT_LAYER",
        "qm0_baseline_not_verified",
    )

    influence_contribution = float(
        influence_payload.get("readback_contribution", 0.0)
    )
    actual_hot_path = bool(
        influence_payload.get("actual_runtime_hot_path")
        and influence_payload.get("package_112_scorer_id")
        == "host_body_readback_internal_action_influence"
    )
    require(
        actual_hot_path,
        "cycle_2_package_112_hot_path_not_verified",
    )
    require(
        influence_contribution > 0,
        "cycle_2_readback_contribution_not_positive",
    )
    policy_bypass = bool(
        influence_payload.get("hard_policy_gate_bypassed", True)
        or comparison_payload.get("policy_gate_bypass_detected", True)
    )
    require(not policy_bypass, "cycle_2_policy_gate_bypass_detected")

    status = PASS_STATUS if not failures else BLOCKED_STATUS
    audit = Package129ActivePerceptionGrowthAudit(
        audit_id=stable_id("package_129_audit"),
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        baseline_commit=BASELINE_COMMIT,
        package_128_baseline_verified=package_128_verified,
        package_127_baseline_verified=package_127_verified,
        package_126_baseline_verified=package_126_verified,
        package_125_baseline_verified=package_125_verified,
        qm0_baseline_verified=qm0_verified,
        new_perception_action_kind_created=False,
        new_sensor_source_created=False,
        new_primitive_compiler_created=False,
        new_focus_mode_created=False,
        new_sufficiency_contract_kind_created=False,
        cycle_1_real_capture_verified=cycle_one_real,
        cycle_1_extension_verified=bool(
            cycle_one_lineage
            and cycle_one_sources.get("extend_observation_window")
        ),
        cycle_1_focus_shift_verified=bool(
            cycle_one_lineage
            and cycle_one_sources.get("shift_internal_perception_focus")
        ),
        cycle_1_capture_again_verified=bool(
            cycle_one_lineage
            and cycle_one_sources.get("capture_again")
        ),
        cycle_1_stop_observation_verified=bool(
            cycle_one_lineage
            and cycle_one_sources.get("stop_observation")
        ),
        cycle_1_transport_integrity_verified=cycle_one_transport,
        cycle_1_waiting_teacher_review_verified=cycle_one_waiting,
        cycle_1_exact_approval_verified=cycle_one_approval,
        cycle_1_reviewed_memory_chain_verified=cycle_one_chain,
        cycle_1_working_readback_verified=cycle_one_readback,
        cycle_process_separation_verified=process_separation,
        cycle_2_fresh_capture_verified=cycle_two_real,
        cycle_2_readback_preloaded_verified=timing_valid,
        cycle_2_readback_influence_verified=influence_valid,
        cycle_2_readback_contribution=influence_contribution,
        cycle_2_actual_runtime_hot_path_verified=actual_hot_path,
        cycle_2_policy_gate_bypass_detected=policy_bypass,
        cycle_2_extension_verified=bool(
            cycle_two_lineage
            and cycle_two_sources.get("extend_observation_window")
        ),
        cycle_2_focus_shift_verified=bool(
            cycle_two_lineage
            and cycle_two_sources.get("shift_internal_perception_focus")
        ),
        cycle_2_capture_again_verified=bool(
            cycle_two_lineage
            and cycle_two_sources.get("capture_again")
        ),
        cycle_2_stop_observation_verified=bool(
            cycle_two_lineage
            and cycle_two_sources.get("stop_observation")
        ),
        cycle_2_transport_integrity_verified=cycle_two_transport,
        cycle_2_waiting_teacher_review_verified=cycle_two_waiting,
        cycle_2_auto_approval_detected=cycle_two_auto_approval,
        cycle_2_additional_memory_commit_detected=(
            cycle_two_additional_memory
        ),
        **{field: bool(controls.get(field)) for field in _CONTROL_FIELDS},
        stimulus_ground_truth_used_for_runtime_decision=not fixture_firewall,
        hard_coded_experiment_match_used=bool(
            influence_payload.get("hard_coded_experiment_match_used", True)
        ),
        semantic_vision_created=False,
        object_recognition_created=False,
        auditory_concept_created=False,
        auditory_prediction_created=False,
        uncertainty_signal_created=False,
        novelty_signal_created=False,
        curiosity_signal_created=False,
        thought_engine_used=False,
        endocrine_signal_used=False,
        qingyin_output_created=False,
        external_control_created=False,
        package_130_implemented=False,
        package_131_implemented=False,
        package_132_milestone_claimed=False,
        d_laplace_component_used=False,
        dlm_1_implemented=False,
        llm_runtime_calls=0,
        codex_runtime_calls=0,
        network_runtime_calls=0,
        audit_status=status,
        failure_reasons=tuple(dict.fromkeys(failures)),
        source_trace_refs=tuple(
            dict.fromkeys(
                tuple(cycle_one.get("source_trace_refs") or ())
                + tuple(cycle_two.get("source_trace_refs") or ())
                + tuple(
                    influence_payload.get("source_trace_refs") or ()
                )
            )
        ),
    )
    if append:
        store.append_record("package_129_audits", audit)
    return audit


def _record_valid(record_type: Any, payload: dict[str, Any]) -> bool:
    try:
        record_type.from_dict(payload)
    except (TypeError, ValueError):
        return False
    return True


def _cycle_valid(payload: dict[str, Any], cycle_index: int) -> bool:
    try:
        record = ActivePerceptionGrowthCycleRecord.from_dict(payload)
    except (TypeError, ValueError):
        return False
    return record.cycle_index == cycle_index


def _ordered_stages(
    payloads: tuple[dict[str, Any], ...],
    cycle_index: int,
) -> tuple[dict[str, Any], ...]:
    return tuple(
        sorted(
            (
                item
                for item in payloads
                if int(item.get("cycle_index", 0)) == cycle_index
            ),
            key=lambda item: int(item.get("stage_index", 0)),
        )
    )


def _stage_lineage_valid(
    cycle: dict[str, Any],
    stages: tuple[dict[str, Any], ...],
) -> bool:
    if len(stages) != 4:
        return False
    try:
        records = tuple(
            ActivePerceptionStageRecord.from_dict(item) for item in stages
        )
    except (TypeError, ValueError):
        return False
    return bool(
        tuple(item.stage_index for item in records) == (1, 2, 3, 4)
        and tuple(item.stage_kind for item in records) == STAGE_KINDS
        and tuple(item.internal_action_kind for item in records)
        == _ACTION_SEQUENCE
        and tuple(item.stage_record_id for item in records)
        == tuple(cycle.get("stage_record_ids") or ())
        and records[0].observation_window_id
        == cycle.get("parent_observation_window_id")
        and records[1].observation_window_id
        == cycle.get("parent_observation_window_id")
        and records[2].observation_window_id
        == cycle.get("child_observation_window_id")
        and records[3].observation_window_id
        == cycle.get("child_observation_window_id")
    )


def _verify_existing_stage_sources(
    stages: tuple[dict[str, Any], ...],
    *,
    p125_store: Package125ObservationExtensionStore,
    p126_store: Package126ReacquisitionStore,
    p127_store: Package127InternalFocusStore,
    p128_store: Package128SufficiencyStopStore,
) -> dict[str, bool]:
    result = {kind: False for kind in _ACTION_SEQUENCE}
    if len(stages) != 4:
        return result
    specs = (
        (
            p125_store,
            "observation_extension_internal_actions",
            "observation_extension_executions",
            "applied",
        ),
        (
            p127_store,
            "internal_focus_actions",
            "internal_focus_context_sidecars",
            "focused",
        ),
        (
            p126_store,
            "bounded_reacquisition_internal_actions",
            "reacquisition_capture_executions",
            "completed_clean",
        ),
        (
            p128_store,
            "stop_observation_internal_actions",
            "observation_stop_executions",
            "completed_policy_stop",
        ),
    )
    for stage, spec in zip(stages, specs):
        source_store, action_table, execution_table, expected_status = spec
        try:
            action = source_store.get_payload(
                action_table,
                str(stage["internal_action_id"]),
            )
            execution = source_store.get_payload(
                execution_table,
                str(stage["execution_record_id"]),
            )
        except (KeyError, ValueError):
            continue
        action_kind = str(stage.get("internal_action_kind") or "")
        execution_status = (
            execution.get("execution_status")
            if action_kind != "shift_internal_perception_focus"
            else execution.get("focus_state")
        )
        identity_valid = (
            action.get("action_kind") == action_kind
            and action.get("internal_only") is True
            and action.get("external_side_effect") is False
            and execution_status == expected_status
        )
        if action_kind == "extend_observation_window":
            identity_valid = identity_valid and bool(
                execution.get("same_capture_sessions_preserved")
                and execution.get("sources_reopened") is False
            )
        elif action_kind == "capture_again":
            identity_valid = identity_valid and bool(
                execution.get("capture_session_ids_reused") is False
                and execution.get("sources_reopened") is True
                and execution.get("old_artifact_reused") is False
            )
        elif action_kind == "stop_observation":
            identity_valid = identity_valid and bool(
                execution.get("stopped_before_hard_deadline") is True
                and execution.get("all_required_lanes_received_stop")
                is True
                and execution.get("source_sessions_reopened") is False
            )
        result[action_kind] = bool(identity_valid)
    return result


def _cycle_artifact_refs(cycle: dict[str, Any]) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            tuple(cycle.get("parent_screen_artifact_refs") or ())
            + tuple(cycle.get("parent_host_state_artifact_refs") or ())
            + tuple(cycle.get("child_screen_artifact_refs") or ())
            + tuple(cycle.get("child_host_state_artifact_refs") or ())
        )
    )


def _real_artifacts_valid(
    sensor_store: ContentAddressedSensorArtifactStore,
    artifact_refs: tuple[str, ...],
) -> bool:
    if not artifact_refs:
        return False
    try:
        return all(
            bool(
                sensor_store.get_artifact(ref).get("real_device_capture")
                and sensor_store.verify_artifact(ref).get("valid")
            )
            for ref in artifact_refs
        )
    except KeyError:
        return False


def _transport_clean(stages: tuple[dict[str, Any], ...]) -> bool:
    return bool(
        len(stages) == 4
        and all(
            int(stage.get(field, -1)) == 0
            for stage in stages
            for field in _TRANSPORT_FIELDS
        )
    )


def _verify_cycle_one_teacher_commit(
    store: TeacherGatedSessionStore,
    cycle: dict[str, Any],
) -> tuple[bool, bool, bool]:
    session_id = str(cycle.get("bounded_embodied_session_id") or "")
    if not session_id:
        return False, False, False
    decisions = tuple(
        item
        for item in store.list_teacher_decisions(session_id)
        if item.get("decision") == "approved"
        and item.get("approval_scope") == FULL_COMMIT_APPROVAL_SCOPE
        and item.get("target_evidence_snapshot_id")
        == cycle.get("evidence_snapshot_id")
        and item.get("target_evidence_identity_sha256")
        == cycle.get("evidence_identity_hash")
    )
    approval = len(decisions) == 1
    stages = {
        str(item.get("pipeline_stage"))
        for item in store.list_learning_pipeline_identity_bindings(session_id)
        if item.get("identity_preserved") is True
        and item.get("validator_passed") is True
    }
    required_stages = {
        "reviewed_concept",
        "memory_learning_trace",
        "memory_routing_trace",
        "memory_application_data",
        "reviewed_interpretation_commit",
        "working_readback_commit",
    }
    chain = bool(
        approval
        and required_stages.issubset(stages)
        and store.count_rows("reviewed_interpretation_commits", session_id)
        == 1
        and store.count_rows("session_commit_records", session_id) == 1
    )
    readback = tuple(
        item
        for item in store.load_active_working_readback()
        if item.get("source_evidence_snapshot_id")
        == cycle.get("evidence_snapshot_id")
        and item.get("evidence_identity_sha256")
        == cycle.get("evidence_identity_hash")
        and item.get("evidence_theme")
        == "active_perception_sequence_observed"
    )
    provenance_fields = (
        "source_reviewed_concept_ref",
        "memory_learning_trace_ref",
        "memory_routing_trace_ref",
        "memory_application_data_ref",
    )
    readback_valid = bool(
        len(readback) == 1
        and all(readback[0].get(field) for field in provenance_fields)
    )
    return approval, chain, readback_valid


def _process_separation_valid(
    receipts: tuple[dict[str, Any], ...],
    cycle_one: dict[str, Any],
    cycle_two: dict[str, Any],
    comparison: dict[str, Any],
) -> bool:
    ended_cycles = {
        int(item.get("cycle_index", 0))
        for item in receipts
        if item.get("receipt_kind") == "cycle_process_ended"
    }
    return bool(
        ended_cycles == {1, 2}
        and cycle_one.get("process_instance_id")
        != cycle_two.get("process_instance_id")
        and int(cycle_one.get("operating_system_process_id", 0))
        != int(cycle_two.get("operating_system_process_id", 0))
        and comparison.get("process_instances_distinct") is True
        and comparison.get("operating_system_processes_distinct") is True
        and comparison.get("parent_sessions_distinct") is True
        and comparison.get("child_sessions_distinct") is True
        and comparison.get("raw_artifacts_distinct") is True
    )


def _fixture_firewall_valid(
    manifests: tuple[dict[str, Any], ...],
    cycle_one: dict[str, Any],
    cycle_two: dict[str, Any],
    teacher_store: TeacherGatedSessionStore,
) -> bool:
    if len(manifests) != 2 or not all(
        item.get("consumed_by_perception_runtime") is False
        and item.get("result_frozen_before_manifest_audit") is True
        and all(
            transition.get("consumed_by_perception_runtime") is False
            for transition in tuple(item.get("transitions") or ())
        )
        for item in manifests
    ):
        return False
    forbidden = {
        "stimulus_schedule",
        "expected_selected_grid",
        "expected_stop_checkpoint",
        "expected_stop_time",
    }
    try:
        snapshots = (
            teacher_store.load_evidence_snapshot(
                str(cycle_one["evidence_snapshot_id"])
            ),
            teacher_store.load_evidence_snapshot(
                str(cycle_two["evidence_snapshot_id"])
            ),
        )
    except (KeyError, TypeError):
        return False
    return all(
        not forbidden.intersection(
            _recursive_keys(snapshot.canonical_evidence_payload)
        )
        for snapshot in snapshots
    )


def _recursive_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        keys = {str(key) for key in value}
        for item in value.values():
            keys.update(_recursive_keys(item))
        return keys
    if isinstance(value, (list, tuple)):
        keys: set[str] = set()
        for item in value:
            keys.update(_recursive_keys(item))
        return keys
    return set()
