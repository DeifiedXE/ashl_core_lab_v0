"""Actual negative controls for Package 136."""

from __future__ import annotations

from dataclasses import fields, replace
from pathlib import Path
from typing import Any, Callable, TypeVar

from ashl_core_v1.endocrine.drive_modulation_runtime import (
    apply_audit_only_modulation,
    build_neutralization,
    decide_drive_modulation,
    derive_bounded_modulation,
)
from ashl_core_v1.endocrine.drive_modulation_types import (
    AUDIT_ONLY_CONSUMER_ID,
    AUTHORIZATION_SCHEMA_VERSION,
    CONTROL_NAMES,
    CONTROL_SCHEMA_VERSION,
    DriveModulationApplicationRecord,
    DriveModulationConsumerAllowlistRecord,
    DriveModulationCrossSessionNeutralityRecord,
    Package136ControlResult,
    SameSessionDriveModulationAuthorization,
    SameSessionDriveModulationContract,
)
from ashl_core_v1.endocrine.package_136_drive_modulation_store import (
    Package136DriveModulationStore,
)
from ashl_core_v1.endocrine.package_136_package_135_source import (
    load_package_136_sources_read_only,
)
from ashl_core_v1.runtime.host_sensor_types import sha256_payload, utc_now


T = TypeVar("T")


