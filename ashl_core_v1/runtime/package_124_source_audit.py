"""Read-only source audit for Package 124 real host perception milestone."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import sha256_bytes, sha256_payload, stable_id, utc_now
from ashl_core_v1.runtime.package_124_provenance_graph import build_milestone_provenance_graph
from ashl_core_v1.runtime.package_124_types import (
    PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY,
    PACKAGE_123_CYCLE_1_SESSION_ID,
    PACKAGE_123_CYCLE_2_SESSION_ID,
    PACKAGE_123_REJECTED_EVIDENCE_IDENTITY,
    PACKAGE_123_SOURCE_COMMIT,
    PACKAGE_124_AUDIT_SCHEMA_VERSION,
    PACKAGE_124_IDENTITY_SCHEMA_VERSION,
    PACKAGE_124_MILESTONE_ID,
    AudioTimelineContinuityAudit,
    MilestoneReadbackTimingAudit,
    Package124RealHostPerceptionMilestoneAuditRecord,
    PreservedPendingReviewRecord,
    RealHostPerceptionGrowthMilestoneIdentity,
    RejectedEvidenceIsolationAudit,
)


SOURCE_AUDIT_STATUS = "source_audit_passed_pending_archive"
FINAL_AUDIT_STATUS = "passed_real_host_perception_growth_loop_milestone_audit"


def inspect_package_124_source(
    state_dir: str | Path,
    *,
    expected_commit: str = PACKAGE_123_SOURCE_COMMIT,
) -> dict[str, object]:
    source = Path(state_dir)
    dbs = _required_db_paths(source)
    return {
        "source_state_dir": str(source),
        "source_state_dir_exists": source.exists(),
        "source_state_dir_is_outside_repository": _outside_repository(source),
        "expected_commit": expected_commit,
        "expected_commit_verified": expected_commit == PACKAGE_123_SOURCE_COMMIT,
        "databases": {name: {"path": str(path), "exists": path.exists(), "byte_length": path.stat().st_size if path.exists() else 0} for name, path in dbs.items()},
        "archive_marker_present": (source / "ARCHIVE_READ_ONLY").exists(),
    }


def audit_package_124_source(
    state_dir: str | Path,
    *,
    expected_commit: str = PACKAGE_123_SOURCE_COMMIT,
    expected_cycle_1_evidence_identity: str = PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY,
    expected_cycle_2_session: str = PACKAGE_123_CYCLE_2_SESSION_ID,
    archive_created: bool = False,
    archive_manifest_verified: bool = False,
    archive_read_only_reverification_passed: bool = False,
) -> dict[str, object]:
    source = Path(state_dir)
    failures: list[str] = []
    if not source.exists():
        failures.append("source_state_dir_missing")
    if expected_commit != PACKAGE_123_SOURCE_COMMIT:
        failures.append("source_commit_mismatch")
    if expected_cycle_1_evidence_identity != PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY:
        failures.append("cycle_1_evidence_identity_mismatch")
    if expected_cycle_2_session != PACKAGE_123_CYCLE_2_SESSION_ID:
        failures.append("cycle_2_session_mismatch")

    evidence: dict[str, Any] = {}
    try:
        evidence = _read_authoritative_evidence(source)
    except Exception as error:
        failures.append(f"missing_authoritative_evidence:{error}")
        evidence = {}

    identity = _build_identity(
        source,
        package_123_growth_audit_id=str((evidence.get("package_123_growth_audit") or {}).get("audit_id") or ""),
        package_123_transport_audit_id=str((evidence.get("package_123_transport_audit") or {}).get("audit_id") or ""),
        expected_commit=expected_commit,
    )
    graph = build_milestone_provenance_graph(evidence)
    audio_timeline = _audit_audio_timeline(evidence)
    readback_timing = _audit_readback_timing(evidence)
    rejected_isolation = _audit_rejected_evidence_isolation(source, evidence)
    preserved_pending = _build_preserved_pending_review(evidence)

    checks = _evaluate_checks(evidence, audio_timeline, readback_timing, rejected_isolation)
    failures.extend(reason for reason, valid in checks.items() if not valid)
    failures.extend(_forbidden_claim_checks(evidence))

    source_ok = not failures
    final_ok = source_ok and archive_created and archive_manifest_verified and archive_read_only_reverification_passed
    audit_record = Package124RealHostPerceptionMilestoneAuditRecord(
        audit_id=stable_id("package_124_milestone_audit"),
        schema_version=PACKAGE_124_AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        milestone_id=PACKAGE_124_MILESTONE_ID,
        source_commit_verified=expected_commit == PACKAGE_123_SOURCE_COMMIT,
        cycle_1_real_sources_verified=checks.get("cycle_1_real_sources_verified", False),
        cycle_1_transport_verified=checks.get("cycle_1_transport_verified", False),
        cycle_1_exact_teacher_approval_verified=checks.get("cycle_1_exact_teacher_approval_verified", False),
        cycle_1_memory_chain_verified=checks.get("cycle_1_memory_chain_verified", False),
        cycle_1_working_readback_verified=checks.get("cycle_1_working_readback_verified", False),
        rejected_evidence_isolation_verified=rejected_isolation.isolation_verified,
        cycle_process_separation_verified=checks.get("cycle_process_separation_verified", False),
        cycle_2_readback_timing_verified=readback_timing.timing_verified,
        cycle_2_package_112_influence_verified=checks.get("cycle_2_package_112_influence_verified", False),
        cycle_2_teacher_gate_verified=checks.get("cycle_2_teacher_gate_verified", False),
        audio_timeline_continuity_verified=audio_timeline.continuity_verified,
        stimulus_ground_truth_excluded=checks.get("stimulus_ground_truth_excluded", False),
        hard_coded_recognition_absent=checks.get("hard_coded_recognition_absent", False),
        semantic_recognition_created=False,
        time_perception_created=False,
        language_understanding_created=False,
        qingyin_output_created=False,
        llm_runtime_calls=int((evidence.get("runtime_counters") or {}).get("llm_runtime_calls", 0)),
        codex_runtime_calls=int((evidence.get("runtime_counters") or {}).get("codex_runtime_calls", 0)),
        network_runtime_calls=int((evidence.get("runtime_counters") or {}).get("network_runtime_calls", 0)),
        archive_created=archive_created,
        archive_manifest_verified=archive_manifest_verified,
        archive_read_only_reverification_passed=archive_read_only_reverification_passed,
        runtime_behavior_changed=False,
        audit_status=FINAL_AUDIT_STATUS if final_ok else SOURCE_AUDIT_STATUS if source_ok else "blocked_package_124_source_audit",
        failure_reasons=tuple(dict.fromkeys(failures)),
    )
    return {
        "identity": identity.to_dict(),
        "audit": audit_record.to_dict(),
        "provenance_graph": graph.to_dict(),
        "audio_timeline_continuity": audio_timeline.to_dict(),
        "readback_timing": readback_timing.to_dict(),
        "rejected_evidence_isolation": rejected_isolation.to_dict(),
        "preserved_pending_review": preserved_pending.to_dict(),
        "evidence": _public_evidence_summary(evidence),
        "source_ok": source_ok,
        "final_ok": final_ok,
    }


def _read_authoritative_evidence(source: Path) -> dict[str, Any]:
    dbs = _required_db_paths(source)
    for path in dbs.values():
        if not path.exists():
            raise FileNotFoundError(path)

    cycle_records = _payloads(dbs["package_123"], "package_123_cycle_records")
    cycle_one = _find_payload(cycle_records, bounded_runtime_session_id=PACKAGE_123_CYCLE_1_SESSION_ID, cycle_index=1)
    cycle_two = _find_payload(cycle_records, bounded_runtime_session_id=PACKAGE_123_CYCLE_2_SESSION_ID, cycle_index=2)
    if not cycle_one or not cycle_two:
        raise KeyError("missing exact Package 123 cycle records")

    transport_summaries = _payloads(dbs["package_123"], "package_123_transport_integrity_summaries")
    cycle_one_transport = _last_payload(
        transport_summaries,
        experiment_run_id=cycle_one["experiment_run_id"],
        cycle_index=1,
    )
    coverage = tuple(
        item
        for item in _payloads(dbs["package_123"], "package_123_alignment_window_coverage")
        if item.get("experiment_run_id") == cycle_one.get("experiment_run_id") and int(item.get("cycle_index", -1)) == 1
    )
    if not cycle_one_transport:
        raise KeyError("missing Cycle 1 transport summary")

    teacher_decisions = _rows(dbs["teacher"], "teacher_decisions", "created_at")
    teacher_decision = _find_row(
        teacher_decisions,
        session_id=PACKAGE_123_CYCLE_1_SESSION_ID,
        decision="approved",
        target_evidence_identity_sha256=PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY,
    )
    if not teacher_decision:
        raise KeyError("missing exact Cycle 1 teacher approval")
    pending_reviews = _rows(dbs["teacher"], "pending_teacher_reviews", "created_at")
    pending_review = _find_row(
        pending_reviews,
        session_id=PACKAGE_123_CYCLE_1_SESSION_ID,
        pending_teacher_review_id=teacher_decision["pending_teacher_review_id"],
    )
    rejected_pending = _find_row(
        pending_reviews,
        evidence_identity_sha256=PACKAGE_123_REJECTED_EVIDENCE_IDENTITY,
    )
    evidence_snapshot = _find_row(
        _rows(dbs["teacher"], "learning_evidence_snapshots", "created_at"),
        evidence_snapshot_id=teacher_decision["target_evidence_snapshot_id"],
        evidence_identity_sha256=PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY,
    )
    reviewed_interpretation = _find_row(
        _rows(dbs["teacher"], "reviewed_interpretation_commits", "created_at"),
        session_id=PACKAGE_123_CYCLE_1_SESSION_ID,
        evidence_identity_sha256=PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY,
    )
    working_readback = _find_row(
        _rows(dbs["teacher"], "working_readback_commits", "created_at"),
        session_id=PACKAGE_123_CYCLE_1_SESSION_ID,
        evidence_identity_sha256=PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY,
    )
    commit_record = _find_row(
        _rows(dbs["teacher"], "session_commit_records", "created_at"),
        session_id=PACKAGE_123_CYCLE_1_SESSION_ID,
        commit_status="session_committed",
    )
    identity_bindings = tuple(
        item
        for item in _rows(dbs["teacher"], "learning_pipeline_identity_bindings", "created_at")
        if item.get("session_id") == PACKAGE_123_CYCLE_1_SESSION_ID
        and item.get("evidence_identity_sha256") == PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY
    )
    provenance_binding = _find_row(
        _rows(dbs["teacher"], "interpretation_provenance_bindings", "created_at"),
        session_id=PACKAGE_123_CYCLE_1_SESSION_ID,
        evidence_identity_sha256=PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY,
    )
    teacher_targets = tuple(
        item
        for item in _rows(dbs["teacher"], "teacher_decision_target_bindings", "created_at")
        if item.get("teacher_decision_id") == teacher_decision.get("teacher_decision_id")
    )

    readback_timing = _last_payload(
        _payloads(dbs["package_123"], "readback_load_timing_records"),
        cycle_record_id=cycle_two["cycle_record_id"],
    )
    influence = _payloads(dbs["package_123"], "readback_influence_records")[-1]
    comparison = _payloads(dbs["package_123"], "two_cycle_comparison_records")[-1]
    growth_audit = _last_payload(
        _payloads(dbs["package_123"], "package_123_audit_records"),
        audit_status="passed_no_codex_real_perception_two_cycle_growth_run",
    )
    transport_audit = _last_payload(
        _payloads(dbs["package_123"], "package_123_transport_repair_audits"),
        audit_status="passed_package_123_transport_integrity_repair",
    )
    rerun_lineage = _payloads(dbs["package_123"], "package_123_rerun_lineage")[-1]
    source_profiles = _payloads(dbs["package_123"], "experience_source_profiles")
    cycle_one_profile = _find_payload(source_profiles, experiment_run_id=cycle_one["experiment_run_id"])
    cycle_two_profile = _find_payload(source_profiles, experiment_run_id=cycle_two["experiment_run_id"])

    artifact_ids = tuple(
        dict.fromkeys(
            tuple(cycle_one.get("screen_artifact_refs") or ())
            + tuple(cycle_one.get("audio_artifact_refs") or ())
            + tuple(cycle_one.get("host_state_artifact_refs") or ())
            + tuple(cycle_two.get("screen_artifact_refs") or ())
            + tuple(cycle_two.get("audio_artifact_refs") or ())
            + tuple(cycle_two.get("host_state_artifact_refs") or ())
        )
    )
    artifacts = {artifact_id: _sensor_artifact(source, artifact_id) for artifact_id in artifact_ids}
    artifact_hashes = {artifact_id: item["content_sha256"] for artifact_id, item in artifacts.items()}
    cycle_one_primitive_ids, cycle_two_primitive_ids = _primitive_ids_for_cycles(dbs["perception"], cycle_one, cycle_two)

    return {
        "source_state_dir": str(source),
        "db_paths": {name: str(path) for name, path in dbs.items()},
        "cycle_1_record": cycle_one,
        "cycle_2_record": cycle_two,
        "cycle_1_transport_summary": cycle_one_transport,
        "cycle_1_coverage_records": coverage,
        "teacher_decision": teacher_decision,
        "pending_review": pending_review,
        "evidence_snapshot": evidence_snapshot,
        "reviewed_interpretation_commit": reviewed_interpretation,
        "working_readback_commit": working_readback,
        "session_commit_record": commit_record,
        "learning_pipeline_identity_bindings": identity_bindings,
        "interpretation_provenance_binding": provenance_binding,
        "teacher_decision_target_bindings": teacher_targets,
        "readback_timing": readback_timing,
        "readback_timing_id": (readback_timing or {}).get("timing_record_id"),
        "readback_influence": influence,
        "two_cycle_comparison": comparison,
        "package_123_growth_audit": growth_audit,
        "package_123_transport_audit": transport_audit,
        "package_123_rerun_lineage": rerun_lineage,
        "cycle_1_source_profile": cycle_one_profile,
        "cycle_2_source_profile": cycle_two_profile,
        "artifacts": artifacts,
        "artifact_hashes": artifact_hashes,
        "cycle_1_primitive_ids": cycle_one_primitive_ids,
        "cycle_2_primitive_ids": cycle_two_primitive_ids,
        "rejected_pending_review": rejected_pending,
        "runtime_counters": _runtime_counters(growth_audit, comparison),
        "cycle_2_teacher_decisions": tuple(
            item for item in teacher_decisions if item.get("session_id") == PACKAGE_123_CYCLE_2_SESSION_ID
        ),
        "cycle_2_commit_records": tuple(
            item
            for item in _rows(dbs["teacher"], "session_commit_records", "created_at")
            if item.get("session_id") == PACKAGE_123_CYCLE_2_SESSION_ID
        ),
        "cycle_2_working_readback_commits": tuple(
            item
            for item in _rows(dbs["teacher"], "working_readback_commits", "created_at")
            if item.get("session_id") == PACKAGE_123_CYCLE_2_SESSION_ID
        ),
        "teacher_db_trace_rows": _rows(dbs["teacher"], "trace_envelopes", "sequence_index"),
        "sensor_failures": _payloads(dbs["sensor"], "sensor_capture_failures"),
        "compile_failures": _payloads(dbs["perception"], "perception_compilation_failures"),
    }


def _evaluate_checks(
    evidence: dict[str, Any],
    audio_timeline: AudioTimelineContinuityAudit,
    readback_timing: MilestoneReadbackTimingAudit,
    rejected_isolation: RejectedEvidenceIsolationAudit,
) -> dict[str, bool]:
    cycle_one = dict(evidence.get("cycle_1_record") or {})
    cycle_two = dict(evidence.get("cycle_2_record") or {})
    transport = dict(evidence.get("cycle_1_transport_summary") or {})
    teacher = dict(evidence.get("teacher_decision") or {})
    pending = dict(evidence.get("pending_review") or {})
    interpretation = dict(evidence.get("reviewed_interpretation_commit") or {})
    readback = dict(evidence.get("working_readback_commit") or {})
    commit = dict(evidence.get("session_commit_record") or {})
    influence = dict(evidence.get("readback_influence") or {})
    comparison = dict(evidence.get("two_cycle_comparison") or {})
    growth_audit = dict(evidence.get("package_123_growth_audit") or {})
    transport_audit = dict(evidence.get("package_123_transport_audit") or {})
    cycle_one_profile = dict(evidence.get("cycle_1_source_profile") or {})
    artifacts = dict(evidence.get("artifacts") or {})
    identity_bindings = tuple(evidence.get("learning_pipeline_identity_bindings") or ())
    coverage = tuple(evidence.get("cycle_1_coverage_records") or ())

    required_stages = {
        "reviewed_concept",
        "memory_learning_trace",
        "memory_routing_trace",
        "memory_application_data",
        "working_readback_commit",
        "reviewed_interpretation_commit",
    }
    stages = {str(item.get("pipeline_stage")) for item in identity_bindings if item.get("validator_passed") in {1, True}}
    cycle_one_artifacts = tuple(cycle_one.get("screen_artifact_refs") or ()) + tuple(cycle_one.get("audio_artifact_refs") or ()) + tuple(cycle_one.get("host_state_artifact_refs") or ())
    real_artifacts = all(_artifact_valid_for_kind(artifacts.get(artifact_id, {}), artifact_id) for artifact_id in cycle_one_artifacts)
    source_profile_valid = (
        cycle_one_profile.get("screen_lane") == "windows_window_capture"
        and cycle_one_profile.get("audio_lane") == "system_audio_loopback"
        and cycle_one_profile.get("host_state_lane") == "real_host_state"
        and cycle_one_profile.get("camera_lane") == "not_participating_by_design"
        and cycle_one_profile.get("prerecorded_fixture_used") is False
        and cycle_one_profile.get("real_live_capture") is True
    )
    overlap_records = tuple(item for item in coverage if item.get("visual_audio_overlap_present"))
    overlap_window_indices = {int(item.get("window_index", -1)) for item in overlap_records}
    expected_overlap_windows = {4, 6, 8, 10}
    overlap_windows_valid = (
        overlap_window_indices == expected_overlap_windows
        and all(item.get("required_lanes_complete") for item in overlap_records)
        and all((item.get("screen") or {}).get("salient_change_present") and (item.get("audio") or {}).get("salient_change_present") and (item.get("host_state") or {}).get("source_artifact_present") for item in overlap_records)
    )
    note = str(teacher.get("teacher_note") or "").lower()
    approved_scope_valid = (
        teacher.get("decision") == "approved"
        and teacher.get("approval_scope") == "through_reviewed_concept_and_working_readback"
        and teacher.get("pending_teacher_review_id") == cycle_one.get("pending_teacher_review_id")
        and teacher.get("target_evidence_snapshot_id") == pending.get("evidence_snapshot_id")
        and teacher.get("target_evidence_identity_sha256") == PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY
        and int(teacher.get("scope_sufficient_for_requested_operation") or 0) == 1
        and "stimulus ground truth is not approved" in note
    )
    memory_chain_valid = (
        bool(interpretation)
        and bool(commit)
        and interpretation.get("teacher_decision_id") == teacher.get("teacher_decision_id")
        and interpretation.get("evidence_identity_sha256") == PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY
        and interpretation.get("commit_status") == "active"
        and set(required_stages).issubset(stages)
        and bool(evidence.get("interpretation_provenance_binding"))
    )
    working_readback_valid = (
        bool(readback)
        and readback.get("evidence_identity_sha256") == PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY
        and int(readback.get("active_for_future_sessions") or 0) == 1
        and readback.get("source_reviewed_interpretation_commit_id") == interpretation.get("interpretation_commit_id")
    )
    cycle_one_artifact_set = set(tuple(cycle_one.get("screen_artifact_refs") or ()) + tuple(cycle_one.get("audio_artifact_refs") or ()) + tuple(cycle_one.get("host_state_artifact_refs") or ()))
    cycle_two_artifact_set = set(tuple(cycle_two.get("screen_artifact_refs") or ()) + tuple(cycle_two.get("audio_artifact_refs") or ()) + tuple(cycle_two.get("host_state_artifact_refs") or ()))
    score_without = float(influence.get("score_without_readback") or 0.0)
    score_with = float(influence.get("score_with_readback") or 0.0)
    contribution = float(influence.get("readback_contribution") or 0.0)
    return {
        "source_commit_verified": True,
        "cycle_1_real_sources_verified": real_artifacts and source_profile_valid,
        "cycle_1_transport_verified": (
            int(transport.get("full_alignment_window_count") or 0) == 24
            and int(transport.get("complete_alignment_window_count") or 0) == 24
            and int(transport.get("incomplete_alignment_window_count") or 0) == 0
            and int(transport.get("visual_change_region_count") or 0) == 8
            and int(transport.get("audio_change_region_count") or 0) == 4
            and int(transport.get("visual_audio_overlap_window_count") or 0) == 4
            and int(transport.get("complete_overlap_window_count") or 0) == 4
            and int(transport.get("screen_drop_count") or 0) == 0
            and int(transport.get("audio_drop_count") or 0) == 0
            and int(transport.get("host_state_drop_count") or 0) == 0
            and int(transport.get("backpressure_event_count") or 0) == 0
            and int(transport.get("capture_failure_count") or 0) == 0
            and int(transport.get("compile_failure_count") or 0) == 0
            and transport.get("teacher_review_eligible") is True
            and overlap_windows_valid
        ),
        "cycle_1_exact_teacher_approval_verified": approved_scope_valid,
        "cycle_1_memory_chain_verified": memory_chain_valid,
        "cycle_1_working_readback_verified": working_readback_valid,
        "rejected_evidence_isolation_verified": rejected_isolation.isolation_verified,
        "cycle_process_separation_verified": (
            cycle_one.get("process_instance_id") != cycle_two.get("process_instance_id")
            and int(cycle_one.get("operating_system_process_id") or 0) != int(cycle_two.get("operating_system_process_id") or 0)
            and cycle_one.get("experiment_run_id") != cycle_two.get("experiment_run_id")
            and cycle_one.get("bounded_runtime_session_id") != cycle_two.get("bounded_runtime_session_id")
            and cycle_one.get("perception_session_id") != cycle_two.get("perception_session_id")
            and cycle_one_artifact_set.isdisjoint(cycle_two_artifact_set)
            and str(cycle_one.get("created_at") or "") < str(cycle_two.get("created_at") or "")
            and comparison.get("process_instances_different") is True
            and comparison.get("raw_artifacts_different") is True
            and comparison.get("runtime_sessions_different") is True
        ),
        "cycle_2_package_112_influence_verified": (
            influence.get("scorer_id") == "host_body_readback_internal_action_influence"
            and abs(contribution - 3.0) < 0.000001
            and abs((score_without + contribution) - score_with) < 0.000001
            and influence.get("actual_runtime_hot_path") is True
            and influence.get("hard_coded_experiment_match_used") is False
            and readback.get("working_readback_commit_id") in tuple(influence.get("influencing_readback_refs") or ())
        ),
        "cycle_2_teacher_gate_verified": (
            cycle_two.get("final_session_state") == "WAITING_TEACHER_REVIEW"
            and bool(cycle_two.get("pending_teacher_review_id"))
            and len(tuple(evidence.get("cycle_2_teacher_decisions") or ())) == 0
            and len(tuple(evidence.get("cycle_2_commit_records") or ())) == 0
            and len(tuple(evidence.get("cycle_2_working_readback_commits") or ())) == 0
        ),
        "audio_timeline_continuity_verified": audio_timeline.continuity_verified,
        "stimulus_ground_truth_excluded": (
            (evidence.get("evidence_snapshot") or {}).get("contains_raw_sensor_payload") in {0, False, None}
            and "stimulus ground truth is not approved" in note
            and all(not transition.get("consumed_by_perception_runtime", False) for transition in tuple(evidence.get("stimulus_manifests") or ()))
        ),
        "hard_coded_recognition_absent": (
            growth_audit.get("hard_coded_recognition_detected") is False
            and influence.get("hard_coded_experiment_match_used") is False
        ),
        "package_123_growth_audit_verified": growth_audit.get("audit_status") == "passed_no_codex_real_perception_two_cycle_growth_run",
        "package_123_transport_audit_verified": transport_audit.get("audit_status") == "passed_package_123_transport_integrity_repair",
    }


def _forbidden_claim_checks(evidence: dict[str, Any]) -> tuple[str, ...]:
    audit = dict(evidence.get("package_123_growth_audit") or {})
    reasons: list[str] = []
    if audit.get("time_perception_claimed"):
        reasons.append("time_perception_created")
    if audit.get("language_understanding_claimed"):
        reasons.append("language_understanding_created")
    if audit.get("qingyin_output_created"):
        reasons.append("qingyin_output_created")
    if audit.get("stimulus_ground_truth_entered_learning_path"):
        reasons.append("stimulus_ground_truth_entered_learning_path")
    return tuple(reasons)


def _audit_audio_timeline(evidence: dict[str, Any]) -> AudioTimelineContinuityAudit:
    cycle_one = dict(evidence.get("cycle_1_record") or {})
    audio_ids = tuple(cycle_one.get("audio_artifact_refs") or ())
    artifacts = dict(evidence.get("artifacts") or {})
    audio = [dict(artifacts.get(artifact_id) or {}) for artifact_id in audio_ids]
    audio = [item for item in audio if item]
    starts = [int(item.get("captured_at_monotonic_ns") or 0) for item in audio]
    durations = [int(item.get("capture_duration_ns") or 0) for item in audio]
    source_duration = 0
    if starts and durations:
        source_duration = max(starts[index] + durations[index] for index in range(len(starts))) - min(starts)
    normalized_duration = sum(durations)
    gaps = [starts[index + 1] - starts[index] for index in range(max(0, len(starts) - 1))]
    compression_detected = any(gap > 150_000_000 for gap in gaps) or normalized_duration < 11_900_000_000
    expansion_detected = normalized_duration > 12_100_000_000 or any(gap < 90_000_000 for gap in gaps)
    zero_pcm_segments = sum(1 for item in audio if bool(item.get("all_zero_pcm")))
    synthetic_segments = sum(1 for item in audio if bool((item.get("adapter_metadata") or {}).get("silence_fill_performed")))
    return AudioTimelineContinuityAudit(
        audit_id=stable_id("package_124_audio_timeline_continuity"),
        source_audio_duration_ns=source_duration,
        normalized_audio_duration_ns=normalized_duration,
        silent_gap_count=zero_pcm_segments,
        synthetic_zero_pcm_segment_count=synthetic_segments,
        timeline_compression_detected=compression_detected,
        timeline_expansion_beyond_tolerance_detected=expansion_detected,
        continuity_verified=bool(audio and not compression_detected and not expansion_detected and source_duration >= 11_900_000_000),
    )


def _audit_readback_timing(evidence: dict[str, Any]) -> MilestoneReadbackTimingAudit:
    timing = dict(evidence.get("readback_timing") or {})
    readback = dict(evidence.get("working_readback_commit") or {})
    return MilestoneReadbackTimingAudit(
        audit_id=stable_id("package_124_readback_timing"),
        working_readback_id=str(readback.get("working_readback_commit_id") or ""),
        cycle_2_session_id=PACKAGE_123_CYCLE_2_SESSION_ID,
        readback_loaded_monotonic_ns=int(timing.get("readback_loaded_monotonic_ns") or 0),
        capture_started_monotonic_ns=int(timing.get("capture_started_monotonic_ns") or 0) if timing.get("capture_started_monotonic_ns") is not None else None,
        stimulus_started_monotonic_ns=int(timing.get("stimulus_started_monotonic_ns") or 0),
        candidate_evaluated_monotonic_ns=int(timing.get("candidate_evaluated_monotonic_ns") or 0),
        loaded_before_capture=bool(timing.get("loaded_before_capture")) if timing else None,
        loaded_before_stimulus=bool(timing.get("loaded_before_stimulus")),
        loaded_before_candidate_evaluation=bool(timing.get("loaded_before_candidate_evaluation")),
        timing_verified=bool(timing.get("loaded_before_stimulus") and timing.get("loaded_before_candidate_evaluation")),
    )


def _audit_rejected_evidence_isolation(source: Path, evidence: dict[str, Any]) -> RejectedEvidenceIsolationAudit:
    dbs = _required_db_paths(source)
    teacher_decisions = _rows(dbs["teacher"], "teacher_decisions", "created_at")
    rejection = _find_row(teacher_decisions, decision="rejected", target_evidence_identity_sha256=PACKAGE_123_REJECTED_EVIDENCE_IDENTITY)
    rejected_session = str((rejection or {}).get("session_id") or "")
    reviewed = tuple(
        item
        for item in _rows(dbs["teacher"], "reviewed_interpretation_commits", "created_at")
        if item.get("session_id") == rejected_session or item.get("evidence_identity_sha256") == PACKAGE_123_REJECTED_EVIDENCE_IDENTITY
    )
    readbacks = tuple(
        item
        for item in _rows(dbs["teacher"], "working_readback_commits", "created_at")
        if item.get("session_id") == rejected_session or item.get("evidence_identity_sha256") == PACKAGE_123_REJECTED_EVIDENCE_IDENTITY
    )
    serialized_clean = json.dumps(
        {
            "cycle_1": evidence.get("cycle_1_record"),
            "cycle_2": evidence.get("cycle_2_record"),
            "comparison": evidence.get("two_cycle_comparison"),
            "influence": evidence.get("readback_influence"),
        },
        sort_keys=True,
    )
    referenced_by_clean = PACKAGE_123_REJECTED_EVIDENCE_IDENTITY in serialized_clean
    isolation_verified = bool(rejection and not reviewed and not readbacks and not referenced_by_clean)
    return RejectedEvidenceIsolationAudit(
        audit_id=stable_id("package_124_rejected_evidence_isolation"),
        rejected_evidence_identity=PACKAGE_123_REJECTED_EVIDENCE_IDENTITY,
        rejection_decision_id=str((rejection or {}).get("teacher_decision_id") or ""),
        reviewed_memory_created=bool(reviewed),
        working_readback_created=bool(readbacks),
        referenced_by_clean_cycle_1=referenced_by_clean,
        referenced_by_cycle_2=referenced_by_clean,
        isolation_verified=isolation_verified,
    )


def _build_preserved_pending_review(evidence: dict[str, Any]) -> PreservedPendingReviewRecord:
    cycle_two = dict(evidence.get("cycle_2_record") or {})
    return PreservedPendingReviewRecord(
        preservation_record_id=stable_id("package_124_preserved_cycle_2_pending_review"),
        created_at=utc_now(),
        pending_review_id=str(cycle_two.get("pending_teacher_review_id") or ""),
        session_id=PACKAGE_123_CYCLE_2_SESSION_ID,
        preservation_reason="cycle_2_teacher_gate_is_milestone_evidence_not_a_required_memory_commit",
        teacher_decision_applied=False,
        memory_commit_created=False,
        resume_allowed_from_milestone_archive=False,
    )


def _build_identity(
    source: Path,
    *,
    package_123_growth_audit_id: str,
    package_123_transport_audit_id: str,
    expected_commit: str,
) -> RealHostPerceptionGrowthMilestoneIdentity:
    payload = {
        "milestone_id": PACKAGE_124_MILESTONE_ID,
        "schema_version": PACKAGE_124_IDENTITY_SCHEMA_VERSION,
        "package_number": "124",
        "package_name": "ASHL Core v1 Real Host Perception Growth Loop Milestone Audit And Evidence Archive Minimal v0",
        "source_repository_commit": expected_commit,
        "source_state_dir": str(source),
        "cycle_1_session_id": PACKAGE_123_CYCLE_1_SESSION_ID,
        "cycle_1_evidence_identity": PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY,
        "cycle_2_session_id": PACKAGE_123_CYCLE_2_SESSION_ID,
        "package_123_growth_audit_id": package_123_growth_audit_id,
        "package_123_transport_audit_id": package_123_transport_audit_id,
    }
    identity_hash = sha256_payload(payload)
    return RealHostPerceptionGrowthMilestoneIdentity(
        created_at=utc_now(),
        identity_hash=identity_hash,
        **payload,
    )


def _public_evidence_summary(evidence: dict[str, Any]) -> dict[str, object]:
    cycle_one = dict(evidence.get("cycle_1_record") or {})
    cycle_two = dict(evidence.get("cycle_2_record") or {})
    transport = dict(evidence.get("cycle_1_transport_summary") or {})
    influence = dict(evidence.get("readback_influence") or {})
    return {
        "cycle_1_experiment_run_id": cycle_one.get("experiment_run_id"),
        "cycle_1_process_instance_id": cycle_one.get("process_instance_id"),
        "cycle_1_os_pid": cycle_one.get("operating_system_process_id"),
        "cycle_1_session_id": cycle_one.get("bounded_runtime_session_id"),
        "cycle_1_perception_session_id": cycle_one.get("perception_session_id"),
        "cycle_2_experiment_run_id": cycle_two.get("experiment_run_id"),
        "cycle_2_process_instance_id": cycle_two.get("process_instance_id"),
        "cycle_2_os_pid": cycle_two.get("operating_system_process_id"),
        "cycle_2_session_id": cycle_two.get("bounded_runtime_session_id"),
        "cycle_2_perception_session_id": cycle_two.get("perception_session_id"),
        "full_windows": transport.get("full_alignment_window_count"),
        "complete_windows": transport.get("complete_alignment_window_count"),
        "overlap_windows": transport.get("visual_audio_overlap_window_count"),
        "complete_overlap_windows": transport.get("complete_overlap_window_count"),
        "visual_change_regions": transport.get("visual_change_region_count"),
        "audio_change_regions": transport.get("audio_change_region_count"),
        "readback_contribution": influence.get("readback_contribution"),
        "scorer_id": influence.get("scorer_id"),
        "working_readback_commit_id": (evidence.get("working_readback_commit") or {}).get("working_readback_commit_id"),
        "package_123_growth_audit_id": (evidence.get("package_123_growth_audit") or {}).get("audit_id"),
        "package_123_transport_audit_id": (evidence.get("package_123_transport_audit") or {}).get("audit_id"),
    }


def _required_db_paths(source: Path) -> dict[str, Path]:
    return {
        "package_123": source / "package_123_real_perception_v0" / "package_123.sqlite3",
        "teacher": source / "ashl_bounded_session_v1.sqlite3",
        "sensor": source / "host_sensor_artifacts_v0" / "sensor_artifacts.sqlite3",
        "perception": source / "perception_primitives_v0" / "perception_primitives.sqlite3",
        "multimodal": source / "bounded_multimodal_perception_sessions_v0" / "multimodal_sessions.sqlite3",
    }


def _connect_ro(path: Path) -> sqlite3.Connection:
    uri = path.resolve().as_posix()
    connection = sqlite3.connect(f"file:{uri}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def _rows(path: Path, table: str, order: str) -> tuple[dict[str, Any], ...]:
    with closing(_connect_ro(path)) as connection:
        rows = connection.execute(f"SELECT * FROM {table} ORDER BY {order}").fetchall()
    return tuple(_decode_row(dict(row)) for row in rows)


def _payloads(path: Path, table: str) -> tuple[dict[str, Any], ...]:
    order = "row_id" if table.startswith("package_123") or table in {"stimulus_run_manifests", "two_cycle_comparison_records", "readback_influence_records", "readback_load_timing_records", "experience_source_profiles"} else "created_at"
    with closing(_connect_ro(path)) as connection:
        rows = connection.execute(f"SELECT payload_json FROM {table} ORDER BY {order}").fetchall()
    return tuple(json.loads(str(row["payload_json"])) for row in rows)


def _decode_row(row: dict[str, Any]) -> dict[str, Any]:
    decoded = dict(row)
    for key, value in list(decoded.items()):
        if isinstance(value, str) and value and value[0] in "[{":
            try:
                decoded[key] = json.loads(value)
            except Exception:
                pass
    return decoded


def _find_payload(payloads: tuple[dict[str, Any], ...], **matches: object) -> dict[str, Any]:
    for item in payloads:
        if all(item.get(key) == value for key, value in matches.items()):
            return dict(item)
    return {}


def _last_payload(payloads: tuple[dict[str, Any], ...], **matches: object) -> dict[str, Any]:
    found = [dict(item) for item in payloads if all(item.get(key) == value for key, value in matches.items())]
    return found[-1] if found else {}


def _find_row(rows: tuple[dict[str, Any], ...], **matches: object) -> dict[str, Any]:
    for item in rows:
        if all(item.get(key) == value for key, value in matches.items()):
            return dict(item)
    return {}


def _sensor_artifact(source: Path, artifact_id: str) -> dict[str, Any]:
    sensor_db = _required_db_paths(source)["sensor"]
    artifact = _find_payload(_payloads(sensor_db, "sensor_raw_artifacts"), artifact_id=artifact_id)
    if not artifact:
        raise KeyError(f"missing artifact: {artifact_id}")
    relative_blob_path = Path(str(artifact["blob_relative_path"]))
    blob_path = source / "host_sensor_artifacts_v0" / relative_blob_path
    if relative_blob_path.is_absolute() or ".." in relative_blob_path.parts:
        raise ValueError(f"artifact path escapes state_dir: {artifact_id}")
    data = blob_path.read_bytes()
    artifact["blob_exists"] = blob_path.exists()
    artifact["blob_sha256_valid"] = sha256_bytes(data) == artifact.get("content_sha256")
    artifact["blob_length_valid"] = len(data) == int(artifact.get("byte_length") or -1)
    artifact["all_zero_pcm"] = artifact.get("source_kind") == "microphone" and bool(data) and all(byte == 0 for byte in data)
    trace_id = str(artifact.get("trace_envelope_id") or "")
    if trace_id:
        trace = _find_row(_rows(sensor_db, "sensor_trace_envelopes", "created_at"), trace_id=trace_id)
        artifact["adapter_metadata"] = (trace.get("payload_snapshot_json") or trace.get("payload_snapshot") or {}).get("adapter_metadata", {})
    return artifact


def _artifact_valid_for_kind(artifact: dict[str, Any], artifact_id: str) -> bool:
    if not artifact:
        return False
    adapter = str(artifact.get("adapter_id") or "")
    source_kind = str(artifact.get("source_kind") or "")
    expected = (
        source_kind == "screen" and adapter.startswith("windows_window_capture")
        or source_kind == "microphone" and adapter.startswith("windows_wasapi_loopback")
        or source_kind == "host_state" and adapter.startswith("host_state")
    )
    return bool(
        artifact.get("artifact_id") == artifact_id
        and artifact.get("real_device_capture") is True
        and artifact.get("blob_exists")
        and artifact.get("blob_sha256_valid")
        and artifact.get("blob_length_valid")
        and expected
    )


def _primitive_ids_for_cycles(perception_db: Path, cycle_one: dict[str, Any], cycle_two: dict[str, Any]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    readable = {item["perception_id"]: item for item in _payloads(perception_db, "perception_readable_data")}

    def ids_for(cycle: dict[str, Any]) -> tuple[str, ...]:
        ids: list[str] = []
        for perception_id in tuple(cycle.get("perception_readable_data_refs") or ()):
            payload = dict(readable.get(perception_id, {}).get("readable_payload") or {})
            primitive_id = payload.get("primitive_record_id")
            if primitive_id:
                ids.append(str(primitive_id))
        return tuple(dict.fromkeys(ids))

    return ids_for(cycle_one), ids_for(cycle_two)


def _runtime_counters(growth_audit: dict[str, Any], comparison: dict[str, Any]) -> dict[str, int]:
    return {
        "llm_runtime_calls": int(growth_audit.get("llm_runtime_calls") or 0),
        "codex_runtime_calls": int(growth_audit.get("codex_runtime_calls") or 0),
        "network_runtime_calls": int(growth_audit.get("network_runtime_calls") or 0),
        "comparison_no_llm_runtime": 1 if comparison.get("no_llm_runtime") else 0,
        "comparison_no_codex_runtime": 1 if comparison.get("no_codex_runtime") else 0,
        "comparison_no_network_runtime": 1 if comparison.get("no_network_runtime") else 0,
    }


def _outside_repository(path: Path) -> bool:
    repo = Path.cwd().resolve()
    try:
        path.resolve().relative_to(repo)
        return False
    except ValueError:
        return True
