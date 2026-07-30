"""Evidence-scoped final audit for Package 128."""

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
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
    ContentAddressedSensorArtifactStore,
)
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.internal_perception_focus_types import (
    PACKAGE_127_PASS_STATUS,
)
from ashl_core_v1.runtime.package_126_reacquisition_store import (
    Package126ReacquisitionStore,
)
from ashl_core_v1.runtime.package_124a_temporal_store import (
    Package124ATemporalStore,
)
from ashl_core_v1.runtime.package_127_internal_focus_store import (
    Package127InternalFocusStore,
)
from ashl_core_v1.runtime.package_128_sufficiency_stop_store import (
    Package128SufficiencyStopStore,
)
from ashl_core_v1.runtime.perception_reacquisition_types import (
    PACKAGE_126_PASS_STATUS,
)
from ashl_core_v1.runtime.structural_evidence_sufficiency_types import (
    BASELINE_COMMIT,
    CONTRACT_KIND,
    PACKAGE_128_BLOCKED_STATUS,
    PACKAGE_128_PASS_STATUS,
    STOP_ACTION_KIND,
    Package128StructuralEvidenceSufficiencyStopAudit,
)


PACKAGE_128_AUDIT_SCHEMA_VERSION = (
    "ashl_package_128_structural_evidence_sufficiency_stop_audit_v0"
)


