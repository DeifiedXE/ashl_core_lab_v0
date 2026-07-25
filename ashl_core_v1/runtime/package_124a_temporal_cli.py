"""CLI for Package 124A grounded temporal primitive foundation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.grounded_temporal_primitive_compiler import (
    DEFAULT_PACKAGE_124_ARCHIVE,
    calibrate_against_stimulus_after_compilation,
    compile_package_124_archive_temporal_bundle,
    verify_replay_speed_independence,
    verify_temporal_deterministic_replay,
)
from ashl_core_v1.runtime.host_sensor_types import canonical_json
from ashl_core_v1.runtime.package_124a_temporal_audit import (
    audit_package_124a_temporal_foundation,
    run_package_124a_guided_foundation,
    summarize_package_124a_archive_evidence,
)
from ashl_core_v1.runtime.package_124a_temporal_store import Package124ATemporalStore


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Package 124A grounded temporal primitive CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    _state_command(sub, "inspect-clock-domains")
    _archive_state_command(sub, "compile-milestone-archive")
    _state_command(sub, "show-temporal-bundle")
    _state_command(sub, "show-spans")
    _state_command(sub, "show-intervals")
    _state_command(sub, "show-relations")
    _state_command(sub, "show-continuity")
    _state_command(sub, "show-external-gaps")
    _archive_state_command(sub, "calibrate-against-stimulus")
    _archive_state_command(sub, "verify-deterministic-replay")
    _state_command(sub, "audit")
    _archive_state_command(sub, "guided-foundation-run")
    args = parser.parse_args(argv)
    result = dispatch(args)
    print(canonical_json(result))
    return 0


def dispatch(args: argparse.Namespace) -> dict[str, Any]:
    command = args.command
    if command == "compile-milestone-archive":
        result = compile_package_124_archive_temporal_bundle(
            archive_dir=args.archive_dir,
            state_dir=args.state_dir,
            persist=True,
            verify_archive=getattr(args, "verify_archive", True),
        )
        return {
            "status": "compiled",
            "archive_dir": result.archive_dir,
            "archive_verified": result.archive_verified,
            "archive_opened_read_only": result.archive_opened_read_only,
            "archive_modified": result.archive_modified,
            "temporal_bundle_id": result.temporal_bundle.temporal_bundle_id,
            "anchor_count": len(result.anchors),
            "span_count": len(result.spans),
            "interval_count": len(result.intervals),
            "relation_count": len(result.relations),
            "continuity_count": len(result.continuity_records),
            "repeated_structure_count": len(result.repeated_structures),
            "external_gap_count": len(result.external_gaps),
        }
    if command == "guided-foundation-run":
        return run_package_124a_guided_foundation(archive_dir=args.archive_dir, state_dir=args.state_dir)
    if command == "calibrate-against-stimulus":
        record = calibrate_against_stimulus_after_compilation(archive_dir=args.archive_dir, state_dir=args.state_dir)
        return record.to_dict()
    if command == "verify-deterministic-replay":
        return {
            "deterministic": verify_temporal_deterministic_replay(args.archive_dir),
            "replay_speed": verify_replay_speed_independence(args.archive_dir),
        }
    if command == "audit":
        return audit_package_124a_temporal_foundation(state_dir=args.state_dir).to_dict()
    store = Package124ATemporalStore(args.state_dir)
    if command == "inspect-clock-domains":
        return {
            "clock_domains": store.list_payloads("temporal_clock_domains"),
            "clock_quality": store.list_payloads("temporal_clock_quality"),
        }
    if command == "show-temporal-bundle":
        return {
            "latest_bundle": store.latest_payload("grounded_temporal_bundles"),
            "counts": store.counts(),
        }
    if command == "show-spans":
        return _summarize_records(store.list_payloads("temporal_span_primitives"), "temporal_span_id", fields=("span_kind", "source_lane", "start_event_time_ns", "end_event_time_ns", "observed_duration_ns"))
    if command == "show-intervals":
        return _summarize_records(store.list_payloads("temporal_interval_primitives"), "temporal_interval_id", fields=("interval_kind", "left_event_time_ns", "right_event_time_ns", "interval_ns"))
    if command == "show-relations":
        return _summarize_records(store.list_payloads("temporal_relation_primitives"), "temporal_relation_id", fields=("relation_kind", "left_temporal_ref", "right_temporal_ref", "gap_ns", "overlap_ns"))
    if command == "show-continuity":
        return {"continuity": store.list_payloads("temporal_continuity_primitives")}
    if command == "show-external-gaps":
        return {"external_gaps": store.list_payloads("cross_process_external_gaps")}
    raise ValueError(f"unknown command: {command}")


def _summarize_records(records: tuple[dict[str, Any], ...], id_key: str, *, fields: tuple[str, ...]) -> dict[str, Any]:
    return {
        "count": len(records),
        "records": tuple({id_key: item.get(id_key), **{field: item.get(field) for field in fields}} for item in records),
    }


def _state_command(sub: argparse._SubParsersAction[argparse.ArgumentParser], name: str) -> None:
    parser = sub.add_parser(name)
    parser.add_argument("--state-dir", required=True)


def _archive_state_command(sub: argparse._SubParsersAction[argparse.ArgumentParser], name: str) -> None:
    parser = sub.add_parser(name)
    parser.add_argument("--archive-dir", default=str(DEFAULT_PACKAGE_124_ARCHIVE))
    parser.add_argument("--state-dir", required=True)


if __name__ == "__main__":
    raise SystemExit(main())
