"""Package 136 bounded modulation policy and counterfactual runtime."""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from dataclasses import fields
from pathlib import Path
from typing import Any, TypeVar

from ashl_core_v1.endocrine.drive_modulation_consumer_inventory import (
    build_drive_modulation_consumer_inventory,
    consumer_inventory_sha256,
)
from ashl_core_v1.endocrine.drive_modulation_types import (
    ALLOWLIST_SCHEMA_VERSION,
    APPLICATION_SCHEMA_VERSION,
    AUDIT_ONLY_CONSUMER_ID,
    AUTHORIZATION_SCHEMA_VERSION,
    BASELINE_COMMIT,
    COMPARISON_SCHEMA_VERSION,
    CONTRACT_SCHEMA_VERSION,
    CROSS_SESSION_SCHEMA_VERSION,
    DECISION_SCHEMA_VERSION,
    DERIVATION_SCHEMA_VERSION,
    MAXIMUM_ABSOLUTE_OFFSET,
    MAXIMUM_AUTHORIZATION_LIFETIME_NS,
    MAXIMUM_DELTA_PER_APPLICATION,
    MODULATION_AUTHORITY,
    NEUTRALIZATION_SCHEMA_VERSION,
    NEUTRAL_OFFSET,
    PROCESS_SCHEMA_VERSION,
    SIGNAL_AUTHORITY,
    SNAPSHOT_SCHEMA_VERSION,
    DriveModulationApplicationRecord,
    DriveModulationBoundarySnapshot,
    DriveModulationConsumerAllowlistRecord,
    DriveModulationCounterfactualComparison,
    DriveModulationCrossSessionNeutralityRecord,
    DriveModulationDerivationRecord,
    DriveModulationNeutralizationRecord,
    DriveModulationPolicyDecision,
    DriveModulationProcessReceipt,
    SameSessionDriveModulationAuthorization,
    SameSessionDriveModulationContract,
)
from ashl_core_v1.endocrine.drive_signal_trace_types import (
    DriveRegulatorySignalTraceRecord,
)
from ashl_core_v1.endocrine.package_135_authority_source import source_tree_sha256
from ashl_core_v1.endocrine.package_136_drive_modulation_store import (
    Package136DriveModulationStore,
)
from ashl_core_v1.endocrine.package_136_package_135_source import (
    Package136SourceBundle,
    load_package_136_sources_read_only,
)
from ashl_core_v1.runtime.host_sensor_types import (
    monotonic_ns,
    sha256_bytes,
    sha256_payload,
    stable_id,
    utc_now,
)


T = TypeVar("T")


def preflight_same_session_drive_modulation(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_135_state_dir: str | Path,
    state_dir: str | Path,
) -> dict[str, Any]:
    root, output, source_133, source_134, source_135 = _validate_external_roots(
        ashl_root,
        state_dir,
        package_133_state_dir,
        package_134_state_dir,
        package_135_state_dir,
    )
    source = load_package_136_sources_read_only(
        package_133_state_dir=source_133,
        package_134_state_dir=source_134,
        package_135_state_dir=source_135,
    )
    inventory = build_drive_modulation_consumer_inventory(root)
    return {
        "source_head": _git_output(root, "rev-parse", "HEAD"),
        "baseline_commit": BASELINE_COMMIT,
        "baseline_is_ancestor": _is_ancestor(root, BASELINE_COMMIT),
        "package_135_audit_id": source.package_135_audit["audit_id"],
        "package_135_audit_status": source.package_135_audit["audit_status"],
        "package_135_contract_id": source.package_135_contract.contract_id,
        "selected_signal_trace_id": source.selected_trace.signal_trace_id,
        "selected_signal_session_id": source.selected_trace.runtime_session_id,
        "fresh_session_root_trace_id": source.fresh_session_root_trace.signal_trace_id,
        "consumer_inventory_count": len(inventory),
        "consumer_inventory_sha256": consumer_inventory_sha256(inventory),
        "production_consumer_count": sum(item.production_eligible for item in inventory),
        "audit_only_consumer_id": AUDIT_ONLY_CONSUMER_ID,
        "state_dir_is_external": not _is_within(output, root),
        "readiness": "ready_for_same_session_modulation_infrastructure_with_empty_production_allowlist",
    }


def build_same_session_modulation_contract(
    *, source: Package136SourceBundle
) -> SameSessionDriveModulationContract:
    payload: dict[str, Any] = {
        "contract_id": "",
        "contract_sha256": "",
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "baseline_commit": BASELINE_COMMIT,
        "modulation_authority": MODULATION_AUTHORITY,
        "signal_authority": SIGNAL_AUTHORITY,
        "same_session_only": True,
        "read_only_signal_consumption": True,
        "neutral_offset": NEUTRAL_OFFSET,
        "maximum_absolute_offset": MAXIMUM_ABSOLUTE_OFFSET,
        "maximum_delta_per_application": MAXIMUM_DELTA_PER_APPLICATION,
        "maximum_authorization_lifetime_ns": MAXIMUM_AUTHORIZATION_LIFETIME_NS,
        "single_application_per_authorization": True,
        "session_expiry_required": True,
        "fail_to_neutral_required": True,
        "production_consumer_count": 0,
        "audit_only_consumer_count": 1,
        "production_runtime_influence_allowed": False,
        "cross_session_carry_allowed": False,
        "semantic_interpretation_allowed": False,
        "purpose_or_preference_allowed": False,
        "contract_status": "ready_with_empty_production_allowlist",
        "source_record_refs": (
            source.source_binding.source_binding_id,
            source.package_135_contract.contract_id,
            str(source.package_135_audit["audit_id"]),
        ),
    }
    return _hashed_record(
        SameSessionDriveModulationContract,
        payload,
        id_field="contract_id",
        hash_field="contract_sha256",
        prefix="same_session_drive_modulation_contract",
    )


