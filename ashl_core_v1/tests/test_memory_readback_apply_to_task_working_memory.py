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
    list_memory_application_readback_previews,
    preview_all_memory_application_readbacks,
)
from ashl_core_v1.memory.memory_readback_apply_to_task_working_memory import (
    apply_memory_readback_to_task_working_memory,
    list_memory_readback_applications,
    load_last_memory_readback_application,
)
from ashl_core_v1.memory.reviewed_learning_to_memory_trace import (
    build_all_approved_reviewed_learning_memory_traces,
)
from ashl_core_v1.memory.task_working_memory_lifecycle import ActiveTaskFrame
from ashl_core_v1.runtime.cradle_task_teacher_console import (
    apply_memory_readback_from_teacher_console,
)
from ashl_core_v1.runtime.multi_case_closure_candidate_audit import (
    run_multi_case_closure_candidate_audit,
)
from ashl_core_v1.runtime.multi_case_cradle_task_suite import (
    run_all_multi_case_cradle_task_cases,
)


class MemoryReadbackApplyToTaskWorkingMemoryTests(unittest.TestCase):
    def test_valid_preview_can_apply_hints_to_active_task_frame(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            payload = self._apply_first_preview(temp_dir)
        self.assertTrue(payload["memory_readback_application_created"])
        self.assertTrue(
            payload["task_working_memory_readback_application_record"][
                "working_memory_updated"
            ]
        )

    def test_applied_record_preserves_memory_application_data_id(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            preview = self._first_preview(temp_dir)
            payload = self._apply_first_preview(temp_dir)
        self.assertEqual(
            payload["task_working_memory_readback_application_record"][
                "source_memory_application_data_id"
            ],
            preview["source_memory_application_data_id"],
        )

    def test_applied_record_preserves_preview_id(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            preview = self._first_preview(temp_dir)
            payload = self._apply_first_preview(temp_dir)
        self.assertEqual(
            payload["task_working_memory_readback_application_record"][
                "source_readback_preview_id"
            ],
            preview["readback_preview_id"],
        )

    def test_applied_record_preserves_active_task_frame_id(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            preview = self._first_preview(temp_dir)
            payload = self._apply_first_preview(temp_dir)
        self.assertEqual(
            payload["task_working_memory_readback_application_record"][
                "target_active_task_frame_id"
            ],
            preview["target_active_task_frame_id"],
        )

    def test_before_and_after_hints_differ(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            record = self._apply_first_preview(temp_dir)[
                "task_working_memory_readback_application_record"
            ]
        self.assertNotEqual(
            record["before_next_candidate_hints"],
            record["after_next_candidate_hints"],
        )

    def test_invalid_preview_blocks_application(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            with self.assertRaises(LookupError):
                apply_memory_readback_to_task_working_memory(
                    preview_id="missing",
                    active_task_frame_id="active",
                    base_dir=temp_dir,
                )

    def test_missing_active_task_frame_blocks_application(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            with self.assertRaises(LookupError):
                apply_memory_readback_to_task_working_memory(
                    preview_id=self._first_preview(temp_dir)["readback_preview_id"],
                    active_task_frame_id="wrong_frame",
                    base_dir=temp_dir,
                )

    def test_duplicate_hint_does_not_duplicate_in_working_memory(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            preview = self._first_preview(temp_dir)
            existing_hint = preview["suggested_working_memory_hints"][0]
            frame = ActiveTaskFrame(
                active_task_frame_id=preview["target_active_task_frame_id"],
                memory_layer="working",
                task_id=preview["task_id"],
                task_status="active",
                current_goal="duplicate hint test",
                approved_scope="bounded_task_working_memory_only",
                current_tick=0,
                current_step=None,
                recent_attempt_refs=(),
                last_outcome_ref=None,
                last_outcome_label=None,
                next_candidate_hints=(existing_hint,),
                blocked_reason=None,
                continue_allowed=True,
                stop_reason=None,
                source_trace_refs=(),
            )
            record = apply_memory_readback_to_task_working_memory(
                preview_id=preview["readback_preview_id"],
                active_task_frame_id=preview["target_active_task_frame_id"],
                active_task_frame=frame,
                base_dir=temp_dir,
            )["task_working_memory_readback_application_record"]
        self.assertEqual(
            record["after_next_candidate_hints"].count(existing_hint),
            1,
        )

    def test_application_scope_and_forbidden_flags(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            record = self._apply_first_preview(temp_dir)[
                "task_working_memory_readback_application_record"
            ]
        self.assertEqual(record["application_scope"], "bounded_task_working_memory_only")
        self.assertFalse(record["action_selection"])
        self.assertFalse(record["action_execution"])
        self.assertFalse(record["core_memory_write"])
        self.assertFalse(record["long_term_memory_write"])
        self.assertFalse(record["archive_memory_write"])
        self.assertFalse(record["anchor_layer_write"])
        self.assertFalse(record["direct_memory_promotion"])

    def test_cli_apply_readback_works(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            preview = self._first_preview(temp_dir)
            result = self._run_cli(
                temp_dir,
                "apply-readback",
                "--preview-id",
                preview["readback_preview_id"],
                "--active-task-frame-id",
                preview["target_active_task_frame_id"],
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            show = self._run_cli(temp_dir, "show-last-application")
            self.assertEqual(show.returncode, 0, show.stderr)
            listing = self._run_cli(temp_dir, "list-applications")
            self.assertEqual(listing.returncode, 0, listing.stderr)

    def test_teacher_console_apply_memory_readback_works(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            preview = self._first_preview(temp_dir)
            payload = apply_memory_readback_from_teacher_console(
                preview_id=preview["readback_preview_id"],
                active_task_frame_id=preview["target_active_task_frame_id"],
                base_dir=temp_dir,
            )
        self.assertEqual(payload["console_action"], "apply_memory_readback")
        self.assertFalse(payload["action_execution"])

    def test_show_and_list_applications_work(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            saved = self._apply_first_preview(temp_dir)
            loaded = load_last_memory_readback_application(temp_dir)
            listed = list_memory_readback_applications(temp_dir)
        self.assertEqual(
            loaded["task_working_memory_readback_application_record"][
                "readback_application_id"
            ],
            saved["task_working_memory_readback_application_record"][
                "readback_application_id"
            ],
        )
        self.assertEqual(len(listed), 1)

    def test_no_repo_data_pollution(self) -> None:
        with self._preview_temp_dir() as temp_dir:
            self._apply_first_preview(temp_dir)
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
            note="approve readback",
            base_dir=temp_dir.name,
        )
        build_all_approved_reviewed_learning_memory_traces(temp_dir.name)
        preview_all_memory_application_readbacks(temp_dir.name)
        return temp_dir

    def _first_preview(self, temp_dir: str) -> dict:
        return list_memory_application_readback_previews(temp_dir)[0]

    def _apply_first_preview(self, temp_dir: str) -> dict:
        preview = self._first_preview(temp_dir)
        return apply_memory_readback_to_task_working_memory(
            preview_id=preview["readback_preview_id"],
            active_task_frame_id=preview["target_active_task_frame_id"],
            base_dir=temp_dir,
        )

    def _run_cli(self, temp_dir: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.memory.memory_readback_apply_to_task_working_memory_cli",
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
