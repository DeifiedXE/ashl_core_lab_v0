import copy
import unittest

from ashl_core.sandbox_body_motor_command_execution_loop_minimal import (
    run_sandbox_body_motor_command_execution_loop_minimal_check,
)
from ashl_core.sandbox_body_motor_execution_feedback_settling_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_body_motor_execution_feedback_settling_record,
    run_sandbox_body_motor_execution_feedback_settling_minimal_check,
    validate_sandbox_body_motor_execution_feedback_settling_record,
)
from ashl_core.teaching_cli import run_command


class SandboxBodyMotorExecutionFeedbackSettlingMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_body_motor_command_execution_loop_minimal_check()["valid_records"]

    def test_valid_feedback_settling_record_is_created(self):
        record = build_sandbox_body_motor_execution_feedback_settling_record(self.sources[0])
        result = validate_sandbox_body_motor_execution_feedback_settling_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "sandbox_body_motor_execution_feedback_settling_minimal")
        self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_step_forward_outcome_creates_movement_feedback_and_settling(self):
        record = build_sandbox_body_motor_execution_feedback_settling_record(self.sources[0])
        feedback = record["feedback_trace"]
        settling = record["settling_trace"]

        self.assertTrue(feedback["feedback_trace_created"])
        self.assertEqual(feedback["source_final_action"], "step_forward")
        self.assertEqual(feedback["feedback_label"], "movement_success_feedback")
        self.assertEqual(feedback["response_axis"], "dopamine_like")
        self.assertTrue(settling["settling_trace_created"])
        self.assertEqual(settling["settling_mode"], "natural_settling")
        self.assertTrue(settling["settled_to_baseline"])

    def test_reach_front_outcome_creates_reach_feedback_and_settling(self):
        record = build_sandbox_body_motor_execution_feedback_settling_record(self.sources[2])
        feedback = record["feedback_trace"]

        self.assertTrue(feedback["feedback_trace_created"])
        self.assertEqual(feedback["source_final_action"], "reach_front")
        self.assertEqual(feedback["feedback_label"], "reach_success_feedback")
        self.assertEqual(feedback["source_execution_result"], "front_item_reached")

    def test_wall_case_blocks_feedback_and_settling(self):
        record = build_sandbox_body_motor_execution_feedback_settling_record(self.sources[1])

        self.assertFalse(record["feedback_trace"]["feedback_trace_created"])
        self.assertEqual(record["feedback_trace"]["blocked_reason"], "outcome_not_available_for_feedback")
        self.assertFalse(record["settling_trace"]["settling_trace_created"])
        self.assertEqual(record["settling_trace"]["blocked_reason"], "feedback_not_available_for_settling")

    def test_rollback_restores_baseline_without_dirty_state(self):
        record = build_sandbox_body_motor_execution_feedback_settling_record(self.sources[0])
        rollback = record["rollback_trace"]

        self.assertTrue(rollback["rollback_available"])
        self.assertTrue(rollback["session_end_restores_baseline"])
        self.assertFalse(rollback["dirty_state_after_rollback"])
        self.assertFalse(rollback["persistent_update_performed"])

    def test_feedback_is_same_session_only_and_trace_only(self):
        record = build_sandbox_body_motor_execution_feedback_settling_record(self.sources[0])
        feedback = record["feedback_trace"]

        self.assertEqual(feedback["feedback_scope"], "same_session_sandbox_only")
        self.assertTrue(feedback["trace_only"])
        self.assertFalse(feedback["applied_persistently"])
        self.assertFalse(feedback["candidate_reordering_created"])
        self.assertFalse(feedback["new_action_created"])

    def test_feedback_not_created_blocks(self):
        record = build_sandbox_body_motor_execution_feedback_settling_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["feedback_trace"]["feedback_trace_created"] = False

        result = validate_sandbox_body_motor_execution_feedback_settling_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("feedback_trace_feedback_trace_created_not_expected", result["error_codes"])

    def test_wrong_feedback_label_blocks(self):
        record = build_sandbox_body_motor_execution_feedback_settling_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["feedback_trace"]["feedback_label"] = "wrong"

        result = validate_sandbox_body_motor_execution_feedback_settling_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("feedback_trace_feedback_label_not_expected", result["error_codes"])

    def test_persistent_feedback_blocks(self):
        record = build_sandbox_body_motor_execution_feedback_settling_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["feedback_trace"]["applied_persistently"] = True

        result = validate_sandbox_body_motor_execution_feedback_settling_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("feedback_trace_applied_persistently_not_expected", result["error_codes"])

    def test_candidate_reordering_blocks(self):
        record = build_sandbox_body_motor_execution_feedback_settling_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["feedback_trace"]["candidate_reordering_created"] = True

        result = validate_sandbox_body_motor_execution_feedback_settling_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("feedback_trace_candidate_reordering_created_not_expected", result["error_codes"])

    def test_settling_not_to_baseline_blocks(self):
        record = build_sandbox_body_motor_execution_feedback_settling_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["settling_trace"]["settled_to_baseline"] = False

        result = validate_sandbox_body_motor_execution_feedback_settling_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("settling_trace_settled_to_baseline_not_expected", result["error_codes"])

    def test_memory_write_blocks(self):
        record = build_sandbox_body_motor_execution_feedback_settling_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["blocked_flags"]["memory_write_performed"] = True

        result = validate_sandbox_body_motor_execution_feedback_settling_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_memory_write_performed_not_false", result["error_codes"])

    def test_predictor_mutation_blocks(self):
        record = build_sandbox_body_motor_execution_feedback_settling_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["blocked_flags"]["predictor_mutation_performed"] = True

        result = validate_sandbox_body_motor_execution_feedback_settling_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_predictor_mutation_performed_not_false", result["error_codes"])

    def test_subjective_claim_blocks(self):
        record = build_sandbox_body_motor_execution_feedback_settling_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["blocked_flags"]["subjective_emotion_claim_allowed"] = True

        result = validate_sandbox_body_motor_execution_feedback_settling_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_subjective_emotion_claim_allowed_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_sandbox_body_motor_execution_feedback_settling_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["feedback_settling_result_count"], 37)
        self.assertEqual(summary["valid_feedback_settling_count"], 3)
        self.assertEqual(summary["invalid_feedback_settling_count"], 34)
        self.assertEqual(summary["feedback_trace_created_count"], 2)
        self.assertEqual(summary["feedback_blocked_count"], 1)
        self.assertEqual(summary["settling_trace_created_count"], 2)
        self.assertEqual(summary["settling_blocked_count"], 1)
        self.assertEqual(summary["step_forward_feedback_count"], 1)
        self.assertEqual(summary["reach_front_feedback_count"], 1)
        self.assertEqual(summary["wall_feedback_blocked_count"], 1)

    def test_cli_command(self):
        result = run_command("run-sandbox-body-motor-execution-feedback-settling-minimal-check")

        self.assertEqual(result["command"], "run-sandbox-body-motor-execution-feedback-settling-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
