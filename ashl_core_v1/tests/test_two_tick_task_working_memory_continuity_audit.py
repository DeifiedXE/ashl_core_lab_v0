import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.two_tick_task_working_memory_continuity_audit import (
    TwoTickTaskWorkingMemoryContinuityAudit,
    build_two_tick_task_working_memory_continuity_audit,
    build_two_tick_task_working_memory_continuity_audit_demo,
    list_two_tick_task_working_memory_continuity_audits,
    load_last_two_tick_task_working_memory_continuity_audit,
    run_two_tick_task_working_memory_continuity_audit,
    validate_two_tick_task_working_memory_continuity_audit,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.runtime.two_tick_task_working_memory_continuity_audit_cli"


class TwoTickTaskWorkingMemoryContinuityAuditTests(unittest.TestCase):
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
        return build_two_tick_task_working_memory_continuity_audit_demo()

    def audit_from_parts(self, parts: dict) -> TwoTickTaskWorkingMemoryContinuityAudit:
        return build_two_tick_task_working_memory_continuity_audit(
            parts.get("active_task_frame"),
            parts.get("first_tick_stub_record"),
            parts.get("second_tick_stub_record"),
            parts.get("first_tick_working_memory_update"),
            None,
            parts.get("task_closure_record"),
            parts.get("task_working_memory_disposition"),
        )

    def test_valid_two_tick_working_memory_continuity_passes(self):
        audit = self.audit_from_parts(self.parts())

        self.assertEqual("passed", audit.continuity_status)
        self.assertTrue(audit.same_task_id_preserved)
        self.assertTrue(audit.tick2_read_updated_working_memory)
        self.assertTrue(validate_two_tick_task_working_memory_continuity_audit(audit)["valid"])

    def test_missing_active_task_frame_blocks_audit(self):
        parts = self.parts()
        parts["active_task_frame"] = None

        audit = self.audit_from_parts(parts)

        self.assertEqual("blocked_missing_task_frame", audit.continuity_status)

    def test_active_task_frame_with_non_working_memory_layer_blocks_audit(self):
        parts = self.parts()
        parts["active_task_frame"]["memory_layer"] = "long_term"

        audit = self.audit_from_parts(parts)

        self.assertEqual("blocked_not_working_memory_layer", audit.continuity_status)
        self.assertFalse(audit.working_memory_layer_confirmed)

    def test_missing_first_tick_blocks_audit(self):
        parts = self.parts()
        parts["first_tick_stub_record"] = None

        audit = self.audit_from_parts(parts)

        self.assertEqual("blocked_missing_tick1", audit.continuity_status)

    def test_missing_second_tick_blocks_audit(self):
        parts = self.parts()
        parts["second_tick_stub_record"] = None

        audit = self.audit_from_parts(parts)

        self.assertEqual("blocked_missing_tick2", audit.continuity_status)

    def test_task_id_mismatch_blocks_audit(self):
        parts = self.parts()
        parts["second_tick_stub_record"]["source_active_task_frame_id"] = "other_frame"
        parts["second_tick_stub_record"]["trace_refs"] = ["task:other_task"]

        audit = self.audit_from_parts(parts)

        self.assertEqual("blocked_task_id_mismatch", audit.continuity_status)
        self.assertFalse(audit.same_task_id_preserved)

    def test_missing_tick1_working_memory_update_blocks_audit(self):
        parts = self.parts()
        parts["first_tick_working_memory_update"] = None

        audit = self.audit_from_parts(parts)

        self.assertEqual("blocked_missing_tick1_update", audit.continuity_status)

    def test_tick2_not_linked_to_updated_working_memory_blocks_audit(self):
        parts = self.parts()
        second = parts["second_tick_stub_record"]
        second.pop("source_task_working_memory_update_refs", None)
        second["trace_refs"] = [
            ref for ref in second["trace_refs"] if not ref.startswith("task_working_memory_update:")
        ]

        audit = self.audit_from_parts(parts)

        self.assertEqual(
            "blocked_missing_tick2_working_memory_read",
            audit.continuity_status,
        )
        self.assertFalse(audit.tick2_read_updated_working_memory)

    def test_tick2_ignoring_tick1_outcome_blocks_audit(self):
        parts = self.parts()
        second = parts["second_tick_stub_record"]
        second["second_tick_summary"] = "tick 2 read task hint"
        second["previous_tick_summary"] = "previous summary unavailable"
        second["trace_refs"] = [
            ref for ref in second["trace_refs"] if not ref.startswith("outcome:")
        ]

        audit = self.audit_from_parts(parts)

        self.assertEqual("blocked_tick2_ignores_tick1_outcome", audit.continuity_status)
        self.assertFalse(audit.tick2_uses_tick1_outcome)

    def test_tick2_ignoring_tick1_candidate_hint_blocks_audit(self):
        parts = self.parts()
        second = parts["second_tick_stub_record"]
        second["second_tick_summary"] = "tick 2 read blocked outcome"
        second["trace_refs"] = [
            ref for ref in second["trace_refs"] if not ref.startswith("hint:")
        ]

        audit = self.audit_from_parts(parts)

        self.assertEqual(
            "blocked_tick2_ignores_working_memory_hint",
            audit.continuity_status,
        )
        self.assertFalse(audit.tick2_uses_tick1_candidate_hint)

    def test_missing_teacher_gate_blocks_audit(self):
        parts = self.parts()
        parts["second_tick_stub_record"]["teacher_gate_status"] = "blocked"

        audit = self.audit_from_parts(parts)

        self.assertEqual("blocked_teacher_gate_missing", audit.continuity_status)

    def test_second_tick_not_stopped_blocks_audit(self):
        parts = self.parts()
        parts["second_tick_stub_record"]["stopped_after_second_tick"] = False

        audit = self.audit_from_parts(parts)

        self.assertEqual("blocked_second_tick_not_stopped", audit.continuity_status)

    def test_third_tick_created_true_blocks_audit(self):
        parts = self.parts()
        parts["second_tick_stub_record"]["third_tick_created"] = True

        audit = self.audit_from_parts(parts)

        self.assertEqual("blocked_third_tick_detected", audit.continuity_status)
        self.assertTrue(audit.third_tick_created)

    def test_automatic_loop_detected_true_blocks_audit(self):
        parts = self.parts()
        parts["second_tick_stub_record"]["continuous_loop_created"] = True

        audit = self.audit_from_parts(parts)

        self.assertEqual("blocked_automatic_loop_detected", audit.continuity_status)
        self.assertTrue(audit.automatic_loop_detected)

    def test_scheduler_detected_true_blocks_audit(self):
        parts = self.parts()
        blocked = parts["second_tick_stub_record"]["preserved_blocked_surfaces"]
        parts["second_tick_stub_record"]["preserved_blocked_surfaces"] = [
            surface for surface in blocked if surface != "background_scheduler"
        ]

        audit = self.audit_from_parts(parts)

        self.assertEqual("blocked_automatic_loop_detected", audit.continuity_status)
        self.assertTrue(audit.scheduler_detected)

    def test_free_action_selection_detected_true_blocks_audit(self):
        parts = self.parts()
        blocked = parts["second_tick_stub_record"]["preserved_blocked_surfaces"]
        parts["second_tick_stub_record"]["preserved_blocked_surfaces"] = [
            surface for surface in blocked if surface != "free_action_selection"
        ]

        audit = self.audit_from_parts(parts)

        self.assertEqual("blocked_automatic_loop_detected", audit.continuity_status)
        self.assertTrue(audit.free_action_selection_detected)

    def test_action_execution_detected_true_blocks_audit(self):
        parts = self.parts()
        blocked = parts["second_tick_stub_record"]["preserved_blocked_surfaces"]
        parts["second_tick_stub_record"]["preserved_blocked_surfaces"] = [
            surface for surface in blocked if surface != "action_execution"
        ]

        audit = self.audit_from_parts(parts)

        self.assertEqual("blocked_action_execution_detected", audit.continuity_status)
        self.assertTrue(audit.action_execution_detected)

    def test_direct_memory_promotion_detected_true_blocks_audit(self):
        parts = self.parts()
        parts["task_working_memory_disposition"]["learning_digest_candidate_refs"] = [
            "core:direct_write"
        ]

        audit = self.audit_from_parts(parts)

        self.assertEqual(
            "blocked_direct_memory_promotion_detected",
            audit.continuity_status,
        )
        self.assertTrue(audit.direct_memory_promotion_detected)

    def test_unity_voice_bridge_detected_true_blocks_audit(self):
        parts = self.parts()
        parts["second_tick_stub_record"]["voice_output_created"] = True

        audit = self.audit_from_parts(parts)

        self.assertEqual("failed", audit.continuity_status)
        self.assertTrue(audit.unity_voice_bridge_detected)

    def test_cli_run_audit_creates_audit_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = json.loads(self.run_cli(Path(temp_dir), "run-audit").stdout)

            self.assertTrue(payload["two_tick_task_working_memory_continuity_audit_created"])
            self.assertEqual("passed", payload["continuity_status"])
            self.assertTrue(payload["tick2_read_updated_working_memory"])

    def test_cli_show_last_audit_returns_latest_audit(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            run_payload = json.loads(self.run_cli(data_dir, "run-audit").stdout)
            last_payload = json.loads(self.run_cli(data_dir, "show-last-audit").stdout)

            self.assertEqual(run_payload["audit"]["audit_id"], last_payload["audit_id"])

    def test_cli_list_audits_returns_created_audits(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            run_two_tick_task_working_memory_continuity_audit(data_dir)
            run_two_tick_task_working_memory_continuity_audit(data_dir)

            payload = json.loads(self.run_cli(data_dir, "list-audits").stdout)

            self.assertEqual(
                2,
                payload["two_tick_task_working_memory_continuity_audit_count"],
            )

    def test_show_missing_audit_returns_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "show-last-audit", check=False)

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_save_load_helpers_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            result = run_two_tick_task_working_memory_continuity_audit(data_dir)

            self.assertEqual(
                result["audit"],
                load_last_two_tick_task_working_memory_continuity_audit(data_dir),
            )
            self.assertEqual(
                1,
                list_two_tick_task_working_memory_continuity_audits(data_dir)[
                    "two_tick_task_working_memory_continuity_audit_count"
                ],
            )

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
