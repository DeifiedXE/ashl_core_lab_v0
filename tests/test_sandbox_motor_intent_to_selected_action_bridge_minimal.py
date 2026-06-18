import copy
import unittest

from ashl_core.sandbox_motor_intent_preview_minimal import run_sandbox_motor_intent_preview_minimal_check
from ashl_core.sandbox_motor_intent_to_selected_action_bridge_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_motor_intent_to_selected_action_bridge_record,
    run_sandbox_motor_intent_to_selected_action_bridge_minimal_check,
    validate_sandbox_motor_intent_to_selected_action_bridge_record,
)
from ashl_core.teaching_cli import run_command


class SandboxMotorIntentToSelectedActionBridgeMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_motor_intent_preview_minimal_check()["valid_records"]

    def test_valid_bridge_record_is_created(self):
        record = build_sandbox_motor_intent_to_selected_action_bridge_record(self.sources[0])
        result = validate_sandbox_motor_intent_to_selected_action_bridge_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "sandbox_motor_intent_to_selected_action_bridge_minimal")
        self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_step_forward_intent_creates_sandbox_selected_action(self):
        record = build_sandbox_motor_intent_to_selected_action_bridge_record(self.sources[0])
        selected = record["selected_action_bridge_result"]

        self.assertTrue(selected["selected_action_created"])
        self.assertEqual(selected["selected_action"], "step_forward")
        self.assertEqual(selected["selected_action_scope"], "sandbox_only")
        self.assertEqual(selected["selected_action_source"], "sandbox_selected_motor_intent_preview")

    def test_reach_front_intent_creates_sandbox_selected_action(self):
        record = build_sandbox_motor_intent_to_selected_action_bridge_record(self.sources[2])
        selected = record["selected_action_bridge_result"]

        self.assertTrue(selected["selected_action_created"])
        self.assertEqual(selected["selected_action"], "reach_front")
        self.assertEqual(selected["selected_action_scope"], "sandbox_only")

    def test_wall_no_intent_blocks_selected_action(self):
        record = build_sandbox_motor_intent_to_selected_action_bridge_record(self.sources[1])
        selected = record["selected_action_bridge_result"]

        self.assertFalse(selected["selected_action_created"])
        self.assertIsNone(selected["selected_action"])
        self.assertEqual(selected["blocked_reason"], "no_selected_motor_intent")

    def test_bridge_does_not_create_downstream_action_outputs(self):
        record = build_sandbox_motor_intent_to_selected_action_bridge_record(self.sources[0])
        selected = record["selected_action_bridge_result"]

        self.assertFalse(selected["final_action_created"])
        self.assertFalse(selected["direct_command_created"])
        self.assertFalse(selected["motor_action_executed"])
        self.assertTrue(selected["rollback_available"])
        self.assertTrue(selected["audit_recorded"])

    def test_invalid_source_blocks(self):
        record = build_sandbox_motor_intent_to_selected_action_bridge_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["source_motor_intent_preview"]["source_validated"] = False

        result = validate_sandbox_motor_intent_to_selected_action_bridge_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_motor_intent_preview_not_validated", result["error_codes"])

    def test_missing_selected_action_blocks(self):
        record = build_sandbox_motor_intent_to_selected_action_bridge_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["selected_action_bridge_result"]["selected_action_created"] = False

        result = validate_sandbox_motor_intent_to_selected_action_bridge_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("selected_action_bridge_result_selected_action_created_not_expected", result["error_codes"])

    def test_wrong_selected_action_blocks(self):
        record = build_sandbox_motor_intent_to_selected_action_bridge_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["selected_action_bridge_result"]["selected_action"] = "reach_front"

        result = validate_sandbox_motor_intent_to_selected_action_bridge_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("selected_action_bridge_result_selected_action_not_expected", result["error_codes"])

    def test_invalid_selected_action_blocks(self):
        record = build_sandbox_motor_intent_to_selected_action_bridge_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["selected_action_bridge_result"]["selected_action"] = "jump"

        result = validate_sandbox_motor_intent_to_selected_action_bridge_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("selected_action_bridge_result_selected_action_invalid", result["error_codes"])

    def test_wrong_scope_blocks(self):
        record = build_sandbox_motor_intent_to_selected_action_bridge_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["selected_action_bridge_result"]["selected_action_scope"] = "production"

        result = validate_sandbox_motor_intent_to_selected_action_bridge_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("selected_action_bridge_result_selected_action_scope_not_expected", result["error_codes"])

    def test_final_action_blocks(self):
        record = build_sandbox_motor_intent_to_selected_action_bridge_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["selected_action_bridge_result"]["final_action_created"] = True

        result = validate_sandbox_motor_intent_to_selected_action_bridge_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("selected_action_bridge_result_final_action_created_not_expected", result["error_codes"])
        self.assertIn("selected_action_bridge_result_final_action_created_not_false", result["error_codes"])

    def test_direct_command_blocks(self):
        record = build_sandbox_motor_intent_to_selected_action_bridge_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["selected_action_bridge_result"]["direct_command_created"] = True

        result = validate_sandbox_motor_intent_to_selected_action_bridge_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("selected_action_bridge_result_direct_command_created_not_expected", result["error_codes"])

    def test_motor_execution_blocks(self):
        record = build_sandbox_motor_intent_to_selected_action_bridge_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["selected_action_bridge_result"]["motor_action_executed"] = True

        result = validate_sandbox_motor_intent_to_selected_action_bridge_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("selected_action_bridge_result_motor_action_executed_not_expected", result["error_codes"])

    def test_blocked_flags_true_block(self):
        record = build_sandbox_motor_intent_to_selected_action_bridge_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["blocked_flags"]["predictor_mutation_performed"] = True

        result = validate_sandbox_motor_intent_to_selected_action_bridge_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_predictor_mutation_performed_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_sandbox_motor_intent_to_selected_action_bridge_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["selected_action_bridge_result_count"], 29)
        self.assertEqual(summary["valid_selected_action_bridge_count"], 3)
        self.assertEqual(summary["invalid_selected_action_bridge_count"], 26)
        self.assertEqual(summary["selected_action_created_count"], 2)
        self.assertEqual(summary["selected_action_blocked_count"], 1)
        self.assertEqual(summary["step_forward_selected_count"], 1)
        self.assertEqual(summary["reach_front_selected_count"], 1)
        self.assertEqual(summary["direct_command_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-sandbox-motor-intent-to-selected-action-bridge-minimal-check")

        self.assertEqual(result["command"], "run-sandbox-motor-intent-to-selected-action-bridge-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
