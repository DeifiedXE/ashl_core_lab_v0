"""Builders and validators for Package 133 structural self-state lineage."""

from __future__ import annotations

from typing import Any

from ashl_core_v1.runtime.host_sensor_types import sha256_payload, utc_now
from ashl_core_v1.state.persistent_self_state_schema import (
    ALLOWED_PERSISTENT_FIELDS,
    GOVERNANCE_PROFILE_VERSION,
    LINEAGE_SCHEMA_VERSION,
    REPRESENTATION_STATUS,
    SELF_STATE_SCHEMA_VERSION,
    TRANSITION_SCHEMA_VERSION,
    PersistentSelfStateLineageValidationRecord,
    PersistentSelfStateRecord,
    PersistentSelfStateRepresentationContract,
    PersistentSelfStateTransitionRecord,
    calculate_self_state_sha256,
    calculate_transition_id,
    calculate_transition_sha256,
)


def build_self_state_lineage_id(
    *,
    origin_session_id: str,
    representation_contract_ref: str,
) -> str:
    if not origin_session_id or not representation_contract_ref:
        raise ValueError("self-state lineage origin and contract are required")
    payload = {
        "origin_session_id": origin_session_id,
        "representation_contract_ref": representation_contract_ref,
        "lineage_kind": "package_133_structural_self_state",
    }
    return f"self_state_lineage:{sha256_payload(payload)[:16]}"


def build_initial_self_state_record(
    *,
    contract: PersistentSelfStateRepresentationContract,
    origin_session_id: str,
    created_at: str | None = None,
) -> PersistentSelfStateRecord:
    lineage_id = build_self_state_lineage_id(
        origin_session_id=origin_session_id,
        representation_contract_ref=contract.contract_id,
    )
    initialization_ref = (
        "self_state_initialization:"
        + sha256_payload(
            {
                "contract_id": contract.contract_id,
                "lineage_id": lineage_id,
                "origin_session_id": origin_session_id,
            }
        )[:16]
    )
    payload = _base_state_payload(
        contract=contract,
        created_at=created_at or utc_now(),
        lineage_id=lineage_id,
        version=1,
        generation=0,
        parent_id=None,
        parent_sha256=None,
        origin_session_id=origin_session_id,
        source_session_id=origin_session_id,
        session_refs=(f"session:{origin_session_id}",),
        transition_ref=initialization_ref,
        source_refs=(contract.contract_id, initialization_ref),
    )
    return _state_from_payload(payload)


def build_successor_self_state_records(
    *,
    parent: PersistentSelfStateRecord,
    contract: PersistentSelfStateRepresentationContract,
    source_session_id: str,
    created_at: str | None = None,
) -> tuple[PersistentSelfStateRecord, PersistentSelfStateTransitionRecord]:
    if source_session_id == parent.source_session_id:
        raise ValueError("Package 133 successor requires distinct session provenance")
    if parent.representation_contract_ref != contract.contract_id:
        raise ValueError("parent self-state contract mismatch")
    child_version = parent.self_state_version + 1
    child_generation = parent.lineage_generation + 1
    transition_seed = {
        "representation_contract_ref": contract.contract_id,
        "self_state_lineage_id": parent.self_state_lineage_id,
        "transition_kind": "validated_schema_successor",
        "parent_self_state_record_id": parent.self_state_record_id,
        "parent_self_state_sha256": parent.self_state_sha256,
        "to_self_state_version": child_version,
        "source_session_id": source_session_id,
    }
    transition_id = calculate_transition_id(transition_seed)
    session_refs = parent.session_provenance_refs + (f"session:{source_session_id}",)
    child_payload = _base_state_payload(
        contract=contract,
        created_at=created_at or utc_now(),
        lineage_id=parent.self_state_lineage_id,
        version=child_version,
        generation=child_generation,
        parent_id=parent.self_state_record_id,
        parent_sha256=parent.self_state_sha256,
        origin_session_id=parent.origin_session_id,
        source_session_id=source_session_id,
        session_refs=session_refs,
        transition_ref=transition_id,
        source_refs=(contract.contract_id, parent.self_state_record_id, transition_id),
    )
    child = _state_from_payload(child_payload)
    transition_payload: dict[str, Any] = {
        "transition_id": transition_id,
        "transition_sha256": "",
        "schema_version": TRANSITION_SCHEMA_VERSION,
        "created_at": child.created_at,
        "representation_contract_ref": contract.contract_id,
        "self_state_lineage_id": parent.self_state_lineage_id,
        "transition_kind": "validated_schema_successor",
        "transition_scope": "representation_only",
        "transition_reason_code": "explicit_schema_lineage_validation",
        "parent_self_state_record_id": parent.self_state_record_id,
        "parent_self_state_sha256": parent.self_state_sha256,
        "child_self_state_record_id": child.self_state_record_id,
        "child_self_state_sha256": child.self_state_sha256,
        "from_self_state_version": parent.self_state_version,
        "to_self_state_version": child.self_state_version,
        "from_lineage_generation": parent.lineage_generation,
        "to_lineage_generation": child.lineage_generation,
        "source_session_id": source_session_id,
        "session_provenance_refs": session_refs,
        "parent_integrity_verified": True,
        "child_integrity_verified": True,
        "forbidden_content_absent": True,
        "recovery_performed": False,
        "active_head_changed": False,
        "runtime_state_loaded": False,
        "behavior_influence_created": False,
        "drive_signal_created": False,
        "memory_write_created": False,
        "perception_action_created": False,
        "output_created": False,
        "source_record_refs": (
            contract.contract_id,
            parent.self_state_record_id,
            child.self_state_record_id,
        ),
    }
    transition_payload["transition_sha256"] = calculate_transition_sha256(
        transition_payload
    )
    transition = PersistentSelfStateTransitionRecord(**transition_payload)
    return child, transition