def build_drive_modulation_consumer_allowlist(
    *,
    contract: SameSessionDriveModulationContract,
    inventory: tuple[Any, ...],
) -> DriveModulationConsumerAllowlistRecord:
    production = tuple(
        item.consumer_surface_id for item in inventory if item.production_eligible
    )
    audit_only = tuple(
        item.consumer_surface_id for item in inventory if item.audit_only_eligible
    )
    payload: dict[str, Any] = {
        "allowlist_id": "",
        "allowlist_sha256": "",
        "schema_version": ALLOWLIST_SCHEMA_VERSION,
        "created_at": utc_now(),
        "contract_ref": contract.contract_id,
        "production_consumer_ids": production,
        "audit_only_consumer_ids": audit_only,
        "production_allowlist_empty": not production,
        "production_empty_reason": "no_existing_consumer_without_authority_violation",
        "forbidden_consumer_classes": (
            "perception",
            "attention",
            "thought_engine",
            "candidate_ordering",
            "selected_action",
            "memory",
            "self_state",
            "purpose",
            "output",
            "cross_session_recovery",
        ),
        "consumer_read_only_required": True,
        "no_runtime_capability_created": True,
        "allowlist_status": "verified_empty_production_allowlist_with_audit_only_probe",
        "source_record_refs": (
            contract.contract_id,
            *(item.inventory_record_id for item in inventory),
        ),
    }
    return _hashed_record(
        DriveModulationConsumerAllowlistRecord,
        payload,
        id_field="allowlist_id",
        hash_field="allowlist_sha256",
        prefix="drive_modulation_consumer_allowlist",
    )


def build_same_session_modulation_authorization(
    *,
    contract: SameSessionDriveModulationContract,
    allowlist: DriveModulationConsumerAllowlistRecord,
    source: Package136SourceBundle,
    authorized_at_monotonic_ns: int | None = None,
) -> SameSessionDriveModulationAuthorization:
    authorized_at = monotonic_ns() if authorized_at_monotonic_ns is None else int(authorized_at_monotonic_ns)
    trace = source.selected_trace
    payload: dict[str, Any] = {
        "authorization_id": "",
        "authorization_sha256": "",
        "schema_version": AUTHORIZATION_SCHEMA_VERSION,
        "created_at": utc_now(),
        "contract_ref": contract.contract_id,
        "allowlist_ref": allowlist.allowlist_id,
        "source_binding_ref": source.source_binding.source_binding_id,
        "runtime_session_id": trace.runtime_session_id,
        "signal_lineage_id": trace.signal_lineage_id,
        "signal_trace_id": trace.signal_trace_id,
        "signal_trace_sha256": trace.signal_trace_sha256,
        "consumer_id": AUDIT_ONLY_CONSUMER_ID,
        "authorization_source": "explicit_session_configuration",
        "authorized_by": "local_operator",
        "authorized_at_monotonic_ns": authorized_at,
        "expires_at_monotonic_ns": authorized_at + MAXIMUM_AUTHORIZATION_LIFETIME_NS,
        "maximum_absolute_offset": MAXIMUM_ABSOLUTE_OFFSET,
        "maximum_delta_per_application": MAXIMUM_DELTA_PER_APPLICATION,
        "single_application_only": True,
        "same_session_only": True,
        "cross_session_carry_allowed": False,
        "authorization_status": "authorized_for_one_same_session_audit_only_application",
        "source_record_refs": (
            contract.contract_id,
            allowlist.allowlist_id,
            source.source_binding.source_binding_id,
            trace.signal_trace_id,
        ),
    }
    return _hashed_record(
        SameSessionDriveModulationAuthorization,
        payload,
        id_field="authorization_id",
        hash_field="authorization_sha256",
        prefix="same_session_drive_modulation_authorization",
    )


