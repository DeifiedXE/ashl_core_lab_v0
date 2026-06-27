"""Fixed first-stage circulation runner for the blocked front-obstacle case."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.manual_samples import build_blocked_manual_circulation_sample


FIXED_RUNNER_ENV = "ASHL_CORE_V1_FIXED_RUNNER_DIR"
DEFAULT_FIXED_RUNNER_DIR = Path(__file__).resolve().parents[1] / "data" / "fixed_runner"

LAST_BLOCKED_CYCLE_FILE = "last_blocked_cycle.json"
BLOCKED_CYCLE_HISTORY_FILE = "blocked_cycle_history.jsonl"


def resolve_fixed_runner_dir(data_dir: str | Path | None = None) -> Path:
    if data_dir is not None:
        return Path(data_dir)
    env_value = os.environ.get(FIXED_RUNNER_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_FIXED_RUNNER_DIR


def ensure_fixed_runner_store(data_dir: str | Path | None = None) -> Path:
    runner_dir = resolve_fixed_runner_dir(data_dir)
    runner_dir.mkdir(parents=True, exist_ok=True)
    (runner_dir / BLOCKED_CYCLE_HISTORY_FILE).touch(exist_ok=True)
    return runner_dir


def run_blocked_cycle(data_dir: str | Path | None = None) -> dict[str, Any]:
    """Run the fixed blocked/front-obstacle circulation case."""

    from ashl_core_v1.memory.trace_store import seed_blocked_sample_trace

    runner_dir = ensure_fixed_runner_store(data_dir)
    sample = build_blocked_manual_circulation_sample()
    seed_blocked_sample_trace(runner_dir / "memory_traces")

    cycle = {
        "cycle_id": "fixed_blocked_cycle_001",
        "case_id": "blocked_front_obstacle",
        "record_order": list(sample["cycle_summary"]["record_order"]),
        "records": {
            "perception_id": sample["perception_readable_data"]["perception_id"],
            "endocrine_signal_id": sample["endocrine_signal"]["endocrine_signal_id"],
            "learning_digest_id": sample["learning_digest"]["learning_digest_id"],
            "review_record_id": sample["learning_review_record"]["review_record_id"],
            "reviewed_digest_id": sample["reviewed_learning_digest"]["reviewed_digest_id"],
            "memory_learning_trace_id": sample["memory_learning_trace"]["memory_learning_trace_id"],
            "memory_routing_trace_id": sample["memory_routing_trace"]["memory_routing_trace_id"],
            "memory_application_data_id": sample["memory_application_data"][
                "memory_application_data_id"
            ],
            "thought_read_trace_id": sample["thought_read_trace"]["thought_read_trace_id"],
            "influence_trace_id": sample["influence_trace"]["influence_trace_id"],
            "thought_signal_id": sample["thought_signal"]["thought_signal_id"],
            "body_action_signal_id": sample["body_action_signal"]["body_action_signal_id"],
        },
        "summary": {
            "influence_visible": sample["cycle_summary"]["influence_visible"],
            "body_action_signal_type": sample["cycle_summary"]["body_action_signal_type"],
            "next_expected_feedback_kind": sample["cycle_summary"][
                "next_expected_feedback_kind"
            ],
        },
    }
    _write_json(runner_dir / LAST_BLOCKED_CYCLE_FILE, cycle)
    _append_jsonl(runner_dir / BLOCKED_CYCLE_HISTORY_FILE, cycle)
    return cycle


def show_last_cycle(data_dir: str | Path | None = None) -> dict[str, Any] | None:
    path = ensure_fixed_runner_store(data_dir) / LAST_BLOCKED_CYCLE_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as file:
        file.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
        file.write("\n")
