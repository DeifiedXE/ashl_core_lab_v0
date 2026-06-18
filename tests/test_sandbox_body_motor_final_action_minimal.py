import copy
import unittest

from ashl_core.sandbox_body_motor_final_action_approval_boundary_minimal import (
    run_sandbox_body_motor_final_action_approval_boundary_minimal_check,
)
from ashl_core.sandbox_body_motor_final_action_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_body_motor_final_action_record,
    run_sandbox_body_motor_final_action_minimal_check,
    validate_sandbox_body_motor_final_action_record,
)
from ashl_core.teaching_cli import run_command


class SandboxBodyMotorFinalActionMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_body_motor_final_action_approval_boundary_minimal_check()["valid_records"]

    def test_valid_final_action_record_is_created(self):
        record = build_sandbox_body_motor_final_action_record(self.sources[0])
        result = validate_sandbox_body_motor_final_action_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "sandbox_body_motor_final_action_minimal")
        self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_step_forward_creates_sandbox_final_action(self):
        record = build_sandbox_body_motor_final_action_record(self.sources[0])
        final_action = record["final_action_result"]

        self.assertTrue(final_action["final_action_created"])
        self.assertEqual(final_action["final_action"], "step_forward")
        self.assertEqual(final_action["final_action_scope"], "sandbox_only")
        self.assertEqual(final_action["final_action_source"], "body_motor_selected_action_approval_boundary")

    def test_reach_front_creates_sandbox_final_action(self):
        record = build_sandbox_body_motor_final_action_record(self.sources[2])
        final_action = record["final_action_result"]

        self.assertTrue(final_action["final_action_created"])
        self.assertEqual(final_action["final_action"], "reach_front")
        self.assertEqual(final_action["final_action_scope"], "sandbox_only")

    def test_wall_no_approval_blocks_final_action(self):
        record = build_sandbox_body_motor_final_action_record(self.sources[1])
        final_action = record["final_action_result"]

        self.assertFalse(final_action["final_action_created"])
        self.assertIsNone(final_action["final_action"])
        self.assertEqual(final_action["blocked_reason"], "final_action_not_approved")

    def test_final_action_does_not_create_command_or_execution(self):
        record = build_sandbox_body_motor_final_action_record(self.sources[0])
        final_action = record["final_action_result"]

        self.assertFalse(final_action["direct_command_created"])
        self.assertFalse(final_action["motor_action_executed"])
        self.assertTrue(final_action["future_direct_command_requires_separate_boundary"])
        self.assertTrue(final_action["audit_recorded"])
        self.assertTrue(final_action["rollback_available"])

    def test_source_not_validated_blocks(self):
        record = build_sandbox_body_motor_final_action_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["source_final_action_approval_boundary"]["source_validated"] = False

        result = validate_sandbox_body_motor_final_action_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_final_action_approval_boundary_not_validated", result["error_codes"])

    def test_source_bad_action_blocks(self):
        record = build_sandbox_body_motor_final_action_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["source_final_action_approval_boundary"]["selected_action"] = "jump"

        result = validate_sandbox_body_motor_final_action_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_final_action_approval_boundary_selected_action_invalid", result["error_codes"])

    def test_missing_final_action_blocks(self):
        record = build_sandbox_body_motor_final_action_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["final_action_result"]["final_action_created"] = False

        result = validate_sandbox_body_motor_final_action_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("final_action_result_final_action_created_not_expected", result["error_codes"])

    def test_wrong_final_action_blocks(self):
        record = build_sandbox_body_motor_final_action_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["final_action_result"]["final_action"] = "reach_front"

        result = validate_sandbox_body_motor_final_action_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("final_action_result_final_action_not_expected", result["error_codes"])

    def test_invalid_final_action_blocks(self):
        record = build_sandbox_body_motor_final_action_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["final_action_result"]["final_action"] = "jump"

        result = validate_sandbox_body_motor_final_action_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("final_action_result_final_action_invalid", result["error_codes"])

    def test_wrong_scope_blocks(self):
        record = build_sandbox_body_motor_final_action_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["final_action_result"]["final_action_scope"] = "production"

        result = validate_sandbox_body_motor_final_action_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("final_action_result_final_action_scope_not_expected", result["error_codes"])

    def test_direct_command_created_blocks(self):
        record = build_sandbox_body_motor_final_action_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["final_action_result"]["direct_command_created"] = True

        result = validate_sandbox_body_motor_final_action_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("final_action_result_direct_command_created_not_expected", result["error_codes"])
        self.assertIn("final_action_result_direct_command_created_not_false", result["error_codes"])

    def test_motor_action_executed_blocks(self):
        record = build_sandbox_body_motor_final_action_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["final_action_result"]["motor_action_executed"] = True

        result = validate_sandbox_body_motor_final_action_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("final_action_result_motor_action_executed_not_expected", result["error_codes"])

    def test_blocked_flags_true_block(self):
        record = build_sandbox_body_motor_final_action_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["blocked_flags"]["predictor_mutation_performed"] = True

        result = validate_sandbox_body_motor_final_action_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_predictor_mutation_performed_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_sandbox_body_motor_final_action_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["final_action_result_count"], 29)
        self.assertEqual(summary["valid_final_action_count"], 3)
        self.assertEqual(summary["invalid_final_action_count"], 26)
        self.assertEqual(summary["approval_checked_count"], 2)
        self.assertEqual(summary["approval_blocked_count"], 1)
        self.assertEqual(summary["final_action_created_count"], 2)
        self.assertEqual(summary["final_action_blocked_count"], 1)
        self.assertEqual(summary["step_forward_final_action_count"], 1)
        self.assertEqual(summary["reach_front_final_action_count"], 1)
        self.assertEqual(summary["direct_command_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-sandbox-body-motor-final-action-minimal-check")

        self.assertEqual(result["command"], "run-sandbox-body-motor-final-action-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