def validate_persistent_self_state_record(
    record: PersistentSelfStateRecord | dict[str, Any],
) -> dict[str, Any]:
    try:
        item = record if isinstance(record, PersistentSelfStateRecord) else PersistentSelfStateRecord.from_dict(record)
    except (KeyError, TypeError, ValueError) as error:
        return {
            "valid": False,
            "validation_status": "blocked_invalid_self_state_record",
            "failure_reasons": (str(error),),
        }
    return {
        "valid": True,
        "validation_status": "validated_persistent_self_state_representation",
        "failure_reasons": tuple(),
        "self_state_record_id": item.self_state_record_id,
        "self_state_sha256": item.self_state_sha256,
    }


def validate_persistent_self_state_lineage(
    parent: PersistentSelfStateRecord | dict[str, Any],
    child: PersistentSelfStateRecord | dict[str, Any],
    transition: PersistentSelfStateTransitionRecord | dict[str, Any],
) -> dict[str, Any]:
    try:
        parent_item = parent if isinstance(parent, PersistentSelfStateRecord) else PersistentSelfStateRecord.from_dict(parent)
        child_item = child if isinstance(child, PersistentSelfStateRecord) else PersistentSelfStateRecord.from_dict(child)
        transition_item = transition if isinstance(transition, PersistentSelfStateTransitionRecord) else PersistentSelfStateTransitionRecord.from_dict(transition)
    except (KeyError, TypeError, ValueError) as error:
        return {
            "valid": False,
            "validation_status": "blocked_invalid_self_state_lineage",
            "failure_reasons": (str(error),),
        }
    checks = _lineage_checks(parent_item, child_item, transition_item)
    failures = tuple(name for name, passed in checks.items() if not passed)
    return {
        "valid": not failures,
        "validation_status": (
            "validated_parent_child_representation_lineage"
            if not failures
            else "blocked_invalid_self_state_lineage"
        ),
        "failure_reasons": failures,
        **checks,
    }


def build_self_state_lineage_validation_record(
    *,
    parent: PersistentSelfStateRecord,
    child: PersistentSelfStateRecord,
    transition: PersistentSelfStateTransitionRecord,
    created_at: str | None = None,
) -> PersistentSelfStateLineageValidationRecord:
    result = validate_persistent_self_state_lineage(parent, child, transition)
    checks = _lineage_checks(parent, child, transition)
    identity_payload = {
        "parent": parent.self_state_record_id,
        "child": child.self_state_record_id,
        "transition": transition.transition_id,
        "checks": checks,
    }
    return PersistentSelfStateLineageValidationRecord(
        lineage_validation_id=(
            f"self_state_lineage_validation:{sha256_payload(identity_payload)[:16]}"
        ),
        schema_version=LINEAGE_SCHEMA_VERSION,
        created_at=created_at or utc_now(),
        self_state_lineage_id=parent.self_state_lineage_id,
        parent_self_state_record_id=parent.self_state_record_id,
        child_self_state_record_id=child.self_state_record_id,
        transition_id=transition.transition_id,
        parent_integrity_valid=checks["parent_integrity_valid"],
        child_integrity_valid=checks["child_integrity_valid"],
        transition_integrity_valid=checks["transition_integrity_valid"],
        same_lineage_id=checks["same_lineage_id"],
        parent_link_exact=checks["parent_link_exact"],
        parent_hash_link_exact=checks["parent_hash_link_exact"],
        version_increment_exact=checks["version_increment_exact"],
        generation_increment_exact=checks["generation_increment_exact"],
        session_provenance_distinct=checks["session_provenance_distinct"],
        session_provenance_accumulated=checks["session_provenance_accumulated"],
        allowed_persistent_fields_exact=checks["allowed_persistent_fields_exact"],
        forbidden_content_absent=checks["forbidden_content_absent"],
        forbidden_authority_absent=checks["forbidden_authority_absent"],
        lineage_valid=bool(result["valid"]),
        validation_status=str(result["validation_status"]),
        failure_reasons=tuple(result["failure_reasons"]),
        source_record_refs=(
            parent.self_state_record_id,
            child.self_state_record_id,
            transition.transition_id,
        ),
    )


