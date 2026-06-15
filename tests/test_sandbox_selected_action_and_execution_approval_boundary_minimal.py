import unittest
from copy import deepcopy

from ashl_core.sandbox_selected_action_and_execution_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    TOP_RANKED_CANDIDATE,
    build_sandbox_action_execution_approval_boundary_record,
    build_sandbox_selected_action_record,
    build_selected_action_execution_boundary_summary,
    run_sandbox_selected_action_and_execution_approval_boundary_minimal_check,
    validate_sandbox_action_execution_approval_boundary_record,
    validate_sandbox_selected_action_record,
    validate_selected_action_execution_boundary_summary,
)
from ashl_core.teaching_cli import run_command


class SandboxSelectedActionAndExecutionApprovalBoundaryMinimalTests(unittest.TestCase):
    def test_valid_sandbox_selected_action(self):
        record = build_sandbox_selected_action_record()
        result = validate_sandbox_selected_action_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual("sandbox_selected_action", record["record_type"])
        self.assertEqual("sandbox_selected_action_approval_boundary_b94", record["source_selected_action_approval_boundary"])
        self.assertEqual(TOP_RANKED_CANDIDATE, record["top_ranked_candidate"])
        self.assertEqual(record["top_ranked_candidate"], record["selected_action"])
        self.assertTrue(record["selected_action_created"])
        self.assertFalse(record["action_executed"])

    def test_valid_execution_approval_boundary(self):
        record = build_sandbox_action_execution_approval_boundary_record()
        result = validate_sandbox_action_execution_approval_boundary_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual("approved_for_future_sandbox_action_execution_package_only", record["approval_status"])
        self.assertTrue(record["execution_allowed_in_future_package"])
        self.assertFalse(record["implementation_in_this_package"])
        self.assertFalse(record["execution_created"])

    def test_valid_combined_summary(self):
        record = build_selected_action_execution_boundary_summary()
        result = validate_selected_action_execution_boundary_summary(record)

        self.assertTrue(result["valid"])
        self.assertEqual("2026-06-09-b94", BOUNDARY_INDEX_BEFORE)
        self.assertEqual("2026-06-09-b95", BOUNDARY_INDEX_AFTER)
        self.assertTrue(record["sandbox_selected_action_created"])
        self.assertFalse(record["action_executed"])

    def test_cli_command_returns_ok(self):
        result = run_command("run-sandbox-selected-action-and-execution-approval-boundary-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_selected_action_count"])

    def test_invalid_missing_b94_approval_source(self):
        self.assertInvalidSelectedAction("source_selected_action_approval_boundary", "missing_b94_approval")

    def test_invalid_selected_action_differs_from_top_ranked_candidate(self):
        self.assertInvalidSelectedAction("selected_action", "check_before_retry")
        self.assertInvalidSummary("selected_action", "check_before_retry")

    def test_invalid_selected_action_outside_sandbox_scope(self):
        self.assertInvalidSelectedAction("sandbox_scope", "production_scope")
        self.assertInvalidSelectedAction("selection_scope", "runtime")

    def test_invalid_action_executed_in_this_package(self):
        self.assertInvalidSelectedAction("execution_allowed_in_this_package", True)
        self.assertInvalidSelectedAction("action_executed", True)
        self.assertInvalidSummary("action_executed", True)

    def test_invalid_final_action(self):
        self.assertInvalidSelectedAction("final_action_created", True)
        self.assertInvalidExecutionApproval("final_action_created", True)
        self.assertInvalidExecutionApproval("final_action_allowed", True)
        self.assertInvalidSummary("final_action_created", True)

    def test_invalid_direct_command(self):
        self.assertInvalidSelectedAction("direct_command_created", True)
        self.assertInvalidExecutionApproval("direct_command_created", True)
        self.assertInvalidSummary("direct_command_created", True)

    def test_invalid_production_behavior(self):
        self.assertInvalidSelectedAction("production_behavior_changed", True)
        self.assertInvalidExecutionApproval("production_behavior_changed", True)
        self.assertInvalidSummary("production_behavior_changed", True)

    def test_invalid_persistent_rule(self):
        self.assertInvalidSelectedAction("persistent_rule_created", True)
        self.assertInvalidExecutionApproval("persistent_rule_created", True)

    def test_invalid_persistent_trust_doubt_update(self):
        self.assertInvalidSelectedAction("persistent_trust_doubt_update_performed", True)

    def test_invalid_cross_session_persistence(self):
        self.assertInvalidSelectedAction("cross_session_feedback_persistence", True)

    def test_invalid_memory_write(self):
        self.assertInvalidSelectedAction("memory_write_performed", True)
        self.assertInvalidSelectedAction("retained_jsonl_write_performed", True)
        self.assertInvalidExecutionApproval("memory_write_performed", True)
        self.assertInvalidExecutionApproval("retained_jsonl_write_performed", True)
        self.assertInvalidSummary("memory_write_performed", True)

    def test_invalid_retention_write(self):
        self.assertInvalidSelectedAction("retention_write_performed", True)
        self.assertInvalidExecutionApproval("retention_write_performed", True)
        self.assertInvalidSummary("retention_write_performed", True)

    def test_invalid_predictor_read_influence_mutation(self):
        self.assertInvalidSelectedAction("predictor_read_enabled", True)
        self.assertInvalidSelectedAction("predictor_influence_enabled", True)
        self.assertInvalidSelectedAction("predictor_mutation_performed", True)
        self.assertInvalidExecutionApproval("predictor_mutation_performed", True)
        self.assertInvalidSummary("predictor_mutation_performed", True)

    def test_invalid_proof_claim(self):
        self.assertInvalidSelectedAction("proof_of_learning_claim_allowed", True)
        self.assertInvalidExecutionApproval("proof_of_learning_claim_allowed", True)
        self.assertInvalidSummary("proof_of_learning_claim_allowed", True)

    def test_invalid_autonomous_learning_action_claim(self):
        self.assertInvalidSelectedAction("autonomous_learning_claim_allowed", True)
        self.assertInvalidSelectedAction("autonomous_action_claim_allowed", True)

    def test_invalid_execution_approval_without_selected_action_source(self):
        self.assertInvalidExecutionApproval("source_selected_action_record_type", "missing_selected_action")
        self.assertInvalidExecutionApproval("selected_action_required_before_execution", False)

    def test_invalid_future_final_action_allowed(self):
        self.assertInvalidSelectedAction("future_final_action_requires_separate_boundary", False)
        self.assertInvalidExecutionApproval("future_final_action_requires_separate_boundary", False)

    def test_summary_counts_are_deterministic(self):
        result = run_sandbox_selected_action_and_execution_approval_boundary_minimal_check()
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_selected_action_count"])
        self.assertGreaterEqual(summary["invalid_selected_action_count"], 20)
        self.assertEqual(1, summary["valid_execution_approval_count"])
        self.assertGreaterEqual(summary["invalid_execution_approval_count"], 15)
        self.assertEqual(1, summary["valid_summary_count"])
        self.assertGreaterEqual(summary["invalid_summary_count"], 15)
        self.assertEqual(1, summary["selected_action_source_checked_count"])
        self.assertEqual(1, summary["top_ranked_candidate_checked_count"])
        self.assertEqual(1, summary["execution_blocked_count"])
        self.assertEqual(1, summary["future_execution_approval_checked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["direct_command_blocked_count"])
        self.assertEqual(1, summary["persistent_update_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_sandbox_selected_action_and_execution_approval_boundary_checks_passed"])

    def assertInvalidSelectedAction(self, field, value):
        record = deepcopy(build_sandbox_selected_action_record())
        record[field] = value
        self.assertFalse(validate_sandbox_selected_action_record(record)["valid"])

    def assertInvalidExecutionApproval(self, field, value):
        record = deepcopy(build_sandbox_action_execution_approval_boundary_record())
        record[field] = value
        self.assertFalse(validate_sandbox_action_execution_approval_boundary_record(record)["valid"])

    def assertInvalidSummary(self, field, value):
        record = deepcopy(build_selected_action_execution_boundary_summary())
        record[field] = value
        self.assertFalse(validate_selected_action_execution_boundary_summary(record)["valid"])


if __name__ == "__main__":
    unittest.main()
