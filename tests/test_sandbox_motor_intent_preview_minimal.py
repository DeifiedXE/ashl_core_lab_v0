import copy
import unittest

from ashl_core.minimal_body_schema_affordance_consistency_runtime import (
    run_minimal_body_schema_affordance_consistency_runtime_check,
)
from ashl_core.sandbox_motor_intent_preview_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_motor_intent_preview_record,
    run_sandbox_motor_intent_preview_minimal_check,
    validate_sandbox_motor_intent_preview_record,
)
from ashl_core.teaching_cli import run_command


class SandboxMotorIntentPreviewMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_minimal_body_schema_affordance_consistency_runtime_check()["valid_records"]

    def test_valid_motor_intent_preview_is_created(self):
        record = build_sandbox_motor_intent_preview_record(self.sources[0])
        result = validate_sandbox_motor_intent_preview_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "sandbox_motor_intent_preview_minimal")
        self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_empty_front_creates_step_forward_motor_intent(self):
        record = build_sandbox_motor_intent_preview_record(self.sources[0])
        preview = record["motor_intent_preview"]

        self.assertTrue(preview["selected_motor_intent_created"])
        self.assertEqual(preview["selected_motor_intent"], "step_forward")
        self.assertEqual(preview["intent_source_decision"], "empty_front_step_forward")

    def test_wall_front_creates_no_motor_intent(self):
        record = build_sandbox_motor_intent_preview_record(self.sources[1])
        preview = record["motor_intent_preview"]

        self.assertFalse(preview["selected_motor_intent_created"])
        self.assertIsNone(preview["selected_motor_intent"])
        self.assertEqual(preview["blocked_reason"], "front_blocked_by_affordance")

    def test_item_front_prioritizes_reach_front(self):
        record = build_sandbox_motor_intent_preview_record(self.sources[2])
        preview = record["motor_intent_preview"]

        self.assertTrue(preview["selected_motor_intent_created"])
        self.assertEqual(preview["selected_motor_intent"], "reach_front")
        self.assertEqual(preview["intent_source_decision"], "item_front_reach_front")

    def test_preview_does_not_create_action_outputs(self):
        record = build_sandbox_motor_intent_preview_record(self.sources[0])
        preview = record["motor_intent_preview"]

        self.assertFalse(preview["selected_action_created"])
        self.assertFalse(preview["final_action_created"])
        self.assertFalse(preview["direct_command_created"])
        self.assertFalse(preview["motor_action_executed"])
        self.assertTrue(preview["preview_only"])

    def test_invalid_source_consistency_blocks(self):
        record = build_sandbox_motor_intent_preview_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["source_body_schema_readiness"]["body_schema_consistent"] = False

        result = validate_sandbox_motor_intent_preview_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_body_schema_readiness_not_consistent", result["error_codes"])

    def test_wrong_intent_blocks(self):
        record = build_sandbox_motor_intent_preview_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["motor_intent_preview"]["selected_motor_intent"] = "reach_front"

        result = validate_sandbox_motor_intent_preview_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("motor_intent_preview_selected_motor_intent_not_expected", result["error_codes"])

    def test_invalid_intent_value_blocks(self):
        record = build_sandbox_motor_intent_preview_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["motor_intent_preview"]["selected_motor_intent"] = "jump"

        result = validate_sandbox_motor_intent_preview_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("motor_intent_preview_selected_motor_intent_invalid", result["error_codes"])

    def test_selected_action_blocks(self):
        record = build_sandbox_motor_intent_preview_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["motor_intent_preview"]["selected_action_created"] = True

        result = validate_sandbox_motor_intent_preview_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("motor_intent_preview_selected_action_created_not_expected", result["error_codes"])
        self.assertIn("motor_intent_preview_selected_action_created_not_false", result["error_codes"])

    def test_final_action_blocks(self):
        record = build_sandbox_motor_intent_preview_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["motor_intent_preview"]["final_action_created"] = True

        result = validate_sandbox_motor_intent_preview_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("motor_intent_preview_final_action_created_not_expected", result["error_codes"])

    def test_direct_command_blocks(self):
        record = build_sandbox_motor_intent_preview_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["motor_intent_preview"]["direct_command_created"] = True

        result = validate_sandbox_motor_intent_preview_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("motor_intent_preview_direct_command_created_not_expected", result["error_codes"])

    def test_motor_execution_blocks(self):
        record = build_sandbox_motor_intent_preview_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["motor_intent_preview"]["motor_action_executed"] = True

        result = validate_sandbox_motor_intent_preview_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("motor_intent_preview_motor_action_executed_not_expected", result["error_codes"])

    def test_blocked_flags_true_block(self):
        record = build_sandbox_motor_intent_preview_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["blocked_flags"]["predictor_mutation_performed"] = True

        result = validate_sandbox_motor_intent_preview_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_predictor_mutation_performed_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_sandbox_motor_intent_preview_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["motor_intent_preview_result_count"], 29)
        self.assertEqual(summary["valid_motor_intent_preview_count"], 3)
        self.assertEqual(summary["invalid_motor_intent_preview_count"], 26)
        self.assertEqual(summary["selected_motor_intent_created_count"], 2)
        self.assertEqual(summary["no_intent_created_count"], 1)
        self.assertEqual(summary["step_forward_intent_count"], 1)
        self.assertEqual(summary["reach_front_intent_count"], 1)
        self.assertEqual(summary["direct_command_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-sandbox-motor-intent-preview-minimal-check")

        self.assertEqual(result["command"], "run-sandbox-motor-intent-preview-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
