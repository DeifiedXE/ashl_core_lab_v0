import unittest
from copy import deepcopy

from ashl_core.teaching_cli import run_command
from ashl_core.verification_execution_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER,
    BOUNDARY_INDEX_VERSION_BEFORE,
    build_verification_execution_record,
    build_verification_execution_result_trace,
    run_verification_execution_minimal_check,
    validate_verification_execution_record,
    validate_verification_execution_result_trace,
)


class VerificationExecutionMinimalTests(unittest.TestCase):
    def test_valid_sandbox_only_verification_execution(self):
        record = build_verification_execution_record()
        result = validate_verification_execution_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual("verification_execution", record["record_type"])
        self.assertEqual("completed_sandbox_only_verification_execution", record["execution_status"])
        self.assertEqual("observe_or_alternative_probe", record["selected_verification_candidate_id"])
        self.assertTrue(record["verification_action_executed"])

    def test_valid_result_trace(self):
        trace = build_verification_execution_result_trace()
        result = validate_verification_execution_result_trace(trace)

        self.assertTrue(result["valid"])
        self.assertEqual("verification_execution_result_trace", trace["record_type"])
        self.assertEqual("valid_sandbox_only_verification_result", trace["trace_status"])
        self.assertEqual("local_context_observed", trace["actual_probe_result"])

    def test_execution_uses_b88_registry_and_b89_plan(self):
        record = build_verification_execution_record()

        self.assertEqual("verification_plan_b89", record["source_verification_plan"])
        self.assertEqual("verification_candidate_registry_b88", record["source_candidate_registry"])
        self.assertTrue(record["candidate_found_in_registry"])

    def test_execution_budget_and_stop_condition(self):
        record = build_verification_execution_record()

        self.assertEqual(1, record["execution_count"])
        self.assertEqual(1, record["execution_budget"])
        self.assertEqual(0, record["budget_remaining"])
        self.assertTrue(record["stop_condition_met"])

    def test_probe_result_recorded(self):
        record = build_verification_execution_record()

        self.assertEqual("local_context_observed_or_alternative_checked", record["expected_probe_outcome"])
        self.assertEqual("local_context_observed", record["actual_probe_result"])
        self.assertTrue(record["probe_result_recorded"])

    def test_boundaries_remain_blocked(self):
        record = build_verification_execution_record()

        self.assertFalse(record["selected_action_created"])
        self.assertFalse(record["final_action_created"])
        self.assertFalse(record["direct_command_created"])
        self.assertFalse(record["persistent_rule_created"])
        self.assertFalse(record["long_term_memory_write_performed"])
        self.assertFalse(record["retained_jsonl_write_performed"])
        self.assertFalse(record["retention_write_performed"])
        self.assertFalse(record["predictor_mutation_performed"])
        self.assertFalse(record["production_behavior_changed"])
        self.assertFalse(record["proof_of_learning_claim_allowed"])

    def test_result_trace_allows_future_doubt_feedback_without_update(self):
        trace = build_verification_execution_result_trace()

        self.assertTrue(trace["doubt_feedback_allowed"])
        self.assertFalse(trace["doubt_score_update_performed"])
        self.assertFalse(trace["trust_score_update_performed"])
        self.assertFalse(trace["persistent_update_performed"])

    def test_cli_command_returns_ok(self):
        result = run_command("run-verification-execution-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_execution_count"])

    def test_boundary_versions(self):
        result = run_verification_execution_minimal_check()

        self.assertEqual("2026-06-09-b89", BOUNDARY_INDEX_VERSION_BEFORE)
        self.assertEqual("2026-06-09-b90", BOUNDARY_INDEX_VERSION_AFTER)
        self.assertEqual("2026-06-09-b89", result["boundary"]["boundary_index_version_before"])
        self.assertEqual("2026-06-09-b90", result["boundary"]["boundary_index_version_after"])

    def test_invalid_missing_registry_candidate(self):
        self.assertInvalidExecution("candidate_found_in_registry", False)

    def test_invalid_unapproved_candidate_id(self):
        self.assertInvalidExecution("selected_verification_candidate_id", "inspect_device")

    def test_invalid_execution_count_over_one(self):
        self.assertInvalidExecution("execution_count", 2)

    def test_invalid_budget_over_one(self):
        self.assertInvalidExecution("execution_budget", 2)

    def test_invalid_budget_remaining_negative(self):
        self.assertInvalidExecution("budget_remaining", -1)

    def test_invalid_missing_stop_condition(self):
        self.assertInvalidExecution("stop_condition_met", False)

    def test_invalid_probe_result_outside_vocabulary(self):
        self.assertInvalidExecution("actual_probe_result", "free_form_result")

    def test_invalid_execution_outside_sandbox_scope(self):
        self.assertInvalidExecution("sandbox_scope", "production_scope")

    def test_invalid_natural_language_action(self):
        self.assertInvalidExecution("natural_language_action_executed", True)

    def test_invalid_external_tool_action(self):
        self.assertInvalidExecution("external_tool_action_executed", True)

    def test_invalid_selected_final_direct_and_persistent_flags(self):
        self.assertInvalidExecution("selected_action_created", True)
        self.assertInvalidExecution("final_action_created", True)
        self.assertInvalidExecution("direct_command_created", True)
        self.assertInvalidExecution("persistent_rule_created", True)

    def test_invalid_memory_retention_predictor_production_and_proof(self):
        self.assertInvalidExecution("long_term_memory_write_performed", True)
        self.assertInvalidExecution("retained_jsonl_write_performed", True)
        self.assertInvalidExecution("retention_write_performed", True)
        self.assertInvalidExecution("predictor_read_enabled", True)
        self.assertInvalidExecution("predictor_influence_enabled", True)
        self.assertInvalidExecution("predictor_mutation_performed", True)
        self.assertInvalidExecution("production_behavior_changed", True)
        self.assertInvalidExecution("proof_of_learning_claim_allowed", True)

    def test_invalid_autonomous_claims(self):
        self.assertInvalidExecution("autonomous_learning_claim_allowed", True)
        self.assertInvalidExecution("autonomous_action_claim_allowed", True)

    def test_invalid_llm_used_true(self):
        self.assertInvalidExecution("llm_used", True)

    def test_invalid_dirty_state_after_completion(self):
        self.assertInvalidExecution("dirty_state_after_completion", True)

    def test_invalid_result_trace_persistent_updates(self):
        self.assertInvalidTrace("doubt_score_update_performed", True)
        self.assertInvalidTrace("trust_score_update_performed", True)
        self.assertInvalidTrace("persistent_update_performed", True)

    def test_invalid_result_trace_source_blocks(self):
        trace = build_verification_execution_result_trace()
        trace["source_execution_record"] = {}

        self.assertFalse(validate_verification_execution_result_trace(trace)["valid"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_verification_execution_minimal_check()
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_execution_count"])
        self.assertGreaterEqual(summary["invalid_execution_count"], 27)
        self.assertEqual(1, summary["valid_result_trace_count"])
        self.assertGreaterEqual(summary["invalid_result_trace_count"], 10)
        self.assertEqual(1, summary["candidate_registry_checked_count"])
        self.assertEqual(1, summary["verification_plan_checked_count"])
        self.assertEqual(1, summary["execution_budget_checked_count"])
        self.assertEqual(1, summary["stop_condition_checked_count"])
        self.assertEqual(1, summary["probe_result_checked_count"])
        self.assertEqual(1, summary["selected_action_blocked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["persistent_rule_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_verification_execution_checks_passed"])

    def assertInvalidExecution(self, field, value):
        record = deepcopy(build_verification_execution_record())
        record[field] = value

        self.assertFalse(validate_verification_execution_record(record)["valid"])

    def assertInvalidTrace(self, field, value):
        trace = deepcopy(build_verification_execution_result_trace())
        trace[field] = value

        self.assertFalse(validate_verification_execution_result_trace(trace)["valid"])


if __name__ == "__main__":
    unittest.main()
