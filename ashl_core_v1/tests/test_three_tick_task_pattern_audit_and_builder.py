import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.memory.task_working_memory_lifecycle import create_active_task_frame
from ashl_core_v1.runtime.manual_teacher_gated_tick_builder import (
    build_manual_teacher_gated_task_tick,
)
from ashl_core_v1.runtime.three_tick_task_pattern_audit import (
    build_manual_teacher_gated_tick_builder_demo,
    build_three_tick_task_pattern_audit,
    build_three_tick_task_pattern_fixture,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.runtime.three_tick_task_pattern_audit_cli"


class ThreeTickTaskPatternAuditAndBuilderTests(unittest.TestCase):
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

    def fixture(self) -> dict:
        return build_three_tick_task_pattern_fixture()

    def audit(self, fixture: dict) -> dict:
        return build_three_tick_task_pattern_audit(
            fixture.get("tick_records"),
            fixture.get("working_memory_updates"),
        )

    def test_valid_three_tick_pattern_passes(self):
        audit = self.audit(self.fixture())

        self.assertEqual("passed", audit["pattern_status"])
        self.assertTrue(audit["same_task_id_preserved"])
        self.assertTrue(audit["tick3_reads_tick2_working_memory_update"])

    def test_missing_tick1_blocks(self):
        audit = build_three_tick_task_pattern_audit([], [])

        self.assertEqual("blocked_missing_tick1", audit["pattern_status"])

    def test_missing_tick2_blocks(self):
        fixture = self.fixture()
        audit = build_three_tick_task_pattern_audit(
            fixture["tick_records"][:1],
            fixture["working_memory_updates"][:1],
        )

        self.assertEqual("blocked_missing_tick2", audit["pattern_status"])

    def test_missing_tick3_blocks(self):
        fixture = self.fixture()
        audit = build_three_tick_task_pattern_audit(
            fixture["tick_records"][:2],
            fixture["working_memory_updates"][:2],
        )

        self.assertEqual("blocked_missing_tick3", audit["pattern_status"])

    def test_task_id_mismatch_blocks(self):
        fixture = self.fixture()
        fixture["tick_records"][2]["task_id"] = "other_task"

        audit = self.audit(fixture)

        self.assertEqual("blocked_task_id_mismatch", audit["pattern_status"])

    def test_tick3_not_reading_tick2_working_memory_blocks(self):
        fixture = self.fixture()
        fixture["tick_records"][2]["previous_working_memory_update_id"] = "wrong"

        audit = self.audit(fixture)

        self.assertEqual(
            "blocked_tick3_not_reading_tick2_working_memory",
            audit["pattern_status"],
        )

    def test_missing_teacher_gate_blocks(self):
        fixture = self.fixture()
        fixture["tick_records"][1]["teacher_gate_preserved"] = False

        audit = self.audit(fixture)

        self.assertEqual("blocked_teacher_gate_missing", audit["pattern_status"])

    def test_automatic_loop_flag_blocks(self):
        fixture = self.fixture()
        fixture["tick_records"][1]["automatic_loop_created"] = True

        audit = self.audit(fixture)

        self.assertEqual("blocked_automatic_loop_detected", audit["pattern_status"])

    def test_fourth_tick_detected_blocks(self):
        fixture = self.fixture()
        fixture["tick_records"].append(dict(fixture["tick_records"][-1], tick_number=4))

        audit = self.audit(fixture)

        self.assertEqual("blocked_fourth_tick_detected", audit["pattern_status"])

    def test_builder_creates_exactly_one_tick(self):
        demo = build_manual_teacher_gated_tick_builder_demo()

        self.assertTrue(demo["tick_creation_summary"]["created_exactly_one_tick"])

    def test_builder_refuses_recursive_or_auto_loop_mode(self):
        frame = create_active_task_frame("goal", "scope", task_id="task_builder")
        kwargs = dict(
            task_id=frame.task_id,
            active_task_frame=frame,
            previous_tick_stub_record=None,
            previous_working_memory_update=None,
            tick_number=1,
            teacher_gate={"teacher_gate_id": "gate"},
            fresh_context={"fresh_context_id": "context"},
            dry_run_stub={"dry_run_stub_id": "dry"},
            audit_stub={"audit_stub_id": "audit"},
            outcome_label="blocked",
            next_hint="observe",
        )

        with self.assertRaises(ValueError):
            build_manual_teacher_gated_task_tick(**kwargs, recursive_call_requested=True)
        with self.assertRaises(ValueError):
            build_manual_teacher_gated_task_tick(**kwargs, automatic_loop_requested=True)

    def test_builder_preserves_task_id_and_emits_working_memory_update(self):
        demo = build_manual_teacher_gated_tick_builder_demo()
        tick = demo["manual_teacher_gated_tick_stub_record"]
        update = demo["task_working_memory_tick_update"]

        self.assertEqual("builder_demo_task", tick["task_id"])
        self.assertEqual(tick["task_working_memory_update_id"], update["task_working_memory_tick_update_id"])

    def test_cli_run_audit_works(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = json.loads(self.run_cli(Path(temp_dir), "run-audit").stdout)

            self.assertEqual("passed", payload["three_tick_task_pattern_audit"]["pattern_status"])

    def test_cli_run_builder_demo_works(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = json.loads(self.run_cli(Path(temp_dir), "run-builder-demo").stdout)

            self.assertTrue(payload["manual_teacher_gated_tick_builder_demo_created"])

    def test_cli_show_last_audit_works(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.run_cli(data_dir, "run-audit")
            payload = json.loads(self.run_cli(data_dir, "show-last-audit").stdout)

            self.assertIn("three_tick_task_pattern_audit", payload)

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
