"""Package 119 milestone audit for the no-Codex fixture growth loop."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_run import (
    LINEAGE_RESULT_SCHEMA_VERSION,
    TwoCycleGrowthLineageResult,
    fixture_payload_for_kind,
    runtime_config_sha256,
)
from ashl_core_v1.runtime.session_learning_evidence_identity import (
    FULL_COMMIT_APPROVAL_SCOPE,
    LearningPipelineEvidenceIdentityBindingRecord,
    SessionLearningEvidenceSnapshot,
    calculate_sha256,
    validate_learning_pipeline_identity_chain,
    validate_session_learning_evidence_snapshot,
)
from ashl_core_v1.runtime.teacher_gated_session_store import STORE_FILENAME
from ashl_core_v1.runtime.trace_envelope import RAW_TRACE_FORBIDDEN_KEYS, TraceEnvelope


AUDIT_SCHEMA_VERSION = "ashl_no_codex_fixture_growth_loop_milestone_audit_v0"
CERTIFICATE_SCHEMA_VERSION = "ashl_no_codex_fixture_growth_loop_milestone_certificate_v0"
MILESTONE_ID = "ashl_v1_no_codex_fixture_embodied_growth_loop_v0"
PACKAGE_COMMITS = ("b87ab76", "d2e940f", "f151867", "30b8d6e")

SAFE_CLAIM = (
    "ASHL Core v1 has completed and audited a bounded, fixture-only, "
    "teacher-gated, cross-process embodied growth loop without Codex or LLM "
    "runtime participation. Cycle 1 committed exact teacher-approved reviewed "
    "interpretation and active working readback; Cycle 2 started in a new "
    "process/runtime/store/session, loaded that readback before event handling, "
    "and consumed it through actual candidate scoring during normal Host Body "
    "internal-action processing."
)
FORBIDDEN_CLAIMS = (
    "general autonomous learning",
    "automatic teacher approval",
    "unbounded long-term growth",
    "real camera perception",
    "real screen perception",
    "real audio perception",
    "semantic vision",
    "object recognition",
    "speech understanding",
    "production action",
    "computer control",
    "first_output",
    "continuous autonomous scheduler",
    "open-ended runtime",
    "Thought Engine completion",
    "GCMC / CL completion",
    "awakening",
    "consciousness",
    "subjective experience",
)
SCOPE_LIMITS = (
    "fixture-only",
    "teacher-gated",
    "bounded",
    "cross-process proof only",
    "no automatic approval",
    "no real sensor perception",
    "no external control",
    "no first_output",
    "no live scheduler",
    "no open-ended autonomy",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _plain(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def _json(value: Any) -> str:
    return json.dumps(_plain(value), ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _loads(value: str | bytes | None, default: Any) -> Any:
    if not value:
        return default
    return json.loads(value)


def _state_dir_fingerprint(state_dir: Path) -> str:
    return calculate_sha256({"state_dir": str(state_dir.resolve())})


@dataclass(frozen=True)
class NoCodexFixtureGrowthLoopMilestoneAuditRecord:
    milestone_audit_id: str
    schema_version: str
    created_at: str
    milestone_id: str
    run_id: str
    state_dir_fingerprint: str
    package_115_runtime_valid: bool
    package_116_commit_valid: bool
    package_117_identity_valid: bool
    package_118_two_cycle_valid: bool
    cycle_one_process_id: str
    cycle_two_process_id: str
    cycle_one_runtime_id: str
    cycle_two_runtime_id: str
    cycle_one_session_id: str
    cycle_two_session_id: str
    process_boundary_valid: bool
    runtime_boundary_valid: bool
    session_boundary_valid: bool
    store_connection_boundary_valid: bool
    fixture_identity_valid: bool
    runtime_config_identity_valid: bool
    base_candidate_set_identity_valid: bool
    exact_teacher_evidence_binding_valid: bool
    teacher_approval_scope_valid: bool
    package_90_92_identity_chain_valid: bool
    interpretation_commit_valid: bool
    working_readback_commit_valid: bool
    cycle_two_readback_loaded_before_event: bool
    cycle_two_readback_evaluated: bool
    cycle_two_matching_rule_found: bool
    cycle_two_candidate_delta_applied: bool
    cycle_two_readback_consumed: bool
    cross_session_lineage_complete: bool
    lineage_reaches_cycle_one_raw_trace: bool
    codex_runtime_call_count: int
    llm_runtime_call_count: int
    network_model_call_count: int
    arbitrary_runtime_subprocess_call_count: int
    dynamic_code_execution_attempt_count: int
    raw_trace_append_only_valid: bool
    raw_trace_unchanged_valid: bool
    raw_trace_unsummarized_valid: bool
    concept_id_absent_from_raw_history: bool
    trace_collision_policy_valid: bool
    cycle_two_auto_approval_detected: bool
    unrestricted_memory_promotion_detected: bool
    external_control_detected: bool
    first_output_detected: bool
    live_scheduler_detected: bool
    open_ended_loop_detected: bool
    evidence_record_ids: tuple[str, ...]
    source_trace_refs: tuple[str, ...]
    passed_criteria: tuple[str, ...]
    blocked_criteria: tuple[str, ...]
    failure_reasons: tuple[str, ...]
    audit_status: str
    safe_claim: str
    forbidden_claims: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "NoCodexFixtureGrowthLoopMilestoneAuditRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class NoCodexFixtureGrowthLoopMilestoneCertificate:
    certificate_id: str
    schema_version: str
    created_at: str
    milestone_id: str
    source_audit_id: str
    source_run_id: str
    package_commits: tuple[str, ...]
    evidence_record_ids: tuple[str, ...]
    source_trace_refs: tuple[str, ...]
    capability_claim: str
    scope_limits: tuple[str, ...]
    certificate_sha256: str

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "NoCodexFixtureGrowthLoopMilestoneCertificate":
        return cls(**dict(data))


class _ReadOnlyStore:
    def __init__(self, state_dir: str | Path) -> None:
        self.state_dir = Path(state_dir)
        self.db_path = self.state_dir / STORE_FILENAME
        if not self.db_path.exists():
            raise FileNotFoundError(f"store database not found: {self.db_path}")

    def connect(self) -> sqlite3.Connection:
        uri = self.db_path.resolve().as_posix()
        connection = sqlite3.connect(f"file:{uri}?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
        return connection

    def payload(self, table: str, where: str, args: tuple[Any, ...]) -> dict[str, Any]:
        connection = self.connect()
        try:
            row = connection.execute(f"SELECT payload_json FROM {table} WHERE {where}", args).fetchone()
        finally:
            connection.close()
        if row is None:
            raise KeyError(f"missing row in {table}: {where}")
        return dict(_loads(row["payload_json"], {}))

    def payloads(self, table: str, where: str, args: tuple[Any, ...], order: str = "created_at") -> tuple[dict[str, Any], ...]:
        connection = self.connect()
        try:
            rows = connection.execute(
                f"SELECT payload_json FROM {table} WHERE {where} ORDER BY {order}",
                args,
            ).fetchall()
        finally:
            connection.close()
        return tuple(dict(_loads(row["payload_json"], {})) for row in rows)

    def rows(self, table: str, where: str, args: tuple[Any, ...], order: str = "created_at") -> tuple[dict[str, Any], ...]:
        connection = self.connect()
        try:
            rows = connection.execute(
                f"SELECT * FROM {table} WHERE {where} ORDER BY {order}",
                args,
            ).fetchall()
        finally:
            connection.close()
        return tuple(dict(row) for row in rows)

    def row(self, table: str, where: str, args: tuple[Any, ...]) -> dict[str, Any]:
        connection = self.connect()
        try:
            row = connection.execute(f"SELECT * FROM {table} WHERE {where}", args).fetchone()
        finally:
            connection.close()
        if row is None:
            raise KeyError(f"missing row in {table}: {where}")
        return dict(row)


def build_no_codex_fixture_growth_loop_milestone_audit(
    *,
    state_dir: str | Path,
    run_id: str,
) -> NoCodexFixtureGrowthLoopMilestoneAuditRecord:
    reader = _ReadOnlyStore(state_dir)
    failure_reasons: list[str] = []
    missing = False
    try:
        run = reader.payload("two_cycle_fixture_growth_runs", "run_id = ?", (run_id,))
        process_receipts = reader.payloads("cycle_process_receipts", "run_id = ?", (run_id,), "cycle_index")
        cycle_one = reader.payload("cycle_one_growth_commit_receipts", "run_id = ?", (run_id,))
        cycle_two = reader.payload("cycle_two_readback_consumption_receipts", "run_id = ?", (run_id,))
    except Exception as error:
        run = {"run_id": run_id}
        process_receipts = tuple()
        cycle_one = {}
        cycle_two = {}
        missing = True
        failure_reasons.append(f"missing_authoritative_evidence:{error}")

    p1 = process_receipts[0] if len(process_receipts) > 0 else {}
    p2 = process_receipts[1] if len(process_receipts) > 1 else {}
    cycle_one_session_id = str(cycle_one.get("session_id") or p1.get("session_id") or "")
    cycle_two_session_id = str(cycle_two.get("session_id") or p2.get("session_id") or "")

    try:
        cycle_one_traces = _trace_envelopes(reader, cycle_one_session_id)
        cycle_two_traces = _trace_envelopes(reader, cycle_two_session_id)
    except Exception as error:
        cycle_one_traces = tuple()
        cycle_two_traces = tuple()
        missing = True
        failure_reasons.append(f"missing_trace_evidence:{error}")

    pending_review = _safe_row(reader, "pending_teacher_reviews", "pending_teacher_review_id = ?", (str(cycle_one.get("pending_teacher_review_id", "")),), failure_reasons)
    teacher_decision = _safe_row(reader, "teacher_decisions", "teacher_decision_id = ?", (str(cycle_one.get("teacher_decision_id", "")),), failure_reasons)
    interpretation_commit = _safe_row(reader, "reviewed_interpretation_commits", "interpretation_commit_id = ?", (str(cycle_one.get("reviewed_interpretation_commit_id", "")),), failure_reasons)
    working_readback_commit = _safe_row(reader, "working_readback_commits", "working_readback_commit_id = ?", (str(cycle_one.get("working_readback_commit_id", "")),), failure_reasons)
    evidence_snapshot_row = _safe_row(reader, "learning_evidence_snapshots", "evidence_snapshot_id = ?", (str(cycle_one.get("evidence_snapshot_id", "")),), failure_reasons)
    teacher_target_bindings = _safe_rows(reader, "teacher_decision_target_bindings", "teacher_decision_id = ?", (str(cycle_one.get("teacher_decision_id", "")),), failure_reasons)
    identity_bindings = _safe_identity_bindings(reader, cycle_one_session_id, failure_reasons)
    session_heads = _safe_rows(
        reader,
        "session_heads",
        "session_id IN (?, ?)",
        (cycle_one_session_id, cycle_two_session_id),
        failure_reasons,
        order="updated_at",
    )
    cycle_one_checkpoints = _safe_rows(reader, "session_checkpoints", "session_id = ?", (cycle_one_session_id,), failure_reasons)
    commit_records = _safe_rows(reader, "session_commit_records", "session_id = ?", (cycle_one_session_id,), failure_reasons)
    profile_rows = _safe_rows(reader, "runtime_capability_profiles", "1 = ?", (1,), failure_reasons)
    if (
        len(process_receipts) < 2
        or not cycle_one
        or not cycle_two
        or not pending_review
        or not teacher_decision
        or not interpretation_commit
        or not working_readback_commit
        or not evidence_snapshot_row
        or not teacher_target_bindings
        or not identity_bindings
    ):
        missing = True
        failure_reasons.append("missing_authoritative_evidence")

    snapshot = _snapshot_from_row(evidence_snapshot_row) if evidence_snapshot_row else None
    snapshot_validation = (
        validate_session_learning_evidence_snapshot(snapshot) if snapshot else {"valid": False}
    )
    identity_chain_validation = (
        validate_learning_pipeline_identity_chain(tuple(identity_bindings))
        if identity_bindings
        else {"valid": False}
    )

    process_boundary_valid = bool(p1 and p2 and p1.get("process_instance_id") != p2.get("process_instance_id") and p1.get("operating_system_pid") != p2.get("operating_system_pid") and p1.get("store_closed") and p2.get("store_closed") and str(p1.get("worker_closed_at", "")) <= str(p2.get("worker_started_at", "")))
    runtime_boundary_valid = bool(p1 and p2 and p1.get("runtime_instance_id") != p2.get("runtime_instance_id"))
    session_boundary_valid = bool(p1 and p2 and p1.get("session_id") != p2.get("session_id"))
    store_connection_boundary_valid = bool(p1 and p2 and p1.get("store_connection_id") != p2.get("store_connection_id"))

    fixture_identity_valid = bool(
        run.get("fixture_kind") == cycle_two.get("current_fixture_kind")
        and run.get("fixture_payload_sha256") == cycle_two.get("current_fixture_payload_sha256")
        and run.get("fixture_payload_sha256") == calculate_sha256(fixture_payload_for_kind(str(run.get("fixture_kind"))))
    )
    runtime_config_identity_valid = bool(
        run.get("runtime_config_sha256") == cycle_two.get("current_runtime_config_sha256")
        and run.get("runtime_config_sha256") == runtime_config_sha256()
    )
    base_candidate_set_identity_valid = bool(
        run.get("base_candidate_set_sha256")
        and run.get("base_candidate_set_sha256") != "pending"
        and run.get("base_candidate_set_sha256") == cycle_two.get("current_base_candidate_set_sha256")
    )

    package_115_runtime_valid = _package_115_runtime_valid(
        cycle_one_traces=cycle_one_traces,
        checkpoints=cycle_one_checkpoints,
        pending_review=pending_review,
    )
    package_116_commit_valid = _package_116_commit_valid(
        session_heads=session_heads,
        commit_records=commit_records,
        teacher_decision=teacher_decision,
        interpretation_commit=interpretation_commit,
        working_readback_commit=working_readback_commit,
    )
    exact_teacher_evidence_binding_valid = bool(
        snapshot
        and teacher_decision
        and teacher_target_bindings
        and pending_review
        and pending_review.get("evidence_identity_sha256") == snapshot.evidence_identity_sha256
        and teacher_decision.get("target_evidence_identity_sha256") == snapshot.evidence_identity_sha256
        and teacher_decision.get("target_evidence_snapshot_id") == snapshot.evidence_snapshot_id
        and teacher_target_bindings[0].get("evidence_identity_sha256") == snapshot.evidence_identity_sha256
    )
    teacher_approval_scope_valid = bool(
        teacher_decision
        and teacher_decision.get("decision") == "approved"
        and teacher_decision.get("approval_scope") == FULL_COMMIT_APPROVAL_SCOPE
        and int(teacher_decision.get("scope_sufficient_for_requested_operation", 0)) == 1
    )
    interpretation_commit_valid = bool(
        interpretation_commit
        and interpretation_commit.get("commit_status") == "active"
        and interpretation_commit.get("evidence_identity_sha256") == cycle_one.get("evidence_identity_sha256")
    )
    working_readback_commit_valid = bool(
        working_readback_commit
        and int(working_readback_commit.get("active_for_future_sessions", 0)) == 1
        and working_readback_commit.get("evidence_identity_sha256") == cycle_one.get("evidence_identity_sha256")
        and working_readback_commit.get("source_reviewed_interpretation_commit_id") == cycle_one.get("reviewed_interpretation_commit_id")
    )
    package_117_identity_valid = bool(
        snapshot_validation.get("valid")
        and exact_teacher_evidence_binding_valid
        and teacher_approval_scope_valid
        and identity_chain_validation.get("valid")
        and interpretation_commit_valid
        and working_readback_commit_valid
        and profile_rows
    )
    cycle_two_readback_loaded_before_event = bool(cycle_two.get("loaded_before_event_processing"))
    cycle_two_readback_evaluated = bool(cycle_two.get("readback_evaluated"))
    cycle_two_matching_rule_found = bool(cycle_two.get("matching_rule_found"))
    cycle_two_candidate_delta_applied = bool(cycle_two.get("candidate_delta_applied") and int(cycle_two.get("nonzero_delta_count", 0)) > 0)
    cycle_two_readback_consumed = bool(cycle_two.get("readback_consumed"))
    lineage = _lineage_result_from_records(reader, run_id, run, cycle_one, cycle_two, process_receipts)
    package_118_two_cycle_valid = bool(
        run.get("run_status") == "completed"
        and process_boundary_valid
        and runtime_boundary_valid
        and session_boundary_valid
        and store_connection_boundary_valid
        and cycle_two_readback_loaded_before_event
        and cycle_two_readback_evaluated
        and cycle_two_matching_rule_found
        and cycle_two_candidate_delta_applied
        and cycle_two_readback_consumed
        and lineage.valid
    )
    raw_trace_append_only_valid = _raw_trace_append_only_valid(cycle_one_traces, cycle_two_traces)
    raw_trace_unchanged_valid = _raw_trace_unchanged_valid(cycle_one_traces, cycle_two_traces)
    raw_trace_unsummarized_valid = _raw_trace_unsummarized_valid(cycle_one_traces, cycle_two_traces)
    concept_id_absent_from_raw_history = _concept_id_absent(cycle_one_traces, cycle_two_traces)
    trace_collision_policy_valid = _trace_collision_policy_valid(reader)
    counters = _counter_totals(process_receipts)

    audit_payloads: tuple[Any, ...] = (
        run,
        process_receipts,
        cycle_one,
        cycle_two,
        pending_review,
        teacher_decision,
        interpretation_commit,
        working_readback_commit,
        evidence_snapshot_row,
        teacher_target_bindings,
        tuple(item.to_dict() for item in identity_bindings),
        tuple(item.to_dict() for item in cycle_one_traces),
        tuple(item.to_dict() for item in cycle_two_traces),
    )
    cycle_two_auto_approval_detected = _cycle_two_auto_approval_detected(reader, cycle_two_session_id)
    unrestricted_memory_promotion_detected = _truthy_forbidden_flag(
        audit_payloads,
        {"unrestricted_memory_promotion_detected", "unrestricted_memory_promotion_created", "unrestricted_memory_promotion_allowed"},
    )
    external_control_detected = _truthy_forbidden_flag(
        audit_payloads,
        {"external_control_detected", "external_control_created", "external_control_allowed", "allow_external_control"},
    )
    first_output_detected = _truthy_forbidden_flag(
        audit_payloads,
        {"first_output_detected", "first_output_created", "first_output_allowed", "allow_first_output"},
    )
    live_scheduler_detected = _truthy_forbidden_flag(
        audit_payloads,
        {"live_scheduler_detected", "live_scheduler_created", "live_scheduler_allowed", "allow_live_scheduler"},
    )
    open_ended_loop_detected = _truthy_forbidden_flag(
        audit_payloads,
        {"open_ended_loop_detected", "open_ended_loop_created", "open_ended_loop_allowed"},
    )

    checks = {
        "package_115_runtime_valid": package_115_runtime_valid,
        "package_116_commit_valid": package_116_commit_valid,
        "package_117_identity_valid": package_117_identity_valid,
        "package_118_two_cycle_valid": package_118_two_cycle_valid,
        "process_boundary_valid": process_boundary_valid,
        "runtime_boundary_valid": runtime_boundary_valid,
        "session_boundary_valid": session_boundary_valid,
        "store_connection_boundary_valid": store_connection_boundary_valid,
        "fixture_identity_valid": fixture_identity_valid,
        "runtime_config_identity_valid": runtime_config_identity_valid,
        "base_candidate_set_identity_valid": base_candidate_set_identity_valid,
        "exact_teacher_evidence_binding_valid": exact_teacher_evidence_binding_valid,
        "teacher_approval_scope_valid": teacher_approval_scope_valid,
        "package_90_92_identity_chain_valid": bool(identity_chain_validation.get("valid")),
        "interpretation_commit_valid": interpretation_commit_valid,
        "working_readback_commit_valid": working_readback_commit_valid,
        "cycle_two_readback_loaded_before_event": cycle_two_readback_loaded_before_event,
        "cycle_two_readback_evaluated": cycle_two_readback_evaluated,
        "cycle_two_matching_rule_found": cycle_two_matching_rule_found,
        "cycle_two_candidate_delta_applied": cycle_two_candidate_delta_applied,
        "cycle_two_readback_consumed": cycle_two_readback_consumed,
        "cross_session_lineage_complete": lineage.valid,
        "lineage_reaches_cycle_one_raw_trace": lineage.source_trace_refs_preserved,
        "no_codex_runtime_calls": counters["codex_runtime_call_count"] == 0,
        "no_llm_runtime_calls": counters["llm_runtime_call_count"] == 0,
        "no_network_model_calls": counters["network_model_call_count"] == 0,
        "no_arbitrary_runtime_subprocess_calls": counters["arbitrary_runtime_subprocess_call_count"] == 0,
        "no_dynamic_code_execution_attempts": counters["dynamic_code_execution_attempt_count"] == 0,
        "raw_trace_append_only_valid": raw_trace_append_only_valid,
        "raw_trace_unchanged_valid": raw_trace_unchanged_valid,
        "raw_trace_unsummarized_valid": raw_trace_unsummarized_valid,
        "concept_id_absent_from_raw_history": concept_id_absent_from_raw_history,
        "trace_collision_policy_valid": trace_collision_policy_valid,
        "no_cycle_two_auto_approval": not cycle_two_auto_approval_detected,
        "no_unrestricted_memory_promotion": not unrestricted_memory_promotion_detected,
        "no_external_control": not external_control_detected,
        "no_first_output": not first_output_detected,
        "no_live_scheduler": not live_scheduler_detected,
        "no_open_ended_loop": not open_ended_loop_detected,
    }
    blocked_criteria = tuple(key for key, valid in checks.items() if not valid)
    passed_criteria = tuple(key for key, valid in checks.items() if valid)
    if blocked_criteria:
        failure_reasons.extend(blocked_criteria)
    audit_status = _audit_status(
        missing=missing,
        checks=checks,
        counters=counters,
        cycle_two_auto_approval_detected=cycle_two_auto_approval_detected,
        external_control_detected=external_control_detected,
        first_output_detected=first_output_detected,
        live_scheduler_detected=live_scheduler_detected,
        open_ended_loop_detected=open_ended_loop_detected,
    )
    evidence_record_ids = _evidence_record_ids(run, process_receipts, cycle_one, cycle_two, pending_review, teacher_decision, evidence_snapshot_row, interpretation_commit, working_readback_commit)
    source_trace_refs = tuple(dict.fromkeys(tuple(cycle_two.get("source_trace_refs", ())) + tuple(cycle_one.get("source_trace_refs", ()))))
    return NoCodexFixtureGrowthLoopMilestoneAuditRecord(
        milestone_audit_id=f"no_codex_fixture_growth_loop_milestone_audit:{run_id}:{uuid4().hex[:8]}",
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        milestone_id=MILESTONE_ID,
        run_id=run_id,
        state_dir_fingerprint=_state_dir_fingerprint(Path(state_dir)),
        package_115_runtime_valid=package_115_runtime_valid,
        package_116_commit_valid=package_116_commit_valid,
        package_117_identity_valid=package_117_identity_valid,
        package_118_two_cycle_valid=package_118_two_cycle_valid,
        cycle_one_process_id=str(p1.get("process_instance_id", "")),
        cycle_two_process_id=str(p2.get("process_instance_id", "")),
        cycle_one_runtime_id=str(p1.get("runtime_instance_id", "")),
        cycle_two_runtime_id=str(p2.get("runtime_instance_id", "")),
        cycle_one_session_id=cycle_one_session_id,
        cycle_two_session_id=cycle_two_session_id,
        process_boundary_valid=process_boundary_valid,
        runtime_boundary_valid=runtime_boundary_valid,
        session_boundary_valid=session_boundary_valid,
        store_connection_boundary_valid=store_connection_boundary_valid,
        fixture_identity_valid=fixture_identity_valid,
        runtime_config_identity_valid=runtime_config_identity_valid,
        base_candidate_set_identity_valid=base_candidate_set_identity_valid,
        exact_teacher_evidence_binding_valid=exact_teacher_evidence_binding_valid,
        teacher_approval_scope_valid=teacher_approval_scope_valid,
        package_90_92_identity_chain_valid=bool(identity_chain_validation.get("valid")),
        interpretation_commit_valid=interpretation_commit_valid,
        working_readback_commit_valid=working_readback_commit_valid,
        cycle_two_readback_loaded_before_event=cycle_two_readback_loaded_before_event,
        cycle_two_readback_evaluated=cycle_two_readback_evaluated,
        cycle_two_matching_rule_found=cycle_two_matching_rule_found,
        cycle_two_candidate_delta_applied=cycle_two_candidate_delta_applied,
        cycle_two_readback_consumed=cycle_two_readback_consumed,
        cross_session_lineage_complete=lineage.valid,
        lineage_reaches_cycle_one_raw_trace=lineage.source_trace_refs_preserved,
        codex_runtime_call_count=counters["codex_runtime_call_count"],
        llm_runtime_call_count=counters["llm_runtime_call_count"],
        network_model_call_count=counters["network_model_call_count"],
        arbitrary_runtime_subprocess_call_count=counters["arbitrary_runtime_subprocess_call_count"],
        dynamic_code_execution_attempt_count=counters["dynamic_code_execution_attempt_count"],
        raw_trace_append_only_valid=raw_trace_append_only_valid,
        raw_trace_unchanged_valid=raw_trace_unchanged_valid,
        raw_trace_unsummarized_valid=raw_trace_unsummarized_valid,
        concept_id_absent_from_raw_history=concept_id_absent_from_raw_history,
        trace_collision_policy_valid=trace_collision_policy_valid,
        cycle_two_auto_approval_detected=cycle_two_auto_approval_detected,
        unrestricted_memory_promotion_detected=unrestricted_memory_promotion_detected,
        external_control_detected=external_control_detected,
        first_output_detected=first_output_detected,
        live_scheduler_detected=live_scheduler_detected,
        open_ended_loop_detected=open_ended_loop_detected,
        evidence_record_ids=evidence_record_ids,
        source_trace_refs=source_trace_refs,
        passed_criteria=passed_criteria,
        blocked_criteria=blocked_criteria,
        failure_reasons=tuple(dict.fromkeys(failure_reasons)),
        audit_status=audit_status,
        safe_claim=SAFE_CLAIM if audit_status.startswith("passed_") else "",
        forbidden_claims=FORBIDDEN_CLAIMS,
    )


def issue_no_codex_fixture_growth_loop_milestone_certificate(
    *,
    audit: NoCodexFixtureGrowthLoopMilestoneAuditRecord,
    output_path: str | Path,
) -> NoCodexFixtureGrowthLoopMilestoneCertificate:
    if audit.audit_status != "passed_no_codex_fixture_growth_loop_milestone":
        raise ValueError("certificate requires passed audit")
    data = {
        "certificate_id": f"no_codex_fixture_growth_loop_certificate:{audit.run_id}:{uuid4().hex[:8]}",
        "schema_version": CERTIFICATE_SCHEMA_VERSION,
        "created_at": _now(),
        "milestone_id": MILESTONE_ID,
        "source_audit_id": audit.milestone_audit_id,
        "source_run_id": audit.run_id,
        "package_commits": PACKAGE_COMMITS,
        "evidence_record_ids": audit.evidence_record_ids,
        "source_trace_refs": audit.source_trace_refs,
        "capability_claim": SAFE_CLAIM,
        "scope_limits": SCOPE_LIMITS,
        "certificate_sha256": "",
    }
    data["certificate_sha256"] = _certificate_hash(data)
    certificate = NoCodexFixtureGrowthLoopMilestoneCertificate(**data)
    path = Path(output_path)
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(certificate.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return certificate


def validate_no_codex_fixture_growth_loop_milestone_certificate(
    certificate_path: str | Path,
) -> dict[str, object]:
    try:
        data = json.loads(Path(certificate_path).read_text(encoding="utf-8"))
        certificate = NoCodexFixtureGrowthLoopMilestoneCertificate.from_dict(data)
    except Exception as error:
        return {"valid": False, "status": "invalid_certificate", "reasons": (str(error),)}
    reasons: list[str] = []
    if certificate.schema_version != CERTIFICATE_SCHEMA_VERSION:
        reasons.append("schema_version_mismatch")
    if certificate.milestone_id != MILESTONE_ID:
        reasons.append("milestone_id_mismatch")
    if tuple(certificate.package_commits) != PACKAGE_COMMITS:
        reasons.append("package_commits_mismatch")
    if not certificate.evidence_record_ids:
        reasons.append("missing_evidence_record_ids")
    if not certificate.source_trace_refs:
        reasons.append("missing_source_trace_refs")
    if "runtime authority" in certificate.capability_claim.lower():
        reasons.append("certificate_grants_runtime_authority")
    if _certificate_hash(certificate.to_dict()) != certificate.certificate_sha256:
        reasons.append("certificate_hash_mismatch")
    return {
        "valid": not reasons,
        "status": "certificate_valid" if not reasons else "certificate_invalid",
        "reasons": tuple(reasons),
        "certificate_sha256": certificate.certificate_sha256,
    }


def show_no_codex_fixture_growth_loop_evidence(state_dir: str | Path, run_id: str) -> dict[str, object]:
    reader = _ReadOnlyStore(state_dir)
    return {
        "run": reader.payload("two_cycle_fixture_growth_runs", "run_id = ?", (run_id,)),
        "process_receipts": reader.payloads("cycle_process_receipts", "run_id = ?", (run_id,), "cycle_index"),
        "cycle_one_commit_receipt": reader.payload("cycle_one_growth_commit_receipts", "run_id = ?", (run_id,)),
        "cycle_two_consumption_receipt": reader.payload("cycle_two_readback_consumption_receipts", "run_id = ?", (run_id,)),
    }


def show_no_codex_fixture_growth_loop_lineage(state_dir: str | Path, run_id: str) -> dict[str, object]:
    audit = build_no_codex_fixture_growth_loop_milestone_audit(state_dir=state_dir, run_id=run_id)
    return {
        "cross_session_lineage_complete": audit.cross_session_lineage_complete,
        "lineage_reaches_cycle_one_raw_trace": audit.lineage_reaches_cycle_one_raw_trace,
        "evidence_record_ids": audit.evidence_record_ids,
        "source_trace_refs": audit.source_trace_refs,
        "blocked_criteria": audit.blocked_criteria,
    }


def _certificate_hash(data: dict[str, Any]) -> str:
    return calculate_sha256({key: value for key, value in data.items() if key not in {"created_at", "certificate_sha256"}})


def _safe_row(reader: _ReadOnlyStore, table: str, where: str, args: tuple[Any, ...], failures: list[str]) -> dict[str, Any]:
    try:
        return reader.row(table, where, args)
    except Exception as error:
        failures.append(f"missing_{table}:{error}")
        return {}


def _safe_rows(
    reader: _ReadOnlyStore,
    table: str,
    where: str,
    args: tuple[Any, ...],
    failures: list[str],
    order: str = "created_at",
) -> tuple[dict[str, Any], ...]:
    try:
        return reader.rows(table, where, args, order=order)
    except Exception as error:
        failures.append(f"missing_{table}:{error}")
        return tuple()


def _safe_identity_bindings(reader: _ReadOnlyStore, session_id: str, failures: list[str]) -> tuple[LearningPipelineEvidenceIdentityBindingRecord, ...]:
    try:
        rows = reader.rows("learning_pipeline_identity_bindings", "session_id = ?", (session_id,))
        return tuple(
            LearningPipelineEvidenceIdentityBindingRecord(
                binding_id=row["binding_id"],
                schema_version="ashl_learning_pipeline_evidence_identity_binding_v0",
                created_at=row["created_at"],
                session_id=row["session_id"],
                evidence_snapshot_id=row["evidence_snapshot_id"],
                evidence_identity_sha256=row["evidence_identity_sha256"],
                pipeline_stage=row["pipeline_stage"],
                target_record_kind=row["target_record_kind"],
                target_record_id=row["target_record_id"],
                source_binding_id=row["source_binding_id"],
                source_trace_refs=tuple(_loads(row["source_trace_refs_json"], [])),
                identity_preserved=True,
                validator_passed=bool(row["validator_passed"]),
            )
            for row in rows
        )
    except Exception as error:
        failures.append(f"missing_identity_bindings:{error}")
        return tuple()


def _trace_envelopes(reader: _ReadOnlyStore, session_id: str) -> tuple[TraceEnvelope, ...]:
    if not session_id:
        return tuple()
    rows = reader.rows("trace_envelopes", "session_id = ?", (session_id,), "sequence_index")
    return tuple(
        TraceEnvelope(
            trace_id=row["trace_id"],
            trace_schema_version=row["trace_schema_version"],
            session_id=row["session_id"],
            event_id=row["event_id"],
            parent_event_id=row["parent_event_id"],
            root_event_id=row["root_event_id"],
            sequence_index=int(row["sequence_index"]),
            monotonic_tick=int(row["monotonic_tick"]),
            nesting_depth=int(row["nesting_depth"]),
            source_line=row["source_line"],
            source_module=row["source_module"],
            record_kind=row["record_kind"],
            record_id=row["record_id"],
            trace_layer=row["trace_layer"],
            payload_schema=row["payload_schema"],
            payload_snapshot=dict(_loads(row["payload_snapshot_json"], {})),
            source_trace_refs=tuple(_loads(row["source_trace_refs_json"], [])),
            source_record_refs=tuple(_loads(row["source_record_refs_json"], [])),
            created_at=row["created_at"],
            append_only=bool(row["append_only"]),
            time_aligned=bool(row["time_aligned"]),
        )
        for row in rows
    )


def _snapshot_from_row(row: dict[str, Any]) -> SessionLearningEvidenceSnapshot | None:
    if not row:
        return None
    payload = dict(_loads(row["canonical_payload_json"], {}))
    return SessionLearningEvidenceSnapshot(
        evidence_snapshot_id=row["evidence_snapshot_id"],
        schema_version="ashl_session_learning_evidence_snapshot_v0",
        created_at=row["created_at"],
        session_id=row["session_id"],
        root_event_id=row["root_event_id"],
        source_event_id=row["source_event_id"],
        source_learning_evidence_packet_id=str(payload.get("source_learning_evidence_packet_id", "")),
        source_learning_feedback_mapping_id=str(payload.get("source_learning_feedback_mapping_id", "")),
        source_learning_feedback_bridge_id=str(payload.get("source_learning_feedback_bridge_id", "")),
        source_existing_review_adapter_id=str(payload.get("source_existing_review_adapter_id", "")),
        evidence_kind=row["evidence_kind"],
        evidence_theme=row["evidence_theme"],
        feedback_candidate_kind=row["feedback_candidate_kind"],
        feedback_candidate_scope=row["feedback_candidate_scope"],
        evidence_summary=str(payload.get("evidence_summary", "")),
        canonical_evidence_payload=payload,
        source_record_refs=tuple(_loads(row["source_record_refs_json"], [])),
        source_trace_refs=tuple(_loads(row["source_trace_refs_json"], [])),
        canonical_payload_sha256=row["canonical_payload_sha256"],
        evidence_identity_sha256=row["evidence_identity_sha256"],
        immutable_snapshot=bool(row["immutable_snapshot"]),
        teacher_review_required=True,
        contains_raw_sensor_payload=False,
        contains_interpreted_memory=False,
    )


def _package_115_runtime_valid(
    *,
    cycle_one_traces: tuple[TraceEnvelope, ...],
    checkpoints: tuple[dict[str, Any], ...],
    pending_review: dict[str, Any],
) -> bool:
    kinds = {item.record_kind for item in cycle_one_traces}
    return all(
        (
            "HostBodyEventRecord" in kinds,
            "HostBodyRuntimeEventFrameBridgeRecord" in kinds,
            "HostBodyInternalActionChoiceRecord" in kinds,
            "InternalActionHomeSurfaceLinkTraceRecord" in kinds,
            "HostBodyLearningEvidencePacketRecord" in kinds,
            "PendingTeacherReviewRecord" in kinds,
            any(row.get("session_status") == "waiting_teacher_review" for row in checkpoints),
            bool(pending_review),
        )
    )


def _package_116_commit_valid(
    *,
    session_heads: tuple[dict[str, Any], ...],
    commit_records: tuple[dict[str, Any], ...],
    teacher_decision: dict[str, Any],
    interpretation_commit: dict[str, Any],
    working_readback_commit: dict[str, Any],
) -> bool:
    return all(
        (
            any(row.get("current_status") == "committed" for row in session_heads),
            bool(commit_records),
            teacher_decision.get("decision") == "approved",
            teacher_decision.get("decision_source") == "teacher_interface",
            bool(interpretation_commit),
            bool(working_readback_commit),
        )
    )


def _lineage_result_from_records(
    reader: _ReadOnlyStore,
    run_id: str,
    run: dict[str, Any],
    cycle_one: dict[str, Any],
    cycle_two: dict[str, Any],
    process_receipts: tuple[dict[str, Any], ...],
) -> TwoCycleGrowthLineageResult:
    reasons: list[str] = []
    process_boundary_valid = (
        len(process_receipts) >= 2
        and process_receipts[0].get("process_instance_id") != process_receipts[1].get("process_instance_id")
        and process_receipts[0].get("runtime_instance_id") != process_receipts[1].get("runtime_instance_id")
        and process_receipts[0].get("store_connection_id") != process_receipts[1].get("store_connection_id")
        and process_receipts[0].get("session_id") != process_receipts[1].get("session_id")
    )
    readback_commit_continuity_valid = bool(cycle_one.get("working_readback_commit_id") in tuple(cycle_two.get("loaded_working_readback_commit_ids", ())))
    readback_consumption_valid = bool(cycle_two.get("readback_loaded") and cycle_two.get("readback_evaluated") and cycle_two.get("matching_rule_found") and cycle_two.get("candidate_delta_applied") and cycle_two.get("readback_consumed"))
    evidence_identity_preserved = bool(cycle_one.get("evidence_identity_sha256") in tuple(cycle_two.get("loaded_evidence_identity_hashes", ())))
    source_trace_refs_preserved = _trace_refs_reach_raw_trace(
        reader=reader,
        session_id=str(cycle_one.get("session_id", "")),
        trace_refs=tuple(cycle_two.get("source_trace_refs", ())),
    )
    if not source_trace_refs_preserved:
        reasons.append("lineage_does_not_reach_cycle_one_raw_trace")
    valid = bool(run.get("run_status") == "completed" and cycle_one.get("session_committed") and process_boundary_valid and readback_commit_continuity_valid and readback_consumption_valid and evidence_identity_preserved and source_trace_refs_preserved)
    return TwoCycleGrowthLineageResult(
        lineage_result_id=f"two_cycle_growth_lineage_result:{run_id}:audit:{uuid4().hex[:8]}",
        schema_version=LINEAGE_RESULT_SCHEMA_VERSION,
        created_at=_now(),
        run_id=run_id,
        valid=valid,
        cycle_one_committed=bool(cycle_one.get("session_committed")),
        process_boundary_valid=process_boundary_valid,
        readback_commit_continuity_valid=readback_commit_continuity_valid,
        readback_consumption_valid=readback_consumption_valid,
        evidence_identity_preserved=evidence_identity_preserved,
        source_trace_refs_preserved=source_trace_refs_preserved,
        no_codex_runtime_calls=True,
        status="two_cycle_growth_lineage_valid" if valid else "blocked_two_cycle_growth_lineage",
        reasons=tuple(reasons),
    )


def _trace_refs_reach_raw_trace(
    *,
    reader: _ReadOnlyStore,
    session_id: str,
    trace_refs: tuple[str, ...],
) -> bool:
    traces = {item.trace_id: item for item in _trace_envelopes(reader, session_id)}
    pending = list(trace_refs)
    seen: set[str] = set()
    while pending:
        trace_id = pending.pop()
        if trace_id in seen:
            continue
        seen.add(trace_id)
        envelope = traces.get(trace_id)
        if envelope is None:
            continue
        if envelope.trace_layer == "raw":
            return True
        pending.extend(ref for ref in envelope.source_trace_refs if ref not in seen)
    return False


def _counter_totals(process_receipts: tuple[dict[str, Any], ...]) -> dict[str, int]:
    return {
        "codex_runtime_call_count": sum(int(item.get("codex_runtime_call_count", 0)) for item in process_receipts),
        "llm_runtime_call_count": sum(int(item.get("llm_runtime_call_count", 0)) for item in process_receipts),
        "network_model_call_count": sum(int(item.get("network_model_call_count", 0)) for item in process_receipts),
        "arbitrary_runtime_subprocess_call_count": sum(int(item.get("arbitrary_runtime_subprocess_call_count", 0)) for item in process_receipts),
        "dynamic_code_execution_attempt_count": sum(int(item.get("dynamic_code_execution_attempt_count", 0)) for item in process_receipts),
    }


def _raw_trace_append_only_valid(*trace_groups: tuple[TraceEnvelope, ...]) -> bool:
    for traces in trace_groups:
        sequences = [item.sequence_index for item in traces]
        if sequences != list(range(len(sequences))):
            return False
        if any(not item.append_only or not item.time_aligned for item in traces):
            return False
    return True


def _raw_trace_unchanged_valid(*trace_groups: tuple[TraceEnvelope, ...]) -> bool:
    for traces in trace_groups:
        raw_ids = [item.trace_id for item in traces if item.trace_layer == "raw"]
        if len(raw_ids) != len(set(raw_ids)):
            return False
    return True


def _raw_trace_unsummarized_valid(*trace_groups: tuple[TraceEnvelope, ...]) -> bool:
    for traces in trace_groups:
        for item in traces:
            if item.trace_layer == "raw" and _contains_key_fragment(item.payload_snapshot, "summary"):
                return False
    return True


def _concept_id_absent(*trace_groups: tuple[TraceEnvelope, ...]) -> bool:
    for traces in trace_groups:
        for item in traces:
            if item.trace_layer == "raw" and _contains_any_key(item.payload_snapshot, RAW_TRACE_FORBIDDEN_KEYS | {"concept_id"}):
                return False
    return True


def _trace_collision_policy_valid(reader: _ReadOnlyStore) -> bool:
    connection = reader.connect()
    try:
        rows = connection.execute(
            "SELECT trace_id, COUNT(*) AS count FROM trace_envelopes GROUP BY trace_id HAVING count > 1"
        ).fetchall()
    finally:
        connection.close()
    return len(rows) == 0


def _cycle_two_auto_approval_detected(reader: _ReadOnlyStore, session_id: str) -> bool:
    if not session_id:
        return False
    decisions = reader.rows("teacher_decisions", "session_id = ?", (session_id,))
    return bool(decisions)


def _evidence_record_ids(*records: Any) -> tuple[str, ...]:
    ids: list[str] = []
    for record in records:
        if isinstance(record, (list, tuple)):
            ids.extend(_evidence_record_ids(*record))
            continue
        if not isinstance(record, dict):
            continue
        for key, value in record.items():
            if key.endswith("_id") and value:
                ids.append(str(value))
    return tuple(dict.fromkeys(ids))


def _contains_key_fragment(value: Any, fragment: str) -> bool:
    if isinstance(value, dict):
        return any(fragment in str(key) or _contains_key_fragment(item, fragment) for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return any(_contains_key_fragment(item, fragment) for item in value)
    return False


def _contains_any_key(value: Any, keys: set[str]) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key) in keys or _contains_any_key(item, keys):
                return True
    if isinstance(value, (list, tuple)):
        return any(_contains_any_key(item, keys) for item in value)
    return False


def _truthy_forbidden_flag(value: Any, keys: set[str]) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key) in keys and bool(item):
                return True
            if _truthy_forbidden_flag(item, keys):
                return True
        return False
    if isinstance(value, (list, tuple)):
        return any(_truthy_forbidden_flag(item, keys) for item in value)
    return False


def _audit_status(
    *,
    missing: bool,
    checks: dict[str, bool],
    counters: dict[str, int],
    cycle_two_auto_approval_detected: bool,
    external_control_detected: bool,
    first_output_detected: bool,
    live_scheduler_detected: bool,
    open_ended_loop_detected: bool,
) -> str:
    if missing:
        return "blocked_missing_authoritative_evidence"
    mapping = (
        ("process_boundary_valid", "blocked_process_boundary_invalid"),
        ("session_boundary_valid", "blocked_session_reuse"),
        ("runtime_boundary_valid", "blocked_runtime_reuse"),
        ("store_connection_boundary_valid", "blocked_store_connection_reuse"),
        ("fixture_identity_valid", "blocked_fixture_identity_mismatch"),
        ("runtime_config_identity_valid", "blocked_runtime_config_mismatch"),
        ("base_candidate_set_identity_valid", "blocked_candidate_set_mismatch"),
        ("exact_teacher_evidence_binding_valid", "blocked_teacher_binding_invalid"),
        ("teacher_approval_scope_valid", "blocked_approval_scope_invalid"),
        ("package_90_92_identity_chain_valid", "blocked_pipeline_identity_invalid"),
        ("interpretation_commit_valid", "blocked_interpretation_commit_invalid"),
        ("working_readback_commit_valid", "blocked_working_readback_commit_invalid"),
        ("cycle_two_readback_loaded_before_event", "blocked_readback_loaded_after_event"),
        ("cycle_two_readback_evaluated", "blocked_readback_not_evaluated"),
        ("cycle_two_matching_rule_found", "blocked_readback_no_matching_rule"),
        ("cycle_two_candidate_delta_applied", "blocked_candidate_delta_missing"),
        ("cycle_two_readback_consumed", "blocked_readback_not_consumed"),
        ("cross_session_lineage_complete", "blocked_lineage_incomplete"),
        ("lineage_reaches_cycle_one_raw_trace", "blocked_lineage_incomplete"),
        ("raw_trace_append_only_valid", "blocked_raw_trace_mutation"),
        ("raw_trace_unchanged_valid", "blocked_raw_trace_mutation"),
        ("raw_trace_unsummarized_valid", "blocked_raw_trace_summarization"),
        ("concept_id_absent_from_raw_history", "blocked_concept_id_in_raw_history"),
        ("trace_collision_policy_valid", "blocked_trace_collision_policy"),
        ("package_115_runtime_valid", "blocked_package_115_runtime_invalid"),
        ("package_116_commit_valid", "blocked_package_116_commit_invalid"),
        ("package_117_identity_valid", "blocked_package_117_identity_invalid"),
        ("package_118_two_cycle_valid", "blocked_package_118_two_cycle_invalid"),
    )
    for key, status in mapping:
        if not checks.get(key, False):
            return status
    if counters["codex_runtime_call_count"]:
        return "blocked_codex_runtime_call"
    if counters["llm_runtime_call_count"]:
        return "blocked_llm_runtime_call"
    if counters["network_model_call_count"]:
        return "blocked_network_model_call"
    if counters["arbitrary_runtime_subprocess_call_count"]:
        return "blocked_arbitrary_runtime_subprocess"
    if counters["dynamic_code_execution_attempt_count"]:
        return "blocked_dynamic_code_execution"
    if cycle_two_auto_approval_detected:
        return "blocked_cycle_two_auto_approval"
    if external_control_detected:
        return "blocked_external_control"
    if first_output_detected:
        return "blocked_first_output"
    if live_scheduler_detected:
        return "blocked_live_scheduler"
    if open_ended_loop_detected:
        return "blocked_open_ended_loop"
    return "passed_no_codex_fixture_growth_loop_milestone"
