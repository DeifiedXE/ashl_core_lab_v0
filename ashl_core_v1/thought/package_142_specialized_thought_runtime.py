"""Bounded deterministic specialized-rule runtime for Package 142."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

from ashl_core_v1.runtime.host_sensor_types import monotonic_ns, sha256_payload, utc_now
from ashl_core_v1.runtime.local_operator_console_store import LocalOperatorConsoleStore
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.thought.instinct_layer_types import (
    BoundedInstinctSignalRecord,
    InstinctEvaluationBundleRecord,
    InstinctLayerConsumerBoundaryRecord,
    InstinctRuleContractRecord,
    Package141InstinctLayerRuntimeAudit,
)
from ashl_core_v1.thought.package_142_specialized_thought_store import (
    Package142SpecializedThoughtStore,
)
from ashl_core_v1.thought.specialized_thought_types import (
    BASELINE_COMMIT,
    CLOSED_FAMILY_ID,
    CLOSED_PRECURSOR,
    CONSUMER_SCHEMA_VERSION,
    CONSUMER_SCOPE,
    COUNTERFACTUAL_SCHEMA_VERSION,
    EVALUATION_SCHEMA_VERSION,
    EVALUATION_SCOPE,
    FAMILY_DEFINITIONS,
    FAMILY_SCHEMA_VERSION,
    INVALIDATION_SCHEMA_VERSION,
    MAXIMUM_BINDING_LIFETIME_NS,
    OPEN_FAMILY_ID,
    OPEN_PRECURSOR,
    OUTPUT_DOMAIN,
    PACKAGE_141_BUNDLE_SCHEMA,
    PACKAGE_141_PASS_STATUS,
    PACKAGE_141_SIGNAL_KIND,
    PACKAGE_141_SIGNAL_LIFETIME,
    PACKAGE_141_SIGNAL_SCHEMA,
    PRECURSOR_BINDING_SCHEMA_VERSION,
    RESULT_SCHEMA_VERSION,
    CONFLICT_POLICY,
    CONFLICT_SCHEMA_VERSION,
    BoundedSpecializedThoughtResultRecord,
    SpecializedThoughtCascadeInvalidationRecord,
    SpecializedThoughtCounterfactualEquivalenceRecord,
    SpecializedThoughtCrossFamilyConflictRecord,
    SpecializedThoughtInstinctConsumerBindingRecord,
    SpecializedThoughtPrecursorBindingRecord,
    SpecializedThoughtRuleEvaluationRecord,
    SpecializedThoughtRuleFamilyContractRecord,
    build_hashed_record,
)


PACKAGE_141_RELATIVE_DATABASE = Path(
    "package_141_instinct_layer_runtime_v0/package_141.sqlite3"
)
PACKAGE_132_CLOSURE_RELATIVE = Path(
    "ashl_core_v1/docs/reference/perception_attention_capability_boundary_closure_v0.json"
)
PACKAGE_140_CONTRACT_RELATIVE = Path(
    "ashl_core_v1/docs/reference/persistent_self_state_and_drive_capability_contract_v0.json"
)


@dataclass(frozen=True)
class Package141EvidenceSnapshot:
    database_path: Path
    database_sha256: str
    audit: Package141InstinctLayerRuntimeAudit
    boundary: InstinctLayerConsumerBoundaryRecord
    rule_contract: InstinctRuleContractRecord
    bundles: tuple[InstinctEvaluationBundleRecord, ...]
    signals: tuple[BoundedInstinctSignalRecord, ...]
    closed_bundle: InstinctEvaluationBundleRecord
    open_bundle: InstinctEvaluationBundleRecord
    conflict_bundle: InstinctEvaluationBundleRecord


@dataclass(frozen=True)
class Package142Preflight:
    source: Package141EvidenceSnapshot
    consumer_binding: SpecializedThoughtInstinctConsumerBindingRecord
    family_contracts: tuple[SpecializedThoughtRuleFamilyContractRecord, ...]


@dataclass(frozen=True)
class SpecializedEvaluationOutput:
    precursor_binding: SpecializedThoughtPrecursorBindingRecord
    evaluation: SpecializedThoughtRuleEvaluationRecord
    result: BoundedSpecializedThoughtResultRecord | None


def load_package_142_preflight(
    *,
    ashl_root: str | Path,
    package_141_state_dir: str | Path,
    state_dir: str | Path | None = None,
    append: bool = False,
) -> Package142Preflight:
    root = Path(ashl_root).resolve()
    if state_dir is not None:
        _require_external_state_dir(root, Path(state_dir))
    source = load_package_141_evidence(package_141_state_dir)
    if source.audit.source_head != BASELINE_COMMIT:
        raise ValueError("blocked_package_141_audit_not_bound_to_package_142_baseline")
    binding = _build_consumer_binding(source)
    families = tuple(_build_family_contract(binding, definition) for definition in FAMILY_DEFINITIONS)
    if append:
        if state_dir is None:
            raise ValueError("state_dir is required when appending Package 142 preflight")
        store = Package142SpecializedThoughtStore(state_dir)
        store.append_group(
            (("specialized_thought_consumer_bindings", binding),)
            + tuple(("specialized_thought_rule_family_contracts", item) for item in families)
        )
        stream = LocalOperatorEventStream(LocalOperatorConsoleStore(state_dir))
        _emit(stream, "specialized_thought_consumer_bound", (binding.consumer_binding_id, source.audit.audit_id))
        for family in families:
            _emit(stream, "specialized_thought_rule_family_loaded", (family.family_contract_id, binding.consumer_binding_id))
    return Package142Preflight(source=source, consumer_binding=binding, family_contracts=families)


def load_package_141_evidence(state_dir: str | Path) -> Package141EvidenceSnapshot:
    database = _resolve_package_141_database(state_dir)
    before = _sha256_file(database)
    audit_payloads = _read_verified_table(database, "package_141_audits")
    boundary_payloads = _read_verified_table(database, "instinct_consumer_boundaries")
    rule_payloads = _read_verified_table(database, "instinct_rule_contracts")
    bundle_payloads = _read_verified_table(database, "instinct_evaluation_bundles")
    signal_payloads = _read_verified_table(database, "bounded_instinct_signals")
    passed_audits = tuple(
        Package141InstinctLayerRuntimeAudit(**item)
        for item in audit_payloads
        if item.get("audit_status") == PACKAGE_141_PASS_STATUS
    )
    if not passed_audits:
        raise ValueError("blocked_missing_passed_package_141_audit")
    audit = passed_audits[-1]
    boundary = InstinctLayerConsumerBoundaryRecord(**_require_single_identity(boundary_payloads, "boundary_id"))
    rule_contract = InstinctRuleContractRecord(**_require_single_identity(rule_payloads, "rule_contract_id"))
    bundles = tuple(InstinctEvaluationBundleRecord(**item) for item in bundle_payloads)
    signals = tuple(BoundedInstinctSignalRecord(**item) for item in signal_payloads)
    if any(item.schema_version != PACKAGE_141_SIGNAL_SCHEMA for item in signals):
        raise ValueError("blocked_unknown_package_141_signal_schema")
    signal_map = {item.instinct_signal_id: item for item in signals}
    closed_candidates = _eligible_single_bundles(bundles, signal_map, CLOSED_PRECURSOR)
    open_candidates = _eligible_single_bundles(bundles, signal_map, OPEN_PRECURSOR)
    conflict_candidates = tuple(
        item
        for item in bundles
        if item.schema_version == PACKAGE_141_BUNDLE_SCHEMA
        and item.evaluation_status == "conflict_preserved_no_selection"
        and set(item.bounded_annotations) == {CLOSED_PRECURSOR, OPEN_PRECURSOR}
        and all(ref in signal_map for ref in item.instinct_signal_refs)
    )
    if not closed_candidates or not open_candidates or not conflict_candidates:
        raise ValueError("blocked_incomplete_package_141_precursor_evidence")
    after = _sha256_file(database)
    if before != after:
        raise RuntimeError("blocked_package_141_source_changed_during_read")
    return Package141EvidenceSnapshot(
        database_path=database,
        database_sha256=before,
        audit=audit,
        boundary=boundary,
        rule_contract=rule_contract,
        bundles=bundles,
        signals=signals,
        closed_bundle=sorted(closed_candidates, key=lambda item: item.evaluation_bundle_id)[0],
        open_bundle=sorted(open_candidates, key=lambda item: item.evaluation_bundle_id)[0],
        conflict_bundle=sorted(conflict_candidates, key=lambda item: item.evaluation_bundle_id)[0],
    )


def evaluate_specialized_precursor(
    *,
    preflight: Package142Preflight,
    family_id: str,
    source_bundle: InstinctEvaluationBundleRecord,
    source_signal: BoundedInstinctSignalRecord,
    bound_at_monotonic_ns: int | None = None,
    evaluated_at_monotonic_ns: int | None = None,
    precursor_revoked: bool = False,
    append_to: Package142SpecializedThoughtStore | None = None,
    event_stream: LocalOperatorEventStream | None = None,
) -> SpecializedEvaluationOutput:
    if not isinstance(source_bundle, InstinctEvaluationBundleRecord) or not isinstance(
        source_signal, BoundedInstinctSignalRecord
    ):
        raise ValueError("blocked_package_142_requires_typed_package_141_precursor")
    family = _family_contract(preflight, family_id)
    _validate_source_precursor(source_bundle, source_signal, family)
    if precursor_revoked:
        raise ValueError("blocked_revoked_package_141_precursor")
    bound_at = int(bound_at_monotonic_ns or monotonic_ns())
    evaluated_at = int(evaluated_at_monotonic_ns or (bound_at + 1))
    binding = _build_precursor_binding(
        preflight.consumer_binding,
        family,
        source_bundle,
        source_signal,
        bound_at,
    )
    expired = evaluated_at >= binding.expires_at_monotonic_ns
    conditions = (
        (
            "source_signal_schema_version",
            "equals_allowlisted_schema",
            PACKAGE_141_SIGNAL_SCHEMA,
            source_signal.schema_version,
            source_signal.schema_version == PACKAGE_141_SIGNAL_SCHEMA,
        ),
        (
            "source_bounded_annotation",
            "equals_family_input_allowlist_member",
            family.input_annotation_allowlist[0],
            source_signal.bounded_annotation,
            source_signal.bounded_annotation in family.input_annotation_allowlist,
        ),
        (
            "source_evaluation_bundle_status",
            "is_typed_matched_or_conflict_bundle",
            "matched_single_or_conflict_preserved_no_selection",
            source_bundle.evaluation_status,
            source_bundle.evaluation_status
            in {"matched_single", "conflict_preserved_no_selection"},
        ),
        (
            "source_instinct_signal_lineage",
            "signal_ref_is_member_of_source_bundle",
            source_signal.instinct_signal_id,
            source_signal.instinct_signal_id,
            source_signal.instinct_signal_id in source_bundle.instinct_signal_refs,
        ),
        (
            "precursor_binding_lease",
            "evaluated_before_expiry",
            "active",
            "expired" if expired else "active",
            not expired,
        ),
    )
    condition_match = all(item[4] for item in conditions)
    deterministic_hash = sha256_payload(
        {
            "family_id": family.family_id,
            "family_version": family.family_version,
            "rule_id": family.rule_id,
            "rule_version": family.rule_version,
            "source_instinct_signal_sha256": source_signal.instinct_signal_sha256,
            "source_annotation": source_signal.bounded_annotation,
            "output_annotation": family.output_annotation_allowlist[0] if condition_match else None,
            "matched": condition_match,
        }
    )
    failure_reasons = ("blocked_expired_package_141_precursor",) if expired else ()
    evaluation = build_hashed_record(
        SpecializedThoughtRuleEvaluationRecord,
        {
            "specialized_evaluation_id": "",
            "specialized_evaluation_sha256": "",
            "schema_version": EVALUATION_SCHEMA_VERSION,
            "created_at": utc_now(),
            "family_contract_id": family.family_contract_id,
            "family_id": family.family_id,
            "rule_id": family.rule_id,
            "precursor_binding_refs": (binding.precursor_binding_id,),
            "source_instinct_signal_refs": (source_signal.instinct_signal_id,),
            "evaluated_at_monotonic_ns": evaluated_at,
            "binding_expires_at_monotonic_ns": binding.expires_at_monotonic_ns,
            "rule_conditions": conditions,
            "matched": condition_match,
            "evaluation_status": "blocked_expired_precursor" if expired else ("matched" if condition_match else "not_matched"),
            "bounded_result_annotation": family.output_annotation_allowlist[0] if condition_match else None,
            "deterministic_result_sha256": deterministic_hash,
            "deterministic_rule": True,
            "random_value_used": False,
            "weighted_score_used": False,
            "learned_ranking_used": False,
            "recursive_input_used": False,
            "drive_input_used": False,
            "self_state_readback_used": False,
            "legacy_thought_signal_used": False,
            "direct_perception_input_used": False,
            "semantic_label": None,
            "failure_reasons": failure_reasons,
            "source_record_refs": (
                binding.precursor_binding_id,
                source_signal.instinct_signal_id,
                source_bundle.evaluation_bundle_id,
                family.family_contract_id,
            ),
            "source_trace_refs": source_signal.source_trace_refs,
        },
        id_field="specialized_evaluation_id",
        hash_field="specialized_evaluation_sha256",
        prefix="specialized_evaluation",
    )
    result = _build_result(binding, evaluation, family, source_bundle, source_signal) if condition_match else None
    if append_to is not None:
        records: tuple[tuple[str, Any], ...] = (
            ("specialized_thought_precursor_bindings", binding),
            ("specialized_thought_rule_evaluations", evaluation),
        )
        if result is not None:
            records += (("bounded_specialized_thought_results", result),)
        append_to.append_group(records)
    _emit(event_stream, "specialized_thought_precursor_bound", (binding.precursor_binding_id, source_signal.instinct_signal_id), source_signal.source_trace_refs)
    _emit(event_stream, "specialized_thought_rule_evaluated", (evaluation.specialized_evaluation_id, binding.precursor_binding_id), source_signal.source_trace_refs)
    if result is not None:
        _emit(event_stream, "bounded_specialized_thought_result_created", (result.specialized_result_id, evaluation.specialized_evaluation_id), source_signal.source_trace_refs)
    elif expired:
        _emit(event_stream, "specialized_thought_evaluation_blocked", (evaluation.specialized_evaluation_id, binding.precursor_binding_id), source_signal.source_trace_refs)
    return SpecializedEvaluationOutput(binding, evaluation, result)


def create_cross_family_conflict(
    *,
    source_bundle: InstinctEvaluationBundleRecord,
    outputs: tuple[SpecializedEvaluationOutput, ...],
    append_to: Package142SpecializedThoughtStore | None = None,
    event_stream: LocalOperatorEventStream | None = None,
) -> SpecializedThoughtCrossFamilyConflictRecord:
    results = tuple(item.result for item in outputs if item.result is not None)
    if len(results) != 2:
        raise ValueError("Package 142 conflict requires two matched specialized results")
    conflict = build_hashed_record(
        SpecializedThoughtCrossFamilyConflictRecord,
        {
            "conflict_id": "",
            "conflict_sha256": "",
            "schema_version": CONFLICT_SCHEMA_VERSION,
            "created_at": utc_now(),
            "source_evaluation_bundle_id": source_bundle.evaluation_bundle_id,
            "source_evaluation_bundle_sha256": source_bundle.evaluation_bundle_sha256,
            "family_refs": tuple(item.family_contract_id for item in results),
            "specialized_result_refs": tuple(item.specialized_result_id for item in results),
            "output_domain": OUTPUT_DOMAIN,
            "bounded_result_annotations": tuple(item.bounded_result_annotation for item in results),
            "incompatible_results_detected": True,
            "conflict_policy": CONFLICT_POLICY,
            "conflict_status": "unresolved_cross_family_conflict_preserved",
            "all_results_preserved": True,
            "winner_result_id": None,
            "ranking_used": False,
            "voting_used": False,
            "random_tie_break_used": False,
            "deliberation_created": False,
            "action_selection_created": False,
            "source_record_refs": (source_bundle.evaluation_bundle_id,) + tuple(item.specialized_result_id for item in results),
            "source_trace_refs": source_bundle.source_trace_refs,
        },
        id_field="conflict_id",
        hash_field="conflict_sha256",
        prefix="specialized_conflict",
    )
    if append_to is not None:
        append_to.append_once("specialized_thought_cross_family_conflicts", conflict)
    _emit(event_stream, "specialized_thought_cross_family_conflict_preserved", (conflict.conflict_id,) + conflict.specialized_result_refs, conflict.source_trace_refs)
    return conflict


def invalidate_specialized_results(
    *,
    output: SpecializedEvaluationOutput,
    transition_kind: str,
    observed_at_monotonic_ns: int,
    append_to: Package142SpecializedThoughtStore | None = None,
    event_stream: LocalOperatorEventStream | None = None,
) -> SpecializedThoughtCascadeInvalidationRecord:
    if output.result is None:
        raise ValueError("Package 142 invalidation requires a created result")
    invalidation = build_hashed_record(
        SpecializedThoughtCascadeInvalidationRecord,
        {
            "invalidation_id": "",
            "invalidation_sha256": "",
            "schema_version": INVALIDATION_SCHEMA_VERSION,
            "created_at": utc_now(),
            "precursor_binding_id": output.precursor_binding.precursor_binding_id,
            "source_instinct_signal_id": output.precursor_binding.source_instinct_signal_id,
            "specialized_result_refs": (output.result.specialized_result_id,),
            "transition_kind": transition_kind,
            "observed_at_monotonic_ns": int(observed_at_monotonic_ns),
            "binding_expires_at_monotonic_ns": output.precursor_binding.expires_at_monotonic_ns,
            "source_lifetime_scope": output.precursor_binding.source_lifetime_scope,
            "upstream_scope_closed": True,
            "package_141_record_mutated": False,
            "cascade_invalidation_required": True,
            "result_valid_before_transition": True,
            "result_valid_after_transition": False,
            "dangling_specialized_result": False,
            "invalidation_status": "cascade_invalidated",
            "source_record_refs": (
                output.precursor_binding.source_instinct_signal_id,
                output.precursor_binding.precursor_binding_id,
                output.result.specialized_result_id,
            ),
            "source_trace_refs": output.result.source_trace_refs,
        },
        id_field="invalidation_id",
        hash_field="invalidation_sha256",
        prefix="specialized_invalidation",
    )
    if append_to is not None:
        append_to.append_once("specialized_thought_cascade_invalidations", invalidation)
    _emit(event_stream, "specialized_thought_result_invalidated", (invalidation.invalidation_id, output.result.specialized_result_id), invalidation.source_trace_refs)
    return invalidation


def run_specialized_thought_suite(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
    package_141_state_dir: str | Path,
) -> dict[str, Any]:
    root = Path(ashl_root).resolve()
    _require_external_state_dir(root, Path(state_dir))
    preflight = load_package_142_preflight(
        ashl_root=root,
        package_141_state_dir=package_141_state_dir,
        state_dir=state_dir,
        append=True,
    )
    store = Package142SpecializedThoughtStore(state_dir)
    stream = LocalOperatorEventStream(LocalOperatorConsoleStore(state_dir))
    signal_map = {item.instinct_signal_id: item for item in preflight.source.signals}
    closed_signal = signal_map[preflight.source.closed_bundle.instinct_signal_refs[0]]
    open_signal = signal_map[preflight.source.open_bundle.instinct_signal_refs[0]]
    base = monotonic_ns()
    closed = evaluate_specialized_precursor(
        preflight=preflight,
        family_id=CLOSED_FAMILY_ID,
        source_bundle=preflight.source.closed_bundle,
        source_signal=closed_signal,
        bound_at_monotonic_ns=base,
        evaluated_at_monotonic_ns=base + 1,
        append_to=store,
        event_stream=stream,
    )
    closed_repeat = evaluate_specialized_precursor(
        preflight=preflight,
        family_id=CLOSED_FAMILY_ID,
        source_bundle=preflight.source.closed_bundle,
        source_signal=closed_signal,
        bound_at_monotonic_ns=base + 2,
        evaluated_at_monotonic_ns=base + 3,
        append_to=store,
        event_stream=stream,
    )
    open_output = evaluate_specialized_precursor(
        preflight=preflight,
        family_id=OPEN_FAMILY_ID,
        source_bundle=preflight.source.open_bundle,
        source_signal=open_signal,
        bound_at_monotonic_ns=base + 10,
        evaluated_at_monotonic_ns=base + 11,
        append_to=store,
        event_stream=stream,
    )
    conflict_outputs: list[SpecializedEvaluationOutput] = []
    for offset, signal_ref in enumerate(preflight.source.conflict_bundle.instinct_signal_refs, start=20):
        signal = signal_map[signal_ref]
        family_id = CLOSED_FAMILY_ID if signal.bounded_annotation == CLOSED_PRECURSOR else OPEN_FAMILY_ID
        conflict_outputs.append(
            evaluate_specialized_precursor(
                preflight=preflight,
                family_id=family_id,
                source_bundle=preflight.source.conflict_bundle,
                source_signal=signal,
                bound_at_monotonic_ns=base + offset,
                evaluated_at_monotonic_ns=base + offset + 1,
                append_to=store,
                event_stream=stream,
            )
        )
    conflict = create_cross_family_conflict(
        source_bundle=preflight.source.conflict_bundle,
        outputs=tuple(conflict_outputs),
        append_to=store,
        event_stream=stream,
    )
    invalidations = [
        invalidate_specialized_results(
            output=closed,
            transition_kind="upstream_precursor_expired",
            observed_at_monotonic_ns=closed.precursor_binding.expires_at_monotonic_ns,
            append_to=store,
            event_stream=stream,
        ),
        invalidate_specialized_results(
            output=closed_repeat,
            transition_kind="upstream_precursor_revoked",
            observed_at_monotonic_ns=closed_repeat.evaluation.evaluated_at_monotonic_ns + 1,
            append_to=store,
            event_stream=stream,
        ),
        invalidate_specialized_results(
            output=open_output,
            transition_kind="upstream_precursor_revoked",
            observed_at_monotonic_ns=open_output.evaluation.evaluated_at_monotonic_ns + 1,
            append_to=store,
            event_stream=stream,
        ),
    ]
    invalidations.extend(
        invalidate_specialized_results(
            output=item,
            transition_kind="upstream_precursor_revoked",
            observed_at_monotonic_ns=item.evaluation.evaluated_at_monotonic_ns + 1,
            append_to=store,
            event_stream=stream,
        )
        for item in conflict_outputs
    )
    counterfactual = build_counterfactual_equivalence(
        root=root,
        source_sha256_before=preflight.source.database_sha256,
        source_sha256_after=_sha256_file(preflight.source.database_path),
        source_record_refs=(
            preflight.consumer_binding.consumer_binding_id,
            closed.result.specialized_result_id if closed.result else "",
            open_output.result.specialized_result_id if open_output.result else "",
            conflict.conflict_id,
        ),
    )
    store.append_once("specialized_thought_counterfactual_equivalence_records", counterfactual)
    _emit(stream, "specialized_thought_counterfactual_verified", (counterfactual.counterfactual_id, preflight.consumer_binding.consumer_binding_id))
    return {
        "consumer_binding_id": preflight.consumer_binding.consumer_binding_id,
        "family_contract_ids": tuple(item.family_contract_id for item in preflight.family_contracts),
        "closed_source_bundle_id": preflight.source.closed_bundle.evaluation_bundle_id,
        "open_source_bundle_id": preflight.source.open_bundle.evaluation_bundle_id,
        "conflict_source_bundle_id": preflight.source.conflict_bundle.evaluation_bundle_id,
        "closed_result_id": closed.result.specialized_result_id if closed.result else None,
        "open_result_id": open_output.result.specialized_result_id if open_output.result else None,
        "conflict_result_ids": tuple(item.result.specialized_result_id for item in conflict_outputs if item.result),
        "conflict_id": conflict.conflict_id,
        "conflict_status": conflict.conflict_status,
        "deterministic_repeat_verified": closed.evaluation.deterministic_result_sha256 == closed_repeat.evaluation.deterministic_result_sha256,
        "invalidation_ids": tuple(item.invalidation_id for item in invalidations),
        "expiry_cascade_verified": invalidations[0].transition_kind == "upstream_precursor_expired",
        "revocation_cascade_verified": all(item.transition_kind == "upstream_precursor_revoked" for item in invalidations[1:]),
        "counterfactual_id": counterfactual.counterfactual_id,
        "counterfactual_status": counterfactual.counterfactual_status,
        "package_141_source_sha256_before": preflight.source.database_sha256,
        "package_141_source_sha256_after": _sha256_file(preflight.source.database_path),
    }


def build_counterfactual_equivalence(
    *,
    root: Path,
    source_sha256_before: str,
    source_sha256_after: str,
    source_record_refs: tuple[str, ...],
) -> SpecializedThoughtCounterfactualEquivalenceRecord:
    p132_before = _sha256_file(root / PACKAGE_132_CLOSURE_RELATIVE)
    p140_before = _sha256_file(root / PACKAGE_140_CONTRACT_RELATIVE)
    authority_payload = {
        "package_141_source": source_sha256_before,
        "package_132_closure": p132_before,
        "package_140_contract": p140_before,
        "purpose_authority": "unchanged",
        "action_authority": "unchanged",
        "memory_authority": "unchanged",
        "self_state_authority": "unchanged",
        "drive_authority": "unchanged",
        "perception_authority": "unchanged",
        "output_authority": "unchanged",
    }
    neutral = sha256_payload(authority_payload)
    p132_after = _sha256_file(root / PACKAGE_132_CLOSURE_RELATIVE)
    p140_after = _sha256_file(root / PACKAGE_140_CONTRACT_RELATIVE)
    specialized_payload = dict(authority_payload)
    specialized_payload.update(
        {
            "package_141_source": source_sha256_after,
            "package_132_closure": p132_after,
            "package_140_contract": p140_after,
        }
    )
    specialized = sha256_payload(specialized_payload)
    source_unchanged = all(
        (
            source_sha256_before == source_sha256_after,
            p132_before == p132_after,
            p140_before == p140_after,
            neutral == specialized,
        )
    )
    return build_hashed_record(
        SpecializedThoughtCounterfactualEquivalenceRecord,
        {
            "counterfactual_id": "",
            "counterfactual_sha256": "",
            "schema_version": COUNTERFACTUAL_SCHEMA_VERSION,
            "created_at": utc_now(),
            "package_141_source_sha256_before": source_sha256_before,
            "package_141_source_sha256_after": source_sha256_after,
            "package_132_closure_sha256_before": p132_before,
            "package_132_closure_sha256_after": p132_after,
            "package_140_contract_sha256_before": p140_before,
            "package_140_contract_sha256_after": p140_after,
            "neutral_authority_fingerprint": neutral,
            "specialized_authority_fingerprint": specialized,
            "changed_surfaces": ("package_142_specialized_thought_evidence_only",),
            "runtime_behavior_equivalent": source_unchanged,
            "memory_equivalent": source_unchanged,
            "purpose_equivalent": source_unchanged,
            "action_equivalent": source_unchanged,
            "output_equivalent": source_unchanged,
            "self_state_equivalent": source_unchanged,
            "drive_equivalent": source_unchanged,
            "perception_authority_equivalent": source_unchanged,
            "source_authorities_unchanged": source_unchanged,
            "specialized_records_only_difference": source_unchanged,
            "counterfactual_status": "passed_specialized_thought_counterfactual_equivalence" if source_unchanged else "blocked_specialized_thought_counterfactual_equivalence",
            "source_record_refs": tuple(item for item in source_record_refs if item),
        },
        id_field="counterfactual_id",
        hash_field="counterfactual_sha256",
        prefix="specialized_counterfactual",
    )


def validate_no_forbidden_specialized_authority(**flags: bool) -> None:
    if any(bool(value) for value in flags.values()):
        names = ",".join(sorted(name for name, value in flags.items() if value))
        raise ValueError(f"blocked_forbidden_package_142_authority:{names}")


def _build_consumer_binding(source: Package141EvidenceSnapshot) -> SpecializedThoughtInstinctConsumerBindingRecord:
    return build_hashed_record(
        SpecializedThoughtInstinctConsumerBindingRecord,
        {
            "consumer_binding_id": "",
            "consumer_binding_sha256": "",
            "schema_version": CONSUMER_SCHEMA_VERSION,
            "created_at": utc_now(),
            "package_141_audit_id": source.audit.audit_id,
            "package_141_audit_sha256": source.audit.audit_sha256,
            "package_141_audit_status": source.audit.audit_status,
            "package_141_source_head": source.audit.source_head,
            "package_141_boundary_id": source.boundary.boundary_id,
            "package_141_boundary_sha256": source.boundary.boundary_sha256,
            "package_141_rule_contract_id": source.rule_contract.rule_contract_id,
            "package_141_rule_contract_sha256": source.rule_contract.rule_contract_sha256,
            "package_141_source_database_sha256": source.database_sha256,
            "consumer_scope": CONSUMER_SCOPE,
            "allowed_input_schema_versions": (PACKAGE_141_SIGNAL_SCHEMA,),
            "allowed_precursor_annotations": (CLOSED_PRECURSOR, OPEN_PRECURSOR),
            "production_drive_input_allowlist": (),
            "production_self_state_readback_input_allowlist": (),
            "production_output_consumer_allowlist": (),
            "package_141_store_read_only": True,
            "package_141_history_mutated": False,
            "legacy_thought_signal_allowed": False,
            "direct_perception_input_allowed": False,
            "hard_safety_precedence_preserved": source.boundary.hard_safety_precedence_preserved,
            "teacher_authority_precedence_preserved": source.boundary.teacher_authority_precedence_preserved,
            "approved_purpose_scope_preserved": source.boundary.approved_purpose_scope_preserved,
            "binding_status": "ready_for_bounded_specialized_thought",
            "source_record_refs": (
                source.audit.audit_id,
                source.boundary.boundary_id,
                source.rule_contract.rule_contract_id,
            ),
            "source_trace_refs": ("trace:package_142:read_only_package_141_consumer",),
        },
        id_field="consumer_binding_id",
        hash_field="consumer_binding_sha256",
        prefix="specialized_consumer",
    )


def _build_family_contract(
    binding: SpecializedThoughtInstinctConsumerBindingRecord,
    definition: tuple[str, str, str, str, str, str, str],
) -> SpecializedThoughtRuleFamilyContractRecord:
    return build_hashed_record(
        SpecializedThoughtRuleFamilyContractRecord,
        {
            "family_contract_id": "",
            "family_contract_sha256": "",
            "schema_version": FAMILY_SCHEMA_VERSION,
            "created_at": utc_now(),
            "consumer_binding_id": binding.consumer_binding_id,
            "family_id": definition[0],
            "family_version": definition[1],
            "rule_id": definition[2],
            "rule_version": definition[3],
            "evaluation_scope": EVALUATION_SCOPE,
            "input_schema_allowlist": (PACKAGE_141_SIGNAL_SCHEMA,),
            "input_annotation_allowlist": (definition[4],),
            "output_annotation_allowlist": (definition[5],),
            "output_domain": OUTPUT_DOMAIN,
            "rule_condition": definition[6],
            "maximum_precursor_count": 1,
            "maximum_evaluation_count": 1,
            "maximum_binding_lifetime_ns": MAXIMUM_BINDING_LIFETIME_NS,
            "deterministic": True,
            "versioned": True,
            "precursor_expiry_required": True,
            "precursor_revocation_required": True,
            "recursive_input_allowed": False,
            "cross_family_chaining_allowed": False,
            "persistent_state_created": False,
            "workspace_created": False,
            "iterative_search_allowed": False,
            "arbitrary_rule_chaining_allowed": False,
            "hard_safety_precedence_preserved": True,
            "teacher_authority_precedence_preserved": True,
            "approved_purpose_scope_preserved": True,
            "purpose_authority": False,
            "candidate_ordering_authority": False,
            "action_selection_authority": False,
            "memory_write_authority": False,
            "self_state_mutation_authority": False,
            "perception_action_authority": False,
            "output_authority": False,
            "external_control_authority": False,
            "source_record_refs": (binding.consumer_binding_id, binding.package_141_rule_contract_id),
        },
        id_field="family_contract_id",
        hash_field="family_contract_sha256",
        prefix="specialized_family_contract",
    )


def _build_precursor_binding(
    consumer: SpecializedThoughtInstinctConsumerBindingRecord,
    family: SpecializedThoughtRuleFamilyContractRecord,
    bundle: InstinctEvaluationBundleRecord,
    signal: BoundedInstinctSignalRecord,
    bound_at: int,
) -> SpecializedThoughtPrecursorBindingRecord:
    return build_hashed_record(
        SpecializedThoughtPrecursorBindingRecord,
        {
            "precursor_binding_id": "",
            "precursor_binding_sha256": "",
            "schema_version": PRECURSOR_BINDING_SCHEMA_VERSION,
            "created_at": utc_now(),
            "consumer_binding_id": consumer.consumer_binding_id,
            "family_contract_id": family.family_contract_id,
            "family_id": family.family_id,
            "source_evaluation_bundle_id": bundle.evaluation_bundle_id,
            "source_evaluation_bundle_sha256": bundle.evaluation_bundle_sha256,
            "source_instinct_signal_id": signal.instinct_signal_id,
            "source_instinct_signal_sha256": signal.instinct_signal_sha256,
            "source_rule_id": signal.rule_id,
            "source_bounded_annotation": signal.bounded_annotation,
            "source_signal_schema_version": signal.schema_version,
            "source_signal_kind": signal.signal_kind,
            "source_lifetime_scope": signal.lifetime_scope,
            "source_revocable": signal.revocable,
            "source_consumed_by_production_runtime_at_creation": signal.consumed_by_production_runtime,
            "bound_at_monotonic_ns": bound_at,
            "expires_at_monotonic_ns": bound_at + MAXIMUM_BINDING_LIFETIME_NS,
            "single_evaluation_only": True,
            "hard_safety_gate_clear": True,
            "binding_status": "bound_for_one_specialized_evaluation",
            "failure_reasons": (),
            "source_record_refs": (
                consumer.consumer_binding_id,
                family.family_contract_id,
                bundle.evaluation_bundle_id,
                signal.instinct_signal_id,
            ),
            "source_trace_refs": signal.source_trace_refs,
        },
        id_field="precursor_binding_id",
        hash_field="precursor_binding_sha256",
        prefix="specialized_precursor_binding",
    )


def _build_result(
    binding: SpecializedThoughtPrecursorBindingRecord,
    evaluation: SpecializedThoughtRuleEvaluationRecord,
    family: SpecializedThoughtRuleFamilyContractRecord,
    bundle: InstinctEvaluationBundleRecord,
    signal: BoundedInstinctSignalRecord,
) -> BoundedSpecializedThoughtResultRecord:
    return build_hashed_record(
        BoundedSpecializedThoughtResultRecord,
        {
            "specialized_result_id": "",
            "specialized_result_sha256": "",
            "schema_version": RESULT_SCHEMA_VERSION,
            "created_at": utc_now(),
            "specialized_evaluation_id": evaluation.specialized_evaluation_id,
            "family_contract_id": family.family_contract_id,
            "family_id": family.family_id,
            "rule_id": family.rule_id,
            "precursor_binding_id": binding.precursor_binding_id,
            "source_instinct_signal_id": signal.instinct_signal_id,
            "source_evaluation_bundle_id": bundle.evaluation_bundle_id,
            "result_kind": "revocable_bounded_specialized_thought",
            "output_domain": OUTPUT_DOMAIN,
            "bounded_result_annotation": str(evaluation.bounded_result_annotation),
            "evaluation_scope": EVALUATION_SCOPE,
            "deterministic_result_sha256": evaluation.deterministic_result_sha256,
            "created_at_monotonic_ns": evaluation.evaluated_at_monotonic_ns,
            "expires_at_monotonic_ns": binding.expires_at_monotonic_ns,
            "active_at_creation": True,
            "revocable": True,
            "production_consumer_count": 0,
            "recursive_input_allowed": False,
            "feedback_family_id": None,
            "semantic_label": None,
            "purpose_authority": False,
            "candidate_ordering_authority": False,
            "action_selection_authority": False,
            "memory_write_authority": False,
            "self_state_mutation_authority": False,
            "perception_action_authority": False,
            "output_authority": False,
            "external_control_authority": False,
            "drive_input_used": False,
            "self_state_readback_used": False,
            "source_record_refs": (
                evaluation.specialized_evaluation_id,
                binding.precursor_binding_id,
                signal.instinct_signal_id,
                bundle.evaluation_bundle_id,
            ),
            "source_trace_refs": signal.source_trace_refs,
        },
        id_field="specialized_result_id",
        hash_field="specialized_result_sha256",
        prefix="specialized_result",
    )


def _validate_source_precursor(
    bundle: InstinctEvaluationBundleRecord,
    signal: BoundedInstinctSignalRecord,
    family: SpecializedThoughtRuleFamilyContractRecord,
) -> None:
    if bundle.schema_version != PACKAGE_141_BUNDLE_SCHEMA:
        raise ValueError("blocked_unknown_package_141_bundle_schema")
    if signal.schema_version != PACKAGE_141_SIGNAL_SCHEMA:
        raise ValueError("blocked_unknown_package_141_signal_schema")
    if signal.signal_kind != PACKAGE_141_SIGNAL_KIND or signal.lifetime_scope != PACKAGE_141_SIGNAL_LIFETIME:
        raise ValueError("blocked_invalid_package_141_precursor_kind")
    if not signal.revocable or signal.consumed_by_production_runtime:
        raise ValueError("blocked_ineligible_package_141_precursor")
    if signal.instinct_signal_id not in bundle.instinct_signal_refs:
        raise ValueError("blocked_package_141_precursor_lineage_mismatch")
    if signal.bounded_annotation not in family.input_annotation_allowlist:
        raise ValueError("blocked_precursor_not_allowed_for_specialized_family")


def _family_contract(preflight: Package142Preflight, family_id: str) -> SpecializedThoughtRuleFamilyContractRecord:
    for family in preflight.family_contracts:
        if family.family_id == family_id:
            return family
    raise ValueError("blocked_unknown_specialized_rule_family")


def _eligible_single_bundles(
    bundles: tuple[InstinctEvaluationBundleRecord, ...],
    signals: dict[str, BoundedInstinctSignalRecord],
    annotation: str,
) -> tuple[InstinctEvaluationBundleRecord, ...]:
    return tuple(
        item
        for item in bundles
        if item.schema_version == PACKAGE_141_BUNDLE_SCHEMA
        and item.evaluation_status == "matched_single"
        and item.bounded_annotations == (annotation,)
        and len(item.instinct_signal_refs) == 1
        and item.instinct_signal_refs[0] in signals
        and signals[item.instinct_signal_refs[0]].bounded_annotation == annotation
    )


def _resolve_package_141_database(state_dir: str | Path) -> Path:
    supplied = Path(state_dir).resolve()
    candidates = (
        supplied if supplied.is_file() else None,
        supplied / "package_141.sqlite3",
        supplied / PACKAGE_141_RELATIVE_DATABASE,
    )
    existing = tuple(path for path in candidates if path is not None and path.is_file())
    unique = tuple(dict.fromkeys(existing))
    if len(unique) != 1:
        raise ValueError("blocked_package_141_state_dir_missing_or_ambiguous")
    return unique[0]


def _read_verified_table(database: Path, table: str) -> tuple[dict[str, Any], ...]:
    uri = f"file:{quote(database.as_posix(), safe='/:')}?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True, timeout=30.0)
    connection.row_factory = sqlite3.Row
    try:
        integrity = str(connection.execute("PRAGMA integrity_check").fetchone()[0])
        if integrity != "ok":
            raise RuntimeError("blocked_corrupt_package_141_store")
        rows = connection.execute(
            f"SELECT payload_json, payload_sha256 FROM {table} ORDER BY row_id"
        ).fetchall()
    except sqlite3.Error as error:
        raise RuntimeError(f"blocked_unreadable_package_141_table:{table}") from error
    finally:
        connection.close()
    payloads: list[dict[str, Any]] = []
    for row in rows:
        payload = json.loads(str(row["payload_json"]))
        if str(row["payload_sha256"]) != sha256_payload(payload):
            raise RuntimeError(f"blocked_corrupt_package_141_payload:{table}")
        payloads.append(payload)
    return tuple(payloads)


def _require_single_identity(payloads: tuple[dict[str, Any], ...], id_field: str) -> dict[str, Any]:
    by_id = {str(item[id_field]): item for item in payloads}
    if len(by_id) != 1:
        raise ValueError(f"blocked_ambiguous_package_141_authority:{id_field}")
    return next(iter(by_id.values()))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_external_state_dir(root: Path, state_dir: Path) -> None:
    target = state_dir.resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return
    raise ValueError("Package 142 state_dir must be outside the Git repository")


def _emit(
    event_stream: LocalOperatorEventStream | None,
    event_kind: str,
    source_record_refs: tuple[str, ...],
    source_trace_refs: tuple[str, ...] = (),
) -> None:
    if event_stream is None:
        return
    event_stream.append_event(
        event_kind=event_kind,
        source_record_refs=source_record_refs,
        source_trace_refs=source_trace_refs,
    )
