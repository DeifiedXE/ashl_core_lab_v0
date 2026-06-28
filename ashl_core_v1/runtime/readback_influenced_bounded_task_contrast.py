"""Contrast bounded task runs with and without memory readback hints."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.memory.memory_readback_apply_to_task_working_memory import (
    apply_memory_readback_to_task_working_memory,
    load_last_memory_readback_application,
)
from ashl_core_v1.memory.memory_application_readback_to_task_working_memory_preview import (
    list_memory_application_readback_previews,
)
from ashl_core_v1.runtime.bounded_teacher_gated_task_tick_runner import (
    build_bounded_teacher_gated_task_tick_run,
)


READBACK_INFLUENCED_CONTRAST_ENV = "ASHL_CORE_V1_READBACK_INFLUENCED_CONTRAST_DIR"
DEFAULT_READBACK_INFLUENCED_CONTRAST_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "readback_influenced_contrast"
)

LAST_READBACK_INFLUENCED_CONTRAST_FILE = "last_readback_influenced_contrast.json"
READBACK_INFLUENCED_CONTRAST_HISTORY_FILE = "readback_influenced_contrast_history.jsonl"

BLOCKED_CONTRAST_PLAN: tuple[tuple[str, str], ...] = (
    ("blocked", "observe_or_adjust"),
    ("blocked", "avoid_direct_retry"),
    ("avoid_direct_retry", "wait_or_stop"),
)


def build_readback_influenced_bounded_task_contrast(
    *,
    case_id: str = "blocked_front_obstacle",
    readback_application: dict[str, Any] | None = None,
    base_dir: str | Path | None = None,
    force_same_tick_summaries: bool = False,
    free_action_selection_used: bool = False,
    action_execution_used: bool = False,
    scheduler_used: bool = False,
    memory_layer_promotion_used: bool = False,
) -> dict[str, Any]:
    application_payload = readback_application or _load_or_create_application(case_id, base_dir)
    if not application_payload:
        return _blocked_record(case_id, "blocked_missing_readback_application")
    application = application_payload["task_working_memory_readback_application_record"]
    readback_hints = tuple(application["after_next_candidate_hints"])
    baseline_run = build_bounded_teacher_gated_task_tick_run(
        max_ticks=5,
        task_id=f"contrast_baseline:{case_id}",
        goal=f"contrast baseline for {case_id}",
        tick_plan=BLOCKED_CONTRAST_PLAN,
        stop_reason_override="blocked_front_obstacle",
        final_task_status_hint="failed",
        case_id=case_id,
        expected_candidate_kinds=("blocked_front_obstacle", "repeated_blocked"),
        initial_candidate_hints=(),
    )
    readback_run = build_bounded_teacher_gated_task_tick_run(
        max_ticks=5,
        task_id=f"contrast_readback:{case_id}",
        goal=f"contrast readback for {case_id}",
        tick_plan=BLOCKED_CONTRAST_PLAN,
        stop_reason_override="blocked_front_obstacle",
        final_task_status_hint="failed",
        case_id=case_id,
        expected_candidate_kinds=("blocked_front_obstacle", "repeated_blocked"),
        initial_candidate_hints=readback_hints,
    )
    baseline_summaries = _tick_summaries(baseline_run, ())
    readback_summaries = (
        baseline_summaries
        if force_same_tick_summaries
        else _tick_summaries(readback_run, readback_hints)
    )
    readback_visible_wm = bool(readback_hints)
    readback_visible_tick = any(
        readback_hints
        and set(readback_hints).issubset(set(summary.get("initial_context_hints", [])))
        for summary in readback_summaries
    )
    difference_visible = baseline_summaries != readback_summaries
    status = _contrast_status(
        baseline_run=baseline_run,
        readback_run=readback_run,
        readback_application=application_payload,
        readback_visible_wm=readback_visible_wm,
        readback_visible_tick=readback_visible_tick,
        difference_visible=difference_visible,
        free_action_selection_used=free_action_selection_used,
        action_execution_used=action_execution_used,
        scheduler_used=scheduler_used,
        memory_layer_promotion_used=memory_layer_promotion_used,
    )
    return {
        "contrast_id": _contrast_id(),
        "case_id": case_id,
        "task_id": f"contrast_task:{case_id}",
        "baseline_run_id": baseline_run["bounded_task_tick_run_record"]["run_id"],
        "readback_applied_run_id": readback_run["bounded_task_tick_run_record"]["run_id"],
        "readback_application_id": application["readback_application_id"],
        "baseline_initial_hints": [],
        "readback_initial_hints": list(readback_hints),
        "baseline_tick_summaries": baseline_summaries,
        "readback_tick_summaries": readback_summaries,
        "readback_hint_visible_in_working_memory": readback_visible_wm,
        "readback_hint_visible_in_tick_context": readback_visible_tick,
        "task_processing_difference_visible": difference_visible,
        "influence_summary": _influence_summary(readback_hints, difference_visible),
        "free_action_selection_used": free_action_selection_used,
        "action_execution_used": action_execution_used,
        "scheduler_used": scheduler_used,
        "memory_layer_promotion_used": memory_layer_promotion_used,
        "contrast_status": status,
        "source_trace_refs": [
            baseline_run["bounded_task_tick_run_record"]["run_id"],
            readback_run["bounded_task_tick_run_record"]["run_id"],
            application["readback_application_id"],
        ],
        "baseline_run": baseline_run,
        "readback_run": readback_run,
        "readback_application": application_payload,
    }


def run_readback_influenced_bounded_task_contrast(
    *,
    case_id: str = "blocked_front_obstacle",
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    contrast = build_readback_influenced_bounded_task_contrast(
        case_id=case_id,
        base_dir=base_dir,
    )
    return save_readback_influenced_bounded_task_contrast(contrast, base_dir)


def save_readback_influenced_bounded_task_contrast(
    contrast: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    contrast_dir = ensure_readback_influenced_contrast_store(base_dir)
    (contrast_dir / LAST_READBACK_INFLUENCED_CONTRAST_FILE).write_text(
        json.dumps(contrast, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (contrast_dir / READBACK_INFLUENCED_CONTRAST_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(contrast, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(contrast)


def load_last_readback_influenced_bounded_task_contrast(
    base_dir: str | Path | None = None,
) -> dict[str, Any] | None:
    path = (
        resolve_readback_influenced_contrast_dir(base_dir)
        / LAST_READBACK_INFLUENCED_CONTRAST_FILE
    )
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_readback_influenced_bounded_task_contrasts(
    base_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    path = (
        resolve_readback_influenced_contrast_dir(base_dir)
        / READBACK_INFLUENCED_CONTRAST_HISTORY_FILE
    )
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def resolve_readback_influenced_contrast_dir(
    base_dir: str | Path | None = None,
) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(READBACK_INFLUENCED_CONTRAST_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_READBACK_INFLUENCED_CONTRAST_DIR


def ensure_readback_influenced_contrast_store(
    base_dir: str | Path | None = None,
) -> Path:
    contrast_dir = resolve_readback_influenced_contrast_dir(base_dir)
    contrast_dir.mkdir(parents=True, exist_ok=True)
    (contrast_dir / READBACK_INFLUENCED_CONTRAST_HISTORY_FILE).touch(exist_ok=True)
    return contrast_dir


def _load_or_create_application(
    case_id: str,
    base_dir: str | Path | None,
) -> dict[str, Any] | None:
    existing = load_last_memory_readback_application(base_dir)
    if existing is not None:
        return existing
    previews = list_memory_application_readback_previews(base_dir)
    if not previews:
        return None
    preview = previews[-1]
    if preview.get("case_id") != case_id:
        return None
    return apply_memory_readback_to_task_working_memory(
        preview_id=preview["readback_preview_id"],
        active_task_frame_id=preview["target_active_task_frame_id"],
        base_dir=base_dir,
    )


def _tick_summaries(
    run: dict[str, Any],
    initial_hints: tuple[str, ...],
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for tick in run["per_tick_stub_records"]:
        summaries.append(
            {
                "tick_number": tick["tick_number"],
                "outcome_label": tick["outcome_label"],
                "next_candidate_hint": tick["next_candidate_hint"],
                "initial_context_hints": list(initial_hints),
                "processing_note": (
                    "readback_hint_observed"
                    if initial_hints
                    else "default_bounded_processing"
                ),
            }
        )
    return summaries


def _contrast_status(
    *,
    baseline_run: dict[str, Any] | None,
    readback_run: dict[str, Any] | None,
    readback_application: dict[str, Any] | None,
    readback_visible_wm: bool,
    readback_visible_tick: bool,
    difference_visible: bool,
    free_action_selection_used: bool,
    action_execution_used: bool,
    scheduler_used: bool,
    memory_layer_promotion_used: bool,
) -> str:
    if baseline_run is None:
        return "blocked_missing_baseline_run"
    if readback_run is None:
        return "blocked_missing_readback_run"
    if readback_application is None:
        return "blocked_missing_readback_application"
    if not readback_visible_wm:
        return "blocked_readback_not_visible_in_working_memory"
    if not difference_visible:
        return "failed_no_readback_difference"
    if not readback_visible_tick:
        return "blocked_readback_not_visible_in_tick_context"
    if free_action_selection_used:
        return "blocked_action_selection_detected"
    if action_execution_used:
        return "blocked_action_execution_detected"
    if scheduler_used:
        return "blocked_scheduler_detected"
    if memory_layer_promotion_used:
        return "blocked_memory_layer_promotion_detected"
    return "passed"


def _blocked_record(case_id: str, status: str) -> dict[str, Any]:
    return {
        "contrast_id": _contrast_id(),
        "case_id": case_id,
        "task_id": f"contrast_task:{case_id}",
        "baseline_run_id": None,
        "readback_applied_run_id": None,
        "readback_application_id": None,
        "baseline_initial_hints": [],
        "readback_initial_hints": [],
        "baseline_tick_summaries": [],
        "readback_tick_summaries": [],
        "readback_hint_visible_in_working_memory": False,
        "readback_hint_visible_in_tick_context": False,
        "task_processing_difference_visible": False,
        "influence_summary": "readback application missing",
        "free_action_selection_used": False,
        "action_execution_used": False,
        "scheduler_used": False,
        "memory_layer_promotion_used": False,
        "contrast_status": status,
        "source_trace_refs": [],
    }


def _influence_summary(readback_hints: tuple[str, ...], difference_visible: bool) -> str:
    if not difference_visible:
        return "No bounded processing difference was visible."
    return "Readback hints were visible in bounded tick context: " + ",".join(readback_hints)


def _contrast_id() -> str:
    return "readback_influenced_contrast_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