def _base_state_payload(
    *,
    contract: PersistentSelfStateRepresentationContract,
    created_at: str,
    lineage_id: str,
    version: int,
    generation: int,
    parent_id: str | None,
    parent_sha256: str | None,
    origin_session_id: str,
    source_session_id: str,
    session_refs: tuple[str, ...],
    transition_ref: str,
    source_refs: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "self_state_record_id": "",
        "self_state_sha256": "",
        "schema_version": SELF_STATE_SCHEMA_VERSION,
        "created_at": created_at,
        "representation_contract_ref": contract.contract_id,
        "self_state_lineage_id": lineage_id,
        "self_state_version": version,
        "lineage_generation": generation,
        "representation_status": REPRESENTATION_STATUS,
        "governance_profile_version": GOVERNANCE_PROFILE_VERSION,
        "parent_self_state_record_id": parent_id,
        "parent_self_state_sha256": parent_sha256,
        "origin_session_id": origin_session_id,
        "source_session_id": source_session_id,
        "session_provenance_refs": session_refs,
        "transition_provenance_ref": transition_ref,
        "persistent_field_names": ALLOWED_PERSISTENT_FIELDS,
        "integrity_algorithm": "sha256_canonical_json",
        "raw_perception_embedded": False,
        "world_facts_embedded": False,
        "memory_content_embedded": False,
        "semantic_history_embedded": False,
        "output_content_embedded": False,
        "cross_session_recovery_authority": False,
        "active_head_selection_authority": False,
        "runtime_behavior_influence_authority": False,
        "drive_signal_authority": False,
        "memory_write_authority": False,
        "perception_control_authority": False,
        "action_selection_authority": False,
        "output_authority": False,
        "thought_engine_authority": False,
        "source_record_refs": source_refs,
    }


def _state_from_payload(payload: dict[str, Any]) -> PersistentSelfStateRecord:
    digest = calculate_self_state_sha256(payload)
    payload = dict(payload)
    payload["self_state_sha256"] = digest
    payload["self_state_record_id"] = f"persistent_self_state:{digest[:16]}"
    return PersistentSelfStateRecord(**payload)


def _lineage_checks(
    parent: PersistentSelfStateRecord,
    child: PersistentSelfStateRecord,
    transition: PersistentSelfStateTransitionRecord,
) -> dict[str, bool]:
    content_flags = (
        "raw_perception_embedded",
        "world_facts_embedded",
        "memory_content_embedded",
        "semantic_history_embedded",
        "output_content_embedded",
    )
    authority_flags = (
        "cross_session_recovery_authority",
        "active_head_selection_authority",
        "runtime_behavior_influence_authority",
        "drive_signal_authority",
        "memory_write_authority",
        "perception_control_authority",
        "action_selection_authority",
        "output_authority",
        "thought_engine_authority",
    )
    return {
        "parent_integrity_valid": parent.self_state_sha256 == calculate_self_state_sha256(parent),
        "child_integrity_valid": child.self_state_sha256 == calculate_self_state_sha256(child),
        "transition_integrity_valid": (
            transition.transition_id == calculate_transition_id(transition)
            and transition.transition_sha256 == calculate_transition_sha256(transition)
            and transition.parent_self_state_record_id == parent.self_state_record_id
            and transition.child_self_state_record_id == child.self_state_record_id
        ),
        "same_lineage_id": parent.self_state_lineage_id == child.self_state_lineage_id == transition.self_state_lineage_id,
        "parent_link_exact": child.parent_self_state_record_id == parent.self_state_record_id,
        "parent_hash_link_exact": child.parent_self_state_sha256 == parent.self_state_sha256,
        "version_increment_exact": child.self_state_version == parent.self_state_version + 1,
        "generation_increment_exact": child.lineage_generation == parent.lineage_generation + 1,
        "session_provenance_distinct": parent.source_session_id != child.source_session_id == transition.source_session_id,
        "session_provenance_accumulated": child.session_provenance_refs == parent.session_provenance_refs + (f"session:{child.source_session_id}",),
        "allowed_persistent_fields_exact": parent.persistent_field_names == child.persistent_field_names == ALLOWED_PERSISTENT_FIELDS,
        "forbidden_content_absent": not any(getattr(item, name) for item in (parent, child) for name in content_flags),
        "forbidden_authority_absent": not any(getattr(item, name) for item in (parent, child) for name in authority_flags),
    }
