"""Fresh-process worker used by the Package 129 public CLI."""

from __future__ import annotations

import argparse
import json
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain
from ashl_core_v1.runtime.package_129_active_perception_growth_runtime import (
    run_active_perception_cycle,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Package 129 isolated real-cycle worker"
    )
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--cycle-index", type=int, choices=(1, 2), required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run_active_perception_cycle(
            state_dir=args.state_dir,
            cycle_index=args.cycle_index,
        )
        payload = _worker_summary(result)
        exit_code = 0
    except Exception as error:
        payload = {
            "status": (
                f"blocked_package_129_cycle_{args.cycle_index}"
            ),
            "cycle_index": args.cycle_index,
            "exception_kind": type(error).__name__,
            "reason": str(error),
        }
        exit_code = 1
    print(
        json.dumps(
            plain(payload),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return exit_code


def _worker_summary(result: dict[str, Any]) -> dict[str, Any]:
    cycle = dict(result["cycle_record"])
    stages = tuple(dict(item) for item in result["stage_records"])
    payload: dict[str, Any] = {
        "status": result["status"],
        "cycle_record": {
            key: cycle[key]
            for key in (
                "cycle_record_id",
                "experiment_id",
                "experiment_run_id",
                "cycle_index",
                "process_instance_id",
                "operating_system_process_id",
                "stimulus_config_hash",
                "source_plan_hash",
                "parent_runtime_session_id",
                "parent_perception_session_id",
                "parent_observation_window_id",
                "child_runtime_session_id",
                "child_perception_session_id",
                "child_observation_window_id",
                "bounded_embodied_session_id",
                "final_session_state",
                "pending_teacher_review_id",
                "evidence_snapshot_id",
                "evidence_identity_hash",
                "readback_loaded_before_event",
                "loaded_readback_refs",
            )
        },
        "stage_records": tuple(
            {
                key: stage[key]
                for key in (
                    "stage_record_id",
                    "stage_index",
                    "stage_kind",
                    "internal_action_kind",
                    "internal_action_id",
                    "execution_record_id",
                    "required_lane_drop_count",
                    "backpressure_fault_count",
                    "capture_failure_count",
                    "compile_failure_count",
                    "flush_remaining_count",
                )
            }
            for stage in stages
        ),
        "teacher_gate": {
            key: result["teacher_gate"][key]
            for key in (
                "package_115_session_id",
                "pending_review_id",
                "evidence_snapshot_id",
                "evidence_identity_hash",
                "automatic_teacher_decision_created",
            )
        },
        "sequence": result["sequence"],
    }
    for key in (
        "readback_load_timing",
        "readback_influence",
        "cycle_2_review_preservation",
        "comparison",
        "controls",
    ):
        if key in result:
            payload[key] = result[key]
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