def decide_drive_modulation(
    *,
    contract: SameSessionDriveModulationContract,
    allowlist: DriveModulationConsumerAllowlistRecord,
    authorization: SameSessionDriveModulationAuthorization | None,
    signal_trace_payload: DriveRegulatorySignalTraceRecord | dict[str, Any] | None,
    runtime_session_id: str,
    consumer_id: str,
    evaluated_at_monotonic_ns: int,
    prior_authorization_use_count: int = 0,
) -> tuple[DriveModulationPolicyDecision, DriveRegulatorySignalTraceRecord | None]:
    trace: DriveRegulatorySignalTraceRecord | None
    try:
        trace = (
            signal_trace_payload
            if isinstance(signal_trace_payload, DriveRegulatorySignalTraceRecord)
            else DriveRegulatorySignalTraceRecord.from_dict(dict(signal_trace_payload or {}))
        )
        signal_valid = True
    except (TypeError, ValueError):
        trace = None
        signal_valid = False
    auth_present = authorization is not None
    auth_valid = bool(
        authorization
        and authorization.contract_ref == contract.contract_id
        and authorization.allowlist_ref == allowlist.allowlist_id
        and authorization.single_application_only
        and authorization.same_session_only
        and not authorization.cross_session_carry_allowed
    )
    consumer_allowlisted = consumer_id in allowlist.audit_only_consumer_ids
    session_matches = bool(
        authorization
        and trace
        and authorization.runtime_session_id == runtime_session_id == trace.runtime_session_id
    )
    lineage_matches = bool(
        authorization
        and trace
        and authorization.signal_lineage_id == trace.signal_lineage_id
        and authorization.signal_trace_id == trace.signal_trace_id
        and authorization.signal_trace_sha256 == trace.signal_trace_sha256
    )
    unexpired = bool(
        authorization
        and authorization.authorized_at_monotonic_ns <= evaluated_at_monotonic_ns
        < authorization.expires_at_monotonic_ns
    )
    use_available = prior_authorization_use_count == 0
    if not auth_present:
        decision = "neutral_authorization_missing"
        failures = ("authorization_missing",)
    elif not auth_valid:
        decision = "neutral_authorization_invalid"
        failures = ("authorization_invalid",)
    elif not signal_valid:
        decision = "neutral_signal_invalid"
        failures = ("signal_invalid",)
    elif not consumer_allowlisted:
        decision = "neutral_consumer_not_allowlisted"
        failures = ("consumer_not_allowlisted",)
    elif not session_matches:
        decision = "neutral_session_mismatch"
        failures = ("session_mismatch",)
    elif not lineage_matches:
        decision = "neutral_lineage_mismatch"
        failures = ("lineage_mismatch",)
    elif not unexpired:
        decision = "neutral_authorization_expired"
        failures = ("authorization_expired",)
    elif not use_available:
        decision = "neutral_authorization_already_consumed"
        failures = ("authorization_already_consumed",)
    else:
        decision = "allow_bounded_audit_only_modulation"
        failures = ()
    payload: dict[str, Any] = {
        "policy_decision_id": "",
        "policy_decision_sha256": "",
        "schema_version": DECISION_SCHEMA_VERSION,
        "created_at": utc_now(),
        "contract_ref": contract.contract_id,
        "authorization_ref": authorization.authorization_id if authorization else None,
        "signal_trace_ref": trace.signal_trace_id if trace else None,
        "runtime_session_id": runtime_session_id,
        "consumer_id": consumer_id,
        "evaluated_at_monotonic_ns": int(evaluated_at_monotonic_ns),
        "decision": decision,
        "authorization_present": auth_present,
        "authorization_valid": auth_valid,
        "signal_integrity_valid": signal_valid,
        "consumer_allowlisted": consumer_allowlisted,
        "session_identity_matches": session_matches,
        "lineage_identity_matches": lineage_matches,
        "authorization_unexpired": unexpired,
        "authorization_use_available": use_available,
        "fail_to_neutral": bool(failures),
        "failure_reasons": failures,
        "source_record_refs": tuple(
            item
            for item in (
                contract.contract_id,
                allowlist.allowlist_id,
                authorization.authorization_id if authorization else None,
                trace.signal_trace_id if trace else None,
            )
            if item is not None
        ),
    }
    return (
        _hashed_record(
            DriveModulationPolicyDecision,
            payload,
            id_field="policy_decision_id",
            hash_field="policy_decision_sha256",
            prefix="drive_modulation_policy_decision",
        ),
        trace,
    )


def derive_bounded_modulation(
    *,
    decision: DriveModulationPolicyDecision,
    authorization: SameSessionDriveModulationAuthorization,
    trace: DriveRegulatorySignalTraceRecord,
    previous_effective_offset: float = NEUTRAL_OFFSET,
) -> DriveModulationDerivationRecord:
    if decision.decision != "allow_bounded_audit_only_modulation":
        raise ValueError("Package 136 derivation requires an allowed policy decision")
    raw = trace.normalized_level - 0.5
    absolute = _clamp(raw, -authorization.maximum_absolute_offset, authorization.maximum_absolute_offset)
    raw_delta = absolute - previous_effective_offset
    bounded_delta = _clamp(
        raw_delta,
        -authorization.maximum_delta_per_application,
        authorization.maximum_delta_per_application,
    )
    effective = previous_effective_offset + bounded_delta
    payload: dict[str, Any] = {
        "derivation_id": "",
        "derivation_sha256": "",
        "schema_version": DERIVATION_SCHEMA_VERSION,
        "created_at": utc_now(),
        "policy_decision_ref": decision.policy_decision_id,
        "authorization_ref": authorization.authorization_id,
        "signal_trace_ref": trace.signal_trace_id,
        "signal_trace_sha256": trace.signal_trace_sha256,
        "runtime_session_id": trace.runtime_session_id,
        "signal_lineage_id": trace.signal_lineage_id,
        "source_event_time_ns": trace.event_time_ns,
        "source_processing_time_ns": trace.processing_time_ns,
        "source_normalized_level": trace.normalized_level,
        "source_normalized_delta": trace.normalized_delta,
        "neutral_center": 0.5,
        "raw_level_offset": raw,
        "absolute_clamped_offset": absolute,
        "previous_effective_offset": previous_effective_offset,
        "raw_delta_from_previous_effective": raw_delta,
        "effective_offset": effective,
        "maximum_absolute_offset": authorization.maximum_absolute_offset,
        "maximum_delta_per_application": authorization.maximum_delta_per_application,
        "absolute_clamp_applied": not math.isclose(raw, absolute, abs_tol=1e-12),
        "delta_clamp_applied": not math.isclose(raw_delta, bounded_delta, abs_tol=1e-12),
        "source_trace_read_only": True,
        "source_trace_mutated": False,
        "semantic_label": None,
        "desire_label": None,
        "reward_label": None,
        "emotion_label": None,
        "purpose_ref": None,
        "preference_ref": None,
        "derivation_status": "bounded_offset_derived_from_read_only_trace",
        "source_record_refs": (
            decision.policy_decision_id,
            authorization.authorization_id,
            trace.signal_trace_id,
        ),
    }
    return _hashed_record(
        DriveModulationDerivationRecord,
        payload,
        id_field="derivation_id",
        hash_field="derivation_sha256",
        prefix="drive_modulation_derivation",
    )


