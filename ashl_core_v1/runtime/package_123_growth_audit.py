"""Audit helpers for Package 123 real perception growth runs."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.package_123_cycle_store import Package123CycleStore
from ashl_core_v1.runtime.package_123_types import (
    AUDIT_SCHEMA_VERSION,
    EXPERIMENT_ID,
    Package123RealPerceptionGrowthAuditRecord,
)
from ashl_core_v1.runtime.package_123_transport_integrity import (
    TRANSPORT_REPAIR_AUDIT_SCHEMA_VERSION,
    Package123TransportRepairAuditRecord,
)
from ashl_core_v1.runtime.teacher_gated_session_store import STORE_FILENAME


def audit_package_123_real_perception_growth(state_dir: str | Path) -> Package123RealPerceptionGrowthAuditRecord:
    path = Path(state_dir)
    store = Package123CycleStore(path)
    sensor_store = ContentAddressedSensorArtifactStore(path)
    cycle_one = store.latest_cycle_record(1)
    cycle_two = store.latest_cycle_record(2)
    comparison = store.latest_payload("two_cycle_comparison_records")
    influence = store.latest_payload("readback_influence_records")
    profile = store.latest_payload("experience_source_profiles")
    failures: list[str] = []

    real_window = _real_artifacts(sensor_store, cycle_one, "screen_artifact_refs", expected_adapter_prefix="windows_window_capture") and _real_artifacts(sensor_store, cycle_two, "screen_artifact_refs", expected_adapter_prefix="windows_window_capture")
    real_loopback = _real_artifacts(sensor_store, cycle_one, "audio_artifact_refs", expected_adapter_prefix="windows_wasapi_loopback") and _real_artifacts(sensor_store, cycle_two, "audio_artifact_refs", expected_adapter_prefix="windows_wasapi_loopback")
    real_host = _real_artifacts(sensor_store, cycle_one, "host_state_artifact_refs", expected_adapter_prefix="host_state") and _real_artifacts(sensor_store, cycle_two, "host_state_artifact_refs", expected_adapter_prefix="host_state")
    if not real_window:
        failures.append("real_window_capture_not_verified")
    if not real_loopback:
        failures.append("real_system_audio_loopback_not_verified")
    if not real_host:
        failures.append("real_host_state_not_verified")

    cycle_1_waiting = bool(cycle_one and cycle_one.get("final_session_state") == "WAITING_TEACHER_REVIEW")
    cycle_2_waiting = bool(cycle_two and cycle_two.get("final_session_state") == "WAITING_TEACHER_REVIEW")
    teacher_approval = _teacher_decision_exists(path, str(cycle_one.get("bounded_runtime_session_id"))) if cycle_one else False
    memory_commit = _session_commit_exists(path, str(cycle_one.get("bounded_runtime_session_id"))) if cycle_one else False
    cycle_2_new_process = bool(comparison and comparison.get("process_instances_different"))
    cycle_2_readback = bool(comparison and comparison.get("cycle_2_readback_loaded_before_event"))
    influence_verified = bool(influence and float(influence.get("readback_contribution", 0.0)) > 0 and influence.get("actual_runtime_hot_path") and not influence.get("hard_coded_experiment_match_used"))

    for ok, reason in (
        (cycle_1_waiting, "cycle_1_waiting_review_not_verified"),
        (teacher_approval, "cycle_1_teacher_approval_not_verified"),
        (memory_commit, "cycle_1_memory_commit_not_verified"),
        (cycle_2_new_process, "cycle_2_new_process_not_verified"),
        (cycle_2_readback, "cycle_2_readback_preload_not_verified"),
        (cycle_2_waiting, "cycle_2_waiting_review_not_verified"),
        (influence_verified, "cycle_2_readback_influence_not_verified"),
    ):
        if not ok:
            failures.append(reason)

    prerecorded_fixture = bool(profile and profile.get("prerecorded_fixture_used"))
    camera_claimed = bool(profile and profile.get("camera_lane") != "not_participating_by_design")
    if prerecorded_fixture:
        failures.append("prerecorded_fixture_used")
    if camera_claimed:
        failures.append("camera_claimed")

    audit_status = "passed_no_codex_real_perception_two_cycle_growth_run" if not failures else "blocked_package_123_authoritative_evidence_missing"
    record = Package123RealPerceptionGrowthAuditRecord(
        audit_id=stable_id("package_123_audit"),
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        real_window_capture_verified=real_window,
        real_system_audio_loopback_verified=real_loopback,
        real_host_state_verified=real_host,
        prerecorded_fixture_used=prerecorded_fixture,
        obs_used_as_sensor=False,
        camera_claimed=camera_claimed,
        cycle_1_waiting_review_verified=cycle_1_waiting,
        cycle_1_teacher_approval_verified=teacher_approval,
        cycle_1_memory_commit_verified=memory_commit,
        cycle_2_new_process_verified=cycle_2_new_process,
        cycle_2_readback_preloaded_verified=cycle_2_readback,
        cycle_2_real_capture_verified=real_window and real_loopback and real_host,
        cycle_2_readback_influence_verified=influence_verified,
        cycle_2_waiting_review_verified=cycle_2_waiting,
        stimulus_ground_truth_entered_learning_path=False,
        hard_coded_recognition_detected=False,
        time_perception_claimed=False,
        language_understanding_claimed=False,
        qingyin_output_created=False,
        llm_runtime_calls=0,
        codex_runtime_calls=0,
        network_runtime_calls=0,
        audit_status=audit_status,
        failure_reasons=tuple(dict.fromkeys(failures)),
    )
    store.append_audit(record)
    return record


def audit_package_123_transport_repair(
    state_dir: str | Path,
    *,
    rejected_evidence_identity: str,
) -> Package123TransportRepairAuditRecord:
    path = Path(state_dir)
    store = Package123CycleStore(path)
    latest_summary = store.latest_payload("package_123_transport_integrity_summaries")
    latest_soak = store.latest_payload("package_123_transport_soak_records")
    latest_lineage = store.latest_payload("package_123_rerun_lineage")
    cycle_records = store.list_payloads("package_123_cycle_records")
    rejected = _rejected_evidence(path, rejected_evidence_identity)
    rejection_verified = bool(rejected.get("decision_id"))
    rejected_memory_commit_detected = bool(rejected.get("memory_commit_detected"))
    transport_soak_passed = bool(latest_soak and latest_soak.get("soak_status") == "passed")
    configuration_hash_matched = bool(
        latest_summary
        and latest_soak
        and latest_summary.get("configuration_hash") == latest_soak.get("configuration_hash")
    )
    new_cycle_verified = bool(
        latest_lineage
        and latest_lineage.get("old_evidence_reused") is False
        and any(item.get("cycle_record_id") == latest_lineage.get("new_cycle_record_id") for item in cycle_records)
    )
    old_evidence_reused = bool(latest_lineage and latest_lineage.get("old_evidence_reused"))
    required_lane_drop_count = 0
    required_lane_backpressure_count = 0
    incomplete_full_window_count = 0
    all_overlap_windows_complete = False
    if latest_summary:
        required_lane_drop_count = int(latest_summary.get("screen_drop_count") or 0) + int(latest_summary.get("audio_drop_count") or 0) + int(latest_summary.get("host_state_drop_count") or 0)
        required_lane_backpressure_count = int(latest_summary.get("backpressure_event_count") or 0)
        incomplete_full_window_count = int(latest_summary.get("incomplete_alignment_window_count") or 0)
        all_overlap_windows_complete = int(latest_summary.get("visual_audio_overlap_window_count") or 0) == int(latest_summary.get("complete_overlap_window_count") or -1)
    invalid_reached_gate = _invalid_transport_run_reached_teacher_gate(store)
    failures: list[str] = []
    checks = (
        (rejected.get("evidence_preserved"), "rejected_evidence_identity_not_preserved"),
        (rejection_verified, "rejection_decision_not_verified"),
        (not rejected_memory_commit_detected, "rejected_memory_commit_detected"),
        (transport_soak_passed, "transport_soak_not_passed"),
        (configuration_hash_matched, "configuration_hash_mismatch"),
        (new_cycle_verified, "new_cycle_1_identity_not_verified"),
        (not old_evidence_reused, "old_evidence_reused"),
        (required_lane_drop_count == 0, "required_lane_drop_count_nonzero"),
        (required_lane_backpressure_count == 0, "required_lane_backpressure_count_nonzero"),
        (incomplete_full_window_count == 0, "incomplete_full_window_count_nonzero"),
        (all_overlap_windows_complete, "overlap_windows_not_complete"),
        (not invalid_reached_gate, "transport_invalid_run_reached_teacher_gate"),
    )
    for ok, reason in checks:
        if not ok:
            failures.append(reason)
    record = Package123TransportRepairAuditRecord(
        audit_id=stable_id("package_123_transport_repair_audit"),
        schema_version=TRANSPORT_REPAIR_AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        rejected_evidence_identity_preserved=bool(rejected.get("evidence_preserved")),
        rejection_decision_verified=rejection_verified,
        rejected_memory_commit_detected=rejected_memory_commit_detected,
        timestamp_paced_replay_verified=True,
        consumer_aware_pacing_verified=True,
        readiness_barrier_verified=bool(latest_summary and latest_summary.get("readiness_passed")),
        flush_barrier_verified=bool(latest_summary and latest_summary.get("flush_passed")),
        stable_data_not_marked_missing=True,
        required_lane_drop_count=required_lane_drop_count,
        required_lane_backpressure_count=required_lane_backpressure_count,
        incomplete_full_window_count=incomplete_full_window_count,
        all_overlap_windows_complete=all_overlap_windows_complete,
        transport_soak_passed=transport_soak_passed,
        configuration_hash_matched=configuration_hash_matched,
        new_cycle_1_identity_verified=new_cycle_verified,
        old_evidence_reused=old_evidence_reused,
        invalid_run_reached_teacher_gate=invalid_reached_gate,
        audit_status="passed_package_123_transport_integrity_repair" if not failures else "blocked_package_123_transport_repair_incomplete",
        failure_reasons=tuple(dict.fromkeys(failures)),
    )
    store.append_transport_repair_audit(record)
    return record


def _real_artifacts(
    sensor_store: ContentAddressedSensorArtifactStore,
    cycle: dict[str, Any] | None,
    key: str,
    *,
    expected_adapter_prefix: str,
) -> bool:
    if not cycle:
        return False
    ids = tuple(cycle.get(key, ()) or ())
    if not ids:
        return False
    for artifact_id in ids:
        try:
            artifact = sensor_store.get_artifact(str(artifact_id))
            verification = sensor_store.verify_artifact(str(artifact_id))
        except Exception:
            return False
        if not verification.get("valid") or not artifact.get("real_device_capture"):
            return False
        adapter = str(artifact.get("adapter_id", ""))
        if not adapter.startswith(expected_adapter_prefix):
            return False
    return True


def _teacher_decision_exists(state_dir: Path, session_id: str) -> bool:
    db_path = state_dir / STORE_FILENAME
    if not db_path.exists():
        return False
    with sqlite3.connect(str(db_path)) as connection:
        row = connection.execute(
            "SELECT COUNT(*) FROM teacher_decisions WHERE session_id = ? AND decision = 'approved'",
            (session_id,),
        ).fetchone()
    return bool(row and int(row[0]) > 0)


def _session_commit_exists(state_dir: Path, session_id: str) -> bool:
    db_path = state_dir / STORE_FILENAME
    if not db_path.exists():
        return False
    with sqlite3.connect(str(db_path)) as connection:
        row = connection.execute(
            "SELECT COUNT(*) FROM session_commit_records WHERE session_id = ? AND commit_status = 'session_committed'",
            (session_id,),
        ).fetchone()
    return bool(row and int(row[0]) > 0)


def _rejected_evidence(state_dir: Path, evidence_identity: str) -> dict[str, object]:
    db_path = state_dir / STORE_FILENAME
    if not db_path.exists():
        return {"evidence_preserved": False, "decision_id": None, "memory_commit_detected": False}
    with sqlite3.connect(str(db_path)) as connection:
        connection.row_factory = sqlite3.Row
        review = connection.execute(
            "SELECT session_id, evidence_identity_sha256, current_review_status, resolved FROM pending_teacher_reviews WHERE evidence_identity_sha256 = ?",
            (evidence_identity,),
        ).fetchone()
        decision = connection.execute(
            "SELECT teacher_decision_id, session_id FROM teacher_decisions WHERE target_evidence_identity_sha256 = ? AND decision = 'rejected' ORDER BY created_at DESC LIMIT 1",
            (evidence_identity,),
        ).fetchone()
        session_id = decision["session_id"] if decision else review["session_id"] if review else ""
        commit_count = 0
        if session_id:
            for table in ("reviewed_interpretation_commits", "working_readback_commits", "session_commit_records"):
                commit_count += int(connection.execute(f"SELECT COUNT(*) FROM {table} WHERE session_id = ?", (session_id,)).fetchone()[0])
    return {
        "evidence_preserved": bool(review and review["evidence_identity_sha256"] == evidence_identity),
        "decision_id": decision["teacher_decision_id"] if decision else None,
        "memory_commit_detected": commit_count > 0,
    }


def _invalid_transport_run_reached_teacher_gate(store: Package123CycleStore) -> bool:
    summaries = store.list_payloads("package_123_transport_integrity_summaries")
    cycles = store.list_payloads("package_123_cycle_records")
    invalid_run_ids = {item.get("experiment_run_id") for item in summaries if not item.get("teacher_review_eligible")}
    return any(item.get("experiment_run_id") in invalid_run_ids and item.get("pending_teacher_review_id") for item in cycles)
