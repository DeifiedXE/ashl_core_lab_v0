import copy
import unittest

from ashl_core.sandbox_body_motor_final_action_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_body_motor_final_action_approval_boundary_record,
    run_sandbox_body_motor_final_action_approval_boundary_minimal_check,
    validate_sandbox_body_motor_final_action_approval_boundary_record,
)
from ashl_core.sandbox_motor_intent_to_selected_action_bridge_minimal import (
    run_sandbox_motor_intent_to_selected_action_bridge_minimal_check,
)
from ashl_core.teaching_cli import run_command


class SandboxBodyMotorFinalActionApprovalBoundaryMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_motor_intent_to_selected_action_bridge_minimal_check()["valid_records"]

    def test_valid_approval_boundary_record_is_created(self):
        record = build_sandbox_body_motor_final_action_approval_boundary_record(self.sources[0])
        result = validate_sandbox_body_motor_final_action_approval_boundary_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "sandbox_body_motor_final_action_approval_boundary_minimal")
        self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_step_forward_selected_action_is_allowed_for_future_final_action(self):
        record = build_sandbox_body_motor_final_action_approval_boundary_record(self.sources[0])
        boundary = record["final_action_approval_boundary"]

        self.assertEqual(boundary["selected_action"], "step_forward")
        self.assertTrue(boundary["final_action_allowed_in_future_package"])
        self.assertEqual(boundary["allowed_next_package"], "Sandbox Body-Motor Final Action Minimal v0")

    def test_reach_front_selected_action_is_allowed_for_future_final_action(self):
        record = build_sandbox_body_motor_final_action_approval_boundary_record(self.sources[2])
        boundary = record["final_action_approval_boundary"]

        self.assertEqual(boundary["selected_action"], "reach_front")
        self.assertTrue(boundary["final_action_allowed_in_future_package"])

    def test_no_selected_action_blocks_future_final_action(self):
        record = build_sandbox_body_motor_final_action_approval_boundary_record(self.sources[1])
        boundary = record["final_action_approval_boundary"]

        self.assertFalse(boundary["final_action_allowed_in_future_package"])
        self.assertIsNone(boundary["selected_action"])
        self.assertEqual(boundary["blocked_reason"], "no_selected_action_for_final_action")

    def test_boundary_does_not_create_final_action_or_downstream_outputs(self):
        record = build_sandbox_body_motor_final_action_approval_boundary_record(self.sources[0])
        boundary = record["final_action_approval_boundary"]

        self.assertFalse(boundary["implementation_in_this_package"])
        self.assertFalse(boundary["final_action_created"])
        self.assertFalse(boundary["direct_command_created"])
        self.assertFalse(boundary["motor_action_executed"])

    def test_source_not_validated_blocks(self):
        record = build_sandbox_body_motor_final_action_approval_boundary_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["source_selected_action_bridge"]["source_validated"] = False

        result = validate_sandbox_body_motor_final_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_selected_action_bridge_not_validated", result["error_codes"])

    def test_bad_source_action_blocks(self):
        record = build_sandbox_body_motor_final_action_approval_boundary_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["source_selected_action_bridge"]["selected_action"] = "jump"

        result = validate_sandbox_body_motor_final_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_selected_action_bridge_selected_action_invalid", result["error_codes"])

    def test_wrong_scope_blocks(self):
        record = build_sandbox_body_motor_final_action_approval_boundary_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["source_selected_action_bridge"]["selected_action_scope"] = "production"

        result = validate_sandbox_body_motor_final_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_selected_action_bridge_scope_not_sandbox_only", result["error_codes"])

    def test_allowed_false_blocks(self):
        record = build_sandbox_body_motor_final_action_approval_boundary_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["final_action_approval_boundary"]["final_action_allowed_in_future_package"] = False

        result = validate_sandbox_body_motor_final_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "final_action_approval_boundary_final_action_allowed_in_future_package_not_expected",
            result["error_codes"],
        )

    def test_final_action_created_blocks(self):
        record = build_sandbox_body_motor_final_action_approval_boundary_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["final_action_approval_boundary"]["final_action_created"] = True

        result = validate_sandbox_body_motor_final_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("final_action_approval_boundary_final_action_created_not_expected", result["error_codes"])
        self.assertIn("final_action_approval_boundary_final_action_created_not_false", result["error_codes"])

    def test_direct_command_created_blocks(self):
        record = build_sandbox_body_motor_final_action_approval_boundary_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["final_action_approval_boundary"]["direct_command_created"] = True

        result = validate_sandbox_body_motor_final_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("final_action_approval_boundary_direct_command_created_not_expected", result["error_codes"])

    def test_motor_action_executed_blocks(self):
        record = build_sandbox_body_motor_final_action_approval_boundary_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["final_action_approval_boundary"]["motor_action_executed"] = True

        result = validate_sandbox_body_motor_final_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("final_action_approval_boundary_motor_action_executed_not_expected", result["error_codes"])

    def test_blocked_flags_true_block(self):
        record = build_sandbox_body_motor_final_action_approval_boundary_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["blocked_flags"]["predictor_mutation_performed"] = True

        result = validate_sandbox_body_motor_final_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_predictor_mutation_performed_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_sandbox_body_motor_final_action_approval_boundary_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["final_action_approval_boundary_result_count"], 31)
        self.assertEqual(summary["valid_final_action_approval_boundary_count"], 3)
        self.assertEqual(summary["invalid_final_action_approval_boundary_count"], 28)
        self.assertEqual(summary["future_final_action_allowed_count"], 2)
        self.assertEqual(summary["future_final_action_blocked_count"], 1)
        self.assertEqual(summary["step_forward_allowed_count"], 1)
        self.assertEqual(summary["reach_front_allowed_count"], 1)
        self.assertEqual(summary["final_action_blocked_count"], 3)
        self.assertEqual(summary["direct_command_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-sandbox-body-motor-final-action-approval-boundary-minimal-check")

        self.assertEqual(result["command"], "run-sandbox-body-motor-final-action-approval-boundary-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