def apply_audit_only_modulation(
    *,
    derivation: DriveModulationDerivationRecord,
    decision: DriveModulationPolicyDecision,
    authorization: SameSessionDriveModulationAuthorization,
    applied_at_monotonic_ns: int,
    consumer_fault: bool = False,
) -> DriveModulationApplicationRecord:
    if consumer_fault:
        raise RuntimeError("audit_only_consumer_fault")
    payload: dict[str, Any] = {
        "application_id": "",
        "application_sha256": "",
        "schema_version": APPLICATION_SCHEMA_VERSION,
        "created_at": utc_now(),
        "derivation_ref": derivation.derivation_id,
        "policy_decision_ref": decision.policy_decision_id,
        "authorization_ref": authorization.authorization_id,
        "runtime_session_id": derivation.runtime_session_id,
        "signal_lineage_id": derivation.signal_lineage_id,
        "consumer_id": AUDIT_ONLY_CONSUMER_ID,
        "applied_at_monotonic_ns": int(applied_at_monotonic_ns),
        "expires_at_monotonic_ns": authorization.expires_at_monotonic_ns,
        "neutral_offset": NEUTRAL_OFFSET,
        "effective_offset": derivation.effective_offset,
        "temporary_same_session_context": True,
        "authorization_consumed_once": True,
        "production_consumer": False,
        "audit_only_consumer": True,
        "read_only_consumption": True,
        "semantic_label": None,
        "desire_label": None,
        "reward_label": None,
        "emotion_label": None,
        "purpose_ref": None,
        "preference_ref": None,
        "perception_modulation_authority": False,
        "attention_modulation_authority": False,
        "candidate_ordering_authority": False,
        "thought_engine_authority": False,
        "memory_write_authority": False,
        "self_state_write_authority": False,
        "purpose_authority": False,
        "action_preference_authority": False,
        "selected_action_authority": False,
        "observation_extension_authority": False,
        "focus_change_authority": False,
        "output_authority": False,
        "cross_session_persistence_authority": False,
        "application_status": "audit_only_modulation_active_until_session_end",
        "source_record_refs": (
            derivation.derivation_id,
            decision.policy_decision_id,
            authorization.authorization_id,
        ),
    }
    return _hashed_record(
        DriveModulationApplicationRecord,
        payload,
        id_field="application_id",
        hash_field="application_sha256",
        prefix="drive_modulation_application",
    )


def build_neutralization(
    *,
    runtime_session_id: str,
    reason: str,
    source_record_refs: tuple[str, ...],
    policy_decision_ref: str | None = None,
    prior_application: DriveModulationApplicationRecord | None = None,
) -> DriveModulationNeutralizationRecord:
    payload: dict[str, Any] = {
        "neutralization_id": "",
        "neutralization_sha256": "",
        "schema_version": NEUTRALIZATION_SCHEMA_VERSION,
        "created_at": utc_now(),
        "runtime_session_id": runtime_session_id,
        "consumer_id": AUDIT_ONLY_CONSUMER_ID,
        "reason": reason,
        "policy_decision_ref": policy_decision_ref,
        "prior_application_ref": prior_application.application_id if prior_application else None,
        "prior_effective_offset": prior_application.effective_offset if prior_application else NEUTRAL_OFFSET,
        "final_effective_offset": NEUTRAL_OFFSET,
        "neutral_baseline_restored": True,
        "authorization_carried_from_prior_session": False,
        "trace_carried_from_prior_session": False,
        "source_modulation_loaded_from_prior_session": False,
        "production_runtime_influence_created": False,
        "neutralization_status": "failed_or_expired_to_neutral",
        "source_record_refs": source_record_refs,
    }
    return _hashed_record(
        DriveModulationNeutralizationRecord,
        payload,
        id_field="neutralization_id",
        hash_field="neutralization_sha256",
        prefix="drive_modulation_neutralization",
    )


def build_authority_invariant_payload(
    *,
    ashl_root: str | Path,
    source: Package136SourceBundle,
) -> dict[str, Any]:
    root = Path(ashl_root).resolve()
    hard_safety = _source_set_sha256(
        root,
        (
            "ashl_core_v1/runtime/no_codex_runtime_guard.py",
            "ashl_core_v1/runtime/perception_attention_closure_types.py",
        ),
    )
    teacher = _source_set_sha256(
        root,
        (
            "ashl_core_v1/runtime/teacher_gated_session_resume_commit.py",
            "ashl_core_v1/task/teacher_gated_selected_action_application.py",
        ),
    )
    purpose = sha256_payload(
        {
            "source": _source_set_sha256(
                root, ("ashl_core_v1/runtime/open_cradle_event_loop_design_gate.py",)
            ),
            "package_136_access": "none",
            "scope_expansion": False,
        }
    )
    candidate = sha256_payload(
        {
            "source": _source_set_sha256(
                root,
                ("ashl_core_v1/task/advisory_readback_candidate_ordering_application.py",),
            ),
            "candidate_set": (),
            "package_136_access": "none",
        }
    )
    selected_action = sha256_payload(
        {
            "source": _source_set_sha256(
                root,
                ("ashl_core_v1/task/teacher_gated_selected_action_application.py",),
            ),
            "selected_action": None,
            "package_136_access": "none",
        }
    )
    memory = _tree_python_sha256(root / "ashl_core_v1" / "memory")
    perception = sha256_payload(
        {
            "perception_tree": _tree_python_sha256(root / "ashl_core_v1" / "perception"),
            "closure": _source_set_sha256(
                root, ("ashl_core_v1/runtime/perception_attention_closure_types.py",)
            ),
            "history_loaded": False,
        }
    )
    output = _source_set_sha256(
        root,
        (
            "ashl_core_v1/runtime/raw_output_token_registry.py",
            "ashl_core_v1/runtime/operator_console_types.py",
        ),
    )
    payload = {
        "hard_safety_sha256": hard_safety,
        "teacher_authority_sha256": teacher,
        "purpose_scope_sha256": purpose,
        "candidate_set_sha256": candidate,
        "selected_action_sha256": selected_action,
        "memory_authority_sha256": memory,
        "perception_history_authority_sha256": perception,
        "self_state_sha256": source.package_133_134.package_133_tree_sha256,
        "output_authority_sha256": output,
        "recovery_result_sha256": source.package_133_134.package_134_tree_sha256,
    }
    payload["invariant_payload_sha256"] = sha256_payload(payload)
    return payload


