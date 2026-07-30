"""Final evidence-scoped audit for Package 126."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ashl_core_v1.host_body.host_body_internal_action_choice import (
    ALLOWED_INTERNAL_ACTION_KINDS,
)
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.perception_reacquisition_types import (
    BASELINE_COMMIT,
    MAXIMUM_PARENT_TO_CHILD_GAP_NS,
    MAXIMUM_REACQUISITION_WINDOW_NS,
    MAXIMUM_TOTAL_CHAIN_DURATION_NS,
    PACKAGE_126_PASS_STATUS,
    Package126BoundedReacquisitionAudit,
)
from ashl_core_v1.runtime.package_126_reacquisition_store import (
    Package126ReacquisitionStore,
)


PACKAGE_126_AUDIT_SCHEMA_VERSION = "ashl_package_126_bounded_reacquisition_audit_v0"
BLOCKED_AUDIT_STATUS = "blocked_bounded_re_sampling_and_listen_again_internal_action_v0"


def audit_package_126_reacquisition(
    *,
    state_dir: str | Path,
    append: bool = True,
) -> Package126BoundedReacquisitionAudit:
    store = Package126ReacquisitionStore(state_dir)
    runs = store.list_payloads("package_126_real_run_records")
    capture = _latest_action_run(runs, "capture_again")
    listen = _latest_action_run(runs, "listen_again")
    controls = store.latest_payload("package_126_control_results") or {}
    scores = store.list_payloads("package_112_score_equivalence_records")
    event_failures = store.list_payloads("operator_event_delivery_failures")
    failures: list[str] = []

    def require(flag: bool, reason: str) -> bool:
        if not flag:
            failures.append(reason)
        return flag

    package_125_verified = require(
        "extend_observation_window" in ALLOWED_INTERNAL_ACTION_KINDS,
        "package_125_internal_action_registry_missing",
    )
    qm0_verified = require(
        BASELINE_COMMIT == "acb543ed79a9d56bbf4a1660628200f8916497d2",
        "qm0_baseline_commit_mismatch",
    )
    capture_verified = require(
        _run_valid(capture, require_visual=True),
        "capture_again_real_run_not_verified",
    )
    listen_verified = require(
        _run_valid(listen, require_visual=False)
        and _listen_privacy_valid(listen),
        "listen_again_real_run_not_verified",
    )
    capture_action = bool(
        capture
        and capture.get("action_kind") == "capture_again"
        and capture.get("internal_action_id")
    )
    listen_action = bool(
        listen
        and listen.get("action_kind") == "listen_again"
        and listen.get("internal_action_id")
    )
    require(capture_action, "capture_again_action_missing")
    require(listen_action, "listen_again_action_missing")

    parent_windows_clean = all(
        bool(run)
        and str(run.get("parent", {}).get("role")) == "parent"
        and int(run.get("parent", {}).get("required_lane_drop_count", -1)) == 0
        and int(run.get("parent", {}).get("backpressure_fault_count", -1)) == 0
        and int(run.get("parent", {}).get("capture_failure_count", -1)) == 0
        and int(run.get("parent", {}).get("compile_failure_count", -1)) == 0
        and int(run.get("parent", {}).get("flush_remaining_count", -1)) == 0
        for run in (capture, listen)
    )
    child_windows_created = all(
        bool(run)
        and run.get("child", {}).get("observation_window_id")
        and run.get("parent", {}).get("observation_window_id")
        != run.get("child", {}).get("observation_window_id")
        for run in (capture, listen)
    )
    plan_equal = all(
        bool(run)
        and run.get("parent_plan_hash") == run.get("child_plan_hash")
        for run in (capture, listen)
    )
    targets_equal = all(
        bool(run) and run.get("target_identity_equal") is True
        for run in (capture, listen)
    )
    configs_equal = all(
        bool(run) and run.get("configuration_identity_equal") is True
        for run in (capture, listen)
    )
    sessions_distinct = all(
        bool(run) and run.get("capture_session_ids_distinct") is True
        for run in (capture, listen)
    )
    reopened = all(
        bool(run) and run.get("sources_reopened") is True
        for run in (capture, listen)
    )
    gaps = all(
        bool(run)
        and int(run.get("cross_window_gap_ns", -1)) >= 0
        and run.get("continuity_link_id")
        for run in (capture, listen)
    )
    for flag, reason in (
        (parent_windows_clean, "parent_window_not_completed_clean"),
        (child_windows_created, "child_window_missing_or_merged"),
        (plan_equal, "parent_child_plan_identity_mismatch"),
        (targets_equal, "parent_child_target_identity_mismatch"),
        (configs_equal, "parent_child_configuration_mismatch"),
        (sessions_distinct, "capture_session_identity_reused"),
        (reopened, "source_reopen_not_derived"),
        (gaps, "cross_window_gap_missing"),
    ):
        require(flag, reason)

    capture_child = dict(capture.get("child", {})) if capture else {}
    listen_child = dict(listen.get("child", {})) if listen else {}
    new_visual = bool(capture_child.get("visual_primitive_refs"))
    new_audio = bool(
        capture_child.get("audio_primitive_refs")
        and listen_child.get("audio_primitive_refs")
    )
    new_host = bool(
        capture_child.get("host_state_primitive_refs")
        and listen_child.get("host_state_primitive_refs")
    )
    audio_deletion = bool(
        listen_child.get("audio_deletion", {}).get("deletion_verified")
        and listen_child.get("audio_deletion", {}).get(
            "ring_buffer_live_bytes_after"
        )
        == 0
        and listen_child.get("audio_deletion", {}).get("raw_audio_retained")
        is False
    )
    for flag, reason in (
        (new_visual, "child_visual_evidence_missing"),
        (new_audio, "child_audio_evidence_missing"),
        (new_host, "child_host_state_evidence_missing"),
        (audio_deletion, "listen_again_audio_deletion_not_verified"),
    ):
        require(flag, reason)

    child_counts = {
        key: sum(
            int(run.get("child", {}).get(key, 0) or 0)
            for run in (capture, listen)
            if run
        )
        for key in (
            "required_lane_drop_count",
            "backpressure_fault_count",
            "capture_failure_count",
            "compile_failure_count",
            "flush_remaining_count",
        )
    }
    for key, value in child_counts.items():
        require(value == 0, f"child_{key}_nonzero")

    control_fields = (
        "authorization_off_control_passed",
        "parent_active_control_passed",
        "plan_mismatch_control_passed",
        "attempt_limit_control_passed",
        "expired_request_control_passed",
        "old_artifact_replay_control_passed",
        "session_id_reuse_control_passed",
        "transport_fault_control_passed",
        "operator_stop_control_passed",
        "audio_retention_violation_control_passed",
        "no_event_child_control_passed",
    )
    for name in control_fields:
        require(controls.get(name) is True, f"{name}_missing_or_failed")

    package_112_changed = bool(
        len(scores) < 2
        or any(
            item.get("package_112_score_changed")
            or int(item.get("package_126_score_contribution", -1)) != 0
            or int(item.get("authoritative_score_before", -1))
            != int(item.get("authoritative_score_after", -2))
            for item in scores[-2:]
        )
    )
    require(not package_112_changed, "package_112_score_equivalence_failed")
    require(not event_failures, "operator_event_delivery_failure")

    audit_status = PACKAGE_126_PASS_STATUS if not failures else BLOCKED_AUDIT_STATUS
    audit = Package126BoundedReacquisitionAudit(
        audit_id=stable_id("package_126_audit"),
        schema_version=PACKAGE_126_AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        baseline_commit=BASELINE_COMMIT,
        package_125_baseline_verified=package_125_verified,
        qm0_baseline_verified=qm0_verified,
        capture_again_real_run_verified=capture_verified,
        listen_again_real_run_verified=listen_verified,
        capture_again_action_created=capture_action,
        listen_again_action_created=listen_action,
        parent_windows_completed_clean=parent_windows_clean,
        child_windows_created=child_windows_created,
        parent_child_plan_identity_equal=plan_equal,
        parent_child_target_identity_equal=targets_equal,
        parent_child_config_identity_equal=configs_equal,
        capture_session_ids_distinct=sessions_distinct,
        sources_reopened_verified=reopened,
        old_artifact_reused=False,
        cross_window_gap_recorded=gaps,
        windows_falsely_merged=False,
        child_new_visual_evidence_present=new_visual,
        child_new_audio_evidence_present=new_audio,
        child_new_host_state_evidence_present=new_host,
        listen_again_recognition_ephemeral_verified=_listen_privacy_valid(listen),
        raw_audio_retained=False,
        audio_deletion_verified=audio_deletion,
        child_required_lane_drop_count=child_counts[
            "required_lane_drop_count"
        ],
        child_backpressure_fault_count=child_counts[
            "backpressure_fault_count"
        ],
        child_capture_failure_count=child_counts["capture_failure_count"],
        child_compile_failure_count=child_counts["compile_failure_count"],
        child_flush_remaining_count=child_counts["flush_remaining_count"],
        authorization_off_control_passed=bool(
            controls.get("authorization_off_control_passed")
        ),
        parent_active_control_passed=bool(
            controls.get("parent_active_control_passed")
        ),
        plan_mismatch_control_passed=bool(
            controls.get("plan_mismatch_control_passed")
        ),
        attempt_limit_control_passed=bool(
            controls.get("attempt_limit_control_passed")
        ),
        expired_request_control_passed=bool(
            controls.get("expired_request_control_passed")
        ),
        old_artifact_replay_control_passed=bool(
            controls.get("old_artifact_replay_control_passed")
        ),
        session_id_reuse_control_passed=bool(
            controls.get("session_id_reuse_control_passed")
        ),
        transport_fault_control_passed=bool(
            controls.get("transport_fault_control_passed")
        ),
        operator_stop_control_passed=bool(
            controls.get("operator_stop_control_passed")
        ),
        audio_retention_violation_control_passed=bool(
            controls.get("audio_retention_violation_control_passed")
        ),
        no_event_child_control_passed=bool(
            controls.get("no_event_child_control_passed")
        ),
        package_112_score_changed=package_112_changed,
        memory_write_created=False,
        working_readback_created=False,
        focus_selection_created=False,
        evidence_sufficiency_runtime_created=False,
        uncertainty_signal_created=False,
        novelty_signal_created=False,
        thought_engine_used=False,
        output_created=False,
        external_control_created=False,
        same_event_claimed=False,
        same_sound_claimed=False,
        speaker_recognition_claimed=False,
        language_understanding_claimed=False,
        subjective_listening_claimed=False,
        package_127_implemented=False,
        package_128_implemented=False,
        d_laplace_component_used=False,
        d_laplace_migration_performed=False,
        dlm_1_implemented=False,
        llm_runtime_calls=0,
        codex_runtime_calls=0,
        network_runtime_calls=0,
        audit_status=audit_status,
        failure_reasons=tuple(dict.fromkeys(failures)),
        source_trace_refs=tuple(),
    )
    if append:
        store.append_record("package_126_audits", audit)
    return audit


def _latest_action_run(
    runs: tuple[dict[str, Any], ...],
    action_kind: str,
) -> dict[str, Any]:
    matches = tuple(
        item
        for item in runs
        if item.get("action_kind") == action_kind
        and item.get("run_status") == "passed_real_bounded_reacquisition"
    )
    return dict(matches[-1]) if matches else {}


def _run_valid(run: dict[str, Any], *, require_visual: bool) -> bool:
    if not run:
        return False
    child = dict(run.get("child", {}))
    parent = dict(run.get("parent", {}))
    parent_duration_ns = int(parent.get("actual_window_ns", -1))
    child_duration_ns = int(child.get("actual_window_ns", -1))
    gap_ns = int(run.get("cross_window_gap_ns", -1))
    return bool(
        run.get("run_status") == "passed_real_bounded_reacquisition"
        and run.get("parent_plan_hash") == run.get("child_plan_hash")
        and run.get("target_identity_equal") is True
        and run.get("configuration_identity_equal") is True
        and run.get("capture_session_ids_distinct") is True
        and run.get("sources_reopened") is True
        and run.get("old_artifact_reused") is False
        and 0 < parent_duration_ns <= MAXIMUM_REACQUISITION_WINDOW_NS
        and 0 < child_duration_ns <= MAXIMUM_REACQUISITION_WINDOW_NS
        and 0 <= gap_ns <= MAXIMUM_PARENT_TO_CHILD_GAP_NS
        and parent_duration_ns + gap_ns + child_duration_ns
        <= MAXIMUM_TOTAL_CHAIN_DURATION_NS
        and parent.get("observation_window_id")
        != child.get("observation_window_id")
        and int(parent.get("required_windows_expected", 0)) > 0
        and int(parent.get("required_windows_complete", -1))
        == int(parent.get("required_windows_expected", 0))
        and int(child.get("required_windows_expected", 0)) > 0
        and int(child.get("required_windows_complete", -1))
        == int(child.get("required_windows_expected", 0))
        and child.get("audio_primitive_refs")
        and child.get("host_state_primitive_refs")
        and (child.get("visual_primitive_refs") if require_visual else True)
        and int(child.get("required_lane_drop_count", -1)) == 0
        and int(child.get("backpressure_fault_count", -1)) == 0
        and int(child.get("capture_failure_count", -1)) == 0
        and int(child.get("compile_failure_count", -1)) == 0
        and int(child.get("flush_remaining_count", -1)) == 0
        and int(run.get("operator_event_delivery_failure_count", -1)) == 0
    )


def _listen_privacy_valid(run: dict[str, Any]) -> bool:
    if not run:
        return False
    child = dict(run.get("child", {}))
    deletion = dict(child.get("audio_deletion", {}))
    return bool(
        child.get("screen_capture_session_id") is None
        and child.get("ephemeral_audio_session_id")
        and child.get("audio_event_region_present") is True
        and child.get("raw_audio_retained") is False
        and child.get("raw_parent_artifact_reused") is False
        and child.get("semantic_interpretation_created") is False
        and child.get("recognition_result_created") is False
        and deletion.get("deletion_verified") is True
        and deletion.get("ring_buffer_live_bytes_after") == 0
        and deletion.get("backend_transient_file_created") is False
    )
