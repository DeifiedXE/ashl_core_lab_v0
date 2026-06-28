from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.lesson.cradle_learning_candidate_review import (
    list_cradle_learning_candidates,
    review_cradle_learning_candidate,
)
from ashl_core_v1.memory.memory_application_readback_to_task_working_memory_preview import (
    preview_all_memory_application_readbacks,
)
from ashl_core_v1.memory.reviewed_learning_to_memory_trace import (
    build_all_approved_reviewed_learning_memory_traces,
)
from ashl_core_v1.runtime.cradle_task_teacher_console import (
    run_readback_contrast_from_teacher_console,
)
from ashl_core_v1.runtime.multi_case_closure_candidate_audit import (
    run_multi_case_closure_candidate_audit,
)
from ashl_core_v1.runtime.multi_case_cradle_task_suite import (
    run_all_multi_case_cradle_task_cases,
)
from ashl_core_v1.runtime.readback_influenced_bounded_task_contrast import (
    build_readback_influenced_bounded_task_contrast,
    list_readback_influenced_bounded_task_contrasts,
    load_last_readback_influenced_bounded_task_contrast,
    run_readback_influenced_bounded_task_contrast,
)


class ReadbackInfluencedBoundedTaskContrastTests(unittest.TestCase):
    def test_valid_contrast_passes(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            contrast = run_readback_influenced_bounded_task_contrast(base_dir=temp_dir)
        self.assertEqual(contrast["contrast_status"], "passed")

    def test_baseline_and_readback_runs_exist(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            contrast = run_readback_influenced_bounded_task_contrast(base_dir=temp_dir)
        self.assertTrue(contrast["baseline_run_id"])
        self.assertTrue(contrast["readback_applied_run_id"])

    def test_readback_application_id_preserved(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            contrast = run_readback_influenced_bounded_task_contrast(base_dir=temp_dir)
        self.assertTrue(contrast["readback_application_id"].startswith("memory_readback_application:"))

    def test_readback_hint_visible_in_working_memory_and_tick_context(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            contrast = run_readback_influenced_bounded_task_contrast(base_dir=temp_dir)
        self.assertTrue(contrast["readback_hint_visible_in_working_memory"])
        self.assertTrue(contrast["readback_hint_visible_in_tick_context"])

    def test_task_processing_difference_visible_true(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            contrast = run_readback_influenced_bounded_task_contrast(base_dir=temp_dir)
        self.assertTrue(contrast["task_processing_difference_visible"])

    def test_missing_readback_application_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contrast = build_readback_influenced_bounded_task_contrast(base_dir=temp_dir)
        self.assertEqual(contrast["contrast_status"], "blocked_missing_readback_application")

    def test_same_tick_summaries_with_no_difference_block(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            contrast = build_readback_influenced_bounded_task_contrast(
                base_dir=temp_dir,
                force_same_tick_summaries=True,
            )
        self.assertEqual(contrast["contrast_status"], "failed_no_readback_difference")

    def test_free_action_selection_flag_blocks(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            contrast = build_readback_influenced_bounded_task_contrast(
                base_dir=temp_dir,
                free_action_selection_used=True,
            )
        self.assertEqual(contrast["contrast_status"], "blocked_action_selection_detected")

    def test_action_execution_flag_blocks(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            contrast = build_readback_influenced_bounded_task_contrast(
                base_dir=temp_dir,
                action_execution_used=True,
            )
        self.assertEqual(contrast["contrast_status"], "blocked_action_execution_detected")

    def test_scheduler_flag_blocks(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            contrast = build_readback_influenced_bounded_task_contrast(
                base_dir=temp_dir,
                scheduler_used=True,
            )
        self.assertEqual(contrast["contrast_status"], "blocked_scheduler_detected")

    def test_memory_layer_promotion_flag_blocks(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            contrast = build_readback_influenced_bounded_task_contrast(
                base_dir=temp_dir,
                memory_layer_promotion_used=True,
            )
        self.assertEqual(
            contrast["contrast_status"],
            "blocked_memory_layer_promotion_detected",
        )

    def test_cli_run_contrast_works(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            result = self._run_cli(temp_dir, "run-contrast", "--case-id", "blocked_front_obstacle")
            self.assertEqual(result.returncode, 0, result.stderr)
            show = self._run_cli(temp_dir, "show-last-contrast")
            self.assertEqual(show.returncode, 0, show.stderr)
            listing = self._run_cli(temp_dir, "list-contrasts")
            self.assertEqual(listing.returncode, 0, listing.stderr)

    def test_teacher_console_run_readback_contrast_works(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            payload = run_readback_contrast_from_teacher_console(base_dir=temp_dir)
        self.assertEqual(payload["console_action"], "run_readback_contrast")
        self.assertFalse(payload["action_execution"])

    def test_show_and_list_contrasts_work(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            saved = run_readback_influenced_bounded_task_contrast(base_dir=temp_dir)
            loaded = load_last_readback_influenced_bounded_task_contrast(temp_dir)
            listed = list_readback_influenced_bounded_task_contrasts(temp_dir)
        self.assertEqual(loaded["contrast_id"], saved["contrast_id"])
        self.assertEqual(len(listed), 1)

    def test_no_repo_data_pollution(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            run_readback_influenced_bounded_task_contrast(base_dir=temp_dir)
            self.assertTrue(Path(temp_dir).exists())
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _preview_temp_dir(self) -> tempfile.TemporaryDirectory:
        temp_dir = tempfile.TemporaryDirectory()
        run_all_multi_case_cradle_task_cases(base_dir=temp_dir.name)
        run_multi_case_closure_candidate_audit(temp_dir.name)
        candidate = list_cradle_learning_candidates(temp_dir.name)[0]
        review_cradle_learning_candidate(
            candidate_id=candidate["candidate_id"],
            status="approved",
            note="approve contrast",
            base_dir=temp_dir.name,
        )
        build_all_approved_reviewed_learning_memory_traces(temp_dir.name)
        preview_all_memory_application_readbacks(temp_dir.name)
        return temp_dir

    def _run_cli(self, temp_dir: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.runtime.readback_influenced_bounded_task_contrast_cli",
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
