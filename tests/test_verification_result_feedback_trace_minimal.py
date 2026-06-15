import unittest
from copy import deepcopy

from ashl_core.teaching_cli import run_command
from ashl_core.verification_result_feedback_trace_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER,
    BOUNDARY_INDEX_VERSION_BEFORE,
    build_verification_result_feedback_trace,
    run_verification_result_feedback_trace_minimal_check,
    validate_verification_result_feedback_trace,
)


class VerificationResultFeedbackTraceMinimalTests(unittest.TestCase):
    def test_valid_feedback_trace(self):
        trace = build_verification_result_feedback_trace()
        result = validate_verification_result_feedback_trace(trace)

        self.assertTrue(result["valid"])
        self.assertEqual("verification_result_feedback_trace", trace["record_type"])
        self.assertEqual("valid_trace_only_verification_result_feedback", trace["trace_status"])
        self.assertEqual("trace_only_feedback_generated", trace["feedback_status"])

    def test_feedback_trace_uses_b90_execution_source(self):
        trace = build_verification_result_feedback_trace()

        self.assertEqual("verification_execution_b90", trace["source_verification_execution"])
        self.assertEqual("verification_plan_b89", trace["source_verification_plan"])
        self.assertEqual("verification_candidate_registry_b88", trace["source_verification_candidate_registry"])
        self.assertEqual("observe_or_alternative_probe", trace["selected_verification_candidate_id"])

    def test_probe_result_fields(self):
        trace = build_verification_result_feedback_trace()

        self.assertEqual("local_context_observed", trace["actual_probe_result"])
        self.assertTrue(trace["probe_result_recorded"])
        self.assertTrue(trace["stop_condition_met"])
        self.assertEqual(1, trace["execution_budget"])
        self.assertEqual(1, trace["execution_count"])

    def test_feedback_payloads_are_trace_only(self):
        trace = build_verification_result_feedback_trace()

        self.assertEqual(-0.1, trace["doubt_feedback"]["suggested_delta"])
        self.assertEqual(0.05, trace["verification_candidate_trust_feedback"]["suggested_delta"])
        self.assertEqual(0.35, trace["direct_retry_weight_feedback"]["suggested_weight"])
        self.assertEqual(0.0, trace["hypothesis_trust_feedback"]["suggested_delta"])
        self.assertFalse(trace["doubt_feedback"]["applied_persistently"])
        self.assertFalse(trace["verification_candidate_trust_feedback"]["applied_persistently"])
        self.assertFalse(trace["direct_retry_weight_feedback"]["applied_persistently"])
        self.assertFalse(trace["hypothesis_trust_feedback"]["applied_persistently"])

    def test_boundaries_remain_blocked(self):
        trace = build_verification_result_feedback_trace()

        self.assertFalse(trace["feedback_applied_to_runtime"])
        self.assertFalse(trace["persistent_update_performed"])
        self.assertFalse(trace["memory_write_performed"])
        self.assertFalse(trace["retention_write_performed"])
        self.assertFalse(trace["predictor_mutation_performed"])
        self.assertFalse(trace["persistent_rule_created"])
        self.assertFalse(trace["selected_action_created"])
        self.assertFalse(trace["final_action_created"])
        self.assertFalse(trace["direct_command_created"])
        self.assertFalse(trace["production_behavior_changed"])
        self.assertFalse(trace["proof_of_learning_claim_allowed"])

    def test_cli_command_returns_ok(self):
        result = run_command("run-verification-result-feedback-trace-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_feedback_trace_count"])

    def test_boundary_versions(self):
        result = run_verification_result_feedback_trace_minimal_check()

        self.assertEqual("2026-06-09-b90", BOUNDARY_INDEX_VERSION_BEFORE)
        self.assertEqual("2026-06-09-b91", BOUNDARY_INDEX_VERSION_AFTER)
        self.assertEqual("2026-06-09-b90", result["boundary"]["boundary_index_version_before"])
        self.assertEqual("2026-06-09-b91", result["boundary"]["boundary_index_version_after"])

    def test_invalid_missing_source_execution(self):
        self.assertInvalid("source_execution_result_trace", {})

    def test_invalid_missing_actual_probe_result(self):
        self.assertInvalid("actual_probe_result", "")

    def test_invalid_stop_condition_not_met(self):
        self.assertInvalid("stop_condition_met", False)

    def test_invalid_execution_budget_not_one(self):
        self.assertInvalid("execution_budget", 2)

    def test_invalid_execution_count_not_one(self):
        self.assertInvalid("execution_count", 2)

    def test_invalid_feedback_applied_to_runtime(self):
        self.assertInvalid("feedback_applied_to_runtime", True)

    def test_invalid_persistent_update_performed(self):
        self.assertInvalid("persistent_update_performed", True)

    def test_invalid_persistent_doubt_update(self):
        self.assertInvalidNested("doubt_feedback", "applied_persistently", True)

    def test_invalid_persistent_trust_update(self):
        self.assertInvalidNested("verification_candidate_trust_feedback", "applied_persistently", True)

    def test_invalid_hypothesis_trust_direct_increase(self):
        self.assertInvalidNested("hypothesis_trust_feedback", "suggested_delta", 0.1)

    def test_invalid_direct_retry_weight_increase(self):
        self.assertInvalidNested("direct_retry_weight_feedback", "suggested_weight", 0.5)

    def test_invalid_memory_retention_predictor_and_rule(self):
        self.assertInvalid("memory_write_performed", True)
        self.assertInvalid("retention_write_performed", True)
        self.assertInvalid("predictor_mutation_performed", True)
        self.assertInvalid("persistent_rule_created", True)

    def test_invalid_selected_final_direct_and_production(self):
        self.assertInvalid("selected_action_created", True)
        self.assertInvalid("final_action_created", True)
        self.assertInvalid("direct_command_created", True)
        self.assertInvalid("production_behavior_changed", True)

    def test_invalid_proof_and_autonomous_claims(self):
        self.assertInvalid("proof_of_learning_claim_allowed", True)
        self.assertInvalid("autonomous_learning_claim_allowed", True)
        self.assertInvalid("autonomous_action_claim_allowed", True)

    def test_invalid_llm_used_true(self):
        self.assertInvalid("llm_used", True)

    def test_summary_counts_are_deterministic(self):
        result = run_verification_result_feedback_trace_minimal_check()
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_feedback_trace_count"])
        self.assertGreaterEqual(summary["invalid_feedback_trace_count"], 25)
        self.assertEqual(1, summary["source_execution_checked_count"])
        self.assertEqual(1, summary["probe_result_checked_count"])
        self.assertEqual(1, summary["feedback_generated_count"])
        self.assertEqual(1, summary["persistent_update_blocked_count"])
        self.assertEqual(1, summary["runtime_feedback_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["persistent_rule_blocked_count"])
        self.assertEqual(1, summary["selected_action_blocked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_verification_result_feedback_trace_checks_passed"])

    def assertInvalid(self, field, value):
        trace = deepcopy(build_verification_result_feedback_trace())
        trace[field] = value

        self.assertFalse(validate_verification_result_feedback_trace(trace)["valid"])

    def assertInvalidNested(self, section, field, value):
        trace = deepcopy(build_verification_result_feedback_trace())
        trace[section][field] = value

        self.assertFalse(validate_verification_result_feedback_trace(trace)["valid"])


if __name__ == "__main__":
    unittest.main()
