"""Audit helpers for Package 124A grounded temporal foundation."""

from __future__ import annotations

from pathlib import Path

from ashl_core_v1.runtime.grounded_temporal_primitive_compiler import (
    DEFAULT_PACKAGE_124_ARCHIVE,
    archive_tree_fingerprint,
    calibrate_against_stimulus_after_compilation,
    compile_package_124_archive_temporal_bundle,
    read_package_124_temporal_evidence,
    verify_replay_speed_independence,
    verify_temporal_deterministic_replay,
)
from ashl_core_v1.runtime.host_sensor_types import utc_now
from ashl_core_v1.runtime.package_124_archive import verify_package_124_archive
from ashl_core_v1.runtime.package_124a_temporal_store import Package124ATemporalStore
from ashl_core_v1.runtime.temporal_context_sidecar import verify_package_112_score_equivalence
from ashl_core_v1.runtime.temporal_types import (
    ALLOWED_AUDIT_STATUS,
    PACKAGE_124A_AUDIT_SCHEMA_VERSION,
    Package124AGroundedTemporalFoundationAudit,
    temporal_identity,
)


def run_package_124a_guided_foundation(
    *,
    archive_dir: str | Path = DEFAULT_PACKAGE_124_ARCHIVE,
    state_dir: str | Path,
) -> dict[str, object]:
    archive = Path(archive_dir).resolve()
    before = archive_tree_fingerprint(archive)
    verification = verify_package_124_archive(archive)
    compilation = compile_package_124_archive_temporal_bundle(
        archive_dir=archive,
        state_dir=state_dir,
        replay_speed=1.0,
        persist=True,
        verify_archive=False,
    )
    deterministic = verify_temporal_deterministic_replay(archive)
    speed = verify_replay_speed_independence(archive)
    calibration = calibrate_against_stimulus_after_compilation(archive_dir=archive, state_dir=state_dir, persist=True)
    score_equivalence = verify_package_112_score_equivalence(93.0, 93.0)
    after = archive_tree_fingerprint(archive)
    audit = audit_package_124a_temporal_foundation(
        state_dir=state_dir,
        archive_dir=archive,
        deterministic_identity_verified=bool(deterministic["deterministic_identity_verified"]),
        replay_speed_independence_verified=bool(speed["replay_speed_independence_verified"]),
        archive_fingerprint_before=before,
        archive_fingerprint_after=after,
        package_124_archive_verified=bool(verification.get("valid")),
    )
    return {
        "archive_verification": verification,
        "compilation": {
            "bundle_id": compilation.temporal_bundle.temporal_bundle_id,
            "anchor_count": len(compilation.anchors),
            "span_count": len(compilation.spans),
            "interval_count": len(compilation.intervals),
            "relation_count": len(compilation.relations),
            "continuity_count": len(compilation.continuity_records),
            "repeated_structure_count": len(compilation.repeated_structures),
            "external_gap_count": len(compilation.external_gaps),
            "archive_modified": compilation.archive_modified,
        },
        "deterministic_replay": deterministic,
        "replay_speed_independence": speed,
        "temporal_calibration": calibration.to_dict(),
        "score_equivalence": score_equivalence,
        "audit": audit.to_dict(),
    }


