from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.lesson.cradle_learning_candidate_review import (
    list_cradle_learning_candidates,
    list_cradle_reviewed_learning_records,
)
from ashl_core_v1.memory.memory_application_readback_to_task_working_memory_preview import (
    list_memory_application_readback_previews,
)
from ashl_core_v1.memory.memory_readback_apply_to_task_working_memory import (
    list_memory_readback_applications,
)
from ashl_core_v1.memory.reviewed_learning_to_memory_trace import (
    list_memory_application_data_records,
)
from ashl_core_v1.runtime.bounded_teacher_gated_task_tick_runner import (
    run_bounded_teacher_gated_task_tick_runner,
)
from ashl_core_v1.runtime.closed_learning_readback_loop_evidence import (
    list_closed_learning_readback_loop_evidence,
)
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    apply_readback_from_guided_cradle_growth_console,
    build_loop_evidence_from_guided_cradle_growth_console,
    build_memory_trace_from_guided_cradle_growth_console,
    close_last_run_from_guided_cradle_growth_console,
    get_guided_cradle_growth_status,
    guided_cradle_growth_next_step,
    list_candidates_from_guided_cradle_growth_console,
    preview_readback_from_guided_cradle_growth_console,
    review_candidate_from_guided_cradle_growth_console,
    run_case_from_guided_cradle_growth_console,
    run_readback_contrast_from_guided_cradle_growth_console,
    show_loop_evidence_from_guided_cradle_growth_console,
)
from ashl_core_v1.runtime.readback_influenced_bounded_task_contrast import (
    list_readback_influenced_bounded_task_contrasts,
)
from ashl_core_v1.runtime.task_run_closure import close_last_task_run