def build_boundary_snapshot(
    *,
    branch_kind: str,
    runtime_session_id: str,
    offset: float,
    invariants: dict[str, Any],
    source_record_refs: tuple[str, ...],
) -> DriveModulationBoundarySnapshot:
    payload: dict[str, Any] = {
        "snapshot_id": "",
        "snapshot_sha256": "",
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "branch_kind": branch_kind,
        "runtime_session_id": runtime_session_id,
        "consumer_id": AUDIT_ONLY_CONSUMER_ID,
        "audit_only_regulatory_offset": offset,
        **invariants,
        "candidate_count": 0,
        "selected_action_ref": None,
        "output_ref": None,
        "memory_write_created": False,
        "self_state_write_created": False,
        "perception_history_changed": False,
        "production_behavior_changed": False,
        "source_record_refs": source_record_refs,
    }
    return _hashed_record(
        DriveModulationBoundarySnapshot,
        payload,
        id_field="snapshot_id",
        hash_field="snapshot_sha256",
        prefix="drive_modulation_boundary_snapshot",
    )


def compare_counterfactual_snapshots(
    *,
    neutral: DriveModulationBoundarySnapshot,
    modulated: DriveModulationBoundarySnapshot,
) -> DriveModulationCounterfactualComparison:
    invariant_names = (
        "invariant_payload_sha256",
        "hard_safety_sha256",
        "teacher_authority_sha256",
        "purpose_scope_sha256",
        "candidate_set_sha256",
        "selected_action_sha256",
        "memory_authority_sha256",
        "perception_history_authority_sha256",
        "self_state_sha256",
        "output_authority_sha256",
        "recovery_result_sha256",
    )
    equal = {name: getattr(neutral, name) == getattr(modulated, name) for name in invariant_names}
    payload: dict[str, Any] = {
        "comparison_id": "",
        "comparison_sha256": "",
        "schema_version": COMPARISON_SCHEMA_VERSION,
        "created_at": utc_now(),
        "neutral_snapshot_ref": neutral.snapshot_id,
        "modulated_snapshot_ref": modulated.snapshot_id,
        "invariant_payload_equal": equal["invariant_payload_sha256"],
        "modulation_surface_different": not math.isclose(
            neutral.audit_only_regulatory_offset,
            modulated.audit_only_regulatory_offset,
            abs_tol=1e-12,
        ),
        "differing_paths": ("audit_only_regulatory_offset",),
        "hard_safety_equivalent": equal["hard_safety_sha256"],
        "teacher_authority_equivalent": equal["teacher_authority_sha256"],
        "purpose_scope_equivalent": equal["purpose_scope_sha256"],
        "candidate_set_equivalent": equal["candidate_set_sha256"],
        "selected_action_equivalent": equal["selected_action_sha256"],
        "memory_equivalent": equal["memory_authority_sha256"],
        "perception_history_equivalent": equal["perception_history_authority_sha256"],
        "self_state_equivalent": equal["self_state_sha256"],
        "output_equivalent": equal["output_authority_sha256"],
        "recovery_result_equivalent": equal["recovery_result_sha256"],
        "production_behavior_equivalent": (
            not neutral.production_behavior_changed
            and not modulated.production_behavior_changed
        ),
        "comparison_status": "passed_isolated_audit_only_modulation_counterfactual",
        "source_record_refs": (neutral.snapshot_id, modulated.snapshot_id),
    }
    return _hashed_record(
        DriveModulationCounterfactualComparison,
        payload,
        id_field="comparison_id",
        hash_field="comparison_sha256",
        prefix="drive_modulation_counterfactual_comparison",
    )