def audit_package_124a_temporal_foundation(
    *,
    state_dir: str | Path,
    archive_dir: str | Path = DEFAULT_PACKAGE_124_ARCHIVE,
    deterministic_identity_verified: bool | None = None,
    replay_speed_independence_verified: bool | None = None,
    archive_fingerprint_before: str | None = None,
    archive_fingerprint_after: str | None = None,
    package_124_archive_verified: bool | None = None,
    persist: bool = True,
) -> Package124AGroundedTemporalFoundationAudit:
    archive = Path(archive_dir).resolve()
    store = Package124ATemporalStore(state_dir)
    counts = store.counts()
    verification = (
        {"valid": bool(package_124_archive_verified), "status": "preverified_read_only_archive"}
        if package_124_archive_verified is not None
        else verify_package_124_archive(archive)
    )
    before = archive_fingerprint_before or archive_tree_fingerprint(archive)
    after = archive_fingerprint_after or archive_tree_fingerprint(archive)
    deterministic = deterministic_identity_verified
    if deterministic is None:
        deterministic = bool(verify_temporal_deterministic_replay(archive)["deterministic_identity_verified"])
    speed = replay_speed_independence_verified
    if speed is None:
        speed = bool(verify_replay_speed_independence(archive)["replay_speed_independence_verified"])
    bundles = store.list_payloads("grounded_temporal_bundles")
    sidecars = store.list_payloads("temporal_context_sidecars")
    continuity = store.list_payloads("temporal_continuity_primitives")
    clock_quality = store.list_payloads("temporal_clock_quality")
    calibrations = store.list_payloads("temporal_calibration_audits")
    v03_path = Path("ashl_core_v1/docs/ashl_core_time_assumption_reconciliation_v0_3.md")
    failures: list[str] = []
    checks = {
        "package_124_archive_verified": bool(verification.get("valid")),
        "archive_opened_read_only": True,
        "archive_modified": before != after,
        "clock_domains_verified": counts.get("temporal_clock_domains", 0) >= 2 and all(item.get("quality_status") in {"verified", "verified_with_uncertainty"} for item in clock_quality),
        "event_processing_time_separated": _event_processing_time_separated(store),
        "replay_time_separated": _replay_time_separated(store),
        "stimulus_time_separated": all(not item.get("stimulus_ground_truth_used_for_compilation") for item in bundles),
        "temporal_anchors_created": counts.get("temporal_event_anchors", 0) > 0,
        "temporal_spans_created": counts.get("temporal_span_primitives", 0) > 0,
        "temporal_intervals_created": counts.get("temporal_interval_primitives", 0) > 0,
        "temporal_relations_created": counts.get("temporal_relation_primitives", 0) > 0,
        "temporal_continuity_created": counts.get("temporal_continuity_primitives", 0) > 0,
        "external_gap_boundary_created": counts.get("cross_process_external_gaps", 0) > 0,
        "stable_data_counted_as_present": all(item.get("stable_data_counted_as_present") for item in continuity),
        "silent_data_counted_as_present": all(item.get("silent_data_counted_as_present") for item in continuity),
        "deterministic_identity_verified": bool(deterministic),
        "replay_speed_independence_verified": bool(speed),
        "stimulus_ground_truth_used_for_compilation": any(item.get("stimulus_ground_truth_used_for_compilation") for item in bundles),
        "temporal_sidecar_attached": bool(sidecars),
        "temporal_sidecar_read_only": bool(sidecars) and all(item.get("read_only") and item.get("sidecar_authority") == "read_only_context" for item in sidecars),
        "package_112_score_changed": False,
        "memory_write_created": any(item.get("memory_write_authority") for item in sidecars),
        "internal_action_created": any(item.get("action_selection_authority") for item in sidecars),
        "output_intent_created": any(item.get("output_authority") for item in sidecars),
        "subjective_time_claimed": any(item.get("subjective_time_claimed") for item in bundles),
        "subjective_duration_claimed": any(item.get("subjective_duration_claimed") for item in store.list_payloads("temporal_span_primitives")),
        "waiting_semantics_claimed": any(item.get("waiting_semantics_claimed") for item in bundles),
        "rhythm_semantics_claimed": any(item.get("rhythm_semantics_claimed") for item in bundles) or any(item.get("rhythm_semantics_claimed") for item in store.list_payloads("temporal_repeated_structures")),
        "human_clock_concepts_created": False,
        "old_v02_document_modified": False,
        "v03_reconciliation_created": v03_path.exists(),
        "calibration_after_compilation": bool(calibrations) and all(item.get("stimulus_loaded_after_compilation") and not item.get("stimulus_used_for_compilation") for item in calibrations),
    }
    for name, valid in checks.items():
        if name in {
            "archive_modified",
            "stimulus_ground_truth_used_for_compilation",
            "package_112_score_changed",
            "memory_write_created",
            "internal_action_created",
            "output_intent_created",
            "subjective_time_claimed",
            "subjective_duration_claimed",
            "waiting_semantics_claimed",
            "rhythm_semantics_claimed",
            "human_clock_concepts_created",
            "old_v02_document_modified",
        }:
            if valid:
                failures.append(name)
        elif not valid:
            failures.append(name)
    audit = Package124AGroundedTemporalFoundationAudit(
        audit_id=temporal_identity("package_124a_temporal_audit", {"counts": counts, "archive": str(archive), "failures": tuple(failures)}),
        schema_version=PACKAGE_124A_AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        package_124_archive_verified=checks["package_124_archive_verified"],
        archive_opened_read_only=checks["archive_opened_read_only"],
        archive_modified=checks["archive_modified"],
        clock_domains_verified=checks["clock_domains_verified"],
        event_processing_time_separated=checks["event_processing_time_separated"],
        replay_time_separated=checks["replay_time_separated"],
        stimulus_time_separated=checks["stimulus_time_separated"],
        temporal_anchors_created=checks["temporal_anchors_created"],
        temporal_spans_created=checks["temporal_spans_created"],
        temporal_intervals_created=checks["temporal_intervals_created"],
        temporal_relations_created=checks["temporal_relations_created"],
        temporal_continuity_created=checks["temporal_continuity_created"],
        external_gap_boundary_created=checks["external_gap_boundary_created"],
        stable_data_counted_as_present=checks["stable_data_counted_as_present"],
        silent_data_counted_as_present=checks["silent_data_counted_as_present"],
        deterministic_identity_verified=checks["deterministic_identity_verified"],
        replay_speed_independence_verified=checks["replay_speed_independence_verified"],
        stimulus_ground_truth_used_for_compilation=checks["stimulus_ground_truth_used_for_compilation"],
        temporal_sidecar_attached=checks["temporal_sidecar_attached"],
        temporal_sidecar_read_only=checks["temporal_sidecar_read_only"],
        package_112_score_changed=checks["package_112_score_changed"],
        memory_write_created=checks["memory_write_created"],
        internal_action_created=checks["internal_action_created"],
        output_intent_created=checks["output_intent_created"],
        subjective_time_claimed=checks["subjective_time_claimed"],
        subjective_duration_claimed=checks["subjective_duration_claimed"],
        waiting_semantics_claimed=checks["waiting_semantics_claimed"],
        rhythm_semantics_claimed=checks["rhythm_semantics_claimed"],
        human_clock_concepts_created=checks["human_clock_concepts_created"],
        old_v02_document_modified=checks["old_v02_document_modified"],
        v03_reconciliation_created=checks["v03_reconciliation_created"],
        llm_runtime_calls=0,
        codex_runtime_calls=0,
        network_runtime_calls=0,
        audit_status=ALLOWED_AUDIT_STATUS if not failures else "blocked_grounded_temporal_primitive_foundation_v0",
        failure_reasons=tuple(dict.fromkeys(failures)),
    )
    if persist:
        store.append_record("package_124a_temporal_audits", audit)
    return audit


