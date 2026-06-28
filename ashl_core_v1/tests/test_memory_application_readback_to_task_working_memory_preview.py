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
    build_memory_application_readback_preview,
    list_memory_application_readback_previews,
    preview_all_memory_application_readbacks,
    preview_memory_application_readback,
)
from ashl_core_v1.memory.reviewed_learning_to_memory_trace import (
    build_all_approved_reviewed_learning_memory_traces,
    list_memory_application_data_records,
)
from ashl_core_v1.memory.task_working_memory_lifecycle import create_active_task_frame
from ashl_core_v1.runtime.cradle_task_teacher_console import (
    preview_memory_readback_from_teacher_console,
)
from ashl_core_v1.runtime.multi_case_closure_candidate_audit import (
    run_multi_case_closure_candidate_audit,
)
from ashl_core_v1.runtime.multi_case_cradle_task_suite import (
    run_all_multi_case_cradle_task_cases,
)


class MemoryApplicationReadbackToTaskWorkingMemoryPreviewTests(unittest.TestCase):
    def test_approved_memory_application_data_can_create_readback_preview(self) -> None:
        with self._memory_data_temp_dir("blocked_front_obstacle") as temp_dir:
            payload = preview_memory_application_readback(
                memory_application_data_id=self._memory_data_id(temp_dir),
                case_id="blocked_front_obstacle",
                base_dir=temp_dir,
            )
        self.assertTrue(payload["memory_application_readback_preview_created"])

    def test_blocked_memory_creates_direct_retry_hints(self) -> None:
        hints = self._preview_hints_for_kind("blocked_front_obstacle")
        self.assertIn("observe_before_direct_retry", hints)
        self.assertIn("avoid_same_failed_direct_retry", hints)

    def test_unknown_memory_creates_gather_context_hint(self) -> None:
        hints = self._preview_hints_for_kind("unknown_resolved")
        self.assertIn("gather_context_first", hints)
        self.assertIn("observe_or_adjust", hints)

    def test_success_memory_creates_known_success_hint(self) -> None:
        hints = self._preview_hints_for_kind("successful_path")
        self.assertIn("known_success_path_available", hints)

    def test_conflict_memory_creates_expected_actual_hint(self) -> None:
        hints = self._preview_hints_for_kind("expected_vs_actual_mismatch")
        self.assertIn("verify_expected_actual_before_retry", hints)

    def test_preview_only_true_and_not_applied(self) -> None:
        with self._memory_data_temp_dir("blocked_front_obstacle") as temp_dir:
            payload = preview_memory_application_readback(
                memory_application_data_id=self._memory_data_id(temp_dir),
                case_id="blocked_front_obstacle",
                base_dir=temp_dir,
            )
        preview = payload["memory_application_readback_preview"]
        hint = payload["task_working_memory_readback_hints"][0]
        self.assertTrue(preview["preview_only"])
        self.assertFalse(preview["applied_to_working_memory"])
        self.assertTrue(hint["preview_only"])
        self.assertFalse(hint["applied_to_working_memory"])

    def test_readback_preserves_memory_application_data_id(self) -> None:
        with self._memory_data_temp_dir("blocked_front_obstacle") as temp_dir:
            memory_id = self._memory_data_id(temp_dir)
            payload = preview_memory_application_readback(
                memory_application_data_id=memory_id,
                case_id="blocked_front_obstacle",
                base_dir=temp_dir,
            )
        self.assertEqual(
            payload["memory_application_readback_preview"][
                "source_memory_application_data_id"
            ],
            memory_id,
        )

    def test_readback_preserves_active_task_frame_id(self) -> None:
        with self._memory_data_temp_dir("blocked_front_obstacle") as temp_dir:
            frame = create_active_task_frame(
                current_goal="custom preview",
                approved_scope="preview_only",
                task_id="custom_preview_task",
            ).to_dict()
            payload = build_memory_application_readback_preview(
                memory_application_data_id=self._memory_data_id(temp_dir),
                case_id="blocked_front_obstacle",
                active_task_frame=frame,
                base_dir=temp_dir,
            )
        self.assertEqual(
            payload["memory_application_readback_preview"][
                "target_active_task_frame_id"
            ],
            frame["active_task_frame_id"],
        )

    def test_preview_all_and_show_readback_previews_work(self) -> None:
        with self._memory_data_temp_dir("blocked_front_obstacle") as temp_dir:
            preview_all_memory_application_readbacks(temp_dir)
            previews = list_memory_application_readback_previews(temp_dir)
        self.assertEqual(len(previews), 1)

    def test_teacher_console_preview_works(self) -> None:
        with self._memory_data_temp_dir("blocked_front_obstacle") as temp_dir:
            payload = preview_memory_readback_from_teacher_console(temp_dir)
        self.assertEqual(payload["console_action"], "preview_memory_readback")
        self.assertFalse(payload["working_memory_mutation"])

    def test_no_runner_behavior_change_or_forbidden_effects(self) -> None:
        with self._memory_data_temp_dir("blocked_front_obstacle") as temp_dir:
            payload = preview_memory_application_readback(
                memory_application_data_id=self._memory_data_id(temp_dir),
                case_id="blocked_front_obstacle",
                base_dir=temp_dir,
            )
        preview = payload["memory_application_readback_preview"]
        self.assertFalse(preview["runner_behavior_changed"])
        self.assertFalse(preview["action_selection"])
        self.assertFalse(preview["memory_write"])
        self.assertFalse(preview["direct_memory_promotion"])
        self.assertFalse(preview["scheduler_created"])

    def test_cli_commands_work(self) -> None:
        with self._memory_data_temp_dir("blocked_front_obstacle") as temp_dir:
            memory_id = self._memory_data_id(temp_dir)
            preview_result = self._run_cli(
                temp_dir,
                "preview-readback",
                "--memory-application-data-id",
                memory_id,
                "--case-id",
                "blocked_front_obstacle",
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            all_result = self._run_cli(temp_dir, "preview-all")
            self.assertEqual(all_result.returncode, 0, all_result.stderr)
            show_result = self._run_cli(temp_dir, "show-readback-previews")
            self.assertEqual(show_result.returncode, 0, show_result.stderr)

    def test_no_repo_data_pollution(self) -> None:
        with self._memory_data_temp_dir("blocked_front_obstacle") as temp_dir:
            preview_all_memory_application_readbacks(temp_dir)
            self.assertTrue(Path(temp_dir).exists())
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _preview_hints_for_kind(self, candidate_kind: str) -> list[str]:
        with self._memory_data_temp_dir(candidate_kind) as temp_dir:
            payload = preview_memory_application_readback(
                memory_application_data_id=self._memory_data_id(temp_dir),
                case_id=candidate_kind,
                base_dir=temp_dir,
            )
            return payload["memory_application_readback_preview"][
                "suggested_working_memory_hints"
            ]

    def _memory_data_temp_dir(self, candidate_kind: str) -> tempfile.TemporaryDirectory:
        temp_dir = tempfile.TemporaryDirectory()
        run_all_multi_case_cradle_task_cases(base_dir=temp_dir.name)
        run_multi_case_closure_candidate_audit(temp_dir.name)
        candidate = self._candidate_by_kind(temp_dir.name, candidate_kind)
        review_cradle_learning_candidate(
            candidate_id=candidate["candidate_id"],
            status="approved",
            note=f"approve {candidate_kind}",
            base_dir=temp_dir.name,
        )
        build_all_approved_reviewed_learning_memory_traces(temp_dir.name)
        return temp_dir

    def _candidate_by_kind(self, temp_dir: str, candidate_kind: str) -> dict:
        for candidate in list_cradle_learning_candidates(temp_dir):
            if candidate["candidate_kind"] == candidate_kind:
                return candidate
        raise AssertionError(f"candidate kind not found: {candidate_kind}")

    def _memory_data_id(self, temp_dir: str) -> str:
        records = list_memory_application_data_records(temp_dir)
        self.assertEqual(len(records), 1)
        return records[0]["memory_application_data_id"]

    def _run_cli(self, temp_dir: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.memory.memory_application_readback_to_task_working_memory_preview_cli",
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
