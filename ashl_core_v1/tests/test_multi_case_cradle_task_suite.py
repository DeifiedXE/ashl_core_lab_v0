from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.cradle_task_teacher_console import run_case_from_teacher_console
from ashl_core_v1.runtime.multi_case_cradle_task_suite import (
    list_cradle_task_suite_cases,
    load_last_multi_case_cradle_task_case_run,
    load_last_multi_case_cradle_task_suite_summary,
    run_all_multi_case_cradle_task_cases,
    run_multi_case_cradle_task_case,
)


class MultiCaseCradleTaskSuiteTests(unittest.TestCase):
    def test_list_cases_returns_all_six_cases(self) -> None:
        case_ids = {case["case_id"] for case in list_cradle_task_suite_cases()}
        self.assertEqual(
            case_ids,
            {
                "blocked_front_obstacle",
                "success_simple_reach",
                "unknown_needs_observe",
                "teacher_stopped",
                "suspended_waiting_for_teacher",
                "conflict_expected_vs_actual",
            },
        )

    def test_each_case_can_run_through_bounded_runner(self) -> None:
        for case in list_cradle_task_suite_cases():
            with self.subTest(case=case["case_id"]):
                payload = run_multi_case_cradle_task_case(case["case_id"])
                self.assertTrue(payload["bounded_task_run"]["bounded_task_tick_run_created"])
                self.assertTrue(payload["task_run_closure"]["task_run_closure_created"])

    def test_each_case_uses_working_memory_and_preserves_task_id(self) -> None:
        for case in list_cradle_task_suite_cases():
            with self.subTest(case=case["case_id"]):
                payload = run_multi_case_cradle_task_case(case["case_id"])
                record = payload["bounded_task_run"]["bounded_task_tick_run_record"]
                self.assertTrue(record["working_memory_used_for_all_ticks"])
                self.assertTrue(record["all_ticks_same_task"])

    def test_each_case_respects_max_ticks(self) -> None:
        for case in list_cradle_task_suite_cases():
            with self.subTest(case=case["case_id"]):
                payload = run_multi_case_cradle_task_case(case["case_id"], max_ticks=5)
                self.assertLessEqual(
                    payload["bounded_task_run"]["bounded_task_tick_run_record"][
                        "actual_ticks"
                    ],
                    5,
                )
        with self.assertRaises(ValueError):
            run_multi_case_cradle_task_case("blocked_front_obstacle", max_ticks=6)

    def test_blocked_case_closes_with_blocked_candidate(self) -> None:
        payload = run_multi_case_cradle_task_case("blocked_front_obstacle")
        kinds = self._candidate_kinds(payload)
        self.assertIn("blocked_front_obstacle", kinds)
        self.assertIn(
            payload["task_run_closure"]["task_run_closure_record"]["final_task_status"],
            {"failed", "system_stopped"},
        )

    def test_success_case_closes_completed(self) -> None:
        payload = run_multi_case_cradle_task_case("success_simple_reach")
        self.assertEqual(
            payload["task_run_closure"]["task_run_closure_record"]["final_task_status"],
            "completed",
        )
        self.assertIn("successful_path", self._candidate_kinds(payload))

    def test_unknown_case_produces_observe_related_candidate(self) -> None:
        payload = run_multi_case_cradle_task_case("unknown_needs_observe")
        self.assertTrue(
            {"unknown_resolved", "needs_observe"} & self._candidate_kinds(payload)
        )

    def test_teacher_stopped_case_closes_teacher_stopped(self) -> None:
        payload = run_multi_case_cradle_task_case("teacher_stopped")
        self.assertEqual(
            payload["task_run_closure"]["task_run_closure_record"]["final_task_status"],
            "teacher_stopped",
        )
        self.assertIn("teacher_stopped", self._candidate_kinds(payload))

    def test_suspended_case_creates_or_references_suspended_task_frame(self) -> None:
        payload = run_multi_case_cradle_task_case("suspended_waiting_for_teacher")
        self.assertEqual(
            payload["task_run_closure"]["task_run_closure_record"]["final_task_status"],
            "suspended",
        )
        self.assertIsNotNone(payload["task_run_closure"]["suspended_task_frame"])
        self.assertTrue({"suspended", "waiting_for_teacher"} & self._candidate_kinds(payload))

    def test_conflict_case_produces_mismatch_or_conflict_candidate(self) -> None:
        payload = run_multi_case_cradle_task_case("conflict_expected_vs_actual")
        self.assertTrue(
            {"expected_vs_actual_mismatch", "conflict_detected"}
            & self._candidate_kinds(payload)
        )

    def test_run_all_cases_produces_suite_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = run_all_multi_case_cradle_task_cases(base_dir=temp_dir)
            loaded = load_last_multi_case_cradle_task_suite_summary(temp_dir)
        self.assertEqual(payload["suite_summary"]["case_count"], 6)
        self.assertEqual(loaded["suite_summary"]["case_count"], 6)

    def test_teacher_console_can_run_named_case(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = run_case_from_teacher_console(
                case_id="success_simple_reach",
                base_dir=temp_dir,
            )
        self.assertEqual(payload["case_run"]["case_id"], "success_simple_reach")
        self.assertFalse(payload["scheduler_created"])

    def test_no_scheduler_action_or_direct_memory_promotion(self) -> None:
        payload = run_all_multi_case_cradle_task_cases()
        summary = payload["suite_summary"]
        self.assertFalse(summary["scheduler_used"])
        self.assertFalse(summary["free_action_selection_used"])
        self.assertFalse(summary["action_execution_used"])
        self.assertFalse(summary["direct_memory_promotion_used"])

    def test_cli_commands_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            list_result = self._run_cli(temp_dir, "list-cases")
            self.assertEqual(list_result.returncode, 0, list_result.stderr)
            run_result = self._run_cli(
                temp_dir,
                "run-case",
                "--case-id",
                "blocked_front_obstacle",
                "--max-ticks",
                "5",
            )
            self.assertEqual(run_result.returncode, 0, run_result.stderr)
            show_result = self._run_cli(temp_dir, "show-last-case-run")
            self.assertEqual(show_result.returncode, 0, show_result.stderr)
            all_result = self._run_cli(temp_dir, "run-all-cases", "--max-ticks", "5")
            self.assertEqual(all_result.returncode, 0, all_result.stderr)
            summary_result = self._run_cli(temp_dir, "show-suite-summary")
            self.assertEqual(summary_result.returncode, 0, summary_result.stderr)
            self.assertIsNotNone(load_last_multi_case_cradle_task_case_run(temp_dir))

    def test_no_repo_data_pollution(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_all_multi_case_cradle_task_cases(base_dir=temp_dir)
            self.assertTrue(Path(temp_dir).exists())
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _candidate_kinds(self, payload: dict) -> set[str]:
        return {
            candidate["candidate_kind"]
            for candidate in payload["task_run_closure"][
                "task_learning_digest_candidate_records"
            ]
        }

    def _run_cli(self, temp_dir: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.runtime.multi_case_cradle_task_suite_cli",
                "--data-dir",
                temp_dir,
                *args,
            ],
            check=False,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
