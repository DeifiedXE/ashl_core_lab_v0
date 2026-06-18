import copy
import unittest

from ashl_core.body_motor_feedback_gated_candidate_reordering_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record,
    run_body_motor_feedback_gated_candidate_reordering_approval_boundary_minimal_check,
    validate_body_motor_feedback_gated_candidate_reordering_approval_boundary_record,
)
from ashl_core.body_motor_feedback_gated_next_action_preview_minimal import (
    run_body_motor_feedback_gated_next_action_preview_minimal_check,
)
from ashl_core.teaching_cli import run_command


class BodyMotorFeedbackGatedCandidateReorderingApprovalBoundaryMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_body_motor_feedback_gated_next_action_preview_minimal_check()["valid_records"]

    def test_valid_approval_boundary_record_is_created(self):
        record = build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(self.sources[0])
        result = validate_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(
            record["record_type"],
            "body_motor_feedback_gated_candidate_reordering_approval_boundary_minimal",
        )
        self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_movement_pressure_allows_future_reordering_package(self):
        record = build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(self.sources[0])
        boundary = record["candidate_reordering_approval_boundary"]

        self.assertEqual(boundary["pressure_target"], "continue_body_motor_exploration")
        self.assertTrue(boundary["candidate_reordering_allowed_in_future_package"])
        self.assertEqual(
            boundary["allowed_next_package"],
            "Body-Motor Feedback-Gated Candidate Reordering Minimal v0",
        )

    def test_reach_pressure_allows_future_reordering_package(self):
        record = build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(self.sources[2])
        boundary = record["candidate_reordering_approval_boundary"]

        self.assertEqual(boundary["pressure_target"], "inspect_or_reach_nearby_item")
        self.assertTrue(boundary["candidate_reordering_allowed_in_future_package"])

    def test_wall_no_pressure_blocks_future_reordering_package(self):
        record = build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(self.sources[1])
        boundary = record["candidate_reordering_approval_boundary"]

        self.assertFalse(boundary["candidate_reordering_allowed_in_future_package"])
        self.assertIsNone(boundary["pressure_target"])
        self.assertEqual(boundary["blocked_reason"], "no_pressure_preview_for_candidate_reordering")

    def test_boundary_does_not_reorder_or_create_actions(self):
        record = build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(self.sources[0])
        boundary = record["candidate_reordering_approval_boundary"]

        self.assertFalse(boundary["implementation_in_this_package"])
        self.assertFalse(boundary["candidate_reordering_applied"])
        self.assertFalse(boundary["selected_action_created"])
        self.assertFalse(boundary["final_action_created"])
        self.assertFalse(boundary["direct_command_created"])
        self.assertFalse(boundary["motor_execution_created"])

    def test_source_not_validated_blocks(self):
        record = build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["source_next_action_preview"]["source_validated"] = False

        result = validate_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_next_action_preview_not_validated", result["error_codes"])

    def test_wrong_pressure_target_blocks(self):
        record = build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["source_next_action_preview"]["pressure_target"] = "wander"

        result = validate_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_next_action_preview_pressure_target_invalid", result["error_codes"])

    def test_wrong_scope_blocks(self):
        record = build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["source_next_action_preview"]["preview_scope"] = "production"

        result = validate_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_next_action_preview_scope_not_same_session_sandbox_only", result["error_codes"])

    def test_reordering_already_applied_blocks(self):
        record = build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["source_next_action_preview"]["candidate_reordering_applied"] = True

        result = validate_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_next_action_preview_candidate_reordering_already_applied", result["error_codes"])

    def test_allowed_false_blocks(self):
        record = build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["candidate_reordering_approval_boundary"]["candidate_reordering_allowed_in_future_package"] = False

        result = validate_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "candidate_reordering_approval_boundary_candidate_reordering_allowed_in_future_package_not_expected",
            result["error_codes"],
        )

    def test_candidate_reordering_applied_blocks(self):
        record = build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["candidate_reordering_approval_boundary"]["candidate_reordering_applied"] = True

        result = validate_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "candidate_reordering_approval_boundary_candidate_reordering_applied_not_expected",
            result["error_codes"],
        )

    def test_selected_action_created_blocks(self):
        record = build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["candidate_reordering_approval_boundary"]["selected_action_created"] = True

        result = validate_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "candidate_reordering_approval_boundary_selected_action_created_not_expected",
            result["error_codes"],
        )

    def test_direct_command_created_blocks(self):
        record = build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["candidate_reordering_approval_boundary"]["direct_command_created"] = True

        result = validate_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "candidate_reordering_approval_boundary_direct_command_created_not_expected",
            result["error_codes"],
        )

    def test_memory_write_blocks(self):
        record = build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["blocked_flags"]["memory_write_performed"] = True

        result = validate_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_memory_write_performed_not_false", result["error_codes"])

    def test_predictor_mutation_blocks(self):
        record = build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["blocked_flags"]["predictor_mutation_performed"] = True

        result = validate_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_predictor_mutation_performed_not_false", result["error_codes"])

    def test_proof_claim_blocks(self):
        record = build_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["blocked_flags"]["proof_of_learning_claimed"] = True

        result = validate_body_motor_feedback_gated_candidate_reordering_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_proof_of_learning_claimed_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_body_motor_feedback_gated_candidate_reordering_approval_boundary_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["candidate_reordering_approval_boundary_result_count"], 37)
        self.assertEqual(summary["valid_candidate_reordering_approval_boundary_count"], 3)
        self.assertEqual(summary["invalid_candidate_reordering_approval_boundary_count"], 34)
        self.assertEqual(summary["future_reordering_allowed_count"], 2)
        self.assertEqual(summary["future_reordering_blocked_count"], 1)
        self.assertEqual(summary["movement_pressure_allowed_count"], 1)
        self.assertEqual(summary["reach_pressure_allowed_count"], 1)
        self.assertEqual(summary["wall_pressure_blocked_count"], 1)
        self.assertEqual(summary["candidate_reordering_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-body-motor-feedback-gated-candidate-reordering-approval-boundary-minimal-check")

        self.assertEqual(
            result["command"],
            "run-body-motor-feedback-gated-candidate-reordering-approval-boundary-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
