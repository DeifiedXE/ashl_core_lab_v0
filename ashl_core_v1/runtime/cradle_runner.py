"""Fixed multi-case cradle runner for ASHL Core v1."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.cradle_cases import (
    build_all_cradle_case_samples,
    build_cradle_case_sample,
    list_cradle_case_ids,
)


CRADLE_RUNNER_ENV = "ASHL_CORE_V1_CRADLE_RUNNER_DIR"
DEFAULT_CRADLE_RUNNER_DIR = Path(__file__).resolve().parents[1] / "data" / "cradle_runner"

LAST_CRADLE_RUN_FILE = "last_cradle_run.json"
CRADLE_RUN_HISTORY_FILE = "cradle_run_history.jsonl"


def resolve_cradle_runner_dir(data_dir: str | Path | None = None) -> Path:
    if data_dir is not None:
        return Path(data_dir)
    env_value = os.environ.get(CRADLE_RUNNER_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_CRADLE_RUNNER_DIR


def ensure_cradle_runner_store(data_dir: str | Path | None = None) -> Path:
    runner_dir = resolve_cradle_runner_dir(data_dir)
    runner_dir.mkdir(parents=True, exist_ok=True)
    (runner_dir / CRADLE_RUN_HISTORY_FILE).touch(exist_ok=True)
    return runner_dir


def run_cradle_case(case_id: str, data_dir: str | Path | None = None) -> dict[str, Any]:
    sample = build_cradle_case_sample(case_id)
    result = {
        "run_id": f"cradle_case_run_{case_id}_001",
        "case_id": case_id,
        "cycle_summary": dict(sample["cycle_summary"]),
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
    }
    _save_run(result, data_dir)
    return result


def run_all_cradle_cases(data_dir: str | Path | None = None) -> dict[str, Any]:
    samples = build_all_cradle_case_samples()
    case_ids = list(list_cradle_case_ids())
    result = {
        "run_id": "cradle_all_cases_run_001",
        "case_count": len(case_ids),
        "case_ids": case_ids,
        "case_summaries": [
            _case_summary_for_run(case_id, samples[case_id]["cycle_summary"]) for case_id in case_ids
        ],
        "all_cases_completed": True,
    }
    _save_run(result, data_dir)
    return result


def load_last_cradle_run(data_dir: str | Path | None = None) -> dict[str, Any] | None:
    path = ensure_cradle_runner_store(data_dir) / LAST_CRADLE_RUN_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _case_summary_for_run(case_id: str, summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "review_status": summary["review_status"],
        "routing_status": summary["routing_status"],
        "memory_entry_allowed": summary["memory_entry_allowed"],
        "memory_layer_target": summary["memory_layer_target"],
        "influence_visible": summary["influence_visible"],
        "body_action_signal_type": summary["body_action_signal_type"],
    }


def _save_run(result: dict[str, Any], data_dir: str | Path | None) -> None:
    runner_dir = ensure_cradle_runner_store(data_dir)
    (runner_dir / LAST_CRADLE_RUN_FILE).write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (runner_dir / CRADLE_RUN_HISTORY_FILE).open("a", encoding="utf-8", newline="\n") as file:
        file.write(json.dumps(result, ensure_ascii=False, sort_keys=True))
        file.write("\n")