def run_drive_modulation_worker(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_135_state_dir: str | Path,
    state_dir: str | Path,
    process_role: str,
    process_instance_id: str,
    authorization_id: str | None,
) -> dict[str, Any]:
    started = monotonic_ns()
    pid = os.getpid()
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
    if process_role == "modulated_session_a":
        if not authorization_id:
            raise RuntimeError("blocked_package_136_worker_authorization_missing")
        authorization = _record_from_payload(
            SameSessionDriveModulationAuthorization,
            store.get_payload("same_session_drive_modulation_authorizations", authorization_id),
        )
        trace = source.selected_trace
        decision, validated_trace = decide_drive_modulation(
            contract=contract,
            allowlist=allowlist,
            authorization=authorization,
            signal_trace_payload=trace,
            runtime_session_id=trace.runtime_session_id,
            consumer_id=AUDIT_ONLY_CONSUMER_ID,
            evaluated_at_monotonic_ns=monotonic_ns(),
            prior_authorization_use_count=0,
        )
        if validated_trace is None:
            raise RuntimeError("blocked_package_136_worker_signal_invalid")
        derivation = derive_bounded_modulation(
            decision=decision,
            authorization=authorization,
            trace=validated_trace,
        )
        application = apply_audit_only_modulation(
            derivation=derivation,
            decision=decision,
            authorization=authorization,
            applied_at_monotonic_ns=monotonic_ns(),
        )
        invariants = build_authority_invariant_payload(ashl_root=ashl_root, source=source)
        neutral_snapshot = build_boundary_snapshot(
            branch_kind="neutral",
            runtime_session_id=trace.runtime_session_id,
            offset=NEUTRAL_OFFSET,
            invariants=invariants,
            source_record_refs=(contract.contract_id, trace.signal_trace_id),
        )
        modulated_snapshot = build_boundary_snapshot(
            branch_kind="bounded_modulated",
            runtime_session_id=trace.runtime_session_id,
            offset=application.effective_offset,
            invariants=invariants,
            source_record_refs=(application.application_id, trace.signal_trace_id),
        )
        comparison = compare_counterfactual_snapshots(
            neutral=neutral_snapshot,
            modulated=modulated_snapshot,
        )
        neutralization = build_neutralization(
            runtime_session_id=trace.runtime_session_id,
            reason="session_end",
            policy_decision_ref=decision.policy_decision_id,
            prior_application=application,
            source_record_refs=(
                application.application_id,
                comparison.comparison_id,
                trace.signal_trace_id,
            ),
        )
        ended = max(monotonic_ns(), started + 1)
        receipt = _build_process_receipt(
            process_role=process_role,
            process_instance_id=process_instance_id,
            pid=pid,
            runtime_session_id=trace.runtime_session_id,
            started=started,
            ended=ended,
            source_trace_ref=trace.signal_trace_id,
            authorization_loaded=True,
            application_ref=application.application_id,
            neutralization_ref=neutralization.neutralization_id,
            comparison_ref=comparison.comparison_id,
        )
        store.append_group(
            (
                ("drive_modulation_policy_decisions", decision),
                ("drive_modulation_derivations", derivation),
                ("drive_modulation_applications", application),
                ("drive_modulation_boundary_snapshots", neutral_snapshot),
                ("drive_modulation_boundary_snapshots", modulated_snapshot),
                ("drive_modulation_counterfactual_comparisons", comparison),
                ("drive_modulation_neutralizations", neutralization),
                ("drive_modulation_process_receipts", receipt),
            )
        )
    elif process_role == "neutral_session_b":
        trace = source.fresh_session_root_trace
        decision, _ = decide_drive_modulation(
            contract=contract,
            allowlist=allowlist,
            authorization=None,
            signal_trace_payload=trace,
            runtime_session_id=trace.runtime_session_id,
            consumer_id=AUDIT_ONLY_CONSUMER_ID,
            evaluated_at_monotonic_ns=monotonic_ns(),
            prior_authorization_use_count=0,
        )
        neutralization = build_neutralization(
            runtime_session_id=trace.runtime_session_id,
            reason="fresh_session_start_after_structural_recovery",
            policy_decision_ref=decision.policy_decision_id,
            source_record_refs=(
                decision.policy_decision_id,
                trace.signal_trace_id,
                source.package_133_134.active_head.active_head_id,
            ),
        )
        ended = max(monotonic_ns(), started + 1)
        receipt = _build_process_receipt(
            process_role=process_role,
            process_instance_id=process_instance_id,
            pid=pid,
            runtime_session_id=trace.runtime_session_id,
            started=started,
            ended=ended,
            source_trace_ref=trace.signal_trace_id,
            authorization_loaded=False,
            application_ref=None,
            neutralization_ref=neutralization.neutralization_id,
            comparison_ref=None,
        )
        store.append_group(
            (
                ("drive_modulation_policy_decisions", decision),
                ("drive_modulation_neutralizations", neutralization),
                ("drive_modulation_process_receipts", receipt),
            )
        )
    else:
        raise ValueError("unknown Package 136 worker role")
    return receipt.to_dict()


