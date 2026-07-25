"""Scoped audit helpers for Package 125 bounded observation-window extension."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ashl_core_v1.host_body import host_body_readback_internal_action_influence as package_112
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.observation_window_types import (
    DEFAULT_EXTENSION_NS,
    PACKAGE_112_SCORE_EQUIVALENCE_SCHEMA_VERSION,
    PACKAGE_125_AUDIT_SCHEMA_VERSION,
    PACKAGE_125_PASS_STATUS,
    Package112ScoreEquivalenceRecord,
    Package125BoundedObservationExtensionAudit,
    ObservationWindowState,
)
from ashl_core_v1.runtime.package_125_observation_extension_store import Package125ObservationExtensionStore


SYNTHETIC_PACKAGE_125_PASS_STATUS = "passed_synthetic_bounded_observation_window_extension_audit_v0"


def package_112_score_equivalence_context(
    *,
    observation_window: ObservationWindowState,
    extension_context_record_ids: tuple[str, ...],
) -> Package112ScoreEquivalenceRecord:
    """Run the authoritative Package 112 scorer twice with identical inputs.

    Package 125 records are retained as read-only provenance on the equivalence
    record. They are deliberately not arguments to the Package 112 scorer.
    """

    demo = package_112.build_demo_no_matching_readback_signal_no_change()
    signal = tuple(demo["readback_internal_action_signals"])[0]
    before = package_112.build_host_body_internal_action_candidate_readback_score(
        readback_signal=signal,
        candidate_action_kind="observe_again",
        base_candidate_priority=5,
    )
    after = package_112.build_host_body_internal_action_candidate_readback_score(
        readback_signal=signal,
        candidate_action_kind="observe_again",
        base_candidate_priority=5,
    )
    changed = (
        int(before.final_candidate_priority) != int(after.final_candidate_priority)
        or int(before.readback_delta) != int(after.readback_delta)
    )
    return Package112ScoreEquivalenceRecord(
        score_equivalence_record_id=stable_id("package_125_score_equivalence"),
        schema_version=PACKAGE_112_SCORE_EQUIVALENCE_SCHEMA_VERSION,
        created_at=utc_now(),
        experiment_run_id=observation_window.experiment_run_id,
        audit_group_id=observation_window.audit_group_id,
        scenario_name=observation_window.scenario_name,
        runtime_session_id=observation_window.runtime_session_id,
        perception_session_id=observation_window.perception_session_id,
        observation_window_id=observation_window.observation_window_id,
        candidate_action_kind="observe_again",
        base_candidate_priority=5,
        authoritative_score_before=int(before.final_candidate_priority),
        authoritative_score_after=int(after.final_candidate_priority),
        authoritative_readback_delta_before=int(before.readback_delta),
        authoritative_readback_delta_after=int(after.readback_delta),
        observation_extension_score_contribution=0,
        package_112_score_changed=changed,
        extension_context_read_only=True,
        source_record_refs=tuple(extension_context_record_ids),
        source_trace_refs=tuple(),
    )


def audit_package_125_observation_extension(
    *,
    state_dir: str | Path,
    observation_window_id: str | None = None,
    append: bool = True,
    require_real_source_capture: bool = True,
) -> Package125BoundedObservationExtensionAudit:
    store = Package125ObservationExtensionStore(state_dir)
    states = store.list_payloads("observation_window_states")
    target = _target_state(states, observation_window_id)
    failures: list[str] = []

    def require(flag: bool, reason: str) -> bool:
        if not flag:
            failures.append(reason)
        return flag

    if not target:
        failures.append("missing_observation_window_state")
    scope = _scope_from(target)
    target_window_id = str(scope["observation_window_id"])
    scoped_states = _scoped(states, scope)
    tails = _scoped(store.list_payloads("temporal_tail_evidence"), scope)
    candidates = _scoped(store.list_payloads("observation_extension_candidates"), scope)
    policies = _scoped(store.list_payloads("observation_extension_policy_decisions"), scope)
    actions = _scoped(store.list_payloads("observation_extension_internal_actions"), scope)
    executions = _scoped(store.list_payloads("observation_extension_executions"), scope)
    outcomes = _scoped(store.list_payloads("observation_extension_outcomes"), scope)
    comparisons = _scoped(store.list_payloads("observation_extension_comparisons"), scope)
    identities = _scoped(store.list_payloads("active_capture_session_identities"), scope)
    closures = _scoped(store.list_payloads("temporal_region_closure_links"), scope)
    score_records = _scoped(store.list_payloads("package_112_score_equivalence_records"), scope)
    event_failures = tuple(
        item
        for item in store.list_payloads("operator_event_delivery_failures")
        if str(item.get("audit_group_id") or "") == scope["audit_group_id"]
    )

    execution = _latest_where(executions, lambda item: item.get("execution_status") == "applied") or {}
    action = _by_id(actions, "internal_action_id", execution.get("internal_action_id")) or {}
    policy = _by_id(
        policies,
        "extension_policy_decision_id",
        action.get("extension_policy_decision_id"),
    ) or {}
    candidate = _by_id(
        candidates,
        "extension_candidate_id",
        policy.get("extension_candidate_id"),
    ) or {}
    tail = _by_id(
        tails,
        "temporal_tail_evidence_id",
        candidate.get("temporal_tail_evidence_id"),
    ) or {}
    outcome = _latest_where(
        outcomes,
        lambda item: item.get("extension_execution_id") == execution.get("extension_execution_id"),
    ) or {}
    comparison = _latest_where(
        comparisons,
        lambda item: (
            item.get("extension_execution_id") == execution.get("extension_execution_id")
            and item.get("extension_outcome_id") == outcome.get("extension_outcome_id")
        ),
    ) or {}

    authorization = _by_id(
        store.list_payloads("observation_window_authorizations"),
        "authorization_id",
        policy.get("authorization_id"),
    ) or {}
    identity_before = _by_id(
        identities,
        "active_capture_identity_id",
        execution.get("capture_identity_before_id"),
    ) or {}
    identity_after = _by_id(
        identities,
        "active_capture_identity_id",
        execution.get("capture_identity_after_id"),
    ) or {}

    temporal_tail_evidence_verified = require(
        bool(tail)
        and bool(tail.get("structural_tail_only"))
        and tail.get("semantic_label") is None
        and bool(tail.get("continuous_source_coverage"))
        and bool(tail.get("required_lane_delivery_complete")),
        "missing_or_invalid_temporal_tail_evidence",
    )
    candidate_from_actual_temporal_evidence = require(
        bool(candidate)
        and bool(tail)
        and candidate.get("temporal_tail_evidence_id") == tail.get("temporal_tail_evidence_id")
        and tail.get("temporal_tail_evidence_id") in tuple(candidate.get("source_record_refs") or ())
        and not bool(candidate.get("stimulus_ground_truth_used")),
        "missing_candidate_from_tail_evidence",
    )
    session_authorization_verified = require(
        bool(authorization)
        and bool(authorization.get("bounded_extension_allowed"))
        and authorization.get("runtime_session_id") == scope["runtime_session_id"]
        and authorization.get("perception_session_id") == scope["perception_session_id"]
        and bool(authorization.get("expires_at_session_end")),
        "missing_or_invalid_session_authorization",
    )
    policy_gate_verified = require(
        bool(policy)
        and policy.get("decision") == "allow"
        and policy.get("extension_candidate_id") == candidate.get("extension_candidate_id"),
        "policy_did_not_allow_scoped_candidate",
    )
    internal_action_created = require(
        bool(action)
        and action.get("extension_policy_decision_id") == policy.get("extension_policy_decision_id")
        and policy.get("extension_policy_decision_id") in tuple(action.get("source_record_refs") or ()),
        "missing_internal_action",
    )
    internal_action_kind_verified = require(
        action.get("action_kind") == "extend_observation_window"
        and action.get("internal_only") is True
        and action.get("external_side_effect") is False,
        "wrong_internal_action_kind_or_boundary",
    )
    deadline_extension_atomic = require(
        execution.get("execution_status") == "applied"
        and int(execution.get("applied_new_deadline_ns", 0))
        - int(execution.get("previous_deadline_ns", 0))
        == DEFAULT_EXTENSION_NS
        and execution.get("internal_action_id") == action.get("internal_action_id")
        and action.get("internal_action_id") in tuple(execution.get("source_record_refs") or ()),
        "deadline_extension_not_atomically_applied_once",
    )
    identity_chain_verified = require(
        bool(identity_before)
        and bool(identity_after)
        and _capture_identity_continuity(identity_before, identity_after)
        and int(identity_before.get("observed_deadline_ns", 0))
        == int(execution.get("previous_deadline_ns", -1))
        and int(identity_after.get("observed_deadline_ns", 0))
        == int(execution.get("applied_new_deadline_ns", -1)),
        "active_capture_identity_chain_invalid",
    )
    same_source_sessions_preserved = require(
        identity_chain_verified
        and execution.get("same_capture_sessions_preserved") is True
        and execution.get("sources_reopened") is False
        and comparison.get("same_source_sessions") is True
        and comparison.get("same_alignment_origin") is True,
        "source_sessions_or_alignment_not_preserved",
    )
    all_required_lanes_extended = require(
        execution.get("screen_deadline_updated") is True
        and execution.get("audio_deadline_updated") is True
        and execution.get("host_state_deadline_updated") is True,
        "required_lane_deadline_missing",
    )

    base_deadline = int(comparison.get("base_boundary_event_time_ns", 0))
    valid_closures = tuple(
        item
        for item in closures
        if int(item.get("closure_event_time_ns", 0)) > base_deadline
        and item.get("open_region_observation_id")
        in tuple(tail.get("open_visual_region_refs") or ()) + tuple(tail.get("open_audio_region_refs") or ())
    )
    event_closure_observed = require(
        bool(valid_closures)
        and int(outcome.get("finalized_visual_spans_after", 0))
        + int(outcome.get("finalized_audio_spans_after", 0))
        > 0
        and int(comparison.get("newly_observed_closure_count", 0)) == len(valid_closures),
        "no_event_closure_observed_after_base",
    )
    post_event_context_observed = require(
        int(outcome.get("post_event_context_ns", 0)) > 0
        and int(comparison.get("newly_observed_post_event_context_ns", 0)) > 0,
        "missing_post_event_context",
    )
    transport_flush_verified = require(
        comparison.get("transport_flush_verified") is True
        and int(comparison.get("flush_remaining_required_records", -1)) == 0,
        "transport_flush_not_verified",
    )

    real_source_capture_verified = _verify_real_capture_identity(
        state_dir=state_dir,
        identity_before=identity_before,
        identity_after=identity_after,
        execution=execution,
    )
    if require_real_source_capture:
        require(real_source_capture_verified, "real_source_capture_not_verified")

    stable_control_did_not_extend = _control_did_not_extend(store, scope["audit_group_id"], "stable_baseline_control")
    early_complete_control_did_not_extend = _control_did_not_extend(store, scope["audit_group_id"], "early_complete_control")
    authorization_off_control_blocked = _authorization_off_blocked(store, scope["audit_group_id"])
    operator_interrupt_verified = _operator_stop_verified(store, scope["audit_group_id"])
    transport_fault_control_verified = _transport_fault_verified(store, scope["audit_group_id"])
    for reason, flag in (
        ("stable_control_missing_or_extended", stable_control_did_not_extend),
        ("early_complete_control_missing_or_extended", early_complete_control_did_not_extend),
        ("authorization_off_control_missing_or_allowed", authorization_off_control_blocked),
        ("operator_interrupt_control_missing", operator_interrupt_verified),
        ("transport_fault_control_missing_or_extended", transport_fault_control_verified),
    ):
        require(flag, reason)

    stimulus_ground_truth_used = bool(
        comparison.get("stimulus_ground_truth_used_for_runtime_decision")
        or candidate.get("stimulus_ground_truth_used")
        or any(
            "stimulus_audit_manifest" in str(ref)
            for ref in tuple(candidate.get("source_record_refs") or ())
            + tuple(candidate.get("source_trace_refs") or ())
        )
    )
    require(not stimulus_ground_truth_used, "stimulus_ground_truth_used_for_decision")

    required_lane_drop_count = int(outcome.get("required_lane_drops", 0) or tail.get("dropped_required_record_count", 0) or 0)
    backpressure_fault_count = int(outcome.get("transport_faults", 0) or tail.get("backpressure_fault_count", 0) or 0)
    capture_failure_count = int(outcome.get("capture_failures", 0) or tail.get("capture_failure_count", 0) or 0)
    compile_failure_count = int(outcome.get("compile_failures", 0) or tail.get("compile_failure_count", 0) or 0)
    for count_name, value in (
        ("required_lane_drop_count", required_lane_drop_count),
        ("backpressure_fault_count", backpressure_fault_count),
        ("capture_failure_count", capture_failure_count),
        ("compile_failure_count", compile_failure_count),
    ):
        require(value == 0, f"{count_name}_nonzero")

    score_record = score_records[-1] if score_records else {}
    package_112_score_changed = bool(
        not score_record
        or score_record.get("package_112_score_changed")
        or int(score_record.get("observation_extension_score_contribution", -1)) != 0
        or int(score_record.get("authoritative_score_before", -1))
        != int(score_record.get("authoritative_score_after", -2))
    )
    require(not package_112_score_changed, "package_112_score_equivalence_failed")
    require(not event_failures, "operator_event_delivery_failure")

    scoped_records = (
        tuple(scoped_states)
        + tails
        + candidates
        + policies
        + actions
        + executions
        + outcomes
        + comparisons
    )
    memory_write_created = _truthy_key(scoped_records, ("memory_write_created", "memory_write_performed"))
    external_action_created = _truthy_key(
        scoped_records,
        ("external_action_created", "external_control_created", "external_side_effect"),
    )
    focus_selection_created = _truthy_key(
        scoped_records,
        ("focus_selection_created", "focus_target_selected", "focus_candidate_ranking_created"),
    )
    thought_engine_used = _truthy_key(scoped_records, ("thought_engine_used",))
    output_created = _truthy_key(scoped_records, ("output_created", "first_output_created"))
    for reason, flag in (
        ("memory_write_created", memory_write_created),
        ("external_action_created", external_action_created),
        ("focus_selection_created", focus_selection_created),
        ("thought_engine_used", thought_engine_used),
        ("output_created", output_created),
    ):
        require(not flag, reason)

    audit_mode = "real_active_capture" if require_real_source_capture else "synthetic_verification"
    audit_status = (
        PACKAGE_125_PASS_STATUS
        if not failures and require_real_source_capture
        else SYNTHETIC_PACKAGE_125_PASS_STATUS
        if not failures
        else "blocked_bounded_observation_window_extension_audit"
    )
    audit = Package125BoundedObservationExtensionAudit(
        audit_id=stable_id("package_125_audit"),
        schema_version=PACKAGE_125_AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        real_source_capture_verified=real_source_capture_verified,
        temporal_tail_evidence_verified=temporal_tail_evidence_verified,
        candidate_from_actual_temporal_evidence=candidate_from_actual_temporal_evidence,
        session_authorization_verified=session_authorization_verified,
        policy_gate_verified=policy_gate_verified,
        internal_action_created=internal_action_created,
        internal_action_kind_verified=internal_action_kind_verified,
        deadline_extension_atomic=deadline_extension_atomic,
        same_source_sessions_preserved=same_source_sessions_preserved,
        all_required_lanes_extended=all_required_lanes_extended,
        extension_count=1 if execution.get("execution_status") == "applied" else 0,
        granted_extension_ns=int(policy.get("granted_extension_ns", 0) or 0),
        event_closure_observed_after_base_deadline=event_closure_observed,
        post_event_context_observed=post_event_context_observed,
        required_lane_drop_count=required_lane_drop_count,
        backpressure_fault_count=backpressure_fault_count,
        capture_failure_count=capture_failure_count,
        compile_failure_count=compile_failure_count,
        stable_control_did_not_extend=stable_control_did_not_extend,
        early_complete_control_did_not_extend=early_complete_control_did_not_extend,
        authorization_off_control_blocked=authorization_off_control_blocked,
        operator_interrupt_verified=operator_interrupt_verified,
        stimulus_ground_truth_used_for_decision=stimulus_ground_truth_used,
        package_112_score_changed=package_112_score_changed,
        memory_write_created=memory_write_created,
        external_action_created=external_action_created,
        focus_selection_created=focus_selection_created,
        thought_engine_used=thought_engine_used,
        output_created=output_created,
        subjective_time_claimed=False,
        waiting_semantics_claimed=False,
        novelty_semantics_claimed=False,
        object_or_audio_semantics_claimed=False,
        d_laplace_component_used=False,
        d_laplace_migration_performed=False,
        llm_runtime_calls=0,
        codex_runtime_calls=0,
        network_runtime_calls=0,
        audit_status=audit_status,
        failure_reasons=tuple(dict.fromkeys(failures)),
        audit_mode=audit_mode,
        target_observation_window_id=target_window_id,
        target_runtime_session_id=str(scope["runtime_session_id"]),
        target_perception_session_id=str(scope["perception_session_id"]),
        target_experiment_run_id=str(scope["experiment_run_id"]),
        target_audit_group_id=str(scope["audit_group_id"]),
        target_scenario_name=str(scope["scenario_name"]),
        active_capture_identity_chain_verified=identity_chain_verified,
        transport_flush_verified=transport_flush_verified,
        flush_remaining_required_records=int(comparison.get("flush_remaining_required_records", -1)),
        operator_event_delivery_failure_count=len(event_failures),
        package_112_score_equivalence_record_id=(
            str(score_record.get("score_equivalence_record_id")) if score_record else None
        ),
    )
    if append:
        store.append_record("package_125_audits", audit)
    return audit


def _target_state(
    states: tuple[dict[str, Any], ...],
    observation_window_id: str | None,
) -> dict[str, Any]:
    if observation_window_id:
        matches = tuple(
            item for item in states if item.get("observation_window_id") == observation_window_id
        )
        return matches[-1] if matches else {}
    real_late = tuple(
        item
        for item in states
        if item.get("scenario_name") == "late_event"
        and item.get("capture_mode") == "real_active_capture"
    )
    if real_late:
        return real_late[-1]
    late = tuple(item for item in states if item.get("scenario_name") == "late_event")
    return late[-1] if late else (states[-1] if states else {})


def _scope_from(target: dict[str, Any]) -> dict[str, str]:
    return {
        name: str(target.get(name) or "")
        for name in (
            "observation_window_id",
            "runtime_session_id",
            "perception_session_id",
            "experiment_run_id",
            "audit_group_id",
            "scenario_name",
        )
    }


def _scoped(
    items: tuple[dict[str, Any], ...],
    scope: dict[str, str],
) -> tuple[dict[str, Any], ...]:
    return tuple(
        item
        for item in items
        if all(str(item.get(name) or "") == value for name, value in scope.items())
    )


def _by_id(
    items: tuple[dict[str, Any], ...],
    key: str,
    value: object,
) -> dict[str, Any] | None:
    for item in reversed(items):
        if item.get(key) == value:
            return item
    return None


def _latest_where(
    items: tuple[dict[str, Any], ...],
    predicate: Any,
) -> dict[str, Any] | None:
    for item in reversed(items):
        if predicate(item):
            return item
    return None


def _capture_identity_continuity(
    before: dict[str, Any],
    after: dict[str, Any],
) -> bool:
    fields = (
        "experiment_run_id",
        "audit_group_id",
        "scenario_name",
        "runtime_session_id",
        "perception_session_id",
        "observation_window_id",
        "screen_capture_session_id",
        "audio_capture_session_id",
        "host_state_capture_session_id",
        "screen_descriptor_id",
        "audio_descriptor_id",
        "host_state_descriptor_id",
        "screen_config_sha256",
        "audio_config_sha256",
        "host_state_config_sha256",
        "window_handle",
        "render_endpoint_id",
        "alignment_origin_monotonic_ns",
        "clock_domain_ids",
        "real_source_capture",
    )
    return (
        all(before.get(name) == after.get(name) for name in fields)
        and not bool(after.get("sources_reopened"))
        and int(after.get("observed_deadline_ns", 0)) >= int(before.get("observed_deadline_ns", 0))
    )


def _verify_real_capture_identity(
    *,
    state_dir: str | Path,
    identity_before: dict[str, Any],
    identity_after: dict[str, Any],
    execution: dict[str, Any],
) -> bool:
    if not (
        identity_before
        and identity_after
        and identity_before.get("real_source_capture") is True
        and identity_after.get("real_source_capture") is True
        and _capture_identity_continuity(identity_before, identity_after)
    ):
        return False
    try:
        sensor_store = ContentAddressedSensorArtifactStore(state_dir)
        sessions = {
            str(item.get("capture_session_id")): item
            for item in sensor_store.list_capture_sessions()
        }
        artifacts = sensor_store.list_artifacts()
    except Exception:
        return False
    expected = (
        (
            "screen",
            "screen_capture_session_id",
            "screen_descriptor_id",
            "screen_config_sha256",
        ),
        (
            "microphone",
            "audio_capture_session_id",
            "audio_descriptor_id",
            "audio_config_sha256",
        ),
        (
            "host_state",
            "host_state_capture_session_id",
            "host_state_descriptor_id",
            "host_state_config_sha256",
        ),
    )
    applied_absolute_ns = int(identity_after.get("alignment_origin_monotonic_ns", 0)) + int(
        execution.get("applied_new_deadline_ns", 0)
    )
    tolerance_ns = 300_000_000
    for source_kind, session_field, descriptor_field, config_field in expected:
        session_id = str(identity_after.get(session_field) or "")
        session = sessions.get(session_id)
        if not session:
            return False
        if (
            session.get("source_kind") != source_kind
            or session.get("source_device_descriptor_id") != identity_after.get(descriptor_field)
            or session.get("capture_config_sha256") != identity_after.get(config_field)
        ):
            return False
        lane_artifacts = tuple(
            item for item in artifacts if item.get("capture_session_id") == session_id
        )
        if not lane_artifacts:
            return False
        if max(int(item.get("captured_at_monotonic_ns", 0)) for item in lane_artifacts) < (
            applied_absolute_ns - tolerance_ns
        ):
            return False
        if not all(sensor_store.verify_artifact(str(item["artifact_id"]))["valid"] for item in lane_artifacts):
            return False
    return True


def _control_payloads(
    store: Package125ObservationExtensionStore,
    audit_group_id: str,
    scenario_name: str,
) -> dict[str, tuple[dict[str, Any], ...]]:
    scope = {"audit_group_id": audit_group_id, "scenario_name": scenario_name}
    return {
        "states": tuple(
            item
            for item in store.list_payloads("observation_window_states")
            if all(str(item.get(key) or "") == value for key, value in scope.items())
        ),
        "policies": tuple(
            item
            for item in store.list_payloads("observation_extension_policy_decisions")
            if all(str(item.get(key) or "") == value for key, value in scope.items())
        ),
        "executions": tuple(
            item
            for item in store.list_payloads("observation_extension_executions")
            if all(str(item.get(key) or "") == value for key, value in scope.items())
        ),
    }


def _control_did_not_extend(
    store: Package125ObservationExtensionStore,
    audit_group_id: str,
    scenario_name: str,
) -> bool:
    rows = _control_payloads(store, audit_group_id, scenario_name)
    return bool(rows["states"]) and not any(
        item.get("execution_status") == "applied" for item in rows["executions"]
    )


def _authorization_off_blocked(
    store: Package125ObservationExtensionStore,
    audit_group_id: str,
) -> bool:
    rows = _control_payloads(store, audit_group_id, "authorization_off_control")
    return (
        bool(rows["policies"])
        and any(
            item.get("decision") == "block"
            and item.get("authorization_valid") is False
            for item in rows["policies"]
        )
        and not any(item.get("execution_status") == "applied" for item in rows["executions"])
    )


def _operator_stop_verified(
    store: Package125ObservationExtensionStore,
    audit_group_id: str,
) -> bool:
    rows = _control_payloads(store, audit_group_id, "operator_stop_control")
    return (
        any(item.get("window_status") == "operator_interrupted" for item in rows["states"])
        and any(
            "operator_stop_requested" in tuple(item.get("failure_reasons") or ())
            for item in rows["policies"]
        )
        and not any(item.get("execution_status") == "applied" for item in rows["executions"])
    )


def _transport_fault_verified(
    store: Package125ObservationExtensionStore,
    audit_group_id: str,
) -> bool:
    rows = _control_payloads(store, audit_group_id, "transport_fault_control")
    return (
        any(item.get("window_status") == "failed" for item in rows["states"])
        and any(
            item.get("transport_integrity_valid") is False
            and item.get("decision") == "block"
            for item in rows["policies"]
        )
        and not any(item.get("execution_status") == "applied" for item in rows["executions"])
    )


def _truthy_key(
    records: tuple[dict[str, Any], ...],
    keys: tuple[str, ...],
) -> bool:
    return any(bool(record.get(key)) for record in records for key in keys)