def run_package_136_drive_modulation_controls(
    *,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_135_state_dir: str | Path,
    state_dir: str | Path,
    append: bool = True,
) -> Package136ControlResult:
    source = load_package_136_sources_read_only(
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_135_state_dir=package_135_state_dir,
    )
    store = Package136DriveModulationStore(state_dir)
    contract = _record_from_payload(
        SameSessionDriveModulationContract,
        _require_one(store.list_payloads("same_session_drive_modulation_contracts"), "contract"),
    )
    allowlist = _record_from_payload(
        DriveModulationConsumerAllowlistRecord,
        _require_one(store.list_payloads("drive_modulation_consumer_allowlists"), "allowlist"),
    )
    authorization = _record_from_payload(
        SameSessionDriveModulationAuthorization,
        _require_one(store.list_payloads("same_session_drive_modulation_authorizations"), "authorization"),
    )
    application = _record_from_payload(
        DriveModulationApplicationRecord,
        _require_one(store.list_payloads("drive_modulation_applications"), "application"),
    )
    neutrality = _record_from_payload(
        DriveModulationCrossSessionNeutralityRecord,
        _require_one(store.list_payloads("drive_modulation_cross_session_neutrality"), "cross_session_neutrality"),
    )
    selected = source.selected_trace
    fresh_root = source.fresh_session_root_trace
    passed: list[str] = []

    def check(name: str, callback: Callable[[], bool]) -> None:
        try:
            if callback():
                passed.append(name)
        except (TypeError, ValueError, RuntimeError):
            return

    check(
        "production_allowlist_nonempty_rejected",
        lambda: _raises(
            ValueError,
            lambda: replace(
                allowlist,
                production_consumer_ids=("forbidden_production_consumer",),
                production_allowlist_empty=False,
            ),
        ),
    )
    check(
        "authorization_missing_fails_neutral",
        lambda: _decision_is(
            contract,
            allowlist,
            None,
            selected,
            selected.runtime_session_id,
            AUDIT_ONLY_CONSUMER_ID,
            authorization.authorized_at_monotonic_ns + 1,
            "neutral_authorization_missing",
        ),
    )
    corrupted = selected.to_dict()
    corrupted["normalized_level"] = 0.9
    check(
        "invalid_trace_hash_fails_neutral",
        lambda: _decision_is(
            contract,
            allowlist,
            authorization,
            corrupted,
            selected.runtime_session_id,
            AUDIT_ONLY_CONSUMER_ID,
            authorization.authorized_at_monotonic_ns + 1,
            "neutral_signal_invalid",
        ),
    )
    check(
        "unauthorized_consumer_fails_neutral",
        lambda: _decision_is(
            contract,
            allowlist,
            authorization,
            selected,
            selected.runtime_session_id,
            "bounded_capture_deadline",
            authorization.authorized_at_monotonic_ns + 1,
            "neutral_consumer_not_allowlisted",
        ),
    )
    check(
        "wrong_session_fails_neutral",
        lambda: _decision_is(
            contract,
            allowlist,
            authorization,
            selected,
            "package_136_wrong_session",
            AUDIT_ONLY_CONSUMER_ID,
            authorization.authorized_at_monotonic_ns + 1,
            "neutral_session_mismatch",
        ),
    )
    wrong_lineage_authorization = _authorization_for_trace(
        authorization,
        selected,
        signal_lineage_id="drive_signal_lineage:wrong_lineage_control",
    )
    check(
        "wrong_lineage_fails_neutral",
        lambda: _decision_is(
            contract,
            allowlist,
            wrong_lineage_authorization,
            selected,
            selected.runtime_session_id,
            AUDIT_ONLY_CONSUMER_ID,
            authorization.authorized_at_monotonic_ns + 1,
            "neutral_lineage_mismatch",
        ),
    )
    check(
        "expired_authorization_fails_neutral",
        lambda: _decision_is(
            contract,
            allowlist,
            authorization,
            selected,
            selected.runtime_session_id,
            AUDIT_ONLY_CONSUMER_ID,
            authorization.expires_at_monotonic_ns,
            "neutral_authorization_expired",
        ),
    )
    check(
        "duplicate_authorization_use_fails_neutral",
        lambda: _decision_is(
            contract,
            allowlist,
            authorization,
            selected,
            selected.runtime_session_id,
            AUDIT_ONLY_CONSUMER_ID,
            authorization.authorized_at_monotonic_ns + 1,
            "neutral_authorization_already_consumed",
            prior_use_count=1,
        ),
    )
    root_authorization = _authorization_for_trace(authorization, fresh_root)
    root_decision, root_trace = decide_drive_modulation(
        contract=contract,
        allowlist=allowlist,
        authorization=root_authorization,
        signal_trace_payload=fresh_root,
        runtime_session_id=fresh_root.runtime_session_id,
        consumer_id=AUDIT_ONLY_CONSUMER_ID,
        evaluated_at_monotonic_ns=root_authorization.authorized_at_monotonic_ns + 1,
    )
    root_derivation = derive_bounded_modulation(
        decision=root_decision,
        authorization=root_authorization,
        trace=root_trace,
    )
    check(
        "absolute_level_clamp_enforced",
        lambda: root_derivation.absolute_clamp_applied
        and abs(root_derivation.absolute_clamped_offset) == root_authorization.maximum_absolute_offset,
    )
    selected_decision, selected_trace = decide_drive_modulation(
        contract=contract,
        allowlist=allowlist,
        authorization=authorization,
        signal_trace_payload=selected,
        runtime_session_id=selected.runtime_session_id,
        consumer_id=AUDIT_ONLY_CONSUMER_ID,
        evaluated_at_monotonic_ns=authorization.authorized_at_monotonic_ns + 1,
    )
    selected_derivation = derive_bounded_modulation(
        decision=selected_decision,
        authorization=authorization,
        trace=selected_trace,
    )
    check(
        "delta_clamp_enforced",
        lambda: selected_derivation.delta_clamp_applied
        and abs(selected_derivation.effective_offset)
        == authorization.maximum_delta_per_application,
    )

    def consumer_fault_control() -> bool:
        try:
            apply_audit_only_modulation(
                derivation=selected_derivation,
                decision=selected_decision,
                authorization=authorization,
                applied_at_monotonic_ns=authorization.authorized_at_monotonic_ns + 2,
                consumer_fault=True,
            )
        except RuntimeError as error:
            neutral = build_neutralization(
                runtime_session_id=selected.runtime_session_id,
                reason="consumer_fault",
                policy_decision_ref=selected_decision.policy_decision_id,
                source_record_refs=(selected_decision.policy_decision_id,),
            )
            return str(error) == "audit_only_consumer_fault" and neutral.neutral_baseline_restored
        return False

    check("consumer_fault_fails_neutral", consumer_fault_control)
    check(
        "session_end_fails_neutral",
        lambda: any(
            item["reason"] == "session_end"
            and item["neutral_baseline_restored"] is True
            and item["final_effective_offset"] == 0.0
            for item in store.list_payloads("drive_modulation_neutralizations")
        ),
    )
    check(
        "cross_session_carry_rejected",
        lambda: _decision_is(
            contract,
            allowlist,
            authorization,
            fresh_root,
            fresh_root.runtime_session_id,
            AUDIT_ONLY_CONSUMER_ID,
            authorization.authorized_at_monotonic_ns + 1,
            "neutral_session_mismatch",
        ),
    )
    check(
        "semantic_identity_injection_rejected",
        lambda: _raises(ValueError, lambda: replace(application, semantic_label="fear")),
    )
    check(
        "purpose_desire_reward_emotion_injection_rejected",
        lambda: all(
            _raises(ValueError, callback)
            for callback in (
                lambda: replace(application, purpose_ref="new-purpose"),
                lambda: replace(application, desire_label="want"),
                lambda: replace(application, reward_label="reward"),
                lambda: replace(application, emotion_label="happy"),
            )
        ),
    )
    check(
        "candidate_action_memory_state_output_authority_rejected",
        lambda: all(
            _raises(ValueError, callback)
            for callback in (
                lambda: replace(application, candidate_ordering_authority=True),
                lambda: replace(application, selected_action_authority=True),
                lambda: replace(application, memory_write_authority=True),
                lambda: replace(application, self_state_write_authority=True),
                lambda: replace(application, output_authority=True),
            )
        ),
    )
    check(
        "package_135_trace_mutation_rejected",
        lambda: _raises(
            ValueError,
            lambda: replace(selected, normalized_level=0.9),
        ),
    )
    check(
        "package_134_recovery_modulation_rejected",
        lambda: (
            not neutrality.package_134_drive_state_restored
            and _raises(
                ValueError,
                lambda: replace(neutrality, authorization_carried=True),
            )
        ),
    )
    result = Package136ControlResult(
        control_result_id=f"package_136_controls:{sha256_payload({'passed': tuple(passed)})[:16]}",
        schema_version=CONTROL_SCHEMA_VERSION,
        created_at=utc_now(),
        control_names=CONTROL_NAMES,
        passed_control_names=tuple(passed),
        expected_count=len(CONTROL_NAMES),
        passed_count=len(passed),
        controls_passed=tuple(passed) == CONTROL_NAMES,
        source_record_refs=(
            contract.contract_id,
            allowlist.allowlist_id,
            authorization.authorization_id,
            source.source_binding.source_binding_id,
            application.application_id,
            neutrality.neutrality_record_id,
        ),
    )
    if append:
        store.append_once("package_136_control_results", result)
    return result


