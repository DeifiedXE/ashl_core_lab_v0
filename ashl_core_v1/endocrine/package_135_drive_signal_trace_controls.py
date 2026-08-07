"""Actual invalid-construction controls for Package 135."""

from __future__ import annotations

from dataclasses import fields, replace
from pathlib import Path
from typing import Any

from ashl_core_v1.endocrine.drive_signal_trace_runtime import build_signal_trace
from ashl_core_v1.endocrine.drive_signal_trace_types import (
    CONTROL_NAMES,
    CONTROL_SCHEMA_VERSION,
    DriveRegulatorySignalSourceObservation,
    DriveRegulatorySignalTraceContract,
    DriveRegulatorySignalTraceRecord,
    Package135DriveTraceControlResult,
)
from ashl_core_v1.endocrine.package_135_drive_signal_trace_store import (
    Package135DriveSignalTraceStore,
)
from ashl_core_v1.runtime.host_sensor_types import sha256_payload, utc_now


def run_package_135_drive_trace_controls(
    *, state_dir: str | Path, append: bool = True
) -> Package135DriveTraceControlResult:
    store = Package135DriveSignalTraceStore(state_dir)
    contract = _record_from_payload(
        DriveRegulatorySignalTraceContract,
        _require_one(store.list_payloads("drive_trace_contracts"), "contract"),
    )
    observations = tuple(
        DriveRegulatorySignalSourceObservation(**_tuple_payload(DriveRegulatorySignalSourceObservation, item))
        for item in store.list_payloads("drive_source_observations")
    )
    traces = tuple(
        DriveRegulatorySignalTraceRecord.from_dict(item)
        for item in store.list_payloads("drive_signal_traces")
    )
    root_a = next(item for item in traces if item.sequence_index == 0)
    successor_a = next(item for item in traces if item.sequence_index == 1)
    observation_a = next(
        item for item in observations if item.source_observation_id == root_a.source_observation_ref
    )
    observation_b = next(
        item for item in observations if item.runtime_session_id != root_a.runtime_session_id
    )

    def rejects(call: Any) -> bool:
        try:
            call()
        except (KeyError, TypeError, ValueError, RuntimeError):
            return True
        return False

    controls = {
        "semantic_identity_rejected": rejects(
            lambda: replace(root_a, semantic_label="semantic_drive")
        ),
        "purpose_desire_reward_emotion_rejected": all(
            rejects(call)
            for call in (
                lambda: replace(root_a, purpose_ref="purpose:x"),
                lambda: replace(root_a, desire_authority=True),
                lambda: replace(root_a, reward_authority=True),
                lambda: replace(root_a, semantic_emotion_authority=True),
            )
        ),
        "tendency_affordance_selected_action_conflation_rejected": all(
            rejects(call)
            for call in (
                lambda: replace(root_a, tendency_ref="tendency:x"),
                lambda: replace(root_a, affordance_authority=True),
                lambda: replace(root_a, action_preference_authority=True),
                lambda: replace(root_a, selected_action_ref="selected_action:x"),
            )
        ),
        "self_state_or_memory_content_rejected": all(
            rejects(call)
            for call in (
                lambda: replace(root_a, self_state_content_authority=True),
                lambda: replace(root_a, memory_content_authority=True),
                lambda: replace(root_a, cross_session_persistence_authority=True),
            )
        ),
        "runtime_modulation_authority_rejected": all(
            rejects(call)
            for call in (
                lambda: replace(root_a, perception_modulation_authority=True),
                lambda: replace(root_a, attention_modulation_authority=True),
                lambda: replace(root_a, candidate_ordering_authority=True),
                lambda: replace(root_a, thought_engine_authority=True),
                lambda: replace(root_a, memory_influence_authority=True),
                lambda: replace(root_a, output_authority=True),
            )
        ),
        "legacy_endocrine_promotion_rejected": rejects(
            lambda: replace(observation_a, legacy_endocrine_promoted=True)
        ),
        "runtime_status_relabel_rejected": rejects(
            lambda: replace(observation_a, runtime_status_relabelled_as_drive=True)
        ),
        "invalid_value_or_time_rejected": all(
            rejects(call)
            for call in (
                lambda: replace(observation_a, normalized_level=1.25),
                lambda: replace(
                    observation_a,
                    observed_at_processing_time_ns=observation_a.observed_at_event_time_ns - 1,
                ),
            )
        ),
        "lineage_hash_tamper_rejected": rejects(
            lambda: replace(successor_a, parent_signal_trace_sha256="0" * 64)
        ),
        "cross_session_parent_rejected": rejects(
            lambda: build_signal_trace(
                contract=contract,
                observation=observation_b,
                signal_lineage_id=root_a.signal_lineage_id,
                sequence_index=1,
                parent=root_a,
            )
        ),
        "package_134_drive_recovery_rejected": rejects(
            lambda: replace(contract, package_134_recovery_allowed=True)
        ),
        "package_136_authority_rejected": rejects(
            lambda: replace(contract, package_136_modulation_authorized=True)
        ),
    }
    ordered = tuple((name, bool(controls[name])) for name in CONTROL_NAMES)
    result = Package135DriveTraceControlResult(
        control_result_id=f"package_135_controls:{sha256_payload(controls)[:16]}",
        schema_version=CONTROL_SCHEMA_VERSION,
        created_at=utc_now(),
        controls=ordered,
        passed_count=sum(passed for _name, passed in ordered),
        expected_count=len(CONTROL_NAMES),
        controls_passed=all(passed for _name, passed in ordered),
    )
    if append:
        store.append_once("package_135_control_results", result)
    return result


def _record_from_payload(record_type: type[Any], payload: dict[str, Any]) -> Any:
    return record_type(**_tuple_payload(record_type, payload))


def _tuple_payload(record_type: type[Any], payload: dict[str, Any]) -> dict[str, Any]:
    values = dict(payload)
    for item in fields(record_type):
        if "tuple" in str(item.type).lower() and isinstance(values.get(item.name), list):
            values[item.name] = tuple(values[item.name])
    return values


def _require_one(payloads: tuple[dict[str, Any], ...], label: str) -> dict[str, Any]:
    if len(payloads) != 1:
        raise RuntimeError(f"blocked_package_135_{label}_cardinality:{len(payloads)}")
    return payloads[0]
