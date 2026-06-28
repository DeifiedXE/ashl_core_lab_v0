from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.cradle_task_teacher_console import (
    close_last_run_from_teacher_console,
    get_cradle_task_teacher_console_status,
    mark_learning_candidate_from_teacher_console,
    run_blocked_task_from_teacher_console,
    show_learning_candidates_from_teacher_console,
    show_working_memory_from_teacher_console,
)


class CradleTaskTeacherConsoleTests(unittest.TestCase):
    def test_status_works_without_prior_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            status = get_cradle_task_teacher_console_status(temp_dir)
        self.assertIsNone(status["last_run_id"])
        self.assertEqual(status["pending_learning_candidate_count"], 0)

    def test_run_blocked_task_calls_bounded_runner(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = run_blocked_task_from_teacher_console(
                max_ticks=5,
                base_dir=temp_dir,
            )
        self.assertEqual(payload["console_action"], "run_blocked_task")
        self.assertTrue(payload["bounded_task_run"]["bounded_task_tick_run_created"])
        self.assertFalse(payload["scheduler_created"])
        self.assertFalse(payload["action_execution_used"])

    def test_show_working_memory_returns_active_frame_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_blocked_task_from_teacher_console(base_dir=temp_dir)
            summary = show_working_memory_from_teacher_console(temp_dir)
        self.assertEqual(summary["task_id"], "handle_front_obstacle")
        self.assertEqual(summary["current_tick"], 5)
        self.assertEqual(summary["last_outcome_label"], "budget_stop")

    def test_close_last_run_creates_closure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_blocked_task_from_teacher_console(base_dir=temp_dir)
            closure = close_last_run_from_teacher_console(temp_dir)
        self.assertEqual(closure["console_action"], "close_last_run")
        self.assertTrue(closure["task_run_closure"]["task_run_closure_created"])

    def test_show_learning_candidates_lists_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_blocked_task_from_teacher_console(base_dir=temp_dir)
            close_last_run_from_teacher_console(temp_dir)
            candidates = show_learning_candidates_from_teacher_console(temp_dir)[
                "task_learning_digest_candidates"
            ]
        self.assertTrue(candidates)

    def test_mark_candidate_teacher_seen_works(self) -> None:
        candidate_id, temp_dir = self._create_candidate_fixture()
        with temp_dir:
            mark = mark_learning_candidate_from_teacher_console(
                candidate_id=candidate_id,
                status="teacher_seen",
                base_dir=temp_dir.name,
            )
        self.assertTrue(mark["candidate_marked"])
        self.assertFalse(mark["approved"])

    def test_mark_candidate_ignored_works(self) -> None:
        candidate_id, temp_dir = self._create_candidate_fixture()
        with temp_dir:
            mark = mark_learning_candidate_from_teacher_console(
                candidate_id=candidate_id,
                status="ignored",
                base_dir=temp_dir.name,
            )
        self.assertEqual(mark["status"], "ignored")

    def test_mark_candidate_needs_manual_review_works(self) -> None:
        candidate_id, temp_dir = self._create_candidate_fixture()
        with temp_dir:
            mark = mark_learning_candidate_from_teacher_console(
                candidate_id=candidate_id,
                status="needs_manual_review",
                base_dir=temp_dir.name,
            )
        self.assertEqual(mark["status"], "needs_manual_review")

    def test_mark_candidate_does_not_approve_candidate(self) -> None:
        candidate_id, temp_dir = self._create_candidate_fixture()
        with temp_dir:
            with self.assertRaises(ValueError):
                mark_learning_candidate_from_teacher_console(
                    candidate_id=candidate_id,
                    status="approved",
                    base_dir=temp_dir.name,
                )

    def test_mark_candidate_does_not_write_memory(self) -> None:
        candidate_id, temp_dir = self._create_candidate_fixture()
        with temp_dir:
            mark = mark_learning_candidate_from_teacher_console(
                candidate_id=candidate_id,
                status="teacher_seen",
                base_dir=temp_dir.name,
            )
        self.assertFalse(mark["memory_write"])
        self.assertFalse(mark["reviewed_learning_digest_created"])

    def test_console_does_not_create_scheduler_or_execute_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = run_blocked_task_from_teacher_console(base_dir=temp_dir)
        self.assertFalse(payload["scheduler_created"])
        self.assertFalse(payload["action_execution_used"])

    def test_cli_status_run_close_show_and_mark_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            status = self._run_cli(temp_dir, "status")
            self.assertEqual(status.returncode, 0, status.stderr)
            run = self._run_cli(temp_dir, "run-blocked-task", "--max-ticks", "5")
            self.assertEqual(run.returncode, 0, run.stderr)
            working = self._run_cli(temp_dir, "show-working-memory")
            self.assertEqual(working.returncode, 0, working.stderr)
            close = self._run_cli(temp_dir, "close-last-run")
            self.assertEqual(close.returncode, 0, close.stderr)
            candidates = show_learning_candidates_from_teacher_console(temp_dir)[
                "task_learning_digest_candidates"
            ]
            candidate_id = candidates[0]["candidate_id"]
            mark = self._run_cli(
                temp_dir,
                "mark-candidate",
                "--candidate-id",
                candidate_id,
                "--status",
                "teacher_seen",
            )
            self.assertEqual(mark.returncode, 0, mark.stderr)
            show = self._run_cli(temp_dir, "show-learning-candidates")
            self.assertEqual(show.returncode, 0, show.stderr)

    def test_temp_directory_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_blocked_task_from_teacher_console(base_dir=temp_dir)
            close_last_run_from_teacher_console(temp_dir)
            self.assertTrue(Path(temp_dir).exists())
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _create_candidate_fixture(self) -> tuple[str, tempfile.TemporaryDirectory]:
        temp_dir = tempfile.TemporaryDirectory()
        run_blocked_task_from_teacher_console(base_dir=temp_dir.name)
        close_last_run_from_teacher_console(temp_dir.name)
        candidates = show_learning_candidates_from_teacher_console(temp_dir.name)[
            "task_learning_digest_candidates"
        ]
        return candidates[0]["candidate_id"], temp_dir

    def _run_cli(self, temp_dir: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.runtime.cradle_task_teacher_console_cli",
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