def audit_package_128_sufficiency_stop(
    *,
    state_dir: str | Path,
    append: bool = True,
) -> Package128StructuralEvidenceSufficiencyStopAudit:
    path = Path(state_dir)
    store = Package128SufficiencyStopStore(path)
    focus_store = Package127InternalFocusStore(path)
    reacquisition_store = Package126ReacquisitionStore(path)
    temporal_store = Package124ATemporalStore(path)
    sensor_store = ContentAddressedSensorArtifactStore(path)
    run = _latest_passed_run(
        store.list_payloads("package_128_real_run_records")
    )
    control_fields = (
        "open_event_control_passed",
        "insufficient_post_context_control_passed",
        "no_event_control_passed",
        "authorization_off_control_passed",
        "wrong_window_control_passed",
        "stale_checkpoint_control_passed",
        "transport_fault_control_passed",
        "operator_stop_control_passed",
        "duplicate_stop_control_passed",
        "stimulus_injection_control_passed",
        "semantic_injection_control_passed",
        "incomplete_focus_control_passed",
    )
    controls = _latest_complete_controls(
        store.list_payloads("package_128_control_results"),
        control_fields,
    )
    checkpoints = tuple(
        item
        for item in store.list_payloads(
            "structural_evidence_checkpoints"
        )
        if item.get("checkpoint_id")
        in set(run.get("checkpoint_ids") or ())
    )
    assessments = tuple(
        item
        for item in store.list_payloads(
            "structural_evidence_assessments"
        )
        if item.get("assessment_id")
        in set(run.get("assessment_ids") or ())
    )
    contract = _payload_or_empty(
        store,
        "structural_sufficiency_contracts",
        str(run.get("contract_id") or ""),
    )
    action = _payload_or_empty(
        store,
        "stop_observation_internal_actions",
        str(run.get("stop_action_id") or ""),
    )
    execution = _payload_or_empty(
        store,
        "observation_stop_executions",
        str(run.get("stop_execution_id") or ""),
    )
    completion = _payload_or_empty(
        store,
        "observation_completion_records",
        str(run.get("completion_record_id") or ""),
    )
    score = _payload_or_empty(
        store,
        "package_128_score_equivalence_records",
        str(run.get("package_112_score_equivalence_id") or ""),
    )
    reacquisition_execution = _payload_or_empty(
        reacquisition_store,
        "reacquisition_capture_executions",
        str(run.get("reacquisition_execution_id") or ""),
    )
    reacquisition_action = _payload_or_empty(
        reacquisition_store,
        "bounded_reacquisition_internal_actions",
        str(reacquisition_execution.get("internal_action_id") or ""),
    )
    active_focus = _payload_or_empty(
        focus_store,
        "internal_focus_context_sidecars",
        str(run.get("active_focus_context_id") or ""),
    )
    released_focus = _payload_or_empty(
        focus_store,
        "internal_focus_context_sidecars",
        str(run.get("released_focus_context_id") or ""),
    )
    focus_release = _payload_or_empty(
        focus_store,
        "internal_focus_release_records",
        str(run.get("focus_release_record_id") or ""),
    )
    final_temporal_bundle = _payload_or_empty(
        temporal_store,
        "grounded_temporal_bundles",
        str(run.get("final_temporal_bundle_id") or ""),
    )
    failures: list[str] = []

    def require(flag: bool, reason: str) -> bool:
        if not flag:
            failures.append(reason)
        return flag

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
        "extend_observation_window" in ALLOWED_INTERNAL_ACTION_KINDS,
        "package_125_baseline_not_verified",
    )
    qm0_verified = require(
        D_LAPLACE_QM0_AUDIT_STATUS
        == "passed_d_laplace_qm0_read_only_migration_audit_v0"
        and QINGYIN_MIGRATION_STATUS
        == "QINGYIN_MIGRATION_INCOMPLETE_AUDIT_LAYER",
        "qm0_baseline_not_verified",
    )
    child = dict(run.get("child") or {})
    focused_child = require(
        bool(
            run.get("package_126_child_window_used") is True
            and run.get("focus_plan_id")
            and run.get("active_focus_context_id")
            and child.get("screen_capture_session_id")
            and child.get("host_state_capture_session_id")
            and child.get("observation_window_id")
            and reacquisition_execution.get("execution_status")
            == "completed_clean"
            and reacquisition_execution.get(
                "child_observation_window_id"
            )
            == child.get("observation_window_id")
            and set(
                reacquisition_execution.get(
                    "child_capture_session_refs"
                )
                or ()
            )
            == set(child.get("capture_session_refs") or ())
            and reacquisition_execution.get(
                "capture_session_ids_reused"
            )
            is False
            and reacquisition_execution.get("sources_reopened")
            is True
            and reacquisition_execution.get("old_artifact_reused")
            is False
            and int(
                reacquisition_execution.get("actual_window_ns", -1)
            )
            <= int(reacquisition_action.get("granted_window_ns", -2))
        ),
        "real_focused_child_window_not_verified",
    )
    full_frame = require(
        bool(
            run.get("full_frame_preserved") is True
            and child.get("visual_primitive_refs")
            and child.get("visual_readable_data_refs")
        ),
        "full_frame_not_preserved",
    )
    focused_evidence = require(
        run.get("focused_region_evidence_present") is True,
        "focused_region_evidence_not_verified",
    )
    contract_authorized = require(
        bool(
            contract
            and run.get("contract_authorized") is True
            and contract.get("authorization_source")
            == "explicit_session_configuration"
            and contract.get("authorized_by") == "local_operator"
        ),
        "explicit_contract_authorization_not_verified",
    )
    contract_kind = require(
        contract.get("contract_kind") == CONTRACT_KIND,
        "contract_kind_not_verified",
    )
    checkpoint_count = len(checkpoints)
    checkpoint_lineage = require(
        bool(
            checkpoint_count >= 1
            and len(assessments) == checkpoint_count
            and all(
                item.get("contract_id") == contract.get("contract_id")
                and item.get("runtime_session_id")
                == child.get("runtime_session_id")
                and item.get("perception_session_id")
                == child.get("perception_session_id")
                and item.get("observation_window_id")
                == child.get("observation_window_id")
                and item.get("semantic_label") is None
                and item.get("uncertainty_score") is None
                and item.get("confidence_score") is None
                and _checkpoint_artifacts_exist(
                    sensor_store,
                    item,
                    child,
                )
                for item in checkpoints
            )
        ),
        "checkpoints_not_grounded_in_runtime_evidence",
    )
    final_assessment = next(
        (
            item
            for item in assessments
            if item.get("assessment_id")
            == run.get("final_assessment_id")
        ),
        {},
    )
    final_sufficient = require(
        bool(
            final_assessment.get("assessment_status") == "sufficient"
            and final_assessment.get("contract_satisfied") is True
            and not final_assessment.get("failure_reasons")
        ),
        "final_assessment_not_sufficient",
    )
    structural_keys = (
        "minimum_elapsed_met",
        "minimum_complete_windows_met",
        "focused_region_evidence_present",
        "full_frame_preserved",
        "observed_visual_region_present",
        "all_visual_regions_closed",
        "no_open_visual_region_remaining",
        "post_event_coverage_met",
        "required_lane_coverage_complete",
        "transport_integrity_valid",
        "clock_integrity_valid",
        "lineage_integrity_valid",
    )
    all_criteria = require(
        bool(
            final_assessment
            and all(
                final_assessment.get(key) is True
                for key in structural_keys
            )
        ),
        "structural_criteria_not_all_verified",
    )
    policy_allowed = require(
        run.get("policy_decision") == "allow_policy_stop",
        "policy_stop_not_allowed",
    )
    action_created = require(
        bool(
            action
            and action.get("action_kind") == STOP_ACTION_KIND
            and action.get("internal_only") is True
            and action.get("external_side_effect") is False
            and STOP_ACTION_KIND in ALLOWED_INTERNAL_ACTION_KINDS
        ),
        "stop_observation_action_not_verified",
    )
    stopped_early = require(
        bool(
            execution.get("stopped_before_hard_deadline") is True
            and int(
                execution.get(
                    "final_observation_end_event_time_ns", 0
                )
            )
            < int(
                execution.get(
                    "original_hard_deadline_event_time_ns", 0
                )
            )
        ),
        "observation_not_stopped_before_deadline",
    )
    all_lanes_stopped = require(
        bool(
            execution.get("screen_stop_signal_applied") is True
            and execution.get("host_state_stop_signal_applied") is True
            and execution.get("all_required_lanes_received_stop")
            is True
            and execution.get("producers_stopped") is True
        ),
        "required_lanes_not_stopped_together",
    )
    source_sessions_reopened = bool(
        execution.get("source_sessions_reopened")
    )
    require(
        not source_sessions_reopened,
        "source_sessions_reopened_by_policy_stop",
    )
    alignment_changed = bool(
        execution.get("alignment_origin_changed")
    )
    require(
        not alignment_changed,
        "alignment_origin_changed_by_policy_stop",
    )
    focus_changed = bool(execution.get("focus_context_changed"))
    require(
        not focus_changed,
        "focus_context_changed_before_completion",
    )
    flush_completed = require(
        bool(
            execution.get("artifacts_finalized") is True
            and execution.get("compilers_drained") is True
            and execution.get("ingress_queues_drained") is True
            and execution.get("alignment_finalized") is True
            and int(completion.get("flush_remaining_count", -1)) == 0
        ),
        "final_flush_not_verified",
    )
    require(
        bool(
            completion.get("completion_kind")
            == "policy_sufficient_stop"
            and completion.get("contract_satisfied") is True
            and completion.get("final_temporal_bundle_id")
            == run.get("final_temporal_bundle_id")
            and final_temporal_bundle.get("temporal_bundle_id")
            == run.get("final_temporal_bundle_id")
            and set(run.get("final_closed_visual_span_refs") or ())
            .issubset(
                set(final_temporal_bundle.get("span_refs") or ())
            )
        ),
        "final_completion_or_temporal_bundle_not_verified",
    )
    focus_released = require(
        bool(
            active_focus.get("focus_state") == "focused"
            and active_focus.get("automatically_released") is False
            and released_focus.get("focus_state") == "released"
            and released_focus.get("automatically_released") is True
            and released_focus.get("child_observation_window_id")
            == child.get("observation_window_id")
            and focus_release.get("focus_context_id")
            == active_focus.get("focus_context_id")
            and focus_release.get("new_focus_state") == "released"
            and focus_release.get("child_window_count") == 1
            and focus_release.get("history_preserved") is True
            and completion.get("final_focus_context_id")
            == released_focus.get("focus_context_id")
        ),
        "focus_release_not_verified",
    )
    transport_counts = {
        "required_lane_drop_count": int(
            completion.get("required_lane_drop_count", -1)
        ),
        "backpressure_fault_count": int(
            completion.get("backpressure_fault_count", -1)
        ),
        "capture_failure_count": int(
            completion.get("capture_failure_count", -1)
        ),
        "compile_failure_count": int(
            completion.get("compile_failure_count", -1)
        ),
        "flush_remaining_count": int(
            completion.get("flush_remaining_count", -1)
        ),
    }
    for name, value in transport_counts.items():
        require(value == 0, f"{name}_not_zero")
    for name in control_fields:
        require(
            controls.get(name) is True,
            name.replace("_passed", "_failed"),
        )
    score_changed = bool(
        score.get("package_112_score_changed", True)
    )
    require(
        not score_changed
        and score.get("package_128_score_contribution") == 0,
        "package_112_score_equivalence_failed",
    )
    event_failures = (
        store.list_payloads("operator_event_delivery_failures")
        + focus_store.list_payloads(
            "operator_event_delivery_failures"
        )
        + reacquisition_store.list_payloads(
            "operator_event_delivery_failures"
        )
    )
    require(
        not event_failures,
        "operator_event_delivery_failure_visible",
    )
    boundary_false_fields = (
        "memory_write_created",
        "working_readback_created",
        "package_128_extension_action_created",
        "package_128_reacquisition_action_created",
        "package_128_focus_shift_action_created",
        "uncertainty_signal_created",
        "novelty_signal_created",
        "thought_engine_used",
        "endocrine_signal_used",
        "output_created",
        "external_control_created",
        "semantic_understanding_claimed",
        "recognition_claimed",
        "certainty_claimed",
        "subjective_time_claimed",
        "package_129_implemented",
        "package_130_implemented",
        "package_131_implemented",
        "d_laplace_component_used",
        "dlm_1_implemented",
    )
    for name in boundary_false_fields:
        require(
            run.get(name) is False,
            f"boundary_violation:{name}",
        )
    for name in (
        "llm_runtime_calls",
        "codex_runtime_calls",
        "network_runtime_calls",
    ):
        require(int(run.get(name, -1)) == 0, f"{name}_not_zero")
    require(
        run.get("fixture_manifest_consumed_by_runtime") is False
        and run.get("fixture_manifest_audited_after_result_frozen")
        is True,
        "stimulus_ground_truth_firewall_not_verified",
    )

    status = (
        PACKAGE_128_PASS_STATUS
        if not failures
        else PACKAGE_128_BLOCKED_STATUS
    )
    audit = Package128StructuralEvidenceSufficiencyStopAudit(
        audit_id=stable_id("package_128_audit"),
        schema_version=PACKAGE_128_AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        baseline_commit=BASELINE_COMMIT,
        package_127_baseline_verified=package_127_verified,
        package_126_baseline_verified=package_126_verified,
        package_125_baseline_verified=package_125_verified,
        qm0_baseline_verified=qm0_verified,
        real_focused_child_window_verified=focused_child,
        full_frame_preserved=full_frame,
        focused_region_evidence_verified=focused_evidence,
        explicit_contract_authorization_verified=contract_authorized,
        contract_kind_verified=contract_kind,
        checkpoint_count=checkpoint_count,
        checkpoints_from_actual_runtime_evidence=checkpoint_lineage,
        final_assessment_sufficient=final_sufficient,
        all_structural_criteria_verified=all_criteria,
        policy_stop_allowed=policy_allowed,
        stop_observation_action_created=action_created,
        stop_action_kind_verified=(
            action.get("action_kind") == STOP_ACTION_KIND
        ),
        stopped_before_hard_deadline=stopped_early,
        all_required_lanes_stopped=all_lanes_stopped,
        source_sessions_reopened=source_sessions_reopened,
        alignment_origin_changed=alignment_changed,
        focus_context_changed_before_completion=focus_changed,
        flush_completed=flush_completed,
        focus_released_at_completion=focus_released,
        **transport_counts,
        **{
            name: bool(controls.get(name))
            for name in control_fields
        },
        package_112_score_changed=score_changed,
        memory_write_created=False,
        working_readback_created=False,
        extension_action_created=False,
        reacquisition_action_created=False,
        focus_shift_action_created=False,
        uncertainty_signal_created=False,
        novelty_signal_created=False,
        thought_engine_used=False,
        endocrine_signal_used=False,
        output_created=False,
        external_control_created=False,
        semantic_understanding_claimed=False,
        recognition_claimed=False,
        certainty_claimed=False,
        subjective_time_claimed=False,
        package_129_implemented=False,
        package_130_implemented=False,
        package_131_implemented=False,
        d_laplace_component_used=False,
        dlm_1_implemented=False,
        llm_runtime_calls=0,
        codex_runtime_calls=0,
        network_runtime_calls=0,
        audit_status=status,
        failure_reasons=tuple(dict.fromkeys(failures)),
        source_trace_refs=tuple(),
    )
    if append:
        store.append_record("package_128_audits", audit)
    return audit