def run_real_same_session_drive_modulation(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_135_state_dir: str | Path,
    state_dir: str | Path,
    allow_same_session_drive_modulation: bool,
) -> dict[str, Any]:
    if not allow_same_session_drive_modulation:
        raise RuntimeError("blocked_same_session_drive_modulation_authorization_missing")
    root, output, source_133, source_134, source_135 = _validate_external_roots(
        ashl_root,
        state_dir,
        package_133_state_dir,
        package_134_state_dir,
        package_135_state_dir,
    )
    before = {
        "package_133": source_tree_sha256(source_133),
        "package_134": source_tree_sha256(source_134),
        "package_135": source_tree_sha256(source_135),
    }
    source = load_package_136_sources_read_only(
        package_133_state_dir=source_133,
        package_134_state_dir=source_134,
        package_135_state_dir=source_135,
    )
    store = Package136DriveModulationStore(output)
    if any(
        store.count(table)
        for table in (
            "drive_modulation_applications",
            "drive_modulation_process_receipts",
            "package_136_audits",
        )
    ):
        raise RuntimeError("blocked_package_136_state_dir_not_fresh")
    inventory = build_drive_modulation_consumer_inventory(root)
    contract = build_same_session_modulation_contract(source=source)
    allowlist = build_drive_modulation_consumer_allowlist(
        contract=contract, inventory=inventory
    )
    authorization = build_same_session_modulation_authorization(
        contract=contract, allowlist=allowlist, source=source
    )
    for record in inventory:
        store.append_once("drive_modulation_consumer_inventory", record)
    store.append_once("package_135_signal_authority_bindings", source.source_binding)
    store.append_once("same_session_drive_modulation_contracts", contract)
    store.append_once("drive_modulation_consumer_allowlists", allowlist)
    store.append_once("same_session_drive_modulation_authorizations", authorization)
    process_a = _run_worker_subprocess(
        root=root,
        state_dir=output,
        source_133=source_133,
        source_134=source_134,
        source_135=source_135,
        process_role="modulated_session_a",
        process_instance_id=stable_id("package_136_process_a"),
        authorization_id=authorization.authorization_id,
    )
    process_b = _run_worker_subprocess(
        root=root,
        state_dir=output,
        source_133=source_133,
        source_134=source_134,
        source_135=source_135,
        process_role="neutral_session_b",
        process_instance_id=stable_id("package_136_process_b"),
        authorization_id=None,
    )
    neutrality = _build_cross_session_neutrality(
        source=source,
        process_a=process_a,
        process_b=process_b,
    )
    store.append_record("drive_modulation_cross_session_neutrality", neutrality)
    after = {
        "package_133": source_tree_sha256(source_133),
        "package_134": source_tree_sha256(source_134),
        "package_135": source_tree_sha256(source_135),
    }
    if before != after:
        raise RuntimeError("blocked_package_133_134_or_135_source_modified")
    application = _require_one(
        store.list_payloads("drive_modulation_applications"), "application"
    )
    derivation = _require_one(
        store.list_payloads("drive_modulation_derivations"), "derivation"
    )
    comparison = _require_one(
        store.list_payloads("drive_modulation_counterfactual_comparisons"),
        "counterfactual_comparison",
    )
    return {
        "source_binding_id": source.source_binding.source_binding_id,
        "contract_id": contract.contract_id,
        "allowlist_id": allowlist.allowlist_id,
        "production_consumer_ids": list(allowlist.production_consumer_ids),
        "audit_only_consumer_ids": list(allowlist.audit_only_consumer_ids),
        "authorization_id": authorization.authorization_id,
        "source_trace_id": source.selected_trace.signal_trace_id,
        "raw_level_offset": derivation["raw_level_offset"],
        "effective_offset": application["effective_offset"],
        "absolute_clamp_applied": derivation["absolute_clamp_applied"],
        "delta_clamp_applied": derivation["delta_clamp_applied"],
        "counterfactual_comparison_id": comparison["comparison_id"],
        "counterfactual_status": comparison["comparison_status"],
        "process_a": process_a,
        "process_b": process_b,
        "cross_session_neutrality_id": neutrality.neutrality_record_id,
        "cross_session_neutrality_status": neutrality.neutrality_status,
        "package_133_source_unchanged": before["package_133"] == after["package_133"],
        "package_134_source_unchanged": before["package_134"] == after["package_134"],
        "package_135_source_unchanged": before["package_135"] == after["package_135"],
        "production_runtime_behavior_changed": False,
    }


def _build_process_receipt(
    *,
    process_role: str,
    process_instance_id: str,
    pid: int,
    runtime_session_id: str,
    started: int,
    ended: int,
    source_trace_ref: str,
    authorization_loaded: bool,
    application_ref: str | None,
    neutralization_ref: str,
    comparison_ref: str | None,
) -> DriveModulationProcessReceipt:
    payload: dict[str, Any] = {
        "process_receipt_id": "",
        "process_receipt_sha256": "",
        "schema_version": PROCESS_SCHEMA_VERSION,
        "created_at": utc_now(),
        "process_role": process_role,
        "process_instance_id": process_instance_id,
        "operating_system_process_id": pid,
        "runtime_session_id": runtime_session_id,
        "started_monotonic_ns": started,
        "ended_monotonic_ns": ended,
        "source_signal_trace_ref": source_trace_ref,
        "authorization_loaded": authorization_loaded,
        "prior_session_authorization_loaded": False,
        "prior_session_application_loaded": False,
        "application_ref": application_ref,
        "neutralization_ref": neutralization_ref,
        "comparison_ref": comparison_ref,
        "final_effective_offset": NEUTRAL_OFFSET,
        "worker_status": (
            "same_session_modulation_applied_then_neutralized"
            if process_role == "modulated_session_a"
            else "fresh_session_started_neutral"
        ),
        "source_record_refs": tuple(
            item
            for item in (
                source_trace_ref,
                application_ref,
                neutralization_ref,
                comparison_ref,
            )
            if item is not None
        ),
    }
    return _hashed_record(
        DriveModulationProcessReceipt,
        payload,
        id_field="process_receipt_id",
        hash_field="process_receipt_sha256",
        prefix="drive_modulation_process_receipt",
    )


