"""Deterministic, bounded instinct rule runtime for Package 141."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import monotonic_ns, sha256_payload, utc_now
from ashl_core_v1.runtime.local_operator_console_store import LocalOperatorConsoleStore
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.runtime.structural_evidence_sufficiency_assessor import (
    CHECKPOINT_SCHEMA_VERSION,
    create_structural_evidence_checkpoint,
    create_structural_sufficiency_contract,
)
from ashl_core_v1.runtime.structural_evidence_sufficiency_types import (
    StructuralEvidenceCheckpoint,
)
from ashl_core_v1.thought.instinct_layer_types import (
    AUTHORITY_INVENTORY,
    BASELINE_COMMIT,
    BOUNDARY_SCHEMA_VERSION,
    CLOSED_SPAN_ANNOTATION,
    CLOSED_SPAN_RULE_ID,
    CONFLICT_POLICY,
    CONTEXT_SCHEMA_VERSION,
    EVALUATION_SCHEMA_VERSION,
    EVALUATION_SCOPE,
    INPUT_AUTHORITY_INTERFACE,
    INPUT_EVIDENCE_KIND,
    INPUT_GATE_SCHEMA_VERSION,
    INVENTORY_SCHEMA_VERSION,
    OPEN_REGION_ANNOTATION,
    OPEN_REGION_RULE_ID,
    PACKAGE_132_AUDIT_STATUS,
    PACKAGE_132_CLOSURE_ID,
    PACKAGE_140_AUDIT_STATUS,
    PACKAGE_140_CONTRACT_ID,
    RULE_CONTRACT_SCHEMA_VERSION,
    RULE_DEFINITIONS,
    SIGNAL_SCHEMA_VERSION,
    UNKNOWN_POLICY,
    BUNDLE_SCHEMA_VERSION,
    CONFLICT_SCHEMA_VERSION,
    BoundedInstinctSignalRecord,
    InstinctConflictResolutionRecord,
    InstinctEvaluationBundleRecord,
    InstinctEvidenceContextRecord,
    InstinctInputGateDecisionRecord,
    InstinctLayerAuthorityInventoryRecord,
    InstinctLayerConsumerBoundaryRecord,
    InstinctRuleContractRecord,
    InstinctRuleEvaluationRecord,
    build_hashed_record,
)
from ashl_core_v1.thought.package_141_instinct_store import Package141InstinctStore


PACKAGE_132_DATABASE_RELATIVE = Path(
    "package_132_perception_attention_milestone_v0/package_132.sqlite3"
)
PACKAGE_140_DATABASE_RELATIVE = Path(
    "package_140_persistent_self_state_and_drive_milestone_v0/package_140.sqlite3"
)
PACKAGE_132_CLOSURE_RELATIVE = Path(
    "ashl_core_v1/docs/reference/perception_attention_capability_boundary_closure_v0.json"
)
PACKAGE_140_CONTRACT_RELATIVE = Path(
    "ashl_core_v1/docs/reference/persistent_self_state_and_drive_capability_contract_v0.json"
)


@dataclass(frozen=True)
class Package141Preflight:
    inventory: InstinctLayerAuthorityInventoryRecord
    boundary: InstinctLayerConsumerBoundaryRecord
    rule_contract: InstinctRuleContractRecord


@dataclass(frozen=True)
class InstinctEvaluationResult:
    input_gate: InstinctInputGateDecisionRecord
    context: InstinctEvidenceContextRecord | None
    evaluations: tuple[InstinctRuleEvaluationRecord, ...]
    signals: tuple[BoundedInstinctSignalRecord, ...]
    conflict: InstinctConflictResolutionRecord | None
    bundle: InstinctEvaluationBundleRecord


def load_package_141_preflight(
    *,
    ashl_root: str | Path,
    package_132_state_dir: str | Path,
    package_140_state_dir: str | Path,
    state_dir: str | Path | None = None,
    append: bool = False,
) -> Package141Preflight:
    root = Path(ashl_root).resolve()
    closure_payload = _load_hashed_contract(
        root / PACKAGE_132_CLOSURE_RELATIVE,
        id_field="closure_contract_id",
        hash_field="closure_sha256",
        expected_id=PACKAGE_132_CLOSURE_ID,
    )
    capability_payload = _load_hashed_contract(
        root / PACKAGE_140_CONTRACT_RELATIVE,
        id_field="capability_contract_id",
        hash_field="capability_contract_sha256",
        expected_id=PACKAGE_140_CONTRACT_ID,
    )
    _validate_package_132_closure(closure_payload)
    _validate_package_140_contract(capability_payload)
    package_132_audit = _load_latest_audit(
        _resolve_database(package_132_state_dir, PACKAGE_132_DATABASE_RELATIVE),
        table="package_132_audits",
        expected_status=PACKAGE_132_AUDIT_STATUS,
    )
    package_140_audit = _load_latest_audit(
        _resolve_database(package_140_state_dir, PACKAGE_140_DATABASE_RELATIVE),
        table="package_140_audits",
        expected_status=PACKAGE_140_AUDIT_STATUS,
    )

    inventory = build_hashed_record(
        InstinctLayerAuthorityInventoryRecord,
        {
            "inventory_id": "",
            "inventory_sha256": "",
            "schema_version": INVENTORY_SCHEMA_VERSION,
            "created_at": utc_now(),
            "inventory_entries": AUTHORITY_INVENTORY,
            "current_authority_entry_count": sum(
                "current_" in item[2] for item in AUTHORITY_INVENTORY
            ),
            "historical_entry_count": sum(
                "historical_" in item[2] for item in AUTHORITY_INVENTORY
            ),
            "parallel_rule_system_created": False,
            "legacy_thought_signal_promoted": False,
            "source_record_refs": (
                PACKAGE_132_CLOSURE_ID,
                PACKAGE_140_CONTRACT_ID,
                "legacy_inventory:thought_reflex_heuristic_tendency_affordance_task_safety_v0",
            ),
        },
        id_field="inventory_id",
        hash_field="inventory_sha256",
        prefix="instinct_inventory",
    )
    boundary = build_hashed_record(
        InstinctLayerConsumerBoundaryRecord,
        {
            "boundary_id": "",
            "boundary_sha256": "",
            "schema_version": BOUNDARY_SCHEMA_VERSION,
            "created_at": utc_now(),
            "package_132_closure_contract_id": PACKAGE_132_CLOSURE_ID,
            "package_132_audit_id": str(package_132_audit["audit_id"]),
            "package_132_audit_status": str(package_132_audit["audit_status"]),
            "package_140_capability_contract_id": PACKAGE_140_CONTRACT_ID,
            "package_140_audit_id": str(package_140_audit["audit_id"]),
            "package_140_audit_status": str(package_140_audit["audit_status"]),
            "production_input_allowlist": (INPUT_EVIDENCE_KIND,),
            "production_drive_input_allowlist": tuple(),
            "production_self_state_readback_input_allowlist": tuple(),
            "production_output_consumer_allowlist": tuple(),
            "evaluation_scope": EVALUATION_SCOPE,
            "hard_safety_precedence_preserved": True,
            "teacher_authority_precedence_preserved": True,
            "approved_purpose_scope_preserved": True,
            "purpose_creation_allowed": False,
            "action_selection_allowed": False,
            "memory_write_allowed": False,
            "self_state_mutation_allowed": False,
            "perception_action_allowed": False,
            "output_allowed": False,
            "external_control_allowed": False,
            "boundary_status": "ready_for_bounded_instinct_evaluation",
            "source_record_refs": (
                PACKAGE_132_CLOSURE_ID,
                str(package_132_audit["audit_id"]),
                PACKAGE_140_CONTRACT_ID,
                str(package_140_audit["audit_id"]),
                inventory.inventory_id,
            ),
        },
        id_field="boundary_id",
        hash_field="boundary_sha256",
        prefix="instinct_boundary",
    )
    rule_contract = build_hashed_record(
        InstinctRuleContractRecord,
        {
            "rule_contract_id": "",
            "rule_contract_sha256": "",
            "schema_version": RULE_CONTRACT_SCHEMA_VERSION,
            "created_at": utc_now(),
            "rule_definitions": RULE_DEFINITIONS,
            "evaluation_scope": EVALUATION_SCOPE,
            "deterministic": True,
            "random_selection_used": False,
            "weighted_scoring_used": False,
            "learned_ranking_used": False,
            "conflict_policy": CONFLICT_POLICY,
            "unknown_or_missing_evidence_policy": UNKNOWN_POLICY,
            "maximum_rule_count": len(RULE_DEFINITIONS),
            "maximum_signal_count_per_evaluation": len(RULE_DEFINITIONS),
            "signals_revocable": True,
            "output_is_thought_precursor_only": True,
            "source_record_refs": (boundary.boundary_id, inventory.inventory_id),
        },
        id_field="rule_contract_id",
        hash_field="rule_contract_sha256",
        prefix="instinct_rule_contract",
    )
    preflight = Package141Preflight(
        inventory=inventory,
        boundary=boundary,
        rule_contract=rule_contract,
    )
    if append:
        if state_dir is None:
            raise ValueError("state_dir is required when appending Package 141 preflight")
        _require_external_state_dir(root, Path(state_dir).resolve())
        Package141InstinctStore(state_dir).append_group(
            (
                ("instinct_authority_inventories", inventory),
                ("instinct_consumer_boundaries", boundary),
                ("instinct_rule_contracts", rule_contract),
            )
        )
    return preflight


def evaluate_instinct_checkpoint(
    *,
    preflight: Package141Preflight,
    checkpoint: StructuralEvidenceCheckpoint | None,
    state_dir: str | Path | None = None,
    append: bool = False,
    event_stream: LocalOperatorEventStream | None = None,
    input_evidence_kind: str | None = INPUT_EVIDENCE_KIND,
    hard_safety_gate_status: str = "clear",
) -> InstinctEvaluationResult:
    input_gate = _build_input_gate(
        preflight=preflight,
        checkpoint=checkpoint,
        input_evidence_kind=input_evidence_kind,
        hard_safety_gate_status=hard_safety_gate_status,
    )
    if input_gate.decision == "block":
        deterministic_result_sha256 = sha256_payload(
            {
                "input_gate_sha256": input_gate.input_gate_sha256,
                "rule_contract_sha256": preflight.rule_contract.rule_contract_sha256,
                "evaluation_status": "blocked_input",
                "failure_reasons": input_gate.failure_reasons,
            }
        )
        bundle = build_hashed_record(
            InstinctEvaluationBundleRecord,
            {
                "evaluation_bundle_id": "",
                "evaluation_bundle_sha256": "",
                "schema_version": BUNDLE_SCHEMA_VERSION,
                "created_at": utc_now(),
                "input_gate_id": input_gate.input_gate_id,
                "context_id": None,
                "rule_contract_id": preflight.rule_contract.rule_contract_id,
                "rule_evaluation_refs": tuple(),
                "instinct_signal_refs": tuple(),
                "conflict_resolution_ref": None,
                "matched_rule_ids": tuple(),
                "bounded_annotations": tuple(),
                "evaluation_status": "blocked_input",
                "deterministic_result_sha256": deterministic_result_sha256,
                "result_revocable": True,
                "production_consumer_count": 0,
                **_forbidden_output_flags(),
                "llm_runtime_calls": 0,
                "codex_runtime_calls": 0,
                "network_runtime_calls": 0,
                "failure_reasons": input_gate.failure_reasons,
                "source_record_refs": (input_gate.input_gate_id, preflight.rule_contract.rule_contract_id),
                "source_trace_refs": tuple(),
            },
            id_field="evaluation_bundle_id",
            hash_field="evaluation_bundle_sha256",
            prefix="instinct_bundle",
        )
        result = InstinctEvaluationResult(input_gate, None, tuple(), tuple(), None, bundle)
        _persist_result(result, state_dir=state_dir, append=append)
        _emit_result_events(result, event_stream)
        return result

    assert checkpoint is not None
    context = _build_context(input_gate, checkpoint)
    evaluations = tuple(
        _evaluate_rule(
            context=context,
            rule_contract=preflight.rule_contract,
            rule_id=rule_id,
            rule_version=version,
        )
        for rule_id, version, _conditions, _annotation in RULE_DEFINITIONS
    )
    matched = tuple(item for item in evaluations if item.matched)
    signals = tuple(_build_signal(context, item) for item in matched)
    conflict = _build_conflict(context, matched, signals)
    if len(matched) > 1:
        evaluation_status = "conflict_preserved_no_selection"
    elif len(matched) == 1:
        evaluation_status = "matched_single"
    else:
        evaluation_status = "neutral_no_rule_matched"
    deterministic_result_sha256 = sha256_payload(
        {
            "source_checkpoint_sha256": context.source_checkpoint_sha256,
            "rule_contract_sha256": preflight.rule_contract.rule_contract_sha256,
            "matched_rule_ids": tuple(item.rule_id for item in matched),
            "bounded_annotations": tuple(item.bounded_annotation for item in matched),
            "evaluation_status": evaluation_status,
            "conflict_status": conflict.conflict_status,
        }
    )
    bundle = build_hashed_record(
        InstinctEvaluationBundleRecord,
        {
            "evaluation_bundle_id": "",
            "evaluation_bundle_sha256": "",
            "schema_version": BUNDLE_SCHEMA_VERSION,
            "created_at": utc_now(),
            "input_gate_id": input_gate.input_gate_id,
            "context_id": context.context_id,
            "rule_contract_id": preflight.rule_contract.rule_contract_id,
            "rule_evaluation_refs": tuple(item.rule_evaluation_id for item in evaluations),
            "instinct_signal_refs": tuple(item.instinct_signal_id for item in signals),
            "conflict_resolution_ref": conflict.conflict_resolution_id,
            "matched_rule_ids": tuple(item.rule_id for item in matched),
            "bounded_annotations": tuple(str(item.bounded_annotation) for item in matched),
            "evaluation_status": evaluation_status,
            "deterministic_result_sha256": deterministic_result_sha256,
            "result_revocable": True,
            "production_consumer_count": 0,
            **_forbidden_output_flags(),
            "llm_runtime_calls": 0,
            "codex_runtime_calls": 0,
            "network_runtime_calls": 0,
            "failure_reasons": tuple(),
            "source_record_refs": (
                input_gate.input_gate_id,
                context.context_id,
                preflight.rule_contract.rule_contract_id,
                conflict.conflict_resolution_id,
            ),
            "source_trace_refs": checkpoint.source_trace_refs,
        },
        id_field="evaluation_bundle_id",
        hash_field="evaluation_bundle_sha256",
        prefix="instinct_bundle",
    )
    result = InstinctEvaluationResult(input_gate, context, evaluations, signals, conflict, bundle)
    _persist_result(result, state_dir=state_dir, append=append)
    _emit_result_events(result, event_stream)
    return result


def run_bounded_instinct_probe_suite(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
    package_132_state_dir: str | Path,
    package_140_state_dir: str | Path,
) -> dict[str, Any]:
    preflight = load_package_141_preflight(
        ashl_root=ashl_root,
        package_132_state_dir=package_132_state_dir,
        package_140_state_dir=package_140_state_dir,
        state_dir=state_dir,
        append=True,
    )
    event_stream = LocalOperatorEventStream(LocalOperatorConsoleStore(state_dir))
    checkpoints = {
        name: build_controlled_structural_checkpoint(name)
        for name in ("closed", "open", "neutral", "conflict")
    }
    closed_first = evaluate_instinct_checkpoint(
        preflight=preflight,
        checkpoint=checkpoints["closed"],
        state_dir=state_dir,
        append=True,
        event_stream=event_stream,
    )
    closed_repeat = evaluate_instinct_checkpoint(
        preflight=preflight,
        checkpoint=checkpoints["closed"],
        state_dir=state_dir,
        append=True,
        event_stream=event_stream,
    )
    open_result = evaluate_instinct_checkpoint(
        preflight=preflight,
        checkpoint=checkpoints["open"],
        state_dir=state_dir,
        append=True,
        event_stream=event_stream,
    )
    neutral_result = evaluate_instinct_checkpoint(
        preflight=preflight,
        checkpoint=checkpoints["neutral"],
        state_dir=state_dir,
        append=True,
        event_stream=event_stream,
    )
    conflict_result = evaluate_instinct_checkpoint(
        preflight=preflight,
        checkpoint=checkpoints["conflict"],
        state_dir=state_dir,
        append=True,
        event_stream=event_stream,
    )
    blocked_result = evaluate_instinct_checkpoint(
        preflight=preflight,
        checkpoint=None,
        state_dir=state_dir,
        append=True,
        event_stream=event_stream,
        input_evidence_kind=None,
    )
    return {
        "baseline_commit": BASELINE_COMMIT,
        "boundary_id": preflight.boundary.boundary_id,
        "rule_contract_id": preflight.rule_contract.rule_contract_id,
        "production_input_allowlist": preflight.boundary.production_input_allowlist,
        "production_drive_input_allowlist": preflight.boundary.production_drive_input_allowlist,
        "production_self_state_readback_input_allowlist": preflight.boundary.production_self_state_readback_input_allowlist,
        "production_output_consumer_allowlist": preflight.boundary.production_output_consumer_allowlist,
        "closed_first_bundle_id": closed_first.bundle.evaluation_bundle_id,
        "closed_repeat_bundle_id": closed_repeat.bundle.evaluation_bundle_id,
        "closed_deterministic_result_equal": (
            closed_first.bundle.deterministic_result_sha256
            == closed_repeat.bundle.deterministic_result_sha256
        ),
        "closed_matched_rule_ids": closed_first.bundle.matched_rule_ids,
        "open_bundle_id": open_result.bundle.evaluation_bundle_id,
        "open_matched_rule_ids": open_result.bundle.matched_rule_ids,
        "different_condition_different_firing": (
            closed_first.bundle.matched_rule_ids != open_result.bundle.matched_rule_ids
        ),
        "neutral_bundle_id": neutral_result.bundle.evaluation_bundle_id,
        "neutral_status": neutral_result.bundle.evaluation_status,
        "conflict_bundle_id": conflict_result.bundle.evaluation_bundle_id,
        "conflict_status": conflict_result.bundle.evaluation_status,
        "conflict_winner_rule_id": (
            conflict_result.conflict.winner_rule_id if conflict_result.conflict else None
        ),
        "blocked_bundle_id": blocked_result.bundle.evaluation_bundle_id,
        "blocked_status": blocked_result.bundle.evaluation_status,
        "bounded_signal_count": sum(
            len(item.signals)
            for item in (
                closed_first,
                closed_repeat,
                open_result,
                neutral_result,
                conflict_result,
            )
        ),
        "llm_runtime_calls": 0,
        "codex_runtime_calls": 0,
        "network_runtime_calls": 0,
    }


def build_controlled_structural_checkpoint(condition: str) -> StructuralEvidenceCheckpoint:
    if condition not in {"closed", "open", "neutral", "conflict"}:
        raise ValueError("unknown Package 141 controlled structural condition")
    suffix = condition
    contract = create_structural_sufficiency_contract(
        runtime_session_id=f"runtime_session:package_141:{suffix}",
        perception_session_id=f"perception_session:package_141:{suffix}",
        observation_window_id=f"observation_window:package_141:{suffix}",
        focus_context_id=f"focus_context:package_141:{suffix}",
        hard_deadline_event_time_ns=3_000_000_000,
        source_record_refs=(
            f"package_128_contract_source:package_141:{suffix}",
            PACKAGE_132_CLOSURE_ID,
        ),
        source_trace_refs=(f"trace:package_141:structural_probe:{suffix}",),
    )
    observed = tuple()
    open_regions = tuple()
    closed_spans = tuple()
    closure: int | None = None
    if condition == "closed":
        observed = ("visual_region:package_141:closed:0",)
        closed_spans = ("temporal_span:package_141:closed:0",)
        closure = 1_400_000_000
    elif condition == "open":
        observed = ("visual_region:package_141:open:0",)
        open_regions = ("visual_region:package_141:open:0",)
    elif condition == "conflict":
        observed = (
            "visual_region:package_141:conflict:closed",
            "visual_region:package_141:conflict:open",
        )
        open_regions = ("visual_region:package_141:conflict:open",)
        closed_spans = ("temporal_span:package_141:conflict:closed",)
        closure = 1_400_000_000
    return create_structural_evidence_checkpoint(
        contract=contract,
        checkpoint_index=4,
        evaluated_at_event_time_ns=2_000_000_000,
        evaluated_at_processing_time_ns=2_100_000_000,
        elapsed_observation_ns=2_000_000_000,
        complete_alignment_window_count=4,
        partial_alignment_window_count=0,
        focused_region_view_id=f"focused_region_view:package_141:{suffix}",
        full_frame_perception_readable_data_refs=(
            f"perception_readable_data:package_141:{suffix}:full_frame",
        ),
        focused_region_evidence_record_count=1 if observed else 0,
        observed_visual_region_refs=observed,
        open_visual_region_refs=open_regions,
        closed_visual_span_refs=closed_spans,
        latest_visual_closure_event_time_ns=closure,
        latest_complete_source_coverage_event_time_ns=2_000_000_000,
        screen_source_coverage_present=True,
        host_state_source_coverage_present=True,
        source_record_refs=(
            f"package_128_checkpoint_source:package_141:{suffix}",
            f"alignment_window:package_141:{suffix}:complete",
            f"full_frame_primitive:package_141:{suffix}",
        ),
        source_trace_refs=(f"trace:package_141:structural_probe:{suffix}",),
    )


def validate_no_forbidden_instinct_authority(
    *,
    drive_input_used: bool = False,
    self_state_readback_used: bool = False,
    memory_used: bool = False,
    purpose_created_or_expanded: bool = False,
    semantic_input_used: bool = False,
    confidence_used: bool = False,
    teacher_authority_overridden: bool = False,
    selected_action_created: bool = False,
    motor_command_created: bool = False,
    memory_write_created: bool = False,
    self_state_mutation_created: bool = False,
    perception_action_created: bool = False,
    output_created: bool = False,
    external_control_created: bool = False,
    random_rule_used: bool = False,
    llm_used: bool = False,
    codex_used: bool = False,
    network_used: bool = False,
    package_142_implemented: bool = False,
) -> None:
    forbidden = {
        "drive_input_used": drive_input_used,
        "self_state_readback_used": self_state_readback_used,
        "memory_used": memory_used,
        "purpose_created_or_expanded": purpose_created_or_expanded,
        "semantic_input_used": semantic_input_used,
        "confidence_used": confidence_used,
        "teacher_authority_overridden": teacher_authority_overridden,
        "selected_action_created": selected_action_created,
        "motor_command_created": motor_command_created,
        "memory_write_created": memory_write_created,
        "self_state_mutation_created": self_state_mutation_created,
        "perception_action_created": perception_action_created,
        "output_created": output_created,
        "external_control_created": external_control_created,
        "random_rule_used": random_rule_used,
        "llm_used": llm_used,
        "codex_used": codex_used,
        "network_used": network_used,
        "package_142_implemented": package_142_implemented,
    }
    active = tuple(name for name, value in forbidden.items() if value)
    if active:
        raise ValueError(f"Package 141 forbidden authority requested:{','.join(active)}")


def _build_input_gate(
    *,
    preflight: Package141Preflight,
    checkpoint: StructuralEvidenceCheckpoint | None,
    input_evidence_kind: str | None,
    hard_safety_gate_status: str,
) -> InstinctInputGateDecisionRecord:
    failures: list[str] = []
    checkpoint_payload: dict[str, Any] | None = None
    if hard_safety_gate_status not in {"clear", "blocked"}:
        raise ValueError("invalid hard-safety gate status")
    if hard_safety_gate_status == "blocked":
        failures.append("blocked_hard_safety_precedence")
    if checkpoint is None:
        failures.append("blocked_missing_structural_evidence")
    elif not isinstance(checkpoint, StructuralEvidenceCheckpoint):
        failures.append("blocked_unknown_evidence_type")
    else:
        checkpoint_payload = checkpoint.to_dict()
        if input_evidence_kind != INPUT_EVIDENCE_KIND:
            failures.append("blocked_unknown_evidence_kind")
        if checkpoint.schema_version != CHECKPOINT_SCHEMA_VERSION:
            failures.append("blocked_checkpoint_schema_mismatch")
        if not all((checkpoint.checkpoint_id, checkpoint.contract_id, checkpoint.runtime_session_id, checkpoint.perception_session_id, checkpoint.observation_window_id, checkpoint.source_record_refs)):
            failures.append("blocked_incomplete_checkpoint_lineage")
        if any((checkpoint.required_lane_drop_count, checkpoint.backpressure_fault_count, checkpoint.capture_failure_count, checkpoint.compile_failure_count)):
            failures.append("blocked_transport_or_compiler_integrity")
        if any(value is not None for value in (checkpoint.semantic_label, checkpoint.uncertainty_score, checkpoint.confidence_score)):
            failures.append("blocked_semantic_or_score_injection")
    decision = "block" if failures else "allow"
    checkpoint_sha256 = sha256_payload(checkpoint_payload) if checkpoint_payload else None
    refs = [preflight.boundary.boundary_id, preflight.rule_contract.rule_contract_id]
    if checkpoint is not None and isinstance(checkpoint, StructuralEvidenceCheckpoint):
        refs.extend(checkpoint.source_record_refs)
    payload = {
        "input_gate_id": "",
        "input_gate_sha256": "",
        "schema_version": INPUT_GATE_SCHEMA_VERSION,
        "created_at": utc_now(),
        "boundary_id": preflight.boundary.boundary_id,
        "input_evidence_kind": input_evidence_kind,
        "source_checkpoint_id": checkpoint.checkpoint_id if isinstance(checkpoint, StructuralEvidenceCheckpoint) else None,
        "source_checkpoint_sha256": checkpoint_sha256,
        "runtime_session_id": checkpoint.runtime_session_id if isinstance(checkpoint, StructuralEvidenceCheckpoint) else None,
        "perception_session_id": checkpoint.perception_session_id if isinstance(checkpoint, StructuralEvidenceCheckpoint) else None,
        "observation_window_id": checkpoint.observation_window_id if isinstance(checkpoint, StructuralEvidenceCheckpoint) else None,
        "hard_safety_gate_status": hard_safety_gate_status,
        "decision": decision,
        "decision_status": "ready_for_instinct_evaluation" if decision == "allow" else failures[0],
        "failure_reasons": tuple(failures),
        "drive_input_used": False,
        "self_state_readback_used": False,
        "memory_used": False,
        "purpose_used_or_created": False,
        "semantic_input_used": False,
        "source_record_refs": tuple(refs),
        "source_trace_refs": checkpoint.source_trace_refs if isinstance(checkpoint, StructuralEvidenceCheckpoint) else tuple(),
    }
    return build_hashed_record(
        InstinctInputGateDecisionRecord,
        payload,
        id_field="input_gate_id",
        hash_field="input_gate_sha256",
        prefix="instinct_input_gate",
    )


def _build_context(
    input_gate: InstinctInputGateDecisionRecord,
    checkpoint: StructuralEvidenceCheckpoint,
) -> InstinctEvidenceContextRecord:
    processing_time = monotonic_ns()
    payload = {
        "context_id": "",
        "context_sha256": "",
        "schema_version": CONTEXT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "input_gate_id": input_gate.input_gate_id,
        "input_evidence_kind": INPUT_EVIDENCE_KIND,
        "source_authority_interface": INPUT_AUTHORITY_INTERFACE,
        "source_checkpoint_id": checkpoint.checkpoint_id,
        "source_checkpoint_sha256": input_gate.source_checkpoint_sha256,
        "runtime_session_id": checkpoint.runtime_session_id,
        "perception_session_id": checkpoint.perception_session_id,
        "observation_window_id": checkpoint.observation_window_id,
        "source_event_time_ns": checkpoint.evaluated_at_event_time_ns,
        "source_processing_time_ns": checkpoint.evaluated_at_processing_time_ns,
        "evaluation_processing_time_ns": processing_time,
        "observed_visual_region_refs": checkpoint.observed_visual_region_refs,
        "open_visual_region_refs": checkpoint.open_visual_region_refs,
        "closed_visual_span_refs": checkpoint.closed_visual_span_refs,
        "observed_visual_region_count": len(checkpoint.observed_visual_region_refs),
        "open_visual_region_count": len(checkpoint.open_visual_region_refs),
        "closed_visual_span_count": len(checkpoint.closed_visual_span_refs),
        "full_frame_evidence_present": bool(checkpoint.full_frame_perception_readable_data_refs),
        "focused_region_evidence_present": checkpoint.focused_region_evidence_record_count > 0,
        "transport_integrity_valid": not any((checkpoint.required_lane_drop_count, checkpoint.backpressure_fault_count, checkpoint.capture_failure_count, checkpoint.compile_failure_count)),
        "lineage_integrity_valid": True,
        "semantic_label": None,
        "confidence_score": None,
        "uncertainty_score": None,
        "source_record_refs": (input_gate.input_gate_id, checkpoint.checkpoint_id) + checkpoint.source_record_refs,
        "source_trace_refs": checkpoint.source_trace_refs,
    }
    return build_hashed_record(
        InstinctEvidenceContextRecord,
        payload,
        id_field="context_id",
        hash_field="context_sha256",
        prefix="instinct_context",
    )


def _evaluate_rule(
    *,
    context: InstinctEvidenceContextRecord,
    rule_contract: InstinctRuleContractRecord,
    rule_id: str,
    rule_version: str,
) -> InstinctRuleEvaluationRecord:
    if rule_id == CLOSED_SPAN_RULE_ID:
        conditions = (
            ("observed_visual_region_count", "gte", 1, context.observed_visual_region_count, context.observed_visual_region_count >= 1),
            ("closed_visual_span_count", "gte", 1, context.closed_visual_span_count, context.closed_visual_span_count >= 1),
        )
        annotation = CLOSED_SPAN_ANNOTATION
    elif rule_id == OPEN_REGION_RULE_ID:
        conditions = (
            ("observed_visual_region_count", "gte", 1, context.observed_visual_region_count, context.observed_visual_region_count >= 1),
            ("open_visual_region_count", "gte", 1, context.open_visual_region_count, context.open_visual_region_count >= 1),
        )
        annotation = OPEN_REGION_ANNOTATION
    else:
        raise ValueError("unknown Package 141 rule")
    matched = all(bool(item[4]) for item in conditions)
    payload = {
        "rule_evaluation_id": "",
        "rule_evaluation_sha256": "",
        "schema_version": EVALUATION_SCHEMA_VERSION,
        "created_at": utc_now(),
        "context_id": context.context_id,
        "rule_contract_id": rule_contract.rule_contract_id,
        "rule_id": rule_id,
        "rule_version": rule_version,
        "rule_conditions": conditions,
        "matched": matched,
        "evaluation_result": "matched" if matched else "not_matched",
        "bounded_annotation": annotation if matched else None,
        "source_event_time_ns": context.source_event_time_ns,
        "evaluation_processing_time_ns": monotonic_ns(),
        "deterministic_rule": True,
        "random_value_used": False,
        "weighted_score_used": False,
        "failure_reasons": tuple(),
        "source_record_refs": (context.context_id, rule_contract.rule_contract_id, context.source_checkpoint_id),
        "source_trace_refs": context.source_trace_refs,
    }
    return build_hashed_record(
        InstinctRuleEvaluationRecord,
        payload,
        id_field="rule_evaluation_id",
        hash_field="rule_evaluation_sha256",
        prefix="instinct_rule_evaluation",
    )


def _build_signal(
    context: InstinctEvidenceContextRecord,
    evaluation: InstinctRuleEvaluationRecord,
) -> BoundedInstinctSignalRecord:
    if not evaluation.matched or not evaluation.bounded_annotation:
        raise ValueError("Package 141 signal requires a matched rule")
    payload = {
        "instinct_signal_id": "",
        "instinct_signal_sha256": "",
        "schema_version": SIGNAL_SCHEMA_VERSION,
        "created_at": utc_now(),
        "context_id": context.context_id,
        "rule_evaluation_id": evaluation.rule_evaluation_id,
        "rule_id": evaluation.rule_id,
        "bounded_annotation": evaluation.bounded_annotation,
        "signal_kind": "revocable_structural_thought_precursor",
        "lifetime_scope": "one_instinct_evaluation_bundle",
        "revocable": True,
        "consumed_by_production_runtime": False,
        "purpose_authority": False,
        "candidate_ordering_authority": False,
        "action_selection_authority": False,
        "motor_command_authority": False,
        "memory_write_authority": False,
        "self_state_mutation_authority": False,
        "perception_action_authority": False,
        "output_authority": False,
        "external_control_authority": False,
        "semantic_label": None,
        "source_record_refs": (context.context_id, evaluation.rule_evaluation_id),
        "source_trace_refs": context.source_trace_refs,
    }
    return build_hashed_record(
        BoundedInstinctSignalRecord,
        payload,
        id_field="instinct_signal_id",
        hash_field="instinct_signal_sha256",
        prefix="instinct_signal",
    )


def _build_conflict(
    context: InstinctEvidenceContextRecord,
    matched: tuple[InstinctRuleEvaluationRecord, ...],
    signals: tuple[BoundedInstinctSignalRecord, ...],
) -> InstinctConflictResolutionRecord:
    conflict = len(matched) > 1
    payload = {
        "conflict_resolution_id": "",
        "conflict_resolution_sha256": "",
        "schema_version": CONFLICT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "context_id": context.context_id,
        "matched_rule_evaluation_refs": tuple(item.rule_evaluation_id for item in matched),
        "instinct_signal_refs": tuple(item.instinct_signal_id for item in signals),
        "conflict_detected": conflict,
        "conflict_status": "conflict_preserved_no_selection" if conflict else "no_conflict",
        "conflict_policy": CONFLICT_POLICY,
        "winner_rule_id": None,
        "all_matches_preserved": True,
        "candidate_ordering_created": False,
        "action_selection_created": False,
        "source_record_refs": (context.context_id,) + tuple(item.rule_evaluation_id for item in matched),
    }
    return build_hashed_record(
        InstinctConflictResolutionRecord,
        payload,
        id_field="conflict_resolution_id",
        hash_field="conflict_resolution_sha256",
        prefix="instinct_conflict",
    )


def _persist_result(
    result: InstinctEvaluationResult,
    *,
    state_dir: str | Path | None,
    append: bool,
) -> None:
    if not append:
        return
    if state_dir is None:
        raise ValueError("state_dir is required when appending Package 141 evaluation")
    records: list[tuple[str, Any]] = [
        ("instinct_input_gate_decisions", result.input_gate),
    ]
    if result.context is not None:
        records.append(("instinct_evidence_contexts", result.context))
    records.extend(("instinct_rule_evaluations", item) for item in result.evaluations)
    records.extend(("bounded_instinct_signals", item) for item in result.signals)
    if result.conflict is not None:
        records.append(("instinct_conflict_resolutions", result.conflict))
    records.append(("instinct_evaluation_bundles", result.bundle))
    Package141InstinctStore(state_dir).append_group(tuple(records))


def _emit_result_events(
    result: InstinctEvaluationResult,
    event_stream: LocalOperatorEventStream | None,
) -> None:
    if event_stream is None:
        return
    ids = {
        "runtime_session_id": result.input_gate.runtime_session_id,
        "perception_session_id": result.input_gate.perception_session_id,
        "observation_window_id": result.input_gate.observation_window_id,
    }
    if result.input_gate.decision == "block":
        event_stream.append_event(
            event_kind="instinct_evaluation_blocked",
            source_record_refs=(result.input_gate.input_gate_id, result.bundle.evaluation_bundle_id),
            source_trace_refs=result.input_gate.source_trace_refs,
            **ids,
        )
        return
    event_stream.append_event(
        event_kind="instinct_input_context_bound",
        source_record_refs=(result.input_gate.input_gate_id, str(result.context.context_id)),
        source_trace_refs=result.input_gate.source_trace_refs,
        **ids,
    )
    for evaluation in result.evaluations:
        event_stream.append_event(
            event_kind="instinct_rule_evaluated",
            source_record_refs=(evaluation.rule_evaluation_id, evaluation.context_id),
            source_trace_refs=evaluation.source_trace_refs,
            **ids,
        )
    for signal in result.signals:
        event_stream.append_event(
            event_kind="bounded_instinct_signal_created",
            source_record_refs=(signal.instinct_signal_id, signal.rule_evaluation_id),
            source_trace_refs=signal.source_trace_refs,
            **ids,
        )
    if result.bundle.evaluation_status == "conflict_preserved_no_selection":
        event_stream.append_event(
            event_kind="instinct_rule_conflict_preserved",
            source_record_refs=(str(result.conflict.conflict_resolution_id), result.bundle.evaluation_bundle_id),
            source_trace_refs=result.bundle.source_trace_refs,
            **ids,
        )
    elif result.bundle.evaluation_status == "neutral_no_rule_matched":
        event_stream.append_event(
            event_kind="instinct_evaluation_neutral",
            source_record_refs=(result.bundle.evaluation_bundle_id,),
            source_trace_refs=result.bundle.source_trace_refs,
            **ids,
        )
    event_stream.append_event(
        event_kind="instinct_evaluation_completed",
        source_record_refs=(result.bundle.evaluation_bundle_id,),
        source_trace_refs=result.bundle.source_trace_refs,
        **ids,
    )


def _forbidden_output_flags() -> dict[str, bool]:
    return {
        "purpose_created_or_expanded": False,
        "selected_action_created": False,
        "motor_command_created": False,
        "memory_write_created": False,
        "self_state_mutation_created": False,
        "perception_action_created": False,
        "output_created": False,
        "external_control_created": False,
    }


def _load_hashed_contract(
    path: Path,
    *,
    id_field: str,
    hash_field: str,
    expected_id: str,
) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    identity = dict(payload)
    observed_id = str(identity.pop(id_field, ""))
    observed_hash = str(identity.pop(hash_field, ""))
    identity.pop("created_at", None)
    if observed_id != expected_id or observed_hash != sha256_payload(identity):
        raise RuntimeError(f"blocked_corrupt_frozen_contract:{path.name}")
    return payload


def _validate_package_132_closure(payload: dict[str, Any]) -> None:
    if not payload.get("perception_capability_construction_frozen"):
        raise RuntimeError("blocked_package_132_perception_line_not_frozen")
    if payload.get("package_132_adds_runtime_capability") or payload.get("package_132_adds_internal_action"):
        raise RuntimeError("blocked_package_132_closure_authority_changed")
    if INPUT_AUTHORITY_INTERFACE not in payload.get("downstream_read_only_interfaces", ()):
        raise RuntimeError("blocked_package_132_structural_history_interface_missing")
    required_forbidden = {
        "perception_action_selection_authority",
        "memory_write_or_admission_authority",
        "output_authority",
        "external_control_authority",
    }
    if not required_forbidden.issubset(set(payload.get("downstream_forbidden_authorities", ()))):
        raise RuntimeError("blocked_package_132_downstream_boundary_incomplete")


def _validate_package_140_contract(payload: dict[str, Any]) -> None:
    if not payload.get("authority_line_frozen") or not payload.get("stable_consumer_boundary"):
        raise RuntimeError("blocked_package_140_authority_line_not_frozen")
    if not payload.get("package_141_plus_may_consume_existing_contracts") or payload.get("package_141_plus_may_bypass_or_expand_authorities"):
        raise RuntimeError("blocked_package_140_downstream_contract_changed")
    if int(payload.get("production_drive_consumer_count", -1)) != 0 or int(payload.get("production_readback_consumer_count", -1)) != 0:
        raise RuntimeError("blocked_package_140_production_consumer_boundary_changed")


def _resolve_database(root: str | Path, relative: Path) -> Path:
    supplied = Path(root).resolve()
    direct = supplied / relative
    if direct.is_file():
        database = direct
    elif supplied.is_file() and supplied.name == relative.name:
        database = supplied
    else:
        matches = tuple(path for path in supplied.rglob(relative.name) if path.is_file())
        if len(matches) != 1:
            raise RuntimeError(
                f"blocked_missing_or_ambiguous_authority_database:{relative.name}:{len(matches)}"
            )
        database = matches[0]
    if database.is_symlink():
        raise RuntimeError("blocked_symlinked_authority_database")
    return database


def _load_latest_audit(
    database: Path,
    *,
    table: str,
    expected_status: str,
) -> dict[str, Any]:
    uri = f"file:{database.as_posix()}?mode=ro"
    with closing(sqlite3.connect(uri, uri=True, timeout=30.0)) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        if str(connection.execute("PRAGMA integrity_check").fetchone()[0]) != "ok":
            raise RuntimeError(f"blocked_corrupt_authority_database:{database.name}")
        row = connection.execute(
            f"SELECT payload_json, payload_sha256 FROM {table} ORDER BY row_id DESC LIMIT 1"
        ).fetchone()
    if row is None:
        raise RuntimeError(f"blocked_authority_audit_missing:{table}")
    payload = json.loads(str(row["payload_json"]))
    if str(row["payload_sha256"]) != sha256_payload(payload):
        raise RuntimeError(f"blocked_corrupt_authority_audit_payload:{table}")
    if payload.get("audit_status") != expected_status or payload.get("failure_reasons"):
        raise RuntimeError(f"blocked_authority_audit_not_passed:{table}")
    return payload


def _require_external_state_dir(root: Path, state_dir: Path) -> None:
    try:
        state_dir.relative_to(root)
    except ValueError:
        return
    raise ValueError("Package 141 state_dir must be outside the repository")
