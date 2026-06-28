from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.bounded_teacher_gated_task_tick_runner import (
    build_bounded_teacher_gated_task_tick_run,
    run_bounded_teacher_gated_task_tick_runner,
)
from ashl_core_v1.runtime.task_run_closure import (
    build_task_run_closure,
    close_last_task_run,
    list_task_learning_digest_candidates,
    load_last_task_run_closure,
)


class TaskRunClosureAndLearningCandidateExtractionTests(unittest.TestCase):
    def test_close_last_run_creates_closure_record(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_bounded_teacher_gated_task_tick_runner(base_dir=temp_dir)
            payload = close_last_task_run(temp_dir)
        self.assertTrue(payload["task_run_closure_created"])
        self.assertIn("task_run_closure_record_id", payload["task_run_closure_record"])

    def test_closure_links_to_bounded_run(self) -> None:
        run = build_bounded_teacher_gated_task_tick_run()
        closure = build_task_run_closure(run)
        self.assertEqual(
            closure["task_run_closure_record"]["source_run_id"],
            run["bounded_task_tick_run_record"]["run_id"],
        )

    def test_disposition_discards_scratch_refs(self) -> None:
        closure = build_task_run_closure(build_bounded_teacher_gated_task_tick_run())
        self.assertTrue(closure["task_run_disposition_record"]["discard_scratch_refs"])

    def test_disposition_keeps_session_summary_ref(self) -> None:
        closure = build_task_run_closure(build_bounded_teacher_gated_task_tick_run())
        summary_id = closure["task_run_session_summary_record"][
            "task_run_session_summary_id"
        ]
        self.assertIn(
            summary_id,
            closure["task_run_disposition_record"]["session_summary_refs"],
        )

    def test_learning_candidates_are_review_required(self) -> None:
        closure = build_task_run_closure(build_bounded_teacher_gated_task_tick_run())
        self.assertTrue(closure["task_learning_digest_candidate_records"])
        self.assertTrue(
            all(
                candidate["review_required"]
                for candidate in closure["task_learning_digest_candidate_records"]
            )
        )

    def test_repeated_blocked_can_create_candidate(self) -> None:
        run = build_bounded_teacher_gated_task_tick_run()
        run["per_tick_working_memory_updates"][1]["observed_outcome_label"] = "blocked"
        closure = build_task_run_closure(run)
        kinds = {
            candidate["candidate_kind"]
            for candidate in closure["task_learning_digest_candidate_records"]
        }
        self.assertIn("repeated_blocked", kinds)

    def test_budget_stop_can_create_candidate(self) -> None:
        closure = build_task_run_closure(build_bounded_teacher_gated_task_tick_run())
        kinds = {
            candidate["candidate_kind"]
            for candidate in closure["task_learning_digest_candidate_records"]
        }
        self.assertIn("budget_stop", kinds)

    def test_no_direct_promotion_to_other_memory_layers(self) -> None:
        closure = build_task_run_closure(build_bounded_teacher_gated_task_tick_run())
        self.assertFalse(closure["task_run_disposition_record"]["direct_memory_promotion"])

    def test_no_automatic_reviewed_digest_or_memory_write(self) -> None:
        closure = build_task_run_closure(build_bounded_teacher_gated_task_tick_run())
        self.assertFalse(
            closure["task_run_closure_record"]["automatic_reviewed_digest_created"]
        )
        self.assertFalse(closure["task_run_closure_record"]["memory_write"])
        self.assertTrue(
            all(
                candidate["memory_write"] is False
                for candidate in closure["task_learning_digest_candidate_records"]
            )
        )

    def test_show_last_closure_works(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_bounded_teacher_gated_task_tick_runner(base_dir=temp_dir)
            saved = close_last_task_run(temp_dir)
            loaded = load_last_task_run_closure(temp_dir)
        self.assertEqual(
            loaded["task_run_closure_record"]["task_run_closure_record_id"],
            saved["task_run_closure_record"]["task_run_closure_record_id"],
        )

    def test_list_learning_candidates_works(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_bounded_teacher_gated_task_tick_runner(base_dir=temp_dir)
            close_last_task_run(temp_dir)
            candidates = list_task_learning_digest_candidates(temp_dir)
        self.assertTrue(candidates)

    def test_cli_close_show_and_list_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_bounded_teacher_gated_task_tick_runner(base_dir=temp_dir)
            close_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ashl_core_v1.runtime.task_run_closure_cli",
                    "--data-dir",
                    temp_dir,
                    "close-last-run",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(close_result.returncode, 0, close_result.stderr)
            show_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ashl_core_v1.runtime.task_run_closure_cli",
                    "--data-dir",
                    temp_dir,
                    "show-last-closure",
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
                    "ashl_core_v1.runtime.task_run_closure_cli",
                    "--data-dir",
                    temp_dir,
                    "list-learning-candidates",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(list_result.returncode, 0, list_result.stderr)

    def test_temp_directory_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_bounded_teacher_gated_task_tick_runner(base_dir=temp_dir)
            close_last_task_run(temp_dir)
            self.assertTrue(Path(temp_dir).exists())
        self.assertFalse(Path("ashl_core_v1/data").exists())


if __name__ == "__main__":
    unittest.main()
