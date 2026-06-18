import copy
import unittest

from ashl_core.body_motor_feedback_gated_next_action_preview_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_body_motor_feedback_gated_next_action_preview_record,
    run_body_motor_feedback_gated_next_action_preview_minimal_check,
    validate_body_motor_feedback_gated_next_action_preview_record,
)
from ashl_core.sandbox_body_motor_execution_feedback_settling_minimal import (
    run_sandbox_body_motor_execution_feedback_settling_minimal_check,
)
from ashl_core.teaching_cli import run_command


class BodyMotorFeedbackGatedNextActionPreviewMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_body_motor_execution_feedback_settling_minimal_check()["valid_records"]

    def test_valid_next_action_preview_record_is_created(self):
        record = build_body_motor_feedback_gated_next_action_preview_record(self.sources[0])
        result = validate_body_motor_feedback_gated_next_action_preview_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "body_motor_feedback_gated_next_action_preview_minimal")
        self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_movement_success_creates_continue_pressure_preview(self):
        record = build_body_motor_feedback_gated_next_action_preview_record(self.sources[0])
        preview = record["candidate_pressure_preview"]

        self.assertTrue(preview["pressure_preview_created"])
        self.assertEqual(preview["source_feedback_label"], "movement_success_feedback")
        self.assertEqual(preview["pressure_target"], "continue_body_motor_exploration")
        self.assertEqual(preview["pressure_delta"], 0.04)
        self.assertTrue(preview["advisory_only"])

    def test_reach_success_creates_item_attention_pressure_preview(self):
        record = build_body_motor_feedback_gated_next_action_preview_record(self.sources[2])
        preview = record["candidate_pressure_preview"]

        self.assertTrue(preview["pressure_preview_created"])
        self.assertEqual(preview["source_feedback_label"], "reach_success_feedback")
        self.assertEqual(preview["pressure_target"], "inspect_or_reach_nearby_item")
        self.assertEqual(preview["pressure_delta"], 0.05)

    def test_wall_case_blocks_pressure_preview(self):
        record = build_body_motor_feedback_gated_next_action_preview_record(self.sources[1])
        preview = record["candidate_pressure_preview"]

        self.assertFalse(preview["pressure_preview_created"])
        self.assertIsNone(preview["pressure_target"])
        self.assertEqual(preview["blocked_reason"], "settled_feedback_not_available_for_next_action_preview")

    def test_candidate_order_is_preserved_without_reordering(self):
        record = build_body_motor_feedback_gated_next_action_preview_record(self.sources[0])
        preview = record["candidate_pressure_preview"]

        self.assertEqual(preview["candidate_order_before_preview"], preview["candidate_order_after_preview"])
        self.assertFalse(preview["candidate_reordering_applied"])

    def test_no_action_or_command_is_created(self):
        record = build_body_motor_feedback_gated_next_action_preview_record(self.sources[0])
        preview = record["candidate_pressure_preview"]

        self.assertFalse(preview["selected_action_created"])
        self.assertFalse(preview["final_action_created"])
        self.assertFalse(preview["direct_command_created"])
        self.assertFalse(preview["motor_execution_created"])

    def test_rollback_restores_candidate_baseline(self):
        record = build_body_motor_feedback_gated_next_action_preview_record(self.sources[0])
        rollback = record["rollback_preview"]

        self.assertTrue(rollback["rollback_available"])
        self.assertTrue(rollback["session_end_restores_baseline"])
        self.assertFalse(rollback["dirty_state_after_rollback"])
        self.assertEqual(rollback["candidate_order_restored"], record["candidate_pressure_preview"]["candidate_order_before_preview"])

    def test_preview_not_created_blocks(self):
        record = build_body_motor_feedback_gated_next_action_preview_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["candidate_pressure_preview"]["pressure_preview_created"] = False

        result = validate_body_motor_feedback_gated_next_action_preview_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("candidate_pressure_preview_pressure_preview_created_not_expected", result["error_codes"])

    def test_candidate_order_change_blocks(self):
        record = build_body_motor_feedback_gated_next_action_preview_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["candidate_pressure_preview"]["candidate_order_after_preview"] = list(reversed(bad["candidate_pressure_preview"]["candidate_order_after_preview"]))

        result = validate_body_motor_feedback_gated_next_action_preview_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("candidate_pressure_preview_candidate_order_after_preview_not_expected", result["error_codes"])

    def test_reordering_applied_blocks(self):
        record = build_body_motor_feedback_gated_next_action_preview_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["candidate_pressure_preview"]["candidate_reordering_applied"] = True

        result = validate_body_motor_feedback_gated_next_action_preview_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("candidate_pressure_preview_candidate_reordering_applied_not_expected", result["error_codes"])

    def test_selected_action_created_blocks(self):
        record = build_body_motor_feedback_gated_next_action_preview_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["candidate_pressure_preview"]["selected_action_created"] = True

        result = validate_body_motor_feedback_gated_next_action_preview_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("candidate_pressure_preview_selected_action_created_not_expected", result["error_codes"])

    def test_direct_command_created_blocks(self):
        record = build_body_motor_feedback_gated_next_action_preview_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["candidate_pressure_preview"]["direct_command_created"] = True

        result = validate_body_motor_feedback_gated_next_action_preview_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("candidate_pressure_preview_direct_command_created_not_expected", result["error_codes"])

    def test_memory_write_blocks(self):
        record = build_body_motor_feedback_gated_next_action_preview_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["blocked_flags"]["memory_write_performed"] = True

        result = validate_body_motor_feedback_gated_next_action_preview_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_memory_write_performed_not_false", result["error_codes"])

    def test_predictor_mutation_blocks(self):
        record = build_body_motor_feedback_gated_next_action_preview_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["blocked_flags"]["predictor_mutation_performed"] = True

        result = validate_body_motor_feedback_gated_next_action_preview_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_predictor_mutation_performed_not_false", result["error_codes"])

    def test_proof_claim_blocks(self):
        record = build_body_motor_feedback_gated_next_action_preview_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["blocked_flags"]["proof_of_learning_claimed"] = True

        result = validate_body_motor_feedback_gated_next_action_preview_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_proof_of_learning_claimed_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_body_motor_feedback_gated_next_action_preview_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["next_action_preview_result_count"], 34)
        self.assertEqual(summary["valid_next_action_preview_count"], 3)
        self.assertEqual(summary["invalid_next_action_preview_count"], 31)
        self.assertEqual(summary["pressure_preview_created_count"], 2)
        self.assertEqual(summary["pressure_preview_blocked_count"], 1)
        self.assertEqual(summary["movement_success_pressure_count"], 1)
        self.assertEqual(summary["reach_success_pressure_count"], 1)
        self.assertEqual(summary["wall_pressure_blocked_count"], 1)
        self.assertEqual(summary["candidate_order_preserved_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-body-motor-feedback-gated-next-action-preview-minimal-check")

        self.assertEqual(result["command"], "run-body-motor-feedback-gated-next-action-preview-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
