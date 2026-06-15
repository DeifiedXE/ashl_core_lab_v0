import unittest
from copy import deepcopy

from ashl_core.doubt_gated_sandbox_candidate_ordering_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER,
    BOUNDARY_INDEX_VERSION_BEFORE,
    build_doubt_gated_candidate_ordering_record,
    run_doubt_gated_sandbox_candidate_ordering_minimal_check,
    validate_doubt_gated_candidate_ordering_record,
)
from ashl_core.teaching_cli import run_command


class DoubtGatedSandboxCandidateOrderingMinimalTests(unittest.TestCase):
    def test_valid_doubt_gated_ordering(self):
        record = build_doubt_gated_candidate_ordering_record()
        result = validate_doubt_gated_candidate_ordering_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual("doubt_gated_sandbox_candidate_ordering", record["record_type"])
        self.assertEqual("phase0_level3_sandbox_only", record["sandbox_scope"])
        self.assertNotEqual(record["expected_outcome"], record["actual_outcome"])
        self.assertGreater(record["doubt_after"], record["doubt_before"])
        self.assertLess(record["direct_retry_weight_after"], record["direct_retry_weight_before"])
        self.assertLess(
            record["candidate_actions_after_ordering"].index("observe_or_alternative_probe"),
            record["candidate_actions_after_ordering"].index("retry_same_action_without_check"),
        )
        self.assertLess(
            record["candidate_actions_after_ordering"].index("check_before_retry"),
            record["candidate_actions_after_ordering"].index("retry_same_action_without_check"),
        )
        self.assertTrue(record["ordering_is_sandbox_only"])
        self.assertTrue(record["ordering_is_advisory"])

    def test_cli_command_returns_ok(self):
        result = run_command("run-doubt-gated-sandbox-candidate-ordering-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_ordering_count"])

    def test_boundary_versions(self):
        result = run_doubt_gated_sandbox_candidate_ordering_minimal_check()

        self.assertEqual("2026-06-09-b86", BOUNDARY_INDEX_VERSION_BEFORE)
        self.assertEqual("2026-06-09-b87", BOUNDARY_INDEX_VERSION_AFTER)
        self.assertEqual("2026-06-09-b86", result["boundary"]["boundary_index_version_before"])
        self.assertEqual("2026-06-09-b87", result["boundary"]["boundary_index_version_after"])

    def test_invalid_no_mismatch(self):
        self.assertInvalid("actual_outcome", "box_pushed")

    def test_invalid_doubt_does_not_rise(self):
        self.assertInvalid("doubt_after", 0.18)

    def test_invalid_direct_retry_weight_does_not_drop(self):
        self.assertInvalid("direct_retry_weight_after", 0.50)

    def test_invalid_verification_candidate_not_ranked_before_direct_retry(self):
        self.assertInvalid(
            "candidate_actions_after_ordering",
            [
                "check_before_retry",
                "fallback_stop_and_report",
                "retry_same_action_without_check",
                "observe_or_alternative_probe",
            ],
        )

    def test_invalid_check_before_retry_not_ranked_before_direct_retry(self):
        self.assertInvalid(
            "candidate_actions_after_ordering",
            [
                "observe_or_alternative_probe",
                "fallback_stop_and_report",
                "retry_same_action_without_check",
                "check_before_retry",
            ],
        )

    def test_invalid_verification_executed(self):
        self.assertInvalid("verification_action_executed", True)

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

    def test_invalid_retained_jsonl_write(self):
        self.assertInvalid("retained_jsonl_write_performed", True)

    def test_invalid_retention_write(self):
        self.assertInvalid("retention_write_performed", True)

    def test_invalid_predictor_read_influence_mutation(self):
        self.assertInvalid("predictor_read_enabled", True)
        self.assertInvalid("predictor_influence_enabled", True)
        self.assertInvalid("predictor_mutation_performed", True)

    def test_invalid_production_behavior(self):
        self.assertInvalid("production_behavior_changed", True)

    def test_invalid_proof_claim(self):
        self.assertInvalid("proof_of_learning_claim_allowed", True)

    def test_invalid_llm_used_true(self):
        self.assertInvalid("llm_used", True)

    def test_invalid_autonomous_learning_action_claim(self):
        self.assertInvalid("autonomous_learning_claim_allowed", True)
        self.assertInvalid("autonomous_action_claim_allowed", True)

    def test_summary_counts_are_deterministic(self):
        result = run_doubt_gated_sandbox_candidate_ordering_minimal_check()
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_ordering_count"])
        self.assertGreaterEqual(summary["invalid_ordering_count"], 21)
        self.assertEqual(1, summary["mismatch_checked_count"])
        self.assertEqual(1, summary["doubt_increase_checked_count"])
        self.assertEqual(1, summary["direct_retry_decrease_checked_count"])
        self.assertEqual(1, summary["verification_rank_checked_count"])
        self.assertEqual(1, summary["check_before_retry_rank_checked_count"])
        self.assertEqual(1, summary["verification_execution_blocked_count"])
        self.assertEqual(1, summary["selected_action_blocked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["persistent_rule_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_doubt_gated_sandbox_candidate_ordering_checks_passed"])

    def assertInvalid(self, field, value):
        record = deepcopy(build_doubt_gated_candidate_ordering_record())
        record[field] = value

        self.assertFalse(validate_doubt_gated_candidate_ordering_record(record)["valid"])


if __name__ == "__main__":
    unittest.main()
