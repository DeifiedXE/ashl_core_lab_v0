from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.bounded_teacher_gated_task_tick_runner import (
    build_bounded_teacher_gated_task_tick_run,
    list_bounded_teacher_gated_task_tick_runs,
    load_last_bounded_teacher_gated_task_tick_run,
    run_bounded_teacher_gated_task_tick_runner,
)


class BoundedTeacherGatedTaskTickRunnerTests(unittest.TestCase):
    def test_runner_creates_run_record(self) -> None:
        payload = build_bounded_teacher_gated_task_tick_run()
        self.assertTrue(payload["bounded_task_tick_run_created"])
        self.assertIn("run_id", payload["bounded_task_tick_run_record"])

    def test_runner_respects_max_ticks_5(self) -> None:
        payload = build_bounded_teacher_gated_task_tick_run(max_ticks=5)
        record = payload["bounded_task_tick_run_record"]
        self.assertEqual(record["max_ticks"], 5)
        self.assertEqual(record["actual_ticks"], 5)
        self.assertEqual(len(payload["per_tick_stub_records"]), 5)
        with self.assertRaises(ValueError):
            build_bounded_teacher_gated_task_tick_run(max_ticks=6)

    def test_runner_can_stop_before_max_ticks_when_task_closes(self) -> None:
        payload = build_bounded_teacher_gated_task_tick_run(max_ticks=5, close_after_tick=3)
        record = payload["bounded_task_tick_run_record"]
        self.assertEqual(record["actual_ticks"], 3)
        self.assertEqual(record["stop_reason"], "task_closed")
        self.assertFalse(payload["final_active_task_frame"]["continue_allowed"])

    def test_every_tick_shares_task_id(self) -> None:
        payload = build_bounded_teacher_gated_task_tick_run()
        task_id = payload["bounded_task_tick_run_record"]["task_id"]
        self.assertTrue(
            all(tick["task_id"] == task_id for tick in payload["per_tick_stub_records"])
        )
        self.assertTrue(payload["bounded_task_tick_run_record"]["all_ticks_same_task"])

    def test_every_tick_reads_previous_working_memory_update(self) -> None:
        payload = build_bounded_teacher_gated_task_tick_run()
        ticks = payload["per_tick_stub_records"]
        updates = payload["per_tick_working_memory_updates"]
        for index in range(1, len(ticks)):
            self.assertEqual(
                ticks[index]["previous_working_memory_update_id"],
                updates[index - 1]["task_working_memory_tick_update_id"],
            )

    def test_every_tick_writes_working_memory_update(self) -> None:
        payload = build_bounded_teacher_gated_task_tick_run()
        ticks = payload["per_tick_stub_records"]
        updates = payload["per_tick_working_memory_updates"]
        self.assertEqual(len(ticks), len(updates))
        for tick, update in zip(ticks, updates):
            self.assertEqual(
                tick["task_working_memory_update_id"],
                update["task_working_memory_tick_update_id"],
            )
        self.assertTrue(
            payload["bounded_task_tick_run_record"]["working_memory_used_for_all_ticks"]
        )

    def test_teacher_gate_preserved_for_every_tick(self) -> None:
        payload = build_bounded_teacher_gated_task_tick_run()
        self.assertTrue(
            payload["bounded_task_tick_run_record"][
                "teacher_gate_preserved_for_all_ticks"
            ]
        )

    def test_manual_within_cli_run_marked_true(self) -> None:
        payload = build_bounded_teacher_gated_task_tick_run()
        self.assertTrue(
            payload["bounded_task_tick_run_record"]["all_ticks_manual_within_cli_run"]
        )

    def test_no_scheduler_or_action_or_direct_memory_promotion(self) -> None:
        record = build_bounded_teacher_gated_task_tick_run()[
            "bounded_task_tick_run_record"
        ]
        self.assertFalse(record["scheduler_used"])
        self.assertFalse(record["free_action_selection_used"])
        self.assertFalse(record["action_execution_used"])
        self.assertFalse(record["direct_memory_promotion_used"])

    def test_final_summary_includes_stop_reason(self) -> None:
        summary = build_bounded_teacher_gated_task_tick_run()[
            "bounded_task_tick_run_summary"
        ]
        self.assertEqual(summary["stop_reason"], "budget_stop")

    def test_show_last_run_works(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            saved = run_bounded_teacher_gated_task_tick_runner(base_dir=temp_dir)
            loaded = load_last_bounded_teacher_gated_task_tick_run(temp_dir)
        self.assertEqual(
            loaded["bounded_task_tick_run_record"]["run_id"],
            saved["bounded_task_tick_run_record"]["run_id"],
        )

    def test_list_runs_works(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_bounded_teacher_gated_task_tick_runner(base_dir=temp_dir)
            run_bounded_teacher_gated_task_tick_runner(base_dir=temp_dir, max_ticks=2)
            runs = list_bounded_teacher_gated_task_tick_runs(temp_dir)
        self.assertEqual(len(runs), 2)

    def test_cli_run_show_and_list_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            command = [
                sys.executable,
                "-m",
                "ashl_core_v1.runtime.bounded_teacher_gated_task_tick_runner_cli",
                "--data-dir",
                temp_dir,
                "run-task-budget",
                "--max-ticks",
                "5",
            ]
            run_result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(run_result.returncode, 0, run_result.stderr)
            show_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ashl_core_v1.runtime.bounded_teacher_gated_task_tick_runner_cli",
                    "--data-dir",
                    temp_dir,
                    "show-last-run",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(show_result.returncode, 0, show_result.stderr)
            list_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ashl_core_v1.runtime.bounded_teacher_gated_task_tick_runner_cli",
                    "--data-dir",
                    temp_dir,
                    "list-runs",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(list_result.returncode, 0, list_result.stderr)

    def test_temp_directory_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_bounded_teacher_gated_task_tick_runner(base_dir=temp_dir)
            self.assertTrue(Path(temp_dir).exists())
        self.assertFalse(Path("ashl_core_v1/data").exists())


if __name__ == "__main__":
    unittest.main()