def _latest_passed_run(
    runs: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    return next(
        (
            item
            for item in reversed(runs)
            if item.get("run_status")
            == "passed_real_structural_sufficiency_policy_stop"
        ),
        {},
    )


def _latest_complete_controls(
    records: tuple[dict[str, Any], ...],
    required_fields: tuple[str, ...],
) -> dict[str, Any]:
    return next(
        (
            item
            for item in reversed(records)
            if all(field in item for field in required_fields)
        ),
        {},
    )


def _payload_or_empty(
    store: Any,
    table: str,
    record_id: str,
) -> dict[str, Any]:
    if not record_id:
        return {}
    try:
        return store.get_payload(table, record_id)
    except KeyError:
        return {}


def _checkpoint_artifacts_exist(
    sensor_store: ContentAddressedSensorArtifactStore,
    checkpoint: dict[str, Any],
    child: dict[str, Any],
) -> bool:
    child_artifacts = set(child.get("screen_artifact_ids") or ())
    child_artifacts.update(child.get("host_artifact_ids") or ())
    refs = set(checkpoint.get("source_record_refs") or ())
    artifact_refs = tuple(child_artifacts.intersection(refs))
    if len(artifact_refs) < 2:
        return False
    try:
        return all(
            bool(sensor_store.get_artifact(ref))
            for ref in artifact_refs
        )
    except KeyError:
        return False