class GuidedCradleGrowthTeacherConsoleTests(unittest.TestCase):
    def test_growth_status_works_with_empty_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            status = get_guided_cradle_growth_status(temp_dir)
        self.assertIsNone(status["last_run_id"])
        self.assertEqual(status["suggested_next_step"], "run_case")

    def test_next_step_suggests_run_case_when_no_run_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertEqual(guided_cradle_growth_next_step(base_dir=temp_dir), "run_case")

    def test_next_step_suggests_close_run_after_run_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_bounded_teacher_gated_task_tick_runner(base_dir=temp_dir)
            self.assertEqual(guided_cradle_growth_next_step(base_dir=temp_dir), "close_run")

    def test_next_step_suggests_review_candidate_after_candidates_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            self._seed_closed_run(temp_dir)
            self.assertEqual(
                guided_cradle_growth_next_step(base_dir=temp_dir),
                "review_candidate",
            )

    def test_next_step_suggests_build_memory_trace_after_approved_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            candidate_id = self._seed_closed_run(temp_dir)
            review_candidate_from_guided_cradle_growth_console(
                candidate_id=candidate_id,
                status="approved",
                note="approve",
                base_dir=temp_dir,
            )
            self.assertEqual(
                guided_cradle_growth_next_step(base_dir=temp_dir),
                "build_memory_trace",
            )

    def test_next_step_suggests_preview_readback_after_memory_application_data(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            reviewed_id = self._seed_approved_review(temp_dir)
            build_memory_trace_from_guided_cradle_growth_console(
                reviewed_id=reviewed_id,
                base_dir=temp_dir,
            )
            self.assertEqual(
                guided_cradle_growth_next_step(base_dir=temp_dir),
                "preview_readback",
            )

    def test_next_step_suggests_apply_readback_after_preview(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_id = self._seed_memory_data(temp_dir)
            preview_readback_from_guided_cradle_growth_console(
                memory_application_data_id=memory_id,
                base_dir=temp_dir,
            )
            self.assertEqual(
                guided_cradle_growth_next_step(base_dir=temp_dir),
                "apply_readback",
            )

    def test_next_step_suggests_run_readback_contrast_after_application(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            preview = self._seed_preview(temp_dir)
            apply_readback_from_guided_cradle_growth_console(
                preview_id=preview["readback_preview_id"],
                active_task_frame_id=preview["target_active_task_frame_id"],
                base_dir=temp_dir,
            )
            self.assertEqual(
                guided_cradle_growth_next_step(base_dir=temp_dir),
                "run_readback_contrast",
            )

    def test_next_step_suggests_build_loop_evidence_after_contrast(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            self._seed_application(temp_dir)
            run_readback_contrast_from_guided_cradle_growth_console(base_dir=temp_dir)
            self.assertEqual(
                guided_cradle_growth_next_step(base_dir=temp_dir),
                "build_loop_evidence",
            )

    def test_next_step_suggests_inspect_loop_evidence_after_evidence_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            self._seed_contrast(temp_dir)
            build_loop_evidence_from_guided_cradle_growth_console(temp_dir)
            self.assertEqual(
                guided_cradle_growth_next_step(base_dir=temp_dir),
                "inspect_loop_evidence",
            )

    def test_guided_commands_call_existing_components(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            case_payload = run_case_from_guided_cradle_growth_console(
                case_id="blocked_front_obstacle",
                base_dir=temp_dir,
            )
            candidates = list_candidates_from_guided_cradle_growth_console(temp_dir)
        self.assertEqual(case_payload["guided_console_action"], "run_case")
        self.assertGreaterEqual(len(candidates["learning_candidates"]), 1)

    def test_full_guided_path_creates_expected_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            self._seed_contrast(temp_dir)
            evidence = build_loop_evidence_from_guided_cradle_growth_console(temp_dir)
            shown = show_loop_evidence_from_guided_cradle_growth_console(temp_dir)
            self.assertGreaterEqual(len(list_memory_readback_applications(temp_dir)), 1)
            self.assertGreaterEqual(
                len(list_readback_influenced_bounded_task_contrasts(temp_dir)),
                1,
            )
            self.assertGreaterEqual(
                len(list_closed_learning_readback_loop_evidence(temp_dir)),
                1,
            )
        self.assertEqual(
            evidence["loop_evidence"]["loop_status"],
            "closed_loop_evidence_visible",
        )
        self.assertEqual(shown["loop_status"], "closed_loop_evidence_visible")

    def test_cli_growth_status_and_next_step_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            status = self._run_cli(temp_dir, "growth-status")
            self.assertEqual(status.returncode, 0, status.stderr)
            next_step = self._run_cli(temp_dir, "next-step")
            self.assertEqual(next_step.returncode, 0, next_step.stderr)

    def test_cli_run_case_works(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self._run_cli(
                temp_dir,
                "run-case",
                "--case-id",
                "blocked_front_obstacle",
            )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_forbidden_flags_and_repo_pollution(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            status = get_guided_cradle_growth_status(temp_dir)
            self.assertFalse(status["scheduler_created"])
            self.assertFalse(status["action_execution_used"])
            self.assertFalse(status["memory_layer_write"])
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _seed_closed_run(self, temp_dir: str) -> str:
        run_bounded_teacher_gated_task_tick_runner(base_dir=temp_dir)
        close_last_task_run(temp_dir)
        return list_cradle_learning_candidates(temp_dir)[0]["candidate_id"]

    def _seed_approved_review(self, temp_dir: str) -> str:
        candidate_id = self._seed_closed_run(temp_dir)
        review_candidate_from_guided_cradle_growth_console(
            candidate_id=candidate_id,
            status="approved",
            note="approve",
            base_dir=temp_dir,
        )
        return list_cradle_reviewed_learning_records(temp_dir)[0][
            "cradle_reviewed_learning_record_id"
        ]

    def _seed_memory_data(self, temp_dir: str) -> str:
        reviewed_id = self._seed_approved_review(temp_dir)
        build_memory_trace_from_guided_cradle_growth_console(
            reviewed_id=reviewed_id,
            base_dir=temp_dir,
        )
        return list_memory_application_data_records(temp_dir)[0][
            "memory_application_data_id"
        ]

    def _seed_preview(self, temp_dir: str) -> dict:
        memory_id = self._seed_memory_data(temp_dir)
        preview_readback_from_guided_cradle_growth_console(
            memory_application_data_id=memory_id,
            base_dir=temp_dir,
        )
        return list_memory_application_readback_previews(temp_dir)[0]

    def _seed_application(self, temp_dir: str) -> None:
        preview = self._seed_preview(temp_dir)
        apply_readback_from_guided_cradle_growth_console(
            preview_id=preview["readback_preview_id"],
            active_task_frame_id=preview["target_active_task_frame_id"],
            base_dir=temp_dir,
        )

    def _seed_contrast(self, temp_dir: str) -> None:
        self._seed_application(temp_dir)
        run_readback_contrast_from_guided_cradle_growth_console(base_dir=temp_dir)

    def _run_cli(self, temp_dir: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli",
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
