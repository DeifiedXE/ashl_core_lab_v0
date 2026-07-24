"""CLI for Package 123 no-Codex real perception two-cycle growth run."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain
from ashl_core_v1.perception.perception_primitive_store import PerceptionPrimitiveStore
from ashl_core_v1.runtime.bounded_multimodal_perception_session_runtime import MultimodalPerceptionSessionStore
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore
from ashl_core_v1.runtime.package_123_cycle_runtime import (
    capture_package_123_sources,
    review_cycle_one,
    run_cycle_one,
    run_cycle_two,
    run_transport_soak,
)
from ashl_core_v1.runtime.package_123_cycle_store import Package123CycleStore, strip_package_123_raw_media
from ashl_core_v1.runtime.package_123_growth_audit import audit_package_123_real_perception_growth, audit_package_123_transport_repair
from ashl_core_v1.runtime.package_123_preflight import run_package_123_preflight
from ashl_core_v1.runtime.package_123_types import EXPERIMENT_ID, new_experiment_run_id, new_process_instance_id
from ashl_core_v1.runtime.package_123_transport_integrity import coverage_records_for_review
from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore
from ashl_core_v1.runtime.windows_wasapi_loopback_source import list_loopback_sources


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package 123 real perception two-cycle growth run")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-audio-endpoints")

    preflight = sub.add_parser("preflight")
    preflight.add_argument("--state-dir", required=True)
    preflight.add_argument("--render-endpoint", default="default")
    preflight.add_argument("--allow-dirty-tree", action="store_true", help=argparse.SUPPRESS)

    cycle1 = sub.add_parser("run-cycle-1")
    cycle1.add_argument("--state-dir", required=True)
    cycle1.add_argument("--render-endpoint", default="default")
    cycle1.add_argument("--allow-dirty-tree", action="store_true", help=argparse.SUPPRESS)
    cycle1.add_argument("--require-passed-transport-soak", action="store_true")

    review_show = sub.add_parser("show-cycle-1-review")
    review_show.add_argument("--state-dir", required=True)
    review_show.add_argument("--verbose-windows", action="store_true")

    review = sub.add_parser("review-cycle-1")
    review.add_argument("--state-dir", required=True)
    review.add_argument("--decision", required=True, choices=("approve", "approved", "reject", "rejected"))
    review.add_argument("--reviewer", required=True)
    review.add_argument("--approval-text")
    review.add_argument("--reason")
    review.add_argument("--reason-file")
    review.add_argument("--pending-review-id")
    review.add_argument("--evidence-snapshot-id")
    review.add_argument("--evidence-identity")
    review.add_argument("--required-scope")
    review.add_argument("--allowed-interpretation-scope")
    review.add_argument("--confirm", action="store_true")

    soak = sub.add_parser("transport-soak")
    soak.add_argument("--state-dir", required=True)
    soak.add_argument("--render-endpoint", default="default")
    soak.add_argument("--allow-dirty-tree", action="store_true", help=argparse.SUPPRESS)

    show_soak = sub.add_parser("show-transport-soak")
    show_soak.add_argument("--state-dir", required=True)

    show_integrity = sub.add_parser("show-transport-integrity")
    show_integrity.add_argument("--state-dir", required=True)
    show_integrity.add_argument("--cycle", type=int, default=1)

    show_lineage = sub.add_parser("show-rerun-lineage")
    show_lineage.add_argument("--state-dir", required=True)

    cycle2 = sub.add_parser("run-cycle-2")
    cycle2.add_argument("--state-dir", required=True)
    cycle2.add_argument("--render-endpoint", default="default")
    cycle2.add_argument("--allow-dirty-tree", action="store_true", help=argparse.SUPPRESS)

    comparison = sub.add_parser("show-comparison")
    comparison.add_argument("--state-dir", required=True)

    audit = sub.add_parser("audit")
    audit.add_argument("--state-dir", required=True)

    repair_audit = sub.add_parser("audit-transport-repair")
    repair_audit.add_argument("--state-dir", required=True)
    repair_audit.add_argument("--rejected-evidence-identity", required=True)

    cleanup = sub.add_parser("cleanup-raw-evidence")
    cleanup.add_argument("--state-dir", required=True)
    cleanup.add_argument("--experiment-id", required=True)
    cleanup.add_argument("--confirm", action="store_true")

    guided = sub.add_parser("guided-run")
    guided.add_argument("--state-dir", required=True)

    smoke = sub.add_parser("real-smoke")
    smoke.add_argument("--state-dir", required=True)
    smoke.add_argument("--render-endpoint", default="default")
    smoke.add_argument("--allow-dirty-tree", action="store_true", help=argparse.SUPPRESS)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "list-audio-endpoints":
        return _print_json({"audio_endpoints": [item.to_dict() for item in list_loopback_sources()]})
    if args.command == "preflight":
        record = run_package_123_preflight(
            state_dir=args.state_dir,
            render_endpoint=args.render_endpoint,
            allow_dirty_tree=args.allow_dirty_tree,
        )
        return _print_json(record.to_dict())
    if args.command == "run-cycle-1":
        return _print_json(
            run_cycle_one(
                state_dir=args.state_dir,
                render_endpoint=args.render_endpoint,
                allow_dirty_tree=args.allow_dirty_tree,
                require_passed_transport_soak=args.require_passed_transport_soak,
            )
        )
    if args.command == "show-cycle-1-review":
        return _print_json(show_cycle_one_review(args.state_dir, verbose_windows=args.verbose_windows))
    if args.command == "review-cycle-1":
        note = _review_note_from_args(args)
        return _print_json(
            review_cycle_one(
                state_dir=args.state_dir,
                decision=args.decision,
                reviewer=args.reviewer,
                approval_text=note,
                confirm=args.confirm,
                pending_review_id=args.pending_review_id,
                evidence_snapshot_id=args.evidence_snapshot_id,
                evidence_identity=args.evidence_identity,
                required_scope=args.required_scope,
                allowed_interpretation_scope=args.allowed_interpretation_scope,
            )
        )
    if args.command == "transport-soak":
        return _print_json(run_transport_soak(state_dir=args.state_dir, render_endpoint=args.render_endpoint, allow_dirty_tree=args.allow_dirty_tree))
    if args.command == "show-transport-soak":
        store = Package123CycleStore(args.state_dir)
        return _print_json(store.latest_payload("package_123_transport_soak_records") or {"found": False})
    if args.command == "show-transport-integrity":
        return _print_json(show_transport_integrity(args.state_dir, cycle_index=args.cycle))
    if args.command == "show-rerun-lineage":
        store = Package123CycleStore(args.state_dir)
        return _print_json({"lineage_records": store.list_payloads("package_123_rerun_lineage")})
    if args.command == "run-cycle-2":
        return _print_json(run_cycle_two(state_dir=args.state_dir, render_endpoint=args.render_endpoint, allow_dirty_tree=args.allow_dirty_tree))
    if args.command == "show-comparison":
        store = Package123CycleStore(args.state_dir)
        return _print_json(store.latest_payload("two_cycle_comparison_records") or {"found": False})
    if args.command == "audit":
        return _print_json(audit_package_123_real_perception_growth(args.state_dir).to_dict())
    if args.command == "audit-transport-repair":
        return _print_json(
            audit_package_123_transport_repair(
                args.state_dir,
                rejected_evidence_identity=args.rejected_evidence_identity,
            ).to_dict()
        )
    if args.command == "cleanup-raw-evidence":
        if args.experiment_id != EXPERIMENT_ID:
            raise SystemExit(f"--experiment-id must be {EXPERIMENT_ID}")
        if not args.confirm:
            raise SystemExit("--confirm is required")
        return _print_json(
            {
                "status": "manual_audio_deletion_required_via_package_120a",
                "experiment_id": EXPERIMENT_ID,
                "raw_evidence_deleted_by_package_123": False,
                "message": "Use Package 120A artifact deletion commands for explicit hash-bound waveform deletion.",
            }
        )
    if args.command == "guided-run":
        return _print_json(guided_run(args.state_dir))
    if args.command == "real-smoke":
        preflight = run_package_123_preflight(
            state_dir=args.state_dir,
            render_endpoint=args.render_endpoint,
            allow_dirty_tree=args.allow_dirty_tree,
        )
        if preflight.preflight_status != "passed":
            return _print_json({"status": "blocked_preflight", "preflight": preflight.to_dict()})
        capture = capture_package_123_sources(
            state_dir=args.state_dir,
            experiment_run_id=new_experiment_run_id(),
            process_instance_id=new_process_instance_id(),
            render_endpoint=args.render_endpoint,
            duration_ms=4000,
        )
        return _print_json(
            {
                "status": "real_smoke_completed",
                "screen_artifacts": capture["screen_artifact_ids"],
                "audio_artifacts": capture["audio_artifact_ids"],
                "host_state_artifacts": capture["host_state_artifact_ids"],
                "learning_session_created": False,
                "memory_commit_created": False,
            }
        )
    raise SystemExit(f"unknown command: {args.command}")


def show_cycle_one_review(state_dir: str | Path, *, verbose_windows: bool = False) -> dict[str, object]:
    package_store = Package123CycleStore(state_dir)
    cycle = package_store.latest_cycle_record(1)
    if not cycle:
        return {"found": False, "reason": "no_cycle_1_record"}
    teacher_store = TeacherGatedSessionStore(state_dir)
    pending_id = str(cycle["pending_teacher_review_id"])
    review = teacher_store.get_pending_review(pending_id)
    snapshot = teacher_store.load_evidence_snapshot(review.evidence_snapshot_id)
    return {
        "found": True,
        "cycle_record": strip_package_123_raw_media(cycle),
        "low_level_perception_evidence": _build_review_evidence_summary(state_dir, cycle),
        "transport_integrity": _build_transport_review_summary(state_dir, cycle, verbose_windows=verbose_windows),
        "pending_teacher_review": review.to_dict(),
        "evidence_snapshot": snapshot.to_dict(),
        "stimulus_ground_truth_displayed_as_candidate": False,
        "raw_media_displayed": False,
        "allowed_interpretation_scope": "low_level_observed_multimodal_pattern_only",
    }


def show_transport_integrity(state_dir: str | Path, *, cycle_index: int) -> dict[str, object]:
    store = Package123CycleStore(state_dir)
    summaries = tuple(
        item
        for item in store.list_payloads("package_123_transport_integrity_summaries")
        if int(item.get("cycle_index", -1)) == int(cycle_index)
    )
    if not summaries:
        return {"found": False, "cycle_index": cycle_index}
    summary = summaries[-1]
    coverage = tuple(
        item
        for item in store.list_payloads("package_123_alignment_window_coverage")
        if item.get("integrity_summary_id") == summary.get("integrity_summary_id")
        or (
            item.get("experiment_run_id") == summary.get("experiment_run_id")
            and int(item.get("cycle_index", -1)) == int(cycle_index)
        )
    )
    return {
        "found": True,
        "transport_integrity_summary": summary,
        "alignment_window_coverage": coverage,
        "fault_records": tuple(
            item
            for item in store.list_payloads("package_123_transport_faults")
            if item.get("experiment_run_id") == summary.get("experiment_run_id")
            and int(item.get("cycle_index", -1)) == int(cycle_index)
        ),
    }


def guided_run(state_dir: str | Path) -> dict[str, object]:
    return {
        "status": "guided_package_123_steps",
        "state_dir": str(state_dir),
        "step_1": f"py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli real-smoke --state-dir {state_dir} --render-endpoint default",
        "step_2": f"py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli transport-soak --state-dir {state_dir} --render-endpoint default",
        "step_3": f"py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli run-cycle-1 --state-dir {state_dir} --render-endpoint default --require-passed-transport-soak",
        "step_4": f"py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli show-cycle-1-review --state-dir {state_dir} --verbose-windows",
        "step_5": f"py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli review-cycle-1 --state-dir {state_dir} --decision approve --reviewer local_teacher --approval-text \"I approve this exact low-level observed multimodal pattern only.\" --confirm",
        "step_6_new_process": f"py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli run-cycle-2 --state-dir {state_dir} --render-endpoint default",
        "step_5_new_process": f"py -3 -m ashl_core_v1.runtime.package_123_real_perception_cli run-cycle-2 --state-dir {state_dir} --render-endpoint default",
        "this_command_keeps_process_alive_across_cycles": False,
    }


def _review_note_from_args(args: argparse.Namespace) -> str | None:
    if args.reason and args.approval_text:
        raise SystemExit("use either --reason or --approval-text, not both")
    if args.reason_file and (args.reason or args.approval_text):
        raise SystemExit("use --reason-file without --reason or --approval-text")
    if args.reason_file:
        return Path(args.reason_file).read_text(encoding="utf-8")
    return args.reason or args.approval_text


def _build_transport_review_summary(
    state_dir: str | Path,
    cycle: dict[str, object],
    *,
    verbose_windows: bool,
) -> dict[str, object]:
    store = Package123CycleStore(state_dir)
    experiment_run_id = str(cycle.get("experiment_run_id") or "")
    summaries = tuple(
        item
        for item in store.list_payloads("package_123_transport_integrity_summaries")
        if item.get("experiment_run_id") == experiment_run_id and int(item.get("cycle_index", -1)) == 1
    )
    if not summaries:
        return {"found": False, "reason": "no_transport_integrity_summary_for_cycle"}
    summary = summaries[-1]
    coverage = tuple(
        item
        for item in store.list_payloads("package_123_alignment_window_coverage")
        if item.get("experiment_run_id") == experiment_run_id and int(item.get("cycle_index", -1)) == 1
    )
    payload = {
        "found": True,
        "summary": summary,
        "readiness": tuple(
            item
            for item in store.list_payloads("package_123_transport_lane_readiness")
            if item.get("experiment_run_id") == experiment_run_id and int(item.get("cycle_index", -1)) == 1
        ),
        "flush": tuple(
            item
            for item in store.list_payloads("package_123_transport_flush_records")
            if item.get("experiment_run_id") == experiment_run_id and int(item.get("cycle_index", -1)) == 1
        ),
        "faults": tuple(
            item
            for item in store.list_payloads("package_123_transport_faults")
            if item.get("experiment_run_id") == experiment_run_id and int(item.get("cycle_index", -1)) == 1
        ),
        "window_table": _window_review_table(coverage, verbose=verbose_windows),
    }
    return payload


def _window_review_table(coverage: tuple[dict[str, object], ...], *, verbose: bool) -> tuple[dict[str, object], ...]:
    rows = coverage_records_for_review({"alignment_window_coverage": coverage}, verbose=verbose)
    return tuple(
        {
            "window_index": item.get("window_index"),
            "alignment_window_id": item.get("alignment_window_id"),
            "time_range_ms": (
                int(int(item.get("start_event_time_ns") or 0) / 1_000_000),
                int(int(item.get("end_event_time_ns") or 0) / 1_000_000),
            ),
            "screen": _lane_window_cell(item.get("screen") or {}),
            "audio": _lane_window_cell(item.get("audio") or {}),
            "host_state": _lane_window_cell(item.get("host_state") or {}, include_sample_count=True),
            "required_lanes_complete": item.get("required_lanes_complete"),
            "visual_audio_overlap": item.get("visual_audio_overlap_present"),
            "failure_reasons": item.get("incomplete_reason_codes"),
        }
        for item in rows
    )


def _lane_window_cell(payload: dict[str, object], *, include_sample_count: bool = False) -> dict[str, object]:
    cell = {
        "source": bool(payload.get("source_artifact_present")),
        "primitive": bool(payload.get("compiled_primitive_present")),
        "delivered": bool(payload.get("delivered_to_alignment")),
        "salient": bool(payload.get("salient_change_present")),
        "drops": int(payload.get("dropped_record_count") or 0),
    }
    if include_sample_count:
        cell["sample_count"] = len(tuple(payload.get("source_artifact_refs") or ()))
    return cell


def _build_review_evidence_summary(state_dir: str | Path, cycle: dict[str, object]) -> dict[str, object]:
    perception_store = PerceptionPrimitiveStore(state_dir)
    multimodal_store = MultimodalPerceptionSessionStore(state_dir)
    sensor_store = ContentAddressedSensorArtifactStore(state_dir)
    perception_ids = tuple(str(item) for item in cycle.get("perception_readable_data_refs", ()) or ())
    readable_rows = []
    primitive_summaries = []
    for perception_id in perception_ids:
        try:
            readable = perception_store.get_perception_readable_data(perception_id)
        except KeyError:
            continue
        payload = dict(readable.get("readable_payload") or {})
        primitive_id = str(payload.get("primitive_record_id") or "")
        readable_rows.append(
            {
                "perception_id": readable.get("perception_id"),
                "source_kind": readable.get("source_kind"),
                "readable_type": readable.get("readable_type"),
                "uncertainty": readable.get("uncertainty"),
                "primitive_record_id": primitive_id,
                "source_trace_refs": readable.get("source_trace_refs", ()),
            }
        )
        if primitive_id:
            try:
                primitive_summaries.append(_primitive_review_summary(perception_store.get_primitive(primitive_id)))
            except KeyError:
                primitive_summaries.append({"primitive_record_id": primitive_id, "status": "missing"})
    session_id = str(cycle.get("perception_session_id") or "")
    windows = tuple(
        item
        for item in multimodal_store.list_payloads("multimodal_alignment_windows")
        if item.get("session_id") == session_id
    )
    lane_items = tuple(
        item
        for item in multimodal_store.list_payloads("perception_lane_items")
        if item.get("session_id") == session_id
    )
    lane_item_by_id = {str(item.get("lane_item_id")): item for item in lane_items}
    primitive_to_lane_items: dict[str, list[dict[str, object]]] = {}
    artifact_to_lane_items: dict[str, list[dict[str, object]]] = {}
    for item in lane_items:
        primitive_to_lane_items.setdefault(str(item.get("primitive_record_id")), []).append(item)
        artifact_to_lane_items.setdefault(str(item.get("source_artifact_id")), []).append(item)
    primitive_by_id = {
        str(item.get("primitive_record_id")): item
        for item in primitive_summaries
        if item.get("primitive_record_id")
    }
    window_by_lane_item_id = _window_refs_by_lane_item(windows)
    bridges = tuple(
        item
        for item in multimodal_store.list_payloads("perception_host_body_event_bridges")
        if item.get("session_id") == session_id
    )
    backpressure = tuple(
        item
        for item in multimodal_store.list_payloads("perception_backpressure_records")
        if item.get("session_id") == session_id
    )
    dropped = tuple(
        item
        for item in multimodal_store.list_payloads("perception_dropped_sample_records")
        if item.get("session_id") == session_id
    )
    sensor_failures = tuple(sensor_store.list_failures())
    compilation_failures = tuple(perception_store.list_compilation_failures())
    visual_change_regions = _visual_change_regions(primitive_summaries)
    audio_change_regions = _audio_change_regions(primitive_summaries)
    overlap_windows = _multimodal_overlap_windows(windows, lane_item_by_id, primitive_by_id)
    incomplete_windows = _incomplete_window_summaries(windows, overlap_windows)
    backpressure_details = _backpressure_details(
        backpressure,
        primitive_to_lane_items,
        window_by_lane_item_id,
        overlap_windows,
    )
    dropped_details = _dropped_sample_details(
        dropped,
        artifact_to_lane_items,
        window_by_lane_item_id,
        overlap_windows,
    )
    backpressure_summary = _summarize_records_by_source_and_policy(backpressure, "policy", "action_taken")
    dropped_summary = _summarize_records_by_source_and_policy(dropped, "drop_policy", "reason_code")
    drop_counts = _drop_counts_by_required_lane(dropped)
    required_lane_failure_summary = _required_lane_failure_summary(sensor_failures, compilation_failures)
    review_rule_assessment = _review_rule_assessment(
        overlap_windows=overlap_windows,
        drop_counts=drop_counts,
        required_lane_failure_summary=required_lane_failure_summary,
        backpressure_details=backpressure_details,
    )
    return {
        "perception_readable_data_count": len(readable_rows),
        "perception_readable_data": tuple(readable_rows),
        "primitive_summaries": tuple(primitive_summaries),
        "observed_visual_change_region_count": len(visual_change_regions),
        "observed_visual_change_regions": visual_change_regions,
        "observed_audio_change_region_count": len(audio_change_regions),
        "observed_audio_change_regions": audio_change_regions,
        "multimodal_overlap_window_count": len(overlap_windows),
        "multimodal_overlap_windows": overlap_windows,
        "alignment_window_count": len(windows),
        "complete_window_count": sum(1 for item in windows if item.get("complete_for_config")),
        "eventful_window_count": sum(
            1
            for item in windows
            if item.get("visual_change_present") or item.get("audio_activity_present") or item.get("host_state_delta_present")
        ),
        "incomplete_window_count": len(incomplete_windows),
        "incomplete_windows": incomplete_windows,
        "bridge_records": tuple(
            {
                "bridge_record_id": item.get("bridge_record_id"),
                "alignment_window_id": item.get("alignment_window_id"),
                "emitted_event_kind": item.get("emitted_event_kind"),
                "host_body_event_id": item.get("host_body_event_id"),
                "raw_media_embedded": item.get("raw_media_embedded"),
                "semantic_binding_created": item.get("semantic_binding_created"),
            }
            for item in bridges
        ),
        "backpressure_record_count": len(backpressure),
        "backpressure_by_source_policy_action": backpressure_summary,
        "backpressure_details": backpressure_details,
        "dropped_sample_record_count": len(dropped),
        "dropped_sample_by_source_policy_reason": dropped_summary,
        "dropped_sample_counts_by_required_lane": drop_counts,
        "dropped_sample_details": dropped_details,
        "dropped_samples_deleted_raw_artifacts": any(bool(item.get("raw_artifact_deleted")) for item in dropped),
        "dropped_samples_deleted_primitives": any(bool(item.get("primitive_deleted")) for item in dropped),
        "required_lane_failure_summary": required_lane_failure_summary,
        "review_rule_assessment": review_rule_assessment,
        "raw_media_displayed": False,
        "stimulus_ground_truth_displayed": False,
    }


def _primitive_review_summary(primitive: dict[str, object]) -> dict[str, object]:
    if "visual_primitive_id" in primitive:
        return {
            "primitive_record_kind": "visual_frame_primitive",
            "primitive_record_id": primitive["visual_primitive_id"],
            "source_kind": primitive.get("source_kind"),
            "source_artifact_id": primitive.get("source_artifact_id"),
            "luminance_mean": primitive.get("luminance_mean"),
            "contrast_proxy": primitive.get("contrast_proxy"),
            "edge_density": primitive.get("edge_density"),
            "quality_uncertainty": primitive.get("quality_uncertainty"),
            "semantic_label": primitive.get("semantic_label"),
            "object_class": primitive.get("object_class"),
        }
    if "visual_change_id" in primitive:
        return {
            "primitive_record_kind": "visual_change_primitive",
            "primitive_record_id": primitive["visual_change_id"],
            "source_kind": primitive.get("source_kind"),
            "previous_source_artifact_id": primitive.get("previous_source_artifact_id"),
            "current_source_artifact_id": primitive.get("current_source_artifact_id"),
            "changed_area_ratio": primitive.get("changed_area_ratio"),
            "motion_proxy": primitive.get("motion_proxy"),
            "quality_uncertainty": primitive.get("quality_uncertainty"),
            "semantic_label": primitive.get("semantic_label"),
            "object_tracking_created": primitive.get("object_tracking_created"),
        }
    if "audio_primitive_id" in primitive:
        envelope = tuple(float(item) for item in (primitive.get("amplitude_envelope") or ()))
        return {
            "primitive_record_kind": "audio_primitive",
            "primitive_record_id": primitive["audio_primitive_id"],
            "source_artifact_id": primitive.get("source_artifact_id"),
            "duration_ms": primitive.get("duration_ms"),
            "amplitude_envelope_point_count": len(envelope),
            "max_amplitude_envelope": max(envelope) if envelope else 0.0,
            "amplitude_activity_present": bool(envelope and max(envelope) > 0.0),
            "onset_count": len(tuple(primitive.get("onset_events") or ())),
            "offset_count": len(tuple(primitive.get("offset_events") or ())),
            "pause_count": len(tuple(primitive.get("pause_intervals") or ())),
            "coarse_pitch_band": primitive.get("coarse_pitch_band"),
            "uncertainty": primitive.get("uncertainty"),
            "semantic_label": primitive.get("semantic_label"),
            "speech_content": primitive.get("speech_content"),
            "speaker_identity": primitive.get("speaker_identity"),
            "emotion_label": primitive.get("emotion_label"),
        }
    if "host_state_primitive_id" in primitive:
        return {
            "primitive_record_kind": "host_state_primitive",
            "primitive_record_id": primitive["host_state_primitive_id"],
            "source_artifact_id": primitive.get("source_artifact_id"),
            "memory_available_ratio": primitive.get("memory_available_ratio"),
            "display_count": primitive.get("display_count"),
            "camera_adapter_available": primitive.get("camera_adapter_available"),
            "microphone_adapter_available": primitive.get("microphone_adapter_available"),
            "screen_adapter_available": primitive.get("screen_adapter_available"),
            "quality_uncertainty": primitive.get("quality_uncertainty"),
            "semantic_label": primitive.get("semantic_label"),
            "host_condition_label": primitive.get("host_condition_label"),
        }
    return {"primitive_record_id": "unknown", "status": "unknown_kind"}


def _visual_change_regions(primitive_summaries: list[dict[str, object]]) -> tuple[dict[str, object], ...]:
    regions = []
    for item in primitive_summaries:
        if item.get("primitive_record_kind") != "visual_change_primitive":
            continue
        if float(item.get("changed_area_ratio") or 0.0) <= 0.0:
            continue
        regions.append(
            {
                "primitive_record_id": item.get("primitive_record_id"),
                "previous_source_artifact_id": item.get("previous_source_artifact_id"),
                "current_source_artifact_id": item.get("current_source_artifact_id"),
                "changed_area_ratio": item.get("changed_area_ratio"),
                "motion_proxy": item.get("motion_proxy"),
                "quality_uncertainty": item.get("quality_uncertainty"),
                "semantic_label": item.get("semantic_label"),
                "object_tracking_created": item.get("object_tracking_created"),
            }
        )
    return tuple(regions)


def _audio_change_regions(primitive_summaries: list[dict[str, object]]) -> tuple[dict[str, object], ...]:
    regions = []
    for item in primitive_summaries:
        if item.get("primitive_record_kind") != "audio_primitive":
            continue
        if float(item.get("max_amplitude_envelope") or 0.0) <= 0.0:
            continue
        regions.append(
            {
                "primitive_record_id": item.get("primitive_record_id"),
                "source_artifact_id": item.get("source_artifact_id"),
                "duration_ms": item.get("duration_ms"),
                "max_amplitude_envelope": item.get("max_amplitude_envelope"),
                "onset_count": item.get("onset_count"),
                "offset_count": item.get("offset_count"),
                "pause_count": item.get("pause_count"),
                "uncertainty": item.get("uncertainty"),
                "speech_content": item.get("speech_content"),
                "speaker_identity": item.get("speaker_identity"),
                "emotion_label": item.get("emotion_label"),
            }
        )
    return tuple(regions)


def _multimodal_overlap_windows(
    windows: tuple[dict[str, object], ...],
    lane_item_by_id: dict[str, dict[str, object]],
    primitive_by_id: dict[str, dict[str, object]],
) -> tuple[dict[str, object], ...]:
    overlaps = []
    for window in windows:
        screen_items = _items_for_window(window, "screen_lane_item_ids", lane_item_by_id)
        audio_items = _items_for_window(window, "microphone_lane_item_ids", lane_item_by_id)
        visual_change_ids = tuple(
            str(item.get("primitive_record_id"))
            for item in screen_items
            if item.get("primitive_record_kind") == "visual_change_primitive"
        )
        audio_change_ids = tuple(
            str(item.get("primitive_record_id"))
            for item in audio_items
            if float(primitive_by_id.get(str(item.get("primitive_record_id")), {}).get("max_amplitude_envelope") or 0.0) > 0.0
        )
        if not (visual_change_ids and audio_change_ids):
            continue
        overlaps.append(
            {
                "alignment_window_id": window.get("alignment_window_id"),
                "window_index": window.get("window_index"),
                "window_start_ms": int(int(window.get("window_start_relative_ns") or 0) / 1_000_000),
                "window_end_ms": int(int(window.get("window_end_relative_ns") or 0) / 1_000_000),
                "visual_change_primitive_ids": visual_change_ids,
                "audio_change_primitive_ids": audio_change_ids,
                "has_visual_change": True,
                "has_audio_change": True,
                "has_host_state": bool(window.get("host_state_lane_item_ids")),
                "present_source_kinds": window.get("present_source_kinds"),
                "missing_required_source_kinds": window.get("missing_required_source_kinds"),
                "complete_for_config": window.get("complete_for_config"),
                "all_required_lanes_present": not bool(window.get("missing_required_source_kinds")),
                "semantic_binding_created": window.get("semantic_binding_created"),
                "claim_causality": False,
            }
        )
    return tuple(overlaps)


def _items_for_window(
    window: dict[str, object],
    key: str,
    lane_item_by_id: dict[str, dict[str, object]],
) -> tuple[dict[str, object], ...]:
    return tuple(
        lane_item_by_id[item_id]
        for item_id in (str(item) for item in (window.get(key) or ()))
        if item_id in lane_item_by_id
    )


def _incomplete_window_summaries(
    windows: tuple[dict[str, object], ...],
    overlap_windows: tuple[dict[str, object], ...],
) -> tuple[dict[str, object], ...]:
    overlap_ids = {str(item.get("alignment_window_id")) for item in overlap_windows}
    first_overlap_start = min((int(item.get("window_start_ms") or 0) for item in overlap_windows), default=0)
    last_overlap_end = max((int(item.get("window_end_ms") or 0) for item in overlap_windows), default=0)
    return tuple(
        {
            "alignment_window_id": item.get("alignment_window_id"),
            "window_index": item.get("window_index"),
            "window_start_ms": int(int(item.get("window_start_relative_ns") or 0) / 1_000_000),
            "window_end_ms": int(int(item.get("window_end_relative_ns") or 0) / 1_000_000),
            "present_source_kinds": item.get("present_source_kinds"),
            "missing_required_source_kinds": item.get("missing_required_source_kinds"),
            "inside_observed_multimodal_overlap_window": str(item.get("alignment_window_id")) in overlap_ids,
            "explanation_code": _incomplete_window_explanation(item, overlap_ids, first_overlap_start, last_overlap_end),
            "explained_as_only_preroll_postroll_or_boundary_alignment": _incomplete_window_explanation(item, overlap_ids, first_overlap_start, last_overlap_end)
            != "core_overlap_missing_required_lane",
            "required_lane_capture_failure_present": False,
            "required_lane_compile_failure_present": False,
            "complete_for_config": item.get("complete_for_config"),
            "aggregate_quality_uncertainty": item.get("aggregate_quality_uncertainty"),
        }
        for item in windows
        if item.get("missing_required_source_kinds")
    )


def _incomplete_window_explanation(
    window: dict[str, object],
    overlap_ids: set[str],
    first_overlap_start_ms: int,
    last_overlap_end_ms: int,
) -> str:
    window_id = str(window.get("alignment_window_id"))
    start_ms = int(int(window.get("window_start_relative_ns") or 0) / 1_000_000)
    end_ms = int(int(window.get("window_end_relative_ns") or 0) / 1_000_000)
    present = tuple(str(item) for item in (window.get("present_source_kinds") or ()))
    if window_id in overlap_ids:
        return "core_overlap_missing_required_lane"
    if end_ms <= first_overlap_start_ms:
        return "pre_core_alignment_gap"
    if start_ms >= last_overlap_end_ms:
        return "post_core_or_tail_alignment_gap"
    if present == ("screen",):
        return "visual_boundary_or_sparse_replay_alignment_gap"
    if present == ("host_state",):
        return "host_state_sparse_alignment_gap"
    if present == ("microphone", "screen") or present == ("screen", "microphone"):
        return "source_sampling_alignment_gap"
    return "source_sampling_alignment_gap"


def _window_refs_by_lane_item(windows: tuple[dict[str, object], ...]) -> dict[str, tuple[dict[str, object], ...]]:
    refs: dict[str, list[dict[str, object]]] = {}
    for window in windows:
        summary = {
            "alignment_window_id": window.get("alignment_window_id"),
            "window_index": window.get("window_index"),
            "window_start_ms": int(int(window.get("window_start_relative_ns") or 0) / 1_000_000),
            "window_end_ms": int(int(window.get("window_end_relative_ns") or 0) / 1_000_000),
            "complete_for_config": window.get("complete_for_config"),
            "missing_required_source_kinds": window.get("missing_required_source_kinds"),
        }
        for key in ("screen_lane_item_ids", "microphone_lane_item_ids", "host_state_lane_item_ids", "camera_lane_item_ids"):
            for lane_item_id in window.get(key) or ():
                refs.setdefault(str(lane_item_id), []).append(summary)
    return {key: tuple(value) for key, value in refs.items()}


def _backpressure_details(
    records: tuple[dict[str, object], ...],
    primitive_to_lane_items: dict[str, list[dict[str, object]]],
    window_by_lane_item_id: dict[str, tuple[dict[str, object], ...]],
    overlap_windows: tuple[dict[str, object], ...],
) -> tuple[dict[str, object], ...]:
    overlap_ids = {str(item.get("alignment_window_id")) for item in overlap_windows}
    details = []
    for record in records:
        affected = []
        affected_core_window_ids: list[str] = []
        for source_record_id in tuple(str(item) for item in (record.get("affected_source_record_ids") or ())):
            for lane_item in primitive_to_lane_items.get(source_record_id, []):
                windows = window_by_lane_item_id.get(str(lane_item.get("lane_item_id")), tuple())
                affected_core_window_ids.extend(
                    str(window.get("alignment_window_id"))
                    for window in windows
                    if str(window.get("alignment_window_id")) in overlap_ids
                )
                affected.append(
                    {
                        "affected_source_record_id": source_record_id,
                        "source_artifact_id": lane_item.get("source_artifact_id"),
                        "primitive_record_kind": lane_item.get("primitive_record_kind"),
                        "alignment_window_refs": windows,
                    }
                )
        details.append(
            {
                "backpressure_record_id": record.get("backpressure_record_id"),
                "source_kind": record.get("source_kind"),
                "policy": record.get("policy"),
                "action_taken": record.get("action_taken"),
                "queue_depth_before": record.get("queue_depth_before"),
                "queue_depth_limit": record.get("queue_depth_limit"),
                "affected": tuple(affected),
                "affects_observed_multimodal_overlap_window": bool(affected_core_window_ids),
                "affected_overlap_window_ids": tuple(dict.fromkeys(affected_core_window_ids)),
            }
        )
    return tuple(details)


def _dropped_sample_details(
    records: tuple[dict[str, object], ...],
    artifact_to_lane_items: dict[str, list[dict[str, object]]],
    window_by_lane_item_id: dict[str, tuple[dict[str, object], ...]],
    overlap_windows: tuple[dict[str, object], ...],
) -> tuple[dict[str, object], ...]:
    overlap_ids = {str(item.get("alignment_window_id")) for item in overlap_windows}
    details = []
    for record in records:
        artifact_id = str(record.get("source_record_id"))
        affected = []
        affected_core_window_ids: list[str] = []
        for lane_item in artifact_to_lane_items.get(artifact_id, []):
            windows = window_by_lane_item_id.get(str(lane_item.get("lane_item_id")), tuple())
            affected_core_window_ids.extend(
                str(window.get("alignment_window_id"))
                for window in windows
                if str(window.get("alignment_window_id")) in overlap_ids
            )
            affected.append(
                {
                    "primitive_record_id": lane_item.get("primitive_record_id"),
                    "primitive_record_kind": lane_item.get("primitive_record_kind"),
                    "alignment_window_refs": windows,
                }
            )
        details.append(
            {
                "dropped_sample_record_id": record.get("dropped_sample_record_id"),
                "source_kind": record.get("source_kind"),
                "source_artifact_id": artifact_id,
                "drop_policy": record.get("drop_policy"),
                "reason_code": record.get("reason_code"),
                "timeline_gap_created": record.get("timeline_gap_created"),
                "raw_artifact_deleted": record.get("raw_artifact_deleted"),
                "primitive_deleted": record.get("primitive_deleted"),
                "affected": tuple(affected),
                "affects_observed_multimodal_overlap_window": bool(affected_core_window_ids),
                "affected_overlap_window_ids": tuple(dict.fromkeys(affected_core_window_ids)),
            }
        )
    return tuple(details)


def _drop_counts_by_required_lane(records: tuple[dict[str, object], ...]) -> dict[str, int]:
    counts = Counter(str(item.get("source_kind")) for item in records)
    return {
        "screen_frame_count": int(counts.get("screen", 0)),
        "audio_chunk_count": int(counts.get("microphone", 0)),
        "host_state_count": int(counts.get("host_state", 0)),
        "total_required_lane_drop_count": int(counts.get("screen", 0) + counts.get("microphone", 0) + counts.get("host_state", 0)),
    }


def _required_lane_failure_summary(
    sensor_failures: tuple[dict[str, object], ...],
    compilation_failures: tuple[dict[str, object], ...],
) -> dict[str, object]:
    required = {"screen", "microphone", "host_state"}
    sensor = tuple(
        {
            "failure_record_id": item.get("failure_record_id"),
            "source_kind": item.get("source_kind"),
            "failure_kind": item.get("failure_kind"),
            "artifact_created": item.get("artifact_created"),
        }
        for item in sensor_failures
        if item.get("source_kind") in required
    )
    compile_failures = tuple(
        {
            "failure_record_id": item.get("failure_record_id"),
            "source_kind": item.get("source_kind"),
            "source_artifact_id": item.get("source_artifact_id"),
            "source_buffer_id": item.get("source_buffer_id"),
            "failure_kind": item.get("failure_kind"),
            "primitive_created": item.get("primitive_created"),
            "perception_readable_data_created": item.get("perception_readable_data_created"),
        }
        for item in compilation_failures
        if item.get("source_kind") in required
    )
    return {
        "required_lane_capture_failure_count": len(sensor),
        "required_lane_compile_failure_count": len(compile_failures),
        "required_lane_capture_failures": sensor,
        "required_lane_compile_failures": compile_failures,
    }


def _review_rule_assessment(
    *,
    overlap_windows: tuple[dict[str, object], ...],
    drop_counts: dict[str, int],
    required_lane_failure_summary: dict[str, object],
    backpressure_details: tuple[dict[str, object], ...],
) -> dict[str, object]:
    incomplete_core_windows = tuple(
        item for item in overlap_windows if not item.get("all_required_lanes_present")
    )
    backpressure_core_ids = tuple(
        dict.fromkeys(
            window_id
            for item in backpressure_details
            for window_id in (item.get("affected_overlap_window_ids") or ())
        )
    )
    failure_count = int(required_lane_failure_summary["required_lane_capture_failure_count"]) + int(
        required_lane_failure_summary["required_lane_compile_failure_count"]
    )
    required_lane_drop_count = int(drop_counts["total_required_lane_drop_count"])
    can_approve = not incomplete_core_windows and required_lane_drop_count == 0 and failure_count == 0 and not backpressure_core_ids
    reasons = []
    if incomplete_core_windows:
        reasons.append("core_overlap_windows_missing_required_lanes")
    if required_lane_drop_count:
        reasons.append("required_lane_drop_count_nonzero")
    if failure_count:
        reasons.append("required_lane_failure_count_nonzero")
    if backpressure_core_ids:
        reasons.append("backpressure_affects_observed_multimodal_overlap_windows")
    return {
        "supplied_rule_status": "can_approve" if can_approve else "must_reject_rerun",
        "can_approve_by_supplied_rules": can_approve,
        "all_core_overlap_windows_complete": not incomplete_core_windows,
        "core_overlap_windows_missing_required_lanes": tuple(
            {
                "alignment_window_id": item.get("alignment_window_id"),
                "window_index": item.get("window_index"),
                "missing_required_source_kinds": item.get("missing_required_source_kinds"),
            }
            for item in incomplete_core_windows
        ),
        "required_lane_drop_count": required_lane_drop_count,
        "required_lane_failure_count": failure_count,
        "backpressure_affects_core_overlap_windows": bool(backpressure_core_ids),
        "backpressure_affected_core_overlap_window_ids": backpressure_core_ids,
        "decision_reasons": tuple(reasons),
    }


def _summarize_records_by_source_and_policy(
    records: tuple[dict[str, object], ...],
    policy_key: str,
    result_key: str,
) -> tuple[dict[str, object], ...]:
    counts = Counter(
        (
            str(item.get("source_kind")),
            str(item.get(policy_key)),
            str(item.get(result_key)),
        )
        for item in records
    )
    return tuple(
        {
            "source_kind": source_kind,
            "policy": policy,
            "result": result,
            "count": count,
        }
        for (source_kind, policy, result), count in sorted(counts.items())
    )


def _print_json(payload: Any) -> int:
    print(json.dumps(plain(payload), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
