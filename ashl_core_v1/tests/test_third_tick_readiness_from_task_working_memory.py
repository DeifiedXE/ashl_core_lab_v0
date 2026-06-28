import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.third_tick_readiness_from_task_working_memory import (
    READY_STATUS,
    ThirdTickReadinessFromTaskWorkingMemory,
    build_blocked_closed_task_third_tick_readiness_demo,
    build_ready_third_tick_readiness_demo,
    build_third_tick_readiness_from_task_working_memory,
    list_third_tick_readiness_from_task_working_memory,
    load_last_third_tick_readiness_from_task_working_memory,
    run_closed_task_blocked_third_tick_readiness_demo,
    run_third_tick_readiness_from_task_working_memory,
    validate_third_tick_readiness_from_task_working_memory,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.runtime.third_tick_readiness_from_task_working_memory_cli"


class ThirdTickReadinessFromTaskWorkingMemoryTests(unittest.TestCase):
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

    def parts(self) -> dict:
        return build_ready_third_tick_readiness_demo()

    def readiness_from_parts(
        self,
        parts: dict,
        **kwargs,
    ) -> ThirdTickReadinessFromTaskWorkingMemory:
        return build_third_tick_readiness_from_task_working_memory(
            parts.get("two_tick_audit"),
            parts.get("active_task_frame"),
            **kwargs,
        )

    def test_valid_readiness_passes(self):
        readiness = self.readiness_from_parts(self.parts())

        self.assertEqual(READY_STATUS, readiness.readiness_status)
        self.assertTrue(readiness.two_tick_audit_passed)
        self.assertTrue(readiness.active_task_can_continue)
        self.assertFalse(readiness.third_tick_created)
        self.assertTrue(
            validate_third_tick_readiness_from_task_working_memory(readiness)["valid"]
        )

    def test_two_tick_audit_not_passed_blocks_readiness(self):
        parts = self.parts()
        parts["two_tick_audit"]["continuity_status"] = "blocked_missing_tick2"

        readiness = self.readiness_from_parts(parts)

        self.assertEqual("blocked_two_tick_audit_not_passed", readiness.readiness_status)

    def test_missing_active_task_frame_blocks_readiness(self):
        parts = self.parts()
        parts["active_task_frame"] = None

        readiness = self.readiness_from_parts(parts)

        self.assertEqual("blocked_missing_active_task_frame", readiness.readiness_status)

    def test_task_id_mismatch_blocks_readiness(self):
        parts = self.parts()
        parts["active_task_frame"]["task_id"] = "other_task"

        readiness = self.readiness_from_parts(parts)

        self.assertEqual("blocked_task_id_mismatch", readiness.readiness_status)

    def test_non_working_memory_layer_blocks_readiness(self):
        parts = self.parts()
        parts["active_task_frame"]["memory_layer"] = "long_term"

        readiness = self.readiness_from_parts(parts)

        self.assertEqual("blocked_not_working_memory_layer", readiness.readiness_status)

    def test_tick2_not_reading_working_memory_blocks_readiness(self):
        parts = self.parts()
        parts["two_tick_audit"]["tick2_read_updated_working_memory"] = False

        readiness = self.readiness_from_parts(parts)

        self.assertEqual(
            "blocked_tick2_not_using_working_memory",
            readiness.readiness_status,
        )

    def test_tick2_not_using_tick1_outcome_blocks_readiness(self):
        parts = self.parts()
        parts["two_tick_audit"]["tick2_uses_tick1_outcome"] = False

        readiness = self.readiness_from_parts(parts)

        self.assertEqual(
            "blocked_tick2_not_using_tick1_outcome",
            readiness.readiness_status,
        )

    def test_tick2_not_using_tick1_hint_blocks_readiness(self):
        parts = self.parts()
        parts["two_tick_audit"]["tick2_uses_tick1_candidate_hint"] = False

        readiness = self.readiness_from_parts(parts)

        self.assertEqual(
            "blocked_tick2_not_using_tick1_hint",
            readiness.readiness_status,
        )

    def test_closed_task_blocks_readiness(self):
        demo = build_blocked_closed_task_third_tick_readiness_demo()

        self.assertEqual("blocked_active_task_closed", demo["readiness_status"])
        self.assertFalse(demo["active_task_can_continue"])

    def test_continue_allowed_false_blocks_readiness(self):
        parts = self.parts()
        parts["active_task_frame"]["continue_allowed"] = False

        readiness = self.readiness_from_parts(parts)

        self.assertEqual("blocked_active_task_closed", readiness.readiness_status)

    def test_missing_fresh_context_required_blocks_readiness(self):
        readiness = self.readiness_from_parts(
            self.parts(),
            fresh_context_required=False,
        )

        self.assertEqual("blocked_no_next_tick_context", readiness.readiness_status)

    def test_missing_teacher_gate_required_blocks_readiness(self):
        readiness = self.readiness_from_parts(
            self.parts(),
            teacher_gate_required=False,
        )

        self.assertEqual("blocked_teacher_gate_missing", readiness.readiness_status)

    def test_missing_manual_trigger_required_blocks_readiness(self):
        readiness = self.readiness_from_parts(
            self.parts(),
            manual_trigger_required=False,
        )

        self.assertEqual("blocked_manual_trigger_missing", readiness.readiness_status)

    def test_missing_third_tick_dry_run_required_blocks_readiness(self):
        readiness = self.readiness_from_parts(
            self.parts(),
            third_tick_dry_run_required=False,
        )

        self.assertEqual("blocked_teacher_gate_missing", readiness.readiness_status)

    def test_missing_third_tick_audit_required_blocks_readiness(self):
        readiness = self.readiness_from_parts(
            self.parts(),
            third_tick_audit_required=False,
        )

        self.assertEqual("blocked_teacher_gate_missing", readiness.readiness_status)

    def test_third_tick_created_true_blocks_readiness(self):
        readiness = self.readiness_from_parts(
            self.parts(),
            third_tick_created=True,
        )

        self.assertEqual("blocked_third_tick_already_created", readiness.readiness_status)

    def test_automatic_loop_detected_true_blocks_readiness(self):
        readiness = self.readiness_from_parts(
            self.parts(),
            automatic_loop_detected=True,
        )

        self.assertEqual("blocked_automatic_loop_detected", readiness.readiness_status)

    def test_scheduler_detected_true_blocks_readiness(self):
        readiness = self.readiness_from_parts(
            self.parts(),
            scheduler_detected=True,
        )

        self.assertEqual("blocked_automatic_loop_detected", readiness.readiness_status)

    def test_free_action_selection_detected_true_blocks_readiness(self):
        readiness = self.readiness_from_parts(
            self.parts(),
            free_action_selection_detected=True,
        )

        self.assertEqual("blocked_action_execution_detected", readiness.readiness_status)

    def test_action_execution_detected_true_blocks_readiness(self):
        readiness = self.readiness_from_parts(
            self.parts(),
            action_execution_detected=True,
        )

        self.assertEqual("blocked_action_execution_detected", readiness.readiness_status)

    def test_direct_memory_promotion_detected_true_blocks_readiness(self):
        readiness = self.readiness_from_parts(
            self.parts(),
            direct_memory_promotion_detected=True,
        )

        self.assertEqual(
            "blocked_direct_memory_promotion_detected",
            readiness.readiness_status,
        )

    def test_unity_voice_bridge_detected_true_blocks_readiness(self):
        readiness = self.readiness_from_parts(
            self.parts(),
            unity_voice_bridge_detected=True,
        )

        self.assertEqual("blocked_action_execution_detected", readiness.readiness_status)

    def test_cli_run_readiness_creates_readiness_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = json.loads(self.run_cli(Path(temp_dir), "run-readiness").stdout)

            self.assertTrue(payload["third_tick_readiness_record_created"])
            self.assertEqual(READY_STATUS, payload["readiness_status"])
            self.assertFalse(payload["third_tick_created"])

    def test_cli_blocked_closed_task_demo_returns_blocked_active_task_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = json.loads(
                self.run_cli(Path(temp_dir), "run-closed-task-blocked-demo").stdout
            )

            self.assertEqual("blocked_active_task_closed", payload["readiness_status"])
            self.assertFalse(payload["active_task_can_continue"])

    def test_cli_show_last_readiness_returns_latest_readiness(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            run_payload = json.loads(self.run_cli(data_dir, "run-readiness").stdout)
            last_payload = json.loads(self.run_cli(data_dir, "show-last-readiness").stdout)

            self.assertEqual(run_payload["readiness"]["readiness_id"], last_payload["readiness_id"])

    def test_cli_list_readiness_returns_created_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            run_third_tick_readiness_from_task_working_memory(data_dir)
            run_closed_task_blocked_third_tick_readiness_demo(data_dir)

            payload = json.loads(self.run_cli(data_dir, "list-readiness").stdout)

            self.assertEqual(2, payload["third_tick_readiness_count"])

    def test_show_missing_readiness_returns_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "show-last-readiness", check=False)

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_save_load_helpers_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            result = run_third_tick_readiness_from_task_working_memory(data_dir)

            self.assertEqual(
                result["readiness"],
                load_last_third_tick_readiness_from_task_working_memory(data_dir),
            )
            self.assertEqual(
                1,
                list_third_tick_readiness_from_task_working_memory(data_dir)[
                    "third_tick_readiness_count"
                ],
            )

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
