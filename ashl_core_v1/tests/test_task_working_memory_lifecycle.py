import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.memory.task_working_memory_lifecycle import (
    ActiveTaskFrame,
    SuspendedTaskFrame,
    TaskWorkingMemoryClosureRecord,
    TaskWorkingMemoryDispositionRecord,
    TaskWorkingMemoryTickUpdate,
    apply_task_working_memory_tick_update,
    build_blocked_task_working_memory_lifecycle_demo,
    close_task_working_memory,
    create_active_task_frame,
    create_suspended_task_frame,
    create_task_working_memory_disposition,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.memory.task_working_memory_lifecycle_cli"


class TaskWorkingMemoryLifecycleTests(unittest.TestCase):
    def run_cli(
        self,
        data_dir: Path,
        *args: str,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", CLI_MODULE, "--data-dir", str(data_dir), *args],
            cwd=ROOT,
            check=check,
            capture_output=True,
            text=True,
        )

    def active_frame(self) -> ActiveTaskFrame:
        return create_active_task_frame(
            current_goal="handle front obstacle",
            approved_scope="sandbox_working_memory_only",
            task_id="task_001",
            current_step="step_forward",
            source_trace_refs=("trace:task_001",),
        )

    def updated_frame_and_update(self) -> tuple[ActiveTaskFrame, TaskWorkingMemoryTickUpdate]:
        result = apply_task_working_memory_tick_update(
            self.active_frame(),
            tick_id="tick_001",
            after_step="step_forward",
            observed_outcome_ref="outcome:blocked",
            observed_outcome_label="blocked",
            working_memory_delta={"last_outcome_label": "blocked"},
            next_candidate_hints_added=("observe_or_adjust",),
            continue_allowed_after_update=False,
            stop_reason_after_update="blocked_front_obstacle",
        )
        return (
            result["updated_active_task_frame"],
            result["tick_update"],
        )

    def closure_record(self) -> TaskWorkingMemoryClosureRecord:
        updated_frame, _ = self.updated_frame_and_update()
        return close_task_working_memory(
            updated_frame,
            final_task_status="failed",
            stop_reason="blocked_front_obstacle",
        )

    def test_active_task_frame_requires_memory_layer_working(self):
        with self.assertRaises(ValueError):
            ActiveTaskFrame(
                active_task_frame_id="frame_001",
                memory_layer="long_term",
                task_id="task_001",
                task_status="active",
                current_goal="goal",
                approved_scope="scope",
                current_tick=0,
                current_step=None,
                recent_attempt_refs=(),
                last_outcome_ref=None,
                last_outcome_label=None,
                next_candidate_hints=(),
                blocked_reason=None,
                continue_allowed=True,
                stop_reason=None,
                source_trace_refs=(),
            )

    def test_active_task_frame_active_status_allows_continue(self):
        frame = self.active_frame()

        self.assertEqual("working", frame.memory_layer)
        self.assertEqual("active", frame.task_status)
        self.assertTrue(frame.continue_allowed)

    def test_active_task_frame_completed_status_blocks_continue(self):
        with self.assertRaises(ValueError):
            ActiveTaskFrame(
                active_task_frame_id="frame_001",
                memory_layer="working",
                task_id="task_001",
                task_status="completed",
                current_goal="goal",
                approved_scope="scope",
                current_tick=1,
                current_step="done",
                recent_attempt_refs=(),
                last_outcome_ref=None,
                last_outcome_label=None,
                next_candidate_hints=(),
                blocked_reason=None,
                continue_allowed=True,
                stop_reason=None,
                source_trace_refs=(),
            )

    def test_task_working_memory_tick_update_links_to_active_task_frame(self):
        updated_frame, update = self.updated_frame_and_update()

        self.assertEqual(updated_frame.active_task_frame_id, update.active_task_frame_id)
        self.assertEqual(1, update.tick_number)

    def test_task_working_memory_tick_update_records_outcome_and_next_hints(self):
        updated_frame, update = self.updated_frame_and_update()

        self.assertEqual("blocked", update.observed_outcome_label)
        self.assertEqual(("observe_or_adjust",), update.next_candidate_hints_added)
        self.assertIn("observe_or_adjust", updated_frame.next_candidate_hints)
        self.assertFalse(update.continue_allowed_after_update)

    def test_task_working_memory_closure_record_closes_active_task_frame(self):
        updated_frame, _ = self.updated_frame_and_update()
        closure = close_task_working_memory(
            updated_frame,
            final_task_status="failed",
            stop_reason="blocked_front_obstacle",
        )

        self.assertEqual(updated_frame.active_task_frame_id, closure.active_task_frame_id)
        self.assertEqual("failed", closure.final_task_status)
        self.assertEqual("blocked_front_obstacle", closure.stop_reason)

    def test_task_working_memory_disposition_record_can_discard_scratch(self):
        closure = self.closure_record()
        disposition = create_task_working_memory_disposition(
            closure,
            discard_scratch_refs=("scratch:retry_notes",),
        )

        self.assertEqual(("scratch:retry_notes",), disposition.discard_scratch_refs)

    def test_task_working_memory_disposition_record_can_keep_session_summary(self):
        closure = self.closure_record()
        disposition = create_task_working_memory_disposition(
            closure,
            session_summary_refs=("session_summary:task_001",),
        )

        self.assertEqual(("session_summary:task_001",), disposition.session_summary_refs)

    def test_task_working_memory_disposition_can_emit_learning_digest_candidate_refs(self):
        closure = self.closure_record()
        disposition = create_task_working_memory_disposition(
            closure,
            learning_digest_candidate_refs=("learning_digest_candidate:blocked",),
        )

        self.assertEqual(
            ("learning_digest_candidate:blocked",),
            disposition.learning_digest_candidate_refs,
        )

    def test_task_working_memory_disposition_can_create_suspended_task_refs(self):
        closure = self.closure_record()
        disposition = create_task_working_memory_disposition(
            closure,
            suspended_task_frame_refs=("suspended_task_frame:task_001",),
        )

        self.assertEqual(
            ("suspended_task_frame:task_001",),
            disposition.suspended_task_frame_refs,
        )

    def test_disposition_does_not_directly_promote_to_other_memory_layers(self):
        closure = self.closure_record()

        with self.assertRaises(ValueError):
            create_task_working_memory_disposition(
                closure,
                learning_digest_candidate_refs=("core:direct_write",),
            )
        with self.assertRaises(ValueError):
            create_task_working_memory_disposition(
                closure,
                learning_digest_candidate_refs=("long_term:direct_write",),
            )
        with self.assertRaises(ValueError):
            create_task_working_memory_disposition(
                closure,
                learning_digest_candidate_refs=("archive:direct_write",),
            )
        with self.assertRaises(ValueError):
            create_task_working_memory_disposition(
                closure,
                learning_digest_candidate_refs=("anchor:direct_write",),
            )

    def test_suspended_task_frame_preserves_resume_hint(self):
        updated_frame, _ = self.updated_frame_and_update()
        closure = close_task_working_memory(
            updated_frame,
            final_task_status="suspended",
            stop_reason="teacher_pause",
        )

        suspended = create_suspended_task_frame(
            updated_frame,
            closure,
            pause_reason="teacher_pause",
            needed_next="teacher_review",
            resume_hint="observe before retry",
        )

        self.assertEqual("observe before retry", suspended.resume_hint)
        self.assertEqual(updated_frame.task_id, suspended.task_id)

    def test_all_records_support_to_dict_and_from_dict(self):
        updated_frame, update = self.updated_frame_and_update()
        closure = close_task_working_memory(
            updated_frame,
            final_task_status="failed",
            stop_reason="blocked_front_obstacle",
        )
        disposition = create_task_working_memory_disposition(
            closure,
            discard_scratch_refs=("scratch:retry_notes",),
        )
        suspended = create_suspended_task_frame(
            updated_frame,
            closure,
            pause_reason="teacher_pause",
            resume_hint="observe before retry",
        )

        self.assertEqual(
            self.active_frame().task_id,
            ActiveTaskFrame.from_dict(self.active_frame().to_dict()).task_id,
        )
        self.assertEqual(
            update.tick_id,
            TaskWorkingMemoryTickUpdate.from_dict(update.to_dict()).tick_id,
        )
        self.assertEqual(
            closure.task_id,
            TaskWorkingMemoryClosureRecord.from_dict(closure.to_dict()).task_id,
        )
        self.assertEqual(
            disposition.task_closure_record_id,
            TaskWorkingMemoryDispositionRecord.from_dict(
                disposition.to_dict()
            ).task_closure_record_id,
        )
        self.assertEqual(
            suspended.resume_hint,
            SuspendedTaskFrame.from_dict(suspended.to_dict()).resume_hint,
        )

    def test_demo_creates_all_required_records(self):
        demo = build_blocked_task_working_memory_lifecycle_demo()

        self.assertTrue(demo["task_working_memory_lifecycle_demo_created"])
        self.assertIn("active_task_frame", demo)
        self.assertIn("task_working_memory_tick_update", demo)
        self.assertIn("task_closure_record", demo)
        self.assertIn("task_working_memory_disposition", demo)

    def test_demo_marks_working_memory_is_five_layer_member_true(self):
        demo = build_blocked_task_working_memory_lifecycle_demo()

        self.assertEqual("working", demo["memory_layer"])
        self.assertTrue(demo["working_memory_is_five_layer_member"])

    def test_demo_marks_direct_promotion_to_other_memory_layer_false(self):
        demo = build_blocked_task_working_memory_lifecycle_demo()

        self.assertFalse(demo["direct_promotion_to_other_memory_layer"])
        self.assertIn(
            "learning_digest_candidate:",
            demo["task_working_memory_disposition"]["learning_digest_candidate_refs"][0],
        )

    def test_cli_run_demo_works_with_temp_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = json.loads(self.run_cli(Path(temp_dir), "run-demo").stdout)

            self.assertTrue(payload["task_working_memory_lifecycle_demo_created"])
            self.assertEqual("working", payload["memory_layer"])
            self.assertFalse(payload["direct_promotion_to_other_memory_layer"])

    def test_cli_show_last_demo_shows_latest_demo(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            run_payload = json.loads(self.run_cli(data_dir, "run-demo").stdout)
            last_payload = json.loads(self.run_cli(data_dir, "show-last-demo").stdout)

            self.assertEqual(
                run_payload["active_task_frame_id"],
                last_payload["active_task_frame_id"],
            )

    def test_cli_show_missing_demo_returns_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "show-last-demo", check=False)

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
