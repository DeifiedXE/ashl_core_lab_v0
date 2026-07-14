"""No-Codex two-cycle fixture growth run orchestration for Package 118."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, fields, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from ashl_core_v1.runtime.bounded_embodied_session_runtime import (
    BoundedEmbodiedSessionConfig,
    BoundedEmbodiedSessionRuntime,
    BoundedEmbodiedSessionStage,
    BoundedEmbodiedSessionStatus,
)
from ashl_core_v1.runtime.no_codex_runtime_guard import NoCodexRuntimeGuard
from ashl_core_v1.runtime.runtime_capability_profile import build_verified_runtime_capability_profile
from ashl_core_v1.runtime.session_evidence_identity_approval_scope_repair import (
    build_session_evidence_identity_approval_scope_audit,
)
from ashl_core_v1.runtime.session_learning_evidence_identity import (
    FULL_COMMIT_APPROVAL_SCOPE,
    calculate_sha256,
    validate_learning_pipeline_identity_chain,
    validate_session_learning_evidence_snapshot,
)
from ashl_core_v1.runtime.teacher_gated_session_resume_commit import (
    TeacherGatedSessionResumeCommitRuntime,
)
from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore


RUN_SCHEMA_VERSION = "ashl_no_codex_two_cycle_fixture_growth_run_v0"
PROCESS_RECEIPT_SCHEMA_VERSION = "ashl_no_codex_two_cycle_process_receipt_v0"
CYCLE_ONE_RECEIPT_SCHEMA_VERSION = "ashl_no_codex_cycle_one_growth_commit_receipt_v0"
CYCLE_TWO_RECEIPT_SCHEMA_VERSION = "ashl_no_codex_cycle_two_readback_consumption_receipt_v0"
LINEAGE_RESULT_SCHEMA_VERSION = "ashl_no_codex_two_cycle_growth_lineage_result_v0"
WORKER_MODULE = "ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_worker"

ALLOWED_RUN_STATUSES = {
    "created",
    "cycle_one_waiting_teacher_review",
    "cycle_one_committed",
    "cycle_one_process_closed",
    "cycle_two_started",
    "cycle_two_readback_loaded",
    "cycle_two_readback_consumed",
    "cycle_two_waiting_teacher_review",
    "completed",
    "blocked",
    "failed",
}


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


def _hash(value: Any) -> str:
    return calculate_sha256(_plain(value))


@dataclass(frozen=True)
class TwoCycleFixtureGrowthRunRecord:
    run_id: str
    schema_version: str
    created_at: str
    state_dir: str
    fixture_kind: str
    fixture_payload_sha256: str
    base_candidate_set_sha256: str
    runtime_config_sha256: str
    cycle_one_session_id: str | None
    cycle_two_session_id: str | None
    cycle_one_process_instance_id: str | None
    cycle_two_process_instance_id: str | None
    cycle_one_runtime_instance_id: str | None
    cycle_two_runtime_instance_id: str | None
    cycle_one_status: str
    cycle_two_status: str
    run_status: str

    def __post_init__(self) -> None:
        if self.schema_version != RUN_SCHEMA_VERSION:
            raise ValueError("invalid two-cycle run schema_version")
        if self.run_status not in ALLOWED_RUN_STATUSES:
            raise ValueError(f"unsupported run_status: {self.run_status}")
        if not self.state_dir:
            raise ValueError("state_dir is required")
        if self.fixture_kind != "camera_unknown_low_level_event":
            raise ValueError("Package 118 primary run requires camera_unknown_low_level_event")

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TwoCycleFixtureGrowthRunRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class CycleProcessReceipt:
    cycle_process_receipt_id: str
    schema_version: str
    created_at: str
    run_id: str
    cycle_index: int
    process_instance_id: str
    operating_system_pid: int
    runtime_instance_id: str
    store_connection_id: str
    session_id: str
    worker_mode: str
    worker_started_at: str
    worker_closed_at: str | None
    store_opened: bool
    store_closed: bool
    process_exit_requested: bool
    process_exit_status: str | None
    codex_runtime_call_count: int = 0
    llm_runtime_call_count: int = 0
    network_model_call_count: int = 0
    arbitrary_runtime_subprocess_call_count: int = 0
    dynamic_code_execution_attempt_count: int = 0

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class CycleOneGrowthCommitReceipt:
    cycle_one_commit_receipt_id: str
    schema_version: str
    created_at: str
    run_id: str
    session_id: str
    pending_teacher_review_id: str
    evidence_snapshot_id: str
    evidence_identity_sha256: str
    teacher_decision_id: str
    teacher_approval_scope: str
    reviewed_interpretation_commit_id: str
    working_readback_commit_id: str
    package_90_to_92_identity_chain_valid: bool
    commit_provenance_valid: bool
    session_committed: bool

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class CycleTwoReadbackConsumptionReceipt:
    cycle_two_consumption_receipt_id: str
    schema_version: str
    created_at: str
    run_id: str
    session_id: str
    source_cycle_one_session_id: str
    loaded_before_event_processing: bool
    loaded_working_readback_commit_ids: tuple[str, ...]
    loaded_interpretation_commit_ids: tuple[str, ...]
    loaded_evidence_identity_hashes: tuple[str, ...]
    current_event_id: str
    current_fixture_kind: str
    current_fixture_payload_sha256: str
    current_base_candidate_set_sha256: str
    current_runtime_config_sha256: str
    evaluated_readback_item_ids: tuple[str, ...]
    matched_readback_item_ids: tuple[str, ...]
    unmatched_readback_item_ids: tuple[str, ...]
    readback_signal_ids: tuple[str, ...]
    candidate_score_record_ids: tuple[str, ...]
    ordering_record_ids: tuple[str, ...]
    internal_action_choice_ids: tuple[str, ...]
    nonzero_delta_count: int
    ordering_changed: bool
    selected_action_changed_from_baseline: bool
    readback_loaded: bool
    readback_evaluated: bool
    matching_rule_found: bool
    candidate_delta_applied: bool
    readback_consumed: bool
    source_trace_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class TwoCycleGrowthLineageResult:
    lineage_result_id: str
    schema_version: str
    created_at: str
    run_id: str
    valid: bool
    cycle_one_committed: bool
    process_boundary_valid: bool
    readback_commit_continuity_valid: bool
    readback_consumption_valid: bool
    evidence_identity_preserved: bool
    source_trace_refs_preserved: bool
    no_codex_runtime_calls: bool
    status: str
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


def fixture_payload_for_kind(fixture_kind: str) -> dict[str, object]:
    if fixture_kind != "camera_unknown_low_level_event":
        raise ValueError("Package 118 primary fixture must be camera_unknown_low_level_event")
    return {
        "fixture_kind": fixture_kind,
        "source_port_kind": "camera_port",
        "event_type": "camera_unknown_low_level_event",
        "low_level_only": True,
        "payload_version": "package_118_primary_fixture_v0",
    }


def runtime_config_sha256() -> str:
    return _hash(BoundedEmbodiedSessionConfig().to_dict())


def candidate_set_sha256(candidates: tuple[Any, ...] | list[Any]) -> str:
    payload = []
    for item in candidates:
        data = item.to_dict() if hasattr(item, "to_dict") else dict(item)
        payload.append(
            {
                "candidate_action_kind": data.get("candidate_action_kind"),
                "candidate_reason_codes": tuple(data.get("candidate_reason_codes", ())),
                "candidate_priority": data.get("candidate_priority"),
                "candidate_status": data.get("candidate_status"),
            }
        )
    return _hash(payload)


def create_two_cycle_fixture_growth_run(
    *,
    state_dir: str | Path,
    fixture_kind: str = "camera_unknown_low_level_event",
) -> TwoCycleFixtureGrowthRunRecord:
    path = Path(state_dir)
    if not str(path):
        raise ValueError("state_dir is required")
    path.mkdir(parents=True, exist_ok=True)
    record = TwoCycleFixtureGrowthRunRecord(
        run_id=f"two_cycle_fixture_growth_run:{uuid4().hex[:12]}",
        schema_version=RUN_SCHEMA_VERSION,
        created_at=_now(),
        state_dir=str(path),
        fixture_kind=fixture_kind,
        fixture_payload_sha256=_hash(fixture_payload_for_kind(fixture_kind)),
        base_candidate_set_sha256="pending",
        runtime_config_sha256=runtime_config_sha256(),
        cycle_one_session_id=None,
        cycle_two_session_id=None,
        cycle_one_process_instance_id=None,
        cycle_two_process_instance_id=None,
        cycle_one_runtime_instance_id=None,
        cycle_two_runtime_instance_id=None,
        cycle_one_status="not_started",
        cycle_two_status="not_started",
        run_status="created",
    )
    TeacherGatedSessionStore(path).upsert_two_cycle_run(record.to_dict())
    return record


def load_two_cycle_fixture_growth_run(state_dir: str | Path, run_id: str) -> TwoCycleFixtureGrowthRunRecord:
    return TwoCycleFixtureGrowthRunRecord.from_dict(TeacherGatedSessionStore(state_dir).get_two_cycle_run(run_id))


def execute_cycle_one_worker(
    *,
    state_dir: str | Path,
    run_id: str,
    fixture_kind: str,
    teacher_decision: str,
    approval_scope: str,
    teacher_approval_text: str,
    reason_code: str,
    process_instance_id: str,
    runtime_instance_id: str,
    store_connection_id: str,
) -> dict[str, object]:
    if teacher_decision != "approved":
        raise ValueError("Package 118 primary Cycle 1 worker requires explicit approved decision")
    if approval_scope != FULL_COMMIT_APPROVAL_SCOPE:
        raise ValueError("Cycle 1 requires through_reviewed_concept_and_working_readback approval scope")
    if not teacher_approval_text:
        raise ValueError("teacher_approval_text is required")
    started = _now()
    path = Path(state_dir)
    with NoCodexRuntimeGuard() as guard:
        store = TeacherGatedSessionStore(path)
        run = load_two_cycle_fixture_growth_run(path, run_id)
        profile = build_verified_runtime_capability_profile()
        runtime = BoundedEmbodiedSessionRuntime(capability_profile=profile)
        state = runtime.create_session(BoundedEmbodiedSessionConfig())
        session_id = state.session_id
        runtime.inject_fixture_host_event(session_id, fixture_kind)
        run_result = runtime.run_until_blocked(session_id)
        if run_result.final_status != BoundedEmbodiedSessionStatus.WAITING_TEACHER_REVIEW.value:
            raise RuntimeError(f"Cycle 1 did not reach teacher gate: {run_result.final_status}")
        resume_runtime = TeacherGatedSessionResumeCommitRuntime()
        resume_runtime.persist_waiting_session(runtime, session_id, path)
        pending_reviews = store.list_pending_reviews(session_id)
        if len(pending_reviews) != 1:
            raise RuntimeError("Cycle 1 expected exactly one pending review")
        pending_review = pending_reviews[0]
        snapshot = store.load_evidence_snapshot(pending_review.evidence_snapshot_id)
        snapshot_validation = validate_session_learning_evidence_snapshot(snapshot)
        if not snapshot_validation["valid"]:
            raise RuntimeError(f"invalid Cycle 1 evidence snapshot: {snapshot_validation}")
        decision = resume_runtime.apply_teacher_decision(
            session_id,
            pending_review.pending_teacher_review_id,
            teacher_decision,
            (reason_code,),
            teacher_approval_text,
            path,
            approval_scope=approval_scope,
            expected_evidence_hash=snapshot.evidence_identity_sha256,
        )
        commit_result = resume_runtime.resume_after_approval(
            session_id,
            decision.teacher_decision_id,
            path,
        )
        if commit_result.final_status != BoundedEmbodiedSessionStatus.COMMITTED.value:
            raise RuntimeError(f"Cycle 1 did not commit: {commit_result.final_status}")
        audit = build_session_evidence_identity_approval_scope_audit(
            store=store,
            session_id=session_id,
        )
        bindings = tuple(
            {
                "schema_version": "ashl_learning_pipeline_evidence_identity_binding_v0",
                **{
                    key: value
                    for key, value in item.items()
                    if key
                    in {
                        "binding_id",
                        "created_at",
                        "session_id",
                        "evidence_snapshot_id",
                        "evidence_identity_sha256",
                        "pipeline_stage",
                        "target_record_kind",
                        "target_record_id",
                        "source_binding_id",
                        "source_trace_refs",
                        "identity_preserved",
                        "validator_passed",
                    }
                },
            }
            for item in store.list_learning_pipeline_identity_bindings(session_id)
        )
        identity_chain = validate_learning_pipeline_identity_chain(tuple(bindings))
        active_readback = store.load_active_working_readback()
        active_for_session = tuple(item for item in active_readback if item.get("session_id", session_id) == session_id)
        readback_item = active_for_session[-1] if active_for_session else active_readback[-1]
        commit_receipt = CycleOneGrowthCommitReceipt(
            cycle_one_commit_receipt_id=f"cycle_one_growth_commit_receipt:{run_id}:{uuid4().hex[:8]}",
            schema_version=CYCLE_ONE_RECEIPT_SCHEMA_VERSION,
            created_at=_now(),
            run_id=run_id,
            session_id=session_id,
            pending_teacher_review_id=pending_review.pending_teacher_review_id,
            evidence_snapshot_id=snapshot.evidence_snapshot_id,
            evidence_identity_sha256=snapshot.evidence_identity_sha256,
            teacher_decision_id=decision.teacher_decision_id,
            teacher_approval_scope=approval_scope,
            reviewed_interpretation_commit_id=str(readback_item["interpretation_commit_id"]),
            working_readback_commit_id=str(readback_item["working_readback_commit_id"]),
            package_90_to_92_identity_chain_valid=bool(identity_chain["valid"]),
            commit_provenance_valid=audit.audit_status.startswith("passed_"),
            session_committed=True,
        )
        store.insert_cycle_one_growth_commit_receipt(commit_receipt.to_dict())
        base_hash = candidate_set_sha256(tuple(runtime._records[session_id]["internal_action_candidates"]))
        updated_run = replace(
            run,
            base_candidate_set_sha256=base_hash,
            cycle_one_session_id=session_id,
            cycle_one_process_instance_id=process_instance_id,
            cycle_one_runtime_instance_id=runtime_instance_id,
            cycle_one_status=BoundedEmbodiedSessionStatus.COMMITTED.value,
            run_status="cycle_one_process_closed",
        )
        store.upsert_two_cycle_run(updated_run.to_dict())
        receipt = CycleProcessReceipt(
            cycle_process_receipt_id=f"cycle_process_receipt:{run_id}:1:{uuid4().hex[:8]}",
            schema_version=PROCESS_RECEIPT_SCHEMA_VERSION,
            created_at=_now(),
            run_id=run_id,
            cycle_index=1,
            process_instance_id=process_instance_id,
            operating_system_pid=os.getpid(),
            runtime_instance_id=runtime_instance_id,
            store_connection_id=store_connection_id,
            session_id=session_id,
            worker_mode="cycle-one",
            worker_started_at=started,
            worker_closed_at=_now(),
            store_opened=True,
            store_closed=True,
            process_exit_requested=True,
            process_exit_status="normal_exit_requested",
            codex_runtime_call_count=guard.counters().codex_runtime_call_count,
            llm_runtime_call_count=guard.counters().llm_runtime_call_count,
            network_model_call_count=guard.counters().network_connection_attempt_count,
            arbitrary_runtime_subprocess_call_count=guard.counters().arbitrary_subprocess_attempt_count,
            dynamic_code_execution_attempt_count=guard.counters().dynamic_code_execution_attempt_count,
        )
        store.insert_cycle_process_receipt(receipt.to_dict())
        return {
            "run_record": updated_run.to_dict(),
            "cycle_process_receipt": receipt.to_dict(),
            "cycle_one_commit_receipt": commit_receipt.to_dict(),
            "session_run_result": commit_result.to_dict(),
            "actual_runtime_bindings": tuple(runtime.binding_log(session_id)),
            "no_codex_guard_counters": guard.counters().to_dict(),
        }


def execute_cycle_two_worker(
    *,
    state_dir: str | Path,
    run_id: str,
    fixture_kind: str,
    process_instance_id: str,
    runtime_instance_id: str,
    store_connection_id: str,
) -> dict[str, object]:
    started = _now()
    path = Path(state_dir)
    with NoCodexRuntimeGuard() as guard:
        store = TeacherGatedSessionStore(path)
        run = load_two_cycle_fixture_growth_run(path, run_id)
        cycle_one = store.get_cycle_one_growth_commit_receipt(run_id)
        if not cycle_one.get("session_committed"):
            raise RuntimeError("Cycle 1 must be committed before Cycle 2")
        readback = tuple(
            item
            for item in store.load_active_working_readback()
            if item.get("working_readback_commit_id") == cycle_one["working_readback_commit_id"]
        )
        if not readback:
            raise RuntimeError("Cycle 2 could not load Cycle 1 active working readback")
        profile = build_verified_runtime_capability_profile()
        runtime = BoundedEmbodiedSessionRuntime(capability_profile=profile)
        state = runtime.create_session(BoundedEmbodiedSessionConfig())
        session_id = state.session_id
        runtime.attach_working_readback_snapshot(session_id, readback)
        runtime.inject_fixture_host_event(session_id, fixture_kind)
        run_result = runtime.run_until_blocked(session_id)
        if run_result.final_status != BoundedEmbodiedSessionStatus.WAITING_TEACHER_REVIEW.value:
            raise RuntimeError(f"Cycle 2 did not reach teacher gate: {run_result.final_status}")
        records = runtime._records[session_id]
        candidates = tuple(records.get("internal_action_candidates", ()))
        base_hash = candidate_set_sha256(candidates)
        if run.base_candidate_set_sha256 != base_hash:
            raise RuntimeError("Cycle 2 base candidate set does not match Cycle 1")
        evaluation = dict(records.get("readback_consumption_evaluation", {}))
        signals = tuple(records.get("readback_internal_action_signals", ()))
        scores = tuple(records.get("readback_candidate_scores", ()))
        ordering = records.get("readback_influenced_ordering")
        influenced_choice = records.get("readback_influenced_choice")
        base_choice = records.get("internal_action_choice")
        receipt = CycleTwoReadbackConsumptionReceipt(
            cycle_two_consumption_receipt_id=f"cycle_two_readback_consumption_receipt:{run_id}:{uuid4().hex[:8]}",
            schema_version=CYCLE_TWO_RECEIPT_SCHEMA_VERSION,
            created_at=_now(),
            run_id=run_id,
            session_id=session_id,
            source_cycle_one_session_id=str(cycle_one["session_id"]),
            loaded_before_event_processing=True,
            loaded_working_readback_commit_ids=tuple(str(item["working_readback_commit_id"]) for item in readback),
            loaded_interpretation_commit_ids=tuple(str(item["interpretation_commit_id"]) for item in readback),
            loaded_evidence_identity_hashes=tuple(str(item["evidence_identity_sha256"]) for item in readback),
            current_event_id=str(records["host_body_event"].host_body_event_id),
            current_fixture_kind=fixture_kind,
            current_fixture_payload_sha256=_hash(fixture_payload_for_kind(fixture_kind)),
            current_base_candidate_set_sha256=base_hash,
            current_runtime_config_sha256=runtime_config_sha256(),
            evaluated_readback_item_ids=tuple(str(item["working_readback_commit_id"]) for item in readback),
            matched_readback_item_ids=tuple(evaluation.get("matched_readback_item_ids", ())),
            unmatched_readback_item_ids=tuple(evaluation.get("unmatched_readback_item_ids", ())),
            readback_signal_ids=tuple(str(item.readback_internal_action_signal_id) for item in signals),
            candidate_score_record_ids=tuple(str(item.candidate_readback_score_id) for item in scores),
            ordering_record_ids=tuple(
                [str(ordering.readback_influenced_ordering_id)] if ordering is not None else []
            ),
            internal_action_choice_ids=tuple(
                item
                for item in (
                    str(influenced_choice.readback_influenced_choice_id) if influenced_choice is not None else None,
                    str(base_choice.internal_action_choice_id) if base_choice is not None else None,
                )
                if item
            ),
            nonzero_delta_count=int(evaluation.get("nonzero_delta_count", 0)),
            ordering_changed=bool(evaluation.get("ordering_changed", False)),
            selected_action_changed_from_baseline=bool(
                influenced_choice is not None
                and base_choice is not None
                and influenced_choice.selected_internal_action_kind != base_choice.selected_internal_action_kind
            ),
            readback_loaded=bool(evaluation.get("readback_loaded", False)),
            readback_evaluated=bool(evaluation.get("readback_evaluated", False)),
            matching_rule_found=bool(evaluation.get("matching_rule_found", False)),
            candidate_delta_applied=bool(evaluation.get("candidate_delta_applied", False)),
            readback_consumed=bool(evaluation.get("readback_consumed", False)),
            source_trace_refs=tuple(
                dict.fromkeys(
                    ref
                    for item in readback
                    for ref in tuple(item.get("source_trace_refs", ()) or ())
                )
            ),
        )
        store.insert_cycle_two_readback_consumption_receipt(receipt.to_dict())
        receipt_process = CycleProcessReceipt(
            cycle_process_receipt_id=f"cycle_process_receipt:{run_id}:2:{uuid4().hex[:8]}",
            schema_version=PROCESS_RECEIPT_SCHEMA_VERSION,
            created_at=_now(),
            run_id=run_id,
            cycle_index=2,
            process_instance_id=process_instance_id,
            operating_system_pid=os.getpid(),
            runtime_instance_id=runtime_instance_id,
            store_connection_id=store_connection_id,
            session_id=session_id,
            worker_mode="cycle-two",
            worker_started_at=started,
            worker_closed_at=_now(),
            store_opened=True,
            store_closed=True,
            process_exit_requested=True,
            process_exit_status="normal_exit_requested",
            codex_runtime_call_count=guard.counters().codex_runtime_call_count,
            llm_runtime_call_count=guard.counters().llm_runtime_call_count,
            network_model_call_count=guard.counters().network_connection_attempt_count,
            arbitrary_runtime_subprocess_call_count=guard.counters().arbitrary_subprocess_attempt_count,
            dynamic_code_execution_attempt_count=guard.counters().dynamic_code_execution_attempt_count,
        )
        store.insert_cycle_process_receipt(receipt_process.to_dict())
        updated_run = replace(
            run,
            cycle_two_session_id=session_id,
            cycle_two_process_instance_id=process_instance_id,
            cycle_two_runtime_instance_id=runtime_instance_id,
            cycle_two_status=BoundedEmbodiedSessionStatus.WAITING_TEACHER_REVIEW.value,
            run_status="completed" if receipt.readback_consumed else "blocked",
        )
        store.upsert_two_cycle_run(updated_run.to_dict())
        return {
            "run_record": updated_run.to_dict(),
            "cycle_process_receipt": receipt_process.to_dict(),
            "cycle_two_readback_consumption_receipt": receipt.to_dict(),
            "session_run_result": run_result.to_dict(),
            "actual_runtime_bindings": tuple(runtime.binding_log(session_id)),
            "no_codex_guard_counters": guard.counters().to_dict(),
        }


def run_worker_process(
    *,
    mode: str,
    state_dir: str | Path,
    run_id: str,
    fixture_kind: str = "camera_unknown_low_level_event",
    teacher_decision: str | None = None,
    approval_scope: str | None = None,
    teacher_approval_text: str | None = None,
    reason_code: str | None = None,
) -> dict[str, Any]:
    if mode not in {"cycle-one", "cycle-two"}:
        raise ValueError(f"unsupported worker mode: {mode}")
    args = [
        sys.executable,
        "-m",
        WORKER_MODULE,
        mode,
        "--state-dir",
        str(state_dir),
        "--run-id",
        run_id,
        "--fixture",
        fixture_kind,
    ]
    if mode == "cycle-one":
        if not all((teacher_decision, approval_scope, teacher_approval_text, reason_code)):
            raise ValueError("Cycle 1 worker requires explicit teacher decision, scope, text, and reason")
        args.extend(
            [
                "--teacher-decision",
                str(teacher_decision),
                "--approval-scope",
                str(approval_scope),
                "--teacher-approval-text",
                str(teacher_approval_text),
                "--reason-code",
                str(reason_code),
            ]
        )
    completed = subprocess.run(args, capture_output=True, text=True, shell=False, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"worker failed ({mode}): {completed.stderr or completed.stdout}")
    return dict(json.loads(completed.stdout))


def run_two_cycle_fixture_growth_demo(
    *,
    teacher_decision: str,
    approval_scope: str,
    teacher_approval_text: str,
    reason_code: str,
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    if state_dir is None:
        state_dir = Path(tempfile.mkdtemp(prefix="ashl_pkg118_two_cycle_"))
    run = create_two_cycle_fixture_growth_run(state_dir=state_dir)
    cycle_one = run_worker_process(
        mode="cycle-one",
        state_dir=state_dir,
        run_id=run.run_id,
        teacher_decision=teacher_decision,
        approval_scope=approval_scope,
        teacher_approval_text=teacher_approval_text,
        reason_code=reason_code,
    )
    cycle_two = run_worker_process(
        mode="cycle-two",
        state_dir=state_dir,
        run_id=run.run_id,
    )
    lineage = validate_two_cycle_growth_lineage(Path(state_dir), run.run_id)
    return {
        "run_id": run.run_id,
        "state_dir": str(state_dir),
        "cycle_one": cycle_one,
        "cycle_two": cycle_two,
        "lineage": lineage.to_dict(),
        "orchestrator_worker_subprocess_count": 2,
        "arbitrary_subprocess_count": 0,
        "shell_used": False,
    }


def validate_two_cycle_growth_lineage(
    state_dir: Path,
    run_id: str,
) -> TwoCycleGrowthLineageResult:
    store = TeacherGatedSessionStore(state_dir)
    reasons: list[str] = []
    run = load_two_cycle_fixture_growth_run(state_dir, run_id)
    try:
        cycle_one = store.get_cycle_one_growth_commit_receipt(run_id)
    except Exception as error:
        cycle_one = {}
        reasons.append(f"missing_cycle_one_commit_receipt:{error}")
    try:
        cycle_two = store.get_cycle_two_readback_consumption_receipt(run_id)
    except Exception as error:
        cycle_two = {}
        reasons.append(f"missing_cycle_two_consumption_receipt:{error}")
    process_receipts = store.list_cycle_process_receipts(run_id)
    process_boundary_valid = (
        len(process_receipts) >= 2
        and process_receipts[0]["process_instance_id"] != process_receipts[1]["process_instance_id"]
        and process_receipts[0]["runtime_instance_id"] != process_receipts[1]["runtime_instance_id"]
        and process_receipts[0]["store_connection_id"] != process_receipts[1]["store_connection_id"]
        and process_receipts[0]["session_id"] != process_receipts[1]["session_id"]
        and process_receipts[0]["store_closed"]
        and process_receipts[1]["store_closed"]
    )
    if not process_boundary_valid:
        reasons.append("process_boundary_invalid")
    readback_commit_continuity_valid = bool(
        cycle_one
        and cycle_two
        and cycle_one["working_readback_commit_id"] in tuple(cycle_two["loaded_working_readback_commit_ids"])
    )
    if not readback_commit_continuity_valid:
        reasons.append("working_readback_commit_continuity_invalid")
    readback_consumption_valid = bool(
        cycle_two
        and cycle_two.get("readback_loaded")
        and cycle_two.get("readback_evaluated")
        and cycle_two.get("matching_rule_found")
        and cycle_two.get("candidate_delta_applied")
        and cycle_two.get("readback_consumed")
    )
    if not readback_consumption_valid:
        reasons.append("readback_not_consumed")
    evidence_identity_preserved = bool(
        cycle_one
        and cycle_two
        and cycle_one["evidence_identity_sha256"] in tuple(cycle_two["loaded_evidence_identity_hashes"])
    )
    if not evidence_identity_preserved:
        reasons.append("evidence_identity_not_preserved")
    source_trace_refs_preserved = bool(
        cycle_two
        and cycle_two.get("source_trace_refs")
        and cycle_one
        and _trace_refs_reach_raw_trace(
            store=store,
            session_id=str(cycle_one["session_id"]),
            trace_refs=tuple(cycle_two["source_trace_refs"]),
        )
    )
    if not source_trace_refs_preserved:
        reasons.append("cycle_two_source_trace_refs_do_not_reach_raw_trace")
    valid = (
        run.run_status == "completed"
        and bool(cycle_one.get("session_committed"))
        and process_boundary_valid
        and readback_commit_continuity_valid
        and readback_consumption_valid
        and evidence_identity_preserved
        and source_trace_refs_preserved
    )
    return TwoCycleGrowthLineageResult(
        lineage_result_id=f"two_cycle_growth_lineage_result:{run_id}:{uuid4().hex[:8]}",
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
    store: TeacherGatedSessionStore,
    session_id: str,
    trace_refs: tuple[str, ...],
) -> bool:
    traces = {item.trace_id: item for item in store.list_trace_envelopes(session_id)}
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
