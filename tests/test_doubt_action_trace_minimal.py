import unittest
from copy import deepcopy

from ashl_core.doubt_action_trace_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER,
    BOUNDARY_INDEX_VERSION_BEFORE,
    build_doubt_action_trace,
    run_doubt_action_trace_minimal_check,
    validate_doubt_action_trace,
)
from ashl_core.teaching_cli import run_command


class DoubtActionTraceMinimalTests(unittest.TestCase):
    def test_valid_mismatch_trace(self):
        trace = build_doubt_action_trace()
        result = validate_doubt_action_trace(trace)

        self.assertTrue(result["valid"])
        self.assertEqual("doubt_action", trace["event_type"])
        self.assertNotEqual(trace["expected_outcome"], trace["actual_outcome"])
        self.assertGreater(trace["doubt_after"], trace["doubt_before"])
        self.assertLess(trace["direct_retry_weight_after"], trace["direct_retry_weight_before"])
        self.assertEqual("observe_or_alternative_probe", trace["verification_candidate"])
        self.assertFalse(trace["verification_action_executed"])
        self.assertTrue(trace["trace_only"])
        self.assertTrue(trace["candidate_adjustment_only"])

    def test_cli_command_returns_ok(self):
        result = run_command("run-doubt-action-trace-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_trace_count"])

    def test_boundary_versions(self):
        result = run_doubt_action_trace_minimal_check()

        self.assertEqual("2026-06-09-b85", BOUNDARY_INDEX_VERSION_BEFORE)
        self.assertEqual("2026-06-09-b86", BOUNDARY_INDEX_VERSION_AFTER)
        self.assertEqual("2026-06-09-b85", result["boundary"]["boundary_index_version_before"])
        self.assertEqual("2026-06-09-b86", result["boundary"]["boundary_index_version_after"])

    def test_invalid_no_mismatch(self):
        self.assertInvalid("actual_outcome", "box_pushed")

    def test_invalid_doubt_does_not_increase(self):
        self.assertInvalid("doubt_after", 0.18)

    def test_invalid_retry_weight_does_not_decrease(self):
        self.assertInvalid("direct_retry_weight_after", 0.50)

    def test_invalid_missing_verification_candidate(self):
        self.assertInvalid("verification_candidate", "")

    def test_invalid_verification_executed(self):
        self.assertInvalid("verification_action_executed", True)

    def test_invalid_missing_stop_condition(self):
        self.assertInvalid("stop_condition_present", False)

    def test_invalid_llm_used_true(self):
        self.assertInvalid("llm_used", True)

    def test_invalid_selected_action(self):
        self.assertInvalid("selected_action_created", True)

    def test_invalid_final_action(self):
        self.assertInvalid("final_action_created", True)

    def test_invalid_direct_command(self):
        self.assertInvalid("direct_command_created", True)

    def test_invalid_persistent_rule(self):
        self.assertInvalid("persistent_rule_created", True)

    def test_invalid_memory_write(self):
        self.assertInvalid("long_term_memory_write_performed", True)
        self.assertInvalid("retained_jsonl_write_performed", True)

    def test_invalid_retention_write(self):
        self.assertInvalid("retention_write_performed", True)

    def test_invalid_predictor_mutation(self):
        self.assertInvalid("predictor_mutation_performed", True)

    def test_invalid_production_behavior(self):
        self.assertInvalid("production_behavior_changed", True)

    def test_invalid_proof_claim(self):
        self.assertInvalid("proof_of_learning_claim_allowed", True)

    def test_invalid_autonomous_learning_action_claim(self):
        self.assertInvalid("autonomous_learning_claim_allowed", True)
        self.assertInvalid("autonomous_action_claim_allowed", True)

    def test_summary_counts_are_deterministic(self):
        result = run_doubt_action_trace_minimal_check()
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_trace_count"])
        self.assertGreaterEqual(summary["invalid_trace_count"], 19)
        self.assertEqual(1, summary["mismatch_checked_count"])
        self.assertEqual(1, summary["doubt_increase_checked_count"])
        self.assertEqual(1, summary["direct_retry_decrease_checked_count"])
        self.assertEqual(1, summary["verification_candidate_checked_count"])
        self.assertEqual(1, summary["verification_execution_blocked_count"])
        self.assertEqual(1, summary["stop_condition_checked_count"])
        self.assertEqual(1, summary["llm_blocked_count"])
        self.assertEqual(1, summary["selected_action_blocked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["persistent_rule_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_doubt_action_trace_minimal_checks_passed"])

    def assertInvalid(self, field, value):
        trace = deepcopy(build_doubt_action_trace())
        trace[field] = value

        self.assertFalse(validate_doubt_action_trace(trace)["valid"])


if __name__ == "__main__":
    unittest.main()
