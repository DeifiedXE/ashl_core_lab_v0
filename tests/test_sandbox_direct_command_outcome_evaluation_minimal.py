import unittest
from copy import deepcopy

from ashl_core.sandbox_direct_command_outcome_evaluation_minimal import (
    BOUNDARY_INDEX,
    build_sandbox_direct_command_outcome_evaluation_record,
    run_sandbox_direct_command_outcome_evaluation_minimal_check,
    validate_sandbox_direct_command_outcome_evaluation_record,
)
from ashl_core.sandbox_direct_command_execution_minimal import DIRECT_COMMAND, EXECUTION_RESULT


class SandboxDirectCommandOutcomeEvaluationMinimalTests(unittest.TestCase):
    def setUp(self):
        self.record = build_sandbox_direct_command_outcome_evaluation_record()

    def test_valid_outcome_evaluation(self):
        result = validate_sandbox_direct_command_outcome_evaluation_record(self.record)
        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual("sandbox_direct_command_outcome_evaluation", self.record["record_type"])
        self.assertEqual("passed_sandbox_direct_command_outcome_evaluation", self.record["evaluation_status"])
        self.assertEqual(BOUNDARY_INDEX, self.record["boundary_index_before"])
        self.assertEqual(BOUNDARY_INDEX, self.record["boundary_index_after"])
        self.assertFalse(self.record["boundary_change_required"])
        self.assertFalse(self.record["boundary_index_update_required"])

    def test_reuses_b103_b104_feedback_loop_sources(self):
        result = validate_sandbox_direct_command_outcome_evaluation_record(self.record)
        self.assertTrue(result["source_feedback_loop_checked"])
        for field in (
            "source_feedback_trace_record",
            "source_ephemeral_application_record",
            "source_reordering_record",
            "source_rollback_record",
        ):
            bad = deepcopy(self.record)
            bad[field] = {}
            self.assertFalse(validate_sandbox_direct_command_outcome_evaluation_record(bad)["valid"], field)

    def test_direct_command_outcome_passes(self):
        result = validate_sandbox_direct_command_outcome_evaluation_record(self.record)
        evaluation = self.record["outcome_evaluation"]
        self.assertTrue(result["outcome_evaluation_passed"])
        self.assertEqual(DIRECT_COMMAND, self.record["direct_command"])
        self.assertEqual(EXECUTION_RESULT, self.record["execution_result"])
        self.assertEqual(1, self.record["execution_count"])
        self.assertEqual(1, self.record["execution_budget"])
        self.assertEqual("passed", evaluation["evaluation_result"])
        self.assertEqual("sandbox_observation_success", evaluation["outcome_label"])
        self.assertTrue(evaluation["observed_context"])
        self.assertTrue(evaluation["execution_within_budget"])
        self.assertTrue(evaluation["stop_condition_met"])
        self.assertFalse(evaluation["dirty_state_after_rollback"])

    def test_next_cycle_readiness_is_prepare_only(self):
        result = validate_sandbox_direct_command_outcome_evaluation_record(self.record)
        readiness = self.record["next_cycle_readiness"]
        self.assertTrue(result["next_cycle_readiness_checked"])
        self.assertTrue(readiness["ready_to_prepare_next_sandbox_cycle"])
        self.assertEqual("prepare_next_sandbox_cycle_only", readiness["allowed_next_step"])
        self.assertFalse(readiness["may_create_new_direct_command"])
        self.assertFalse(readiness["may_execute_next_direct_command"])
        self.assertFalse(readiness["may_change_production_behavior"])
        self.assertTrue(readiness["requires_separate_approval_for_next_execution"])

    def test_boundary_unchanged_required(self):
        bad = deepcopy(self.record)
        bad["boundary_index_after"] = "2026-06-09-b105"
        result = validate_sandbox_direct_command_outcome_evaluation_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn("boundary_index_after_not_expected", result["error_codes"])
        self.assertFalse(result["boundary_unchanged_checked"])

    def test_wrong_command_blocks(self):
        bad = deepcopy(self.record)
        bad["direct_command"] = "sandbox.retry_same_action"
        result = validate_sandbox_direct_command_outcome_evaluation_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn("direct_command_not_expected", result["error_codes"])

    def test_execution_count_greater_than_one_blocks(self):
        bad = deepcopy(self.record)
        bad["execution_count"] = 2
        result = validate_sandbox_direct_command_outcome_evaluation_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn("execution_count_not_expected", result["error_codes"])

    def test_outcome_failure_blocks(self):
        bad = deepcopy(self.record)
        bad["outcome_evaluation"]["evaluation_result"] = "failed"
        result = validate_sandbox_direct_command_outcome_evaluation_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn("outcome_evaluation_evaluation_result_not_expected", result["error_codes"])
        self.assertFalse(result["outcome_evaluation_passed"])

    def test_dirty_rollback_blocks(self):
        bad = deepcopy(self.record)
        bad["outcome_evaluation"]["dirty_state_after_rollback"] = True
        result = validate_sandbox_direct_command_outcome_evaluation_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn("outcome_evaluation_dirty_state_after_rollback_not_expected", result["error_codes"])

    def test_may_create_new_direct_command_blocks(self):
        bad = deepcopy(self.record)
        bad["next_cycle_readiness"]["may_create_new_direct_command"] = True
        result = validate_sandbox_direct_command_outcome_evaluation_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn(
            "next_cycle_readiness_may_create_new_direct_command_not_expected",
            result["error_codes"],
        )
        self.assertFalse(result["next_cycle_readiness_checked"])

    def test_may_execute_next_direct_command_blocks(self):
        bad = deepcopy(self.record)
        bad["next_cycle_readiness"]["may_execute_next_direct_command"] = True
        result = validate_sandbox_direct_command_outcome_evaluation_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn(
            "next_cycle_readiness_may_execute_next_direct_command_not_expected",
            result["error_codes"],
        )
        self.assertFalse(result["new_direct_command_blocked"])

    def test_blocked_flags_true_block(self):
        for field in self.record["blocked_flags"]:
            bad = deepcopy(self.record)
            bad["blocked_flags"][field] = True
            result = validate_sandbox_direct_command_outcome_evaluation_record(bad)
            self.assertFalse(result["valid"], field)
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_all_boundary_groups_are_blocked(self):
        result = validate_sandbox_direct_command_outcome_evaluation_record(self.record)
        self.assertTrue(result["new_direct_command_blocked"])
        self.assertTrue(result["production_behavior_blocked"])
        self.assertTrue(result["persistent_feedback_blocked"])
        self.assertTrue(result["memory_write_blocked"])
        self.assertTrue(result["retention_blocked"])
        self.assertTrue(result["predictor_mutation_blocked"])
        self.assertTrue(result["runtime_behavior_change_blocked"])
        self.assertTrue(result["action_creation_blocked"])
        self.assertTrue(result["proof_claim_blocked"])

    def test_human_summary_fields_required(self):
        for field in self.record["human_review_summary"]:
            bad = deepcopy(self.record)
            bad["human_review_summary"][field] = ""
            result = validate_sandbox_direct_command_outcome_evaluation_record(bad)
            self.assertFalse(result["valid"], field)
            self.assertIn(f"human_review_summary_{field}_empty", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_sandbox_direct_command_outcome_evaluation_minimal_check()
        summary = result["summary"]
        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_outcome_evaluation_count"])
        self.assertEqual(54, summary["invalid_outcome_evaluation_count"])
        self.assertEqual(1, summary["source_feedback_loop_checked_count"])
        self.assertEqual(1, summary["boundary_unchanged_checked_count"])
        self.assertEqual(1, summary["outcome_evaluation_passed_count"])
        self.assertEqual(1, summary["next_cycle_readiness_checked_count"])
        self.assertEqual(1, summary["new_direct_command_blocked_count"])
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["persistent_feedback_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["runtime_behavior_change_blocked_count"])
        self.assertEqual(1, summary["action_creation_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_sandbox_direct_command_outcome_evaluation_checks_passed"])


if __name__ == "__main__":
    unittest.main()