def _build_cross_session_neutrality(
    *,
    source: Package136SourceBundle,
    process_a: dict[str, Any],
    process_b: dict[str, Any],
) -> DriveModulationCrossSessionNeutralityRecord:
    payload: dict[str, Any] = {
        "neutrality_record_id": "",
        "neutrality_sha256": "",
        "schema_version": CROSS_SESSION_SCHEMA_VERSION,
        "created_at": utc_now(),
        "process_a_receipt_ref": str(process_a["process_receipt_id"]),
        "process_b_receipt_ref": str(process_b["process_receipt_id"]),
        "package_134_active_head_ref": source.package_133_134.active_head.active_head_id,
        "package_134_active_head_sha256": source.package_133_134.active_head.active_head_sha256,
        "package_135_session_a_trace_ref": source.selected_trace.signal_trace_id,
        "package_135_session_b_fresh_root_ref": source.fresh_session_root_trace.signal_trace_id,
        "process_ids_distinct": int(process_a["operating_system_process_id"]) != int(process_b["operating_system_process_id"]),
        "process_instance_ids_distinct": str(process_a["process_instance_id"]) != str(process_b["process_instance_id"]),
        "sessions_distinct": str(process_a["runtime_session_id"]) != str(process_b["runtime_session_id"]),
        "process_a_ended_before_process_b_started": int(process_a["ended_monotonic_ns"]) < int(process_b["started_monotonic_ns"]),
        "package_134_structural_identity_same": source.package_133_134.non_recovery_evidence.structural_identity_continuity_verified,
        "package_134_drive_state_restored": source.package_133_134.non_recovery_evidence.drive_state_restored,
        "package_135_session_b_trace_is_fresh_root": (
            source.fresh_session_root_trace.sequence_index == 0
            and source.fresh_session_root_trace.parent_signal_trace_id is None
        ),
        "authorization_carried": bool(process_b["prior_session_authorization_loaded"]),
        "application_carried": bool(process_b["prior_session_application_loaded"]),
        "effective_offset_carried": not math.isclose(float(process_b["final_effective_offset"]), NEUTRAL_OFFSET),
        "process_b_started_neutral": (
            not process_b["authorization_loaded"]
            and process_b["application_ref"] is None
            and math.isclose(float(process_b["final_effective_offset"]), NEUTRAL_OFFSET)
        ),
        "neutrality_status": "passed_structural_recovery_with_neutral_modulation",
        "source_record_refs": (
            str(process_a["process_receipt_id"]),
            str(process_b["process_receipt_id"]),
            source.package_133_134.active_head.active_head_id,
            source.selected_trace.signal_trace_id,
            source.fresh_session_root_trace.signal_trace_id,
        ),
    }
    return _hashed_record(
        DriveModulationCrossSessionNeutralityRecord,
        payload,
        id_field="neutrality_record_id",
        hash_field="neutrality_sha256",
        prefix="drive_modulation_cross_session_neutrality",
    )


def _run_worker_subprocess(
    *,
    root: Path,
    state_dir: Path,
    source_133: Path,
    source_134: Path,
    source_135: Path,
    process_role: str,
    process_instance_id: str,
    authorization_id: str | None,
) -> dict[str, Any]:
    environment = dict(os.environ)
    pycache = state_dir / "package_136_same_session_drive_modulation_v0" / "pycache"
    pycache.mkdir(parents=True, exist_ok=True)
    environment["PYTHONPYCACHEPREFIX"] = str(pycache)
    command = [
        sys.executable,
        "-m",
        "ashl_core_v1.endocrine.package_136_drive_modulation_worker",
        "--ashl-root",
        str(root),
        "--package-133-state-dir",
        str(source_133),
        "--package-134-state-dir",
        str(source_134),
        "--package-135-state-dir",
        str(source_135),
        "--state-dir",
        str(state_dir),
        "--process-role",
        process_role,
        "--process-instance-id",
        process_instance_id,
    ]
    if authorization_id:
        command.extend(("--authorization-id", authorization_id))
    completed = subprocess.run(
        tuple(command),
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"blocked_package_136_{process_role}_worker:{completed.stderr.strip()}"
        )
    lines = tuple(line for line in completed.stdout.splitlines() if line.strip())
    if not lines:
        raise RuntimeError(f"blocked_package_136_{process_role}_receipt_missing")
    payload = json.loads(lines[-1])
    if payload.get("process_role") != process_role:
        raise RuntimeError(f"blocked_package_136_{process_role}_receipt_role_mismatch")
    return payload


def _hashed_record(
    record_type: type[T],
    payload: dict[str, Any],
    *,
    id_field: str,
    hash_field: str,
    prefix: str,
) -> T:
    identity = dict(payload)
    identity.pop(id_field, None)
    identity.pop(hash_field, None)
    identity.pop("created_at", None)
    digest = sha256_payload(identity)
    payload[id_field] = f"{prefix}:{digest[:16]}"
    payload[hash_field] = digest
    return record_type(**payload)


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


def _source_set_sha256(root: Path, paths: tuple[str, ...]) -> str:
    entries: list[dict[str, Any]] = []
    for relative in paths:
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        entries.append(
            {
                "relative_path": relative,
                "sha256": sha256_bytes(path.read_bytes()),
            }
        )
    return sha256_payload(entries)


def _tree_python_sha256(root: Path) -> str:
    if not root.is_dir():
        raise FileNotFoundError(root)
    entries = tuple(
        {
            "relative_path": path.relative_to(root).as_posix(),
            "sha256": sha256_bytes(path.read_bytes()),
        }
        for path in sorted(root.rglob("*.py"), key=lambda item: item.as_posix().lower())
        if path.is_file() and "__pycache__" not in path.parts
    )
    return sha256_payload(entries)


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


def _validate_external_roots(
    ashl_root: str | Path,
    state_dir: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_135_state_dir: str | Path,
) -> tuple[Path, Path, Path, Path, Path]:
    root = Path(ashl_root).resolve()
    output = Path(state_dir).resolve()
    sources = tuple(
        Path(item).resolve()
        for item in (
            package_133_state_dir,
            package_134_state_dir,
            package_135_state_dir,
        )
    )
    if not root.is_dir() or not all(item.is_dir() for item in sources):
        raise FileNotFoundError("Package 136 root or authority source is missing")
    if _is_within(output, root) or any(_is_within(output, item) for item in sources):
        raise ValueError("Package 136 state_dir must be external and separate from authority sources")
    if len({item.as_posix().lower() for item in sources}) != 3:
        raise ValueError("Package 133, 134 and 135 source roots must be distinct")
    return root, output, sources[0], sources[1], sources[2]


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _git_output(root: Path, *args: str) -> str:
    return subprocess.check_output(("git", *args), cwd=root, text=True).strip()


def _is_ancestor(root: Path, commit: str) -> bool:
    return subprocess.run(
        ("git", "merge-base", "--is-ancestor", commit, "HEAD"),
        cwd=root,
        check=False,
        capture_output=True,
    ).returncode == 0