def _decision_is(
    contract: SameSessionDriveModulationContract,
    allowlist: DriveModulationConsumerAllowlistRecord,
    authorization: SameSessionDriveModulationAuthorization | None,
    trace: Any,
    runtime_session_id: str,
    consumer_id: str,
    evaluated_at: int,
    expected: str,
    *,
    prior_use_count: int = 0,
) -> bool:
    decision, _ = decide_drive_modulation(
        contract=contract,
        allowlist=allowlist,
        authorization=authorization,
        signal_trace_payload=trace,
        runtime_session_id=runtime_session_id,
        consumer_id=consumer_id,
        evaluated_at_monotonic_ns=evaluated_at,
        prior_authorization_use_count=prior_use_count,
    )
    neutral = build_neutralization(
        runtime_session_id=runtime_session_id,
        reason=decision.failure_reasons[0],
        policy_decision_ref=decision.policy_decision_id,
        source_record_refs=(decision.policy_decision_id,),
    )
    return (
        decision.decision == expected
        and decision.fail_to_neutral
        and neutral.neutral_baseline_restored
        and neutral.final_effective_offset == 0.0
    )


def _authorization_for_trace(
    authorization: SameSessionDriveModulationAuthorization,
    trace: Any,
    *,
    signal_lineage_id: str | None = None,
) -> SameSessionDriveModulationAuthorization:
    payload = authorization.to_dict()
    payload.update(
        {
            "authorization_id": "",
            "authorization_sha256": "",
            "schema_version": AUTHORIZATION_SCHEMA_VERSION,
            "runtime_session_id": trace.runtime_session_id,
            "signal_lineage_id": signal_lineage_id or trace.signal_lineage_id,
            "signal_trace_id": trace.signal_trace_id,
            "signal_trace_sha256": trace.signal_trace_sha256,
            "source_record_refs": tuple(payload["source_record_refs"]),
        }
    )
    identity = dict(payload)
    identity.pop("authorization_id")
    identity.pop("authorization_sha256")
    identity.pop("created_at")
    digest = sha256_payload(identity)
    payload["authorization_id"] = f"same_session_drive_modulation_authorization:{digest[:16]}"
    payload["authorization_sha256"] = digest
    return SameSessionDriveModulationAuthorization(**payload)


def _record_from_payload(record_type: type[T], payload: dict[str, Any]) -> T:
    values = dict(payload)
    for item in fields(record_type):
        if "tuple" in str(item.type).lower() and isinstance(values.get(item.name), list):
            values[item.name] = tuple(values[item.name])
    return record_type(**values)


def _require_one(payloads: tuple[dict[str, Any], ...], label: str) -> dict[str, Any]:
    if len(payloads) != 1:
        raise RuntimeError(f"blocked_package_136_{label}_cardinality:{len(payloads)}")
    return payloads[0]


def _raises(expected: type[BaseException], callback: Callable[[], Any]) -> bool:
    try:
        callback()
    except expected:
        return True
    return False