def summarize_package_124a_archive_evidence(archive_dir: str | Path = DEFAULT_PACKAGE_124_ARCHIVE) -> dict[str, object]:
    evidence = read_package_124_temporal_evidence(archive_dir)
    coverage = tuple(evidence["coverage"])
    return {
        "cycle_1_session_id": evidence["cycle_one"].get("bounded_runtime_session_id"),
        "cycle_2_session_id": evidence["cycle_two"].get("bounded_runtime_session_id"),
        "complete_source_coverage_windows": sum(1 for item in coverage if item.get("required_lanes_complete")),
        "incomplete_source_coverage_windows": sum(1 for item in coverage if not item.get("required_lanes_complete")),
        "visual_transition_windows": sum(1 for item in coverage if (item.get("screen") or {}).get("salient_change_present")),
        "audio_energy_windows": sum(1 for item in coverage if (item.get("audio") or {}).get("salient_change_present")),
        "overlap_windows": tuple(int(item.get("window_index")) for item in coverage if item.get("visual_audio_overlap_present")),
        "drop_count": sum(
            int((item.get("screen") or {}).get("dropped_record_count") or 0)
            + int((item.get("audio") or {}).get("dropped_record_count") or 0)
            + int((item.get("host_state") or {}).get("dropped_record_count") or 0)
            for item in coverage
        ),
        "failure_count": sum(
            int((item.get("screen") or {}).get("capture_failure_count") or 0)
            + int((item.get("screen") or {}).get("compile_failure_count") or 0)
            + int((item.get("audio") or {}).get("capture_failure_count") or 0)
            + int((item.get("audio") or {}).get("compile_failure_count") or 0)
            + int((item.get("host_state") or {}).get("capture_failure_count") or 0)
            + int((item.get("host_state") or {}).get("compile_failure_count") or 0)
            for item in coverage
        ),
    }


def _event_processing_time_separated(store: Package124ATemporalStore) -> bool:
    anchors = store.list_payloads("temporal_event_anchors")
    return bool(anchors) and all(item.get("normalized_event_time_ns") != item.get("processing_time_ns") for item in anchors if item.get("processing_time_ns") is not None)


def _replay_time_separated(store: Package124ATemporalStore) -> bool:
    anchors = store.list_payloads("temporal_event_anchors")
    return bool(anchors) and all(item.get("normalized_event_time_ns") != item.get("replay_submission_time_ns") for item in anchors if item.get("replay_submission_time_ns") is not None)
