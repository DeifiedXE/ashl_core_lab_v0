import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.teacher_gated_third_tick_runtime_stub import (
    build_teacher_gated_third_tick_runtime_stub,
    list_third_tick_stub_records,
    load_last_third_tick_stub_record,
    run_blocked_third_tick_runtime_stub_demo,
    run_teacher_gated_third_tick_runtime_stub,
)
from ashl_core_v1.runtime.third_tick_readiness_from_task_working_memory import (
    build_blocked_closed_task_third_tick_readiness_demo,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.runtime.teacher_gated_third_tick_runtime_stub_cli"


class TeacherGatedThirdTickRuntimeStubTests(unittest.TestCase):
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

    def payload(self) -> dict:
        return build_teacher_gated_third_tick_runtime_stub()

    def test_readiness_passed_can_create_third_tick(self):
        payload = self.payload()

        self.assertTrue(payload["third_tick_runtime_stub_created"])
        self.assertTrue(payload["third_tick_created"])

    def test_readiness_blocked_cannot_create_third_tick(self):
        payload = build_teacher_gated_third_tick_runtime_stub(
            build_blocked_closed_task_third_tick_readiness_demo()
        )

        self.assertFalse(payload["third_tick_runtime_stub_created"])
        self.assertFalse(payload["third_tick_created"])
        self.assertEqual("blocked_by_readiness", payload["third_tick_stub_record"]["third_tick_status"])

    def test_third_tick_links_to_second_tick(self):
        record = self.payload()["third_tick_stub_record"]

        self.assertEqual("tick_2_stub", record["source_second_tick_stub_record_id"])

    def test_third_tick_links_to_active_task_frame(self):
        record = self.payload()["third_tick_stub_record"]

        self.assertTrue(record["active_task_frame_id"].startswith("active_task_frame_"))
        self.assertIn(
            f"active_task_frame:{record['active_task_frame_id']}",
            record["source_trace_refs"],
        )

    def test_third_tick_reads_task_working_memory_update_refs(self):
        record = self.payload()["third_tick_stub_record"]

        self.assertTrue(record["source_task_working_memory_update_refs"])
        self.assertIn(
            "task_working_memory_update:",
            record["source_task_working_memory_update_refs"][0],
        )

    def test_third_tick_preserves_same_task_id(self):
        record = self.payload()["third_tick_stub_record"]

        self.assertEqual("handle_front_obstacle", record["task_id"])

    def test_third_tick_uses_fresh_context_and_teacher_gate(self):
        record = self.payload()["third_tick_stub_record"]

        self.assertTrue(record["fresh_context_used"])
        self.assertTrue(record["teacher_gate_preserved"])
        self.assertTrue(record["manual_trigger"])

    def test_third_tick_creates_working_memory_update(self):
        payload = self.payload()

        self.assertIsNotNone(payload["third_tick_working_memory_update"])
        self.assertEqual(
            payload["third_tick_stub_record"]["active_task_frame_id"],
            payload["third_tick_working_memory_update"]["active_task_frame_id"],
        )

    def test_third_tick_stops_immediately_and_creates_no_next_tick(self):
        record = self.payload()["third_tick_stub_record"]

        self.assertTrue(record["third_tick_stopped"])
        self.assertFalse(record["next_tick_created"])

    def test_no_scheduler_loop_action_or_memory_promotion(self):
        record = self.payload()["third_tick_stub_record"]

        self.assertFalse(record["scheduler_used"])
        self.assertFalse(record["automatic_loop_created"])
        self.assertFalse(record["action_execution_used"])
        self.assertFalse(record["direct_memory_promotion_used"])
        self.assertFalse(record["unity_voice_bridge_used"])

    def test_save_load_and_list_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            payload = run_teacher_gated_third_tick_runtime_stub(data_dir)

            self.assertEqual(payload, load_last_third_tick_stub_record(data_dir))
            self.assertEqual(1, list_third_tick_stub_records(data_dir)["third_tick_stub_record_count"])

    def test_blocked_demo_saves_blocked_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = run_blocked_third_tick_runtime_stub_demo(Path(temp_dir))

            self.assertFalse(payload["third_tick_created"])

    def test_cli_run_third_tick_works(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = json.loads(self.run_cli(Path(temp_dir), "run-third-tick").stdout)

            self.assertTrue(payload["third_tick_created"])

    def test_cli_show_last_third_tick_works(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            run_payload = json.loads(self.run_cli(data_dir, "run-third-tick").stdout)
            last_payload = json.loads(self.run_cli(data_dir, "show-last-third-tick").stdout)

            self.assertEqual(run_payload["third_tick_stub_record_id"], last_payload["third_tick_stub_record_id"])

    def test_cli_list_third_ticks_works(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.run_cli(data_dir, "run-third-tick")
            payload = json.loads(self.run_cli(data_dir, "list-third-ticks").stdout)

            self.assertEqual(1, payload["third_tick_stub_record_count"])

    def test_cli_show_missing_returns_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "show-last-third-tick", check=False)

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
